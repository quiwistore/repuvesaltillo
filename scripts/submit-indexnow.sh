#!/bin/bash
# Submit all URLs to IndexNow (Bing + Yandex via Cloudflare + others)
# Uso: bash scripts/submit-indexnow.sh

export DOMAIN="repuvesaltillo.com"
export KEY="da6db3e70d8d4d77b1af7f7bed36b47a"

URLS=$(python3 -c "
import json, os
domain = os.environ['DOMAIN']
with open('data/repuve.json') as f:
    d = json.load(f)
urls = [f'https://{domain}/']
for p in d['pages_centrales']:
    urls.append(f\"https://{domain}/{p['slug']}/\")
urls.append(f'https://{domain}/oficinas/')
for o in d['oficinas']:
    urls.append(f\"https://{domain}/oficinas/{o['slug']}/\")
for s in ['aviso-de-privacidad','contacto','sobre-nosotros']:
    urls.append(f'https://{domain}/{s}/')
print(json.dumps(urls))
")

TOTAL=$(echo $URLS | python3 -c 'import json,sys; print(len(json.loads(sys.stdin.read())))')
echo "Enviando $TOTAL URLs a IndexNow..."

curl -sk -X POST 'https://api.indexnow.org/IndexNow' \
  -H 'Content-Type: application/json; charset=utf-8' \
  -d "{
    \"host\": \"${DOMAIN}\",
    \"key\": \"${KEY}\",
    \"keyLocation\": \"https://${DOMAIN}/${KEY}.txt\",
    \"urlList\": ${URLS}
  }" \
  -w "\n\nHTTP Status: %{http_code}\n"

echo ""
echo "Códigos esperados:"
echo "  200 OK = aceptado y procesado"
echo "  202 Accepted = aceptado, en cola"
echo "  403 SiteVerificationNotCompleted = esperá 10-30 min más, IndexNow aún no validó el key.txt"
