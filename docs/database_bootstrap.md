# Bootstrap administrativo do banco

## Finalidade

O pacote `database_bootstrap` cria somente os dados operacionais minimos de uma
instalacao Mova Sports cujo schema ja foi preparado e validado por migrations:

- loja operacional `matriz`;
- singleton `app_state` com `id=1`;
- primeiro usuario administrador.

O bootstrap nao cria ou altera tabelas, indices, constraints ou o historico de
migrations. Ele nao popula produtos, clientes, vendas, estoque, caixa,
recebiveis, contas a pagar ou dados demonstrativos.

## Separacao de responsabilidades

- `database_migrations`: evolucao estrutural e `schema_migrations`.
- `database_bootstrap`: dados operacionais minimos da primeira instalacao.
- `server.py`: operacoes normais da aplicacao.

O bootstrap nao e chamado por HTTP, import, WSGI, Gunicorn, startup, health,
readiness, login, sessao ou hooks Flask. Importar o pacote nao abre conexao e
nao executa SQL. Nao existe endpoint HTTP de bootstrap.

## Pre-requisitos

Antes de executar `run`, o banco deve:

1. existir e estar acessivel;
2. possuir `schema_migrations`;
3. possuir a migration 001 registrada com descricao e checksum validos;
4. nao possuir migrations pendentes ou futuras;
5. corresponder integralmente ao schema atual;
6. nao apresentar dados operacionais incompatíveis.

O bootstrap nunca aplica migration, registra baseline ou repara schema.

## Status somente leitura

```powershell
python -m database_bootstrap status
```

`status` nao exige autorizacao de escrita. No SQLite ele usa `mode=ro`, nao
cria arquivo ausente e nao corrige inconsistencias. A saida JSON informa o
driver, ambiente, versao estrutural e situacao de store, app_state e admin sem
expor URL, senha, hash ou conteudo do estado.

Estados estruturais incluem `DATABASE_MISSING`, `DATABASE_UNAVAILABLE`,
`SCHEMA_MIGRATIONS_MISSING`, `SCHEMA_INVALID`, `SCHEMA_OUTDATED`,
`SCHEMA_FUTURE` e `MIGRATION_HISTORY_INVALID`.

Estados operacionais incluem `BOOTSTRAP_NOT_STARTED`, `BOOTSTRAP_PARTIAL` e
`BOOTSTRAP_COMPLETE`. Stores, estado ou administradores incompatíveis bloqueiam
a escrita e exigem revisao manual.

## Execucao explicita

Configure temporariamente uma senha sintetica ou real adequada no ambiente do
processo. O valor abaixo e apenas o nome da variavel, nao a senha:

```powershell
$env:APP_ENV = "development"
$env:MOVA_ALLOW_BOOTSTRAP = "true"
$env:MOVA_BOOTSTRAP_ADMIN_PASSWORD = "<defina-fora-do-historico-do-shell>"

python -m database_bootstrap run `
  --confirm-bootstrap `
  --store-name "Loja Matriz" `
  --admin-name "Administrador" `
  --admin-login "admin" `
  --admin-password-env MOVA_BOOTSTRAP_ADMIN_PASSWORD
```

Nao passe senha diretamente como argumento. A opcao
`--admin-password-env` recebe somente o nome da variavel que contem a senha.

## Autorizacao

Toda escrita exige simultaneamente:

- `APP_ENV` reconhecido;
- `MOVA_ALLOW_BOOTSTRAP` com `1`, `true`, `yes` ou `on`;
- comando `run` explicito;
- `--confirm-bootstrap`;
- dados obrigatorios de store e administrador;
- senha obtida da variavel indicada.

Em `production`, `--confirm-production` tambem e obrigatorio. A autorizacao de
bootstrap e independente de `MOVA_ALLOW_MIGRATIONS`. Valores desconhecidos de
flag sao tratados como falsos.

Remova a variavel de senha do ambiente quando o procedimento operacional
estiver concluido e validado. A aplicacao armazena somente o hash Werkzeug em
`users.password_hash`.

## Contratos criados

### Store

O runtime atual usa explicitamente `store_id=matriz`. O comando cria essa store
somente quando nenhuma store existe. Store existente nao e renomeada, removida
ou modificada. A tabela atual nao possui coluna `active`.

### App state

O schema atual define um unico registro global `app_state.id=1` e nao possui
coluna `store_id`. O JSON inicial contem somente as colecoes reconhecidas pela
aplicacao, todas vazias, inclusive `users`. Nao contem senha, hash, dados
pessoais, timestamps internos ou exemplos.

### Administrador

O primeiro administrador usa o identificador reservado `admin`, role `admin`,
`active=1` e `store_id=matriz`. Nome e login sao obrigatorios. A senha deve ter
ao menos oito caracteres, nao pode ser uma senha comum nem ser igual ao login.

Administrador existente nao tem nome, login, status ou senha alterados.
Operador nao e promovido, administrador inativo nao e reativado e conflitos de
identificador, login ou store bloqueiam o comando.

## Idempotencia e estados parciais

Uma segunda execucao sobre estado completo nao altera dados e retorna
`already_complete=true`. Em estado parcial integralmente compativel, somente os
componentes ausentes sao criados. Dados existentes nunca sao sobrescritos.

## Transacao, locking e rollback

No SQLite, `run` abre arquivo existente em modo `rw`, habilita foreign keys e
usa `BEGIN IMMEDIATE`. Store, app_state e admin sao criados na mesma transacao.

No PostgreSQL, a conexao usa `autocommit=False`, timeouts locais e advisory lock
`556079114083002502`, distinto do lock das migrations
`556079114083002501`. O status e relido depois do lock.

Qualquer falha executa rollback integral. Conexoes sao fechadas explicitamente
em sucesso ou erro. Execucoes concorrentes nao dependem apenas de constraints:
o estado e relido depois da aquisicao do lock.

## Banco novo

1. Criar ou apontar o banco.
2. Executar migrations explicitamente.
3. Validar `python -m database_migrations status`.
4. Validar `python -m database_bootstrap status`.
5. Configurar a senha em variavel de ambiente temporaria.
6. Executar `database_bootstrap run` com as confirmacoes.
7. Validar status completo e login.
8. Remover a variavel de senha quando operacionalmente adequado.
9. Liberar trafego apenas em etapa operacional aprovada.

## Banco legado

1. Produzir backup ou snapshot.
2. Validar integralmente o schema.
3. Registrar baseline explicita, quando aplicavel.
4. Validar o status das migrations.
5. Consultar o status do bootstrap.
6. Nao recriar nem corrigir dados existentes automaticamente.
7. Executar bootstrap apenas para componentes ausentes compativeis.
8. Validar a aplicacao.

## Riscos residuais

- O bootstrap legado ainda existe dentro de `init_db()`.
- Rotas remanescentes ainda alcancam `init_db()`.
- A remocao desse legado pertence a Sprint 5B.6.
- PostgreSQL e validado por adapter simulado; nao houve acesso a banco externo.
- Readiness estrutural nao verifica os dados operacionais do bootstrap.
- A senha inicial exige procedimento operacional seguro fora do historico do
  shell e dos logs.
