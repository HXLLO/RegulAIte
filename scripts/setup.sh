#!/bin/bash
# Updated setup.sh for RegulAite Plugin with Docker image building
# This script configures the plugin and builds required Docker images

set -e  # Exit on error

# ANSI color codes for prettier output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PLUGIN_DIR="$( cd "$SCRIPT_DIR/.." &> /dev/null && pwd )"
DOCKER_COMPOSE_FILE="$PLUGIN_DIR/docker-compose.yml"
ENV_FILE="$PLUGIN_DIR/.env"
BACKEND_IMAGE="ai_backend:latest"
FRONTEND_IMAGE="regulaite_frontend:latest"
FRONTEND_DIR="$PLUGIN_DIR/front-end"
BUILD_TARGET="development" # Default to development mode

# Backup system configuration
BACKUP_DIR="$PLUGIN_DIR/database-backups"
BACKUP_SCRIPTS_DIR="$PLUGIN_DIR/scripts"

# Service configuration
MAX_WAIT=60  # Maximum time to wait for services to start (seconds)

# Print banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║                                                                      ║"
echo "║                        RegulAIte Plugin Setup                        ║"
echo "║                                                                      ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Step 1: Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"
for cmd in docker grep sed; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}Error: $cmd is not installed or not in PATH${NC}"
        exit 1
    fi
done

if ! docker info &> /dev/null; then
    echo -e "${RED}Error: Docker daemon is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All dependencies are installed and Docker is running${NC}"

# Step 2: Create a dedicated network (for containers to talk to each other)
NETWORK_NAME="regulaite_network"

# Create a new network if it doesn't exist
echo -e "${YELLOW}Setting up Docker network: ${NETWORK_NAME}${NC}"
if ! docker network ls | grep -q "$NETWORK_NAME"; then
    docker network create "$NETWORK_NAME"
    echo -e "${GREEN}✅ Network '$NETWORK_NAME' created${NC}"
else
    echo -e "${GREEN}✅ Network '$NETWORK_NAME' already exists${NC}"
fi

# Step 4: Update .env file - Using localhost configuration
echo -e "${YELLOW}Configuring environment variables...${NC}"

# Set Kibana host to localhost for simplicity
KIBANA_HOST="localhost"

# Step 4: Stop any running containers and start fresh
echo -e "${YELLOW}Stopping any running containers...${NC}"
docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
echo -e "${GREEN}✅ Containers stopped${NC}"

# Create or update .env file
if [ -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}Found existing .env file. Updating...${NC}"
else
    echo -e "${YELLOW}Creating new .env file...${NC}"
fi

# Prompt for OpenAI API key if not in .env
OPENAI_API_KEY=""
if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    OPENAI_API_KEY="${OPENAI_API_KEY:-}"
fi

if [ -z "$OPENAI_API_KEY" ]; then
    echo -n "Enter your OpenAI API key (required for AI services): "
    read -r OPENAI_API_KEY

    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}No API key provided. Using placeholder - some features may not work correctly.${NC}"
        OPENAI_API_KEY="your-openai-api-key"
    fi
fi

# Prompt for MariaDB root password
MARIADB_ROOT_PASSWORD="${MARIADB_ROOT_PASSWORD:-}"
if [ -z "$MARIADB_ROOT_PASSWORD" ]; then
    echo -n "Enter a root password for MariaDB (leave blank for default 'StrongR00tP@ssW0rd!'): "
    read -r MARIADB_ROOT_PASSWORD

    if [ -z "$MARIADB_ROOT_PASSWORD" ]; then
        echo -e "${YELLOW}Using default root password for MariaDB${NC}"
        MARIADB_ROOT_PASSWORD="StrongR00tP@ssW0rd!"
    fi
fi

# Prompt for MariaDB user credentials
MARIADB_DATABASE="${MARIADB_DATABASE:-regulaite}"
MARIADB_USER="${MARIADB_USER:-regulaite_user}"
MARIADB_PASSWORD="${MARIADB_PASSWORD:-}"

