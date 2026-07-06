# Preparar GitHub para Railway

## 1. Criar repositorio no GitHub

Crie um repositorio privado, por exemplo:

```text
mova-sports-sistema
```

Use repositorio privado para evitar expor estrutura interna do sistema.

## 2. Conferir arquivos que nao devem subir

Estes arquivos e pastas devem ficar somente no computador ou no volume do Railway:

- `loja.db`
- `loja.db-shm`
- `loja.db-wal`
- `backups/`
- `uploads/`
- `flask.log`
- `flask.err`

Eles ja estao protegidos por `.gitignore` e `.railwayignore`.

## 3. Primeiro envio para GitHub

Depois de criar o repositorio no GitHub, rode:

```powershell
git remote add origin https://github.com/SEU-USUARIO/mova-sports-sistema.git
git branch -M main
git push -u origin main
```

## 4. Conectar no Railway

No Railway:

1. New Project.
2. Deploy from GitHub repo.
3. Escolha o repositorio.
4. Configure as variaveis do arquivo `RAILWAY.md`.
5. Crie o volume persistente em `/data`.
6. Faça o deploy.

## 5. Primeiro login

O login inicial sera criado usando:

```text
MOVA_ADMIN_LOGIN
MOVA_ADMIN_PASSWORD
```

Defina esses valores antes do primeiro deploy.
