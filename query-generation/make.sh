# Pass directory with query files as argument

if [[ -d $1 ]]
then
    mkdir -p queries/mod
    mkdir queries/empty

    java -Xmx20g -jar ../database/jena/jars/fuseki.jar --loc=../database/jena/db/jena --timeout=1000000 /jena &
    sleep 1m

    for file in $1/*.txt
    do
        echo "Generating for "$file
        new_file=${file:${#1}+1}
        touch queries/mod/$new_file
        touch queries/empty/$new_file
        echo "Output in queries/mod/"$new_file" and queries/empty/"$new_file
        python3 generator.py $file mod > queries/mod/$new_file
        python3 generator.py $file empty > queries/empty/$new_file
    done

    kill $!
else
    echo "'"$1"' is not a directory"
fi
