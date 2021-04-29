#!/bin/bash

cd shows

for f in *.xml; do n=$(echo "${f%.*}" | sed -e "s/-/ /g"); n_shows=$(grep -i "<title>$n" $f | wc -l); echo "$n;$n_shows"; done
