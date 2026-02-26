"""
FastAPI router for system-wide configuration settings.
"""
import logging
import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/config",
    tags=["configuration"],
    responses={404: {"description": "Not found"}},
)

# Models for API
class LLMConfig(BaseModel):
    """Configuration for LLM settings."""
    model: str = Field("gpt-4", description="Default model to use")
    temperature: float = Field(0.7, description="Default temperature")
    max_tokens: int = Field(2048, description="Default maximum tokens")
    top_p: float = Field(1.0, description="Default top_p value")
    frequency_penalty: float = Field(0.0, description="Default frequency penalty")
    presence_penalty: float = Field(0.0, description="Default presence penalty")
    api_key: Optional[str] = Field(None, description="OpenAI API key (masked for security)")
    api_base: Optional[str] = Field(None, description="Custom API base URL")
    default_system_prompt: Optional[str] = Field(None, description="Default system prompt")


class RAGConfig(BaseModel):
    """Configuration for RAG settings."""
    hybrid_search: bool = Field(True, description="Whether to use hybrid search by default")
    vector_weight: float = Field(0.7, description="Weight for vector search in hybrid mode")
    semantic_weight: float = Field(0.3, description="Weight for semantic search in hybrid mode")
    default_top_k: int = Field(5, description="Default number of results to retrieve")
    reranking_enabled: bool = Field(False, description="Whether to use reranking")
    reranking_model: Optional[str] = Field(None, description="Model to use for reranking")
    embedding_model: str = Field("text-embedding-ada-002", description="Embedding model to use")
    embedding_dim: int = Field(1536, description="Dimension of embeddings")


class UIConfig(BaseModel):
    """Configuration for UI settings."""
    theme: str = Field("system", description="UI theme (light, dark, system)")
    primary_color: str = Field("#0077CC", description="Primary color")
    accent_color: str = Field("#00AAFF", description="Accent color")
    logo_url: Optional[str] = Field(None, description="Custom logo URL")
    app_name: str = Field("RegulAite", description="Application name")
    welcome_message: Optional[str] = Field(None, description="Welcome message")
    default_page: str = Field("dashboard", description="Default landing page")
    hide_experimental: bool = Field(False, description="Hide experimental features")


class SystemConfig(BaseModel):
    """System-wide configuration."""
    debug_mode: bool = Field(False, description="Whether debug mode is enabled")
    log_level: str = Field("INFO", description="Logging level")
    max_concurrent_tasks: int = Field(5, description="Maximum concurrent background tasks")
    task_timeout_seconds: int = Field(300, description="Task timeout in seconds")
    enable_telemetry: bool = Field(True, description="Whether to collect anonymous usage statistics")
    api_rate_limit: int = Field(100, description="API rate limit per minute")
    maintenance_mode: bool = Field(False, description="Whether maintenance mode is enabled")


class ConfigResponse(BaseModel):
    """Combined configuration response."""
    llm: LLMConfig = Field(..., description="LLM configuration")
    rag: RAGConfig = Field(..., description="RAG configuration")
    ui: UIConfig = Field(..., description="UI configuration")
    system: SystemConfig = Field(..., description="System configuration")
    last_updated: str = Field(..., description="Last updated timestamp")


# Helper function to get database connection
async def get_db_connection():
    """Get MariaDB connection from main application."""
    from main import get_mariadb_connection
    return get_mariadb_connection()


