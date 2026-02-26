"""
Agent Orchestrateur Principal pour RegulAIte avec capacités itératives.
Analyse les requêtes en français et délègue aux agents spécialisés avec iteration sur documents.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import time

from .agent import Agent, AgentResponse, Query, QueryContext
from .integrations.llm_integration import LLMIntegration
from .agent_logger import AgentLogger, ActivityType, ActivityStatus, LogLevel

# Backward compatibility alias
LLMClient = LLMIntegration

logger = logging.getLogger(__name__)

def _make_json_serializable(obj):
    """
    Recursively converts an object into a JSON-serializable format.
    """
    if obj is None:
        return None
    
    try:
        # Test if already serializable
        json.dumps(obj)
        return obj
    except (TypeError, ValueError):
        pass
    
    # Handle different types
    if hasattr(obj, 'model_dump'):
        # Pydantic models
        return obj.model_dump()
    elif isinstance(obj, dict):
        # Dictionary - recursively process values
        result = {}
        for key, value in obj.items():
            result[key] = _make_json_serializable(value)
        return result
    elif isinstance(obj, (list, tuple)):
        # List/tuple - recursively process items
        return [_make_json_serializable(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool)):
        # Primitive types
        return obj
    else:
        # Convert to string as fallback
        return str(obj)

class IterationContext:
    """Contexte pour gérer les itérations d'analyse."""
    
    def __init__(self, max_iterations: int = 2):
        self.iteration_count = 0
        self.max_iterations = max_iterations
        self.previous_queries = []
        self.previous_results = []
        self.context_gaps = []
        self.reformulated_queries = []
        self.document_analysis_history = []
        self.knowledge_gained = []
        
    def add_iteration(self, query: str, results: Dict[str, Any], gaps: List[str]):
        """Ajoute une itération au contexte."""
        self.iteration_count += 1
        self.previous_queries.append(query)
        self.previous_results.append(results)
        self.context_gaps.extend(gaps)
        
    def should_continue_iteration(self) -> bool:
        """Détermine si on doit continuer les itérations."""
        # Always allow the first iteration
        if self.iteration_count == 0:
            return True
        
        # Don't iterate if we've reached max iterations
        if self.iteration_count >= self.max_iterations:
            return False
            
        # Don't iterate if no significant context gaps
        if len(self.context_gaps) == 0:
            return False
            
        # Don't iterate if we've seen the same gaps repeatedly (avoid loops)
        recent_gaps = set(self.context_gaps[-3:]) if len(self.context_gaps) >= 3 else set()
        if len(recent_gaps) <= 1 and self.iteration_count > 1:
            return False
            
        # Continue only if we have meaningful gaps to address
        return True
    
    def get_iteration_summary(self) -> Dict[str, Any]:
        """Retourne un résumé des itérations."""
        return {
            "total_iterations": self.iteration_count,
            "queries_tried": self.previous_queries,
            "gaps_identified": self.context_gaps,
            "reformulations": self.reformulated_queries,
            "knowledge_progression": self.knowledge_gained
        }

