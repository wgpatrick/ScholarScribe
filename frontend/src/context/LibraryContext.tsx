import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { Document, getDocuments } from '../api/documents';

interface LibraryContextType {
  documents: Document[];
  isLoading: boolean;
  error: string | null;
  refreshDocuments: () => Promise<void>;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  filteredDocuments: Document[];
  viewMode: 'grid' | 'list';
  setViewMode: (mode: 'grid' | 'list') => void;
}

const LibraryContext = createContext<LibraryContextType | undefined>(undefined);

export const useLibrary = () => {
  const context = useContext(LibraryContext);
  if (context === undefined) {
    throw new Error('useLibrary must be used within a LibraryProvider');
  }
  return context;
};

interface LibraryProviderProps {
  children: ReactNode;
}

// Mock data for initial development
const MOCK_DOCUMENTS: Document[] = [
  {
    id: '1',
    title: 'Attention Is All You Need',
    authors: ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar'],
    abstract: 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...',
    processing_status: 'completed',
    created_at: '2025-03-10T10:00:00Z',
    updated_at: '2025-03-10T10:00:00Z',
    view_count: 5,
    last_viewed_at: '2025-03-12T10:00:00Z',
  },
  {
    id: '2',
    title: 'Deep Residual Learning for Image Recognition',
    authors: ['Kaiming He', 'Xiangyu Zhang', 'Shaoqing Ren'],
    abstract: 'Deeper neural networks are more difficult to train. We present a residual learning framework...',
    processing_status: 'completed',
    created_at: '2025-03-08T15:30:00Z',
    updated_at: '2025-03-08T15:30:00Z',
    view_count: 3,
    last_viewed_at: '2025-03-10T15:30:00Z',
  },
  {
    id: '3',
    title: 'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding',
    authors: ['Jacob Devlin', 'Ming-Wei Chang', 'Kenton Lee'],
    abstract: 'We introduce a new language representation model called BERT...',
    processing_status: 'processing',
    created_at: '2025-03-12T08:00:00Z',
    updated_at: '2025-03-12T08:00:00Z',
    view_count: 0,
  }
];

export const LibraryProvider = ({ children }: LibraryProviderProps) => {
  const [documents, setDocuments] = useState<Document[]>(MOCK_DOCUMENTS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');

  const refreshDocuments = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Uncomment the below line to fetch from API when ready
      // const data = await getDocuments();
      // setDocuments(data);
      
      // For now, use mock data
      // This setTimeout simulates network delay
      await new Promise(resolve => setTimeout(resolve, 500));
      setDocuments(MOCK_DOCUMENTS);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setError('Failed to load documents. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  // Filter documents based on search query
  const filteredDocuments = documents.filter(doc => 
    doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    doc.authors.some(author => author.toLowerCase().includes(searchQuery.toLowerCase())) ||
    (doc.abstract && doc.abstract.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Load documents on initial render
  useEffect(() => {
    refreshDocuments();
  }, []);

  const value = {
    documents,
    isLoading,
    error,
    refreshDocuments,
    searchQuery,
    setSearchQuery,
    filteredDocuments,
    viewMode,
    setViewMode
  };

  return (
    <LibraryContext.Provider value={value}>
      {children}
    </LibraryContext.Provider>
  );
};