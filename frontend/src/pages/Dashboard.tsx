import { Link } from 'react-router-dom';

export default function Dashboard() {
  const quickAccessCards = [
    {
      title: 'Clinical Trials',
      description: 'Search for ongoing and completed clinical studies',
      icon: 'fa-flask',
      color: 'blue',
      path: '/clinical-trials',
    },
    {
      title: 'Disease Information',
      description: 'Look up comprehensive disease information',
      icon: 'fa-disease',
      color: 'purple',
      path: '/disease-info',
    },
    {
      title: 'Literature Search',
      description: 'Search medical literature from PubMed',
      icon: 'fa-book-medical',
      color: 'green',
      path: '/literature',
    },
    {
      title: 'Drug Interactions',
      description: 'Check medication interactions and safety',
      icon: 'fa-pills',
      color: 'red',
      path: '/drug-interactions',
    },
  ];

  return (
    <div>
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-xl shadow-lg text-white p-8 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <h2 className="text-3xl font-bold mb-2">Welcome to Your Clinical Assistant</h2>
            <p className="text-blue-100 mb-4 text-lg">
              Get evidence-based support for patient care, medication guidance, and clinical protocols
            </p>

            {/* Compliance Notice */}
            <div className="bg-blue-500/30 border border-blue-400/30 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <i className="fas fa-shield-alt text-blue-200 mt-1 text-xl"></i>
                <div className="text-sm">
                  <p className="font-semibold text-blue-100 mb-1">Clinical Decision Support Tool</p>
                  <p className="text-blue-200">
                    Educational and reference purposes only. Always follow your institution's protocols and verify all
                    clinical decisions with appropriate healthcare professionals. No PHI is stored or processed.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="hidden lg:block">
            <div className="text-right">
              <div className="bg-white/10 rounded-lg p-6 backdrop-blur">
                <div className="text-4xl font-bold mb-1">v2.1.0</div>
                <div className="text-blue-200">Evidence-Based</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Access Cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {quickAccessCards.map((card) => (
          <Link
            key={card.path}
            to={card.path}
            className={`bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200`}
          >
            <div className={`bg-${card.color}-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
              <i className={`fas ${card.icon} text-${card.color}-600 text-2xl`}></i>
            </div>
            <h3 className="text-lg font-bold text-gray-800 mb-2">{card.title}</h3>
            <p className="text-gray-600 text-sm">{card.description}</p>
            <div className="mt-4 flex items-center text-blue-600 font-medium text-sm">
              <span>Explore</span>
              <i className="fas fa-arrow-right ml-2"></i>
            </div>
          </Link>
        ))}
      </div>

      {/* Stats/Info Section */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 p-3 rounded-lg">
              <i className="fas fa-database text-green-600 text-2xl"></i>
            </div>
            <div>
              <p className="text-sm text-gray-600">Live Data Sources</p>
              <p className="text-2xl font-bold text-gray-800">4+</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <i className="fas fa-book-medical text-blue-600 text-2xl"></i>
            </div>
            <div>
              <p className="text-sm text-gray-600">PubMed Articles</p>
              <p className="text-2xl font-bold text-gray-800">35M+</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-purple-100 p-3 rounded-lg">
              <i className="fas fa-check-circle text-purple-600 text-2xl"></i>
            </div>
            <div>
              <p className="text-sm text-gray-600">System Status</p>
              <p className="text-2xl font-bold text-green-600">Healthy</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}