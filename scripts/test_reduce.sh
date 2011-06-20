#!/bin/bash
set -e
set -x
logs="intel manhattanOlson3500 w10000-odom"
data='../data'

mkdir -p out

efpno_simplification --fast --max_dist=20 < ${data}/manhattanOlson3500.g2o > out/manhattanOlson3500-20.g20

efpno_plot --fast --outdir out/ out/manhattanOlson3500-20.g20