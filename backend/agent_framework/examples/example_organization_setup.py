#!/usr/bin/env python3
"""
Example: How to configure your organization in RegulAIte
This script demonstrates the complete organization configuration process.
"""

from backend.agent_framework.modules.organization_config import (
    OrganizationConfigManager,
    OrganizationType,
    RegulatorySector,
    ComplianceFramework
)

def setup_example_organization():
    """Example of setting up a technology company."""
    
    # Initialize the configuration manager
    config_manager = OrganizationConfigManager()
    
    # 1. Basic organization data
    org_data = {
        "organization_id": "tech-company-001",
        "name": "TechCorp Solutions",
        "organization_type": "technology",
        "sector": "technology", 
        "size": "medium",
        "employee_count": 250,
        "annual_revenue": "50M-100M",
        
        # Operational context
        "geographical_presence": ["France", "Germany", "UK"],
        "business_model": "digital",
        "digital_maturity": "advanced",
        "transformation_stage": "evolving"
    }
    
    # 2. Custom settings for governance and risk
    custom_settings = {
        "preferred_methodologies": ["ISO27001", "NIST"],
        "analysis_preferences": {
            "report_format": "executive_summary",
            "detail_level": "high",
            "focus_areas": ["cybersecurity", "data_protection", "cloud_security"]
        },
        "risk_appetite": "moderate",
        "governance_preferences": {
            "board_reporting": "quarterly",
            "risk_committee": True,
            "external_audits": "annual"
        }
    }
    
    org_data["custom_settings"] = custom_settings
    
    # 3. Create the organization profile
    profile = config_manager.create_organization_profile(org_data, use_templates=True)
    
    print(f"✅ Organization '{profile.name}' configured successfully!")
    print(f"📊 Organization ID: {profile.organization_id}")
    print(f"🏢 Type: {profile.organization_type.value}")
    print(f"📈 Sector: {profile.sector.value}")
    print(f"👥 Size: {profile.size} ({profile.employee_count} employees)")
    
    # 4. Display applied configurations
    print("\n🛡️ **Regulatory Context:**")
    reg_context = config_manager.get_regulatory_context(profile.organization_id)
    for framework in reg_context["frameworks"]:
        print(f"  - {framework.upper()}")
    print(f"  - Regulatory pressure: {reg_context['pressure']}")
    
    print("\n🎯 **Key Assets:**")
    assets = config_manager.get_organization_assets(profile.organization_id)
    for asset in assets[:5]:  # Show first 5
        print(f"  - {asset['name']} (Criticality: {asset['criticality']})")
    
    print("\n⚠️ **Threat Landscape:**")
    threats = config_manager.get_threat_landscape(profile.organization_id)
    for threat in threats[:3]:  # Show first 3
        print(f"  - {threat['name']} (Likelihood: {threat['likelihood']})")
    
    print("\n🏛️ **Governance Maturity:**")
    governance = config_manager.get_governance_context(profile.organization_id)
    for domain, level in governance["maturity"].items():
        print(f"  - {domain.title()}: {level}")
    
    return profile

def setup_banking_organization():
    """Example of setting up a banking organization."""
    
    config_manager = OrganizationConfigManager()
    
    org_data = {
        "organization_id": "eurobank-001", 
        "name": "EuroBank Financial",
        "organization_type": "financial",
        "sector": "banking",
        "size": "large",
        "employee_count": 1500,
        "annual_revenue": ">1B",
        "geographical_presence": ["France", "EU"],
        "business_model": "traditional",
        "digital_maturity": "intermediate"
    }
    
    custom_settings = {
        "preferred_methodologies": ["DORA", "PCI_DSS", "ISO27001"],
        "analysis_preferences": {
            "regulatory_focus": True,
            "audit_readiness": True,
            "detail_level": "very_high"
        },
        "risk_appetite": "conservative"
    }
    
    org_data["custom_settings"] = custom_settings
    profile = config_manager.create_organization_profile(org_data, use_templates=True)
    
    print(f"\n🏦 Banking Organization '{profile.name}' configured!")
    reg_context = config_manager.get_regulatory_context(profile.organization_id)
    print(f"📋 Regulatory frameworks: {', '.join(reg_context['frameworks'])}")
    print(f"⚡ Regulatory pressure: {reg_context['pressure']}")
    
    return profile

def setup_healthcare_organization():
    """Example of setting up a healthcare organization."""
    
    config_manager = OrganizationConfigManager()
    
    org_data = {
        "organization_id": "medtech-001",
        "name": "MedTech Solutions",
        "organization_type": "healthcare", 
        "sector": "healthcare",
        "size": "medium",
        "employee_count": 500,
        "annual_revenue": "100M-1B",
        "geographical_presence": ["France", "EU", "US"],
        "business_model": "hybrid"
    }
    
    custom_settings = {
        "preferred_methodologies": ["HIPAA", "RGPD", "ISO27001"],
        "analysis_preferences": {
            "patient_data_focus": True,
            "medical_device_security": True,
            "detail_level": "high"
        },
        "risk_appetite": "conservative"
    }
    
    org_data["custom_settings"] = custom_settings
    profile = config_manager.create_organization_profile(org_data, use_templates=True)
    
    print(f"\n🏥 Healthcare Organization '{profile.name}' configured!")
    assets = config_manager.get_organization_assets(profile.organization_id)
    print("🔒 Critical healthcare assets identified:")
    for asset in assets[:3]:
        print(f"  - {asset['name']}")
    
    return profile

if __name__ == "__main__":
    print("🚀 RegulAIte Organization Configuration Examples\n")
    print("=" * 60)
    
    # Set up different types of organizations
    tech_profile = setup_example_organization()
    banking_profile = setup_banking_organization() 
    healthcare_profile = setup_healthcare_organization()
    
    print(f"\n✅ Successfully configured {len([tech_profile, banking_profile, healthcare_profile])} organizations!")
    print("\n📝 **Next Steps:**")
    print("1. Review and customize the auto-generated assets and threat profiles")
    print("2. Adjust governance maturity levels based on current state") 
    print("3. Configure specific compliance requirements")
    print("4. Set up risk tolerance thresholds")
    print("5. Define custom analysis preferences")
    print("\n🎯 Your organization is now ready for RegulAIte analysis!") 