"""
Organization Router - API endpoints for organization configuration and management.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import logging
from datetime import datetime
from enum import Enum

# Define enums locally to avoid import issues
class OrganizationType(Enum):
    STARTUP = "startup"
    SME = "sme"
    LARGE_CORP = "large_corp"
    PUBLIC_SECTOR = "public_sector"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    TECHNOLOGY = "technology"
    MANUFACTURING = "manufacturing"
    ENERGY = "energy"
    TELECOM = "telecom"

class RegulatorySector(Enum):
    BANKING = "banking"
    INSURANCE = "insurance"
    HEALTHCARE = "healthcare"
    ENERGY = "energy"
    TELECOM = "telecom"
    TECHNOLOGY = "technology"
    PUBLIC = "public"
    GENERAL = "general"

class ComplianceFramework(Enum):
    ISO27001 = "iso27001"
    RGPD = "rgpd"
    DORA = "dora"
    NIST = "nist"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    HIPAA = "hipaa"
    ANSSI = "anssi"

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/organizations", tags=["organizations"])

# Pydantic models for API
class OrganizationCreateRequest(BaseModel):
    """Request model for creating an organization."""
    organization_id: Optional[str] = None
    name: str = Field(..., description="Organization name")
    organization_type: str = Field(default="technology", description="Type of organization")
    sector: str = Field(default="technology", description="Regulatory sector")
    size: str = Field(default="medium", description="Organization size")
    employee_count: int = Field(default=250, description="Number of employees")
    annual_revenue: str = Field(default="10M-100M", description="Annual revenue range")
    
    # Operational context
    geographical_presence: List[str] = Field(default_factory=list, description="Geographical presence")
    business_model: str = Field(default="digital", description="Business model")
    digital_maturity: str = Field(default="intermediate", description="Digital maturity level")
    transformation_stage: str = Field(default="evolving", description="Transformation stage")
    
    # Risk & Governance
    risk_appetite: str = Field(default="moderate", description="Risk appetite")
    risk_tolerance: Dict[str, str] = Field(default_factory=dict, description="Risk tolerance by category")
    governance_maturity: Dict[str, str] = Field(default_factory=dict, description="Governance maturity levels")
    
    # Preferences
    preferred_methodologies: List[str] = Field(default_factory=list, description="Preferred compliance frameworks")
    analysis_preferences: Dict[str, Any] = Field(default_factory=dict, description="Analysis preferences")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")

class OrganizationResponse(BaseModel):
    """Response model for organization data."""
    organization_id: str
    name: str
    organization_type: str
    sector: str
    size: str
    employee_count: int
    annual_revenue: str
    geographical_presence: List[str]
    business_model: str
    digital_maturity: str
    transformation_stage: str
    risk_appetite: str
    created_date: datetime
    last_updated: datetime

class AssetResponse(BaseModel):
    """Response model for organization assets."""
    id: str
    name: str
    type: str
    criticality: str
    description: str
    owner: str
    business_value: str
    regulatory_classification: str

class ThreatResponse(BaseModel):
    """Response model for threat profile."""
    name: str
    likelihood: str
    sophistication: str
    motivation: str
    resources: str
    persistence: str

class RegulatoryContextResponse(BaseModel):
    """Response model for regulatory context."""
    frameworks: List[str]
    pressure: str
    audit_frequency: str
    penalties_exposure: str
    certifications: List[str]

class GovernanceContextResponse(BaseModel):
    """Response model for governance context."""
    maturity: Dict[str, str]
    board_composition: Dict[str, Any]
    reporting_structure: Dict[str, Any]
    transformation_stage: str

class OrganizationTemplatesResponse(BaseModel):
    """Response model for organization templates."""
    organization_types: List[Dict[str, str]]
    regulatory_sectors: List[Dict[str, str]]
    size_categories: List[Dict[str, str]]
    compliance_frameworks: List[Dict[str, str]]

@router.get("/templates", response_model=OrganizationTemplatesResponse)
async def get_organization_templates():
    """Get organization configuration templates and options."""
    try:
        organization_types = [
            {"value": t.value, "label": t.value.replace("_", " ").title(), "description": f"{t.value.replace('_', ' ').title()} organization"}
            for t in OrganizationType
        ]
        
        regulatory_sectors = [
            {"value": s.value, "label": s.value.title(), "description": f"{s.value.title()} sector"}
            for s in RegulatorySector
        ]
        
        size_categories = [
            {"value": "startup", "label": "Startup", "description": "Limited resources, high agility"},
            {"value": "small", "label": "Small", "description": "Developing governance, moderate resources"},
            {"value": "medium", "label": "Medium", "description": "Defined processes, adequate budget"},
            {"value": "large", "label": "Large", "description": "Managed governance, substantial resources"}
        ]
        
        compliance_frameworks = [
            {"value": f.value, "label": f.value.upper().replace("_", " "), "description": f"{f.value.upper().replace('_', ' ')} compliance framework"}
            for f in ComplianceFramework
        ]
        
        return OrganizationTemplatesResponse(
            organization_types=organization_types,
            regulatory_sectors=regulatory_sectors,
            size_categories=size_categories,
            compliance_frameworks=compliance_frameworks
        )
        
    except Exception as e:
        logger.error(f"Error fetching organization templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organization templates: {str(e)}"
        )

@router.post("/validate", response_model=Dict[str, Any])
async def validate_organization_config(
    org_data: OrganizationCreateRequest
):
    """Validate organization configuration before creation."""
    try:
        # For now, perform basic validation
        # TODO: Implement comprehensive validation logic
        
        errors = []
        warnings = []
        
        # Basic validation
        if not org_data.name:
            errors.append("Organization name is required")
        
        if not org_data.organization_type:
            errors.append("Organization type is required")
        
        if org_data.employee_count < 1:
            errors.append("Employee count must be greater than 0")
        
        # Add some warnings for best practices
        if not org_data.preferred_methodologies:
            warnings.append("Consider selecting at least one compliance framework")
        
        if not org_data.geographical_presence:
            warnings.append("Consider specifying geographical presence")
        
        is_valid = len(errors) == 0
        
        return {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "suggestions": ["Consider adding more details for better analysis"] if is_valid else []
        }
        
    except Exception as e:
        logger.error(f"Error validating organization config: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to validate organization config: {str(e)}"
        )

@router.post("/", response_model=dict)
async def create_organization(
    org_data: OrganizationCreateRequest
):
    """Create a new organization profile."""
    try:
        # For now, just return a success response
        # TODO: Implement actual organization creation with database storage
        
        # Generate organization ID if not provided
        org_id = org_data.organization_id or f"{org_data.name.lower().replace(' ', '-')}-{int(datetime.now().timestamp())}"
        
        logger.info(f"Organization creation requested: {org_id}")
        
        return {
            "status": "success",
            "message": f"Organization '{org_data.name}' created successfully",
            "organization_id": org_id,
            "name": org_data.name,
            "organization_type": org_data.organization_type,
            "sector": org_data.sector
        }
        
    except Exception as e:
        logger.error(f"Error creating organization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create organization: {str(e)}"
        )

@router.get("/{org_id}", response_model=dict)
async def get_organization(
    org_id: str
):
    """Get organization profile by ID."""
    try:
        # For now, return 404 since we don't have a real organization database
        # TODO: Implement actual organization retrieval from database
        
        logger.info(f"Organization requested: {org_id}")
        
        raise HTTPException(
            status_code=404, 
            detail="Organization not found. Please create an organization first."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get organization: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{org_id}/assets", response_model=List[Dict[str, str]])
async def get_organization_assets(
    org_id: str
):
    """Get organization assets."""
    try:
        # For now, return empty list since we don't have a real backend
        # TODO: Implement actual asset retrieval from database
        
        logger.info(f"Assets requested for organization: {org_id}")
        
        return []
        
    except Exception as e:
        logger.error(f"Error fetching assets for organization {org_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organization assets: {str(e)}"
        )

@router.get("/{org_id}/threats", response_model=List[Dict[str, str]])
async def get_organization_threats(
    org_id: str
):
    """Get organization threat profile."""
    try:
        # For now, return empty list since we don't have a real backend
        # TODO: Implement actual threat profile retrieval from database
        
        logger.info(f"Threat profile requested for organization: {org_id}")
        
        return []
        
    except Exception as e:
        logger.error(f"Error fetching threats for organization {org_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch organization threats: {str(e)}"
        )

@router.get("/{org_id}/regulatory-context", response_model=Dict[str, Any])
async def get_regulatory_context(
    org_id: str
):
    """Get organization regulatory context."""
    try:
        # For now, return placeholder data
        # TODO: Implement actual regulatory context retrieval
        
        logger.info(f"Regulatory context requested for organization: {org_id}")
        
        return {
            "frameworks": [],
            "pressure": "medium",
            "audit_frequency": "annual",
            "penalties_exposure": "medium",
            "certifications": []
        }
        
    except Exception as e:
        logger.error(f"Error fetching regulatory context for organization {org_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch regulatory context: {str(e)}"
        )

@router.get("/{org_id}/governance-context", response_model=Dict[str, Any])
async def get_governance_context(
    org_id: str
):
    """Get organization governance context."""
    try:
        # For now, return placeholder data
        # TODO: Implement actual governance context retrieval
        
        logger.info(f"Governance context requested for organization: {org_id}")
        
        return {
            "maturity": {"strategic": "developing", "risk": "developing", "compliance": "developing"},
            "board_composition": {},
            "reporting_structure": {},
            "transformation_stage": "evolving"
        }
        
    except Exception as e:
        logger.error(f"Error fetching governance context for organization {org_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch governance context: {str(e)}"
        )

@router.get("/", response_model=List[Dict[str, Any]])
async def list_organizations():
    """List all organizations (admin only)."""
    try:
        # For now, return empty list since we don't have a real backend
        # TODO: Implement actual organization listing from database
        
        logger.info("Organization list requested")
        
        return []
        
    except Exception as e:
        logger.error(f"Error listing organizations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list organizations: {str(e)}"
        )

@router.delete("/{org_id}", response_model=dict)
async def delete_organization(
    org_id: str
):
    """Delete an organization."""
    try:
        # For now, just return success message
        # TODO: Implement actual organization deletion from database
        
        logger.info(f"Organization deletion requested: {org_id}")
        
        return {"message": f"Organization {org_id} deletion requested (not implemented yet)"}
        
    except Exception as e:
        logger.error(f"Error deleting organization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete organization: {str(e)}"
        ) 