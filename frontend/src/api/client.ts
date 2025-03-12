// Base API client for making requests to the backend

const API_BASE_URL = '/api'

interface ApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'
  body?: any
  headers?: Record<string, string>
}

/**
 * Generic API request function
 * 
 * @param endpoint - API endpoint to request
 * @param options - Request options
 * @returns Promise with response data
 */
export async function apiRequest<T = any>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const { method = 'GET', body, headers = {} } = options
  
  const requestHeaders: Record<string, string> = {
    'Content-Type': 'application/json',
    ...headers
  }
  
  const config: RequestInit = {
    method,
    headers: requestHeaders,
    credentials: 'same-origin',
  }
  
  if (body) {
    config.body = JSON.stringify(body)
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, config)
  
  if (!response.ok) {
    // Get error message from the response
    let errorMessage = 'An error occurred'
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch (err) {
      // If response doesn't contain valid JSON
      errorMessage = response.statusText
    }
    
    throw new Error(`API Error: ${errorMessage}`)
  }
  
  // Check if response is empty
  const contentType = response.headers.get('content-type')
  if (contentType && contentType.includes('application/json')) {
    return await response.json() as T
  }
  
  return {} as T
}

/**
 * File upload function
 * 
 * @param endpoint - API endpoint for file upload
 * @param file - File to upload
 * @param additionalData - Additional form data to include
 * @returns Promise with response data
 */
export async function uploadFile<T = any>(
  endpoint: string, 
  file: File, 
  additionalData: Record<string, string> = {}
): Promise<T> {
  const formData = new FormData()
  formData.append('file', file)
  
  // Add any additional data
  Object.entries(additionalData).forEach(([key, value]) => {
    formData.append(key, value)
  })
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    body: formData,
    credentials: 'same-origin',
  })
  
  if (!response.ok) {
    // Get error message from the response
    let errorMessage = 'An error occurred during file upload'
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorData.message || errorMessage
    } catch (err) {
      // If response doesn't contain valid JSON
      errorMessage = response.statusText
    }
    
    throw new Error(`API Error: ${errorMessage}`)
  }
  
  return await response.json() as T
}

// Export common API methods
export const api = {
  get: <T = any>(endpoint: string, headers?: Record<string, string>) => 
    apiRequest<T>(endpoint, { method: 'GET', headers }),
    
  post: <T = any>(endpoint: string, body: any, headers?: Record<string, string>) => 
    apiRequest<T>(endpoint, { method: 'POST', body, headers }),
    
  put: <T = any>(endpoint: string, body: any, headers?: Record<string, string>) => 
    apiRequest<T>(endpoint, { method: 'PUT', body, headers }),
    
  patch: <T = any>(endpoint: string, body: any, headers?: Record<string, string>) => 
    apiRequest<T>(endpoint, { method: 'PATCH', body, headers }),
    
  delete: <T = any>(endpoint: string, headers?: Record<string, string>) => 
    apiRequest<T>(endpoint, { method: 'DELETE', headers }),
    
  upload: uploadFile
}