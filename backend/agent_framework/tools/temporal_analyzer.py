"""
Temporal Analyzer - Outil d'analyse temporelle pour le suivi des tendances GRC.
Analyse l'évolution des risques, contrôles et conformité dans le temps.
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import json
import statistics
from collections import defaultdict

from ..integrations.llm_integration import get_llm_client

logger = logging.getLogger(__name__)

class TrendDirection(Enum):
    """Direction des tendances."""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"
    UNKNOWN = "unknown"

class MetricType(Enum):
    """Types de métriques analysées."""
    RISK_LEVEL = "risk_level"
    CONTROL_EFFECTIVENESS = "control_effectiveness"
    COMPLIANCE_SCORE = "compliance_score"
    FINDING_COUNT = "finding_count"
    INCIDENT_FREQUENCY = "incident_frequency"
    REMEDIATION_TIME = "remediation_time"

@dataclass
class TimeSeriesPoint:
    """Point de données dans une série temporelle."""
    timestamp: datetime
    value: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class TrendAnalysis:
    """Analyse de tendance pour une métrique."""
    metric_type: MetricType
    entity_id: str
    entity_name: str
    time_series: List[TimeSeriesPoint]
    trend_direction: TrendDirection
    trend_strength: float  # 0.0 - 1.0
    slope: float  # Pente de la tendance
    confidence_interval: Tuple[float, float]
    anomalies_detected: List[Dict[str, Any]]
    summary: str

@dataclass
class TemporalReport:
    """Rapport d'analyse temporelle."""
    analysis_period: Tuple[datetime, datetime]
    trend_analyses: List[TrendAnalysis]
    comparative_analysis: Dict[str, Any]
    forecasts: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    summary: Dict[str, Any]

