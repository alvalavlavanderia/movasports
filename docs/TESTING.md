# Testes e Validação — Mova Sports

## Objetivo

Este documento define os padrões mínimos de testes e validações do Mova Sports.

Toda alteração deve ser validada de acordo com o risco e o impacto da funcionalidade.

O objetivo é evitar regressões, inconsistências financeiras, erros de estoque e perda de dados.

---

# 1. PRINCÍPIOS GERAIS

Antes de concluir qualquer alteração:

- verificar se o sistema continua iniciando normalmente;
- verificar erros de sintaxe;
- executar os testes automatizados existentes;
- testar o fluxo alterado;
- testar os principais fluxos relacionados;
- revisar possíveis efeitos colaterais;
- não considerar uma tarefa concluída apenas porque não houve erro visual.

Alterações financeiras exigem validação mais rigorosa.

---

# 2. NÍVEIS DE RISCO

## Baixo risco

Exemplos:

- texto;
- espaçamento;
- ícone;
- pequena alteração visual.

Validar:

- aparência;
- responsividade;
- ausência de regressão visual.

## Médio risco

Exemplos:

- filtros;
- formulários;
- consultas;
- Dashboard;
- relatórios.

Validar:

- resultado esperado;
- estados vazios;
- filtros;
- dados reais;
- possíveis efeitos em módulos relacionados.

## Alto risco

Exemplos:

- vendas;
- cancelamentos;
- devoluções;
- estoque;
- crediário;
- pagamentos;
- caixa;
- financeiro;
- banco de dados.

Exigir:

- análise antes da alteração;
- testes do fluxo principal;
- testes de exceção;
- validação dos efeitos em módulos relacionados;
- revisão do estado antes e depois da operação.

---

# 3. VENDAS

Testar, quando aplicável:

- venda com cliente cadastrado;
- venda com cliente padrão;
- venda em dinheiro;
- venda em Pix;
- venda em débito;
- venda em crédito;
- venda em crediário;
- venda com pagamento misto;
- venda com desconto;
- tentativa de vender produto sem estoque;
- tentativa de vender quantidade superior ao estoque;
- cliente com parcelas vencidas;
- cliente ultrapassando limite de crédito.

Após a venda, validar:

- registro da venda;
- baixa correta do estoque;
- formas de pagamento;
- movimentação financeira;
- atualização do Dashboard;
- histórico do cliente.

---

# 4. CANCELAMENTO DE VENDA

Testar separadamente:

- Dinheiro;
- Pix;
- Débito;
- Crédito;
- Crediário;
- Pagamento misto.

Após cancelar, validar:

- venda marcada como cancelada;
- histórico preservado;
- estoque devolvido corretamente;
- faturamento corrigido;
- lucro corrigido;
- caixa corrigido quando aplicável;
- crediário corrigido;
- Dashboard atualizado.

## Idempotência

Uma venda já cancelada não pode gerar um segundo estorno.

Repetir a ação não pode:

- devolver estoque novamente;
- gerar nova saída financeira;
- cancelar parcelas novamente.

---

# 5. DEVOLUÇÕES E TROCAS

Testar:

- devolução total;
- devolução parcial;
- troca;
- múltiplos produtos;
- diferentes formas de pagamento.

Validar:

- retorno correto ao estoque;
- histórico preservado;
- impacto financeiro;
- impacto no faturamento;
- impacto no lucro;
- impacto no Dashboard;
- ausência de duplicidade.

---

# 6. ESTOQUE

Testar:

- entrada inicial;
- saída por venda;
- retorno por cancelamento;
- retorno por devolução;
- reserva por condicional;
- devolução de condicional;
- venda de condicional;
- inventário.

Nunca permitir:

- estoque negativo;
- alteração silenciosa;
- duplicidade de movimentação.

---

# 7. INVENTÁRIO

Validar:

- quantidade anterior;
- quantidade contada;
- diferença;
- quantidade final;
- usuário responsável;
- data e hora;
- motivo.

Somente o administrador pode confirmar o ajuste.

---

# 8. CREDIÁRIO

Testar:

- criação das parcelas;
- pagamento integral;
- pagamento parcial;
- antecipação;
- parcelas vencidas;
- juros;
- multas;
- cancelamento da venda vinculada.

Validar:

