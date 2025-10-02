import { useState, useRef } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { clinicalTrialsService } from '../services/api';
import VoiceDictation from '../components/VoiceDictation';
import { LiveRegion } from '../components/ScreenReaderOnly';

interface DiagnosisOption {
  disease_id: number;
  disease_name: string;
  category: string;
}

export default function ClinicalTrials() {
  const { t } = useTranslation();
  const [searchQuery, setSearchQuery] = useState('');
  const [condition, setCondition] = useState('');
  const [status, setStatus] = useState('');
  const [maxStudies, setMaxStudies] = useState(10);
  const [diagnosisResults, setDiagnosisResults] = useState<DiagnosisOption[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [announceMessage, setAnnounceMessage] = useState('');
  const debounceRef = useRef<NodeJS.Timeout>();

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['clinical-trials', condition, maxStudies, status],
    queryFn: () => clinicalTrialsService.search(condition, maxStudies, status || undefined),
    enabled: false, // Don't auto-fetch, wait for user to click search
  });

  const handleDiagnosisSearch = (query: string) => {
    setSearchQuery(query);
    setHighlightedIndex(-1);

    // Clear previous debounce timer
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Debounce with 0ms delay (instant response like IDE autocomplete)
    debounceRef.current = setTimeout(async () => {
      if (query.length >= 3) {
        try {
          const response = await fetch(`/api/v1/content-settings/diagnosis/search?q=${encodeURIComponent(query)}&limit=15`);
          const results = await response.json();
          setDiagnosisResults(results);
          setShowDropdown(true);
        } catch (error) {
          console.error('Failed to search diagnoses:', error);
          setDiagnosisResults([]);
        }
      } else {
        setDiagnosisResults([]);
        setShowDropdown(false);
      }
    }, 0);
  };

  const selectDiagnosis = (diagnosis: DiagnosisOption) => {
    setSearchQuery(diagnosis.disease_name);
    setCondition(diagnosis.disease_name);
    setShowDropdown(false);
    // Auto-trigger search
    refetch();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showDropdown || diagnosisResults.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev < diagnosisResults.length - 1 ? prev + 1 : prev));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < diagnosisResults.length) {
          selectDiagnosis(diagnosisResults[highlightedIndex]);
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        break;
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setCondition(searchQuery);
      setAnnounceMessage(`Searching clinical trials for "${searchQuery}"...`);
      refetch();
    }
  };

  const handleVoiceTranscript = (transcript: string) => {
    handleDiagnosisSearch(searchQuery + ' ' + transcript);
  };

  return (
    <div>
      {/* Live Region for Screen Reader Announcements */}
      <LiveRegion>{announceMessage}</LiveRegion>

      <h1 className="text-3xl font-bold text-gray-800 mb-6">{t('clinicalTrials.title')}</h1>

      {/* Search Form */}
      <div className="card mb-6" role="search" aria-label="Clinical trials search">
        <form onSubmit={handleSearch}>
          <div className="mb-4">
            <label htmlFor="trials-search" className="block text-gray-700 font-medium mb-2">
              <i className="fas fa-search mr-2" aria-hidden="true"></i>
              {t('clinicalTrials.searchSection.diagnosisLabel')}
            </label>
            <div className="flex gap-2 mb-2">
              <div className="relative flex-1">
                <i className="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" aria-hidden="true"></i>
                <input
                  id="trials-search"
                  type="text"
                  value={searchQuery}
                  onChange={(e) => handleDiagnosisSearch(e.target.value)}
                  onKeyDown={handleKeyDown}
                  onFocus={() => diagnosisResults.length > 0 && setShowDropdown(true)}
                  placeholder="Type the disease name (e.g., diabetes, hypertension, asthma)..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  autoComplete="off"
                  aria-describedby="trials-hint"
                  aria-autocomplete="list"
                  aria-expanded={showDropdown}
                  aria-controls={showDropdown ? "trials-dropdown" : undefined}
                />
                {showDropdown && diagnosisResults.length > 0 && (
                  <div
                    id="trials-dropdown"
                    role="listbox"
                    className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto"
                  >
                    {diagnosisResults.map((result, index) => (
                      <div
                        key={result.disease_id}
                        role="option"
                        aria-selected={index === highlightedIndex}
                        onClick={() => selectDiagnosis(result)}
                        className={`px-4 py-2 cursor-pointer ${
                          index === highlightedIndex ? 'bg-blue-50' : 'hover:bg-gray-50'
                        }`}
                      >
                        <div className="font-medium text-gray-900">{result.disease_name}</div>
                        <div className="text-xs text-gray-500">{result.category}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <VoiceDictation
                onTranscript={handleVoiceTranscript}
                medicalTerms={diagnosisResults.map(d => d.disease_name)}
                placeholder="Use voice to search"
              />
            </div>
            <p id="trials-hint" className="text-sm text-gray-500 mt-1">
              <i className="fas fa-info-circle mr-1" aria-hidden="true"></i>
              Start typing the disease name or use voice input - results refine as you type. Use arrow keys to navigate, Enter to select.
            </p>
          </div>

          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">
              Trial Status (Optional)
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Statuses</option>
              <option value="RECRUITING">Recruiting</option>
              <option value="ACTIVE_NOT_RECRUITING">Active, Not Recruiting</option>
              <option value="COMPLETED">Completed</option>
              <option value="ENROLLING_BY_INVITATION">Enrolling by Invitation</option>
              <option value="NOT_YET_RECRUITING">Not Yet Recruiting</option>
              <option value="SUSPENDED">Suspended</option>
              <option value="TERMINATED">Terminated</option>
              <option value="WITHDRAWN">Withdrawn</option>
            </select>
            <p className="text-sm text-gray-500 mt-1">
              <i className="fas fa-info-circle mr-1"></i>
              Filter trials by their current recruitment status
            </p>
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