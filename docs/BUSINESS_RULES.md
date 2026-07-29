# Regras de Negócio — Mova Sports

ERP MOVA SPORTS
ESPECIFICAÇÃO FUNCIONAL E REGRAS DE NEGÓCIO

Versão: 1.0
Data de oficialização: 17 de julho de 2026
Status: OFICIAL — APROVADA PARA IMPLEMENTAÇÃO
Estabelecimento: MOVA SPORTS
Responsável pela validação: Administração da MOVA SPORTS

## Objetivo

Este documento define as regras oficiais de negócio do sistema Mova Sports.

Caso exista conflito entre o comportamento atual do sistema e este documento, a divergência deve ser identificada e confirmada antes de qualquer alteração relevante.

O Codex não deve inventar novas regras de negócio. Quando uma regra não estiver definida, deve solicitar esclarecimento.

---

# 1. CLIENTES

## 1.1 Cadastro de cliente

O sistema deve permitir o cadastro de clientes.

O cadastro possui os seguintes campos:

- nome completo;
- CPF;
- data de nascimento;
- telefone;
- e-mail;
- CEP;
- endereço;
- número;
- bairro;
- cidade;
- estado;
- limite de crédito;
- observações.

São obrigatórios:

- nome completo;
- telefone;
- limite de crédito.

Os demais campos são opcionais, salvo quando outra regra de negócio exigir a informação para uma operação específica.

O backend deve validar os campos obrigatórios.

O frontend pode indicar visualmente os campos obrigatórios, mas a validação não pode existir somente na interface.

---

## 1.2 Nome completo

O nome completo do cliente é obrigatório.

Não permitir cadastro com nome:

- vazio;
- contendo somente espaços.

O nome deve ser utilizado nas buscas e na identificação do cliente nas operações do sistema.

Alterações futuras no nome do cadastro não devem apagar ou invalidar operações históricas vinculadas ao identificador do cliente.

---

## 1.3 CPF

O CPF é opcional no cadastro do cliente.

Quando informado, o CPF deve:

- possuir formato válido;
- possuir quantidade correta de dígitos;
- ser validado matematicamente;
- ser único no sistema.

Não aceitar CPF matematicamente inválido.

Não aceitar CPF duplicado.

A validação autoritativa deve existir no backend.

O frontend pode formatar visualmente o CPF no padrão:

000.000.000-00

A formatação visual não substitui a validação matemática.

Clientes sem CPF podem ser cadastrados normalmente.

A ausência de CPF não deve ser tratada como duplicidade entre clientes.

---

## 1.4 CPF já cadastrado

Quando o CPF informado já pertencer a outro cliente, o novo cadastro deve ser recusado.

O sistema deve informar que o CPF já está cadastrado.

Quando possível, a interface pode identificar ou permitir abrir o cadastro existente.

Não criar automaticamente um segundo cliente com o mesmo CPF.

Clientes desativados continuam sendo considerados na validação de unicidade do CPF.

A desativação de um cliente não libera seu CPF para outro cadastro.

---

## 1.5 Telefone

O telefone é obrigatório.

O telefone deve ser utilizado para contato e busca do cliente.

O sistema pode aplicar formatação visual compatível com telefone ou celular.

A existência de outro cliente com o mesmo telefone não deve bloquear automaticamente o cadastro.

Quando o telefone já estiver cadastrado para outro cliente, o sistema deve apresentar um alerta de possível duplicidade.

O usuário pode continuar o cadastro após o alerta.

---

## 1.6 Data de nascimento

A data de nascimento é opcional.

Quando informada, deve ser armazenada como data civil.

A data de nascimento não deve sofrer conversão de timezone.

Não aceitar uma data impossível ou em formato inválido.

---

## 1.7 Endereço

O endereço do cliente pode conter:

- CEP;
- endereço;
- número;
- bairro;
- cidade;
- estado.

Os dados de endereço são opcionais.

O sistema pode utilizar o CEP para auxiliar no preenchimento dos demais campos, quando existir integração disponível.

O preenchimento automático por CEP não transforma os campos de endereço em obrigatórios.

O usuário deve poder corrigir os dados preenchidos quando necessário.

---

## 1.8 E-mail

O e-mail é opcional.

Quando informado, deve possuir formato válido.

O e-mail não é utilizado como identificador obrigatório do cliente.

Não existe, neste momento, regra de unicidade obrigatória para e-mail.

---

## 1.9 Observações

O cadastro do cliente pode possuir campo de observações.

As observações são opcionais.

O campo pode ser utilizado para informações operacionais relevantes ao atendimento do cliente.

As observações não devem alterar automaticamente:

- limite de crédito;
- situação do cliente;
- score;
- bloqueio;
- regras do crediário.

---

## 1.10 Cliente padrão

O sistema deve possuir um cliente padrão para vendas sem identificação individual do comprador.

O cliente padrão deve ser utilizado automaticamente em venda comum quando nenhum outro cliente for selecionado.

O cliente padrão:

- não precisa possuir CPF;
- não pode ser excluído;
- não pode ser desativado;
- não pode utilizar crediário;
- não pode utilizar condicional;
- não possui limite de crédito utilizável;
- deve ser utilizado somente para vendas comuns sem identificação de cliente.

O cliente padrão não representa uma pessoa física cadastrada.

Operações que exigem cliente cadastrado individualmente não podem utilizar o cliente padrão.

---

## 1.11 Situação do cliente

O cliente pode possuir as seguintes situações:

- Ativo;
- Bloqueado;
- Desativado.

A situação deve ser persistida no backend.

A interface pode utilizar destaque visual para identificar a situação do cliente.

---

## 1.12 Cliente ativo

O cliente Ativo pode participar normalmente das operações permitidas pelo sistema.

Um cliente Ativo pode:

- realizar compras;
- utilizar crediário dentro das respectivas regras;
- utilizar condicional;
- possuir histórico de vendas;
- possuir limite de crédito;
- possuir parcelas abertas ou quitadas.

A situação Ativo não elimina outras validações.

Limite de crédito, parcelas atrasadas, estoque e demais regras continuam sendo verificados normalmente.

---

## 1.13 Cliente bloqueado

O cliente Bloqueado permanece cadastrado e mantém todo o histórico.

Um cliente Bloqueado:

- pode realizar venda à vista;
- não pode realizar nova compra no crediário;
- não pode receber novo condicional.

O bloqueio não apaga:

- vendas;
- parcelas;
- pagamentos;
- condicionais anteriores;
- devoluções;
- histórico do cliente.

Obrigações financeiras existentes permanecem válidas e podem continuar sendo recebidas normalmente.

O bloqueio não cancela automaticamente crediários ou condicionais existentes.

---

## 1.14 Bloqueio e desbloqueio de cliente

Administrador e Operador podem bloquear ou desbloquear clientes.

O bloqueio exige motivo.

O motivo deve ser informado manualmente pelo usuário.

Exemplos de motivo podem incluir:

- inadimplência;
- acordo com cliente;
- solicitação do cliente;
- outro.

A lista de exemplos não limita o motivo informado.

O sistema deve preservar, no mínimo:

- motivo do bloqueio;
- data e hora;
- usuário responsável.

Ao desbloquear o cliente, o sistema deve preservar o histórico do bloqueio anterior.

O desbloqueio não deve apagar o motivo ou a ocorrência histórica do bloqueio.

---

## 1.15 Cliente desativado

O cliente pode ser desativado.

Cliente desativado:

- permanece cadastrado;
- mantém todo o histórico;
- não deve aparecer nas buscas normais para novas vendas;
- não deve aparecer nas buscas normais para novo crediário;
- não deve aparecer nas buscas normais para novo condicional;
- não pode ser utilizado em novas operações.

Vendas, pagamentos, parcelas, devoluções e condicionais históricos permanecem preservados.

O cliente pode ser reativado.

Após a reativação, volta a participar das operações conforme sua situação e as demais regras de negócio.

---

## 1.16 Exclusão de cliente

Clientes não devem ser excluídos permanentemente pelo fluxo normal do sistema.

Quando um cliente não deve mais ser utilizado, deve ser desativado.

Não permitir exclusão definitiva através da interface normal.

A regra se aplica mesmo quando o cliente ainda não possuir operações.

O objetivo é preservar a integridade dos cadastros e evitar remoções acidentais.

---

## 1.17 Limite de crédito

Todo cliente cadastrado deve possuir limite de crédito informado.

O limite de crédito é obrigatório.

O limite deve ser maior que zero.

Não permitir:

- limite igual a zero;
- limite negativo;
- valor inválido;
- NaN;
- infinito.

Não existe limite máximo de crédito definido pela regra de negócio.

O valor pode ser definido pelo usuário conforme decisão comercial da loja.

O cliente padrão não utiliza essa regra de limite de crédito.

---

## 1.18 Alteração do limite de crédito

Administrador e Operador podem alterar o limite de crédito do cliente.

Não existe restrição de perfil entre Administrador e Operador para essa operação.

O novo limite deve continuar sendo maior que zero.

A alteração deve preservar histórico.

O histórico da alteração deve registrar, no mínimo:

- limite anterior;
- novo limite;
- data e hora;
- usuário responsável.

Exemplo:

14/07/2026 — Limite alterado de R$ 500,00 para R$ 1.000,00 por Mauro.

Alterar o limite não deve modificar retroativamente vendas ou parcelas existentes.

---

## 1.19 Resumo financeiro do cliente

A ficha do cliente deve apresentar resumo financeiro.

O resumo deve conter, quando aplicável:

- limite de crédito;
- saldo devedor;
- crédito disponível;
- valor em atraso.

Os valores devem ser calculados com base nas regras financeiras oficiais do crediário.

Pagamentos parciais, devoluções, cancelamentos e demais operações que alterem o saldo devem ser considerados.

Não utilizar apenas o valor original das parcelas quando existir:

- valor recebido;
- valor devolvido;
- cancelamento;
- outro abatimento oficial.

---

## 1.20 Crédito disponível

O crédito disponível do cliente deve ser calculado com base em:

- limite de crédito;
- saldo devedor válido.

A fórmula conceitual é:

Crédito disponível = Limite de crédito - Saldo devedor

O cálculo do saldo devedor deve respeitar as regras oficiais do Crediário.

Parcelas quitadas não consomem crédito.

Valores oficialmente devolvidos ou abatidos devem reduzir o saldo correspondente.

O sistema não deve utilizar valores brutos quando existir saldo líquido oficial.

---

## 1.21 Parcelas atrasadas

A ficha do cliente deve identificar quando existirem parcelas atrasadas.

Quando houver atraso, apresentar destaque visual.

Exemplo:

Cliente possui R$ 350,00 em parcelas atrasadas.

O destaque deve considerar o saldo efetivamente em atraso.

Uma parcela parcialmente paga deve considerar apenas o saldo restante.

Valores devolvidos ou abatidos devem ser considerados conforme a regra oficial do crediário.

---

## 1.22 Atraso e novas vendas

A existência de parcelas atrasadas não bloqueia automaticamente uma nova venda.

Ao selecionar um cliente com parcelas atrasadas durante uma venda, o sistema deve apresentar um alerta.

O usuário pode:

- continuar a venda;
- interromper a operação.

O alerta possui finalidade informativa e comercial.

Não existe bloqueio automático de venda à vista por atraso no crediário.

As regras específicas de limite de crédito continuam sendo aplicadas quando a nova venda utilizar Crediário.

---

## 1.23 Tela de Clientes

A tela de Clientes deve possuir, no topo:

- botão NOVO CLIENTE;
- campo de busca.

A busca deve permitir localizar clientes por:

- nome;
- CPF;
- telefone.

A busca deve considerar formatação e normalização dos dados quando necessário.

Exemplo:

A busca por CPF pode ignorar pontos e traço para fins de comparação.

---

## 1.24 Indicadores da tela de Clientes

A tela de Clientes deve apresentar cards de resumo.

Os indicadores são:

- Total de Clientes;
- Clientes com Crediário em Aberto;
- Clientes com Parcelas Atrasadas;
- Total a Receber.

Os valores devem refletir os dados válidos do sistema.

O Total a Receber deve utilizar saldo líquido válido do crediário.

Não considerar como aberto o valor já:

- pago;
- devolvido;
- cancelado;
- abatido oficialmente.

---

## 1.25 Listagem de clientes

A listagem principal deve apresentar:

- Cliente;
- CPF;
- Telefone;
- Limite;
- Saldo Devedor;
- Situação;
- Ação.

A ação principal deve permitir visualizar os detalhes do cliente.

A listagem deve permitir identificar visualmente clientes:

- Ativos;
- Bloqueados;
- Desativados, quando o filtro ou contexto permitir sua exibição.

Clientes desativados não devem aparecer nas buscas operacionais normais de venda, crediário ou condicional.

---

## 1.26 Detalhes do cliente

Ao selecionar um cliente, o sistema deve permitir visualizar sua ficha detalhada.

A ficha deve organizar as informações em áreas ou seções coerentes.

Deve apresentar:

- dados do cliente;
- resumo financeiro;
- histórico de compras;
- crediário;
- condicionais.

A organização visual pode utilizar abas, seções ou painéis, desde que as informações permaneçam claras.

---

## 1.27 Dados do cliente na ficha

A ficha deve apresentar os dados cadastrais disponíveis.

Entre eles:

- nome completo;
- CPF;
- data de nascimento;
- telefone;
- e-mail;
- endereço;
- observações;
- situação.

Também deve permitir edição conforme as permissões definidas pelo sistema.

---

## 1.28 Histórico de compras

A ficha do cliente deve apresentar histórico de compras.

O histórico deve considerar todas as vendas vinculadas ao cliente, incluindo vendas realizadas por:

- Dinheiro;
- Pix;
- Débito;
- Crédito;
- Crediário;
- pagamento misto.

Também devem permanecer identificáveis vendas:

- concluídas;
- canceladas;
- com devolução parcial;
- com devolução total.

O histórico não deve apagar uma venda porque ela foi posteriormente cancelada ou devolvida.

A situação correta deve ser apresentada.

---

## 1.29 Informações do histórico de compras

Cada venda exibida no histórico do cliente deve permitir identificar, no mínimo:

- data;
- número da venda;
- valor;
- forma ou formas de pagamento;
- situação.

Quando necessário, deve existir ação para visualizar os detalhes completos da venda.

Os detalhes completos seguem as regras do módulo de Histórico de Vendas.

---

## 1.30 Crediário na ficha do cliente

A ficha do cliente deve permitir consultar as informações do Crediário vinculadas ao cliente.

Devem ser identificáveis:

- parcelas abertas;
- parcelas em dia;
- parcelas atrasadas;
- parcelas quitadas.

Pagamentos parciais devem ser refletidos no saldo restante.

Devoluções e cancelamentos devem ser considerados conforme as regras financeiras oficiais.

A ficha do cliente não substitui a tela principal do Crediário.

Ela funciona como uma visão vinculada ao cliente selecionado.

---

## 1.31 Condicionais na ficha do cliente

A ficha do cliente deve permitir consultar os condicionais vinculados ao cliente.

Devem ser identificáveis condicionais:

- abertos;
- atrasados;
- finalizados;
- cancelados.

A ficha pode apresentar um resumo e permitir acesso aos detalhes do condicional.

O histórico deve preservar produtos comprados e devolvidos conforme as regras do módulo Condicional.

---

## 1.32 Cliente duplicado por CPF

CPF duplicado bloqueia o cadastro.

Não permitir continuar o cadastro enquanto o CPF pertencer a outro cliente.

A regra também considera clientes desativados.

---

## 1.33 Possível duplicidade por telefone

Quando outro cliente possuir o mesmo telefone, apresentar alerta.

O alerta não bloqueia o cadastro.

O usuário pode confirmar e continuar.

Essa regra permite situações como:

- familiares utilizando o mesmo telefone;
- telefone comercial compartilhado;
- outro uso legítimo do mesmo número.

---

## 1.34 Possível duplicidade por nome

Quando existir cliente com nome igual ou potencialmente semelhante, o sistema pode apresentar alerta de possível duplicidade.

O alerta não bloqueia o cadastro.

O usuário pode continuar.

Não utilizar somente o nome como chave única do cliente.

Pessoas diferentes podem possuir o mesmo nome.

---

## 1.35 Score do cliente

O sistema possui previsão futura de Score do Cliente.

O Score não deve ser calculado ou inventado enquanto a fórmula oficial não estiver definida.

A ficha do cliente pode ser estruturada para futura apresentação de:

- pontuação;
- classificação;
- histórico de pagamento;
- pontualidade.

Neste momento:

- não atribuir score automático;
- não criar classificação fictícia;
- não alterar limite de crédito automaticamente com base em score;
- não bloquear cliente com base em score inexistente.

A implementação do Score do Cliente depende de definição específica da regra de pontuação.

---

## 1.36 Rastreabilidade do cliente

O sistema deve preservar o vínculo do cliente com suas operações históricas.

Entre elas:

- vendas;
- crediário;
- pagamentos;
- devoluções;
- cancelamentos;
- condicionais.

Alterações cadastrais futuras não devem transferir operações antigas para outro cliente.

O identificador persistente do cliente deve ser utilizado como vínculo autoritativo.

Nome, CPF ou telefone não devem ser utilizados isoladamente como vínculo histórico quando existir identificador persistente.

---

## 1.37 Regras gerais do módulo Clientes

O sistema deve:

- exigir nome completo;
- exigir telefone;
- exigir limite de crédito maior que zero;
- validar matematicamente o CPF quando informado;
- impedir CPF duplicado;
- permitir cliente sem CPF;
- alertar telefone duplicado sem bloquear;
- alertar possível nome duplicado sem bloquear;
- preservar histórico de alteração de limite;
- permitir bloqueio com motivo;
- preservar histórico de bloqueio;
- permitir somente desativação, nunca exclusão pelo fluxo normal;
- preservar todo o histórico do cliente;
- impedir cliente padrão no Crediário;
- impedir cliente padrão no Condicional;
- destacar parcelas atrasadas;
- não bloquear automaticamente venda à vista por atraso;
- não calcular Score antes da definição da fórmula oficial.

# 2. PRODUTOS E ENTRADAS

## 2.1 Finalidade

O módulo Produtos e Entradas deve centralizar:

- cadastro de Produtos;
- consulta de Produtos;
- edição cadastral;
- atualização dos dados comerciais atuais;
- registro de novas Entradas de Produtos.

O código do Produto deve determinar o fluxo inicial.

Ao informar ou ler um código, o sistema deve verificar no backend se o Produto já existe na loja autenticada.

Quando o código não existir, o sistema inicia o cadastro de um novo Produto.

Quando o código já existir, o sistema recupera o cadastro atual do Produto e permite registrar uma nova Entrada.

Não deve ser necessário acessar um módulo separado de Entrada de Mercadorias para realizar a reposição normal de Produtos.

---

## 2.2 Busca pelo código do Produto

A tela deve possuir o Código do Produto como ponto inicial do fluxo.

O usuário pode informar o código por:

- digitação;
- leitura por leitor compatível com entrada de teclado.

Após a informação do código, o sistema deve consultar o Produto correspondente.

A consulta deve respeitar:

- loja autenticada;
- código normalizado;
- situação e regras oficiais do Produto.

O navegador não deve determinar autoritativamente se o Produto é novo ou existente.

O backend deve validar a existência do Produto.

---

## 2.3 Código inexistente

Quando o código informado não estiver vinculado a Produto existente da loja, o sistema deve iniciar o fluxo:

NOVO PRODUTO.

A interface deve permitir o preenchimento dos dados necessários ao cadastro.

O Produto ainda não deve ser persistido apenas pela consulta do código.

A persistência ocorre somente após confirmação válida do usuário.

---

## 2.4 Código existente

Quando o código já estiver vinculado a Produto existente, o sistema deve iniciar o fluxo:

PRODUTO JÁ CADASTRADO.

O sistema deve recuperar os dados atuais persistidos do Produto.

Devem ser apresentados, quando aplicáveis:

- código;
- nome;
- Marca;
- Categoria;
- Cor;
- Tamanho;
- Gênero;
- Fornecedor atual;
- foto;
- preço de custo atual;
- preço de venda atual;
- estoque real atual;
- quantidade reservada;
- quantidade disponível.

A interface não deve exigir novo preenchimento dos dados já existentes.

---

## 2.5 Dados cadastrais do Produto

O Produto deve possuir os dados definidos pelas regras oficiais do cadastro.

Entre eles, quando aplicáveis:

- Código;
- Nome;
- Marca;
- Categoria;
- Cor;
- Tamanho;
- Gênero;
- Fornecedor;
- Foto;
- Preço de custo;
- Preço de venda;
- Estoque mínimo.

As validações específicas de cada campo continuam seguindo as regras oficiais do módulo e dos Cadastros Auxiliares.

---

## 2.6 Novo Produto e primeira Entrada

Ao cadastrar um novo Produto, o usuário deve informar a quantidade correspondente à primeira Entrada.

A quantidade informada deve representar a quantidade física efetivamente recebida.

Ao confirmar a operação, o sistema deve:

1. validar o Produto;
2. validar os dados cadastrais;
3. validar os preços;
4. validar a quantidade;
5. criar o Produto;
6. registrar a primeira Entrada;
7. aumentar o estoque pela quantidade informada;
8. registrar o usuário responsável;
9. registrar data e hora;
10. preservar o histórico da Entrada.

O cadastro inicial e a primeira Entrada devem formar uma operação consistente.

Falha durante a confirmação não deve criar Produto parcialmente cadastrado com Entrada incompleta.

---

## 2.7 Produto existente e nova Entrada

Quando o Produto já existir, o usuário pode registrar nova Entrada.

A interface deve apresentar o estoque atual como informação.

Exemplo:

Estoque real atual:
5.

O usuário informa:

Quantidade desta Entrada:
10.

O sistema apresenta:

Estoque após Entrada:
15.

Ao confirmar, a quantidade da Entrada deve ser somada ao estoque real atual.

---

## 2.8 Quantidade da Entrada

A quantidade da Entrada deve ser:

- numérica;
- finita;
- inteira;
- maior que zero.

Não permitir:

- quantidade zero;
- quantidade negativa;
- quantidade fracionada;
- NaN;
- infinito;
- texto inválido.

A validação autoritativa deve ocorrer no backend.

---

## 2.9 Estoque atual na tela de Entrada

O estoque real atual deve ser apresentado como informação de somente leitura durante o fluxo de Entrada.

O usuário não deve informar livremente o novo estoque total.

Exemplo incorreto:

Estoque:
20.

Exemplo correto:

Estoque atual:
5.

Quantidade desta Entrada:
15.

Estoque após Entrada:
20.

A finalidade é preservar a origem da alteração do estoque.

---

## 2.10 Proibição de edição direta do estoque

O fluxo Produtos e Entradas não deve permitir substituir diretamente o estoque atual por outro valor.

O usuário não deve utilizar a tela de Produto para corrigir divergências de estoque.

Correções de estoque devem utilizar o módulo Inventário e suas regras de movimentação corretiva.

Essa separação deve permitir distinguir:

- Entrada real de mercadoria;
- Correção de divergência de estoque.

---

## 2.11 Estoque real

O Estoque real representa a quantidade física persistida do Produto.

Uma Entrada confirmada aumenta o Estoque real.

Exemplo:

Estoque real anterior:
5.

Entrada:
10.

Novo Estoque real:
15.

O sistema deve preservar a movimentação correspondente.

---

## 2.12 Estoque reservado

O estoque reservado deve seguir as regras oficiais dos Condicionais abertos.

Produtos vinculados a Condicional aberto continuam fisicamente fora da disponibilidade normal de venda.

A Entrada não altera retroativamente as reservas existentes.

---

## 2.13 Estoque disponível

O Estoque disponível deve continuar sendo calculado conforme a regra oficial:

Estoque disponível =
Estoque real - Quantidade reservada em Condicionais abertos.

Exemplo:

Estoque real:
15.

Reservado:
2.

Disponível:
13.

A Entrada aumenta o Estoque real.

O sistema recalcula a disponibilidade utilizando as reservas existentes.

---

## 2.14 Estoque após Entrada

A interface pode apresentar uma prévia do Estoque real após a Entrada.

A fórmula é:

Estoque real atual + Quantidade da Entrada.

Essa informação é apenas uma prévia antes da confirmação.

O valor autoritativo deve ser recalculado no backend no momento da confirmação.

O backend não deve confiar no valor de Estoque após Entrada enviado pelo navegador.

---

## 2.15 Concorrência na Entrada

Antes de confirmar uma Entrada, o backend deve utilizar o estoque persistido mais recente.

Exemplo:

Tela carregou:
Estoque atual 5.

Outra operação altera o estoque para:
4.

Usuário confirma Entrada de:
10.

O backend deve aplicar a Entrada sobre o estado persistido válido no momento da operação.

Não deve confiar no valor 5 anteriormente exibido pelo navegador como estoque autoritativo.

A operação deve utilizar proteção transacional compatível com a arquitetura oficial.

---

## 2.16 Edição cadastral durante nova Entrada

Quando o Produto já existir, a tela pode permitir editar dados cadastrais atuais durante o fluxo de nova Entrada.

Podem ser alterados, conforme as regras específicas:

- Nome;
- Marca;
- Categoria;
- Cor;
- Tamanho;
- Gênero;
- Fornecedor atual;
- Foto.

A alteração deve atualizar o cadastro atual do Produto.

As alterações valem para operações futuras.

Não reescrever dados históricos de Vendas, Devoluções, Trocas ou outras operações que possuam snapshots preservados.

---

## 2.17 Fornecedor atual do Produto

O Produto pode possuir um Fornecedor atual ou preferencial.

Durante nova Entrada, o usuário pode alterar o Fornecedor atual do Produto.

O Fornecedor deve ser selecionado entre Fornecedores ativos.

A interface deve permitir acesso rápido à criação de Novo Fornecedor conforme as regras dos Cadastros Auxiliares.

Fornecedor desativado não deve ser utilizado em nova Entrada.

---

## 2.18 Fornecedor histórico da Entrada

Cada Entrada deve preservar o Fornecedor utilizado naquela operação.

Exemplo:

Entrada nº 10:
Fornecedor A.

Entrada nº 25:
Fornecedor B.

A alteração do Fornecedor atual do Produto para Fornecedor B não deve reescrever a Entrada nº 10.

O histórico da Entrada deve continuar identificando o Fornecedor A.

---

## 2.19 Produto com mudança de Fornecedor

Um mesmo Produto pode ser adquirido de Fornecedores diferentes ao longo do tempo.

O sistema não deve exigir que todas as Entradas do Produto utilizem o mesmo Fornecedor histórico.

O Fornecedor atual do Produto representa a informação cadastral atual.

O Fornecedor da Entrada representa a origem histórica daquela Entrada.

São informações relacionadas, mas não devem ser tratadas como o mesmo dado histórico.

---

## 2.20 Preço de custo atual

O Produto deve possuir Preço de custo atual.

Durante nova Entrada, o usuário pode alterar o Preço de custo.

O valor informado deve ser:

- numérico;
- finito;
- maior que zero.

O backend deve validar o valor.

---

## 2.21 Alteração do Preço de custo

Quando uma nova Entrada utilizar custo diferente do custo atual, o custo atual do Produto deve ser atualizado para o valor informado na operação mais recente.

Exemplo:

Custo atual:
R$ 80,00.

Nova Entrada:
R$ 90,00.

Após confirmação:

Custo atual do Produto:
R$ 90,00.

O sistema não deve calcular automaticamente custo médio ponderado.

A regra oficial utiliza o custo cadastral mais atual.

---

## 2.22 Valor financeiro do Estoque

O valor financeiro atual do Estoque deve continuar utilizando o custo atual do Produto.

Exemplo:

Estoque disponível:
10.

Custo atual:
R$ 90,00.

Valor financeiro:
R$ 900,00.

A alteração do custo atual pode alterar o valor financeiro atual do Estoque.

Essa regra não altera o custo histórico das Vendas antigas.

---

## 2.23 Custo histórico das Vendas

Vendas antigas devem preservar o custo histórico utilizado na operação.

Exemplo:

Venda realizada quando o custo era:
R$ 80,00.

Nova Entrada altera o custo atual para:
R$ 90,00.

A Venda antiga continua utilizando:
R$ 80,00.

Não recalcular lucro histórico utilizando o custo atual do Produto.

---

## 2.24 Custo histórico da Entrada

Cada Entrada deve preservar o custo unitário informado naquela operação.

Exemplo:

Entrada nº 10:
R$ 80,00 por unidade.

Entrada nº 25:
R$ 90,00 por unidade.

A alteração futura do custo atual não deve reescrever o custo das Entradas anteriores.

---

## 2.25 Preço de venda atual

O Produto deve possuir Preço de venda atual.

Durante uma nova Entrada, o usuário pode alterar o Preço de venda.

O valor informado deve seguir as regras oficiais do Produto.

O backend deve validar o valor.

---

## 2.26 Alteração do Preço de venda

Quando o Preço de venda for alterado durante a Entrada, o cadastro atual do Produto deve ser atualizado.

A alteração vale para:

- novas Vendas;
- Catálogo;
- consultas atuais;
- novas operações que utilizem o preço cadastral atual.

A alteração não deve modificar Vendas antigas.

---

## 2.27 Preço original de novas Vendas

Após alteração do Preço de venda atual, novas Vendas devem utilizar esse valor como Preço original do Produto no momento da Venda.

Exemplo:

Preço anterior:
R$ 199,90.

Nova Entrada altera para:
R$ 219,90.

Nova Venda:
Preço original R$ 219,90.

Venda antiga:
permanece com seu Preço original histórico.

---

## 2.28 Alteração de preço sem reescrita histórica

Alterações de:

- Preço de custo;
- Preço de venda

não devem reescrever operações históricas.

Preservar, conforme a estrutura oficial:

- custo histórico da Venda;
- preço original da Venda;
- preço praticado;
- custo da Entrada;
- valores de Devoluções;
- valores de Trocas.

---

## 2.29 Estoque mínimo

O Estoque mínimo deve seguir a regra oficial já definida para Produtos e Estoque.

O valor padrão deve ser:

0.

O Estoque mínimo pode permanecer em zero.

O usuário não é obrigado a alterar o valor.

O Estoque mínimo não deve gerar alerta.

A Entrada não deve exigir Estoque mínimo maior que zero.

---

## 2.30 Novo Produto sem Entrada válida

Não permitir concluir o cadastro inicial quando a quantidade da primeira Entrada for inválida.

O sistema não deve criar silenciosamente Produto com uma Entrada inválida.

A operação deve informar o erro ao usuário.

---

## 2.31 Produto existente sem quantidade de Entrada

No fluxo de Produto existente, uma operação apresentada como Nova Entrada deve exigir quantidade válida.

Se o usuário desejar apenas editar o cadastro atual sem registrar Entrada, a interface deve diferenciar a ação.

Exemplo:

SALVAR ALTERAÇÕES.

e:

CONFIRMAR ENTRADA.

A edição cadastral não deve gerar movimentação de estoque.

A Entrada deve gerar movimentação de estoque.

---

## 2.32 Separação entre edição e Entrada

O sistema deve distinguir:

Edição cadastral:
altera dados atuais permitidos do Produto.

Entrada:
aumenta o Estoque real e registra histórico.

Quando o usuário alterar dados e informar quantidade de Entrada na mesma operação, o sistema pode confirmar as duas ações conjuntamente.

O histórico deve continuar distinguindo a alteração cadastral da movimentação de estoque.

---

## 2.33 Confirmação de novo Produto

Para Produto novo, a ação principal pode utilizar texto equivalente a:

CADASTRAR E DAR ENTRADA.

A ação deve deixar claro que:

- o Produto será criado;
- a quantidade será adicionada ao estoque.

---

## 2.34 Confirmação de nova Entrada

Para Produto existente com quantidade informada, a ação principal pode utilizar texto equivalente a:

CONFIRMAR ENTRADA.

A confirmação deve registrar a movimentação de estoque.

---

## 2.35 Edição sem Entrada

Quando o Produto existente for apenas editado, utilizar ação equivalente a:

SALVAR ALTERAÇÕES.

Essa ação não deve:

- aumentar estoque;
- reduzir estoque;
- criar Entrada fictícia.

---

## 2.36 Histórico de Entradas

O sistema deve preservar histórico das Entradas.

Cada Entrada deve permitir identificar, no mínimo:

- identificador persistente;
- número da Entrada;
- Produto;
- código histórico relevante;
- quantidade;
- custo unitário da Entrada;
- custo total da Entrada;
- Fornecedor da Entrada;
- data e hora;
- usuário responsável;
- situação.

A estrutura pode preservar informações adicionais necessárias à rastreabilidade.

---

## 2.37 Número da Entrada

Cada Entrada deve possuir número automático.

O número deve ser definido pelo backend.

O usuário não pode escolher ou alterar manualmente o número da Entrada.

A numeração deve seguir a regra de isolamento por loja.

---

## 2.38 Data e hora da Entrada

A Entrada deve registrar a data e hora da confirmação da operação.

O timestamp deve seguir as regras oficiais do sistema.

Novos timestamps devem ser armazenados em UTC com offset explícito.

A apresentação ao usuário deve utilizar:

America/Sao_Paulo.

---

## 2.39 Usuário responsável pela Entrada

A Entrada deve preservar o usuário autenticado responsável pela confirmação.

O usuário deve ser obtido da sessão e do cadastro persistido.

O navegador não deve informar autoritativamente o usuário responsável.

Administrador e Operador podem registrar Entradas.

---

## 2.40 Custo total da Entrada

O custo total da Entrada do Produto deve ser calculado pelo backend.

Fórmula:

Quantidade da Entrada × Custo unitário da Entrada.

Exemplo:

10 unidades × R$ 90,00 =
R$ 900,00.

O backend não deve confiar no custo total enviado pelo navegador.

---

## 2.41 Movimentação de Estoque

Toda Entrada confirmada deve gerar movimentação de Estoque correspondente.

A movimentação deve permitir identificar:

- Produto;
- quantidade adicionada;
- tipo Entrada;
- referência à Entrada;
- usuário;
- data e hora.

Não aumentar estoque sem preservar a origem da movimentação.

---

## 2.42 Atomicidade da Entrada

A confirmação de uma Entrada deve ser atômica.

Quando aplicável, devem ocorrer na mesma operação consistente:

- criação ou atualização do Produto;
- atualização do custo atual;
- atualização do preço de venda atual;
- aumento do estoque;
- criação da Entrada;
- criação da movimentação de Estoque;
- auditoria.

Qualquer falha deve impedir persistência parcial inconsistente.

---

## 2.43 Idempotência da Entrada

A confirmação de Entrada é uma operação com efeito sobre estoque.

O sistema deve possuir proteção contra processamento duplicado da mesma tentativa.

Falha de rede ou reenvio não deve adicionar a mesma quantidade duas vezes.

Exemplo:

Entrada:
10 unidades.

Resposta da rede falha.

Usuário tenta novamente a mesma operação.

O sistema não deve registrar:
20 unidades.

A estratégia deve seguir o padrão oficial de idempotência das operações financeiras e de estoque.

---

## 2.44 Reutilização de chave idempotente

A mesma chave de idempotência com o mesmo conteúdo da Entrada deve retornar o resultado já concluído quando a operação anterior tiver sido processada.

A mesma chave com conteúdo diferente deve ser recusada.

Nova operação consciente deve utilizar nova chave.

---

## 2.45 Cancelamento de Entrada

O cancelamento de Entrada deve ser tratado como evolução específica do módulo.

Não apagar uma Entrada confirmada diretamente.

Até a definição completa das regras de cancelamento, o histórico da Entrada deve ser preservado.

Correções de quantidade física devem utilizar Inventário quando corresponderem a divergência de estoque.

O sistema não deve permitir exclusão silenciosa de Entrada para ajustar estoque.

---

## 2.46 Entrada e Contas a Pagar

Produtos e Entradas e Contas a Pagar continuam sendo módulos distintos.

Uma Entrada aumenta estoque.

Uma Conta a Pagar representa obrigação financeira.

O registro de Entrada não deve criar silenciosamente uma Conta a Pagar sem ação e regra específica.

A integração entre Entrada e Contas a Pagar deve ser definida em evolução própria antes de ser implementada.

---

## 2.47 Entrada e frete

O sistema não deve ratear automaticamente frete entre Produtos sem regra oficial específica.

O custo unitário informado na Entrada representa o custo atual desejado para o Produto.

Despesas adicionais, como frete, devem seguir o fluxo financeiro apropriado quando registradas.

Não inventar custo rateado automaticamente.

---

## 2.48 Busca e leitura de código

A busca pelo código deve funcionar de forma compatível com leitor que opere como entrada de teclado.

O sistema deve evitar múltiplos processamentos da mesma leitura por eventos duplicados da interface.

A leitura deve iniciar a consulta do Produto correspondente.

---

## 2.49 Produto desativado

Quando o código corresponder a Produto desativado, o sistema não deve tratá-lo como Produto novo.

A interface deve informar que o Produto existe e está desativado.

O sistema deve seguir a regra oficial de reativação do Produto.

Não criar segundo Produto com o mesmo código para contornar a desativação.

---

## 2.50 Código único

O Código do Produto deve permanecer único dentro da loja conforme a regra oficial.

A Entrada não deve criar novo Produto quando o código já pertencer a Produto existente.

A validação deve ocorrer no backend.

---

## 2.51 Cadastros Auxiliares durante a Entrada

Durante o cadastro ou edição do Produto, o usuário pode utilizar os fluxos rápidos oficiais para criar:

- Marca;
- Categoria;
- Tamanho;
- Cor;
- Fornecedor.

Após criação válida, o novo cadastro auxiliar pode ser selecionado no Produto em montagem.

A criação do cadastro auxiliar não deve confirmar automaticamente o Produto ou a Entrada.

---

## 2.52 Permissões

Administrador e Operador podem acessar Produtos e Entradas.

Ambos podem:

- cadastrar Produto;
- editar Produto;
- registrar Entrada;
- alterar Fornecedor atual;
- alterar Preço de custo;
- alterar Preço de venda;
- utilizar Cadastros Auxiliares permitidos.

As permissões especiais exclusivas do Administrador continuam limitadas às regras oficiais já definidas.

---

## 2.53 Histórico e auditoria

Alterações e Entradas devem preservar rastreabilidade.

Quando a estrutura geral de auditoria suportar a ação, registrar:

- tipo da operação;
- Produto;
- usuário;
- data e hora;
- referência da Entrada.

Alterações relevantes de:

- custo;
- preço de venda;
- Fornecedor

devem ser identificáveis historicamente quando realizadas junto à Entrada.

---

## 2.54 Apresentação da tela

A tela Produtos e Entradas deve priorizar o fluxo pelo Código do Produto.

Estrutura conceitual:

PRODUTOS E ENTRADAS.

Código do Produto.

Após consulta:

DADOS DO PRODUTO.

PREÇOS.

ESTOQUE.

NOVA ENTRADA.

Para Produto existente, apresentar:

Estoque real atual.

Reservado.

Disponível.

Quantidade desta Entrada.

Estoque após Entrada.

---

## 2.55 Estado de Produto novo

Quando o Produto for novo, a interface deve deixar claro:

NOVO PRODUTO.

Os campos necessários devem ser disponibilizados para preenchimento.

A ação principal deve utilizar texto equivalente a:

CADASTRAR E DAR ENTRADA.

---

## 2.56 Estado de Produto existente

Quando o Produto já existir, a interface deve deixar claro:

PRODUTO JÁ CADASTRADO.

Os dados atuais devem ser carregados.

A interface deve permitir:

- edição cadastral;
- atualização de preços;
- alteração de Fornecedor;
- registro de nova Entrada.

---

## 2.57 Prévia da operação

Antes da confirmação da Entrada, a interface deve apresentar de forma clara:

- Estoque atual;
- Quantidade da Entrada;
- Estoque após Entrada.

Quando houver alteração de custo, pode apresentar:

Custo atual:
R$ 80,00.

Novo custo:
R$ 90,00.

Quando houver alteração de preço de venda, pode apresentar:

Preço de venda atual:
R$ 199,90.

Novo preço de venda:
R$ 219,90.

---

## 2.58 Regras gerais de Produtos e Entradas

O sistema deve:

- centralizar cadastro de Produtos e Entradas;
- utilizar o Código do Produto como ponto inicial do fluxo;
- consultar a existência do Produto no backend;
- iniciar Novo Produto quando o código não existir;
- carregar o Produto atual quando o código existir;
- permitir primeira Entrada junto ao cadastro;
- permitir nova Entrada de Produto existente;
- exigir quantidade inteira e maior que zero;
- apresentar Estoque real atual;
- apresentar Estoque reservado;
- apresentar Estoque disponível;
- apresentar Estoque após Entrada;
- não permitir edição direta do Estoque atual;
- utilizar Inventário para correções de estoque;
- permitir edição cadastral durante nova Entrada;
- permitir alteração do Fornecedor atual;
- preservar o Fornecedor histórico da Entrada;
- permitir Fornecedores diferentes entre Entradas;
- permitir alteração do Preço de custo;
- utilizar o custo mais atual no cadastro do Produto;
- não utilizar custo médio ponderado;
- utilizar custo atual no valor financeiro do Estoque;
- preservar custo histórico das Vendas;
- preservar custo histórico das Entradas;
- permitir alteração do Preço de venda;
- aplicar novo Preço de venda às operações futuras;
- preservar preços históricos das Vendas;
- manter Estoque mínimo padrão zero;
- permitir Estoque mínimo zero;
- não emitir alerta de Estoque mínimo;
- diferenciar Edição cadastral de Entrada;
- não gerar movimentação de Estoque em edição simples;
- gerar movimentação em toda Entrada;
- numerar Entradas automaticamente;
- registrar data e hora;
- registrar usuário responsável;
- calcular custo total no backend;
- utilizar proteção transacional;
- proteger a Entrada contra duplicidade;
- preservar histórico;
- não excluir Entrada silenciosamente;
- não criar Conta a Pagar automaticamente sem regra específica;
- não ratear frete automaticamente;
- suportar leitura de código;
- não tratar Produto desativado como Produto novo;
- preservar unicidade do Código;
- permitir Cadastros Auxiliares rápidos;
- permitir acesso a Administrador e Operador;
- preservar auditoria e rastreabilidade.

## 2.59 Integração entre Entrada e Contas a Pagar

A Entrada de Produtos e a Conta a Pagar são operações distintas, porém podem possuir vínculo entre si.

A Entrada representa o recebimento físico de mercadorias e o aumento do estoque.

A Conta a Pagar representa a obrigação financeira relacionada ao fornecedor.

O sistema pode criar uma ou mais Contas a Pagar vinculadas a uma Entrada confirmada.

A criação da Conta a Pagar é opcional.

---

## 2.60 Pergunta para gerar Conta a Pagar

Após a confirmação válida de uma Entrada, o sistema deve permitir a opção:

GERAR CONTA A PAGAR PARA ESTA ENTRADA.

O usuário pode escolher:

- gerar uma ou mais Contas a Pagar;
- não gerar Conta a Pagar.

A ausência de Conta a Pagar não invalida a Entrada.

A Entrada física permanece confirmada independentemente da criação da obrigação financeira.

---

## 2.61 Situações sem Conta a Pagar vinculada

Uma Entrada pode permanecer sem Conta a Pagar vinculada.

Exemplos:

- mercadoria já paga;
- compra registrada financeiramente por outro fluxo válido;
- obrigação ainda não cadastrada;
- entrada operacional legítima sem obrigação vinculada.

O sistema não deve criar Conta a Pagar automaticamente sem confirmação do usuário.

---

## 2.62 Vínculo persistente

Quando uma Conta a Pagar for criada a partir de uma Entrada, o vínculo deve ser persistido.

Nos detalhes da Entrada, deve ser possível identificar as Contas a Pagar vinculadas.

Nos detalhes da Conta a Pagar, deve ser possível identificar a Entrada de origem.

Exemplo:

Entrada:
Entrada nº 125.

Conta a Pagar:
Origem — Entrada nº 125.

O vínculo deve utilizar identificadores persistentes.

Não utilizar somente número visual, descrição ou nome do fornecedor como vínculo autoritativo.

---

## 2.63 Valor sugerido da obrigação

Ao iniciar a criação de Conta a Pagar a partir de uma Entrada, o sistema deve calcular o custo total da Entrada.

O custo total deve utilizar:

Quantidade da Entrada × Custo unitário histórico da Entrada.

Quando a Entrada possuir vários itens, somar os custos totais dos itens.

Exemplo:

10 Camisetas × R$ 50,00 =
R$ 500,00.

5 Calções × R$ 40,00 =
R$ 200,00.

Custo total da Entrada:
R$ 700,00.

O sistema deve sugerir R$ 700,00 como valor inicial da obrigação.

---

## 2.64 Valor sugerido não é obrigatório

O valor calculado da Entrada deve ser apresentado como sugestão para a Conta a Pagar.

O usuário pode alterar o valor da obrigação antes da confirmação.

Exemplos de diferença podem ocorrer por:

- desconto comercial;
- bonificação;
- ajuste da nota;
- imposto;
- frete tratado separadamente;
- outro acordo financeiro com o fornecedor.

O sistema não deve obrigar que o valor da Conta seja idêntico ao custo total da Entrada.

---

## 2.65 Alteração do valor financeiro da Conta

Alterar o valor da Conta a Pagar não deve alterar os custos unitários dos Produtos.

Exemplo:

Custo total histórico da Entrada:
R$ 5.000,00.

Conta a Pagar:
R$ 4.800,00.

Os custos unitários informados na Entrada permanecem preservados.

O sistema não deve ratear automaticamente a diferença de R$ 200,00 entre os Produtos.

A obrigação financeira e o custo cadastral da mercadoria são informações distintas.

---

## 2.66 Proibição de rateio automático

O sistema não deve recalcular automaticamente o custo dos Produtos para forçar igualdade entre:

- custo total da Entrada;
- valor das Contas a Pagar.

Não criar rateio automático de:

- descontos do fornecedor;
- bonificações;
- impostos;
- fretes;
- diferenças de nota.

Qualquer futura regra de apropriação desses valores ao custo dos Produtos exige definição específica.

---

## 2.67 Várias Contas a Pagar por Entrada

Uma única Entrada pode possuir várias Contas a Pagar vinculadas.

Exemplo:

Entrada nº 125.

Custo total:
R$ 9.000,00.

Contas vinculadas:

Conta 1:
R$ 3.000,00.
Vencimento 10/08/2026.

Conta 2:
R$ 3.000,00.
Vencimento 10/09/2026.

Conta 3:
R$ 3.000,00.
Vencimento 10/10/2026.

A Entrada permanece uma única operação física.

As Contas representam obrigações financeiras separadas.

---

## 2.68 Cadastro individual das Contas vinculadas

Cada Conta a Pagar vinculada deve possuir seu próprio cadastro.

Cada Conta deve preservar, conforme as regras do módulo Contas a Pagar:

- fornecedor;
- categoria;
- descrição;
- valor;
- data de emissão;
- data de vencimento;
- observações;
- status;
- pagamentos.

As Contas não devem ser tratadas como parcelas internas de uma única entidade sem identidade própria.

---

## 2.69 Soma das Contas vinculadas

A soma das Contas a Pagar vinculadas não precisa ser exatamente igual ao custo total da Entrada.

O sistema deve permitir diferença.

A diferença não bloqueia automaticamente a operação.

O sistema deve apresentar comparação entre:

- custo total da Entrada;
- total das Contas vinculadas;
- diferença.

---

## 2.70 Exemplo de diferença

Exemplo:

Custo total da Entrada:
R$ 9.000,00.

Total das Contas vinculadas:
R$ 8.500,00.

Diferença:
R$ 500,00.

O sistema deve apresentar a diferença de forma clara.

A diferença não deve ser automaticamente classificada como erro.

Pode representar, por exemplo:

- desconto;
- bonificação;
- valor já pago;
- outra condição comercial.

---

## 2.71 Diferença negativa

Quando o total das Contas vinculadas for superior ao custo total da Entrada, o sistema também deve apresentar a diferença.

Exemplo:

Custo total da Entrada:
R$ 9.000,00.

Contas vinculadas:
R$ 9.500,00.

Diferença:
R$ -500,00 em relação ao custo da Entrada.

A interface deve apresentar a situação de maneira compreensível.

O sistema não deve corrigir automaticamente os custos dos Produtos.

---

## 2.72 Conta já paga no momento da Entrada

Não deve existir fluxo especial de Conta já paga dentro da Entrada.

Quando a mercadoria já tiver sido paga, o usuário pode:

- não gerar Conta a Pagar;
- criar a Conta a Pagar e registrar o pagamento através do fluxo normal de Contas a Pagar.

O pagamento deve seguir as regras oficiais do módulo financeiro.

Não duplicar o fluxo de pagamento dentro de Produtos e Entradas.

---

## 2.73 Centralização do pagamento

O pagamento de Contas vinculadas à Entrada deve ser realizado no módulo Contas a Pagar.

Produtos e Entradas não devem:

- receber pagamento da Conta;
- gerar saída financeira diretamente;
- marcar Conta como paga;
- criar pagamento parcial.

A Entrada pode apresentar o status financeiro das Contas vinculadas.

As operações de pagamento permanecem centralizadas no módulo Contas a Pagar.

---

## 2.74 Fornecedor da Conta vinculada

Quando uma Conta a Pagar for originada de uma Entrada, o Fornecedor deve ser obtido da Entrada correspondente.

O campo deve ser preenchido automaticamente.

O usuário não deve trocar o Fornecedor por outro na Conta vinculada.

A Conta deve preservar o mesmo Fornecedor histórico da Entrada.

---

## 2.75 Proibição de alteração do Fornecedor

Conta a Pagar vinculada a uma Entrada não pode ser alterada para outro Fornecedor.

Exemplo:

Entrada:
Fornecedor A.

Conta vinculada:
Fornecedor A.

Não permitir alterar para:
Fornecedor B.

Quando o vínculo estiver incorreto por erro operacional, a correção deve seguir fluxo rastreável adequado.

O sistema não deve quebrar silenciosamente o vínculo histórico.

---

## 2.76 Categoria da Conta vinculada

Conta a Pagar originada de Entrada deve utilizar automaticamente a Categoria de Despesa:

Mercadorias.

A Categoria deve ser definida pelo sistema.

---

## 2.77 Categoria Mercadorias fixa

A Categoria Mercadorias não deve ser alterável na Conta vinculada a uma Entrada.

A origem física da obrigação é uma compra de mercadorias.

Não permitir trocar a Categoria para:

- Energia;
- Aluguel;
- Serviços;
- Outra Categoria.

Contas não originadas de Entrada continuam seguindo as regras normais de Categoria.

---

## 2.78 Descrição sugerida

A Conta vinculada pode receber descrição automática ou sugerida.

Exemplo:

Compra de mercadorias — Entrada nº 125.

O usuário pode complementar a descrição antes da confirmação quando permitido.

A descrição não substitui o vínculo persistente com a Entrada.

---

## 2.79 Data de emissão

A Conta vinculada deve permitir informar a Data de emissão.

Quando existir data de compra ou emissão registrada na Entrada, essa data pode ser sugerida.

A Data de emissão deve seguir as regras de data civil.

O usuário pode confirmar a informação antes da criação da Conta.

---

## 2.80 Vencimento

Cada Conta vinculada deve possuir sua própria Data de vencimento.

O usuário deve informar o vencimento de cada obrigação.

O sistema não deve gerar vencimentos automáticos de 30 dias como regra de Contas a Pagar.

O parcelamento e os vencimentos dependem do acordo com o Fornecedor.

---

## 2.81 Contas vinculadas e pagamentos parciais

Contas vinculadas à Entrada podem receber pagamentos:

- totais;
- parciais.

O pagamento deve seguir as regras oficiais de Contas a Pagar.

A existência do vínculo com a Entrada não altera as formas de pagamento permitidas.

Continuam permitidas:

- Dinheiro;
- Pix;
- Débito.

Crédito não é forma permitida para pagamento de Conta a Pagar.

---

## 2.82 Juros, multa e desconto

Contas vinculadas à Entrada podem possuir, no momento do pagamento:

- juros;
- multa;
- desconto.

Esses valores devem seguir as regras oficiais de Contas a Pagar.

Juros, multas ou descontos não alteram retroativamente:

- custo unitário da Entrada;
- custo atual do Produto;
- estoque.

---

## 2.83 Resumo financeiro da Entrada

Os detalhes da Entrada devem apresentar resumo financeiro das Contas vinculadas.

O resumo deve apresentar:

- custo total da Entrada;
- total das Contas vinculadas;
- total pago;
- saldo pendente;
- diferença entre custo total da Entrada e Contas vinculadas.

Os valores devem utilizar o estado atual válido das Contas.

---

## 2.84 Total das Contas vinculadas

O Total das Contas vinculadas representa a soma dos valores originais válidos das Contas vinculadas à Entrada.

Contas canceladas devem ser tratadas conforme sua situação oficial.

O resumo deve deixar claro se valores cancelados estão ou não compondo o total apresentado.

Minha recomendação é utilizar somente Contas válidas e não canceladas nos totais financeiros atuais.

O histórico das Contas canceladas permanece disponível separadamente.

---

## 2.85 Total pago

O Total pago deve considerar os pagamentos válidos das Contas vinculadas.

Pagamentos parciais devem ser somados.

Estornos devem ser considerados.

Não utilizar somente o status textual da Conta para determinar o Total pago.

---

## 2.86 Saldo pendente

O Saldo pendente deve utilizar o saldo líquido atual das Contas vinculadas.

O cálculo deve considerar:

- valor original;
- pagamentos;
- juros e multas oficialmente incorporados;
- descontos;
- estornos;
- cancelamentos.

O sistema deve utilizar a mesma regra autoritativa do módulo Contas a Pagar.

---

## 2.87 Diferença entre Entrada e obrigações

A diferença deve ser calculada conceitualmente como:

Total das Contas válidas vinculadas - Custo total histórico da Entrada.

A apresentação deve identificar se as obrigações vinculadas estão:

- abaixo;
- iguais;
- acima

do custo total da Entrada.

O valor possui finalidade de conferência.

Não produz movimentação financeira automática.

---

## 2.88 Cancelamento de Entrada com Contas pendentes

Quando uma Entrada possuir apenas Contas vinculadas pendentes e sem pagamento, o cancelamento válido da Entrada pode cancelar automaticamente essas Contas.

O cancelamento deve preservar:

- Entrada;
- Contas;
- vínculos;
- histórico.

As Contas devem assumir situação Cancelada.

Não excluir os registros.

---

## 2.89 Requisitos para cancelamento automático das Contas

O cancelamento automático de Conta vinculada somente pode ocorrer quando a Conta:

- não possuir pagamento válido;
- não possuir efeito financeiro efetivamente realizado que dependa de estorno.

A validação deve ocorrer no backend.

Não confiar apenas no status visual da Conta.

---

## 2.90 Entrada com Conta parcialmente paga

Quando existir Conta vinculada parcialmente paga, a Entrada não pode ser cancelada diretamente.

O sistema deve impedir o cancelamento e informar a existência de pagamento financeiro.

Exemplo:

Não é possível cancelar esta Entrada.

A Conta nº X possui pagamentos registrados.

O usuário deve tratar primeiro a situação financeira correspondente.

---

## 2.91 Entrada com Conta totalmente paga

Quando existir Conta vinculada totalmente paga, a Entrada não pode ser cancelada diretamente.

O sistema deve impedir a operação.

O pagamento deve ser tratado pelo fluxo oficial de estorno ou correção de Contas a Pagar antes de nova tentativa de cancelamento da Entrada.

Não apagar pagamento.

Não gerar estorno financeiro automaticamente sem fluxo formal.

---

## 2.92 Várias Contas e cancelamento da Entrada

Quando uma Entrada possuir várias Contas vinculadas, todas devem ser verificadas antes do cancelamento.

Exemplo:

Conta A:
Pendente, sem pagamento.

Conta B:
Parcialmente paga.

Resultado:

A Entrada não pode ser cancelada.

O sistema não deve cancelar apenas a Conta A e deixar a operação em estado financeiro parcial sem regra específica.

---

## 2.93 Validação financeira antes do cancelamento

Antes de cancelar Entrada, o backend deve recalcular a situação atual das Contas vinculadas.

A validação deve ocorrer utilizando os dados persistidos mais recentes.

Não confiar no estado carregado anteriormente pelo navegador.

A concorrência com pagamento de Conta deve ser tratada de forma transacionalmente segura.

---

## 2.94 Cancelamento da Entrada e estoque

As regras de cancelamento da Entrada sobre estoque continuam seguindo o módulo Produtos e Entradas.

O sistema deve validar se existe estoque suficiente para reverter as quantidades da Entrada.

O cancelamento financeiro das Contas vinculadas não substitui a validação de estoque.

A Entrada somente pode ser cancelada quando todas as condições físicas e financeiras forem atendidas.

---

## 2.95 Atomicidade do cancelamento

Quando o cancelamento da Entrada for permitido, a operação deve ser atômica.

Devem ser tratados de forma consistente:

- cancelamento da Entrada;
- reversão válida do estoque;
- movimentação de estoque;
- cancelamento das Contas vinculadas sem pagamento;
- histórico;
- auditoria.

Falha em qualquer etapa deve evitar estado parcial.

---

## 2.96 Cancelamento da Conta vinculada

O cancelamento de uma Conta a Pagar vinculada não cancela a Entrada.

A Conta representa obrigação financeira.

A Entrada representa recebimento físico de Produto.

São operações distintas.

---

## 2.97 Efeito do cancelamento da Conta no estoque

Cancelar Conta a Pagar vinculada não deve:

- reduzir estoque;
- aumentar estoque;
- cancelar Entrada;
- alterar quantidade da Entrada.

O estoque não deve ser modificado por cancelamento isolado da obrigação financeira.

---

## 2.98 Entrada após cancelamento da Conta

Quando uma Conta vinculada for cancelada e a Entrada permanecer válida, os Produtos continuam no estoque conforme os efeitos da Entrada.

Os detalhes da Entrada devem identificar a Conta como Cancelada.

O resumo financeiro deve recalcular os totais atuais conforme a regra de Contas válidas.

---

## 2.99 Nova Conta após cancelamento de Conta vinculada

Quando necessário, o usuário pode criar nova Conta a Pagar vinculada à mesma Entrada.

A nova Conta deve possuir identidade própria.

O sistema não deve reativar silenciosamente uma Conta cancelada quando a intenção for criar uma nova obrigação.

O histórico deve preservar ambas as Contas.

---

## 2.100 Relatório de Entradas

Os Relatórios devem possuir visão de Entradas de Produtos conforme as regras oficiais do módulo Relatórios.

O Relatório de Entradas deve permitir análise das movimentações de compra e recebimento de mercadorias.

---

## 2.101 Filtros do Relatório de Entradas

O Relatório de Entradas deve permitir filtros por:

- período;
- Fornecedor;
- Produto;
- Código;
- com Conta a Pagar;
- sem Conta a Pagar;
- com saldo pendente;
- integralmente pagas.

Os filtros podem ser utilizados em conjunto.

---

## 2.102 Entrada com Conta a Pagar

O filtro Com Conta a Pagar deve apresentar Entradas que possuam pelo menos uma Conta vinculada válida ou histórica conforme a regra de apresentação.

A interface deve deixar claro se Contas canceladas são consideradas na definição do filtro.

Minha recomendação é utilizar Contas não canceladas para o filtro operacional atual.

Contas canceladas permanecem identificáveis nos detalhes.

---

## 2.103 Entrada sem Conta a Pagar

O filtro Sem Conta a Pagar deve apresentar Entradas sem Conta válida vinculada.

Entrada que possua somente Contas canceladas pode ser considerada sem obrigação ativa vinculada para fins operacionais.

O histórico das Contas canceladas permanece preservado.

---

## 2.104 Entrada com saldo pendente

O filtro Com saldo pendente deve utilizar o saldo líquido atual das Contas vinculadas.

Apresentar Entrada quando a soma dos saldos pendentes válidos for maior que zero.

Não utilizar somente o status textual Pendente.

---

## 2.105 Entrada integralmente paga

O filtro Integralmente pagas deve apresentar Entradas cujas Contas válidas vinculadas possuam saldo pendente total igual a zero e possuam obrigações financeiras vinculadas.

Entrada sem nenhuma Conta a Pagar não deve ser classificada automaticamente como Integralmente paga.

Ela deve permanecer classificada como Entrada sem Conta a Pagar.

---

## 2.106 Colunas do Relatório de Entradas

O Relatório de Entradas deve apresentar, no mínimo:

- número da Entrada;
- data e hora;
- Fornecedor;
- quantidade total de peças;
- custo total da Entrada;
- total das Contas vinculadas;
- total pago;
- saldo pendente;
- situação da Entrada;
- situação financeira vinculada.

A listagem deve permitir abrir os detalhes da Entrada.

---

## 2.107 Situação financeira da Entrada

A situação financeira vinculada pode apresentar, conforme o estado atual:

- Sem Conta a Pagar;
- Com saldo pendente;
- Integralmente paga.

Contas canceladas devem ser consideradas conforme as regras atuais de saldo e obrigação válida.

A situação financeira não substitui a situação operacional da Entrada.

---

## 2.108 Detalhes das Contas vinculadas

Nos detalhes da Entrada, listar as Contas vinculadas.

Para cada Conta, apresentar:

- identificação;
- descrição;
- valor;
- vencimento;
- total pago;
- saldo;
- status;
- ação para visualizar a Conta.

As informações devem utilizar os dados atuais oficiais da Conta.

---

## 2.109 Entrada nos detalhes da Conta

Nos detalhes da Conta a Pagar originada de Entrada, apresentar:

Origem:
Entrada nº X.

Deve existir ação para visualizar a Entrada correspondente quando a interface permitir navegação entre módulos.

---

## 2.110 Impressão e documentos

A impressão ou PDF de detalhes da Entrada deve permitir identificar as Contas vinculadas.

O documento pode apresentar:

- custo total da Entrada;
- total das Contas vinculadas;
- total pago;
- saldo pendente.

A geração deve seguir as regras oficiais de Impressões e Documentos Gerados.

---

## 2.111 Permissões

Administrador e Operador podem gerar Contas a Pagar a partir de Entradas.

Ambos podem consultar os vínculos.

O pagamento das Contas continua seguindo as permissões oficiais do módulo Contas a Pagar.

Não existe restrição adicional de perfil para a integração Entrada ↔ Conta a Pagar.

---

## 2.112 Segurança e fonte autoritativa

O backend deve validar:

- existência da Entrada;
- loja;
- Fornecedor da Entrada;
- custo total histórico da Entrada;
- Contas já vinculadas;
- situação das Contas;
- pagamentos;
- saldos.

O navegador não deve informar autoritativamente:

- custo total da Entrada;
- Fornecedor da Conta vinculada;
- Categoria Mercadorias;
- total pago;
- saldo pendente.

Esses dados devem ser obtidos ou recalculados pelo backend.

---

## 2.113 Concorrência

A criação de Conta vinculada e o cancelamento da Entrada devem considerar operações concorrentes.

Exemplo:

Usuário A inicia cancelamento da Entrada.

Usuário B paga uma Conta vinculada.

O cancelamento não deve concluir utilizando um estado financeiro antigo.

A validação final deve ocorrer dentro da operação protegida.

---

## 2.114 Idempotência

A criação de Contas a Pagar vinculadas deve possuir proteção contra processamento duplicado quando fizer parte de uma confirmação com efeito persistente.

Retry ou clique duplicado não devem criar duas Contas idênticas involuntariamente para a mesma tentativa.

A estratégia deve seguir o padrão oficial de idempotência das operações críticas.

---

## 2.115 Regras gerais da integração Entrada e Contas a Pagar

O sistema deve:

- permitir geração opcional de Conta a Pagar após Entrada;
- não criar Conta automaticamente sem confirmação;
- preservar Entrada sem Conta a Pagar;
- vincular Conta e Entrada por identificadores persistentes;
- mostrar a Conta nos detalhes da Entrada;
- mostrar a Entrada nos detalhes da Conta;
- calcular custo total da Entrada no backend;
- sugerir o custo total como valor da obrigação;
- permitir alteração do valor sugerido;
- não alterar custos dos Produtos quando o valor da Conta mudar;
- não ratear automaticamente diferenças;
- permitir várias Contas por Entrada;
- manter cada Conta como cadastro individual;
- não exigir igualdade entre custo da Entrada e total das Contas;
- apresentar diferenças;
- não criar fluxo especial de Conta já paga dentro da Entrada;
- manter pagamentos centralizados em Contas a Pagar;
- utilizar o Fornecedor da Entrada na Conta vinculada;
- impedir alteração do Fornecedor da Conta vinculada;
- utilizar Categoria Mercadorias;
- impedir alteração da Categoria Mercadorias em Conta vinculada;
- permitir descrição complementar;
- permitir Data de emissão;
- permitir vencimento individual por Conta;
- permitir pagamentos totais;
- permitir pagamentos parciais;
- permitir juros;
- permitir multas;
- permitir descontos;
- não alterar custos históricos por juros, multas ou descontos;
- apresentar resumo financeiro da Entrada;
- mostrar custo total;
- mostrar total das Contas;
- mostrar total pago;
- mostrar saldo pendente;
- mostrar diferença;
- cancelar automaticamente Contas pendentes e sem pagamento quando a Entrada puder ser cancelada;
- impedir cancelamento da Entrada quando houver Conta parcialmente paga;
- impedir cancelamento da Entrada quando houver Conta totalmente paga;
- validar todas as Contas antes do cancelamento;
- recalcular a situação financeira no backend;
- validar estoque separadamente;
- executar cancelamento permitido de forma atômica;
- não cancelar Entrada ao cancelar Conta;
- não alterar estoque ao cancelar Conta;
- permitir nova Conta vinculada após cancelamento de Conta anterior;
- preservar histórico;
- possuir Relatório de Entradas;
- permitir filtros financeiros;
- distinguir Entrada sem Conta e Entrada integralmente paga;
- apresentar situação financeira;
- permitir navegação entre Entrada e Conta;
- respeitar permissões;
- utilizar backend como fonte autoritativa;
- proteger operações concorrentes;
- utilizar idempotência nas operações críticas.

## 2.116 Cancelamento de Entrada

Uma Entrada confirmada pode ser cancelada somente por meio de operação formal de cancelamento.

A Entrada não deve ser excluída.

O cancelamento deve preservar:

- Entrada original;
- itens;
- quantidades;
- custos históricos;
- Fornecedor;
- usuário da Entrada;
- data e hora da Entrada;
- Contas a Pagar vinculadas;
- histórico.

O cancelamento produz uma reversão operacional da Entrada.

---

## 2.117 Regra de estoque para cancelamento

O cancelamento da Entrada somente pode ocorrer quando o Estoque real atual possuir quantidade suficiente para reverter integralmente todas as quantidades originalmente recebidas.

A validação deve ser realizada por Produto.

Exemplo:

Entrada:
10 unidades.

Estoque real atual:
12 unidades.

Resultado:

Cancelamento permitido.

Após a reversão:

Estoque real:
2 unidades.

O sistema não precisa identificar fisicamente se as unidades restantes pertencem ao lote específico da Entrada cancelada.

A regra utiliza a disponibilidade quantitativa atual necessária para impedir estoque negativo.

---

## 2.118 Ausência de controle físico por lote

O sistema não possui controle físico obrigatório de lote por Entrada.

Por esse motivo, o cancelamento utiliza uma regra quantitativa operacional.

Exemplo:

Entrada A:
10 unidades.

Entrada B:
5 unidades.

Vendas e outras saídas:
8 unidades.

Estoque real atual:
7 unidades.

O sistema não deve afirmar quais unidades físicas pertencem à Entrada A ou à Entrada B.

A validação do cancelamento considera somente se o estoque real atual é suficiente para realizar a reversão integral da Entrada selecionada.

---

## 2.119 Validação de todos os itens

Quando a Entrada possuir vários Produtos, todos os itens devem possuir estoque real suficiente para reversão.

Exemplo:

Entrada:

Produto A:
10 unidades.

Produto B:
5 unidades.

Estoque real atual:

Produto A:
12 unidades.

Produto B:
2 unidades.

Resultado:

O cancelamento integral da Entrada deve ser recusado.

A quantidade insuficiente do Produto B impede o cancelamento completo.

---

## 2.120 Cancelamento integral

O cancelamento da Entrada deve ser integral.

Não permitir cancelamento parcial da quantidade de uma Entrada.

Exemplo:

Entrada original:
10 unidades.

Não permitir cancelar somente:
3 unidades.

O cancelamento deve desfazer integralmente as quantidades registradas na Entrada.

---

## 2.121 Correção de quantidade registrada incorretamente

Quando a quantidade física estiver divergente e o objetivo não for desfazer integralmente a Entrada, o usuário deve utilizar o Inventário.

Exemplo:

Entrada registrada:
10 unidades.

Quantidade física correta:
7 unidades.

Se a Entrada não puder ou não deva ser integralmente cancelada, a diferença deve ser tratada pelo fluxo oficial de Inventário.

O Inventário deve registrar:

- quantidade anterior;
- quantidade física;
- diferença;
- motivo;
- usuário;
- data e hora.

Não utilizar cancelamento parcial de Entrada como substituto do Inventário.

---

## 2.122 Motivo obrigatório do cancelamento

Todo cancelamento de Entrada exige motivo.

Os motivos iniciais podem incluir:

- Entrada duplicada;
- Lançamento incorreto;
- Operação cadastrada por engano;
- Outro.

Quando o motivo for Outro, a descrição complementar é obrigatória.

O sistema não deve concluir cancelamento sem motivo válido.

---

## 2.123 Mercadoria devolvida ao Fornecedor

A devolução física de mercadoria ao Fornecedor não deve ser tratada automaticamente como cancelamento de Entrada.

Quando a Entrada original foi corretamente registrada e, posteriormente, parte ou toda a mercadoria for devolvida ao Fornecedor, deve existir operação específica de:

DEVOLUÇÃO AO FORNECEDOR.

Exemplo:

Entrada correta:
10 unidades.

Posteriormente devolvidas ao Fornecedor:
3 unidades.

A Entrada original permanece válida.

A operação deve ser registrada como Devolução ao Fornecedor.

---

## 2.124 Diferença entre Cancelamento e Devolução ao Fornecedor

Cancelamento de Entrada:

- desfaz integralmente uma Entrada;
- é utilizado para operação duplicada, incorreta ou cadastrada por engano;
- exige estoque suficiente para reversão integral;
- não permite cancelamento parcial.

Devolução ao Fornecedor:

- ocorre após uma Entrada válida;
- pode envolver parte das quantidades;
- representa saída física de mercadoria em direção ao Fornecedor;
- possui histórico próprio.

O sistema deve preservar essa diferença.

---

## 2.125 Contas a Pagar vinculadas

Antes do cancelamento da Entrada, o backend deve verificar todas as Contas a Pagar vinculadas.

O sistema deve considerar:

- situação;
- pagamentos;
- estornos;
- saldo;
- efeitos financeiros já realizados.

Não confiar somente no status visual da Conta.

---

## 2.126 Contas sem pagamento

Quando todas as Contas a Pagar vinculadas estiverem sem qualquer pagamento válido, o cancelamento da Entrada pode cancelar automaticamente essas Contas.

As Contas devem assumir situação:

Cancelada.

Os registros devem permanecer preservados.

Não excluir as Contas.

---

## 2.127 Cancelamento automático de todas as Contas elegíveis

Quando o cancelamento da Entrada for permitido, todas as Contas vinculadas elegíveis devem ser canceladas automaticamente na mesma operação.

O sistema não deve perguntar individualmente:

Cancelar Conta A?

Cancelar Conta B?

Cancelar Conta C?

As Contas vinculadas sem pagamento devem acompanhar a reversão integral da Entrada.

---

## 2.128 Conta parcialmente paga

Quando qualquer Conta vinculada possuir pagamento parcial válido, o cancelamento da Entrada deve ser recusado.

O sistema deve informar que existem efeitos financeiros já realizados.

Exemplo:

Não é possível cancelar esta Entrada.

A Conta nº 125 possui pagamento registrado.

O usuário deve tratar primeiro a situação financeira no módulo Contas a Pagar.

---

## 2.129 Conta integralmente paga

Quando qualquer Conta vinculada estiver integralmente paga, o cancelamento da Entrada deve ser recusado.

O sistema não deve:

- apagar o pagamento;
- devolver dinheiro automaticamente;
- criar estorno silencioso.

O usuário deve utilizar o fluxo oficial de estorno ou correção financeira antes de nova tentativa de cancelamento.

---

## 2.130 Validação conjunta das Contas

Quando existirem várias Contas vinculadas, todas devem ser validadas.

Exemplo:

Conta A:
Pendente e sem pagamento.

Conta B:
Parcialmente paga.

Resultado:

O cancelamento da Entrada deve ser recusado.

O sistema não deve cancelar parcialmente apenas a Conta A e deixar a Entrada em estado intermediário inconsistente.

---

## 2.131 Custo atual após cancelamento

O cancelamento da Entrada não deve restaurar automaticamente o Preço de custo anterior do Produto.

Exemplo:

Antes da Entrada:

Custo atual:
R$ 80,00.

Na Entrada cancelada:

Novo custo:
R$ 90,00.

Após cancelamento da Entrada:

O sistema não deve assumir automaticamente que o custo atual deve voltar para R$ 80,00.

O custo atual permanece com o valor vigente no cadastro no momento do cancelamento.

---

## 2.132 Motivo para não restaurar o custo automaticamente

Outras operações podem ter ocorrido após a Entrada.

Exemplo:

Entrada A altera custo:
R$ 80,00 para R$ 90,00.

Entrada B posterior altera custo:
R$ 90,00 para R$ 95,00.

Posteriormente, Entrada A é cancelada.

O sistema não pode retornar o custo atual para R$ 80,00.

Isso apagaria o efeito cadastral da Entrada B.

Por esse motivo, cancelamento de Entrada não restaura automaticamente custo atual.

---

## 2.133 Preço de venda após cancelamento

O cancelamento da Entrada não deve restaurar automaticamente o Preço de venda anterior.

Exemplo:

Preço anterior:
R$ 199,90.

Na Entrada:
Preço alterado para R$ 219,90.

Outras operações podem ter ocorrido posteriormente.

Após o cancelamento da Entrada, o Preço de venda atual permanece conforme o cadastro vigente.

Não reverter automaticamente o preço.

---

## 2.134 Cancelamento e histórico de preços

Mesmo quando a Entrada for cancelada, o histórico deve preservar que naquela operação houve informação de custo e preço correspondente.

O cancelamento não deve reescrever silenciosamente o histórico da Entrada.

Os valores atuais do Produto são independentes da reversão quantitativa da Entrada.

---

## 2.135 Produto criado junto à Entrada cancelada

Quando um Produto tiver sido criado junto com sua primeira Entrada e essa Entrada for posteriormente cancelada, o Produto deve permanecer cadastrado.

O Produto não deve ser excluído automaticamente.

Exemplo:

Novo Produto criado.

Primeira Entrada:
10 unidades.

Entrada cancelada.

Novo estoque real:
0.

O Produto permanece cadastrado.

---

## 2.136 Produto com estoque zero após cancelamento

Produto que ficar com estoque zero após cancelamento deve seguir as regras oficiais de Produtos e Estoque.

O Produto:

- permanece cadastrado;
- preserva histórico;
- não aparece nas listagens operacionais de disponibilidade quando a regra exigir estoque disponível;
- pode voltar a aparecer após nova Entrada.

Não desativar automaticamente o Produto.

---

## 2.137 Confirmação do cancelamento

Antes de concluir o cancelamento, o sistema deve apresentar um resumo.

O resumo deve identificar:

- número da Entrada;
- Fornecedor;
- Produtos;
- quantidades que serão revertidas;
- impacto no estoque;
- Contas vinculadas que serão canceladas;
- motivo.

O usuário deve confirmar a operação.

---

## 2.138 Validação final no backend

No momento da confirmação, o backend deve recalcular:

- situação atual da Entrada;
- estoque real atual de cada Produto;
- situação das Contas vinculadas;
- pagamentos das Contas;
- efeitos financeiros existentes.

A validação deve utilizar os dados persistidos mais recentes.

Não confiar em valores previamente exibidos pelo navegador.

---

## 2.139 Atomicidade do cancelamento

O cancelamento da Entrada deve ocorrer em uma única operação lógica e transacional.

Quando permitido, devem ser tratados de forma consistente:

- situação da Entrada;
- reversão das quantidades do estoque;
- movimentações de Estoque;
- cancelamento das Contas vinculadas elegíveis;
- histórico;
- auditoria.

Qualquer falha deve provocar rollback completo.

---

## 2.140 Movimentação de reversão

O cancelamento deve gerar movimentação de Estoque específica.

A movimentação deve identificar:

- tipo;
- Produto;
- quantidade;
- Entrada de origem;
- usuário;
- data e hora.

O tipo deve representar claramente a reversão de Entrada.

Não apagar a movimentação original de Entrada.

---

## 2.141 Preservação da movimentação original

A movimentação original de Entrada deve permanecer no histórico.

Exemplo:

Entrada:
+10 unidades.

Cancelamento da Entrada:
-10 unidades.

O histórico deve apresentar os dois fatos.

Não substituir a movimentação original por zero.

Não apagar a Entrada original.

---

## 2.142 Entrada já cancelada

Entrada já cancelada não pode ser cancelada novamente.

O backend deve recusar nova tentativa.

A operação deve retornar conflito compatível com a arquitetura da API.

Recomendação:

409 Conflict.

---

## 2.143 Idempotência do cancelamento

O cancelamento deve possuir proteção idempotente.

A mesma tentativa processada novamente não pode:

- reduzir estoque novamente;
- cancelar Contas novamente;
- criar nova movimentação de reversão;
- gerar nova auditoria financeira equivalente.

A mesma chave idempotente e o mesmo conteúdo devem retornar o resultado já processado.

---

## 2.144 Chave reutilizada com conteúdo diferente

Quando a mesma chave idempotente for reutilizada com conteúdo diferente, a operação deve ser recusada.

Exemplo:

Primeira tentativa:

Entrada nº 125.

Motivo:
Entrada duplicada.

Segunda requisição com a mesma chave:

Entrada nº 130.

Resultado:

Conflito.

Não reutilizar a chave para outra operação.

---

## 2.145 Concorrência entre cancelamento e estoque

O cancelamento deve considerar alterações concorrentes do estoque.

Exemplo:

Estoque atual:
10.

Entrada a cancelar:
10.

Usuário A inicia cancelamento.

Usuário B vende 1 unidade.

O cancelamento não pode concluir utilizando a leitura antiga de estoque igual a 10.

A validação final deve ocorrer dentro da operação protegida.

Se o estoque atual for 9, o cancelamento deve ser recusado.

---

## 2.146 Concorrência entre cancelamento e pagamento

O cancelamento deve considerar pagamento concorrente de Conta vinculada.

Exemplo:

Usuário A inicia cancelamento.

Usuário B registra pagamento de Conta vinculada.

A validação financeira final deve ocorrer depois da aquisição do bloqueio transacional correspondente.

Se existir pagamento válido, o cancelamento deve ser recusado.

---

## 2.147 Histórico da Entrada cancelada

Os detalhes da Entrada cancelada devem apresentar:

- situação Cancelada;
- motivo do cancelamento;
- descrição complementar, quando aplicável;
- data e hora do cancelamento;
- usuário responsável;
- quantidades originalmente recebidas;
- movimentação original;
- movimentações de reversão;
- Contas vinculadas;
- Contas canceladas automaticamente.

O histórico deve permanecer acessível.

---

## 2.148 Tentativa recusada de cancelamento

Uma tentativa recusada porque:

- estoque insuficiente;
- Conta parcialmente paga;
- Conta totalmente paga;
- conflito concorrente

não precisa ser apresentada como ocorrência operacional permanente nos detalhes normais da Entrada.

Logs técnicos e auditoria de segurança podem seguir suas regras próprias.

A Entrada deve permanecer no estado anterior.

---

## 2.149 Impressão e detalhes atuais

A impressão ou PDF dos detalhes atuais de uma Entrada cancelada deve identificar claramente:

CANCELADA.

O documento deve apresentar o motivo do cancelamento.

A movimentação original e a reversão devem permanecer identificáveis quando a finalidade do documento exigir detalhamento.

---

## 2.150 Relatórios

Relatórios de Entradas devem permitir identificar Entradas canceladas.

O status deve ser preservado.

Entradas canceladas não devem compor indicadores líquidos atuais de mercadorias recebidas quando o relatório representar efeito líquido operacional.

Quando o relatório for histórico de ocorrências, a Entrada original e seu cancelamento podem permanecer visíveis.

A finalidade do relatório deve ficar clara.

---

## 2.151 Regras gerais do Cancelamento de Entrada

O sistema deve:

- permitir cancelamento formal de Entrada;
- nunca excluir a Entrada;
- exigir estoque real suficiente;
- validar todos os Produtos da Entrada;
- exigir possibilidade de reversão integral;
- impedir cancelamento parcial;
- utilizar Inventário para divergência quantitativa parcial;
- exigir motivo;
- permitir motivos pré-definidos;
- exigir descrição quando o motivo for Outro;
- diferenciar Cancelamento de Entrada e Devolução ao Fornecedor;
- validar todas as Contas vinculadas;
- cancelar automaticamente Contas sem pagamento;
- cancelar todas as Contas elegíveis na mesma operação;
- impedir cancelamento quando existir pagamento parcial;
- impedir cancelamento quando existir pagamento integral;
- não apagar pagamentos;
- não gerar estorno financeiro silencioso;
- não restaurar automaticamente o custo anterior;
- não restaurar automaticamente o Preço de venda anterior;
- preservar histórico de preços;
- manter Produto cadastrado após cancelamento da primeira Entrada;
- permitir Produto com estoque zero;
- apresentar resumo antes da confirmação;
- recalcular estoque e financeiro no backend;
- executar a operação de forma atômica;
- gerar movimentação de reversão;
- preservar movimentação original;
- impedir novo cancelamento de Entrada cancelada;
- utilizar idempotência;
- impedir dupla redução de estoque;
- impedir duplo cancelamento de Contas;
- tratar concorrência de estoque;
- tratar concorrência com pagamento;
- preservar histórico completo;
- identificar Entrada cancelada nos documentos;
- considerar o cancelamento nos Relatórios.

## 2.152 Devolução ao Fornecedor

A Devolução ao Fornecedor representa a saída física de mercadorias anteriormente recebidas por meio de uma Entrada válida.

A operação deve ser utilizada quando a Entrada original estiver correta, mas parte ou toda a mercadoria for posteriormente devolvida ao Fornecedor.

A Devolução ao Fornecedor não cancela nem reescreve a Entrada original.

A Entrada permanece preservada no histórico.

---

## 2.153 Diferença entre Cancelamento de Entrada e Devolução ao Fornecedor

Cancelamento de Entrada representa o desfazimento integral de uma Entrada incorreta, duplicada ou cadastrada por engano.

Devolução ao Fornecedor representa uma nova operação realizada após uma Entrada válida.

Exemplo:

Entrada correta:
10 unidades.

Posteriormente devolvidas ao Fornecedor:
3 unidades.

Resultado:

A Entrada original de 10 unidades permanece válida.

O sistema registra uma Devolução ao Fornecedor de 3 unidades.

Não cancelar parcialmente a Entrada original.

---

## 2.154 Origem obrigatória

Toda Devolução ao Fornecedor deve possuir uma Entrada de origem.

O fluxo deve partir de uma Entrada confirmada e válida.

Fluxo conceitual:

Produtos e Entradas.

Histórico de Entradas.

Ver detalhes.

DEVOLVER AO FORNECEDOR.

O sistema deve recuperar da Entrada:

- Fornecedor;
- Produtos;
- quantidades originalmente recebidas;
- custos históricos;
- identificadores persistentes.

---

## 2.155 Vínculo persistente com a Entrada

A Devolução ao Fornecedor deve possuir vínculo persistente com a Entrada de origem.

Não utilizar somente:

- número visual da Entrada;
- descrição;
- nome do Fornecedor

como vínculo autoritativo.

O backend deve validar a Entrada correspondente e sua loja.

---

## 2.156 Fornecedor da Devolução

O Fornecedor da Devolução deve ser o Fornecedor histórico da Entrada de origem.

O usuário não pode trocar o Fornecedor durante a Devolução.

Exemplo:

Entrada nº 125:
Fornecedor A.

Devolução originada da Entrada nº 125:
Fornecedor A.

Não permitir alterar para Fornecedor B.

---

## 2.157 Devolução parcial

A Devolução ao Fornecedor pode ser parcial.

Exemplo:

Entrada:
10 unidades.

Devolução:
3 unidades.

A Entrada original permanece válida.

O sistema registra a saída de 3 unidades.

A quantidade restante historicamente devolvível da Entrada passa a considerar a Devolução realizada.

---

## 2.158 Devolução total

A Devolução ao Fornecedor pode abranger toda a quantidade ainda devolvível da Entrada.

Exemplo:

Entrada:
10 unidades.

Quantidade ainda devolvível:
10 unidades.

Devolução:
10 unidades.

A Entrada não deve ser cancelada.

A Entrada permanece Confirmada e vinculada à Devolução total ao Fornecedor.

---

## 2.159 Devolução de alguns itens

Quando uma Entrada possuir vários Produtos, o usuário pode devolver somente alguns itens.

Exemplo:

Entrada:

Camiseta A:
10 unidades.

Calção B:
5 unidades.

Devolução:

Camiseta A:
3 unidades.

Calção B:
0 unidades.

A operação deve registrar somente a quantidade efetivamente devolvida.

---

## 2.160 Seleção dos Produtos

A tela de Devolução ao Fornecedor deve listar os Produtos da Entrada de origem.

Para cada item, apresentar:

- Produto;
- Código;
- quantidade originalmente recebida;
- quantidade já devolvida ao Fornecedor;
- quantidade ainda devolvível;
- Estoque real atual;
- quantidade a devolver.

A quantidade a devolver deve iniciar em:

0.

O sistema não deve preencher automaticamente todos os itens com a quantidade máxima.

---

## 2.161 Quantidade devolvida

A quantidade informada para um item deve ser:

- numérica;
- finita;
- inteira;
- igual ou maior que zero.

Pelo menos um item da operação deve possuir quantidade maior que zero.

Não permitir:

- quantidade negativa;
- quantidade fracionada;
- NaN;
- infinito;
- texto inválido.

---

## 2.162 Limite histórico da Entrada

A quantidade devolvida de um Produto não pode superar a quantidade originalmente recebida naquela Entrada, descontadas as Devoluções ao Fornecedor válidas anteriores.

Fórmula conceitual:

Quantidade ainda devolvível =
Quantidade recebida na Entrada - Quantidade já devolvida ao Fornecedor.

Exemplo:

Entrada:
10 unidades.

Primeira Devolução:
3 unidades.

Quantidade ainda devolvível:
7 unidades.

Não permitir nova Devolução de 8 unidades vinculada à mesma Entrada.

---

## 2.163 Estoque de outras Entradas não aumenta o limite histórico

A existência de estoque atual proveniente de outras Entradas não aumenta a quantidade historicamente devolvível da Entrada selecionada.

Exemplo:

Entrada A:
10 unidades.

Já devolvidas da Entrada A:
3 unidades.

Quantidade ainda devolvível da Entrada A:
7 unidades.

Estoque real atual do Produto:
50 unidades.

A quantidade máxima vinculada à Entrada A continua sendo:

7 unidades.

Não permitir devolver 20 unidades como se pertencessem historicamente à Entrada A.

---

## 2.164 Estoque real suficiente

Além do limite histórico da Entrada, o Estoque real atual deve possuir quantidade suficiente para a saída física.

Exemplo:

Quantidade ainda devolvível:
7 unidades.

Estoque real atual:
2 unidades.

Quantidade máxima operacionalmente devolvível:
2 unidades.

A Devolução não pode criar Estoque real negativo.

---

## 2.165 Validação conjunta da quantidade

A quantidade máxima permitida deve respeitar simultaneamente:

- quantidade ainda devolvível da Entrada;
- Estoque real atual.

Conceitualmente:

Máximo devolvível =
menor valor entre quantidade ainda devolvível e Estoque real atual.

O backend deve realizar a validação autoritativa.

---

## 2.166 Estoque reservado em Condicional

A Devolução ao Fornecedor deve considerar que Produtos em Condicionais abertos permanecem reservados.

Mercadoria reservada e fisicamente com cliente não deve ser considerada livre para Devolução ao Fornecedor.

A validação deve considerar a quantidade disponível para a saída conforme as regras oficiais de Estoque e Condicional.

O sistema não deve retirar do estoque uma quantidade que torne as reservas existentes inconsistentes.

---

## 2.167 Motivo obrigatório

Toda Devolução ao Fornecedor deve possuir motivo.

Os motivos iniciais devem incluir:

- Defeito;
- Produto incorreto;
- Tamanho ou grade incorreta;
- Mercadoria em desacordo;
- Excesso de mercadoria;
- Acordo comercial;
- Outro.

O motivo deve ser persistido.

---

## 2.168 Motivo Outro

Quando o motivo selecionado for:

Outro.

A descrição complementar é obrigatória.

Não concluir a Devolução sem descrição válida.

---

## 2.169 Custo histórico utilizado

O valor histórico da Devolução ao Fornecedor deve utilizar o custo unitário histórico da Entrada de origem.

Exemplo:

Entrada nº 10:

Custo histórico:
R$ 80,00.

Custo atual do Produto:
R$ 95,00.

Devolução de uma unidade vinculada à Entrada nº 10:

Valor histórico devolvido:
R$ 80,00.

Não utilizar R$ 95,00 para reescrever o valor histórico da operação.

---

## 2.170 Valor histórico por item

Para cada item devolvido, o backend deve calcular:

Quantidade devolvida × Custo unitário histórico da Entrada.

Exemplo:

3 unidades × R$ 80,00 =
R$ 240,00.

O navegador não deve informar autoritativamente o valor histórico total do item.

---

## 2.171 Valor histórico total da Devolução

O valor histórico total da Devolução deve corresponder à soma dos valores históricos dos itens devolvidos.

O cálculo deve ser realizado pelo backend.

Exemplo:

Produto A:
R$ 240,00.

Produto B:
R$ 100,00.

Valor histórico total:
R$ 340,00.

---

## 2.172 Custo atual após Devolução

A Devolução ao Fornecedor não deve alterar automaticamente o Preço de custo atual do Produto.

O custo atual permanece conforme o cadastro vigente.

A operação preserva separadamente o custo histórico da Entrada utilizada na Devolução.

---

## 2.173 Preço de venda após Devolução

A Devolução ao Fornecedor não deve alterar automaticamente o Preço de venda atual.

A operação representa saída física para o Fornecedor.

Não representa alteração de preço comercial.

---

## 2.174 Efeito no Estoque

A confirmação da Devolução ao Fornecedor deve reduzir o Estoque real dos Produtos devolvidos.

Exemplo:

Estoque real:
10 unidades.

Devolução ao Fornecedor:
3 unidades.

Novo Estoque real:
7 unidades.

A redução deve ocorrer somente após confirmação válida.

---

## 2.175 Movimentação de Estoque

Toda Devolução ao Fornecedor confirmada deve gerar movimentação de Estoque.

A movimentação deve permitir identificar:

- tipo Devolução ao Fornecedor;
- Produto;
- quantidade;
- Entrada de origem;
- Devolução de origem;
- usuário;
- data e hora.

Não reduzir Estoque sem preservar a origem da movimentação.

---

## 2.176 Tratamento financeiro obrigatório

Toda Devolução ao Fornecedor deve possuir tratamento financeiro identificado.

As opções iniciais são:

- ABATER CONTA A PAGAR;
- CRÉDITO COM FORNECEDOR;
- DINHEIRO OU PIX DEVOLVIDO PELO FORNECEDOR;
- ACERTO FINANCEIRO PENDENTE.

O tratamento financeiro deve ser persistido.

---

## 2.177 Separação entre efeito físico e financeiro

A saída física da mercadoria e o acerto financeiro são efeitos relacionados, mas distintos.

A Devolução reduz o Estoque real.

O tratamento financeiro define como o valor histórico da mercadoria devolvida será conciliado.

O sistema não deve assumir automaticamente que toda Devolução:

- cancela uma Conta;
- gera crédito;
- gera Entrada financeira.

---

## 2.178 Valor conciliável

O valor máximo inicialmente conciliável da Devolução deve corresponder ao valor histórico total dos itens devolvidos.

Exemplo:

Valor histórico da Devolução:
R$ 1.000,00.

Valor máximo total dos efeitos financeiros vinculados:
R$ 1.000,00.

O sistema deve controlar o valor já conciliado e o valor pendente.

---

## 2.179 Conciliação parcial

A conciliação financeira pode ser parcial.

Exemplo:

Valor histórico da Devolução:
R$ 1.000,00.

Abatimento em Conta:
R$ 600,00.

Acerto pendente:
R$ 400,00.

O sistema deve preservar os dois valores.

---

## 2.180 Conciliação combinada

Uma mesma Devolução pode possuir mais de uma forma de acerto financeiro ao longo do tempo.

Exemplo:

Valor histórico:
R$ 1.000,00.

Abatimento de Conta:
R$ 400,00.

Crédito com Fornecedor:
R$ 300,00.

Pix devolvido pelo Fornecedor:
R$ 300,00.

Total conciliado:
R$ 1.000,00.

Saldo pendente:
R$ 0,00.

O sistema deve permitir conciliação parcial e combinada.

---

## 2.181 Abater Conta a Pagar

Quando o usuário escolher:

ABATER CONTA A PAGAR.

O sistema deve listar somente Contas a Pagar elegíveis.

A Conta deve:

- pertencer à mesma loja;
- pertencer ao mesmo Fornecedor;
- não estar Cancelada;
- possuir saldo pendente maior que zero.

---

## 2.182 Seleção de Contas para abatimento

O usuário pode selecionar uma ou mais Contas a Pagar elegíveis.

Para cada Conta selecionada, deve informar o valor do abatimento.

Exemplo:

Valor histórico pendente da Devolução:
R$ 1.000,00.

Conta A:
Abatimento R$ 600,00.

Conta B:
Abatimento R$ 400,00.

Total abatido:
R$ 1.000,00.

---

## 2.183 Limite do abatimento

O abatimento não pode superar:

- o saldo pendente da Conta selecionada;
- o valor ainda não conciliado da Devolução.

Exemplo:

Saldo da Conta:
R$ 300,00.

Não permitir abatimento:
R$ 400,00.

A validação deve ocorrer no backend.

---

## 2.184 Abatimento não é pagamento

O abatimento decorrente de Devolução ao Fornecedor não deve ser registrado como pagamento comum da Conta.

O sistema deve preservar a origem do abatimento.

A Conta deve permitir distinguir:

- pagamentos;
- juros;
- multas;
- descontos;
- abatimentos por Devolução ao Fornecedor;
- estornos.

---

## 2.185 Efeito do abatimento no saldo da Conta

O abatimento válido deve reduzir o saldo pendente da Conta.

Exemplo:

Saldo anterior:
R$ 1.000,00.

Abatimento por Devolução:
R$ 300,00.

Novo saldo:
R$ 700,00.

Não gerar saída financeira pelo valor abatido.

---

## 2.186 Crédito com Fornecedor

Quando o usuário escolher:

CRÉDITO COM FORNECEDOR.

O sistema deve registrar crédito rastreável vinculado ao Fornecedor e à Devolução.

O crédito representa valor reconhecido para utilização futura.

---

## 2.187 Saldo de crédito do Fornecedor

O sistema deve permitir consultar o saldo de crédito disponível por Fornecedor.

Exemplo:

Fornecedor:
Nike.

Crédito disponível:
R$ 1.000,00.

O saldo deve ser calculado utilizando créditos válidos menos utilizações e estornos válidos.

---

## 2.188 Crédito não altera custo

A criação de Crédito com Fornecedor não deve alterar:

- custo histórico da Entrada;
- custo atual do Produto;
- Preço de venda;
- quantidade da Devolução.

O crédito representa um efeito financeiro/comercial.

---

## 2.189 Utilização futura do crédito

Ao gerar Conta a Pagar vinculada a futura Entrada do mesmo Fornecedor, o sistema pode permitir:

UTILIZAR CRÉDITO DO FORNECEDOR.

O usuário deve informar o valor de crédito a utilizar.

O valor não pode superar:

- crédito disponível;
- valor da obrigação compatível.

---

## 2.190 Crédito utilizado em Conta a Pagar

A utilização do Crédito com Fornecedor deve reduzir o saldo da obrigação correspondente.

A operação não deve ser registrada como pagamento em:

- Dinheiro;
- Pix;
- Débito.

A origem deve permanecer identificada como:

Crédito com Fornecedor.

---

## 2.191 Rastreamento da utilização do crédito

Toda utilização de Crédito com Fornecedor deve preservar:

- Fornecedor;
- crédito de origem;
- Devolução de origem;
- Conta a Pagar beneficiada;
- valor utilizado;
- usuário;
- data e hora.

O sistema deve permitir rastrear a origem e o destino do crédito.

---

## 2.192 Dinheiro ou Pix devolvido pelo Fornecedor

Quando o Fornecedor devolver valor diretamente, o usuário deve selecionar:

- Dinheiro;
- Pix.

O sistema deve registrar uma Entrada financeira correspondente.

---

## 2.193 Entrada financeira da restituição

A Entrada financeira deve preservar:

- tipo de origem;
- Devolução ao Fornecedor;
- Fornecedor;
- forma;
- valor;
- usuário;
- data e hora.

A origem deve ser identificada como restituição de Fornecedor ou descrição equivalente.

---

## 2.194 Limite da restituição financeira

O valor recebido em Dinheiro ou Pix não pode superar o valor ainda não conciliado da Devolução.

Exemplo:

Valor histórico:
R$ 1.000,00.

Já conciliado:
R$ 700,00.

Pendente:
R$ 300,00.

Não permitir registrar restituição de:
R$ 400,00.

---

## 2.195 Dinheiro devolvido pelo Fornecedor

Quando a forma for Dinheiro, a restituição deve produzir Entrada financeira em Dinheiro conforme as regras oficiais do Caixa.

O valor deve compor o saldo correspondente.

A operação deve permanecer vinculada à Devolução.

---

## 2.196 Pix devolvido pelo Fornecedor

Quando a forma for Pix, a restituição deve produzir Entrada financeira em Pix conforme as regras financeiras oficiais.

O valor deve permanecer vinculado à Devolução e ao Fornecedor.

---

## 2.197 Acerto financeiro pendente

Quando o usuário escolher:

ACERTO FINANCEIRO PENDENTE.

A Devolução física deve ser confirmada normalmente.

O Estoque real deve ser reduzido.

O valor histórico não conciliado deve permanecer pendente.

---

## 2.198 Valor pendente de acerto

O sistema deve calcular:

Valor pendente =
Valor histórico da Devolução - Total conciliado válido.

Exemplo:

Valor histórico:
R$ 1.000,00.

Conciliado:
R$ 0,00.

Pendente:
R$ 1.000,00.

---

## 2.199 Conciliação posterior

Uma Devolução com acerto pendente deve permitir conciliação posterior.

O usuário pode registrar posteriormente:

- abatimento em Conta a Pagar;
- Crédito com Fornecedor;
- Dinheiro devolvido;
- Pix devolvido.

A conciliação pode ocorrer parcialmente.

---

## 2.200 Situação financeira da Devolução

A Devolução ao Fornecedor deve possuir situação financeira calculada.

As situações operacionais podem incluir:

- Pendente de acerto;
- Parcialmente conciliada;
- Conciliada.

Pendente de acerto:

Total conciliado igual a zero e valor histórico maior que zero.

Parcialmente conciliada:

Total conciliado maior que zero e menor que o valor histórico.

Conciliada:

Valor pendente igual a zero.

---

## 2.201 Situação operacional da Devolução

A situação operacional da Devolução deve ser separada da situação financeira.

Situações operacionais podem incluir:

- Confirmada;
- Cancelada.

Exemplo:

Operacional:
Confirmada.

Financeira:
Pendente de acerto.

Não utilizar uma única situação para representar os dois conceitos.

---

## 2.202 Cancelamento da Devolução ao Fornecedor

Uma Devolução ao Fornecedor pode ser cancelada somente por operação formal.

A Devolução não deve ser excluída.

O cancelamento deve preservar todo o histórico.

---

## 2.203 Cancelamento sem conciliação financeira

Quando a Devolução estiver Confirmada e não possuir efeito financeiro conciliado, o cancelamento pode ser permitido.

Exemplo:

Devolução:
3 unidades.

Acerto financeiro:
Pendente.

Total conciliado:
R$ 0,00.

O cancelamento pode:

- devolver as 3 unidades ao Estoque real;
- gerar movimentação de reversão;
- marcar a Devolução como Cancelada;
- preservar o histórico.

---

## 2.204 Cancelamento com abatimento em Conta

Quando a Devolução possuir abatimento aplicado a Conta a Pagar, o cancelamento não deve ocorrer diretamente.

O sistema deve impedir a operação até que o efeito financeiro seja tratado de forma segura.

Não aumentar automaticamente o saldo da Conta sem fluxo formal de reversão.

---

## 2.205 Cancelamento com Crédito de Fornecedor

Quando a Devolução tiver gerado Crédito com Fornecedor, o cancelamento deve verificar o crédito.

Se o crédito já tiver sido utilizado, o cancelamento deve ser bloqueado.

Não cancelar a Devolução enquanto existir crédito consumido por outra obrigação.

---

## 2.206 Crédito não utilizado

Quando o crédito originado pela Devolução não tiver sido utilizado, uma futura evolução pode permitir reversão atômica do crédito junto ao cancelamento.

A implementação deve possuir regra explícita e testada.

Até existir fluxo seguro, o sistema pode bloquear o cancelamento e exigir tratamento do crédito.

Não apagar o crédito silenciosamente.

---

## 2.207 Cancelamento com restituição em Dinheiro ou Pix

Quando existir Entrada financeira por restituição do Fornecedor, o cancelamento da Devolução deve ser bloqueado enquanto o efeito financeiro permanecer válido.

O sistema não deve gerar automaticamente uma Saída financeira inversa sem operação formal de estorno.

---

## 2.208 Validação financeira do cancelamento

Antes de cancelar uma Devolução, o backend deve verificar:

- abatimentos em Contas;
- Créditos com Fornecedor;
- utilização dos Créditos;
- restituições em Dinheiro;
- restituições em Pix;
- estornos existentes;
- valor conciliado;
- valor pendente.

A validação deve utilizar o estado persistido mais recente.

---

## 2.209 Estoque no cancelamento da Devolução

Quando o cancelamento for permitido, as quantidades devolvidas devem retornar ao Estoque real.

Exemplo:

Devolução:
-3 unidades.

Cancelamento da Devolução:
+3 unidades.

O sistema deve gerar movimentação de reversão.

---

## 2.210 Movimentação original preservada

A movimentação original da Devolução deve permanecer no histórico.

Exemplo:

Devolução ao Fornecedor:
-3.

Cancelamento da Devolução:
+3.

Não apagar a movimentação original.

---

## 2.211 Devolução já cancelada

Devolução já Cancelada não pode ser cancelada novamente.

O backend deve recusar a operação.

Recomendação:

409 Conflict.

A operação não deve alterar novamente o Estoque.

---

## 2.212 Atomicidade

A confirmação da Devolução ao Fornecedor deve ser atômica.

Quando aplicável, devem ocorrer de forma consistente:

- criação da Devolução;
- criação dos itens;
- redução do Estoque;
- movimentações de Estoque;
- efeito financeiro inicial;
- atualização de Contas;
- criação de Crédito com Fornecedor;
- Entrada financeira;
- histórico;
- auditoria.

Qualquer falha deve provocar rollback completo.

---

## 2.213 Idempotência

A confirmação da Devolução ao Fornecedor deve possuir proteção idempotente.

Retry, duplo clique ou resposta de rede desconhecida não podem:

- reduzir Estoque duas vezes;
- abater Conta duas vezes;
- gerar Crédito duas vezes;
- registrar restituição financeira duas vezes.

A mesma tentativa deve produzir um único efeito persistente.

---

## 2.214 Concorrência

O backend deve tratar operações concorrentes.

Exemplos:

- Venda concorrente reduzindo Estoque;
- Condicional concorrente reservando Produto;
- outra Devolução da mesma Entrada;
- pagamento concorrente de Conta a Pagar;
- utilização concorrente de Crédito com Fornecedor.

A validação final deve ocorrer dentro da operação protegida.

---

## 2.215 Número da Devolução ao Fornecedor

Cada Devolução ao Fornecedor deve possuir número automático por loja.

Exemplo:

Devolução ao Fornecedor nº 000015.

O número deve ser definido pelo backend.

O usuário não pode alterá-lo manualmente.

---

## 2.216 Data e hora

A Devolução deve registrar a data e hora da confirmação.

Novos timestamps devem seguir as regras oficiais do sistema.

Armazenamento:

UTC com offset explícito.

Apresentação:

America/Sao_Paulo.

---

## 2.217 Usuário responsável

A Devolução deve preservar o usuário autenticado responsável pela operação.

O usuário deve ser obtido da sessão e do cadastro persistido.

O navegador não deve informar autoritativamente o usuário responsável.

Administrador e Operador podem realizar Devolução ao Fornecedor.

---

## 2.218 Detalhes da Devolução

Os detalhes devem apresentar:

- número;
- situação operacional;
- situação financeira;
- Entrada de origem;
- Fornecedor;
- data e hora;
- usuário responsável;
- motivo;
- descrição complementar;
- Produtos;
- códigos;
- quantidades devolvidas;
- custos históricos;
- valor histórico por item;
- valor histórico total;
- total conciliado;
- valor pendente.

---

## 2.219 Histórico financeiro da Devolução

Os detalhes devem apresentar todos os efeitos financeiros vinculados.

Para cada efeito, identificar:

- tipo;
- valor;
- data e hora;
- usuário;
- destino ou origem relacionada.

Exemplos:

Abatimento em Conta nº 125.

Crédito com Fornecedor.

Crédito utilizado na Conta nº 180.

Pix devolvido pelo Fornecedor.

---

## 2.220 Histórico de Estoque

Os detalhes devem permitir identificar as movimentações de Estoque relacionadas à Devolução.

Quando cancelada, apresentar também as movimentações de reversão.

---

## 2.221 Lista de Devoluções ao Fornecedor

Produtos e Entradas deve permitir consultar as Devoluções ao Fornecedor.

A listagem deve apresentar, no mínimo:

- número;
- data;
- Fornecedor;
- Entrada de origem;
- quantidade total de peças;
- valor histórico;
- situação operacional;
- situação financeira;
- ação Ver detalhes.

---

## 2.222 Busca

A listagem deve permitir busca por:

- número da Devolução;
- número da Entrada;
- Fornecedor;
- Produto;
- Código.

---

## 2.223 Filtros

A listagem deve permitir filtros por:

- período;
- Fornecedor;
- situação operacional;
- situação financeira.

Situação operacional:

- Confirmada;
- Cancelada.

Situação financeira:

- Pendente de acerto;
- Parcialmente conciliada;
- Conciliada.

---

## 2.224 Alertas de acerto pendente

Devoluções ao Fornecedor com valor pendente de acerto devem ser identificáveis na Central de Alertas.

O alerta deve possuir ação equivalente a:

VER DEVOLUÇÃO.

A finalidade é impedir que mercadoria saia da loja e o acerto com o Fornecedor seja esquecido.

---

## 2.225 Relatórios

Os Relatórios devem permitir analisar Devoluções ao Fornecedor.

O Relatório deve permitir filtros por:

- período;
- Fornecedor;
- Produto;
- motivo;
- situação operacional;
- situação financeira.

---

## 2.226 Conteúdo do Relatório

O Relatório de Devoluções ao Fornecedor deve apresentar, no mínimo:

- número da Devolução;
- Entrada de origem;
- data;
- Fornecedor;
- quantidade de peças;
- valor histórico;
- total conciliado;
- valor pendente;
- motivo;
- situação operacional;
- situação financeira.

---

## 2.227 Impressão e PDF

A Devolução ao Fornecedor deve permitir impressão ou PDF simples.

O documento deve seguir as regras oficiais de Impressões e Documentos Gerados.

Deve apresentar:

- identificação da loja;
- número da Devolução;
- Entrada de origem;
- Fornecedor;
- data e hora;
- usuário responsável;
- motivo;
- Produtos;
- quantidades;
- custo histórico;
- valor histórico total;
- tratamento financeiro;
- total conciliado;
- valor pendente;
- situação.

---

## 2.228 Fonte autoritativa

O backend deve validar e calcular:

- Entrada de origem;
- Fornecedor;
- itens da Entrada;
- quantidade originalmente recebida;
- quantidade já devolvida;
- quantidade ainda devolvível;
- Estoque real;
- reservas;
- custo histórico;
- valor histórico;
- Contas elegíveis;
- saldo das Contas;
- Crédito disponível;
- valor conciliado;
- valor pendente.

O navegador não deve informar esses valores como fonte autoritativa.

---

## 2.229 Isolamento por loja

Toda Devolução ao Fornecedor deve respeitar a loja autenticada.

O sistema deve impedir:

- utilizar Entrada de outra loja;
- utilizar Conta a Pagar de outra loja;
- utilizar Crédito de Fornecedor de outra loja;
- consultar Devolução de outra loja.

A validação deve ocorrer no backend.

---

## 2.230 Regras gerais da Devolução ao Fornecedor

O sistema deve:

- diferenciar Devolução ao Fornecedor de Cancelamento de Entrada;
- exigir Entrada de origem;
- preservar vínculo persistente;
- utilizar o Fornecedor histórico da Entrada;
- impedir alteração do Fornecedor;
- permitir Devolução parcial;
- permitir Devolução total;
- permitir devolver somente alguns itens;
- iniciar quantidades em zero;
- exigir quantidade inteira válida;
- limitar a quantidade pela Entrada de origem;
- descontar Devoluções anteriores;
- não utilizar estoque de outras Entradas para ampliar o limite histórico;
- exigir Estoque real suficiente;
- considerar reservas de Condicionais;
- exigir motivo;
- exigir descrição para Outro;
- utilizar custo histórico da Entrada;
- calcular valores no backend;
- não alterar custo atual;
- não alterar Preço de venda atual;
- reduzir Estoque real;
- gerar movimentação de Estoque;
- exigir tratamento financeiro;
- permitir abatimento em Conta a Pagar;
- permitir várias Contas no abatimento;
- impedir abatimento superior ao saldo;
- impedir abatimento superior ao valor pendente da Devolução;
- diferenciar abatimento de pagamento;
- permitir Crédito com Fornecedor;
- manter saldo rastreável de Crédito;
- permitir utilização futura do Crédito;
- vincular origem e destino do Crédito;
- permitir restituição em Dinheiro;
- permitir restituição em Pix;
- gerar Entrada financeira correspondente;
- impedir restituição superior ao valor pendente;
- permitir Acerto financeiro pendente;
- permitir conciliação posterior;
- permitir conciliação parcial;
- permitir conciliação combinada;
- calcular situação financeira;
- separar situação operacional e financeira;
- permitir cancelamento formal;
- nunca excluir Devolução;
- permitir cancelamento simples quando não houver efeito financeiro conciliado;
- bloquear cancelamento com efeitos financeiros não tratados;
- verificar Crédito utilizado;
- não gerar estorno financeiro silencioso;
- devolver quantidades ao Estoque quando o cancelamento for permitido;
- gerar movimentação de reversão;
- preservar movimentação original;
- impedir novo cancelamento;
- utilizar transação;
- utilizar idempotência;
- tratar concorrência;
- numerar Devoluções automaticamente;
- registrar data e hora;
- registrar usuário responsável;
- apresentar detalhes completos;
- apresentar histórico financeiro;
- apresentar histórico de Estoque;
- possuir listagem;
- possuir busca;
- possuir filtros;
- alertar acertos financeiros pendentes;
- possuir Relatório;
- permitir PDF;
- utilizar o backend como fonte autoritativa;
- respeitar isolamento por loja.

## 2.231 Crédito com Fornecedor

O Crédito com Fornecedor representa valor reconhecido a favor da loja junto a um Fornecedor.

O Crédito somente pode ser originado de uma Devolução ao Fornecedor confirmada.

Não permitir criação manual de Crédito com Fornecedor sem vínculo com uma Devolução válida.

O Crédito deve possuir vínculo persistente com:

- loja;
- Fornecedor;
- Devolução ao Fornecedor de origem.

---

## 2.232 Origem obrigatória do Crédito

Toda criação de Crédito com Fornecedor deve possuir uma Devolução ao Fornecedor como origem.

A Devolução deve:

- pertencer à mesma loja;
- estar Confirmada;
- possuir valor ainda não conciliado suficiente;
- possuir tratamento financeiro compatível com Crédito com Fornecedor.

O backend deve validar a origem.

O navegador não deve criar Crédito informando livremente Fornecedor e valor.

---

## 2.233 Valor inicial do Crédito

O valor inicial do Crédito deve corresponder exatamente à parte do valor histórico da Devolução destinada ao tratamento:

CRÉDITO COM FORNECEDOR.

Exemplo:

Valor histórico da Devolução:
R$ 1.000,00.

Abatimento em Conta:
R$ 400,00.

Crédito com Fornecedor:
R$ 600,00.

Valor inicial do Crédito:
R$ 600,00.

O backend deve calcular e validar o limite conciliável da Devolução.

---

## 2.234 Limite de criação do Crédito

O valor do Crédito não pode superar o valor ainda não conciliado da Devolução ao Fornecedor.

Exemplo:

Valor histórico:
R$ 1.000,00.

Já conciliado:
R$ 700,00.

Valor pendente:
R$ 300,00.

Não permitir criar Crédito de:
R$ 400,00.

A validação deve ocorrer no backend.

---

## 2.235 Crédito vinculado ao Fornecedor

O Crédito pertence exclusivamente ao Fornecedor da Devolução de origem.

Exemplo:

Crédito originado de Devolução ao Fornecedor Nike.

Fornecedor do Crédito:
Nike.

O Crédito não pode ser utilizado em Conta a Pagar de outro Fornecedor.

---

## 2.236 Proibição de transferência de Crédito

O sistema não deve permitir transferir Crédito entre Fornecedores.

Exemplo:

Crédito Nike:
R$ 1.000,00.

Não permitir utilizar ou transferir para:

Adidas.

Puma.

Outro Fornecedor.

O vínculo com o Fornecedor deve permanecer preservado.

---

## 2.237 Vários Créditos do mesmo Fornecedor

Um Fornecedor pode possuir vários Créditos.

Cada Crédito deve permanecer individualmente preservado.

Exemplo:

Crédito A:
Origem Devolução nº 10.
R$ 500,00.

Crédito B:
Origem Devolução nº 15.
R$ 1.000,00.

Crédito total disponível do Fornecedor:
R$ 1.500,00.

O sistema deve preservar a identidade de cada Crédito.

---

## 2.238 Saldo total de Crédito do Fornecedor

A ficha do Fornecedor deve apresentar o Crédito total disponível.

O valor deve ser calculado utilizando:

- Créditos válidos;
- utilizações válidas;
- estornos de utilizações;
- reversões formais.

Fórmula conceitual:

Crédito disponível =
Créditos válidos - Utilizações líquidas válidas.

O sistema não deve utilizar apenas a soma dos valores originais dos Créditos.

---

## 2.239 Utilização parcial

O Crédito pode ser utilizado parcialmente.

Exemplo:

Crédito disponível:
R$ 1.000,00.

Conta a Pagar:
R$ 300,00.

Valor utilizado:
R$ 300,00.

Saldo disponível do Crédito:
R$ 700,00.

A utilização parcial deve ser preservada no histórico.

---

## 2.240 Múltiplas utilizações

O mesmo Crédito pode ser utilizado em várias operações até consumir integralmente seu saldo.

Exemplo:

Crédito original:
R$ 1.000,00.

Primeira utilização:
R$ 300,00.

Segunda utilização:
R$ 200,00.

Terceira utilização:
R$ 500,00.

Saldo:
R$ 0,00.

Cada utilização deve possuir registro próprio.

---

## 2.241 Ordem de utilização dos Créditos

Quando existirem vários Créditos disponíveis do mesmo Fornecedor, o sistema deve utilizar primeiro o Crédito mais antigo.

A regra oficial é FIFO:

First In, First Out.

Em português:

Crédito mais antigo primeiro.

O usuário deve informar o valor total de Crédito que deseja utilizar.

O backend deve distribuir o valor automaticamente entre os Créditos disponíveis mais antigos.

---

## 2.242 Exemplo de FIFO

Fornecedor possui:

Crédito A:
Data 01/06.
Saldo R$ 300,00.

Crédito B:
Data 15/06.
Saldo R$ 500,00.

Usuário deseja utilizar:
R$ 600,00.

Alocação:

Crédito A:
R$ 300,00.

Crédito B:
R$ 300,00.

Saldo restante:

Crédito A:
R$ 0,00.

Crédito B:
R$ 200,00.

O histórico deve preservar as alocações.

---

## 2.243 Distribuição autoritativa pelo backend

A distribuição FIFO deve ser calculada pelo backend.

O navegador não deve informar autoritativamente quais Créditos serão consumidos.

O backend deve:

1. localizar os Créditos disponíveis do Fornecedor;
2. ordenar pela data e critério persistente de desempate;
3. consumir os mais antigos;
4. criar as alocações de utilização.

A ordenação deve ser determinística.

---

## 2.244 Critério de desempate

Quando dois Créditos possuírem a mesma data e hora operacional relevante, o sistema deve utilizar identificador ou ordem persistente como critério de desempate.

O resultado da regra FIFO deve ser reproduzível.

Não utilizar ordenação aleatória.

---

## 2.245 Expiração do Crédito

Crédito com Fornecedor não expira automaticamente.

O sistema não deve cancelar Crédito por:

- passagem de 30 dias;
- passagem de 90 dias;
- virada do ano;
- ausência de utilização.

O Crédito permanece disponível enquanto possuir saldo válido.

---

## 2.246 Encerramento do Crédito

O Crédito deixa de possuir saldo disponível quando:

- for integralmente utilizado;
- for formalmente revertido por operação válida;
- sua origem for tratada por fluxo formal compatível.

O sistema não deve zerar Crédito manualmente sem operação rastreável.

---

## 2.247 Situação do Crédito

O Crédito pode possuir situação calculada.

As situações são:

- Disponível;
- Parcialmente utilizado;
- Utilizado;
- Revertido.

Disponível:

Valor utilizado líquido igual a zero e saldo maior que zero.

Parcialmente utilizado:

Valor utilizado maior que zero e saldo disponível maior que zero.

Utilizado:

Saldo disponível igual a zero por utilização válida.

Revertido:

Crédito sem efeito válido em razão de operação formal de reversão.

---

## 2.248 Crédito utilizado permanece no histórico

Crédito integralmente utilizado não deve ser excluído.

O registro deve permanecer disponível.

Apresentar:

Valor original.

Valor utilizado.

Saldo disponível:
R$ 0,00.

Situação:
Utilizado.

A origem da Devolução deve permanecer identificável.

---

## 2.249 Utilização em Conta a Pagar

O Crédito com Fornecedor pode ser utilizado para reduzir o saldo de qualquer Conta a Pagar pendente do mesmo Fornecedor.

A Conta não precisa ser obrigatoriamente originada de Entrada de Mercadorias.

Exemplo:

Crédito originado de Devolução de mercadorias.

Conta a Pagar do mesmo Fornecedor vinculada a Serviço.

A utilização do Crédito é permitida.

O vínculo pelo Fornecedor é obrigatório.

---

## 2.250 Conta elegível para Crédito

Para receber Crédito com Fornecedor, a Conta a Pagar deve:

- pertencer à mesma loja;
- pertencer ao mesmo Fornecedor;
- não estar Cancelada;
- possuir saldo pendente maior que zero.

O valor utilizado não pode superar o saldo pendente da Conta.

---

## 2.251 Crédito como forma de baixa da Conta

No fluxo de pagamento ou baixa de Conta a Pagar, deve existir a opção:

CRÉDITO DO FORNECEDOR.

Essa opção representa utilização de Crédito disponível.

Ela não deve ser tratada como forma bancária ou de Caixa.

---

## 2.252 Formas de pagamento e Crédito do Fornecedor

As formas financeiras normais de pagamento de Conta permanecem:

- Dinheiro;
- Pix;
- Débito.

Crédito do Fornecedor é uma forma de abatimento do saldo da obrigação com origem comercial rastreável.

O sistema deve diferenciar:

- pagamento financeiro;
- utilização de Crédito do Fornecedor.

---

## 2.253 Efeito financeiro da utilização do Crédito

A utilização de Crédito com Fornecedor não gera:

- Entrada no Caixa;
- Saída no Caixa;
- recebível bancário;
- movimentação Pix;
- movimentação de Débito.

O efeito é a redução do saldo da Conta a Pagar.

---

## 2.254 Redução do saldo da Conta

Exemplo:

Saldo da Conta:
R$ 1.000,00.

Crédito utilizado:
R$ 300,00.

Novo saldo:
R$ 700,00.

Não gerar Saída financeira de R$ 300,00.

A Conta deve preservar que a redução ocorreu por Crédito do Fornecedor.

---

## 2.255 Utilização combinada na Conta

Uma Conta a Pagar pode ser baixada utilizando combinação de:

- Crédito do Fornecedor;
- Dinheiro;
- Pix;
- Débito.

Exemplo:

Saldo:
R$ 1.000,00.

Crédito do Fornecedor:
R$ 400,00.

Pix:
R$ 600,00.

Saldo final:
R$ 0,00.

O sistema deve preservar cada efeito separadamente.

---

## 2.256 Limite da utilização

O valor de Crédito solicitado não pode superar:

- Crédito total disponível do Fornecedor;
- saldo pendente da Conta.

Exemplo:

Crédito disponível:
R$ 500,00.

Saldo da Conta:
R$ 300,00.

Máximo utilizável:
R$ 300,00.

O backend deve validar o limite.

---

## 2.257 Pagamento parcial com Crédito

A utilização de Crédito pode ser parcial.

Exemplo:

Saldo da Conta:
R$ 1.000,00.

Crédito utilizado:
R$ 200,00.

Novo saldo:
R$ 800,00.

A Conta permanece pendente ou na situação correspondente ao saldo atual.

---

## 2.258 Histórico da utilização

Cada utilização de Crédito deve registrar:

- Fornecedor;
- Conta a Pagar;
- valor total utilizado;
- data e hora;
- usuário responsável.

Também devem ser preservadas as alocações entre os Créditos de origem consumidos pela regra FIFO.

---

## 2.259 Alocações de Crédito

O sistema deve preservar, para cada utilização:

- Crédito de origem;
- Devolução ao Fornecedor de origem;
- valor alocado;
- Conta a Pagar de destino.

Exemplo:

Conta nº 200.

Utilização total:
R$ 600,00.

Alocações:

Crédito A:
R$ 300,00.

Crédito B:
R$ 300,00.

O vínculo deve permanecer consultável.

---

## 2.260 Usuário responsável pela utilização

O usuário responsável deve ser obtido da sessão autenticada.

Administrador e Operador podem utilizar Crédito com Fornecedor em Conta a Pagar.

O navegador não deve informar autoritativamente o usuário.

---

## 2.261 Data e hora da utilização

Toda utilização deve possuir timestamp oficial.

Novos timestamps devem ser armazenados em UTC com offset explícito.

A apresentação deve utilizar:

America/Sao_Paulo.

---

## 2.262 Cancelamento de Conta que utilizou Crédito

O cancelamento ou estorno de uma Conta que utilizou Crédito deve tratar as utilizações de Crédito vinculadas.

O sistema não deve perder o valor consumido.

Quando a utilização for revertida validamente, o valor deve retornar aos Créditos originais.

---

## 2.263 Retorno aos Créditos originais

O estorno da utilização deve reverter exatamente as alocações originais.

Exemplo:

Utilização:

Crédito A:
R$ 300,00.

Crédito B:
R$ 200,00.

Estorno integral da utilização:

Crédito A recebe novamente:
R$ 300,00 de saldo disponível.

Crédito B recebe novamente:
R$ 200,00 de saldo disponível.

O sistema não deve criar um terceiro Crédito artificial de R$ 500,00.

---

## 2.264 Estorno parcial de utilização

Quando o fluxo de Conta permitir estorno parcial do efeito correspondente, o sistema deve reverter as alocações de forma determinística.

A reversão deve respeitar as alocações persistidas.

O sistema não deve inventar uma nova origem de Crédito.

A implementação deve possuir cobertura específica de testes.

---

## 2.265 Histórico do estorno

O estorno não deve apagar a utilização original.

O histórico deve apresentar:

- utilização do Crédito;
- estorno da utilização.

O saldo disponível deve utilizar o efeito líquido válido.

---

## 2.266 Conta cancelada

Quando uma Conta for cancelada e todas as utilizações de Crédito forem revertidas de forma válida, os Créditos originais voltam a possuir o saldo correspondente.

A Conta permanece Cancelada.

Os Créditos permanecem vinculados às suas Devoluções de origem.

---

## 2.267 Crédito originado de Devolução cancelada

Uma Devolução ao Fornecedor não pode ser cancelada livremente quando tiver originado Crédito com Fornecedor válido.

O cancelamento deve considerar:

- saldo original do Crédito;
- valor utilizado;
- utilizações estornadas;
- situação atual.

Se o Crédito tiver sido utilizado e o efeito não tiver sido integralmente revertido, o cancelamento da Devolução deve ser bloqueado.

---

## 2.268 Crédito disponível não utilizado e reversão

Quando um Crédito nunca tiver sido utilizado, sua reversão pode ser executada em operação formal compatível com a reversão da Devolução de origem.

A operação deve:

- preservar o Crédito;
- marcar a situação como Revertido;
- zerar seu efeito disponível;
- preservar histórico.

Não excluir o Crédito.

---

## 2.269 Proibição de ajuste manual do saldo

O usuário não pode editar diretamente:

Crédito disponível:
R$ 1.000,00

para:

R$ 500,00.

O saldo deve ser consequência de:

- criação de Crédito;
- utilização;
- estorno;
- reversão formal.

Correções não devem ser feitas por edição direta do saldo.

---

## 2.270 Ficha do Fornecedor

A ficha do Fornecedor deve apresentar resumo financeiro relacionado ao Crédito.

O resumo deve incluir:

- Crédito disponível;
- Contas em aberto;
- Contas vencidas.

Os valores devem utilizar os saldos atuais válidos.

---

## 2.271 Área de Créditos na ficha do Fornecedor

A ficha deve possuir área ou seção de Créditos.

Para cada Crédito, apresentar:

- origem;
- número da Devolução ao Fornecedor;
- data;
- valor original;
- valor utilizado líquido;
- saldo disponível;
- situação.

A listagem deve permitir abrir os detalhes quando aplicável.

---

## 2.272 Área de utilizações

A ficha do Fornecedor deve permitir consultar as utilizações de Crédito.

Apresentar:

- Conta a Pagar;
- data e hora;
- valor utilizado;
- usuário responsável.

Quando uma utilização consumir vários Créditos, os detalhes devem permitir visualizar as alocações.

---

## 2.273 Crédito total disponível

A ficha do Fornecedor deve apresentar o total disponível de forma destacada.

Exemplo:

Crédito disponível:
R$ 2.500,00.

O valor deve ser calculado no backend.

O frontend não deve somar dados incompletos carregados apenas na página atual como fonte autoritativa.

---

## 2.274 Conta a Pagar e Crédito disponível

Ao abrir uma Conta a Pagar de Fornecedor que possua Crédito disponível, o sistema deve informar essa disponibilidade.

Exemplo:

Crédito disponível com este Fornecedor:
R$ 1.000,00.

A informação possui finalidade operacional.

O sistema não deve aplicar o Crédito automaticamente sem ação do usuário.

---

## 2.275 Uso consciente do Crédito

O usuário deve escolher utilizar Crédito do Fornecedor.

A existência de Crédito disponível não deve reduzir automaticamente todas as Contas do Fornecedor.

O usuário informa o valor a utilizar na operação correspondente.

---

## 2.276 Alertas

Crédito disponível não gera alerta obrigatório por si só.

O sistema não deve encher a Central de Alertas apenas porque existe Crédito com Fornecedor.

Acertos pendentes de Devolução ao Fornecedor continuam seguindo a regra de alerta específica.

---

## 2.277 Relatórios

Os Relatórios devem permitir consultar Créditos com Fornecedores.

O Relatório pode permitir filtros por:

- Fornecedor;
- período de origem;
- situação.

Situações:

- Disponível;
- Parcialmente utilizado;
- Utilizado;
- Revertido.

---

## 2.278 Colunas do Relatório de Créditos

O Relatório deve apresentar, no mínimo:

- Fornecedor;
- Devolução de origem;
- data;
- valor original;
- valor utilizado;
- saldo disponível;
- situação.

O relatório deve permitir acesso aos detalhes quando aplicável.

---

## 2.279 Relatório de utilizações

As utilizações de Crédito devem permanecer consultáveis.

Devem permitir identificar:

- Fornecedor;
- Conta a Pagar;
- data;
- valor utilizado;
- usuário;
- Créditos de origem.

---

## 2.280 Impressão e PDF

A ficha ou relatório de Créditos pode ser exportado conforme as regras oficiais de Impressões e Documentos Gerados.

O documento deve respeitar os filtros aplicados.

Valores devem ser apresentados no padrão brasileiro.

---

## 2.281 Atomicidade

A utilização de Crédito em Conta a Pagar deve ser atômica.

Devem ocorrer de forma consistente:

- validação da Conta;
- validação do Fornecedor;
- validação do saldo da Conta;
- validação dos Créditos disponíveis;
- alocação FIFO;
- redução dos saldos dos Créditos;
- redução do saldo da Conta;
- criação do histórico;
- auditoria.

Qualquer falha deve provocar rollback completo.

---

## 2.282 Idempotência

A utilização de Crédito deve possuir proteção idempotente.

Clique duplo, retry ou falha de rede não podem:

- consumir Crédito duas vezes;
- reduzir a Conta duas vezes;
- criar utilizações duplicadas.

A mesma tentativa deve produzir um único efeito persistente.

---

## 2.283 Concorrência

O backend deve tratar duas utilizações concorrentes do mesmo Crédito.

Exemplo:

Crédito disponível:
R$ 500,00.

Usuário A tenta usar:
R$ 400,00.

Usuário B tenta usar:
R$ 300,00.

Somente operações compatíveis com o saldo real serializado podem concluir.

O sistema não pode produzir saldo negativo de Crédito.

---

## 2.284 Validação após bloqueio

A validação do saldo disponível deve ocorrer após a aquisição do mecanismo de bloqueio transacional correspondente.

Não utilizar somente saldo lido antes da transação.

Essa regra também se aplica ao saldo da Conta a Pagar.

---

## 2.285 Fonte autoritativa

O backend deve calcular:

- Crédito total disponível;
- saldo de cada Crédito;
- ordem FIFO;
- alocações;
- saldo da Conta;
- valor máximo utilizável;
- situação do Crédito.

O navegador não deve informar esses valores como fonte autoritativa.

---

## 2.286 Isolamento por loja

O sistema deve impedir utilização de Crédito:

- de outra loja;
- em Conta de outra loja;
- para Fornecedor de outra loja.

Todo vínculo deve respeitar a loja autenticada.

---

## 2.287 Regras gerais do Crédito com Fornecedor

O sistema deve:

- permitir Crédito somente a partir de Devolução ao Fornecedor;
- impedir Crédito manual sem origem;
- utilizar o valor destinado ao tratamento Crédito com Fornecedor;
- impedir valor superior ao pendente da Devolução;
- vincular Crédito ao Fornecedor;
- impedir transferência entre Fornecedores;
- permitir vários Créditos por Fornecedor;
- preservar cada Crédito individualmente;
- calcular Crédito total disponível;
- permitir utilização parcial;
- permitir várias utilizações;
- utilizar Crédito mais antigo primeiro;
- aplicar FIFO;
- calcular a distribuição no backend;
- utilizar ordenação determinística;
- não expirar Crédito automaticamente;
- preservar Crédito até utilização ou reversão formal;
- calcular situação do Crédito;
- preservar Crédito integralmente utilizado;
- permitir uso em qualquer Conta a Pagar pendente do mesmo Fornecedor;
- impedir uso em Conta de outro Fornecedor;
- apresentar Crédito do Fornecedor como opção de baixa;
- diferenciar Crédito de pagamento financeiro;
- não gerar Entrada de Caixa;
- não gerar Saída de Caixa;
- reduzir o saldo da Conta;
- permitir utilização combinada com Dinheiro;
- permitir utilização combinada com Pix;
- permitir utilização combinada com Débito;
- impedir uso superior ao Crédito disponível;
- impedir uso superior ao saldo da Conta;
- permitir utilização parcial na Conta;
- registrar cada utilização;
- preservar alocações dos Créditos de origem;
- registrar usuário;
- registrar data e hora;
- devolver valores aos Créditos originais em estorno válido;
- não criar Crédito artificial durante estorno;
- preservar histórico de utilização e estorno;
- bloquear cancelamento da Devolução quando Crédito utilizado não tiver sido revertido;
- permitir reversão formal de Crédito não utilizado;
- impedir edição direta do saldo;
- apresentar Crédito disponível na ficha do Fornecedor;
- apresentar Contas em aberto;
- apresentar Contas vencidas;
- listar Créditos;
- listar utilizações;
- informar Crédito disponível na Conta a Pagar;
- não aplicar Crédito automaticamente;
- não gerar alerta apenas por existir Crédito;
- permitir Relatório de Créditos;
- permitir consulta das utilizações;
- executar utilização de forma atômica;
- utilizar idempotência;
- tratar concorrência;
- validar saldos após bloqueio;
- calcular valores no backend;
- respeitar isolamento por loja.

# 3. ESTOQUE


## 3.1 Conceitos de estoque

O sistema deve distinguir três conceitos de estoque.

### Estoque real

Quantidade total registrada fisicamente no estoque.

### Estoque reservado

Quantidade vinculada a condicionais ativos.

### Estoque disponível

Quantidade efetivamente disponível para novas vendas e novos condicionais.

Fórmula:

Estoque disponível = Estoque real - Estoque reservado

O estoque nunca pode ficar negativo.

---

## 3.2 Entrada de mercadoria

A entrada de novas unidades pode ocorrer através do próprio fluxo de cadastro de produtos.

Ao digitar um código de produto já existente:

1. o sistema deve identificar o produto;
2. preencher automaticamente os dados já cadastrados;
3. não preencher o campo da nova quantidade de entrada com o estoque atual;
4. permitir informar a quantidade da nova entrada;
5. somar a nova quantidade ao estoque existente.

Exemplo:

- Estoque atual: 5;
- Nova entrada: 3;
- Novo estoque real: 8.

A nova entrada não deve substituir silenciosamente o estoque anterior.

---

## 3.3 Atualização do cadastro durante nova entrada

Ao realizar uma nova entrada de um código existente, o usuário pode atualizar os dados atuais do produto, incluindo:

- Preço de custo;
- Preço de venda;
- Margem;
- Demais informações cadastrais permitidas.

Os novos valores passam a valer para operações futuras.

Alterações no cadastro não podem modificar dados históricos de vendas já realizadas.

---

## 3.4 Movimentações de estoque

O histórico de estoque deve registrar:

- Entrada;
- Venda;
- Cancelamento;
- Devolução;
- Condicional/Reserva;
- Inventário.

Cada movimentação deve possuir, quando aplicável:

- Produto;
- Código;
- Tipo da movimentação;
- Quantidade;
- Data e hora;
- Usuário responsável;
- Origem da movimentação;
- Referência da venda, condicional, devolução ou inventário.

O histórico deve ser preservado.

---

## 3.5 Venda

A venda reduz o estoque somente quando for efetivamente finalizada.

Não é permitido:

- vender quantidade superior ao estoque disponível;
- gerar estoque negativo.

Produtos com estoque disponível igual a zero não podem ser vendidos.

---

## 3.6 Condicional e reserva

Produtos enviados em condicional ficam reservados.

A reserva reduz o estoque disponível, mas não deve provocar uma segunda baixa quando o produto for posteriormente transformado em venda.

Quando o produto for:

- devolvido → libera a reserva;
- vendido → converte a reserva em saída definitiva;
- cancelado no condicional → libera a reserva.

O sistema deve impedir duplicidade de movimentações.

---

## 3.7 Estoque mínimo

O estoque mínimo funciona como indicador de alerta.

Quando o estoque atingir ou ficar abaixo do mínimo:

- o sistema pode emitir alerta;
- o produto continua disponível normalmente enquanto houver estoque disponível maior que zero.

O estoque mínimo não bloqueia vendas.

---

## 3.8 Produtos com estoque zero

Produtos com estoque zero:

- permanecem cadastrados;
- preservam todo o histórico;
- não podem ser excluídos automaticamente;
- não aparecem nas listagens operacionais de produtos disponíveis.

Devem ficar ocultos das listagens de:

- Venda;
- Estoque operacional;
- Condicional;
- Catálogo.

O produto volta a aparecer automaticamente quando receber uma nova entrada de estoque.

O cadastro histórico deve continuar acessível ao sistema para:

- nova entrada pelo código;
- histórico;
- auditoria;
- relatórios que necessitem de dados históricos.

---

## 3.9 Catálogo

O catálogo deve exibir somente produtos com estoque disponível maior que zero.

Produtos com estoque disponível igual a zero não devem aparecer no catálogo.

---

## 3.10 Inventário

O inventário é o único processo autorizado para corrigir divergências de estoque.

O inventário pode abranger todo o estoque.

Durante o processo, deve ser possível registrar:

- quantidade registrada no sistema;
- quantidade física encontrada;
- diferença;
- motivo da divergência.

Após a confirmação:

- o sistema corrige o estoque;
- gera uma movimentação de inventário;
- preserva a quantidade anterior;
- registra a quantidade encontrada;
- registra a diferença;
- registra o motivo;
- registra data e hora;
- registra o usuário responsável.

A correção não pode ocorrer de forma silenciosa.

---

## 3.11 Restrições

Não é permitido:

- estoque negativo;
- ajuste manual direto fora do inventário;
- apagar histórico de movimentações;
- vender produto reservado para outro cliente;
- duplicar baixa de estoque;
- duplicar retorno por cancelamento ou devolução;
- desativar manualmente um produto apenas para retirá-lo do estoque.

A disponibilidade do produto deve ser determinada pelo estoque.

# 4. VENDAS

O módulo de vendas possui cinco operações principais:

1. Nova Venda;
2. Condicional;
3. Devolução/Troca;
4. Histórico;
5. Cancelar Venda.

---

## 4.1 Nova Venda


### 4.1.1 Identificação da venda

Toda nova venda deve possuir:

- número gerado automaticamente;
- data e hora automáticas;
- usuário responsável registrado.

O cliente padrão deve vir selecionado inicialmente para agilizar vendas rápidas.

---

### 4.1.2 Seleção de produtos

A tela de Nova Venda deve possuir uma lista de produtos disponíveis no lado esquerdo.

A listagem inicial deve mostrar aproximadamente 10 produtos por vez, evitando crescimento excessivo da página.

A busca deve permitir localizar produtos por:

- código;
- nome.

Somente produtos com estoque disponível maior que zero devem aparecer como disponíveis para venda.

Cada produto deve possuir uma ação de adição, identificada visualmente por botão com símbolo de “+” ou equivalente.

O usuário pode:

- adicionar mais de uma unidade do mesmo produto;
- alterar a quantidade;
- remover produtos antes da finalização.

O sistema deve validar o estoque disponível antes de permitir a quantidade solicitada.

---

### 4.1.3 Cliente

O cliente padrão deve ser utilizado quando não houver necessidade de vincular um cliente cadastrado.

O usuário pode trocar o cliente durante a montagem da venda.

Quando um cliente cadastrado for selecionado:

- o sistema deve consultar a situação do crediário;
- caso existam parcelas em atraso, deve exibir um alerta;
- o usuário pode continuar ou interromper a venda.

O alerta de inadimplência não bloqueia automaticamente a operação.

Quando a forma de pagamento escolhida for crediário:

- um cliente cadastrado é obrigatório;
- o cliente padrão não pode ser utilizado;
- caso nenhum cliente válido esteja selecionado, o sistema deve exigir a escolha de um cliente cadastrado.

---

### 4.1.4 Preços, descontos e acréscimos

O sistema deve permitir alterações de valor durante a venda.

Podem ser aplicados:

- desconto por produto;
- desconto geral na venda;
- alteração manual do valor de um produto;
- acréscimo por produto;
- acréscimo geral na venda.

Não existe limite fixo de desconto.

Qualquer usuário autorizado a realizar vendas pode alterar preços, descontos e acréscimos.

Toda alteração deve afetar somente a venda atual, salvo quando houver alteração explícita do cadastro do produto.

A venda deve preservar:

- preço original;
- preço praticado;
- desconto;
- acréscimo;
- valor final.

---

### 4.1.5 Formas de pagamento

São permitidas:

- Dinheiro;
- Pix;
- Débito;
- Crédito;
- Crediário.

O sistema deve permitir pagamentos mistos.

Não existe limite fixo de quantidade de formas de pagamento utilizadas na mesma venda.

A soma de todas as formas de pagamento deve corresponder ao valor final da venda.

A venda não pode ser concluída quando:

- o total informado nas formas de pagamento for menor que o valor da venda;
- houver inconsistência entre o total da venda e a distribuição das formas de pagamento.

O pagamento em dinheiro pode possuir tratamento específico de troco.

---

### 4.1.6 Dinheiro

Pagamentos em dinheiro entram diretamente no caixa.

Quando houver valor entregue superior ao valor devido em dinheiro, o sistema deve calcular e exibir o troco.

O valor efetivamente registrado como receita da venda deve corresponder ao valor devido, e não ao valor entregue pelo cliente.

O troco deve aparecer no comprovante quando aplicável.

---

### 4.1.7 Pix

Pagamentos em Pix entram diretamente no caixa.

O valor deve ser registrado com sua forma de pagamento correspondente.

---

### 4.1.8 Débito e Crédito

Pagamentos em cartão de débito ou crédito:

- registram normalmente a venda;
- não exigem registro do número de parcelas do cartão no sistema;
- seguem o fluxo financeiro de recebíveis e entrada posterior por conta bancária.

O sistema não controla diretamente o parcelamento realizado pela operadora de cartão.

Os valores não devem ser considerados como dinheiro disponível no caixa antes do efetivo recebimento, conforme as regras financeiras do sistema.

---

### 4.1.9 Crediário

Quando houver crediário:

- o cliente cadastrado é obrigatório;
- aplicam-se as regras da seção de Crediário;
- o valor lançado no crediário deve respeitar as regras de limite de crédito;
- o sistema pode permitir entrada por outra forma de pagamento e crediário para o saldo restante.

Quando o limite de crédito for ultrapassado:

- o sistema deve alertar o usuário;
- o usuário pode autorizar a venda;
- o limite do cliente pode ser aumentado conforme as regras definidas para o crediário.

---

### 4.1.10 Pagamento misto

O pagamento misto pode utilizar qualquer combinação das formas de pagamento permitidas.

Exemplo:

- Dinheiro;
- Pix;
- Crédito;
- Crediário.

Cada forma deve registrar seu valor individualmente.

A soma de todos os componentes deve corresponder ao total final da venda.

Cada componente deve seguir sua própria regra financeira.

Não existe limite fixo para a quantidade de formas de pagamento utilizadas na mesma venda.

---

### 4.1.11 Confirmação da venda

Ao clicar em finalizar, o sistema deve solicitar confirmação.

Antes da confirmação, deve apresentar o resumo da venda.

A venda somente produz efeitos definitivos após a confirmação.

Após a confirmação:

- a venda é registrada;
- o estoque é baixado;
- as formas de pagamento são registradas;
- as movimentações financeiras correspondentes são geradas;
- o crediário é criado, quando aplicável.

A operação deve ser tratada de forma consistente, evitando que uma falha parcial deixe estoque, financeiro ou crediário em estados divergentes.

---

### 4.1.12 Pós-venda

Após a confirmação da venda, o sistema deve exibir:

- detalhes da venda;
- opção de impressão.

O usuário deve conseguir visualizar o resumo completo da operação concluída.

---

### 4.1.13 Venda em montagem

Enquanto a venda ainda não foi confirmada:

- nenhuma baixa definitiva de estoque deve ocorrer;
- nenhuma movimentação financeira deve ser gerada;
- nenhum crediário deve ser criado.

A tela deve possuir uma opção para limpar a venda.

Ao limpar:

- todos os produtos adicionados são removidos;
- os valores temporários são zerados;
- o cliente pode retornar ao padrão definido pelo sistema.

Se o usuário tentar sair da área de venda com uma venda em montagem, o sistema deve solicitar confirmação.

Exemplo:

> Deseja realmente sair? A venda em andamento será descartada.

Ao abandonar uma venda em montagem:

- nenhum efeito deve ocorrer no estoque;
- nenhum efeito deve ocorrer no caixa;
- nenhum efeito deve ocorrer no crediário.

---

### 4.1.14 Histórico da venda

Cada venda finalizada deve preservar:

- número da venda;
- data e hora;
- cliente;
- usuário responsável;
- produtos;
- atributos dos produtos;
- quantidade;
- preço original;
- preço praticado;
- desconto;
- acréscimo;
- formas de pagamento;
- valor total;
- situação.

O histórico deve permanecer disponível mesmo após:

- cancelamento;
- devolução;
- troca.

---

### 4.1.15 Edição após finalização

Uma venda finalizada não pode ser editada diretamente.

Correções devem ocorrer através de processos específicos, como:

- cancelamento;
- devolução;
- troca.

O histórico original deve ser preservado.

---

### 4.1.16 Comprovante e impressão

Após a finalização, o sistema deve permitir imprimir um comprovante em formato simples, semelhante a um cupom.

O comprovante deve apresentar:

- logo da empresa ou nome **MOVA SPORTS** no cabeçalho;
- data;
- hora;
- número da venda;
- cliente;
- produtos;
- atributos dos produtos, quando aplicável;
- quantidade;
- formas de pagamento;
- quantidade de parcelas, quando houver crediário;
- valor pago;
- troco, quando houver;
- valor total.

O comprovante deve priorizar leitura simples e impressão prática.

---

### 4.1.17 Regras gerais de segurança

Não é permitido:

- concluir venda com estoque insuficiente;
- concluir venda com pagamento inconsistente ou incompleto;
- gerar efeitos financeiros antes da confirmação;
- editar diretamente uma venda já finalizada;
- apagar o histórico para corrigir erros;
- baixar estoque duas vezes pela mesma venda;
- gerar movimentações financeiras duplicadas pela mesma operação.

Toda venda deve permanecer rastreável.

## 4.2 Condicional

O condicional funciona como uma reserva temporária de produtos para um cliente.

O cliente é obrigatório.

A tela deve permitir:

- selecionar o cliente;
- adicionar produtos;
- visualizar os produtos enviados;
- finalizar o condicional posteriormente.

### Reserva de estoque

Produtos enviados em condicional devem ficar indisponíveis para outras vendas enquanto o condicional estiver ativo.

Exemplo:

Se existe apenas:

- 1 calça;
- tamanho M;
- cor vermelha;

e essa peça estiver em um condicional ativo, ela não poderá ser vendida para outro cliente.

O estoque físico permanece rastreável, mas a quantidade deve ser considerada reservada.

### Finalização do condicional

O condicional pode resultar em:

- venda dos produtos;
- devolução dos produtos;
- venda parcial e devolução parcial.

Produtos devolvidos voltam a ficar disponíveis.

Produtos vendidos são definitivamente baixados do estoque.

---

## 4.3 Devolução e Troca

O sistema deve permitir localizar uma venda por:

- Código ou número da venda;
- CPF do cliente;
- Nome do cliente.

Após localizar a venda, o sistema deve:

- listar os produtos;
- apresentar o resumo da venda;
- permitir selecionar os itens envolvidos;
- solicitar o motivo da devolução ou troca.

### Motivos

O sistema pode possuir motivos pré-cadastrados e também permitir a opção:

- Outro.

Quando necessário, deve permitir uma descrição complementar.

### Estoque

Produtos efetivamente devolvidos devem retornar ao estoque.

Toda devolução ou troca deve permanecer registrada no histórico.

---

## 4.4 Histórico de Vendas


### 4.4.1 Objetivo

O Histórico de Vendas deve permitir consultar todas as vendas realizadas e acessar os detalhes completos de cada operação.

O histórico deve preservar vendas:

- concluídas;
- canceladas;
- devolvidas.

As vendas não devem ser apagadas do histórico.

---

### 4.4.2 Busca

O sistema deve permitir localizar vendas por:

- CPF do cliente;
- nome do cliente;
- número da venda.

A busca deve funcionar em conjunto com os demais filtros disponíveis.

---

### 4.4.3 Filtro por período

O usuário deve poder definir:

- data inicial;
- data final.

Os resultados e indicadores devem considerar somente as vendas dentro do intervalo selecionado.

---

### 4.4.4 Filtro por situação

O histórico deve permitir filtrar por:

- Concluída;
- Cancelada;
- Devolvida.

Quando nenhum filtro específico de situação estiver aplicado, o sistema pode apresentar todas as situações.

---

### 4.4.5 Indicadores

A tela deve apresentar três cards:

- Total de vendas;
- Total faturado;
- Ticket médio.

Os indicadores devem ser atualizados conforme:

- busca;
- intervalo de datas;
- situação selecionada;
- demais filtros aplicados.

Os cards devem representar exatamente o conjunto de resultados filtrados.

---

### 4.4.6 Total de vendas

Exibe a quantidade de vendas correspondente aos filtros aplicados.

A regra deve respeitar a situação selecionada.

---

### 4.4.7 Total faturado

Exibe o valor financeiro correspondente às vendas encontradas pelos filtros.

O cálculo deve respeitar:

- situação da venda;
- cancelamentos;
- devoluções;
- regras de valores líquidos definidas neste documento.

---

### 4.4.8 Ticket médio

O ticket médio deve ser calculado com base nos resultados válidos do filtro aplicado.

Fórmula geral:

Ticket médio = Total faturado ÷ Quantidade de vendas consideradas

O sistema deve evitar divisão por zero quando não houver resultados.

---

### 4.4.9 Listagem

A listagem deve apresentar:

- Número da venda;
- Data;
- Cliente;
- Quantidade de itens;
- Valor total;
- Forma de pagamento;
- Situação da venda;
- Ação “Ver detalhes”.

Quando uma venda possuir pagamento misto, a coluna de forma de pagamento deve indicar claramente que existem múltiplas formas.

---

### 4.4.10 Ordenação

As vendas devem ser exibidas das mais recentes para as mais antigas.

A ordenação padrão deve considerar:

- data;
- hora.

---

### 4.4.11 Paginação

A listagem deve apresentar até 10 vendas por página.

Quando houver mais resultados, o sistema deve permitir navegar entre as páginas sem perder os filtros aplicados.

---

### 4.4.12 Detalhes da venda

Ao clicar em **Ver detalhes**, o sistema deve apresentar:

- número da venda;
- data e hora;
- cliente;
- usuário responsável pela venda;
- produtos vendidos;
- atributos dos produtos;
- quantidade de cada produto;
- preço de cada produto;
- preço original, quando aplicável;
- descontos;
- acréscimos;
- valor total;
- formas de pagamento;
- situação atual da venda.

---

### 4.4.13 Crediário

Quando a venda possuir crediário, os detalhes devem apresentar:

- valor lançado no crediário;
- quantidade de parcelas;
- identificação das parcelas;
- vencimentos;
- situação das parcelas;
- valores pagos;
- saldo restante.

---

### 4.4.14 Devoluções

Quando houver devolução vinculada à venda, os detalhes devem apresentar:

- produtos devolvidos;
- quantidades;
- data da devolução;
- valores correspondentes;
- situação da devolução;
- impactos registrados no histórico.

O histórico da venda original deve ser preservado.

---

### 4.4.15 Cancelamento

Quando a venda estiver cancelada, os detalhes devem apresentar:

- situação de cancelada;
- data e hora do cancelamento;
- motivo;
- usuário responsável pelo cancelamento;
- informações dos estornos realizados;
- eventuais avisos de conciliação manual.

A venda original deve permanecer integralmente disponível para consulta.

---

### 4.4.16 Impressão

O sistema deve permitir imprimir os detalhes da venda diretamente pelo Histórico.

A impressão deve apresentar as informações relevantes da operação de forma clara e organizada.

---

### 4.4.17 Regras gerais

- O histórico não deve apagar vendas antigas.
- Os filtros devem funcionar em conjunto.
- Os indicadores devem acompanhar os filtros aplicados.
- As vendas mais recentes devem aparecer primeiro.
- A paginação não deve remover os filtros selecionados.
- Cancelamentos e devoluções devem permanecer rastreáveis.
- Os detalhes devem utilizar os dados históricos da venda, e não os preços atuais do cadastro dos produtos.

## 4.5 Cancelamento de Venda


### 4.5.1 Objetivo

O cancelamento permite desfazer uma venda finalizada de forma controlada, preservando todo o histórico e revertendo corretamente os efeitos da operação.

Uma venda cancelada nunca deve ser apagada.

---

### 4.5.2 Permissão

Qualquer usuário autorizado a utilizar o sistema pode cancelar uma venda.

O usuário responsável pelo cancelamento deve ficar registrado.

---

### 4.5.3 Localização da venda

O sistema deve permitir localizar a venda por:

- CPF do cliente;
- nome do cliente;
- número da venda.

---

### 4.5.4 Motivo obrigatório

Todo cancelamento exige um motivo.

O cancelamento não pode ser confirmado sem que o motivo seja informado.

Devem ser registrados:

- motivo;
- data e hora;
- usuário responsável.

---

### 4.5.5 Confirmação

Antes de concluir o cancelamento, o sistema deve:

- apresentar os dados da venda;
- informar os efeitos da operação;
- solicitar confirmação do usuário.

Após confirmado, o cancelamento não deve permitir edição direta da venda original.

---

### 4.5.6 Estoque

Ao cancelar uma venda:

- os produtos devem retornar ao estoque quando aplicável;
- o retorno deve ocorrer apenas uma vez;
- o sistema não pode gerar estoque duplicado.

Uma segunda tentativa de cancelamento não pode devolver os produtos novamente.

---

### 4.5.7 Tratamento financeiro

O cancelamento deve reverter somente valores efetivamente recebidos.

#### Dinheiro

Gerar saída no caixa pelo valor efetivamente recebido em dinheiro.

#### Pix

Gerar saída financeira correspondente ao valor efetivamente recebido por Pix.

#### Débito e Crédito pendentes

Cancelar o recebível correspondente.

Não gerar saída financeira quando o valor ainda não tiver sido recebido.

#### Débito e Crédito já recebidos

Cancelar o recebível e gerar saída somente pelo valor efetivamente recebido.

#### Crediário não pago

Cancelar as parcelas vinculadas.

Não gerar saída financeira para valores que não foram recebidos.

#### Crediário já pago

Estornar somente os valores efetivamente pagos, respeitando a forma de pagamento utilizada em cada baixa.

#### Pagamento misto

Cada componente deve ser tratado separadamente conforme sua forma de pagamento e situação financeira.

---

### 4.5.8 Registros antigos sem vínculo confiável

Quando não existir vínculo seguro entre uma movimentação financeira antiga e a venda:

- não realizar estorno automático por aproximação;
- preservar os registros existentes;
- manter a parte ambígua intacta;
- informar ao usuário a necessidade de conciliação manual.

O sistema deve priorizar segurança e rastreabilidade.

---

### 4.5.9 Idempotência

O cancelamento deve ser idempotente.

Uma venda já cancelada não pode gerar novamente:

- retorno de estoque;
- estorno financeiro;
- cancelamento de parcelas;
- cancelamento de recebíveis.

Uma segunda tentativa deve ser rejeitada sem produzir novos efeitos.

---

### 4.5.10 Histórico

A venda cancelada deve preservar:

- venda original;
- produtos;
- preços;
- formas de pagamento;
- cliente;
- usuário da venda;
- usuário responsável pelo cancelamento;
- data e hora do cancelamento;
- motivo;
- movimentações de estoque;
- estornos financeiros;
- recebíveis cancelados;
- parcelas canceladas;
- avisos de conciliação manual.

---

### 4.5.11 Dashboard e indicadores

Vendas canceladas não devem compor os indicadores de vendas válidas.

O cancelamento deve ser refletido corretamente em:

- faturamento;
- lucro;
- quantidade vendida;
- formas de pagamento;
- ranking de marcas;
- estoque;
- caixa e financeiro, conforme os efeitos reais da operação.

---

### 4.5.12 Regras de segurança

Não é permitido:

- apagar uma venda para simular cancelamento;
- cancelar a mesma venda duas vezes;
- devolver estoque duas vezes;
- gerar estorno financeiro duplicado;
- estornar valores não recebidos;
- adivinhar vínculos financeiros antigos;
- alterar silenciosamente o histórico.

Toda operação deve permanecer rastreável.

# 5. CREDIÁRIO


## Objetivo

O crediário permite realizar vendas a prazo vinculadas a um cliente cadastrado e controlar parcelas, recebimentos, atrasos, renegociações e saldo devedor.

---

## 5.1 Cliente obrigatório

Toda venda em crediário exige um cliente previamente cadastrado.

A venda em crediário não pode utilizar o cliente padrão de venda rápida.

Ao finalizar a venda, o crediário deve ser automaticamente vinculado à conta do cliente selecionado.

---

## 5.2 Limite de crédito

Antes de concluir uma venda em crediário, o sistema deve verificar o limite de crédito do cliente.

Caso o limite seja excedido:

- exibir um alerta;
- permitir que o usuário autorize a venda;
- ao autorizar, aumentar o limite de crédito do cliente para comportar a operação.

A venda não deve ser bloqueada definitivamente apenas por exceder o limite.

---

## 5.3 Parcelamento

O crediário permite parcelamento em até 3 parcelas.

### Regras

- primeira parcela: vencimento em 30 dias;
- parcelas seguintes: intervalo de 30 dias;
- máximo: 3 parcelas no crediário.

Exemplo:

- Compra: 10/07;
- 1ª parcela: 09/08;
- 2ª parcela: 08/09;
- 3ª parcela: 08/10.

O cálculo exato das datas deve respeitar o comportamento de datas do sistema.

---

## 5.4 Entrada + Crediário

Quando houver entrada e parcelamento:

- a entrada deve ser registrada como uma forma de pagamento separada;
- somente o saldo restante deve gerar o crediário.

Exemplo:

Venda: R$ 1.000,00

- Entrada em Pix: R$ 400,00;
- Crediário: R$ 600,00 em 3 parcelas.

A venda possui duas formas de pagamento:

- Pix: R$ 400,00;
- Crediário: R$ 600,00.

O limite de crédito deve considerar apenas o valor efetivamente lançado no crediário.

---

## 5.5 Tela do Crediário

A tela deve possuir:

- botão para cadastrar novo cliente;
- busca por nome ou CPF;
- indicadores resumidos;
- filtros por situação;
- listagem dos crediários;
- detalhes da conta selecionada.

---

## 5.6 Busca

Permitir busca por:

- Nome;
- CPF.

Os indicadores da tela devem refletir os resultados da busca.

Quando nenhuma busca tiver sido realizada, os indicadores relacionados à busca não devem apresentar valores de um cliente específico.

---

## 5.7 Indicadores

Após realizar uma busca, exibir três cards:

### Valor a receber

Saldo total ainda pendente.

### Valor em dia

Saldo das parcelas abertas que ainda não estão vencidas.

### Valor em atraso

Saldo das parcelas vencidas e ainda não quitadas.

Os valores devem considerar pagamentos parciais.

---

## 5.8 Filtros da listagem

A listagem deve possuir os filtros:

- Todos;
- Em dia;
- Atrasadas;
- Quitadas.

---

## 5.9 Listagem

A listagem principal deve apresentar:

- Cliente;
- Limite de crédito;
- Saldo devedor;
- Parcelas;
- Situação;
- Ação.

A ação principal deve ser:

**RECEBER**

Ao selecionar um cliente ou crediário, a área lateral deve apresentar os detalhes da venda e da conta.

---

## 5.10 Recebimento de parcela

Ao clicar em **RECEBER**, abrir a tela de recebimento.

Exibir:

- cliente;
- venda de origem;
- parcela;
- valor original;
- valor já pago;
- saldo atual;
- vencimento;
- situação.

O usuário pode receber:

- o valor total;
- um valor parcial.

Um pagamento parcial não altera automaticamente a data de vencimento.

O saldo restante continua vinculado à parcela original.

---

## 5.11 Pagamento parcial

Qualquer parcela pode receber pagamento parcial.

Após o pagamento:

- registrar o valor recebido;
- atualizar o total pago;
- atualizar o saldo restante;
- preservar o vencimento original;
- manter a parcela aberta enquanto houver saldo.

O histórico de cada pagamento deve ser preservado.

---

## 5.12 Juros e multa

Juros e multas nunca são calculados ou aplicados automaticamente.

Quando houver necessidade, o usuário pode informar manualmente:

- juros;
- multa;
- outros acréscimos negociados.

Esses valores devem ficar registrados separadamente do valor original da parcela sempre que a estrutura do sistema permitir.

O sistema deve preservar:

- valor original;
- acréscimos;
- valor efetivamente recebido.

---

## 5.13 Pagamento com cartão e acréscimos negociados

O crediário pode ser pago utilizando qualquer forma de pagamento permitida pelo sistema.

São permitidos:

- Dinheiro;
- Pix;
- Débito;
- Crédito;
- outras formas já suportadas pelo sistema.

Quando o pagamento for realizado por cartão, poderá existir um acréscimo negociado com o cliente.

Esse acréscimo:

- deve ser informado manualmente;
- nunca deve ser aplicado automaticamente;
- deve ficar registrado no recebimento.

---

## 5.14 Renegociação

A renegociação é uma ação distinta do pagamento parcial.

Somente através da opção de renegociação é permitido alterar manualmente a data de vencimento.

A renegociação pode envolver:

- pagamento parcial;
- novo saldo;
- alteração manual do vencimento;
- juros;
- multa;
- outros acréscimos negociados.

O histórico anterior não deve ser apagado.

Deve permanecer registrado:

- vencimento anterior;
- novo vencimento;
- saldo anterior;
- valor pago;
- novo saldo;
- usuário responsável;
- data da renegociação.

---

## 5.15 Situação das parcelas

Uma parcela pode estar:

- Em dia;
- Atrasada;
- Quitada;
- Cancelada, quando vinculada a uma venda cancelada.

### Em dia

Parcela aberta cujo vencimento ainda não ocorreu.

### Atrasada

Parcela aberta cujo vencimento já passou.

### Quitada

Parcela sem saldo pendente.

O status deve ser determinado pelos dados reais da parcela.

---

## 5.16 Histórico da conta

O histórico deve apresentar:

- Data da compra;
- Número da venda;
- Valor da compra;
- Quantidade de parcelas;
- Identificação da parcela;
- Valor original;
- Valor pago;
- Saldo restante;
- Data de vencimento;
- Situação.

Exemplo de identificação:

- 1/3;
- 2/3;
- 3/3.

Também devem ser preservados os históricos de:

- pagamentos parciais;
- juros;
- multas;
- acréscimos;
- renegociações;
- alterações de vencimento.

---

## 5.17 Integração com o Caixa

### Dinheiro e Pix

Pagamentos de crediário realizados em:

- Dinheiro;
- Pix;

geram entrada imediata no caixa.

### Débito e Crédito

Pagamentos realizados em:

- Débito;
- Crédito;

seguem o fluxo financeiro já definido para recebíveis de cartão.

Não devem entrar imediatamente no saldo disponível do caixa quando ainda não tiverem sido efetivamente recebidos.

---

## 5.18 Identificação no Caixa

Uma movimentação originada pelo recebimento de crediário deve permitir identificar:

- Tipo: Entrada;
- Cliente;
- Número da venda;
- Parcela;
- Forma de pagamento;
- Valor.

Exemplo:

**Entrada — João da Silva — Venda #1254 — Parcela 1/3 — Pix**

Isso deve permitir rastrear facilmente a origem da movimentação.

---

## 5.19 Regras de segurança e histórico

O sistema deve:

- preservar o histórico dos pagamentos;
- não apagar parcelas quitadas;
- não apagar renegociações anteriores;
- não duplicar entradas financeiras;
- não permitir que pagamentos ultrapassem o saldo devido sem tratamento explícito;
- manter vínculo entre pagamento, cliente, venda e parcela;
- preservar a forma de pagamento utilizada.

Toda operação financeira deve ser rastreável.

---

## 5.20 Integração com o Score do Cliente

O histórico do crediário deve fornecer dados para o Score do Cliente.

Devem ser considerados, quando a fórmula definitiva for implementada:

- pagamentos em dia;
- atrasos;
- frequência de atrasos;
- parcelas atualmente vencidas;
- histórico de quitação.

Juros ou multas negociados não devem, isoladamente, definir o Score.

O Score deve considerar principalmente o comportamento de pagamento do cliente.

# 6. CAIXA E FINANCEIRO


## 6.1 Objetivo

O módulo de Caixa e Financeiro deve registrar e apresentar as movimentações financeiras da loja de forma contínua, rastreável e cronológica.

O sistema não utiliza fechamento diário de caixa.

O caixa funciona como um saldo contínuo, atualizado a cada movimentação válida.

---

## 6.2 Indicadores

Na parte superior da tela devem existir três cards:

- Total em Caixa;
- Entradas Hoje;
- Saídas Hoje.

### Total em Caixa

Representa o saldo atual disponível no caixa conforme as movimentações registradas.

### Entradas Hoje

Representa a soma das entradas realizadas na data atual.

### Saídas Hoje

Representa a soma das saídas realizadas na data atual.

Os indicadores devem ser atualizados após cada movimentação válida.

---

## 6.3 Caixa contínuo

Não existe fechamento diário de caixa.

O saldo deve continuar de um dia para o outro.

Cada movimentação deve alterar o saldo acumulado.

Fórmula geral:

Saldo resultante = Saldo anterior + Entradas - Saídas

O sistema não pode permitir saldo negativo.

Uma saída superior ao saldo disponível deve ser bloqueada.

---

## 6.4 Formas de pagamento e entrada no caixa

### Dinheiro

Valores recebidos em dinheiro entram diretamente no caixa.

### Pix

Valores recebidos por Pix entram diretamente no caixa.

### Débito e Crédito

Valores de vendas realizadas em Débito ou Crédito não entram automaticamente no caixa.

Esses valores devem ser registrados como recebíveis e somente entram no caixa através do lançamento manual realizado pela função Conta Bancária, quando o valor for efetivamente recebido.

---

## 6.5 Botões principais

No topo da página devem existir os botões:

- Conta Bancária;
- Movimentação.

---

## 6.6 Movimentação manual

O botão Movimentação permite registrar manualmente:

- Entrada;
- Saída.

Toda movimentação manual deve exigir uma descrição.

A movimentação deve registrar:

- tipo de movimentação;
- descrição;
- forma de pagamento;
- tipo de despesa, quando aplicável;
- valor;
- data e hora;
- usuário responsável.

---

## 6.7 Entrada manual

Uma entrada manual deve registrar:

- descrição;
- forma de pagamento;
- valor;
- data e hora;
- usuário responsável.

As formas permitidas para entrada manual operacional são:

- Dinheiro;
- Pix.

Recebimentos de Débito e Crédito provenientes de vendas devem utilizar o fluxo específico de Conta Bancária.

---

## 6.8 Saída manual

Uma saída manual deve registrar:

- descrição;
- tipo de despesa;
- forma de pagamento;
- valor;
- data e hora;
- usuário responsável.

As formas permitidas para saída são:

- Dinheiro;
- Pix;
- Débito.

O sistema deve verificar o saldo antes de confirmar a saída.

Não é permitido concluir uma saída que torne o saldo negativo.

---

## 6.9 Tipos de despesa

Toda saída manual deve possuir um tipo de despesa.

O sistema pode possuir categorias previamente cadastradas, como:

- Gasolina;
- Lanches;
- Estacionamento;
- Material de limpeza;
- Motoboy;
- Acessórios;
- Outros.

O usuário deve poder criar novas categorias de despesa.

As categorias devem permitir organizar e analisar as saídas financeiras.

---

## 6.10 Conta Bancária

A função Conta Bancária é utilizada para registrar manualmente valores efetivamente recebidos provenientes de vendas realizadas por cartão.

O lançamento deve permitir informar:

- data;
- descrição;
- valor de Crédito recebido;
- valor de Débito recebido.

Os valores somente devem entrar no caixa quando o usuário confirmar o recebimento.

O lançamento deve preservar a rastreabilidade dos valores recebidos.

Quando houver vínculo confiável com recebíveis existentes, o sistema deve atualizar a situação correspondente sem duplicar o recebimento.

---

## 6.11 Recebimentos de cartão

Vendas em Débito e Crédito:

- registram normalmente a venda;
- não aumentam imediatamente o saldo do caixa;
- permanecem como valores a receber;
- entram no caixa somente quando efetivamente recebidas e registradas através de Conta Bancária.

O sistema deve impedir que o mesmo recebível seja reconhecido duas vezes.

---

## 6.12 Crediário

O único módulo próprio de contas a receber da loja é o Crediário.

Os recebimentos de crediário seguem as regras definidas na seção específica.

### Dinheiro e Pix

Entram diretamente no caixa quando recebidos.

### Débito e Crédito

Seguem o fluxo financeiro correspondente aos recebíveis de cartão.

---

## 6.13 Linha do tempo do caixa

As movimentações devem ser exibidas em formato de linha do tempo.

As movimentações mais recentes devem aparecer primeiro.

Cada registro deve apresentar, quando aplicável:

- data e hora;
- tipo da movimentação;
- tipo de despesa;
- descrição;
- origem da movimentação;
- forma de pagamento;
- valor da movimentação em destaque;
- saldo resultante após a movimentação.

A origem deve permitir identificar, quando aplicável:

- venda;
- número da venda;
- cliente;
- parcela do crediário;
- movimentação manual;
- conta bancária;
- conta a pagar;
- cancelamento;
- devolução;
- estorno.

---

## 6.14 Saldo por movimentação

Cada movimentação deve preservar o saldo resultante após sua ocorrência.

Isso deve permitir acompanhar a evolução histórica do caixa.

A ordem cronológica das movimentações deve ser respeitada para o cálculo do saldo.

---

## 6.15 Filtros

A tela do caixa deve permitir filtros por:

- intervalo de datas;
- forma de pagamento;
- tipo de movimentação;
- tipo de despesa.

### Intervalo de datas

Ao abrir a página, o período inicial deve apresentar a data atual.

O usuário pode selecionar outro intervalo.

### Forma de pagamento

Permitir filtrar por:

- Dinheiro;
- Pix;
- Débito;
- Crédito.

### Tipo de movimentação

Permitir filtrar por:

- Entrada;
- Saída.

### Tipo de despesa

Permitir filtrar pelas categorias de despesas existentes.

Os filtros devem funcionar em conjunto.

---

## 6.16 Relação de despesas por tipo

O sistema deve permitir visualizar as despesas agrupadas por tipo.

Essa relação deve considerar os filtros aplicados quando pertinente.

As categorias criadas posteriormente pelo usuário também devem ser consideradas.

---

## 6.17 Estorno de movimentação

Uma movimentação financeira já registrada não deve ser apagada ou editada para corrigir um erro.

A correção deve ocorrer através de estorno.

O estorno deve:

- preservar a movimentação original;
- gerar uma movimentação inversa correspondente;
- registrar data e hora;
- registrar o usuário responsável;
- manter vínculo com a movimentação original;
- impedir estorno duplicado.

O histórico deve mostrar claramente:

- movimentação original;
- movimentação de estorno.

---

## 6.18 Exportação

O sistema deve permitir exportar as movimentações do caixa para uma planilha Excel.

A exportação deve respeitar os filtros atualmente aplicados.

A planilha deve representar as linhas exibidas pelo filtro e conter, quando aplicável:

- data e hora;
- tipo da movimentação;
- descrição;
- origem;
- cliente;
- número da venda;
- parcela;
- forma de pagamento;
- tipo de despesa;
- valor;
- saldo resultante.

---

## 6.19 Permissões

Atualmente, qualquer usuário autorizado a acessar o sistema pode:

- registrar entradas;
- registrar saídas;
- criar categorias de despesas;
- registrar recebimentos através de Conta Bancária;
- realizar as demais movimentações permitidas pelo módulo.

Uma futura evolução do sistema de permissões poderá restringir essas ações.

---

## 6.20 Contas a Pagar

### 6.20.1 Objetivo

O módulo de Contas a Pagar deve controlar as obrigações financeiras da loja, seus vencimentos, pagamentos, pagamentos parciais e impactos no caixa.

Toda conta deve permanecer rastreável desde o cadastro até sua quitação, cancelamento ou estorno.

---

### 6.20.2 Cadastro da conta

Cada conta a pagar possui cadastro individual.

O cadastro deve conter:

- Fornecedor;
- Categoria da despesa;
- Descrição;
- Valor;
- Data de emissão;
- Data de vencimento;
- Observações.

Não é permitido anexar arquivos, boletos, notas fiscais ou comprovantes neste momento.

---

### 6.20.3 Fornecedor

Toda conta deve permitir identificar o fornecedor ou credor correspondente.

O fornecedor deve permanecer registrado no histórico da conta.

---

### 6.20.4 Categorias

O sistema deve possuir inicialmente as seguintes categorias:

- Mercadorias;
- Aluguel;
- Energia;
- Água;
- Internet;
- Impostos;
- Salários;
- Serviços;
- Outros.

O usuário pode criar novas categorias.

As categorias devem ser utilizadas nos filtros e indicadores do módulo.

---

### 6.20.5 Parcelamento

Cada conta possui seu próprio cadastro.

Quando uma obrigação possuir várias parcelas, cada parcela deve ser cadastrada como uma conta individual, com:

- seu próprio valor;
- sua própria data de vencimento;
- sua própria situação.

O sistema não deve presumir automaticamente que várias contas pertencem ao mesmo parcelamento, salvo futura implementação específica.

---

### 6.20.6 Situações

Uma conta pode possuir as seguintes situações:

- Pendente;
- Vencida;
- Paga;
- Cancelada.

#### Pendente

Conta ainda não quitada e cujo vencimento ainda não ocorreu.

#### Vencida

Conta com saldo pendente cuja data de vencimento já passou.

#### Paga

Conta sem saldo devedor.

#### Cancelada

Conta cancelada sem pagamento pendente.

O histórico da conta cancelada deve ser preservado.

---

### 6.20.7 Indicadores

A tela deve possuir quatro cards:

- Total de Contas a Pagar;
- Vencidas;
- Vencem Hoje;
- A Vencer.

Os indicadores devem ser atualizados conforme os filtros aplicados.

#### Total de Contas a Pagar

Representa o saldo total pendente das contas encontradas.

#### Vencidas

Representa o saldo pendente das contas cujo vencimento já passou.

#### Vencem Hoje

Representa o saldo pendente das contas com vencimento na data atual.

#### A Vencer

Representa o saldo pendente das contas com vencimento futuro.

Pagamentos parciais devem reduzir os valores apresentados nos indicadores.

---

### 6.20.8 Alertas de vencimento

Contas com vencimento na data atual devem:

- emitir alerta no sistema;
- receber destaque visual na listagem.

Contas vencidas também devem possuir identificação visual clara.

O alerta não deve gerar pagamento ou qualquer movimentação financeira automaticamente.

---

### 6.20.9 Listagem

A listagem deve apresentar:

- Fornecedor;
- Categoria;
- Descrição;
- Vencimento;
- Valor;
- Status;
- Ação.

A ação principal para contas com saldo pendente deve ser:

**PAGAR**

---

### 6.20.10 Ordenação

As contas devem priorizar visualmente:

1. contas vencidas;
2. contas que vencem hoje;
3. contas a vencer.

Dentro de cada grupo, devem ser ordenadas pela data de vencimento.

---

### 6.20.11 Filtros

A tela deve permitir filtros por:

- período;
- categoria;
- status.

O filtro de período deve considerar a data de vencimento, salvo quando a interface indicar explicitamente outro tipo de data.

Os filtros devem funcionar em conjunto.

Os cards devem ser recalculados conforme os resultados filtrados.

---

### 6.20.12 Pagamento

Ao clicar em **PAGAR**, o sistema deve apresentar os dados da conta e permitir informar:

- valor pago;
- forma de pagamento;
- juros;
- multa;
- desconto.

O pagamento pode ser:

- total;
- parcial.

A data do pagamento deve ser registrada automaticamente no momento da operação e não deve ser alterada manualmente pelo usuário.

---

### 6.20.13 Pagamento parcial

Uma conta pode receber pagamentos parciais.

Após um pagamento parcial:

- registrar o valor pago;
- atualizar o total já pago;
- atualizar o saldo restante;
- manter a conta aberta enquanto existir saldo pendente;
- preservar o vencimento original;
- preservar o histórico do pagamento.

O pagamento parcial não altera automaticamente a data de vencimento.

---

### 6.20.14 Juros e multa

Juros e multas devem ser informados manualmente pelo usuário.

O sistema não deve aplicá-los automaticamente.

Sempre que possível, preservar separadamente:

- valor original;
- juros;
- multa;
- desconto;
- valor efetivamente pago;
- saldo restante.

---

### 6.20.15 Desconto

O usuário pode informar manualmente um desconto no momento do pagamento.

O desconto deve ficar registrado no histórico da operação.

O sistema deve preservar a diferença entre:

- valor original da obrigação;
- desconto concedido;
- valor efetivamente pago.

---

### 6.20.16 Formas de pagamento

São permitidas:

- Dinheiro;
- Pix;
- Débito.

Não é permitido utilizar Crédito como forma de pagamento de uma conta a pagar.

---

### 6.20.17 Integração com o Caixa

Todo pagamento confirmado deve gerar automaticamente a saída correspondente no caixa.

A movimentação deve permitir identificar:

- conta de origem;
- fornecedor;
- categoria;
- descrição;
- forma de pagamento;
- valor efetivamente movimentado;
- data e hora;
- usuário responsável.

O sistema não pode gerar a mesma saída duas vezes.

---

### 6.20.18 Contas recorrentes

O cadastro pode permitir marcar uma despesa como recorrente.

Quando configurada como recorrente:

- a recorrência será mensal;
- a despesa deve aparecer novamente no mês seguinte;
- deve manter o mesmo dia de referência;
- cada nova ocorrência deve possuir seu próprio registro.

A recorrência deve gerar somente uma nova conta por mês.

O sistema deve impedir duplicidade da mesma ocorrência mensal.

A conta recorrente original e as ocorrências geradas devem permanecer vinculadas para fins de rastreabilidade.

---

### 6.20.19 Edição antes do pagamento

Uma conta ainda não paga pode ser alterada por qualquer usuário autorizado a acessar o módulo.

As alterações devem preservar rastreabilidade quando envolverem dados financeiros relevantes.

---

### 6.20.20 Conta com pagamento parcial

Após existir qualquer pagamento parcial, alterações que afetem valores financeiros já movimentados não devem apagar ou reescrever silenciosamente o histórico.

Correções devem preservar os pagamentos já realizados.

---

### 6.20.21 Conta paga

Depois que uma conta for paga, ela não pode ser editada diretamente para corrigir valores ou movimentações financeiras.

A correção deve ocorrer através de estorno.

---

### 6.20.22 Estorno

O estorno deve:

- preservar a conta original;
- preservar o pagamento original;
- gerar a movimentação financeira inversa correspondente;
- registrar data e hora;
- registrar usuário responsável;
- manter vínculo com a operação original;
- impedir estorno duplicado.

O sistema não deve apagar o pagamento original.

Após o estorno, a situação e o saldo da conta devem ser recalculados de acordo com os valores efetivamente estornados.

---

### 6.20.23 Cancelamento

Uma conta ainda não paga pode ser cancelada.

O cancelamento:

- não deve gerar saída no caixa;
- deve preservar o cadastro e o histórico;
- deve alterar a situação para Cancelada.

Contas com pagamentos já realizados não devem ser canceladas de forma a apagar os efeitos financeiros existentes.

Nesses casos, os pagamentos devem ser tratados através de estorno.

---

### 6.20.24 Histórico

O histórico da conta deve preservar:

- cadastro original;
- alterações relevantes;
- pagamentos totais;
- pagamentos parciais;
- juros;
- multas;
- descontos;
- estornos;
- cancelamento;
- usuário responsável por cada operação;
- data e hora das operações.

---

### 6.20.25 Permissões

Atualmente, qualquer usuário autorizado a acessar o sistema pode:

- cadastrar contas;
- editar contas ainda não pagas;
- realizar pagamentos;
- criar categorias.

Uma futura evolução do sistema de permissões poderá restringir essas ações.

---

### 6.20.26 Regras de segurança específicas

Não é permitido:

- apagar uma conta para corrigir um pagamento;
- editar silenciosamente uma conta já paga;
- duplicar saídas no caixa;
- pagar valor superior ao saldo devido sem tratamento explícito de juros ou outros acréscimos;
- gerar duas vezes a mesma ocorrência de uma conta recorrente;
- utilizar Crédito como forma de pagamento;
- alterar manualmente a data efetiva de um pagamento concluído.

Toda operação deve permanecer rastreável.

## 6.21 Regras de segurança

Não é permitido:

- saldo negativo;
- apagar movimentações para corrigir erros;
- editar silenciosamente movimentações financeiras concluídas;
- registrar o mesmo recebível duas vezes;
- duplicar entradas ou saídas;
- considerar Débito ou Crédito como recebido antes do efetivo lançamento;
- gerar movimentações sem origem rastreável quando houver uma operação vinculada.

Toda movimentação deve preservar:

- data e hora;
- usuário responsável;
- valor;
- tipo;
- origem;
- forma de pagamento, quando aplicável.

O histórico financeiro deve permanecer auditável.


# 7. USUÁRIOS E PERMISSÕES

## 7.1 Perfis de usuário

O sistema possui dois perfis de usuário:

- Administrador;
- Operador.

Não existem outros níveis ou perfis intermediários de acesso.

O perfil do usuário deve ser obtido dos dados persistidos no servidor.

O frontend não é fonte autoritativa para definição de perfil ou permissão.

---

## 7.2 Administrador

O Administrador possui acesso completo às funções operacionais do sistema.

Além das operações normais do sistema, somente o Administrador pode acessar e alterar as Configurações.

O Administrador pode:

- acessar as Configurações;
- criar usuários;
- editar usuários;
- alterar o perfil de usuários;
- desativar usuários;
- desbloquear usuários bloqueados por tentativas de login;
- redefinir a senha de outros usuários sem necessidade da senha anterior.

O Administrador também possui acesso aos indicadores gerenciais restritos definidos pelo sistema.

Atualmente são restritos ao Administrador:

- Lucro do Mês;
- Valor financeiro do estoque;
- Configurações.

Não existem outras restrições operacionais específicas para o perfil Operador, salvo quando expressamente definidas em outra regra de negócio.

---

## 7.3 Operador

O Operador possui acesso às funções operacionais do sistema.

O Operador pode, entre outras operações:

- cadastrar clientes;
- editar clientes;
- alterar limite de crédito de clientes;
- cadastrar produtos;
- editar produtos;
- realizar vendas;
- cancelar vendas;
- registrar devoluções;
- registrar trocas;
- criar e movimentar condicionais;
- receber parcelas do crediário;
- realizar renegociações, quando o fluxo estiver disponível;
- registrar movimentações de caixa;
- pagar contas;
- realizar operações de estoque e inventário conforme as regras do respectivo módulo.

O Operador não possui acesso às Configurações.

O Operador também não recebe os indicadores gerenciais protegidos:

- Lucro do Mês;
- Valor financeiro do estoque.

Não devem ser criadas outras limitações para o Operador sem definição expressa nas regras de negócio.

---

## 7.4 Cadastro de usuário

O cadastro de usuário possui:

- nome;
- login;
- senha;
- perfil.

O perfil deve ser:

- Administrador;
- Operador.

O login deve identificar unicamente o usuário dentro do sistema.

Não permitir dois usuários ativos ou cadastrados com o mesmo login quando isso gerar ambiguidade de autenticação.

---

## 7.5 Alteração da própria senha

Cada usuário pode alterar a própria senha.

Para alterar a própria senha, o usuário deve informar:

- senha atual;
- nova senha;
- confirmação da nova senha.

A senha atual deve ser validada pelo backend.

Se a senha atual estiver incorreta, a alteração deve ser recusada.

A nova senha e sua confirmação devem coincidir.

A senha nunca deve ser armazenada em texto aberto.

---

## 7.6 Redefinição de senha pelo Administrador

O Administrador pode redefinir a senha de outro usuário.

Nesse fluxo, não é necessário informar a senha antiga do usuário alterado.

A redefinição deve ser permitida somente para Administradores autenticados.

O Operador não pode redefinir a senha de outro usuário.

A alteração deve preservar o cadastro e o histórico operacional do usuário.

---

## 7.7 Desativação de usuário

Usuários não devem ser excluídos permanentemente.

O Administrador pode desativar um usuário.

Um usuário desativado:

- permanece cadastrado;
- permanece vinculado às operações históricas realizadas;
- não pode realizar login;
- não pode iniciar nova sessão.

Vendas, cancelamentos, devoluções, recebimentos e demais operações históricas vinculadas ao usuário devem permanecer preservadas.

A desativação não remove ou altera o histórico operacional.

---

## 7.8 Alteração de perfil

O Administrador pode alterar o perfil de outro usuário.

São permitidas as alterações:

- Operador para Administrador;
- Administrador para Operador.

A alteração deve passar a valer conforme o perfil persistido no servidor.

O sistema não pode ficar sem nenhum Administrador ativo.

Não permitir uma alteração de perfil ou desativação que resulte em zero Administradores ativos.

Se a operação remover o último Administrador ativo, ela deve ser recusada.

Essa proteção deve existir no backend.

---

## 7.9 Rastreabilidade por usuário

As operações do sistema devem preservar o usuário responsável quando essa informação for necessária ao histórico operacional.

O objetivo é permitir identificar quem realizou uma operação.

Exemplos:

- venda realizada por determinado usuário;
- cancelamento realizado por determinado usuário;
- devolução registrada por determinado usuário;
- recebimento do crediário registrado por determinado usuário.

O histórico de vendas deve permitir identificar o usuário responsável pela venda.

Operações relacionadas devem preservar o usuário responsável quando a estrutura do módulo exigir rastreabilidade.

Não existe, neste momento, regra para criação de módulo de produtividade, monitoramento de funcionários ou avaliação de desempenho por usuário.

A identificação do usuário possui finalidade de rastreabilidade operacional.

---

## 7.10 Login

O acesso ao sistema é realizado por:

- login;
- senha.

O backend deve validar:

- existência do usuário;
- situação ativa do usuário;
- situação de bloqueio;
- senha.

Usuário desativado não pode realizar login.

Usuário bloqueado por tentativas inválidas não pode realizar login, mesmo que posteriormente informe a senha correta.

---

## 7.11 Tentativas inválidas de login

Cada usuário pode realizar no máximo 5 tentativas consecutivas de login com senha incorreta.

O comportamento deve ser:

1ª tentativa incorreta:
- informar senha incorreta.

2ª tentativa incorreta:
- informar senha incorreta.

3ª tentativa incorreta:
- informar que a senha está incorreta;
- informar que restam 2 tentativas antes do bloqueio.

4ª tentativa incorreta:
- informar que a senha está incorreta;
- informar que resta 1 tentativa antes do bloqueio.

5ª tentativa incorreta:
- bloquear o usuário;
- informar que o usuário foi bloqueado.

Após o bloqueio:

- o usuário não pode realizar login;
- informar a senha correta não remove o bloqueio;
- o contador não deve ser reiniciado automaticamente por tempo;
- somente um Administrador pode desbloquear o usuário.

A proteção e a contagem das tentativas devem existir no backend.

Não confiar apenas em controle realizado pelo frontend.

---

## 7.12 Desbloqueio de usuário

Somente o Administrador pode desbloquear um usuário bloqueado.

Ao desbloquear:

- remover o estado de bloqueio;
- zerar o contador de tentativas inválidas.

O desbloqueio não altera:

- senha;
- perfil;
- histórico;
- operações anteriores do usuário.

Após o desbloqueio, o usuário pode realizar uma nova tentativa de login normalmente.

---

## 7.13 Login realizado com sucesso

Quando o login for realizado com sucesso:

- autenticar o usuário;
- carregar o perfil persistido no servidor;
- iniciar a sessão;
- aplicar as permissões correspondentes ao perfil.

Uma autenticação válida deve zerar o contador de tentativas inválidas anteriores, desde que o usuário ainda não esteja bloqueado.

Usuário já bloqueado não pode remover o próprio bloqueio apenas informando a senha correta.

---

## 7.14 Opção “Lembrar-me”

A tela de login pode possuir a opção:

- Lembrar-me.

Quando selecionada, a sessão pode permanecer ativa no dispositivo conforme a política de sessão do sistema.

A opção Lembrar-me não pode:

- armazenar a senha em texto aberto;
- exibir a senha posteriormente;
- utilizar armazenamento inseguro da senha para realizar login automático.

A persistência deve ocorrer através do mecanismo seguro de sessão adotado pelo sistema.

Quando a opção não estiver selecionada, utilizar o comportamento normal de sessão definido pela aplicação.

---

## 7.15 Permissões autoritativas no backend

Permissões não devem ser protegidas apenas visualmente.

O backend deve validar o perfil persistido do usuário para operações restritas.

Atualmente exigem perfil Administrador:

- acesso e alteração das Configurações;
- gerenciamento de usuários;
- criação de usuários;
- edição administrativa de usuários;
- alteração de perfil;
- desativação de usuários;
- desbloqueio de usuários;
- redefinição administrativa de senha;
- acesso aos indicadores gerenciais protegidos.

O frontend pode ocultar botões, menus, páginas ou cards conforme o perfil.

Entretanto, ocultar um elemento na interface não substitui a validação de autorização no backend.

Parâmetros enviados pelo navegador não podem definir o perfil ou elevar a permissão do usuário.

---

## 7.16 Dados gerenciais protegidos

Os seguintes dados são restritos ao Administrador:

- Lucro do Mês;
- Valor financeiro do estoque.

Esses dados devem ser protegidos no backend.

Para usuários Operadores:

- os campos protegidos devem ser omitidos da resposta quando aplicável;
- não devem ser enviados e apenas escondidos visualmente.

Não existem outras restrições de visualização de dados definidas neste momento.

O Operador pode acessar os demais dados operacionais necessários ao funcionamento do sistema.

---

## 7.17 Configurações

A área de Configurações é exclusiva do Administrador.

O Operador:

- não deve visualizar a opção de Configurações na navegação;
- não deve acessar a área diretamente;
- não deve executar operações de alteração de Configurações através da API.

A restrição deve existir no backend e no frontend.

---

## 7.18 Preservação histórica

Alterações realizadas no cadastro de um usuário não devem modificar retroativamente o histórico das operações já realizadas.

A alteração de:

- nome;
- senha;
- perfil;
- situação ativa ou desativada;

não deve apagar vendas, recebimentos ou demais registros históricos vinculados ao usuário.

O identificador persistente do usuário deve ser preservado para rastreabilidade.

Quando necessário para exibição histórica, o sistema deve utilizar os dados preservados na operação ou o vínculo persistente disponível, sem atribuir uma operação antiga a outro usuário.

---

## 7.19 Regras gerais de segurança de usuários

O sistema deve:

- armazenar senhas utilizando hash seguro;
- nunca armazenar senha em texto aberto;
- nunca retornar senha ou hash de senha em APIs;
- validar autorização no backend;
- impedir login de usuário desativado;
- impedir login de usuário bloqueado;
- impedir que o sistema fique sem Administrador ativo;
- preservar histórico de usuários desativados;
- impedir elevação de perfil pelo frontend;
- registrar o usuário responsável nas operações que exigem rastreabilidade.

Não existe exclusão permanente de usuário pelo fluxo normal do sistema.

# 8. CATÁLOGO

## 8.1 Finalidade do Catálogo

O Catálogo é uma área interna do sistema destinada à consulta visual dos produtos disponíveis na loja.

O Catálogo funciona como vitrine e ferramenta de consulta para os usuários da MOVA SPORTS.

O Catálogo:

- não finaliza vendas;
- não possui carrinho;
- não reserva produtos;
- não altera estoque;
- não gera pedidos;
- não gera movimentações financeiras;
- não gera condicionais;
- não produz efeitos operacionais sobre o produto.

A consulta ao Catálogo não modifica a disponibilidade do estoque.

As operações de venda, reserva e movimentação de produtos devem continuar sendo realizadas nos respectivos módulos do sistema.

---

## 8.2 Acesso ao Catálogo

O Catálogo é acessado somente por usuários autenticados da loja.

Não existe, neste momento, Catálogo público.

O Catálogo não deve ser disponibilizado diretamente por link público para clientes.

Administrador e Operador podem acessar o Catálogo.

O acesso deve respeitar a autenticação normal do sistema.

A possibilidade futura de criação de Catálogo público ou compartilhável não faz parte da regra atual.

---

## 8.3 Produtos exibidos

O Catálogo deve exibir somente produtos com estoque disponível maior que zero.

O estoque disponível deve considerar:

- estoque real;
- quantidades reservadas em condicionais ativos.

A regra conceitual é:

Estoque disponível = Estoque real - Quantidade reservada

Produto com estoque disponível igual ou inferior a zero não deve aparecer no Catálogo.

Exemplo:

Estoque real:
1 unidade

Reservado em condicional:
1 unidade

Estoque disponível:
0 unidades

Resultado:

O produto não aparece no Catálogo.

O Catálogo não deve utilizar somente o estoque físico bruto para definir a disponibilidade.

---

## 8.4 Produto reservado em condicional

Produtos reservados em condicionais ativos devem reduzir a quantidade disponível para o Catálogo.

A reserva deve considerar as regras oficiais do módulo Condicional.

Se todas as unidades disponíveis estiverem reservadas, o produto deve deixar de aparecer no Catálogo.

Se apenas parte do estoque estiver reservada e ainda existir estoque disponível maior que zero, o produto permanece no Catálogo.

Quando uma peça reservada retornar ao estoque disponível, o produto pode voltar a aparecer automaticamente.

---

## 8.5 Produtos com estoque zero

Produtos com estoque disponível igual a zero não devem aparecer no Catálogo.

O produto não deve ser exibido apenas porque:

- possui cadastro ativo;
- possui foto;
- possui preço;
- já teve estoque anteriormente.

A disponibilidade atual é obrigatória para exibição.

Quando o produto voltar a possuir estoque disponível maior que zero, deve voltar a aparecer no Catálogo.

Não é necessária ativação manual do produto para que ele reapareça.

---

## 8.6 Combinações de produtos

Cada combinação cadastrada de produto deve permanecer separada no Catálogo.

Não agrupar automaticamente produtos por:

- nome;
- modelo;
- marca;
- cor;
- tamanho.

Exemplo:

- Camiseta Nike preta P;
- Camiseta Nike preta M;
- Camiseta Nike preta G.

Cada cadastro deve aparecer como um produto separado.

Essa regra segue a estrutura atual de cadastro, na qual cada combinação pode possuir:

- código próprio;
- estoque próprio;
- tamanho próprio;
- cor própria.

O sistema não deve deduzir automaticamente que produtos semelhantes pertencem ao mesmo modelo.

Um futuro agrupamento por modelo dependerá de estrutura e regra específica.

---

## 8.7 Informações do card do produto

Cada produto exibido no Catálogo deve apresentar:

- foto;
- nome;
- marca;
- preço de venda;
- tamanho;
- cor;
- situação de disponibilidade.

O card deve priorizar a apresentação visual do produto.

O Catálogo não deve apresentar no card:

- preço de custo;
- valor financeiro do estoque;
- margem de lucro;
- quantidade exata em estoque;
- dados financeiros internos.

O código interno do produto não precisa ser apresentado no card.

---

## 8.8 Situação de disponibilidade

O Catálogo deve apresentar a situação de disponibilidade do produto.

São utilizadas as seguintes apresentações:

- Disponível;
- Última unidade.

Exibir:

Disponível

quando o estoque disponível for maior que 1.

Exibir:

Última unidade

quando o estoque disponível for exatamente 1.

Não apresentar a quantidade exata disponível.

Exemplos:

Estoque disponível:
8 unidades

Apresentação:
Disponível

Estoque disponível:
2 unidades

Apresentação:
Disponível

Estoque disponível:
1 unidade

Apresentação:
Última unidade

Estoque disponível:
0 unidades

Resultado:
Produto não exibido no Catálogo.

---

## 8.9 Busca de produtos

O Catálogo deve possuir campo de busca.

A busca deve permitir localizar produtos por:

- nome;
- marca;
- categoria;
- cor;
- tamanho.

A busca deve considerar os dados cadastrados do produto.

Exemplos de busca:

- Nike;
- camiseta;
- preta;
- G.

A busca deve atuar sobre os produtos disponíveis para exibição no Catálogo.

Produtos sem estoque disponível não devem reaparecer apenas por corresponderem ao texto pesquisado.

---

## 8.10 Filtros do Catálogo

O Catálogo deve possuir filtros para facilitar a consulta dos produtos.

Os filtros são:

- Categoria;
- Marca;
- Tamanho;
- Cor;
- Faixa de preço.

Os filtros podem ser utilizados em conjunto.

Exemplo:

Categoria:
Camiseta

Marca:
Nike

Tamanho:
G

Cor:
Preta

O resultado deve considerar simultaneamente os filtros aplicados.

Os filtros não devem incluir produtos sem estoque disponível.

---

## 8.11 Faixa de preço

O filtro de faixa de preço deve utilizar o preço de venda atual cadastrado no produto.

O filtro não deve utilizar:

- preço de custo;
- preço praticado em vendas anteriores;
- descontos concedidos em vendas;
- acréscimos aplicados em vendas anteriores.

A faixa de preço representa o preço atual exibido no Catálogo.

---

## 8.12 Ordenação

O Catálogo deve permitir ordenar os produtos por:

- menor preço;
- maior preço;
- nome.

Menor preço:

ordena pelo preço de venda atual em ordem crescente.

Maior preço:

ordena pelo preço de venda atual em ordem decrescente.

Nome:

ordena os produtos alfabeticamente.

A ordenação deve ser aplicada aos resultados atuais da busca e dos filtros.

---

## 8.13 Produto sem foto

Produto com estoque disponível pode aparecer no Catálogo mesmo quando não possuir foto cadastrada.

Nesse caso, o sistema deve utilizar uma imagem padrão da MOVA SPORTS.

A ausência de foto não deve ocultar automaticamente um produto disponível.

A imagem padrão deve preservar o layout do card e indicar visualmente a ausência da foto específica do produto.

Quando uma foto for adicionada ao cadastro, o Catálogo deve utilizar a foto do produto.

---

## 8.14 Detalhes do produto

Ao selecionar um produto no Catálogo, o sistema deve abrir a visualização de detalhes.

Os detalhes devem apresentar:

- foto em tamanho maior;
- nome;
- marca;
- categoria;
- preço de venda;
- cor;
- tamanho;
- descrição, quando disponível;
- situação de disponibilidade.

A visualização deve permitir fechar ou retornar ao Catálogo.

A abertura dos detalhes não deve:

- reservar o produto;
- alterar estoque;
- iniciar venda automaticamente;
- gerar pedido;
- gerar condicional.

A visualização possui finalidade exclusivamente informativa.

---

## 8.15 Preço exibido no Catálogo

O preço exibido no Catálogo deve ser o preço de venda atual cadastrado no produto.

Alterações de preço realizadas somente durante uma venda não devem alterar o Catálogo.

Exemplo:

Preço cadastrado:
R$ 199,90

Preço praticado em uma venda:
R$ 180,00

Preço exibido no Catálogo:
R$ 199,90

O preço do Catálogo somente deve mudar quando o preço de venda do cadastro do produto for efetivamente alterado.

Descontos e acréscimos de uma venda são históricos daquela operação.

---

## 8.16 Atualização da disponibilidade

O Catálogo deve refletir o estoque disponível atual.

Alterações de disponibilidade podem ocorrer em razão de:

- entrada de estoque;
- venda;
- cancelamento de venda;
- devolução;
- condicional;
- reserva;
- devolução de produto em condicional;
- inventário;
- correção oficial de estoque.

Após uma operação válida que altere o estoque disponível, o Catálogo deve refletir a nova situação.

Exemplo:

Produto possui 1 unidade disponível.

A unidade é enviada em condicional.

Novo estoque disponível:
0

Resultado:
O produto deixa de aparecer no Catálogo.

Se a unidade for devolvida pelo condicional:

Novo estoque disponível:
1

Resultado:
O produto volta ao Catálogo como Última unidade.

---

## 8.17 Atualização automática

O usuário não deve precisar ativar ou desativar manualmente um produto no Catálogo em razão do estoque.

A exibição deve ser determinada automaticamente pelo estoque disponível.

O Catálogo deve utilizar os dados atuais do sistema ao carregar ou atualizar sua listagem.

Não criar um controle manual independente de disponibilidade do Catálogo.

A disponibilidade comercial do produto é consequência do estoque disponível.

---

## 8.18 Exportação do Catálogo em PDF

O Catálogo deve permitir exportação em PDF.

Administrador e Operador podem realizar a exportação.

A exportação deve utilizar os produtos correspondentes à consulta atual do Catálogo.

Devem ser considerados:

- busca aplicada;
- categoria selecionada;
- marca selecionada;
- tamanho selecionado;
- cor selecionada;
- faixa de preço aplicada;
- ordenação selecionada.

Produtos sem estoque disponível não devem ser incluídos no PDF.

---

## 8.19 Conteúdo do PDF do Catálogo

O PDF do Catálogo deve possuir apresentação visual adequada para consulta ou apresentação de produtos.

O PDF pode apresentar:

- identificação MOVA SPORTS;
- foto do produto;
- nome;
- marca;
- preço de venda;
- tamanho;
- cor;
- situação Disponível ou Última unidade.

O PDF não deve apresentar:

- preço de custo;
- margem de lucro;
- valor financeiro do estoque;
- quantidade exata em estoque;
- informações internas de caixa;
- informações de fornecedores;
- dados de clientes.

O código interno do produto não precisa ser apresentado.

---

## 8.20 Estoque no PDF

O PDF não deve apresentar a quantidade exata disponível.

A mesma regra visual do Catálogo deve ser utilizada:

- Disponível;
- Última unidade.

Produtos com estoque disponível igual a zero não devem ser exportados.

A geração do PDF deve validar a disponibilidade atual dos produtos.

Não confiar exclusivamente em uma lista antiga já renderizada no navegador quando o backend possuir dados mais atuais.

---

## 8.21 Segurança dos dados do Catálogo

O Catálogo deve utilizar somente os dados necessários para sua finalidade.

A resposta específica do Catálogo não deve fornecer desnecessariamente:

- preço de custo;
- margem;
- lucro;
- valor financeiro do estoque.

Mesmo sendo uma área interna, a API do Catálogo deve retornar apenas os dados necessários para consulta e exportação.

A ocultação visual de um campo não substitui a limitação dos dados retornados pelo backend.

---

## 8.22 Catálogo e Venda

O Catálogo não substitui a tela de Nova Venda.

Consultar um produto no Catálogo não adiciona automaticamente o produto a uma venda.

O Catálogo não possui carrinho.

O Catálogo não possui botão de finalizar compra.

O preço exibido representa o preço atual cadastrado.

A alteração manual do preço praticado continua sendo realizada somente no fluxo da venda, conforme as regras do módulo Vendas.

---

## 8.23 Catálogo e Condicional

O Catálogo não cria ou altera condicionais.

Consultar um produto não gera reserva.

Produtos já integralmente reservados em condicionais ativos não aparecem no Catálogo.

A criação de um novo condicional deve ocorrer exclusivamente no módulo correspondente.

---

## 8.24 Catálogo e Inventário

O Catálogo não permite corrigir estoque.

Diferenças de estoque devem ser tratadas pelo Inventário, conforme as regras do módulo Estoque.

Após a confirmação válida de um inventário ou correção oficial de estoque, o Catálogo deve refletir o novo estoque disponível.

---

## 8.25 Regras gerais do Catálogo

O sistema deve:

- permitir acesso ao Catálogo somente para usuários autenticados;
- permitir acesso para Administrador e Operador;
- funcionar como vitrine e consulta interna;
- não possuir carrinho;
- não finalizar vendas;
- não reservar produtos;
- não gerar pedidos;
- exibir somente produtos com estoque disponível maior que zero;
- descontar reservas de condicionais ativos;
- manter cada combinação de produto separada;
- apresentar foto, nome, marca, preço, tamanho e cor;
- apresentar Disponível ou Última unidade;
- não apresentar quantidade exata;
- permitir busca por nome, marca, categoria, cor e tamanho;
- permitir filtros por categoria, marca, tamanho, cor e faixa de preço;
- permitir ordenação por menor preço, maior preço e nome;
- utilizar imagem padrão quando o produto não possuir foto;
- permitir visualização de detalhes;
- utilizar o preço atual do cadastro;
- não alterar o preço do Catálogo por desconto ou acréscimo concedido em uma venda;
- atualizar a disponibilidade conforme estoque e reservas;
- permitir exportação do Catálogo em PDF;
- respeitar os filtros e a ordenação na exportação;
- não incluir produtos indisponíveis no PDF;
- não expor dados financeiros internos desnecessários.


# 9. RELATÓRIOS

## 9.1 Finalidade do módulo Relatórios

O módulo Relatórios é destinado à consulta, análise e exportação das informações operacionais e financeiras da MOVA SPORTS.

Os relatórios devem utilizar os mesmos dados e regras oficiais dos respectivos módulos do sistema.

O módulo Relatórios não deve manter cálculos financeiros paralelos ou independentes.

Sempre que uma informação já possuir regra oficial em outro módulo, o relatório deve utilizar a mesma regra.

Os relatórios devem considerar, conforme aplicável:

- vendas válidas;
- cancelamentos;
- devoluções;
- pagamentos mistos;
- crediário;
- condicionais;
- movimentações de caixa;
- recebíveis bancários;
- contas a pagar;
- estoque real;
- estoque reservado;
- estoque disponível;
- custos históricos.

Os relatórios possuem finalidade de consulta e exportação.

A geração ou consulta de um relatório não deve alterar dados operacionais ou financeiros.

---

## 9.2 Acesso aos Relatórios

Administrador e Operador podem acessar o módulo Relatórios.

Os dois perfis podem consultar e exportar relatórios.

As restrições de informações gerenciais por perfil continuam sendo aplicadas.

Somente o Administrador pode visualizar:

- lucro;
- margem de lucro;
- valor financeiro total do estoque.

O Operador não deve receber esses dados em respostas específicas de relatório quando não possuir autorização para visualizá-los.

A ocultação visual de um campo não substitui a autorização no backend.

O backend deve determinar o perfil do usuário autenticado utilizando o cadastro persistido do usuário.

Parâmetros enviados pelo navegador não podem elevar a permissão do usuário.

---

## 9.3 Filtros dos Relatórios

Cada relatório deve possuir os filtros correspondentes à sua finalidade.

Os filtros devem ser aplicados no backend.

A interface pode manter estado visual dos filtros, mas não deve ser a única responsável por limitar os dados retornados.

Quando existir filtro por período, o sistema deve validar:

- data inicial;
- data final;
- formato das datas;
- ordem cronológica do período.

Não permitir período personalizado em que a data inicial seja posterior à data final.

Datas civis devem seguir as regras oficiais do sistema.

Timestamps devem utilizar o fuso operacional America/Sao_Paulo para definição do dia correspondente.

---

## 9.4 Resultado conforme filtros

Os dados apresentados no relatório devem corresponder aos filtros atualmente aplicados.

Os indicadores e totais do relatório também devem ser recalculados conforme os filtros.

A exportação deve utilizar os mesmos critérios da consulta atual.

Não apresentar totais gerais quando a listagem estiver filtrada, salvo quando a interface identificar claramente que se trata de um total geral separado.

Por padrão, os resumos principais devem representar os resultados filtrados.

---

## 9.5 Relatório de Vendas

O sistema deve possuir Relatório de Vendas.

O relatório representa vendas e não linhas individuais de produtos.

Uma venda com vários produtos deve representar uma única venda na listagem principal.

O Relatório de Vendas deve permitir filtros por:

- período;
- cliente;
- usuário;
- produto;
- marca;
- categoria;
- forma de pagamento;
- situação da venda.

Os filtros podem ser utilizados em conjunto.

---

## 9.6 Colunas do Relatório de Vendas

A listagem do Relatório de Vendas deve apresentar, no mínimo:

- número da venda;
- data e hora;
- cliente;
- usuário;
- quantidade de peças;
- total líquido;
- forma ou formas de pagamento;
- situação.

Quando uma venda possuir pagamento misto, o relatório deve identificar as formas utilizadas.

A quantidade de peças deve considerar a quantidade líquida válida quando a finalidade do relatório exigir o resultado após devoluções.

O total líquido deve respeitar as regras oficiais de cancelamento e devolução.

---

## 9.7 Situação das vendas no relatório

O Relatório de Vendas deve permitir identificar vendas:

- concluídas;
- canceladas;
- devolvidas;
- parcialmente devolvidas, quando aplicável.

Vendas canceladas devem permanecer no histórico.

A venda não deve ser apagada do relatório em razão de cancelamento ou devolução.

A situação deve identificar corretamente o estado da operação.

Os efeitos nos totais devem seguir as regras financeiras oficiais.

---

## 9.8 Detalhes da venda no relatório

O Relatório de Vendas deve permitir abrir os detalhes da venda.

Os detalhes devem utilizar as mesmas informações oficiais do Histórico de Vendas.

Devem ser identificáveis, quando aplicável:

- produtos;
- quantidades;
- preço original;
- preço praticado;
- desconto;
- acréscimo;
- formas de pagamento;
- cliente;
- usuário;
- cancelamento;
- devoluções;
- parcelas do crediário.

O módulo Relatórios não deve reconstruir detalhes históricos utilizando o cadastro atual do produto quando existir snapshot histórico da venda.

---

## 9.9 Resumo do Relatório de Vendas

O Relatório de Vendas deve apresentar resumo correspondente aos filtros aplicados.

O resumo deve apresentar:

- quantidade de vendas;
- quantidade líquida de peças vendidas;
- valor líquido vendido.

Para Administrador, apresentar também:

- lucro líquido.

O lucro não deve ser enviado ao Operador pela API específica do relatório.

Vendas canceladas não compõem os resultados líquidos.

Devoluções devem ser consideradas conforme a data e a regra financeira oficial da devolução.

---

## 9.10 Relatório de Produtos Vendidos

O sistema deve possuir Relatório de Produtos Vendidos.

Esse relatório representa produtos e quantidades vendidas.

Ele é diferente do Relatório de Vendas.

Exemplo:

Uma venda contém:

- 2 camisetas;
- 1 calção;
- 1 tênis.

No Relatório de Vendas:

1 venda.

No Relatório de Produtos Vendidos:

4 peças.

O relatório deve utilizar as linhas históricas das vendas como fonte autoritativa.

---

## 9.11 Filtros de Produtos Vendidos

O Relatório de Produtos Vendidos deve permitir filtros por:

- período;
- produto;
- código;
- marca;
- categoria;
- tamanho;
- cor.

Os filtros podem ser utilizados em conjunto.

Marca, tamanho, cor e demais atributos históricos devem utilizar os dados preservados na venda quando disponíveis.

Não utilizar o cadastro atual do produto para alterar a classificação histórica de uma venda antiga.

---

## 9.12 Colunas de Produtos Vendidos

O relatório deve apresentar, no mínimo:

- produto;
- código;
- marca;
- tamanho;
- cor;
- quantidade líquida vendida;
- valor líquido vendido.

Para Administrador, apresentar também:

- custo histórico líquido;
- lucro líquido.

O custo deve utilizar o custo histórico preservado na venda.

Não recalcular o custo de uma venda antiga utilizando o custo atual do cadastro do produto.

---

## 9.13 Devoluções no Relatório de Produtos Vendidos

Devoluções devem reduzir a quantidade líquida vendida.

Também devem reduzir o valor líquido correspondente.

O custo devolvido deve reduzir o custo histórico líquido.

O lucro deve refletir o efeito líquido da devolução.

As regras de desconto proporcional devem seguir as regras oficiais do módulo de devoluções.

Trocas classificadas como exchange devem seguir a regra temporária oficial enquanto o fluxo definitivo de troca não estiver implementado.

---

## 9.14 Relatório de Caixa

O sistema deve possuir acesso ao Relatório de Caixa dentro da área de Relatórios.

O Relatório de Caixa deve utilizar a mesma fonte de dados e as mesmas regras do módulo Caixa.

Não criar um segundo cálculo independente de saldo.

O relatório deve permitir filtros por:

- período;
- tipo de movimentação;
- forma de pagamento;
- tipo de despesa.

Tipo de movimentação compreende:

- entrada;
- saída.

---

## 9.15 Colunas do Relatório de Caixa

O Relatório de Caixa deve apresentar, no mínimo:

- data e hora;
- tipo de movimentação;
- descrição;
- origem;
- cliente, quando aplicável;
- forma de pagamento;
- tipo de despesa, quando aplicável;
- valor;
- saldo.

A coluna cliente pode permanecer vazia quando a movimentação não possuir vínculo com cliente.

A origem deve permitir identificar, quando possível:

- venda;
- crediário;
- conta a pagar;
- movimentação manual;
- estorno;
- outra origem oficial.

---

## 9.16 Resumo do Relatório de Caixa

O Relatório de Caixa deve apresentar resumo conforme os filtros aplicados.

O resumo deve apresentar:

- total de entradas;
- total de saídas;
- saldo correspondente.

Quando aplicável, a interface deve deixar claro se o saldo apresentado representa:

- saldo final do caixa;
- resultado líquido das movimentações filtradas.

Não utilizar a mesma descrição para valores conceitualmente diferentes.

---

## 9.17 Exportação do Relatório de Caixa

O Relatório de Caixa deve poder ser exportado.

A exportação deve respeitar os filtros aplicados.

A exportação não deve incluir movimentações fora do resultado filtrado.

A exportação do Caixa já existente e o acesso pelo módulo Relatórios devem utilizar a mesma regra e fonte de dados.

Não manter dois relatórios de Caixa com cálculos divergentes.

---

## 9.18 Relatório de Crediário

O sistema deve possuir Relatório de Crediário.

O relatório deve permitir filtros por:

- cliente;
- período de vencimento;
- situação.

As situações devem permitir identificar, conforme aplicável:

- em dia;
- atrasada;
- quitada.

O relatório deve utilizar o saldo líquido oficial das parcelas.

---

## 9.19 Colunas do Relatório de Crediário

O Relatório de Crediário deve apresentar:

- cliente;
- número da venda;
- identificação da parcela;
- vencimento;
- valor original;
- valor pago;
- valor devolvido ou abatido;
- saldo;
- situação.

A identificação da parcela deve permitir reconhecer sua posição no parcelamento.

Exemplo futuro ou quando implementado:

1/3
2/3
3/3

O relatório não deve considerar somente `amount - received` quando existir valor devolvido ou abatido oficialmente.

---

## 9.20 Saldo do Crediário nos Relatórios

O saldo da parcela deve utilizar a regra financeira oficial do Crediário.

O cálculo deve considerar, conforme aplicável:

- valor original;
- valor recebido;
- valor devolvido;
- abatimentos oficiais;
- cancelamento.

O relatório deve utilizar o mesmo helper ou regra autoritativa do backend utilizada pelo módulo Crediário.

Não duplicar fórmulas divergentes entre Crediário e Relatórios.

---

## 9.21 Resumo do Relatório de Crediário

O Relatório de Crediário deve apresentar:

- total original;
- total recebido;
- total em aberto;
- total atrasado.

Os valores devem corresponder aos filtros aplicados.

Pagamentos parciais devem ser considerados.

Parcelas parcialmente pagas devem contribuir para o saldo em aberto somente pelo valor restante.

O total atrasado deve considerar apenas o saldo vencido ainda devido.

---

## 9.22 Relatório de Contas a Pagar

O sistema deve possuir Relatório de Contas a Pagar.

O relatório deve permitir filtros por:

- período de emissão;
- período de vencimento;
- fornecedor;
- categoria;
- status.

Os filtros podem ser utilizados em conjunto.

As categorias devem utilizar as categorias cadastradas no módulo Contas a Pagar.

---

## 9.23 Colunas de Contas a Pagar

O relatório deve apresentar:

- fornecedor;
- categoria;
- descrição;
- data de emissão;
- data de vencimento;
- valor original;
- valor pago;
- juros ou multa;
- desconto;
- saldo;
- status.

Os valores devem refletir pagamentos parciais quando existentes.

Contas canceladas devem permanecer identificáveis no histórico.

---

## 9.24 Resumo de Contas a Pagar

O Relatório de Contas a Pagar deve apresentar:

- total cadastrado;
- total pago;
- total pendente;
- total vencido.

Os valores devem corresponder aos filtros aplicados.

O total vencido deve considerar o saldo ainda pendente das contas vencidas.

Uma conta parcialmente paga deve contribuir apenas com seu saldo restante.

---

## 9.25 Relatório de Estoque

O sistema deve possuir Relatório de Estoque.

O relatório deve permitir filtros por:

- produto;
- código;
- marca;
- categoria;
- tamanho;
- cor;
- somente produtos com estoque;
- somente última unidade;
- estoque zero.

Os filtros devem utilizar o estado atual do estoque.

O Relatório de Estoque representa posição atual e não histórico de vendas.

---

## 9.26 Colunas do Relatório de Estoque

Para Administrador e Operador, o relatório deve apresentar:

- código;
- produto;
- marca;
- tamanho;
- cor;
- estoque real;
- quantidade reservada;
- estoque disponível;
- custo unitário.

Somente o Administrador pode visualizar:

- valor financeiro do estoque.

O valor financeiro do estoque deve utilizar o custo atual conforme a regra oficial do Dashboard e Estoque.

O Operador pode visualizar custo unitário.

O Operador não deve receber o valor financeiro total do estoque na API específica do relatório.

---

## 9.27 Estoque disponível no relatório

O estoque disponível deve ser calculado considerando:

Estoque disponível = Estoque real - Quantidade reservada

Reservas em condicionais ativos devem ser consideradas.

O relatório deve diferenciar:

- estoque real;
- reservado;
- disponível.

Não apresentar o estoque real como se fosse integralmente disponível para venda.

---

## 9.28 Filtro Última Unidade

O filtro Última Unidade deve apresentar produtos com estoque disponível exatamente igual a 1.

A quantidade reservada deve ser considerada antes da classificação.

Exemplo:

Estoque real:
2

Reservado:
1

Disponível:
1

Resultado:

O produto deve aparecer no filtro Última Unidade.

---

## 9.29 Relatório de Condicionais

O sistema deve possuir Relatório de Condicionais.

O relatório deve permitir filtros por:

- período de saída;
- cliente;
- situação.

As situações devem incluir:

- aberto;
- atrasado;
- finalizado;
- cancelado.

O relatório deve utilizar os dados oficiais do módulo Condicional.

---

## 9.30 Colunas do Relatório de Condicionais

O relatório deve apresentar:

- cliente;
- data de saída;
- produtos ou quantidade de produtos;
- data prevista de retorno;
- quantidade comprada;
- quantidade devolvida;
- situação.

A listagem deve permitir abrir os detalhes do condicional.

Os detalhes devem preservar o histórico dos produtos vinculados à operação.

---

## 9.31 Condicionais atrasados

Um condicional deve ser classificado como atrasado conforme a regra oficial do módulo Condicional.

O relatório não deve inventar uma regra de atraso independente.

A situação apresentada deve utilizar a mesma regra autoritativa utilizada pela tela operacional.

---

## 9.32 Relatórios por usuário

O sistema deve permitir filtrar vendas por usuário responsável.

Essa funcionalidade possui finalidade de rastreabilidade operacional.

O sistema pode apresentar:

- vendas realizadas pelo usuário;
- operações vinculadas ao usuário;
- período correspondente.

Não criar, neste momento:

- ranking de vendedores;
- metas individuais;
- comparação de desempenho;
- nota de funcionário;
- score de vendedor.

O sistema não possui módulo de produtividade ou monitoramento de desempenho dos usuários.

---

## 9.33 Usuário histórico da venda

O relatório deve utilizar o usuário histórico vinculado à venda.

Alterações futuras no perfil do usuário não devem alterar a autoria histórica da operação.

Se um usuário for desativado, suas vendas continuam vinculadas ao histórico.

A desativação não remove o usuário dos relatórios históricos.

---

## 9.34 Exportação dos Relatórios

Os relatórios devem permitir exportação em:

- Excel;
- PDF.

O usuário deve poder selecionar a opção correspondente.

A exportação deve respeitar os filtros aplicados.

Os dados exportados devem corresponder ao resultado válido da consulta.

Não exportar registros fora dos filtros apenas porque estavam carregados anteriormente na interface.

---

## 9.35 Exportação em Excel

A exportação em Excel é destinada principalmente à análise de dados.

O arquivo deve utilizar estrutura tabular.

As colunas devem corresponder ao relatório selecionado.

Valores numéricos devem ser exportados como valores utilizáveis em planilha quando tecnicamente possível.

Datas devem ser apresentadas de forma consistente.

A exportação deve preservar os dados permitidos para o perfil autenticado.

O Operador não deve receber lucro ou valor financeiro total do estoque por meio da exportação.

---

## 9.36 Exportação em PDF

A exportação em PDF é destinada à consulta, apresentação e impressão.

O PDF deve possuir identificação da MOVA SPORTS.

O PDF deve identificar:

- tipo do relatório;
- filtros aplicados;
- período, quando aplicável;
- data de geração.

O conteúdo deve respeitar as permissões do usuário autenticado.

Campos exclusivos do Administrador não devem ser incluídos no PDF de Operador.

---

## 9.37 Resumos dos Relatórios

Relatórios financeiros ou gerenciais devem apresentar resumo correspondente à sua finalidade.

Exemplos:

Relatório de Vendas:

- quantidade de vendas;
- peças vendidas;
- valor líquido vendido;
- lucro líquido para Administrador.

Relatório de Crediário:

- total original;
- recebido;
- em aberto;
- atrasado.

Relatório de Caixa:

- entradas;
- saídas;
- saldo.

Relatório de Contas a Pagar:

- total cadastrado;
- pago;
- pendente;
- vencido.

Os resumos devem acompanhar os filtros aplicados.

---

## 9.38 Relatório de Lucro

O sistema deve possuir Relatório de Lucro.

O Relatório de Lucro é exclusivo do Administrador.

Operadores não podem acessar o relatório.

A API não deve retornar os dados do Relatório de Lucro para Operador.

O frontend não deve ser utilizado como única barreira de autorização.

---

## 9.39 Filtros do Relatório de Lucro

O Relatório de Lucro deve permitir filtros por:

- período;
- marca;
- categoria;
- produto.

Os filtros podem ser utilizados em conjunto.

O período deve utilizar a data operacional oficial do sistema.

Devoluções devem ser contabilizadas conforme a data em que ocorreram.

---

## 9.40 Indicadores do Relatório de Lucro

O Relatório de Lucro deve apresentar:

- receita líquida;
- custo histórico líquido;
- lucro líquido;
- margem percentual.

A receita líquida deve considerar:

- vendas válidas;
- cancelamentos;
- devoluções.

O custo histórico líquido deve considerar:

- custo histórico dos itens vendidos;
- custo histórico dos itens devolvidos.

O lucro líquido deve utilizar:

Lucro líquido = Receita líquida - Custo histórico líquido

A margem percentual deve utilizar regra matemática consistente e documentada.

Quando a receita líquida for zero, o sistema não deve realizar divisão inválida.

---

## 9.41 Custo histórico no Relatório de Lucro

O Relatório de Lucro deve utilizar o custo preservado no momento da venda.

Não utilizar o custo atual do produto para recalcular vendas antigas.

Exemplo:

Custo na data da venda:
R$ 80,00

Custo atual do cadastro:
R$ 100,00

O relatório histórico da venda deve utilizar:
R$ 80,00

Alterações futuras no custo do produto não devem reescrever o lucro histórico de vendas anteriores.

---

## 9.42 Devoluções no Relatório de Lucro

Devoluções devem reduzir a receita líquida conforme o valor líquido devolvido.

O custo histórico correspondente ao item devolvido também deve ser reduzido.

O efeito conceitual no lucro é:

Valor líquido devolvido - Custo histórico devolvido

A devolução deve produzir efeito no período em que ocorreu.

Períodos anteriores não devem ser reescritos.

Essa regra deve permanecer coerente com o Dashboard.

---

## 9.43 Cancelamentos no Relatório de Lucro

Vendas canceladas não devem compor receita ou lucro válidos.

O histórico da venda cancelada permanece preservado.

O relatório pode permitir identificação da venda cancelada em relatórios operacionais.

O Relatório de Lucro deve utilizar somente os efeitos financeiros válidos conforme as regras oficiais de cancelamento.

---

## 9.44 Pagamentos mistos nos Relatórios

Vendas com pagamentos mistos devem preservar todas as formas utilizadas.

Relatórios que analisam formas de pagamento devem considerar a composição original e os efeitos líquidos das devoluções.

Não classificar uma venda mista integralmente em apenas uma forma de pagamento.

O rateio e os ajustes em centavos devem seguir a regra financeira oficial.

---

## 9.45 Dados históricos

Relatórios históricos devem utilizar snapshots preservados nas operações sempre que existirem.

Não substituir dados históricos por dados atuais do cadastro quando isso alterar o significado da operação original.

Essa regra se aplica, conforme disponível, a:

- produto;
- marca;
- preço original;
- preço praticado;
- custo;
- usuário;
- cliente vinculado;
- formas de pagamento.

Quando um dado histórico confiável não existir, o sistema não deve inventar informação utilizando o cadastro atual.

---

## 9.46 Segurança dos Relatórios

O backend deve aplicar autorização por perfil antes de retornar informações restritas.

Somente Administrador pode receber:

- lucro;
- margem;
- valor financeiro total do estoque.

O cache de relatórios, quando existir, deve considerar:

- loja;
- usuário;
- perfil;
- relatório;
- filtros.

Dados administrativos não podem ser reutilizados após troca para sessão de Operador.

Em expiração de sessão, dados restritos já renderizados devem ser removidos conforme as regras gerais de autenticação.

---

## 9.47 Relatórios e dados atuais

Relatórios de posição atual devem utilizar o estado atual correspondente.

Exemplos:

- Estoque;
- saldo atual do Crediário;
- Contas a Pagar em aberto.

Relatórios históricos devem utilizar os dados históricos correspondentes.

Exemplos:

- vendas;
- produtos vendidos;
- lucro histórico.

O sistema deve diferenciar posição atual de ocorrência histórica.

Não recalcular o passado com base exclusiva no cadastro atual.

---

## 9.48 Regras gerais do módulo Relatórios

O sistema deve:

- permitir acesso aos Relatórios para Administrador e Operador;
- restringir lucro, margem e valor financeiro total do estoque ao Administrador;
- aplicar autorização no backend;
- permitir filtros específicos por relatório;
- recalcular totais conforme os filtros;
- possuir Relatório de Vendas;
- possuir Relatório de Produtos Vendidos;
- possuir Relatório de Caixa;
- possuir Relatório de Crediário;
- possuir Relatório de Contas a Pagar;
- possuir Relatório de Estoque;
- possuir Relatório de Condicionais;
- permitir filtro operacional por usuário;
- não criar ranking de vendedores;
- permitir exportação em Excel;
- permitir exportação em PDF;
- respeitar os filtros nas exportações;
- respeitar o perfil do usuário nas exportações;
- possuir Relatório de Lucro exclusivo do Administrador;
- utilizar custo histórico nas vendas;
- considerar cancelamentos;
- considerar devoluções na data da ocorrência;
- considerar pagamentos mistos;
- preservar snapshots históricos;
- não recalcular vendas antigas utilizando custo ou marca atuais;
- utilizar as mesmas regras financeiras dos módulos autoritativos;
- não alterar dados durante consulta ou exportação.

# 10. CONDICIONAL

## 10.1 Finalidade do Condicional

O módulo Condicional é destinado ao controle de produtos enviados temporariamente a clientes para escolha.

O Condicional permite que produtos disponíveis sejam retirados da loja por cliente cadastrado e permaneçam reservados até que sejam:

- comprados;
- devolvidos;
- parcialmente comprados e parcialmente devolvidos;
- mantidos temporariamente com o cliente em razão de retorno parcial.

O Condicional interfere diretamente no estoque disponível.

Produtos vinculados a um Condicional aberto ou atrasado permanecem reservados enquanto estiverem com o cliente.

O Condicional não representa uma venda.

A venda somente existe quando os produtos escolhidos pelo cliente forem efetivamente encaminhados e confirmados no fluxo de Nova Venda.

---

## 10.2 Cliente obrigatório

Todo Condicional deve possuir cliente cadastrado e individualmente identificado.

Não permitir Condicional para:

- Cliente Padrão;
- cliente bloqueado;
- cliente desativado;
- cliente inexistente.

Somente cliente Ativo pode receber novo Condicional.

A validação deve ser realizada pelo backend.

O identificador persistente do cliente deve ser utilizado como vínculo autoritativo.

Nome, CPF ou telefone não substituem o identificador do cliente para fins de vínculo histórico.

---

## 10.3 Número do Condicional

Cada Condicional deve receber número automático.

O número não deve ser digitado manualmente pelo usuário.

O sistema deve garantir a identificação da operação.

O número do Condicional deve ser utilizado:

- na listagem;
- nos detalhes;
- na impressão;
- nas buscas;
- nos vínculos históricos, quando aplicável.

---

## 10.4 Data e hora da saída

A data e a hora da saída devem ser registradas automaticamente no momento da confirmação do Condicional.

O usuário não deve informar manualmente a data e a hora de saída.

O timestamp deve seguir as regras oficiais de timezone do sistema.

A data operacional deve utilizar America/Sao_Paulo.

A data e a hora da saída devem permanecer preservadas no histórico.

---

## 10.5 Usuário responsável

O sistema deve registrar o usuário autenticado responsável pela confirmação da saída do Condicional.

O usuário não deve ser selecionado manualmente pelo navegador.

O vínculo deve utilizar o usuário autenticado e validado pelo backend.

A alteração futura do perfil ou a desativação do usuário não deve remover sua autoria histórica.

---

## 10.6 Prazo do Condicional

O prazo padrão do Condicional é de 3 dias.

Ao iniciar um novo Condicional, o sistema deve calcular automaticamente a data prevista de retorno.

A data prevista de retorno deve ser apresentada ao usuário durante a criação do Condicional.

O prazo deve utilizar a data civil operacional da loja.

O usuário não precisa calcular manualmente o prazo.

O sistema deve utilizar a regra oficial de 3 dias para novos Condicionais.

---

## 10.7 Data prevista de retorno

Todo Condicional deve possuir data prevista de retorno.

Para novos Condicionais, a data prevista deve ser calculada automaticamente com base no prazo de 3 dias.

A data prevista de retorno deve permanecer registrada no Condicional.

A data deve ser utilizada para:

- identificação de atraso;
- alertas;
- listagem;
- ficha do cliente;
- relatórios;
- impressão.

A data prevista de retorno é uma data civil.

Não aplicar conversão de timezone sobre uma data civil YYYY-MM-DD.

---

## 10.8 Alerta após o prazo

Quando o prazo de 3 dias for ultrapassado e ainda existirem produtos com o cliente, o sistema deve emitir alerta.

O alerta deve identificar que o Condicional está atrasado.

O atraso deve produzir destaque visual nas áreas correspondentes.

O alerta não deve:

- gerar multa automática;
- gerar juros automáticos;
- criar cobrança;
- criar conta a receber;
- transformar produtos automaticamente em venda;
- cancelar o Condicional.

O alerta possui finalidade operacional.

---

## 10.9 Produtos disponíveis para Condicional

Somente produtos com estoque disponível maior que zero podem ser adicionados a um novo Condicional.

O estoque disponível deve considerar:

- estoque real;
- quantidades já reservadas em outros Condicionais ativos.

A regra conceitual é:

Estoque disponível = Estoque real - Quantidade reservada

Não permitir adicionar ao Condicional quantidade superior ao estoque disponível.

A validação autoritativa deve existir no backend.

A interface não deve ser a única responsável pela validação do estoque.

---

## 10.10 Seleção de produtos

A montagem do Condicional deve permitir:

- busca por código;
- busca por nome;
- visualização dos produtos disponíveis;
- adicionar produto;
- adicionar mais de uma unidade do mesmo produto;
- alterar quantidade;
- remover produto antes da confirmação.

A listagem de seleção deve considerar somente produtos com estoque disponível.

O código de barras pode funcionar como código do produto conforme as regras oficiais do módulo Produtos.

Cada combinação cadastrada de produto permanece individualmente identificada.

---

## 10.11 Montagem do Condicional

Enquanto o Condicional estiver somente em montagem, nenhuma reserva deve ser criada.

Adicionar um produto à tela de montagem não altera o estoque.

Alterar quantidade durante a montagem não altera o estoque.

Remover produto durante a montagem não gera movimentação.

A reserva somente passa a existir após a confirmação definitiva da saída do Condicional.

---

## 10.12 Preço de referência

Ao confirmar a saída do Condicional, o sistema deve preservar o preço de venda atual do produto como preço de referência.

O preço de referência representa o preço cadastrado no momento da saída.

Alterações futuras no preço do cadastro não devem reescrever o preço histórico do Condicional.

Exemplo:

Preço no momento da saída:
R$ 200,00

Preço cadastrado posteriormente:
R$ 220,00

Preço histórico de referência do Condicional:
R$ 200,00

O sistema não deve substituir automaticamente o preço histórico pelo preço atual.

---

## 10.13 Preço na venda originada do Condicional

O preço de referência do Condicional não impede alteração do preço praticado na venda.

Quando produtos escolhidos pelo cliente forem enviados para Nova Venda, devem seguir as regras normais do módulo Vendas.

O usuário pode, conforme as regras oficiais da venda:

- alterar o preço praticado;
- conceder desconto por produto;
- aplicar desconto geral;
- aplicar acréscimo.

A alteração realizada na venda não deve modificar retroativamente o preço histórico de referência do Condicional.

Também não deve alterar automaticamente o preço cadastrado do produto.

---

## 10.14 Confirmação da saída

Ao confirmar a saída do Condicional, o sistema deve:

1. apresentar resumo da operação;
2. solicitar confirmação;
3. validar novamente cliente e produtos;
4. validar novamente o estoque disponível;
5. gravar o Condicional;
6. registrar data e hora;
7. registrar usuário responsável;
8. reservar as quantidades correspondentes;
9. registrar o histórico necessário;
10. apresentar os detalhes do Condicional;
11. disponibilizar a opção de impressão.

A reserva somente deve ocorrer após a confirmação definitiva.

Se a confirmação não ocorrer, nenhuma quantidade deve ser reservada.

---

## 10.15 Reserva de estoque

Produtos confirmados em Condicional devem permanecer reservados.

A reserva reduz o estoque disponível.

A reserva não reduz o estoque real enquanto o produto ainda estiver vinculado ao Condicional.

Exemplo:

Estoque real:
5

Reservado em Condicionais:
2

Estoque disponível:
3

Os produtos reservados não podem ser utilizados em outra operação como se estivessem disponíveis.

---

## 10.16 Reserva por quantidade

A reserva deve ser controlada por produto e quantidade.

Cada unidade enviada em Condicional reduz a disponibilidade correspondente.

Exemplo:

Produto possui 3 unidades disponíveis.

1 unidade é enviada em Condicional.

Resultado:

Estoque real:
3

Reservado:
1

Disponível:
2

Se as outras 2 unidades também forem reservadas:

Estoque real:
3

Reservado:
3

Disponível:
0

O produto não pode mais ser adicionado a nova venda ou novo Condicional como produto disponível.

---

## 10.17 Retorno do Condicional

Quando o cliente retornar, o usuário deve abrir o Condicional correspondente.

O sistema deve apresentar os produtos que ainda permanecem com o cliente.

O usuário deve poder definir o destino das peças apresentadas no retorno.

Para cada produto ou quantidade correspondente, deve ser possível identificar se o cliente:

- devolveu a peça;
- ficou com a peça.

A interface pode utilizar ações ou seleções equivalentes a:

- DEVOLVER;
- FICOU COM A PEÇA.

O sistema não deve presumir automaticamente que todas as peças foram compradas ou devolvidas.

---

## 10.18 Seleção por quantidade no retorno

Quando existir mais de uma unidade do mesmo produto no Condicional, o retorno deve permitir definir quantidades.

Exemplo:

Condicional:
3 unidades do Produto A

Retorno:

- cliente ficou com 1;
- cliente devolveu 1;
- 1 permanece com o cliente.

O sistema deve preservar corretamente cada quantidade.

A soma das quantidades:

- compradas;
- devolvidas;
- ainda com o cliente

não pode ultrapassar a quantidade originalmente vinculada ao Condicional, considerando os retornos anteriores.

---

## 10.19 Retorno parcial

O Condicional permite retorno parcial.

O cliente pode devolver ou comprar apenas parte dos produtos em determinado momento.

Os demais produtos podem continuar com o cliente.

Exemplo:

Cliente levou 5 peças.

No primeiro retorno:

- ficou com 1;
- devolveu 2;
- continua com 2.

O Condicional permanece aberto com as 2 peças restantes.

As peças restantes continuam reservadas.

O retorno parcial deve ser preservado no histórico.

---

## 10.20 Retornos em momentos diferentes

O mesmo Condicional pode possuir retornos em momentos diferentes.

O sistema deve preservar cada ocorrência de retorno.

Cada retorno deve registrar, no mínimo:

- data e hora;
- usuário responsável;
- produtos envolvidos;
- quantidades devolvidas;
- quantidades destinadas à compra.

O histórico anterior não deve ser reescrito por um novo retorno.

O sistema deve considerar os retornos anteriores antes de aceitar novas quantidades.

---

## 10.21 Produtos devolvidos

Produtos confirmados como devolvidos devem deixar de permanecer reservados no Condicional.

A quantidade devolvida volta a compor o estoque disponível.

A devolução de produto do Condicional não representa devolução de venda.

Não gerar estorno financeiro.

Não gerar saída financeira.

Não gerar entrada financeira.

Não criar devolução comercial de venda.

A operação representa retorno físico de produto que estava reservado.

---

## 10.22 Produtos que o cliente ficou

Produtos identificados como peças com as quais o cliente ficou devem ser encaminhados diretamente para uma Nova Venda vinculada ao Condicional.

A venda deve possuir:

- cliente do Condicional já vinculado;
- produtos selecionados no retorno;
- quantidades correspondentes;
- vínculo com o Condicional de origem.

O usuário não deve precisar selecionar novamente o cliente.

Os produtos devem ser transferidos para o fluxo normal de venda.

---

## 10.23 Venda vinculada ao Condicional

A compra de produtos originados de um Condicional deve gerar uma venda normal.

A venda deve seguir todas as regras oficiais do módulo Vendas.

Devem continuar disponíveis, conforme as regras da venda:

- alteração do preço praticado;
- desconto por produto;
- desconto geral;
- acréscimo;
- Dinheiro;
- Pix;
- Débito;
- Crédito;
- Crediário;
- pagamento misto.

O Condicional não deve possuir fluxo financeiro próprio para registrar a compra.

O efeito financeiro ocorre na venda vinculada.

---

## 10.24 Vínculo entre venda e Condicional

A venda originada de um Condicional deve preservar vínculo com o Condicional de origem.

O vínculo deve permitir identificar:

- número do Condicional;
- venda gerada;
- cliente;
- produtos transferidos;
- quantidades transferidas.

O histórico da venda deve permitir identificar sua origem no Condicional.

O histórico do Condicional deve permitir identificar a venda correspondente.

Não utilizar apenas nome do cliente ou data como vínculo.

O sistema deve utilizar identificadores persistentes.

---

## 10.25 Confirmação da venda originada do Condicional

Os produtos selecionados como peças com as quais o cliente ficou devem seguir para a tela de Nova Venda.

A venda somente produz efeitos financeiros após sua confirmação definitiva.

A confirmação deve seguir as regras normais do módulo Vendas.

Ao concluir a venda com sucesso:

- os produtos correspondentes deixam de permanecer reservados no Condicional;
- as quantidades são reconhecidas como vendidas;
- o estoque é atualizado conforme a regra oficial da venda;
- os efeitos financeiros são gerados pela venda;
- o vínculo entre venda e Condicional é preservado.

---

## 10.26 Cancelamento da venda durante o retorno do Condicional

Não existe abandono silencioso da venda originada do Condicional.

Quando produtos de um Condicional forem encaminhados para a venda, o fluxo deve preservar sua origem.

Se a venda vinculada for cancelada antes de sua conclusão definitiva, os produtos correspondentes devem retornar ao contexto do Condicional.

A venda cancelada não pode transformar os produtos em peças vendidas.

Os produtos devem permanecer vinculados ao Condicional até nova definição válida.

O usuário deve retornar ao Condicional e corrigir a seleção das peças.

As peças que não serão compradas devem ser retiradas da seleção de compra e tratadas conforme sua situação física.

Quando devolvidas fisicamente, devem ser registradas como devolvidas.

O Condicional somente deve ser finalizado quando não existirem peças pendentes com o cliente e todos os destinos necessários tiverem sido corretamente confirmados.

---

## 10.27 Integridade entre Condicional e Venda

O sistema não deve permitir que uma falha ou cancelamento da venda faça desaparecer a reserva histórica do Condicional.

Produtos encaminhados para uma venda ainda não concluída devem permanecer rastreáveis.

Uma venda não confirmada não deve:

- produzir receita;
- produzir caixa;
- produzir recebível;
- produzir crediário;
- retirar definitivamente a peça do Condicional.

A transição entre Condicional e Venda deve preservar a integridade das quantidades.

---

## 10.28 Finalização do Condicional

O Condicional deve ser finalizado quando todas as peças originalmente vinculadas tiverem destino confirmado.

Os destinos válidos são:

- compradas por meio de venda vinculada concluída;
- devolvidas fisicamente.

Não finalizar o Condicional enquanto existirem peças ainda com o cliente.

Retornos parciais não finalizam automaticamente o Condicional quando restarem peças pendentes.

Ao não existir mais quantidade pendente, o Condicional pode assumir situação Finalizado.

---

## 10.29 Condicional aberto

O status Aberto representa Condicional com produtos ainda pendentes e dentro do prazo de retorno.

O Condicional Aberto pode possuir:

- todas as peças ainda com o cliente;
- parte das peças já devolvida;
- parte das peças já comprada;
- produtos restantes ainda com o cliente.

A existência de retorno parcial não encerra automaticamente o Condicional.

---

## 10.30 Condicional atrasado

O status Atrasado representa Condicional que:

- ultrapassou a data prevista de retorno;
- ainda possui produtos pendentes com o cliente.

A classificação deve ocorrer automaticamente com base na data operacional.

O usuário não precisa marcar manualmente o Condicional como atrasado.

Um Condicional atrasado permanece operacionalmente aberto.

Ele pode receber:

- devolução de produtos;
- seleção de produtos para compra;
- retornos parciais.

O atraso não transforma automaticamente o Condicional em venda.

---

## 10.31 Condicional finalizado

O status Finalizado representa Condicional sem produtos pendentes com o cliente.

Um Condicional pode ser finalizado quando todas as peças forem:

- devolvidas;
- compradas;
- parcialmente devolvidas e parcialmente compradas.

As compras devem possuir venda vinculada concluída.

O histórico completo deve permanecer disponível após a finalização.

Condicional finalizado não pode receber novos produtos.

---

## 10.32 Condicional cancelado

O status Cancelado representa o cancelamento formal do Condicional.

O cancelamento deve preservar o histórico da operação.

Administrador e Operador podem cancelar Condicional.

O cancelamento exige motivo obrigatório.

O sistema deve registrar:

- motivo;
- data e hora;
- usuário responsável.

---

## 10.33 Regra física para cancelamento

Um Condicional não pode ser cancelado enquanto existirem peças fisicamente com o cliente.

Antes do cancelamento, todas as peças ainda reservadas devem possuir retorno físico confirmado.

O sistema não deve liberar automaticamente estoque apenas porque o usuário clicou em Cancelar.

Exemplo:

Produto permanece com o cliente.

Resultado:

O Condicional não pode ser cancelado.

O Condicional deve permanecer:

- Aberto;
- ou Atrasado.

Quando a peça retornar fisicamente, sua devolução pode ser registrada.

Após não existirem peças pendentes com o cliente, o cancelamento pode ser concluído quando aplicável.

---

## 10.34 Cancelamento e estoque

O cancelamento não pode criar estoque fictício.

Somente produtos fisicamente confirmados como devolvidos podem voltar ao estoque disponível.

Produtos vendidos por venda vinculada concluída permanecem vendidos.

O cancelamento do Condicional não deve cancelar automaticamente vendas já concluídas.

Qualquer cancelamento ou devolução de venda deve seguir as regras próprias do módulo Vendas.

---

## 10.35 Impressão do Condicional

O Condicional deve permitir impressão simples.

A impressão deve possuir cabeçalho com:

MOVA SPORTS

A impressão deve apresentar:

- número do Condicional;
- data da saída;
- hora da saída;
- cliente;
- telefone;
- data prevista de retorno;
- produtos;
- atributos do produto;
- quantidade;
- preço de referência;
- usuário responsável.

Os atributos devem apresentar, quando disponíveis:

- tamanho;
- cor.

Ao final, apresentar texto simples indicando:

Produtos enviados em condicional.

A impressão não exige assinatura obrigatória do cliente.

Não é necessário criar fluxo de assinatura digital.

---

## 10.36 Impressão após retornos

Os detalhes do Condicional devem permanecer disponíveis após retornos parciais ou finalização.

Quando houver impressão de um Condicional já movimentado, o sistema deve deixar clara a situação atual.

O histórico deve permitir identificar:

- peças compradas;
- peças devolvidas;
- peças ainda com o cliente.

Quando existirem vendas vinculadas, elas devem permanecer identificáveis nos detalhes.

---

## 10.37 Tela de Condicionais

A tela de Condicionais deve possuir indicadores, busca, filtros e listagem.

A tela deve priorizar a identificação rápida de:

- Condicionais abertos;
- Condicionais atrasados;
- produtos ainda com clientes.

O usuário deve conseguir acessar os detalhes da operação.

---

## 10.38 Indicadores do Condicional

A tela deve apresentar os seguintes cards:

- Condicionais Abertos;
- Condicionais Atrasados;
- Peças em Condicional;
- Valor em Condicional.

Os indicadores devem utilizar o estado atual das operações.

Peças já devolvidas não devem continuar compondo Peças em Condicional.

Peças já vendidas por venda vinculada concluída não devem continuar compondo Peças em Condicional.

---

## 10.39 Valor em Condicional

O indicador Valor em Condicional deve representar o valor de referência das peças ainda pendentes com clientes.

O cálculo deve utilizar o preço de referência preservado na saída do Condicional.

Não utilizar o preço atual do cadastro para reescrever Condicionais antigos.

Não incluir:

- peças devolvidas;
- peças já vendidas por venda vinculada concluída.

O indicador possui finalidade operacional.

Ele não representa faturamento ou receita.

---

## 10.40 Busca de Condicionais

A busca deve permitir localizar Condicionais por:

- cliente;
- CPF;
- telefone;
- número do Condicional.

A busca deve considerar normalização dos dados quando aplicável.

CPF pode ser comparado sem pontos e traço.

Telefone pode ser comparado considerando sua representação normalizada.

---

## 10.41 Filtros de Condicionais

A tela deve permitir filtros por:

- período de saída;
- situação.

As situações são:

- Aberto;
- Atrasado;
- Finalizado;
- Cancelado.

Os filtros podem ser utilizados em conjunto com a busca.

Os indicadores devem acompanhar os filtros aplicados quando a regra visual da tela utilizar resumos filtrados.

---

## 10.42 Listagem de Condicionais

A listagem deve apresentar:

- número;
- data de saída;
- cliente;
- quantidade de peças ainda com o cliente;
- valor das peças ainda com o cliente;
- retorno previsto;
- situação;
- ação.

A ação principal deve ser:

VER DETALHES

A listagem deve permitir destaque visual para Condicionais atrasados.

---

## 10.43 Detalhes do Condicional

Ao abrir os detalhes, o sistema deve apresentar, no mínimo:

- número;
- cliente;
- telefone;
- data e hora da saída;
- data prevista de retorno;
- usuário responsável;
- produtos originais;
- quantidades originais;
- preços de referência;
- peças compradas;
- peças devolvidas;
- peças ainda com o cliente;
- retornos parciais;
- vendas vinculadas;
- situação.

Também devem estar disponíveis as ações permitidas para o estado atual da operação.

---

## 10.44 Histórico do Condicional

O sistema deve preservar o histórico completo do Condicional.

O histórico deve permitir identificar:

- criação;
- saída;
- produtos enviados;
- retornos;
- devoluções físicas;
- produtos destinados à compra;
- vendas vinculadas;
- cancelamento, quando existir;
- finalização.

Cada ocorrência relevante deve preservar:

- data e hora;
- usuário responsável.

O histórico não deve ser apagado após a finalização ou cancelamento.

---

## 10.45 Condicional na ficha do cliente

A ficha do cliente deve apresentar os Condicionais vinculados ao cliente.

Devem ser identificáveis:

- Abertos;
- Atrasados;
- Finalizados;
- Cancelados.

A ficha deve permitir acesso aos detalhes da operação.

O histórico do cliente deve preservar Condicionais antigos mesmo após sua finalização.

---

## 10.46 Alerta ao selecionar cliente

Quando um cliente possuir Condicional atrasado, o sistema pode apresentar alerta ao selecionar o cliente em uma operação.

O alerta deve possuir finalidade informativa.

O sistema deve identificar a existência de produto pendente em Condicional atrasado.

O alerta não deve criar cobrança ou venda automática.

As restrições de cliente Bloqueado continuam seguindo as regras do módulo Clientes.

---

## 10.47 Condicional e Catálogo

Produtos reservados em Condicionais Abertos ou Atrasados reduzem o estoque disponível utilizado pelo Catálogo.

Se a reserva consumir todo o estoque disponível, o produto deixa de aparecer no Catálogo.

Quando uma peça for fisicamente devolvida:

- a reserva correspondente é removida;
- o estoque disponível é recalculado;
- o produto pode voltar ao Catálogo.

Quando uma peça for vendida:

- a reserva correspondente deixa de existir;
- a venda produz o efeito definitivo de estoque.

---

## 10.48 Condicional e Estoque

O módulo Estoque deve diferenciar:

- estoque real;
- reservado;
- disponível.

Produtos em Condicional compõem a quantidade reservada enquanto permanecerem pendentes com o cliente.

Retorno físico reduz a reserva e aumenta a disponibilidade.

Venda vinculada concluída reduz a reserva e produz o efeito definitivo da venda no estoque.

O sistema deve impedir dupla redução ou dupla liberação da mesma quantidade.

---

## 10.49 Condicional e Dashboard

Condicionais não representam vendas.

A saída de produto em Condicional não deve aumentar:

- Vendas Hoje;
- Vendas no Mês;
- lucro;
- receita;
- composição de pagamentos.

O valor em Condicional não deve ser tratado como faturamento.

Somente a venda vinculada concluída produz efeitos financeiros e gerenciais de venda.

As reservas podem interferir nos cálculos de estoque disponível e peças paradas conforme as regras oficiais do Dashboard.

---

## 10.50 Condicional e Relatórios

O Relatório de Condicionais deve utilizar os dados oficiais deste módulo.

Devem ser preservadas as situações:

- Aberto;
- Atrasado;
- Finalizado;
- Cancelado.

Os relatórios devem considerar:

- data de saída;
- cliente;
- produtos;
- data prevista de retorno;
- comprados;
- devolvidos;
- situação.

As vendas originadas do Condicional continuam aparecendo nos relatórios de vendas como vendas normais, preservando o vínculo histórico com o Condicional.

---

## 10.51 Integridade de quantidades

O sistema deve controlar as quantidades acumuladas do Condicional.

Para cada produto, a soma de:

- quantidade vendida por venda vinculada válida;
- quantidade devolvida fisicamente;
- quantidade ainda pendente com o cliente

deve corresponder à quantidade válida enviada no Condicional.

O sistema não deve permitir processar a mesma quantidade duas vezes.

Retornos anteriores devem ser considerados antes de aceitar nova operação.

---

## 10.52 Regras gerais do módulo Condicional

O sistema deve:

- exigir cliente cadastrado e Ativo;
- impedir Cliente Padrão no Condicional;
- impedir cliente Bloqueado;
- impedir cliente Desativado;
- gerar número automático;
- registrar data e hora automaticamente;
- registrar usuário responsável;
- utilizar prazo padrão de 3 dias;
- calcular data prevista de retorno;
- alertar após o prazo;
- permitir somente produtos com estoque disponível;
- permitir busca por código ou nome;
- permitir múltiplos produtos;
- permitir múltiplas unidades;
- reservar estoque somente após confirmação;
- preservar o preço de referência da saída;
- permitir alteração do preço praticado somente na venda;
- permitir devolução de peças;
- permitir seleção das peças com as quais o cliente ficou;
- gerar venda normal vinculada para produtos comprados;
- permitir retorno parcial;
- permitir retornos em momentos diferentes;
- preservar histórico de cada retorno;
- manter reservadas as peças ainda com o cliente;
- retornar produtos ao Condicional quando a venda vinculada não for concluída;
- não permitir abandono silencioso da transição Condicional para Venda;
- finalizar somente quando não existirem peças pendentes;
- classificar atraso automaticamente;
- não gerar multa automática;
- não gerar venda automática;
- permitir cancelamento por Administrador e Operador;
- exigir motivo para cancelamento;
- impedir cancelamento enquanto existirem peças fisicamente com o cliente;
- não criar estoque fictício no cancelamento;
- permitir impressão simples;
- não exigir assinatura do cliente;
- apresentar cards operacionais;
- permitir busca e filtros;
- preservar vínculo com vendas originadas;
- não tratar Condicional como faturamento;
- refletir as reservas no Estoque e no Catálogo;
- impedir processamento duplicado das mesmas quantidades.


# 11. REGRAS GERAIS

## 11.1 Operação

O Mova Sports foi desenvolvido para a operação de uma única loja.

Neste momento, não existe necessidade de arquitetura multi-loja.

## 11.2 Princípios gerais

Toda funcionalidade deve priorizar:

- Simplicidade;
- Rapidez;
- Segurança;
- Clareza;
- Facilidade de uso;
- Preservação dos dados;
- Rastreabilidade.

## 11.3 Histórico e auditoria

Ações importantes devem permanecer registradas sempre que aplicável.

Especialmente:

- Cancelamentos;
- Devoluções;
- Alterações de limite de crédito;
- Ajustes de inventário;
- Movimentações financeiras;
- Pagamentos;
- Alterações sensíveis.

Registros históricos não devem ser apagados para ocultar operações anteriores.

---

# 12. REGRAS A CONFIRMAR FUTURAMENTE

As seguintes regras ainda podem ser detalhadas ou refinadas:

---

# 13. REGRAS COMPROVADAS PELO CÓDIGO ATUAL

Esta seção complementa as regras manuais acima com comportamentos confirmados em `server.py` e `script.js`. Ela não substitui regras já definidas manualmente. Quando houver conflito, a regra manual permanece preservada e o conflito é listado em **DIVERGÊNCIAS ENCONTRADAS**.

## 13.1 Regras gerais de acesso às APIs

- Todas as rotas iniciadas por `/api/` exigem login, exceto `/api/health`, `/api/session`, `/api/login` e `/api/logout`.
- A sessão é revalidada no banco antes das APIs protegidas.
- Se o usuário da sessão não existir mais ou estiver inativo, a sessão é encerrada.
- Ações administrativas usam validação específica de perfil `admin`.
- O sistema registra auditoria para ações importantes como login, logout, criação, atualização, exclusão, pagamento, cancelamento, importação, exportação, backup, reset e upload.

## 13.2 Clientes

- O nome do cliente é obrigatório.
- O limite de crédito não pode ser negativo.
- CPF vazio é permitido.
- CPF preenchido deve ser único por loja.
- O cliente possui status armazenado em cadastro.
- Venda no crediário não é permitida para cliente com status `blocked`.
- Cliente com venda, conta a receber ou pagamento vinculado não pode ser excluído pelo endpoint atual.
- Cliente sem histórico financeiro pode ser excluído fisicamente pelo endpoint atual.
- A listagem de clientes é ordenada por nome.
- O crediário usa o cliente para calcular saldo em aberto, parcelas em dia, parcelas atrasadas e parcelas quitadas.

## 13.3 Produtos, marcas e categorias

- Código de barras é obrigatório no backend.
- Nome do produto é obrigatório.
- Código de barras deve ser único por loja quando preenchido.
- Estoque e estoque mínimo são normalizados para valores inteiros maiores ou iguais a zero.
- Custo e preço são armazenados como valores numéricos.
- O frontend calcula margem automaticamente quando custo e preço de venda são informados.
- O frontend calcula preço de venda automaticamente quando custo e margem são informados.
- Produto com histórico de venda, troca ou devolução não pode ser excluído.
- Produto sem vínculo com venda ou devolução pode ser excluído fisicamente.
- Marcas e categorias exigem nome.
- Marcas e categorias não podem ser duplicadas.
- Ao renomear marca ou categoria, os produtos vinculados são atualizados para o novo nome.
- Marca ou categoria vinculada a produto não pode ser excluída.

## 13.4 Fornecedores

- Nome do fornecedor é obrigatório.
- Fornecedores podem ter CNPJ, telefone, e-mail e endereço.
- Fornecedor vinculado a conta a pagar não pode ser excluído.
- Fornecedor sem conta a pagar vinculada pode ser excluído fisicamente.
- A listagem de fornecedores é ordenada por nome.

## 13.5 Estoque

- A venda considera o estoque do produto menos as quantidades reservadas em condicionais abertos.
- O sistema rejeita venda com quantidade maior que o estoque disponível após reservas de condicional.
- O frontend não permite adicionar ao carrinho produto sem estoque disponível.
- O frontend limita a quantidade do carrinho ao estoque disponível.
- Ao finalizar venda, o estoque dos produtos vendidos é reduzido.
- Ao cancelar venda, o estoque dos itens vendidos é aumentado.
- Ao registrar devolução ou troca, o estoque dos itens informados é aumentado.
- Não foi encontrada tabela própria de movimentações de estoque.

## 13.6 Vendas

- Venda exige pelo menos um produto.
- Cada venda recebe código sequencial no formato `VENDA001`, `VENDA002` e assim por diante.
- Se o código informado já existir, o backend gera o próximo código disponível.
- Cada item de venda precisa possuir produto e quantidade maior que zero.
- O total da venda é calculado por subtotal menos desconto, com mínimo zero.
- A soma das formas de pagamento deve fechar com o total da venda.
- Venda sem cliente usa o nome `Venda simples`.
- Vendas são criadas com status `completed`.
- Vendas canceladas permanecem no histórico com status `cancelled`.
- Dashboard, relatórios e histórico desconsideram vendas canceladas para faturamento e ticket médio.
- O histórico de vendas permite filtro por nome, CPF, telefone, número da venda, código de barras, período e situação.

## 13.7 Pagamentos da venda

- Formas aceitas na venda: dinheiro (`cash`), PIX (`pix`), débito (`debit`), crédito (`credit`) e crediário (`storeCredit`).
- Pagamento misto é aceito desde que a soma feche com o total.
- Dinheiro e PIX geram movimentação de entrada no caixa no momento da venda.
- Débito e crédito geram conta a receber com status `cardPending`.
- Débito e crédito não entram no caixa no momento da venda.
- Crediário gera contas a receber com método `storeCredit`.
- Parcelas de crediário são geradas em intervalos de 30 dias a partir da data da venda.
- O valor das parcelas é dividido igualmente, com ajuste de arredondamento na última parcela.

## 13.8 Crediário e contas a receber

- Crediário exige cliente cadastrado.
- Cliente inexistente impede venda no crediário.
- Cliente bloqueado impede venda no crediário.
- O limite de crédito compara dívida aberta existente mais novo valor no crediário.
- Usuário não administrador é bloqueado quando ultrapassa o limite.
- Usuário administrador pode liberar venda acima do limite no fluxo do frontend/backend.
- Contas a receber canceladas não entram no saldo em aberto.
- Pagamento de crediário aceita dinheiro, PIX, débito e crédito.
- Pagamento de crediário exige cliente e parcelas.
- Pagamento parcial de parcela é permitido.
- Não é permitido receber valor maior que o saldo da parcela.
- Quando uma parcela é quitada, o status passa para `paid` e `paidAt` é preenchido.
- Quando uma parcela continua com saldo, o status permanece `open`.
- Pagamentos de crediário em dinheiro ou PIX geram entrada no caixa.
- Pagamentos de crediário em débito ou crédito geram nova conta a receber com status `cardPending`.
- O histórico de contas a receber mantém registros de pagamentos por parcela.

## 13.9 Condicionais

### Objetivo

O Condicional permite reservar temporariamente produtos para um cliente cadastrado, mantendo controle sobre os produtos que estão fisicamente fora da loja e indisponíveis para outras vendas.

### Cliente

- Cliente cadastrado é obrigatório.
- Não é permitido utilizar cliente padrão.
- O limite de crédito não interfere na criação ou manutenção do condicional.
- O limite de crédito será considerado somente se os produtos forem posteriormente vendidos por crediário.

### Datas

Ao criar um condicional, registrar:

- data e hora de saída;
- data prevista de retorno;
- data de cada movimentação posterior.

A data prevista de retorno será inicialmente calculada como 3 dias após a saída.

Após 3 dias sem finalização, o sistema deve emitir um alerta.

O atraso:

- não cancela automaticamente o condicional;
- não libera automaticamente os produtos;
- não bloqueia outras operações do cliente.

### Reserva de estoque

Produtos enviados em condicional ficam reservados.

O estoque deve distinguir:

- Estoque real: quantidade física total registrada;
- Estoque reservado: quantidade vinculada a condicionais ativos;
- Estoque disponível: estoque real menos estoque reservado.

Fórmula:

Estoque disponível = Estoque real - Estoque reservado

Somente o estoque disponível pode ser vendido ou adicionado a outro condicional.

Exemplo:

- Estoque real: 3;
- Reservado: 2;
- Disponível: 1.

Se o estoque disponível chegar a zero, o produto deve ficar indisponível para novas vendas e novos condicionais.

### Movimentações do condicional

Um condicional aberto pode receber novos produtos posteriormente.

Também é permitido devolver produtos em momentos diferentes.

Toda movimentação deve preservar:

- produto;
- quantidade;
- data e hora;
- usuário responsável;
- tipo da movimentação.

### Retorno

O cliente pode:

- devolver todos os produtos;
- comprar todos os produtos;
- comprar parte e devolver parte;
- devolver produtos em momentos diferentes.

Produtos devolvidos deixam de estar reservados e voltam imediatamente ao estoque disponível.

### Transformação em venda

Na listagem do condicional, o usuário deve poder definir quais produtos serão:

- enviados para venda;
- devolvidos.

Os produtos escolhidos para compra devem abrir a tela normal de Nova Venda:

- com o cliente já vinculado;
- com os produtos selecionados já adicionados.

A partir desse momento, a operação segue todas as regras normais de venda.

São permitidos:

- descontos;
- Dinheiro;
- Pix;
- Débito;
- Crédito;
- Crediário;
- pagamentos mistos.

Quando houver crediário, aplicam-se normalmente as regras de limite de crédito.

A reserva do produto deve ser convertida corretamente em saída definitiva de estoque, sem baixar a mesma peça duas vezes.

### Finalização parcial

Um condicional pode permanecer aberto enquanto ainda possuir produtos pendentes.

Exemplo:

- 5 produtos enviados;
- 2 comprados;
- 1 devolvido;
- 2 ainda permanecem com o cliente.

Nesse caso, o condicional continua aberto e somente os 2 produtos restantes permanecem reservados.

### Status

O condicional pode possuir os seguintes status:

- Aberto;
- Atrasado;
- Finalizado;
- Cancelado.

#### Aberto

Possui produtos ainda pendentes e está dentro do período inicial de 3 dias.

#### Atrasado

Possui produtos pendentes e já ultrapassou 3 dias desde a saída.

#### Finalizado

Todos os produtos foram:

- vendidos;
- devolvidos;
- ou distribuídos entre venda e devolução.

Não existem mais produtos pendentes.

#### Cancelado

O condicional foi cancelado.

O cancelamento deve liberar todos os produtos ainda reservados.

Produtos já vendidos anteriormente não podem ser revertidos pelo cancelamento do condicional.

### Histórico

O histórico deve apresentar:

- cliente;
- data de saída;
- data prevista de retorno;
- produtos enviados;
- produtos comprados;
- produtos devolvidos;
- produtos ainda pendentes;
- situação atual.

O histórico deve preservar movimentações parciais e não apenas o estado final.

### Impressão

O sistema deve permitir imprimir o comprovante do condicional.

O comprovante deve apresentar, no mínimo:

- identificação da loja;
- cliente;
- data de saída;
- produtos;
- quantidades;
- data prevista de retorno.

Não é obrigatória assinatura do cliente.

### Regras de segurança

- Não permitir reservar quantidade superior ao estoque disponível.
- Não permitir vender para outro cliente uma unidade já reservada.
- Não liberar produto reservado sem uma movimentação válida.
- Não baixar o estoque duas vezes ao transformar condicional em venda.
- Não devolver duas vezes o mesmo produto.
- Não apagar o histórico de condicionais finalizados ou cancelados.
- Toda movimentação deve ser rastreável.

## 13.10 Devoluções e trocas

### Regras Financeiras de Devolução

### Valor da devolução

O valor da devolução deve ser calculado exclusivamente com base nos dados registrados na venda original.

O sistema nunca deve confiar em:

- preço enviado pelo navegador;
- custo enviado pelo navegador;
- valor calculado apenas no frontend.

O backend deve determinar o valor correto da devolução.

### Desconto da venda

Quando a venda possuir desconto global, o desconto deve ser distribuído proporcionalmente entre os itens.

Exemplo:

- valor bruto da venda: R$ 200,00;
- desconto global: R$ 20,00;
- valor líquido da venda: R$ 180,00;
- item com valor bruto de R$ 100,00;
- valor líquido atribuído ao item: R$ 90,00.

A devolução desse item deve considerar R$ 90,00.

### Quantidade máxima devolvida

A soma das devoluções de um item nunca pode ultrapassar a quantidade originalmente vendida.

O sistema deve considerar devoluções anteriores antes de autorizar uma nova devolução.

### Data gerencial

A devolução deve produzir impacto gerencial na data em que ocorrer.

Exemplo:

- venda realizada em junho;
- devolução realizada em julho.

A venda permanece registrada no histórico de junho e a devolução reduz os resultados líquidos de julho.

Períodos históricos anteriores não devem ser reescritos.

### Pagamentos mistos

Quando uma venda possuir múltiplas formas de pagamento, o valor devolvido deve ser distribuído proporcionalmente à composição financeira original.

Exemplo:

- 50% Pix;
- 50% Crédito;
- devolução de R$ 100,00.

A devolução será alocada em:

- R$ 50,00 para Pix;
- R$ 50,00 para Crédito.

Cada componente deve ser tratado conforme sua situação financeira real.

### Valores pendentes e recebidos

Para cartão e crediário:

1. reduzir ou cancelar primeiro valores ainda pendentes;
2. somente valores efetivamente recebidos podem gerar saída financeira.

Valores sem vínculo confiável não devem ser estornados automaticamente.

Nesses casos:

- preservar os registros;
- informar necessidade de conciliação manual;
- não realizar estorno por aproximação.

### Histórico e rastreabilidade

Toda devolução deve preservar:

- venda original;
- itens devolvidos;
- quantidade;
- valor bruto;
- desconto proporcional;
- valor líquido;
- custo correspondente;
- data e hora;
- usuário;
- alocação entre formas de pagamento;
- movimentações financeiras geradas.

### Idempotência

Uma devolução não pode:

- devolver o mesmo item acima da quantidade originalmente vendida;
- aumentar o estoque duas vezes pela mesma operação;
- gerar estorno financeiro duplicado;
- reduzir indicadores duas vezes pela mesma operação.

---

### Regra Temporária de Troca

Enquanto o fluxo completo de troca não estiver implementado:

- `return` representa devolução e gera os efeitos financeiros correspondentes;
- `exchange` pode recompor o estoque do produto devolvido;
- `exchange` deve permanecer registrado no histórico;
- `exchange` não reduz o faturamento.

Esta é uma regra temporária.

O fluxo definitivo de troca deverá controlar:

- produto devolvido;
- produto substituto;
- diferença de valor;
- pagamento adicional, quando necessário;
- devolução de diferença ao cliente, quando necessário;
- movimentações de estoque;
- movimentações financeiras.

## 13.11 Cancelamento de venda

- Venda inexistente não pode ser cancelada.
- Venda já cancelada não pode ser cancelada novamente.
- Cancelamento altera a venda para status `cancelled`.
- Cancelamento devolve ao estoque as quantidades dos itens vendidos.
- Contas a receber vinculadas à venda são alteradas para status `cancelled`.
- Valores efetivamente recebidos são devolvidos ao cliente por movimentações financeiras de saída, sem apagar as entradas originais.
- Pagamento em dinheiro gera saída no caixa pelo valor recebido em dinheiro.
- Pagamento em PIX gera saída financeira pelo valor recebido via PIX.
- Recebível de débito ou crédito ainda pendente é cancelado sem gerar saída financeira.
- Recebível de débito ou crédito já recebido gera saída somente pelo valor efetivamente recebido.
- Parcelas de crediário não pagas são canceladas sem movimentação de caixa.
- Pagamentos de crediário em dinheiro ou PIX são devolvidos conforme o histórico de pagamentos de cada parcela.
- Pagamentos de crediário em débito ou crédito utilizam o recebível bancário explicitamente vinculado à parcela e à venda; somente a parte efetivamente recebida gera saída.
- Pagamentos mistos são tratados separadamente por forma de pagamento.
- Novos recebíveis de cartão originados por baixa de crediário mantêm `saleId` da venda e referência à parcela no campo `installment`, no formato `origin:<receivableId>`.
- Registros antigos de cartão sem vínculo confiável não são cancelados ou estornados por aproximação; o cancelamento preserva o registro, informa a necessidade de conciliação manual e processa apenas as partes rastreáveis.
- O estorno usa a venda e a forma de pagamento para impedir movimentações financeiras duplicadas.
- A transição para `cancelled` é protegida para que estoque, recebíveis e estornos sejam processados apenas uma vez.
- A venda, seus pagamentos, parcelas e movimentações originais permanecem no histórico.
- O cancelamento registra auditoria.

## 13.12 Caixa

- Movimentações de caixa possuem direção (`in` ou `out`), tipo, descrição, forma, valor, referência e data/hora.
- Movimentação manual exige valor maior que zero.
- Movimentação manual exige descrição.
- Saída manual exige tipo de despesa.
- A linha do tempo do caixa é ordenada por data/hora decrescente.
- O saldo do caixa é calculado somando entradas e subtraindo saídas.
- Fechamento de caixa registra data, valor esperado em dinheiro, valor informado, diferença, saldo total, entradas em dinheiro do dia, saídas em dinheiro do dia, observações e usuário responsável.
- O valor esperado em dinheiro considera movimentos com método `cash` até a data do fechamento.

## 13.13 Recebimentos de cartão e conta bancária

- Recebimento manual de cartão/conta bancária exige valor recebido maior que zero.
- Valores recebidos de crédito e débito geram entradas de caixa com método `card`.
- Esses recebimentos liquidam contas a receber com status `cardPending`.
- A liquidação de cartão percorre pendências antigas primeiro.
- A liquidação pode ser parcial se o valor recebido não cobrir todas as pendências.
- Não há cálculo automático de taxa de cartão nesse fluxo; o valor informado é tratado como valor líquido recebido.

## 13.14 Contas a pagar

- Conta a pagar exige categoria.
- Conta a pagar exige valor maior que zero.
- Conta a pagar exige data de vencimento.
- Status aceitos no backend: `pending`, `paid` e `cancelled`.
- O saldo devido considera valor original mais juros/multa menos desconto.
- Conta cancelada tem saldo em aberto igual a zero.
- Conta paga não pode receber novo pagamento.
- Pagamento de conta a pagar aceita pagamento parcial.
- O valor pago não pode ser maior que o saldo em aberto.
- Ao pagar, o sistema acumula `paidAmount`.
- A conta passa para `paid` quando o valor pago acumulado cobre o total devido.
- Se ainda houver saldo, a conta permanece `pending`.
- Todo pagamento de conta a pagar gera saída de caixa do valor pago.
- A saída de caixa de conta a pagar usa tipo `contas a pagar`.

## 13.15 Usuários e permissões

- Perfis aceitos no backend: `admin` e `operator`.
- Nome do usuário é obrigatório.
- Login do usuário é obrigatório.
- Senha é obrigatória ao criar usuário.
- Login deve ser único por loja.
- Senhas são armazenadas como hash.
- Em produção, senha fraca é rejeitada conforme validação mínima do backend.
- Apenas administrador pode criar, alterar e excluir usuários.
- Não é possível excluir o usuário atualmente logado.
- Não é possível excluir o último administrador ativo.
- Se o administrador altera seu próprio cadastro, a sessão é atualizada com os novos dados públicos.
- Alteração da própria senha exige senha atual correta.

## 13.16 Configurações, backup, importação e reset

- Status do banco, backups, exportação, importação, reset, alteração de estado e auditoria exigem administrador.
- Exportação remove o campo de senha dos usuários antes de gerar o JSON.
- Importação exige confirmação textual `RESTAURAR`.
- Reset exige confirmação textual `ZERAR`.
- Reset apaga dados de negócio e preserva usuários.
- Reset zera produtos, clientes, fornecedores, marcas, categorias, vendas, recebíveis, contas a pagar, caixa, fechamentos e devoluções.
- Backup manual por arquivo só se aplica ao SQLite.
- Em PostgreSQL, o backend retorna erro informando que backup por arquivo não se aplica.
- Upload de foto de produto aceita JPG, JPEG, PNG e WEBP.
- Upload de foto de produto rejeita arquivo maior que 5 MB.
- Upload usa Cloudinary quando configurado; caso contrário, usa armazenamento local em `uploads/products`.

## 13.17 Dashboard e relatórios

- Dashboard ignora vendas canceladas nos indicadores de vendas, lucro, pagamentos, marcas mais vendidas e gráfico por dia.
- Vendas do dia consideram `createdAt` igual à data do dashboard.
- Vendas do mês consideram o mês da data informada.
- Lucro do mês é calculado como total vendido menos custo total das vendas válidas.
- Valor do estoque é calculado por estoque atual vezes custo do produto.
- Crediário em aberto considera apenas contas a receber `storeCredit`, não canceladas e com saldo.
- Marcas mais vendidas são calculadas por quantidade de peças vendidas.
- Produtos parados são produtos com estoque positivo e mais de 90 dias sem venda, usando última venda ou `updatedAt` como base.
- Relatórios por período trocam início e fim quando o início informado é maior que o fim.
- Relatórios ignoram vendas canceladas para total, ticket médio e produtos vendidos, mas contam quantas vendas foram canceladas no período.

---

# 14. DIVERGÊNCIAS ENCONTRADAS

- A regra manual diz que clientes nunca devem ser excluídos definitivamente, mas o código permite exclusão física de cliente quando não há venda, recebível ou pagamento vinculado.
- A regra manual diz que o limite de crédito deve ser maior que R$ 0,00, mas o backend apenas impede limite negativo. Limite zero é aceito.
- A regra manual descreve Score do Cliente de 0 a 100, mas não foi encontrada implementação comprovada do cálculo de score no código analisado.
- A regra manual diz que clientes com parcelas vencidas devem gerar alerta durante nova venda. Não foi encontrada validação específica de inadimplência no fluxo de finalização de venda; o código valida limite de crédito e cliente bloqueado no crediário.
- A regra manual descreve controle de estoque por movimentações e inventário com histórico próprio. O código atual altera diretamente o saldo do produto em vendas, cancelamentos e devoluções, sem tabela própria de movimentações de estoque ou inventário confirmada.
- A regra manual diz que ações financeiras devem registrar usuário responsável quando aplicável. O fechamento de caixa registra usuário; já a entidade `cash_movements` não possui campo próprio de usuário, embora exista auditoria separada.
- A regra manual menciona que o limite de crédito poderá ser aumentado para comportar operação liberada. O código permite admin liberar venda acima do limite, mas não aumenta automaticamente o limite do cliente.

---

# 15. REGRAS QUE PRECISAM DE CONFIRMAÇÃO

- Fórmula e existência operacional do Score do Cliente.
- Quais valores de status de cliente são oficiais além de `active` e `blocked`.
- Se operador pode ou não exceder limite de crédito em algum fluxo alternativo.
- Número máximo permitido de parcelas no crediário.
- Critério definitivo para vencimento das parcelas: atualmente o código usa intervalos de 30 dias.
- Tratamento financeiro completo de devoluções e trocas.
- Regra para impedir devoluções repetidas que, somadas, ultrapassem a quantidade original vendida.
- Processo oficial de inventário e histórico de ajustes de estoque.
- Se produto inativo deve ou não aparecer em venda, estoque, catálogo e relatórios.
- Se fornecedores, marcas, categorias e produtos sem vínculo devem ser excluídos fisicamente ou desativados.
- Permissões detalhadas para perfil `operator`.
- Política de auditoria para alterações em cada módulo.

---

# 16. REGRAS IMPLÍCITAS OU ESPALHADAS PELO CÓDIGO

- A loja atual usa `store_id` fixo `matriz`.
- O sistema mantém tabelas relacionais e também um `app_state` JSON para sincronização/compatibilidade.
- Algumas regras existem no frontend e no backend, como validação de estoque disponível considerando condicionais.
- Algumas validações existem apenas no frontend, como cálculo visual de margem e preço de venda.
- O frontend usa `localStorage` como cache/fallback e as APIs como fonte quando o sistema está rodando via servidor.
- O frontend usa `sessionStorage` para guardar sessão local, mas a sessão válida é confirmada no backend por `/api/session`.
- IDs de vendas e condicionais seguem padrões sequenciais legíveis, mas outros cadastros usam IDs aleatórios.
- As listas principais costumam ser ordenadas por nome, data ou vencimento, dependendo do módulo.
- Operações críticas registram auditoria, mas nem todo histórico operacional possui tabela própria dedicada.

# 17. TROCAS

## 17.1 Finalidade do módulo Trocas

O módulo Trocas é destinado ao controle da substituição de produtos adquiridos em uma venda válida.

Toda Troca deve possuir vínculo com uma venda existente.

A Troca deve preservar:

- venda original;
- cliente;
- produtos entregues pelo cliente;
- produtos recebidos pelo cliente;
- valores considerados;
- efeitos de estoque;
- efeitos financeiros;
- data e hora;
- usuário responsável.

A Troca é uma operação distinta de:

- cancelamento;
- devolução.

O sistema deve preservar essa diferença histórica e financeira.

---

## 17.2 Origem obrigatória da Troca

Toda Troca deve iniciar a partir de uma venda existente.

O fluxo principal deve ser:

Histórico de Vendas
→ Ver Detalhes
→ TROCAR PRODUTO

Não permitir criação de Troca sem vínculo com venda.

A venda original deve ser identificada por seu identificador persistente.

Não utilizar somente:

- número visual da venda;
- nome do cliente;
- data da venda

como vínculo autoritativo.

---

## 17.3 Venda elegível para Troca

A Troca deve utilizar uma venda válida como origem.

Venda cancelada não pode receber nova Troca.

Os itens disponíveis para Troca devem considerar:

- quantidade originalmente vendida;
- quantidade já devolvida;
- quantidade já trocada.

O sistema não deve permitir trocar quantidade superior ao saldo elegível do item.

A validação autoritativa deve ocorrer no backend.

---

## 17.4 Prazo para Troca

O prazo para Troca é de 30 dias.

O prazo deve ser contado a partir da data operacional da venda.

A data operacional deve seguir America/Sao_Paulo.

Após o prazo de 30 dias, a venda não deve permitir nova Troca pelo fluxo normal.

O sistema deve validar o prazo no backend.

A interface não deve ser a única responsável pelo bloqueio.

---

## 17.5 Data civil e prazo

O cálculo do prazo de Troca deve utilizar a data operacional da venda.

Timestamps armazenados em UTC devem ser convertidos para America/Sao_Paulo antes da definição da data da venda.

O sistema não deve utilizar diretamente o prefixo textual do timestamp UTC para determinar o dia operacional.

O prazo deve ser calculado utilizando datas civis válidas.

---

## 17.6 Motivo obrigatório

Toda Troca exige motivo.

Os motivos pré-definidos são:

- Tamanho;
- Cor;
- Modelo;
- Defeito;
- Presente;
- Outro.

O usuário deve selecionar um motivo.

Quando o motivo for Outro, a descrição complementar é obrigatória.

Não permitir confirmação de Troca sem motivo válido.

---

## 17.7 Observações

A Troca pode possuir observações.

As observações são opcionais.

O campo pode ser utilizado para registrar informações complementares da operação.

As observações não substituem o motivo obrigatório.

---

## 17.8 Produtos entregues pelo cliente

O usuário deve selecionar os produtos da venda original que estão sendo entregues pelo cliente.

Somente itens pertencentes à venda original podem ser selecionados.

O sistema deve apresentar, conforme disponível:

- produto;
- código;
- marca;
- tamanho;
- cor;
- quantidade vendida;
- quantidade já devolvida;
- quantidade já trocada;
- quantidade ainda elegível para Troca.

A seleção deve permitir informar a quantidade exata.

---

## 17.9 Troca parcial de quantidade

O sistema deve permitir Troca parcial da quantidade vendida.

Exemplo:

Venda original:
3 unidades do Produto A

Cliente troca:
1 unidade

Resultado:

Quantidade trocada:
1

Quantidade ainda elegível:
2

O sistema deve considerar Trocas e devoluções anteriores antes de calcular a quantidade disponível.

A mesma quantidade não pode ser processada mais de uma vez.

---

## 17.10 Múltiplos produtos entregues

Uma única Troca pode receber vários produtos da venda original.

Exemplo:

Cliente entrega:

- 1 camiseta;
- 1 calção.

O sistema deve somar os valores líquidos elegíveis dos produtos entregues.

A Troca pode representar:

- 1 produto por 1 produto;
- 1 produto por vários produtos;
- vários produtos por 1 produto;
- vários produtos por vários produtos.

---

## 17.11 Valor de crédito da Troca

O valor considerado como crédito da Troca deve utilizar o valor líquido histórico atribuído ao item na venda original.

Não utilizar o preço atual do cadastro do produto.

O cálculo deve considerar, conforme aplicável:

- preço praticado na venda;
- desconto do item;
- desconto geral proporcional;
- acréscimos oficialmente atribuídos ao item.

O cálculo deve utilizar as mesmas regras financeiras oficiais utilizadas nas devoluções quando aplicáveis.

---

## 17.12 Exemplo de valor de crédito

Exemplo:

Preço praticado:
R$ 200,00

Desconto proporcional atribuído ao item:
R$ 20,00

Valor líquido histórico:
R$ 180,00

Crédito da Troca:
R$ 180,00

Se o preço atual do produto for R$ 250,00, essa alteração não modifica o crédito histórico.

O sistema não deve recalcular o valor da venda antiga utilizando o cadastro atual.

---

## 17.13 Crédito acumulado dos itens entregues

Quando vários produtos forem entregues na mesma Troca, o sistema deve somar seus valores líquidos elegíveis.

Exemplo:

Produto A:
R$ 100,00 líquidos

Produto B:
R$ 150,00 líquidos

Crédito total da Troca:
R$ 250,00

O crédito deve ser calculado utilizando centavos inteiros ou mecanismo equivalente que evite diferenças de arredondamento.

---

## 17.14 Condição física do produto entregue

Para cada produto entregue pelo cliente, o usuário deve informar se o item possui condição de retornar ao estoque disponível.

As opções conceituais são:

- Em condição de venda;
- Sem condição de venda.

O sistema não deve presumir automaticamente que todo produto entregue pode voltar ao estoque.

---

## 17.15 Produto em condição de venda

Quando o produto entregue estiver em condição de venda:

- o produto pode retornar ao estoque;
- o estoque real deve ser recomposto conforme a quantidade confirmada;
- o estoque disponível deve ser recalculado;
- o histórico da movimentação deve ser preservado.

A movimentação deve possuir vínculo com a Troca.

O sistema deve impedir dupla recomposição do mesmo item.

---

## 17.16 Produto sem condição de venda

Quando o produto entregue estiver sem condição de venda:

- não retornar ao estoque disponível;
- não aumentar silenciosamente o estoque real disponível para venda;
- preservar o produto entregue no histórico da Troca.

O sistema deve registrar que o item não foi reintegrado ao estoque.

Motivo Defeito não deve obrigatoriamente significar que o produto está sem condição de venda.

A condição física deve ser informada separadamente.

---

## 17.17 Produtos novos da Troca

Para existir uma Troca, deve existir pelo menos um novo produto selecionado.

O usuário deve selecionar os produtos que o cliente receberá.

Somente produtos com estoque disponível suficiente podem ser selecionados.

A seleção deve permitir:

- busca por código;
- busca por nome;
- vários produtos;
- várias unidades;
- alteração de quantidade;
- remoção antes da confirmação.

A validação de estoque deve ocorrer no backend.

---

## 17.18 Troca sem novo produto

Quando o cliente entregar o produto e não selecionar nenhum novo produto, a operação não deve ser classificada como Troca.

Nesse caso, o sistema deve utilizar o fluxo de Devolução.

A devolução deve seguir integralmente as regras financeiras oficiais do módulo Vendas.

Não utilizar Troca como forma alternativa de devolver integralmente dinheiro ao cliente.

---

## 17.19 Preço dos novos produtos

Os novos produtos devem utilizar o preço de venda atual como preço original de referência da nova operação.

O preço praticado pode ser alterado conforme as regras oficiais do módulo Vendas.

O usuário pode, quando permitido:

- alterar preço praticado;
- aplicar desconto por produto;
- aplicar desconto geral;
- aplicar acréscimo.

Alterações realizadas durante a operação não devem modificar automaticamente o preço cadastrado do produto.

---

## 17.20 Comparação financeira da Troca

O sistema deve comparar:

- crédito líquido dos produtos entregues;
- valor líquido dos novos produtos.

A operação pode resultar em:

- diferença a pagar;
- valores iguais;
- diferença a devolver.

O sistema deve calcular o resultado antes da confirmação definitiva.

---

## 17.21 Novo produto de maior valor

Quando o valor líquido dos novos produtos for superior ao crédito da Troca, o cliente deve pagar a diferença.

Exemplo:

Crédito da Troca:
R$ 180,00

Novos produtos:
R$ 250,00

Diferença a pagar:
R$ 70,00

O sistema deve cobrar somente a diferença.

---

## 17.22 Pagamento da diferença

A diferença a pagar pode utilizar as formas oficiais de pagamento:

- Dinheiro;
- Pix;
- Débito;
- Crédito;
- Crediário.

O sistema deve permitir pagamento misto.

As formas de pagamento devem seguir as mesmas regras autoritativas do módulo Vendas.

Métodos desconhecidos ou inválidos devem ser rejeitados.

---

## 17.23 Venda vinculada para diferença

Quando existir diferença a pagar, o sistema deve gerar uma venda vinculada à Troca.

A venda deve preservar:

- cliente;
- produtos novos;
- quantidades;
- valores;
- formas de pagamento;
- vínculo com a Troca;
- vínculo histórico com a operação de origem.

A venda deve seguir as regras normais de:

- estoque;
- caixa;
- recebíveis;
- Crediário;
- auditoria;
- autorização;
- idempotência e atomicidade, quando implementadas como regra oficial da criação de venda.

---

## 17.24 Novos produtos de valor igual

Quando o valor líquido dos novos produtos for igual ao crédito da Troca:

- não gerar entrada financeira;
- não gerar saída financeira;
- tratar o estoque dos produtos entregues conforme sua condição;
- baixar os produtos novos;
- preservar o histórico da Troca.

O sistema deve identificar que a diferença financeira é zero.

---

## 17.25 Novos produtos de menor valor

Quando o valor líquido dos novos produtos for inferior ao crédito da Troca, o sistema deve calcular a diferença a devolver.

Exemplo:

Crédito da Troca:
R$ 200,00

Novos produtos:
R$ 150,00

Diferença a devolver:
R$ 50,00

A operação continua sendo uma Troca porque existe pelo menos um novo produto selecionado.

A diferença deve ser devolvida ao cliente.

---

## 17.26 Devolução da diferença

A diferença financeira da Troca deve utilizar as regras financeiras oficiais de estorno da venda original.

O sistema deve considerar a composição real do pagamento original.

A devolução deve respeitar, conforme aplicável:

- Dinheiro;
- Pix;
- Débito;
- Crédito;
- Crediário;
- pagamento misto.

O sistema não deve escolher arbitrariamente uma forma de pagamento para devolver a diferença.

---

## 17.27 Ordem financeira da diferença a devolver

A diferença a devolver deve utilizar a mesma lógica autoritativa das devoluções financeiras.

Quando existirem valores pendentes, o sistema deve reduzir primeiro os valores ainda não efetivamente recebidos, conforme as regras oficiais.

Quando existir valor efetivamente recebido e rastreável, o sistema deve gerar o efeito financeiro correspondente.

Registros antigos sem vínculo confiável não devem ter forma de pagamento inventada.

Nesses casos, a operação deve exigir conciliação manual conforme as regras oficiais de devolução.

---

## 17.28 Troca e Crediário

Produtos adquiridos originalmente em venda com Crediário podem ser trocados.

A Troca não deve reescrever automaticamente as parcelas antigas apenas porque houve substituição de produto.

O crédito da Troca utiliza o valor líquido histórico do produto entregue.

Quando o novo produto possuir valor igual ou superior, as parcelas originais permanecem preservadas.

---

## 17.29 Diferença a pagar e Crediário

Quando existir diferença a pagar, o cliente pode utilizar Crediário para a diferença.

A nova utilização de Crediário deve seguir as regras oficiais vigentes no momento da nova operação.

Devem ser validados:

- cliente;
- situação do cliente;
- limite disponível;
- parcelas;
- autorizações aplicáveis.

A nova diferença não deve ser adicionada silenciosamente a uma parcela antiga.

O sistema deve preservar a nova operação vinculada à Troca.

---

## 17.30 Diferença a devolver e Crediário

Quando existir diferença a devolver em uma Troca originada de venda com Crediário, o sistema deve seguir a regra oficial de abatimento financeiro.

Parcelas pendentes devem ser abatidas conforme a ordem oficial do Crediário.

Somente após consumir valores pendentes devem ser tratados valores já pagos.

O sistema não deve devolver dinheiro referente a valor que ainda não foi efetivamente recebido quando esse valor puder ser corretamente abatido do saldo pendente.

---

## 17.31 Montagem da Troca

Enquanto a Troca estiver somente em montagem:

- o produto entregue não retorna ao estoque;
- os novos produtos não são baixados;
- nenhuma reserva definitiva é criada em razão da simples seleção;
- nenhuma entrada financeira é criada;
- nenhuma saída financeira é criada;
- nenhum recebível é criado;
- nenhuma parcela é criada ou alterada.

A operação somente produz efeitos após confirmação definitiva.

---

## 17.32 Resumo antes da confirmação

Antes da confirmação, o sistema deve apresentar resumo da Troca.

O resumo deve identificar:

- produtos entregues;
- quantidades;
- condição física;
- crédito por item;
- crédito total;
- novos produtos;
- quantidades;
- valor dos novos produtos;
- diferença a pagar;
- diferença a devolver;
- formas de pagamento, quando aplicável;
- motivo.

O usuário deve confirmar a operação.

---

## 17.33 Confirmação da Troca

Ao confirmar a Troca, o backend deve validar novamente:

- venda original;
- prazo de 30 dias;
- situação da venda;
- cliente;
- itens elegíveis;
- quantidades;
- devoluções anteriores;
- Trocas anteriores;
- estoque disponível dos novos produtos;
- valores históricos;
- formas de pagamento;
- Crediário, quando aplicável.

As validações devem ocorrer antes dos efeitos definitivos.

---

## 17.34 Efeitos da confirmação

Após confirmação válida, o sistema deve:

1. criar a Troca;
2. registrar os itens entregues;
3. registrar os novos produtos;
4. tratar o retorno ao estoque dos itens elegíveis;
5. baixar os novos produtos;
6. calcular e aplicar a diferença financeira;
7. criar a venda vinculada quando aplicável;
8. criar caixa, recebíveis ou Crediário quando aplicável;
9. registrar alocações financeiras quando aplicável;
10. registrar usuário;
11. registrar data e hora;
12. preservar auditoria.

Os efeitos devem representar uma única operação lógica.

---

## 17.35 Atomicidade da Troca

A confirmação da Troca deve ser atômica.

Não permitir estado parcial em que:

- produto antigo retornou ao estoque, mas o novo não foi baixado;
- produto novo foi baixado, mas a Troca não foi criada;
- diferença foi recebida sem a Troca ser concluída;
- diferença foi devolvida sem registro da Troca;
- venda vinculada foi criada sem vínculo;
- Crediário foi alterado sem conclusão da operação.

Qualquer falha deve reverter os efeitos da operação.

---

## 17.36 Idempotência da Troca

A confirmação da Troca deve possuir proteção contra processamento duplicado.

Clique duplo, retry ou resposta desconhecida não podem gerar:

- duas Trocas;
- dupla entrada no estoque;
- dupla baixa dos produtos novos;
- dupla cobrança da diferença;
- dupla devolução financeira;
- duas vendas vinculadas.

A operação deve possuir identificador idempotente persistente.

A mesma chave e o mesmo conteúdo devem retornar o resultado já concluído.

A mesma chave com conteúdo financeiro diferente deve ser rejeitada.

---

## 17.37 Concorrência de estoque

A Troca deve validar o estoque disponível dos novos produtos dentro da operação protegida.

Exemplo:

Existe 1 unidade disponível.

Dois usuários tentam utilizar a mesma unidade em operações diferentes.

Somente uma operação pode concluir a baixa.

A outra deve recalcular a disponibilidade e ser recusada.

O sistema não pode gerar estoque negativo.

---

## 17.38 Cancelamento durante a montagem

Enquanto a Troca não estiver confirmada, o usuário pode cancelar a montagem.

Nesse caso:

- nenhuma Troca é criada;
- nenhum estoque é alterado;
- nenhum financeiro é gerado.

Não existe necessidade de estorno para operação que nunca foi confirmada.

---

## 17.39 Correção após Troca concluída

Troca concluída não deve ser editada diretamente.

O sistema não deve permitir alteração silenciosa de:

- produtos entregues;
- produtos novos;
- quantidades;
- valores;
- diferença;
- motivo;
- condição física.

Quando houver erro após a conclusão, deve existir operação formal de cancelamento ou estorno da Troca.

---

## 17.40 Cancelamento ou estorno da Troca

O cancelamento de Troca concluída deve preservar o histórico original.

A operação deve reverter os efeitos válidos da Troca.

A reversão deve considerar:

- estoque dos produtos entregues;
- estoque dos novos produtos;
- diferença recebida;
- diferença devolvida;
- venda vinculada;
- recebíveis;
- Crediário.

O sistema deve impedir estorno duplicado.

O cancelamento exige motivo.

O sistema deve registrar:

- motivo;
- data e hora;
- usuário responsável.

---

## 17.41 Troca e venda original

A Troca não deve apagar a venda original.

A venda original permanece preservada.

Os itens trocados devem ser identificáveis no histórico da venda.

O sistema deve permitir visualizar:

- quantidade vendida;
- quantidade devolvida;
- quantidade trocada;
- quantidade ainda elegível.

A Troca deve aparecer nos detalhes da venda original.

---

## 11.42 Troca e devolução

Troca e devolução devem utilizar os mesmos valores históricos autoritativos quando calcularem o valor líquido de um item da venda original.

A soma acumulada de:

- devoluções;
- Trocas

não pode ultrapassar a quantidade vendida.

O sistema deve considerar todas as operações anteriores antes de aceitar nova quantidade.

---

## 17.43 Troca e cancelamento da venda

Venda cancelada não aceita nova Troca.

Uma Troca concluída deve ser considerada antes de permitir cancelamento da venda original.

O sistema não deve cancelar silenciosamente uma venda ignorando produtos já trocados.

As regras de cancelamento devem preservar a integridade das Trocas vinculadas.

Quando existir conflito entre cancelamento da venda e Troca concluída, o backend deve impedir operação inconsistente ou executar o fluxo formal de reversão necessário.

---

## 17.44 Número da Troca

Cada Troca deve possuir número próprio.

O número deve ser gerado automaticamente.

O usuário não deve informar manualmente o número.

O número deve ser utilizado em:

- detalhes;
- histórico;
- impressão;
- busca;
- relatórios.

---

## 17.45 Usuário responsável

Toda Troca deve registrar o usuário autenticado responsável.

O usuário não deve ser escolhido manualmente pelo navegador.

O backend deve utilizar a sessão autenticada e o cadastro persistido do usuário.

A desativação futura do usuário não deve remover sua autoria histórica.

---

## 17.46 Histórico da Troca

A Troca deve preservar, no mínimo:

- número da Troca;
- venda original;
- cliente;
- produtos entregues;
- quantidades entregues;
- valor líquido de crédito por item;
- crédito total;
- condição física dos itens entregues;
- reintegração ou não ao estoque;
- produtos novos;
- quantidades;
- valores;
- diferença financeira;
- formas de pagamento;
- venda vinculada;
- motivo;
- observações;
- data e hora;
- usuário responsável.

O histórico não deve ser apagado.

---

## 17.47 Impressão da Troca

O sistema deve permitir impressão simples da Troca.

O comprovante deve possuir cabeçalho:

MOVA SPORTS

Deve apresentar:

- número da Troca;
- data e hora;
- cliente;
- venda original;
- produtos entregues pelo cliente;
- produtos recebidos pelo cliente;
- crédito considerado;
- diferença paga ou devolvida;
- forma ou formas de pagamento;
- usuário responsável.

Não é necessária assinatura digital.

---

## 17.48 Acesso à Troca

O acesso principal à criação de Troca deve ocorrer por:

Histórico de Vendas
→ Ver Detalhes
→ TROCAR PRODUTO

O sistema não precisa possuir item Trocas no menu lateral neste momento.

A criação deve sempre partir da venda original.

---

## 17.49 Consulta de Trocas

As Trocas devem permanecer consultáveis.

A consulta pode existir dentro do Histórico de Vendas ou área de Relatórios.

Deve permitir busca ou filtro por:

- número da Troca;
- número da venda;
- cliente;
- período.

A consulta deve permitir abrir os detalhes da Troca.

---

## 17.50 Troca no Histórico de Vendas

Os detalhes da venda devem identificar Trocas vinculadas.

Devem ser identificáveis:

- número da Troca;
- data;
- produtos envolvidos;
- quantidades;
- crédito utilizado;
- diferença financeira;
- situação da Troca.

A existência de Troca não deve apagar os dados originais da venda.

---

## 17.51 Troca no Dashboard

A Troca deve substituir a regra temporária atualmente utilizada para exchange.

O Dashboard deve utilizar os efeitos financeiros e gerenciais definitivos da operação.

O sistema não deve simplesmente ignorar toda Troca nos indicadores.

Os efeitos devem considerar:

- produtos originalmente vendidos;
- produtos trocados;
- novos produtos;
- diferença financeira;
- custo histórico correspondente.

O cálculo definitivo deve ser documentado e utilizar os registros oficiais da Troca.

---

## 17.52 Troca nos Relatórios

Os Relatórios devem considerar as Trocas conforme seus efeitos oficiais.

Relatórios de produtos vendidos devem permitir calcular quantidades líquidas válidas.

Relatórios financeiros devem considerar diferenças recebidas ou devolvidas.

Relatórios de lucro devem utilizar custos históricos.

O sistema deve preservar vínculo entre:

- venda original;
- Troca;
- venda vinculada, quando existir.

Não recalcular o passado utilizando o cadastro atual dos produtos.

---

## 17.53 Regras gerais do módulo Trocas

O sistema deve:

- exigir venda original;
- impedir Troca sem vínculo com venda;
- utilizar prazo máximo de 30 dias;
- calcular o prazo pela data operacional America/Sao_Paulo;
- exigir motivo;
- exigir descrição quando o motivo for Outro;
- permitir observações;
- permitir selecionar produtos da venda original;
- permitir Troca parcial de quantidade;
- considerar devoluções e Trocas anteriores;
- impedir quantidade superior ao saldo elegível;
- utilizar valor líquido histórico como crédito;
- não utilizar preço atual para recalcular crédito;
- permitir vários produtos entregues;
- permitir vários produtos novos;
- exigir pelo menos um novo produto para caracterizar Troca;
- direcionar operação sem novo produto para Devolução;
- registrar condição física dos produtos entregues;
- reintegrar ao estoque somente produtos em condição de venda;
- não reintegrar automaticamente produtos sem condição de venda;
- permitir diferença a pagar;
- permitir Dinheiro;
- permitir Pix;
- permitir Débito;
- permitir Crédito;
- permitir Crediário;
- permitir pagamento misto;
- permitir diferença a devolver;
- utilizar as regras financeiras oficiais de devolução para a diferença devolvida;
- permitir Troca de venda com Crediário;
- não reescrever silenciosamente parcelas antigas;
- validar estoque dos novos produtos no backend;
- apresentar resumo antes da confirmação;
- aplicar efeitos somente após confirmação;
- executar a Troca de forma atômica;
- possuir proteção idempotente;
- impedir processamento duplicado;
- impedir dupla entrada de estoque;
- impedir dupla baixa de estoque;
- impedir dupla cobrança;
- impedir dupla devolução financeira;
- preservar a venda original;
- preservar vínculo com venda vinculada;
- registrar número automático;
- registrar usuário autenticado;
- registrar data e hora;
- preservar histórico;
- permitir impressão simples;
- permitir consulta de Trocas;
- substituir a regra temporária de exchange por regra financeira e gerencial definitiva.

# 18. CONFIGURAÇÕES

## 18.1 Finalidade das Configurações

A área Configurações é destinada aos dados gerais da loja e aos parâmetros administrativos permitidos pelo sistema.

As Configurações não devem substituir regras autoritativas de negócio.

Regras financeiras, operacionais ou de integridade definidas como fixas pelo sistema não podem ser alteradas livremente pelo usuário.

A área deve preservar histórico das alterações realizadas.

---

## 18.2 Acesso às Configurações

Somente usuários com perfil Administrador podem acessar a área Configurações.

Usuários com perfil Operador não podem acessar a tela de Configurações.

A autorização deve ser validada no backend.

Ocultar a opção na interface não é proteção suficiente.

O backend deve recuperar o perfil atual do usuário autenticado utilizando o cadastro persistido.

Não confiar em perfil informado pelo navegador.

---

## 18.3 Operador e Configurações

A restrição à área Configurações não altera as permissões operacionais gerais do perfil Operador.

O Operador continua podendo executar as funções permitidas pelas regras oficiais dos demais módulos.

A restrição desta seção é específica aos parâmetros gerais e administrativos da loja.

---

## 18.4 Dados da loja

A área Configurações deve possuir uma seção DADOS DA LOJA.

Devem ser permitidos os seguintes campos:

- Nome da loja;
- Nome fantasia;
- CNPJ;
- CPF;
- Telefone;
- WhatsApp;
- E-mail;
- CEP;
- Endereço;
- Número;
- Complemento;
- Bairro;
- Cidade;
- Estado.

---

## 18.5 Nome da loja

O Nome da loja é obrigatório.

O sistema não deve permitir salvar as Configurações sem um Nome da loja válido.

O nome configurado deve ser utilizado nas apresentações oficiais da loja onde aplicável.

O valor atualmente utilizado como MOVA SPORTS deve ser substituído pelo Nome da loja configurado nos locais definidos pelas regras de apresentação.

---

## 18.6 Nome fantasia

O Nome fantasia é opcional.

Quando informado, deve permanecer disponível para identificação comercial e futuras apresentações definidas pelo sistema.

O Nome fantasia não substitui obrigatoriamente o Nome da loja.

---

## 18.7 CPF e CNPJ da loja

CPF e CNPJ são opcionais.

A loja pode possuir:

- CPF;
- CNPJ;
- nenhum dos dois

conforme sua configuração.

Quando CPF for informado, deve ser validado matematicamente.

Quando CNPJ for informado, deve ser validado matematicamente.

Não aceitar CPF ou CNPJ matematicamente inválido.

A validação autoritativa deve ocorrer no backend.

---

## 18.8 Contatos da loja

A Configuração pode armazenar:

- Telefone;
- WhatsApp;
- E-mail.

Esses dados podem ser utilizados em:

- comprovantes;
- relatórios;
- impressões;
- identificação da loja.

A exibição de cada informação nos comprovantes deve respeitar as preferências de impressão.

---

## 18.9 Endereço da loja

A Configuração pode armazenar:

- CEP;
- Endereço;
- Número;
- Complemento;
- Bairro;
- Cidade;
- Estado.

Os dados devem permanecer separados.

O endereço pode ser utilizado em comprovantes, relatórios e impressões conforme a preferência configurada.

---

## 18.10 Logo da loja

O Administrador pode cadastrar a logo da loja.

Devem ser aceitos os formatos:

- JPG;
- JPEG;
- PNG;
- WEBP.

O tamanho máximo do arquivo deve ser de 5 MB.

Arquivos fora dos formatos permitidos devem ser rejeitados.

Arquivos acima do limite devem ser rejeitados.

A validação deve ocorrer no backend.

---

## 18.11 Uso da logo

A logo configurada pode ser utilizada em:

- comprovantes;
- relatórios PDF;
- impressões;
- tela de login.

Quando não existir logo configurada, o sistema deve apresentar o Nome da loja onde a identificação visual for necessária.

A ausência de logo não pode impedir o funcionamento do sistema.

---

## 18.12 Nome da loja e nome do sistema

O Nome da loja e o nome da aplicação são conceitos distintos.

Exemplo:

Nome da loja:
MOVA SPORTS

Nome do sistema:
nome próprio da aplicação, quando existir.

O Nome da loja deve identificar o estabelecimento.

O nome do sistema pode identificar o software.

A alteração do Nome da loja não deve alterar automaticamente a identidade técnica da aplicação.

---

## 18.13 Substituição de textos fixos

Referências fixas a MOVA SPORTS devem ser substituídas pelo Nome da loja configurado onde representarem a identificação do estabelecimento.

Isso se aplica, conforme o contexto, a:

- login;
- comprovantes;
- relatórios;
- impressões.

Textos técnicos ou nomes próprios da aplicação não devem ser substituídos automaticamente.

---

## 18.14 Preferências de impressão

A área Configurações deve permitir definir quais dados da loja aparecem nos comprovantes.

O Nome da loja deve ser sempre apresentado.

O Administrador pode ativar ou desativar a exibição de:

- CPF ou CNPJ;
- Telefone;
- WhatsApp;
- Endereço;
- E-mail.

As preferências devem ser aplicadas aos comprovantes compatíveis.

---

## 18.15 Nome da loja obrigatório nas impressões

O Nome da loja não pode ser ocultado dos comprovantes oficiais gerados pelo sistema.

As demais informações configuráveis podem ser ativadas ou desativadas.

A ausência de um dado cadastrado deve impedir somente sua exibição.

Não apresentar campos vazios desnecessários.

---

## 18.16 Mensagem de rodapé

O Administrador pode configurar uma mensagem personalizada para o rodapé dos comprovantes de venda.

O campo é opcional.

Exemplos:

Obrigado pela preferência!

Trocas em até 30 dias mediante apresentação deste comprovante.

O sistema deve possuir limite razoável de caracteres.

O texto deve ser tratado como texto simples.

Não interpretar HTML ou código executável informado no campo.

---

## 18.17 Aplicação da mensagem de rodapé

A mensagem personalizada deve ser aplicada aos comprovantes de venda.

Comprovantes específicos de:

- Condicional;
- Troca

podem utilizar os textos próprios definidos em suas regras oficiais.

A mensagem geral não deve substituir automaticamente textos obrigatórios desses módulos.

---

## 18.18 Numeração das vendas

O número da venda é automático.

O Administrador não pode alterar manualmente o próximo número da venda pelas Configurações.

Não disponibilizar campo editável de próxima venda.

Quando necessário, o sistema pode apresentar a última numeração utilizada em modo somente leitura.

---

## 18.19 Numeração do Condicional

O número do Condicional é automático.

O Administrador não pode alterar manualmente o próximo número do Condicional.

Quando necessário, a última numeração utilizada pode ser apresentada somente para consulta.

---

## 18.20 Numeração das Trocas

O número da Troca é automático.

O Administrador não pode alterar manualmente o próximo número da Troca.

Quando necessário, a última numeração utilizada pode ser apresentada somente para consulta.

---

## 18.21 Integridade das numerações

Numerações operacionais não são parâmetros administrativos livres.

O sistema deve impedir alterações manuais que possam provocar:

- duplicidade;
- reutilização de número;
- conflito histórico;
- quebra de vínculo.

A geração deve permanecer autoritativa no backend.

---

## 18.22 Prazo do Condicional

O prazo padrão do Condicional é fixo em 3 dias.

O prazo não é configurável pelo Administrador.

A área Configurações não deve possuir campo para alterar esse prazo.

A regra deve seguir a seção oficial do módulo Condicional.

---

## 18.23 Prazo para Troca

O prazo máximo para Troca é fixo em 30 dias.

O prazo não é configurável pelo Administrador.

A área Configurações não deve possuir campo para alterar esse prazo.

A regra deve seguir a seção oficial do módulo Trocas.

---

## 18.24 Máximo de parcelas do Crediário

O Crediário permite no máximo 3 parcelas.

O limite máximo não é configurável pelo Administrador.

A área Configurações não deve possuir campo para aumentar a quantidade máxima de parcelas.

O backend deve rejeitar quantidade superior a 3 parcelas.

---

## 18.25 Data da primeira parcela do Crediário

Ao criar um Crediário, o sistema deve sugerir a data da primeira parcela.

A sugestão padrão deve ser 30 dias após a data operacional da venda.

A sugestão não é obrigatória.

O usuário pode alterar a data da primeira parcela antes da confirmação da venda.

A data efetivamente escolhida deve ser validada pelo backend.

---

## 18.26 Data-base das parcelas

A data da primeira parcela define o dia-base mensal do Crediário.

As parcelas seguintes devem utilizar o mesmo dia-base da primeira parcela sempre que esse dia existir no mês correspondente.

Exemplo:

Primeira parcela:
10/08/2026

Segunda parcela:
10/09/2026

Terceira parcela:
10/10/2026

O sistema não deve calcular as parcelas seguintes simplesmente adicionando 30 dias ao vencimento anterior.

---

## 18.27 Meses sem o dia-base

Quando o dia-base da primeira parcela não existir em determinado mês, utilizar o último dia válido daquele mês.

Exemplo:

Primeira parcela:
31/01/2026

Segunda parcela:
28/02/2026

Terceira parcela:
31/03/2026

Em ano bissexto:

Primeira parcela:
31/01/2028

Segunda parcela:
29/02/2028

Terceira parcela:
31/03/2028

O uso do último dia válido de um mês não altera permanentemente o dia-base original.

Nos meses seguintes, o sistema deve voltar ao dia-base da primeira parcela quando ele existir.

---

## 18.28 Exemplo de preservação do dia-base

Exemplo:

Dia-base:
31

Parcelas:

31/01
28/02
31/03

O sistema não deve produzir:

31/01
28/02
28/03

O dia-base original permanece 31.

A adaptação ao último dia do mês é aplicada somente ao mês que não possui o dia-base.

---

## 18.29 Alteração da primeira parcela

Enquanto a venda ainda não estiver confirmada, o usuário pode alterar a data da primeira parcela.

Ao alterar a primeira parcela, o sistema deve recalcular automaticamente os vencimentos seguintes.

Exemplo:

Data inicialmente sugerida:
10/08

Usuário altera para:
15/08

Parcelas:

15/08
15/09
15/10

As datas devem ser apresentadas ao usuário antes da confirmação.

---

## 18.30 Confirmação das datas do Crediário

Antes de concluir a venda com Crediário, o usuário deve conseguir visualizar as datas das parcelas.

O backend deve recalcular ou validar os vencimentos utilizando a data-base informada.

O navegador não deve ser autoritativo para definir silenciosamente vencimentos incompatíveis com a regra oficial.

---

## 18.31 Estoque mínimo dos produtos

O estoque mínimo é um parâmetro individual do produto.

O estoque mínimo pode ser igual a 0.

Não permitir estoque mínimo:

- negativo;
- fracionado.

Quando o estoque mínimo for igual a 0, considerar que o produto não possui limite mínimo específico configurado.

O estoque mínimo não é obrigatório para o funcionamento operacional do produto.

A validação deve ocorrer no backend.

---

## 18.32 Estoque mínimo na criação do produto

Ao criar um produto, o estoque mínimo deve iniciar automaticamente com valor 0.

O usuário não é obrigado a alterar o estoque mínimo durante o cadastro.

O usuário pode informar valor inteiro superior a 0 quando desejar manter uma referência mínima específica para aquele produto.

O sistema não deve permitir valor negativo ou fracionado.

---

## 18.33 Estoque mínimo e Configurações

Não é necessário possuir configuração global de estoque mínimo padrão.

Todo novo produto inicia com estoque mínimo igual a 0.

Cada produto pode possuir seu próprio estoque mínimo igual ou superior a 0.

A área Configurações não deve alterar em massa o estoque mínimo dos produtos existentes.

O estoque mínimo não gera alerta na Central de Alertas.

O valor pode permanecer disponível no módulo Estoque para filtros, consultas e análises compatíveis com sua finalidade.

## 18.34 Lembrar-me

A opção Lembrar-me deve permanecer disponível para todos os usuários na tela de login.

Cada usuário decide se deseja utilizar a opção no momento do login.

O Administrador não precisa ativar ou desativar globalmente essa funcionalidade pelas Configurações.

O comportamento deve respeitar as regras de segurança e sessão oficiais.

---

## 18.35 Formas oficiais de pagamento

As formas oficiais de pagamento são:

- Dinheiro;
- Pix;
- Débito;
- Crédito;
- Crediário.

As formas de pagamento são controladas pelo sistema.

Não são cadastros livres.

---

## 18.36 Proibição de novas formas de pagamento pelas Configurações

O Administrador não pode criar novas formas de pagamento pelas Configurações.

Não permitir cadastrar formas livres como:

- Cheque;
- Vale;
- Transferência;
- Fiado alternativo;
- outros métodos sem regra financeira implementada.

Cada forma oficial possui efeitos financeiros próprios.

Uma nova forma de pagamento somente pode existir após definição e implementação de sua regra de negócio.

---

## 18.37 Dados e Backup

A área Configurações pode possuir uma seção DADOS E BACKUP.

O acesso é exclusivo do Administrador.

A seção pode permitir exportação de backup dos dados da loja.

A exportação deve respeitar as regras de segurança do sistema.

---

## 18.38 Exportação de backup

O Administrador pode gerar ou exportar um backup dos dados da loja.

A operação deve registrar:

- data e hora;
- usuário responsável.

A geração do backup não deve alterar os dados operacionais.

A existência de backup não substitui as políticas de backup da infraestrutura de produção.

---

## 18.39 Restauração de backup

A restauração de backup não deve ser disponibilizada como operação simples nas Configurações neste momento.

Não disponibilizar fluxo comum de:

- importar banco;
- restaurar estado;
- substituir todos os dados

sem auditoria específica da funcionalidade.

A restauração deve permanecer fora das Configurações normais até definição técnica e de segurança própria.

---

## 18.40 Reset do sistema

Não disponibilizar nas Configurações botão para:

- RESETAR SISTEMA;
- APAGAR TODOS OS DADOS;
- LIMPAR BANCO;
- ZERAR LOJA.

Funções legadas relacionadas a reset não devem ser consideradas regras oficiais de Configurações.

Qualquer funcionalidade futura de exclusão global exige auditoria e regra específica.

---

## 18.41 Importação de dados

A importação geral de dados ou app_state não deve ser disponibilizada como função administrativa comum neste momento.

Funções legadas de importação devem ser auditadas separadamente.

Não oficializar importação destrutiva ou substituição integral do estado pela tela Configurações.

---

## 18.42 Auditoria das Configurações

Toda alteração de Configurações deve gerar registro de auditoria.

O registro deve preservar:

- configuração alterada;
- valor anterior;
- novo valor;
- data e hora;
- usuário responsável.

A auditoria deve utilizar o usuário autenticado.

O usuário responsável não deve ser informado manualmente pelo navegador.

---

## 18.43 Alterações múltiplas

Quando uma única confirmação alterar vários campos, o sistema deve preservar informação suficiente para identificar todas as alterações relevantes.

Exemplo:

Telefone:
De A para B

Endereço:
De C para D

Mensagem de rodapé:
De E para F

A auditoria não deve registrar apenas a informação genérica Configurações alteradas quando isso impedir a identificação do que foi modificado.

---

## 18.44 Informações sensíveis

Valores secretos ou credenciais futuras não devem ser gravados em texto aberto no histórico de alterações.

Quando uma configuração sensível existir, a auditoria deve registrar a ocorrência da alteração sem preservar o segredo.

Exemplo:

Credencial alterada

Não registrar:

Valor anterior:
senha123

Novo valor:
senha456

---

## 18.45 Data e hora da auditoria

A data e hora da alteração devem seguir as regras oficiais de timestamp do sistema.

Novos timestamps devem ser armazenados em UTC com offset explícito.

A apresentação deve utilizar America/Sao_Paulo.

A data operacional deve ser calculada conforme as regras gerais do sistema.

---

## 18.46 Persistência das Configurações

As Configurações devem ser persistidas no backend.

O navegador não deve ser a fonte autoritativa dos parâmetros da loja.

LocalStorage não deve ser utilizado como única persistência das Configurações oficiais.

As APIs e operações devem utilizar os valores persistidos da loja.

---

## 18.47 Configurações por loja

As Configurações pertencem à loja correspondente.

Os dados devem preservar vínculo persistente com a loja.

O sistema não deve misturar Configurações de lojas diferentes.

Toda leitura e alteração deve respeitar o contexto da loja autenticada.

---

## 18.48 Validação no backend

O backend deve validar, conforme aplicável:

- perfil Administrador;
- Nome da loja obrigatório;
- CPF;
- CNPJ;
- formatos de arquivo;
- tamanho da logo;
- valores permitidos;
- integridade das preferências.

Não confiar exclusivamente nas validações HTML ou JavaScript.

---

## 18.49 Regras fixas não configuráveis

As seguintes regras são fixas e não devem ser alteráveis pelas Configurações:

- prazo do Condicional de 3 dias;
- prazo para Troca de 30 dias;
- máximo de 3 parcelas no Crediário;
- formas oficiais de pagamento;
- numeração automática das vendas;
- numeração automática dos Condicionais;
- numeração automática das Trocas;

Alterações nessas regras exigem mudança formal das regras de negócio e implementação correspondente.

---

## 18.50 Regras gerais das Configurações

O sistema deve:

- permitir acesso às Configurações somente ao Administrador;
- validar autorização no backend;
- manter Operador fora da área Configurações;
- permitir cadastro dos dados da loja;
- exigir Nome da loja;
- validar CPF quando informado;
- validar CNPJ quando informado;
- permitir cadastro de logo;
- aceitar JPG;
- aceitar JPEG;
- aceitar PNG;
- aceitar WEBP;
- limitar a logo a 5 MB;
- utilizar o Nome da loja nas identificações do estabelecimento;
- separar Nome da loja e nome do sistema;
- permitir preferências de dados exibidos nos comprovantes;
- sempre exibir o Nome da loja nos comprovantes;
- permitir mensagem opcional de rodapé nas vendas;
- impedir alteração manual das numerações automáticas;
- manter prazo do Condicional fixo em 3 dias;
- manter prazo de Troca fixo em 30 dias;
- limitar Crediário a 3 parcelas;
- sugerir a primeira parcela para 30 dias;
- permitir alteração da data da primeira parcela antes da confirmação;
- utilizar a primeira parcela como data-base mensal;
- manter o mesmo dia-base nas parcelas seguintes;
- utilizar o último dia válido quando o mês não possuir o dia-base;
- retornar ao dia-base original nos meses seguintes;
- permitir estoque mínimo igual a 0;
- impedir estoque mínimo negativo;
- impedir estoque mínimo fracionado;
- iniciar novo produto com estoque mínimo 0;
- não exigir alteração do estoque mínimo durante o cadastro;
- não utilizar estoque mínimo como origem de alerta na Central de Alertas;
- manter Lembrar-me disponível aos usuários;
- limitar pagamentos às formas oficiais;
- impedir criação livre de formas de pagamento;
- permitir exportação de backup ao Administrador;
- não disponibilizar restauração simples de backup;
- não disponibilizar reset global do sistema;
- não oficializar importação geral sem auditoria específica;
- auditar alterações das Configurações;
- preservar valor anterior e novo valor quando não forem sensíveis;
- não gravar segredos em texto aberto na auditoria;
- utilizar timestamps oficiais;
- persistir Configurações no backend;
- preservar vínculo com a loja;
- validar regras autoritativamente no backend.

# 19. ALERTAS DO SISTEMA

## 19.1 Finalidade da Central de Alertas

A Central de Alertas é destinada a apresentar situações operacionais atuais que exigem atenção dos usuários da loja.

Os alertas devem representar o estado atual do sistema.

A Central de Alertas não substitui:

- relatórios;
- históricos;
- auditoria;
- indicadores dos módulos.

Os alertas devem facilitar a identificação e o acesso às situações pendentes.

---

## 19.2 Acesso à Central de Alertas

A Central de Alertas deve ser acessada por um ícone de sino no topo do sistema.

O sino deve apresentar a quantidade de alertas novos para o usuário autenticado.

Exemplo:

🔔 5

Ao clicar no sino, o sistema deve abrir a lista dos alertas atuais.

---

## 19.3 Usuários com acesso aos alertas

Usuários com perfil Administrador podem acessar a Central de Alertas.

Usuários com perfil Operador também podem acessar a Central de Alertas.

Administrador e Operador podem visualizar os alertas operacionais da loja.

A Central de Alertas não deve utilizar o perfil para ocultar situações operacionais que o Operador pode tratar normalmente.

As permissões administrativas exclusivas permanecem definidas nas regras de Usuários, Permissões e Configurações.

---

## 19.4 Tipos oficiais de alerta

A Central de Alertas deve possuir inicialmente os seguintes tipos oficiais:

1. Crediário atrasado;
2. Condicional atrasado;
3. Conta vencendo hoje;
4. Conta vencida;
5. Última unidade disponível.

Estoque mínimo não gera alerta.

Produto sem estoque não gera alerta na Central de Alertas.

Bloqueio ou tentativas de login não fazem parte da Central de Alertas operacional.

---

## 19.5 Alertas calculados pelo estado atual

Os alertas operacionais devem ser calculados utilizando o estado atual do sistema.

Não tratar o alerta operacional como uma mensagem fixa independente da situação que o originou.

Exemplo:

Conta está vencida:
alerta ativo.

Conta é paga integralmente:
alerta deixa de existir.

Parcela está atrasada:
alerta ativo.

Parcela é quitada:
alerta deixa de existir.

Condicional está atrasado:
alerta ativo.

Condicional é finalizado:
alerta deixa de existir.

Estoque disponível é 1:
alerta ativo.

Estoque disponível aumenta:
alerta deixa de existir.

---

## 19.6 Resolução automática do alerta

O usuário não precisa clicar em Resolver alerta.

O alerta deve deixar de existir automaticamente quando a situação que o originou deixar de existir.

Marcar um alerta como lido não significa resolver a situação.

A resolução depende do estado operacional correspondente.

---

## 19.7 Data operacional dos alertas

Alertas dependentes de data devem utilizar a data operacional oficial do sistema.

O fuso operacional é:

America/Sao_Paulo.

Timestamps armazenados em UTC devem ser convertidos para o fuso operacional antes da definição do dia correspondente.

Datas civis no formato YYYY-MM-DD devem permanecer datas civis.

O sistema não deve utilizar diretamente o prefixo textual de um timestamp UTC para determinar atraso ou vencimento.

---

## 19.8 Alerta de Crediário atrasado

O sistema deve gerar alerta de Crediário atrasado quando existir parcela com:

- saldo líquido em aberto;
- vencimento anterior à data operacional atual.

O saldo deve considerar:

- valor original;
- pagamentos;
- devoluções;
- abatimentos oficialmente registrados.

Parcela sem saldo pendente não gera alerta.

---

## 19.9 Agrupamento do Crediário atrasado

Os alertas de Crediário atrasado devem ser agrupados por cliente.

Não apresentar obrigatoriamente um alerta separado para cada parcela atrasada.

Exemplo:

Crediário atrasado

Maria da Silva

2 parcelas atrasadas

Total em aberto: R$ 300,00

O agrupamento deve considerar somente parcelas realmente atrasadas e com saldo líquido em aberto.

---

## 19.10 Informações do alerta de Crediário

O alerta de Crediário atrasado deve apresentar, conforme aplicável:

- cliente;
- quantidade de parcelas atrasadas;
- saldo total atrasado;
- quantidade de dias de atraso.

Quando existirem várias parcelas atrasadas, a quantidade de dias pode utilizar como referência a parcela vencida há mais tempo.

O sistema deve deixar claro que o valor apresentado representa o saldo atrasado.

---

## 19.11 Ação do alerta de Crediário

Ao clicar no alerta de Crediário atrasado, o sistema deve abrir o Crediário correspondente ao cliente.

O usuário deve conseguir visualizar as parcelas relacionadas.

A navegação deve utilizar identificadores persistentes.

Não utilizar somente o nome do cliente como vínculo autoritativo.

---

## 19.12 Alerta de Condicional atrasado

O sistema deve gerar alerta quando existir Condicional:

- ativo;
- com peças ainda em posse do cliente;
- com prazo de 3 dias ultrapassado.

O prazo deve seguir as regras oficiais do módulo Condicional.

Deve existir um alerta por Condicional atrasado.

---

## 19.13 Informações do alerta de Condicional

O alerta deve apresentar, conforme aplicável:

- cliente;
- número do Condicional;
- quantidade de peças ainda com o cliente;
- data prevista de retorno;
- quantidade de dias de atraso.

Exemplo:

Condicional atrasado

João da Silva — nº 102

3 peças com o cliente

Atrasado há 2 dias

---

## 19.14 Ação do alerta de Condicional

Ao clicar no alerta de Condicional atrasado, o sistema deve abrir os detalhes do Condicional correspondente.

O usuário deve poder continuar o fluxo normal de retorno ou finalização conforme as regras oficiais.

O alerta não deve finalizar automaticamente o Condicional.

---

## 19.15 Alerta de Conta vencendo hoje

O sistema deve gerar alerta para Conta a Pagar quando:

- existir saldo pendente;
- a data de vencimento for igual à data operacional atual.

O status calculado da conta deve ser compatível com a situação pendente.

Conta integralmente paga não gera alerta.

Conta cancelada não gera alerta.

---

## 19.16 Saldo da conta vencendo hoje

Quando a Conta a Pagar possuir pagamento parcial, o alerta deve apresentar somente o saldo pendente.

Exemplo:

Valor original:
R$ 1.000,00

Valor pago:
R$ 400,00

Saldo pendente:
R$ 600,00

Alerta:

Conta vence hoje

Fornecedor

R$ 600,00 pendentes

Não apresentar R$ 1.000,00 como valor exigível atual.

---

## 19.17 Ação do alerta de Conta vencendo hoje

Ao clicar no alerta, o sistema deve abrir o módulo Contas a Pagar.

A conta correspondente deve ser localizada ou destacada.

A navegação deve utilizar o identificador persistente da conta.

---

## 19.18 Alerta de Conta vencida

O sistema deve gerar alerta quando existir Conta a Pagar com:

- saldo pendente;
- vencimento anterior à data operacional atual.

Conta integralmente paga não gera alerta.

Conta cancelada não gera alerta.

Deve existir um alerta por conta vencida.

---

## 19.19 Informações do alerta de Conta vencida

O alerta deve apresentar, conforme aplicável:

- fornecedor;
- descrição;
- saldo pendente;
- data de vencimento;
- quantidade de dias de atraso.

Exemplo:

Conta vencida

Fornecedor XYZ

Saldo: R$ 1.250,00

Vencida há 8 dias

---

## 19.20 Ação do alerta de Conta vencida

Ao clicar no alerta de Conta vencida, o sistema deve abrir a Conta a Pagar correspondente.

A conta deve ser localizada ou destacada.

O usuário pode executar as ações permitidas pelo módulo Contas a Pagar.

O alerta não deve marcar a conta como paga.

---

## 19.21 Estoque mínimo

Estoque mínimo não gera alerta na Central de Alertas.

O campo estoque mínimo pode existir no cadastro do produto.

O valor pode ser utilizado em:

- consultas;
- filtros;
- análises do módulo Estoque.

A Central de Alertas não deve gerar aviso quando o estoque disponível atingir ou ficar abaixo do estoque mínimo.

---

## 19.22 Última unidade disponível

O sistema deve gerar alerta quando o estoque disponível de um produto for exatamente igual a 1.

O alerta deve utilizar o estoque disponível.

Estoque disponível deve considerar as regras oficiais de reserva e Condicional.

Não utilizar somente o estoque físico bruto quando existirem unidades reservadas ou em Condicional.

---

## 19.23 Informações do alerta de última unidade

O alerta deve apresentar, conforme aplicável:

- produto;
- código;
- marca;
- tamanho;
- cor;
- informação de que existe somente 1 unidade disponível.

Exemplo:

Última unidade disponível

Tênis Nike Air — 42

Apenas 1 unidade disponível

As informações devem utilizar os dados persistidos do produto.

---

## 19.24 Ação do alerta de última unidade

Ao clicar no alerta de última unidade, o sistema deve abrir o produto correspondente no módulo Estoque ou no cadastro operacional compatível.

O produto deve ser localizado utilizando seu identificador persistente.

---

## 19.25 Produto sem estoque

Produto com estoque disponível igual a 0 não gera alerta na Central de Alertas.

A situação Sem estoque deve permanecer visível e tratável no módulo Estoque.

O Catálogo deve seguir suas regras oficiais de disponibilidade.

A Central de Alertas não deve acumular alertas de produtos antigos ou produtos zerados.

---

## 19.26 Estoque negativo

A ausência de alerta para produto sem estoque não autoriza estoque negativo.

O sistema deve continuar impedindo operações que produzam estoque disponível inválido conforme as regras oficiais.

Estoque negativo representa erro de integridade e não um tipo normal de alerta operacional.

---

## 19.27 Estado novo e lido

Os alertas atuais podem possuir estado de leitura por usuário.

Um alerta pode ser apresentado como:

- Novo;
- Lido.

O estado de leitura é visual.

A leitura não altera a situação operacional que originou o alerta.

---

## 19.28 Marcar alerta como lido

Quando o usuário visualizar ou abrir o alerta conforme a regra da interface, o sistema pode registrá-lo como lido para aquele usuário.

O alerta continua na Central enquanto a situação existir.

Exemplo:

Conta continua vencida.

Usuário abriu o alerta.

Resultado:

Alerta:
Lido.

Situação:
Ainda vencida.

O alerta permanece na lista.

---

## 19.29 Leitura individual por usuário

O estado de leitura deve ser individual por usuário.

Exemplo:

Usuário Mauro visualizou o alerta.

Para Mauro:
Lido.

Operador ainda não visualizou.

Para o Operador:
Novo.

Não utilizar estado global de leitura da loja.

---

## 19.30 Identidade lógica do alerta

Para preservar a leitura individual, o sistema deve possuir uma identidade lógica estável para cada situação alertada.

Exemplos conceituais:

- Crediário atrasado + cliente;
- Condicional atrasado + Condicional;
- Conta vencendo hoje + conta;
- Conta vencida + conta;
- Última unidade + produto.

A identidade não deve depender somente do texto visual do alerta.

---

## 19.31 Mudança da situação do alerta

Quando a situação que originou um alerta deixar de existir, o alerta deve sair da lista ativa.

Se uma nova situação equivalente ocorrer futuramente, o sistema deve conseguir tratá-la como uma nova ocorrência quando aplicável.

O sistema não deve reutilizar incorretamente uma leitura antiga para ocultar uma situação nova.

---

## 19.32 Contador do sino

O contador apresentado no sino deve representar a quantidade de alertas novos para o usuário autenticado.

Alertas já lidos não devem aumentar o contador de novos.

Alertas lidos podem continuar visíveis dentro da Central enquanto estiverem ativos.

Quando não existir alerta novo, o sistema pode ocultar o contador numérico.

---

## 19.33 Prioridade crítica

São alertas de prioridade CRÍTICA:

1. Conta vencida;
2. Crediário atrasado;
3. Condicional atrasado.

Os alertas críticos devem ser apresentados antes dos alertas de Atenção.

A prioridade deve ser representada visualmente de forma discreta e clara.

---

## 19.34 Prioridade de atenção

São alertas de prioridade ATENÇÃO:

1. Conta vencendo hoje;
2. Última unidade disponível.

Os alertas de Atenção devem ser apresentados depois dos alertas críticos.

---

## 19.35 Alertas informativos

A Central de Alertas não possui inicialmente um tipo oficial de alerta meramente informativo.

Estoque mínimo não gera alerta.

Novos tipos informativos somente devem ser adicionados após definição de sua finalidade.

---

## 19.36 Ordenação dos alertas críticos

Dentro da mesma categoria crítica, os alertas mais antigos ou mais atrasados devem possuir prioridade visual de ordenação.

Exemplo:

Conta vencida há 20 dias deve aparecer antes de conta vencida há 2 dias dentro do mesmo tipo de alerta.

Crediário com atraso mais antigo deve possuir prioridade dentro dos alertas de Crediário.

Condicional mais atrasado deve possuir prioridade dentro dos alertas de Condicional.

---

## 19.37 Ordenação dos alertas de atenção

Conta vencendo hoje deve ser ordenada de forma consistente.

Quando existirem várias contas vencendo hoje, o sistema pode utilizar como critério complementar:

- saldo pendente;
- fornecedor;
- data de criação

desde que a ordenação seja determinística.

Alertas de última unidade podem ser ordenados por:

- produto;
- código

ou outro critério determinístico definido pela interface.

---

## 19.38 Atualização ao entrar no sistema

Os alertas devem ser carregados ou recalculados ao entrar no sistema após autenticação válida.

O sistema não deve exibir alertas pertencentes a uma sessão anterior.

A troca de usuário deve invalidar os dados de alertas da sessão anterior.

---

## 19.39 Atualização ao abrir a Central

Ao abrir a Central de Alertas, o sistema deve buscar ou recalcular o estado atual dos alertas.

A Central não deve depender exclusivamente de uma lista carregada no início da sessão.

---

## 19.40 Atualização após Crediário

Após pagamento, estorno, devolução ou outra operação que altere o saldo do Crediário, os alertas relacionados devem ser atualizados.

O sistema deve recalcular:

- existência de atraso;
- quantidade de parcelas atrasadas;
- saldo atrasado.

---

## 19.41 Atualização após Condicional

Após retorno parcial ou finalização de Condicional, os alertas relacionados devem ser atualizados.

O sistema deve considerar a quantidade de peças ainda em posse do cliente.

Condicional sem peças pendentes não deve permanecer como alerta atrasado.

---

## 19.42 Atualização após Contas a Pagar

Após:

- pagamento total;
- pagamento parcial;
- estorno;
- cancelamento

de Conta a Pagar, os alertas relacionados devem ser atualizados.

O valor exibido deve utilizar o saldo pendente atual.

---

## 19.43 Atualização após Venda

Após uma Venda, os alertas de última unidade devem ser atualizados.

Se o estoque disponível de um produto passar para 1, o alerta deve aparecer.

Se passar de 1 para 0, o alerta de última unidade deve deixar de existir.

Produto com 0 disponível não gera alerta na Central.

---

## 19.44 Atualização após Devolução

Após uma Devolução que recomponha estoque, os alertas de última unidade devem ser recalculados.

Exemplo:

Produto possuía 1 disponível.

Alerta ativo.

Devolução reintegra 1 unidade.

Disponível passa para 2.

Alerta deixa de existir.

---

## 19.45 Atualização após Troca

Após uma Troca, os alertas de última unidade devem ser recalculados para todos os produtos afetados.

Devem ser considerados:

- produtos entregues e reintegrados;
- produtos entregues e não reintegrados;
- novos produtos baixados.

A atualização deve ocorrer após a confirmação válida da Troca.

---

## 19.46 Atualização após movimentação de estoque

Após movimentação válida de estoque, os alertas de última unidade devem ser atualizados.

A movimentação pode fazer o alerta:

- aparecer;
- permanecer;
- desaparecer.

O cálculo deve utilizar o estoque disponível atual.

---

## 19.47 Virada do dia operacional

Na virada do dia operacional, os alertas dependentes de data devem ser recalculados.

Isso inclui:

- Crediário atrasado;
- Condicional atrasado;
- Conta vencendo hoje;
- Conta vencida.

Exemplo:

Conta vence em 14/07.

Em 14/07:
Conta vencendo hoje.

Em 15/07, se continuar pendente:
Conta vencida.

O alerta deve mudar de situação automaticamente.

---

## 19.48 Foco e visibilidade

Quando a aplicação recuperar foco ou visibilidade após permanecer suspensa, o sistema deve conferir a data operacional e atualizar os alertas quando necessário.

Essa regra deve ser compatível com a estratégia oficial de virada automática do dia já utilizada no sistema.

Não criar múltiplos timers ou listeners duplicados.

---

## 19.49 Botão Atualizar

A Central de Alertas deve possuir um botão discreto ATUALIZAR.

Ao utilizar o botão, o sistema deve buscar ou recalcular os alertas atuais.

O botão não cria alertas manualmente.

O botão não marca todos os alertas como resolvidos.

---

## 19.50 Falha no carregamento

Quando ocorrer erro de rede ou servidor ao carregar os alertas, a interface deve apresentar estado de erro discreto.

O sistema não deve apresentar dados antigos como se fossem alertas atuais sem indicar a falha.

Deve ser possível tentar novamente.

Erro de autenticação deve seguir o fluxo oficial de sessão expirada.

---

## 19.51 Estado vazio

Quando não existirem alertas ativos, a Central deve apresentar estado vazio claro.

Exemplo:

Nenhum alerta no momento.

Não apresentar lista artificial ou alertas zerados.

O contador do sino não deve indicar alertas novos inexistentes.

---

## 19.52 Segurança dos alertas

O backend deve calcular ou validar os alertas utilizando os dados persistidos da loja.

O navegador não deve informar autoritativamente:

- que uma conta está vencida;
- que um Crediário está atrasado;
- que um Condicional está atrasado;
- que existe última unidade.

O frontend é responsável pela apresentação.

A situação operacional deve ser determinada pelo backend.

---

## 19.53 Isolamento por loja

Os alertas pertencem à loja autenticada.

O sistema não deve misturar alertas entre lojas.

O estado de leitura também deve preservar:

- loja;
- usuário;
- identidade lógica do alerta.

---

## 19.54 Histórico e alertas

A Central de Alertas não é um histórico permanente de situações antigas.

Quando uma situação é resolvida, ela deixa a lista ativa.

Os históricos oficiais devem permanecer nos módulos correspondentes.

Exemplos:

- histórico do Crediário;
- histórico do Condicional;
- histórico da Conta a Pagar;
- movimentações de Estoque.

Não utilizar a Central de Alertas como substituta da auditoria.

---

## 19.55 Regras gerais da Central de Alertas

O sistema deve:

- possuir ícone de sino no topo;
- apresentar quantidade de alertas novos;
- permitir acesso ao Administrador;
- permitir acesso ao Operador;
- gerar alerta de Crediário atrasado;
- agrupar Crediário atrasado por cliente;
- gerar alerta de Condicional atrasado;
- gerar um alerta por Condicional atrasado;
- gerar alerta de Conta vencendo hoje;
- gerar alerta de Conta vencida;
- gerar um alerta por conta;
- gerar alerta de última unidade disponível;
- não gerar alerta de estoque mínimo;
- não gerar alerta de produto sem estoque;
- calcular alertas pelo estado atual;
- remover automaticamente alertas resolvidos;
- não exigir ação manual de resolver;
- permitir estado Novo;
- permitir estado Lido;
- preservar leitura individual por usuário;
- não utilizar leitura global da loja;
- manter alertas lidos enquanto a situação existir;
- contar somente alertas novos no sino;
- priorizar Conta vencida;
- priorizar Crediário atrasado;
- priorizar Condicional atrasado;
- apresentar Conta vencendo hoje como Atenção;
- apresentar Última unidade disponível como Atenção;
- ordenar situações críticas pelo atraso;
- atualizar ao entrar no sistema;
- atualizar ao abrir a Central;
- atualizar após Crediário;
- atualizar após Condicional;
- atualizar após Contas a Pagar;
- atualizar após Venda;
- atualizar após Devolução;
- atualizar após Troca;
- atualizar após movimentação de Estoque;
- atualizar na virada do dia operacional;
- conferir alertas ao recuperar foco ou visibilidade;
- possuir botão Atualizar;
- apresentar erro de carregamento;
- permitir nova tentativa;
- apresentar estado vazio claro;
- calcular situações autoritativamente no backend;
- preservar isolamento por loja;
- não substituir históricos ou auditoria pela Central de Alertas.

# 20. SCORE DO CLIENTE

## 20.1 Finalidade do Score do Cliente

O Score do Cliente é um indicador interno de risco de crédito e comportamento de pagamento.

O Score deve auxiliar os usuários na análise do cliente, especialmente antes da utilização do Crediário.

O Score não substitui as regras oficiais de:

- limite de crédito;
- bloqueio do cliente;
- autorização administrativa;
- Crediário;
- venda;
- Condicional.

O Score não deve tomar decisões financeiras automaticamente.

O sistema não deve:

- aumentar limite automaticamente;
- reduzir limite automaticamente;
- bloquear cliente automaticamente;
- desbloquear cliente automaticamente;
- impedir venda automaticamente;
- impedir Condicional automaticamente.

O Score possui finalidade informativa e de apoio à decisão.

---

## 20.2 Escala do Score

O Score utiliza escala de 0 a 100.

O resultado final não pode ser inferior a 0.

O resultado final não pode ser superior a 100.

As classificações oficiais são:

- 90 a 100 — Excelente;
- 75 a 89 — Bom;
- 50 a 74 — Regular;
- 25 a 49 — Atenção;
- 0 a 24 — Alto risco.

O sistema deve utilizar exatamente as faixas oficiais definidas nesta seção.

---

## 20.3 Indicador visual do Score

O Score deve possuir indicador visual circular apresentado junto à classificação.

As cores oficiais são:

- Excelente — verde forte;
- Bom — verde claro;
- Regular — amarelo;
- Atenção — laranja;
- Alto risco — vermelho.

Exemplo conceitual:

● Score 94 — EXCELENTE

● Score 82 — BOM

● Score 68 — REGULAR

● Score 41 — ATENÇÃO

● Score 18 — ALTO RISCO

A cor deve ser complementar.

O sistema deve sempre apresentar também:

- valor numérico;
- classificação textual.

A interpretação do Score não pode depender exclusivamente da cor.

---

## 20.4 Score não editável

O Score é calculado automaticamente pelo sistema.

Administrador não pode informar manualmente o Score.

Operador não pode informar manualmente o Score.

Não permitir campo de edição direta do Score no cadastro do cliente.

Não permitir alteração do Score por requisição do navegador.

O backend é responsável pelo cálculo autoritativo.

---

## 20.5 Período considerado

O Score deve considerar o histórico válido dos últimos 12 meses.

O período deve utilizar a data operacional oficial do sistema.

O fuso operacional é:

America/Sao_Paulo.

O cálculo dos 12 meses deve utilizar as regras oficiais de data e timestamp do sistema.

Parcelas atualmente atrasadas devem permanecer consideradas enquanto possuírem saldo atrasado válido, mesmo quando a venda de origem for anterior ao período normal de 12 meses.

---

## 20.6 Componentes do Score

O Score é composto por dois blocos:

1. Comportamento no Crediário;
2. Histórico de compras pagas diretamente.

O peso máximo de cada bloco é:

Crediário:
80 pontos.

Compras diretas:
20 pontos.

O Crediário possui maior peso porque o Score mede principalmente risco e comportamento de crédito.

---

## 20.7 Peso do Crediário

O componente de Crediário representa até 80 pontos do Score.

O cálculo deve considerar o comportamento válido das parcelas do cliente.

Devem ser considerados:

- parcelas pagas antecipadamente;
- parcelas pagas em dia;
- parcelas pagas com atraso;
- quantidade de dias de atraso;
- parcelas atualmente atrasadas;
- frequência de atrasos;
- pagamentos parciais;
- parcelas quitadas;
- saldo líquido válido das parcelas.

O sistema deve utilizar os registros financeiros persistidos.

Não confiar em valores calculados exclusivamente pelo navegador.

---

## 20.8 Pagamento antecipado

Parcela quitada antes do vencimento representa comportamento correto.

Pagamento antecipado deve possuir o mesmo tratamento positivo de uma parcela paga no vencimento.

O sistema não deve conceder pontuação superior apenas porque o cliente realizou o pagamento muitos dias antes.

Pagamento antecipado:
comportamento correto.

Pagamento no vencimento:
comportamento correto.

Ambos possuem o mesmo peso positivo no componente do Crediário.

---

## 20.9 Pagamento em dia

Parcela integralmente quitada até a data de vencimento deve ser classificada como paga em dia.

A parcela recebe 100% do valor positivo correspondente na avaliação do comportamento do Crediário.

Pagamentos parciais realizados antes do vencimento podem compor a quitação em dia.

O que determina a classificação é a situação líquida da parcela até o vencimento.

---

## 20.10 Atraso leve

Parcela quitada com atraso de 1 a 5 dias deve ser classificada como:

Atraso leve.

A parcela mantém 85% do valor positivo correspondente na avaliação do Crediário.

O atraso deve ser calculado utilizando datas civis e a data operacional oficial.

---

## 20.11 Atraso moderado

Parcela quitada com atraso de 6 a 15 dias deve ser classificada como:

Atraso moderado.

A parcela mantém 60% do valor positivo correspondente na avaliação do Crediário.

---

## 20.12 Atraso grave

Parcela quitada com atraso de 16 a 30 dias deve ser classificada como:

Atraso grave.

A parcela mantém 30% do valor positivo correspondente na avaliação do Crediário.

---

## 20.13 Atraso crítico

Parcela quitada com atraso superior a 30 dias deve ser classificada como:

Atraso crítico.

A parcela recebe 0% do valor positivo correspondente na avaliação do Crediário.

O histórico do atraso deve ser preservado.

A quitação posterior não transforma retroativamente a parcela em pagamento em dia.

---

## 20.14 Faixas de atraso

As faixas oficiais de atraso são:

- 0 dias ou pagamento antecipado — Em dia;
- 1 a 5 dias — Atraso leve;
- 6 a 15 dias — Atraso moderado;
- 16 a 30 dias — Atraso grave;
- acima de 30 dias — Atraso crítico.

As faixas não são configuráveis pelo usuário.

Administrador não pode alterar os intervalos pelas Configurações.

Operador não pode alterar os intervalos.

---

## 20.15 Parcelas atualmente atrasadas

Parcela vencida, com saldo líquido em aberto, deve produzir penalização adicional no Score.

Uma parcela atualmente atrasada deve possuir impacto maior do que uma parcela antiga com atraso equivalente que já foi quitada.

O sistema deve distinguir:

- atraso histórico quitado;
- atraso atual em aberto.

A existência de dívida atualmente vencida representa risco financeiro atual.

---

## 20.16 Penalização por atraso atual

As penalizações-base por parcela atualmente atrasada são:

- 1 a 5 dias — até 5 pontos;
- 6 a 15 dias — até 10 pontos;
- 16 a 30 dias — até 20 pontos;
- acima de 30 dias — até 30 pontos.

A penalização deve considerar o saldo líquido atualmente atrasado.

O sistema não deve tratar automaticamente uma dívida pequena como equivalente a uma dívida significativamente maior quando existirem vários saldos atrasados.

---

## 20.17 Ponderação dos saldos atualmente atrasados

Quando existirem várias parcelas atualmente atrasadas, a penalização deve considerar a participação do saldo de cada parcela no saldo total atrasado do cliente.

Exemplo conceitual:

Saldo atrasado total:
R$ 1.000,00.

Parcela A:
R$ 100,00.

Parcela B:
R$ 900,00.

A Parcela A representa 10% do saldo atrasado.

A Parcela B representa 90% do saldo atrasado.

A distribuição da penalização deve considerar essa proporção.

O cálculo deve utilizar centavos inteiros ou mecanismo equivalente que preserve precisão financeira.

---

## 20.18 Pagamento parcial

Pagamento parcial não representa inadimplência automaticamente.

Quando a parcela ainda não estiver vencida:

- pagamento parcial é neutro em relação ao atraso;
- o saldo restante continua com o vencimento original.

Quando vários pagamentos quitarem integralmente a parcela até o vencimento:

- a parcela deve ser classificada como paga em dia.

Quando a parcela vencer com saldo restante:

- somente o saldo líquido restante deve ser considerado atualmente atrasado.

---

## 20.19 Exemplo de pagamento parcial

Exemplo:

Valor líquido da parcela:
R$ 300,00.

Pagamento antes do vencimento:
R$ 200,00.

Saldo no vencimento:
R$ 100,00.

Após o vencimento, o Score deve considerar como saldo atualmente atrasado:

R$ 100,00.

Os R$ 200,00 já pagos não devem continuar sendo tratados como dívida atrasada.

---

## 20.20 Juros e multas

Juros e multas cobrados não alteram diretamente a classificação do comportamento no Score.

O Score considera:

- vencimento;
- data efetiva dos pagamentos;
- saldo líquido válido;
- quantidade de dias de atraso.

Exemplo:

Cliente atrasou 10 dias.

Sem multa:
atraso de 10 dias.

Com multa:
atraso de 10 dias.

A cobrança ou não de multa não altera o número de dias de atraso.

---

## 20.21 Acréscimos manuais

Acréscimos financeiros manuais não devem ser utilizados para melhorar ou piorar artificialmente o Score.

O sistema deve avaliar o comportamento de pagamento sobre a obrigação financeira válida conforme as regras oficiais do Crediário.

A existência de acréscimo não substitui o histórico das datas.

---

## 20.22 Renegociação

A renegociação não apaga o comportamento anterior do cliente.

O sistema deve preservar o atraso ocorrido antes da renegociação.

Exemplo:

Parcela permaneceu 40 dias atrasada.

Depois foi renegociada.

O histórico deve preservar:

Atraso crítico — 40 dias.

A renegociação não transforma a obrigação anterior em pagamento em dia.

---

## 20.23 Comportamento após renegociação

Após a renegociação, a nova data de vencimento passa a valer para o saldo oficialmente renegociado.

Os pagamentos posteriores devem ser avaliados utilizando as novas condições válidas.

O cliente pode melhorar seu Score com comportamento positivo futuro.

O histórico negativo anterior deixa de participar normalmente quando sair do período de 12 meses, desde que não exista saldo atualmente atrasado vinculado à obrigação.

---

## 20.24 Cancelamento de venda

Venda cancelada não deve produzir efeito negativo ou positivo no Score.

Parcelas canceladas em razão do cancelamento válido da venda devem ser excluídas da base de comportamento de crédito.

Venda cancelada também não conta como compra direta positiva.

O cancelamento deve seguir suas regras oficiais e preservar histórico.

---

## 20.25 Devoluções

Valores oficialmente devolvidos ou abatidos não devem prejudicar o Score.

O sistema deve utilizar o saldo líquido válido após devoluções.

Exemplo:

Parcela original:
R$ 300,00.

Devolução válida abate:
R$ 100,00.

Obrigação líquida:
R$ 200,00.

O Score deve avaliar o comportamento de pagamento sobre os R$ 200,00 válidos.

Não considerar os R$ 100,00 devolvidos como dívida não paga.

---

## 20.26 Devolução total

Quando uma devolução válida eliminar integralmente a obrigação financeira correspondente, o valor eliminado não deve produzir atraso no Score.

O sistema não deve penalizar o cliente por obrigação financeira oficialmente removida.

O histórico da devolução permanece preservado nos módulos correspondentes.

---

## 20.27 Componente de compras diretas

Compras válidas pagas diretamente podem contribuir com até 20 pontos do Score.

São consideradas compras diretas válidas as vendas concluídas sem utilização de Crediário.

Podem ser consideradas formas de pagamento:

- Dinheiro;
- Pix;
- Débito;
- Crédito;
- pagamento misto sem Crediário.

O componente de compras diretas representa relacionamento comercial positivo.

---

## 20.28 Frequência de compras diretas

A pontuação de compras diretas deve utilizar a quantidade de vendas válidas dos últimos 12 meses.

A pontuação oficial é:

- nenhuma venda direta — 0 pontos;
- 1 venda direta — 5 pontos;
- 2 a 3 vendas diretas — 10 pontos;
- 4 a 6 vendas diretas — 15 pontos;
- 7 ou mais vendas diretas — 20 pontos.

O componente não pode ultrapassar 20 pontos.

---

## 20.29 Valor gasto não aumenta a pontuação direta

O valor financeiro da compra direta não deve aumentar a pontuação do componente de compras diretas.

Exemplo:

Cliente A:
1 compra de R$ 5.000,00.

Cliente B:
1 compra de R$ 100,00.

Ambos possuem:

1 venda direta válida.

Ambos recebem a mesma pontuação correspondente à frequência.

O Score não deve classificar poder de compra como menor risco de crédito.

---

## 20.30 Vendas mistas sem Crediário

Venda paga utilizando várias formas diretas continua sendo uma venda direta quando não possuir componente de Crediário.

Exemplo:

Dinheiro + Pix.

Débito + Pix.

Crédito + Dinheiro.

A venda conta uma única vez na frequência de compras diretas.

Não contar uma venda como várias compras porque possui várias formas de pagamento.

---

## 20.31 Venda com Crediário não conta como compra direta

Venda que possuir componente de Crediário não deve ser contabilizada no componente de compras diretas.

Mesmo quando existir entrada em:

- Dinheiro;
- Pix;
- Débito;
- Crédito,

a venda permanece uma venda com utilização de crédito da loja.

O comportamento correspondente deve ser avaliado pelo componente de Crediário.

---

## 20.32 Cliente sem histórico de Crediário

Cliente que nunca utilizou Crediário não deve receber Score numérico de risco de crédito.

O sistema deve apresentar:

Score não disponível.

Ou:

Sem histórico de crédito suficiente.

O sistema não deve iniciar automaticamente o cliente em:

- 0;
- 50;
- 100.

A ausência de histórico de Crediário não significa Alto risco.

---

## 20.33 Compras diretas sem histórico de Crediário

Quando o cliente possuir compras diretas, mas nunca tiver utilizado Crediário, o sistema deve apresentar o histórico positivo separadamente.

Exemplo:

Score de Crédito:
Não disponível.

Histórico de compras:
10 compras diretas nos últimos 12 meses.

O sistema pode classificar visualmente o histórico de compras como positivo.

Não apresentar Score 20 — Alto risco.

---

## 20.34 Ativação do Score numérico

O Score numérico de 0 a 100 somente deve ser apresentado quando existir histórico válido de Crediário para o cliente.

A partir da existência de histórico de Crediário:

- o componente de Crediário pode gerar até 80 pontos;
- o componente de compras diretas pode gerar até 20 pontos.

As compras diretas atuam como componente positivo complementar.

---

## 20.35 Fórmula conceitual

A fórmula conceitual do Score é:

Score =
Componente do Crediário
+
Componente de Compras Diretas
-
Penalização por Parcelas Atualmente Atrasadas.

Onde:

Componente do Crediário:
mínimo 0;
máximo 80.

Componente de Compras Diretas:
mínimo 0;
máximo 20.

O resultado final deve ser limitado ao intervalo de 0 a 100.

---

## 20.36 Limite inferior e superior

Quando o cálculo produzir resultado inferior a 0:

Score final:
0.

Quando o cálculo produzir resultado superior a 100:

Score final:
100.

O sistema não deve apresentar:

Score -5.

O sistema não deve apresentar:

Score 104.

---

## 20.37 Precisão do cálculo

O backend deve executar o cálculo autoritativo do Score.

Valores financeiros utilizados na ponderação devem utilizar centavos inteiros ou mecanismo equivalente que evite diferenças indevidas de ponto flutuante.

A regra de arredondamento do Score final deve ser determinística.

O Score exibido deve ser um número inteiro.

Quando houver resultado decimal intermediário, o sistema deve aplicar arredondamento matemático para o inteiro mais próximo.

---

## 20.38 Atualização após pagamento

Após pagamento de Crediário, o Score deve ser recalculado.

Isso inclui:

- pagamento integral;
- pagamento parcial;
- pagamento antecipado;
- quitação.

O sistema deve utilizar o estado financeiro confirmado após a conclusão válida da operação.

---

## 20.39 Atualização após virada do dia

Na virada do dia operacional, o Score pode mudar sem existir nova movimentação financeira.

Exemplo:

Ontem:
parcela ainda não vencida.

Hoje:
parcela vencida e com saldo.

O Score deve passar a considerar o atraso atual.

A atualização deve seguir a data operacional America/Sao_Paulo.

---

## 20.40 Atualização após renegociação

Após renegociação válida, o Score deve ser recalculado.

O cálculo deve preservar o comportamento anterior e considerar as novas obrigações conforme as regras oficiais.

A renegociação não pode apagar automaticamente penalizações históricas ainda pertencentes ao período considerado.

---

## 20.41 Atualização após devolução

Após Devolução com efeito no Crediário, o Score deve ser recalculado.

O sistema deve utilizar os saldos líquidos resultantes da operação confirmada.

Não recalcular o Score utilizando valores anteriores à Devolução como se ainda fossem exigíveis.

---

## 20.42 Atualização após cancelamento

Após cancelamento válido de venda com efeito no Crediário, o Score deve ser recalculado.

Obrigações canceladas não devem continuar produzindo impacto no Score.

Venda cancelada não deve continuar contribuindo para o componente de compras diretas.

---

## 20.43 Atualização após nova venda

Após nova venda válida vinculada ao cliente, o Score ou o histórico de compras deve ser atualizado.

Venda direta válida pode alterar o componente de compras diretas.

Nova venda com Crediário pode ativar o Score numérico para cliente que anteriormente não possuía histórico de crédito.

---

## 20.44 Exibição na ficha do cliente

A ficha do cliente deve apresentar o Score quando existir histórico válido de Crediário.

Exemplo:

● Score 82 — BOM

Abaixo do Score, o sistema deve apresentar resumo explicativo.

Exemplo:

8 parcelas quitadas em dia.

1 atraso leve.

Nenhuma parcela atualmente atrasada.

O resumo deve utilizar dados reais do período considerado.

---

## 20.45 Exibição de situação de atenção

Quando o cliente possuir Score de Atenção ou Alto risco, a ficha deve apresentar a situação de forma clara.

Exemplo:

● Score 41 — ATENÇÃO

2 parcelas atualmente atrasadas.

O sistema não deve utilizar mensagens ofensivas ou classificações não definidas nesta seção.

---

## 20.46 Exibição durante a venda

Ao selecionar cliente em uma venda, o sistema pode apresentar o Score do cliente.

Exemplo:

Cliente:
João da Silva.

● Score 41 — ATENÇÃO.

O indicador deve possuir finalidade informativa.

A exibição não substitui a validação de:

- cliente bloqueado;
- limite de crédito;
- saldo utilizado;
- regras do Crediário.

---

## 20.47 Cliente sem Score durante a venda

Quando o cliente nunca tiver utilizado Crediário, a seleção deve apresentar informação compatível.

Exemplo:

Score de Crédito:
Sem histórico.

Quando existirem compras diretas, o sistema pode apresentar:

7 compras diretas nos últimos 12 meses.

Não classificar automaticamente o cliente como Alto risco.

---

## 20.48 Score e limite de crédito

O Score não altera automaticamente o limite de crédito do cliente.

Exemplo:

Score 95:
não aumenta limite automaticamente.

Score 15:
não reduz limite automaticamente.

Alterações do limite devem seguir as regras oficiais do cadastro do cliente e permissões dos usuários.

---

## 20.49 Score e bloqueio do cliente

O Score não bloqueia automaticamente o cliente.

Cliente com Score Alto risco pode permanecer ativo e não bloqueado.

Cliente bloqueado deve seguir a regra oficial de bloqueio independentemente do Score.

Score e bloqueio são informações distintas.

---

## 20.50 Score e autorização

O Score pode auxiliar a decisão do usuário, mas não substitui autorizações exigidas por outras regras.

Excesso de limite, quando possuir fluxo de autorização específico, deve seguir sua própria regra.

O sistema não deve considerar Score alto como autorização automática para ultrapassar limite.

---

## 20.51 Histórico explicativo

O Score deve ser explicável.

O sistema deve conseguir apresentar os principais fatores utilizados no resultado.

Exemplos:

- parcelas pagas em dia;
- atrasos leves;
- atrasos moderados;
- atrasos graves;
- atrasos críticos;
- parcelas atualmente atrasadas;
- saldo atualmente atrasado;
- compras diretas válidas.

Não é necessário apresentar ao usuário toda a fórmula matemática interna em cada tela.

O resultado não deve ser uma nota sem justificativa operacional.

---

## 20.52 Dados históricos

O cálculo deve utilizar os registros históricos persistidos.

Alterações atuais no cadastro do cliente não devem reescrever comportamento financeiro antigo.

Alteração de:

- telefone;
- endereço;
- e-mail;
- limite atual

não modifica o histórico de pagamentos.

---

## 20.53 Registros antigos sem informação suficiente

Quando registros antigos não possuírem informação confiável para determinar:

- vencimento;
- data de pagamento;
- saldo líquido;
- vínculo da parcela,

o sistema não deve inventar comportamento positivo ou negativo.

O registro inseguro deve ficar fora do cálculo específico que depender da informação ausente.

O sistema deve preservar o dado histórico.

---

## 20.54 Segurança do cálculo

O navegador não deve informar o Score final ao backend.

O navegador não deve informar a classificação do cliente como valor autoritativo.

O backend deve calcular:

- Score;
- classificação;
- componentes;
- penalizações;
- resumo.

O frontend é responsável pela apresentação visual.

---

## 20.55 Isolamento por loja

O Score deve utilizar somente o histórico do cliente dentro da loja correspondente.

Não misturar:

- vendas;
- parcelas;
- pagamentos;
- devoluções

de lojas diferentes.

Todo cálculo deve respeitar o contexto persistente da loja.

---

## 20.56 Regras gerais do Score do Cliente

O sistema deve:

- utilizar Score de 0 a 100;
- classificar Excelente de 90 a 100;
- classificar Bom de 75 a 89;
- classificar Regular de 50 a 74;
- classificar Atenção de 25 a 49;
- classificar Alto risco de 0 a 24;
- utilizar verde forte para Excelente;
- utilizar verde claro para Bom;
- utilizar amarelo para Regular;
- utilizar laranja para Atenção;
- utilizar vermelho para Alto risco;
- sempre apresentar classificação textual junto à cor;
- considerar os últimos 12 meses;
- manter parcelas atualmente atrasadas no cálculo enquanto possuírem saldo válido;
- atribuir até 80 pontos ao comportamento no Crediário;
- atribuir até 20 pontos às compras diretas;
- dar maior peso ao Crediário;
- tratar pagamento antecipado como comportamento correto;
- tratar pagamento no vencimento como comportamento correto;
- classificar atraso de 1 a 5 dias como leve;
- classificar atraso de 6 a 15 dias como moderado;
- classificar atraso de 16 a 30 dias como grave;
- classificar atraso acima de 30 dias como crítico;
- penalizar adicionalmente parcelas atualmente atrasadas;
- considerar o saldo líquido atualmente atrasado;
- tratar pagamentos parciais conforme o saldo restante;
- não utilizar juros ou multas como fator direto do Score;
- preservar atrasos anteriores à renegociação;
- utilizar novas datas após renegociação válida;
- não penalizar valores cancelados;
- não penalizar valores devolvidos;
- utilizar saldo líquido após abatimentos;
- considerar frequência de compras diretas;
- não utilizar valor gasto como fator positivo;
- contar cada venda direta válida uma única vez;
- não contar venda com Crediário como compra direta;
- não apresentar Score numérico para cliente sem histórico de Crediário;
- apresentar histórico de compras diretas separadamente quando não existir Score;
- ativar Score numérico após existir histórico válido de Crediário;
- limitar o resultado mínimo a 0;
- limitar o resultado máximo a 100;
- apresentar Score inteiro;
- calcular o Score no backend;
- impedir edição manual;
- recalcular após pagamento;
- recalcular após pagamento parcial;
- recalcular após quitação;
- recalcular na virada do dia;
- recalcular após renegociação;
- recalcular após Devolução;
- recalcular após cancelamento;
- recalcular após nova venda;
- apresentar Score na ficha do cliente;
- apresentar resumo explicativo;
- permitir exibição durante a venda;
- não alterar limite automaticamente;
- não bloquear cliente automaticamente;
- não autorizar excesso de limite automaticamente;
- preservar histórico financeiro;
- não inventar comportamento para registros antigos inseguros;
- respeitar isolamento por loja.


# 21. FORNECEDORES E CADASTROS AUXILIARES

## 21.1 Finalidade

O sistema deve possuir cadastros auxiliares para padronizar informações utilizadas nos módulos operacionais.

Os cadastros auxiliares incluem:

- Fornecedores;
- Marcas;
- Categorias de Produtos;
- Gêneros;
- Tamanhos;
- Cores;
- Categorias de Despesas.

O objetivo é evitar duplicidades, variações desnecessárias de escrita e perda de vínculo histórico.

Os cadastros auxiliares não devem ser excluídos permanentemente pelo fluxo normal quando possuírem uso histórico.

---

## 21.2 Cadastro de Fornecedor

O sistema deve permitir o cadastro de fornecedores.

O cadastro possui:

- Nome ou Razão Social;
- Nome Fantasia;
- CPF ou CNPJ;
- Telefone;
- WhatsApp;
- E-mail;
- CEP;
- Endereço;
- Número;
- Bairro;
- Cidade;
- Estado;
- Observações.

O campo Nome ou Razão Social é obrigatório.

Os demais campos são opcionais, salvo quando outra regra de negócio exigir informação específica.

O backend deve validar os campos obrigatórios.

---

## 21.3 Nome ou Razão Social do Fornecedor

O Nome ou Razão Social é obrigatório.

Não permitir cadastro com valor:

- vazio;
- composto somente por espaços.

O nome deve ser utilizado para identificação e busca do fornecedor.

---

## 21.4 CPF e CNPJ do Fornecedor

CPF ou CNPJ é opcional.

Quando informado, o documento deve ser validado matematicamente.

O sistema deve reconhecer se o valor informado corresponde a:

- CPF;
- CNPJ.

Não aceitar documento matematicamente inválido.

A validação autoritativa deve ocorrer no backend.

---

## 21.5 Unicidade de CPF ou CNPJ do Fornecedor

CPF ou CNPJ informado deve ser único entre fornecedores.

Não permitir dois fornecedores com o mesmo documento válido.

A comparação deve considerar o documento normalizado, ignorando formatação visual.

Exemplo:

12.345.678/0001-90

e

12345678000190

representam o mesmo documento.

Fornecedor desativado continua sendo considerado na regra de unicidade.

Documento em branco é permitido e não gera duplicidade entre fornecedores sem documento.

---

## 21.6 Documento duplicado de Fornecedor

Quando o CPF ou CNPJ já estiver vinculado a outro fornecedor, o cadastro deve ser recusado.

O sistema deve informar que o documento já está cadastrado.

Quando possível, deve permitir localizar ou abrir o fornecedor existente.

Não criar automaticamente um segundo fornecedor com o mesmo documento.

---

## 21.7 Situação do Fornecedor

O fornecedor pode estar:

- Ativo;
- Desativado.

Fornecedor Ativo pode ser utilizado em novas operações.

Fornecedor Desativado permanece no histórico, mas não deve ser utilizado em novas operações que exigem fornecedor ativo.

---

## 21.8 Desativação de Fornecedor

Fornecedor não deve ser excluído permanentemente pelo fluxo normal.

Administrador e Operador podem desativar fornecedor.

Ao desativar:

- preservar o cadastro;
- preservar Contas a Pagar vinculadas;
- preservar histórico;
- impedir seleção em novas contas.

Fornecedor desativado pode ser reativado.

A reativação não altera registros históricos anteriores.

---

## 21.9 Fornecedor nas Contas a Pagar

Novas Contas a Pagar devem utilizar fornecedor cadastrado.

O fornecedor deve ser selecionado utilizando seu identificador persistente.

Não utilizar texto livre como vínculo autoritativo do fornecedor em novas contas.

A interface deve permitir busca entre fornecedores ativos.

---

## 21.10 Novo Fornecedor dentro de Contas a Pagar

A tela de cadastro de Conta a Pagar deve permitir acesso rápido à ação:

NOVO FORNECEDOR.

O usuário pode cadastrar um fornecedor sem precisar abandonar o fluxo da Conta a Pagar.

Após cadastro válido, o novo fornecedor pode ser selecionado na conta em montagem.

A criação do fornecedor não deve confirmar automaticamente a Conta a Pagar.

---

## 21.11 Histórico do Fornecedor

Alterações futuras no cadastro do fornecedor não devem apagar ou transferir Contas a Pagar históricas.

O identificador persistente do fornecedor deve ser preservado.

Quando existir snapshot histórico necessário para apresentação de uma operação antiga, o sistema deve utilizar a informação preservada correspondente.

---

## 21.12 Cadastro de Marcas

O sistema deve possuir cadastro de Marcas.

O cadastro de Marca possui:

- Nome da Marca.

O nome é obrigatório.

Não permitir marca com nome vazio ou composto somente por espaços.

---

## 21.13 Unicidade da Marca

O nome da Marca deve ser único.

A comparação deve ignorar:

- diferenças entre letras maiúsculas e minúsculas;
- espaços extras no início ou no final;
- espaços internos duplicados quando utilizados apenas como variação de digitação.

Exemplo:

Nike

NIKE

` Nike `

não devem gerar três marcas diferentes.

---

## 21.14 Situação da Marca

A Marca pode estar:

- Ativa;
- Desativada.

Marca Ativa pode ser utilizada em novos cadastros e edições de produtos.

Marca Desativada não deve aparecer para novas seleções normais.

O histórico existente permanece preservado.

---

## 21.15 Desativação de Marca

Marca não deve ser excluída permanentemente pelo fluxo normal.

Administrador e Operador podem desativar Marca.

A desativação:

- não altera produtos históricos;
- não altera vendas;
- não altera snapshots de marca preservados em vendas;
- não altera relatórios históricos.

Marca desativada pode ser reativada.

---

## 21.16 Marca no cadastro do Produto

O cadastro de Produto deve permitir:

- selecionar Marca existente;
- criar nova Marca rapidamente.

Quando a Marca desejada não existir, a interface deve disponibilizar ação equivalente a:

+ NOVA MARCA.

Após cadastro válido, a nova Marca deve ficar disponível e pode ser selecionada no Produto em montagem.

A criação da Marca não deve salvar automaticamente o Produto.

---

## 21.17 Cadastro de Categorias de Produtos

O sistema deve possuir cadastro de Categorias de Produtos.

O cadastro possui:

- Nome da Categoria.

O nome é obrigatório.

Exemplos:

- Camisetas;
- Calções;
- Tênis;
- Chuteiras;
- Acessórios.

---

## 21.18 Unicidade da Categoria de Produto

O nome da Categoria de Produto deve ser único.

A comparação deve ignorar diferenças de:

- letras maiúsculas e minúsculas;
- espaços extras;
- variações puramente de formatação.

Não permitir categorias duplicadas por diferença de digitação.

---

## 21.19 Situação da Categoria de Produto

A Categoria de Produto pode estar:

- Ativa;
- Desativada.

Categoria Ativa pode ser utilizada em novos Produtos.

Categoria Desativada permanece no histórico e não deve aparecer para novas seleções normais.

---

## 21.20 Desativação de Categoria de Produto

Categoria de Produto não deve ser excluída permanentemente pelo fluxo normal.

Administrador e Operador podem desativar Categoria.

A desativação não modifica:

- produtos históricos;
- vendas;
- relatórios históricos.

A Categoria pode ser reativada.

---

## 21.21 Nova Categoria no cadastro do Produto

A tela de Produto deve permitir selecionar Categoria existente ou criar nova Categoria rapidamente.

Quando necessário, disponibilizar ação equivalente a:

+ NOVA CATEGORIA.

Após cadastro válido, a Categoria deve ficar disponível para seleção.

A criação da Categoria não deve salvar automaticamente o Produto.

---

## 21.22 Gênero

O campo Gênero deve utilizar uma lista controlada.

Os valores iniciais são:

- Masculino;
- Feminino;
- Unissex;
- Infantil.

O sistema deve evitar texto livre com variações como:

- masc;
- MASCULINO;
- masculino;
- Masc.

A utilização de valores controlados melhora filtros e relatórios.

---

## 21.23 Evolução dos Gêneros

Novos valores de Gênero não devem ser criados livremente sem definição específica.

A lista inicial deve ser utilizada como referência oficial.

Quando houver necessidade comercial real de novo Gênero, a regra pode ser revisada.

Gênero não deve ser utilizado como substituto de Categoria.

---

## 21.24 Cadastro de Tamanhos

O sistema deve possuir cadastro simples de Tamanhos.

Exemplos:

- P;
- M;
- G;
- GG;
- 38;
- 39;
- 40;
- Único.

O tamanho deve ser selecionado entre valores cadastrados.

O objetivo é evitar variações desnecessárias de escrita.

---

## 21.25 Criação de Tamanho

Administrador e Operador podem criar novos Tamanhos.

A tela de Produto deve permitir criação rápida quando o Tamanho desejado não existir.

Após cadastro válido, o novo Tamanho pode ser selecionado no Produto.

A criação do Tamanho não deve salvar automaticamente o Produto.

---

## 21.26 Unicidade do Tamanho

O sistema deve impedir Tamanhos duplicados por diferença puramente de formatação.

Exemplo:

GG

` GG `

não devem representar dois Tamanhos diferentes.

A comparação deve utilizar valor normalizado.

Quando diferenças de letras maiúsculas e minúsculas não possuírem significado comercial, devem ser tratadas como o mesmo valor.

---

## 21.27 Situação do Tamanho

O Tamanho pode estar:

- Ativo;
- Desativado.

Tamanho Desativado não deve aparecer para novas seleções normais.

O histórico de produtos existentes permanece preservado.

Tamanho desativado pode ser reativado.

---

## 21.28 Cadastro de Cores

O sistema deve possuir cadastro simples de Cores.

Exemplos:

- Preto;
- Branco;
- Azul;
- Bordô;
- Vermelho.

A Cor deve ser selecionada entre valores cadastrados.

O objetivo é evitar variações como:

- Preto;
- preto;
- PRETO.

---

## 21.29 Criação de Cor

Administrador e Operador podem criar novas Cores.

A tela de Produto deve permitir criação rápida quando a Cor desejada não existir.

Após cadastro válido, a nova Cor pode ser selecionada no Produto.

A criação da Cor não deve salvar automaticamente o Produto.

---

## 21.30 Unicidade da Cor

O nome da Cor deve ser único após normalização.

A comparação deve ignorar:

- diferenças entre letras maiúsculas e minúsculas;
- espaços extras;
- variações puramente de formatação.

Não criar múltiplas Cores para o mesmo nome comercial.

---

## 21.31 Situação da Cor

A Cor pode estar:

- Ativa;
- Desativada.

Cor Desativada não aparece para novas seleções normais.

Produtos e vendas históricas permanecem preservados.

Cor desativada pode ser reativada.

---

## 21.32 Categorias de Despesas

O sistema deve possuir um único cadastro de Categorias de Despesas.

O cadastro deve ser utilizado por:

- Caixa;
- Contas a Pagar.

Não manter cadastros separados e divergentes de categorias de despesas para cada módulo.

---

## 21.33 Categorias de Despesas iniciais

O sistema deve possuir inicialmente categorias compatíveis com a operação da loja.

Entre elas:

- Mercadorias;
- Aluguel;
- Energia;
- Água;
- Internet;
- Impostos;
- Salários;
- Serviços;
- Gasolina;
- Lanches;
- Estacionamento;
- Material de limpeza;
- Motoboy;
- Acessórios;
- Outros.

As categorias iniciais não impedem a criação de novas Categorias de Despesas.

---

## 21.34 Criação de Categoria de Despesa

Administrador e Operador podem criar novas Categorias de Despesas.

A criação deve permitir atender necessidades reais da operação.

O nome é obrigatório.

Não permitir categoria vazia.

A nova Categoria pode ser utilizada em novas movimentações compatíveis.

---

## 21.35 Unicidade da Categoria de Despesa

O nome da Categoria de Despesa deve ser único após normalização.

A comparação deve ignorar:

- letras maiúsculas e minúsculas;
- espaços extras;
- variações puramente de formatação.

Exemplo:

Motoboy

MOTOBOY

` Motoboy `

representam a mesma categoria.

---

## 21.36 Desativação de Categoria de Despesa

Categoria de Despesa não deve ser excluída permanentemente quando possuir uso histórico.

Administrador e Operador podem desativar Categoria de Despesa.

Categoria desativada:

- não aparece para novas movimentações;
- não aparece para novas Contas a Pagar;
- permanece nas operações históricas.

A Categoria pode ser reativada.

---

## 21.37 Categorias históricas

Alterar ou desativar uma Categoria de Despesa não deve apagar o vínculo com movimentações históricas.

Movimentações antigas devem continuar identificáveis.

O sistema não deve substituir automaticamente a categoria histórica por outra categoria atual.

---

## 21.38 Permissões dos Cadastros Auxiliares

Administrador e Operador podem operar os Cadastros Auxiliares.

Ambos podem, conforme o cadastro:

- criar;
- editar;
- desativar;
- reativar.

Essa regra se aplica a:

- Fornecedores;
- Marcas;
- Categorias de Produtos;
- Tamanhos;
- Cores;
- Categorias de Despesas.

Não existe restrição exclusiva de Administrador para esses cadastros.

---

## 21.39 Validação no backend

As validações dos Cadastros Auxiliares devem existir no backend.

Não confiar somente na interface para:

- obrigatoriedade;
- unicidade;
- validação de CPF;
- validação de CNPJ;
- situação ativa ou desativada.

O navegador não deve criar vínculo autoritativo utilizando apenas o texto visual quando existir identificador persistente.

---

## 21.40 Identificadores persistentes

Os cadastros auxiliares devem possuir identificadores persistentes.

Operações devem preservar o vínculo pelo identificador quando aplicável.

Não utilizar somente o nome como vínculo histórico autoritativo.

Essa regra é especialmente importante para:

- Fornecedor;
- Marca;
- Categoria de Produto;
- Categoria de Despesa.

---

## 21.41 Alteração de nome de cadastro auxiliar

Alterar o nome atual de um cadastro auxiliar não deve transferir registros para outra entidade.

Exemplo:

Marca com identificador A:
Adidas

Nome corrigido:
ADIDAS ORIGINAL

Os produtos vinculados ao identificador A continuam vinculados à mesma Marca.

Não criar uma nova entidade silenciosamente apenas por alteração do nome.

---

## 21.42 Rastreabilidade das alterações

Não é necessário criar uma tela de auditoria específica para cada Cadastro Auxiliar.

Quando a estrutura geral de auditoria já suportar a operação, o sistema deve preservar o usuário responsável pelas alterações relevantes.

Exemplo:

Marca alterada por Mauro.

Fornecedor desativado por João.

A finalidade é rastreabilidade operacional.

Não criar módulo de produtividade ou monitoramento de usuários.

---

## 21.43 Dados históricos de Vendas

Marcas, Categorias, Tamanhos e Cores atuais não devem reescrever snapshots históricos das vendas.

Quando a Venda possuir atributo histórico preservado, o sistema deve utilizar esse valor para relatórios e históricos da operação.

Exemplo:

Marca na data da venda:
Marca A.

Marca atual do Produto:
Marca B.

A Venda histórica continua utilizando:
Marca A.

---

## 21.44 Dados históricos de Produtos

A edição de Cadastro Auxiliar pode alterar a classificação atual do Produto quando o usuário efetivamente editar o vínculo do Produto.

Essa alteração vale para operações futuras.

Não alterar retroativamente:

- itens de vendas antigas;
- devoluções históricas;
- Trocas históricas;
- relatórios históricos baseados em snapshots.

---

## 21.45 Desativação não é exclusão

A desativação deve ser o mecanismo padrão para retirar um Cadastro Auxiliar das novas operações.

A desativação:

- preserva o registro;
- preserva vínculos;
- preserva histórico;
- impede seleção normal em novos cadastros ou operações.

A reativação deve ser permitida.

---

## 21.46 Regras gerais de Fornecedores e Cadastros Auxiliares

O sistema deve:

- exigir Nome ou Razão Social do Fornecedor;
- permitir CPF ou CNPJ opcional;
- validar CPF quando informado;
- validar CNPJ quando informado;
- impedir documento duplicado entre fornecedores;
- permitir fornecedor sem documento;
- desativar fornecedor em vez de excluir;
- preservar Contas a Pagar históricas;
- exigir fornecedor cadastrado em novas Contas a Pagar;
- permitir Novo Fornecedor dentro do fluxo de Conta a Pagar;
- possuir cadastro de Marcas;
- exigir nome da Marca;
- impedir Marca duplicada após normalização;
- desativar Marca em vez de excluir;
- permitir Nova Marca na tela de Produto;
- possuir cadastro de Categorias de Produtos;
- impedir Categoria duplicada após normalização;
- desativar Categoria em vez de excluir;
- permitir Nova Categoria na tela de Produto;
- utilizar lista controlada de Gêneros;
- utilizar inicialmente Masculino, Feminino, Unissex e Infantil;
- possuir cadastro de Tamanhos;
- permitir criação de novos Tamanhos;
- impedir Tamanho duplicado por formatação;
- permitir desativação e reativação de Tamanho;
- possuir cadastro de Cores;
- permitir criação de novas Cores;
- impedir Cor duplicada após normalização;
- permitir desativação e reativação de Cor;
- possuir um único cadastro de Categorias de Despesas;
- utilizar Categorias de Despesas no Caixa e Contas a Pagar;
- iniciar com categorias de despesas operacionais padrão;
- permitir criação de novas Categorias de Despesas;
- impedir duplicidade de Categoria de Despesa após normalização;
- desativar Categoria de Despesa em vez de excluir;
- preservar categorias históricas;
- permitir Administração e Operação dos cadastros por Administrador e Operador;
- validar regras no backend;
- utilizar identificadores persistentes;
- preservar histórico após alteração de nomes;
- não reescrever snapshots históricos de Vendas;
- preservar rastreabilidade operacional quando a auditoria geral suportar a ação;
- utilizar desativação como mecanismo padrão em vez de exclusão.

## 21.47 Tela de Fornecedores

O sistema deve possuir tela própria de Fornecedores.

Administrador e Operador podem acessar a tela.

A tela deve permitir:

- visualizar indicadores;
- realizar busca;
- aplicar filtros;
- consultar a listagem;
- abrir a ficha detalhada do Fornecedor.

A autorização deve seguir as regras oficiais de Usuários e Permissões.

---

## 21.48 Indicadores da tela de Fornecedores

A tela de Fornecedores deve apresentar os seguintes cards:

- Fornecedores Ativos;
- Contas em Aberto;
- Contas Vencidas;
- Crédito Disponível.

Fornecedores Ativos representa quantidade de Fornecedores atualmente ativos.

Os demais cards representam valores financeiros totais da loja.

---

## 21.49 Card Contas em Aberto

O card Contas em Aberto deve apresentar o saldo pendente total das Contas a Pagar válidas e não canceladas vinculadas a Fornecedores.

O cálculo deve utilizar os saldos líquidos atuais.

Devem ser considerados, conforme as regras oficiais de Contas a Pagar:

- pagamentos;
- pagamentos parciais;
- descontos;
- juros;
- multas;
- estornos;
- abatimentos por Devolução ao Fornecedor;
- Créditos com Fornecedor utilizados.

Não utilizar somente o valor original das Contas.

---

## 21.50 Card Contas Vencidas

O card Contas Vencidas deve apresentar o saldo pendente total das Contas a Pagar vencidas.

A Conta deve possuir:

- saldo pendente maior que zero;
- vencimento anterior à data operacional atual;
- situação válida e não cancelada.

A data operacional deve utilizar America/Sao_Paulo.

---

## 21.51 Card Crédito Disponível

O card Crédito Disponível deve apresentar a soma dos saldos disponíveis dos Créditos com Fornecedores válidos da loja.

O cálculo deve considerar:

- Créditos criados;
- utilizações;
- estornos;
- reversões formais.

Crédito Utilizado ou Revertido sem saldo disponível não compõe o valor atual.

---

## 21.52 Busca de Fornecedores

A tela deve permitir busca por:

- Nome ou Razão Social;
- Nome Fantasia;
- CPF;
- CNPJ;
- Telefone.

A busca deve utilizar normalização quando aplicável.

CPF e CNPJ devem ser comparados utilizando o documento normalizado.

Telefone pode utilizar representação normalizada para busca.

---

## 21.53 Filtros de Fornecedores

A tela deve permitir filtros por:

- situação;
- possui Contas em Aberto;
- possui Contas Vencidas;
- possui Crédito Disponível.

Situações:

- Ativo;
- Desativado.

Os filtros podem ser utilizados em conjunto com a busca.

---

## 21.54 Filtro Possui Contas em Aberto

O filtro Possui Contas em Aberto deve utilizar o saldo líquido atual das Contas do Fornecedor.

O Fornecedor deve ser apresentado quando o saldo pendente total válido for maior que zero.

Não utilizar somente a existência de uma Conta com status textual Pendente.

---

## 21.55 Filtro Possui Contas Vencidas

O filtro Possui Contas Vencidas deve apresentar Fornecedores que possuam pelo menos uma Conta válida:

- com saldo pendente;
- vencida em relação à data operacional atual.

Conta paga integralmente não torna o Fornecedor elegível para o filtro.

Conta cancelada não deve ser considerada.

---

## 21.56 Filtro Possui Crédito Disponível

O filtro Possui Crédito Disponível deve utilizar o saldo atual de Crédito do Fornecedor.

O Fornecedor deve ser apresentado quando:

Crédito disponível > 0.

Não utilizar somente a existência histórica de Crédito já integralmente utilizado.

---

## 21.57 Listagem de Fornecedores

A listagem deve apresentar:

- Fornecedor;
- CPF ou CNPJ;
- Telefone;
- Contas em Aberto;
- Contas Vencidas;
- Crédito Disponível;
- Situação;
- Ação.

A ação principal deve ser:

VER DETALHES.

---

## 21.58 Valores da listagem

Os valores financeiros apresentados na listagem devem utilizar os saldos atuais oficiais.

Contas em Aberto:
saldo pendente total válido.

Contas Vencidas:
saldo pendente vencido.

Crédito Disponível:
saldo de Crédito válido e ainda utilizável.

O backend deve calcular os valores autoritativos.

---

## 21.59 Ficha do Fornecedor

A ficha do Fornecedor deve centralizar informações cadastrais, operacionais e financeiras vinculadas ao Fornecedor.

A ficha deve permitir consultar:

- resumo;
- dados cadastrais;
- Entradas;
- Contas a Pagar;
- Devoluções ao Fornecedor;
- Créditos;
- utilizações de Crédito;
- Garantias.

A ficha não deve reescrever os módulos de origem.

As informações devem permanecer vinculadas às entidades oficiais correspondentes.

---

## 21.60 Resumo da ficha do Fornecedor

O topo da ficha deve apresentar:

- Nome ou Razão Social;
- Nome Fantasia;
- Situação;
- Crédito Disponível;
- Total em Aberto;
- Total Vencido.

Os valores devem utilizar o estado financeiro atual.

---

## 21.61 Dados cadastrais na ficha

A ficha deve apresentar, conforme cadastrados:

- CPF ou CNPJ;
- Telefone;
- WhatsApp;
- E-mail;
- CEP;
- Endereço;
- Número;
- Bairro;
- Cidade;
- Estado;
- Observações.

Campos sem informação não devem produzir apresentação visual desnecessária.

---

## 21.62 Entradas do Fornecedor

A ficha deve possuir seção:

ENTRADAS.

A seção deve apresentar as Entradas vinculadas ao Fornecedor histórico correspondente.

Para cada Entrada, apresentar:

- número;
- data;
- quantidade total de peças;
- custo total;
- Contas a Pagar vinculadas;
- saldo pendente;
- situação da Entrada.

Deve ser possível abrir os detalhes da Entrada.

---

## 21.63 Fornecedor histórico das Entradas

A seção Entradas deve utilizar o Fornecedor preservado na própria Entrada.

Alterar o Fornecedor atual de um Produto não deve transferir Entradas antigas para outro Fornecedor.

A ficha deve respeitar o vínculo histórico persistido.

---

## 21.64 Saldo pendente das Entradas

O saldo pendente apresentado na Entrada deve utilizar as Contas a Pagar válidas vinculadas àquela Entrada.

O cálculo deve considerar o saldo líquido atual.

Entrada sem Conta a Pagar deve ser identificada conforme sua regra oficial.

---

## 21.65 Contas a Pagar do Fornecedor

A ficha deve possuir seção:

CONTAS A PAGAR.

A seção deve apresentar todas as Contas vinculadas ao Fornecedor.

Para cada Conta, apresentar:

- descrição;
- origem;
- data de emissão;
- vencimento;
- valor;
- total pago;
- saldo pendente;
- status.

Deve ser possível abrir os detalhes da Conta.

---

## 21.66 Origem da Conta a Pagar

A origem da Conta deve ser identificada quando conhecida.

Exemplos:

- Entrada nº 125;
- Cadastro manual;
- outra origem oficial futura.

O vínculo deve utilizar o identificador persistente da entidade de origem.

A descrição textual não substitui o vínculo.

---

## 21.67 Total pago da Conta

O Total pago deve utilizar os pagamentos financeiros válidos da Conta.

O sistema deve distinguir:

- pagamentos;
- abatimentos por Devolução ao Fornecedor;
- Crédito do Fornecedor utilizado;
- descontos;
- estornos.

A apresentação pode resumir o saldo, mas os detalhes devem preservar cada origem.

---

## 21.68 Devoluções ao Fornecedor

A ficha deve possuir seção:

DEVOLUÇÕES.

A seção deve apresentar as Devoluções ao Fornecedor vinculadas.

Para cada Devolução, apresentar:

- número;
- data;
- Entrada de origem;
- quantidade total de peças;
- valor histórico;
- total conciliado;
- saldo pendente de acerto;
- situação operacional;
- situação financeira.

Deve ser possível abrir os detalhes.

---

## 21.69 Devoluções pendentes de acerto

Devolução com valor pendente de acerto deve possuir destaque visual na ficha do Fornecedor.

O valor apresentado deve utilizar:

Valor histórico - Total conciliado válido.

A ficha não substitui o alerta oficial de Acerto financeiro pendente.

---

## 21.70 Créditos do Fornecedor

A ficha deve possuir seção:

CRÉDITOS.

O Crédito total disponível deve ser apresentado em destaque.

Abaixo, listar cada Crédito individualmente.

---

## 21.71 Dados de cada Crédito

Para cada Crédito, apresentar:

- Devolução ao Fornecedor de origem;
- data;
- valor original;
- valor utilizado líquido;
- saldo disponível;
- situação.

Situações:

- Disponível;
- Parcialmente utilizado;
- Utilizado;
- Revertido.

---

## 21.72 Utilizações de Crédito

A ficha deve possuir área ou visão de utilizações de Crédito.

Para cada utilização, apresentar:

- Conta a Pagar;
- data e hora;
- valor utilizado;
- usuário responsável.

Os detalhes devem permitir visualizar as alocações entre os Créditos originais quando uma utilização consumir mais de um Crédito.

---

## 21.73 Origem e destino do Crédito

A ficha deve permitir rastrear:

Devolução ao Fornecedor
→ Crédito
→ Utilização
→ Conta a Pagar.

O sistema não deve perder o vínculo entre origem e destino do Crédito.

---

## 21.74 Garantias vinculadas ao Fornecedor

A ficha deve possuir seção:

GARANTIAS.

A seção deve apresentar somente Garantias vinculadas ao Fornecedor correspondente.

Para cada Garantia, apresentar:

- número;
- Cliente;
- Produto;
- data de envio ao Fornecedor;
- última atualização;
- quantidade de dias sem atualização;
- situação.

Deve ser possível abrir os detalhes da Garantia.

---

## 21.75 Dias sem atualização da Garantia

A quantidade de dias sem atualização deve utilizar a regra oficial do módulo Garantias.

A contagem deve iniciar:

- na data e hora do envio ao Fornecedor;

ou

- na última atualização válida registrada enquanto a Garantia permanecer com o Fornecedor.

A apresentação deve utilizar America/Sao_Paulo.

---

## 21.76 Destaque de Garantia sem atualização

Garantia Enviada ao Fornecedor com 7 dias ou mais sem atualização válida deve possuir destaque visual.

A ficha deve deixar clara a necessidade de acompanhamento.

O destaque não representa automaticamente responsabilidade, recusa ou atraso legal do Fornecedor.

---

## 21.77 Situação atual das Garantias

Garantias Resolvidas ou Canceladas podem permanecer no histórico da ficha.

A visão operacional pode permitir filtro por:

- em andamento;
- resolvidas;
- canceladas.

A ficha deve preservar o histórico completo.

---

## 21.78 Desativação do Fornecedor

Fornecedor pode ser desativado mesmo quando possuir vínculos operacionais ativos.

A existência de:

- Contas em Aberto;
- Contas Vencidas;
- Crédito Disponível;
- Garantias em andamento

não bloqueia automaticamente a desativação.

O sistema deve apresentar aviso forte antes da confirmação.

---

## 21.79 Aviso antes da desativação

Quando existirem vínculos operacionais ativos, o sistema deve apresentar resumo antes de confirmar a desativação.

Exemplo:

Este Fornecedor possui vínculos operacionais ativos.

Contas em Aberto:
R$ 10.000,00.

Contas Vencidas:
R$ 2.000,00.

Crédito Disponível:
R$ 1.500,00.

Garantias em andamento:
3.

Deseja continuar?

O usuário deve confirmar a desativação.

---

## 21.80 Cálculo do aviso de desativação

Os valores e quantidades do aviso devem ser calculados pelo backend utilizando o estado atual.

O navegador não deve informar autoritativamente:

- saldo de Contas;
- valor vencido;
- Crédito disponível;
- quantidade de Garantias.

A confirmação deve utilizar o estado mais recente.

---

## 21.81 Efeitos da desativação do Fornecedor

Após a desativação, o Fornecedor:

- não pode ser utilizado em novas Entradas;
- não pode ser utilizado em novas Contas a Pagar;
- não pode ser selecionado em nova Garantia;
- permanece vinculado às operações históricas.

O Fornecedor não deve ser excluído.

---

## 21.82 Contas antigas de Fornecedor desativado

Contas a Pagar existentes do Fornecedor desativado continuam operacionais.

O sistema deve permitir:

- pagamento;
- pagamento parcial;
- estorno permitido;
- consulta;
- cancelamento conforme as regras oficiais.

A desativação do Fornecedor não cancela as Contas.

---

## 21.83 Créditos existentes de Fornecedor desativado

Créditos existentes do Fornecedor desativado permanecem preservados.

O Crédito pode continuar sendo utilizado em Contas a Pagar já existentes e válidas do mesmo Fornecedor.

A desativação não deve zerar ou reverter automaticamente o Crédito.

---

## 21.84 Limite da utilização de Crédito após desativação

Fornecedor desativado não pode receber nova Conta a Pagar.

Por esse motivo, Crédito existente não deve ser aplicado em nova obrigação criada após a desativação.

O Crédito pode ser utilizado somente em Contas válidas já existentes do mesmo Fornecedor.

---

## 21.85 Garantias em andamento de Fornecedor desativado

Garantias já vinculadas ao Fornecedor desativado continuam operacionais.

O sistema deve permitir:

- atualização;
- acompanhamento;
- aprovação;
- recusa;
- solução;
- resolução.

A desativação não remove o Fornecedor das Garantias históricas ou em andamento.

---

## 21.86 Nova Garantia e Fornecedor desativado

Fornecedor desativado não deve aparecer na seleção normal de nova Garantia.

Quando uma Garantia antiga já possuir o Fornecedor vinculado, o vínculo permanece.

Não substituir automaticamente o Fornecedor por outro.

---

## 21.87 Entradas antigas de Fornecedor desativado

Entradas históricas permanecem vinculadas ao Fornecedor desativado.

O usuário pode consultar:

- Entrada;
- Contas vinculadas;
- Devoluções;
- Créditos.

A desativação não reescreve o histórico.

---

## 21.88 Reativação do Fornecedor

Administrador e Operador podem reativar Fornecedor desativado.

Após reativação, o Fornecedor volta a poder ser utilizado em novas operações compatíveis.

A reativação não altera os vínculos históricos.

---

## 21.89 Revalidação do cadastro na reativação

Ao reativar, o backend deve validar as regras atuais do cadastro.

Exemplo:

CPF ou CNPJ duplicado não deve ser permitido em razão de inconsistência criada por dado inválido.

A reativação deve preservar a integridade cadastral.

---

## 21.90 Edição da ficha

Administrador e Operador podem editar os dados cadastrais permitidos do Fornecedor.

A edição deve seguir as regras oficiais de:

- obrigatoriedade;
- CPF;
- CNPJ;
- unicidade;
- normalização.

Alterações cadastrais não reescrevem operações históricas.

---

## 21.91 Cards e filtros após alteração financeira

Os cards, filtros e valores da tela de Fornecedores devem ser atualizados após operações que alterem:

- Contas a Pagar;
- pagamentos;
- estornos;
- Devoluções ao Fornecedor;
- Créditos;
- utilizações de Crédito.

O sistema não deve manter saldos antigos como se fossem atuais.

---

## 21.92 Atualização após Garantia

A seção Garantias deve ser atualizada após:

- envio ao Fornecedor;
- atualização de acompanhamento;
- aprovação;
- recusa;
- resolução;
- cancelamento.

A quantidade de dias sem atualização deve utilizar o histórico atual.

---

## 21.93 Estado de carregamento

A tela de Fornecedores e a ficha detalhada devem possuir estado de carregamento claro.

Dados antigos não devem ser apresentados provisoriamente como se pertencessem ao Fornecedor atualmente selecionado.

A troca de Fornecedor deve invalidar requisições antigas quando necessário.

---

## 21.94 Estado de erro

Falhas de rede ou servidor devem apresentar estado de erro discreto.

Deve ser possível tentar novamente.

Erro de autenticação deve seguir o fluxo oficial de sessão expirada.

---

## 21.95 Estado vazio

Se um Fornecedor não possuir determinada operação, a seção correspondente deve apresentar estado vazio claro.

Exemplos:

Nenhuma Entrada vinculada.

Nenhuma Conta a Pagar.

Nenhuma Devolução ao Fornecedor.

Nenhum Crédito.

Nenhuma Garantia vinculada.

Não criar registros artificiais para preencher a tela.

---

## 21.96 Fonte autoritativa

O backend deve calcular e validar:

- Contas em Aberto;
- Contas Vencidas;
- Crédito Disponível;
- Entradas vinculadas;
- saldos;
- Devoluções;
- conciliações;
- Créditos;
- utilizações;
- Garantias;
- vínculos operacionais ativos antes da desativação.

O navegador não deve informar esses resumos como fonte autoritativa.

---

## 21.97 Isolamento por loja

A tela e a ficha do Fornecedor devem respeitar a loja autenticada.

O sistema deve impedir:

- consultar Fornecedor de outra loja;
- visualizar Contas de outra loja;
- visualizar Crédito de outra loja;
- visualizar Garantias de outra loja;
- desativar Fornecedor de outra loja.

A validação deve ocorrer no backend.

---

## 21.98 Regras gerais da Ficha e Gestão de Fornecedores

O sistema deve:

- possuir tela própria de Fornecedores;
- permitir acesso ao Administrador;
- permitir acesso ao Operador;
- apresentar card Fornecedores Ativos;
- apresentar card Contas em Aberto;
- apresentar card Contas Vencidas;
- apresentar card Crédito Disponível;
- utilizar valores financeiros atuais;
- permitir busca por Nome ou Razão Social;
- permitir busca por Nome Fantasia;
- permitir busca por CPF ou CNPJ;
- permitir busca por Telefone;
- permitir filtro por Situação;
- permitir filtro por Contas em Aberto;
- permitir filtro por Contas Vencidas;
- permitir filtro por Crédito Disponível;
- apresentar listagem com valores atuais;
- possuir ação VER DETALHES;
- possuir ficha detalhada;
- apresentar resumo financeiro;
- apresentar dados cadastrais;
- listar Entradas;
- utilizar Fornecedor histórico das Entradas;
- listar Contas a Pagar;
- identificar origem das Contas;
- utilizar saldos líquidos atuais;
- listar Devoluções ao Fornecedor;
- destacar acertos financeiros pendentes;
- apresentar Crédito total disponível;
- listar Créditos individuais;
- listar utilizações de Crédito;
- preservar origem e destino dos Créditos;
- listar Garantias vinculadas;
- apresentar dias sem atualização;
- destacar Garantias com 7 dias sem atualização;
- permitir desativação com vínculos ativos;
- apresentar aviso forte antes da desativação;
- mostrar Contas em Aberto no aviso;
- mostrar Contas Vencidas;
- mostrar Crédito Disponível;
- mostrar Garantias em andamento;
- calcular o aviso no backend;
- impedir novas Entradas com Fornecedor desativado;
- impedir novas Contas com Fornecedor desativado;
- impedir seleção em nova Garantia;
- manter Contas antigas operacionais;
- manter Créditos existentes;
- permitir uso de Crédito em Contas antigas válidas;
- manter Garantias em andamento;
- preservar Entradas históricas;
- permitir reativação;
- validar integridade na reativação;
- permitir edição cadastral;
- atualizar valores após operações financeiras;
- atualizar Garantias;
- possuir estado de carregamento;
- possuir estado de erro;
- possuir estado vazio;
- utilizar backend como fonte autoritativa;
- respeitar isolamento por loja.

# 22. BACKUP, IMPORTAÇÃO E RESET

## 22.1 Finalidade

As funções relacionadas a Backup, Importação e Reset devem priorizar:

- integridade dos dados;
- segurança financeira;
- preservação de histórico;
- rastreabilidade;
- isolamento por loja.

O sistema deve distinguir:

- Backup técnico;
- Exportação de dados;
- Relatórios;
- Restauração técnica.

Essas funções possuem finalidades diferentes.

Não tratar Backup técnico como relatório comum.

Não tratar exportação de relatório como mecanismo de restauração.

---

## 22.2 Acesso ao Backup manual

O sistema deve permitir geração manual de Backup técnico pela área Configurações.

Somente usuário com perfil Administrador pode gerar Backup técnico.

Usuário com perfil Operador não pode gerar Backup técnico.

A autorização deve ser validada no backend utilizando o perfil persistido do usuário autenticado.

O navegador não deve definir autoritativamente que o usuário é Administrador.

---

## 22.3 Backup por loja

O Backup técnico pertence à loja autenticada.

O Backup não deve incluir dados de outras lojas.

A geração deve respeitar o isolamento por loja.

O sistema não deve permitir que identificadores enviados pelo navegador sejam utilizados para acessar dados de outra loja.

---

## 22.4 Conteúdo do Backup técnico

O Backup técnico deve possuir os dados necessários para reconstrução consistente da loja, conforme a estrutura existente no momento da geração.

Quando aplicável, incluir:

- Clientes;
- Produtos;
- Estoque;
- Movimentações de Estoque;
- Vendas;
- Itens das Vendas;
- Pagamentos das Vendas;
- Cancelamentos;
- Devoluções;
- Itens das Devoluções;
- Alocações financeiras das Devoluções;
- Trocas;
- Condicionais;
- Itens dos Condicionais;
- Crediário;
- Parcelas;
- Pagamentos de parcelas;
- Recebíveis;
- Caixa;
- Movimentações financeiras;
- Contas a Pagar;
- Pagamentos de Contas a Pagar;
- Fornecedores;
- Marcas;
- Categorias de Produtos;
- Gêneros, quando persistidos como cadastro;
- Tamanhos;
- Cores;
- Categorias de Despesas;
- Usuários;
- Configurações da loja;
- Auditorias;
- Estado de leitura dos Alertas;
- Operações idempotentes;
- demais vínculos persistentes necessários à reconstrução consistente da loja.

A lista deve acompanhar a evolução oficial do schema.

Uma nova entidade financeira ou operacional persistente não deve ser ignorada pelo Backup técnico quando for necessária à reconstrução consistente do estado.

---

## 22.5 Integridade referencial do Backup

O Backup técnico deve preservar os identificadores e vínculos persistentes necessários à reconstrução dos dados.

Exemplos:

- Venda e Cliente;
- Venda e Itens;
- Venda e Pagamentos;
- Devolução e Venda;
- Devolução e Itens;
- Devolução e Alocações;
- Condicional e Cliente;
- Condicional e Produtos;
- Crediário e Venda;
- Parcela e Crediário;
- Pagamento e Parcela;
- Conta a Pagar e Fornecedor;
- Produto e Marca;
- Produto e Categoria.

Não gerar Backup técnico composto apenas por textos visuais quando existirem vínculos persistentes necessários.

---

## 22.6 Dados financeiros

O Backup técnico deve preservar os dados financeiros persistidos necessários à reconstrução consistente da loja.

Isso inclui, quando aplicável:

- valores originais;
- valores líquidos;
- descontos;
- custos históricos preservados;
- pagamentos;
- estornos;
- devoluções;
- alocações;
- recebíveis;
- saldos;
- movimentações de caixa;
- Contas a Pagar;
- pagamentos parciais;
- operações idempotentes.

O Backup não deve recalcular ou substituir valores históricos utilizando o cadastro atual do Produto.

---

## 22.7 Dados históricos

O Backup técnico deve preservar os dados históricos existentes.

Alterações atuais de:

- Produto;
- Marca;
- Categoria;
- Cliente;
- Fornecedor;
- Usuário

não devem reescrever snapshots históricos durante a geração do Backup.

O Backup deve representar os dados persistidos no momento da geração.

---

## 22.8 Senhas em texto aberto

O sistema nunca deve incluir senha em texto aberto no Backup técnico.

O sistema não deve:

- descriptografar senha;
- tentar reconstruir senha original;
- registrar senha em arquivo de Backup;
- registrar senha em metadados;
- registrar senha em auditoria.

Senhas devem seguir as regras oficiais de segurança e armazenamento.

---

## 22.9 Hash de senha no Backup técnico

Quando tecnicamente necessário para uma futura restauração integral segura, o Backup técnico pode preservar o hash persistido da senha.

O hash somente pode fazer parte do Backup técnico.

O hash de senha não deve ser incluído em:

- exportação comum de usuários;
- PDF;
- relatório;
- planilha;
- consulta operacional;
- exportação destinada à leitura humana.

Hash de senha não é senha em texto aberto.

A preservação do hash não autoriza sua exibição na interface.

---

## 22.10 Backup técnico e Exportação de dados

Backup técnico e Exportação de dados são funções diferentes.

Backup técnico:

- possui finalidade de preservação técnica;
- pode conter identificadores internos;
- pode conter metadados de schema;
- pode preservar hashes de senha quando tecnicamente necessário;
- não possui finalidade principal de leitura humana.

Exportação de dados:

- possui finalidade de consulta;
- pode utilizar PDF ou outro formato oficialmente permitido;
- não inclui senha;
- não inclui hash de senha;
- não deve expor dados técnicos internos desnecessários.

O sistema não deve utilizar uma exportação comum como se fosse Backup técnico completo.

---

## 22.11 Formato do Backup técnico

O formato do Backup técnico deve ser definido pelo sistema.

O usuário não escolhe livremente o formato técnico do Backup.

O Backup deve utilizar estrutura própria, versionada e compatível com a finalidade técnica.

O arquivo deve possuir metadados suficientes para identificar sua origem e estrutura.

---

## 22.12 Metadados do Backup

O Backup técnico deve possuir, conforme aplicável:

- versão do formato do Backup;
- versão ou identificação compatível do schema;
- identificação persistente da loja;
- data e hora da geração;
- fuso operacional da loja ou do sistema;
- usuário responsável pela geração;
- versão da aplicação, quando disponível;
- metadados necessários à validação técnica futura.

A data e hora devem seguir as regras oficiais de timestamp do sistema.

Novos timestamps devem ser armazenados ou representados com informação inequívoca de fuso.

---

## 22.13 Versão do Backup

Todo Backup técnico deve possuir versão de formato.

Exemplo conceitual:

backupVersion:
1

A versão deve permitir que uma futura ferramenta técnica determine a estrutura esperada do arquivo.

O sistema não deve assumir que todo arquivo de Backup antigo possui a mesma estrutura do schema atual.

---

## 22.14 Geração do Backup

Ao solicitar GERAR BACKUP, o backend deve:

1. validar a sessão;
2. recuperar o usuário autenticado;
3. validar o perfil persistido;
4. confirmar que o usuário é Administrador;
5. identificar a loja autenticada;
6. obter os dados da loja de forma consistente;
7. montar o Backup técnico;
8. adicionar os metadados;
9. gerar o arquivo;
10. registrar a operação para rastreabilidade.

O frontend não deve montar autoritativamente o Backup utilizando somente dados já carregados no navegador.

---

## 22.15 Consistência durante a geração

O Backup técnico deve representar um estado consistente dos dados.

O sistema deve evitar gerar arquivo em que partes relacionadas representem momentos incompatíveis da operação.

Exemplo de situação inválida:

- Venda incluída;
- pagamento da mesma Venda ainda não incluído por diferença de leitura;
- estoque lido em outro estado incompatível.

A implementação deve utilizar mecanismo de consistência compatível com o banco e a arquitetura oficial.

---

## 22.16 Backup e operações simultâneas

A geração de Backup não deve corromper operações financeiras simultâneas.

O mecanismo de leitura consistente deve respeitar as características de:

- SQLite;
- PostgreSQL.

A implementação não deve introduzir gravações desnecessárias nos dados de negócio apenas para gerar o Backup.

---

## 22.17 Download do Backup

Após geração válida, o Administrador pode baixar o arquivo de Backup técnico.

O download do arquivo não altera:

- estoque;
- vendas;
- caixa;
- Crediário;
- Contas a Pagar;
- usuários;
- configurações.

Gerar Backup é uma operação de leitura e preservação técnica.

---

## 22.18 Nome do arquivo

O sistema deve gerar nome de arquivo identificável e determinístico o suficiente para uso operacional.

O nome pode conter:

- identificação segura da loja;
- data;
- hora.

Exemplo conceitual:

backup-mova-sports-2026-07-14-153000

Não incluir:

- senha;
- hash de senha;
- CPF;
- dados pessoais sensíveis desnecessários

no nome do arquivo.

---

## 22.19 Registro da geração

A geração do Backup técnico deve ser registrada para rastreabilidade.

Registrar, conforme a estrutura de auditoria oficial:

- loja;
- usuário;
- data e hora;
- tipo da operação;
- versão do Backup.

Não registrar o conteúdo integral do Backup dentro da auditoria.

Não registrar senhas ou hashes de senha no texto da auditoria.

---

## 22.20 Último Backup manual

A área Dados e Backup deve apresentar informação sobre o último Backup manual gerado.

Apresentar, quando existir:

- data;
- hora;
- usuário responsável.

Exemplo:

Último backup manual:

14/07/2026 às 15:30

Gerado por Mauro

A informação deve representar geração concluída com sucesso.

Tentativa que falhou não deve aparecer como último Backup concluído.

---

## 22.21 Falha na geração

Quando ocorrer falha durante a geração do Backup:

- não registrar a operação como concluída;
- não apresentar arquivo incompleto como Backup válido;
- informar a falha ao usuário;
- permitir nova tentativa.

Quando tecnicamente possível, arquivos temporários incompletos devem ser descartados.

---

## 22.22 Estado de carregamento

Durante a geração do Backup, a interface deve apresentar estado de processamento.

Exemplo:

Gerando backup...

O botão GERAR BACKUP deve ser protegido contra múltiplos acionamentos simultâneos desnecessários.

A interface não deve aparentar conclusão antes da confirmação do backend.

---

## 22.23 Restauração pela interface normal

O sistema não deve possuir função operacional normal de restauração de Backup.

Não disponibilizar botão ativo:

RESTAURAR BACKUP.

Administrador não pode substituir os dados atuais da loja por um arquivo através da interface normal.

Operador não pode restaurar Backup.

---

## 22.24 Motivo da restrição de restauração

A restauração pode afetar:

- estoque;
- vendas;
- caixa;
- recebíveis;
- Crediário;
- Contas a Pagar;
- usuários;
- auditoria;
- operações idempotentes;
- vínculos históricos.

Por esse motivo, restauração não deve ser tratada como ação administrativa simples.

Uma futura restauração deve possuir fluxo técnico específico, validação e auditoria próprias antes de ser oficialmente implementada.

---

## 22.25 Arquivos de Backup enviados pelo navegador

A interface normal não deve aceitar arquivo de Backup para substituir o estado da loja.

O sistema não deve confiar em arquivo enviado pelo navegador como estado autoritativo completo.

Não permitir que o usuário envie um Backup e determine diretamente:

- vendas;
- caixa;
- estoque;
- pagamentos;
- usuários;
- auditorias.

---

## 22.26 Importação geral de estado

Importação geral de estado não é uma função oficial da aplicação.

Não permitir substituir todo o estado do sistema por:

- JSON;
- arquivo de Backup;
- arquivo de estado;
- conteúdo copiado e colado.

Fluxos legados de importação geral devem ser considerados fora da regra oficial até auditoria e decisão específica.

---

## 22.27 Funções legadas de importação

A existência de função legada no código não torna a operação uma regra oficial.

Fluxos antigos equivalentes a:

- Importar estado;
- Restaurar JSON;
- Substituir dados;
- RESTAURAR

devem ser auditados separadamente.

Quando encontrados, não devem ser documentados como função operacional oficial apenas porque existem no código.

---

## 22.28 Reset global

O sistema não deve possuir botão operacional normal de Reset global.

Não disponibilizar ação equivalente a:

- RESETAR SISTEMA;
- ZERAR SISTEMA;
- APAGAR TODOS OS DADOS;
- LIMPAR LOJA.

Essa restrição também se aplica ao Administrador.

---

## 22.29 Administrador e Reset

O perfil Administrador não autoriza exclusão global dos dados da loja.

Administrador possui permissões específicas definidas nas regras oficiais.

O perfil não deve ser interpretado como autorização irrestrita para apagar:

- Clientes;
- Produtos;
- Vendas;
- Caixa;
- Crediário;
- Contas a Pagar;
- Auditorias.

---

## 22.30 Confirmações textuais legadas

Confirmações textuais como:

ZERAR

ou:

RESTAURAR

não são proteção suficiente para uma operação destrutiva global.

A existência de confirmação textual não oficializa a função.

Fluxos legados que utilizem essas confirmações devem ser auditados e removidos, desativados ou isolados conforme a arquitetura vigente.

---

## 22.31 Limpeza de ambiente de testes

A necessidade de limpar dados para desenvolvimento ou testes deve ser tratada fora da operação comercial normal.

Ambientes de:

- desenvolvimento;
- testes automatizados;
- homologação

podem possuir mecanismos técnicos próprios para criação e limpeza de dados.

Esses mecanismos não devem estar disponíveis na interface de produção.

---

## 22.32 Produção

Em ambiente de produção, o sistema não deve disponibilizar função de zerar a loja.

A configuração de ambiente não deve depender somente de ocultação visual no frontend.

O backend deve impedir operações destrutivas globais não autorizadas pela regra oficial.

---

## 22.33 Operações específicas dos módulos

A ausência de Reset global não impede operações oficiais específicas.

Exemplos:

- desativar Cliente;
- reativar Cliente;
- desativar Usuário;
- reativar Usuário;
- desativar Fornecedor;
- desativar Marca;
- desativar Categoria;
- cancelar Venda;
- realizar Devolução;
- realizar Troca;
- estornar operação quando permitido;
- cancelar Conta a Pagar conforme regra oficial.

Cada operação deve seguir sua própria regra de negócio.

---

## 22.34 Correção rastreável

Erros operacionais devem ser corrigidos utilizando o fluxo específico do módulo correspondente.

Exemplo:

Venda incorreta:
Cancelamento, Devolução ou Troca, conforme o caso.

Conta incorreta:
Cancelamento ou correção permitida pela regra de Contas a Pagar.

Cliente que não deve mais ser utilizado:
Desativação.

Fornecedor que não deve mais ser utilizado:
Desativação.

Não utilizar Reset global para corrigir erros individuais.

---

## 22.35 Preservação de histórico

As operações específicas devem preservar histórico conforme suas regras.

A aplicação deve priorizar:

- cancelamento;
- estorno;
- devolução;
- desativação;
- reativação;
- movimentação corretiva rastreável

em vez de exclusão global ou reescrita silenciosa dos dados.

---

## 22.36 Backup automático

Backup automático não é uma função operacional do usuário dentro da aplicação neste momento.

O sistema não deve disponibilizar configuração administrativa de:

- backup diário;
- backup semanal;
- horário de backup automático

como regra oficial atual.

---

## 22.37 Backup de infraestrutura

Backups automáticos do banco e da infraestrutura devem ser tratados conforme o ambiente de hospedagem e banco de dados.

Exemplos de responsabilidades técnicas:

- política de retenção;
- snapshots;
- backups do PostgreSQL;
- redundância;
- recuperação de desastre.

Essas políticas não devem ser confundidas com o botão GERAR BACKUP da aplicação.

---

## 22.38 Independência entre Backup manual e infraestrutura

A existência de Backup manual não substitui uma política adequada de Backup de infraestrutura.

Da mesma forma, a existência de Backup de infraestrutura não impede a aplicação de oferecer Backup técnico manual ao Administrador.

São mecanismos com finalidades diferentes.

---

## 22.39 Tela Dados e Backup

A área Configurações do Administrador deve possuir seção:

DADOS E BACKUP.

A seção deve apresentar:

Backup manual.

Texto explicativo equivalente a:

Gere uma cópia técnica dos dados da loja.

Ação principal:

GERAR BACKUP.

---

## 22.40 Informações da tela Dados e Backup

A tela deve apresentar, quando disponível:

- data do último Backup manual;
- hora do último Backup manual;
- usuário responsável.

A tela não deve apresentar ações operacionais de:

- Importar;
- Restaurar;
- Resetar;
- Zerar.

---

## 22.41 Operador e Dados e Backup

Usuário com perfil Operador não deve possuir acesso funcional à geração de Backup técnico.

O frontend pode ocultar a área administrativa correspondente.

O backend deve recusar a operação quando o perfil persistido não for Administrador.

Ocultar o botão não substitui validação de autorização no servidor.

---

## 22.42 Sessão expirada

Quando a sessão expirar durante a solicitação de geração de Backup, o sistema deve seguir o fluxo oficial de sessão expirada.

Dados técnicos do Backup não devem permanecer disponíveis para download após uma resposta não autorizada gerada por sessão inválida.

---

## 22.43 Dados pessoais no Backup

O Backup técnico pode conter dados pessoais necessários à reconstrução dos cadastros da loja.

Exemplos:

- nome;
- CPF;
- telefone;
- endereço;
- e-mail.

Por possuir dados pessoais e financeiros, o arquivo deve ser tratado como conteúdo sensível da loja.

A interface deve deixar claro que o arquivo é uma cópia técnica dos dados.

---

## 22.44 Exposição do conteúdo

O sistema não deve exibir o conteúdo integral do Backup técnico na tela como texto comum.

Não apresentar:

- JSON completo;
- hashes;
- identificadores internos;
- dados financeiros completos

em uma caixa de texto para copiar e colar.

A função normal deve gerar o arquivo para download autorizado.

---

## 22.45 Logs e erros

Mensagens de erro relacionadas ao Backup não devem expor:

- senha;
- hash de senha;
- conteúdo integral do banco;
- tokens;
- segredos;
- credenciais de infraestrutura.

Logs técnicos devem seguir as regras oficiais de segurança.

---

## 22.46 Evolução futura de restauração

Uma futura implementação de restauração deve ser tratada como tarefa própria.

Antes da implementação, devem ser definidos:

- quem pode restaurar;
- validação do arquivo;
- compatibilidade de versão;
- validação de schema;
- integridade referencial;
- comportamento com dados atuais;
- estratégia de rollback;
- auditoria;
- concorrência;
- confirmação;
- recuperação em caso de falha.

A regra atual não autoriza implementação automática de restauração.

---

## 22.47 Evolução futura de importação

Importações específicas podem ser definidas futuramente.

Exemplo conceitual:

- importar Produtos;
- importar Clientes;
- importar Fornecedores.

Cada importação deve possuir:

- formato oficial;
- validação;
- tratamento de duplicidade;
- relatório de erros;
- regras de atualização;
- auditoria.

A possibilidade futura de importação específica não autoriza importação geral de estado.

---

## 22.48 Regras gerais de Backup, Importação e Reset

O sistema deve:

- permitir Backup técnico manual;
- permitir Backup técnico somente ao Administrador;
- validar a autorização no backend;
- gerar Backup somente da loja autenticada;
- preservar isolamento por loja;
- incluir dados necessários à reconstrução consistente;
- preservar vínculos persistentes;
- preservar dados financeiros necessários;
- preservar dados históricos;
- nunca incluir senha em texto aberto;
- permitir hash de senha somente no Backup técnico quando necessário;
- nunca incluir hash de senha em exportações comuns;
- distinguir Backup técnico de Exportação de dados;
- utilizar formato técnico próprio;
- versionar o formato do Backup;
- incluir metadados técnicos;
- registrar data e hora da geração;
- registrar usuário responsável;
- gerar o Backup no backend;
- utilizar leitura consistente;
- não corromper operações simultâneas;
- permitir download após geração válida;
- registrar a geração para rastreabilidade;
- apresentar o último Backup manual concluído;
- não considerar tentativa falha como Backup concluído;
- apresentar estado de processamento;
- impedir múltiplas solicitações simultâneas desnecessárias;
- não permitir restauração pela interface normal;
- não permitir envio de Backup para substituir o estado;
- não oficializar importação geral;
- considerar fluxos legados de importação fora da regra oficial;
- não possuir Reset global;
- não permitir Reset global ao Administrador;
- não considerar confirmações ZERAR ou RESTAURAR como proteção suficiente;
- manter limpeza de dados restrita a ambientes técnicos de desenvolvimento ou teste;
- impedir função de zerar loja em produção;
- utilizar operações específicas dos módulos para correções;
- preservar histórico;
- não configurar Backup automático pela interface neste momento;
- tratar Backup automático de infraestrutura separadamente;
- possuir área DADOS E BACKUP;
- apresentar ação GERAR BACKUP;
- apresentar último Backup manual;
- não apresentar Importar;
- não apresentar Restaurar;
- não apresentar Resetar;
- não apresentar Zerar;
- impedir Operador de gerar Backup;
- tratar arquivo de Backup como conteúdo sensível;
- não exibir o conteúdo técnico integral na interface;
- não expor segredos em erros ou logs;
- tratar futura restauração como tarefa específica;
- tratar futuras importações específicas individualmente.

# 23. IMPRESSÕES E DOCUMENTOS GERADOS

## 23.1 Finalidade

As impressões, PDFs e arquivos gerados pelo sistema devem apresentar informações claras, consistentes e vinculadas aos dados oficiais persistidos.

Os documentos devem utilizar as mesmas regras de negócio dos módulos de origem.

A geração de documento não deve:

- alterar dados;
- criar movimentação financeira;
- alterar estoque;
- alterar situação de venda;
- alterar histórico.

Imprimir, reimprimir ou exportar representa uma operação de consulta e apresentação.

---

## 23.2 Identidade visual da loja

Os documentos gerados pelo sistema devem utilizar a identidade visual configurada da loja.

Quando existir logo cadastrada, o documento pode apresentar:

- logo da loja;
- nome da loja.

O Nome da loja deve sempre ser apresentado.

Os dados adicionais da loja devem respeitar as preferências de impressão definidas nas Configurações.

Podem ser apresentados, quando habilitados:

- CPF ou CNPJ;
- telefone;
- WhatsApp;
- endereço;
- e-mail.

---

## 23.3 Ausência de logo

A ausência de logo cadastrada não deve impedir a geração de documentos.

Quando não existir logo:

- apresentar o Nome da loja em destaque;
- preservar o alinhamento do documento;
- não apresentar imagem quebrada;
- não reservar espaço visual vazio desnecessário.

O documento deve continuar funcional e identificável.

---

## 23.4 Nome da loja

O Nome da loja deve ser obtido das Configurações persistidas.

Não utilizar texto fixo MOVA SPORTS quando o texto representar a identificação comercial da loja.

Quando o Nome da loja configurado for MOVA SPORTS, apresentar normalmente esse nome.

O navegador não deve informar autoritativamente o Nome da loja para geração de documentos oficiais.

---

## 23.5 Dados da operação

Documentos que representam uma operação devem apresentar a data e hora da própria operação.

Exemplos:

- Venda;
- Condicional;
- Troca;
- Cancelamento;
- Devolução, quando existir documento específico.

A data de impressão ou reimpressão não deve substituir a data histórica da operação.

---

## 23.6 Reimpressão

Quando um documento histórico for reimpresso, os dados da operação original devem permanecer preservados.

Exemplo:

Venda realizada:
10/07/2026 às 14:30.

Reimpressão:
15/07/2026 às 09:10.

O documento deve continuar apresentando:

Venda:
10/07/2026 às 14:30.

O sistema pode apresentar de forma discreta:

Reimpresso em 15/07/2026 às 09:10.

A informação de reimpressão não altera a data da venda.

---

## 23.7 Data e hora da geração

Documentos exportados, como Relatórios e Catálogo em PDF, devem apresentar a data e hora da geração quando aplicável.

A data e hora devem utilizar o fuso operacional:

America/Sao_Paulo.

Não apresentar timestamp UTC ou formato ISO diretamente ao usuário.

---

## 23.8 Formato visual de datas

Datas apresentadas ao usuário devem utilizar o padrão brasileiro:

DD/MM/AAAA.

Exemplo:

14/07/2026.

Quando houver data e hora, utilizar apresentação equivalente a:

14/07/2026 às 15:30.

Não apresentar ao usuário formatos como:

2026-07-14T18:30:00+00:00.

O armazenamento técnico continua seguindo as regras oficiais de timestamps.

---

## 23.9 Formato de valores monetários

Valores monetários devem utilizar o padrão brasileiro.

Exemplo:

R$ 1.250,90.

Não apresentar valores ao usuário como:

1250.9

R$1250.90

1,250.90

O formato visual não altera o valor numérico persistido.

---

## 23.10 Usuário responsável

Documentos de operações devem apresentar o usuário responsável quando definido pelas regras do módulo.

Na Venda, utilizar apresentação equivalente a:

Atendido por: Mauro.

Nos documentos de:

- Condicional;
- Troca;
- operações administrativas compatíveis

utilizar apresentação equivalente a:

Usuário responsável: Mauro.

O nome apresentado deve corresponder ao usuário histórico da operação.

---

## 23.11 Alteração posterior do usuário

A alteração futura do nome, perfil ou situação do usuário não deve transferir a autoria da operação para outro usuário.

Quando existir snapshot histórico do nome do usuário, o documento deve utilizar o dado preservado.

Quando existir somente vínculo persistente, o sistema deve manter a vinculação correta ao usuário original.

Usuário desativado continua identificado nas operações históricas.

---

## 23.12 Comprovante da Venda

A Venda deve permitir impressão de comprovante simples em estilo de cupom.

O comprovante deve priorizar leitura rápida.

A ordem visual recomendada é:

1. identificação da loja;
2. número da Venda;
3. data e hora;
4. cliente;
5. usuário responsável;
6. produtos;
7. quantidades;
8. preço praticado;
9. descontos e acréscimos;
10. total;
11. formas de pagamento;
12. informações do Crediário, quando aplicável;
13. valor recebido em Dinheiro, quando aplicável;
14. troco;
15. mensagem de rodapé.

---

## 23.13 Cabeçalho do comprovante de Venda

O cabeçalho deve apresentar:

- logo, quando cadastrada;
- Nome da loja.

Também pode apresentar os dados de contato habilitados nas Configurações.

O Nome da loja é obrigatório.

---

## 23.14 Identificação da Venda

O comprovante deve apresentar:

- número da Venda;
- data;
- hora.

O número deve corresponder à numeração automática persistida pelo backend.

O usuário não pode alterar o número durante a impressão.

---

## 23.15 Cliente no comprovante

O comprovante deve apresentar o cliente vinculado à Venda.

Quando a Venda utilizar Cliente Padrão, o documento pode apresentar:

Cliente Padrão.

Quando existir cliente cadastrado, apresentar seu Nome.

O comprovante simples não precisa exibir CPF completo do cliente por padrão.

---

## 23.16 Produtos no comprovante da Venda

Cada item deve permitir identificar:

- produto;
- atributos relevantes;
- quantidade;
- preço praticado.

Os atributos podem incluir:

- tamanho;
- cor.

O documento deve utilizar os dados históricos da Venda.

Não reconstruir o item utilizando somente o cadastro atual do Produto.

---

## 23.17 Preço original e preço praticado

O comprovante simples deve priorizar o preço efetivamente praticado.

Quando existir desconto ou acréscimo relevante, o documento deve deixar a operação compreensível.

Pode apresentar, conforme a estrutura da Venda:

- preço original;
- desconto;
- acréscimo;
- preço praticado.

O sistema não deve apresentar preço atual do Produto como se fosse o preço histórico da Venda.

---

## 23.18 Desconto geral

Quando existir desconto geral aplicado à Venda, o comprovante deve apresentar a informação.

Exemplo:

Desconto:
R$ 20,00.

O total final deve corresponder ao valor oficial confirmado pela Venda.

---

## 23.19 Acréscimo

Quando existir acréscimo aplicado à Venda, o comprovante deve apresentar a informação.

O valor deve utilizar o histórico da operação.

A impressão não deve recalcular o acréscimo utilizando valores atuais.

---

## 23.20 Total da Venda

O comprovante deve apresentar o total final da Venda.

O total deve utilizar o valor oficial persistido após:

- preços praticados;
- descontos;
- acréscimos.

O documento não deve confiar em total recalculado exclusivamente pelo navegador.

---

## 23.21 Formas de pagamento

O comprovante deve apresentar todas as formas de pagamento utilizadas.

Exemplo:

Pix:
R$ 100,00.

Dinheiro:
R$ 50,00.

Quando existir pagamento misto, não resumir a operação em apenas uma forma.

As formas devem utilizar os registros oficiais da Venda.

---

## 23.22 Crediário no comprovante

Quando a Venda possuir Crediário, o comprovante deve apresentar as informações correspondentes.

Devem ser identificáveis:

- quantidade de parcelas;
- identificação das parcelas;
- datas de vencimento;
- valores.

Exemplo:

Crediário — 3 parcelas.

1/3 — 10/08/2026 — R$ 100,00.

2/3 — 10/09/2026 — R$ 100,00.

3/3 — 10/10/2026 — R$ 100,00.

As datas devem utilizar a regra oficial de data-base mensal.

---

## 23.23 Valor recebido em Dinheiro

Quando houver pagamento em Dinheiro, o comprovante deve apresentar o valor entregue pelo cliente quando essa informação fizer parte da Venda.

Exemplo:

Dinheiro recebido:
R$ 100,00.

Essa informação deve ser diferenciada do valor efetivamente devido em Dinheiro.

---

## 23.24 Troco

Quando existir troco, o comprovante deve apresentar:

Troco:
R$ 10,00.

O troco deve utilizar o valor oficial calculado pelo backend.

O troco não é receita.

Não apresentar troco quando o valor for igual a zero.

---

## 23.25 Mensagem de rodapé

O comprovante de Venda deve utilizar a mensagem de rodapé configurada, quando existir.

O texto deve ser apresentado como texto simples.

Não executar:

- HTML;
- JavaScript;
- código informado na Configuração.

Quando não existir mensagem configurada, o documento pode encerrar após os dados da operação.

---

## 23.26 Comprovante histórico original

A Venda deve possuir possibilidade de imprimir o comprovante da operação original.

O comprovante original deve representar a Venda no momento de sua conclusão.

Operações posteriores não devem reescrever o comprovante histórico original.

Exemplos de operações posteriores:

- Cancelamento;
- Devolução;
- Troca.

---

## 23.27 Venda cancelada e comprovante original

Quando uma Venda for posteriormente cancelada, o comprovante histórico original da Venda continua representando a operação originalmente realizada.

A reimpressão intitulada:

COMPROVANTE DA VENDA ORIGINAL

deve preservar:

- produtos;
- valores;
- pagamentos;
- cliente;
- usuário.

O sistema não deve apagar esses dados.

---

## 23.28 Venda com Devolução e comprovante original

Quando existir Devolução posterior, o comprovante original não deve ser reescrito como se a Venda tivesse sido originalmente menor.

A Venda original permanece preservada.

A Devolução possui seu próprio histórico e vínculo.

---

## 23.29 Venda com Troca e comprovante original

Quando existir Troca posterior, o comprovante original não deve substituir os produtos da Venda pelos produtos novos da Troca.

O comprovante da Venda original permanece histórico.

A Troca deve possuir documento e vínculo próprios.

---

## 23.30 Detalhes atuais da Venda

Além do comprovante original, o sistema pode permitir impressão dos detalhes atuais da Venda.

A ação pode ser identificada como:

IMPRIMIR DETALHES ATUAIS.

Esse documento deve apresentar a situação atual.

Pode identificar:

- Venda concluída;
- Venda cancelada;
- Devoluções;
- Trocas;
- Crediário;
- pagamentos relacionados.

---

## 23.31 Diferença entre comprovante original e detalhes atuais

O sistema deve diferenciar claramente:

COMPROVANTE DA VENDA ORIGINAL

e:

DETALHES ATUAIS DA VENDA.

O usuário não deve receber documentos com títulos ambíguos.

O comprovante original representa a operação original.

Os detalhes atuais representam o estado histórico acumulado até o momento da geração.

---

## 23.32 Impressão do Condicional

O Condicional deve seguir as regras específicas de impressão do módulo Condicional.

O documento deve apresentar, no mínimo:

- identificação da loja;
- número do Condicional;
- data e hora da saída;
- cliente;
- telefone;
- data prevista de retorno;
- produtos;
- tamanho;
- cor;
- quantidade;
- preço de referência;
- usuário responsável.

Ao final, apresentar:

Produtos enviados em condicional.

Não é necessária assinatura digital.

---

## 23.33 Condicional histórico

A impressão do Condicional deve utilizar os dados históricos da saída.

O preço de referência deve ser o valor preservado no Condicional.

Não utilizar o preço atual do Produto para reescrever o documento.

---

## 23.34 Condicional após retornos

Quando o Condicional possuir retornos parciais, a impressão de detalhes atuais deve permitir identificar:

- produtos originais;
- produtos comprados;
- produtos devolvidos;
- produtos ainda com o cliente.

O sistema deve deixar clara a situação atual.

---

## 23.35 Impressão da Troca

A Troca deve seguir as regras específicas do módulo Trocas.

O documento deve apresentar:

- identificação da loja;
- número da Troca;
- data e hora;
- cliente;
- Venda original;
- produtos entregues pelo cliente;
- produtos recebidos pelo cliente;
- crédito considerado;
- diferença paga ou devolvida;
- formas de pagamento;
- usuário responsável.

Não é necessária assinatura digital.

---

## 23.36 Valores da Troca

Os valores apresentados no documento da Troca devem utilizar os valores históricos oficiais da operação.

O crédito deve utilizar o valor líquido histórico dos itens entregues.

A diferença deve utilizar o valor confirmado da Troca.

Não utilizar preços atuais para recalcular documento antigo.

---

## 23.37 Exportação do Catálogo em PDF

O Catálogo deve permitir exportação em PDF conforme as regras oficiais do módulo Catálogo.

O documento deve apresentar a identificação da loja.

O PDF deve considerar:

- busca;
- filtros;
- ordenação

aplicados à consulta.

Somente produtos disponíveis podem ser incluídos.

---

## 23.38 Conteúdo do PDF do Catálogo

O PDF do Catálogo pode apresentar:

- logo;
- Nome da loja;
- foto do Produto;
- Nome do Produto;
- Marca;
- preço de venda;
- tamanho;
- cor;
- Disponível;
- Última unidade.

O PDF não deve apresentar:

- custo;
- margem;
- quantidade exata;
- valor financeiro do Estoque.

---

## 23.39 PDFs de Relatórios

Todo Relatório exportado em PDF deve apresentar:

- identificação da loja;
- tipo do Relatório;
- período, quando aplicável;
- filtros aplicados;
- data e hora da geração;
- usuário responsável pela geração;
- número da página.

O conteúdo deve respeitar o perfil do usuário autenticado.

---

## 23.40 Identificação do Relatório

O título deve identificar claramente o Relatório.

Exemplos:

RELATÓRIO DE VENDAS.

RELATÓRIO DE CREDIÁRIO.

RELATÓRIO DE CONTAS A PAGAR.

RELATÓRIO DE ESTOQUE.

RELATÓRIO DE LUCRO.

Não utilizar título genérico:

Relatório.

---

## 23.41 Período do Relatório

Quando o Relatório utilizar período, o PDF deve apresentar o período aplicado.

Exemplo:

Período:
01/07/2026 a 31/07/2026.

Quando o filtro não utilizar período, não inventar uma faixa de datas.

---

## 23.42 Filtros aplicados

O PDF deve apresentar os filtros relevantes aplicados.

Exemplo:

Período:
01/07/2026 a 31/07/2026.

Marca:
Nike.

Categoria:
Tênis.

Usuário:
Mauro.

Não é necessário apresentar filtros sem valor selecionado.

---

## 23.43 Data e hora de geração do Relatório

O PDF deve apresentar a data e hora da geração.

Exemplo:

Gerado em:
14/07/2026 às 15:30.

Essa data não substitui as datas históricas dos registros do Relatório.

---

## 23.44 Usuário que gerou o Relatório

O PDF deve apresentar o usuário autenticado responsável pela geração.

Exemplo:

Gerado por:
Mauro.

O usuário deve ser obtido da sessão autenticada e do cadastro persistido.

Não confiar em nome enviado pelo navegador.

---

## 23.45 Número de página

Relatórios PDF com várias páginas devem apresentar numeração de página.

Exemplo:

Página 1 de 5.

A numeração deve permanecer consistente.

---

## 23.46 Permissões nos PDFs

Os PDFs devem respeitar as mesmas permissões das APIs e telas.

Operador não pode receber em PDF:

- lucro;
- margem;
- valor financeiro total do Estoque.

Relatório de Lucro é exclusivo do Administrador.

A geração do PDF deve validar o perfil no backend.

Não gerar todos os dados e apenas escondê-los visualmente.

---

## 23.47 Exportação em Excel

Os Relatórios analíticos devem permitir exportação em Excel conforme as regras do módulo Relatórios.

O Excel possui finalidade tabular e analítica.

Não é necessário reproduzir o layout visual dos PDFs.

---

## 23.48 Estrutura do Excel

A exportação em Excel deve apresentar:

- título do Relatório;
- data e hora da geração;
- filtros aplicados;
- cabeçalho das colunas;
- dados tabulares.

A estrutura deve permanecer clara para uso em planilha.

---

## 23.49 Valores numéricos no Excel

Valores numéricos devem ser exportados como números quando tecnicamente possível.

Exemplo:

Valor:
1250,90 como valor numérico da planilha.

Não exportar todo valor financeiro exclusivamente como texto:

R$ 1.250,90.

A formatação monetária pode ser aplicada na célula.

O dado deve continuar utilizável em:

- soma;
- média;
- fórmula;
- filtro.

---

## 23.50 Datas no Excel

Datas devem ser exportadas como datas quando tecnicamente possível.

A célula pode apresentar:

14/07/2026.

O valor deve permitir ordenação e filtros de data da planilha.

Não exportar datas válidas exclusivamente como texto quando a biblioteca utilizada permitir tipo de data.

---

## 23.51 Data e hora no Excel

Campos com timestamp devem permitir representação de data e hora.

Exemplo visual:

14/07/2026 15:30.

O sistema deve converter o timestamp para America/Sao_Paulo antes da exportação destinada ao usuário.

---

## 23.52 Permissões no Excel

A exportação em Excel deve respeitar o perfil do usuário.

Operador não pode receber colunas ou resumos com:

- lucro;
- margem;
- valor financeiro total do Estoque.

O backend deve gerar o conteúdo permitido ao usuário autenticado.

---

## 23.53 Nome dos arquivos

Os arquivos gerados devem possuir nomes claros e padronizados.

Exemplos:

venda-000123.pdf

condicional-000045.pdf

troca-000012.pdf

catalogo-2026-07-14.pdf

relatorio-vendas-2026-07-01-a-2026-07-31.pdf

relatorio-vendas-2026-07-01-a-2026-07-31.xlsx

O padrão pode utilizar caracteres seguros para arquivos.

---

## 23.54 Dados pessoais no nome do arquivo

Não incluir dados pessoais desnecessários no nome do arquivo.

Não utilizar, por padrão:

- CPF;
- CNPJ de cliente;
- telefone;
- e-mail;
- endereço;
- nome completo do cliente.

O identificador da operação deve ser priorizado.

---

## 23.55 Arquivo de Venda

O PDF de Venda deve utilizar padrão equivalente a:

venda-NUMERO.pdf.

Exemplo:

venda-000123.pdf.

O número deve ser o número oficial da Venda.

---

## 23.56 Arquivo de Condicional

O PDF do Condicional deve utilizar padrão equivalente a:

condicional-NUMERO.pdf.

Exemplo:

condicional-000045.pdf.

---

## 23.57 Arquivo de Troca

O PDF da Troca deve utilizar padrão equivalente a:

troca-NUMERO.pdf.

Exemplo:

troca-000012.pdf.

---

## 23.58 Arquivo de Catálogo

O PDF do Catálogo deve utilizar padrão equivalente a:

catalogo-AAAA-MM-DD.pdf.

A data pode representar a data operacional da geração.

Exemplo:

catalogo-2026-07-14.pdf.

---

## 23.59 Arquivos de Relatórios

Os arquivos de Relatórios devem identificar:

- tipo do Relatório;
- período, quando aplicável;
- extensão.

Exemplo:

relatorio-vendas-2026-07-01-a-2026-07-31.pdf.

relatorio-vendas-2026-07-01-a-2026-07-31.xlsx.

Quando não existir período, utilizar nome compatível com a finalidade do Relatório sem inventar datas.

---

## 23.60 Visualização para impressão

O sistema pode utilizar visualização preparada para impressão pelo navegador.

A tela de impressão deve apresentar somente o conteúdo necessário ao documento.

Elementos operacionais da interface não devem aparecer desnecessariamente.

Exemplos a ocultar na impressão:

- menu lateral;
- botões de ação;
- campo de busca;
- navegação;
- Central de Alertas.

---

## 23.61 Impressão pelo navegador

A impressão física pode utilizar o mecanismo padrão de impressão do navegador.

O navegador pode permitir seleção de:

- impressora;
- tamanho de papel;
- orientação;
- número de cópias.

Essas escolhas físicas não alteram os dados oficiais da operação.

---

## 23.62 Fonte autoritativa dos documentos oficiais

Documentos oficiais exportados devem utilizar dados validados pelo backend.

O backend deve recuperar os dados persistidos correspondentes à operação ou Relatório.

O sistema não deve confiar em HTML visível alterado pelo usuário como fonte autoritativa para gerar PDF oficial.

---

## 23.63 Manipulação do frontend

Alterações locais no HTML, JavaScript ou DOM do navegador não devem permitir gerar documento oficial com valores financeiros diferentes dos persistidos.

Exemplo:

Venda oficial:
R$ 100,00.

Usuário altera visualmente o DOM para:
R$ 10,00.

O PDF oficial da Venda deve continuar utilizando:
R$ 100,00.

---

## 23.64 Identificadores enviados pelo navegador

O navegador pode informar qual operação deseja consultar ou exportar.

O backend deve validar:

- existência;
- loja;
- autorização;
- situação compatível.

O navegador não deve enviar autoritativamente o conteúdo completo do documento financeiro para que o servidor apenas converta em PDF.

---

## 23.65 Documentos e isolamento por loja

Todo documento deve utilizar somente dados da loja autenticada.

O sistema deve impedir geração de documento de operação pertencente a outra loja.

A validação deve ocorrer no backend.

---

## 23.66 Sessão expirada

Quando a sessão expirar durante a geração de documento protegido, o sistema deve seguir o fluxo oficial de autenticação.

Não gerar documento restrito para sessão inválida.

Dados administrativos já renderizados devem seguir as regras de limpeza de sessão.

---

## 23.67 Falha na geração

Quando ocorrer erro durante a geração de PDF ou Excel:

- informar a falha;
- não apresentar arquivo incompleto como válido;
- permitir nova tentativa.

Quando possível, arquivos temporários incompletos devem ser descartados.

---

## 23.68 Estado de processamento

Durante a geração de arquivo, a interface deve apresentar estado de processamento.

Exemplo:

Gerando PDF...

ou:

Gerando Excel...

O sistema deve evitar múltiplos acionamentos simultâneos desnecessários.

---

## 23.69 Reimpressão e auditoria

A simples reimpressão não altera a operação histórica.

Quando a arquitetura de auditoria geral suportar essa informação, o sistema pode registrar:

- documento reimpresso;
- data e hora;
- usuário.

Não é necessário criar módulo específico de histórico de impressões neste momento.

---

## 23.70 Regras gerais de Impressões e Documentos Gerados

O sistema deve:

- utilizar a logo da loja quando cadastrada;
- apresentar sempre o Nome da loja;
- utilizar dados da loja conforme as preferências de impressão;
- apresentar Nome da loja quando não existir logo;
- não apresentar imagem quebrada;
- preservar a data e hora histórica da operação;
- permitir identificação discreta da data de reimpressão;
- utilizar America/Sao_Paulo na apresentação;
- apresentar datas em DD/MM/AAAA;
- apresentar data e hora no padrão brasileiro;
- apresentar valores monetários em padrão brasileiro;
- apresentar usuário responsável;
- utilizar Atendido por na Venda;
- utilizar Usuário responsável em Condicional e Troca;
- permitir comprovante simples de Venda;
- apresentar produtos e atributos históricos;
- apresentar preço praticado;
- apresentar descontos e acréscimos;
- apresentar total;
- apresentar todas as formas de pagamento;
- apresentar parcelas do Crediário;
- apresentar valor recebido em Dinheiro quando aplicável;
- apresentar troco;
- utilizar mensagem de rodapé configurada;
- preservar o comprovante da Venda original;
- não reescrever comprovante original após Cancelamento;
- não reescrever comprovante original após Devolução;
- não reescrever comprovante original após Troca;
- permitir impressão dos detalhes atuais da Venda;
- diferenciar comprovante original e detalhes atuais;
- seguir as regras de impressão do Condicional;
- seguir as regras de impressão da Troca;
- permitir Catálogo em PDF;
- permitir Relatórios em PDF;
- identificar o tipo do Relatório;
- apresentar período;
- apresentar filtros aplicados;
- apresentar data e hora de geração;
- apresentar usuário que gerou;
- numerar páginas;
- respeitar permissões do usuário nos PDFs;
- permitir Excel para Relatórios analíticos;
- exportar números como números quando possível;
- exportar datas como datas quando possível;
- converter timestamps para America/Sao_Paulo;
- respeitar permissões no Excel;
- utilizar nomes de arquivos padronizados;
- não incluir dados pessoais desnecessários no nome dos arquivos;
- permitir visualização preparada para impressão;
- permitir impressão pelo navegador;
- utilizar o backend como fonte autoritativa dos documentos oficiais;
- não confiar em DOM alterado;
- validar identificadores;
- respeitar isolamento por loja;
- respeitar sessão e autorização;
- tratar falhas de geração;
- apresentar estado de processamento;
- preservar a operação histórica durante reimpressões.

# 24. GARANTIAS

## 24.1 Finalidade do módulo Garantias

O módulo Garantias é destinado ao controle de produtos vendidos que apresentem defeito ou problema posterior à venda e necessitem de análise, reparo, encaminhamento ao Fornecedor ou outra solução comercial válida.

A Garantia é uma operação distinta de:

- Troca normal;
- Devolução comercial;
- Cancelamento de Venda.

O sistema deve preservar o vínculo entre:

- Venda original;
- Cliente;
- Produto;
- Solicitação de Garantia;
- Fornecedor, quando aplicável;
- Solução adotada.

A Garantia não deve reescrever a Venda original.

---

## 24.2 Origem obrigatória em uma Venda

Toda Garantia deve possuir uma Venda existente como origem.

O fluxo principal deve partir de:

Histórico de Vendas.

Ver Detalhes.

SOLICITAR GARANTIA.

O backend deve validar a Venda correspondente.

Não permitir criação de Garantia sem vínculo com Venda.

---

## 24.3 Vínculo persistente com a Venda

A Garantia deve utilizar o identificador persistente da Venda como vínculo autoritativo.

Não utilizar somente:

- número visual da Venda;
- nome do Cliente;
- data da Venda

como vínculo histórico.

A Venda original deve permanecer preservada.

---

## 24.4 Prazo da Garantia

A Garantia não possui prazo máximo fixo definido pelo sistema.

O sistema não deve bloquear automaticamente a abertura de Garantia em razão da quantidade de dias transcorridos desde a Venda.

O usuário pode registrar a solicitação para análise independentemente do tempo transcorrido.

---

## 24.5 Dias transcorridos desde a Venda

A tela deve informar quantos dias se passaram desde a data operacional da Venda.

Exemplo:

Venda realizada há 45 dias.

A informação possui finalidade operacional.

A quantidade de dias não deve produzir recusa automática da Garantia.

O cálculo deve utilizar a data operacional America/Sao_Paulo.

---

## 24.6 Análise do prazo pelo usuário

A ausência de prazo fixo no sistema não representa aprovação automática da Garantia.

O usuário responsável pode utilizar:

- data da Venda;
- tipo de Produto;
- descrição do defeito;
- estado físico;
- orientação do Fornecedor

como informações para análise.

A decisão deve ser registrada por meio do fluxo da Garantia.

---

## 24.7 Cliente vinculado

A Garantia deve permanecer vinculada ao Cliente histórico da Venda.

Quando a Venda possuir Cliente cadastrado, utilizar o identificador persistente do Cliente.

A alteração futura dos dados do Cliente não transfere a Garantia para outro Cliente.

---

## 24.8 Garantia de Venda com Cliente Padrão

Venda vinculada ao Cliente Padrão pode originar Garantia.

A existência de Cliente Padrão não deve impedir o registro da solicitação quando a Venda e o Produto puderem ser identificados.

Nesse caso, o sistema deve permitir registrar informações de contato para acompanhamento.

---

## 24.9 Contato em Garantia de Cliente Padrão

Quando a Venda utilizar Cliente Padrão, a Garantia pode exigir:

- nome para contato;
- telefone para contato.

Essas informações pertencem à Garantia.

O registro não deve alterar automaticamente o Cliente Padrão.

O sistema não deve transformar silenciosamente o contato informado em novo Cliente cadastrado.

---

## 24.10 Produto elegível para Garantia

Somente Produtos pertencentes à Venda original podem ser selecionados para Garantia.

O sistema deve apresentar os itens históricos da Venda.

Devem ser considerados:

- Produto;
- código histórico;
- atributos;
- quantidade originalmente vendida;
- quantidade já devolvida;
- quantidade já trocada;
- quantidade vinculada a Garantias abertas.

---

## 24.11 Quantidade elegível

A quantidade em Garantia não pode superar o saldo elegível do item.

Fórmula conceitual:

Quantidade elegível =
Quantidade vendida
- Quantidade devolvida
- Quantidade trocada
- Quantidade já vinculada a Garantias abertas.

O backend deve recalcular o saldo antes da confirmação.

---

## 24.12 Garantia parcial de quantidade

O sistema deve permitir Garantia de apenas parte da quantidade vendida.

Exemplo:

Venda:
3 unidades.

Garantia:
1 unidade.

As outras 2 unidades permanecem fora da Garantia.

O sistema deve preservar a quantidade exata vinculada.

---

## 24.13 Quantidade válida

A quantidade em Garantia deve ser:

- numérica;
- finita;
- inteira;
- maior que zero.

Não permitir:

- zero;
- valor negativo;
- quantidade fracionada;
- NaN;
- infinito.

A validação deve ocorrer no backend.

---

## 24.14 Categoria do defeito

A Garantia deve possuir categoria do defeito.

As categorias iniciais são:

- Costura;
- Cola;
- Solado;
- Tecido;
- Zíper;
- Estampa;
- Acessório;
- Outro.

A categoria deve ser persistida.

---

## 24.15 Descrição obrigatória do defeito

Toda Garantia deve possuir descrição do defeito.

Exemplo:

Costura abriu na lateral após duas utilizações.

Não permitir Garantia sem descrição válida.

A descrição deve ser tratada como texto simples.

---

## 24.16 Categoria Outro

Quando a categoria selecionada for Outro, a descrição continua sendo obrigatória.

O usuário deve explicar o defeito ou problema identificado.

Não criar Garantia com categoria Outro e descrição vazia.

---

## 24.17 Fotos da Garantia

A Garantia deve permitir anexar fotos do defeito.

O sistema deve permitir várias fotos.

O limite inicial é de até 5 fotos por Garantia.

---

## 24.18 Formatos das fotos

São permitidos:

- JPG;
- JPEG;
- PNG;
- WEBP.

Arquivos fora dos formatos permitidos devem ser rejeitados.

A validação deve ocorrer no backend.

---

## 24.19 Fotos e segurança

O sistema deve validar o arquivo recebido.

Não confiar somente na extensão informada pelo navegador.

As fotos devem permanecer vinculadas à Garantia correspondente.

A existência de foto não substitui a descrição obrigatória do defeito.

---

## 24.20 Situação física do Produto

Ao abrir a Garantia, o sistema deve registrar a situação física do Produto.

As opções são:

- Produto recebido pela loja;
- Produto permanece com o Cliente.

A situação deve ser persistida.

---

## 24.21 Produto recebido pela loja

Quando o Produto for recebido fisicamente pela loja, o sistema deve registrar:

- data e hora do recebimento;
- usuário responsável.

O Produto deve passar a ser controlado no fluxo da Garantia.

Ele não retorna ao Estoque disponível.

---

## 24.22 Produto permanece com o Cliente

Quando o Produto permanecer com o Cliente, a Garantia pode continuar aberta ou em análise.

O sistema deve registrar que a peça ainda não foi recebida fisicamente pela loja.

O Produto não deve ser tratado como item disponível no Estoque da loja.

---

## 24.23 Envio ao Fornecedor

O Produto somente pode ser marcado como Enviado ao Fornecedor quando tiver sido recebido fisicamente pela loja.

O sistema deve impedir envio ao Fornecedor de Produto ainda marcado como em posse do Cliente.

A validação deve ocorrer no backend.

---

## 24.24 Estoque e Garantia

Produto recebido para Garantia não deve retornar ao Estoque disponível.

O sistema deve controlar conceitualmente a quantidade:

Em Garantia.

Essa quantidade representa Produto fora do estoque comercial normal.

---

## 24.25 Produto em Garantia não disponível para Venda

Produto recebido em Garantia não pode ser:

- vendido;
- reservado em Condicional;
- exibido como disponível no Catálogo.

O Produto defeituoso não deve aumentar o Estoque disponível.

---

## 24.26 Situações da Garantia

As situações oficiais são:

- Aberta;
- Em análise;
- Enviada ao Fornecedor;
- Aprovada;
- Recusada;
- Resolvida;
- Cancelada.

A situação deve representar o estágio atual da Garantia.

---

## 24.27 Garantia Aberta

A situação Aberta representa Garantia registrada e ainda não submetida a uma decisão final.

Pode existir:

- Produto com o Cliente;
- Produto recebido pela loja.

A Garantia Aberta pode receber novas informações e seguir para análise.

---

## 24.28 Garantia Em análise

A situação Em análise representa Garantia em avaliação pela loja.

O Produto pode estar:

- na loja;
- ainda com o Cliente, quando a análise inicial puder ocorrer sem recebimento físico.

O sistema deve preservar o histórico da mudança de situação.

---

## 24.29 Garantia Enviada ao Fornecedor

A situação Enviada ao Fornecedor representa Produto encaminhado ao Fornecedor para análise ou solução.

O Produto deve estar fisicamente recebido pela loja antes do envio.

O envio deve possuir registro próprio.

---

## 24.30 Dados do envio ao Fornecedor

Ao enviar o Produto ao Fornecedor, registrar:

- Fornecedor;
- data e hora do envio;
- usuário responsável;
- observações;
- número de protocolo, quando existir.

O protocolo é opcional.

---

## 24.31 Seleção do Fornecedor

O usuário deve selecionar o Fornecedor responsável pelo encaminhamento da Garantia.

O sistema pode sugerir o Fornecedor histórico relacionado ao Produto quando existir vínculo confiável.

A sugestão não deve obrigar o uso desse Fornecedor.

O usuário pode selecionar outro Fornecedor ativo.

---

## 24.32 Motivo para permitir outro Fornecedor

Um Produto pode ter sido adquirido de diferentes Fornecedores ao longo do tempo.

O sistema pode não possuir rastreabilidade física por lote suficiente para determinar com certeza o Fornecedor da unidade vendida.

Por esse motivo, o Fornecedor da Garantia deve ser selecionado pelo usuário.

O sistema não deve inventar a origem física da peça.

---

## 24.33 Garantia Aprovada

A situação Aprovada representa Garantia aceita para solução.

A aprovação deve registrar:

- data e hora;
- usuário responsável;
- observações, quando aplicável.

A aprovação ainda pode exigir a execução da solução correspondente.

---

## 24.34 Soluções da Garantia aprovada

As soluções permitidas são:

- Troca;
- Devolução do valor;
- Reparo;
- Substituição pelo Fornecedor.

O sistema não deve possuir Crédito para o Cliente como solução oficial neste momento.

---

## 24.35 Troca por Garantia

Quando a solução for Troca, o sistema deve utilizar o fluxo oficial do módulo Trocas.

A Troca deve preservar vínculo com a Garantia.

O sistema deve identificar que a origem comercial da Troca foi uma Garantia aprovada.

As regras de Estoque, diferença financeira e rastreabilidade continuam sendo aplicadas.

---

## 24.36 Garantia e prazo normal de Troca

Troca originada de Garantia aprovada não deve ser bloqueada pelo prazo normal de 30 dias da Troca comercial.

A Garantia aprovada representa uma origem própria e autorizada para a solução.

O sistema deve diferenciar:

- Troca comercial normal;
- Troca originada de Garantia.

---

## 24.37 Devolução do valor por Garantia

Quando a solução for Devolução do valor, o sistema deve utilizar o fluxo financeiro oficial de Devolução.

A operação deve preservar vínculo com a Garantia.

O valor deve utilizar os valores históricos autoritativos da Venda.

Não utilizar o preço atual do Produto.

---

## 24.38 Garantia e Devolução

A Devolução originada de Garantia aprovada deve seguir as regras de:

- valor líquido histórico;
- pagamentos mistos;
- Crediário;
- cartão;
- alocações;
- conciliação manual de registros antigos inseguros.

A Garantia não deve possuir cálculo financeiro paralelo.

---

## 24.39 Reparo

Quando a solução for Reparo, o sistema deve registrar:

- data da conclusão do reparo;
- descrição ou observação do reparo;
- usuário responsável.

O Reparo não gera Venda.

O Reparo não gera receita.

O Reparo não gera pagamento automaticamente.

---

## 24.40 Produto reparado

Após o Reparo, o Produto deve ser devolvido ao Cliente.

O sistema deve registrar a entrega física ao Cliente.

A Garantia somente deve assumir situação Resolvida após a conclusão válida da solução e entrega correspondente quando necessária.

---

## 24.41 Substituição pelo Fornecedor

Quando o Fornecedor substituir o Produto defeituoso por outra peça, o sistema deve registrar a substituição.

Devem ser identificáveis:

- Produto defeituoso enviado;
- Produto substituto recebido;
- data;
- Fornecedor;
- usuário responsável.

---

## 24.42 Destino do Produto substituto

O Produto substituto recebido do Fornecedor pode possuir dois destinos:

- Entrega direta ao Cliente;
- Entrada no Estoque.

O usuário deve informar o destino.

---

## 24.43 Substituição com entrega direta ao Cliente

Quando o Produto substituto for entregue diretamente ao Cliente:

- não adicionar o Produto ao Estoque disponível;
- registrar o recebimento do substituto;
- registrar a entrega ao Cliente;
- concluir a solução da Garantia.

Não gerar Venda.

---

## 24.44 Substituição com Entrada no Estoque

Quando o Produto substituto for destinado ao Estoque, a operação deve gerar Entrada rastreável.

A Entrada deve identificar como origem:

Substituição de Garantia pelo Fornecedor.

O sistema deve registrar:

- Produto;
- quantidade;
- Fornecedor;
- Garantia de origem;
- data e hora;
- usuário.

---

## 24.45 Custo do Produto substituto

Quando o Produto substituto for destinado ao Estoque, o custo deve ser informado ou obtido de forma autoritativa conforme a operação.

O sistema não deve inventar custo.

Quando a substituição não possuir novo custo financeiro, o usuário deve confirmar o custo cadastral aplicável antes da Entrada, conforme as regras de Produtos e Entradas.

---

## 24.46 Garantia Recusada

A situação Recusada representa Garantia não aprovada.

A recusa exige motivo obrigatório.

O sistema deve registrar:

- motivo;
- data e hora;
- usuário responsável.

---

## 24.47 Produto de Garantia recusada

Quando a Garantia for recusada e o Produto estiver na loja, ele deve permanecer vinculado à Garantia até ser devolvido fisicamente ao Cliente.

A situação Recusada não significa entrega automática ao Cliente.

---

## 24.48 Entrega do Produto recusado ao Cliente

Ao entregar o Produto ao Cliente, registrar:

- data e hora;
- usuário responsável.

Após a entrega física válida, a Garantia pode assumir situação Resolvida.

---

## 24.49 Garantia recusada com Produto em posse do Cliente

Quando o Produto nunca tiver sido recebido pela loja e permanecer com o Cliente, a recusa pode ser registrada.

A Garantia pode ser Resolvida após a conclusão da comunicação e do fluxo operacional definido.

O sistema deve preservar que o Produto permaneceu com o Cliente.

---

## 24.50 Garantia Resolvida

A situação Resolvida representa Garantia com solução ou encerramento operacional concluído.

Pode decorrer de:

- Troca concluída;
- Devolução concluída;
- Reparo e entrega ao Cliente;
- Substituição pelo Fornecedor e entrega;
- Recusa concluída.

A situação Resolvida deve preservar a solução adotada.

---

## 24.51 Garantia Cancelada

A situação Cancelada representa cancelamento formal da solicitação de Garantia.

O cancelamento exige motivo.

O sistema deve registrar:

- motivo;
- data e hora;
- usuário responsável.

A Garantia não deve ser excluída.

---

## 24.52 Cancelamento da Garantia

O cancelamento somente deve ocorrer quando não existir operação vinculada incompatível com a reversão.

Exemplo de situações que devem ser verificadas:

- Produto enviado ao Fornecedor;
- Troca já concluída;
- Devolução financeira concluída;
- Reparo concluído;
- Produto substituto recebido.

O backend deve validar os vínculos antes do cancelamento.

---

## 24.53 Garantia e quantidade elegível da Venda

Enquanto uma Garantia permanecer Aberta, Em análise, Enviada ao Fornecedor ou Aprovada sem solução final, a quantidade correspondente deve permanecer considerada como vinculada a Garantia aberta.

Essa quantidade não pode ser utilizada simultaneamente em:

- nova Devolução;
- nova Troca;
- outra Garantia.

---

## 24.54 Garantia resolvida por Troca

Quando a Garantia for resolvida por Troca, a quantidade correspondente passa a ser considerada conforme o histórico da Troca.

O sistema deve impedir dupla utilização da mesma quantidade em outra operação.

---

## 24.55 Garantia resolvida por Devolução

Quando a Garantia for resolvida por Devolução, a quantidade correspondente passa a ser considerada conforme o histórico da Devolução.

Não permitir nova operação sobre a mesma quantidade além do saldo elegível da Venda.

---

## 24.56 Garantia resolvida por Reparo

Quando a Garantia for resolvida por Reparo, a quantidade vendida permanece historicamente vendida.

O Reparo não reduz a quantidade líquida vendida.

Não tratar Reparo como Devolução ou Troca.

---

## 24.57 Garantia resolvida por Substituição do Fornecedor

Quando a solução for Substituição pelo Fornecedor, a Venda original permanece preservada.

A Garantia deve registrar a substituição.

Não criar nova Venda quando o Produto substituto for entregue diretamente ao Cliente sem diferença comercial.

---

## 24.58 Número da Garantia

Cada Garantia deve possuir número automático por loja.

O número deve ser definido pelo backend.

O usuário não pode alterar manualmente o número.

---

## 24.59 Data e hora da Garantia

A Garantia deve registrar a data e hora da criação.

Novos timestamps devem ser armazenados em UTC com offset explícito.

A apresentação deve utilizar America/Sao_Paulo.

---

## 24.60 Usuário responsável pela abertura

A Garantia deve registrar o usuário autenticado responsável pela abertura.

O usuário deve ser obtido da sessão e do cadastro persistido.

Administrador e Operador podem abrir Garantias.

---

## 24.61 Histórico de alterações

A Garantia deve preservar histórico de suas principais ocorrências.

Entre elas:

- abertura;
- recebimento físico;
- início da análise;
- envio ao Fornecedor;
- aprovação;
- recusa;
- solução;
- entrega ao Cliente;
- cancelamento;
- resolução.

Cada ocorrência relevante deve registrar:

- data e hora;
- usuário responsável.

---

## 24.62 Fotos no histórico

As fotos anexadas devem permanecer vinculadas à Garantia.

O sistema deve permitir visualizar as fotos nos detalhes.

A exclusão ou substituição de fotos após a Garantia avançar deve seguir regras de rastreabilidade compatíveis.

Não apagar evidências silenciosamente quando já utilizadas na análise.

---

## 24.63 Cards da tela de Garantias

A tela de Garantias deve apresentar os seguintes indicadores:

- Garantias abertas;
- Em análise;
- Com Fornecedor;
- Aguardando entrega ao Cliente.

Os indicadores devem utilizar o estado atual das Garantias.

---

## 24.64 Garantias abertas

O indicador Garantias abertas deve representar Garantias ainda não Resolvidas ou Canceladas que estejam em estágio inicial compatível.

A interface deve utilizar critérios documentados e consistentes.

Não contar Garantia Resolvida.

---

## 24.65 Em análise

O indicador Em análise deve representar Garantias na situação correspondente.

A quantidade deve utilizar os registros atuais da loja.

---

## 24.66 Com Fornecedor

O indicador Com Fornecedor deve representar Garantias enviadas ao Fornecedor e ainda não concluídas.

O sistema deve considerar a situação e o histórico do envio.

---

## 24.67 Aguardando entrega ao Cliente

O indicador Aguardando entrega ao Cliente deve representar Garantias cuja solução ou recusa esteja concluída, mas ainda exista Produto que deva ser entregue fisicamente ao Cliente.

Exemplos:

- Produto reparado;
- Produto substituto recebido;
- Produto de Garantia recusada.

---

## 24.68 Busca de Garantias

A tela deve permitir busca por:

- número da Garantia;
- número da Venda;
- Cliente;
- CPF;
- telefone;
- Produto;
- Código.

A busca deve utilizar normalização quando aplicável.

---

## 24.69 Filtros

A tela deve permitir filtros por:

- período;
- situação;
- Fornecedor.

Os filtros podem ser utilizados em conjunto.

O período deve utilizar a data operacional oficial.

---

## 24.70 Listagem de Garantias

A listagem deve apresentar:

- número;
- data;
- Cliente;
- Produto;
- defeito;
- situação;
- Fornecedor;
- ação.

A ação principal deve ser:

VER DETALHES.

---

## 24.71 Detalhes da Garantia

Os detalhes devem apresentar, no mínimo:

- número;
- Venda de origem;
- Cliente;
- contato, quando aplicável;
- Produto;
- quantidade;
- data da Venda;
- dias transcorridos desde a Venda;
- categoria do defeito;
- descrição;
- fotos;
- situação física;
- situação da Garantia;
- Fornecedor;
- protocolo;
- histórico;
- solução adotada.

---

## 24.72 Garantia na ficha do Cliente

A ficha do Cliente deve permitir visualizar Garantias vinculadas.

Devem ser identificáveis:

- abertas;
- em análise;
- com Fornecedor;
- aprovadas;
- recusadas;
- resolvidas;
- canceladas.

A ficha deve permitir acesso aos detalhes.

---

## 24.73 Garantia no Histórico de Vendas

Os detalhes da Venda original devem identificar as Garantias vinculadas.

Apresentar, conforme aplicável:

- número da Garantia;
- Produto;
- quantidade;
- data;
- situação;
- solução.

A Garantia não deve apagar a Venda original.

---

## 24.74 Alerta de Garantia com Fornecedor sem atualização

A Central de Alertas deve gerar alerta quando uma Garantia permanecer na situação:

Enviada ao Fornecedor

por 7 dias consecutivos sem nenhuma nova atualização registrada no histórico da Garantia.

O prazo possui finalidade operacional de acompanhamento.

O alerta não representa recusa, atraso legal ou responsabilidade automática do Fornecedor.

---

## 24.75 Início da contagem do prazo

A contagem inicial deve utilizar a data e hora do envio ao Fornecedor.

Exemplo:

Garantia enviada ao Fornecedor em:
01/08/2026 às 10:00.

Sem nova atualização registrada.

Ao completar 7 dias sem atualização, o alerta deve ficar ativo.

O cálculo deve utilizar a data e hora operacional em America/Sao_Paulo.

---

## 24.76 Reinício da contagem após atualização

Quando uma nova atualização válida for registrada na Garantia enquanto ela permanecer com o Fornecedor, a contagem de 7 dias deve reiniciar.

Exemplo:

Enviada ao Fornecedor:
01/08.

Atualização registrada:
05/08.

Nova contagem:
a partir de 05/08.

Se não houver nova atualização por 7 dias, o alerta deve voltar a ser gerado.

---

## 24.77 Atualização válida da Garantia

Para fins de reinício da contagem, deve existir uma ocorrência real registrada no histórico da Garantia.

Exemplos:

- retorno do Fornecedor;
- nova observação de acompanhamento;
- atualização de protocolo;
- informação de análise;
- mudança válida de situação;
- registro de contato com o Fornecedor.

A simples abertura da tela da Garantia não representa atualização.

Marcar o alerta como lido não reinicia o prazo.

---

## 24.78 Conteúdo do alerta de Garantia com Fornecedor

O alerta deve apresentar, conforme aplicável:

- número da Garantia;
- Cliente;
- Produto;
- Fornecedor;
- quantidade de dias sem atualização.

Exemplo:

Garantia sem atualização

Garantia nº 125

Fornecedor Nike

8 dias sem atualização

A ação principal deve abrir os detalhes da Garantia.

---

## 24.79 Prioridade do alerta

O alerta de Garantia com Fornecedor sem atualização deve possuir prioridade:

ATENÇÃO.

Ele deve ser apresentado junto aos demais alertas operacionais de Atenção.

Não classificar automaticamente como alerta Crítico.

---

## 24.80 Resolução automática do alerta

O alerta deve deixar de existir quando:

- uma nova atualização válida for registrada;
- a Garantia deixar a situação Enviada ao Fornecedor;
- a Garantia for Resolvida;
- a Garantia for Cancelada.

O usuário não precisa resolver o alerta manualmente.

Marcar como lido não remove a situação operacional.

---

## 24.81 Virada do dia e atualização do alerta

A Central de Alertas deve recalcular o prazo das Garantias na virada do dia operacional.

Também deve recalcular:

- ao entrar no sistema;
- ao abrir a Central de Alertas;
- após atualização de Garantia;
- ao recuperar foco ou visibilidade da aplicação.

O sistema não precisa consultar o servidor continuamente em intervalos curtos.

---

## 24.82 Garantia aguardando entrega ao Cliente

Garantia com Produto pronto, substituído ou recusado aguardando entrega física ao Cliente deve gerar alerta.

O alerta deve permitir abrir os detalhes da Garantia.

Após registrar a entrega, o alerta deve desaparecer automaticamente.

# 25. INVENTÁRIO

## 25.1 Finalidade do Inventário

O módulo Inventário é destinado à conferência física do Estoque da loja.

O Inventário deve permitir comparar:

- quantidade fisicamente esperada na loja;
- quantidade efetivamente contada.

Quando existirem divergências, a finalização do Inventário deve gerar Ajustes de Inventário rastreáveis.

O Inventário não deve funcionar como edição livre de Estoque.

O usuário informa a contagem física.

O backend calcula a posição esperada, identifica divergências e executa os ajustes correspondentes.

---

## 25.2 Acesso ao Inventário

Administrador e Operador podem acessar o módulo Inventário.

Ambos podem:

- iniciar Inventário;
- realizar contagem;
- alterar contagens enquanto o Inventário estiver Em andamento;
- salvar o andamento;
- finalizar Inventário;
- cancelar Inventário Em andamento.

As operações devem registrar o usuário autenticado responsável.

---

## 25.3 Tipos de Inventário

O sistema deve permitir:

- Inventário Geral;
- Inventário Parcial.

O tipo do Inventário deve ser persistido.

---

## 25.4 Inventário Geral

O Inventário Geral deve incluir todos os Produtos ativos elegíveis da loja no momento de sua abertura.

O conjunto de Produtos deve ser definido pelo backend.

O navegador não deve informar livremente a lista autoritativa de Produtos do Inventário Geral.

---

## 25.5 Inventário Parcial

O Inventário Parcial deve permitir selecionar o escopo antes de iniciar a contagem.

Os filtros iniciais podem incluir:

- Marca;
- Categoria;
- Gênero;
- Produto;
- Código.

Somente os Produtos elegíveis correspondentes ao escopo confirmado devem integrar o Inventário.

---

## 25.6 Escopo persistente do Inventário Parcial

O escopo do Inventário Parcial deve ser preservado.

Exemplo:

Inventário parcial.

Filtro:
Marca Nike.

O sistema deve registrar que o Inventário foi iniciado para o escopo Marca Nike.

Alterações futuras no cadastro da Marca ou do Produto não devem reescrever silenciosamente o escopo histórico do Inventário.

---

## 25.7 Produtos do Inventário

Ao iniciar o Inventário, o backend deve definir os Produtos pertencentes à operação.

Cada Produto incluído deve possuir registro próprio dentro do Inventário.

O conjunto histórico do Inventário deve permanecer preservado.

Produto cadastrado depois do início do Inventário não deve ser adicionado automaticamente ao Inventário já Em andamento.

---

## 25.8 Fotografia inicial do Estoque

Ao iniciar o Inventário, o sistema deve criar uma fotografia da posição de Estoque naquele momento.

Para cada Produto, preservar:

- Produto;
- Código;
- Estoque real registrado;
- quantidade reservada em Condicionais ativos;
- quantidade disponível;
- quantidade fisicamente esperada na loja.

A fotografia deve permanecer vinculada ao Inventário.

---

## 25.9 Estoque real na fotografia inicial

O Estoque real registrado na fotografia deve utilizar o estado persistido no momento da abertura do Inventário.

O navegador não deve informar autoritativamente o Estoque real inicial.

O backend deve obter o valor do estado persistido.

---

## 25.10 Quantidade reservada na fotografia inicial

A quantidade reservada deve considerar Condicionais ativos conforme as regras oficiais do módulo Condicional.

O sistema deve calcular a reserva por Produto.

Não confiar em quantidade reservada enviada pelo navegador.

---

## 25.11 Quantidade disponível na fotografia inicial

A quantidade disponível deve utilizar a regra oficial de Estoque.

Fórmula conceitual:

Quantidade disponível =
Estoque real - Quantidade reservada em Condicionais ativos.

A fotografia deve preservar o resultado correspondente ao momento de abertura do Inventário.

---

## 25.12 Quantidade fisicamente esperada na loja

A quantidade fisicamente esperada na loja deve representar a quantidade que deveria estar disponível fisicamente para contagem comercial.

Conceitualmente:

Quantidade física esperada =
Estoque real - Quantidade reservada em Condicionais ativos.

Produtos fisicamente controlados em fluxos próprios e fora do Estoque comercial normal devem seguir suas regras específicas.

---

## 25.13 Fotografia inicial imutável

A fotografia inicial do Inventário não deve ser reescrita após a abertura.

Vendas, Entradas, Condicionais, Trocas, Devoluções ou outras movimentações posteriores não alteram os valores históricos da fotografia inicial.

As movimentações posteriores devem ser consideradas separadamente na posição esperada da finalização.

---

## 25.14 Operação da loja durante o Inventário

O Inventário não deve bloquear automaticamente a operação da loja.

Durante Inventário Em andamento, o sistema pode continuar permitindo:

- Vendas;
- Condicionais;
- retorno de Condicionais;
- Entradas;
- Trocas;
- Devoluções;
- Devoluções ao Fornecedor;
- Garantias;
- demais movimentações válidas de Estoque.

O Inventário deve considerar as movimentações posteriores ao seu início.

---

## 25.15 Movimentações posteriores ao início

O sistema deve identificar as movimentações de Estoque válidas ocorridas após o início do Inventário.

As movimentações devem ser consideradas por Produto.

Exemplos:

- Venda;
- Entrada;
- Cancelamento;
- Condicional;
- retorno de Condicional;
- Troca;
- Devolução;
- Devolução ao Fornecedor;
- Ajustes válidos;
- operações de Garantia com efeito no Estoque comercial.

---

## 25.16 Posição esperada na finalização

Na finalização do Inventário, o backend deve recalcular a posição esperada de cada Produto.

Conceitualmente:

Posição esperada na finalização =
Fotografia inicial
+ Movimentações válidas posteriores ao início.

O cálculo deve utilizar as movimentações oficiais e seus efeitos líquidos.

---

## 25.17 Reservas na finalização

A posição física esperada na loja deve considerar as reservas válidas existentes no momento da finalização.

Exemplo:

Estoque real esperado:
10.

Quantidade atualmente reservada em Condicionais:
3.

Quantidade fisicamente esperada na loja:
7.

O sistema deve utilizar o estado persistido mais recente dentro da operação protegida de finalização.

---

## 25.18 Inventário e movimentações concorrentes

Como a loja permanece operando durante o Inventário, a finalização deve tratar movimentações concorrentes.

A validação final deve ocorrer dentro de mecanismo transacional compatível.

Uma movimentação de Estoque não pode ser ignorada por ocorrer simultaneamente à finalização do Inventário.

---

## 25.19 Tela de contagem

Para cada Produto do Inventário, a tela deve apresentar:

- Código;
- Produto;
- Marca;
- Cor;
- Tamanho;
- quantidade esperada;
- Quantidade contada.

Informações adicionais podem ser apresentadas quando úteis, desde que não prejudiquem a clareza da contagem.

---

## 25.20 Quantidade contada inicialmente vazia

O campo Quantidade contada deve iniciar vazio.

O sistema não deve preencher automaticamente a quantidade contada utilizando a quantidade esperada.

A ausência de valor representa:

Produto ainda não contado.

Zero informado explicitamente representa:

Produto contado fisicamente com quantidade zero.

Os dois estados devem ser distintos.

---

## 25.21 Produto não contado

Produto com campo Quantidade contada vazio deve ser considerado Não contado.

O sistema deve identificar claramente os Produtos ainda não contados.

A ausência de contagem não deve ser interpretada como zero.

---

## 25.22 Quantidade contada igual a zero

O usuário pode informar explicitamente:

0.

Nesse caso, o Produto foi contado e nenhuma unidade física foi localizada na loja.

O valor zero é uma contagem válida.

---

## 25.23 Validação da quantidade contada

A quantidade contada deve ser:

- numérica;
- finita;
- inteira;
- igual ou maior que zero.

Não permitir:

- valor negativo;
- quantidade fracionada;
- NaN;
- infinito;
- texto inválido.

A validação autoritativa deve ocorrer no backend.

---

## 25.24 Salvamento do andamento

O Inventário deve permitir salvar o andamento da contagem.

As quantidades já contadas devem permanecer persistidas.

O usuário pode sair da tela e retornar posteriormente.

O Inventário permanece Em andamento até sua finalização ou cancelamento formal.

---

## 25.25 Vários usuários na contagem

Administrador e Operador podem acessar Inventário Em andamento.

Quando uma contagem for alterada, o sistema deve preservar o usuário responsável pela última alteração daquele item ou possuir histórico equivalente.

A implementação deve evitar perda silenciosa de atualização concorrente.

---

## 25.26 Filtro Não contados

A tela deve possuir filtro:

NÃO CONTADOS.

O filtro deve apresentar Produtos cujo campo Quantidade contada permaneça sem valor.

O objetivo é facilitar a conclusão de Inventários grandes.

---

## 25.27 Contador de Produtos não contados

A interface deve informar a quantidade de Produtos ainda não contados.

Exemplo:

12 produtos ainda não contados.

O contador deve ser atualizado conforme as contagens forem persistidas.

---

## 25.28 Bloqueio da finalização com Produtos não contados

O Inventário não pode ser finalizado enquanto existir Produto Não contado.

Exemplo de mensagem:

Existem 12 produtos ainda não contados.

O usuário deve concluir todas as contagens antes da finalização.

A validação deve ocorrer no backend.

---

## 25.29 Leitor de Código de Barras

A tela de Inventário deve permitir utilização de leitor de Código de Barras.

O leitor deve utilizar o código persistido do Produto.

A leitura deve localizar o Produto pertencente ao Inventário.

---

## 25.30 Incremento por leitura

Ao ler um Código válido pertencente ao Inventário, o sistema deve incrementar a Quantidade contada em uma unidade.

Exemplo:

Quantidade contada:
0.

Primeira leitura:
1.

Segunda leitura:
2.

Terceira leitura:
3.

A interface deve destacar o Produto localizado.

---

## 25.31 Primeira leitura de Produto não contado

Quando o Produto ainda estiver Não contado e seu Código for lido pela primeira vez, a Quantidade contada deve passar para:

1.

Não utilizar o Estoque esperado como base do incremento.

---

## 25.32 Edição manual da contagem

O usuário pode editar manualmente a Quantidade contada.

Exemplo:

Leitor registrou:
10.

Após conferência física:
9.

O usuário pode corrigir para:
9.

A alteração deve ser persistida.

---

## 25.33 Código único

O Código do Produto deve seguir a regra oficial de unicidade do sistema.

Uma leitura válida deve localizar exatamente um Produto.

O Inventário não deve possuir lógica de escolha entre vários Produtos com o mesmo Código.

---

## 25.34 Código inexistente

Quando o Código lido não corresponder a Produto existente, apresentar mensagem equivalente a:

Produto não encontrado.

O sistema não deve criar Produto automaticamente durante o Inventário.

---

## 25.35 Produto fora do escopo do Inventário

Quando o Código corresponder a Produto existente, mas o Produto não pertencer ao Inventário atual, apresentar mensagem específica.

Exemplo:

Produto fora deste Inventário.

Não adicionar o Produto automaticamente ao escopo já iniciado.

---

## 25.36 Condicionais abertos

Produtos vinculados a Condicionais ativos permanecem reservados.

Essas unidades podem estar fisicamente com o Cliente e não estarão disponíveis para contagem na loja.

O Inventário deve considerar as reservas válidas.

---

## 25.37 Quantidade física esperada e Condicional

Exemplo:

Estoque real:
10.

Quantidade reservada em Condicional:
3.

Quantidade fisicamente esperada na loja:
7.

Contagem física:
7.

Resultado:
Sem divergência.

O Inventário não deve interpretar a ausência física das 3 unidades reservadas como perda de Estoque.

---

## 25.38 Alteração de Condicional durante o Inventário

Quando uma reserva de Condicional for criada, devolvida ou convertida em Venda durante Inventário Em andamento, o sistema deve considerar os efeitos válidos na posição esperada da finalização.

A fotografia inicial permanece preservada.

O cálculo final deve utilizar o histórico e o estado atual correspondente.

---

## 25.39 Produtos Em Garantia

Produto defeituoso recebido pela loja e controlado como Em Garantia não integra o Estoque comercial disponível.

O Produto Em Garantia possui controle próprio no módulo Garantias.

---

## 25.40 Produto Em Garantia e contagem comercial

A quantidade Em Garantia não deve ser incluída na contagem normal do Inventário comercial.

O sistema não deve somar Produto defeituoso recebido em Garantia à quantidade física esperada do Estoque comercial.

---

## 25.41 Garantia durante Inventário

Movimentações de Garantia que afetem o Estoque comercial durante Inventário Em andamento devem ser consideradas na posição esperada da finalização.

Exemplo:

Produto substituto recebido do Fornecedor e destinado ao Estoque.

A Entrada correspondente deve integrar as movimentações posteriores ao início.

---

## 25.42 Divergência de Inventário

A divergência deve ser calculada pelo backend.

Fórmula conceitual:

Divergência =
Quantidade contada - Quantidade fisicamente esperada.

Resultado:

0:
Sem divergência.

Negativo:
Falta física.

Positivo:
Sobra física.

---

## 25.43 Divergência negativa

Exemplo:

Quantidade fisicamente esperada:
10.

Quantidade contada:
8.

Divergência:
-2.

A finalização deve gerar:

AJUSTE DE INVENTÁRIO — SAÍDA.

Quantidade:
2.

---

## 25.44 Ajuste negativo do Estoque real

O ajuste negativo deve corrigir o Estoque real considerando as reservas válidas.

Exemplo:

Quantidade fisicamente contada na loja:
8.

Quantidade reservada em Condicionais:
3.

Novo Estoque real controlado:
11.

Conceitualmente:

Novo Estoque real =
Quantidade física contada + Quantidade reservada válida.

O sistema não deve reduzir o Estoque real para 8 ignorando as 3 unidades reservadas.

---

## 25.45 Divergência positiva

Exemplo:

Quantidade fisicamente esperada:
10.

Quantidade contada:
12.

Divergência:
+2.

A finalização deve gerar:

AJUSTE DE INVENTÁRIO — ENTRADA.

Quantidade:
2.

O Estoque real deve ser corrigido.

---

## 25.46 Ajuste positivo do Estoque real

O ajuste positivo deve aumentar o Estoque real na quantidade correspondente à divergência positiva.

Exemplo:

Estoque real esperado:
10.

Sem reservas.

Contagem:
12.

Ajuste:
+2.

Novo Estoque real:
12.

---

## 25.47 Produto sem divergência

Quando a Quantidade contada for igual à Quantidade fisicamente esperada, não gerar movimentação de Ajuste de Inventário para o Produto.

O Produto deve permanecer registrado nos detalhes do Inventário como:

Sem divergência.

---

## 25.48 Movimentação de Ajuste de Inventário

Cada Produto com divergência deve gerar movimentação de Estoque correspondente.

A movimentação deve identificar:

- tipo Ajuste de Inventário;
- direção Entrada ou Saída;
- Produto;
- quantidade;
- Inventário de origem;
- usuário responsável pela finalização;
- data e hora.

---

## 25.49 Origem do Ajuste

Todo ajuste gerado pela finalização deve possuir vínculo persistente com o Inventário de origem.

Não utilizar somente descrição textual como vínculo.

Os detalhes da movimentação devem permitir abrir ou identificar o Inventário correspondente.

---

## 25.50 Observação geral obrigatória com divergência

Quando existir pelo menos uma divergência no Inventário, a finalização deve exigir Observação geral.

Exemplo:

Divergências identificadas após contagem física geral da loja.

A observação deve ser persistida.

---

## 25.51 Inventário sem divergência

Quando nenhum Produto possuir divergência, a Observação geral não é obrigatória.

O Inventário pode ser finalizado sem ajuste de Estoque.

O histórico deve registrar que a contagem foi concluída sem divergências.

---

## 25.52 Motivo individual por Produto

O sistema não deve exigir motivo individual para cada Produto divergente.

A finalidade é evitar um fluxo inviável em Inventários grandes.

Cada Produto deve preservar:

- quantidade esperada;
- quantidade contada;
- divergência.

A Observação geral representa a justificativa operacional da finalização.

---

## 25.53 Custo gerencial do ajuste positivo

Quando existir divergência positiva, o sistema deve utilizar o custo atual cadastrado do Produto como valor gerencial do ajuste.

Exemplo:

Divergência:
+2 unidades.

Custo atual:
R$ 50,00.

Valor gerencial do ajuste:
R$ 100,00.

O valor possui finalidade gerencial e histórica.

---

## 25.54 Custo atual autoritativo

O custo atual utilizado no ajuste positivo deve ser obtido pelo backend a partir do Produto persistido no momento da finalização.

O navegador não deve informar autoritativamente o custo do ajuste.

---

## 25.55 Ajuste positivo não é Entrada de mercadoria

A divergência positiva não deve gerar Entrada de mercadoria.

Não criar Entrada fictícia.

A origem da quantidade deve permanecer identificada como:

Ajuste de Inventário.

---

## 25.56 Ajuste positivo não gera Conta a Pagar

A divergência positiva não deve gerar Conta a Pagar.

O sistema não deve presumir compra de mercadoria.

Não existe obrigação financeira automática decorrente do Ajuste de Inventário.

---

## 25.57 Ajuste positivo não possui Fornecedor inventado

O sistema não deve vincular automaticamente o ajuste positivo a Fornecedor.

A origem física da divergência pode ser desconhecida.

Não inventar Fornecedor para completar o histórico.

---

## 25.58 Valor gerencial da divergência negativa

A divergência negativa pode utilizar o custo atual cadastrado do Produto como referência gerencial do impacto de Estoque.

Exemplo:

Falta:
2 unidades.

Custo atual:
R$ 50,00.

Impacto gerencial estimado:
R$ 100,00.

Esse valor não representa Saída financeira automática.

---

## 25.59 Ajuste negativo não gera Saída financeira

A falta física identificada no Inventário não deve gerar automaticamente:

- Saída de Caixa;
- Conta a Pagar;
- pagamento;
- recebível.

O efeito direto é sobre o Estoque e os indicadores gerenciais correspondentes.

---

## 25.60 Situações do Inventário

As situações oficiais são:

- Em andamento;
- Finalizado;
- Cancelado.

A situação deve ser persistida.

---

## 25.61 Inventário Em andamento

Inventário Em andamento permite:

- registrar contagens;
- alterar contagens;
- utilizar leitor;
- salvar andamento;
- consultar Produtos não contados;
- cancelar;
- finalizar quando todas as regras forem atendidas.

---

## 25.62 Inventário Finalizado

Inventário Finalizado representa contagem concluída e posição reconciliada.

Após a finalização:

- contagens não podem ser editadas;
- escopo não pode ser alterado;
- fotografia inicial não pode ser alterada;
- ajustes gerados permanecem preservados.

---

## 25.63 Inventário Cancelado

Inventário Cancelado representa contagem interrompida formalmente antes da finalização.

O cancelamento não deve alterar o Estoque.

As contagens realizadas devem permanecer preservadas no histórico.

---

## 25.64 Cancelamento de Inventário Em andamento

Administrador e Operador podem cancelar Inventário Em andamento.

O cancelamento deve exigir confirmação.

Minha recomendação é exigir também motivo ou observação de cancelamento para preservar contexto operacional.

A operação deve registrar:

- usuário;
- data e hora;
- motivo ou observação.

---

## 25.65 Inventário Cancelado não gera ajustes

Ao cancelar Inventário Em andamento:

- não alterar Estoque;
- não gerar Ajuste de Inventário;
- não gerar Entrada;
- não gerar Saída financeira.

A fotografia e as contagens permanecem históricas.

---

## 25.66 Inventário Finalizado não pode ser cancelado diretamente

Inventário Finalizado não pode ser cancelado diretamente.

Os ajustes já podem ter sido seguidos por:

- Vendas;
- Condicionais;
- Entradas;
- Trocas;
- Devoluções;
- outras movimentações.

Não gerar reversão automática do Inventário finalizado.

---

## 25.67 Correção após Inventário Finalizado

Quando um erro for identificado após a finalização, a correção deve ocorrer por novo Inventário.

O novo Inventário realiza nova contagem física e gera os ajustes necessários.

Não editar o Inventário anterior.

Não apagar movimentações anteriores.

---

## 25.68 Número do Inventário

Cada Inventário deve possuir número automático por loja.

O número deve ser definido pelo backend.

O usuário não pode alterar manualmente o número.

---

## 25.69 Data e hora de início

O Inventário deve registrar a data e hora de início.

O timestamp deve seguir as regras oficiais do sistema.

Armazenamento:

UTC com offset explícito.

Apresentação:

America/Sao_Paulo.

---

## 25.70 Usuário que iniciou

O Inventário deve registrar o usuário autenticado responsável pela abertura.

O usuário deve ser obtido da sessão.

O navegador não deve informar autoritativamente o responsável.

---

## 25.71 Data e hora da finalização

Inventário Finalizado deve registrar a data e hora da finalização.

O timestamp deve ser gerado ou normalizado pelo backend.

---

## 25.72 Usuário que finalizou

O Inventário deve registrar o usuário autenticado responsável pela finalização.

O usuário que finaliza pode ser diferente do usuário que iniciou.

O histórico deve preservar ambos.

---

## 25.73 Histórico de contagem

O Inventário deve preservar as contagens finais de cada Produto.

Quando tecnicamente implementado histórico detalhado de alterações, o sistema pode preservar também as mudanças de contagem realizadas durante o processo.

No mínimo, deve ser possível identificar:

- Produto;
- quantidade contada final;
- usuário responsável pela última alteração da contagem.

---

## 25.74 Lista de Inventários

O módulo deve possuir Histórico de Inventários.

A listagem deve apresentar:

- número;
- tipo;
- escopo;
- data de início;
- data de finalização, quando existir;
- usuário que iniciou;
- situação;
- quantidade de Produtos;
- quantidade de Produtos com divergência;
- ação.

A ação principal deve ser:

VER DETALHES.

---

## 25.75 Busca de Inventários

A listagem deve permitir busca por:

- número do Inventário;
- Produto;
- Código;
- Marca.

Quando a busca utilizar Produto, Código ou Marca, o sistema deve localizar Inventários cujo escopo ou itens históricos correspondam ao critério.

---

## 25.76 Filtros de Inventários

A listagem deve permitir filtros por:

- período;
- tipo;
- situação;
- usuário responsável.

Tipos:

- Geral;
- Parcial.

Situações:

- Em andamento;
- Finalizado;
- Cancelado.

---

## 25.77 Detalhes do Inventário

Os detalhes devem apresentar:

- número;
- tipo;
- escopo;
- situação;
- data e hora de início;
- usuário que iniciou;
- data e hora de finalização;
- usuário que finalizou;
- observação geral;
- motivo de cancelamento, quando aplicável.

---

## 25.78 Produtos nos detalhes do Inventário

Para cada Produto, apresentar:

- Código;
- Produto;
- Marca;
- Cor;
- Tamanho;
- Estoque real inicial;
- reserva inicial;
- quantidade física esperada inicial;
- posição física esperada na finalização;
- quantidade contada;
- divergência;
- tipo de ajuste gerado;
- quantidade ajustada.

---

## 25.79 Resumo do Inventário

Os detalhes devem apresentar resumo com:

- total de Produtos contados;
- Produtos sem divergência;
- Produtos com divergência positiva;
- Produtos com divergência negativa;
- quantidade total de peças em sobra;
- quantidade total de peças em falta;
- impacto gerencial estimado das sobras;
- impacto gerencial estimado das faltas.

Os valores gerenciais devem utilizar as regras de custo definidas para o Inventário.

---

## 25.80 Produtos com divergência

A tela de detalhes deve permitir filtrar:

- Todos;
- Sem divergência;
- Divergência positiva;
- Divergência negativa.

O objetivo é facilitar auditoria e análise operacional.

---

## 25.81 Inventário na movimentação do Produto

O histórico de movimentações do Produto deve apresentar Ajustes de Inventário.

Exemplo:

AJUSTE DE INVENTÁRIO — ENTRADA +2.

AJUSTE DE INVENTÁRIO — SAÍDA -1.

A movimentação deve permitir identificar o Inventário de origem.

---

## 25.82 Inventário na ficha do Produto

A ficha ou detalhes do Produto devem permitir identificar os Inventários que produziram ajustes sobre o Produto.

O histórico deve preservar:

- data;
- Inventário;
- divergência;
- ajuste.

---

## 25.83 Relatório de Inventários

O sistema deve possuir Relatório de Inventários.

O Relatório deve permitir filtros por:

- período;
- tipo;
- situação;
- Produto;
- Marca;
- usuário.

---

## 25.84 Relatório de divergências

O sistema deve permitir analisar divergências de Inventário.

Apresentar, no mínimo:

- Inventário;
- data;
- Produto;
- Código;
- quantidade esperada;
- quantidade contada;
- divergência;
- custo gerencial de referência;
- impacto gerencial estimado.

---

## 25.85 Impressão e PDF

Inventário Finalizado deve permitir impressão ou exportação em PDF.

O documento deve seguir as regras oficiais de Impressões e Documentos Gerados.

Deve apresentar:

- identificação da loja;
- número do Inventário;
- tipo;
- escopo;
- situação;
- data de início;
- data de finalização;
- usuários responsáveis;
- observação geral;
- resumo;
- Produtos;
- quantidades esperadas;
- quantidades contadas;
- divergências;
- ajustes.

---

## 25.86 Atomicidade da finalização

A finalização do Inventário deve ser atômica.

Devem ocorrer de forma consistente:

- validação da situação;
- validação das contagens;
- recálculo da posição esperada;
- validação das reservas;
- cálculo das divergências;
- criação dos ajustes;
- alteração do Estoque;
- criação das movimentações;
- finalização do Inventário;
- auditoria.

Qualquer falha deve provocar rollback completo.

---

## 25.87 Idempotência da finalização

A finalização do Inventário deve possuir proteção idempotente.

Clique duplo, retry ou resposta de rede desconhecida não podem:

- finalizar duas vezes;
- gerar ajustes duplicados;
- alterar Estoque duas vezes;
- criar movimentações duplicadas.

A mesma tentativa deve produzir um único efeito persistente.

---

## 25.88 Concorrência na finalização

O backend deve tratar concorrência entre a finalização do Inventário e outras movimentações de Estoque.

Exemplo:

Inventário está sendo finalizado.

Simultaneamente ocorre uma Venda do mesmo Produto.

A operação deve serializar ou bloquear os registros necessários para que a Venda seja:

- considerada corretamente na posição esperada;

ou

- executada após a conclusão do Inventário sobre a posição já reconciliada.

O sistema não pode perder uma das movimentações.

---

## 25.89 Concorrência entre contagens

Quando dois usuários alterarem a contagem do mesmo Produto, o sistema deve impedir perda silenciosa de atualização.

A implementação deve utilizar mecanismo de controle compatível.

Pode utilizar:

- versão do item;
- timestamp de atualização;
- controle otimista equivalente.

Conflito detectado deve ser informado ao usuário.

---

## 25.90 Fonte autoritativa

O backend deve calcular e validar:

- Produtos do escopo;
- fotografia inicial;
- Estoque real;
- reservas;
- quantidade disponível;
- movimentações posteriores;
- posição esperada na finalização;
- quantidade fisicamente esperada;
- divergência;
- custo atual de referência;
- impacto gerencial;
- ajustes de Estoque.

O navegador não deve informar esses valores como fonte autoritativa.

---

## 25.91 Isolamento por loja

Todo Inventário deve respeitar a loja autenticada.

O sistema deve impedir:

- incluir Produto de outra loja;
- consultar Inventário de outra loja;
- alterar contagem de Inventário de outra loja;
- finalizar Inventário de outra loja.

A validação deve ocorrer no backend.

---

## 25.92 Regras gerais do Inventário

O sistema deve:

- permitir acesso ao Administrador;
- permitir acesso ao Operador;
- permitir Inventário Geral;
- permitir Inventário Parcial;
- permitir filtro por Marca no escopo parcial;
- permitir filtro por Categoria;
- permitir filtro por Gênero;
- permitir seleção por Produto;
- permitir seleção por Código;
- criar fotografia inicial;
- preservar Estoque real inicial;
- preservar reservas iniciais;
- preservar quantidade disponível inicial;
- preservar quantidade física esperada inicial;
- manter a fotografia imutável;
- não bloquear a operação da loja;
- considerar movimentações posteriores;
- recalcular a posição esperada na finalização;
- considerar reservas atuais;
- tratar movimentações concorrentes;
- iniciar Quantidade contada vazia;
- diferenciar Não contado de quantidade zero;
- aceitar contagem zero;
- exigir quantidade inteira e não negativa;
- permitir salvar andamento;
- permitir vários usuários;
- identificar responsável pela contagem;
- possuir filtro Não contados;
- informar quantidade de Produtos não contados;
- bloquear finalização com Produtos não contados;
- permitir leitor de Código de Barras;
- incrementar uma unidade por leitura;
- iniciar primeira leitura em um;
- permitir edição manual;
- utilizar Código único;
- informar Produto não encontrado;
- não criar Produto durante Inventário;
- informar Produto fora do Inventário;
- considerar Condicionais ativos;
- excluir reservas da quantidade física esperada na loja;
- considerar alterações de Condicional durante o Inventário;
- não incluir Produto Em Garantia no Estoque comercial;
- considerar movimentações válidas de Garantia;
- calcular divergência no backend;
- gerar Ajuste de Inventário — Saída;
- gerar Ajuste de Inventário — Entrada;
- corrigir Estoque real considerando reservas;
- não gerar ajuste para Produto sem divergência;
- gerar movimentação de Estoque;
- vincular ajuste ao Inventário;
- exigir Observação geral quando houver divergência;
- não exigir motivo por Produto;
- utilizar custo atual como referência gerencial do ajuste positivo;
- não criar Entrada fictícia;
- não criar Conta a Pagar;
- não inventar Fornecedor;
- permitir referência gerencial de custo na divergência negativa;
- não gerar Saída financeira pela falta física;
- utilizar situações Em andamento, Finalizado e Cancelado;
- permitir cancelamento de Inventário Em andamento;
- não alterar Estoque no cancelamento;
- preservar contagens de Inventário Cancelado;
- impedir cancelamento direto de Inventário Finalizado;
- exigir novo Inventário para correção posterior;
- gerar número automático;
- registrar data e hora de início;
- registrar usuário que iniciou;
- registrar data e hora de finalização;
- registrar usuário que finalizou;
- preservar contagens;
- possuir Histórico de Inventários;
- permitir busca;
- permitir filtros;
- apresentar detalhes;
- apresentar resumo;
- permitir análise das divergências;
- vincular ajustes ao histórico do Produto;
- possuir Relatório;
- permitir PDF;
- finalizar de forma atômica;
- utilizar idempotência;
- tratar concorrência de Estoque;
- tratar concorrência de contagem;
- utilizar backend como fonte autoritativa;
- respeitar isolamento por loja.

# 26. LOGIN, SESSÕES E SEGURANÇA DE ACESSO

## 26.1 Finalidade

As regras de Login, Sessões e Segurança de Acesso definem a autenticação dos usuários e o controle das sessões do sistema.

O sistema deve proteger o acesso à loja autenticada e preservar a identidade do usuário responsável pelas operações.

As regras desta seção são complementares às regras oficiais de Usuários e Permissões.

---

## 26.2 Perfis autenticáveis

Os perfis oficiais que podem realizar Login são:

- Administrador;
- Operador.

O usuário deve estar ativo e autorizado para acessar a loja correspondente.

Não existem outros perfis oficiais de usuário neste momento.

---

## 26.3 Identificação no Login

O Login deve aceitar:

- Nome de usuário;
- E-mail.

O usuário pode utilizar qualquer um dos identificadores válidos vinculados ao seu cadastro.

A senha é obrigatória.

---

## 26.4 Nome de usuário único

O Nome de usuário deve ser único dentro da loja.

A comparação deve ignorar diferenças entre letras maiúsculas e minúsculas.

Exemplo:

mauro

MAURO

Mauro

Os valores representam o mesmo Nome de usuário para fins de unicidade.

Espaços externos devem ser removidos antes da validação.

---

## 26.5 E-mail único

Quando informado, o E-mail deve ser único dentro da loja.

A comparação deve ignorar diferenças entre letras maiúsculas e minúsculas.

Espaços externos devem ser removidos antes da validação.

A normalização não deve alterar arbitrariamente o conteúdo interno do endereço.

---

## 26.6 E-mail obrigatório para Administrador

Todo usuário com perfil Administrador deve possuir E-mail válido cadastrado.

O E-mail é obrigatório para permitir recuperação segura de acesso administrativo.

Não permitir:

- criar Administrador sem E-mail;
- alterar Operador para Administrador sem E-mail;
- remover o E-mail de usuário Administrador.

A validação deve ocorrer no backend.

---

## 26.7 E-mail do Operador

O E-mail pode ser opcional para usuário Operador.

Quando informado, deve seguir as regras de formato e unicidade.

A ausência de E-mail pode impedir a utilização de fluxos de recuperação por E-mail disponíveis ao usuário.

---

## 26.8 Autenticação

O backend deve localizar o usuário pelo identificador informado e validar a senha utilizando o hash persistido.

O navegador não deve decidir se as credenciais são válidas.

A autenticação deve ocorrer no backend.

---

## 26.9 Mensagem genérica de credenciais inválidas

Quando o Nome de usuário, E-mail ou senha não permitirem autenticação, o sistema deve utilizar mensagem genérica.

Mensagem:

Usuário ou senha inválidos.

O sistema não deve informar publicamente:

- Usuário não existe;
- E-mail não cadastrado;
- Senha incorreta.

A finalidade é evitar exposição desnecessária dos usuários cadastrados.

---

## 26.10 Contagem de falhas de Login

O sistema deve controlar falhas consecutivas de Login por usuário.

A contagem deve ser persistida no backend.

Não utilizar somente:

- navegador;
- localStorage;
- sessionStorage;
- cookie local

como fonte autoritativa da quantidade de falhas.

---

## 26.11 Tentativas em dispositivos diferentes

As falhas de Login do mesmo usuário devem ser consideradas independentemente do dispositivo utilizado.

Exemplo:

3 falhas no computador A.

2 falhas no computador B.

Resultado:

5 falhas consecutivas do mesmo usuário.

A troca de computador não deve reiniciar a contagem.

---

## 26.12 Máximo de tentativas

O usuário pode acumular até 5 falhas consecutivas de Login antes da aplicação da regra de bloqueio correspondente.

A contagem inicia na primeira tentativa inválida identificável para um usuário existente.

---

## 26.13 Aviso na terceira falha

Na terceira falha consecutiva, o sistema deve informar:

Usuário ou senha inválidos. Restam 2 tentativas antes do bloqueio.

O aviso deve utilizar a contagem autoritativa do backend.

---

## 26.14 Aviso na quarta falha

Na quarta falha consecutiva, o sistema deve informar:

Usuário ou senha inválidos. Resta 1 tentativa antes do bloqueio.

O aviso deve utilizar a contagem autoritativa do backend.

---

## 26.15 Quinta falha

Na quinta falha consecutiva, o sistema deve aplicar a regra de bloqueio correspondente ao usuário.

A regra depende da existência de outro Administrador ativo na loja quando o usuário bloqueado possuir perfil Administrador.

---

## 26.16 Login válido antes da quinta falha

Quando o usuário realizar Login válido antes da quinta falha consecutiva, o contador de falhas deve voltar para zero.

Exemplo:

Falha 1.

Falha 2.

Falha 3.

Login válido.

Contador:
0.

As falhas são consecutivas.

---

## 26.17 Bloqueio do Operador

Na quinta falha consecutiva, o Operador deve ser bloqueado.

Mensagem:

Usuário bloqueado. Solicite o desbloqueio a um Administrador.

O bloqueio não possui expiração automática.

O Operador permanece bloqueado até desbloqueio administrativo.

---

## 26.18 Bloqueio de Administrador quando existe outro Administrador ativo

Quando o usuário possuir perfil Administrador e existir outro Administrador ativo na mesma loja, a quinta falha consecutiva deve bloquear o usuário.

O Administrador bloqueado permanece bloqueado até ser desbloqueado por outro Administrador.

O sistema não deve permitir que o próprio usuário bloqueado se desbloqueie por sessão antiga.

---

## 26.19 Identificação do único Administrador ativo

Antes de aplicar bloqueio permanente a um Administrador, o backend deve verificar quantos Administradores ativos existem na loja.

O próprio usuário deve ser considerado nessa verificação.

Quando não existir outro Administrador ativo capaz de realizar o desbloqueio, o usuário deve ser tratado como único Administrador ativo.

---

## 26.20 Proteção do único Administrador ativo

O único Administrador ativo da loja não deve receber bloqueio permanente por falhas de Login.

Na quinta falha consecutiva, deve ser aplicado bloqueio temporário de 15 minutos.

Mensagem equivalente:

Acesso temporariamente suspenso por segurança. Tente novamente em 15 minutos.

---

## 26.21 Bloqueio temporário do único Administrador

Durante o bloqueio temporário de 15 minutos, o usuário não pode realizar nova tentativa de autenticação por senha.

O bloqueio deve ser controlado pelo backend.

Não deve ser removido por:

- fechar o navegador;
- limpar armazenamento local;
- trocar de computador;
- utilizar outro navegador.

---

## 26.22 Final do bloqueio temporário

Após completar 15 minutos, o único Administrador ativo volta a poder tentar autenticação.

O sistema não realiza Login automático.

O contador de falhas consecutivas deve reiniciar para zero para o novo ciclo de tentativas.

Se ocorrerem novamente 5 falhas consecutivas, um novo bloqueio temporário de 15 minutos deve ser aplicado.

---

## 26.23 Desbloqueio administrativo

Somente Administrador autenticado pode desbloquear usuário com bloqueio permanente.

O desbloqueio deve:

- remover o bloqueio;
- zerar o contador de falhas;
- preservar a senha atual.

O desbloqueio não exige redefinição automática de senha.

---

## 26.24 Histórico do desbloqueio

O desbloqueio administrativo deve registrar:

- usuário desbloqueado;
- Administrador responsável;
- data e hora.

A operação deve permanecer disponível na auditoria correspondente.

---

## 26.25 Lembrar-me

A tela de Login deve possuir opção:

Lembrar-me.

O usuário decide se deseja utilizar uma sessão de maior duração.

A escolha deve ser enviada ao backend durante a autenticação.

---

## 26.26 Sessão sem Lembrar-me

Quando Lembrar-me não estiver selecionado, a sessão possui validade máxima de 12 horas.

Após a expiração, o usuário deve realizar novo Login.

---

## 26.27 Sessão com Lembrar-me

Quando Lembrar-me estiver selecionado, a sessão possui validade máxima de 30 dias.

Após a expiração, o usuário deve realizar novo Login.

Lembrar-me não representa sessão permanente.

---

## 26.28 Validade autoritativa da Sessão

A validade da Sessão deve ser controlada pelo backend.

Alterar relógio do navegador ou valores armazenados localmente não deve ampliar a validade da Sessão.

O servidor deve validar a expiração.

---

## 26.29 Sessões simultâneas

O mesmo usuário pode possuir várias Sessões válidas simultaneamente.

Exemplo:

Computador do Caixa.

Segundo computador da loja.

As Sessões devem ser independentes e rastreáveis.

---

## 26.30 Identificação da Sessão

Cada Sessão deve possuir identificador persistente ou mecanismo equivalente que permita sua invalidação individual.

O sistema deve ser capaz de:

- encerrar a Sessão atual;
- invalidar todas as Sessões de um usuário.

---

## 26.31 Logout

Ao realizar Logout, o sistema deve encerrar a Sessão atual.

Outras Sessões válidas do mesmo usuário permanecem ativas, salvo quando outra regra exigir invalidação global.

---

## 26.32 Usuário desativado

Usuário desativado não pode realizar Login.

A desativação deve invalidar todas as Sessões existentes do usuário.

Uma Sessão criada antes da desativação não pode continuar autorizando acesso.

---

## 26.33 Usuário bloqueado

Usuário com bloqueio permanente não pode realizar novo Login até o desbloqueio administrativo.

Sessões existentes devem ser tratadas conforme as regras de segurança do bloqueio.

Minha recomendação oficial é invalidar todas as Sessões do usuário no momento do bloqueio permanente.

---

## 26.34 Bloqueio temporário e Sessões existentes

O bloqueio temporário do único Administrador é uma proteção contra novas tentativas de autenticação.

Sessões válidas já existentes não devem ser automaticamente encerradas apenas pelo bloqueio temporário de Login.

A regra evita que tentativas externas de senha derrubem Sessões administrativas legítimas já autenticadas.

---

## 26.35 Alterar Minha Senha

Todo usuário autenticado pode utilizar a opção:

ALTERAR MINHA SENHA.

O fluxo deve exigir:

- senha atual;
- nova senha;
- confirmação da nova senha.

---

## 26.36 Validação da senha atual

A senha atual deve ser validada pelo backend.

Não permitir alteração da própria senha sem confirmação válida da senha atual.

A sessão autenticada, isoladamente, não substitui essa confirmação.

---

## 26.37 Nova senha

Não existe regra mínima de tamanho ou complexidade da senha.

O sistema deve permitir qualquer senha informada pelo usuário.

A senha deve possuir algum valor.

Não permitir senha ausente.

---

## 26.38 Confirmação da nova senha

A confirmação deve ser idêntica à nova senha.

Quando os valores forem diferentes, a alteração deve ser recusada.

O backend deve validar a operação.

---

## 26.39 Ausência de complexidade obrigatória

O sistema não deve exigir obrigatoriamente:

- quantidade mínima de caracteres;
- letra maiúscula;
- letra minúscula;
- número;
- caractere especial;
- troca periódica de senha.

Exemplos de senhas simples podem ser aceitos.

A interface não deve apresentar regra de complexidade inexistente.

---

## 26.40 Armazenamento da senha

A senha nunca deve ser armazenada em texto puro.

O sistema deve utilizar hash seguro de senha.

O mecanismo deve utilizar algoritmo apropriado para armazenamento de credenciais.

A senha original não deve ser recuperável a partir do cadastro.

---

## 26.41 Senha em Logs e Auditoria

O sistema não deve registrar:

- senha atual;
- nova senha;
- confirmação de senha;
- código de recuperação em texto reutilizável

em Logs ou Auditoria.

A Auditoria pode registrar que uma alteração ou redefinição ocorreu.

---

## 26.42 Alteração da própria senha e Sessões

Após alteração válida da própria senha, todas as Sessões do usuário devem ser invalidadas.

Isso inclui a Sessão atual.

O usuário deve realizar novo Login utilizando a nova senha.

---

## 26.43 Redefinição de senha pelo Administrador

Administrador pode redefinir a senha de outro usuário.

A operação não exige conhecimento da senha antiga do usuário.

O Administrador deve informar:

- nova senha;
- confirmação da nova senha.

---

## 26.44 Administrador e própria senha

Quando o Administrador alterar a própria senha, deve utilizar o fluxo:

ALTERAR MINHA SENHA.

Nesse caso, a senha atual é obrigatória.

A permissão administrativa de redefinição sem senha antiga é destinada a outro usuário.

---

## 26.45 Efeitos da redefinição administrativa

Após redefinição administrativa válida:

- todas as Sessões do usuário devem ser invalidadas;
- contador de falhas deve voltar para zero;
- bloqueio permanente deve ser removido;
- bloqueio temporário aplicável deve ser removido.

O usuário deve realizar novo Login com a nova senha.

---

## 26.46 Auditoria da redefinição administrativa

A redefinição administrativa deve registrar:

- usuário cuja senha foi redefinida;
- Administrador responsável;
- data e hora.

A senha não deve ser registrada.

---

## 26.47 Alteração de perfil

Quando o perfil do usuário for alterado entre:

- Administrador;
- Operador

todas as Sessões do usuário devem ser invalidadas.

O usuário deve realizar novo Login.

As novas permissões passam a ser aplicadas após nova autenticação.

---

## 26.48 Alteração para Administrador

Antes de alterar Operador para Administrador, o backend deve validar a existência de E-mail válido.

Administrador exige E-mail cadastrado.

A alteração deve ser recusada enquanto o requisito não for atendido.

---

## 26.49 Proteção contra ausência de Administrador

A loja não pode ficar sem Administrador ativo.

O backend deve impedir operação que resulte em zero Administradores ativos.

A regra deve considerar, no mínimo:

- desativação;
- alteração de perfil de Administrador para Operador.

---

## 26.50 Último Administrador ativo

Quando o usuário for o último Administrador ativo da loja, o sistema deve impedir:

- sua desativação;
- sua alteração para Operador.

Mensagem equivalente:

A loja deve possuir pelo menos um Administrador ativo.

A validação deve ocorrer no backend.

---

## 26.51 Recuperação de senha

O sistema deve possuir fluxo:

ESQUECI MINHA SENHA.

A recuperação deve utilizar o E-mail cadastrado do usuário.

O sistema não deve enviar a senha atual.

---

## 26.52 Solicitação de recuperação

O usuário informa seu identificador ou E-mail conforme o fluxo implementado.

A resposta pública deve evitar revelar desnecessariamente a existência do usuário.

Mensagem equivalente:

Se os dados informados corresponderem a um usuário elegível, as instruções de recuperação serão enviadas ao E-mail cadastrado.

---

## 26.53 Destino da recuperação

As instruções de recuperação devem ser enviadas somente ao E-mail persistido no cadastro do próprio usuário.

O navegador não pode informar livremente um E-mail alternativo para receber a recuperação.

---

## 26.54 Token ou código de recuperação

A recuperação deve utilizar Token ou Código seguro de uso único.

O valor deve possuir validade máxima de 30 minutos.

Após utilização válida, o Token ou Código não pode ser reutilizado.

---

## 26.55 Armazenamento do Token de recuperação

O sistema não deve armazenar Token reutilizável de recuperação em texto puro quando existir mecanismo seguro de hash aplicável.

O backend deve validar o Token de forma segura.

O Token não deve ser registrado em Logs ou Auditoria.

---

## 26.56 Expiração da recuperação

Após 30 minutos, o Token ou Código de recuperação deve ser considerado expirado.

Token expirado não pode alterar a senha.

O usuário deve solicitar nova recuperação.

---

## 26.57 Nova solicitação de recuperação

Uma nova solicitação pode invalidar Tokens anteriores ainda não utilizados do mesmo usuário.

Minha recomendação oficial é manter somente a solicitação de recuperação mais recente como válida.

Isso reduz ambiguidade e risco de uso de links antigos.

---

## 26.58 Conclusão da recuperação

Ao concluir a recuperação de senha:

- persistir o novo hash de senha;
- invalidar o Token ou Código;
- zerar o contador de falhas;
- remover bloqueio permanente;
- remover bloqueio temporário;
- invalidar todas as Sessões do usuário.

O usuário deve realizar novo Login.

---

## 26.59 Histórico da recuperação

A conclusão válida de recuperação de senha deve registrar evento de segurança.

O histórico pode registrar:

- usuário;
- data e hora;
- tipo de evento Recuperação de senha concluída.

Não registrar:

- senha;
- Token;
- Código de recuperação.

---

## 26.60 Tentativas de recuperação inválidas

Token ou Código:

- inexistente;
- expirado;
- já utilizado;
- invalidado

não deve permitir alteração da senha.

O sistema deve apresentar mensagem segura e clara ao usuário.

---

## 26.61 Data e hora de segurança

Eventos de segurança devem registrar timestamp oficial.

Novos timestamps devem ser armazenados em UTC com offset explícito.

A apresentação deve utilizar:

America/Sao_Paulo.

---

## 26.62 Sessão e loja autenticada

Toda Sessão deve permanecer vinculada à loja correspondente.

O usuário não deve acessar dados de outra loja alterando parâmetros enviados pelo navegador.

A loja da Sessão deve ser validada no backend.

---

## 26.63 Usuário autoritativo

O usuário responsável por uma operação deve ser obtido da Sessão autenticada e do cadastro persistido.

O navegador não deve informar autoritativamente:

- ID do usuário responsável;
- Nome do usuário responsável;
- Perfil do usuário.

---

## 26.64 Perfil autoritativo

O perfil atual deve ser validado pelo backend.

Não confiar em perfil armazenado somente no navegador.

Alterar JavaScript, HTML ou armazenamento local não deve conceder permissão administrativa.

---

## 26.65 Sessão expirada

Quando a Sessão estiver expirada, o backend deve recusar a operação autenticada.

A interface deve:

- limpar dados gerenciais renderizados;
- invalidar caches protegidos;
- cancelar ou invalidar requisições protegidas pendentes quando aplicável;
- apresentar novamente o fluxo de Login.

Dados protegidos não devem permanecer visíveis como se a Sessão ainda estivesse válida.

---

## 26.66 Operação após invalidação da Sessão

Sessão invalidada por:

- Logout;
- alteração de senha;
- redefinição de senha;
- alteração de perfil;
- desativação

não pode continuar realizando operações.

O backend deve recusar a Sessão invalidada.

---

## 26.67 Atomicidade das operações de segurança

Operações críticas de segurança devem ser executadas de forma consistente.

Exemplos:

- redefinição de senha e invalidação de Sessões;
- alteração de perfil e invalidação de Sessões;
- desativação e invalidação de Sessões;
- recuperação de senha e consumo do Token.

Qualquer falha deve evitar estado parcial inseguro.

---

## 26.68 Concorrência no último Administrador

O backend deve tratar operações concorrentes envolvendo Administradores.

Exemplo:

A loja possui 2 Administradores ativos.

Administrador A é desativado simultaneamente à alteração do Administrador B para Operador.

O sistema não pode concluir ambas as operações se o resultado for zero Administradores ativos.

A validação deve ocorrer dentro de mecanismo transacional compatível.

---

## 26.69 Proteção contra repetição da recuperação

A conclusão da recuperação de senha deve possuir proteção contra repetição.

O mesmo Token ou Código não pode alterar a senha duas vezes.

Duas requisições concorrentes utilizando a mesma recuperação devem produzir no máximo uma conclusão válida.

---

## 26.70 Fonte autoritativa

O backend deve calcular e validar:

- usuário;
- loja;
- perfil;
- situação ativa;
- bloqueio;
- quantidade de falhas;
- existência de outro Administrador ativo;
- validade da Sessão;
- duração da Sessão;
- senha;
- validade da recuperação.

O navegador não deve informar esses estados como fonte autoritativa.

---

## 26.71 Regras gerais de Login, Sessões e Segurança de Acesso

O sistema deve:

- permitir Login de Administrador;
- permitir Login de Operador;
- aceitar Nome de usuário;
- aceitar E-mail;
- exigir senha;
- manter Nome de usuário único por loja;
- comparar Nome de usuário sem diferenciar maiúsculas e minúsculas;
- manter E-mail único por loja;
- exigir E-mail para Administrador;
- permitir E-mail opcional para Operador;
- autenticar no backend;
- utilizar mensagem genérica para credenciais inválidas;
- controlar falhas consecutivas por usuário;
- persistir a contagem no backend;
- considerar tentativas em dispositivos diferentes;
- permitir até 5 falhas consecutivas;
- avisar na terceira falha;
- avisar na quarta falha;
- aplicar bloqueio na quinta falha;
- zerar falhas após Login válido;
- bloquear Operador até desbloqueio administrativo;
- bloquear Administrador quando existir outro Administrador ativo;
- identificar o único Administrador ativo;
- aplicar bloqueio temporário de 15 minutos ao único Administrador;
- controlar bloqueio temporário no backend;
- reiniciar o ciclo após 15 minutos;
- permitir desbloqueio somente por Administrador;
- zerar falhas no desbloqueio;
- preservar a senha no desbloqueio;
- auditar o desbloqueio;
- possuir opção Lembrar-me;
- utilizar Sessão de 12 horas sem Lembrar-me;
- utilizar Sessão de 30 dias com Lembrar-me;
- controlar expiração no backend;
- permitir Sessões simultâneas;
- permitir encerrar Sessão atual;
- invalidar Sessões de usuário desativado;
- invalidar Sessões em bloqueio permanente;
- preservar Sessões válidas existentes no bloqueio temporário do único Administrador;
- permitir alteração da própria senha;
- exigir senha atual;
- não possuir complexidade mínima obrigatória;
- permitir qualquer senha não ausente;
- exigir confirmação idêntica;
- armazenar somente hash seguro;
- não registrar senha;
- invalidar todas as Sessões após alteração da própria senha;
- permitir redefinição administrativa da senha de outro usuário;
- não exigir senha antiga na redefinição administrativa;
- invalidar Sessões após redefinição;
- zerar falhas após redefinição;
- remover bloqueio após redefinição;
- auditar redefinição sem registrar senha;
- invalidar Sessões após alteração de perfil;
- exigir E-mail antes de tornar usuário Administrador;
- impedir loja sem Administrador ativo;
- impedir desativação do último Administrador;
- impedir alteração do último Administrador para Operador;
- possuir Esqueci minha senha;
- recuperar somente pelo E-mail persistido;
- não enviar senha atual;
- utilizar Token ou Código de uso único;
- utilizar validade de 30 minutos;
- proteger o Token de recuperação;
- invalidar recuperação após expiração;
- manter somente a recuperação mais recente válida;
- invalidar Sessões após recuperação;
- zerar falhas após recuperação;
- remover bloqueios após recuperação;
- registrar evento de segurança;
- não registrar Token ou Código;
- utilizar timestamps oficiais;
- vincular Sessão à loja;
- obter usuário da Sessão;
- validar perfil no backend;
- tratar Sessão expirada;
- recusar Sessão invalidada;
- utilizar atomicidade em operações críticas;
- tratar concorrência sobre o último Administrador;
- impedir reutilização de recuperação;
- utilizar backend como fonte autoritativa;
- respeitar isolamento por loja.

# 27. AUDITORIA E HISTÓRICO DE OPERAÇÕES

## 27.1 Finalidade da Auditoria

A Auditoria é o mecanismo central de rastreabilidade das ações relevantes realizadas no sistema.

A Auditoria deve permitir identificar:

- o que ocorreu;
- quem realizou a ação;
- quando a ação ocorreu;
- qual módulo foi afetado;
- qual entidade ou operação foi afetada;
- quais dados relevantes foram alterados, quando aplicável.

A Auditoria possui finalidade de segurança, integridade, rastreabilidade e diagnóstico.

---

## 27.2 Auditoria e históricos operacionais

A Auditoria não substitui os históricos próprios dos módulos.

Exemplos de históricos operacionais:

- Histórico da Venda;
- Histórico do Condicional;
- Histórico do Crediário;
- Histórico da Garantia;
- Histórico da Conta a Pagar;
- Histórico do Inventário;
- Histórico de movimentações do Estoque.

Os históricos operacionais registram a evolução da entidade correspondente.

A Auditoria registra transversalmente as ações relevantes realizadas no sistema.

Os dois controles devem coexistir.

---

## 27.3 Exemplo de coexistência dos históricos

Exemplo de Histórico da Garantia:

10/07/2026:
Enviada ao Fornecedor.

15/07/2026:
Fornecedor informou que o Produto permanece em análise.

Exemplo de Auditoria:

15/07/2026 às 10:32:
Mauro atualizou a Garantia nº 125.

O evento operacional permanece na Garantia.

A ação do usuário permanece na Auditoria.

---

## 27.4 Acesso à Central de Auditoria

Somente Administrador pode acessar a Central de Auditoria.

Operador não pode acessar a tela central de Auditoria.

A autorização deve ser validada no backend.

Ocultar o item de menu no frontend não substitui a validação de permissão.

---

## 27.5 Históricos operacionais para o Operador

A ausência de acesso à Central de Auditoria não impede o Operador de consultar históricos operacionais dos módulos aos quais possui acesso.

Exemplos:

- Histórico da Venda;
- Histórico do Condicional;
- Histórico do Crediário;
- Histórico da Garantia;
- Histórico do Produto;
- Histórico de movimentações.

O acesso deve seguir as regras oficiais do módulo correspondente.

---

## 27.6 Imutabilidade da Auditoria

Registros de Auditoria não podem ser editados.

Nenhum usuário pode alterar:

- usuário responsável;
- perfil histórico;
- data e hora;
- módulo;
- ação;
- entidade;
- referência;
- alterações registradas;
- origem técnica persistida.

A regra também se aplica ao Administrador.

---

## 27.7 Proibição de exclusão da Auditoria

Registros de Auditoria não podem ser excluídos por Administrador ou Operador.

O sistema não deve possuir ação operacional comum para:

- apagar evento;
- limpar Auditoria;
- remover histórico selecionado;
- remover Auditoria por usuário;
- remover Auditoria por módulo.

A Auditoria deve permanecer preservada.

---

## 27.8 Ações relevantes

A Auditoria deve registrar ações relevantes de segurança, cadastro, operação e movimentação.

O sistema não deve utilizar a Auditoria para registrar indiscriminadamente cada interação visual do usuário.

A classificação do evento deve considerar seu efeito sobre:

- segurança;
- dados persistidos;
- estado operacional;
- Estoque;
- valores financeiros;
- permissões;
- histórico relevante.

---

## 27.9 Eventos de Segurança

Devem ser auditados, conforme aplicável:

- Login válido;
- falha de Login identificável;
- bloqueio de usuário;
- bloqueio temporário do único Administrador;
- desbloqueio administrativo;
- Logout;
- recuperação de senha concluída;
- alteração da própria senha;
- redefinição de senha pelo Administrador;
- alteração de perfil;
- ativação de usuário;
- desativação de usuário.

A Auditoria não deve registrar o conteúdo de credenciais ou Tokens.

---

## 27.10 Falha de Login identificável

Falha de Login pode ser vinculada a um usuário quando o identificador informado corresponder de forma segura a usuário persistido.

Nesse caso, o evento pode registrar o usuário afetado e a falha de autenticação.

Quando o identificador não corresponder a usuário conhecido, o sistema pode registrar evento técnico de tentativa inválida sem criar usuário ou referência inexistente.

A resposta pública continua seguindo a mensagem genérica oficial de autenticação.

---

## 27.11 Eventos de Usuários

Devem ser auditados, conforme aplicável:

- criação de usuário;
- edição de usuário;
- alteração de perfil;
- ativação;
- desativação;
- desbloqueio;
- redefinição administrativa de senha.

Alterações cadastrais devem preservar os campos efetivamente modificados.

---

## 27.12 Eventos de Clientes

Devem ser auditados, conforme aplicável:

- criação de Cliente;
- edição de Cliente;
- alteração de Limite de Crédito;
- desativação;
- reativação.

Quando houver edição, devem ser preservados os campos efetivamente alterados.

---

## 27.13 Eventos de Produtos e Estoque

Devem ser auditados, conforme aplicável:

- criação de Produto;
- edição de Produto;
- alteração de preço;
- alteração de custo;
- alteração de dados cadastrais relevantes;
- Entrada;
- Ajuste de Inventário;
- demais ajustes oficiais de Estoque.

A Auditoria não deve permitir edição livre de quantidade como substituição de uma operação oficial de Estoque.

---

## 27.14 Eventos de Vendas

Devem ser auditados, conforme aplicável:

- criação de Venda;
- cancelamento de Venda;
- Devolução;
- Troca;
- demais operações formais que alterem o estado financeiro ou operacional da Venda.

O evento deve possuir vínculo com a Venda correspondente.

---

## 27.15 Eventos de Condicionais

Devem ser auditados, conforme aplicável:

- criação de Condicional;
- alteração operacional relevante;
- retorno parcial;
- retorno total;
- seleção de Produtos devolvidos;
- seleção de Produtos mantidos pelo Cliente;
- geração de Venda vinculada;
- finalização;
- cancelamento, quando aplicável pelas regras oficiais.

O histórico próprio do Condicional permanece obrigatório.

---

## 27.16 Eventos de Crediário

Devem ser auditados, conforme aplicável:

- criação do Crediário;
- recebimento;
- recebimento parcial;
- recebimento antecipado;
- estorno;
- acréscimo;
- juros;
- multa;
- renegociação;
- demais operações financeiras oficiais.

A Auditoria não substitui o histórico financeiro detalhado do Crediário.

---

## 27.17 Eventos Financeiros

Devem ser auditados, conforme aplicável:

- criação de Conta a Pagar;
- edição permitida;
- pagamento;
- pagamento parcial;
- estorno;
- cancelamento;
- utilização de Crédito com Fornecedor;
- reversão de Crédito;
- conciliação de Devolução ao Fornecedor;
- demais operações financeiras relevantes.

O evento deve possuir referência à entidade financeira correspondente.

---

## 27.18 Eventos de Fornecedores

Devem ser auditados, conforme aplicável:

- criação de Fornecedor;
- edição de Fornecedor;
- desativação;
- reativação.

Alterações cadastrais devem preservar os campos efetivamente modificados.

---

## 27.19 Eventos de Garantias

Devem ser auditados, conforme aplicável:

- abertura de Garantia;
- recebimento do Produto;
- envio ao Fornecedor;
- atualização relevante;
- alteração de situação;
- aprovação;
- recusa;
- reparo;
- substituição;
- troca;
- devolução financeira;
- entrega ao Cliente;
- resolução;
- cancelamento.

O histórico próprio da Garantia permanece obrigatório.

---

## 27.20 Eventos de Inventário

Devem ser auditados, conforme aplicável:

- início de Inventário;
- cancelamento;
- finalização;
- Ajustes de Inventário gerados.

Alterações individuais de contagem podem permanecer no histórico próprio do Inventário quando o controle detalhado estiver implementado.

A Auditoria central não precisa gerar evento independente para cada leitura de Código de Barras.

---

## 27.21 Interações que não exigem Auditoria

Não é obrigatório auditar ações exclusivamente visuais ou de navegação sem alteração relevante de estado.

Exemplos:

- abrir uma tela;
- fechar uma tela;
- abrir um modal;
- fechar um modal;
- realizar busca;
- aplicar filtro;
- alterar paginação;
- ordenar uma listagem;
- visualizar detalhes;
- imprimir uma lista operacional comum.

Essas ações não devem gerar volume artificial de Auditoria.

---

## 27.22 Impressões sensíveis

A impressão ou exportação comum de documentos operacionais não exige evento de Auditoria específico.

Exportações da própria Central de Auditoria podem ser auditadas como evento de segurança ou controle administrativo.

A implementação deve evitar registrar conteúdo sensível completo dentro do evento de exportação.

---

## 27.23 Alterações de cadastro

Quando uma edição modificar dados persistidos relevantes, a Auditoria deve preservar:

- valor anterior;
- valor novo.

Somente os campos efetivamente alterados devem ser apresentados como alterações.

Campos sem mudança não devem ser registrados artificialmente como modificados.

---

## 27.24 Exemplo de alteração de Cliente

Exemplo:

Entidade:
Cliente.

Ação:
Cadastro alterado.

Alterações:

Telefone.

Antes:
(48) 99999-1111.

Depois:
(48) 99999-2222.

O sistema não deve apresentar todos os campos do Cliente quando somente o Telefone foi alterado.

---

## 27.25 Exemplo de alteração de Produto

Exemplo:

Entidade:
Produto.

Ação:
Preço alterado.

Alterações:

Preço de Venda.

Antes:
R$ 100,00.

Depois:
R$ 120,00.

O histórico deve preservar a alteração efetivamente realizada.

---

## 27.26 Alterações financeiras

Operações financeiras não devem ser reduzidas somente a uma comparação genérica de antes e depois.

Quando existir entidade operacional própria, a Auditoria deve registrar a ação e a referência correspondente.

Exemplo:

Ação:
Recebimento registrado.

Referência:
Crediário nº 125.

Valor:
R$ 200,00.

Forma:
Pix.

Os detalhes financeiros completos permanecem no módulo de origem.

---

## 27.27 Senhas

A Auditoria nunca deve registrar:

- senha atual;
- senha anterior;
- nova senha;
- confirmação de senha;
- hash da senha.

Quando ocorrer alteração, registrar somente o evento correspondente.

Exemplos:

Senha alterada.

Senha redefinida pelo Administrador.

Recuperação de senha concluída.

---

## 27.28 Tokens e Códigos de Segurança

A Auditoria nunca deve registrar:

- Token de Sessão;
- Cookie de autenticação;
- Token de recuperação;
- Código de recuperação;
- chave secreta;
- credencial reutilizável.

A existência de um evento de segurança pode ser registrada sem preservar o segredo correspondente.

---

## 27.29 Chaves de idempotência

Chaves de idempotência financeiras ou operacionais não devem ser apresentadas como informação comum ao usuário.

Quando necessárias para diagnóstico técnico, podem possuir referência interna protegida.

A Central de Auditoria não deve expor desnecessariamente valores reutilizáveis ou informações técnicas sensíveis.

---

## 27.30 CPF na Auditoria

Alterações de CPF podem ser preservadas na Auditoria.

O sistema deve permitir identificar que o documento foi alterado.

Na apresentação visual da Central de Auditoria, o CPF deve ser parcialmente mascarado.

Exemplo visual:

***.***.***-09.

A persistência deve preservar informação suficiente para rastreabilidade e integridade conforme a arquitetura adotada.

---

## 27.31 CNPJ na Auditoria

Alterações de CNPJ podem ser preservadas na Auditoria.

Na apresentação visual da Central de Auditoria, o documento pode ser parcialmente mascarado.

A Auditoria deve permitir identificar a alteração sem exposição visual desnecessária do documento completo.

---

## 27.32 E-mail na Auditoria

Alterações de E-mail podem ser preservadas.

Na Central de Auditoria, o E-mail pode ser parcialmente mascarado.

Exemplo:

m***@dominio.com.br.

A mascaragem visual não deve alterar o registro histórico persistido da alteração.

---

## 27.33 Telefone na Auditoria

Alterações de Telefone podem ser preservadas.

A interface pode aplicar mascaragem parcial quando necessário para reduzir exposição desnecessária.

O histórico deve continuar identificando que o campo foi alterado.

---

## 27.34 Usuário responsável

Toda ação autenticada deve utilizar o usuário real da Sessão como responsável.

O backend deve obter o usuário da Sessão autenticada.

O navegador não deve informar autoritativamente:

- ID do usuário responsável;
- Nome do usuário responsável;
- Perfil do usuário responsável.

---

## 27.35 Identificação histórica do usuário

O evento deve preservar:

- ID do usuário;
- Nome histórico do usuário no momento da ação;
- Perfil histórico no momento da ação.

Alterações futuras no cadastro do usuário não devem reescrever a identificação histórica do evento.

---

## 27.36 Perfil histórico

Exemplo:

Mauro realiza uma ação como Administrador.

Posteriormente, o perfil de Mauro é alterado para Operador.

A Auditoria antiga deve continuar apresentando:

Mauro — Administrador.

O perfil histórico representa o perfil utilizado no momento da ação.

---

## 27.37 Usuário desativado no histórico

Quando um usuário for desativado, seus eventos anteriores permanecem na Auditoria.

A Auditoria não deve remover ou anonimizar automaticamente o Nome histórico do usuário em razão da desativação operacional.

A situação atual do usuário não reescreve os eventos antigos.

---

## 27.38 Data e hora do evento

Cada evento de Auditoria deve possuir timestamp oficial.

O usuário não pode informar ou editar autoritativamente a data e hora do evento.

O timestamp deve ser gerado ou normalizado pelo backend.

---

## 27.39 Armazenamento do timestamp

Novos timestamps de Auditoria devem ser armazenados em UTC com offset explícito.

O sistema deve seguir a regra temporal oficial da aplicação.

---

## 27.40 Apresentação da data e hora

A apresentação dos eventos deve utilizar:

America/Sao_Paulo.

A ordenação cronológica deve utilizar o timestamp persistido.

---

## 27.41 Origem técnica do evento

Quando tecnicamente disponível e apropriado, o evento pode preservar informações de origem da ação.

Exemplos:

- Sessão;
- endereço IP;
- User-Agent.

Essas informações possuem finalidade de segurança e diagnóstico.

---

## 27.42 Sessão de origem

Quando a arquitetura possuir Sessões identificáveis, o evento pode manter referência interna à Sessão responsável pela ação.

A referência não deve permitir reutilização da Sessão.

Token ou Cookie de autenticação não deve ser persistido na Auditoria.

---

## 27.43 Endereço IP

O endereço IP pode ser registrado quando tecnicamente disponível.

A Auditoria não deve transformar automaticamente o IP em localização geográfica do usuário.

O IP possui finalidade de segurança e diagnóstico.

---

## 27.44 User-Agent e dispositivo

O User-Agent pode ser registrado quando tecnicamente disponível.

A interface pode apresentar informação simplificada.

Exemplo:

Chrome / Windows.

A apresentação simplificada não deve ser tratada como identificação infalível do dispositivo físico.

---

## 27.45 Ausência de origem técnica

A ausência de IP, User-Agent ou referência de Sessão não invalida automaticamente um evento de Auditoria.

Eventos internos ou operações técnicas podem não possuir todas as informações de origem.

O usuário responsável e a entidade afetada devem seguir as regras aplicáveis ao tipo de evento.

---

## 27.46 Tela Central de Auditoria

O sistema deve possuir tela:

AUDITORIA.

A tela é exclusiva do Administrador.

A interface deve permitir:

- busca;
- filtros;
- listagem;
- visualização de detalhes;
- exportação autorizada.

---

## 27.47 Busca da Auditoria

A Central de Auditoria deve permitir busca por:

- usuário;
- ação;
- entidade;
- número;
- referência.

A busca deve utilizar os dados históricos do evento.

---

## 27.48 Filtros da Auditoria

A Central deve permitir filtros por:

- período;
- usuário;
- módulo;
- tipo de ação.

Os filtros podem ser utilizados em conjunto com a busca.

---

## 27.49 Módulos da Auditoria

Os eventos devem possuir classificação por módulo.

Exemplos:

- Segurança;
- Usuários;
- Clientes;
- Produtos;
- Vendas;
- Condicionais;
- Crediário;
- Estoque;
- Financeiro;
- Fornecedores;
- Garantias;
- Inventário.

Novos módulos oficiais podem ser incluídos futuramente.

---

## 27.50 Tipo de ação

Os eventos devem possuir tipo de ação coerente.

Exemplos:

- Criado;
- Alterado;
- Desativado;
- Reativado;
- Cancelado;
- Finalizado;
- Pago;
- Recebido;
- Estornado;
- Bloqueado;
- Desbloqueado;
- Login realizado;
- Falha de Login.

A classificação deve facilitar busca e filtro.

---

## 27.51 Listagem da Auditoria

A listagem deve apresentar, no mínimo:

- Data e Hora;
- Usuário;
- Módulo;
- Ação;
- Referência;
- Ação de visualização.

A ação principal deve ser:

VER DETALHES.

---

## 27.52 Ordenação da Auditoria

A listagem deve apresentar inicialmente os eventos mais recentes.

Ordenação padrão:

Data e Hora decrescente.

A implementação pode permitir outras ordenações sem alterar o histórico persistido.

---

## 27.53 Referência do evento

A referência deve identificar a entidade ou operação afetada.

Exemplos:

Venda nº 125.

Garantia nº 32.

Inventário nº 8.

Produto 789123.

Cliente João da Silva.

Quando existir identificador persistente próprio, o evento deve preservar o vínculo correspondente.

---

## 27.54 Detalhes do evento

Ao selecionar VER DETALHES, apresentar:

- Usuário;
- Perfil histórico;
- Data e Hora;
- Módulo;
- Ação;
- Entidade;
- Referência;
- Alterações;
- Origem técnica, quando disponível.

Informações secretas devem permanecer protegidas.

---

## 27.55 Alterações nos detalhes

Quando o evento representar edição, apresentar somente os campos alterados.

Para cada campo, apresentar:

- Campo;
- Antes;
- Depois.

A interface deve aplicar as regras de mascaragem visual correspondentes.

---

## 27.56 Evento sem comparação de campos

Quando o evento não possuir comparação Antes e Depois, os detalhes devem apresentar os dados relevantes da ação.

Exemplo:

Ação:
Inventário finalizado.

Referência:
Inventário nº 15.

Produtos com divergência:
8.

Ajustes positivos:
5.

Ajustes negativos:
3.

Não criar comparação artificial de campos.

---

## 27.57 Exportação da Auditoria

Somente Administrador pode exportar dados da Central de Auditoria.

Os formatos oficiais são:

- PDF;
- CSV.

A autorização deve ser validada no backend.

---

## 27.58 Exportação e filtros

A exportação deve respeitar os filtros aplicados.

Exemplo:

Período:
01/07/2026 a 31/07/2026.

Módulo:
Vendas.

Usuário:
Mauro.

O arquivo exportado deve conter somente os eventos correspondentes ao conjunto filtrado.

---

## 27.59 Exportação em PDF

O PDF deve seguir as regras oficiais de Impressões e Documentos Gerados.

Deve apresentar, conforme aplicável:

- identificação da loja;
- título Auditoria;
- período;
- filtros aplicados;
- data de geração;
- usuário Administrador responsável pela exportação;
- eventos correspondentes.

Dados sensíveis devem seguir as regras de mascaragem visual.

---

## 27.60 Exportação em CSV

O CSV deve representar os eventos filtrados em estrutura tabular.

Pode conter, conforme aplicável:

- timestamp;
- usuário;
- perfil histórico;
- módulo;
- ação;
- entidade;
- referência.

Alterações estruturadas podem ser representadas de forma compatível com exportação tabular.

Segredos e credenciais não podem ser exportados.

---

## 27.61 Auditoria da exportação

A exportação da Central de Auditoria deve gerar evento de Auditoria.

O evento deve registrar:

- Administrador responsável;
- data e hora;
- formato;
- filtros gerais utilizados.

Não registrar o conteúdo integral do arquivo dentro do evento.

---

## 27.62 Retenção da Auditoria

Não existe prazo automático de exclusão dos eventos de Auditoria.

Os registros não devem ser apagados automaticamente após:

- 30 dias;
- 1 ano;
- 5 anos;
- outro prazo operacional fixo.

A Auditoria permanece preservada enquanto a loja existir no sistema.

---

## 27.63 Crescimento do volume de Auditoria

O crescimento do volume não autoriza exclusão silenciosa de eventos.

Quando necessário, a arquitetura pode implementar:

- arquivamento;
- particionamento;
- armazenamento histórico;
- otimização de consulta.

Essas medidas não devem eliminar o histórico de Auditoria.

---

## 27.64 Paginação da Auditoria

A Central de Auditoria deve utilizar paginação real ou mecanismo equivalente de consulta incremental.

O sistema não deve exigir o carregamento de todo o histórico da loja no navegador.

Busca, filtros e paginação devem ser processados de forma compatível com o volume de dados.

---

## 27.65 Auditoria e operações transacionais

Quando uma ação de negócio e sua Auditoria representarem a mesma operação crítica, o registro da Auditoria deve integrar a mesma unidade transacional sempre que aplicável.

Exemplos:

- recebimento de Crediário;
- finalização de Inventário;
- pagamento de Conta;
- cancelamento financeiro.

A operação não deve ser concluída financeiramente e perder sua Auditoria por falha posterior evitável.

---

## 27.66 Rollback da Auditoria transacional

Quando a operação principal sofrer rollback completo, o evento de sucesso correspondente não deve permanecer na Auditoria como se a ação tivesse sido concluída.

Exemplo:

Recebimento falhou.

Pagamento revertido pela transação.

Não registrar:

Recebimento concluído.

Eventos técnicos de falha podem seguir mecanismo próprio de Logs ou Segurança.

---

## 27.67 Auditoria de operações idempotentes

Operações protegidas por idempotência não devem gerar eventos de sucesso duplicados em caso de replay.

Exemplo:

Mesmo recebimento reenviado com a mesma chave e o mesmo conteúdo.

Resultado financeiro:
um recebimento.

Auditoria:
um evento de recebimento concluído.

A resposta reapresentada não representa nova ação financeira.

---

## 27.68 Concorrência

A Auditoria deve preservar a ordem temporal real possível das operações concorrentes.

O sistema não deve reescrever evento anterior para refletir estado futuro.

Cada evento representa a ação concluída correspondente.

---

## 27.69 Integridade do evento

Campos autoritativos do evento devem ser definidos pelo backend.

O navegador não deve informar autoritativamente:

- usuário responsável;
- perfil histórico;
- timestamp;
- loja;
- módulo de segurança;
- origem técnica.

Dados da operação podem ser utilizados para compor a referência somente após validação.

---

## 27.70 Isolamento por loja

Todo evento de Auditoria deve permanecer vinculado à loja correspondente.

Administrador pode consultar somente a Auditoria da loja autenticada.

O sistema deve impedir:

- consultar eventos de outra loja;
- exportar Auditoria de outra loja;
- abrir detalhes de evento de outra loja.

A validação deve ocorrer no backend.

---

## 27.71 Estado de carregamento

A Central de Auditoria deve possuir estado de carregamento claro.

Ao alterar:

- busca;
- período;
- usuário;
- módulo;
- tipo de ação;
- página

dados antigos não devem ser apresentados provisoriamente como se correspondessem ao filtro atual.

---

## 27.72 Estado de erro

Falha de rede ou servidor deve apresentar estado de erro discreto.

Deve ser possível tentar novamente.

Erro de autenticação deve seguir o fluxo oficial de Sessão expirada.

Erro de autorização não deve exibir dados da Auditoria.

---

## 27.73 Estado vazio

Quando nenhum evento corresponder aos filtros, apresentar estado vazio claro.

Exemplo:

Nenhum evento de Auditoria encontrado.

Não criar eventos artificiais para preencher a listagem.

---

## 27.74 Fonte autoritativa

O backend deve definir e validar:

- loja;
- usuário responsável;
- perfil histórico;
- timestamp;
- módulo;
- ação;
- entidade;
- referência validada;
- alterações;
- origem técnica.

O navegador não deve ser fonte autoritativa desses campos.

---

## 27.75 Regras gerais da Auditoria e Histórico de Operações

O sistema deve:

- possuir Central de Auditoria;
- permitir acesso somente ao Administrador;
- impedir acesso do Operador à Central;
- manter históricos operacionais acessíveis conforme os módulos;
- não substituir históricos próprios dos módulos;
- manter Auditoria e históricos operacionais simultaneamente;
- tornar eventos de Auditoria imutáveis;
- impedir edição de Auditoria;
- impedir exclusão de Auditoria;
- auditar ações relevantes;
- não auditar indiscriminadamente cada clique;
- auditar eventos de Segurança;
- auditar Login válido;
- auditar falha de Login identificável;
- auditar bloqueio;
- auditar desbloqueio;
- auditar recuperação de senha concluída;
- auditar redefinição de senha;
- auditar alteração de perfil;
- auditar eventos relevantes de Usuários;
- auditar eventos relevantes de Clientes;
- auditar eventos relevantes de Produtos;
- auditar eventos relevantes de Estoque;
- auditar eventos relevantes de Vendas;
- auditar eventos relevantes de Condicionais;
- auditar eventos relevantes de Crediário;
- auditar eventos financeiros;
- auditar eventos de Fornecedores;
- auditar eventos de Garantias;
- auditar eventos de Inventário;
- não exigir Auditoria para abertura de tela;
- não exigir Auditoria para busca;
- não exigir Auditoria para filtro;
- preservar Antes e Depois em edições relevantes;
- registrar somente campos efetivamente alterados;
- não registrar senha;
- não registrar hash de senha;
- não registrar Token de Sessão;
- não registrar Token de recuperação;
- não registrar Código de recuperação;
- não expor chaves técnicas sensíveis;
- preservar alterações de CPF;
- mascarar CPF visualmente;
- preservar alterações de CNPJ;
- mascarar CNPJ visualmente;
- preservar alterações de E-mail;
- permitir mascaragem visual do E-mail;
- preservar alterações de Telefone;
- obter usuário responsável da Sessão;
- preservar ID do usuário;
- preservar Nome histórico;
- preservar Perfil histórico;
- não reescrever eventos após alteração de perfil;
- manter eventos de usuário desativado;
- gerar timestamp no backend;
- armazenar novos timestamps em UTC com offset explícito;
- apresentar datas em America/Sao_Paulo;
- permitir origem técnica;
- permitir referência à Sessão;
- não persistir Token de Sessão na Auditoria;
- permitir registro de IP;
- não transformar IP automaticamente em geolocalização;
- permitir registro de User-Agent;
- possuir busca;
- permitir busca por usuário;
- permitir busca por ação;
- permitir busca por entidade;
- permitir busca por número ou referência;
- possuir filtros;
- permitir filtro por período;
- permitir filtro por usuário;
- permitir filtro por módulo;
- permitir filtro por tipo de ação;
- classificar eventos por módulo;
- classificar eventos por ação;
- listar Data e Hora;
- listar Usuário;
- listar Módulo;
- listar Ação;
- listar Referência;
- possuir VER DETALHES;
- ordenar inicialmente pelos eventos mais recentes;
- preservar vínculo com entidade;
- apresentar Perfil histórico nos detalhes;
- apresentar alterações;
- apresentar origem técnica quando disponível;
- permitir exportação em PDF;
- permitir exportação em CSV;
- permitir exportação somente ao Administrador;
- respeitar filtros na exportação;
- mascarar dados sensíveis na exportação visual;
- auditar exportação da Central;
- não possuir exclusão automática por prazo;
- preservar Auditoria enquanto a loja existir;
- permitir arquivamento técnico sem perda histórica;
- utilizar paginação real ou consulta incremental;
- integrar Auditoria às operações transacionais críticas;
- não registrar sucesso após rollback;
- evitar eventos duplicados em replay idempotente;
- tratar concorrência;
- utilizar backend como fonte autoritativa;
- respeitar isolamento por loja;
- possuir estado de carregamento;
- possuir estado de erro;
- possuir estado vazio.

# 28. CONFIGURAÇÕES DA LOJA

## 28.1 Finalidade das Configurações da Loja

O módulo Configurações da Loja centraliza dados e parâmetros administrativos permitidos da loja.

As Configurações não devem permitir alteração livre de regras estruturais fixas do sistema.

Somente parâmetros expressamente definidos nesta seção podem ser alterados pelo Administrador.

---

## 28.2 Acesso às Configurações

Somente Administrador pode acessar a tela Configurações da Loja.

Operador não pode acessar ou alterar Configurações da Loja.

A autorização deve ser validada no backend.

Ocultar a opção no frontend não substitui a validação de permissão.

---

## 28.3 Dados da Loja

As Configurações devem permitir editar:

- Nome da Loja;
- Razão Social;
- CPF ou CNPJ;
- Telefone;
- WhatsApp;
- E-mail;
- CEP;
- Endereço;
- Número;
- Bairro;
- Cidade;
- Estado.

Nome da Loja é obrigatório.

Os demais campos são opcionais, salvo quando outra regra futura estabelecer obrigatoriedade específica.

---

## 28.4 CPF ou CNPJ da Loja

Quando CPF ou CNPJ for informado, o documento deve ser validado matematicamente.

CPF inválido deve ser recusado.

CNPJ inválido deve ser recusado.

O documento deve ser normalizado para validação e persistência conforme o padrão oficial do sistema.

A validação autoritativa deve ocorrer no backend.

---

## 28.5 Utilização dos dados da Loja

Os dados da Loja podem ser utilizados em:

- PDFs;
- impressões;
- comprovantes;
- relatórios;
- documentos gerados pelo sistema.

Os documentos devem utilizar os dados atuais da Loja no momento de sua geração.

---

## 28.6 Logo da Loja

O Administrador pode cadastrar Logo da Loja.

Os formatos permitidos são:

- PNG;
- JPG;
- JPEG;
- WEBP.

SVG não deve ser aceito inicialmente.

---

## 28.7 Utilização da Logo

A Logo pode ser utilizada em:

- tela de Login;
- cabeçalho do sistema;
- PDFs;
- impressões;
- comprovantes.

Quando não existir Logo cadastrada, o sistema deve utilizar o Nome da Loja quando uma identificação visual for necessária.

---

## 28.8 Validação do arquivo da Logo

O backend deve validar o arquivo enviado.

A validação não deve confiar somente:

- na extensão do arquivo;
- no MIME informado pelo navegador.

Arquivos incompatíveis devem ser recusados.

A implementação deve possuir limite técnico de tamanho de arquivo compatível com a finalidade da Logo.

---

## 28.9 Substituição da Logo

O Administrador pode substituir a Logo atual.

A nova Logo passa a ser utilizada nas novas renderizações e documentos gerados.

Documentos históricos já gerados não devem ser reescritos automaticamente.

---

## 28.10 Tema e Aparência

O sistema deve permitir as opções:

- Tema Claro;
- Tema Escuro;
- Seguir Sistema.

A preferência de Tema pertence ao usuário.

Não é uma Configuração global da Loja.

---

## 28.11 Preferência de Tema por usuário

Cada usuário pode possuir sua própria preferência de Tema.

Exemplo:

Administrador utiliza Tema Escuro.

Operador utiliza Tema Claro.

Alterar a preferência de um usuário não altera a aparência dos demais usuários.

---

## 28.12 Seguir Sistema

Quando a opção Seguir Sistema estiver selecionada, a interface deve acompanhar a preferência de aparência informada pelo ambiente do usuário quando tecnicamente disponível.

A preferência persistida continua sendo:

Seguir Sistema.

Não substituir automaticamente a preferência persistida por Claro ou Escuro.

---

## 28.13 Dados Pix da Loja

As Configurações devem permitir cadastrar informações de recebimento por Pix.

Os campos são:

- Chave Pix;
- Tipo da Chave Pix;
- Nome do favorecido;
- CPF ou CNPJ do favorecido;
- Banco, opcional.

---

## 28.14 Tipos de Chave Pix

Quando Chave Pix for cadastrada, o sistema deve permitir identificar o Tipo da Chave.

Exemplos:

- CPF;
- CNPJ;
- E-mail;
- Telefone;
- Chave aleatória.

A validação deve ser compatível com o Tipo informado quando aplicável.

---

## 28.15 Dados Pix são informativos

O cadastro dos dados Pix possui finalidade informativa e documental.

O sistema não deve presumir integração bancária.

O cadastro não representa:

- geração automática de cobrança Pix;
- confirmação automática de pagamento;
- consulta bancária;
- conciliação Pix automática.

Integração bancária depende de implementação específica futura.

---

## 28.16 Utilização dos dados Pix

Os dados Pix podem ser apresentados em documentos ou comprovantes quando aplicável.

A exibição deve utilizar os dados atuais cadastrados.

Documentos históricos já gerados não devem ser reescritos após alteração dos dados Pix.

---

## 28.17 Formas oficiais de pagamento

As formas oficiais de pagamento são:

- Dinheiro;
- Pix;
- Débito;
- Crédito;
- Crediário.

O Administrador não pode criar novas Formas de Pagamento pela tela de Configurações.

---

## 28.18 Identificadores internos das Formas de Pagamento

As Formas de Pagamento devem utilizar identificadores internos oficiais e estáveis.

Exemplos conceituais:

- cash;
- pix;
- debit;
- credit;
- storeCredit.

O Administrador não pode alterar os identificadores internos.

---

## 28.19 Nome das Formas de Pagamento

O Administrador não pode renomear as Formas oficiais de Pagamento.

Exemplo:

Crédito não pode ser renomeado para Parcelado.

Crediário não pode ser renomeado para Fiado.

Os nomes oficiais devem permanecer coerentes em todo o sistema.

---

## 28.20 Disponibilidade das Formas de Pagamento

O Administrador pode ativar ou desativar a disponibilidade comercial de:

- Pix;
- Débito;
- Crédito;
- Crediário.

Dinheiro permanece sempre ativo.

---

## 28.21 Dinheiro obrigatório

A Forma de Pagamento Dinheiro não pode ser desativada.

A tela não deve oferecer ação de desativação para Dinheiro.

O backend deve recusar tentativa de desativação por requisição manipulada.

---

## 28.22 Forma de Pagamento desativada

Forma de Pagamento desativada não deve estar disponível para novas Vendas.

O backend deve recusar nova Venda que utilize Forma de Pagamento atualmente desativada.

Não confiar somente na ausência da opção na interface.

---

## 28.23 Histórico de Forma de Pagamento desativada

Desativar uma Forma de Pagamento não altera operações históricas.

Exemplo:

Crediário foi desativado.

Crediários antigos continuam existindo.

Recebimentos antigos permanecem preservados.

Parcelas existentes continuam podendo ser recebidas conforme as regras oficiais.

---

## 28.24 Pix desativado

Quando Pix estiver desativado, novas Vendas não podem utilizar Pix.

Vendas históricas pagas por Pix permanecem identificadas como Pix.

Movimentações financeiras históricas não devem ser reclassificadas.

---

## 28.25 Débito desativado

Quando Débito estiver desativado, novas Vendas não podem utilizar Débito.

Recebíveis bancários históricos de Débito permanecem operacionais e podem ser conciliados.

---

## 28.26 Crédito desativado

Quando Crédito estiver desativado, novas Vendas não podem utilizar Crédito.

Recebíveis bancários históricos de Crédito permanecem operacionais e podem ser conciliados.

---

## 28.27 Crediário desativado

Quando Crediário estiver desativado, novas Vendas não podem criar novo Crediário.

Crediários existentes permanecem operacionais.

O sistema deve continuar permitindo, conforme as regras oficiais:

- recebimentos;
- pagamentos parciais;
- pagamentos antecipados;
- estornos;
- renegociações;
- demais operações válidas sobre Crediário existente.

---

## 28.28 Parcelamento no Cartão de Crédito

Pagamento em Cartão de Crédito pode ser informado como:

- 1x;
- 2x;
- 3x.

Não permitir quantidade superior a 3 parcelas.

---

## 28.29 Máximo fixo de parcelas no Crédito

O máximo de parcelas no Cartão de Crédito é fixo em:

3 parcelas.

O valor não é configurável pelo Administrador.

A tela de Configurações não deve possuir campo Máximo de Parcelas no Crédito.

---

## 28.30 Parcelamento do Cartão não é Crediário

A quantidade de parcelas informada no pagamento em Cartão de Crédito possui finalidade de identificação do pagamento e cálculo da taxa aplicável.

Pagamento em Crédito 2x ou 3x não cria Crediário.

Não criar parcelas de Crediário para pagamento em Cartão.

Não vincular o pagamento às regras de Limite de Crédito do Cliente.

---

## 28.31 Informação do parcelamento na Venda

A Venda deve preservar a quantidade de parcelas do pagamento em Crédito.

Exemplos:

Crédito 1x.

Crédito 2x.

Crédito 3x.

A informação deve permanecer histórica.

---

## 28.32 Débito

Pagamento em Débito não possui parcelamento.

A regra oficial do Débito corresponde a uma única operação de cartão.

A taxa aplicável deve utilizar a configuração específica de Débito.

---

## 28.33 Bandeiras de Cartão

O sistema não deve exigir informação de Bandeira do Cartão.

Não criar cadastro obrigatório de Bandeiras.

Não exigir seleção de:

- Visa;
- Mastercard;
- Elo;
- American Express;
- Hipercard;
- outra Bandeira.

---

## 28.34 Pagamento com Cartão sem Bandeira

Para pagamento em Débito ou Crédito, o sistema deve registrar a Forma de Pagamento e, no Crédito, a quantidade de parcelas.

Exemplos:

Débito.

Crédito 1x.

Crédito 2x.

Crédito 3x.

A ausência de Bandeira não invalida o pagamento.

---

## 28.35 Configuração das Taxas de Cartão

O Administrador deve poder cadastrar as taxas aplicáveis às operações de cartão.

As taxas configuráveis são:

- Débito;
- Crédito 1x;
- Crédito 2x;
- Crédito 3x.

Não existe configuração de taxa por Bandeira.

---

## 28.36 Taxa de Débito

A Configuração deve permitir informar a taxa percentual do Débito.

Exemplo:

Débito:
1,50%.

A taxa deve ser utilizada nas novas operações em Débito.

---

## 28.37 Taxa de Crédito 1x

A Configuração deve permitir informar a taxa percentual do Crédito 1x.

Exemplo:

Crédito 1x:
2,50%.

A taxa deve ser utilizada nas novas operações de Crédito em 1 parcela.

---

## 28.38 Taxa de Crédito 2x

A Configuração deve permitir informar a taxa percentual do Crédito 2x.

Exemplo:

Crédito 2x:
3,10%.

A taxa deve ser utilizada nas novas operações de Crédito em 2 parcelas.

---

## 28.39 Taxa de Crédito 3x

A Configuração deve permitir informar a taxa percentual do Crédito 3x.

Exemplo:

Crédito 3x:
3,50%.

A taxa deve ser utilizada nas novas operações de Crédito em 3 parcelas.

---

## 28.40 Validação das Taxas

As taxas devem ser valores numéricos e finitos.

Não permitir:

- NaN;
- infinito;
- valor negativo;
- texto inválido.

A taxa zero deve ser permitida.

A validação autoritativa deve ocorrer no backend.

---

## 28.41 Unidade das Taxas

As taxas de Cartão devem representar percentual.

Exemplo:

3,50%.

O sistema deve possuir representação persistente que evite ambiguidade entre:

3,50%.

e:

350%.

A conversão e o cálculo devem ser realizados de forma consistente no backend.

---

## 28.42 Taxa autoritativa na Venda

O navegador não deve informar autoritativamente a taxa financeira aplicada ao pagamento.

Ao criar a Venda, o backend deve localizar a configuração vigente correspondente à operação.

Exemplos:

Débito:
Taxa de Débito.

Crédito 2x:
Taxa de Crédito 2x.

---

## 28.43 Fotografia da Taxa na Venda

A taxa utilizada deve ser preservada no pagamento ou recebível correspondente à Venda.

A operação deve fotografar a taxa vigente no momento da Venda.

Alterações futuras nas Configurações não devem modificar a taxa histórica.

---

## 28.44 Valor bruto do Cartão

O sistema deve preservar o valor bruto do componente pago em Cartão.

Exemplo:

Crédito 2x.

Valor bruto:
R$ 1.000,00.

O valor bruto representa o valor do pagamento atribuído à Venda.

---

## 28.45 Valor da Taxa

O sistema deve calcular o valor estimado da taxa.

Fórmula conceitual:

Valor da Taxa =
Valor bruto x Taxa percentual.

O cálculo financeiro deve utilizar a política oficial de precisão e arredondamento monetário do sistema.

---

## 28.46 Valor líquido esperado

O sistema deve calcular:

Valor líquido esperado =
Valor bruto - Valor da Taxa.

Exemplo:

Valor bruto:
R$ 1.000,00.

Taxa:
3,50%.

Valor da Taxa:
R$ 35,00.

Valor líquido esperado:
R$ 965,00.

---

## 28.47 Pagamento da Venda e Taxa do Cartão

Para fins de quitação da Venda, o pagamento em Cartão deve considerar o valor bruto atribuído pelo Cliente.

Exemplo:

Venda:
R$ 1.000,00.

Crédito:
R$ 1.000,00.

Taxa:
R$ 35,00.

Venda:
Paga em R$ 1.000,00.

A taxa não cria saldo devedor para o Cliente.

O custo da taxa pertence à operação financeira da Loja.

---

## 28.48 Recebível bancário do Cartão

Pagamento em Débito ou Crédito deve gerar recebível bancário.

O recebível deve preservar, no mínimo:

- Forma de Pagamento;
- quantidade de parcelas, quando Crédito;
- valor bruto;
- taxa percentual fotografada;
- valor estimado da taxa;
- valor líquido esperado;
- data da Venda;
- previsão de recebimento;
- Venda de origem.

---

## 28.49 Antecipação das operações de Crédito

A Loja trabalha com antecipação das operações de Cartão de Crédito.

Por essa razão, Crédito 1x, Crédito 2x e Crédito 3x possuem previsão operacional de recebimento em 1 dia.

O sistema não deve gerar previsões separadas em:

- 30 dias;
- 60 dias;
- 90 dias.

---

## 28.50 Previsão de recebimento do Débito

Pagamento em Débito possui previsão de recebimento em:

1 dia.

A previsão deve ser calculada a partir da data operacional da Venda conforme a regra temporal oficial.

---

## 28.51 Previsão de recebimento do Crédito

Pagamento em Crédito possui previsão de recebimento em:

1 dia.

A regra se aplica a:

- Crédito 1x;
- Crédito 2x;
- Crédito 3x.

A quantidade de parcelas altera a taxa aplicável, mas não altera o prazo esperado de recebimento.

---

## 28.52 Recebível único por componente de Cartão

Como a operação utiliza antecipação, cada componente de pagamento em Cartão deve gerar recebível bancário correspondente ao valor líquido esperado da operação.

Crédito 2x ou 3x não deve gerar automaticamente dois ou três recebíveis mensais.

A quantidade de parcelas permanece preservada como informação histórica e financeira da operação.

---

## 28.53 Data prevista do recebível

A data prevista deve considerar o prazo fixo de 1 dia.

O cálculo deve utilizar a data operacional oficial em America/Sao_Paulo.

A persistência temporal deve seguir as regras oficiais do sistema.

---

## 28.54 Conciliação do recebível

A conciliação bancária deve comparar o recebimento efetivo com o recebível esperado correspondente.

A conciliação deve respeitar:

- Forma de Pagamento;
- Venda de origem ou vínculo financeiro persistente;
- valor líquido esperado;
- previsão de recebimento.

O sistema não deve conciliar Crédito contra Débito apenas por ordem de criação.

---

## 28.55 Diferença na conciliação

Quando o valor efetivamente recebido for diferente do valor líquido esperado, o sistema deve preservar a diferença para análise.

Exemplo:

Líquido esperado:
R$ 965,00.

Recebido:
R$ 960,00.

Diferença:
-R$ 5,00.

A diferença não deve reescrever a taxa histórica fotografada.

---

## 28.56 Taxa alterada após a Venda

Alterar uma taxa nas Configurações afeta somente novas operações.

Exemplo:

Crédito 3x.

Taxa anterior:
3,50%.

Venda realizada:
Taxa fotografada em 3,50%.

Nova configuração:
3,80%.

A Venda antiga permanece com 3,50%.

Novas Vendas utilizam 3,80%.

---

## 28.57 Regras fixas do sistema

Determinadas regras são fixas e não devem ser apresentadas como Configurações da Loja.

As regras fixas devem ser alteradas somente por evolução formal das regras de negócio e implementação correspondente.

---

## 28.58 Prazo fixo do Condicional

O prazo oficial do Condicional é:

3 dias.

Não criar campo de Configuração para alterar esse prazo.

---

## 28.59 Prazo fixo de Troca

O prazo oficial de Troca é:

30 dias.

Não criar campo de Configuração para alterar esse prazo.

---

## 28.60 Máximo fixo do Crediário

O máximo oficial do Crediário é:

3 parcelas.

Não criar campo de Configuração para aumentar ou reduzir esse limite.

---

## 28.61 Sugestão da primeira parcela do Crediário

A primeira parcela do Crediário deve sugerir vencimento em:

30 dias.

A data pode ser informada pelo usuário conforme as regras oficiais do Crediário.

Não criar Configuração para alterar a sugestão padrão.

---

## 28.62 Parcelas seguintes do Crediário

A segunda e a terceira parcelas devem utilizar o mesmo dia-base da primeira parcela nos meses seguintes, conforme as regras oficiais do Crediário.

Não criar Configuração para alterar essa regra.

---

## 28.63 Estoque Mínimo padrão

O Estoque Mínimo padrão é:

0.

O valor zero é permitido.

Não existe obrigação de alterar o Estoque Mínimo no cadastro do Produto.

---

## 28.64 Estoque Mínimo e Alertas

Estoque Mínimo não deve gerar alerta.

Não criar Configuração para ativar alerta de Estoque Mínimo.

---

## 28.65 Garantia sem atualização

Garantia Enviada ao Fornecedor deve gerar alerta após:

7 dias sem atualização válida.

Não criar Configuração para alterar o prazo.

---

## 28.66 Máximo de falhas de Login

O máximo oficial de falhas consecutivas de Login é:

5.

Não criar Configuração para alterar a quantidade.

---

## 28.67 Bloqueio temporário do único Administrador

O bloqueio temporário do único Administrador ativo é:

15 minutos.

Não criar Configuração para alterar o prazo.

---

## 28.68 Validade da recuperação de senha

Token ou Código de recuperação de senha possui validade máxima de:

30 minutos.

Não criar Configuração para alterar o prazo.

---

## 28.69 Sessão sem Lembrar-me

A Sessão sem Lembrar-me possui validade máxima de:

12 horas.

Não criar Configuração para alterar a duração.

---

## 28.70 Sessão com Lembrar-me

A Sessão com Lembrar-me possui validade máxima de:

30 dias.

Não criar Configuração para alterar a duração.

---

## 28.71 Máximo de parcelas no Cartão

O máximo oficial do Cartão de Crédito é:

3 parcelas.

Não criar Configuração para alterar esse limite.

---

## 28.72 Prazo esperado do Cartão

O prazo operacional esperado de recebimento de Débito e Crédito é:

1 dia.

A regra considera a operação atual da Loja com antecipação de Crédito.

Não criar Configuração para alterar o prazo neste momento.

---

## 28.73 Auditoria das Configurações

Toda alteração relevante nas Configurações da Loja deve gerar evento de Auditoria.

A Auditoria deve seguir as regras oficiais da Central de Auditoria.

---

## 28.74 Alteração de dados da Loja

Alterações cadastrais devem preservar os campos efetivamente modificados.

Exemplo:

Telefone.

Antes:
(48) 99999-1111.

Depois:
(48) 99999-2828.

Campos sem alteração não devem ser registrados artificialmente.

---

## 28.75 Alteração de disponibilidade de pagamento

Ativação ou desativação de Forma de Pagamento deve gerar evento de Auditoria.

Exemplo:

Mauro desativou Crediário como Forma de Pagamento.

O evento deve preservar:

- usuário;
- data e hora;
- Forma de Pagamento;
- situação anterior;
- situação nova.

---

## 28.76 Alteração de taxa

Alteração de Taxa de Cartão deve gerar evento de Auditoria.

Exemplo:

Taxa Crédito 3x.

Antes:
3,50%.

Depois:
3,80%.

O histórico não deve reescrever Vendas antigas.

---

## 28.77 Alteração da Logo

Substituição ou remoção da Logo deve gerar evento de Auditoria.

O evento deve registrar a ação.

Não é necessário armazenar o conteúdo binário completo da imagem dentro do evento de Auditoria.

---

## 28.78 Central de Auditoria como histórico das Configurações

Não é necessário criar segunda tela de histórico dentro das Configurações.

A Central de Auditoria é o histórico oficial das alterações administrativas.

A tela de Configurações pode apresentar somente os valores atuais.

---

## 28.79 Efeito histórico das Configurações

Alterar Configuração não deve reescrever automaticamente operações históricas.

A regra se aplica a dados e parâmetros com efeito operacional.

---

## 28.80 Taxa histórica

Alterar Taxa de Cartão não modifica:

- Venda antiga;
- pagamento antigo;
- recebível antigo;
- valor líquido esperado histórico.

A taxa fotografada permanece preservada.

---

## 28.81 Forma de Pagamento histórica

Desativar Forma de Pagamento não altera o método registrado em Venda histórica.

Exemplo:

Venda paga em Pix permanece identificada como Pix mesmo após desativação do Pix para novas Vendas.

---

## 28.82 Parcelamento histórico do Cartão

Pagamento histórico em Crédito deve preservar a quantidade de parcelas informada no momento da Venda.

Alterações futuras nas regras do sistema não devem reclassificar automaticamente a operação histórica.

---

## 28.83 Logo e documentos históricos

Alterar a Logo não deve reescrever arquivos já gerados.

Novos documentos utilizam a Logo atual.

Documentos históricos persistidos permanecem como foram gerados.

---

## 28.84 Dados da Loja e documentos históricos

Alterar Nome, Endereço ou outros dados da Loja não deve reescrever documentos históricos já persistidos.

Novos documentos utilizam os dados atuais.

---

## 28.85 Validação autoritativa das Configurações

O backend deve validar:

- permissão administrativa;
- dados da Loja;
- CPF ou CNPJ;
- arquivo da Logo;
- disponibilidade das Formas de Pagamento;
- taxas;
- valores numéricos;
- regras fixas do sistema.

O navegador não deve ser fonte autoritativa das Configurações.

---

## 28.86 Atomicidade da alteração

Alterações de Configuração e seu evento de Auditoria devem ser persistidos de forma consistente.

Quando uma alteração crítica falhar, o sistema não deve apresentar a nova Configuração como aplicada.

O evento de sucesso não deve permanecer se a alteração sofrer rollback.

---

## 28.87 Concorrência nas Configurações

O sistema deve tratar alterações concorrentes realizadas por Administradores.

Uma alteração não deve sobrescrever silenciosamente outra alteração baseada em estado antigo.

A implementação deve utilizar mecanismo de controle compatível.

Conflito deve ser informado ao usuário quando aplicável.

---

## 28.88 Isolamento por Loja

As Configurações pertencem à Loja autenticada.

Administrador não pode:

- consultar Configurações de outra Loja;
- alterar Configurações de outra Loja;
- utilizar Taxas de outra Loja;
- alterar Logo de outra Loja.

A validação deve ocorrer no backend.

---

## 28.89 Regras gerais das Configurações da Loja

O sistema deve:

- possuir Configurações da Loja;
- permitir acesso somente ao Administrador;
- impedir acesso do Operador;
- permitir editar Nome da Loja;
- exigir Nome da Loja;
- permitir Razão Social;
- permitir CPF ou CNPJ;
- validar CPF matematicamente;
- validar CNPJ matematicamente;
- permitir Telefone;
- permitir WhatsApp;
- permitir E-mail;
- permitir Endereço completo;
- utilizar dados da Loja em documentos;
- permitir Logo;
- aceitar PNG;
- aceitar JPG;
- aceitar JPEG;
- aceitar WEBP;
- não aceitar SVG inicialmente;
- validar arquivo no backend;
- permitir substituição da Logo;
- utilizar Nome da Loja quando não existir Logo;
- possuir Tema Claro;
- possuir Tema Escuro;
- possuir Seguir Sistema;
- manter Tema por usuário;
- permitir dados Pix;
- identificar Tipo da Chave Pix;
- não presumir integração bancária;
- utilizar dados Pix de forma informativa;
- manter Dinheiro;
- manter Pix;
- manter Débito;
- manter Crédito;
- manter Crediário;
- impedir criação livre de novas Formas de Pagamento;
- impedir renomear Formas oficiais;
- manter Dinheiro sempre ativo;
- permitir ativar ou desativar Pix;
- permitir ativar ou desativar Débito;
- permitir ativar ou desativar Crédito;
- permitir ativar ou desativar Crediário;
- impedir nova operação com Forma desativada;
- preservar operações históricas;
- permitir Crédito 1x;
- permitir Crédito 2x;
- permitir Crédito 3x;
- impedir Crédito acima de 3x;
- manter máximo de 3x fixo;
- não tratar Cartão como Crediário;
- preservar quantidade de parcelas do Crédito;
- não parcelar Débito;
- não exigir Bandeira;
- não possuir cadastro obrigatório de Bandeiras;
- permitir Taxa de Débito;
- permitir Taxa de Crédito 1x;
- permitir Taxa de Crédito 2x;
- permitir Taxa de Crédito 3x;
- permitir taxa zero;
- impedir taxa negativa;
- calcular taxa no backend;
- fotografar taxa na Venda;
- preservar valor bruto;
- calcular valor da taxa;
- calcular valor líquido esperado;
- considerar valor bruto para quitação da Venda;
- gerar recebível bancário;
- vincular recebível à Venda;
- utilizar antecipação no Crédito;
- prever Débito em 1 dia;
- prever Crédito 1x em 1 dia;
- prever Crédito 2x em 1 dia;
- prever Crédito 3x em 1 dia;
- não gerar recebíveis mensais separados para Crédito parcelado;
- preservar quantidade de parcelas;
- conciliar por vínculo financeiro válido;
- não conciliar Débito contra Crédito por FIFO genérico;
- preservar diferenças de conciliação;
- não reescrever taxa histórica;
- manter prazo de Condicional fixo em 3 dias;
- manter prazo de Troca fixo em 30 dias;
- manter Crediário limitado a 3 parcelas;
- sugerir primeira parcela do Crediário em 30 dias;
- utilizar mesmo dia-base nas parcelas seguintes;
- manter Estoque Mínimo padrão em zero;
- permitir Estoque Mínimo zero;
- não gerar alerta de Estoque Mínimo;
- gerar alerta de Garantia após 7 dias sem atualização;
- manter 5 falhas máximas de Login;
- manter bloqueio temporário do único Administrador em 15 minutos;
- manter recuperação de senha em 30 minutos;
- manter Sessão normal em 12 horas;
- manter Lembrar-me em 30 dias;
- manter máximo de Crédito em 3x;
- manter prazo esperado do Cartão em 1 dia;
- auditar alterações relevantes;
- auditar alteração de dados da Loja;
- auditar disponibilidade de pagamento;
- auditar alteração de Taxas;
- auditar alteração da Logo;
- utilizar Central de Auditoria como histórico;
- não reescrever operações históricas;
- preservar Taxa histórica;
- preservar Forma de Pagamento histórica;
- preservar Parcelamento histórico;
- não reescrever documentos históricos;
- validar Configurações no backend;
- persistir alteração e Auditoria de forma consistente;
- tratar concorrência;
- respeitar isolamento por Loja.

# 29. RELATÓRIOS E EXPORTAÇÕES — REGRAS GERAIS

## 29.1 Finalidade

As regras gerais de Relatórios e Exportações definem os padrões de consulta, apresentação e geração de documentos a partir dos dados do sistema.

Esta seção não substitui as regras específicas de cada módulo.

Cada módulo continua responsável por definir:

- quais Relatórios existem;
- quais indicadores pertencem ao Relatório;
- quais entidades são consideradas;
- como os valores são calculados;
- como cancelamentos, Devoluções, Estornos e demais operações afetam os resultados.

Esta seção define o comportamento comum dos Relatórios e das Exportações.

---

## 29.2 Relatórios específicos dos módulos

Os Relatórios devem respeitar as regras oficiais do módulo correspondente.

Exemplos:

- Vendas;
- Clientes;
- Crediário;
- Condicionais;
- Estoque;
- Entradas;
- Contas a Pagar;
- Fornecedores;
- Devoluções ao Fornecedor;
- Garantias;
- Inventários;
- Lucro.

Uma regra geral de Relatórios não deve substituir uma regra financeira ou operacional específica do módulo de origem.

---

## 29.3 Acesso aos Relatórios

Administrador pode acessar todos os Relatórios permitidos da Loja.

Operador pode acessar Relatórios operacionais dos módulos aos quais possui acesso.

A autorização deve ser validada no backend.

Ocultar Relatório ou botão no frontend não substitui a validação de permissão.

---

## 29.4 Dados financeiros restritos

Operador não deve receber dados restritos de:

- Lucro;
- Margem;
- Custo financeiro agregado;
- Valor financeiro total do Estoque.

Esses dados são exclusivos do Administrador.

A restrição deve ocorrer no backend.

---

## 29.5 Relatório de Lucro

Relatório específico de Lucro é exclusivo do Administrador.

Operador não pode:

- consultar;
- exportar;
- receber dados agregados equivalentes por endpoint alternativo.

A proteção deve considerar o significado financeiro do dado e não somente o nome da tela.

---

## 29.6 Margem

Indicadores de Margem são exclusivos do Administrador quando representarem resultado financeiro da Loja.

Exemplos:

- Margem Bruta;
- Margem percentual;
- Margem por Produto;
- Margem por Venda;
- Margem por período.

Operador não deve receber esses valores.

---

## 29.7 Custo agregado

Operador pode acessar dados operacionais necessários aos módulos conforme as regras específicas já definidas.

Porém, Relatórios não devem fornecer ao Operador consolidações financeiras restritas de custo.

Exemplos restritos:

- Custo total vendido no período;
- Custo total do Estoque;
- Custo agregado por categoria;
- Custo agregado por Marca;
- Custo agregado utilizado para cálculo de Lucro.

---

## 29.8 Valor financeiro do Estoque

O valor financeiro total do Estoque é exclusivo do Administrador.

Operador pode consultar Estoque quantitativo.

Exemplo permitido ao Operador:

Produto A:
5 unidades disponíveis.

Exemplo restrito ao Operador:

Valor de custo do Estoque:
R$ 150.000,00.

A restrição deve ser aplicada no backend.

---

## 29.9 Relatórios operacionais do Operador

Operador pode acessar Relatórios operacionais, conforme as permissões dos módulos correspondentes.

Podem ser disponibilizados Relatórios de:

- Vendas;
- Clientes;
- Crediário;
- Condicionais;
- Estoque quantitativo;
- Entradas;
- Contas a Pagar;
- Fornecedores;
- Devoluções ao Fornecedor;
- Garantias;
- Inventários.

Os dados apresentados devem respeitar as restrições financeiras do perfil.

---

## 29.10 Mesmo Relatório para perfis diferentes

Quando Administrador e Operador acessarem o mesmo Relatório operacional, o backend deve retornar somente os dados permitidos ao perfil autenticado.

Exemplo:

Relatório de Estoque.

Administrador pode receber:

- quantidade;
- custo permitido;
- valor financeiro agregado;
- demais indicadores administrativos autorizados.

Operador pode receber:

- quantidade;
- disponibilidade;
- dados cadastrais operacionais permitidos.

O navegador não deve receber dados restritos para apenas ocultá-los visualmente.

---

## 29.11 Filtros de período

Quando o Relatório possuir dimensão temporal, os filtros padronizados de período são:

- Hoje;
- 7 dias;
- 30 dias;
- Mês atual;
- Personalizado.

Relatórios que não façam sentido por período podem não apresentar esse filtro.

---

## 29.12 Hoje

O filtro Hoje deve utilizar a data civil operacional atual.

A interpretação deve utilizar:

America/Sao_Paulo.

O intervalo deve representar o dia civil correspondente.

---

## 29.13 Últimos 7 dias

O filtro 7 dias deve representar o período operacional correspondente aos últimos 7 dias civis, incluindo a data atual.

A implementação deve utilizar a regra temporal oficial do sistema.

---

## 29.14 Últimos 30 dias

O filtro 30 dias deve representar o período operacional correspondente aos últimos 30 dias civis, incluindo a data atual.

A implementação deve utilizar a regra temporal oficial do sistema.

---

## 29.15 Mês atual

O filtro Mês atual deve representar o intervalo iniciado no primeiro dia do mês civil atual até a data operacional atual.

A interpretação deve utilizar:

America/Sao_Paulo.

---

## 29.16 Período Personalizado

O filtro Personalizado deve permitir informar:

- Data inicial;
- Data final.

As duas datas são obrigatórias quando o período Personalizado estiver selecionado.

---

## 29.17 Validação do período Personalizado

A Data inicial não pode ser posterior à Data final.

Período inválido deve ser recusado.

A validação autoritativa deve ocorrer no backend.

---

## 29.18 Datas civis dos Relatórios

Datas de filtro representam datas civis operacionais.

A interpretação dos limites do período deve utilizar:

America/Sao_Paulo.

O backend deve converter corretamente os limites para a representação temporal persistida.

---

## 29.19 Ausência de limite máximo do período

Não existe limite máximo fixo de quantidade de dias para o período Personalizado neste momento.

O usuário pode consultar períodos históricos extensos.

A ausência de limite não autoriza carregar todo o histórico da Loja no navegador de forma indiscriminada.

---

## 29.20 Filtros específicos do módulo

Cada Relatório pode possuir filtros adicionais conforme sua finalidade.

Exemplos:

- Cliente;
- Fornecedor;
- Produto;
- Marca;
- Situação;
- Forma de Pagamento;
- Usuário;
- Categoria operacional.

Os filtros devem seguir as regras oficiais do módulo.

---

## 29.21 Combinação de filtros

Filtros podem ser utilizados em conjunto.

Exemplo:

Período:
01/07/2026 a 31/07/2026.

Fornecedor:
Fornecedor A.

Situação:
Pendente.

O conjunto retornado deve atender simultaneamente aos filtros aplicados.

---

## 29.22 Filtros autoritativos

O navegador pode informar os filtros desejados.

O backend deve:

- validar os filtros;
- normalizar os valores;
- aplicar o isolamento por Loja;
- aplicar as permissões do perfil;
- calcular o conjunto correspondente.

O navegador não define autoritativamente o resultado do Relatório.

---

## 29.23 Mesmos filtros na tela e na Exportação

A Exportação deve representar o mesmo conjunto lógico definido pelos filtros aplicados ao Relatório.

Exemplo:

Tela filtrada por:

01/07/2026 a 31/07/2026.

Fornecedor A.

Situação Pendente.

A Exportação deve utilizar esses mesmos filtros.

---

## 29.24 Exportação não pode ignorar filtros

O sistema não deve exportar todo o histórico quando o usuário solicitar Exportação de um conjunto filtrado.

A geração deve reaplicar os filtros no backend.

Não confiar em uma lista de linhas enviada pelo navegador como fonte autoritativa do arquivo.

---

## 29.25 Formatos oficiais de Exportação

Os formatos oficiais são:

- PDF;
- Excel `.xlsx`;
- CSV.

Nem todo Relatório precisa possuir todos os formatos.

A disponibilidade depende da finalidade do Relatório.

---

## 29.26 PDF

PDF deve ser priorizado para:

- leitura;
- apresentação;
- impressão;
- compartilhamento documental.

O PDF deve seguir as regras oficiais de Impressões e Documentos Gerados.

---

## 29.27 Excel

Excel `.xlsx` deve ser priorizado para Relatórios tabulares e análise de dados.

Exemplos:

- Vendas;
- Estoque;
- Crediário;
- Contas a Pagar;
- Entradas;
- Fornecedores;
- Inventários.

A disponibilidade específica deve seguir o módulo correspondente.

---

## 29.28 CSV

CSV deve ser utilizado principalmente quando houver necessidade técnica ou administrativa específica.

Exemplos:

- Auditoria;
- integrações futuras;
- extrações técnicas autorizadas.

CSV não é o formato operacional principal dos Relatórios comuns da Loja.

---

## 29.29 Prioridade do Excel nos Relatórios operacionais

Relatórios operacionais comuns devem priorizar:

- PDF;
- Excel `.xlsx`.

Não é necessário oferecer CSV quando Excel atender adequadamente à finalidade do Relatório.

---

## 29.30 Formatos por Relatório

Cada Relatório deve definir os formatos aplicáveis.

Exemplo conceitual:

Vendas:
PDF e Excel.

Estoque:
PDF e Excel.

Crediário:
PDF e Excel.

Contas a Pagar:
PDF e Excel.

Auditoria:
PDF e CSV.

A ausência de um formato não representa erro quando ele não fizer parte da regra oficial do Relatório.

---

## 29.31 Totais e Resumos

Quando o Relatório apresentar resumo do conjunto filtrado, a Exportação correspondente deve apresentar os mesmos indicadores conceituais.

Exemplo de Vendas:

- quantidade de Vendas;
- quantidade de Peças;
- valor bruto;
- Devoluções;
- valor líquido.

Os cálculos devem utilizar o conjunto filtrado.

---

## 29.32 Permissão sobre Totais

Totais e Resumos devem respeitar o perfil autenticado.

Um indicador restrito ao Administrador não deve ser incluído na Exportação do Operador.

Exemplo:

Relatório operacional de Vendas do Operador pode apresentar valor vendido quando permitido pelas regras de Vendas.

Não deve apresentar Lucro ou Margem.

---

## 29.33 Resumo não calculado no navegador

Indicadores financeiros e agregados relevantes devem ser calculados ou validados pelo backend.

O navegador não deve ser a fonte autoritativa de:

- totais;
- Lucro;
- Margem;
- custo agregado;
- valor financeiro do Estoque.

---

## 29.34 Coerência entre listagem e resumo

A listagem e o resumo devem utilizar a mesma definição de filtros e regras de negócio.

Exemplo:

Listagem exclui Vendas canceladas do resultado líquido.

Resumo não pode somar Vendas canceladas como Receita válida.

Diferenças conceituais devem ser explicitamente definidas pelo módulo.

---

## 29.35 Dados históricos

Relatórios históricos devem utilizar os valores e snapshots preservados nas operações.

O sistema não deve reconstruir o passado utilizando indiscriminadamente o cadastro atual.

---

## 29.36 Nome histórico do Produto

Quando a operação preservar Nome histórico do Produto, o Relatório histórico deve utilizar esse valor.

Exemplo:

Na data da Venda:

Nome:
Camiseta Básica.

Posteriormente:

Nome atual:
Camiseta Premium.

O Relatório histórico da Venda deve apresentar:

Camiseta Básica.

---

## 29.37 Marca histórica

Quando a operação preservar Marca histórica, o Relatório histórico deve utilizar a Marca correspondente ao momento da operação.

Alteração posterior da Marca no cadastro não deve reescrever a Venda histórica.

---

## 29.38 Preço histórico

Relatórios de Vendas devem utilizar o preço praticado na operação.

Exemplo:

Preço atual:
R$ 200,00.

Preço da Venda histórica:
R$ 150,00.

O Relatório da Venda deve utilizar:

R$ 150,00.

---

## 29.39 Custo histórico

Quando o perfil e o Relatório possuírem autorização para utilizar Custo, deve ser utilizado o Custo histórico fotografado na operação.

O Custo atual do Produto não deve reescrever o resultado histórico.

---

## 29.40 Taxa histórica do Cartão

Relatórios financeiros devem utilizar a Taxa de Cartão fotografada na operação.

Alterar a Taxa atual nas Configurações não deve modificar Relatórios históricos.

---

## 29.41 Usuário histórico

Quando a operação preservar o usuário responsável, o Relatório histórico deve utilizar a identificação histórica aplicável.

Alteração futura do perfil do usuário não deve reclassificar a operação anterior.

---

## 29.42 Dados atuais

Alguns Relatórios representam a posição atual do sistema.

Exemplos:

- Estoque atual;
- Crédito disponível do Fornecedor;
- Contas a Pagar em aberto;
- Crediário em aberto;
- Garantias em andamento.

Esses Relatórios devem utilizar o estado atual válido das entidades.

---

## 29.43 Identificação de Posição atual

Quando o Relatório representar estado atual, a interface e a Exportação devem deixar clara a natureza da informação.

Expressão recomendada:

Posição atual.

O documento pode apresentar também a data e hora de geração.

---

## 29.44 Identificação de Período histórico

Quando o Relatório representar operações ocorridas em determinado intervalo, a interface e a Exportação devem apresentar o período correspondente.

Expressão recomendada:

Período:
01/07/2026 a 31/07/2026.

---

## 29.45 Posição atual não é reconstrução histórica

Relatório de Posição atual representa o estado no momento da consulta.

Exemplo:

Estoque atual.

A Exportação gerada hoje não representa automaticamente qual era o Estoque em data anterior.

Relatório histórico de posição exige regra específica própria.

---

## 29.46 Data e hora da Posição atual

Relatórios de Posição atual devem apresentar a data e hora de geração quando isso ajudar a interpretar o documento.

Exemplo:

Posição atual em:
15/07/2026 às 15:30.

A apresentação deve utilizar:

America/Sao_Paulo.

---

## 29.47 Cancelamentos

Não existe regra global de ocultar todas as operações canceladas de todos os Relatórios.

Cada Relatório deve seguir sua finalidade e as regras do módulo correspondente.

---

## 29.48 Relatório líquido de Vendas

Relatório de resultado líquido de Vendas deve seguir as regras financeiras oficiais.

Vendas canceladas não devem ser consideradas Receita válida.

Devoluções devem afetar o resultado conforme a data e as regras oficiais do módulo.

---

## 29.49 Histórico de operações

Relatório ou Histórico de operações pode apresentar Vendas canceladas.

Nesse caso, deve identificar claramente a situação:

Cancelada.

A presença da Venda no histórico não significa que seu valor compõe Receita líquida.

---

## 29.50 Devoluções

Devoluções devem ser tratadas conforme a finalidade do Relatório.

Exemplo:

Resultado líquido por período.

A Devolução afeta o período conforme a data oficial em que ocorreu e a regra financeira definida.

Histórico da Venda.

A Devolução permanece vinculada à Venda original.

---

## 29.51 Trocas

Trocas devem seguir as regras oficiais de Vendas e Devoluções.

O Relatório não deve tratar toda Troca como nova Receita integral sem considerar os vínculos financeiros da operação.

A regra específica do módulo prevalece.

---

## 29.52 Estornos

Estornos devem ser tratados conforme a entidade financeira de origem.

O Relatório deve distinguir:

- operação original;
- estorno;
- resultado líquido correspondente.

Não apagar a operação original para simular ausência de histórico.

---

## 29.53 Paginação real

Listagens de Relatórios devem utilizar paginação real ou mecanismo equivalente de consulta incremental.

O navegador não deve precisar carregar todo o conjunto histórico para exibir a primeira página.

---

## 29.54 Filtros e Paginação

Busca, filtros, ordenação e paginação devem ser processados de forma coerente.

Ao alterar um filtro, o conjunto paginado deve ser recalculado.

A interface deve retornar à primeira página quando a página atual não for válida para o novo conjunto.

---

## 29.55 Exportação gerada pelo backend

A Exportação deve ser gerada pelo backend ou por mecanismo servidor equivalente autorizado.

O navegador não deve precisar carregar todas as linhas do Relatório antes de gerar o arquivo.

---

## 29.56 Fonte dos dados da Exportação

O backend deve consultar novamente os dados autorizados utilizando:

- Loja autenticada;
- usuário autenticado;
- perfil atual;
- filtros validados;
- regras do módulo.

A Exportação não deve confiar em dados tabulares completos enviados pelo navegador.

---

## 29.57 Estado Gerando Relatório

Durante a geração de arquivo, a interface deve apresentar estado claro.

Mensagem recomendada:

Gerando relatório...

A ação de geração correspondente deve permanecer temporariamente indisponível durante o envio ativo.

---

## 29.58 Prevenção de duplo envio

A interface deve impedir múltiplos cliques simultâneos na mesma ação de Exportação enquanto a requisição estiver em andamento.

A proteção visual não substitui controles de consistência no backend quando aplicáveis.

---

## 29.59 Falha na geração

Quando a geração falhar, o sistema deve apresentar erro discreto.

Mensagem equivalente:

Não foi possível gerar o relatório. Tente novamente.

A ação deve voltar a ficar disponível.

---

## 29.60 Sessão expirada durante geração

Quando a Sessão estiver expirada ou invalidada, a Exportação deve ser recusada.

O sistema deve seguir o fluxo oficial de Sessão expirada.

Arquivo protegido não deve ser gerado para Sessão inválida.

---

## 29.61 Segurança da Exportação

O backend deve recalcular e validar:

- Loja;
- usuário;
- perfil;
- filtros;
- dados permitidos;
- formato permitido.

O navegador não pode conceder permissão a si próprio.

---

## 29.62 Perfil informado pelo navegador

O backend não deve aceitar campo enviado pelo navegador como autoridade para definir perfil.

Exemplos inválidos como fonte autoritativa:

role = admin.

isAdmin = true.

includeProfit = true.

includeCost = true.

As permissões devem ser obtidas da Sessão e do cadastro persistido.

---

## 29.63 Campos restritos

Quando o perfil não possuir autorização, o backend não deve incluir campos restritos na resposta ou no arquivo.

Não utilizar somente:

display: none.

ou ocultação equivalente no frontend.

Dados restritos não devem ser enviados ao Operador.

---

## 29.64 Isolamento por Loja

Todo Relatório e Exportação deve permanecer restrito à Loja autenticada.

O sistema deve impedir:

- consultar Relatório de outra Loja;
- alterar storeId para acessar outra Loja;
- exportar dados de outra Loja;
- combinar dados de Lojas diferentes.

A validação deve ocorrer no backend.

---

## 29.65 Identificação da Loja no PDF

PDF deve apresentar a identificação da Loja conforme as regras oficiais de documentos.

Pode incluir:

- Logo;
- Nome da Loja;
- CPF ou CNPJ;
- demais dados aplicáveis.

A composição específica depende do documento.

---

## 29.66 Título do Relatório

Toda Exportação deve possuir título claro.

Exemplos:

Relatório de Vendas.

Relatório de Estoque.

Relatório de Crediário.

Relatório de Contas a Pagar.

Auditoria.

---

## 29.67 Filtros no documento

Quando aplicável, o documento deve apresentar os filtros relevantes utilizados.

Exemplo:

Período:
01/07/2026 a 31/07/2026.

Situação:
Pendente.

Fornecedor:
Fornecedor A.

Filtros técnicos internos não precisam ser apresentados.

---

## 29.68 Data de geração

Documentos gerados devem apresentar a data de geração quando aplicável.

A apresentação deve utilizar:

America/Sao_Paulo.

O timestamp oficial deve ser definido pelo backend.

---

## 29.69 Usuário responsável pela geração

Quando aplicável ao documento, pode ser apresentado o usuário responsável pela geração.

Para Exportações sensíveis, a identificação do usuário deve ser preservada obrigatoriamente na Auditoria correspondente.

---

## 29.70 PDF e dados sensíveis

PDF deve respeitar as regras de permissão e mascaragem aplicáveis.

O documento não deve incluir dados restritos apenas porque foi gerado em formato PDF.

A permissão do usuário continua válida durante a geração.

---

## 29.71 Excel e dados sensíveis

Excel deve respeitar as mesmas regras de autorização do Relatório.

Colunas restritas não devem ser incluídas no arquivo do Operador.

Não gerar a coluna oculta ou escondida dentro da planilha.

---

## 29.72 CSV e dados sensíveis

CSV deve respeitar as regras de autorização correspondentes.

Segredos e credenciais não podem ser exportados.

Dados sensíveis devem seguir as regras específicas do módulo e da Exportação.

---

## 29.73 Auditoria das Exportações

Não é obrigatório auditar toda Exportação operacional comum.

Exemplos que não exigem evento específico:

- PDF de Vendas;
- Excel de Estoque;
- PDF de Crediário;
- Excel de Contas a Pagar.

A regra evita volume artificial na Central de Auditoria.

---

## 29.74 Exportações sensíveis

Exportações sensíveis devem gerar evento de Auditoria.

Incluem:

- Exportação da Central de Auditoria;
- Relatório de Lucro;
- Backup técnico.

Novas Exportações sensíveis podem ser classificadas formalmente no futuro.

---

## 29.75 Auditoria do Relatório de Lucro

Exportação do Relatório de Lucro deve registrar:

- Administrador responsável;
- data e hora;
- formato;
- período;
- filtros gerais aplicados.

O evento não precisa armazenar o conteúdo integral do arquivo.

---

## 29.76 Auditoria da Central de Auditoria

A Exportação da Central de Auditoria deve seguir as regras específicas da seção oficial de Auditoria.

O evento deve preservar os filtros gerais e o formato utilizado.

---

## 29.77 Backup técnico

Geração ou Exportação de Backup técnico deve ser auditada.

O evento deve registrar:

- Administrador responsável;
- data e hora;
- tipo da operação.

Credenciais, chaves secretas ou conteúdo integral do Backup não devem ser copiados para o evento de Auditoria.

---

## 29.78 Dados atuais durante geração

Relatórios de Posição atual devem utilizar uma visão consistente dos dados durante a geração.

A implementação deve evitar que totais e linhas representem estados incompatíveis da mesma consulta por efeito de alterações concorrentes.

---

## 29.79 Consistência de Relatórios históricos

Relatórios históricos devem utilizar dados persistidos e vínculos válidos.

A implementação não deve inferir informação histórica inexistente a partir do cadastro atual quando isso puder alterar o significado da operação.

---

## 29.80 Dados históricos desconhecidos

Quando um dado histórico necessário não existir em operação legada, o sistema não deve inventar o valor.

Exemplo:

Preço original histórico desconhecido.

Apresentar estado compatível, como:

Não informado.

ou:

Histórico indisponível.

Não utilizar automaticamente o preço atual como se fosse o preço histórico.

---

## 29.81 Valores monetários

Valores monetários devem seguir a política oficial de precisão e arredondamento do sistema.

Totais da tela e da Exportação devem utilizar a mesma regra financeira.

O arquivo não deve recalcular valores com lógica divergente do backend.

---

## 29.82 Datas e horários

Relatórios devem seguir a regra temporal oficial.

Novos timestamps são armazenados em UTC com offset explícito.

Apresentação operacional utiliza:

America/Sao_Paulo.

Filtros de datas civis devem ser interpretados nesse fuso.

---

## 29.83 Estado de carregamento

A tela de Relatório deve possuir estado de carregamento claro.

Ao alterar filtros, dados antigos não devem permanecer apresentados como se correspondessem ao novo conjunto.

---

## 29.84 Estado de erro

Falha de rede ou servidor deve apresentar estado de erro discreto.

A interface deve permitir nova tentativa.

Erro de autenticação deve seguir o fluxo oficial de Sessão expirada.

---

## 29.85 Estado vazio

Quando nenhum registro corresponder aos filtros, apresentar estado vazio claro.

Mensagem equivalente:

Nenhum registro encontrado para os filtros informados.

O sistema não deve criar linhas artificiais.

---

## 29.86 Relatório sem permissão

Quando o usuário não possuir permissão para o Relatório, o backend deve recusar o acesso.

A interface não deve apresentar dados parciais restritos como alternativa automática.

Mensagem equivalente:

Você não possui permissão para acessar este relatório.

---

## 29.87 Formato não permitido

Quando um Relatório não possuir determinado formato oficial, o backend deve recusar a solicitação de Exportação nesse formato.

Exemplo:

Relatório permite PDF e Excel.

Requisição manipulada solicita CSV.

Resultado:

Formato não permitido para este relatório.

---

## 29.88 Nome do arquivo

Arquivos exportados devem possuir nome claro e previsível.

Exemplo conceitual:

relatorio-vendas-2026-07.xlsx.

relatorio-estoque-2026-07-15.pdf.

auditoria-2026-07.csv.

O nome não deve expor segredo ou identificador técnico sensível.

---

## 29.89 Repetição da geração

Gerar novamente o mesmo Relatório com os mesmos filtros representa nova geração documental.

A operação não altera os dados de origem.

Não é necessária idempotência financeira para Exportação comum.

---

## 29.90 Exportação e operações em andamento

A Exportação deve utilizar somente estados persistidos e válidos conforme o módulo.

Dados temporários existentes apenas no navegador não devem ser incluídos.

Exemplo:

Venda ainda não finalizada no navegador.

Não deve aparecer no Relatório de Vendas concluídas.

---

## 29.91 Fonte autoritativa

O backend deve definir e validar:

- Loja;
- usuário;
- perfil;
- permissão;
- filtros;
- período;
- dados permitidos;
- regras de cálculo;
- totais;
- formato;
- conteúdo da Exportação.

O navegador não deve ser fonte autoritativa desses elementos.

---

## 29.92 Regras gerais de Relatórios e Exportações

O sistema deve:

- possuir regras gerais de Relatórios;
- preservar regras específicas dos módulos;
- permitir todos os Relatórios autorizados ao Administrador;
- permitir Relatórios operacionais ao Operador;
- restringir Lucro ao Administrador;
- restringir Margem ao Administrador;
- restringir custo financeiro agregado ao Administrador;
- restringir valor financeiro total do Estoque ao Administrador;
- permitir Estoque quantitativo ao Operador;
- aplicar restrições no backend;
- não enviar dados restritos para ocultação somente visual;
- possuir filtro Hoje;
- possuir filtro 7 dias;
- possuir filtro 30 dias;
- possuir filtro Mês atual;
- possuir filtro Personalizado;
- exigir Data inicial no Personalizado;
- exigir Data final no Personalizado;
- impedir Data inicial posterior à Data final;
- interpretar datas civis em America/Sao_Paulo;
- não possuir limite máximo fixo de dias no Personalizado;
- permitir filtros específicos por módulo;
- combinar filtros;
- validar filtros no backend;
- utilizar os mesmos filtros na tela e na Exportação;
- impedir Exportação ignorando filtros;
- permitir PDF;
- permitir Excel `.xlsx`;
- permitir CSV quando aplicável;
- priorizar PDF para leitura e impressão;
- priorizar Excel para Relatórios tabulares;
- utilizar CSV principalmente para finalidade técnica ou administrativa;
- não exigir todos os formatos em todos os Relatórios;
- apresentar Totais e Resumos quando definidos;
- respeitar permissões nos Totais;
- calcular agregados relevantes no backend;
- manter coerência entre listagem e resumo;
- utilizar snapshots históricos;
- utilizar Nome histórico quando preservado;
- utilizar Marca histórica quando preservada;
- utilizar Preço histórico;
- utilizar Custo histórico quando autorizado;
- utilizar Taxa histórica do Cartão;
- preservar usuário histórico quando aplicável;
- diferenciar Posição atual de Período histórico;
- identificar Relatórios de Posição atual;
- identificar períodos históricos;
- não tratar Posição atual como reconstrução histórica;
- apresentar data e hora da Posição atual quando aplicável;
- não possuir regra global de ocultação de cancelados;
- seguir regras específicas dos módulos;
- excluir Vendas canceladas de Receita válida;
- permitir canceladas em históricos quando identificadas;
- tratar Devoluções conforme a finalidade do Relatório;
- tratar Trocas conforme as regras de Vendas;
- preservar Estornos;
- utilizar paginação real ou consulta incremental;
- recalcular paginação após alteração de filtros;
- gerar Exportações no backend;
- não exigir carregamento de todas as linhas no navegador;
- consultar novamente os dados autorizados para Exportação;
- apresentar Gerando relatório;
- impedir duplo clique durante geração ativa;
- tratar falha de geração;
- recusar Exportação com Sessão expirada;
- recalcular Loja;
- recalcular usuário;
- recalcular perfil;
- validar filtros;
- validar dados permitidos;
- validar formato;
- não confiar em perfil informado pelo navegador;
- não aceitar includeProfit como autorização;
- não aceitar includeCost como autorização;
- remover campos restritos da resposta e do arquivo;
- respeitar isolamento por Loja;
- identificar a Loja no PDF;
- apresentar título claro;
- apresentar filtros relevantes;
- apresentar data de geração;
- respeitar mascaragem e dados sensíveis;
- aplicar permissões ao PDF;
- aplicar permissões ao Excel;
- aplicar permissões ao CSV;
- não auditar toda Exportação operacional comum;
- auditar Exportação da Auditoria;
- auditar Relatório de Lucro;
- auditar Backup técnico;
- preservar consistência da Posição atual durante geração;
- preservar dados históricos;
- não inventar dados históricos inexistentes;
- utilizar política monetária oficial;
- utilizar regra temporal oficial;
- possuir estado de carregamento;
- possuir estado de erro;
- possuir estado vazio;
- recusar Relatório sem permissão;
- recusar formato não permitido;
- utilizar nomes claros de arquivos;
- permitir nova geração documental;
- utilizar somente estados persistidos válidos;
- utilizar backend como fonte autoritativa.

# 30. CONCILIAÇÃO DE CARTÕES E RECEBÍVEIS BANCÁRIOS

## 30.1 Finalidade

O módulo de Conciliação de Cartões e Recebíveis Bancários controla os valores esperados de operações realizadas em Cartão e os valores efetivamente recebidos pela Loja.

O módulo deve permitir identificar:

- a Venda de origem;
- a modalidade do pagamento;
- o valor bruto;
- a Taxa fotografada;
- o valor estimado da Taxa;
- o valor líquido esperado;
- a previsão de recebimento;
- o valor efetivamente recebido;
- eventuais diferenças;
- as Conciliações realizadas.

A Conciliação não deve alterar o valor pago pelo Cliente na Venda.

A Taxa de Cartão e eventuais diferenças pertencem à operação financeira da Loja.

---

## 30.2 Acesso ao módulo

Administrador e Operador podem acessar o módulo de Recebíveis de Cartão.

Ambos podem:

- consultar Recebíveis;
- visualizar detalhes;
- registrar recebimento individual;
- realizar Conciliação em Lote.

As permissões devem ser validadas no backend.

---

## 30.3 Tela de Recebíveis de Cartão

O sistema deve possuir tela:

RECEBÍVEIS DE CARTÃO.

A tela deve apresentar os Recebíveis Bancários originados por pagamentos em Cartão.

O usuário não deve precisar consultar a Venda individualmente para localizar cada Recebível.

---

## 30.4 Geração automática do Recebível

Toda Venda válida que possuir pagamento em:

- Débito;
- Crédito 1x;
- Crédito 2x;
- Crédito 3x

deve gerar automaticamente Recebível Bancário correspondente.

O usuário não cria manualmente o Recebível originado da Venda.

---

## 30.5 Componente de pagamento em Cartão

Cada componente de pagamento em Cartão gera seu próprio Recebível.

Exemplo:

Venda paga com:

Dinheiro:
R$ 100,00.

Débito:
R$ 200,00.

Crédito 2x:
R$ 300,00.

Resultado:

Dinheiro gera Entrada financeira conforme as regras oficiais.

Débito gera Recebível Bancário.

Crédito 2x gera Recebível Bancário.

Os dois Recebíveis de Cartão permanecem individualmente identificados.

---

## 30.6 Recebível não é Crediário

Recebível de Cartão não representa Crediário da Loja.

Crédito 2x ou 3x não cria parcelas de Crediário.

O Recebível de Cartão não utiliza:

- Limite de Crédito do Cliente;
- parcelas do Crediário;
- vencimentos do Crediário;
- Score do Cliente como regra de autorização.

---

## 30.7 Dados históricos do Recebível

Cada Recebível deve preservar, no mínimo:

- identificador próprio;
- Loja;
- Venda de origem;
- componente de pagamento de origem;
- data e hora da Venda;
- modalidade;
- quantidade de parcelas, quando Crédito;
- valor bruto;
- Taxa percentual fotografada;
- valor estimado da Taxa;
- valor líquido esperado;
- data prevista de recebimento;
- situação;
- valor efetivamente recebido acumulado;
- diferença, quando aplicável.

---

## 30.8 Modalidade do Recebível

A modalidade deve identificar corretamente a operação.

As modalidades oficiais são:

- Débito;
- Crédito 1x;
- Crédito 2x;
- Crédito 3x.

O sistema não deve exigir Bandeira do Cartão.

---

## 30.9 Taxa fotografada

A Taxa utilizada no Recebível deve ser a Taxa vigente no momento da Venda.

A Taxa deve ser obtida pelo backend a partir das Configurações da Loja.

O navegador não deve informar autoritativamente a Taxa aplicada.

---

## 30.10 Alteração futura da Taxa

Alterar a Taxa nas Configurações não modifica Recebíveis já criados.

Exemplo:

Crédito 2x.

Taxa no momento da Venda:
3,10%.

Taxa atual:
3,50%.

O Recebível histórico permanece com:

3,10%.

---

## 30.11 Valor bruto

O valor bruto representa o valor atribuído ao componente de pagamento em Cartão na Venda.

Exemplo:

Venda:
R$ 1.000,00.

Crédito 2x:
R$ 1.000,00.

Valor bruto do Recebível:
R$ 1.000,00.

---

## 30.12 Valor estimado da Taxa

O sistema deve calcular o valor estimado da Taxa utilizando a Taxa fotografada.

Fórmula conceitual:

Valor estimado da Taxa =
Valor bruto x Taxa percentual.

O cálculo deve utilizar a política oficial de precisão e arredondamento monetário.

---

## 30.13 Valor líquido esperado

O sistema deve calcular:

Valor líquido esperado =
Valor bruto - Valor estimado da Taxa.

Exemplo:

Valor bruto:
R$ 1.000,00.

Taxa:
3,50%.

Valor estimado da Taxa:
R$ 35,00.

Valor líquido esperado:
R$ 965,00.

---

## 30.14 Antecipação do Crédito

A Loja trabalha com antecipação das operações de Crédito.

Por essa razão, o Crédito parcelado não gera Recebíveis mensais separados.

Crédito 2x gera um Recebível.

Crédito 3x gera um Recebível.

A quantidade de parcelas permanece preservada como informação histórica e para definição da Taxa aplicável.

---

## 30.15 Previsão de recebimento

Débito possui previsão operacional de recebimento em:

1 dia.

Crédito 1x possui previsão operacional de recebimento em:

1 dia.

Crédito 2x possui previsão operacional de recebimento em:

1 dia.

Crédito 3x possui previsão operacional de recebimento em:

1 dia.

---

## 30.16 Data prevista

A data prevista do Recebível deve ser calculada pelo backend.

A regra deve utilizar a data operacional oficial da Venda.

A interpretação de data civil deve utilizar:

America/Sao_Paulo.

---

## 30.17 Situações do Recebível

As situações oficiais são:

- Pendente;
- Parcialmente recebido;
- Recebido;
- Com divergência;
- Cancelado;
- Estornado.

A situação deve ser derivada das operações persistidas e das regras oficiais.

O navegador não deve definir autoritativamente a situação.

---

## 30.18 Situação Pendente

Recebível permanece Pendente quando não possui recebimento efetivo registrado e continua aguardando Conciliação.

---

## 30.19 Situação Parcialmente recebido

Recebível fica Parcialmente recebido quando o valor efetivamente recebido acumulado é superior a zero e inferior ao saldo esperado, sem encerramento com divergência.

Exemplo:

Líquido esperado:
R$ 1.000,00.

Recebido:
R$ 600,00.

Saldo esperado:
R$ 400,00.

Situação:

Parcialmente recebido.

---

## 30.20 Situação Recebido

Recebível fica Recebido quando o valor efetivamente recebido corresponder ao valor líquido esperado, respeitando a política monetária oficial.

Exemplo:

Líquido esperado:
R$ 965,00.

Recebido:
R$ 965,00.

Situação:

Recebido.

---

## 30.21 Situação Com divergência

Recebível fica Com divergência quando for encerrado com valor efetivamente recebido diferente do valor líquido esperado.

A diferença pode ser:

- positiva;
- negativa.

---

## 30.22 Diferença positiva

Exemplo:

Líquido esperado:
R$ 965,00.

Recebido:
R$ 970,00.

Diferença:
+R$ 5,00.

Situação:

Com divergência.

O valor excedente não deve ser atribuído automaticamente a outro Recebível.

---

## 30.23 Diferença negativa

Exemplo:

Líquido esperado:
R$ 965,00.

Recebido:
R$ 960,00.

Diferença:
-R$ 5,00.

Quando o usuário confirmar o encerramento da diferença, a situação deve ser:

Com divergência.

---

## 30.24 Saldo esperado

O saldo esperado deve considerar:

Saldo esperado =
Valor líquido esperado - valores efetivamente recebidos anteriormente.

Exemplo:

Líquido esperado:
R$ 1.000,00.

Recebido anteriormente:
R$ 600,00.

Saldo esperado:
R$ 400,00.

---

## 30.25 Conciliação individual

O sistema deve permitir Conciliação individual de Recebível.

O fluxo deve partir de um Recebível específico.

Ação:

REGISTRAR RECEBIMENTO.

O sistema deve identificar autoritativamente o Recebível selecionado.

---

## 30.26 Dados do recebimento individual

No recebimento individual, o usuário deve informar:

- data do recebimento;
- valor efetivamente recebido;
- observação opcional.

O usuário não deve informar novamente:

- Venda;
- modalidade;
- quantidade de parcelas;
- Taxa;
- valor bruto;
- valor líquido esperado.

Esses dados pertencem ao Recebível selecionado.

---

## 30.27 Recebimento parcial individual

O sistema deve permitir recebimento parcial.

Exemplo:

Saldo esperado:
R$ 1.000,00.

Valor recebido:
R$ 600,00.

Resultado:

Recebido acumulado:
R$ 600,00.

Saldo esperado:
R$ 400,00.

Situação:
Parcialmente recebido.

---

## 30.28 Novo recebimento após parcial

Recebível Parcialmente recebido pode receber nova Conciliação.

A nova operação deve considerar o saldo atualizado.

O valor recebido anteriormente permanece preservado no histórico.

---

## 30.29 Encerrar com divergência

Quando existir saldo esperado e o usuário souber que não haverá novo recebimento correspondente, deve existir a ação:

ENCERRAR COM DIVERGÊNCIA.

A ação exige observação.

---

## 30.30 Observação da divergência

A observação de encerramento com divergência é obrigatória.

Exemplo:

Diferença de Taxa da operadora.

Valor descontado pela adquirente.

Ajuste identificado no extrato.

O sistema não deve exigir que a observação corresponda a uma categoria técnica fixa neste momento.

---

## 30.31 Conciliação em Lote

O sistema deve permitir Conciliação em Lote.

A Conciliação em Lote permite selecionar múltiplos Recebíveis e registrar uma única entrada bancária correspondente ao conjunto selecionado.

---

## 30.32 Finalidade da Conciliação em Lote

A Conciliação em Lote deve representar situações em que um único valor recebido no banco corresponde a múltiplos Recebíveis de Cartão.

Exemplo:

Depósito bancário:
R$ 4.850,00.

Recebíveis correspondentes:

Venda 101:
R$ 950,00.

Venda 102:
R$ 1.900,00.

Venda 103:
R$ 2.000,00.

Os três Recebíveis podem ser conciliados em uma única operação.

---

## 30.33 Seleção de Recebíveis em Lote

O usuário deve poder selecionar dois ou mais Recebíveis elegíveis.

Podem ser selecionados Recebíveis:

- Pendentes;
- Parcialmente recebidos.

Recebíveis concluídos ou operacionalmente encerrados não devem ser selecionados para nova Conciliação comum.

---

## 30.34 Modalidades diferentes no mesmo Lote

A Conciliação em Lote pode conter modalidades diferentes.

Exemplo:

- Débito;
- Crédito 1x;
- Crédito 2x;
- Crédito 3x.

O sistema não deve utilizar a modalidade para distribuir automaticamente valores.

Cada Recebível selecionado permanece individualmente identificado.

---

## 30.35 Resumo do Lote

Antes da confirmação, o sistema deve apresentar:

- quantidade de Recebíveis selecionados;
- total líquido esperado original;
- total já recebido anteriormente, quando houver parciais;
- saldo esperado selecionado;
- valor efetivamente recebido informado;
- diferença.

---

## 30.36 Exemplo de resumo do Lote

Exemplo:

3 Recebíveis selecionados.

Saldo esperado:
R$ 4.850,00.

Valor recebido:
R$ 4.850,00.

Diferença:
R$ 0,00.

---

## 30.37 Lote com valor exato

Quando o valor efetivamente recebido corresponder exatamente à soma dos saldos esperados selecionados, o sistema pode atribuir a cada Recebível o respectivo saldo esperado.

Exemplo:

Recebível A:
Saldo R$ 950,00.

Recebível B:
Saldo R$ 1.900,00.

Recebível C:
Saldo R$ 2.000,00.

Total recebido:
R$ 4.850,00.

Resultado:

A recebe R$ 950,00.

B recebe R$ 1.900,00.

C recebe R$ 2.000,00.

---

## 30.38 Ausência de distribuição genérica

O sistema não deve utilizar FIFO genérico para distribuir o valor recebido entre Recebíveis.

O sistema não deve distribuir valores:

- por ordem de criação;
- por ordem da Venda;
- por modalidade;
- aleatoriamente.

A seleção e a atribuição devem permanecer vinculadas aos Recebíveis da Conciliação.

---

## 30.39 Lote com diferença

Quando o valor efetivamente recebido for diferente da soma dos saldos esperados selecionados, o sistema deve apresentar a diferença.

Exemplo:

Saldo esperado:
R$ 4.850,00.

Recebido:
R$ 4.843,50.

Diferença:
-R$ 6,50.

O sistema não deve distribuir automaticamente a diferença.

---

## 30.40 Distribuição manual da Conciliação

Quando houver diferença no Lote, o sistema deve permitir informar o valor atribuído a cada Recebível selecionado.

Exemplo:

Venda 101.

Saldo esperado:
R$ 950,00.

Valor atribuído:
R$ 950,00.

Venda 102.

Saldo esperado:
R$ 1.900,00.

Valor atribuído:
R$ 1.893,50.

Venda 103.

Saldo esperado:
R$ 2.000,00.

Valor atribuído:
R$ 2.000,00.

---

## 30.41 Validação da soma atribuída

A soma dos valores atribuídos aos Recebíveis deve corresponder exatamente ao valor efetivamente recebido informado para a Conciliação.

Fórmula:

Soma dos valores atribuídos =
Valor efetivamente recebido.

A validação deve ocorrer no backend.

---

## 30.42 Valor atribuído inválido

O sistema deve recusar:

- NaN;
- infinito;
- valor negativo;
- texto inválido.

Valores monetários devem seguir a política oficial de precisão.

---

## 30.43 Diferença não atribuída automaticamente

Quando houver diferença, o sistema não deve decidir sozinho qual Venda ou Recebível absorve a diferença.

O usuário deve informar a distribuição dos valores efetivamente recebidos.

---

## 30.44 Resultado individual após Conciliação em Lote

Após a Conciliação em Lote, cada Recebível deve recalcular sua própria situação.

Exemplo:

Recebível A.

Esperado:
R$ 950,00.

Atribuído:
R$ 950,00.

Situação:
Recebido.

Recebível B.

Esperado:
R$ 1.900,00.

Atribuído:
R$ 1.893,50.

Se encerrado com diferença:

Situação:
Com divergência.

---

## 30.45 Encerramento de diferença no Lote

Quando um valor atribuído for inferior ao saldo esperado e o usuário desejar encerrar o Recebível como divergente, a decisão deve ser explícita.

O sistema não deve presumir automaticamente que toda diferença negativa é definitiva.

---

## 30.46 Recebível parcial no Lote

Recebível pode permanecer Parcialmente recebido após Conciliação em Lote.

Exemplo:

Saldo esperado:
R$ 1.000,00.

Valor atribuído no Lote:
R$ 600,00.

Sem encerramento com divergência.

Resultado:

Parcialmente recebido.

Saldo:
R$ 400,00.

---

## 30.47 Recebível divergente no Lote

Quando o usuário marcar o Recebível para encerramento com divergência, deve ser exigida observação.

A observação pode ser específica para o Recebível divergente.

---

## 30.48 Operação agrupadora de Conciliação

A Conciliação em Lote deve possuir identificador próprio.

A operação agrupadora deve preservar:

- Loja;
- usuário responsável;
- data e hora da operação;
- data do recebimento;
- valor efetivamente recebido;
- quantidade de Recebíveis;
- observação geral opcional;
- situação da Conciliação.

---

## 30.49 Itens da Conciliação em Lote

Cada Recebível incluído no Lote deve possuir vínculo com a Conciliação agrupadora.

O item deve preservar, no mínimo:

- Conciliação;
- Recebível;
- saldo esperado no momento da operação;
- valor atribuído;
- encerramento com divergência, quando aplicável;
- observação da divergência, quando aplicável.

---

## 30.50 Recebíveis permanecem separados

A Conciliação em Lote não transforma múltiplos Recebíveis em um único Recebível.

Cada Recebível continua:

- vinculado à Venda de origem;
- com seu valor bruto;
- com sua Taxa;
- com seu líquido esperado;
- com seu histórico;
- com sua situação.

A Conciliação apenas agrupa o evento de recebimento bancário.

---

## 30.51 Uma entrada bancária

Uma Conciliação em Lote deve gerar uma única Entrada financeira correspondente ao valor efetivamente recebido.

Exemplo:

Conciliação em Lote.

Valor recebido:
R$ 4.843,50.

Entrada financeira:
R$ 4.843,50.

---

## 30.52 Proibição de Entradas artificiais por Recebível

O sistema não deve gerar uma Entrada financeira independente para cada Recebível incluído no mesmo depósito conciliado.

Exemplo incorreto:

Entrada R$ 950,00.

Entrada R$ 1.893,50.

Entrada R$ 2.000,00.

Quando o banco recebeu um único depósito de:

R$ 4.843,50.

O resultado correto é uma única Entrada de R$ 4.843,50.

---

## 30.53 Vínculo da Entrada financeira

A Entrada financeira deve permanecer vinculada à Conciliação correspondente.

A Conciliação mantém os vínculos individuais com os Recebíveis.

Assim:

Entrada financeira
→ Conciliação
→ Itens da Conciliação
→ Recebíveis
→ Vendas de origem.

---

## 30.54 Conciliação individual e Entrada financeira

Conciliação individual deve gerar uma Entrada financeira correspondente ao valor efetivamente recebido naquela operação.

Se o Recebível possuir múltiplos recebimentos parciais, cada evento bancário individual gera sua própria Entrada financeira.

---

## 30.55 Valor efetivamente recebido

A Entrada financeira deve utilizar o valor efetivamente recebido.

Não utilizar:

- valor bruto da Venda;
- líquido esperado;
- valor estimado da Taxa

como substituição do valor bancário informado.

---

## 30.56 Taxa real manual

O sistema não deve exigir informação manual de Taxa real.

O controle deve preservar:

- valor bruto;
- Taxa estimada fotografada;
- valor estimado da Taxa;
- líquido esperado;
- valor efetivamente recebido;
- diferença.

Esses dados são suficientes para análise da operação neste momento.

---

## 30.57 Diferença financeira

A diferença deve ser calculada a partir do valor esperado e do valor efetivamente atribuído ao Recebível.

A diferença não deve reescrever a Taxa histórica.

---

## 30.58 Histórico de recebimentos do Recebível

Cada Recebível deve possuir histórico dos recebimentos relacionados.

O histórico deve permitir identificar:

- data do recebimento;
- valor atribuído;
- usuário responsável;
- Conciliação de origem;
- observação, quando aplicável.

---

## 30.59 Detalhes da Conciliação em Lote

A Conciliação em Lote deve possuir visualização de detalhes.

A tela deve apresentar:

- data do recebimento;
- usuário responsável;
- valor total recebido;
- quantidade de Recebíveis;
- Recebíveis incluídos;
- Venda de origem de cada Recebível;
- modalidade;
- saldo esperado no momento;
- valor atribuído;
- diferença individual;
- situação resultante.

---

## 30.60 Busca dos Recebíveis

A tela deve permitir busca por:

- número da Venda;
- valor.

A busca deve respeitar a Loja autenticada.

---

## 30.61 Filtros dos Recebíveis

A tela deve permitir filtros por:

- período;
- Débito;
- Crédito 1x;
- Crédito 2x;
- Crédito 3x;
- situação.

Os filtros podem ser utilizados em conjunto.

---

## 30.62 Cards da tela

A tela deve apresentar os cards:

- A receber;
- Previsto para hoje;
- Recebido no mês;
- Divergências.

Os valores devem ser calculados pelo backend.

---

## 30.63 Card A receber

A receber deve representar o saldo ainda aguardando recebimento dos Recebíveis válidos.

Recebíveis Cancelados ou Estornados não devem compor o saldo como valor a receber.

Recebíveis encerrados Com divergência não devem manter diferença negativa como saldo pendente.

---

## 30.64 Card Previsto para hoje

Previsto para hoje deve representar o saldo esperado dos Recebíveis com data prevista correspondente à data operacional atual.

A data deve utilizar:

America/Sao_Paulo.

---

## 30.65 Card Recebido no mês

Recebido no mês deve utilizar os valores efetivamente recebidos no mês civil atual.

O indicador não deve utilizar o líquido esperado como se tivesse sido recebido.

---

## 30.66 Card Divergências

Divergências deve representar Recebíveis encerrados ou identificados com diferença conforme as regras oficiais.

A interface pode apresentar quantidade e valor agregado da diferença quando permitido pelo módulo.

---

## 30.67 Listagem dos Recebíveis

A listagem deve apresentar, no mínimo:

- Venda;
- data;
- modalidade;
- valor bruto;
- Taxa;
- líquido esperado;
- valor recebido;
- diferença;
- previsão;
- situação;
- ação VER DETALHES.

---

## 30.68 Seleção para Conciliação em Lote

A listagem deve permitir seleção de Recebíveis elegíveis.

A seleção deve apresentar visualmente:

- quantidade selecionada;
- saldo esperado selecionado.

A ação principal deve ser:

CONCILIAR EM LOTE.

---

## 30.69 Recebível inelegível para seleção

Recebível não elegível não deve permitir seleção para nova Conciliação comum.

Exemplos:

- Recebido;
- Com divergência encerrada;
- Cancelado;
- Estornado.

A validação deve ocorrer também no backend.

---

## 30.70 Cancelamento da Venda e Recebível Pendente

Quando uma Venda for cancelada e o Recebível ainda estiver integralmente Pendente, o Recebível deve ser cancelado conforme a operação transacional da Venda.

Nenhuma Saída financeira deve ser criada pelo Recebível, pois nenhum valor bancário foi efetivamente recebido.

---

## 30.71 Cancelamento da Venda e Recebível recebido

Quando o Recebível possuir valor efetivamente recebido, o cancelamento da Venda deve utilizar o valor recebido como informação financeira autoritativa para os efeitos aplicáveis.

O sistema não deve presumir que o líquido esperado entrou integralmente no banco.

---

## 30.72 Cancelamento da Venda e histórico

O Recebível não deve ser apagado após cancelamento da Venda.

O histórico deve preservar:

- Recebível;
- recebimentos realizados;
- Conciliações;
- cancelamento ou estorno correspondente.

---

## 30.73 Devolução e saldo pendente

Devolução de Venda deve considerar o saldo pendente do Recebível conforme as regras oficiais de Devoluções.

A parte ainda não recebida pode ser consumida antes da geração de Saída financeira, conforme o vínculo da operação.

---

## 30.74 Devolução e valor recebido

Quando a Devolução atingir valor já efetivamente recebido, a Saída financeira deve considerar somente o valor que exige devolução financeira efetiva.

A Conciliação fornece o valor autoritativo já recebido.

---

## 30.75 Proibição de usar líquido esperado como recebido

O sistema não deve considerar automaticamente o valor líquido esperado como valor bancário recebido.

Recebimento efetivo somente existe após Conciliação registrada.

---

## 30.76 Estorno de Conciliação

Conciliação registrada deve poder ser estornada conforme fluxo formal.

O estorno não deve apagar o histórico da Conciliação original.

A operação deve preservar:

- Conciliação original;
- usuário responsável pelo estorno;
- data e hora;
- motivo obrigatório.

---

## 30.77 Motivo do Estorno

Estorno de Conciliação exige motivo.

O motivo deve ser persistido.

A Auditoria deve registrar o evento.

---

## 30.78 Estorno e Entrada financeira

Quando uma Conciliação que gerou Entrada financeira for estornada, o sistema deve reverter o efeito financeiro correspondente conforme as regras oficiais do Financeiro.

A Entrada original não deve ser apagada silenciosamente.

A reversão deve possuir vínculo com a operação original.

---

## 30.79 Estorno em Lote

Estorno de Conciliação em Lote deve reverter a operação agrupadora completa.

O sistema não deve estornar silenciosamente somente um item de um depósito bancário agrupado como se fosse uma Conciliação independente.

Correções parciais futuras devem possuir fluxo formal específico.

---

## 30.80 Atomicidade da Conciliação individual

A Conciliação individual deve ser transacional.

Devem ocorrer na mesma unidade de consistência:

- validação do Recebível;
- registro do recebimento;
- atualização do Recebível;
- geração da Entrada financeira;
- Auditoria;
- conclusão da operação.

Qualquer falha deve provocar rollback completo.

---

## 30.81 Atomicidade da Conciliação em Lote

A Conciliação em Lote deve ser totalmente transacional.

Devem ocorrer na mesma unidade de consistência:

- validação de todos os Recebíveis;
- criação da Conciliação;
- criação dos itens;
- registro dos valores atribuídos;
- atualização de todos os Recebíveis;
- geração de uma única Entrada financeira;
- registro da Auditoria;
- conclusão da Conciliação.

Qualquer falha deve provocar rollback completo.

---

## 30.82 Falha intermediária no Lote

Se a operação falhar durante o processamento de qualquer Recebível, nenhum item do Lote deve permanecer conciliado.

Exemplo:

5 Recebíveis selecionados.

Falha no terceiro Recebível.

Resultado:

nenhum dos 5 Recebíveis é atualizado.

Nenhuma Entrada financeira é gerada.

Nenhuma Conciliação concluída permanece.

---

## 30.83 Concorrência

O backend deve revalidar todos os Recebíveis selecionados dentro da transação.

A validação deve ocorrer após a aquisição do mecanismo de bloqueio aplicável.

---

## 30.84 Recebível alterado durante seleção

Exemplo:

Mauro seleciona 5 Recebíveis.

Outro usuário concilia um dos Recebíveis.

Mauro confirma a Conciliação em Lote.

O backend identifica que um Recebível não possui mais o saldo esperado utilizado na seleção.

Resultado:

A Conciliação inteira deve ser recusada.

---

## 30.85 Mensagem de conflito

Quando um ou mais Recebíveis forem alterados antes da confirmação, apresentar mensagem equivalente:

Um ou mais recebíveis foram alterados. Revise a conciliação e tente novamente.

Nenhum efeito parcial deve permanecer.

---

## 30.86 Controle de estado concorrente

A implementação deve utilizar mecanismo de controle compatível com o banco de dados.

SQLite deve utilizar trava de escrita adequada à operação crítica.

PostgreSQL deve utilizar bloqueio dos registros financeiros envolvidos ou mecanismo transacional equivalente.

---

## 30.87 Idempotência

Conciliações financeiras devem possuir proteção idempotente.

A interface deve gerar chave única por tentativa de Conciliação.

A mesma tentativa após falha de rede deve reutilizar a mesma chave e o mesmo conteúdo.

---

## 30.88 Replay idempotente

Mesma chave e mesmo conteúdo devem retornar o resultado já concluído.

Não gerar:

- nova Conciliação;
- novos itens;
- nova Entrada financeira;
- novos recebimentos;
- nova Auditoria de sucesso.

---

## 30.89 Conflito de chave

Mesma chave de idempotência utilizada com conteúdo financeiro diferente deve ser recusada.

Resposta equivalente:

409 Conflict.

A operação original deve permanecer preservada.

---

## 30.90 Conteúdo financeiro da Conciliação

O conteúdo utilizado na proteção idempotente deve considerar os dados financeiros relevantes.

Na Conciliação em Lote, deve considerar, no mínimo:

- Loja;
- Recebíveis selecionados;
- valores atribuídos;
- valor total recebido;
- data do recebimento;
- decisões de encerramento com divergência.

A implementação deve utilizar Hash determinístico.

---

## 30.91 Auditoria da Conciliação individual

Conciliação individual concluída deve gerar evento de Auditoria.

O evento deve preservar:

- usuário;
- data e hora;
- Recebível;
- Venda de origem;
- valor recebido;
- situação resultante.

---

## 30.92 Auditoria da Conciliação em Lote

Conciliação em Lote concluída deve gerar um evento principal de Auditoria vinculado à operação agrupadora.

O evento deve preservar:

- usuário;
- data e hora;
- Conciliação;
- quantidade de Recebíveis;
- valor total recebido.

Os detalhes individuais permanecem nos itens da Conciliação.

---

## 30.93 Ausência de Auditoria duplicada por item

A Conciliação em Lote não precisa gerar evento central independente de sucesso para cada Recebível.

O evento principal da Conciliação deve possuir vínculo suficiente com os itens.

Os históricos individuais dos Recebíveis permanecem atualizados.

---

## 30.94 Auditoria de divergência

Encerramento com divergência deve ser identificável na Auditoria ou nos detalhes vinculados ao evento correspondente.

A observação obrigatória deve permanecer preservada no histórico operacional.

---

## 30.95 Auditoria de Estorno

Estorno de Conciliação deve gerar evento de Auditoria.

O evento deve preservar:

- usuário;
- data e hora;
- Conciliação original;
- motivo.

---

## 30.96 Isolamento por Loja

Recebíveis e Conciliações pertencem à Loja correspondente.

O sistema deve impedir:

- consultar Recebível de outra Loja;
- selecionar Recebível de outra Loja;
- conciliar Recebíveis de Lojas diferentes;
- abrir Conciliação de outra Loja;
- estornar Conciliação de outra Loja.

A validação deve ocorrer no backend.

---

## 30.97 Paginação

A listagem de Recebíveis deve utilizar paginação real ou mecanismo equivalente de consulta incremental.

O navegador não deve carregar todo o histórico de Recebíveis para exibir a primeira página.

---

## 30.98 Estado de carregamento

A tela deve possuir estado de carregamento claro.

Ao alterar busca, filtro ou página, dados antigos não devem permanecer apresentados como se correspondessem ao novo conjunto.

---

## 30.99 Estado de erro

Falha de rede ou servidor deve apresentar erro discreto.

A interface deve permitir nova tentativa.

Erro de autenticação deve seguir o fluxo oficial de Sessão expirada.

---

## 30.100 Estado vazio

Quando nenhum Recebível corresponder aos filtros, apresentar estado vazio claro.

Mensagem equivalente:

Nenhum recebível de cartão encontrado.

---

## 30.101 Estado de envio da Conciliação

Durante a confirmação de Conciliação individual ou em Lote, a ação correspondente deve permanecer temporariamente indisponível.

A interface deve impedir envios simultâneos da mesma tentativa.

---

## 30.102 Fonte autoritativa

O backend deve definir e validar:

- Loja;
- usuário responsável;
- Recebíveis;
- Venda de origem;
- modalidade;
- quantidade de parcelas;
- valor bruto;
- Taxa fotografada;
- valor estimado da Taxa;
- líquido esperado;
- saldo esperado;
- valores anteriormente recebidos;
- situação;
- diferença;
- Entrada financeira.

O navegador não deve ser fonte autoritativa desses dados.

---

## 30.103 Dados permitidos ao navegador

O navegador pode informar, conforme o fluxo:

- Recebíveis selecionados;
- data do recebimento;
- valor efetivamente recebido;
- valores atribuídos;
- decisão de encerrar com divergência;
- observações.

Todos os dados devem ser revalidados pelo backend.

---

## 30.104 Regras gerais da Conciliação de Cartões e Recebíveis Bancários

O sistema deve:

- possuir tela Recebíveis de Cartão;
- permitir acesso ao Administrador;
- permitir acesso ao Operador;
- gerar Recebível automaticamente a partir de Venda válida;
- gerar Recebível para Débito;
- gerar Recebível para Crédito 1x;
- gerar Recebível para Crédito 2x;
- gerar Recebível para Crédito 3x;
- não permitir criação manual comum do Recebível de Venda;
- manter Recebível separado por componente de Cartão;
- não tratar Recebível como Crediário;
- preservar Venda de origem;
- preservar componente de pagamento de origem;
- preservar data e hora da Venda;
- preservar modalidade;
- preservar quantidade de parcelas;
- preservar valor bruto;
- preservar Taxa fotografada;
- preservar valor estimado da Taxa;
- preservar líquido esperado;
- preservar data prevista;
- preservar situação;
- preservar valor recebido;
- preservar diferença;
- não exigir Bandeira;
- obter Taxa no backend;
- não confiar na Taxa enviada pelo navegador;
- não reescrever Taxa histórica;
- calcular valor estimado da Taxa;
- calcular líquido esperado;
- utilizar antecipação;
- gerar um Recebível para Crédito 2x;
- gerar um Recebível para Crédito 3x;
- não gerar Recebíveis mensais separados;
- prever Débito em 1 dia;
- prever Crédito 1x em 1 dia;
- prever Crédito 2x em 1 dia;
- prever Crédito 3x em 1 dia;
- possuir situação Pendente;
- possuir situação Parcialmente recebido;
- possuir situação Recebido;
- possuir situação Com divergência;
- possuir situação Cancelado;
- possuir situação Estornado;
- calcular saldo esperado;
- permitir Conciliação individual;
- permitir recebimento parcial;
- permitir novo recebimento após parcial;
- permitir Encerrar com divergência;
- exigir observação para encerramento com divergência;
- permitir Conciliação em Lote;
- permitir selecionar múltiplos Recebíveis;
- permitir Pendentes no Lote;
- permitir Parcialmente recebidos no Lote;
- permitir modalidades diferentes no mesmo Lote;
- calcular quantidade selecionada;
- calcular total líquido esperado;
- calcular total anteriormente recebido;
- calcular saldo esperado selecionado;
- calcular diferença do Lote;
- atribuir automaticamente saldos somente quando o total for exato;
- não utilizar FIFO genérico;
- não distribuir por ordem de criação;
- não distribuir por modalidade;
- não distribuir diferença automaticamente;
- permitir distribuição manual quando houver diferença;
- exigir soma atribuída igual ao valor recebido;
- validar valores no backend;
- recalcular situação individual dos Recebíveis;
- permitir parcial após Lote;
- permitir divergência após Lote;
- exigir decisão explícita de encerramento com divergência;
- possuir operação agrupadora de Conciliação;
- possuir itens da Conciliação;
- manter Recebíveis individualmente separados;
- gerar uma única Entrada financeira por Conciliação em Lote;
- não gerar Entradas artificiais por Recebível do mesmo depósito;
- vincular Entrada à Conciliação;
- vincular Conciliação aos Recebíveis;
- vincular Recebíveis às Vendas;
- utilizar valor efetivamente recebido na Entrada;
- não exigir Taxa real manual;
- calcular diferença;
- preservar histórico de recebimentos;
- possuir detalhes da Conciliação;
- permitir busca por Venda;
- permitir busca por valor;
- permitir filtro por período;
- permitir filtro por Débito;
- permitir filtro por Crédito 1x;
- permitir filtro por Crédito 2x;
- permitir filtro por Crédito 3x;
- permitir filtro por situação;
- possuir card A receber;
- possuir card Previsto para hoje;
- possuir card Recebido no mês;
- possuir card Divergências;
- listar Venda;
- listar data;
- listar modalidade;
- listar bruto;
- listar Taxa;
- listar líquido esperado;
- listar recebido;
- listar diferença;
- listar previsão;
- listar situação;
- possuir VER DETALHES;
- permitir seleção para Conciliação em Lote;
- impedir seleção de Recebível encerrado;
- tratar cancelamento da Venda;
- não gerar Saída por Recebível nunca recebido;
- considerar valor efetivamente recebido no cancelamento;
- preservar histórico após cancelamento;
- considerar saldo pendente na Devolução;
- considerar valor recebido na Devolução;
- não tratar líquido esperado como recebido;
- permitir Estorno formal da Conciliação;
- exigir motivo no Estorno;
- preservar Conciliação original;
- reverter efeito financeiro por operação vinculada;
- estornar Lote como operação agrupadora completa;
- tornar Conciliação individual transacional;
- tornar Conciliação em Lote transacional;
- realizar rollback completo em falha;
- impedir Lote parcialmente conciliado;
- revalidar todos os Recebíveis dentro da transação;
- tratar concorrência;
- recusar Lote quando Recebível tiver sido alterado;
- utilizar bloqueio transacional adequado;
- proteger Conciliações com idempotência;
- reutilizar chave após falha de rede;
- retornar replay seguro;
- impedir efeitos duplicados;
- retornar conflito para chave reutilizada com conteúdo diferente;
- utilizar Hash determinístico;
- auditar Conciliação individual;
- auditar Conciliação em Lote;
- evitar Auditoria central duplicada por item do Lote;
- preservar divergências;
- auditar Estorno;
- respeitar isolamento por Loja;
- utilizar paginação real;
- possuir estado de carregamento;
- possuir estado de erro;
- possuir estado vazio;
- bloquear envio simultâneo da mesma tentativa;
- utilizar backend como fonte autoritativa;
- revalidar dados enviados pelo navegador.

# 31. NOTIFICAÇÕES E CENTRAL DE ALERTAS

## 31.1 Finalidade

A Central de Alertas concentra todas as situações operacionais que exigem atenção dos usuários da Loja.

Os Alertas representam situações pendentes do sistema e não substituem a Auditoria nem os históricos específicos dos módulos.

A Central deve fornecer acesso rápido às entidades que originaram cada Alerta.

---

## 31.2 Acesso

Administrador e Operador podem acessar a Central de Alertas.

Cada usuário visualizará apenas Alertas referentes aos módulos para os quais possui permissão de acesso.

A validação das permissões deve ocorrer no backend.

---

## 31.3 Alertas pertencem à Loja

Os Alertas pertencem à Loja e não ao usuário.

Uma mesma situação operacional gera apenas um Alerta para a Loja.

Exemplo:

Condicional nº 131 atrasado.

Administrador e Operador visualizam o mesmo Alerta.

---

## 31.4 Estado de leitura

O estado de leitura pertence ao usuário.

Cada usuário possui seu próprio controle de:

- Não lido;
- Lido.

Marcar um Alerta como lido não altera o estado para os demais usuários.

---

## 31.5 Marcar como lido

O usuário pode marcar um Alerta como lido.

Essa ação apenas altera a interface do usuário.

Não modifica:

- prioridade;
- situação;
- entidade de origem;
- resolução do problema.

---

## 31.6 Marcar como não lido

O usuário pode marcar novamente um Alerta como não lido.

Essa ação é apenas organizacional.

---

## 31.7 Marcar todos como lidos

A Central deve possuir a ação:

MARCAR TODOS COMO LIDOS.

A ação altera apenas o estado de leitura do usuário autenticado.

Não resolve nenhum Alerta.

---

## 31.8 Resolução automática

Não existe botão:

RESOLVER ALERTA.

Quando a situação operacional deixar de existir, o Alerta deve desaparecer automaticamente.

Exemplos:

- Conta paga;
- Condicional devolvido;
- Garantia atualizada;
- Recebível conciliado.

---

## 31.9 Sem histórico próprio

A Central de Alertas exibe apenas Alertas ativos.

Alertas resolvidos não permanecem armazenados na Central.

O histórico operacional continua preservado:

- na entidade correspondente;
- na Auditoria, quando aplicável.

---

## 31.10 Prioridades

As prioridades oficiais são:

- Crítico;
- Atenção;
- Informativo.

A prioridade é definida automaticamente pelas regras do sistema.

O usuário não pode alterá-la.

---

## 31.11 Cores

Representação visual sugerida:

🔴 Crítico

🟠 Atenção

🔵 Informativo

As cores possuem apenas finalidade visual.

A regra oficial é a prioridade persistida.

---

## 31.12 Alertas Críticos

São classificados como Crítico, entre outros:

- Conta a Pagar vencida;
- Parcela de Crediário vencida;
- Falha crítica de integridade operacional.

Novos Alertas Críticos poderão ser adicionados futuramente.

---

## 31.13 Alertas de Atenção

São classificados como Atenção:

- Condicional vencido;
- Garantia sem atualização por período definido;
- Garantia aguardando entrega ao Cliente;
- Devolução ao Fornecedor pendente;
- Recebível previsto ainda não conciliado;
- Recebível encerrado com divergência.

---

## 31.14 Alertas Informativos

A categoria Informativo permanece disponível para futuras funcionalidades.

Na versão inicial do sistema não existirão Alertas Informativos oficiais.

---

## 31.15 Ordenação

A Central deve ordenar os Alertas na seguinte sequência:

1. Alertas fixados.
2. Prioridade.
3. Data de início da situação (mais antiga primeiro).

---

## 31.16 Antiguidade

Dentro da mesma prioridade, Alertas mais antigos aparecem antes dos mais recentes.

---

## 31.17 Contador do sino

O cabeçalho do sistema deve apresentar o sino de Alertas.

O contador representa:

Quantidade de Alertas ativos não lidos pelo usuário autenticado.

---

## 31.18 Atualização do contador

O contador deve ser atualizado:

- após Login;
- ao abrir a Central;
- após operações que alterem Alertas;
- na mudança do dia operacional;
- quando a aplicação recuperar o foco.

Não utilizar atualização contínua em intervalos de poucos segundos.

---

## 31.19 Abrir entidade

Todo Alerta deve possuir uma ação contextual.

Exemplos:

VER CONTA

VER CREDIÁRIO

VER CONDICIONAL

VER GARANTIA

VER DEVOLUÇÃO

VER RECEBÍVEL

A ação deve abrir diretamente a entidade correspondente.

---

### Fixação de Alertas

## 31.20 Fixar Alerta

O usuário pode fixar um Alerta ativo.

A fixação possui apenas finalidade de organização visual.

---

## 31.21 Efeitos da fixação

Fixar um Alerta não altera:

- prioridade;
- leitura;
- situação;
- resolução;
- data de criação.

---

## 31.22 Fixação por usuário

Cada usuário possui sua própria lista de Alertas fixados.

A fixação não é compartilhada entre usuários.

---

## 31.23 Persistência

Os Alertas fixados permanecem fixados após:

- atualizar a página;
- novo Login;
- troca de navegador.

Enquanto o Alerta existir.

---

## 31.24 Remover fixação

O usuário pode remover a fixação a qualquer momento.

Após remover, o Alerta volta para a ordenação normal.

---

## 31.25 Alerta resolvido

Quando a situação deixar de existir:

- o Alerta desaparece;
- a fixação é removida automaticamente.

Não manter referências para Alertas inexistentes.

---

## 31.26 Auditoria

Fixar ou desfazer a fixação de um Alerta não gera evento na Auditoria.

São preferências individuais de interface.

---

## 31.27 Busca

A Central deve permitir busca textual por:

- número da entidade;
- nome do Cliente;
- descrição resumida do Alerta.

---

## 31.28 Filtros

A Central deve permitir filtros por:

- prioridade;
- módulo;
- lido;
- não lido;
- fixado.

Os filtros podem ser combinados.

---

## 31.29 Paginação

A Central deve utilizar paginação real.

Não carregar todo o histórico de Alertas para o navegador.

---

## 31.30 Estado vazio

Quando não existirem Alertas ativos:

"Nenhum alerta pendente."

---

## 31.31 Estado de carregamento

Durante consultas:

"Carregando alertas..."

---

## 31.32 Estado de erro

Falhas devem apresentar mensagem discreta e permitir nova tentativa.

---

## 31.33 Isolamento

O backend deve impedir acesso a Alertas de outra Loja.

Todo Alerta pertence exclusivamente à Loja autenticada.

---

## 31.34 Fonte autoritativa

O backend é responsável por:

- identificar Alertas ativos;
- calcular prioridade;
- validar permissões;
- aplicar filtros;
- controlar leitura;
- controlar fixações.

O frontend possui apenas função de apresentação.

---

## 31.35 Regras gerais

O sistema deve:

- possuir Central de Alertas;
- permitir acesso ao Administrador;
- permitir acesso ao Operador;
- restringir Alertas conforme permissões;
- manter Alertas por Loja;
- manter leitura individual por usuário;
- permitir marcar como lido;
- permitir marcar como não lido;
- permitir marcar todos como lidos;
- remover Alertas automaticamente quando resolvidos;
- não possuir botão "Resolver Alerta";
- não manter histórico próprio de Alertas resolvidos;
- possuir prioridades Crítico, Atenção e Informativo;
- ordenar por fixação, prioridade e antiguidade;
- possuir contador no sino;
- atualizar Alertas em momentos relevantes;
- possuir ação contextual para cada Alerta;
- permitir fixar Alertas;
- permitir desfazer fixação;
- persistir fixações por usuário;
- remover fixações automaticamente quando o Alerta deixar de existir;
- não auditar fixações;
- permitir busca;
- permitir filtros;
- utilizar paginação real;
- possuir estados de carregamento, vazio e erro;
- respeitar isolamento por Loja;
- utilizar o backend como fonte autoritativa.

# 32. DASHBOARD — PAINEL INICIAL

## 32.1 Finalidade

O Dashboard é o Painel Inicial do sistema.

Sua finalidade é apresentar uma visão resumida, atual e confiável da operação da Loja, permitindo identificar rapidamente:

- desempenho das Vendas;
- valores recebidos;
- pendências financeiras;
- Condicionais em andamento;
- Recebíveis de Cartão;
- Alertas ativos;
- demais indicadores permitidos ao perfil autenticado.

O Dashboard não substitui os módulos operacionais nem os Relatórios detalhados.

Cada indicador deve permitir acessar o módulo correspondente quando existir destino operacional.

---

## 32.2 Dashboard após o Login

Após Login válido, o usuário deve ser direcionado ao Dashboard, salvo quando existir fluxo específico autorizado que determine outro destino.

O Dashboard deve utilizar:

- Loja da Sessão autenticada;
- usuário autenticado;
- perfil atual;
- permissões atuais;
- data operacional oficial.

O navegador não deve informar autoritativamente a Loja, o usuário ou o perfil utilizado nos cálculos.

---

## 32.3 Perfis do Dashboard

O Dashboard deve possuir apresentação adequada ao perfil autenticado.

Os perfis oficiais são:

- Administrador;
- Operador.

Administrador possui visão gerencial completa.

Operador possui visão operacional, sem acesso a informações financeiras restritas.

---

## 32.4 Dashboard do Administrador

O Administrador pode visualizar os indicadores gerenciais e operacionais autorizados.

O Dashboard do Administrador pode apresentar:

- Vendas hoje;
- Faturamento hoje;
- Recebido hoje;
- Crediário em aberto;
- Contas a Pagar;
- Recebíveis de Cartão;
- Clientes com Condicional;
- Alertas ativos;
- gráficos gerenciais;
- informações de Lucro, Margem e valor financeiro do Estoque quando previstas pelas regras específicas do Dashboard.

Os dados devem ser calculados no backend.

---

## 32.5 Dashboard do Operador

O Operador deve possuir Dashboard operacional.

O Dashboard do Operador pode apresentar:

- Vendas hoje;
- Clientes atendidos;
- Condicionais;
- Alertas ativos;
- Recebíveis pendentes em visão operacional;
- gráficos operacionais permitidos.

O Operador não deve receber informações restritas de:

- Lucro;
- Margem;
- custo financeiro agregado;
- valor financeiro total do Estoque.

A restrição deve ocorrer no backend.

---

## 32.6 Dados não enviados ao Operador

Dados exclusivos do Administrador não devem ser enviados ao navegador do Operador para serem apenas ocultados visualmente.

O backend deve remover ou deixar de calcular para o Operador:

- Lucro;
- Margem;
- valor financeiro do Estoque;
- custo agregado restrito;
- demais informações gerenciais exclusivas.

Alterar HTML, CSS, JavaScript ou armazenamento local não deve permitir acesso a esses dados.

---

# CARDS DO ADMINISTRADOR

## 32.7 Card Vendas Hoje

O card Vendas Hoje deve apresentar a quantidade de Vendas válidas realizadas na data operacional atual.

Vendas Canceladas não devem compor a quantidade atual de Vendas válidas.

A regra deve considerar a data operacional:

America/Sao_Paulo.

O card deve possuir ação para abrir o módulo de Vendas filtrado por Hoje.

---

## 32.8 Card Faturamento Hoje

O card Faturamento Hoje deve apresentar o valor líquido das Vendas válidas realizadas na data operacional atual.

O cálculo deve considerar:

- Vendas válidas;
- cancelamentos;
- Devoluções;
- valores líquidos conforme as regras oficiais do módulo Vendas.

Vendas Canceladas não devem compor o Faturamento válido.

Devoluções devem produzir o efeito correspondente conforme sua data operacional e regra financeira oficial.

---

## 32.9 Faturamento não é recebimento

Faturamento Hoje e Recebido Hoje representam conceitos distintos.

Faturamento Hoje representa o resultado comercial líquido das Vendas.

Recebido Hoje representa valores financeiros efetivamente recebidos na data.

O sistema não deve utilizar um único valor para representar os dois conceitos.

---

## 32.10 Card Recebido Hoje

O card Recebido Hoje deve apresentar os valores financeiros efetivamente recebidos na data operacional atual.

O cálculo deve considerar, conforme as regras oficiais:

- Dinheiro;
- Pix;
- recebimentos de Crediário;
- recebimentos conciliados de Cartão;
- demais Entradas financeiras válidas.

Não considerar como recebido:

- Recebível de Cartão ainda Pendente;
- parcela de Crediário ainda não paga;
- valor apenas previsto;
- valor estimado sem entrada financeira efetiva.

---

## 32.11 Card Crediário em Aberto

O card Crediário em Aberto deve apresentar o saldo líquido atual do Crediário.

O saldo deve considerar:

- valor original;
- recebimentos;
- recebimentos parciais;
- Devoluções;
- cancelamentos;
- estornos;
- juros;
- multas;
- descontos;
- renegociações, quando implementadas.

O cálculo não deve utilizar apenas:

Valor original - recebido

quando existirem outros efeitos financeiros válidos.

---

## 32.12 Ação do card Crediário em Aberto

Ao selecionar o card Crediário em Aberto, o sistema deve abrir o módulo Crediário com filtro correspondente às parcelas ou saldos ainda em aberto.

A tela de destino deve respeitar o perfil autenticado.

---

## 32.13 Card Contas a Pagar

O card Contas a Pagar deve apresentar o saldo pendente atual das Contas a Pagar válidas.

O cálculo deve considerar:

- pagamentos;
- pagamentos parciais;
- descontos;
- juros;
- multas;
- estornos;
- abatimentos por Devolução ao Fornecedor;
- Créditos com Fornecedor utilizados;
- cancelamentos.

Contas Canceladas não devem compor o saldo pendente atual.

---

## 32.14 Contas vencidas no Dashboard

Quando existirem Contas a Pagar vencidas, o card pode apresentar informação complementar.

Exemplo:

Contas a Pagar:
R$ 15.000,00.

Vencidas:
R$ 2.000,00.

A apresentação deve deixar claro qual valor representa o saldo total e qual representa a parte vencida.

---

## 32.15 Ação do card Contas a Pagar

Ao selecionar o card, o sistema deve abrir Contas a Pagar com filtro de saldo em aberto.

Quando o usuário selecionar informação específica de vencidas, o destino deve aplicar o filtro correspondente.

---

## 32.16 Card Recebíveis de Cartão

O card Recebíveis de Cartão deve apresentar o saldo ainda aguardando Conciliação dos Recebíveis válidos.

O cálculo deve considerar:

- Recebíveis Pendentes;
- Recebíveis Parcialmente recebidos;
- valores efetivamente recebidos anteriormente;
- Cancelamentos;
- Estornos;
- encerramentos com divergência.

Não considerar o valor bruto da Venda como saldo bancário esperado.

O saldo deve utilizar o valor líquido esperado restante.

---

## 32.17 Recebíveis previstos e vencidos

O card pode apresentar informações complementares, como:

- previsto para Hoje;
- atrasado para Conciliação;
- com divergência.

Os valores devem utilizar as regras oficiais de Recebíveis de Cartão.

---

## 32.18 Ação do card Recebíveis de Cartão

Ao selecionar o card, o sistema deve abrir a tela Recebíveis de Cartão.

O destino pode aplicar filtro inicial para:

- Pendentes;
- Parcialmente recebidos;
- previsão correspondente.

---

## 32.19 Card Clientes com Condicional

O card Clientes com Condicional deve apresentar a quantidade de Clientes que possuem pelo menos um Condicional ativo.

O mesmo Cliente com mais de um Condicional ativo deve ser contado uma única vez quando o indicador representar Clientes.

Quando o indicador representar Condicionais, a interface deve utilizar denominação diferente.

---

## 32.20 Condicionais atrasados

O card pode apresentar informação complementar sobre Condicionais que ultrapassaram o prazo fixo de 3 dias.

Exemplo:

Clientes com Condicional:
8.

Condicionais atrasados:
3.

Condicional atrasado possui prioridade Atenção na Central de Alertas.

---

## 32.21 Ação do card Clientes com Condicional

Ao selecionar o card, o sistema deve abrir o módulo Condicionais com filtro para operações ativas.

Quando selecionar a informação de atrasados, o destino deve aplicar o filtro correspondente.

---

## 32.22 Card Alertas Ativos

O card Alertas Ativos deve apresentar a quantidade de Alertas ativos acessíveis ao usuário autenticado.

No Dashboard, o card deve apresentar apenas o resumo quantitativo.

O Dashboard não deve repetir toda a lista da Central de Alertas.

---

## 32.23 Contagem dos Alertas no Dashboard

A contagem do card deve seguir as regras oficiais da Central de Alertas.

O sistema pode apresentar:

- total de Alertas ativos;
- quantidade de Alertas Críticos;
- quantidade de Alertas de Atenção.

O estado Lido ou Não lido não resolve a situação operacional.

---

## 32.24 Ação do card Alertas Ativos

Ao selecionar o card, o sistema deve abrir a Central de Alertas.

Quando o usuário selecionar um resumo de prioridade específica, a Central pode ser aberta com o filtro correspondente.

---

# CARDS DO OPERADOR

## 32.25 Card Vendas Hoje do Operador

O Operador pode visualizar a quantidade de Vendas válidas realizadas Hoje.

O card pode abrir o Histórico de Vendas filtrado pela data operacional atual.

O valor apresentado deve respeitar as permissões operacionais definidas para o módulo Vendas.

---

## 32.26 Card Clientes Atendidos

O card Clientes Atendidos deve apresentar a quantidade de Clientes distintos vinculados a Vendas válidas no período correspondente.

Quando uma Venda utilizar Cliente Padrão, a regra deve definir de forma consistente se o atendimento será contado como atendimento sem identificação individual.

Minha recomendação é contar o atendimento, mas não criar Cliente cadastrado artificialmente.

---

## 32.27 Clientes atendidos e Vendas

Clientes Atendidos e quantidade de Vendas não são necessariamente iguais.

Exemplo:

Um Cliente realiza duas Vendas válidas.

Vendas:
2.

Clientes atendidos:
1.

O Dashboard deve preservar essa diferença conceitual.

---

## 32.28 Card Condicionais do Operador

O Operador pode visualizar:

- quantidade de Condicionais ativos;
- quantidade de Condicionais atrasados.

O card deve abrir o módulo Condicionais com o filtro correspondente.

---

## 32.29 Card Alertas do Operador

O Operador pode visualizar a quantidade de Alertas ativos dos módulos aos quais possui acesso.

Alertas administrativos ou de segurança exclusivos do Administrador não devem ser enviados ao Operador.

---

## 32.30 Recebíveis Pendentes do Operador

O Operador pode visualizar informações operacionais de Recebíveis Pendentes necessárias à Conciliação.

Quando a política do Dashboard restringir determinado agregado financeiro, o Operador deve receber somente:

- quantidade de Recebíveis;
- situação;
- previsão;
- demais dados operacionais permitidos.

O backend deve aplicar a regra de perfil.

---

# CARDS E NAVEGAÇÃO

## 32.31 Cards clicáveis

Os cards do Dashboard devem possuir navegação contextual quando existir módulo de destino.

Ao selecionar um card, o sistema deve abrir a tela correspondente com os filtros relacionados ao indicador.

Exemplos:

Vendas Hoje:
abre Vendas filtradas por Hoje.

Crediário em Aberto:
abre Crediário com saldo em aberto.

Contas a Pagar:
abre Contas pendentes.

Alertas:
abre a Central de Alertas.

---

## 32.32 Cards não substituem permissões

A navegação iniciada por um card deve respeitar as permissões do usuário.

O card não concede acesso adicional ao módulo de destino.

O backend deve validar novamente a autorização na consulta correspondente.

---

## 32.33 Card com valor zero

Quando o resultado do indicador for zero, o card deve permanecer visível.

Exemplo:

Vendas Hoje:
0.

Não esconder o card apenas por ausência de atividade.

A permanência do card preserva a estabilidade do layout e a compreensão da informação.

---

## 32.34 Card sem informação disponível

Quando o dado não puder ser calculado por erro, ausência de permissão ou indisponibilidade técnica, o sistema não deve apresentar zero como se fosse resultado válido.

Deve apresentar estado apropriado, como:

- carregando;
- não disponível;
- erro ao carregar.

Zero deve ser utilizado somente quando o cálculo válido resultar em zero.

---

# GRÁFICOS DO ADMINISTRADOR

## 32.35 Gráfico Vendas por Dia

O Dashboard do Administrador deve possuir gráfico de Vendas por Dia.

O gráfico deve utilizar o valor líquido das Vendas válidas no período selecionado.

O cálculo deve considerar:

- cancelamentos;
- Devoluções;
- datas operacionais;
- valores históricos.

O gráfico não deve recalcular Vendas antigas usando dados atuais dos Produtos.

---

## 32.36 Dias sem Vendas

Quando um dia do período não possuir Vendas válidas, o gráfico deve apresentar valor zero para aquele dia quando isso for necessário para preservar a sequência temporal.

O sistema não deve criar Venda artificial.

---

## 32.37 Gráfico de Formas de Pagamento

O Dashboard do Administrador deve possuir gráfico de Formas de Pagamento.

As formas oficiais são:

- Dinheiro;
- Pix;
- Débito;
- Crédito;
- Crediário.

O gráfico deve utilizar as regras líquidas oficiais.

---

## 32.38 Formas de Pagamento e Devoluções

O gráfico deve separar conceitualmente:

- valor bruto;
- valor devolvido;
- valor líquido;
- valor utilizado na representação gráfica.

Quando uma modalidade possuir resultado líquido negativo, o valor negativo deve permanecer identificável na legenda.

Fatia gráfica deve utilizar somente valores líquidos positivos.

---

## 32.39 Percentuais do gráfico de pagamento

Os percentuais das fatias positivas devem totalizar 100%.

Valores líquidos negativos não devem criar fatia negativa.

Quando existir valor negativo, apresentar indicação equivalente a:

Sem fatia — houve mais Devoluções do que recebimentos no período.

---

## 32.40 Gráfico de Faturamento Mensal

O Dashboard do Administrador pode apresentar gráfico de Faturamento Mensal.

O gráfico deve representar o resultado comercial líquido por mês, conforme as regras oficiais de Vendas.

Vendas Canceladas não compõem Faturamento válido.

Devoluções devem produzir efeito no mês operacional correspondente à ocorrência.

---

## 32.41 Gráficos operacionais do Operador

O Dashboard do Operador pode apresentar gráficos operacionais autorizados.

Exemplos:

- quantidade de Vendas por dia;
- quantidade de atendimentos;
- Condicionais iniciados e concluídos;
- volume quantitativo de operações.

Os gráficos do Operador não devem apresentar:

- Lucro;
- Margem;
- custo agregado restrito;
- valor financeiro total do Estoque.

---

# FILTROS DO DASHBOARD

## 32.42 Períodos disponíveis

O Dashboard deve permitir os períodos:

- Hoje;
- 7 dias;
- 30 dias;
- Mês atual.

Quando já existir regra oficial de período Personalizado para os gráficos do Dashboard, ela pode permanecer disponível.

A aplicação deve utilizar nomenclatura e comportamento consistentes.

---

## 32.43 Filtro Hoje

Hoje representa a data civil operacional atual em:

America/Sao_Paulo.

O sistema não deve utilizar o fuso configurado no computador do usuário como fonte autoritativa.

---

## 32.44 Filtro 7 dias

O filtro 7 dias deve representar os últimos 7 dias civis operacionais, incluindo Hoje.

---

## 32.45 Filtro 30 dias

O filtro 30 dias deve representar os últimos 30 dias civis operacionais, incluindo Hoje.

---

## 32.46 Filtro Mês atual

Mês atual deve representar o período entre o primeiro dia do mês operacional atual e Hoje.

---

## 32.47 Aplicação dos filtros

Os filtros de período devem ser aplicados aos gráficos e aos indicadores que possuam dimensão temporal correspondente.

Indicadores de posição atual podem permanecer baseados no estado atual.

Exemplos de posição atual:

- Crediário em aberto;
- Contas a Pagar;
- Recebíveis Pendentes;
- Condicionais ativos;
- Alertas ativos.

A interface deve deixar clara a diferença entre período histórico e posição atual.

---

## 32.48 Mudança de período

Ao alterar o período:

- invalidar a requisição anterior quando necessário;
- apresentar estado de carregamento;
- buscar os dados correspondentes;
- atualizar os gráficos e indicadores afetados;
- não apresentar dados antigos como se pertencessem ao novo período.

---

## 32.49 Período Personalizado

Quando o Dashboard possuir período Personalizado, o usuário deve informar:

- Data inicial;
- Data final.

A Data inicial não pode ser posterior à Data final.

As datas são civis e devem ser interpretadas em:

America/Sao_Paulo.

O período Personalizado deve permanecer preservado na virada do dia, salvo ação expressa do usuário.

---

# ATUALIZAÇÃO DO DASHBOARD

## 32.50 Momentos de atualização

O Dashboard deve ser atualizado:

- após Login;
- ao entrar ou voltar para o Dashboard;
- após operações relevantes;
- por atualização manual;
- na virada do dia operacional;
- ao recuperar foco ou visibilidade quando for necessário verificar mudança de data.

O sistema não deve realizar consultas a cada poucos segundos sem necessidade.

---

## 32.51 Operações relevantes

Exemplos de operações que podem invalidar o Dashboard:

- Venda;
- Cancelamento de Venda;
- Devolução;
- Troca;
- recebimento de Crediário;
- pagamento ou estorno de Conta a Pagar;
- Conciliação de Cartão;
- Entrada de Produto;
- Devolução ao Fornecedor;
- Inventário;
- alteração de Condicional;
- criação ou resolução de Alerta.

A invalidação deve ocorrer somente nos indicadores afetados ou no conjunto do Dashboard conforme a arquitetura adotada.

---

## 32.52 Atualização manual

O Dashboard deve possuir ação:

ATUALIZAR

ou representação visual equivalente.

A ação deve solicitar novamente os dados atuais ao backend.

---

## 32.53 Estado durante atualização manual

Durante uma atualização ativa:

- impedir múltiplos envios simultâneos da mesma ação;
- apresentar estado de carregamento;
- não manter valores antigos como se fossem atuais;
- preservar o tamanho dos cards e gráficos quando possível.

---

## 32.54 Virada do dia

O Dashboard deve detectar a virada do dia operacional.

A data operacional utiliza:

America/Sao_Paulo.

Na virada:

- invalidar caches relativos à data;
- recalcular Hoje;
- recalcular 7 dias;
- recalcular 30 dias;
- recalcular Mês atual;
- atualizar indicadores correspondentes.

Não é necessário recarregar toda a página.

---

## 32.55 Timer da virada

A aplicação deve manter apenas um timer ativo para a próxima virada do dia.

Antes de agendar novo timer, deve cancelar o timer anterior.

O agendamento não deve criar listeners ou timers duplicados após:

- Login;
- Logout;
- troca de usuário;
- retorno ao Dashboard.

---

## 32.56 Recuperação de foco e visibilidade

Ao recuperar foco ou visibilidade, a aplicação deve conferir se a data operacional mudou.

Essa regra protege o Dashboard quando:

- a aba ficou suspensa;
- o computador entrou em repouso;
- o timer não executou no momento esperado.

---

## 32.57 Logout e novo Login

O mecanismo de atualização temporal deve continuar funcional após:

- Logout;
- novo Login;
- troca de usuário;
- troca de perfil.

Não manter dados residuais do usuário anterior.

---

# LAYOUT E PERSONALIZAÇÃO

## 32.58 Layout fixo

Na primeira versão, o Dashboard deve possuir layout fixo.

O usuário não pode:

- arrastar cards;
- reorganizar gráficos;
- remover indicadores;
- salvar layouts personalizados.

A regra reduz complexidade e mantém uma apresentação consistente.

---

## 32.59 Grade por perfil

A grade deve se adaptar ao perfil autenticado.

Administrador deve utilizar a quantidade de colunas apropriada aos cards apresentados.

Operador deve redistribuir os cards visíveis sem deixar espaços reservados para indicadores ocultos.

---

## 32.60 Responsividade

O Dashboard deve possuir comportamento responsivo.

A grade deve se adaptar a:

- desktop;
- tablet;
- celular.

Os cards e gráficos não devem exigir rolagem horizontal desnecessária.

Breakpoints devem preservar legibilidade e acesso às ações.

---

## 32.61 Perfil alterado

Quando o perfil do usuário mudar e uma nova Sessão for iniciada, o Dashboard deve recalcular:

- cards permitidos;
- gráficos permitidos;
- grade;
- dados recebidos.

Não manter classes, indicadores ou dados do perfil anterior.

---

# ESTADOS VISUAIS

## 32.62 Estado de carregamento

Durante o carregamento, o Dashboard deve apresentar indicadores visuais compatíveis.

Pode utilizar skeletons para preservar:

- tamanho dos cards;
- altura dos gráficos;
- estabilidade do layout.

Valores antigos não devem permanecer visíveis como se correspondessem à nova consulta.

---

## 32.63 Estado de erro

Falhas de servidor ou rede devem apresentar mensagem discreta.

A interface deve permitir:

TENTAR NOVAMENTE.

A tentativa bem-sucedida deve remover automaticamente a mensagem de erro.

---

## 32.64 Erro de autenticação

Resposta de autenticação inválida ou Sessão expirada deve seguir o fluxo oficial de segurança.

O sistema deve:

- limpar dados protegidos do Dashboard;
- invalidar caches;
- invalidar requisições pendentes;
- apresentar o Login novamente.

Dados gerenciais não devem permanecer visíveis após a expiração da Sessão.

---

## 32.65 Requisições antigas

Ao alterar:

- período;
- usuário;
- perfil;
- Loja;
- estado dos dados

requisições antigas devem ser invalidadas ou ignoradas.

Uma resposta antiga não deve sobrescrever dados mais recentes.

---

## 32.66 Estado vazio dos gráficos

Quando não existirem dados válidos no período, o gráfico deve apresentar estado vazio claro.

Exemplo:

Nenhuma Venda no período.

Nenhum pagamento no período.

Não criar:

- linha artificial;
- ponto artificial;
- fatia artificial;
- tooltip artificial.

---

## 32.67 Pagamentos apenas negativos

Quando o período possuir somente Devoluções ou Estornos líquidos negativos, o gráfico de pagamento não deve criar fatias artificiais.

A legenda deve preservar os valores negativos e indicar a ausência de fatia positiva.

---

## 32.68 Tooltips antigos

Ao alterar o período ou entrar em estado vazio, tooltips antigos devem ser ocultados.

O sistema não deve apresentar tooltip de um conjunto de dados anterior.

---

# CÁLCULOS E INTEGRIDADE

## 32.69 Regras oficiais dos módulos

Todos os indicadores do Dashboard devem reutilizar as regras oficiais dos módulos correspondentes.

O Dashboard não deve implementar versões simplificadas e divergentes dos cálculos.

---

## 32.70 Cancelamentos

Vendas Canceladas devem ser desconsideradas dos indicadores de resultado comercial válido.

O histórico da operação permanece preservado nos módulos correspondentes.

---

## 32.71 Devoluções

Devoluções devem afetar os indicadores conforme:

- data operacional da ocorrência;
- valores históricos;
- formas de pagamento;
- efeitos financeiros oficiais.

Não utilizar apenas a data da Venda original para atribuir a Devolução.

---

## 32.72 Pagamentos mistos

Venda com pagamentos mistos deve distribuir corretamente os valores entre as formas correspondentes.

Exemplo:

Dinheiro:
R$ 100,00.

Pix:
R$ 200,00.

Crédito:
R$ 300,00.

O gráfico e os indicadores devem considerar cada componente válido.

---

## 32.73 Valores históricos

O Dashboard deve utilizar snapshots históricos quando o indicador representar operações passadas.

Alterações atuais de:

- Produto;
- Marca;
- preço;
- custo;
- Cliente;
- usuário

não devem reescrever resultados históricos.

---

## 32.74 Data operacional

Todos os agrupamentos temporais devem utilizar:

America/Sao_Paulo.

Timestamps persistidos em UTC devem ser convertidos antes da definição de:

- dia;
- mês;
- período operacional.

Datas civis `YYYY-MM-DD` não devem sofrer conversão de fuso.

---

## 32.75 Timestamps legados

Timestamps legados sem fuso devem seguir a regra temporal oficial definida para o sistema.

Registros inválidos ou impossíveis de interpretar não devem receber data inventada para entrar no Dashboard.

---

## 32.76 Precisão monetária

Cálculos financeiros devem utilizar a política oficial de precisão e arredondamento monetário.

O frontend não deve recalcular totais financeiros com lógica diferente do backend.

---

# DESEMPENHO E BACKEND

## 32.77 Cálculo no backend

Cards, gráficos e rankings devem ser calculados no backend.

O navegador não deve carregar milhares de Vendas, pagamentos ou movimentações para produzir os indicadores localmente.

---

## 32.78 Consultas agregadas

O backend deve utilizar consultas agregadas e estruturas adequadas ao volume de dados.

A implementação deve evitar:

- repetição desnecessária de consultas;
- processamento completo de todo o histórico a cada atualização;
- consultas N+1;
- respostas excessivamente grandes.

---

## 32.79 Cache

O Dashboard pode utilizar cache quando isso não comprometer a exatidão.

O cache deve considerar, no mínimo:

- Loja;
- usuário, quando aplicável;
- perfil;
- período;
- permissões.

Dados gerenciais de Administrador não podem ser reutilizados em resposta de Operador.

---

## 32.80 Invalidação do cache

O cache deve ser invalidado após operações que alterem os indicadores correspondentes.

Também deve ser invalidado:

- na virada do dia;
- após troca de usuário;
- após troca de perfil;
- após Logout;
- quando necessário por atualização manual.

---

## 32.81 Resposta única ou múltiplas consultas

A arquitetura pode utilizar:

- uma resposta agregada;
- múltiplas consultas específicas.

A escolha técnica deve preservar:

- consistência;
- desempenho;
- segurança;
- tratamento de erro;
- ausência de dados residuais.

---

# SEGURANÇA

## 32.82 Sessão obrigatória

O Dashboard exige Sessão válida.

O backend deve recusar requisições sem autenticação.

---

## 32.83 Perfil autoritativo

O perfil deve ser obtido da Sessão e do cadastro persistido.

O navegador não pode enviar:

isAdmin = true

ou equivalente como autorização.

---

## 32.84 Isolamento por Loja

Todos os indicadores devem considerar somente os dados da Loja autenticada.

O sistema deve impedir:

- consulta de outra Loja;
- alteração de identificador da Loja pelo navegador;
- mistura de dados entre Lojas;
- cache compartilhado incorretamente.

---

## 32.85 Dados restritos após Logout

Após Logout, os dados do Dashboard devem ser removidos da interface.

O cache protegido do usuário deve ser invalidado.

Novo usuário não deve visualizar valores renderizados pelo usuário anterior.

---

# TESTES E VALIDAÇÃO

## 32.86 Testes dos indicadores

Cada indicador deve possuir testes para:

- conjunto vazio;
- resultado positivo;
- cancelamento;
- Devolução;
- pagamento misto;
- mudança de período;
- virada do dia;
- permissão de perfil.

---

## 32.87 Testes dos gráficos

Os gráficos devem possuir testes para:

- nenhum dado;
- um ponto;
- múltiplos pontos;
- valores líquidos positivos;
- valores líquidos negativos;
- combinação de positivos e negativos;
- troca de período;
- limpeza de tooltip.

---

## 32.88 Testes de perfil

Os testes devem confirmar que:

- Administrador recebe dados autorizados;
- Operador não recebe dados restritos;
- a grade acompanha os cards visíveis;
- Login, Logout e troca de usuário não deixam estado residual.

---

## 32.89 Testes de timezone

Os testes devem cobrir:

- fronteira da meia-noite operacional;
- registros antes e depois da virada;
- virada de mês;
- filtro Hoje;
- 7 dias;
- 30 dias;
- Mês atual;
- período Personalizado, quando disponível.

---

## 32.90 Testes responsivos

O Dashboard deve ser validado visualmente ou por teste compatível em:

- desktop;
- tablet;
- celular.

A validação deve considerar Administrador e Operador.

---

# REGRAS GERAIS

## 32.91 Regras gerais do Dashboard

O sistema deve:

- possuir Dashboard como Painel Inicial;
- carregar o Dashboard após Login;
- utilizar Loja e usuário da Sessão;
- possuir Dashboard do Administrador;
- possuir Dashboard do Operador;
- restringir Lucro ao Administrador;
- restringir Margem ao Administrador;
- restringir valor financeiro do Estoque ao Administrador;
- não enviar dados restritos ao Operador;
- apresentar Vendas Hoje;
- apresentar Faturamento Hoje ao Administrador;
- apresentar Recebido Hoje ao Administrador;
- diferenciar Faturamento de Recebimento;
- apresentar Crediário em Aberto;
- apresentar Contas a Pagar;
- apresentar Recebíveis de Cartão;
- apresentar Clientes com Condicional;
- apresentar Alertas Ativos;
- apresentar Clientes Atendidos ao Operador;
- apresentar Condicionais ao Operador;
- apresentar Alertas ao Operador;
- apresentar Recebíveis em visão operacional ao Operador;
- tornar cards clicáveis;
- abrir módulos com filtros correspondentes;
- manter card visível quando o valor for zero;
- diferenciar zero de erro;
- possuir gráfico de Vendas por Dia;
- possuir gráfico de Formas de Pagamento;
- possuir gráfico de Faturamento Mensal para o Administrador;
- permitir gráficos operacionais ao Operador;
- impedir gráficos financeiros restritos ao Operador;
- permitir filtro Hoje;
- permitir filtro 7 dias;
- permitir filtro 30 dias;
- permitir filtro Mês atual;
- preservar período Personalizado quando já previsto;
- diferenciar indicadores históricos de posição atual;
- atualizar após Login;
- atualizar ao voltar para o Dashboard;
- atualizar após operações relevantes;
- permitir atualização manual;
- atualizar na virada do dia;
- conferir a data ao recuperar foco ou visibilidade;
- manter somente um timer de virada;
- impedir listeners duplicados;
- limpar estado após Logout;
- possuir layout fixo;
- não permitir reorganização de cards na primeira versão;
- adaptar a grade ao perfil;
- ser responsivo;
- possuir estado de carregamento;
- utilizar skeletons quando aplicável;
- possuir estado de erro;
- permitir tentar novamente;
- tratar Sessão expirada;
- invalidar requisições antigas;
- possuir estados vazios claros;
- não criar gráficos artificiais;
- preservar valores negativos nas legendas;
- utilizar somente valores positivos nas fatias;
- utilizar regras oficiais dos módulos;
- desconsiderar Vendas Canceladas dos resultados válidos;
- considerar Devoluções na data operacional da ocorrência;
- considerar pagamentos mistos;
- utilizar snapshots históricos;
- utilizar America/Sao_Paulo;
- utilizar precisão monetária oficial;
- calcular indicadores no backend;
- utilizar consultas agregadas;
- evitar carregamento integral no navegador;
- permitir cache seguro;
- separar cache por Loja e perfil;
- invalidar cache corretamente;
- exigir Sessão válida;
- validar perfil no backend;
- respeitar isolamento por Loja;
- remover dados após Logout;
- possuir testes de cálculos;
- possuir testes de gráficos;
- possuir testes de perfil;
- possuir testes de timezone;
- possuir validação responsiva.

# 33. IMPRESSÕES E DOCUMENTOS GERADOS

## 33.1 Finalidade

As regras de Impressões e Documentos Gerados definem o padrão de emissão, visualização, impressão e reemissão dos documentos operacionais do sistema.

Os documentos devem representar fielmente as operações persistidas.

A geração de documento não deve:

- alterar a operação de origem;
- recalcular valores históricos com dados atuais;
- criar efeito financeiro;
- alterar Estoque;
- alterar situação da entidade;
- substituir os históricos próprios dos módulos.

---

## 33.2 Documentos e operações de origem

Todo documento operacional deve possuir uma entidade ou operação de origem válida.

Exemplos:

- Venda;
- recebimento de Crediário;
- Condicional;
- Garantia;
- Entrada de Produtos;
- Devolução ao Fornecedor;
- Inventário;
- Conta a Pagar;
- pagamento de Conta;
- outros documentos oficialmente definidos.

O documento deve permanecer vinculado à operação correspondente.

---

## 33.3 Acesso aos documentos

Administrador e Operador podem gerar, visualizar e imprimir documentos das operações que possuem permissão para consultar.

A permissão para imprimir não concede acesso adicional à entidade de origem.

O backend deve validar:

- Sessão;
- Loja;
- usuário;
- perfil;
- permissão sobre a operação;
- dados permitidos no documento.

---

## 33.4 Dados restritos por perfil

Documentos gerados pelo Operador não devem conter informações financeiras restritas ao Administrador.

O Operador não deve receber em documentos:

- Lucro;
- Margem;
- Custo agregado restrito;
- valor financeiro total do Estoque;
- demais informações gerenciais exclusivas.

A restrição deve ocorrer no backend.

Os dados não devem ser enviados ao navegador para serem apenas ocultados visualmente.

---

## 33.5 Formatos oficiais

Os formatos oficiais de documentos são:

- A4/PDF;
- Térmico.

Nem todo documento precisa possuir os dois formatos.

A disponibilidade deve ser definida conforme a finalidade da operação.

---

## 33.6 Formato A4/PDF

O formato A4/PDF deve ser utilizado prioritariamente para documentos completos, detalhados ou destinados a arquivo.

Exemplos:

- Garantia;
- Entrada de Produtos;
- Devolução ao Fornecedor;
- Inventário;
- Relatórios;
- documentos detalhados de Crediário;
- Conta a Pagar;
- documentos administrativos.

---

## 33.7 Formato Térmico

O formato Térmico deve ser utilizado para comprovantes rápidos e operacionais.

Exemplos:

- comprovante de Venda;
- comprovante de recebimento de Crediário;
- Condicional;
- comprovantes financeiros simples.

O formato Térmico deve apresentar somente as informações necessárias e permitidas.

---

## 33.8 Documento sem versão Térmica

Quando determinado documento possuir somente versão A4/PDF, o sistema não deve oferecer impressão Térmica.

Exemplos iniciais:

- Entrada de Produtos;
- Inventário;
- Devolução ao Fornecedor detalhada.

Uma requisição manipulada para formato não permitido deve ser recusada pelo backend.

---

## 33.9 Identificação da Loja

Os documentos devem utilizar a identificação atual da Loja no momento da geração.

Podem ser apresentados, conforme cadastrados e aplicáveis:

- Logo;
- Nome da Loja;
- Razão Social;
- CPF ou CNPJ;
- Telefone;
- WhatsApp;
- E-mail;
- Endereço;
- dados Pix;
- outras informações institucionais permitidas.

---

## 33.10 Ausência de Logo

Quando a Loja não possuir Logo cadastrada, o documento deve utilizar o Nome da Loja como identificação principal.

A ausência de Logo não deve impedir a geração do documento.

---

## 33.11 Dados vazios da Loja

Campos institucionais sem informação cadastrada não devem produzir linhas vazias ou marcadores desnecessários no documento.

Exemplo:

Se não existir E-mail cadastrado, não apresentar:

E-mail: —.

A composição deve preservar clareza visual.

---

# COMPROVANTE DE VENDA

## 33.12 Comprovante de Venda

Toda Venda concluída deve permitir geração de comprovante.

O comprovante pode possuir:

- formato Térmico;
- formato A4/PDF, quando aplicável.

O documento deve utilizar os dados históricos da Venda.

---

## 33.13 Conteúdo do comprovante de Venda

O comprovante de Venda deve apresentar, no mínimo:

- identificação da Loja;
- número da Venda;
- data e hora;
- usuário responsável;
- Cliente, quando identificado;
- itens;
- quantidade;
- preço unitário praticado;
- desconto;
- subtotal ou total por item, quando aplicável;
- total da Venda;
- Formas de Pagamento;
- quantidade de parcelas do Cartão, quando houver;
- valor de entrada, quando houver;
- Crediário, quando houver;
- troco, quando houver;
- situação atual da Venda.

---

## 33.14 Cliente no comprovante

Quando a Venda possuir Cliente cadastrado, o comprovante pode apresentar:

- Nome completo;
- CPF parcialmente mascarado, quando necessário;
- telefone, quando aplicável.

Quando a Venda utilizar Cliente Padrão, o documento pode apresentar:

Cliente não identificado

ou expressão equivalente.

O sistema não deve inventar um Cliente cadastrado.

---

## 33.15 Itens da Venda

Para cada item, apresentar:

- Nome histórico do Produto;
- Código histórico, quando aplicável;
- Cor;
- Tamanho;
- quantidade;
- preço unitário praticado;
- desconto aplicado ao item, quando existir;
- total do item.

A apresentação deve respeitar os snapshots históricos preservados na Venda.

---

## 33.16 Desconto da Venda

Quando existir desconto geral ou por item, o comprovante deve apresentar a informação de forma clara.

Exemplo:

Subtotal:
R$ 500,00.

Desconto:
R$ 50,00.

Total:
R$ 450,00.

O documento não deve recalcular o desconto utilizando preços atuais.

---

## 33.17 Formas de Pagamento no comprovante

O documento deve apresentar cada componente do pagamento separadamente.

Exemplo:

Dinheiro:
R$ 100,00.

Pix:
R$ 200,00.

Crédito 2x:
R$ 300,00.

Crediário:
R$ 400,00.

Pagamentos mistos devem permanecer identificados.

---

## 33.18 Cartão no comprovante

Quando existir pagamento em Crédito, o comprovante deve apresentar:

- Crédito;
- quantidade de parcelas;
- valor bruto atribuído à Venda.

Exemplos:

Crédito 1x:
R$ 500,00.

Crédito 3x:
R$ 900,00.

Não é obrigatório apresentar a Taxa da operadora ao Cliente.

---

## 33.19 Débito no comprovante

Pagamento em Débito deve ser apresentado como:

Débito.

Não exigir ou inventar Bandeira do Cartão.

---

## 33.20 Troco

Quando existir pagamento em Dinheiro superior ao valor devido e o excesso for oficialmente registrado como troco, o comprovante deve apresentar:

- valor recebido em Dinheiro;
- troco.

Exemplo:

Dinheiro recebido:
R$ 100,00.

Troco:
R$ 20,00.

---

## 33.21 Informações proibidas no comprovante de Venda

O comprovante destinado ao Cliente não deve apresentar:

- Custo do Produto;
- Margem;
- Lucro;
- valor financeiro do Estoque;
- Taxa interna do Cartão;
- informações técnicas;
- identificadores internos desnecessários.

---

## 33.22 Venda Cancelada

Quando uma segunda via for gerada para Venda Cancelada, o documento deve identificar claramente:

VENDA CANCELADA.

O comprovante não deve aparentar que a Venda permanece válida.

Quando aplicável, pode apresentar:

- data do cancelamento;
- motivo;
- usuário responsável.

---

## 33.23 Venda com Devolução ou Troca

Quando uma Venda possuir Devoluções ou Trocas vinculadas, uma segunda via detalhada pode identificar a situação atual.

O documento original da Venda não deve ser reescrito silenciosamente.

A apresentação deve deixar clara a diferença entre:

- operação original;
- operações posteriores;
- situação atual.

---

# DOCUMENTOS DO CREDIÁRIO

## 33.24 Documento de Crediário

Venda com Crediário deve permitir geração de documento específico.

O documento deve apresentar:

- Cliente;
- Venda de origem;
- valor total da Venda;
- entrada, quando existir;
- valor financiado;
- quantidade de parcelas;
- parcelas;
- vencimentos;
- valores;
- saldo inicial;
- usuário responsável;
- data e hora da operação.

---

## 33.25 Identificação das parcelas

As parcelas do Crediário devem ser apresentadas no formato:

- 1/1;
- 1/2 e 2/2;
- 1/3, 2/3 e 3/3.

A identificação deve utilizar a quantidade total oficial de parcelas.

Não apresentar somente:

Parcela 1

sem indicar o total, quando o documento detalhado permitir a identificação completa.

---

## 33.26 Datas das parcelas

Os vencimentos devem utilizar as datas civis históricas preservadas no Crediário.

A segunda e a terceira parcelas devem refletir as datas oficialmente geradas a partir da data informada para a primeira parcela.

O documento não deve recalcular vencimentos utilizando a data atual.

---

## 33.27 Resumo completo do Crediário

O sistema deve permitir documento completo, preferencialmente A4/PDF, contendo todas as parcelas.

O resumo deve apresentar:

- valor financiado;
- total de parcelas;
- valor de cada parcela;
- vencimento;
- situação inicial;
- saldo inicial de cada parcela.

---

## 33.28 Carnê do Crediário

O sistema deve permitir geração de carnê simples.

Cada parte do carnê deve apresentar, no mínimo:

- identificação da Loja;
- Cliente;
- número da Venda ou Crediário;
- identificação da parcela;
- vencimento;
- valor original da parcela;
- espaço para confirmação ou anotação operacional, quando aplicável.

---

## 33.29 Carnê e pagamento parcial

O carnê representa os valores originais das parcelas no momento de sua geração.

Pagamentos parciais posteriores não devem reescrever automaticamente carnês já impressos.

Uma nova via detalhada pode apresentar o saldo atual.

O documento deve identificar quando representa:

- valor original;
- posição atual.

---

## 33.30 Crediário renegociado

Quando houver Renegociação oficialmente implementada, a nova documentação deve identificar:

- obrigação anterior;
- novo acordo;
- novas datas;
- novos valores;
- usuário responsável;
- data da Renegociação.

O documento original não deve ser apagado.

---

# COMPROVANTE DE RECEBIMENTO DO CREDIÁRIO

## 33.31 Comprovante de recebimento

Cada operação válida de recebimento de Crediário deve permitir geração de comprovante.

O comprovante pode possuir:

- formato Térmico;
- formato A4/PDF, quando aplicável.

---

## 33.32 Conteúdo do comprovante de recebimento

O comprovante deve apresentar:

- identificação da Loja;
- Cliente;
- Venda ou Crediário de origem;
- parcelas envolvidas;
- valor recebido em cada parcela;
- valor total recebido;
- Forma de Pagamento;
- saldo anterior;
- saldo atual;
- data e hora;
- usuário responsável.

---

## 33.33 Recebimento de várias parcelas

Quando uma única operação receber valores de várias parcelas, deve ser gerado um único comprovante da operação.

O documento deve listar separadamente as parcelas afetadas.

Exemplo:

Parcela 1/3:
R$ 200,00.

Parcela 2/3:
R$ 100,00.

Total recebido:
R$ 300,00.

---

## 33.34 Recebimento parcial

Quando o recebimento for parcial, o comprovante deve apresentar claramente:

- saldo anterior;
- valor recebido;
- saldo restante.

Exemplo:

Saldo anterior:
R$ 500,00.

Recebido:
R$ 200,00.

Saldo atual:
R$ 300,00.

---

## 33.35 Recebimento com Cartão

Quando um recebimento de Crediário utilizar Débito ou Crédito, o documento deve apresentar a Forma de Pagamento correspondente.

No Crédito, apresentar a quantidade de parcelas quando essa informação fizer parte da operação.

O comprovante não deve tratar o pagamento em Cartão como novo Crediário.

---

## 33.36 Estorno de recebimento

Quando um recebimento tiver sido estornado, a segunda via ou detalhe atual deve identificar a situação.

O documento do recebimento original não deve ser apagado.

A operação de estorno deve possuir documento ou identificação própria quando aplicável.

---

# DOCUMENTO DO CONDICIONAL

## 33.37 Documento do Condicional

Todo Condicional confirmado deve permitir geração de documento.

O documento pode possuir:

- formato Térmico;
- formato A4/PDF.

---

## 33.38 Conteúdo do Condicional

O documento deve apresentar:

- identificação da Loja;
- número do Condicional;
- Cliente;
- telefone;
- data e hora da saída;
- prazo fixo de 3 dias;
- data prevista de retorno;
- Produtos;
- Códigos;
- Cor;
- Tamanho;
- quantidades;
- preços vigentes informativos;
- usuário responsável;
- espaço para assinatura manual do Cliente, quando em A4.

---

## 33.39 Preços do Condicional

Os preços apresentados no documento possuem finalidade informativa.

O documento deve utilizar o preço fotografado ou oficialmente preservado no Condicional.

Alteração posterior do preço do Produto não deve alterar a segunda via histórica do Condicional.

---

## 33.40 Prazo do Condicional

O documento deve apresentar o prazo oficial de 3 dias.

A data prevista de retorno deve ser calculada pelo backend utilizando a data operacional da saída.

O usuário não pode alterar livremente o prazo no documento.

---

## 33.41 Retorno parcial

Quando o Condicional possuir retorno parcial, a operação correspondente deve permanecer no histórico.

Uma nova via detalhada pode apresentar:

- itens originalmente entregues;
- itens devolvidos;
- itens mantidos;
- itens ainda pendentes.

O documento original da saída não deve ser reescrito.

---

## 33.42 Condicional finalizado com Venda

Quando Produtos mantidos pelo Cliente gerarem Venda, os detalhes do Condicional devem identificar a Venda vinculada.

O comprovante da Venda deve ser emitido pelo fluxo oficial de Vendas.

O documento do Condicional não substitui o comprovante da Venda.

---

## 33.43 Condicional atrasado

Quando uma segunda via for gerada após o prazo de 3 dias e o Condicional permanecer ativo, o documento detalhado pode identificar:

ATRASADO.

A identificação deve utilizar o estado operacional atual.

---

# DOCUMENTO DE GARANTIA

## 33.44 Documento de Garantia

Toda Garantia deve permitir geração de documento.

O formato principal deve ser A4/PDF.

Versão Térmica pode ser disponibilizada somente para resumo simples, caso oficialmente implementada.

---

## 33.45 Conteúdo da Garantia

O documento deve apresentar:

- identificação da Loja;
- número da Garantia;
- Venda de origem;
- Cliente;
- contato;
- Produto;
- Código;
- quantidade;
- data da Venda;
- categoria do defeito;
- descrição do defeito;
- situação física do Produto;
- Fornecedor, quando houver;
- protocolo, quando houver;
- situação da Garantia;
- solução, quando definida;
- data e hora;
- usuário responsável.

---

## 33.46 Fotos da Garantia

Fotos podem ser incluídas no PDF detalhado.

As fotos não devem ser incluídas obrigatoriamente em impressão Térmica.

O documento pode organizar as fotos em páginas adicionais.

A ausência de fotos não impede a geração quando a Garantia for válida.

---

## 33.47 Garantia sem prazo fixo

O documento não deve informar prazo máximo fixo de Garantia quando essa regra não existe no sistema.

Pode apresentar:

- data da Venda;
- quantidade de dias transcorridos.

A informação não representa aprovação automática.

---

## 33.48 Garantia enviada ao Fornecedor

Quando a Garantia estiver com o Fornecedor, o documento pode apresentar:

- Fornecedor;
- data de envio;
- protocolo;
- última atualização;
- situação atual.

---

## 33.49 Garantia Resolvida ou Recusada

Quando Resolvida, apresentar a solução adotada.

Quando Recusada, apresentar o motivo da recusa.

Quando Cancelada, identificar claramente:

GARANTIA CANCELADA.

O documento não deve ocultar a situação atual.

---

# ENTRADAS DE PRODUTOS

## 33.50 Documento da Entrada

Toda Entrada confirmada deve permitir geração de documento A4/PDF.

Não é necessária versão Térmica na primeira implementação.

---

## 33.51 Conteúdo da Entrada

O documento deve apresentar:

- identificação da Loja;
- número da Entrada;
- Fornecedor;
- data e hora;
- usuário responsável;
- Produtos;
- Códigos;
- quantidades;
- custos unitários históricos;
- custo total por item;
- custo total da Entrada;
- preços informados na operação, quando aplicável;
- Contas a Pagar vinculadas;
- situação da Entrada.

---

## 33.52 Dados restritos da Entrada

Quando o perfil não possuir autorização para valores de Custo ou outros dados financeiros restritos, o backend deve remover esses dados do documento.

O documento do Operador não deve receber colunas restritas para serem apenas ocultadas.

---

## 33.53 Entrada Cancelada

Quando a Entrada estiver Cancelada, o documento deve apresentar claramente:

ENTRADA CANCELADA.

Pode apresentar:

- motivo;
- data e hora do cancelamento;
- usuário responsável;
- movimentação de reversão;
- Contas canceladas vinculadas.

---

## 33.54 Contas vinculadas

O documento pode apresentar, para cada Conta vinculada:

- identificação;
- vencimento;
- valor;
- situação;
- saldo atual, quando o documento representar posição atual.

A emissão original e a posição atual devem permanecer conceitualmente distintas.

---

# INVENTÁRIO

## 33.55 Documento de Inventário

Inventário Finalizado deve permitir geração de A4/PDF.

Inventário Em andamento pode permitir impressão operacional da lista de contagem, quando oficialmente implementada.

Inventário Cancelado pode permitir consulta e PDF histórico.

---

## 33.56 Conteúdo do Inventário Finalizado

O documento deve apresentar:

- identificação da Loja;
- número do Inventário;
- tipo;
- escopo;
- situação;
- data e hora de início;
- usuário que iniciou;
- data e hora de finalização;
- usuário que finalizou;
- observação geral;
- resumo das divergências;
- Produtos;
- quantidade esperada;
- quantidade contada;
- divergência;
- ajuste gerado.

---

## 33.57 Valores gerenciais do Inventário

Valores gerenciais de Custo ou impacto financeiro devem respeitar o perfil autenticado.

Operador pode receber a visão quantitativa permitida.

Administrador pode receber valores gerenciais autorizados.

---

## 33.58 Inventário Cancelado

Documento de Inventário Cancelado deve identificar:

INVENTÁRIO CANCELADO.

Deve apresentar, quando disponíveis:

- motivo;
- usuário;
- data e hora;
- contagens realizadas.

Não apresentar ajustes de Estoque inexistentes.

---

# DEVOLUÇÃO AO FORNECEDOR

## 33.59 Documento de Devolução ao Fornecedor

Toda Devolução ao Fornecedor deve permitir geração de A4/PDF.

Não é necessária versão Térmica inicialmente.

---

## 33.60 Conteúdo da Devolução ao Fornecedor

O documento deve apresentar:

- identificação da Loja;
- número;
- Entrada de origem;
- Fornecedor;
- data e hora;
- usuário responsável;
- motivo;
- Produtos;
- Códigos;
- quantidades;
- custos históricos;
- valor histórico por item;
- valor histórico total;
- tratamento financeiro;
- total conciliado;
- valor pendente;
- situação operacional;
- situação financeira.

---

## 33.61 Devolução Cancelada

Quando a Devolução ao Fornecedor estiver Cancelada, o documento deve apresentar:

DEVOLUÇÃO CANCELADA.

A movimentação original e a reversão devem permanecer identificáveis no histórico detalhado.

---

# CONTAS A PAGAR

## 33.62 Documento da Conta a Pagar

Conta a Pagar deve permitir geração de documento A4/PDF.

Pode existir comprovante simples de pagamento em formato Térmico ou A4, conforme a operação.

---

## 33.63 Conteúdo da Conta a Pagar

O documento deve apresentar:

- identificação da Loja;
- Conta;
- Fornecedor;
- origem;
- descrição;
- categoria;
- emissão;
- vencimento;
- valor original;
- pagamentos;
- descontos;
- juros;
- multas;
- abatimentos;
- Créditos do Fornecedor utilizados;
- saldo atual;
- situação.

---

## 33.64 Comprovante de pagamento de Conta

Cada pagamento válido deve permitir comprovante contendo:

- Fornecedor;
- Conta;
- valor pago;
- Forma de Pagamento;
- saldo anterior;
- saldo atual;
- data e hora;
- usuário responsável.

Quando uma operação pagar várias Contas, o documento deve listar todas as alocações correspondentes.

---

## 33.65 Conta Cancelada

Conta Cancelada deve ser identificada claramente no documento.

Pagamentos e estornos históricos não devem ser apagados.

---

# SEGUNDA VIA

## 33.66 Segunda via

O sistema deve permitir gerar segunda via de documentos a qualquer momento, desde que:

- a operação exista;
- pertença à Loja autenticada;
- o usuário possua permissão;
- o formato seja permitido.

---

## 33.67 Identificação da segunda via

Documento reemitido após a primeira geração deve apresentar:

SEGUNDA VIA.

A identificação deve ser clara, mas não deve prejudicar a leitura do documento.

---

## 33.68 Primeira emissão

O sistema deve persistir que ocorreu uma primeira emissão ou geração oficial do documento.

Apenas abrir a pré-visualização não precisa ser considerado primeira emissão, desde que o arquivo ainda não tenha sido efetivamente gerado, impresso ou baixado conforme o fluxo definido.

A implementação deve possuir um critério único e documentado.

---

## 33.69 Vias posteriores

A segunda e demais vias podem utilizar a mesma identificação:

SEGUNDA VIA.

Não é necessário apresentar:

Terceira via.

Quarta via.

O sistema pode preservar internamente a quantidade de emissões.

---

## 33.70 Segunda via e operação atual

A segunda via deve utilizar os dados históricos da operação.

Quando o documento tiver finalidade de posição atual, pode apresentar também a situação atual e os saldos atuais.

A natureza da informação deve ficar clara.

---

## 33.71 Segunda via de operação Cancelada

Quando a operação estiver Cancelada, a segunda via deve apresentar simultaneamente, quando aplicável:

SEGUNDA VIA.

CANCELADA.

O documento não deve aparentar validade operacional inexistente.

---

## 33.72 Auditoria da segunda via

Não é obrigatório auditar toda reimpressão operacional comum.

Exportações ou documentos classificados como sensíveis podem seguir as regras específicas de Auditoria.

O sistema pode manter um histórico técnico de emissões sem gerar evento central para cada impressão.

---

# DADOS HISTÓRICOS

## 33.73 Dados históricos da operação

Os documentos devem utilizar snapshots e valores históricos da operação.

Exemplos:

- Nome histórico do Produto;
- Marca histórica;
- preço praticado;
- Custo histórico, quando autorizado;
- Forma de Pagamento;
- quantidade de parcelas;
- Taxa histórica;
- Cliente histórico;
- usuário histórico;
- datas históricas.

---

## 33.74 Alteração posterior do Produto

Alterar o cadastro atual do Produto não deve modificar o documento histórico.

Exemplo:

Na Venda:

Marca A.

Atualmente:

Marca B.

Segunda via da Venda:

Marca A.

---

## 33.75 Alteração posterior de preço

Alterar o preço atual do Produto não deve modificar:

- comprovante histórico da Venda;
- documento histórico do Condicional;
- documento histórico da Entrada;
- outros documentos de operações anteriores.

---

## 33.76 Dados históricos inexistentes

Quando um dado histórico não estiver disponível em registro legado, o sistema não deve inventar informação usando o cadastro atual.

Pode apresentar:

- Não informado;
- Histórico indisponível;
- Sem marca;

conforme a regra aplicável.

---

## 33.77 Dados atuais da Loja em nova via

Nova segunda via deve utilizar os dados institucionais atuais da Loja.

Exemplos:

- Logo atual;
- Nome atual;
- Endereço atual;
- Telefone atual.

A operação continua utilizando seus dados históricos próprios.

---

## 33.78 Documentos já gerados

Documento já gerado e persistido não deve ser reescrito automaticamente após alteração de:

- Logo;
- Nome da Loja;
- Endereço;
- Produto;
- Cliente;
- preço;
- situação posterior.

O arquivo histórico permanece como foi gerado.

---

## 33.79 Nova geração e arquivo anterior

Gerar segunda via cria nova representação documental.

O arquivo anteriormente gerado não deve ser sobrescrito silenciosamente quando existir necessidade de preservação documental.

A arquitetura pode armazenar:

- arquivo histórico;
- metadados de geração;
- versão do template.

---

# NUMERAÇÃO E IDENTIFICAÇÃO

## 33.80 Número do documento

O número principal do documento deve ser o número da operação de origem.

Exemplos:

- Venda nº 152;
- Condicional nº 48;
- Garantia nº 20;
- Entrada nº 125;
- Inventário nº 8.

---

## 33.81 Ausência de numeração paralela

O sistema não deve criar uma sequência operacional independente apenas para o PDF ou comprovante.

O documento deve utilizar o identificador oficial da entidade de origem.

---

## 33.82 Documento de suboperação

Quando o documento representar suboperação com identidade própria, deve utilizar a identificação dessa operação.

Exemplos:

- recebimento de Crediário;
- pagamento de Conta;
- Conciliação de Cartão;
- Devolução;
- Troca.

O documento deve também preservar a referência à operação principal.

---

## 33.83 Número definido pelo backend

Os números das operações devem ser definidos pelo backend conforme as regras oficiais.

O navegador não pode informar autoritativamente o número a ser impresso.

---

# ASSINATURAS

## 33.84 Assinatura manual

Documentos A4 podem possuir espaço para assinatura manual.

Exemplos:

- Cliente;
- responsável pela Loja;
- Fornecedor, quando aplicável.

O espaço é opcional conforme o tipo de documento.

---

## 33.85 Assinatura não obrigatória

A ausência de assinatura manual não deve impedir automaticamente a conclusão da operação no sistema.

A assinatura possui finalidade documental complementar.

Quando alguma operação futura exigir assinatura obrigatória, deverá possuir regra específica.

---

## 33.86 Assinatura digital

A primeira versão não deve implementar:

- assinatura digital certificada;
- assinatura eletrônica avançada;
- coleta de assinatura desenhada na tela;
- biometria;
- validação por certificado.

Essas funcionalidades dependem de evolução específica.

---

## 33.87 Assinatura e comprovante Térmico

Documento Térmico pode possuir linha simples para assinatura quando houver espaço e finalidade operacional.

Não é obrigatório em todos os comprovantes.

---

# GERAÇÃO DO DOCUMENTO

## 33.88 Geração pelo backend

Os documentos devem ser gerados pelo backend ou por mecanismo servidor autorizado.

O navegador não deve enviar HTML completo como conteúdo autoritativo do documento.

---

## 33.89 Dados enviados pelo navegador

O navegador pode informar:

- operação selecionada;
- formato solicitado;
- opções visuais permitidas;
- solicitação de primeira ou segunda via, quando necessário.

O backend deve recuperar novamente os dados da operação.

---

## 33.90 Template oficial

Cada documento deve utilizar template oficial correspondente ao tipo e formato.

O template deve respeitar:

- dados permitidos;
- perfil;
- formato;
- situação da operação;
- regras de segunda via;
- identificação da Loja.

---

## 33.91 Versão do template

A arquitetura pode preservar a versão do template utilizada na geração.

Isso ajuda a identificar documentos emitidos antes e depois de alterações visuais.

A versão do template não altera os dados da operação.

---

## 33.92 Estado Gerando documento

Durante a geração, a interface deve apresentar:

Gerando documento...

A ação correspondente deve permanecer temporariamente indisponível.

---

## 33.93 Prevenção de duplo clique

A interface deve impedir múltiplas solicitações simultâneas da mesma geração.

A proteção visual não substitui validações do backend.

---

## 33.94 Falha de geração

Quando a geração falhar, apresentar mensagem equivalente:

Não foi possível gerar o documento. Tente novamente.

A operação de origem não deve ser alterada pela falha documental.

---

## 33.95 Sessão expirada

Quando a Sessão estiver expirada, a geração deve ser recusada.

O sistema deve seguir o fluxo oficial de Sessão expirada.

Nenhum documento protegido deve ser gerado para Sessão inválida.

---

## 33.96 Operação inexistente

Quando a operação não existir ou não pertencer à Loja, o documento não deve ser gerado.

A resposta não deve revelar dados de outra Loja.

---

## 33.97 Formato inválido

Quando o formato solicitado não for permitido para o documento, a geração deve ser recusada.

Exemplo:

Inventário solicita formato Térmico sem suporte oficial.

Resultado:

Formato não permitido para este documento.

---

## 33.98 Documento e estado concorrente

Antes da geração, o backend deve obter o estado persistido atual da operação.

Quando o documento representar posição atual, deve utilizar visão consistente dos dados.

Quando representar operação histórica, deve utilizar os snapshots preservados.

---

# ARMAZENAMENTO E DOWNLOAD

## 33.99 Visualização

O sistema pode permitir pré-visualização antes da impressão ou download.

A pré-visualização deve utilizar os mesmos dados autorizados do documento final.

---

## 33.100 Download

O documento deve poder ser baixado quando o formato permitir.

O nome do arquivo deve ser claro.

Exemplos:

- venda-152.pdf;
- condicional-48.pdf;
- garantia-20.pdf;
- inventario-8.pdf;
- recebimento-crediario-125.pdf.

---

## 33.101 Nome seguro do arquivo

O nome do arquivo não deve conter:

- senha;
- Token;
- CPF completo desnecessário;
- segredo;
- identificador técnico sensível.

Caracteres incompatíveis com sistemas de arquivos devem ser normalizados.

---

## 33.102 Armazenamento de documentos

O sistema pode gerar documentos sob demanda ou armazená-los quando houver necessidade histórica.

A estratégia deve ser definida pela arquitetura conforme o tipo de documento.

Quando o arquivo for persistido, devem ser preservados:

- Loja;
- operação;
- tipo;
- formato;
- data e hora da geração;
- usuário responsável;
- indicador de primeira ou segunda via;
- versão do template, quando aplicável.

---

## 33.103 Isolamento dos arquivos

Arquivos gerados devem respeitar o isolamento por Loja.

O sistema deve impedir:

- download de documento de outra Loja;
- alteração de caminho ou identificador para acessar arquivo alheio;
- URL pública previsível sem autorização;
- combinação de dados entre Lojas.

---

# AUDITORIA E HISTÓRICO

## 33.104 Gerações operacionais comuns

Não é obrigatório gerar evento na Central de Auditoria para toda impressão ou download comum.

Exemplos:

- comprovante de Venda;
- Condicional;
- recebimento de Crediário;
- segunda via comum.

A regra evita volume excessivo.

---

## 33.105 Documentos sensíveis

Documentos ou exportações sensíveis devem seguir as regras oficiais de Auditoria.

Exemplos:

- Relatório de Lucro;
- Central de Auditoria;
- Backup técnico.

---

## 33.106 Metadados de emissão

Mesmo quando não houver evento na Central de Auditoria, o sistema pode preservar metadados próprios da emissão.

Exemplos:

- primeira emissão;
- segunda via;
- usuário;
- data e hora;
- formato.

Esses metadados pertencem ao controle documental.

---

## 33.107 Senhas e segredos

Documentos nunca devem conter:

- senha;
- hash de senha;
- Token de Sessão;
- Token de recuperação;
- chave secreta;
- dados técnicos sensíveis.

---

# PRECISÃO, DATAS E FORMATAÇÃO

## 33.108 Valores monetários

Valores devem utilizar o padrão monetário brasileiro.

Exemplo:

R$ 1.234,56.

Os cálculos devem utilizar a política oficial de precisão e arredondamento.

O documento não deve recalcular valores com lógica diferente do backend.

---

## 33.109 Datas

Datas civis devem utilizar o padrão brasileiro:

DD/MM/AAAA.

Exemplo:

15/07/2026.

---

## 33.110 Horários

Horários devem utilizar apresentação compatível com o padrão brasileiro.

Exemplo:

15/07/2026 às 14:30.

A apresentação deve utilizar:

America/Sao_Paulo.

---

## 33.111 Timestamps históricos

Timestamps persistidos em UTC devem ser convertidos corretamente para apresentação.

Datas civis `YYYY-MM-DD` não devem sofrer conversão de fuso.

---

## 33.112 Quantidades

Quantidades inteiras devem ser apresentadas sem casas decimais quando a regra da entidade exigir unidade inteira.

Exemplo:

3 peças.

Não apresentar:

3,00 peças.

---

# TESTES

## 33.113 Testes dos documentos

Cada documento deve possuir testes para:

- operação válida;
- operação inexistente;
- operação de outra Loja;
- perfil autorizado;
- perfil não autorizado;
- primeira via;
- segunda via;
- operação Cancelada;
- dados históricos;
- ausência de Logo;
- falha de geração.

---

## 33.114 Testes do comprovante de Venda

Os testes devem cobrir:

- Venda simples;
- pagamento misto;
- desconto;
- troco;
- Crédito 1x, 2x e 3x;
- Crediário;
- Cliente cadastrado;
- Cliente Padrão;
- Venda Cancelada;
- Devolução vinculada.

---

## 33.115 Testes do Crediário

Os testes devem cobrir:

- uma parcela;
- duas parcelas;
- três parcelas;
- entrada;
- vencimentos;
- recebimento parcial;
- recebimento de várias parcelas;
- estorno;
- segunda via.

---

## 33.116 Testes do Condicional

Os testes devem cobrir:

- prazo de 3 dias;
- Produtos;
- preços históricos;
- retorno parcial;
- finalização;
- Venda vinculada;
- Condicional atrasado;
- segunda via.

---

## 33.117 Testes de permissão

Os testes devem confirmar que:

- Administrador recebe os dados permitidos;
- Operador não recebe dados restritos;
- alteração de parâmetros no navegador não amplia permissão;
- usuário de outra Loja não acessa o documento.

---

## 33.118 Testes de snapshots históricos

Os testes devem alterar o cadastro atual após a operação e confirmar que o documento histórico continua utilizando:

- Nome histórico;
- Marca histórica;
- preço histórico;
- Forma de Pagamento histórica;
- datas históricas.

---

## 33.119 Testes de timezone

Os testes devem validar apresentação de data e hora em:

America/Sao_Paulo.

Devem ser cobertas operações próximas à virada do dia operacional.

---

# REGRAS GERAIS

## 33.120 Regras gerais de Impressões e Documentos Gerados

O sistema deve:

- possuir regras padronizadas de documentos;
- vincular documentos às operações de origem;
- permitir geração ao Administrador;
- permitir geração ao Operador conforme permissões;
- remover dados restritos dos documentos do Operador;
- permitir formato A4/PDF;
- permitir formato Térmico quando aplicável;
- não exigir ambos os formatos para todos os documentos;
- validar o formato no backend;
- utilizar identificação da Loja;
- utilizar Logo quando cadastrada;
- utilizar Nome da Loja quando não houver Logo;
- omitir campos institucionais vazios;
- permitir comprovante de Venda;
- apresentar número da Venda;
- apresentar data e hora;
- apresentar usuário;
- apresentar Cliente;
- apresentar itens;
- apresentar preço praticado;
- apresentar desconto;
- apresentar total;
- apresentar pagamentos mistos;
- apresentar parcelamento do Cartão;
- apresentar troco;
- não apresentar Custo ao Cliente;
- não apresentar Margem;
- não apresentar Lucro;
- identificar Venda Cancelada;
- permitir documento de Crediário;
- apresentar entrada;
- apresentar valor financiado;
- apresentar parcelas;
- utilizar identificação 1/3, 2/3 e 3/3;
- preservar vencimentos;
- permitir resumo completo;
- permitir carnê;
- permitir comprovante de recebimento;
- apresentar saldo anterior;
- apresentar saldo atual;
- gerar um comprovante para recebimento de várias parcelas;
- identificar recebimento parcial;
- permitir documento do Condicional;
- apresentar prazo de 3 dias;
- apresentar retorno previsto;
- utilizar preços históricos;
- permitir espaço para assinatura;
- identificar Condicional atrasado;
- permitir documento de Garantia;
- incluir fotos no PDF detalhado;
- não exigir fotos na impressão Térmica;
- não inventar prazo fixo de Garantia;
- apresentar situação da Garantia;
- permitir documento de Entrada;
- apresentar Produtos e quantidades;
- respeitar permissão sobre Custos;
- identificar Entrada Cancelada;
- permitir documento de Inventário;
- apresentar divergências;
- respeitar permissão sobre valores gerenciais;
- identificar Inventário Cancelado;
- permitir documento de Devolução ao Fornecedor;
- apresentar tratamento financeiro;
- identificar Devolução Cancelada;
- permitir documento de Conta a Pagar;
- permitir comprovante de pagamento de Conta;
- identificar Conta Cancelada;
- permitir segunda via;
- identificar Segunda Via;
- persistir primeira emissão;
- utilizar Segunda Via nas reemissões posteriores;
- utilizar dados históricos da operação;
- utilizar dados atuais da Loja na nova via;
- não reescrever documentos já persistidos;
- preservar arquivos anteriores quando necessário;
- utilizar número da operação;
- não criar numeração paralela desnecessária;
- definir números no backend;
- permitir assinatura manual;
- não exigir assinatura para concluir operação;
- não implementar assinatura digital na primeira versão;
- gerar documentos no backend;
- não aceitar HTML completo do navegador como autoridade;
- utilizar template oficial;
- permitir controle de versão do template;
- apresentar Gerando documento;
- impedir duplo clique;
- tratar falha de geração;
- recusar Sessão expirada;
- recusar operação inexistente;
- recusar operação de outra Loja;
- recusar formato inválido;
- utilizar estado persistido atual quando aplicável;
- permitir pré-visualização;
- permitir download;
- utilizar nome de arquivo seguro;
- permitir armazenamento quando necessário;
- preservar metadados de emissão;
- isolar arquivos por Loja;
- não auditar toda impressão comum;
- auditar documentos sensíveis conforme regra própria;
- nunca incluir senhas ou Tokens;
- utilizar formatação monetária brasileira;
- utilizar datas brasileiras;
- apresentar horários em America/Sao_Paulo;
- respeitar precisão monetária;
- possuir testes de documentos;
- possuir testes de perfil;
- possuir testes históricos;
- possuir testes de timezone.

# 34. LOGS TÉCNICOS E MONITORAMENTO DE ERROS

## 34.1 Finalidade

Os Logs Técnicos registram falhas, comportamentos anormais e eventos técnicos necessários ao diagnóstico, suporte e monitoramento do sistema.

Os Logs Técnicos são diferentes da Auditoria.

A Auditoria registra ações relevantes dos usuários e operações do negócio.

Os Logs Técnicos registram informações relacionadas ao funcionamento técnico da aplicação, da infraestrutura, do banco de dados e das integrações.

Os Logs Técnicos não substituem:

- Auditoria;
- histórico de Vendas;
- histórico financeiro;
- histórico de Estoque;
- histórico de Garantias;
- histórico dos demais módulos.

---

## 34.2 Separação entre Log Técnico e Auditoria

Um mesmo acontecimento pode produzir registros diferentes quando possuir efeito operacional e técnico.

Exemplo:

Usuário tenta finalizar uma Venda.

Ocorre erro inesperado no banco de dados.

Resultado:

Log Técnico:

Falha ao persistir a Venda.

Auditoria:

Não deve registrar Venda concluída, pois a operação sofreu rollback.

Quando aplicável, a Auditoria pode registrar uma tentativa operacional recusada somente se existir regra específica para isso.

O Log Técnico preserva o diagnóstico da falha.

---

## 34.3 Acesso aos Logs Técnicos

Administrador pode acessar uma visão resumida dos erros técnicos relacionados à própria Loja.

Operador não pode acessar a tela de Logs Técnicos.

A autorização deve ser validada no backend.

Ocultar a opção no menu não substitui o controle de permissão.

---

## 34.4 Limites do acesso do Administrador

O Administrador da Loja não deve receber informações técnicas que possam comprometer a segurança ou a infraestrutura.

A visão administrativa não deve expor obrigatoriamente:

- Stack Trace completo;
- comandos SQL completos;
- caminhos internos do servidor;
- variáveis de ambiente;
- credenciais;
- chaves secretas;
- estrutura detalhada da infraestrutura;
- dados de outras Lojas.

Essas informações permanecem restritas ao ambiente técnico da aplicação.

---

## 34.5 Logs gerais de infraestrutura

Eventos gerais de infraestrutura podem não estar vinculados a uma Loja.

Exemplos:

- falha de inicialização do servidor;
- erro de Migration global;
- indisponibilidade geral do banco;
- falha do serviço de armazenamento;
- erro de configuração do ambiente.

Esses eventos não devem ser apresentados ao Administrador comum de uma Loja.

O acesso fica restrito à administração técnica da aplicação.

---

## 34.6 Eventos técnicos registrados

O sistema deve registrar eventos técnicos relevantes, conforme aplicável.

Exemplos:

- erro inesperado no servidor;
- exceção não tratada;
- falha de banco de dados;
- violação de restrição persistente;
- timeout;
- falha de conexão;
- falha na geração de PDF;
- falha na geração de planilha;
- falha no envio de E-mail;
- falha em integração;
- Migration com erro;
- tarefa automática com falha;
- falha ao processar arquivo;
- erro de armazenamento;
- falha de serialização;
- conflito técnico inesperado;
- recurso incompatível ou inexistente, quando relevante;
- falha de rollback;
- falha crítica de integridade.

---

## 34.7 Requisições bem-sucedidas

O sistema não precisa registrar cada requisição bem-sucedida como Log Técnico permanente.

Exemplos que não precisam gerar Log Técnico por padrão:

- abrir uma tela;
- realizar busca válida;
- alterar um filtro;
- carregar uma listagem;
- salvar operação concluída sem anormalidade;
- consultar um cadastro.

Métricas de tráfego e acesso podem utilizar ferramentas próprias de observabilidade sem poluir a tela de erros da Loja.

---

## 34.8 Eventos esperados de negócio

Recusas normais previstas pelas regras de negócio não devem ser classificadas automaticamente como erro técnico.

Exemplos:

- CPF inválido;
- Estoque insuficiente;
- Cliente bloqueado;
- saldo insuficiente;
- usuário sem permissão;
- Conta já paga;
- período inválido;
- senha incorreta;
- Recebível alterado por outro usuário.

Essas situações devem retornar mensagens operacionais adequadas.

Podem gerar Auditoria ou eventos de segurança quando definidos nas regras correspondentes.

---

## 34.9 Erro técnico inesperado

Uma situação deve ser tratada como erro técnico quando o sistema não consegue concluir o comportamento esperado por falha interna ou de infraestrutura.

Exemplos:

- banco indisponível;
- arquivo corrompido;
- exceção não prevista;
- falha ao confirmar transação;
- serviço externo indisponível;
- erro ao gerar documento válido.

---

# SEVERIDADE

## 34.10 Níveis de severidade

Os níveis oficiais dos Logs Técnicos são:

- INFO;
- WARNING;
- ERROR;
- CRITICAL.

A severidade deve ser definida pelo backend ou pelo mecanismo técnico responsável pelo evento.

O usuário não pode alterar a severidade original do Log.

---

## 34.11 Severidade INFO

INFO representa evento técnico relevante sem falha operacional grave.

Exemplos:

- tarefa técnica concluída;
- rotina de manutenção iniciada;
- configuração técnica carregada;
- processo de Migration concluído;
- integração restabelecida.

Eventos INFO não precisam aparecer obrigatoriamente na tela resumida da Loja.

---

## 34.12 Severidade WARNING

WARNING representa comportamento anormal ou condição que exige atenção, mas que não impediu necessariamente a continuidade segura do sistema.

Exemplos:

- tentativa de processamento com dado legado incompleto;
- integração temporariamente lenta;
- arquivo próximo do limite permitido;
- recurso utilizado de forma degradada;
- repetição incomum de uma operação;
- fallback técnico utilizado.

---

## 34.13 Severidade ERROR

ERROR representa falha em uma operação técnica ou funcional.

Exemplos:

- falha ao gerar documento;
- falha ao salvar operação;
- erro de conexão com serviço;
- exceção tratada que impediu a conclusão;
- erro de banco com rollback.

A operação principal não deve permanecer parcialmente concluída quando houver exigência de atomicidade.

---

## 34.14 Severidade CRITICAL

CRITICAL representa risco elevado de indisponibilidade, perda de integridade ou comprometimento amplo do sistema.

Exemplos:

- falha ao executar rollback crítico;
- corrupção detectada;
- banco principal indisponível;
- falha de Migration que impede inicialização;
- inconsistência financeira grave detectada;
- perda de acesso ao armazenamento essencial;
- falha repetida que paralisa módulo crítico.

Eventos CRITICAL devem receber destaque máximo na visão técnica apropriada.

---

## 34.15 Severidade e mensagem pública

A severidade interna não precisa ser apresentada integralmente ao usuário que executou a operação.

O usuário comum deve receber mensagem segura e compreensível.

O Log Técnico preserva os detalhes necessários ao diagnóstico.

---

# VÍNCULO COM LOJA, USUÁRIO E OPERAÇÃO

## 34.16 Vínculo com a Loja

Quando o evento estiver relacionado a uma operação autenticada, o Log deve preservar o vínculo com a Loja correspondente.

O vínculo deve ser obtido da Sessão e do contexto validado pelo backend.

O navegador não deve informar autoritativamente a Loja do evento.

---

## 34.17 Evento sem Loja

Eventos podem permanecer sem Loja quando ocorrerem:

- antes do Login;
- durante inicialização da aplicação;
- em rotina global;
- em infraestrutura compartilhada;
- em Migration;
- em tarefa técnica geral.

Esses eventos não devem ser atribuídos artificialmente a uma Loja.

---

## 34.18 Vínculo com o usuário

Quando disponível, o Log Técnico pode preservar:

- ID do usuário;
- Nome histórico;
- Perfil histórico.

O usuário deve ser obtido da Sessão autenticada.

O navegador não deve informar autoritativamente o responsável.

---

## 34.19 Evento sem usuário

Um evento pode não possuir usuário quando ocorrer:

- antes da autenticação;
- em tarefa automática;
- em rotina de infraestrutura;
- em processamento assíncrono;
- em inicialização;
- após expiração da Sessão sem identificação confiável.

A ausência de usuário não invalida o Log.

---

## 34.20 Referência segura da Sessão

Quando disponível, o Log pode preservar referência interna segura à Sessão.

Não registrar:

- Cookie completo;
- Token de autenticação;
- identificador reutilizável;
- segredo de Sessão.

A referência deve permitir correlação técnica sem permitir reutilização da autenticação.

---

## 34.21 Rota e operação

O Log pode preservar:

- rota;
- método;
- módulo;
- operação;
- tipo de entidade;
- referência da entidade.

Exemplo:

Módulo:
Vendas.

Operação:
Criar Venda.

Referência:
Tentativa vinculada ao Cliente ID 125.

A informação deve ser suficiente para diagnóstico sem exposição desnecessária.

---

## 34.22 Entidade relacionada

Quando o erro estiver relacionado a uma entidade persistida, o Log pode registrar:

- tipo da entidade;
- identificador interno seguro;
- número operacional;
- referência pública permitida.

Exemplos:

Venda nº 152.

Garantia nº 20.

Inventário nº 8.

Não utilizar dados pessoais completos quando um identificador for suficiente.

---

# PROTEÇÃO DE DADOS

## 34.23 Dados secretos proibidos

Os Logs Técnicos nunca devem registrar:

- senha;
- hash de senha;
- confirmação de senha;
- Token de Sessão;
- Cookie;
- Token de recuperação;
- Código de recuperação;
- chave de API;
- segredo de integração;
- chave privada;
- credencial bancária;
- conteúdo integral de Backup;
- dados completos de Cartão;
- código de segurança do Cartão;
- arquivo bruto sensível.

---

## 34.24 Senhas

Quando ocorrer falha relacionada à senha, o Log deve registrar somente o evento técnico necessário.

Exemplo permitido:

Falha ao validar credencial do usuário ID 15.

Exemplo proibido:

Senha informada: 123456.

---

## 34.25 Tokens

Tokens e Códigos de segurança não devem ser incluídos:

- na mensagem;
- no contexto estruturado;
- no Stack Trace sanitizado;
- na URL registrada;
- em parâmetros;
- em cabeçalhos persistidos.

A aplicação deve aplicar sanitização antes da persistência do Log.

---

## 34.26 Dados de Cartão

O sistema não deve registrar dados completos do Cartão.

Como o sistema não exige Bandeira ou número do Cartão, esses dados não devem ser coletados nem persistidos nos Logs.

O Log pode registrar apenas:

- modalidade;
- quantidade de parcelas;
- valor;
- Recebível relacionado.

---

## 34.27 Dados pessoais

O sistema deve evitar registrar dados pessoais completos quando identificadores internos forem suficientes.

Dados que exigem cautela incluem:

- CPF;
- CNPJ;
- telefone;
- E-mail;
- endereço;
- data de nascimento;
- observações pessoais.

---

## 34.28 Uso de identificadores internos

Preferir:

Cliente ID 125.

Produto ID 80.

Venda nº 152.

Fornecedor ID 15.

Evitar:

CPF completo do Cliente.

Endereço completo.

Telefone completo.

---

## 34.29 Mascaragem

Quando dado pessoal for tecnicamente necessário para diagnóstico, ele deve ser mascarado sempre que possível.

Exemplos:

CPF:
***.***.***-09.

E-mail:
m***@dominio.com.br.

Telefone:
(**) *****-1234.

A mascaragem deve ocorrer antes da apresentação ao Administrador.

---

## 34.30 Corpo das requisições

O corpo completo das requisições não deve ser persistido indiscriminadamente.

Quando necessário registrar contexto, incluir apenas os campos técnicos permitidos e sanitizados.

Campos sensíveis devem ser removidos.

---

## 34.31 Arquivos enviados

O Log não deve armazenar o conteúdo binário integral de arquivos enviados.

Pode registrar:

- tipo do arquivo;
- tamanho;
- nome sanitizado;
- motivo da recusa;
- identificador técnico seguro.

---

# MENSAGEM AO USUÁRIO E CÓDIGO DE REFERÊNCIA

## 34.32 Mensagem pública segura

O usuário não deve receber detalhes internos da exceção.

Exemplo de erro interno:

IntegrityError em restrição única do banco.

Mensagem pública:

Não foi possível concluir a operação. Tente novamente.

---

## 34.33 Mensagem específica quando segura

Quando for possível apresentar mensagem operacional clara sem expor detalhes técnicos, o sistema deve fazê-lo.

Exemplos:

Não foi possível gerar o documento. Tente novamente.

Não foi possível enviar o E-mail.

O serviço está temporariamente indisponível.

---

## 34.34 Ausência de Stack Trace para o usuário

A interface não deve apresentar:

- Stack Trace;
- nome de tabela interna;
- comando SQL;
- caminho do servidor;
- nome de variável de ambiente;
- biblioteca interna;
- credencial;
- estrutura da exceção.

---

## 34.35 Código de referência do erro

Cada erro técnico relevante deve possuir identificador único de referência.

Exemplo:

ERR-20260715-A8F21.

O código pode ser apresentado ao usuário.

---

## 34.36 Finalidade do código de referência

O código permite localizar o evento correspondente nos Logs Técnicos.

O usuário pode informar o código ao suporte ou ao Administrador.

O código não deve conter:

- CPF;
- ID sequencial previsível sensível;
- Token;
- Loja em texto aberto;
- informação secreta.

---

## 34.37 Unicidade do código

Cada ocorrência técnica relevante deve possuir código único.

Eventos agrupados podem apresentar um código principal do grupo e permitir acesso aos códigos individuais quando necessário no ambiente técnico.

---

## 34.38 Código em falhas conhecidas

Nem toda validação de negócio precisa gerar código de erro.

Exemplos que não exigem código técnico:

- CPF inválido;
- senha incorreta;
- Estoque insuficiente;
- período inválido.

O código deve ser utilizado para falhas técnicas relevantes.

---

# TELA ERROS DO SISTEMA

## 34.39 Tela administrativa

O sistema deve possuir tela:

ERROS DO SISTEMA.

A tela é acessível somente ao Administrador.

A tela apresenta visão resumida dos eventos técnicos relacionados à própria Loja.

---

## 34.40 Cards

A tela deve apresentar os cards:

- Erros Hoje;
- Erros Críticos;
- Erros Não Resolvidos.

Os valores devem utilizar os eventos visíveis para a Loja autenticada.

---

## 34.41 Card Erros Hoje

Erros Hoje deve apresentar a quantidade de ocorrências técnicas registradas na data operacional atual.

O indicador deve utilizar:

America/Sao_Paulo.

A regra pode considerar WARNING, ERROR e CRITICAL conforme a definição da tela.

Eventos INFO não precisam compor esse card.

---

## 34.42 Card Erros Críticos

Erros Críticos deve apresentar a quantidade de eventos ou grupos de severidade CRITICAL ainda visíveis no período de retenção.

A interface deve deixar claro se o card representa:

- ocorrências;
- grupos.

A definição deve ser consistente.

---

## 34.43 Card Erros Não Resolvidos

Erros Não Resolvidos deve considerar grupos ou eventos nas situações:

- Novo;
- Em análise.

Eventos Resolvidos ou Ignorados não devem compor esse total.

---

## 34.44 Busca

A tela deve permitir busca por:

- código de referência;
- módulo;
- operação;
- mensagem resumida;
- número ou referência da entidade.

A busca deve respeitar o isolamento por Loja.

---

## 34.45 Filtros

A tela deve permitir filtros por:

- período;
- severidade;
- módulo;
- situação.

Os filtros podem ser combinados.

---

## 34.46 Período

Os filtros de período podem utilizar:

- Hoje;
- 7 dias;
- 30 dias;
- Personalizado.

O período Personalizado deve exigir Data inicial e Data final válidas.

---

## 34.47 Listagem

A listagem deve apresentar, no mínimo:

- Data e Hora;
- Código;
- Módulo;
- Mensagem resumida;
- Severidade;
- Quantidade de ocorrências, quando agrupado;
- Situação;
- Ação.

A ação principal deve ser:

VER DETALHES.

---

## 34.48 Ordenação

A ordenação inicial deve priorizar:

1. Severidade;
2. Situação;
3. Última ocorrência mais recente.

Eventos CRITICAL devem possuir maior destaque.

A implementação pode permitir outras ordenações.

---

# SITUAÇÕES DO ERRO

## 34.49 Situações oficiais

As situações administrativas são:

- Novo;
- Em análise;
- Resolvido;
- Ignorado.

A situação administrativa não altera a severidade original do evento.

---

## 34.50 Situação Novo

Novo representa erro ainda não classificado ou tratado administrativamente.

Novos grupos de erro devem iniciar nessa situação.

---

## 34.51 Situação Em análise

Em análise representa erro que está sendo acompanhado.

O Administrador pode adicionar observação administrativa.

Marcar Em análise não resolve a falha técnica.

---

## 34.52 Situação Resolvido

Resolvido representa erro considerado tratado ou cuja causa deixou de ocorrer.

Marcar como Resolvido não apaga:

- evento;
- ocorrências;
- detalhes;
- histórico.

Nova ocorrência tecnicamente equivalente pode reabrir ou gerar novo estado conforme a regra adotada.

---

## 34.53 Situação Ignorado

Ignorado representa erro conhecido que não será tratado naquele momento ou que não exige ação operacional da Loja.

Ignorar não exclui o Log.

A situação pode ser revertida posteriormente.

---

## 34.54 Alteração da situação

Somente Administrador pode alterar a situação administrativa.

A alteração deve registrar:

- situação anterior;
- situação nova;
- usuário responsável;
- data e hora;
- observação, quando informada.

---

## 34.55 Auditoria da classificação

Alterar a situação de um erro técnico pode gerar evento de Auditoria administrativa.

O evento não deve copiar detalhes técnicos sensíveis.

Exemplo:

Mauro marcou o erro ERR-20260715-A8F21 como Em análise.

---

## 34.56 Observação administrativa

O Administrador pode registrar observação relacionada ao tratamento do erro.

A observação deve ser texto simples.

Não permitir inserção de HTML executável.

A observação não modifica o Log Técnico original.

---

## 34.57 Reabertura

Erro marcado como Resolvido ou Ignorado pode voltar para Novo ou Em análise quando:

- ocorrer novamente;
- o Administrador alterar a situação;
- a regra técnica de agrupamento identificar recorrência relevante.

O histórico das alterações deve permanecer preservado.

---

# DETALHES VISÍVEIS AO ADMINISTRADOR

## 34.58 Detalhes do erro

A visão administrativa pode apresentar:

- código de referência;
- data e hora da primeira ocorrência;
- data e hora da última ocorrência;
- quantidade de ocorrências;
- severidade;
- situação;
- módulo;
- operação;
- mensagem resumida;
- usuário relacionado, quando houver;
- perfil histórico;
- referência da entidade;
- observações administrativas;
- resumo técnico sanitizado.

---

## 34.59 Resumo técnico sanitizado

O resumo técnico deve fornecer contexto suficiente para suporte sem expor detalhes sensíveis.

Exemplo:

Falha ao gerar PDF da Venda nº 152.

Não apresentar obrigatoriamente:

File "/app/internal/pdf_engine.py", line 182.

---

## 34.60 Detalhes restritos

Não apresentar ao Administrador comum:

- Stack Trace integral;
- SQL integral;
- credenciais;
- variáveis de ambiente;
- caminhos internos completos;
- configuração da infraestrutura;
- conteúdo bruto de requisição;
- dados de outra Loja.

---

## 34.61 Usuário relacionado

Quando existir usuário relacionado, a tela pode apresentar:

- Nome;
- Perfil histórico.

Não apresentar dados de autenticação.

---

## 34.62 Entidade relacionada

Quando existir entidade relacionada, a tela deve permitir identificar ou abrir a operação correspondente, desde que o Administrador possua permissão.

Exemplos:

VER VENDA.

VER GARANTIA.

VER INVENTÁRIO.

A navegação não deve expor dados de outra Loja.

---

# AGRUPAMENTO

## 34.63 Agrupamento de erros equivalentes

Erros tecnicamente equivalentes podem ser agrupados para evitar repetição excessiva na listagem.

O agrupamento deve utilizar assinatura técnica estável.

---

## 34.64 Assinatura do erro

A assinatura pode considerar, de forma sanitizada:

- tipo da exceção;
- módulo;
- operação;
- ponto de origem;
- mensagem normalizada;
- código interno da falha.

A assinatura não deve utilizar dado pessoal variável de forma que impeça o agrupamento adequado.

---

## 34.65 Exemplo de agrupamento

Falha ao gerar PDF ocorreu 50 vezes.

A tela pode apresentar:

Falha ao gerar PDF.

Ocorrências:
50.

Primeira ocorrência:
10:00.

Última ocorrência:
14:35.

Os eventos individuais permanecem preservados tecnicamente.

---

## 34.66 Erros diferentes não agrupados

Falhas com causas ou operações diferentes não devem ser agrupadas apenas porque possuem texto semelhante.

Exemplo:

Falha ao gerar PDF por arquivo ausente.

Falha ao gerar PDF por timeout.

Podem formar grupos distintos.

---

## 34.67 Situação do grupo

A situação administrativa pode pertencer ao grupo de erros equivalentes.

Nova ocorrência em grupo Resolvido pode:

- reabrir o grupo como Novo;

ou

- preservar Resolvido e indicar recorrência.

A regra escolhida deve ser única e documentada.

Minha recomendação oficial é reabrir como Novo quando ocorrer novamente após a resolução.

---

## 34.68 Contagem das ocorrências

O grupo deve preservar:

- quantidade total;
- primeira ocorrência;
- última ocorrência.

A retenção e o arquivamento podem limitar a quantidade detalhada disponível na tela da Loja.

---

# RETENÇÃO

## 34.69 Retenção na visão da Loja

A tela Erros do Sistema deve manter disponíveis os Logs resumidos dos últimos 90 dias.

O prazo deve utilizar a data operacional oficial.

---

## 34.70 Eventos anteriores a 90 dias

Eventos com mais de 90 dias podem deixar de aparecer na visão administrativa da Loja.

Isso não significa necessariamente exclusão imediata da infraestrutura técnica.

---

## 34.71 Retenção técnica

A retenção completa dos Logs na infraestrutura pode ser superior a 90 dias.

A política técnica depende:

- do ambiente;
- da capacidade de armazenamento;
- da criticidade;
- das exigências de diagnóstico;
- da política de segurança.

---

## 34.72 Logs não são histórico oficial do negócio

A remoção ou arquivamento de Log Técnico não deve apagar:

- Auditoria;
- Venda;
- recebimento;
- pagamento;
- movimentação de Estoque;
- Conta;
- Garantia;
- Inventário;
- documento;
- histórico operacional.

Logs Técnicos não são fonte autoritativa das operações do negócio.

---

## 34.73 Eventos críticos

Eventos CRITICAL podem possuir retenção técnica superior aos demais níveis.

A regra da infraestrutura pode preservar esses eventos por prazo ampliado.

A tela da Loja continua sujeita à visão resumida de 90 dias, salvo evolução futura.

---

## 34.74 Limpeza segura

Rotinas de retenção devem:

- respeitar o prazo;
- não apagar Auditoria;
- não apagar entidades do negócio;
- não bloquear a aplicação;
- registrar falha técnica caso a limpeza não seja concluída.

---

# DATA E HORA

## 34.75 Timestamp do evento

Cada ocorrência deve possuir timestamp oficial.

O timestamp deve ser gerado pelo backend ou pela infraestrutura responsável.

O navegador não deve informar autoritativamente a data do erro.

---

## 34.76 Armazenamento

Novos timestamps devem ser armazenados em UTC com offset explícito ou representação técnica equivalente compatível.

---

## 34.77 Apresentação

A tela administrativa deve apresentar data e hora em:

America/Sao_Paulo.

---

## 34.78 Ordenação temporal

O agrupamento e a listagem devem utilizar os timestamps persistidos.

Não utilizar texto formatado como fonte da ordenação.

---

# ALERTAS E MONITORAMENTO

## 34.79 Erro crítico na Central de Alertas

Falha técnica CRITICAL relacionada à Loja pode gerar Alerta Crítico para o Administrador.

O Operador não deve receber detalhes técnicos sensíveis.

A geração do Alerta depende da relevância operacional para a Loja.

---

## 34.80 Alerta não substitui o Log

O Alerta informa que existe uma situação crítica.

O Log preserva os detalhes técnicos.

Resolver ou marcar o Alerta como lido não altera automaticamente o Log.

---

## 34.81 Erros comuns

Eventos WARNING ou ERROR não precisam gerar Alerta individual na Central de Alertas.

A tela Erros do Sistema é o local principal de acompanhamento técnico administrativo.

---

## 34.82 Monitoramento da infraestrutura

Ferramentas externas de monitoramento podem ser utilizadas para:

- disponibilidade;
- uso de memória;
- CPU;
- banco;
- tempo de resposta;
- erros;
- tarefas;
- integrações.

Essas ferramentas não precisam ser expostas diretamente ao Administrador da Loja.

---

# LOGS DE MIGRATIONS E TAREFAS

## 34.83 Migrations

Falhas de Migration devem ser registradas como evento técnico.

Quando a falha impedir o funcionamento seguro da aplicação, a severidade deve ser CRITICAL.

O sistema não deve continuar silenciosamente em Schema incompatível.

---

## 34.84 Migration concluída

Migration concluída pode gerar evento INFO técnico.

Não é necessário apresentar esse evento na tela da Loja.

---

## 34.85 Tarefas automáticas

Tarefas automáticas devem registrar falhas relevantes.

Exemplos:

- envio de E-mail;
- geração agendada;
- limpeza técnica;
- processamento de arquivo;
- sincronização;
- rotina de alerta.

---

## 34.86 Repetição de tarefa

Quando uma tarefa falhar repetidamente, os erros podem ser agrupados.

O sistema deve preservar a quantidade de tentativas e a última ocorrência.

---

# CONSISTÊNCIA E TRANSAÇÕES

## 34.87 Erro em operação transacional

Quando uma operação crítica falhar, o sistema deve executar rollback conforme as regras do módulo.

O Log deve indicar que a operação falhou.

Não registrar sucesso operacional na Auditoria.

---

## 34.88 Falha no próprio registro do Log

O mecanismo de Log não deve impedir desnecessariamente o rollback da operação principal.

Quando tecnicamente possível, deve existir mecanismo alternativo ou fallback para registrar falhas críticas.

A aplicação não deve mascarar a falha original.

---

## 34.89 Idempotência

Replays idempotentes válidos não devem ser registrados como erros.

Conflito de chave com conteúdo diferente é uma recusa operacional prevista e pode ser registrado como WARNING ou evento de segurança quando relevante.

---

## 34.90 Concorrência

Conflitos concorrentes esperados e tratados não devem ser classificados automaticamente como ERROR.

Exemplo:

Recebível foi alterado por outro usuário.

A operação deve retornar conflito operacional.

Erro técnico deve ser reservado para falha inesperada no mecanismo de concorrência.

---

# ESTADOS VISUAIS

## 34.91 Estado de carregamento

A tela Erros do Sistema deve possuir estado de carregamento claro.

Ao alterar filtros ou página, dados antigos não devem permanecer apresentados como se correspondessem ao novo conjunto.

---

## 34.92 Estado vazio

Quando não existirem erros correspondentes aos filtros, apresentar:

Nenhum erro encontrado.

Quando não existirem erros ativos, pode apresentar:

Nenhum erro técnico pendente.

---

## 34.93 Estado de erro da própria tela

Se a tela de Logs falhar ao carregar, apresentar mensagem discreta.

Exemplo:

Não foi possível carregar os erros do sistema. Tente novamente.

Não expor a exceção interna.

---

## 34.94 Paginação

A tela deve utilizar paginação real ou consulta incremental.

O navegador não deve carregar todos os Logs dos 90 dias para exibir a primeira página.

---

## 34.95 Requisições antigas

Ao alterar busca, filtro ou página, respostas antigas devem ser ignoradas quando não corresponderem ao estado atual.

---

# SEGURANÇA E ISOLAMENTO

## 34.96 Sessão obrigatória

A tela Erros do Sistema exige Sessão válida de Administrador.

O backend deve recusar usuário não autenticado.

---

## 34.97 Perfil autoritativo

O perfil deve ser obtido da Sessão e do cadastro persistido.

O navegador não pode informar:

isAdmin = true

como autorização.

---

## 34.98 Isolamento por Loja

Administrador pode visualizar apenas eventos vinculados à própria Loja.

O sistema deve impedir:

- consultar Log de outra Loja;
- alterar identificador da Loja;
- visualizar usuário de outra Loja;
- abrir entidade de outra Loja;
- exportar Logs de outra Loja.

---

## 34.99 Eventos sem Loja

Eventos sem Loja específica não devem aparecer na tela comum de uma Loja.

Eles permanecem na infraestrutura técnica.

---

## 34.100 Sanitização

Mensagens e contextos devem ser sanitizados antes de:

- persistência;
- apresentação;
- agrupamento;
- exportação.

A sanitização deve remover segredos e dados proibidos.

---

# EXPORTAÇÃO

## 34.101 Exportação dos Logs da Loja

A tela pode permitir ao Administrador exportar a visão resumida em:

- PDF;
- CSV.

A exportação deve respeitar os filtros aplicados.

---

## 34.102 Dados da exportação

A exportação administrativa pode conter:

- código;
- data e hora;
- severidade;
- módulo;
- operação;
- mensagem resumida;
- quantidade de ocorrências;
- situação.

Não deve conter detalhes técnicos restritos.

---

## 34.103 Auditoria da exportação

Exportação de Logs Técnicos deve gerar evento de Auditoria administrativa.

Registrar:

- Administrador;
- data e hora;
- formato;
- filtros gerais.

Não registrar o conteúdo integral do arquivo na Auditoria.

---

# TESTES

## 34.104 Testes dos Logs

Os testes devem cobrir:

- geração de código único;
- vínculo com Loja;
- vínculo com usuário;
- evento sem Loja;
- evento sem usuário;
- severidades;
- sanitização;
- ausência de senha;
- ausência de Token;
- mascaragem;
- agrupamento;
- retenção;
- permissão.

---

## 34.105 Testes da mensagem pública

Os testes devem confirmar que exceções internas não são apresentadas ao usuário.

A resposta pública pode incluir o código de referência.

---

## 34.106 Testes de isolamento

Os testes devem confirmar que Administrador de uma Loja não consulta Logs de outra Loja.

Operador deve receber recusa de autorização.

---

## 34.107 Testes de agrupamento

Os testes devem cobrir:

- eventos equivalentes agrupados;
- eventos diferentes separados;
- primeira ocorrência;
- última ocorrência;
- contagem;
- reabertura após nova ocorrência.

---

## 34.108 Testes de retenção

Os testes devem validar a janela de 90 dias da tela da Loja.

A retenção não pode alterar Auditoria ou entidades operacionais.

---

## 34.109 Testes de dados sensíveis

Os testes devem confirmar que não são persistidos ou apresentados:

- senha;
- hash;
- Token;
- Cookie;
- Código de recuperação;
- chave secreta;
- corpo bruto sensível.

---

# REGRAS GERAIS

## 34.110 Regras gerais dos Logs Técnicos

O sistema deve:

- possuir Logs Técnicos;
- diferenciar Logs de Auditoria;
- não substituir históricos dos módulos;
- permitir acesso resumido somente ao Administrador;
- impedir acesso do Operador;
- restringir detalhes sensíveis de infraestrutura;
- manter eventos gerais fora da visão da Loja;
- registrar erros inesperados;
- registrar falhas de banco;
- registrar timeouts;
- registrar falhas de documentos;
- registrar falhas de integração;
- registrar falhas de E-mail;
- registrar falhas de Migration;
- registrar falhas de tarefas;
- registrar exceções não tratadas;
- não registrar toda requisição bem-sucedida;
- diferenciar recusa de negócio de erro técnico;
- utilizar severidades INFO, WARNING, ERROR e CRITICAL;
- definir severidade no backend;
- vincular evento à Loja quando aplicável;
- permitir evento sem Loja;
- vincular usuário quando disponível;
- permitir evento sem usuário;
- utilizar referência segura da Sessão;
- registrar rota e operação quando apropriado;
- vincular entidade por referência segura;
- nunca registrar senha;
- nunca registrar hash de senha;
- nunca registrar Token;
- nunca registrar Cookie;
- nunca registrar Código de recuperação;
- nunca registrar chave de API;
- nunca registrar segredo;
- nunca registrar dados completos de Cartão;
- nunca registrar conteúdo integral de Backup;
- evitar dados pessoais completos;
- preferir IDs internos;
- mascarar dados quando necessários;
- não persistir corpo completo indiscriminadamente;
- não armazenar arquivo bruto;
- apresentar mensagem pública segura;
- não apresentar Stack Trace;
- gerar código de referência único;
- não exigir código para validações comuns;
- possuir tela Erros do Sistema;
- possuir cards Erros Hoje, Erros Críticos e Erros Não Resolvidos;
- permitir busca;
- permitir filtros;
- possuir listagem;
- possuir VER DETALHES;
- utilizar situações Novo, Em análise, Resolvido e Ignorado;
- permitir alteração de situação pelo Administrador;
- preservar histórico de classificação;
- permitir observação administrativa;
- não alterar o Log original;
- permitir reabertura;
- apresentar detalhes sanitizados;
- não apresentar SQL completo;
- não apresentar caminhos internos;
- não apresentar variáveis de ambiente;
- agrupar erros equivalentes;
- preservar ocorrências individuais tecnicamente;
- utilizar assinatura técnica estável;
- não agrupar causas diferentes;
- reabrir grupo Resolvido após nova ocorrência;
- manter visão da Loja por 90 dias;
- permitir retenção técnica superior;
- não apagar Auditoria;
- não apagar histórico operacional;
- gerar timestamps oficiais;
- armazenar timestamps em UTC;
- apresentar em America/Sao_Paulo;
- permitir Alerta Crítico quando aplicável;
- não transformar todo erro em Alerta;
- registrar falhas de Migrations;
- registrar falhas de tarefas;
- tratar rollback corretamente;
- não registrar sucesso após falha;
- não tratar replay idempotente como erro;
- diferenciar conflito esperado de falha técnica;
- possuir estado de carregamento;
- possuir estado vazio;
- possuir estado de erro;
- utilizar paginação real;
- invalidar respostas antigas;
- exigir Sessão válida;
- validar perfil no backend;
- respeitar isolamento por Loja;
- ocultar eventos gerais da Loja;
- sanitizar dados;
- permitir exportação resumida;
- auditar exportação;
- possuir testes de Log;
- possuir testes de segurança;
- possuir testes de agrupamento;
- possuir testes de retenção;
- utilizar backend e infraestrutura como fontes autoritativas.

# 35. SEGURANÇA CONSOLIDADA DO SISTEMA

## 35.1 Finalidade

A Segurança Consolidada estabelece as regras obrigatórias de proteção aplicáveis a todo o sistema.

Estas regras possuem prioridade sobre implementações específicas dos módulos sempre que houver conflito.

Todo módulo deve obedecer obrigatoriamente às regras desta seção.

---

## 35.2 Objetivos

Os objetivos da Segurança são:

- garantir confidencialidade;
- garantir integridade;
- garantir disponibilidade;
- impedir acesso não autorizado;
- impedir alteração indevida de dados;
- impedir vazamento entre Lojas;
- impedir manipulação pelo navegador;
- garantir rastreabilidade das operações.

---

## 35.3 Backend como autoridade

Toda decisão de segurança deve ser tomada pelo backend.

O frontend possui finalidade exclusivamente operacional.

O navegador nunca será considerado fonte autoritativa para:

- usuário;
- perfil;
- Loja;
- permissões;
- preços;
- custos;
- estoque;
- saldos;
- datas;
- situação de entidades.

---

## 35.4 Frontend

O frontend pode:

- validar preenchimento;
- melhorar experiência do usuário;
- impedir erros simples;
- exibir mensagens.

O frontend nunca substitui validações do backend.

---

## 35.5 Confiança Zero

Todo dado recebido pelo backend deve ser tratado como potencialmente inválido.

Mesmo quando enviado pelo próprio sistema.

---

# AUTENTICAÇÃO

## 35.6 Sessão obrigatória

Toda operação protegida exige Sessão válida.

Não existirão operações autenticadas apenas pelo frontend.

---

## 35.7 Login

O Login deverá seguir exclusivamente as regras da Seção Login.

Após autenticação válida deverá existir Sessão autenticada.

---

## 35.8 Logout

Logout deve:

- invalidar Sessão;
- remover Token;
- limpar caches protegidos;
- remover dados sensíveis da interface;
- impedir reutilização da autenticação.

---

## 35.9 Sessão expirada

Quando a Sessão expirar:

o backend deverá recusar imediatamente novas operações.

O frontend deverá:

- limpar dados protegidos;
- redirecionar para Login;
- impedir continuidade da operação.

---

## 35.10 Reautenticação

Quando uma operação crítica exigir confirmação de identidade futuramente, deverá existir mecanismo de reautenticação.

Na primeira versão essa funcionalidade não será obrigatória.

---

# AUTORIZAÇÃO

## 35.11 Perfil

Toda autorização deverá utilizar exclusivamente o Perfil persistido da Sessão.

Nunca utilizar:

isAdmin enviado pelo navegador.

---

## 35.12 Verificação

Toda rota protegida deve validar:

- autenticação;
- perfil;
- Loja;
- permissão da operação.

Ocultar botão não concede segurança.

---

## 35.13 Permissões

Cada operação deverá validar sua permissão individual.

Exemplo:

Usuário pode visualizar Clientes.

Isso não significa que possa:

- excluir Cliente;
- alterar limite;
- cancelar Venda;
- alterar Estoque.

Cada operação possui autorização própria.

---

## 35.14 Permissões do menu

Menus ocultos possuem apenas finalidade visual.

Mesmo que um usuário descubra a URL diretamente, o backend deverá impedir o acesso.

---

## 35.15 Mudança de Perfil

Quando o Perfil for alterado:

a nova permissão somente terá efeito após nova autenticação ou atualização oficial da Sessão.

---

# ISOLAMENTO POR LOJA

## 35.16 Isolamento obrigatório

Todo registro pertence obrigatoriamente a uma Loja.

Nenhuma consulta poderá retornar dados de outra Loja.

---

## 35.17 StoreId

StoreId nunca será confiado ao navegador.

Será obtido exclusivamente da Sessão autenticada.

---

## 35.18 Alteração manual

Modificar:

storeId

companyId

tenantId

ou parâmetros semelhantes nunca poderá permitir acesso a outra Loja.

---

## 35.19 Consultas

Toda consulta deverá conter filtro obrigatório pela Loja autenticada.

Sem exceções.

---

## 35.20 Escritas

Toda gravação deverá registrar automaticamente a Loja correspondente.

Nunca aceitar Loja enviada pelo navegador.

---

## 35.21 Uploads

Todo arquivo deverá pertencer exclusivamente à Loja autenticada.

---

## 35.22 Downloads

Todo documento deverá validar:

- Loja;
- Sessão;
- permissão.

Antes da entrega do arquivo.

---

## 35.23 Auditoria

Toda Auditoria deverá permanecer isolada por Loja.

---

## 35.24 Logs

Logs administrativos apresentados à Loja nunca poderão conter dados pertencentes a outra Loja.

---

# VALIDAÇÃO

## 35.25 Backend

Todo dado deverá ser validado novamente pelo backend.

Mesmo quando o frontend já realizou validação.

---

## 35.26 Tipos

Validar:

- inteiro;
- decimal;
- texto;
- data;
- enum;
- boolean;
- UUID;
- identificadores.

---

## 35.27 Limites

Validar:

- tamanho mínimo;
- tamanho máximo;
- obrigatoriedade;
- formato;
- unicidade quando necessária.

---

## 35.34 Datas

Datas deverão seguir regras oficiais do sistema.

Nunca confiar na data enviada pelo navegador.

---

## 35.29 Valores monetários

Valores monetários deverão ser recalculados pelo backend.

Nunca aceitar total enviado pelo frontend como valor definitivo.

---

## 35.30 Estoque

Toda movimentação deverá recalcular disponibilidade imediatamente antes da confirmação.

Nunca confiar apenas na consulta inicial.

---

# HTTPS

## 35.31 Produção

Todo ambiente de produção deverá utilizar HTTPS.

---

## 35.32 Dados protegidos

Nunca transmitir por HTTP:

- senha;
- sessão;
- documentos;
- dados financeiros;
- dados pessoais.

---

## 35.33 Cookies

Quando utilizados deverão possuir:

- HttpOnly;
- Secure;
- SameSite.

Conforme ambiente.

---

## 35.34 CSRF

Quando autenticação utilizar Cookie deverão existir mecanismos oficiais de proteção CSRF.

---

## 35.35 Cabeçalhos

Respostas deverão utilizar cabeçalhos compatíveis com boas práticas de segurança.

A configuração detalhada dependerá da infraestrutura adotada.

---

# UPLOADS

## 35.36 Validação

Todo upload deverá validar:

- tipo real;
- extensão;
- tamanho;
- autorização;
- Loja;
- usuário.

---

## 35.37 Nome do arquivo

Nunca utilizar diretamente o nome enviado pelo usuário.

O sistema deverá gerar nome seguro.

---

## 35.38 Extensão

A extensão deverá ser compatível com o tipo real do arquivo.

Alterar apenas a extensão não deverá permitir upload inválido.

---

## 35.39 Tamanho

Todo upload deverá respeitar limite máximo configurado.

---

## 35.40 Local de armazenamento

Arquivos protegidos nunca deverão ficar acessíveis por URL pública previsível.

## 35.41 Downloads protegidos

Todo download deverá validar obrigatoriamente:

- Sessão válida;
- Loja autenticada;
- Perfil;
- Permissão sobre o documento;
- Existência do documento.

O backend nunca deverá entregar arquivos protegidos apenas porque o usuário conhece a URL.

---

## 35.42 Links públicos

Documentos internos não deverão possuir links públicos permanentes.

Quando necessário compartilhar documentos, utilizar links temporários com expiração e validação.

---

## 35.43 Manipulação de URL

Modificar manualmente:

- ID da Venda;
- ID do Cliente;
- ID da Garantia;
- ID do Documento;
- ID do Inventário;
- qualquer identificador interno;

nunca poderá permitir acesso a informações de outra Loja ou sem autorização.

---

# SQL INJECTION

## 35.44 Consultas

Todas as consultas ao banco deverão utilizar:

- parâmetros preparados (Prepared Statements);
- ORM;
- Query Builder seguro;
- mecanismo equivalente.

---

## 35.45 Proibição

É proibido montar comandos SQL concatenando diretamente valores enviados pelo usuário.

Exemplo proibido:

SELECT * FROM clientes WHERE nome = '" + nome + "'.

---

## 35.46 Stored Procedures

Caso Stored Procedures sejam utilizadas, também deverão utilizar parâmetros seguros.

---

## 35.47 Pesquisa

Campos de pesquisa textual deverão ser tratados como dados.

Nunca interpretar conteúdo pesquisado como comando SQL.

---

# XSS

## 35.48 Entrada de texto

Todo texto informado pelo usuário deverá ser tratado como texto simples.

---

## 35.49 HTML

Não interpretar HTML enviado pelo usuário.

Exemplos:

- observações;
- descrições;
- comentários;
- motivos;
- histórico;
- mensagens.

---

## 35.50 Escape

A apresentação deverá escapar caracteres especiais antes da renderização.

---

## 35.51 JavaScript

Nunca executar JavaScript proveniente de campos cadastrados.

---

## 35.52 Sanitização

Quando existir necessidade futura de aceitar HTML controlado, deverá existir sanitização específica.

Na primeira versão não será permitido HTML.

---

# CSRF

## 35.53 Cookies

Quando autenticação utilizar Cookies, todas as operações de escrita deverão possuir proteção CSRF.

---

## 35.54 Operações protegidas

Exemplos:

- Venda;
- Cancelamento;
- Entrada;
- Recebimento;
- Pagamento;
- Inventário;
- Garantia;
- Configurações.

---

## 35.55 GET

Operações GET nunca deverão alterar dados persistidos.

---

# IDEMPOTÊNCIA

## 35.56 Objetivo

Operações críticas deverão impedir duplicidade causada por:

- duplo clique;
- atualização da página;
- reenvio automático;
- perda de conexão;
- repetição de requisição.

---

## 35.57 Operações obrigatórias

Aplicar proteção em:

- Venda;
- Recebimento de Crediário;
- Pagamento de Conta;
- Conciliação;
- Estorno;
- Cancelamento;
- Inventário;
- Entrada;
- Devolução.

---

## 35.58 Chave de Idempotência

Quando utilizada, deverá possuir validade limitada e ser vinculada:

- à Loja;
- ao usuário;
- à operação.

---

## 35.59 Repetição

Repetir a mesma operação idempotente não poderá produzir efeitos duplicados.

---

# TRANSAÇÕES

## 35.60 Atomicidade

Operações compostas deverão ocorrer dentro de transação única.

Ou todas as alterações são persistidas ou nenhuma delas.

---

## 35.61 Rollback

Falhas durante transações deverão executar rollback completo.

Nunca deixar:

- Estoque alterado;
- Financeiro não alterado;
- Auditoria inconsistente.

---

## 35.62 Consistência

Após confirmação da transação o banco deverá permanecer consistente.

---

# CONCORRÊNCIA

## 35.63 Revalidação

Antes da confirmação deverão ser revalidados:

- Estoque;
- Saldos;
- Situação da entidade;
- Permissões.

---

## 35.64 Alterações simultâneas

Quando dois usuários alterarem o mesmo registro simultaneamente deverá existir tratamento oficial de concorrência.

---

## 35.65 Estoque

Nunca permitir venda utilizando saldo obtido apenas na abertura da tela.

---

## 35.66 Inventário

Inventários deverão respeitar bloqueios definidos nas regras específicas do módulo.

---

# RATE LIMIT

## 35.67 Limitação

Operações sensíveis poderão possuir limitação de frequência.

Exemplos:

- Login;
- Recuperação de senha;
- Geração de documentos;
- Exportações.

---

## 35.68 Objetivo

Evitar:

- ataques automatizados;
- força bruta;
- consumo abusivo;
- negação de serviço.

---

# CABEÇALHOS DE SEGURANÇA

## 35.69 Respostas HTTP

A infraestrutura deverá utilizar cabeçalhos compatíveis com boas práticas.

Exemplos:

- Content Security Policy;
- X-Content-Type-Options;
- Referrer Policy;
- Frame Options.

A implementação dependerá da infraestrutura escolhida.

---

## 35.70 Cache

Conteúdo protegido não deverá permanecer em cache compartilhado quando isso representar risco de exposição.

---

# LOGS DE SEGURANÇA

## 35.71 Eventos

Eventos relevantes poderão gerar Logs de Segurança.

Exemplos:

- tentativas repetidas de Login;
- acesso negado;
- manipulação de parâmetros;
- Token inválido;
- falha CSRF.

---

## 35.72 Dados proibidos

Logs de Segurança nunca deverão registrar:

- senhas;
- tokens;
- cookies;
- segredos;
- chaves privadas.

---

## 35.73 Integração

Logs de Segurança deverão seguir as regras da Seção de Logs Técnicos quando aplicável.

---

## 35.74 Auditoria

Eventos de Segurança poderão gerar Auditoria quando envolverem ações administrativas relevantes.

---

## 35.75 Mensagens

Mensagens apresentadas ao usuário nunca deverão revelar detalhes suficientes para facilitar ataques.

Exemplo:

"Usuário ou senha inválidos."

Nunca:

"Usuário inexistente."

# PROTEÇÃO DAS APIs

## 35.76 APIs protegidas

Toda API protegida deverá exigir autenticação válida.

Nenhuma API interna deverá confiar exclusivamente em parâmetros enviados pelo cliente.

---

## 35.77 Validação das requisições

Todas as requisições deverão validar:

- autenticação;
- autorização;
- Loja;
- formato dos dados;
- integridade dos parâmetros.

---

## 35.78 Métodos HTTP

Os métodos HTTP deverão respeitar sua finalidade.

GET:
Somente leitura.

POST:
Criação de recursos.

PUT/PATCH:
Atualização.

DELETE:
Remoção lógica ou física conforme regra do módulo.

Operações de escrita não poderão utilizar GET.

---

## 35.79 Versionamento

As APIs deverão suportar versionamento.

Exemplo:

/api/v1/

A evolução da API não deverá quebrar integrações existentes sem estratégia de migração.

---

## 35.80 CORS

A configuração de CORS deverá permitir somente origens autorizadas.

Não utilizar curingas (`*`) em ambientes de produção para APIs autenticadas.

---

# CRIPTOGRAFIA

## 35.81 Senhas

Senhas nunca deverão ser armazenadas em texto puro.

Deverão utilizar algoritmo de hash seguro e apropriado.

---

## 35.82 Dados sensíveis

Sempre que necessário armazenar informações sensíveis, deverão ser utilizados mecanismos de criptografia compatíveis com as boas práticas atuais.

---

## 35.83 Chaves criptográficas

Chaves utilizadas para criptografia nunca deverão ficar gravadas diretamente no código-fonte.

Devem ser obtidas por mecanismo seguro de configuração.

---

## 35.84 Comparações

Comparações de dados sensíveis deverão utilizar métodos seguros quando aplicável, evitando vulnerabilidades de tempo de resposta.

---

# CONFIGURAÇÃO E SEGREDOS

## 35.85 Variáveis de ambiente

Credenciais e configurações sensíveis deverão ser fornecidas por variáveis de ambiente ou serviço equivalente.

---

## 35.86 Segredos proibidos no código

É proibido manter no código-fonte:

- senha do banco;
- chave JWT;
- senha SMTP;
- token de integração;
- credenciais de APIs;
- certificados privados.

---

## 35.87 Frontend

Nenhum segredo deverá ser distribuído para o frontend.

O navegador somente receberá informações estritamente necessárias para a operação.

---

## 35.88 Ambientes

Os ambientes de:

- Desenvolvimento;
- Homologação;
- Produção;

deverão possuir configurações independentes.

Credenciais nunca deverão ser compartilhadas entre ambientes.

---

# DEPENDÊNCIAS

## 35.89 Bibliotecas

Somente bibliotecas mantidas e confiáveis deverão ser utilizadas.

---

## 35.90 Atualizações

Atualizações de segurança deverão ser avaliadas periodicamente.

Sempre que possível deverão ser aplicadas após validação em ambiente de testes.

---

## 35.91 Dependências abandonadas

Dependências sem manutenção ou conhecidamente vulneráveis deverão ser substituídas quando houver alternativa compatível.

---

# BACKUP E RECUPERAÇÃO

## 35.92 Backups

Backups deverão seguir política própria da infraestrutura.

Os backups não substituem os mecanismos de Auditoria nem os históricos do sistema.

---

## 35.93 Restauração

Processos de restauração deverão ser testados periodicamente.

Uma política de backup sem possibilidade de restauração não atende aos requisitos de segurança.

---

# DISPONIBILIDADE

## 35.94 Tratamento de falhas

Falhas inesperadas deverão retornar mensagens controladas ao usuário.

Nunca exibir detalhes internos da aplicação.

---

## 35.95 Continuidade

Sempre que possível, falhas isoladas não deverão comprometer módulos independentes.

---

## 35.96 Degradação controlada

Quando um serviço secundário estiver indisponível, o sistema poderá continuar operando parcialmente, desde que a integridade das operações principais seja preservada.

---

# TESTES DE SEGURANÇA

## 35.97 Testes obrigatórios

O sistema deverá possuir testes para:

- autenticação;
- autorização;
- isolamento por Loja;
- permissões;
- uploads;
- downloads;
- SQL Injection;
- XSS;
- CSRF;
- concorrência;
- idempotência;
- sessões;
- rate limit.

---

## 35.98 Testes de isolamento

Os testes deverão confirmar que nenhuma Loja consegue acessar dados pertencentes a outra Loja.

---

## 35.99 Testes de autorização

Os testes deverão validar que esconder elementos da interface não concede acesso às operações protegidas.

---

## 35.100 Testes de SQL Injection

Os testes deverão confirmar que entradas maliciosas não alteram a estrutura das consultas.

---

## 35.101 Testes de XSS

Os testes deverão confirmar que HTML e JavaScript enviados por usuários são tratados como texto.

---

## 35.102 Testes de CSRF

Quando a autenticação utilizar Cookies, deverão existir testes específicos para validação da proteção CSRF.

---

## 35.103 Testes de concorrência

Os testes deverão validar operações simultâneas em:

- Venda;
- Estoque;
- Recebimentos;
- Pagamentos;
- Inventário.

---

## 35.104 Testes de Idempotência

Os testes deverão confirmar que múltiplas requisições idênticas produzem apenas um efeito persistente.

---

## 35.105 Testes de recuperação

Os testes deverão validar comportamento após:

- queda de conexão;
- timeout;
- rollback;
- reinício do serviço.

---

# REGRAS GERAIS

## 35.106 Regras gerais da Segurança Consolidada

O sistema deverá:

- considerar o backend como autoridade;
- nunca confiar em dados enviados pelo frontend;
- validar autenticação em operações protegidas;
- validar autorização em todas as operações;
- validar perfil pelo backend;
- validar Loja pelo backend;
- impedir acesso entre Lojas;
- validar todos os dados recebidos;
- validar tipos, formatos e limites;
- recalcular valores monetários;
- recalcular Estoque antes da confirmação;
- utilizar HTTPS em produção;
- proteger Cookies;
- utilizar proteção CSRF quando aplicável;
- validar uploads;
- validar downloads;
- impedir URLs públicas previsíveis para arquivos protegidos;
- utilizar consultas parametrizadas;
- impedir SQL Injection;
- impedir XSS;
- tratar HTML como texto;
- impedir execução de JavaScript enviado por usuários;
- proteger operações críticas com idempotência;
- utilizar transações atômicas;
- executar rollback em falhas;
- tratar concorrência adequadamente;
- utilizar Rate Limit quando necessário;
- utilizar cabeçalhos de segurança;
- registrar Logs de Segurança;
- nunca registrar senhas ou segredos;
- utilizar versionamento de APIs;
- restringir CORS;
- armazenar senhas com hash seguro;
- manter segredos fora do código-fonte;
- utilizar variáveis de ambiente;
- separar configurações por ambiente;
- utilizar bibliotecas confiáveis;
- manter dependências atualizadas;
- possuir política de backup;
- testar restauração;
- tratar falhas de forma segura;
- preservar disponibilidade sempre que possível;
- possuir testes abrangentes de segurança;
- manter isolamento completo entre Lojas;
- preservar a confidencialidade, integridade e disponibilidade dos dados.

## 35.107 Precedência das regras

As regras desta seção possuem caráter transversal.

Sempre que um módulo específico tratar de segurança, deverá respeitar estas regras.

Em caso de conflito, prevalecerá a regra mais restritiva.

## 35.108 Evolução da segurança

Novos mecanismos de autenticação, criptografia, proteção contra ataques ou endurecimento da infraestrutura poderão ser incorporados futuramente sem alterar as regras de negócio já estabelecidas, desde que mantenham compatibilidade funcional.

## 35.109 Revisões

Toda alteração relevante nesta seção deverá ser registrada no histórico de versões do BUSINESS_RULES.md, indicando data, versão e motivo da alteração.

## 35.110 Encerramento

A Segurança Consolidada estabelece o conjunto mínimo obrigatório de controles para todo o sistema.

Nenhum módulo poderá reduzir ou flexibilizar estas regras sem revisão formal da especificação.

# 36. PERFORMANCE E ESCALABILIDADE

## 36.1 Finalidade

A Performance e Escalabilidade estabelecem as regras obrigatórias para garantir que o sistema permaneça rápido, consistente e responsivo, independentemente do crescimento da quantidade de dados.

Estas regras aplicam-se ao backend, frontend, banco de dados e integrações.

---

## 36.2 Objetivos

Os objetivos desta seção são:

- manter baixo tempo de resposta;
- evitar desperdício de processamento;
- reduzir consumo de memória;
- reduzir consultas desnecessárias;
- permitir crescimento da base de dados;
- garantir experiência consistente ao usuário;
- facilitar futuras expansões.

---

## 36.3 Performance como requisito

Performance não deve ser tratada como otimização posterior.

Toda implementação deverá considerar desempenho desde sua concepção.

---

## 36.4 Escalabilidade

Toda implementação deverá suportar crescimento contínuo da base de dados sem necessidade de alteração das regras de negócio.

---

# PAGINAÇÃO

## 36.5 Paginação obrigatória

Toda listagem deverá utilizar paginação.

É proibido carregar todos os registros em uma única consulta.

---

## 36.6 Módulos obrigatórios

A paginação aplica-se obrigatoriamente a:

- Clientes;
- Produtos;
- Vendas;
- Recebimentos;
- Contas;
- Garantias;
- Inventários;
- Auditoria;
- Logs;
- Fornecedores;
- Entradas;
- Devoluções;
- Usuários;
- Alertas;
- demais módulos com listagens.

---

## 36.7 Quantidade padrão

A quantidade padrão deverá ser:

50 registros por página.

---

## 36.8 Quantidades permitidas

O usuário poderá selecionar:

- 25;
- 50;
- 100.

---

## 36.9 Opção "Todos"

Não deverá existir opção:

Todos.

O sistema nunca deverá carregar integralmente grandes conjuntos de dados apenas para exibição.

---

## 36.10 Mudança de página

Alterar a página não deverá perder:

- filtros;
- pesquisa;
- ordenação;
- quantidade por página.

---

## 36.11 Número da página

Quando uma página deixar de existir após filtros ou exclusões, o sistema deverá retornar automaticamente para a última página válida.

---

## 36.12 Navegação

A paginação deverá permitir:

- primeira página;
- anterior;
- próxima;
- última;
- navegação direta quando aplicável.

---

# ORDENAÇÃO

## 36.13 Ordenação padrão

Cada módulo deverá possuir ordenação inicial oficial.

---

## 36.14 Clientes

Ordenação inicial:

Nome crescente.

---

## 36.15 Produtos

Ordenação inicial:

Nome crescente.

---

## 36.16 Vendas

Ordenação inicial:

Mais recentes primeiro.

---

## 36.17 Recebimentos

Mais recentes primeiro.

---

## 36.18 Contas

Próximo vencimento ou mais recente conforme regra do módulo.

---

## 36.19 Auditoria

Mais recente primeiro.

---

## 36.20 Logs

Mais recente primeiro.

---

## 36.21 Alteração

O usuário poderá alterar a ordenação quando o módulo permitir.

---

## 36.22 Persistência

A ordenação escolhida poderá permanecer durante a Sessão.

---

# PESQUISA

## 36.23 Pesquisa dinâmica

A pesquisa deverá ocorrer automaticamente durante a digitação.

---

## 36.24 Debounce

Toda pesquisa automática deverá utilizar debounce.

Tempo padrão:

360 ms.

---

## 36.25 Objetivo

O debounce evita consultas desnecessárias ao backend enquanto o usuário ainda está digitando.

---

## 36.26 Pesquisa vazia

Campo vazio deverá retornar a listagem padrão.

---

## 36.27 Espaços

Espaços excedentes deverão ser desconsiderados na pesquisa.

---

## 36.34 Sensibilidade

Pesquisas textuais deverão ignorar diferenças entre letras maiúsculas e minúsculas.

---

## 36.29 Acentuação

Sempre que possível, pesquisas deverão ignorar diferenças de acentuação.

Exemplo:

José = Jose.

---

## 36.30 Múltiplos filtros

Pesquisa deverá funcionar em conjunto com filtros.

Nunca substituir filtros já aplicados.

---

## 36.31 Pesquisa sem resultados

Quando não houver registros, apresentar:

Nenhum registro encontrado.

---

## 36.32 Cancelamento

Ao iniciar nova pesquisa, consultas anteriores deverão ser canceladas ou ignoradas quando possível.

---

# CONSULTAS

## 36.33 Backend

Consultas deverão retornar apenas os dados necessários para a tela atual.

---

## 36.34 Colunas

Evitar selecionar colunas que não serão utilizadas.

---

## 36.35 Relações

Relacionamentos deverão ser carregados apenas quando necessários.

---

## 36.36 Consultas N+1

É proibido implementar consultas N+1 quando houver alternativa eficiente.

---

## 36.37 JOINs

JOINs deverão ser utilizados de forma criteriosa.

Relacionamentos excessivos deverão ser evitados quando puderem comprometer desempenho.

---

## 36.38 Lazy Loading

Informações pesadas deverão utilizar Lazy Loading.

Exemplos:

- anexos;
- imagens;
- documentos;
- fotos de Garantia;
- histórico detalhado.

---

## 36.39 Consulta única

Sempre que possível, informações relacionadas deverão ser obtidas em uma única consulta otimizada.

---

## 36.40 Paginação no banco

A paginação deverá ocorrer no banco de dados.

Nunca carregar todos os registros para paginar no frontend.

---

# ÍNDICES

## 36.41 Índices obrigatórios

Campos utilizados frequentemente em pesquisas deverão possuir índices apropriados.

---

## 36.42 Campos

Exemplos:

- código;
- nome;
- CPF;
- CNPJ;
- data;
- situação;
- número da Venda;
- número da Garantia.

---

## 36.43 Ordenação

Campos utilizados frequentemente para ordenação também deverão possuir índices quando necessário.

---

## 36.44 Chaves estrangeiras

Relacionamentos utilizados em consultas deverão possuir índices compatíveis.

---

## 36.45 Índices desnecessários

Não criar índices indiscriminadamente.

Cada índice possui custo de armazenamento e atualização.

---

# FRONTEND

## 36.46 Estado de carregamento

Toda consulta deverá apresentar estado visual de carregamento.

---

## 36.47 Skeleton

Sempre que apropriado, utilizar Skeleton Loading em vez de telas vazias.

---

## 36.48 Interface responsiva

A interface deverá permanecer responsiva durante consultas.

Nunca bloquear totalmente a aplicação enquanto aguarda resposta do servidor.

---

## 36.49 Clique duplo

Botões de operações críticas deverão impedir múltiplos cliques durante processamento.

---

## 36.50 Requisições antigas

Quando uma nova consulta substituir outra, respostas antigas não deverão sobrescrever os dados atuais da interface.

# CACHE

## 36.51 Objetivo do cache

O cache deverá ser utilizado para reduzir consultas repetitivas e melhorar o tempo de resposta.

Seu uso nunca poderá comprometer a consistência das informações apresentadas.

---

## 36.52 Cache permitido

É permitido utilizar cache para informações com baixa frequência de alteração.

Exemplos:

- categorias;
- marcas;
- cores;
- tamanhos;
- configurações gerais;
- parâmetros do sistema;
- tabelas auxiliares;
- listas de municípios;
- listas de estados.

---

## 36.53 Cache proibido

Não utilizar cache para informações operacionais que exigem consistência imediata.

Exemplos:

- estoque atual;
- saldo financeiro;
- recebíveis;
- parcelas;
- contas em aberto;
- permissões do usuário;
- situação da sessão.

---

## 36.54 Atualização do cache

Quando um dado armazenado em cache for alterado, o cache correspondente deverá ser invalidado imediatamente ou atualizado de forma consistente.

---

## 36.55 Tempo de vida

Cada tipo de cache deverá possuir tempo de vida compatível com sua natureza.

Não utilizar um tempo único para todos os dados.

---

## 36.56 Cache por Loja

Quando aplicável, o cache deverá respeitar o isolamento por Loja.

Nunca compartilhar dados entre Lojas por meio do cache.

---

## 36.57 Cache no navegador

O navegador poderá armazenar apenas informações que não comprometam segurança ou consistência.

Documentos protegidos e dados sensíveis não deverão permanecer em cache compartilhado.

---

# DASHBOARDS

## 36.58 Objetivo

Os Dashboards deverão apresentar informações resumidas de forma rápida.

Não deverão executar consultas excessivamente pesadas a cada acesso.

---

## 36.59 Agregações

Indicadores deverão utilizar agregações otimizadas sempre que possível.

---

## 36.60 Recalculo

O Dashboard não deverá recalcular toda a base de dados a cada carregamento da página.

---

## 36.61 Independência

Cada indicador deverá ser calculado de forma independente.

A falha de um indicador não deverá impedir a exibição dos demais.

---

## 36.62 Atualização

Ao atualizar o Dashboard, apenas os indicadores necessários deverão ser recalculados.

---

## 36.63 Consultas

Consultas do Dashboard deverão retornar apenas os valores necessários para apresentação.

---

## 36.64 Histórico

Consultas históricas muito extensas deverão utilizar agregações ou mecanismos específicos de otimização.

---

# EXPORTAÇÕES

## 36.65 Exportações imediatas

Exportações com até 10.000 registros poderão ser executadas imediatamente.

---

## 36.66 Exportações grandes

Exportações acima de 10.000 registros deverão utilizar processamento assíncrono.

---

## 36.67 Processamento

Durante o processamento deverá ser apresentada mensagem semelhante a:

Exportação em processamento...

---

## 36.68 Conclusão

Ao término do processamento, o usuário deverá ser informado que o arquivo está disponível.

---

## 36.69 Continuidade

Enquanto a exportação estiver sendo executada, o usuário deverá continuar utilizando normalmente o sistema.

---

## 36.70 Cancelamento

Quando tecnicamente possível, exportações longas poderão ser canceladas pelo usuário antes da conclusão.

---

## 36.71 Isolamento

Cada exportação deverá permanecer vinculada:

- à Loja;
- ao usuário solicitante;
- aos filtros utilizados.

---

## 36.72 Consistência

A exportação deverá utilizar um conjunto consistente de dados.

O conteúdo não deverá mudar durante a geração do mesmo arquivo.

---

# PROCESSAMENTO ASSÍNCRONO

## 36.73 Objetivo

Operações demoradas deverão utilizar processamento em segundo plano sempre que possível.

---

## 36.74 Exemplos

Podem utilizar processamento assíncrono:

- grandes exportações;
- geração de relatórios extensos;
- processamento de arquivos;
- rotinas administrativas;
- sincronizações futuras.

---

## 36.75 Jobs

Cada processamento assíncrono deverá possuir identificação própria.

---

## 36.76 Situação

Os estados mínimos são:

- aguardando;
- processando;
- concluído;
- falhou;
- cancelado.

---

## 36.77 Falhas

Falhas em um processamento assíncrono não deverão comprometer outras tarefas independentes.

---

## 36.78 Repetição

Quando apropriado, tarefas poderão ser reenviadas para processamento após correção da causa da falha.

---

# FRONTEND

## 36.79 Renderização

A interface deverá renderizar apenas os componentes necessários para a tela atual.

---

## 36.80 Componentes pesados

Componentes pesados deverão ser carregados apenas quando utilizados.

---

## 36.81 Requisições paralelas

Quando possível, consultas independentes poderão ser executadas em paralelo.

---

## 36.82 Responsividade

A interface deverá permanecer utilizável durante consultas demoradas.

---

## 36.83 Estados visuais

Toda operação deverá apresentar estados claros:

- carregando;
- concluído;
- erro;
- vazio.

---

## 36.84 Atualizações

Alterações pequenas não deverão provocar recarregamento completo da página.

---

## 36.85 Reutilização

Componentes reutilizáveis deverão evitar renderizações desnecessárias.

---

# TIMEOUT

## 36.86 Operações demoradas

Quando uma operação ultrapassar aproximadamente 36 segundos, o sistema deverá informar que o processamento continua em andamento, sempre que tecnicamente possível.

---

## 36.87 Interface

A interface nunca deverá aparentar travamento durante operações longas.

---

## 36.88 Falha

Quando ocorrer timeout, deverá existir tratamento apropriado, preservando a integridade da operação.

---

## 36.89 Recuperação

Sempre que possível, operações interrompidas deverão permitir retomada ou nova tentativa sem duplicidade.

---

# GRANDES VOLUMES

## 36.90 Crescimento

Toda implementação deverá considerar crescimento contínuo da base de dados.

---

## 36.91 Produtos

O sistema deverá suportar futuramente mais de 1.000.000 de produtos.

---

## 36.92 Clientes

O sistema deverá suportar futuramente mais de 1.000.000 de clientes.

---

## 36.93 Vendas

O sistema deverá suportar milhões de vendas sem alteração das regras de negócio.

---

## 36.94 Financeiro

O sistema deverá suportar milhões de movimentações financeiras.

---

## 36.95 Auditoria

A Auditoria deverá continuar performática mesmo com grande volume de registros.

---

## 36.96 Logs

Os Logs deverão utilizar paginação e filtros eficientes.

---

## 36.97 Índices futuros

Novos módulos deverão seguir os mesmos critérios de indexação estabelecidos nesta seção.

---

## 36.98 Escalabilidade horizontal

A arquitetura deverá permitir futura evolução para ambientes distribuídos sem alterar as regras de negócio.

---

## 36.99 Escalabilidade vertical

O sistema deverá aproveitar adequadamente aumentos de recursos computacionais quando disponíveis.

---

## 36.100 Independência

O crescimento de um módulo não deverá degradar desnecessariamente o desempenho dos demais módulos.

# MONITORAMENTO DE PERFORMANCE

## 36.101 Objetivo

O sistema deverá permitir monitoramento contínuo do desempenho das principais operações.

O monitoramento deverá auxiliar na identificação preventiva de gargalos antes que impactem a operação da Loja.

---

## 36.102 Indicadores

Sempre que possível deverão ser acompanhados indicadores como:

- tempo médio de resposta;
- tempo máximo de resposta;
- quantidade de consultas;
- quantidade de operações por módulo;
- utilização de processamento;
- utilização de memória;
- tempo de geração de documentos;
- tempo de exportações.

---

## 36.103 Consultas lentas

Consultas que apresentarem desempenho significativamente inferior ao esperado deverão ser identificadas para futura otimização.

---

## 36.104 Métricas

As métricas de desempenho deverão possuir finalidade exclusivamente técnica.

Nunca substituirão os indicadores de negócio apresentados nos Dashboards.

---

## 36.105 Histórico

O histórico de desempenho poderá ser utilizado para identificar degradações ao longo do tempo.

---

# TESTES DE PERFORMANCE

## 36.106 Testes obrigatórios

O sistema deverá possuir testes específicos para:

- paginação;
- pesquisa;
- ordenação;
- filtros;
- Dashboard;
- exportações;
- consultas;
- processamento assíncrono.

---

## 36.107 Testes de carga

Os testes deverão simular múltiplos usuários executando operações simultaneamente.

O objetivo é validar estabilidade e tempo de resposta.

---

## 36.108 Testes de estresse

Sempre que possível deverão existir testes de estresse para identificar o comportamento do sistema próximo aos seus limites operacionais.

---

## 36.109 Testes de grandes volumes

Os testes deverão validar o funcionamento com bases contendo grandes quantidades de registros.

Exemplos:

- mais de 1.000.000 de Produtos;
- mais de 1.000.000 de Clientes;
- milhões de Vendas;
- milhões de movimentações financeiras;
- milhões de registros de Auditoria.

---

## 36.110 Testes de concorrência

Os testes deverão validar operações simultâneas envolvendo:

- Vendas;
- Estoque;
- Recebimentos;
- Pagamentos;
- Inventários.

O desempenho não poderá comprometer a integridade das informações.

---

## 36.111 Testes de exportação

As exportações deverão ser testadas tanto para:

- processamento imediato;

quanto para:

- processamento assíncrono.

---

## 36.112 Testes de recuperação

Os testes deverão validar o comportamento do sistema após:

- timeout;
- falha de comunicação;
- interrupção do processamento;
- reinício do serviço.

---

# BENCHMARK

## 36.113 Comparação de desempenho

Sempre que alterações significativas forem realizadas em consultas críticas, deverá ser possível comparar o desempenho antes e depois da alteração.

---

## 36.114 Regressão

Uma melhoria funcional não deverá provocar degradação significativa de desempenho sem justificativa técnica.

---

## 36.115 Otimizações

Toda otimização deverá preservar:

- regras de negócio;
- consistência;
- integridade dos dados;
- segurança.

Nunca otimizar sacrificando a confiabilidade das operações.

---

# EVOLUÇÃO

## 36.116 Novos módulos

Todo novo módulo deverá seguir integralmente as regras desta seção.

---

## 36.117 Novas consultas

Toda nova consulta deverá considerar:

- paginação;
- índices;
- filtros;
- ordenação;
- escalabilidade.

---

## 36.118 Crescimento futuro

As decisões arquiteturais deverão considerar crescimento contínuo da utilização do sistema ao longo dos anos.

---

## 36.119 Compatibilidade

Melhorias de desempenho não deverão alterar o comportamento funcional previamente aprovado nas regras de negócio.

---

# REGRAS GERAIS

## 36.120 Regras gerais de Performance e Escalabilidade

O sistema deverá:

- tratar desempenho como requisito obrigatório;
- considerar escalabilidade desde a implementação inicial;
- utilizar paginação obrigatória;
- utilizar 50 registros por página como padrão;
- permitir 25, 50 e 100 registros por página;
- não permitir opção "Todos";
- preservar filtros durante a paginação;
- preservar ordenação durante a navegação;
- utilizar ordenações padrão por módulo;
- utilizar pesquisa automática;
- utilizar debounce de aproximadamente 360 ms;
- permitir combinação entre pesquisa e filtros;
- cancelar consultas obsoletas;
- retornar apenas os dados necessários para cada tela;
- evitar consultas N+1;
- utilizar Lazy Loading para conteúdos pesados;
- realizar paginação no banco de dados;
- criar índices apropriados;
- evitar índices desnecessários;
- apresentar estados de carregamento;
- impedir múltiplos cliques em operações críticas;
- ignorar respostas antigas;
- utilizar cache apenas quando não comprometer consistência;
- nunca utilizar cache para Estoque, saldos, recebíveis ou permissões;
- invalidar cache quando necessário;
- isolar cache por Loja;
- otimizar Dashboards;
- utilizar agregações eficientes;
- evitar recálculo completo dos Dashboards;
- executar exportações até 10.000 registros imediatamente;
- utilizar processamento assíncrono acima desse limite;
- permitir continuidade de uso durante exportações;
- preservar consistência das exportações;
- utilizar processamento em segundo plano para tarefas demoradas;
- controlar estados dos jobs assíncronos;
- manter a interface responsiva;
- evitar renderizações desnecessárias;
- executar consultas paralelas quando apropriado;
- informar operações superiores a aproximadamente 36 segundos;
- tratar timeout adequadamente;
- permitir crescimento para milhões de registros;
- manter desempenho da Auditoria;
- manter desempenho dos Logs;
- permitir evolução para arquiteturas distribuídas;
- monitorar indicadores de desempenho;
- identificar consultas lentas;
- realizar testes de carga;
- realizar testes de estresse;
- validar grandes volumes de dados;
- validar concorrência;
- validar exportações;
- validar recuperação após falhas;
- preservar regras de negócio durante otimizações;
- aplicar estas regras a todos os módulos futuros.

## 36.121 Precedência

As regras desta seção deverão ser observadas por todos os módulos do sistema.

Quando houver conflito entre uma implementação e estas regras, deverá prevalecer a solução que preserve simultaneamente:

- integridade;
- segurança;
- consistência;
- desempenho.

## 36.122 Revisões

Alterações nesta seção deverão ser registradas no histórico de versões do BUSINESS_RULES.md.

## 36.123 Encerramento

A Seção Performance e Escalabilidade estabelece os requisitos mínimos obrigatórios para garantir que o sistema permaneça eficiente, estável e preparado para crescimento contínuo, independentemente do volume de dados ou da quantidade de usuários simultâneos.

# 37. APIs E INTEGRAÇÕES FUTURAS

## 37.1 Finalidade

Esta seção estabelece as regras para APIs internas, futuras APIs públicas e integrações com sistemas externos.

As regras desta seção deverão garantir:

- segurança;
- compatibilidade;
- escalabilidade;
- versionamento;
- estabilidade;
- interoperabilidade.

---

## 37.2 Objetivos

As APIs deverão permitir integração futura sem alterar as regras de negócio já estabelecidas.

Toda integração deverá respeitar as mesmas regras aplicadas à interface oficial do sistema.

---

## 37.3 Fonte autoritativa

As APIs deverão utilizar exatamente as mesmas regras de negócio do sistema.

Não poderá existir lógica diferente apenas porque a operação ocorreu via API.

---

## 37.4 Primeira versão

A primeira versão do sistema não disponibilizará API pública.

As APIs existentes serão utilizadas exclusivamente pelos componentes internos da aplicação.

---

## 37.5 Evolução

A arquitetura deverá permitir publicação futura de APIs externas sem necessidade de reescrever os módulos internos.

---

# ARQUITETURA

## 37.6 Arquitetura única

Frontend, aplicativo futuro e integrações deverão consumir as mesmas regras de negócio oficiais.

A lógica operacional deverá permanecer centralizada no backend.

---

## 37.7 Independência

A implementação de novas interfaces não deverá alterar o funcionamento dos módulos existentes.

---

## 37.8 Serviços

Sempre que possível, operações deverão ser organizadas em serviços reutilizáveis.

Evitar duplicação de regras entre diferentes APIs.

---

## 37.9 Consistência

Toda operação realizada por API deverá produzir exatamente o mesmo resultado que a operação equivalente realizada pela interface gráfica.

---

## 37.10 Evolução incremental

Novas funcionalidades deverão ser adicionadas sem comprometer compatibilidade das integrações existentes.

---

# VERSIONAMENTO

## 37.11 Versionamento obrigatório

Toda API deverá nascer versionada.

---

## 37.12 Prefixo

O padrão oficial será:

/api/v1/

---

## 37.13 Novas versões

Mudanças incompatíveis deverão gerar nova versão da API.

Exemplo:

/api/v2/

---

## 37.14 Compatibilidade

A criação de nova versão não deverá interromper imediatamente a versão anterior.

O período de convivência será definido conforme a política oficial de evolução.

---

## 37.15 Descontinuação

Versões antigas somente poderão ser descontinuadas após comunicação e prazo adequado para migração.

---

# FORMATO

## 37.16 Formato oficial

As APIs deverão utilizar exclusivamente JSON.

---

## 37.17 Codificação

A codificação oficial deverá ser UTF-8.

---

## 37.18 Datas

Datas deverão utilizar formato padronizado conforme regras oficiais da aplicação.

Internamente poderão utilizar ISO-8601 quando apropriado.

---

## 37.19 Valores monetários

Valores monetários deverão respeitar a política oficial de precisão definida pelo sistema.

---

## 37.20 Booleanos

Valores booleanos deverão utilizar representação nativa.

Nunca utilizar textos como:

"SIM"

"NÃO"

para representar booleanos.

---

# AUTENTICAÇÃO

## 37.21 Autenticação obrigatória

Toda API protegida deverá exigir autenticação válida.

---

## 37.22 Backend

Toda autenticação deverá ser validada exclusivamente pelo backend.

---

## 37.23 Usuário

O usuário autenticado deverá ser obtido da Sessão ou do mecanismo oficial de autenticação.

Nunca do corpo da requisição.

---

## 37.24 Perfil

O Perfil deverá ser obtido da autenticação oficial.

Jamais confiar em:

perfil=Administrador

enviado pelo cliente.

---

## 37.25 Loja

A Loja autenticada deverá ser obtida exclusivamente da autenticação.

Nunca confiar em:

storeId

companyId

tenantId

enviados na requisição.

---

# AUTORIZAÇÃO

## 37.26 Permissões

Cada endpoint deverá validar sua própria autorização.

---

## 37.27 Independência

Permissão para consultar não implica permissão para alterar.

---

## 37.28 Operações

Cada operação deverá validar:

- autenticação;
- autorização;
- Loja;
- regras de negócio.

---

## 37.29 Backend

Ocultar botões na interface nunca substituirá validações da API.

---

## 37.30 Sessão

Sessão expirada deverá impedir imediatamente novas chamadas protegidas.

---

# ISOLAMENTO ENTRE LOJAS

## 37.31 Isolamento obrigatório

Toda API deverá respeitar integralmente o isolamento entre Lojas.

---

## 37.32 Consultas

Consultas deverão retornar apenas registros pertencentes à Loja autenticada.

---

## 37.33 Escritas

Toda gravação deverá registrar automaticamente a Loja correspondente.

---

## 37.34 Alteração manual

Modificar parâmetros relacionados à Loja nunca deverá permitir acesso a dados de outra empresa.

---

## 37.35 Relacionamentos

Relacionamentos entre entidades deverão sempre respeitar o mesmo isolamento.

---

# ENDPOINTS

## 37.36 Organização

Os endpoints deverão possuir organização consistente por módulo.

Exemplos:

/clientes

/produtos

/vendas

/garantias

/recebimentos

---

## 37.37 Nomenclatura

Utilizar nomes claros, em minúsculas e sem espaços.

---

## 37.38 Recursos

Cada endpoint deverá representar um recurso específico.

Evitar endpoints genéricos que executem múltiplas funções distintas.

---

## 37.39 Métodos HTTP

Os métodos HTTP deverão respeitar sua finalidade:

GET:
consulta.

POST:
criação.

PUT/PATCH:
atualização.

DELETE:
remoção conforme regras do módulo.

---

## 37.40 GET

Requisições GET nunca deverão alterar dados persistidos.

# PAGINAÇÃO

## 37.41 Paginação obrigatória

Toda API que retornar listas deverá utilizar paginação.

Nenhum endpoint poderá retornar integralmente grandes volumes de registros.

---

## 37.42 Quantidade padrão

A quantidade padrão deverá ser:

50 registros.

---

## 37.43 Quantidades permitidas

A API poderá aceitar:

- 25
- 50
- 100

como quantidade por página.

---

## 37.44 Limite máximo

Mesmo que o consumidor informe quantidade superior ao limite permitido, a API deverá respeitar o limite máximo definido pelo sistema.

---

## 37.45 Informações da paginação

As respostas paginadas deverão informar, no mínimo:

- página atual;
- quantidade por página;
- total de registros;
- total de páginas;
- quantidade retornada.

---

## 37.46 Página inexistente

Quando uma página não existir, a API deverá retornar resultado vazio ou resposta apropriada, sem erro interno.

---

# ORDENAÇÃO

## 37.47 Ordenação

As APIs poderão permitir ordenação apenas por campos oficialmente autorizados.

---

## 37.48 Campos

Não permitir ordenação por qualquer coluna enviada pelo consumidor.

---

## 37.49 Direção

Permitir:

ASC

DESC

---

## 37.50 Valor inválido

Ordenações inválidas deverão utilizar a ordenação padrão ou retornar erro de validação conforme a política da API.

---

# FILTROS

## 37.51 Campos permitidos

Filtros deverão existir apenas para campos oficialmente definidos.

---

## 37.52 Segurança

Filtros nunca deverão permitir construção dinâmica de consultas SQL.

---

## 37.53 Combinação

Filtros poderão ser utilizados em conjunto.

---

## 37.54 Pesquisa

Quando existir pesquisa textual, ela deverá seguir as mesmas regras da interface gráfica.

---

## 37.55 Dados inexistentes

Filtros sem resultado deverão retornar lista vazia.

Nunca erro interno.

---

# RESPOSTAS

## 37.56 Estrutura

As respostas deverão possuir estrutura consistente.

---

## 37.57 Objetivo

Uma mesma operação deverá retornar sempre o mesmo formato estrutural.

---

## 37.58 Dados

Retornar apenas os campos necessários para a operação solicitada.

---

## 37.59 Dados protegidos

Nunca retornar:

- senha;
- hash;
- token;
- segredo;
- permissões internas desnecessárias.

---

## 37.60 Valores históricos

Quando a operação exigir dados históricos, a API deverá utilizar exatamente os mesmos snapshots utilizados pela interface oficial.

---

# CÓDIGOS HTTP

## 37.61 Sucesso

Operações bem-sucedidas deverão utilizar códigos HTTP compatíveis.

---

## 37.62 Erros de validação

Validações deverão retornar código apropriado para erro do cliente.

---

## 37.63 Não autenticado

Requisições sem autenticação deverão retornar resposta apropriada para autenticação obrigatória.

---

## 37.64 Sem permissão

Usuários autenticados sem autorização deverão receber resposta específica de acesso negado.

---

## 37.65 Erro interno

Falhas inesperadas deverão retornar erro interno genérico.

Nunca expor detalhes técnicos.

---

# ERROS

## 37.66 Mensagem

Mensagens deverão ser claras e seguras.

---

## 37.67 SQL

Nunca retornar:

- SQL;
- Stack Trace;
- caminhos internos;
- variáveis de ambiente;
- detalhes da infraestrutura.

---

## 37.68 Código interno

Erros relevantes poderão possuir código interno de referência.

---

## 37.69 Consistência

Erros equivalentes deverão utilizar estrutura consistente.

---

## 37.70 Logs

Erros relevantes deverão seguir as regras da Seção de Logs Técnicos.

---

# IDEMPOTÊNCIA

## 37.71 Operações críticas

As APIs deverão aceitar mecanismo oficial de idempotência nas operações críticas.

---

## 37.72 Operações

Exemplos:

- Venda;
- Recebimento;
- Pagamento;
- Estorno;
- Entrada;
- Inventário.

---

## 37.73 Repetição

Repetir a mesma requisição idempotente não poderá produzir efeitos duplicados.

---

## 37.74 Chave

A chave de idempotência deverá possuir validade limitada e vinculação ao contexto da operação.

---

## 37.75 Consistência

A resposta para requisições idempotentes repetidas deverá permanecer consistente com a primeira execução válida.

---

# RATE LIMIT

## 37.76 Objetivo

As APIs deverão possuir limitação de requisições para evitar uso abusivo.

---

## 37.77 Aplicação

O Rate Limit deverá considerar:

- usuário;
- autenticação;
- IP, quando aplicável;
- contexto operacional.

---

## 37.78 Excedente

Quando o limite for excedido, a API deverá retornar resposta apropriada sem comprometer a estabilidade do sistema.

---

## 37.79 Independência

O consumo excessivo de uma integração não deverá prejudicar os demais usuários do sistema.

---

## 37.80 Evolução

Os limites poderão ser ajustados futuramente sem alterar as regras de negócio.

---

# SEGURANÇA DAS APIs

## 37.81 Backend

Toda validação crítica deverá ocorrer exclusivamente no backend.

---

## 37.82 Dados recebidos

Todo dado recebido deverá ser tratado como potencialmente inválido.

---

## 37.83 Validação

As APIs deverão validar:

- tipos;
- formatos;
- obrigatoriedade;
- limites;
- integridade.

---

## 37.84 Isolamento

Nenhuma API poderá permitir acesso entre Lojas.

---

## 37.85 Sessão

Sessões expiradas deverão impedir imediatamente novas operações protegidas.

---

# PERFORMANCE DAS APIs

## 37.86 Paginação

Grandes conjuntos de dados deverão utilizar paginação obrigatória.

---

## 37.87 Consultas

As APIs deverão retornar apenas os dados necessários para cada operação.

---

## 37.88 Consultas N+1

Evitar consultas N+1 em endpoints com relacionamentos.

---

## 37.89 Índices

Consultas frequentes deverão utilizar índices compatíveis.

---

## 37.90 Tempo de resposta

As APIs deverão manter tempo de resposta compatível com a operação executada, preservando sempre a integridade das informações.

# WEBHOOKS

## 37.91 Arquitetura preparada

Embora a primeira versão do sistema não implemente Webhooks, toda a arquitetura deverá permitir sua inclusão futura sem necessidade de alterações estruturais relevantes.

---

## 37.92 Eventos

Os Webhooks futuros poderão representar eventos como:

- Venda concluída;
- Venda cancelada;
- Cliente cadastrado;
- Cliente atualizado;
- Produto alterado;
- Produto com estoque baixo;
- Recebimento realizado;
- Conta paga;
- Garantia aberta;
- Garantia encerrada;
- Inventário finalizado;
- Entrada de Produtos;
- Devolução ao Fornecedor.

---

## 37.93 Segurança

Toda entrega de Webhook deverá possuir mecanismo oficial de autenticação e validação de integridade.

---

## 37.94 Reenvio

Quando um Webhook não puder ser entregue, deverá existir mecanismo oficial de nova tentativa.

---

## 37.95 Idempotência

Eventos repetidos não deverão provocar duplicidade nas integrações consumidoras.

Sempre que possível os eventos deverão possuir identificador único.

---

# INTEGRAÇÕES FUTURAS

## 37.96 Princípio

Toda integração deverá utilizar exclusivamente as APIs oficiais.

É proibido acessar diretamente o banco de dados da aplicação.

---

## 37.97 ERP

A arquitetura deverá permitir futura integração com sistemas ERP.

---

## 37.98 E-commerce

A arquitetura deverá permitir futura integração com plataformas de comércio eletrônico.

---

## 37.99 Marketplace

O sistema deverá permitir futura integração com marketplaces.

---

## 37.100 Aplicativos

A arquitetura deverá permitir futura integração com aplicativos móveis oficiais.

---

## 37.101 Business Intelligence

O sistema deverá permitir futura integração com ferramentas de Business Intelligence (BI).

---

## 37.102 Gateways de pagamento

A arquitetura deverá permitir futura integração com gateways de pagamento.

---

## 37.103 Serviços fiscais

A arquitetura deverá permitir futura integração com serviços fiscais quando aplicável.

---

## 37.104 Evolução

Novas integrações não deverão alterar as regras de negócio existentes.

Toda integração deverá respeitar integralmente o comportamento oficial do sistema.

---

# DOCUMENTAÇÃO

## 37.105 Documentação oficial

Quando existir API pública, deverá existir documentação oficial.

---

## 37.106 OpenAPI

O padrão recomendado para documentação será OpenAPI.

---

## 37.107 Swagger

Sempre que possível deverá existir interface Swagger para consulta e testes das APIs públicas.

---

## 37.108 Atualização

A documentação deverá permanecer sincronizada com a implementação oficial.

Documentação desatualizada deverá ser tratada como defeito.

---

## 37.109 Exemplos

Sempre que possível, a documentação deverá apresentar exemplos de:

- requisição;
- resposta;
- erros;
- autenticação;
- paginação;
- filtros.

---

# COMPATIBILIDADE

## 37.110 Compatibilidade

Novas versões da API não deverão quebrar integrações existentes sem política oficial de migração.

---

## 37.111 Convivência

Versões diferentes poderão coexistir durante período de transição.

---

## 37.112 Descontinuação

A descontinuação de versões deverá ocorrer somente após comunicação oficial e prazo adequado.

---

## 37.113 Evolução incremental

Novas funcionalidades deverão ser adicionadas preferencialmente de forma compatível com versões existentes.

---

## 37.114 Alterações incompatíveis

Mudanças incompatíveis deverão gerar nova versão da API.

Nunca alterar silenciosamente o comportamento de uma versão já publicada.

---

# TESTES

## 37.115 Testes obrigatórios

As APIs deverão possuir testes para:

- autenticação;
- autorização;
- isolamento por Loja;
- paginação;
- ordenação;
- filtros;
- respostas;
- erros;
- idempotência;
- rate limit;
- desempenho.

---

## 37.116 Testes de isolamento

Os testes deverão confirmar que nenhuma Loja consegue acessar dados pertencentes a outra.

---

## 37.117 Testes de autorização

Os testes deverão validar que cada endpoint respeita corretamente as permissões definidas.

---

## 37.118 Testes de idempotência

Os testes deverão confirmar que múltiplas requisições idênticas produzem apenas um efeito persistente.

---

## 37.119 Testes de desempenho

Os testes deverão validar o comportamento das APIs com grandes volumes de dados e múltiplas requisições simultâneas.

---

## 37.120 Testes de compatibilidade

Sempre que nova versão da API for criada, deverão existir testes garantindo que versões anteriores continuem funcionando conforme especificado.

---

# REGRAS GERAIS

## 37.121 Regras gerais de APIs e Integrações Futuras

O sistema deverá:

- possuir arquitetura preparada para APIs públicas;
- utilizar backend como fonte autoritativa;
- centralizar regras de negócio;
- utilizar versionamento obrigatório;
- utilizar prefixo `/api/v1/`;
- utilizar exclusivamente JSON UTF-8;
- exigir autenticação para APIs protegidas;
- validar autorização em todos os endpoints;
- validar Loja exclusivamente pelo backend;
- respeitar isolamento completo entre Lojas;
- organizar endpoints por recursos;
- utilizar corretamente os métodos HTTP;
- impedir operações de escrita via GET;
- utilizar paginação obrigatória;
- limitar quantidade máxima de registros por resposta;
- permitir apenas ordenações autorizadas;
- permitir apenas filtros autorizados;
- retornar apenas os dados necessários;
- nunca retornar senhas, tokens ou segredos;
- utilizar códigos HTTP apropriados;
- retornar mensagens de erro seguras;
- nunca expor SQL ou Stack Trace;
- permitir idempotência em operações críticas;
- utilizar rate limit;
- validar todos os dados recebidos;
- tratar requisições como potencialmente inválidas;
- otimizar consultas;
- evitar consultas N+1;
- preparar arquitetura para Webhooks;
- preparar integração com ERP;
- preparar integração com E-commerce;
- preparar integração com Marketplace;
- preparar integração com aplicativos móveis;
- preparar integração com BI;
- preparar integração com gateways de pagamento;
- preparar integração com serviços fiscais;
- utilizar documentação OpenAPI;
- disponibilizar Swagger quando houver API pública;
- manter documentação atualizada;
- preservar compatibilidade entre versões;
- permitir coexistência de versões;
- realizar testes completos de APIs;
- aplicar estas regras a todas as integrações futuras.

## 37.122 Precedência

As regras desta seção deverão ser aplicadas a toda comunicação entre sistemas.

Sempre que houver conflito entre implementação e especificação, deverá prevalecer a solução que preserve:

- segurança;
- compatibilidade;
- consistência;
- integridade;
- escalabilidade.

## 37.123 Revisões

Toda alteração nesta seção deverá ser registrada no histórico de versões do BUSINESS_RULES.md.

## 37.124 Encerramento

A Seção APIs e Integrações Futuras estabelece o padrão oficial para comunicação entre o sistema e aplicações externas, garantindo evolução tecnológica sem comprometer a estabilidade, a segurança e as regras de negócio.

# 38. MIGRAÇÕES E VERSIONAMENTO DO BANCO DE DADOS

## 38.1 Finalidade

Esta seção estabelece as regras obrigatórias para evolução da estrutura do banco de dados, garantindo compatibilidade, integridade, rastreabilidade e segurança durante todo o ciclo de vida do sistema.

Nenhuma alteração estrutural deverá ocorrer fora das regras desta seção.

---

## 38.2 Objetivos

As Migrations deverão garantir:

- evolução controlada do banco;
- preservação dos dados;
- rastreabilidade;
- repetibilidade;
- compatibilidade entre versões;
- facilidade de implantação;
- facilidade de manutenção.

---

## 38.3 Banco como patrimônio

Os dados armazenados constituem patrimônio da Loja.

Nenhuma Migration poderá colocar em risco a integridade dessas informações.

---

## 38.4 Fonte oficial

Toda alteração estrutural deverá ocorrer exclusivamente através de Migration oficial.

É proibido alterar manualmente a estrutura do banco em ambientes oficiais.

---

## 38.5 Escopo

As regras desta seção aplicam-se a:

- tabelas;
- colunas;
- índices;
- chaves;
- relacionamentos;
- constraints;
- views;
- triggers;
- funções;
- procedures;
- demais objetos estruturais do banco.

---

# MIGRATIONS

## 38.6 Migration obrigatória

Toda alteração estrutural deverá possuir Migration correspondente.

---

## 38.7 Alterações permitidas

As Migrations poderão:

- criar tabelas;
- alterar tabelas;
- adicionar colunas;
- alterar colunas;
- criar índices;
- remover índices;
- criar constraints;
- alterar constraints;
- criar relacionamentos;
- remover relacionamentos;
- criar views;
- alterar views.

---

## 38.8 Alterações proibidas

Não será permitido alterar diretamente o banco em produção sem Migration oficial.

---

## 38.9 Repositório

Todas as Migrations deverão permanecer versionadas juntamente com o código-fonte da aplicação.

---

## 38.10 Histórico

O histórico de Migrations nunca deverá ser apagado.

Mesmo Migrations antigas deverão permanecer registradas.

---

# VERSIONAMENTO

## 38.11 Identificação

Cada Migration deverá possuir identificação única.

---

## 38.12 Informações mínimas

Cada Migration deverá possuir:

- identificador;
- data;
- descrição;
- ordem de execução.

Autor poderá ser registrado quando aplicável.

---

## 38.13 Descrição

A descrição deverá informar claramente o objetivo da alteração estrutural.

Exemplo:

Adicionar índice em Produtos.

---

## 38.14 Ordem

As Migrations deverão ser executadas exatamente na ordem oficial definida pelo projeto.

---

## 38.15 Sequência

Não deverá existir execução fora da sequência.

---

## 38.16 Registro

O sistema deverá manter registro das Migrations executadas.

---

## 38.17 Repetição

Uma Migration já executada nunca deverá ser executada novamente.

---

## 38.18 Idempotência

O mecanismo de controle deverá impedir execução duplicada da mesma Migration.

---

## 38.19 Integridade

A ordem das Migrations deverá permanecer consistente em todos os ambientes.

---

## 38.20 Compatibilidade

Cada nova Migration deverá considerar a estrutura existente antes de aplicar alterações.

---

# EXECUÇÃO

## 38.21 Processo

As Migrations deverão ser executadas automaticamente pelo mecanismo oficial da aplicação.

---

## 38.22 Execução manual

Não executar comandos SQL manuais em produção para substituir Migrations.

---

## 38.23 Ambiente

Antes da execução deverá ser identificado corretamente o ambiente:

- Desenvolvimento;
- Homologação;
- Produção.

---

## 38.24 Consistência

Durante a execução deverá ser preservada a consistência estrutural do banco.

---

## 38.25 Atomicidade

Sempre que suportado pelo banco de dados, a execução da Migration deverá ocorrer dentro de transação.

---

## 38.26 Rollback automático

Quando ocorrer falha durante uma Migration transacional, deverá ocorrer rollback completo.

---

## 38.27 Continuação

Uma Migration com falha nunca deverá permitir continuidade automática das próximas Migrations.

---

## 38.28 Interrupção

Ao ocorrer erro estrutural, o processo deverá ser interrompido imediatamente.

---

## 38.29 Diagnóstico

Toda falha deverá gerar Log Técnico conforme regras da Seção 28.

---

## 38.30 Auditoria

Migrations não geram Auditoria de negócio.

Geram apenas registros técnicos.

---

# ROLLBACK

## 38.31 Objetivo

Sempre que tecnicamente possível, cada Migration deverá possuir Rollback correspondente.

---

## 38.32 Rollback seguro

O Rollback deverá restaurar a estrutura anterior preservando a integridade dos dados.

---

## 38.33 Limitações

Quando uma Migration não puder possuir Rollback seguro, essa limitação deverá estar documentada.

---

## 38.34 Exclusões

Migrations destrutivas deverão ser evitadas.

Sempre que possível deverá existir estratégia intermediária de transição.

---

## 38.35 Recuperação

Após Rollback bem-sucedido, o banco deverá permanecer consistente e utilizável pela versão correspondente da aplicação.

---

# ALTERAÇÕES ESTRUTURAIS

## 38.36 Novas tabelas

Toda nova tabela deverá ser criada exclusivamente por Migration.

---

## 38.37 Novas colunas

Toda nova coluna deverá ser criada por Migration.

---

## 38.38 Novos índices

Todo novo índice deverá possuir Migration correspondente.

---

## 38.39 Novas constraints

Constraints deverão ser criadas por Migration.

---

## 38.40 Novos relacionamentos

Relacionamentos entre tabelas deverão ser definidos exclusivamente através de Migration.

# PRESERVAÇÃO DOS DADOS

## 38.41 Princípio

Toda Migration deverá preservar integralmente os dados de negócio existentes.

---

## 38.42 Exclusão de dados

Nenhuma Migration poderá excluir automaticamente:

- Clientes;
- Produtos;
- Vendas;
- Recebimentos;
- Contas;
- Garantias;
- Inventários;
- Auditorias;
- Logs;
- demais registros operacionais.

---

## 38.43 Conversão

Quando houver necessidade de conversão de dados, a Migration deverá executar a transformação de forma segura.

---

## 38.44 Validação

Após conversão de dados deverá existir validação de consistência.

---

## 38.45 Interrupção

Caso seja detectada inconsistência crítica durante a conversão, a Migration deverá interromper sua execução.

---

# ALTERAÇÃO DE COLUNAS

## 38.46 Alteração de tipo

Mudanças de tipo deverão utilizar estratégia segura de migração.

Nunca alterar diretamente quando houver risco de perda de informação.

---

## 38.47 Estratégia recomendada

Sempre que necessário utilizar o seguinte fluxo:

1. Criar nova coluna.
2. Migrar os dados.
3. Validar.
4. Atualizar a aplicação.
5. Remover a coluna antiga em versão futura.

---

## 38.48 Compatibilidade

Durante o período de transição poderá existir convivência entre colunas antiga e nova.

---

## 38.49 Campos obrigatórios

Ao tornar uma coluna obrigatória, deverá existir estratégia para preencher registros antigos.

---

## 38.50 Valores padrão

Quando apropriado poderão ser utilizados valores padrão para preservar compatibilidade.

---

# REMOÇÃO DE ESTRUTURAS

## 38.51 Colunas

Colunas não deverão ser removidas imediatamente após deixarem de ser utilizadas.

---

## 38.52 Descontinuação

A estratégia recomendada será:

- marcar como obsoleta;
- remover referências na aplicação;
- aguardar versão futura;
- remover definitivamente.

---

## 38.53 Tabelas

O mesmo princípio aplica-se à remoção de tabelas.

---

## 38.54 Índices

Índices somente deverão ser removidos após confirmação de que não são mais utilizados.

---

## 38.55 Constraints

Constraints deverão ser removidas apenas quando sua eliminação não comprometer a integridade dos dados.

---

# SEEDS

## 38.56 Separação

Migration e Seed possuem responsabilidades distintas.

Migration altera estrutura.

Seed popula dados iniciais.

---

## 38.57 Seeds oficiais

Seeds poderão cadastrar apenas dados básicos necessários ao funcionamento do sistema.

---

## 38.58 Exemplos

São exemplos apropriados para Seeds:

- perfis;
- parâmetros;
- configurações padrão;
- situações;
- tabelas auxiliares;
- tipos;
- estados;
- municípios, quando aplicável.

---

## 38.59 Dados proibidos

Seeds nunca deverão cadastrar:

- Clientes;
- Produtos;
- Fornecedores;
- Vendas;
- Recebimentos;
- Contas;
- Garantias;
- Inventários.

---

## 38.60 Idempotência

Seeds oficiais deverão poder ser executados novamente sem produzir duplicidade.

---

# COMPATIBILIDADE

## 38.61 Atualização

Atualizações entre versões consecutivas deverão ocorrer de forma compatível.

---

## 38.62 Aplicação

Sempre que possível, a aplicação deverá suportar a transição entre versões durante o processo de implantação.

---

## 38.63 Estrutura

Alterações estruturais deverão minimizar indisponibilidade.

---

## 38.64 Convivência

Quando necessário, estruturas antiga e nova poderão coexistir temporariamente.

---

## 38.65 Evolução

A evolução do Schema deverá ocorrer de forma incremental.

---

# AMBIENTES

## 38.66 Ambientes oficiais

As mesmas Migrations deverão funcionar em:

- Desenvolvimento;
- Homologação;
- Produção.

---

## 38.67 Estrutura

Não deverão existir estruturas diferentes entre ambientes oficiais.

---

## 38.68 Testes

Toda Migration deverá ser validada em ambiente de testes antes da produção.

---

## 38.69 Produção

A execução em Produção deverá utilizar exclusivamente Migrations aprovadas.

---

## 38.70 Configuração

Diferenças entre ambientes deverão ocorrer apenas por configuração.

Nunca pela estrutura oficial do banco.

---

# FALHAS

## 38.71 Interrupção

Ao ocorrer falha durante uma Migration, nenhuma Migration posterior deverá ser executada.

---

## 38.72 Diagnóstico

A falha deverá registrar informações suficientes para diagnóstico técnico.

---

## 38.73 Continuação

A correção deverá ocorrer antes da continuidade da atualização.

---

## 38.74 Integridade

O banco nunca deverá permanecer parcialmente atualizado quando a transação puder ser revertida.

---

## 38.75 Recuperação

Após correção da causa da falha, a execução deverá continuar a partir do ponto oficialmente controlado pelo mecanismo de Migrations.

---

# EVOLUÇÃO DO SCHEMA

## 38.76 Novos módulos

Todo novo módulo deverá possuir suas próprias Migrations.

---

## 38.77 Evolução incremental

Pequenas alterações deverão preferencialmente gerar novas Migrations.

Nunca editar Migrations antigas já publicadas.

---

## 38.78 Histórico

O histórico de evolução do banco deverá permanecer preservado.

---

## 38.79 Documentação

Alterações estruturais relevantes deverão possuir descrição clara.

---

## 38.80 Padronização

Todas as futuras Migrations deverão seguir os mesmos padrões definidos nesta seção.

# MONITORAMENTO

## 38.81 Registro das Migrations

O sistema deverá manter registro permanente das Migrations executadas.

O histórico deverá permitir identificar:

- versão;
- data de execução;
- ordem;
- situação;
- duração;
- resultado.

---

## 38.82 Log Técnico

Toda execução de Migration deverá gerar Log Técnico.

Quando ocorrer falha, o Log deverá conter informações suficientes para diagnóstico, respeitando as regras da Seção 28.

---

## 38.83 Auditoria

As Migrations não geram Auditoria de negócio.

As alterações estruturais pertencem exclusivamente ao histórico técnico da aplicação.

---

## 38.84 Tempo de execução

Sempre que possível deverá ser registrado o tempo de execução de cada Migration.

---

## 38.85 Identificação

Cada execução deverá estar vinculada à versão da aplicação responsável pela atualização.

---

# TESTES

## 38.86 Testes obrigatórios

Toda Migration deverá possuir validação antes da utilização em Produção.

---

## 38.87 Estrutura

Os testes deverão confirmar:

- criação de tabelas;
- criação de colunas;
- criação de índices;
- criação de constraints;
- relacionamentos;
- compatibilidade.

---

## 38.88 Dados

Os testes deverão confirmar que os dados existentes permanecem íntegros após a execução.

---

## 38.89 Conversões

Sempre que houver transformação de dados, deverão existir testes específicos para validar a conversão.

---

## 38.90 Rollback

Quando houver Rollback disponível, ele também deverá ser testado.

---

## 38.91 Execução repetida

Os testes deverão confirmar que Migrations já executadas não sejam reaplicadas.

---

## 38.92 Seeds

Os testes deverão validar que Seeds oficiais possam ser executados novamente sem gerar duplicidade.

---

## 38.93 Ambientes

As mesmas Migrations deverão ser testadas nos ambientes de:

- Desenvolvimento;
- Homologação.

Somente após aprovação poderão ser utilizadas em Produção.

---

## 38.94 Compatibilidade

Os testes deverão validar atualização entre versões consecutivas.

---

## 38.95 Regressão

Novas Migrations não deverão comprometer estruturas já existentes.

---

# VERSIONAMENTO DO SCHEMA

## 38.96 Controle

A estrutura oficial do banco deverá possuir versionamento controlado.

---

## 38.97 Estado do banco

Deverá ser possível identificar exatamente em qual versão estrutural o banco se encontra.

---

## 38.98 Compatibilidade

Cada versão do sistema deverá informar claramente quais versões do Schema são suportadas.

---

## 38.99 Atualização

A atualização do Schema deverá ocorrer exclusivamente através das Migrations oficiais.

---

## 38.100 Integridade

Não deverá existir banco parcialmente versionado sem identificação oficial.

---

# BOAS PRÁTICAS

## 38.101 Pequenas alterações

Preferir Migrations pequenas e objetivas.

Evitar grandes alterações estruturais em uma única Migration.

---

## 38.102 Legibilidade

Os nomes das Migrations deverão descrever claramente seu objetivo.

---

## 38.103 Independência

Cada Migration deverá executar apenas a alteração necessária.

Evitar acumular mudanças independentes em um único arquivo.

---

## 38.104 Organização

As Migrations deverão permanecer organizadas cronologicamente e versionadas juntamente com o projeto.

---

## 38.105 Documentação

Alterações estruturais relevantes deverão possuir documentação complementar quando envolverem mudanças significativas de arquitetura.

---

# REGRAS GERAIS

## 38.106 Regras gerais de Migrações e Versionamento

O sistema deverá:

- utilizar exclusivamente Migrations para alterações estruturais;
- proibir alterações manuais em Produção;
- manter histórico permanente das Migrations;
- identificar unicamente cada Migration;
- registrar data, descrição e ordem;
- executar Migrations em sequência oficial;
- impedir execução duplicada;
- utilizar controle de versão do Schema;
- executar Migrations automaticamente pelo mecanismo oficial;
- utilizar transações sempre que suportado;
- executar Rollback em caso de falha transacional;
- interromper imediatamente a atualização quando ocorrer erro;
- gerar Logs Técnicos;
- não gerar Auditoria de negócio;
- preservar integralmente os dados existentes;
- utilizar estratégias seguras para alteração de tipos;
- evitar remoções imediatas de colunas e tabelas;
- utilizar fase de descontinuação antes da exclusão definitiva;
- separar completamente Migration e Seed;
- utilizar Seeds apenas para dados iniciais do sistema;
- impedir Seeds de cadastrar dados operacionais;
- permitir reexecução segura dos Seeds;
- manter compatibilidade entre versões consecutivas;
- utilizar as mesmas Migrations em todos os ambientes;
- validar todas as alterações em ambiente de testes;
- impedir continuidade após falhas;
- preservar consistência estrutural;
- registrar tempo de execução;
- testar criação, alteração e remoção de estruturas;
- testar conversões de dados;
- testar Rollback;
- testar reexecução;
- testar compatibilidade entre versões;
- manter versionamento oficial do Schema;
- identificar claramente a versão estrutural do banco;
- preferir Migrations pequenas;
- manter nomenclatura clara;
- manter documentação adequada;
- aplicar estas regras a toda evolução futura do banco.

## 38.107 Precedência

As regras desta seção deverão ser aplicadas a toda alteração estrutural do banco de dados.

Nenhuma exceção poderá ser implementada sem revisão formal da especificação.

---

## 38.108 Revisões

Toda alteração nesta seção deverá ser registrada no histórico oficial de versões do BUSINESS_RULES.md.

---

## 38.109 Evolução

Novas tecnologias de banco de dados poderão ser adotadas futuramente, desde que preservem:

- integridade;
- rastreabilidade;
- compatibilidade;
- histórico das Migrations;
- regras de negócio.

---

## 38.110 Encerramento

A Seção Migrações e Versionamento estabelece o padrão oficial para evolução controlada da estrutura do banco de dados, garantindo estabilidade, segurança e preservação das informações durante todo o ciclo de vida do sistema.

# 39. GLOSSÁRIO OFICIAL

## 39.1 Finalidade

O Glossário Oficial estabelece o significado único e oficial dos termos utilizados em todo o sistema.

Sempre que um termo definido nesta seção for utilizado em qualquer módulo, documento ou regra de negócio, deverá possuir exatamente o significado aqui estabelecido.

---

## 39.2 Objetivo

O Glossário tem como objetivos:

- eliminar ambiguidades;
- padronizar nomenclaturas;
- facilitar o desenvolvimento;
- facilitar a manutenção;
- garantir interpretação uniforme das regras de negócio.

---

## 39.3 Abrangência

As definições desta seção aplicam-se a:

- BUSINESS_RULES.md;
- documentação técnica;
- documentação funcional;
- banco de dados;
- APIs;
- interfaces;
- testes;
- futuras integrações.

---

## 39.4 Termo oficial

Cada termo definido neste Glossário deverá possuir apenas um significado oficial.

---

## 39.5 Conflitos

Em caso de conflito entre interpretações, prevalecerá a definição estabelecida nesta seção.

---

# ENTIDADES

## 39.6 Loja

Loja é a empresa cadastrada no sistema.

Toda informação pertence exclusivamente à Loja proprietária.

---

## 39.7 Usuário

Usuário é a pessoa autorizada a acessar o sistema mediante autenticação válida.

---

## 39.8 Administrador

Administrador é o Usuário que possui acesso completo às funcionalidades autorizadas da Loja.

---

## 39.9 Operador

Operador é o Usuário cujas permissões são definidas pelo Administrador.

---

## 39.10 Sessão

Sessão é o período compreendido entre o Login e o Logout ou expiração automática da autenticação.

---

## 39.11 Cliente

Cliente é a pessoa física ou jurídica que realiza compras ou utiliza serviços da Loja.

---

## 39.12 Fornecedor

Fornecedor é a pessoa física ou jurídica responsável pelo fornecimento de produtos ou serviços para a Loja.

---

## 39.13 Produto

Produto é qualquer item controlado pelo sistema que possa ser comercializado, movimentado ou utilizado pela Loja.

---

## 39.14 Categoria

Categoria é a classificação utilizada para organizar Produtos.

---

## 39.15 Marca

Marca é a identificação comercial do fabricante ou da linha do Produto.

---

## 39.16 Cor

Cor é uma característica utilizada para diferenciar variações de um Produto.

---

## 39.17 Tamanho

Tamanho é uma característica utilizada para identificar variações dimensionais de um Produto.

---

## 39.18 Gênero

Gênero é uma característica opcional utilizada para classificação comercial de determinados Produtos.

---

## 39.19 Código do Produto

Código do Produto é o identificador operacional utilizado pela Loja para localizar um Produto.

---

## 39.20 Código de Barras

Código de Barras é o identificador comercial utilizado para leitura automática de Produtos.

---

# OPERAÇÕES

## 39.21 Entrada de Produtos

Entrada de Produtos é a operação responsável pela incorporação de mercadorias ao Estoque.

---

## 39.22 Estoque

Estoque representa a quantidade disponível de determinado Produto.

---

## 39.23 Movimentação de Estoque

Movimentação de Estoque é qualquer operação que altere a quantidade disponível de um Produto.

---

## 39.24 Venda

Venda é a operação comercial que formaliza a negociação entre a Loja e o Cliente.

---

## 39.25 Item da Venda

Item da Venda é cada Produto individual pertencente a uma Venda.

---

## 39.26 Cancelamento

Cancelamento é a operação que invalida uma transação conforme as regras específicas do módulo correspondente.

---

## 39.27 Estorno

Estorno é a operação destinada a desfazer efeitos financeiros ou operacionais de uma transação conforme regras específicas.

---

## 39.28 Finalização

Finalização é o momento em que determinada operação torna-se concluída conforme as regras do módulo.

---

## 39.29 Situação

Situação representa a condição operacional atual de uma entidade.

Exemplos:

- Aberta;
- Finalizada;
- Cancelada;
- Pendente;
- Paga.

---

## 39.30 Estado

Estado representa a condição lógica utilizada internamente pelo sistema para controlar o ciclo de vida de uma entidade.

---

# DOCUMENTOS

## 39.31 Documento

Documento é qualquer registro formal emitido ou controlado pelo sistema.

---

## 39.32 Número

Número é o identificador sequencial utilizado para individualizar um Documento.

---

## 39.33 Histórico

Histórico é o conjunto cronológico de registros relacionados a determinada entidade.

---

## 39.34 Observação

Observação é um texto livre utilizado para registrar informações complementares.

---

## 39.35 Anexo

Anexo é qualquer arquivo vinculado a uma entidade do sistema.

---

# USUÁRIOS

## 39.36 Autenticação

Autenticação é o processo de validação da identidade do Usuário.

---

## 39.37 Autorização

Autorização é o processo de verificação das permissões concedidas ao Usuário autenticado.

---

## 39.38 Permissão

Permissão é o direito concedido para executar determinada funcionalidade.

---

## 39.39 Perfil

Perfil é o conjunto de permissões atribuídas ao Usuário.

---

## 39.40 Login

Login é o procedimento de início de uma Sessão autenticada no sistema.

# FINANCEIRO

## 39.41 Crediário

Crediário é a modalidade de pagamento parcelado concedida diretamente pela Loja ao Cliente, sem intermediação financeira externa.

---

## 39.42 Parcela

Parcela é cada obrigação financeira individual originada de um Crediário.

---

## 39.43 Recebimento

Recebimento é a operação que registra a quitação total ou parcial de uma ou mais Parcelas de um Cliente.

---

## 39.44 Recebível

Recebível é o valor que a Loja tem direito de receber de uma operadora de cartão em razão de vendas realizadas.

---

## 39.45 Conta

Conta é toda obrigação financeira assumida pela Loja perante um Fornecedor ou outro credor.

---

## 39.46 Pagamento

Pagamento é a operação que liquida total ou parcialmente uma Conta.

---

## 39.47 Forma de Pagamento

Forma de Pagamento é o meio utilizado para liquidar uma Venda, Recebimento ou Pagamento.

Exemplos:

- Dinheiro;
- PIX;
- Cartão;
- Transferência;
- Crediário.

---

## 39.48 Operadora de Cartão

Operadora de Cartão é a instituição responsável pelo processamento das transações realizadas por cartões.

---

## 39.49 Taxa

Taxa é o percentual ou valor aplicado sobre determinada operação financeira conforme configuração da Loja.

---

## 39.50 Antecipação

Antecipação é a operação financeira pela qual a Loja recebe um Recebível antes do prazo originalmente previsto.

---

# PÓS-VENDA

## 39.51 Garantia

Garantia é o processo de atendimento pós-venda destinado ao tratamento de defeitos, assistência técnica, troca ou análise de Produtos.

---

## 39.52 Atendimento

Atendimento é cada ação registrada durante o processo de Garantia.

---

## 39.53 Condicional

Condicional é a saída temporária de Produtos para avaliação pelo Cliente, sem caracterizar Venda definitiva.

---

## 39.54 Devolução

Devolução é a operação pela qual um Produto retorna ao Estoque conforme regras específicas do módulo correspondente.

---

## 39.55 Troca

Troca é a substituição de um Produto por outro conforme regras da Garantia ou da política comercial da Loja.

---

# CONTROLE

## 39.56 Inventário

Inventário é o processo de conferência física do Estoque com posterior regularização das divergências encontradas.

---

## 39.57 Divergência

Divergência é a diferença identificada entre a quantidade física e a quantidade registrada no sistema.

---

## 39.58 Ajuste

Ajuste é a movimentação destinada à regularização do Estoque após validação do Inventário.

---

## 39.59 Conferência

Conferência é a verificação realizada para validar informações registradas pelo sistema.

---

## 39.60 Regularização

Regularização é o conjunto de ações destinadas a corrigir inconsistências identificadas durante processos operacionais.

---

# GESTÃO

## 39.61 Dashboard

Dashboard é o painel responsável pela apresentação consolidada dos principais indicadores do sistema.

---

## 39.62 Indicador

Indicador é uma informação consolidada utilizada para acompanhamento operacional ou gerencial.

---

## 39.63 Relatório

Relatório é a apresentação organizada de informações destinadas à consulta, análise ou impressão.

---

## 39.64 Filtro

Filtro é o critério utilizado para restringir o conjunto de registros apresentados ao usuário.

---

## 39.65 Pesquisa

Pesquisa é o mecanismo utilizado para localizar registros com base em critérios informados pelo usuário.

---

# SEGURANÇA

## 39.66 Auditoria

Auditoria é o registro permanente das ações relevantes realizadas pelos Usuários.

---

## 39.67 Log Técnico

Log Técnico é o registro de eventos, falhas, exceções e informações utilizadas para diagnóstico da aplicação.

---

## 39.68 Permissão Efetiva

Permissão Efetiva é o conjunto de permissões realmente aplicadas ao Usuário durante sua Sessão.

---

## 39.69 Isolamento

Isolamento é o princípio que impede qualquer Loja de acessar dados pertencentes a outra Loja.

---

## 39.70 Fonte Autoritativa

Fonte Autoritativa é a origem oficial considerada verdadeira pelo sistema.

O Backend é sempre a fonte autoritativa para autenticação, permissões, Estoque, valores e regras de negócio.

---

# INFRAESTRUTURA

## 39.71 API

API é a interface oficial de comunicação entre o sistema e aplicações externas ou componentes internos.

---

## 39.72 Endpoint

Endpoint é um recurso específico disponibilizado por uma API para execução de determinada operação.

---

## 39.73 Webhook

Webhook é o mecanismo de notificação automática enviado pelo sistema para aplicações externas quando determinado evento ocorrer.

---

## 39.74 Migration

Migration é a alteração controlada da estrutura do banco de dados, executada pelo mecanismo oficial da aplicação.

---

## 39.75 Seed

Seed é a rotina responsável pela criação dos dados iniciais necessários ao funcionamento do sistema.

---

## 39.76 Backup

Backup é a cópia de segurança destinada à recuperação dos dados em caso de falha, perda ou desastre.

---

## 39.77 Restore

Restore é o processo de recuperação dos dados previamente armazenados em um Backup.

---

## 39.78 Rollback

Rollback é o processo de reversão controlada de uma operação ou Migration para retornar ao estado anterior.

---

## 39.79 Idempotência

Idempotência é a propriedade que garante que múltiplas execuções da mesma operação produzam apenas um único efeito persistente.

---

## 39.80 Rate Limit

Rate Limit é o mecanismo responsável por limitar a quantidade de requisições permitidas em determinado intervalo de tempo.

# CONCEITOS GERAIS

## 39.81 Snapshot

Snapshot é o registro histórico imutável dos dados utilizados em determinada operação.

Seu objetivo é preservar exatamente as informações existentes no momento da operação, independentemente de alterações futuras.

---

## 39.82 Data Operacional

Data Operacional é a data oficial utilizada pelo sistema para registros, cálculos, vencimentos e regras de negócio.

Ela prevalece sobre qualquer data enviada pelo navegador ou dispositivo do usuário.

---

## 39.83 Hora Operacional

Hora Operacional é o horário oficial utilizado pelo sistema para registrar eventos e executar regras de negócio.

---

## 39.84 Regra de Negócio

Regra de Negócio é toda norma funcional que determina como o sistema deverá se comportar diante de determinada situação.

---

## 39.85 Fluxo

Fluxo é a sequência lógica de etapas que compõem uma operação do sistema.

---

## 39.86 Processo

Processo é o conjunto organizado de operações relacionadas a um mesmo objetivo funcional.

---

## 39.87 Evento

Evento é qualquer ocorrência relevante que possa alterar o estado de uma entidade ou gerar registros técnicos ou de Auditoria.

---

## 39.88 Estado

Estado é a condição lógica atual de uma entidade durante seu ciclo de vida.

---

## 39.89 Situação

Situação é a classificação operacional utilizada para representar a condição atual de uma entidade perante o usuário.

---

## 39.90 Módulo

Módulo é o conjunto de funcionalidades relacionadas a um mesmo domínio de negócio.

Exemplos:

- Clientes;
- Produtos;
- Estoque;
- Vendas;
- Garantias;
- Financeiro.

---

# DOCUMENTAÇÃO

## 39.91 BUSINESS_RULES.md

Documento oficial que reúne todas as regras de negócio do sistema.

É a principal referência funcional para desenvolvimento, testes e manutenção.

---

## 39.92 Especificação

Especificação é qualquer documento oficial que descreva comportamentos, requisitos ou padrões do sistema.

---

## 39.93 Implementação

Implementação é a materialização das regras de negócio através do desenvolvimento do software.

---

## 39.94 Compatibilidade

Compatibilidade é a capacidade de evolução do sistema sem comprometer funcionalidades previamente aprovadas.

---

## 39.95 Evolução

Evolução é a incorporação controlada de novas funcionalidades preservando as regras já estabelecidas.

---

# PRINCÍPIOS

## 39.96 Fonte Única da Verdade

Sempre que houver divergência entre informações, prevalecerá a fonte autoritativa definida pelo sistema.

---

## 39.97 Consistência

Consistência é a garantia de que todas as informações relacionadas permanecem corretas entre si após qualquer operação.

---

## 39.98 Integridade

Integridade é a preservação da exatidão, confiabilidade e coerência dos dados armazenados.

---

## 39.99 Rastreabilidade

Rastreabilidade é a capacidade de identificar a origem, alterações e histórico de uma informação.

---

## 39.100 Escalabilidade

Escalabilidade é a capacidade do sistema crescer em volume de dados e usuários sem necessidade de alterar suas regras de negócio.

---

# CONVENÇÕES DO GLOSSÁRIO

## 39.101 Singular

Sempre que possível, os termos do Glossário deverão ser interpretados em seu significado singular, ainda que utilizados no plural em outros documentos.

---

## 39.102 Gênero textual

As definições do Glossário possuem finalidade técnica.

O gênero gramatical utilizado não altera o significado funcional dos termos.

---

## 39.103 Novos termos

Todo novo termo incorporado ao sistema deverá ser adicionado ao Glossário Oficial antes de sua utilização definitiva.

---

## 39.104 Termos equivalentes

Não deverão existir dois termos diferentes representando oficialmente o mesmo conceito de negócio.

---

## 39.105 Revisões

Toda alteração no significado de qualquer termo deverá ser registrada no histórico de versões do BUSINESS_RULES.md.

---

# REGRAS GERAIS

## 39.106 Regras gerais do Glossário Oficial

O Glossário deverá:

- definir oficialmente todos os conceitos utilizados pelo sistema;
- eliminar ambiguidades;
- padronizar nomenclaturas;
- servir como referência para todas as regras de negócio;
- ser utilizado por desenvolvedores, analistas e testadores;
- manter um único significado para cada termo;
- preservar compatibilidade entre documentos;
- ser atualizado sempre que novos conceitos forem incorporados;
- impedir interpretações conflitantes;
- servir de base para APIs, banco de dados, documentação e testes.

---

## 39.107 Precedência

Quando houver conflito entre interpretações de um termo, prevalecerá a definição constante nesta seção.

---

## 39.108 Aplicação

As definições deste Glossário aplicam-se a:

- BUSINESS_RULES.md;
- documentação técnica;
- documentação funcional;
- banco de dados;
- APIs;
- testes;
- integrações futuras;
- manuais do sistema.

---

## 39.109 Revisão

Toda inclusão, alteração ou remoção de termos deverá ser registrada no histórico oficial do documento.

---

## 39.110 Encerramento

O Glossário Oficial constitui a referência terminológica única do sistema.

Todos os módulos, regras de negócio, documentos, implementações e futuras evoluções deverão utilizar obrigatoriamente as definições estabelecidas nesta seção.

# 40. CONVENÇÕES GERAIS DO SISTEMA

## 40.1 Finalidade

Esta seção estabelece as convenções gerais que deverão ser observadas por todos os módulos do sistema.

Sempre que uma regra específica não existir em determinado módulo, deverão prevalecer as convenções estabelecidas nesta seção.

---

## 40.2 Objetivos

As Convenções Gerais têm como objetivos:

- padronizar comportamentos;
- reduzir ambiguidades;
- facilitar manutenção;
- garantir consistência entre módulos;
- evitar duplicação de regras.

---

## 40.3 Abrangência

Estas convenções aplicam-se a:

- interfaces;
- banco de dados;
- APIs;
- relatórios;
- dashboards;
- integrações;
- documentação;
- futuros módulos.

---

## 40.4 Obrigatoriedade

Todo novo módulo deverá respeitar integralmente estas convenções.

---

## 40.5 Prevalência

Na ausência de regra específica, esta seção será considerada referência oficial de comportamento.

---

# ENTIDADES

## 40.6 Identificador

Toda entidade deverá possuir identificador interno único.

---

## 40.7 Imutabilidade

O identificador interno nunca poderá ser alterado após sua criação.

---

## 40.8 Chave técnica

O identificador interno possui finalidade exclusivamente técnica.

Não deverá ser utilizado como informação operacional para o usuário quando existir outro identificador apropriado.

---

## 40.9 Código operacional

Quando existir código operacional (Produto, Cliente, Documento etc.), ele poderá ser apresentado ao usuário conforme regras do módulo.

---

## 40.10 Exclusividade

Não poderão existir dois registros ativos utilizando o mesmo identificador interno.

---

# CAMPOS

## 40.11 Campos obrigatórios

Todo campo obrigatório deverá ser identificado visualmente.

---

## 40.12 Campos opcionais

Campos opcionais poderão permanecer sem preenchimento, salvo quando exigidos por regras específicas.

---

## 40.13 Campos somente leitura

Campos protegidos deverão impedir edição pelo usuário.

---

## 40.14 Validação

Todo campo deverá ser validado antes da gravação.

---

## 40.15 Mensagens

Campos inválidos deverão apresentar mensagens claras e específicas.

---

## 40.16 Valores padrão

Sempre que apropriado, poderão existir valores padrão previamente definidos.

---

## 40.17 Máscaras

Campos com formato conhecido poderão utilizar máscaras de entrada.

Exemplos:

- CPF;
- CNPJ;
- telefone;
- CEP;
- datas.

---

## 40.18 Texto

Campos textuais deverão remover espaços excedentes no início e no final do conteúdo.

---

## 40.19 Conteúdo

A normalização nunca deverá alterar o significado do texto informado pelo usuário.

---

## 40.20 Numéricos

Campos numéricos deverão aceitar apenas valores compatíveis com seu tipo.

---

# DATAS

## 40.21 Formato

A apresentação oficial das datas será:

dd/MM/yyyy

---

## 40.22 Armazenamento

Internamente o sistema poderá utilizar formato técnico apropriado.

---

## 40.23 Exibição

Toda interface deverá apresentar datas de forma consistente.

---

## 40.24 Datas inválidas

Datas inválidas deverão ser rejeitadas durante a validação.

---

## 40.25 Comparações

Comparações entre datas deverão utilizar a Data Operacional oficial do sistema quando aplicável.

---

# HORÁRIOS

## 40.26 Formato

O formato oficial será:

HH:mm:ss

---

## 40.27 Precisão

Quando segundos não forem relevantes, poderão ser ocultados na interface.

---

## 40.28 Registro

Eventos técnicos deverão registrar horário completo.

---

## 40.29 Timezone

Toda operação deverá utilizar o Timezone oficial configurado para a Loja.

---

## 40.30 Consistência

Datas e horários deverão utilizar o mesmo padrão em todos os módulos.

---

# VALORES MONETÁRIOS

## 40.31 Precisão

Valores monetários deverão utilizar duas casas decimais.

---

## 40.32 Interface

Na interface deverão utilizar:

vírgula como separador decimal.

---

## 40.33 Armazenamento

Internamente poderão utilizar representação técnica apropriada.

---

## 40.34 Arredondamento

O arredondamento deverá ocorrer apenas no momento apropriado definido pela regra de negócio correspondente.

---

## 40.35 Consistência

Uma mesma operação nunca deverá apresentar valores diferentes em telas distintas.

---

# VALIDAÇÕES

## 40.36 Backend

Toda validação obrigatória deverá ocorrer no backend.

---

## 40.37 Frontend

O frontend poderá realizar validações para melhorar a experiência do usuário.

Nunca substituirá a validação oficial do backend.

---

## 40.38 Campos obrigatórios

Nenhuma operação poderá ser concluída com campos obrigatórios vazios.

---

## 40.39 Integridade

Toda gravação deverá preservar a integridade das informações.

---

## 40.40 Consistência

Validações deverão produzir resultados consistentes independentemente da interface utilizada.

# INTERFACE

## 40.41 Consistência visual

Todas as telas deverão seguir o mesmo padrão visual definido para o sistema.

---

## 40.42 Componentes

Componentes equivalentes deverão apresentar o mesmo comportamento em todos os módulos.

---

## 40.43 Navegação

A navegação entre telas deverá ser consistente e previsível.

---

## 40.44 Responsividade

Todas as telas deverão funcionar corretamente nas resoluções oficialmente suportadas.

---

## 40.45 Feedback

Toda ação do usuário deverá produzir retorno visual apropriado.

Exemplos:

- carregando;
- concluído;
- erro;
- aviso;
- informação.

---

# MENSAGENS

## 40.46 Clareza

As mensagens deverão utilizar linguagem simples, objetiva e de fácil compreensão.

---

## 40.47 Padronização

Mensagens equivalentes deverão utilizar o mesmo texto em todos os módulos.

---

## 40.48 Erros

Mensagens de erro deverão informar o problema sem expor detalhes técnicos da implementação.

---

## 40.49 Sucesso

Operações concluídas com sucesso deverão apresentar confirmação quando apropriado.

---

## 40.50 Avisos

Mensagens de aviso deverão orientar o usuário sobre possíveis consequências antes da execução da operação.

---

# CONFIRMAÇÕES

## 40.51 Operações críticas

Operações críticas deverão solicitar confirmação antes da execução.

---

## 40.52 Exemplos

Exemplos de operações críticas:

- exclusão;
- cancelamento;
- estorno;
- encerramento de inventário;
- encerramento de garantia;
- reversões.

---

## 40.53 Texto

A confirmação deverá informar claramente qual operação será executada.

---

## 40.54 Cancelamento

O usuário poderá desistir da operação antes da confirmação definitiva.

---

## 40.55 Irreversibilidade

Quando a operação for irreversível, isso deverá ser informado explicitamente.

---

# EXCLUSÕES

## 40.56 Exclusão lógica

Sempre que aplicável, deverá ser utilizada exclusão lógica.

---

## 40.57 Exclusão física

A exclusão física somente poderá ocorrer quando prevista nas regras específicas do módulo.

---

## 40.58 Integridade

Nenhuma exclusão poderá comprometer a integridade referencial dos dados.

---

## 40.59 Histórico

Quando existir Auditoria ou Histórico, a exclusão não deverá apagar os registros históricos.

---

## 40.60 Permissões

Somente usuários autorizados poderão executar exclusões.

---

# PESQUISAS

## 40.61 Pesquisa padrão

Toda pesquisa deverá apresentar resultados consistentes com os filtros aplicados.

---

## 40.62 Pesquisa parcial

Sempre que aplicável, deverá ser permitida pesquisa por parte do conteúdo.

---

## 40.63 Maiúsculas e minúsculas

Pesquisas textuais deverão ignorar diferenças entre letras maiúsculas e minúsculas.

---

## 40.64 Acentuação

Sempre que possível, pesquisas deverão ignorar diferenças de acentuação.

---

## 40.65 Resultado vazio

Quando nenhum registro for encontrado deverá ser apresentada mensagem apropriada.

---

# FILTROS

## 40.66 Independência

Filtros poderão ser utilizados isoladamente ou em conjunto.

---

## 40.67 Persistência

Durante a navegação na listagem, os filtros deverão permanecer aplicados até que sejam alterados ou removidos pelo usuário.

---

## 40.68 Limpeza

O sistema deverá permitir limpar todos os filtros de forma simples.

---

## 40.69 Compatibilidade

Filtros deverão ser compatíveis com pesquisa, ordenação e paginação.

---

## 40.70 Consistência

A aplicação dos filtros nunca deverá produzir resultados inconsistentes.

---

# LISTAGENS

## 40.71 Paginação

Todas as listagens deverão seguir a política oficial de paginação definida pelo sistema.

---

## 40.72 Ordenação

Toda listagem deverá possuir ordenação inicial definida.

---

## 40.73 Alteração

Quando permitido, o usuário poderá alterar a ordenação.

---

## 40.74 Colunas

As colunas apresentadas deverão ser compatíveis com o objetivo da listagem.

---

## 40.75 Atualização

Após inclusão, alteração ou exclusão de registros, a listagem deverá permanecer consistente.

---

# COMPORTAMENTOS PADRÃO

## 40.76 Salvamento

Operações somente serão consideradas concluídas após confirmação oficial do backend.

---

## 40.77 Cancelamento

Operações canceladas não deverão produzir alterações permanentes.

---

## 40.78 Concorrência

Quando dois usuários alterarem o mesmo registro simultaneamente, deverão prevalecer as regras oficiais de concorrência definidas pelo sistema.

---

## 40.79 Integridade

Toda operação deverá preservar a integridade dos dados relacionados.

---

## 40.80 Consistência

O comportamento de funcionalidades equivalentes deverá permanecer uniforme em todos os módulos.

# CONVENÇÕES TRANSVERSAIS

## 40.81 Aplicação geral

As Convenções Gerais aplicam-se a todos os módulos existentes e futuros do sistema.

---

## 40.82 Novos módulos

Todo novo módulo deverá seguir integralmente as convenções desta seção, salvo quando houver regra específica mais restritiva.

---

## 40.83 Reutilização

Sempre que possível, funcionalidades equivalentes deverão reutilizar os mesmos componentes, fluxos e comportamentos.

---

## 40.84 Uniformidade

A experiência do usuário deverá permanecer uniforme em toda a aplicação.

---

## 40.85 Independência

As convenções desta seção independem da tecnologia utilizada para implementação.

---

# PADRONIZAÇÃO

## 40.86 Nomenclatura

A nomenclatura utilizada em telas, relatórios, APIs e documentação deverá ser consistente com o Glossário Oficial.

---

## 40.87 Terminologia

Não deverão existir termos diferentes representando o mesmo conceito de negócio.

---

## 40.88 Campos equivalentes

Campos que representem a mesma informação deverão possuir o mesmo comportamento em todos os módulos.

---

## 40.89 Valores padrão

Valores padrão deverão ser utilizados de forma consistente sempre que previstos nas regras de negócio.

---

## 40.90 Documentação

Toda documentação oficial deverá utilizar as mesmas convenções estabelecidas nesta seção.

---

# COMPATIBILIDADE

## 40.91 Evolução

Novas funcionalidades deverão respeitar integralmente as Convenções Gerais.

---

## 40.92 Retrocompatibilidade

Sempre que possível, melhorias não deverão alterar comportamentos já conhecidos pelos usuários sem justificativa funcional.

---

## 40.93 Alterações

Mudanças nas convenções deverão ocorrer apenas mediante revisão oficial do BUSINESS_RULES.md.

---

## 40.94 Consistência

A evolução do sistema nunca deverá comprometer a consistência entre módulos.

---

## 40.95 Escalabilidade

As convenções deverão permitir crescimento do sistema sem necessidade de redefinição dos padrões estabelecidos.

---

# MANUTENÇÃO

## 40.96 Revisões

Toda alteração nesta seção deverá ser registrada no histórico oficial de versões do BUSINESS_RULES.md.

---

## 40.97 Inclusões

Novas convenções deverão ser incorporadas nesta seção antes de sua utilização definitiva.

---

## 40.98 Remoções

Convenções somente poderão ser removidas quando substituídas por regra equivalente oficialmente aprovada.

---

## 40.99 Histórico

O histórico das convenções deverá permanecer preservado para rastreabilidade das alterações.

---

## 40.100 Governança

As Convenções Gerais deverão servir como referência obrigatória para analistas, desenvolvedores, testadores e futuras integrações.

---

# REGRAS GERAIS

## 40.101 Regras gerais das Convenções Gerais do Sistema

O sistema deverá:

- aplicar estas convenções a todos os módulos;
- utilizar identificadores internos únicos;
- impedir alteração dos identificadores internos;
- identificar claramente campos obrigatórios;
- validar todos os campos antes da gravação;
- utilizar o formato oficial de datas;
- utilizar o formato oficial de horários;
- utilizar duas casas decimais para valores monetários;
- realizar arredondamentos conforme regras oficiais;
- utilizar o timezone oficial da Loja;
- remover espaços excedentes em campos textuais;
- validar campos numéricos;
- impedir gravações com campos obrigatórios vazios;
- utilizar exclusão lógica sempre que aplicável;
- restringir exclusões físicas às regras específicas;
- apresentar mensagens claras e padronizadas;
- solicitar confirmação em operações críticas;
- manter pesquisas consistentes;
- permitir filtros compatíveis entre si;
- utilizar paginação padronizada;
- manter ordenação consistente;
- preservar a integridade dos dados;
- preservar consistência entre módulos;
- reutilizar comportamentos equivalentes;
- utilizar terminologia padronizada;
- manter compatibilidade durante a evolução;
- documentar alterações de convenções;
- aplicar estas regras a toda funcionalidade futura.

---

## 40.102 Precedência

Na ausência de regra específica, prevalecerão as Convenções Gerais estabelecidas nesta seção.

Quando existir conflito entre uma regra específica e esta seção, prevalecerá a regra específica, desde que não reduza requisitos obrigatórios de segurança, integridade ou isolamento definidos em outras seções.

---

## 40.103 Integração com outras seções

As Convenções Gerais complementam todas as demais seções do BUSINESS_RULES.md e deverão ser interpretadas em conjunto com:

- Glossário Oficial;
- Segurança;
- Performance;
- Auditoria;
- Logs Técnicos;
- APIs;
- Migrações;
- demais módulos funcionais.

---

## 40.104 Evolução

Novas convenções poderão ser adicionadas futuramente sem alterar o comportamento funcional previamente aprovado, desde que mantenham compatibilidade com as regras existentes.

---

## 40.105 Encerramento

A Seção Convenções Gerais do Sistema estabelece os padrões mínimos obrigatórios de comportamento para toda a aplicação.

Toda funcionalidade existente ou futura deverá observar estas convenções, garantindo uniformidade, previsibilidade, facilidade de manutenção e consistência em todo o sistema.

# 41. REGRAS GERAIS DE DESENVOLVIMENTO

## 41.1 Finalidade

Esta seção estabelece os princípios obrigatórios que deverão orientar o desenvolvimento, a manutenção e a evolução do sistema.

As regras desta seção independem da linguagem, framework, banco de dados ou infraestrutura utilizados.

Toda implementação deverá respeitar simultaneamente:

- as regras específicas do módulo;
- as regras transversais do BUSINESS_RULES.md;
- as convenções gerais do sistema;
- os requisitos de segurança, integridade e isolamento.

---

## 41.2 Objetivos

As Regras Gerais de Desenvolvimento têm como objetivos:

- manter coerência entre módulos;
- evitar duplicação de lógica;
- preservar as regras de negócio;
- facilitar manutenção;
- reduzir regressões;
- melhorar testabilidade;
- permitir evolução segura;
- impedir decisões improvisadas pela implementação.

---

## 41.3 Autoridade funcional

O BUSINESS_RULES.md é a autoridade máxima para as regras funcionais do sistema.

A implementação não poderá:

- contrariar regra aprovada;
- simplificar comportamento alterando seu significado;
- omitir validação obrigatória;
- criar exceção não documentada;
- substituir regra oficial por conveniência técnica.

---

## 41.4 Ausência de regra específica

Quando uma situação não estiver expressamente definida em um módulo, deverão ser aplicadas:

1. as regras transversais do BUSINESS_RULES.md;
2. as Convenções Gerais do Sistema;
3. a regra que preserve maior integridade, segurança e rastreabilidade.

A implementação não deverá inventar nova regra de negócio sem revisão formal da especificação.

---

## 41.5 Conflitos entre regras

Quando houver aparente conflito entre regras:

- a regra específica do módulo prevalece sobre regra genérica;
- a regra mais recente prevalece quando houver revisão formal;
- requisitos de segurança, integridade e isolamento não podem ser reduzidos;
- a divergência deverá ser registrada e esclarecida antes da implementação definitiva.

---

# BACKEND COMO FONTE AUTORITATIVA

## 41.6 Backend autoritativo

Toda regra de negócio deverá ser implementada e validada no backend.

O backend deverá ser a fonte autoritativa para:

- autenticação;
- autorização;
- Loja;
- usuário responsável;
- preços;
- custos;
- Estoque;
- saldos;
- limites;
- situações;
- datas oficiais;
- efeitos financeiros;
- efeitos operacionais.

---

## 41.7 Dados recebidos do frontend

Todo dado enviado pelo frontend deverá ser tratado como potencialmente inválido.

Mesmo quando o frontend oficial tiver realizado validação anterior.

---

## 41.8 Revalidação

O backend deverá revalidar integralmente:

- tipos;
- formatos;
- obrigatoriedade;
- limites;
- relacionamentos;
- permissão;
- estado atual da entidade;
- consistência financeira;
- disponibilidade de Estoque.

---

## 41.9 Campos derivados

Campos derivados não deverão ser aceitos como autoridade quando puderem ser calculados pelo backend.

Exemplos:

- subtotal;
- total;
- custo total;
- saldo;
- situação;
- valor da Taxa;
- valor líquido;
- quantidade disponível.

---

## 41.10 Identidade da operação

O backend deverá obter do contexto autenticado:

- Loja;
- usuário;
- Perfil;
- permissões;
- Sessão.

O cliente não poderá definir esses dados autoritativamente.

---

# RESPONSABILIDADE DO FRONTEND

## 41.11 Finalidade do frontend

O frontend será responsável por:

- apresentação;
- navegação;
- interação;
- feedback visual;
- acessibilidade;
- validações preliminares;
- organização da experiência do usuário.

---

## 41.12 Limites do frontend

O frontend não deverá decidir autoritativamente:

- se o usuário possui permissão;
- se existe Estoque suficiente;
- qual custo deve ser utilizado;
- qual saldo permanece;
- qual situação será gravada;
- qual número de operação será criado;
- qual Taxa financeira será aplicada.

---

## 41.13 Validações preliminares

Validações do frontend possuem finalidade de melhorar a experiência.

Exemplos:

- campo obrigatório;
- formato de telefone;
- número inválido;
- data incompleta;
- bloqueio visual de duplo envio.

A mesma validação deverá existir no backend quando for relevante à integridade.

---

## 41.14 Ocultação visual

Ocultar:

- botão;
- menu;
- card;
- campo;
- rota visual

não representa proteção de segurança.

A autorização correspondente deverá existir no backend.

---

## 41.15 Estado visual

O frontend deverá refletir o estado confirmado pelo backend.

Não deverá apresentar uma operação como concluída antes da confirmação oficial.

---

# CENTRALIZAÇÃO DAS REGRAS

## 41.16 Regra implementada uma vez

Toda regra de negócio deverá possuir implementação centralizada sempre que for utilizada por mais de um fluxo.

Evitar duplicar a mesma lógica em:

- rotas diferentes;
- páginas diferentes;
- comandos diferentes;
- integrações;
- tarefas automáticas.

---

## 41.17 Serviços reutilizáveis

Regras compartilhadas deverão ser implementadas em serviços, casos de uso ou componentes de domínio reutilizáveis.

Exemplos:

- validação de CPF;
- cálculo de saldo;
- aplicação de Taxa;
- geração de parcelas;
- validação de Estoque;
- criação de Auditoria.

---

## 41.18 Duplicação de lógica

É proibido manter versões diferentes da mesma regra sem justificativa funcional.

Exemplo incorreto:

Uma rota calcula saldo de Crediário de uma forma.

Outra rota calcula o mesmo saldo de forma diferente.

---

## 41.19 Interface única para a regra

Quando diferentes módulos necessitarem da mesma regra, deverão consumir uma única implementação oficial ou contrato comum.

---

## 41.20 Alteração centralizada

Alterar uma regra compartilhada deverá exigir mudança em um ponto central, sempre que tecnicamente possível.

---

# MODULARIDADE

## 41.21 Responsabilidade dos módulos

Cada módulo deverá possuir responsabilidade funcional claramente definida.

Exemplos:

- Clientes controla Clientes;
- Estoque controla movimentações quantitativas;
- Vendas controla operações comerciais;
- Financeiro controla efeitos financeiros;
- Auditoria controla rastreabilidade transversal.

---

## 41.22 Baixo acoplamento

Os módulos deverão possuir baixo acoplamento.

Uma alteração interna em um módulo não deverá exigir mudanças desnecessárias em módulos não relacionados.

---

## 41.23 Alta coesão

Cada módulo deverá agrupar regras e comportamentos pertencentes ao mesmo domínio.

Não misturar responsabilidades sem necessidade.

---

## 41.24 Comunicação entre módulos

A comunicação entre módulos deverá ocorrer por contratos claros e estáveis.

Evitar dependência direta de detalhes internos de outro módulo.

---

## 41.25 Dependências circulares

Dependências circulares entre módulos deverão ser evitadas.

Quando identificadas, a arquitetura deverá extrair a responsabilidade compartilhada para componente apropriado.

---

## 41.26 Efeitos entre módulos

Quando uma operação produzir efeitos em múltiplos módulos, o fato de negócio deverá possuir coordenação única.

Exemplo:

Venda pode afetar:

- Estoque;
- Financeiro;
- Crediário;
- Recebíveis;
- Auditoria.

A operação deverá ser coordenada como uma unidade consistente.

---

# ORGANIZAÇÃO DO CÓDIGO

## 41.27 Separação de responsabilidades

A implementação deverá separar, sempre que aplicável:

- apresentação;
- validação;
- regra de negócio;
- acesso a dados;
- geração de documentos;
- integrações;
- infraestrutura.

---

## 41.28 Regras de negócio e rotas

Rotas ou controladores não deverão concentrar toda a lógica de negócio.

Devem:

- receber a requisição;
- validar o contrato;
- acionar o caso de uso;
- devolver a resposta apropriada.

---

## 41.29 Acesso a dados

Consultas e persistência deverão ser organizadas de forma a evitar SQL espalhado indiscriminadamente pelo código.

---

## 41.30 Funções extensas

Funções excessivamente longas ou com múltiplas responsabilidades deverão ser divididas quando isso melhorar clareza e testabilidade.

---

## 41.31 Nomes claros

Classes, funções, variáveis, tabelas e componentes deverão possuir nomes claros e coerentes com o Glossário Oficial.

---

## 41.32 Comentários

Comentários deverão explicar decisões relevantes, limitações ou regras não óbvias.

Comentários não deverão substituir código legível.

---

## 41.33 Código morto

Código sem utilização deverá ser removido após confirmação de que não participa de compatibilidade ou transição oficial.

---

## 41.34 Código legado

Código legado ainda necessário deverá ser identificado e tratado com cautela.

Refatorações não poderão alterar silenciosamente o comportamento funcional aprovado.

---

# REUTILIZAÇÃO E CONSISTÊNCIA

## 41.35 Componentes reutilizáveis

Componentes equivalentes deverão ser reutilizados quando isso preservar consistência.

Exemplos:

- campos de moeda;
- seleção de datas;
- paginação;
- estados de carregamento;
- confirmações;
- mensagens.

---

## 41.36 Validações reutilizáveis

Validações comuns deverão utilizar a mesma implementação.

Exemplos:

- CPF;
- CNPJ;
- CEP;
- E-mail;
- valores monetários;
- datas civis.

---

## 41.37 Cálculos financeiros

Cálculos financeiros equivalentes deverão utilizar a mesma política de precisão e arredondamento.

---

## 41.38 Datas e horários

Conversão e apresentação temporal deverão utilizar funções oficiais compartilhadas.

Evitar lógica de timezone duplicada em múltiplos módulos.

---

## 41.39 Estados e situações

Estados e situações oficiais deverão ser representados por valores centralizados e consistentes.

Não espalhar textos livres diferentes para representar o mesmo estado.

---

## 41.40 Contratos estáveis

Serviços e componentes compartilhados deverão possuir contratos claros para reduzir regressões durante sua evolução.

# CONFIGURAÇÕES

## 41.41 Centralização

Toda configuração parametrizável deverá permanecer centralizada.

Nunca espalhar configurações equivalentes por múltiplos módulos.

---

## 41.42 Valores fixos

Evitar números mágicos e textos fixos no código.

Sempre que possível deverão ser utilizados:

- constantes;
- parâmetros;
- configurações oficiais.

---

## 41.43 Configurações da Loja

Configurações específicas da Loja deverão respeitar integralmente o isolamento entre Lojas.

---

## 41.44 Configurações globais

Configurações globais somente poderão existir quando forem comuns a todo o sistema.

---

## 41.45 Alterações

Toda alteração de configuração deverá respeitar as regras de Auditoria quando aplicável.

---

# TRATAMENTO DE ERROS

## 41.46 Obrigatoriedade

Toda exceção deverá possuir tratamento apropriado.

Nunca permitir falhas silenciosas.

---

## 41.47 Mensagens

Mensagens apresentadas ao usuário deverão ser compreensíveis e não expor detalhes técnicos.

---

## 41.48 Logs

Erros técnicos deverão ser registrados conforme a Seção de Logs Técnicos.

---

## 41.49 Recuperação

Sempre que possível, o sistema deverá permitir recuperação segura após falhas.

---

## 41.50 Integridade

Falhas nunca deverão comprometer a integridade dos dados persistidos.

---

# AUDITORIA

## 41.51 Integração

Toda funcionalidade que alterar informações deverá respeitar integralmente as regras da Seção de Auditoria.

---

## 41.52 Eventos

Eventos auditáveis deverão ser registrados automaticamente.

---

## 41.53 Usuário

Sempre que aplicável, a Auditoria deverá identificar:

- usuário;
- Loja;
- data;
- hora;
- operação.

---

## 41.54 Integridade

Registros de Auditoria não poderão ser modificados pelas funcionalidades comuns do sistema.

---

## 41.55 Consistência

A ausência de Auditoria em uma operação obrigatória deverá ser considerada defeito de implementação.

---

# LOGS TÉCNICOS

## 41.56 Integração

Todo módulo deverá respeitar integralmente a Seção de Logs Técnicos.

---

## 41.57 Falhas

Exceções relevantes deverão gerar Log Técnico.

---

## 41.58 Diagnóstico

Os Logs deverão conter informações suficientes para análise técnica.

---

## 41.59 Segurança

Logs nunca deverão expor:

- senhas;
- tokens;
- segredos;
- informações sensíveis.

---

## 41.60 Continuidade

A geração de Logs não deverá impedir o funcionamento normal da aplicação, salvo quando a própria falha impossibilitar a continuidade da operação.

---

# SEGURANÇA

## 41.61 Conformidade

Todo módulo deverá cumprir integralmente as regras da Seção de Segurança.

---

## 41.62 Autenticação

Toda operação protegida deverá validar autenticação.

---

## 41.63 Autorização

Toda operação protegida deverá validar autorização.

---

## 41.64 Isolamento

Toda implementação deverá preservar o isolamento completo entre Lojas.

---

## 41.65 Backend

Nenhuma decisão crítica de segurança poderá depender exclusivamente do frontend.

---

# PERFORMANCE

## 41.66 Conformidade

Todo módulo deverá cumprir integralmente as regras da Seção de Performance.

---

## 41.67 Consultas

Consultas deverão retornar apenas os dados necessários.

---

## 41.68 Paginação

Listagens deverão utilizar paginação oficial.

---

## 41.69 Índices

Consultas frequentes deverão considerar os índices definidos para o banco de dados.

---

## 41.70 Escalabilidade

Novas funcionalidades deverão preservar a escalabilidade do sistema.

---

# DOCUMENTAÇÃO

## 41.71 Obrigatoriedade

Toda funcionalidade implementada deverá permanecer compatível com a documentação oficial.

---

## 41.72 Atualização

Quando houver alteração de comportamento funcional, a documentação correspondente deverá ser revisada.

---

## 41.73 Glossário

A documentação deverá utilizar os termos definidos no Glossário Oficial.

---

## 41.74 Consistência

A documentação nunca deverá contradizer o comportamento implementado.

---

## 41.75 Rastreabilidade

Sempre que possível deverá existir rastreabilidade entre:

- requisito;
- regra de negócio;
- implementação;
- teste.

---

# TESTABILIDADE

## 41.76 Testabilidade

Toda regra de negócio deverá ser implementada de forma que possa ser testada.

---

## 41.77 Isolamento

Regras de negócio deverão poder ser testadas independentemente da interface gráfica.

---

## 41.78 Regressão

Alterações em regras compartilhadas deverão considerar impacto sobre funcionalidades existentes.

---

## 41.79 Consistência

Os testes deverão validar exatamente o comportamento definido pelo BUSINESS_RULES.md.

---

## 41.80 Evolução

Novas funcionalidades deverão possuir testes compatíveis com sua complexidade e criticidade.

# EVOLUÇÃO

## 41.81 Evolução contínua

O sistema deverá permitir evolução contínua sem comprometer as regras de negócio já aprovadas.

---

## 41.82 Novos módulos

Todo novo módulo deverá obedecer automaticamente:

- BUSINESS_RULES.md;
- Glossário Oficial;
- Convenções Gerais;
- Segurança;
- Auditoria;
- Logs;
- Performance;
- APIs;
- Migrações.

---

## 41.83 Novas funcionalidades

Toda nova funcionalidade deverá integrar-se aos padrões existentes.

Não deverão existir exceções sem justificativa formal.

---

## 41.84 Compatibilidade

Alterações futuras deverão preservar compatibilidade funcional sempre que possível.

---

## 41.85 Refatorações

Refatorações deverão preservar integralmente o comportamento funcional aprovado.

Quando houver mudança funcional, ela deverá ser documentada e aprovada previamente.

---

# MANUTENÇÃO

## 41.86 Legibilidade

O código deverá priorizar clareza e facilidade de manutenção.

---

## 41.87 Simplicidade

Sempre que houver duas soluções funcionalmente equivalentes, deverá ser preferida a mais simples e compreensível.

---

## 41.88 Complexidade

Complexidade desnecessária deverá ser evitada.

---

## 41.89 Responsabilidade

Cada componente deverá possuir responsabilidade claramente definida.

---

## 41.90 Organização

A organização da implementação deverá facilitar futuras evoluções sem necessidade de grandes refatorações.

---

# GOVERNANÇA

## 41.91 Revisões

Toda alteração relevante deverá ser revisada antes de sua incorporação definitiva.

---

## 41.92 Consistência

Nenhuma implementação poderá contrariar o BUSINESS_RULES.md.

---

## 41.93 Atualizações

Sempre que uma regra de negócio for alterada, sua implementação correspondente deverá ser atualizada.

---

## 41.94 Sincronização

A documentação oficial e a implementação deverão permanecer sincronizadas.

---

## 41.95 Histórico

Toda alteração relevante nas regras deverá ser registrada no histórico oficial do projeto.

---

# QUALIDADE

## 41.96 Confiabilidade

Toda implementação deverá priorizar confiabilidade antes de otimizações prematuras.

---

## 41.97 Integridade

A preservação da integridade dos dados terá prioridade sobre desempenho quando houver conflito entre ambos.

---

## 41.98 Segurança

Nenhuma otimização poderá reduzir os requisitos mínimos de segurança estabelecidos pelo sistema.

---

## 41.99 Rastreabilidade

Toda operação relevante deverá permanecer rastreável conforme as regras de Auditoria e Logs.

---

## 41.100 Padronização

Todas as implementações deverão seguir padrões consistentes em nomenclatura, comportamento e organização.

---

# REGRAS GERAIS

## 41.101 Regras gerais de Desenvolvimento

Todo desenvolvimento do sistema deverá:

- respeitar integralmente o BUSINESS_RULES.md;
- considerar o backend como fonte autoritativa;
- utilizar o frontend apenas para apresentação e experiência do usuário;
- centralizar regras de negócio compartilhadas;
- evitar duplicação de lógica;
- utilizar serviços reutilizáveis;
- manter baixo acoplamento entre módulos;
- manter alta coesão;
- centralizar configurações;
- evitar números mágicos;
- tratar todas as exceções;
- integrar-se obrigatoriamente à Auditoria;
- integrar-se obrigatoriamente aos Logs Técnicos;
- cumprir integralmente as regras de Segurança;
- cumprir integralmente as regras de Performance;
- manter documentação atualizada;
- utilizar nomenclatura consistente com o Glossário Oficial;
- implementar funcionalidades testáveis;
- preservar compatibilidade funcional;
- preservar integridade dos dados;
- preservar rastreabilidade;
- facilitar manutenção;
- permitir evolução contínua;
- aplicar automaticamente estas regras a todos os módulos futuros.

---

## 41.102 Hierarquia das especificações

Na implementação do sistema, deverá ser observada a seguinte ordem de precedência:

1. BUSINESS_RULES.md;
2. Regras específicas do módulo;
3. Convenções Gerais do Sistema;
4. Glossário Oficial;
5. Demais documentos oficiais do projeto.

Nenhuma decisão técnica poderá contrariar uma regra de negócio oficialmente aprovada.

---

## 41.103 Resolução de conflitos

Quando houver conflito entre uma decisão técnica e uma regra funcional, deverá prevalecer a regra funcional.

Caso a implementação técnica não consiga atender à regra de negócio, a especificação deverá ser revisada formalmente antes da alteração do comportamento do sistema.

---

## 41.104 Aplicação

As regras desta seção aplicam-se a:

- desenvolvimento inicial;
- correções;
- melhorias;
- refatorações;
- integrações;
- novos módulos;
- futuras versões do sistema.

---

## 41.105 Encerramento

A Seção Regras Gerais de Desenvolvimento estabelece os princípios obrigatórios que deverão orientar toda implementação do sistema.

Seu objetivo é garantir que a evolução tecnológica preserve integralmente as regras de negócio, a consistência funcional, a segurança, a integridade dos dados e a qualidade geral da aplicação.

# 42. CRITÉRIOS DE ACEITE E QUALIDADE

## 42.1 Finalidade

Esta seção estabelece os critérios mínimos obrigatórios para que qualquer funcionalidade seja considerada concluída.

Nenhuma implementação poderá ser considerada pronta apenas porque executa corretamente sua função principal.

---

## 42.2 Objetivos

Os Critérios de Aceite e Qualidade têm como objetivos:

- garantir conformidade funcional;
- garantir qualidade técnica;
- reduzir regressões;
- preservar integridade dos dados;
- garantir segurança;
- assegurar padronização;
- estabelecer critérios objetivos para homologação.

---

## 42.3 Aplicação

Esta seção aplica-se a:

- novos módulos;
- novas funcionalidades;
- melhorias;
- correções;
- integrações;
- refatorações;
- evoluções futuras.

---

## 42.4 Obrigatoriedade

Todo desenvolvimento deverá atender integralmente aos critérios desta seção.

---

## 42.5 Aprovação

Uma funcionalidade somente poderá ser considerada concluída quando atender simultaneamente todos os critérios definidos nesta seção.

---

# IMPLEMENTAÇÃO

## 42.6 Regras de negócio

Toda funcionalidade deverá implementar integralmente as regras de negócio aplicáveis.

---

## 42.7 Implementação parcial

Não será permitido considerar concluída uma funcionalidade parcialmente implementada.

---

## 42.8 Consistência

A implementação deverá produzir exatamente o comportamento definido pelo BUSINESS_RULES.md.

---

## 42.9 Compatibilidade

A implementação não poderá contrariar regras previamente aprovadas.

---

## 42.10 Integridade

Toda implementação deverá preservar a integridade dos dados existentes.

---

# TESTES

## 42.11 Testes obrigatórios

Toda funcionalidade deverá ser submetida a testes antes da homologação.

---

## 42.12 Casos de sucesso

Os testes deverão validar os fluxos normais de utilização.

---

## 42.13 Casos de erro

Os testes deverão validar cenários de erro previsíveis.

---

## 42.14 Limites

Sempre que aplicável deverão ser testados:

- valores mínimos;
- valores máximos;
- limites operacionais;
- entradas inválidas.

---

## 42.15 Regressão

Sempre que houver alteração funcional deverão ser executados testes de regressão.

---

## 42.16 Regras compartilhadas

Alterações em regras compartilhadas deverão validar todos os módulos impactados.

---

## 42.17 Reprodutibilidade

Os testes deverão produzir resultados consistentes quando executados novamente nas mesmas condições.

---

## 42.18 Cobertura

Toda regra de negócio relevante deverá possuir ao menos um cenário de validação.

---

## 42.19 Correções

A correção de um defeito deverá incluir teste que impeça sua recorrência.

---

## 42.20 Aprovação

Os testes deverão ser considerados aprovados antes da homologação da funcionalidade.

---

# VALIDAÇÕES

## 42.21 Campos obrigatórios

Todos os campos obrigatórios deverão ser corretamente validados.

---

## 42.22 Dados inválidos

Entradas inválidas deverão ser rejeitadas conforme as regras oficiais.

---

## 42.23 Consistência

As validações deverão produzir resultados consistentes em qualquer interface utilizada.

---

## 42.24 Backend

Toda validação crítica deverá ocorrer obrigatoriamente no backend.

---

## 42.25 Frontend

Validações do frontend possuem finalidade exclusivamente auxiliar.

Nunca substituirão a validação oficial do backend.

---

# INTEGRIDADE

## 42.26 Preservação

A funcionalidade nunca poderá comprometer a integridade das informações já existentes.

---

## 42.27 Relacionamentos

Todos os relacionamentos entre entidades deverão permanecer consistentes após qualquer operação.

---

## 42.28 Transações

Operações que envolvam múltiplas alterações relacionadas deverão preservar consistência conforme as regras oficiais.

---

## 42.29 Cancelamentos

Cancelamentos deverão restaurar corretamente os efeitos previstos pelas regras do módulo correspondente.

---

## 42.30 Recuperação

Sempre que possível, falhas deverão permitir recuperação segura sem perda indevida de informações.

---

# CRITÉRIOS FUNCIONAIS

## 42.31 Interface

A interface deverá refletir corretamente o estado real da operação.

---

## 42.32 Mensagens

Mensagens deverão ser claras, objetivas e compatíveis com o Glossário Oficial.

---

## 42.33 Navegação

A navegação entre telas deverá permanecer consistente após a implementação.

---

## 42.34 Fluxos

Todos os fluxos previstos nas regras de negócio deverão funcionar corretamente.

---

## 42.35 Fluxos alternativos

Sempre que existirem fluxos alternativos previstos, eles também deverão ser validados.

---

## 42.36 Estados

Todos os estados possíveis da entidade deverão ser corretamente tratados.

---

## 42.37 Situações

As situações operacionais deverão permanecer coerentes durante todo o ciclo de vida da funcionalidade.

---

## 42.38 Compatibilidade entre módulos

A implementação não deverá produzir comportamento diferente entre módulos equivalentes.

---

## 42.39 Experiência do usuário

A funcionalidade deverá manter comportamento consistente com o restante da aplicação.

---

## 42.40 Conclusão funcional

Somente após o atendimento de todos os critérios desta Parte 1 a funcionalidade poderá prosseguir para as validações técnicas descritas nas partes seguintes desta seção.

# SEGURANÇA

## 42.41 Conformidade

Toda funcionalidade deverá cumprir integralmente as regras estabelecidas na Seção de Segurança.

---

## 42.42 Autenticação

Toda operação protegida deverá validar corretamente a autenticação do Usuário.

---

## 42.43 Autorização

Toda operação protegida deverá validar as permissões do Usuário antes de sua execução.

---

## 42.44 Isolamento entre Lojas

Toda funcionalidade deverá comprovar que respeita integralmente o isolamento entre Lojas.

Nenhuma informação poderá ser acessada por Loja diferente da proprietária.

---

## 42.45 Dados sensíveis

Informações sensíveis nunca deverão ser expostas ao usuário sem necessidade funcional.

---

# AUDITORIA

## 42.46 Integração obrigatória

Toda funcionalidade que altere dados deverá obedecer às regras da Seção de Auditoria.

---

## 42.47 Registro

As operações auditáveis deverão registrar automaticamente:

- usuário;
- Loja;
- data;
- hora;
- operação realizada;
- entidade afetada.

---

## 42.48 Integridade

Os registros de Auditoria deverão permanecer íntegros após a conclusão da operação.

---

## 42.49 Validação

Durante a homologação deverá ser confirmado que todos os eventos obrigatórios geram Auditoria.

---

## 42.50 Defeito

A ausência de Auditoria em operação obrigatória deverá impedir a aprovação da funcionalidade.

---

# LOGS TÉCNICOS

## 42.51 Integração

Toda funcionalidade deverá obedecer às regras da Seção de Logs Técnicos.

---

## 42.52 Exceções

Falhas relevantes deverão gerar Logs Técnicos apropriados.

---

## 42.53 Diagnóstico

Os Logs deverão conter informações suficientes para investigação técnica.

---

## 42.54 Segurança

Logs não poderão registrar:

- senhas;
- tokens;
- segredos;
- informações confidenciais.

---

## 42.55 Validação

Durante a homologação deverá ser confirmado que os Logs Técnicos estão sendo gerados corretamente.

---

# PERFORMANCE

## 42.56 Conformidade

Toda funcionalidade deverá atender aos requisitos definidos na Seção de Performance.

---

## 42.57 Tempo de resposta

A implementação deverá apresentar desempenho compatível com a operação executada.

---

## 42.58 Paginação

Listagens deverão utilizar obrigatoriamente a paginação oficial do sistema.

---

## 42.59 Consultas

Consultas deverão retornar apenas as informações necessárias para cada operação.

---

## 42.60 Escalabilidade

A implementação não deverá comprometer a escalabilidade do sistema.

---

# DOCUMENTAÇÃO

## 42.61 Atualização

Sempre que houver alteração funcional, a documentação correspondente deverá ser atualizada.

---

## 42.62 Consistência

A documentação deverá permanecer compatível com a implementação.

---

## 42.63 Glossário

A documentação deverá utilizar exclusivamente a terminologia oficial do Glossário.

---

## 42.64 Versionamento

Alterações relevantes deverão ser registradas no histórico oficial do projeto.

---

## 42.65 Revisão

A documentação deverá ser revisada antes da homologação da funcionalidade.

---

# HOMOLOGAÇÃO

## 42.66 Ambiente

Toda funcionalidade deverá ser validada em ambiente de homologação antes da Produção.

---

## 42.67 Aprovação

Somente funcionalidades aprovadas poderão seguir para Produção.

---

## 42.68 Cenários

A homologação deverá contemplar:

- fluxo principal;
- fluxos alternativos;
- cenários de erro;
- permissões;
- integrações;
- concorrência, quando aplicável.

---

## 42.69 Correções

Caso sejam encontrados defeitos durante a homologação, estes deverão ser corrigidos antes da liberação.

---

## 42.70 Nova validação

Após correções relevantes deverá ser realizada nova homologação.

---

# PRODUÇÃO

## 42.71 Liberação

Somente funcionalidades homologadas poderão ser disponibilizadas em Produção.

---

## 42.72 Integridade

A implantação não poderá comprometer dados já existentes.

---

## 42.73 Compatibilidade

A implantação deverá preservar compatibilidade com funcionalidades já aprovadas.

---

## 42.74 Migrações

Quando houver alterações estruturais, deverão ser utilizadas exclusivamente as Migrations oficiais.

---

## 42.75 Monitoramento

Após a implantação deverá ser realizado acompanhamento inicial para identificação de possíveis comportamentos inesperados.

---

# CHECKLIST TÉCNICO

## 42.76 Implementação

Confirmar que todas as regras de negócio foram implementadas.

---

## 42.77 Segurança

Confirmar autenticação, autorização e isolamento entre Lojas.

---

## 42.78 Auditoria

Confirmar geração correta dos registros de Auditoria.

---

## 42.79 Logs

Confirmar geração correta dos Logs Técnicos.

---

## 42.80 Documentação

Confirmar atualização da documentação oficial antes da conclusão da funcionalidade.

# GOVERNANÇA DA QUALIDADE

## 42.81 Responsabilidade

A qualidade do sistema é responsabilidade de todo o processo de desenvolvimento.

Nenhuma funcionalidade deverá ser considerada concluída sem atender aos critérios estabelecidos nesta seção.

---

## 42.82 Evidências

Sempre que possível deverão existir evidências objetivas da aprovação da funcionalidade.

Exemplos:

- testes executados;
- registros de homologação;
- validações documentadas;
- aprovação formal.

---

## 42.83 Critérios objetivos

A aprovação de uma funcionalidade deverá basear-se em critérios objetivos.

Nunca apenas na percepção subjetiva de que "está funcionando".

---

## 42.84 Defeitos

Todo defeito identificado durante homologação deverá ser:

- registrado;
- classificado;
- corrigido;
- validado novamente.

---

## 42.85 Rastreabilidade

Toda funcionalidade deverá possuir rastreabilidade entre:

- requisito;
- regra de negócio;
- implementação;
- testes;
- homologação.

---

# QUALIDADE FUNCIONAL

## 42.86 Conformidade

A funcionalidade deverá apresentar exatamente o comportamento definido no BUSINESS_RULES.md.

---

## 42.87 Consistência

O comportamento deverá permanecer consistente em todas as interfaces oficiais.

---

## 42.88 Previsibilidade

O sistema deverá responder de maneira previsível em todos os cenários previstos.

---

## 42.89 Robustez

Entradas inválidas nunca deverão comprometer a estabilidade da aplicação.

---

## 42.90 Confiabilidade

A funcionalidade deverá operar corretamente durante uso contínuo.

---

# CHECKLIST FINAL

## 42.91 Implementação

Confirmar que todas as regras de negócio foram implementadas.

---

## 42.92 Testes

Confirmar aprovação dos testes previstos.

---

## 42.93 Segurança

Confirmar conformidade com a Seção de Segurança.

---

## 42.94 Auditoria

Confirmar geração correta da Auditoria quando aplicável.

---

## 42.95 Logs Técnicos

Confirmar geração correta dos Logs Técnicos.

---

## 42.96 Performance

Confirmar conformidade com a Seção de Performance.

---

## 42.97 Documentação

Confirmar atualização da documentação oficial.

---

## 42.98 Homologação

Confirmar aprovação formal em ambiente de homologação.

---

## 42.99 Produção

Confirmar que todos os critérios obrigatórios foram atendidos antes da implantação em Produção.

---

## 42.100 Aceite

Somente após o atendimento integral deste checklist a funcionalidade poderá ser considerada oficialmente concluída.

---

# REGRAS GERAIS

## 42.101 Regras gerais dos Critérios de Aceite e Qualidade

Toda funcionalidade deverá:

- implementar integralmente as regras de negócio;
- preservar a integridade dos dados;
- passar por testes obrigatórios;
- validar cenários de sucesso;
- validar cenários de erro;
- validar limites operacionais;
- executar testes de regressão quando aplicável;
- validar todas as regras compartilhadas impactadas;
- validar corretamente todos os campos;
- realizar validações críticas no backend;
- respeitar integralmente a Seção de Segurança;
- respeitar integralmente a Seção de Auditoria;
- respeitar integralmente a Seção de Logs Técnicos;
- respeitar integralmente a Seção de Performance;
- manter documentação atualizada;
- utilizar a terminologia oficial do Glossário;
- ser homologada antes da Produção;
- preservar compatibilidade com funcionalidades existentes;
- utilizar exclusivamente Migrations oficiais quando houver alterações estruturais;
- ser monitorada após implantação;
- atender ao checklist final desta seção.

---

## 42.102 Critério oficial de conclusão

Uma funcionalidade somente será considerada oficialmente concluída quando atender simultaneamente a:

- regras de negócio;
- testes;
- validações;
- segurança;
- auditoria;
- logs técnicos;
- performance;
- documentação;
- homologação;
- critérios desta seção.

---

## 42.103 Não conformidade

Qualquer descumprimento de um critério obrigatório impedirá a aprovação da funcionalidade até sua regularização.

---

## 42.104 Evolução

Novos critérios de qualidade poderão ser adicionados futuramente, desde que não reduzam o nível mínimo de qualidade estabelecido nesta seção.

---

## 42.105 Encerramento

A Seção Critérios de Aceite e Qualidade estabelece o padrão oficial para aprovação de funcionalidades do sistema.

Seu objetivo é garantir que toda entrega preserve as regras de negócio, a segurança, a integridade, a rastreabilidade, a qualidade técnica e a consistência funcional antes de sua disponibilização aos usuários.

# 43. ENCERRAMENTO OFICIAL DO BUSINESS_RULES.md

## 43.1 Finalidade

Esta seção estabelece o encerramento oficial do BUSINESS_RULES.md e define sua autoridade como documento funcional principal do sistema.

---

## 43.2 Objetivo

O objetivo desta seção é:

- consolidar a especificação funcional;
- definir sua governança;
- estabelecer regras para futuras revisões;
- garantir evolução controlada da documentação;
- preservar a consistência das regras de negócio.

---

## 43.3 Escopo

O BUSINESS_RULES.md contempla todas as regras funcionais aprovadas para o sistema até sua versão oficial.

Todas as futuras evoluções deverão respeitar esta base.

---

## 43.4 Documento oficial

O BUSINESS_RULES.md constitui o documento oficial das regras de negócio do sistema.

Nenhum outro documento poderá alterar ou substituir regras funcionais sem revisão formal deste documento.

---

## 43.5 Autoridade

Toda decisão funcional deverá utilizar o BUSINESS_RULES.md como referência principal.

Sempre que houver dúvida sobre comportamento esperado, prevalecerá este documento.

---

# HIERARQUIA DOCUMENTAL

## 43.6 Ordem de precedência

Os documentos oficiais do projeto deverão obedecer à seguinte ordem de precedência:

1. BUSINESS_RULES.md
2. DATABASE.md
3. ARCHITECTURE.md
4. UI_UX.md
5. Demais documentos oficiais.

---

## 43.7 Conflitos

Quando houver conflito entre documentos, prevalecerá o documento de maior precedência.

---

## 43.8 Implementação

A implementação do sistema deverá respeitar integralmente esta hierarquia.

---

## 43.9 Decisões técnicas

Nenhuma decisão técnica poderá modificar regras de negócio oficialmente aprovadas.

---

## 43.10 Revisão obrigatória

Quando uma decisão técnica exigir alteração funcional, o BUSINESS_RULES.md deverá ser revisado antes da implementação.

---

# EVOLUÇÃO

## 43.11 Evolução contínua

O BUSINESS_RULES.md deverá evoluir continuamente juntamente com o sistema.

---

## 43.12 Inclusões

Toda nova funcionalidade deverá ser documentada antes de sua implementação definitiva.

---

## 43.13 Alterações

Toda alteração funcional deverá ser registrada oficialmente neste documento.

---

## 43.14 Remoções

Nenhuma regra poderá ser removida sem revisão formal.

---

## 43.15 Compatibilidade

Sempre que possível, novas versões deverão preservar compatibilidade com as regras anteriormente aprovadas.

---

# HISTÓRICO

## 43.16 Registro

Toda alteração relevante deverá ser registrada no histórico oficial de versões.

---

## 43.17 Versionamento

Cada versão deverá possuir:

- número;
- data;
- descrição resumida;
- responsável pela revisão, quando aplicável.

---

## 43.18 Rastreabilidade

Toda alteração deverá permanecer rastreável.

---

## 43.19 Revisões

Revisões nunca deverão apagar o histórico das versões anteriores.

---

## 43.20 Transparência

O histórico deverá permitir compreender claramente a evolução da especificação.

---

# GOVERNANÇA

## 43.21 Revisão formal

Toda alteração funcional deverá passar por revisão formal antes de tornar-se oficial.

---

## 43.22 Aprovação

Somente regras aprovadas integrarão o BUSINESS_RULES.md.

---

## 43.23 Consistência

Novas regras deverão preservar consistência com as regras já existentes.

---

## 43.24 Conflitos

Quando uma nova regra gerar conflito com regra anterior, a revisão deverá resolver explicitamente a divergência.

---

## 43.25 Glossário

Toda nova terminologia deverá ser incorporada ao Glossário Oficial.

---

# APLICAÇÃO

## 43.26 Desenvolvimento

Toda implementação deverá respeitar integralmente este documento.

---

## 43.27 Testes

Todos os testes deverão utilizar o BUSINESS_RULES.md como referência funcional.

---

## 43.28 Homologação

Toda homologação deverá validar conformidade com este documento.

---

## 43.29 Produção

Nenhuma funcionalidade poderá ser considerada oficialmente concluída quando contrariar regras desta especificação.

---

## 43.30 Evolução futura

Todas as futuras versões do sistema deverão preservar os princípios estabelecidos neste documento.

---

# MANUTENÇÃO

## 43.31 Revisões periódicas

Sempre que necessário deverão ser realizadas revisões gerais da especificação.

---

## 43.32 Qualidade documental

A documentação deverá permanecer:

- atualizada;
- consistente;
- organizada;
- rastreável.

---

## 43.33 Duplicidades

Durante revisões deverão ser eliminadas regras duplicadas sempre que isso não comprometer a clareza.

---

## 43.34 Referências

As referências entre seções deverão permanecer válidas.

---

## 43.35 Numeração

A numeração oficial deverá permanecer consistente após futuras revisões.

---

# VERSÃO OFICIAL

## 43.36 Versão

Versão inicial oficial:

1.0

---

## 43.37 Situação

Status:

Oficial.

---

## 43.38 Condição

Situação da especificação:

Aprovada para desenvolvimento.

---

## 43.39 Validade

Esta especificação permanecerá válida até publicação oficial de versão posterior.

---

## 43.40 Continuidade

Versões futuras deverão manter compatibilidade documental sempre que possível.

---

# DECLARAÇÃO OFICIAL

## 43.41 Declaração

O BUSINESS_RULES.md constitui a especificação funcional oficial do sistema.

Todas as implementações, testes, homologações, integrações, documentações, evoluções e futuras versões deverão observar integralmente as regras aqui estabelecidas.

---

## 43.42 Fonte funcional

Este documento representa a fonte oficial das regras de negócio.

---

## 43.43 Obrigatoriedade

Toda equipe envolvida no desenvolvimento deverá utilizar este documento como referência obrigatória.

---

## 43.44 Objetivo permanente

Seu objetivo é garantir:

- consistência;
- integridade;
- segurança;
- rastreabilidade;
- qualidade;
- previsibilidade;
- evolução controlada.

---

## 43.45 Encerramento

Com a conclusão desta seção considera-se oficialmente encerrada a versão 1.0 do BUSINESS_RULES.md.

Esta especificação passa a constituir a referência funcional oficial para todo o ciclo de vida do sistema, abrangendo análise, desenvolvimento, testes, homologação, implantação, manutenção e evolução futura.


# RETIFICAÇÃO OFICIAL Nº 001
## Alteração das Regras de Cartão de Crédito
### BUSINESS_RULES.md

**Versão da Retificação:** 1.0.1

**Data:** ___/___/____

---

# 1. Finalidade

Esta Retificação Oficial altera as regras referentes às modalidades de Cartão de Crédito, configuração de taxas, histórico de vigência e parcelamento das vendas.

As regras desta Retificação prevalecem sobre quaisquer regras anteriores incompatíveis.

---

# 2. Crediário da Loja

Permanecem inalteradas todas as regras do módulo Crediário.

O Crediário continua limitado a:

- máximo de 3 (três) parcelas;
- utilização do Limite de Crédito do Cliente;
- geração de parcelas próprias;
- recebimentos próprios;
- vencimentos próprios.

O Cartão de Crédito não utiliza as regras do Crediário.

---

# 3. Cartão de Crédito

O Cartão de Crédito passa a permitir parcelamento em:

- Crédito 1x;
- Crédito 2x;
- Crédito 3x;
- Crédito 4x;
- Crédito 5x;
- Crédito 6x;
- Crédito 7x;
- Crédito 8x;
- Crédito 9x;
- Crédito 10x.

O limite máximo oficial passa a ser de **10 parcelas**.

---

# 4. Modalidades de Cartão

As modalidades oficiais passam a ser:

- Débito;
- Crédito 1x;
- Crédito 2x;
- Crédito 3x;
- Crédito 4x;
- Crédito 5x;
- Crédito 6x;
- Crédito 7x;
- Crédito 8x;
- Crédito 9x;
- Crédito 10x.

---

# 5. Configuração das Modalidades

Cada modalidade possuirá configuração independente.

Cada configuração deverá conter:

- Modalidade;
- Situação (Ativa/Inativa);
- Taxa percentual;
- Prazo de recebimento;
- Data/Hora de início da vigência;
- Data/Hora de fim da vigência (quando substituída).

---

# 6. Situação da Modalidade

Cada modalidade poderá estar:

- Ativa;
- Inativa.

Somente modalidades Ativas poderão ser utilizadas em novas Vendas.

Modalidades Inativas permanecerão cadastradas para fins históricos.

---

# 7. Taxas

Cada modalidade possuirá sua própria taxa.

Exemplo:

- Débito;
- Crédito 1x;
- Crédito 2x;
- Crédito 3x;
- Crédito 4x;
- Crédito 5x;
- Crédito 6x;
- Crédito 7x;
- Crédito 8x;
- Crédito 9x;
- Crédito 10x.

Será permitido cadastrar taxa igual a **0,00%**.

---

# 8. Prazo de Recebimento

Cada modalidade possuirá prazo próprio de recebimento.

Na implantação inicial todas utilizarão:

**1 (um) dia.**

O prazo poderá ser alterado futuramente pelo Administrador.

---

# 9. Histórico de Vigência

Toda alteração de:

- Taxa;
- Prazo;
- Situação da Modalidade;

deverá preservar histórico.

Cada alteração criará uma nova vigência.

A configuração anterior jamais será perdida.

---

# 10. Venda

Durante a Venda deverão ser apresentados:

Forma de pagamento:

Cartão

Modalidade:

- Débito;
- Crédito.

Parcelamento:

- 1x até 10x.

Somente modalidades Ativas deverão aparecer para seleção.

---

# 11. Snapshot

Ao concluir uma Venda em Cartão o sistema deverá gravar, obrigatoriamente:

- Modalidade;
- Quantidade de parcelas;
- Taxa aplicada;
- Prazo aplicado;
- Valor bruto;
- Valor da taxa;
- Valor líquido esperado.

Essas informações serão imutáveis.

---

# 12. Recebíveis

Independentemente da quantidade de parcelas escolhida pelo Cliente:

- Crédito 1x;
- Crédito 2x;
- ...
- Crédito 10x;

o sistema continuará gerando apenas **um Recebível**, em razão da política de antecipação da Loja.

---

# 13. Relatórios

Os Relatórios deverão permitir filtros por:

- Modalidade;
- Quantidade de parcelas;
- Taxa aplicada;
- Valor bruto;
- Valor líquido;
- Valor da taxa.

---

# 14. Dashboard

Os Dashboards poderão apresentar indicadores por:

- Modalidade;
- Quantidade de parcelas;
- Valor vendido;
- Custo financeiro;
- Valor líquido esperado.

---

# 15. Auditoria

Toda alteração nas configurações deverá registrar:

- Modalidade;
- Situação anterior;
- Situação nova;
- Taxa anterior;
- Nova taxa;
- Prazo anterior;
- Novo prazo;
- Usuário;
- Loja;
- Data;
- Hora.

---

# 16. Segurança

Somente usuários com perfil Administrador poderão:

- cadastrar taxas;
- alterar taxas;
- ativar modalidades;
- desativar modalidades;
- alterar prazos.

Operadores utilizarão apenas as modalidades disponíveis.

---

# 17. Histórico das Taxas

O sistema deverá manter histórico permanente de todas as alterações de taxas.

Cada registro histórico deverá apresentar:

- Período de vigência;
- Modalidade;
- Taxa;
- Prazo;
- Situação;
- Usuário responsável.

O histórico nunca poderá ser apagado pelas rotinas normais do sistema.

---

# 18. Revogação

Ficam revogadas todas as regras anteriormente descritas no BUSINESS_RULES.md que:

- limitavam o Cartão de Crédito a 3 parcelas;
- permitiam configuração apenas para Crédito 1x, 2x e 3x;
- utilizavam a ausência de taxa como único mecanismo de habilitação das modalidades.

Todas as demais regras permanecem integralmente válidas.

---

# 19. Vigência

Esta Retificação entra em vigor imediatamente e deverá ser considerada complementar ao BUSINESS_RULES.md até a publicação da Versão 1.1 consolidada.

TERMO DE APROVAÇÃO DA VERSÃO 1.0

Declara-se aprovada a versão 1.0 da Especificação Funcional e das Regras de Negócio do ERP MOVA SPORTS.

Esta documentação passa a constituir a referência oficial para:

desenvolvimento;
correção do sistema existente;
testes;
homologação;
implantação;
treinamento;
manutenção;
futuras evoluções.

Qualquer comportamento do sistema que seja incompatível com as regras aprovadas deverá ser tratado como divergência de implementação, salvo alteração formal posterior desta especificação.

Versão aprovada: 1.0
Data: 17 de julho de 2026
Status: OFICIAL — APROVADA PARA IMPLEMENTAÇÃO

Responsável pela aprovação:

MOVA SPORTS

---

# EVIDENCIA DE IMPLEMENTACAO - ETAPA 10

O modulo Crediario foi consolidado na Etapa 10 com as seguintes evidencias:

- novas vendas exigem cliente identificado, ativo e nao padrao;
- o parcelamento e limitado a tres parcelas;
- os vencimentos seguem recorrencia mensal pelo dia-base confirmado;
- excesso de limite exige autorizacao explicita e gera historico da elevacao;
- recebimentos podem ser totais, parciais ou antecipados;
- descontos por valor ou percentual nao podem gerar saldo negativo;
- desconto que zera o saldo encerra a parcela;
- juros, multa e acrescimo dependem de informacao manual;
- Dinheiro e Pix entram imediatamente no Caixa;
- Debito e Credito geram recebivel bancario com snapshot da modalidade;
- renegociacao e operacao separada e preserva vencimentos e saldos historicos;
- recebimentos e renegociacoes sao idempotentes, auditados e transacionais.

A migration aditiva `v011_store_credit_business_rules` preserva os dados
existentes e adiciona os campos e a tabela necessarios para saldo aberto,
ajustes, idempotencia e historico de renegociacao. Ela nao foi executada em
banco operacional ou de producao durante a implementacao.

---

# EVIDENCIA DE IMPLEMENTACAO - ETAPA 13

O modulo Caixa e Financeiro foi consolidado na Etapa 13 com as seguintes
evidencias:

- o Caixa opera como saldo continuo, sem fechamento diario obrigatorio;
- saidas que tornariam o saldo negativo sao rejeitadas no backend;
- entradas manuais aceitam somente Dinheiro ou Pix;
- saidas manuais aceitam Dinheiro, Pix ou Debito e exigem categoria ativa;
- movimentos preservam origem, operador, timestamp e saldo resultante;
- correcoes sao feitas por movimento inverso vinculado, uma unica vez;
- recebimentos de Debito e Credito registram manualmente o valor efetivo;
- Contas a Pagar aceitam pagamento total, parcial e desconto integral;
- juros, multa e desconto dependem de informacao manual;
- pagamentos de Contas a Pagar podem ser estornados sem apagar historico;
- contas sem pagamento podem ser canceladas;
- recorrencias mensais geram no maximo uma ocorrencia por serie e mes;
- contas parcialmente pagas possuem edicao financeira restrita;
- contas pagas ou canceladas nao podem ser silenciosamente reeditadas;
- o cancelamento integral de Venda utiliza devolucao total vinculada;
- estoque e efeitos financeiros do cancelamento sao revertidos uma unica vez;
- operacoes criticas sao transacionais, idempotentes e auditadas.

A migration aditiva `v014_financial_ledger` amplia os movimentos financeiros e
as Contas a Pagar e adiciona pagamentos, eventos, recebimentos bancarios e
cancelamentos de Venda. Ela preserva os dados existentes e nao foi executada em
banco operacional ou de producao durante a implementacao.

---

# EVIDENCIA DE IMPLEMENTACAO - ETAPA 14

O modulo Conciliacao de Cartoes foi consolidado na Etapa 14 com as seguintes
evidencias:

- recebiveis de Debito e Credito preservam dados financeiros e comerciais;
- conciliacao individual aceita recebimento exato, parcial ou divergente;
- divergencia exige encerramento explicito e observacao;
- conciliacao em lote exige alocacao vinculada e soma igual ao valor recebido;
- cada conciliacao gera uma unica entrada financeira;
- pagamentos e itens permanecem vinculados ao agrupador e ao recebivel;
- alteracoes concorrentes sao bloqueadas por versao e saldo esperado;
- conciliacoes e estornos sao idempotentes;
- estorno reverte o agrupador completo, preserva historico e exige motivo;
- recebiveis, pagamentos, Caixa, espelho e auditoria compartilham a mesma
  transacao;
- registros estornados deixam de compor valores efetivamente recebidos;
- o endpoint bancario anterior rejeita novas baixas sem vinculo e preserva
  somente os registros historicos existentes.

A migration aditiva `v015_card_reconciliation` adiciona diferencas,
agrupadores, itens, vinculos de pagamento e dados de estorno. Ela preserva os
dados existentes e nao foi executada em banco operacional ou de producao
durante a implementacao.

---

# EVIDENCIA DE IMPLEMENTACAO - ETAPA 15

O modulo Catalogo e Documentos foi consolidado na Etapa 15 com as seguintes
evidencias:

- o Catalogo lista somente produtos ativos com estoque disponivel positivo;
- reservas de Condicionais ativos reduzem a disponibilidade;
- a interface informa `Disponivel` ou `Ultima unidade`, sem quantidade exata;
- custo, margem, estoque interno e dados financeiros nao sao enviados pela API
  do Catalogo;
- busca, filtros, ordenacao e detalhes sao processados pelo backend;
- a emissao do Catalogo revalida a consulta no servidor;
- etiquetas utilizam codigo Code128 real em SVG;
- comprovantes de Venda, Condicionais e Trocas preservam a operacao de origem;
- cada emissao registra snapshot, loja, usuario, data, formato, modelo,
  idempotencia e numero da via;
- segundas vias reutilizam o snapshot imutavel da emissao original;
- geracao e reimpressao nao alteram estoque, Caixa, recebiveis ou financeiro;
- as operacoes sao auditadas, isoladas por loja e transacionais.

A migration aditiva `v016_catalog_documents` cria a estrutura de documentos
gerados e seus indices. Ela preserva os dados existentes e nao foi executada
em banco operacional ou de producao durante a implementacao.

---

# EVIDENCIA DE IMPLEMENTACAO - ETAPA 16

O modulo Relatorios e Exportacoes foi consolidado na Etapa 16 com as seguintes
evidencias:

- existem relatorios de Vendas, Produtos Vendidos, Caixa, Crediario, Contas a
  Pagar, Estoque, Condicionais e Lucro;
- os periodos relativos e personalizados sao calculados no backend no fuso
  operacional `America/Sao_Paulo`;
- filtros e paginacao sao aplicados pelo servidor;
- Vendas canceladas nao compoem os totais validos;
- devolucoes reduzem quantidade, receita, custo e lucro na data da ocorrencia;
- pagamentos mistos preservam a composicao real da Venda;
- produtos vendidos utilizam snapshots historicos de marca, categoria,
  variacao, custo e valor praticado;
- o Estoque considera as reservas de Condicionais em aberto;
- contas antigas sem pagamentos relacionais preservam seus acumulados
  financeiros;
- Lucro e os valores financeiros restritos do Estoque sao protegidos no
  backend;
- exportacoes PDF e XLSX sao geradas no servidor com os filtros vigentes;
- exportacoes de Lucro sao auditadas sem gravar linhas do relatorio;
- a interface trata carregamento, erro, vazio, sucesso e nova tentativa;
- as consultas nao chamam `write_state()` nem `sync_business_tables()` e nao
  alteram dados operacionais.

Nenhuma migration foi necessaria ou executada nesta etapa. As novas
dependencias `openpyxl` e `reportlab` sao utilizadas somente para gerar XLSX e
PDF, respectivamente.