- valor original;
- valor pago;
- saldo restante;
- situação da parcela;
- impacto no caixa;
- impacto no Dashboard;
- histórico.

---

# 9. CAIXA E FINANCEIRO

Testar:

- entrada automática;
- entrada manual;
- saída manual;
- conta a pagar;
- conta a receber;
- venda em dinheiro;
- venda em Pix;
- cancelamento;
- devolução.

Validar sempre:

Saldo final = saldo anterior + entradas - saídas

Nenhuma movimentação deve ser duplicada.

Toda movimentação deve possuir origem rastreável.

---

# 10. CLIENTES

Testar:

- cadastro somente com campos obrigatórios;
- campos opcionais vazios;
- normalização e validação matemática do CPF;
- unicidade do CPF inclusive em clientes desativados;
- alerta não bloqueante de possível duplicidade por nome ou telefone;
- validação de nascimento, e-mail e limite de crédito;
- limite de crédito;
- histórico de alteração do limite com usuário e data;
- bloqueio, desbloqueio e desativação com histórico;
- desativação;
- alerta de inadimplência;
- ultrapassagem de limite;
- ficha consolidada com compras, pagamentos, crediário e condicionais;
- cliente padrão protegido e impedido em crediário e condicional;
- venda simples usando o cliente padrão;
- cliente bloqueado impedido apenas em crediário e condicional;
- rollback quando auditoria ou persistência falhar;
- contrato visual da tela de cadastro, busca, indicadores e detalhes;
- Score.

Clientes não devem ser excluídos definitivamente.

Cobertura automatizada da Etapa 2:

- `tests/test_customer_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_bootstrap.py`;
- `tests/test_database_bootstrap_postgresql.py`;
- `tests/test_database_readiness.py`.

As migrations são executadas somente contra bancos temporários descartáveis
durante os testes. A Etapa 2 não autoriza execução contra banco operacional ou
de produção.

## 10.1 Fornecedores e cadastros auxiliares

Validar:

- cadastro completo do fornecedor e campos opcionais;
- CPF/CNPJ opcional, matematicamente válido e único;
- normalização de documento, e-mail e UF;
- busca por nome, nome fantasia, documento e telefone;
- indicadores de fornecedores ativos, contas abertas e vencidas;
- desativação com confirmação quando houver vínculo financeiro aberto;
- reativação e histórico de situação;
- preservação de contas e demais vínculos após desativação;
- ausência de exclusão física no fluxo normal;
- nomes normalizados e únicos para marca, categoria, tamanho, cor e categoria
  de despesa;
- IDs estáveis e estados ativo/desativado dos cadastros auxiliares;
- categorias de despesa padrão sem duplicidade;
- Produto vinculado por ID a marca, categoria, tamanho, cor e fornecedor;
- Conta a Pagar vinculada por ID a fornecedor e categoria de despesa ativos;
- saída manual do Caixa vinculada por ID a categoria de despesa ativa;
- gênero de Produto restrito a Masculino, Feminino, Unissex e Infantil;
- alteração de marca no cadastro sem reescrever o snapshot histórico da venda;
- criação rápida de fornecedor a partir de Conta a Pagar e de marca, categoria,
  tamanho e cor a partir de Produto;
- auditoria, espelho de compatibilidade e isolamento por loja;
- migration v3 aditiva para SQLite e PostgreSQL.

Cobertura automatizada da Etapa 3:

- `tests/test_supplier_auxiliary_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_bootstrap.py`;
- `tests/test_database_bootstrap_postgresql.py`;
- `tests/test_database_readiness.py`;
- testes de persistência de Contas a Pagar.

Entradas de mercadoria, devoluções ao fornecedor, créditos e garantias não
pertencem à Etapa 3 e devem ser validados nas etapas que criarem esses fluxos.
Nenhuma migration da Etapa 3 deve ser executada contra banco operacional ou de
produção sem autorização específica.

## 10.2 Produtos e Entradas - núcleo

Validar:

- consulta por código normalizado sem persistência quando o produto não existe;
- primeira Entrada criando produto, item, movimento, saldo e auditoria na mesma
  transação;
