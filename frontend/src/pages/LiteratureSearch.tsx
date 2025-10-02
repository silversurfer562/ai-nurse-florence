import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { literatureService } from '../services/api';
import VoiceDictation from '../components/VoiceDictation';
import { LiveRegion } from '../components/ScreenReaderOnly';

export default function LiteratureSearch() {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);
  const [announceMessage, setAnnounceMessage] = useState('');
  const [displayCount, setDisplayCount] = useState(3); // Show 3 articles initially

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['literature', query, maxResults],
    queryFn: () => literatureService.search(query, maxResults),
    enabled: false,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setQuery(searchQuery);
      setDisplayCount(3); // Reset to 3 articles on new search
      setAnnounceMessage(`Searching for "${searchQuery}"...`);
      refetch();
    }
  };

  const handleLoadMore = () => {
    setDisplayCount(prev => prev + 5); // Show 5 more articles
    setAnnounceMessage(`Loading 5 more articles...`);
  };

  const handleVoiceTranscript = (transcript: string) => {
    setSearchQuery(prev => prev + ' ' + transcript);
  };

  return (
    <div>
      {/* Live Region for Screen Reader Announcements */}
      <LiveRegion>{announceMessage}</LiveRegion>

      <h1 className="text-3xl font-bold text-gray-800 mb-6">{t('literatureSearch.title')}</h1>

      {/* Search Form */}
      <div className="card mb-6" role="search" aria-label="Literature search">
        <form onSubmit={handleSearch}>
          <div className="mb-4">
            <label htmlFor="literature-search" className="block text-gray-700 font-medium mb-2">
              <i className="fas fa-search mr-2" aria-hidden="true"></i>
              {t('literatureSearch.subtitle')}
            </label>
            <div className="flex gap-2">
              <input
                id="literature-search"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={t('literatureSearch.searchPlaceholder')}
                className="input-field flex-1"
                aria-describedby="search-hint"
                required
              />
              <VoiceDictation
                onTranscript={handleVoiceTranscript}
                placeholder="Use voice to search literature"
              />
            </div>
            <p id="search-hint" className="text-sm text-gray-500 mt-1">
              Type to search or use microphone for voice input
            </p>
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">
              Maximum Results: {maxResults}
            </label>
            <input
              type="range"
              min="5"
              max="50"
              value={maxResults}
              onChange={(e) => setMaxResults(Number(e.target.value))}
              className="w-full"
            />
          </div>

          <button type="submit" className="btn-primary" disabled={isLoading}>
            {isLoading ? (
              <>
                <i className="fas fa-spinner fa-spin mr-2"></i>
                {t('literatureSearch.searchButton')}...
              </>
            ) : (
              <>
                <i className="fas fa-search mr-2"></i>
                {t('literatureSearch.searchButton')}
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
        <div>
          <div className="bg-blue-100 border border-blue-400 text-blue-800 px-4 py-3 rounded-lg mb-4">
            <i className="fas fa-info-circle mr-2"></i>
            {data.results_summary || `Found ${data.total_results} articles`}
          </div>

          <div className="space-y-4">
            {data.articles?.slice(0, displayCount).map((article: any) => (
              <div key={article.pmid} className="card">
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-bold text-gray-800 flex-1">{article.title}</h3>
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium ml-4">
                    PMID: {article.pmid}
                  </span>
                </div>

                {article.authors && article.authors.length > 0 && (
                  <p className="text-sm text-gray-600 mb-2">
                    <span className="font-medium">Authors:</span> {article.authors.join(', ')}
                  </p>
                )}

                <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
                  {article.journal && (
                    <span>
                      <i className="fas fa-book mr-1"></i>
                      {article.journal}
                    </span>
                  )}
                  {article.year && (
                    <span>
                      <i className="fas fa-calendar mr-1"></i>
                      {article.year}
                    </span>
                  )}
                </div>

                {article.abstract && (
                  <p className="text-sm text-gray-700 line-clamp-3">{article.abstract}</p>
                )}

                <a
                  href={`https://pubmed.ncbi.nlm.nih.gov/${article.pmid}/`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 font-medium text-sm mt-3 inline-block"
                >
                  View on PubMed <i className="fas fa-external-link-alt ml-1"></i>
                </a>
              </div>
            ))}
          </div>

          {/* Load More Button */}
          {data.articles && data.articles.length > displayCount && (
            <div className="mt-6 text-center">
              <button
                onClick={handleLoadMore}
                className="btn-secondary px-6 py-3"
                aria-label={`Load 5 more articles. Currently showing ${displayCount} of ${data.articles.length} articles`}
              >
                <i className="fas fa-plus-circle mr-2"></i>
                Load More (5 more articles)
                <span className="ml-2 text-sm text-gray-600">
                  {displayCount} of {data.articles.length}
                </span>
              </button>
            </div>
          )}

          {/* Banner */}
          {data.banner && (
            <div className="mt-6 bg-gray-100 border border-gray-300 text-gray-700 px-4 py-3 rounded-lg text-sm">
              <i className="fas fa-info-circle mr-2"></i>
              {data.banner}
            </div>
          )}
        </div>
      )}
    </div>
  );
}