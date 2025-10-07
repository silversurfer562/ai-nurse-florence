/**
 * About Us Page
 * Our story, mission, and commitment to public health
 */
export default function AboutUs() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <a href="/" className="flex items-center">
                <i className="fas fa-heart-pulse text-secondary-500 text-2xl mr-3"></i>
                <span className="text-xl font-bold text-gray-900">AI Nurse Florence</span>
              </a>
            </div>
            <div className="flex items-center gap-4">
              <a href="/" className="text-gray-600 hover:text-primary-600 transition-colors">
                Home
              </a>
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
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            About AI Nurse Florence
          </h1>
          <p className="text-2xl text-gray-600">
            Serving the healthcare community through accessible, evidence-based clinical tools
          </p>
        </div>
      </section>

      {/* Our Story */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Our Story</h2>
            <div className="space-y-6 text-lg text-gray-700">
              <p>
                AI Nurse Florence was created to provide comprehensive clinical decision support for nursing professionals.
                We built a platform with three core capabilities: <strong>advanced clinical documentation wizards</strong>,
                <strong>sophisticated drug interaction and medication safety tools</strong>, and <strong>comprehensive
                research features</strong> including literature search, clinical trials database, and medical references.
              </p>
              <p>
                Our drug interaction system was designed to go far beyond basic checking—it analyzes severity, provides
                clinical context, and integrates with our documentation tools. Our research features give nurses instant
                access to evidence-based information. Our documentation wizards use AI to help create SBAR reports, SOAP
                notes, care plans, and more in minutes instead of hours.
              </p>
              <p>
                We were refining these advanced features for healthcare institutions when the National Institutes of Health
                (NIH) discontinued its Drug Interaction API. Overnight, patients, caregivers, and the public lost access
                to a critical resource. We weren't ready to launch publicly, but we couldn't stand by.
              </p>
              <p>
                So we deployed our <strong>more advanced drug interaction checker</strong> as a free public service—no login,
                no data storage, just better drug checking than what was lost. We didn't just fill the gap; we exceeded it
                with more comprehensive interaction analysis and clearer clinical guidance.
              </p>
              <p>
                That decision defined who we are. We're building advanced clinical tools—documentation wizards, research
                capabilities, and medication safety features—for healthcare institutions. But we're also committed to public
                health. Our drug interaction checker remains free because critical health information should be accessible to
                everyone, not just those with institutional access. The advanced features? Those help nurses deliver better care.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Mission & Values */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-12 text-center">Our Mission & Values</h2>

          <div className="grid md:grid-cols-2 gap-8 mb-12">
            {/* Mission */}
            <div className="bg-white p-8 rounded-xl border border-gray-200">
              <div className="w-12 h-12 bg-primary-600 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-bullseye text-white text-2xl"></i>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Our Mission</h3>
              <p className="text-gray-700">
                To empower nurses with AI-powered clinical decision support tools that help them
                work more efficiently, make confident decisions, and deliver exceptional patient care.
              </p>
            </div>

            {/* Public Health Commitment */}
            <div className="bg-white p-8 rounded-xl border border-gray-200">
              <div className="w-12 h-12 bg-secondary-500 rounded-lg flex items-center justify-center mb-4">
                <i className="fas fa-users text-white text-2xl"></i>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Public Health First</h3>
              <p className="text-gray-700">
                We believe healthcare technology should serve the public good. That's why we maintain
                free tools like our drug interaction checker—accessible to everyone, always.
              </p>
            </div>
          </div>

          {/* Core Values */}
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8 border border-blue-100">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Core Values</h3>
            <div className="grid md:grid-cols-3 gap-6">
              <div>
                <h4 className="font-bold text-gray-900 mb-2 flex items-center">
                  <i className="fas fa-shield-alt text-primary-600 mr-2"></i>
                  Evidence-Based
                </h4>
                <p className="text-sm text-gray-700">
                  Every feature is grounded in nursing best practices and clinical guidelines.
                </p>
              </div>
              <div>
                <h4 className="font-bold text-gray-900 mb-2 flex items-center">
                  <i className="fas fa-heart text-secondary-500 mr-2"></i>
                  User-Centered
                </h4>
                <p className="text-sm text-gray-700">
                  Built for nurses, by listening to nurses, and continuously refined based on real-world needs.
                </p>
              </div>
              <div>
                <h4 className="font-bold text-gray-900 mb-2 flex items-center">
                  <i className="fas fa-lock text-accent-500 mr-2"></i>
                  Privacy-First
                </h4>
                <p className="text-sm text-gray-700">
                  Your clinical documentation is yours. We prioritize data privacy and security in everything we build.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Why We Built This */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-8">Why We Built This</h2>
          <div className="space-y-6 text-lg text-gray-700">
            <p>
              Nurses are the backbone of our healthcare system. They're the ones at the bedside,
              managing complex patient loads, coordinating care, and making critical decisions
              every single day.
            </p>
            <p>
              Yet too often, the technology available to nurses feels like it was designed for
              administrators or billing departments—not for the people actually delivering care.
              Documentation becomes a burden instead of a tool. Critical information gets buried
              in clunky interfaces. Time that should be spent with patients gets consumed by
              inefficient workflows.
            </p>
            <p>
              We built AI Nurse Florence to change that. Every feature is designed with one question
              in mind: <strong>Will this help a nurse deliver better patient care?</strong>
            </p>
            <p>
              From SBAR reports to medication reconciliation, from shift handoffs to discharge planning—we're
              creating tools that fit naturally into nursing workflows, not the other way around.
            </p>
          </div>
        </div>
      </section>

      {/* Our Commitment */}
      <section className="py-16 bg-primary-600 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-6">Our Commitment to You</h2>
          <div className="grid md:grid-cols-3 gap-8 text-left">
            <div>
              <i className="fas fa-check-circle text-4xl mb-4 block"></i>
              <h3 className="font-bold text-xl mb-2">Always Improving</h3>
              <p className="text-blue-100">
                We continuously update our tools based on user feedback and emerging best practices.
              </p>
            </div>
            <div>
              <i className="fas fa-comments text-4xl mb-4 block"></i>
              <h3 className="font-bold text-xl mb-2">Responsive Support</h3>
              <p className="text-blue-100">
                We listen to our users and respond quickly to questions, concerns, and suggestions.
              </p>
            </div>
            <div>
              <i className="fas fa-globe text-4xl mb-4 block"></i>
              <h3 className="font-bold text-xl mb-2">Public Health Focus</h3>
              <p className="text-blue-100">
                Key tools like our drug checker remain free for the public good.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">
            Join Us in Serving Healthcare
          </h2>
          <p className="text-xl text-gray-600 mb-8">
            Whether you're a nurse looking for better tools or someone who needs our free
            drug interaction checker, we're here to help.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="/app"
              className="px-8 py-4 bg-primary-600 text-white text-lg font-semibold rounded-lg hover:bg-primary-700 transition-colors shadow-lg"
            >
              <i className="fas fa-rocket mr-2"></i>
              Get Started
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
