sudo docker build -t "serve_static_other" .

sudo docker run --name serve_static_other --network="host" serve_static_other
