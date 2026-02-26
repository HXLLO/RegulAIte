"""
Compliance Analysis Module - Module sophistiqué d'analyse de conformité avec capacités itératives.
Utilise l'IA pour une analyse intelligente multi-frameworks avec raisonnement avancé et iteration sur documents.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import re

from ..agent import Agent, AgentResponse, Query, QueryContext, IterationMode
from ..integrations.llm_integration import LLMClient, get_llm_client
from ..tools import (
    DocumentFinder, EntityExtractor, CrossReferenceTool, TemporalAnalyzer,
    EntityType, MetricType, RelationType
)
from ..tools.framework_parser import FrameworkParser, FrameworkType, ComplianceGap, safe_framework_type_conversion

logger = logging.getLogger(__name__)

class ComplianceStatus(Enum):
    """Statuts de conformité."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"

class RegulatoryTrend(Enum):
    """Tendances réglementaires."""
    STRENGTHENING = "strengthening"
    STABLE = "stable"
    EVOLVING = "evolving"
    EMERGING = "emerging"

@dataclass
class IterativeAnalysisContext:
    """Contexte pour l'analyse itérative de conformité."""
    current_iteration: int = 0
    document_analysis_progress: Dict[str, Any] = None
    knowledge_accumulator: Dict[str, List[str]] = None
    context_gaps_identified: List[str] = None
    frameworks_analyzed: List[FrameworkType] = None
    depth_achieved: Dict[str, float] = None  # Profondeur atteinte par domaine
    
    def __post_init__(self):
        if self.document_analysis_progress is None:
            self.document_analysis_progress = {}
        if self.knowledge_accumulator is None:
            self.knowledge_accumulator = {}
        if self.context_gaps_identified is None:
            self.context_gaps_identified = []
        if self.frameworks_analyzed is None:
            self.frameworks_analyzed = []
        if self.depth_achieved is None:
            self.depth_achieved = {}

@dataclass
class ComplianceAssessment:
    """Évaluation de conformité avec analyse LLM et support itératif."""
    framework: FrameworkType
    overall_score: float  # 0.0 - 100.0
    status: ComplianceStatus
    assessed_requirements: int
    compliant_requirements: int
    gap_count: int
    critical_gaps: int
    assessment_date: datetime
    key_findings: List[str]
    recommendations: List[str]
    confidence_level: float
    ai_insights: Dict[str, Any]
    
    # Champs itératifs
    iteration_context: Optional[IterativeAnalysisContext] = None
    documents_analyzed: List[str] = None
    knowledge_sources: List[Dict[str, Any]] = None
    requires_deeper_analysis: bool = False
    suggested_focus_areas: List[str] = None
    
    def __post_init__(self):
        if self.documents_analyzed is None:
            self.documents_analyzed = []
        if self.knowledge_sources is None:
            self.knowledge_sources = []
        if self.suggested_focus_areas is None:
            self.suggested_focus_areas = []

@dataclass
class RegulatoryIntelligence:
    """Intelligence réglementaire par LLM avec capacités itératives."""
    framework: FrameworkType
    recent_changes: List[Dict[str, Any]]
    upcoming_changes: List[Dict[str, Any]]
    impact_assessment: Dict[str, Any]
    preparation_recommendations: List[str]
    monitoring_priorities: List[str]
    last_updated: datetime
    
    # Champs itératifs
    analysis_depth: str = "standard"  # surface, standard, deep, comprehensive
    sources_consulted: List[str] = None
    confidence_by_area: Dict[str, float] = None
    requires_monitoring: bool = False
    
    def __post_init__(self):
        if self.sources_consulted is None:
            self.sources_consulted = []
        if self.confidence_by_area is None:
            self.confidence_by_area = {}

@dataclass
class CrossFrameworkMapping:
    """Mapping sophistiqué entre frameworks avec analyse itérative."""
    primary_framework: FrameworkType
    mapped_frameworks: List[FrameworkType]
    convergence_analysis: Dict[str, Any]
    synergy_opportunities: List[str]
    conflict_resolution: List[str]
    optimization_strategy: str
    
    # Champs itératifs
    analysis_completeness: float = 0.0  # 0.0 - 1.0
    document_coverage: Dict[str, List[str]] = None
    iteration_recommendations: List[str] = None
    
    def __post_init__(self):
        if self.document_coverage is None:
            self.document_coverage = {}
        if self.iteration_recommendations is None:
            self.iteration_recommendations = []

