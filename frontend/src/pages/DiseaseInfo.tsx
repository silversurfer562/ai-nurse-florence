import { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { diseaseService } from '../services/api';
import DiseaseAutocomplete from '../components/DiseaseAutocomplete';

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
            <label className="block text-gray-700 font-medium mb-2">
              {t('diseaseInfo.subtitle')}
            </label>
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
        <div className="card">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">{data.query}</h2>

          {data.summary && (
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Summary</h3>
              <p className="text-gray-700">{data.summary}</p>
            </div>
          )}

          {data.description && (
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Description</h3>
              <p className="text-gray-700">{data.description}</p>
            </div>
          )}

          {data.symptoms && data.symptoms.length > 0 && (
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Symptoms</h3>
              <ul className="list-disc list-inside space-y-1">
                {data.symptoms.map((symptom: string, index: number) => (
                  <li key={index} className="text-gray-700">{symptom}</li>
                ))}
              </ul>
            </div>
          )}

          {data.related_articles && data.related_articles.length > 0 && (
            <div className="mb-4">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">
                <i className="fas fa-book-medical mr-2"></i>
                Related Research Articles
              </h3>
              <div className="space-y-4">
                {data.related_articles.map((article: any, index: number) => (
                  <div key={article.pmid} className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-semibold text-gray-800 flex-1">
                        {index + 1}. {article.title}
                      </h4>
                    </div>
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

          {data.sources && (
            <div className="mt-4 pt-4 border-t">
              <p className="text-sm text-gray-600">
                <span className="font-medium">Sources:</span> {data.sources.join(', ')}
              </p>
            </div>
          )}

          {data.banner && (
            <div className="mt-4 bg-gray-100 border border-gray-300 text-gray-700 px-4 py-3 rounded-lg text-sm">
              <i className="fas fa-info-circle mr-2"></i>
              {data.banner}
            </div>
          )}
        </div>
      )}
    </div>
  );
}