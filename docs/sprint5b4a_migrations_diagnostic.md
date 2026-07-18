# Sprint 5B.4A - Diagnostico e plano de migrations versionadas

## 1. Resumo executivo

Esta analise foi realizada exclusivamente sobre o commit
`1432e544a7150e58c719b5c20b3159463fdbbe3e`, na branch
`sprint5b4a/diagnose-versioned-migrations` e no worktree isolado
`C:\Bingo\build\sprint5b4a`.

O banco atual possui 19 tabelas de aplicacao e 30 indices criados por
`init_db()`. A mesma funcao tambem:

- insere a loja `matriz`;
- cria o registro inicial de `app_state`;
- pode criar o administrador inicial;
- executa a evolucao implicita de `payables.discount`;
- pode reconstruir todas as tabelas de negocio a partir do JSON de
  `app_state`.

Portanto, `init_db()` nao e apenas um inicializador estrutural. Ele mistura
schema, migration, bootstrap, deteccao de estado legado e reconstrucao de
dados. A substituicao segura exige migrations explicitas fora do ciclo HTTP,
bootstrap separado e retirada gradual das chamadas restantes de `init_db()`.

Recomendacao central:

1. adotar uma baseline formal `001` que represente o schema atual completo;
2. registrar uma linha imutavel por migration em `schema_migrations`;
3. usar checksum SHA-256 desde a primeira migration;
4. criar bancos novos somente por comando administrativo explicito;
5. registrar bancos legados por baseline explicita, depois de validacao
   estrutural rigorosa e backup;
6. manter migrations, bootstrap e requests HTTP como fluxos separados;
7. nao executar migration, bootstrap ou reconstrucao em import de modulo,
   WSGI, health, readiness, login ou rota administrativa comum.

Nenhum SQL foi executado nesta sprint. Nenhuma migration, tabela ou dado foi
criado ou alterado.

## 2. Base analisada e caminhos de inicializacao

| Item | Resultado |
|---|---|
| Repositorio | `C:\Bingo` |
| Worktree | `C:\Bingo\build\sprint5b4a` |
| Branch | `sprint5b4a/diagnose-versioned-migrations` |
| HEAD inicial | `1432e544a7150e58c719b5c20b3159463fdbbe3e` |
| Branch base | `sprint5b3/database-readiness` |
| Base esperada | `1432e544a7150e58c719b5c20b3159463fdbbe3e` |
| `main` local | `a5fceba7e08ca779973e6d683867c7c4bab81530` |
| `origin/main` | `a5fceba7e08ca779973e6d683867c7c4bab81530` |
| Estado inicial | worktree limpa e base exata |

### 2.1 Startup real

- `python server.py`: executa `init_db()`, depois
  `ensure_startup_backup()` e inicia o servidor Flask.
- `python -m flask --app server run` (usado por `run_flask.ps1`): importa
  `server`, mas nao entra no bloco `if __name__ == "__main__"`; nao executa
  `init_db()` no import.
- WSGI: `wsgi.py` apenas importa `app` de `server`.
- Gunicorn/Railway: `gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1
  --threads 4 --timeout 120`.
- Healthcheck Railway: `/api/health`; a rota nao abre o banco.
- Readiness: `/api/readiness`; usa conexao somente leitura e nao executa DDL
  ou DML.
- Nao existe `Dockerfile`, `package.json`, script `.bat`, `.cmd` ou `.sh` no
  commit analisado. Existem `Procfile`, `railway.json`, `wsgi.py` e
  `run_flask.ps1`.

Consequencia: no caminho WSGI/Gunicorn, o schema atual nao e criado no import.
Entretanto, muitas requisicoes ainda chamam `init_db()` direta ou
indiretamente e podem executar DDL, bootstrap e reconstrucao no primeiro uso.

## 3. Conexao e diferencas entre bancos

### 3.1 `connect_db()`

**SQLite**

- abre `DB_PATH` com `sqlite3.connect`, criando o arquivo se ele nao existir;
- configura `row_factory = sqlite3.Row`;
- executa `PRAGMA foreign_keys = ON`;
- executa `PRAGMA busy_timeout`;
- executa `PRAGMA journal_mode = WAL` (efeito persistente no arquivo);
- executa `PRAGMA synchronous = NORMAL`.

**PostgreSQL**

- usa `psycopg2` por meio de `PgConnection`;
- traduz `?` para `%s`;
- ignora SQL iniciado por `PRAGMA`;
- traduz somente o `INSERT OR IGNORE` conhecido da loja matriz para
  `ON CONFLICT (id) DO NOTHING`;
- faz commit ao sair sem erro e rollback ao sair com erro.

### 3.2 Divergencias relevantes

- `TEXT`, `INTEGER` e `REAL` sao usados nos dois bancos. Em PostgreSQL isso
  mantem timestamps como texto e valores financeiros como `REAL`, nao como
  `TIMESTAMPTZ`/`NUMERIC`.
- SQLite exige `PRAGMA foreign_keys = ON` por conexao; PostgreSQL aplica FKs
  nativamente.
- SQLite consulta `PRAGMA table_info(payables)` antes do `ALTER`; PostgreSQL
  usa `ADD COLUMN IF NOT EXISTS`.
- `CREATE ... IF NOT EXISTS` evita erro por nome existente, mas nao valida se
  o objeto existente possui colunas, constraints ou definicao corretas.
- Indices parciais (`cpf` e `barcode`) sao aceitos por ambos.
- O adaptador PostgreSQL nao oferece uma abstracao especifica de migration,
  lock ou timeout. O executor futuro deve usar conexao dedicada.
- `connect_db()` nao e adequado como unico mecanismo do migration runner,
  porque no SQLite altera `journal_mode` durante a abertura.

## 4. Inventario ordenado de `init_db()`

Legenda de classificacao:

- **SCHEMA_BASELINE**: estrutura necessaria para banco novo;
- **MIGRATION**: evolucao de schema existente;
- **INDEX**: indice ou unicidade;
- **BOOTSTRAP**: dado operacional minimo;
- **SEED**: dado opcional/demonstrativo;
- **RECONSTRUCTION**: sincronizacao ampla de dados;
- **RUNTIME**: deteccao ou operacao de execucao;
- **LEGACY_UNKNOWN**: finalidade nao comprovada.

Nas linhas de `CREATE ... IF NOT EXISTS`, a reexecucao normalmente nao falha,
mas tambem nao corrige definicoes divergentes. Todos os objetos dependentes
pressupoem que o objeto anterior tenha a forma esperada.

