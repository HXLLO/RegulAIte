"""
Tool Registry for the RegulAIte Agent Framework.

This module provides a registry for tools that can be used by agents,
including dynamic tool discovery, registration, and selection logic.
"""
from typing import Dict, List, Optional, Any, Callable, Type, Set, Union
from pydantic import BaseModel, Field, create_model
import inspect
import logging
import importlib
import pkgutil
import os
import json
from functools import wraps

# Set up logging
logger = logging.getLogger(__name__)

class ToolParameter(BaseModel):
    """Parameter definition for a tool."""
    name: str
    description: str
    type: str
    required: bool = False
    default: Optional[Any] = None
    
class ToolMetadata(BaseModel):
    """Metadata for a tool."""
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    parameters: List[ToolParameter] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    requires_context: bool = False
    
class Tool:
    """Base class for defining tools that can be used by agents."""
    
    def __init__(self, func: Callable = None):
        """
        Initialize a tool from a function.
        
        Args:
            func: The function to wrap as a tool
        """
        # Set default metadata
        self.metadata = ToolMetadata(
            id=getattr(func, "__name__", "unknown_tool"),
            name=getattr(func, "__name__", "Unknown Tool").replace("_", " ").title(),
            description=getattr(func, "__doc__", "No description provided").strip()
        )
        
        self.func = func
        
        if func:
            # Introspect the function to get parameter information
            sig = inspect.signature(func)
            params = []
            
            for name, param in sig.parameters.items():
                # Skip self for methods
                if name == "self":
                    continue
                    
                # Get parameter type
                param_type = "any"
                if param.annotation != inspect.Parameter.empty:
                    if hasattr(param.annotation, "__name__"):
                        param_type = param.annotation.__name__
                    else:
                        param_type = str(param.annotation)
                
                # Determine if required
                required = param.default == inspect.Parameter.empty
                
                # Get default value if available
                default = None if param.default == inspect.Parameter.empty else param.default
                
                # Try to get description from docstring if possible
                description = f"Parameter: {name}"
                
                params.append(ToolParameter(
                    name=name,
                    description=description,
                    type=param_type,
                    required=required,
                    default=default
                ))
                
            self.metadata.parameters = params
    
    def __call__(self, *args, **kwargs):
        """
        Execute the tool.
        
        Args:
            *args: Positional arguments to pass to the tool function
            **kwargs: Keyword arguments to pass to the tool function
            
        Returns:
            The result of the tool function
        """
        if not self.func:
            raise NotImplementedError("Tool function not implemented")
            
        # Log tool execution
        logger.info(f"Executing tool: {self.metadata.id}")
        
        # Execute the tool function
        return self.func(*args, **kwargs)

def tool(id: str = None, name: str = None, description: str = None, 
         tags: List[str] = None, requires_context: bool = False, 
         version: str = "1.0.0"):
    """
    Decorator to register a function as a tool.
    
    Args:
        id: Unique identifier for the tool (defaults to function name)
        name: Display name for the tool (defaults to formatted function name)
        description: Description of the tool (defaults to function docstring)
        tags: Tags for categorizing the tool
        requires_context: Whether the tool requires context
        version: Version of the tool
        
    Returns:
        Decorated function wrapped as a Tool
    """
    def decorator(func):
        # Create a new Tool instance
        tool_instance = Tool(func)
        
        # Update metadata with provided values
        if id:
            tool_instance.metadata.id = id
        if name:
            tool_instance.metadata.name = name
        if description:
            tool_instance.metadata.description = description
        if tags:
            tool_instance.metadata.tags = tags
        
        tool_instance.metadata.requires_context = requires_context
        tool_instance.metadata.version = version
        
        # Save metadata on the function itself
        func._tool_metadata = tool_instance.metadata
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return tool_instance(*args, **kwargs)
            
        wrapper._tool_metadata = tool_instance.metadata
        return wrapper
        
    return decorator

