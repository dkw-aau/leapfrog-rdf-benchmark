#!/bin/bash

start=$(date)
echo Loading started $start

cd jena
java -Xmx300g -jar jars/fuseki-jenaclone.jar --loc=db/jena --timeout=1000000 /jenaclone &
cd ..

sleep 60m
echo "[Done]"

echo Warming up
python3 benchmark.py queries/warmup.txt http://localhost:3030/jenaclone/sparql > /dev/null
echo "[Done]"
sleep 1m

for file in $1/*.txt
do
    queryName=$(basename $file)
    echo Processing $queryName

    python3 benchmark.py $1/$queryName http://localhost:3030/jenaclone/sparql > $1/output/${queryName%%.txt}/jenaclone
    echo "[Done]"
done

kill $!
