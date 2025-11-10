"""
Modelo de Gênero
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base


class Genero(Base):
    """
    Modelo de Gênero de mangá
    """
    __tablename__ = 'generos'
    
    id_genero = Column(Integer, primary_key=True, autoincrement=True)
    tipo_genero = Column(String(100), unique=True, nullable=False)
    
    # Relacionamentos
    manga_generos = relationship("MangaGenero", back_populates="genero", cascade="all, delete-orphan")
    
    def renomear(self, novo_nome: str) -> None:
        """Renomeia o gênero"""
        self.tipo_genero = novo_nome
    
    def __repr__(self):
        return f"<Genero(id={self.id_genero}, tipo={self.tipo_genero})>"
