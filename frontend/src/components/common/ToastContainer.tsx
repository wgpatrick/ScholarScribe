import React from 'react';
import { useUI } from '../../context/UIContext';

const ToastContainer = () => {
  const { toasts, dismissToast } = useUI();

  if (toasts.length === 0) {
    return null;
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map(toast => (
        <div 
          key={toast.id}
          className={`p-4 rounded-md shadow-lg max-w-xs flex justify-between items-center transition-all duration-300 ${
            toast.type === 'success' ? 'bg-green-100 text-green-800 border-l-4 border-green-500' :
            toast.type === 'error' ? 'bg-red-100 text-red-800 border-l-4 border-red-500' :
            'bg-blue-100 text-blue-800 border-l-4 border-blue-500'
          }`}
        >
          <span>{toast.message}</span>
          <button 
            onClick={() => dismissToast(toast.id)}
            className="ml-2 text-gray-500 hover:text-gray-700"
            aria-label="Dismiss"
          >
            &times;
          </button>
        </div>
      ))}
    </div>
  );
};

export default ToastContainer;