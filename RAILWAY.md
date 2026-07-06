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
MOVA_ADMIN_NAME=Administrador
MOVA_ADMIN_LOGIN=admin
MOVA_ADMIN_PASSWORD=troque-por-uma-senha-forte
MOVA_SESSION_HOURS=12
MOVA_LOGIN_ATTEMPTS=5
MOVA_LOGIN_WINDOW_SECONDS=900
```

Nao precisa configurar `MOVA_DB` para PostgreSQL.

Use uma senha forte antes do primeiro deploy, porque o usuario inicial e criado quando o banco ainda nao existe.

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

Depois entre no sistema com o login configurado em `MOVA_ADMIN_LOGIN` e `MOVA_ADMIN_PASSWORD`.

## 5. Fotos de produtos

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

Quando essas variaveis existem, as novas fotos sao enviadas para o Cloudinary e o banco salva a URL publica da imagem. Sem essas variaveis, o sistema continua usando armazenamento local.
