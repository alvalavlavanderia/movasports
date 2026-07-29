# Matriz de Conformidade Business - Mova Sports

## 1. Identificacao

Esta matriz compara a especificacao funcional oficial com a implementacao
presente na base tecnica aprovada da Mova Sports.

- Data da analise: 2026-07-24
- Commit de codigo analisado: `e6b9ac6a10d45b06b19a92eb1d3150f903e64ef5`
- Branch de trabalho: `business/clients-stage2`
- Especificacao: `docs/BUSINESS_RULES.md`
- SHA-256 da especificacao:
  `C17F22CDEA6433DE51FA06863DA1DD4DF3E67B716F3E766E85F4F23CE6EFC7DC`
- Escopo do produto: ERP da loja de roupas esportivas Mova Sports.

Este documento iniciou como diagnostico da Etapa 1 e foi atualizado ao concluir
as Etapas 2 - Clientes, 3 - Fornecedores e Cadastros Auxiliares, 4 - Produtos
e Entradas - nucleo, 5 - Entradas e financeiro de compras, 6 - Estoque
transacional, 7 - Inventario e as entregas seguintes ate a Etapa 18 -
Configuracoes e Permissoes. As migrations
criadas sao aditivas; nenhuma migration foi executada em banco real nestas
etapas.

## 2. Legenda

| Status | Significado |
| --- | --- |
| Conforme | A regra principal esta implementada e possui evidencia direta no codigo. |
| Parcial | Existe fluxo funcional, mas faltam regras, estados ou integracoes. |
| Divergente | O comportamento atual contraria uma regra oficial. |
| Ausente | Nao existe entidade, persistencia ou fluxo correspondente. |
| Documental | Regra de governanca ou orientacao, sem funcionalidade isolada. |
| Revalidar | Trecho historico da documentacao que precisa ser confrontado novamente apos as implementacoes. |

Uma classificacao "Conforme" nesta matriz nao encerra o modulo. A conclusao de
uma Sprint exige testes funcionais, de autorizacao, concorrencia, idempotencia
e rollback aplicaveis ao fluxo.

## 3. Evidencias Estruturais

### 3.1 Persistencia existente

O schema versionado atual contem:

- lojas e estado JSON de compatibilidade;
- usuarios e auditoria;
- marcas, categorias, tamanhos, cores, categorias de despesa, fornecedores,
  clientes e produtos;
- historicos cadastrais de clientes e fornecedores;
- entradas de mercadorias, itens de entrada, sequencias por loja e movimentos
  de estoque originados por Entrada;
- vinculos financeiros e cancelamentos de Entrada;
- devolucoes ao fornecedor, alocacoes financeiras e creditos de fornecedor;
- livro transacional unificado de estoque, com saldos real, reservado e
  disponivel por movimento;
- inventarios, itens contados, eventos de contagem e sequencias por loja;
- vendas, itens de venda e pagamentos;
- movimentos e fechamentos de caixa;
- recebiveis e pagamentos de recebiveis;
- documentos gerados com snapshot, origem, formato, via e idempotencia;
- devolucoes de venda e respectivos itens;
- contas a pagar.

Nao existem tabelas especificas para:

- condicionais;
- garantias;
- configuracoes e vigencias de cartao;
- conciliacoes bancarias;
- alertas persistidos;
- score de cliente;
- configuracoes operacionais da loja.

Fonte: `database_migrations/schema.py`.

### 3.2 APIs existentes

Existem APIs para:

- autenticacao, sessao, usuarios e senha;
- produtos, clientes, fornecedores, marcas, categorias, tamanhos, cores e
  categorias de despesa;
- vendas, cancelamentos, devolucoes e condicionais;
- caixa, fechamentos, recebimentos de cartao e recebiveis;
- contas a pagar;
- Dashboard e relatorios;
- upload, auditoria, backup, exportacao, importacao e reset.

Fonte: rotas Flask em `server.py`.

### 3.3 Frontend existente

Existem telas para:

- Dashboard;
- produtos, clientes, fornecedores, marcas, categorias, tamanhos, cores,
  categorias de despesa e usuarios;
- estoque e catalogo;
- nova venda, condicional, devolucao, historico e cancelamento;
- crediario;
- contas a pagar;
- caixa e fechamento;
- configuracoes e auditoria.

As telas de Catalogo, Cartoes e Relatorios possuem acesso pela navegacao
principal. O catalogo de Relatorios e filtrado no backend conforme o perfil.

Fonte: `index.html` e `script.js`.

### 3.4 Cobertura automatizada existente

A cobertura versionada e forte para:

- configuracao de ambientes;
- protecao de importacao e reset;
- armazenamento de credenciais;
- autenticacao e sessao sem inicializacao estrutural;
- readiness;
- migrations e bootstrap administrativo;
- persistencia direcionada de movimentos e fechamentos de caixa;
- criacao, edicao e pagamento de contas a pagar.
- regras cadastrais, historicos e integracoes essenciais de clientes;
- fornecedores, cadastros auxiliares e seus vinculos atuais com produtos e
  contas a pagar.
- Produtos e Entradas, incluindo idempotencia, snapshots, movimento de estoque,
  rollback e compatibilidade entre SQLite e PostgreSQL.
- financeiro de compras, incluindo contas vinculadas, cancelamento de Entrada,
  devolucao ao fornecedor, abatimentos, creditos e reembolsos.
- estoque transacional, incluindo Entrada, cancelamento de Entrada, devolucao
  ao fornecedor, cancelamento de devolucao, venda, cancelamento de venda,
  devolucao de cliente e reserva/liberacao de Condicional.
- inventario fisico, incluindo abertura geral e parcial, contagem por item e
  codigo de barras, concorrencia, divergencia, ajuste, auditoria e rollback.
- relatorios oficiais, filtros, paginacao, perfis, valores liquidos e
  exportacoes PDF/XLSX no servidor.

A cobertura e insuficiente ou inexistente para:

- vendas;
- cancelamentos e devolucoes;
- crediario;
- condicionais;
- catalogo;
- cartoes e conciliacao;
- alertas, score e garantias.

Fonte: arquivos versionados em `tests/`.

## 4. Matriz Geral por Capitulo

