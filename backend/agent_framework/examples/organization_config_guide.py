#!/usr/bin/env python3
"""
RegulAIte Organization Configuration Guide
A standalone example showing how to configure your organization.
"""

def print_configuration_guide():
    """Print a comprehensive organization configuration guide."""
    
    print("🚀 RegulAIte Organization Configuration Guide")
    print("=" * 60)
    
    print("\n📋 **Step 1: Basic Organization Information**")
    print("-" * 50)
    
    basic_config = {
        "organization_id": "your-company-2024",
        "name": "Your Company Name",
        "organization_type": "technology",  # See options below
        "sector": "technology",
        "size": "medium", 
        "employee_count": 250,
        "annual_revenue": "10M-100M"
    }
    
    print("Required fields:")
    for key, value in basic_config.items():
        print(f"  • {key}: {value}")
    
    print("\n🏢 **Organization Types Available:**")
    org_types = [
        "startup - Early-stage companies", 
        "sme - Small/Medium Enterprise",
        "large_corp - Large Corporation",
        "public_sector - Government entities",
        "healthcare - Healthcare organizations", 
        "financial - Financial institutions",
        "technology - Tech companies",
        "manufacturing - Manufacturing companies",
        "energy - Energy sector",
        "telecom - Telecommunications"
    ]
    for org_type in org_types:
        print(f"  • {org_type}")
    
    print("\n📈 **Regulatory Sectors:**")
    sectors = ["banking", "insurance", "healthcare", "energy", "telecom", "technology", "public", "general"]
    for sector in sectors:
        print(f"  • {sector}")
    
    print("\n📊 **Size Categories:**")
    sizes = [
        "startup - Limited resources, high agility",
        "small - Developing governance, moderate resources", 
        "medium - Defined processes, adequate budget",
        "large - Managed governance, substantial resources"
    ]
    for size in sizes:
        print(f"  • {size}")
    
    print("\n🌍 **Step 2: Operational Context**")
    print("-" * 50)
    
    operational_config = {
        "geographical_presence": ["France", "EU", "International"],
        "business_model": "digital",  # traditional, digital, hybrid, platform
        "digital_maturity": "advanced",  # basic, intermediate, advanced, leading
        "transformation_stage": "evolving"  # stable, evolving, transforming, disrupting
    }
    
    print("Operational context fields:")
    for key, value in operational_config.items():
        print(f"  • {key}: {value}")
    
    print("\n⚖️ **Step 3: Risk & Governance Configuration**")
    print("-" * 50)
    
    risk_config = {
        "risk_appetite": "moderate",  # conservative, moderate, aggressive
        "risk_tolerance": {
            "cyber": "low",
            "operational": "medium", 
            "financial": "low",
            "regulatory": "very_low"
        },
        "governance_maturity": {
            "strategic": "managed",
            "risk": "defined",
            "compliance": "developing"
        }
    }
    
    print("Risk and governance settings:")
    for key, value in risk_config.items():
        if isinstance(value, dict):
            print(f"  • {key}:")
            for sub_key, sub_value in value.items():
                print(f"    - {sub_key}: {sub_value}")
        else:
            print(f"  • {key}: {value}")
    
    print("\n🛡️ **Step 4: Compliance & Methodology Preferences**")
    print("-" * 50)
    
    compliance_config = {
        "preferred_methodologies": ["ISO27001", "NIST", "RGPD"],
        "analysis_preferences": {
            "report_format": "executive_summary",
            "detail_level": "high",
            "focus_areas": ["cybersecurity", "data_protection", "cloud_security"]
        }
    }
    
    print("Compliance configuration:")
    for key, value in compliance_config.items():
        if isinstance(value, dict):
            print(f"  • {key}:")
            for sub_key, sub_value in value.items():
                print(f"    - {sub_key}: {sub_value}")
        else:
            print(f"  • {key}: {value}")
    
    print("\n🎯 **Available Compliance Frameworks:**")
    frameworks = [
        "ISO27001 - Information Security Management",
        "RGPD - General Data Protection Regulation", 
        "DORA - Digital Operational Resilience Act",
        "NIST - Cybersecurity Framework",
        "SOX - Sarbanes-Oxley Act",
        "PCI_DSS - Payment Card Industry Standard",
        "HIPAA - Health Insurance Portability",
        "ANSSI - French Cybersecurity Agency"
    ]
    for framework in frameworks:
        print(f"  • {framework}")

