# Segurança

## Objetivo

Garantir que toda alteração preserve a integridade dos dados, a segurança dos usuários e a estabilidade do sistema.

---

# Dados sensíveis

Nunca:

- expor senhas;
- expor tokens;
- expor chaves da API;
- expor credenciais do banco;
- expor dados pessoais de clientes.

---

# Banco

Sempre:

- utilizar transações quando necessário;
- validar entradas;
- evitar exclusões permanentes;
- utilizar migrations reversíveis;
- manter compatibilidade.

Nunca:

- apagar tabelas;
- apagar colunas;
- alterar produção sem autorização.

---

# Backend

Toda requisição deve validar:

- autenticação;
- autorização;
- dados recebidos.

Nunca confiar apenas no frontend.

## Credenciais de usuários

- A tabela `users` e o campo `password_hash` são a única fonte de autenticação.
- Senhas em texto existem apenas durante requisições específicas de login, criação ou alteração e não são persistidas em estado, logs ou respostas.
- `app_state`, importações e atualizações genéricas não podem criar ou alterar credenciais.
- Credenciais legadas no `app_state` permanecem preservadas internamente na Fase 1, mas não são usadas nem expostas.
- O modo de autenticação offline por `file:` está descontinuado; falha de rede mantém o usuário desconectado.
- O navegador não deve armazenar senha, hash ou verificador equivalente em memória global, `localStorage` ou `sessionStorage`.
- Usuário sem hash válido não pode ser corrigido ou reconstruído automaticamente; o fluxo deve ser bloqueado com aviso sem identificação ou credencial.
- O bootstrap não utiliza senha padrão: um banco novo só recebe o administrador quando `MOVA_ADMIN_PASSWORD` foi configurada explicitamente.
- A ausência da variável não interrompe a aplicação e não cria credencial; o log informa apenas a configuração necessária.

---

# Uploads

Validar:

- extensão;
- tamanho;
- tipo do arquivo.

Evitar sobrescrever arquivos existentes.

---

# Auditoria

Sempre que possível registrar:

- usuário;
- data;
- ação;
- registro alterado;
- valores anteriores.

---

# Logs

Logs nunca devem conter:

- senha;
- token;
- CPF;
- cartão;
- credenciais.

---

# Produção

Nunca:

- fazer deploy automaticamente;
- alterar produção sem autorização;
- executar comandos destrutivos.

---

# Ambientes

- Configurar `APP_ENV` explicitamente como `development`, `staging` ou `production`.
- Ausência ou valor inválido ativa temporariamente um modo compatível e restritivo, nunca desenvolvimento implícito.
- `MOVA_ALLOW_MIGRATIONS` e `MOVA_ALLOW_DATA_IMPORT_RESET` permanecem desabilitadas por padrão.
- `production` não recebe capacidades sensíveis apenas porque uma flag foi habilitada.
- Bancos, segredos e uploads não devem ser compartilhados entre ambientes.
- A importação de `wsgi.py` não pode alterar banco ou dados.
- As regras operacionais estão documentadas em `docs/ENVIRONMENTS.md`.
- Importação, reset e substituição integral do estado exigem administrador autenticado, ambiente de desenvolvimento ou homologação e liberação explícita da capacidade.
- Produção, ambiente ausente e ambiente inválido sempre bloqueiam importação, reset e substituição integral do estado.
- Tentativas bloqueadas devem usar log seguro sem payload, arquivos, identificação pessoal, credenciais ou escrita de auditoria no banco.
- A interface recebe apenas capacidades booleanas calculadas pelo backend; elas não substituem a autorização das rotas.

---

# Git

Nunca:

- fazer push automaticamente;
- apagar histórico;
- alterar branches principais sem autorização.