# Prompt MariaDB user name if not in .env
if [ -z "$MARIADB_USER" ]; then
    echo -n "Enter a username for MariaDB (leave blank for default 'regulaite_user'): "
    read -r MARIADB_USER

    if [ -z "$MARIADB_USER" ]; then
        echo -e "${YELLOW}Using default username 'regulaite_user'${NC}"
        MARIADB_USER="regulaite_user"
    fi
fi

# Prompt for MariaDB password if not in .env
if [ -z "$MARIADB_PASSWORD" ]; then
    echo -n "Enter a password for MariaDB user '$MARIADB_USER' (leave blank for default 'SecureP@ssw0rd!'): "
    read -r MARIADB_PASSWORD

    if [ -z "$MARIADB_PASSWORD" ]; then
        echo -e "${YELLOW}Using default password for MariaDB user${NC}"
        MARIADB_PASSWORD="SecureP@ssw0rd!"
    fi
fi

# Prompt for MariaDB database name if not in .env
if [ -z "$MARIADB_DATABASE" ]; then
    echo -n "Enter a name for MariaDB database (leave blank for default 'regulaite'): "
    read -r MARIADB_DATABASE

    if [ -z "$MARIADB_DATABASE" ]; then
        echo -e "${YELLOW}Using default database name 'regulaite'${NC}"
        MARIADB_DATABASE="regulaite"
    fi
fi

# Document Parser API Keys
echo -e "${YELLOW}Document Parser Configuration${NC}"

# Unstructured Cloud API Key
UNSTRUCTURED_CLOUD_API_KEY=""
if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    UNSTRUCTURED_CLOUD_API_KEY="${UNSTRUCTURED_CLOUD_API_KEY:-}"
fi

echo -n "Enter Unstructured Cloud API Key (optional): "
read -r UNSTRUCTURED_CLOUD_API_KEY_INPUT
if [ -n "$UNSTRUCTURED_CLOUD_API_KEY_INPUT" ]; then
    UNSTRUCTURED_CLOUD_API_KEY="$UNSTRUCTURED_CLOUD_API_KEY_INPUT"
fi

# LlamaParse API Key
LLAMAPARSE_API_KEY=""
if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    LLAMAPARSE_API_KEY="${LLAMAPARSE_API_KEY:-}"
fi

echo -n "Enter LlamaParse API Key (optional): "
read -r LLAMAPARSE_API_KEY_INPUT
if [ -n "$LLAMAPARSE_API_KEY_INPUT" ]; then
    LLAMAPARSE_API_KEY="$LLAMAPARSE_API_KEY_INPUT"
fi

# Doctly API Key
DOCTLY_API_KEY=""
if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    DOCTLY_API_KEY="${DOCTLY_API_KEY:-}"
fi

echo -n "Enter Doctly API Key (optional): "
read -r DOCTLY_API_KEY_INPUT
if [ -n "$DOCTLY_API_KEY_INPUT" ]; then
    DOCTLY_API_KEY="$DOCTLY_API_KEY_INPUT"
fi

# Default Parser Selection
DEFAULT_PARSER_TYPE="unstructured"
if [ -f "$ENV_FILE" ]; then
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    DEFAULT_PARSER_TYPE="${DEFAULT_PARSER_TYPE:-unstructured}"
fi

echo -e "${YELLOW}Select default document parser:${NC}"
echo "1) Unstructured (Local) - default"
echo "2) Unstructured Cloud"
echo "3) LlamaParse"
echo "4) Doctly"
read -rp "Enter your choice [1]: " parser_choice
parser_choice=${parser_choice:-1}

case $parser_choice in
    2)
        DEFAULT_PARSER_TYPE="unstructured_cloud"
        echo -e "${YELLOW}Setting default parser to: Unstructured Cloud${NC}"
        if [ -z "$UNSTRUCTURED_CLOUD_API_KEY" ]; then
            echo -e "${RED}Warning: No API key provided for Unstructured Cloud. This parser may not work.${NC}"
        fi
        ;;
    3)
        DEFAULT_PARSER_TYPE="llamaparse"
        echo -e "${YELLOW}Setting default parser to: LlamaParse${NC}"
        if [ -z "$LLAMAPARSE_API_KEY" ]; then
            echo -e "${RED}Warning: No API key provided for LlamaParse. This parser may not work.${NC}"
        fi
        ;;
    4)
        DEFAULT_PARSER_TYPE="doctly"
        echo -e "${YELLOW}Setting default parser to: Doctly${NC}"
        if [ -z "$DOCTLY_API_KEY" ]; then
            echo -e "${RED}Warning: No API key provided for Doctly. This parser may not work.${NC}"
        fi
        ;;
    *)
        echo -e "${YELLOW}Setting default parser to: Unstructured (Local)${NC}"
        ;;
