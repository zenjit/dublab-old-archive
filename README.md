# dublab-old-archive

# in shows folder there's an xml file for each show
# in order to prepare shows for extracting information, run:

cd shows/
for f in *.xml; do ./clean_shows.sh $f; done

# this will produce a clean (*_clean.xml) version of each show under shows/clean

# run python program to get info from cleaned shows:

python old-archive-formatter.py