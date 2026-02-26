"""
Organization Configuration Module - Gère les contextes organisationnels pour RegulAIte.
Permet la personnalisation des analyses selon les besoins spécifiques de l'organisation.
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)

class OrganizationType(Enum):
    """Types d'organisation supportés."""
    STARTUP = "startup"
    SME = "sme"  # Small/Medium Enterprise
    LARGE_CORP = "large_corp"
    PUBLIC_SECTOR = "public_sector"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    TECHNOLOGY = "technology"
    MANUFACTURING = "manufacturing"
    ENERGY = "energy"
    TELECOM = "telecom"

class RegulatorySector(Enum):
    """Secteurs réglementaires."""
    BANKING = "banking"
    INSURANCE = "insurance"
    HEALTHCARE = "healthcare"
    ENERGY = "energy"
    TELECOM = "telecom"
    TECHNOLOGY = "technology"
    PUBLIC = "public"
    GENERAL = "general"

class ComplianceFramework(Enum):
    """Frameworks de conformité applicables."""
    ISO27001 = "iso27001"
    RGPD = "rgpd"
    DORA = "dora"
    NIST = "nist"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    ANSSI = "anssi"

@dataclass
class AssetTemplate:
    """Template d'actif pour l'organisation."""
    id: str
    name: str
    type: str  # system, data, application, network, human, physical
    criticality: str  # very_low, low, medium, high, very_high
    description: str = ""
    owner: str = ""
    location: str = ""
    business_value: str = "medium"
    regulatory_classification: str = ""

@dataclass
class ThreatProfile:
    """Profil de menace pour l'organisation."""
    threat_type: str
    likelihood: str  # very_low, low, medium, high, very_high
    sophistication: str  # basic, intermediate, advanced, expert
    motivation: str  # financial, espionage, activism, disruption
    resources: str  # limited, moderate, substantial, extensive
    persistence: str  # low, medium, high, very_high

@dataclass
class RegulatoryEnvironment:
    """Environnement réglementaire de l'organisation."""
    primary_frameworks: List[ComplianceFramework] = field(default_factory=list)
    regulatory_pressure: str = "medium"  # low, medium, high, very_high
    audit_frequency: str = "annual"  # quarterly, bi_annual, annual, ad_hoc
    penalties_exposure: str = "medium"  # low, medium, high, very_high
    external_oversight: List[str] = field(default_factory=list)
    certification_requirements: List[str] = field(default_factory=list)

@dataclass
class OrganizationProfile:
    """Profil complet de l'organisation."""
    # Informations de base
    organization_id: str
    name: str
    organization_type: OrganizationType
    sector: RegulatorySector
    size: str  # startup, small, medium, large, enterprise
    employee_count: int
    annual_revenue: str  # ranges: <1M, 1M-10M, 10M-100M, 100M-1B, >1B
    
    # Contexte opérationnel
    geographical_presence: List[str] = field(default_factory=list)  # countries/regions
    business_model: str = "traditional"  # traditional, digital, hybrid, platform
    digital_maturity: str = "intermediate"  # basic, intermediate, advanced, leading
    transformation_stage: str = "evolving"  # stable, evolving, transforming, disrupting
    
    # Posture de risque
    risk_appetite: str = "moderate"  # conservative, moderate, aggressive
    risk_tolerance: Dict[str, str] = field(default_factory=dict)  # by risk type
    insurance_coverage: List[str] = field(default_factory=list)
    
    # Environnement réglementaire
    regulatory_env: RegulatoryEnvironment = field(default_factory=RegulatoryEnvironment)
    
    # Assets et infrastructure
    asset_templates: List[AssetTemplate] = field(default_factory=list)
    critical_processes: List[str] = field(default_factory=list)
    key_technologies: List[str] = field(default_factory=list)
    
    # Profil de menaces
    threat_profile: List[ThreatProfile] = field(default_factory=list)
    
    # Gouvernance
    governance_maturity: Dict[str, str] = field(default_factory=dict)  # by domain
    board_composition: Dict[str, Any] = field(default_factory=dict)
    reporting_structure: Dict[str, Any] = field(default_factory=dict)
    
    # Historique et contexte
    created_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    assessment_history: List[Dict[str, Any]] = field(default_factory=list)
    
    # Configuration spécifique RegulAIte
    preferred_methodologies: List[str] = field(default_factory=list)
    custom_frameworks: List[Dict[str, Any]] = field(default_factory=list)
    analysis_preferences: Dict[str, Any] = field(default_factory=dict)

