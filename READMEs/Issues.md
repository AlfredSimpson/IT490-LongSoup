# Issues

We encountered numerous issues while working on this project. This document will help you if you encountered them, too... we hope. If you encounter an issue we didn't cover, good luck.

## Table of Contents



## RabbitMQ, Erlang, and TLS

On 12/2 one of our primary servers updated. This change caused RabbitMQ to stop working. This was because Erlang changed a default in tls options to verify_peer. This caused RabbitMQ to fail to connect to itself. We fixed this by adding the following to the RabbitMQ config file:

```erlang
{rabbitmq_management, [
    {listener, [{port,     15672},
                 {ssl,      true},
                 {ssl_opts, [{cacertfile, "/etc/rabbitmq/ssl/cacert.pem"},
                             {certfile,   "/etc/rabbitmq/ssl/cert.pem"},
                             {keyfile,    "/etc/rabbitmq/ssl/key.pem"},
                             {verify,     verify_none},
                             {fail_if_no_peer_cert, false}]}]}
  ]},
```

We had to generate a new cert for RabbitMQ and add it to the config file. We also had to add the verify and fail_if_no_peer_cert options to the ssl_opts. This fixed the issue.

However, we also had to add the following to the RabbitMQ startup script:

```bash
export RABBITMQ_SERVER_ADDITIONAL_ERL_ARGS="-rabbit ssl_dist_opt_server verify_none"
```

This was because the RabbitMQ startup script was not passing the ssl_dist_opt_server option to Erlang. This caused RabbitMQ to fail to connect to itself. This fixed the issue.

In addition, we had issues even getting rabbitmq to accept a config file. To add a config file to rabbitmq, we took the following steps:

1. Create a config file in /etc/rabbitmq/rabbitmq.config
2. Add the following to the file:

```erlang
[
  {rabbit, [
    {ssl_listeners, [5671]},
    {ssl_options, [{cacertfile, "/etc/rabbitmq/ssl/cacert.pem"},
                   {certfile,   "/etc/rabbitmq/ssl/cert.pem"},
                   {keyfile,    "/etc/rabbitmq/ssl/key.pem"},
                   {verify,     verify_none},
                   {fail_if_no_peer_cert, false}]}
  ]}
].
```

We then had to restart rabbitmq by running:
    
    ```bash 
    sudo systemctl restart rabbitmq-server
    ```


Next, we needed to modify our python code to use TLS. as pika.SSLOptions only takes SSLContext objects, we had to create one. We did this by adding the following to our code - first laying out our ssl_options and then passing it to the ssl context and finally giving that to the pika connection object:

```python
ssl_options = {
    "ca_certs": cafile,
    "certfile": certfile,
    "keyfile": keyfile,
    "cert_reqs": ssl.CERT_NONE,
    "server_side": False
}

ssl_context = ssl.create_default_context(cafile=cafile)
ssl_context.load_cert_chain(certfile=certfile, keyfile=keyfile)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=host,
        port=port,
        virtual_host=virtual_host,
        credentials=credentials,
        ssl_options=ssl_context
    )
)
```


We also had to pass this to the pika connection object:

```python
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=host,
        port=port,
        virtual_host=virtual_host,
        credentials=credentials,
        ssl_options=ssl_options
    )
)
```


It took a few tries, and iterating because it wasn't as straight forward as I had hoped.

A subissue we ran into was permissioning. rabbitmq needed to read the ssl files. I actually knew this but just forgot to do it. Obviously you're going to sudo chmod this, but I'm going to put it here for completeness:

```bash
sudo chmod 644 /etc/rabbitmq/ssl/*
```
644 provides read access to the owner and group, and read access to everyone else.


After modifying the permissions, we encountered a new error:
    
```bash
    TypeError: ssl_options must be None or SSLOptions but got <ssl.SSLContext object at 0x7f7ddeea8940>
```

This was because we were passing the ssl_context object to the pika connection object. We fixed this modifying our connection parameters to look like this:
    
```python
ssl_options = {
    "ca_certs": "/etc/rabbitmq/ssl/ca_certificate.pem",
    "certfile": "/etc/rabbitmq/ssl/client_LongSoup-DB_certificate.pem",
    "keyfile": "/etc/rabbitmq/ssl/client_LongSoup-DB_key.pem",
    "cert_reqs": ssl.CERT_REQUIRED,
    "ssl_version": ssl.PROTOCOL_TLS,
}

ssl_context = ssl.create_default_context(cafile=ssl_options["ca_certs"])
ssl_context.verify_mode = ssl.CERT_REQUIRED
ssl_context.load_cert_chain(
    ssl_options["certfile"], ssl_options["keyfile"], password="puosgnol"
)
ssl_options = pika.SSLOptions(ssl_context)
creds = pika.PlainCredentials(username=BROKER_USER, password=BROKER_PASS)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=BROKER_HOST,
        port=5672,
        credentials=creds,
        virtual_host=vHost,
        ssl_options=ssl_options,
    )
)
```

This created *another* issue. We were giving the wrong ssl version number. We tried passing 1_2, 1_1, and 1_3. None of these worked. We then tried passing ssl.PROTOCOL_TLS. This also did not work.

We then tried passing ssl.PROTOCOL_TLS_CLIENT. This worked. We were able to connect to rabbitmq. Still no luck. We were getting the following error:

```bash
Traceback (most recent call last):
  File "/home/alfred/Desktop/IT490-LongSoup/DB/fixme.py", line 775, in <module>
    connection = pika.BlockingConnection(
  File "/home/alfred/.local/lib/python3.10/site-packages/pika/adapters/blocking_connection.py", line 360, in __init__
    self._impl = self._create_connection(parameters, _impl_class)
  File "/home/alfred/.local/lib/python3.10/site-packages/pika/adapters/blocking_connection.py", line 451, in _create_connection
    raise self._reap_last_connection_workflow_error(error)
  File "/home/alfred/.local/lib/python3.10/site-packages/pika/adapters/utils/io_services_utils.py", line 636, in _do_ssl_handshake
    self._sock.do_handshake()
  File "/usr/lib/python3.10/ssl.py", line 1371, in do_handshake
    self._sslobj.do_handshake()
ssl.SSLError: [SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1007)

```

We checked what ssl library we were using in python by running this in the terminal:

```bash
python -c "import ssl; print(ssl.OPENSSL_VERSION)"
```
The version we had was from March 2022 - which was likely part of the issue. I say this because the changes to SSL came about after a critical vulnerability was discovered around this time. We had to update python3 to the latest version on Ubuntu using this:
