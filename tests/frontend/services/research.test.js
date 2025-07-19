import { researchService } from '../research';
import api from '../api';

// Mock the api module
jest.mock('../api');

describe('Research Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('startResearch', () => {
    test('research service calls start endpoint correctly', async () => {
      const mockResponse = {
        data: {
          research_id: 'test-research-id-123',
          status: 'started',
          message: 'Research initiated successfully'
        }
      };
      
      api.post.mockResolvedValue(mockResponse);

      const researchData = {
        query: 'What are the latest AI developments in healthcare?',
        max_subagents: 3,
        max_iterations: 5
      };

      const result = await researchService.startResearch(researchData);

      expect(api.post).toHaveBeenCalledWith('/research/start', {
        query: 'What are the latest AI developments in healthcare?',
        max_subagents: 3,
        max_iterations: 5
      });
      expect(result).toEqual(mockResponse.data);
    });

    test('request validation prevents invalid calls', async () => {
      // Test empty query
      await expect(researchService.startResearch({ query: '' }))
        .rejects.toThrow('Query is required and must be a string');

      // Test missing query
      await expect(researchService.startResearch({}))
        .rejects.toThrow('Query is required and must be a string');
      
      // Test short query
      await expect(researchService.startResearch({ query: 'short' }))
        .rejects.toThrow('Query must be at least 10 characters long');

      // Test invalid max_subagents
      await expect(researchService.startResearch({
        query: 'Valid query here',
        max_subagents: 10
      })).rejects.toThrow('max_subagents must be between 1 and 5');

      // Test invalid max_iterations
      await expect(researchService.startResearch({
        query: 'Valid query here',
        max_iterations: 15
      })).rejects.toThrow('max_iterations must be between 2 and 10');
    });

    test('error handling works correctly', async () => {
      // Test 400 error
      api.post.mockRejectedValue({
        response: { status: 400, data: { detail: 'Invalid parameters' } }
      });

      await expect(researchService.startResearch({
        query: 'Valid query here'
      })).rejects.toThrow('Invalid parameters');

      // Test 500 error
      api.post.mockRejectedValue({
        response: { status: 500 }
      });

      await expect(researchService.startResearch({
        query: 'Valid query here'
      })).rejects.toThrow('Server error occurred while starting research');

      // Test network error
      api.post.mockRejectedValue({
        code: 'ECONNABORTED'
      });

      await expect(researchService.startResearch({
        query: 'Valid query here'
      })).rejects.toThrow('Request timeout - please try again');
    });

    test('response validation handles malformed data', async () => {
      // Test missing research_id
      api.post.mockResolvedValue({
        data: { status: 'started' }
      });

      await expect(researchService.startResearch({
        query: 'Valid query here that is long enough'
      })).rejects.toThrow('Invalid response: missing research_id');
    });
  });

  describe('getResearchStatus', () => {
    test('gets research status correctly', async () => {
      const mockResponse = {
        data: {
          research_id: 'test-id',
          status: 'in_progress',
          progress_percentage: 45,
          current_stage: 'searching',
          message: 'Agents are gathering information'
        }
      };

      api.get.mockResolvedValue(mockResponse);

      const result = await researchService.getResearchStatus('test-id');

      expect(api.get).toHaveBeenCalledWith('/research/test-id/status');
      expect(result).toEqual(mockResponse.data);
    });

    test('validates research ID parameter', async () => {
      await expect(researchService.getResearchStatus(''))
        .rejects.toThrow('Research ID is required and must be a string');

      await expect(researchService.getResearchStatus(null))
        .rejects.toThrow('Research ID is required and must be a string');
    });

    test('handles 404 error correctly', async () => {
      api.get.mockRejectedValue({
        response: { status: 404 }
      });

      await expect(researchService.getResearchStatus('invalid-id'))
        .rejects.toThrow('Research task not found');
    });
  });

  describe('getResearchResult', () => {
    test('gets research results correctly', async () => {
      const mockResponse = {
        data: {
          research_id: 'test-id',
          query: 'Test query',
          report: 'Research report content',
          sources_used: [],
          citations: [],
          total_tokens_used: 1500,
          execution_time: 120
        }
      };

      api.get.mockResolvedValue(mockResponse);

      const result = await researchService.getResearchResult('test-id');

      expect(api.get).toHaveBeenCalledWith('/research/test-id/result');
      expect(result).toEqual(mockResponse.data);
    });

    test('handles research not completed error', async () => {
      api.get.mockRejectedValue({
        response: { status: 400 }
      });

      await expect(researchService.getResearchResult('test-id'))
        .rejects.toThrow('Research not completed yet');
    });
  });

  describe('getResearchHistory', () => {
    test('gets research history correctly', async () => {
      const mockResponse = {
        data: [
          {
            research_id: 'id1',
            query: 'Query 1',
            status: 'completed',
            created_at: '2025-01-01T00:00:00Z'
          },
          {
            research_id: 'id2',
            query: 'Query 2',
            status: 'failed',
            created_at: '2025-01-02T00:00:00Z'
          }
        ]
      };

      api.get.mockResolvedValue(mockResponse);

      const result = await researchService.getResearchHistory();

      expect(api.get).toHaveBeenCalledWith('/research/history', {
        params: { limit: 50, offset: 0 }
      });
      expect(result).toEqual(mockResponse.data);
    });

    test('validates pagination parameters', async () => {
      await expect(researchService.getResearchHistory({ limit: 0 }))
        .rejects.toThrow('Limit must be between 1 and 100');

      await expect(researchService.getResearchHistory({ offset: -1 }))
        .rejects.toThrow('Offset must be non-negative');
    });
  });

  describe('validateQuery', () => {
    test('validates queries correctly', () => {
      // Valid query
      const validResult = researchService.validateQuery('This is a valid research query');
      expect(validResult.isValid).toBe(true);
      expect(validResult.errors).toHaveLength(0);

      // Too short query
      const shortResult = researchService.validateQuery('short');
      expect(shortResult.isValid).toBe(false);
      expect(shortResult.errors).toContain('Query must be at least 10 characters long');

      // Empty query
      const emptyResult = researchService.validateQuery('');
      expect(emptyResult.isValid).toBe(false);
      expect(emptyResult.errors).toContain('Query is required and must be a string');

      // Malicious content
      const maliciousResult = researchService.validateQuery('<script>alert("xss")</script>');
      expect(maliciousResult.isValid).toBe(false);
      expect(maliciousResult.errors).toContain('Query contains potentially unsafe content');
    });
  });

  describe('formatResults', () => {
    test('formats results correctly', () => {
      const rawResults = {
        research_id: 'test-id',
        query: 'Test query',
        created_at: '2025-01-01T12:00:00Z',
        execution_time: 125,
        total_tokens_used: 1500,
        sources_used: [],
        citations: []
      };

      const formatted = researchService.formatResults(rawResults);

      expect(formatted.created_at).toBeInstanceOf(Date);
      expect(formatted.execution_time_formatted).toBe('2m 5s');
      expect(formatted.tokens_formatted).toBe('1,500');
      expect(Array.isArray(formatted.sources_used)).toBe(true);
      expect(Array.isArray(formatted.citations)).toBe(true);
    });

    test('handles null input', () => {
      const result = researchService.formatResults(null);
      expect(result).toBeNull();
    });
  });

  describe('retryRequest', () => {
    test('retries failed requests correctly', async () => {
      const mockApiCall = jest.fn()
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce('Success');

      const result = await researchService.retryRequest(mockApiCall, 3, 10);

      expect(mockApiCall).toHaveBeenCalledTimes(3);
      expect(result).toBe('Success');
    });

    test('does not retry client errors', async () => {
      const mockApiCall = jest.fn()
        .mockRejectedValue({ response: { status: 400 } });

      await expect(researchService.retryRequest(mockApiCall, 3, 10))
        .rejects.toEqual({ response: { status: 400 } });

      expect(mockApiCall).toHaveBeenCalledTimes(1);
    });
  });
});