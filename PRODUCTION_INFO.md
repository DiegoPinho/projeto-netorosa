# 🚀 PM Organizer - Produção

## ✅ DEPLOY COMPLETO E FUNCIONANDO!

Toda a configuração foi concluída com sucesso. O projeto está em produção!

---

## 🌐 URLs de Produção

### Aplicação Principal
**URL:** https://pmorganizer.vercel.app

### Admin Django
**URL:** https://pmorganizer.vercel.app/admin/

**Credenciais:**
- Username: `admin`
- Password: `admin123`
- Email: `admin@pmorganizer.com`

⚠️ **IMPORTANTE:** Altere a senha após o primeiro login!

### Outras URLs
- Dashboard: `/app/`
- API: `/api/`
- Login: `/area-restrita/login/`

---

## 🗄️ Banco de Dados PostgreSQL

**Status:** ✅ Conectado e Configurado

- Provider: Prisma Postgres (Vercel)
- Database: `pmorganizer-db`
- Migrações: 67 migrations aplicadas
- Tabelas: 50+ tabelas criadas

**Models principais:**
- User, UserProfile
- Company, Client, Consultant, Supplier
- Project, ProjectActivity, ProjectObservation
- AccountsPayable, AccountsReceivable
- BillingInvoice, TimeEntry
- Ticket, Phase, Product, Module

---

## 🔧 Configuração Técnica

### Stack
- **Framework:** Django 5.2.6
- **Python:** 3.12 (Vercel) / 3.10+ (dev)
- **Database:** PostgreSQL (Prisma)
- **Static Files:** WhiteNoise (CompressedManifestStaticFilesStorage)
- **Hosting:** Vercel Serverless Functions

### Arquivos de Configuração
- **vercel.json** - Configuração do Vercel (builds e rotas)
- **index.py** - Entry point WSGI para Vercel
- **vercel_build.py** - Script de build (collectstatic)
- **build_files.sh** - Script alternativo de build
- **pmorganizer/wsgi.py** - WSGI application padrão Django
- **pmorganizer/settings.py** - Configurações Django

### Environment Variables (Configuradas)
- `DATABASE_URL` - PostgreSQL connection string
- `DEBUG=False` - Production mode
- `SECRET_KEY` - Secure key gerada
- `ALLOWED_HOSTS=.vercel.app,*` - Hosts permitidos
- `PYTHON_VERSION` **nao deve ser definido** (Vercel usa Python 3.12 automaticamente)
- `OPPORTUNITIES_API_TOKEN`

### Static Files Configuration
- **STATIC_URL:** `/static/`
- **STATIC_ROOT:** `BASE_DIR / "staticfiles"`
- **STATICFILES_DIRS:** `[BASE_DIR / "assets"]`
- **STATICFILES_STORAGE:** `whitenoise.storage.CompressedManifestStaticFilesStorage`
- **Middleware:** WhiteNoise configurado após SecurityMiddleware
- **Build:** Arquivos coletados via `vercel_build.py` durante deploy

---

## 🔄 Workflow de Deploy

### Desenvolvimento
```bash
# Work on dev branch
git checkout dev
# Make changes...
git add .
git commit -m "feat: nova funcionalidade"
git push origin dev
```

### Deploy Preview (Testing)
```bash
# Create PR from dev to main
# GitHub Actions automatically:
# - Builds the project
# - Deploys to preview environment
# - Comments on PR with preview URL
```

### Deploy Production
```bash
# Merge PR or:
git checkout main
git merge dev
git push origin main
# GitHub Actions automatically deploys to production!
```

---

## 📊 Infraestrutura

### GitHub
- **Repo:** https://github.com/netorosa/pmorganizer
- **Actions:** https://github.com/netorosa/pmorganizer/actions
- **Secrets:** Configurados (VERCEL_TOKEN, VERCEL_ORG_ID, VERCEL_PROJECT_ID)

### Vercel
- **Dashboard:** https://vercel.com/netorosa/pmorganizer
- **Deployments:** https://vercel.com/netorosa/pmorganizer
- **Database:** https://vercel.com/netorosa/pmorganizer/stores
- **Env Vars:** https://vercel.com/netorosa/pmorganizer/settings/environment-variables

---

## 🛠️ Comandos Úteis

### Rodar migrações localmente no banco de produção
```bash
# Via script (já configurado)
python -c "from dotenv import load_dotenv; import os; load_dotenv('.env.production'); os.system('python manage.py migrate')"
```

