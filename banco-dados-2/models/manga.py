"""
Modelo de Manga com enumerações de Status
"""
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class Status(enum.Enum):
    """Status do mangá"""
    HIATO = "Hiato"
    CONCLUIDO = "Concluido"
    EM_ANDAMENTO = "Em_andamento"


class Manga(Base):
    """
    Modelo de Mangá
    """
    __tablename__ = 'mangas'
    
    id_manga = Column(Integer, primary_key=True, autoincrement=True)
    titulo_manga = Column(String(255), nullable=False, index=True)
    autor = Column(String(255), nullable=False)
    status = Column(SQLEnum(Status), nullable=False, default=Status.EM_ANDAMENTO)
    data_criacao = Column(DateTime, nullable=False, default=datetime.now)
    
    # Relacionamentos
    capitulos = relationship("Capitulo", back_populates="manga", cascade="all, delete-orphan")
    comentarios = relationship("Comentario", back_populates="manga", cascade="all, delete-orphan")
    avaliacoes = relationship("Avaliacao", back_populates="manga", cascade="all, delete-orphan")
    leituras = relationship("LeitorManga", back_populates="manga", cascade="all, delete-orphan")
    manga_generos = relationship("MangaGenero", back_populates="manga", cascade="all, delete-orphan")
    
    def adicionar_capitulo(self, capitulo):
        """Adiciona um capítulo ao mangá"""
        capitulo.manga = self
        self.capitulos.append(capitulo)
    
    def remover_capitulo(self, capitulo, session):
        """Remove um capítulo do mangá"""
        if capitulo in self.capitulos:
            session.delete(capitulo)
            self.capitulos.remove(capitulo)
    
    def adicionar_comentarios(self, leitor, texto: str):
        """Adiciona um comentário ao mangá"""
        from models.comentario import Comentario
        from datetime import datetime
        
        comentario = Comentario(
            texto_comentario=texto,
            manga=self,
            leitor=leitor,
            data_criacao=datetime.now()
        )
        return comentario
    
    def obter_media_avaliacoes(self) -> float:
        """Calcula a média das avaliações do mangá"""
        if not self.avaliacoes:
            return 0.0
        
        total = sum(avaliacao.nota for avaliacao in self.avaliacoes)
        return round(total / len(self.avaliacoes), 2)
    
    def __repr__(self):
        return f"<Manga(id={self.id_manga}, titulo={self.titulo_manga}, autor={self.autor})>"
