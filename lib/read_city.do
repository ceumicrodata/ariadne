args infile outfile
use `infile', clear

keep geonameid name asciiname latitude longitude countrycode population dem timezone

save `outfile', replace
