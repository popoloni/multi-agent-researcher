/**
 * Settings API service for managing application configuration
 */

import api from './api';

export const settingsService = {
  /**
   * Get all configurable settings
   */
  async getAllSettings() {
    try {
      const response = await api.get('/api/settings/all');
      return response.data;
    } catch (error) {
      console.error('Error fetching settings:', error);
      throw error;
    }
  },

  /**
   * Update multiple settings
   */
  async updateSettings(settings) {
    try {
      const response = await api.post('/api/settings/update', { settings });
      return response.data;
    } catch (error) {
      console.error('Error updating settings:', error);
      throw error;
    }
  },

  /**
   * Get provider connection status
   */
  async getProviderStatus() {
    try {
      const response = await api.get('/api/settings/providers/status');
      return response.data;
    } catch (error) {
      console.error('Error fetching provider status:', error);
      throw error;
    }
  },

  /**
   * Get available models from all providers
   */
  async getAvailableModels() {
    try {
      const response = await api.get('/api/settings/models/available');
      return response.data;
    } catch (error) {
      console.error('Error fetching available models:', error);
      throw error;
    }
  },

  /**
   * Apply a model configuration preset
   */
  async applyModelPreset(presetName) {
    try {
      const response = await api.post(`/api/settings/models/preset/${presetName}`);
      return response.data;
    } catch (error) {
      console.error('Error applying model preset:', error);
      throw error;
    }
  },

  /**
   * Test connection to a specific provider
   */
  async testProviderConnection(provider) {
    try {
      const response = await api.post(`/api/settings/test-connection/${provider}`);
      return response.data;
    } catch (error) {
      console.error('Error testing provider connection:', error);
      throw error;
    }
  },

  /**
   * Export current settings configuration
   */
  async exportSettings() {
    try {
      const response = await api.get('/api/settings/export');
      return response.data;
    } catch (error) {
      console.error('Error exporting settings:', error);
      throw error;
    }
  }
};

export default settingsService;