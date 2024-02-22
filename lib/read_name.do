args infile outfile
use `infile', clear

local preferred_languages en de hu ru gr cs sk pl ro tr it nl fr es pt

keep alternateNameId geonameid isolanguage alternatename
merge m:1 geonameid using "data/city.dta", keep(match) nogen keepusing(geonameid name countrycode) 
mvencode is* , mv(0)

rename countrycode ISO31661Alpha2
merge m:1 ISO31661Alpha2 using "data/country-codes.dta", keep(master match) nogen keepusing(Languages)

keep if length(isolanguage) == 2
generate byte local_language = index(Languages, "," + isolanguage) > 0
tabulate local_language

* add the proper name
bysort geonameid: generate N = (_n == _N)+1
expand N, generate(expanded)
replace alternatename = name if expanded == 1
replace isolanguage = "local" if expanded == 1

generate byte preferred = 0
foreach lang in `preferred_languages' {
    replace preferred = 1 if isolanguage == "`lang'"
}
replace preferred = 1 if local_language == 1
replace preferred = 1 if isolanguage == "local"
keep if preferred == 1
drop preferred

drop name expanded N ISO* Languages alternateNameId

save `outfile', replace
