import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  CheckCircle, 
  Loader2, 
  Search, 
  FileText, 
  Users, 
  BarChart3,
  AlertTriangle,
  Activity,
  Zap,
  Target,
  TrendingUp
} from 'lucide-react';

const ResearchProgress = ({ status, isActive }) => {
  const [elapsedTime, setElapsedTime] = useState(0);
  const [startTime] = useState(Date.now());

  useEffect(() => {
    if (isActive) {
      const interval = setInterval(() => {
        setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [isActive, startTime]);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusInfo = () => {
    if (!status) return { stage: 'Initializing', progress: 0, color: 'blue' };

    switch (status.status) {
      case 'started':
        return { stage: 'Planning Research', progress: 10, color: 'blue' };
      case 'planning':
        return { stage: 'Creating Research Plan', progress: 20, color: 'blue' };
      case 'executing':
        return { stage: 'Agents Researching', progress: 40, color: 'yellow' };
      case 'synthesizing':
        return { stage: 'Synthesizing Results', progress: 80, color: 'orange' };
      case 'citing':
        return { stage: 'Adding Citations', progress: 90, color: 'purple' };
      case 'completed':
        return { stage: 'Research Complete', progress: 100, color: 'green' };
      case 'failed':
        return { stage: 'Research Failed', progress: 0, color: 'red' };
      default:
        return { stage: 'Processing', progress: 30, color: 'blue' };
    }
  };

  const { stage, progress, color } = getStatusInfo();

  // Get real agent activities from backend status
  const getAgentActivities = () => {
    if (!status || !isActive || !status.progress?.agent_activities) return [];
    
    // Use real agent activity data from the backend
    return status.progress.agent_activities.map((activity, index) => ({
      id: activity.agent_id || index + 1,
      name: activity.agent_name || `Agent ${index + 1}`,
      status: activity.status || 'waiting',
      task: activity.current_task || 'Processing...',
      progress: activity.progress_percentage || 0,
      tokensUsed: activity.tokens_used || 0
    }));
  };

  const agentActivities = getAgentActivities();

  const getAgentIcon = (agentStatus) => {
    switch (agentStatus) {
      case 'searching':
        return <Search className="w-4 h-4 text-blue-500 animate-pulse" />;
      case 'analyzing':
        return <BarChart3 className="w-4 h-4 text-orange-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <AlertTriangle className="w-4 h-4 text-red-500" />;
      case 'waiting':
        return <Clock className="w-4 h-4 text-gray-400" />;
      default:
        return <Activity className="w-4 h-4 text-gray-500" />;
    }
  };

  const getAgentStatusColor = (agentStatus) => {
    switch (agentStatus) {
      case 'searching':
        return 'bg-blue-100 text-blue-800';
      case 'analyzing':
        return 'bg-orange-100 text-orange-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'waiting':
        return 'bg-gray-100 text-gray-600';
      default:
        return 'bg-gray-100 text-gray-600';
    }
  };

  const getProgressBarColor = () => {
    switch (color) {
      case 'green':
        return 'bg-green-500';
      case 'red':
        return 'bg-red-500';
      case 'yellow':
        return 'bg-yellow-500';
      case 'orange':
        return 'bg-orange-500';
      case 'purple':
        return 'bg-purple-500';
      default:
        return 'bg-blue-500';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
      {/* Header Section */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {isActive ? (
            <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
          ) : status?.status === 'completed' ? (
            <CheckCircle className="w-6 h-6 text-green-500" />
          ) : status?.status === 'failed' ? (
            <AlertTriangle className="w-6 h-6 text-red-500" />
          ) : (
            <Clock className="w-6 h-6 text-gray-500" />
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">{stage}</h3>
            <p className="text-sm text-gray-600">
              {status?.message || 'Research in progress...'}
            </p>
          </div>
        </div>
        
        <div className="text-right">
          <div className="text-sm text-gray-500">Elapsed Time</div>
          <div className="text-lg font-mono font-semibold text-gray-900">
            {formatTime(elapsedTime)}
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>Progress</span>
          <span>{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all duration-500 ease-out ${getProgressBarColor()}`}
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Research Stages */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
        {[
          { stage: 'Plan', icon: FileText, threshold: 20, description: 'Research planning' },
          { stage: 'Search', icon: Search, threshold: 40, description: 'Information gathering' },
          { stage: 'Analyze', icon: BarChart3, threshold: 60, description: 'Data analysis' },
          { stage: 'Synthesize', icon: Users, threshold: 80, description: 'Content synthesis' },
          { stage: 'Complete', icon: CheckCircle, threshold: 100, description: 'Finalization' }
        ].map((item, index) => {
          const isCompleted = progress >= item.threshold;
          const isActive = progress > (index * 20) && progress < item.threshold;
          
          return (
            <div 
              key={index}
              className={`flex flex-col items-center p-3 rounded-lg border-2 transition-all duration-300 ${
                isCompleted 
                  ? 'border-green-200 bg-green-50 text-green-700 shadow-sm' 
                  : isActive 
                    ? 'border-blue-200 bg-blue-50 text-blue-700 shadow-sm' 
                    : 'border-gray-200 bg-gray-50 text-gray-500'
              }`}
              title={item.description}
            >
              <item.icon className={`w-5 h-5 mb-1 ${isActive ? 'animate-pulse' : ''}`} />
              <span className="text-xs font-medium">{item.stage}</span>
            </div>
          );
        })}
      </div>

      {/* Agent Activities */}
      {isActive && agentActivities.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <Users className="w-4 h-4 mr-2" />
            Agent Activities ({agentActivities.length} active)
          </h4>
          <div className="space-y-3">
            {agentActivities.map((agent) => (
              <div 
                key={agent.id}
                className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-100 hover:shadow-sm transition-shadow"
              >
                <div className="flex items-center space-x-3 flex-1">
                  {getAgentIcon(agent.status)}
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <div className="text-sm font-medium text-gray-900">
                        {agent.name}
                      </div>
                      <span className={`px-2 py-1 text-xs rounded-full font-medium ${getAgentStatusColor(agent.status)}`}>
                        {agent.status}
                      </span>
                    </div>
                    <div className="text-xs text-gray-600 mb-2">
                      {agent.task}
                    </div>
                    {/* Agent Progress Bar */}
                    <div className="flex items-center space-x-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                        <div 
                          className="bg-blue-400 h-1.5 rounded-full transition-all duration-300"
                          style={{ width: `${agent.progress}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-500 w-8">{agent.progress}%</span>
                    </div>
                  </div>
                </div>
                <div className="ml-4 text-right">
                  <div className="text-xs text-gray-500">Tokens</div>
                  <div className="text-sm font-medium text-gray-700">{agent.tokensUsed}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Performance Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Users className="w-4 h-4 text-blue-500 mr-1" />
            <span className="text-lg font-semibold text-gray-900">
              {status?.agents?.length || agentActivities.length || 3}
            </span>
          </div>
          <div className="text-xs text-gray-500">Active Agents</div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Search className="w-4 h-4 text-green-500 mr-1" />
            <span className="text-lg font-semibold text-gray-900">
              {status?.sources_found || Math.floor(progress / 10) || '...'}
            </span>
          </div>
          <div className="text-xs text-gray-500">Sources Found</div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <Zap className="w-4 h-4 text-orange-500 mr-1" />
            <span className="text-lg font-semibold text-gray-900">
              {status?.tokens_used || agentActivities.reduce((sum, agent) => sum + agent.tokensUsed, 0) || '...'}
            </span>
          </div>
          <div className="text-xs text-gray-500">Tokens Used</div>
        </div>
        
        <div className="text-center">
          <div className="flex items-center justify-center mb-1">
            <TrendingUp className="w-4 h-4 text-purple-500 mr-1" />
            <span className="text-lg font-semibold text-gray-900">
              {Math.round((progress / 100) * (status?.estimated_completion || 100))}%
            </span>
          </div>
          <div className="text-xs text-gray-500">Efficiency</div>
        </div>
      </div>

      {/* Status Details */}
      {status?.details && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-start space-x-2">
            <Target className="w-4 h-4 text-blue-600 mt-0.5" />
            <div>
              <div className="text-sm font-medium text-blue-900">Current Focus</div>
              <div className="text-sm text-blue-700">{status.details}</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResearchProgress;