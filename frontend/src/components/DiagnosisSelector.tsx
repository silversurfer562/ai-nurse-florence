import { useState, useEffect, useRef } from 'react';

interface DiagnosisOption {
  id: string;
  label: string;
  value: string;
  icd10_code: string;
}

interface DiagnosisSelectorProps {
  onChange: (diagnosis: DiagnosisOption | null) => void;
  placeholder?: string;
  className?: string;
}

export default function DiagnosisSelector({
  onChange,
  placeholder = 'Search for diagnosis...',
  className = '',
}: DiagnosisSelectorProps) {
  const [query, setQuery] = useState('');
  const [options, setOptions] = useState<DiagnosisOption[]>([]);
  const [showOptions, setShowOptions] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const debounceRef = useRef<NodeJS.Timeout>();

  // Close options when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setShowOptions(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Fetch diagnosis options from API
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    if (query.length < 2) {
      setOptions([]);
      setShowOptions(false);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setIsLoading(true);
      try {
        const response = await fetch(
          `/api/v1/content-settings/diagnosis/autocomplete?q=${encodeURIComponent(query)}&limit=10`
        );
        if (response.ok) {
          const data = await response.json();
          setOptions(data);
          setShowOptions(data.length > 0);
        }
      } catch (error) {
        console.error('Error fetching diagnoses:', error);
        setOptions([]);
      } finally {
        setIsLoading(false);
      }
    }, 300);
  }, [query]);

  const handleSelect = (option: DiagnosisOption) => {
    setQuery(option.label);
    onChange(option);
    setShowOptions(false);
    setSelectedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!showOptions) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) => (prev < options.length - 1 ? prev + 1 : prev));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < options.length) {
          handleSelect(options[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowOptions(false);
        setSelectedIndex(-1);
        break;
    }
  };

  return (
    <div ref={wrapperRef} className={`relative ${className}`}>
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            if (!e.target.value) {
              onChange(null);
            }
          }}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (options.length > 0) {
              setShowOptions(true);
            }
          }}
          placeholder={placeholder}
          className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
        <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
          {isLoading ? (
            <i className="fas fa-spinner fa-spin text-gray-400"></i>
          ) : (
            <i className="fas fa-search text-gray-400"></i>
          )}
        </div>
      </div>

      {showOptions && options.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
          {options.map((option, index) => (
            <div
              key={option.id}
              onClick={() => handleSelect(option)}
              className={`px-4 py-2 cursor-pointer transition-colors ${
                index === selectedIndex
                  ? 'bg-blue-100'
                  : 'hover:bg-gray-100'
              }`}
            >
              <div className="font-medium text-gray-900">{option.label}</div>
              <div className="text-sm text-gray-500">ICD-10: {option.icd10_code}</div>
            </div>
          ))}
        </div>
      )}

      {showOptions && query.length >= 2 && options.length === 0 && !isLoading && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg p-4">
          <p className="text-gray-500 text-sm">
            <i className="fas fa-info-circle mr-2"></i>
            No diagnoses found in the content library. Try different keywords or contact your administrator to add new diagnoses.
          </p>
        </div>
      )}
    </div>
  );
}
