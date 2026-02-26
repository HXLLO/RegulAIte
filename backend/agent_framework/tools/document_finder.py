"""
Document Finder - Outil de recherche intelligente de documents GRC.
Classifie et recherche des documents selon des critères multiples.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import re
from dataclasses import dataclass
from enum import Enum

from ..integrations.llm_integration import get_llm_client

logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Types de documents GRC."""
    POLITIQUE = "politique"
    PROCEDURE = "procedure"
    INSTRUCTION = "instruction"
    AUDIT = "audit"
    EVALUATION_RISQUE = "evaluation_risque"
    RAPPORT_CONFORMITE = "rapport_conformite"
    PENTEST = "pentest"
    CARTOGRAPHIE = "cartographie"
    PLAN_ACTION = "plan_action"
    CHARTE = "charte"
    STANDARD = "standard"
    GUIDE = "guide"
    AUTRE = "autre"

@dataclass
class DocumentMetadata:
    """Métadonnées d'un document."""
    doc_id: str
    title: str
    doc_type: DocumentType
    author: Optional[str] = None
    creation_date: Optional[datetime] = None
    last_modified: Optional[datetime] = None
    version: Optional[str] = None
    framework: Optional[str] = None  # ISO27001, RGPD, DORA, etc.
    criticality: str = "normal"  # low, normal, high, critical
    tags: List[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []

@dataclass
class SearchCriteria:
    """Critères de recherche pour les documents."""
    keywords: List[str] = None
    doc_types: List[DocumentType] = None
    frameworks: List[str] = None
    date_range: Tuple[Optional[datetime], Optional[datetime]] = None
    authors: List[str] = None
    tags: List[str] = None
    criticality_min: str = "low"
    fuzzy_match: bool = True
    semantic_search: bool = True
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.doc_types is None:
            self.doc_types = []
        if self.frameworks is None:
            self.frameworks = []
        if self.authors is None:
            self.authors = []
        if self.tags is None:
            self.tags = []

class DocumentFinder:
    """
    Outil de recherche intelligente et classification de documents GRC.
    """
    
    def __init__(self, rag_system=None, use_query_expansion=False):
        """
        Initialise le Document Finder.
        
        Args:
            rag_system: Système RAG pour la recherche sémantique
            use_query_expansion: Whether to enable query expansion for enhanced search
        """
        self.rag_system = rag_system
        self.llm_client = get_llm_client()
        self.use_query_expansion = use_query_expansion
        
        # Initialize query expansion if enabled
        self.query_expander = None
        if self.use_query_expansion:
            try:
                from .query_expansion import get_query_expander
                self.query_expander = get_query_expander()
                logger.info("DocumentFinder: Query expansion initialized")
            except Exception as e:
                logger.error(f"DocumentFinder: Failed to initialize query expansion: {str(e)}")
                self.use_query_expansion = False
        
        # Cache des métadonnées de documents
        self.document_cache: Dict[str, DocumentMetadata] = {}
        
        # Patterns pour la classification automatique
        self.classification_patterns = {
            DocumentType.POLITIQUE: [
                r"politique\s+de\s+sécurité", r"pssi", r"security\s+policy",
                r"politique\s+générale", r"policy", r"politique\s+.*sécurité"
            ],
            DocumentType.PROCEDURE: [
                r"procédure", r"procedure", r"mode\s+opératoire",
                r"instruction\s+de\s+travail", r"protocole"
            ],
            DocumentType.AUDIT: [
                r"rapport\s+d.audit", r"audit\s+report", r"audit",
                r"contrôle\s+interne", r"évaluation\s+de\s+contrôle"
            ],
            DocumentType.EVALUATION_RISQUE: [
                r"analyse\s+de\s+risque", r"évaluation\s+.*risque",
                r"risk\s+assessment", r"cartographie\s+des\s+risques",
                r"appréciation\s+du\s+risque"
            ],
            DocumentType.PENTEST: [
                r"test\s+d.intrusion", r"pentest", r"penetration\s+test",
                r"test\s+de\s+pénétration", r"audit\s+technique"
            ],
            DocumentType.RAPPORT_CONFORMITE: [
                r"rapport\s+de\s+conformité", r"compliance\s+report",
                r"évaluation\s+.*conformité", r"gap\s+analysis"
            ]
        }
        
        # Frameworks reconnus
        self.framework_patterns = {
            "ISO27001": [r"iso\s?27001", r"iso/iec\s?27001"],
            "RGPD": [r"rgpd", r"gdpr", r"règlement\s+général"],
            "DORA": [r"dora", r"digital\s+operational\s+resilience"],
            "SOX": [r"sarbanes.oxley", r"sox"],
            "PCI": [r"pci.dss", r"payment\s+card"],
            "NIST": [r"nist", r"cybersecurity\s+framework"]
        }

    async def search_documents(
        self, 
        query: str, 
        criteria: SearchCriteria = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Recherche des documents selon une requête et des critères.
        
        Args:
            query: Requête de recherche
            criteria: Critères de recherche supplémentaires
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des documents trouvés avec métadonnées
        """
        if criteria is None:
            criteria = SearchCriteria()
            
        logger.info(f"Recherche de documents: {query}")
        
        # 1. Query expansion if enabled
        expanded_queries = [query]
        expansion_info = None
        
        if self.use_query_expansion and self.query_expander:
            try:
                expansion_result = await self.query_expander.expand_query(
                    query,
                    strategy="balanced",
                    max_expansions=5,
                    include_frameworks=True
                )
                
                if expansion_result.expanded_terms:
                    # Create enhanced query with expansion terms
                    enhanced_query = f"{query} {' '.join(expansion_result.expanded_terms[:3])}"
                    expanded_queries.append(enhanced_query)
                    
                    expansion_info = {
                        "expanded_terms": expansion_result.expanded_terms,
                        "framework_terms": expansion_result.framework_terms,
                        "confidence_score": expansion_result.confidence_score
                    }
                    
                    logger.info(
                        f"DocumentFinder: Query expanded with {len(expansion_result.expanded_terms)} terms, "
                        f"confidence: {expansion_result.confidence_score:.2f}"
                    )
                    
            except Exception as e:
                logger.warning(f"DocumentFinder: Query expansion failed: {str(e)}")
        
        # 2. Analyse intelligente de la requête
        analyzed_query = await self._analyze_search_query(query)
        
        # 3. Enrichir les critères avec l'analyse de la requête
        enriched_criteria = self._enrich_criteria(criteria, analyzed_query)
        
        # 4. Recherche sémantique via RAG si disponible  
        semantic_results = []
        if self.rag_system and enriched_criteria.semantic_search:
            for search_query in expanded_queries:
                query_results = await self._semantic_search(search_query, limit)
                semantic_results.extend(query_results)
            
            # Remove duplicates from semantic results
            semantic_results = self._deduplicate_results(semantic_results)
        
        # 5. Recherche par métadonnées et mots-clés
        metadata_results = await self._metadata_search(enriched_criteria, limit)
        
        # 6. Fusion et classement des résultats
        combined_results = await self._merge_and_rank_results(
            semantic_results, 
            metadata_results, 
            analyzed_query,
            limit
        )
        
        # Add expansion information to results
        if expansion_info and combined_results:
            for result in combined_results:
                if 'metadata' not in result:
                    result['metadata'] = {}
                result['metadata']['query_expansion'] = expansion_info
        
        # 7. Determine if full documents should be retrieved based on relevance and query intent
        should_retrieve_full_docs = await self._should_retrieve_full_documents(query, analyzed_query, combined_results)
        
        # 8. Enrichir avec classification automatique et récupération de documents complets
        enriched_results = []
        for result in combined_results[:limit]:
            enriched_result = await self._enrich_result_metadata(result)
            
            # Retrieve full document content if this result is highly relevant
            if should_retrieve_full_docs:
                doc_id = result.get('doc_id', result.get('entity', ''))
                score = result.get('score', result.get('final_score', 0))
                
                # Retrieve full document for high-scoring results
                if doc_id and score > 0.7:  # High relevance threshold
                    logger.info(f"Retrieving full document content for highly relevant document: {doc_id} (score: {score:.3f})")
                    full_doc = await self.retrieve_full_document_content(doc_id)
                    if full_doc:
                        # Merge the full document content with the chunk result
                        enriched_result.update({
                            'full_content': full_doc['full_content'],
                            'content_size': full_doc['content_size'],
                            'chunk_count': full_doc['chunk_count'],
                            'has_full_content': True,
                            'retrieval_type': 'full_document_with_chunk'
                        })
                        logger.info(f"Added full content ({full_doc['content_size']} chars) to result for {doc_id}")
                    else:
                        enriched_result['has_full_content'] = False
                else:
                    enriched_result['has_full_content'] = False
            else:
                enriched_result['has_full_content'] = False
            
            enriched_results.append(enriched_result)
            
        return enriched_results

    async def classify_document(
        self, 
        doc_id: str, 
        content: str = None,
        metadata: Dict[str, Any] = None
    ) -> DocumentMetadata:
        """
        Classifie automatiquement un document.
        
        Args:
            doc_id: Identifiant du document
            content: Contenu du document (optionnel)
            metadata: Métadonnées existantes (optionnel)
            
        Returns:
            Métadonnées enrichies du document
        """
        logger.info(f"Classification du document: {doc_id}")
        
        # Classification LLM si contenu disponible
        llm_classification = None
        if content:
            llm_classification = await self._llm_classify_document(content)
        
        # Classification par patterns
        pattern_classification = self._pattern_classify_document(
            content or "", 
            metadata or {}
        )
        
        # Fusion des classifications
        final_metadata = self._merge_classifications(
            doc_id,
            llm_classification,
            pattern_classification,
            metadata or {}
        )
        
        # Mise en cache
        self.document_cache[doc_id] = final_metadata
        
        return final_metadata

    async def find_related_documents(
        self, 
        doc_id: str, 
        relationship_types: List[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Trouve des documents liés à un document donné.
        
        Args:
            doc_id: Identifiant du document de référence
            relationship_types: Types de relations à chercher
            
        Returns:
            Documents liés par type de relation
        """
        if relationship_types is None:
            relationship_types = [
                "references", "supersedes", "implements", 
                "supports", "conflicts", "complements"
            ]
        
        related_docs = {rel_type: [] for rel_type in relationship_types}
        
        # Obtenir les métadonnées du document de référence
        ref_metadata = self.document_cache.get(doc_id)
        if not ref_metadata:
            logger.warning(f"Métadonnées non trouvées pour {doc_id}")
            return related_docs
        
        # Rechercher via LLM pour les relations complexes
        if self.rag_system:
            llm_relations = await self._find_llm_relationships(doc_id, ref_metadata)
            for rel_type, docs in llm_relations.items():
                if rel_type in related_docs:
                    related_docs[rel_type].extend(docs)
        
        return related_docs

    async def _analyze_search_query(self, query: str) -> Dict[str, Any]:
        """Analyse intelligente de la requête de recherche."""
        analysis_prompt = f"""
Analyse cette requête de recherche de documents GRC:

REQUÊTE: "{query}"

Extrais les éléments suivants au format JSON:
{{
    "intent": "search|classification|compliance_check|gap_analysis",
    "document_types": ["politique", "procedure", "audit", ...],
    "frameworks": ["ISO27001", "RGPD", "DORA", ...],
    "keywords": ["mot1", "mot2", ...],
    "temporal_context": "recent|historical|all",
    "scope": "specific|general|comprehensive",
    "priority_keywords": ["mot_important1", ...]
}}
"""
        
        try:
            return await self.llm_client.analyze_with_structured_output(
                prompt=analysis_prompt,
                schema={
                    "intent": "",
                    "document_types": [],
                    "frameworks": [],
                    "keywords": [],
                    "temporal_context": "",
                    "scope": "",
                    "priority_keywords": []
                },
                agent_type="document_finder"
            )
        except Exception as e:
            logger.error(f"Erreur analyse requête: {str(e)}")
            return {
                "intent": "search",
                "document_types": [],
                "frameworks": [],
                "keywords": query.split(),
                "temporal_context": "all",
                "scope": "general",
                "priority_keywords": []
            }

    def _enrich_criteria(
        self, 
        criteria: SearchCriteria, 
        analysis: Dict[str, Any]
    ) -> SearchCriteria:
        """Enrichit les critères de recherche avec l'analyse de la requête."""
        enriched = SearchCriteria(
            keywords=criteria.keywords + analysis.get("keywords", []),
            doc_types=criteria.doc_types + [
                DocumentType(dt) for dt in analysis.get("document_types", [])
                if dt in [t.value for t in DocumentType]
            ],
            frameworks=criteria.frameworks + analysis.get("frameworks", []),
            date_range=criteria.date_range,
            authors=criteria.authors,
            tags=criteria.tags + analysis.get("priority_keywords", []),
            criticality_min=criteria.criticality_min,
            fuzzy_match=criteria.fuzzy_match,
            semantic_search=criteria.semantic_search
        )
        
        # Ajuster la plage temporelle selon le contexte
        if analysis.get("temporal_context") == "recent" and not criteria.date_range:
            recent_date = datetime.now() - timedelta(days=90)
            enriched.date_range = (recent_date, None)
            
        return enriched

    async def _semantic_search(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Recherche sémantique via le système RAG."""
        try:
            if hasattr(self.rag_system, 'retrieve'):
                results = await asyncio.get_event_loop().run_in_executor(
                    None, self.rag_system.retrieve, query, limit
                )
                return results
            else:
                logger.warning("Méthode retrieve non disponible dans le système RAG")
                return []
        except Exception as e:
            logger.error(f"Erreur recherche sémantique: {str(e)}")
            return []

    async def _metadata_search(
        self, 
        criteria: SearchCriteria, 
        limit: int
    ) -> List[Dict[str, Any]]:
        """Recherche par métadonnées et mots-clés."""
        results = []
        
        # Parcourir le cache de documents
        for doc_id, metadata in self.document_cache.items():
            score = self._calculate_metadata_score(metadata, criteria)
            
            if score > 0:
                results.append({
                    "doc_id": doc_id,
                    "title": metadata.title,
                    "score": score,
                    "metadata": metadata,
                    "source": "metadata_search"
                })
        
        # Trier par score décroissant
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results[:limit]

    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on document ID and content."""
        seen = set()
        deduplicated = []
        
        for result in results:
            # Create unique identifier
            doc_id = result.get("doc_id", result.get("entity", ""))
            content_hash = hash(str(result.get("content", result.get("text", "")))[:200])
            unique_id = f"{doc_id}_{content_hash}"
            
            if unique_id not in seen:
                seen.add(unique_id)
                deduplicated.append(result)
        
        logger.debug(f"Deduplicated {len(results)} -> {len(deduplicated)} semantic results")
        return deduplicated

    def _calculate_metadata_score(
        self, 
        metadata: DocumentMetadata, 
        criteria: SearchCriteria
    ) -> float:
        """Calcule un score de pertinence pour les métadonnées."""
        score = 0.0
        
        # Score par type de document
        if not criteria.doc_types or metadata.doc_type in criteria.doc_types:
            score += 1.0
        elif criteria.doc_types:
            return 0.0  # Exclusion si type non correspondant
        
        # Score par framework
        if criteria.frameworks and metadata.framework:
            if metadata.framework in criteria.frameworks:
                score += 2.0
            else:
                score += 0.5  # Partiel si autre framework
        
        # Score par mots-clés dans le titre
        title_lower = metadata.title.lower()
        for keyword in criteria.keywords:
            if keyword.lower() in title_lower:
                score += 1.5
        
        # Score par tags
        for tag in criteria.tags:
            if tag.lower() in [t.lower() for t in metadata.tags]:
                score += 1.0
        
        # Score temporel
        if criteria.date_range:
            start_date, end_date = criteria.date_range
            doc_date = metadata.last_modified or metadata.creation_date
            
            if doc_date:
                if start_date and doc_date < start_date:
                    score *= 0.5  # Pénalité pour documents trop anciens
                elif end_date and doc_date > end_date:
                    score *= 0.5  # Pénalité pour documents trop récents
                else:
                    score += 0.5  # Bonus pour documents dans la plage
        
        return score

    async def _merge_and_rank_results(
        self,
        semantic_results: List[Dict[str, Any]],
        metadata_results: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fusionne et classe les résultats des différentes recherches."""
        
        # Normaliser les scores
        all_results = {}
        
        # Ajouter les résultats sémantiques
        for result in semantic_results:
            doc_id = result.get("doc_id", result.get("entity", ""))
            if doc_id:
                all_results[doc_id] = {
                    **result,
                    "semantic_score": result.get("score", result.get("relevance", 0.5)),
                    "metadata_score": 0.0,
                    "sources": ["semantic"]
                }
        
        # Ajouter les résultats de métadonnées
        for result in metadata_results:
            doc_id = result["doc_id"]
            if doc_id in all_results:
                all_results[doc_id]["metadata_score"] = result["score"]
                all_results[doc_id]["sources"].append("metadata")
            else:
                all_results[doc_id] = {
                    **result,
                    "semantic_score": 0.0,
                    "metadata_score": result["score"],
                    "sources": ["metadata"]
                }
        
        # Calculer un score final pondéré
        final_results = []
        for doc_id, result in all_results.items():
            # Pondération : 60% sémantique, 40% métadonnées
            final_score = (
                0.6 * result["semantic_score"] + 
                0.4 * result["metadata_score"]
            )
            
            # Bonus pour documents trouvés par plusieurs méthodes
            if len(result["sources"]) > 1:
                final_score *= 1.2
            
            result["final_score"] = final_score
            final_results.append(result)
        
        # Trier par score final
        final_results.sort(key=lambda x: x["final_score"], reverse=True)
        
        return final_results[:limit]

    async def _llm_classify_document(self, content: str) -> Dict[str, Any]:
        """Classification d'un document via LLM."""
        classification_prompt = f"""
Classe ce document GRC selon ses caractéristiques:

CONTENU (extrait):
{content[:2000]}...

Réponds au format JSON:
{{
    "document_type": "politique|procedure|audit|evaluation_risque|pentest|rapport_conformite|autre",
    "framework": "ISO27001|RGPD|DORA|SOX|PCI|NIST|autre|aucun",
    "criticality": "low|normal|high|critical",
    "tags": ["tag1", "tag2", ...],
    "confidence": 0.0-1.0,
    "reasoning": "explication de la classification"
}}
"""
        
        try:
            return await self.llm_client.analyze_with_structured_output(
                prompt=classification_prompt,
                schema={
                    "document_type": "",
                    "framework": "",
                    "criticality": "",
                    "tags": [],
                    "confidence": 0.0,
                    "reasoning": ""
                },
                agent_type="document_finder"
            )
        except Exception as e:
            logger.error(f"Erreur classification LLM: {str(e)}")
            return {}

    def _pattern_classify_document(
        self, 
        content: str, 
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Classification par patterns regex."""
        content_lower = content.lower()
        title = metadata.get("title", "").lower()
        combined_text = f"{title} {content_lower}"
        
        # Classification du type de document
        doc_type = DocumentType.AUTRE
        max_matches = 0
        
        for doc_type_enum, patterns in self.classification_patterns.items():
            matches = sum(
                len(re.findall(pattern, combined_text, re.IGNORECASE))
                for pattern in patterns
            )
            if matches > max_matches:
                max_matches = matches
                doc_type = doc_type_enum
        
        # Détection du framework
        framework = None
        for fw, patterns in self.framework_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    framework = fw
                    break
            if framework:
                break
        
        return {
            "document_type": doc_type.value,
            "framework": framework,
            "pattern_matches": max_matches,
            "confidence": min(max_matches / 3.0, 1.0)  # Normaliser la confiance
        }

    def _merge_classifications(
        self,
        doc_id: str,
        llm_result: Dict[str, Any],
        pattern_result: Dict[str, Any],
        existing_metadata: Dict[str, Any]
    ) -> DocumentMetadata:
        """Fusionne les différentes classifications."""
        
        # Utiliser la classification LLM si confiance élevée, sinon patterns
        if llm_result.get("confidence", 0) > 0.7:
            doc_type = DocumentType(llm_result.get("document_type", "autre"))
            framework = llm_result.get("framework")
            tags = llm_result.get("tags", [])
            criticality = llm_result.get("criticality", "normal")
        else:
            doc_type = DocumentType(pattern_result.get("document_type", "autre"))
            framework = pattern_result.get("framework")
            tags = []
            criticality = "normal"
        
        # Créer les métadonnées finales
        return DocumentMetadata(
            doc_id=doc_id,
            title=existing_metadata.get("title", f"Document {doc_id}"),
            doc_type=doc_type,
            author=existing_metadata.get("author"),
            creation_date=existing_metadata.get("creation_date"),
            last_modified=existing_metadata.get("last_modified"),
            version=existing_metadata.get("version"),
            framework=framework,
            criticality=criticality,
            tags=tags + existing_metadata.get("tags", []),
            file_path=existing_metadata.get("file_path"),
            file_size=existing_metadata.get("file_size")
        )

    async def _enrich_result_metadata(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Enrichit un résultat avec des métadonnées supplémentaires."""
        doc_id = result.get("doc_id", "")
        
        # Ajouter les métadonnées du cache si disponibles
        if doc_id in self.document_cache:
            metadata = self.document_cache[doc_id]
            result["enriched_metadata"] = {
                "type": metadata.doc_type.value,
                "framework": metadata.framework,
                "criticality": metadata.criticality,
                "tags": metadata.tags,
                "author": metadata.author,
                "version": metadata.version
            }
        
        return result

    async def _find_llm_relationships(
        self, 
        doc_id: str, 
        metadata: DocumentMetadata
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Trouve des relations entre documents via LLM."""
        relationship_prompt = f"""
Trouve des documents liés à ce document GRC:

DOCUMENT DE RÉFÉRENCE:
- ID: {doc_id}
- Titre: {metadata.title}
- Type: {metadata.doc_type.value}
- Framework: {metadata.framework}

Identifie les types de relations suivants:
- references: documents référencés par ce document
- implements: documents qui implémentent ce document
- supports: documents qui supportent ce document
- conflicts: documents en conflit potentiel
- supersedes: documents remplacés par ce document
- complements: documents complémentaires

Réponds au format JSON avec les IDs des documents liés.
"""
        
        try:
            return await self.llm_client.analyze_with_structured_output(
                prompt=relationship_prompt,
                schema={
                    "references": [],
                    "implements": [],
                    "supports": [],
                    "conflicts": [],
                    "supersedes": [],
                    "complements": []
                },
                agent_type="cross_reference"
            )
        except Exception as e:
            logger.error(f"Erreur recherche relations LLM: {str(e)}")
            return {rel: [] for rel in ["references", "implements", "supports", 
                                      "conflicts", "supersedes", "complements"]}

    async def retrieve_full_document_content(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the full content of a document by fetching all its chunks.
        
        Args:
            doc_id: Document ID to retrieve full content for
            
        Returns:
            Dictionary with full document content and metadata, or None if not found
        """
        try:
            if not self.rag_system or not hasattr(self.rag_system, 'qdrant_client'):
                logger.warning("RAG system or Qdrant client not available for full document retrieval")
                return None
            
            logger.info(f"Retrieving full content for document: {doc_id}")
            
            # Search for all chunks of this document in Qdrant
            import qdrant_client.models as qdrant_models
            
            # Get all chunks for this document
            chunks_response = self.rag_system.qdrant_client.scroll(
                collection_name=self.rag_system.collection_name,
                scroll_filter=qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="doc_id",
                            match=qdrant_models.MatchValue(value=doc_id)
                        ),
                        # Only get regular chunks, not questions
                        qdrant_models.FieldCondition(
                            key="is_question",
                            match=qdrant_models.MatchValue(value=False)
                        )
                    ]
                ),
                limit=10000,  # Large limit to get all chunks
                with_payload=True,
                with_vectors=False
            )
            
            if not chunks_response or not chunks_response[0]:
                logger.warning(f"No chunks found for document: {doc_id}")
                return None
            
            chunks = chunks_response[0]
            logger.info(f"Found {len(chunks)} chunks for document {doc_id}")
            
            # Sort chunks by their index to maintain order
            sorted_chunks = sorted(chunks, key=lambda x: x.payload.get('chunk_index', 0))
            
            # Reconstruct full document content
            full_text_parts = []
            metadata = {}
            total_size = 0
            
            for chunk in sorted_chunks:
                payload = chunk.payload
                
                # Extract text content
                chunk_text = payload.get('text', '')
                if chunk_text:
                    full_text_parts.append(chunk_text)
                    total_size += len(chunk_text)
                
                # Collect metadata from the first chunk (should be consistent across chunks)
                if not metadata:
                    metadata.update(payload.get('metadata', {}))
            
            # Get document metadata from metadata collection
            doc_metadata = await self._get_document_metadata(doc_id)
            if doc_metadata:
                metadata.update(doc_metadata)
            
            # Reconstruct full document
            full_content = "\n\n".join(full_text_parts)
            
            result = {
                'doc_id': doc_id,
                'title': metadata.get('title', metadata.get('filename', f'Document {doc_id[:8]}')),
                'filename': metadata.get('filename', metadata.get('original_filename', '')),
                'full_content': full_content,
                'content': full_content,  # For compatibility
                'text': full_content,     # For compatibility
                'chunk_count': len(sorted_chunks),
                'content_size': total_size,
                'metadata': metadata,
                'file_type': metadata.get('file_type', ''),
                'author': metadata.get('author', ''),
                'created_at': metadata.get('created_at', ''),
                'language': metadata.get('language', 'en'),
                'category': metadata.get('category', 'Uncategorized'),
                'retrieval_type': 'full_document'
            }
            
            logger.info(f"Successfully retrieved full document: {doc_id} ({total_size} characters from {len(sorted_chunks)} chunks)")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving full document content for {doc_id}: {str(e)}")
            return None
    
    async def _get_document_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Get document metadata from the metadata collection.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document metadata dictionary or None if not found
        """
        try:
            if not hasattr(self.rag_system, 'metadata_collection_name'):
                return None
            
            import qdrant_client.models as qdrant_models
            
            metadata_response = self.rag_system.qdrant_client.scroll(
                collection_name=self.rag_system.metadata_collection_name,
                scroll_filter=qdrant_models.Filter(
                    must=[
                        qdrant_models.FieldCondition(
                            key="doc_id",
                            match=qdrant_models.MatchValue(value=doc_id)
                        )
                    ]
                ),
                limit=1,
                with_payload=True,
                with_vectors=False
            )
            
            if metadata_response and metadata_response[0]:
                return metadata_response[0][0].payload
            
            return None
            
        except Exception as e:
            logger.warning(f"Error getting metadata for document {doc_id}: {str(e)}")
            return None

    async def _should_retrieve_full_documents(
        self, 
        query: str, 
        analyzed_query: Dict[str, Any], 
        results: List[Dict[str, Any]]
    ) -> bool:
        """
        Determine if full documents should be retrieved based on query characteristics and results.
        
        Args:
            query: Original search query
            analyzed_query: Analyzed query with intent and characteristics
            results: Search results
            
        Returns:
            True if full documents should be retrieved for highly relevant results
        """
        try:
            # Don't retrieve full docs if no results
            if not results:
                return False
            
            # Query intent analysis
            intent = analyzed_query.get('intent', 'search')
            scope = analyzed_query.get('scope', 'general')
            
            # Check for high-intent indicators
            high_intent_indicators = [
                'compliance_check', 'gap_analysis', 'comprehensive'
            ]
            
            # Check for specific document requests
            specific_doc_keywords = [
                'document complet', 'texte intégral', 'full document', 'entire document',
                'document entier', 'contenu complet', 'version complète', 'politique complète',
                'procédure complète', 'audit complet', 'rapport complet'
            ]
            
            query_lower = query.lower()
            
            # Retrieve full docs if:
            # 1. Explicit request for full/complete documents
            if any(keyword in query_lower for keyword in specific_doc_keywords):
                logger.info("Full document retrieval triggered by explicit request")
                return True
            
            # 2. High-intent analysis tasks
            if intent in high_intent_indicators or scope == 'comprehensive':
                logger.info(f"Full document retrieval triggered by intent: {intent}, scope: {scope}")
                return True
            
            # 3. Few but highly relevant results (suggests specific document need)
            if len(results) <= 3:
                high_score_results = [r for r in results if r.get('score', r.get('final_score', 0)) > 0.8]
                if high_score_results:
                    logger.info(f"Full document retrieval triggered by {len(high_score_results)} high-scoring results with limited total results")
                    return True
            
            # 4. Multiple results from same document with high scores (user likely needs the full document)
            doc_scores = {}
            for result in results:
                doc_id = result.get('doc_id', result.get('entity', ''))
                score = result.get('score', result.get('final_score', 0))
                if doc_id:
                    if doc_id not in doc_scores:
                        doc_scores[doc_id] = []
                    doc_scores[doc_id].append(score)
            
            for doc_id, scores in doc_scores.items():
                if len(scores) >= 2 and max(scores) > 0.75:  # Multiple chunks from same doc with high score
                    logger.info(f"Full document retrieval triggered by multiple high-scoring chunks from document: {doc_id}")
                    return True
            
            # 5. Query contains framework-specific terms (often need full context)
            framework_keywords = [
                'iso27001', 'iso 27001', 'rgpd', 'gdpr', 'dora', 'sox', 'pci', 'nist',
                'conformité', 'compliance', 'audit', 'contrôle', 'mesure de sécurité'
            ]
            
            if any(keyword in query_lower for keyword in framework_keywords):
                avg_score = sum(r.get('score', r.get('final_score', 0)) for r in results) / len(results)
                if avg_score > 0.6:  # Good average relevance with framework context
                    logger.info("Full document retrieval triggered by framework context with good relevance")
                    return True
            
            # Default: don't retrieve full documents
            logger.debug("Full document retrieval not triggered - returning chunks only")
            return False
            
        except Exception as e:
            logger.error(f"Error determining if full documents should be retrieved: {str(e)}")
            return False


# Fonction outil pour l'utilisation par les agents
async def document_finder_tool(
    query: str,
    doc_types: List[str] = None,
    frameworks: List[str] = None,
    limit: int = 10,
    **kwargs
) -> Dict[str, Any]:
    """
    Outil de recherche de documents pour les agents.
    
    Args:
        query: Requête de recherche
        doc_types: Types de documents à chercher
        frameworks: Frameworks concernés
        limit: Nombre maximum de résultats
        
    Returns:
        Résultats de recherche formatés
    """
    try:
        # Récupérer le système RAG depuis l'importation globale
        rag_system = None
        try:
            import sys
            if 'main' in sys.modules:
                from main import rag_system as global_rag_system
                rag_system = global_rag_system
        except ImportError:
            logger.warning("Impossible d'importer le système RAG global")
        
        finder = DocumentFinder(rag_system=rag_system)
        
        # Construire les critères de recherche
        criteria = SearchCriteria(
            doc_types=[DocumentType(dt) for dt in (doc_types or []) 
                      if dt in [t.value for t in DocumentType]],
            frameworks=frameworks or [],
            fuzzy_match=True,
            semantic_search=True
        )
        
        # Effectuer la recherche
        results = await finder.search_documents(
            query=query,
            criteria=criteria,
            limit=limit
        )
        
        return {
            "status": "success",
            "query": query,
            "total_results": len(results),
            "documents": results,
            "search_criteria": {
                "doc_types": doc_types,
                "frameworks": frameworks,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Erreur dans document_finder_tool: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "query": query,
            "documents": []
        }

# Fonction d'initialisation du Document Finder global
_global_document_finder = None

def get_document_finder(rag_system=None, use_query_expansion=False):
    """Récupère l'instance globale du Document Finder."""
    global _global_document_finder
    
    if _global_document_finder is None:
        _global_document_finder = DocumentFinder(
            rag_system=rag_system,
            use_query_expansion=use_query_expansion
        )
    
    return _global_document_finder 