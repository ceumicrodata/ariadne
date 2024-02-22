args infile outfile
use `infile', clear

keep ISO31661Alpha2 Languages
* we add a comma to be able to search for language coses like ",hu" and match whether it is the first or the last language in the list
replace Languages = "," + Languages

save `outfile', replace