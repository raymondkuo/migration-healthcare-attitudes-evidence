# Decode the archived V-Dem data file (vdem.RData of the V-Dem Institute's R package vdemdata) for
# 92_collect_vdem.py: the liberal democracy index, its 68% interval and standard deviation for the
# given countries and years, written to a CSV with every digit R holds (%.17g), and the codebook
# entry of the index. Base R only.
#
#   Rscript --vanilla scripts/92_decode_vdem.R <vdem.RData> <codebook.RData> <ISO3,ISO3,...> <first> <last> <out.csv> <codebook_out.csv>
args <- commandArgs(TRUE)
e <- new.env()
stopifnot(identical(load(args[1], envir = e), "vdem"))
v <- e$vdem
iso <- strsplit(args[3], ",")[[1]]
cols <- c("country_name", "country_text_id", "country_id", "year",
          "v2x_libdem", "v2x_libdem_codelow", "v2x_libdem_codehigh", "v2x_libdem_sd")
s <- v[v$country_text_id %in% iso & v$year >= as.integer(args[4]) & v$year <= as.integer(args[5]), cols]
s <- s[order(s$country_text_id, s$year), ]
for (c in cols[5:8]) s[[c]] <- ifelse(is.na(s[[c]]), "", sprintf("%.17g", s[[c]]))
write.csv(s, args[6], row.names = FALSE, fileEncoding = "UTF-8")
ce <- new.env()
stopifnot(identical(load(args[2], envir = ce), "codebook"))
cb <- ce$codebook
r <- cb[cb$tag == "v2x_libdem", ]
stopifnot(nrow(r) == 1)
out <- data.frame(field = names(r), value = vapply(names(r), function(n) as.character(r[[n]]), ""))
write.csv(out, args[7], row.names = FALSE, fileEncoding = "UTF-8")
cat(sprintf("decoded %d rows of %d countries; %d columns in the data file\n",
            nrow(s), length(unique(s$country_text_id)), ncol(v)))
