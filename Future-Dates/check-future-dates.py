import csv
import elasticsearch
import datetime
from dateutil.relativedelta import relativedelta
import dateutil.parser
import pytz

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
        http_auth=(username, password)
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
  
  print(f"Querying complete. Found {len(results)} results. Writing to CSV. This takes a long time too. Go get some water...")

  with open('results.csv', 'w') as f:

    writer = csv.writer(f)
    writer.writerow(['Index', 'Document ID', 'Timestamp', 'Difference'])

    for index, doc_id in results:

      doc = client.get(index=index, id=doc_id)
      timestamp_str = doc['_source']['@timestamp']
      timestamp = dateutil.parser.parse(timestamp_str)

      diff = relativedelta(timestamp, now)

      writer.writerow([index, doc_id, timestamp, f"{diff.years} years, {diff.months} months, {diff.days} days"])

  print("Done! File saved to './results.csv'")