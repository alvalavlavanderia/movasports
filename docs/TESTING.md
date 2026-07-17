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
- limite de crédito;
- desativação;
- alerta de inadimplência;
- ultrapassagem de limite;
- histórico;
- Score.

Clientes não devem ser excluídos definitivamente.

---

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
