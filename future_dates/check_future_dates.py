import csv
import time
import elasticsearch
import datetime
from dateutil.relativedelta import relativedelta
import dateutil.parser
import pytz
import tkinter as tk
from tkinter import ttk


def get_client():
  print("Select Elasticsearch environment:")
  print("1. Cloud")
  print("2. Self-managed")

  env = input("Enter 1 or 2: ")

  if env == '1':
    cloud_id = input("Enter Cloud ID: ")
    auth = input("Enter 'basic' or 'api' for authentication: ")

    if auth == 'basic':
      username = input("Enter username: ")
      password = input("Enter password: ")
      client = elasticsearch.Elasticsearch(
        cloud_id=cloud_id, 
        basic_auth=(username, password)
      )

    elif auth == 'api':
      api_key = input("Enter API key: ")
      client = elasticsearch.Elasticsearch(
        cloud_id=cloud_id,
        api_key=api_key
      )

  elif env == '2':
    host = input("Enter Elasticsearch host URL: ")
    port = input("Enter port: ")
    auth = input("Enter 'basic' or 'api' for authentication: ")

    if auth == 'basic':
      username = input("Enter username: ")
      password = input("Enter password: ")
      client = elasticsearch.Elasticsearch(
        hosts=[{'host': host, 'port': port}],
        http_auth=(username, password)
      )

    elif auth == 'api':
      api_key = input("Enter API key: ")
      client = elasticsearch.Elasticsearch(
        hosts=[{'host': host, 'port': port}],
        api_key=api_key
      )

  return client


def search_future_timestamps(client):

  utc_tz = pytz.utc
  local_tz = pytz.timezone('America/Los_Angeles')

  now = utc_tz.localize(datetime.datetime.utcnow())
  local_now = now.astimezone(local_tz)

  query = {
    "range": {
      "@timestamp": {
        "gt": local_now  
      }
    }
  }

  results = []

  try:
    response = client.search(
      index='*',
      query=query,
      scroll='1m' 
    )
        
    while True:
      for hit in response['hits']['hits']:
        results.append((hit['_index'], hit['_id']))

      scroll_id = response['_scroll_id']
      response = client.scroll(scroll_id=scroll_id, scroll='1m')

      if len(response['hits']['hits']) == 0:
        break

  except Exception as e:
    print("Search failed:")
    print(e)

  return results


if __name__ == '__main__':

  client = get_client()

  # Make now timezone aware
  utc_tz = pytz.utc
  now = utc_tz.localize(datetime.datetime.utcnow())

  print(f"Current UTC time: {now.isoformat()}")
  print(f"Querying the data. This may take a while...")

  results = search_future_timestamps(client)
  
  print(f"Querying complete. Found {len(results)} results.")
  time.sleep(3)

  with open('results.csv', 'w') as f:

    writer = csv.writer(f)
    writer.writerow(['Index', 'Document ID', 'Timestamp', 'Difference'])

    for index, doc_id in results:

      doc = client.get(index=index, id=doc_id)
      timestamp_str = doc['_source']['@timestamp']
      timestamp = dateutil.parser.parse(timestamp_str)

      diff = relativedelta(timestamp, now)

      writer.writerow([index, doc_id, timestamp, f"{diff.years} years, {diff.months} months, {diff.days} days, diff.hours hours, {diff.minutes} minutes, {diff.seconds} seconds"])
      print (f"Writing {index} {doc_id} {timestamp}")

  print("Done! File saved to './results.csv'")

root = tk.Tk()
root.title('Future Timestamps')
window_width = 1200
window_height = 800
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width/2) - (window_width/2)
y = (screen_height/2) - (window_height/2)
root.geometry('%dx%d+%d+%d' % (window_width, window_height, x, y))

# Read CSV file 
with open('results.csv') as f:
  reader = csv.reader(f)
  header = next(reader)
  data = []
  for row in reader:
    data.append([col.strip() for col in row])

# Define column widths
col_widths = [20, 20, 30, 50]

# Create Treeview
tv = ttk.Treeview(root, columns=header, show='headings')
tv.column("#0", width=0, stretch=tk.NO)
for i, width in enumerate(col_widths):
  tv.column(header[i], width=width, anchor='w')

# Style the treeview
style = ttk.Style()
style.configure("Treeview", 
  font=('Helvetica', 10),
  rowheight=30,
  fieldbackground="lightgrey",
  borderwidth=2
)
style.configure("Treeview.Heading", 
  font=('Helvetica', 12, 'bold'),
  foreground='grey'  
)

for i, h in enumerate(header):
  tv.heading(h, text=h.title(), command=lambda c=h: sortby(tv, c, 0))

# Add data  
for row in data:
  if any(row):
    tv.insert('', 'end', values=row)

# Add scrollbar 
scrollbar = ttk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

tv.configure(yscrollcommand=scrollbar.set)
scrollbar.config(command=tv.yview)

tv.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

def sortby(tree, col, descending):
  """Sort treeview contents when a column header is clicked"""
  data = [(tree.set(child, col), child) for child in tree.get_children('')]

  data.sort(reverse=descending)

  for ix, item in enumerate(data):
    tree.move(item[1], '', ix)

  tree.heading(col, command=lambda col=col: sortby(tree, col, int(not descending)))

root.eval('tk::PlaceWindow . center')
root.mainloop()