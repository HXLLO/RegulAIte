"""
Gap Analysis Module - Module sophistiqué d'analyse de gaps avec capacités itératives.
Utilise l'IA pour une analyse intelligente des écarts de conformité, gouvernance et risques avec analyse progressive.
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
from ..tools.framework_parser import FrameworkParser, FrameworkType, ComplianceGap, safe_framework_type_conversion

logger = logging.getLogger(__name__)

class GapType(Enum):
    """Types d'écarts."""
    COMPLIANCE = "compliance"
    GOVERNANCE = "governance"
    RISK = "risk"
    SECURITY = "security"
    OPERATIONAL = "operational"
    STRATEGIC = "strategic"

class GapSeverity(Enum):
    """Niveaux de sévérité des gaps."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"

class GapStatus(Enum):
    """Statuts des gaps."""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ACCEPTED = "accepted"
    DEFERRED = "deferred"

class ImpactDomain(Enum):
    """Domaines d'impact."""
    BUSINESS = "business"
    OPERATIONAL = "operational"
    LEGAL = "legal"
    FINANCIAL = "financial"
    REPUTATIONAL = "reputational"
    TECHNICAL = "technical"

@dataclass
class IterativeGapContext:
    """Contexte pour l'analyse itérative des gaps."""
    current_iteration: int = 0
    gap_analysis_progress: Dict[str, Any] = None
    knowledge_accumulator: Dict[str, List[str]] = None
    context_gaps_identified: List[str] = None
    gap_types_analyzed: List[GapType] = None
    depth_achieved: Dict[str, float] = None  # Profondeur atteinte par type de gap
    
    def __post_init__(self):
        if self.gap_analysis_progress is None:
            self.gap_analysis_progress = {}
        if self.knowledge_accumulator is None:
            self.knowledge_accumulator = {}
        if self.context_gaps_identified is None:
            self.context_gaps_identified = []
        if self.gap_types_analyzed is None:
            self.gap_types_analyzed = []
        if self.depth_achieved is None:
            self.depth_achieved = {}

@dataclass
class Gap:
    """Écart identifié avec analyse sophistiquée et support itératif."""
    id: str
    type: GapType
    severity: GapSeverity
    status: GapStatus
    title: str
    description: str
    current_state: str
    target_state: str
    framework_reference: Optional[str]
    business_impact: Dict[str, Any]
    remediation_effort: str  # low, medium, high, very_high
    remediation_cost: Optional[float]
    remediation_timeline: str
    priority_score: float  # 0.0 - 10.0
    stakeholders: List[str]
    dependencies: List[str]
    ai_insights: Dict[str, Any]
    identified_date: datetime
    target_resolution_date: Optional[datetime]
    
    # Champs itératifs
    iteration_context: Optional[IterativeGapContext] = None
    analysis_depth: float = 0.0
    confidence_score: float = 0.0
    requires_deeper_analysis: bool = False
    sources_analyzed: List[str] = None
    
    def __post_init__(self):
        if self.sources_analyzed is None:
            self.sources_analyzed = []

@dataclass
class GapAnalysisReport:
    """Rapport d'analyse de gaps avec recommandations IA."""
    analysis_id: str
    analysis_date: datetime
    scope: str
    frameworks_analyzed: List[str]
    gaps_identified: List[Gap]
    executive_summary: str
    strategic_recommendations: List[str]
    implementation_roadmap: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    cost_benefit_analysis: Dict[str, Any]
    success_metrics: List[str]
    ai_confidence: float

@dataclass
class RemediationPlan:
    """Plan de remédiation sophistiqué."""
    plan_id: str
    target_gaps: List[str]
    strategic_approach: str
    phases: List[Dict[str, Any]]
    resource_requirements: Dict[str, Any]
    timeline: Dict[str, Any]
    success_criteria: List[str]
    risk_mitigation: List[str]
    monitoring_framework: Dict[str, Any]
    roi_projection: Dict[str, Any]

