"""
Document Finder Agent - Agent spécialisé dans la recherche et classification de documents GRC.
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from ..agent import Agent, Query, AgentResponse
from ..tools.document_finder import DocumentFinder, SearchCriteria, DocumentType
from ..integrations.rag_integration import get_rag_integration
from ..integrations.llm_integration import get_llm_client

logger = logging.getLogger(__name__)

class DocumentFinderAgent(Agent):
    """
    Agent spécialisé dans la recherche et la classification de documents GRC.
    
    Fonctionnalités:
    - Recherche intelligente de documents par mots-clés, type, framework
    - Classification automatique de documents
    - Recherche sémantique via RAG
    - Analyse des relations entre documents
    """
    
    def __init__(self, agent_id: str = "document_finder", name: str = "Agent de Recherche de Documents"):
        """
        Initialise l'agent de recherche de documents.
        
        Args:
            agent_id: Identifiant unique de l'agent
            name: Nom humain de l'agent
        """
        super().__init__(agent_id=agent_id, name=name)
        
        # Initialiser le système RAG
        self.rag_integration = get_rag_integration()
        self.llm_client = get_llm_client()
        
        # Initialiser le Document Finder avec RAG
        self.document_finder = DocumentFinder(rag_system=self.rag_integration.rag_system)
        
        logger.info(f"DocumentFinderAgent initialisé: {name}")
    
    async def process_query(self, query: Query) -> AgentResponse:
        """
        Traite une requête de recherche de documents.
        
        Args:
            query: Requête utilisateur
            
        Returns:
            Réponse avec les documents trouvés et informations associées
        """
        try:
            logger.info(f"DocumentFinderAgent traite: {query.query_text}")
            
            # Analyser la requête pour extraire les critères de recherche
            search_analysis = await self._analyze_query_for_search(query.query_text)
            
            # Construire les critères de recherche
            criteria = self._build_search_criteria(search_analysis)
            
            # Effectuer la recherche
            search_results = await self.document_finder.search_documents(
                query=query.query_text,
                criteria=criteria,
                limit=search_analysis.get('limit', 10)
            )
            
            # Classifier les nouveaux documents si nécessaire
            if search_analysis.get('classify_results', False):
                for result in search_results:
                    if 'classification' not in result:
                        doc_id = result.get('doc_id', '')
                        content = result.get('content', '')
                        if doc_id and content:
                            classification = await self.document_finder.classify_document(
                                doc_id=doc_id,
                                content=content
                            )
                            result['classification'] = {
                                'type': classification.doc_type.value,
                                'framework': classification.framework,
                                'criticality': classification.criticality,
                                'tags': classification.tags
                            }
            
            # Générer la réponse structurée
            response_content = await self._format_search_response(
                query.query_text, 
                search_results, 
                search_analysis
            )
            
            # Extraire les sources des résultats
            sources = []
            for result in search_results:
                source = {
                    'doc_id': result.get('doc_id', ''),
                    'title': result.get('title', 'Document sans titre'),
                    'relevance_score': result.get('score', 0.0),
                    'document_type': result.get('enriched_metadata', {}).get('type', 'unknown'),
                    'framework': result.get('enriched_metadata', {}).get('framework'),
                    'file_path': result.get('file_path')
                }
                sources.append(source)
            
            return AgentResponse(
                content=response_content,
                sources=sources,
                confidence=min(len(search_results) / 10.0, 1.0),  # Confidence basée sur le nombre de résultats
                metadata={
                    'search_criteria': search_analysis,
                    'total_documents_found': len(search_results),
                    'search_type': 'document_finder',
                    'agent_type': 'document_finder'
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur dans DocumentFinderAgent: {str(e)}")
            return AgentResponse(
                content=f"Erreur lors de la recherche de documents: {str(e)}",
                sources=[],
                confidence=0.0,
                metadata={
                    'error': str(e),
                    'agent_type': 'document_finder'
                }
            )
    
    async def _analyze_query_for_search(self, query_text: str) -> Dict[str, Any]:
        """
        Analyse la requête pour extraire les critères de recherche implicites.
        
        Args:
            query_text: Texte de la requête
            
        Returns:
            Dictionnaire avec les critères extraits
        """
        analysis_prompt = f"""
