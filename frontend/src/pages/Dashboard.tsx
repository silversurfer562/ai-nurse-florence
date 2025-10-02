import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

export default function Dashboard() {
  const { t } = useTranslation();

  const quickAccessCards = [
    {
      title: t('dashboard.patientEducation.title'),
      description: t('dashboard.patientEducation.description'),
      action: t('dashboard.patientEducation.action'),
      icon: 'fa-file-medical',
      color: 'blue',
      path: '/patient-education',
    },
    {
      title: t('dashboard.drugInteractions.title'),
      description: t('dashboard.drugInteractions.description'),
      action: t('dashboard.drugInteractions.action'),
      icon: 'fa-pills',
      color: 'red',
      path: '/drug-interactions',
    },
    {
      title: 'Clinical Trials',
      description: 'Find relevant clinical trials for patient conditions',
      action: 'Search',
      icon: 'fa-flask',
      color: 'purple',
      path: '/clinical-trials',
    },
    {
      title: 'Disease Information',
      description: 'Evidence-based disease information and clinical guidelines',
      action: 'Learn',
      icon: 'fa-stethoscope',
      color: 'green',
      path: '/disease-info',
    },
  ];

  return (
    <div>
      {/* Compliance Notice */}
      <div className="bg-blue-600 rounded-xl shadow-lg text-white p-6 mb-6">
        <div className="flex items-start space-x-3">
          <i className="fas fa-shield-alt text-blue-200 mt-1 text-xl"></i>
          <div className="text-sm">
            <p className="font-semibold text-blue-100 mb-1">{t('dashboard.complianceNotice.title')}</p>
            <p className="text-blue-200">
              {t('dashboard.complianceNotice.text')}
            </p>
          </div>
        </div>
      </div>

      {/* Quick Access Cards - 4 Primary Features */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
              <span>{card.action}</span>
              <i className="fas fa-arrow-right ml-2"></i>
            </div>
          </Link>
        ))}
      </div>

      {/* Clinical Documentation Section */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          <i className="fas fa-clipboard-list text-blue-600 mr-2"></i>
          Clinical Documentation
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/sbar-report"
            className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-all duration-200 border-l-4 border-blue-500"
          >
            <div className="flex items-center space-x-3">
              <i className="fas fa-comments text-blue-600 text-xl"></i>
              <div>
                <h3 className="font-semibold text-gray-800">SBAR Report</h3>
                <p className="text-xs text-gray-500">Situation-Background-Assessment-Recommendation</p>
              </div>
            </div>
          </Link>

          <Link
            to="/discharge-instructions"
            className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-all duration-200 border-l-4 border-green-500"
          >
            <div className="flex items-center space-x-3">
              <i className="fas fa-sign-out-alt text-green-600 text-xl"></i>
              <div>
                <h3 className="font-semibold text-gray-800">Discharge Instructions</h3>
                <p className="text-xs text-gray-500">Patient discharge planning and instructions</p>
              </div>
            </div>
          </Link>

          <Link
            to="/medication-guide"
            className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-all duration-200 border-l-4 border-purple-500"
          >
            <div className="flex items-center space-x-3">
              <i className="fas fa-prescription-bottle text-purple-600 text-xl"></i>
              <div>
                <h3 className="font-semibold text-gray-800">Medication Guide</h3>
                <p className="text-xs text-gray-500">Patient medication information sheets</p>
              </div>
            </div>
          </Link>

          <Link
            to="/incident-report"
            className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-all duration-200 border-l-4 border-red-500"
          >
            <div className="flex items-center space-x-3">
              <i className="fas fa-exclamation-triangle text-red-600 text-xl"></i>
              <div>
                <h3 className="font-semibold text-gray-800">Incident Report</h3>
                <p className="text-xs text-gray-500">Safety event documentation</p>
              </div>
            </div>
          </Link>
        </div>
      </div>

      {/* Stats/Info Section */}
      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-green-100 p-3 rounded-lg">
              <i className="fas fa-database text-green-600 text-2xl"></i>
            </div>
            <div>
              <p className="text-sm text-gray-600">{t('dashboard.stats.dataSources.label')}</p>
              <p className="text-2xl font-bold text-gray-800">{t('dashboard.stats.dataSources.value')}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-blue-100 p-3 rounded-lg">
              <i className="fas fa-book-medical text-blue-600 text-2xl"></i>
            </div>
            <div>
              <p className="text-sm text-gray-600">{t('dashboard.stats.pubmedArticles.label')}</p>
              <p className="text-2xl font-bold text-gray-800">{t('dashboard.stats.pubmedArticles.value')}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6">
          <div className="flex items-center space-x-4">
            <div className="bg-purple-100 p-3 rounded-lg">
              <i className="fas fa-check-circle text-purple-600 text-2xl"></i>
            </div>
            <div>
              <p className="text-sm text-gray-600">{t('dashboard.stats.systemStatus.label')}</p>
              <p className="text-2xl font-bold text-green-600">{t('dashboard.stats.systemStatus.healthy')}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}