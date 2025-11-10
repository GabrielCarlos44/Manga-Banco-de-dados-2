# Nome do Projeto  
**Sistema de Gerenciamente de Mangás (Aplicação com Python, Docker, PostgreSQL e SQLAlchemy)**

## 1. Descrição Geral

Este projeto consiste no desenvolvimento de um sistema para leitura de mangás, com foco em modelagem de dados e aplicação prática de conceitos de Banco de Dados II.  
A aplicação utiliza Python com o framework SQLAlchemy para ORM (Object-Relational Mapping), PostgreSQL como banco de dados relacional e Docker para gerenciamento de containers, garantindo portabilidade e facilidade de implantação.

O objetivo acadêmico é demonstrar a evolução da modelagem conceitual, lógica e física, além da implementação de uma API capaz de manipular entidades do sistema utilizando boas práticas de arquitetura.

---

## 2. Estrutura do Projeto

```
/
├── app/
│   ├── src/
│   │   ├── models/
│   │   ├── controllers/
│   │   ├── database/
│   │   └── main.py
│   ├── requirements.txt
│   ├── uv.lock (gerado automaticamente)
│   └── entrypoint.sh
├── docker-compose.yml
├── Dockerfile
└── README.md
```

---

## 3. Tecnologias Utilizadas

| Tecnologia | Descrição |
|------------|-----------|
| Python 3.x | Lógica da aplicação e ORM |
| SQLAlchemy | Mapeamento objeto-relacional |
| Alembic | Controle de versão de banco de dados |
| PostgreSQL | Banco de dados relacional |
| Docker / Docker Compose | Infraestrutura e orquestração de containers |

---

## 4. Pré-Requisitos

Antes de executar a aplicação, certifique-se de possuir:

- Docker e Docker Compose instalados
- Git para versionamento
- Python 3.10+ (caso execute sem Docker)

---

## 5. Configuração e Execução

### 5.1 Clonar o repositório

```sh
git clone https://github.com/GabrielCarlos44/Manga-Banco-de-dados-2.git
cd Manga-Banco-de-dados-2
```

### 5.2 Subir a aplicação com Docker

```sh
docker compose up --build
```

Após a execução, os containers serão inicializados automaticamente.  
O banco de dados estará disponível em:

```
host: localhost
porta: 5432
banco de dados: manga_system
usuário: manga_user
senha: manga_pass
```

---

## 6. Execeutando a aplicação

Para executar a aplicação é necessário os seguintes comandos:

docker compose up --build (para subir o container)

No segundo passo você irá abrir no Docker o container: "manga_App" e ir em "EXEC"

Os comandos serão:

uv run python -m alambic upgrade head(para fazer o migration de dados)

uv run python -m alambic seed_data.py (para ppopular o banco)

uv run python -m app_cli.py (para carregar o menu interarivo)



## 7. Obsevando o banco de dados

Nessa aplicação utilizamos o db Postgres

para visualizar o banco de dados é necessário o programa do Postgres ou algum outro que o suporte

Utilizamos o DBEAVER para visualizar as tabelas utilizando os seguintes passos:

-abrir DBEAVER
-conectar o banco
- localhost: manga_system
- usuario: manga_user
- senha: manga_pass

aparece o mangasystem e segue o caminho

Mangasystem > Banco de Dados > manga_system > esquemas > public > tabelas


## 8. Autores

Projeto desenvolvido para fins acadêmicos por:

**Gabriel Carlos Nascimento Machado**  
**Josue Xavier Silva**
Disciplina: Banco de Dados II – Universidade Federal do Sul e Sudeste do Pará (UNIFESSPA)
