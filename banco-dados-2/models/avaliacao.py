"""
Modelo de Avaliação
"""
from sqlalchemy import Column, Integer, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from database import Base


class Avaliacao(Base):
    """
    Modelo de Avaliação de Mangá
    """
    __tablename__ = 'avaliacoes'
    
    id_avaliacao = Column(Integer, primary_key=True, autoincrement=True)
    nota = Column(Float, nullable=False)
    
    # Chaves estrangeiras
    id_leitor = Column(Integer, ForeignKey('leitores.id_usuario'), nullable=False)
    id_manga = Column(Integer, ForeignKey('mangas.id_manga'), nullable=False)
    
    # Relacionamentos
    leitor = relationship("Leitor", back_populates="avaliacoes")
    manga = relationship("Manga", back_populates="avaliacoes")
    
    # Constraint para nota entre 0.0 e 5.0
    __table_args__ = (
        CheckConstraint('nota >= 0.0 AND nota <= 5.0', name='check_nota_range'),
    )
    
    def editar_avaliacao(self, nova_nota: float) -> None:
        """Edita a nota da avaliação"""
        if 0.0 <= nova_nota <= 5.0:
            self.nota = nova_nota
        else:
            raise ValueError("Nota deve estar entre 0.0 e 5.0")
    
    def remover_edicao(self):
        """Remove a avaliação (marca para deleção)"""
        # Este método seria usado em conjunto com session.delete()
        pass
    
    def __repr__(self):
        return f"<Avaliacao(id={self.id_avaliacao}, nota={self.nota}, leitor_id={self.id_leitor}, manga_id={self.id_manga})>"
