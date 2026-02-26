"""
Factory for creating and initializing agents in the RegulAIte Agent Framework.

This module provides factory functions for creating different types of agents
with all necessary components.
"""
from typing import Dict, List, Optional, Any, Union
import logging

from .agent import Agent
from .rag_agent import RAGAgent
from .orchestrator import OrchestratorAgent
from .tool_registry import ToolRegistry
from .query_parser import QueryParser
from .integrations.rag_integration import get_rag_integration
from .integrations.llm_integration import get_llm_integration, LLMIntegration, get_llm_client

# Set up logging
logger = logging.getLogger(__name__)

# Backward compatibility alias
LLMClient = LLMIntegration

async def create_rag_agent(agent_id: str = "rag_agent",
                     name: str = "RAG Agent",
                     tool_registry: Optional[ToolRegistry] = None,
                     query_parser: Optional[QueryParser] = None,
                     model: str = "gpt-4",
                     max_sources: int = 5,
                     use_query_expansion: bool = False,
                     **kwargs) -> RAGAgent:
    """
    Create and initialize a RAG agent with all necessary components.
    
    Args:
        agent_id: Unique identifier for the agent
        name: Human-readable name for the agent
        tool_registry: Registry of tools (if None, a new one will be created)
        query_parser: Query parser (if None, a new one will be created)
        model: LLM model to use
        max_sources: Maximum number of sources to retrieve
        use_query_expansion: Whether to enable query expansion for better retrieval
        **kwargs: Additional arguments for the agent
        
    Returns:
        An initialized RAG agent
    """
    logger.info(f"Creating RAG agent: {agent_id}")
    
    # Create components if not provided
    if tool_registry is None:
        tool_registry = ToolRegistry()
        
    # Get integrations first
    rag_integration = get_rag_integration(use_query_expansion=use_query_expansion)
    llm_integration = get_llm_integration(model=model)
    
    if use_query_expansion:
        logger.info("RAG agent created with query expansion enabled")
        
    if query_parser is None:
        query_parser = QueryParser(llm_client=llm_integration)
        
    # Create and initialize the agent
    agent = RAGAgent(
        agent_id=agent_id,
        name=name,
        tool_registry=tool_registry,
        query_parser=query_parser,
        retrieval_system=rag_integration,
        llm_client=llm_integration,
        max_sources=max_sources
    )
    
    # Discover and register tools
    try:
        # First try the correct package path for tools
        tool_ids = tool_registry.discover_tools("agent_framework.tools")
        logger.info(f"Registered {len(tool_ids)} tools: {', '.join(tool_ids)}")
        
        # If no tools were discovered, try to import and register them directly
        if len(tool_ids) == 0:
            logger.warning("No tools discovered via package discovery, trying direct import")
            try:
                from agent_framework.tools.search_tools import (
                    query_reformulation, 
                    filter_search, 
                    extract_search_entities
                )
                
                # Register tools directly
                tool_registry.register(query_reformulation)
                tool_registry.register(filter_search)
                tool_registry.register(extract_search_entities)
                
                logger.info("Successfully registered tools via direct import: query_reformulation, filter_search, extract_search_entities")
            except ImportError as e:
                logger.error(f"Could not import tools directly: {str(e)}")
                
    except Exception as e:
        logger.error(f"Error discovering tools: {str(e)}")
    
    return agent

async def create_orchestrator_agent(
    agent_id: str = "orchestrator",
    name: str = "Orchestrateur Principal GRC",
    llm_client: Optional[LLMClient] = None,
    log_callback = None,
    **kwargs
) -> OrchestratorAgent:
    """
    Crée et initialise l'agent orchestrateur principal.
    
    Args:
        agent_id: Identifiant unique de l'agent
        name: Nom humain de l'agent
        llm_client: Client LLM (si None, utilise le client par défaut)
        log_callback: Callback function for detailed logging
        **kwargs: Arguments supplémentaires
        
    Returns:
        Agent orchestrateur initialisé
    """
    logger.info(f"Création de l'agent orchestrateur: {agent_id}")
    
    # Créer le client LLM si non fourni
    if llm_client is None:
        llm_client = get_llm_client()
    
    # Créer l'agent orchestrateur
    orchestrator = OrchestratorAgent(llm_client=llm_client, log_callback=log_callback)
    
    return orchestrator