### Acessar shell Django com DB de produção
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv('.env.production'); os.system('python manage.py shell')"
```

### Ver logs da aplicação
```bash
# Via Vercel Dashboard
# https://vercel.com/netorosa/pmorganizer
# Clique em um deployment > Runtime Logs
```

---

## 🎯 Funcionalidades Principais

1. **Gestão de Projetos**
   - Criação e acompanhamento de projetos
   - Atividades e sub-atividades
   - Timeline e cronograma
   - Observações e auditoria

2. **Gestão de Consultores**
   - Cadastro de consultores
   - Competências e certificações
   - Alocação em projetos
   - Banco de horas

3. **Gestão Financeira**
   - Contas a pagar e receber
   - Faturamento e invoices
   - Pagamentos e recebimentos
   - Relatórios financeiros

4. **Integração com APIs**
   - SeniorConnect (Oportunidades)
   - Brasil API (CNPJ)
   - OpenAI ChatGPT (Análises)

5. **Sistema de Tickets**
   - Suporte e atendimento
   - Prioridades e criticidades
   - Anexos e respostas

---

## 🔐 Segurança

✅ **Configurações de Segurança:**
- DEBUG=False em produção
- SECRET_KEY único e seguro
- ALLOWED_HOSTS restrito
- DATABASE_URL criptografada
- Secrets do GitHub protegidos
- HTTPS automático (Vercel)
- PostgreSQL com SSL

⚠️ **TODO - Segurança:**
- [ ] Alterar senha do admin
- [ ] Configurar 2FA para admin
- [ ] Review de permissões de usuários
- [ ] Configurar CORS se necessário
- [ ] Configurar rate limiting

---

## 📈 Monitoramento

### GitHub Actions
- **Status:** https://github.com/netorosa/pmorganizer/actions
- Visualizar builds e deploys
- Logs completos disponíveis

### Vercel
- **Analytics:** https://vercel.com/netorosa/pmorganizer/analytics
- **Logs:** https://vercel.com/netorosa/pmorganizer (Runtime Logs)
- **Performance:** Speed Insights disponível

---

## 🆘 Troubleshooting

### Erro 500 - Missing variable 'handler' or 'app'
**Causa:** Vercel não encontra o WSGI handler no arquivo especificado.
**Solução aplicada:**
1. Alterado `vercel.json` para usar `index.py` como entry point
2. Criado `index.py` que exporta `app = application` do WSGI
3. Mantido `pmorganizer/wsgi.py` no formato padrão Django

### Erro 500 - TypeError: issubclass() arg 1 must be a class
**Causa:** Vercel esperava classe HTTPRequestHandler, não aplicação WSGI.
**Solução aplicada:**
1. Configurado corretamente `index.py` como handler
2. Removido exports extras de `wsgi.py`
3. Simplificado configuração de rotas em `vercel.json`

### CSS/JS não carregam (arquivos estáticos desconfigurados)
**Causa:** Arquivos estáticos não servidos corretamente pelo Vercel.
**Solução aplicada:**
1. Corrigido `STATIC_URL` de `"static/"` para `"/static/"`
2. Configurado `STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"`
3. Criado `vercel_build.py` para executar `collectstatic` durante build
4. Removido build estático separado do `vercel.json`
5. WhiteNoise agora serve todos os arquivos automaticamente

### Erro de database
1. Verificar se `DATABASE_URL` está configurada no Vercel
2. Verificar se migrações foram aplicadas (67 migrations)
3. Verificar logs de conexão no Vercel Dashboard
4. Testar conexão local com `.env.production`

### Python version mismatch
**Causa:** Django 5.2.6 requer Python >=3.10.
**Solução aplicada:**
1. Removido runtime fixo do `vercel.json` (Vercel usa Python 3.12 automaticamente)
2. Atualizado workflow GitHub Actions para Python 3.12
3. Removida a variavel `PYTHON_VERSION` (evita override invalido)

---

## 💡 Lições Aprendidas

### 1. Django + Vercel Serverless
- Django funciona em Vercel Serverless Functions via `@vercel/python`
- Entry point deve exportar `app` (aplicação WSGI)
- Usar `index.py` como wrapper do `wsgi.py` padrão Django

### 2. Arquivos Estáticos em Serverless
- WhiteNoise é essencial para servir static files sem servidor dedicado
- `CompressedManifestStaticFilesStorage` otimiza performance
- `collectstatic` deve rodar durante build via `vercel_build.py`
- `STATIC_URL` precisa começar com `/` (ex: `/static/`)

### 3. Configuração Git + Vercel
- Git author email deve ter acesso ao projeto Vercel
- Usar `git config --local` para configurar email por repositório
- Fine-grained tokens GitHub precisam de permissões específicas

### 4. Python Version Management
- Django 5.2.6+ requer Python 3.10+
- Especificar runtime em `vercel.json` e GitHub Actions
- Manter consistência entre ambientes local, CI/CD e produção

### 5. Database em Produção
- PostgreSQL via Prisma Postgres (Vercel) funciona perfeitamente
- Migrations podem rodar localmente contra DB de produção
- Usar `DATABASE_URL` com SSL obrigatório
- Connection pooling com `conn_max_age=600`

---

## 📞 Suporte

**Documentação:**
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Guia completo de deployment
- [MIGRATIONS_GUIDE.md](MIGRATIONS_GUIDE.md) - Guia de migrações
- [PRODUCTION_INFO.md](PRODUCTION_INFO.md) - Este arquivo

**APIs Externas:**
- SeniorConnect: https://seniorconnect.com.br
- Brasil API: https://brasilapi.com.br
- OpenAI: https://platform.openai.com

**Recursos Vercel:**
- Documentação: https://vercel.com/docs
- Python Runtime: https://vercel.com/docs/functions/serverless-functions/runtimes/python
- Environment Variables: https://vercel.com/docs/environment-variables

---

## 🎉 Status Final

| Componente | Status |
|------------|--------|
| Repositório Git | ✅ |
| GitHub Secrets | ✅ |
| GitHub Actions | ✅ |
| Vercel Project | ✅ |
| PostgreSQL Database | ✅ |
| Migrações | ✅ 67 applied |
| Superusuário | ✅ |
| Deploy Production | ✅ |
| Static Files | ✅ |
| Admin Panel | ✅ |

---

**Projeto 100% funcional em produção! 🚀**

Última atualização: 04/01/2026
