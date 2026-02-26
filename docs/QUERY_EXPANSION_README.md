# Query Expansion for RegulAIte RAG System

## Overview

The Query Expansion feature enhances the RegulAIte RAG system's retrieval accuracy by automatically expanding user queries with domain-specific synonyms, framework terminology, and compliance-related terms. This improvement is specifically designed for Governance, Risk, and Compliance (GRC) content retrieval.

## Features

### 🎯 GRC-Specific Term Expansion
- **Risk Management Terms**: risk → threat, vulnerability, hazard, exposure
- **Compliance Terms**: compliance → conformity, adherence, observance, alignment
- **Security Terms**: security → protection, safety, defense, cybersecurity
- **Governance Terms**: governance → oversight, management, administration
- **Document Types**: report → document, assessment, evaluation, analysis

### 🏗️ Framework-Aware Expansion
- **ISO 27001**: Expands to information security, ISMS, security controls
- **GDPR/RGPD**: Expands to data protection, privacy, personal data
- **DORA**: Expands to operational resilience, digital resilience, ICT risk
- **SOX**: Expands to financial controls, internal controls
- **NIST**: Expands to cybersecurity framework, security controls
- **PCI DSS**: Expands to payment security, card data

### 📊 Smart Expansion Strategies
- **Conservative**: Top 2 synonyms per term
- **Balanced**: Top 4 synonyms per term (default)
- **Comprehensive**: Up to max_expansions synonyms per term

### 📈 Statistics & Monitoring
- Tracks expansion success rates
- Monitors average expansion ratios
- Identifies most commonly expanded terms
- Provides confidence scores for expansions

## Implementation

### Core Components

#### 1. GRCQueryExpander Class
```python
from backend.agent_framework.tools.query_expansion import get_query_expander

query_expander = get_query_expander()
expansion_result = await query_expander.expand_query(
    "security risks in data processing",
    strategy="balanced",
    max_expansions=5
)
```

#### 2. RAG Integration with Query Expansion
```python
from backend.agent_framework.factory import create_rag_agent

# Create RAG agent with query expansion enabled
rag_agent = await create_rag_agent(
    agent_id="enhanced_rag_agent",
    use_query_expansion=True,
    max_sources=10
)
```

#### 3. Enhanced DocumentFinder
```python
from backend.agent_framework.tools.document_finder import get_document_finder

# Create DocumentFinder with query expansion
doc_finder = get_document_finder(
    rag_system=your_rag_system,
    use_query_expansion=True
)
```

## Usage Examples

### Basic Query Expansion

```python
import asyncio
from backend.agent_framework.tools.query_expansion import get_query_expander

async def example_expansion():
    expander = get_query_expander()
    
    result = await expander.expand_query(
        "GDPR compliance audit",
        strategy="balanced",
        max_expansions=6,
        include_frameworks=True
    )
    
    print(f"Original: {result.original_query}")
    print(f"Expanded: {result.expanded_terms}")
    print(f"Frameworks: {result.framework_terms}")
    print(f"Confidence: {result.confidence_score}")

# Run the example
asyncio.run(example_expansion())
```

### Enhanced RAG Retrieval

```python
from backend.agent_framework.integrations.rag_integration import get_rag_integration

# Initialize RAG with query expansion
rag_integration = get_rag_integration(
    rag_system=your_rag_system,
    use_query_expansion=True
)

# Retrieve with automatic query expansion
results = await rag_integration.retrieve(
    query="risk assessment procedures",
    top_k=10
)

# Check if expansion was used
if "query_expansion" in results:
    expansion_info = results["query_expansion"]
    print(f"Expanded with: {expansion_info['expanded_terms']}")
    print(f"Confidence: {expansion_info['confidence_score']}")
```

### Custom Synonyms and Framework Mappings

```python
# Add organization-specific terms
expander = get_query_expander()

# Add custom synonyms
expander.add_custom_synonyms("pentest", [
    "penetration testing", 
    "security testing", 
    "ethical hacking"
])

# Add custom framework mapping
expander.add_framework_mapping("CUSTOM-FRAMEWORK", [
    "custom control framework",
    "organization security standard"
])
```

## Configuration Options

### Expansion Strategies

