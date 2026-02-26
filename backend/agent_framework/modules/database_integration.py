"""
Database Integration Module - Intégration avec la base de données RegulAIte.
Gère la persistance des profils organisationnels et des résultats d'analyse.
"""
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import asdict
import asyncio

from .organization_config import (
    OrganizationProfile, OrganizationConfigManager, AssetTemplate, ThreatProfile,
    RegulatoryEnvironment, OrganizationType, RegulatorySector, ComplianceFramework
)

logger = logging.getLogger(__name__)

class RegulAIteDatabaseIntegration:
    """
    Intégration avec la base de données RegulAIte pour la persistance des configurations organisationnelles.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize database integration.
        
        Args:
            db_connection: Connexion à la base de données RegulAIte (MariaDB/MySQL)
        """
        self.db_connection = db_connection
        self.org_config_manager = None
        
    def set_org_config_manager(self, manager: OrganizationConfigManager):
        """Définit le gestionnaire de configuration organisationnelle."""
        self.org_config_manager = manager
    
    async def load_organization_profiles_from_db(self) -> Dict[str, OrganizationProfile]:
        """
        Charge les profils organisationnels depuis la base de données RegulAIte.
        """
        profiles = {}
        
        try:
            if not self.db_connection:
                logger.warning("Pas de connexion DB - utilisation des profils par défaut")
                return self._create_default_profiles()
            
            # Requête pour récupérer les organisations depuis la table organizations
            query = """
            SELECT 
                o.id, o.name, o.sector, o.size, o.employee_count, o.annual_revenue,
                o.organization_type, o.business_model, o.digital_maturity,
                o.risk_appetite, o.created_at, o.updated_at,
                o.geographical_presence, o.custom_settings
            FROM organizations o
            WHERE o.active = 1
            """
            
            async with self.db_connection.execute(query) as cursor:
                rows = await cursor.fetchall()
                
                for row in rows:
                    org_profile = await self._create_profile_from_db_row(row)
                    if org_profile:
                        profiles[org_profile.organization_id] = org_profile
                        
            logger.info(f"Chargé {len(profiles)} profils organisationnels depuis la DB")
            
        except Exception as e:
            logger.error(f"Erreur chargement profils DB: {str(e)}")
            profiles = self._create_default_profiles()
            
        return profiles
    
    async def _create_profile_from_db_row(self, row: Dict[str, Any]) -> Optional[OrganizationProfile]:
        """Crée un profil organisationnel à partir d'une ligne de base de données."""
        try:
            # Parse custom settings JSON
            custom_settings = {}
            if row.get('custom_settings'):
                try:
                    custom_settings = json.loads(row['custom_settings'])
                except json.JSONDecodeError:
                    logger.warning(f"Erreur parsing custom_settings pour org {row['id']}")
            
            # Parse geographical presence
            geographical_presence = []
            if row.get('geographical_presence'):
                try:
                    geographical_presence = json.loads(row['geographical_presence'])
                except json.JSONDecodeError:
                    geographical_presence = [row['geographical_presence']]
            
            # Créer le profil de base
            profile = OrganizationProfile(
                organization_id=str(row['id']),
                name=row['name'],
                organization_type=OrganizationType(row.get('organization_type', 'technology')),
                sector=RegulatorySector(row.get('sector', 'general')),
                size=row.get('size', 'medium'),
                employee_count=row.get('employee_count', 100),
                annual_revenue=row.get('annual_revenue', '10M-100M'),
                geographical_presence=geographical_presence,
                business_model=row.get('business_model', 'traditional'),
                digital_maturity=row.get('digital_maturity', 'intermediate'),
                risk_appetite=row.get('risk_appetite', 'moderate'),
                created_date=row.get('created_at', datetime.now()),
                last_updated=row.get('updated_at', datetime.now())
            )
            
            # Charger les données associées
            await self._load_organization_assets(profile)
            await self._load_organization_threats(profile)
            await self._load_regulatory_environment(profile)
            await self._load_governance_maturity(profile)
            
            # Appliquer les custom settings
            if custom_settings:
                if 'preferred_methodologies' in custom_settings:
                    profile.preferred_methodologies = custom_settings['preferred_methodologies']
                if 'analysis_preferences' in custom_settings:
                    profile.analysis_preferences = custom_settings['analysis_preferences']
            
            return profile
            
        except Exception as e:
            logger.error(f"Erreur création profil pour org {row.get('id')}: {str(e)}")
            return None
    
    async def _load_organization_assets(self, profile: OrganizationProfile):
        """Charge les actifs organisationnels depuis la DB."""
        try:
            query = """
            SELECT asset_id, asset_name, asset_type, criticality, description, 
                   owner, location, business_value, regulatory_classification
            FROM organization_assets 
            WHERE organization_id = %s AND active = 1
            """
            
            async with self.db_connection.execute(query, (profile.organization_id,)) as cursor:
                rows = await cursor.fetchall()
                
                for row in rows:
                    asset = AssetTemplate(
                        id=row['asset_id'],
                        name=row['asset_name'],
                        type=row['asset_type'],
                        criticality=row['criticality'],
                        description=row.get('description', ''),
                        owner=row.get('owner', ''),
                        location=row.get('location', ''),
                        business_value=row.get('business_value', 'medium'),
                        regulatory_classification=row.get('regulatory_classification', '')
                    )
                    profile.asset_templates.append(asset)
                    
        except Exception as e:
            logger.error(f"Erreur chargement actifs pour org {profile.organization_id}: {str(e)}")
    
    async def _load_organization_threats(self, profile: OrganizationProfile):
        """Charge le profil de menaces depuis la DB."""
        try:
            query = """
            SELECT threat_type, likelihood, sophistication, motivation, 
                   resources, persistence
            FROM organization_threat_profiles 
            WHERE organization_id = %s AND active = 1
            """
            
            async with self.db_connection.execute(query, (profile.organization_id,)) as cursor:
                rows = await cursor.fetchall()
                
                for row in rows:
                    threat = ThreatProfile(
                        threat_type=row['threat_type'],
                        likelihood=row['likelihood'],
                        sophistication=row['sophistication'],
                        motivation=row['motivation'],
                        resources=row['resources'],
                        persistence=row['persistence']
                    )
                    profile.threat_profile.append(threat)
                    
        except Exception as e:
            logger.error(f"Erreur chargement menaces pour org {profile.organization_id}: {str(e)}")
    
    async def _load_regulatory_environment(self, profile: OrganizationProfile):
        """Charge l'environnement réglementaire depuis la DB."""
        try:
            query = """
            SELECT frameworks, regulatory_pressure, audit_frequency, 
                   penalties_exposure, external_oversight, certification_requirements
            FROM organization_regulatory_env 
            WHERE organization_id = %s
            """
            
            async with self.db_connection.execute(query, (profile.organization_id,)) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    # Parse frameworks JSON
                    frameworks = []
                    if row.get('frameworks'):
                        try:
                            framework_list = json.loads(row['frameworks'])
                            frameworks = [ComplianceFramework(f) for f in framework_list if f in ComplianceFramework._value2member_map_]
                        except (json.JSONDecodeError, ValueError):
                            logger.warning(f"Erreur parsing frameworks pour org {profile.organization_id}")
                    
                    # Parse oversight and certifications
                    external_oversight = []
                    certification_requirements = []
                    
                    if row.get('external_oversight'):
                        try:
                            external_oversight = json.loads(row['external_oversight'])
                        except json.JSONDecodeError:
                            external_oversight = [row['external_oversight']]
                    
                    if row.get('certification_requirements'):
                        try:
                            certification_requirements = json.loads(row['certification_requirements'])
                        except json.JSONDecodeError:
                            certification_requirements = [row['certification_requirements']]
                    
                    profile.regulatory_env = RegulatoryEnvironment(
                        primary_frameworks=frameworks,
                        regulatory_pressure=row.get('regulatory_pressure', 'medium'),
                        audit_frequency=row.get('audit_frequency', 'annual'),
                        penalties_exposure=row.get('penalties_exposure', 'medium'),
                        external_oversight=external_oversight,
                        certification_requirements=certification_requirements
                    )
                    
        except Exception as e:
            logger.error(f"Erreur chargement env. réglementaire pour org {profile.organization_id}: {str(e)}")
    
    async def _load_governance_maturity(self, profile: OrganizationProfile):
        """Charge la maturité de gouvernance depuis la DB."""
        try:
            query = """
            SELECT domain, maturity_level, assessment_date
            FROM organization_governance_maturity 
            WHERE organization_id = %s AND active = 1
            """
            
            async with self.db_connection.execute(query, (profile.organization_id,)) as cursor:
                rows = await cursor.fetchall()
                
                governance_maturity = {}
                for row in rows:
                    governance_maturity[row['domain']] = row['maturity_level']
                
                profile.governance_maturity = governance_maturity
                    
        except Exception as e:
            logger.error(f"Erreur chargement gouvernance pour org {profile.organization_id}: {str(e)}")
    
    async def save_organization_profile(self, profile: OrganizationProfile) -> bool:
        """
        Sauvegarde un profil organisationnel dans la base de données.
        """
        try:
            if not self.db_connection:
                logger.warning("Pas de connexion DB - profil non sauvegardé")
                return False
            
            # Upsert organization
            await self._upsert_organization(profile)
            
            # Sauvegarder les données associées
            await self._save_organization_assets(profile)
            await self._save_organization_threats(profile)
            await self._save_regulatory_environment(profile)
            await self._save_governance_maturity(profile)
            
            logger.info(f"Profil organisationnel {profile.organization_id} sauvegardé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde profil {profile.organization_id}: {str(e)}")
            return False
    
    async def _upsert_organization(self, profile: OrganizationProfile):
        """Upsert de l'organisation principale."""
        query = """
        INSERT INTO organizations (
            id, name, sector, size, employee_count, annual_revenue,
            organization_type, business_model, digital_maturity, risk_appetite,
            geographical_presence, custom_settings, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            sector = VALUES(sector),
            size = VALUES(size),
            employee_count = VALUES(employee_count),
            annual_revenue = VALUES(annual_revenue),
            organization_type = VALUES(organization_type),
            business_model = VALUES(business_model),
            digital_maturity = VALUES(digital_maturity),
            risk_appetite = VALUES(risk_appetite),
            geographical_presence = VALUES(geographical_presence),
            custom_settings = VALUES(custom_settings),
            updated_at = VALUES(updated_at)
        """
        
        custom_settings = {
            'preferred_methodologies': profile.preferred_methodologies,
            'analysis_preferences': profile.analysis_preferences,
            'custom_frameworks': profile.custom_frameworks
        }
        
        await self.db_connection.execute(query, (
            profile.organization_id,
            profile.name,
            profile.sector.value,
            profile.size,
            profile.employee_count,
            profile.annual_revenue,
            profile.organization_type.value,
            profile.business_model,
            profile.digital_maturity,
            profile.risk_appetite,
            json.dumps(profile.geographical_presence),
            json.dumps(custom_settings),
            datetime.now()
        ))
    
    async def save_analysis_result(
        self, 
        org_id: str, 
        analysis_type: str, 
        result: Dict[str, Any], 
        metadata: Dict[str, Any] = None
    ) -> bool:
        """
        Sauvegarde un résultat d'analyse dans la base de données.
        """
        try:
            if not self.db_connection:
                return False
            
            query = """
            INSERT INTO analysis_results (
                organization_id, analysis_type, result_data, metadata, created_at
            ) VALUES (%s, %s, %s, %s, %s)
            """
            
            await self.db_connection.execute(query, (
                org_id,
                analysis_type,
                json.dumps(result, default=str),
                json.dumps(metadata or {}, default=str),
                datetime.now()
            ))
            
            logger.info(f"Résultat d'analyse {analysis_type} sauvegardé pour org {org_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur sauvegarde résultat d'analyse: {str(e)}")
            return False
    
    def _create_default_profiles(self) -> Dict[str, OrganizationProfile]:
        """Crée des profils par défaut si la DB n'est pas disponible."""
        default_profile = OrganizationProfile(
            organization_id="default_org",
            name="Organisation par défaut",
            organization_type=OrganizationType.TECHNOLOGY,
            sector=RegulatorySector.TECHNOLOGY,
            size="medium",
            employee_count=100,
            annual_revenue="10M-100M"
        )
        
        # Ajouter quelques actifs par défaut
        default_profile.asset_templates = [
            AssetTemplate(
                id="SYS-001",
                name="Systèmes d'information",
                type="system",
                criticality="high"
            ),
            AssetTemplate(
                id="DATA-001", 
                name="Données sensibles",
                type="data",
                criticality="very_high"
            )
        ]
        
        return {"default_org": default_profile}

# Factory function
def get_database_integration(db_connection=None) -> RegulAIteDatabaseIntegration:
    """Factory function pour obtenir une instance d'intégration DB."""
    return RegulAIteDatabaseIntegration(db_connection=db_connection) 