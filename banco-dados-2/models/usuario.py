"""
Modelo de Usuario com herança para Leitor e Administrador
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import bcrypt
import os


class Usuario(Base):
    """
    Classe base para usuários do sistema
    Implementa herança joined table (tabela por subclasse)
    """
    __tablename__ = 'usuarios'
    
    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nome = Column(String(255), nullable=False)
    senha = Column(String(255), nullable=False)
    tipo = Column(String(50))  # Discriminador para herança
    
    __mapper_args__ = {
        'polymorphic_identity': 'usuario',
        'polymorphic_on': tipo
    }
    
    def __init__(self, **kwargs):
        """Inicializa o usuário e faz hash da senha"""
        if 'senha' in kwargs:
            senha_plain = kwargs.pop('senha')
            kwargs['senha'] = self._hash_senha(senha_plain)
        super().__init__(**kwargs)
    
    @staticmethod
    def _hash_senha(senha: str) -> str:
        """Gera hash bcrypt da senha"""
        rounds = int(os.getenv('BCRYPT_ROUNDS', 12))
        salt = bcrypt.gensalt(rounds=rounds)
        return bcrypt.hashpw(senha.encode('utf-8'), salt).decode('utf-8')
    
    def verificar_senha(self, senha: str) -> bool:
        """Verifica se a senha fornecida corresponde ao hash armazenado"""
        return bcrypt.checkpw(senha.encode('utf-8'), self.senha.encode('utf-8'))
    
    def alterar_senha(self, senha_atual: str, nova_senha: str) -> bool:
        """Altera a senha do usuário"""
        if self.verificar_senha(senha_atual):
            self.senha = self._hash_senha(nova_senha)
            return True
        return False
    
    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, email={self.email}, nome={self.nome})>"


class Leitor(Usuario):
    """
    Leitor herda de Usuario
    """
    __tablename__ = 'leitores'
    
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), primary_key=True)
    codinome = Column(String(100), unique=True, nullable=False)
    
    # Relacionamentos
    comentarios = relationship("Comentario", back_populates="leitor", cascade="all, delete-orphan")
    avaliacoes = relationship("Avaliacao", back_populates="leitor", cascade="all, delete-orphan")
    leituras = relationship("LeitorManga", back_populates="leitor", cascade="all, delete-orphan")
    
    __mapper_args__ = {
        'polymorphic_identity': 'leitor',
    }
    
    def comentar_manga(self, manga, texto: str, session):
        """Adiciona um comentário a um mangá"""
        from models.comentario import Comentario
        from datetime import datetime
        
        comentario = Comentario(
            texto_comentario=texto,
            manga=manga,
            leitor=self,
            data_criacao=datetime.now()
        )
        session.add(comentario)
        return comentario
    
    def avaliar_manga(self, manga, nota: float, session):
        """Avalia um mangá com nota de 0.0 a 5.0"""
        from models.avaliacao import Avaliacao
        
        if not (0.0 <= nota <= 5.0):
            raise ValueError("Nota deve estar entre 0.0 e 5.0")
        
        # Verificar se já existe avaliação
        avaliacao_existente = session.query(Avaliacao).filter_by(
            leitor=self, manga=manga
        ).first()
        
        if avaliacao_existente:
            avaliacao_existente.editar_nota(nota)
            return avaliacao_existente
        
        avaliacao = Avaliacao(nota=nota, leitor=self, manga=manga)
        session.add(avaliacao)
        return avaliacao
    
    def adicionar_favorito(self, manga, session):
        """Adiciona um mangá aos favoritos"""
        from models.leitor_manga import LeitorManga
        from datetime import datetime
        
        leitura_existente = session.query(LeitorManga).filter_by(
            leitor=self, manga=manga
        ).first()
        
        if not leitura_existente:
            leitura = LeitorManga(
                leitor=self,
                manga=manga,
                data_favorito=datetime.now()
            )
            session.add(leitura)
            return leitura
        else:
            leitura_existente.marcar_como_favorito()
            return leitura_existente
    
    def remover_favorito(self, manga, session):
        """Remove um mangá dos favoritos"""
        from models.leitor_manga import LeitorManga
        
        leitura = session.query(LeitorManga).filter_by(
            leitor=self, manga=manga
        ).first()
        
        if leitura:
            leitura.desmarcar_favorito()
    
    def ler_capitulo(self, capitulo, session):
        """Registra leitura de um capítulo"""
        from models.leitor_manga import LeitorManga
        
        leitura = session.query(LeitorManga).filter_by(
            leitor=self, manga=capitulo.manga
        ).first()
        
        if not leitura:
            from datetime import datetime
            leitura = LeitorManga(
                leitor=self,
                manga=capitulo.manga,
                data_favorito=datetime.now()
            )
            session.add(leitura)
        
        leitura.atualizar_progresso(capitulo)
    
    def __repr__(self):
        return f"<Leitor(id={self.id_usuario}, codinome={self.codinome})>"


class Administrador(Usuario):
    """
    Administrador herda de Usuario
    """
    __tablename__ = 'administradores'
    
    id_usuario = Column(Integer, ForeignKey('usuarios.id_usuario'), primary_key=True)
    numero_de_mangas_upados = Column(Integer, default=0)
    
    __mapper_args__ = {
        'polymorphic_identity': 'administrador',
    }
    
    def adicionar_manga(self, manga, session):
        """Adiciona um mangá ao sistema"""
        session.add(manga)
        self.numero_de_mangas_upados += 1
        return manga
    
    def adicionar_capitulo(self, manga, capitulo, session):
        """Adiciona um capítulo a um mangá"""
        manga.adicionar_capitulo(capitulo)
        session.add(capitulo)
        return capitulo
    
    def excluir_manga(self, manga, session):
        """Exclui um mangá do sistema"""
        session.delete(manga)
        self.numero_de_mangas_upados -= 1
    
    def excluir_capitulo(self, manga, capitulo, session):
        """Exclui um capítulo de um mangá"""
        manga.remover_capitulo(capitulo, session)
    
    def editar_manga(self, manga, **kwargs):
        """Edita informações de um mangá"""
        for key, value in kwargs.items():
            if hasattr(manga, key):
                setattr(manga, key, value)
    
    def excluir_comentario(self, comentario, session):
        """Exclui um comentário"""
        session.delete(comentario)
    
    def __repr__(self):
        return f"<Administrador(id={self.id_usuario}, mangas_upados={self.numero_de_mangas_upados})>"
