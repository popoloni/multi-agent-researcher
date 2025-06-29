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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/common/Tabs';

const Documentation = () => {
  const { repositoryId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  
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
  
  // Documentation state
  const [documentation, setDocumentation] = useState({});
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [docStatus, setDocStatus] = useState('not_generated');
  const [lastGenerated, setLastGenerated] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  // Load repository and documentation on mount
  useEffect(() => {
    if (repositoryId) {
      loadRepositoryDetails();
      loadDocumentation();
      loadFunctionalities();
    }
  }, [repositoryId, selectedBranch]);

  // Update URL when doc type changes
  useEffect(() => {
    if (selectedDocType) {
      const newParams = new URLSearchParams(location.search);
      newParams.set('type', selectedDocType);
      navigate(`${location.pathname}?${newParams.toString()}`, { replace: true });
    }
  }, [selectedDocType, navigate, location]);

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

  // Load documentation
  const loadDocumentation = async () => {
    if (!repositoryId) return;
    
    try {
      // Get all documentation types
      const response = await documentationService.getDocumentation(repositoryId, selectedBranch);
      
      if (response.data && response.data.documentation) {
        setDocumentation(response.data.documentation);
        setDocStatus('generated');
        setLastGenerated(response.data.last_generated || new Date().toISOString());
      } else {
        setDocStatus('not_generated');
      }
    } catch (err) {
      console.error('Error loading documentation:', err);
      setDocStatus('not_generated');
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

  // Generate documentation
  const handleGenerateDocumentation = async (options) => {
    if (!repository || !repository.id) return;
    
    setIsGenerating(true);
    setDocStatus('generating');
    setGenerationProgress(0);
    
    try {
      // Start progress simulation
      const progressInterval = setInterval(() => {
        setGenerationProgress(prev => {
          const newProgress = prev + (100 - prev) * 0.05;
          return newProgress > 95 ? 95 : newProgress;
        });
      }, 1000);
      
      // Generate documentation
      const response = await documentationService.generateDocumentation(repository.id, {
        branch: selectedBranch,
        ...options
      });
      
      clearInterval(progressInterval);
      setGenerationProgress(100);
      
      // Update documentation state
      if (response.data && response.data.documentation) {
        setDocumentation(response.data.documentation);
        setDocStatus('generated');
        setLastGenerated(new Date().toISOString());
      }
      
      // Reload functionalities
      await loadFunctionalities();
    } catch (error) {
      console.error('Error generating documentation:', error);
      setDocStatus('failed');
    } finally {
      setIsGenerating(false);
    }
  };

  // Convert API reference object to markdown
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
          markdown += '```python\n' + func.code_snippet + '\n```\n\n';
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
          markdown += '```python\n' + cls.code_snippet + '\n```\n\n';
        }
        markdown += '---\n\n';
      });
    }

    return markdown;
  };

  // Convert architecture object to markdown
  const convertArchitectureToMarkdown = (arch) => {
    if (!arch || typeof arch !== 'object') return '';

    let markdown = '# Architecture Documentation\n\n';

    // Overview
    markdown += '## Repository Architecture Overview\n\n';

    if (arch.language) {
      markdown += `**Primary Language:** ${arch.language}\n\n`;
    }

    if (arch.total_files) {
      markdown += `**Total Files:** ${arch.total_files}\n\n`;
    }

    if (arch.total_elements) {
      markdown += `**Total Code Elements:** ${arch.total_elements}\n\n`;
    }

    // Element breakdown
    if (arch.element_counts) {
      markdown += '## Code Element Distribution\n\n';
      Object.entries(arch.element_counts).forEach(([type, count]) => {
        markdown += `- **${type.charAt(0).toUpperCase() + type.slice(1)}s:** ${count}\n`;
      });
      markdown += '\n';
    }

    // Frameworks detected
    if (arch.frameworks_detected && arch.frameworks_detected.length > 0) {
      markdown += '## Detected Frameworks\n\n';
      arch.frameworks_detected.forEach(framework => {
        markdown += `- ${framework}\n`;
      });
      markdown += '\n';
    }

    // Architecture insights
    markdown += '## Architecture Analysis\n\n';
    markdown += 'This repository follows a structured approach with well-organized code elements. ';
    markdown += `The codebase contains ${arch.total_elements || 0} total elements across ${arch.total_files || 0} files, `;
    markdown += `indicating a ${arch.total_elements > 500 ? 'large-scale' : 'medium-scale'} project.\n\n`;

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
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-4">
            <TabsTrigger value="view">View Documentation</TabsTrigger>
            <TabsTrigger value="search">Search</TabsTrigger>
            <TabsTrigger value="functionalities">Functionalities</TabsTrigger>
            <TabsTrigger value="generate">Generate</TabsTrigger>
          </TabsList>
          
          <TabsContent value="view">
            <DocumentationViewer 
              content={
                selectedDocType === 'api' ?
                  convertApiReferenceToMarkdown(documentation['api_reference']) :
                selectedDocType === 'architecture' ?
                  convertArchitectureToMarkdown(documentation['architecture']) :
                  documentation[selectedDocType] || ''
              }
              title={
                selectedDocType === 'overview' ? 'Repository Overview' :
                selectedDocType === 'api' ? 'API Documentation' :
                selectedDocType === 'architecture' ? 'Architecture Documentation' :
                selectedDocType === 'usage' ? 'Usage Guide' :
                'Documentation'
              }
              docType={selectedDocType}
              isLoading={isLoading}
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
          
          <TabsContent value="functionalities">
            <FunctionalitiesRegistry
              repository={repository}
              branch={selectedBranch}
              apiEndpoints={apiEndpoints}
              onGenerateDocumentation={() => handleGenerateDocumentation({})}
              onBranchChange={setSelectedBranch}
            />
          </TabsContent>
          
          <TabsContent value="generate">
            <DocumentationGenerator 
              repository={repository}
              onGenerationStart={() => {
                setIsGenerating(true);
                setDocStatus('generating');
              }}
              onGenerationComplete={(data) => {
                setDocumentation(data.documentation || {});
                setDocStatus('generated');
                setLastGenerated(new Date().toISOString());
                setIsGenerating(false);
              }}
              onGenerationError={() => {
                setDocStatus('failed');
                setIsGenerating(false);
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