class OrganizationConfigManager:
    """Gestionnaire de configuration organisationnelle."""
    
    def __init__(self):
        self.profiles: Dict[str, OrganizationProfile] = {}
        self.sector_templates = self._load_sector_templates()
        self.size_templates = self._load_size_templates()
    
    def create_organization_profile(
        self,
        org_data: Dict[str, Any],
        use_templates: bool = True
    ) -> OrganizationProfile:
        """Crée un profil d'organisation avec templates sectoriels."""
        
        org_type = OrganizationType(org_data.get("organization_type", "technology"))
        sector = RegulatorySector(org_data.get("sector", "general"))
        size = org_data.get("size", "medium")
        
        profile = OrganizationProfile(
            organization_id=org_data["organization_id"],
            name=org_data["name"],
            organization_type=org_type,
            sector=sector,
            size=size,
            employee_count=org_data.get("employee_count", 100),
            annual_revenue=org_data.get("annual_revenue", "10M-100M")
        )
        
        if use_templates:
            # Appliquer les templates sectoriels
            self._apply_sector_template(profile, sector)
            self._apply_size_template(profile, size)
            self._apply_type_template(profile, org_type)
        
        # Personnalisations spécifiques
        if "custom_settings" in org_data:
            self._apply_custom_settings(profile, org_data["custom_settings"])
        
        self.profiles[profile.organization_id] = profile
        return profile
    
    def get_organization_assets(self, org_id: str, scope: str = None) -> List[Dict[str, Any]]:
        """Récupère les actifs de l'organisation selon le périmètre."""
        profile = self.profiles.get(org_id)
        if not profile:
            return self._get_default_assets()
        
        assets = []
        for template in profile.asset_templates:
            if scope and scope.lower() not in template.name.lower():
                continue
            
            assets.append({
                "id": template.id,
                "name": template.name,
                "type": template.type,
                "criticality": template.criticality,
                "description": template.description,
                "owner": template.owner,
                "business_value": template.business_value,
                "regulatory_classification": template.regulatory_classification
            })
        
        return assets if assets else self._get_default_assets()
    
    def get_threat_landscape(self, org_id: str) -> List[Dict[str, Any]]:
        """Récupère le paysage de menaces pour l'organisation."""
        profile = self.profiles.get(org_id)
        if not profile:
            return self._get_default_threats()
        
        threats = []
        for threat in profile.threat_profile:
            threats.append({
                "name": threat.threat_type,
                "likelihood": threat.likelihood,
                "sophistication": threat.sophistication,
                "motivation": threat.motivation,
                "resources": threat.resources,
                "persistence": threat.persistence
            })
        
        return threats if threats else self._get_default_threats()
    
    def get_regulatory_context(self, org_id: str) -> Dict[str, Any]:
        """Récupère le contexte réglementaire."""
        profile = self.profiles.get(org_id)
        if not profile:
            return {"frameworks": ["iso27001"], "pressure": "medium"}
        
        return {
            "frameworks": [f.value for f in profile.regulatory_env.primary_frameworks],
            "pressure": profile.regulatory_env.regulatory_pressure,
            "audit_frequency": profile.regulatory_env.audit_frequency,
            "penalties_exposure": profile.regulatory_env.penalties_exposure,
            "certifications": profile.regulatory_env.certification_requirements
        }
    
    def get_governance_context(self, org_id: str) -> Dict[str, Any]:
        """Récupère le contexte de gouvernance."""
        profile = self.profiles.get(org_id)
        if not profile:
            return {
                "maturity": {"strategic": "developing", "risk": "defined"},
                "structure": "traditional"
            }
        
        return {
            "maturity": profile.governance_maturity,
            "board_composition": profile.board_composition,
            "reporting_structure": profile.reporting_structure,
            "transformation_stage": profile.transformation_stage
        }
    
    def _load_sector_templates(self) -> Dict[str, Dict[str, Any]]:
        """Charge les templates sectoriels."""
        return {
            RegulatorySector.BANKING.value: {
                "regulatory_frameworks": [ComplianceFramework.DORA, ComplianceFramework.PCI_DSS],
                "regulatory_pressure": "very_high",
                "key_threats": ["cybercrime", "insider_threat", "nation_state"],
                "critical_assets": ["payment_systems", "customer_data", "trading_platforms"],
                "risk_appetite": "conservative"
            },
            RegulatorySector.HEALTHCARE.value: {
                "regulatory_frameworks": [ComplianceFramework.HIPAA, ComplianceFramework.RGPD],
                "regulatory_pressure": "very_high",
                "key_threats": ["ransomware", "data_theft", "insider_threat"],
                "critical_assets": ["patient_data", "medical_devices", "ehr_systems"],
                "risk_appetite": "conservative"
            },
            RegulatorySector.TECHNOLOGY.value: {
                "regulatory_frameworks": [ComplianceFramework.ISO27001, ComplianceFramework.RGPD],
                "regulatory_pressure": "medium",
                "key_threats": ["advanced_apt", "supply_chain", "ip_theft"],
                "critical_assets": ["source_code", "customer_data", "infrastructure"],
                "risk_appetite": "moderate"
            }
        }
    
    def _load_size_templates(self) -> Dict[str, Dict[str, Any]]:
        """Charge les templates par taille d'organisation."""
        return {
            "startup": {
                "governance_maturity": "initial",
                "security_budget": "limited",
                "resource_constraints": "high",
                "agility": "very_high"
            },
            "small": {
                "governance_maturity": "developing",
                "security_budget": "moderate",
                "resource_constraints": "medium",
                "agility": "high"
            },
            "medium": {
                "governance_maturity": "defined",
                "security_budget": "adequate",
                "resource_constraints": "low",
                "agility": "medium"
            },
            "large": {
                "governance_maturity": "managed",
                "security_budget": "substantial",
                "resource_constraints": "very_low",
                "agility": "low"
            }
        }
    
    def _apply_sector_template(self, profile: OrganizationProfile, sector: RegulatorySector):
        """Applique le template sectoriel."""
        template = self.sector_templates.get(sector.value, {})
        
        if "regulatory_frameworks" in template:
            profile.regulatory_env.primary_frameworks = template["regulatory_frameworks"]
        if "regulatory_pressure" in template:
            profile.regulatory_env.regulatory_pressure = template["regulatory_pressure"]
        if "risk_appetite" in template:
            profile.risk_appetite = template["risk_appetite"]
        
        # Ajouter actifs critiques du secteur
        if "critical_assets" in template:
            for i, asset_name in enumerate(template["critical_assets"]):
                profile.asset_templates.append(AssetTemplate(
                    id=f"{sector.value.upper()}-{i+1:03d}",
                    name=asset_name.replace("_", " ").title(),
                    type="system",
                    criticality="high"
                ))
        
        # Ajouter profil de menaces du secteur
        if "key_threats" in template:
            for threat in template["key_threats"]:
                profile.threat_profile.append(ThreatProfile(
                    threat_type=threat,
                    likelihood="medium",
                    sophistication="intermediate",
                    motivation="financial",
                    resources="moderate",
                    persistence="medium"
                ))
    
    def _apply_size_template(self, profile: OrganizationProfile, size: str):
        """Applique le template de taille."""
        template = self.size_templates.get(size, {})
        
        if "governance_maturity" in template:
            profile.governance_maturity = {
                "strategic": template["governance_maturity"],
                "risk": template["governance_maturity"],
                "compliance": template["governance_maturity"]
            }
    
    def _apply_type_template(self, profile: OrganizationProfile, org_type: OrganizationType):
        """Applique le template de type d'organisation."""
        # Personnalisations selon le type d'organisation
        pass
    
    def _apply_custom_settings(self, profile: OrganizationProfile, custom_settings: Dict[str, Any]):
        """Applique les paramètres personnalisés."""
        if "preferred_methodologies" in custom_settings:
            profile.preferred_methodologies = custom_settings["preferred_methodologies"]
        if "analysis_preferences" in custom_settings:
            profile.analysis_preferences = custom_settings["analysis_preferences"]
    
    def _get_default_assets(self) -> List[Dict[str, Any]]:
        """Assets par défaut si aucun profil organisationnel."""
        return [
            {"id": "SYS-001", "name": "Systèmes d'information", "type": "system", "criticality": "high"},
            {"id": "DATA-001", "name": "Données sensibles", "type": "data", "criticality": "very_high"},
            {"id": "APP-001", "name": "Applications métier", "type": "application", "criticality": "high"},
            {"id": "NET-001", "name": "Infrastructure réseau", "type": "network", "criticality": "medium"},
            {"id": "HR-001", "name": "Personnel", "type": "human", "criticality": "high"}
        ]
    
    def _get_default_threats(self) -> List[Dict[str, Any]]:
        """Menaces par défaut si aucun profil organisationnel."""
        return [
            {"name": "Cybercriminels", "likelihood": "medium", "sophistication": "intermediate"},
            {"name": "Menaces internes", "likelihood": "low", "sophistication": "basic"},
            {"name": "Hacktivistes", "likelihood": "low", "sophistication": "intermediate"},
            {"name": "Erreurs humaines", "likelihood": "high", "sophistication": "basic"}
        ]

# Instance globale du gestionnaire
org_config_manager = OrganizationConfigManager()

def get_organization_config_manager() -> OrganizationConfigManager:
    """Récupère l'instance du gestionnaire de configuration."""
    return org_config_manager 