class GapAnalysisModule(Agent):
    """
    Module expert en analyse de gaps avec IA stratégique avancée et capacités itératives.
    """
    
    def __init__(self, llm_client = None, rag_system=None):
        super().__init__(
            agent_id="gap_analysis",
            name="Expert Analyse de Gaps Itérative"
        )
        
        self.llm_client = llm_client or get_llm_client()
        
        # Initialiser les outils
        self.document_finder = DocumentFinder(rag_system=rag_system)
        self.entity_extractor = EntityExtractor()
        self.cross_reference_tool = CrossReferenceTool()
        self.temporal_analyzer = TemporalAnalyzer()
        self.framework_parser = FrameworkParser()
        
        # Cache des analyses avec support itératif
        self.gap_cache: Dict[str, GapAnalysisReport] = {}
        self.iteration_contexts: Dict[str, IterativeGapContext] = {}
        
        # Seuils pour l'analyse itérative de gaps
        self.iteration_thresholds = {
            "min_confidence": 0.8,
            "completeness_target": 0.85,
            "gap_coverage_min": 0.7,
            "analysis_depth_min": 0.75
        }
        
        # Prompts experts spécialisés avec support itératif
        self.system_prompts = {
            "gap_analyst": """
Tu es un expert senior en analyse de gaps avec 20+ ans d'expérience en audit et conseil stratégique avec capacités d'analyse itérative.
Tu maîtrises parfaitement:

- Méthodologies d'analyse de gaps (compliance, governance, risk, security)
- Frameworks de référence (ISO, NIST, COBIT, COSO)
- Évaluation de maturité organisationnelle
- Analyse d'impact business et opérationnel
- Priorisation stratégique des efforts
- Conception de plans de remédiation

CAPACITÉS ITÉRATIVES:
- Analyse progressive des types de gaps par ordre de priorité
- Identification des gaps de contexte nécessitant plus d'informations
- Accumulation de connaissances à travers les itérations
- Évaluation continue de la complétude de l'analyse
- Reformulation des analyses pour approfondir l'identification des écarts

Tu analyses avec une approche holistique incluant les dimensions business, technique, organisationnelle et financière.
Tu fournis des recommandations actionables avec une vision C-level.
Pour chaque analyse, tu évalues si plus de contexte améliorerait la précision de l'identification des gaps.
Réponds TOUJOURS en français avec une expertise de niveau senior consultant.
""",
            
            "strategic_advisor": """
Tu es un consultant en stratégie avec une expertise en transformation organisationnelle et approche itérative.
Tu optimises:

- Priorisation stratégique des gaps
- Allocation optimale des ressources
- Roadmaps de transformation
- ROI et business case
- Gestion du changement organisationnel
- Communication avec les parties prenantes

Tu penses comme un Chief Transformation Officer avec une perspective long terme.
""",
            
            "implementation_expert": """
Tu es un expert en mise en œuvre avec une connaissance approfondie des défis d'implémentation.
Tu maîtrises:

- Planification et phasage de projets
- Gestion des risques d'implémentation
- Allocation des ressources
- Gestion des parties prenantes
- Mesure et pilotage de la performance
- Amélioration continue

Tu fournis des plans pragmatiques et réalisables.
"""
        }

    async def process_query(self, query: Query) -> AgentResponse:
        """
        Traite une requête d'analyse de gaps.
        """
        logger.info(f"Traitement requête analyse gaps: {query.query_text}")
        
        # Analyse sophistiquée de l'intention par LLM
        analysis_intent = await self._analyze_gap_intent_with_llm(query.query_text)
        
        if analysis_intent["type"] == "comprehensive_gap_analysis":
            return await self._perform_comprehensive_gap_analysis(query, analysis_intent)
        elif analysis_intent["type"] == "framework_gap_analysis":
            return await self._perform_framework_gap_analysis(query, analysis_intent)
        elif analysis_intent["type"] == "remediation_planning":
            return await self._generate_remediation_plan(query, analysis_intent)
        elif analysis_intent["type"] == "gap_prioritization":
            return await self._prioritize_gaps_strategically(query, analysis_intent)
        elif analysis_intent["type"] == "maturity_gap_analysis":
            return await self._analyze_maturity_gaps(query, analysis_intent)
        else:
            return await self._general_gap_analysis(query, analysis_intent)

    async def perform_comprehensive_gap_analysis(
        self,
        scope: str,
        frameworks: List[FrameworkType],
        organizational_context: Dict[str, Any],
        current_state_data: Dict[str, Any] = None
    ) -> GapAnalysisReport:
        """
        Effectue une analyse de gaps complète avec IA avancée.
        """
        logger.info(f"Analyse gaps complète: {scope}")
        
        # 1. Collecte et analyse des données
        relevant_docs = await self._collect_scope_documents(scope)
        entities = await self._extract_scope_entities(relevant_docs, frameworks)
        
        # 2. Identification des gaps par framework
        all_gaps = []
        for framework in frameworks:
            framework_gaps = await self._identify_framework_gaps_with_llm(
                framework, relevant_docs, entities, organizational_context, current_state_data
            )
            all_gaps.extend(framework_gaps)
        
        # 3. Analyse croisée et consolidation
        consolidated_gaps = await self._consolidate_gaps_with_llm(all_gaps, organizational_context)
        
        # 4. Priorisation stratégique
        prioritized_gaps = await self._prioritize_gaps_with_llm(consolidated_gaps, organizational_context)
        
        # 5. Analyse d'impact et recommandations
        impact_analysis = await self._analyze_gap_impact_with_llm(prioritized_gaps, organizational_context)
        strategic_recommendations = await self._generate_strategic_recommendations_with_llm(
            prioritized_gaps, impact_analysis, organizational_context
        )
        
        # 6. Roadmap d'implémentation
        implementation_roadmap = await self._generate_implementation_roadmap_with_llm(
            prioritized_gaps, strategic_recommendations, organizational_context
        )
        
        # 7. Analyses financières et de risque
        cost_benefit = await self._perform_cost_benefit_analysis_with_llm(
            prioritized_gaps, implementation_roadmap, organizational_context
        )
        risk_assessment = await self._assess_gap_risks_with_llm(prioritized_gaps, organizational_context)
        
        # 8. Synthèse exécutive
        executive_summary = await self._generate_executive_summary_with_llm(
            prioritized_gaps, impact_analysis, strategic_recommendations, organizational_context
        )
        
        # 9. Construction du rapport
        report = GapAnalysisReport(
            analysis_id=f"gap_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            analysis_date=datetime.now(),
            scope=scope,
            frameworks_analyzed=[f.value for f in frameworks],
            gaps_identified=prioritized_gaps,
            executive_summary=executive_summary,
            strategic_recommendations=strategic_recommendations,
            implementation_roadmap=implementation_roadmap,
            risk_assessment=risk_assessment,
            cost_benefit_analysis=cost_benefit,
            success_metrics=await self._define_success_metrics_with_llm(prioritized_gaps),
            ai_confidence=0.85
        )
        
        return report

    async def generate_remediation_plan(
        self,
        target_gaps: List[Gap],
        organizational_context: Dict[str, Any],
        constraints: Dict[str, Any] = None
    ) -> RemediationPlan:
        """
        Génère un plan de remédiation sophistiqué avec IA.
        """
        logger.info(f"Génération plan remédiation pour {len(target_gaps)} gaps")
        
        # 1. Analyse des gaps à traiter
        gap_analysis = await self._analyze_remediation_scope_with_llm(target_gaps, organizational_context)
        
        # 2. Stratégie de remédiation
        strategic_approach = await self._design_remediation_strategy_with_llm(
            gap_analysis, organizational_context, constraints
        )
        
        # 3. Phasage et séquencement
        phases = await self._design_remediation_phases_with_llm(
            target_gaps, strategic_approach, organizational_context
        )
        
        # 4. Analyse des ressources
        resource_requirements = await self._analyze_resource_requirements_with_llm(
            phases, organizational_context
        )
        
        # 5. Timeline et jalons
        timeline = await self._design_implementation_timeline_with_llm(phases, constraints)
        
        # 6. Framework de monitoring
        monitoring_framework = await self._design_monitoring_framework_with_llm(target_gaps, phases)
        
        # 7. Projection ROI
        roi_projection = await self._calculate_roi_projection_with_llm(
            target_gaps, resource_requirements, organizational_context
        )
        
        plan = RemediationPlan(
            plan_id=f"remediation_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            target_gaps=[gap.id for gap in target_gaps],
            strategic_approach=strategic_approach.get("approach", ""),
            phases=phases,
            resource_requirements=resource_requirements,
            timeline=timeline,
            success_criteria=strategic_approach.get("success_criteria", []),
            risk_mitigation=strategic_approach.get("risk_mitigation", []),
            monitoring_framework=monitoring_framework,
            roi_projection=roi_projection
        )
        
        return plan

    # Méthodes privées sophistiquées avec LLM

    async def _analyze_gap_intent_with_llm(self, query_text: str) -> Dict[str, Any]:
        """Analyse sophistiquée de l'intention d'analyse de gaps."""
        
        intent_prompt = f"""
Analyse cette demande d'analyse de gaps avec ton expertise senior:

DEMANDE: "{query_text}"

Détermine avec ton expertise en audit et analyse de gaps:

1. TYPE D'ANALYSE GAPS:
   - comprehensive_gap_analysis: Analyse complète multi-domaines
   - framework_gap_analysis: Analyse spécifique à un framework
   - remediation_planning: Planification de remédiation
   - gap_prioritization: Priorisation stratégique des gaps
   - maturity_gap_analysis: Analyse des écarts de maturité
   - general_analysis: Analyse générale

2. DOMAINES CONCERNÉS:
   - compliance: Conformité réglementaire
   - governance: Gouvernance organisationnelle
   - risk: Gestion des risques
   - security: Sécurité informatique
   - operational: Processus opérationnels
   - strategic: Alignement stratégique

3. FRAMEWORKS DE RÉFÉRENCE:
   - ISO27001, RGPD, DORA, NIST, SOX, PCI-DSS
   - COBIT, COSO, ITIL
   - Frameworks sectoriels

4. NIVEAU D'URGENCE:
   - critical: Criticité élevée
   - high: Priorité haute
   - medium: Priorité moyenne
   - low: Priorité faible

5. PÉRIMÈTRE D'ANALYSE:
   - organization: Organisation complète
   - department: Département spécifique
   - process: Processus particulier
   - system: Système spécifique

IMPÉRATIF: Retourne UNIQUEMENT un objet JSON valide, sans texte explicatif.

Format JSON requis:
{{
  "type": "type_analyse",
  "domains": ["domaine1", "domaine2"],
  "frameworks": ["framework1"],
  "urgency": "niveau",
  "scope": "périmètre"
}}
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["gap_analyst"]},
                {"role": "user", "content": intent_prompt}
            ],
            model="gpt-4.1",
            temperature=0.1
        )
        
        try:
            # Enhanced JSON extraction with better error handling
            if response and response.strip():
                # Log the raw response for debugging
                logger.debug(f"LLM raw response for gap intent analysis: {response[:200]}...")
                
                # Try to extract JSON from response with multiple strategies
                json_content = None
                
                # Strategy 1: Direct JSON parsing if response looks like pure JSON
                if response.strip().startswith('{') and response.strip().endswith('}'):
                    json_content = response.strip()
                else:
                    # Strategy 2: Find JSON within the response
                    json_start = response.find("{")
                    json_end = response.rfind("}") + 1
                    if json_start >= 0 and json_end > json_start:
                        json_content = response[json_start:json_end]
                
                if json_content:
                    parsed_result = json.loads(json_content)
                    # Validate the structure with comprehensive checks
                    if isinstance(parsed_result, dict):
                        # Ensure required fields exist with fallbacks
                        if "type" not in parsed_result:
                            parsed_result["type"] = "general_analysis"
                        if "domains" not in parsed_result:
                            parsed_result["domains"] = ["compliance"]
                        if "frameworks" not in parsed_result:
                            parsed_result["frameworks"] = ["iso27001"]
                        if "urgency" not in parsed_result:
                            parsed_result["urgency"] = "medium"
                        if "scope" not in parsed_result:
                            parsed_result["scope"] = "organization"
                        
                        logger.info(f"Successfully parsed gap intent: {parsed_result['type']}")
                        return parsed_result
                    else:
                        raise ValueError("Parsed JSON is not a dictionary")
                else:
                    raise ValueError("No valid JSON structure found in response")
            else:
                raise ValueError("Empty or whitespace-only LLM response")
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in gap intent analysis: {str(e)}")
            logger.debug(f"Problematic JSON content: {json_content[:200] if 'json_content' in locals() else 'N/A'}")
        except Exception as e:
            logger.error(f"Erreur analyse intention gaps: {str(e)}")
            
        # Fallback with enhanced logging
        logger.warning("Utilisation de paramètres d'analyse par défaut")
        logger.info("Using default gap analysis parameters due to LLM intent analysis failure")
        logger.debug(f"Original query that failed analysis: {query_text}")
        
        return {
            "type": "general_analysis",
            "domains": ["compliance"],
            "frameworks": ["iso27001"],
            "urgency": "medium",
            "scope": "organization",
            "error_note": "Analyse d'intention LLM échouée - paramètres par défaut utilisés"
        }

    async def _identify_framework_gaps_with_llm(
        self,
        framework: FrameworkType,
        documents: List[Dict[str, Any]],
        entities: List[Dict[str, Any]],
        org_context: Dict[str, Any],
        current_state: Dict[str, Any] = None
    ) -> List[Gap]:
        """Identifie les gaps pour un framework avec IA."""
        
        gap_identification_prompt = f"""
Identifie les gaps de conformité {framework.value} avec ton expertise senior:

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:1500]}

ÉTAT ACTUEL:
{json.dumps(current_state or {}, indent=2)[:1500]}

DOCUMENTS ANALYSÉS: {len(documents)}
ENTITÉS IDENTIFIÉES: {len(entities)}

