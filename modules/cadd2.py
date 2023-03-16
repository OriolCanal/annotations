import requests
import re

# URL for the CADD release page
url = "https://cadd.gs.washington.edu/download"

# Get the release page content
response = requests.get(url)
html = response.content.decode("utf-8")
#print(f"{html = }")

pattern = r"Developmental release: v(\d+\.\d+)"
matches = re.findall(pattern, html)
print(f"{matches}")
# Find the links to the database files
