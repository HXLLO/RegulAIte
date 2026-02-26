#!/usr/bin/env python3
"""
Test simple d'intégration pour le système de configuration organisationnelle RegulAIte.
Test autonome sans dépendances externes.
"""
import sys
import os
sys.path.append('.')

# Import direct des modules nécessaires
exec(open('agent_framework/modules/organization_config.py').read())

def test_organization_profile_creation():
    """Test de création d'un profil organisationnel."""
    print("🧪 Test création profil organisationnel...")
    
    org_manager = OrganizationConfigManager()
    
    # Données d'organisation test
    org_data = {
        "organization_id": "test_org_001",
        "name": "Entreprise Test GRC",
        "organization_type": "technology",
        "sector": "technology",
        "size": "medium",
        "employee_count": 250,
        "annual_revenue": "10M-100M",
        "custom_settings": {
            "preferred_methodologies": ["ebios", "iso27005"],
            "analysis_preferences": {
                "risk_assessment": {"depth": "detailed", "focus": "cybersecurity"}
            }
        }
    }
    
    # Créer le profil
    profile = org_manager.create_organization_profile(org_data)
    
    # Vérifications
    assert profile.organization_id == "test_org_001"
    assert profile.name == "Entreprise Test GRC"
    assert profile.organization_type == OrganizationType.TECHNOLOGY
    assert profile.sector == RegulatorySector.TECHNOLOGY
    assert profile.size == "medium"
    assert profile.employee_count == 250
    
    # Vérifier l'application des templates sectoriels
    assert len(profile.asset_templates) > 0
    assert len(profile.threat_profile) > 0
    assert len(profile.regulatory_env.primary_frameworks) > 0
    
    # Vérifier les custom settings
    assert "ebios" in profile.preferred_methodologies
    assert "iso27005" in profile.preferred_methodologies
    
    print("✅ Profil organisationnel créé avec succès")
    print(f"   - Assets: {len(profile.asset_templates)}")
    print(f"   - Threats: {len(profile.threat_profile)}")
    print(f"   - Frameworks: {[f.value for f in profile.regulatory_env.primary_frameworks]}")
    

def test_sector_specific_templates():
    """Test des templates spécifiques par secteur."""
    print("\n🧪 Test templates sectoriels...")
    
    org_manager = OrganizationConfigManager()
    
    # Test secteur bancaire
    banking_org = {
        "organization_id": "bank_001",
        "name": "Banque Test",
        "organization_type": "financial",
        "sector": "banking",
        "size": "large"
    }
    
    profile = org_manager.create_organization_profile(banking_org)
    
    # Vérifier les frameworks financiers
    framework_values = [f.value for f in profile.regulatory_env.primary_frameworks]
    assert "dora" in framework_values or "pci_dss" in framework_values
    assert profile.regulatory_env.regulatory_pressure == "very_high"
    assert profile.risk_appetite == "conservative"
    
    # Vérifier les menaces spécifiques au secteur bancaire
    threat_types = [t.threat_type for t in profile.threat_profile]
    assert any("cybercrime" in threat.lower() or "nation_state" in threat.lower() 
              for threat in threat_types)
    
    print("✅ Templates sectoriels appliqués correctement")
    print(f"   - Secteur: {profile.sector.value}")
    print(f"   - Pression réglementaire: {profile.regulatory_env.regulatory_pressure}")
    print(f"   - Appétit au risque: {profile.risk_appetite}")