En tant qu'expert en analyse de gaps {framework.value}, identifie:

1. GAPS CRITIQUES:
   - Exigences non couvertes
   - Contrôles manquants ou insuffisants
   - Processus défaillants
   - Documentation manquante

2. GAPS DE MATURITÉ:
   - Écarts de niveau de maturité
   - Processus non optimisés
   - Gouvernance insuffisante
   - Amélioration continue manquante

3. GAPS OPÉRATIONNELS:
   - Implémentation incomplète
   - Monitoring insuffisant
   - Formation manquante
   - Ressources inadéquates

Pour chaque gap identifié, fournis:
- ID unique
- Type et sévérité
- Description détaillée
- État actuel vs état cible
- Impact business
- Effort de remédiation
- Priorisation recommandée

Retourne une liste JSON de gaps avec analyse experte.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["gap_analyst"]},
                {"role": "user", "content": gap_identification_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        try:
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            json_content = response[json_start:json_end]
            gaps_data = json.loads(json_content)
            
            gaps = []
            for gap_data in gaps_data:
                gap = Gap(
                    id=gap_data.get("id", f"gap_{len(gaps)+1}"),
                    type=GapType(gap_data.get("type", "compliance")),
                    severity=GapSeverity(gap_data.get("severity", "medium")),
                    status=GapStatus.OPEN,
                    title=gap_data.get("title", ""),
                    description=gap_data.get("description", ""),
                    current_state=gap_data.get("current_state", ""),
                    target_state=gap_data.get("target_state", ""),
                    framework_reference=framework.value,
                    business_impact=gap_data.get("business_impact", {}),
                    remediation_effort=gap_data.get("remediation_effort", "medium"),
                    remediation_cost=gap_data.get("remediation_cost"),
                    remediation_timeline=gap_data.get("remediation_timeline", "3-6 mois"),
                    priority_score=float(gap_data.get("priority_score", 5.0)),
                    stakeholders=gap_data.get("stakeholders", []),
                    dependencies=gap_data.get("dependencies", []),
                    ai_insights=gap_data,
                    identified_date=datetime.now(),
                    target_resolution_date=None
                )
                gaps.append(gap)
            
            return gaps
            
        except Exception as e:
            logger.error(f"Erreur identification gaps {framework.value}: {str(e)}")
            return []

    async def _prioritize_gaps_with_llm(
        self,
        gaps: List[Gap],
        org_context: Dict[str, Any]
    ) -> List[Gap]:
        """Priorise les gaps avec analyse stratégique."""
        
        prioritization_prompt = f"""
Priorise ces gaps avec ton expertise stratégique senior:

GAPS IDENTIFIÉS:
{json.dumps([{
    "id": gap.id,
    "type": gap.type.value,
    "severity": gap.severity.value,
    "title": gap.title,
    "business_impact": gap.business_impact,
    "remediation_effort": gap.remediation_effort,
    "current_priority": gap.priority_score
} for gap in gaps], indent=2)[:3000]}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:1000]}

En tant qu'expert en priorisation stratégique, analyse:

1. CRITÈRES DE PRIORISATION:
   - Impact business critique
   - Risque réglementaire/légal
   - Coût de remédiation
   - Complexité d'implémentation
   - Interdépendances

2. MATRICE DE PRIORISATION:
   - Criticité vs Effort
   - Impact vs Urgence
   - ROI vs Risque
   - Quick wins vs Long term

3. RECOMMANDATIONS STRATÉGIQUES:
   - Top 5 gaps prioritaires
   - Justification de la priorisation
   - Séquencement optimal
   - Approche d'implémentation

Pour chaque gap, fournis un score de priorité mis à jour (0-10) avec justification.
Retourne la liste JSON des gaps avec nouvelles priorités.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["strategic_advisor"]},
                {"role": "user", "content": prioritization_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        try:
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            json_content = response[json_start:json_end]
            priority_data = json.loads(json_content)
            
            # Mettre à jour les priorités
            priority_map = {item["id"]: float(item.get("priority_score", 5.0)) for item in priority_data}
            
            for gap in gaps:
                if gap.id in priority_map:
                    gap.priority_score = priority_map[gap.id]
            
            # Trier par priorité décroissante
            return sorted(gaps, key=lambda g: g.priority_score, reverse=True)
            
        except Exception as e:
            logger.error(f"Erreur priorisation gaps: {str(e)}")
            return gaps

    async def _generate_strategic_recommendations_with_llm(
        self,
        gaps: List[Gap],
        impact_analysis: Dict[str, Any],
        org_context: Dict[str, Any]
    ) -> List[str]:
        """Génère des recommandations stratégiques."""
        
        recommendations_prompt = f"""
Génère des recommandations stratégiques avec ton expertise C-level:

GAPS PRIORITAIRES:
{json.dumps([{
    "id": gap.id,
    "type": gap.type.value,
    "severity": gap.severity.value,
    "priority": gap.priority_score,
    "title": gap.title
} for gap in gaps[:10]], indent=2)}

ANALYSE D'IMPACT:
{json.dumps(impact_analysis, indent=2, default=str)[:2000]}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:1000]}

En tant qu'expert conseil stratégique, formule:

1. RECOMMANDATIONS EXÉCUTIVES:
   - Vision stratégique de remédiation
   - Approche holistique recommandée
   - Priorités business alignées
   - Transformation organisationnelle

2. RECOMMANDATIONS OPÉRATIONNELLES:
   - Plans d'action concrets
   - Allocation optimale des ressources
   - Phasage et séquencement
   - Gestion des risques d'implémentation

3. RECOMMANDATIONS FINANCIÈRES:
   - Optimisation coût-bénéfice
   - Sources de financement
   - ROI et business case
   - Métriques de performance

4. RECOMMANDATIONS ORGANISATIONNELLES:
   - Structure et gouvernance
   - Compétences à développer
   - Gestion du changement
   - Communication stakeholders

