sudo docker build -t "serve_static_content" .

sudo docker run --name serve_static_content --network="host" serve_static_content