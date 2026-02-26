"""
Risk Assessment Module - Module d'analyse des risques selon EBIOS/MEHARI avec capacités itératives.
Utilise les outils universels pour une évaluation complète des risques avec analyse progressive.
Intégré avec la configuration organisationnelle RegulAIte.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

from ..agent import Agent, AgentResponse, Query, QueryContext, IterationMode
from ..integrations.llm_integration import LLMIntegration, get_llm_client
from ..tools import (
    DocumentFinder, EntityExtractor, CrossReferenceTool, TemporalAnalyzer,
    EntityType, MetricType, RelationType
)
from .organization_config import get_organization_config_manager, OrganizationConfigManager
from ..agent_logger import AgentLogger, ActivityType, ActivityStatus, LogLevel

logger = logging.getLogger(__name__)

class RiskAssessmentMethodology(Enum):
    """Méthodologies d'évaluation des risques."""
    EBIOS = "ebios"
    MEHARI = "mehari"
    ISO27005 = "iso27005"
    NIST = "nist"
    CUSTOM = "custom"

class RiskTreatmentStrategy(Enum):
    """Stratégies de traitement des risques."""
    ACCEPT = "accept"
    MITIGATE = "mitigate"
    TRANSFER = "transfer"
    AVOID = "avoid"

@dataclass
class IterativeRiskContext:
    """Contexte pour l'analyse itérative des risques."""
    current_iteration: int = 0
    risk_analysis_progress: Dict[str, Any] = None
    knowledge_accumulator: Dict[str, List[str]] = None
    context_gaps_identified: List[str] = None
    scenarios_analyzed: List[str] = None
    depth_achieved: Dict[str, float] = None  # Profondeur atteinte par domaine de risque
    
    def __post_init__(self):
        if self.risk_analysis_progress is None:
            self.risk_analysis_progress = {}
        if self.knowledge_accumulator is None:
            self.knowledge_accumulator = {}
        if self.context_gaps_identified is None:
            self.context_gaps_identified = []
        if self.scenarios_analyzed is None:
            self.scenarios_analyzed = []
        if self.depth_achieved is None:
            self.depth_achieved = {}

@dataclass
class RiskScenario:
    """Scénario de risque EBIOS avec support itératif."""
    id: str
    name: str
    description: str
    threat_source: str
    threat_action: str
    vulnerability: str
    asset_affected: str
    likelihood: str  # very_low, low, medium, high, very_high
    impact: str     # very_low, low, medium, high, very_high
    risk_level: str  # calculated from likelihood and impact
    existing_controls: List[str]
    residual_risk: str
    treatment_strategy: RiskTreatmentStrategy
    action_plan: List[str]
    
    # Champs itératifs
    iteration_context: Optional[IterativeRiskContext] = None
    analysis_depth: float = 0.0
    confidence_score: float = 0.0
    requires_deeper_analysis: bool = False
    
    def __post_init__(self):
        if self.existing_controls is None:
            self.existing_controls = []
        if self.action_plan is None:
            self.action_plan = []

@dataclass
class RiskAssessmentReport:
    """Rapport d'évaluation des risques avec support itératif."""
    assessment_id: str
    organization_id: str
    methodology: RiskAssessmentMethodology
    scope: str
    assessment_date: datetime
    risk_scenarios: List[RiskScenario]
    risk_matrix: Dict[str, Any]
    control_effectiveness: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    executive_summary: str
    detailed_analysis: Dict[str, Any]
    organizational_context: Dict[str, Any]
    
    # Champs itératifs
    iteration_summary: Optional[Dict[str, Any]] = None
    sources_analyzed: List[Dict[str, Any]] = None
    analysis_completeness: float = 0.0
    
    def __post_init__(self):
        if self.sources_analyzed is None:
            self.sources_analyzed = []

