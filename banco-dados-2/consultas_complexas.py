"""
Consultas Complexas usando SQLAlchemy ORM
Demonstra queries avançadas com joins, agregações e filtros compostos
"""

from sqlalchemy import func, and_, or_, desc, case, text
from sqlalchemy.orm import joinedload, selectinload
from database import get_session
from models import (
    Manga, Capitulo, Genero, MangaGenero, 
    Usuario, Leitor, Administrador,
    Avaliacao, Comentario, LeitorManga
)


def consulta_1_top_mangas_avaliados():
    """
    Consulta Complexa 1: Top 5 Mangás Mais Bem Avaliados
    
    Utiliza:
    - JOIN entre Manga e Avaliacao
    - Agregação com AVG e COUNT
    - GROUP BY
    - ORDER BY
    - LIMIT
    - LEFT JOIN para incluir mangás sem avaliação
    """
    print("\n" + "="*80)
    print("CONSULTA 1: Top 5 Mangás Mais Bem Avaliados (com média e total de avaliações)")
    print("="*80 + "\n")
    
    session = get_session()
    
    try:
        # Query ORM complexa
        resultados = (
            session.query(
                Manga.titulo_manga,
                Manga.autor,
                Manga.status,
                func.avg(Avaliacao.nota).label('media_avaliacao'),
                func.count(Avaliacao.id_avaliacao).label('total_avaliacoes')
            )
            .outerjoin(Avaliacao, Manga.id_manga == Avaliacao.id_manga)
            .group_by(Manga.id_manga, Manga.titulo_manga, Manga.autor, Manga.status)
            .having(func.count(Avaliacao.id_avaliacao) > 0)  # Apenas com avaliações
            .order_by(desc('media_avaliacao'), desc('total_avaliacoes'))
            .limit(5)
            .all()
        )
        
        print(f"{'Título':<30} {'Autor':<20} {'Status':<15} {'Média':<10} {'Avaliações':<12}")
        print("-" * 90)
        
        for titulo, autor, status, media, total in resultados:
            print(f"{titulo:<30} {autor:<20} {status.value:<15} {media:>7.2f} {total:>10}")
        
        print(f"\n✓ Total de mangás encontrados: {len(resultados)}")
        
        # Mostrar SQL gerado
        print("\n--- SQL Equivalente Gerado pelo ORM ---")
        from sqlalchemy.dialects import postgresql
        query = (
            session.query(
                Manga.titulo_manga,
                Manga.autor,
                Manga.status,
                func.avg(Avaliacao.nota).label('media_avaliacao'),
                func.count(Avaliacao.id_avaliacao).label('total_avaliacoes')
            )
            .outerjoin(Avaliacao, Manga.id_manga == Avaliacao.id_manga)
            .group_by(Manga.id_manga, Manga.titulo_manga, Manga.autor, Manga.status)
            .having(func.count(Avaliacao.id_avaliacao) > 0)
            .order_by(desc('media_avaliacao'), desc('total_avaliacoes'))
            .limit(5)
        )
        print(str(query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})))
        
    finally:
        session.close()