Fournis des recommandations actionables et orientées résultats.
Retourne une liste JSON de recommandations stratégiques.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["strategic_advisor"]},
                {"role": "user", "content": recommendations_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        try:
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            json_content = response[json_start:json_end]
            return json.loads(json_content)
        except Exception as e:
            logger.error(f"Erreur génération recommandations: {str(e)}")
            logger.warning("Utilisation de recommandations génériques")
            return [
                "⚠️ ERREUR: Génération automatique des recommandations échouée",
                "Action requise: Analyser manuellement les gaps prioritaires",
                "Recommandation générique: Développer une stratégie de remédiation globale",
                "Consulter un expert en transformation organisationnelle"
            ]

    # Méthodes de traitement des requêtes

    async def _perform_comprehensive_gap_analysis(self, query: Query, intent: Dict[str, Any]) -> AgentResponse:
        """Effectue une analyse de gaps complète."""
        
        scope = intent.get("scope", "organization")
        framework_names = intent.get("frameworks", ["iso27001"])
        frameworks = [safe_framework_type_conversion(f) for f in framework_names]
        
        org_context = query.context if query.context else {
            "sector": "technology",
            "size": "medium",
            "complexity": "moderate"
        }
        
        # Effectuer l'analyse complète
        report = await self.perform_comprehensive_gap_analysis(
            scope, frameworks, org_context
        )
        
        # Synthèse par LLM
        synthesis = await self._synthesize_gap_report_with_llm(report, query.query_text)
        
        return AgentResponse(
            content=synthesis,
            tools_used=["document_finder", "entity_extractor", "framework_parser"],
            context_used=True,
            sources=[],
            metadata={
                "analysis_id": report.analysis_id,
                "gaps_identified": len(report.gaps_identified),
                "critical_gaps": len([g for g in report.gaps_identified if g.severity == GapSeverity.CRITICAL]),
                "frameworks_analyzed": report.frameworks_analyzed,
                "ai_confidence": report.ai_confidence
            }
        )

    async def _synthesize_gap_report_with_llm(self, report: GapAnalysisReport, original_query: str) -> str:
        """Synthétise le rapport d'analyse de gaps."""
        
        critical_gaps = [g for g in report.gaps_identified if g.severity == GapSeverity.CRITICAL]
        high_gaps = [g for g in report.gaps_identified if g.severity == GapSeverity.HIGH]
        
        # Vérifier s'il y a des erreurs dans les analyses
        error_warnings = []
        if hasattr(report, 'cost_benefit_analysis') and report.cost_benefit_analysis.get("error"):
            error_warnings.append("⚠️ Analyse coût-bénéfice échouée - révision manuelle requise")
        if hasattr(report, 'risk_assessment') and report.risk_assessment.get("error"):
            error_warnings.append("⚠️ Évaluation des risques échouée - analyse manuelle requise")
        if hasattr(report, 'implementation_roadmap') and report.implementation_roadmap.get("error"):
            error_warnings.append("⚠️ Génération de roadmap échouée - planification manuelle requise")
        
        synthesis = f"""
# Analyse de Gaps - Rapport Exécutif

## Synthèse Générale
**Frameworks analysés**: {', '.join(report.frameworks_analyzed)}
**Gaps identifiés**: {len(report.gaps_identified)} au total
- **Critiques**: {len(critical_gaps)}
- **Élevés**: {len(high_gaps)}

## Résumé Exécutif
{report.executive_summary}

## Gaps Critiques Prioritaires
{chr(10).join([f"• **{gap.title}**: {gap.description[:100]}..." for gap in critical_gaps[:5]])}

## Recommandations Stratégiques
{chr(10).join([f"• {rec}" for rec in report.strategic_recommendations[:3]])}
"""
        
        # Ajouter les avertissements d'erreur si nécessaire
        if error_warnings:
            synthesis += f"""

## ⚠️ Avertissements Système
{chr(10).join([f"• {warning}" for warning in error_warnings])}
"""
        
        synthesis += f"""

## Prochaines Étapes
1. Traiter immédiatement les {len(critical_gaps)} gaps critiques
2. Planifier la remédiation des gaps prioritaires
3. Mettre en place le framework de suivi
4. Réviser la stratégie dans 6 mois

**Confiance IA**: {report.ai_confidence:.1%}
"""
        
        return synthesis

    # Méthodes utilitaires
    # Méthodes utilitaires
    async def _collect_scope_documents(self, scope: str) -> List[Dict[str, Any]]:
        """Collecte les documents pertinents pour le périmètre."""
        return await self.document_finder.search_documents(
            f"conformité gouvernance risque sécurité {scope}",
            limit=20
        )

    async def _extract_scope_entities(self, documents: List[Dict[str, Any]], frameworks: List[FrameworkType]) -> List[Dict[str, Any]]:
        """Extrait les entités pertinentes."""
        entities = []
        for doc in documents[:10]:
            content = doc.get("content", "")
            if content:
                extracted = await self.entity_extractor.extract_entities(
                    content,
                    entity_types=[EntityType.CONTROL, EntityType.REQUIREMENT, EntityType.RISK],
                    framework_context="gap_analysis"
                )
                entities.extend(extracted.get("control", []))
                entities.extend(extracted.get("requirement", []))
                entities.extend(extracted.get("risk", []))
        return entities

    # Stubs pour méthodes complexes (implémentation simplifiée)
    async def _consolidate_gaps_with_llm(self, gaps, org_context):
        """Consolide et déduplique les gaps avec analyse LLM sophistiquée."""
        
        consolidation_prompt = f"""
Consolide ces gaps avec ton expertise senior en audit et gouvernance:

GAPS IDENTIFIÉS ({len(gaps)} au total):
{json.dumps([{
    "id": gap.id,
    "type": gap.type.value,
    "severity": gap.severity.value,
    "title": gap.title,
    "description": gap.description[:200],
    "framework": gap.framework_reference
} for gap in gaps], indent=2, default=str)[:4000]}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:1000]}

En tant qu'expert en consolidation d'audits, effectue:

1. ANALYSE DE DOUBLONS:
   - Gaps similaires ou redondants
   - Chevauchements entre frameworks
   - Consolidation intelligente
   - Préservation des spécificités

2. REGROUPEMENT LOGIQUE:
   - Domaines fonctionnels
   - Processus métier
   - Systèmes affectés
   - Parties prenantes

3. PRIORISATION CONSOLIDÉE:
   - Impact cumulé des gaps liés
   - Interdépendances identifiées
   - Effort de remédiation optimisé
   - ROI de la consolidation

4. GAPS UNIFIÉS:
   - Description consolidée
   - Périmètre élargi si pertinent
   - Références frameworks multiples
   - Plan de traitement unifié

Retourne une liste JSON des gaps consolidés avec justification des regroupements.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["gap_analyst"]},
                {"role": "user", "content": consolidation_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        try:
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            json_content = response[json_start:json_end]
            consolidated_data = json.loads(json_content)
            
            consolidated_gaps = []
            for gap_data in consolidated_data:
                # Trouver le gap original ou créer un nouveau
                original_gap = next((g for g in gaps if g.id == gap_data.get("id")), None)
                if original_gap:
                    # Mettre à jour avec les données consolidées
                    if gap_data.get("consolidated_description"):
                        original_gap.description = gap_data["consolidated_description"]
                    if gap_data.get("consolidated_title"):
                        original_gap.title = gap_data["consolidated_title"]
                    if gap_data.get("updated_priority"):
                        original_gap.priority_score = float(gap_data["updated_priority"])
                    consolidated_gaps.append(original_gap)
            
            logger.info(f"Gaps consolidés: {len(gaps)} -> {len(consolidated_gaps)}")
            return consolidated_gaps[:25]  # Limiter pour performance
            
        except Exception as e:
            logger.error(f"Erreur consolidation gaps: {str(e)}")
            logger.warning("Utilisation des gaps originaux sans consolidation")
            return gaps[:20]  # Fallback: retourner les gaps originaux

    async def _analyze_gap_impact_with_llm(self, gaps, org_context):
        """Analyse l'impact business avec expertise LLM."""
        
        impact_prompt = f"""
Analyse l'impact business de ces gaps avec ton expertise C-level:

GAPS PRIORITAIRES:
{json.dumps([{
    "id": gap.id,
    "type": gap.type.value,
    "severity": gap.severity.value,
    "title": gap.title,
    "priority": gap.priority_score,
    "business_impact": gap.business_impact
} for gap in gaps[:15]], indent=2)}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:1000]}

En tant qu'expert en analyse d'impact business, évalue:

1. IMPACT FINANCIER:
   - Pertes potentielles directes
   - Coûts indirects et cachés
   - Impact sur le chiffre d'affaires
   - Coûts de mise en conformité

2. IMPACT OPÉRATIONNEL:
   - Disruption des processus
   - Efficacité réduite
   - Charge de travail additionnelle
   - Performance dégradée

3. IMPACT RÉGLEMENTAIRE/LÉGAL:
   - Risques de sanctions
   - Non-conformité réglementaire
   - Exposition juridique
   - Perte de licences/autorisations

4. IMPACT RÉPUTATIONNEL:
   - Confiance client/partenaire
   - Image de marque
   - Compétitivité
   - Attractivité RH

5. IMPACT STRATÉGIQUE:
   - Objectifs business
   - Croissance entravée
   - Innovation freinée
   - Avantage concurrentiel

Pour chaque domaine, fournis:
- Niveau d'impact (critique/élevé/moyen/faible)
- Quantification si possible
- Timeline d'impact
- Mesures d'atténuation

Retourne une analyse JSON structurée avec métriques et insights.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["strategic_advisor"]},
                {"role": "user", "content": impact_prompt}
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
            logger.error(f"Erreur analyse impact: {str(e)}")
            return {
                "error": True,
                "error_message": f"Échec de l'analyse d'impact par LLM: {str(e)}",
                "error_type": "llm_parsing_error",
                "fallback_message": "L'analyse d'impact automatique a échoué. Évaluation manuelle recommandée.",
                "suggested_actions": [
                    "Réviser les données des gaps d'entrée",
                    "Effectuer une analyse d'impact manuelle",
                    "Consulter les parties prenantes métier",
                    "Utiliser une matrice d'impact simplifiée"
                ]
            }

    # Méthodes de traitement des requêtes

    async def _perform_framework_gap_analysis(self, query, intent):
        """Effectue une analyse de gaps spécifique à un framework."""
        
        framework_name = intent.get("frameworks", ["iso27001"])[0]
        try:
            framework = safe_framework_type_conversion(framework_name)
        except:
            framework = FrameworkType.ISO27001
        
        # Collecte d'informations contextuelles
        relevant_docs = await self.document_finder.search_documents(
            f"{framework_name} conformité gap analyse {query.query_text}",
            limit=15
        )
        
        # Extraction d'entités spécifiques au framework
        entities = []
        for doc in relevant_docs[:5]:
            content = doc.get("content", "")
            if content:
                extracted = await self.entity_extractor.extract_entities(
                    content,
                    entity_types=[EntityType.CONTROL, EntityType.REQUIREMENT],
                    framework_context=framework_name
                )
                entities.extend(extracted.get("control", []))
                entities.extend(extracted.get("requirement", []))
        
        # Analyse sophistiquée par LLM
        framework_analysis_prompt = f"""
Effectue une analyse de gaps {framework_name} experte pour: "{query.query_text}"

DOCUMENTS ANALYSÉS: {len(relevant_docs)}
ENTITÉS {framework_name}: {len(entities)}

CONTEXTE ORGANISATIONNEL:
{json.dumps(make_json_serializable(query.context) if query.context else {}, indent=2)[:1000]}

En tant qu'expert {framework_name} senior, analyse:

1. CONFORMITÉ ACTUELLE:
   - Exigences couvertes vs non couvertes
   - Niveau de maturité par domaine
   - Contrôles implémentés vs manquants
   - Documentation vs pratiques

2. GAPS CRITIQUES IDENTIFIÉS:
   - Non-conformités majeures
   - Exigences non satisfaites
   - Contrôles défaillants
   - Preuves manquantes

3. ANALYSE DE MATURITÉ:
   - Niveau actuel par clause
   - Écart vs niveau cible
   - Processus d'amélioration continue
   - Gouvernance du framework

4. PRIORISATION SPÉCIFIQUE:
   - Criticité business par exigence
   - Risques de non-conformité
   - Effort vs impact
   - Dependencies entre contrôles

5. ROADMAP {framework_name}:
   - Plan de mise en conformité
   - Phasage recommandé
   - Ressources nécessaires
   - Timeline réaliste

6. RECOMMANDATIONS EXPERTES:
   - Actions prioritaires
   - Bonnes pratiques sectorielles
   - Optimisations possibles
   - Points d'attention

Fournis une analyse {framework_name} complète et actionnable.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["gap_analyst"]},
                {"role": "user", "content": framework_analysis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        return AgentResponse(
            content=response,
            tools_used=["document_finder", "entity_extractor", "framework_parser"],
            context_used=True,
            sources=self.format_documents_as_sources(relevant_docs[:5]),
            metadata={
                "framework": framework_name,
                "documents_analyzed": len(relevant_docs),
                "entities_found": len(entities),
                "analysis_type": "framework_gap_analysis"
            }
        )

    async def _generate_remediation_plan(self, query, intent):
        """Génère un plan de remédiation sophistiqué."""
        
        # Collecte d'informations sur les gaps existants
        relevant_docs = await self.document_finder.search_documents(
            f"remédiation plan action gap conformité {query.query_text}",
            limit=15
        )
        
        # Extraction d'entités pour le contexte
        gap_entities = []
        for doc in relevant_docs[:5]:
            content = doc.get("content", "")
            if content:
                entities = await self.entity_extractor.extract_entities(
                    content,
                    entity_types=[EntityType.CONTROL, EntityType.RISK, EntityType.REQUIREMENT],
                    framework_context="remediation"
                )
                gap_entities.extend(entities.get("risk", []))
                gap_entities.extend(entities.get("control", []))
        
        # Génération de plan sophistiqué par LLM
        remediation_prompt = f"""
Conçois un plan de remédiation stratégique pour: "{query.query_text}"

DOCUMENTS ANALYSÉS: {len(relevant_docs)}
GAPS/CONTRÔLES IDENTIFIÉS: {len(gap_entities)}

CONTEXTE ORGANISATIONNEL:
{json.dumps(make_json_serializable(query.context) if query.context else {}, indent=2)[:1000]}

En tant qu'expert en transformation et remédiation, conçois:

1. ANALYSE DE SITUATION:
   - État actuel des gaps
   - Impacts business critiques
   - Contraintes organisationnelles
   - Ressources disponibles

2. STRATÉGIE DE REMÉDIATION:
   - Approche globale recommandée
   - Principes directeurs
   - Facteurs clés de succès
   - Risques d'implémentation

3. PLAN D'ACTION DÉTAILLÉ:
   - Phases et étapes
   - Objectifs par phase
   - Livrables attendus
   - Jalons et points de contrôle

4. ALLOCATION DES RESSOURCES:
   - Équipes et compétences
   - Budget par phase
   - Technologies nécessaires
   - Support externe requis

5. GESTION DES RISQUES:
   - Risques identifiés
   - Plans de contingence
   - Mesures préventives
   - Escalation procedures

6. MONITORING ET PILOTAGE:
   - KPI et métriques
   - Fréquence de suivi
   - Reporting stakeholders
   - Ajustements possibles

7. GESTION DU CHANGEMENT:
   - Communication
   - Formation équipes
   - Accompagnement utilisateurs
   - Conduite du changement

Fournis un plan de remédiation complet et opérationnel.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["implementation_expert"]},
                {"role": "user", "content": remediation_prompt}
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
                "gap_entities": len(gap_entities),
                "analysis_type": "remediation_planning"
            }
        )

    async def _prioritize_gaps_strategically(self, query, intent):
        """Priorise les gaps avec une approche stratégique."""
        
        # Collecte d'informations sur les gaps
        relevant_docs = await self.document_finder.search_documents(
            f"priorisation gap risque impact critique {query.query_text}",
            limit=15
        )
        
        # Extraction d'entités gap/risque
        gap_entities = []
        for doc in relevant_docs[:5]:
            content = doc.get("content", "")
            if content:
                entities = await self.entity_extractor.extract_entities(
                    content,
                    entity_types=[EntityType.RISK, EntityType.CONTROL, EntityType.FINDING],
                    framework_context="prioritization"
                )
                gap_entities.extend(entities.get("risk", []))
                gap_entities.extend(entities.get("finding", []))
        
        # Analyse temporelle pour comprendre l'évolution
        from datetime import datetime, timedelta
        end_time = datetime.now()
        start_time = end_time - timedelta(days=180)  # 6 months
        
        # Create dummy entities from documents for trend analysis
        doc_entities = [{"id": f"doc_{i}", "name": doc.get("title", f"Document {i}")} 
                       for i, doc in enumerate(relevant_docs[:3])]
        
        trends = await self.temporal_analyzer.analyze_trends(
            entities=doc_entities,
            metric_types=[MetricType.RISK_LEVEL],
            time_range=(start_time, end_time),
            include_forecasts=False
        )
        
        # Priorisation sophistiquée par LLM
        prioritization_prompt = f"""
Effectue une priorisation stratégique des gaps pour: "{query.query_text}"

DOCUMENTS ANALYSÉS: {len(relevant_docs)}
GAPS/RISQUES IDENTIFIÉS: {len(gap_entities)}
TENDANCES HISTORIQUES: {len(trends.trend_analyses) if trends else 0} points

CONTEXTE ORGANISATIONNEL:
{json.dumps(make_json_serializable(query.context) if query.context else {}, indent=2)[:1000]}

En tant qu'expert en priorisation stratégique, analyse:

1. MATRICE DE CRITICITÉ:
   - Impact business (critique/élevé/moyen/faible)
   - Urgence temporelle (immédiat/court/moyen/long terme)
   - Complexité de résolution (simple/modérée/complexe/très complexe)
   - Coût de remédiation (faible/moyen/élevé/très élevé)

2. CRITÈRES STRATÉGIQUES:
   - Alignement objectifs business
   - Risques réglementaires/légaux
   - Impact sur la réputation
   - Avantage concurrentiel
   - Capacité d'absorption organisationnelle

3. ANALYSE COMPARATIVE:
   - Ranking par criticité globale
   - Trade-offs identifiés
   - Synergies possibles
   - Quick wins vs long-term value

4. SÉQUENCEMENT OPTIMAL:
   - Ordre de traitement recommandé
   - Dépendances entre gaps
   - Parallélisation possible
   - Gestion des ressources

5. RECOMMANDATIONS EXÉCUTIVES:
   - Top 5 gaps prioritaires
   - Justification stratégique
   - Plan de déploiement
   - Allocation budgétaire

6. FRAMEWORK DE PRIORISATION:
   - Méthodologie reproductible
   - Critères de décision
   - Processus de révision
   - Escalation criteria

Fournis une priorisation stratégique claire et justifiée.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["strategic_advisor"]},
                {"role": "user", "content": prioritization_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        return AgentResponse(
            content=response,
            tools_used=["document_finder", "entity_extractor", "temporal_analyzer"],
            context_used=True,
            sources=self.format_documents_as_sources(relevant_docs[:5]),
            metadata={
                "documents_analyzed": len(relevant_docs),
                "gap_entities": len(gap_entities),
                "trend_data_points": len(trends.trend_analyses) if trends else 0,
                "analysis_type": "strategic_prioritization"
            }
        )

    async def _analyze_maturity_gaps(self, query, intent):
        """Analyse les écarts de maturité organisationnelle."""
        
        # Collecte d'informations sur la maturité
        relevant_docs = await self.document_finder.search_documents(
            f"maturité processus gouvernance capabilité {query.query_text}",
            limit=15
        )
        
        # Extraction d'entités pour évaluer la maturité
        maturity_entities = []
        for doc in relevant_docs[:5]:
            content = doc.get("content", "")
            if content:
                entities = await self.entity_extractor.extract_entities(
                    content,
                    entity_types=[EntityType.CONTROL, EntityType.REQUIREMENT],
                    framework_context="maturity_assessment"
                )
                maturity_entities.extend(entities.get("control", []))
                maturity_entities.extend(entities.get("requirement", []))
        
        # Analyse temporelle pour l'évolution de maturité
        from datetime import datetime, timedelta
        end_time = datetime.now()
        start_time = end_time - timedelta(days=365)  # 12 months
        
        # Create dummy entities from documents for trend analysis
        doc_entities = [{"id": f"doc_{i}", "name": doc.get("title", f"Document {i}")} 
                       for i, doc in enumerate(relevant_docs[:3])]
        
        maturity_trends = await self.temporal_analyzer.analyze_trends(
            entities=doc_entities,
            metric_types=[MetricType.CONTROL_EFFECTIVENESS],
            time_range=(start_time, end_time),
            include_forecasts=False
        )
        
        # Analyse de maturité sophistiquée par LLM
        maturity_prompt = f"""
Effectue une analyse de maturité organisationnelle pour: "{query.query_text}"

DOCUMENTS ANALYSÉS: {len(relevant_docs)}
ENTITÉS MATURITÉ: {len(maturity_entities)}
TENDANCES MATURITÉ: {len(maturity_trends.trend_analyses) if maturity_trends else 0} points

CONTEXTE ORGANISATIONNEL:
{json.dumps(make_json_serializable(query.context) if query.context else {}, indent=2)[:1000]}

En tant qu'expert en évaluation de maturité organisationnelle, analyse:

1. MODÈLE DE MATURITÉ:
   - Niveau 1: Initial/Ad-hoc
   - Niveau 2: Reproductible/Géré
   - Niveau 3: Défini/Standardisé
   - Niveau 4: Quantitatif/Maîtrisé
   - Niveau 5: Optimisé/Innovation

2. ÉVALUATION PAR DOMAINE:
   - Gouvernance et stratégie
   - Processus et procédures
   - Organisation et compétences
   - Technologies et outils
   - Mesure et amélioration continue

3. GAPS DE MATURITÉ IDENTIFIÉS:
   - Écart entre niveau actuel et cible
   - Capacités manquantes
   - Processus immatures
   - Compétences à développer

4. ANALYSE COMPARATIVE:
   - Benchmarking sectoriel
   - Meilleures pratiques industrie
   - Standards de référence
   - Objectifs organisationnels

5. ROADMAP DE MATURITÉ:
   - Trajectoire d'évolution
   - Jalons de progression
   - Investissements requis
   - Timeline de transformation

6. FACTEURS CLÉS DE SUCCÈS:
   - Leadership et engagement
   - Culture organisationnelle
   - Gestion du changement
   - Ressources et compétences

7. MÉTRIQUES DE PROGRESSION:
   - Indicateurs de maturité
   - Suivi de l'évolution
   - Targets intermédiaires
   - Mesures correctives

Fournis une évaluation de maturité complète avec recommandations d'évolution.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["gap_analyst"]},
                {"role": "user", "content": maturity_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        return AgentResponse(
            content=response,
            tools_used=["document_finder", "entity_extractor", "temporal_analyzer"],
            context_used=True,
            sources=self.format_documents_as_sources(relevant_docs[:5]),
            metadata={
                "documents_analyzed": len(relevant_docs),
                "maturity_entities": len(maturity_entities),
                "trend_data_points": len(maturity_trends.trend_analyses) if maturity_trends else 0,
                "analysis_type": "maturity_gap_analysis"
            }
        )

    async def _general_gap_analysis(self, query, intent):
        """Analyse générale de gaps avec approche holistique."""
        
        # Collecte d'informations générales
        relevant_docs = await self.document_finder.search_documents(
            f"gap écart conformité gouvernance risque {query.query_text}",
            limit=20
        )
        
        # Extraction d'entités multiples types
        all_entities = []
        for doc in relevant_docs[:8]:
            content = doc.get("content", "")
            if content:
                entities = await self.entity_extractor.extract_entities(
                    content,
                    entity_types=[EntityType.CONTROL, EntityType.RISK, EntityType.REQUIREMENT, EntityType.FINDING],
                    framework_context="general_analysis"
                )
                for entity_type in entities:
                    all_entities.extend(entities[entity_type])
        
        # Analyse croisée pour identifier les relations
        cross_refs = await self.cross_reference_tool.analyze_relationships(
            [doc.get("content", "") for doc in relevant_docs[:5]],
            relation_types=[RelationType.CONTROLS, RelationType.IMPLEMENTS, RelationType.AFFECTS]
        )
        
        # Analyse temporelle pour comprendre l'évolution
        from datetime import datetime, timedelta
        end_time = datetime.now()
        start_time = end_time - timedelta(days=180)  # 6 months
        
        # Create dummy entities from documents for trend analysis
        doc_entities = [{"id": f"doc_{i}", "name": doc.get("title", f"Document {i}")} 
                       for i, doc in enumerate(relevant_docs[:3])]
        
        trends = await self.temporal_analyzer.analyze_trends(
            entities=doc_entities,
            metric_types=[MetricType.COMPLIANCE_SCORE],
            time_range=(start_time, end_time),
            include_forecasts=False
        )
        
        # Analyse générale sophistiquée par LLM
        general_analysis_prompt = f"""
Effectue une analyse de gaps holistique pour: "{query.query_text}"

DOCUMENTS ANALYSÉS: {len(relevant_docs)}
ENTITÉS IDENTIFIÉES: {len(all_entities)}
RELATIONS CROISÉES: {len(cross_refs.relationships)}
TENDANCES HISTORIQUES: {len(trends.trend_analyses) if trends else 0} points

CONTEXTE ORGANISATIONNEL:
{json.dumps(make_json_serializable(query.context) if query.context else {}, indent=2)[:1000]}

En tant qu'expert senior en analyse organisationnelle, effectue:

1. DIAGNOSTIC GLOBAL:
   - Vue d'ensemble des gaps identifiés
   - Domaines d'impact principaux
   - Criticité et urgence
   - Tendances et évolutions

2. CATÉGORISATION DES GAPS:
   - Gaps de conformité réglementaire
   - Gaps de gouvernance
   - Gaps de gestion des risques
   - Gaps opérationnels et processus
   - Gaps technologiques et sécurité

3. ANALYSE DES CAUSES RACINES:
   - Facteurs organisationnels
   - Défaillances processus
   - Lacunes compétences
   - Contraintes ressources
   - Résistances culturelles

4. IMPACT BUSINESS GLOBAL:
   - Conséquences opérationnelles
   - Risques financiers
   - Exposition réglementaire
   - Impact réputationnel
   - Avantage concurrentiel

5. INTERDÉPENDANCES ET SYNERGIES:
   - Relations entre gaps
   - Effets domino potentiels
   - Opportunités de traitement groupé
   - Optimisations possibles

6. PRIORISATION HOLISTIQUE:
   - Matrice impact/effort
   - Quick wins identifiés
   - Projets structurants
   - Transformation long terme

7. APPROCHE STRATÉGIQUE:
   - Vision globale de remédiation
   - Phasage recommandé
   - Allocation des ressources
   - Gouvernance du programme

8. PLAN D'ACTION INTÉGRÉ:
   - Actions immédiates
   - Projets moyen terme
   - Transformation long terme
   - Métriques de suivi

Fournis une analyse complète avec vision stratégique et recommandations actionables.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["strategic_advisor"]},
                {"role": "user", "content": general_analysis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        return AgentResponse(
            content=response,
            tools_used=["document_finder", "entity_extractor", "cross_reference_tool", "temporal_analyzer"],
            context_used=True,
            sources=self.format_documents_as_sources(relevant_docs[:5]),
            metadata={
                "documents_analyzed": len(relevant_docs),
                "entities_found": len(all_entities),
                "relationships_found": len(cross_refs.relationships),
                "trend_data_points": len(trends.trend_analyses) if trends else 0,
                "analysis_type": "general_gap_analysis"
            }
        )

    # Stubs pour autres méthodes
    async def _analyze_remediation_scope_with_llm(self, gaps, org_context):
        """Analyse la portée de remédiation avec LLM."""
        
        scope_prompt = f"""
Analyse la portée de remédiation pour ces gaps:

GAPS À TRAITER:
{json.dumps([{
    "id": gap.id,
    "type": gap.type.value,
    "severity": gap.severity.value,
    "description": gap.description[:200]
} for gap in gaps], indent=2)}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:1000]}

Analyse:
1. COMPLEXITÉ GLOBALE (simple/modérée/complexe/très complexe)
2. PORTÉE ORGANISATIONNELLE (département/division/entreprise/groupe)
3. INTERDÉPENDANCES entre gaps
4. IMPACT TRANSFORMATION requis
5. RESSOURCES NÉCESSAIRES estimées

Retourne une analyse JSON structurée.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["implementation_expert"]},
                {"role": "user", "content": scope_prompt}
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
            logger.error(f"Erreur analyse portée remédiation: {str(e)}")
            return {
                "error": True,
                "error_message": "Échec de l'analyse de portée par LLM",
                "fallback_message": "Analyse manuelle de la portée requise"
            }

    async def _design_remediation_strategy_with_llm(self, analysis, org_context, constraints):
        """Conçoit une stratégie de remédiation avec LLM."""
        
        strategy_prompt = f"""
Conçois une stratégie de remédiation optimale:

ANALYSE PORTÉE:
{json.dumps(analysis, indent=2, default=str)[:1500]}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:1000]}

