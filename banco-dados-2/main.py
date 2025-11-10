"""
Sistema de Gerenciamento de Mangás
Trabalho de Banco de Dados II - UNIFESSPA

Este módulo demonstra:
- Consultas complexas com subconsultas e agregações
- Operações CRUD completas
- Navegação por relacionamentos ORM
- Herança e polimorfismo
- Transações e tratamento de exceções
"""
from datetime import datetime
from sqlalchemy import func, and_, or_
from database import SessionLocal
from models import (
    Usuario, Leitor, Administrador,
    Manga, Status, Genero,
    Capitulo, Avaliacao, Comentario, LeitorManga
)


def print_separator(title=""):
    """Imprime um separador visual"""
    print("\n" + "="*80)
    if title:
        print(f"  {title}")
        print("="*80)
    print()


def consulta_complexa_1(session):
    """
    CONSULTA COMPLEXA 1: 
    Encontrar mangás com média de avaliação >= 4.5, 
    que tenham mais de 1 comentário,
    ordenados por média de avaliação decrescente
    """
    print_separator("CONSULTA COMPLEXA 1: Mangás Bem Avaliados com Engajamento")
    
    print("Critérios:")
    print("  - Média de avaliação >= 4.5")
    print("  - Pelo menos 2 comentários")
    print("  - Ordenados por média de avaliação (decrescente)")
    print()
    
    # Subconsulta para calcular média de avaliações
    subquery_media = (
        session.query(
            Avaliacao.id_manga,
            func.avg(Avaliacao.nota).label('media_nota'),
            func.count(Avaliacao.id_avaliacao).label('total_avaliacoes')
        )
        .group_by(Avaliacao.id_manga)
        .having(func.avg(Avaliacao.nota) >= 4.5)
        .subquery()
    )
    
    # Subconsulta para contar comentários
    subquery_comentarios = (
        session.query(
            Comentario.id_manga,
            func.count(Comentario.id_comentario).label('total_comentarios')
        )
        .group_by(Comentario.id_manga)
        .having(func.count(Comentario.id_comentario) >= 2)
        .subquery()
    )
    
    # Consulta principal
    resultados = (
        session.query(
            Manga,
            subquery_media.c.media_nota,
            subquery_media.c.total_avaliacoes,
            subquery_comentarios.c.total_comentarios
        )
        .join(subquery_media, Manga.id_manga == subquery_media.c.id_manga)
        .join(subquery_comentarios, Manga.id_manga == subquery_comentarios.c.id_manga)
        .order_by(subquery_media.c.media_nota.desc())
        .all()
    )
    
    print(f"Total de resultados: {len(resultados)}\n")
    
    for manga, media, total_aval, total_coment in resultados:
        print(f"📚 {manga.titulo_manga}")
        print(f"   Autor: {manga.autor}")
        print(f"   Gênero: {manga.genero.value}")
        print(f"   Status: {manga.status.value}")
        print(f"   ⭐ Média: {float(media):.2f} ({total_aval} avaliações)")
        print(f"   💬 Comentários: {total_coment}")
        print()


def consulta_complexa_2(session):
    """
    CONSULTA COMPLEXA 2:
    Encontrar leitores que:
    - Possuem mais de 1 favorito
    - Avaliaram pelo menos 2 mangás
    - Têm progresso de leitura > 50% em pelo menos um mangá
    Mostrar quantidade de favoritos, avaliações e progresso médio
    """
    print_separator("CONSULTA COMPLEXA 2: Leitores Ativos e Engajados")
    
    print("Critérios:")
    print("  - Mais de 1 mangá favorito")
    print("  - Pelo menos 2 avaliações")
    print("  - Progresso > 50% em pelo menos um mangá")
    print()
    
    # Subconsulta para favoritos
    subquery_favoritos = (
        session.query(
            LeitorManga.id_leitor,
            func.count(LeitorManga.id).label('total_favoritos')
        )
        .filter(LeitorManga.data_favorito.isnot(None))
        .group_by(LeitorManga.id_leitor)
        .having(func.count(LeitorManga.id) > 1)
        .subquery()
    )
    
    # Subconsulta para avaliações
    subquery_avaliacoes = (
        session.query(
            Avaliacao.id_leitor,
            func.count(Avaliacao.id_avaliacao).label('total_avaliacoes'),
            func.avg(Avaliacao.nota).label('media_notas_dadas')
        )
        .group_by(Avaliacao.id_leitor)
        .having(func.count(Avaliacao.id_avaliacao) >= 2)
        .subquery()
    )
    
    # Subconsulta para progresso
    subquery_progresso = (
        session.query(
            LeitorManga.id_leitor,
            func.avg(LeitorManga.progresso_leitura).label('progresso_medio')
        )
        .filter(LeitorManga.progresso_leitura > 50.0)
        .group_by(LeitorManga.id_leitor)
        .subquery()
    )
    
    # Consulta principal
    resultados = (
        session.query(
            Leitor,
            subquery_favoritos.c.total_favoritos,
            subquery_avaliacoes.c.total_avaliacoes,
            subquery_avaliacoes.c.media_notas_dadas,
            subquery_progresso.c.progresso_medio
        )
        .join(subquery_favoritos, Leitor.id_usuario == subquery_favoritos.c.id_leitor)
        .join(subquery_avaliacoes, Leitor.id_usuario == subquery_avaliacoes.c.id_leitor)
        .join(subquery_progresso, Leitor.id_usuario == subquery_progresso.c.id_leitor)
        .all()
    )
    
    print(f"Total de resultados: {len(resultados)}\n")
    
    for leitor, favoritos, avaliacoes, media_notas, progresso in resultados:
        print(f"👤 {leitor.codinome} ({leitor.nome})")
        print(f"   Email: {leitor.email}")
        print(f"   ❤️ Favoritos: {favoritos}")
        print(f"   ⭐ Avaliações: {avaliacoes} (média dada: {float(media_notas):.2f})")
        print(f"   📖 Progresso médio: {float(progresso):.2f}%")
        print()


