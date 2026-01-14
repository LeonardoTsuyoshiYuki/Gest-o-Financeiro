# Especificação Técnica: Sistema de Relatório Web Gerencial

## 1. Visão Geral do Projeto

### 1.1. Contexto e Justificativa
No ambiente corporativo atual, a tomada de decisão baseada em dados (data-driven) é crucial. Este projeto visa substituir processos manuais (como planilhas Excel trocadas por e-mail) por uma plataforma centralizada, segura e web, garantindo integridade dos dados e facilidade de acesso.

### 1.2. Objetivo
Desenvolver uma aplicação Web para visualização de indicadores gerenciais, permitindo a análise de dados através de dashboards interativos e grades de dados com filtros avançados, com suporte a exportação para formatos corporativos (PDF, Excel).

### 1.3. Público-Alvo
- **Diretoria/Gerência**: Visualização de dashboards consolidados e KPIs.
- **Analistas**: Extração de relatórios detalhados e exportação de dados.
- **Administradores do Sistema**: Gestão de usuários e configurações de integrações.

---

## 2. Requisitos do Sistema

### 2.1. Requisitos Funcionais (RF)
- **RF01 - Autenticação**: O sistema deve permitir login via e-mail e senha (JWT).
- **RF02 - Dashboard Principal**: Exibir cards com KPIs principais e gráficos resumidos ao entrar.
- **RF03 - Filtros Dinâmicos**: Permitir filtrar dados por período (Data Início/Fim), Categoria, Status e Unidade de Negócio.
- **RF04 - Visualização em Tabela**: Exibir dados analíticos em tabelas paginadas, com ordenação por colunas.
- **RF05 - Gráficos Interativos**: Gráficos de barra, linha e pizza que atualizam conforme os filtros.
- **RF06 - Exportação**: Permitir download da visão atual em CSV, Excel (.xlsx) e PDF.
- **RF07 - Gestão de Usuários**: (Admin) Criar, editar e inativar usuários.

### 2.2. Requisitos Não Funcionais (RNF)
- **RNF01 - Performance**: O tempo de carregamento dos dashboards deve ser inferior a 2 segundos para datasets de até 10.000 registros.
- **RNF02 - Segurança**: Senhas criptografadas (PBKDF2/Argon2), comunicação HTTPS e Tokens JWT com expiração curta.
- **RNF03 - Escalabilidade**: Backend stateless pronto para containerização (Docker).
- **RNF04 - Responsividade**: Acesso otimizado para Desktop (foco principal) e compatibilidade com Tablets/Mobile.
- **RNF05 - Usabilidade**: Interface limpa, seguindo Material Design ou similar.

---

## 3. Arquitetura da Solução

### 3.1. Desenho da Arquitetura
O sistema seguirá uma arquitetura **Client-Server desacoplada**:

*   **Frontend (SPA)**: React.js rodando no navegador do cliente. Consome a API REST.
*   **Backend (API)**: Django REST Framework servindo dados em JSON.
*   **Banco de Dados**: PostgreSQL para persistência relacional.
*   **Web Server (Reverse Proxy)**: Nginx (em produção) para servir estáticos do React e encaminhar chamadas de API para o Gunicorn/Django.

### 3.2. Fluxo de Dados
1.  Usuário acessa o Frontend e realiza Login.
2.  Frontend recebe `access_token` e `refresh_token`.
3.  Frontend armazena tokens de forma segura (HttpOnly cookie ou in-memory + local storage controlado).
4.  Requisições subsequentes enviam o token no Header `Authorization: Bearer <token>`.
5.  Django valida o token, consulta o PostgreSQL e retorna os dados.

---

## 4. Stack Tecnológico

| Camada | Tecnologia | Justificativa |
| :--- | :--- | :--- |
| **Frontend** | **React (Vite)** | Padrão de mercado, alta performance, ecossistema rico. Vite para build rápido. |
| **Estilização** | **Material UI (MUI)** | Componentes prontos de alta qualidade, ideal para sistemas corporativos ("look & feel" profissional). |
| **Gerenciamento de Estado** | **Zustand** ou **Context API** | Simplicidade e redução de boilerplate comparado ao Redux. |
| **Gráficos** | **Recharts** | Biblioteca leve, construída sobre componentes React e D3, fácil customização. |
| **Backend** | **Django 5.x** | Robusto, seguro ("batteries included"), excelente ORM. |
| **API** | **Django REST Framework (DRF)** | Poderoso para criação de APIs, serialização simples. |
| **Autenticação** | **SimpleJWT** | Padrão industrial para Auth em DRF. |
| **Documentação** | **drf-spectacular** | Geração automática de OpenAPI 3.0 (Swagger). |
| **Banco de Dados** | **PostgreSQL** | Relacional, robusto, suporte a JSONB se necessário, open-source. |
| **Infra** | **Docker & Docker Compose** | Padronização de ambiente dev/prod. |

---

## 5. Modelagem de Dados (ER Simplificado)

### Tabelas Principais

**1. Users (CustomUser - Herança do AbstractUser)**
*   `id` (PK)
*   `email` (Unique, Username field)
*   `full_name`
*   `role` (Enum: Admin, Manager, Viewer)
*   `is_active`

**2. Relatorios (Reports)**
*   `id` (PK)
*   `titulo`
*   `data_referencia` (Date)
*   `categoria` (FK para Category)
*   `valor_total` (Decimal)
*   `status` (Enum: Pendente, Aprovado, Cancelado)
*   `criado_em` (Timestamp)
*   `atualizado_em` (Timestamp)

