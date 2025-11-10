"""
Script para popular o banco de dados com dados de exemplo
Execute: python -m alembic.seed_data
ou: uv run python -m alembic.seed_data
"""
from datetime import datetime
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import (
    Usuario, Leitor, Administrador,
    Manga, Status, Genero, MangaGenero,
    Capitulo, Avaliacao, Comentario, LeitorManga
)


def limpar_dados(session: Session):
    """Remove todos os dados do banco"""
    print("  Limpando dados existentes...")
    
    # A ordem importa por causa das FKs
    session.query(Comentario).delete()
    session.query(Avaliacao).delete()
    session.query(LeitorManga).delete()
    session.query(Capitulo).delete()
    session.query(MangaGenero).delete()
    session.query(Manga).delete()
    session.query(Genero).delete()
    session.query(Leitor).delete()
    session.query(Administrador).delete()
    session.query(Usuario).delete()
    
    session.commit()
    print("✓ Dados removidos\n")


def criar_generos(session: Session):
    """Cria os gêneros de mangá"""
    print(" Criando gêneros...")
    
    generos_nomes = [
        "Ação", "Aventura", "Fantasia", "Ficção Científica",
        "Terror/Horror", "Romance", "Comédia", "Drama",
        "Slice of Life", "Mistério", "Esporte", "Histórico", "Sobrenatural"
    ]
    
    generos = [Genero(tipo_genero=nome) for nome in generos_nomes]
    session.add_all(generos)
    session.commit()
    
    print(f"✓ Criados: {len(generos)} gêneros")
    return generos


def criar_usuarios(session: Session):
    """Cria usuários (admin e leitores)"""
    print(" Criando usuários...")
    
    # Administrador
    admin = Administrador(
        email="admin@manga.com",
        nome="Admin Principal",
        senha="admin123",
        numero_de_mangas_upados=0
    )
    session.add(admin)
    
    # Leitores
    leitores = [
        Leitor(
            email="leitor1@manga.com",
            nome="João Silva",
            senha="senha123",
            codinome="JoaoMangaFan"
        ),
        Leitor(
            email="leitor2@manga.com",
            nome="Maria Santos",
            senha="senha456",
            codinome="MariOtaku"
        ),
        Leitor(
            email="leitor3@manga.com",
            nome="Pedro Costa",
            senha="senha789",
            codinome="PedroLeitor"
        )
    ]
    
    session.add_all(leitores)
    session.commit()
    
    print(f"✓ Criados: 1 admin + {len(leitores)} leitores")
    
    return admin, leitores


def criar_mangas(session: Session, admin: Administrador, generos: list):
    """Cria mangás via administrador"""
    print("\n Criando mangás...")
    
    mangas_data = [
        {
            "titulo_manga": "One Piece",
            "autor": "Eiichiro Oda",
            "status": Status.EM_ANDAMENTO,
            "generos": ["Aventura", "Ação"]  # Múltiplos gêneros
        },
        {
            "titulo_manga": "Death Note",
            "autor": "Tsugumi Ohba",
            "status": Status.CONCLUIDO,
            "generos": ["Mistério", "Sobrenatural"]
        },
        {
            "titulo_manga": "Attack on Titan",
            "autor": "Hajime Isayama",
            "status": Status.CONCLUIDO,
            "generos": ["Ação", "Drama"]
        },
        {
            "titulo_manga": "Naruto",
            "autor": "Masashi Kishimoto",
            "status": Status.CONCLUIDO,
            "generos": ["Ação", "Aventura"]
        },
        {
            "titulo_manga": "My Hero Academia",
            "autor": "Kohei Horikoshi",
            "status": Status.EM_ANDAMENTO,
            "generos": ["Ação", "Sobrenatural"]
        }
    ]
    
    mangas = []
    for data in mangas_data:
        generos_nomes = data.pop("generos")
        manga = Manga(**data)
        admin.adicionar_manga(manga, session)
        
        # Adicionar gêneros ao mangá
        for i, genero_nome in enumerate(generos_nomes):
            genero = session.query(Genero).filter_by(tipo_genero=genero_nome).first()
            if genero:
                manga_genero = MangaGenero(
                    manga=manga,
                    genero=genero,
                    principal=(i == 0)  # Primeiro gênero é o principal
                )
                session.add(manga_genero)
        
        mangas.append(manga)
    
    session.commit()
    
    print(f"✓ Criados: {len(mangas)} mangás")
    
    return mangas


