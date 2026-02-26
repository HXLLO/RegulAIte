# plugins/regul_aite/backend/unstructured_parser/document_parser.py
import os
import requests
import logging
import json
import uuid
from typing import Dict, List, Any, Optional, BinaryIO, Callable, Literal
from datetime import datetime as py_datetime  
import datetime  # Import the full module too
import tempfile
import time
import math
import re
import asyncio

# Import MetadataParser and DocumentChunk
from data_enrichment.metadata_parser import MetadataParser
from data_enrichment.document_chunk import DocumentChunk

# Import LangChain TokenTextSplitter with fallback
try:
    from langchain_text_splitters import TokenTextSplitter
    HAS_TOKEN_SPLITTER = True
except ImportError:
    HAS_TOKEN_SPLITTER = False
    logging.warning("langchain_text_splitters package not found. Token-based chunking will fall back to fixed size chunking.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Define chunking strategies
ChunkingStrategy = Literal["fixed", "recursive", "semantic", "hierarchical", "token"]

class DocumentParser:
    """
    Parser for documents using Unstructured API.
    
    This class is responsible only for parsing documents and extracting chunks.
    Storage operations are handled by the RAG system.
    """

    def __init__(
          self,
          unstructured_api_url: Optional[str] = None,
          unstructured_api_key: Optional[str] = None,
          embedding_dim: int = 384,  # Added embedding_dim
          chunk_size: int = 2048,
          chunk_overlap: int = 200,
          chunking_strategy: ChunkingStrategy = "token",
          extract_tables: bool = True,
          extract_metadata: bool = True,
          extract_images: bool = False,
          is_cloud: bool = False
      ):
      """
      Initialize the document parser.

      Args:
          unstructured_api_url: URL for Unstructured API (defaults to env var)
          unstructured_api_key: API key for Unstructured API (defaults to env var)
          embedding_dim: Dimension of the embeddings to be used for dummy vectors
          chunk_size: Maximum size of text chunks in characters
          chunk_overlap: Number of characters to overlap between chunks
          chunking_strategy: Strategy for chunking text ("fixed", "recursive", "semantic", "hierarchical", "token")
          extract_tables: Whether to extract tables from documents
          extract_metadata: Whether to extract detailed metadata
          extract_images: Whether to extract and process images
          is_cloud: Whether to use the cloud version of Unstructured API
      """
      self.is_cloud = is_cloud
      self.embedding_dim = embedding_dim # Store embedding_dim

      # Get Unstructured API credentials from environment if not provided
      if is_cloud:
          # Use cloud-specific environment variables
          self.unstructured_api_url = unstructured_api_url or os.getenv(
              "UNSTRUCTURED_CLOUD_API_URL", "https://api.unstructured.io/general/v0/general"
          )
          self.unstructured_api_key = unstructured_api_key or os.getenv(
              "UNSTRUCTURED_CLOUD_API_KEY", ""
          )
          if not self.unstructured_api_key:
              logger.warning("No API key provided for Unstructured Cloud API")
      else:
          # Use local-specific environment variables
          self.unstructured_api_url = unstructured_api_url or os.getenv(
              "UNSTRUCTURED_API_URL", "http://unstructured:8000/general/v0/general"
          )
          self.unstructured_api_key = unstructured_api_key or os.getenv(
              "UNSTRUCTURED_API_KEY", ""
          )

      # Chunking parameters
      self.chunk_size = chunk_size
      self.chunk_overlap = chunk_overlap
      self.chunking_strategy = chunking_strategy

      # Extraction options
      self.extract_tables = extract_tables
      self.extract_metadata = extract_metadata
      self.extract_images = extract_images

      # Initialize embedding model for generating embeddings in chunks
      try:
          from rag.embeddings_model import EmbeddingsModel
          self.embedding_model = EmbeddingsModel()
          logger.info("Successfully initialized EmbeddingsModel")
      except Exception as e:
          logger.error(f"Failed to initialize EmbeddingsModel: {e}")
          # Create a dummy embedding model
          class DummyEmbeddingModel:
              def get_text_embedding(self, text: str) -> List[float]:
                  return [0.0] * embedding_dim
          self.embedding_model = DummyEmbeddingModel()
          logger.warning("Using dummy embedding model. Document chunks won't have useful embeddings.")

      # Initialize metadata parser
      self.metadata_parser = MetadataParser()
      
      # Log initialization
      api_type = "cloud" if is_cloud else "local"
      logger.info(f"Initialized DocumentParser with {api_type} Unstructured API at {self.unstructured_api_url}")

    def _call_unstructured_api(self, file_content: bytes, file_name: str) -> List[Dict[str, Any]]:
      """
      Call the Unstructured API to extract text from a file.

      Args:
          file_content: Binary content of the file
          file_name: Name of the file

      Returns:
          List of elements extracted from the document
      """
      logger.info(f"Calling Unstructured API for document: {file_name}")

      # Create a temporary file to send to the API
      with tempfile.NamedTemporaryFile(delete=False) as temp_file:
          temp_file.write(file_content)
          temp_file_path = temp_file.name

      try:
          headers = {
              "Accept": "application/json",
              "unstructured-api-key": self.unstructured_api_key
          }

          with open(temp_file_path, "rb") as f:
              files = {"files": (file_name, f)}

              # Enhanced parameters for better extraction
              data = {
                  "strategy": "auto",
                  "ocr_enabled": "true",
                  "languages": "auto",  # Use languages instead of ocr_languages
                  "include_page_breaks": "true",  # Preserve page break information
                  "hierarchical_pdf": "true" if self.chunking_strategy == "hierarchical" else "false",
                  "extract_images": "true" if self.extract_images else "false",
                  "extract_tables": "true" if self.extract_tables else "false",
                  "include_metadata": "true" if self.extract_metadata else "false"
              }

              logger.info(f"Calling Unstructured API with parameters: {data}")

              try:
                  response = requests.post(
                      self.unstructured_api_url,
                      headers=headers,
                      files=files,
                      data=data,
                      timeout=300  # 5-minute timeout for large documents
                  )

                  if response.status_code != 200:
                      logger.error(f"Unstructured API error: {response.status_code} - {response.text}")
                      # Don't raise here, use fallback
                      return self._create_fallback_elements(file_name, file_content)

                  # Parse and return the response
                  try:
                      elements = response.json()
                      if not elements or len(elements) == 0:
                          logger.warning(f"Unstructured API returned empty elements list for {file_name}")
                          return self._create_fallback_elements(file_name, file_content)
                      
                      logger.info(f"Extracted {len(elements)} elements from document")

                      # Log element types to help with debugging
                      element_types = {}
                      text_count = 0
                      image_count = 0
                      for element in elements:
                          element_type = element.get("type", "unknown")
                          has_text = bool(element.get("text", "").strip())
                          if has_text:
                              text_count += 1
                              
                          if element_type == 'Image':
                              image_count += 1

                          if element_type in element_types:
                              element_types[element_type] += 1
                          else:
                              element_types[element_type] = 1
                              
                      logger.info(f"Element types: {element_types}, {text_count} with text, {image_count} images")
                      
                      # If no text elements, use fallback
                      if text_count == 0:
                          logger.warning(f"No text elements found in API response for {file_name}, using fallback")
                          return self._create_fallback_elements(file_name, file_content)
                      
                      # Return the parsed elements
                      return elements
                  except json.JSONDecodeError as je:
                      logger.error(f"Failed to parse Unstructured API response as JSON: {str(je)}")
                      logger.error(f"Response content: {response.text[:500]}...")
                      return self._create_fallback_elements(file_name, file_content)
              except requests.exceptions.RequestException as re:
                  logger.error(f"Request to Unstructured API failed: {str(re)}")
                  return self._create_fallback_elements(file_name, file_content)

      except Exception as e:
          logger.error(f"Error calling Unstructured API: {str(e)}", exc_info=True)
          return self._create_fallback_elements(file_name, file_content)
      finally:
          try:
              os.unlink(temp_file_path)
          except Exception as e:
              logger.warning(f"Failed to delete temp file: {str(e)}")

    def _create_fallback_elements(self, file_name: str, file_content: bytes) -> List[Dict[str, Any]]:
        """
        Create fallback document elements when the Unstructured API fails.
        
        Args:
            file_name: Name of the file
            file_content: Binary content of the file
            
        Returns:
            List with at least one element containing basic file information
        """
        logger.info(f"Creating fallback document elements for {file_name}")
        
        # Try to extract some text content depending on file type
        text_content = ""
        file_ext = os.path.splitext(file_name)[1].lower()
        
        try:
            # For text-based files, try to decode the content
            if file_ext in ['.txt', '.csv', '.md', '.json', '.xml', '.html']:
                # Try different encodings
                for encoding in ['utf-8', 'latin-1', 'windows-1252']:
                    try:
                        text_content = file_content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                        
                if not text_content:
                    text_content = f"Failed to extract text from {file_name}"
            else:
                text_content = f"Document: {file_name} (failed to extract content)"
        except Exception as e:
            logger.warning(f"Error creating fallback text: {str(e)}")
            text_content = f"Document: {file_name} (extraction error)"
            
        # Create at least one fallback element
        fallback_element = {
            "type": "Text",
            "text": text_content or f"Document: {file_name} (no extractable text)",
            "metadata": {
                "filename": file_name,
                "filetype": file_ext.lstrip('.') if file_ext else "unknown",
                "is_fallback": True,
                "extraction_failed": True
            }
        }
        
        return [fallback_element]

    def _process_table_elements(self, elements: List[Dict[str, Any]]) -> None:
        """Process table elements to enhance their data."""
        for element in elements:
            if element.get("type") == "Table":
                # Add any table-specific processing here
                pass
    
    def _enhance_metadata(self, elements: List[Dict[str, Any]], file_name: str) -> None:
        """
        Enhance element metadata with additional information.
        
        Args:
            elements: List of document elements to enhance
            file_name: Original filename for reference
        """
        try:
            # Extract basename from file
            basename = os.path.basename(file_name)
            
            # Add global metadata to all elements
            for element in elements:
                if "metadata" not in element:
                    element["metadata"] = {}
                
                # Add source file info
                element["metadata"]["source_file"] = basename
                
                # Add position context if available
                if "position" in element and isinstance(element["position"], dict):
                    # Copy relevant position info to metadata
                    for key in ["page_number", "section", "paragraph"]:
                        if key in element["position"]:
                            element["metadata"][key] = element["position"][key]
        
        except Exception as e:
            logger.error(f"Error enhancing element metadata: {str(e)}")

    def _safe_copy_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a safe copy of metadata to prevent circular references.

        Args:
            metadata: Original metadata dictionary

        Returns:
            Clean copy of metadata with no circular references
        """
        try:
            # First try a quick deep copy - handles most cases
            return json.loads(json.dumps(metadata, default=str))
        except (TypeError, ValueError, json.JSONDecodeError) as e:
            # If we hit errors with JSON serialization, try a manual clean copy
            logger.warning(f"JSON serialization error in metadata: {str(e)}")
            return self._manual_clean_copy(metadata)

    def _manual_clean_copy(self, obj: Any, depth: int = 0, max_depth: int = 5) -> Any:
        """
        Manually create a clean copy of an object, handling circular references.

        Args:
            obj: Object to copy
            depth: Current recursion depth
            max_depth: Maximum recursion depth

        Returns:
            Clean copy of the object
        """
        # Guard against recursion depth
        if depth > max_depth:
            return "[max depth exceeded]"

        # Handle simple types directly
        if obj is None or isinstance(obj, (bool, int, float, str)):
            return obj

        # Handle lists
        if isinstance(obj, list):
            return [self._manual_clean_copy(item, depth + 1, max_depth) for item in obj]

        # Handle dictionaries
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                # Skip complex nested structures that might cause issues
                if isinstance(value, (dict, list)) and depth > 2:
                    result[key] = str(value)[:100] + "..." if len(str(value)) > 100 else str(value)
                else:
                    result[key] = self._manual_clean_copy(value, depth + 1, max_depth)
            return result

        # Other types - convert to string
        return str(obj)

    def _chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks based on the configured chunking strategy.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        if not text or len(text.strip()) == 0:
            return []

        if len(text) <= self.chunk_size:
            return [text]

        # Choose chunking strategy
        if self.chunking_strategy == "fixed":
            return self._fixed_size_chunking(text)
        elif self.chunking_strategy == "recursive":
            return self._recursive_chunking(text)
        elif self.chunking_strategy == "semantic":
            return self._semantic_chunking(text)
        elif self.chunking_strategy == "hierarchical":
            return self._hierarchical_chunking(text)
        elif self.chunking_strategy == "token":
            # Check if token-based chunking is available and enabled
            if HAS_TOKEN_SPLITTER and os.environ.get("ENABLE_TOKEN_CHUNKING", "true").lower() != "false":
                return self._token_chunking(text)
            else:
                logger.warning(f"Token-based chunking requested but not available or disabled, using fixed size chunking")
                return self._fixed_size_chunking(text)
        else:
            # Default to fixed size chunking
            logger.warning(f"Unknown chunking strategy '{self.chunking_strategy}', using fixed size chunking")
            return self._fixed_size_chunking(text)

    def _fixed_size_chunking(self, text: str) -> List[str]:
        """
        Split text into chunks of fixed size with overlap.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        chunks = []
        start = 0
        text_len = len(text)

        while start < text_len:
            end = start + self.chunk_size

            if end >= text_len:
                chunk = text[start:text_len]
            else:
                # Try to find a sentence boundary
                sentence_end = text.rfind(". ", start, end) + 1

                if sentence_end > start:
                    end = sentence_end
                else:
                    # If no sentence boundary, try a word boundary
                    word_end = text.rfind(" ", start, end) + 1
                    if word_end > start:
                        end = word_end

            chunks.append(text[start:end].strip())
            start = end - self.chunk_overlap

        return chunks

    def _recursive_chunking(self, text: str) -> List[str]:
        """
        Recursively split text based on structural elements like paragraphs and sections.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        # First split by double newlines (paragraphs)
        paragraphs = [p for p in text.split("\n\n") if p.strip()]

        chunks = []
        current_chunk = ""

        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
            else:
                # If current chunk is too large, first add it to results
                if current_chunk:
                    chunks.append(current_chunk)

                # If paragraph itself exceeds chunk size, use fixed size chunking
                if len(paragraph) > self.chunk_size:
                    paragraph_chunks = self._fixed_size_chunking(paragraph)
                    chunks.extend(paragraph_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph

        # Add final chunk if not empty
        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _semantic_chunking(self, text: str) -> List[str]:
        """
        Split text based on semantic boundaries using section detection.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        # This is a simplified version - ideally would use ML to detect semantic boundaries
        # For now, use a heuristic approach to identify common section markers
        import re

        # Define section header patterns
        section_patterns = [
            r'\n#+\s+[A-Z]',  # Markdown headers
            r'\n[A-Z][A-Za-z\s]{2,40}\n-{3,}',  # Underlined headers
            r'\n\d+\.\d*\s+[A-Z]',  # Numbered sections
            r'\n[A-Z][A-Z\s]{4,40}[:\n]',  # ALL CAPS headers
            r'\nArticle \d+',  # Legal document sections
            r'\nSection \d+',  # Legal document sections
        ]

        pattern = '|'.join(section_patterns)
        sections = re.split(pattern, text)

        # If we didn't find any sections, fall back to fixed chunking
        if len(sections) <= 1:
            return self._fixed_size_chunking(text)

        # Process each section
        chunks = []
        for section in sections:
            if not section.strip():
                continue

            if len(section) <= self.chunk_size:
                chunks.append(section.strip())
            else:
                # If section is too large, recursively chunk it
                section_chunks = self._recursive_chunking(section)
                chunks.extend(section_chunks)

        return chunks

    def _hierarchical_chunking(self, text: str) -> List[str]:
        """
        Create hierarchical chunks based on document structure, maintaining parent-child relationships.
        This is particularly useful for structured documents.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks with hierarchy information in metadata
        """
        # For simplicity, this implementation is similar to semantic chunking
        # In a production environment, this would track parent-child relationships
        return self._semantic_chunking(text)

    def _token_chunking(self, text: str) -> List[str]:
        """
        Split text into chunks based on token count rather than character count.
        This uses LangChain's TokenTextSplitter which is more aware of token boundaries
        and is better aligned with how LLMs process text.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks split by token count
        """
        if not text or len(text.strip()) == 0:
            return []

        # If TokenTextSplitter is not available, fall back to fixed size chunking
        if not HAS_TOKEN_SPLITTER:
            logger.warning("Token-based chunking not available - falling back to fixed size chunking")
            return self._fixed_size_chunking(text)

        try:
            # Convert character sizes to approximate token counts
            # Rule of thumb: ~4 chars per token for English text
            chars_per_token = 4
            token_size = max(1, self.chunk_size // chars_per_token)
            token_overlap = max(1, self.chunk_overlap // chars_per_token)
            
            # Create TokenTextSplitter with appropriate settings
            splitter = TokenTextSplitter(
                chunk_size=token_size,
                chunk_overlap=token_overlap
            )
            
            # Split the text
            chunks = splitter.split_text(text)
            logger.info(f"Token-based chunking created {len(chunks)} chunks from text of length {len(text)}")
            
            return chunks
        except Exception as e:
            logger.error(f"Error in token chunking: {str(e)}")
            # Fall back to fixed size chunking if token chunking fails
            logger.warning("Falling back to fixed size chunking")
            return self._fixed_size_chunking(text)

    def _hierarchical_chunking_from_elements(self, elements: List[Dict[str, Any]], doc_id: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Create hierarchical chunks from document elements, maintaining parent-child relationships.
        
        Args:
            elements: Document elements extracted from parser
            doc_id: Document ID for creating chunk IDs
            
        Returns:
            Tuple of (chunks, sections) where chunks is a list of chunk dictionaries 
            and sections is a list of section dictionaries
        """
        # This is a simplified implementation
        chunks = []
        sections = []
        
        # Track section hierarchy
        current_section = {"name": "Document", "level": 0, "parent": None}
        sections.append(current_section)
        
        # First pass: identify sections
        for idx, element in enumerate(elements):
            element_type = element.get("type", "unknown")
            element_text = element.get("text", "").strip()
            
            # Skip empty elements
            if not element_text:
                continue
                
            # Create a basic chunk
            chunk = {
                "chunk_id": f"{doc_id}_chunk_{idx}",
                "text": element_text,
                "index": idx,
                "element_type": element_type,
                "section": current_section["name"],
                "metadata": element.get("metadata", {})
            }
            
            # Add page number if available in metadata
            if "metadata" in element and "page_number" in element["metadata"]:
                chunk["page_num"] = element["metadata"]["page_number"]
            else:
                chunk["page_num"] = 0  # Default page number
                
            # Add order_index (same as index) for consistent sorting
            chunk["order_index"] = idx
            
            # Check if this is a heading/title that should start a new section
            if element_type in ["Title", "Header", "Heading", "h1", "h2", "h3"]:
                # Determine heading level
                level = 1
                if "metadata" in element and "header_level" in element["metadata"]:
                    level = element["metadata"]["header_level"]
                elif element_type == "h1":
                    level = 1
                elif element_type == "h2":
                    level = 2
                elif element_type == "h3":
                    level = 3
                
                # Create a new section
                section = {
                    "name": element_text[:100],  # Truncate long titles
                    "level": level,
                    "parent": current_section["name"] if level > current_section["level"] else None
                }
                
                sections.append(section)
                current_section = section
                
                # Update the chunk with section info
                chunk["section"] = section["name"]
                
            chunks.append(chunk)
            
        return chunks, sections
    
    def _fixed_chunking_from_elements(self, elements: List[Dict[str, Any]], doc_id: str) -> List[Dict[str, Any]]:
        """
        Create fixed-size chunks from document elements.
        
        Args:
            elements: Document elements extracted from parser
            doc_id: Document ID for creating chunk IDs
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        chunk_index = 0
        current_chunk_text = ""
        current_section = "Document"
        current_element_types = []
        current_metadata = {}
        current_page_num = 0  # Track current page number
        
        # Process each element
        for element in elements:
            element_type = element.get("type", "unknown")
            element_text = element.get("text", "").strip()
            
            # Skip empty elements
            if not element_text:
                continue
                
            # Check if this element has page information
            if "metadata" in element and "page_number" in element["metadata"]:
                current_page_num = element["metadata"]["page_number"]
                
            # Check if this is a title element to mark a new section
            if element_type == "Title":
                # If we have text in the current chunk, save it before starting a new section
                if current_chunk_text:
                    # Create metadata with the string ID
                    metadata = current_metadata.copy() if current_metadata else {}
                    metadata["doc_id"] = doc_id
                    metadata["chunk_string_id"] = f"{doc_id}_chunk_{chunk_index}"
                    
                    chunk = {
                        "chunk_id": uuid.uuid4(),  # Use UUID for chunk_id
                        "text": current_chunk_text,
                        "index": chunk_index,
                        "element_type": ", ".join(current_element_types),
                        "section": current_section,
                        "metadata": metadata,
                        "page_num": current_page_num,  # Add page number
                        "order_index": chunk_index,  # Add order index
                        "doc_id": doc_id  # Add doc_id directly in chunk
                    }
                    
                    chunks.append(chunk)
                    chunk_index += 1
                    current_chunk_text = ""
                    current_element_types = []
                    
                # Update current section to the title text
                current_section = element_text
                
            # Add element to current chunk
            if current_chunk_text:
                current_chunk_text += "\n\n"
            current_chunk_text += element_text
            
            # Keep track of element types in this chunk
            if element_type not in current_element_types:
                current_element_types.append(element_type)
                
            # Copy metadata from element if available
            if "metadata" in element and isinstance(element["metadata"], dict):
                for key, value in element["metadata"].items():
                    current_metadata[key] = value
                    
            # If we've reached the max chunk size, finalize this chunk and start a new one
            if len(current_chunk_text) >= self.chunk_size:
                # Create metadata with the string ID
                metadata = current_metadata.copy() if current_metadata else {}
                metadata["doc_id"] = doc_id
                metadata["chunk_string_id"] = f"{doc_id}_chunk_{chunk_index}"
                
                chunk = {
                    "chunk_id": uuid.uuid4(),  # Use UUID for chunk_id
                    "text": current_chunk_text,
                    "index": chunk_index,
                    "element_type": ", ".join(current_element_types),
                    "section": current_section,
                    "metadata": metadata,
                    "page_num": current_page_num,  # Add page number
                    "order_index": chunk_index,  # Add order index
                    "doc_id": doc_id  # Add doc_id directly in chunk
                }
                
                chunks.append(chunk)
                chunk_index += 1
                
                # Start a new chunk with overlap
                words = current_chunk_text.split()
                overlap_word_count = min(len(words), int(self.chunk_overlap / 5))  # Approximate words for overlap
                overlap_text = " ".join(words[-overlap_word_count:])
                
                current_chunk_text = overlap_text
                current_element_types = [element_type]  # Reset to current element type
        
        # Add final chunk if not empty
        if current_chunk_text:
            # Create metadata with the string ID
            metadata = current_metadata.copy() if current_metadata else {}
            metadata["doc_id"] = doc_id
            metadata["chunk_string_id"] = f"{doc_id}_chunk_{chunk_index}"
            
            chunk = {
                "chunk_id": uuid.uuid4(),  # Use UUID for chunk_id
                "text": current_chunk_text,
                "index": chunk_index,
                "element_type": ", ".join(current_element_types),
                "section": current_section,
                "metadata": metadata,
                "page_num": current_page_num,  # Add page number
                "order_index": chunk_index,  # Add order index
                "doc_id": doc_id  # Add doc_id directly in chunk
            }
            
            chunks.append(chunk)
        
        return chunks
           
    def _enrich_document(self, doc_id: str, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich document chunks with additional metadata and embeddings.
        
        NOTE: This method no longer stores chunks - it only enriches them for return.

        Args:
            doc_id: Document ID
            chunks: List of document chunks

        Returns:
            Enriched chunks ready for storage by RAG system
        """
        logger.info(f"Enriching document {doc_id} with {len(chunks)} chunks")
        
        # Convert dictionary chunks to DocumentChunk objects with embeddings
        enriched_chunks = []
        
        for chunk in chunks:
            # Skip empty chunks
            if not chunk.get("text", "").strip():
                continue
                
            # Generate embedding for the chunk
            embedding = self.embedding_model.get_text_embedding(chunk.get("text", ""))
            
            # Ensure we have a proper UUID for chunk_id
            chunk_id = chunk.get("chunk_id")
            if not isinstance(chunk_id, uuid.UUID):
                chunk_id = uuid.uuid4()
                
            # Ensure metadata contains string ID if needed
            metadata = chunk.get("metadata", {}).copy()
            if "chunk_string_id" not in metadata:
                metadata["chunk_string_id"] = f"{doc_id}_chunk_{str(chunk_id)[-8:]}"
                
            # Create enriched chunk dictionary
            try:
                enriched_chunk = {
                    "chunk_id": chunk_id,
                    "doc_id": doc_id,
                    "text": chunk.get("text", ""),
                    "content": chunk.get("text", ""),  # For compatibility
                    "embedding": embedding,
                    "metadata": metadata,
                    "page_num": chunk.get("page_num", 0),
                    "element_type": chunk.get("element_type", "text"),
                    "index": chunk.get("index", len(enriched_chunks)),
                    "order_index": chunk.get("order_index", len(enriched_chunks))
                }
                enriched_chunks.append(enriched_chunk)
            except Exception as e:
                logger.warning(f"Error enriching chunk: {str(e)}")
        
        logger.info(f"Enriched {len(enriched_chunks)} chunks with embeddings")
        
        return enriched_chunks

    def process_document(
        self,
        file_content: bytes,
        file_name: str,
        doc_id: Optional[str] = None,
        doc_metadata: Optional[Dict[str, Any]] = None,
        detect_language: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a document and extract text, structure, and metadata.
        
        NOTE: This method now only parses and returns chunks without storing them.
        Storage should be handled by the RAG system.

        Args:
            file_content: Binary content of the file
            file_name: Name of the file
            doc_id: Optional document ID
            doc_metadata: Optional document metadata
            detect_language: Whether to detect document language
            **kwargs: Additional parser-specific arguments

        Returns:
            Dict with document ID, chunks, and processing details
        """
        # Generate document ID if not provided
        if not doc_id:
            doc_id = f"doc_{uuid.uuid4()}"

        # Initialize metadata if not provided
        if doc_metadata is None:
            doc_metadata = {}
            
        # Validate and sanitize metadata
        self._sanitize_metadata(doc_metadata, file_name, file_content)
        
        # Apply parser settings from metadata if provided
        if "parser_settings" in doc_metadata and isinstance(doc_metadata["parser_settings"], dict):
            settings = doc_metadata["parser_settings"]
            
            # Apply extract_images setting if provided
            if "extract_images" in settings:
                self.extract_images = settings["extract_images"]
                logger.info(f"Setting extract_images to {self.extract_images} from document metadata")
                
            # Apply extract_tables setting if provided
            if "extract_tables" in settings:
                self.extract_tables = settings["extract_tables"]
                logger.info(f"Setting extract_tables to {self.extract_tables} from document metadata")
                
            # Apply extract_metadata setting if provided
            if "extract_metadata" in settings:
                self.extract_metadata = settings["extract_metadata"]
                logger.info(f"Setting extract_metadata to {self.extract_metadata} from document metadata")
                
            # Apply chunking_strategy if provided
            if "chunking_strategy" in settings:
                self.chunking_strategy = settings["chunking_strategy"]
                logger.info(f"Setting chunking_strategy to {self.chunking_strategy} from document metadata")
                
            # Apply chunk_size if provided
            if "chunk_size" in settings and isinstance(settings["chunk_size"], int):
                self.chunk_size = settings["chunk_size"]
                logger.info(f"Setting chunk_size to {self.chunk_size} from document metadata")
                
            # Apply chunk_overlap if provided
            if "chunk_overlap" in settings and isinstance(settings["chunk_overlap"], int):
                self.chunk_overlap = settings["chunk_overlap"]
                logger.info(f"Setting chunk_overlap to {self.chunk_overlap} from document metadata")

        # Check if file size exceeds threshold for special processing
        file_size = len(file_content)
        max_regular_size = 20 * 1024 * 1024  # 20 MB
        
        if file_size > max_regular_size:
            logger.info(f"Document size ({file_size/1024/1024:.2f} MB) exceeds threshold, using large document processing")
            
            # Use file extension to determine processing strategy
            file_ext = os.path.splitext(file_name)[1].lower()
            
            if file_ext in ['.txt', '.md', '.csv', '.tsv']:
                # For text files, split by content
                return self._process_large_text_document(
                    file_content, file_name, doc_id, doc_metadata
                )
            else:
                # For binary files like PDFs, use a different approach
                return self._process_large_binary_document(
                    file_content, file_name, doc_id, doc_metadata,
                    max_size_per_chunk=10 * 1024 * 1024  # 10 MB per chunk
                )

        # For normal sized documents
        try:
            logger.info(f"Processing document: {file_name} with ID: {doc_id}")
            
            # Process the document with Unstructured
            elements = self._call_unstructured_api(file_content, file_name)
            
            # Generate chunks from elements
            if self.chunking_strategy == "hierarchical":
                chunks, structured_data = self._hierarchical_chunking_from_elements(elements, doc_id)
            else:
                chunks = self._fixed_chunking_from_elements(elements, doc_id)
                structured_data = []

            # Enrich chunks with additional data and embeddings (but don't store)
            enriched_chunks = self._enrich_document(doc_id, chunks)
            
            logger.info(f"Generated {len(enriched_chunks)} enriched chunks for document: {doc_id}")
            
            # Return the parsed result with chunks for the RAG system to store
            return {
                "doc_id": doc_id,
                "chunks": enriched_chunks,
                "metadata": doc_metadata,
                "chunk_count": len(enriched_chunks),
                "section_count": len(structured_data),
                "image_count": sum(1 for chunk in chunks if chunk.get("type") == "Image"),
                "table_count": sum(1 for chunk in chunks if chunk.get("type") == "Table"),
                "file_name": file_name,
                "content": "\n\n".join([chunk.get("text", "") for chunk in enriched_chunks])  # Raw content for RAG
            }
        
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}", exc_info=True)
            raise

    def process_large_document(
        self,
        file_content: bytes,
        file_name: str,
        doc_id: Optional[str] = None,
        doc_metadata: Optional[Dict[str, Any]] = None,
        max_size_per_chunk: int = 5 * 1024 * 1024,  # 5MB chunks
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a large document by chunking it into smaller pieces.

        For the Unstructured API implementation, we simply delegate to the regular
        process_document method as it already handles large documents appropriately.

        Args:
            file_content: Binary content of the file
            file_name: Name of the file
            doc_id: Optional document ID
            doc_metadata: Optional document metadata
            max_size_per_chunk: Maximum size per chunk in bytes
            **kwargs: Additional parser-specific arguments

        Returns:
            Dict with document ID and processing details
        """
        return self.process_document(
            file_content=file_content,
            file_name=file_name,
            doc_id=doc_id,
            doc_metadata=doc_metadata,
            detect_language=True,
            **kwargs
        )

    def close(self):
        """
        Close the document parser and release resources.
        """
        # No resources to close in this implementation
        pass

    def get_document_chunks(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Note: This method is deprecated since storage is now handled by RAG system.
        This method is kept for backward compatibility but will return empty list.
        
        Args:
            doc_id: Document ID to retrieve chunks for
            
        Returns:
            Empty list (storage is handled by RAG system)
        """
        logger.warning("get_document_chunks called on DocumentParser - storage is now handled by RAG system")
        return []

    def _sanitize_metadata(self, metadata: Dict[str, Any], file_name: str, file_content: bytes) -> None:
        """
        Sanitize metadata to ensure valid values.
        
        Args:
            metadata: Metadata dictionary to sanitize (modified in place)
            file_name: Name of the file
            file_content: Binary content of the file
        """
        # Ensure basic metadata fields exist with valid values
        
        # File size
        if "size" not in metadata or not isinstance(metadata["size"], (int, float)) or math.isnan(metadata["size"]):
            metadata["size"] = len(file_content)
            
        # Calculate size in KB for display
        metadata["size_kb"] = round(metadata["size"] / 1024, 2) if metadata["size"] > 0 else 0
            
        # File type
        if "file_type" not in metadata or not metadata["file_type"]:
            ext = os.path.splitext(file_name)[1].lower().lstrip('.')
            metadata["file_type"] = ext if ext else "Unknown"
            
        # Title
        if "title" not in metadata or not metadata["title"]:
            # Use filename without extension as title
            base_name = os.path.basename(file_name)
            title = os.path.splitext(base_name)[0]
            # Convert CamelCase or snake_case to spaces for better readability
            title = re.sub(r'([a-z])([A-Z])', r'\1 \2', title)  # CamelCase to spaces
            title = re.sub(r'_+', ' ', title)  # snake_case to spaces
            title = re.sub(r'\s+', ' ', title).strip()  # Normalize spaces
            metadata["title"] = title if title else file_name
            
        # Author
        if "author" not in metadata or not isinstance(metadata["author"], str):
            metadata["author"] = "N/A"
            
        # Category
        if "category" not in metadata or not isinstance(metadata["category"], str):
            metadata["category"] = "Uncategorized"
            
        # Timestamps
        current_time = py_datetime.now().isoformat()
        
        if "created_at" not in metadata or not metadata["created_at"]:
            metadata["created_at"] = current_time
            
        if "uploaded_at" not in metadata:
            metadata["uploaded_at"] = current_time
            
        # Language (this will be further processed during language detection)
        if "language" not in metadata or not isinstance(metadata["language"], str):
            metadata["language"] = "en"
            
        # Clean any None values
        for key in list(metadata.keys()):
            if metadata[key] is None:
                if key in ["title", "author", "category"]:
                    # Replace important None fields with defaults
                    if key == "title":
                        metadata[key] = os.path.basename(file_name)
                    elif key == "author":
                        metadata[key] = "N/A"
                    elif key == "category":
                        metadata[key] = "Uncategorized"