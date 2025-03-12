import { Routes, Route } from 'react-router-dom'
import { Suspense, lazy } from 'react'
import AppLayout from './components/common/AppLayout'
import { AppProviders } from './context'
import ToastContainer from './components/common/ToastContainer'

// Lazy-loaded components
const LibraryDashboard = lazy(() => import('./pages/LibraryDashboard'))
const DocumentViewer = lazy(() => import('./pages/DocumentViewer'))
const NotFound = lazy(() => import('./pages/NotFound'))

// Loading component
const Loading = () => (
  <div className="flex items-center justify-center h-screen">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-700 mx-auto"></div>
      <p className="mt-4 text-gray-600">Loading...</p>
    </div>
  </div>
)

function App() {
  return (
    <AppProviders>
      <Suspense fallback={<Loading />}>
        <Routes>
          <Route path="/" element={<AppLayout />}>
            <Route index element={<LibraryDashboard />} />
            <Route path="documents/:documentId" element={<DocumentViewer />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </Suspense>
      <ToastContainer />
    </AppProviders>
  )
}

export default App