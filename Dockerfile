FROM ubuntu

RUN apt update
RUN apt install openjdk-11-jdk -y
RUN apt install default-jre -y
#RUN apt install python3.8 -y
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install python3 -y

RUN apt install python3-pip -y
RUN pip3 install SPARQLWrapper

RUN mkdir /benchmark
WORKDIR /benchmark

ENTRYPOINT bash run-all.sh
