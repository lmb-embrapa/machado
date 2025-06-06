#!/bin/bash

# Esperar o Elasticsearch ficar disponível
until curl -s http://localhost:9200; do
  echo "Aguardando Elasticsearch..."
  sleep 2
done

if ! curl -s -I http://localhost:9200/haystack | grep -q "200 OK"; then
  # Criar o índice haystack apenas se ele não existir
  curl -XPUT "http://localhost:9200/haystack" -H "Content-Type: application/json" -d '{
    "settings": {
      "index": {
        "max_result_window": 500000
      }
    }
  }'
  echo "Índice haystack criado com sucesso!"
else
  echo "Índice haystack já existe. Nada a fazer."
fi
 45 changes: 45 additions & 0 deletions45  
docker-compose.yml
