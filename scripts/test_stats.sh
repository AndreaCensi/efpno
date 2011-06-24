#!/bin/bash
set -e
set -x
logs="intel manhattanOlson3500 w10000-odom"
data='../data'
out="out/test_stats/"
mkdir -p $out

logs="w10000-odom manhattanOlson3500 intel "

dists="20"
scale="10000"

for log in $logs; do
	source=$data/$log.g2o
	efpno_plot --stats --outdir $out/reports $source
	
	for dist in $dists; do
		mkdir -p $out/solved/
		solved=$out/solved/$log-solved$dist-T$scale.g2o
		efpno_solve  --seed 0 --scale $scale --max_dist=$dist $source > $solved
		efpno_plot   --stats --outdir $out/reports $solved
	done
done

