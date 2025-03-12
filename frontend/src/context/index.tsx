import React, { ReactNode } from 'react';
import { LibraryProvider } from './LibraryContext';
import { DocumentProvider } from './DocumentContext';
import { UIProvider } from './UIContext';

interface AppProvidersProps {
  children: ReactNode;
}

export const AppProviders = ({ children }: AppProvidersProps) => {
  return (
    <UIProvider>
      <LibraryProvider>
        <DocumentProvider>
          {children}
        </DocumentProvider>
      </LibraryProvider>
    </UIProvider>
  );
};