| # | Linha | Operacao | Classe | SQLite / PostgreSQL | Idempotencia e risco |
|---:|---:|---|---|---|---|
| 1 | 983 | habilitar foreign keys | RUNTIME | PRAGMA / ignorado | Por conexao; baixo risco |
| 2 | 984 | criar `stores` | SCHEMA_BASELINE | igual | Nome idempotente; nao valida forma |
| 3 | 993 | inserir `matriz` | BOOTSTRAP | `OR IGNORE` / `ON CONFLICT` | Idempotente por `id`; cria dado de negocio |
| 4 | 997 | criar `app_state` | SCHEMA_BASELINE | igual | Nome idempotente; depende apenas do banco |
| 5 | 1006 | consultar `app_state.id=1` | RUNTIME | igual | Somente leitura |
| 6 | 1009 | inserir estado inicial se ausente | BOOTSTRAP | igual | Condicional; JSON inclui descritor publico de admin |
| 7 | 1013 | criar `users` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 8 | 1028 | criar `idx_users_store_login` | INDEX | igual | Idempotente por nome; unicidade pode falhar com duplicatas |
| 9 | 1029 | criar `audit_logs` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 10 | 1046 | criar `idx_audit_store_created` | INDEX | igual | Idempotente por nome |
| 11 | 1047 | criar `idx_audit_module` | INDEX | igual | Idempotente por nome |
| 12 | 1048 | ler JSON de `app_state` | RUNTIME | igual | Somente leitura |
| 13 | 1049 | interpretar JSON ou usar default | RUNTIME | igual | JSON invalido e ocultado por fallback |
| 14 | 1053 | contar usuarios | RUNTIME | igual | Somente leitura |
| 15 | 1054 | criar admin ou emitir aviso | BOOTSTRAP | igual | Usa `MOVA_ADMIN_PASSWORD`; sem auditoria |
| 16 | 1065 | criar `brands` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 17 | 1076 | criar `idx_brands_store_name` | INDEX | igual | Unico; pode falhar com duplicatas |
| 18 | 1077 | criar `categories` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 19 | 1088 | criar `idx_categories_store_name` | INDEX | igual | Unico; pode falhar com duplicatas |
| 20 | 1089 | criar `suppliers` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 21 | 1104 | criar `customers` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 22 | 1127 | criar `idx_customers_store_name` | INDEX | igual | Idempotente por nome |
| 23 | 1128 | criar `idx_customers_store_cpf` | INDEX | igual | Unico/parcial; pode falhar com CPFs duplicados |
| 24 | 1135 | criar `products` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 25 | 1159 | criar `idx_products_store_barcode` | INDEX | igual | Unico/parcial; pode falhar com codigos duplicados |
| 26 | 1166 | criar `sales` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 27 | 1184 | criar `idx_sales_store_created` | INDEX | igual | Idempotente por nome |
| 28 | 1185 | criar `idx_sales_customer` | INDEX | igual | Sem FK para customer |
| 29 | 1186 | criar `sale_items` | SCHEMA_BASELINE | igual | Depende de `sales`; cascade |
| 30 | 1203 | criar `idx_sale_items_sale` | INDEX | igual | Idempotente por nome |
| 31 | 1204 | criar `idx_sale_items_product` | INDEX | igual | Sem FK para product |
| 32 | 1205 | criar `sale_payments` | SCHEMA_BASELINE | igual | Depende de `sales`; cascade |
| 33 | 1219 | criar `idx_sale_payments_sale` | INDEX | igual | Idempotente por nome |
| 34 | 1220 | criar `idx_sale_payments_method` | INDEX | igual | Idempotente por nome |
| 35 | 1221 | criar `cash_movements` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 36 | 1237 | criar `idx_cash_store_created` | INDEX | igual | Idempotente por nome |
| 37 | 1238 | criar `idx_cash_method` | INDEX | igual | Idempotente por nome |
| 38 | 1239 | criar `idx_cash_ref` | INDEX | igual | Idempotente por nome |
| 39 | 1240 | criar `cash_closings` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 40 | 1260 | criar `idx_cash_closings_store_date` | INDEX | igual | Idempotente por nome |
| 41 | 1261 | criar `receivables` | SCHEMA_BASELINE | igual | Depende de `stores` |
| 42 | 1283 | criar `idx_receivables_store_due` | INDEX | igual | Idempotente por nome |
| 43 | 1284 | criar `idx_receivables_status` | INDEX | igual | Idempotente por nome |
| 44 | 1285 | criar `idx_receivables_sale` | INDEX | igual | Sem FK para sale |
| 45 | 1286 | criar `idx_receivables_customer` | INDEX | igual | Sem FK para customer |
| 46 | 1287 | criar `receivable_payments` | SCHEMA_BASELINE | igual | Depende de `stores` e `receivables`; cascade |
| 47 | 1304 | criar `idx_receivable_payments_receivable` | INDEX | igual | Idempotente por nome |
| 48 | 1305 | criar `idx_receivable_payments_customer` | INDEX | igual | Idempotente por nome |
| 49 | 1306 | criar `sale_returns` | SCHEMA_BASELINE | igual | Depende de `stores`; `sale_id` sem FK |
| 50 | 1321 | criar `idx_returns_store_created` | INDEX | igual | Idempotente por nome |
| 51 | 1322 | criar `idx_returns_sale` | INDEX | igual | Idempotente por nome |
| 52 | 1323 | criar `sale_return_items` | SCHEMA_BASELINE | igual | Depende de `sale_returns`; cascade |
| 53 | 1338 | criar `idx_return_items_return` | INDEX | igual | Idempotente por nome |
| 54 | 1339 | criar `payables` | SCHEMA_BASELINE | igual | Depende de `stores`; schema novo ja inclui discount |
| 55 | 1361 | detectar/adicionar `payables.discount` | MIGRATION | `PRAGMA`+ALTER / ALTER IF NOT EXISTS | Aditiva; redundante em banco novo |
| 56 | 1367 | criar `idx_payables_store_due` | INDEX | igual | Idempotente por nome |
| 57 | 1368 | criar `idx_payables_status` | INDEX | igual | Idempotente por nome |
| 58 | 1369 | criar `idx_payables_supplier` | INDEX | igual | Idempotente por nome |
| 59 | 1370 | reler `app_state` | RUNTIME | igual | Somente leitura |
| 60 | 1371 | contar products | RUNTIME | igual | Detecta tabela vazia |
| 61 | 1372 | contar customers | RUNTIME | igual | Detecta tabela vazia |
| 62 | 1373 | contar sales | RUNTIME | igual | Detecta tabela vazia |
| 63 | 1374 | contar cash movements | RUNTIME | igual | Detecta tabela vazia |
| 64 | 1375 | contar receivables | RUNTIME | igual | Detecta tabela vazia |
| 65 | 1376 | contar payables | RUNTIME | igual | Detecta tabela vazia |
| 66 | 1377 | decidir se tabelas estao vazias | LEGACY_UNKNOWN | igual | Nao verifica todas as tabelas; pode inferir incorretamente |
| 67 | 1378 | reconstruir tabelas pelo JSON/default | RECONSTRUCTION | igual | DML destrutivo amplo; alto risco operacional |

### 4.1 Quantidades estruturais

- 19 comandos `CREATE TABLE`.
- 30 comandos `CREATE INDEX`/`CREATE UNIQUE INDEX`.
- 2 sites de `ALTER TABLE` no codigo, mutuamente exclusivos por driver e
  destinados a mesma coluna.
- 49 objetos estruturais finais da aplicacao (19 tabelas + 30 indices), sem
  contar a futura `schema_migrations`.
- 51 sites de DDL no fonte (19 + 30 + 2), embora apenas um dos dois `ALTER`
  possa executar por chamada.

### 4.2 Responsabilidades e dados por faixa

- Operacoes 2, 4, 7, 9, 16, 18, 20, 21, 24, 26, 29, 32, 35, 39, 41,
  46, 49, 52 e 54 sao schema puro e nao deveriam conter regra de negocio.
- Operacoes 8, 10, 11, 17, 19, 22, 23, 25, 27, 28, 30, 31, 33, 34,
  36-38, 40, 42-45, 47, 48, 50, 51, 53 e 56-58 sao indices. Indices
  unicos incorporam regras de unicidade e podem falhar ao encontrar dados
  legados duplicados.
- Operacoes 3, 6 e 15 contem dados iniciais. A 15 tambem contem regra de
  seguranca/negocio para o administrador.
- Operacao 55 e migration estrutural aditiva.
- Operacoes 5, 12-14, 59-66 sao deteccao em runtime, dependentes do schema
  anterior.
- Operacao 67 contem regra legada de recuperacao e altera dados de varias
  tabelas; e a de maior risco.
- Nao existe operacao classificada como SEED demonstrativo no fluxo atual.

### 4.3 Comportamento atual por estado do banco

- **SQLite ausente:** a primeira chamada a `connect_db()` fora do caminho
  somente leitura cria o arquivo. Se chegar a `init_db()`, as 19 tabelas, os
  indices e o bootstrap sao executados automaticamente.
- **Banco vazio:** `init_db()` cria estrutura, loja, app_state e tenta criar o
  administrador se `MOVA_ADMIN_PASSWORD` existir.
- **Schema legado completo:** DDL `IF NOT EXISTS` nao altera a maior parte dos
  objetos; o ALTER de discount e executado/verificado; a reconstrucao pode
  ocorrer se as seis tabelas contadas estiverem vazias.
- **Schema parcial:** objetos ausentes podem ser criados, mas objetos presentes
  com definicao incorreta nao sao corrigidos. A chamada pode falhar no meio por
  tabela/coluna/indice incompativel ou unicidade de dados.
