FROM nginx

RUN rm -f /usr/share/nginx/html/index.html
RUN mkdir /usr/share/nginx/html/static

COPY static /usr/share/nginx/html/static
COPY ping /usr/share/nginx/html/
COPY nginx.conf /etc/nginx/

EXPOSE 7777

CMD ["nginx", "-g", "daemon off;"]
