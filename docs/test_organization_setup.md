# Organization Setup Page Test Guide

## How to Access the Organization Setup Page

### 1. Frontend Access
The React application should be running on `http://localhost:3000`

**Direct URL:** `http://localhost:3000/organization/setup`

**Via Navigation:** 
- Go to `http://localhost:3000`
- Click on "Organization" in the top navigation bar

### 2. Testing the Organization Setup

The page includes a 4-step wizard:

#### Step 1: Basic Information
- Organization Name (required)
- Organization Type (dropdown)
- Regulatory Sector (dropdown) 
- Organization Size (dropdown)
- Employee Count (number input)
- Annual Revenue (dropdown)

#### Step 2: Operational Context
- Business Model (dropdown)
- Digital Maturity (dropdown)
- Transformation Stage (dropdown)
- Geographical Presence (checkboxes)

#### Step 3: Risk & Governance
- Risk Appetite (dropdown)
- Risk Tolerance by Category (dropdowns for cyber, operational, financial, regulatory)
- Governance Maturity (dropdowns for strategic, risk, compliance)

#### Step 4: Compliance & Preferences
- Preferred Compliance Frameworks (checkboxes)
- Report Format (dropdown)
- Analysis Detail Level (dropdown)
- Analysis Focus Areas (checkboxes)

### 3. Test Mode Features

The application runs in test mode when:
- `NODE_ENV=development` (default for `npm start`)
- Backend is not available

**Test Mode Behavior:**
- Simulates 2-second API delay
- Shows success toast with "(Test Mode)" indicator
- Saves configuration to localStorage
- Redirects to dashboard after 2 seconds

### 4. Checking Test Results

After completing the setup, you can verify the saved data:

**Browser Console:**
```javascript
// View saved organization profile
console.log(JSON.parse(localStorage.getItem('organization_profile')));
```

**Browser DevTools:**
1. Open DevTools (F12)
2. Go to Application tab
3. Select Local Storage → http://localhost:3000
4. Look for `organization_profile` key

### 5. Sample Test Data

**Example Organization:**
- Name: "TechCorp Solutions"
- Type: "Technology"
- Sector: "Technology" 
- Size: "Medium"
- Employees: 250
- Revenue: "10M-100M"
- Geographical: ["Europe", "North America"]
- Frameworks: ["ISO 27001", "RGPD/GDPR"]

### 6. Troubleshooting

**If page doesn't load:**
- Check React server is running: `npm start` in front-end directory
- Verify URL: `http://localhost:3000/organization/setup`
- Check browser console for errors

**If navigation link missing:**
- Refresh the page
- Check if you're logged in (authentication required)

**If form submission fails:**
- Check browser console for errors
- Verify all required fields are filled
- Test mode should work even without backend

### 7. Backend API Testing (Optional)

If you want to test with actual backend:

**Start Backend:**
```bash
cd backend
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Test API Endpoints:**
```bash
# Get templates
curl -X GET "http://localhost:8000/organizations/templates"

# Create organization (requires JSON data)
curl -X POST "http://localhost:8000/organizations" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Corp", "organization_type": "technology"}'
```

The frontend will automatically detect if backend is available and switch between test mode and API mode accordingly. 