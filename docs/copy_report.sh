#!/bin/zsh

cp -R ../scripts/out/test_solve source/my_static
rm source/my_static/test_solve/**/*.pickle
du -h -s source/my_static/test_solve