"""
Pacote de modelos do sistema de mangás
"""
from models.usuario import Usuario, Leitor, Administrador
from models.manga import Manga, Status
from models.genero import Genero
from models.manga_genero import MangaGenero
from models.capitulo import Capitulo
from models.avaliacao import Avaliacao
from models.comentario import Comentario
from models.leitor_manga import LeitorManga

__all__ = [
    'Usuario',
    'Leitor',
    'Administrador',
    'Manga',
    'Status',
    'Genero',
    'MangaGenero',
    'Capitulo',
    'Avaliacao',
    'Comentario',
    'LeitorManga',
]
