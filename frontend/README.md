# ScholarScribe Frontend

This is the frontend application for ScholarScribe, an academic paper reader and note-taking application.

## Running the Application

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open the application in your browser:
   - The application will be available at http://localhost:5173 (or another port if 5173 is in use)

## Features Implemented

- Document library dashboard with search and filtering
- Document upload with drag-and-drop support
- Document viewing with toggle between Markdown and PDF
- Section navigation sidebar
- Basic application layout and routing

## Next Steps

- Complete PDF viewer implementation
- Add position synchronization between PDF and Markdown views
- Implement section summaries in navigation
- Add annotation and comment system
- Create reference display in the sidebar

## Troubleshooting

If you encounter any issues:

1. Make sure the backend server is running (see main project README)
2. Ensure all dependencies are installed with `npm install`
3. Check for TypeScript errors with `npm run type-check`
4. For TailwindCSS issues, make sure the PostCSS configuration is correct