- **Schema futuro:** readiness o rejeita se houver versao acima de 1, mas uma
  rota que chama `init_db()` ainda tenta executar o DDL legado antes de sua
  operacao normal.
- **App_state presente e tabelas vazias:** pode ocorrer reconstrucao global
  automatica; isso nao e aceitavel no modelo futuro.

## 5. Schema atual: tabelas, colunas e dependencias

Convencoes: `PK` = primary key, `NN` = not null, `FK` = foreign key,
`D` = default. Colunas sem `NN` sao nullable.

| Tabela | Colunas e constraints | Finalidade, uso e criticidade |
|---|---|---|
| `stores` | `id TEXT PK`; `name TEXT NN`; `created_at TEXT NN` | Loja/tenant. Referenciada por quase todas as tabelas; bootstrap cria `matriz`. Critica. |
| `app_state` | `id INTEGER PK CHECK(id=1)`; `data TEXT NN`; `updated_at TEXT NN` | Espelho JSON legado, condicionais e compatibilidade. Usada por `/api/state`, import/export, dashboard/relatorios e sincronizacoes. Critica enquanto o legado existir. |
| `users` | `id TEXT PK`; `store_id TEXT NN FK stores`; `name TEXT NN`; `login TEXT NN`; `password_hash TEXT NN`; `role TEXT NN D operator`; `active INTEGER NN D 1`; `updated_at TEXT NN` | Fonte autoritativa de autenticacao e CRUD de usuarios. Critica e sensivel. |
| `audit_logs` | `id TEXT PK`; `store_id TEXT NN FK stores`; `user_id`, `user_name`, `user_role`; `action TEXT NN`; `module TEXT NN`; `ref_id`; `details`; `created_at TEXT NN` | Auditoria das operacoes. Escrita por `record_audit`; leitura em `/api/audit-logs`. Critica. |
| `brands` | `id TEXT PK`; `store_id TEXT NN FK stores`; `name TEXT NN`; `updated_at TEXT NN` | Cadastro de marcas e vinculo textual de produtos. CRUD `/api/brands`. Media. |
| `categories` | mesma estrutura de `brands` | Cadastro de categorias. CRUD `/api/categories`. Media. |
| `suppliers` | `id TEXT PK`; `store_id TEXT NN FK stores`; `name TEXT NN`; `cnpj`, `phone`, `email`, `address`; `updated_at TEXT NN` | Fornecedores. CRUD `/api/suppliers`; referencia textual em contas. Alta. |
| `customers` | `id TEXT PK`; `store_id TEXT NN FK stores`; `code`; `name TEXT NN`; `cpf`, `rg`, `birth`, `whatsapp`, `email`, `address`, `city`, `district`, `zip`; `credit_limit REAL NN D 0`; `status TEXT NN D active`; `updated_at TEXT NN` | Clientes, vendas e crediario. CRUD `/api/customers`, vendas e recebiveis. Critica. |
| `products` | `id TEXT PK`; `store_id TEXT NN FK stores`; `barcode`; `name TEXT NN`; `size`, `color`, `gender`, `category_name`, `brand_name`; `stock INTEGER NN D 0`; `min_stock INTEGER NN D 0`; `description`; `active INTEGER NN D 1`; `cost REAL NN D 0`; `price REAL NN D 0`; `photo`; `updated_at TEXT NN` | Produtos/estoque. CRUD, vendas e devolucoes. Critica. |
| `sales` | `id TEXT PK`; `store_id TEXT NN FK stores`; `customer_id`; `customer_name TEXT NN`; `subtotal`, `discount`, `total`, `cost_total REAL NN D 0`; `status TEXT NN D completed`; `created_at`, `updated_at TEXT NN` | Cabecalho de vendas. `/api/sales`, cancelamento e devolucao. Critica. |
| `sale_items` | `id TEXT PK`; `sale_id TEXT NN FK sales ON DELETE CASCADE`; `product_id`; `barcode`; `name TEXT NN`; `brand`; `quantity INTEGER NN D 1`; `unit_cost`, `unit_price`, `total REAL NN D 0` | Snapshot dos itens vendidos. Vendas, cancelamentos, devolucoes e ranking. Critica. |
| `sale_payments` | `id TEXT PK`; `sale_id TEXT NN FK sales ON DELETE CASCADE`; `method TEXT NN`; `amount REAL NN D 0`; `installments INTEGER NN D 1`; `status TEXT NN D registered`; `created_at TEXT NN` | Composicao do pagamento de vendas. Critica. |
| `cash_movements` | `id TEXT PK`; `store_id TEXT NN FK stores`; `direction TEXT NN`; `type`, `description`, `method`; `amount REAL NN D 0`; `ref_id`; `created_at TEXT NN` | Livro de entradas/saidas. GET/POST de caixa e efeitos financeiros. Critica. |
| `cash_closings` | `id TEXT PK`; `store_id TEXT NN FK stores`; `date TEXT NN`; `expected_cash`, `informed_cash`, `difference`, `total_balance`, `cash_in`, `cash_out REAL NN D 0`; `notes`, `user_id`, `user_name`; `created_at TEXT NN` | Fechamentos de caixa. GET/POST `/api/cash-closings`. Alta. |
| `receivables` | `id TEXT PK`; `store_id TEXT NN FK stores`; `sale_id`, `customer_id`, `customer_name`; `method TEXT NN`; `amount`, `received REAL NN D 0`; `status TEXT NN D open`; `due_date`, `paid_at`, `last_payment_at`, `installment`; `created_at`, `updated_at TEXT NN` | Cartoes e crediario a receber. GET e pagamentos de recebiveis. Critica. |
| `receivable_payments` | `id TEXT PK`; `store_id TEXT NN FK stores`; `receivable_id TEXT NN FK receivables ON DELETE CASCADE`; `sale_id`, `customer_id`; `method TEXT NN`; `amount REAL NN D 0`; `created_at TEXT NN`; `note` | Historico de baixas de recebiveis. Critica. |
| `sale_returns` | `id TEXT PK`; `store_id TEXT NN FK stores`; `sale_id TEXT NN`; `customer_name`; `total REAL NN D 0`; `reason`, `notes`; `created_at TEXT NN` | Cabecalho de devolucoes/trocas. GET/POST `/api/returns`. Critica. |
| `sale_return_items` | `id TEXT PK`; `return_id TEXT NN FK sale_returns ON DELETE CASCADE`; `product_id`, `product_name`; `action TEXT NN`; `quantity INTEGER NN D 1`; `unit_price`, `total REAL NN D 0` | Itens devolvidos/trocados. Critica. |
| `payables` | `id TEXT PK`; `store_id TEXT NN FK stores`; `supplier`; `category TEXT NN`; `amount REAL NN D 0`; `issue_date`; `due_date TEXT NN`; `notes`; `paid_amount`, `fee`, `discount REAL NN D 0`; `status TEXT NN D pending`; `paid_at`; `created_at`, `updated_at TEXT NN` | Contas a pagar e baixas. GET/POST/PUT/pagamento. Critica. |

### 5.1 Foreign keys e constraints

- `store_id -> stores(id)`: users, audit_logs, brands, categories,
  suppliers, customers, products, sales, cash_movements, cash_closings,
  receivables, receivable_payments, sale_returns e payables.
- `sale_items.sale_id -> sales(id) ON DELETE CASCADE`.
- `sale_payments.sale_id -> sales(id) ON DELETE CASCADE`.
- `receivable_payments.receivable_id -> receivables(id) ON DELETE CASCADE`.
- `sale_return_items.return_id -> sale_returns(id) ON DELETE CASCADE`.
- `app_state.id` possui `CHECK (id = 1)`.
- Nao ha FKs para `sales.customer_id`, `sale_items.product_id`,
  `receivables.sale_id/customer_id` ou `sale_returns.sale_id`.
- Status, valores monetarios, quantidades e estoque nao possuem `CHECK` de
  dominio ou nao negatividade.
- Unicidades sao implementadas por indices, nao por constraints nomeadas na
  declaracao das tabelas.

### 5.2 DDL atual por driver

