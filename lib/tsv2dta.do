args inf outf
import delimited "`inf'", varnames(1) case(preserve) clear encoding(UTF-8) delimiter(tab)

save "`outf'", replace