class RiskAssessmentModule(Agent):
    """
    Module spécialisé d'évaluation des risques avec intégration organisationnelle.
    """
    
    def __init__(self, llm_client = None, agent_logger: AgentLogger = None, rag_system=None):
        super().__init__(
            agent_id="risk_assessment",
            name="Expert Évaluation des Risques Itératif"
        )
        
        self.llm_client = llm_client or get_llm_client()
        self.org_config: OrganizationConfigManager = get_organization_config_manager()
        self.agent_logger = agent_logger  # For detailed logging
        
        # Initialiser les outils universels
        self.document_finder = DocumentFinder(rag_system=rag_system)
        self.entity_extractor = EntityExtractor()
        self.cross_reference_tool = CrossReferenceTool()
        self.temporal_analyzer = TemporalAnalyzer()
        
        # Cache itératif
        self.iteration_contexts: Dict[str, IterativeRiskContext] = {}
        
        # Matrice de risques EBIOS
        self.risk_matrix = {
            "likelihood": {
                "very_low": 1,
                "low": 2, 
                "medium": 3,
                "high": 4,
                "very_high": 5
            },
            "impact": {
                "very_low": 1,
                "low": 2,
                "medium": 3, 
                "high": 4,
                "very_high": 5
            }
        }
        
        # Mapping des niveaux de risque
        self.risk_levels = {
            (1, 1): "very_low", (1, 2): "very_low", (1, 3): "low",
            (1, 4): "medium", (1, 5): "medium",
            (2, 1): "very_low", (2, 2): "low", (2, 3): "low", 
            (2, 4): "medium", (2, 5): "high",
            (3, 1): "low", (3, 2): "low", (3, 3): "medium",
            (3, 4): "high", (3, 5): "high",
            (4, 1): "medium", (4, 2): "medium", (4, 3): "high",
            (4, 4): "high", (4, 5): "very_high",
            (5, 1): "medium", (5, 2): "high", (5, 3): "high",
            (5, 4): "very_high", (5, 5): "very_high"
        }
        
        # Seuils pour l'analyse itérative des risques
        self.iteration_thresholds = {
            "min_confidence": 0.8,
            "completeness_target": 0.85,
            "scenario_coverage_min": 0.7,
            "risk_depth_min": 0.75
        }
        
        # Prompts spécialisés avec support itératif
        self.system_prompt = """
Tu es un expert en évaluation des risques cybersécurité selon les méthodologies EBIOS RM et MEHARI avec capacités d'analyse itérative.
Tu maîtrises parfaitement :
- L'identification et la qualification des actifs
- L'analyse des sources de menaces et des modes opératoires
- L'évaluation de la vraisemblance et de l'impact
- La cartographie des risques et scénarios stratégiques
- Les mesures de sécurité et leur efficacité
- L'adaptation aux contextes organisationnels spécifiques

CAPACITÉS ITÉRATIVES:
- Analyse progressive des scenarios de risque par ordre de priorité
- Identification des gaps de contexte nécessitant plus d'informations
- Accumulation de connaissances à travers les itérations
- Reformulation des requêtes pour approfondir l'analyse des risques
- Évaluation continue de la complétude de l'évaluation

Tu tiens compte du contexte organisationnel (secteur, taille, maturité) pour personnaliser tes analyses.
Pour chaque analyse, tu évalues si plus de contexte améliorerait la précision de l'évaluation des risques.
Réponds TOUJOURS en français avec une approche méthodique et structurée.
"""

    async def _log_tool_execution(self, tool_name: str, tool_params: Dict[str, Any], 
                                 result: Any, execution_time_ms: float = None, 
                                 error: str = None) -> None:
        """Helper method to log tool executions."""
        if self.agent_logger:
            import time
            start_time = time.time()
            
            status = ActivityStatus.COMPLETED if error is None else ActivityStatus.FAILED
            await self.agent_logger.log_tool_execution(
                agent_id=self.agent_id,
                agent_name=self.name,
                tool_id=tool_name,
                tool_params=tool_params,
                result=result,
                status=status,
                execution_time_ms=execution_time_ms or ((time.time() - start_time) * 1000),
                error=error
            )

    async def process_query(self, query: Query) -> AgentResponse:
        """
        Traite une requête d'évaluation des risques avec capacités itératives.
        """
        import time
        process_start = time.time()
        
        logger.info(f"Traitement requête risques itérative: {query.query_text}")
        
        # Log query processing start
        if self.agent_logger:
            await self.agent_logger.log_activity(
                agent_id=self.agent_id,
                agent_name=self.name,
                activity_type=ActivityType.QUERY_ANALYSIS,
                status=ActivityStatus.STARTED,
                level=LogLevel.INFO,
                message="Starting risk assessment query processing",
                details={
                    "query": query.query_text,
                    "parameters": query.parameters,
                    "context": query.context.metadata if query.context else {},
                    "step": "risk_query_start"
                }
            )
        
        # Initialiser ou récupérer le contexte itératif
        session_id = query.context.session_id if query.context else "default"
        if session_id not in self.iteration_contexts:
            self.iteration_contexts[session_id] = IterativeRiskContext()
        
        iteration_ctx = self.iteration_contexts[session_id]
        iteration_ctx.current_iteration += 1
        
        # Log iteration context
        if self.agent_logger:
            await self.agent_logger.log_activity(
                agent_id=self.agent_id,
                agent_name=self.name,
                activity_type=ActivityType.ITERATION,
                status=ActivityStatus.IN_PROGRESS,
                level=LogLevel.INFO,
                message=f"Initialized iteration context - iteration {iteration_ctx.current_iteration}",
                details={
                    "iteration_number": iteration_ctx.current_iteration,
                    "scenarios_analyzed": iteration_ctx.scenarios_analyzed,
                    "context_gaps": iteration_ctx.context_gaps_identified,
                    "knowledge_areas": list(iteration_ctx.knowledge_accumulator.keys()),
                    "step": "iteration_context_initialized"
                }
            )
        
        # Extraire l'ID d'organisation du contexte
        org_id = self._extract_organization_id(query)
        
        # Log organization identification
        if self.agent_logger:
            await self.agent_logger.log_activity(
                agent_id=self.agent_id,
                agent_name=self.name,
                activity_type=ActivityType.QUERY_ANALYSIS,
                status=ActivityStatus.IN_PROGRESS,
                level=LogLevel.INFO,
                message="Identified organization context",
                details={
                    "organization_id": org_id,
                    "extraction_source": "query context metadata",
                    "step": "organization_identified"
                }
            )
        
        # Analyser le type de demande avec contexte itératif
        analysis_start = time.time()
        analysis_type = await self._analyze_request_type_with_iterative_context(
            query.query_text, iteration_ctx, query.parameters
        )
        analysis_time = (time.time() - analysis_start) * 1000
        
        # Log analysis type determination
        if self.agent_logger:
            await self.agent_logger.log_activity(
                agent_id=self.agent_id,
                agent_name=self.name,
                activity_type=ActivityType.QUERY_ANALYSIS,
                status=ActivityStatus.COMPLETED,
                level=LogLevel.INFO,
                message="Determined risk analysis type",
                details={
                    "analysis_type": analysis_type,
                    "available_types": ["full_assessment", "scenario_analysis", "control_evaluation", "trend_analysis", "general_analysis"],
                    "step": "analysis_type_determined"
                },
                execution_time_ms=analysis_time
            )
        
        # Traitement basé sur l'intention et le mode itératif
        processing_start = time.time()
        try:
            if query.iteration_mode in [IterationMode.ITERATIVE, IterationMode.DEEP_ANALYSIS]:
                # Log iterative processing
                if self.agent_logger:
                    await self.agent_logger.log_activity(
                        agent_id=self.agent_id,
                        agent_name=self.name,
                        activity_type=ActivityType.DECISION_MAKING,
                        status=ActivityStatus.IN_PROGRESS,
                        level=LogLevel.INFO,
                        message="Selected iterative risk processing approach",
                        details={
                            "iteration_mode": str(query.iteration_mode),
                            "analysis_type": analysis_type,
                            "step": "iterative_approach_selected"
                        }
                    )
                result = await self._process_iterative_risk_query(query, analysis_type, iteration_ctx, org_id)
            else:
                # Log standard processing
                if self.agent_logger:
                    await self.agent_logger.log_activity(
                        agent_id=self.agent_id,
                        agent_name=self.name,
                        activity_type=ActivityType.DECISION_MAKING,
                        status=ActivityStatus.IN_PROGRESS,
                        level=LogLevel.INFO,
                        message="Selected standard risk processing approach",
                        details={
                            "analysis_type": analysis_type,
                            "step": "standard_approach_selected"
                        }
                    )
                result = await self._process_standard_risk_query(query, analysis_type, org_id)
            
            processing_time = (time.time() - processing_start) * 1000
            total_time = (time.time() - process_start) * 1000
            
            # Log successful completion
            if self.agent_logger:
                await self.agent_logger.log_activity(
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    activity_type=ActivityType.SYNTHESIS,
                    status=ActivityStatus.COMPLETED,
                    level=LogLevel.INFO,
                    message="Completed risk assessment query processing",
                    details={
                        "result_length": len(result.content),
                        "tools_used": result.tools_used,
                        "sources_count": len(result.sources),
                        "confidence": result.confidence,
                        "total_processing_time_ms": total_time,
                        "step": "risk_query_completed"
                    },
                    execution_time_ms=processing_time
                )
            
            return result
            
        except Exception as e:
            processing_time = (time.time() - processing_start) * 1000
            
            # Log error
            if self.agent_logger:
                await self.agent_logger.log_activity(
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    activity_type=ActivityType.ERROR_HANDLING,
                    status=ActivityStatus.FAILED,
                    level=LogLevel.ERROR,
                    message="Risk assessment query processing failed",
                    details={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "analysis_type": analysis_type,
                        "step": "risk_query_error"
                    },
                    execution_time_ms=processing_time
                )
            
            raise

    async def _process_iterative_risk_query(self, query: Query, 
                                          analysis_type: str,
                                          iteration_ctx: IterativeRiskContext,
                                          org_id: str) -> AgentResponse:
        """
        Traite une requête de risques avec approche itérative.
        """
        logger.info(f"Analyse itérative des risques - Itération {iteration_ctx.current_iteration}")
        
        # 1. Évaluer les connaissances accumulées sur les risques
        knowledge_assessment = await self._assess_accumulated_risk_knowledge(
            query, iteration_ctx, analysis_type, org_id
        )
        
        # 2. Identifier les scenarios à analyser dans cette itération
        scenarios_to_analyze = await self._prioritize_risk_scenarios_for_iteration(
            query, iteration_ctx, knowledge_assessment, org_id
        )
        
        # 3. Analyser les scenarios prioritaires
        scenario_analysis_results = await self._analyze_risk_scenarios_iteratively(
            scenarios_to_analyze, query, iteration_ctx, org_id
        )
        
        # 4. Intégrer les nouvelles connaissances sur les risques
        updated_knowledge = await self._integrate_new_risk_knowledge(
            scenario_analysis_results, iteration_ctx, analysis_type
        )
        
        # 5. Évaluer la complétude de l'évaluation des risques
        completeness_assessment = await self._assess_risk_analysis_completeness(
            query, iteration_ctx, updated_knowledge
        )
        
        # 6. Générer la réponse avec recommandations d'itération
        if analysis_type == "full_assessment":
            return await self._perform_iterative_full_risk_assessment(
                query, analysis_type, iteration_ctx, completeness_assessment, org_id
            )
        elif analysis_type == "scenario_analysis":
            return await self._perform_iterative_scenario_analysis(
                query, analysis_type, iteration_ctx, completeness_assessment, org_id
            )
        elif analysis_type == "control_evaluation":
            return await self._perform_iterative_control_evaluation(
                query, analysis_type, iteration_ctx, completeness_assessment, org_id
            )
        else:
            return await self._general_iterative_risk_analysis(
                query, analysis_type, iteration_ctx, completeness_assessment, org_id
            )

    async def _process_standard_risk_query(self, query: Query, analysis_type: str, org_id: str) -> AgentResponse:
        """
        Traite une requête de risques standard (non-itérative).
        """
        if analysis_type == "full_assessment":
            # Create a basic iterative context for full assessment
            iteration_ctx = IterativeRiskContext()
            return await self._perform_iterative_full_risk_assessment(query, analysis_type, iteration_ctx, {}, org_id)
        elif analysis_type == "scenario_analysis":
            # Create a basic iterative context for scenario analysis
            iteration_ctx = IterativeRiskContext()
            return await self._perform_iterative_scenario_analysis(query, analysis_type, iteration_ctx, {}, org_id)
        elif analysis_type == "control_evaluation":
            return await self._evaluate_controls_effectiveness(query, org_id)
        elif analysis_type == "trend_analysis":
            return await self._analyze_risk_trends(query, org_id)
        else:
            return await self._general_risk_analysis(query, org_id)
    
    async def _general_risk_analysis(self, query: Query, org_id: str) -> AgentResponse:
        """
        Effectue une analyse générale des risques.
        """
        # Create a basic iterative context for general analysis
        iteration_ctx = IterativeRiskContext()
        
        # Perform general iterative risk analysis
        return await self._general_iterative_risk_analysis(
            query, "general_analysis", iteration_ctx, {}, org_id
        )

    async def _evaluate_controls_effectiveness(self, query: Query, org_id: str) -> AgentResponse:
        """
        Évalue l'efficacité des contrôles de sécurité.
        """
        logger.info(f"Évaluation efficacité contrôles pour organisation: {org_id}")
        
        # Rechercher les documents pertinents sur les contrôles
        relevant_docs = await self.document_finder.search_documents(
            query=f"contrôles sécurité efficacité évaluation {query.query_text}",
            limit=10
        )
        
        # Extraire les entités de contrôles
        control_entities = []
        for doc in relevant_docs[:10]:
            try:
                entities = await self.entity_extractor.extract_controls(
                    doc.get("content", ""), 
                    framework="ISO27001"
                )
                control_entities.extend(entities)
            except Exception as e:
                logger.warning(f"Erreur extraction contrôles: {str(e)}")
        
        # Analyser l'efficacité des contrôles avec LLM
        controls_analysis_prompt = f"""
Analyse l'efficacité des contrôles de sécurité pour: "{query.query_text}"

CONTRÔLES IDENTIFIÉS: {len(control_entities)}
DOCUMENTS ANALYSÉS: {len(relevant_docs)}

En tant qu'expert en analyse de risques, évalue:

1. EFFICACITÉ DES CONTRÔLES EXISTANTS:
   - Contrôles préventifs (efficacité, couverture)
   - Contrôles détectifs (réactivité, précision)
   - Contrôles correctifs (rapidité, efficacité)

2. ÉVALUATION DE LA PERFORMANCE:
   - Indicateurs de performance des contrôles
   - Taux de détection et faux positifs
   - Temps de réaction et de correction

3. ANALYSE DES GAPS:
   - Contrôles manquants ou insuffisants
   - Zones non couvertes par les contrôles
   - Risques résiduels non traités

4. RECOMMANDATIONS D'AMÉLIORATION:
   - Optimisation des contrôles existants
   - Nouveaux contrôles recommandés
   - Plan de renforcement prioritaire

Fournis une analyse détaillée avec recommandations concrètes.
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": controls_analysis_prompt}
                ],
                model="gpt-4.1",
                temperature=0.2
            )
            
            return AgentResponse(
                content=response,
                tools_used=["document_finder", "entity_extractor"],
                context_used=True,
                sources=self.format_documents_as_sources(relevant_docs[:5]),
                metadata={
                    "documents_analyzed": len(relevant_docs),
                    "controls_evaluated": len(control_entities),
                    "analysis_type": "control_effectiveness"
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation des contrôles: {str(e)}")
            return AgentResponse(
                content=f"Erreur lors de l'évaluation de l'efficacité des contrôles: {str(e)}",
                tools_used=["document_finder", "entity_extractor"],
                context_used=False,
                sources=[],
                metadata={"error": str(e)}
            )

    async def _analyze_risk_trends(self, query: Query, org_id: str) -> AgentResponse:
        """
        Analyse les tendances des risques dans le temps.
        """
        logger.info(f"Analyse tendances risques pour organisation: {org_id}")
        
        # Rechercher les documents historiques sur les risques
        relevant_docs = await self.document_finder.search_documents(
            query=f"risques tendances évolution historique {query.query_text}",
            limit=10
        )
        
        # Analyser les tendances avec LLM
        trends_analysis_prompt = f"""
