"""
Cross-Reference Tool - Outil de référencement croisé pour les documents GRC.
Lie les informations connexes entre documents (contrôles, risques, politiques, etc.).
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime
import json

from ..integrations.llm_integration import get_llm_client
from .entity_extractor import EntityExtractor, EntityType

logger = logging.getLogger(__name__)

class RelationType(Enum):
    """Types de relations entre entités."""
    CONTROLS = "controls"          # Contrôle gère le risque
    IMPLEMENTS = "implements"      # Contrôle implémente l'exigence
    SUPPORTS = "supports"         # Document supporte le processus
    REFERENCES = "references"     # Document référence un autre
    DERIVES_FROM = "derives_from"  # Document dérivé d'un autre
    ADDRESSES = "addresses"       # Finding adresse une vulnérabilité
    AFFECTS = "affects"           # Risque affecte un actif
    REMEDIATES = "remediates"     # Action remédie à un finding
    COMPLIES_WITH = "complies_with"  # Contrôle conforme à l'exigence

@dataclass
class Relationship:
    """Relation entre deux entités."""
    source_id: str
    source_type: str
    target_id: str
    target_type: str
    relation_type: RelationType
    confidence: float  # 0.0 - 1.0
    evidence: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class CrossReferenceResult:
    """Résultat d'une analyse de référencement croisé."""
    relationships: List[Relationship]
    coverage_analysis: Dict[str, Any]
    gaps_identified: List[Dict[str, Any]]
    summary: Dict[str, Any]