def criar_capitulos(session: Session, mangas: list):
    """Cria capítulos para os mangás"""
    print("\n Criando capítulos...")
    
    capitulos_data = [
        # One Piece (mangas[0])
        {"titulo_capitulo": "Romance Dawn", "numero_capitulo": 1, "numero_paginas": 53, "manga": mangas[0]},
        {"titulo_capitulo": "Buggy o Palhaço", "numero_capitulo": 2, "numero_paginas": 19, "manga": mangas[0]},
        {"titulo_capitulo": "O Grande Espadachim", "numero_capitulo": 3, "numero_paginas": 20, "manga": mangas[0]},
        
        # Death Note (mangas[1])
        {"titulo_capitulo": "Tédio", "numero_capitulo": 1, "numero_paginas": 58, "manga": mangas[1]},
        {"titulo_capitulo": "Confronto", "numero_capitulo": 2, "numero_paginas": 18, "manga": mangas[1]},
        
        # Attack on Titan (mangas[2])
        {"titulo_capitulo": "Para Você, Daqui a 2000 Anos", "numero_capitulo": 1, "numero_paginas": 51, "manga": mangas[2]},
        {"titulo_capitulo": "Aquele Dia", "numero_capitulo": 2, "numero_paginas": 46, "manga": mangas[2]},
    ]
    
    capitulos = [Capitulo(**data) for data in capitulos_data]
    session.add_all(capitulos)
    session.commit()
    
    print(f"✓ Criados: {len(capitulos)} capítulos")
    
    return capitulos


def criar_avaliacoes(session: Session, leitores: list, mangas: list):
    """Cria avaliações dos leitores"""
    print("\n Criando avaliações...")
    
    avaliacoes_data = [
        # Leitor 1 (JoaoMangaFan)
        {"leitor": leitores[0], "manga": mangas[0], "nota": 5.0},
        {"leitor": leitores[0], "manga": mangas[1], "nota": 4.8},
        
        # Leitor 2 (MariOtaku)
        {"leitor": leitores[1], "manga": mangas[0], "nota": 4.5},
        {"leitor": leitores[1], "manga": mangas[2], "nota": 5.0},
        
        # Leitor 3 (PedroLeitor)
        {"leitor": leitores[2], "manga": mangas[1], "nota": 4.9},
        {"leitor": leitores[2], "manga": mangas[2], "nota": 4.7},
        {"leitor": leitores[2], "manga": mangas[3], "nota": 4.6},
    ]
    
    for data in avaliacoes_data:
        data['leitor'].avaliar_manga(data['manga'], data['nota'], session)
    
    session.commit()
    
    print(f"✓ Criadas: {len(avaliacoes_data)} avaliações")


def criar_comentarios(session: Session, leitores: list, mangas: list):
    """Cria comentários dos leitores"""
    print("\n Criando comentários...")
    
    comentarios_data = [
        {"leitor": leitores[0], "manga": mangas[0], "texto": "Melhor mangá de todos os tempos!"},
        {"leitor": leitores[1], "manga": mangas[0], "texto": "A história é incrível, nunca decepciona!"},
        {"leitor": leitores[1], "manga": mangas[1], "texto": "Thriller psicológico perfeito"},
        {"leitor": leitores[2], "manga": mangas[2], "texto": "Final épico, chorei muito"},
    ]
    
    comentarios = []
    for data in comentarios_data:
        comentario = data['leitor'].comentar_manga(data['manga'], data['texto'], session)
        comentarios.append(comentario)
    
    session.commit()
    
    print(f"✓ Criados: {len(comentarios)} comentários")
    
    return comentarios