- novas Entradas somando ao estoque real existente;
- quantidade inteira e maior que zero;
- preço de custo e preço de venda positivos;
- fornecedor, marca e categoria ativos e vinculados por ID;
- snapshot de produto, fornecedor, custo, preço e saldo em cada item da Entrada;
- custo atual do produto atualizado pela Entrada mais recente, sem custo médio;
- estoque real, reservado em Condicional e disponível;
- edição cadastral sem alteração direta de estoque e sem movimento artificial;
- produto inativo identificado como existente e bloqueado até reativação
  explícita;
- código único por loja;
- numeração automática de Entrada por loja;
- chave de idempotência com repetição segura e conflito para payload diferente;
- rollback integral quando qualquer gravação ou auditoria falhar;
- proteção contra exclusão de produto com histórico de Entrada;
- histórico das Entradas e contrato visual do cadastro;
- caminhos SQLite e PostgreSQL.

Cobertura automatizada da Etapa 4:

- `tests/test_product_stock_entry_business_rules.py`;
- `tests/test_supplier_auxiliary_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_bootstrap.py`;
- `tests/test_database_bootstrap_postgresql.py`;
- `tests/test_database_readiness.py`.

A migration v4 é aditiva e executada nos testes apenas contra bancos temporários
descartáveis. Cancelamento de Entrada, Contas a Pagar vinculadas, devolução ao
fornecedor, créditos e frete pertencem à Etapa 5.

---

## 10.3 Entradas e financeiro de compras

Validar:

- criacao de uma ou varias Contas a Pagar vinculadas a uma Entrada;
- preservacao do fornecedor e da categoria Mercadorias;
- diferenca permitida entre o total da Entrada e o total financeiro;
- cancelamento integral e idempotente da Entrada;
- bloqueio do cancelamento quando houver efeito financeiro ou estoque
  indisponivel;
- cancelamento de contas vinculadas ainda pendentes;
- devolucao parcial ou total ao fornecedor, limitada pela quantidade original
  e pelo estoque disponivel;
- custo historico da Entrada aplicado ao valor devolvido;
- abatimento em Conta a Pagar, credito de fornecedor, reembolso em Dinheiro ou
  Pix e valor pendente;
- uso FIFO do credito somente em conta do mesmo fornecedor;
- pagamento de Conta a Pagar somente por Dinheiro, Pix ou Debito;
- reversao e cancelamento sem duplicidade;
- auditoria e rollback integral;
- caminhos SQLite e PostgreSQL.

Cobertura automatizada da Etapa 5:

- `tests/test_purchase_financial_business_rules.py`;
- `tests/test_payable_payment_persistence.py`;
- `tests/test_product_stock_entry_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_readiness.py`.

A migration v5 e aditiva e somente e aplicada pelos testes em bancos
temporarios descartaveis. Nenhuma migration desta etapa foi executada em banco
operacional ou de producao.

# 11. DASHBOARD

Validar:

- vendas de hoje;
- vendas do mês;
- lucro do mês;
- valor do estoque;
- crediário em aberto;
- saldo em caixa;
- entradas;
- saídas;
- contas a pagar;
- contas a receber;
- vendas por dia;
- formas de pagamento;
- marcas mais vendidas;
- peças paradas.

Testar também:

- vendas canceladas;
- devoluções;
- pagamentos mistos;
- mudança de período;
- ausência de dados;
- virada do dia.

---

# 12. TESTES DE REGRESSÃO

Após alterações de alto risco, verificar os fluxos relacionados.

Exemplo:

Ao alterar cancelamento de venda, testar também:

- estoque;
- caixa;
- crediário;
- Dashboard;
- histórico.

Uma correção não deve causar erro em outro módulo.

---

# 13. VALIDAÇÕES TÉCNICAS

Quando aplicável, executar os comandos disponíveis no projeto.

Para Flutter:

flutter analyze
flutter test

Para JavaScript:

node --check script.js

Para Python:

utilizar as verificações e testes disponíveis no projeto.

Não executar comandos destrutivos.

---

# 14. DADOS DE TESTE

Preferir dados fictícios.

Não utilizar dados pessoais reais em:

- testes;
- logs;
- documentação;
- exemplos.

Quando possível, criar cenários de teste reproduzíveis.

---

# 15. CHECKLIST ANTES DE CONCLUIR

Antes de considerar uma tarefa concluída:

