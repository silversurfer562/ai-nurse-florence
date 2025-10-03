import { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { diseaseService } from '../services/api';
import DiseaseAutocomplete from '../components/DiseaseAutocomplete';
import VoiceDictation from '../components/VoiceDictation';

export default function DiseaseInfo() {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [disease, setDisease] = useState('');
  const queryClient = useQueryClient();

  // Reset form and clear results when component mounts
  useEffect(() => {
    setSearchQuery('');
    setDisease('');
    queryClient.removeQueries({ queryKey: ['disease'] });
  }, [queryClient]);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['disease', disease],
    queryFn: () => diseaseService.lookup(disease),
    enabled: false,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setDisease(searchQuery);
      refetch();
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">{t('diseaseInfo.title')}</h1>

      {/* Search Form */}
      <div className="card mb-6">
        <form onSubmit={handleSearch}>
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <label className="block text-gray-700 font-medium">
                {t('diseaseInfo.subtitle')}
              </label>
              <VoiceDictation
                onTranscript={(text) => setSearchQuery(text)}
              />
            </div>
            <DiseaseAutocomplete
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder={t('diseaseInfo.searchPlaceholder')}
              className="w-full"
            />
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? (
              <>
                <i className="fas fa-spinner fa-spin mr-2"></i>
                {t('diseaseInfo.searchButton')}...
              </>
            ) : (
              <>
                <i className="fas fa-search mr-2"></i>
                {t('diseaseInfo.searchButton')}
              </>
            )}
          </button>
        </form>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-lg mb-6">
          <i className="fas fa-exclamation-circle mr-2"></i>
          Error: {(error as Error).message}
        </div>
      )}

      {/* Results */}
      {data && (
        <div className="space-y-6">
          {/* Main Disease Card */}
          <div className="card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h2 className="text-3xl font-bold text-gray-900 mb-2 capitalize">
                  {(data.disease_name || data.name || data.query).toLowerCase()}
                </h2>
                {data.disease_category && (
                  <span className="inline-block bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
                    {data.disease_category}
                  </span>
                )}
              </div>
              {data.is_rare_disease && (
                <span className="bg-purple-100 text-purple-800 text-xs font-semibold px-3 py-1 rounded-full">
                  Rare Disease
                </span>
              )}
            </div>

            {/* Description */}
            {(data.short_description || data.description || data.summary) && (
              <div className="mb-6">
                <p className="text-lg text-gray-700 leading-relaxed">
                  {data.short_description || data.description || data.summary}
                </p>
              </div>
            )}

            {/* Clinical Codes */}
            <div className="grid md:grid-cols-3 gap-4 mb-6 p-4 bg-gray-50 rounded-lg">
              {data.icd10_codes && data.icd10_codes.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">ICD-10 Code(s)</p>
                  <p className="text-lg font-semibold text-gray-900">
                    {Array.isArray(data.icd10_codes) ? data.icd10_codes.join(', ') : data.icd10_codes}
                  </p>
                </div>
              )}
              {data.snomed_code && (
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">SNOMED CT</p>
                  <p className="text-lg font-semibold text-gray-900">{data.snomed_code}</p>
                </div>
              )}
              {data.estimated_prevalence && (
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-1">Prevalence</p>
                  <p className="text-lg font-semibold text-gray-900">{data.estimated_prevalence}</p>
                </div>
              )}
            </div>

            {/* Synonyms */}
            {data.disease_synonyms && data.disease_synonyms.length > 0 && (
              <div className="mb-6 p-4 bg-blue-50 border-l-4 border-blue-500">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  <i className="fas fa-tag mr-2 text-blue-600"></i>
                  Also Known As:
                </p>
                <p className="text-gray-800">{data.disease_synonyms.join(', ')}</p>
              </div>
            )}

            {/* Symptoms */}
            {data.symptoms && data.symptoms.length > 0 && (
              <div className="mb-6">
                <h3 className="text-xl font-bold text-gray-900 mb-3 flex items-center">
                  <i className="fas fa-heartbeat mr-2 text-red-600"></i>
                  Clinical Symptoms ({data.symptoms.length})
                </h3>
                <div className="grid md:grid-cols-2 gap-3">
                  {data.symptoms.map((symptom: string, index: number) => (
                    <div key={index} className="flex items-start p-3 bg-gray-50 rounded-lg border border-gray-200">
                      <i className="fas fa-check-circle text-green-600 mt-1 mr-3 flex-shrink-0"></i>
                      <span className="text-gray-800">{symptom}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* External Resources */}
          {data.external_resources && (
            <div className="card">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <i className="fas fa-external-link-alt mr-2 text-blue-600"></i>
                External Resources
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {data.external_resources.pubmed && (
                  <a
                    href={data.external_resources.pubmed}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
                  >
                    <i className="fas fa-book-medical text-2xl text-blue-600 mr-3"></i>
                    <div>
                      <p className="font-semibold text-gray-900">PubMed Research</p>
                      <p className="text-sm text-gray-600">Search medical literature</p>
                    </div>
                  </a>
                )}
                {data.external_resources.medlineplus && (
                  <a
                    href={data.external_resources.medlineplus}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center p-4 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
                  >
                    <i className="fas fa-notes-medical text-2xl text-green-600 mr-3"></i>
                    <div>
                      <p className="font-semibold text-gray-900">MedlinePlus</p>
                      <p className="text-sm text-gray-600">Patient education</p>
                    </div>
                  </a>
                )}
                {data.external_resources.mondo && (
                  <a
                    href={data.external_resources.mondo}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center p-4 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 transition-colors"
                  >
                    <i className="fas fa-database text-2xl text-purple-600 mr-3"></i>
                    <div>
                      <p className="font-semibold text-gray-900">MONDO Database</p>
                      <p className="text-sm text-gray-600">Disease ontology</p>
                    </div>
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Related Research Articles */}
          {data.related_articles && data.related_articles.length > 0 && (
            <div className="card">
              <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                <i className="fas fa-file-medical-alt mr-2 text-blue-600"></i>
                Related Research Articles
              </h3>
              <div className="space-y-4">
                {data.related_articles.map((article: any, index: number) => (
                  <div key={article.pmid} className="border-l-4 border-blue-500 bg-blue-50 p-4 rounded-r-lg">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      {index + 1}. {article.title}
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">Authors:</span> {article.authors} |
                      <span className="font-medium ml-2">Journal:</span> {article.journal} |
                      <span className="font-medium ml-2">Published:</span> {article.pub_date}
                    </p>
                    <p className="text-sm text-gray-700 mb-3">{article.summary}</p>
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium text-sm"
                    >
                      <i className="fas fa-external-link-alt mr-1"></i>
                      View on PubMed (PMID: {article.pmid})
                    </a>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
