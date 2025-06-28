import React, { useState } from 'react';
import { FileText, RefreshCw, Settings, AlertCircle, CheckCircle } from 'lucide-react';
import { documentationService } from '../../services/documentation';

const DocumentationGenerator = ({ 
  repository, 
  onGenerationStart, 
  onGenerationComplete,
  onGenerationError,
  isGenerating = false,
  generationProgress = 0
}) => {
  const [showOptions, setShowOptions] = useState(false);
  const [options, setOptions] = useState({
    detailLevel: 'standard', // 'basic', 'standard', 'detailed'
    includeExamples: true,
    includeArchitecture: true,
    includeApi: true,
    includeUsage: true,
    format: 'markdown' // 'markdown', 'html'
  });
  const [error, setError] = useState(null);

  const handleGenerateDocumentation = async () => {
    if (!repository || !repository.id) return;
    
    setError(null);
    
    try {
      if (onGenerationStart) {
        onGenerationStart();
      }
      
      const response = await documentationService.generateDocumentation(repository.id, options);
      
      if (onGenerationComplete) {
        onGenerationComplete(response.data);
      }
    } catch (err) {
      console.error('Error generating documentation:', err);
      setError(err.message || 'Failed to generate documentation');
      
      if (onGenerationError) {
        onGenerationError(err);
      }
    }
  };

  const handleOptionChange = (key, value) => {
    setOptions(prev => ({
      ...prev,
      [key]: value
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow mb-6">
      <div className="border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <div>
          <h2 className="text-lg font-bold text-gray-800">Documentation Generator</h2>
          <p className="text-sm text-gray-500 mt-1">
            Generate comprehensive documentation for this repository
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => setShowOptions(!showOptions)}
            className="text-gray-600 hover:text-gray-800 p-2 rounded-full hover:bg-gray-100"
            title="Generation options"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Error message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 m-4">
          <div className="flex items-start">
            <AlertCircle className="w-5 h-5 text-red-500 mr-2 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-800">Error generating documentation</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Generation options */}
      {showOptions && (
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <h3 className="text-sm font-medium text-gray-700 mb-3">Generation Options</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Detail Level
              </label>
              <select
                value={options.detailLevel}
                onChange={(e) => handleOptionChange('detailLevel', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
              >
                <option value="basic">Basic - Quick overview</option>
                <option value="standard">Standard - Balanced detail</option>
                <option value="detailed">Detailed - Comprehensive coverage</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Output Format
              </label>
              <select
                value={options.format}
                onChange={(e) => handleOptionChange('format', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
              >
                <option value="markdown">Markdown</option>
                <option value="html">HTML</option>
              </select>
            </div>
          </div>
          
          <div className="mt-4 space-y-3">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeExamples"
                checked={options.includeExamples}
                onChange={(e) => handleOptionChange('includeExamples', e.target.checked)}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="includeExamples" className="ml-2 block text-sm text-gray-700">
                Include code examples
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeArchitecture"
                checked={options.includeArchitecture}
                onChange={(e) => handleOptionChange('includeArchitecture', e.target.checked)}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="includeArchitecture" className="ml-2 block text-sm text-gray-700">
                Include architecture documentation
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeApi"
                checked={options.includeApi}
                onChange={(e) => handleOptionChange('includeApi', e.target.checked)}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="includeApi" className="ml-2 block text-sm text-gray-700">
                Include API documentation
              </label>
            </div>
            
            <div className="flex items-center">
              <input
                type="checkbox"
                id="includeUsage"
                checked={options.includeUsage}
                onChange={(e) => handleOptionChange('includeUsage', e.target.checked)}
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="includeUsage" className="ml-2 block text-sm text-gray-700">
                Include usage guide
              </label>
            </div>
          </div>
        </div>
      )}

      {/* Generation progress */}
      {isGenerating && (
        <div className="px-6 py-4">
          <div className="flex items-center mb-2">
            <RefreshCw className="w-5 h-5 text-primary-500 animate-spin mr-2" />
            <span className="text-sm font-medium text-gray-700">
              Generating documentation...
            </span>
            <span className="ml-auto text-sm text-gray-500">
              {Math.round(generationProgress)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-primary-500 h-2.5 rounded-full" 
              style={{ width: `${generationProgress}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            This may take a few minutes depending on repository size
          </p>
        </div>
      )}

      {/* Generation button */}
      <div className="px-6 py-4 flex justify-end">
        <button
          onClick={handleGenerateDocumentation}
          disabled={isGenerating || !repository}
          className={`flex items-center px-4 py-2 rounded-lg text-white ${
            isGenerating || !repository
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-primary-600 hover:bg-primary-700'
          }`}
        >
          {isGenerating ? (
            <>
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <FileText className="w-4 h-4 mr-2" />
              Generate Documentation
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default DocumentationGenerator;