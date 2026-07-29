# Deploy no Railway com PostgreSQL

Este projeto roda no Railway usando Flask, Gunicorn e PostgreSQL gerenciado.

## 1. Adicionar PostgreSQL

No projeto do Railway:

1. Clique em **New** ou **Create**.
2. Escolha **Database**.
3. Escolha **PostgreSQL**.
4. Depois conecte o banco ao servico `web`.

Ao conectar, o Railway fornece automaticamente a variavel:

```text
DATABASE_URL
```

O sistema usa PostgreSQL sempre que essa variavel existir.

## 2. Variaveis do servico web

No servico `web`, configure:

```text
APP_ENV=production
MOVA_SECRET_KEY=troque-por-uma-chave-grande-com-pelo-menos-32-caracteres
MOVA_ALLOW_MIGRATIONS=false
MOVA_ALLOW_DATA_IMPORT_RESET=false
MOVA_ALLOW_BOOTSTRAP=false
MOVA_SESSION_HOURS=12
MOVA_LOGIN_ATTEMPTS=5
MOVA_LOGIN_WINDOW_SECONDS=900
```

Nao precisa configurar `MOVA_DB` para PostgreSQL.

Nao mantenha senha inicial no ambiente de uma instalacao existente. Em banco
realmente novo, migrations e bootstrap devem ser executados explicitamente,
conforme `docs/BUSINESS_RELEASE_READINESS.md` e
`docs/database_bootstrap.md`.

## 3. Start command

O Railway deve detectar o `railway.json` e usar:

```text
gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
```

## 4. Conferir depois do deploy

Acesse:

```text
/api/health
```

O retorno esperado e:

```json
{
  "ok": true,
  "message": "Mova Sports ativo.",
  "database": "PostgreSQL"
}
```

Confira tambem:

```text
/api/readiness
```

Depois entre com um usuario ja existente. O healthcheck confirma o processo;
readiness confirma a compatibilidade estrutural do banco.

## 5. Migrations

O deploy nao executa migrations no startup. Antes de publicar uma versao que
exija schema novo:

1. consulte `python -m database_migrations status`;
2. crie snapshot ou backup logico;
3. autorize migrations somente no processo administrativo;
4. aplique as pendencias com confirmacao de producao;
5. retorne `MOVA_ALLOW_MIGRATIONS=false`;
6. valide novamente o status e `/api/readiness`.

Nunca aplique baseline ou migration por suposicao. Banco legado, checksum
divergente, lacuna ou versao futura exigem interrupcao e diagnostico.

## 6. Fotos de produtos e logo

O PostgreSQL resolve a persistencia dos cadastros, vendas e financeiro.

Para persistir fotos de produtos, configure Cloudinary no servico `web`.

Variaveis aceitas:

```text
CLOUDINARY_URL=cloudinary://...
CLOUDINARY_FOLDER=mova-sports/products
```

Ou, se preferir separar as credenciais:

```text
CLOUDINARY_CLOUD_NAME=seu-cloud-name
CLOUDINARY_API_KEY=sua-api-key
CLOUDINARY_API_SECRET=seu-api-secret
CLOUDINARY_FOLDER=mova-sports/products
```

Quando essas variaveis existem, as novas fotos e a logo da loja sao enviadas
para o Cloudinary e o banco salva a URL publica da imagem. Sem essas variaveis,
o sistema continua usando armazenamento local.

Se ainda nao quiser configurar Cloudinary, remova as variaveis `CLOUDINARY_*` do Railway. O sistema continuara funcionando, mas fotos enviadas podem nao sobreviver a redeploys.