CONTRAINTES:
{json.dumps(constraints or {}, indent=2)[:500]}

Définis:
1. APPROCHE STRATÉGIQUE (big bang/progressive/hybride)
2. PRINCIPES DIRECTEURS
3. FACTEURS CLÉS DE SUCCÈS
4. CRITÈRES DE SUCCÈS mesurables
5. STRATÉGIES D'ATTÉNUATION des risques

Retourne une stratégie JSON structurée.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["strategic_advisor"]},
                {"role": "user", "content": strategy_prompt}
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
            logger.error(f"Erreur conception stratégie: {str(e)}")
            return {
                "error": True,
                "error_message": "Échec de la conception stratégique par LLM",
                "fallback_message": "Stratégie de remédiation manuelle requise"
            }

    async def _design_remediation_phases_with_llm(self, gaps, strategy, org_context):
        """Conçoit les phases de remédiation avec LLM."""
        
        phases_prompt = f"""
Conçois un phasage optimal de remédiation:

GAPS PRIORITAIRES:
{json.dumps([{
    "id": gap.id,
    "priority": gap.priority_score,
    "effort": gap.remediation_effort,
    "timeline": gap.remediation_timeline
} for gap in gaps[:15]], indent=2)}

STRATÉGIE:
{json.dumps(strategy, indent=2, default=str)[:1000]}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:800]}

Définis 3-4 phases avec:
1. OBJECTIFS SPÉCIFIQUES par phase
2. GAPS TRAITÉS dans chaque phase
3. LIVRABLES ATTENDUS
4. DURÉE ET JALONS
5. PRÉREQUIS ET DÉPENDANCES

Retourne un plan de phases JSON structuré.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["implementation_expert"]},
                {"role": "user", "content": phases_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        try:
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            json_content = response[json_start:json_end]
            return json.loads(json_content)
        except Exception as e:
            logger.error(f"Erreur conception phases: {str(e)}")
            return [{
                "error": True,
                "error_message": "Échec de la conception des phases par LLM",
                "fallback_message": "Phasage manuel requis"
            }]

    async def _analyze_resource_requirements_with_llm(self, phases, org_context):
        """Analyse les besoins en ressources avec LLM."""
        
        resources_prompt = f"""
