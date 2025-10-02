import { useState, useEffect } from 'react';
import VoiceDictation from '../components/VoiceDictation';
import { LiveRegion } from '../components/ScreenReaderOnly';

interface GlossaryTerm {
  disease_id: number;
  disease_name: string;
  category: string;
  aliases?: string[];
}

export default function MedicalGlossary() {
  const [searchQuery, setSearchQuery] = useState('');
  const [terms, setTerms] = useState<GlossaryTerm[]>([]);
  const [filteredTerms, setFilteredTerms] = useState<GlossaryTerm[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [isLoading, setIsLoading] = useState(false);
  const [categories, setCategories] = useState<string[]>([]);
  const [announceMessage, setAnnounceMessage] = useState('');

  useEffect(() => {
    // Load all terms on mount
    loadAllTerms();
  }, []);

  useEffect(() => {
    // Filter terms based on search and category
    filterTerms();
  }, [searchQuery, selectedCategory, terms]);

  const loadAllTerms = async () => {
    setIsLoading(true);
    try {
      // Load comprehensive disease list
      const response = await fetch('/api/v1/content-settings/diagnosis/search?q=&limit=1000');
      const data = await response.json();
      setTerms(data);

      // Extract unique categories
      const uniqueCategories = [...new Set(data.map((term: GlossaryTerm) => term.category))].sort() as string[];
      setCategories(uniqueCategories);
    } catch (error) {
      console.error('Failed to load glossary terms:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filterTerms = () => {
    let filtered = terms;

    // Filter by category
    if (selectedCategory !== 'all') {
      filtered = filtered.filter(term => term.category === selectedCategory);
    }

    // Filter by search query
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(term =>
        term.disease_name.toLowerCase().includes(query) ||
        term.category.toLowerCase().includes(query) ||
        term.aliases?.some(alias => alias.toLowerCase().includes(query))
      );
    }

    setFilteredTerms(filtered);

    // Announce results to screen readers
    if (searchQuery.trim()) {
      setAnnounceMessage(`Found ${filtered.length} medical terms matching "${searchQuery}"`);
    } else {
      setAnnounceMessage(`Showing all ${filtered.length} medical terms`);
    }
  };

  const handleVoiceTranscript = (transcript: string) => {
    setSearchQuery(prev => prev + ' ' + transcript);
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

  const downloadDictionary = () => {
    // Generate dictionary file for download
    const dictContent = terms
      .map(term => {
        const lines = [term.disease_name];
        if (term.aliases) {
          lines.push(...term.aliases);
        }
        return lines.join('\n');
      })
      .join('\n');

    const blob = new Blob([dictContent], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'medical-dictionary.txt';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const exportToWord = () => {
    // Generate AutoCorrect entries for Word
    let autocorrectXML = '<?xml version="1.0" encoding="UTF-8"?>\n<AutoCorrect>\n';

    terms.forEach(term => {
      if (term.aliases) {
        term.aliases.forEach(alias => {
          if (alias.toLowerCase() !== term.disease_name.toLowerCase()) {
            autocorrectXML += `  <Entry from="${alias}" to="${term.disease_name}"/>\n`;
          }
        });
      }
    });

    autocorrectXML += '</AutoCorrect>';

    const blob = new Blob([autocorrectXML], { type: 'application/xml' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'medical-autocorrect.xml';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div>
      {/* Live Region for Screen Reader Announcements */}
      <LiveRegion>{announceMessage}</LiveRegion>

      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Medical Glossary</h1>
        <p className="text-gray-600">
          Searchable database of medical terms, diseases, and conditions with aliases and categories
        </p>
      </div>

      {/* Search and Filter Section */}
      <div className="card mb-6" role="search" aria-label="Medical glossary search">
        <div className="grid md:grid-cols-2 gap-4 mb-4">
          {/* Search Box with Voice Input */}
          <div>
            <label htmlFor="glossary-search" className="block text-gray-700 font-medium mb-2">
              <i className="fas fa-search mr-2" aria-hidden="true"></i>
              Search Terms
            </label>
            <div className="flex gap-2">
              <input
                id="glossary-search"
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by disease name, alias, or category..."
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
              Filter by Category
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="input-field w-full"
            >
              <option value="all">All Categories ({terms.length} terms)</option>
              {categories.map(category => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Download Options */}
        <div className="flex flex-wrap gap-3 pt-4 border-t">
          <button onClick={downloadDictionary} className="btn-secondary">
            <i className="fas fa-download mr-2"></i>
            Download Dictionary (.txt)
          </button>
          <button onClick={exportToWord} className="btn-secondary">
            <i className="fas fa-file-word mr-2"></i>
            Export AutoCorrect (XML)
          </button>
          <div className="text-sm text-gray-600 flex items-center ml-auto">
            <i className="fas fa-info-circle mr-2"></i>
            {filteredTerms.length} of {terms.length} terms shown
          </div>
        </div>
      </div>

      {/* Results */}
      {isLoading ? (
        <div className="text-center py-12">
          <i className="fas fa-spinner fa-spin text-4xl text-blue-600 mb-4"></i>
          <p className="text-gray-600">Loading medical glossary...</p>
        </div>
      ) : filteredTerms.length === 0 ? (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded-lg">
          <i className="fas fa-search mr-2"></i>
          No terms found matching your search criteria.
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredTerms.slice(0, 100).map((term) => (
            <div key={term.disease_id} className="card hover:shadow-lg transition-shadow">
              <div className="mb-2">
                <h3 className="font-bold text-gray-800 text-lg">
                  {highlightMatch(term.disease_name, searchQuery)}
                </h3>
                <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded mt-1">
                  {term.category}
                </span>
              </div>

              {term.aliases && term.aliases.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200">
                  <p className="text-xs text-gray-600 font-semibold mb-1">Also known as:</p>
                  <div className="flex flex-wrap gap-1">
                    {term.aliases.slice(0, 3).map((alias, idx) => (
                      <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                        {alias}
                      </span>
                    ))}
                    {term.aliases.length > 3 && (
                      <span className="text-xs text-gray-500 px-2 py-1">
                        +{term.aliases.length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {filteredTerms.length > 100 && (
        <div className="mt-6 bg-gray-50 border border-gray-200 text-gray-700 px-4 py-3 rounded-lg text-center">
          <i className="fas fa-info-circle mr-2"></i>
          Showing first 100 results. Refine your search to see more specific terms.
        </div>
      )}

      {/* Usage Instructions */}
      <div className="card mt-6 bg-blue-50 border-blue-200">
        <h3 className="font-bold text-gray-800 mb-3">
          <i className="fas fa-lightbulb text-yellow-500 mr-2"></i>
          How to Use Dictionary Files
        </h3>
        <div className="space-y-3 text-sm text-gray-700">
          <div>
            <strong>Microsoft Word (.txt):</strong>
            <ol className="list-decimal list-inside ml-4 mt-1">
              <li>Click "Download Dictionary"</li>
              <li>In Word: File → Options → Proofing → Custom Dictionaries</li>
              <li>Click "Add" and select the downloaded .txt file</li>
            </ol>
          </div>
          <div>
            <strong>AutoCorrect (XML):</strong>
            <ol className="list-decimal list-inside ml-4 mt-1">
              <li>Click "Export AutoCorrect"</li>
              <li>In Word: File → Options → Proofing → AutoCorrect Options</li>
              <li>Manually add corrections or use macro to import XML</li>
            </ol>
          </div>
          <div className="pt-2 border-t border-blue-300">
            <i className="fas fa-shield-alt text-blue-600 mr-2"></i>
            <strong>Note:</strong> These dictionaries help ensure consistent medical terminology in your documents.
          </div>
        </div>
      </div>
    </div>
  );
}