- [ ] O código executa sem erros?
- [ ] O fluxo principal foi testado?
- [ ] Os casos de erro foram considerados?
- [ ] Os dados existentes foram preservados?
- [ ] Estoque permanece consistente?
- [ ] Caixa permanece consistente?
- [ ] Crediário permanece consistente?
- [ ] Dashboard permanece consistente?
- [ ] Não existe duplicidade de operação?
- [ ] Não foram expostos dados sensíveis?
- [ ] O diff foi revisado?
- [ ] A documentação precisa ser atualizada?

---

# 16. REGRA PARA O CODEX

O Codex deve:

1. identificar o nível de risco da tarefa;
2. informar quais testes são necessários;
3. executar os testes disponíveis;
4. informar claramente o que foi e o que não foi testado;
5. nunca afirmar que uma funcionalidade está validada quando não foi possível testá-la.

Alterações de alto risco devem ser implementadas em etapas pequenas e revisáveis.

---

# 17. CONFIGURAÇÃO DE AMBIENTES

Testar sem conexão de banco ou rede:

- reconhecimento de `development`, `staging` e `production`;
- tratamento restritivo de `APP_ENV` ausente ou inválida;
- flags sensíveis desabilitadas por padrão;
- impossibilidade de produção adquirir capacidade sensível por flags;
- ausência de segredos e URLs completas em avisos de log;
- importação de `wsgi.py` sem inicialização ou alteração de banco.

Os testes devem fornecer um mapa de variáveis diretamente à função de configuração. Não devem alterar variáveis do Railway, abrir o banco de produção ou utilizar credenciais reais.

## 18. IMPORTAÇÃO E RESET

Validar com banco temporário e descartável:

- bloqueio sem autenticação e para operador;
- bloqueio com flag desabilitada, ambiente ausente ou inválido;
- bloqueio permanente em produção;
- permissão exclusiva para administrador em `development` ou `staging` com flag explicitamente habilitada;
- autorização antes de ler payload, arquivo ou acessar o banco;
- ausência de escrita e de conteúdo sensível nos logs de tentativas bloqueadas;
- capacidade booleana da sessão e limpeza imediata no logout, expiração ou troca de usuário;
- ocultamento exclusivo dos controles Restaurar dados e Zerar sistema.

## 19. CREDENCIAIS FORA DO APP_STATE

Validar exclusivamente com banco temporário e sem conexão externa:

- login existente sem alteração do hash;
- criação e alteração de senha gravando somente `users.password_hash`;
- edição de dados públicos preservando o hash;
- ausência de senha e hash em estado, exportação, sessão e respostas de usuários;
- entradas genéricas incapazes de criar ou alterar credenciais;
- preservação interna, sem uso ou exposição, de chaves legadas do `app_state`;
- bloqueio de reconstrução quando `users` está vazia em instalação legada;
- bootstrap com hash somente em banco comprovadamente novo;
- hash ausente ou inválido bloqueado sem correção automática ou log sensível;
- navegador sem credenciais em objetos globais, `localStorage` ou `sessionStorage`;
- abertura via `file:` e falha da API sem fallback local de autenticação;
- login, sessão e logout normais pelo backend Flask.
- banco novo com e sem `MOVA_ADMIN_PASSWORD`, tanto em development quanto em production;
- ausência da configuração sem criação de administrador, sem segredo em log e sem falha geral de inicialização;
- inexistência de senha padrão no bootstrap e nos testes.

---

# 20. ESTOQUE TRANSACIONAL

Cobertura automatizada da Etapa 6:

- `tests/test_transactional_inventory_business_rules.py`;
- `tests/test_product_stock_entry_business_rules.py`;
- `tests/test_purchase_financial_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`.

Validar:

- saldos real, reservado e disponível em cada origem;
- snapshots de nome e código preservados após edição do produto;
- conflito de concorrência sem gravação parcial;
- espelho de compatibilidade no `app_state`;
- histórico filtrado por produto e tipo;
- produtos sem disponibilidade fora das listas operacionais.

A migration v6 é aditiva e somente deve ser aplicada de forma explícita. Os
testes utilizam bancos temporários descartáveis; nenhuma migration da Etapa 6
foi executada em banco operacional ou de produção.

---

# 22. VENDAS TRANSACIONAIS

Cobertura automatizada da Etapa 9:

- `tests/test_sale_business_rules.py`;
- `tests/test_transactional_inventory_business_rules.py`;
- `tests/test_card_modalities_business_rules.py`;
- `tests/test_customer_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_readiness.py`.