No SQLite, o DDL efetivo e exatamente o conjunto de declaracoes de colunas da
secao 5, seguido dos 30 `CREATE [UNIQUE] INDEX` da secao 6. As tabelas usam
`TEXT`, `INTEGER`, `REAL`, PKs textuais (exceto app_state), FKs declarativas e
os quatro `ON DELETE CASCADE` listados. O unico `CHECK` e `app_state.id=1`.

No PostgreSQL, `translate_postgres_sql()` envia as mesmas declaracoes de
tabelas e indices, substituindo placeholders apenas quando existentes e
ignorando PRAGMAs. O tipo `REAL`, os timestamps em `TEXT`, defaults e
constraints permanecem como escritos. O insert da store e traduzido para
`ON CONFLICT`; o ALTER de discount usa `IF NOT EXISTS`.

A migration 001 futura deve manter essas definicoes para preservar
compatibilidade. Ela deve usar DDL estrito, sem depender de `IF NOT EXISTS`
para ocultar objetos inesperados em banco novo. O comando de baseline legado
nao executa esse DDL: ele compara o catalogo existente com a mesma
especificacao canonica.

## 6. Inventario dos 30 indices

| # | Indice | Tabela | Colunas | Unico/parcial |
|---:|---|---|---|---|
| 1 | `idx_users_store_login` | users | store_id, login | unico |
| 2 | `idx_audit_store_created` | audit_logs | store_id, created_at | nao |
| 3 | `idx_audit_module` | audit_logs | module | nao |
| 4 | `idx_brands_store_name` | brands | store_id, name | unico |
| 5 | `idx_categories_store_name` | categories | store_id, name | unico |
| 6 | `idx_customers_store_name` | customers | store_id, name | nao |
| 7 | `idx_customers_store_cpf` | customers | store_id, cpf | unico; `cpf` preenchido |
| 8 | `idx_products_store_barcode` | products | store_id, barcode | unico; barcode preenchido |
| 9 | `idx_sales_store_created` | sales | store_id, created_at | nao |
| 10 | `idx_sales_customer` | sales | customer_id | nao |
| 11 | `idx_sale_items_sale` | sale_items | sale_id | nao |
| 12 | `idx_sale_items_product` | sale_items | product_id | nao |
| 13 | `idx_sale_payments_sale` | sale_payments | sale_id | nao |
| 14 | `idx_sale_payments_method` | sale_payments | method | nao |
| 15 | `idx_cash_store_created` | cash_movements | store_id, created_at | nao |
| 16 | `idx_cash_method` | cash_movements | method | nao |
| 17 | `idx_cash_ref` | cash_movements | ref_id | nao |
| 18 | `idx_cash_closings_store_date` | cash_closings | store_id, date | nao |
| 19 | `idx_receivables_store_due` | receivables | store_id, due_date | nao |
| 20 | `idx_receivables_status` | receivables | status | nao |
| 21 | `idx_receivables_sale` | receivables | sale_id | nao |
| 22 | `idx_receivables_customer` | receivables | customer_id | nao |
| 23 | `idx_receivable_payments_receivable` | receivable_payments | receivable_id | nao |
| 24 | `idx_receivable_payments_customer` | receivable_payments | store_id, customer_id, created_at | nao |
| 25 | `idx_returns_store_created` | sale_returns | store_id, created_at | nao |
| 26 | `idx_returns_sale` | sale_returns | sale_id | nao |
| 27 | `idx_return_items_return` | sale_return_items | return_id | nao |
| 28 | `idx_payables_store_due` | payables | store_id, due_date | nao |
| 29 | `idx_payables_status` | payables | status | nao |
| 30 | `idx_payables_supplier` | payables | supplier | nao |

A readiness atual valida somente os tres indices unicos de users/login,
customers/CPF e products/barcode. Ela nao detecta ausencia ou definicao
incorreta dos outros 27 indices.

## 7. Evolucao estrutural legada: `payables.discount`

O historico Git confirma a sequencia:

- `116e4da`: schema inicial de `payables` sem `discount`;
- `97b66e9`: inclusao da coluna no `CREATE TABLE`;
- `5e60013`: correcao para adicionar a coluna em bancos PostgreSQL existentes
  e verificacao condicional no SQLite.

| Aspecto | Resultado |
|---|---|
| Estado anterior | `payables` sem `discount` |
| Estado posterior | `discount REAL NOT NULL DEFAULT 0` |
| Deteccao SQLite | `PRAGMA table_info(payables)` e busca pelo nome da coluna |
| Deteccao PostgreSQL | `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` |
| Banco novo | `CREATE TABLE` ja inclui a coluna; ALTER e redundante |
| Banco existente | coluna adicionada com default zero |
| Backfill | o default `0` atende registros existentes; nao ha calculo historico |
| Dados afetados | metadado estrutural e preenchimento logico de zero nos registros antigos |
| Reversibilidade | PostgreSQL permite `DROP COLUMN`, mas e destrutivo; SQLite exige rebuild da tabela |
| Risco | lock de tabela; falha se tabela estiver ausente ou incompatibilidade nao detectada |

Esta e a unica migration estrutural historica comprovada embutida em
`init_db()`. Nao foram encontrados outros `ALTER TABLE` no commit analisado.

## 8. Dados iniciais, bootstrap e reconstrucoes

### 8.1 Loja matriz

- tabela: `stores`;
- condicao: toda chamada de `init_db()` executa insert idempotente;
- valores: `id=matriz`, `name=Loja Matriz`, `created_at=utc_now()` apenas na
  primeira insercao;
- sensibilidade: nao contem segredo;
- classificacao: BOOTSTRAP, nao migration;
- futuro: comando explicito de bootstrap operacional.

### 8.2 App state inicial

- tabela: `app_state`, sempre `id=1`;
- condicao: registro ausente;
- valores: JSON de `default_state()` e timestamp UTC;
- conteudo: listas vazias de produtos, clientes, fornecedores, marcas,
  categorias, vendas, recebiveis, contas a pagar, caixa, fechamentos,
  devolucoes e condicionais; a lista `users` recebe o descritor publico do
  administrador inicial, sem senha/hash;
- sensibilidade: nao deve conter credenciais, mas e dado operacional;
- classificacao: BOOTSTRAP/compatibilidade legada, nao schema e nao seed
  demonstrativo;
- futuro: bootstrap separado deve gerar `users` a partir da tabela autoritativa.
  Se o administrador nao for criado, a lista deve permanecer vazia.

### 8.3 Administrador inicial

`create_initial_admin_user()`:

- recebe conexao e `store_id` (default `matriz`);
- usa `MOVA_ADMIN_PASSWORD`, obrigatoria e nunca registrada em log;
- usa `MOVA_ADMIN_NAME` (default `Administrador`) e `MOVA_ADMIN_LOGIN`
  (default `admin`);
- grava somente `generate_password_hash(password)` em `users.password_hash`;
- usa id fixo `admin`, role `admin`, active `1` e timestamp UTC;
- so e chamada quando `users` esta vazia e o registro `app_state` acabou de
  ser criado;
- nao e chamada quando existe estado legado ou banco existente sem usuarios;
- retorna `False` e registra erro seguro se a senha nao estiver configurada;
- nao grava auditoria;
- usa a mesma regra em development, staging e production;
- e condicionalmente idempotente pelo `COUNT(*)`, mas uma chamada direta
  repetida pode colidir com PK/login.

Futuro recomendado: comando CLI de bootstrap separado, executado uma unica
vez depois das migrations. Ele deve validar banco estruturalmente pronto,
ausencia real de usuarios e legado utilizavel, exigir segredo por ambiente e
gravar auditoria na mesma transacao. Migration nunca deve criar usuario.

### 8.4 Seeds

Nao foi identificado catalogo demonstrativo, produto, cliente, marca ou
categoria opcional inserido por `init_db()`. O `default_state()` e um estado
operacional vazio, nao um seed de demonstracao. Caso dados demonstrativos
sejam desejados no futuro, devem usar comando separado e nunca production por
padrao.

### 8.5 Reconstrucao global

