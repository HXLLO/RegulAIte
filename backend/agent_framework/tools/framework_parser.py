"""
Framework Parser - Analyseur sophistiqué de frameworks de conformité.
Utilise l'IA pour parser, mapper et analyser intelligemment les frameworks réglementaires.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import re

from ..integrations.llm_integration import get_llm_client

logger = logging.getLogger(__name__)

def extract_json_from_llm_response(response: str) -> Dict[str, Any]:
    """
    Extrait de manière robuste un JSON d'une réponse LLM qui peut contenir du texte supplémentaire.
    
    Args:
        response: Réponse complète du LLM
        
    Returns:
        Dictionnaire JSON parsé ou dictionnaire vide en cas d'erreur
    """
    if not response or not response.strip():
        logger.warning("Empty LLM response received")
        return {}
    
    # Clean up the response
    cleaned_response = response.strip()
    
    # Strategy 1: Try to find JSON within code blocks
    json_code_block_patterns = [
        r'```json\s*(\{.*?\})\s*```',
        r'```\s*(\{.*?\})\s*```',
    ]
    
    for pattern in json_code_block_patterns:
        matches = re.findall(pattern, cleaned_response, re.DOTALL | re.IGNORECASE)
        if matches:
            try:
                return json.loads(matches[0])
            except json.JSONDecodeError:
                continue
    
    # Strategy 2: Find JSON by counting braces (most robust for nested objects)
    json_start = cleaned_response.find('{')
    if json_start == -1:
        logger.warning("No opening brace found in LLM response")
        return {}
    
    # Count braces to find the complete JSON object
    brace_count = 0
    json_end = json_start
    in_string = False
    escape_next = False
    
    for i, char in enumerate(cleaned_response[json_start:], json_start):
        if escape_next:
            escape_next = False
            continue
            
        if char == '\\':
            escape_next = True
            continue
            
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
            
        if not in_string:
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    json_end = i + 1
                    break
    
    if brace_count != 0:
        logger.warning("Unbalanced braces in JSON, trying simpler extraction")
        # Fallback to original method
        json_end = cleaned_response.rfind('}') + 1
    
    json_content = cleaned_response[json_start:json_end]
    
    # Strategy 3: Try multiple parsing approaches
    parsing_strategies = [
        # Try exact extraction
        lambda: json.loads(json_content),
        # Try with trailing content removed
        lambda: json.loads(json_content.rstrip()),
        # Try finding last valid JSON
        lambda: json.loads(json_content[:json_content.rfind('}') + 1]),
    ]
    
    for strategy in parsing_strategies:
        try:
            parsed_json = strategy()
            if isinstance(parsed_json, dict):
                logger.debug(f"Successfully parsed JSON using strategy: {strategy.__name__}")
                return parsed_json
        except (json.JSONDecodeError, ValueError, AttributeError) as e:
            logger.debug(f"JSON parsing strategy failed: {str(e)}")
            continue
    
    # Strategy 4: If all else fails, try to extract individual key-value pairs
    logger.warning("All JSON parsing strategies failed, attempting key-value extraction")
    try:
        # Look for key patterns in the response
        patterns = {
            'requirements': r'"requirements"\s*:\s*\[(.*?)\]',
            'mappings': r'"mappings"\s*:\s*\[(.*?)\]',
            'gaps': r'"gaps"\s*:\s*\[(.*?)\]',
            'analysis': r'"analysis"\s*:\s*\{(.*?)\}',
        }
        
        result = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, cleaned_response, re.DOTALL)
            if match:
                try:
                    result[key] = json.loads(f'[{match.group(1)}]' if key.endswith('s') and key != 'analysis' else f'{{{match.group(1)}}}')
                except:
                    continue
        
        if result:
            logger.info("Partial JSON extraction successful")
            return result
            
    except Exception as e:
        logger.error(f"Key-value extraction failed: {str(e)}")
    
    # Final fallback
    logger.error("All JSON extraction methods failed")
    logger.debug(f"Problematic response (first 500 chars): {cleaned_response[:500]}")
    return {}

class FrameworkType(Enum):
    """Types de frameworks supportés."""
    ISO27001 = "iso27001"
    RGPD = "rgpd"
    DORA = "dora"
    NIST = "nist"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    CUSTOM = "custom"

def safe_framework_type_conversion(framework_str: str) -> FrameworkType:
    """
    Convertit de manière sécurisée une chaîne en FrameworkType.
    Gère les différences de casse et les variations communes.
    """
    if isinstance(framework_str, FrameworkType):
        return framework_str
    
    # Normaliser la chaîne (minuscule, espaces supprimés)
    normalized = framework_str.lower().strip()
    
    # Mappings spéciaux pour les variations communes
    mappings = {
        "rgpd": FrameworkType.RGPD,
        "gdpr": FrameworkType.RGPD,
        "iso27001": FrameworkType.ISO27001,
        "iso_27001": FrameworkType.ISO27001,
        "iso-27001": FrameworkType.ISO27001,
        "nist": FrameworkType.NIST,
        "dora": FrameworkType.DORA,
        "sox": FrameworkType.SOX,
        "pci_dss": FrameworkType.PCI_DSS,
        "pci-dss": FrameworkType.PCI_DSS,
        "pcidss": FrameworkType.PCI_DSS,
        "custom": FrameworkType.CUSTOM
    }
    
    if normalized in mappings:
        return mappings[normalized]
    
    # Essayer la conversion directe avec la valeur enum
    try:
        return FrameworkType(normalized)
    except ValueError:
        pass
    
    # Essayer avec le nom de l'enum (majuscules)
    try:
        return FrameworkType[framework_str.upper()]
    except KeyError:
        pass
    
    # Si rien ne marche, lever une erreur explicite
    valid_values = [ft.value for ft in FrameworkType] + list(mappings.keys())
    raise ValueError(f"Framework '{framework_str}' n'est pas reconnu. Valeurs valides: {valid_values}")

class RequirementType(Enum):
    """Types d'exigences dans les frameworks."""
    CONTROL = "control"
    PRINCIPLE = "principle"
    PROCESS = "process"
    DOCUMENTATION = "documentation"
    ASSESSMENT = "assessment"
    REPORTING = "reporting"

