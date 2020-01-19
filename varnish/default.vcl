vcl 4.0;

import directors;

backend django1 {
    .host = "0.0.0.0";
    .port = "1234";
}

/*
backend django2 {
    .host = "0.0.0.0";
    .port = "4321";
}
*/

backend static_other {
    .host = "0.0.0.0";
    .port = "7777";
}

backend content_other {
    .host = "0.0.0.0";
    .port = "8888";
}

sub vcl_init {
    new django_director = directors.round_robin();
    django_director.add_backend(django1);
    #django_director.add_backend(django2);

    new static_director = directors.round_robin();
    static_director.add_backend(static_other);

    new content_director = directors.round_robin();
    content_director.add_backend(content_other);
}

sub vcl_recv {
    if (req.url ~ "/") {
        set req.backend_hint = django_director.backend();
    }

    if (req.url ~ "/static/admin" || req.url ~ "/static/css" ||
        req.url ~ "/static/images" || req.url ~ "/static/js") {
        set req.backend_hint = static_director.backend();
        return (hash);
    }

    if (req.url ~ "/static/content") {
        set req.backend_hint = content_director.backend();
        return (pass);
    }
}

sub vcl_backend_response {
    if (bereq.url ~ "/static/admin" || bereq.url ~ "/static/css" ||
        bereq.url ~ "/static/images" || bereq.url ~ "/static/js") {
        unset beresp.http.set-cookie;
        set beresp.http.cache-control = "public, max-age=5";
        set beresp.ttl = 15s;
        return (deliver);
    }
}