#!/bin/bash

# Automatic database restore during container initialization
# This script runs during MariaDB container startup and restores data if backups exist

set -e

BACKUP_FILE="/app/database-backups/mariadb_backup.sql"

echo "🔍 Checking for database backup to restore..."

if [[ -f "$BACKUP_FILE" ]]; then
    echo "📥 Found backup file, restoring data during initialization..."
    echo "⏳ Waiting for MariaDB to be ready..."
    
    # Wait for MariaDB to be ready
    until mysqladmin ping -h localhost -u root -p"${MYSQL_ROOT_PASSWORD}" --silent; do
        echo "Waiting for MariaDB..."
        sleep 2
    done
    
    echo "📂 Restoring database from backup..."
    mysql -u root -p"${MYSQL_ROOT_PASSWORD}" < "$BACKUP_FILE"
    
    echo "✅ Database restored successfully during initialization!"
else
    echo "ℹ️ No backup file found at $BACKUP_FILE, skipping restore"
fi 