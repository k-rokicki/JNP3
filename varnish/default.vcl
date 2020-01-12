vcl 4.0;

import directors;

backend server1 {
    .host = "127.0.0.1";
    .port = "1234";
}

backend server2 {
    .host = "127.0.0.1";
    .port = "4321";
}

sub vcl_init {
    new bar = directors.round_robin();
    bar.add_backend(server1);
    bar.add_backend(server2);
}

sub vcl_recv {
    set req.backend_hint = bar.backend();
}