class CrossReferenceTool:
    """
    Outil de référencement croisé pour analyser les relations entre entités GRC.
    """
    
    def __init__(self, rag_system=None, entity_extractor=None):
        """
        Initialise l'outil de référencement croisé.
        
        Args:
            rag_system: Système RAG pour la recherche sémantique
            entity_extractor: Extracteur d'entités
        """
        self.rag_system = rag_system
        self.entity_extractor = entity_extractor or EntityExtractor()
        self.llm_client = get_llm_client()
        
        # Cache des relations découvertes
        self.relationships_cache: Dict[str, List[Relationship]] = {}
        
        # Patterns de détection de relations
        self.relation_patterns = {
            RelationType.CONTROLS: [
                r"contrôle\s+([A-Z0-9\.-]+)\s+.*(?:gère|contrôle|mitigue).*risque\s+([A-Z0-9\.-]+)",
                r"le\s+risque\s+([A-Z0-9\.-]+)\s+est\s+(?:géré|contrôlé)\s+par.*contrôle\s+([A-Z0-9\.-]+)",
                r"([A-Z0-9\.-]+)\s+→\s+([A-Z0-9\.-]+)",  # Format diagramme
            ],
            RelationType.IMPLEMENTS: [
                r"contrôle\s+([A-Z0-9\.-]+)\s+.*implémente.*(?:exigence|article)\s+([A-Z0-9\.-]+)",
                r"(?:article|exigence)\s+([A-Z0-9\.-]+)\s+.*implémenté.*par.*contrôle\s+([A-Z0-9\.-]+)",
            ],
            RelationType.REFERENCES: [
                r"voir\s+(?:document|politique|procédure)\s+([A-Z0-9\.-]+)",
                r"référence.*:?\s+([A-Z0-9\.-]+)",
                r"cf\.?\s+([A-Z0-9\.-]+)",
            ],
            RelationType.ADDRESSES: [
                r"finding\s+([A-Z0-9\.-]+)\s+.*(?:adresse|corrige).*CVE-([0-9]{4}-[0-9]+)",
                r"vulnérabilité\s+([A-Z0-9\.-]+).*corrigée.*par.*([A-Z0-9\.-]+)",
            ]
        }
        
        # Base de données de vulnérabilités connues (exemple)
        self.vulnerability_db = {
            "CVE-2023-": "Vulnérabilités 2023",
            "CVE-2024-": "Vulnérabilités 2024",
            "OWASP-": "OWASP Top 10",
            "CWE-": "Common Weakness Enumeration"
        }
        
        # Frameworks et leurs mappings
        self.framework_mappings = {
            "ISO27001": {
                "controls": ["A.5", "A.6", "A.7", "A.8", "A.9", "A.10", "A.11", "A.12", 
                           "A.13", "A.14", "A.15", "A.16", "A.17", "A.18"],
                "risk_categories": ["operational", "technical", "legal", "strategic"]
            },
            "RGPD": {
                "articles": ["Art.5", "Art.6", "Art.25", "Art.32", "Art.33", "Art.35"],
                "principles": ["lawfulness", "purpose_limitation", "data_minimization"]
            }
        }

    async def analyze_cross_references(
        self,
        documents: List[Dict[str, Any]],
        focus_types: List[RelationType] = None,
        include_external: bool = True
    ) -> CrossReferenceResult:
        """
        Analyse les références croisées entre plusieurs documents.
        
        Args:
            documents: Liste des documents à analyser
            focus_types: Types de relations à chercher spécifiquement
            include_external: Inclure les références externes
            
        Returns:
            Résultats de l'analyse de référencement croisé
        """
        if focus_types is None:
            focus_types = list(RelationType)
            
        logger.info(f"Analyse de références croisées sur {len(documents)} documents")
        
        # 1. Extraction des entités de tous les documents
        all_entities = await self._extract_entities_from_documents(documents)
        
        # 2. Recherche de relations par patterns
        pattern_relationships = await self._find_pattern_relationships(
            documents, focus_types
        )
        
        # 3. Recherche de relations par LLM
        llm_relationships = await self._find_llm_relationships(
            documents, all_entities, focus_types
        )
        
        # 4. Recherche de références externes
        external_relationships = []
        if include_external:
            external_relationships = await self._find_external_references(
                documents, all_entities
            )
        
        # 5. Fusion et déduplication des relations
        all_relationships = self._merge_relationships(
            pattern_relationships + llm_relationships + external_relationships
        )
        
        # 6. Analyse de couverture
        coverage_analysis = await self._analyze_coverage(
            all_entities, all_relationships
        )
        
        # 7. Identification des gaps
        gaps = await self._identify_gaps(all_entities, all_relationships, focus_types)
        
        # 8. Génération du résumé
        summary = self._generate_summary(
            all_relationships, coverage_analysis, gaps
        )
        
        return CrossReferenceResult(
            relationships=all_relationships,
            coverage_analysis=coverage_analysis,
            gaps_identified=gaps,
            summary=summary
        )

    async def map_controls_to_risks(
        self,
        controls: List[Dict[str, Any]],
        risks: List[Dict[str, Any]]
    ) -> List[Relationship]:
        """
        Mappe spécifiquement les contrôles aux risques qu'ils gèrent.
        """
        logger.info(f"Mapping {len(controls)} contrôles vers {len(risks)} risques")
        
        relationships = []
        
        for control in controls:
            control_id = control.get("id", "")
            control_desc = control.get("description", "")
            
            # Recherche de risques liés dans la description du contrôle
            related_risks = await self._find_related_risks_for_control(
                control_id, control_desc, risks
            )
            
            for risk_id, confidence in related_risks:
                relationship = Relationship(
                    source_id=control_id,
                    source_type="control",
                    target_id=risk_id,
                    target_type="risk",
                    relation_type=RelationType.CONTROLS,
                    confidence=confidence,
                    evidence=f"Contrôle {control_id} gère le risque {risk_id}",
                    metadata={
                        "control_type": control.get("control_type"),
                        "analysis_method": "semantic_matching"
                    }
                )
                relationships.append(relationship)
        
        return relationships

    async def correlate_findings_to_vulnerabilities(
        self,
        findings: List[Dict[str, Any]],
        external_db_query: bool = True
    ) -> List[Relationship]:
        """
        Corrèle les findings aux bases de données de vulnérabilités.
        """
        logger.info(f"Corrélation de {len(findings)} findings avec bases de vulnérabilités")
        
        relationships = []
        
        for finding in findings:
            finding_id = finding.get("id", "")
            finding_desc = finding.get("description", "")
            
            # Recherche de CVE dans la description
            cve_matches = re.findall(r"CVE-([0-9]{4}-[0-9]+)", finding_desc)
            
            for cve in cve_matches:
                cve_id = f"CVE-{cve}"
                
                # Recherche d'informations sur la CVE
                vuln_info = await self._get_vulnerability_info(cve_id)
                
                relationship = Relationship(
                    source_id=finding_id,
                    source_type="finding",
                    target_id=cve_id,
                    target_type="vulnerability",
                    relation_type=RelationType.ADDRESSES,
                    confidence=0.95,  # Haute confiance pour match CVE exact
                    evidence=f"Finding {finding_id} adresse {cve_id}",
                    metadata={
                        "vulnerability_info": vuln_info,
                        "cvss_score": finding.get("cvss_score"),
                        "severity": finding.get("severity")
                    }
                )
                relationships.append(relationship)
        
        return relationships

    async def trace_document_lineage(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[Relationship]:
        """
        Trace la lignée des documents (politique → procédure → instruction).
        """
        logger.info("Traçage de la lignée documentaire")
        
        relationships = []
        
        # Classement des documents par type hiérarchique
        policies = [d for d in documents if "politique" in d.get("type", "").lower()]
        procedures = [d for d in documents if "procédure" in d.get("type", "").lower()]
        instructions = [d for d in documents if "instruction" in d.get("type", "").lower()]
        
        # Politique → Procédure
        for policy in policies:
            related_procedures = await self._find_derived_documents(
                policy, procedures, RelationType.DERIVES_FROM
            )
            relationships.extend(related_procedures)
        
        # Procédure → Instruction
        for procedure in procedures:
            related_instructions = await self._find_derived_documents(
                procedure, instructions, RelationType.DERIVES_FROM
            )
            relationships.extend(related_instructions)
        
        return relationships

    async def analyze_relationships(
        self,
        content_list: List[str],
        relation_types: List[RelationType] = None
    ) -> CrossReferenceResult:
        """
        Analyse les relations entre entités à partir d'une liste de contenus.
        
        Args:
            content_list: Liste des contenus textuels à analyser
            relation_types: Types de relations à rechercher
            
        Returns:
            Résultats de l'analyse des relations
        """
        if relation_types is None:
            relation_types = list(RelationType)
            
        # Créer des documents temporaires à partir des contenus
        documents = []
        for i, content in enumerate(content_list):
            documents.append({
                "id": f"doc_{i}",
                "content": content,
                "type": "text"
            })
        
        # Utiliser la méthode d'analyse de références croisées existante
        return await self.analyze_cross_references(
            documents=documents,
            focus_types=relation_types,
            include_external=False
        )

    async def _extract_entities_from_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extrait les entités de tous les documents.
        """
        all_entities = {
            "controls": [],
            "risks": [],
            "findings": [],
            "requirements": [],
            "assets": []
        }
        
        for doc in documents:
            content = doc.get("content", "")
            if content:
                doc_entities = await self.entity_extractor.extract_entities(
                    content, 
                    entity_types=[EntityType.CONTROL, EntityType.RISK, 
                                EntityType.FINDING, EntityType.REQUIREMENT, 
                                EntityType.ASSET]
                )
                
                # Ajouter l'ID du document aux entités
                for entity_type, entities in doc_entities.items():
                    for entity in entities:
                        entity["source_document"] = doc.get("id", "")
                    all_entities[entity_type].extend(entities)
        
        return all_entities

    async def _find_pattern_relationships(
        self,
        documents: List[Dict[str, Any]],
        focus_types: List[RelationType]
    ) -> List[Relationship]:
        """
        Trouve les relations en utilisant des patterns regex.
        """
        relationships = []
        
        for doc in documents:
            content = doc.get("content", "")
            doc_id = doc.get("id", "")
            
            for relation_type in focus_types:
                if relation_type in self.relation_patterns:
                    patterns = self.relation_patterns[relation_type]
                    
                    for pattern in patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        
                        for match in matches:
                            if isinstance(match, tuple) and len(match) >= 2:
                                source_id, target_id = match[0], match[1]
                                
                                relationship = Relationship(
                                    source_id=source_id,
                                    source_type="entity",
                                    target_id=target_id,
                                    target_type="entity",
                                    relation_type=relation_type,
                                    confidence=0.7,  # Confiance modérée pour patterns
                                    evidence=f"Pattern trouvé dans {doc_id}",
                                    metadata={"source_document": doc_id, "method": "pattern"}
                                )
                                relationships.append(relationship)
        
        return relationships

    async def _find_llm_relationships(
        self,
        documents: List[Dict[str, Any]],
        entities: Dict[str, List[Dict[str, Any]]],
        focus_types: List[RelationType]
    ) -> List[Relationship]:
        """
        Trouve les relations en utilisant l'analyse LLM.
        """
        relationships = []
        
        # Préparer le contexte des entités
        entities_context = json.dumps(entities, indent=2, default=str)[:2000]
        focus_types_str = ", ".join([t.value for t in focus_types])
        
        for doc in documents:
            content = doc.get("content", "")[:3000]  # Limite pour LLM
            doc_id = doc.get("id", "")
            
            prompt = f"""
Analyse les relations entre entités dans ce document GRC.

ENTITÉS CONNUES:
{entities_context}

TYPES DE RELATIONS À RECHERCHER: {focus_types_str}

DOCUMENT:
{content}

Identifie toutes les relations et retourne un JSON:
{{
    "relationships": [
        {{
            "source_id": "id_source",
            "source_type": "type_source",
            "target_id": "id_cible", 
            "target_type": "type_cible",
            "relation_type": "controls|implements|references|...",
            "confidence": 0.0-1.0,
            "evidence": "justification"
        }}
    ]
}}
"""

            try:
                response = await self.llm_client.generate_response(
                    messages=[{"role": "user", "content": prompt}],
                    model="gpt-4.1",
                    temperature=0.1
                )
                
                # Extraire le JSON
                json_start = response.find("{")
                json_end = response.rfind("}") + 1
                json_content = response[json_start:json_end]
                
                data = json.loads(json_content)
                
                for rel_data in data.get("relationships", []):
                    relationship = Relationship(
                        source_id=rel_data.get("source_id", ""),
                        source_type=rel_data.get("source_type", ""),
                        target_id=rel_data.get("target_id", ""),
                        target_type=rel_data.get("target_type", ""),
                        relation_type=RelationType(rel_data.get("relation_type", "references")),
                        confidence=float(rel_data.get("confidence", 0.5)),
                        evidence=rel_data.get("evidence", ""),
                        metadata={"source_document": doc_id, "method": "llm_analysis"}
                    )
                    relationships.append(relationship)
                    
            except Exception as e:
                logger.error(f"Erreur analyse LLM pour {doc_id}: {str(e)}")
                continue
        
        return relationships

    async def _find_external_references(
        self,
        documents: List[Dict[str, Any]],
        entities: Dict[str, List[Dict[str, Any]]]
    ) -> List[Relationship]:
        """
        Trouve les références vers des sources externes.
        """
        relationships = []
        
        for doc in documents:
            content = doc.get("content", "")
            doc_id = doc.get("id", "")
            
            # Rechercher des références vers des frameworks
            for framework, framework_data in self.framework_mappings.items():
                if framework.lower() in content.lower():
                    # Rechercher des références spécifiques aux contrôles du framework
                    if "controls" in framework_data:
                        for control_ref in framework_data["controls"]:
                            if control_ref in content:
                                relationship = Relationship(
                                    source_id=doc_id,
                                    source_type="document",
                                    target_id=f"{framework}.{control_ref}",
                                    target_type="framework_control",
                                    relation_type=RelationType.REFERENCES,
                                    confidence=0.8,
                                    evidence=f"Référence {framework} {control_ref} dans {doc_id}",
                                    metadata={"framework": framework, "external": True}
                                )
                                relationships.append(relationship)
        
        return relationships

    def _merge_relationships(
        self,
        relationships: List[Relationship]
    ) -> List[Relationship]:
        """
        Fusionne et déduplique les relations trouvées.
        """
        # Créer un dictionnaire pour déduplication
        unique_relations = {}
        
        for rel in relationships:
            # Clé unique basée sur source, target et type
            key = f"{rel.source_id}_{rel.target_id}_{rel.relation_type.value}"
            
            if key not in unique_relations:
                unique_relations[key] = rel
            else:
                # Garder la relation avec la plus haute confiance
                if rel.confidence > unique_relations[key].confidence:
                    unique_relations[key] = rel
        
        return list(unique_relations.values())

    async def _analyze_coverage(
        self,
        entities: Dict[str, List[Dict[str, Any]]],
        relationships: List[Relationship]
    ) -> Dict[str, Any]:
        """
        Analyse la couverture des relations.
        """
        coverage = {
            "total_entities": sum(len(ents) for ents in entities.values()),
            "total_relationships": len(relationships),
            "coverage_by_type": {},
            "orphaned_entities": [],
            "highly_connected": []
        }
        
        # Calculer la couverture par type d'entité
        for entity_type, entity_list in entities.items():
            connected = set()
            
            for rel in relationships:
                if rel.source_type == entity_type:
                    connected.add(rel.source_id)
                if rel.target_type == entity_type:
                    connected.add(rel.target_id)
            
            coverage["coverage_by_type"][entity_type] = {
                "total": len(entity_list),
                "connected": len(connected),
                "coverage_percentage": (len(connected) / max(len(entity_list), 1)) * 100 if entity_list else 0
            }
            
            # Identifier les entités orphelines
            for entity in entity_list:
                entity_id = entity.get("id", "")
                if entity_id and entity_id not in connected:
                    coverage["orphaned_entities"].append({
                        "id": entity_id,
                        "type": entity_type,
                        "name": entity.get("name", "")
                    })
        
        return coverage

    async def _identify_gaps(
        self,
        entities: Dict[str, List[Dict[str, Any]]],
        relationships: List[Relationship],
        focus_types: List[RelationType]
    ) -> List[Dict[str, Any]]:
        """
        Identifie les gaps dans la couverture.
        """
        gaps = []
        
        # Gap: Risques sans contrôles
        risks = entities.get("risks", [])
        controlled_risks = set()
        
        for rel in relationships:
            if rel.relation_type == RelationType.CONTROLS and rel.target_type == "risk":
                controlled_risks.add(rel.target_id)
        
        for risk in risks:
            risk_id = risk.get("id", "")
            if risk_id and risk_id not in controlled_risks:
                gaps.append({
                    "type": "uncontrolled_risk",
                    "entity_id": risk_id,
                    "entity_name": risk.get("name", ""),
                    "description": f"Risque {risk_id} n'a pas de contrôle identifié",
                    "severity": "high"
                })
        
        # Gap: Contrôles sans risques associés
        controls = entities.get("controls", [])
        risk_controlling = set()
        
        for rel in relationships:
            if rel.relation_type == RelationType.CONTROLS and rel.source_type == "control":
                risk_controlling.add(rel.source_id)
        
        for control in controls:
            control_id = control.get("id", "")
            if control_id and control_id not in risk_controlling:
                gaps.append({
                    "type": "orphaned_control",
                    "entity_id": control_id,
                    "entity_name": control.get("name", ""),
                    "description": f"Contrôle {control_id} ne gère aucun risque identifié",
                    "severity": "medium"
                })
        
        return gaps

    def _generate_summary(
        self,
        relationships: List[Relationship],
        coverage: Dict[str, Any],
        gaps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Génère un résumé de l'analyse.
        """
        return {
            "total_relationships": len(relationships),
            "relationship_types": {
                rel_type.value: len([r for r in relationships if r.relation_type == rel_type])
                for rel_type in RelationType
            },
            "average_confidence": sum(r.confidence for r in relationships) / len(relationships) if relationships else 0,
            "total_gaps": len(gaps),
            "gap_severity": {
                "high": len([g for g in gaps if g.get("severity") == "high"]),
                "medium": len([g for g in gaps if g.get("severity") == "medium"]),
                "low": len([g for g in gaps if g.get("severity") == "low"])
            },
            "overall_coverage": (coverage.get("total_relationships", 0) / max(coverage.get("total_entities", 1), 1)) * 100
        }

    # Méthodes helper supplémentaires
    async def _find_related_risks_for_control(
        self, 
        control_id: str, 
        control_desc: str, 
        risks: List[Dict[str, Any]]
    ) -> List[Tuple[str, float]]:
        """
        Trouve les risques liés à un contrôle spécifique.
        """
        related = []
        
        for risk in risks:
            risk_id = risk.get("id", "")
            risk_desc = risk.get("description", "")
            
            # Calcul de similarité sémantique simple
            similarity = await self._calculate_semantic_similarity(
                control_desc, risk_desc
            )
            
            if similarity > 0.5:  # Seuil de similarité
                related.append((risk_id, similarity))
        
        return related

    async def _calculate_semantic_similarity(
        self, 
        text1: str, 
        text2: str
    ) -> float:
        """
        Calcule la similarité sémantique entre deux textes.
        """
        # Implémentation simple - peut être améliorée avec des embeddings
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

    async def _get_vulnerability_info(self, cve_id: str) -> Dict[str, Any]:
        """
        Récupère les informations sur une vulnérabilité.
        """
        # Placeholder - intégration avec NIST NVD ou autres bases
        return {
            "cve_id": cve_id,
            "description": f"Informations sur {cve_id}",
            "cvss_score": "N/A",
            "published_date": "N/A"
        }

    async def _find_derived_documents(
        self,
        parent_doc: Dict[str, Any],
        candidate_docs: List[Dict[str, Any]],
        relation_type: RelationType
    ) -> List[Relationship]:
        """
        Trouve les documents dérivés d'un document parent.
        """
        relationships = []
        parent_id = parent_doc.get("id", "")
        parent_title = parent_doc.get("title", "").lower()
        
        for candidate in candidate_docs:
            candidate_id = candidate.get("id", "")
            candidate_content = candidate.get("content", "").lower()
            
            # Rechercher des références au document parent
            if parent_id.lower() in candidate_content or any(
                word in candidate_content for word in parent_title.split()[:3]
            ):
                relationship = Relationship(
                    source_id=candidate_id,
                    source_type="document",
                    target_id=parent_id,
                    target_type="document",
                    relation_type=relation_type,
                    confidence=0.6,
                    evidence=f"Document {candidate_id} dérive de {parent_id}",
                    metadata={"lineage": "document_hierarchy"}
                )
                relationships.append(relationship)
        
        return relationships


# Tool function for agent integration
async def cross_reference_tool(
    documents: List[Dict[str, Any]],
    focus_types: List[str] = None,
    include_external: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Outil de référencement croisé pour les agents.
    """
    tool = CrossReferenceTool()
    
    # Convertir les types de relation
    if focus_types:
        relation_types = [RelationType(t) for t in focus_types if t in [r.value for r in RelationType]]
    else:
        relation_types = None
    
    try:
        result = await tool.analyze_cross_references(
            documents=documents,
            focus_types=relation_types,
            include_external=include_external
        )
        
        return {
            "success": True,
            "relationships": [
                {
                    "source_id": r.source_id,
                    "source_type": r.source_type,
                    "target_id": r.target_id,
                    "target_type": r.target_type,
                    "relation_type": r.relation_type.value,
                    "confidence": r.confidence,
                    "evidence": r.evidence,
                    "metadata": r.metadata
                }
                for r in result.relationships
            ],
            "coverage_analysis": result.coverage_analysis,
            "gaps_identified": result.gaps_identified,
            "summary": result.summary
        }
        
    except Exception as e:
        logger.error(f"Erreur dans cross_reference_tool: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "relationships": []
        }


def get_cross_reference_tool(rag_system=None, entity_extractor=None):
    """Factory function pour obtenir une instance de CrossReferenceTool."""
    return CrossReferenceTool(rag_system=rag_system, entity_extractor=entity_extractor) 