Analyse les tendances des risques pour: "{query.query_text}"

DOCUMENTS ANALYSÉS: {len(relevant_docs)}

En tant qu'expert en analyse de risques, analyse:

1. ÉVOLUTION HISTORIQUE DES RISQUES:
   - Nouveaux risques émergents
   - Risques en augmentation/diminution
   - Tendances sectorielles observées

2. ANALYSE TEMPORELLE:
   - Patterns cycliques ou saisonniers
   - Corrélations avec événements externes
   - Vitesse d'évolution des menaces

3. FACTEURS D'INFLUENCE:
   - Changements technologiques
   - Évolutions réglementaires
   - Transformations organisationnelles

4. PRÉDICTIONS ET RECOMMANDATIONS:
   - Risques à surveiller
   - Mesures préventives recommandées
   - Stratégies d'adaptation

Fournis une analyse des tendances avec projections et recommandations.
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": trends_analysis_prompt}
                ],
                model="gpt-4.1",
                temperature=0.2
            )
            
            return AgentResponse(
                content=response,
                tools_used=["document_finder", "temporal_analyzer"],
                context_used=True,
                sources=self.format_documents_as_sources(relevant_docs[:5]),
                metadata={
                    "documents_analyzed": len(relevant_docs),
                    "analysis_type": "risk_trends"
                }
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse des tendances: {str(e)}")
            return AgentResponse(
                content=f"Erreur lors de l'analyse des tendances de risques: {str(e)}",
                tools_used=["document_finder", "temporal_analyzer"],
                context_used=False,
                sources=[],
                metadata={"error": str(e)}
            )

    async def _analyze_request_type_with_iterative_context(self, query_text: str,
                                                         iteration_ctx: IterativeRiskContext,
                                                         parameters: Dict[str, Any]) -> str:
        """Analyse le type de demande d'évaluation des risques avec contexte itératif."""
        
        analysis_prompt = f"""
Analyse cette demande d'évaluation des risques avec contexte itératif:

DEMANDE: "{query_text}"
ITÉRATION: {iteration_ctx.current_iteration}

CONTEXTE ACCUMULÉ:
- Scenarios déjà analysés: {iteration_ctx.scenarios_analyzed}
- Gaps identifiés: {iteration_ctx.context_gaps_identified}
- Connaissances acquises: {list(iteration_ctx.knowledge_accumulator.keys())}
- Profondeur atteinte: {iteration_ctx.depth_achieved}

Détermine le type d'analyse de risques demandé:
- full_assessment: Évaluation complète des risques
- scenario_analysis: Analyse de scenarios spécifiques
- control_evaluation: Évaluation de l'efficacité des contrôles
- trend_analysis: Analyse des tendances de risques
- general_analysis: Analyse générale

Retourne uniquement le type d'analyse identifié.
"""

        # Log LLM prompt being sent
        if self.agent_logger:
            await self.agent_logger.log_activity(
                agent_id=self.agent_id,
                agent_name=self.name,
                activity_type=ActivityType.QUERY_ANALYSIS,
                status=ActivityStatus.IN_PROGRESS,
                level=LogLevel.INFO,
                message="Sending analysis type determination prompt to LLM",
                details={
                    "llm_prompt": analysis_prompt,
                    "system_prompt": self.system_prompt,
                    "model": "gpt-4.1",
                    "temperature": 0.1,
                    "step": "analysis_type_llm_prompt"
                }
            )

        try:
            import time
            llm_start = time.time()
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                model="gpt-4.1",
                temperature=0.1
            )
            llm_time = (time.time() - llm_start) * 1000
            
            # Log LLM response received
            if self.agent_logger:
                await self.agent_logger.log_activity(
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    activity_type=ActivityType.QUERY_ANALYSIS,
                    status=ActivityStatus.IN_PROGRESS,
                    level=LogLevel.INFO,
                    message="Received LLM response for analysis type determination",
                    details={
                        "llm_response": response,
                        "response_length": len(response),
                        "step": "analysis_type_llm_response"
                    },
                    execution_time_ms=llm_time
                )
            
            analysis_type = response.strip().lower()
            
            # Valider le type d'analyse
            valid_types = ["full_assessment", "scenario_analysis", "control_evaluation", "trend_analysis", "general_analysis"]
            if analysis_type in valid_types:
                validated_type = analysis_type
            else:
                validated_type = "general_analysis"
            
            # Log validation result
            if self.agent_logger:
                await self.agent_logger.log_activity(
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    activity_type=ActivityType.QUERY_ANALYSIS,
                    status=ActivityStatus.COMPLETED,
                    level=LogLevel.INFO,
                    message="Validated analysis type",
                    details={
                        "raw_response": analysis_type,
                        "validated_type": validated_type,
                        "valid_types": valid_types,
                        "was_valid": validated_type == analysis_type,
                        "step": "analysis_type_validated"
                    }
                )
            
            return validated_type
                
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du type de requête: {str(e)}")
            
            # Log error
            if self.agent_logger:
                await self.agent_logger.log_activity(
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    activity_type=ActivityType.ERROR_HANDLING,
                    status=ActivityStatus.FAILED,
                    level=LogLevel.ERROR,
                    message="Failed to determine analysis type",
                    details={
                        "error": str(e),
                        "error_type": type(e).__name__,
                        "fallback_type": "general_analysis",
                        "step": "analysis_type_error"
                    }
                )
            
            return "general_analysis"

    async def perform_ebios_assessment(
        self,
        scope: str,
        org_id: str = None,
        assets: List[Dict[str, Any]] = None,
        methodology: RiskAssessmentMethodology = RiskAssessmentMethodology.EBIOS
    ) -> RiskAssessmentReport:
        """
        Effectue une évaluation EBIOS complète avec contexte organisationnel.
        """
        logger.info(f"Évaluation EBIOS pour le périmètre: {scope}, organisation: {org_id}")
        
        assessment_id = f"ebios_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Récupérer le contexte organisationnel
        org_context = self._get_organizational_context(org_id)
        
        # Étape 1: Identifier et qualifier les actifs (adaptés à l'organisation)
        if not assets:
            assets = await self._identify_organizational_assets(scope, org_id)
        
        # Étape 2: Identifier les sources de menaces (selon profil organisationnel)
        threat_sources = await self._identify_organizational_threats(assets, org_id)
        
        # Étape 3: Analyser les scenarios de risques
        risk_scenarios = await self._generate_risk_scenarios(
            assets, threat_sources, org_context
        )
        
        # Étape 4: Évaluer les contrôles existants
        control_effectiveness = await self._evaluate_existing_controls(
            risk_scenarios, org_context
        )
        
        # Étape 5: Calculer les risques résiduels
        for scenario in risk_scenarios:
            scenario.residual_risk = self._calculate_residual_risk(
                scenario, control_effectiveness, org_context
            )
        
        # Étape 6: Générer la matrice de risques
        risk_matrix = self._generate_risk_matrix(risk_scenarios)
        
        # Étape 7: Recommandations de traitement (adaptées au contexte)
        recommendations = await self._generate_treatment_recommendations(
            risk_scenarios, org_context
        )
        
        # Étape 8: Synthèse exécutive
        executive_summary = await self._generate_executive_summary(
            risk_scenarios, recommendations, org_context
        )
        
        # Analyse détaillée
        detailed_analysis = {
            "assets_analysis": assets,
            "threat_landscape": threat_sources,
            "scenarios_details": [vars(s) for s in risk_scenarios],
            "control_assessment": control_effectiveness,
            "organizational_factors": org_context
        }
        
        return RiskAssessmentReport(
            assessment_id=assessment_id,
            organization_id=org_id or "default",
            methodology=methodology,
            scope=scope,
            assessment_date=datetime.now(),
            risk_scenarios=risk_scenarios,
            risk_matrix=risk_matrix,
            control_effectiveness=control_effectiveness,
            recommendations=recommendations,
            executive_summary=executive_summary,
            detailed_analysis=detailed_analysis,
            organizational_context=org_context
        )

    def _extract_organization_id(self, query: Query) -> Optional[str]:
        """Extrait l'ID d'organisation du contexte de la requête."""
        if query.context and query.context.metadata:
            return query.context.metadata.get("organization_id") or query.context.metadata.get("org_id")
        return None
    
    def _get_organizational_context(self, org_id: str) -> Dict[str, Any]:
        """Récupère le contexte organisationnel complet."""
        if not org_id:
            return {"organization_type": "general", "sector": "technology", "size": "medium"}
        
        # Récupérer les différents contextes depuis le gestionnaire
        regulatory_context = self.org_config.get_regulatory_context(org_id)
        governance_context = self.org_config.get_governance_context(org_id)
        
        return {
            "organization_id": org_id,
            "regulatory": regulatory_context,
            "governance": governance_context,
            "size": governance_context.get("size", "medium"),
            "sector": regulatory_context.get("sector", "technology"),
            "risk_appetite": governance_context.get("risk_appetite", "moderate"),
            "maturity": governance_context.get("maturity", {})
        }

    async def _identify_organizational_assets(
        self, 
        scope: str, 
        org_id: str
    ) -> List[Dict[str, Any]]:
        """Identifie les actifs selon le profil organisationnel."""
        
        # Récupérer les actifs configurés pour l'organisation
        org_assets = self.org_config.get_organization_assets(org_id, scope)
        
        if org_assets:
            logger.info(f"Actifs organisationnels trouvés: {len(org_assets)}")
            return org_assets
        
        # Fallback: rechercher des documents pertinents
        relevant_docs = await self.document_finder.search_documents(
            f"actifs {scope} inventaire",
            limit=20
        )
        
        assets = []
        for doc in relevant_docs:
            content = doc.get("content", "")
            if content:
                doc_assets = await self.entity_extractor.extract_entities(
                    content,
                    entity_types=[EntityType.ASSET]
                )
                assets.extend(doc_assets.get("asset", []))
        
        # Si toujours pas d'actifs, utiliser les defaults organisationnels
        return assets if assets else self.org_config._get_default_assets()

    async def _identify_organizational_threats(
        self, 
        assets: List[Dict[str, Any]], 
        org_id: str
    ) -> List[Dict[str, Any]]:
        """Identifie les sources de menaces selon le profil organisationnel."""
        
        # Récupérer le paysage de menaces organisationnel
        org_threats = self.org_config.get_threat_landscape(org_id)
        
        if org_threats:
            logger.info(f"Menaces organisationnelles trouvées: {len(org_threats)}")
            return org_threats
        
        # Fallback: analyse par LLM avec contexte organisationnel
        org_context = self._get_organizational_context(org_id)
        
        threat_prompt = f"""
Identifie les sources de menaces selon EBIOS RM pour cette organisation:

CONTEXTE ORGANISATIONNEL:
- Secteur: {org_context.get('sector', 'technology')}
- Taille: {org_context.get('size', 'medium')}
- Appétit au risque: {org_context.get('risk_appetite', 'moderate')}
- Frameworks réglementaires: {org_context.get('regulatory', {}).get('frameworks', [])}

ACTIFS ORGANISATIONNELS:
{json.dumps(assets[:10], indent=2, default=str)[:2000]}

Adapte l'identification des menaces au profil spécifique de cette organisation.
Considère les menaces sectorielles pertinentes et les contraintes réglementaires.

Retourne un JSON structuré avec les sources de menaces spécifiques.
"""
        
        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": threat_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_content = response[json_start:json_end]
            threats = json.loads(json_content).get("threat_sources", [])
            return threats
        except Exception as e:
            logger.error(f"Erreur parsing menaces organisationnelles: {str(e)}")
            return self.org_config._get_default_threats()

    # Mise à jour des méthodes privées pour intégrer le contexte organisationnel
    async def _generate_risk_scenarios(
        self,
        assets: List[Dict[str, Any]],
        threat_sources: List[Dict[str, Any]],
        org_context: Dict[str, Any]
    ) -> List[RiskScenario]:
        """Génère les scénarios de risque avec contexte organisationnel."""
        scenarios = []
        scenario_id = 1
        
        # Limiter selon la taille de l'organisation
        max_assets = self._get_max_assets_for_org_size(org_context.get("size", "medium"))
        max_threats = self._get_max_threats_for_org_size(org_context.get("size", "medium"))
        
        for asset in assets[:max_assets]:
            for threat in threat_sources[:max_threats]:
                scenario_data = await self._create_risk_scenario_with_context(
                    asset, threat, scenario_id, org_context
                )
                
                if scenario_data:
                    scenarios.append(scenario_data)
                    scenario_id += 1
        
        return scenarios

    def _get_max_assets_for_org_size(self, size: str) -> int:
        """Détermine le nombre max d'actifs selon la taille de l'organisation."""
        size_limits = {
            "startup": 5,
            "small": 8,
            "medium": 12,
            "large": 20,
            "enterprise": 30
        }
        return size_limits.get(size, 10)
    
    def _get_max_threats_for_org_size(self, size: str) -> int:
        """Détermine le nombre max de menaces selon la taille de l'organisation."""
        size_limits = {
            "startup": 3,
            "small": 4,
            "medium": 5,
            "large": 6,
            "enterprise": 8
        }
        return size_limits.get(size, 5)

    async def _create_risk_scenario_with_context(
        self,
        asset: Dict[str, Any],
        threat_source: Dict[str, Any],
        scenario_id: int,
        org_context: Dict[str, Any]
    ) -> Optional[RiskScenario]:
        """Crée un scénario de risque avec contexte organisationnel."""
        
        scenario_prompt = f"""
Crée un scénario de risque EBIOS détaillé adapté à ce contexte organisationnel:

CONTEXTE ORGANISATIONNEL:
- Secteur: {org_context.get('sector', 'technology')}
- Taille: {org_context.get('size', 'medium')}
- Maturité sécurité: {org_context.get('maturity', {}).get('security', 'developing')}
- Appétit au risque: {org_context.get('risk_appetite', 'moderate')}

ACTIF CIBLE:
{json.dumps(asset, indent=2, default=str)}

SOURCE DE MENACE:
{json.dumps(threat_source, indent=2, default=str)}

Adapte le scénario aux spécificités organisationnelles:
- Contraintes sectorielles
- Niveau de maturité
- Ressources disponibles
- Contexte réglementaire

Retourne un JSON structuré avec le scénario adapté.
"""
        
        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": scenario_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_content = response[json_start:json_end]
            data = json.loads(json_content)
            
            # Calculer le niveau de risque avec ajustement contextuel
            likelihood_val = self.risk_matrix["likelihood"].get(data.get("likelihood", "medium"), 3)
            impact_val = self.risk_matrix["impact"].get(data.get("impact", "medium"), 3)
            
            # Ajustement selon le contexte organisationnel
            if org_context.get("risk_appetite") == "conservative":
                likelihood_val = min(5, likelihood_val + 1)  # Plus conservateur
            elif org_context.get("risk_appetite") == "aggressive":
                likelihood_val = max(1, likelihood_val - 1)  # Moins conservateur
            
            risk_level = self.risk_levels.get((likelihood_val, impact_val), "medium")
            
            return RiskScenario(
                id=f"RS-{scenario_id:03d}",
                name=data.get("name", f"Scénario {scenario_id}"),
                description=data.get("description", ""),
                threat_source=threat_source.get("name", ""),
                threat_action=data.get("threat_action", ""),
                vulnerability=data.get("vulnerability", ""),
                asset_affected=asset.get("name", ""),
                likelihood=data.get("likelihood", "medium"),
                impact=data.get("impact", "medium"),
                risk_level=risk_level,
                existing_controls=[],
                residual_risk="",
                treatment_strategy=RiskTreatmentStrategy.MITIGATE,
                action_plan=[]
            )
            
        except Exception as e:
            logger.error(f"Erreur création scénario contextuel: {str(e)}")
            return self._create_fallback_scenario(asset, threat_source, scenario_id, e)
    
    def _create_fallback_scenario(
        self, 
        asset: Dict[str, Any], 
        threat_source: Dict[str, Any], 
        scenario_id: int, 
        error: Exception
    ) -> RiskScenario:
        """Crée un scénario de fallback en cas d'erreur."""
        return RiskScenario(
            id=f"RS-ERROR-{scenario_id:03d}",
            name=f"⚠️ ERREUR: Scénario {scenario_id} - Génération échouée",
            description=f"Échec de la génération automatique du scénario par LLM: {str(error)}",
            threat_source=threat_source.get("name", "Source inconnue"),
            threat_action="Action à déterminer manuellement",
            vulnerability="Vulnérabilité à identifier manuellement",
            asset_affected=asset.get("name", "Actif inconnu"),
            likelihood="medium",
            impact="medium",
            risk_level="medium",
            existing_controls=[],
            residual_risk="À évaluer manuellement",
            treatment_strategy=RiskTreatmentStrategy.MITIGATE,
            action_plan=[
                "⚠️ Scénario généré automatiquement échoué",
                "Analyser manuellement le risque entre cet actif et cette menace",
                "Consulter un expert en analyse de risques",
                "Réviser les données d'entrée et réessayer"
            ]
        )

    # Resto des méthodes existantes avec mise à jour pour le contexte organisationnel...
    # [Les autres méthodes restent largement similaires mais avec intégration du contexte org]

    async def _assess_accumulated_risk_knowledge(self, query: Query, 
                                               iteration_ctx: IterativeRiskContext,
                                               analysis_type: str, org_id: str) -> Dict[str, Any]:
        """Évalue les connaissances accumulées sur les risques."""
        assessment_prompt = f"""
Évalue les connaissances accumulées pour cette analyse de risques itérative.

REQUÊTE: "{query.query_text}"
ITÉRATION: {iteration_ctx.current_iteration}
TYPE D'ANALYSE: {analysis_type}

CONNAISSANCES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

SCENARIOS ANALYSÉS: {iteration_ctx.scenarios_analyzed}
PROFONDEUR ATTEINTE: {iteration_ctx.depth_achieved}

Évalue:
1. La pertinence des scenarios déjà analysés
2. Les domaines de risque bien couverts vs. manquants
3. La qualité des évaluations de vraisemblance/impact
4. Les gaps de contexte restants
5. La cohérence des mesures de sécurité identifiées

Réponds au format JSON:
{{
    "risk_knowledge_quality": 0.0-1.0,
    "scenario_coverage": {{
        "well_covered_risks": ["risk1", "risk2"],
        "gaps_identified": ["gap1", "gap2"],
        "coverage_by_domain": {{"cyber": 0.8, "operational": 0.6}}
    }},
    "assessment_reliability": 0.0-1.0,
    "consistency_score": 0.0-1.0,
    "actionable_insights": ["insight1", "insight2"],
    "priority_gaps": ["high_priority_gap1", "high_priority_gap2"]
}}
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": assessment_prompt}
                ],
                model="gpt-4.1",
                temperature=0.1
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation des connaissances risques: {str(e)}")
            return {
                "risk_knowledge_quality": 0.5,
                "scenario_coverage": {"well_covered_risks": [], "gaps_identified": ["error_in_assessment"]},
                "assessment_reliability": 0.5,
                "consistency_score": 0.5,
                "actionable_insights": [],
                "priority_gaps": ["assessment_error"]
            }

    async def _prioritize_risk_scenarios_for_iteration(self, query: Query,
                                                     iteration_ctx: IterativeRiskContext,
                                                     knowledge_assessment: Dict[str, Any],
                                                     org_id: str) -> List[str]:
        """Priorise les scenarios de risque à analyser dans cette itération."""
        try:
            # Identifier les scenarios pertinents pour l'organisation
            org_context = self._get_organizational_context(org_id)
            
            prioritization_criteria = {
                "query": query.query_text,
                "organization_context": org_context,
                "focus_areas": knowledge_assessment.get("priority_gaps", []),
                "exclude_analyzed": iteration_ctx.scenarios_analyzed
            }
            
            # Recherche de scenarios à analyser
            scenarios_found = await self._identify_priority_risk_scenarios(
                prioritization_criteria,
                max_scenarios=3,  # Limiter pour cette itération
                org_id=org_id
            )
            
            return scenarios_found
            
        except Exception as e:
            logger.error(f"Erreur lors de la priorisation des scenarios: {str(e)}")
            return []

    async def _identify_priority_risk_scenarios(self, criteria: Dict[str, Any], 
                                              max_scenarios: int, org_id: str) -> List[str]:
        """Identifie les scenarios de risque prioritaires à analyser."""
        org_context = self._get_organizational_context(org_id)
        
        scenario_identification_prompt = f"""
