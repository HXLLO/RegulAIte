import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8090';

// Get authentication header
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// Create a new organization profile
export const createOrganizationProfile = async (organizationData) => {
  try {
    const response = await axios.post(`${API_URL}/organizations`, organizationData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error creating organization profile:', error);
    throw error;
  }
};

// Get organization profile by ID
export const getOrganizationProfile = async (orgId) => {
  try {
    const response = await axios.get(`${API_URL}/organizations/${orgId}`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching organization profile:', error);
    throw error;
  }
};

// Update organization profile
export const updateOrganizationProfile = async (orgId, updateData) => {
  try {
    const response = await axios.put(`${API_URL}/organizations/${orgId}`, updateData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error updating organization profile:', error);
    throw error;
  }
};

// Get organization assets
export const getOrganizationAssets = async (orgId, scope = null) => {
  try {
    const params = scope ? { scope } : {};
    const response = await axios.get(`${API_URL}/organizations/${orgId}/assets`, {
      headers: getAuthHeader(),
      params,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching organization assets:', error);
    throw error;
  }
};

// Get organization threat landscape
export const getOrganizationThreats = async (orgId) => {
  try {
    const response = await axios.get(`${API_URL}/organizations/${orgId}/threats`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching organization threats:', error);
    throw error;
  }
};

// Get regulatory context
export const getRegulatoryContext = async (orgId) => {
  try {
    const response = await axios.get(`${API_URL}/organizations/${orgId}/regulatory-context`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching regulatory context:', error);
    throw error;
  }
};

// Get governance context
export const getGovernanceContext = async (orgId) => {
  try {
    const response = await axios.get(`${API_URL}/organizations/${orgId}/governance-context`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching governance context:', error);
    throw error;
  }
};

// Get all organizations (for admin users)
export const getAllOrganizations = async () => {
  try {
    const response = await axios.get(`${API_URL}/organizations`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching organizations:', error);
    throw error;
  }
};

// Delete organization
export const deleteOrganization = async (orgId) => {
  try {
    const response = await axios.delete(`${API_URL}/organizations/${orgId}`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error('Error deleting organization:', error);
    throw error;
  }
};

// Get organization configuration templates
export const getOrganizationTemplates = async () => {
  try {
    const response = await axios.get(`${API_URL}/organizations/templates`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching organization templates:', error);
    throw error;
  }
};

// Validate organization configuration
export const validateOrganizationConfig = async (configData) => {
  try {
    const response = await axios.post(`${API_URL}/organizations/validate`, configData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error validating organization config:', error);
    throw error;
  }
};

// Export default object with all functions
export default {
  createOrganizationProfile,
  getOrganizationProfile,
  updateOrganizationProfile,
  getOrganizationAssets,
  getOrganizationThreats,
  getRegulatoryContext,
  getGovernanceContext,
  getAllOrganizations,
  deleteOrganization,
  getOrganizationTemplates,
  validateOrganizationConfig,
}; 