Validar:

- criacao atomica da venda, itens, pagamentos e efeitos financeiros;
- snapshots autoritativos de produto, cliente e modalidade de cartao;
- pagamento misto, dinheiro entregue e troco;
- recebiveis de cartao com taxa e valor liquido;
- crediario identificado, limite, bloqueio e parcelamento;
- saldo disponivel descontando condicionais ativos;
- idempotencia por chave e conflito de reutilizacao;
- rollback integral quando auditoria ou persistencia falhar;
- ausencia de `write_state()`, `sync_business_tables()` e
  `sync_sale_to_state()` no `POST /api/sales`;
- compatibilidade SQLite e caminho PostgreSQL por adaptador simulado.

Comandos de validacao da etapa:

```powershell
python -m unittest tests.test_sale_business_rules
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile server.py environment_config.py
node --check script.js
git diff --check
```

A migration v10 e aditiva e somente deve ser aplicada de forma explicita. Os
testes utilizam bancos temporarios descartaveis; nenhuma migration da Etapa 9
foi executada em banco operacional ou de producao.

---

# 23. CREDIARIO TRANSACIONAL

Cobertura automatizada da Etapa 10:

- `tests/test_store_credit_business_rules.py`;
- `tests/test_sale_business_rules.py`;
- `tests/test_customer_business_rules.py`;
- `tests/test_card_modalities_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_readiness.py`.

Validar:

- cliente identificado, ativo e elegivel;
- limite de credito, autorizacao explicita de excesso e historico;
- maximo de tres parcelas;
- primeiro vencimento confirmado e recorrencia mensal pelo dia-base;
- pagamento total, parcial, antecipado e idempotente;
- desconto por valor e percentual sem saldo negativo;
- desconto integral encerrando a parcela sem entrada de caixa;
- juros, multa e acrescimo somente manuais;
- Dinheiro e Pix com entrada imediata no Caixa;
- Debito e Credito gerando recebivel bancario pelo valor liquido;
- renegociacao separada, com vencimento original e historico preservados;
- auditoria e rollback integral;
- ausencia de `write_state()` e `sync_business_tables()` nos fluxos dedicados;
- compatibilidade SQLite e caminho PostgreSQL por adaptador simulado.

Comandos de validacao da etapa:

```powershell
python -m unittest tests.test_store_credit_business_rules tests.test_sale_business_rules
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile server.py environment_config.py
node --check script.js
git diff --check
```

A migration v11 e aditiva e somente deve ser aplicada de forma explicita. Os
testes utilizam bancos temporarios descartaveis; nenhuma migration da Etapa 10
foi executada em banco operacional ou de producao.

---

# 24. CONDICIONAIS TRANSACIONAIS

Cobertura automatizada da Etapa 11:

- `tests/test_conditional_business_rules.py`;
- `tests/test_transactional_inventory_business_rules.py`;
- `tests/test_sale_business_rules.py`;
- `tests/test_customer_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_readiness.py`.

Validar:

- cliente identificado e ativo;
- numero sequencial, usuario, saida e prazo de tres dias;
- snapshots de produto, custo e preco de referencia;
- reserva sem alteracao do estoque real;
- saldo disponivel descontando reservas ativas;
- retorno parcial, total e em momentos diferentes;
- devolucao liberando somente a reserva correspondente;
- selecao de compra mantendo reserva ate a Venda;
- vinculo entre item do Condicional, retorno e Venda;
- baixa conjunta de estoque real e reserva na Venda;
- finalizacao apenas sem pecas pendentes;
- cancelamento bloqueado com pecas pendentes e motivo obrigatorio;
- idempotencia e concorrencia;
- rollback de documento, reserva, espelho e auditoria;
- indicadores, busca, filtros, detalhe, historico e impressao;
- compatibilidade SQLite e caminho PostgreSQL por adaptador simulado.

Comandos de validacao da etapa:

```powershell
python -m unittest tests.test_conditional_business_rules tests.test_transactional_inventory_business_rules tests.test_sale_business_rules
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile server.py environment_config.py
node --check script.js
git diff --check
```

A migration v12 e aditiva e somente deve ser aplicada de forma explicita. Os
testes utilizam bancos temporarios descartaveis; nenhuma migration da Etapa 11
foi executada em banco operacional ou de producao.

