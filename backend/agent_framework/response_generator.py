"""
Response Generator for the RegulAIte Agent Framework.

This module provides functionality for generating, formatting, and validating
responses from the agent system.
"""
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, model_validator
import logging
import json
from datetime import datetime

from .agent import AgentResponse, Query
from .query_parser import ParsedQuery, QueryCategory

# Set up logging
logger = logging.getLogger(__name__)

class SourceInfo(BaseModel):
    """Information about a source used in a response."""
    title: Optional[str] = Field(None, description="Document title if available")
    url: Optional[str] = None
    snippet: Optional[str] = None
    relevance_score: Optional[float] = None
    source_type: str = "document"

class ResponseFormat(str):
    """Response format type."""
    TEXT = "text"
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"

class FormattedResponse(BaseModel):
    """A fully formatted response ready for delivery to the user."""
    response_id: str
    content: str
    format: str = ResponseFormat.TEXT
    sources: Optional[List[SourceInfo]] = None
    confidence: float = 1.0
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_content_format(self):
        """Validate that the content matches the specified format."""
        if self.format == ResponseFormat.JSON:
            try:
                # Check if content is valid JSON
                json.loads(self.content)
            except json.JSONDecodeError:
                # If not valid JSON, wrap in a JSON object
                self.content = json.dumps({"response": self.content})
                
        return self

