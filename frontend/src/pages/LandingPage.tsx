/**
 * AI Nurse Florence Landing Page
 * Modern clinical decision support platform for nursing professionals
 */
import { useState, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Close mobile menu on escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMobileMenuOpen(false);
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, []);

  // Prevent body scroll when mobile menu is open
  useEffect(() => {
    if (mobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
  }, [mobileMenuOpen]);

  return (
    <div className="min-h-screen bg-white">
      {/* SEO Meta Tags */}
      <Helmet>
        <title>AI Nurse Florence - Clinical Decision Support Built for Nurses</title>
        <meta
          name="description"
          content="AI-powered clinical documentation wizards, free drug interaction checker, and evidence-based decision support tools designed for nursing professionals. No login required."
        />
        <meta property="og:title" content="AI Nurse Florence - Clinical Decision Support Built for Nurses" />
        <meta property="og:description" content="AI-powered clinical documentation wizards, free drug interaction checker, and evidence-based decision support tools designed for nursing professionals." />
        <meta property="og:type" content="website" />
        <meta property="og:image" content="/og-image.png" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="AI Nurse Florence - Clinical Decision Support Built for Nurses" />
        <meta name="twitter:description" content="Free drug interaction checker and AI-powered clinical documentation tools for nurses" />
      </Helmet>

      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <i className="fas fa-heart-pulse text-secondary-500 text-2xl mr-3"></i>
              <span className="text-xl font-bold text-gray-900">AI Nurse Florence</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-4">
              <a href="/about" className="text-gray-600 hover:text-primary-600 transition-colors">
                About
              </a>
              <a href="/drug-checker" className="text-gray-600 hover:text-primary-600 transition-colors">
                Drug Checker
              </a>
              <a
                href="/app"
                className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
              >
                Try Free
              </a>
            </div>

            {/* Mobile Menu Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
              aria-label="Toggle menu"
              aria-expanded={mobileMenuOpen}
            >
              <i className={`fas ${mobileMenuOpen ? 'fa-times' : 'fa-bars'} text-xl`}></i>
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <div className="px-4 py-4 space-y-3">
              <a
                href="/about"
                className="block px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                About
              </a>
              <a
                href="/drug-checker"
                className="block px-4 py-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Drug Checker
              </a>
              <a
                href="/app"
                className="block px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors text-center"
                onClick={() => setMobileMenuOpen(false)}
              >
                Try Free
              </a>
            </div>
          </div>
        )}
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
              Provide better patient care while improving compliance with regulatory and legal requirements—in a fraction of the time.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="/app"
                className="px-8 py-4 bg-primary-600 text-white text-lg font-semibold rounded-lg hover:bg-primary-700 transition-colors shadow-lg"
              >
                <i className="fas fa-rocket mr-2"></i>
                Try Free - No Login Required
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
                Complete compliant SBAR reports, discharge instructions, and incident reports in minutes, not hours.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li><i className="fas fa-check text-green-500 mr-2"></i>Regulatory compliant</li>
                <li><i className="fas fa-check text-green-500 mr-2"></i>Evidence-based templates</li>
                <li><i className="fas fa-check text-green-500 mr-2"></i>90% time savings</li>
              </ul>
            </div>

            {/* Feature 2 */}
            <div className="bg-gradient-to-br from-purple-50 to-white p-8 rounded-2xl border border-purple-100 hover:shadow-lg transition-shadow">
              <div className="w-12 h-12 bg-secondary-500 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-pills text-white text-xl"></i>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Medication Safety</h3>
              <p className="text-gray-600 mb-4">
                Drug interaction checking powered by FDA and authoritative medical data sources.
              </p>
              <ul className="text-sm text-gray-600 space-y-2">
                <li><i className="fas fa-check text-green-500 mr-2"></i>25,000+ FDA-sourced medications</li>
                <li><i className="fas fa-check text-green-500 mr-2"></i>Real-time checking</li>
                <li><i className="fas fa-check text-green-500 mr-2"></i>Free public service</li>
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
              Check medication interactions instantly using FDA and authoritative medical data—no login required.
            </p>
            <div className="flex flex-wrap gap-6 justify-center mb-8">
              <div className="text-center">
                <div className="text-3xl font-bold">25,000+</div>
                <div className="text-blue-100">FDA Medications</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold">100%</div>
                <div className="text-blue-100">Public Service</div>
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

      {/* Our Story */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Our Story
            </h2>
            <p className="text-xl text-gray-600">
              Born from a commitment to public health and accessible healthcare technology
            </p>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8 md:p-12 border border-blue-100">
            <div className="prose prose-lg max-w-none">
              <p className="text-gray-700 mb-4">
                When the NIH discontinued its Drug Interaction API, we were building advanced clinical tools for healthcare
                institutions—comprehensive documentation wizards, research features, and medication safety systems powered by
                FDA and authoritative medical data sources, far beyond what the public API offered.
              </p>
              <p className="text-gray-700 mb-4">
                We weren't ready to launch publicly, but we couldn't stand by while patients and healthcare consumers lost
                access to drug interaction checking. So we deployed our <strong>more advanced drug checker</strong>—built on
                FDA-sourced medication data and evidence-based interaction databases—as a free public service. No login required.
                No data stored. Just authoritative drug interaction checking for everyone.
              </p>
              <p className="text-gray-700 mb-4">
                That free tool is just the beginning. Our platform integrates data from the FDA, NIH, PubMed, and other trusted
                medical authorities to provide AI-powered clinical documentation, comprehensive research capabilities, and
                evidence-based decision support—all designed to help nursing professionals deliver exceptional care. The drug
                checker remains free because we believe critical health information from authoritative sources should be
                accessible to all, not just those with institutional access.
              </p>
              <p className="text-gray-700 font-semibold">
                <a href="/about" className="text-primary-600 hover:text-primary-700 underline">
                  Read our full story →
                </a>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            Ready to Transform Your Workflow?
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Deliver better patient care, improve regulatory compliance, and reduce documentation time by 90%. Try our full platform now—no signup required.
          </p>
          <a
            href="/app"
            className="inline-block px-10 py-5 bg-primary-600 text-white text-xl font-bold rounded-lg hover:bg-primary-700 transition-colors shadow-xl"
          >
            <i className="fas fa-heart-pulse mr-3"></i>
            Try Free Now
          </a>
          <p className="text-sm text-gray-500 mt-4">Full access • No login required • Test all features</p>
        </div>
      </section>

      {/* Contact Section */}
      <section className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Interested in Enterprise Deployment?
            </h2>
            <p className="text-xl text-gray-600">
              Contact us to discuss how AI Nurse Florence can serve your hospital or healthcare institution
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Contact Info */}
            <div className="bg-gradient-to-br from-primary-50 to-white p-8 rounded-2xl border border-primary-100">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">Get in Touch</h3>
              <div className="space-y-4">
                <div className="flex items-start">
                  <i className="fas fa-hospital text-primary-600 text-xl mr-4 mt-1"></i>
                  <div>
                    <h4 className="font-bold text-gray-900 mb-1">For Hospitals & Health Systems</h4>
                    <p className="text-gray-600">
                      Learn about enterprise licensing, integration options, and custom features
                      for your organization.
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <i className="fas fa-user-md text-primary-600 text-xl mr-4 mt-1"></i>
                  <div>
                    <h4 className="font-bold text-gray-900 mb-1">For Healthcare Professionals</h4>
                    <p className="text-gray-600">
                      Questions about features, workflows, or how AI Nurse Florence can
                      fit into your practice? We're here to help.
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <i className="fas fa-lightbulb text-primary-600 text-xl mr-4 mt-1"></i>
                  <div>
                    <h4 className="font-bold text-gray-900 mb-1">Feedback & Suggestions</h4>
                    <p className="text-gray-600">
                      We're continuously improving. Share your ideas for new features or
                      enhancements.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Contact Form */}
            <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-lg">
              <div className="space-y-6">
                <div className="text-center">
                  <i className="fas fa-envelope text-primary-600 text-5xl mb-4"></i>
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">Email Us Directly</h3>
                  <p className="text-gray-600 mb-6">
                    The fastest way to reach our team
                  </p>
                  <a
                    href="mailto:support@deepstudyai.com?subject=AI%20Nurse%20Florence%20Inquiry"
                    className="inline-block px-8 py-4 bg-primary-600 text-white text-lg font-semibold rounded-lg hover:bg-primary-700 transition-colors shadow-md"
                  >
                    <i className="fas fa-paper-plane mr-2"></i>
                    support@deepstudyai.com
                  </a>
                </div>

                <div className="border-t border-gray-200 pt-6">
                  <p className="text-sm text-gray-600 text-center">
                    When contacting us, please include:
                  </p>
                  <ul className="mt-3 space-y-2 text-sm text-gray-600">
                    <li className="flex items-start">
                      <i className="fas fa-check text-green-500 mr-2 mt-1"></i>
                      Your name and role
                    </li>
                    <li className="flex items-start">
                      <i className="fas fa-check text-green-500 mr-2 mt-1"></i>
                      Organization/hospital name
                    </li>
                    <li className="flex items-start">
                      <i className="fas fa-check text-green-500 mr-2 mt-1"></i>
                      What you'd like to discuss
                    </li>
                  </ul>
                  <p className="mt-4 text-sm text-gray-500 text-center italic">
                    We typically respond within 1 business day
                  </p>
                </div>
              </div>
            </div>
          </div>
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
              <h3 className="font-bold mb-4">Company</h3>
              <ul className="space-y-2 text-gray-400">
                <li><a href="/about" className="hover:text-white transition-colors">About Us</a></li>
                <li><a href="/" className="hover:text-white transition-colors">Home</a></li>
              </ul>
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