Analyse cette requête de recherche de documents GRC et extrait les critères:

REQUÊTE: {query_text}

Identifie:
- keywords: mots-clés principaux
- doc_types: types de documents mentionnés (politique, procédure, audit, etc.)
- frameworks: frameworks cités (ISO27001, RGPD, DORA, etc.)
- time_range: période mentionnée (récent, 2023, etc.)
- search_intent: intention (chercher, lister, classifier, analyser)
- limit: nombre de résultats souhaités (défaut: 10)
- classify_results: si la classification est demandée (true/false)

Réponds en JSON avec ces champs.
"""
        
        try:
            response = await self.llm_client.generate_response(
                messages=[{'role': 'user', 'content': analysis_prompt}],
                model='gpt-4o-mini',
                temperature=0.1
            )
            
            # Essayer de parser la réponse JSON
            import json
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # Fallback si le JSON n'est pas valide
                return {
                    'keywords': query_text.split(),
                    'doc_types': [],
                    'frameworks': [],
                    'search_intent': 'chercher',
                    'limit': 10,
                    'classify_results': False
                }
                
        except Exception as e:
            logger.error(f"Erreur analyse requête: {str(e)}")
            return {
                'keywords': query_text.split(),
                'doc_types': [],
                'frameworks': [],
                'search_intent': 'chercher',
                'limit': 10,
                'classify_results': False
            }
    
    def _build_search_criteria(self, analysis: Dict[str, Any]) -> SearchCriteria:
        """
        Construit les critères de recherche à partir de l'analyse.
        
        Args:
            analysis: Résultat de l'analyse de la requête
            
        Returns:
            Critères de recherche structurés
        """
        # Convertir les types de documents
        doc_types = []
        for doc_type_str in analysis.get('doc_types', []):
            # S'assurer que doc_type_str est une chaîne
            if isinstance(doc_type_str, list):
                # Si c'est une liste, prendre le premier élément
                if doc_type_str:
                    doc_type_str = str(doc_type_str[0])
                else:
                    continue
            elif not isinstance(doc_type_str, str):
                doc_type_str = str(doc_type_str)
            
            try:
                doc_type = DocumentType(doc_type_str.lower())
                doc_types.append(doc_type)
            except ValueError:
                # Essayer de mapper des synonymes
                type_mapping = {
                    'policy': DocumentType.POLITIQUE,
                    'procedure': DocumentType.PROCEDURE,
                    'audit': DocumentType.AUDIT,
                    'risk': DocumentType.EVALUATION_RISQUE,
                    'compliance': DocumentType.RAPPORT_CONFORMITE,
                    'pentest': DocumentType.PENTEST
                }
                if doc_type_str.lower() in type_mapping:
                    doc_types.append(type_mapping[doc_type_str.lower()])
        
        # Gestion de la période temporelle
        date_range = (None, None)
        time_range = analysis.get('time_range')
        if time_range:
            # Convert time_range to string if it's a list or other type
            if isinstance(time_range, list):
                time_range_str = ' '.join(str(item) for item in time_range)
            else:
                time_range_str = str(time_range)
            
            time_range_lower = time_range_str.lower()
            if 'récent' in time_range_lower or 'recent' in time_range_lower:
                # Documents des 6 derniers mois
                from datetime import timedelta
                date_range = (datetime.now() - timedelta(days=180), None)
            elif any(year in time_range_str for year in ['2023', '2024']):
                # Année spécifique
                year = next(year for year in ['2023', '2024'] if year in time_range_str)
                date_range = (datetime(int(year), 1, 1), datetime(int(year), 12, 31))
        
        return SearchCriteria(
            keywords=analysis.get('keywords', []),
            doc_types=doc_types,
            frameworks=analysis.get('frameworks', []),
            date_range=date_range,
            fuzzy_match=True,
            semantic_search=True
        )
    
    async def _format_search_response(
        self, 
        query: str, 
        results: List[Dict[str, Any]], 
        analysis: Dict[str, Any]
    ) -> str:
        """
        Formate la réponse de recherche de façon structurée.
        
        Args:
            query: Requête originale
            results: Résultats de la recherche
            analysis: Analyse de la requête
            
        Returns:
            Réponse formatée
        """
        if not results:
            return f"""## Recherche de Documents : Aucun résultat