Analyse les besoins en ressources pour ce plan:

PHASES PLANIFIÉES:
{json.dumps(phases, indent=2, default=str)[:2000]}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:800]}

Estime pour chaque phase:
1. RESSOURCES HUMAINES (ETP internes/externes)
2. BUDGET ESTIMÉ (€)
3. COMPÉTENCES SPÉCIALISÉES requises
4. TECHNOLOGIES ET OUTILS
5. FORMATION NÉCESSAIRE

Retourne une analyse JSON détaillée des ressources.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["implementation_expert"]},
                {"role": "user", "content": resources_prompt}
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
            logger.error(f"Erreur analyse ressources: {str(e)}")
            return {
                "error": True,
                "error_message": "Échec de l'analyse des ressources par LLM",
                "fallback_message": "Estimation manuelle des ressources requise"
            }

    async def _design_implementation_timeline_with_llm(self, phases, constraints):
        """Conçoit la timeline d'implémentation avec LLM."""
        
        timeline_prompt = f"""
Conçois une timeline optimale d'implémentation:

PHASES À PLANIFIER:
{json.dumps(phases, indent=2, default=str)[:2000]}

CONTRAINTES:
{json.dumps(constraints or {}, indent=2)[:500]}

Définis:
1. DATES DE DÉBUT/FIN par phase
2. JALONS CRITIQUES
3. CHEMIN CRITIQUE identifié
4. BUFFER/CONTINGENCE temps
5. POINTS DE DÉCISION GO/NO-GO

Retourne une timeline JSON structurée avec dates et jalons.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["implementation_expert"]},
                {"role": "user", "content": timeline_prompt}
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
            logger.error(f"Erreur conception timeline: {str(e)}")
            return {
                "error": True,
                "error_message": "Échec de la conception de timeline par LLM",
                "fallback_message": "Planification temporelle manuelle requise"
            }

    async def _design_monitoring_framework_with_llm(self, gaps, phases):
        """Conçoit le framework de monitoring avec LLM."""
        
        monitoring_prompt = f"""
