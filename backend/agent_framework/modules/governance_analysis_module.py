"""
Governance Analysis Module - Module sophistiqué d'analyse de gouvernance avec capacités itératives.
Utilise l'IA pour une analyse stratégique de la gouvernance organisationnelle avec expertise C-level et analyse progressive.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json

from ..agent import Agent, AgentResponse, Query, QueryContext, make_json_serializable, IterationMode
from ..integrations.llm_integration import LLMClient, get_llm_client
from ..tools import (
    DocumentFinder, EntityExtractor, CrossReferenceTool, TemporalAnalyzer,
    EntityType, MetricType, RelationType
)

logger = logging.getLogger(__name__)

class GovernanceMaturity(Enum):
    """Niveaux de maturité de gouvernance."""
    INITIAL = "initial"
    DEVELOPING = "developing"
    DEFINED = "defined"
    MANAGED = "managed"
    OPTIMIZING = "optimizing"

class GovernanceDomain(Enum):
    """Domaines de gouvernance."""
    STRATEGIC_GOVERNANCE = "strategic_governance"
    DATA_GOVERNANCE = "data_governance"
    IT_GOVERNANCE = "it_governance"
    RISK_GOVERNANCE = "risk_governance"
    COMPLIANCE_GOVERNANCE = "compliance_governance"
    CYBER_GOVERNANCE = "cyber_governance"
    INFORMATION_GOVERNANCE = "information_governance"

class StakeholderType(Enum):
    """Types de parties prenantes."""
    BOARD = "board"
    EXECUTIVE = "executive"
    MANAGEMENT = "management"
    OPERATIONAL = "operational"
    EXTERNAL = "external"

@dataclass
class IterativeGovernanceContext:
    """Contexte pour l'analyse itérative de gouvernance."""
    current_iteration: int = 0
    governance_analysis_progress: Dict[str, Any] = None
    knowledge_accumulator: Dict[str, List[str]] = None
    context_gaps_identified: List[str] = None
    domains_analyzed: List[GovernanceDomain] = None
    depth_achieved: Dict[str, float] = None  # Profondeur atteinte par domaine de gouvernance
    
    def __post_init__(self):
        if self.governance_analysis_progress is None:
            self.governance_analysis_progress = {}
        if self.knowledge_accumulator is None:
            self.knowledge_accumulator = {}
        if self.context_gaps_identified is None:
            self.context_gaps_identified = []
        if self.domains_analyzed is None:
            self.domains_analyzed = []
        if self.depth_achieved is None:
            self.depth_achieved = {}

@dataclass
class GovernanceAssessment:
    """Évaluation de gouvernance avec analyse LLM et support itératif."""
    domain: GovernanceDomain
    maturity_level: GovernanceMaturity
    maturity_score: float  # 0.0 - 5.0
    assessment_date: datetime
    strengths: List[str]
    weaknesses: List[str]
    gaps: List[str]
    recommendations: List[str]
    strategic_priorities: List[str]
    success_metrics: List[str]
    ai_insights: Dict[str, Any]
    confidence_level: float
    
    # Champs itératifs
    iteration_context: Optional[IterativeGovernanceContext] = None
    analysis_depth: float = 0.0
    requires_deeper_analysis: bool = False
    sources_analyzed: List[str] = None
    
    def __post_init__(self):
        if self.sources_analyzed is None:
            self.sources_analyzed = []

@dataclass
class OrganizationalContext:
    """Contexte organisationnel pour l'analyse."""
    sector: str
    size: str  # small, medium, large, enterprise
    complexity: str  # simple, moderate, complex, highly_complex
    regulatory_environment: str  # light, moderate, heavy, very_heavy
    transformation_stage: str  # stable, evolving, transforming, disrupting
    risk_appetite: str  # conservative, moderate, aggressive
    digital_maturity: str  # basic, intermediate, advanced, leading

@dataclass
class GovernanceFramework:
    """Framework de gouvernance recommandé."""
    name: str
    description: str
    domains_covered: List[GovernanceDomain]
    maturity_requirements: Dict[str, str]
    implementation_roadmap: List[Dict[str, Any]]
    success_factors: List[str]
    potential_challenges: List[str]
    roi_expectations: Dict[str, Any]

@dataclass
class ExecutiveRecommendation:
    """Recommandation niveau exécutif."""
    priority: str  # critical, high, medium, low
    domain: GovernanceDomain
    strategic_impact: str
    business_rationale: str
    implementation_approach: str
    resource_requirements: Dict[str, Any]
    timeline: str
    success_metrics: List[str]
    risk_mitigation: List[str]