| Capitulo | Modulo | Status atual | Evidencia ou divergencia principal | Proxima acao |
| --- | --- | --- | --- | --- |
| 1 | Clientes | Conforme no escopo da Etapa 2 | Cadastro validado, CPF opcional e unico, estados auditados, historico de limite, cliente padrao, ficha consolidada e desativacao sem exclusao fisica. Score permanece fora do escopo. | Manutencao e integracoes das etapas dependentes |
| 2 | Produtos e Entradas | Conforme no escopo das Etapas 4, 5, 6 e 7 | Primeira e novas Entradas sao atomicas e rastreaveis; contas vinculadas, cancelamento, devolucao, credito de fornecedor e inventario possuem efeitos proprios no estoque transacional. | Manutencao |
| 3 | Estoque | Conforme no escopo das Etapas 6 e 7 | As origens operacionais atuais e os ajustes de inventario alimentam `inventory_movements`, com saldos real, reservado e disponivel, snapshots, origem, usuario e data. | Manutencao e integracoes futuras |
| 4 | Vendas | Conforme no escopo das Etapas 9, 12 e 13 | Venda atomica, snapshots, pagamentos mistos, baixa de estoque, devolucao liquida, troca formal e cancelamento integral possuem persistencia transacional e idempotente. | Manutencao e relatorios futuros |
| 5 | Crediario | Concluido no escopo da Etapa 10 | Limite, ate tres parcelas, recebimentos parciais, ajustes manuais, cartao, historico e renegociacao possuem persistencia transacional. | Evolucoes dependem das etapas de devolucoes, relatorios e alertas |
| 6 | Caixa e Financeiro | Conforme no escopo das Etapas 13 e 14 | Caixa continuo, saldo nao negativo, movimentos manuais, conciliacao vinculada de cartoes, estornos, contas a pagar, recorrencias e cancelamento integral de Venda possuem rastreabilidade e persistencia direcionada. | Manutencao e relatorios futuros |
| 7 | Usuarios e Permissoes | Parcial | Existem `admin` e `operator`; nao ha matriz granular por modulo e acao. | Sprint Business 18 |
| 8 | Catalogo | Conforme no escopo da Etapa 15 | Catalogo autoritativo exibe somente estoque disponivel, desconta reservas ativas, protege custo e quantidade exata, possui filtros, ordenacao, detalhe e emissao rastreavel. | Manutencao e relatorios futuros |
| 9 | Relatorios | Concluido no escopo da Etapa 16 | Os oito relatorios oficiais usam fontes relacionais, filtros autoritativos, paginacao e exportacao PDF/XLSX no servidor. | Manutencao e indicadores da Etapa 17 |
| 10 | Condicional | Concluido no escopo da Etapa 11 | Saida, reserva, prazo, retornos parciais, estados, historico e conversao vinculada em Venda possuem persistencia relacional e transacional. | Evolucoes dependem das etapas de relatorios e alertas |
| 11 | Regras gerais | Parcial | Algumas regras transversais existem, mas nao sao aplicadas uniformemente. | Aplicar em todas as Sprints |
| 12 | Regras futuras | Documental | Nao representa entrega imediata. | Manter fora do escopo ate decisao formal |
| 13 | Regras comprovadas pelo codigo | Revalidar | E um retrato historico; parte ficou desatualizada apos as Sprints de infraestrutura. | Atualizar apos cada modulo |
| 14 | Divergencias encontradas | Revalidar | Lista historica, nao substitui esta matriz. | Conciliar com esta matriz |
| 15 | Regras a confirmar | Revalidar | Decisoes ainda nao aprovadas nao podem ser implementadas. | Criar bloqueios explicitos por Sprint |
| 16 | Regras implicitas | Revalidar | Comportamentos espalhados devem virar regras ou ser removidos com aprovacao. | Tratar no modulo correspondente |
| 17 | Trocas | Concluido no escopo da Etapa 12 | Produto devolvido e substituto, diferenca financeira, estoque, venda vinculada, cancelamento formal e auditoria possuem persistencia transacional. | Relatorios consolidados pertencem a Etapa 16 |
| 18 | Configuracoes | Concluido no escopo da Etapa 18 | Configuracoes da loja versionadas, preferencias visuais por usuario, meios de pagamento operacionais e matriz fixa de acessos protegida no backend. | Evolucoes exigem nova regra oficial |
| 19 | Alertas do Sistema | Concluido no escopo da Etapa 17 | Cinco alertas operacionais oficiais, leitura, fixacao, busca, filtros, paginacao e estado isolado por usuario. | Evolucoes de tipos exigem nova regra oficial |
| 20 | Score do Cliente | Concluido no escopo da Etapa 17 | Score informativo de 0 a 100 calculado no backend com crediario, atrasos, renegociacoes, saldo vencido e compras diretas dos ultimos 12 meses. | Sem decisao automatica de credito |
| 21 | Fornecedores e Cadastros Auxiliares | Conforme no escopo das Etapas 3, 5 e 12 | Fornecedor completo, documento opcional e unico, status auditado e ficha com contas, Entradas, devolucoes, creditos e vinculo de garantia. Reposicao de garantia destinada ao estoque gera Entrada rastreavel. | Manutencao e relatorios futuros |
| 22 | Backup, Importacao e Reset | Parcial / Conforme no nucleo | Existem fluxos protegidos por ambiente e perfil. A estrategia de backup PostgreSQL continua externa. | Manutencao transversal |
| 23 | Impressoes e Documentos | Conforme no escopo da Etapa 15 | Comprovantes de Venda, Condicionais, Trocas, Catalogos e Etiquetas possuem snapshot imutavel, origem, formato, via, usuario, data, idempotencia e historico. | Novos tipos dependem da regra do modulo de origem |
| 24 | Garantias | Concluido no nucleo da Etapa 12 | Garantia vinculada a venda, cliente, item, fornecedor, fotos, eventos, estados, reparo, substituicao, credito, reembolso e troca possuem historico persistente. | Alertas e relatorios consolidados permanecem nas etapas correspondentes |
| 25 | Inventario | Conforme no escopo da Etapa 7 | Abertura geral ou parcial, snapshot, contagem, divergencia, aprovacao administrativa, ajuste, cancelamento, historico e auditoria possuem persistencia propria. | Relatorios e documentos pertencem a Etapa 16 |
| 26 | Login, Sessoes e Seguranca de Acesso | Conforme no nucleo / Parcial | Login backend, hash, sessao e rate limit existem; faltam perfis granulares e politicas futuras. | Manutencao transversal |
| 27 | Auditoria e Historico | Parcial | Ha `audit_logs`, mas a cobertura nao e uniforme e alguns detalhes incluem objetos extensos. | Aplicar em todas as Sprints |
| 28 | Configuracoes da Loja | Concluido no escopo da Etapa 18 | Dados cadastrais, identidade visual, documentos, Pix informativo e formas de pagamento possuem persistencia relacional, auditoria e concorrencia otimista. | Evolucao futura para multiplas lojas |
| 29 | Relatorios e Exportacoes | Concluido no escopo da Etapa 16 | Vendas, produtos vendidos, Caixa, Crediario, Contas a Pagar, Estoque, Condicionais e Lucro possuem filtros, paginacao, perfis e exportacao PDF/XLSX. | Manutencao e otimizacao para volumes excepcionais |
| 30 | Conciliacao de Cartoes | Concluido no escopo da Etapa 14 | Recebiveis sao conciliados individualmente ou em lote por vinculo explicito, com valor efetivo, divergencia, uma entrada financeira, historico e estorno integral. | Manutencao e relatorios da Etapa 16 |
| 31 | Notificacoes e Central de Alertas | Concluido no escopo da Etapa 17 | Central operacional derivada do estado atual, com sino, contagem, prioridades, acoes contextuais e preferencias persistentes por usuario. | Sem notificacao externa nesta etapa |
| 32 | Dashboard | Concluido no escopo da Etapa 17 | Fontes relacionais, periodos oficiais, valores liquidos, pagamentos mistos, perfis protegidos, virada do dia e estados visuais completos. | Evolucoes de indicadores exigem nova regra oficial |
| 33 | Impressoes e Documentos Gerados | Conforme no escopo da Etapa 15 | Emissoes e segundas vias sao persistidas sem recalcular snapshots historicos; a impressao utiliza o navegador e nao altera efeitos operacionais ou financeiros. | Manutencao |
| 34 | Logs Tecnicos | Parcial | Logs Flask existem; faltam correlacao, classificacao e monitoramento estruturado. | Trilha tecnica posterior |
| 35 | Seguranca Consolidada | Parcial | A infraestrutura melhorou, mas autorizacao granular e protecao de dados por modulo ainda faltam. | Criterio transversal |
| 36 | Performance e Escalabilidade | Parcial / Divergente | Backend e frontend sao monoliticos; `app_state` ainda acopla fluxos e algumas listas nao paginam. | Evolucao incremental por modulo |
| 37 | APIs e Integracoes Futuras | Ausente / Parcial | Existem APIs internas, mas nao ha versao publica, webhooks ou contratos externos. | Fora do primeiro ciclo Business |
| 38 | Migrations e Versionamento | Conforme no framework | Framework versionado e CLI existem; cada nova estrutura ainda exigira migration aditiva propria. | Usar em todas as mudancas de schema |
| 39 | Glossario | Documental | Deve orientar nomes de dominio. | Validar nomes em toda Sprint |
| 40 | Convencoes Gerais | Documental / Parcial | Parte esta refletida no codigo; precisa ser usada como checklist. | Criterio transversal |
| 41 | Regras de Desenvolvimento | Documental | Define processo, nao modulo funcional. | Criterio transversal |
| 42 | Criterios de Aceite e Qualidade | Documental | Deve compor a Definition of Done. | Obrigatorio em toda Sprint |
| 43 | Encerramento Oficial | Documental | Confirma autoridade do documento. | Sem implementacao isolada |
| Retificacao 001 | Cartoes de Credito | Divergente / Ausente | Nao existem modalidades 1x a 10x, taxas e vigencias configuraveis, snapshot financeiro ou relatorios correspondentes. | Sprint Business 8 antes de Vendas |

## 5. Matriz Detalhada dos Modulos Operacionais

### 5.1 Clientes

| Grupo de regras | Status | Implementacao atual | Gap oficial |
| --- | --- | --- | --- |
| Nome obrigatorio | Conforme | Normalizado e validado no backend. | Sem gap no escopo. |
| CPF | Conforme | Opcional, normalizado, validado matematicamente e unico inclusive entre desativados. | Sem gap no escopo. |
| Telefone, nascimento, endereco e e-mail | Conforme | Telefone obrigatorio; campos opcionais e formatos validados no backend. | Clientes legados incompletos sao preservados e devem ser completados ao editar. |
| Observacoes | Conforme | Campo persistido na tabela e no espelho de compatibilidade. | Permissao granular futura permanece fora do escopo. |
| Cliente padrao | Conforme | Registro protegido, sem CPF, usado em venda simples e impedido em crediario e condicional. | Sem gap no escopo. |
| Ativo, bloqueado e desativado | Conforme | Transicoes registram motivo, usuario e data; desativado sai da busca operacional. | Sem gap no escopo. |
| Exclusao | Conforme | API rejeita exclusao fisica e orienta desativacao. | Sem gap no escopo. |
| Limite e credito disponivel | Conforme no cadastro | Limite positivo e historico de alteracoes; ficha calcula saldo e credito disponivel. | Autorizacao de excesso pertence ao fluxo futuro de Vendas/Crediario. |
| Resumo e ficha do cliente | Conforme | Consolida compras, pagamentos, recebiveis, condicionais e historicos. | Score permanece fora do escopo. |
| Duplicidade por nome/telefone | Conforme | Alertas nao bloqueantes exigem confirmacao explicita; CPF continua autoritativo. | Sem gap no escopo. |
| Score | Ausente | Nao existe. | Implementar somente apos dados financeiros confiaveis. |
| Rastreabilidade | Conforme no escopo | Auditoria e tabelas dedicadas preservam status e limite com usuario e data. | Auditoria granular de campos sensiveis pode evoluir com permissoes. |

### 5.2 Fornecedores e Cadastros Auxiliares

