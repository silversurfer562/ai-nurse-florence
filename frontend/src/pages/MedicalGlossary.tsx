import { useState, useEffect } from 'react';
import VoiceDictation from '../components/VoiceDictation';
import { LiveRegion } from '../components/ScreenReaderOnly';

interface GlossaryTerm {
  mondo_id: string;
  disease_name: string;
  synonyms: string[];
  icd10_codes: string[];
  snomed_code?: string;
  umls_code?: string;
  description?: string;
  category?: string;
  is_rare: boolean;
  prevalence?: string;
}

interface GlossaryResponse {
  total: number;
  returned: number;
  offset: number;
  diseases: GlossaryTerm[];
  categories?: string[];
}

export default function MedicalGlossary() {
  const [searchQuery, setSearchQuery] = useState('');
  const [terms, setTerms] = useState<GlossaryTerm[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [rareOnly, setRareOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [categories, setCategories] = useState<string[]>([]);
  const [announceMessage, setAnnounceMessage] = useState('');
  const [totalCount, setTotalCount] = useState(0);
  const [currentOffset, setCurrentOffset] = useState(0);
  const limit = 100;

  useEffect(() => {
    loadTerms();
  }, [searchQuery, selectedCategory, rareOnly, currentOffset]);

  const loadTerms = async () => {
    setIsLoading(true);
    try {
      const params = new URLSearchParams({
        limit: limit.toString(),
        offset: currentOffset.toString(),
        include_categories: currentOffset === 0 ? 'true' : 'false'
      });

      if (searchQuery.trim()) {
        params.append('search', searchQuery.trim());
      }
      if (selectedCategory !== 'all') {
        params.append('category', selectedCategory);
      }
      if (rareOnly) {
        params.append('rare_only', 'true');
      }

      const response = await fetch(`/api/v1/disease-glossary/?${params}`);
      const data: GlossaryResponse = await response.json();

      setTerms(data.diseases || []);
      setTotalCount(data.total || 0);

      // Load categories only on first load
      if (data.categories) {
        setCategories(data.categories);
      }

      // Announce results to screen readers
      if (searchQuery.trim()) {
        setAnnounceMessage(`Found ${data.total} diseases matching "${searchQuery}"`);
      } else {
        setAnnounceMessage(`Showing ${data.returned} of ${data.total} diseases`);
      }
    } catch (error) {
      console.error('Failed to load glossary terms:', error);
      setAnnounceMessage('Error loading disease glossary');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVoiceTranscript = (transcript: string) => {
    setSearchQuery(prev => prev + ' ' + transcript);
    setCurrentOffset(0); // Reset to first page on new search
  };

  const highlightMatch = (text: string, query: string) => {
    if (!query.trim()) return text;

    const regex = new RegExp(`(${query})`, 'gi');
    const parts = text.split(regex);

    return parts.map((part, index) =>
      regex.test(part) ? (
        <mark key={index} className="bg-yellow-200 font-semibold">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  const downloadGlossary = async (format: 'json' | 'csv') => {
    try {
      const params = new URLSearchParams({ format });
      if (selectedCategory !== 'all') {
        params.append('category', selectedCategory);
      }
      if (rareOnly) {
        params.append('rare_only', 'true');
      }

      const response = await fetch(`/api/v1/disease-glossary/export?${params}`);
      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;

      // Extract filename from Content-Disposition header if available
      const contentDisposition = response.headers.get('Content-Disposition');
      const filenameMatch = contentDisposition?.match(/filename="?(.+)"?/);
      a.download = filenameMatch ? filenameMatch[1] : `disease_glossary.${format}`;

      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download glossary:', error);
    }
  };

  const loadNextPage = () => {
    setCurrentOffset(prev => prev + limit);
  };

  const loadPreviousPage = () => {
    setCurrentOffset(prev => Math.max(0, prev - limit));
  };

  return (
    <div>
      {/* Live Region for Screen Reader Announcements */}
      <LiveRegion>{announceMessage}</LiveRegion>

      <div className="mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              <i className="fas fa-book-medical mr-3 text-blue-600"></i>
              Disease Glossary
            </h1>
            <p className="text-gray-600">
              Comprehensive database of {totalCount.toLocaleString()}+ diseases with MONDO IDs, ICD-10 codes, SNOMED codes, and clinical descriptions
            </p>
          </div>
          <a
            href="/"
            className="btn-primary flex items-center gap-2 whitespace-nowrap"
            title="Check drug interactions"
          >
            <i className="fas fa-pills"></i>
            Drug Checker
          </a>
        </div>
      </div>

      {/* Search and Filter Section */}
      <div className="card mb-6" role="search" aria-label="Disease glossary search">
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          {/* Search Box with Voice Input */}
          <div>
            <label htmlFor="glossary-search" className="block text-gray-700 font-medium mb-2">
              <i className="fas fa-search mr-2" aria-hidden="true"></i>
              Search Diseases
            </label>
            <div className="flex gap-2">
              <input
                id="glossary-search"
                type="text"
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setCurrentOffset(0);
                }}
                placeholder="Search by disease name or synonym..."
                className="input-field flex-1"
                aria-describedby="search-hint"
              />
              <VoiceDictation
                onTranscript={handleVoiceTranscript}
                medicalTerms={terms.map(t => t.disease_name)}
                placeholder="Use voice to search"
              />
            </div>
            <p id="search-hint" className="text-sm text-gray-500 mt-1">
              Type to search or use microphone for voice input
            </p>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-gray-700 font-medium mb-2">
              <i className="fas fa-filter mr-2"></i>
              Filter Options
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => {
                setSelectedCategory(e.target.value);
                setCurrentOffset(0);
              }}
              className="input-field w-full mb-2"
            >
              <option value="all">All Categories</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
            <label className="flex items-center text-sm text-gray-700">
              <input
                type="checkbox"
                checked={rareOnly}
                onChange={(e) => {
                  setRareOnly(e.target.checked);
                  setCurrentOffset(0);
                }}
                className="mr-2"
              />
              <i className="fas fa-star text-purple-500 mr-1"></i>
              Show only rare diseases
            </label>
          </div>
        </div>

        {/* Download Options */}
        <div className="flex flex-wrap gap-3 pt-4 border-t">
          <button onClick={() => downloadGlossary('json')} className="btn-secondary">
            <i className="fas fa-download mr-2"></i>
            Download JSON
          </button>
          <button onClick={() => downloadGlossary('csv')} className="btn-secondary">
            <i className="fas fa-file-csv mr-2"></i>
            Download CSV
          </button>
          <div className="text-sm text-gray-600 flex items-center ml-auto">
            <i className="fas fa-info-circle mr-2"></i>
            {totalCount.toLocaleString()} diseases total
          </div>
        </div>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="text-center py-12">
          <i className="fas fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
          <p className="text-gray-600">Loading disease glossary...</p>
        </div>
      ) : terms.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg">
          <i className="fas fa-search mr-2"></i>
          No diseases found matching your search criteria.
        </div>
      ) : (
        <>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {terms.map((term) => (
              <div key={term.mondo_id} className="card hover:shadow-lg transition-shadow">
                <div className="mb-2">
                  <h3 className="font-bold text-gray-800 text-lg">
                    {highlightMatch(term.disease_name, searchQuery)}
                  </h3>
                  <div className="flex gap-2 mt-2 flex-wrap">
                    {term.category && (
                      <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                        {term.category}
                      </span>
                    )}
                    {term.is_rare && (
                      <span className="inline-block bg-purple-100 text-purple-800 text-xs px-2 py-1 rounded">
                        <i className="fas fa-star mr-1"></i>
                        Rare Disease
                      </span>
                    )}
                  </div>
                </div>

                {term.description && (
                  <p className="text-sm text-gray-600 mt-2">{term.description}</p>
                )}

                <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                  <div className="text-xs text-gray-500">
                    <strong>MONDO:</strong> {term.mondo_id}
                  </div>
                  {term.icd10_codes && term.icd10_codes.length > 0 && (
                    <div className="text-xs text-gray-500">
                      <strong>ICD-10:</strong> {term.icd10_codes.join(', ')}
                    </div>
                  )}
                  {term.snomed_code && (
                    <div className="text-xs text-gray-500">
                      <strong>SNOMED:</strong> {term.snomed_code}
                    </div>
                  )}
                  {term.prevalence && (
                    <div className="text-xs text-gray-500">
                      <strong>Prevalence:</strong> {term.prevalence}
                    </div>
                  )}
                </div>

                {term.synonyms && term.synonyms.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-xs text-gray-600 font-semibold mb-1">Also known as:</p>
                    <div className="flex flex-wrap gap-1">
                      {term.synonyms.slice(0, 3).map((synonym, idx) => (
                        <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                          {synonym}
                        </span>
                      ))}
                      {term.synonyms.length > 3 && (
                        <span className="text-xs text-gray-500 px-2 py-1">
                          +{term.synonyms.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalCount > limit && (
            <div className="mt-6 flex justify-between items-center">
              <button
                onClick={loadPreviousPage}
                disabled={currentOffset === 0}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <i className="fas fa-chevron-left mr-2"></i>
                Previous
              </button>
              <span className="text-gray-600">
                Showing {currentOffset + 1} - {Math.min(currentOffset + limit, totalCount)} of {totalCount.toLocaleString()}
              </span>
              <button
                onClick={loadNextPage}
                disabled={currentOffset + limit >= totalCount}
                className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
                <i className="fas fa-chevron-right ml-2"></i>
              </button>
            </div>
          )}
        </>
      )}

      {/* Usage Instructions */}
      <div className="card mt-6 bg-blue-50 border-blue-200">
        <h3 className="font-bold text-gray-800 mb-3">
          <i className="fas fa-lightbulb text-yellow-500 mr-2"></i>
          About This Glossary
        </h3>
        <div className="space-y-3 text-sm text-gray-700">
          <div>
            <strong>Data Sources:</strong>
            <ul className="list-disc list-inside ml-4 mt-1">
              <li>MONDO (Monarch Disease Ontology) - Primary disease classification</li>
              <li>ICD-10 - International Classification of Diseases codes</li>
              <li>SNOMED CT - Clinical terminology</li>
              <li>UMLS - Unified Medical Language System</li>
            </ul>
          </div>
          <div>
            <strong>Export Options:</strong>
            <ul className="list-disc list-inside ml-4 mt-1">
              <li><strong>JSON:</strong> Complete structured data with metadata and CC-BY-4.0 license</li>
              <li><strong>CSV:</strong> Spreadsheet-friendly format for analysis and import</li>
            </ul>
          </div>
          <div className="pt-2 border-t border-blue-300">
            <i className="fas fa-creative-commons text-blue-600 mr-2"></i>
            <strong>License:</strong> Open data available under CC-BY-4.0. Attribution: AI Nurse Florence
          </div>
        </div>
      </div>
    </div>
  );
}
