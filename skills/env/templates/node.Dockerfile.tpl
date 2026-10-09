# Gerado pela skill `env` (init). Ajuste a vontade — este arquivo E versionado.
# Imagem de desenvolvimento Node. Codigo entra por volume (bind mount).
FROM node:${VERSION}-bookworm

WORKDIR /app
COPY boot.sh /usr/local/bin/envstack-boot
EXPOSE ${PORT}
# Bundlers nativos multi-thread (rolldown/turbopack/esbuild) inflam o RSS via arenas
# de malloc do glibc (ate 8x cores). Com 2 arenas um dev server Vite cai de ~700MB
ENV MALLOC_ARENA_MAX=2
# DEV_CMD e montado pelo init conforme o framework detectado:
#   Vite -> npm run dev -- --host 0.0.0.0 --port <porta>
#   Next -> npm run dev -- -H 0.0.0.0 -p <porta>   (Next nao aceita --host/--port)
# Heap do V8 capado no dev server: sem cap o Node ve a RAM inteira da VM e assume
# heap default de ~4GB — GC preguicoso, RSS chega a ~850MB. 512MB e um default
# generico seguro (Next e mais pesado que Vite; p/ Vite da p/ baixar a 256).
# So no dev server: o npm install do 1o boot fica sem cap (transitorio).
CMD ["sh", "/usr/local/bin/envstack-boot", "node", "sh", "-c", "${DEV_CMD}"]
