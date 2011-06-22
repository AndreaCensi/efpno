#!/bin/bash
set -e
set -x
logs="intel manhattanOlson3500 w10000-odom"
data='../data'
out="out/"
mkdir -p $out

logs="manhattanOlson3500 intel w10000-odom"
# logs="intel"
# logs="manhattanOlson3500"
# logs="w10000-odom"
# logs="intel"
# logs="manhattanOlson3500"

dists="10 20"
# dists="15"
# logs="w10000-odom"
for log in $logs; do
	source=$data/$log.g2o
	efpno_plot --fast --outdir $out/reports $source
	
	for dist in $dists; do
		mkdir -p $out/simplified/
		simplified=$out/simplified/$log-agg$dist.g2o
		efpno_simplification --fast --max_dist=$dist $source > $simplified
		efpno_plot --fast --outdir $out/reports $simplified
	done
done

