import { useState, useRef, useEffect } from 'react';

interface LanguageOption {
  code: string;
  name: string;
  nativeName: string;
}

interface LanguageAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect?: (code: string) => void;
  placeholder?: string;
  required?: boolean;
}

const LANGUAGES: LanguageOption[] = [
  { code: 'en', name: 'English', nativeName: 'English' },
  { code: 'es', name: 'Spanish', nativeName: 'Español' },
  { code: 'zh', name: 'Chinese (Mandarin)', nativeName: '中文' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी' },
  { code: 'ar', name: 'Arabic', nativeName: 'العربية' },
  { code: 'pt', name: 'Portuguese', nativeName: 'Português' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা' },
  { code: 'ru', name: 'Russian', nativeName: 'Русский' },
  { code: 'ja', name: 'Japanese', nativeName: '日本語' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ' },
  { code: 'de', name: 'German', nativeName: 'Deutsch' },
  { code: 'ko', name: 'Korean', nativeName: '한국어' },
  { code: 'fr', name: 'French', nativeName: 'Français' },
  { code: 'vi', name: 'Vietnamese', nativeName: 'Tiếng Việt' },
  { code: 'it', name: 'Italian', nativeName: 'Italiano' },
  { code: 'tl', name: 'Tagalog', nativeName: 'Tagalog' },
];

export default function LanguageAutocomplete({
  value,
  onChange,
  onSelect,
  placeholder = 'Search for a language...',
  required = false,
}: LanguageAutocompleteProps) {
  const [inputValue, setInputValue] = useState('');
  const [filteredLanguages, setFilteredLanguages] = useState<LanguageOption[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Get display name for selected language code
  useEffect(() => {
    const selected = LANGUAGES.find(lang => lang.code === value);
    if (selected && inputValue === '') {
      setInputValue(selected.name);
    }
  }, [value, inputValue]);

  // Filter languages based on input
  const filterLanguages = (query: string) => {
    if (!query || query.length === 0) {
      setFilteredLanguages(LANGUAGES);
      return;
    }

    const lowerQuery = query.toLowerCase();
    const filtered = LANGUAGES.filter(
      lang =>
        lang.name.toLowerCase().includes(lowerQuery) ||
        lang.nativeName.toLowerCase().includes(lowerQuery) ||
        lang.code.toLowerCase().includes(lowerQuery)
    );
    setFilteredLanguages(filtered);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    filterLanguages(newValue);
    setShowDropdown(true);
    setSelectedIndex(-1);
  };

  const handleSelect = (language: LanguageOption) => {
    setInputValue(language.name);
    onChange(language.code);
    setShowDropdown(false);
    setSelectedIndex(-1);
    if (onSelect) {
      onSelect(language.code);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showDropdown || filteredLanguages.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex(prev => (prev < filteredLanguages.length - 1 ? prev + 1 : prev));
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex(prev => (prev > 0 ? prev - 1 : 0));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < filteredLanguages.length) {
          handleSelect(filteredLanguages[selectedIndex]);
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const handleFocus = () => {
    filterLanguages(inputValue);
    setShowDropdown(true);
  };

  const handleBlur = () => {
    // Delay to allow click on dropdown item
    setTimeout(() => {
      setShowDropdown(false);
      setSelectedIndex(-1);
    }, 200);
  };

  return (
    <div className="relative">
      <div className="relative">
        <i className="fas fa-language absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          autoComplete="off"
          required={required}
        />
      </div>

      {showDropdown && filteredLanguages.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto"
        >
          {filteredLanguages.map((language, index) => (
            <div
              key={language.code}
              onClick={() => handleSelect(language)}
              onMouseEnter={() => setSelectedIndex(index)}
              className={`px-4 py-3 cursor-pointer transition-colors ${
                index === selectedIndex
                  ? 'bg-blue-50 border-l-4 border-blue-500'
                  : 'hover:bg-gray-50 border-l-4 border-transparent'
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-gray-900">{language.name}</div>
                  <div className="text-sm text-gray-500">{language.nativeName}</div>
                </div>
                <div className="text-xs text-gray-400 uppercase">{language.code}</div>
              </div>
            </div>
          ))}
        </div>
      )}

      {showDropdown && filteredLanguages.length === 0 && inputValue.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg p-4">
          <p className="text-sm text-gray-500 text-center">
            <i className="fas fa-search mr-2"></i>
            No languages found matching "{inputValue}"
          </p>
        </div>
      )}
    </div>
  );
}