def criar_favoritos(session: Session, leitores: list, mangas: list):
    """Adiciona mangás favoritos"""
    print("\n  Criando favoritos...")
    
    favoritos_data = [
        {"leitor": leitores[0], "manga": mangas[0]},  # JoaoMangaFan -> One Piece
        {"leitor": leitores[0], "manga": mangas[1]},  # JoaoMangaFan -> Death Note
        {"leitor": leitores[1], "manga": mangas[0]},  # MariOtaku -> One Piece
        {"leitor": leitores[1], "manga": mangas[2]},  # MariOtaku -> Attack on Titan
        {"leitor": leitores[2], "manga": mangas[1]},  # PedroLeitor -> Death Note
    ]
    
    for data in favoritos_data:
        data['leitor'].adicionar_favorito(data['manga'], session)
    
    session.commit()
    
    print(f"✓ Criados: {len(favoritos_data)} favoritos")


def criar_leituras(session: Session, leitores: list, capitulos: list):
    """Registra leituras de capítulos"""
    print("\n Registrando leituras...")
    
    leituras_data = [
        {"leitor": leitores[0], "capitulo": capitulos[0]},  # JoaoMangaFan -> One Piece Cap 1
        {"leitor": leitores[0], "capitulo": capitulos[1]},  # JoaoMangaFan -> One Piece Cap 2
        {"leitor": leitores[1], "capitulo": capitulos[3]},  # MariOtaku -> Death Note Cap 1
        {"leitor": leitores[2], "capitulo": capitulos[5]},  # PedroLeitor -> AoT Cap 1
        {"leitor": leitores[2], "capitulo": capitulos[6]},  # PedroLeitor -> AoT Cap 2
    ]
    
    for data in leituras_data:
        data['leitor'].ler_capitulo(data['capitulo'], session)
    
    session.commit()
    
    print(f"✓ Registradas: {len(leituras_data)} leituras")


def curtir_comentarios(session: Session, comentarios: list):
    """Adiciona curtidas nos comentários"""
    print("\n Adicionando curtidas...")
    
    total_curtidas = 0
    for comentario in comentarios[:2]:  # Apenas nos 2 primeiros
        comentario.curtir_comentario()
        comentario.curtir_comentario()
        total_curtidas += 2
    
    session.commit()
    
    print(f"✓ Adicionadas: {total_curtidas} curtidas")


def seed():
    """Função principal de seed"""
    print("="*80)
    print("  SEED DATABASE - Populando Banco de Dados")
    print("="*80)
    print()
    
    session = SessionLocal()
    
    try:
        # Limpar dados existentes
        limpar_dados(session)
        
        # Criar dados
        admin, leitores = criar_usuarios(session)
        generos = criar_generos(session)
        mangas = criar_mangas(session, admin, generos)
        capitulos = criar_capitulos(session, mangas)
        criar_avaliacoes(session, leitores, mangas)
        comentarios = criar_comentarios(session, leitores, mangas)
        criar_favoritos(session, leitores, mangas)
        criar_leituras(session, leitores, capitulos)
        curtir_comentarios(session, comentarios)
        
        print()
        print("="*80)
        print("  ✓ SEED CONCLUÍDO COM SUCESSO")
        print("="*80)
        print()
        print(f"   Usuários: {len(leitores) + 1} (1 admin + {len(leitores)} leitores)")
        print(f"   Gêneros: {len(generos)}")
        print(f"   Mangás: {len(mangas)}")
        print(f"   Capítulos: {len(capitulos)}")
        print(f"   Avaliações: {session.query(Avaliacao).count()}")
        print(f"   Comentários: {len(comentarios)}")
        print(f"   Favoritos: {session.query(LeitorManga).filter(LeitorManga.data_favorito.isnot(None)).count()}")
        print()
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Erro durante seed: {e}")
        raise
        
    finally:
        session.close()


if __name__ == "__main__":
    seed()