@router.get("", response_model=ConfigResponse)
async def get_all_config():
    """Get all configuration settings."""
    try:
        conn = await get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT setting_key, setting_value, updated_at
            FROM regulaite_settings
            """
        )

        settings = {}
        last_updated = None

        for row in cursor.fetchall():
            settings[row['setting_key']] = row['setting_value']
            # Track the most recent update
            if last_updated is None or row['updated_at'] > last_updated:
                last_updated = row['updated_at']

        conn.close()

        # Parse settings into respective config objects
        # LLM Configuration
        llm_config = LLMConfig(
            model=settings.get('llm_model', 'gpt-4'),
            temperature=float(settings.get('llm_temperature', 0.7)),
            max_tokens=int(settings.get('llm_max_tokens', 2048)),
            top_p=float(settings.get('llm_top_p', 1.0)),
            frequency_penalty=float(settings.get('llm_frequency_penalty', 0.0)),
            presence_penalty=float(settings.get('llm_presence_penalty', 0.0)),
            api_base=settings.get('llm_api_base', None),
            default_system_prompt=settings.get('llm_default_system_prompt', None)
        )

        # Don't return the actual API key, just indicate if it's set
        if 'llm_api_key' in settings and settings['llm_api_key']:
            llm_config.api_key = '**********'

        # RAG Configuration
        rag_config = RAGConfig(
            hybrid_search=settings.get('rag_hybrid_search', 'true').lower() == 'true',
            vector_weight=float(settings.get('rag_vector_weight', 0.7)),
            semantic_weight=float(settings.get('rag_semantic_weight', 0.3)),
            default_top_k=int(settings.get('rag_default_top_k', 5)),
            reranking_enabled=settings.get('rag_reranking_enabled', 'false').lower() == 'true',
            reranking_model=settings.get('rag_reranking_model', None),
            embedding_model=settings.get('rag_embedding_model', 'text-embedding-ada-002'),
            embedding_dim=int(settings.get('rag_embedding_dim', 1536))
        )

        # UI Configuration
        ui_config = UIConfig(
            theme=settings.get('ui_theme', 'system'),
            primary_color=settings.get('ui_primary_color', '#0077CC'),
            accent_color=settings.get('ui_accent_color', '#00AAFF'),
            logo_url=settings.get('ui_logo_url', None),
            app_name=settings.get('ui_app_name', 'RegulAite'),
            welcome_message=settings.get('ui_welcome_message', None),
            default_page=settings.get('ui_default_page', 'dashboard'),
            hide_experimental=settings.get('ui_hide_experimental', 'false').lower() == 'true'
        )

        # System Configuration
        system_config = SystemConfig(
            debug_mode=settings.get('system_debug_mode', 'false').lower() == 'true',
            log_level=settings.get('system_log_level', 'INFO'),
            max_concurrent_tasks=int(settings.get('system_max_concurrent_tasks', 5)),
            task_timeout_seconds=int(settings.get('system_task_timeout_seconds', 300)),
            enable_telemetry=settings.get('system_enable_telemetry', 'true').lower() == 'true',
            api_rate_limit=int(settings.get('system_api_rate_limit', 100)),
            maintenance_mode=settings.get('system_maintenance_mode', 'false').lower() == 'true'
        )

        return ConfigResponse(
            llm=llm_config,
            rag=rag_config,
            ui=ui_config,
            system=system_config,
            last_updated=last_updated.isoformat() if last_updated else None
        )

    except Exception as e:
        logger.error(f"Error retrieving configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving configuration: {str(e)}"
        )


@router.post("/llm", response_model=LLMConfig)
async def update_llm_config(config: LLMConfig):
    """Update LLM configuration settings."""
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()

        # Update each provided setting
        updates = config.dict(exclude_none=True)

        for key, value in updates.items():
            # Special handling for API key - only update if it's not masked
            if key == "api_key" and value == "**********":
                continue

            setting_key = f"llm_{key}"

            cursor.execute(
                """
                INSERT INTO regulaite_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON DUPLICATE KEY UPDATE setting_value = ?
                """,
                (setting_key, str(value), str(value))
            )

        conn.commit()
        conn.close()

        # Reload configuration from database to return the updated values
        return (await get_all_config()).llm

    except Exception as e:
        logger.error(f"Error updating LLM configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating LLM configuration: {str(e)}"
        )


@router.post("/rag", response_model=RAGConfig)
async def update_rag_config(config: RAGConfig):
    """Update RAG configuration settings."""
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()

        # Update each provided setting
        updates = config.dict(exclude_none=True)

        for key, value in updates.items():
            # Convert boolean values to strings
            if isinstance(value, bool):
                value = str(value).lower()

            setting_key = f"rag_{key}"

            cursor.execute(
                """
                INSERT INTO regulaite_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON DUPLICATE KEY UPDATE setting_value = ?
                """,
                (setting_key, str(value), str(value))
            )

        conn.commit()
        conn.close()

        # Update the RAG system with new configuration if possible
        try:
            from main import rag_system

            # Update RAG system parameters if they exist in our config
            if "hybrid_search" in updates:
                rag_system.hybrid_search = updates["hybrid_search"]
            if "vector_weight" in updates:
                rag_system.vector_weight = updates["vector_weight"]
            if "semantic_weight" in updates:
                rag_system.semantic_weight = updates["semantic_weight"]

            logger.info("Updated RAG system with new configuration")
        except Exception as e:
            logger.warning(f"Could not update RAG system configuration: {str(e)}")

        # Reload configuration from database to return the updated values
        return (await get_all_config()).rag

    except Exception as e:
        logger.error(f"Error updating RAG configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating RAG configuration: {str(e)}"
        )


@router.post("/ui", response_model=UIConfig)
async def update_ui_config(config: UIConfig):
    """Update UI configuration settings."""
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()

        # Update each provided setting
        updates = config.dict(exclude_none=True)

        for key, value in updates.items():
            # Convert boolean values to strings
            if isinstance(value, bool):
                value = str(value).lower()

            setting_key = f"ui_{key}"

            cursor.execute(
                """
                INSERT INTO regulaite_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON DUPLICATE KEY UPDATE setting_value = ?
                """,
                (setting_key, str(value), str(value))
            )

        conn.commit()
        conn.close()

        # Reload configuration from database to return the updated values
        return (await get_all_config()).ui

    except Exception as e:
        logger.error(f"Error updating UI configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating UI configuration: {str(e)}"
        )


@router.post("/system", response_model=SystemConfig)
async def update_system_config(config: SystemConfig):
    """Update system configuration settings."""
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()

        # Update each provided setting
        updates = config.dict(exclude_none=True)

        for key, value in updates.items():
            # Convert boolean values to strings
            if isinstance(value, bool):
                value = str(value).lower()

            setting_key = f"system_{key}"

            cursor.execute(
                """
                INSERT INTO regulaite_settings (setting_key, setting_value)
                VALUES (?, ?)
                ON DUPLICATE KEY UPDATE setting_value = ?
                """,
                (setting_key, str(value), str(value))
            )

        conn.commit()
        conn.close()

        # Update log level if it was changed
        if "log_level" in updates:
            try:
                log_level = getattr(logging, updates["log_level"].upper())
                logging.getLogger().setLevel(log_level)
                logger.info(f"Updated log level to {updates['log_level'].upper()}")
            except (AttributeError, TypeError):
                logger.warning(f"Invalid log level: {updates['log_level']}")

        # Reload configuration from database to return the updated values
        return (await get_all_config()).system

    except Exception as e:
        logger.error(f"Error updating system configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating system configuration: {str(e)}"
        )


@router.get("/exported", response_model=Dict[str, Any])
async def export_config():
    """Export all configuration as a single JSON object for backup."""
    try:
        conn = await get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT setting_key, setting_value, created_at, updated_at
            FROM regulaite_settings
            """
        )

        # Format the results for export
        settings = {}
        for row in cursor.fetchall():
            # Convert timestamps to ISO format strings
            created = row['created_at'].isoformat() if row['created_at'] else None
            updated = row['updated_at'].isoformat() if row['updated_at'] else None

            settings[row['setting_key']] = {
                "value": row['setting_value'],
                "created_at": created,
                "updated_at": updated
            }

        conn.close()

        return {
            "settings": settings,
            "exported_at": datetime.now().isoformat(),
            "version": "1.0"
        }

    except Exception as e:
        logger.error(f"Error exporting configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting configuration: {str(e)}"
        )


