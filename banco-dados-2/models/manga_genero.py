"""
Modelo de associação Manga-Genero
"""
from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from database import Base


class MangaGenero(Base):
    """
    Modelo de associação entre Manga e Gênero (muitos para muitos)
    """
    __tablename__ = 'manga_genero'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_manga = Column(Integer, ForeignKey('mangas.id_manga', ondelete='CASCADE'), nullable=False)
    id_genero = Column(Integer, ForeignKey('generos.id_genero', ondelete='CASCADE'), nullable=False)
    principal = Column(Boolean, default=False)  # Indica se é o gênero principal
    
    # Relacionamentos
    manga = relationship("Manga", back_populates="manga_generos")
    genero = relationship("Genero", back_populates="manga_generos")
    
    def alterar_genero(self, novo_id_genero: int) -> None:
        """Altera o gênero"""
        self.id_genero = novo_id_genero
    
    def marcar_como_principal(self) -> None:
        """Marca este gênero como principal para o mangá"""
        self.principal = True
    
    def __repr__(self):
        return f"<MangaGenero(manga_id={self.id_manga}, genero_id={self.id_genero}, principal={self.principal})>"
