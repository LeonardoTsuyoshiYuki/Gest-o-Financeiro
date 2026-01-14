# Guia de Testes e Execução

Este guia descreve como rodar os testes automatizados do backend (Django) e do frontend (React), além de comandos úteis para o dia a dia.

---

## 🐍 Backend (Django)

Os testes do backend cobrem a API, Modelos e Lógica de Negócio (ex: cálculo de dashboards).

### 1. Rodar todos os testes
No terminal, execute via Docker:
```bash
docker-compose exec backend python manage.py test
```

### 2. Rodar testes com Coverage (Cobertura)
Para ver a porcentagem de código testado:
```bash
docker-compose exec backend coverage run manage.py test
docker-compose exec backend coverage report
```

### O que está sendo testado?
*   **Users**: Autenticação e geração de token JWT.
*   **Reports**: CRUD de relatórios e endpoints de cálculo do Dashboard.

---

## ⚛️ Frontend (React)

Os testes do frontend verificam se os componentes estão renderizando e se comportando corretamente (ex: formulário de login).

### 1. Instalar dependências de teste
Caso ainda não tenha feito, instale as libs necessárias:
```bash
cd frontend
npm install -D vitest jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event @types/jest
```

### 2. Rodar os testes
```bash
npm test
```
*Isso iniciará o Vitest em modo watch. Pressione 'q' para sair.*

### 3. Rodar com Coverage
```bash
npm run test -- --coverage
```

### O que está sendo testado?
*   **Login**: Verifica se campos existem e se a mensagem de erro aparece ao falhar.
*   *Configuração pronta para adicionar mais testes em `src/features`.*

---

## 🚀 Comandos Úteis (Cheat Sheet)

### Subir o Projeto
```bash
docker-compose up --build
```
*Acesse:*
*   Frontend: http://localhost:3000
*   Backend API: http://localhost:8000
*   Swagger Docs: http://localhost:8000/api/docs/

### Criar um Superusuário (Admin)
```bash
docker-compose exec backend python manage.py createsuperuser
```

### Resetar Banco de Dados
```bash
docker-compose down -v
docker-compose up -d
```