**3. Categorias (Categories)**
*   `id` (PK)
*   `nome`
*   `descricao`

**4. Metas (Targets - Opcional para Comparativo)**
*   `id` (PK)
*   `periodo` (Date)
*   `valor_meta` (Decimal)

---

## 6. Definição da API REST

### Autenticação
*   `POST /api/auth/token/`: Obter tokens (Login).
*   `POST /api/auth/token/refresh/`: Renovar token de acesso.

### Dashboard & Analytics
*   `GET /api/dashboard/summary/`: Retorna KPIs consolidados (Total Vendas, Qtd Pedidos, Ticket Médio).
    *   *Params: start_date, end_date*
*   `GET /api/dashboard/charts/sales-by-category/`: Retorna dados formatados para o gráfico de pizza.

### Relatórios
*   `GET /api/reports/`: Listagem paginada.
    *   *Filters: search, star_date, end_date, status, category*
*   `GET /api/reports/{id}/`: Detalhes de um registro.
*   `POST /api/reports/`: Criar novo registro (se aplicável).
*   `PATCH /api/reports/{id}/`: Atualizar.
*   `GET /api/reports/export/`: Endpoint específico que retorna blob (PDF/XLSX) baseado nos filtros aplicados.

---

## 7. Estrutura de Pastas e Organização

### 7.1. Frontend (React)
```text
src/
├── assets/          # Imagens, fontes
├── components/      # Componentes globais reutilizáveis
│   ├── Layout/      # Sidebar, Header, MainWrapper
│   ├── UI/          # Buttons, Cards, Inputs customizados
│   └── Charts/      # Wrappers para Recharts
├── contexts/        # Context API (AuthContext, ThemeContext)
├── hooks/           # Custom hooks (useAuth, useFetchReports)
├── pages/           # Páginas da aplicação
│   ├── Login/
│   ├── Dashboard/
│   └── Reports/
├── services/        # Configuração do Axios e chamadas à API
├── styles/          # Temas globais (MUI Theme)
├── utils/           # Formatadores de data, moeda, validações
└── App.tsx          # Rotas e Providers
```

### 7.2. Backend (Django)
```text
backend/
├── core/                # Configurações do projeto (settings, wsgi)
├── users/               # App de gestão de usuários e auth
├── reports/             # App principal de negócio
│   ├── migrations/
│   ├── models.py        # Modelos do DB
│   ├── serializers.py   # Serializers do DRF
│   ├── views.py         # ViewSets e APIViews
│   ├── urls.py          # Rotas do app
│   └── services.py      # Lógica de negócio pesada (separada das views)
├── utils/               # Exportadores PDF/Excel, Helpers gerais
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 8. UX/UI e Design System

*   **Paleta de Cores**:
    *   Primária: Azul Corporativo (#1976D2 - Passa confiança e seriedade).
    *   Secundária: Laranja (#ED6C02 - Para call-to-actions ou destaques).
    *   Background: Cinza Claro (#F4F6F8 - Para fundo de aplicação) vs Branco (#FFFFFF - Para Cards/Containers).
*   **Tipografia**: Roboto ou Inter (Legibilidade em telas de dados densos).
*   **Feedback**:
    *   Skeletons durante o carregamento de dados.
    *   Toasts/Snackbars para sucesso ou erro de operações.
*   **Dashboard**: Layout de Grid (Masonry ou CSS Grid). KPIs no topo, Gráficos ao meio, Tabela detalhada abaixo.

---

## 9. Plano de Desenvolvimento (Cronograma Sugerido)

Considerando uma Sprint de 2 semanas (10 dias úteis):

**Dias 1-2: Setup e Base**
*   Configurar repositório.
*   Setup Django + Docker + Postgres.
*   Setup React + Vite + MUI.
*   Implementar Login e Autenticação (Backend + Frontend).

**Dias 3-5: Backend Core**
*   Modelagem do banco.
*   CRUD de Relatórios e Categorias.
*   Endpoints de Agregação (Soma, Contagem, Médias para o Dashboard).
*   Testes unitários básicos.

**Dias 6-8: Frontend Visualização**
*   Construção do Layout Principal (Sidebar/Header).
*   Implementação dos Cards de KPI.
*   Integração da lib de Gráficos (Recharts).
*   Tabela de dados com paginação Server-Side.

**Dias 9-10: Refinamento e Exportação**
*   Filtros globais (integrar Frontend <-> Backend).
*   Implementar exportação (Excel/PDF) no Backend.
*   Polimento visual e tratamento de erros.

---

## 10. Boas Práticas Adotadas

1.  **Backend**:
    *   Uso de *ViewSets* para CRUD padrão e *APIView* para endpoints customizados.
    *   Filtros via `django-filter` para evitar queries manuais complexas.
    *   `select_related` e `prefetch_related` para evitar problema de N+1 queries.
    *   Environment Variables (`python-decouple`) para segredos.

2.  **Frontend**:
    *   Code Splitting (Lazy Load) para rotas.
    *   Axios Interceptors para renovação automática de Token.
    *   Tipagem estrita com TypeScript.

3.  **Segurança**:
    *   CORS restrito aos domínios confiáveis.
    *   Validação de dados de entrada nos Serializers.

## 11. Sugestões de Evolução Futura
*   **Modo Escuro (Dark Mode)**: Suporte nativo via MUI.
*   **Notificações em Tempo Real**: Websockets (Django Channels) para alertas de novos relatórios.
*   **Auditoria**: Logar quem exportou ou visualizou quais dados sensíveis.
*   **Drill-down**: Clicar em uma fatia do gráfico e filtrar a tabela automaticamente.
