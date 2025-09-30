import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { clinicalTrialsService } from '../services/api';

export default function ClinicalTrials() {
  const [searchQuery, setSearchQuery] = useState('');
  const [condition, setCondition] = useState('');
  const [maxStudies, setMaxStudies] = useState(10);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['clinical-trials', condition, maxStudies],
    queryFn: () => clinicalTrialsService.search(condition, maxStudies),
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
      <h1 className="text-3xl font-bold text-gray-800 mb-6">Clinical Trials Search</h1>

      {/* Search Form */}
      <div className="card mb-6">
        <form onSubmit={handleSearch}>
          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">
              Search by Condition
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g., diabetes, cancer, hypertension"
              className="input-field w-full"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">
              Maximum Results: {maxStudies}
            </label>
            <input
              type="range"
              min="5"
              max="50"
              value={maxStudies}
              onChange={(e) => setMaxStudies(Number(e.target.value))}
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
                Search Clinical Trials
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
            {data.studies_summary || `Found ${data.total_studies} trials`}
          </div>

          <div className="space-y-4">
            {data.trials?.map((trial: any) => (
              <div key={trial.nct_id} className="card">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-bold text-gray-800 flex-1">{trial.title}</h3>
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium ml-4">
                    {trial.nct_id}
                  </span>
                </div>

                <div className="grid md:grid-cols-3 gap-4 mb-3">
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Phase</p>
                    <p className="text-sm font-medium text-gray-800">{trial.phase || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Status</p>
                    <p className="text-sm font-medium text-gray-800">{trial.status}</p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 uppercase tracking-wide">Type</p>
                    <p className="text-sm font-medium text-gray-800">{trial.study_type}</p>
                  </div>
                </div>

                {trial.condition && (
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Condition:</span> {trial.condition}
                  </p>
                )}

                {trial.brief_summary && (
                  <p className="text-sm text-gray-600 mt-2 line-clamp-3">{trial.brief_summary}</p>
                )}

                <a
                  href={`https://clinicaltrials.gov/study/${trial.nct_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 font-medium text-sm mt-3 inline-block"
                >
                  View on ClinicalTrials.gov <i className="fas fa-external-link-alt ml-1"></i>
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