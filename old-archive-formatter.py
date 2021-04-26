#Python code to illustrate parsing of XML files
# importing the required modules
# -*- coding: utf-8 -*-
import csv
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser

def parseXML(xmlfilename):

	with open(xmlfilename, 'r') as xmlfile:
		data=xmlfile.read().replace('\n', '')

	root = ET.fromstring(data)

	# create empty list for news items
	showsitems = []

	# iterate news items
	for item in root.findall('./channel/item'):
		title = item.find('title').text
		if "attachment" in title:
			continue
		print(title)
		print("\n")
		content = item.find('contentencoded').text
		url=find_between( content, '<iframe width="100%" height="60" src="', '" frameborder="0" ></iframe>' )
		urlGood=re.sub(r'%2F', '/', url)
		urlVeryGood=urlGood.replace('widget/iframe/?hide_cover=1&mini=1&light=1&feed=/', '')
		urlVeryVeryGood=urlVeryGood.replace('https//', '')

		print(urlVeryVeryGood)
		print("\n")
		result = re.search('<p class="" style="white-spacepre-wrap;">(.*)</p></li></ul>', content)
		if result:
			#print(result.group(1))
			tracklist=result.group(1).replace('</p></li><li><p class="" style="white-spacepre-wrap;">','\n').replace('</p></li></ul><ul data-rte-list="default"><li><p class="" style="white-spacepre-wrap;">','\n')
			#print(content)
			print(tracklist)
		else:
			print "no tracklist found" 
			result = re.search('style="white-space pre-wrap;">(.*)</p></li></ul>', content)
			if not result:
				print "no tracklist found - B"
				result = re.search('<p style="white-spacepre-wrap;">(.*)</p></li></ul>', content)
				if not result:
					print "no tracklist found - C"
					result = re.search('<em>(.*)</em>', content)
					if not result:
						print "no tracklist found - D"
					else:
						print(result.group(1))
				else:
					tracklist=result.group(1).replace('</p></li><li><p style="white-spacepre-wrap;">','\n')
					tracklist=tracklist.replace('</p></li></ul><ul data-rte-list="default"><li><p style="white-spacepre-wrap;">', '\n')
					print(tracklist)
			else:
				tracklist=result.group(1).replace('</p></li><li><p style="white-space pre-wrap;">','\n').replace('</p></li></ul><ul data-rte-list="default"><li><p style="white-space pre-wrap;">','\n')
				tracklist=tracklist.replace('</p><ul data-rte-list="default"><li><p style="white-space pre-wrap;">', '\n').replace('</p></li></ul><p style="white-space pre-wrap;">', '\n').replace('<br><br>', '\n').strip()
				#print(content)
				print(tracklist)

		#show = ET.fromstring(content.decode('utf-8'))

		# empty news dictionary
		shows = {}

		# append news dictionary to news items list
		showsitems.append(shows)
	
	# return news items list
	return showsitems


def savetoCSV(newsitems, filename):

	# specifying the fields for csv file
	fields = ['guid', 'title', 'pubDate', 'description', 'link', 'media']

	# writing to csv file
	with open(filename, 'w') as csvfile:

		# creating a csv dict writer object
		writer = csv.DictWriter(csvfile, fieldnames = fields)

		# writing headers (field names)
		writer.writeheader()

		# writing data rows
		writer.writerows(newsitems)

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_between_r( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

	
def main():

	# parse xml file
	newsitems = parseXML('6474_clean.xml')

	# store news items in a csv file
	savetoCSV(newsitems, 'battuta.csv')
	
	
if __name__ == "__main__":

	# calling main function
	main()
