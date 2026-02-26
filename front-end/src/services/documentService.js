import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8090';

// Helper function to get auth header
const getAuthHeader = () => {
  const token = localStorage.getItem('token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Get document list with optional filtering
export const getDocuments = async (
  limit = 10,
  offset = 0,
  sortBy = 'created',
  sortOrder = 'desc',
  filters = {}
) => {
  try {
    const { fileType, category, language, tags, search } = filters;
    const params = {
      limit,
      offset,
      sort_by: sortBy,
      sort_order: sortOrder,
      ...(fileType && { file_type: fileType }),
      ...(category && { category }),
      ...(language && { language }),
      ...(tags && { tags }),
      ...(search && { search }),
    };

    const response = await axios.get(`${API_URL}/documents`, {
      headers: getAuthHeader(),
      params,
    });
    
    // The backend now returns an object with documents and pagination metadata
    const data = response.data;
    
    // Handle both old format (array) and new format (object with documents)
    if (Array.isArray(data)) {
      // Fallback for old format - this shouldn't happen with updated backend
      return {
        documents: data,
        total_count: data.length
      };
    } else {
      // New format with proper pagination
      return {
        documents: data.documents || [],
        total_count: data.total_count || 0,
        limit: data.limit || limit,
        offset: data.offset || offset
      };
    }
  } catch (error) {
    throw error;
  }
};

// Get a single document by ID
export const getDocument = async (docId, includeChunks = false, includeEntities = false) => {
  try {
    const params = {
      include_chunks: includeChunks,
      include_entities: includeEntities,
    };

    const response = await axios.get(`${API_URL}/documents/${docId}`, {
      headers: getAuthHeader(),
      params,
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Upload and process a document
export const uploadDocument = async (
  file,
  metadata = {},
  options = {
    useNlp: true,
    detectLanguage: true,
    language: null,
    useQueue: false,
    parserType: 'unstructured',
    extractImages: false,
    parserSettings: null
  }
) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    if (metadata) {
      formData.append('metadata', JSON.stringify(metadata));
    }
    
    formData.append('use_nlp', options.useNlp.toString());
    formData.append('detect_language', options.detectLanguage.toString());
    
    if (options.language) {
      formData.append('language', options.language);
    }
    
    formData.append('use_queue', options.useQueue.toString());
    
    // Add parser type
    formData.append('parser_type', options.parserType);
    
    // Add parser settings if provided
    if (options.parserSettings) {
      formData.append('parser_settings', JSON.stringify(options.parserSettings));
    }

    const response = await axios.post(`${API_URL}/documents/process`, formData, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Delete a document
export const deleteDocument = async (docId, deleteFromIndex = true) => {
  try {
    const params = {
      delete_from_index: deleteFromIndex,
    };

    const response = await axios.delete(`${API_URL}/documents/${docId}`, {
      headers: getAuthHeader(),
      params,
    });
    return response.data;
  } catch (error) {
    console.error('Error deleting document:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
    throw error;
  }
};

// Search documents
export const searchDocuments = async (query, options = {}) => {
  try {
    const { limit = 10, offset = 0, filters = null, dateRange = null, hybridSearch = true } = options;
    
    const searchParams = {
      query,
      limit,
      offset,
      filters,
      date_range: dateRange,
      hybrid_search: hybridSearch,
    };

    const response = await axios.post(`${API_URL}/documents/search`, searchParams, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Get document statistics
export const getDocumentStats = async () => {
  try {
    const response = await axios.get(`${API_URL}/documents/stats`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Get document configuration
export const getDocumentConfig = async () => {
  try {
    const response = await axios.get(`${API_URL}/documents/config`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Update document configuration
export const updateDocumentConfig = async (configUpdates) => {
  try {
    const response = await axios.post(`${API_URL}/documents/config`, configUpdates, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
};

// Get available parser types
export const getParserTypes = async () => {
  try {
    const response = await axios.get(`${API_URL}/documents/parsers`, {
      headers: getAuthHeader(),
    });
    return response.data;
  } catch (error) {
    // If the endpoint doesn't exist, return default parsers
    return {
      parsers: [
        { id: 'unstructured', name: 'Unstructured', description: 'Default document parser' },
        { id: 'unstructured_cloud', name: 'Unstructured Cloud', description: 'Cloud-based parser with enhanced capabilities' },
        { id: 'doctly', name: 'Doctly', description: 'Specialized for legal and regulatory documents' },
        { id: 'llamaparse', name: 'LlamaParse', description: 'AI-powered document parser based on LlamaIndex' },
      ]
    };
  }
};

// Explicitly index a document in the vector store
export const indexDocument = async (docId, forceReindex = false) => {
  try {
    const response = await axios.post(
      `${API_URL}/documents/index/${docId}`,
      { force_reindex: forceReindex },
      {
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error indexing document:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
    throw error;
  }
};

// Reindex all documents that need indexing
export const reindexAllDocuments = async (force = false) => {
  try {
    const response = await axios.post(
      `${API_URL}/documents/reindex-all`,
      { force_reindex: force },
      {
        headers: {
          ...getAuthHeader(),
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error reindexing all documents:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
    throw error;
  }
};

// Repair document metadata
export const repairDocumentMetadata = async (docId = null) => {
  try {
    const url = `${API_URL}/documents/repair-metadata`;
    const params = docId ? { doc_id: docId } : {};
    
    const response = await axios.post(url, {}, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      },
      params: params,
    });
    return response.data;
  } catch (error) {
    console.error('Error repairing document metadata:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
    throw error;
  }
};

// Repair document sizes
export const repairDocumentSizes = async () => {
  try {
    const url = `${API_URL}/documents/repair-sizes`;
    
    const response = await axios.post(url, {}, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error repairing document sizes:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
    throw error;
  }
};

// Repair document file types
export const repairDocumentFileTypes = async () => {
  try {
    const url = `${API_URL}/documents/repair-file-types`;
    
    const response = await axios.post(url, {}, {
      headers: {
        ...getAuthHeader(),
        'Content-Type': 'application/json',
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error repairing document file types:', error);
    if (error.response) {
      console.error('Response data:', error.response.data);
      console.error('Response status:', error.response.status);
    }
    throw error;
  }
}; 