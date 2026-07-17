# Arquitetura Atual - Mova Sports

Este documento descreve a arquitetura encontrada no repositório no momento da análise. Ele registra apenas informações confirmadas por arquivos do projeto. Quando algo não pôde ser confirmado pelo código ou documentação existente, foi marcado como **A confirmar**.

## 1. Tecnologias Utilizadas

### Aplicação web atual

- **Backend:** Python com Flask.
- **Servidor WSGI:** Gunicorn em produção.
- **Frontend web:** HTML, CSS e JavaScript puros.
- **Persistência local:** SQLite, usando o arquivo `loja.db`.
- **Persistência em produção:** PostgreSQL quando a variável `DATABASE_URL` está configurada.
- **Uploads de imagens:** armazenamento local em `uploads/products` ou Cloudinary quando configurado.
- **Deploy:** Railway, com configuração em `railway.json` e `Procfile`.
- **PWA:** há `app.webmanifest` e `sw.js`, mas o service worker apenas limpa caches no `activate`.

### Flutter

- **Flutter/Dart:** existe estrutura Flutter no repositório.
- **Dependências Flutter confirmadas:** `google_mlkit_text_recognition`, `image_picker`, `shared_preferences`, `cupertino_icons`.
- O app Flutter encontrado em `lib/main.dart` ainda usa o nome e domínio funcional de um **Conferidor de Bingo**, não do sistema Mova Sports web atual.
- Relação do app Flutter com a aplicação web Mova Sports: **A confirmar**.

## 2. Estrutura de Pastas

Estrutura relevante encontrada:

```text
.
├── android/                 # Projeto Android gerado pelo Flutter
├── assets/                  # Arquivos visuais, incluindo logo
├── backups/                 # Backups locais do SQLite
├── build/                   # Artefatos gerados
├── docs/                    # Documentação do projeto
├── icons/                   # Ícones usados pelo webmanifest
├── lib/                     # Código Flutter/Dart
├── test/                    # Estrutura de testes Flutter
├── uploads/                 # Uploads locais do sistema
├── index.html               # Interface web principal
├── style.css                # Estilos da interface web
├── script.js                # Lógica frontend web
├── server.py                # Backend Flask e acesso a dados
├── environment_config.py    # Ambiente efetivo e capacidades sensíveis
├── wsgi.py                  # Entrada WSGI para produção
├── Procfile                 # Start command para plataformas web
├── railway.json             # Configuração Railway
├── requirements.txt         # Dependências Python
├── pubspec.yaml             # Dependências Flutter
├── app.webmanifest          # Manifest PWA
└── sw.js                    # Service worker
```

Arquivos e pastas ignorados no deploy Railway incluem `android/`, `lib/`, `test/`, `build/`, `.dart_tool/`, bancos locais, backups, uploads e logs, conforme `.railwayignore`.

## 3. Organização do Frontend Flutter

O frontend Flutter encontrado está concentrado em:

- `lib/main.dart`

O arquivo contém:

- `main()` executando `BingoApp`;
- `MaterialApp` com título `Conferidor de Bingo`;
- modelos como `BingoCardModel`, `BingoPattern` e `BingoHit`;
- armazenamento local via `SharedPreferences`;
- uso de `image_picker` e `google_mlkit_text_recognition`;
- tema Material 3.

Não foram encontrados, dentro de `lib/`, módulos separados por telas, serviços, repositórios ou componentes reutilizáveis. A organização Flutter atual é monolítica em um único arquivo.

Integração do Flutter com o backend Flask atual: **A confirmar**.

## 4. Organização do Backend Flask/Python

O backend está concentrado principalmente em `server.py`.

Responsabilidades encontradas no arquivo:

- criação da aplicação Flask;
- configuração de sessão e headers de segurança;
- proteção global das rotas `/api/*`;
- conexão com SQLite ou PostgreSQL;
- criação das tabelas no `init_db()`;
- sincronização entre tabelas relacionais e `app_state`;
- autenticação e controle de sessão;
- APIs de produtos, clientes, fornecedores, marcas, categorias e usuários;
- APIs de vendas, devoluções, condicionais, recebíveis, contas a pagar, caixa e relatórios;
- upload de fotos de produtos;
- auditoria;
- importação, exportação, reset e backup.

Arquivos auxiliares:

- `environment_config.py`: reconhece o ambiente e centraliza capacidades sensíveis sem ler ou expor credenciais.
- `wsgi.py`: importa somente `app`, sem inicializar banco, executar migrations ou alterar dados durante a importação.
- `requirements.txt`: dependências Python.
- `Procfile`: comando Gunicorn.
- `railway.json`: start command e healthcheck.

