# Guia de Infraestrutura e Validação

## 1. Comandos de Setup Inicial

### 1.1. Subir o ambiente
Execute na raiz do projeto (onde está o `docker-compose.yml`):
```bash
docker-compose up --build -d
```
*Aguarde alguns segundos até que o banco de dados esteja saudável (healthy).*

### 1.2. Criar Migrações e Migrar Banco de Dados
```bash
# Criar as migrações dos apps
docker-compose exec backend python manage.py makemigrations

# Aplicar as migrações no banco
docker-compose exec backend python manage.py migrate
```

### 1.3. Criar Superusuário (Admin)
```bash
docker-compose exec backend python manage.py createsuperuser
```
*Siga as instruções interativas para definir email e senha.*

---

## 2. Checklist de Validação da API

Após subir o ambiente, verifique se tudo está funcionando:

### ✅ Validação de Saúde
- [ ] Acessar `http://localhost:8000/admin/`
    - Deve carregar a tela de login do Django Admin.
- [ ] Acessar `http://localhost:8000/api/docs/`
    - Deve abrir o Swagger UI com a lista de endpoints.

### ✅ Teste de Autenticação (Flow JWT)
1. Abra o Swagger (`/api/docs/`).
2. Vá em `api/auth/token/` (POST).
3. Insira as credenciais do superuser criado.
4. Execute e verifique se retornou `access` e `refresh` tokens.
5. Copie o `access` token.
6. Clique no botão **Authorize** no topo do Swagger e insira: `Bearer <SEU_TOKEN>`.

### ✅ Teste de Endpoints (Requer Auth)
- [ ] **GET /api/users/me/**: Deve retornar os dados do seu usuário.
- [ ] **GET /api/categories/**: Deve retornar lista vazia (200 OK).
- [ ] **POST /api/categories/**: Tente criar uma categoria teste:
    ```json
    {
      "name": "Financeiro",
      "description": "Relatórios financeiros"
    }
    ```
- [ ] **POST /api/reports/**: Crie um relatório vinculado à categoria acima.

---

## 3. Comandos Úteis no Dia a Dia

**Ver logs do backend:**
```bash
docker-compose logs -f backend
```

**Derrubar o ambiente:**
```bash
docker-compose down
```

**Resetar banco de dados (CUIDADO!):**
```bash
docker-compose down -v
```