def show_sector_examples():
    """Show configuration examples for different sectors."""
    
    print("\n\n🏭 **Sector-Specific Configuration Examples**")
    print("=" * 60)
    
    examples = {
        "Technology Company": {
            "organization_type": "technology",
            "sector": "technology", 
            "risk_appetite": "moderate",
            "frameworks": ["ISO27001", "RGPD", "NIST"],
            "regulatory_pressure": "medium",
            "key_assets": ["Source code", "Customer data", "Infrastructure"],
            "main_threats": ["Advanced APT", "Supply chain", "IP theft"]
        },
        
        "Banking Institution": {
            "organization_type": "financial",
            "sector": "banking",
            "risk_appetite": "conservative", 
            "frameworks": ["DORA", "PCI_DSS", "ISO27001"],
            "regulatory_pressure": "very_high",
            "key_assets": ["Payment systems", "Customer data", "Trading platforms"],
            "main_threats": ["Cybercrime", "Insider threat", "Nation state"]
        },
        
        "Healthcare Organization": {
            "organization_type": "healthcare",
            "sector": "healthcare",
            "risk_appetite": "conservative",
            "frameworks": ["HIPAA", "RGPD", "ISO27001"], 
            "regulatory_pressure": "very_high",
            "key_assets": ["Patient data", "Medical devices", "EHR systems"],
            "main_threats": ["Ransomware", "Data theft", "Insider threat"]
        }
    }
    
    for sector_name, config in examples.items():
        print(f"\n🏢 **{sector_name}**")
        print("-" * 40)
        for key, value in config.items():
            if isinstance(value, list):
                print(f"  • {key}: {', '.join(value)}")
            else:
                print(f"  • {key}: {value}")

def show_implementation_code():
    """Show the actual implementation code."""
    
    print("\n\n💻 **Implementation Code Example**")
    print("=" * 60)
    
    code_example = '''
# Example: Configure a technology company
from backend.agent_framework.modules.organization_config import OrganizationConfigManager

# Initialize the manager
config_manager = OrganizationConfigManager()

# Define your organization
org_data = {
    "organization_id": "tech-corp-2024",
    "name": "TechCorp Solutions", 
    "organization_type": "technology",
    "sector": "technology",
    "size": "medium",
    "employee_count": 250,
    "annual_revenue": "50M-100M",
    
    # Custom settings
    "custom_settings": {
        "preferred_methodologies": ["ISO27001", "NIST"],
        "risk_appetite": "moderate",
        "analysis_preferences": {
            "detail_level": "high",
            "focus_areas": ["cybersecurity", "data_protection"]
        }
    }
}

# Create the organization profile
profile = config_manager.create_organization_profile(org_data, use_templates=True)

# Access your configuration
assets = config_manager.get_organization_assets(profile.organization_id)
threats = config_manager.get_threat_landscape(profile.organization_id) 
regulatory_context = config_manager.get_regulatory_context(profile.organization_id)
governance_context = config_manager.get_governance_context(profile.organization_id)
'''
    
    print(code_example)

def show_next_steps():
    """Show what to do after configuration."""
    
    print("\n📝 **Next Steps After Configuration**")
    print("=" * 60)
    
    steps = [
        "1. Review auto-generated assets and customize if needed",
        "2. Adjust threat profiles based on your specific context", 
        "3. Set governance maturity levels to match current state",
        "4. Configure risk tolerance thresholds for each risk type",
        "5. Define compliance timeline and audit schedules",
        "6. Set up analysis preferences and reporting formats",
        "7. Test the configuration with a sample analysis",
        "8. Train your team on the RegulAIte interface"
    ]
    
    for step in steps:
        print(f"  ✓ {step}")
    
    print("\n🎯 **Configuration Benefits:**")
    benefits = [
        "• Tailored risk assessments for your industry",
        "• Automatic compliance framework mapping", 
        "• Contextual threat landscape analysis",
        "• Industry-specific asset templates",
        "• Governance maturity benchmarking",
        "• Regulatory pressure calibration",
        "• Customized reporting and analysis"
    ]
    
    for benefit in benefits:
        print(f"  {benefit}")

if __name__ == "__main__":
    print_configuration_guide()
    show_sector_examples()
    show_implementation_code()
    show_next_steps()
    
    print(f"\n✨ **Your Organization is Ready for RegulAIte!**")
    print("The system will automatically adapt all analyses to your organizational context.") 