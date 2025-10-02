import React, { useState, useEffect, useRef } from 'react';
import { api } from '../services/api';
import VoiceDictation from './VoiceDictation';

interface DrugAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect?: (drug: string) => void;
  placeholder?: string;
  className?: string;
  enableVoice?: boolean;
}

export default function DrugAutocomplete({
  value,
  onChange,
  onSelect,
  placeholder = 'Enter medication name...',
  className = '',
  enableVoice = true
}: DrugAutocompleteProps) {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [networkWarning, setNetworkWarning] = useState<string | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout>();

  // Close suggestions when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch suggestions from API
  const fetchSuggestions = async (query: string) => {
    if (query.length < 2) {
      setSuggestions([]);
      setNetworkWarning(null);
      return;
    }

    setIsLoading(true);
    try {
      const response = await api.get('/api/v1/drug-interactions/drug-names', {
        params: { query, limit: 10 }
      });

      if (response.data?.success && response.data?.data?.drugs) {
        setSuggestions(response.data.data.drugs);
        setShowSuggestions(true);
        // Check for network warning
        if (response.data.data.network_warning) {
          setNetworkWarning(response.data.data.network_warning);
        } else {
          setNetworkWarning(null);
        }
      }
    } catch (error) {
      console.error('Failed to fetch drug suggestions:', error);
      setSuggestions([]);
      setNetworkWarning('⚠️ Unable to fetch medication list. Please check your connection.');
    } finally {
      setIsLoading(false);
    }
  };

  // Debounced input handler
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    setSelectedIndex(-1);

    // Clear existing debounce timer
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    // Set new debounce timer
    debounceRef.current = setTimeout(() => {
      fetchSuggestions(newValue);
    }, 300); // 300ms debounce
  };

  // Handle suggestion selection
  const handleSelect = (drug: string) => {
    onChange(drug);
    setShowSuggestions(false);
    setSuggestions([]);
    if (onSelect) {
      onSelect(drug);
    }
  };

  // Keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showSuggestions || suggestions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev =>
          prev < suggestions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => prev > 0 ? prev - 1 : -1);
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < suggestions.length) {
          handleSelect(suggestions[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowSuggestions(false);
        break;
    }
  };

  const handleVoiceTranscript = (transcript: string) => {
    const newValue = value + ' ' + transcript;
    onChange(newValue);
    fetchSuggestions(newValue);
  };

  return (
    <div ref={wrapperRef} className="relative">
      {networkWarning && (
        <div className="mb-2 p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm text-yellow-800">
          <i className="fas fa-exclamation-triangle mr-2"></i>
          {networkWarning}
        </div>
      )}

      <div className="flex gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={value}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => value.length >= 2 && suggestions.length > 0 && setShowSuggestions(true)}
            placeholder={placeholder}
            className={`form-input ${className}`}
            autoComplete="off"
          />
          {isLoading && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <i className="fas fa-spinner fa-spin text-gray-400"></i>
            </div>
          )}
        </div>
        {enableVoice && (
          <VoiceDictation
            onTranscript={handleVoiceTranscript}
            medicalTerms={suggestions}
            placeholder="Use voice to search medications"
          />
        )}
      </div>

      {showSuggestions && suggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {suggestions.map((drug, index) => (
            <div
              key={drug}
              onClick={() => handleSelect(drug)}
              onMouseEnter={() => setSelectedIndex(index)}
              className={`px-4 py-2 cursor-pointer transition-colors ${
                index === selectedIndex
                  ? 'bg-blue-500 text-white'
                  : 'hover:bg-gray-100'
              }`}
            >
              <div className="flex items-center">
                <i className="fas fa-pills text-sm mr-2 opacity-60"></i>
                <span>{drug}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showSuggestions && suggestions.length === 0 && !isLoading && value.length >= 2 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg px-4 py-2 text-sm text-gray-500">
          <i className="fas fa-info-circle mr-2"></i>
          No medications found matching "{value}"
        </div>
      )}
    </div>
  );
}