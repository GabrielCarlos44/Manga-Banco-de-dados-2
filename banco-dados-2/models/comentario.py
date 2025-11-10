"""
Modelo de Comentário
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Comentario(Base):
    """
    Modelo de Comentário em Mangá
    """
    __tablename__ = 'comentarios'
    
    id_comentario = Column(Integer, primary_key=True, autoincrement=True)
    texto_comentario = Column(String(1000), nullable=False)
    numero_curtidas = Column(Integer, default=0)
    data_criacao = Column(DateTime, default=datetime.now, nullable=False)
    
    # Chaves estrangeiras
    id_leitor = Column(Integer, ForeignKey('leitores.id_usuario'), nullable=False)
    id_manga = Column(Integer, ForeignKey('mangas.id_manga'), nullable=False)
    
    # Relacionamentos
    leitor = relationship("Leitor", back_populates="comentarios")
    manga = relationship("Manga", back_populates="comentarios")
    
    def responder_comentario(self, leitor, texto: str):
        """
        Cria uma resposta ao comentário (implementação simplificada)
        Em uma implementação completa, poderia ter uma tabela de respostas
        """
        resposta = Comentario(
            texto_comentario=f"@{self.leitor.codinome}: {texto}",
            leitor=leitor,
            manga=self.manga,
            data_criacao=datetime.now()
        )
        return resposta
    
    def editar_comentario(self, novo_texto: str):
        """Edita o texto do comentário"""
        self.texto_comentario = novo_texto
    
    def curtir_comentario(self):
        """Incrementa o número de curtidas"""
        self.numero_curtidas += 1
    
    def __repr__(self):
        return f"<Comentario(id={self.id_comentario}, leitor={self.leitor.codinome if self.leitor else 'N/A'}, curtidas={self.numero_curtidas})>"
