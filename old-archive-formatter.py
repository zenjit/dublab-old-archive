#Python code to illustrate parsing of XML files
# importing the required modules
# -*- coding: utf-8 -*-
import csv
import re
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser

def parseXML(xmlfilename, showsitems):

	with open(xmlfilename, 'r') as xmlfile:
		data=xmlfile.read().replace('\n', '')

	try:
		root=ET.fromstring(data)
	except Exception as e:
		print(e)
		print("Error parsing " + xmlfilename)
		return

	# iterate shows items
	for item in root.findall('./channel/item'):
		title=item.find('title').text
		if "attachment" in title:
			continue

		content=item.find('contentencoded').text
		url=getUrlFromContent(content)
		tracklist=getTracklistFromContent(content)

		# empty news dictionary
		show={'title': title, 'link':url, 'tracklist':tracklist}

		# append news dictionary to news items list
		showsitems.append(show)

		print(title + "\n" + url + "\n\n" + tracklist + "\n")
	
	# return news items list
	return showsitems

def getUrlFromContent(content):

	url=find_between( content, '<iframe width="100%" height="60" src="', '" frameborder="0" ></iframe>' )
	if not url:
		url=find_between( content, '<iframe width="100%" height="60" src="', '" frameborder="0"></iframe>' )
	urlGood=re.sub(r'%2F', '/', url)

	if "?feed" in urlGood:
		urlVeryGood=find_between( urlGood, '?feed=', '&hide_cover' )
	else:
		urlVeryGood=urlGood.replace('widget/iframe/?hide_cover=1&mini=1&light=1&feed=/', '')
	urlVeryVeryGood=urlVeryGood.replace('https//', '').replace('https%3A//', '')
	return urlVeryVeryGood


def getTracklistFromContent(content):

	tracklist="no tracklist found"
	result=re.search('<p class="" style="white-spacepre-wrap;">(.*)</p></li></ul>', content)
	if result:
		tracklist=result.group(1).replace('</p></li><li><p class="" style="white-spacepre-wrap;">','\n').replace('</p></li></ul><ul data-rte-list="default"><li><p class="" style="white-spacepre-wrap;">','\n')
	else:
		result=re.search('style="white-space pre-wrap;">(.*)</p></li></ul>', content)
		if not result:
			result=re.search('<p style="white-spacepre-wrap;">(.*)</p></li></ul>', content)
			if not result:
				result=re.search('<em>(.*)</em>', content)
			else:
				tracklist=result.group(1).replace('</p></li><li><p style="white-spacepre-wrap;">','\n')
				tracklist=tracklist.replace('</p></li></ul><ul data-rte-list="default"><li><p style="white-spacepre-wrap;">', '\n')
		else:
			tracklist=result.group(1).replace('</p></li><li><p style="white-space pre-wrap;">','\n').replace('</p></li></ul><ul data-rte-list="default"><li><p style="white-space pre-wrap;">','\n')
			tracklist=tracklist.replace('</p><ul data-rte-list="default"><li><p style="white-space pre-wrap;">', '\n').replace('</p></li></ul><p style="white-space pre-wrap;">', '\n').replace('<br><br>', '\n').strip()

	tracklist=cleanTracklist(tracklist)

	return(tracklist)


def cleanTracklist(tracklist):
	tracklist=tracklist.replace("&amp;","&")
	return tracklist


def savetoCSV(newsitems, filename):

	# specifying the fields for csv file
	fields=['title', 'link', 'tracklist']

	# writing to csv file
	with open(filename, 'w') as csvfile:

		# creating a csv dict writer object
		writer=csv.DictWriter(csvfile, fieldnames=fields)

		# writing headers (field names)
		writer.writeheader()

		# writing data rows
		writer.writerows(newsitems)

def find_between( s, first, last ):
    try:
        start=s.index( first ) + len( first )
        end=s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def find_between_r( s, first, last ):
    try:
        start=s.rindex( first ) + len( first )
        end=s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""

	
def main():

	# create empty list for shows items
	showsitems=[]

	for file in os.listdir("./shows/clean"):
		if file.endswith(".xml"):
			#print(file)
			# parse xml file
			showsitems=parseXML(os.path.join("./shows/clean", file), showsitems)
			
	#print showsitems
	# store news items in a csv file
	#savetoCSV(newsitems, 'dublab-old-archive.csv')
	
if __name__ == "__main__":

	# calling main function
	main()
