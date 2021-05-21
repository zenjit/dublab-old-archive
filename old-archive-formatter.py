#Python code to illustrate parsing of XML files
# importing the required modules
# -*- coding: utf-8 -*-
import csv
import re
import os
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import XMLParser
import json
from collections import OrderedDict
import ntpath

def parseXML(xmlfilename, showsitems, normalizeTitle):

	with open(xmlfilename, 'r') as xmlfile:
		data=xmlfile.read().replace('\n', '')

	try:
		root=ET.fromstring(data)
		firstTitle=root.findall('./channel/item')[0]
		firstTitle=firstTitle.find('title').text
	except Exception as e:
		print(e)
		print("Error parsing " + xmlfilename)
		return

	if normalizeTitle:
		showName=nameNormalizer(xmlfilename, firstTitle)
	else:
		showName=pathLeaf(os.path.splitext(pathLeaf(xmlfilename))[0])

	# iterate shows items
	for item in root.findall('./channel/item'):
		completeTitle=item.find('title').text
		if "attachment" in completeTitle:
			continue

		title,date=getTitleAndDateFromCompleteTitle(completeTitle, normalizeTitle)

		content=item.find('contentencoded').text
		url=getUrlFromContent(content)
		tracklist=getTracklistFromContent(content)

		if not date:
			date=getDateFromUrl(url)

		show={'show': showName.encode("UTF-8"), 'title': completeTitle.encode("UTF-8"), 'title': title.encode("UTF-8"), 'date': date.encode("UTF-8"), 'link':url.encode("UTF-8"), 'tracklist':tracklist.encode("UTF-8")}
		# append shows dictionary to shows items list
		showsitems.append(show)
		#print(completeTitle.encode("UTF-8") + "\n" + title.encode("UTF-8") + "\n" + date.encode("UTF-8") + "\n" + url.encode("UTF-8") + "\n\n" + tracklist.encode("UTF-8") + "\n")
	
	# return shows items list
	return showsitems

def getTitleAndDateFromCompleteTitle(completeTitle, normalizeTitle):
	if "Est.88" in completeTitle:
		title="Est.88"
		date=title.replace("Est.88","").strip()
		return title, date
	date=re.search(r'\b(\d{1,2}\W\d{1,2}\W\d{1,2})\b', completeTitle)
	if date:
		date=date.group(0)
		title=completeTitle.replace(date,"").strip()
		date=date.replace(".","/")
	else:
		title=completeTitle
		date=""
	return cleanText(title), date

def nameNormalizer(xmlfilename, firstTitle):
	showLen=len(re.split("\s+|-", os.path.splitext(pathLeaf(xmlfilename))[0]))
	show=firstTitle.split()[:showLen]
	show=" ".join(show)
	return show


def pathLeaf(xmlfilename):
    head, tail = ntpath.split(xmlfilename)
    return tail or ntpath.basename(head).replace("_clean","")

def getDateFromUrl(url):
	date=re.search('(\d{6})', url)
	if date:
		date=date.group(1)
		date='/'.join(a+b for a,b in zip(date[::2], date[1::2]))
		return date
	else:
		return ""

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

	tracklist=cleanText(tracklist)

	return(tracklist)


def cleanText(tracklist):
	tracklist=tracklist.replace("&amp;","&").replace("<br>","").replace("&nbsp;","")
	tracklist=re.sub("[\<\[].*?[\>\]]", "", tracklist)
	return tracklist

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
	bsidesitems=[]
	sponsorsitems=[]

	bsidesitems=parseXML("./shows/bsides.xml", bsidesitems, False)
	with open('bsides.json', 'w') as f:
		json.dump(bsidesitems, f, ensure_ascii=False, indent=4)

	sponsorsitems=parseXML("./shows/sponsors.xml", sponsorsitems, False)
	#print(json.dumps( sponsorsitems, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))
	with open('sponsors.json', 'w') as f:
		json.dump(sponsorsitems, f, ensure_ascii=False, indent=4)

	for file in os.listdir("./shows/clean"):
		if file.endswith(".xml"):
			showsitems=parseXML(os.path.join("./shows/clean", file), showsitems, True)

	with open('dublab-old-archive.json', 'w') as f:
		json.dump(showsitems, f, ensure_ascii=False, indent=4)
	counter = OrderedDict()
	for item in showsitems:
		if 'show' in item:
			counter[item['show']] = counter.get(item['show'], 0) + 1
	print(json.dumps( counter, sort_keys=True, indent=4, separators=(',', ': '), ensure_ascii=False))
	
if __name__ == "__main__":

	main()