| Strategy | Description | Synonyms per Term | Use Case |
|----------|-------------|-------------------|----------|
| `conservative` | Minimal expansion | 2 | Precise searches |
| `balanced` | Moderate expansion | 4 | General use (default) |
| `comprehensive` | Maximum expansion | Up to limit | Broad discovery |

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strategy` | str | "balanced" | Expansion strategy |
| `max_expansions` | int | 10 | Maximum expanded terms |
| `include_frameworks` | bool | True | Include framework-specific terms |

## Performance Benefits

### Expected Improvements
- **Recall Improvement**: 15-30% for domain-specific queries
- **User Experience**: Better results for natural language queries
- **Coverage**: Enhanced discovery across framework variations

### Example Transformations

| Original Query | Expanded Terms |
|----------------|----------------|
| "security risks" | threat, vulnerability, hazard, exposure, danger |
| "GDPR compliance" | data protection, privacy, personal data, RGPD |
| "access controls" | authentication, authorization, identity management |
| "risk assessment" | risk evaluation, risk analysis, threat assessment |

## Integration Points

### 1. RAG Agent Framework
- Automatic expansion in `RAGAgent.process_query()`
- Statistics logging in query processing
- Configurable via `create_rag_agent(use_query_expansion=True)`

### 2. Document Finder
- Multi-query search with expanded terms
- Deduplication of results across query variations
- Expansion metadata in search results

### 3. Search Tools
- Enhanced `query_reformulation` tool with `grc_expand` strategy
- Integration with existing search workflows

## Monitoring and Statistics

### Available Metrics
```python
expander = get_query_expander()
stats = expander.get_expansion_statistics()

print(f"Total expansions: {stats['total_expansions']}")
print(f"Success rate: {stats['successful_expansions']}/{stats['total_expansions']}")
print(f"Average ratio: {stats['average_expansion_ratio']:.2f}")
print(f"Top terms: {stats['most_expanded_terms']}")
```

### Logging
Query expansion activities are logged at various levels:
- **INFO**: Successful expansions with term counts and confidence
- **WARNING**: Expansion failures with fallback to original query
- **DEBUG**: Detailed expansion process information

## Testing

Run the comprehensive test suite:

```bash
python test_query_expansion.py
```

This test script validates:
- Basic query expansion functionality
- Integration with RAG agent framework
- Custom synonym management
- Statistics tracking
- Error handling

## Error Handling

The system includes robust error handling:
- **Graceful degradation**: Falls back to original query if expansion fails
- **Initialization safety**: Continues without expansion if setup fails
- **Input validation**: Handles malformed queries and parameters
- **Performance protection**: Limits expansion to prevent over-expansion

## Future Enhancements

### Planned Features
1. **Machine Learning Integration**: Learn from user feedback to improve expansions
2. **Dynamic Synonym Discovery**: Automatically discover new synonyms from document corpus
3. **Context-Aware Expansion**: Tailor expansions based on user role and document context
4. **Multi-language Support**: Expand queries across different languages
5. **Industry-Specific Customization**: Pre-built synonym sets for different industries

### Performance Optimizations
1. **Caching**: Cache frequent expansions for faster retrieval
2. **Batch Processing**: Process multiple queries simultaneously
3. **Adaptive Strategies**: Automatically adjust strategy based on query performance

## Best Practices

### When to Enable Query Expansion
- ✅ **Recommended for**: General document search, exploration, natural language queries
- ✅ **Ideal for**: Users unfamiliar with specific GRC terminology
- ⚠️ **Consider carefully for**: Highly specific technical searches
- ❌ **Not recommended for**: Exact phrase matching, regulatory citation lookup

### Optimization Tips
1. Start with "balanced" strategy and adjust based on results
2. Monitor expansion statistics to identify optimization opportunities
3. Add organization-specific synonyms for better relevance
4. Use conservative strategy for precise searches
5. Enable comprehensive strategy for discovery and research queries

## Troubleshooting

### Common Issues

**Query Expansion Not Working**
- Verify `use_query_expansion=True` in agent creation
- Check logs for initialization errors
- Ensure proper module imports

**Low Expansion Quality**
- Review and customize synonym dictionaries
- Adjust expansion strategy
- Add domain-specific terms

**Performance Issues**
- Reduce `max_expansions` parameter
- Use conservative strategy
- Consider caching for frequent queries

### Debug Information
Enable debug logging to see detailed expansion process:
```python
import logging
logging.getLogger('backend.agent_framework.tools.query_expansion').setLevel(logging.DEBUG)
``` 