| Grupo de regras | Status | Implementacao atual | Gap oficial |
| --- | --- | --- | --- |
| Fornecedor | Conforme no escopo | Cadastro completo, CPF/CNPJ opcional e unico, busca, indicadores, ficha, Entradas, devolucoes, creditos, status reversivel e historico auditado. | Garantias pertencem a etapa futura. |
| Marca e categoria | Conforme no escopo | IDs estaveis, nome normalizado e unico, edicao e desativacao sem exclusao fisica. | Entrada futura devera preservar o snapshot historico aplicavel. |
| Cor e tamanho | Conforme no escopo | Entidades auxiliares por loja, com ID, nome unico e estado ativo/desativado. | Variacoes e estoque por lote pertencem a Produtos/Entradas. |
| Categoria de despesa | Conforme no escopo | Cadastro por ID, estado ativo/desativado e 15 categorias padrao sem duplicidade. | Relatorios financeiros completos pertencem a etapas posteriores. |
| Vinculo produto-fornecedor | Conforme como cadastro atual | Produto pode referenciar fornecedor ativo por ID e preserva os demais auxiliares por ID. | O fornecedor historico da aquisicao deve pertencer a Entrada na Etapa 4. |
| Vinculo de Conta a Pagar | Conforme | Uma Entrada pode originar uma ou varias contas, preservando fornecedor, categoria e IDs de origem. | Relatorios consolidados pertencem a etapas posteriores. |
| Creditos do fornecedor | Conforme | Credito nasce de devolucao, fica vinculado ao fornecedor e e consumido por FIFO sem movimentar Caixa. | Conciliacao e relatorios consolidados pertencem a etapas posteriores. |

### 5.3 Produtos, Entradas, Estoque e Inventario

| Grupo de regras | Status | Implementacao atual | Gap oficial |
| --- | --- | --- | --- |
| Codigo unico | Conforme no banco | Barcode obrigatorio e indice unico. | Manter em todas as entradas e leituras. |
| Cadastro do produto | Conforme no nucleo | Codigo consultado antes da operacao, dados atuais editaveis sem alterar estoque e novo produto criado somente com a primeira Entrada. | Variacoes ou lotes futuros devem preservar este contrato. |
| Primeira e novas Entradas | Conforme | Documento, item, saldo, movimento, contas vinculadas, espelho de compatibilidade e auditoria possuem persistencia rastreavel. | Sem gap no escopo. |
| Estoque real/reservado/disponivel | Conforme no escopo das Etapas 6 e 7 | Real persiste no produto, reserva deriva das Condicionais abertas e cada evento guarda saldos anterior e posterior, incluindo disponibilidade. | Manter a mesma fonte nas integracoes futuras. |
| Movimento de estoque | Conforme no escopo da Etapa 6 | Entrada, reversoes de compra, venda, cancelamento, devolucao e Condicional alimentam `inventory_movements` com snapshot de produto, origem, usuario e data. | Novas origens futuras devem usar o mesmo ledger. |
| Custo historico | Conforme | Item da Entrada guarda custo unitario e total; a Entrada mais recente atualiza o custo atual e devolucoes usam o custo historico. | Sem media ponderada ou rateio automatico. |
| Idempotencia e concorrencia | Conforme no nucleo | Chave por loja, hash do payload, transacao unica, bloqueio SQLite e locks PostgreSQL evitam duplicidade. | Revalidar em cargas e integracoes futuras. |
| Conta a pagar da Entrada | Conforme | Vinculo persistente aceita uma ou varias obrigacoes e total diferente do documento. | Relatorios consolidados pertencem a etapas posteriores. |
| Cancelamento de Entrada | Conforme | Cancelamento integral e idempotente reverte estoque uma vez, cancela contas pendentes e bloqueia efeitos financeiros existentes. | Nao existe cancelamento parcial por regra oficial. |
| Devolucao ao fornecedor | Conforme | Devolucao parcial ou total movimenta estoque, preserva custo, motivo, financeiro, fornecedor e auditoria. | Garantia de fornecedor foi integrada na Etapa 12. |
| Inventario | Conforme no escopo da Etapa 7 | Inventario geral ou parcial preserva snapshot de abertura, aceita contagem explicita inclusive zero, compara com o disponivel atual e gera ajuste auditado no ledger. | Relatorios e documentos ficam para a Etapa 16. |

### 5.4 Vendas, Condicionais, Trocas e Garantias

| Grupo de regras | Status | Implementacao atual | Gap oficial |
| --- | --- | --- | --- |
| Criacao de venda | Conforme no escopo da Etapa 9 | Itens, desconto, pagamentos, efeitos financeiros e estoque sao persistidos em transacao direcionada, idempotente e concorrente. | Manutencao. |
| Pagamento misto | Conforme | Cada componente e persistido pela forma oficial e devolucoes sao alocadas proporcionalmente quando nao ha escolha manual. | Manutencao. |
| Snapshot do item | Conforme | Produto, variacao, marca, custo e valores comerciais sao preservados no item historico. | Manutencao. |
| Cartoes | Conforme no fluxo das Etapas 8, 9 e 14 | Modalidade e condicoes financeiras sao preservadas; recebiveis carregam taxa, prazo e valor liquido e possuem conciliacao vinculada. | Integracoes automaticas com operadoras permanecem futuras. |
| Cancelamento | Conforme no escopo da Etapa 13 | O cancelamento integral usa uma devolucao total vinculada, recompoe estoque uma vez e reverte separadamente cada componente recebido ou pendente. | Registros antigos sem vinculo seguro permanecem sujeitos a conciliacao manual. |
| Devolucao | Conforme no escopo da Etapa 12 | Devolucao parcial ou total usa valor liquido e custo historico, recompoe estoque uma vez, aloca pagamentos mistos e reduz recebiveis pendentes antes de devolver valores pagos. | Registros legados sem vinculo seguro exigem conciliacao manual. |
| Condicional | Conforme no escopo da Etapa 11 | Reserva persistente, prazo, retornos por quantidade, historico e conversao atomica em Venda. | Relatorio consolidado e alertas ficam nas etapas correspondentes. |
| Troca | Conforme no escopo da Etapa 12 | Produto devolvido, produto substituto, diferenca a pagar ou devolver, venda vinculada e cancelamento formal sao transacionais e idempotentes. | Relatorios consolidados pertencem a Etapa 16. |
| Garantia | Conforme no nucleo da Etapa 12 | Abertura, fotos, analise, fornecedor, eventos, reparo, substituicao, credito, reembolso, troca e reposicao em estoque possuem rastreabilidade. | Alertas de prazo e relatorios pertencem as Etapas 16 e 17. |

### 5.5 Crediario

| Grupo de regras | Status | Implementacao atual | Gap oficial |
| --- | --- | --- | --- |
| Cliente obrigatorio | Conforme | Venda em crediario exige cliente. | Manter validacao autoritativa. |
| Cliente bloqueado | Conforme no fluxo de venda | Backend impede crediario. | Adicionar motivo e historico do bloqueio. |
| Limite | Parcial | Operador e bloqueado; administrador ultrapassa. | Autorizacao formal e historico da decisao. |
| Maximo de tres parcelas | Divergente | Backend aceita qualquer inteiro positivo. | Impor limite oficial. |
| Vencimentos | Parcial | Parcelas em intervalos de 30 dias. | Datas civis, ajustes e regras completas. |
| Pagamento parcial | Parcial | Aceita valor menor que o saldo. | Transacao direcionada e concorrencia segura. |
| Desconto, juros e multa | Ausente na base aprovada | Recebimento considera apenas valor. | Aplicar regras aprovadas, rateio e auditoria. |
| Antecipacao | Parcial | Qualquer parcela pode ser selecionada. | Regras e apresentacao explicitas. |
| Renegociacao | Ausente | Nao existe. | Aguardar regras marcadas para confirmacao. |
| Integracao financeira | Conforme no escopo atual | Dinheiro/Pix entram no Caixa; cartao cria recebivel e a conciliacao gera uma unica entrada vinculada. | Relatorios consolidados pertencem a Etapa 16. |

### 5.6 Caixa, Contas e Cartoes

| Grupo de regras | Status | Implementacao atual | Gap oficial |
| --- | --- | --- | --- |
| Movimento manual | Conforme no fluxo basico | Entrada/saida, tipo, forma, valor e auditoria. | Permissoes e categorias configuraveis. |
| Fechamento | Conforme no fluxo basico | Persiste esperado, informado e diferenca. | Regras completas de reabertura e aprovacao. |
| Contas a pagar | Parcial | CRUD e pagamento parcial com taxa/desconto. | Vinculos de origem, cancelamentos e creditos de fornecedor. |
| Recebiveis | Conforme no escopo atual | Cartao e Crediario compartilham estrutura, preservando estados, modalidade, taxa, prazo, saldo e historico. | Relatorios consolidados pertencem a Etapa 16. |
| Conciliacao | Conforme no escopo da Etapa 14 | Baixa individual ou em lote usa vinculos explicitos, divergencia formal e uma entrada financeira por operacao. | Integracao automatica com adquirentes permanece futura. |
| Estornos | Conforme nos fluxos consolidados | Movimentos, pagamentos e conciliacoes possuem reversao vinculada e idempotente sem apagar o historico. | Manutencao por nova origem financeira. |

## 6. Divergencias Bloqueantes

