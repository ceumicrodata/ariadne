import delimited "data/training.csv", encoding(UTF-8) case(preserve) clear

generate byte match = (geonameid1 == geonameid2)
generate byte name_exact = city1 == city2

foreach X in ascii_ratio name_ratio name_jaro name_levenshtein {
    generate ln_`X' = ln(`X')
}

poisson match ln_ascii_ratio ln_name_jaro ln_name_ratio size2 same_country 
poisson match ln_ascii_ratio ln_name_jaro size2 same_country 
poisson match ln_name_ratio  ln_name_jaro size2 same_country 
poisson match ln_name_jaro size2 same_country 

* overweight unmatched pairs
generate fw = 1
replace fw = 100 if !match 
poisson match ln_name_jaro  name_exact   size2 same_country [fw=fw]