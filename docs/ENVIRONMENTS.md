# Ambientes - Mova Sports

## Objetivo

Separar desenvolvimento, homologação e produção sem compartilhar bancos, credenciais, uploads ou permissões sensíveis.

## Ambientes reconhecidos

`APP_ENV` aceita exclusivamente:

- `development`;
- `staging`;
- `production`.

Enquanto a configuração obrigatória não for implantada, `APP_ENV` ausente ou inválida mantém a aplicação em modo compatível e restritivo. Esse modo não é considerado desenvolvimento e mantém todas as capacidades sensíveis desabilitadas.

## Matriz de configuração

| Configuração | Desenvolvimento | Homologação | Produção |
|---|---|---|---|
| `APP_ENV` | `development` | `staging` | `production` |
| Banco | SQLite ou PostgreSQL local | PostgreSQL separado com dados fictícios ou anonimizados | PostgreSQL exclusivo de produção |
| Segredos | Exclusivos do desenvolvimento | Exclusivos da homologação | Exclusivos da produção |
| Cloudinary | Conta ou pasta de desenvolvimento | Conta ou pasta de homologação | Conta ou pasta de produção |
| `MOVA_ALLOW_MIGRATIONS` | `false` por padrão | `false` por padrão | sempre sem capacidade efetiva nesta fase |
| `MOVA_ALLOW_DATA_IMPORT_RESET` | `false` por padrão | `false` por padrão | sempre sem capacidade efetiva nesta fase |

As flags sensíveis somente produzem capacidade efetiva em `development` ou `staging`. Em `production`, com `APP_ENV` ausente ou com valor inválido, permanecem desabilitadas mesmo quando a variável contém `true`.

Nesta fase, as capacidades são apenas centralizadas e diagnosticáveis. A aplicação delas às rotas de importação e reset pertence a uma tarefa posterior.

## Configuração manual no Railway

No serviço web de produção, configurar manualmente:

```text
APP_ENV=production
MOVA_ALLOW_MIGRATIONS=false
MOVA_ALLOW_DATA_IMPORT_RESET=false
```

Não substituir nem copiar entre ambientes:

- `DATABASE_URL`;
- `MOVA_SECRET_KEY`;
- `MOVA_ADMIN_PASSWORD`;
- credenciais do Cloudinary;
- demais tokens e segredos.

O código não modifica variáveis do Railway. Nenhum valor real deve ser gravado em arquivos versionados ou logs.

## Homologação

A homologação deve utilizar serviço, banco e credenciais próprios. Quando precisar representar produção, os dados devem ser fictícios ou anonimizados. Testes e migrations não devem utilizar o banco de produção.

## Importação WSGI

Importar `wsgi.py` apenas expõe a aplicação Flask. A importação não inicializa banco, não executa migrations, não cria backup e não altera dados. Inicializações de banco existentes continuam ocorrendo nos fluxos explícitos atuais e serão revistas separadamente.

## Endurecimento futuro

Uma fase posterior, dependente de autorização, poderá:

- tornar `APP_ENV` obrigatória;
- interromper o startup diante de ambiente inválido;
- ampliar validações de segredo, PostgreSQL e cookies seguros;
- aplicar as capacidades centralizadas às rotas sensíveis.