Não há uma separação atual em blueprints, services, repositories ou módulos Python independentes. A arquitetura Flask está centralizada em um único arquivo.

## 5. Banco de Dados Encontrado

O sistema suporta dois modos:

- **SQLite local:** usado quando `DATABASE_URL` não está configurado.
- **PostgreSQL:** usado quando `DATABASE_URL` está configurado.

No SQLite, o arquivo padrão é:

```text
loja.db
```

Configurações SQLite confirmadas:

- `PRAGMA foreign_keys = ON`;
- `PRAGMA busy_timeout`;
- `PRAGMA journal_mode = WAL`;
- `PRAGMA synchronous = NORMAL`.

Tabelas criadas pelo `init_db()`:

- `stores`
- `app_state`
- `users`
- `audit_logs`
- `brands`
- `categories`
- `suppliers`
- `customers`
- `products`
- `sales`
- `sale_items`
- `sale_payments`
- `cash_movements`
- `cash_closings`
- `receivables`
- `receivable_payments`
- `sale_returns`
- `sale_return_items`
- `payables`

O sistema também mantém um registro JSON em `app_state`, usado para compatibilidade/sincronização com o formato de estado do frontend.

Não foram encontrados arquivos separados de migration. A criação/evolução de schema acontece dentro de `init_db()` com `CREATE TABLE IF NOT EXISTS` e alguns `ALTER TABLE` condicionais.

## 6. Como Funciona a Autenticação

A autenticação é baseada em sessão Flask.

Fluxo confirmado:

1. O frontend chama `POST /api/login`.
2. O backend busca o usuário na tabela `users`.
3. A senha é validada com `check_password_hash`.
4. Em caso de sucesso, o backend grava o usuário público em `session["user"]`.
5. As rotas `/api/*`, exceto `/api/health`, `/api/session`, `/api/login` e `/api/logout`, exigem sessão ativa.
6. Antes de atender APIs protegidas, o backend recarrega o usuário do banco e invalida a sessão se o usuário não existir ou estiver inativo.
7. `POST /api/logout` remove `session["user"]`.

Configurações de sessão confirmadas:

- `SESSION_COOKIE_HTTPONLY=True`;
- `SESSION_COOKIE_SAMESITE="Lax"`;
- `SESSION_COOKIE_SECURE=True` em produção;
- tempo de sessão configurável por `MOVA_SESSION_HOURS`.

Há controle de excesso de tentativas de login em memória, usando `MOVA_LOGIN_ATTEMPTS` e `MOVA_LOGIN_WINDOW_SECONDS`.

Usuário inicial:

- em desenvolvimento, se não configurado, o padrão é `admin` / `1234`;
- em produção, `MOVA_ADMIN_PASSWORD` é obrigatório e precisa atender validações mínimas.

Permissões:

- há função `require_admin()` para ações restritas a administrador;
- matriz completa de permissões por perfil: **A confirmar**.

## 7. Como os Uploads São Tratados

Endpoint confirmado:

```text
POST /api/uploads/product-photo
```

Regras confirmadas:

- campo esperado: `photo`;
- extensões aceitas: `jpg`, `jpeg`, `png`, `webp`;
- tamanho máximo: 5 MB;
- nomes locais são sanitizados com `secure_filename`;
- o banco guarda a URL retornada para a imagem.

Modos de armazenamento:

1. **Cloudinary**
   - usado quando `CLOUDINARY_URL` começa com `cloudinary://`; ou
   - quando `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY` e `CLOUDINARY_API_SECRET` estão configurados.
   - pasta padrão: `mova-sports/products`, configurável por `CLOUDINARY_FOLDER`.

2. **Local**
   - usado quando Cloudinary não está configurado;
   - salva arquivos em `uploads/products`;
   - serve imagens por `GET /uploads/products/<filename>`.

Persistência de uploads locais em produção: **A confirmar**. A documentação recomenda Cloudinary porque uploads locais podem não sobreviver a redeploys.

## 8. Serviços Externos Utilizados

Serviços confirmados por arquivos do projeto:

- **Railway:** deploy, healthcheck e execução com Gunicorn.
- **PostgreSQL:** banco gerenciado quando `DATABASE_URL` está configurado.
- **Cloudinary:** armazenamento externo de fotos de produtos quando configurado.
- **GitHub:** mencionado na documentação de deploy como origem para Railway.

