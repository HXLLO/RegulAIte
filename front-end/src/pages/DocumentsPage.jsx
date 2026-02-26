import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  Flex, 
  Grid, 
  Heading, 
  Input, 
  Text, 
  useToast,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  Badge,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Select,
  FormControl,
  FormLabel,
  Spinner,
  Tag,
  TagLabel,
  HStack,
  Tooltip,
  Divider,
  ButtonGroup
} from '@chakra-ui/react';
import { FiUpload, FiSearch, FiFilter, FiMoreVertical, FiFile, FiTrash2, FiDownload, FiInfo } from 'react-icons/fi';
import { getDocuments, uploadDocument, deleteDocument, getDocumentStats, getParserTypes, repairDocumentMetadata, repairDocumentSizes, repairDocumentFileTypes } from '../services/documentService';

const DocumentsPage = () => {
  const toast = useToast();
  const { isOpen: isUploadOpen, onOpen: onUploadOpen, onClose: onUploadClose } = useDisclosure();
  const { isOpen: isFilterOpen, onOpen: onFilterOpen, onClose: onFilterClose } = useDisclosure();
  const { isOpen: isDetailOpen, onOpen: onDetailOpen, onClose: onDetailClose } = useDisclosure();
  
  const [documents, setDocuments] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [parsers, setParsers] = useState([]);
  const [filters, setFilters] = useState({
    fileType: '',
    category: '',
    language: ''
  });
  const [pagination, setPagination] = useState({
    limit: 10,
    offset: 0,
    totalCount: 0
  });
  const [file, setFile] = useState(null);
  const [metadata, setMetadata] = useState({
    title: '',
    author: '',
    category: '',
    tags: ''
  });
  const [processingOptions, setProcessingOptions] = useState({
    useNlp: true,
    detectLanguage: true,
    parserType: 'unstructured',
    useQueue: false,
    extractImages: false,
    chunkingStrategy: 'fixed',
    chunkSize: 1000,
    chunkOverlap: 200
  });

  // Available chunking strategies
  const chunkingStrategies = [
    { value: 'fixed', label: 'Fixed Size', description: 'Split by fixed character count with natural breaks at sentences' },
    { value: 'recursive', label: 'Recursive', description: 'Recursively split by paragraphs and other structural elements' },
    { value: 'semantic', label: 'Semantic', description: 'Split based on semantic boundaries and section markers' },
    { value: 'hierarchical', label: 'Hierarchical', description: 'Maintain document hierarchy with parent-child relationships' },
    { value: 'token', label: 'Token', description: 'Split by token count rather than character count (better for LLMs)' }
  ];

  // Load documents, stats, and parser types on mount
  useEffect(() => {
    fetchDocuments();
    fetchStats();
    fetchParserTypes();
  }, [pagination.offset, filters]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const { limit, offset } = pagination;
      const result = await getDocuments(limit, offset, 'created', 'desc', {
        fileType: filters.fileType,
        category: filters.category,
        language: filters.language,
        search: searchTerm
      });
      
      console.log('Documents API Response:', result);
      console.log('Documents Array:', result.documents || result);
      
      setDocuments(result.documents || []);
      setPagination(prev => ({
        ...prev,
        totalCount: result.total_count || 0
      }));
    } catch (error) {
      console.error('Error fetching documents:', error);
      toast({
        title: 'Error fetching documents',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const result = await getDocumentStats();
      console.log('Stats API Response:', result);
      setStats(result);
    } catch (error) {
      console.error('Error fetching document stats:', error);
    }
  };

  const fetchParserTypes = async () => {
    try {
      const result = await getParserTypes();
      setParsers(result.parsers || []);
    } catch (error) {
      console.error('Error fetching parser types:', error);
      // Default parsers in case API call fails
      setParsers([
        { id: 'unstructured', name: 'Unstructured', description: 'Default document parser' },
        { id: 'unstructured_cloud', name: 'Unstructured Cloud', description: 'Cloud-based parser with enhanced capabilities' },
        { id: 'doctly', name: 'Doctly', description: 'Specialized for legal and regulatory documents' },
        { id: 'llamaparse', name: 'LlamaParse', description: 'AI-powered document parser based on LlamaIndex' },
      ]);
    }
  };

  const handleSearch = () => {
    setPagination(prev => ({ ...prev, offset: 0 }));
    fetchDocuments();
  };

  const handleFileChange = (e) => {
    if (e.target.files[0]) {
      setFile(e.target.files[0]);
      
      // Try to auto-fill title from filename
      const fileName = e.target.files[0].name;
      setMetadata(prev => ({
        ...prev,
        title: fileName.split('.')[0].replace(/_/g, ' ')
      }));
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast({
        title: 'No file selected',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setUploadLoading(true);

    try {
      // Prepare tags array
      const tagsArray = metadata.tags
        ? metadata.tags.split(',').map(tag => tag.trim()).filter(Boolean)
        : [];

      // Add metadata to the form data
      const metadataToSend = {
        ...metadata,
        tags: tagsArray,
      };

      // Process document with selected options
      const response = await uploadDocument(
        file,
        metadataToSend,
        {
          useNlp: processingOptions.useNlp,
          detectLanguage: processingOptions.detectLanguage,
          parserType: processingOptions.parserType,
          useQueue: processingOptions.useQueue,
          extractImages: processingOptions.extractImages,
          parserSettings: {
            chunking_strategy: processingOptions.chunkingStrategy,
            chunk_size: processingOptions.chunkSize,
            chunk_overlap: processingOptions.chunkOverlap,
            extract_images: processingOptions.extractImages
          }
        }
      );

      // Handle successful upload
      toast({
        title: 'Document uploaded successfully',
        description: response.message || 'Your document is being processed',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      // Reset form
      setFile(null);
      setMetadata({
        title: '',
        author: '',
        category: '',
        tags: ''
      });
      onUploadClose();

      // Refresh document list with multiple retries to ensure the document is indexed
      const refreshWithRetry = async (retries = 3, delay = 2000) => {
        try {
          await fetchDocuments();
          await fetchStats();
        } catch (error) {
          console.error('Error refreshing documents:', error);
          if (retries > 0) {
            // Wait and retry
            setTimeout(() => refreshWithRetry(retries - 1, delay), delay);
          }
        }
      };

      // Initial refresh after a short delay
      setTimeout(() => refreshWithRetry(), 2000);
      
      // Second refresh after a longer delay to catch late indexing
      setTimeout(() => refreshWithRetry(), 7000);

    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: 'Upload failed',
        description: error.message || 'Failed to upload document',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setUploadLoading(false);
    }
  };

  const handleDelete = async (docId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await deleteDocument(docId);
        
        toast({
          title: 'Document deleted',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        
        // Refresh document list and stats
        fetchDocuments();
        fetchStats();
      } catch (error) {
        toast({
          title: 'Error deleting document',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    }
  };

  const handleDocumentClick = (doc) => {
    setSelectedDoc(doc);
    onDetailOpen();
  };

  const handleNextPage = () => {
    if (pagination.offset + pagination.limit < pagination.totalCount) {
      setPagination(prev => ({
        ...prev,
        offset: prev.offset + prev.limit
      }));
    }
  };

  const handlePrevPage = () => {
    if (pagination.offset > 0) {
      setPagination(prev => ({
        ...prev,
        offset: Math.max(0, prev.offset - prev.limit)
      }));
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleString();
  };

  const getFileIcon = (fileType) => {
    switch (fileType?.toLowerCase()) {
      case 'pdf': return <FiFile />;
      case 'docx': return <FiFile />;
      case 'txt': return <FiFile />;
      default: return <FiFile />;
    }
  };

  const getFileTypeBadge = (fileType) => {
    let color = 'gray';
    
    switch (fileType?.toLowerCase()) {
      case 'pdf': color = 'red'; break;
      case 'docx': color = 'blue'; break;
      case 'txt': color = 'green'; break;
      case 'pptx': color = 'orange'; break;
      case 'xlsx': color = 'teal'; break;
      default: color = 'gray';
    }
    
    return (
      <Badge colorScheme={color} variant="solid" borderRadius="full" px={2}>
        {fileType?.toUpperCase() || 'UNKNOWN'}
      </Badge>
    );
  };

  // Get the current parser information for display
  const getSelectedParserInfo = () => {
    const parser = parsers.find(p => p.id === processingOptions.parserType);
    return parser || { name: 'Loading...', description: '' };
  };

  // The selected parser info
  const selectedParserInfo = getSelectedParserInfo();

  // Add the repair function
  const handleRepairMetadata = async () => {
    try {
      setLoading(true);
      await repairDocumentMetadata();
      toast({
        title: 'Metadata repair initiated',
        description: 'Document metadata is being repaired. This may take a moment.',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
      
      // Refresh document list after a delay
      setTimeout(() => {
        fetchDocuments();
        fetchStats();
      }, 1000);
    } catch (error) {
      console.error('Error repairing metadata:', error);
      toast({
        title: 'Error repairing metadata',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  // Add size repair function
  const handleRepairSizes = async () => {
    try {
      setLoading(true);
      await repairDocumentSizes();
      toast({
        title: 'Size repair initiated',
        description: 'Document sizes are being updated. This may take a moment.',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
      
      // Refresh document list after a delay
      setTimeout(() => {
        fetchDocuments();
        fetchStats();
      }, 1000);
    } catch (error) {
      console.error('Error repairing document sizes:', error);
      toast({
        title: 'Error repairing document sizes',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  // Add file type repair function
  const handleRepairFileTypes = async () => {
    try {
      setLoading(true);
      await repairDocumentFileTypes();
      toast({
        title: 'File type repair initiated',
        description: 'Document file types are being updated. This may take a moment.',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
      
      // Refresh document list after a delay
      setTimeout(() => {
        fetchDocuments();
        fetchStats();
      }, 1000);
    } catch (error) {
      console.error('Error repairing document file types:', error);
      toast({
        title: 'Error repairing document file types',
        description: error.message,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box p={5}>
      <Flex justifyContent="space-between" alignItems="center" mb={6}>
        <Heading size="lg">Document Management</Heading>
        <ButtonGroup spacing={2}>
          <Button 
            leftIcon={<FiUpload />} 
            colorScheme="purple" 
            bg="#4415b6"
            onClick={onUploadOpen}
          >
            Upload Document
          </Button>
        </ButtonGroup>
      </Flex>

      {/* Stats Cards */}
      {stats && (
        <Grid templateColumns={{ base: "repeat(1, 1fr)", md: "repeat(4, 1fr)" }} gap={4} mb={6}>
          <Box p={4} borderRadius="md" boxShadow="sm" bg="white">
            <Text fontSize="sm" color="gray.500">Total Documents</Text>
            <Text fontSize="2xl" fontWeight="bold">{stats.total_documents}</Text>
          </Box>
          <Box p={4} borderRadius="md" boxShadow="sm" bg="white">
            <Text fontSize="sm" color="gray.500">Total Chunks</Text>
            <Text fontSize="2xl" fontWeight="bold">{stats.total_chunks}</Text>
          </Box>
          <Box p={4} borderRadius="md" boxShadow="sm" bg="white">
            <Text fontSize="sm" color="gray.500">Storage Used</Text>
            <Text fontSize="2xl" fontWeight="bold">{stats.total_storage_mb.toFixed(2)} MB</Text>
          </Box>
          <Box p={4} borderRadius="md" boxShadow="sm" bg="white">
            <Text fontSize="sm" color="gray.500">Document Types</Text>
            <Text fontSize="2xl" fontWeight="bold">{Object.keys(stats.documents_by_type).length}</Text>
          </Box>
        </Grid>
      )}

      {/* Search and Filter */}
      <Flex mb={6} gap={2} flexDir={{ base: "column", md: "row" }}>
        <Flex flex="1">
          <Input
            placeholder="Search documents..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <Button 
            leftIcon={<FiSearch />} 
            ml={2} 
            onClick={handleSearch}
          >
            Search
          </Button>
        </Flex>
        <Button leftIcon={<FiFilter />} onClick={onFilterOpen}>
          Filters
        </Button>
      </Flex>

      {/* Document Table */}
      {loading ? (
        <Flex justify="center" align="center" height="200px">
          <Spinner size="xl" color="#4415b6" />
        </Flex>
      ) : (
        <>
          <Box overflowX="auto">
            <Table variant="simple">
              <Thead>
                <Tr>
                  <Th>Document</Th>
                  <Th>Type</Th>
                  <Th>Date Uploaded</Th>
                  <Th>Size</Th>
                  <Th>Category</Th>
                  <Th>Actions</Th>
                </Tr>
              </Thead>
              <Tbody>
                {documents.length > 0 ? (
                  documents.map((doc) => (
                    <Tr 
                      key={doc.doc_id} 
                      _hover={{ bg: "gray.50", cursor: "pointer" }}
                      onClick={() => handleDocumentClick(doc)}
                    >
                      <Td>
                        <Flex align="center">
                          {getFileIcon(doc.file_type)}
                          <Text ml={2} fontWeight="medium">{doc.name || doc.title}</Text>
                        </Flex>
                      </Td>
                      <Td>{getFileTypeBadge(doc.file_type)}</Td>
                      <Td>{formatDate(doc.created_at)}</Td>
                      <Td>{(doc.size / 1024).toFixed(2)} KB</Td>
                      <Td>{doc.category || 'Uncategorized'}</Td>
                      <Td onClick={(e) => e.stopPropagation()}>
                        <Menu>
                          <MenuButton
                            as={IconButton}
                            icon={<FiMoreVertical />}
                            variant="ghost"
                            size="sm"
                          />
                          <MenuList>
                            <MenuItem icon={<FiInfo />} onClick={() => handleDocumentClick(doc)}>
                              View Details
                            </MenuItem>
                            <MenuItem icon={<FiDownload />}>
                              Download
                            </MenuItem>
                            <MenuItem 
                              icon={<FiTrash2 />} 
                              color="red.500"
                              onClick={() => handleDelete(doc.doc_id)}
                            >
                              Delete
                            </MenuItem>
                          </MenuList>
                        </Menu>
                      </Td>
                    </Tr>
                  ))
                ) : (
                  <Tr>
                    <Td colSpan={6} textAlign="center" py={10}>
                      <Text fontSize="lg" color="gray.500">No documents found</Text>
                      <Text fontSize="sm" color="gray.400" mt={2}>Upload a document to get started</Text>
                      <Button 
                        leftIcon={<FiUpload />} 
                        colorScheme="purple" 
                        bg="#4415b6"
                        mt={4}
                        onClick={onUploadOpen}
                      >
                        Upload Document
                      </Button>
                    </Td>
                  </Tr>
                )}
              </Tbody>
            </Table>
          </Box>

          {/* Pagination */}
          {documents.length > 0 && (
            <Flex justify="space-between" mt={4} align="center">
              <Text color="gray.500">
                Showing {pagination.offset + 1} to {Math.min(pagination.offset + documents.length, pagination.totalCount)} of {pagination.totalCount} documents
              </Text>
              <Flex>
                <Button 
                  onClick={handlePrevPage} 
                  isDisabled={pagination.offset === 0}
                  mr={2}
                  size="sm"
                >
                  Previous
                </Button>
                <Button 
                  onClick={handleNextPage} 
                  isDisabled={pagination.offset + pagination.limit >= pagination.totalCount}
                  size="sm"
                >
                  Next
                </Button>
              </Flex>
            </Flex>
          )}
        </>
      )}

      {/* Upload Modal */}
      <Modal isOpen={isUploadOpen} onClose={onUploadClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Upload Document</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl mb={4}>
              <FormLabel>Select File</FormLabel>
              <Input
                type="file"
                onChange={handleFileChange}
                p={1}
              />
              {file && (
                <Text fontSize="sm" mt={1} color="gray.500">
                  Selected: {file.name} ({(file.size / 1024).toFixed(2)} KB)
                </Text>
              )}
            </FormControl>

            <FormControl mb={4}>
              <FormLabel>Title</FormLabel>
              <Input
                value={metadata.title}
                onChange={(e) => setMetadata({ ...metadata, title: e.target.value })}
                placeholder="Document title"
              />
            </FormControl>

            <FormControl mb={4}>
              <FormLabel>Author</FormLabel>
              <Input
                value={metadata.author}
                onChange={(e) => setMetadata({ ...metadata, author: e.target.value })}
                placeholder="Document author"
              />
            </FormControl>

            <FormControl mb={4}>
              <FormLabel>Category</FormLabel>
              <Input
                value={metadata.category}
                onChange={(e) => setMetadata({ ...metadata, category: e.target.value })}
                placeholder="Document category"
              />
            </FormControl>

            <FormControl mb={4}>
              <FormLabel>Tags (comma separated)</FormLabel>
              <Input
                value={metadata.tags}
                onChange={(e) => setMetadata({ ...metadata, tags: e.target.value })}
                placeholder="tag1, tag2, tag3"
              />
            </FormControl>

            <Divider my={4} />
            <Heading size="sm" mb={3}>Processing Options</Heading>
            
            <FormControl mb={4}>
              <FormLabel display="flex" alignItems="center">
                Parser Type
                <Tooltip 
                  label="Select the document parser to use for processing. Different parsers may have different capabilities."
                  placement="top"
                >
                  <Box as="span" ml={1} color="gray.500" cursor="help">
                    <FiInfo size={14} />
                  </Box>
                </Tooltip>
              </FormLabel>
              <Select
                value={processingOptions.parserType}
                onChange={(e) => setProcessingOptions(prev => ({ 
                  ...prev, 
                  parserType: e.target.value 
                }))}
              >
                {parsers.map(parser => (
                  <option key={parser.id} value={parser.id}>
                    {parser.name}
                  </option>
                ))}
              </Select>
              {selectedParserInfo.description && (
                <Text fontSize="sm" mt={1} color="gray.500">
                  {selectedParserInfo.description}
                </Text>
              )}
            </FormControl>
            
            <FormControl mb={4}>
              <FormLabel display="flex" alignItems="center">
                Chunking Strategy
                <Tooltip 
                  label="Select how documents will be split into chunks for processing and retrieval"
                  placement="top"
                >
                  <Box as="span" ml={1} color="gray.500" cursor="help">
                    <FiInfo size={14} />
                  </Box>
                </Tooltip>
              </FormLabel>
              <Select
                value={processingOptions.chunkingStrategy}
                onChange={(e) => setProcessingOptions(prev => ({ 
                  ...prev, 
                  chunkingStrategy: e.target.value 
                }))}
              >
                {chunkingStrategies.map(strategy => (
                  <option key={strategy.value} value={strategy.value}>
                    {strategy.label}
                  </option>
                ))}
              </Select>
              {chunkingStrategies.find(s => s.value === processingOptions.chunkingStrategy)?.description && (
                <Text fontSize="sm" mt={1} color="gray.500">
                  {chunkingStrategies.find(s => s.value === processingOptions.chunkingStrategy)?.description}
                </Text>
              )}
            </FormControl>
            
            <Grid templateColumns="repeat(2, 1fr)" gap={4}>
              <FormControl mb={4}>
                <FormLabel display="flex" alignItems="center">
                  Chunk Size
                  <Tooltip 
                    label="Maximum size of each chunk in characters (or tokens for Token strategy)"
                    placement="top"
                  >
                    <Box as="span" ml={1} color="gray.500" cursor="help">
                      <FiInfo size={14} />
                    </Box>
                  </Tooltip>
                </FormLabel>
                <Input
                  type="number"
                  value={processingOptions.chunkSize}
                  onChange={(e) => setProcessingOptions(prev => ({ 
                    ...prev, 
                    chunkSize: parseInt(e.target.value) 
                  }))}
                  min={100}
                  max={10000}
                />
              </FormControl>
              
              <FormControl mb={4}>
                <FormLabel display="flex" alignItems="center">
                  Chunk Overlap
                  <Tooltip 
                    label="Number of characters (or tokens) to overlap between chunks"
                    placement="top"
                  >
                    <Box as="span" ml={1} color="gray.500" cursor="help">
                      <FiInfo size={14} />
                    </Box>
                  </Tooltip>
                </FormLabel>
                <Input
                  type="number"
                  value={processingOptions.chunkOverlap}
                  onChange={(e) => setProcessingOptions(prev => ({ 
                    ...prev, 
                    chunkOverlap: parseInt(e.target.value) 
                  }))}
                  min={0}
                  max={processingOptions.chunkSize / 2}
                />
              </FormControl>
            </Grid>

            <FormControl display="flex" alignItems="center" mb={2}>
              <FormLabel htmlFor="useNlp" mb="0">
                Use NLP Processing
                <Tooltip 
                  label="Extract entities and relationships from the document using natural language processing"
                  placement="top"
                >
                  <Box as="span" ml={1} color="gray.500" cursor="help">
                    <FiInfo size={14} />
                  </Box>
                </Tooltip>
              </FormLabel>
              <input
                type="checkbox"
                id="useNlp"
                checked={processingOptions.useNlp}
                onChange={() => setProcessingOptions(prev => ({ 
                  ...prev, 
                  useNlp: !prev.useNlp 
                }))}
              />
            </FormControl>

            <FormControl display="flex" alignItems="center" mb={2}>
              <FormLabel htmlFor="detectLanguage" mb="0">
                Auto-detect Language
                <Tooltip 
                  label="Automatically detect the document's language"
                  placement="top"
                >
                  <Box as="span" ml={1} color="gray.500" cursor="help">
                    <FiInfo size={14} />
                  </Box>
                </Tooltip>
              </FormLabel>
              <input
                type="checkbox"
                id="detectLanguage"
                checked={processingOptions.detectLanguage}
                onChange={() => setProcessingOptions(prev => ({ 
                  ...prev, 
                  detectLanguage: !prev.detectLanguage 
                }))}
              />
            </FormControl>

            <FormControl display="flex" alignItems="center" mb={2}>
              <FormLabel htmlFor="useQueue" mb="0">
                Use Queue Processing
                <Tooltip 
                  label="Process document in background queue for better performance with large files"
                  placement="top"
                >
                  <Box as="span" ml={1} color="gray.500" cursor="help">
                    <FiInfo size={14} />
                  </Box>
                </Tooltip>
              </FormLabel>
              <input
                type="checkbox"
                id="useQueue"
                checked={processingOptions.useQueue}
                onChange={() => setProcessingOptions(prev => ({ 
                  ...prev, 
                  useQueue: !prev.useQueue 
                }))}
              />
            </FormControl>

            <FormControl display="flex" alignItems="center" mb={2}>
              <FormLabel htmlFor="extractImages" mb="0">
                Extract Images
                <Tooltip 
                  label="Extract and save images from the document for later reference"
                  placement="top"
                >
                  <Box as="span" ml={1} color="gray.500" cursor="help">
                    <FiInfo size={14} />
                  </Box>
                </Tooltip>
              </FormLabel>
              <input
                type="checkbox"
                id="extractImages"
                checked={processingOptions.extractImages}
                onChange={() => setProcessingOptions(prev => ({ 
                  ...prev, 
                  extractImages: !prev.extractImages 
                }))}
              />
            </FormControl>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onUploadClose}>
              Cancel
            </Button>
            <Button 
              colorScheme="purple" 
              bg="#4415b6"
              onClick={handleUpload}
              isLoading={uploadLoading}
              loadingText="Uploading"
            >
              Upload
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Filter Modal */}
      <Modal isOpen={isFilterOpen} onClose={onFilterClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Filter Documents</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl mb={4}>
              <FormLabel>File Type</FormLabel>
              <Select
                placeholder="All Types"
                value={filters.fileType}
                onChange={(e) => setFilters({ ...filters, fileType: e.target.value })}
              >
                <option value="pdf">PDF</option>
                <option value="docx">DOCX</option>
                <option value="txt">TXT</option>
                <option value="pptx">PPTX</option>
                <option value="xlsx">XLSX</option>
              </Select>
            </FormControl>

            <FormControl mb={4}>
              <FormLabel>Category</FormLabel>
              <Input
                placeholder="Filter by category"
                value={filters.category}
                onChange={(e) => setFilters({ ...filters, category: e.target.value })}
              />
            </FormControl>

            <FormControl mb={4}>
              <FormLabel>Language</FormLabel>
              <Select
                placeholder="All Languages"
                value={filters.language}
                onChange={(e) => setFilters({ ...filters, language: e.target.value })}
              >
                <option value="french">French (Default)</option>
                <option value="english">English</option>
                <option value="spanish">Spanish</option>
                <option value="german">German</option>
                <option value="chinese">Chinese</option>
              </Select>
            </FormControl>
          </ModalBody>

          <ModalFooter>
            <Button 
              variant="outline" 
              mr={3} 
              onClick={() => {
                setFilters({
                  fileType: '',
                  category: '',
                  language: ''
                });
                onFilterClose();
              }}
            >
              Reset Filters
            </Button>
            <Button colorScheme="purple" bg="#4415b6" onClick={onFilterClose}>
              Apply Filters
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Document Detail Modal */}
      {selectedDoc && (
        <Modal isOpen={isDetailOpen} onClose={onDetailClose} size="xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>Document Details</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <Grid templateColumns="1fr 1fr" gap={4}>
                <Box>
                  <Text fontWeight="bold">Filename</Text>
                  <Text mb={3}>{selectedDoc.name || "Unknown"}</Text>
                  
                  <Text fontWeight="bold">Title</Text>
                  <Text mb={3}>{selectedDoc.title || "Untitled"}</Text>
                  
                  <Text fontWeight="bold">File Type</Text>
                  <Text mb={3}>{selectedDoc.file_type?.toUpperCase() || 'Unknown'}</Text>
                  
                  <Text fontWeight="bold">File Size</Text>
                  <Text mb={3}>{(selectedDoc.size / 1024).toFixed(2)} KB</Text>
                  
                  <Text fontWeight="bold">Uploaded</Text>
                  <Text mb={3}>{formatDate(selectedDoc.created_at)}</Text>
                </Box>
                
                <Box>
                  <Text fontWeight="bold">Author</Text>
                  <Text mb={3}>{selectedDoc.author || 'N/A'}</Text>
                  
                  <Text fontWeight="bold">Category</Text>
                  <Text mb={3}>{selectedDoc.category || 'Uncategorized'}</Text>
                  
                  <Text fontWeight="bold">Language</Text>
                  <Text mb={3}>{selectedDoc.language || 'Unknown'}</Text>
                  
                  <Text fontWeight="bold">Tags</Text>
                  <HStack spacing={2} mb={3}>
                    {selectedDoc.tags && selectedDoc.tags.length > 0 ? (
                      selectedDoc.tags.map((tag, index) => (
                        <Tag
                          key={index}
                          size="sm"
                          borderRadius="full"
                          variant="solid"
                          colorScheme="purple"
                        >
                          <TagLabel>{tag}</TagLabel>
                        </Tag>
                      ))
                    ) : (
                      <Text color="gray.500">No tags</Text>
                    )}
                  </HStack>
                </Box>
              </Grid>
              
              <Box mt={4}>
                <Text fontWeight="bold" mb={2}>Processing Information</Text>
                <Grid templateColumns="1fr 1fr" gap={4}>
                  <Box>
                    <Text fontSize="sm">Chunks: {selectedDoc.chunk_count || 0}</Text>
                    <Text fontSize="sm">Entities: {selectedDoc.entity_count || 0}</Text>
                    {selectedDoc.parser_type && (
                      <Text fontSize="sm">Parser: {selectedDoc.parser_type}</Text>
                    )}
                  </Box>
                  <Box>
                    <Text fontSize="sm">Indexed: {selectedDoc.is_indexed ? 'Yes' : 'No'}</Text>
                    <Text fontSize="sm">Processing Status: {selectedDoc.processing_status || 'Complete'}</Text>
                  </Box>
                </Grid>
              </Box>
            </ModalBody>

            <ModalFooter>
              <Button 
                variant="outline" 
                colorScheme="red" 
                mr={3} 
                leftIcon={<FiTrash2 />}
                onClick={() => {
                  handleDelete(selectedDoc.doc_id);
                  onDetailClose();
                }}
              >
                Delete
              </Button>
              <Button 
                colorScheme="blue" 
                mr={3}
                leftIcon={<FiDownload />}
              >
                Download
              </Button>
              <Button variant="ghost" onClick={onDetailClose}>
                Close
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      )}
    </Box>
  );
};

export default DocumentsPage; 