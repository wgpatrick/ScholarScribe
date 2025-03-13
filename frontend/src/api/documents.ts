import { api } from './client'

// Types
export interface Document {
  id: string
  title: string
  authors: string[]
  abstract: string
  publication_date?: string
  journal_or_conference?: string
  doi?: string
  processing_status: 'pending' | 'processing' | 'completed' | 'failed'
  parsing_method?: string
  parsing_error?: string
  created_at: string
  updated_at: string
  last_viewed_at?: string
  view_count: number
}

export interface Section {
  id: string
  document_id: string
  title: string
  level: number
  order: number
  parent_id?: string
  content: string
  summary?: string
  word_count: number
  has_equations: boolean
  has_figures: boolean
  has_tables: boolean
  keywords: string[]
}

export interface Reference {
  id: string
  document_id: string
  raw_citation: string
  order: number
  title?: string
  authors: string[]
  publication_year?: number
  journal_or_conference?: string
  doi?: string
  url?: string
}

export interface Figure {
  id: string
  document_id: string
  section_id?: string
  figure_type: 'figure' | 'table' | 'equation'
  caption: string
  content?: string
  image_path?: string
  order: number
  reference_id: string
}

// API functions

/**
 * Get all documents
 */
export async function getDocuments() {
  return api.get<Document[]>('/documents/')
}

/**
 * Get a document by ID
 */
export async function getDocument(id: string) {
  return api.get<Document>(`/documents/${id}`)
}

/**
 * Get a document with its sections
 */
export async function getDocumentWithSections(id: string) {
  return api.get<Document & { sections: Section[] }>(`/documents/${id}/with-sections`)
}

/**
 * Get document references
 */
export async function getDocumentReferences(id: string) {
  return api.get<Reference[]>(`/documents/${id}/references`)
}

/**
 * Get document figures
 */
export async function getDocumentFigures(id: string) {
  return api.get<Figure[]>(`/documents/${id}/figures`)
}

/**
 * Upload a new document
 */
export async function uploadDocument(file: File, metadata?: Record<string, string>) {
  return api.upload<Document>('/documents/', file, metadata || {})
}

/**
 * Delete a document
 */
export async function deleteDocument(id: string) {
  return api.delete(`/documents/${id}`)
}

/**
 * Get document processing status
 */
export async function getDocumentStatus(id: string) {
  // Since there's no dedicated status endpoint, we'll get the document and check its status
  const document = await api.get<Document>(`/documents/${id}`);
  return { status: document.processing_status };
}