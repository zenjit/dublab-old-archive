#Python code to illustrate parsing of XML files
# importing the required modules
# -*- coding: utf-8 -*-
import csv
import re
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser
import json

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
		completeTitle=item.find('title').text
		title,date=getTitleAndDateFromCompleteTitle(completeTitle)
		if "attachment" in completeTitle:
			continue

		content=item.find('contentencoded').text
		url=getUrlFromContent(content)
		tracklist=getTracklistFromContent(content)

		# empty news dictionary
		show={'title': completeTitle.encode("UTF-8"), 'show': title.encode("UTF-8"), 'date': date.encode("UTF-8"), 'link':url.encode("UTF-8"), 'tracklist':tracklist.encode("UTF-8")}
		#print(tracklist)
		# append news dictionary to news items list
		showsitems.append(show)

		print(title.encode("UTF-8") + "\n" + date.encode("UTF-8") + "\n" + url.encode("UTF-8") + "\n\n" + tracklist.encode("UTF-8") + "\n")
	
	# return news items list
	return showsitems

def getTitleAndDateFromCompleteTitle(completeTitle):
	
	date=re.search(r'(\d{1,2}\W\d{1,2}\W\d{1,2})', completeTitle)
	if date:
		date=date.group(0)
		title=completeTitle.replace(date,"").strip()
		date=date.replace(".","/")
	else:
		title=completeTitle
		date=""
	return title, date

def getUrlFromContent(content):

	url=find_between( content, '<iframe width="100%" height="60" src="', '" frameborder="0" ></iframe>' )
	if not url:
		url=find_between( content, '<iframe width="100%" height="60" src="', '" frameborder="0"></iframe>' )
	url=re.sub(r'%2F', '/', url)

	if "?feed" in url:
		url=find_between( url, '?feed=', '&hide_cover' )
	else:
		url=url.replace('widget/iframe/?hide_cover=1&mini=1&light=1&feed=/', '')
	url=url.replace('https//', '').replace('https%3A//', '')
	return url


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
				if result:
					tracklist=result.group(1)
				else:
					result=re.search('>(.*)</p>', content)
					if result:
						tracklist=result.group(1)
			else:
				tracklist=result.group(1).replace('</p></li><li><p style="white-spacepre-wrap;">','\n')
				tracklist=tracklist.replace('</p></li></ul><ul data-rte-list="default"><li><p style="white-spacepre-wrap;">', '\n')
		else:
			tracklist=result.group(1).replace('</p></li><li><p style="white-space pre-wrap;">','\n').replace('</p></li></ul><ul data-rte-list="default"><li><p style="white-space pre-wrap;">','\n')
			tracklist=tracklist.replace('</p><ul data-rte-list="default"><li><p style="white-space pre-wrap;">', '\n').replace('</p></li></ul><p style="white-space pre-wrap;">', '\n').replace('<br><br>', '\n').strip()

	tracklist=cleanTracklist(tracklist)

	return(tracklist)


def cleanTracklist(tracklist):
	tracklist=tracklist.replace("&amp;","&").replace("<br>","").replace("&nbsp;","")
	tracklist=re.sub("[\<\[].*?[\>\]]", "", tracklist)
	return tracklist


def savetoCSV(newsitems, filename):
	# specifying the fields for csv file
	fields=['title', 'completeTitle', 'date' , 'link', 'tracklist']
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

	#showsitems=parseXML("prova.xml", showsitems)
	#return

	for file in os.listdir("./shows/clean"):
		if file.endswith(".xml"):
			showsitems=parseXML(os.path.join("./shows/clean", file), showsitems)

	print(json.dumps( showsitems, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))
	with open('dublab-old-archive.json', 'w') as f:
		json.dump(showsitems, f, ensure_ascii=False, indent=4)
	#savetoCSV(showsitems, 'dublab-old-archive.csv')
	
if __name__ == "__main__":

	# calling main function
	main()
