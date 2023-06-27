#!/bin/bash

cd jena
java -Xmx20g -jar jars/fuseki.jar --loc=db/jena --timeout=1000000 /jena &
cd ..

sleep 1m

echo Warming up
python3 benchmark.py queries/warmup.txt http://localhost:3030/jena/sparql > /dev/null
echo "[Done]"

sleep 1m

for file in $1/*.txt
do
    queryName=$(basename $file)
    echo Processing $queryName

    python3 benchmark.py $1/$queryName http://localhost:3030/jena/sparql > $1/output/${queryName%%.txt}/jena.csv
    echo "[Done]"
done

kill $!
