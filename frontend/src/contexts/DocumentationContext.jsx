import React, { createContext, useContext, useState, useEffect } from 'react';
import { documentationService } from '../services/documentation';

const DocumentationContext = createContext();

export const useDocumentation = () => {
  const context = useContext(DocumentationContext);
  if (!context) {
    throw new Error('useDocumentation must be used within a DocumentationProvider');
  }
  return context;
};

export const DocumentationProvider = ({ children }) => {
  // Global documentation state
  const [documentationCache, setDocumentationCache] = useState(new Map());
  const [generationStatus, setGenerationStatus] = useState(new Map());

  // Get documentation for a repository
  const getDocumentation = async (repositoryId, branch = 'main', forceRefresh = false) => {
    const cacheKey = `${repositoryId}_${branch}`;
    
    // Return cached data if available and not forcing refresh
    if (!forceRefresh && documentationCache.has(cacheKey)) {
      console.log('Returning cached documentation from context');
      return documentationCache.get(cacheKey);
    }

    try {
      console.log('Fetching documentation from service');
      const response = await documentationService.getDocumentation(repositoryId, branch);
      
      if (response.data && response.data.documentation) {
        const docData = response.data.documentation;
        
        // Cache in context
        setDocumentationCache(prev => new Map(prev.set(cacheKey, {
          documentation: docData,
          lastGenerated: response.data.last_generated || new Date().toISOString(),
          status: 'generated'
        })));
        
        return {
          documentation: docData,
          lastGenerated: response.data.last_generated || new Date().toISOString(),
          status: 'generated'
        };
      } else {
        // No documentation found
        setDocumentationCache(prev => new Map(prev.set(cacheKey, {
          documentation: {},
          lastGenerated: null,
          status: 'not_generated'
        })));
        
        return {
          documentation: {},
          lastGenerated: null,
          status: 'not_generated'
        };
      }
    } catch (error) {
      console.error('Error fetching documentation:', error);
      throw error;
    }
  };

  // Set documentation (after generation)
  const setDocumentation = (repositoryId, branch = 'main', docData) => {
    const cacheKey = `${repositoryId}_${branch}`;
    
    setDocumentationCache(prev => new Map(prev.set(cacheKey, {
      documentation: docData,
      lastGenerated: new Date().toISOString(),
      status: 'generated'
    })));
    
    // Also update the service cache
    documentationService.setCache(repositoryId, docData);
  };

  // Clear documentation cache
  const clearDocumentation = (repositoryId, branch = 'main') => {
    const cacheKey = `${repositoryId}_${branch}`;
    setDocumentationCache(prev => {
      const newCache = new Map(prev);
      newCache.delete(cacheKey);
      return newCache;
    });
    
    // Also clear service cache
    documentationService.clearCache(repositoryId);
  };

  // Get cached documentation without API call
  const getCachedDocumentation = (repositoryId, branch = 'main') => {
    const cacheKey = `${repositoryId}_${branch}`;
    return documentationCache.get(cacheKey) || null;
  };

  // Set generation status
  const setDocumentationGenerationStatus = (repositoryId, status) => {
    setGenerationStatus(prev => new Map(prev.set(repositoryId, status)));
  };

  // Get generation status
  const getDocumentationGenerationStatus = (repositoryId) => {
    return generationStatus.get(repositoryId) || null;
  };

  const value = {
    // Documentation methods
    getDocumentation,
    setDocumentation,
    clearDocumentation,
    getCachedDocumentation,
    
    // Generation status methods
    setDocumentationGenerationStatus,
    getDocumentationGenerationStatus,
    
    // State
    documentationCache,
    generationStatus
  };

  return (
    <DocumentationContext.Provider value={value}>
      {children}
    </DocumentationContext.Provider>
  );
};

export default DocumentationContext;