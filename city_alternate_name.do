***********************                            ***********************
*           Alternative names for cities, dataset creation
***********************                            ***********************

clear all

*set directory
cd "C:\Users\depir\OneDrive\Desktop\Geodata"

////////////////////////////////////////////////////////////////////////////////
*prepare the dataset from raw
use geoname_raw.dta

* Split the var in separate columns using  ";" as delimiter
split alternatenames, p(,) generate(split_var)

*For safety, save the dataset
save geoname_split0.dta, replace

clear
use geoname_split0.dta
keep geonameid name split_var1-split_var269
tolong split_var, i( geonameid ) j(alternatenames)
keep if split_var!="" | alternatenames==1
bysort geonameid: egen count=count( alternatenames )
sort geonameid alternatenames
replace split_var= name if split_var==""
save geoname_split1.dta, replace

*use python to detect the languages
*city_language_detect.py

////////////////////////////////////////////////////////////////////////////////

*Import csv results from python
cd "C:\Users\depir\OneDrive\Desktop\Geodata"
clear
import delimited "language_detection_results.csv", encoding(UTF-8) 
sort geonameid
rename alternatenames count_name
merge m:m geonameid using "geoname_raw.dta"
*save dataset
save "city_dataset_v0.dta", replace
























