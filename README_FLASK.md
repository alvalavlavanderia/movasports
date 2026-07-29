# Mova Sports - Versao Web Local

Esta versao roda em um servidor Flask. Localmente, salva os dados no SQLite `loja.db`. Em hospedagem web, pode usar PostgreSQL via `DATABASE_URL`.

## Rodar

```powershell
pip install -r requirements.txt
python server.py
```

Acesse:

```text
http://127.0.0.1:5005
```

Tambem e possivel alterar host e porta:

```powershell
$env:HOST="0.0.0.0"
$env:PORT="5005"
python server.py
```

## Usuario inicial

O servidor nao cria administrador durante importacao WSGI, health, readiness,
login ou startup do Gunicorn.

Em banco realmente novo, aplique primeiro as migrations e use o bootstrap
administrativo explicito descrito em `docs/database_bootstrap.md`. A senha deve
ser fornecida somente por uma variavel temporaria indicada ao comando; nunca
como argumento, log ou configuracao permanente.

Instalacoes existentes preservam os usuarios e hashes atuais e nao devem
executar bootstrap novamente.

## Producao

Em producao, configure:

```powershell
$env:APP_ENV="production"
$env:MOVA_SECRET_KEY="uma-chave-grande-com-pelo-menos-32-caracteres"
python server.py
```

Regras aplicadas em producao:

- `MOVA_SECRET_KEY` precisa ter pelo menos 32 caracteres.
- Cookie de sessao usa `Secure`, `HttpOnly` e `SameSite=Lax`.
- O sistema bloqueia temporariamente excesso de tentativas de login.
- Headers basicos de seguranca sao enviados em todas as respostas.

Opcional:

```powershell
$env:MOVA_DB="C:\caminho\para\loja.db"
$env:MOVA_SESSION_HOURS="12"
$env:MOVA_LOGIN_ATTEMPTS="5"
$env:MOVA_LOGIN_WINDOW_SECONDS="900"
```

## Deploy web

Para hospedar em uma plataforma web Linux, use:

```text
gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
```

O projeto tambem possui `Procfile` com esse comando, usado por varias plataformas.

Variaveis recomendadas para deploy:

```text
APP_ENV=production
MOVA_SECRET_KEY=uma-chave-grande-com-pelo-menos-32-caracteres
DATABASE_URL=postgresql://...
MOVA_DB_BUSY_TIMEOUT_MS=5000
```

Se `DATABASE_URL` estiver configurado, o sistema usa PostgreSQL. Se nao estiver, usa SQLite local.

Enquanto o sistema usar SQLite, mantenha `--workers 1`. Com PostgreSQL, a persistencia dos cadastros, vendas e financeiro fica no banco gerenciado da hospedagem.

Para Railway, este projeto possui:

- `railway.json`, com comando de start e healthcheck;
- `.railwayignore`, para nao enviar banco local, backups e uploads;
- `RAILWAY.md`, com o passo a passo de deploy usando PostgreSQL.

## Dados

O ERP exige acesso pelo backend Flask em HTTP/HTTPS. Abrir `index.html` por
`file:` nao permite autenticacao nem libera a interface. O navegador nao e
fonte de credenciais ou sessao.

## Banco de dados

Sem `DATABASE_URL`, o sistema usa SQLite. Para uso local, o servidor ativa:

- `foreign_keys`;
- `journal_mode=WAL`;
- `synchronous=NORMAL`;
- `busy_timeout`.

O timeout pode ser configurado:

```powershell
$env:MOVA_DB_BUSY_TIMEOUT_MS="5000"
```

Administrador pode verificar integridade, tamanho, modo WAL e contagem de registros pela tela **Configurações > Saúde do banco**.

## Backup

Ao iniciar o servidor, o sistema cria no maximo um backup automatico por dia na pasta `backups`.

Administrador tambem pode criar backup manual pela API:

```text
POST /api/backups
```

E listar backups:

```text
GET /api/backups
```

Para alterar a pasta:

```powershell
$env:MOVA_BACKUP_DIR="C:\backups-mova"
```

## Fotos de produtos

As novas fotos de produtos enviadas pelo cadastro sao salvas em `uploads/products`.
O banco guarda apenas a URL da imagem.

Para alterar a pasta base dos uploads:

```powershell
$env:MOVA_UPLOAD_DIR="C:\uploads-mova"
```

Em producao, configure Cloudinary para as fotos ficarem fora do servidor:

```text
CLOUDINARY_URL=cloudinary://...
CLOUDINARY_FOLDER=mova-sports/products
```

Tambem e possivel usar `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY` e `CLOUDINARY_API_SECRET` em vez de `CLOUDINARY_URL`.