esac

# Ask for environment type
echo -e "${YELLOW}Select environment type:${NC}"
echo "1) Development (runs as root, hot-reloading enabled)"
echo "2) Production (runs as non-root user, security hardened)"
read -rp "Enter your choice [1]: " env_choice
env_choice=${env_choice:-1}

if [ "$env_choice" = "2" ]; then
    BUILD_TARGET="production"
    echo -e "${YELLOW}Setting up PRODUCTION environment${NC}"
else
    echo -e "${YELLOW}Setting up DEVELOPMENT environment${NC}"
fi

# Create or update .env file with localhost configuration
cat > "$ENV_FILE" << EOL

#Build target
BUILD_TARGET=$BUILD_TARGET

# API Keys
OPENAI_API_KEY=$OPENAI_API_KEY

# MariaDB Configuration
MARIADB_ROOT_PASSWORD=$MARIADB_ROOT_PASSWORD
MARIADB_DATABASE=$MARIADB_DATABASE
MARIADB_USER=$MARIADB_USER
MARIADB_PASSWORD=$MARIADB_PASSWORD

# Qdrant Configuration
QDRANT_URL=http://qdrant:6333
QDRANT_GRPC_URL=http://qdrant:6334

# Unstructured Configuration
UNSTRUCTURED_API_URL=http://unstructured:8000/general/v0/general
UNSTRUCTURED_CLOUD_API_URL=https://api.unstructured.io/general/v0/general
UNSTRUCTURED_CLOUD_API_KEY=$UNSTRUCTURED_CLOUD_API_KEY
UNSTRUCTURED_EXTRA_ARGS=""

# LlamaParse Configuration
LLAMAPARSE_API_URL=https://api.llamaindex.ai/v1/parsing
LLAMAPARSE_API_KEY=$LLAMAPARSE_API_KEY

# Doctly Configuration
DOCTLY_API_URL=https://api.doctly.dev/v1/parse
DOCTLY_API_KEY=$DOCTLY_API_KEY

# Default Parser
DEFAULT_PARSER_TYPE=$DEFAULT_PARSER_TYPE

# AI_BACKEND Configuration
AI_BACKEND_BROWSER_URL=http://localhost:8090

# Processing Configuration
MAX_WORKERS=5

# Cache Directory
CACHE_DIR=/app/cache
EOL

echo -e "${GREEN}✅ Environment configuration completed${NC}"

# Step 6: Build the Pyndantic Docker image 
echo -e "${YELLOW}Building AI Backend Docker image...${NC}"

# Verfy if dockerfile exists for AI_BACKEND
AI_BACKEND_DIR="$PLUGIN_DIR/backend"
PY_DOCKERFILE="$AI_BACKEND_DIR/Dockerfile"

if [ -f "$PY_DOCKERFILE" ]; then
    echo -e "${YELLOW}✅ Found existing AI_BACKEND Dockerfile. ${NC}"
else
    echo -e "${RED}Dockerfile for AI_BACKEND doesn't exist!${NC}"
fi

# Step 6: Update docker-compose.yml to use our build target
echo -e "${YELLOW}Updating docker-compose.yml with build target...${NC}"
if grep -q "target:" "$DOCKER_COMPOSE_FILE"; then
    # Update existing target
    sed -i "s/target: .*/target: $BUILD_TARGET/" "$DOCKER_COMPOSE_FILE"
else
    # Add target if it doesn't exist
    sed -i "/context: \.\/backend/a \ \ \ \ \ \ target: $BUILD_TARGET" "$DOCKER_COMPOSE_FILE"
fi
echo -e "${GREEN}✅ Updated docker-compose.yml with build target: $BUILD_TARGET${NC}"