Depois de criar todo o schema, `init_db()` conta somente products, customers,
sales, cash_movements, receivables e payables. Se essas seis tabelas estiverem
vazias e existir `app_state`, chama `sync_business_tables()`.

Essa funcao apaga e recria dados de brands, categories, suppliers, customers,
products, sales, sale_items, sale_payments, cash_movements, cash_closings,
receivables, receivable_payments, returns, return_items e payables. A
reconstrucao:

- e DML amplo e potencialmente destrutivo;
- nao pertence a migration;
- nao valida se tabelas nao contadas possuem dados;
- usa `default_state()` se o JSON estiver invalido;
- pode ocorrer durante uma request que apenas pretendia ler dados;
- deve virar ferramenta explicita de recuperacao/importacao, nunca bootstrap
  automatico.

## 9. Chamadas restantes de `init_db()`

### 9.1 Rotas HTTP

| Rota/metodo | Linha | Chamada | Motivo aparente | Risco | Sprint sugerida |
|---|---:|---|---|---|---|
| GET `/api/database/status` | 3348 | indireta por `database_status` | garantir tabelas antes do diagnostico | DDL/bootstrap em consulta administrativa | 5B.6 |
| GET `/api/export` | 3356 | indireta por `read_state` | garantir app_state | DDL/reconstrucao em exportacao | 5B.6 |
| POST `/api/import` | 3407 | indireta por read/write state | estado atual e substituicao | DDL somado a importacao destrutiva | 5B.6 |
| POST `/api/backups` | 3458 | indireta por backup | garantir arquivo SQLite | DDL antes do backup; copia ja alterada | 5B.6 |
| GET `/api/audit-logs` | 3489 | direta | garantir audit_logs | leitura pode criar schema/bootstrap | 5B.6 |
| GET `/api/dashboard` | 3533 | indireta por `read_state` | carregar espelho | DDL/reconstrucao em dashboard | 5B.6 |
| GET `/api/reports` | 3544 | indireta por `read_state` | carregar espelho | DDL/reconstrucao em relatorio | 5B.6 |
| POST `/api/me/password` | 3598 | direta | garantir users | DDL no fluxo de credencial | 5B.6 |
| GET/POST/PUT/DELETE `/api/users...` | 3644-3773 | direta | CRUD users | DDL/bootstrap em administracao | 5B.6 |
| GET/PUT `/api/state` | 3801/4969 | indireta | ler/substituir estado | DDL e reconstrucoes | 5B.6 |
| GET/POST/PUT/DELETE `/api/products...` | 3807-3891 | direta | CRUD products | request pode alterar schema | 5B.6 |
| GET/POST/PUT/DELETE `/api/brands...` | 3917-3938 | direta/indireta | CRUD brands | request pode alterar schema | 5B.6 |
| GET/POST/PUT/DELETE `/api/categories...` | 3943-3964 | direta/indireta | CRUD categories | request pode alterar schema | 5B.6 |
| GET/POST/PUT/DELETE `/api/suppliers...` | 4034-4095 | direta | CRUD suppliers | request pode alterar schema | 5B.6 |
| GET/POST/PUT/DELETE `/api/customers...` | 4117-4198 | direta | CRUD customers | request pode alterar schema | 5B.6 |
| GET/POST `/api/sales`, cancelamento | 4228-4360 | direta; POST tambem le estado | venda/cancelamento | DDL/reconstrucao em fluxo critico | 5B.6, apos persistencia direcionada |
| GET `/api/returns`; POST `/api/returns` | 4446/4539 | direta | devolucoes | DDL em fluxo critico | 5B.6, apos persistencia direcionada |
| GET/POST/PUT `/api/conditionals...` | 4482-4509 | indireta por `read_state` | condicionais no JSON | DDL/reconstrucao | 5B.6 |
| GET `/api/cash-movements` | 4632 | direta | listar caixa | DDL em leitura | 5B.6 |
| GET `/api/cash-closings` | 4669 | direta | listar fechamentos | DDL em leitura | 5B.6 |
| POST `/api/cash-closings` | 4687 | indireta por `read_state` | calcular metricas | persistencia e direta, leitura ainda inicializa | 5B.6 |
| POST `/api/card-receipts` | 4718 | indireta por espelho de caixa | atualizar estado/recebiveis | DDL/reconstrucao | 5B.6 |
| GET `/api/receivables` | 4766 | direta | listar recebiveis | DDL em leitura | 5B.6 |
| POST `/api/receivables/payments` | 4804 | indireta por read/write state | baixa de recebiveis | DDL/reconstrucao em financeiro | 5B.6, apos persistencia direcionada |
| GET `/api/payables` | 4908 | direta | listar contas | DDL em leitura | 5B.6 |

Observacoes:

- login, logout, `/api/session` e refresh de sessao nao chamam `init_db()` na
  base analisada.
- `/api/health` e `/api/readiness` tambem nao chamam `init_db()`.
- POST `/api/cash-movements` e as gravacoes direcionadas de payables nao
  aparecem na lista porque as Sprints 5A removeram a reconstrucoes desses
  caminhos.
- A listagem agrupa rotas irmas que chamam o mesmo helper; a linha indicada e
  a do handler inicial do grupo.

### 9.2 Chamadas nao HTTP

- `create_database_backup()` chama diretamente;
- `database_status()` chama diretamente;
- `read_state()` e `write_state()` chamam diretamente;
- `python server.py` chama diretamente antes do servidor local;
- `ensure_startup_backup()` chama backup, mas somente depois de `init_db()` no
  bloco principal;
- import de `server` e `wsgi.py` nao chama `init_db()` por si so.

## 10. Dependencia dos testes atuais

Dez dos onze arquivos de teste usam `server.init_db()` em fixtures ou
cenarios especificos; somente `test_environment_config.py` nao depende dele.
Os testes afetados cobrem autenticacao/sessao, readiness, permissoes,
credenciais, movimentos e fechamentos de caixa e as tres persistencias de
contas a pagar.

Na implementacao futura, essas fixtures devem executar o migration runner em
banco temporario, seguido do bootstrap minimo exigido pelo teste. Nao devem
continuar usando `init_db()` como atalho, porque isso mascararia DDL em fluxo
HTTP e misturaria dados iniciais com estrutura.

## 11. `MOVA_ALLOW_MIGRATIONS` atual e contrato futuro

Estado atual:

- lida em `environment_config.py` por parser estrito;
- valores verdadeiros: `1`, `true`, `yes`, `on`;
- valores falsos: vazio, `0`, `false`, `no`, `off`;
- valor desconhecido gera aviso seguro e vira `False`;
- default efetivo: `False`;
- so fica efetivamente `True` em `development` ou `staging`;
- em production, APP_ENV ausente ou invalida permanece `False`;
- o valor e carregado em `server.ALLOW_MIGRATIONS`, mas nao protege nem
  aciona operacao estrutural no commit analisado.

Contrato recomendado:

1. migration nunca roda por request, readiness, health ou import;
2. a flag apenas autoriza o comando administrativo explicito;
3. development/staging exigem flag verdadeira para evitar execucao acidental;
4. production exige `APP_ENV=production`, flag textual estritamente valida,
   confirmacao explicita do operador e janela de manutencao;
5. como a configuracao atual sempre neutraliza a flag em production, a futura
   API de configuracao deve separar `flag solicitada` de `capacidade HTTP`:
   habilitar o CLI nao pode habilitar nenhuma rota;
6. testes podem fornecer ambiente isolado e flag verdadeira apenas a fixtures;
7. ausencia ou valor invalido bloqueia;
8. nenhum segredo, DATABASE_URL ou confirmacao deve aparecer em logs.

O nome continua adequado se seu unico significado futuro for autorizar o
executor administrativo. Nao deve ser reutilizado para bootstrap ou import.

## 12. Estrategia de baseline

### 12.1 Alternativas avaliadas

**Alternativa A - `001` cria o schema completo; legado recebe baseline
explicita.** E a recomendada. Mantem o mesmo caminho estrutural para banco
novo e exige decisao humana para reconhecer legado.

**Alternativa B - `001` somente registra baseline e outra migration cria
schema novo.** Rejeitada: produz semanticas diferentes para o mesmo numero de
versao e dificulta checksum, testes e readiness.