class OrchestratorAgent(Agent):
    """
    Agent orchestrateur principal qui analyse les requêtes et coordonne 
    les agents spécialisés pour les analyses GRC avec capacités itératives.
    """
    
    def __init__(self, llm_client: LLMClient, log_callback=None):
        super().__init__(
            agent_id="orchestrator", 
            name="Orchestrateur Principal GRC Itératif"
        )
        
        self.llm_client = llm_client
        self.specialized_agents: Dict[str, Agent] = {}
        self.agent_logger = None  # Will be initialized per session
        self.log_callback = log_callback
        
        # Prompts spécialisés pour l'orchestration itérative
        self.system_prompt = """
Tu es l'orchestrateur principal d'un système d'analyse GRC (Gouvernance, Risque, Conformité) avec capacités itératives.
Tu communiques en français et analyses les demandes pour déterminer quels agents spécialisés mobiliser.

CAPACITÉS ITÉRATIVES:
- Analyse du contexte manquant après chaque étape
- Reformulation automatique des requêtes pour combler les gaps
- Iteration sur les documents pour approfondir l'analyse
- Synthèse progressive des connaissances acquises

Agents disponibles:
1. risk_assessment - Analyse des risques (identification, évaluation, traitement)
2. compliance_analysis - Analyse de conformité (RGPD, ISO 27001, DORA)  
3. governance_analysis - Analyse de gouvernance (politiques, procédures, contrôles)
4. gap_analysis - Analyse des écarts et recommandations

Outils universels disponibles:
- document_finder - Recherche intelligente de documents
- entity_extractor - Extraction d'entités GRC
- cross_reference - Liens entre documents/contrôles
- temporal_analyzer - Analyse des tendances temporelles

PROCESSUS ITÉRATIF:
1. Analyser la demande utilisateur
2. Déterminer quels agents/outils mobiliser
3. Exécuter l'analyse initiale
4. Identifier les gaps de contexte
5. Reformuler la requête si nécessaire
6. Itérer jusqu'à satisfaction ou limite atteinte
7. Synthétiser tous les résultats

Réponds TOUJOURS en français avec un plan d'action structuré.
"""

    def register_agent(self, agent_id: str, agent: Agent):
        """Enregistre un agent spécialisé."""
        self.specialized_agents[agent_id] = agent
        logger.info(f"Agent {agent_id} enregistré dans l'orchestrateur")

    def get_registered_agents(self) -> Dict[str, str]:
        """Retourne un dictionnaire des agents enregistrés avec leurs noms."""
        return {
            agent_id: getattr(agent, 'name', f'Agent {agent_id}')
            for agent_id, agent in self.specialized_agents.items()
        }

    def debug_agent_status(self):
        """Debug method to log current agent status."""
        logger.info(f"Orchestrator {self.agent_id} has {len(self.specialized_agents)} agents registered:")
        for agent_id, agent in self.specialized_agents.items():
            agent_name = getattr(agent, 'name', 'Unknown')
            agent_type = type(agent).__name__
            logger.info(f"  - {agent_id}: {agent_name} ({agent_type})")
        return self.specialized_agents

    async def process_query(self, query: Union[str, Query]) -> AgentResponse:
        """
        Traite une requête utilisateur et orchestre les agents appropriés avec iteration.
        """
        if isinstance(query, str):
            query = Query(query_text=query)
        
        # Initialize detailed logger for this session
        session_id = query.context.session_id if query.context else None
        self.agent_logger = AgentLogger(session_id=session_id, callback=self.log_callback)
        
        start_time = time.time()
        logger.info(f"Orchestrateur - Analyse itérative de la requête: {query.query_text}")
        
        # Log query analysis start
        await self.agent_logger.log_query_analysis(
            agent_id=self.agent_id,
            agent_name=self.name,
            query=query.query_text,
            analysis_result={"status": "starting", "query_length": len(query.query_text)}
        )
        
        # Initialiser le contexte d'itération
        iteration_context = IterationContext()
        
        # Analyse initiale de la requête
        analysis_start = time.time()
        analysis_result = await self._analyze_request(query.query_text)
        analysis_time = (time.time() - analysis_start) * 1000
        
        # Log detailed query analysis
        await self.agent_logger.log_query_analysis(
            agent_id=self.agent_id,
            agent_name=self.name,
            query=query.query_text,
            analysis_result=analysis_result,
            execution_time_ms=analysis_time
        )
        
        # Boucle d'itération pour raffiner l'analyse
        while iteration_context.should_continue_iteration():
            iteration_num = iteration_context.iteration_count + 1
            
            # Log iteration start
            await self.agent_logger.log_iteration(
                agent_id=self.agent_id,
                agent_name=self.name,
                iteration_number=iteration_num,
                reason_for_iteration="Identified context gaps requiring deeper analysis",
                context_gaps=iteration_context.context_gaps
            )
            
            # Exécuter le plan d'action
            execution_start = time.time()
            execution_results = await self._execute_plan_with_iteration(
                analysis_result, query, iteration_context
            )
            execution_time = (time.time() - execution_start) * 1000
            
            # Log agent selection and execution
            if analysis_result.get("agents_requis"):
                await self.agent_logger.log_agent_selection(
                    orchestrator_id=self.agent_id,
                    selected_agents=analysis_result["agents_requis"],
                    reasoning=f"Iteration {iteration_num}: Selected agents based on current context gaps",
                    execution_time_ms=execution_time
                )
            
            # Analyser les gaps de contexte
            gap_analysis_start = time.time()
            context_gaps = await self._identify_context_gaps(
                query.query_text, analysis_result, execution_results, iteration_context
            )
            gap_analysis_time = (time.time() - gap_analysis_start) * 1000
            
            # Log decision making about context gaps
            await self.agent_logger.log_decision_making(
                agent_id=self.agent_id,
                agent_name=self.name,
                decision_context=f"Analysis of iteration {iteration_num} results",
                decision_made=f"Identified {len(context_gaps)} context gaps" if context_gaps else "No significant context gaps found",
                reasoning=f"Analyzed execution results and found areas needing clarification: {context_gaps}" if context_gaps else "Results appear comprehensive",
                confidence=0.8 if not context_gaps else 0.6,
                alternatives_considered=["Continue with current results", "Perform additional iteration"]
            )
            
            # Ajouter cette itération au contexte
            iteration_context.add_iteration(
                query.query_text, execution_results, context_gaps
            )
            
            # Si des gaps sont identifiés, reformuler la requête
            if context_gaps and iteration_context.should_continue_iteration():
                reformulation_start = time.time()
                reformulated_query = await self._reformulate_query(
                    query.query_text, context_gaps, iteration_context
                )
                reformulation_time = (time.time() - reformulation_start) * 1000
                
                if reformulated_query:
                    iteration_context.reformulated_queries.append(reformulated_query)
                    query.query_text = reformulated_query
                    logger.info(f"Requête reformulée (itération {iteration_context.iteration_count}): {reformulated_query}")
                    
                    # Log the reformulation
                    await self.agent_logger.log_activity(
                        agent_id=self.agent_id,
                        agent_name=self.name,
                        activity_type=ActivityType.QUERY_ANALYSIS,
                        status=ActivityStatus.COMPLETED,
                        level=LogLevel.INFO,
                        message=f"Reformulated query for iteration {iteration_num}",
                        details={
                            "original_query": query.query_text,
                            "reformulated_query": reformulated_query,
                            "context_gaps_addressed": context_gaps,
                            "iteration_number": iteration_num
                        },
                        execution_time_ms=reformulation_time
                    )
                    
                    # Réanalyser avec la requête reformulée
                    analysis_result = await self._analyze_request(reformulated_query)
                else:
                    break
            else:
                break
        
        # Synthèse finale avec tout le contexte itératif
        synthesis_start = time.time()
        final_response = await self._synthesize_iterative_results(
            query.query_text, analysis_result, iteration_context
        )
        synthesis_time = (time.time() - synthesis_start) * 1000
        total_processing_time = (time.time() - start_time) * 1000
        
        # Log final synthesis
        synthesis_inputs = {
            "sources": self._aggregate_all_sources(iteration_context),
            "agent_results": self._get_all_agents_used(iteration_context),
            "total_iterations": iteration_context.iteration_count,
            "context_gaps_resolved": len(iteration_context.context_gaps)
        }
        
        await self.agent_logger.log_activity(
            agent_id=self.agent_id,
            agent_name=self.name,
            activity_type=ActivityType.SYNTHESIS,
            status=ActivityStatus.COMPLETED,
            level=LogLevel.INFO,
            message="Synthesized final response from all processing steps",
            details={
                "synthesis_inputs": synthesis_inputs,
                "final_response_length": len(final_response),
                "sources_integrated": len(synthesis_inputs.get("sources", [])),
                "agents_contributing": len(synthesis_inputs.get("agent_results", [])),
                "iterations_completed": synthesis_inputs.get("total_iterations", 0),
                "total_processing_time_ms": total_processing_time
            },
            execution_time_ms=synthesis_time
        )
        
        # Get session summary for metadata
        session_summary = self.agent_logger.get_session_summary()
        
        return AgentResponse(
            content=final_response,
            tools_used=analysis_result.get("tools_used", []),
            context_used=True,
            sources=self._aggregate_all_sources(iteration_context),
            metadata={
                "orchestration_plan": analysis_result,
                "iteration_summary": iteration_context.get_iteration_summary(),
                "agents_involved": self._get_all_agents_used(iteration_context),
                "total_iterations": iteration_context.iteration_count,
                "context_gaps_resolved": len(iteration_context.context_gaps),
                "detailed_logs": session_summary,
                "total_processing_time_ms": total_processing_time,
                "agent_performance": session_summary.get("agent_performance", {}),
                "activity_timeline": session_summary.get("timeline", [])
            }
        )

    async def _analyze_request(self, user_query: str) -> Dict[str, Any]:
        """
        Analyse la requête utilisateur pour déterminer le plan d'action.
        """
        # Log the start of request analysis
        if self.agent_logger:
            await self.agent_logger.log_activity(
                agent_id=self.agent_id,
                agent_name=self.name,
                activity_type=ActivityType.QUERY_ANALYSIS,
                status=ActivityStatus.STARTED,
                level=LogLevel.INFO,
                message="Starting detailed query analysis",
                details={
                    "query": user_query,
                    "step": "request_analysis_start"
                }
            )

        analysis_prompt = f"""
Analyse cette demande utilisateur et crée un plan d'action:

DEMANDE: "{user_query}"

Réponds au format JSON avec:
{{
    "type_analyse": "risk_assessment|compliance_analysis|governance_analysis|mixed",
    "frameworks_concernes": ["ISO27001", "RGPD", "DORA", "autres"],
    "agents_requis": [
        {{
            "agent_id": "nom_agent",
            "priorite": 1-3,
            "objectif": "description_objectif",
            "outils_necessaires": ["document_finder", "entity_extractor", ...]
        }}
    ],
    "collaboration_requise": true/false,
    "sequence_execution": [
        {{
            "etape": 1,
            "action": "description",
            "agent": "agent_id",
            "dependances": ["etape_precedente"]
        }}
    ],
    "objectif_final": "description_synthese_attendue"
}}
"""

        # Log the LLM prompt being sent
        if self.agent_logger:
            await self.agent_logger.log_activity(
                agent_id=self.agent_id,
                agent_name=self.name,
                activity_type=ActivityType.QUERY_ANALYSIS,
                status=ActivityStatus.IN_PROGRESS,
                level=LogLevel.INFO,
                message="Sending analysis prompt to LLM",
                details={
                    "llm_prompt": analysis_prompt,
                    "system_prompt": self.system_prompt,
                    "model": "gpt-4.1",
                    "temperature": 0.1,
                    "step": "llm_prompt_send"
                }
            )

        try:
            llm_start = time.time()
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": analysis_prompt}
                ],
                model="gpt-4.1",
                temperature=0.1
            )
            llm_time = (time.time() - llm_start) * 1000
            
            # Log the LLM response received
            if self.agent_logger:
                await self.agent_logger.log_activity(
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    activity_type=ActivityType.QUERY_ANALYSIS,
                    status=ActivityStatus.IN_PROGRESS,
                    level=LogLevel.INFO,
                    message="Received LLM response for query analysis",
                    details={
                        "llm_response": response,
                        "response_length": len(response),
                        "step": "llm_response_received"
                    },
                    execution_time_ms=llm_time
                )
            
            # Extraire le JSON de la réponse
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_content = response[json_start:json_end]
            
            parsed_result = json.loads(json_content)
            
            # Log successful parsing
            if self.agent_logger:
                await self.agent_logger.log_activity(
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    activity_type=ActivityType.QUERY_ANALYSIS,
                    status=ActivityStatus.COMPLETED,
                    level=LogLevel.INFO,
                    message="Successfully parsed analysis result",
                    details={
                        "parsed_result": parsed_result,
                        "json_extracted": json_content,
                        "step": "analysis_complete"
                    }
                )
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de la requête: {str(e)}")
            # Plan de fallback
            return {
                "type_analyse": "mixed",
                "frameworks_concernes": ["ISO27001", "RGPD"],
                "agents_requis": [
                    {
                        "agent_id": "compliance_analysis",
                        "priorite": 1,
                        "objectif": "Analyse générale",
                        "outils_necessaires": ["document_finder", "entity_extractor"]
                    }
                ],
                "collaboration_requise": False,
                "sequence_execution": [
                    {
                        "etape": 1,
                        "action": "Analyse de conformité",
                        "agent": "compliance_analysis",
                        "dependances": []
                    }
                ],
                "objectif_final": "Analyse GRC générale"
            }

    async def _execute_plan_with_iteration(self, analysis: Dict[str, Any], 
                                         original_query: Query, 
                                         iteration_context: IterationContext) -> Dict[str, Any]:
        """
        Exécute le plan d'action en orchestrant les agents appropriés avec contexte itératif.
        """
        # Log execution plan start
        if self.agent_logger:
            await self.agent_logger.log_activity(
                agent_id=self.agent_id,
                agent_name=self.name,
                activity_type=ActivityType.TOOL_EXECUTION,
                status=ActivityStatus.STARTED,
                level=LogLevel.INFO,
                message="Starting execution of orchestrated plan",
                details={
                    "analysis_plan": analysis,
                    "iteration": iteration_context.iteration_count + 1,
                    "previous_knowledge": iteration_context.knowledge_gained[-5:] if iteration_context.knowledge_gained else [],
                    "step": "plan_execution_start"
                }
            )

        results = {
            "agent_results": {},
            "all_sources": [],
            "detailed_sources": [],  # Sources détaillées pour visibilité utilisateur
            "summary": {},
            "errors": [],
            "iteration_info": {
                "current_iteration": iteration_context.iteration_count + 1,
                "previous_knowledge": iteration_context.knowledge_gained[-5:] if iteration_context.knowledge_gained else []
            }
        }
        
        try:
            # Trier les étapes par ordre d'exécution
            execution_sequence = sorted(
                analysis.get("sequence_execution", []),
                key=lambda x: x.get("etape", 0)
            )
            
            # Log execution sequence
            if self.agent_logger:
                await self.agent_logger.log_activity(
                    agent_id=self.agent_id,
                    agent_name=self.name,
                    activity_type=ActivityType.TOOL_EXECUTION,
                    status=ActivityStatus.IN_PROGRESS,
                    level=LogLevel.INFO,
                    message="Prepared execution sequence",
                    details={
                        "execution_sequence": execution_sequence,
                        "total_steps": len(execution_sequence),
                        "step": "execution_sequence_prepared"
                    }
                )
            
            for step in execution_sequence:
                agent_id = step.get("agent")
                action = step.get("action")
                step_number = step.get('etape', 0)
                
                logger.info(f"Exécution étape {step_number} (itération {iteration_context.iteration_count + 1}): {action} avec {agent_id}")
                
                # Log individual step start
                if self.agent_logger:
                    await self.agent_logger.log_activity(
                        agent_id=self.agent_id,
                        agent_name=self.name,
                        activity_type=ActivityType.TOOL_EXECUTION,
                        status=ActivityStatus.IN_PROGRESS,
                        level=LogLevel.INFO,
                        message=f"Executing step {step_number}: {action}",
                        details={
                            "step_info": step,
                            "target_agent": agent_id,
                            "action": action,
                            "iteration": iteration_context.iteration_count + 1,
                            "step": f"step_{step_number}_start"
                        }
                    )
                
                # Debug logging for agent lookup
                logger.info(f"Looking for agent '{agent_id}'. Available agents: {list(self.specialized_agents.keys())}")
                
                if agent_id in self.specialized_agents:
                    try:
                        # Préparer le contexte enrichi pour l'agent spécialisé
                        context = QueryContext(
                            session_id=original_query.context.session_id,
                            metadata=_make_json_serializable({
                                "orchestrator_plan": analysis,
                                "step_info": step,
                                "previous_results": results["agent_results"],
                                "iteration_context": {
                                    "current_iteration": iteration_context.iteration_count + 1,
                                    "previous_queries": iteration_context.previous_queries,
                                    "previous_results": iteration_context.previous_results,
                                    "identified_gaps": iteration_context.context_gaps,
                                    "knowledge_progression": iteration_context.knowledge_gained
                                }
                            })
                        )
                        
                        # Créer une requête enrichie pour l'agent avec contexte itératif
                        enriched_query = Query(
                            query_text=original_query.query_text,
                            context=context,
                            parameters={
                                "specific_objective": step.get("objectif", action),
                                "required_tools": step.get("outils_necessaires", []),
                                "frameworks": analysis.get("frameworks_concernes", []),
                                "iteration_mode": True,
                                "previous_findings": iteration_context.knowledge_gained,
                                "focus_areas": iteration_context.context_gaps
                            }
                        )
                        
                        # Log agent execution start
                        if self.agent_logger:
                            await self.agent_logger.log_activity(
                                agent_id=agent_id,
                                agent_name=f"Specialized Agent: {agent_id}",
                                activity_type=ActivityType.TOOL_EXECUTION,
                                status=ActivityStatus.STARTED,
                                level=LogLevel.INFO,
                                message=f"Starting execution of {agent_id} agent",
                                details=_make_json_serializable({
                                    "enriched_query": enriched_query.query_text,
                                    "query_parameters": enriched_query.parameters,
                                    "context_metadata": enriched_query.context.metadata if enriched_query.context else {},
                                    "step": f"agent_{agent_id}_execution_start"
                                })
                            )

                        # Exécuter l'agent spécialisé avec contexte itératif
                        agent_start_time = time.time()
                        agent_response = await self.specialized_agents[agent_id].process_query(enriched_query)
                        agent_execution_time = (time.time() - agent_start_time) * 1000
                        
                        # Log agent execution completion
                        if self.agent_logger:
                            await self.agent_logger.log_activity(
                                agent_id=agent_id,
                                agent_name=f"Specialized Agent: {agent_id}",
                                activity_type=ActivityType.TOOL_EXECUTION,
                                status=ActivityStatus.COMPLETED,
                                level=LogLevel.INFO,
                                message=f"Completed execution of {agent_id} agent",
                                details={
                                    "agent_response": {
                                        "content": agent_response.content,
                                        "content_length": len(agent_response.content),
                                        "tools_used": agent_response.tools_used,
                                        "sources_count": len(agent_response.sources),
                                        "confidence": agent_response.confidence
                                    },
                                    "step": f"agent_{agent_id}_execution_complete"
                                },
                                execution_time_ms=agent_execution_time
                            )
                        
                        results["agent_results"][agent_id] = {
                            "response": agent_response.content,
                            "tools_used": agent_response.tools_used,
                            "sources": agent_response.sources,
                            "confidence": agent_response.confidence,
                            "step_info": step,
                            "iteration": iteration_context.iteration_count + 1,
                            "execution_time_ms": agent_execution_time
                        }
                        
                        # Agréger les sources avec détails pour visibilité utilisateur
                        results["all_sources"].extend(agent_response.sources)
                        
                        # Ajouter sources détaillées avec contexte d'itération
                        for source in agent_response.sources:
                            detailed_source = {
                                "source": source,
                                "agent": agent_id,
                                "iteration": iteration_context.iteration_count + 1,
                                "step": step.get("etape", 0),
                                "action": action,
                                "timestamp": datetime.now().isoformat(),
                                "tools_used": agent_response.tools_used
                            }
                            results["detailed_sources"].append(detailed_source)
                        
                        # Extraire les nouvelles connaissances acquises
                        new_knowledge = await self._extract_knowledge_from_response(agent_response)
                        iteration_context.knowledge_gained.extend(new_knowledge)
                        
                    except Exception as e:
                        error_msg = f"Erreur lors de l'exécution de {agent_id} (itération {iteration_context.iteration_count + 1}): {str(e)}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                else:
                    error_msg = f"Agent {agent_id} non trouvé"
                    logger.warning(error_msg)
                    results["errors"].append(error_msg)
            
            # Résumé de l'exécution avec informations itératives
            results["summary"] = {
                "total_steps": len(execution_sequence),
                "successful_agents": len(results["agent_results"]),
                "total_sources": len(results["all_sources"]),
                "detailed_sources_count": len(results["detailed_sources"]),
                "errors_count": len(results["errors"]),
                "iteration": iteration_context.iteration_count + 1,
                "knowledge_items_gained": len(iteration_context.knowledge_gained)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du plan: {str(e)}")
            results["errors"].append(f"Erreur d'orchestration: {str(e)}")
            
        return results

    async def _identify_context_gaps(self, original_query: str, analysis: Dict[str, Any], 
                                   execution_results: Dict[str, Any], 
                                   iteration_context: IterationContext) -> List[str]:
        """
        Identifie les gaps de contexte qui nécessitent une itération supplémentaire.
        """
        gap_analysis_prompt = f"""
Analyse les résultats de cette analyse GRC pour identifier UNIQUEMENT les gaps de contexte CRITIQUES qui nécessitent absolument plus d'information.

REQUÊTE ORIGINALE: "{original_query}"

ITÉRATION ACTUELLE: {iteration_context.iteration_count + 1}

RÉSULTATS OBTENUS:
{json.dumps(_make_json_serializable(execution_results.get("agent_results", {})), indent=2, ensure_ascii=False)}

CONNAISSANCES ACQUISES PRÉCÉDEMMENT:
{iteration_context.knowledge_gained}

GAPS IDENTIFIÉS PRÉCÉDEMMENT:
{iteration_context.context_gaps}

CRITÈRES STRICTS pour identifier un gap critique:
1. Information ESSENTIELLE manquante pour répondre à la question principale
2. Contradiction MAJEURE nécessitant clarification urgente
3. Aspect FONDAMENTAL de la question complètement non couvert
4. Données QUANTITATIVES manquantes quand nécessaires pour l'évaluation

NE PAS considérer comme gaps:
- Détails supplémentaires qui enrichiraient seulement la réponse
- Informations contextuelles non essentielles
- Aspects déjà partiellement couverts
- Questions hypothétiques ou prospectives
- Répétitions des gaps précédents

Sois TRÈS CONSERVATEUR. Préfère retourner [] si les résultats sont suffisants pour répondre à la question principale.

Réponds avec une liste JSON des gaps CRITIQUES uniquement:
["gap_critique_1", "gap_critique_2"]

Si aucun gap critique, réponds: []
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": gap_analysis_prompt}
                ],
                model="gpt-4.1",
                temperature=0.2
            )
            
            # Extraire la liste JSON
            if response.strip().startswith('[') and response.strip().endswith(']'):
                gaps = json.loads(response.strip())
                return gaps
            else:
                # Chercher une liste JSON dans la réponse
                import re
                json_match = re.search(r'\[.*?\]', response, re.DOTALL)
                if json_match:
                    gaps = json.loads(json_match.group())
                    return gaps
                
            return []
            
        except Exception as e:
            logger.error(f"Erreur lors de l'identification des gaps: {str(e)}")
            return []

    async def _reformulate_query(self, original_query: str, context_gaps: List[str], 
                               iteration_context: IterationContext) -> Optional[str]:
        """
        Reformule la requête pour combler les gaps de contexte identifiés.
        """
        if not context_gaps:
            return None
            
        reformulation_prompt = f"""
Reformule cette requête GRC pour combler les gaps de contexte identifiés.

REQUÊTE ORIGINALE: "{original_query}"

ITÉRATION: {iteration_context.iteration_count + 1}

GAPS À COMBLER:
{chr(10).join(f"- {gap}" for gap in context_gaps)}

REQUÊTES PRÉCÉDENTES:
{chr(10).join(f"Itération {i+1}: {q}" for i, q in enumerate(iteration_context.previous_queries))}

CONNAISSANCES ACQUISES:
{iteration_context.knowledge_gained}

Créé une nouvelle formulation qui:
1. Conserve l'intention originale
2. Cible spécifiquement les gaps identifiés
3. Utilise les connaissances déjà acquises
4. Est plus précise et focalisée
5. Évite la redondance avec les requêtes précédentes

Réponds UNIQUEMENT avec la nouvelle formulation de la requête, sans explication.
"""

        try:
            reformulated = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": reformulation_prompt}
                ],
                model="gpt-4.1",
                temperature=0.3
            )
            
            return reformulated.strip()
            
        except Exception as e:
            logger.error(f"Erreur lors de la reformulation: {str(e)}")
            return None

    async def _extract_knowledge_from_response(self, agent_response: AgentResponse) -> List[str]:
        """
        Extrait les nouvelles connaissances acquises de la réponse d'un agent.
        """
        knowledge_extraction_prompt = f"""
Extrait les principales connaissances/insights de cette réponse d'analyse GRC.

RÉPONSE À ANALYSER:
{agent_response.content}

SOURCES UTILISÉES:
{agent_response.sources}

Identifie les connaissances clés acquises:
1. Faits nouveaux découverts
2. Conclusions importantes
3. Risques identifiés
4. Contrôles trouvés
5. Gaps de conformité
6. Recommandations

Réponds avec une liste JSON de phrases courtes représentant chaque connaissance:
["connaissance1", "connaissance2", "connaissance3"]
"""

        try:
            response = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": "Tu es un expert en extraction de connaissances GRC."},
                    {"role": "user", "content": knowledge_extraction_prompt}
                ],
                model="gpt-4.1",
                temperature=0.1
            )
            
            # Extraire la liste JSON
            if response.strip().startswith('[') and response.strip().endswith(']'):
                knowledge = json.loads(response.strip())
                return knowledge
            else:
                # Chercher une liste JSON dans la réponse
                import re
                json_match = re.search(r'\[.*?\]', response, re.DOTALL)
                if json_match:
                    knowledge = json.loads(json_match.group())
                    return knowledge
                
            return []
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction de connaissances: {str(e)}")
            return []

    async def _synthesize_iterative_results(self, original_query: str, analysis: Dict[str, Any], 
                                          iteration_context: IterationContext) -> str:
        """
        Synthétise les résultats de toutes les itérations en une réponse cohérente avec sources visibles.
        """
        # Compiler toutes les sources détaillées de toutes les itérations
        all_detailed_sources = []
        for results in iteration_context.previous_results:
            all_detailed_sources.extend(results.get("detailed_sources", []))
        
        # Organiser les sources par itération pour visibilité
        sources_by_iteration = {}
        for source in all_detailed_sources:
            iteration = source.get("iteration", 0)
            if iteration not in sources_by_iteration:
                sources_by_iteration[iteration] = []
            sources_by_iteration[iteration].append(source)
        
        synthesis_prompt = f"""
Tu dois synthétiser les résultats d'une analyse GRC multi-agents avec {iteration_context.iteration_count} itérations.

DEMANDE ORIGINALE: "{original_query}"

PROGRESSION ITÉRATIVE:
{json.dumps(_make_json_serializable(iteration_context.get_iteration_summary()), indent=2, ensure_ascii=False)}

CONNAISSANCES ACQUISES:
{chr(10).join(f"- {k}" for k in iteration_context.knowledge_gained)}

SOURCES CONSULTÉES PAR ITÉRATION:
{self._format_sources_for_synthesis(sources_by_iteration)}

TOUS LES RÉSULTATS:
{json.dumps(_make_json_serializable(iteration_context.previous_results), indent=2, ensure_ascii=False)}

Crée une synthèse complète et structurée en français qui:
1. Répond directement à la demande utilisateur
2. Intègre TOUTES les analyses des itérations
3. Montre la progression des connaissances
4. Présente les findings finaux
5. Identifie les gaps résiduels s'il y en a
6. Fournit des recommandations actionables
7. Structure la réponse de manière claire et professionnelle
8. INCLUT une section "SOURCES CONSULTÉES" détaillée montrant:
   - Toutes les sources utilisées par itération
   - Les outils mobilisés à chaque étape
   - La progression de l'analyse documentaire
   - La traçabilité complète des informations

La réponse doit être adaptée à un contexte GRC et montrer clairement la valeur ajoutée de l'approche itérative avec TRANSPARENCE TOTALE sur les sources.
"""

        try:
            synthesis = await self.llm_client.generate_response(
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": synthesis_prompt}
                ],
                model="gpt-4.1",
                temperature=0.2
            )
            
            # Ajouter une section sources détaillées à la fin de la synthèse
            sources_section = self._create_detailed_sources_section(sources_by_iteration)
            final_synthesis = f"{synthesis}\n\n{sources_section}"
            
            return final_synthesis
            
        except Exception as e:
            logger.error(f"Erreur lors de la synthèse itérative: {str(e)}")
            
            # Synthèse de fallback avec sources visibles
            fallback_response = f"""
# Analyse GRC Itérative - Synthèse

## Demande analysée
{original_query}

## Progression itérative ({iteration_context.iteration_count} itérations)
"""
            
            for i, (query, results) in enumerate(zip(iteration_context.previous_queries, iteration_context.previous_results)):
                fallback_response += f"""
### Itération {i + 1}
**Requête**: {query}
**Résultats obtenus**: {len(results.get('agent_results', {}))} analyses
**Sources consultées**: {len(results.get('detailed_sources', []))}
"""
            
            fallback_response += f"""
## Connaissances acquises
{chr(10).join(f"- {k}" for k in iteration_context.knowledge_gained)}

## Gaps résiduels
{chr(10).join(f"- {gap}" for gap in iteration_context.context_gaps)}

{self._create_detailed_sources_section(sources_by_iteration)}
"""
            
            return fallback_response

    def _format_sources_for_synthesis(self, sources_by_iteration: Dict[int, List[Dict[str, Any]]]) -> str:
        """Formate les sources par itération pour la synthèse LLM."""
        formatted = ""
        for iteration, sources in sources_by_iteration.items():
            formatted += f"\nItération {iteration}:\n"
            for source in sources:
                source_info = source.get("source", {})
                if isinstance(source_info, dict):
                    source_name = source_info.get("title", source_info.get("name", source_info.get("id", "Source inconnue")))
                else:
                    source_name = str(source_info)
                
                formatted += f"  - {source_name} (via {source.get('agent', 'agent')}, outils: {', '.join(source.get('tools_used', []))})\n"
        
        return formatted

    def _create_detailed_sources_section(self, sources_by_iteration: Dict[int, List[Dict[str, Any]]]) -> str:
        """Crée une section détaillée des sources pour la visibilité utilisateur."""
        # Section sources supprimée - les sources sont maintenant affichées dans l'interface utilisateur séparément
        return ""

    def _aggregate_all_sources(self, iteration_context: IterationContext) -> List[Dict[str, Any]]:
        """Agrège toutes les sources de toutes les itérations avec détails complets."""
        all_sources = []
        detailed_sources = []
        
        for results in iteration_context.previous_results:
            # Sources simples pour compatibilité
            all_sources.extend(results.get("all_sources", []))
            
            # Sources détaillées avec contexte d'itération
            detailed_sources.extend(results.get("detailed_sources", []))
        
        # Retourner les sources détaillées qui incluent plus d'informations
        return detailed_sources if detailed_sources else all_sources

    def _get_all_agents_used(self, iteration_context: IterationContext) -> List[str]:
        """Retourne tous les agents utilisés à travers toutes les itérations."""
        all_agents = set()
        for results in iteration_context.previous_results:
            all_agents.update(results.get("agent_results", {}).keys())
        return list(all_agents) 