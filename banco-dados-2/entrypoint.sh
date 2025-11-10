#!/bin/bash
set -e

echo "🔧 Aguardando PostgreSQL..."
while ! pg_isready -h db -U manga_user > /dev/null 2>&1; do
    sleep 1
done

echo "✓ PostgreSQL está pronto!"
echo ""

echo "📦 Aplicando migrations..."
uv run alembic upgrade head
echo "✓ Migrations aplicadas!"
echo ""

echo "🌱 Populando banco de dados..."
uv run python alembic/seed_data.py
echo ""

echo "🚀 Executando aplicação..."
uv run python main.py
