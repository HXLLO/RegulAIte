# RegulAite Database Architecture & Data Distribution Strategy

## Overview

RegulAite uses a hybrid data storage approach combining MariaDB for structured relational data and Qdrant for vector embeddings and semantic search capabilities. This design optimizes performance while maintaining data integrity and supporting the advanced RAG (Retrieval-Augmented Generation) functionality.

## Database Architecture

### MariaDB (Primary Relational Database)

MariaDB handles all structured data that requires ACID compliance, complex relationships, and traditional SQL queries.

#### Core System Tables

1. **`regulaite_settings`** - Global system configuration
2. **`users`** - User authentication and management
3. **`organizations`** - Multi-tenant organization management
4. **`audit_trail`** - Compliance and security audit logging

#### Organization Management Tables

1. **`organization_assets`** - Asset inventory and classification
2. **`organization_threat_profiles`** - Threat landscape mapping
3. **`organization_regulatory_env`** - Regulatory framework associations
4. **`organization_governance_maturity`** - Governance maturity assessments
5. **`organization_custom_frameworks`** - Custom compliance frameworks

#### Document Management

1. **`documents`** - Document metadata and processing status
   - Content and embeddings stored in Qdrant
   - Only metadata, file paths, and processing status in MariaDB

#### Analysis & Results

1. **`analysis_results`** - Analysis outputs and recommendations
2. **`organization_assessment_history`** - Historical assessment data

#### Chat & Communication

1. **`chat_sessions`** - Chat session management
2. **`chat_history`** - Message history with agent attribution
3. **`task_chat_messages`** - Task-specific communications

#### Task Management

1. **`tasks`** - Task lifecycle and status tracking
2. **`task_chat_messages`** - Task-related communications

#### Agent System

1. **`agents`** - Agent definitions and configurations
2. **`agent_executions`** - Execution tracking and performance
3. **`agent_progress`** - Long-running task progress
4. **`agent_feedback`** - User feedback and ratings

#### Analytics & Reporting

1. **`agent_analytics`** - Daily agent performance aggregations
2. **`system_analytics`** - System-wide metrics

### Qdrant (Vector Database)

Qdrant is optimized for storing and retrieving vector embeddings with associated metadata for semantic search and RAG functionality.

## Data Distribution Strategy

### Data Stored in MariaDB

**Structured Relational Data:**
- User accounts and authentication
- Organization configurations and relationships
- Task management and status tracking
- Agent definitions and execution logs
- Settings and configuration data
- Audit trails and compliance logs
- Analytics and performance metrics

**Characteristics:**
- Requires ACID transactions
- Complex relational queries
- Frequent updates and status changes
- Real-time consistency requirements
- Structured reporting needs

### Data Stored in Qdrant

**Vector Embeddings & Semantic Content:**

#### 1. Document Content Collections
```json
{
  "collection_name": "documents",
  "vectors": "document_embeddings",
  "payload": {
    "document_id": "string",
    "organization_id": "string", 
    "content": "full_text_content",
    "chunk_id": "string",
    "chunk_sequence": "integer",
    "document_type": "string",
    "classification": "string",
    "metadata": {
      "filename": "string",
      "page_number": "integer",
      "section": "string",
      "extraction_method": "string"
    },
    "processed_at": "timestamp"
  }
}
```

#### 2. Framework Knowledge Base
```json
{
  "collection_name": "frameworks",
  "vectors": "framework_embeddings",
  "payload": {
    "framework_id": "string",
    "framework_name": "string",
    "control_id": "string",
    "control_text": "string",
    "control_category": "string",
    "requirements": "array",
    "guidance": "string",
    "mappings": "object"
  }
}
```

#### 3. Analysis Results Embeddings
```json
{
  "collection_name": "analysis_embeddings",
  "vectors": "analysis_embeddings",
  "payload": {
    "analysis_id": "string",
    "organization_id": "string",
    "analysis_type": "string",
    "content": "analysis_summary_content",
    "findings": "array",
    "recommendations": "array",
    "created_at": "timestamp"
  }
}
```

#### 4. Historical Context
```json
{
  "collection_name": "historical_context",
  "vectors": "context_embeddings", 
  "payload": {
    "context_id": "string",
    "organization_id": "string",
    "context_type": "string",
    "content": "historical_data",
    "time_period": "string",
    "relevance_score": "float"
  }
}
```

## Performance Optimization Strategy

### MariaDB Optimizations

1. **Indexing Strategy:**
   - Primary keys on all ID fields
   - Composite indexes on frequently queried combinations
   - Organization-based partitioning for multi-tenant queries
   - Time-based indexes for audit and analytics tables

2. **Query Optimization:**
   - Views for complex organizational profiles
   - Materialized aggregations for analytics
   - Efficient foreign key relationships

3. **Caching Strategy:**
   - Redis integration for session management
   - Application-level caching for settings and configurations

### Qdrant Optimizations

1. **Collection Design:**
   - Separate collections by content type for optimal performance
   - Organization-based payload filtering
   - Hierarchical filtering capabilities

2. **Vector Configuration:**
   - Optimized vector dimensions (1536 for OpenAI embeddings)
   - HNSW index configuration for fast similarity search
   - Quantization for memory efficiency

3. **Search Strategies:**
   - Hybrid search combining vector similarity and metadata filtering
   - Multi-stage retrieval with reranking
   - Context-aware search based on organization profile

## RAG Functionality Integration

### Document Processing Pipeline

1. **Ingestion:**
   - Document metadata stored in MariaDB `documents` table
   - Content extracted and chunked
   - Embeddings generated and stored in Qdrant

2. **Retrieval:**
   - Semantic search in Qdrant based on query embeddings
   - Metadata filtering by organization, document type, etc.
   - Context ranking and relevance scoring

3. **Augmentation:**
   - Retrieved context combined with organizational profile from MariaDB
   - Framework-specific knowledge injection
   - Historical analysis context integration

### Context Management

1. **Organization Context:**
   - Retrieved from MariaDB organization tables
   - Includes assets, threats, regulatory environment
   - Used for filtering and weighting Qdrant results

2. **User Context:**
   - Chat history and preferences from MariaDB
   - Previous analysis results
   - Role-based access and filtering

3. **Temporal Context:**
   - Historical trends from MariaDB analytics
   - Time-aware document relevance
   - Evolution of organizational maturity

## Data Consistency & Synchronization

### Document Processing
1. MariaDB tracks processing status
2. Qdrant stores processed content and embeddings
3. Cross-reference via document_id ensures consistency

### Analysis Results
1. Structured results in MariaDB for reporting
2. Semantic content in Qdrant for future retrieval
3. Bidirectional linking maintains data integrity

### Cache Invalidation
1. Document updates trigger Qdrant re-indexing
2. Organizational changes invalidate cached contexts
3. Agent configurations sync between systems

## Monitoring & Analytics

### Performance Metrics
- Query response times for both databases
- Vector search accuracy and relevance scores
- Cache hit rates and memory utilization
- Cross-database query coordination timing

### Data Quality Metrics
- Embedding quality assessments
- Document processing success rates
- Semantic search relevance feedback
- User satisfaction with retrieved contexts

## Scalability Considerations

### Horizontal Scaling
- MariaDB read replicas for analytics workloads
- Qdrant cluster for distributed vector search
- Organization-based sharding strategies

### Data Archival
- Time-based archival policies for both systems
- Cold storage for historical embeddings
- Compliance-driven retention management

This architecture ensures optimal performance for both structured queries and semantic search while maintaining the integrity needed for GRC compliance and audit requirements. 