@echo off
echo Configurando ambiente de desenvolvimento Backend...

if not exist venv (
    echo Criando virtualenv...
    python -m venv venv
)

echo Ativando virtualenv...
call venv\Scripts\activate

echo Instalando dependencias...
pip install -r requirements.txt

echo Rodando migracoes...
# Para rodar localmente, precisamos garantir que o DB esteja acessivel em localhost:5432 (padrao)
# O docker-compose ja expoem a porta 5432.
# Definindo variaveis para local
set DB_HOST=localhost
set DB_PORT=5432
set DB_USER=postgres
set DB_PASSWORD=postgres
set DB_NAME=app_db

python manage.py migrate

echo Pronto!
pause
