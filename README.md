# Environment Variables


### `VIRTUAL_HOST`
- Sever name
- Loads a nginx config with the same name (`/etc/nginx/vhost.d/$VIRTUAL_HOST`), if available. It will be wrapped in a `server { ... }` block.  
- It also will look for a htaccess file with the same name (`/etc/nginx/htpasswd/$VIRTUAL_HOST`), if available, to provide basic authentication.

### `VIRTUAL_PROTO`
Possible values:

- `http`: Regular proxy. Default.
- `uwsgi`
- `fastcgi`

### `VIRTUAL_PORT`
Set a specific port.  
Default: `80`. 

### `URL_PATH`
The socket's path will be `/sockets/bots/${URL_PATH}.sock`.  
Used only if `VIRTUAL_ACCESS=file`.   

    
### `VIRTUAL_ACCESS`
- `port`: regular network. Default.
- `file`: file based unix socket
If it should access  based sockets or   
Currently only supported for `VIRTUAL_PROTO=uwsgi`.  
Default: `port`.
 
