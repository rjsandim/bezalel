# Gerado pela skill `env` (init). Os placeholders env:CHAVE sao resolvidos a cada
# `env new`/`update`. Ajuste a URL da API para a pasta backend correta.
# Ex.: env:url.api aponta para a pasta "api" do mesmo ambiente.
VITE_API_URL=${env:url.backend}

# Libera o host publico deste ambiente no dev server do Vite (atras do Traefik o
# Vite responde 403 a hosts desconhecidos). Adiciona ao server.allowedHosts sem
# tocar no vite.config — funciona desde que o config nao use allowedHosts:true.
__VITE_ADDITIONAL_SERVER_ALLOWED_HOSTS=${env:host.self}
