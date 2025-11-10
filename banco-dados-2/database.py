"""
Configuração da base de dados e sessão SQLAlchemy
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# URL de conexão com o banco de dados
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://manga_user:manga_pass@localhost:5432/manga_system")

# Criar engine
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Mostra SQL no console
    pool_pre_ping=True,  # Verifica conexões antes de usar
)

# Criar sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para os modelos
Base = declarative_base()


def get_db():
    """Retorna uma sessão de banco de dados (generator para FastAPI)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session():
    """Retorna uma sessão de banco de dados (uso direto)"""
    return SessionLocal()
