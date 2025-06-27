"""
Dashboard Service for Phase 4 Kenobi Code Analysis Agent
Provides data aggregation and real-time updates for the web dashboard
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
from collections import defaultdict

from app.services.repository_service import RepositoryService
from app.services.cache_service import cache_service, cache_result
from app.engines.analytics_engine import analytics_engine
from app.engines.quality_engine import QualityEngine
from app.engines.vector_service import VectorService
from app.agents.repository_analysis_agent import RepositoryAnalysisAgent
from app.agents.dependency_analysis_agent import DependencyAnalysisAgent


class DashboardService:
    """Service for aggregating and providing dashboard data"""
    
    def __init__(self):
        self.repository_service = RepositoryService()
        self.quality_engine = QualityEngine()
        self.vector_service = VectorService()
        self.repo_analysis_agent = RepositoryAnalysisAgent()
        self.dependency_analysis_agent = DependencyAnalysisAgent()
        
        # Real-time data cache
        self.real_time_cache = {}
        self.last_update = datetime.now()
        
    @cache_result(ttl=300, key_prefix="dashboard_overview")  # 5 minutes
    async def get_dashboard_overview(self) -> Dict[str, Any]:
        """Get comprehensive dashboard overview"""
        try:
            overview = {
                "timestamp": datetime.now().isoformat(),
                "system_health": await self._get_system_health(),
                "repository_summary": await self._get_repository_summary(),
                "quality_overview": await self._get_quality_overview(),
                "performance_metrics": await self._get_performance_metrics(),
                "recent_activity": await self._get_recent_activity(),
                "alerts": await self._get_active_alerts()
            }
            
            return overview
            
        except Exception as e:
            return {
                "error": f"Failed to get dashboard overview: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_real_time_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data (not cached)"""
        try:
            real_time_data = {
                "timestamp": datetime.now().isoformat(),
                "analytics": await analytics_engine.get_real_time_data(),
                "system_status": await self._get_system_status(),
                "active_processes": await self._get_active_processes(),
                "live_metrics": await self._get_live_metrics()
            }
            
            # Update cache
            self.real_time_cache = real_time_data
            self.last_update = datetime.now()
            
            return real_time_data
            
        except Exception as e:
            return {
                "error": f"Failed to get real-time data: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    @cache_result(ttl=600, key_prefix="repository_dashboard")  # 10 minutes
    async def get_repository_dashboard(self, repository_id: str) -> Dict[str, Any]:
        """Get detailed dashboard data for a specific repository"""
        try:
            repository = await self.repository_service.get_repository_metadata(repository_id)
            if not repository:
                raise ValueError(f"Repository {repository_id} not found")
            
            dashboard_data = {
                "repository_id": repository_id,
                "repository_name": repository.name,
                "timestamp": datetime.now().isoformat(),
                "overview": await self._get_repository_overview(repository_id),
                "quality_metrics": await self._get_repository_quality_metrics(repository_id),
                "dependency_analysis": await self._get_repository_dependency_analysis(repository_id),
                "code_structure": await self._get_repository_code_structure(repository_id),
                "trends": await self._get_repository_trends(repository_id),
                "recommendations": await self._get_repository_recommendations(repository_id)
            }
            
            return dashboard_data
            
        except Exception as e:
            return {
                "error": f"Failed to get repository dashboard: {str(e)}",
                "repository_id": repository_id,
                "timestamp": datetime.now().isoformat()
            }
    
    @cache_result(ttl=900, key_prefix="quality_dashboard")  # 15 minutes
    async def get_quality_dashboard(self) -> Dict[str, Any]:
        """Get quality-focused dashboard data"""
        try:
            quality_dashboard = {
                "timestamp": datetime.now().isoformat(),
                "overall_quality": await self._get_overall_quality_metrics(),
                "quality_trends": await self._get_quality_trends(),
                "quality_distribution": await self._get_quality_distribution(),
                "top_issues": await self._get_top_quality_issues(),
                "improvement_opportunities": await self._get_improvement_opportunities(),
                "quality_by_language": await self._get_quality_by_language(),
                "quality_by_repository": await self._get_quality_by_repository()
            }
            
            return quality_dashboard
            
        except Exception as e:
            return {
                "error": f"Failed to get quality dashboard: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    @cache_result(ttl=1200, key_prefix="dependency_dashboard")  # 20 minutes
    async def get_dependency_dashboard(self) -> Dict[str, Any]:
        """Get dependency-focused dashboard data"""
        try:
            dependency_dashboard = {
                "timestamp": datetime.now().isoformat(),
                "dependency_overview": await self._get_dependency_overview(),
                "dependency_health": await self._get_dependency_health_overview(),
                "circular_dependencies": await self._get_circular_dependencies_overview(),
                "external_dependencies": await self._get_external_dependencies_overview(),
                "dependency_trends": await self._get_dependency_trends(),
                "integration_opportunities": await self._get_integration_opportunities()
            }
            
            return dependency_dashboard
            
        except Exception as e:
            return {
                "error": f"Failed to get dependency dashboard: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_search_dashboard(self) -> Dict[str, Any]:
        """Get search and discovery dashboard data"""
        try:
            search_dashboard = {
                "timestamp": datetime.now().isoformat(),
                "vector_statistics": self.vector_service.get_collection_stats(),
                "search_analytics": await self._get_search_analytics(),
                "popular_searches": await self._get_popular_searches(),
                "code_clusters": await self._get_code_clusters(),
                "similarity_insights": await self._get_similarity_insights()
            }
            
            return search_dashboard
            
        except Exception as e:
            return {
                "error": f"Failed to get search dashboard: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics"""
        try:
            # Get analytics summary
            analytics_summary = await analytics_engine.get_metrics_summary(hours=1)
            
            # Calculate health score
            performance = analytics_summary.get("performance", {})
            avg_response_time = performance.get("response_time", {}).get("avg", 0)
            error_rate = performance.get("error_rate", {}).get("avg", 0)
            
            health_score = 1.0
            if avg_response_time > 1000:  # > 1 second
                health_score -= 0.3
            if error_rate > 0.05:  # > 5%
                health_score -= 0.4
            
            health_status = "healthy"
            if health_score < 0.5:
                health_status = "critical"
            elif health_score < 0.7:
                health_status = "warning"
            
            return {
                "status": health_status,
                "score": round(health_score, 2),
                "avg_response_time": avg_response_time,
                "error_rate": error_rate,
                "uptime_hours": analytics_summary.get("system", {}).get("uptime_hours", 0)
            }
            
        except Exception as e:
            return {"status": "unknown", "error": str(e)}
    
    async def _get_repository_summary(self) -> Dict[str, Any]:
        """Get repository summary statistics"""
        try:
            repositories = await self.repository_service.list_repositories()
            
            total_repos = len(repositories)
            total_elements = 0
            languages = set()
            
            for repo in repositories:
                elements = await self.repository_service.indexing_service.get_repository_elements(repo.id)
                total_elements += len(elements)
                
                for element in elements:
                    language = element.get("language")
                    if language:
                        languages.add(language)
            
            return {
                "total_repositories": total_repos,
                "total_code_elements": total_elements,
                "supported_languages": len(languages),
                "languages": list(languages),
                "avg_elements_per_repo": round(total_elements / max(1, total_repos), 2)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_quality_overview(self) -> Dict[str, Any]:
        """Get overall quality metrics overview"""
        try:
            repositories = await self.repository_service.list_repositories()
            
            quality_scores = []
            total_issues = 0
            
            for repo in repositories[:10]:  # Limit for performance
                try:
                    elements = await self.repository_service.indexing_service.get_repository_elements(repo.id)
                    
                    for element in elements[:20]:  # Limit elements per repo
                        try:
                            code_element = self._dict_to_code_element(element)
                            quality_result = await self.quality_engine.analyze_element_quality(code_element)
                            
                            if "overall_score" in quality_result:
                                quality_scores.append(quality_result["overall_score"])
                            
                            issues = quality_result.get("issues", [])
                            total_issues += len(issues)
                            
                        except Exception:
                            continue
                except Exception:
                    continue
            
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return {
                "average_quality_score": round(avg_quality, 2),
                "total_quality_issues": total_issues,
                "elements_analyzed": len(quality_scores),
                "quality_grade": self._get_quality_grade(avg_quality)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics overview"""
        try:
            analytics_summary = await analytics_engine.get_metrics_summary(hours=24)
            performance = analytics_summary.get("performance", {})
            
            return {
                "avg_response_time": performance.get("response_time", {}).get("avg", 0),
                "max_response_time": performance.get("response_time", {}).get("max", 0),
                "p95_response_time": performance.get("response_time", {}).get("p95", 0),
                "throughput": performance.get("throughput", {}).get("total", 0),
                "error_rate": performance.get("error_rate", {}).get("avg", 0)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        try:
            # This would typically come from activity logs
            # For now, return mock data based on analytics
            analytics_summary = await analytics_engine.get_metrics_summary(hours=1)
            usage = analytics_summary.get("usage", {})
            
            activities = []
            
            # API calls activity
            api_calls = usage.get("total_api_calls", 0)
            if api_calls > 0:
                activities.append({
                    "type": "api_usage",
                    "description": f"{api_calls} API calls in the last hour",
                    "timestamp": datetime.now().isoformat(),
                    "severity": "info"
                })
            
            # Repository access activity
            repo_access = usage.get("repository_access", {})
            if repo_access:
                most_accessed = max(repo_access.items(), key=lambda x: x[1])
                activities.append({
                    "type": "repository_access",
                    "description": f"Repository {most_accessed[0]} accessed {most_accessed[1]} times",
                    "timestamp": datetime.now().isoformat(),
                    "severity": "info"
                })
            
            return activities[:10]  # Return last 10 activities
            
        except Exception as e:
            return [{"type": "error", "description": str(e)}]
    
    async def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get active system alerts"""
        try:
            analytics_summary = await analytics_engine.get_metrics_summary(hours=1)
            alerts_summary = analytics_summary.get("alerts", {})
            
            return alerts_summary.get("recent_triggers", [])
            
        except Exception as e:
            return [{"type": "error", "description": str(e)}]
    
    async def _get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        try:
            cache_stats = await cache_service.get_cache_stats()
            vector_stats = self.vector_service.get_collection_stats()
            
            return {
                "cache_status": "healthy" if cache_stats.get("hit_rate", 0) > 0.5 else "warning",
                "vector_db_status": "healthy" if vector_stats.get("total_documents", 0) > 0 else "warning",
                "cache_hit_rate": cache_stats.get("hit_rate", 0),
                "vector_documents": vector_stats.get("total_documents", 0)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_active_processes(self) -> List[Dict[str, Any]]:
        """Get currently active processes"""
        # This would typically track active analysis tasks
        # For now, return mock data
        return [
            {
                "process_id": "analysis_001",
                "type": "repository_analysis",
                "status": "running",
                "progress": 75,
                "started_at": (datetime.now() - timedelta(minutes=5)).isoformat()
            }
        ]
    
    async def _get_live_metrics(self) -> Dict[str, Any]:
        """Get live system metrics"""
        try:
            real_time_data = await analytics_engine.get_real_time_data()
            
            return {
                "current_throughput": real_time_data.get("performance", {}).get("current_throughput", 0),
                "active_sessions": real_time_data.get("usage", {}).get("active_sessions", 0),
                "memory_usage": 0,  # Would need system monitoring
                "cpu_usage": 0     # Would need system monitoring
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_repository_overview(self, repository_id: str) -> Dict[str, Any]:
        """Get repository overview metrics"""
        try:
            analysis = await self.repo_analysis_agent.analyze_repository_comprehensive(repository_id)
            
            return {
                "overall_score": analysis.get("overall_score", 0),
                "total_elements": analysis.get("code_structure", {}).get("total_elements", 0),
                "languages": list(analysis.get("code_structure", {}).get("languages", {}).keys()),
                "last_analyzed": analysis.get("analysis_timestamp"),
                "recommendations_count": len(analysis.get("recommendations", []))
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_repository_quality_metrics(self, repository_id: str) -> Dict[str, Any]:
        """Get repository quality metrics"""
        try:
            analysis = await self.repo_analysis_agent.analyze_repository_comprehensive(repository_id)
            quality_metrics = analysis.get("quality_metrics", {})
            
            return {
                "average_score": quality_metrics.get("average_quality_score", 0),
                "elements_analyzed": quality_metrics.get("elements_analyzed", 0),
                "detailed_metrics": quality_metrics.get("detailed_metrics", {}),
                "quality_distribution": quality_metrics.get("quality_distribution", {})
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_repository_dependency_analysis(self, repository_id: str) -> Dict[str, Any]:
        """Get repository dependency analysis"""
        try:
            health_analysis = await self.dependency_analysis_agent.analyze_dependency_health(repository_id)
            
            return {
                "health_score": health_analysis.get("overall_health_score", 0),
                "health_metrics": health_analysis.get("health_metrics", {}),
                "issues": health_analysis.get("issues", []),
                "strengths": health_analysis.get("strengths", [])
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_repository_code_structure(self, repository_id: str) -> Dict[str, Any]:
        """Get repository code structure analysis"""
        try:
            analysis = await self.repo_analysis_agent.analyze_repository_comprehensive(repository_id)
            code_structure = analysis.get("code_structure", {})
            
            return {
                "element_types": code_structure.get("element_types", {}),
                "languages": code_structure.get("languages", {}),
                "file_extensions": code_structure.get("file_extensions", {}),
                "structure_score": code_structure.get("structure_score", 0)
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _get_repository_trends(self, repository_id: str) -> Dict[str, Any]:
        """Get repository trend analysis"""
        # This would typically analyze historical data
        # For now, return mock trend data
        return {
            "quality_trend": "stable",
            "complexity_trend": "improving",
            "size_trend": "growing",
            "activity_trend": "active"
        }
    
    async def _get_repository_recommendations(self, repository_id: str) -> List[Dict[str, Any]]:
        """Get repository improvement recommendations"""
        try:
            analysis = await self.repo_analysis_agent.analyze_repository_comprehensive(repository_id)
            return analysis.get("recommendations", [])
            
        except Exception as e:
            return [{"type": "error", "description": str(e)}]
    
    def _dict_to_code_element(self, element_dict: Dict) -> Any:
        """Convert dictionary to CodeElement (simplified)"""
        # This is a simplified conversion - in practice you'd use the proper model
        class SimpleCodeElement:
            def __init__(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
        
        return SimpleCodeElement(element_dict)
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to grade"""
        if score >= 0.9:
            return "A+"
        elif score >= 0.8:
            return "A"
        elif score >= 0.7:
            return "B"
        elif score >= 0.6:
            return "C"
        elif score >= 0.5:
            return "D"
        else:
            return "F"
    
    # Additional helper methods for comprehensive dashboard data
    async def _get_overall_quality_metrics(self) -> Dict[str, Any]:
        """Get overall quality metrics across all repositories"""
        # Implementation would aggregate quality data across all repos
        return {"placeholder": "implementation_needed"}
    
    async def _get_quality_trends(self) -> Dict[str, Any]:
        """Get quality trends over time"""
        # Implementation would analyze historical quality data
        return {"placeholder": "implementation_needed"}
    
    async def _get_quality_distribution(self) -> Dict[str, Any]:
        """Get quality score distribution"""
        # Implementation would analyze quality score distribution
        return {"placeholder": "implementation_needed"}
    
    async def _get_top_quality_issues(self) -> List[Dict[str, Any]]:
        """Get top quality issues across repositories"""
        # Implementation would identify most common quality issues
        return []
    
    async def _get_improvement_opportunities(self) -> List[Dict[str, Any]]:
        """Get improvement opportunities"""
        # Implementation would identify improvement opportunities
        return []
    
    async def _get_quality_by_language(self) -> Dict[str, Any]:
        """Get quality metrics by programming language"""
        # Implementation would break down quality by language
        return {}
    
    async def _get_quality_by_repository(self) -> Dict[str, Any]:
        """Get quality metrics by repository"""
        # Implementation would break down quality by repository
        return {}
    
    async def _get_dependency_overview(self) -> Dict[str, Any]:
        """Get dependency overview across all repositories"""
        # Implementation would aggregate dependency data
        return {"placeholder": "implementation_needed"}
    
    async def _get_dependency_health_overview(self) -> Dict[str, Any]:
        """Get dependency health overview"""
        # Implementation would analyze dependency health
        return {"placeholder": "implementation_needed"}
    
    async def _get_circular_dependencies_overview(self) -> Dict[str, Any]:
        """Get circular dependencies overview"""
        # Implementation would identify circular dependencies
        return {"placeholder": "implementation_needed"}
    
    async def _get_external_dependencies_overview(self) -> Dict[str, Any]:
        """Get external dependencies overview"""
        # Implementation would analyze external dependencies
        return {"placeholder": "implementation_needed"}
    
    async def _get_dependency_trends(self) -> Dict[str, Any]:
        """Get dependency trends over time"""
        # Implementation would analyze dependency trends
        return {"placeholder": "implementation_needed"}
    
    async def _get_integration_opportunities(self) -> List[Dict[str, Any]]:
        """Get integration opportunities between repositories"""
        # Implementation would identify integration opportunities
        return []
    
    async def _get_search_analytics(self) -> Dict[str, Any]:
        """Get search usage analytics"""
        # Implementation would analyze search patterns
        return {"placeholder": "implementation_needed"}
    
    async def _get_popular_searches(self) -> List[Dict[str, Any]]:
        """Get most popular search queries"""
        # Implementation would track popular searches
        return []
    
    async def _get_code_clusters(self) -> Dict[str, Any]:
        """Get code clustering analysis"""
        # Implementation would analyze code clusters
        return {"placeholder": "implementation_needed"}
    
    async def _get_similarity_insights(self) -> Dict[str, Any]:
        """Get code similarity insights"""
        # Implementation would analyze code similarity patterns
        return {"placeholder": "implementation_needed"}


# Global dashboard service instance
dashboard_service = DashboardService()