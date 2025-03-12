import { Link, useNavigate } from 'react-router-dom'
import UploadModal from '../library/UploadModal'
import { useUI } from '../../context/UIContext'
import { useLibrary } from '../../context/LibraryContext'

const Navbar = () => {
  const { isUploadModalOpen, setUploadModalOpen, showToast } = useUI()
  const { refreshDocuments } = useLibrary()
  const navigate = useNavigate()
  
  const handleUploadComplete = (documentId: string) => {
    refreshDocuments()
    showToast('Document uploaded successfully!', 'success')
    navigate(`/documents/${documentId}`)
  }

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="text-xl font-bold text-primary-700">
                ScholarScribe
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              <Link
                to="/"
                className="border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium"
              >
                Library
              </Link>
            </div>
          </div>
          <div className="hidden sm:ml-6 sm:flex sm:items-center">
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => setIsUploadModalOpen(true)}
            >
              Upload Paper
            </button>
          </div>
        </div>
      </div>
      
      {/* Upload Modal */}
      <UploadModal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        onUploadComplete={handleUploadComplete}
      />
    </nav>
  )
}

export default Navbar