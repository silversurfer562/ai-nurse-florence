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
      bgColor: 'bg-primary-100',
      iconColor: 'text-primary-600',
      path: '/app/patient-education',
    },
    {
      title: t('dashboard.drugInteractions.title'),
      description: t('dashboard.drugInteractions.description'),
      action: t('dashboard.drugInteractions.action'),
      icon: 'fa-pills',
      bgColor: 'bg-secondary-100',
      iconColor: 'text-secondary-600',
      path: '/app/drug-interactions',
    },
    {
      title: t('clinicalTrials.title'),
      description: t('clinicalTrials.subtitle'),
      action: t('clinicalTrials.searchSection.searchButton'),
      icon: 'fa-flask',
      bgColor: 'bg-accent-100',
      iconColor: 'text-accent-600',
      path: '/app/clinical-trials',
    },
    {
      title: t('diseaseInfo.title'),
      description: t('diseaseInfo.subtitle'),
      action: t('diseaseInfo.searchButton'),
      icon: 'fa-stethoscope',
      bgColor: 'bg-success-100',
      iconColor: 'text-success-600',
      path: '/app/disease-info',
    },
  ];

  return (
    <div>
      {/* Quick Access Cards - 4 Primary Features */}
      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {quickAccessCards.map((card) => (
          <Link
            key={card.path}
            to={card.path}
            className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200"
          >
            <div className={`${card.bgColor} w-12 h-12 rounded-lg flex items-center justify-center mb-4`}>
              <i className={`fas ${card.icon} ${card.iconColor} text-2xl`}></i>
            </div>
            <h3 className="text-lg font-bold text-gray-800 mb-2">{card.title}</h3>
            <p className="text-gray-600 text-sm">{card.description}</p>
            <div className="mt-4 flex items-center text-primary-600 font-medium text-sm">
              <span>{card.action}</span>
              <i className="fas fa-arrow-right ml-2"></i>
            </div>
          </Link>
        ))}
      </div>

      {/* Clinical Documentation Section */}
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-800 mb-4">
          <i className="fas fa-clipboard-list text-primary-600 mr-2"></i>
          Clinical Documentation
        </h2>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Link
            to="/app/sbar-report"
            className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-all duration-200 border-l-4 border-primary-500"
          >
            <div className="flex items-center space-x-3">
              <i className="fas fa-comments text-primary-600 text-xl"></i>
              <div>
                <h3 className="font-semibold text-gray-800">SBAR Report</h3>
                <p className="text-xs text-gray-500">Situation-Background-Assessment-Recommendation</p>
              </div>
            </div>
          </Link>

          <Link
            to="/app/discharge-instructions"
            className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-all duration-200 border-l-4 border-secondary-500"
          >
            <div className="flex items-center space-x-3">
              <i className="fas fa-sign-out-alt text-secondary-600 text-xl"></i>
              <div>
                <h3 className="font-semibold text-gray-800">Discharge Instructions</h3>
                <p className="text-xs text-gray-500">Patient discharge planning and instructions</p>
              </div>
            </div>
          </Link>

          <Link
            to="/app/medication-guide"
            className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-all duration-200 border-l-4 border-accent-500"
          >
            <div className="flex items-center space-x-3">
              <i className="fas fa-prescription-bottle text-accent-600 text-xl"></i>
              <div>
                <h3 className="font-semibold text-gray-800">Medication Guide</h3>
                <p className="text-xs text-gray-500">Patient medication information sheets</p>
              </div>
            </div>
          </Link>

          <Link
            to="/app/incident-report"
            className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-all duration-200 border-l-4 border-success-500"
          >
            <div className="flex items-center space-x-3">
              <i className="fas fa-exclamation-triangle text-success-600 text-xl"></i>
              <div>
                <h3 className="font-semibold text-gray-800">Incident Report</h3>
                <p className="text-xs text-gray-500">Safety event documentation</p>
              </div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}