---

# 21. INVENTÁRIO FÍSICO

Cobertura automatizada da Etapa 7:

- `tests/test_physical_inventory_business_rules.py`;
- `tests/test_transactional_inventory_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_readiness.py`.

Validar:

- abertura geral e parcial com snapshot dos saldos;
- estoque reservado por Condicional fora do disponível para contagem;
- quantidade zero diferente de item não contado;
- contagem manual e por código de barras;
- bloqueio de produto fora do escopo;
- conflito de versão sem sobrescrever contagem concorrente;
- finalização bloqueada com itens pendentes;
- divergência exigindo administrador e observação;
- finalização sem divergência permitida ao operador;
- ajustes positivos e negativos no ledger transacional;
- ausência de efeitos em Caixa, Contas a Pagar e Entradas;
- idempotência de abertura e finalização;
- cancelamento preservando histórico sem alterar saldo;
- rollback integral quando movimento, espelho ou auditoria falhar;
- filtros por busca, tipo, situação, responsável e período;
- compatibilidade SQLite e caminho PostgreSQL por adaptador simulado.

A migration v7 é aditiva e somente deve ser aplicada de forma explícita. Os
testes utilizam bancos temporários descartáveis; nenhuma migration da Etapa 7
foi executada em banco operacional ou de produção.

---

# 25. DEVOLUÇÕES, TROCAS E GARANTIAS TRANSACIONAIS

Cobertura automatizada da Etapa 12:

- `tests/test_returns_exchanges_warranties.py`;
- `tests/test_sale_business_rules.py`;
- `tests/test_store_credit_business_rules.py`;
- `tests/test_transactional_inventory_business_rules.py`;
- `tests/test_purchase_financial_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_readiness.py`.

Validar:

- devolução parcial e total com quantidade elegível;
- desconto global rateado, valor líquido e custo histórico;
- estoque recomposto uma única vez;
- pagamento misto alocado proporcionalmente;
- Dinheiro, Pix, Débito, Crédito e Crediário tratados pela origem real;
- recebíveis pendentes reduzidos antes de devolver valores recebidos;
- registros antigos sem vínculo seguro bloqueados para conciliação manual;
- troca com item devolvido, substituto e diferença financeira;
- venda vinculada aos itens novos da troca;
- cancelamento formal de troca, idempotência e reversão integral;
- garantia vinculada a Venda, cliente, item, produto e fornecedor;
- fotos e eventos do ciclo de garantia;
- reparo, substituição, crédito, reembolso e troca;
- reposição do fornecedor destinada ao estoque gerando Entrada rastreável;
- rollback quando estoque, espelho ou auditoria falhar;
- ausência de `write_state()` e `sync_business_tables()` nos fluxos dedicados;
- compatibilidade SQLite e caminho PostgreSQL por adaptador simulado.

Comandos de validação da etapa:

```powershell
python -m unittest tests.test_returns_exchanges_warranties
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile server.py environment_config.py
node --check script.js
git diff --check
```

A migration v13 é aditiva e somente deve ser aplicada de forma explícita. Os
testes utilizam bancos temporários descartáveis; nenhuma migration da Etapa 12
foi executada em banco operacional ou de produção.

---

# 26. CAIXA E FINANCEIRO CONTINUOS

Cobertura automatizada da Etapa 13:

- `tests/test_cash_movement_persistence.py`;
- `tests/test_payable_payment_persistence.py`;
- `tests/test_returns_exchanges_warranties.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_readiness.py`.

Validar:

- saldo continuo e bloqueio de saida que torne o Caixa negativo;
- entradas manuais somente em Dinheiro ou Pix;
- saidas manuais em Dinheiro, Pix ou Debito, com categoria obrigatoria;
- origem, operador e saldo resultante dos movimentos;
- estorno por movimento inverso vinculado e idempotente;
- historico bancario legado preservado e novas baixas sem vinculo bloqueadas;
- baixa total, parcial e por desconto integral de Contas a Pagar;
- juros, multa e desconto informados manualmente;
- estorno de baixa e cancelamento de conta sem pagamento;
- recorrencia mensal com uma ocorrencia por serie e mes;
- restricoes de edicao depois de pagamento parcial, total ou cancelamento;
- cancelamento integral de Venda por devolucao total vinculada;
- recomposicao unica do estoque e reversao financeira por origem;
- ausencia de `write_state()` e `sync_business_tables()` nos fluxos dedicados;
- idempotencia, auditoria e rollback das operacoes criticas;
- compatibilidade SQLite e caminho PostgreSQL por adaptador simulado.

