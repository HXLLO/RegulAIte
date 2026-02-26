-- RegulAite Database Initialization Script
-- Creates all necessary tables for the RegulAite GRC platform
-- Including: Core tables, Organization management, Agent system, Analytics

-- Create or check regulaite database
CREATE DATABASE IF NOT EXISTS regulaite CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE regulaite;

-- =============================================
-- CORE SYSTEM TABLES
-- =============================================

-- Table for global settings
CREATE TABLE IF NOT EXISTS regulaite_settings (
    setting_key VARCHAR(255) PRIMARY KEY,
    setting_value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    description TEXT,
    category VARCHAR(50) DEFAULT 'general',
    is_system BOOLEAN DEFAULT FALSE,
    
    INDEX idx_category (category),
    INDEX idx_is_system (is_system)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- USER MANAGEMENT TABLES
-- =============================================

-- Create user table for authentication and user management
CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    username VARCHAR(255) UNIQUE,
    role ENUM('admin', 'analyst', 'auditor', 'viewer') DEFAULT 'analyst',
    organization_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    settings JSON,
    is_active BOOLEAN DEFAULT TRUE,

    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_organization_id (organization_id),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- ORGANIZATION MANAGEMENT TABLES
-- =============================================

-- Table principale des organisations
CREATE TABLE IF NOT EXISTS organizations (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sector ENUM('banking', 'insurance', 'healthcare', 'energy', 'telecom', 'technology', 'public', 'general') DEFAULT 'general',
    size ENUM('startup', 'small', 'medium', 'large', 'enterprise') DEFAULT 'medium',
    employee_count INT DEFAULT 100,
    annual_revenue VARCHAR(50) DEFAULT '10M-100M',
    organization_type ENUM('startup', 'sme', 'large_corp', 'public_sector', 'healthcare', 'financial', 'technology', 'manufacturing', 'energy', 'telecom') DEFAULT 'technology',
    business_model ENUM('traditional', 'digital', 'hybrid', 'platform') DEFAULT 'traditional',
    digital_maturity ENUM('basic', 'intermediate', 'advanced', 'leading') DEFAULT 'intermediate',
    risk_appetite ENUM('conservative', 'moderate', 'aggressive') DEFAULT 'moderate',
    geographical_presence JSON,
    custom_settings JSON,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_sector (sector),
    INDEX idx_size (size),
    INDEX idx_organization_type (organization_type),
    INDEX idx_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des actifs organisationnels
CREATE TABLE IF NOT EXISTS organization_assets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id VARCHAR(50) NOT NULL,
    asset_id VARCHAR(50) NOT NULL,
    asset_name VARCHAR(255) NOT NULL,
    asset_type ENUM('system', 'data', 'application', 'network', 'human', 'physical') NOT NULL,
    criticality ENUM('very_low', 'low', 'medium', 'high', 'very_high') DEFAULT 'medium',
    description TEXT,
    owner VARCHAR(255),
    location VARCHAR(255),
    business_value ENUM('very_low', 'low', 'medium', 'high', 'very_high') DEFAULT 'medium',
    regulatory_classification VARCHAR(100),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    UNIQUE KEY unique_org_asset (organization_id, asset_id),
    INDEX idx_organization_id (organization_id),
    INDEX idx_asset_type (asset_type),
    INDEX idx_criticality (criticality),
    INDEX idx_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table des profils de menaces organisationnelles
CREATE TABLE IF NOT EXISTS organization_threat_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id VARCHAR(50) NOT NULL,
    threat_type VARCHAR(100) NOT NULL,
    likelihood ENUM('very_low', 'low', 'medium', 'high', 'very_high') DEFAULT 'medium',
    sophistication ENUM('basic', 'intermediate', 'advanced', 'expert') DEFAULT 'intermediate',
    motivation ENUM('financial', 'espionage', 'activism', 'disruption') DEFAULT 'financial',
    resources ENUM('limited', 'moderate', 'substantial', 'extensive') DEFAULT 'moderate',
    persistence ENUM('low', 'medium', 'high', 'very_high') DEFAULT 'medium',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    INDEX idx_organization_id (organization_id),
    INDEX idx_threat_type (threat_type),
    INDEX idx_likelihood (likelihood),
    INDEX idx_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table de l'environnement réglementaire
CREATE TABLE IF NOT EXISTS organization_regulatory_env (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id VARCHAR(50) NOT NULL,
    frameworks JSON, -- Liste des frameworks applicables
    regulatory_pressure ENUM('low', 'medium', 'high', 'very_high') DEFAULT 'medium',
    audit_frequency ENUM('quarterly', 'bi_annual', 'annual', 'ad_hoc') DEFAULT 'annual',
    penalties_exposure ENUM('low', 'medium', 'high', 'very_high') DEFAULT 'medium',
    external_oversight JSON, -- Liste des autorités de supervision
    certification_requirements JSON, -- Liste des certifications requises
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    UNIQUE KEY unique_org_regulatory (organization_id),
    INDEX idx_organization_id (organization_id),
    INDEX idx_regulatory_pressure (regulatory_pressure)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table de maturité de gouvernance
CREATE TABLE IF NOT EXISTS organization_governance_maturity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id VARCHAR(50) NOT NULL,
    domain VARCHAR(50) NOT NULL, -- strategic, risk, compliance, etc.
    maturity_level ENUM('initial', 'developing', 'defined', 'managed', 'optimized') DEFAULT 'developing',
    assessment_date DATE,
    assessor VARCHAR(255),
    score INT, -- Score numérique optionnel (0-100)
    comments TEXT,
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    UNIQUE KEY unique_org_domain (organization_id, domain),
    INDEX idx_organization_id (organization_id),
    INDEX idx_domain (domain),
    INDEX idx_maturity_level (maturity_level),
    INDEX idx_active (active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- DOCUMENT AND KNOWLEDGE MANAGEMENT
-- =============================================

-- Table for document metadata (content stored in Qdrant)
CREATE TABLE IF NOT EXISTS documents (
    id VARCHAR(255) PRIMARY KEY,
    organization_id VARCHAR(50),
    filename VARCHAR(500) NOT NULL,
    original_filename VARCHAR(500),
    file_path VARCHAR(1000),
    file_size BIGINT,
    file_hash VARCHAR(64),
    mime_type VARCHAR(100),
    document_type ENUM('policy', 'procedure', 'risk_assessment', 'audit_report', 'compliance_report', 'framework', 'evidence', 'other') DEFAULT 'other',
    classification ENUM('public', 'internal', 'confidential', 'restricted') DEFAULT 'internal',
    status ENUM('pending', 'processing', 'processed', 'failed', 'archived') DEFAULT 'pending',
    processing_status JSON, -- Detailed processing information
    metadata JSON, -- Document-specific metadata
    uploaded_by VARCHAR(255),
    processed_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_organization_id (organization_id),
    INDEX idx_document_type (document_type),
    INDEX idx_status (status),
    INDEX idx_classification (classification),
    INDEX idx_uploaded_by (uploaded_by),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- FRAMEWORK MANAGEMENT
-- =============================================

-- Table de configuration des frameworks personnalisés
CREATE TABLE IF NOT EXISTS organization_custom_frameworks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id VARCHAR(50) NOT NULL,
    framework_name VARCHAR(100) NOT NULL,
    framework_version VARCHAR(20),
    framework_data JSON NOT NULL, -- Structure complète du framework
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    UNIQUE KEY unique_org_framework (organization_id, framework_name, framework_version),
    INDEX idx_organization_id (organization_id),
    INDEX idx_framework_name (framework_name),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- ANALYSIS AND RESULTS TABLES
-- =============================================

-- Table des résultats d'analyse
CREATE TABLE IF NOT EXISTS analysis_results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id VARCHAR(50) NOT NULL,
    analysis_type ENUM('risk_assessment', 'compliance_analysis', 'governance_analysis', 'gap_analysis', 'vulnerability_assessment', 'audit_preparation') NOT NULL,
    analysis_id VARCHAR(100), -- ID unique de l'analyse
    title VARCHAR(255),
    description TEXT,
    result_data JSON NOT NULL, -- Résultats complets de l'analyse
    summary JSON, -- Résumé pour affichage rapide
    recommendations JSON, -- Recommandations structurées
    metadata JSON, -- Métadonnées (versions, paramètres, etc.)
    status ENUM('pending', 'processing', 'completed', 'failed', 'archived') DEFAULT 'completed',
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    created_by VARCHAR(255),
    assigned_to VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    expires_at TIMESTAMP NULL, -- Optionnel pour l'archivage automatique
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_organization_id (organization_id),
    INDEX idx_analysis_type (analysis_type),
    INDEX idx_analysis_id (analysis_id),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table d'historique des évaluations
CREATE TABLE IF NOT EXISTS organization_assessment_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id VARCHAR(50) NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,
    assessment_date DATE NOT NULL,
    methodology VARCHAR(50),
    scope TEXT,
    assessor VARCHAR(255),
    score DECIMAL(5,2), -- Score global (ex: 85.50)
    summary TEXT,
    detailed_results JSON,
    recommendations JSON,
    status ENUM('draft', 'final', 'superseded') DEFAULT 'final',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (assessor) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_organization_id (organization_id),
    INDEX idx_assessment_type (assessment_type),
    INDEX idx_assessment_date (assessment_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- CHAT AND MESSAGING SYSTEM
-- =============================================

-- Table for storing chat sessions
CREATE TABLE IF NOT EXISTS chat_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL UNIQUE,
    user_id VARCHAR(255) NOT NULL,
    organization_id VARCHAR(50),
    title VARCHAR(255) DEFAULT 'New Conversation',
    context_type ENUM('general', 'analysis', 'document_review', 'compliance_check') DEFAULT 'general',
    context_data JSON, -- Additional context information
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    preview TEXT,
    message_count INT DEFAULT 0,
    is_archived BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
    INDEX idx_session_id (session_id),
    INDEX idx_user_id (user_id),
    INDEX idx_organization_id (organization_id),
    INDEX idx_last_message_time (last_message_time),
    INDEX idx_is_archived (is_archived)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for chat messages history
CREATE TABLE IF NOT EXISTS chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    organization_id VARCHAR(50),
    message_text TEXT NOT NULL,
    message_role ENUM('user', 'assistant', 'system') NOT NULL,
    agent_id VARCHAR(64), -- Which agent generated the response
    context_used BOOLEAN DEFAULT FALSE, -- Whether RAG context was used
    tokens_used INT,
    processing_time_ms INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSON,

    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_organization_id (organization_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_agent_id (agent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- TASK MANAGEMENT SYSTEM
-- =============================================

-- Create task tracking table
CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR(255) PRIMARY KEY,
    organization_id VARCHAR(50),
    user_id VARCHAR(255),
    task_type VARCHAR(100) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    status ENUM('queued', 'processing', 'completed', 'failed', 'cancelled', 'pending_review') NOT NULL,
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    progress_percent FLOAT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    started_at TIMESTAMP NULL,
    completed_at TIMESTAMP NULL,
    estimated_duration INT, -- In minutes
    actual_duration INT, -- In minutes
    result JSON,
    error TEXT,
    message TEXT,
    parameters JSON,
    assigned_agent VARCHAR(64),
    
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_task_type (task_type),
    INDEX idx_priority (priority),
    INDEX idx_user_id (user_id),
    INDEX idx_organization_id (organization_id),
    INDEX idx_created_at (created_at),
    INDEX idx_assigned_agent (assigned_agent)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for task chat messages
CREATE TABLE IF NOT EXISTS task_chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message_id VARCHAR(255) NOT NULL UNIQUE,
    task_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    role ENUM('user', 'assistant', 'system') NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE CASCADE,
    INDEX idx_message_id (message_id),
    INDEX idx_task_id (task_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- AGENT SYSTEM TABLES
-- =============================================

-- Table for agent definitions and configurations
CREATE TABLE IF NOT EXISTS agents (
    agent_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    agent_type ENUM('universal_tool', 'risk_assessment', 'compliance_analysis', 'governance_analysis', 'gap_analysis', 'document_processor') NOT NULL,
    capabilities JSON, -- List of capabilities
    configuration JSON, -- Agent-specific configuration
    model_config JSON, -- LLM model configuration
    is_active BOOLEAN DEFAULT TRUE,
    version VARCHAR(20) DEFAULT '1.0',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_agent_type (agent_type),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for tracking agent executions
CREATE TABLE IF NOT EXISTS agent_executions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    execution_id VARCHAR(255) UNIQUE NOT NULL,
    agent_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(255),
    organization_id VARCHAR(50),
    session_id VARCHAR(64) NOT NULL,
    task VARCHAR(500) NOT NULL,
    input_data JSON,
    output_data JSON,
    model VARCHAR(64),
    response_time_ms INT,
    token_count INT,
    prompt_token_count INT,
    completion_token_count INT,
    cost_estimate DECIMAL(10,6), -- Estimated cost in USD
    error BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    context_used BOOLEAN DEFAULT FALSE,
    context_sources JSON, -- Sources used for RAG
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
    INDEX idx_execution_id (execution_id),
    INDEX idx_agent_id (agent_id),
    INDEX idx_user_id (user_id),
    INDEX idx_organization_id (organization_id),
    INDEX idx_session_id (session_id),
    INDEX idx_timestamp (timestamp),
    INDEX idx_error (error)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for tracking agent execution progress (for long-running tasks)
CREATE TABLE IF NOT EXISTS agent_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    execution_id INT NOT NULL,
    progress_percent FLOAT,
    status VARCHAR(32) NOT NULL,
    status_message TEXT,
    step_name VARCHAR(255),
    total_steps INT,
    current_step INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (execution_id) REFERENCES agent_executions(id) ON DELETE CASCADE,
    INDEX idx_execution_id (execution_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for storing feedback on agent responses
CREATE TABLE IF NOT EXISTS agent_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    execution_id VARCHAR(255),
    agent_id VARCHAR(64) NOT NULL,
    user_id VARCHAR(255),
    session_id VARCHAR(64) NOT NULL,
    message_id VARCHAR(64) DEFAULT '',
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    feedback_type ENUM('accuracy', 'helpfulness', 'completeness', 'performance', 'other') DEFAULT 'other',
    context_used BOOLEAN,
    model VARCHAR(64),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_execution_id (execution_id),
    INDEX idx_agent_id (agent_id),
    INDEX idx_user_id (user_id),
    INDEX idx_session_id (session_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- ANALYTICS AND REPORTING TABLES
-- =============================================

-- Table for agent usage analytics (daily aggregations)
CREATE TABLE IF NOT EXISTS agent_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    agent_id VARCHAR(64) NOT NULL,
    organization_id VARCHAR(50),
    day DATE NOT NULL,
    execution_count INT DEFAULT 0,
    success_count INT DEFAULT 0,
    error_count INT DEFAULT 0,
    avg_response_time_ms FLOAT,
    avg_rating FLOAT,
    total_tokens INT DEFAULT 0,
    total_cost DECIMAL(10,6) DEFAULT 0,
    unique_users INT DEFAULT 0,
    success_rate FLOAT,
    
    FOREIGN KEY (agent_id) REFERENCES agents(agent_id) ON DELETE CASCADE,
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    UNIQUE KEY unique_agent_org_day (agent_id, organization_id, day),
    INDEX idx_agent_id (agent_id),
    INDEX idx_organization_id (organization_id),
    INDEX idx_day (day)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table for system-wide analytics
CREATE TABLE IF NOT EXISTS system_analytics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6),
    metric_category ENUM('performance', 'usage', 'cost', 'quality', 'error') NOT NULL,
    organization_id VARCHAR(50),
    day DATE NOT NULL,
    metadata JSON,
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
    UNIQUE KEY unique_metric_org_day (metric_name, organization_id, day),
    INDEX idx_metric_name (metric_name),
    INDEX idx_metric_category (metric_category),
    INDEX idx_organization_id (organization_id),
    INDEX idx_day (day)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- AUDIT AND COMPLIANCE TABLES
-- =============================================

-- Table for audit trails
CREATE TABLE IF NOT EXISTS audit_trail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    organization_id VARCHAR(50),
    user_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    details JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_organization_id (organization_id),
    INDEX idx_user_id (user_id),
    INDEX idx_action (action),
    INDEX idx_resource_type (resource_type),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- INITIALIZE DEFAULT DATA
-- =============================================

-- Insert default settings
INSERT IGNORE INTO regulaite_settings (setting_key, setting_value, description, category, is_system) VALUES
('llm_model', 'gpt-4', 'Default LLM model', 'ai', TRUE),
('llm_temperature', '0.7', 'Default temperature for LLM', 'ai', TRUE),
('llm_max_tokens', '2048', 'Default max tokens for LLM', 'ai', TRUE),
('llm_top_p', '1', 'Default top_p value for LLM', 'ai', TRUE),
('enable_chat_history', 'true', 'Whether to save chat history', 'general', FALSE),
('max_file_size_mb', '50', 'Maximum file upload size in MB', 'documents', FALSE),
('supported_file_types', '["pdf", "docx", "doc", "txt", "xlsx", "csv"]', 'Supported file types for upload', 'documents', FALSE),
('rag_chunk_size', '1000', 'Default chunk size for RAG processing', 'ai', TRUE),
('rag_chunk_overlap', '200', 'Default chunk overlap for RAG processing', 'ai', TRUE),
('default_analysis_retention_days', '365', 'Default retention period for analysis results', 'general', FALSE);

-- Insert default organization
INSERT IGNORE INTO organizations (
    id, name, sector, size, organization_type, 
    business_model, digital_maturity, risk_appetite
) VALUES (
    'default_org', 
    'RegulAIte Demo Organization', 
    'technology', 
    'medium', 
    'technology',
    'digital', 
    'intermediate', 
    'moderate'
);

-- Insert default agents
INSERT IGNORE INTO agents (agent_id, name, description, agent_type, capabilities, configuration) VALUES
('universal_tools', 'Universal Tool Suite', 'Provides foundational GRC capabilities including document finding, entity extraction, and cross-referencing', 'universal_tool', 
 JSON_ARRAY('document_finder', 'entity_extractor', 'cross_reference', 'document_relationship_mapper', 'temporal_analyzer'),
 JSON_OBJECT('max_documents', 1000, 'entity_types', JSON_ARRAY('controls', 'risks', 'findings', 'requirements', 'assets'))),

('risk_assessment', 'Risk Assessment Module', 'Comprehensive risk analysis and assessment capabilities', 'risk_assessment',
 JSON_ARRAY('risk_identification', 'risk_analysis', 'risk_evaluation', 'risk_treatment', 'risk_monitoring'),
 JSON_OBJECT('risk_scales', JSON_OBJECT('likelihood', JSON_ARRAY('very_low', 'low', 'medium', 'high', 'very_high'), 'impact', JSON_ARRAY('very_low', 'low', 'medium', 'high', 'very_high')))),

('compliance_analysis', 'Compliance Analysis Module', 'Framework compliance analysis and gap identification', 'compliance_analysis',
 JSON_ARRAY('framework_mapping', 'gap_analysis', 'compliance_monitoring', 'control_assessment'),
 JSON_OBJECT('supported_frameworks', JSON_ARRAY('iso27001', 'iso27002', 'nist', 'sox', 'gdpr', 'hipaa'))),

('governance_analysis', 'Governance Analysis Module', 'Organizational governance maturity and effectiveness analysis', 'governance_analysis',
 JSON_ARRAY('maturity_assessment', 'governance_structure_analysis', 'policy_effectiveness', 'strategic_alignment'),
 JSON_OBJECT('maturity_model', 'cmmi', 'assessment_areas', JSON_ARRAY('strategic', 'risk', 'compliance', 'security'))),

('gap_analysis', 'Gap Analysis Module', 'Identifies gaps between current state and desired state', 'gap_analysis',
 JSON_ARRAY('current_state_assessment', 'target_state_definition', 'gap_identification', 'remediation_planning'),
 JSON_OBJECT('analysis_types', JSON_ARRAY('control_gaps', 'process_gaps', 'technology_gaps', 'skill_gaps'))),

('document_processor', 'Document Processing Module', 'Intelligent document processing and analysis', 'document_processor',
 JSON_ARRAY('document_parsing', 'content_extraction', 'classification', 'metadata_enrichment'),
 JSON_OBJECT('supported_formats', JSON_ARRAY('pdf', 'docx', 'doc', 'txt', 'xlsx'), 'extraction_methods', JSON_ARRAY('unstructured', 'llamaparse', 'doctly')));

-- Insert sample organizational assets for default org
INSERT IGNORE INTO organization_assets (
    organization_id, asset_id, asset_name, asset_type, criticality, description
) VALUES 
    ('default_org', 'SYS-001', 'Information Systems', 'system', 'high', 'Core IT infrastructure'),
    ('default_org', 'DATA-001', 'Customer Data', 'data', 'very_high', 'Customer and business data'),
    ('default_org', 'APP-001', 'Business Applications', 'application', 'high', 'Critical business applications'),
    ('default_org', 'NET-001', 'Network Infrastructure', 'network', 'medium', 'Network and telecommunications'),
    ('default_org', 'HR-001', 'Human Resources', 'human', 'high', 'Personnel and competencies');

-- Insert sample threat profiles for default org
INSERT IGNORE INTO organization_threat_profiles (
    organization_id, threat_type, likelihood, sophistication, motivation
) VALUES 
    ('default_org', 'Cybercriminals', 'medium', 'intermediate', 'financial'),
    ('default_org', 'Insider Threats', 'low', 'basic', 'financial'),
    ('default_org', 'Hacktivists', 'low', 'intermediate', 'activism'),
    ('default_org', 'Human Error', 'high', 'basic', 'disruption');

-- Insert default regulatory environment
INSERT IGNORE INTO organization_regulatory_env (
    organization_id, frameworks, regulatory_pressure, audit_frequency
) VALUES (
    'default_org', 
    JSON_ARRAY('iso27001', 'gdpr'), 
    'medium', 
    'annual'
);

-- Insert default governance maturity
INSERT IGNORE INTO organization_governance_maturity (
    organization_id, domain, maturity_level, assessment_date
) VALUES 
    ('default_org', 'strategic', 'defined', CURDATE()),
    ('default_org', 'risk', 'developing', CURDATE()),
    ('default_org', 'compliance', 'defined', CURDATE()),
    ('default_org', 'security', 'developing', CURDATE());

-- Add foreign key constraints for users table
ALTER TABLE users ADD CONSTRAINT fk_users_organization 
    FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL;

-- =============================================
-- CREATE USEFUL VIEWS
-- =============================================

-- Vue complète des organisations avec leurs contextes
CREATE OR REPLACE VIEW organization_complete_profiles AS
SELECT 
    o.*,
    ore.frameworks,
    ore.regulatory_pressure,
    ore.audit_frequency,
    COUNT(DISTINCT oa.id) as asset_count,
    COUNT(DISTINCT otp.id) as threat_count,
    AVG(CASE 
        WHEN ogm.maturity_level = 'initial' THEN 1
        WHEN ogm.maturity_level = 'developing' THEN 2
        WHEN ogm.maturity_level = 'defined' THEN 3
        WHEN ogm.maturity_level = 'managed' THEN 4
        WHEN ogm.maturity_level = 'optimized' THEN 5
        ELSE 2
    END) as avg_governance_maturity
FROM organizations o
LEFT JOIN organization_regulatory_env ore ON o.id = ore.organization_id
LEFT JOIN organization_assets oa ON o.id = oa.organization_id AND oa.active = 1
LEFT JOIN organization_threat_profiles otp ON o.id = otp.organization_id AND otp.active = 1
LEFT JOIN organization_governance_maturity ogm ON o.id = ogm.organization_id AND ogm.active = 1
WHERE o.active = 1
GROUP BY o.id, ore.frameworks, ore.regulatory_pressure, ore.audit_frequency;

-- Vue des analyses récentes par organisation
CREATE OR REPLACE VIEW recent_analyses_by_org AS
SELECT 
    organization_id,
    analysis_type,
    COUNT(*) as analysis_count,
    MAX(created_at) as last_analysis_date,
    AVG(JSON_EXTRACT(metadata, '$.duration_seconds')) as avg_duration
FROM analysis_results 
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    AND status = 'completed'
GROUP BY organization_id, analysis_type;

-- Vue des performances des agents
CREATE OR REPLACE VIEW agent_performance_summary AS
SELECT 
    a.agent_id,
    a.name,
    a.agent_type,
    COUNT(ae.id) as total_executions,
    COUNT(CASE WHEN ae.error = FALSE THEN 1 END) as successful_executions,
    AVG(ae.response_time_ms) as avg_response_time,
    AVG(af.rating) as avg_rating,
    SUM(ae.cost_estimate) as total_cost
FROM agents a
LEFT JOIN agent_executions ae ON a.agent_id = ae.agent_id
LEFT JOIN agent_feedback af ON ae.execution_id = af.execution_id
WHERE a.is_active = TRUE
    AND ae.timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY a.agent_id, a.name, a.agent_type;

-- Grant privileges to regulaite_user
GRANT ALL PRIVILEGES ON regulaite.* TO 'regulaite_user'@'%';
FLUSH PRIVILEGES;
