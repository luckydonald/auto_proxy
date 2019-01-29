# auto_proxy


## Labels

### Insert environment variables
On supported labels you can insert environment variables of that container.
Syntax is `§{VAR_NAME}`. 
Example: 
```yml
app:
    # ...
    environment:
        URL_PATH: "service"
        API_VERSION: "v1"
        URL_HOSTNAME: "example.com"
    labels:
        auto_proxy.enable: "1" 
        auto_proxy.host: "§{URL_HOSTNAME}"
        auto_proxy.mount_point: "/§{URL_PATH}/%{API_VERSION}/"
        auto_proxy.access: socket
```

Would result in the labels
- `auto_proxy.enable`: `1`
- `auto_proxy.host`: `example.com`
- `auto_proxy.mount_point`: `/service/v1/`
- `auto_proxy.access`: `socket`

### List of available labels

#### `auto_proxy.enable`
Must be set to `1` to let it be picked up by `auto_proxy`.

Note: This label doesn't support [environment variables](#insert-environment-variables).

#### `auto_proxy.host`
Hostname where to serve it from.
E.g. `example.com,www.example.com`


#### `auto_proxy.access`
- `net`: Use normal port based proxy (default)
- `socket`: Use file based socket

#### `auto_proxy.protocol`
- `http`: Just proxy it through. (default)
- `uwsgi`: Use the `uwsgi` protocol instead.


#### `auto_proxy.port`
> Used only if `auto_proxy.access = net`.

Set an port on the container to use.

Default: `80`

#### `auto_proxy.mount_point`
Set a mount point on the host.

Default: `/{service_name_short}`
Where `{service_name_short}` is the name of the container,
or just the service name in case of docker compose.

#### `auto_proxy.container_path`
#### Not implemented
Set an path in the container to use.

Default: `/` (root)