def consulta_2_leitores_ativos_por_genero():
    """
    Consulta Complexa 2: Leitores Mais Ativos por Gênero
    
    Utiliza:
    - Múltiplos JOINs (5 tabelas)
    - Subconsulta com agregação
    - Filtro composto com AND
    - Eager loading (joinedload)
    - CASE para categorização
    """
    print("\n" + "="*80)
    print("CONSULTA 2: Leitores Mais Ativos (com progresso > 50% em mangás de Ação)")
    print("="*80 + "\n")
    
    session = get_session()
    
    try:
        # Subconsulta para encontrar mangás de Ação
        subquery_mangas_acao = (
            session.query(MangaGenero.id_manga)
            .join(Genero, MangaGenero.id_genero == Genero.id_genero)
            .filter(Genero.tipo_genero == 'Ação')
            .subquery()
        )
        
        # Query principal com múltiplos joins
        resultados = (
            session.query(
                Leitor.codinome,
                Usuario.nome,
                Usuario.email,
                func.count(LeitorManga.id_manga).label('mangas_lendo'),
                func.avg(LeitorManga.progresso_leitura).label('progresso_medio'),
                func.max(LeitorManga.progresso_leitura).label('maior_progresso'),
                # CASE para classificar leitor
                case(
                    (func.avg(LeitorManga.progresso_leitura) >= 80, 'Hardcore'),
                    (func.avg(LeitorManga.progresso_leitura) >= 50, 'Regular'),
                    else_='Casual'
                ).label('categoria_leitor')
            )
            .join(LeitorManga, Leitor.id_usuario == LeitorManga.id_leitor)
            .filter(
                and_(
                    LeitorManga.id_manga.in_(subquery_mangas_acao),
                    LeitorManga.progresso_leitura > 50
                )
            )
            .group_by(Leitor.id_usuario, Leitor.codinome, Usuario.nome, Usuario.email)
            .order_by(desc('progresso_medio'))
            .all()
        )
        
        print(f"{'Codinome':<20} {'Nome':<20} {'Email':<25} {'Mangás':<8} {'Progresso Médio':<18} {'Categoria':<12}")
        print("-" * 110)
        
        for codinome, nome, email, mangas, prog_medio, max_prog, categoria in resultados:
            print(f"{codinome:<20} {nome:<20} {email:<25} {mangas:>6} {prog_medio:>15.2f}% {categoria:<12}")
        
        print(f"\n✓ Total de leitores ativos encontrados: {len(resultados)}")
        
        # Mostrar SQL gerado
        print("\n--- SQL Equivalente Gerado pelo ORM ---")
        from sqlalchemy.dialects import postgresql
        query = (
            session.query(
                Leitor.codinome,
                func.count(LeitorManga.id_manga).label('mangas_lendo'),
                func.avg(LeitorManga.progresso_leitura).label('progresso_medio')
            )
            .join(LeitorManga, Leitor.id_usuario == LeitorManga.id_leitor)
            .filter(
                and_(
                    LeitorManga.id_manga.in_(subquery_mangas_acao),
                    LeitorManga.progresso_leitura > 50
                )
            )
            .group_by(Leitor.id_usuario, Leitor.codinome)
        )
        print(str(query.statement.compile(dialect=postgresql.dialect(), compile_kwargs={"literal_binds": True})))
        
    finally:
        session.close()

def comparacao_orm_vs_sql_direto():
    """
    Demonstração: Comparação entre ORM e SQL Direto
    """
    print("\n" + "="*80)
    print("COMPARAÇÃO: ORM vs SQL Direto")
    print("="*80 + "\n")
    
    session = get_session()
    
    try:
        # 1. Usando ORM
        print("--- Usando SQLAlchemy ORM ---")
        import time
        
        start = time.time()
        orm_result = (
            session.query(Manga.titulo_manga, func.count(Capitulo.id_capitulo))
            .join(Capitulo)
            .group_by(Manga.id_manga, Manga.titulo_manga)
            .all()
        )
        orm_time = time.time() - start
        
        print(f"Resultado ORM: {len(orm_result)} mangás")
        print(f"Tempo: {orm_time*1000:.2f}ms")
        
        # 2. Usando SQL Direto
        print("\n--- Usando SQL Direto ---")
        sql = text("""
            SELECT m.titulo_manga, COUNT(c.id_capitulo)
            FROM mangas m
            JOIN capitulos c ON m.id_manga = c.id_manga
            GROUP BY m.id_manga, m.titulo_manga
        """)
        
        start = time.time()
        sql_result = session.execute(sql).fetchall()
        sql_time = time.time() - start
        
        print(f"Resultado SQL: {len(sql_result)} mangás")
        print(f"Tempo: {sql_time*1000:.2f}ms")
        
        # Comparação
        print("\n--- Análise ---")
        print(f"Diferença de performance: {abs(orm_time - sql_time)*1000:.2f}ms")
        print(f"ORM é: {'mais rápido' if orm_time < sql_time else 'mais lento'}")
        print("\nVantagens ORM:")
        print("  + Type safety (erros em tempo de compilação)")
        print("  + Código mais legível e manutenível")
        print("  + Abstração do dialeto SQL")
        print("  + Facilita refatoração")
        print("\nVantagens SQL Direto:")
        print("  + Queries muito complexas podem ser mais eficientes")
        print("  + Controle total sobre a query")
        print("  + Útil para operações em lote")
        
    finally:
        session.close()


if __name__ == "__main__":
    print("\nDEMONSTRACAO DE CONSULTAS COMPLEXAS - Sistema de Mangas")
    print("=" * 80)
    
    try:
        consulta_1_top_mangas_avaliados()
        consulta_2_leitores_ativos_por_genero()
        comparacao_orm_vs_sql_direto()
        
        print("\n" + "="*80)
        print("TODAS AS CONSULTAS EXECUTADAS COM SUCESSO")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\nErro ao executar consultas: {e}")
        import traceback
        traceback.print_exc()