class ImplementationLevel(Enum):
    """Niveaux d'implémentation."""
    NOT_IMPLEMENTED = "not_implemented"
    PARTIALLY_IMPLEMENTED = "partially_implemented"
    LARGELY_IMPLEMENTED = "largely_implemented"
    FULLY_IMPLEMENTED = "fully_implemented"
    NOT_APPLICABLE = "not_applicable"

@dataclass
class FrameworkRequirement:
    """Exigence d'un framework avec analyse LLM."""
    id: str
    framework: FrameworkType
    section: str
    title: str
    description: str
    requirement_type: RequirementType
    mandatory: bool
    implementation_guidance: str
    evidence_required: List[str]
    related_requirements: List[str]
    risk_areas: List[str]
    business_impact: str
    implementation_complexity: str
    ai_analysis: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.evidence_required is None:
            self.evidence_required = []
        if self.related_requirements is None:
            self.related_requirements = []
        if self.risk_areas is None:
            self.risk_areas = []
        if self.ai_analysis is None:
            self.ai_analysis = {}

@dataclass
class FrameworkMapping:
    """Mapping entre frameworks analysé par LLM."""
    source_framework: FrameworkType
    target_framework: FrameworkType
    source_requirement: str
    target_requirement: str
    mapping_type: str  # full, partial, conceptual, none
    confidence_score: float
    mapping_rationale: str
    implementation_notes: str

@dataclass
class ComplianceGap:
    """Gap de conformité identifié par LLM."""
    requirement_id: str
    framework: FrameworkType
    gap_type: str
    severity: str
    description: str
    current_state: str
    target_state: str
    remediation_plan: List[str]
    estimated_effort: str
    business_justification: str

