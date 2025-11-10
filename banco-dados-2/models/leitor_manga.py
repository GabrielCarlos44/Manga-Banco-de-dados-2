"""
Modelo de relacionamento Leitor-Manga (Tabela Associativa)
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class LeitorManga(Base):
    """
    Tabela associativa entre Leitor e Manga
    Armazena informações de favoritos e progresso de leitura
    """
    __tablename__ = 'leitor_manga'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Chaves estrangeiras
    id_leitor = Column(Integer, ForeignKey('leitores.id_usuario'), nullable=False)
    id_manga = Column(Integer, ForeignKey('mangas.id_manga'), nullable=False)
    
    # Atributos do relacionamento
    data_favorito = Column(DateTime, nullable=True)
    progresso_leitura = Column(Float, default=0.0)  # Percentual de 0.0 a 100.0
    ultimo_capitulo_lido = Column(Integer, default=0)
    
    # Relacionamentos
    leitor = relationship("Leitor", back_populates="leituras")
    manga = relationship("Manga", back_populates="leituras")
    
    def marcar_como_favorito(self):
        """Marca o mangá como favorito"""
        if not self.data_favorito:
            self.data_favorito = datetime.now()
    
    def desmarcar_favorito(self):
        """Desmarca o mangá como favorito"""
        self.data_favorito = None
    
    def atualizar_progresso(self, capitulo):
        """Atualiza o progresso de leitura baseado no capítulo lido"""
        # Garantir que ultimo_capitulo_lido não seja None
        if self.ultimo_capitulo_lido is None:
            self.ultimo_capitulo_lido = 0
            
        if capitulo.numero_capitulo > self.ultimo_capitulo_lido:
            self.ultimo_capitulo_lido = capitulo.numero_capitulo
            
            # Calcula progresso baseado no total de capítulos
            total_capitulos = len(self.manga.capitulos)
            if total_capitulos > 0:
                self.progresso_leitura = round((self.ultimo_capitulo_lido / total_capitulos) * 100, 2)
    
    def __repr__(self):
        return f"<LeitorManga(leitor_id={self.id_leitor}, manga_id={self.id_manga}, progresso={self.progresso_leitura}%)>"
