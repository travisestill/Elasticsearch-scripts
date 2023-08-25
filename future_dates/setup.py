from setuptools import setup, find_packages

setup(
    name='myapp',
    version='1.0',
    packages=find_packages(),
    install_requires=[
        'elasticsearch',
        'python-dateutil',
        'pytz',
    ]
)