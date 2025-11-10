"""
Modelo de Capítulo
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Capitulo(Base):
    """
    Modelo de Capítulo de Mangá
    """
    __tablename__ = 'capitulos'
    
    id_capitulo = Column(Integer, primary_key=True, autoincrement=True)
    titulo_capitulo = Column(String(255), nullable=False)
    numero_capitulo = Column(Integer, nullable=False)
    numero_paginas = Column(Integer, nullable=False, default=0)
    paginas_lidas = Column(Integer, default=0)
    data_publicacao = Column(DateTime, nullable=False, default=datetime.now)
    
    # Chave estrangeira
    id_manga = Column(Integer, ForeignKey('mangas.id_manga', ondelete='CASCADE'), nullable=False)
    
    # Relacionamento
    manga = relationship("Manga", back_populates="capitulos")
    
    def get_paginas_lidas(self) -> int:
        """Retorna o número de páginas lidas"""
        return self.paginas_lidas
    
    def marcar_progresso(self, paginas: int):
        """Marca o progresso de leitura"""
        if 0 <= paginas <= self.numero_paginas:
            self.paginas_lidas = paginas
    
    def concluir(self):
        """Marca o capítulo como concluído"""
        self.paginas_lidas = self.numero_paginas
    
    def __repr__(self):
        return f"<Capitulo(id={self.id_capitulo}, numero={self.numero_capitulo}, titulo={self.titulo_capitulo})>"
