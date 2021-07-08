#!/bin/sh


python3 wrappertest.py app.py $1 $2 $3 $4 $5 $6

pprof

cp profile.0.0.0 profile_output
