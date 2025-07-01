import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import FunctionalitiesRegistry from '../components/documentation/FunctionalitiesRegistry';
import DocumentationViewer from '../components/documentation/DocumentationViewer';
import DocumentationNavigation from '../components/documentation/DocumentationNavigation';
import DocumentationGenerator from '../components/documentation/DocumentationGenerator';
import DocumentationSearch from '../components/documentation/DocumentationSearch';
import DocumentationStatus from '../components/common/DocumentationStatus';
import { repositoryService } from '../services/repositories';
import { documentationService } from '../services/documentation';
import { useDocumentation } from '../contexts/DocumentationContext';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/common/Tabs';

const Documentation = () => {
  const { repositoryId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Use documentation context
  const { 
    getDocumentation, 
    setDocumentation: setContextDocumentation, 
    getCachedDocumentation 
  } = useDocumentation();
  
  // Get docType from URL query params
  const queryParams = new URLSearchParams(location.search);
  const docTypeParam = queryParams.get('type');
  
  const [repository, setRepository] = useState(null);
  const [selectedBranch, setSelectedBranch] = useState('main');
  const [selectedDocType, setSelectedDocType] = useState(docTypeParam || 'overview');
  const [apiEndpoints, setApiEndpoints] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('view'); // 'view', 'search', 'functionalities'
  
  // Documentation state - now managed by context
  const [documentation, setDocumentation] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [generationStage, setGenerationStage] = useState('');
  const [docStatus, setDocStatus] = useState('not_generated');
  const [lastGenerated, setLastGenerated] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  // Load repository and documentation on mount and when branch changes
  useEffect(() => {
    if (repositoryId) {
      loadRepositoryDetails();
      loadDocumentationFromContext();
    }
  }, [repositoryId, selectedBranch]);

  // Load documentation when returning to the page
  useEffect(() => {
    const handleFocus = () => {
      if (repositoryId && docStatus === 'generated') {
        loadDocumentationFromContext();
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [repositoryId, docStatus]);

  // Handle tab changes
  useEffect(() => {
    if (activeTab === 'view' && docStatus === 'generated') {
      loadDocumentationFromContext();
    }
  }, [activeTab]);

  // Update URL when doc type changes
  useEffect(() => {
    // Only update URL if docType actually changed and is different from current URL param
    if (selectedDocType && selectedDocType !== docTypeParam) {
      const newParams = new URLSearchParams(location.search);
      newParams.set('type', selectedDocType);
      navigate(`${location.pathname}?${newParams.toString()}`, { replace: true });
    }
  }, [selectedDocType]); // Only depend on selectedDocType

  // Load repository details
  const loadRepositoryDetails = async () => {
    try {
      setIsLoading(true);
      const response = await repositoryService.getRepositoryDetails(repositoryId);
      setRepository(response.data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading repository details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Load documentation from context - PERSISTENT AND RELIABLE
  const loadDocumentationFromContext = async () => {
    if (!repositoryId) return;
    
    try {
      console.log('Loading documentation from context for:', repositoryId);
      
      // First check if we have cached documentation
      const cached = getCachedDocumentation(repositoryId, selectedBranch);
      if (cached && cached.documentation && Object.keys(cached.documentation).length > 0) {
        console.log('Found cached documentation in context');
        setDocumentation(cached.documentation);
        setDocStatus(cached.status);
        setLastGenerated(cached.lastGenerated);
        loadFunctionalities();
        return;
      }
      
      // If no cache, fetch from API via context
      const result = await getDocumentation(repositoryId, selectedBranch);
      
      if (result && result.documentation && Object.keys(result.documentation).length > 0) {
        console.log('Documentation loaded from API via context');
        setDocumentation(result.documentation);
        setDocStatus(result.status);
        setLastGenerated(result.lastGenerated);
        loadFunctionalities();
      } else {
        console.log('No documentation found');
        setDocStatus('not_generated');
        setDocumentation({});
      }
    } catch (err) {
      console.error('Error loading documentation from context:', err);
      setDocStatus('not_generated');
      setDocumentation({});
    }
  };

  // Load functionalities
  const loadFunctionalities = async () => {
    try {
      const response = await repositoryService.getFunctionalitiesRegistry(repositoryId, selectedBranch);
      setApiEndpoints(response.data.endpoints || []);
    } catch (err) {
      console.error('Error loading functionalities:', err);
      setApiEndpoints([]);
    }
  };

  // Handle documentation generation - SIMPLE AND RELIABLE
  const handleGenerateDocumentation = async (options = {}) => {
    if (!repository || !repository.id) return;
    
    setIsGenerating(true);
    setDocStatus('generating');
    setGenerationProgress(0);
    setGenerationStage('Initializing...');
    
    try {
      console.log('Starting documentation generation for:', repository.id);
      
      const response = await documentationService.generateDocumentation(repository.id, {
        branch: selectedBranch,
        ...options
      });
      
      const taskId = response.data.task_id;
      
      const result = await documentationService.pollDocumentationStatus(
        repository.id,
        taskId,
        (status) => {
          setGenerationProgress(status.progress || 0);
          setGenerationStage(formatStageName(status.current_stage || ''));
        }
      );
      
      console.log('Generation completed:', result);
      
      if (result.documentation) {
        // Parse the documentation
        let docData = result.documentation;
        if (typeof docData === 'string') {
          try {
            docData = JSON.parse(docData);
          } catch (e) {
            console.error('Failed to parse generated documentation:', e);
            throw new Error('Invalid generated documentation');
          }
        }
        
        // Set the documentation in context and local state
        setDocumentation(docData);
        setDocStatus('generated');
        setLastGenerated(new Date().toISOString());
        
        // Cache it in context (this will also update the service cache)
        setContextDocumentation(repository.id, selectedBranch, docData);
        console.log('Documentation generated and cached successfully');
        
        // Load functionalities
        await loadFunctionalities();
      } else {
        console.log('No documentation in result, loading from API');
        await loadDocumentationFromContext();
      }
      
    } catch (error) {
      console.error('Error generating documentation:', error);
      setDocStatus('failed');
    } finally {
      setIsGenerating(false);
      setGenerationProgress(0);
      setGenerationStage('');
    }
  };

  // Format stage names for better UX
  const formatStageName = (stage) => {
    if (!stage) return 'Processing...';
    
    const stageMap = {
      'initializing': 'Initializing...',
      'analyzing_repository': 'Analyzing repository structure...',
      'analyzing_functions_and_classes': 'Analyzing functions and classes...',
      'generating_function_descriptions': 'Generating function descriptions...',
      'generating_class_descriptions': 'Generating class descriptions...',
      'generating_overview': 'Generating overview...',
      'generating_architecture_analysis': 'Generating architecture analysis...',
      'generating_user_guide': 'Generating user guide...',
      'finalizing_documentation': 'Finalizing documentation...',
      'completed': 'Documentation generated successfully!'
    };
    
    if (stage.startsWith('analyzing_function_')) {
      const funcName = stage.replace('analyzing_function_', '');
      return `Analyzing function: ${funcName}`;
    }
    
    if (stage.startsWith('analyzing_class_')) {
      const className = stage.replace('analyzing_class_', '');
      return `Analyzing class: ${className}`;
    }
    
    return stageMap[stage] || stage;
  };

  // Get documentation content for selected type
  const getDocumentationContent = () => {
    if (!documentation || Object.keys(documentation).length === 0) {
      return '';
    }

    // Map frontend doc types to backend doc types
    const docTypeMapping = {
      'overview': 'overview',
      'api': 'api_reference', 
      'architecture': 'architecture',
      'usage': 'user_guide'
    };

    const backendDocType = docTypeMapping[selectedDocType];
    
    if (!backendDocType) {
      return '';
    }

    // Handle api_reference which is an object
    if (backendDocType === 'api_reference' && documentation.api_reference) {
      return convertApiReferenceToMarkdown(documentation.api_reference);
    }

    // Return the content directly (already markdown)
    return documentation[backendDocType] || '';
  };

  // Convert API reference object to markdown (for backward compatibility)
  const convertApiReferenceToMarkdown = (apiRef) => {
    if (!apiRef || typeof apiRef !== 'object') return '';

    let markdown = '# API Reference\n\n';

    // Functions section
    if (apiRef.functions && apiRef.functions.length > 0) {
      markdown += '## Functions\n\n';
      apiRef.functions.forEach((func, index) => {
        markdown += `### ${func.name}\n\n`;
        if (func.description) {
          markdown += `${func.description}\n\n`;
        }
        if (func.file && func.line) {
          markdown += `**Location:** \`${func.file}:${func.line}\`\n\n`;
        }
        if (func.code_snippet) {
          markdown += '```\n' + func.code_snippet + '\n```\n\n';
        }
        markdown += '---\n\n';
      });
    }

    // Classes section
    if (apiRef.classes && apiRef.classes.length > 0) {
      markdown += '## Classes\n\n';
      apiRef.classes.forEach((cls, index) => {
        markdown += `### ${cls.name}\n\n`;
        if (cls.description) {
          markdown += `${cls.description}\n\n`;
        }
        if (cls.file && cls.line) {
          markdown += `**Location:** \`${cls.file}:${cls.line}\`\n\n`;
        }
        if (cls.code_snippet) {
          markdown += '```\n' + cls.code_snippet + '\n```\n\n';
        }
        markdown += '---\n\n';
      });
    }

    return markdown;
  };

  // Handle doc type selection
  const handleDocTypeSelect = (docType) => {
    setSelectedDocType(docType);
  };

  // Handle search
  const handleSearch = async (query) => {
    if (!query || !repository) return;
    
    setSearchQuery(query);
    setActiveTab('search');
    
    try {
      const response = await documentationService.searchDocumentation(
        repository.id, 
        query,
        selectedBranch
      );
      
      setSearchResults(response.data.results || []);
    } catch (err) {
      console.error('Error searching documentation:', err);
      setSearchResults([]);
    }
  };

  // Handle search result click
  const handleSearchResultClick = (result) => {
    if (result.doc_type) {
      setSelectedDocType(result.doc_type);
      setActiveTab('view');
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="text-red-600 mb-4">Error loading repository</div>
          <p className="text-gray-600">{error}</p>
        </div>
      </Layout>
    );
  }

  if (!repository) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="text-gray-600">Repository not found</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Documentation Navigation */}
        <div className="flex justify-between items-start">
          <h1 className="text-2xl font-bold">Repository Documentation</h1>
          <DocumentationStatus 
            status={docStatus}
            lastGenerated={lastGenerated}
            qualityScore={documentation.quality_score}
            missingTypes={documentation.missing_types}
            onRefresh={() => handleGenerateDocumentation({})}
          />
        </div>
        
        <DocumentationNavigation 
          repository={repository}
          selectedDocType={selectedDocType}
          onSelectDocType={handleDocTypeSelect}
          onSearch={handleSearch}
        />
        
        {/* Documentation Tabs */}
        <Tabs value={activeTab} onValueChange={(value) => {
          if (value === 'functionalities') {
            // Navigate to the original functionalities page instead of using embedded tab
            navigate(`/repositories/${repository.id}/functionalities`);
          } else {
            setActiveTab(value);
          }
        }}>
          <TabsList className="mb-4">
            <TabsTrigger value="view">View Documentation</TabsTrigger>
            <TabsTrigger value="search">Search</TabsTrigger>
            <TabsTrigger value="functionalities">Functionalities</TabsTrigger>
            <TabsTrigger value="generate">Generate</TabsTrigger>
          </TabsList>
          
          <TabsContent value="view">
            <DocumentationViewer 
              content={getDocumentationContent()}
              title={
                selectedDocType === 'overview' ? 'Repository Overview' :
                selectedDocType === 'api' ? 'API Reference' :
                selectedDocType === 'architecture' ? 'Architecture Documentation' :
                selectedDocType === 'usage' ? 'User Guide' :
                'Documentation'
              }
              docType={selectedDocType}
              isLoading={isGenerating}
              onSearch={handleSearch}
            />
          </TabsContent>
          
          <TabsContent value="search">
            <DocumentationSearch 
              repository={repository}
              onResultClick={handleSearchResultClick}
              initialQuery={searchQuery}
            />
          </TabsContent>
          
          <TabsContent value="generate">
            <DocumentationGenerator 
              repository={repository}
              onGenerationStart={(progressInfo) => {
                setIsGenerating(true);
                setDocStatus('generating');
                if (progressInfo) {
                  setGenerationProgress(progressInfo.progress || 0);
                  setGenerationStage(progressInfo.stage || '');
                }
              }}
              onGenerationComplete={(documentation) => {
                setDocumentation(documentation || {});
                setDocStatus('generated');
                setLastGenerated(new Date().toISOString());
                setIsGenerating(false);
                setGenerationProgress(0);
                setGenerationStage('');
                
                // Reload functionalities
                loadFunctionalities();
              }}
              onGenerationError={(error) => {
                setDocStatus('failed');
                setIsGenerating(false);
                setGenerationProgress(0);
                setGenerationStage('');
                console.error('Documentation generation failed:', error);
              }}
              isGenerating={isGenerating}
              generationProgress={generationProgress}
            />
          </TabsContent>
        </Tabs>
      </div>
    </Layout>
  );
};

export default Documentation;