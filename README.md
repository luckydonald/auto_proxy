# auto_proxy
#### TODO: rename 'über_prox' or 'doprox'

## `auto_proxy` Environment Variables
Use environment variables to configure the `auto_proxy` container.

### List of available environment variables
#### `SIGNALS`
> Note: Any containers with the [`auto_proxy.signal` label](#auto_proxy-signal) will be automatically added to this list, with the correct container id. 
> Therefore you should prefer setting the `auto_proxy.signal` label on a specific container over using this. This is intended only for containers where you somehow can't set the labels.  

On creation of a new config file it can send signals to other containers, to e.g. reload configuration files.
Provide key-value like `container=signal`.

- `container` can be either the name or the id of the container.
- `signal` can be either the case insensitive signal name, or it's number.

If you want to send multiple signals make a comma separated list.  

For example:
```dotenv
SIGNALS=nginx=sighup,nginx=1,nginx=SIGHUB
```  
This would send `SIGHUP` 3 times to the `nginx` container.


## Container Labels

### Insert environment variables
On supported labels you can insert environment variables of that container.
Syntax is `§{VAR_NAME}`.
 
### List of available labels

#### `auto_proxy.signal`
> You don't need to set `auto_proxy.enable` for this to work.

This container will be send an signal in case of a change in configuration.
Can be the signal number or the case insensitive name.
Also a comma separated list of multiple signals to send is possible.

Example: `auto_proxy.signal: SIGHUP,1,sighup` would have it send the `SIGHUP` signal 3 times. 

Note: This label don't support [environment variables](#insert-environment-variables).


#### `auto_proxy.enable`
Must be set to `1` to let it be picked up by `auto_proxy` for generating a config.

Note: This label don't support [environment variables](#insert-environment-variables).

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

Default: `/service_name_short`,
Where `service_name_short` is the name of the container,
or just the service name in case of docker compose.

#### `auto_proxy.buffer`
If we want to buffer the response before sending.  
Set to `1` to enable, `0` to disable.

Default: `1`  
Like the [nginx default](http://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_buffering).

#### `auto_proxy.enforce_https`
If we encounter a connection with `http`, should we redirect to `https://$server_name$request_uri`?
 
- `0`: off. Don't perform any checks. `https` stays `https`, `http` keeps being `http`.
- `client`: The scheme of the client directly connected.  
- `proxy`: We are behind another proxy (e.g. cloudflare), and we want to look into the `X-Forwarded-Proto` header. Enable only if you trust that proxy to set the header correctly.
- `1`: Default. Basically an "auto" mode trying `proxy` and `client`. If there is a `X-Forwarded-Proto` header, use that, else use the connection's scheme. Note, if you are not behind a proxy, clients could set that header.


#### `auto_proxy.socket_name`
> Used only if `auto_proxy.access = socket`.

Custom socket file name.

Default: `service_name_short.sock`,
Where `service_name_short` is the name of the container,
or just the service name in case of docker compose.


#### `auto_proxy.container_path`
#### Not implemented
Set an path in the container to use.

Default: `/` (root)


## Example `docker-compose.yml`

Having something like  
```yml
version: "2.3" # probably newer is fine too.

volumes:
  auto_proxy:
    external: false
    driver: local
    
services:
  auto_proxy:
    restart: 'always'
    image: luckydonald/auto_proxy
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - auto_proxy:/output/
  proxy:
    restart: 'always'
    image: nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - auto_proxy:/etc/nginx/conf.d/
    labels:
      auto_proxy.signal: SIGHUP
    
  app:
    # ...
    image: 'jwilder/whoami'  # for example
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

Would result in ´app´ having the labels
- `auto_proxy.enable`: `1`
- `auto_proxy.host`: `example.com`
- `auto_proxy.mount_point`: `/service/v1/`
- `auto_proxy.access`: `socket`

And the `proxy` container getting a `SIGHUP` signal
after any configuration change. 