def test_size_based_adaptations():
    """Test des adaptations selon la taille d'organisation."""
    print("\n🧪 Test adaptations par taille...")
    
    org_manager = OrganizationConfigManager()
    
    # Startup
    startup_org = {
        "organization_id": "startup_001",
        "name": "Startup Test",
        "size": "startup"
    }
    startup_profile = org_manager.create_organization_profile(startup_org)
    
    # Enterprise
    enterprise_org = {
        "organization_id": "enterprise_001",
        "name": "Enterprise Test",
        "size": "large"
    }
    enterprise_profile = org_manager.create_organization_profile(enterprise_org)
    
    # Vérifier les différences de maturité
    assert startup_profile.governance_maturity.get("strategic") in ["initial", "developing"]
    assert enterprise_profile.governance_maturity.get("strategic") in ["defined", "managed"]
    
    print("✅ Adaptations par taille appliquées")
    print(f"   - Startup - Maturité stratégique: {startup_profile.governance_maturity.get('strategic')}")
    print(f"   - Enterprise - Maturité stratégique: {enterprise_profile.governance_maturity.get('strategic')}")


def test_organizational_context_retrieval():
    """Test de récupération du contexte organisationnel."""
    print("\n🧪 Test récupération contexte...")
    
    org_manager = OrganizationConfigManager()
    
    # Créer une organisation healthcare
    healthcare_org = {
        "organization_id": "hospital_001",
        "name": "Hospital Test",
        "sector": "healthcare",
        "organization_type": "healthcare",
        "size": "medium"
    }
    
    profile = org_manager.create_organization_profile(healthcare_org)
    
    # Test de récupération d'actifs
    assets = org_manager.get_organization_assets("hospital_001")
    assert len(assets) > 0
    print(f"   - Assets récupérés: {len(assets)}")
    
    # Test de récupération du paysage de menaces
    threats = org_manager.get_threat_landscape("hospital_001")
    assert len(threats) > 0
    print(f"   - Menaces récupérées: {len(threats)}")
    
    # Test de récupération du contexte réglementaire
    regulatory_context = org_manager.get_regulatory_context("hospital_001")
    assert "frameworks" in regulatory_context
    assert "pressure" in regulatory_context
    assert regulatory_context["pressure"] == "very_high"  # Healthcare = high pressure
    print(f"   - Contexte réglementaire: {regulatory_context['pressure']}")
    
    # Test de récupération du contexte de gouvernance
    governance_context = org_manager.get_governance_context("hospital_001")
    assert "maturity" in governance_context
    print(f"   - Maturité gouvernance: {governance_context['maturity']}")
    
    print("✅ Récupération de contexte fonctionnelle")


def test_assets_and_threats_filtering():
    """Test du filtrage d'actifs et menaces."""
    print("\n🧪 Test filtrage actifs et menaces...")
    
    org_manager = OrganizationConfigManager()
    
    # Créer une organisation avec des données spécifiques
    tech_org = {
        "organization_id": "tech_company_001",
        "name": "Tech Company",
        "sector": "technology",
        "size": "medium"
    }
    
    profile = org_manager.create_organization_profile(tech_org)
    
    # Test de récupération de tous les actifs
    all_assets = org_manager.get_organization_assets("tech_company_001")
    assert len(all_assets) > 0
    
    # Test de récupération avec scope
    data_assets = org_manager.get_organization_assets("tech_company_001", scope="data")
    
    # Vérifier que le filtrage fonctionne (si des actifs data existent)
    if data_assets:
        for asset in data_assets:
            assert "data" in asset["name"].lower() or asset["type"] == "data"
    
    print(f"   - Tous les actifs: {len(all_assets)}")
    print(f"   - Actifs data: {len(data_assets)}")
    print("✅ Filtrage fonctionnel")


def run_all_tests():
    """Exécute tous les tests d'intégration."""
    print("🚀 Démarrage des tests d'intégration organisationnelle RegulAIte\n")
    
    try:
        test_organization_profile_creation()
        test_sector_specific_templates()
        test_size_based_adaptations()
        test_organizational_context_retrieval()
        test_assets_and_threats_filtering()
        
        print("\n🎉 Tous les tests d'intégration ont réussi!")
        print("✅ Le système de configuration organisationnelle fonctionne correctement")
        return True
        
    except Exception as e:
        print(f"\n❌ Erreur dans les tests: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 