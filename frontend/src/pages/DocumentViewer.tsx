import { useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useDocument } from '../context/DocumentContext'
import { useUI } from '../context/UIContext'
// We'll use a simpler approach for now to avoid any rendering issues
// import ReactMarkdown from 'react-markdown'
// import remarkGfm from 'remark-gfm'
// import rehypeRaw from 'rehype-raw'

const DocumentViewer = () => {
  const { documentId } = useParams<{ documentId: string }>()
  const { 
    document,
    sections,
    isLoading,
    error,
    viewMode,
    setViewMode,
    loadDocument,
    currentSection,
    setCurrentSection
  } = useDocument()
  
  const { showToast } = useUI()
  
  // Construct document content from sections
  const documentContent = 
    document ? 
      `# ${document.title}\n\n` + 
      sections.map(section => 
        `${'#'.repeat(section.level)} ${section.title}\n\n${section.content}`
      ).join('\n\n')
    : ''

  // Load document on mount
  useEffect(() => {
    if (documentId) {
      loadDocument(documentId).catch(err => {
        showToast('Error loading document', 'error')
        console.error('Error loading document:', err)
      })
    }
  }, [documentId, loadDocument, showToast])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading document...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-[calc(100vh-4rem)]">
      {/* Left sidebar - Outline */}
      <div className="w-64 border-r border-gray-200 bg-gray-50 overflow-y-auto p-4">
        <h2 className="text-lg font-bold mb-4">Outline</h2>
        <nav className="space-y-1">
          <div className="navigation-item-active">Abstract</div>
          <div className="navigation-item">1. Introduction</div>
          <div className="navigation-item">2. Background</div>
          <div className="navigation-item">3. Model Architecture</div>
          <div className="navigation-item">4. Experiments</div>
          <div className="navigation-item">5. Results</div>
          <div className="navigation-item">6. Conclusion</div>
          <div className="navigation-item">References</div>
        </nav>
      </div>

      {/* Main content */}
      <div className="flex-1 overflow-y-auto bg-white">
        {/* Document header */}
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              {document && (
                <>
                  <h1 className="text-xl font-bold">{document.title}</h1>
                  <p className="text-sm text-gray-600">{document.authors.join(', ')}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {document.publication_date ? `Published: ${new Date(document.publication_date).toLocaleDateString('en-US', { year: 'numeric', month: 'long' })}` : 'Publication date unknown'}
                    {document.journal_or_conference && ` • ${document.journal_or_conference}`}
                  </p>
                </>
              )}
            </div>
            <div className="flex space-x-2">
              <button 
                className={`btn ${viewMode === 'markdown' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setViewMode('markdown')}
              >
                Markdown
              </button>
              <button 
                className={`btn ${viewMode === 'pdf' ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setViewMode('pdf')}
              >
                PDF
              </button>
            </div>
          </div>
        </div>

        {/* Document content */}
        <div className="px-6 py-4">
          {viewMode === 'markdown' && document ? (
            <div className="prose prose-lg max-w-full bg-white p-4 rounded-md">
              {/* Using a simple approach to render markdown-like content */}
              <div className="markdown-content">
                {/* Split by newlines to handle headings properly */}
                {documentContent.split('\n').map((line, i) => {
                  // Trim the line to handle any extra spaces
                  const trimmedLine = line.trim();
                  
                  // Skip empty lines
                  if (trimmedLine === '') {
                    return null;
                  }
                  
                  // Simple heading detection
                  if (trimmedLine.startsWith('# ')) {
                    return <h1 key={i} className="text-2xl font-bold mb-4 mt-6">{trimmedLine.replace(/^# /, '')}</h1>
                  } else if (trimmedLine.startsWith('## ')) {
                    return <h2 key={i} className="text-xl font-semibold mb-3 mt-5">{trimmedLine.replace(/^## /, '')}</h2>
                  } else if (trimmedLine.startsWith('### ')) {
                    return <h3 key={i} className="text-lg font-medium mb-2 mt-4">{trimmedLine.replace(/^### /, '')}</h3>
                  } else if (/^\d+\.\s/.test(trimmedLine)) {
                    // Handle numbered list items
                    return <p key={i} className="mb-2 font-medium">{trimmedLine}</p>
                  } else {
                    // Regular paragraph with proper spacing
                    return (
                      <p key={i} className="mb-4">
                        {trimmedLine}
                      </p>
                    );
                  }
                })}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-[80vh]">
              <div className="text-center">
                <p className="text-gray-600">PDF viewer will be implemented in the next phase.</p>
                <button 
                  className="mt-4 btn btn-primary"
                  onClick={() => setViewMode('markdown')}
                >
                  Switch to Markdown View
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Right sidebar - Annotations and References */}
      <div className="w-72 border-l border-gray-200 bg-gray-50 overflow-y-auto p-4">
        <h2 className="text-lg font-bold mb-4">Annotations</h2>
        <div className="text-sm text-gray-600">
          <p>No annotations yet. This feature will be implemented in a future phase.</p>
        </div>
      </div>
    </div>
  )
}

export default DocumentViewer