**Alternativa C - deteccao e baseline automaticas.** Rejeitada: um conjunto
parcial de tabelas/indices pode parecer compativel e ser marcado sem prova.
Isso nao pode ocorrer em request nem startup.

### 12.2 Versao recomendada

A baseline formal deve ser **versao 1** e representar o schema legado atual
completo no commit analisado: 19 tabelas, 30 indices, constraints atuais e
`payables.discount` presente. Isso preserva o `REQUIRED_SCHEMA_VERSION = 1`
introduzido na Sprint 5B.3 e evita simular no historico formal cada alteracao
anterior ao versionamento.

A evolucao historica de `discount` deve permanecer documentada. Se um banco
legado estiver sem essa coluna, ele nao e compativel com a baseline 1 e deve
ser recusado pelo comando `baseline`. A correcao desse estado deve ocorrer por
procedimento explicito aprovado antes do registro da baseline, nunca por
deducao silenciosa.

## 13. Tabela futura `schema_migrations`

Uma linha deve representar exatamente uma migration aplicada. Nao usar uma
unica linha de "versao atual", pois ela perde historico, duracao e prova de
imutabilidade.

Modelo logico recomendado:

| Coluna | SQLite | PostgreSQL | Regra |
|---|---|---|---|
| `version` | `INTEGER PRIMARY KEY` | `INTEGER PRIMARY KEY` | positivo; ordem total |
| `description` | `TEXT NOT NULL` | `TEXT NOT NULL` | nome humano imutavel |
| `applied_at` | `TEXT NOT NULL` | `TIMESTAMPTZ NOT NULL` | UTC; servidor gera |
| `checksum` | `TEXT NOT NULL` | `TEXT NOT NULL` | SHA-256 hexadecimal |
| `execution_time_ms` | `INTEGER NOT NULL` | `INTEGER NOT NULL` | duracao monotonic arredondada |

Regras:

- PK impede duplicata normal; o validador ainda deve rejeitar metadado
  malformado ou versoes repetidas em adaptador simulado/corrompido;
- versoes aplicadas devem formar um prefixo continuo das migrations
  conhecidas (`1..N`); lacuna bloqueia;
- versao aplicada maior que a ultima conhecida bloqueia;
- checksum divergente bloqueia novas migrations e deve tornar readiness nao
  pronta quando essa verificacao for incorporada;
- registros sao imutaveis: sem UPDATE/DELETE pelo executor;
- a linha e inserida na mesma transacao da migration, apenas depois das
  validacoes posteriores;
- `applied_at` e UTC. No SQLite, ISO 8601 com `Z`/offset explicito; no
  PostgreSQL, `TIMESTAMPTZ` normalizado para UTC;
- a propria tabela de controle e criada somente quando o comando de migration
  explicito for executado. Ela e infraestrutura do runner, nao deve surgir em
  import ou request.

## 14. Checksum e imutabilidade

Checksum deve existir desde a versao 1.

- algoritmo: SHA-256;
- entrada: representacao canonica UTF-8/LF contendo version, description,
  operacoes SQLite e operacoes PostgreSQL na ordem exata, alem dos
  identificadores das validacoes pre/pos declaradas;
- nao incluir timestamps, caminho absoluto, comentarios externos ou ambiente;
- migration aplicada nao pode ser editada; qualquer correcao vira nova
  migration;
- arquivo alterado depois de aplicado causa bloqueio do executor;
- migration legada registrada por baseline recebe o checksum oficial do
  artefato `001`, depois da comprovacao estrutural;
- migrations anteriores sem checksum nao existirao no modelo novo. Se forem
  encontradas, o estado e invalido e exige procedimento administrativo;
- checksum divergente nao deve impedir o processo Python de importar, mas
  deve bloquear migration e, apos a integracao com readiness, impedir
  recebimento de trafego.

## 15. Migrations propostas

O historico real mostra todo o schema/indices no primeiro commit web e apenas
`payables.discount` como evolucao posterior. Como o projeto ainda nao tinha
versionamento, a recomendacao e uma baseline consolidada, nao uma
reconstituicao especulativa do historico antigo.

### 15.1 `001_create_current_schema`

| Item | Definicao |
|---|---|
| Objetivo | criar o schema atual completo para banco novo |
| Precondicoes | banco novo/vazio ou comando explicito com validacao de ausencia de objetos incompatíveis |
| SQLite | criar as 19 tabelas na ordem atual, com `discount`, depois os 30 indices |
| PostgreSQL | mesmas tabelas/constraints/indices, usando SQL nativo parametrizado quando aplicavel |
| Validacao anterior | catalogo sem objetos conflitantes; se legado, comparacao integral de tabelas, colunas, nullability, defaults, PK, FK, CHECK e indices |
| Validacao posterior | exatamente 19 tabelas esperadas + 30 indices e definicoes completas; integridade/FKs verificaveis |
| Transacao | unica e explicita, incluindo registro em `schema_migrations` |
| Rollback | rollback transacional para banco novo; nao oferecer DROP automatico em legado |
| Dados afetados | nenhum dado de negocio; nao insere store, app_state ou usuario |
| Duracao | curta em banco novo; criacao de indices pode ser proporcional aos dados em legado |
| Risco | lock durante indices; conflito de nomes/definicoes; SQLite pode bloquear escritores |

Embora o SQL logico seja o mesmo, devem existir planos por driver. O executor
nao deve depender da traducao ad hoc de `PgConnection` para DDL critico.

### 15.2 Proxima versao

Nao ha uma migration `002` necessaria para representar o commit atual. A
proxima alteracao real de schema recebera versao 2. Em particular, nao criar
uma `002_add_payables_discount` apenas para reencenar o passado: a baseline 1
ja exige essa coluna. Bancos pre-baseline sem a coluna sao incompativeis e
devem passar por uma tarefa de reparo explicitamente aprovada antes da
baseline.

### 15.3 Por que indices nao viram migration separada

Os 30 indices ja pertenciam ao schema inicial versionado no historico
disponivel. Separar indices em uma segunda versao criaria um estado formal
intermediario que nunca deve estar pronto e aumentaria as combinacoes para
baseline legado. Internamente, a migration 001 pode executar tabelas e
indices em fases ordenadas, mantendo uma unica versao atomica.

## 16. Executor futuro

Nome sugerido: `run_database_migrations()` exposto por comando Flask CLI, por
exemplo `flask --app server db migrate`, ou por script administrativo fino que
importe um modulo dedicado de migrations. O modulo nao deve ser inicializado
ao importar `server`.

Fluxo recomendado:

1. carregar configuracao central sem registrar segredos;
2. validar APP_ENV, flag e confirmacao administrativa;
3. abrir conexao dedicada de migration;
4. configurar timeouts e transacao sem usar request/session;
5. adquirir lock exclusivo do executor;
6. criar/validar `schema_migrations` somente nesse contexto;
7. reler historico depois do lock;
8. validar continuidade, versao futura e checksums;
9. aplicar migrations pendentes em ordem;
10. validar schema posterior;
11. inserir uma linha por migration na mesma transacao;
12. commit somente ao final da migration;
13. liberar lock e fechar conexao em `finally`;
14. emitir log seguro com versao, descricao, duracao e resultado, sem URL ou
    SQL com dados.

O executor nao pode ser chamado por `before_request`, rota HTTP, login,
readiness, health, import, factory Flask, import WSGI, refresh de sessao ou
CRUD administrativo. Futuramente, o Railway pode chama-lo em release command
controlado, mas essa configuracao exige autorizacao separada.

Quem pode executar: operador de infraestrutura autorizado, com acesso ao
shell/release do ambiente. Perfil admin do ERP nao concede essa capacidade.
Nao deve existir endpoint de migration.

## 17. Transacoes e concorrencia

### 17.1 SQLite

- usar conexao dedicada ao arquivo explicitamente selecionado;
- permitir criar arquivo ausente somente por comando aprovado, com opcao
  explicita (`--create`) e nunca em request;
- `BEGIN IMMEDIATE` e recomendado para adquirir reserva de escrita antes de
  validar/aplicar;
