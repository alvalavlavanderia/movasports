# Migrations versionadas do banco

## Finalidade

O pacote `database_migrations` controla a evolucao estrutural do banco da Mova
Sports. Ele e independente do servidor Flask e somente executa alteracoes por
um comando administrativo explicito.

O import do pacote, o startup WSGI, requisicoes HTTP, `health`, `readiness`,
login e sessao nunca executam migrations. Nao existe endpoint HTTP de
migration.

## Autorizacao

Comandos que escrevem exigem simultaneamente:

- `APP_ENV` igual a `development`, `staging` ou `production`;
- `MOVA_ALLOW_MIGRATIONS` com um valor verdadeiro reconhecido: `1`, `true`,
  `yes` ou `on`;
- em `production`, o argumento adicional `--confirm-production`.

Valores ausentes, falsos ou desconhecidos bloqueiam a operacao. A flag nunca
faz a migration rodar automaticamente.

O comando `status` e somente leitura e nao exige a flag de escrita.

## Comandos

Consultar o estado sem alterar ou criar o banco:

```powershell
python -m database_migrations status
```

Aplicar migrations pendentes em banco existente:

```powershell
python -m database_migrations migrate
```

Criar explicitamente um arquivo SQLite ausente e aplicar a migration inicial:

```powershell
python -m database_migrations migrate --create
```

O argumento `--create` so se aplica ao SQLite. Sem ele, um arquivo ausente e
recusado e nao e criado.

Registrar a baseline de um banco legado integralmente compativel:

```powershell
python -m database_migrations baseline --version 1 --confirm-baseline
```

Em producao, acrescente `--confirm-production` ao comando de escrita. Os
comandos tambem podem ser executados por `python migration_runner.py`.

## Migration 001

A migration `001_create_current_schema` representa o schema consolidado atual:

- 19 tabelas operacionais;
- 30 indices;
- constraints, chaves estrangeiras e defaults atuais;
- `payables.discount` presente desde o `CREATE TABLE`.

Ela nao executa o `ALTER TABLE` historico de `payables.discount` e nao insere
dados. Nenhuma loja, linha de `app_state`, usuario administrador, seed ou dado
demonstrativo e criado.

## Historico e checksum

Cada migration aplicada gera uma linha imutavel em `schema_migrations` com:

- `version`;
- `description`;
- `applied_at` em UTC;
- `checksum` SHA-256;
- `execution_time_ms`.

O checksum usa uma representacao canonica de versao, descricao, SQL SQLite,
SQL PostgreSQL e identificador de codigo. Finais de linha e espacos externos
sao normalizados, mantendo o resultado estavel entre Windows e Linux.

Descricao ou checksum divergente, versao duplicada, lacuna e versao futura
bloqueiam a execucao. O historico nunca e corrigido automaticamente.

## Banco legado e baseline

Banco com tabelas existentes e sem `schema_migrations` nunca recebe a migration
001 automaticamente. O operador deve usar `baseline`, que:

1. exige banco existente e confirmacao explicita;
2. valida integralmente tabelas, colunas, tipos, nullability, defaults,
   primary keys, foreign keys, checks e os 30 indices;
3. recusa banco vazio ou schema parcial;
4. cria apenas `schema_migrations` e registra a versao 1;
5. nao executa DDL de negocio nem altera dados existentes.

## Transacoes e concorrencia

No SQLite, cada migration usa uma conexao dedicada, `BEGIN IMMEDIATE`, commit
somente no final e rollback integral em erro. Nenhum PRAGMA persistente e
alterado.

No PostgreSQL, a conexao dedicada usa `autocommit=False`, transacao, timeout de
lock de 30 segundos, timeout de statement de 10 minutos e
`pg_advisory_xact_lock(556079114083002501)`. O historico e relido depois do
lock para impedir aplicacao duplicada concorrente.

Conexoes sao sempre fechadas. Falha parcial nao registra a migration e nao
executa migrations posteriores.

## Separacao de bootstrap

Migration trata somente schema. Bootstrap de loja, `app_state`, administrador
e dados iniciais permanece fora do runner. O runner nao chama `init_db()`,
`write_state()`, `sync_business_tables()` nem `create_initial_admin_user()`.

## Saida segura

O CLI retorna JSON operacional e codigo de saida diferente de zero em erro.
Ele nao exibe `DATABASE_URL`, caminho do SQLite, credenciais, dados pessoais ou
stack trace por padrao.
