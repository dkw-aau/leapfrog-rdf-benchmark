FROM openjdk:11

RUN apt update -y
RUN apt install python3 -y
RUN apt install python3-pip -y
RUN pip3 install SPARQLWrapper

RUN mkdir /home/gen
RUN mkdir /home/database
RUN mkdir /home/queries

WORKDIR /home/gen

ENTRYPOINT bash make.sh ../queries
