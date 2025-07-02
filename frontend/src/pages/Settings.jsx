import React, { useState, useEffect, useCallback } from 'react';
import { settingsService } from '../services/settings';
import { useNotifications } from '../contexts/NotificationContext';
import './Settings.css';

const Settings = () => {
  const [settings, setSettings] = useState({});
  const [categories, setCategories] = useState({});
  const [providerStatus, setProviderStatus] = useState({});

  const [modelPresets, setModelPresets] = useState({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [activeCategory, setActiveCategory] = useState('api');
  const [pendingChanges, setPendingChanges] = useState({});
  const [testingProvider, setTestingProvider] = useState(null);
  
  const { addNotification } = useNotifications();

  const loadSettings = useCallback(async () => {
    try {
      setLoading(true);
      const data = await settingsService.getAllSettings();
      setSettings(data.settings);
      setCategories(data.categories);
      setProviderStatus(data.provider_status);
      setModelPresets(data.model_presets);
    } catch (error) {
      addNotification('Failed to load settings', 'error');
      console.error('Error loading settings:', error);
    } finally {
      setLoading(false);
    }
  }, [addNotification]);

  useEffect(() => {
    loadSettings();
  }, [loadSettings]);

  const handleSettingChange = (key, value) => {
    setPendingChanges(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const saveSettings = async () => {
    if (Object.keys(pendingChanges).length === 0) {
      addNotification('No changes to save', 'info');
      return;
    }

    try {
      setSaving(true);
      const result = await settingsService.updateSettings(pendingChanges);
      
      if (result.success) {
        addNotification(
          `Settings updated successfully. ${result.restart_required ? 'Server restart may be required.' : ''}`,
          result.restart_required ? 'warning' : 'success'
        );
        setPendingChanges({});
        await loadSettings(); // Reload to get updated values
      }
    } catch (error) {
      addNotification('Failed to save settings', 'error');
      console.error('Error saving settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const discardChanges = () => {
    setPendingChanges({});
    addNotification('Changes discarded', 'info');
  };

  const testProviderConnection = async (provider) => {
    try {
      setTestingProvider(provider);
      const result = await settingsService.testProviderConnection(provider);
      
      if (result.success) {
        addNotification(`Successfully connected to ${provider}`, 'success');
      } else {
        addNotification(`Failed to connect to ${provider}: ${result.message}`, 'error');
      }
    } catch (error) {
      addNotification(`Error testing ${provider} connection`, 'error');
    } finally {
      setTestingProvider(null);
    }
  };

  const applyModelPreset = async (presetName) => {
    try {
      setSaving(true);
      const result = await settingsService.applyModelPreset(presetName);
      
      if (result.success) {
        addNotification(`Applied ${presetName} preset successfully`, 'success');
        setPendingChanges({});
        await loadSettings();
      }
    } catch (error) {
      addNotification('Failed to apply preset', 'error');
    } finally {
      setSaving(false);
    }
  };

  const exportSettings = async () => {
    try {
      const data = await settingsService.exportSettings();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'settings-export.json';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      addNotification('Settings exported successfully', 'success');
    } catch (error) {
      addNotification('Failed to export settings', 'error');
    }
  };

  const renderSettingInput = (setting) => {
    const currentValue = pendingChanges[setting.key] !== undefined 
      ? pendingChanges[setting.key] 
      : setting.value;

    switch (setting.type) {
      case 'boolean':
        return (
          <select
            value={currentValue}
            onChange={(e) => handleSettingChange(setting.key, e.target.value)}
            className="setting-input"
          >
            <option value="true">True</option>
            <option value="false">False</option>
          </select>
        );

      case 'select':
        return (
          <select
            value={currentValue}
            onChange={(e) => handleSettingChange(setting.key, e.target.value)}
            className="setting-input"
          >
            {setting.options?.map(option => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        );

      case 'number':
        return (
          <input
            type="number"
            value={currentValue}
            onChange={(e) => handleSettingChange(setting.key, e.target.value)}
            className="setting-input"
          />
        );

      case 'password':
        return (
          <input
            type="password"
            value={currentValue}
            onChange={(e) => handleSettingChange(setting.key, e.target.value)}
            className="setting-input"
            placeholder={currentValue ? '••••••••' : 'Enter value'}
          />
        );

      default:
        return (
          <input
            type="text"
            value={currentValue}
            onChange={(e) => handleSettingChange(setting.key, e.target.value)}
            className="setting-input"
          />
        );
    }
  };

  const getProviderStatusIcon = (provider) => {
    const status = providerStatus[provider];
    if (!status) return '❓';
    return status.connected ? '✅' : '❌';
  };

  const getProviderStatusText = (provider) => {
    const status = providerStatus[provider];
    if (!status) return 'Unknown';
    if (status.connected) return 'Connected';
    return status.error || 'Disconnected';
  };

  if (loading) {
    return (
      <div className="settings-container">
        <div className="loading">Loading settings...</div>
      </div>
    );
  }

  const categorySettings = Object.values(settings).filter(
    setting => setting.category === activeCategory
  );

  return (
    <div className="settings-container">
      <div className="settings-header">
        <h1>Settings</h1>
        <div className="settings-actions">
          <button onClick={exportSettings} className="btn btn-secondary">
            Export Settings
          </button>
          {Object.keys(pendingChanges).length > 0 && (
            <>
              <button onClick={discardChanges} className="btn btn-secondary">
                Discard Changes
              </button>
              <button 
                onClick={saveSettings} 
                className="btn btn-primary"
                disabled={saving}
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </>
          )}
        </div>
      </div>

      <div className="settings-content">
        {/* Category Navigation */}
        <div className="settings-sidebar">
          <nav className="category-nav">
            {Object.entries(categories).map(([key, label]) => (
              <button
                key={key}
                className={`category-btn ${activeCategory === key ? 'active' : ''}`}
                onClick={() => setActiveCategory(key)}
              >
                {label}
              </button>
            ))}
          </nav>

          {/* Provider Status */}
          <div className="provider-status">
            <h3>Provider Status</h3>
            {Object.entries(providerStatus).map(([provider, status]) => (
              <div key={provider} className="provider-item">
                <div className="provider-info">
                  <span className="provider-icon">
                    {getProviderStatusIcon(provider)}
                  </span>
                  <div>
                    <div className="provider-name">{provider}</div>
                    <div className="provider-status-text">
                      {getProviderStatusText(provider)}
                    </div>
                  </div>
                </div>
                {provider !== 'mock' && (
                  <button
                    onClick={() => testProviderConnection(provider)}
                    disabled={testingProvider === provider}
                    className="btn btn-sm btn-secondary"
                  >
                    {testingProvider === provider ? 'Testing...' : 'Test'}
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Model Presets */}
          {activeCategory === 'models' && (
            <div className="model-presets">
              <h3>Model Presets</h3>
              {Object.entries(modelPresets).map(([key, preset]) => (
                <div key={key} className="preset-item">
                  <div className="preset-info">
                    <div className="preset-name">{preset.name}</div>
                    <div className="preset-description">{preset.description}</div>
                  </div>
                  <button
                    onClick={() => applyModelPreset(key)}
                    disabled={saving}
                    className="btn btn-sm btn-primary"
                  >
                    Apply
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Settings Form */}
        <div className="settings-main">
          <div className="category-header">
            <h2>{categories[activeCategory]}</h2>
            {Object.keys(pendingChanges).length > 0 && (
              <div className="changes-indicator">
                {Object.keys(pendingChanges).length} unsaved changes
              </div>
            )}
          </div>

          <div className="settings-form">
            {categorySettings.map(setting => (
              <div key={setting.key} className="setting-item">
                <div className="setting-label">
                  <label htmlFor={setting.key}>
                    {setting.key.replace(/_/g, ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                  </label>
                  {setting.requires_restart && (
                    <span className="restart-required">Requires restart</span>
                  )}
                  {pendingChanges[setting.key] !== undefined && (
                    <span className="changed-indicator">Modified</span>
                  )}
                </div>
                <div className="setting-description">
                  {setting.description}
                </div>
                <div className="setting-control">
                  {renderSettingInput(setting)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;