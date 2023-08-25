from setuptools import setup, find_packages

setup(
    name='future_dates',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'elasticsearch',
        'python-dateutil',
        'pytz',
    ]
)