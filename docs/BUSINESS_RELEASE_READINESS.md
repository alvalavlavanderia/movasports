# Etapa 19 - Consolidacao e Preparacao para Publicacao

## Objetivo

Consolidar as Etapas Business 2 a 18 e preparar uma publicacao controlada sem
misturar alteracoes, executar migrations implicitamente ou acessar producao
durante a preparacao.

Esta etapa nao executa commit, push, migration ou deploy. Cada operacao exige
autorizacao especifica.

## Estado avaliado

- base tecnica: `e6b9ac6a10d45b06b19a92eb1d3150f903e64ef5`;
- branch de trabalho: `business/clients-stage2`;
- `main`: `a5fceba7e08ca779973e6d683867c7c4bab81530`;
- alteracoes Business: acumuladas e ainda nao versionadas;
- schema exigido pela aplicacao: versao 18;
- migrations disponiveis: v1 a v18;
- validacao local: 509 testes aprovados;
- nenhuma migration foi executada em banco operacional ou de producao;
- nenhum push ou deploy foi executado.

## Bloqueios atuais

1. O pacote Business ainda nao possui commit revisavel.
2. O estado estrutural do PostgreSQL de producao nao foi consultado.
3. Nao existe candidata limpa contendo exclusivamente as Etapas 2 a 18.
4. O backend exige schema v18; publicar o codigo antes da evolucao controlada
   do banco pode deixar `/api/readiness` indisponivel.
5. Ainda existem chamadas legadas de `init_db()` em rotas HTTP. Elas nao
   substituem migrations e permanecem como risco tecnico conhecido.
6. O healthcheck do Railway consulta `/api/health`, que comprova processo ativo,
   mas nao substitui a verificacao de `/api/readiness`.

## Fase 19.1 - Consolidacao Git

Executar somente apos autorizacao:

1. confirmar o inventario completo de arquivos alterados e novos;
2. verificar ausencia de banco, backup, upload, log, cache, `.env` e segredos;
3. criar uma branch Business de consolidacao a partir da base exata;
4. criar commit ou commits revisaveis sem incorporar branches WIP;
5. criar worktree limpo para a candidata;
6. executar a suite e as verificacoes estaticas na arvore limpa;
7. comparar a candidata com o snapshot aprovado das Etapas 2 a 18.

O conjunto nao deve ser integrado diretamente a `main` a partir do worktree
atual, pois ele contem alteracoes acumuladas ainda sem revisao Git.

## Fase 19.2 - Diagnostico somente leitura do banco

Antes de qualquer migration:

1. confirmar o commit candidato;
2. confirmar `APP_ENV=production` e `DATABASE_URL` sem exibir valores;
3. executar `python -m database_migrations status`;
4. executar `python -m database_bootstrap status`;
5. registrar apenas estado, driver e versoes, nunca URL, senha ou hash.

Decisoes:

- `up_to_date` na versao 18: nao aplicar migration;
- banco versionado anterior: aplicar somente as migrations pendentes;
- banco legado compativel: interromper e preparar baseline explicita;
- banco legado incompativel, checksum divergente, lacuna ou versao futura:
  interromper sem alterar dados;
- banco vazio: aplicar migrations e depois executar bootstrap explicito.

## Fase 19.3 - Backup e migrations

Para banco existente:

1. criar snapshot ou backup logico verificavel;
2. registrar o ponto de restauracao;
3. habilitar `MOVA_ALLOW_MIGRATIONS=true` somente no processo administrativo;
4. executar:

```text
python -m database_migrations migrate --confirm-production
```

5. restaurar `MOVA_ALLOW_MIGRATIONS=false`;
6. confirmar versao 18 com `database_migrations status`;
7. validar `/api/readiness` com o codigo candidato em ambiente controlado.

As migrations sao aplicadas em ordem, possuem historico e transacao por
migration. Algumas migrations preenchem campos novos com dados ja existentes;
por isso o backup continua obrigatorio, mesmo sem comandos destrutivos.

## Fase 19.4 - Bootstrap

Instalacao existente:

- nao executar bootstrap;
- nao configurar `MOVA_ADMIN_PASSWORD`;
- preservar loja, estado e usuarios atuais.

Banco realmente novo:

1. aplicar todas as migrations;
2. consultar `database_bootstrap status`;
3. fornecer a senha somente em variavel temporaria;
4. habilitar `MOVA_ALLOW_BOOTSTRAP=true` somente no processo administrativo;
5. executar `database_bootstrap run` com `--confirm-bootstrap` e
   `--confirm-production`;
6. remover a variavel de senha e desabilitar a flag;
7. validar login sem registrar credenciais.

## Fase 19.5 - Deploy

Ordem recomendada:

1. aprovar candidata limpa;
2. confirmar backup;
3. preparar o schema v18;
4. manter importacao e reset desabilitados;
5. publicar o commit aprovado;
6. acompanhar build e startup sem expor variaveis;
7. validar `/api/health`;
8. validar `/api/readiness`;
9. testar login existente;
10. executar smoke tests somente leitura;
11. liberar operacao gradualmente.

## Smoke tests

- pagina de login abre pelo dominio oficial;
- autenticacao local ou via `file:` permanece indisponivel;
- usuario existente entra com a mesma credencial;
- sessao e logout funcionam;
- Dashboard carrega conforme o perfil;
- configuracoes sensiveis permanecem exclusivas do Administrador;
- importacao e reset retornam bloqueio em producao;
- produtos, clientes, fornecedores e configuracoes podem ser consultados;
- nenhuma resposta contem senha ou `password_hash`;
- `/api/readiness` retorna sucesso.

Testes que criem venda, movimentem estoque, recebam parcelas ou alterem
financeiro exigem autorizacao e dados de homologacao.

## Rollback

Se o deploy falhar antes das migrations:

- interromper a publicacao e manter o banco intacto.

Se o schema v18 estiver aplicado e o novo codigo falhar:

- nao desfazer migrations manualmente;
- manter o snapshot preservado;
- avaliar retorno temporario ao commit anterior, pois as alteracoes estruturais
  sao aditivas;
- se houver incompatibilidade operacional, restaurar o snapshot somente com
  autorizacao e janela de manutencao.

Nao usar `git reset --hard`, apagar historico de migrations ou editar tabelas
manualmente como mecanismo de rollback.

## Variaveis de producao

Obrigatorias ou esperadas:

- `APP_ENV=production`;
- `DATABASE_URL`;
- `MOVA_SECRET_KEY` forte;
- `PORT`, fornecida pela plataforma;
- configuracao valida do Cloudinary para persistencia das imagens.

Devem permanecer desabilitadas:

- `MOVA_ALLOW_MIGRATIONS=false`;
- `MOVA_ALLOW_DATA_IMPORT_RESET=false`;
- `MOVA_ALLOW_BOOTSTRAP=false`.

Variaveis de senha de bootstrap devem existir apenas durante a operacao
administrativa explicitamente autorizada.

## Criterio de prontidao

A publicacao somente esta pronta quando:

1. o pacote Business estiver versionado e revisado;
2. a candidata limpa repetir os 509 testes;
3. o status estrutural do banco for conhecido;
4. houver backup valido;
5. o plano de migration correspondente ao estado real estiver aprovado;
6. as variaveis estiverem conferidas sem exposicao de segredos;
7. rollback e responsavel operacional estiverem definidos.
