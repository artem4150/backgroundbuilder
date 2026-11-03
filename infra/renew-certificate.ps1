# Run from the ASCII project alias C:/Users/artem/composition-build.
$ErrorActionPreference='Stop'
docker compose --profile tls run --rm certbot renew --quiet
if ($LASTEXITCODE -ne 0) { throw 'Certificate renewal failed' }
docker compose -f compose.yaml -f compose.tls.yaml exec nginx nginx -t
if ($LASTEXITCODE -ne 0) { throw 'Nginx config check failed' }
docker compose -f compose.yaml -f compose.tls.yaml exec nginx nginx -s reload
