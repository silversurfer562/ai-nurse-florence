/**
 * AI Nurse Florence Landing Page
 * Modern clinical decision support platform for nursing professionals
 */
export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <i className="fas fa-heart-pulse text-secondary-500 text-2xl mr-3"></i>
              <span className="text-xl font-bold text-gray-900">AI Nurse Florence</span>
            </div>
            <div className="flex items-center gap-4">
              <a href="/drug-checker" className="text-gray-600 hover:text-primary-600 transition-colors">
                Drug Checker
              </a>
              <a
                href="/app"
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Sign In
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-50 via-white to-secondary-50 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              Clinical Decision Support
              <span className="block text-primary-600 mt-2">Built for Nurses</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              AI-powered tools to help you document faster, make confident decisions,
              and deliver exceptional patient care.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/app"
                className="px-8 py-4 bg-primary-600 text-white text-lg font-semibold rounded-lg hover:bg-primary-700 transition-colors shadow-lg"
              >
                <i className="fas fa-rocket mr-2"></i>
                Get Started Free
              </a>
              <a
                href="/drug-checker"
                className="px-8 py-4 bg-white text-primary-600 text-lg font-semibold rounded-lg hover:bg-gray-50 transition-colors shadow-lg border-2 border-primary-600"
              >
                <i className="fas fa-pills mr-2"></i>
                Try Drug Checker
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything You Need to Deliver Better Care
            </h2>
            <p className="text-xl text-gray-600">
              Comprehensive clinical wizards and documentation tools designed for nursing workflows
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="bg-gradient-to-br from-blue-50 to-white p-8 rounded-2xl border border-blue-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-file-medical text-white text-xl"></i>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Clinical Documentation</h3>
              <p className="text-gray-600 mb-4">
                SBAR reports, SOAP notes, shift handoffs, and care plans with AI-powered assistance.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li><i className="fas fa-check text-green-500 mr-2"></i>Guided wizards</li>
                <li><i className="fas fa-check text-green-500 mr-2"></i>Evidence-based templates</li>
                <li><i className="fas fa-check text-green-500 mr-2"></i>Instant generation</li>
              </ul>
            </div>

            {/* Feature 2 */}
            <div className="bg-gradient-to-br from-purple-50 to-white p-8 rounded-2xl border border-purple-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-secondary-500 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-pills text-white text-xl"></i>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Medication Safety</h3>
              <p className="text-gray-600 mb-4">
                Drug interaction checking, dosage calculations, and medication reconciliation tools.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li><i className="fas fa-check text-green-500 mr-2"></i>500+ medications</li>
                <li><i className="fas fa-check text-green-500 mr-2"></i>Real-time checking</li>
                <li><i className="fas fa-check text-green-500 mr-2"></i>Always free</li>
              </ul>
            </div>

            {/* Feature 3 */}
            <div className="bg-gradient-to-br from-green-50 to-white p-8 rounded-2xl border border-green-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-accent-500 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-user-nurse text-white text-xl"></i>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Patient Education</h3>
              <p className="text-gray-600 mb-4">
                Generate discharge instructions, medication guides, and patient education materials.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li><i className="fas fa-check text-green-500 mr-2"></i>Patient-friendly language</li>
                <li><i className="fas fa-check text-green-500 mr-2"></i>Customizable content</li>
                <li><i className="fas fa-check text-green-500 mr-2"></i>Print ready</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Drug Checker Highlight */}
      <section className="py-20 bg-gradient-to-br from-blue-600 to-purple-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <div className="inline-block p-4 bg-white bg-opacity-20 rounded-full mb-6">
              <i className="fas fa-pills text-5xl"></i>
            </div>
            <h2 className="text-4xl font-bold mb-4">Free Drug Interaction Checker</h2>
            <p className="text-xl mb-8 text-blue-100">
              When the NIH Drug Interaction API was discontinued, we stepped up.
              Check medication interactions instantly—no login required.
            </p>
            <div className="flex flex-wrap gap-6 justify-center mb-8">
              <div className="text-center">
                <div className="text-3xl font-bold">500+</div>
                <div className="text-blue-100">Medications</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">100%</div>
                <div className="text-blue-100">Free</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">0</div>
                <div className="text-blue-100">Data Stored</div>
              </div>
            </div>
            <a
              href="/drug-checker"
              className="inline-block px-8 py-4 bg-white text-blue-600 text-lg font-semibold rounded-lg hover:bg-gray-100 transition-colors shadow-lg"
            >
              <i className="fas fa-arrow-right mr-2"></i>
              Start Checking Now
            </a>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Built for Every Care Setting
            </h2>
            <p className="text-xl text-gray-600">
              From ICU to home health, our tools adapt to your workflow
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-xl border border-gray-200 text-center hover:shadow-md transition-shadow">
              <i className="fas fa-hospital text-blue-600 text-3xl mb-3"></i>
              <h3 className="font-bold text-gray-900 mb-2">Med-Surg</h3>
              <p className="text-sm text-gray-600">Multi-patient management</p>
            </div>
            <div className="bg-white p-6 rounded-xl border border-gray-200 text-center hover:shadow-md transition-shadow">
              <i className="fas fa-heartbeat text-red-600 text-3xl mb-3"></i>
              <h3 className="font-bold text-gray-900 mb-2">ICU/Critical Care</h3>
              <p className="text-sm text-gray-600">Complex assessments</p>
            </div>
            <div className="bg-white p-6 rounded-xl border border-gray-200 text-center hover:shadow-md transition-shadow">
              <i className="fas fa-ambulance text-orange-600 text-3xl mb-3"></i>
              <h3 className="font-bold text-gray-900 mb-2">Emergency</h3>
              <p className="text-sm text-gray-600">Fast documentation</p>
            </div>
            <div className="bg-white p-6 rounded-xl border border-gray-200 text-center hover:shadow-md transition-shadow">
              <i className="fas fa-home text-green-600 text-3xl mb-3"></i>
              <h3 className="font-bold text-gray-900 mb-2">Home Health</h3>
              <p className="text-sm text-gray-600">Remote care support</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Ready to Transform Your Workflow?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Join nurses using AI Nurse Florence to save time and improve patient outcomes.
          </p>
          <a
            href="/app"
            className="inline-block px-10 py-5 bg-primary-600 text-white text-xl font-bold rounded-lg hover:bg-primary-700 transition-colors shadow-xl"
          >
            <i className="fas fa-heart-pulse mr-3"></i>
            Start Using Florence Today
          </a>
          <p className="text-sm text-gray-500 mt-4">No credit card required • Free to start</p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            <div>
              <div className="flex items-center mb-4">
                <i className="fas fa-heart-pulse text-secondary-500 text-2xl mr-3"></i>
                <span className="text-xl font-bold">AI Nurse Florence</span>
              </div>
              <p className="text-gray-400">
                Clinical decision support tools designed to help nurses deliver exceptional patient care.
              </p>
            </div>
            <div>
              <h3 className="font-bold mb-4">Tools</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="/drug-checker" className="hover:text-white transition-colors">Drug Interaction Checker</a></li>
                <li><a href="/app" className="hover:text-white transition-colors">Clinical Wizards</a></li>
                <li><a href="/app" className="hover:text-white transition-colors">Documentation Tools</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-bold mb-4">Mission</h3>
              <p className="text-gray-400 text-sm">
                Serving the healthcare community with accessible, evidence-based clinical tools
                that help nurses work more efficiently and safely.
              </p>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-gray-400 text-sm">
            <p className="mb-2">
              &copy; 2025 AI Nurse Florence. Educational use only - not medical advice.
            </p>
            <p className="text-xs text-gray-500">
              Always consult your healthcare provider about your medications and health concerns.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
