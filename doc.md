# PMOrganizer - Documentacao Tecnica Completa

Este documento descreve a aplicacao PMOrganizer com foco tecnico, operacional e de manutencao. Ele foi atualizado a partir do codigo-fonte do repositorio.

> Nota de seguranca: este repositorio contem exemplos, valores default e documentos internos com credenciais. Nao replique tokens reais em documentos externos. Em producao, use apenas variaveis de ambiente seguras.

Ultima atualizacao: 29/01/2026

---

## 1) Visao geral

PMOrganizer e um sistema Django para gestao de projetos, consultores e operacoes financeiras. A aplicacao inclui:
- Area publica (site, candidatura e solicitacao de proposta).
- Area restrita (dashboards, cadastros, projetos, apontamentos, financeiro, tickets, conhecimento).
- API REST (Django REST Framework) para entidades principais.
- Integracoes externas: SeniorConnect (oportunidades), Brasil API (CNPJ), OpenAI (analise de projeto) e WhatsApp Z-API.
- Fluxos financeiros completos (contas a pagar/receber, faturamento, conciliacao bancaria com OFX, DRE).
- Controles de acesso por perfil (roles) e troca de senha obrigatoria no primeiro acesso.

---

## 2) Stack e dependencias

### Tecnologias principais
- Python 3.10+ (deploy configurado para 3.12)
- Django 5.2.6
- Django REST Framework 3.15.2
- Banco de dados: SQLite (dev) ou PostgreSQL via `DATABASE_URL` (prod)

### Dependencias do projeto (`requirements.txt`)
- Django==5.2.6
- djangorestframework==3.15.2
- openpyxl==3.1.5 (importacao e exportacao Excel)
- reportlab==4.1.0 (geracao de PDF)
- requests==2.31.0 (disponivel; integracoes usam urllib hoje)
- whitenoise==6.6.0 (static files)
- psycopg[binary]==3.2.3 (PostgreSQL)
- dj-database-url==2.1.0 (parse de DATABASE_URL)
- python-dotenv==1.0.1 (carregar .env local)

---

## 3) Estrutura do repositorio

### Raiz
- `manage.py`: entrypoint Django.
- `pmorganizer/`: projeto Django (settings/urls/asgi/wsgi).
- `cadastros/`: app principal (models, views, forms, web_views, etc).
- `templates/`: templates HTML (publico, registration, restrito).
- `assets/`: static files (CSS, imagens, modelos XLSX).
- `media/`: uploads (anexos e arquivos enviados).
- `api/index.py`: entrypoint WSGI para Vercel Serverless.
- `index.py`, `vercel_app.py`: wrappers WSGI para Vercel.
- `vercel.json`, `vercel_build.py`, `build_files.sh`: deploy.
- `README.md`, `PRODUCTION_INFO.md`, `DEPLOYMENT_GUIDE.md`, `MIGRATIONS_GUIDE.md`, `DEPLOY_OPTIMIZATION.md`: docs internas.
- `.env.example`: exemplo de variaveis de ambiente.

### Diretorio `pmorganizer/`
- `settings.py`: configuracoes Django, DB, static/media, APIs externas, logging, REST framework.
- `urls.py`: rotas principais (publicas, autenticacao, app, admin, API).
- `wsgi.py`, `asgi.py`: entrypoints WSGI/ASGI.

### Diretorio `cadastros/`
Arquivos principais:
- `models.py`: entidades de negocio e regras de validacao.
- `forms.py`: forms com validacoes e widgets (inclui reembolso de viagem, chatgpt e whatsapp settings).
- `web_views.py`: views da area restrita (CRUD, dashboards, relatorios, OFX, faturamento, DRE).
- `web_urls.py`: rotas da area restrita.
- `views.py`: viewsets DRF (API).
- `urls.py`: rotas da API.
- `auth_views.py`: login e fluxos de senha.
- `public_views.py`: forms publicos.
- `context_processors.py`: contexto global de UI (perfil, notificacoes).
- `middleware.py`: middleware para troca de senha obrigatoria.
- `importers.py`: importacao de templates e plano de contas (xlsx/csv/xml).
- `observations.py`: auditoria de alteracoes em projetos.
- `roles.py`: regras de acesso por perfil e visibilidade.
- `whatsapp_client.py` / `whatsapp_notifications.py`: integracao WhatsApp.
- `signals.py`: cria UserProfile ao criar User.
- `admin.py`: admin Django com inlines.
- `management/commands/`: comandos utilitarios.

