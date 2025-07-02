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
  // Global documentation state with persistence
  const [documentationCache, setDocumentationCache] = useState(() => {
    // Initialize from localStorage if available
    try {
      const stored = localStorage.getItem('documentationCache');
      if (stored) {
        const parsed = JSON.parse(stored);
        return new Map(Object.entries(parsed));
      }
    } catch (e) {
      console.warn('Failed to load documentation cache from localStorage:', e);
    }
    return new Map();
  });
  const [generationStatus, setGenerationStatus] = useState(new Map());

  // Persist cache to localStorage whenever it changes
  useEffect(() => {
    try {
      const cacheObject = Object.fromEntries(documentationCache);
      localStorage.setItem('documentationCache', JSON.stringify(cacheObject));
    } catch (e) {
      console.warn('Failed to persist documentation cache to localStorage:', e);
    }
  }, [documentationCache]);

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
    const cached = documentationCache.get(cacheKey);
    
    // If not found in memory cache, try to recover from service cache
    if (!cached) {
      try {
        const serviceCache = documentationService.getCache(repositoryId);
        if (serviceCache) {
          console.log('Recovering documentation from service cache');
          const recoveredData = {
            documentation: serviceCache,
            lastGenerated: new Date().toISOString(),
            status: 'generated'
          };
          
          // Update context cache
          setDocumentationCache(prev => new Map(prev.set(cacheKey, recoveredData)));
          return recoveredData;
        }
      } catch (e) {
        console.warn('Failed to recover from service cache:', e);
      }
    }
    
    return cached || null;
  };

  // Force refresh documentation from API
  const refreshDocumentation = async (repositoryId, branch = 'main') => {
    console.log('Force refreshing documentation for:', repositoryId);
    return await getDocumentation(repositoryId, branch, true);
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
    refreshDocumentation,
    
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