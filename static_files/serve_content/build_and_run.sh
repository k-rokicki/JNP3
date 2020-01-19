docker build -t "serve_static" .

docker run -p 8888:80  serve_static