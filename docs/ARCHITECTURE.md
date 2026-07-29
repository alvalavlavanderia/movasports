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
- **Exportacao de relatorios:** XLSX com `openpyxl` e PDF com `reportlab`.
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
├── report_exports.py        # Geracao de relatorios PDF e XLSX
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
- APIs de vendas, devoluções, trocas, garantias, condicionais, recebíveis, contas a pagar, caixa e relatórios;
- consultas relacionais paginadas e exportacoes PDF/XLSX dos relatorios oficiais;
- upload de fotos de produtos;
- auditoria;
- importação, exportação, reset e backup.

Arquivos auxiliares:

- `environment_config.py`: reconhece o ambiente e centraliza capacidades sensíveis sem ler ou expor credenciais.
- `report_exports.py`: transforma o contrato tabular dos relatorios em PDF e XLSX, sem consultar ou alterar o banco.
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

Tabelas funcionais do schema versionado atual:

- `stores`
- `app_state`
- `users`
- `audit_logs`
- `brands`
- `categories`
- `sizes`
- `colors`
- `expense_categories`
- `suppliers`
- `supplier_status_history`
- `customers`
- `customer_status_history`
- `customer_credit_limit_history`
- `products`
- `stock_entry_sequences`
- `stock_entries`
- `stock_entry_items`
- `stock_movements`
- `stock_entry_payables`
- `stock_entry_cancellations`
- `purchase_stock_movements`
- `supplier_return_sequences`
- `supplier_returns`
- `supplier_return_items`
- `supplier_return_allocations`
- `supplier_credits`
- `supplier_credit_usages`
- `supplier_credit_allocations`
- `inventory_movements`
- `inventory_sequences`
- `inventories`
- `inventory_items`
- `inventory_count_events`
- `card_modalities`
- `card_modality_history`
- `sales`
- `sale_items`
- `sale_payments`
- `cash_movements`
- `cash_closings`
- `receivables`
- `receivable_payments`
- `receivable_renegotiations`
- `card_reconciliations`
- `card_reconciliation_items`
- `sale_returns`
- `sale_return_items`
- `sale_return_allocations`
- `sale_return_receivable_reductions`
- `exchange_sequences`
- `exchanges`
- `exchange_return_items`
- `exchange_new_items`
- `exchange_payments`
- `exchange_cancellations`
- `warranty_sequences`
- `warranties`
- `warranty_photos`
- `warranty_events`
- `conditional_sequences`
- `conditionals`
- `conditional_items`
- `conditional_returns`
- `conditional_return_items`
- `conditional_sale_links`
- `payables`
- `payable_payments`
- `payable_events`
- `bank_receipts`
- `sale_cancellations`
- `generated_documents`
- `schema_migrations`

O sistema também mantém um registro JSON em `app_state`, usado para compatibilidade/sincronização com o formato de estado do frontend.

As migrations versionadas ficam em `database_migrations/migrations/` e são
registradas em `database_migrations/registry.py`. A versão 1 preserva o schema
histórico congelado; a versão 2 adiciona os campos e históricos necessários ao
módulo Clientes; a versão 3 adiciona os campos de Fornecedores, os cadastros
auxiliares de tamanho, cor e categoria de despesa, os vínculos persistentes em
Produtos, Contas a Pagar e saídas manuais do Caixa e o histórico de situação do
fornecedor; a versão 4 adiciona o código normalizado e as datas imutáveis do
produto, o documento de Entrada, seus itens, a sequência numérica por loja e os
movimentos de estoque gerados pelas Entradas; a versao 5 adiciona os vinculos
entre Entradas e Contas a Pagar, os cancelamentos de Entrada, as devolucoes ao
fornecedor, seus efeitos financeiros e os creditos de fornecedor; a versao 6
adiciona o livro transacional unificado de estoque, incluindo snapshots,
origem e saldos real, reservado e disponivel; a versao 7 adiciona abertura,
itens, eventos de contagem e sequencias do inventario fisico, cujos ajustes
utilizam o mesmo livro transacional; a versao 8 adiciona as modalidades de
Debito e Credito; a versao 9 adiciona identificadores estaveis e o historico
de vigencias dessas modalidades; a versao 10 adiciona a venda transacional,
snapshots comerciais, idempotencia e efeitos financeiros; a versao 11
adiciona saldo aberto, ajustes, idempotencia de recebimentos e historico de
renegociacao do Crediario; a versao 12 adiciona Condicionais relacionais,
itens com snapshots, retornos parciais, reservas e vinculos atomicos com
Vendas; e a versao 13 amplia devolucoes e adiciona alocacoes financeiras,
reducoes de recebiveis, trocas, cancelamentos de troca, garantias, fotos,
eventos e a origem de reposicao de garantia nas Entradas; e a versao 14
adiciona o ledger financeiro continuo, estornos rastreaveis, pagamentos e
eventos de Contas a Pagar, recorrencias mensais, recebimentos bancarios e
cancelamentos integrais de Venda; e a versao 15 adiciona agrupadores e itens
de conciliacao de cartoes, vinculos de pagamento, diferencas e estornos
rastreaveis; e a versao 16 adiciona documentos gerados com snapshot
historico, origem, formato, numero da via, usuario e idempotencia. O framework
suporta SQLite e PostgreSQL e não executa
migrations automaticamente durante requisições HTTP ou importação WSGI.

O `init_db()` permanece como inicializador legado de compatibilidade e não
substitui a aplicação explícita das migrations versionadas.

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

