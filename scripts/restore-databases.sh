#!/bin/bash

# Database restore script for RegulAite
# This script restores databases from backups created by backup-databases.sh

set -e

# Configuration
BACKUP_DIR="./database-backups"
COMPOSE_FILE="docker-compose.yml"

# Default values (matching docker-compose.yml defaults)
MARIADB_ROOT_PASSWORD="${MARIADB_ROOT_PASSWORD:-StrongR00tP@ssW0rd!}"
MARIADB_DATABASE="${MARIADB_DATABASE:-regulaite}"
MARIADB_USER="${MARIADB_USER:-regulaite_user}"
MARIADB_PASSWORD="${MARIADB_PASSWORD:-SecureP@ssw0rd!}"

echo "🔄 Starting database restore process..."

# Check if backup files exist
if [[ ! -f "$BACKUP_DIR/mariadb_backup.sql" ]]; then
    echo "❌ MariaDB backup file not found: $BACKUP_DIR/mariadb_backup.sql"
    exit 1
fi

if [[ ! -f "$BACKUP_DIR/qdrant_backup.tar.gz" ]]; then
    echo "❌ Qdrant backup file not found: $BACKUP_DIR/qdrant_backup.tar.gz"
    exit 1
fi

# Check if containers are running
if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "regulaite-mariadb.*Up"; then
    echo "❌ MariaDB container is not running. Please start it first with: docker-compose up mariadb"
    exit 1
fi

if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "regulaite-qdrant.*Up"; then
    echo "❌ Qdrant container is not running. Please start it first with: docker-compose up qdrant"
    exit 1
fi

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 10

# Restore MariaDB
echo "📥 Restoring MariaDB database..."
docker-compose -f "$COMPOSE_FILE" exec -T mariadb mysql \
    -u root -p"${MARIADB_ROOT_PASSWORD}" \
    < "$BACKUP_DIR/mariadb_backup.sql"

echo "✅ MariaDB restore completed"

# Restore Qdrant
echo "📥 Restoring Qdrant collections..."

# Stop Qdrant to restore data files
echo "🛑 Stopping Qdrant container for data restoration..."
docker-compose -f "$COMPOSE_FILE" stop qdrant

# Clear existing Qdrant data and restore from backup
echo "🗑️ Clearing existing Qdrant data..."
sudo rm -rf ./backend/database/qdrant/*

echo "📂 Restoring Qdrant data from backup..."
tar -xzf "$BACKUP_DIR/qdrant_backup.tar.gz" -C ./backend/database/qdrant/

# Fix permissions
sudo chown -R $(id -u):$(id -g) ./backend/database/qdrant/

# Start Qdrant again
echo "🚀 Starting Qdrant container..."
docker-compose -f "$COMPOSE_FILE" start qdrant

# Wait for Qdrant to be ready
echo "⏳ Waiting for Qdrant to be ready..."
sleep 15

echo "✅ Qdrant restore completed"

# Display backup info if available
if [[ -f "$BACKUP_DIR/backup_info.json" ]]; then
    echo ""
    echo "📋 Backup Information:"
    cat "$BACKUP_DIR/backup_info.json" | jq . 2>/dev/null || cat "$BACKUP_DIR/backup_info.json"
fi

echo ""
echo "🎉 Database restore completed successfully!" 