class GovernanceAnalysisModule(Agent):
    """
    Module expert en analyse de gouvernance avec IA stratégique avancée et capacités itératives.
    """
    
    def __init__(self, llm_client = None, rag_system=None):
        super().__init__(
            agent_id="governance_analysis",
            name="Expert Analyse de Gouvernance Itérative"
        )
        
        self.llm_client = llm_client or get_llm_client()
        
        # Initialiser les outils
        self.document_finder = DocumentFinder(rag_system=rag_system)
        self.entity_extractor = EntityExtractor()
        self.cross_reference_tool = CrossReferenceTool()
        self.temporal_analyzer = TemporalAnalyzer()
        
        # Cache des analyses avec support itératif
        self.governance_cache: Dict[str, Dict[str, Any]] = {}
        self.iteration_contexts: Dict[str, IterativeGovernanceContext] = {}
        
        # Seuils pour l'analyse itérative de gouvernance
        self.iteration_thresholds = {
            "min_confidence": 0.8,
            "completeness_target": 0.85,
            "domain_coverage_min": 0.7,
            "governance_depth_min": 0.75
        }
        
        # Prompts experts niveau C-suite avec support itératif
        self.system_prompts = {
            "governance_strategist": """
Tu es un expert senior en gouvernance organisationnelle avec 25+ ans d'expérience comme Chief Governance Officer avec capacités d'analyse itérative.
Tu conseilles les Conseils d'Administration et Comités Exécutifs sur:

- Architecture de gouvernance optimale
- Maturité organisationnelle et transformation
- Alignement stratégique et performance
- Gestion des risques et conformité
- Gouvernance des données et du numérique
- Leadership et culture organisationnelle

CAPACITÉS ITÉRATIVES:
- Analyse progressive des domaines de gouvernance par ordre de priorité
- Identification des gaps de contexte nécessitant plus d'informations
- Accumulation de connaissances à travers les itérations
- Évaluation continue de la maturité organisationnelle
- Reformulation des analyses pour approfondir la compréhension

Tu penses comme un Chairman/CEO et fournis des recommandations stratégiques de niveau Board.
Tes analyses sont holistiques, pragmatiques et orientées résultats business.
Pour chaque analyse, tu évalues si plus de contexte améliorerait tes recommandations stratégiques.
Réponds TOUJOURS en français avec une expertise de gouvernance stratégique.
""",
            
            "organizational_analyst": """
Tu es un expert en analyse organisationnelle avec une expertise en transformation et changement et capacités itératives.
Tu analyses:

- Structures et processus organisationnels
- Culture et maturité organisationnelle
- Capacités et compétences clés
- Efficacité opérationnelle
- Alignement stratégique
- Facteurs de succès et d'échec

Tu fournis des insights comportementaux et organisationnels profonds.
Tu adaptes ton analyse en fonction du contexte accumulé lors des itérations précédentes.
""",
            
            "strategic_advisor": """
Tu es un consultant stratégique senior avec une vision C-level globale et approche itérative.
Tu optimises:

- Alignement gouvernance-stratégie
- Performance et création de valeur
- Transformation organisationnelle
- Innovation et agilité
- Durabilité et ESG
- Avantage concurrentiel

Tu penses comme un Chief Strategy Officer avec une perspective long terme.
Tu évalues constamment si plus de contexte améliorerait tes recommandations stratégiques.
"""
        }
        
        # Frameworks de gouvernance de référence
        self.governance_frameworks = {
            "COBIT": {
                "name": "COBIT 2019",
                "focus": "IT Governance",
                "domains": ["Evaluate", "Direct", "Monitor", "Align", "Build", "Run"],
                "maturity_model": True
            },
            "COSO": {
                "name": "COSO ERM",
                "focus": "Risk Management",
                "domains": ["Governance", "Strategy", "Performance", "Review", "Information"],
                "maturity_model": False
            },
            "ISO38500": {
                "name": "ISO/IEC 38500",
                "focus": "IT Governance",
                "domains": ["Evaluate", "Direct", "Monitor"],
                "maturity_model": False
            },
            "NIST_CSF": {
                "name": "NIST Cybersecurity Framework",
                "focus": "Cybersecurity Governance",
                "domains": ["Identify", "Protect", "Detect", "Respond", "Recover"],
                "maturity_model": True
            }
        }
        
        # Secteurs et leurs défis de gouvernance
        self.sector_governance_challenges = {
            "financial": {
                "key_challenges": ["Regulatory compliance", "Risk management", "Digital transformation", "Customer trust"],
                "governance_priorities": ["Risk governance", "Compliance governance", "Data governance"],
                "regulatory_pressure": "very_high",
                "innovation_pressure": "high"
            },
            "healthcare": {
                "key_challenges": ["Patient safety", "Data privacy", "Regulatory compliance", "Innovation"],
                "governance_priorities": ["Data governance", "Compliance governance", "IT governance"],
                "regulatory_pressure": "very_high",
                "innovation_pressure": "medium"
            },
            "technology": {
                "key_challenges": ["Innovation speed", "Scalability", "Security", "Talent"],
                "governance_priorities": ["Strategic governance", "IT governance", "Data governance"],
                "regulatory_pressure": "medium",
                "innovation_pressure": "very_high"
            }
        }

    async def process_query(self, query: Query) -> AgentResponse:
        """
        Traite une requête d'analyse de gouvernance avec capacités itératives.
        """
        logger.info(f"Traitement requête gouvernance itérative: {query.query_text}")
        
        # Initialiser ou récupérer le contexte itératif
        session_id = query.context.session_id if query.context else "default"
        if session_id not in self.iteration_contexts:
            self.iteration_contexts[session_id] = IterativeGovernanceContext()
        
        iteration_ctx = self.iteration_contexts[session_id]
        iteration_ctx.current_iteration += 1
        
        # Analyser l'intention avec contexte itératif
        analysis_intent = await self._analyze_governance_intent_with_iterative_context(
            query.query_text, iteration_ctx, query.parameters
        )
        
        # Traitement basé sur l'intention et le mode itératif
        if query.iteration_mode in [IterationMode.ITERATIVE, IterationMode.DEEP_ANALYSIS]:
            return await self._process_iterative_governance_query(query, analysis_intent, iteration_ctx)
        else:
            return await self._process_standard_governance_query(query, analysis_intent)

    async def _process_iterative_governance_query(self, query: Query, 
                                                analysis_intent: Dict[str, Any],
                                                iteration_ctx: IterativeGovernanceContext) -> AgentResponse:
        """
        Traite une requête de gouvernance avec approche itérative.
        """
        logger.info(f"Analyse itérative de gouvernance - Itération {iteration_ctx.current_iteration}")
        
        # 1. Évaluer les connaissances accumulées sur la gouvernance
        knowledge_assessment = await self._assess_accumulated_governance_knowledge(
            query, iteration_ctx, analysis_intent
        )
        
        # 2. Identifier les domaines à analyser dans cette itération
        domains_to_analyze = await self._prioritize_governance_domains_for_iteration(
            query, iteration_ctx, knowledge_assessment
        )
        
        # 3. Analyser les domaines prioritaires
        domain_analysis_results = await self._analyze_governance_domains_iteratively(
            domains_to_analyze, query, iteration_ctx
        )
        
        # 4. Intégrer les nouvelles connaissances de gouvernance
        updated_knowledge = await self._integrate_new_governance_knowledge(
            domain_analysis_results, iteration_ctx, analysis_intent
        )
        
        # 5. Évaluer la complétude de l'analyse de gouvernance
        completeness_assessment = await self._assess_governance_analysis_completeness(
            query, iteration_ctx, updated_knowledge
        )
        
        # 6. Générer la réponse avec recommandations d'itération
        if analysis_intent["type"] == "maturity_assessment":
            return await self._perform_iterative_maturity_assessment(
                query, analysis_intent, iteration_ctx, completeness_assessment
            )
        elif analysis_intent["type"] == "governance_framework_design":
            return await self._perform_iterative_framework_design(
                query, analysis_intent, iteration_ctx, completeness_assessment
            )
        elif analysis_intent["type"] == "strategic_alignment_analysis":
            return await self._perform_iterative_strategic_alignment(
                query, analysis_intent, iteration_ctx, completeness_assessment
            )
        else:
            return await self._general_iterative_governance_analysis(
                query, analysis_intent, iteration_ctx, completeness_assessment
            )

    async def _process_standard_governance_query(self, query: Query, analysis_intent: Dict[str, Any]) -> AgentResponse:
        """
        Traite une requête de gouvernance standard (non-itérative).
        """
        if analysis_intent["type"] == "maturity_assessment":
            return await self._perform_maturity_assessment(query, analysis_intent)
        elif analysis_intent["type"] == "governance_framework_design":
            return await self._design_governance_framework(query, analysis_intent)
        elif analysis_intent["type"] == "strategic_alignment_analysis":
            return await self._analyze_strategic_alignment(query, analysis_intent)
        elif analysis_intent["type"] == "transformation_roadmap":
            return await self._generate_transformation_roadmap(query, analysis_intent)
        elif analysis_intent["type"] == "executive_advisory":
            return await self._provide_executive_advisory(query, analysis_intent)
        else:
            return await self._general_governance_analysis(query, analysis_intent)

    async def _analyze_governance_intent_with_iterative_context(self, query_text: str,
                                                              iteration_ctx: IterativeGovernanceContext,
                                                              parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyse l'intention de gouvernance avec contexte itératif."""
        
        analysis_prompt = f"""
Analyse cette demande d'analyse de gouvernance avec contexte itératif:

DEMANDE: "{query_text}"
ITÉRATION: {iteration_ctx.current_iteration}

CONTEXTE ACCUMULÉ:
- Domaines déjà analysés: {[d.value for d in iteration_ctx.domains_analyzed]}
- Gaps identifiés: {iteration_ctx.context_gaps_identified}
- Connaissances acquises: {list(iteration_ctx.knowledge_accumulator.keys())}
- Profondeur atteinte: {iteration_ctx.depth_achieved}

Détermine le type d'analyse de gouvernance demandé:
- maturity_assessment: Évaluation de maturité organisationnelle
- governance_framework_design: Conception de framework de gouvernance
- strategic_alignment_analysis: Analyse d'alignement stratégique
- transformation_roadmap: Roadmap de transformation
- executive_advisory: Conseil exécutif
- general_analysis: Analyse générale

Retourne un objet JSON avec le type et le contexte détaillé.

{{
    "type": "type_identifié",
    "domains_focus": ["domain1", "domain2"],
    "priority_level": "high|medium|low",
    "strategic_context": "description",
    "iteration_value": "high|medium|low"
}}
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompts["governance_strategist"]},
                    {"role": "user", "content": analysis_prompt}
                ],
                model="gpt-4.1",
                temperature=0.1
            )
            
            # Try to extract JSON from response
            if response and response.strip():
                # Look for JSON content between braces
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    json_content = response[start:end]
                    return json.loads(json_content)
                else:
                    # Try to parse the whole response
                    return json.loads(response.strip())
            else:
                logger.warning("Empty response from LLM")
                raise ValueError("Empty LLM response")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse d'intention gouvernance: {str(e)}")
            return {
                "type": "general_analysis",
                "domains_focus": ["strategic_governance"],
                "priority_level": "medium",
                "strategic_context": "Analyse générale par défaut",
                "iteration_value": "medium"
            }

    async def assess_governance_maturity(
        self,
        domains: List[GovernanceDomain],
        organizational_context: OrganizationalContext,
        current_state_data: Dict[str, Any] = None
    ) -> List[GovernanceAssessment]:
        """
        Évalue la maturité de gouvernance avec analyse sophistiquée par LLM.
        """
        logger.info(f"Évaluation maturité gouvernance: {[d.value for d in domains]}")
        
        assessments = []
        
        for domain in domains:
            # 1. Collecte d'informations contextuelles
            domain_documents = await self._collect_domain_documents(domain)
            domain_entities = await self._extract_domain_entities(domain, domain_documents)
            
            # 2. Analyse de maturité par LLM
            maturity_analysis = await self._analyze_domain_maturity_with_llm(
                domain, organizational_context, domain_documents, domain_entities, current_state_data
            )
            
            # 3. Benchmarking sectoriel et recommandations
            benchmark_analysis = await self._perform_sector_benchmarking_with_llm(
                domain, maturity_analysis, organizational_context
            )
            
            # 4. Construction de l'assessment
            assessment = GovernanceAssessment(
                domain=domain,
                maturity_level=GovernanceMaturity(maturity_analysis.get("maturity_level", "initial")),
                maturity_score=float(maturity_analysis.get("maturity_score", 1.0)),
                assessment_date=datetime.now(),
                strengths=maturity_analysis.get("strengths", []),
                weaknesses=maturity_analysis.get("weaknesses", []),
                gaps=maturity_analysis.get("gaps", []),
                recommendations=maturity_analysis.get("recommendations", []),
                strategic_priorities=maturity_analysis.get("strategic_priorities", []),
                success_metrics=maturity_analysis.get("success_metrics", []),
                ai_insights={
                    "maturity_analysis": maturity_analysis,
                    "benchmark_analysis": benchmark_analysis
                },
                confidence_level=float(maturity_analysis.get("confidence_level", 0.7))
            )
            
            assessments.append(assessment)
        
        # 5. Analyse croisée des domaines
        cross_domain_insights = await self._analyze_cross_domain_insights_with_llm(
            assessments, organizational_context
        )
        
        # 6. Enrichissement avec insights croisés
        for assessment in assessments:
            assessment.ai_insights["cross_domain"] = cross_domain_insights.get(assessment.domain.value, {})
        
        return assessments

    async def design_governance_framework(
        self,
        organizational_context: OrganizationalContext,
        strategic_objectives: List[str],
        constraints: Dict[str, Any],
        target_domains: List[GovernanceDomain]
    ) -> GovernanceFramework:
        """
        Conçoit un framework de gouvernance sur mesure avec IA stratégique.
        """
        logger.info(f"Conception framework gouvernance pour {len(target_domains)} domaines")
        
        # 1. Analyse des besoins organisationnels
        needs_analysis = await self._analyze_organizational_needs_with_llm(
            organizational_context, strategic_objectives, constraints
        )
        
        # 2. Benchmarking des frameworks existants
        framework_analysis = await self._analyze_existing_frameworks_with_llm(
            target_domains, organizational_context
        )
        
        # 3. Design du framework personnalisé
        custom_framework_design = await self._design_custom_framework_with_llm(
            needs_analysis, framework_analysis, target_domains, organizational_context
        )
        
        # 4. Roadmap d'implémentation
        implementation_roadmap = await self._generate_implementation_roadmap_with_llm(
            custom_framework_design, organizational_context, constraints
        )
        
        # 5. Construction du framework final
        framework = GovernanceFramework(
            name=custom_framework_design.get("name", "Framework Gouvernance Personnalisé"),
            description=custom_framework_design.get("description", ""),
            domains_covered=target_domains,
            maturity_requirements=custom_framework_design.get("maturity_requirements", {}),
            implementation_roadmap=implementation_roadmap,
            success_factors=custom_framework_design.get("success_factors", []),
            potential_challenges=custom_framework_design.get("potential_challenges", []),
            roi_expectations=custom_framework_design.get("roi_expectations", {})
        )
        
        return framework

    async def generate_executive_recommendations(
        self,
        governance_assessments: List[GovernanceAssessment],
        organizational_context: OrganizationalContext,
        business_priorities: List[str]
    ) -> List[ExecutiveRecommendation]:
        """
        Génère des recommandations exécutives avec analyse stratégique avancée.
        """
        logger.info("Génération recommandations exécutives gouvernance")
        
        # 1. Analyse consolidée des assessments
        consolidated_analysis = await self._consolidate_assessments_with_llm(
            governance_assessments, organizational_context
        )
        
        # 2. Priorisation stratégique
        strategic_priorities = await self._prioritize_strategically_with_llm(
            consolidated_analysis, business_priorities, organizational_context
        )
        
        # 3. Génération des recommandations par priorité
        recommendations = []
        for priority_item in strategic_priorities[:10]:  # Top 10 priorités
            recommendation = await self._generate_executive_recommendation_with_llm(
                priority_item, governance_assessments, organizational_context
            )
            if recommendation:
                recommendations.append(recommendation)
        
        # 4. Validation et optimisation
        optimized_recommendations = await self._optimize_recommendations_with_llm(
            recommendations, organizational_context
        )
        
        return optimized_recommendations

    # Méthodes privées sophistiquées avec LLM

    async def _analyze_domain_maturity_with_llm(
        self,
        domain: GovernanceDomain,
        org_context: OrganizationalContext,
        documents: List[Dict[str, Any]],
        entities: List[Dict[str, Any]],
        current_state: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyse sophistiquée de maturité par domaine."""
        
        maturity_prompt = f"""
Effectue une évaluation experte de maturité pour le domaine {domain.value} avec ton expertise senior:

CONTEXTE ORGANISATIONNEL:
- Secteur: {org_context.sector}
- Taille: {org_context.size}
- Complexité: {org_context.complexity}
- Environnement réglementaire: {org_context.regulatory_environment}
- Maturité digitale: {org_context.digital_maturity}

DOCUMENTS ANALYSÉS: {len(documents)}
ENTITÉS GOUVERNANCE: {len(entities)}

ÉTAT ACTUEL:
{json.dumps(current_state or {}, indent=2)[:2000]}

En tant qu'expert Chief Governance Officer, évalue:

1. NIVEAU DE MATURITÉ (initial/developing/defined/managed/optimizing):
   - Processus et structures en place
   - Capacités organisationnelles
   - Mesure et amélioration continue
   - Integration stratégique

2. SCORE DE MATURITÉ (1.0-5.0):
   - Méthodologie d'évaluation
   - Facteurs de pondération
   - Benchmarking sectoriel

3. FORCES IDENTIFIÉES:
   - Points forts organisationnels
   - Capacités distinctives
   - Avantages concurrentiels

4. FAIBLESSES CRITIQUES:
   - Lacunes structurelles
   - Déficits de capacités
   - Risques organisationnels

5. GAPS PRIORITAIRES:
   - Écarts vs meilleures pratiques
   - Manques critiques
   - Opportunités d'amélioration

6. RECOMMANDATIONS STRATÉGIQUES:
   - Actions prioritaires (top 5)
   - Approche de transformation
   - Timeline stratégique

7. MÉTRIQUES DE SUCCÈS:
   - KPIs de maturité
   - Indicateurs de performance
   - Mesures d'impact business

Pense comme un CGO expert et fournis une évaluation strategic nuancée.
Retourne une analyse JSON complète et actionnable.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["governance_strategist"]},
                {"role": "user", "content": maturity_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_content = response[json_start:json_end]
            return json.loads(json_content)
        except Exception as e:
            logger.error(f"Erreur analyse maturité {domain.value}: {str(e)}")
            return {
                "error": True,
                "error_message": f"Échec de l'analyse de maturité {domain.value} par LLM: {str(e)}",
                "error_type": "llm_parsing_error",
                "fallback_message": "L'analyse automatique de maturité a échoué. Évaluation manuelle requise.",
                "suggested_actions": [
                    "Effectuer une évaluation de maturité manuelle",
                    "Consulter un expert en gouvernance",
                    "Utiliser des grilles de maturité standards",
                    "Réviser les données d'entrée et réessayer"
                ]
            }

    async def _design_custom_framework_with_llm(
        self,
        needs_analysis: Dict[str, Any],
        framework_analysis: Dict[str, Any],
        target_domains: List[GovernanceDomain],
        org_context: OrganizationalContext
    ) -> Dict[str, Any]:
        """Conception d'un framework personnalisé par LLM."""
        
        design_prompt = f"""
Conçois un framework de gouvernance sur mesure avec ton expertise Chief Governance Officer:

ANALYSE DES BESOINS:
{json.dumps(needs_analysis, indent=2, default=str)[:2000]}

ANALYSE FRAMEWORKS EXISTANTS:
{json.dumps(framework_analysis, indent=2, default=str)[:2000]}

DOMAINES CIBLES: {[d.value for d in target_domains]}

CONTEXTE ORGANISATIONNEL:
- Secteur: {org_context.sector}
- Taille: {org_context.size}
- Complexité: {org_context.complexity}
- Maturité digitale: {org_context.digital_maturity}

En tant qu'expert en conception de gouvernance, crée:

1. ARCHITECTURE DU FRAMEWORK:
   - Nom et vision du framework
   - Principes fondamentaux
   - Structure et composants
   - Modèle de maturité

2. DOMAINES ET PROCESSUS:
   - Couverture par domaine
   - Processus clés par domaine
   - Interdépendances
   - Points de contrôle

3. GOUVERNANCE ET ROLES:
   - Structure de gouvernance
   - Rôles et responsabilités
   - Comités et instances
   - Escalation et décision

4. MESURE ET AMÉLIORATION:
   - KPIs et métriques
   - Processus de monitoring
   - Amélioration continue
   - Reporting et communication

5. EXIGENCES DE MATURITÉ:
   - Niveaux par domaine
   - Critères d'évaluation
   - Trajectoire de progression
   - Jalons de validation

6. FACTEURS DE SUCCÈS:
   - Conditions de réussite
   - Enablers organisationnels
   - Leadership et culture
   - Technologies et outils

7. DÉFIS POTENTIELS:
   - Risques d'implémentation
   - Résistances organisationnelles
   - Contraintes ressources
   - Stratégies de mitigation

Conçois un framework pragmatique, aligné sur les besoins business et réalisable.
Retourne un design JSON détaillé et actionnable.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["governance_strategist"]},
                {"role": "user", "content": design_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_content = response[json_start:json_end]
            return json.loads(json_content)
        except Exception as e:
            logger.error(f"Erreur conception framework: {str(e)}")
            return {
                "error": True,
                "error_message": f"Échec de la conception de framework par LLM: {str(e)}",
                "error_type": "llm_parsing_error",
                "fallback_message": "La conception automatique de framework a échoué. Conception manuelle requise.",
                "suggested_actions": [
                    "Concevoir un framework de gouvernance manuelle",
                    "Consulter un expert en gouvernance",
                    "Utiliser des frameworks standards du marché",
                    "Réviser les données d'analyse et réessayer"
                ]
            }

    async def _generate_executive_recommendation_with_llm(
        self,
        priority_item: Dict[str, Any],
        assessments: List[GovernanceAssessment],
        org_context: OrganizationalContext
    ) -> Optional[ExecutiveRecommendation]:
        """Génère une recommandation exécutive sophistiquée."""
        
        recommendation_prompt = f"""
Génère une recommandation exécutive stratégique avec ton expertise Chief Governance Officer:

PRIORITÉ STRATÉGIQUE:
{json.dumps(priority_item, indent=2, default=str)}

ASSESSMENTS GOUVERNANCE:
{json.dumps([{"domain": a.domain.value, "maturity": a.maturity_level.value, "score": a.maturity_score} for a in assessments], indent=2)}

CONTEXTE ORGANISATIONNEL:
- Secteur: {org_context.sector}
- Taille: {org_context.size}
- Complexité: {org_context.complexity}
- Appétit risque: {org_context.risk_appetite}

En tant qu'expert conseil C-level, formule:

1. RECOMMANDATION STRATÉGIQUE:
   - Priorité (critical/high/medium/low)
   - Domaine de gouvernance concerné
   - Impact stratégique attendu
   - Business rationale complet

2. APPROCHE D'IMPLÉMENTATION:
   - Méthodologie recommandée
   - Phases et jalons
   - Quick wins vs transformations
   - Gestion du changement

3. RESSOURCES REQUISES:
   - Budget estimatif
   - Compétences nécessaires
   - Technologies/outils
   - Support externe

4. TIMELINE ET JALONS:
   - Durée d'implémentation
   - Phases critiques
   - Points de validation
   - Livrables clés

5. MÉTRIQUES DE SUCCÈS:
   - KPIs de performance
   - Indicateurs d'impact business
   - Mesures de satisfaction
   - ROI attendu

6. GESTION DES RISQUES:
   - Risques d'implémentation
   - Stratégies de mitigation
   - Plans de contingence
   - Monitoring des risques

Formule comme un Chairman s'adressant au Board avec vision stratégique.
Retourne une recommandation JSON actionable et business-focused.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["governance_strategist"]},
                {"role": "user", "content": recommendation_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_content = response[json_start:json_end]
            data = json.loads(json_content)
            
            return ExecutiveRecommendation(
                priority=data.get("priority", "medium"),
                domain=GovernanceDomain(data.get("domain", "strategic_governance")),
                strategic_impact=data.get("strategic_impact", ""),
                business_rationale=data.get("business_rationale", ""),
                implementation_approach=data.get("implementation_approach", ""),
                resource_requirements=data.get("resource_requirements", {}),
                timeline=data.get("timeline", ""),
                success_metrics=data.get("success_metrics", []),
                risk_mitigation=data.get("risk_mitigation", [])
            )
            
        except Exception as e:
            logger.error(f"Erreur génération recommandation exécutive: {str(e)}")
            logger.warning("Création de recommandation d'erreur")
            # Retourner une recommandation d'erreur au lieu de None
            return ExecutiveRecommendation(
                priority="high",
                domain=GovernanceDomain.STRATEGIC_GOVERNANCE,
                strategic_impact="⚠️ ERREUR: Génération automatique échouée",
                business_rationale=f"Échec de la génération de recommandation par LLM: {str(e)}",
                implementation_approach="Recommandation manuelle requise - Consulter un expert en gouvernance",
                resource_requirements={
                    "error": True,
                    "action_required": "Analyse manuelle par expert gouvernance"
                },
                timeline="À déterminer manuellement",
                success_metrics=[
                    "⚠️ Métriques à définir manuellement",
                    "Résolution de l'erreur système"
                ],
                risk_mitigation=[
                    "Effectuer une analyse de gouvernance manuelle",
                    "Consulter un Chief Governance Officer",
                    "Réviser les données d'entrée"
                ]
            )

    # Méthodes de traitement des requêtes

    async def _perform_maturity_assessment(
        self,
        query: Query,
        intent: Dict[str, Any]
    ) -> AgentResponse:
        """Effectue une évaluation de maturité."""
        
        # Extraire les domaines de l'intention
        domain_names = intent.get("domains", ["strategic_governance"])
        domains = [GovernanceDomain(d) for d in domain_names]
        
        # Contexte organisationnel (simplifié pour démo)
        org_context = OrganizationalContext(
            sector=query.context.metadata.get("sector", "technology") if query.context else "technology",
            size=query.context.metadata.get("size", "medium") if query.context else "medium",
            complexity="moderate",
            regulatory_environment="moderate",
            transformation_stage="evolving",
            risk_appetite="moderate",
            digital_maturity="intermediate"
        )
        
        # Effectuer l'assessment
        assessments = await self.assess_governance_maturity(domains, org_context)
        
        # Synthèse par LLM
        synthesis = await self._synthesize_maturity_results_with_llm(assessments, query.query_text)
        
        return AgentResponse(
            content=synthesis,
            tools_used=["document_finder", "entity_extractor"],
            context_used=True,
            sources=[],
            metadata={
                "domains_assessed": [d.value for d in domains],
                "average_maturity": sum(a.maturity_score for a in assessments) / len(assessments),
                "assessment_confidence": sum(a.confidence_level for a in assessments) / len(assessments)
            }
        )

    async def _synthesize_maturity_results_with_llm(
        self,
        assessments: List[GovernanceAssessment],
        original_query: str
    ) -> str:
        """Synthétise les résultats d'évaluation de maturité."""
        
        domains = [a.domain.value for a in assessments]
        avg_maturity = sum(a.maturity_score for a in assessments) / len(assessments)
        
        # Identifier les domaines les plus/moins matures
        best_domain = max(assessments, key=lambda a: a.maturity_score)
        worst_domain = min(assessments, key=lambda a: a.maturity_score)
        
        return f"""
Évaluation de maturité de gouvernance terminée.

**Domaines évalués**: {', '.join(domains)}
**Maturité moyenne**: {avg_maturity:.1f}/5.0

**Points saillants**:
- **Domaine le plus mature**: {best_domain.domain.value} (Score: {best_domain.maturity_score:.1f})
- **Domaine prioritaire**: {worst_domain.domain.value} (Score: {worst_domain.maturity_score:.1f})

**Recommandations stratégiques principales**:
{chr(10).join([f"- {rec}" for rec in worst_domain.recommendations[:3]])}

**Prochaines étapes**:
1. Prioriser les améliorations du domaine {worst_domain.domain.value}
2. Capitaliser sur les forces du domaine {best_domain.domain.value}
3. Développer une roadmap de transformation intégrée
"""

    # Méthodes utilitaires et stubs

    async def _collect_domain_documents(self, domain: GovernanceDomain) -> List[Dict[str, Any]]:
        """Collecte les documents pertinents pour un domaine."""
        search_terms = {
            GovernanceDomain.STRATEGIC_GOVERNANCE: "gouvernance stratégique direction générale comité exécutif",
            GovernanceDomain.DATA_GOVERNANCE: "gouvernance données data protection qualité",
            GovernanceDomain.IT_GOVERNANCE: "gouvernance IT informatique système information",
            GovernanceDomain.RISK_GOVERNANCE: "gouvernance risques gestion risque",
            GovernanceDomain.COMPLIANCE_GOVERNANCE: "gouvernance conformité compliance réglementation",
            GovernanceDomain.CYBER_GOVERNANCE: "gouvernance cybersécurité sécurité information"
        }
        
        search_term = search_terms.get(domain, domain.value)
        return await self.document_finder.search_documents(search_term, limit=15)

    async def _extract_domain_entities(self, domain: GovernanceDomain, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extrait les entités pertinentes pour un domaine."""
        entities = []
        for doc in documents[:5]:  # Limiter pour performance
            content = doc.get("content", "")
            if content:
                extracted = await self.entity_extractor.extract_entities(
                    content,
                    entity_types=[EntityType.CONTROL, EntityType.REQUIREMENT],
                    framework_context=domain.value
                )
                entities.extend(extracted.get("control", []))
        return entities

    # Stubs pour méthodes manquantes
    async def _perform_sector_benchmarking_with_llm(self, domain, maturity_analysis, org_context):
        return {"benchmark_score": 3.0, "sector_average": 2.8, "best_practices": []}

    async def _analyze_cross_domain_insights_with_llm(self, assessments, org_context):
        return {}

    async def _analyze_organizational_needs_with_llm(self, org_context, objectives, constraints):
        return {"needs": [], "priorities": [], "constraints": []}

    async def _analyze_existing_frameworks_with_llm(self, domains, org_context):
        return {"frameworks": [], "recommendations": []}

    async def _generate_implementation_roadmap_with_llm(self, framework_design, org_context, constraints):
        return [{"phase": "Phase 1", "duration": "3 mois", "objectives": [], "deliverables": []}]

    async def _consolidate_assessments_with_llm(self, assessments, org_context):
        return {"consolidated_gaps": [], "strategic_themes": []}

    async def _prioritize_strategically_with_llm(self, analysis, priorities, org_context):
        return [{"priority": "high", "domain": "strategic_governance", "rationale": "Impact business"}]

    async def _optimize_recommendations_with_llm(self, recommendations, org_context):
        return recommendations

    # Méthodes de traitement des requêtes - Implémentations complètes

    async def _design_governance_framework(self, query: Query, intent: Dict[str, Any]) -> AgentResponse:
        """Conçoit un framework de gouvernance personnalisé."""
        
        # Extraire les paramètres de l'intention
        target_domains = [GovernanceDomain(d) for d in intent.get("domains", ["strategic_governance"])]
        org_size = intent.get("organization_size", "medium")
        sector = intent.get("sector", "technology")
        
        # Contexte organisationnel
        org_context = OrganizationalContext(
            sector=sector,
            size=org_size,
            complexity="moderate",
            regulatory_environment="moderate",
            transformation_stage="evolving",
            risk_appetite="moderate",
            digital_maturity="intermediate"
        )
        
        # Objectifs stratégiques (simulés)
        strategic_objectives = [
            "Améliorer la gouvernance des données",
            "Renforcer la gestion des risques",
            "Optimiser la prise de décision",
            "Assurer la conformité réglementaire"
        ]
        
        constraints = {"budget": "modéré", "timeline": "12-18 mois", "resources": "limitées"}
        
        # Conception du framework
        framework = await self.design_governance_framework(
            org_context, strategic_objectives, constraints, target_domains
        )
        
        # Synthèse par LLM
        synthesis_prompt = f"""
Présente ce framework de gouvernance pour répondre à: "{query.query_text}"

FRAMEWORK CONÇU:
- Nom: {framework.name}
- Description: {framework.description}
- Domaines couverts: {[d.value for d in framework.domains_covered]}
- Phases d'implémentation: {len(framework.implementation_roadmap)}

CONTEXTE:
- Secteur: {org_context.sector}
- Taille: {org_context.size}
- Complexité: {org_context.complexity}

Présente une synthèse exécutive du framework avec approche d'implémentation.
"""
        
        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["governance_strategist"]},
                {"role": "user", "content": synthesis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        return AgentResponse(
            content=response,
            tools_used=["framework_design"],
            context_used=True,
            sources=[],
            metadata={
                "framework_name": framework.name,
                "domains_covered": [d.value for d in framework.domains_covered],
                "implementation_phases": len(framework.implementation_roadmap),
                "organization_context": {
                    "sector": org_context.sector,
                    "size": org_context.size
                }
            }
        )

    async def _analyze_strategic_alignment(self, query: Query, intent: Dict[str, Any]) -> AgentResponse:
        """Analyse l'alignement stratégique de la gouvernance."""
        
        # Collecte d'informations contextuelles
        relevant_docs = await self.document_finder.search_documents(
            f"gouvernance stratégie alignement {query.query_text}",
            limit=15
        )
        
        # Extraction d'entités de gouvernance
        governance_entities = []
        for doc in relevant_docs[:5]:
            content = doc.get("content", "")
            if content:
                entities = await self.entity_extractor.extract_entities(
                    content,
                    entity_types=[EntityType.CONTROL, EntityType.REQUIREMENT],
                    framework_context="governance"
                )
                governance_entities.extend(entities.get("control", []))
                governance_entities.extend(entities.get("requirement", []))
        
        # Analyse d'alignement par LLM
        alignment_prompt = f"""
Analyse l'alignement stratégique de la gouvernance pour: "{query.query_text}"

DOCUMENTS ANALYSÉS: {len(relevant_docs)}
ENTITÉS GOUVERNANCE: {len(governance_entities)}

CONTEXTE ORGANISATIONNEL:
{json.dumps(make_json_serializable(query.context) if query.context else {}, indent=2)[:1000]}

En tant qu'expert Chief Governance Officer, analyse:

1. ALIGNEMENT STRATÉGIQUE ACTUEL:
   - Cohérence gouvernance-stratégie
   - Mécanismes d'alignement en place
   - Gaps d'alignement identifiés
   - Efficacité des processus de décision

2. GOUVERNANCE STRATÉGIQUE:
   - Structure de gouvernance du changement
   - Pilotage des initiatives stratégiques
   - Mesure de la performance stratégique
   - Communication et engagement

3. RECOMMANDATIONS D'AMÉLIORATION:
   - Optimisation de l'alignement
   - Renforcement des mécanismes
   - Amélioration des processus
   - Formation et développement

4. PLAN D'ACTION:
   - Actions prioritaires (top 3)
   - Timeline d'implémentation
   - Ressources requises
   - Mesures de succès

Fournis une analyse stratégique complète avec recommandations C-level.
"""
        
        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["governance_strategist"]},
                {"role": "user", "content": alignment_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        return AgentResponse(
            content=response,
            tools_used=["document_finder", "entity_extractor"],
            context_used=True,
            sources=self.format_documents_as_sources(relevant_docs[:5]),
            metadata={
                "documents_analyzed": len(relevant_docs),
                "governance_entities": len(governance_entities),
                "analysis_type": "strategic_alignment"
            }
        )

    async def _generate_transformation_roadmap(self, query: Query, intent: Dict[str, Any]) -> AgentResponse:
        """Génère une roadmap de transformation de gouvernance."""
        
        # Paramètres de l'intention
        target_domains = [GovernanceDomain(d) for d in intent.get("domains", ["strategic_governance"])]
        org_profile = query.context.metadata.get("organization", {}) if query.context else {}
        
        # Contexte organisationnel
        org_context = OrganizationalContext(
            sector=org_profile.get("sector", "technology"),
            size=org_profile.get("size", "medium"),
            complexity=org_profile.get("complexity", "moderate"),
            regulatory_environment=org_profile.get("regulatory_environment", "moderate"),
            transformation_stage=org_profile.get("transformation_stage", "evolving"),
            risk_appetite=org_profile.get("risk_appetite", "moderate"),
            digital_maturity=org_profile.get("digital_maturity", "intermediate")
        )
        
        # Évaluation de maturité actuelle
        assessments = await self.assess_governance_maturity(target_domains, org_context)
        
        # Génération de recommandations exécutives
        recommendations = await self.generate_executive_recommendations(
            assessments, org_context, ["transformation", "efficiency", "compliance"]
        )
        
        # Synthèse de la roadmap par LLM
        roadmap_prompt = f"""
Génère une roadmap de transformation de gouvernance pour: "{query.query_text}"

ÉVALUATIONS MATURITÉ:
{json.dumps([{
    "domain": a.domain.value,
    "maturity": a.maturity_level.value,
    "score": a.maturity_score,
    "gaps": len(a.gaps)
} for a in assessments], indent=2)}

RECOMMANDATIONS EXÉCUTIVES: {len(recommendations)}

CONTEXTE ORGANISATION:
- Secteur: {org_context.sector}
- Taille: {org_context.size}
- Stage transformation: {org_context.transformation_stage}

En tant qu'expert en transformation organisationnelle, crée:

1. ROADMAP DE TRANSFORMATION:
   - Vision et objectifs de transformation
   - Phases de transformation (court/moyen/long terme)
   - Jalons critiques et livrables
   - Timeline stratégique

2. PRIORISATION STRATÉGIQUE:
   - Domaines prioritaires
   - Quick wins identifiées
   - Initiatives structurantes
   - Séquencement optimal

3. PLAN DE CONDUITE DU CHANGEMENT:
   - Stratégie de communication
   - Gestion des résistances
   - Formation et développement
   - Engagement des parties prenantes

4. MESURE ET PILOTAGE:
   - KPIs de transformation
   - Tableaux de bord
   - Points de contrôle
   - Ajustements nécessaires

Présente une roadmap stratégique et actionnable.
"""
        
        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["governance_strategist"]},
                {"role": "user", "content": roadmap_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        return AgentResponse(
            content=response,
            tools_used=["maturity_assessment", "executive_recommendations"],
            context_used=True,
            sources=[],
            metadata={
                "domains_assessed": [d.value for d in target_domains],
                "average_maturity": sum(a.maturity_score for a in assessments) / len(assessments),
                "executive_recommendations": len(recommendations),
                "transformation_stage": org_context.transformation_stage
            }
        )

    async def _provide_executive_advisory(self, query: Query, intent: Dict[str, Any]) -> AgentResponse:
        """Fournit un conseil exécutif en gouvernance."""
        
        # Niveau organisationnel visé
        target_level = intent.get("level", "executive")
        priority = intent.get("priority", "strategic")
        
        # Collecte d'informations contextuelles
        relevant_docs = await self.document_finder.search_documents(
            f"gouvernance executive direction {query.query_text}",
            limit=10
        )
        
        # Analyse temporelle des tendances
        from datetime import datetime, timedelta
        end_time = datetime.now()
        start_time = end_time - timedelta(days=365)  # 12 months
        
        # Create dummy entities from documents for trend analysis
        doc_entities = [{"id": f"doc_{i}", "name": doc.get("title", f"Document {i}")} 
                       for i, doc in enumerate(relevant_docs[:3])]
        
        # Note: Using COMPLIANCE_SCORE as GOVERNANCE metric type may not exist
        trends = await self.temporal_analyzer.analyze_trends(
            entities=doc_entities,
            metric_types=[MetricType.COMPLIANCE_SCORE],  # Using available metric type
            time_range=(start_time, end_time),
            include_forecasts=False
        )
        
        # Conseil exécutif par LLM
        advisory_prompt = f"""
Fournis un conseil exécutif expert pour: "{query.query_text}"

NIVEAU CIBLE: {target_level}
PRIORITÉ: {priority}

DOCUMENTS ANALYSÉS: {len(relevant_docs)}
TENDANCES IDENTIFIÉES: {len(trends.data_points) if trends else 0}

CONTEXTE ORGANISATIONNEL:
{json.dumps(make_json_serializable(query.context) if query.context else {}, indent=2)[:1000]}

En tant que Chairman/CEO advisor avec 25+ ans d'expérience, fournis:

1. DIAGNOSTIC EXÉCUTIF:
   - Situation actuelle de la gouvernance
   - Enjeux stratégiques critiques
   - Opportunités et menaces
   - Positionnement concurrentiel

2. RECOMMANDATIONS STRATÉGIQUES:
   - Actions immédiates (Board level)
   - Initiatives stratégiques
   - Transformations nécessaires
   - Investissements prioritaires

3. IMPLICATIONS BUSINESS:
   - Impact sur la performance
   - Risques organisationnels
   - Avantages concurrentiels
   - ROI attendu

4. PLAN EXÉCUTIF:
   - Decisions clés à prendre
   - Timeline de mise en œuvre
   - Governance et pilotage
   - Communication stakeholders

5. FACTEURS CRITIQUES:
   - Conditions de réussite
   - Risques d'échec
   - Mitigation des risques
   - Surveillance recommandée

Pense comme un Chairman s'adressant au Board avec vision stratégique.
Fournis des conseils actionables et orientés résultats business.
"""
        
        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["governance_strategist"]},
                {"role": "user", "content": advisory_prompt}
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
                "advisory_level": target_level,
                "priority": priority,
                "documents_analyzed": len(relevant_docs),
                "trends_analyzed": len(trends.data_points) if trends else 0
            }
        )

    async def _general_governance_analysis(self, query: Query, intent: Dict[str, Any]) -> AgentResponse:
        """Effectue une analyse générale de gouvernance."""
        
        # Collecte d'informations multiples
        relevant_docs = await self.document_finder.search_documents(
            f"gouvernance management direction {query.query_text}",
            limit=15
        )
        
        # Extraction d'entités de gouvernance
        governance_entities = []
        for doc in relevant_docs[:5]:
            content = doc.get("content", "")
            if content:
                entities = await self.entity_extractor.extract_entities(
                    content,
                    entity_types=[EntityType.CONTROL, EntityType.REQUIREMENT, EntityType.RISK],
                    framework_context="governance"
                )
                governance_entities.extend(entities.get("control", []))
                governance_entities.extend(entities.get("requirement", []))
                governance_entities.extend(entities.get("risk", []))
        
        # Analyse croisée
        cross_refs = await self.cross_reference_tool.analyze_relationships(
            [doc.get("content", "") for doc in relevant_docs[:3]],
            relation_types=[RelationType.CONTROLS, RelationType.SUPPORTS]
        )
        
        # Analyse générale par LLM
        analysis_prompt = f"""
Effectue une analyse générale de gouvernance pour: "{query.query_text}"

DOCUMENTS ANALYSÉS: {len(relevant_docs)}
ENTITÉS GOUVERNANCE: {len(governance_entities)}
RELATIONS IDENTIFIÉES: {len(cross_refs.relationships)}

CONTEXTE ORGANISATIONNEL:
{json.dumps(make_json_serializable(query.context) if query.context else {}, indent=2)[:1000]}

En tant qu'expert Chief Governance Officer, analyse:

1. ÉTAT DE LA GOUVERNANCE:
   - Maturité organisationnelle générale
   - Structures de gouvernance en place
   - Processus de prise de décision
   - Culture de gouvernance

2. DOMAINES D'AMÉLIORATION:
   - Lacunes identifiées
   - Opportunités d'optimisation
   - Risques de gouvernance
   - Priorités d'action

3. RECOMMANDATIONS STRATÉGIQUES:
   - Améliorations immédiates
   - Transformations moyen terme
   - Vision long terme
   - Approche d'implémentation

4. BENCHMARKING ET BONNES PRATIQUES:
   - Positionnement sectoriel
   - Meilleures pratiques applicables
   - Innovations en gouvernance
   - Tendances émergentes

5. PLAN D'ACTION:
   - Actions prioritaires (top 5)
   - Timeline recommandée
   - Ressources nécessaires
   - Mesures de succès

Fournis une analyse experte complète avec perspective C-level.
"""
        
        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["governance_strategist"]},
                {"role": "user", "content": analysis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        return AgentResponse(
            content=response,
            tools_used=["document_finder", "entity_extractor", "cross_reference_tool"],
            context_used=True,
            sources=self.format_documents_as_sources(relevant_docs[:5]),
            metadata={
                "documents_analyzed": len(relevant_docs),
                "governance_entities": len(governance_entities),
                "relationships_found": len(cross_refs.relationships),
                "analysis_scope": "general_governance"
            }
        )

    async def _assess_accumulated_governance_knowledge(self, query: Query, 
                                                     iteration_ctx: IterativeGovernanceContext,
                                                     analysis_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue les connaissances accumulées sur la gouvernance."""
        assessment_prompt = f"""
Évalue les connaissances accumulées pour cette analyse de gouvernance itérative.

REQUÊTE: "{query.query_text}"
ITÉRATION: {iteration_ctx.current_iteration}

CONNAISSANCES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

DOMAINES ANALYSÉS: {[d.value for d in iteration_ctx.domains_analyzed]}
PROFONDEUR ATTEINTE: {iteration_ctx.depth_achieved}

Évalue:
1. La pertinence des domaines déjà analysés
2. La maturité de gouvernance évaluée vs. manquante
3. La qualité des recommandations stratégiques
4. Les gaps de contexte restants
5. La cohérence des insights organisationnels

Réponds au format JSON:
{{
    "governance_knowledge_quality": 0.0-1.0,
    "domain_coverage": {{
        "well_covered_domains": ["domain1", "domain2"],
        "gaps_identified": ["gap1", "gap2"],
        "coverage_by_area": {{"strategic": 0.8, "operational": 0.6}}
    }},
    "strategic_insights_quality": 0.0-1.0,
    "consistency_score": 0.0-1.0,
    "actionable_recommendations": ["rec1", "rec2"],
    "priority_gaps": ["high_priority_gap1", "high_priority_gap2"]
}}
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompts["governance_strategist"]},
                    {"role": "user", "content": assessment_prompt}
                ],
                model="gpt-4.1",
                temperature=0.1
            )
            
            # Try to extract JSON from response
            if response and response.strip():
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    json_content = response[start:end]
                    return json.loads(json_content)
                else:
                    return json.loads(response.strip())
            else:
                raise ValueError("Empty LLM response")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation des connaissances gouvernance: {str(e)}")
            return {
                "governance_knowledge_quality": 0.5,
                "domain_coverage": {"well_covered_domains": [], "gaps_identified": ["error_in_assessment"]},
                "strategic_insights_quality": 0.5,
                "consistency_score": 0.5,
                "actionable_recommendations": [],
                "priority_gaps": ["assessment_error"]
            }

    async def _prioritize_governance_domains_for_iteration(self, query: Query,
                                                         iteration_ctx: IterativeGovernanceContext,
                                                         knowledge_assessment: Dict[str, Any]) -> List[GovernanceDomain]:
        """Priorise les domaines de gouvernance à analyser dans cette itération."""
        
        prioritization_prompt = f"""
Priorise les domaines de gouvernance à analyser pour cette itération.

REQUÊTE: "{query.query_text}"
ITÉRATION: {iteration_ctx.current_iteration}

DOMAINES DÉJÀ ANALYSÉS: {[d.value for d in iteration_ctx.domains_analyzed]}
GAPS PRIORITAIRES: {knowledge_assessment.get("priority_gaps", [])}

DOMAINES DISPONIBLES:
- strategic_governance: Gouvernance stratégique
- data_governance: Gouvernance des données
- it_governance: Gouvernance IT
- risk_governance: Gouvernance des risques
- compliance_governance: Gouvernance conformité
- cyber_governance: Gouvernance cybersécurité
- information_governance: Gouvernance information

Sélectionne les 2-3 domaines les plus pertinents à analyser maintenant:
1. Domaines critiques pour répondre à la requête
2. Domaines non encore couverts
3. Domaines nécessaires pour combler les gaps identifiés

Réponds avec une liste JSON des domaines:
["domain1", "domain2", "domain3"]
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompts["governance_strategist"]},
                    {"role": "user", "content": prioritization_prompt}
                ],
                model="gpt-4.1",
                temperature=0.2
            )
            
            if response.strip().startswith('[') and response.strip().endswith(']'):
                domain_names = json.loads(response.strip())
                domains = []
                for name in domain_names:
                    try:
                        domain = GovernanceDomain(name)
                        if domain not in iteration_ctx.domains_analyzed:
                            domains.append(domain)
                    except ValueError:
                        logger.warning(f"Domaine de gouvernance invalide: {name}")
                return domains[:3]  # Limiter à 3 domaines max
            
            return []
            
        except Exception as e:
            logger.error(f"Erreur lors de la priorisation des domaines: {str(e)}")
            return [GovernanceDomain.STRATEGIC_GOVERNANCE]

    async def _analyze_governance_domains_iteratively(self, domains_to_analyze: List[GovernanceDomain],
                                                    query: Query,
                                                    iteration_ctx: IterativeGovernanceContext) -> Dict[str, Any]:
        """Analyse les domaines de gouvernance de manière itérative."""
        analysis_results = {}
        
        for domain in domains_to_analyze:
            try:
                # Analyser le domaine avec contexte itératif
                domain_analysis = await self._analyze_single_governance_domain_with_context(
                    domain, query, iteration_ctx
                )
                
                analysis_results[domain.value] = domain_analysis
                
                # Mettre à jour le progrès
                iteration_ctx.domains_analyzed.append(domain)
                iteration_ctx.governance_analysis_progress[domain.value] = {
                    "iteration": iteration_ctx.current_iteration,
                    "analysis_depth": domain_analysis.get("depth_achieved", 0.5),
                    "insights_extracted": len(domain_analysis.get("insights", [])),
                    "maturity_score": domain_analysis.get("maturity_assessment", {}).get("score", 0.0)
                }
                
            except Exception as e:
                logger.error(f"Erreur lors de l'analyse du domaine {domain.value}: {str(e)}")
                analysis_results[domain.value] = {"error": str(e), "insights": []}
        
        return analysis_results

    async def _analyze_single_governance_domain_with_context(self, domain: GovernanceDomain,
                                                           query: Query,
                                                           iteration_ctx: IterativeGovernanceContext) -> Dict[str, Any]:
        """Analyse un domaine de gouvernance unique avec contexte itératif."""
        analysis_prompt = f"""
