import { useState, useEffect, useRef } from 'react';

interface VoiceDictationProps {
  onTranscript: (text: string) => void;
  language?: string;
  continuous?: boolean;
  medicalTerms?: string[];
  placeholder?: string;
}

export default function VoiceDictation({
  onTranscript,
  language = 'en-US',
  continuous = false,
  medicalTerms = []
}: VoiceDictationProps) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Check if Web Speech API is supported
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setIsSupported(false);
      return;
    }

    // Initialize speech recognition
    const recognition = new SpeechRecognition();
    recognition.lang = language;
    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.maxAlternatives = 3;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event: any) => {
      let interimText = '';
      let finalText = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const text = result[0].transcript;

        if (result.isFinal) {
          finalText += text + ' ';
        } else {
          interimText += text;
        }
      }

      if (finalText) {
        const correctedText = applyMedicalCorrections(finalText.trim(), medicalTerms);
        setTranscript(prev => prev + correctedText + ' ');
        onTranscript(correctedText);
      }

      setInterimTranscript(interimText);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);

      if (event.error === 'not-allowed') {
        alert('Microphone access denied. Please enable microphone permissions in your browser settings.');
      }
    };

    recognition.onend = () => {
      setIsListening(false);
      setInterimTranscript('');
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [language, continuous, onTranscript, medicalTerms]);

  const applyMedicalCorrections = (text: string, terms: string[]): string => {
    if (!terms.length) return text;

    let corrected = text;

    // Common medical abbreviations and corrections
    const medicalCorrections: { [key: string]: string } = {
      'DM': 'Diabetes Mellitus',
      'MI': 'Myocardial Infarction',
      'CHF': 'Congestive Heart Failure',
      'COPD': 'Chronic Obstructive Pulmonary Disease',
      'HTN': 'Hypertension',
      'CAD': 'Coronary Artery Disease',
      'CVA': 'Cerebrovascular Accident',
      'URI': 'Upper Respiratory Infection',
      'UTI': 'Urinary Tract Infection',
      'DVT': 'Deep Vein Thrombosis',
    };

    // Apply medical term corrections
    Object.entries(medicalCorrections).forEach(([abbr, full]) => {
      const regex = new RegExp(`\\b${abbr}\\b`, 'gi');
      corrected = corrected.replace(regex, full);
    });

    // Try to match against known medical terms (fuzzy matching)
    terms.forEach(term => {
      const termLower = term.toLowerCase();
      const words = corrected.split(' ');

      words.forEach((word, index) => {
        if (word.toLowerCase() === termLower ||
            levenshteinDistance(word.toLowerCase(), termLower) <= 2) {
          words[index] = term;
        }
      });

      corrected = words.join(' ');
    });

    return corrected;
  };

  // Simple Levenshtein distance for fuzzy matching
  const levenshteinDistance = (str1: string, str2: string): number => {
    const m = str1.length;
    const n = str2.length;
    const dp: number[][] = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));

    for (let i = 0; i <= m; i++) dp[i][0] = i;
    for (let j = 0; j <= n; j++) dp[0][j] = j;

    for (let i = 1; i <= m; i++) {
      for (let j = 1; j <= n; j++) {
        if (str1[i - 1] === str2[j - 1]) {
          dp[i][j] = dp[i - 1][j - 1];
        } else {
          dp[i][j] = Math.min(
            dp[i - 1][j - 1] + 1,
            dp[i - 1][j] + 1,
            dp[i][j - 1] + 1
          );
        }
      }
    }

    return dp[m][n];
  };

  const startListening = () => {
    if (!recognitionRef.current || !isSupported) return;

    try {
      recognitionRef.current.start();
    } catch (error) {
      console.error('Error starting recognition:', error);
    }
  };

  const stopListening = () => {
    if (!recognitionRef.current) return;

    try {
      recognitionRef.current.stop();
    } catch (error) {
      console.error('Error stopping recognition:', error);
    }
  };

  const clearTranscript = () => {
    setTranscript('');
    setInterimTranscript('');
  };

  if (!isSupported) {
    return (
      <div
        className="text-sm text-gray-500 italic"
        role="status"
        aria-live="polite"
      >
        <i className="fas fa-microphone-slash mr-2"></i>
        Voice input not supported in this browser. Try Chrome or Edge.
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2">
      <button
        type="button"
        onClick={isListening ? stopListening : startListening}
        className={`p-2 rounded-lg transition-all ${
          isListening
            ? 'bg-red-500 text-white hover:bg-red-600 animate-pulse'
            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
        }`}
        aria-label={isListening ? 'Stop voice dictation' : 'Start voice dictation'}
        aria-pressed={isListening}
        title={isListening ? 'Click to stop recording' : 'Click to start voice input'}
      >
        <i className={`fas fa-microphone ${isListening ? 'fa-pulse' : ''}`}></i>
      </button>

      {transcript && (
        <button
          type="button"
          onClick={clearTranscript}
          className="p-2 text-gray-500 hover:text-gray-700"
          aria-label="Clear voice transcript"
          title="Clear transcript"
        >
          <i className="fas fa-times"></i>
        </button>
      )}

      {/* Live transcript display */}
      {(transcript || interimTranscript) && (
        <div
          className="flex-1 text-sm"
          role="status"
          aria-live="polite"
          aria-atomic="true"
        >
          <span className="text-gray-800">{transcript}</span>
          <span className="text-gray-400 italic">{interimTranscript}</span>
        </div>
      )}

      {/* Screen reader only status */}
      <div className="sr-only" role="status" aria-live="assertive" aria-atomic="true">
        {isListening ? 'Recording voice input' : 'Voice input stopped'}
      </div>
    </div>
  );
}
