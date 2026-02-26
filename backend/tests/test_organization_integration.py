"""
Tests d'intégration pour le système de configuration organisationnelle RegulAIte.
Vérifie l'intégration entre la configuration organisationnelle et les modules d'analyse.
"""
import pytest
import asyncio
import json
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from backend.agent_framework.modules.organization_config import (
    OrganizationConfigManager, OrganizationProfile, AssetTemplate, ThreatProfile,
    RegulatoryEnvironment, OrganizationType, RegulatorySector, ComplianceFramework
)
from backend.agent_framework.modules.database_integration import RegulAIteDatabaseIntegration
from backend.agent_framework.modules.risk_assessment_module import RiskAssessmentModule
from backend.agent_framework.agent import Query, QueryContext

class TestOrganizationIntegration:
    """Tests d'intégration du système organisationnel."""
    
    @pytest.fixture
    def org_manager(self):
        """Gestionnaire de configuration organisationnelle."""
        return OrganizationConfigManager()
    
    @pytest.fixture
    def mock_db_connection(self):
        """Mock de connexion base de données."""
        mock_db = Mock()
        mock_db.execute = AsyncMock()
        return mock_db
    
    @pytest.fixture
    def db_integration(self, mock_db_connection):
        """Intégration base de données avec mock."""
        integration = RegulAIteDatabaseIntegration(mock_db_connection)
        return integration
    
    @pytest.fixture
    def sample_org_profile(self):
        """Profil d'organisation échantillon."""
        return {
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
                    "risk_assessment": {"depth": "detailed", "focus": "cybersecurity"},
                    "compliance": {"frameworks": ["iso27001", "rgpd"]}
                }
            }
        }
    
    @pytest.fixture
    def mock_llm_client(self):
        """Client LLM mocké."""
        mock_client = Mock()
        mock_client.generate_response = AsyncMock()
        return mock_client

    def test_organization_profile_creation(self, org_manager, sample_org_profile):
        """Test de création d'un profil organisationnel avec templates."""
        profile = org_manager.create_organization_profile(sample_org_profile)
        
        # Vérifications de base
        assert profile.organization_id == sample_org_profile["organization_id"]
        assert profile.name == sample_org_profile["name"]
        assert profile.organization_type == OrganizationType.TECHNOLOGY
        assert profile.sector == RegulatorySector.TECHNOLOGY
        
        # Vérifier l'application des templates sectoriels
        assert len(profile.asset_templates) > 0
        assert len(profile.threat_profile) > 0
        assert len(profile.regulatory_env.primary_frameworks) > 0
        
        # Vérifier les custom settings
        assert "ebios" in profile.preferred_methodologies
        assert "iso27005" in profile.preferred_methodologies
    
    def test_sector_specific_templates(self, org_manager):
        """Test des templates spécifiques par secteur."""
        # Test secteur financier
        financial_org = {
            "organization_id": "bank_001",
            "name": "Banque Test",
            "organization_type": "financial",
            "sector": "banking",
            "size": "large"
        }
        
        profile = org_manager.create_organization_profile(financial_org)
        
        # Vérifier les frameworks financiers
        framework_values = [f.value for f in profile.regulatory_env.primary_frameworks]
        assert "dora" in framework_values or "pci_dss" in framework_values
        assert profile.regulatory_env.regulatory_pressure == "very_high"
        assert profile.risk_appetite == "conservative"
        
        # Vérifier les menaces spécifiques au secteur financier
        threat_types = [t.threat_type for t in profile.threat_profile]
        assert any("cybercrime" in threat.lower() or "nation_state" in threat.lower() 
                  for threat in threat_types)
    
    def test_size_based_adaptations(self, org_manager):
        """Test des adaptations selon la taille d'organisation."""
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

    @pytest.mark.asyncio
    async def test_risk_assessment_with_organizational_context(self, mock_llm_client):
        """Test d'évaluation des risques avec contexte organisationnel."""
        # Setup
        org_manager = OrganizationConfigManager()
        risk_module = RiskAssessmentModule(llm_client=mock_llm_client)
        
        # Créer un profil organisationnel
        org_data = {
            "organization_id": "risk_test_org",
            "name": "Organisation Test Risques",
            "sector": "healthcare",
            "size": "medium",
            "organization_type": "healthcare"
        }
        profile = org_manager.create_organization_profile(org_data)
        
        # Mock des réponses LLM
        mock_llm_client.generate_response.return_value = json.dumps({
            "threat_sources": [
                {"name": "Ransomware", "likelihood": "high", "sophistication": "advanced"},
                {"name": "Data theft", "likelihood": "medium", "sophistication": "intermediate"}
            ]
        })
        
        # Test de récupération du contexte
        context = risk_module._get_organizational_context("risk_test_org")
        assert context["organization_id"] == "risk_test_org"
        
        # Test de récupération d'actifs organisationnels
        assets = risk_module.org_config.get_organization_assets("risk_test_org")
        assert len(assets) > 0
        
        # Vérifier l'adaptation sectorielle
        threats = risk_module.org_config.get_threat_landscape("risk_test_org")
        threat_names = [t["name"] for t in threats]
        # Le secteur healthcare devrait avoir des menaces spécifiques
        assert any("ransomware" in threat.lower() for threat in threat_names)

    @pytest.mark.asyncio
    async def test_database_integration_loading(self, db_integration, mock_db_connection):
        """Test du chargement des profils depuis la base de données."""
        # Mock des données de la base
        mock_org_row = {
            'id': 'db_org_001',
            'name': 'Organisation DB Test',
            'sector': 'technology',
            'size': 'medium',
            'organization_type': 'technology',
            'business_model': 'digital',
            'digital_maturity': 'advanced',
            'risk_appetite': 'moderate',
            'employee_count': 150,
            'annual_revenue': '10M-100M',
            'geographical_presence': '["France", "Europe"]',
            'custom_settings': '{"test": "value"}',
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Mock du cursor et des résultats
        mock_cursor = Mock()
        mock_cursor.fetchall = AsyncMock(return_value=[mock_org_row])
        mock_cursor.fetchone = AsyncMock(return_value=None)
        mock_db_connection.execute.return_value.__aenter__ = AsyncMock(return_value=mock_cursor)
        mock_db_connection.execute.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Test du chargement
        profiles = await db_integration.load_organization_profiles_from_db()
        
        assert len(profiles) >= 1
        assert 'db_org_001' in profiles
        
        profile = profiles['db_org_001']
        assert profile.name == 'Organisation DB Test'
        assert profile.sector == RegulatorySector.TECHNOLOGY
        assert profile.digital_maturity == 'advanced'

    @pytest.mark.asyncio 
    async def test_database_integration_saving(self, db_integration, org_manager, sample_org_profile):
        """Test de sauvegarde des profils en base de données."""
        # Créer un profil
        profile = org_manager.create_organization_profile(sample_org_profile)
        
        # Test de sauvegarde
        result = await db_integration.save_organization_profile(profile)
        assert result is True
        
        # Vérifier que les méthodes de DB ont été appelées
        assert db_integration.db_connection.execute.called

    @pytest.mark.asyncio
    async def test_analysis_result_persistence(self, db_integration):
        """Test de persistance des résultats d'analyse."""
        # Données d'analyse factices
        analysis_result = {
            "assessment_id": "test_assessment_001",
            "risk_scenarios": [
                {
                    "id": "RS-001",
                    "name": "Test Scenario",
                    "risk_level": "medium",
                    "likelihood": "medium",
                    "impact": "high"
                }
            ],
            "recommendations": [
                {"priority": "high", "action": "Implement MFA"}
            ]
        }
        
        metadata = {
            "version": "1.0",
            "methodology": "ebios",
            "duration_seconds": 120
        }
        
        # Test de sauvegarde
        result = await db_integration.save_analysis_result(
            org_id="test_org_001",
            analysis_type="risk_assessment", 
            result=analysis_result,
            metadata=metadata
        )
        
        assert result is True

    def test_organizational_assets_retrieval(self, org_manager, sample_org_profile):
        """Test de récupération d'actifs avec filtrage."""
        profile = org_manager.create_organization_profile(sample_org_profile)
        
        # Test de récupération de tous les actifs
        all_assets = org_manager.get_organization_assets(profile.organization_id)
        assert len(all_assets) > 0
        
        # Test de récupération avec scope
        data_assets = org_manager.get_organization_assets(
            profile.organization_id, 
            scope="data"
        )
        
        # Vérifier que le filtrage fonctionne
        if data_assets:
            for asset in data_assets:
                assert "data" in asset["name"].lower() or asset["type"] == "data"

    def test_threat_landscape_adaptation(self, org_manager):
        """Test d'adaptation du paysage de menaces selon l'organisation."""
        # Organisation technologique
        tech_org = {
            "organization_id": "tech_001",
            "name": "Tech Company",
            "sector": "technology",
            "size": "startup"
        }
        tech_profile = org_manager.create_organization_profile(tech_org)
        tech_threats = org_manager.get_threat_landscape("tech_001")
        
        # Organisation financière
        bank_org = {
            "organization_id": "bank_001", 
            "name": "Bank Company",
            "sector": "banking",
            "size": "large"
        }
        bank_profile = org_manager.create_organization_profile(bank_org)
        bank_threats = org_manager.get_threat_landscape("bank_001")
        
        # Vérifier les différences
        tech_threat_types = [t["name"] for t in tech_threats]
        bank_threat_types = [t["name"] for t in bank_threats]
        
        # Les menaces peuvent être différentes selon le secteur
        assert len(tech_threats) > 0
        assert len(bank_threats) > 0

    def test_regulatory_context_retrieval(self, org_manager):
        """Test de récupération du contexte réglementaire."""
        # Organisation healthcare
        healthcare_org = {
            "organization_id": "hospital_001",
            "name": "Hospital Test", 
            "sector": "healthcare",
            "organization_type": "healthcare"
        }
        
        profile = org_manager.create_organization_profile(healthcare_org)
        regulatory_context = org_manager.get_regulatory_context("hospital_001")
        
        assert "frameworks" in regulatory_context
        assert "pressure" in regulatory_context
        assert regulatory_context["pressure"] == "very_high"  # Healthcare = high pressure
        
        # Vérifier les frameworks healthcare
        frameworks = regulatory_context["frameworks"]
        assert any(f in ["hipaa", "rgpd"] for f in frameworks)

    def test_governance_context_retrieval(self, org_manager, sample_org_profile):
        """Test de récupération du contexte de gouvernance."""
        profile = org_manager.create_organization_profile(sample_org_profile)
        governance_context = org_manager.get_governance_context(profile.organization_id)
        
        assert "maturity" in governance_context
        assert "structure" in governance_context or "transformation_stage" in governance_context
        
        # Vérifier la structure de maturité
        maturity = governance_context["maturity"]
        assert isinstance(maturity, dict)
        assert len(maturity) > 0

    @pytest.mark.asyncio
    async def test_end_to_end_risk_assessment_flow(self, mock_llm_client):
        """Test complet du flux d'évaluation des risques avec contexte organisationnel."""
        # 1. Créer une organisation
        org_manager = OrganizationConfigManager()
        org_data = {
            "organization_id": "e2e_test_org",
            "name": "End-to-End Test Organization",
            "sector": "technology",
            "size": "medium",
            "organization_type": "technology"
        }
        profile = org_manager.create_organization_profile(org_data)
        
        # 2. Initialiser le module de risque
        risk_module = RiskAssessmentModule(llm_client=mock_llm_client)
        
        # 3. Mock des réponses LLM pour l'analyse
        mock_responses = [
            # Réponse pour l'identification des menaces
            json.dumps({
                "threat_sources": [
                    {
                        "name": "Advanced Persistent Threat",
                        "likelihood": "medium",
                        "sophistication": "advanced",
                        "motivation": "espionage"
                    }
                ]
            }),
            # Réponse pour la création de scénario
            json.dumps({
                "name": "APT targeting source code",
                "description": "Advanced threat targeting intellectual property",
                "threat_action": "Code exfiltration via backdoor",
                "vulnerability": "Insufficient access controls",
                "likelihood": "medium",
                "impact": "high"
            })
        ]
        
        mock_llm_client.generate_response.side_effect = mock_responses
        
        # 4. Créer une requête avec contexte organisationnel
        query = Query(
            query_text="Effectue une évaluation des risques pour notre infrastructure IT",
            context=QueryContext(context_data={"organization_id": "e2e_test_org"})
        )
        
        # 5. Traiter la requête
        response = await risk_module.process_query(query)
        
        # 6. Vérifications
        assert response is not None
        assert response.agent_id == "risk_assessment"
        
        # Vérifier que le contexte organisationnel a été utilisé
        assert mock_llm_client.generate_response.called
        
        # Vérifier que les calls LLM incluent le contexte organisationnel
        calls = mock_llm_client.generate_response.call_args_list
        for call in calls:
            messages = call[1]["messages"] if "messages" in call[1] else call[0][0]["messages"]
            user_message = next((m for m in messages if m["role"] == "user"), None)
            if user_message:
                content = user_message["content"]
                # Le contenu devrait inclure des informations organisationnelles
                assert "technology" in content.lower() or "medium" in content.lower()

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 