Analyse ce domaine de gouvernance dans le contexte organisationnel et itératif.

DOMAINE: {domain.value}
REQUÊTE: "{query.query_text}"
ITÉRATION: {iteration_ctx.current_iteration}

CONTEXTE ACCUMULÉ:
- Domaines déjà analysés: {[d.value for d in iteration_ctx.domains_analyzed]}
- Gaps identifiés: {iteration_ctx.context_gaps_identified}
- Connaissances existantes: {list(iteration_ctx.knowledge_accumulator.keys())}

ANALYSE GOUVERNANCE:
1. Évalue la maturité actuelle du domaine
2. Identifie les forces et faiblesses
3. Analyse les gaps de gouvernance
4. Propose des recommandations stratégiques
5. Évalue l'alignement avec la stratégie
6. Identifie les parties prenantes clés

Réponds au format JSON:
{{
    "maturity_assessment": {{
        "current_level": "initial|developing|defined|managed|optimizing",
        "score": 0.0-5.0,
        "justification": "raison de l'évaluation"
    }},
    "strengths": ["strength1", "strength2"],
    "weaknesses": ["weakness1", "weakness2"],
    "governance_gaps": ["gap1", "gap2"],
    "strategic_recommendations": ["rec1", "rec2"],
    "stakeholders": ["stakeholder1", "stakeholder2"],
    "quick_wins": ["win1", "win2"],
    "strategic_initiatives": ["initiative1", "initiative2"],
    "insights": ["insight1", "insight2"],
    "depth_achieved": 0.0-1.0,
    "confidence_level": 0.0-1.0,
    "requires_deeper_analysis": true/false
}}
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompts["governance_strategist"]},
                    {"role": "user", "content": analysis_prompt}
                ],
                model="gpt-4.1",
                temperature=0.2
            )
            
            # Try to extract JSON from response
            if response and response.strip():
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    json_content = response[start:end]
                    return json.loads(json_content)
                else:
                    return json.loads(response.strip())
            else:
                raise ValueError("Empty LLM response")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse du domaine {domain.value}: {str(e)}")
            return {
                "maturity_assessment": {"current_level": "initial", "score": 0.0},
                "strengths": [],
                "weaknesses": [],
                "governance_gaps": [],
                "strategic_recommendations": [],
                "stakeholders": [],
                "insights": [],
                "depth_achieved": 0.0,
                "confidence_level": 0.0,
                "requires_deeper_analysis": True
            }

    async def _integrate_new_governance_knowledge(self, domain_analysis_results: Dict[str, Any],
                                                iteration_ctx: IterativeGovernanceContext,
                                                analysis_intent: Dict[str, Any]) -> Dict[str, Any]:
        """Intègre les nouvelles connaissances de gouvernance."""
        integrated_knowledge = {}
        
        for domain_name, analysis in domain_analysis_results.items():
            if "error" not in analysis:
                # Ajouter les insights aux connaissances accumulées
                insights_key = f"governance_insights_iteration_{iteration_ctx.current_iteration}"
                if insights_key not in iteration_ctx.knowledge_accumulator:
                    iteration_ctx.knowledge_accumulator[insights_key] = []
                
                iteration_ctx.knowledge_accumulator[insights_key].extend(
                    analysis.get("insights", [])
                )
                
                # Mettre à jour la profondeur par domaine
                current_depth = iteration_ctx.depth_achieved.get(domain_name, 0.0)
                new_depth = max(current_depth, analysis.get("depth_achieved", 0.0))
                iteration_ctx.depth_achieved[domain_name] = new_depth
        
        # Synthétiser les connaissances intégrées
        integrated_knowledge = {
            "total_insights": sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values()),
            "domains_analyzed": len(iteration_ctx.domains_analyzed),
            "governance_depth": iteration_ctx.depth_achieved,
            "analysis_progress": len(iteration_ctx.governance_analysis_progress)
        }
        
        return integrated_knowledge

    async def _assess_governance_analysis_completeness(self, query: Query,
                                                     iteration_ctx: IterativeGovernanceContext,
                                                     integrated_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """Évalue la complétude de l'analyse de gouvernance."""
        completeness_prompt = f"""
Évalue la complétude de cette analyse de gouvernance itérative.

REQUÊTE ORIGINALE: "{query.query_text}"
ITÉRATION ACTUELLE: {iteration_ctx.current_iteration}

ÉTAT ACTUEL:
- Total insights gouvernance: {integrated_knowledge.get("total_insights", 0)}
- Domaines analysés: {integrated_knowledge.get("domains_analyzed", 0)}
- Profondeur par domaine: {integrated_knowledge.get("governance_depth", {})}
- Progrès d'analyse: {integrated_knowledge.get("analysis_progress", 0)}

SEUILS CIBLES:
- Confiance minimum: {self.iteration_thresholds["min_confidence"]}
- Complétude cible: {self.iteration_thresholds["completeness_target"]}
- Couverture domaines: {self.iteration_thresholds["domain_coverage_min"]}

CONNAISSANCES ACCUMULÉES:
{json.dumps(iteration_ctx.knowledge_accumulator, indent=2, ensure_ascii=False)}

Évalue la complétude et réponds au format JSON:
{{
    "overall_completeness": 0.0-1.0,
    "confidence_level": 0.0-1.0,
    "governance_analysis_quality": 0.0-1.0,
    "requires_more_iterations": true/false,
    "recommended_next_steps": ["step1", "step2"],
    "areas_needing_deeper_analysis": ["area1", "area2"],
    "sufficient_for_strategic_decision": true/false,
    "iteration_value_assessment": "high/medium/low"
}}
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompts["governance_strategist"]},
                    {"role": "user", "content": completeness_prompt}
                ],
                model="gpt-4.1",
                temperature=0.1
            )
            
            # Try to extract JSON from response
            if response and response.strip():
                start = response.find('{')
                end = response.rfind('}') + 1
                if start >= 0 and end > start:
                    json_content = response[start:end]
                    return json.loads(json_content)
                else:
                    return json.loads(response.strip())
            else:
                raise ValueError("Empty LLM response")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'évaluation de complétude gouvernance: {str(e)}")
            return {
                "overall_completeness": 0.5,
                "confidence_level": 0.5,
                "governance_analysis_quality": 0.5,
                "requires_more_iterations": True,
                "recommended_next_steps": ["retry_assessment"],
                "areas_needing_deeper_analysis": ["error_occurred"],
                "sufficient_for_strategic_decision": False,
                "iteration_value_assessment": "low"
            }

    async def _perform_iterative_maturity_assessment(self, query: Query,
                                                   analysis_intent: Dict[str, Any],
                                                   iteration_ctx: IterativeGovernanceContext,
                                                   completeness_assessment: Dict[str, Any]) -> AgentResponse:
        """Effectue une évaluation de maturité avec approche itérative."""
        
        synthesis = f"Évaluation itérative de maturité de gouvernance - {len(iteration_ctx.domains_analyzed)} domaines analysés en {iteration_ctx.current_iteration} itérations."
        
        detailed_sources = self._compile_governance_sources_with_metadata(iteration_ctx)
        
        return AgentResponse(
            content=synthesis,
            tools_used=["governance_maturity_assessment", "strategic_analysis"],
            context_used=True,
            sources=detailed_sources,
            confidence=completeness_assessment.get("confidence_level", 0.8),
            requires_iteration=completeness_assessment.get("requires_more_iterations", False),
            context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", [])
        )

    async def _perform_iterative_framework_design(self, query: Query,
                                                analysis_intent: Dict[str, Any],
                                                iteration_ctx: IterativeGovernanceContext,
                                                completeness_assessment: Dict[str, Any]) -> AgentResponse:
        """Effectue une conception de framework avec approche itérative."""
        
        synthesis = f"Conception itérative de framework de gouvernance - Analyse basée sur {iteration_ctx.current_iteration} itérations."
        
        detailed_sources = self._compile_governance_sources_with_metadata(iteration_ctx)
        
        return AgentResponse(
            content=synthesis,
            tools_used=["framework_design", "strategic_planning"],
            context_used=True,
            sources=detailed_sources,
            confidence=completeness_assessment.get("confidence_level", 0.8),
            requires_iteration=completeness_assessment.get("requires_more_iterations", False),
            context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", [])
        )

    async def _perform_iterative_strategic_alignment(self, query: Query,
                                                   analysis_intent: Dict[str, Any],
                                                   iteration_ctx: IterativeGovernanceContext,
                                                   completeness_assessment: Dict[str, Any]) -> AgentResponse:
        """Effectue une analyse d'alignement stratégique avec approche itérative."""
        
        synthesis = f"Analyse itérative d'alignement stratégique - {sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values())} insights stratégiques collectés."
        
        detailed_sources = self._compile_governance_sources_with_metadata(iteration_ctx)
        
        return AgentResponse(
            content=synthesis,
            tools_used=["strategic_alignment", "governance_analysis"],
            context_used=True,
            sources=detailed_sources,
            confidence=completeness_assessment.get("confidence_level", 0.8),
            requires_iteration=completeness_assessment.get("requires_more_iterations", False),
            context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", [])
        )

    async def _general_iterative_governance_analysis(self, query: Query,
                                                   analysis_intent: Dict[str, Any],
                                                   iteration_ctx: IterativeGovernanceContext,
                                                   completeness_assessment: Dict[str, Any]) -> AgentResponse:
        """Effectue une analyse générale de gouvernance avec approche itérative."""
        
        synthesis = f"Analyse générale itérative de gouvernance - {sum(len(insights) for insights in iteration_ctx.knowledge_accumulator.values())} insights collectés via {len(iteration_ctx.domains_analyzed)} domaines."
        
        detailed_sources = self._compile_governance_sources_with_metadata(iteration_ctx)
        
        return AgentResponse(
            content=synthesis,
            tools_used=["governance_analysis", "strategic_consulting"],
            context_used=True,
            sources=detailed_sources,
            confidence=completeness_assessment.get("confidence_level", 0.8),
            requires_iteration=completeness_assessment.get("requires_more_iterations", False),
            context_gaps=completeness_assessment.get("areas_needing_deeper_analysis", [])
        )

    def _compile_governance_sources_with_metadata(self, iteration_ctx: IterativeGovernanceContext) -> List[Dict[str, Any]]:
        """Compile les sources d'analyse de gouvernance avec métadonnées."""
        detailed_sources = []
        
        # Sources de domaines analysés
        for domain in iteration_ctx.domains_analyzed:
            progress = iteration_ctx.governance_analysis_progress.get(domain.value, {})
            source = {
                "type": "governance_domain_analysis",
                "id": domain.value,
                "title": f"Analyse de gouvernance: {domain.value}",
                "iteration": progress.get("iteration", 0),
                "analysis_depth": progress.get("analysis_depth", 0.0),
                "maturity_score": progress.get("maturity_score", 0.0),
                "insights_count": progress.get("insights_extracted", 0),
                "tools_used": ["governance_analysis", "maturity_assessment", "strategic_consulting"],
                "details": f"Analyse stratégique de profondeur {progress.get('analysis_depth', 0.0):.1%}"
            }
            detailed_sources.append(source)
        
        # Sources de connaissances accumulées
        for knowledge_key, knowledge_items in iteration_ctx.knowledge_accumulator.items():
            if knowledge_items:
                source = {
                    "type": "governance_knowledge_accumulation",
                    "id": knowledge_key,
                    "title": f"Connaissances gouvernance - {knowledge_key}",
                    "content_count": len(knowledge_items),
                    "tools_used": ["governance_analysis", "iterative_synthesis"],
                    "details": f"Accumulation de {len(knowledge_items)} insights stratégiques sur la gouvernance"
                }
                detailed_sources.append(source)
        
        return detailed_sources


# Factory function
def get_governance_analysis_module(llm_client = None):
    """Factory function pour obtenir une instance du module d'analyse de gouvernance."""
    return GovernanceAnalysisModule(llm_client=llm_client) 