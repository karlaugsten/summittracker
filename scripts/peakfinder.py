import requests
from lxml import etree
from pymongo import MongoClient

r = requests.get('http://www.peakfinder.com/allpeaks.asp')
# Find the HTML Table!
start = r.text.find('<table border="1">')
end = r.text.find('</table>', start+1)
txtTable = r.text[start:end+8]

# Parse table with xml parser
table = etree.XML(txtTable)
rows = iter(table)
headers = [col.text for col in next(rows)]
mountains = []
myCols = ["name", "height_meters", "height_feet", "_id"]
# parse the HTML table to get mountain information
for row in rows:
	values = []
	for col in row:
		value = etree.tostring(col).split('<TD>')[1].split('</TD>')[0]
		if value.find('<A') != -1:
			value = value[value.find('>')+1:value.find('</A>')];
		values.append(value)
	mountains.append(dict(zip(myCols, values)))

# Go through each mountain and get the latitude and longitude data
for mountain in mountains:
	r = requests.get('http://www.peakfinder.com/showpeakbyid.asp?MtnId=' + mountain['_id'])
	lat = r.text[r.text.find('Latitude')+9:r.text.find('Longitude')]
	lat = lat.replace(';', ':').replace(' ', '')
	long = r.text[r.text.find('Longitude')+10:r.text.find(',', r.text.find('Longitude'))]
	long = long.replace(';', ':').replace(' ', '')
	mountain['latitude'] = lat
	mountain['longitude'] = long

# Add mountains to mongodb 

url = 'summittrackerdb.cloudapp.net'
client = MongoClient('mongodb://' + url + ':27017/')
db = client['summittracker']
mountaindb = db['mountains']
mountaindb.insert(mountains)
