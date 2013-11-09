#!/bin/sh

mongoexport --db india -c politicians --csv \
	--fieldFile fields.txt \
	--out "combined_politicians.csv"


