#!/usr/bin/env python3
"""
Script de test pour l'intégration du système d'agents RegulAIte.
"""
import asyncio
import logging
import sys
import os
from pathlib import Path

# Ajouter le répertoire backend au chemin
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_llm_client():
    """Test le client LLM."""
    try:
        from agent_framework.integrations.llm_integration import get_llm_client
        
        logger.info("Test du client LLM...")
        
        # Vérifier si la clé API est configurée
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY non configurée, test LLM ignoré")
            return False
        
        llm_client = get_llm_client()
        
        # Test simple
        response = await llm_client.generate_response(
            messages=[
                {"role": "user", "content": "Dis bonjour en français"}
            ]
        )
        
        logger.info(f"Réponse LLM: {response[:100]}...")
        return True
        
    except Exception as e:
        logger.error(f"Erreur test LLM: {str(e)}")
        return False

async def test_document_finder():
    """Test le Document Finder."""
    try:
        from agent_framework.tools.document_finder import DocumentFinder, SearchCriteria
        
        logger.info("Test du Document Finder...")
        
        finder = DocumentFinder(rag_system=None)  # Sans RAG pour le test
        
        # Test de classification de document
        doc_metadata = await finder.classify_document(
            doc_id="test_doc",
            content="Politique de sécurité des systèmes d'information (PSSI) de l'entreprise Neo Financia",
            metadata={"title": "PSSI Neo Financia"}
        )
        
        logger.info(f"Document classifié: {doc_metadata.doc_type.value}, Framework: {doc_metadata.framework}")
        
        # Test de recherche simple
        results = await finder.search_documents(
            query="politique de sécurité",
            limit=5
        )
        
        logger.info(f"Résultats de recherche: {len(results)} documents trouvés")
        return True
        
    except Exception as e:
        logger.error(f"Erreur test Document Finder: {str(e)}")
        return False

async def test_orchestrator():
    """Test l'orchestrateur."""
    try:
        from agent_framework.factory import create_orchestrator_agent
        from agent_framework.agent import Query
        
        logger.info("Test de l'orchestrateur...")
        
        # Vérifier si la clé API est configurée
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY non configurée, test orchestrateur ignoré")
            return False
        
        orchestrator = await create_orchestrator_agent()
        
        # Test d'analyse de requête
        query = Query(query_text="Analyser les risques dans les nouvelles politiques IT")
        
        # Pour ce test, on va seulement tester l'analyse de la requête
        analysis = await orchestrator._analyze_request(query.query_text)
        
        logger.info(f"Analyse de requête: {analysis.get('type_analyse', 'unknown')}")
        logger.info(f"Agents requis: {[agent.get('agent_id') for agent in analysis.get('agents_requis', [])]}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur test orchestrateur: {str(e)}")
        return False

async def test_complete_system():
    """Test le système complet."""
    try:
        from agent_framework.factory import initialize_complete_agent_system
        from agent_framework.agent import Query
        
        logger.info("Test du système complet...")
        
        # Vérifier si la clé API est configurée
        if not os.getenv("OPENAI_API_KEY"):
            logger.warning("OPENAI_API_KEY non configurée, test système complet ignoré")
            return False
        
        orchestrator = await initialize_complete_agent_system()
        
        logger.info(f"Agents spécialisés enregistrés: {list(orchestrator.specialized_agents.keys())}")
        
        # Test d'une requête simple
        query = Query(query_text="Bonjour, peux-tu me présenter tes capacités ?")
        
        response = await orchestrator.process_query(query)
        
        logger.info(f"Réponse système: {response.content[:200]}...")
        logger.info(f"Outils utilisés: {response.tools_used}")
        logger.info(f"Sources: {len(response.sources) if response.sources else 0}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erreur test système complet: {str(e)}")
        return False

async def main():
    """Fonction principale de test."""
    logger.info("=== Début des tests d'intégration du système d'agents ===")
    
    tests = [
        ("Client LLM", test_llm_client),
        ("Document Finder", test_document_finder),
        ("Orchestrateur", test_orchestrator),
        ("Système complet", test_complete_system)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Test: {test_name} ---")
        try:
            success = await test_func()
            results[test_name] = success
            status = "✅ SUCCÈS" if success else "❌ ÉCHEC"
            logger.info(f"{test_name}: {status}")
        except Exception as e:
            results[test_name] = False
            logger.error(f"{test_name}: ❌ ERREUR - {str(e)}")
    
    # Résumé
    logger.info("\n=== Résumé des tests ===")
    success_count = sum(1 for success in results.values() if success)
    total_count = len(results)
    
    for test_name, success in results.items():
        status = "✅" if success else "❌"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\nRésultat global: {success_count}/{total_count} tests réussis")
    
    if success_count == total_count:
        logger.info("🎉 Tous les tests sont passés avec succès!")
        return 0
    else:
        logger.warning("⚠️ Certains tests ont échoué")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 