- configurar foreign keys e busy timeout na conexao;
- nao alterar `journal_mode` silenciosamente no executor;
- executar cada migration e seu registro na mesma transacao;
- em falha, rollback e fechamento integral;
- dois executores sao serializados pelo lock de escrita; depois de adquirir o
  lock, reler `schema_migrations`;
- recomendar copia consistente/backup antes de migration de banco existente.

DDL suportado pelo SQLite atual e transacional quando executado dentro da
transacao explicita. Operacoes futuras que exijam rebuild de tabela devem usar
tabela nova, copia validada e rename na mesma transacao quando suportado.

### 17.2 PostgreSQL

- conexao dedicada com autocommit desabilitado;
- adquirir advisory lock transacional com chave constante e documentada do
  Mova Sports;
- configurar `lock_timeout` e `statement_timeout` locais a transacao;
- reler historico apos o lock;
- executar migration e insert de historico na mesma transacao;
- rollback integral em qualquer falha;
- liberar advisory lock no fim da transacao e fechar conexao;
- nao imprimir DATABASE_URL nem parametros sensiveis.

### 17.3 Falha parcial

- se o DDL for transacional: rollback deixa migration sem linha aplicada;
- a linha de historico nunca e inserida antes da validacao posterior;
- se uma futura operacao nao for transacional, ela deve ser rejeitada pelo
  runner generico e exigir plano operacional especifico, backup e migration
  corretiva;
- nao marcar automaticamente migration como concluida ou "falhou" no mesmo
  banco se a transacao estrutural nao puder ser comprovada;
- depois de falha ambigua, bloquear novas execucoes ate inspecao manual.

## 18. Banco novo

Fluxo futuro:

1. provisionar banco/arquivo no ambiente correto;
2. executar comando de migrations explicitamente;
3. validar readiness estrutural versionada;
4. executar comando de bootstrap para store/app_state;
5. criar administrador por subcomando/parametro explicito com segredo forte;
6. validar existencia de store e usuario autoritativo;
7. iniciar aplicacao e liberar trafego.

Readiness estrutural deve comprovar schema/versao/checksum. Existencia de
store e administrador e prontidao operacional, separada do schema. A
readiness atual verifica somente estrutura, nao exige dados.

Migrations podem criar um SQLite ausente apenas pelo comando explicito e com
`--create`; nao podem criar admin, store matriz ou registro app_state.

## 19. Banco legado

Fluxo futuro:

1. confirmar commit/aplicacao e janela de manutencao;
2. criar e validar backup/snapshot;
3. bloquear trafego/escritas;
4. inspecionar integralmente schema, constraints, indices e versao;
5. executar `db baseline --version 1` explicitamente;
6. recusar se qualquer definicao obrigatoria divergir;
7. inserir a linha da baseline com checksum oficial em transacao;
8. aplicar migrations posteriores, se houver;
9. validar schema, checksums, FKs e readiness;
10. liberar trafego somente apos verificacoes.

O baseline nao executa DDL nem corrige schema. Ele apenas reconhece um schema
ja comprovadamente equivalente. Nao existe baseline automatica, inclusive
quando o banco "parece" conter as tabelas.

Banco com `app_state` e tabelas vazias nao deve ser reconstruido pelo runner.
Recuperacao/sincronizacao legada e um comando diferente, com revisao propria.

## 20. Rollback recomendado

- **Rollback imediato:** transacao da migration; e o mecanismo primario.
- **Downgrade automatico:** nao obrigatorio e nao recomendado como regra geral.
- **Migration corretiva:** preferida depois que uma migration ja foi aplicada
  e o sistema voltou a operar.
- **Restauracao de backup:** necessaria para falha destrutiva ou ambigua que
  nao possa ser revertida transacionalmente.
- **Codigo:** manter compatibilidade de expansao antes de contracao.

Mudancas destrutivas futuras devem seguir: adicionar estrutura, migrar dados,
trocar leitura/escrita, observar, e somente remover estrutura em sprint
posterior autorizada.

## 21. Integracao futura com readiness

A Sprint 5B.3 ja inspeciona schema sem escrita e reconhece opcionalmente
`schema_migrations`, mas aceita `READY_LEGACY` e verifica somente a maior
versao. Depois da implementacao:

- readiness continua estritamente somente leitura;
- exige `schema_migrations` e colunas completas;
- verifica que as versoes aplicadas formam exatamente um prefixo continuo;
- rejeita duplicatas, lacunas, versao futura e checksum divergente;
- compara com a ultima migration conhecida pela aplicacao;
- nao aplica migration e nao sugere SQL em resposta;
- retorna erro externo generico e detalhe tecnico seguro apenas em log;
- `READY_LEGACY` permanece apenas durante a janela de adocao controlada.

Remocao de `READY_LEGACY`: depois que todos os ambientes conhecidos tiverem
baseline registrada, backups validados e ao menos um ciclo de deploy estavel
com readiness versionada. A remocao deve ocorrer em tarefa separada e antes de
considerar o versionamento obrigatorio concluido.

## 22. Separacao futura de schema, bootstrap e seed

| Fluxo | Pode fazer | Nao pode fazer |
|---|---|---|
| Migration | tabelas, colunas, indices, constraints e historico estrutural | store, app_state row, admin, dados demo, reconstrucao |
| Bootstrap | store matriz, app_state vazio coerente e admin inicial, todos explicitos | alterar schema, inferir legado ou reconstruir negocio |
| Seed | dados opcionais de desenvolvimento/teste | executar por padrao em staging/production |
| Runtime HTTP | CRUD e regras normais sobre schema pronto | DDL, baseline, bootstrap, migration, reparo estrutural |
| Recuperacao legada | import/sincronizacao expressamente autorizada | ser chamada automaticamente por migration/startup/request comum |

Plano especifico:

- **store matriz:** subcomando `db bootstrap-store`, idempotente por id, com
  verificacao de conflito de nome e auditoria administrativa;
- **app_state:** subcomando de bootstrap cria apenas `id=1` quando ausente,
  com estado vazio e usuarios publicos obtidos de `users`;
- **administrador:** subcomando separado ou opcao explicita do bootstrap,
  exigindo `MOVA_ADMIN_PASSWORD`, banco sem usuarios e ausencia de legado;
- **seed:** nao ha seed atual a migrar;
- **reconstruction:** ferramenta de recuperacao separada, nunca chamada pelo
  migration runner.

## 23. Matriz de testes da Sprint 5B.4B

| # | Cenario | Resultado esperado |
|---:|---|---|
| 1 | SQLite novo | schema completo e versao 1 |
| 2 | PostgreSQL novo simulado | SQL/adaptador corretos e versao 1 |
| 3 | ordem | migrations aplicadas em ordem crescente |
| 4 | reexecucao | nenhuma migration reaplicada |
| 5 | ja registrada | corpo nao executa novamente |
| 6 | falha intermediaria | rollback de DDL e historico |
| 7 | versao futura | bloqueio seguro |
| 8 | lacuna | bloqueio seguro |
| 9 | duplicata/metadado corrompido | bloqueio seguro |
| 10 | checksum divergente | bloqueio seguro |
| 11 | legado compativel | nao e marcado automaticamente |
| 12 | baseline explicita | registra versao/checksum sem DDL |
| 13 | baseline incompativel | recusa sem escrita |
| 14 | discount ausente | baseline recusa; nenhuma correcao silenciosa |
| 15 | discount presente | validacao aceita a definicao exata |
| 16 | indices ausentes | baseline recusa |
| 17 | indices presentes | nomes, colunas, ordem, unique e predicado validados |
| 18 | request qualquer | migration runner nao chamado |
| 19 | readiness | nao aplica migration |
| 20 | health | nao abre/cria banco nem aplica migration |
| 21 | login | nao aplica migration |
| 22 | API protegida | nao aplica migration |
| 23 | import WSGI | nao aplica migration |
| 24 | Gunicorn import | nao aplica migration |
| 25 | flag ausente em production | comando bloqueado |
| 26 | autorizacao explicita | somente CLI aprovado executa |
| 27 | SQLite ausente | criado somente com `--create` aprovado |
| 28 | conexoes | sempre fechadas, inclusive em erro |
| 29 | PostgreSQL | transacao e advisory lock confirmados |
| 30 | logs | sem senha, token ou DATABASE_URL |
| 31 | bootstrap | nao executado pelo runner |
| 32 | admin | `create_initial_admin_user` nao chamado |
| 33 | app_state | `write_state` nao chamado |
| 34 | reconstrucao | `sync_business_tables` nao chamado |
| 35 | regressao | suite completa verde |