---

## 4) Configuracao e variaveis de ambiente

### Variaveis principais (ver `pmorganizer/settings.py` e `.env.example`)
**Base Django**
- `DEBUG`: bool (default `True` em dev).
- `SECRET_KEY`: chave Django (obrigatoria em prod).
- `ALLOWED_HOSTS`: hosts permitidos (lista separada por virgula).
- `DATABASE_URL`: string de conexao (PostgreSQL em prod).
- `VERCEL_URL`: quando contem `.vercel.app`, adiciona ao `ALLOWED_HOSTS`.

**SeniorConnect (Oportunidades)**
- `OPPORTUNITIES_API_URL`
- `OPPORTUNITIES_API_TOKEN`
- `OPPORTUNITIES_REFRESH_DEFAULT`
- `OPPORTUNITIES_REFRESH_MIN`
- `OPPORTUNITIES_REQUEST_TIMEOUT`

**Brasil API (CNPJ)**
- `RECEITA_FEDERAL_API_URL`
- `RECEITA_FEDERAL_REQUEST_TIMEOUT`
- `RECEITA_FEDERAL_USER_AGENT`

**OpenAI (ChatGPT)**
- `CHATGPT_API_URL`
- `CHATGPT_API_KEY`
- `CHATGPT_ORG_ID`
- `CHATGPT_PROJECT_ID`
- `CHATGPT_MODEL`
- `CHATGPT_REQUEST_TIMEOUT`

**WhatsApp Z-API**
- `WHATSAPP_ZAPI_INSTANCE_ID`
- `WHATSAPP_ZAPI_TOKEN`
- `WHATSAPP_ZAPI_CLIENT_TOKEN`
- `WHATSAPP_ZAPI_BASE_URL`
- `WHATSAPP_ZAPI_TIMEOUT`
- `WHATSAPP_ZAPI_LOG_REQUESTS`

### Configuracoes relevantes em `settings.py`
- `LANGUAGE_CODE = pt-br`, `TIME_ZONE = America/Sao_Paulo`.
- `USE_TZ = True`, `SESSION_EXPIRE_AT_BROWSER_CLOSE = True`.
- Formatos brasileiros para data/hora e separadores decimais (`DECIMAL_SEPARATOR=","`, `THOUSAND_SEPARATOR="."`).
- `STATIC_URL`, `STATICFILES_DIRS` e `STATIC_ROOT` com WhiteNoise.
- `MEDIA_URL` e `MEDIA_ROOT` para uploads.
- `REST_FRAMEWORK` com paginação e filtros (search + ordering).

### Observacoes criticas
- Existem valores default hardcoded em `settings.py` (tokens e chaves). Em producao, substitua via ENV.
- `ALLOWED_HOSTS` recebe `.vercel.app` automaticamente quando `DEBUG=False` e quando `VERCEL_URL` aponta para Vercel.
- O parser de `DATABASE_URL` faz ajustes para casos sem scheme (ex.: Prisma).

---

## 5) Execucao local (dev)

