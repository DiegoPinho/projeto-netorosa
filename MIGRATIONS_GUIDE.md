# 🗄️ Guia de Migrações do Django - PostgreSQL

## ✅ Status Atual

- ✅ PostgreSQL database criado: `pmorganizer-db`
- ✅ DATABASE_URL configurada na Vercel
- ✅ Deployment disparado com nova configuração

---

## 📊 Aguardar Deployment

O deployment está rodando agora com a `DATABASE_URL` configurada!

**Acompanhe em:**
- GitHub Actions: https://github.com/netorosa/pmorganizer/actions
- Vercel: https://vercel.com/netorosa/pmorganizer

Aguarde o deployment terminar (geralmente 2-3 minutos).

---

## 🔧 Rodar Migrações do Django

Após o deployment ter sucesso, você precisa rodar as migrações do Django no banco PostgreSQL.

### Opção 1: Via Vercel CLI (Recomendado)

```bash
# 1. Instalar Vercel CLI (se ainda não tiver)
npm install -g vercel

# 2. Fazer login
vercel login

# 3. Ir para o diretório do projeto
cd c:\Users\nando\Documents\WORKSPACE\WORKSPACE_CLIENTES\pmorganizer

# 4. Link com o projeto
vercel link

# 5. Baixar variáveis de ambiente
vercel env pull .env.production

# 6. Rodar migrações
python manage.py migrate

# 7. Criar superusuário (opcional)
python manage.py createsuperuser
```

### Opção 2: Conectar Diretamente ao Banco

```bash
# 1. Criar arquivo .env.production local
# Adicione no arquivo:
DATABASE_URL="postgres://177c8ada93ba24ced747173ca2d3bfffbe0a566943bd5ebb6869af6dcd839405:sk_uafyrOHIldmMk4-TSe9bZ@db.prisma.io:5432/postgres?sslmode=require"

# 2. Instalar python-dotenv
pip install python-dotenv

# 3. Criar script para rodar migrações
# create_migrations.py
```

Crie o arquivo `run_migrations.py`:

```python
#!/usr/bin/env python
import os
from dotenv import load_dotenv

# Carregar .env.production
load_dotenv('.env.production')

# Rodar migrações
os.system('python manage.py migrate')
```

Execute:
```bash
python run_migrations.py
```

### Opção 3: Via Interface da Vercel (Função Serverless)

Crie um endpoint temporário para rodar migrations:

1. Criar `pmorganizer/migrate_view.py`:
```python
from django.http import HttpResponse
from django.core.management import call_command
import io

def run_migrations(request):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=401)

    out = io.StringIO()
    call_command('migrate', stdout=out)
    return HttpResponse(f"<pre>{out.getvalue()}</pre>")
```

2. Adicionar URL em `pmorganizer/urls.py`:
```python
from pmorganizer.migrate_view import run_migrations

urlpatterns = [
    ...
    path('admin/run-migrations/', run_migrations),
]
```

3. Acessar: `https://your-app.vercel.app/admin/run-migrations/`

⚠️ **REMOVA** este endpoint após rodar as migrações!

---

## 🎯 Verificar se Funcionou

Após rodar as migrações:

1. **Verifique as tabelas criadas:**
   ```bash
   python manage.py dbshell
   \dt  # Lista todas as tabelas
   \q   # Sair
   ```

2. **Acesse o admin do Django:**
   ```
   https://your-app.vercel.app/admin/
   ```

3. **Teste a aplicação:**
   ```
   https://your-app.vercel.app/app/
   ```

---

## 📋 Lista de Migrações

O projeto tem **50+ migrations** na app `cadastros`:

```
cadastros/migrations/
├── 0001_initial.py
├── 0002_alter_certification_created_at_and_more.py
├── 0003_phase_product_module_submodule.py
├── ...
└── 0045_project_contract_type.py
```

Todas serão aplicadas automaticamente com `python manage.py migrate`.

---

## 🔍 Troubleshooting

### Erro: "relation does not exist"
- As migrações não foram rodadas
- Rode: `python manage.py migrate`

### Erro: "no password supplied"
- DATABASE_URL não está configurada
- Verifique: https://vercel.com/netorosa/pmorganizer/settings/environment-variables

### Erro: "connection timeout"
- Verifique se o IP está permitido no firewall do banco
- Prisma Postgres da Vercel geralmente não tem restrições

### Erro: "peer authentication failed"
- Use `?sslmode=require` na DATABASE_URL
- Já está configurado corretamente

---

## 📱 Próximos Passos

1. ✅ Aguardar deployment terminar
2. ✅ Rodar migrações (escolha uma opção acima)
3. ✅ Criar superusuário
4. ✅ Testar aplicação
5. ✅ Importar dados (se necessário)

---

## 🎉 Sucesso!

Quando tudo estiver funcionando:
- ✅ PostgreSQL configurado
- ✅ Migrações aplicadas
- ✅ Admin do Django funcionando
- ✅ Deploy automático configurado

**Seu projeto está em produção!** 🚀
