import React, { createContext, useContext, useState } from 'react';

// Create context for tabs
const TabsContext = createContext(null);

export const Tabs = ({ children, value, onValueChange, className = '' }) => {
  const [activeTab, setActiveTab] = useState(value);

  // Update active tab when value changes
  React.useEffect(() => {
    if (value !== activeTab) {
      setActiveTab(value);
    }
  }, [value]);

  // Handle tab change
  const handleTabChange = (newValue) => {
    setActiveTab(newValue);
    if (onValueChange) {
      onValueChange(newValue);
    }
  };

  return (
    <TabsContext.Provider value={{ value: activeTab, onValueChange: handleTabChange }}>
      <div className={`tabs ${className}`}>
        {children}
      </div>
    </TabsContext.Provider>
  );
};

export const TabsList = ({ children, className = '' }) => {
  return (
    <div className={`flex border-b border-gray-200 ${className}`}>
      {children}
    </div>
  );
};

export const TabsTrigger = ({ children, value, className = '' }) => {
  const { value: activeValue, onValueChange } = useContext(TabsContext);
  const isActive = activeValue === value;

  return (
    <button
      className={`px-4 py-2 text-sm font-medium ${
        isActive
          ? 'text-primary-600 border-b-2 border-primary-600'
          : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
      } ${className}`}
      onClick={() => onValueChange(value)}
    >
      {children}
    </button>
  );
};

export const TabsContent = ({ children, value, className = '' }) => {
  const { value: activeValue } = useContext(TabsContext);
  const isActive = activeValue === value;

  if (!isActive) return null;

  return (
    <div className={`py-4 ${className}`}>
      {children}
    </div>
  );
};