Conçois un framework de monitoring pour ce programme:

GAPS CIBLÉS:
{json.dumps([gap.id for gap in gaps], indent=2)}

PHASES PROGRAMME:
{json.dumps([{"phase": p.get("phase", ""), "duration": p.get("duration", "")} for p in phases], indent=2)}

Définis:
1. KPI STRATÉGIQUES (5-7 indicateurs clés)
2. MÉTRIQUES OPÉRATIONNELLES par phase
3. FRÉQUENCE DE REPORTING (daily/weekly/monthly)
4. DASHBOARDS ET VISUALISATIONS
5. PROCESSUS D'ESCALATION
6. REVUES PÉRIODIQUES (steering committee)

Retourne un framework JSON de monitoring complet.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["implementation_expert"]},
                {"role": "user", "content": monitoring_prompt}
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
            logger.error(f"Erreur framework monitoring: {str(e)}")
            return {
                "error": True,
                "error_message": "Échec de la conception du framework de monitoring par LLM",
                "fallback_message": "Framework de suivi manuel requis"
            }

    async def _calculate_roi_projection_with_llm(self, gaps, resources, org_context):
        """Calcule la projection ROI avec LLM."""
        
        roi_prompt = f"""
Calcule la projection ROI pour ce programme de remédiation:

GAPS TRAITÉS:
{json.dumps([{
    "id": gap.id,
    "business_impact": gap.business_impact,
    "remediation_cost": gap.remediation_cost
} for gap in gaps[:10]], indent=2, default=str)}

RESSOURCES ALLOUÉES:
{json.dumps(resources, indent=2, default=str)[:1500]}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:800]}

Calcule:
1. COÛTS TOTAUX programme
2. BÉNÉFICES QUANTIFIABLES (€/an)
3. ROI PROJETÉ (%)
4. PÉRIODE DE RETOUR (mois)
5. VAN sur 3 ans
6. ANALYSE DE SENSIBILITÉ

Retourne une analyse ROI JSON détaillée.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["strategic_advisor"]},
                {"role": "user", "content": roi_prompt}
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
            logger.error(f"Erreur calcul ROI: {str(e)}")
            return {
                "error": True,
                "error_message": "Échec du calcul ROI par LLM",
                "fallback_message": "Analyse financière manuelle requise"
            }

    async def _assess_gap_risks_with_llm(self, gaps, org_context):
        """Évalue les risques liés aux gaps avec expertise LLM."""
        
        risk_assessment_prompt = f"""
Évalue les risques de ces gaps avec ton expertise en risk management:

GAPS CRITIQUES:
{json.dumps([{
    "id": gap.id,
    "type": gap.type.value,
    "severity": gap.severity.value,
    "title": gap.title,
    "business_impact": gap.business_impact,
    "remediation_effort": gap.remediation_effort
} for gap in gaps[:10]], indent=2, default=str)}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:1000]}

En tant qu'expert en gestion des risques, analyse:

1. RISQUES D'IMPLÉMENTATION:
   - Complexité technique
   - Résistance au changement
   - Disponibilité des ressources
   - Interdépendances projets
   - Risques temporels

2. RISQUES DE NON-TRAITEMENT:
   - Exposition réglementaire
   - Vulnérabilités sécurité
   - Impact business croissant
   - Détérioration réputation
   - Perte avantage concurrentiel

3. RISQUES OPÉRATIONNELS:
   - Disruption processus
   - Performance dégradée
   - Qualité service
   - Satisfaction client
   - Productivité équipes

4. RISQUES FINANCIERS:
   - Dépassement budget
   - Pertes revenus
   - Sanctions pénalités
   - Coûts cachés
   - ROI non atteint

5. STRATÉGIES D'ATTÉNUATION:
   - Plans de contingence
   - Mesures préventives
   - Monitoring proactif
   - Escalation procedures

Pour chaque catégorie, fournis:
- Niveau de risque (critique/élevé/moyen/faible)
- Probabilité d'occurrence
- Impact potentiel
- Mesures d'atténuation
- Indicateurs de surveillance

