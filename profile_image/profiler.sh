#!/bin/sh

python3 stats.py &
timeout -s SIGINT 60 python3 parser.py app.py $1 $2 $3 $4 $5 $6
python3 wrappertest.py app.py $1 $2 $3 $4 $5 $6

pprof

cp profile.0.0.0 profile_output
cp stats.csv profile_output
cp ftimes.csv profile_output
cp ltimes.csv profile_output