As seguintes divergencias devem ser resolvidas antes de considerar os respectivos
modulos aptos para operacao conforme a especificacao:

1. Nao existe matriz granular de permissoes.
2. Alertas e configuracoes transversais ainda nao cobrem todos os fluxos
   Business concluidos.

## 7. Dependencias Oficiais de Implementacao

Fluxo estrutural:

`Clientes + Fornecedores + Cadastros Auxiliares`

`-> Produtos e Entradas`

`-> Movimentos de Estoque`

`-> Inventario`

`-> Configuracoes de Cartao`

`-> Vendas + Crediario + Condicionais`

`-> Cancelamentos + Devolucoes + Trocas + Garantias`

`-> Caixa + Contas + Conciliacao`

`-> Catalogo + Documentos + Relatorios`

`-> Alertas + Score + Dashboard`

Regras transversais obrigatorias em cada etapa:

- autorizacao no backend;
- auditoria;
- timezone operacional;
- transacao unica;
- idempotencia quando aplicavel;
- concorrencia;
- isolamento por loja;
- migracao aditiva;
- rollback;
- estados de interface;
- testes automatizados;
- atualizacao desta matriz.

## 8. Roteiro Aprovavel de Sprints Business

| Ordem | Sprint | Resultado esperado | Dependencias |
| --- | --- | --- | --- |
| 1 | Matriz de conformidade | Documento atual, priorizado e rastreavel. | Base tecnica aprovada |
| 2 | Clientes | Concluida: cadastro e ficha conformes, sem exclusao historica indevida. | Sprint 1 |
| 3 | Fornecedores e auxiliares | Cadastros estruturantes e preservacao historica. | Sprint 1 |
| 4 | Produtos e Entradas - nucleo | Concluida: Entrada, itens, custo, saldo e movimento de estoque atomicos e idempotentes. | Sprints 2 e 3 |
| 5 | Entradas e financeiro de compras | Concluida: contas vinculadas, cancelamento, devolucao e creditos. | Sprint 4 |
| 6 | Estoque transacional | Concluida: saldos real, reservado e disponivel rastreados em ledger unificado. | Sprint 4 |
| 7 | Inventario | Concluida: contagem, divergencia, aprovacao e ajuste auditado. | Sprint 6 |
| 8 | Modalidades de cartao | Concluida: Debito e credito 1x a 10x com taxas, prazos, vigencias e historico. | Sprint 1 |
| 9 | Vendas | Concluida: fluxo atomico com snapshots e pagamentos oficiais. | Sprints 2, 6 e 8 |
| 10 | Crediario | Concluida: limite, parcelas, recebimentos, ajustes manuais e historico. | Sprints 2 e 9 |
| 11 | Condicionais | Concluida: reserva persistente, retornos parciais e conversao segura em venda. | Sprints 2, 6 e 9 |
| 12 | Trocas, devolucoes e garantias | Concluida: fluxos fisicos, financeiros, cancelamento de troca e garantia rastreavel. | Sprints 5, 9, 10 e 11 |
| 13 | Caixa e financeiro | Ledger por origem, contas e reversoes. | Sprints 5, 9 e 10 |
| 14 | Conciliacao de cartoes | Concluida: baixa bancaria vinculada, lote, divergencias, historico e estorno formal. | Sprints 8, 9 e 13 |
| 15 | Catalogo e documentos | Concluida: catalogo protegido, etiquetas Code128, comprovantes e documentos rastreaveis. | Sprints 4, 6 e 9 |
| 16 | Relatorios e exportacoes | Concluida: oito relatorios oficiais, filtros, paginacao, perfis e exportacoes PDF/XLSX no servidor. | Sprints 5 a 15 |
| 17 | Alertas, score e Dashboard | Indicadores derivados das fontes consolidadas. | Sprints 2 a 16 |
| 18 | Configuracoes e permissoes | Configuracoes da loja e matriz de acessos. | Padroes consolidados |

## 9. Conclusao da Etapa 2 - Clientes

### 9.1 Objetivo

Adequar o modulo Clientes ao capitulo 1 do `BUSINESS_RULES.md`, sem iniciar
Configuracoes e permissoes foram concluidas na Etapa 18 com matriz fixa para
Administrador e Operador, sem perfis personalizados.

### 9.2 Entregas concluidas

1. Validar e normalizar os dados cadastrais no backend.
2. Adicionar observacoes com controle de acesso adequado.
3. Formalizar os estados ativo, bloqueado e desativado.
4. Registrar motivo, usuario e data das mudancas de estado.
5. Substituir exclusao normal por desativacao.
6. Preservar compatibilidade com clientes existentes.
7. Implementar alertas de possivel duplicidade por nome e telefone.
8. Manter CPF como bloqueio autoritativo de duplicidade.
9. Registrar historico de alteracao do limite de credito.
10. Consolidar a ficha do cliente usando os dados existentes.
11. Preparar contratos de API para compras, crediario e condicionais.
12. Criar testes de validacao, autorizacao, historico e compatibilidade.

### 9.3 Fora do escopo inicial da Etapa 2

- Score do Cliente;
- central de alertas;
- renegociacao de crediario;
- alteracao das regras de vendas;
- reescrita de historicos existentes;
- exclusao ou limpeza de dados;
- refatoracao ampla de `app_state`.

### 9.4 Decisoes aplicadas

1. Administrador e operador podem bloquear, desbloquear e desativar clientes.
2. CPF invalido bloqueia o cadastro; CPF continua opcional.
3. Administrador e operador podem editar os campos cadastrais previstos.
4. Historicos de status e limite ficam disponiveis aos perfis autenticados que
   ja possuem acesso ao modulo.
5. Clientes antigos incompletos sao preservados sem dados inventados; uma
   edicao exige o preenchimento dos campos obrigatorios atuais.

### 9.5 Estrutura e compatibilidade

- migration `v002_customer_business_rules` adiciona campos e historicos sem
  apagar registros;
- migration v1 permanece congelada com o checksum historico;
- SQLite e PostgreSQL possuem SQL e validacao de schema correspondentes;
- o cliente padrao e criado por migration/bootstrap e protegido contra edicao,
  desativacao e exclusao;
- o sincronizador legado SQLite reconhece schema v1 sem executar migration
  automaticamente;
- nenhuma migration foi executada em banco local operacional ou de producao.

## 10. Conclusao da Etapa 3 - Fornecedores e Cadastros Auxiliares

### 10.1 Objetivo

Estruturar os cadastros que sustentam Produtos, Entradas e Contas a Pagar sem
antecipar os fluxos transacionais das etapas seguintes.

### 10.2 Entregas concluidas

1. Ampliar o cadastro de fornecedor com dados fiscais, contatos, endereco,
   observacoes e nome fantasia.
2. Validar CPF/CNPJ opcional no backend e impedir documento duplicado por loja.
3. Implementar busca, indicadores, ficha e historico de situacao do fornecedor.
4. Substituir exclusao normal de fornecedor por desativacao reversivel.
5. Exigir confirmacao ao desativar fornecedor com conta em aberto.
6. Estruturar marca, categoria, tamanho, cor e categoria de despesa com IDs
   estaveis, nomes normalizados e situacao ativa/desativada.
7. Criar as categorias de despesa padrao de forma idempotente.
8. Vincular Produtos aos cadastros auxiliares e ao fornecedor por ID.
9. Vincular novas Contas a Pagar a fornecedor e categoria de despesa ativos
   por ID.
10. Vincular novas saidas manuais do Caixa a categoria de despesa ativa por ID.
11. Preservar o texto historico da marca já gravado nos itens de venda.
12. Registrar auditoria e manter o espelho necessario no `app_state`.
13. Disponibilizar os fluxos correspondentes na interface web, incluindo
    cadastros rapidos nos fluxos de Produto e Conta a Pagar.
14. Cobrir SQLite, PostgreSQL, migration, bootstrap, validacoes e integracoes
    essenciais com testes automatizados.

### 10.3 Estrutura e compatibilidade

- migration `v003_supplier_auxiliary_catalogs` e aditiva e preserva registros;
- migrations v1 e v2 permanecem congeladas;
- registros antigos so recebem vinculo por ID quando existe correspondencia
  textual exata e confiavel;
- dados historicos sem correspondencia segura permanecem preservados, sem
  associacao inventada;
- SQLite e PostgreSQL possuem schema, indices e validacoes correspondentes;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 10.4 Limites deliberados

Permanecem fora da Etapa 3:

- Entrada de mercadoria e seus itens;
- custo e fornecedor historicos por Entrada;
- devolucao ao fornecedor;
- credito com fornecedor;
- garantia de fornecedor;
- estoque por movimentos e inventario.

Esses itens nao foram simulados por campos ou registros artificiais. Eles
continuam no roteiro oficial das etapas dependentes.

## 11. Conclusao da Etapa 4 - Produtos e Entradas - nucleo

### 11.1 Objetivo

Substituir a criacao de produto com estoque editavel por uma operacao de
Entrada rastreavel, atomica e idempotente, sem antecipar o financeiro de
compras da Etapa 5.

### 11.2 Entregas concluidas

1. Consultar o codigo normalizado antes de decidir entre produto novo e
   existente, sem persistir durante a consulta.