def demonstrar_crud(session):
    """Demonstra operações CRUD completas"""
    print_separator("DEMONSTRAÇÃO DE CRUD COMPLETO")
    
    # CREATE
    print("1️⃣  CREATE - Criando novo mangá e capítulo")
    novo_manga = Manga(
        titulo_manga="Demon Slayer",
        autor="Koyoharu Gotouge",
        status=Status.CONCLUIDO,
        genero=Genero.ACAO
    )
    session.add(novo_manga)
    session.commit()
    print(f"   ✓ Mangá criado: {novo_manga}")
    
    novo_capitulo = Capitulo(
        titulo_capitulo="Crueldade",
        numero_capitulo=1,
        numero_paginas=51,
        manga=novo_manga
    )
    session.add(novo_capitulo)
    session.commit()
    print(f"   ✓ Capítulo criado: {novo_capitulo}\n")
    
    # READ
    print("2️⃣  READ - Consultando mangás de Ação")
    mangas_acao = session.query(Manga).filter(Manga.genero == Genero.ACAO).all()
    print(f"   Total de mangás de Ação: {len(mangas_acao)}")
    for manga in mangas_acao:
        print(f"   - {manga.titulo_manga} ({manga.status.value})")
    print()
    
    # UPDATE
    print("3️⃣  UPDATE - Atualizando status do mangá")
    print(f"   Status antes: {novo_manga.status.value}")
    novo_manga.status = Status.HIATO
    session.commit()
    print(f"   Status depois: {novo_manga.status.value}\n")
    
    # DELETE
    print("4️⃣  DELETE - Removendo capítulo e mangá")
    session.delete(novo_capitulo)
    session.commit()
    print(f"   ✓ Capítulo removido")
    
    session.delete(novo_manga)
    session.commit()
    print(f"   ✓ Mangá removido\n")


def demonstrar_relacionamentos(session):
    """Demonstra navegação por relacionamentos"""
    print_separator("DEMONSTRAÇÃO DE RELACIONAMENTOS")
    
    # Obter um leitor
    leitor = session.query(Leitor).filter(Leitor.codinome == "JoaoMangaFan").first()
    
    if leitor:
        print(f"👤 Leitor: {leitor.codinome}")
        print(f"\n📚 Mangás Favoritos:")
        for leitura in leitor.leituras:
            if leitura.data_favorito:
                print(f"   - {leitura.manga.titulo_manga} (Progresso: {leitura.progresso_leitura}%)")
        
        print(f"\n⭐ Avaliações:")
        for avaliacao in leitor.avaliacoes:
            print(f"   - {avaliacao.manga.titulo_manga}: {avaliacao.nota}/5.0")
        
        print(f"\n💬 Comentários:")
        for comentario in leitor.comentarios:
            print(f"   - {comentario.manga.titulo_manga}: \"{comentario.texto_comentario}\"")
            print(f"     (👍 {comentario.numero_curtidas} curtidas)")


def demonstrar_heranca(session):
    """Demonstra polimorfismo e herança"""
    print_separator("DEMONSTRAÇÃO DE HERANÇA E POLIMORFISMO")
    
    print("Todos os usuários do sistema:\n")
    usuarios = session.query(Usuario).all()
    
    for usuario in usuarios:
        print(f"  Tipo: {usuario.tipo.upper()}")
        print(f"  Nome: {usuario.nome}")
        print(f"  Email: {usuario.email}")
        
        if isinstance(usuario, Administrador):
            print(f"  Mangás Upados: {usuario.numero_de_mangas_upados}")
        elif isinstance(usuario, Leitor):
            print(f"  Codinome: {usuario.codinome}")
            print(f"  Avaliações: {len(usuario.avaliacoes)}")
        
        print()


