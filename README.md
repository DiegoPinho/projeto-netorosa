# pmorganizer

Sistema de gerenciamento de projetos, consultores e finanças desenvolvido em Django.
nd 2
## Tecnologias

## atualizacao

- Django 5.2.6
- Django REST Framework 3.15.2
- Python 3.10+
- SQLite3

## Instalação

```bash
# Criar ambiente virtual (recomendado Python 3.10)
py -3.10 -m venv venv
# Alternativa: manter o venv atual e criar um novo
# py -3.10 -m venv venv310

# Ativar ambiente virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Rodar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Rodar servidor
python manage.py runserver
```

## Deploy

O projeto está configurado para deploy automático na Vercel via GitHub Actions.
