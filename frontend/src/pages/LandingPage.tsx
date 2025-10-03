/**
 * Simple landing page for AI Nurse Florence public tools
 * Focused on the free drug interaction checker
 */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            <i className="fas fa-heart-pulse text-blue-600 mr-3"></i>
            AI Nurse Florence
          </h1>
          <p className="text-2xl text-gray-600 mb-2">
            Free Clinical Decision Support Tools
          </p>
          <p className="text-lg text-gray-500">
            Serving the healthcare community with evidence-based information
          </p>
        </div>

        {/* Main CTA - Drug Interaction Checker */}
        <div className="bg-white rounded-2xl shadow-lg p-12 mb-12 border border-blue-100">
          <div className="text-center mb-8">
            <div className="inline-block p-4 bg-blue-100 rounded-full mb-4">
              <i className="fas fa-pills text-blue-600 text-5xl"></i>
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Free Drug Interaction Checker
            </h2>
            <p className="text-xl text-gray-600 mb-6">
              Check medication interactions instantly - No login required
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="text-center">
              <i className="fas fa-check-circle text-green-500 text-3xl mb-2"></i>
              <p className="font-semibold text-gray-900">Always Free</p>
              <p className="text-sm text-gray-600">No account needed</p>
            </div>
            <div className="text-center">
              <i className="fas fa-database text-blue-500 text-3xl mb-2"></i>
              <p className="font-semibold text-gray-900">Comprehensive</p>
              <p className="text-sm text-gray-600">500+ medications</p>
            </div>
            <div className="text-center">
              <i className="fas fa-shield-alt text-purple-500 text-3xl mb-2"></i>
              <p className="font-semibold text-gray-900">Private</p>
              <p className="text-sm text-gray-600">No data stored</p>
            </div>
          </div>

          <div className="text-center">
            <a
              href="/drug-checker"
              className="inline-block px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 transition-colors shadow-md"
            >
              <i className="fas fa-arrow-right mr-2"></i>
              Start Checking Medications
            </a>
          </div>
        </div>

        {/* Mission Statement */}
        <div className="bg-blue-50 border-l-4 border-blue-600 p-8 rounded-r-lg">
          <h3 className="text-xl font-semibold text-blue-900 mb-4">
            <i className="fas fa-heart mr-2"></i>
            Our Mission: Serving the Healthcare Community
          </h3>
          <div className="text-blue-800 space-y-3">
            <p>
              When the NIH Drug Interaction API was discontinued, the healthcare community lost a valuable public resource.
              We're providing this free tool to help fill that gap and serve patients, caregivers, and healthcare consumers.
            </p>
            <p>
              AI Nurse Florence is a clinical decision support platform designed to help nurses work more efficiently
              and deliver better patient care. This free public tool is part of our commitment to serving the healthcare
              community and advancing accessible health technology.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8 mt-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-sm text-gray-400">
            &copy; 2025 AI Nurse Florence. Educational use only - not medical advice.
          </p>
          <p className="text-xs text-gray-500 mt-2">
            Always consult your healthcare provider about your medications and health concerns.
          </p>
        </div>
      </footer>
    </div>
  );
}
