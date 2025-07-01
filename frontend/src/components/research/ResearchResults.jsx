import React, { useState, useRef, useEffect } from 'react';
import { 
  FileText, 
  Download, 
  ExternalLink, 
  Copy, 
  Share2, 
  BookOpen,
  BarChart3,
  Clock,
  Users,
  CheckCircle,
  Eye,
  Maximize2,
  ChevronDown,
  ChevronRight,
  Search,
  Zap,
  TrendingUp,
  Target,
  AlertCircle,
  MoreVertical,
  FileJson,
  FileSpreadsheet
} from 'lucide-react';

const ResearchResults = ({ results, query }) => {
  const [activeTab, setActiveTab] = useState('report');
  const [expandedSection, setExpandedSection] = useState(null);
  const [showFullReport, setShowFullReport] = useState(false);
  const [copySuccess, setCopySuccess] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const exportMenuRef = useRef(null);

  // Handle click outside export menu
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (exportMenuRef.current && !exportMenuRef.current.contains(event.target)) {
        setShowExportMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Handle case where results is null or undefined
  if (!results) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="text-center text-gray-500">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Available</h3>
          <p className="text-gray-600">Start a research query to see results here.</p>
        </div>
      </div>
    );
  }

  const handleCopyReport = async () => {
    try {
      await navigator.clipboard.writeText(results.report || '');
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy report:', err);
    }
  };

  const handleDownloadReport = () => {
    const blob = new Blob([results.report || ''], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-report-${Date.now()}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleShareReport = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'Research Report',
          text: query || 'Research Report',
          url: window.location.href
        });
      } catch (err) {
        console.error('Error sharing:', err);
      }
    } else {
      // Fallback to copying URL
      await navigator.clipboard.writeText(window.location.href);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  const handleExportJSON = () => {
    const exportData = {
      query,
      timestamp: new Date().toISOString(),
      results: {
        research_id: results.research_id,
        report: results.report,
        sources_used: results.sources_used,
        citations: results.citations,
        total_tokens_used: results.total_tokens_used,
        execution_time: results.execution_time,
        subagent_count: results.subagent_count,
        created_at: results.created_at
      }
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-data-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleExportCSV = () => {
    if (!results.sources_used || results.sources_used.length === 0) {
      return;
    }

    const csvHeaders = ['Title', 'URL', 'Relevance Score', 'Date', 'Snippet'];
    const csvRows = results.sources_used.map(source => [
      `"${(source.title || '').replace(/"/g, '""')}"`,
      `"${(source.url || '').replace(/"/g, '""')}"`,
      source.relevance_score || 0,
      `"${(source.date || '').replace(/"/g, '""')}"`,
      `"${(source.snippet || '').replace(/"/g, '""')}"`
    ]);

    const csvContent = [csvHeaders.join(','), ...csvRows.map(row => row.join(','))].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-sources-${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const formatTime = (seconds) => {
    if (!seconds) return '0s';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Unknown';
    return new Date(dateString).toLocaleString();
  };

  // Enhanced data processing functions
  const calculateAverageRelevance = () => {
    if (!results.sources_used || results.sources_used.length === 0) return 0;
    const total = results.sources_used.reduce((sum, source) => sum + (source.relevance_score || 0), 0);
    return Math.round((total / results.sources_used.length) * 100);
  };

  const getReportLength = () => {
    if (!results.report) return '0';
    const length = results.report.length;
    if (length < 1000) return `${length}`;
    if (length < 1000000) return `${(length / 1000).toFixed(1)}k`;
    return `${(length / 1000000).toFixed(1)}M`;
  };

  const getSourceQualityDistribution = () => {
    if (!results.sources_used || results.sources_used.length === 0) {
      return { high: 0, medium: 0, low: 0 };
    }

    return results.sources_used.reduce((acc, source) => {
      const score = source.relevance_score || 0;
      if (score >= 0.8) acc.high++;
      else if (score >= 0.5) acc.medium++;
      else acc.low++;
      return acc;
    }, { high: 0, medium: 0, low: 0 });
  };

  const getCitationStats = () => {
    if (!results.citations || results.citations.length === 0) {
      return { total: 0, unique: 0, mostCited: null };
    }

    const uniqueUrls = new Set(results.citations.map(c => c.url));
    const mostCited = results.citations.reduce((max, citation) => 
      (citation.times_cited || 0) > (max.times_cited || 0) ? citation : max
    );

    return {
      total: results.citations.length,
      unique: uniqueUrls.size,
      mostCited: mostCited.times_cited > 0 ? mostCited : null
    };
  };

  const ReportSection = ({ children, title, isExpanded, onToggle }) => (
    <div className="border border-gray-200 rounded-lg overflow-hidden mb-4">
      <button
        onClick={onToggle}
        className="w-full px-4 py-3 bg-gray-50 text-left flex items-center justify-between hover:bg-gray-100 transition-colors"
      >
        <span className="font-medium text-gray-900">{title}</span>
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-gray-500" />
        ) : (
          <ChevronRight className="w-4 h-4 text-gray-500" />
        )}
      </button>
      {isExpanded && (
        <div className="p-4 bg-white">
          {children}
        </div>
      )}
    </div>
  );

  const tabs = [
    { id: 'report', label: 'Research Report', icon: FileText },
    { id: 'sources', label: 'Sources', icon: ExternalLink },
    { id: 'citations', label: 'Citations', icon: BookOpen },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 }
  ];

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-6 h-6 text-green-500" />
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Research Complete
              </h2>
              <p className="text-sm text-gray-600">
                Query: {query || 'Research completed successfully'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleCopyReport}
              className={`p-2 rounded-lg transition-colors ${
                copySuccess 
                  ? 'text-green-600 bg-green-50' 
                  : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
              }`}
              title="Copy report"
            >
              <Copy className="w-4 h-4" />
            </button>
            <button
              onClick={handleDownloadReport}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Download report"
            >
              <Download className="w-4 h-4" />
            </button>
            <button
              onClick={handleShareReport}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Share report"
            >
              <Share2 className="w-4 h-4" />
            </button>
            
            {/* Export Menu */}
            <div className="relative" ref={exportMenuRef}>
              <button
                onClick={() => setShowExportMenu(!showExportMenu)}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                title="Export options"
              >
                <MoreVertical className="w-4 h-4" />
              </button>
              
              {showExportMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-10">
                  <button
                    onClick={() => {
                      handleExportJSON();
                      setShowExportMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                  >
                    <FileJson className="w-4 h-4" />
                    <span>Export as JSON</span>
                  </button>
                  <button
                    onClick={() => {
                      handleExportCSV();
                      setShowExportMenu(false);
                    }}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center space-x-2"
                    disabled={!results.sources_used || results.sources_used.length === 0}
                  >
                    <FileSpreadsheet className="w-4 h-4" />
                    <span>Export Sources as CSV</span>
                  </button>
                </div>
              )}
            </div>
            
            <button
              onClick={() => setShowFullReport(!showFullReport)}
              className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
              title="Full screen"
            >
              <Maximize2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {results.sources_used?.length || 0}
            </div>
            <div className="text-xs text-gray-500">Sources</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {results.total_tokens_used?.toLocaleString() || 0}
            </div>
            <div className="text-xs text-gray-500">Tokens</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {formatTime(results.execution_time)}
            </div>
            <div className="text-xs text-gray-500">Duration</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {results.subagent_count || 0}
            </div>
            <div className="text-xs text-gray-500">Agents</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-6 border-b border-gray-200">
        <div className="flex space-x-6">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center space-x-2 py-3 border-b-2 transition-colors ${
                activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              <span className="font-medium">{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="p-6">
        {activeTab === 'report' && (
          <div className="space-y-4">
            {/* Report Content */}
            <div 
              className={`prose max-w-none ${
                showFullReport ? 'max-h-none' : 'max-h-96 overflow-y-auto'
              }`}
            >
              {results.report ? (
                <div 
                  className="text-gray-800 whitespace-pre-wrap leading-relaxed"
                  dangerouslySetInnerHTML={{
                    __html: results.report
                      .replace(/\n/g, '<br/>')
                      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                      .replace(/\*(.*?)\*/g, '<em>$1</em>')
                      .replace(/`(.*?)`/g, '<code class="bg-gray-100 px-1 rounded">$1</code>')
                  }}
                />
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No report content available</p>
                </div>
              )}
            </div>
            
            {!showFullReport && results.report && results.report.length > 2000 && (
              <button
                onClick={() => setShowFullReport(true)}
                className="text-blue-600 hover:text-blue-700 font-medium"
              >
                Show full report
              </button>
            )}
          </div>
        )}

        {activeTab === 'sources' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-medium text-gray-900">
                Sources Used ({results.sources_used?.length || 0})
              </h3>
            </div>
            
            <div className="grid gap-4">
              {results.sources_used?.length > 0 ? (
                results.sources_used.map((source, index) => (
                  <div 
                    key={index}
                    className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">
                          {source.title || `Source ${index + 1}`}
                        </h4>
                        <p className="text-sm text-gray-600 mb-2">
                          {source.snippet || source.description || 'No description available'}
                        </p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>Relevance: {Math.round((source.relevance_score || 0) * 100)}%</span>
                          {source.date && <span>Date: {formatDate(source.date)}</span>}
                        </div>
                      </div>
                      {source.url && (
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="ml-4 p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No sources available</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'citations' && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-900">
              Citations ({results.citations?.length || 0})
            </h3>
            
            <div className="space-y-3">
              {results.citations?.length > 0 ? (
                results.citations.map((citation, index) => (
                  <div 
                    key={index}
                    className="border-l-4 border-blue-200 pl-4 py-2"
                  >
                    <div className="flex items-center space-x-2 mb-1">
                      <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        [{citation.index || index + 1}]
                      </span>
                      <span className="font-medium text-gray-900">
                        {citation.title || `Citation ${index + 1}`}
                      </span>
                    </div>
                    {citation.url && (
                      <a 
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-blue-600 hover:text-blue-700 flex items-center space-x-1"
                      >
                        <span>{citation.url}</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                    {citation.times_cited && (
                      <div className="text-xs text-gray-500 mt-1">
                        Cited {citation.times_cited} time{citation.times_cited !== 1 ? 's' : ''}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <BookOpen className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No citations available</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-6">
            <h3 className="text-lg font-medium text-gray-900">Research Analytics</h3>
            
            {/* Research Metadata */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Clock className="w-4 h-4 mr-2" />
                  Execution Details
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Started:</span>
                    <span className="text-gray-900">{formatDate(results.created_at)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Duration:</span>
                    <span className="text-gray-900">{formatTime(results.execution_time)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Research ID:</span>
                    <span className="text-gray-900 font-mono text-xs">{results.research_id || 'N/A'}</span>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Users className="w-4 h-4 mr-2" />
                  Agent Performance
                </h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Agents Used:</span>
                    <span className="text-gray-900">{results.subagent_count || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Total Tokens:</span>
                    <span className="text-gray-900">{results.total_tokens_used?.toLocaleString() || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg. per Agent:</span>
                    <span className="text-gray-900">
                      {results.subagent_count > 0 
                        ? Math.round((results.total_tokens_used || 0) / results.subagent_count).toLocaleString()
                        : 0
                      }
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Quality Metrics */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                <TrendingUp className="w-4 h-4 mr-2" />
                Quality Metrics
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {calculateAverageRelevance()}%
                  </div>
                  <div className="text-xs text-gray-500">Avg Relevance</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {results.sources_used?.length || 0}
                  </div>
                  <div className="text-xs text-gray-500">Sources</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {getCitationStats().unique}
                  </div>
                  <div className="text-xs text-gray-500">Unique Citations</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">
                    {getReportLength()}
                  </div>
                  <div className="text-xs text-gray-500">Report Length</div>
                </div>
              </div>
            </div>

            {/* Source Quality Distribution */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <Target className="w-4 h-4 mr-2" />
                  Source Quality Distribution
                </h4>
                <div className="space-y-3">
                  {(() => {
                    const distribution = getSourceQualityDistribution();
                    const total = distribution.high + distribution.medium + distribution.low;
                    return (
                      <>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                            <span className="text-sm text-gray-700">High Quality (80%+)</span>
                          </div>
                          <span className="text-sm font-medium text-gray-900">
                            {distribution.high} ({total > 0 ? Math.round((distribution.high / total) * 100) : 0}%)
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                            <span className="text-sm text-gray-700">Medium Quality (50-79%)</span>
                          </div>
                          <span className="text-sm font-medium text-gray-900">
                            {distribution.medium} ({total > 0 ? Math.round((distribution.medium / total) * 100) : 0}%)
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                            <span className="text-sm text-gray-700">Low Quality (&lt;50%)</span>
                          </div>
                          <span className="text-sm font-medium text-gray-900">
                            {distribution.low} ({total > 0 ? Math.round((distribution.low / total) * 100) : 0}%)
                          </span>
                        </div>
                      </>
                    );
                  })()}
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="font-medium text-gray-900 mb-3 flex items-center">
                  <BookOpen className="w-4 h-4 mr-2" />
                  Citation Analysis
                </h4>
                <div className="space-y-2 text-sm">
                  {(() => {
                    const citationStats = getCitationStats();
                    return (
                      <>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Total Citations:</span>
                          <span className="text-gray-900">{citationStats.total}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Unique Sources:</span>
                          <span className="text-gray-900">{citationStats.unique}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Duplication Rate:</span>
                          <span className="text-gray-900">
                            {citationStats.total > 0 
                              ? Math.round(((citationStats.total - citationStats.unique) / citationStats.total) * 100)
                              : 0
                            }%
                          </span>
                        </div>
                        {citationStats.mostCited && (
                          <div className="pt-2 border-t border-gray-200">
                            <div className="text-gray-600 text-xs mb-1">Most Cited Source:</div>
                            <div className="text-gray-900 text-xs font-medium truncate">
                              {citationStats.mostCited.title} ({citationStats.mostCited.times_cited} times)
                            </div>
                          </div>
                        )}
                      </>
                    );
                  })()}
                </div>
              </div>
            </div>

            {/* Report Sections */}
            {results.report_sections && (
              <div>
                <h4 className="font-medium text-gray-900 mb-3">Report Structure</h4>
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="space-y-1">
                    {results.report_sections.map((section, index) => (
                      <div key={index} className="text-sm text-gray-700">
                        {index + 1}. {section}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchResults;