#!/bin/bash
set -e
set -x
logs="intel manhattanOlson3500 w10000-odom"
data='../data'
out="out/test_solve/"
mkdir -p $out

# logs="manhattanOlson3500 intel w10000-odom"
# logs="intel"
logs="manhattanOlson3500 w10000-odom intel"

dists="15"
nodes="150 200 250"
scale=10000

for log in $logs; do
	source=$data/$log.g2o
	efpno_plot --stats  --outdir $out/reports $source
	
	for min_nodes in $nodes; do
	for dist in $dists; do
		mkdir -p $out/solved/
		solved=$out/solved/$log-D$dist-N${min_nodes}-S${scale}.g2o
		efpno_solve  \
			--scale $scale --max_dist $dist --min_nodes $min_nodes \
			$source > $solved
		efpno_plot  --stats  --outdir $out/reports $solved
	done
	done
done

