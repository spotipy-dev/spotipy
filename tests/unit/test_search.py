import sys
import xml.etree.ElementTree as ET
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from tabulate import tabulate

client_id = 'client_id'
client_secret = 'client_secret'

client_credentials_manager = SpotifyClientCredentials(
    client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

search_str = input("Enter a search string: ")
result = sp.search(search_str)

# Convert the search results to a table format
headers = ["Track Name", "Artist", "Album"]
table = [[track['name'], track['artists'][0]['name'], track['album']['name']]
         for track in result['tracks']['items']]
table_str = tabulate(table, headers=headers)

# Create an XML tree and save it to a file
root = ET.Element("search_results")
for track in result['tracks']['items']:
    track_element = ET.SubElement(root, "track")
    track_element.set("name", track['name'])
    track_element.set("artist", track['artists'][0]['name'])
    track_element.set("album", track['album']['name'])

xml_str = ET.tostring(root, encoding='utf8', method='xml')
with open('search_results.xml', 'wb') as f:
    f.write(xml_str)

print(table_str)
print("Search results saved to search_results.xml")
