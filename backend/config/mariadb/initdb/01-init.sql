-- Create or check regulaite database
CREATE DATABASE IF NOT EXISTS regulaite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE regulaite;

-- Drop the table if it exists to ensure it's recreated properly
DROP TABLE IF EXISTS chat_history;

-- Table for chat messages history
CREATE TABLE chat_history (
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
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

-- Table for global settings
CREATE TABLE IF NOT EXISTS regulaite_settings (
    setting_key VARCHAR(255) PRIMARY KEY,
    setting_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    description TEXT
) ENGINE=InnoDB;

-- Insert default settings if they don't exist
INSERT IGNORE INTO regulaite_settings (setting_key, setting_value, description) VALUES
('llm_model', 'gpt-4', 'Default LLM model'),
('llm_temperature', '0.7', 'Default temperature for LLM'),
('llm_max_tokens', '2048', 'Default max tokens for LLM'),
('llm_top_p', '1', 'Default top_p value for LLM'),
('enable_chat_history', 'true', 'Whether to save chat history');

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
) ENGINE=InnoDB;

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
) ENGINE=InnoDB;

-- Table for storing chat sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    title VARCHAR(255) DEFAULT 'New Conversation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    preview TEXT,
    message_count INT DEFAULT 0,
    
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_last_message_time (last_message_time)
) ENGINE=InnoDB;

-- Add any existing sessions to the table by querying chat_history
INSERT IGNORE INTO chat_sessions (session_id, user_id, title, created_at, last_message_time, preview, message_count)
SELECT 
    session_id,
    user_id,
    CONCAT('Conversation ', LEFT(session_id, 8)) as title,
    MIN(timestamp) as created_at,
    MAX(timestamp) as last_message_time,
    (
        SELECT message_text 
        FROM chat_history ch2 
        WHERE ch2.session_id = ch1.session_id 
        ORDER BY timestamp DESC 
        LIMIT 1
    ) as preview,
    COUNT(*) as message_count
FROM 
    chat_history ch1
GROUP BY 
    session_id, user_id;

-- Table for storing feedback on agent responses
CREATE TABLE IF NOT EXISTS agent_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    message_id VARCHAR(64) DEFAULT '',
    rating INT NOT NULL,
    feedback_text TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    context_used BOOLEAN,
    model VARCHAR(64),
    
    INDEX (agent_id),
    INDEX (session_id)
);

-- Table for tracking agent executions
CREATE TABLE IF NOT EXISTS agent_executions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL,
    session_id VARCHAR(64) NOT NULL,
    task TEXT NOT NULL,
    model VARCHAR(64),
    response_time_ms INT,
    token_count INT,
    prompt_token_count INT,
    completion_token_count INT,
    error BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX (agent_id),
    INDEX (session_id),
    INDEX (timestamp)
);

-- Table for tracking agent execution progress (for long-running tasks)
CREATE TABLE IF NOT EXISTS agent_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    execution_id INT NOT NULL,
    progress_percent FLOAT,
    status VARCHAR(32) NOT NULL,
    status_message TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (execution_id) REFERENCES agent_executions(id) ON DELETE CASCADE,
    INDEX (execution_id)
);

-- Table for agent usage analytics
CREATE TABLE IF NOT EXISTS agent_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL,
    day DATE NOT NULL,
    execution_count INT DEFAULT 0,
    avg_response_time_ms FLOAT,
    avg_rating FLOAT,
    error_rate FLOAT,
    unique_users INT DEFAULT 0,
    success_rate FLOAT,
    
    UNIQUE KEY (agent_id, day),
    INDEX (agent_id),
    INDEX (day)
);

-- Grant privileges to regulaite_user
GRANT ALL PRIVILEGES ON regulaite.* TO 'regulaite_user'@'%';
FLUSH PRIVILEGES;
