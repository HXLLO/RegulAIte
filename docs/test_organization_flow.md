# Organization Flow Test Guide

## New Organization Flow

The organization section now has two pages:

1. **Organization Overview** (`/organization`) - Shows existing organization or setup prompt
2. **Organization Setup** (`/organization/setup`) - Configuration wizard

## Testing the Complete Flow

### Step 1: Access Organization Overview
1. Navigate to `http://localhost:3000/organization`
2. If no organization exists, you'll see:
   - Welcome message
   - "No Organization Configured" card
   - "Set Up Organization" button
   - Quick overview of what will be configured

### Step 2: First Time Setup
1. Click "Set Up Organization" button
2. Complete the 4-step wizard:
   - Basic Information
   - Operational Context  
   - Risk & Governance
   - Compliance & Preferences
3. Click "Complete Setup"
4. Success message appears
5. Automatically redirects to `/organization` (overview page)

### Step 3: View Organization Overview
After setup, the overview page shows:
- **Header**: Organization name with type/sector/size badges
- **Stats Cards**: Employees, Revenue, Risk Appetite, Compliance Status
- **Detail Cards**: 
  - Basic Information
  - Operational Context
  - Risk & Governance  
  - Compliance & Preferences
- **Quick Actions**: Edit Profile, Risk Assessment, Compliance Check, Generate Report

### Step 4: Edit Existing Organization
1. From overview page, click "Edit Configuration" button
2. Setup wizard opens in edit mode with pre-filled data
3. Page title shows "Edit Organization Configuration"
4. Final button shows "Update Profile" instead of "Complete Setup"
5. After updating, redirects back to overview page

## Key Features

### Navigation Flow
- Navbar "Organization" link → Overview page (`/organization`)
- Overview page "Set Up Organization" → Setup page (`/organization/setup`)
- Overview page "Edit Configuration" → Setup page in edit mode
- Both setup flows redirect back to overview after completion

### Data Persistence
- **Test Mode**: Saves to localStorage
- **Production**: Uses API endpoints (create/update organization profile)
- **Fallback**: If API fails, falls back to localStorage with warning

### UI Indicators
- **Setup Mode**: "Organization Configuration" / "Complete Setup"
- **Edit Mode**: "Edit Organization Configuration" / "Update Profile"
- **Loading States**: Different text for setup vs update operations
- **Compliance Status**: Visual indicators for framework configuration

## Test Data Flow

1. **No Organization**: Shows setup prompt
2. **Create Organization**: Wizard saves to localStorage/API
3. **View Organization**: Overview loads from localStorage/API
4. **Edit Organization**: Wizard pre-fills from existing data
5. **Update Organization**: Saves changes and returns to overview

## Browser Testing

### localStorage Inspection
```javascript
// View saved organization data
console.log(JSON.parse(localStorage.getItem('organization_profile')));

// Clear organization data (to test fresh setup)
localStorage.removeItem('organization_profile');
```

### Navigation Testing
- Direct URL access: `/organization` and `/organization/setup`
- Navigation bar link behavior
- Back/forward browser buttons
- Refresh page behavior

## Sample Test Organization

```json
{
  "organization_id": "tech-company-1234567890",
  "name": "Tech Company Inc",
  "organization_type": "technology",
  "sector": "technology",
  "size": "medium",
  "employee_count": 250,
  "annual_revenue": "10M-100M",
  "geographical_presence": ["europe", "north_america"],
  "business_model": "digital",
  "digital_maturity": "intermediate",
  "transformation_stage": "evolving",
  "risk_appetite": "moderate",
  "risk_tolerance": {
    "cyber": "medium",
    "operational": "medium", 
    "financial": "medium",
    "regulatory": "low"
  },
  "governance_maturity": {
    "strategic": "developing",
    "risk": "developing",
    "compliance": "developing"
  },
  "preferred_methodologies": ["iso27001", "rgpd", "nist"],
  "analysis_preferences": {
    "detail_level": "comprehensive",
    "reporting_frequency": "monthly",
    "focus_areas": ["security", "compliance", "risk"]
  }
}
```

This creates a complete organization management experience where users can view their organization first and only set up if needed! 