@router.post("/import")
async def import_config(config_data: Dict[str, Any] = Body(...)):
    """Import configuration from a previously exported JSON object."""
    try:
        if "settings" not in config_data:
            raise HTTPException(
                status_code=400,
                detail="Invalid configuration data: 'settings' field is missing"
            )

        conn = await get_db_connection()
        cursor = conn.cursor()

        # Begin transaction
        cursor.execute("START TRANSACTION")

        try:
            settings = config_data["settings"]
            imported_count = 0

            for key, data in settings.items():
                if "value" not in data:
                    logger.warning(f"Skipping setting {key}: missing 'value' field")
                    continue

                value = data["value"]

                cursor.execute(
                    """
                    INSERT INTO regulaite_settings (setting_key, setting_value)
                    VALUES (?, ?)
                    ON DUPLICATE KEY UPDATE setting_value = ?
                    """,
                    (key, str(value), str(value))
                )

                imported_count += 1

            # Commit transaction
            cursor.execute("COMMIT")
            conn.close()

            return {
                "success": True,
                "imported_count": imported_count,
                "message": f"Successfully imported {imported_count} configuration settings"
            }

        except Exception as e:
            # Rollback on error
            cursor.execute("ROLLBACK")
            conn.close()
            raise e

    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error importing configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error importing configuration: {str(e)}"
        )


