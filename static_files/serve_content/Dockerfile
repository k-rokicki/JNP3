FROM nginx

RUN rm -f /usr/share/nginx/html/index.html
RUN mkdir /usr/share/nginx/html/static

COPY static /usr/share/nginx/html/static
COPY nginx.conf /etc/nginx/

EXPOSE 8888

CMD ["nginx", "-g", "daemon off;"]