2. Exigir que produto novo seja criado junto da primeira Entrada.
3. Somar novas Entradas ao estoque real mais recente sob bloqueio transacional.
4. Impedir alteracao direta de estoque na edicao cadastral do produto.
5. Exigir quantidade inteira positiva, custo positivo, preco de venda positivo,
   fornecedor ativo, marca ativa e categoria ativa.
6. Preservar snapshots de produto, fornecedor, custo, preco e saldos no item da
   Entrada.
7. Atualizar o custo atual pela Entrada mais recente, sem media ponderada.
8. Gerar numero sequencial por loja, movimento de estoque e auditoria.
9. Gravar produto, Entrada, item, movimento, espelho JSON e auditoria na mesma
   transacao.
10. Implementar idempotencia por loja e chave, com rejeicao de reutilizacao da
    chave para payload diferente.
11. Calcular estoque reservado pelas Condicionais abertas e apresentar estoque
    real, reservado e disponivel.
12. Preservar produto inativo como cadastro existente e exigir reativacao
    explicita antes da Entrada.
13. Disponibilizar historico de Entradas na API e na interface.
14. Cobrir SQLite e o caminho PostgreSQL por adaptador simulado, incluindo
    locks, rollback, autorizacao e contratos HTTP.

### 11.3 Estrutura e compatibilidade

- migration `v004_product_stock_entries` adiciona campos e tabelas sem apagar
  registros;
- migrations v1, v2 e v3 permanecem congeladas;
- dados anteriores nao recebem datas, custos ou documentos artificiais;
- o indice de codigo normalizado reforca unicidade por loja;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 11.4 Limites deliberados

Permanecem fora da Etapa 4:

- geracao de Contas a Pagar a partir da Entrada;
- frete e rateios financeiros;
- cancelamento de Entrada;
- devolucao ao fornecedor;
- credito com fornecedor;
- consolidacao de todas as origens em um livro unico de estoque;
- inventario.

Geracao de contas, cancelamento e devolucao/credito foram concluidos na Etapa
5. Frete permanece separado e sem rateio automatico. Estoque transacional foi
concluido na Etapa 6 e Inventario pertence a Etapa 7.

## 12. Conclusao da Etapa 5 - Entradas e financeiro de compras

### 12.1 Objetivo

Completar os efeitos financeiros e reversoes do documento de Entrada, mantendo
estoque, Contas a Pagar e fornecedor rastreaveis sem reconstruir historico.

### 12.2 Entregas concluidas

1. Vincular uma ou varias Contas a Pagar a uma Entrada confirmada.
2. Preservar fornecedor, categoria Mercadorias e identificadores de origem.
3. Permitir diferenca documentada entre total da Entrada e total financeiro.
4. Cancelar integralmente uma Entrada, recompondo o saldo apenas uma vez.
5. Cancelar contas vinculadas ainda pendentes e bloquear cancelamento quando
   houver pagamento, abatimento, credito utilizado ou estoque indisponivel.
6. Registrar devolucao parcial ou total ao fornecedor pelo custo historico.
7. Limitar a devolucao pela quantidade original, devolucoes anteriores, estoque
   real e reservas ativas.
8. Tratar o valor devolvido por abatimento de conta, credito de fornecedor,
   reembolso em Dinheiro ou Pix, valor pendente ou composicao parcial.
9. Aplicar credito pelo metodo FIFO somente em contas do mesmo fornecedor.
10. Preservar historico e permitir reversoes controladas sem duplicidade.
11. Exibir Entradas, devolucoes, creditos e saldos na ficha do fornecedor.
12. Restringir pagamento de Conta a Pagar a Dinheiro, Pix ou Debito.
13. Manter produto, documento, financeiro, espelho de compatibilidade e
    auditoria na mesma transacao.
14. Cobrir SQLite e o caminho PostgreSQL por adaptador simulado.

### 12.3 Estrutura e compatibilidade

- migration `v005_purchase_financial_flows` adiciona somente tabelas e indices;
- migrations anteriores permanecem preservadas;
- registros antigos nao recebem vinculos financeiros inventados;
- cancelamentos e devolucoes preservam os documentos originais;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 12.4 Limites deliberados

Permanecem fora da Etapa 5:

- livro transacional unificado de todas as origens de estoque;
- inventario e ajustes de contagem;
- garantias de fornecedor;
- conciliacao bancaria;
- relatorios consolidados de compras.

O item seguinte do roteiro, apos a conclusao da Etapa 6, e a Etapa 7 -
Inventario.

## 13. Conclusao da Etapa 6 - Estoque transacional

### 13.1 Objetivo

Consolidar as origens operacionais atuais em um livro transacional de estoque,
preservando o saldo real do produto e tornando reserva e disponibilidade
rastreaveis.

### 13.2 Entregas concluidas

1. Criar `inventory_movements` com snapshots de produto, origem, referencia,
   usuario, data e saldos anterior e posterior.
2. Registrar quantidade real, reservada e disponivel em cada movimento.
3. Integrar Entrada, cancelamento de Entrada, devolucao ao fornecedor e
   cancelamento dessa devolucao.
4. Integrar venda, cancelamento de venda e devolucao de cliente.
5. Integrar reserva e liberacao de Condicional sem alterar o estoque real.
6. Impedir estoque real, reservado ou disponivel negativo.
7. Detectar saldo ou reserva alterados por operacao concorrente e rejeitar a
   gravacao sem efeitos parciais.
8. Preservar nome e codigo do produto no momento do movimento.
9. Manter espelho compativel no `app_state`, sem usar edicao cadastral como
   origem de estoque.
10. Disponibilizar consulta de historico por produto e tipo de movimento.
11. Exibir estoque real, reservado e disponivel e o historico na tela de
    Estoque.
12. Ocultar produtos sem disponibilidade das listas operacionais de Estoque,
    Venda, Condicional e Catalogo.
13. Cobrir os fluxos em SQLite e o caminho PostgreSQL por adaptadores
    simulados, com rollback e validacao estrutural.

### 13.3 Estrutura e compatibilidade

- migration `v006_transactional_inventory` adiciona somente tabela, indices e
  um snapshot inicial para produtos cujo saldo positivo ja existe;
- o snapshot inicial nao altera o saldo do produto nem inventa documentos
  anteriores;
- produtos sem saldo nao recebem movimento artificial;
- migrations anteriores permanecem preservadas;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 13.4 Limites deliberados

Permanecem fora da Etapa 6:

- inventario, contagem, divergencia, aprovacao e ajuste;
- persistencia relacional completa de Condicionais;
- redesenho transacional completo de Vendas;
- lotes, validade e custo medio;
- relatorios consolidados de estoque.

Esses pontos permanecem nas etapas dependentes do roteiro. A proxima entrega e
a Etapa 7 - Inventario.

## 14. Conclusao da Etapa 7 - Inventario

### 14.1 Objetivo

Permitir a conferencia fisica do estoque sem editar produtos diretamente,
preservando o saldo de abertura, a contagem, as divergencias e os ajustes em
um fluxo transacional e auditavel.

### 14.2 Entregas concluidas

1. Abrir inventario geral ou parcial por marca, categoria e produto.
2. Gerar numero sequencial por loja e snapshot imutavel dos produtos do escopo.
3. Preservar no snapshot os saldos real, reservado e disponivel da abertura.
4. Aceitar contagem manual ou por codigo de barras, distinguindo item nao
   contado de quantidade zero.
5. Registrar cada alteracao de contagem com versao, usuario e data.
6. Impedir contagem fora do escopo e rejeitar versao concorrente desatualizada.
7. Exigir que todos os itens sejam contados antes da finalizacao.
8. Comparar a contagem com o saldo disponivel atual no momento da finalizacao,
   sem tratar pecas reservadas em Condicional como fisicamente disponiveis.
9. Permitir ao operador finalizar somente inventario sem divergencia.
10. Exigir administrador e observacao geral quando houver divergencia.
11. Gerar movimentos `inventory_adjustment` positivos ou negativos no ledger,
    com custo de referencia e impacto financeiro informativo.
12. Atualizar produto, espelho JSON, inventario, movimentos e auditoria na
    mesma transacao.
13. Tornar abertura e finalizacao idempotentes e preservar rollback integral.
14. Permitir cancelamento sem alterar estoque e manter contagens no historico.
15. Disponibilizar lista, busca e filtros por tipo, situacao, responsavel e
    periodo na interface.
16. Cobrir SQLite e PostgreSQL por adaptador simulado, incluindo locks,
    permissao, falhas de auditoria e contratos HTTP.

### 14.3 Estrutura e compatibilidade

- migration `v007_inventory_counts` adiciona `inventory_sequences`,
  `inventories`, `inventory_items` e `inventory_count_events`;
- a migration e aditiva, nao apaga nem reescreve dados existentes;
- os ajustes utilizam o ledger `inventory_movements` criado na Etapa 6;
- migrations anteriores permanecem preservadas;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 14.4 Limites deliberados

Permanecem fora da Etapa 7:

- relatorio consolidado de inventarios;
- exportacao PDF ou documento numerado;
- contagem por lote, validade ou localizacao fisica;
- aprovacao em multiplos niveis;
- integracoes com coletores externos.

Relatorios e documentos permanecem previstos na Etapa 16.

