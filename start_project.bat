@echo off
echo ==========================================
echo      INICIANDO SISTEMA DE RELATORIOS
echo ==========================================

REM 1. Subir Docker
echo.
echo [1/5] Subindo conteineres Docker (Backend + Banco)...
docker-compose up -d --build
IF %ERRORLEVEL% NEQ 0 (
    echo [ERRO] Falha ao executar docker-compose. Verifique se o Docker Desktop esta rodando.
    pause
    exit /b
)

REM 2. Aguardar Banco
echo.
echo [2/5] Aguardando inicializacao do Banco de Dados (10s)...
timeout /t 10 /nobreak >nul

REM 3. Migrations
echo.
echo [3/5] Aplicando migracoes do Django...
docker-compose exec backend python manage.py migrate

REM 4. Superuser (Opcional - vai falhar se já existir, mas ok)
echo.
echo [4/5] Criando superusuario padrao (admin / admin)...
echo from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@admin.com').exists() or User.objects.create_superuser('admin', 'admin@admin.com', 'admin') | docker-compose exec -T backend python manage.py shell

REM 5. Frontend
echo.
echo [5/5] Iniciando Frontend...
cd frontend
echo Instalando dependencias (pode demorar um pouco)...
call npm install
echo Iniciando servidor de desenvolvimento...
call npm run dev