Serviços não confirmados pelo código:

- provedor DNS/domínio em produção: **A confirmar**;
- serviço externo de e-mail, WhatsApp, maquininha ou banco: **A confirmar**.

## 9. Como Ocorre o Deploy

Deploy confirmado para Railway.

Arquivos envolvidos:

- `railway.json`
- `Procfile`
- `wsgi.py`
- `requirements.txt`
- `.railwayignore`

Comando de start:

```text
gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120
```

Healthcheck:

```text
/api/health
```

Importar `wsgi.py` não executa `init_db()`, migrations ou backups. Os fluxos atuais que chamam explicitamente `init_db()` permanecem no backend e serão revisados em uma etapa própria.

Em PostgreSQL, backups por arquivo não são aplicados pelo sistema; a documentação orienta usar backup/snapshot da hospedagem.

Variáveis importantes confirmadas:

- `APP_ENV`
- `MOVA_ALLOW_MIGRATIONS`
- `MOVA_ALLOW_DATA_IMPORT_RESET`
- `MOVA_SECRET_KEY`
- `DATABASE_URL`
- `MOVA_ADMIN_NAME`
- `MOVA_ADMIN_LOGIN`
- `MOVA_ADMIN_PASSWORD`
- `MOVA_SESSION_HOURS`
- `MOVA_LOGIN_ATTEMPTS`
- `MOVA_LOGIN_WINDOW_SECONDS`
- `MOVA_DB`
- `MOVA_DB_BUSY_TIMEOUT_MS`
- `MOVA_BACKUP_DIR`
- `MOVA_UPLOAD_DIR`
- `CLOUDINARY_URL`
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`
- `CLOUDINARY_FOLDER`

### Ambientes

O módulo `environment_config.py` aceita somente `development`, `staging` e `production`. Ausência ou valor inválido de `APP_ENV` não é convertido silenciosamente em desenvolvimento: a aplicação permanece temporariamente operacional em modo compatível e restritivo.

As capacidades de migrations e importação/reset ficam desabilitadas por padrão. Mesmo que as respectivas flags sejam habilitadas, `production`, ambiente ausente ou ambiente inválido não adquirem essas capacidades. Nesta fase, as rotas ainda não consultam a capacidade de importação/reset; esse bloqueio pertence à atividade de segurança seguinte.

As configurações e instruções manuais estão em `docs/ENVIRONMENTS.md`.

## 10. Fluxo Geral da Aplicação

Fluxo web confirmado:

1. O usuário acessa `/`.
2. Flask serve `index.html`.
3. `index.html` carrega `style.css` e `script.js`.
4. O JavaScript inicializa eventos, aplica sessão local e consulta `/api/session`.
5. Após login, o frontend carrega dados pelas APIs modulares:
   - `/api/products`
   - `/api/customers`
   - `/api/suppliers`
   - `/api/brands`
   - `/api/categories`
   - `/api/users`
   - `/api/sales`
   - `/api/receivables`
   - `/api/payables`
   - `/api/cash-movements`
   - `/api/cash-closings`
   - `/api/returns`
   - `/api/conditionals`
6. O frontend renderiza as telas como uma SPA simples usando seções e abas em `index.html`.
7. Operações de cadastro, venda, caixa, crediário e contas são enviadas por `fetch` para `/api/*`.
8. O backend valida sessão, processa a operação, grava no banco e registra auditoria quando aplicável.
9. O frontend atualiza o estado em memória/localStorage e re-renderiza a interface.

Fallback confirmado:

- se o sistema for aberto via `file:`, `script.js` desativa o backend e usa `localStorage`;
- quando servido via Flask, usa APIs do backend e mantém `localStorage` como cache/estado local.

## Arquivos Analisados

- `AGENTS.MD`
- `docs/PROJECT_CONTEXT.md`
- `docs/SECURITY.md`
- `docs/BUSINESS_RULES.md`
- `docs/UI_STANDARDS.md`
- `docs/TESTING.md`
- `docs/BACKLOG.md`
- `docs/ARCHITECTURE.md`
- `server.py`
- `environment_config.py`
- `wsgi.py`
- `requirements.txt`
- `Procfile`
- `railway.json`
- `.railwayignore`
- `.env.example`
- `README.md`
- `README_FLASK.md`
- `RAILWAY.md`
- `GITHUB_DEPLOY.md`
- `index.html`
- `script.js`
- `style.css`
- `pubspec.yaml`
- `lib/main.dart`
- `app.webmanifest`
- `sw.js`
