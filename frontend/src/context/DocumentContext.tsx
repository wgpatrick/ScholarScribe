import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { 
  Document, 
  Section, 
  Reference, 
  Figure, 
  getDocument, 
  getDocumentWithSections, 
  getDocumentReferences,
  getDocumentFigures
} from '../api/documents';

interface DocumentContextType {
  document: Document | null;
  sections: Section[];
  references: Reference[];
  figures: Figure[];
  isLoading: boolean;
  error: string | null;
  currentSection: string | null;
  setCurrentSection: (sectionId: string | null) => void;
  viewMode: 'markdown' | 'pdf';
  setViewMode: (mode: 'markdown' | 'pdf') => void;
  loadDocument: (id: string) => Promise<void>;
}

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export const useDocument = () => {
  const context = useContext(DocumentContext);
  if (context === undefined) {
    throw new Error('useDocument must be used within a DocumentProvider');
  }
  return context;
};

interface DocumentProviderProps {
  children: ReactNode;
}

// Mock data for initial development
const createMockDocument = (id: string): Document => ({
  id,
  title: id === '1' 
    ? 'Attention Is All You Need' 
    : id === '2'
      ? 'Deep Residual Learning for Image Recognition'
      : 'BERT: Pre-training of Deep Bidirectional Transformers',
  authors: id === '1'
    ? ['Ashish Vaswani', 'Noam Shazeer', 'Niki Parmar']
    : id === '2'
      ? ['Kaiming He', 'Xiangyu Zhang', 'Shaoqing Ren']
      : ['Jacob Devlin', 'Ming-Wei Chang', 'Kenton Lee'],
  abstract: id === '1' 
    ? 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.'
    : id === '2'
      ? 'Deeper neural networks are more difficult to train. We present a residual learning framework to ease the training of networks that are substantially deeper than those used previously. We explicitly reformulate the layers as learning residual functions with reference to the layer inputs, instead of learning unreferenced functions.'
      : 'We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.',
  processing_status: 'completed',
  created_at: '2025-03-10T10:00:00Z',
  updated_at: '2025-03-10T10:00:00Z',
  view_count: 0,
});

// Sample mock sections
const createMockSections = (documentId: string): Section[] => [
  {
    id: `${documentId}-s1`,
    document_id: documentId,
    title: 'Abstract',
    level: 1,
    order: 1,
    content: documentId === '1' 
      ? 'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...'
      : documentId === '2'
        ? 'Deeper neural networks are more difficult to train. We present a residual learning framework...'
        : 'We introduce a new language representation model called BERT...',
    word_count: 150,
    has_equations: false,
    has_figures: false,
    has_tables: false,
    keywords: ['abstract', 'summary']
  },
  {
    id: `${documentId}-s2`,
    document_id: documentId,
    title: 'Introduction',
    level: 1,
    order: 2,
    content: documentId === '1' 
      ? 'Recurrent neural networks, long short-term memory and gated recurrent neural networks in particular...'
      : documentId === '2'
        ? 'Deep convolutional neural networks have led to a series of breakthroughs for image classification...'
        : 'Language model pre-training has been shown to be effective for improving many natural language processing tasks...',
    word_count: 500,
    has_equations: false,
    has_figures: true,
    has_tables: false,
    keywords: ['introduction', 'background']
  },
  {
    id: `${documentId}-s3`,
    document_id: documentId,
    title: 'Background',
    level: 1,
    order: 3,
    content: documentId === '1' 
      ? 'The goal of reducing sequential computation also forms the foundation of the Extended Neural GPU...'
      : documentId === '2'
        ? 'When deeper networks are able to start converging, a degradation problem has been exposed...'
        : 'There are two existing strategies for applying pre-trained language representations to downstream tasks...',
    word_count: 700,
    has_equations: true,
    has_figures: false,
    has_tables: true,
    keywords: ['background', 'prior work']
  }
];

export const DocumentProvider = ({ children }: DocumentProviderProps) => {
  const [document, setDocument] = useState<Document | null>(null);
  const [sections, setSections] = useState<Section[]>([]);
  const [references, setReferences] = useState<Reference[]>([]);
  const [figures, setFigures] = useState<Figure[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentSection, setCurrentSection] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'markdown' | 'pdf'>('markdown');

  const loadDocument = async (id: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Fetch document with sections from API
      try {
        const documentWithSections = await getDocumentWithSections(id);
        setDocument(documentWithSections);
        setSections(documentWithSections.sections || []);
        
        // Fetch references and figures
        const referencesData = await getDocumentReferences(id);
        setReferences(referencesData);
        
        const figuresData = await getDocumentFigures(id);
        setFigures(figuresData);
      } catch (error) {
        console.error('Error fetching document from API, falling back to mock data:', error);
        
        // Fallback to mock data if API call fails
        setDocument(createMockDocument(id));
        setSections(createMockSections(id));
        setReferences([]);
        setFigures([]);
      }
      
      // Set the current section to the first section by default
      if (sections.length > 0) {
        setCurrentSection(sections[0].id);
        
        // Scroll to top of document
        window.scrollTo({ top: 0, behavior: 'auto' });
      }
    } catch (err) {
      console.error('Error loading document:', err);
      setError('Failed to load document. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    document,
    sections,
    references,
    figures,
    isLoading,
    error,
    currentSection,
    setCurrentSection,
    viewMode,
    setViewMode,
    loadDocument
  };

  return (
    <DocumentContext.Provider value={value}>
      {children}
    </DocumentContext.Provider>
  );
};