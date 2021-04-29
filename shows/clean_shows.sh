#!/bin/bash

input=$1

show=$(echo "${input%.*}")

output=$(echo "./clean/${show}_clean.xml")

show_name=$(echo $show | sed -e "s/-/ /g") # get show name from filename

# custom rename for some shows containing symbols
if [ "$show_name" == "Im new here" ]; then
	show_name="I'm new here"
elif [ "$show_name" == "internet green text stories" ]; then
	show_name="Internet, Green Text Stories"
elif [ "$show_name" == "its about that" ]; then
	show_name="it's about that"
elif [ "$show_name" == "oh coconut" ]; then
	show_name="Oh, Coconut"
elif [ "$show_name" == "she said so" ]; then
	show_name="SheSaid.So"
elif [ "$show_name" == "the sinners inn show" ]; then
	show_name="the sinners' inn show"
elif [ "$show_name" == "ultra local records" ]; then
	show_name="ultra-local records"
elif [ "$show_name" == "x≠x" ]; then
	show_name="x ≠ x"
elif [ "$show_name" == "ha" ]; then
	show_name="HA'"
fi

n_shows=$(grep -i -n "<title>$show_name" $input | wc -l)

if [ "$n_shows" -eq "0" ]; then
	echo "no show found for $show_name" 
	exit
fi

echo "found $n_shows for $show_name"

# get show start

n_first_show=$(grep -i -n "<title>$show_name" $input | head -n 1) # get first appearance of the show...

n_start=$(echo $n_first_show | cut -d":" -f1) # and get line number

n_first_item=$(head -n $n_start $input | tail | grep -n "<item>" | cut -d":" -f1) # search for the <item> tag line prior to the first show

go_back=$( expr 10 - $n_first_item ) # lines to go back to find first <item> tag

start=$(expr $n_start - $go_back) # get line number containing the firt <item>

# get show end

n_last_show=$(grep -i -n "<title>$show_name" $input | tail -n 1) # get last appearance of the show...

n_stop=$(echo $n_last_show | cut -d":" -f1) # and get line number

n_stop_context=$( expr $n_stop + 200 )

n_last_item=$(head -n $n_stop_context $input | tail -n 200 | grep -n "<item>" | head -n 1 | cut -d":" -f1) # search for the <item> tag line after the last show...

end=$( expr $n_stop + $n_last_item ) # and get line number

# calculate length and range of lines to extract from file which include all shows
range=$( expr $end - $start ) 
end=$( expr $end - 1 )

#exit

# create a simplified version of the file containing only shows
echo '<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:excerpt="http://wordpress.org/export/1.2/excerpt/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:wfw="http://wellformedweb.org/CommentAPI/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:wp="http://wordpress.org/export/1.2/">
  <channel>' > $output

head -n $end $input | tail -n $range | sed -e "s/://g" >> $output

echo '  </channel>
</rss>
' >> $output