Testes adicionais recomendados: dois executores concorrentes, timeout de
lock, falha na validacao posterior, checksum canonico igual em Windows/Linux,
schema_migrations com colunas erradas e fechamento da conexao apos Ctrl+C.

## 24. Riscos e mitigacoes

| Risco | Impacto | Mitigacao |
|---|---|---|
| Schema real de producao divergir do fonte | baseline incorreta ou indisponibilidade | inspecao somente leitura + backup; nunca inferir |
| Indices unicos encontrarem duplicatas | migration falha/lock | preflight de duplicatas sem alterar dados |
| Dois executores | DDL concorrente | advisory lock/BEGIN IMMEDIATE + dupla leitura |
| SQLite criado pelo runtime antes do CLI | arquivo vazio confuso | HTTP/readiness read-only; `--create` exclusivo |
| `connect_db` alterar WAL | efeito persistente inesperado | conexao dedicada de migration |
| DDL longo em PostgreSQL | bloqueio de trafego | manutencao, lock/statement timeout, monitoramento |
| Checksum variar por plataforma | falso positivo | serializacao canonica UTF-8/LF |
| Baseline marcar schema parcial | falsa prontidao | validar tabela, coluna, PK, FK, default, indice e predicado |
| Bootstrap misturado novamente | admin/dados criados sem controle | modulos/comandos e testes sentinela separados |
| READY_LEGACY permanecer indefinidamente | schema sem prova formal | plano de retirada com prazo operacional |
| Futuras branches reintroduzirem init_db em HTTP | DDL durante request | testes sentinela e busca estatica em CI |
| ResourceWarning/conexoes | lock/vazamento | fixtures e runner fecham em `finally` |

## 25. Decisoes expressas

1. **Versao baseline:** `1`, representando o schema atual consolidado.
2. **Uma linha por migration:** sim, imutavel.
3. **Checksum:** sim, SHA-256 desde a versao 1.
4. **Banco legado:** comando explicito de baseline apos backup e validacao
   estrutural integral.
5. **Baseline automatica:** nao; sempre explicita.
6. **Quem executa:** operador de infraestrutura autorizado via CLI/release,
   nao usuario HTTP do ERP.
7. **MOVA_ALLOW_MIGRATIONS:** autoriza somente comando explicito; ausente ou
   invalida bloqueia; nunca habilita request; production exige confirmacao
   adicional e ajuste futuro seguro da configuracao.
8. **Criar SQLite ausente:** sim, somente por CLI com `--create` explicito.
9. **Criar administrador em migration:** nao.
10. **Criar store matriz em migration:** nao.
11. **Inserir app_state em migration:** nao; somente criar a tabela.
12. **Bootstrap separado:** sim.
13. **Concorrencia:** `BEGIN IMMEDIATE` no SQLite; advisory lock transacional
    no PostgreSQL; sempre reler historico depois do lock.
14. **Migration parcial:** rollback; sem registro de versao; falha ambigua
    bloqueia e exige inspecao.
15. **Versao futura:** bloquear executor e readiness.
16. **Lacuna:** bloquear; nao preencher automaticamente.
17. **Arquivo aplicado alterado:** checksum divergente bloqueia; criar nova
    migration em vez de editar.
18. **Readiness exige schema_migrations:** sim, apos a transicao controlada.
19. **Remover READY_LEGACY:** quando todos os ambientes estiverem baselined,
    validados e estaveis em ao menos um ciclo de deploy.
20. **Divisao das proximas sprints:** descrita na secao seguinte.

## 26. Divisao exata 5B.4B, 5B.5 e 5B.6

### Sprint 5B.4B - framework e migration baseline

- modulo dedicado de migrations;
- tabela `schema_migrations`;
- migration imutavel `001_create_current_schema`;
- checksum, locks, transacoes e validacoes;
- comandos explicitos `db migrate`, `db status` e `db baseline`;
- fixtures temporarias passam a usar migrations;
- nenhuma mudanca de bootstrap;
- `init_db()` e chamadas HTTP ainda nao sao removidos nessa sprint, exceto se
  necessario isolar o runner sem alterar comportamento.

### Sprint 5B.5 - bootstrap explicito

- comandos separados para store, app_state e administrador;
- remover do `init_db()` inserts de store/app_state/admin e reconstrucao;
- preservar dados existentes e compatibilidade legada;
- nenhuma reconstrucao automatica;
- documentar instalacao nova e recuperacao legada;
- testes de ausencia de senha, banco legado e idempotencia operacional.

### Sprint 5B.6 - retirada estrutural do runtime

- remover as chamadas restantes de `init_db()` das rotas/helpers/startup;
- usar apenas conexoes sem DDL em requests;
- converter erros de schema em respostas controladas;
- exigir readiness versionada e remover `READY_LEGACY` quando autorizado;
- retirar `init_db()` ou reduzi-lo a compatibilidade nao chamada, com remocao
  final aprovada;
- avaliar release command do Railway em tarefa operacional separada;
- manter migrations e bootstrap fora do HTTP.

## 27. Decisoes/confirmacoes ainda dependentes do ambiente

Nao ha decisao arquitetural bloqueante para iniciar a 5B.4B. Antes de
baseline/deploy reais, ainda sera necessario confirmar:

- schema efetivo de cada banco legado, especialmente producao;
- existencia de duplicatas que impeçam indices unicos;
- versao do SQLite/PostgreSQL hospedado e suporte transacional necessario;
- mecanismo e validacao do backup/snapshot de producao;
- chave numerica do advisory lock e timeouts operacionais;
- formato final do comando (Flask CLI ou script dedicado);
- mecanismo futuro de release command no Railway;
- janela e criterio operacional para remover `READY_LEGACY`.

Nenhuma dessas confirmacoes autoriza acesso a producao nesta sprint.

## 28. Criterios de aprovacao da Sprint 5B.4B

1. somente arquivos de migrations/CLI/config/testes/documentacao aprovados;
2. migration 001 reproduz exatamente as 19 tabelas, 30 indices e constraints;
3. nenhum DML de store, app_state, admin, seed ou negocio;
4. nenhuma chamada por import, WSGI, HTTP, health, readiness ou login;
5. schema_migrations com linha por migration, checksum e transacao;
6. baseline legado sempre explicita e rigorosa;
7. locks e rollback testados nos dois adaptadores;
8. SQLite ausente criado somente com opcao explicita;
9. flag e APP_ENV aplicados de forma restritiva;
10. testes sentinela para admin, write_state e sync_business_tables;
11. matriz minima de 35 cenarios aprovada;
12. suite completa, `py_compile`, `node --check` e `git diff --check` verdes;
13. documentacao de execucao e rollback revisada;
14. nenhum acesso a Railway, producao ou banco externo durante implementacao.

## 29. Arquivos inspecionados

Principais arquivos:

- `server.py`;
- `environment_config.py`;
- `wsgi.py`;
- `.env.example`;
- `Procfile`;
- `railway.json`;
- `run_flask.ps1`;
- `requirements.txt`;
- `README_FLASK.md`;
- `docs/ARCHITECTURE.md`;
- `docs/ENVIRONMENTS.md`;
- `docs/SECURITY.md`;
- `docs/TESTING.md`;
- os 11 arquivos `tests/test_*.py` versionados na base.

## 30. Escopo e garantias desta sprint

O unico arquivo criado foi este relatorio. Nao houve alteracao em codigo
produtivo, frontend, configuracao de runtime, schema, dados ou testes. Nao
houve migration, DDL, DML, merge, push, deploy, acesso ao Railway, producao ou
banco externo.
