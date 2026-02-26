# Database Backup and Restore System

This directory contains database backups for the RegulAite application that can be committed to git and restored during Docker startup.

## Overview

Instead of committing raw database files (which are large, binary, and contain sensitive data), this system uses:
- **MariaDB**: SQL dumps that can be easily versioned and reviewed
- **Qdrant**: Compressed archives of vector database collections

## Files

- `mariadb_backup.sql` - Complete MariaDB database dump
- `qdrant_backup.tar.gz` - Compressed Qdrant collections and metadata
- `backup_info.json` - Metadata about when and how the backup was created

## Usage

### Creating Backups

To create backups of your current database state:

```bash
# Make sure your containers are running
docker-compose up -d mariadb qdrant

# Create backups
./scripts/backup-databases.sh

# Commit the backups to git
git add database-backups/
git commit -m "Add database backups - $(date)"
```

### Restoring Backups

#### Option 1: Manual Restore
```bash
# Make sure containers are running
docker-compose up -d

# Restore from backups
./scripts/restore-databases.sh
```

#### Option 2: Automatic Restore During Startup
The system will automatically restore MariaDB data during container initialization if backup files exist.

For Qdrant, you need to manually restore:
```bash
# Stop services
docker-compose down

# Remove existing Qdrant data
sudo rm -rf backend/database/qdrant/*

# Extract backup
tar -xzf database-backups/qdrant_backup.tar.gz -C backend/database/qdrant/

# Fix permissions
sudo chown -R $(id -u):$(id -g) backend/database/qdrant/

# Start services
docker-compose up -d
```

## Fresh Environment Setup

When cloning the repository on a new machine:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd regulaite
   ```

2. **Create database directories**
   ```bash
   mkdir -p backend/database/mariadb
   mkdir -p backend/database/qdrant
   ```

3. **Start services** (will auto-restore MariaDB if backups exist)
   ```bash
   docker-compose up -d
   ```

4. **Restore Qdrant manually** (if backups exist)
   ```bash
   ./scripts/restore-databases.sh
   ```

## Best Practices

1. **Regular Backups**: Create backups before major changes
2. **Backup Naming**: Consider timestamped backups for multiple versions
3. **Security**: Review SQL dumps before committing to ensure no sensitive data
4. **Size Monitoring**: Monitor backup file sizes, consider compression for large datasets

## Security Considerations

- SQL dumps may contain sensitive data - review before committing
- Consider using `.env` files for database credentials
- Qdrant backups include all vector embeddings - ensure compliance with data policies

## Troubleshooting

### MariaDB Restore Issues
- Ensure container has sufficient memory
- Check for character encoding issues
- Verify database credentials

### Qdrant Restore Issues
- Ensure proper file permissions on extracted files
- Check available disk space
- Verify Qdrant version compatibility

### Permission Issues
```bash
# Fix common permission issues
sudo chown -R $(id -u):$(id -g) backend/database/
sudo chmod -R 755 backend/database/
```

## Alternative Approaches

If this backup approach doesn't meet your needs, consider:

1. **Database Seeding Scripts**: Create initialization scripts instead of dumps
2. **Docker Volumes**: Use named Docker volumes with backup strategies
3. **External Storage**: Use cloud storage for backup files
4. **Database Migrations**: Use migration scripts for schema and data changes 