# Ambiente Local - Instruções para Rodar a Aplicação

Este guia explica como configurar e rodar a aplicação localmente. Certifique-se de seguir todos os passos na ordem correta.

---

## Pré-requisitos

- **Python** >= 3.10
- **Docker** e **Docker Compose** instalados
- **Git** instalado

---

## Primeira Execução (Setup Inicial)

Siga estes passos **apenas na primeira vez** que for rodar o projeto.

### 1. Clonar o Repositório

Clone o repositório do projeto para o seu ambiente local:

```bash
git clone https://github.com/ax-comp-scl/machado.git
cd machado
```

---

### 2. Configurar o `.env`

Crie um arquivo `.env` no diretório raiz do projeto, seguindo o formato do arquivo `.env.example`. Preencha as variáveis de ambiente necessárias, como:

```env
DB_NAME=machadosample
DB_USER=username
DB_PASSWORD=userpass
```

---

### 3. Subir os Containers com Docker Compose

No diretório raiz do projeto, execute o seguinte comando para subir os containers do **PostgreSQL** e **Elasticsearch**:

```bash
docker compose up -d
```

Isso criará e iniciará os containers em segundo plano. Para verificar se os containers estão rodando, use:

```bash
docker compose ps
```

---

### 4. Criar e Ativar um Ambiente Virtual (venv)

#### No Linux/Mac:

1. Crie o ambiente virtual:

   ```bash
   python3 -m venv venv
   ```

2. Ative o ambiente virtual:

   ```bash
   source venv/bin/activate
   ```

#### No Windows:

1. Crie o ambiente virtual:

   ```bash
   python -m venv venv
   ```

2. Ative o ambiente virtual:

   ```bash
   .\venv\Scripts\activate
   ```

---

### 5. Instalar as Dependências

No diretório raiz do projeto, instale as dependências listadas no arquivo `setup.py`:

```bash
pip install -e .
```

Isso instalará todas as dependências necessárias para o projeto.

---

### 6. Configurar o Projeto Machado

1. Navegue até a pasta `WEBPROJECT`:

   ```bash
   cd WEBPROJECT
   ```

2. Aplique as migrações do banco de dados:

   ```bash
   python manage.py migrate
   ```

3. Crie um superuser para acessar o painel de administração e fazer autenticação no frontend:

   ```bash
   python manage.py createsuperuser
   ```

   Siga as instruções para definir um nome de usuário, e-mail e senha.

4. Inicie o servidor de desenvolvimento:

   ```bash
   python manage.py runserver
   ```

   A API estará disponível em `http://localhost:8000`.

---

### 7. Acessar o Painel de Administração

Com o servidor rodando, acesse o painel de administração do Django em:

```
http://localhost:8000/admin/
```

Use as credenciais do superuser criado anteriormente para fazer login.

---

## Resumo

### Primeira Execução:
1. Clone o repositório.
2. Configure o arquivo `.env`.
3. Suba os containers com Docker Compose.
4. Crie e ative um ambiente virtual.
5. Instale as dependências.
6. Aplique as migrações e crie um superusuário.

### Execuções Posteriores:
1. Suba os containers (`docker compose up -d`)
2. Ative o ambiente virtual (venv).
3. Inicie o servidor de desenvolvimento (`python manage.py runserver`).