@router.get("/reset", response_model=Dict[str, Any])
async def reset_config(section: Optional[str] = None):
    """Reset configuration to defaults.

    Args:
        section: Optional section to reset (llm, rag, ui, system). If not provided, resets all settings.
    """
    try:
        # Define default settings for each section
        defaults = {
            "llm": {
                "llm_model": "gpt-4",
                "llm_temperature": "0.7",
                "llm_max_tokens": "2048",
                "llm_top_p": "1.0",
                "llm_frequency_penalty": "0.0",
                "llm_presence_penalty": "0.0"
            },
            "rag": {
                "rag_hybrid_search": "true",
                "rag_vector_weight": "0.7",
                "rag_semantic_weight": "0.3",
                "rag_default_top_k": "5",
                "rag_reranking_enabled": "false",
                "rag_embedding_model": "text-embedding-ada-002",
                "rag_embedding_dim": "1536"
            },
            "ui": {
                "ui_theme": "system",
                "ui_primary_color": "#0077CC",
                "ui_accent_color": "#00AAFF",
                "ui_app_name": "RegulAite",
                "ui_default_page": "dashboard",
                "ui_hide_experimental": "false"
            },
            "system": {
                "system_debug_mode": "false",
                "system_log_level": "INFO",
                "system_max_concurrent_tasks": "5",
                "system_task_timeout_seconds": "300",
                "system_enable_telemetry": "true",
                "system_api_rate_limit": "100",
                "system_maintenance_mode": "false"
            }
        }

        conn = await get_db_connection()
        cursor = conn.cursor()

        # Begin transaction
        cursor.execute("START TRANSACTION")

        try:
            reset_count = 0

            if section:
                if section not in defaults:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid section: {section}. Must be one of: llm, rag, ui, system"
                    )

                # Reset only the specified section
                section_defaults = defaults[section]

                for key, value in section_defaults.items():
                    cursor.execute(
                        """
                        INSERT INTO regulaite_settings (setting_key, setting_value)
                        VALUES (?, ?)
                        ON DUPLICATE KEY UPDATE setting_value = ?
                        """,
                        (key, value, value)
                    )
                    reset_count += 1

            else:
                # Reset all settings
                for section_defaults in defaults.values():
                    for key, value in section_defaults.items():
                        cursor.execute(
                            """
                            INSERT INTO regulaite_settings (setting_key, setting_value)
                            VALUES (?, ?)
                            ON DUPLICATE KEY UPDATE setting_value = ?
                            """,
                            (key, value, value)
                        )
                        reset_count += 1

            # Commit transaction
            cursor.execute("COMMIT")
            conn.close()

            return {
                "success": True,
                "reset_count": reset_count,
                "message": f"Successfully reset {section or 'all'} configuration settings ({reset_count} settings)"
            }

        except Exception as e:
            # Rollback on error
            cursor.execute("ROLLBACK")
            conn.close()
            raise e

    except HTTPException as he:
        # Re-raise HTTP exceptions
        raise he
    except Exception as e:
        logger.error(f"Error resetting configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error resetting configuration: {str(e)}"
        )
