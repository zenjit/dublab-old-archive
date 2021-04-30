# dublab-old-archive

shows folder's contains xml files from Squarespace.

to prepare shows (clean xml files) for extracting information, run:

cd shows/
for f in *.xml; do ./clean_shows.sh $f; done

this will produce a clean (*_clean.xml) version of each show under shows/clean but some (5-10) had to be fixed manually...

finally, run python program to get shows list:

python old-archive-formatter.py