class ResponseGenerator:
    """
    Generator for formatting and validating agent responses.
    """
    
    def __init__(self):
        """Initialize the response generator."""
        self.formatters = {
            ResponseFormat.TEXT: self._format_text,
            ResponseFormat.JSON: self._format_json,
            ResponseFormat.MARKDOWN: self._format_markdown,
            ResponseFormat.HTML: self._format_html
        }
        
    async def generate(self, 
                      response: AgentResponse, 
                      query: Union[Query, ParsedQuery],
                      format: str = ResponseFormat.MARKDOWN) -> FormattedResponse:
        """
        Generate a formatted response.
        
        Args:
            response: The raw agent response
            query: The original query
            format: The desired output format (default: markdown)
            
        Returns:
            A formatted response
        """
        # Get the appropriate formatter
        formatter = self.formatters.get(format, self._format_markdown)
        
        # For markdown format, use the enhanced formatter with metadata
        if format == ResponseFormat.MARKDOWN:
            formatted_content = self._format_markdown_with_metadata(response.content, response, query)
        else:
            formatted_content = formatter(response.content, query)
        
        # Create the formatted response
        formatted_response = FormattedResponse(
            response_id=response.response_id,
            content=formatted_content,
            format=format,
            confidence=response.confidence,
            metadata={
                "query": query.dict() if hasattr(query, "dict") else {"query_text": str(query)},
                "tools_used": response.tools_used,
                "context_used": response.context_used,
                **response.metadata
            }
        )
        
        # Add sources if available
        if response.sources:
            formatted_response.sources = []
            for source in response.sources:
                try:
                    if isinstance(source, dict):
                        # Ensure title is present for dict sources
                        if 'title' not in source or not source['title']:
                            source['title'] = "Unknown Source"
                        formatted_response.sources.append(SourceInfo(**source))
                    else:
                        formatted_response.sources.append(SourceInfo(title=str(source) if source else "Unknown Source"))
                except Exception as e:
                    logger.warning(f"Error creating SourceInfo from {source}: {e}")
                    # Create a minimal valid SourceInfo
                    formatted_response.sources.append(SourceInfo(title="Source Error"))
                    
        elif "sources" in response.metadata:
            formatted_response.sources = []
            for source in response.metadata["sources"]:
                try:
                    if isinstance(source, dict):
                        # Ensure title is present for dict sources
                        if 'title' not in source or not source['title']:
                            source['title'] = "Unknown Source"
                        formatted_response.sources.append(SourceInfo(**source))
                    else:
                        formatted_response.sources.append(SourceInfo(title=str(source) if source else "Unknown Source"))
                except Exception as e:
                    logger.warning(f"Error creating SourceInfo from {source}: {e}")
                    # Create a minimal valid SourceInfo
                    formatted_response.sources.append(SourceInfo(title="Source Error"))
            
        # Log the response generation
        logger.info(f"Generated {format} response for query: {query.query_text if hasattr(query, 'query_text') else query}")
        
        return formatted_response
        
    def _format_text(self, content: str, query: Union[Query, ParsedQuery]) -> str:
        """
        Format the response as plain text.
        
        Args:
            content: The response content
            query: The original query
            
        Returns:
            Formatted plain text response
        """
        # For text format, just return the content as is
        return content
        
    def _format_json(self, content: str, query: Union[Query, ParsedQuery]) -> str:
        """
        Format the response as JSON.
        
        Args:
            content: The response content
            query: The original query
            
        Returns:
            Formatted JSON response
        """
        # Create a response object
        response_obj = {
            "response": content,
            "query": query.query_text if hasattr(query, "query_text") else str(query)
        }
        
        # Add category if available
        if hasattr(query, "category"):
            response_obj["category"] = query.category
            
        # Add entities if available
        if hasattr(query, "entities") and query.entities:
            response_obj["entities"] = query.entities
            
        return json.dumps(response_obj)
        
    def _format_markdown(self, content: str, query: Union[Query, ParsedQuery]) -> str:
        """
        Format the response as Markdown with proper structure.
        
        Args:
            content: The response content
            query: The original query
            
        Returns:
            Formatted Markdown response with proper structure
        """
        # Start with the main response content
        formatted = f"{content}\n\n"
        
        # Don't add redundant "Response" header if content already has structure
        if not content.strip().startswith('#'):
            formatted = f"## Response\n\n{content}\n\n"
        
        return formatted
        
    def _format_markdown_with_metadata(self, content: str, response: 'AgentResponse', query: Union[Query, ParsedQuery]) -> str:
        """
        Format the response as Markdown with metadata sections.
        
        Args:
            content: The response content
            response: The full agent response with metadata
            query: The original query
            
        Returns:
            Formatted Markdown response with metadata sections
        """
        # Clean and ensure proper markdown structure
        formatted = content.strip()
        
        # Ensure the response starts with a markdown header
        if not formatted.startswith('#'):
            # If content doesn't start with a header, add one
            lines = formatted.split('\n')
            first_line = lines[0].strip()
            
            # If first line looks like a title/summary, make it a header
            if first_line and not first_line.startswith('#'):
                # Check if it's a short title-like line (less than 100 chars, no periods at end)
                if len(first_line) < 100 and not first_line.endswith('.'):
                    lines[0] = f"## {first_line}"
                else:
                    # Insert a generic header at the beginning
                    lines.insert(0, "## Réponse" if self._detect_french(formatted) else "## Response")
                    lines.insert(1, "")  # Add spacing
                
                formatted = '\n'.join(lines)
        
        # Ensure proper spacing after headers
        formatted = self._fix_markdown_spacing(formatted)
        
        # Ensure proper ending
        if not formatted.endswith('\n\n'):
            formatted += '\n\n'
        
        # Add tools used section if available
        if response.tools_used and len(response.tools_used) > 0:
            formatted += "## Analysis Tools Used\n\n"
            for tool in response.tools_used:
                formatted += f"- **{tool}**: Specialized analysis tool\n"
            formatted += "\n"
                
        # Add confidence indicator if available and not perfect
        if hasattr(response, 'confidence') and response.confidence < 1.0:
            confidence_percent = int(response.confidence * 100)
            formatted += f"## Confidence Level\n\n"
            formatted += f"Response confidence: **{confidence_percent}%**\n\n"
        
        return formatted
    
    def _detect_french(self, text: str) -> bool:
        """Detect if text is in French."""
        french_indicators = ['le ', 'la ', 'les ', 'de ', 'du ', 'des ', 'et ', 'est ', 'un ', 'une ']
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in french_indicators)
    
    def _fix_markdown_spacing(self, content: str) -> str:
        """Fix markdown spacing issues."""
        lines = content.split('\n')
        fixed_lines = []
        
        for i, line in enumerate(lines):
            fixed_lines.append(line)
            
            # Add spacing after headers if not already present
            if line.startswith('#') and i < len(lines) - 1:
                next_line = lines[i + 1] if i + 1 < len(lines) else ""
                if next_line.strip() != "":
                    fixed_lines.append("")  # Add empty line after header
        
        return '\n'.join(fixed_lines)
        
    def _format_html(self, content: str, query: Union[Query, ParsedQuery]) -> str:
        """
        Format the response as HTML.
        
        Args:
            content: The response content
            query: The original query
            
        Returns:
            Formatted HTML response
        """
        # Convert the content to HTML
        # For now, just wrap in basic HTML tags and escape special characters
        import html
        
        escaped_content = html.escape(content)
        formatted = f"<div class='response'><p>{escaped_content}</p></div>"
        
        # Add sources section if available in query metadata
        if hasattr(query, "metadata") and "sources" in query.metadata:
            formatted += "<div class='sources'><h3>Sources</h3><ul>"
            for i, source in enumerate(query.metadata["sources"]):
                title = html.escape(source.get("title", f"Source {i+1}"))
                url = source.get("url", "")
                
                if url:
                    formatted += f"<li><a href='{html.escape(url)}'>{title}</a></li>"
                else:
                    formatted += f"<li>{title}</li>"
            
            formatted += "</ul></div>"
            
        return formatted 