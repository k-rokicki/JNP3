#!/bin/bash
sudo docker run -d --name pieski-elastic-container --network="host" -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.5.1

while ! nc -z localhost 9200; do   
  sleep 0.1
done

curl -X POST "localhost:9200/images/image/1" -H 'Content-Type: application/json' -d'
{
    "title": "Husky",
    "tags": "cute, smart",
    "upvotes": 5
}
'
curl -X POST "localhost:9200/images/image/2" -H 'Content-Type: application/json' -d'
{
    "title": "Golden",
    "tags": "love, cute",
    "upvotes": 8
}
'
curl -X POST "localhost:9200/images/image/3" -H 'Content-Type: application/json' -d'
{
    "title": "Dachshund",
    "tags": "love, short",
    "upvotes": 12
}
'
curl -X POST "localhost:9200/images/image/4" -H 'Content-Type: application/json' -d'
{
    "title": "Dalmatian",
    "tags": "cute, b&w",
    "upvotes": 3
}
'
curl -X POST "localhost:9200/images/image/5" -H 'Content-Type: application/json' -d'
{
    "title": "Mongrel",
    "tags": "love, cute",
    "upvotes": 27
}
'