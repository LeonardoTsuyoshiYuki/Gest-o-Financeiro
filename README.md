# Sistema de Gestão Financeiro V2

Sistema corporativo para gestão e processamento de faturas, com suporte a OCR, aprovação e controle de acesso (RBAC).

## 🚀 Funcionalidades

-   **Importação de Faturas**: Upload de PDFs com extração automática de dados (OCR).
-   **Tratamento de Erros de Importação**: Identificação de falhas (Extração, Hash, Dados Faltantes) e duplicatas.
-   **Gestão de Usuários (RBAC)**: Perfis de acesso:
    -   **ADMIN**: Acesso total, gestão de usuários.
    -   **GESTOR**: Aprovação e edição.
    -   **ANALISTA**: Operação diária.
    -   **VISUALIZADOR**: Apenas leitura.
-   **Dashboard Financeiro**: Visão geral de despesas.
-   **Categorização**: Organização de despesas por categorias.

## 🛠 Tech Stack

-   **Backend**: Python, Django REST Framework, Celery, Redis, PostgreSQL.
-   **Frontend**: React, TypeScript, Vite, Material UI.
-   **Infra**: Docker Compose.

## 🔧 Configuração e Execução

### Pré-requisitos
- Docker e Docker Compose instalados e **executando**.
- Node.js 18+ (para o frontend).

### 🚀 Inicialização Rápida (Windows)
O projeto inclui um script que automatiza todo o processo:
```bash
./start_project.bat
```
Este script irá:
1. Subir os containers (Backend, Worker, DB, Redis).
2. Aplicar migrações.
3. Criar usuário admin padrão (`admin@admin.com` / `admin`).
4. Instalar dependências e rodar o frontend.

### 🏗️ Estrutura de Arquivos e Volumes
- **Uploads/Mídia**: Arquivos enviados pelos usuários são persistidos no volume Docker `media_data`. Eles não ficam misturados com o código fonte.
- **Banco de Dados**: Persistido no volume `postgres_data`.

### Instalação Manual
Caso prefira rodar passo a passo:

1.  **Backend e Serviços**:
    ```bash
    docker-compose up -d --build
    docker-compose exec backend python manage.py migrate
    ```

2.  **Frontend**:
    ```bash
    cd frontend
    npm install
    npm run dev
    ```

3.  **Acessando**:
    -   Frontend: `http://localhost:5173`
    -   Backend API: `http://localhost:8000/api/`
    -   Admin Django: `http://localhost:8000/admin/`

## 🧪 Testes

### Backend
```bash
cd backend
python manage.py test
```
Cobre autenticação, importação, erros e permissões.

### Frontend
```bash
cd frontend
npm run test
```
Cobre componentes de login, upload e listagem.

## 🔒 Segurança

-   Autenticação via JWT (Access + Refresh Tokens).
-   RBAC implementado em nível de API e Interface.
-   CORS configurado para ambiente seguro.

## 📝 Versão Atual (Refactor/System-Hardening)

-   ✅ Correção de loop "Processing" na importação.
-   ✅ Adição de códigos de erro estruturados na API.
-   ✅ Tela de gestão de usuários.
-   ✅ Exibição amigável de erros no frontend.

---
Desenvolvido por Leonardo Yuki
