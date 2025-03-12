import React, { createContext, useContext, useState, ReactNode } from 'react';

interface UIContextType {
  // Sidebar visibility
  isOutlineSidebarOpen: boolean;
  setOutlineSidebarOpen: (isOpen: boolean) => void;
  isAnnotationSidebarOpen: boolean;
  setAnnotationSidebarOpen: (isOpen: boolean) => void;
  
  // Modal states
  isUploadModalOpen: boolean;
  setUploadModalOpen: (isOpen: boolean) => void;
  
  // UI preferences (could be saved to localStorage)
  fontSize: 'small' | 'medium' | 'large';
  setFontSize: (size: 'small' | 'medium' | 'large') => void;
  
  // Toast notifications
  showToast: (message: string, type: 'success' | 'error' | 'info') => void;
  toasts: Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>;
  dismissToast: (id: string) => void;
}

const UIContext = createContext<UIContextType | undefined>(undefined);

export const useUI = () => {
  const context = useContext(UIContext);
  if (context === undefined) {
    throw new Error('useUI must be used within a UIProvider');
  }
  return context;
};

interface UIProviderProps {
  children: ReactNode;
}

export const UIProvider = ({ children }: UIProviderProps) => {
  // Sidebar visibility
  const [isOutlineSidebarOpen, setOutlineSidebarOpen] = useState(true);
  const [isAnnotationSidebarOpen, setAnnotationSidebarOpen] = useState(true);
  
  // Modal states
  const [isUploadModalOpen, setUploadModalOpen] = useState(false);
  
  // UI preferences
  const [fontSize, setFontSize] = useState<'small' | 'medium' | 'large'>('medium');
  
  // Toast notifications
  const [toasts, setToasts] = useState<Array<{ id: string; message: string; type: 'success' | 'error' | 'info' }>>([]);
  
  const showToast = (message: string, type: 'success' | 'error' | 'info') => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { id, message, type }]);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
      dismissToast(id);
    }, 5000);
  };
  
  const dismissToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const value = {
    isOutlineSidebarOpen,
    setOutlineSidebarOpen,
    isAnnotationSidebarOpen,
    setAnnotationSidebarOpen,
    isUploadModalOpen,
    setUploadModalOpen,
    fontSize,
    setFontSize,
    showToast,
    toasts,
    dismissToast
  };

  return (
    <UIContext.Provider value={value}>
      {children}
    </UIContext.Provider>
  );
};