class FrameworkParser:
    """
    Analyseur sophistiqué de frameworks utilisant l'IA pour une compréhension approfondie.
    """
    
    def __init__(self):
        self.llm_client = get_llm_client()
        
        # Cache des analyses LLM
        self.analysis_cache: Dict[str, Dict[str, Any]] = {}
        
        # Prompts sophistiqués pour différents types d'analyse
        self.system_prompts = {
            "framework_analyst": """
Tu es un expert senior en conformité réglementaire et cybersécurité avec 15+ ans d'expérience.
Tu maîtrises parfaitement les frameworks ISO27001, RGPD, DORA, NIST, SOX, PCI-DSS.
Tu analyses les exigences avec une approche holistique incluant:
- Impact business et opérationnel
- Complexité d'implémentation
- Interdépendances entre exigences
- Risques de non-conformité
- Meilleures pratiques d'implémentation
- Considérations sectorielles spécifiques

Réponds TOUJOURS en français avec une expertise pointue et des recommandations actionables.
""",
            
            "mapping_expert": """
Tu es un expert en mapping de frameworks de conformité avec une connaissance encyclopédique.
Tu identifies les correspondances subtiles entre frameworks en analysant:
- L'intention réglementaire sous-jacente
- Les objectifs de contrôle équivalents
- Les différences de granularité
- Les spécificités sectorielles
- Les évolutions réglementaires

Tu fournis des mappings précis avec des justifications détaillées.
""",
            
            "gap_analyst": """
Tu es un consultant senior spécialisé dans l'analyse de gaps de conformité.
Tu identifies avec précision:
- Les écarts entre état actuel et exigences
- Les risques associés aux gaps
- Les priorités de remédiation
- Les efforts d'implémentation
- Les interdépendances organisationnelles

Tu fournis des plans de remédiation pragmatiques et réalisables.
"""
        }
        
        # Knowledge base des frameworks (sera enrichie par LLM)
        self.framework_knowledge = {
            FrameworkType.ISO27001: {
                "description": "Standard international de management de la sécurité de l'information",
                "version": "2022",
                "domains": ["politique", "organisation", "ressources_humaines", "gestion_actifs", 
                          "controle_acces", "cryptographie", "securite_physique", "exploitation",
                          "communications", "developpement", "fournisseurs", "incidents", "continuite", "conformite"],
                "control_count": 93
            },
            FrameworkType.RGPD: {
                "description": "Règlement Général sur la Protection des Données",
                "version": "2018",
                "domains": ["licéité", "loyauté", "minimisation", "exactitude", "conservation", 
                          "intégrité", "confidentialité", "responsabilité"],
                "article_count": 99
            },
            FrameworkType.DORA: {
                "description": "Digital Operational Resilience Act",
                "version": "2024",
                "domains": ["gouvernance_tic", "gestion_risques_tic", "incidents", "tests_resilience", "tiers"],
                "requirement_count": 75
            }
        }

    async def parse_framework(
        self,
        framework_type: FrameworkType,
        source_content: str = None,
        organization_context: Dict[str, Any] = None
    ) -> List[FrameworkRequirement]:
        """
        Parse sophistiqué d'un framework avec analyse LLM approfondie.
        """
        logger.info(f"Parsing sophistiqué du framework {framework_type.value}")
        
        # 1. Acquisition du contenu si non fourni
        if not source_content:
            source_content = await self._get_framework_content(framework_type)
        
        # 2. Extraction intelligente des exigences par LLM
        raw_requirements = await self._extract_requirements_with_llm(
            framework_type, source_content
        )
        
        # 3. Analyse approfondie de chaque exigence
        analyzed_requirements = []
        for req in raw_requirements:
            analyzed_req = await self._analyze_requirement_with_llm(
                req, framework_type, organization_context
            )
            analyzed_requirements.append(analyzed_req)
        
        # 4. Analyse des interdépendances
        interdependency_analysis = await self._analyze_interdependencies_with_llm(
            analyzed_requirements, framework_type
        )
        
        # 5. Enrichissement avec l'analyse d'interdépendances
        for req in analyzed_requirements:
            req_id = req.id
            if req_id in interdependency_analysis:
                req.related_requirements = interdependency_analysis[req_id].get("related", [])
                req.ai_analysis["interdependencies"] = interdependency_analysis[req_id]
        
        logger.info(f"Framework {framework_type.value} parsé: {len(analyzed_requirements)} exigences")
        return analyzed_requirements

    async def create_framework_mapping(
        self,
        source_framework: FrameworkType,
        target_framework: FrameworkType,
        source_requirements: List[FrameworkRequirement] = None,
        target_requirements: List[FrameworkRequirement] = None
    ) -> List[FrameworkMapping]:
        """
        Crée un mapping intelligent entre deux frameworks via LLM.
        """
        logger.info(f"Création mapping {source_framework.value} → {target_framework.value}")
        
        # Obtenir les exigences si non fournies
        if not source_requirements:
            source_requirements = await self.parse_framework(source_framework)
        if not target_requirements:
            target_requirements = await self.parse_framework(target_framework)
        
        mappings = []
        
        # Analyse par clusters pour optimiser les appels LLM
        source_clusters = self._cluster_requirements_by_domain(source_requirements)
        target_clusters = self._cluster_requirements_by_domain(target_requirements)
        
        for source_domain, source_reqs in source_clusters.items():
            for target_domain, target_reqs in target_clusters.items():
                # Mapping intelligent par domaine
                domain_mappings = await self._map_requirements_cluster_with_llm(
                    source_reqs, target_reqs, source_framework, target_framework
                )
                mappings.extend(domain_mappings)
        
        # Post-traitement pour optimiser les mappings
        optimized_mappings = await self._optimize_mappings_with_llm(mappings)
        
        logger.info(f"Mapping créé: {len(optimized_mappings)} correspondances")
        return optimized_mappings

    async def analyze_compliance_gaps(
        self,
        framework_type: FrameworkType,
        current_implementation: Dict[str, Any],
        organization_profile: Dict[str, Any] = None
    ) -> List[ComplianceGap]:
        """
        Analyse sophistiquée des gaps de conformité avec LLM.
        """
        logger.info(f"Analyse gaps conformité {framework_type.value}")
        
        # 1. Parser le framework cible
        target_requirements = await self.parse_framework(
            framework_type, organization_context=organization_profile
        )
        
        # 2. Analyse de l'état actuel par LLM
        current_state_analysis = await self._analyze_current_state_with_llm(
            current_implementation, framework_type, organization_profile
        )
        
        # 3. Identification des gaps par exigence
        gaps = []
        for requirement in target_requirements:
            gap = await self._identify_requirement_gap_with_llm(
                requirement, current_state_analysis, organization_profile
            )
            if gap:
                gaps.append(gap)
        
        # 4. Priorisation des gaps par LLM
        prioritized_gaps = await self._prioritize_gaps_with_llm(
            gaps, organization_profile
        )
        
        # 5. Plans de remédiation personnalisés
        for gap in prioritized_gaps:
            gap.remediation_plan = await self._generate_remediation_plan_with_llm(
                gap, organization_profile
            )
        
        logger.info(f"Analyse terminée: {len(prioritized_gaps)} gaps identifiés")
        return prioritized_gaps

    async def generate_implementation_roadmap(
        self,
        framework_type: FrameworkType,
        gaps: List[ComplianceGap],
        organization_constraints: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Génère une roadmap d'implémentation intelligente via LLM.
        """
        logger.info(f"Génération roadmap {framework_type.value}")
        
        roadmap_prompt = f"""
Crée une roadmap d'implémentation stratégique pour la conformité {framework_type.value}.

GAPS IDENTIFIÉS:
{json.dumps([{"id": g.requirement_id, "severity": g.severity, "effort": g.estimated_effort} for g in gaps], indent=2)}

CONTRAINTES ORGANISATIONNELLES:
{json.dumps(organization_constraints or {}, indent=2)}

Génère une roadmap incluant:
1. Phases d'implémentation (court/moyen/long terme)
2. Priorisation basée sur risques et efforts
3. Interdépendances et séquencement optimal
4. Jalons de validation et KPIs
5. Ressources requises par phase
6. Risques d'implémentation et mitigation
7. Communication et change management

Retourne un JSON structuré détaillé.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["framework_analyst"]},
                {"role": "user", "content": roadmap_prompt}
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
            logger.error(f"Erreur parsing roadmap: {str(e)}")
            return {"error": "Erreur génération roadmap", "details": str(e)}

    # Méthodes privées sophistiquées

    async def _extract_requirements_with_llm(
        self,
        framework_type: FrameworkType,
        source_content: str
    ) -> List[Dict[str, Any]]:
        """Extraction intelligente des exigences par LLM."""
        
        extraction_prompt = f"""
Analyse ce contenu de framework {framework_type.value} et extrait TOUTES les exigences de conformité.

CONTENU:
{source_content[:8000]}

Pour chaque exigence identifiée, extrais:
- ID/référence unique
- Section/chapitre
- Titre
- Description complète
- Type (contrôle, principe, processus, documentation, évaluation)
- Caractère obligatoire (mandatory/optional)
- Guidance d'implémentation
- Preuves requises
- Domaines de risque concernés

Utilise ta connaissance experte du framework pour:
- Identifier les exigences implicites
- Comprendre les nuances réglementaires
- Détecter les interdépendances
- Évaluer la criticité business

IMPORTANT: Retourne UNIQUEMENT un JSON valide, sans texte explicatif avant ou après.

Format JSON requis:
{{
    "requirements": [
        {{
            "id": "string",
            "section": "string", 
            "title": "string",
            "description": "string",
            "type": "control|principle|process|documentation|assessment",
            "mandatory": true|false,
            "guidance": "string",
            "evidence_required": ["string"],
            "risk_areas": ["string"]
        }}
    ]
}}
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["framework_analyst"]},
                {"role": "user", "content": extraction_prompt}
            ],
            model="gpt-4.1",
            temperature=0.1
        )
        
        try:
            data = extract_json_from_llm_response(response)
            requirements = data.get("requirements", [])
            if not requirements and "exigences" in data:
                requirements = data.get("exigences", [])
            logger.info(f"Successfully extracted {len(requirements)} requirements from LLM response")
            return requirements
        except Exception as e:
            logger.error(f"Erreur extraction exigences: {str(e)}")
            logger.debug(f"LLM response causing error: {response[:300] if response else 'None'}")
            return []

    async def _analyze_requirement_with_llm(
        self,
        requirement_data: Dict[str, Any],
        framework_type: FrameworkType,
        organization_context: Dict[str, Any] = None
    ) -> FrameworkRequirement:
        """Analyse approfondie d'une exigence par LLM."""
        
        analysis_prompt = f"""
Effectue une analyse experte approfondie de cette exigence {framework_type.value}:

EXIGENCE:
{json.dumps(requirement_data, indent=2, default=str)}

CONTEXTE ORGANISATIONNEL:
{json.dumps(organization_context or {}, indent=2)}

Analyse avec ton expertise senior:

1. IMPACT BUSINESS:
   - Criticité pour l'organisation
   - Processus métier impactés
   - Coût de non-conformité
   - Bénéfices de l'implémentation

2. COMPLEXITÉ D'IMPLÉMENTATION:
   - Niveau de difficulté technique
   - Ressources requises
   - Délais estimés
   - Compétences nécessaires

3. INTERDÉPENDANCES:
   - Autres exigences liées
   - Prérequis organisationnels
   - Technologies impliquées
   - Processus connexes

4. GUIDANCE PRATIQUE:
   - Meilleures pratiques d'implémentation
   - Erreurs courantes à éviter
   - Indicateurs de succès
   - Méthodes de validation

5. SECTEUR-SPÉCIFIQUE:
   - Considérations spécifiques au secteur
   - Variations d'interprétation
   - Exemples concrets d'implémentation

IMPORTANT: Retourne UNIQUEMENT un JSON valide, sans texte explicatif avant ou après.

Format JSON requis:
{{
    "business_impact": {{
        "summary": "string",
        "criticality": "low|medium|high|critical",
        "affected_processes": ["string"]
    }},
    "implementation_complexity": {{
        "level": "low|medium|high|very_high",
        "technical_difficulty": "string",
        "estimated_timeline": "string"
    }},
    "interdependencies": {{
        "related_requirements": ["string"],
        "prerequisites": ["string"]
    }},
    "practical_guidance": {{
        "best_practices": ["string"],
        "common_pitfalls": ["string"]
    }}
}}
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["framework_analyst"]},
                {"role": "user", "content": analysis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        try:
            ai_analysis = extract_json_from_llm_response(response)
            if not ai_analysis:
                logger.warning("No analysis data extracted, using default structure")
                ai_analysis = {"error": "No valid JSON found in LLM response"}
        except Exception as e:
            logger.error(f"Erreur analyse exigence: {str(e)}")
            logger.debug(f"LLM response causing error: {response[:300] if response else 'None'}")
            ai_analysis = {"error": str(e)}
        
        # Créer l'objet FrameworkRequirement enrichi
        return FrameworkRequirement(
            id=requirement_data.get("id", ""),
            framework=framework_type,
            section=requirement_data.get("section", ""),
            title=requirement_data.get("title", ""),
            description=requirement_data.get("description", ""),
            requirement_type=RequirementType(requirement_data.get("type", "control")),
            mandatory=requirement_data.get("mandatory", True),
            implementation_guidance=requirement_data.get("guidance", ""),
            evidence_required=requirement_data.get("evidence_required", []),
            related_requirements=[],  # Sera enrichi plus tard
            risk_areas=requirement_data.get("risk_areas", []),
            business_impact=ai_analysis.get("business_impact", {}).get("summary", ""),
            implementation_complexity=ai_analysis.get("implementation_complexity", {}).get("level", "medium"),
            ai_analysis=ai_analysis
        )

    async def _map_requirements_cluster_with_llm(
        self,
        source_reqs: List[FrameworkRequirement],
        target_reqs: List[FrameworkRequirement],
        source_framework: FrameworkType,
        target_framework: FrameworkType
    ) -> List[FrameworkMapping]:
        """Mapping intelligent d'un cluster d'exigences."""
        
        # Préparer les données pour LLM
        source_summary = [
            {"id": req.id, "title": req.title, "description": req.description[:200]}
            for req in source_reqs
        ]
        target_summary = [
            {"id": req.id, "title": req.title, "description": req.description[:200]}
            for req in target_reqs
        ]
        
        mapping_prompt = f"""
