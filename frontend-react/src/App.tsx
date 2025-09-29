import { Navigation } from '@components/Navigation'
import { HomePage } from '@pages/HomePage'
import { SbarWizardPage } from '@pages/SbarWizardPage'
import { WizardHub } from '@pages/WizardHub'
import { Route, Routes } from 'react-router-dom'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Clinical Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-clinical-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900">AI Nurse Florence</h1>
                <p className="text-sm text-gray-500">Healthcare AI Assistant</p>
              </div>
            </div>

            <Navigation />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Clinical Disclaimer */}
        <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center gap-2">
            <svg className="w-5 h-5 text-yellow-600" fill="currentColor" viewBox="0 0 24 24">
              <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
            </svg>
            <p className="text-sm text-yellow-800">
              <strong>Clinical Tool:</strong> For healthcare professionals only.
              Always follow facility protocols and consult with providers as needed.
            </p>
          </div>
        </div>

        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/wizards" element={<WizardHub />} />
          <Route path="/wizards/sbar" element={<SbarWizardPage />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center text-sm text-gray-500">
            <p>AI Nurse Florence v2.1.0 | Educational use only - not medical advice | No PHI stored</p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