1) Criar venv e instalar deps (Python 3.10 recomendado):
```
py -3.10 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
Opcional: manter o venv atual e criar um novo com outro nome:
```
py -3.10 -m venv venv310
venv310\Scripts\activate
```
2) Migrar banco:
```
python manage.py migrate
```
3) Criar superuser:
```
python manage.py createsuperuser
```
4) Rodar servidor:
```
python manage.py runserver
```

---

## 6) Autenticacao, perfis e seguranca

### Perfis (UserRole)
- `admin`, `gp_internal`, `gp_external`, `consultant`, `client`.

### UserProfile
- Criado automaticamente via `cadastros/signals.py` quando um User e criado.
- Contem `role`, `whatsapp_phone` e `must_change_password`.

### Forca de troca de senha
- `ForcePasswordChangeMiddleware` redireciona usuarios com `must_change_password=True` para troca de senha.

### Controle de acesso
- Funcoes em `cadastros/roles.py`:
  - `resolve_user_role`, `can_view_financial`.
  - `filter_projects_for_user` e `filter_activities_for_user`.
  - `allowed_project_visibility` e `filter_by_visibility`.
- Financeiro: acesso restrito a `admin`.

---

## 7) Modelos de dados (visao completa)

### Enumerations (TextChoices)
- Status gerais: `StatusChoices`.
- Usuarios: `UserRole`.
- Empresas e consultores: `CompanyType`, `BillingCycle`, `ConsultantType`, `SupplierPersonType`, `BankAccountType`.
- Financeiro: `FinancialStatus`, `PaymentMethod`, `BillingPaymentStatus`.
- Bancario: `BankMovementDirection`, `BankMovementSource`.
- Projetos: `ProjectStatus`, `ProjectType`, `ProjectContractType`, `ProjectCriticality`, `ProjectVisibility`.
- Observacoes: `ProjectObservationType`, `GoNoGoResult`, `ProjectAttachmentType`.
- Atividades: `ActivityStatus`, `ActivityBillingType`, `ActivityAssumedReason`, `ActivityCriticality`.
- Apontamentos: `TimeEntryType`, `TimeEntryStatus`.
- Tickets: `TicketStatus`, `TicketType`, `TicketCriticality`.
- Plano de contas / DRE: `AccountType`, `AccountNature`, `DreSign`.
- Infra: `DatabaseType`.

### Usuarios
- `UserProfile`: 1-1 com User, role e controle de troca de senha.

### Empresas, clientes e fornecedores
- `Company`: dados da empresa (legal/trade, tax_id, status, contato).
- `Client`: vinculado a Company, ciclo de faturamento, prazo de pagamento.
- `ClientContact`: contatos do cliente (primary, status).
- `Supplier`: fornecedor PF/PJ.

### Consultores
- `Consultant`: dados pessoais, empresa/fornecedor vinculados, flags Senior.
- `ConsultantRate`: historico de valor hora.
- `ConsultantBankAccount`: contas bancarias do consultor.
- `ConsultantAttachment`: anexos.
- `Competency` e `Certification`.

### Financeiro (titulos e pagamentos)
Base abstrata:
- `FinancialEntry`: campos base e validacoes (nao negativos, datas coerentes, status pago/cancelado).
- `total_amount()` calcula valor final com desconto/juros/multa.
- `save()` sincroniza status (open/overdue/paid/canceled).

Contas a pagar:
- `AccountsPayable` (FK supplier, consultant, billing_invoice, account_plan_item).
- UniqueConstraint `(supplier, document_number)`.
- `AccountsPayableAttachment`.
- `AccountsPayablePayment` (valor > 0).

Contas a receber:
- `AccountsReceivable` (FK client, billing_invoice, account_plan_item).
- UniqueConstraint `(client, document_number)`.
- `AccountsReceivablePayment` (valor > 0).
- `AccountsReceivable.save()` sincroniza `BillingInvoice.payment_status`.

### Bancario e conciliacao
- `CompanyBankAccount`.
- `BankStatementImport`: importacao OFX.
- `BankStatementEntry`: movimentos OFX.
- `BankSystemMovement`: lancamentos internos.
- `BankReconciliation`, `BankReconciliationSystemItem`, `BankReconciliationOfxItem`.

### Projetos
- `Phase`, `Product`, `Module`, `Submodule`.
- `Project`: contem dados do cliente, ambiente, datas, contrato e indicadores.
  - Recalcula `total_value`, `contracted_hours`, `available_hours`, `available_value` no `save()`.
  - Validacoes: contingencia (0-100), datas de cutover.
- `ProjectRole`, `ProjectContact`.
- `ProjectObservation` + `ProjectObservationType`.
- `ProjectGoNoGoChecklistItem`.
- `ProjectAttachment`.
- `ProjectOccurrence` + anexos.

### Atividades e apontamentos
- `ProjectActivity`: atividade com predecessoras, datas, billing_type, consultores, visibilidade para cliente.
  - Metodos: `hours_available`, `hours_contingency`, `schedule_state`, `schedule_label`, `subactivities_label`.
  - Validacoes de consistencia produto/modulo/submodulo e datas.
- `ProjectActivitySubactivity`: subatividades ordenadas.
- `TimeEntry`: apontamentos diarios/semanais com horas por dia, aprovacao e rejeicao.
  - Quando aprovado, sincroniza `ProjectActivity.actual_end` e status.
- `TimeEntryAttachment`.

### Faturamento
- `BillingInvoice` e `BillingInvoiceItem`.
- Integracao com `AccountsReceivable` e `TimeEntry`.

### Tickets
- `Ticket`, `TicketAttachment`, `TicketReply`, `TicketReplyAttachment`.

### Conhecimento
- `KnowledgeCategory`, `KnowledgePost`, `KnowledgeAttachment`.

### Templates e plano de contas
- `DeploymentTemplateHeader` e `DeploymentTemplate`.
- `AccountPlanTemplateHeader` e `AccountPlanTemplateItem` (DRE).

### Configuracoes
- `WhatsappSettings`.
- `ChatGPTSettings`.

### Formularios publicos
- `CandidateApplication`.
- `ProposalRequest`.

---

## 8) Regras de negocio e calculos importantes

### Projetos (contrato e contingencia)
- Para `contract_type=fixed_value`: calcula `contracted_hours = total_value / hourly_rate`.
- Para tipos por hora: calcula `total_value = contracted_hours * hourly_rate`.
- `contingency_percent` reduz `available_hours` e `available_value`.

### Atividades
- `hours_available` considera a contingencia do projeto.
- `schedule_state` identifica atrasos vs no prazo vs nao iniciada.
- Ao criar/editar atividades, o sistema pode registrar observacao automatica se a soma de horas ultrapassa o limite do projeto (contingencia).

### Apontamentos
- Apontamentos so sao permitidos para atividades liberadas.
- Status aprovado atualiza `ProjectActivity.actual_end` e `ProjectActivity.status`.

### Financeiro
- Titulos sincronizam status automaticamente com base em datas.
- Pagamentos validam valores nao negativos e limites de saldo aberto.
- `AccountsReceivable` sincroniza status de pagamento da fatura.

---

## 9) Fluxos criticos

### 9.1 Conciliacao bancaria + OFX
1. Importa OFX (`BankStatementImport` + `BankStatementEntry`).
2. Deduplicacao por assinatura (posted_at, amount, direction, FITID, etc.).
3. Gera lancamentos do sistema a partir de OFX (opcional):
   - Creditos exigem conta de receita selecionada.
   - Debitos usam conta 4.03.01 (despesa) por padrao.
4. Conciliacao manual entre movimentos do sistema e OFX:
   - So permite conciliar se total do sistema == total OFX.
5. Desfazer conciliacao disponivel.

### 9.2 Faturamento e contas a receber
1. Filtro por periodo/cliente/projeto/consultor em `BillingClosureView`.
2. Agrupa apontamentos aprovados (nao faturados) por consultor.
3. Gera:
   - `BillingInvoice` e `BillingInvoiceItem`.
   - `AccountsReceivable` (conta 1.01.01).
   - `AccountsPayable` por consultor (conta 3.01.01).
4. Notificacoes por WhatsApp para admin e consultores.

### 9.3 Reembolso de viagem
1. Usuario preenche formulario (consultor/GP interno/admin).
2. Valida:
   - consultor ativo e com fornecedor.
   - cliente "Senior Sistemas" existente.
   - contas 3.03.04 (pagar) e 1.04.01 (receber) no plano.
   - documento unico.
3. Cria:
   - `AccountsPayable` (consultor/fornecedor).
   - `AccountsReceivable` (cliente Senior Sistemas).
   - `AccountsPayableAttachment` obrigatorio.
4. Notifica admin e consultor via WhatsApp.

### 9.4 DRE
- Calculado a partir de pagamentos de contas a receber/pagar e movimentos do sistema.
- Usa `dre_group`, `dre_subgroup`, `dre_sign`, `dre_order` para agrupamento.
- Tela permite atribuir conta contabil para lancamentos sem conta (`DreEntryAssignView`).

### 9.5 ChatGPT (analise de projeto)
- Apenas `admin`.
- Consolida dados de projeto, atividades e apontamentos.
- Envia para API OpenAI com prompt configuravel.
- Permite exportar PDF e anexar ao projeto.

---

## 10) Web UI (area restrita)

### Base
- `BaseListView` e `BaseFormView` padronizam CRUD, filtros, status e permissoes.
- `templates/restricted/base.html` define layout, menu e contexto (user_role).

### Dashboards e paineis
- `DashboardView`: KPIs e graficos de projetos, DRE (admin).
- `FinancialDashboardView`: indicadores financeiros, aging, series e tendencias (admin).
- `ConsultantPanelView`: horas apontadas, titulos e historico mensal.
- `ClientPanelView`: visao de progresso e atividades visiveis ao cliente.
- `AllocationPanelView`: alocacao por consultor e periodo.
- `OpportunitiesPanelView`: oportunidades SeniorConnect.
- `NotificationsView`: pendencias e badges.

### Projetos e atividades
- CRUD de projetos, contatos, anexos, ocorrencias e checklist Go/No-Go.
- `ProjectScheduleView`: cronograma por fases com indicadores de status.
- `ProjectHistoryView`: historico e timeline (go-live e transicao).
- `ProjectActivityGenerateView`: gera atividades a partir de templates.
- Feedback do cliente sobre atividades (client_visible).

### Apontamentos
- `TimeEntryListView`, `TimeEntryCreateView`, `TimeEntryUpdateView`, `TimeEntryReviewView`.
- Relatorio exporta Excel e PDF (`TimeEntryReportView`).

### Financeiro
- `AccountsPayable*` e `AccountsReceivable*` (titulos, pagamentos, anexos).
- `AccountsPayableMissingAttachmentReportView`.
- `BankStatementView` (OFX + conciliacao) e `BankSystemStatementView`.
- `BillingClosureView` e `BillingInvoiceReportView`.

### Conhecimento
- `KnowledgeCategory*` e `KnowledgePost*`.

### Tickets
- `TicketListView`, `TicketCreateView`, `TicketDetailView`, `TicketCloseView`.
- `TicketDashboardView` com metricas (tempo de resposta e solucao).

### Configuracoes
- `UserProfileListView`, `UserCreateView`, `UserProfileUpdateView`.
- `WhatsappSettingsUpdateView`, `ChatGPTSettingsUpdateView`.

---

## 11) API REST (DRF)

### Rotas base
Prefixo `/api/` (router DRF em `cadastros/urls.py`).

### Endpoints principais
- `empresas`, `fornecedores`, `clientes`, `contatos`.
- `consultores`, `competencias`, `certificacoes`.
- `fases`, `produtos`, `modulos`, `submodulos`.
- `projetos`, `atividades-projeto`, `arquivos-projeto`.
- `contas-pagar`, `contas-receber`.
- `templates-implantacao`, `templates-implantacao-itens`.
- `modelos-plano-contas`, `modelos-plano-contas-itens`.

### Filtros e ordenacao
- Search e ordering via DRF (`SearchFilter`, `OrderingFilter`).
- Alguns endpoints permitem filtros adicionais via query params (ex.: status, client_id, project_id).

### Permissoes (resumo)
- Financeiro (contas a pagar/receber): apenas `admin`.
- Projetos/atividades: roles variam entre leitura e alteracao (ver `roles.py`).
- Serializers removem campos financeiros para roles sem permissao.

---

## 12) Integracoes externas

### SeniorConnect (Oportunidades)
- `OpportunitiesDataView` consulta API via `OPPORTUNITIES_API_URL` + token.
- `OpportunitiesApplyView` envia candidatura via WhatsApp.
- Erros tratados com mensagens claras e logs.

### Brasil API (CNPJ)
- `SupplierLookupView` consulta CNPJ (PF nao suportado).
- Monta payload de cadastro para fornecedor.

### OpenAI (ChatGPT)
- `ProjectChatGPTAnalysisView` chama API OpenAI (chat completions).
- `ChatGPTSettings` permite configurar URL, key, org/project e prompts.
- `ProjectChatGPTAnalysisPdfView` salva PDF no projeto.

### WhatsApp Z-API
- `whatsapp_client.py` envia mensagens via Z-API.
- `WhatsappSettings` pode sobrescrever credenciais do `.env`.
- Logging pode mascarar tokens e telefones (`WHATSAPP_ZAPI_LOG_REQUESTS`).

---

## 13) Notificacoes internas e WhatsApp

### Context processor (UI)
`cadastros.context_processors.user_role` injeta:
- `user_role`, `can_view_financial`.
- badges de notificacao: titulos vencendo hoje, pagos hoje, tickets e tarefas atrasadas.

### WhatsApp (eventos)
- Criacao e pagamento de titulos (admin + consultor).
- Apontamentos pendentes/aprovados.
- Fechamento de faturamento por consultor.
- Atividades atribuidas e notificacoes diarias (hoje/atrasadas).
- Tickets: criado, reply e encerrado.
- Candidatura em oportunidades.

---

## 14) Importacao e exportacao

### Templates de implantacao
- `import_deployment_templates` aceita `.xlsx`, `.csv`, `.xml` (MS Project).
- Normaliza cabecalhos e valida campos obrigatorios.

### Plano de contas
- `import_account_plan_templates` aceita `.xlsx` ou `.csv`.
- Normaliza colunas (remove acentos) e valida hierarquia.

### Exportacoes
- Relatorio de apontamentos: Excel e PDF.
- Analise ChatGPT: PDF anexado ao projeto.

Modelos de exemplo:
- `assets/modelos/modelo_importacao_templates.xlsx`
- `assets/modelos/modelo_importacao_plano_contas.xlsx`

---

## 15) Comandos de gerenciamento

### WhatsApp scheduler
`python manage.py run_whatsapp_scheduler [--once] [--interval N] [--force]`
- Dispara notificacoes diarias configuradas em `WhatsappSettings`.

### Sync de status de faturamento
`python manage.py sync_billing_payment_status [--commit]`
- Sincroniza `BillingInvoice.payment_status` com contas a receber.

---

## 16) Admin Django

`cadastros/admin.py` registra a maioria dos models e configura inlines para:
- Contatos do cliente.
- Anexos e contas bancarias do consultor.
- Anexos de projeto, atividades e subatividades.
- Tickets e respostas.
- Itens de template de implantacao e plano de contas.

---

## 17) Logging

Em `settings.py`:
- Logger `cadastros.whatsapp_client` em INFO.
- Logger `cadastros.web_views` em WARNING.

---

## 18) Deploy e operacao

### Vercel
- `vercel.json` roteia tudo para `api/index.py`.
- `vercel_build.py` executa `migrate` e `collectstatic`.
- WhiteNoise serve arquivos estaticos.

### GitHub Actions
` .github/workflows/vercel-deploy.yml`:
- Setup Python 3.12.
- Cache e install de dependencias.
- `python manage.py check`.
- `vercel build` e `vercel deploy`.

---

## 19) Testes

`cadastros/tests.py` existe mas sem cobertura. Recomenda-se ampliar testes para:
- Financeiro (titulos, pagamentos, reconciliacao).
- Importacoes (xlsx/csv/xml).
- Regras de acesso por perfil.
- Fluxo de faturamento e reembolso.

---

## 20) Riscos e recomendacoes

1) Remover credenciais hardcoded de `settings.py` e documentos internos.
2) Garantir rotacao de chaves e tokens em prod.
3) Evitar `ALLOWED_HOSTS = "*"` em producao.
4) Adicionar testes automatizados para fluxos criticos.
5) Monitorar logs das integracoes (SeniorConnect, OpenAI, WhatsApp).
6) Revisar permissao de acesso financeiro caso novos perfis sejam criados.

---

## 21) Referencias internas

- `README.md`
- `PRODUCTION_INFO.md`
- `DEPLOYMENT_GUIDE.md`
- `MIGRATIONS_GUIDE.md`
- `DEPLOY_OPTIMIZATION.md`

---

## 22) Status e manutencao

Esta documentacao reflete o estado atual do codigo no repositorio. Ao adicionar funcionalidades, atualize este arquivo para manter a rastreabilidade tecnica.