# Build the Docker image with specified target
echo -e "${YELLOW}Building Docker image: $BACKEND_IMAGE using target: $BUILD_TARGET${NC}"
if docker build --no-cache --target $BUILD_TARGET -t "$BACKEND_IMAGE" "$AI_BACKEND_DIR"; then
    echo -e "${GREEN}✅ Successfully built $BACKEND_IMAGE with target: $BUILD_TARGET${NC}"
else
    echo -e "${RED}Failed to build $BACKEND_IMAGE${NC}"
    echo -e "${YELLOW}Please check the Dockerfile and build log for errors.${NC}"
    exit 1
fi

# Build frontend image
echo -e "${YELLOW}Building frontend Docker image...${NC}"
if docker build --no-cache -t "$FRONTEND_IMAGE" "$FRONTEND_DIR"; then
    echo -e "${GREEN}✅ Successfully built $FRONTEND_IMAGE${NC}"
else
    echo -e "${RED}Failed to build $FRONTEND_IMAGE${NC}"
fi

# Start containers
echo -e "${YELLOW}Starting containers...${NC}"
docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --remove-orphans

# Step 7: Wait for services to start
echo -e "${YELLOW}Waiting for services to initialize...${NC}"

# Wait for MariaDB to be ready
echo -e "${YELLOW}Waiting for MariaDB to start...${NC}"
for i in $(seq 1 $MAX_WAIT); do
    if docker ps | grep -q "regulaite-mariadb" && docker exec regulaite-mariadb mariadb-admin ping -h localhost -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" --silent; then
        echo -e "${GREEN}✅ MariaDB is ready${NC}"
        break
    fi

    # Show progress
    if [ $((i % 5)) -eq 0 ]; then
        echo -ne "${YELLOW}Still waiting for MariaDB... ${i}s/$MAX_WAIT\r${NC}"
    fi

    # If we've reached max wait, show a message but continue
    if [ "$i" -eq $MAX_WAIT ]; then
        echo -e "${YELLOW}⚠️ Max wait time reached for MariaDB. Continuing anyway...${NC}"
    fi

    sleep 1
done

# Initialize MariaDB schema
echo -e "${YELLOW}Checking MariaDB schema status...${NC}"

