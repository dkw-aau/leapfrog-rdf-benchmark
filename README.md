apt install openjdk-11-jdk# Code
The code for our leapfrog implementation for Apache Jena is available [here](https://github.com/GQgH5wFgzT/jena)

# Repeating the experiments

### Prerequisites
- Java 11
    - ```apt install openjdk-11-jdk```
- any x64 linux distribution with glib support
- Docker
- [bzip2](http://www.bzip.org/)
    - On a debian-based distro: `sudo apt install bzip2`

    Some of the following steps can take hours to complete, so we recommend using [tmux](https://github.com/tmux/tmux) to execute them.

### Getting the repo and the dataset
- Clone this repository. if you use ssh keys, use:
    ```
    git clone git@gitlab.com:learnedrdf/benchmark.git 
    ```
    
    otherwise
    ```
    git clone https://gitlab.com/learnedrdf/benchmark.git
    ```

- Download the [dataset used](https://drive.google.com/file/d/1vtfLE_G3nI0oAFa5xNdzz20R1pDghdHA/view?usp=sharing) and move it to the `benchmark` folder
- Or you can ask administrators to get access to full English-only Wikidata dataset.
- Extract it 
  ```
  bzip2 -d wikidata-filtered.nt.bz2
  ```
- Or you can [construct the dataset from the latest truthy wikidata dump](#building-the-dataset)

### Create the database for Jena, Jenaclone and Leapfrog
- Pull the ubuntu image `docker pull ubuntu`
- Download the files apache-jena-3.17.0.tar.gz from [Apache Jena downloads page](https://archive.apache.org/dist/jena/binaries/apache-jena-3.17.0.tar.gz) and move it into `jena` folder
- Change directory into `jena` folder
- Extract it `tar -xf apache-jena-3.17.0.tar.gz`
- Open a containerized environment 
  ```
  docker run -v ${PWD}/../:/srv -i -t ubuntu /bin/bash
  ```

- Change directory to `srv/jena`
- Upgrade packages `apt update`
- Install JDK 11 `apt install openjdk-11-jdk -y`
- Install the Java runtime environment `apt install default-jre -y`
- Create the database for Jena and Jenaclone `apache-jena-3.17.0/bin/tdbloader2 --loc=db/jena ../wikidata-filtered.nt`
- Edit the file `apache-jena-3.9.0/bin/tdbloader2index` and go to the line following `generate_index "$K3 $K1 $K2" "$DATA_TRIPLES" OSP`
- Add the following lines
  ```
  generate_index "$K1 $K3 $K2" "$DATA_TRIPLES" SOP
  generate_index "$K2 $K1 $K3" "$DATA_TRIPLES" PSO
  generate_index "$K3 $K2 $K1" "$DATA_TRIPLES" OPS
  ```
- Create the database for the leapfrog impementation `apache-jena-3.9.0/bin/tdbloader2 --loc=db/leapfrog ../wikidata-filtered.nt`

### Adding Jenaclone
- Build the Jenaclone project using the `mvn install` Maven lifecycle, as specified in the <a href="https://gitlab.com/learnedrdf/jenaclone-3.17/-/wikis/instructions">documentation</a> of the Jenaclone repository
- From the root directory of Jenaclone, copy the file `jena-fuseki2/jena-fuseki-server/target/jena-fuseki-server-3.17.0` into `benchmark/jena/jars` of the benchmark root directory
- Make sure the Jenaclone .jar file is named `fuseki-jenaclone.jar`

### Run the benchmark
- Change directory into the root directory of this repository
- `docker build -t jenaclone_benchmark .`
-   Run the container
    ```
    docker run \
        --rm  \
        -v ${PWD}/benchmark/:/benchmark \
        jenaclone_benchmark
    ```
    - `${PWD}` matches `<ABSOLUTE PATH>` to current  `<REPOSITORY NAME>`

Now the results are available in the folders `queries/bgps/output` and `queries/optionals/output`

# Results
You can find our results in the results folder. For each query pattern you will find a folder containing two files, one for the Original Apache Jena and for for our modification of Apache Jena. Each line of a file contains three values separated by a semicolon: `queryNumber;numberOfResutls;executionTimeInNanoseconds`

# Analysis
After running the benchmark and the results can be found in `benchmark/benchmark/queries/*/output`, move them to the corresponding folder in `results`.
Convert the benchmark results to .csv files


```
python3 to_csv.py
```

This script requiret matplotlib, which can be install with

```
pip3 install matplotlib
```

Now, to run the analysis tool, run the command

```
python3 analysis.py bgps optionals existence_check
```

You can specify youself the folder containing results you want an analysis of. For example the following command will only provide an analysis of the optional query benchmark results

```
python3 analysis.py optionals
```

To print the query benchmark running times along their query with intermediate result set sizes, run the command

```
python3 result_size_analysis.py <RDF_DATASET> <RESULT_FOLDER1_> {RESULT_FOLDER_N}
```

`<RDF_DATASET>` is the dataset file to compute intermediate result set sizes. Make sure this is the same dataset file used to load the Jena triplestore used in the benchmark results. Following arguments are benchmark result folders, just like when running the `analysis.py` tool. At least one folder is required.

# Common Issues

## Command _tdbloader2_ Loads TDB2 Data

Even though the command seems to load the data into TDB2 instead of TDB1, it is not true. Therefore, make sure not to add the `--tdb2` flag when running the server, since this would make the server return empty result sets because there is no TDB2 data.
According to the <a href="https://jena.apache.org/documentation/tdb/tdb-xloader.html">Apache Jena documentation</a>, _tdbloader_ translates into _tdb1.xloader_, where the prefix determines which version of TDB to use.
