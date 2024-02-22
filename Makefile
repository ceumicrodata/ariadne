all: data/city.dta data/name.dta data/country-codes.dta
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