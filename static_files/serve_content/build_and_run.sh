sudo docker build -t "serve_static_content1" .

sudo docker run --name serve_static_content1 --network="host" serve_static_content1