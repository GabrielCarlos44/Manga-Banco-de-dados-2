"""
Script de inicialização do Alembic
"""
import subprocess
import sys

def init_alembic():
    """Inicializa o Alembic se ainda não estiver configurado"""
    try:
        # Verificar se já existe configuração
        import os
        if not os.path.exists('alembic'):
            print("Inicializando Alembic...")
            subprocess.run([sys.executable, "-m", "alembic", "init", "alembic"], check=True)
            print("Alembic inicializado!")
        else:
            print("Alembic já está configurado.")
    except Exception as e:
        print(f"Erro ao inicializar Alembic: {e}")

if __name__ == "__main__":
    init_alembic()