## 15. Conclusao da Etapa 8 - Modalidades de cartao

### 15.1 Objetivo

Estruturar as configuracoes de Debito e Credito que serao consumidas pelo fluxo
de Vendas, sem antecipar a persistencia ou os efeitos financeiros da venda.

### 15.2 Entregas concluidas

1. Cadastrar Debito em uma parcela e Credito de 1x a 10x.
2. Configurar taxa percentual e prazo de recebimento em dias.
3. Controlar inicio e fim de vigencia em timestamps normalizados para UTC.
4. Ativar e desativar modalidades sem apagar registros historicos.
5. Preservar identificador estavel e versoes anteriores de cada modalidade.
6. Impedir duplicidade por loja, tipo e quantidade de parcelas.
7. Validar tipo, parcelas, taxa, prazo, vigencia e situacao no backend.
8. Restringir consulta e manutencao ao perfil Administrador.
9. Registrar criacao, alteracao e mudanca de situacao na auditoria.
10. Disponibilizar cadastro, busca, edicao, situacao e historico na interface.
11. Limpar taxas e prazos carregados no navegador ao encerrar a sessao.
12. Cobrir migrations, autorizacao, validacoes, historico, auditoria e contrato
    visual com testes automatizados.

### 15.3 Estrutura e compatibilidade

- migration `v008_card_modalities` adiciona o cadastro atual das modalidades;
- migration `v009_card_modality_history` adiciona identificador estavel e
  historico de versoes;
- ambas sao aditivas, preservam as migrations anteriores e possuem comandos
  equivalentes para SQLite e PostgreSQL;
- a ordenacao e as consultas do modulo nao dependem de recursos exclusivos do
  SQLite;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 15.4 Limite desta etapa

A Etapa 8 configura as modalidades. A selecao da modalidade na Venda, o snapshot
imutavel de taxa e prazo, o calculo de taxa e valor liquido e a criacao do
recebivel pertencem a Etapa 9 - Vendas.

## 16. Conclusao da Etapa 9 - Vendas

### 16.1 Objetivo

Tornar a criacao de vendas uma operacao transacional e rastreavel, usando o
backend como fonte autoritativa para produtos, estoque, clientes, modalidades
de cartao e efeitos financeiros.

### 16.2 Entregas concluidas

1. Gerar numero sequencial de venda por loja.
2. Exigir chave de idempotencia e impedir duplicidade por repeticao da mesma
   requisicao.
3. Validar no backend produto ativo, saldo real e saldo reservado em
   Condicional.
4. Preservar snapshots do produto, custo, preco, marca, categoria, tamanho,
   cor e genero no item vendido.
5. Permitir preco praticado, desconto e acrescimo por item.
6. Permitir desconto e acrescimo globais, rateados entre os itens.
7. Registrar pagamentos mistos com soma exata ao total da venda.
8. Tratar valor entregue e troco em Dinheiro sem registrar o troco como
   faturamento.
9. Registrar Dinheiro e Pix como entradas imediatas no caixa.
10. Exigir modalidade ativa e vigente para Debito e Credito.
11. Preservar no pagamento e no recebivel o snapshot imutavel da modalidade,
    taxa, prazo, valor bruto, taxa financeira e valor liquido.
12. Gerar um recebivel de cartao por componente de pagamento.
13. Gerar de uma a tres parcelas de crediario, com vencimentos mensais pelo
    dia-base confirmado, somente para cliente identificado, ativo e
    desbloqueado.
14. Baixar estoque, registrar movimento de inventario, venda, pagamentos,
    recebiveis, caixa, espelho JSON e auditoria em uma unica transacao.
15. Preservar rollback integral quando qualquer etapa da operacao falhar.
16. Disponibilizar no PDV apenas modalidades de cartao permitidas para a venda,
    sem expor taxas ou configuracoes administrativas ao operador.

### 16.3 Estrutura e compatibilidade

- migration `v010_transactional_sales` adiciona sequencias, idempotencia,
  snapshots comerciais e financeiros sem apagar dados existentes;
- a migration possui comandos equivalentes para SQLite e PostgreSQL;
- o fluxo transacional utiliza bloqueio de escrita no SQLite e bloqueios
  explicitos no PostgreSQL;
- a criacao de venda nao chama `write_state()`, `sync_business_tables()` ou
  `sync_sale_to_state()`;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 16.4 Limites deliberados

Esta etapa conclui a criacao da venda. Cancelamento, devolucao, troca,
Condicional e relatorios permanecem nos respectivos fluxos e etapas do roteiro.

## 17. Conclusao da Etapa 10 - Crediario

### 17.1 Objetivo

Consolidar o Crediario como modulo transacional, mantendo venda, parcelas,
recebimentos, caixa, recebiveis de cartao, historico e auditoria coerentes.

### 17.2 Entregas concluidas

1. Exigir cliente identificado, ativo e nao padrao para novas vendas no
   Crediario.
2. Limitar o parcelamento a tres parcelas.
3. Sugerir o primeiro vencimento para o mes seguinte e permitir confirmacao
   manual de uma data valida.
4. Gerar as parcelas seguintes pelo mesmo dia-base, usando o ultimo dia do mes
   quando o dia nao existir.
5. Calcular o credito utilizado pelo saldo aberto autoritativo.
6. Bloquear excesso de limite sem autorizacao explicita e, quando autorizado,
   elevar e auditar o novo limite dentro da transacao da venda.
7. Alertar no PDV quando o cliente possuir parcela vencida.
8. Permitir recebimento total, parcial ou antecipado de parcelas selecionadas.
9. Permitir desconto por valor ou percentual, sem saldo negativo e com baixa
   integral quando o saldo ficar zerado.
10. Registrar juros, multa e acrescimo somente quando informados manualmente.
11. Registrar Dinheiro e Pix imediatamente no Caixa.
12. Registrar Debito e Credito como recebivel bancario liquido, preservando o
    snapshot da modalidade aplicada.
13. Manter valor original, saldo aberto, valores pagos, ajustes, usuario,
    timestamps e vinculo com venda e parcela.
14. Separar renegociacao do recebimento normal, preservando vencimento original,
    vencimento anterior, novo vencimento, saldo anterior e novo saldo.
15. Garantir idempotencia e rollback integral de recebimentos e renegociacoes.
16. Disponibilizar busca, indicadores, filtros, detalhes, historico, recebimento
    e renegociacao na interface.

### 17.3 Estrutura e compatibilidade

- migration `v011_store_credit_business_rules` adiciona saldo aberto, totais de
  ajustes, idempotencia e snapshots aos pagamentos;
- a tabela `receivable_renegotiations` preserva o historico das renegociacoes;
- a migration e aditiva, possui comandos equivalentes para SQLite e PostgreSQL
  e nao reescreve registros historicos;
- pagamentos e renegociacoes usam uma unica transacao, com bloqueio de linha no
  caminho PostgreSQL;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 17.4 Limites deliberados

Devolucoes com impacto no Crediario foram tratadas na Etapa 12. O cancelamento
geral de Venda permanece na Etapa 13; relatorios, alertas e Score permanecem
nas respectivas etapas posteriores.

## 18. Conclusao da Etapa 11 - Condicionais

### 18.1 Objetivo

Consolidar o Condicional como reserva temporaria e rastreavel, preservando
cliente, produtos, prazo, usuario, retornos e a conversao segura em Venda.

### 18.2 Entregas concluidas

1. Exigir cliente cadastrado, identificado e ativo.
2. Gerar numero sequencial, data e hora da saida, usuario responsavel e retorno
   previsto em tres dias civis.
3. Preservar snapshots de produto, variacao, custo e preco de referencia.
4. Reservar somente estoque disponivel sem alterar o estoque real.
5. Impedir que a mesma quantidade reservada seja oferecida em nova Venda,
   Condicional, Catalogo ou operacao de estoque.
6. Classificar atraso dinamicamente pela data prevista e pelas pecas pendentes.
7. Permitir retornos parciais e sucessivos por quantidade.
8. Liberar somente a reserva das pecas devolvidas, sem movimento financeiro.
9. Encaminhar pecas compradas para uma Venda normal com cliente e origem
   preservados.
10. Manter a reserva enquanto a Venda originada do Condicional estiver
    pendente.
11. Baixar estoque real e reserva na mesma transacao da Venda concluida.
12. Finalizar somente quando todas as quantidades tiverem destino confirmado.
13. Bloquear cancelamento com pecas pendentes e exigir motivo, usuario e data.
14. Preservar historico de retornos e vinculos com Vendas.
15. Disponibilizar indicadores, busca, filtros, detalhes, historico e impressao
    na interface.
16. Garantir idempotencia, concorrencia e rollback integral.

### 18.3 Estrutura e compatibilidade

- migration `v012_transactional_conditionals` adiciona tabelas de sequencia,
  documento, itens, retornos e vinculos com Vendas;
- `sales` e `sale_items` recebem apenas os vinculos opcionais de origem;
- a migration e aditiva e equivalente para SQLite e PostgreSQL;
- criacao, retorno, cancelamento e conversao usam transacao unica e bloqueios
  apropriados ao adaptador;
- o `app_state` permanece somente como espelho direcionado de compatibilidade;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 18.4 Limites deliberados

