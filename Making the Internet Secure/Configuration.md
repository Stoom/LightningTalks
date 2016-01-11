# Making the Internet Secure
### Steps
1. Generate self-signed cert to bootstrap reverse proxy
2. Configure reverse proxy (with self-signed cert)
3. Start reverse proxy
4. Update Let's Encrypt certificate
5. Reconfigure reverse proxy with Let's Encrypt certificate
6. Reload reverse proxy
7. Setup crontab job to renew certificate

### Notes
A self-signed certificate is needed to bootstrap the infrastructure 

## Reverse Proxy
### Generate Self-Signed Certificate
```
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt
```

### Nginx Configuration
```Nginx
upstream BackendService {
  server 127.0.0.1:8080 fail_timeout=10s;
}

server {
  listen         80;
  server_name    www.site.com;
  rewrite        ^ https://$server_name$request_uri? permanent;
}

server {
  listen          443 ssl http2;
  server_name     www.site.com;
  ssl_certificate           /etc/letsencrypt/live/www.site.com/fullchain.pem;
  ssl_certificate_key       /etc/letsencrypt/live/www.site.com/privkey.pem;
  ssl_trusted_certificate   /etc/letsencrypt/live/www.site.com/chain.pem;

  ssl_session_timeout       60m;
  ssl_protocols             TLSv1.1 TLSv1.2;

  ssl_ciphers 'ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-DSS-AES128-GCM-SHA256:kEDH+AESGCM:ECDHE-RSA-AES128-SHA256:ECDHE-ECDSA-AES128-SHA256:ECDHE-RSA-AES128-SHA:ECDHE-ECDSA-AES128-SHA:ECDHE-RSA-AES256-SHA384:ECDHE-ECDSA-AES256-SHA384:ECDHE-RSA-AES256-SHA:ECDHE-ECDSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES128-SHA:DHE-DSS-AES128-SHA256:DHE-RSA-AES256-SHA256:DHE-DSS-AES256-SHA:DHE-RSA-AES256-SHA:!aNULL:!eNULL:!EXPORT:!DES:!RC4:!3DES:!MD5:!PSK';
  ssl_prefer_server_ciphers on;

  resolver                  8.8.8.8 8.8.4.4 valid=86400;
  resolver_timeout          10;

  location /.well-known { alias /var/letsencrypt/.well-known/; }
  location / {
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_redirect   http:// https://;

    add_header Pragma "no-cache";

    proxy_pass http://BackendService;
  }
}
```
#### Notes
Multiple servers can be listed under the upstream section to create a load balancer.

## Let's Encrypt Tools
Clone the Let's Encrypt repository from [https://github.com/letsencrypt/letsencrypt.git](https://github.com/letsencrypt/letsencrypt.git).  Once it is cloned enter the new directory and run `./letsencrypt-auto --help` to bootstrap the environment.  
  
Also setup the directory that will be used for the certificate request verification by creating a `/.well-known/` directory.  In this case they are located under `/var/letsencrypt/`.  If applicable set the SE-Linux rules accordingly.

## Update Certificate Script
```shell
#!/bin/bash

SUBJECT_ALT_NAME="www.stie.com"
LETS_ENCRYPT_REPO="/var/letsencrypt"

${LETS_ENCRYPT_REPO}/letsencrypt-auto certonly --webroot -w /var/letsencrypt/ -d ${SUBJECT_ALT_NAME} --renew-by-default

if [ -e /etc/init.d/nginx ]; then
  /etc/init.d/nginx reload
fi
```

#### Notes
Place the above content into `/usr/local/bin/updateLetsEncryptCert.sh` and make executable.

## Crontab Job
```shell
0 0 1 1-12/2 * /usr/local/bin/updateLetsEncryptCert.sh
```
