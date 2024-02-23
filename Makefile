data/matched.csv: ariadne/ariadne.py beads/input/whoiswho-cities/city.csv data/search.csv 
	poetry run python $< < beads/input/whoiswho-cities/city.csv > $@
data/search.csv: data/city.dta data/name.dta lib/merge.do
	stata -b do lib/merge.do
data/%.dta: temp/%.dta lib/read_%.do
	stata -b do lib/read_$*.do $< $@
temp/%.dta: temp/%.tsv lib/tsv2dta.do
	stata -b do lib/tsv2dta.do $< $@
%.tsv: %.csv
	# Convert csv to tsv, replacing commas with tabs using csvkit
	csvformat -T $< > $@
temp/city.tsv: data/cities1000.zip
	unzip -p $< > temp/cities.txt
	echo "geonameid\tname\tasciiname\talternatenames\tlatitude\tlongitude\tfeature class\tfeature code\tcountry code\tcc2\tadmin1 code\tadmin2 code\tadmin3 code\tadmin4 code\tpopulation\televation\tdem\ttimezone\tmodification date" > $@
	cat temp/cities.txt >> $@
temp/name.tsv: data/alternateNamesV2.zip
	unzip -p $< alternateNamesV2.txt > temp/alternateNamesV2.txt
	echo "alternateNameId\tgeonameid\tisolanguage\talternate name\tisPreferredName\tisShortName\tisColloquial\tisHistoric\tfrom\tto" > $@
	cat temp/alternateNamesV2.txt >> $@
data/cities1000.zip:
	curl -Lo $@ https://download.geonames.org/export/dump/cities1000.zip
data/alternateNamesV2.zip:
	curl -Lo $@ https://download.geonames.org/export/dump/alternateNamesV2.zip
temp/country-codes.csv:
	curl -Lo $@ https://datahub.io/core/country-codes/r/country-codes.csv
data/training.csv: data/training-cities.csv ariadne/bad_matches.py
	poetry run python ariadne/bad_matches.py > $@
temp/training-cities.csv: beads/input/whoiswho-cities/city.csv
	echo "city,file" > $@
	csvgrep -c Country -im CZ $< | tail -n +2 | awk 'BEGIN{srand(12345)} {print rand(), $$0}' | sort -n | cut -d' ' -f2- | head -n 112 | sort | uniq | head -n 98 >> $@
	# add two special cases
	echo "Kolozsvár,HU" >> $@
	echo "Viedeň,SK" >> $@