async def create_specialized_agents(
    orchestrator: OrchestratorAgent,
    rag_system = None,
    log_callback = None,
    **kwargs
) -> Dict[str, Agent]:
    """
    Crée et enregistre les agents spécialisés dans l'orchestrateur.
    
    Args:
        orchestrator: Agent orchestrateur principal
        rag_system: Système RAG pour les agents
        log_callback: Callback function for detailed logging
        **kwargs: Arguments supplémentaires
        
    Returns:
        Dictionnaire des agents spécialisés créés
    """
    logger.info("Création des agents spécialisés")
    
    specialized_agents = {}
    
    # Get LLM client - moved here so it's available throughout
    try:
        from .integrations.llm_integration import get_llm_client
        llm_client = get_llm_client()
    except Exception as e:
        logger.error(f"Could not get LLM client: {e}")
        return specialized_agents
    
    # Create agents one by one with individual error handling
    
    # 1. Risk Assessment Agent
    try:
        from .modules.risk_assessment_module import RiskAssessmentModule
        from .agent_logger import AgentLogger
        
        risk_agent = RiskAssessmentModule(
            llm_client=llm_client,
            agent_logger=AgentLogger(callback=log_callback) if log_callback else None,
            rag_system=rag_system
        )
        specialized_agents["risk_assessment"] = risk_agent
        orchestrator.register_agent("risk_assessment", risk_agent)
        logger.info("Created RiskAssessmentModule with detailed logging")
    except Exception as e:
        logger.error(f"Could not create risk_assessment agent: {e}")
        logger.error(f"Error details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Create fallback RAG agent
        try:
            risk_agent = await create_rag_agent(
                agent_id="risk_assessment",
                name="Agent d'Évaluation des Risques",
                **kwargs
            )
            specialized_agents["risk_assessment"] = risk_agent
            orchestrator.register_agent("risk_assessment", risk_agent)
            logger.info("Created fallback RAG agent for risk_assessment")
        except Exception as fallback_e:
            logger.error(f"Could not create fallback risk_assessment agent: {fallback_e}")
    
    # 2. Document Finder Agent
    try:
        from .modules.document_finder_agent import DocumentFinderAgent
        
        document_finder_agent = DocumentFinderAgent(
            agent_id="document_finder",
            name="Agent de Recherche de Documents"
        )
        specialized_agents["document_finder"] = document_finder_agent
        orchestrator.register_agent("document_finder", document_finder_agent)
        logger.info("Created DocumentFinderAgent with RAG integration")
    except Exception as e:
        logger.error(f"Could not create document_finder agent: {e}")
        logger.error(f"Error details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Create fallback RAG agent
        try:
            document_agent = await create_rag_agent(
                agent_id="document_finder",
                name="Agent de Recherche de Documents",
                **kwargs
            )
            specialized_agents["document_finder"] = document_agent
            orchestrator.register_agent("document_finder", document_agent)
            logger.info("Created fallback RAG agent for document_finder")
        except Exception as fallback_e:
            logger.error(f"Could not create fallback document_finder agent: {fallback_e}")

    # 3. Entity Extractor Agent (NEW)
    try:
        from .tools.entity_extractor import EntityExtractor
        from .rag_agent import RAGAgent
        from .tool_registry import ToolRegistry
        from .query_parser import QueryParser
        from .integrations.rag_integration import get_rag_integration
        
        # Create entity extractor as an agent using RAG agent base with specialized tools
        tool_registry = ToolRegistry()
        rag_integration = get_rag_integration()
        query_parser = QueryParser(llm_client=llm_client)
        
        # Create entity extractor agent
        entity_agent = RAGAgent(
            agent_id="entity_extractor",
            name="Agent d'Extraction d'Entités",
            tool_registry=tool_registry,
            query_parser=query_parser,
            retrieval_system=rag_integration,
            llm_client=llm_client,
            max_sources=3
        )
        
        # Register entity extraction tools
        try:
            from .tools.entity_extractor import entity_extractor_tool
            tool_registry.register(entity_extractor_tool)
            logger.info("Registered entity_extractor_tool")
        except Exception as tool_e:
            logger.warning(f"Could not register entity extraction tool: {tool_e}")
        
        specialized_agents["entity_extractor"] = entity_agent
        orchestrator.register_agent("entity_extractor", entity_agent)
        logger.info("Created EntityExtractor agent with specialized tools")
    except Exception as e:
        logger.error(f"Could not create entity_extractor agent: {e}")
        # Create fallback RAG agent
        try:
            entity_agent = await create_rag_agent(
                agent_id="entity_extractor",
                name="Agent d'Extraction d'Entités",
                **kwargs
            )
            specialized_agents["entity_extractor"] = entity_agent
            orchestrator.register_agent("entity_extractor", entity_agent)
            logger.info("Created fallback RAG agent for entity_extractor")
        except Exception as fallback_e:
            logger.error(f"Could not create fallback entity_extractor agent: {fallback_e}")

    # 4. Compliance Analysis Agent
    try:
        from .modules.compliance_analysis_module import ComplianceAnalysisModule
        
        compliance_agent = ComplianceAnalysisModule(llm_client=llm_client, rag_system=rag_system)
        specialized_agents["compliance_analysis"] = compliance_agent
        orchestrator.register_agent("compliance_analysis", compliance_agent)
        logger.info("Created ComplianceAnalysisModule with specialized capabilities")
    except Exception as e:
        logger.error(f"Could not create compliance_analysis agent: {e}")
        logger.error(f"Error details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Create fallback RAG agent
        try:
            compliance_agent = await create_rag_agent(
                agent_id="compliance_analysis",
                name="Agent d'Analyse de Conformité",
                **kwargs
            )
            specialized_agents["compliance_analysis"] = compliance_agent
            orchestrator.register_agent("compliance_analysis", compliance_agent)
            logger.info("Created fallback RAG agent for compliance_analysis")
        except Exception as fallback_e:
            logger.error(f"Could not create fallback compliance_analysis agent: {fallback_e}")

    # 5. Governance Analysis Agent
    try:
        from .modules.governance_analysis_module import GovernanceAnalysisModule
        
        governance_agent = GovernanceAnalysisModule(llm_client=llm_client, rag_system=rag_system)
        specialized_agents["governance_analysis"] = governance_agent
        orchestrator.register_agent("governance_analysis", governance_agent)
        logger.info("Created GovernanceAnalysisModule with specialized capabilities")
    except Exception as e:
        logger.error(f"Could not create governance_analysis agent: {e}")
        logger.error(f"Error details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Create fallback RAG agent
        try:
            governance_agent = await create_rag_agent(
                agent_id="governance_analysis",
                name="Agent d'Analyse de Gouvernance",
                **kwargs
            )
            specialized_agents["governance_analysis"] = governance_agent
            orchestrator.register_agent("governance_analysis", governance_agent)
            logger.info("Created fallback RAG agent for governance_analysis")
        except Exception as fallback_e:
            logger.error(f"Could not create fallback governance_analysis agent: {fallback_e}")

    # 6. Gap Analysis Agent
    try:
        from .modules.gap_analysis_module import GapAnalysisModule
        
        gap_agent = GapAnalysisModule(llm_client=llm_client, rag_system=rag_system)
        specialized_agents["gap_analysis"] = gap_agent
        orchestrator.register_agent("gap_analysis", gap_agent)
        logger.info("Created GapAnalysisModule with specialized capabilities")
    except Exception as e:
        logger.error(f"Could not create gap_analysis agent: {e}")
        logger.error(f"Error details: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Create fallback RAG agent
        try:
            gap_agent = await create_rag_agent(
                agent_id="gap_analysis",
                name="Agent d'Analyse des Écarts",
                **kwargs
            )
            specialized_agents["gap_analysis"] = gap_agent
            orchestrator.register_agent("gap_analysis", gap_agent)
            logger.info("Created fallback RAG agent for gap_analysis")
        except Exception as fallback_e:
            logger.error(f"Could not create fallback gap_analysis agent: {fallback_e}")
    
    logger.info(f"Agents spécialisés créés avec succès: {list(specialized_agents.keys())}")
    
    # Debug: afficher l'état de l'orchestrateur
    orchestrator.debug_agent_status()
    
    return specialized_agents

async def get_agent(agent_type: str, log_callback=None, **kwargs) -> Agent:
    """
    Get an agent of the specified type.
    
    Args:
        agent_type: Type of agent to create
        log_callback: Callback function for detailed logging
        **kwargs: Additional arguments for the agent
        
    Returns:
        An initialized agent
    """
    if agent_type == "rag":
        return await create_rag_agent(**kwargs)
    elif agent_type == "orchestrator":
        return await create_orchestrator_agent(log_callback=log_callback, **kwargs)
    else:
        logger.error(f"Unsupported agent type: {agent_type}")
        raise ValueError(f"Unsupported agent type: {agent_type}")

# Agent instances cache
_agent_instances = {}

async def get_agent_instance(agent_type: str, agent_id: Optional[str] = None, log_callback=None, **kwargs) -> Agent:
    """
    Get a cached agent instance, creating it if it doesn't exist.
    
    Args:
        agent_type: Type of agent to get
        agent_id: Unique identifier for the agent (if None, a default ID will be used)
        log_callback: Callback function for detailed logging
        **kwargs: Additional arguments for creating the agent
        
    Returns:
        An agent instance
    """
    global _agent_instances
    
    # Generate a default agent ID if not provided
    if agent_id is None:
        agent_id = f"{agent_type}_default"
        
    # Create a cache key - include log_callback in key to avoid conflicts
    cache_key = f"{agent_type}_{agent_id}_{id(log_callback) if log_callback else 'no_callback'}"
    
    # Return cached instance if available
    if cache_key in _agent_instances:
        return _agent_instances[cache_key]
        
    # Create a new instance
    agent = await get_agent(agent_type, agent_id=agent_id, log_callback=log_callback, **kwargs)
    
    # Cache the instance
    _agent_instances[cache_key] = agent
    
    return agent 

async def initialize_complete_agent_system(rag_system=None, rag_query_engine=None, log_callback=None, **kwargs) -> OrchestratorAgent:
    """
    Initialise le système complet d'agents avec orchestrateur et agents spécialisés.
    
    Args:
        rag_system: Système RAG à utiliser
        rag_query_engine: Moteur de requête RAG à utiliser  
        log_callback: Callback function for detailed logging
        **kwargs: Arguments supplémentaires
        
    Returns:
        Agent orchestrateur avec tous les agents spécialisés enregistrés
    """
    logger.info("Initialisation du système complet d'agents")
    
    # Initialize RAG integration with provided systems
    if rag_system is not None or rag_query_engine is not None:
        from agent_framework.integrations.rag_integration import initialize_rag_integration
        initialize_rag_integration(rag_system=rag_system, rag_query_engine=rag_query_engine)
        logger.info("RAG integration initialized with provided systems")
    
    # Créer l'orchestrateur
    orchestrator = await create_orchestrator_agent(log_callback=log_callback, **kwargs)
    
    # Créer et enregistrer les agents spécialisés
    specialized_agents = await create_specialized_agents(
        orchestrator=orchestrator,
        rag_system=rag_system,
        log_callback=log_callback,
        **kwargs
    )
    
    logger.info(f"Système d'agents initialisé avec {len(specialized_agents)} agents spécialisés")
    
    return orchestrator 