Comandos de validacao da etapa:

```powershell
python -m unittest tests.test_cash_movement_persistence tests.test_payable_payment_persistence tests.test_returns_exchanges_warranties
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile server.py environment_config.py
node --check script.js
git diff --check
```

A migration v14 e aditiva e somente deve ser aplicada de forma explicita. Os
testes utilizam bancos temporarios descartaveis; nenhuma migration da Etapa 13
foi executada em banco operacional ou de producao.

---

# 27. CONCILIACAO DE CARTOES

Cobertura automatizada da Etapa 14:

- `tests/test_card_reconciliation_business_rules.py`;
- `tests/test_card_modalities_business_rules.py`;
- `tests/test_sale_business_rules.py`;
- `tests/test_cash_movement_persistence.py`;
- `tests/test_returns_exchanges_warranties.py`;
- `tests/test_store_credit_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_readiness.py`.

Validar:

- listagem paginada, busca, modalidade, situacao, periodo e resumos;
- permissao de operador e administrador;
- conciliacao individual exata, parcial e com divergencia explicita;
- conciliacao em lote com soma exata das alocacoes;
- uma unica entrada financeira por conciliacao;
- vinculo entre agrupador, itens, recebiveis, pagamentos e Caixa;
- versao e saldo esperado contra alteracoes concorrentes;
- idempotencia de conciliacao e estorno;
- estorno integral do lote com movimento inverso e motivo;
- rollback de recebiveis, pagamentos, Caixa, espelho e auditoria;
- ausencia de `write_state()` e `sync_business_tables()` no fluxo dedicado;
- compatibilidade SQLite e caminho PostgreSQL por adaptador simulado.

Comandos de validacao da etapa:

```powershell
python -m unittest tests.test_card_reconciliation_business_rules
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile server.py environment_config.py
node --check script.js
git diff --check
```

A migration v15 e aditiva e somente deve ser aplicada de forma explicita. Os
testes utilizam bancos temporarios descartaveis; nenhuma migration da Etapa 14
foi executada em banco operacional ou de producao.

---

# 28. CATALOGO E DOCUMENTOS

Cobertura automatizada da Etapa 15:

- `tests/test_catalog_documents_business_rules.py`;
- `tests/test_versioned_migrations.py`;
- `tests/test_migration_postgresql.py`;
- `tests/test_database_readiness.py`;
- `tests/test_sale_business_rules.py`;
- `tests/test_conditional_business_rules.py`;
- `tests/test_returns_exchanges_warranties.py`.

Validar:

- Catalogo somente para usuario autenticado;
- estoque disponivel maior que zero, descontando reservas ativas;
- ausencia de custo, margem, codigo de barras e quantidade exata no Catalogo;
- busca por multiplos termos, filtros, ordenacao e detalhe;
- revalidacao da consulta na emissao do Catalogo;
- snapshots historicos de Venda, Condicional e Troca;
- etiquetas Code128 reais, limites por produto e por lote;
- numero de via e segunda via baseada no snapshot original;
- idempotencia e conflito de chave;
- isolamento por loja;
- auditoria e rollback integral;
- caminho SQLite e PostgreSQL por adaptador simulado;
- estados de carregamento, erro, vazio e sucesso no frontend.

Comandos de validacao da etapa:

```powershell
python -m unittest tests.test_catalog_documents_business_rules
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile server.py environment_config.py
node --check script.js
git diff --check
```

A migration v16 e aditiva e somente deve ser aplicada de forma explicita. Os
testes utilizam bancos temporarios descartaveis; nenhuma migration da Etapa 15
foi executada em banco operacional ou de producao.

---

# 29. RELATORIOS E EXPORTACOES

Cobertura automatizada da Etapa 16:

- `tests/test_reports_business_rules.py`;
- testes funcionais dos modulos que alimentam Vendas, Estoque, Caixa,
  Crediario, Contas a Pagar e Condicionais;
- testes de migrations, adaptadores e readiness da base acumulada.