Crée un mapping expert entre ces exigences de frameworks.

SOURCE ({source_framework.value}):
{json.dumps(source_summary, indent=2)}

CIBLE ({target_framework.value}):
{json.dumps(target_summary, indent=2)}

Pour chaque exigence source, identifie:
1. La ou les exigences cibles correspondantes
2. Type de mapping: full (équivalence complète), partial (couverture partielle), 
   conceptual (concept similaire), none (pas de correspondance)
3. Score de confiance (0.0-1.0)
4. Justification détaillée du mapping
5. Notes d'implémentation spécifiques

Utilise ta connaissance experte des frameworks pour identifier:
- Les correspondances non-évidentes
- Les différences de granularité
- Les spécificités réglementaires
- Les évolutions entre versions

IMPORTANT: Retourne UNIQUEMENT un JSON valide, sans texte explicatif avant ou après.

Format JSON requis:
{{
    "mappings": [
        {{
            "source_id": "string",
            "target_id": "string", 
            "mapping_type": "full|partial|conceptual|none",
            "confidence": 0.0-1.0,
            "rationale": "string",
            "implementation_notes": "string"
        }}
    ]
}}
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["mapping_expert"]},
                {"role": "user", "content": mapping_prompt}
            ],
            model="gpt-4.1",
            temperature=0.1
        )
        
        try:
            data = extract_json_from_llm_response(response)
            
            mappings = []
            mapping_list = data.get("mappings", [])
            if not mapping_list and "maps" in data:
                mapping_list = data.get("maps", [])
            
            for mapping_data in mapping_list:
                mapping = FrameworkMapping(
                    source_framework=source_framework,
                    target_framework=target_framework,
                    source_requirement=mapping_data.get("source_id", ""),
                    target_requirement=mapping_data.get("target_id", ""),
                    mapping_type=mapping_data.get("mapping_type", "none"),
                    confidence_score=float(mapping_data.get("confidence", 0.0)),
                    mapping_rationale=mapping_data.get("rationale", ""),
                    implementation_notes=mapping_data.get("implementation_notes", "")
                )
                mappings.append(mapping)
            
            logger.info(f"Successfully extracted {len(mappings)} mappings from LLM response")
            return mappings
            
        except Exception as e:
            logger.error(f"Erreur mapping cluster: {str(e)}")
            logger.debug(f"LLM response causing error: {response[:300] if response else 'None'}")
            return []

    async def _identify_requirement_gap_with_llm(
        self,
        requirement: FrameworkRequirement,
        current_state: Dict[str, Any],
        organization_profile: Dict[str, Any] = None
    ) -> Optional[ComplianceGap]:
        """Identification sophistiquée d'un gap par LLM."""
        
        gap_analysis_prompt = f"""
Analyse ce gap de conformité avec ton expertise senior:

EXIGENCE CIBLE:
- ID: {requirement.id}
- Framework: {requirement.framework.value}
- Titre: {requirement.title}
- Description: {requirement.description}
- Obligatoire: {requirement.mandatory}
- Complexité: {requirement.implementation_complexity}

ÉTAT ACTUEL:
{json.dumps(current_state, indent=2)}

PROFIL ORGANISATION:
{json.dumps(organization_profile or {}, indent=2)}

Détermine:
1. Y a-t-il un gap? (oui/non et pourquoi)
2. Type de gap: complet, partiel, documentaire, opérationnel, technique
3. Sévérité: critique, haute, moyenne, faible
4. Description précise du gap
5. État actuel vs état cible
6. Effort estimé de remédiation
7. Justification business de la remédiation
8. Risques de non-remédiation

Si pas de gap significatif, retourne "no_gap".

IMPORTANT: Si gap identifié, retourne UNIQUEMENT un JSON valide, sans texte explicatif avant ou après.

Format JSON requis:
{{
    "gap_type": "complet|partiel|documentaire|operationnel|technique",
    "severity": "critical|high|medium|low",
    "description": "string",
    "current_state": "string",
    "target_state": "string", 
    "estimated_effort": "low|medium|high|very_high",
    "business_justification": "string"
}}
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["gap_analyst"]},
                {"role": "user", "content": gap_analysis_prompt}
            ],
            model="gpt-4.1",
            temperature=0.1
        )
        
        if "no_gap" in response.lower():
            return None
        
        try:
            data = extract_json_from_llm_response(response)
            
            if not data:
                logger.warning(f"No gap analysis data extracted for requirement {requirement.id}")
                return None
            
            return ComplianceGap(
                requirement_id=requirement.id,
                framework=requirement.framework,
                gap_type=data.get("gap_type", "unknown"),
                severity=data.get("severity", "medium"),
                description=data.get("description", ""),
                current_state=data.get("current_state", ""),
                target_state=data.get("target_state", ""),
                remediation_plan=[],  # Sera généré séparément
                estimated_effort=data.get("estimated_effort", "medium"),
                business_justification=data.get("business_justification", "")
            )
            
        except Exception as e:
            logger.error(f"Erreur analyse gap: {str(e)}")
            logger.debug(f"LLM response causing error: {response[:300] if response else 'None'}")
            return None

    # Méthodes utilitaires

    def _cluster_requirements_by_domain(
        self, 
        requirements: List[FrameworkRequirement]
    ) -> Dict[str, List[FrameworkRequirement]]:
        """Regroupe les exigences par domaine pour optimiser l'analyse."""
        clusters = {}
        
        for req in requirements:
            # Déterminer le domaine principal
            domain = self._determine_requirement_domain(req)
            if domain not in clusters:
                clusters[domain] = []
            clusters[domain].append(req)
        
        return clusters

    def _determine_requirement_domain(self, requirement: FrameworkRequirement) -> str:
        """Détermine le domaine d'une exigence."""
        # Logique simplifiée - peut être enrichie
        section = requirement.section.lower()
        title = requirement.title.lower()
        
        if any(term in section + title for term in ["access", "identit", "auth"]):
            return "access_control"
        elif any(term in section + title for term in ["crypto", "chiffr", "encrypt"]):
            return "cryptography"
        elif any(term in section + title for term in ["incident", "breach", "violation"]):
            return "incident_management"
        elif any(term in section + title for term in ["risk", "risque"]):
            return "risk_management"
        elif any(term in section + title for term in ["audit", "monitor", "surveillance"]):
            return "monitoring"
        else:
            return "general"

    async def _get_framework_content(self, framework_type: FrameworkType) -> str:
        """Récupère le contenu d'un framework (simulation)."""
        # Dans une vraie implémentation, cela récupérerait le contenu officiel
        return f"Contenu simulé du framework {framework_type.value}"

    async def _analyze_interdependencies_with_llm(
        self,
        requirements: List[FrameworkRequirement],
        framework_type: FrameworkType
    ) -> Dict[str, Dict[str, Any]]:
        """Analyse les interdépendances entre exigences."""
        # Simplification pour éviter des appels LLM trop nombreux
        return {}

    async def _analyze_current_state_with_llm(
        self,
        implementation_data: Dict[str, Any],
        framework_type: FrameworkType,
        org_profile: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Analyse l'état actuel d'implémentation."""
        return implementation_data

    async def _prioritize_gaps_with_llm(
        self,
        gaps: List[ComplianceGap],
        org_profile: Dict[str, Any] = None
    ) -> List[ComplianceGap]:
        """Priorise les gaps par criticité."""
        return sorted(gaps, key=lambda g: {"critical": 4, "high": 3, "medium": 2, "low": 1}.get(g.severity, 1), reverse=True)

    async def _generate_remediation_plan_with_llm(
        self,
        gap: ComplianceGap,
        org_profile: Dict[str, Any] = None
    ) -> List[str]:
        """Génère un plan de remédiation spécifique."""
        remediation_prompt = f"""
Crée un plan de remédiation détaillé pour ce gap de conformité:

GAP: {gap.description}
SÉVÉRITÉ: {gap.severity}
EFFORT ESTIMÉ: {gap.estimated_effort}
FRAMEWORK: {gap.framework.value}

CONTEXTE ORGANISATION:
{json.dumps(org_profile or {}, indent=2)}

Génère un plan d'action structuré avec:
1. Étapes concrètes d'implémentation
2. Responsabilités et rôles
3. Jalons et livrables
4. Critères de validation
5. Risques et mitigation

Retourne une liste d'actions prioritaires et actionables.
"""

        response = await self.llm_client.generate_response(
            messages=[
                {"role": "system", "content": self.system_prompts["gap_analyst"]},
                {"role": "user", "content": remediation_prompt}
            ],
            model="gpt-4.1",
            temperature=0.2
        )
        
        # Parser la réponse en liste d'actions
        actions = [line.strip() for line in response.split('\n') if line.strip() and not line.startswith('#')]
        return actions[:10]  # Limiter à 10 actions max

    async def _optimize_mappings_with_llm(
        self, 
        mappings: List[FrameworkMapping]
    ) -> List[FrameworkMapping]:
        """Optimise et valide les mappings."""
        # Pour simplifier, retourne les mappings sans optimisation additionnelle
        return mappings


# Tool function for agent integration
async def framework_parser_tool(
    framework_type: str,
    action: str,  # parse, map, analyze_gaps, roadmap
    source_content: str = None,
    target_framework: str = None,
    current_implementation: Dict[str, Any] = None,
    organization_context: Dict[str, Any] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Outil de parsing de frameworks pour les agents.
    """
    parser = FrameworkParser()
    
    try:
        framework = safe_framework_type_conversion(framework_type)
    except ValueError:
        return {
            "success": False,
            "error": f"Framework type non supporté: {framework_type}",
            "supported_types": [f.value for f in FrameworkType]
        }
    
    try:
        if action == "parse":
            requirements = await parser.parse_framework(
                framework, source_content, organization_context
            )
            return {
                "success": True,
                "action": "parse",
                "framework": framework_type,
                "requirements_count": len(requirements),
                "requirements": [
                    {
                        "id": req.id,
                        "title": req.title,
                        "description": req.description[:200] + "..." if len(req.description) > 200 else req.description,
                        "mandatory": req.mandatory,
                        "complexity": req.implementation_complexity,
                        "business_impact": req.business_impact
                    }
                    for req in requirements
                ]
            }
        
        elif action == "map" and target_framework:
            try:
                target_fw = safe_framework_type_conversion(target_framework)
                mappings = await parser.create_framework_mapping(framework, target_fw)
                return {
                    "success": True,
                    "action": "map",
                    "source_framework": framework_type,
                    "target_framework": target_framework,
                    "mappings_count": len(mappings),
                    "mappings": [
                        {
                            "source": m.source_requirement,
                            "target": m.target_requirement,
                            "type": m.mapping_type,
                            "confidence": m.confidence_score,
                            "rationale": m.mapping_rationale
                        }
                        for m in mappings
                    ]
                }
            except ValueError:
                return {
                    "success": False,
                    "error": f"Target framework non supporté: {target_framework}"
                }
        
        elif action == "analyze_gaps":
            if not current_implementation:
                return {
                    "success": False,
                    "error": "current_implementation requis pour l'analyse de gaps"
                }
            
            gaps = await parser.analyze_compliance_gaps(
                framework, current_implementation, organization_context
            )
            return {
                "success": True,
                "action": "analyze_gaps",
                "framework": framework_type,
                "gaps_count": len(gaps),
                "gaps": [
                    {
                        "requirement_id": gap.requirement_id,
                        "severity": gap.severity,
                        "description": gap.description,
                        "estimated_effort": gap.estimated_effort,
                        "business_justification": gap.business_justification
                    }
                    for gap in gaps
                ]
            }
        
        elif action == "roadmap":
            # Pour la roadmap, on a besoin des gaps
            if not current_implementation:
                return {
                    "success": False,
                    "error": "current_implementation requis pour la roadmap"
                }
            
            gaps = await parser.analyze_compliance_gaps(
                framework, current_implementation, organization_context
            )
            roadmap = await parser.generate_implementation_roadmap(
                framework, gaps, organization_context
            )
            return {
                "success": True,
                "action": "roadmap",
                "framework": framework_type,
                "roadmap": roadmap
            }
        
        else:
            return {
                "success": False,
                "error": f"Action non supportée: {action}",
                "supported_actions": ["parse", "map", "analyze_gaps", "roadmap"]
            }
        
    except Exception as e:
        logger.error(f"Erreur dans framework_parser_tool: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }


def get_framework_parser():
    """Factory function pour obtenir une instance de FrameworkParser."""
    return FrameworkParser() 