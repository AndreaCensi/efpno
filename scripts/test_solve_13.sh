#!/bin/bash
set -e
set -x
logs="manhattanOlson3500 M3500a M3500b M3500c"
data='../data'
out="out/test_solve_13/"
mkdir -p $out

# logs="manhattanOlson3500 intel w10000-odom"
# logs="intel"
# logs="manhattanOlson3500 w10000-odom intel"
logs="input_M3500_addsmallnoise input_M3500_original"
dists="15"
nodes="150 200 250"
scale=10000

for log in $logs; do
	source=$data/$log.g2o
	efpno_plot --stats  --outdir $out/reports $source
	mkdir -p $out/source
	cp $source $out/source/$log.graph
	for min_nodes in $nodes; do
	for dist in $dists; do
		mkdir -p $out/solved/
		solved=$out/solved/$log-D$dist-N${min_nodes}-S${scale}.graph
		efpno_solve  \
			--scale $scale --max_dist $dist --min_nodes $min_nodes \
			$source > $solved
		efpno_plot  --stats  --outdir $out/reports $solved
	done
	done
done