Retourne une évaluation JSON structurée avec matrice de risques.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["gap_analyst"]},
                {"role": "user", "content": risk_assessment_prompt}
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
            logger.error(f"Erreur évaluation risques gaps: {str(e)}")
            return {
                "error": True,
                "error_message": f"Échec de l'évaluation des risques par LLM: {str(e)}",
                "error_type": "llm_parsing_error",
                "fallback_message": "L'évaluation automatique des risques a échoué. Analyse manuelle requise.",
                "suggested_actions": [
                    "Effectuer une évaluation de risques manuelle",
                    "Consulter un expert en gestion des risques",
                    "Utiliser une matrice de risques standard",
                    "Réviser les données des gaps et réessayer"
                ]
            }

    async def _generate_executive_summary_with_llm(self, gaps, impact, recommendations, org_context):
        """Génère une synthèse exécutive sophistiquée."""
        
        executive_prompt = f"""
Rédige une synthèse exécutive stratégique pour la direction:

GAPS IDENTIFIÉS:
- Total: {len(gaps)}
- Critiques: {len([g for g in gaps if g.severity == GapSeverity.CRITICAL])}
- Élevés: {len([g for g in gaps if g.severity == GapSeverity.HIGH])}

IMPACT BUSINESS ANALYSÉ:
{json.dumps(impact, indent=2, default=str)[:1500]}

RECOMMANDATIONS CLÉS:
{json.dumps(recommendations[:3], indent=2, default=str)[:1000]}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:800]}

En tant qu'expert conseil C-level, rédige une synthèse de 4-5 paragraphes:

1. SITUATION ACTUELLE:
   - État des lieux objectif
   - Principaux enjeux identifiés
   - Urgence et criticité
   - Contexte organisationnel

2. IMPACT STRATÉGIQUE:
   - Conséquences business
   - Risques majeurs
   - Opportunités manquées
   - Avantage concurrentiel

3. RECOMMANDATIONS EXÉCUTIVES:
   - Approche stratégique
   - Priorisation intelligente
   - Investissements requis
   - ROI attendu

4. PLAN D'ACTION:
   - Étapes critiques
   - Timeline exécutive
   - Ressources nécessaires
   - Facteurs clés de succès

5. APPEL À L'ACTION:
   - Décisions immédiates
   - Sponsorship requis
   - Communication stakeholders
   - Gouvernance programme

Style: professionnel, concis, orienté décision, perspective C-suite.
Longueur: 400-500 mots maximum.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["strategic_advisor"]},
                {"role": "user", "content": executive_prompt}
            ],
            model="gpt-4.1",
            temperature=0.3
        )
        
        return response.strip()

    async def _define_success_metrics_with_llm(self, gaps):
        """Définit des métriques de succès sophistiquées."""
        
        metrics_prompt = f"""
Définis des métriques de succès pour cette transformation gaps:

GAPS À TRAITER:
{json.dumps([{
    "id": gap.id,
    "type": gap.type.value,
    "severity": gap.severity.value,
    "title": gap.title
} for gap in gaps[:10]], indent=2)}

En tant qu'expert en pilotage de performance, définis:

1. MÉTRIQUES DE RÉSULTAT:
   - Réduction gaps par sévérité
   - Amélioration scores conformité
   - Réduction exposition risques
   - ROI programme

2. MÉTRIQUES DE PROCESSUS:
   - Avancement implémentation
   - Respect timeline/budget
   - Qualité livrables
   - Satisfaction stakeholders

3. MÉTRIQUES D'IMPACT:
   - Performance opérationnelle
   - Efficacité processus
   - Maturité gouvernance
   - Résilience organisationnelle

4. MÉTRIQUES AVANCÉES:
   - Temps de détection gaps
   - Rapidité de remédiation
   - Récurrence incidents
   - Innovation facilitée

Pour chaque métrique, définis:
- Indicateur précis
- Méthode de mesure
- Fréquence de suivi
- Cibles et seuils
- Responsable du suivi

Retourne une liste JSON de métriques SMART avec baselines et cibles.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["implementation_expert"]},
                {"role": "user", "content": metrics_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        try:
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            json_content = response[json_start:json_end]
            metrics_data = json.loads(json_content)
            return [metric.get("name", metric) if isinstance(metric, dict) else metric for metric in metrics_data]
        except Exception as e:
            logger.error(f"Erreur définition métriques: {str(e)}")
            logger.warning("Utilisation de métriques par défaut")
            return [
                "⚠️ ERREUR: Définition automatique des métriques échouée",
                "Action requise: Définir manuellement les métriques de succès",
                "Suggestion: Consulter un expert en pilotage de performance",
                "Fallback: Utiliser des métriques standards du secteur"
            ]

    async def _generate_implementation_roadmap_with_llm(self, gaps, recommendations, org_context):
        """Génère une roadmap d'implémentation sophistiquée."""
        
        roadmap_prompt = f"""
Conçois une roadmap d'implémentation stratégique avec ton expertise en transformation:

GAPS À TRAITER:
{json.dumps([{
    "id": gap.id,
    "title": gap.title,
    "severity": gap.severity.value,
    "priority": gap.priority_score,
    "effort": gap.remediation_effort,
    "timeline": gap.remediation_timeline
} for gap in gaps[:10]], indent=2)}

RECOMMANDATIONS STRATÉGIQUES:
{json.dumps(recommendations[:5], indent=2, default=str)[:1500]}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:1000]}

En tant qu'expert en transformation organisationnelle, conçois:

1. PHASAGE STRATÉGIQUE:
   - Phase 1: Quick wins (0-3 mois)
   - Phase 2: Fondations (3-12 mois)
   - Phase 3: Optimisation (12-24 mois)
   - Phase 4: Excellence (24+ mois)

2. SÉQUENCEMENT OPTIMAL:
   - Prérequis et dépendances
   - Gestion des risques
   - Capacité d'absorption
   - Synergies entre projets

3. JALONS ET LIVRABLES:
   - Objectifs par phase
   - Livrables clés
   - Critères de succès
   - Points de contrôle

4. ALLOCATION DES RESSOURCES:
   - Besoins humains par phase
   - Budget requis
   - Compétences nécessaires
   - Support externe

5. GESTION DES RISQUES:
   - Risques d'implémentation
   - Plans de contingence
   - Stratégies d'atténuation
   - Escalation procedures

Retourne une roadmap JSON détaillée avec timeline, ressources et métriques.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["implementation_expert"]},
                {"role": "user", "content": roadmap_prompt}
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
            logger.error(f"Erreur génération roadmap: {str(e)}")
            return {
                "error": True,
                "error_message": f"Échec de la génération de roadmap par LLM: {str(e)}",
                "error_type": "llm_parsing_error",
                "fallback_message": "La génération automatique de roadmap a échoué. Planification manuelle requise.",
                "suggested_actions": [
                    "Créer une roadmap manuelle basée sur les gaps prioritaires",
                    "Consulter un expert en gestion de projet",
                    "Utiliser un outil de planification externe",
                    "Réviser les données d'entrée et réessayer"
                ]
            }

    async def _perform_cost_benefit_analysis_with_llm(self, gaps, roadmap, org_context):
        """Effectue une analyse coût-bénéfice sophistiquée."""
        
        cost_benefit_prompt = f"""
Effectue une analyse coût-bénéfice experte pour cette transformation:

GAPS À TRAITER:
{json.dumps([{
    "id": gap.id,
    "severity": gap.severity.value,
    "business_impact": gap.business_impact,
    "remediation_cost": gap.remediation_cost,
    "remediation_effort": gap.remediation_effort
} for gap in gaps[:10]], indent=2, default=str)}

ROADMAP D'IMPLÉMENTATION:
{json.dumps(roadmap, indent=2, default=str)[:2000]}

CONTEXTE ORGANISATIONNEL:
{json.dumps(org_context, indent=2)[:1000]}

En tant qu'expert financier en transformation, analyse:

1. COÛTS D'IMPLÉMENTATION:
   - Coûts directs par phase
   - Ressources humaines internes
   - Support externe/conseil
   - Technologies et outils
   - Formation et change management

2. COÛTS DE NON-ACTION:
   - Risques financiers
   - Sanctions réglementaires
   - Pertes opérationnelles
   - Impact réputationnel
   - Coûts d'opportunité

3. BÉNÉFICES QUANTIFIABLES:
   - Réduction des risques
   - Efficacité opérationnelle
   - Économies de coûts
   - Nouveaux revenus
   - Avantages compétitifs

4. BÉNÉFICES QUALITATIFS:
   - Amélioration gouvernance
   - Confiance stakeholders
   - Résilience organisationnelle
   - Innovation facilitée
   - Attractivité employeur

5. ANALYSE ROI:
   - ROI par phase
   - ROI global programme
   - Période de retour
   - VAN et TIR
   - Analyse de sensibilité

Fournis une analyse financière complète avec business case.
Retourne un JSON structuré avec métriques financières détaillées.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["strategic_advisor"]},
                {"role": "user", "content": cost_benefit_prompt}
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
            logger.error(f"Erreur analyse coût-bénéfice: {str(e)}")
            return {
                "error": True,
                "error_message": f"Échec de l'analyse coût-bénéfice par LLM: {str(e)}",
                "error_type": "llm_parsing_error",
                "fallback_message": "L'analyse automatique a échoué. Une analyse manuelle est recommandée.",
                "suggested_actions": [
                    "Réviser les données d'entrée pour l'analyse",
                    "Effectuer une analyse financière manuelle",
                    "Consulter un expert financier",
                    "Réessayer l'analyse avec des paramètres différents"
                ]
            }


# Factory function
def get_gap_analysis_module(llm_client = None):
    """Factory function pour obtenir une instance du module d'analyse de gaps."""
    return GapAnalysisModule(llm_client=llm_client) 