import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { literatureService } from '../services/api';

export default function LiteratureSearch() {
  const [searchQuery, setSearchQuery] = useState('');
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(10);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['literature', query, maxResults],
    queryFn: () => literatureService.search(query, maxResults),
    enabled: false,
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setQuery(searchQuery);
      refetch();
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Medical Literature Search</h1>

      {/* Search Form */}
      <div className="card mb-6">
        <form onSubmit={handleSearch}>
          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">
              Search PubMed Literature
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g., diabetes treatment, hypertension guidelines"
              className="input-field w-full"
              required
            />
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
                Searching...
              </>
            ) : (
              <>
                <i className="fas fa-search mr-2"></i>
                Search Literature
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
            {data.articles?.map((article: any) => (
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