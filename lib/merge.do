use "data/name.dta", clear
merge m:1 geonameid using "data/city.dta", keep(match) nogen keepusing(countrycode latitude longitude population) 

rename alternatename name
export delimited "data/search.csv", replace 