Relatorios consolidados e alertas de Condicionais permanecem nas etapas
especificas do roteiro. Trocas, devolucoes de Venda e garantias foram
integradas na Etapa 12.

## 19. Conclusao da Etapa 12 - Trocas, Devolucoes e Garantias

### 19.1 Objetivo

Consolidar o pos-venda como fluxo historico, transacional e rastreavel, sem
apagar a Venda original nem reconstruir globalmente as tabelas de negocio.

### 19.2 Entregas concluidas

1. Permitir devolucao parcial ou total somente de quantidades elegiveis.
2. Ratear o desconto global e usar valor liquido e custo historico do item.
3. Repor estoque vendavel uma unica vez e registrar o movimento de inventario.
4. Alocar devolucoes proporcionalmente entre as formas do pagamento misto.
5. Reduzir primeiro recebiveis pendentes de cartao e Crediario.
6. Devolver somente valores efetivamente recebidos, pela origem rastreavel.
7. Bloquear estorno automatico de registros legados sem vinculo confiavel.
8. Preservar a data operacional da devolucao e o historico da Venda.
9. Implementar troca com produto devolvido, substituto e diferenca financeira.
10. Gerar uma Venda vinculada para os produtos entregues na troca.
11. Permitir cancelamento formal e idempotente da troca, revertendo estoque,
    diferencas financeiras e documentos vinculados na mesma transacao.
12. Abrir garantia vinculada a cliente, Venda, item, produto e fornecedor.
13. Registrar fotos, analise, envio ao fornecedor e eventos do ciclo de vida.
14. Resolver garantia por reparo, substituicao, credito, reembolso ou troca.
15. Gerar Entrada rastreavel quando a substituicao do fornecedor for destinada
    ao estoque da loja.
16. Atualizar apenas os espelhos correspondentes no `app_state`.
17. Preservar auditoria, idempotencia, concorrencia e rollback integral.

### 19.3 Estrutura e compatibilidade

- migration `v013_returns_exchanges_warranties` amplia devolucoes e adiciona
  alocacoes financeiras, reducoes de recebiveis, trocas, cancelamentos de
  troca, garantias, fotos e eventos;
- Entradas originadas por reposicao de garantia preservam `origin` e
  `warranty_id`;
- as alteracoes sao aditivas e equivalentes para SQLite e PostgreSQL;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 19.4 Limites deliberados

O cancelamento geral de Venda continua como pendencia financeira da Etapa 13.
Relatorios consolidados de pos-venda e alertas de garantia permanecem,
respectivamente, nas Etapas 16 e 17.

## 20. Conclusao da Etapa 13 - Caixa e Financeiro

### 20.1 Objetivo

Consolidar o Caixa como saldo continuo e rastreavel, completar Contas a Pagar
e garantir que correcoes financeiras ocorram por estorno, sem apagar o
historico.

### 20.2 Entregas concluidas

1. Manter saldo continuo, sem fechamento diario operacional.
2. Bloquear qualquer saida que torne o saldo financeiro negativo.
3. Registrar entradas manuais somente em Dinheiro ou Pix.
4. Registrar saidas manuais em Dinheiro, Pix ou Debito, com categoria de
   despesa ativa obrigatoria.
5. Preservar origem, usuario, data, hora e saldo resultante em cada movimento.
6. Permitir estorno por movimento inverso vinculado, uma unica vez.
7. Registrar manualmente o valor efetivamente recebido de Debito e Credito
   pela Conta Bancaria, com idempotencia.
8. Filtrar e exportar a linha do tempo do Caixa por periodo, forma,
   movimento e categoria.
9. Permitir baixa total ou parcial de Contas a Pagar com Dinheiro, Pix ou
   Debito.
10. Registrar juros, multa e desconto somente quando informados manualmente.
11. Permitir desconto integral que encerra a conta sem criar saida de Caixa.
12. Permitir estorno de baixa e cancelamento apenas de conta sem pagamento
    ativo.
13. Preservar eventos, pagamentos, usuario, timestamps e saldo aberto da conta.
14. Gerar contas recorrentes mensais com uma unica ocorrencia por serie e mes.
15. Restringir edicao financeira de contas com pagamento parcial e bloquear
    edicao de contas pagas ou canceladas.
16. Cancelar Venda integral por devolucao total vinculada, recompondo estoque
    uma vez e revertendo cada forma de pagamento pela origem real.
17. Garantir idempotencia, auditoria e rollback nas operacoes criticas.

### 20.3 Estrutura e compatibilidade

- migration `v014_financial_ledger` amplia movimentos e contas a pagar e
  adiciona pagamentos, eventos, recebimentos bancarios e cancelamentos de
  Venda;
- os indices impedem repeticao de idempotencia, estorno, recorrencia mensal e
  cancelamento de uma mesma Venda;
- a migration e aditiva e possui comandos equivalentes para SQLite e
  PostgreSQL;
- o `app_state` recebe somente os espelhos diretamente afetados;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 20.4 Limites deliberados

A conciliacao detalhada por operadora, lote e recebivel pertence a Etapa 14.
O CSV atual representa a exportacao tabular do Caixa; documento persistente e
formatos adicionais pertencem as etapas de documentos e relatorios.

## 21. Conclusao da Etapa 14 - Conciliacao de Cartoes

### 21.1 Objetivo

Substituir a baixa bancaria sem vinculo por conciliacao explicita de cada
recebivel de Debito ou Credito, preservando valor previsto, valor efetivo,
diferenca, historico e uma unica movimentacao financeira por operacao.

### 21.2 Entregas concluidas

1. Listar recebiveis de cartao com busca, modalidade, situacao, periodo,
   paginacao e indicadores resumidos.
2. Preservar venda, cliente, modalidade, parcelas, bruto, taxa, tarifa,
   liquido, previsao, saldo recebido e diferenca.
3. Permitir conciliacao individual exata, parcial ou encerrada com
   divergencia explicita e observacao obrigatoria.
4. Permitir conciliacao em lote com distribuicao manual vinculada aos
   recebiveis selecionados.
5. Exigir que a soma das alocacoes corresponda ao valor efetivamente
   recebido.
6. Gerar uma unica entrada no Caixa para cada conciliacao, inclusive em lote.
7. Recalcular individualmente a situacao e o saldo de cada recebivel.
8. Preservar historico do agrupador, dos itens e dos pagamentos vinculados.
9. Permitir estorno formal apenas da conciliacao completa, com motivo,
   movimento financeiro inverso e restauracao dos saldos anteriores.
10. Bloquear repeticao por idempotencia e alteracao concorrente por versao e
    saldo esperado.
11. Executar recebiveis, espelho direcionado, Caixa e auditoria em uma unica
    transacao.
12. Restringir a interface principal ao novo fluxo de recebiveis e bloquear
    novas baixas sem vinculo pelo endpoint bancario legado.

### 21.3 Estrutura e compatibilidade

- migration `v015_card_reconciliation` adiciona agrupadores e itens de
  conciliacao, vinculos de pagamento, diferenca e dados de estorno;
- a migration e aditiva e equivalente para SQLite e PostgreSQL;
- PostgreSQL bloqueia os registros afetados durante a transacao;
- SQLite utiliza transacao imediata para impedir gravacoes concorrentes;
- o `app_state` recebe somente os espelhos diretamente afetados;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 21.4 Limites deliberados

Integracao automatica com operadoras, arquivos bancarios e adquirentes nao faz
parte desta etapa. Relatorios consolidados de conciliacao pertencem a Etapa 16.

## 22. Conclusao da Etapa 15 - Catalogo e Documentos

### 22.1 Objetivo

Disponibilizar um Catalogo interno seguro e transformar impressoes operacionais
em documentos rastreaveis, sem expor custo, margem, quantidade exata de estoque
ou outros dados financeiros internos.

### 22.2 Entregas concluidas

1. Listar apenas produtos ativos com estoque disponivel maior que zero.
2. Calcular disponibilidade como estoque real menos reservas de Condicionais
   ativos.
3. Exibir `Disponivel` ou `Ultima unidade`, sem publicar quantidade exata.
4. Buscar por nome, marca, categoria, cor e tamanho, inclusive por multiplos
   termos.
5. Filtrar por categoria, marca, tamanho, cor e faixa de preco.
6. Ordenar por nome, menor preco ou maior preco.
7. Exibir detalhe do produto com foto, dados comerciais e placeholder.
8. Revalidar no backend a mesma consulta usada para emitir o Catalogo.
9. Gerar etiquetas Code128 em SVG com nome, variacao e preco.
10. Registrar comprovantes de Venda, Condicionais e Trocas com a operacao de
    origem.
11. Preservar snapshot imutavel, loja, usuario, formato, data, nome seguro,
    versao do modelo e numero da via.
12. Gerar segunda via a partir do snapshot original, sem recalculo historico.
13. Aplicar idempotencia, auditoria, isolamento por loja e rollback atomico.
14. Impedir que a geracao ou reimpressao altere estoque, Caixa, recebiveis ou
    qualquer outra regra operacional.

### 22.3 Estrutura e compatibilidade

- migration `v016_catalog_documents` adiciona `generated_documents` e indices
  de idempotencia, origem e data;
- a migration e aditiva e equivalente para SQLite e PostgreSQL;
- a geracao Code128 utiliza `python-barcode` com saida SVG, sem binario
  externo;