Identifie les scenarios de risque prioritaires à analyser pour cette organisation.

CRITÈRES DE RECHERCHE:
{json.dumps(criteria, indent=2, ensure_ascii=False)}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2, ensure_ascii=False)}

MÉTHODOLOGIE: Utilise EBIOS RM pour identifier les scenarios les plus pertinents.

Identifie les {max_scenarios} scenarios de risque les plus critiques à analyser:
1. Menaces les plus probables pour ce secteur
2. Vulnérabilités typiques de ce type d'organisation
3. Actifs les plus sensibles à protéger
4. Scenarios non couverts précédemment

Réponds avec une liste de scenarios au format:
["scenario_1_description", "scenario_2_description", "scenario_3_description"]
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": scenario_identification_prompt}
                ],
                model="gpt-4.1",
                temperature=0.2
            )
            
            if response.strip().startswith('[') and response.strip().endswith(']'):
                scenarios = json.loads(response.strip())
                return scenarios[:max_scenarios]
            
            return []
            
        except Exception as e:
            logger.error(f"Erreur lors de l'identification des scenarios: {str(e)}")
            return [f"Scenario générique {i+1}" for i in range(max_scenarios)]

    async def _analyze_risk_scenarios_iteratively(self, scenarios_to_analyze: List[str],
                                                 query: Query,
                                                 iteration_ctx: IterativeRiskContext,
                                                 org_id: str) -> Dict[str, Any]:
        """Analyse les scenarios de risque de manière itérative."""
        analysis_results = {}
        org_context = self._get_organizational_context(org_id)
        
        for scenario_desc in scenarios_to_analyze:
            try:
                # Analyser le scenario avec contexte organisationnel
                scenario_analysis = await self._analyze_single_risk_scenario_with_context(
                    scenario_desc, query, iteration_ctx, org_context
                )
                
                analysis_results[scenario_desc] = scenario_analysis
                
                # Mettre à jour le progrès
                iteration_ctx.scenarios_analyzed.append(scenario_desc)
                iteration_ctx.risk_analysis_progress[scenario_desc] = {
                    "iteration": iteration_ctx.current_iteration,
                    "analysis_depth": scenario_analysis.get("depth_achieved", 0.5),
                    "insights_extracted": len(scenario_analysis.get("insights", [])),
                    "risk_level": scenario_analysis.get("risk_level", "unknown")
                }
                
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse du scenario {scenario_desc}: {str(e)}")
                analysis_results[scenario_desc] = {"error": str(e), "insights": []}
        
        return analysis_results

    async def _analyze_single_risk_scenario_with_context(self, scenario_desc: str,
                                                        query: Query,
                                                        iteration_ctx: IterativeRiskContext,
                                                        org_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse un scenario de risque unique avec contexte organisationnel."""
        analysis_prompt = f"""
Analyse ce scenario de risque dans le contexte organisationnel et itératif.

SCENARIO: {scenario_desc}
REQUÊTE: "{query.query_text}"
ITÉRATION: {iteration_ctx.current_iteration}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2, ensure_ascii=False)}