class ToolRegistry:
    """
    Registry for managing tools that can be used by agents.
    
    This registry provides methods for discovering, registering, and selecting tools.
    """
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self.tools: Dict[str, Tool] = {}
        self.tags: Set[str] = set()
        self._llm_client = None
        
        # Initialize LLM client for intelligent tool selection
        try:
            from .integrations.llm_integration import get_llm_integration
            self._llm_client = get_llm_integration()
            logger.info("Initialized LLM client for tool registry")
        except Exception as e:
            logger.warning(f"Could not initialize LLM client for tool registry: {str(e)}")
            self._llm_client = None
        
    def register(self, tool_func: Union[Tool, Callable], **kwargs) -> str:
        """
        Register a tool with the registry.
        
        Args:
            tool_func: A Tool instance or a callable to register as a tool
            **kwargs: Additional metadata to apply to the tool
            
        Returns:
            The ID of the registered tool
        """
        # If the tool_func is not a Tool instance, create one
        if not isinstance(tool_func, Tool) and not hasattr(tool_func, "_tool_metadata"):
            tool_func = tool(
                id=kwargs.get("id"),
                name=kwargs.get("name"),
                description=kwargs.get("description"),
                tags=kwargs.get("tags"),
                requires_context=kwargs.get("requires_context", False),
                version=kwargs.get("version", "1.0.0")
            )(tool_func)
        
        # Get the tool metadata
        if isinstance(tool_func, Tool):
            metadata = tool_func.metadata
        else:
            metadata = tool_func._tool_metadata
            
        # Register the tool
        tool_id = metadata.id
        self.tools[tool_id] = tool_func
        
        # Update tags
        for tag in metadata.tags:
            self.tags.add(tag)
            
        logger.info(f"Registered tool: {tool_id}")
        return tool_id
        
    def get_tool(self, tool_id: str) -> Optional[Union[Tool, Callable]]:
        """
        Get a tool by its ID.
        
        Args:
            tool_id: ID of the tool to get
            
        Returns:
            The tool, or None if not found
        """
        return self.tools.get(tool_id)
        
    def get_tools_by_tag(self, tag: str) -> List[Union[Tool, Callable]]:
        """
        Get all tools with a specific tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of tools with the specified tag
        """
        return [
            tool for tool in self.tools.values()
            if tag in (tool.metadata.tags if isinstance(tool, Tool) else tool._tool_metadata.tags)
        ]
        
    def list_tools(self) -> List[ToolMetadata]:
        """
        List metadata for all registered tools.
        
        Returns:
            List of ToolMetadata for all registered tools
        """
        return [
            tool.metadata if isinstance(tool, Tool) else tool._tool_metadata
            for tool in self.tools.values()
        ]
        
    async def select_tools(self, query: str, n: int = 5) -> List[str]:
        """
        Select the most relevant tools for a given query using LLM intelligence.
        
        Args:
            query: The query to select tools for
            n: Maximum number of tools to select
            
        Returns:
            List of tool IDs most relevant to the query
        """
        if not self.tools:
            logger.warning("No tools available for selection")
            return []
            
        # Use LLM for intelligent tool selection if available
        if self._llm_client:
            try:
                return await self._select_tools_with_llm(query, n)
            except Exception as e:
                logger.warning(f"LLM tool selection failed, falling back to keyword matching: {str(e)}")
                return self._select_tools_with_keywords(query, n)
        else:
            # Fallback to keyword-based selection
            return self._select_tools_with_keywords(query, n)
            
    async def _select_tools_with_llm(self, query: str, n: int = 5) -> List[str]:
        """
        Select tools using LLM for semantic understanding.
        
        Args:
            query: The query to select tools for
            n: Maximum number of tools to select
            
        Returns:
            List of tool IDs most relevant to the query
        """
        import json
        
        # Prepare tool information for the LLM
        tools_info = []
        for tool_id, tool in self.tools.items():
            metadata = tool.metadata if isinstance(tool, Tool) else tool._tool_metadata
            tools_info.append({
                "id": tool_id,
                "name": metadata.name,
                "description": metadata.description,
                "tags": metadata.tags,
                "requires_context": metadata.requires_context
            })
        
        prompt = f"""
You are an AI assistant that helps select the most relevant tools for user queries. 

Available tools:
{json.dumps(tools_info, indent=2)}

User query: "{query}"

Analyze the query and select the {n} most relevant tools that would help answer or process this query. Consider:
1. The semantic meaning of the query
2. The capabilities described in each tool's description
3. The tags associated with each tool
4. Whether the tool requires context and if the query suggests context is needed

Return your response as a JSON array of tool IDs, ordered by relevance (most relevant first):
["tool_id_1", "tool_id_2", ...]

If no tools are relevant, return an empty array: []

Response:
"""
        
        try:
            # Use the async LLM client directly without creating a new event loop
            response = await self._llm_client.generate(prompt, temperature=0.1)
            
            # Parse the JSON response
            try:
                selected_tools = json.loads(response)
                if isinstance(selected_tools, list):
                    # Validate that all selected tools exist
                    valid_tools = [tool_id for tool_id in selected_tools if tool_id in self.tools]
                    logger.info(f"LLM selected {len(valid_tools)} tools for query: {query}")
                    return valid_tools[:n]
                else:
                    logger.warning(f"LLM response is not a list: {response}")
                    return []
            except json.JSONDecodeError as e:
                logger.warning(f"LLM response is not valid JSON: {str(e)}")
                # Try to extract tool IDs from the text response
                return self._extract_tool_ids_from_response(response, n)
                
        except Exception as e:
            logger.error(f"Error in LLM tool selection: {str(e)}")
            raise
            
    def _extract_tool_ids_from_response(self, response: str, n: int) -> List[str]:
        """
        Extract tool IDs from a non-JSON LLM response.
        
        Args:
            response: The text response from LLM
            n: Maximum number of tools to extract
            
        Returns:
            List of extracted tool IDs
        """
        import re
        
        # Look for tool IDs in the response
        tool_ids = []
        
        # Try to find quoted tool IDs
        quoted_matches = re.findall(r'"([^"]+)"', response)
        for match in quoted_matches:
            if match in self.tools:
                tool_ids.append(match)
                
        # Try to find tool IDs mentioned directly
        for tool_id in self.tools.keys():
            if tool_id in response and tool_id not in tool_ids:
                tool_ids.append(tool_id)
                
        return tool_ids[:n]
        
    def _select_tools_with_keywords(self, query: str, n: int = 5) -> List[str]:
        """
        Select tools using keyword matching (fallback method).
        
        Args:
            query: The query to select tools for
            n: Maximum number of tools to select
            
        Returns:
            List of tool IDs most relevant to the query
        """
        relevant_tools = []
        query_lower = query.lower()
        
        # Simple keyword matching for now
        for tool_id, tool in self.tools.items():
            metadata = tool.metadata if isinstance(tool, Tool) else tool._tool_metadata
            
            # Check if any keywords in the description or name match the query
            if (query_lower in metadata.description.lower() or 
                query_lower in metadata.name.lower() or
                any(query_lower in tag.lower() for tag in metadata.tags)):
                relevant_tools.append(tool_id)
                
        # Limit to n tools
        return relevant_tools[:n]
        
    def discover_tools(self, package_path: str) -> List[str]:
        """
        Discover and register tools from a Python package.
        
        Args:
            package_path: Path to the package containing tools
            
        Returns:
            List of IDs for registered tools
        """
        registered_tools = []
        
        # Get the package object
        try:
            package = importlib.import_module(package_path)
        except ImportError:
            logger.error(f"Could not import package: {package_path}")
            return registered_tools
            
        # Walk through all modules in the package
        for _, name, is_pkg in pkgutil.iter_modules([os.path.dirname(package.__file__)]):
            # Import the module
            module_name = f"{package_path}.{name}"
            try:
                module = importlib.import_module(module_name)
            except ImportError:
                logger.error(f"Could not import module: {module_name}")
                continue
                
            # Find all functions with _tool_metadata
            for item_name in dir(module):
                item = getattr(module, item_name)
                
                if callable(item) and hasattr(item, "_tool_metadata"):
                    # Register the tool
                    tool_id = self.register(item)
                    registered_tools.append(tool_id)
        
        return registered_tools 