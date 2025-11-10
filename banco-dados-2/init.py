#!/usr/bin/env python3
"""
Script de inicialização do sistema
Executa migrations, seed e aplicação principal
"""
import subprocess
import sys
import time
import os


def wait_for_postgres():
    """Aguarda PostgreSQL estar pronto"""
    print("🔧 Aguardando PostgreSQL...")
    
    max_attempts = 30
    attempt = 0
    
    # Importar aqui para não falhar se não estiver instalado
    try:
        import psycopg2
    except ImportError:
        print("⚠️  psycopg2 não instalado, pulando verificação")
        time.sleep(5)  # Espera fixa
        return True
    
    while attempt < max_attempts:
        try:
            conn = psycopg2.connect(
                host="db",
                database="manga_db",
                user="manga_user",
                password="manga_pass",
                connect_timeout=2
            )
            conn.close()
            print("✓ PostgreSQL está pronto!\n")
            return True
        except Exception:
            attempt += 1
            time.sleep(1)
    
    print("✗ Timeout aguardando PostgreSQL")
    return False


def run_migrations():
    """Executa migrations do Alembic"""
    print("📦 Aplicando migrations...")
    
    result = subprocess.run(
        ["uv", "run", "alembic", "upgrade", "head"],
        capture_output=False
    )
    
    if result.returncode == 0:
        print("✓ Migrations aplicadas!\n")
        return True
    else:
        print("✗ Erro ao aplicar migrations")
        return False


def run_seed():
    """Executa seed do banco de dados"""
    print("🌱 Populando banco de dados...")
    
    result = subprocess.run(
        ["uv", "run", "seed"],
        capture_output=False
    )
    
    if result.returncode == 0:
        print("✓ Seed concluído!\n")
        return True
    else:
        print("⚠️  Aviso: Seed pode ter falhado (dados já existem?)\n")
        return True  # Não falha se dados já existem


def run_app():
    """Executa aplicação principal"""
    print("🚀 Executando aplicação...")
    
    result = subprocess.run(
        ["uv", "run", "dev"]
    )
    
    return result.returncode


def main():
    """Função principal"""
    print("="*80)
    print("  INICIALIZANDO SISTEMA DE GERENCIAMENTO DE MANGÁS")
    print("="*80)
    print()
    
    # Aguardar PostgreSQL
    if not wait_for_postgres():
        sys.exit(1)
    
    # Aplicar migrations
    if not run_migrations():
        sys.exit(1)
    
    # Popular banco (seed)
    run_seed()
    
    # Executar aplicação
    sys.exit(run_app())


if __name__ == "__main__":
    main()
