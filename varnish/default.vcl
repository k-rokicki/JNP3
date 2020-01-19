vcl 4.0;

import directors;

backend django1 {
    .host = "0.0.0.0";
    .port = "1234";
    .probe = {
        .url = "/";
        .timeout = 1s;
        .interval = 5s;
        .window = 5;
        .threshold = 3;
    }
}

backend django2 {
    .host = "0.0.0.0";
    .port = "4321";
    .probe = {
        .url = "/";
        .timeout = 1s;
        .interval = 5s;
        .window = 5;
        .threshold = 3;
    }
}

backend static_other {
    .host = "0.0.0.0";
    .port = "7777";
    .probe = {
        .url = "/ping";
        .timeout = 1s;
        .interval = 5s;
        .window = 5;
        .threshold = 3;
    }
}

backend static_content1 {
    .host = "0.0.0.0";
    .port = "8888";
    .probe = {
        .url = "/static/ping";
        .timeout = 1s;
        .interval = 5s;
        .window = 5;
        .threshold = 3;
    }
}

backend static_content2 {
    .host = "0.0.0.0";
    .port = "9999";
    .probe = {
        .url = "/static/ping";
        .timeout = 1s;
        .interval = 5s;
        .window = 5;
        .threshold = 3;
    }
}

sub vcl_init {
    new django_director = directors.random();
    django_director.add_backend(django1, 1);
    django_director.add_backend(django2, 1);

    new static_director = directors.round_robin();
    static_director.add_backend(static_other);

    new content_director = directors.round_robin();
    content_director.add_backend(static_content1);
    content_director.add_backend(static_content2);
}

sub vcl_recv {
    if (req.url ~ "/") {
        set req.backend_hint = django_director.backend();
    }

    if (req.url ~ "/top") {
        set req.backend_hint = django_director.backend();
        return (hash);
    }

    if (req.url ~ "/static/admin" || req.url ~ "/static/css" ||
        req.url ~ "/static/images" || req.url ~ "/static/js") {
        set req.backend_hint = static_director.backend();
        return (hash);
    }

    if (req.url ~ "/static/content") {
        set req.backend_hint = content_director.backend();
        if (req.url ~ "\?top$") {
            set req.url = regsub(req.url, "\?.*$", "");
            return (hash);
        }
    }
}

sub vcl_backend_response {
    if (bereq.url ~ "/top") {
        unset beresp.http.set-cookie;
        set beresp.http.cache-control = "public, max-age=30";
        set beresp.ttl = 60s;
        return (deliver);
    }

    if (bereq.url ~ "/static/admin" || bereq.url ~ "/static/css" ||
        bereq.url ~ "/static/images" || bereq.url ~ "/static/js") {
        unset beresp.http.set-cookie;
        set beresp.http.cache-control = "public, max-age=15";
        set beresp.ttl = 30s;
        return (deliver);
    }

    if (bereq.url ~ "/static/content") {
        unset beresp.http.set-cookie;
        set beresp.http.cache-control = "public, max-age=30";
        set beresp.ttl = 60s;
        return (deliver);
    }
}