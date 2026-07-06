# Deploy no Railway

Este projeto ja esta preparado para rodar no Railway usando Flask, Gunicorn e SQLite com volume persistente.

## 1. Criar projeto

1. Envie este projeto para um repositorio GitHub.
2. No Railway, crie um novo projeto a partir desse repositorio.
3. O Railway deve detectar o `railway.json` e usar o comando:

```text
gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
```

## 2. Criar volume persistente

Crie um volume no Railway e monte em:

```text
/data
```

O volume e necessario para manter:

- banco SQLite;
- backups;
- fotos de produtos.

## 3. Variaveis de ambiente

Configure no Railway:

```text
APP_ENV=production
MOVA_SECRET_KEY=troque-por-uma-chave-grande-com-pelo-menos-32-caracteres
MOVA_ADMIN_NAME=Administrador
MOVA_ADMIN_LOGIN=admin
MOVA_ADMIN_PASSWORD=troque-por-uma-senha-forte
MOVA_DB=/data/loja.db
MOVA_BACKUP_DIR=/data/backups
MOVA_UPLOAD_DIR=/data/uploads
MOVA_DB_BUSY_TIMEOUT_MS=5000
MOVA_SESSION_HOURS=12
MOVA_LOGIN_ATTEMPTS=5
MOVA_LOGIN_WINDOW_SECONDS=900
```

Use uma senha forte antes do primeiro deploy, porque o usuario inicial e criado quando o banco ainda nao existe.

## 4. SQLite no Railway

Mantenha:

```text
--workers 1
```

SQLite funciona bem para o inicio, mas nao deve rodar com varios workers gravando no mesmo arquivo. Quando o sistema tiver mais uso, o proximo passo sera migrar para PostgreSQL.

## 5. Conferir depois do deploy

Acesse:

```text
/api/health
```

O retorno esperado e:

```json
{
  "ok": true,
  "message": "Mova Sports ativo."
}
```

Depois entre no sistema com o login configurado em `MOVA_ADMIN_LOGIN` e `MOVA_ADMIN_PASSWORD`.
