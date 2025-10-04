import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { clinicalTrialsService } from '../services/api';
import DiseaseAutocomplete from '../components/DiseaseAutocomplete';

export default function ClinicalTrials() {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [condition, setCondition] = useState('');
  const [status, setStatus] = useState('');
  const [maxStudies, setMaxStudies] = useState(10);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['clinical-trials', condition, maxStudies, status],
    queryFn: () => clinicalTrialsService.search(condition, maxStudies, status || undefined),
    enabled: false, // Don't auto-fetch, wait for user to click search
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setCondition(searchQuery);
      refetch();
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">{t('clinicalTrials.title')}</h1>

      {/* Search Form */}
      <div className="card mb-6" role="search" aria-label="Clinical trials search">
        <form onSubmit={handleSearch}>
          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">
              <i className="fas fa-search mr-2" aria-hidden="true"></i>
              {t('clinicalTrials.searchSection.diagnosisLabel')}
            </label>
            <DiseaseAutocomplete
              value={searchQuery}
              onChange={setSearchQuery}
              onSelect={(disease) => {
                setSearchQuery(disease);
                setCondition(disease);
                // Auto-trigger search after selection
                setTimeout(() => refetch(), 100);
              }}
              placeholder="Type the disease name (e.g., diabetes, hypertension, asthma)..."
              enableVoice={true}
            />
            <p className="text-sm text-gray-500 mt-2">
              <i className="fas fa-info-circle mr-1"></i>
              {t('clinicalTrials.searchSection.hint')}
            </p>
          </div>

          {/* Trial Status Filter */}
          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">{t('clinicalTrials.searchSection.statusLabel')}</label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">{t('clinicalTrials.searchSection.statusOptions.all')}</option>
              <option value="recruiting">{t('clinicalTrials.searchSection.statusOptions.recruiting')}</option>
              <option value="not-yet-recruiting">{t('clinicalTrials.searchSection.statusOptions.notYetRecruiting')}</option>
              <option value="active-not-recruiting">{t('clinicalTrials.searchSection.statusOptions.activeNotRecruiting')}</option>
              <option value="completed">{t('clinicalTrials.searchSection.statusOptions.completed')}</option>
            </select>
            <p className="text-sm text-gray-500 mt-1">
              <i className="fas fa-info-circle mr-1"></i>
              {t('clinicalTrials.searchSection.statusHint')}
            </p>
          </div>

          {/* Max Results Slider */}
          <div className="mb-6">
            <label className="block text-gray-700 font-medium mb-2">
              {t('clinicalTrials.searchSection.maxResultsLabel')}: {maxStudies}
            </label>
            <input
              type="range"
              min="1"
              max="50"
              value={maxStudies}
              onChange={(e) => setMaxStudies(Number(e.target.value))}
              className="w-full h-2 bg-blue-200 rounded-lg appearance-none cursor-pointer slider-thumb"
            />
          </div>

          {/* Search Button */}
          <button
            type="submit"
            disabled={!searchQuery.trim()}
            className="w-full btn-primary py-3 text-lg font-semibold"
          >
            <i className="fas fa-search mr-2"></i>
            {t('clinicalTrials.searchSection.searchButton')}
          </button>
        </form>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <i className="fas fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
          <p className="text-gray-600">{t('clinicalTrials.searching')}</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="card bg-red-50 border-l-4 border-red-500 p-4 mb-6">
          <div className="flex items-start">
            <i className="fas fa-exclamation-circle text-red-500 text-xl mr-3 mt-1"></i>
            <div>
              <p className="font-bold text-red-800">{t('clinicalTrials.error')}</p>
              <p className="text-red-700 text-sm">{(error as Error).message}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {data && data.trials && (
        <div>
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            {t('clinicalTrials.results.title')} ({data.trials.length})
          </h2>

          {data.trials.length === 0 ? (
            <div className="card text-center py-12">
              <i className="fas fa-search text-gray-300 text-5xl mb-4"></i>
              <p className="text-gray-600 text-lg">{t('clinicalTrials.results.noResults')}</p>
              <p className="text-gray-500 text-sm mt-2">{t('clinicalTrials.results.tryDifferent')}</p>
            </div>
          ) : (
            <div className="grid lg:grid-cols-2 gap-4 lg:items-start">
              {data.trials.map((study: any, index: number) => (
                <div key={index} className="card hover:shadow-lg transition-shadow h-full">
                <h3 className="text-xl font-bold text-blue-700 mb-2">{study.title || 'Untitled Study'}</h3>

                {study.status && (
                  <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold mb-3 ${
                    study.status.toLowerCase().includes('recruiting') ? 'bg-green-100 text-green-800' :
                    study.status.toLowerCase().includes('active') ? 'bg-blue-100 text-blue-800' :
                    study.status.toLowerCase().includes('completed') ? 'bg-gray-100 text-gray-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {study.status}
                  </span>
                )}

                {study.summary && (
                  <p className="text-gray-700 mb-3">{study.summary}</p>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  {study.phase && (
                    <div className="flex items-center text-gray-600">
                      <i className="fas fa-flask mr-2"></i>
                      <span><strong>Phase:</strong> {study.phase}</span>
                    </div>
                  )}
                  {study.enrollment && (
                    <div className="flex items-center text-gray-600">
                      <i className="fas fa-users mr-2"></i>
                      <span><strong>Enrollment:</strong> {study.enrollment}</span>
                    </div>
                  )}
                  {study.sponsor && (
                    <div className="flex items-center text-gray-600">
                      <i className="fas fa-building mr-2"></i>
                      <span><strong>Sponsor:</strong> {study.sponsor}</span>
                    </div>
                  )}
                  {study.nct_id && (
                    <div className="flex items-center text-gray-600">
                      <i className="fas fa-hashtag mr-2"></i>
                      <span><strong>NCT ID:</strong> {study.nct_id}</span>
                    </div>
                  )}
                </div>

                {study.contact && (
                  <div className="mt-3 p-3 bg-gray-50 rounded-lg text-sm">
                    <p className="font-semibold text-gray-700 mb-1">
                      <i className="fas fa-address-book mr-2"></i>
                      Contact Information:
                    </p>
                    <p className="text-gray-600">{study.contact.name}</p>
                    {study.contact.email && (
                      <p className="text-gray-600">
                        <i className="fas fa-envelope mr-2"></i>
                        {study.contact.email}
                      </p>
                    )}
                    {study.contact.phone && (
                      <p className="text-gray-600">
                        <i className="fas fa-phone mr-2"></i>
                        {study.contact.phone}
                      </p>
                    )}
                  </div>
                )}

                {study.url && (
                  <div className="mt-4 pt-3 border-t border-gray-200">
                    <a
                      href={study.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center"
                    >
                      <i className="fas fa-external-link-alt mr-2"></i>
                      View Full Details on ClinicalTrials.gov
                    </a>
                  </div>
                )}
              </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