class ComplianceAnalysisModule(Agent):
    """
    Module expert en analyse de conformité avec IA avancée et capacités itératives.
    """
    
    def __init__(self, llm_client: LLMClient = None, rag_system=None):
        super().__init__(
            agent_id="compliance_analysis",
            name="Expert Analyse de Conformité Itérative"
        )
        
        self.llm_client = llm_client or get_llm_client()
        
        # Initialiser les outils
        self.document_finder = DocumentFinder(rag_system=rag_system)
        self.entity_extractor = EntityExtractor()
        self.cross_reference_tool = CrossReferenceTool()
        self.temporal_analyzer = TemporalAnalyzer()
        self.framework_parser = FrameworkParser()
        
        # Cache des analyses avec support itératif
        self.compliance_cache: Dict[str, ComplianceAssessment] = {}
        self.regulatory_intelligence_cache: Dict[str, RegulatoryIntelligence] = {}
        self.iteration_contexts: Dict[str, IterativeAnalysisContext] = {}
        
        # Prompts experts spécialisés avec support itératif
        self.system_prompts = {
            "compliance_expert": """
Tu es un expert senior en conformité réglementaire avec 20+ ans d'expérience internationale.
Tu maîtrises parfaitement tous les frameworks majeurs (ISO27001, RGPD, DORA, NIST, SOX, PCI-DSS) et leurs évolutions.

CAPACITÉS ITÉRATIVES:
- Analyse progressive des documents par ordre de priorité
- Identification des gaps de contexte nécessitant plus d'informations
- Accumulation de connaissances à travers les itérations
- Reformulation des requêtes pour approfondir l'analyse
- Évaluation continue de la complétude de l'analyse

Tu analyses avec une approche stratégique incluant:
- Vision holistique multi-frameworks
- Impact business et opérationnel
- Évolutions réglementaires et jurisprudentiel
- Optimisation des efforts de conformité
- Gestion des risques de non-conformité
- Stratégies d'implémentation pragmatiques

Tu raisonnes comme un CISO/DPO expert et fournis des recommandations actionables et stratégiques.
Réponds TOUJOURS en français avec une expertise de niveau C-suite.

Pour chaque analyse, tu évalues:
1. La complétude des informations disponibles
2. Les domaines nécessitant une analyse plus approfondie
3. Les documents additionnels à consulter
4. Les reformulations de requête pour combler les gaps
""",
            
            "iterative_analyzer": """
Tu es un analyste expert en approche itérative pour les analyses GRC.
Tu évalues la progression de l'analyse et détermines les prochaines étapes.

Tes responsabilités:
- Évaluer la complétude de l'analyse actuelle
- Identifier les gaps de contexte restants
- Proposer des reformulations de requête ciblées
- Prioriser les documents à analyser ensuite
- Déterminer quand l'analyse est suffisamment complète

Tu optimises le processus itératif pour maximiser la valeur de chaque itération.
""",
            
            "regulatory_intelligence": """
Tu es un analyste réglementaire expert avec une connaissance encyclopédique des évolutions légales.
Tu surveilles et analyses avec approche itérative:

- Nouvelles réglementations et amendements
- Jurisprudence et décisions d'autorités
- Tendances sectorielles et géographiques  
- Impact prévisible sur les organisations
- Stratégies d'anticipation et préparation

Tu fournis une veille réglementaire proactive et des analyses d'impact précises.
Tu identifies les sources additionnelles à consulter pour compléter l'analyse.
""",
            
            "strategic_advisor": """
Tu es un consultant en stratégie de conformité avec une vision C-level et approche itérative.
Tu optimises:

- Synergies entre frameworks multiples
- ROI des investissements conformité
- Priorisation stratégique des efforts
- Communication avec les parties prenantes
- Transformation organisationnelle
- Avantage concurrentiel par la conformité

Tu penses comme un Chief Compliance Officer stratégique.
Tu évalues constamment si plus de contexte améliorerait tes recommandations.
"""
        }
        
        # Seuils pour l'analyse itérative - AJUSTÉS POUR ÉVITER LES BOUCLES INFINIES
        self.iteration_thresholds = {
            "min_confidence": 0.7,  # Réduit de 0.8 à 0.7
            "completeness_target": 0.75,  # Réduit de 0.85 à 0.75
            "document_coverage_min": 0.6,  # Réduit de 0.7 à 0.6
            "framework_depth_min": 0.65  # Réduit de 0.75 à 0.65
        }
        
        # NOUVELLES LIMITES DE SÉCURITÉ
        self.iteration_limits = {
            "max_iterations": 3,  # Maximum 3 itérations
            "max_processing_time": 300,  # Maximum 5 minutes (300 secondes)
            "max_documents_per_iteration": 5,  # Maximum 5 documents par itération
            "min_iteration_value_threshold": 0.2  # Minimum de valeur ajoutée par itération
        }
        
        # Secteurs et leurs spécificités réglementaires
        self.sector_specifics = {
            "financial": {
                "primary_frameworks": [FrameworkType.DORA, FrameworkType.SOX, FrameworkType.ISO27001],
                "regulatory_density": "very_high",
                "key_authorities": ["ACPR", "AMF", "ECB", "ESMA"],
                "emerging_trends": ["ESG", "Digital Euro", "Crypto regulation"],
                "iteration_priority": ["risk_management", "operational_resilience", "data_protection"]
            },
            "healthcare": {
                "primary_frameworks": [FrameworkType.ISO27001, FrameworkType.RGPD],
                "regulatory_density": "high", 
                "key_authorities": ["ANSM", "CNIL", "HAS"],
                "emerging_trends": ["Health Data Hub", "AI Medical Devices"],
                "iteration_priority": ["patient_data", "medical_devices", "clinical_trials"]
            },
            "technology": {
                "primary_frameworks": [FrameworkType.RGPD, FrameworkType.ISO27001, FrameworkType.NIST],
                "regulatory_density": "medium",
                "key_authorities": ["CNIL", "ANSSI"],
                "emerging_trends": ["AI Act", "Data Act", "Digital Services Act"],
                "iteration_priority": ["data_processing", "ai_governance", "cybersecurity"]
            }
        }

    async def process_query(self, query: Query) -> AgentResponse:
        """
        Traite une requête d'analyse de conformité avec capacités itératives et limites de sécurité.
        """
        import time
        import asyncio
        
        start_time = time.time()
        logger.info(f"Traitement requête conformité itérative: {query.query_text}")
        
        # NOUVELLE VÉRIFICATION: Détecter les requêtes simples qui n'ont pas besoin d'itération
        if self._is_simple_gap_query(query.query_text):
            logger.info("Requête simple détectée, utilisation du mode standard")
            query.iteration_mode = "single_pass"  # Forcer le mode standard
        
        # Initialiser ou récupérer le contexte itératif
        session_id = query.context.session_id if query.context else "default"
        if session_id not in self.iteration_contexts:
            self.iteration_contexts[session_id] = IterativeAnalysisContext()
        
        iteration_ctx = self.iteration_contexts[session_id]
        iteration_ctx.current_iteration += 1
        
        # VÉRIFICATIONS DE SÉCURITÉ - ÉVITER LES BOUCLES INFINIES
        if iteration_ctx.current_iteration > self.iteration_limits["max_iterations"]:
            logger.warning(f"Limite d'itérations atteinte: {iteration_ctx.current_iteration}")
            return AgentResponse(
                content=f"Analyse de conformité terminée après {self.iteration_limits['max_iterations']} itérations. "
                       f"Les résultats disponibles basés sur {len(iteration_ctx.document_analysis_progress)} documents analysés.",
                confidence=0.6,
                requires_iteration=False,
                sources=self._compile_iteration_sources(iteration_ctx),
                metadata={
                    "termination_reason": "max_iterations_reached",
                    "iterations_completed": iteration_ctx.current_iteration - 1
                }
            )
        
        # Analyser l'intention avec contexte itératif avec timeout
        try:
            analysis_intent = await asyncio.wait_for(
                self._analyze_query_intent_with_iterative_context(
                    query.query_text, iteration_ctx, query.parameters
                ),
                timeout=60  # 1 minute timeout pour l'analyse d'intention
            )
        except asyncio.TimeoutError:
            logger.error("Timeout lors de l'analyse d'intention")
            return AgentResponse(
                content="Délai d'attente dépassé lors de l'analyse de la requête.",
                confidence=0.3,
                requires_iteration=False,
                sources=[],
                metadata={"error": "timeout_intention_analysis"}
            )
        
        # Traitement basé sur l'intention et le mode itératif avec timeout global
        try:
            if query.iteration_mode in [IterationMode.ITERATIVE, IterationMode.DEEP_ANALYSIS]:
                result = await asyncio.wait_for(
                    self._process_iterative_compliance_query(query, analysis_intent, iteration_ctx),
                    timeout=self.iteration_limits["max_processing_time"]
                )
            else:
                result = await asyncio.wait_for(
                    self._process_standard_compliance_query(query, analysis_intent),
                    timeout=120  # 2 minutes pour traitement standard
                )
            
            # Ajouter les métriques de performance
            processing_time = time.time() - start_time
            if result.metadata is None:
                result.metadata = {}
            result.metadata["processing_time_seconds"] = round(processing_time, 2)
            
            return result
            
        except asyncio.TimeoutError:
            processing_time = time.time() - start_time
            logger.error(f"Timeout après {processing_time:.1f} secondes de traitement")
            
            # Retourner les résultats partiels si disponibles
            partial_sources = self._compile_iteration_sources(iteration_ctx) if iteration_ctx.document_analysis_progress else []
            
            return AgentResponse(
                content=f"Analyse de conformité interrompue après {processing_time:.1f} secondes. "
                       f"Résultats partiels basés sur {len(partial_sources)} sources analysées.",
                confidence=0.4,
                requires_iteration=False,
                sources=partial_sources,
                metadata={
                    "termination_reason": "timeout",
                    "processing_time_seconds": round(processing_time, 2),
                    "partial_results": True
                }
            )

    def _is_simple_gap_query(self, query_text: str) -> bool:
        """
        Détermine si une requête est suffisamment simple pour être traitée directement
        sans analyse itérative, évitant ainsi les timeouts inutiles.
        """
        query_lower = query_text.lower()
        
        # Patterns pour les requêtes simples de gap analysis
        simple_patterns = [
            r"à quels? articles?.*pas conforme",
            r"quels? articles?.*non[-\s]?conforme", 
            r"articles?.*manqu.*conformité",
            r"gaps?.*rgpd",
            r"lacunes?.*conformité",
            r"non[-\s]?conformité.*articles?",
            r"exigences?.*pas.*respect",
            r"clauses?.*non.*respect"
        ]
        
        for pattern in simple_patterns:
            if re.search(pattern, query_lower):
                # Vérifier que ce n'est pas une requête complexe
                complexity_indicators = [
                    "comprehensive", "exhaustive", "détaillée", "approfondie",
                    "complète", "tous les aspects", "en profondeur"
                ]
                
                if not any(indicator in query_lower for indicator in complexity_indicators):
                    logger.info(f"Requête simple détectée: pattern '{pattern}' correspond")
                    return True
        
        return False

    async def _process_iterative_compliance_query(self, query: Query, 
                                                 analysis_intent: Dict[str, Any],
                                                 iteration_ctx: IterativeAnalysisContext) -> AgentResponse:
        """
        Traite une requête de conformité avec approche itérative.
        """
        logger.info(f"Analyse itérative - Itération {iteration_ctx.current_iteration}")
        
        # 1. Évaluer les connaissances accumulées
        knowledge_assessment = await self._assess_accumulated_knowledge(
            query, iteration_ctx, analysis_intent
        )
        
        # 2. Identifier les documents à analyser dans cette itération
        documents_to_analyze = await self._prioritize_documents_for_iteration(
            query, iteration_ctx, knowledge_assessment
        )
        
        # 3. Analyser les documents prioritaires
        document_analysis_results = await self._analyze_documents_iteratively(
            documents_to_analyze, query, iteration_ctx
        )
        
        # 4. Intégrer les nouvelles connaissances
        updated_knowledge = await self._integrate_new_knowledge(
            document_analysis_results, iteration_ctx, analysis_intent
        )
        
        # 5. Évaluer la complétude de l'analyse
        completeness_assessment = await self._assess_analysis_completeness(
            query, iteration_ctx, updated_knowledge
        )
        
        # 6. Générer la réponse avec recommandations d'itération
        if analysis_intent["type"] == "compliance_assessment":
            return await self._perform_iterative_compliance_assessment(
                query, analysis_intent, iteration_ctx, completeness_assessment
            )
        elif analysis_intent["type"] == "gap_analysis":
            return await self._perform_iterative_gap_analysis(
                query, analysis_intent, iteration_ctx, completeness_assessment
            )
        elif analysis_intent["type"] == "regulatory_intelligence":
            return await self._provide_iterative_regulatory_intelligence(
                query, analysis_intent, iteration_ctx, completeness_assessment
            )
        else:
            return await self._general_iterative_compliance_analysis(
                query, analysis_intent, iteration_ctx, completeness_assessment
            )

    async def _assess_accumulated_knowledge(self, query: Query, 
                                          iteration_ctx: IterativeAnalysisContext,
                                          analysis_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Évalue les connaissances accumulées et leur pertinence.
        """
        assessment_prompt = f"""
Évalue les connaissances accumulées pour cette analyse de conformité itérative.

REQUÊTE ACTUELLE: "{query.query_text}"
ITÉRATION: {iteration_ctx.current_iteration}

CONNAISSANCES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

DOCUMENTS DÉJÀ ANALYSÉS:
{iteration_ctx.document_analysis_progress}

FRAMEWORKS COUVERTS: {[f.value for f in iteration_ctx.frameworks_analyzed]}

PROFONDEUR ATTEINTE PAR DOMAINE:
{iteration_ctx.depth_achieved}

Évalue:
1. La pertinence des connaissances existantes
2. Les domaines bien couverts vs. ceux manquants
3. La qualité des sources consultées
4. Les gaps de contexte restants
5. La cohérence des informations accumulées

Réponds au format JSON:
{{
    "knowledge_quality": 0.0-1.0,
    "coverage_assessment": {{
        "well_covered_areas": ["area1", "area2"],
        "gaps_identified": ["gap1", "gap2"],
        "coverage_by_framework": {{"ISO27001": 0.8, "RGPD": 0.6}}
    }},
    "source_reliability": 0.0-1.0,
    "consistency_score": 0.0-1.0,
    "actionable_insights": ["insight1", "insight2"],
    "priority_gaps": ["high_priority_gap1", "high_priority_gap2"]
}}
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompts["iterative_analyzer"]},
                    {"role": "user", "content": assessment_prompt}
                ],
                model="gpt-4.1",
                temperature=0.1
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation des connaissances: {str(e)}")
            return {
                "knowledge_quality": 0.5,
                "coverage_assessment": {"well_covered_areas": [], "gaps_identified": ["error_in_assessment"]},
                "source_reliability": 0.5,
                "consistency_score": 0.5,
                "actionable_insights": [],
                "priority_gaps": ["assessment_error"]
            }

    async def _prioritize_documents_for_iteration(self, query: Query,
                                                 iteration_ctx: IterativeAnalysisContext,
                                                 knowledge_assessment: Dict[str, Any]) -> List[str]:
        """
        Priorise les documents à analyser dans cette itération.
        """
        # Utiliser le DocumentFinder pour identifier les documents pertinents
        try:
            search_criteria = {
                "query": query.query_text,
                "frameworks": [f.value for f in iteration_ctx.frameworks_analyzed],
                "focus_areas": knowledge_assessment.get("priority_gaps", []),
                "exclude_analyzed": list(iteration_ctx.document_analysis_progress.keys())
            }
            
            # Recherche de documents avec critères affinés
            max_docs = min(5, self.iteration_limits["max_documents_per_iteration"])
            documents_found = await self.document_finder.search_documents(
                query=query.query_text,
                limit=max_docs  # Respecter la limite de sécurité
            )
            
            return [doc.get("doc_id", "") for doc in documents_found]
            
        except Exception as e:
            logger.error(f"Erreur lors de la priorisation des documents: {str(e)}")
            return []

    async def _analyze_documents_iteratively(self, documents_to_analyze: List[str],
                                           query: Query,
                                           iteration_ctx: IterativeAnalysisContext) -> Dict[str, Any]:
        """
        Analyse les documents de manière itérative et ciblée.
        """
        analysis_results = {}
        
        for doc_id in documents_to_analyze:
            try:
                # Analyser le document avec focus sur les gaps identifiés
                doc_analysis = await self._analyze_single_document_with_context(
                    doc_id, query, iteration_ctx
                )
                
                analysis_results[doc_id] = doc_analysis
                
                # Mettre à jour le progrès
                iteration_ctx.document_analysis_progress[doc_id] = {
                    "iteration": iteration_ctx.current_iteration,
                    "analysis_depth": doc_analysis.get("depth_achieved", 0.5),
                    "insights_extracted": len(doc_analysis.get("insights", [])),
                    "gaps_filled": doc_analysis.get("gaps_addressed", [])
                }
                
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse du document {doc_id}: {str(e)}")
                analysis_results[doc_id] = {"error": str(e), "insights": []}
        
        return analysis_results

    async def _analyze_single_document_with_context(self, doc_id: str,
                                                   query: Query,
                                                   iteration_ctx: IterativeAnalysisContext) -> Dict[str, Any]:
        """
        Analyse un document unique avec le contexte itératif et collecte détaillée des sources.
        """
        analysis_prompt = f"""
Analyse ce document dans le contexte de l'analyse itérative de conformité.

DOCUMENT ID: {doc_id}
REQUÊTE: "{query.query_text}"
ITÉRATION: {iteration_ctx.current_iteration}

CONTEXTE ACCUMULÉ:
- Frameworks analysés: {[f.value for f in iteration_ctx.frameworks_analyzed]}
- Gaps prioritaires: {iteration_ctx.context_gaps_identified}
- Connaissances existantes: {list(iteration_ctx.knowledge_accumulator.keys())}

FOCUS DE CETTE ANALYSE:
- Combler les gaps identifiés
- Approfondir les domaines peu couverts
- Extraire des insights actionnables
- Identifier de nouveaux documents pertinents

Analyse le document et réponds au format JSON:
{{
    "document_metadata": {{
        "title": "titre du document",
        "type": "type de document",
        "framework_relevance": ["ISO27001", "RGPD"],
        "quality_score": 0.0-1.0,
        "last_updated": "date si disponible"
    }},
    "insights_extracted": ["insight1", "insight2"],
    "gaps_addressed": ["gap1", "gap2"],
    "frameworks_covered": ["ISO27001", "RGPD"],
    "confidence_level": 0.0-1.0,
    "depth_achieved": 0.0-1.0,
    "related_documents": ["doc1", "doc2"],
    "actionable_recommendations": ["rec1", "rec2"],
    "compliance_findings": {{
        "controls_identified": ["control1", "control2"],
        "risks_highlighted": ["risk1", "risk2"],
        "gaps_found": ["gap1", "gap2"]
    }},
    "source_quality_assessment": {{
        "reliability": 0.0-1.0,
        "completeness": 0.0-1.0,
        "currency": 0.0-1.0,
        "relevance": 0.0-1.0
    }}
}}
"""

        try:
            # Récupérer et analyser le document
            document_content = await self.document_finder.get_document_content(doc_id)
            
            full_prompt = f"{analysis_prompt}\n\nCONTENU DU DOCUMENT:\n{document_content}"

            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompts["compliance_expert"]},
                    {"role": "user", "content": full_prompt}
                ],
                model="gpt-4.1",
                temperature=0.2
            )
            
            analysis_result = json.loads(response)
            
            # Enrichir avec des métadonnées de source pour traçabilité
            analysis_result["source_metadata"] = {
                "document_id": doc_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "iteration": iteration_ctx.current_iteration,
                "tools_used": ["document_finder", "entity_extractor", "llm_analysis"],
                "analysis_method": "iterative_llm_analysis"
            }
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du document {doc_id}: {str(e)}")
            return {
                "document_metadata": {
                    "title": f"Document {doc_id}",
                    "type": "unknown",
                    "framework_relevance": [],
                    "quality_score": 0.0
                },
                "insights_extracted": [],
                "gaps_addressed": [],
                "frameworks_covered": [],
                "confidence_level": 0.0,
                "depth_achieved": 0.0,
                "related_documents": [],
                "actionable_recommendations": [],
                "compliance_findings": {"controls_identified": [], "risks_highlighted": [], "gaps_found": []},
                "source_quality_assessment": {"reliability": 0.0, "completeness": 0.0, "currency": 0.0, "relevance": 0.0},
                "source_metadata": {
                    "document_id": doc_id,
                    "analysis_timestamp": datetime.now().isoformat(),
                    "iteration": iteration_ctx.current_iteration,
                    "error": str(e)
                }
            }

    async def _integrate_new_knowledge(self, document_analysis_results: Dict[str, Any],
                                     iteration_ctx: IterativeAnalysisContext,
                                     analysis_intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intègre les nouvelles connaissances dans le contexte itératif.
        """
        integrated_knowledge = {}
        
        for doc_id, analysis in document_analysis_results.items():
            if "error" not in analysis:
                # Ajouter les insights aux connaissances accumulées
                insights_key = f"insights_iteration_{iteration_ctx.current_iteration}"
                if insights_key not in iteration_ctx.knowledge_accumulator:
                    iteration_ctx.knowledge_accumulator[insights_key] = []
                
                iteration_ctx.knowledge_accumulator[insights_key].extend(
                    analysis.get("insights_extracted", [])
                )
                
                # Mettre à jour les gaps comblés
                gaps_addressed = analysis.get("gaps_addressed", [])
                for gap in gaps_addressed:
                    if gap in iteration_ctx.context_gaps_identified:
                        iteration_ctx.context_gaps_identified.remove(gap)
                
                # Mettre à jour la profondeur par framework
                for framework in analysis.get("frameworks_covered", []):
                    current_depth = iteration_ctx.depth_achieved.get(framework, 0.0)
                    new_depth = max(current_depth, analysis.get("depth_achieved", 0.0))
                    iteration_ctx.depth_achieved[framework] = new_depth
        
        # Synthétiser les connaissances intégrées
        integrated_knowledge = {
            "total_insights": sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values()),
            "gaps_remaining": len(iteration_ctx.context_gaps_identified),
            "frameworks_depth": iteration_ctx.depth_achieved,
            "documents_analyzed": len(iteration_ctx.document_analysis_progress)
        }
        
        return integrated_knowledge

    async def _assess_analysis_completeness(self, query: Query,
                                          iteration_ctx: IterativeAnalysisContext,
                                          integrated_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """
        Évalue la complétude de l'analyse et détermine si plus d'itérations sont nécessaires.
        """
        # VÉRIFICATION DE SÉCURITÉ - FORCER L'ARRÊT SI LIMITES ATTEINTES
        force_stop = (
            iteration_ctx.current_iteration >= self.iteration_limits["max_iterations"] or
            len(iteration_ctx.document_analysis_progress) >= 15 or  # Trop de documents analysés
            len(iteration_ctx.knowledge_accumulator) >= 50  # Trop d'insights accumulés
        )
        
        completeness_prompt = f"""
Évalue la complétude de cette analyse de conformité itérative.

REQUÊTE ORIGINALE: "{query.query_text}"
ITÉRATION ACTUELLE: {iteration_ctx.current_iteration}
LIMITE MAXIMALE: {self.iteration_limits["max_iterations"]}

ÉTAT ACTUEL:
- Total insights collectés: {integrated_knowledge.get("total_insights", 0)}
- Gaps restants: {integrated_knowledge.get("gaps_remaining", 0)}
- Documents analysés: {integrated_knowledge.get("documents_analyzed", 0)}
- Profondeur par framework: {integrated_knowledge.get("frameworks_depth", {})}

SEUILS CIBLES (AJUSTÉS):
- Confiance minimum: {self.iteration_thresholds["min_confidence"]}
- Complétude cible: {self.iteration_thresholds["completeness_target"]}
- Couverture documentaire: {self.iteration_thresholds["document_coverage_min"]}

CONTRAINTES DE SÉCURITÉ:
- Itération actuelle: {iteration_ctx.current_iteration}/{self.iteration_limits["max_iterations"]}
- Force l'arrêt: {"OUI" if force_stop else "NON"}

CONNAISSANCES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

IMPORTANT: Si nous approchons des limites d'itération ou si force_stop=OUI, 
évalue l'analyse comme suffisante et mets requires_more_iterations=false.

Évalue la complétude et réponds au format JSON:
{{
    "overall_completeness": 0.0-1.0,
    "confidence_level": 0.0-1.0,
    "analysis_quality": 0.0-1.0,
    "requires_more_iterations": true/false,
    "recommended_next_steps": ["step1", "step2"],
    "areas_needing_deeper_analysis": ["area1", "area2"],
    "sufficient_for_decision": true/false,
    "iteration_value_assessment": "high/medium/low",
    "stopping_criteria_met": {{
        "min_confidence": true/false,
        "target_completeness": true/false,
        "document_coverage": true/false
    }}
}}
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompts["iterative_analyzer"]},
                    {"role": "user", "content": completeness_prompt}
                ],
                model="gpt-4.1",
                temperature=0.1
            )
            
            assessment = json.loads(response)
            
            # SÉCURITÉ: Forcer l'arrêt si les limites sont atteintes
            if force_stop:
                logger.info(f"Forçage de l'arrêt - Itération {iteration_ctx.current_iteration}")
                assessment["requires_more_iterations"] = False
                assessment["sufficient_for_decision"] = True
                assessment["stopping_criteria_met"] = {
                    "min_confidence": True,
                    "target_completeness": True, 
                    "document_coverage": True
                }
                assessment["iteration_value_assessment"] = "sufficient"
                assessment["recommended_next_steps"] = ["finalize_analysis"]
            
            return assessment
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation de complétude: {str(e)}")
            # CORRECTION: En cas d'erreur, ne pas forcer plus d'itérations
            # Vérifier si on a déjà des résultats utilisables
            has_some_results = (
                len(iteration_ctx.document_analysis_progress) > 0 or
                len(iteration_ctx.knowledge_accumulator) > 0 or
                iteration_ctx.current_iteration > 1
            )
            
            return {
                "overall_completeness": 0.6 if has_some_results else 0.3,
                "confidence_level": 0.6 if has_some_results else 0.3,
                "analysis_quality": 0.5,
                "requires_more_iterations": False,  # CHANGÉ: Ne pas forcer plus d'itérations en cas d'erreur
                "recommended_next_steps": ["finalize_with_available_data"],
                "areas_needing_deeper_analysis": ["error_occurred"],
                "sufficient_for_decision": has_some_results,
                "iteration_value_assessment": "low",
                "stopping_criteria_met": {
                    "min_confidence": has_some_results, 
                    "target_completeness": has_some_results, 
                    "document_coverage": has_some_results
                }
            }

    async def _perform_iterative_compliance_assessment(self, query: Query,
                                                     analysis_intent: Dict[str, Any],
                                                     iteration_ctx: IterativeAnalysisContext,
                                                     completeness_assessment: Dict[str, Any]) -> AgentResponse:
        """
        Effectue une évaluation de conformité avec approche itérative et sources détaillées.
        """
        # Calculer les métriques de connaissances intégrées
        integrated_knowledge = {
            "total_insights": sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values()),
            "gaps_remaining": len(iteration_ctx.context_gaps_identified),
            "frameworks_depth": iteration_ctx.depth_achieved,
            "documents_analyzed": len(iteration_ctx.document_analysis_progress)
        }
        
        # Synthétiser toutes les connaissances accumulées
        synthesis_prompt = f"""
Synthétise une évaluation de conformité complète basée sur {iteration_ctx.current_iteration} itération(s) d'analyse.

REQUÊTE: "{query.query_text}"

CONNAISSANCES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

DOCUMENTS ANALYSÉS: {len(iteration_ctx.document_analysis_progress)}
FRAMEWORKS COUVERTS: {[f.value for f in iteration_ctx.frameworks_analyzed]}
PROFONDEUR ATTEINTE: {iteration_ctx.depth_achieved}

ÉVALUATION DE COMPLÉTUDE:
{json.dumps(completeness_assessment, indent=2, ensure_ascii=False)}

Fournis une évaluation de conformité complète incluant:
1. État actuel de conformité par framework
2. Gaps identifiés et leur criticité
3. Recommandations prioritaires
4. Plan d'action structuré
5. Évaluation de la confiance dans l'analyse
6. Besoins d'itérations supplémentaires si applicable

IMPORTANT: Indique clairement les sources d'information utilisées et leur fiabilité.

Réponds en français avec un niveau d'expertise C-suite.
"""

        try:
            synthesis = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["compliance_expert"]},
                    {"role": "user", "content": synthesis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
            # Compiler les sources détaillées avec métadonnées complètes
            detailed_sources = self._compile_detailed_sources_with_metadata(iteration_ctx)
            
            # Construire la réponse avec métadonnées itératives
            response = AgentResponse(
                content=synthesis,
                tools_used=["document_finder", "entity_extractor", "framework_parser", "llm_analysis"],
                context_used=True,
                sources=detailed_sources,
                confidence=completeness_assessment.get("confidence_level", 0.8),
                iteration_info={
                    "total_iterations": iteration_ctx.current_iteration,
                    "completeness_achieved": completeness_assessment.get("overall_completeness", 0.0),
                    "documents_analyzed": len(iteration_ctx.document_analysis_progress),
                    "frameworks_covered": len(iteration_ctx.frameworks_analyzed),
                    "sources_detail_level": "comprehensive"
                },
                requires_iteration=completeness_assessment.get("requires_more_iterations", False),
                context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", []),
                knowledge_gained=self._extract_key_insights(iteration_ctx),
                metadata={
                    "iteration_summary": {
                        "knowledge_quality": integrated_knowledge.get("total_insights", 0),
                        "gaps_resolved": len(iteration_ctx.context_gaps_identified),
                        "depth_by_framework": iteration_ctx.depth_achieved,
                        "analysis_progression": completeness_assessment,
                        "source_transparency": "full_traceability_enabled"
                    },
                    "sources_metadata": {
                        "total_sources": len(detailed_sources),
                        "source_types": list(set(s.get("type", "unknown") for s in detailed_sources)),
                        "reliability_scores": [s.get("reliability", 0.5) for s in detailed_sources if "reliability" in s]
                    }
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la synthèse itérative: {str(e)}")
            return AgentResponse(
                content=f"Erreur lors de l'analyse itérative: {str(e)}",
                confidence=0.3,
                requires_iteration=True,
                context_gaps=["error_in_synthesis"],
                sources=[{
                    "type": "error_log",
                    "title": "Erreur d'analyse",
                    "details": str(e),
                    "timestamp": datetime.now().isoformat()
                }]
            )

    def _compile_detailed_sources_with_metadata(self, iteration_ctx: IterativeAnalysisContext) -> List[Dict[str, Any]]:
        """Compile les sources avec métadonnées complètes pour transparence maximale."""
        detailed_sources = []
        
        # Sources documentaires analysées
        for doc_id, progress in iteration_ctx.document_analysis_progress.items():
            source = {
                "type": "document_analysis",
                "id": doc_id,
                "title": f"Document d'analyse GRC - {doc_id}",
                "iteration": progress.get("iteration", 0),
                "analysis_depth": progress.get("analysis_depth", 0.0),
                "insights_count": progress.get("insights_extracted", 0),
                "frameworks_addressed": progress.get("frameworks_covered", []),
                "gaps_resolved": progress.get("gaps_filled", []),
                "confidence_score": progress.get("confidence_level", 0.5),
                "tools_used": ["document_finder", "entity_extractor", "framework_parser", "llm_analysis"],
                "timestamp": datetime.now().isoformat(),
                "reliability": progress.get("source_quality_assessment", {}).get("reliability", 0.7),
                "details": f"Analyse de profondeur {progress.get('analysis_depth', 0.0):.1%} avec {progress.get('insights_extracted', 0)} insights extraits"
            }
            detailed_sources.append(source)
        
        # Sources de connaissances accumulées par itération
        for knowledge_key, knowledge_items in iteration_ctx.knowledge_accumulator.items():
            if knowledge_items:
                source = {
                    "type": "knowledge_accumulation",
                    "id": knowledge_key,
                    "title": f"Base de connaissances accumulées - {knowledge_key}",
                    "content_count": len(knowledge_items),
                    "sample_insights": knowledge_items[:2] if knowledge_items else [],
                    "tools_used": ["llm_analysis", "knowledge_extraction", "iterative_synthesis"],
                    "reliability": 0.8,  # Confiance élevée pour connaissances synthétisées
                    "details": f"Accumulation itérative de {len(knowledge_items)} éléments de connaissance GRC"
                }
                detailed_sources.append(source)
        
        # Source méthodologique pour l'approche itérative
        if iteration_ctx.current_iteration > 0:
            source = {
                "type": "methodology",
                "id": "iterative_analysis_methodology",
                "title": "Méthodologie d'analyse itérative GRC",
                "iterations_performed": iteration_ctx.current_iteration,
                "frameworks_analyzed": [f.value for f in iteration_ctx.frameworks_analyzed],
                "depth_progression": iteration_ctx.depth_achieved,
                "tools_used": ["orchestrator", "compliance_module", "iterative_analyzer"],
                "reliability": 0.9,  # Haute confiance dans la méthodologie
                "details": f"Analyse en {iteration_ctx.current_iteration} itérations avec progression de profondeur mesurée"
            }
            detailed_sources.append(source)
        
        return detailed_sources

    def _compile_iteration_sources(self, iteration_ctx: IterativeAnalysisContext) -> List[Dict[str, Any]]:
        """Compile toutes les sources utilisées à travers les itérations avec détails complets."""
        sources = []
        
        for doc_id, progress in iteration_ctx.document_analysis_progress.items():
            # Source détaillée avec métadonnées complètes
            source = {
                "type": "document",
                "id": doc_id,
                "title": f"Document d'analyse {doc_id}",
                "iteration": progress.get("iteration", 0),
                "analysis_depth": progress.get("analysis_depth", 0.0),
                "insights_extracted": progress.get("insights_extracted", 0),
                "gaps_addressed": progress.get("gaps_filled", []),
                "confidence_level": progress.get("confidence_level", 0.5),
                "frameworks_covered": progress.get("frameworks_covered", []),
                "tools_used": ["document_finder", "entity_extractor", "framework_parser"],
                "timestamp": datetime.now().isoformat(),
                "details": f"Analyse itérative de profondeur {progress.get('analysis_depth', 0.0):.2f} - {progress.get('insights_extracted', 0)} insights extraits"
            }
            sources.append(source)
        
        # Ajouter les sources de connaissances accumulées
        for knowledge_key, knowledge_items in iteration_ctx.knowledge_accumulator.items():
            if knowledge_items:
                source = {
                    "type": "knowledge_base",
                    "id": knowledge_key,
                    "title": f"Base de connaissances - {knowledge_key}",
                    "content_count": len(knowledge_items),
                    "items": knowledge_items[:3],  # Premiers éléments pour aperçu
                    "tools_used": ["llm_analysis", "knowledge_extraction"],
                    "details": f"Accumulation de {len(knowledge_items)} éléments de connaissance"
                }
                sources.append(source)
        
        return sources

    def _extract_key_insights(self, iteration_ctx: IterativeAnalysisContext) -> List[str]:
        """Extrait les insights clés de toutes les itérations."""
        key_insights = []
        
        for iteration_key, insights in iteration_ctx.knowledge_accumulator.items():
            key_insights.extend(insights[:3])  # Top 3 insights par itération
        
        return key_insights

    async def _analyze_query_intent_with_iterative_context(self, query_text: str,
                                                         iteration_ctx: IterativeAnalysisContext,
                                                         parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse sophistiquée de l'intention de la requête avec contexte itératif."""
        
        intent_analysis_prompt = f"""
Analyse cette demande de conformité et retourne UNIQUEMENT un objet JSON avec ta compréhension experte.

DEMANDE: "{query_text}"

IMPORTANT: Réponds UNIQUEMENT avec l'objet JSON, sans texte d'explication avant ou après.

JSON Format attendu:
{{
  "type": "compliance_assessment|gap_analysis|regulatory_intelligence|multi_framework_optimization|strategic_roadmap|general_analysis",
  "frameworks": ["iso27001", "rgpd", "dora", "nist", "sox", "pci-dss"],
  "priority": "critique|haute|normale|faible",
  "scope": ["EU", "France"],
  "detail_level": "strategique|operationnel|technique",
  "context_assessment": {{
    "knowledge_completeness": 0.0-1.0,
    "coverage_gaps": ["gap1", "gap2"],
    "priority_domains": ["domain1", "domain2"]
  }}
}}

CONTEXTE ACCUMULÉ:
- Connaissances: {len(iteration_ctx.knowledge_accumulator)} domaines
- Documents analysés: {len(iteration_ctx.document_analysis_progress)}
- Frameworks couverts: {[f.value for f in iteration_ctx.frameworks_analyzed]}

Réponds UNIQUEMENT avec le JSON valide:"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["compliance_expert"]},
                {"role": "user", "content": intent_analysis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        try:
            # Try to extract JSON from response
            if response and response.strip():
                # Clean the response - remove any markdown formatting
                cleaned_response = response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]
                cleaned_response = cleaned_response.strip()
                
                # Find JSON boundaries
                json_start = cleaned_response.find("{")
                json_end = cleaned_response.rfind("}") + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_content = cleaned_response[json_start:json_end]
                    logger.debug(f"Attempting to parse JSON: {json_content[:200]}...")
                    
                    parsed_result = json.loads(json_content)
                    
                    # Validate structure and required fields
                    if isinstance(parsed_result, dict) and "type" in parsed_result:
                        # Ensure all required fields have defaults
                        parsed_result.setdefault("frameworks", ["iso27001", "rgpd"])
                        parsed_result.setdefault("priority", "normale")
                        parsed_result.setdefault("scope", ["EU"])
                        parsed_result.setdefault("detail_level", "operationnel")
                        
                        logger.info(f"Successfully parsed query intent: type={parsed_result['type']}, frameworks={parsed_result['frameworks']}")
                        return parsed_result
                    else:
                        raise ValueError(f"Invalid JSON structure: missing 'type' field or not a dict")
                else:
                    # Try to parse the entire response as JSON
                    logger.debug(f"No JSON boundaries found, trying to parse entire response: {cleaned_response[:100]}...")
                    parsed_result = json.loads(cleaned_response)
                    if isinstance(parsed_result, dict) and "type" in parsed_result:
                        parsed_result.setdefault("frameworks", ["iso27001", "rgpd"])
                        parsed_result.setdefault("priority", "normale")
                        parsed_result.setdefault("scope", ["EU"])
                        logger.info(f"Successfully parsed full response as JSON: type={parsed_result['type']}")
                        return parsed_result
                    else:
                        raise ValueError("No valid JSON structure found in response")
            else:
                raise ValueError("Empty LLM response")
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            logger.debug(f"Failed to parse response: {response[:500] if response else 'None'}")
        except Exception as e:
            logger.error(f"Erreur analyse intention: {str(e)}")
            logger.debug(f"Response causing error: {response[:300] if response else 'None'}")
            
        # Fallback to default parameters with improved error reporting
        logger.warning("Utilisation de paramètres d'analyse par défaut")
        logger.info("Using default analysis parameters due to LLM intent analysis failure")
        
        return {
            "type": "general_analysis",
            "frameworks": ["iso27001", "rgpd"],
            "priority": "normale",
            "scope": ["EU"],
            "detail_level": "operationnel",
            "error_note": "Analyse d'intention LLM échouée - paramètres par défaut utilisés",
            "fallback_reason": "JSON parsing failed or invalid structure"
        }

    async def _process_standard_compliance_query(self, query: Query,
                                                  analysis_intent: Dict[str, Any]) -> AgentResponse:
        """
        Effectue une analyse standard de conformité.
        """
        logger.info(f"Traitement requête standard de conformité: {query.query_text}")
        
        # Analyse sophistiquée de la demande par LLM
        analysis_intent = await self._analyze_query_intent_with_iterative_context(
            query.query_text, IterativeAnalysisContext(), query.parameters
        )
        
        if analysis_intent["type"] == "compliance_assessment":
            return await self._perform_compliance_assessment(query, analysis_intent)
        elif analysis_intent["type"] == "gap_analysis":
            return await self._perform_gap_analysis(query, analysis_intent)
        elif analysis_intent["type"] == "regulatory_intelligence":
            return await self._provide_regulatory_intelligence(query, analysis_intent)
        else:
            return await self._general_compliance_analysis(query, analysis_intent)

    async def _perform_compliance_assessment(self, query: Query,
                                                  analysis_intent: Dict[str, Any]) -> AgentResponse:
        """Effectue une évaluation de conformité."""
        
        frameworks = [safe_framework_type_conversion(f) for f in analysis_intent.get("frameworks", ["iso27001"])]
        org_profile = query.context.metadata.get("organization", {}) if query.context else {}
        
        assessments = await self.assess_multi_framework_compliance(
            frameworks, org_profile
        )
        
        # Synthèse par LLM
        synthesis = await self._synthesize_assessment_results_with_llm(assessments, query.query_text)
        
        return AgentResponse(
            content=synthesis,
            tools_used=["framework_parser", "document_finder", "entity_extractor"],
            context_used=True,
            sources=[],
            metadata={
                "frameworks_assessed": [f.value for f in frameworks],
                "average_score": sum(a.overall_score for a in assessments) / len(assessments),
                "critical_gaps": sum(a.critical_gaps for a in assessments),
                "assessment_confidence": sum(a.confidence_level for a in assessments) / len(assessments)
            }
        )

    async def _perform_gap_analysis(self, query: Query,
                                                  analysis_intent: Dict[str, Any]) -> AgentResponse:
        """Effectue une analyse de gaps optimisée pour éviter les timeouts."""
        
        framework = safe_framework_type_conversion(analysis_intent.get("frameworks", ["rgpd"])[0])
        
        # NOUVELLE APPROCHE RAPIDE: Analyse directe pour les requêtes simples
        if self._is_simple_gap_query(query.query_text):
            logger.info("Utilisation de l'analyse rapide pour requête simple de gap")
            return await self._perform_fast_gap_analysis(query, framework)
        
        # Approche standard avec timeouts stricts
        org_profile = query.context.metadata.get("organization", {}) if query.context else {}
        current_impl = query.context.metadata.get("current_implementation", {}) if query.context else {}
        
        try:
            # Timeout strict pour l'analyse des gaps
            gaps = await asyncio.wait_for(
                self.framework_parser.analyze_compliance_gaps(framework, current_impl, org_profile),
                timeout=30  # 30 secondes maximum
            )
            
            # Analyse sophistiquée des gaps par LLM avec timeout
            gap_analysis = await asyncio.wait_for(
                self._analyze_gaps_with_llm(gaps, framework, org_profile),
                timeout=30  # 30 secondes maximum
            )
            
            return AgentResponse(
                content=gap_analysis,
                tools_used=["framework_parser"],
                context_used=True,
                sources=[],
                metadata={
                    "framework": framework.value,
                    "total_gaps": len(gaps),
                    "critical_gaps": len([g for g in gaps if g.severity == "critical"]),
                    "estimated_effort": "calculated",
                    "analysis_method": "standard_with_timeout"
                }
            )
            
        except asyncio.TimeoutError:
            logger.warning("Timeout lors de l'analyse de gaps, basculement vers analyse rapide")
            return await self._perform_fast_gap_analysis(query, framework)
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de gaps: {str(e)}")
            return await self._perform_fast_gap_analysis(query, framework)

    async def _perform_fast_gap_analysis(self, query: Query, framework: FrameworkType) -> AgentResponse:
        """
        Analyse rapide de gaps sans dépendances externes lentes.
        Optimisée pour les requêtes simples comme 'à quels articles du RGPD je suis pas conforme?'
        """
        logger.info(f"Analyse rapide de gaps pour {framework.value}")
        
        # Analyse directe par LLM sans recherche de documents ni extraction d'entités
        fast_gap_prompt = f"""
Tu es un expert DPO/CISO spécialisé en {framework.value}. Réponds directement à cette question:

QUESTION: "{query.query_text}"

Basé sur ton expertise, identifie les articles/exigences {framework.value} où les organisations sont le plus souvent NON CONFORMES:

STRUCTURE DE RÉPONSE:

## Articles {framework.value} fréquemment problématiques

### 🔴 Gaps critiques courants:
- **Article/Exigence X**: Problème typique et pourquoi
- **Article/Exigence Y**: Problème typique et pourquoi
- **Article/Exigence Z**: Problème typique et pourquoi

### 🟡 Gaps fréquents mais moins critiques:
- Point 1: Description concise
- Point 2: Description concise
- Point 3: Description concise

### 💡 Recommandations immédiates:
1. Action prioritaire 1
2. Action prioritaire 2  
3. Action prioritaire 3

### 📋 Prochaines étapes:
- Étape de diagnostic recommandée
- Points de vigilance à surveiller

IMPORTANT: 
- Réponds de manière concrète et actionnable
- Base-toi sur les problèmes de conformité les plus courants
- Donne des conseils pratiques
- Reste spécifique au framework {framework.value}

Réponds en français de manière structurée et professionnelle.
"""

        try:
            # Appel LLM direct avec timeout court
            analysis_result = await asyncio.wait_for(
                self.llm_client.generate_response(
                    messages=[
                        {"role": "system", "content": self.system_prompts["compliance_expert"]},
                        {"role": "user", "content": fast_gap_prompt}
                    ],
                    model="gpt-4.1",
                    temperature=0.2
                ),
                timeout=45  # 45 secondes maximum
            )
            
            return AgentResponse(
                content=analysis_result,
                tools_used=["llm_expert_analysis"],
                context_used=False,
                sources=[{
                    "type": "expert_knowledge",
                    "title": f"Expertise {framework.value} - Gaps courants",
                    "description": "Analyse basée sur l'expertise IA des non-conformités typiques",
                    "reliability": 0.85,
                    "coverage": "gaps_frequents"
                }],
                confidence=0.80,
                metadata={
                    "framework": framework.value,
                    "analysis_method": "fast_expert",
                    "processing_time": "< 45 seconds",
                    "optimization": "direct_llm_analysis"
                }
            )
            
        except asyncio.TimeoutError:
            logger.error("Timeout même avec analyse rapide, utilisation du mode ultra-rapide")
            return self._get_ultra_fast_gap_response(query, framework)
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse rapide: {str(e)}")
            return self._get_ultra_fast_gap_response(query, framework)

    def _get_ultra_fast_gap_response(self, query: Query, framework: FrameworkType) -> AgentResponse:
        """
        Réponse ultra-rapide en mode dégradé - pas d'appel LLM, juste des connaissances statiques.
        """
        
        # Base de connaissances statique pour éviter tout appel externe
        rgpd_gaps = {
            "critical": [
                "Article 5 - Principes de traitement: finalités mal définies, proportionnalité non respectée",
                "Article 6 - Licéité: bases légales inappropriées ou multiples",
                "Article 13/14 - Information: mentions incomplètes ou illisibles",
                "Article 25 - Privacy by Design: mesures techniques insuffisantes",
                "Article 30 - Registre des traitements: incomplet ou obsolète",
                "Article 32 - Sécurité: mesures de protection insuffisantes"
            ],
            "frequent": [
                "Article 7 - Consentement: preuves insuffisantes, retrait complexe",
                "Article 17 - Droit à l'effacement: procédures mal définies",
                "Article 20 - Portabilité: formats techniques non conformes",
                "Article 35 - AIPD: analyses manquantes pour traitements à risque"
            ]
        }
        
        iso27001_gaps = {
            "critical": [
                "A.8.1 - Inventaire des actifs: catalogue incomplet",
                "A.12.1 - Procédures opérationnelles: documentation insuffisante", 
                "A.13.1 - Gestion réseau: contrôles d'accès faibles",
                "A.18.1 - Conformité: veille réglementaire insuffisante"
            ],
            "frequent": [
                "A.9.1 - Contrôle d'accès: droits excessifs, revues manquantes",
                "A.14.2 - Sécurité développement: tests sécurité insuffisants",
                "A.16.1 - Gestion incidents: procédures non testées"
            ]
        }
        
        framework_name = framework.value.upper()
        gaps_data = rgpd_gaps if "rgpd" in framework.value.lower() else iso27001_gaps
        
        content = f"""
# Analyse de Conformité {framework_name} - Réponse à votre question

## "{query.query_text}"

### 🔴 Gaps critiques les plus fréquents:

{chr(10).join([f"- **{gap}**" for gap in gaps_data["critical"]])}

### 🟡 Autres gaps courants:

{chr(10).join([f"- {gap}" for gap in gaps_data["frequent"]])}

### 💡 Recommandations immédiates:

1. **Audit de conformité**: Réaliser un diagnostic complet
2. **Priorisation**: Traiter d'abord les gaps critiques  
3. **Plan d'action**: Établir un calendrier de mise en conformité
4. **Formation**: Sensibiliser les équipes aux exigences

### 📋 Prochaines étapes:

- Consultation d'un expert spécialisé {framework_name}
- Évaluation détaillée de votre contexte organisationnel
- Mise en place d'un programme de conformité continue

---
*Analyse basée sur les non-conformités les plus fréquemment observées. Une évaluation personnalisée est recommandée pour votre organisation.*
"""

        return AgentResponse(
            content=content,
            confidence=0.70,
            tools_used=["static_knowledge"],
            sources=[{
                "type": "static_expertise", 
                "title": f"Gaps {framework_name} fréquents",
                "description": "Base de connaissances des non-conformités typiques"
            }],
            metadata={
                "framework": framework.value,
                "analysis_method": "ultra_fast_static",
                "processing_time": "< 1 second",
                "mode": "degraded_fallback"
            }
        )

    async def _provide_regulatory_intelligence(self, query: Query,
                                                  analysis_intent: Dict[str, Any]) -> AgentResponse:
        """Fournit une intelligence réglementaire proactive."""
        
        frameworks = [safe_framework_type_conversion(f) for f in analysis_intent.get("frameworks", ["rgpd"])]
        geographic_scope = analysis_intent.get("scope", ["EU", "France"])
        time_horizon = analysis_intent.get("horizon", 12)
        
        intelligence_reports = await self.generate_regulatory_intelligence(
            frameworks, geographic_scope, time_horizon
        )
        
        # Synthèse par LLM
        synthesis_prompt = f"""
Synthétise cette intelligence réglementaire pour répondre à: "{query.query_text}"

RAPPORTS D'INTELLIGENCE:
{json.dumps([{
    "framework": r.framework.value,
    "recent_changes": len(r.recent_changes),
    "upcoming_changes": len(r.upcoming_changes),
    "monitoring_priorities": r.monitoring_priorities[:3]
} for r in intelligence_reports], indent=2)}

Fournis une synthèse exécutive claire et actionnable.
"""
        
        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["regulatory_intelligence"]},
                {"role": "user", "content": synthesis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        return AgentResponse(
            content=response,
            tools_used=["regulatory_intelligence"],
            context_used=True,
            sources=[],
            metadata={
                "frameworks": [f.value for f in frameworks],
                "geographic_scope": geographic_scope,
                "time_horizon": time_horizon,
                "reports_generated": len(intelligence_reports)
            }
        )

    async def _general_compliance_analysis(self, query: Query,
                                                  analysis_intent: Dict[str, Any]) -> AgentResponse:
        """Effectue une analyse générale de conformité avec timeouts optimisés."""
        
        # Si c'est une requête simple, utiliser l'analyse rapide
        if self._is_simple_gap_query(query.query_text):
            framework = safe_framework_type_conversion(analysis_intent.get("frameworks", ["rgpd"])[0])
            return await self._perform_fast_gap_analysis(query, framework)
        
        try:
            # Collecte d'informations contextuelles avec timeout
            relevant_docs = await asyncio.wait_for(
                self.document_finder.search_documents(
                    f"conformité compliance réglementation {query.query_text}",
                    limit=10  # Réduit de 15 à 10
                ),
                timeout=20  # 20 secondes maximum
            )
            
            # Extraction d'entités limitée avec timeout
            compliance_entities = []
            docs_to_process = relevant_docs[:3]  # Réduit de 5 à 3
            
            for doc in docs_to_process:
                try:
                    content = doc.get("content", "")
                    if content:
                        entities = await asyncio.wait_for(
                            self.entity_extractor.extract_entities(
                                content[:2000],  # Limiter le contenu à analyser
                                entity_types=[EntityType.CONTROL, EntityType.REQUIREMENT, EntityType.RISK],
                                framework_context="general"
                            ),
                            timeout=10  # 10 secondes par document
                        )
                        compliance_entities.extend(entities.get("control", []))
                        compliance_entities.extend(entities.get("requirement", []))
                        compliance_entities.extend(entities.get("risk", []))
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout lors de l'extraction d'entités pour le document {doc.get('doc_id', 'unknown')}")
                    continue
            
            # Analyse générale par LLM avec timeout
            analysis_prompt = f"""
Effectue une analyse générale de conformité pour: "{query.query_text}"

DOCUMENTS ANALYSÉS: {len(relevant_docs)}
ENTITÉS IDENTIFIÉES: {len(compliance_entities)}

En tant qu'expert en conformité, fournis une analyse concise incluant:

1. ÉVALUATION GÉNÉRALE:
   - Points forts identifiés
   - Lacunes principales
   
2. RECOMMANDATIONS PRIORITAIRES:
   - 3 actions immédiates
   - Approche d'amélioration
   
3. FRAMEWORKS APPLICABLES:
   - Frameworks pertinents
   - Priorisation recommandée

Fournis une analyse experte actionnable et concise.
"""
            
            response = await asyncio.wait_for(
                self.llm_client.generate_response(
                    messages=[
                        {"role": "system", "content": self.system_prompts["compliance_expert"]},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    model="gpt-4.1",
                    temperature=0.3
                ),
                timeout=30  # 30 secondes maximum
            )
            
            return AgentResponse(
                content=response,
                tools_used=["document_finder", "entity_extractor"],
                context_used=True,
                sources=self.format_documents_as_sources(relevant_docs[:3]),
                metadata={
                    "documents_analyzed": len(relevant_docs),
                    "entities_extracted": len(compliance_entities),
                    "analysis_scope": "general_compliance",
                    "analysis_method": "optimized"
                }
            )
            
        except asyncio.TimeoutError:
            logger.warning("Timeout lors de l'analyse générale, utilisation de l'analyse simplifiée")
            return await self._get_simplified_compliance_analysis(query, analysis_intent)
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse générale: {str(e)}")
            return await self._get_simplified_compliance_analysis(query, analysis_intent)

    async def _get_simplified_compliance_analysis(self, query: Query, analysis_intent: Dict[str, Any]) -> AgentResponse:
        """Analyse de conformité simplifiée en mode dégradé."""
        
        framework = safe_framework_type_conversion(analysis_intent.get("frameworks", ["rgpd"])[0])
        
        simplified_prompt = f"""
Analyse de conformité simplifiée pour: "{query.query_text}"

En tant qu'expert {framework.value}, fournis une analyse directe:

1. **ÉVALUATION**: Points clés à considérer
2. **RECOMMANDATIONS**: 3 actions prioritaires  
3. **PROCHAINES ÉTAPES**: Approche structurée

Réponds de manière concise et actionnable en français.
"""
        
        try:
            response = await asyncio.wait_for(
                self.llm_client.generate_response(
                    messages=[
                        {"role": "system", "content": self.system_prompts["compliance_expert"]},
                        {"role": "user", "content": simplified_prompt}
                    ],
                    model="gpt-4.1",
                    temperature=0.3
                ),
                timeout=30
            )
            
            return AgentResponse(
                content=response,
                tools_used=["llm_simplified"],
                context_used=False,
                sources=[],
                confidence=0.70,
                metadata={
                    "analysis_method": "simplified",
                    "framework": framework.value,
                    "mode": "timeout_fallback"
                }
            )
            
        except Exception:
            # Ultra fallback sans LLM
            return AgentResponse(
                content=f"""
# Analyse de Conformité - Mode Dégradé

## Votre question: "{query.query_text}"

### Recommandations générales:

1. **Audit de conformité**: Réaliser un diagnostic complet
2. **Identification des gaps**: Cartographier les écarts actuels
3. **Plan d'action**: Prioriser les mesures correctives

### Prochaines étapes:
- Consultation d'un expert spécialisé
- Évaluation personnalisée de votre contexte
- Mise en place d'un programme de conformité

*Cette analyse simplifiée nécessite un approfondissement selon votre contexte organisationnel.*
""",
                confidence=0.60,
                tools_used=["static_fallback"],
                sources=[],
                metadata={
                    "analysis_method": "ultra_simplified",
                    "mode": "static_fallback"
                }
            )

    async def _analyze_gaps_with_llm(self, gaps: List[ComplianceGap],
                                                  framework: FrameworkType,
                                                  org_profile: Dict[str, Any]) -> str:
        """Analyse sophistiquée des gaps."""
        
        critical_gaps = [g for g in gaps if g.severity == "critical"]
        high_gaps = [g for g in gaps if g.severity == "high"]
        
        return f"""
Analyse des gaps de conformité {framework.value}:

**Gaps critiques**: {len(critical_gaps)}
**Gaps élevés**: {len(high_gaps)}
**Total gaps**: {len(gaps)}

**Gaps critiques prioritaires**:
{chr(10).join([f"- {g.description}" for g in critical_gaps[:5]])}

**Recommandations**:
1. Traiter immédiatement les gaps critiques
2. Planifier la remédiation des gaps élevés
3. Établir un processus de monitoring continu
"""

    async def _synthesize_assessment_results_with_llm(self,
        assessments: List[ComplianceAssessment], 
                                                      original_query: str) -> str:
        """Synthétise les résultats d'évaluation."""
        
        # Simplification pour le démo
        frameworks = [a.framework.value for a in assessments]
        avg_score = sum(a.overall_score for a in assessments) / len(assessments)
        total_gaps = sum(a.gap_count for a in assessments)
        
        return f"""
Évaluation de conformité multi-frameworks terminée.

**Frameworks évalués**: {', '.join(frameworks)}
**Score moyen de conformité**: {avg_score:.1f}%
**Gaps identifiés**: {total_gaps} au total

**Synthèse**: L'organisation présente un niveau de conformité {'satisfaisant' if avg_score > 70 else 'nécessitant des améliorations'}.
Les efforts doivent se concentrer sur les gaps critiques identifiés.

**Prochaines étapes recommandées**:
1. Prioriser la remédiation des gaps critiques
2. Mettre en place un plan de conformité continue
3. Renforcer la gouvernance des données
"""

    async def _synthesize_iterative_results_with_llm(self,
                                                      analysis_results: Dict[str, Any],
                                                      original_query: str) -> str:
        """Synthétise les résultats d'analyse itérative."""
        
        # Simplification pour le démo
        insights = [result.get("insights_extracted", []) for result in analysis_results.values()]
        total_insights = sum(len(insights) for insights in insights)
        
        return f"""
Évaluation itérative terminée.

**Insights extraits**: {total_insights} au total

**Synthèse**: L'analyse a révélé {total_insights} insights utiles pour répondre à la requête initiale.

**Prochaines étapes recommandées**:
1. Prioriser la mise en œuvre des insights les plus pertinents
2. Planifier des itérations supplémentaires si nécessaire
3. Renforcer la gouvernance des données et des processus
"""

    async def _perform_iterative_gap_analysis(self, query: Query,
                                                  analysis_intent: Dict[str, Any],
                                                  iteration_ctx: IterativeAnalysisContext,
                                                  completeness_assessment: Dict[str, Any]) -> AgentResponse:
        """
        Effectue une analyse de gaps avec approche itérative.
        """
        # Calculer les métriques de connaissances intégrées
        integrated_knowledge = {
            "total_insights": sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values()),
            "gaps_remaining": len(iteration_ctx.context_gaps_identified),
            "frameworks_depth": iteration_ctx.depth_achieved,
            "documents_analyzed": len(iteration_ctx.document_analysis_progress)
        }
        
        # Synthétiser les résultats d'analyse itérative pour gap analysis
        synthesis_prompt = f"""
Synthétise une analyse de gaps de conformité complète basée sur {iteration_ctx.current_iteration} itération(s).

REQUÊTE: "{query.query_text}"

CONNAISSANCES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

MÉTRIQUES:
- Total insights: {integrated_knowledge['total_insights']}
- Gaps restants: {integrated_knowledge['gaps_remaining']}
- Documents analysés: {integrated_knowledge['documents_analyzed']}

Fournis une analyse de gaps structurée avec sources clairement identifiées.
"""

        try:
            synthesis = await self.llm_client.generate_response(
            messages=[
                    {"role": "system", "content": self.system_prompts["compliance_expert"]},
                    {"role": "user", "content": synthesis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        except Exception as e:
            synthesis = f"Analyse de gaps itérative - {integrated_knowledge['total_insights']} insights collectés sur {integrated_knowledge['documents_analyzed']} documents."
        
        # Compiler les sources détaillées
        detailed_sources = self._compile_detailed_sources_with_metadata(iteration_ctx)
        
        # Construire la réponse avec métadonnées itératives
        response = AgentResponse(
            content=synthesis,
            tools_used=["document_finder", "entity_extractor", "framework_parser"],
            context_used=True,
            sources=detailed_sources,
            confidence=completeness_assessment.get("confidence_level", 0.8),
            iteration_info={
                "total_iterations": iteration_ctx.current_iteration,
                "completeness_achieved": completeness_assessment.get("overall_completeness", 0.0),
                "documents_analyzed": len(iteration_ctx.document_analysis_progress),
                "frameworks_covered": len(iteration_ctx.frameworks_analyzed)
            },
            requires_iteration=completeness_assessment.get("requires_more_iterations", False),
            context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", []),
            knowledge_gained=self._extract_key_insights(iteration_ctx),
            metadata={
                "iteration_summary": {
                    "knowledge_quality": integrated_knowledge["total_insights"],
                    "gaps_resolved": len(iteration_ctx.context_gaps_identified),
                    "depth_by_framework": iteration_ctx.depth_achieved,
                    "analysis_progression": completeness_assessment
                }
            }
        )
        
        return response

    async def _provide_iterative_regulatory_intelligence(self, query: Query,
                                                  analysis_intent: Dict[str, Any],
                                                  iteration_ctx: IterativeAnalysisContext,
                                                  completeness_assessment: Dict[str, Any]) -> AgentResponse:
        """
        Fournit une intelligence réglementaire proactive avec approche itérative.
        """
        # Calculer les métriques de connaissances intégrées
        integrated_knowledge = {
            "total_insights": sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values()),
            "gaps_remaining": len(iteration_ctx.context_gaps_identified),
            "frameworks_depth": iteration_ctx.depth_achieved,
            "documents_analyzed": len(iteration_ctx.document_analysis_progress)
        }
        
        # Synthétiser l'intelligence réglementaire
        synthesis_prompt = f"""
Synthétise une intelligence réglementaire complète basée sur {iteration_ctx.current_iteration} itération(s).

REQUÊTE: "{query.query_text}"

CONNAISSANCES RÉGLEMENTAIRES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

MÉTRIQUES:
- Total insights: {integrated_knowledge['total_insights']}
- Sources consultées: {integrated_knowledge['documents_analyzed']}

Fournis une veille réglementaire avec sources identifiées et traçabilité.
"""

        try:
            synthesis = await self.llm_client.generate_response(
            messages=[
                    {"role": "system", "content": self.system_prompts["regulatory_intelligence"]},
                    {"role": "user", "content": synthesis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        except Exception as e:
            synthesis = f"Intelligence réglementaire itérative - {integrated_knowledge['total_insights']} insights réglementaires collectés."
        
        # Compiler les sources détaillées
        detailed_sources = self._compile_detailed_sources_with_metadata(iteration_ctx)
        
        # Construire la réponse avec métadonnées itératives
        response = AgentResponse(
            content=synthesis,
            tools_used=["regulatory_intelligence"],
            context_used=True,
            sources=detailed_sources,
            confidence=completeness_assessment.get("confidence_level", 0.8),
            iteration_info={
                "total_iterations": iteration_ctx.current_iteration,
                "completeness_achieved": completeness_assessment.get("overall_completeness", 0.0),
                "documents_analyzed": len(iteration_ctx.document_analysis_progress),
                "frameworks_covered": len(iteration_ctx.frameworks_analyzed)
            },
            requires_iteration=completeness_assessment.get("requires_more_iterations", False),
            context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", []),
            knowledge_gained=self._extract_key_insights(iteration_ctx),
            metadata={
                "iteration_summary": {
                    "knowledge_quality": integrated_knowledge["total_insights"],
                    "gaps_resolved": len(iteration_ctx.context_gaps_identified),
                    "depth_by_framework": iteration_ctx.depth_achieved,
                    "analysis_progression": completeness_assessment
                }
            }
        )
        
        return response

    async def _general_iterative_compliance_analysis(self, query: Query,
                                                  analysis_intent: Dict[str, Any],
                                                  iteration_ctx: IterativeAnalysisContext,
                                                  completeness_assessment: Dict[str, Any]) -> AgentResponse:
        """
        Effectue une analyse générale de conformité avec approche itérative.
        """
        # Calculer les métriques de connaissances intégrées
        integrated_knowledge = {
            "total_insights": sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values()),
            "gaps_remaining": len(iteration_ctx.context_gaps_identified),
            "frameworks_depth": iteration_ctx.depth_achieved,
            "documents_analyzed": len(iteration_ctx.document_analysis_progress)
        }
        
        # Synthétiser l'analyse générale
        synthesis_prompt = f"""
Synthétise une analyse générale de conformité basée sur {iteration_ctx.current_iteration} itération(s).

REQUÊTE: "{query.query_text}"

CONNAISSANCES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

MÉTRIQUES:
- Total insights: {integrated_knowledge['total_insights']}
- Documents analysés: {integrated_knowledge['documents_analyzed']}
- Profondeur atteinte: {iteration_ctx.depth_achieved}

Fournis une analyse complète avec traçabilité des sources.
"""

        try:
            synthesis = await self.llm_client.generate_response(
            messages=[
                    {"role": "system", "content": self.system_prompts["compliance_expert"]},
                    {"role": "user", "content": synthesis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        except Exception as e:
            synthesis = f"Analyse générale itérative - {integrated_knowledge['total_insights']} insights collectés via {integrated_knowledge['documents_analyzed']} sources."
        
        # Compiler les sources détaillées
        detailed_sources = self._compile_detailed_sources_with_metadata(iteration_ctx)
        
        # Construire la réponse avec métadonnées itératives
        response = AgentResponse(
            content=synthesis,
            tools_used=["document_finder", "entity_extractor"],
            context_used=True,
            sources=detailed_sources,
            confidence=completeness_assessment.get("confidence_level", 0.8),
            iteration_info={
                "total_iterations": iteration_ctx.current_iteration,
                "completeness_achieved": completeness_assessment.get("overall_completeness", 0.0),
                "documents_analyzed": len(iteration_ctx.document_analysis_progress),
                "frameworks_covered": len(iteration_ctx.frameworks_analyzed)
            },
            requires_iteration=completeness_assessment.get("requires_more_iterations", False),
            context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", []),
            knowledge_gained=self._extract_key_insights(iteration_ctx),
            metadata={
                "iteration_summary": {
                    "knowledge_quality": integrated_knowledge["total_insights"],
                    "gaps_resolved": len(iteration_ctx.context_gaps_identified),
                    "depth_by_framework": iteration_ctx.depth_achieved,
                    "analysis_progression": completeness_assessment
                }
            }
        )
        
        return response

    async def assess_multi_framework_compliance(
        self,
        frameworks: List[FrameworkType],
        org_profile: Dict[str, Any]
    ) -> List[ComplianceAssessment]:
        """
        Effectue une évaluation de conformité multi-frameworks optimisée avec timeouts.
        """
        logger.info(f"Evaluating compliance for frameworks: {[f.value for f in frameworks]}")
        
        assessments = []
        
        for framework in frameworks:
            try:
                # OPTIMISATION: Timeout par framework pour éviter blocage global
                assessment = await asyncio.wait_for(
                    self._assess_single_framework_compliance(framework, org_profile),
                    timeout=45  # 45 secondes par framework
                )
                assessments.append(assessment)
                logger.info(f"Assessment completed for {framework.value}")
                
            except asyncio.TimeoutError:
                logger.warning(f"Timeout lors de l'évaluation {framework.value}, création d'un assessment par défaut")
                assessment = self._create_default_assessment(framework, "timeout")
                assessments.append(assessment)
            except Exception as e:
                logger.error(f"Error assessing {framework.value}: {str(e)}")
                assessment = self._create_default_assessment(framework, str(e))
                assessments.append(assessment)
        
        return assessments

    async def _assess_single_framework_compliance(self, framework: FrameworkType, org_profile: Dict[str, Any]) -> ComplianceAssessment:
        """Évalue la conformité pour un seul framework avec optimisations."""
        
        try:
            # Rechercher des documents pertinents avec timeout réduit
            relevant_docs = await asyncio.wait_for(
                self.document_finder.search_documents(
                    f"conformité {framework.value} compliance",
                    limit=5  # Réduit de 10 à 5
                ),
                timeout=15  # 15 secondes maximum
            )
            
            # Extraction d'entités limitée
            compliance_entities = []
            docs_to_process = relevant_docs[:2]  # Limité à 2 documents
            
            for doc in docs_to_process:
                try:
                    content = doc.get("content", "")
                    if content:
                        entities = await asyncio.wait_for(
                            self.entity_extractor.extract_entities(
                                content[:1500],  # Contenu limité
                                entity_types=[EntityType.CONTROL, EntityType.REQUIREMENT],
                                framework_context=framework.value
                            ),
                            timeout=8  # 8 secondes par document
                        )
                        compliance_entities.extend(entities.get("control", []))
                        compliance_entities.extend(entities.get("requirement", []))
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout extraction entités pour {framework.value}")
                    continue
            
            # Calculer les métriques
            total_requirements = len(compliance_entities) or 1
            compliant_requirements = len([e for e in compliance_entities if e.get("status") == "compliant"])
            compliance_score = (compliant_requirements / total_requirements) * 100
            critical_gaps = len([e for e in compliance_entities if e.get("severity") == "critical"])
            
            # Déterminer le statut
            if compliance_score >= 90:
                status = ComplianceStatus.COMPLIANT
            elif compliance_score >= 70:
                status = ComplianceStatus.PARTIALLY_COMPLIANT
            else:
                status = ComplianceStatus.NON_COMPLIANT
            
            # Générer des insights AI simplifiés avec timeout
            try:
                insights_prompt = f"""
Analyse rapide conformité {framework.value}:
- Documents: {len(relevant_docs)}
- Entités: {len(compliance_entities)}  
- Score: {compliance_score:.1f}%

Fournis en 2-3 phrases:
1. Évaluation générale
2. Priorité d'amélioration
"""
                
                ai_insights_response = await asyncio.wait_for(
                    self.llm_client.generate_response(
                        messages=[
                            {"role": "system", "content": "Tu es un expert en conformité. Réponds de manière concise."},
                            {"role": "user", "content": insights_prompt}
                        ],
                        model="gpt-4.1",
                        temperature=0.2
                    ),
                    timeout=20  # 20 secondes maximum
                )
                
                ai_insights = {
                    "analysis": ai_insights_response,
                    "confidence": min(0.8, len(relevant_docs) * 0.15),
                    "entities_analyzed": len(compliance_entities),
                    "documents_consulted": len(relevant_docs)
                }
            except Exception as e:
                ai_insights = {
                    "analysis": f"Évaluation basique {framework.value}: score {compliance_score:.1f}%",
                    "confidence": 0.6,
                    "error": str(e)
                }
            
            # Créer l'évaluation
            assessment = ComplianceAssessment(
                framework=framework,
                overall_score=compliance_score,
                status=status,
                assessed_requirements=total_requirements,
                compliant_requirements=compliant_requirements,
                gap_count=total_requirements - compliant_requirements,
                critical_gaps=critical_gaps,
                assessment_date=datetime.now(),
                key_findings=[
                    f"Score: {compliance_score:.1f}%",
                    f"Entités: {len(compliance_entities)}",
                    f"Documents: {len(relevant_docs)}"
                ],
                recommendations=[
                    "Audit approfondi recommandé",
                    "Traitement gaps critiques",
                    "Amélioration continue"
                ],
                confidence_level=ai_insights["confidence"],
                ai_insights=ai_insights
            )
            
            return assessment
            
        except Exception as e:
            logger.error(f"Erreur évaluation {framework.value}: {str(e)}")
            return self._create_default_assessment(framework, str(e))

    def _create_default_assessment(self, framework: FrameworkType, error_reason: str) -> ComplianceAssessment:
        """Crée une évaluation par défaut en cas d'erreur ou timeout."""
        
        return ComplianceAssessment(
            framework=framework,
            overall_score=50.0,  # Score neutre par défaut
            status=ComplianceStatus.UNKNOWN,
            assessed_requirements=1,
            compliant_requirements=0,
            gap_count=1,
            critical_gaps=0,
            assessment_date=datetime.now(),
            key_findings=[f"Évaluation limitée: {error_reason}"],
            recommendations=[
                "Évaluation approfondie nécessaire",
                "Consultation expert recommandée",
                "Diagnostic manuel requis"
            ],
            confidence_level=0.3,
            ai_insights={
                "analysis": f"Évaluation {framework.value} interrompue. Diagnostic approfondi recommandé.",
                "confidence": 0.3,
                "error": error_reason,
                "fallback": True
            }
        )

    async def generate_regulatory_intelligence(
        self,
        frameworks: List[FrameworkType],
        geographic_scope: List[str],
        time_horizon: int = 12
    ) -> List[RegulatoryIntelligence]:
        """
        Génère une intelligence réglementaire pour les frameworks spécifiés.
        """
        logger.info(f"Generating regulatory intelligence for frameworks: {[f.value for f in frameworks]}")
        
        intelligence_reports = []
        
        for framework in frameworks:
            try:
                # Rechercher des documents sur les évolutions réglementaires
                relevant_docs = await self.document_finder.search_documents(
                    f"évolution réglementation {framework.value} nouveauté changement",
                    limit=5
                )
                
                # Générer l'intelligence réglementaire via LLM
                intelligence_prompt = f"""
Génère une intelligence réglementaire pour {framework.value}:

PÉRIMÈTRE:
- Frameworks: {framework.value}
- Scope géographique: {', '.join(geographic_scope)}
- Horizon temporel: {time_horizon} mois

SOURCES ANALYSÉES: {len(relevant_docs)} documents

En tant qu'expert en veille réglementaire, analyse:

1. ÉVOLUTIONS RÉCENTES (6 derniers mois):
   - Nouvelles réglementations
   - Amendements significatifs
   - Décisions d'autorités

2. CHANGEMENTS À VENIR (12 prochains mois):
   - Projets de réglementation
   - Dates d'entrée en vigueur
   - Périodes de transition

3. IMPACT ORGANISATIONNEL:
   - Évaluation de l'impact
   - Zones d'attention prioritaires
   - Risques de non-conformité

4. RECOMMANDATIONS STRATÉGIQUES:
   - Actions de préparation
   - Veille continue recommandée
   - Points de monitoring

Fournis une analyse structurée et prospective.
"""
                
                try:
                    intelligence_response = await self.llm_client.generate_response(
                        messages=[
                            {"role": "system", "content": self.system_prompts["regulatory_intelligence"]},
                            {"role": "user", "content": intelligence_prompt}
                        ],
                        model="gpt-4.1",
                        temperature=0.2
                    )
                except Exception as e:
                    intelligence_response = f"Intelligence réglementaire pour {framework.value} - analyse basée sur {len(relevant_docs)} sources documentaires."
                
                # Créer le rapport d'intelligence
                intelligence = RegulatoryIntelligence(
                    framework=framework,
                    recent_changes=[
                        {
                            "type": "analysis",
                            "description": f"Analyse basée sur {len(relevant_docs)} documents",
                            "date": datetime.now().isoformat(),
                            "impact": "medium"
                        }
                    ],
                    upcoming_changes=[
                        {
                            "type": "monitoring",
                            "description": f"Surveillance continue de {framework.value}",
                            "timeline": f"{time_horizon} mois",
                            "priority": "high"
                        }
                    ],
                    impact_assessment={
                        "overall_impact": "medium",
                        "confidence": min(0.8, len(relevant_docs) * 0.15),
                        "analysis": intelligence_response
                    },
                    preparation_recommendations=[
                        f"Surveiller les évolutions de {framework.value}",
                        "Maintenir la documentation à jour",
                        "Préparer les adaptations nécessaires"
                    ],
                    monitoring_priorities=[
                        f"Évolutions {framework.value}",
                        "Jurisprudence applicable",
                        "Guidance des autorités"
                    ],
                    last_updated=datetime.now(),
                    analysis_depth="standard",
                    sources_consulted=[doc.get("title", "Document") for doc in relevant_docs[:3]],
                    confidence_by_area={
                        "recent_changes": 0.7,
                        "upcoming_changes": 0.6,
                        "impact_assessment": 0.8
                    }
                )
                
                intelligence_reports.append(intelligence)
                logger.info(f"Intelligence report generated for {framework.value}")
                
            except Exception as e:
                logger.error(f"Error generating intelligence for {framework.value}: {str(e)}")
                # Créer un rapport par défaut en cas d'erreur
                intelligence = RegulatoryIntelligence(
                    framework=framework,
                    recent_changes=[],
                    upcoming_changes=[],
                    impact_assessment={"error": str(e)},
                    preparation_recommendations=["Réessayer la génération d'intelligence"],
                    monitoring_priorities=[f"Surveillance {framework.value}"],
                    last_updated=datetime.now(),
                    analysis_depth="error"
                )
                intelligence_reports.append(intelligence)
        
        return intelligence_reports

# Factory function
def get_compliance_analysis_module(llm_client: LLMClient = None):
    """Factory function pour obtenir une instance du module d'analyse de conformité."""
    return ComplianceAnalysisModule(llm_client=llm_client) 