CONTEXTE ACCUMULÉ:
- Scenarios déjà analysés: {iteration_ctx.scenarios_analyzed}
- Gaps identifiés: {iteration_ctx.context_gaps_identified}
- Connaissances existantes: {list(iteration_ctx.knowledge_accumulator.keys())}

MÉTHODOLOGIE EBIOS RM:
1. Identifie les actifs concernés
2. Analyse les sources de menaces
3. Évalue la vraisemblance
4. Évalue l'impact potentiel
5. Calcule le niveau de risque
6. Identifie les mesures de sécurité existantes
7. Propose des mesures complémentaires

Réponds au format JSON:
{{
    "scenario_analysis": {{
        "assets_affected": ["asset1", "asset2"],
        "threat_sources": ["source1", "source2"],
        "attack_paths": ["path1", "path2"],
        "likelihood_assessment": {{
            "level": "low|medium|high|very_high",
            "justification": "raison de l'évaluation"
        }},
        "impact_assessment": {{
            "level": "low|medium|high|very_high",
            "affected_domains": ["confidentiality", "integrity", "availability"],
            "business_impact": "description"
        }},
        "risk_level": "low|medium|high|critical",
        "existing_controls": ["control1", "control2"],
        "control_gaps": ["gap1", "gap2"],
        "recommended_measures": ["measure1", "measure2"]
    }},
    "insights": ["insight1", "insight2"],
    "depth_achieved": 0.0-1.0,
    "confidence_level": 0.0-1.0,
    "requires_deeper_analysis": true/false
}}
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                model="gpt-4.1",
                temperature=0.2
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du scenario {scenario_desc}: {str(e)}")
            return {
                "scenario_analysis": {"risk_level": "unknown"},
                "insights": [],
                "depth_achieved": 0.0,
                "confidence_level": 0.0,
                "requires_deeper_analysis": True
            }

    async def _integrate_new_risk_knowledge(self, scenario_analysis_results: Dict[str, Any],
                                          iteration_ctx: IterativeRiskContext,
                                          analysis_type: str) -> Dict[str, Any]:
        """Intègre les nouvelles connaissances sur les risques."""
        integrated_knowledge = {}
        
        for scenario_desc, analysis in scenario_analysis_results.items():
            if "error" not in analysis:
                # Ajouter les insights aux connaissances accumulées
                insights_key = f"risk_insights_iteration_{iteration_ctx.current_iteration}"
                if insights_key not in iteration_ctx.knowledge_accumulator:
                    iteration_ctx.knowledge_accumulator[insights_key] = []
                
                iteration_ctx.knowledge_accumulator[insights_key].extend(
                    analysis.get("insights", [])
                )
                
                # Mettre à jour la profondeur par domaine de risque
                scenario_analysis = analysis.get("scenario_analysis", {})
                risk_level = scenario_analysis.get("risk_level", "unknown")
                if risk_level != "unknown":
                    current_depth = iteration_ctx.depth_achieved.get(risk_level, 0.0)
                    new_depth = max(current_depth, analysis.get("depth_achieved", 0.0))
                    iteration_ctx.depth_achieved[risk_level] = new_depth
        
        # Synthétiser les connaissances intégrées
        integrated_knowledge = {
            "total_insights": sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values()),
            "scenarios_analyzed": len(iteration_ctx.scenarios_analyzed),
            "risk_depth": iteration_ctx.depth_achieved,
            "analysis_progress": len(iteration_ctx.risk_analysis_progress)
        }
        
        return integrated_knowledge

    async def _assess_risk_analysis_completeness(self, query: Query,
                                               iteration_ctx: IterativeRiskContext,
                                               integrated_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue la complétude de l'évaluation des risques."""
        completeness_prompt = f"""
Évalue la complétude de cette évaluation des risques itérative.

REQUÊTE ORIGINALE: "{query.query_text}"
ITÉRATION ACTUELLE: {iteration_ctx.current_iteration}

ÉTAT ACTUEL:
- Total insights risques: {integrated_knowledge.get("total_insights", 0)}
- Scenarios analysés: {integrated_knowledge.get("scenarios_analyzed", 0)}
- Profondeur par niveau de risque: {integrated_knowledge.get("risk_depth", {})}
- Progrès d'analyse: {integrated_knowledge.get("analysis_progress", 0)}

SEUILS CIBLES:
- Confiance minimum: {self.iteration_thresholds["min_confidence"]}
- Complétude cible: {self.iteration_thresholds["completeness_target"]}
- Couverture scenarios: {self.iteration_thresholds["scenario_coverage_min"]}

CONNAISSANCES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

Évalue la complétude et réponds au format JSON:
{{
    "overall_completeness": 0.0-1.0,
    "confidence_level": 0.0-1.0,
    "risk_analysis_quality": 0.0-1.0,
    "requires_more_iterations": true/false,
    "recommended_next_steps": ["step1", "step2"],
    "areas_needing_deeper_analysis": ["area1", "area2"],
    "sufficient_for_decision": true/false,
    "iteration_value_assessment": "high/medium/low"
}}
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": completeness_prompt}
                ],
                model="gpt-4.1",
                temperature=0.1
            )
            
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation de complétude risques: {str(e)}")
            return {
                "overall_completeness": 0.5,
                "confidence_level": 0.5,
                "risk_analysis_quality": 0.5,
                "requires_more_iterations": True,
                "recommended_next_steps": ["retry_assessment"],
                "areas_needing_deeper_analysis": ["error_occurred"],
                "sufficient_for_decision": False,
                "iteration_value_assessment": "low"
            }

    async def _perform_iterative_full_risk_assessment(self, query: Query,
                                                    analysis_type: str,
                                                    iteration_ctx: IterativeRiskContext,
                                                    completeness_assessment: Dict[str, Any],
                                                    org_id: str) -> AgentResponse:
        """Effectue une évaluation complète des risques avec approche itérative."""
        
        # Synthétiser toutes les connaissances accumulées
        synthesis_prompt = f"""
Synthétise une évaluation complète des risques basée sur {iteration_ctx.current_iteration} itération(s).

REQUÊTE: "{query.query_text}"

SCENARIOS ANALYSÉS: {iteration_ctx.scenarios_analyzed}

CONNAISSANCES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

PROFONDEUR ATTEINTE: {iteration_ctx.depth_achieved}

ÉVALUATION DE COMPLÉTUDE:
{json.dumps(completeness_assessment, indent=2, ensure_ascii=False)}

Fournis une évaluation EBIOS RM complète incluant:
1. Cartographie des risques identifiés
2. Analyse de vraisemblance et d'impact
3. Évaluation des mesures de sécurité existantes
4. Recommandations de traitement des risques
5. Plan d'action priorisé
6. Besoins d'itérations supplémentaires si applicable

Réponds en français avec une expertise EBIOS RM/MEHARI.
"""

        try:
            synthesis = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": synthesis_prompt}
                ],
                model="gpt-4.1",
                temperature=0.2
            )
            
            # Compiler les sources détaillées
            detailed_sources = self._compile_risk_sources_with_metadata(iteration_ctx)
            
            response = AgentResponse(
                content=synthesis,
                tools_used=["risk_analysis", "ebios_methodology", "organizational_context"],
                context_used=True,
                sources=detailed_sources,
                confidence=completeness_assessment.get("confidence_level", 0.8),
                iteration_info={
                    "total_iterations": iteration_ctx.current_iteration,
                    "completeness_achieved": completeness_assessment.get("overall_completeness", 0.0),
                    "scenarios_analyzed": len(iteration_ctx.scenarios_analyzed),
                    "risk_domains_covered": len(iteration_ctx.depth_achieved)
                },
                requires_iteration=completeness_assessment.get("requires_more_iterations", False),
                context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", []),
                knowledge_gained=self._extract_risk_insights(iteration_ctx),
                metadata={
                    "risk_analysis_summary": {
                        "scenarios_count": len(iteration_ctx.scenarios_analyzed),
                        "insights_total": sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values()),
                        "depth_progression": iteration_ctx.depth_achieved,
                        "analysis_progression": completeness_assessment
                    }
                }
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la synthèse itérative des risques: {str(e)}")
            return AgentResponse(
                content=f"Erreur lors de l'analyse itérative des risques: {str(e)}",
                confidence=0.3,
                requires_iteration=True,
                context_gaps=["error_in_synthesis"]
            )

    async def _perform_iterative_scenario_analysis(self, query: Query,
                                                 analysis_type: str,
                                                 iteration_ctx: IterativeRiskContext,
                                                 completeness_assessment: Dict[str, Any],
                                                 org_id: str) -> AgentResponse:
        """Effectue une analyse de scenarios avec approche itérative."""
        
        # Méthode similaire mais focalisée sur les scenarios
        synthesis = f"Analyse itérative de scenarios de risques - {len(iteration_ctx.scenarios_analyzed)} scenarios analysés en {iteration_ctx.current_iteration} itérations."
        
        detailed_sources = self._compile_risk_sources_with_metadata(iteration_ctx)
        
        return AgentResponse(
            content=synthesis,
            tools_used=["scenario_analysis", "ebios_methodology"],
            context_used=True,
            sources=detailed_sources,
            confidence=completeness_assessment.get("confidence_level", 0.8),
            requires_iteration=completeness_assessment.get("requires_more_iterations", False),
            context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", [])
        )

    async def _perform_iterative_control_evaluation(self, query: Query,
                                                  analysis_type: str,
                                                  iteration_ctx: IterativeRiskContext,
                                                  completeness_assessment: Dict[str, Any],
                                                  org_id: str) -> AgentResponse:
        """Effectue une évaluation des contrôles avec approche itérative."""
        
        synthesis = f"Évaluation itérative des contrôles de sécurité - Analyse basée sur {iteration_ctx.current_iteration} itérations."
        
        detailed_sources = self._compile_risk_sources_with_metadata(iteration_ctx)
        
        return AgentResponse(
            content=synthesis,
            tools_used=["control_evaluation", "effectiveness_assessment"],
            context_used=True,
            sources=detailed_sources,
            confidence=completeness_assessment.get("confidence_level", 0.8),
            requires_iteration=completeness_assessment.get("requires_more_iterations", False),
            context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", [])
        )

    async def _general_iterative_risk_analysis(self, query: Query,
                                             analysis_type: str,
                                             iteration_ctx: IterativeRiskContext,
                                             completeness_assessment: Dict[str, Any],
                                             org_id: str) -> AgentResponse:
        """Effectue une analyse générale des risques avec approche itérative."""
        
        synthesis = f"Analyse générale itérative des risques - {sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values())} insights collectés."
        
        detailed_sources = self._compile_risk_sources_with_metadata(iteration_ctx)
        
        return AgentResponse(
            content=synthesis,
            tools_used=["risk_analysis", "organizational_context"],
            context_used=True,
            sources=detailed_sources,
            confidence=completeness_assessment.get("confidence_level", 0.8),
            requires_iteration=completeness_assessment.get("requires_more_iterations", False),
            context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", [])
        )

    def _compile_risk_sources_with_metadata(self, iteration_ctx: IterativeRiskContext) -> List[Dict[str, Any]]:
        """Compile les sources d'analyse des risques avec métadonnées."""
        detailed_sources = []
        
        # Sources de scenarios analysés
        for scenario in iteration_ctx.scenarios_analyzed:
            progress = iteration_ctx.risk_analysis_progress.get(scenario, {})
            source = {
                "type": "risk_scenario_analysis",
                "id": scenario,
                "title": f"Scenario de risque: {scenario[:50]}...",
                "iteration": progress.get("iteration", 0),
                "analysis_depth": progress.get("analysis_depth", 0.0),
                "risk_level": progress.get("risk_level", "unknown"),
                "insights_count": progress.get("insights_extracted", 0),
                "tools_used": ["ebios_methodology", "risk_assessment", "organizational_context"],
                "details": f"Analyse EBIOS RM de profondeur {progress.get('analysis_depth', 0.0):.1%}"
            }
            detailed_sources.append(source)
        
        # Sources de connaissances accumulées
        for knowledge_key, knowledge_items in iteration_ctx.knowledge_accumulator.items():
            if knowledge_items:
                source = {
                    "type": "risk_knowledge_accumulation",
                    "id": knowledge_key,
                    "title": f"Connaissances risques - {knowledge_key}",
                    "content_count": len(knowledge_items),
                    "tools_used": ["risk_analysis", "iterative_synthesis"],
                    "details": f"Accumulation de {len(knowledge_items)} insights sur les risques"
                }
                detailed_sources.append(source)
        
        return detailed_sources

    def _extract_risk_insights(self, iteration_ctx: IterativeRiskContext) -> List[str]:
        """Extrait les insights clés sur les risques de toutes les itérations."""
        key_insights = []
        
        for iteration_key, insights in iteration_ctx.knowledge_accumulator.items():
            key_insights.extend(insights[:2])  # Top 2 insights par itération
        
        return key_insights

# Factory function
def get_risk_assessment_module(llm_client = None):
    """Factory function pour obtenir une instance du module d'évaluation des risques."""
    return RiskAssessmentModule(llm_client=llm_client) 