# Check if the regulaite_settings table exists (used as a marker for schema initialization)
if ! docker exec regulaite-mariadb mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" "$MARIADB_DATABASE" -e "SHOW TABLES LIKE 'regulaite_settings';" | grep -q "regulaite_settings"; then
    echo -e "${YELLOW}Schema not initialized. Applying database schema...${NC}"

    # First check if the init.sql script worked by itself (it should run on container start)
    sleep 3  # Give a moment for any auto-initialization to complete

    # Check again if tables exist after waiting
    if ! docker exec regulaite-mariadb mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" "$MARIADB_DATABASE" -e "SHOW TABLES LIKE 'regulaite_settings';" | grep -q "regulaite_settings"; then
        echo -e "${YELLOW}Auto-initialization not detected. Running init.sql manually...${NC}"

        # Copy the init.sql file into the container
        docker cp "$PLUGIN_DIR/backend/config/mariadb/init.sql" regulaite-mariadb:/tmp/init.sql

        # Execute the SQL file using the root user instead of the application user
        if docker exec regulaite-mariadb sh -c "mariadb -u\"root\" -p\"$MARIADB_ROOT_PASSWORD\" \"$MARIADB_DATABASE\" < /tmp/init.sql"; then
            echo -e "${GREEN}✅ MariaDB schema initialized successfully from init.sql${NC}"
        else
            echo -e "${RED}Error initializing MariaDB schema from init.sql${NC}"

            # Fallback to minimal schema if the init.sql fails
            echo -e "${YELLOW}Attempting fallback schema initialization...${NC}"
            docker exec regulaite-mariadb mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" "$MARIADB_DATABASE" -e "
                -- Table for global settings
                CREATE TABLE IF NOT EXISTS regulaite_settings (
                    setting_key VARCHAR(255) PRIMARY KEY,
                    setting_value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    description TEXT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

                -- Table for chat messages history
                CREATE TABLE IF NOT EXISTS chat_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    session_id VARCHAR(255) NOT NULL,
                    message_text TEXT NOT NULL,
                    message_role ENUM('user', 'assistant', 'system') NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON,
                    INDEX idx_user_id (user_id),
                    INDEX idx_session_id (session_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

                -- Table for task chat messages
                CREATE TABLE IF NOT EXISTS task_chat_messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    message_id VARCHAR(255) NOT NULL UNIQUE,
                    task_id VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    role ENUM('user', 'assistant', 'system') NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_message_id (message_id),
                    INDEX idx_task_id (task_id),
                    INDEX idx_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

                -- Create task tracking table if needed
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id VARCHAR(255) PRIMARY KEY,
                    status ENUM('queued', 'processing', 'completed', 'failed', 'cancelled') NOT NULL,
                    task_type VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP NULL,
                    result JSON,
                    error TEXT,
                    message TEXT,
                    parameters JSON,
                    INDEX idx_status (status),
                    INDEX idx_task_type (task_type),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

                -- Create user table if needed for future authentication
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(255) PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    company VARCHAR(255),
                    username VARCHAR(255) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    settings JSON,
                    INDEX idx_username (username),
                    INDEX idx_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

                -- Insert default settings
                INSERT IGNORE INTO regulaite_settings (setting_key, setting_value, description) VALUES
                ('llm_model', 'gpt-4', 'Default LLM model'),
                ('llm_temperature', '0.7', 'Default temperature for LLM'),
                ('llm_max_tokens', '2048', 'Default max tokens for LLM'),
                ('llm_top_p', '1', 'Default top_p value for LLM'),
                ('enable_chat_history', 'true', 'Whether to save chat history');
            "

            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ MariaDB schema initialized successfully from init.sql${NC}"
            else
                echo -e "${RED}Critical error initializing MariaDB schema${NC}"
            fi
        fi
    else
        echo -e "${GREEN}✅ MariaDB schema already initialized via container startup${NC}"
    fi
else
    echo -e "${GREEN}✅ MariaDB schema already initialized${NC}"

    # Check for schema version and do migrations if needed
    echo -e "${YELLOW}Checking for schema updates...${NC}"

    # Check if users table has settings column - this is a critical column for the new user settings feature
    if ! docker exec regulaite-mariadb mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" "$MARIADB_DATABASE" -e "SHOW COLUMNS FROM users LIKE 'settings';" | grep -q "settings"; then
        echo -e "${YELLOW}Migrating users table to add settings column...${NC}"
        docker exec regulaite-mariadb mariadb -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" "$MARIADB_DATABASE" -e "
            ALTER TABLE users ADD COLUMN settings JSON;
        "
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Users table migration completed${NC}"
        else
            echo -e "${RED}Error migrating users table${NC}"
        fi
    fi
fi

# Step 8: Database Restoration from Backups
echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}🗄️  Database Restoration System${NC}"
echo -e "${BLUE}===============================================${NC}"

# Check if backup files exist
MARIADB_BACKUP="$BACKUP_DIR/mariadb_backup.sql"
QDRANT_BACKUP="$BACKUP_DIR/qdrant_backup.tar.gz"
BACKUP_INFO="$BACKUP_DIR/backup_info.json"

echo -e "${YELLOW}Checking for existing database backups...${NC}"

HAS_MARIADB_BACKUP=false
HAS_QDRANT_BACKUP=false
HAS_BACKUP_INFO=false

if [ -f "$MARIADB_BACKUP" ]; then
    MARIADB_SIZE=$(du -h "$MARIADB_BACKUP" | cut -f1)
    echo -e "${GREEN}✅ Found MariaDB backup: $MARIADB_SIZE${NC}"
    HAS_MARIADB_BACKUP=true
fi

if [ -f "$QDRANT_BACKUP" ]; then
    QDRANT_SIZE=$(du -h "$QDRANT_BACKUP" | cut -f1)
    echo -e "${GREEN}✅ Found Qdrant backup: $QDRANT_SIZE${NC}"
    HAS_QDRANT_BACKUP=true
fi

if [ -f "$BACKUP_INFO" ]; then
    echo -e "${GREEN}✅ Found backup metadata${NC}"
    HAS_BACKUP_INFO=true
    
    # Display backup information if available
    if command -v jq &> /dev/null; then
        echo -e "${YELLOW}Backup Information:${NC}"
        jq -r '. | "  📅 Created: \(.backup_date)\n  👤 By: \(.created_by)\n  🔗 Git: \(.git_commit[0:8])"' "$BACKUP_INFO" 2>/dev/null || cat "$BACKUP_INFO"
    else
        echo -e "${YELLOW}Backup metadata:${NC}"
        cat "$BACKUP_INFO"
    fi
fi

# Determine restoration strategy
if [ "$HAS_MARIADB_BACKUP" = true ] || [ "$HAS_QDRANT_BACKUP" = true ]; then
    echo ""
    echo -e "${YELLOW}Database backups detected! Choose restoration option:${NC}"
    echo "1) Restore all available backups automatically"
    echo "2) Restore only MariaDB data"
    echo "3) Restore only Qdrant data"
    echo "4) Skip restoration (keep fresh databases)"
    echo "5) View backup details before deciding"
    
    read -rp "Enter your choice [1]: " restore_choice
    restore_choice=${restore_choice:-1}
    
    case $restore_choice in
        1)
            echo -e "${YELLOW}🔄 Starting automatic restoration of all available backups...${NC}"
            RESTORE_MARIADB=$HAS_MARIADB_BACKUP
            RESTORE_QDRANT=$HAS_QDRANT_BACKUP
            ;;
        2)
            echo -e "${YELLOW}🔄 Will restore only MariaDB data...${NC}"
            RESTORE_MARIADB=$HAS_MARIADB_BACKUP
            RESTORE_QDRANT=false
            ;;
        3)
            echo -e "${YELLOW}🔄 Will restore only Qdrant data...${NC}"
            RESTORE_MARIADB=false
            RESTORE_QDRANT=$HAS_QDRANT_BACKUP
            ;;
        4)
            echo -e "${YELLOW}⏭️ Skipping database restoration...${NC}"
            RESTORE_MARIADB=false
            RESTORE_QDRANT=false
            ;;
        5)
            if [ "$HAS_BACKUP_INFO" = true ]; then
                echo -e "${BLUE}📋 Detailed Backup Information:${NC}"
                cat "$BACKUP_INFO"
            else
                echo -e "${YELLOW}No detailed backup information available${NC}"
            fi
            echo ""
            echo -e "${YELLOW}Files found:${NC}"
            [ "$HAS_MARIADB_BACKUP" = true ] && echo -e "  📊 MariaDB: $MARIADB_SIZE"
            [ "$HAS_QDRANT_BACKUP" = true ] && echo -e "  🔍 Qdrant: $QDRANT_SIZE"
            echo ""
            echo -e "${YELLOW}Do you want to restore these backups? (y/N):${NC}"
            read -r confirm_restore
            if [[ "$confirm_restore" =~ ^[Yy]$ ]]; then
                RESTORE_MARIADB=$HAS_MARIADB_BACKUP
                RESTORE_QDRANT=$HAS_QDRANT_BACKUP
            else
                RESTORE_MARIADB=false
                RESTORE_QDRANT=false
            fi
            ;;
        *)
            echo -e "${YELLOW}Invalid choice. Skipping restoration...${NC}"
            RESTORE_MARIADB=false
            RESTORE_QDRANT=false
            ;;
    esac
    
    # Perform MariaDB restoration
    if [ "$RESTORE_MARIADB" = true ] && [ -f "$MARIADB_BACKUP" ]; then
        echo -e "${YELLOW}📥 Restoring MariaDB database from backup...${NC}"
        
        # Wait a moment to ensure MariaDB is fully ready
        echo -e "${YELLOW}⏳ Ensuring MariaDB is ready for restoration...${NC}"
        sleep 5
        
        # Restore MariaDB backup
        if docker exec -i regulaite-mariadb mariadb -u root -p"$MARIADB_ROOT_PASSWORD" < "$MARIADB_BACKUP"; then
            echo -e "${GREEN}✅ MariaDB data restored successfully from backup${NC}"
        else
            echo -e "${RED}❌ Failed to restore MariaDB data. Check backup file integrity.${NC}"
            echo -e "${YELLOW}ℹ️ The system will continue with fresh database schema.${NC}"
        fi
    fi
    
    # Perform Qdrant restoration
    if [ "$RESTORE_QDRANT" = true ] && [ -f "$QDRANT_BACKUP" ]; then
        echo -e "${YELLOW}📥 Restoring Qdrant collections from backup...${NC}"
        
        # Check if Qdrant container is running
        if docker ps | grep -q "regulaite-qdrant"; then
            # Stop Qdrant to safely restore data
            echo -e "${YELLOW}🛑 Stopping Qdrant container for data restoration...${NC}"
            docker-compose -f "$DOCKER_COMPOSE_FILE" stop qdrant
            
            # Clear existing Qdrant data
            QDRANT_DATA_DIR="$PLUGIN_DIR/backend/database/qdrant"
            if [ -d "$QDRANT_DATA_DIR" ]; then
                echo -e "${YELLOW}🗑️ Clearing existing Qdrant data...${NC}"
                sudo rm -rf "$QDRANT_DATA_DIR"/*
            fi
            
            # Create directory if it doesn't exist
            mkdir -p "$QDRANT_DATA_DIR"
            
            # Extract backup
            echo -e "${YELLOW}📂 Extracting Qdrant backup...${NC}"
            if tar -xzf "$QDRANT_BACKUP" -C "$QDRANT_DATA_DIR"; then
                # Fix permissions
                echo -e "${YELLOW}🔧 Fixing permissions...${NC}"
                sudo chown -R $(id -u):$(id -g) "$QDRANT_DATA_DIR"
                
                # Restart Qdrant
                echo -e "${YELLOW}🚀 Starting Qdrant container...${NC}"
                docker-compose -f "$DOCKER_COMPOSE_FILE" start qdrant
                
                # Wait for Qdrant to be ready
                echo -e "${YELLOW}⏳ Waiting for Qdrant to initialize...${NC}"
                sleep 15
                
                # Verify Qdrant is working
                if curl -s "http://localhost:6333/healthz" > /dev/null 2>&1; then
                    echo -e "${GREEN}✅ Qdrant data restored successfully from backup${NC}"
                else
                    echo -e "${YELLOW}⚠️ Qdrant restored but may need more time to initialize${NC}"
                fi
            else
                echo -e "${RED}❌ Failed to extract Qdrant backup${NC}"
                echo -e "${YELLOW}🚀 Starting Qdrant with fresh data...${NC}"
                docker-compose -f "$DOCKER_COMPOSE_FILE" start qdrant
            fi
        else
            echo -e "${YELLOW}⚠️ Qdrant container not found. Skipping Qdrant restoration.${NC}"
        fi
    fi
    
    # Wait for all services to be ready after restoration
    if [ "$RESTORE_MARIADB" = true ] || [ "$RESTORE_QDRANT" = true ]; then
        echo -e "${YELLOW}⏳ Waiting for all services to stabilize after restoration...${NC}"
        sleep 10
        
        # Final health checks
        echo -e "${YELLOW}🔍 Performing post-restoration health checks...${NC}"
        
        # Check MariaDB
        if docker exec regulaite-mariadb mariadb-admin ping -h localhost -u"$MARIADB_USER" -p"$MARIADB_PASSWORD" --silent; then
            echo -e "${GREEN}✅ MariaDB is healthy after restoration${NC}"
        else
            echo -e "${YELLOW}⚠️ MariaDB health check failed - may need more time${NC}"
        fi
        
        # Check Qdrant
        if curl -s "http://localhost:6333/healthz" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Qdrant is healthy after restoration${NC}"
        else
            echo -e "${YELLOW}⚠️ Qdrant health check failed - may need more time${NC}"
        fi
    fi
    
else
    echo -e "${YELLOW}ℹ️ No database backups found. Starting with fresh databases.${NC}"
    echo -e "${BLUE}💡 You can create backups later using: ./scripts/backup-databases.sh${NC}"
fi

echo -e "${BLUE}===============================================${NC}"

# Create database directories for future use
echo -e "${YELLOW}📁 Ensuring database directories exist...${NC}"
mkdir -p "$PLUGIN_DIR/backend/database/mariadb"
mkdir -p "$PLUGIN_DIR/backend/database/qdrant"
echo -e "${GREEN}✅ Database directories created${NC}"

# Step 9: Vector Indexing Verification
echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}🔍 Vector Indexing Verification${NC}"
echo -e "${BLUE}===============================================${NC}"

echo -e "${YELLOW}Verifying Qdrant vector indexing configuration...${NC}"

# Wait for Qdrant to be fully ready
echo -e "${YELLOW}⏳ Waiting for Qdrant to be fully initialized...${NC}"
for i in {1..30}; do
    if curl -s "http://localhost:6333/healthz" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Qdrant is ready${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠️ Qdrant may still be starting up${NC}"
    fi
    sleep 2
done

# Run indexing verification if script exists
if [ -f "$PLUGIN_DIR/scripts/verify-indexing.sh" ]; then
    echo -e "${YELLOW}Running indexing verification...${NC}"
    bash "$PLUGIN_DIR/scripts/verify-indexing.sh" || echo -e "${YELLOW}⚠️ Indexing verification completed with warnings${NC}"
else
    echo -e "${YELLOW}⚠️ Indexing verification script not found${NC}"
fi

# Step 10: Final status and information
echo -e "${GREEN}===============================================${NC}"
echo -e "${BLUE}🎉 RegulAite setup completed!${NC}"
echo -e "${GREEN}===============================================${NC}"
echo ""
echo -e "${BLUE}Environment: ${BUILD_TARGET^^}${NC}"
echo ""
echo -e "${BLUE}All services should be accessible at:${NC}"
echo -e "  MariaDB: localhost:3306${NC}"
echo -e "  AI_BACKEND API: http://localhost:8090${NC}"
echo -e "  Unstructured Healthcheck: http://localhost:9900/healthcheck${NC}"
echo -e "  Unstructured API: http://localhost:9900/general/v0/general${NC}"
echo -e "  Qdrant Healthcheck: http://localhost:6333/healthz${NC}"
echo -e "  Qdrant URL: http://localhost:6333/${NC}"
echo -e "  Qdrant gRPC URL: http://localhost:6334${NC}"
echo ""
echo -e "${YELLOW}MariaDB credentials:${NC}"
echo -e "  Database: $MARIADB_DATABASE"
echo -e "  Root Password: $MARIADB_ROOT_PASSWORD"
echo -e "  Username: $MARIADB_USER"
echo -e "  Password: $MARIADB_PASSWORD"
echo ""
echo -e "${BLUE}📦 Database Backup System:${NC}"
echo -e "  Create backups: ./scripts/backup-databases.sh${NC}"
echo -e "  Restore backups: ./scripts/restore-databases.sh${NC}"
echo -e "  Backup directory: ./database-backups/${NC}"
if [ "$HAS_MARIADB_BACKUP" = true ] || [ "$HAS_QDRANT_BACKUP" = true ]; then
    echo -e "${GREEN}  ✅ Backups available and can be restored${NC}"
else
    echo -e "${YELLOW}  ℹ️ No backups found - create them after adding data${NC}"
fi
echo ""
echo -e "${YELLOW}If any services failed to start, check their logs:${NC}"
echo -e "  docker logs regulaite-mariadb"
echo -e "  docker logs regulaite-ai-backend"
echo -e "  docker logs regulaite-qdrant"
echo -e "  docker logs regulaite-front-end"
echo -e "  docker logs regulaite-unstructured"
echo -e "  docker logs regulaite-redis"
echo -e "  docker logs regulaite-celery-worker"
echo -e "  docker logs regulaite-celery-flower"
echo ""
echo -e "${YELLOW}Navigate to your application at:${NC}"
echo -e "  http://localhost:3000${NC}"
echo ""
echo -e "${BLUE}💡 Quick Commands:${NC}"
echo -e "  View services: docker-compose ps${NC}"
echo -e "  Stop services: docker-compose down${NC}"
echo -e "  Restart services: docker-compose restart${NC}"
echo -e "  Update and restart: ./scripts/setup.sh${NC}"
echo -e "  Verify indexing: ./scripts/verify-indexing.sh${NC}"