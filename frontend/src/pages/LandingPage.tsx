import { Link } from 'react-router-dom';

/**
 * Clean, professional landing page for AI Nurse Florence
 * Content-focused design for October 15th soft launch
 * Minimal marketing text - let the work speak for itself
 */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-indigo-900">AI Nurse Florence</h1>
              <p className="text-sm text-gray-600 mt-1">Clinical Intelligence for Healthcare Professionals</p>
            </div>
            <Link
              to="/login"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Sign In
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Evidence-Based Clinical Decision Support
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Real-time integration with NIH, FDA, PubMed, and ClinicalTrials.gov
          </p>
          <div className="flex gap-4 justify-center">
            <a
              href="/public/drug-interactions"
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
            >
              Try Drug Interaction Checker
            </a>
            <a
              href="#resources"
              className="px-6 py-3 bg-white text-indigo-600 border-2 border-indigo-600 rounded-lg hover:bg-indigo-50 transition-colors font-medium"
            >
              Access Open Data
            </a>
          </div>
        </div>
      </section>

      {/* Live Tools Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 bg-white rounded-2xl shadow-sm mb-16">
        <h3 className="text-2xl font-bold text-gray-900 mb-8">Live Clinical Tools</h3>

        <div className="grid md:grid-cols-3 gap-8">
          {/* Drug Interaction Checker */}
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                <i className="fas fa-pills text-green-600 text-xl"></i>
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Drug Interaction Checker</h4>
            </div>
            <ul className="space-y-2 mb-4 text-sm text-gray-600">
              <li className="flex items-center">
                <i className="fas fa-check text-green-500 mr-2"></i>
                Free, no login required
              </li>
              <li className="flex items-center">
                <i className="fas fa-check text-green-500 mr-2"></i>
                Comprehensive analysis
              </li>
              <li className="flex items-center">
                <i className="fas fa-check text-green-500 mr-2"></i>
                Clinical decision support
              </li>
            </ul>
            <a
              href="/public/drug-interactions"
              className="text-indigo-600 hover:text-indigo-800 font-medium inline-flex items-center"
            >
              Launch Tool <i className="fas fa-arrow-right ml-2"></i>
            </a>
          </div>

          {/* Disease Information */}
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                <i className="fas fa-disease text-blue-600 text-xl"></i>
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Disease Information</h4>
            </div>
            <ul className="space-y-2 mb-4 text-sm text-gray-600">
              <li className="flex items-center">
                <i className="fas fa-check text-green-500 mr-2"></i>
                10,000+ disease database
              </li>
              <li className="flex items-center">
                <i className="fas fa-check text-green-500 mr-2"></i>
                Live NIH/FDA integration
              </li>
              <li className="flex items-center">
                <i className="fas fa-check text-green-500 mr-2"></i>
                Genetic information
              </li>
            </ul>
            <Link
              to="/disease-info"
              className="text-indigo-600 hover:text-indigo-800 font-medium inline-flex items-center"
            >
              Search Diseases <i className="fas fa-arrow-right ml-2"></i>
            </Link>
          </div>

          {/* Clinical Trials */}
          <div className="border border-gray-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                <i className="fas fa-flask text-purple-600 text-xl"></i>
              </div>
              <h4 className="text-lg font-semibold text-gray-900">Clinical Trial Search</h4>
            </div>
            <ul className="space-y-2 mb-4 text-sm text-gray-600">
              <li className="flex items-center">
                <i className="fas fa-check text-green-500 mr-2"></i>
                Live ClinicalTrials.gov data
              </li>
              <li className="flex items-center">
                <i className="fas fa-check text-green-500 mr-2"></i>
                Real-time eligibility
              </li>
              <li className="flex items-center">
                <i className="fas fa-check text-green-500 mr-2"></i>
                16 language support
              </li>
            </ul>
            <Link
              to="/clinical-trials"
              className="text-indigo-600 hover:text-indigo-800 font-medium inline-flex items-center"
            >
              Search Trials <i className="fas fa-arrow-right ml-2"></i>
            </Link>
          </div>
        </div>
      </section>

      {/* Open Data Resources */}
      <section id="resources" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 mb-16">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">Open Data Resources</h3>
        <p className="text-gray-600 mb-8">Free medical datasets for the healthcare community</p>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Disease Database */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <i className="fas fa-database text-indigo-600 mr-2"></i>
              Disease Database (JSON)
            </h4>
            <p className="text-sm text-gray-600 mb-4">
              10,000+ diseases with synonyms, MONDO IDs, and clinical information
            </p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">5.2 MB • CC-BY-4.0 • Updated Oct 2025</span>
              <button className="text-indigo-600 hover:text-indigo-800 font-medium text-sm">
                Download <i className="fas fa-download ml-1"></i>
              </button>
            </div>
          </div>

          {/* Medication Library */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <i className="fas fa-capsules text-indigo-600 mr-2"></i>
              Drug Name Dictionary (JSON)
            </h4>
            <p className="text-sm text-gray-600 mb-4">
              Generic names, brand names, and common spelling variations
            </p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">Coming Soon • CC-BY-4.0</span>
              <button disabled className="text-gray-400 font-medium text-sm cursor-not-allowed">
                Download <i className="fas fa-download ml-1"></i>
              </button>
            </div>
          </div>

          {/* Medical Abbreviations */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <i className="fas fa-book-medical text-indigo-600 mr-2"></i>
              Medical Abbreviations (JSON)
            </h4>
            <p className="text-sm text-gray-600 mb-4">
              5,000+ common medical abbreviations and definitions
            </p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">Coming Soon • CC-BY-4.0</span>
              <button disabled className="text-gray-400 font-medium text-sm cursor-not-allowed">
                Download <i className="fas fa-download ml-1"></i>
              </button>
            </div>
          </div>

          {/* GitHub Repository */}
          <div className="bg-white border border-gray-200 rounded-lg p-6">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <i className="fab fa-github text-indigo-600 mr-2"></i>
              GitHub Data Repository
            </h4>
            <p className="text-sm text-gray-600 mb-4">
              All datasets, documentation, and integration examples
            </p>
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500">Coming Soon</span>
              <button disabled className="text-gray-400 font-medium text-sm cursor-not-allowed">
                View on GitHub <i className="fas fa-external-link-alt ml-1"></i>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Technical Capabilities */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 bg-white rounded-2xl shadow-sm mb-16">
        <h3 className="text-2xl font-bold text-gray-900 mb-8">Technical Capabilities</h3>

        <div className="grid md:grid-cols-2 gap-12">
          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Data Integration</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <i className="fas fa-circle text-indigo-600 text-xs mt-1.5 mr-2"></i>
                NIH APIs: MyDisease.info, MyGene.info, MyChem.info
              </li>
              <li className="flex items-start">
                <i className="fas fa-circle text-indigo-600 text-xs mt-1.5 mr-2"></i>
                FDA: Drug labels, adverse events
              </li>
              <li className="flex items-start">
                <i className="fas fa-circle text-indigo-600 text-xs mt-1.5 mr-2"></i>
                PubMed: 35M+ biomedical articles
              </li>
              <li className="flex items-start">
                <i className="fas fa-circle text-indigo-600 text-xs mt-1.5 mr-2"></i>
                ClinicalTrials.gov: Live trial data
              </li>
              <li className="flex items-start">
                <i className="fas fa-circle text-indigo-600 text-xs mt-1.5 mr-2"></i>
                MedlinePlus: Patient education
              </li>
            </ul>
          </div>

          <div>
            <h4 className="font-semibold text-gray-900 mb-4">Clinical Features</h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start">
                <i className="fas fa-circle text-indigo-600 text-xs mt-1.5 mr-2"></i>
                SBAR report generation
              </li>
              <li className="flex items-start">
                <i className="fas fa-circle text-indigo-600 text-xs mt-1.5 mr-2"></i>
                Discharge instruction creation
              </li>
              <li className="flex items-start">
                <i className="fas fa-circle text-indigo-600 text-xs mt-1.5 mr-2"></i>
                Medication guides (16 languages)
              </li>
              <li className="flex items-start">
                <i className="fas fa-circle text-indigo-600 text-xs mt-1.5 mr-2"></i>
                Patient education materials
              </li>
              <li className="flex items-start">
                <i className="fas fa-circle text-indigo-600 text-xs mt-1.5 mr-2"></i>
                Incident reporting
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200">
          <div className="flex items-center gap-8 text-sm text-gray-600">
            <div className="flex items-center">
              <i className="fas fa-server text-indigo-600 mr-2"></i>
              Redis caching
            </div>
            <div className="flex items-center">
              <i className="fas fa-shield-alt text-indigo-600 mr-2"></i>
              HIPAA-compliant
            </div>
            <div className="flex items-center">
              <i className="fas fa-chart-line text-indigo-600 mr-2"></i>
              Prometheus monitoring
            </div>
            <div className="flex items-center">
              <i className="fas fa-globe text-indigo-600 mr-2"></i>
              16 languages
            </div>
          </div>
        </div>
      </section>

      {/* For Decision Makers */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 mb-16">
        <div className="bg-gradient-to-r from-indigo-600 to-purple-600 rounded-2xl p-12 text-white">
          <h3 className="text-2xl font-bold mb-6">For Decision Makers</h3>

          <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div>
              <h4 className="font-semibold mb-4">Why Collaborate</h4>
              <ul className="space-y-3 text-indigo-100">
                <li className="flex items-start">
                  <i className="fas fa-check-circle mr-3 mt-1"></i>
                  Live medical data integration with authoritative sources
                </li>
                <li className="flex items-start">
                  <i className="fas fa-check-circle mr-3 mt-1"></i>
                  Open knowledge sharing for community benefit
                </li>
                <li className="flex items-start">
                  <i className="fas fa-check-circle mr-3 mt-1"></i>
                  Proven implementation (132 API endpoints, production-ready)
                </li>
                <li className="flex items-start">
                  <i className="fas fa-check-circle mr-3 mt-1"></i>
                  Built for nurses and healthcare professionals
                </li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Community Service</h4>
              <p className="text-indigo-100 mb-4">
                Our public Drug Interaction Checker replaces the discontinued NIH Drug Interaction API,
                providing free clinical decision support to the healthcare community.
              </p>
              <div className="bg-white/10 rounded-lg p-4">
                <p className="font-medium mb-2">Contact</p>
                <p className="text-sm text-indigo-100">patrick.roebuck1955@gmail.com</p>
                <p className="text-sm text-indigo-100">github.com/silversurfer562/ai-nurse-florence</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Beta Access */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 mb-16">
        <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">Request Beta Access</h3>
          <p className="text-gray-600 mb-6">
            Professional platform includes advanced clinical documentation, SBAR wizards,
            multi-language document generation, and HIPAA-compliant workflow tools.
          </p>
          <Link
            to="/register"
            className="inline-block px-8 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            Request Access
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <h5 className="font-semibold text-white mb-4">AI Nurse Florence</h5>
              <p className="text-sm text-gray-400">
                Clinical intelligence for healthcare professionals.
                Evidence-based decision support powered by live medical data.
              </p>
            </div>
            <div>
              <h5 className="font-semibold text-white mb-4">Resources</h5>
              <ul className="space-y-2 text-sm">
                <li><a href="/public/drug-interactions" className="hover:text-white">Drug Interaction Checker</a></li>
                <li><a href="#resources" className="hover:text-white">Open Data</a></li>
                <li><a href="https://github.com/silversurfer562/ai-nurse-florence" className="hover:text-white">GitHub</a></li>
                <li><Link to="/login" className="hover:text-white">Sign In</Link></li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold text-white mb-4">Legal</h5>
              <ul className="space-y-2 text-sm">
                <li><a href="/LICENSE" className="hover:text-white">Apache 2.0 License</a></li>
                <li><a href="/NOTICE" className="hover:text-white">Patent Grant Notice</a></li>
                <li><a href="/PATENTS.md" className="hover:text-white">IP Protection</a></li>
              </ul>
            </div>
          </div>
          <div className="pt-8 border-t border-gray-800 text-sm text-gray-400 text-center">
            <p>Copyright 2023-2025 DeepStudy AI, LLC. Licensed under Apache 2.0.</p>
            <p className="mt-2">Built for healthcare professionals. HIPAA-compliant. No PHI storage.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
