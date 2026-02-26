#!/bin/bash

# Database backup script for RegulAite
# This script creates backups that can be committed to git and restored during startup

set -e

# Configuration
BACKUP_DIR="./database-backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
COMPOSE_FILE="docker-compose.yml"

# Default values (matching docker-compose.yml defaults)
MARIADB_ROOT_PASSWORD="${MARIADB_ROOT_PASSWORD:-StrongR00tP@ssW0rd!}"
MARIADB_DATABASE="${MARIADB_DATABASE:-regulaite}"
MARIADB_USER="${MARIADB_USER:-regulaite_user}"
MARIADB_PASSWORD="${MARIADB_PASSWORD:-SecureP@ssw0rd!}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "🔄 Starting database backup process..."

# Check if containers are running
if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "regulaite-mariadb.*Up"; then
    echo "❌ MariaDB container is not running. Please start it first with: docker-compose up mariadb"
    exit 1
fi

if ! docker-compose -f "$COMPOSE_FILE" ps | grep -q "regulaite-qdrant.*Up"; then
    echo "❌ Qdrant container is not running. Please start it first with: docker-compose up qdrant"
    exit 1
fi

# Backup MariaDB
echo "📦 Backing up MariaDB database..."
docker-compose -f "$COMPOSE_FILE" exec -T mariadb \
    mariadb-dump \
    --single-transaction \
    --routines \
    --triggers \
    --all-databases \
    -u root \
    -p"${MARIADB_ROOT_PASSWORD}" \
    > "$BACKUP_DIR/mariadb_backup.sql"

if [[ $? -eq 0 && -s "$BACKUP_DIR/mariadb_backup.sql" ]]; then
    echo "✅ MariaDB backup completed: $BACKUP_DIR/mariadb_backup.sql"
else
    echo "❌ MariaDB backup failed or is empty"
    exit 1
fi

# Backup Qdrant
echo "📦 Backing up Qdrant collections..."

# Copy Qdrant data (this includes collections metadata and configuration)
echo "📂 Creating Qdrant backup archive..."
if [[ -d "./backend/database/qdrant" ]]; then
    tar -czf "$BACKUP_DIR/qdrant_backup.tar.gz" -C ./backend/database/qdrant . 2>/dev/null || echo "⚠️  Warning: Qdrant backup may be incomplete"
    if [[ -f "$BACKUP_DIR/qdrant_backup.tar.gz" ]]; then
        echo "✅ Qdrant backup completed: $BACKUP_DIR/qdrant_backup.tar.gz"
    else
        echo "⚠️  Warning: Could not create Qdrant backup archive"
    fi
else
    echo "⚠️  Warning: Qdrant data directory not found"
fi

# Create a metadata file with backup information
cat > "$BACKUP_DIR/backup_info.json" << EOF
{
    "backup_date": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "mariadb_backup": "mariadb_backup.sql",
    "qdrant_backup": "qdrant_backup.tar.gz",
    "created_by": "$(whoami)",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'N/A')",
    "backup_size_mb": {
        "mariadb": "$(du -m "$BACKUP_DIR/mariadb_backup.sql" 2>/dev/null | cut -f1 || echo 'N/A')",
        "qdrant": "$(du -m "$BACKUP_DIR/qdrant_backup.tar.gz" 2>/dev/null | cut -f1 || echo 'N/A')"
    }
}
EOF

echo "📝 Backup metadata created: $BACKUP_DIR/backup_info.json"
echo "🎉 Database backup completed successfully!"
echo ""
echo "📊 Backup Summary:"
if [[ -f "$BACKUP_DIR/mariadb_backup.sql" ]]; then
    echo "   MariaDB: $(du -h "$BACKUP_DIR/mariadb_backup.sql" | cut -f1)"
fi
if [[ -f "$BACKUP_DIR/qdrant_backup.tar.gz" ]]; then
    echo "   Qdrant: $(du -h "$BACKUP_DIR/qdrant_backup.tar.gz" | cut -f1)"
fi
echo ""
echo "💡 To commit these backups to git:"
echo "   git add $BACKUP_DIR/"
echo "   git commit -m 'Add database backups - $(date +"%Y-%m-%d")'" 