- não existe senha padrão para o administrador em nenhum ambiente;
- o bootstrap aprovado é executado somente pela CLI `database_bootstrap`, após
  migrations e validação estrutural;
- a senha é fornecida por uma variável temporária cujo nome é informado ao
  comando, nunca como argumento ou configuração permanente;
- o bootstrap exige `MOVA_ALLOW_BOOTSTRAP=true` e confirmações explícitas;
- a credencial inicial é transformada em hash diretamente na tabela `users`
  quando há evidência de banco novo;
- o caminho legado de `init_db()` ainda reconhece `MOVA_ADMIN_PASSWORD`, mas
  essa variável não deve ser configurada no deploy de instalação existente;
- `app_state` não é fonte de autenticação nem de reconstrução da tabela `users`.

Credenciais:

- `users.password_hash` é a única fonte de autenticação e atualização de senha;
- criação e alteração recebem a senha somente durante a requisição e persistem apenas o hash;
- respostas de estado, exportação, sessão e usuários não expõem `password` ou `password_hash`;
- chaves legadas permanecem internamente no `app_state` durante a Fase 1, sem uso, alteração ou exposição;
- instalação existente com `users` vazia e usuários apenas no JSON tem o bootstrap automático bloqueado para evitar perda de acesso.

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
- `MOVA_ALLOW_BOOTSTRAP`
- `MOVA_SECRET_KEY`
- `DATABASE_URL`
- `MOVA_ADMIN_NAME` (compatibilidade legada)
- `MOVA_ADMIN_LOGIN` (compatibilidade legada)
- `MOVA_ADMIN_PASSWORD` (compatibilidade legada; não configurar em instalação existente)
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
   - `/api/stock-entries`
   - `/api/supplier-returns`
   - `/api/supplier-credits`
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
   - `/api/exchanges`
   - `/api/warranties`
   - `/api/conditionals`
   - `/api/catalog/products`
   - `/api/documents`
   - `/api/reports/catalog`
   - `/api/reports/<report_key>`
   - `/api/reports/<report_key>/export`
6. O frontend renderiza as telas como uma SPA simples usando seções e abas em `index.html`.
7. Operações de cadastro, venda, caixa, crediário e contas são enviadas por `fetch` para `/api/*`.
8. O backend valida sessão, processa a operação, grava no banco e registra auditoria quando aplicável.
9. O frontend atualiza o estado em memória/localStorage e re-renderiza a interface.

Autenticação e cache:

- o modo autenticado via `file:` foi descontinuado;
- o ERP exige acesso pelo backend Flask em HTTP/HTTPS;
- indisponibilidade do backend não autoriza login local;
- o navegador não é fonte de sessão, perfil, permissão ou credencial;
- `localStorage` permanece como cache de dados públicos e operacionais, sem senha ou hash;
- dados locais antigos não são usados para autenticação e não recebem novas credenciais.

## Componentes da Etapa Business 17

### Alertas

- `alert_user_states` armazena somente leitura e fixacao por usuario; o
  conteudo do alerta e derivado das fontes operacionais atuais;
- `/api/alerts` oferece consulta, busca, filtros e paginacao;
- as rotas de leitura, fixacao e leitura em massa atualizam apenas o estado do
  usuario autenticado;
- a migration v17 e aditiva e compativel com SQLite e PostgreSQL.

### Score do cliente

- `/api/customers/<id>/score` calcula o indicador no backend;
- o calculo consulta `receivables`, `receivable_payments`,
  `receivable_renegotiations`, `sales` e `sale_payments`;
- nao ha snapshot de score nem efeito automatico sobre limite ou autorizacao
  de credito.

### Dashboard relacional

- `/api/dashboard` consulta fontes relacionais de Vendas, devolucoes,
  pagamentos, Caixa, Contas a Pagar, Crediario, estoque e Condicionais;
- filtros relativos sao resolvidos no fuso `America/Sao_Paulo`;
- campos financeiros sensiveis sao omitidos no backend para Operador;
- o frontend mantem um unico observador leve para a virada do dia e limpa o
  cache ao trocar de sessao.

## Componentes da Etapa Business 18

### Configuracoes da loja

- `store_settings` mantem os dados cadastrais, identidade visual, preferencias
  documentais, dados informativos de Pix e disponibilidade das formas de
  pagamento;
- `/api/settings/store` oferece leitura e alteracao exclusivas para
  Administrador, com versao otimista e auditoria;
- `/api/store/operational-settings` entrega somente nome, logo e meios
  operacionais necessarios ao frontend, sem expor configuracao interna;
- o upload da logo usa o armazenamento de midia ja suportado pelo sistema e
  valida tipo, tamanho e versao da configuracao.

### Preferencias e acessos

- `user_preferences` isola o tema visual por loja e usuario;
- `/api/me/preferences` permite tema claro, escuro ou conforme o sistema;
- `/api/settings/access-matrix` apresenta a matriz fixa de Administrador e
  Operador, calculada pelo backend;
- o frontend nao cria perfis ou permissoes personalizadas.

### Seguranca dos usuarios

- `users.failed_login_attempts`, `users.blocked_at` e `users.last_login_at`
  preservam o estado de autenticacao;
- o quinto erro consecutivo bloqueia o usuario de forma persistente;
- somente Administrador pode desbloquear, criar, editar ou desativar usuarios;
- desativacao preserva o registro e o ultimo Administrador ativo nao pode ser
  removido ou rebaixado;
- a migration v18 e aditiva e compativel com SQLite e PostgreSQL.

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