class TemporalAnalyzer:
    """
    Analyseur temporel pour suivre l'évolution des métriques GRC.
    """
    
    def __init__(self, data_source=None):
        """
        Initialise l'analyseur temporel.
        
        Args:
            data_source: Source de données historiques
        """
        self.data_source = data_source
        self.llm_client = get_llm_client()
        
        # Cache des analyses
        self.analysis_cache: Dict[str, TrendAnalysis] = {}
        
        # Seuils pour détection d'anomalies
        self.anomaly_thresholds = {
            MetricType.RISK_LEVEL: {"min_change": 0.3, "std_multiplier": 2.0},
            MetricType.CONTROL_EFFECTIVENESS: {"min_change": 0.2, "std_multiplier": 1.5},
            MetricType.COMPLIANCE_SCORE: {"min_change": 0.15, "std_multiplier": 1.8},
            MetricType.FINDING_COUNT: {"min_change": 0.5, "std_multiplier": 2.5},
        }
        
        # Patterns de référence pour différents types d'organisations
        self.benchmark_patterns = {
            "startup": {
                "risk_tolerance": "medium_high",
                "maturity_growth_rate": 0.3,
                "typical_improvements": ["control_implementation", "process_documentation"]
            },
            "enterprise": {
                "risk_tolerance": "low",
                "maturity_growth_rate": 0.1,
                "typical_improvements": ["automation", "advanced_monitoring"]
            },
            "financial": {
                "risk_tolerance": "very_low",
                "maturity_growth_rate": 0.05,
                "typical_improvements": ["compliance_alignment", "audit_optimization"]
            }
        }

    async def analyze_trends(
        self,
        entities: List[Dict[str, Any]],
        metric_types: List[MetricType],
        time_range: Tuple[datetime, datetime],
        include_forecasts: bool = True
    ) -> TemporalReport:
        """
        Analyse les tendances pour une liste d'entités sur une période donnée.
        
        Args:
            entities: Entités à analyser (risques, contrôles, etc.)
            metric_types: Types de métriques à analyser
            time_range: Période d'analyse (début, fin)
            include_forecasts: Inclure les prévisions
            
        Returns:
            Rapport d'analyse temporelle
        """
        start_time, end_time = time_range
        logger.info(f"Analyse temporelle de {len(entities)} entités du {start_time} au {end_time}")
        
        trend_analyses = []
        
        # 1. Analyser chaque entité pour chaque métrique
        for entity in entities:
            entity_id = entity.get("id", "")
            entity_name = entity.get("name", entity_id)
            
            for metric_type in metric_types:
                # Récupérer les données historiques
                time_series = await self._get_historical_data(
                    entity_id, metric_type, time_range
                )
                
                if len(time_series) >= 3:  # Minimum pour analyse de tendance
                    trend_analysis = await self._analyze_entity_trend(
                        entity_id, entity_name, metric_type, time_series
                    )
                    trend_analyses.append(trend_analysis)
        
        # 2. Analyse comparative entre entités
        comparative_analysis = await self._perform_comparative_analysis(
            trend_analyses
        )
        
        # 3. Générer des prévisions si demandé
        forecasts = {}
        if include_forecasts:
            forecasts = await self._generate_forecasts(
                trend_analyses, time_range
            )
        
        # 4. Générer des recommandations
        recommendations = await self._generate_recommendations(
            trend_analyses, comparative_analysis, forecasts
        )
        
        # 5. Créer le résumé
        summary = self._create_summary(
            trend_analyses, comparative_analysis, forecasts
        )
        
        return TemporalReport(
            analysis_period=time_range,
            trend_analyses=trend_analyses,
            comparative_analysis=comparative_analysis,
            forecasts=forecasts,
            recommendations=recommendations,
            summary=summary
        )

    async def track_risk_evolution(
        self,
        risks: List[Dict[str, Any]],
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """
        Suit spécifiquement l'évolution des risques dans le temps.
        """
        logger.info(f"Suivi évolution de {len(risks)} risques")
        
        risk_trends = {}
        
        for risk in risks:
            risk_id = risk.get("id", "")
            
            # Analyser l'évolution du niveau de risque
            risk_level_data = await self._get_historical_data(
                risk_id, MetricType.RISK_LEVEL, time_range
            )
            
            if risk_level_data:
                trend = await self._calculate_trend(risk_level_data)
                
                # Analyser l'évolution des contrôles associés
                control_effectiveness = await self._get_control_effectiveness_trend(
                    risk_id, time_range
                )
                
                # Détecter les événements significatifs
                significant_events = await self._detect_significant_events(
                    risk_id, risk_level_data, time_range
                )
                
                risk_trends[risk_id] = {
                    "risk_trend": trend,
                    "control_effectiveness": control_effectiveness,
                    "significant_events": significant_events,
                    "current_level": risk_level_data[-1].value if risk_level_data else None,
                    "change_from_start": self._calculate_change_percentage(risk_level_data)
                }
        
        return {
            "risk_trends": risk_trends,
            "summary": self._summarize_risk_evolution(risk_trends),
            "alerts": self._generate_risk_alerts(risk_trends)
        }

    async def analyze_control_effectiveness_over_time(
        self,
        controls: List[Dict[str, Any]],
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """
        Analyse l'efficacité des contrôles dans le temps.
        """
        logger.info(f"Analyse efficacité temporelle de {len(controls)} contrôles")
        
        control_analyses = {}
        
        for control in controls:
            control_id = control.get("id", "")
            
            # Données d'efficacité historiques
            effectiveness_data = await self._get_historical_data(
                control_id, MetricType.CONTROL_EFFECTIVENESS, time_range
            )
            
            if effectiveness_data:
                # Analyser la tendance d'efficacité
                trend = await self._calculate_trend(effectiveness_data)
                
                # Analyser la variabilité
                variability = self._calculate_variability(effectiveness_data)
                
                # Identifier les périodes de dégradation
                degradation_periods = self._identify_degradation_periods(
                    effectiveness_data
                )
                
                # Corréler avec les incidents
                incident_correlation = await self._correlate_with_incidents(
                    control_id, effectiveness_data, time_range
                )
                
                control_analyses[control_id] = {
                    "effectiveness_trend": trend,
                    "variability_score": variability,
                    "degradation_periods": degradation_periods,
                    "incident_correlation": incident_correlation,
                    "improvement_rate": self._calculate_improvement_rate(effectiveness_data),
                    "stability_score": self._calculate_stability_score(effectiveness_data)
                }
        
        return {
            "control_analyses": control_analyses,
            "benchmarking": self._benchmark_control_performance(control_analyses),
            "optimization_opportunities": self._identify_optimization_opportunities(control_analyses)
        }

    async def track_compliance_posture_evolution(
        self,
        frameworks: List[str],
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """
        Suit l'évolution de la posture de conformité.
        """
        logger.info(f"Suivi conformité pour frameworks: {frameworks}")
        
        compliance_evolution = {}
        
        for framework in frameworks:
            # Score de conformité global
            compliance_scores = await self._get_historical_data(
                framework, MetricType.COMPLIANCE_SCORE, time_range
            )
            
            if compliance_scores:
                # Analyser la progression
                progression = await self._analyze_compliance_progression(
                    framework, compliance_scores
                )
                
                # Identifier les domaines d'amélioration/régression
                domain_analysis = await self._analyze_compliance_domains(
                    framework, time_range
                )
                
                # Prédire l'échéance de conformité complète
                full_compliance_forecast = await self._forecast_full_compliance(
                    framework, compliance_scores
                )
                
                compliance_evolution[framework] = {
                    "progression": progression,
                    "domain_analysis": domain_analysis,
                    "full_compliance_forecast": full_compliance_forecast,
                    "maturity_trajectory": self._assess_maturity_trajectory(compliance_scores)
                }
        
        return {
            "framework_evolution": compliance_evolution,
            "cross_framework_analysis": self._analyze_cross_framework_synergies(compliance_evolution),
            "regulatory_readiness": self._assess_regulatory_readiness(compliance_evolution)
        }

    async def _get_historical_data(
        self,
        entity_id: str,
        metric_type: MetricType,
        time_range: Tuple[datetime, datetime]
    ) -> List[TimeSeriesPoint]:
        """
        Récupère les données historiques pour une entité et métrique.
        """
        # Simulation de données - à remplacer par vraie source de données
        start_time, end_time = time_range
        
        # Générer des points de données simulés
        points = []
        current_time = start_time
        base_value = 0.5  # Valeur de base
        
        while current_time <= end_time:
            # Simulation d'évolution avec bruit
            import random
            trend_factor = (current_time - start_time).days / (end_time - start_time).days
            noise = random.uniform(-0.1, 0.1)
            
            if metric_type == MetricType.RISK_LEVEL:
                # Risque qui diminue généralement dans le temps
                value = max(0.1, min(0.9, base_value - (trend_factor * 0.3) + noise))
            elif metric_type == MetricType.CONTROL_EFFECTIVENESS:
                # Efficacité qui augmente
                value = max(0.1, min(0.9, base_value + (trend_factor * 0.4) + noise))
            elif metric_type == MetricType.COMPLIANCE_SCORE:
                # Score de conformité qui augmente
                value = max(0.0, min(1.0, base_value + (trend_factor * 0.5) + noise))
            else:
                value = max(0.0, min(1.0, base_value + noise))
            
            points.append(TimeSeriesPoint(
                timestamp=current_time,
                value=value,
                metadata={"entity_id": entity_id, "metric_type": metric_type.value}
            ))
            
            current_time += timedelta(days=7)  # Points hebdomadaires
        
        return points

    async def _analyze_entity_trend(
        self,
        entity_id: str,
        entity_name: str,
        metric_type: MetricType,
        time_series: List[TimeSeriesPoint]
    ) -> TrendAnalysis:
        """
        Analyse la tendance pour une entité spécifique.
        """
        # Calculer la pente de la tendance
        x_values = [(point.timestamp - time_series[0].timestamp).days for point in time_series]
        y_values = [point.value for point in time_series]
        
        slope = self._calculate_slope(x_values, y_values)
        
        # Déterminer la direction de la tendance
        if abs(slope) < 0.001:
            direction = TrendDirection.STABLE
        elif slope > 0:
            direction = TrendDirection.IMPROVING if metric_type in [
                MetricType.CONTROL_EFFECTIVENESS, MetricType.COMPLIANCE_SCORE
            ] else TrendDirection.DECLINING
        else:
            direction = TrendDirection.DECLINING if metric_type in [
                MetricType.CONTROL_EFFECTIVENESS, MetricType.COMPLIANCE_SCORE
            ] else TrendDirection.IMPROVING
        
        # Calculer la force de la tendance
        trend_strength = min(1.0, abs(slope) * 1000)  # Normaliser
        
        # Calculer l'intervalle de confiance
        confidence_interval = self._calculate_confidence_interval(y_values)
        
        # Détecter les anomalies
        anomalies = self._detect_anomalies(time_series, metric_type)
        
        # Générer un résumé
        summary = await self._generate_trend_summary(
            entity_id, metric_type, direction, trend_strength, anomalies
        )
        
        return TrendAnalysis(
            metric_type=metric_type,
            entity_id=entity_id,
            entity_name=entity_name,
            time_series=time_series,
            trend_direction=direction,
            trend_strength=trend_strength,
            slope=slope,
            confidence_interval=confidence_interval,
            anomalies_detected=anomalies,
            summary=summary
        )

    async def _perform_comparative_analysis(
        self,
        trend_analyses: List[TrendAnalysis]
    ) -> Dict[str, Any]:
        """
        Effectue une analyse comparative entre les entités.
        """
        analysis = {
            "best_performers": [],
            "worst_performers": [],
            "correlation_analysis": {},
            "cluster_analysis": {}
        }
        
        # Grouper par type de métrique
        by_metric = defaultdict(list)
        for trend in trend_analyses:
            by_metric[trend.metric_type].append(trend)
        
        for metric_type, trends in by_metric.items():
            # Trier par performance
            if metric_type in [MetricType.CONTROL_EFFECTIVENESS, MetricType.COMPLIANCE_SCORE]:
                # Pour ces métriques, plus c'est haut, mieux c'est
                trends.sort(key=lambda t: t.slope, reverse=True)
            else:
                # Pour les risques, moins c'est mieux
                trends.sort(key=lambda t: t.slope)
            
            # Identifier les meilleurs et pires performers
            analysis["best_performers"].extend(trends[:3])
            analysis["worst_performers"].extend(trends[-3:])
        
        return analysis

    async def _generate_forecasts(
        self,
        trend_analyses: List[TrendAnalysis],
        time_range: Tuple[datetime, datetime]
    ) -> Dict[str, Any]:
        """
        Génère des prévisions basées sur les tendances.
        """
        forecasts = {}
        
        for trend in trend_analyses:
            if len(trend.time_series) >= 5:  # Minimum pour prévision
                # Prévision simple basée sur la tendance linéaire
                last_point = trend.time_series[-1]
                forecast_periods = [30, 90, 180]  # 1, 3, 6 mois
                
                entity_forecasts = []
                for days in forecast_periods:
                    future_date = last_point.timestamp + timedelta(days=days)
                    predicted_value = last_point.value + (trend.slope * days)
                    
                    # Contraindre dans des limites réalistes
                    predicted_value = max(0.0, min(1.0, predicted_value))
                    
                    entity_forecasts.append({
                        "date": future_date,
                        "predicted_value": predicted_value,
                        "confidence": max(0.3, trend.trend_strength)
                    })
                
                forecasts[f"{trend.entity_id}_{trend.metric_type.value}"] = entity_forecasts
        
        return forecasts

    async def _generate_recommendations(
        self,
        trend_analyses: List[TrendAnalysis],
        comparative_analysis: Dict[str, Any],
        forecasts: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Génère des recommandations basées sur l'analyse.
        """
        recommendations = []
        
        # Recommandations basées sur les tendances négatives
        for trend in trend_analyses:
            if trend.trend_direction == TrendDirection.DECLINING and trend.trend_strength > 0.5:
                recommendations.append({
                    "type": "urgent_action",
                    "entity_id": trend.entity_id,
                    "entity_name": trend.entity_name,
                    "metric": trend.metric_type.value,
                    "description": f"Tendance de dégradation détectée pour {trend.entity_name}",
                    "suggested_actions": await self._suggest_actions_for_trend(trend),
                    "priority": "high"
                })
        
        # Recommandations basées sur les anomalies
        for trend in trend_analyses:
            if trend.anomalies_detected:
                recommendations.append({
                    "type": "investigate_anomaly",
                    "entity_id": trend.entity_id,
                    "entity_name": trend.entity_name,
                    "description": f"Anomalies détectées dans {trend.entity_name}",
                    "anomaly_count": len(trend.anomalies_detected),
                    "priority": "medium"
                })
        
        return recommendations

    # Méthodes utilitaires
    def _calculate_slope(self, x_values: List[float], y_values: List[float]) -> float:
        """Calcule la pente d'une régression linéaire simple."""
        n = len(x_values)
        if n < 2:
            return 0.0
        
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        
        denominator = n * sum_x2 - sum_x * sum_x
        if abs(denominator) < 1e-10:
            return 0.0
        
        return (n * sum_xy - sum_x * sum_y) / denominator

    def _calculate_confidence_interval(self, values: List[float]) -> Tuple[float, float]:
        """Calcule l'intervalle de confiance à 95%."""
        if len(values) < 2:
            return (0.0, 1.0)
        
        mean = statistics.mean(values)
        std_dev = statistics.stdev(values)
        margin = 1.96 * std_dev / (len(values) ** 0.5)
        
        return (max(0.0, mean - margin), min(1.0, mean + margin))

    def _detect_anomalies(
        self, 
        time_series: List[TimeSeriesPoint], 
        metric_type: MetricType
    ) -> List[Dict[str, Any]]:
        """Détecte les anomalies dans une série temporelle."""
        if len(time_series) < 5:
            return []
        
        values = [point.value for point in time_series]
        mean_val = statistics.mean(values)
        std_val = statistics.stdev(values)
        
        threshold = self.anomaly_thresholds.get(metric_type, {})
        std_multiplier = threshold.get("std_multiplier", 2.0)
        
        anomalies = []
        for i, point in enumerate(time_series):
            if abs(point.value - mean_val) > std_multiplier * std_val:
                anomalies.append({
                    "timestamp": point.timestamp,
                    "value": point.value,
                    "expected_range": (mean_val - std_val, mean_val + std_val),
                    "severity": "high" if abs(point.value - mean_val) > 3 * std_val else "medium"
                })
        
        return anomalies

    async def _suggest_actions_for_trend(self, trend: TrendAnalysis) -> List[str]:
        """Suggère des actions basées sur une tendance."""
        actions = []
        
        if trend.metric_type == MetricType.RISK_LEVEL:
            if trend.trend_direction == TrendDirection.DECLINING:  # Risque qui augmente
                actions = [
                    "Renforcer les contrôles existants",
                    "Implémenter des contrôles additionnels",
                    "Réviser l'évaluation des risques",
                    "Augmenter la fréquence de monitoring"
                ]
        elif trend.metric_type == MetricType.CONTROL_EFFECTIVENESS:
            if trend.trend_direction == TrendDirection.DECLINING:
                actions = [
                    "Réviser les procédures de contrôle",
                    "Former le personnel responsable",
                    "Automatiser le contrôle si possible",
                    "Augmenter la fréquence d'exécution"
                ]
        
        return actions

    def _create_summary(
        self,
        trend_analyses: List[TrendAnalysis],
        comparative_analysis: Dict[str, Any],
        forecasts: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crée un résumé de l'analyse temporelle."""
        improving_trends = [t for t in trend_analyses if t.trend_direction == TrendDirection.IMPROVING]
        declining_trends = [t for t in trend_analyses if t.trend_direction == TrendDirection.DECLINING]
        stable_trends = [t for t in trend_analyses if t.trend_direction == TrendDirection.STABLE]
        
        return {
            "total_entities_analyzed": len(trend_analyses),
            "trend_distribution": {
                "improving": len(improving_trends),
                "declining": len(declining_trends),
                "stable": len(stable_trends)
            },
            "average_trend_strength": statistics.mean([t.trend_strength for t in trend_analyses]) if trend_analyses else 0,
            "total_anomalies": sum(len(t.anomalies_detected) for t in trend_analyses),
            "forecast_coverage": len(forecasts),
            "key_insights": self._extract_key_insights(trend_analyses)
        }

    def _extract_key_insights(self, trend_analyses: List[TrendAnalysis]) -> List[str]:
        """Extrait les insights clés de l'analyse."""
        insights = []
        
        # Insight sur les tendances dominantes
        improving_count = len([t for t in trend_analyses if t.trend_direction == TrendDirection.IMPROVING])
        declining_count = len([t for t in trend_analyses if t.trend_direction == TrendDirection.DECLINING])
        
        if improving_count > declining_count:
            insights.append("Tendance générale d'amélioration observée")
        elif declining_count > improving_count:
            insights.append("Tendance générale de dégradation observée - attention requise")
        else:
            insights.append("Situation globalement stable")
        
        # Insight sur les anomalies
        high_anomaly_entities = [t for t in trend_analyses if len(t.anomalies_detected) > 2]
        if high_anomaly_entities:
            insights.append(f"{len(high_anomaly_entities)} entités présentent des anomalies fréquentes")
        
        return insights

    # Méthodes helper supplémentaires
    def _calculate_change_percentage(self, time_series: List[TimeSeriesPoint]) -> float:
        """Calcule le pourcentage de changement du début à la fin."""
        if len(time_series) < 2:
            return 0.0
        
        start_value = time_series[0].value
        end_value = time_series[-1].value
        
        if start_value == 0:
            return 0.0
        
        return ((end_value - start_value) / start_value) * 100

    async def _generate_trend_summary(
        self,
        entity_id: str,
        metric_type: MetricType,
        direction: TrendDirection,
        strength: float,
        anomalies: List[Dict[str, Any]]
    ) -> str:
        """Génère un résumé textuel de la tendance."""
        direction_text = {
            TrendDirection.IMPROVING: "amélioration",
            TrendDirection.DECLINING: "dégradation", 
            TrendDirection.STABLE: "stabilité",
            TrendDirection.VOLATILE: "volatilité"
        }.get(direction, "évolution inconnue")
        
        strength_text = {
            True: "forte",
            False: "modérée"
        }[strength > 0.7]
        
        summary = f"Tendance de {direction_text} {strength_text} pour {entity_id}"
        
        if anomalies:
            summary += f" avec {len(anomalies)} anomalies détectées"
        
        return summary


# Tool function for agent integration
async def temporal_analyzer_tool(
    entities: List[Dict[str, Any]],
    metric_types: List[str],
    start_date: str,
    end_date: str,
    include_forecasts: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    Outil d'analyse temporelle pour les agents.
    """
    analyzer = TemporalAnalyzer()
    
    # Convertir les dates
    try:
        start_time = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
    except:
        # Fallback sur dates par défaut
        end_time = datetime.now()
        start_time = end_time - timedelta(days=90)
    
    # Convertir les types de métriques
    metrics = []
    for metric_str in metric_types:
        try:
            metrics.append(MetricType(metric_str))
        except ValueError:
            continue
    
    if not metrics:
        metrics = [MetricType.RISK_LEVEL, MetricType.CONTROL_EFFECTIVENESS]
    
    try:
        report = await analyzer.analyze_trends(
            entities=entities,
            metric_types=metrics,
            time_range=(start_time, end_time),
            include_forecasts=include_forecasts
        )
        
        return {
            "success": True,
            "analysis_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat()
            },
            "trend_analyses": [
                {
                    "entity_id": t.entity_id,
                    "entity_name": t.entity_name,
                    "metric_type": t.metric_type.value,
                    "trend_direction": t.trend_direction.value,
                    "trend_strength": t.trend_strength,
                    "slope": t.slope,
                    "anomalies_count": len(t.anomalies_detected),
                    "summary": t.summary
                }
                for t in report.trend_analyses
            ],
            "comparative_analysis": report.comparative_analysis,
            "forecasts": report.forecasts,
            "recommendations": report.recommendations,
            "summary": report.summary
        }
        
    except Exception as e:
        logger.error(f"Erreur dans temporal_analyzer_tool: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "trend_analyses": []
        }


def get_temporal_analyzer(data_source=None):
    """Factory function pour obtenir une instance de TemporalAnalyzer."""
    return TemporalAnalyzer(data_source=data_source) 