- o backend e a fonte autoritativa do Catalogo e dos snapshots;
- nenhuma migration foi executada em banco operacional ou de producao;
- nao houve commit, push ou deploy nesta etapa.

### 22.4 Limites deliberados

O navegador executa a impressao e permite salvar o documento como PDF; o
servidor persiste a emissao e o snapshot, mas nao armazena um arquivo PDF
binario. Relatorios consolidados e suas exportacoes pertencem a Etapa 16.

## 23. Conclusao da Etapa 16 - Relatorios e Exportacoes

### 23.1 Objetivo

Consolidar consultas operacionais e financeiras confiaveis sem recalcular
historicos a partir dos cadastros atuais e sem alterar qualquer estado
operacional durante a emissao.

### 23.2 Entregas

1. Disponibilizar os relatorios de Vendas, Produtos Vendidos, Caixa,
   Crediario, Contas a Pagar, Estoque, Condicionais e Lucro.
2. Aplicar no backend os periodos Hoje, Ultimos 7 dias, Ultimos 30 dias, Mes
   atual e intervalo personalizado no fuso `America/Sao_Paulo`.
3. Aplicar filtros especificos por relatorio e paginacao autoritativa.
4. Preservar snapshots historicos de produtos, marcas, custos e valores
   praticados.
5. Desconsiderar Vendas canceladas e aplicar devolucoes na data da ocorrencia
   aos totais liquidos.
6. Considerar pagamentos mistos por seus componentes reais.
7. Proteger Lucro e totais financeiros de Estoque no backend, permitindo-os
   somente ao Administrador.
8. Gerar PDF e XLSX no servidor com os mesmos filtros da consulta.
9. Auditar a exportacao do relatorio de Lucro sem registrar o conteudo das
   linhas.
10. Exibir carregamento, erro, vazio, sucesso e tentativa novamente na
    interface.
11. Preservar o contrato de sessao e impedir a permanencia de dados de
    relatorio na troca de usuario.

### 23.3 Estrutura e compatibilidade

- `report_exports.py` concentra a geracao dos arquivos PDF e XLSX;
- `openpyxl` e `reportlab` sao dependencias exclusivas de exportacao;
- as consultas utilizam as tabelas relacionais e nao chamam `write_state()` ou
  `sync_business_tables()`;
- contas a pagar antigas sem pagamentos relacionais preservam os acumulados
  existentes no proprio registro;
- a implementacao funciona em SQLite e no caminho PostgreSQL pelo adaptador
  existente;
- nenhuma migration foi necessaria ou executada nesta etapa;
- nao houve commit, push ou deploy nesta etapa.

### 23.4 Limites deliberados

As consultas priorizam compatibilidade com timestamps legados e atualmente
filtram os conjuntos relacionais no backend antes da paginacao. Para volumes
excepcionalmente grandes, indices e paginacao SQL especializada poderao ser
avaliados sem alterar os contratos entregues.

## 24. Conclusao da Etapa 17 - Alertas, Score e Dashboard

### 24.1 Alertas operacionais

- a central deriva do estado atual os alertas de crediario atrasado por
  cliente, Condicional atrasado, Conta a Pagar vencendo hoje, Conta a Pagar
  vencida e ultima unidade disponivel;
- alertas resolvidos deixam de ser exibidos sem apagar o historico operacional
  que os originou;
- leitura, fixacao, busca, filtros e paginacao sao isolados por usuario na
  tabela `alert_user_states`;
- Administrador e Operador podem consultar a central, sem exposicao de
  credenciais ou configuracoes internas.

### 24.2 Score informativo do cliente

- o backend calcula o score de 0 a 100 pelos ultimos 12 meses-calendario;
- o comportamento de pagamento do crediario representa ate 80 pontos e as
  compras diretas representam ate 20 pontos;
- atrasos atuais, inclusive de obrigacoes mais antigas, reduzem o resultado;
- renegociacoes preservam o atraso existente antes da nova data;
- cancelamentos e Vendas totalmente devolvidas nao aumentam a pontuacao;
- clientes sem historico avaliavel recebem estado indisponivel, nunca uma nota
  inventada;
- o score e informativo e nao autoriza ou bloqueia credito automaticamente.

### 24.3 Dashboard

- as consultas usam as tabelas relacionais e respeitam Hoje, 7 dias, 30 dias,
  Mes atual e periodo personalizado no fuso `America/Sao_Paulo`;
- Vendas canceladas sao desconsideradas e devolucoes reduzem os indicadores na
  data em que ocorreram;
- pagamentos mistos sao separados por forma, e a rosca utiliza apenas valores
  liquidos positivos com percentuais totalizando 100%;
- Administrador recebe indicadores financeiros; Operador recebe somente os
  indicadores autorizados pelo backend;
- marcas utilizam snapshots historicos, e produtos parados usam estoque
  disponivel descontando Condicionais em aberto;
- carregamento, erro, vazio, sucesso, tentativa novamente e virada automatica
  do dia foram preservados na interface.

### 24.4 Estrutura e validacao

- a migration aditiva v17 cria apenas `alert_user_states` e seus indices;
- nenhuma migration foi executada em banco operacional ou de producao;
- `tests/test_alert_score_dashboard_business_rules.py` cobre os fluxos da
  etapa em SQLite e o caminho PostgreSQL por adaptador simulado;
- nao houve commit, push ou deploy nesta etapa.

## 25. Conclusao da Etapa 18 - Configuracoes e Permissoes

### 25.1 Configuracoes da loja

- o Administrador pode manter nome empresarial, nomes legal e comercial,
  CPF/CNPJ, contatos, endereco e identidade visual da loja;
- a configuracao exige nome da loja e valida CPF/CNPJ quando informado;
- a logo aceita JPG, PNG ou WEBP de ate 5 MB e a identidade operacional e
  aplicada tambem antes do login;
- preferencias de impressao, rodape do comprovante e dados informativos de Pix
  permanecem versionados e auditados;
- conflitos de edicao concorrente retornam erro controlado e nao sobrescrevem
  silenciosamente uma versao mais recente.

### 25.2 Operacao e aparencia

- Dinheiro permanece sempre habilitado;
- Pix, Debito, Credito e Crediario podem ser habilitados ou desabilitados pelo
  Administrador somente para novas vendas;
- documentos historicos preservam o snapshot da identidade usada na emissao;
- cada usuario escolhe tema claro, escuro ou conforme o sistema, sem alterar a
  preferencia de outros usuarios.

### 25.3 Usuarios e acessos

- a matriz de acesso e fixa para os perfis Administrador e Operador e e
  validada no backend;
- somente o Administrador gerencia configuracoes, usuarios e acessos;
- usuarios deixam de ser excluidos fisicamente e passam a ser desativados;
- o sistema impede desativar ou rebaixar o ultimo Administrador ativo;
- cinco tentativas consecutivas de login incorreto geram bloqueio persistente,
  removido apenas por um Administrador;
- respostas de estado para Operador nao incluem a lista administrativa de
  usuarios.

### 25.4 Estrutura e validacao

- a migration aditiva v18 cria `store_settings` e `user_preferences`, adiciona
  o estado persistente de bloqueio em `users` e cria somente indices novos;
- a migration e compativel com SQLite e PostgreSQL e nao foi executada em
  banco operacional ou de producao;
- `tests/test_store_settings_permissions_business_rules.py` cobre
  configuracoes, concorrencia, permissoes, temas, bloqueio, desativacao,
  documentos e upload de logo;
- nao houve commit, push ou deploy nesta etapa.

## 26. Definition of Done para as Proximas Etapas

Uma Sprint Business somente podera ser declarada concluida quando:

1. regras do escopo estiverem listadas;
2. divergencias tiverem decisao registrada;
3. migration for aditiva e reversivel quando necessaria;
4. backend for a fonte autoritativa;
5. operacao critica usar transacao;
6. autorizacao for validada no servidor;
7. auditoria preservar usuario, loja, data e origem;
8. testes cobrirem sucesso, validacao, permissao, concorrencia e rollback;
9. SQLite e PostgreSQL forem considerados;
10. frontend tratar carregamento, vazio, erro e sucesso;
11. dados historicos forem preservados;
12. documentacao e esta matriz forem atualizadas;
13. suite completa permanecer aprovada;
14. diff for revisado;
15. nao houver commit, push, migration executada ou deploy sem autorizacao.

## 27. Conclusao do Ciclo Atual

A Etapa 1 estabelece que a implementacao Business nao deve comecar por Vendas
ou Dashboard. A primeira implementacao funcional deve ser Clientes, seguida de
Fornecedores e Produtos/Entradas.

O principal risco atual e tratar o saldo de estoque do cadastro do produto como
fonte suficiente. A especificacao oficial exige que estoque e financeiro sejam
consequencias de documentos e movimentos rastreaveis.

As Etapas 2 a 18 foram concluidas com testes de backend, integracao,
migrations, bootstrap e contratos visuais. O roteiro Business documentado
nesta matriz esta funcionalmente concluido; evolucoes posteriores devem partir
de novas regras oficiais e de validacao operacional antes de producao. A
consolidacao, migration e publicacao controlada estao descritas em
`docs/BUSINESS_RELEASE_READINESS.md`.
