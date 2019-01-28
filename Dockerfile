FROM jwilder/docker-gen:latest

COPY nginx.tmpl /etc/docker-gen/templates/nginx.tmpl
CMD [ \
    "-notify-sighup", "nginx", \
    "-watch", "/etc/docker-gen/templates/nginx.tmpl", \
    "/etc/nginx/conf.d/default.conf" \
]
