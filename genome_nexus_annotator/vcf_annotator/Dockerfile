FROM --platform=linux/amd64 node:16-buster

RUN npm install -g genome-nexus-cli

RUN apt-get update && apt-get install -y curl unzip python3 python3-pip

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

COPY requirements.txt .

RUN pip3 install -r requirements.txt

RUN mkdir /annotator

WORKDIR /annotator

COPY scripts/ .

RUN chmod -R a+x .