**Requête :** {query}

Aucun document n'a été trouvé correspondant aux critères de recherche.

**Critères utilisés :**
- Mots-clés : {', '.join(analysis.get('keywords', []))}
- Types : {', '.join(analysis.get('doc_types', []))}
- Frameworks : {', '.join(analysis.get('frameworks', []))}

**Suggestions :**
- Vérifiez l'orthographe des mots-clés
- Utilisez des termes plus généraux
- Supprimez certains filtres pour élargir la recherche"""

        response = f"""## Recherche de Documents : {len(results)} résultat(s) trouvé(s)

**Requête :** {query}

"""
        
        # Count full documents vs chunks
        full_docs_count = sum(1 for r in results if r.get('has_full_content', False))
        if full_docs_count > 0:
            response += f"*Note: {full_docs_count} document(s) complet(s) récupéré(s) pour cette recherche.*\n\n"
        
        for i, result in enumerate(results[:10], 1):  # Limiter à 10 résultats dans la réponse
            title = result.get('title', 'Document sans titre')
            doc_type = result.get('enriched_metadata', {}).get('type', 'Non classifié')
            framework = result.get('enriched_metadata', {}).get('framework', 'N/A')
            score = result.get('score', 0.0)
            doc_id = result.get('doc_id', '')
            has_full_content = result.get('has_full_content', False)
            
            response += f"""### {i}. {title}

- **Type :** {doc_type}
- **Framework :** {framework}
- **Score de pertinence :** {score:.2f}
- **ID :** {doc_id}"""
            
            # Indicate if full document content is available
            if has_full_content:
                content_size = result.get('content_size', 0)
                chunk_count = result.get('chunk_count', 0)
                response += f"""
- **Contenu complet disponible :** Oui ({content_size:,} caractères, {chunk_count} sections)"""
            
            response += "\n\n"
            
            # Show content based on availability
            if has_full_content:
                # Show a longer excerpt from full content since we have it
                full_content = result.get('full_content', '')
                if full_content:
                    # Show first 500 characters of full document
                    content_preview = full_content[:500]
                    response += f"**Aperçu du document complet :** {content_preview}...\n\n"
                    
                    # Add a note about full content availability
                    response += "*[Document complet récupéré et disponible pour analyse approfondie]*\n\n"
            else:
                # Show regular chunk excerpt
                content_excerpt = result.get('content', '')[:200]
                if content_excerpt:
                    response += f"**Extrait :** {content_excerpt}...\n\n"
        
        # Ajouter un résumé des critères utilisés
        response += f"""---

**Critères de recherche utilisés :**
- **Mots-clés :** {', '.join(analysis.get('keywords', []))}
- **Types de documents :** {', '.join(analysis.get('doc_types', [])) or 'Tous'}
- **Frameworks :** {', '.join(analysis.get('frameworks', [])) or 'Tous'}
- **Intention :** {analysis.get('search_intent', 'recherche')}

**Total :** {len(results)} document(s) trouvé(s)"""

        return response
    
    def get_capabilities(self) -> List[str]:
        """
        Retourne la liste des capacités de l'agent.
        
        Returns:
            Liste des capacités
        """
        return [
            "Recherche intelligente de documents",
            "Récupération automatique de documents complets pour les résultats très pertinents",
            "Classification automatique de documents", 
            "Recherche sémantique via RAG",
            "Filtrage par type de document",
            "Filtrage par framework (ISO27001, RGPD, DORA, etc.)",
            "Analyse des relations entre documents",
            "Recherche par mots-clés et métadonnées",
            "Scoring de pertinence",
            "Reconstruction de documents à partir de chunks stockés"
        ] 