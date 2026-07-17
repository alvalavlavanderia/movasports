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

---

# Git

Nunca:

- fazer push automaticamente;
- apagar histórico;
- alterar branches principais sem autorização.