Validar:

- catalogo dos oito relatorios oficiais;
- autenticacao obrigatoria e restricao do relatorio de Lucro ao Administrador;
- omissao de lucro e valor financeiro total do Estoque para Operador;
- periodos Hoje, 7 dias, 30 dias, Mes atual e personalizado;
- filtros especificos e paginacao no backend;
- pagamentos mistos e snapshots historicos;
- exclusao de Vendas canceladas e efeito liquido de devolucoes;
- estoque disponivel descontando Condicionais em aberto;
- compatibilidade de Contas a Pagar antigas sem pagamentos relacionais;
- exportacoes PDF e XLSX geradas no servidor;
- auditoria da exportacao de Lucro sem conteudo sensivel;
- ausencia de `write_state()` e `sync_business_tables()` nas consultas;
- estados de carregamento, erro, vazio e sucesso na interface;
- caminho SQLite e PostgreSQL por adaptador simulado.

Comandos de validacao da etapa:

```powershell
python -m unittest tests.test_reports_business_rules
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile server.py environment_config.py report_exports.py
node --check script.js
git diff --check
```

Nenhuma migration foi necessaria ou executada na Etapa 16. Os testes utilizam
bancos temporarios descartaveis e nao acessam producao.

---

# 30. ALERTAS, SCORE E DASHBOARD

Cobertura automatizada da Etapa 17:

- `tests/test_alert_score_dashboard_business_rules.py`;
- testes acumulados de migrations, Vendas, devolucoes, Crediario, Caixa,
  Contas a Pagar, Condicionais, estoque e relatorios.

Validar:

- os cinco tipos iniciais de alertas e a remocao automatica quando resolvidos;
- isolamento por usuario dos estados lido e fixado;
- busca, filtros, paginacao, sino e acoes contextuais;
- score indisponivel sem historico avaliavel;
- score com pagamentos, descontos, atrasos atuais e renegociacoes;
- exclusao de cancelamentos e Vendas totalmente devolvidas da frequencia de
  compras diretas;
- Dashboard liquido com cancelamentos, devolucoes e pagamentos mistos;
- percentuais positivos da rosca totalizando exatamente 100%;
- protecao dos valores financeiros para Operador no backend;
- periodos oficiais, vazio, erro, carregamento, sucesso e virada do dia;
- marcas historicas e estoque parado disponivel;
- caminho SQLite e PostgreSQL por adaptador simulado.

Comandos de validacao da etapa:

```powershell
python -m unittest tests.test_alert_score_dashboard_business_rules
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile server.py environment_config.py report_exports.py
node --check script.js
git diff --check
```

A migration v17 e aditiva e nao foi executada em banco operacional ou de
producao. Os testes usam bancos temporarios descartaveis e nao acessam servicos
externos.

---

# 31. CONFIGURACOES E PERMISSOES

Cobertura automatizada da Etapa 18:

- `tests/test_store_settings_permissions_business_rules.py`;
- testes acumulados de autenticacao, sessao, permissoes, bootstrap, migrations,
  Vendas e documentos.

Validar:

- criacao aditiva de `store_settings`, `user_preferences` e campos de seguranca
  em `users`;
- configuracao completa da loja com validacao, auditoria e versao otimista;
- identidade operacional minima disponivel sem sessao, sem exposicao de dados
  administrativos;
- upload de logo com validacao de versao;
- Dinheiro sempre ativo e bloqueio de novas vendas em formas desabilitadas;
- tema isolado por usuario;
- matriz de acesso e gestao de usuarios exclusivas para Administrador;
- desativacao sem exclusao fisica e protecao do ultimo Administrador ativo;
- bloqueio persistente apos cinco falhas e desbloqueio administrativo;
- snapshot da identidade nos documentos;
- contratos de autenticacao e migrations atualizados para a versao 18;
- caminhos SQLite e PostgreSQL.

Comandos de validacao da etapa:

```powershell
python -m unittest tests.test_store_settings_permissions_business_rules
python -m unittest discover -s tests -p "test_*.py"
python -m py_compile server.py environment_config.py report_exports.py
node --check script.js
git diff --check
```

A migration v18 e aditiva e nao foi executada em banco operacional ou de
producao. Os testes usam bancos temporarios descartaveis e nao acessam servicos
externos.
