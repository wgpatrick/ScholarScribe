import { useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useDocument } from '../context/DocumentContext'
import { useUI } from '../context/UIContext'
import OutlineNavigator from '../components/navigation/OutlineNavigator'
import ReadingProgress from '../components/document/ReadingProgress'
import BackToTop from '../components/document/BackToTop'
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

  // Create a ref for the content container
  const contentRef = useRef<HTMLDivElement>(null);
  
  // Load document on mount
  useEffect(() => {
    if (documentId) {
      loadDocument(documentId).catch(err => {
        showToast('Error loading document', 'error');
        console.error('Error loading document:', err);
      });
    }
  }, [documentId, loadDocument, showToast]);
  
  // Implement scroll spy to track current section
  useEffect(() => {
    if (!contentRef.current || sections.length === 0) return;
    
    const handleScroll = () => {
      // Get all section elements
      const sectionElements = sections.map(section => 
        document.getElementById(`section-${section.id}`)
      ).filter(Boolean) as HTMLElement[];
      
      if (sectionElements.length === 0) return;
      
      // Find the section currently in view
      const scrollPosition = window.scrollY + 100; // Add offset for header
      
      // Find the last section that starts before the current scroll position
      for (let i = sectionElements.length - 1; i >= 0; i--) {
        const section = sectionElements[i];
        if (section.offsetTop <= scrollPosition) {
          const sectionId = section.id.replace('section-', '');
          if (currentSection !== sectionId) {
            setCurrentSection(sectionId);
          }
          break;
        }
      }
    };
    
    // Add scroll event listener
    window.addEventListener('scroll', handleScroll);
    
    // Initial check
    handleScroll();
    
    // Clean up
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [sections, setCurrentSection, currentSection]);

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
      {/* Left sidebar - Outline Navigator */}
      <OutlineNavigator />

      {/* Main content */}
      <div className="flex-1 overflow-y-auto bg-white">
        {/* Reading progress indicator */}
        <ReadingProgress />
        
        {/* Document header */}
        <div className="sticky top-1 z-10 bg-white border-b border-gray-200 px-6 py-4">
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
        <div className="px-6 py-4" ref={contentRef}>
          {viewMode === 'markdown' && document ? (
            <div className="prose prose-lg max-w-full bg-white p-4 rounded-md">
              {/* Using a simple approach to render markdown-like content */}
              <div className="markdown-content">
                {/* Render sections with proper IDs for navigation */}
                {sections.map((section) => (
                  <div key={section.id} id={`section-${section.id}`} className="mb-8 scroll-mt-20">
                    {/* Section heading based on level */}
                    {section.level === 1 ? (
                      <h1 className="text-2xl font-bold mb-4 mt-6">{section.title}</h1>
                    ) : section.level === 2 ? (
                      <h2 className="text-xl font-semibold mb-3 mt-5">{section.title}</h2>
                    ) : section.level === 3 ? (
                      <h3 className="text-lg font-medium mb-2 mt-4">{section.title}</h3>
                    ) : (
                      <h4 className="text-base font-medium mb-2 mt-3">{section.title}</h4>
                    )}
                    
                    {/* Section content - split by paragraphs */}
                    {section.content.split('\n\n').map((paragraph, i) => {
                      // Skip empty paragraphs
                      if (!paragraph.trim()) return null;
                      
                      // Handle numbered list items
                      if (/^\d+\.\s/.test(paragraph)) {
                        return <p key={i} className="mb-2 font-medium">{paragraph}</p>;
                      }
                      
                      // Regular paragraph
                      return (
                        <p key={i} className="mb-4">
                          {paragraph}
                        </p>
                      );
                    })}
                  </div>
                ))}
              </div>
              
              {/* Back to top button */}
              <BackToTop />
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