def demonstrar_transacoes(session):
    """Demonstra tratamento de transações e exceções"""
    print_separator("DEMONSTRAÇÃO DE TRANSAÇÕES E TRATAMENTO DE EXCEÇÕES")
    
    print("Tentando criar avaliação com nota inválida...\n")
    
    leitor = session.query(Leitor).first()
    manga = session.query(Manga).first()
    
    try:
        # Tentar criar avaliação com nota fora do range
        avaliacao_invalida = Avaliacao(
            nota=10.0,  # Nota inválida (máximo é 5.0)
            leitor=leitor,
            manga=manga
        )
        session.add(avaliacao_invalida)
        session.commit()
        print("✓ Avaliação criada (não deveria chegar aqui)")
        
    except Exception as e:
        session.rollback()
        print(f"✗ Erro capturado (esperado): {type(e).__name__}")
        print(f"  Mensagem: {str(e)}")
        print("  Transação revertida com sucesso!")
    
    print("\nTentando criar avaliação válida...\n")
    
    try:
        avaliacao_valida = Avaliacao(
            nota=4.5,
            leitor=leitor,
            manga=manga
        )
        session.add(avaliacao_valida)
        session.commit()
        print("✓ Avaliação criada com sucesso!")
        
        # Remover para não afetar outros testes
        session.delete(avaliacao_valida)
        session.commit()
        
    except Exception as e:
        session.rollback()
        print(f"✗ Erro inesperado: {e}")


def estatisticas_gerais(session):
    """Mostra estatísticas gerais do sistema"""
    print_separator("ESTATÍSTICAS GERAIS DO SISTEMA")
    
    total_usuarios = session.query(Usuario).count()
    total_leitores = session.query(Leitor).count()
    total_admins = session.query(Administrador).count()
    total_mangas = session.query(Manga).count()
    total_capitulos = session.query(Capitulo).count()
    total_avaliacoes = session.query(Avaliacao).count()
    total_comentarios = session.query(Comentario).count()
    
    print(f"👥 Usuários: {total_usuarios}")
    print(f"   - Leitores: {total_leitores}")
    print(f"   - Administradores: {total_admins}")
    print(f"\n📚 Mangás: {total_mangas}")
    print(f"📖 Capítulos: {total_capitulos}")
    print(f"⭐ Avaliações: {total_avaliacoes}")
    print(f"💬 Comentários: {total_comentarios}")
    
    # Mangá mais bem avaliado
    manga_top = (
        session.query(
            Manga.titulo_manga,
            func.avg(Avaliacao.nota).label('media')
        )
        .join(Avaliacao)
        .group_by(Manga.titulo_manga)
        .order_by(func.avg(Avaliacao.nota).desc())
        .first()
    )
    
    if manga_top:
        print(f"\n🏆 Mangá mais bem avaliado: {manga_top[0]} ({float(manga_top[1]):.2f}/5.0)")


def main():
    """Função principal - Demonstra funcionalidades do sistema"""
    print("\n" + "="*80)
    print("  SISTEMA DE GERENCIAMENTO DE MANGÁS")
    print("  Trabalho de Banco de Dados II - UNIFESSPA")
    print("  SQLAlchemy + PostgreSQL + Alembic")
    print("="*80 + "\n")
    
    # Criar sessão
    session = SessionLocal()
    
    try:
        # Verificar se existem dados
        total_usuarios = session.query(Usuario).count()
        
        if total_usuarios == 0:
            print("⚠️  AVISO: Banco de dados vazio!")
            print("\nPara popular o banco, execute:")
            print("  uv run python alembic/seed_data.py")
            print("  ou")
            print("  python alembic/seed_data.py")
            print("\nAplicando migrations primeiro se necessário:")
            print("  uv run alembic upgrade head\n")
            return
        
        # Executar demonstrações
        estatisticas_gerais(session)
        demonstrar_heranca(session)
        demonstrar_relacionamentos(session)
        consulta_complexa_1(session)
        consulta_complexa_2(session)
        demonstrar_crud(session)
        demonstrar_transacoes(session)
        
        print_separator("EXECUÇÃO CONCLUÍDA COM SUCESSO")
        
    except Exception as e:
        print(f"\n✗ Erro durante execução: {e}")
        session.rollback()
        raise
        
    finally:
        session.close()


if __name__ == "__main__":
    main()
