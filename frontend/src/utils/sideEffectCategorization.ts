/**
 * Side Effect Categorization Utility
 * Categorizes adverse reactions into serious vs common based on text analysis
 */

export interface CategorizedSideEffect {
  description: string;
  severity: 'serious' | 'common' | 'moderate';
}

export interface CategorizedSideEffects {
  serious: string[];
  common: string[];
}

// Keywords that indicate serious/severe side effects
const SERIOUS_KEYWORDS = [
  'fatal',
  'death',
  'life-threatening',
  'severe',
  'serious',
  'emergency',
  'hospitalization',
  'anaphylaxis',
  'anaphylactic',
  'seizure',
  'stroke',
  'heart attack',
  'myocardial infarction',
  'cardiac arrest',
  'respiratory failure',
  'liver failure',
  'kidney failure',
  'renal failure',
  'hepatic failure',
  'suicidal',
  'suicide',
  'coma',
  'bleeding',
  'hemorrhage',
  'stevens-johnson',
  'toxic epidermal necrolysis',
  'agranulocytosis',
  'pancytopenia',
  'thrombocytopenia',
  'neutropenia',
  'aplastic anemia',
  'bone marrow',
  'malignancy',
  'cancer',
  'tumor',
  'neoplasm',
  'hypersensitivity',
  'angioedema',
  'bronchospasm',
  'dyspnea',
  'chest pain',
  'palpitations',
  'arrhythmia',
  'tachycardia',
  'bradycardia',
  'hypertension crisis',
  'hypotension',
  'shock',
  'sepsis',
  'infection',
  'immunosuppression',
  'organ',
  'dysfunction',
  'failure'
];

// Keywords that indicate common/mild side effects
const COMMON_KEYWORDS = [
  'nausea',
  'headache',
  'dizziness',
  'drowsiness',
  'fatigue',
  'dry mouth',
  'constipation',
  'diarrhea',
  'upset stomach',
  'indigestion',
  'gas',
  'bloating',
  'mild',
  'minor',
  'temporary',
  'insomnia',
  'nervousness',
  'anxiety',
  'restlessness',
  'sweating',
  'flushing',
  'rash',
  'itching',
  'muscle pain',
  'joint pain',
  'back pain',
  'weakness',
  'loss of appetite',
  'weight changes',
  'sexual'
];

/**
 * Categorize a single side effect description into serious or common
 */
export function categorizeSideEffect(description: string): 'serious' | 'common' | 'moderate' {
  const lowerDescription = description.toLowerCase();

  // Check for serious keywords
  const hasSeriousKeyword = SERIOUS_KEYWORDS.some(keyword =>
    lowerDescription.includes(keyword)
  );

  if (hasSeriousKeyword) {
    return 'serious';
  }

  // Check for common keywords
  const hasCommonKeyword = COMMON_KEYWORDS.some(keyword =>
    lowerDescription.includes(keyword)
  );

  if (hasCommonKeyword) {
    return 'common';
  }

  // Default to moderate if no clear indicators
  return 'moderate';
}

/**
 * Categorize an array of side effect descriptions
 */
export function categorizeSideEffects(sideEffects: string[]): CategorizedSideEffects {
  const serious: string[] = [];
  const common: string[] = [];

  for (const effect of sideEffects) {
    const category = categorizeSideEffect(effect);

    if (category === 'serious') {
      serious.push(effect);
    } else {
      // Group moderate with common for simpler UI
      common.push(effect);
    }
  }

  return { serious, common };
}

/**
 * Parse severity from interaction text
 */
export function parseInteractionSeverity(description: string): 'major' | 'moderate' | 'minor' {
  const lowerDescription = description.toLowerCase();

  // Major interaction keywords
  const majorKeywords = [
    'contraindicated',
    'avoid',
    'do not',
    'fatal',
    'life-threatening',
    'severe',
    'serious',
    'major',
    'significant',
    'dangerous'
  ];

  // Minor interaction keywords
  const minorKeywords = [
    'minor',
    'mild',
    'slight',
    'minimal',
    'insignificant',
    'unlikely'
  ];

  // Check for major severity
  if (majorKeywords.some(keyword => lowerDescription.includes(keyword))) {
    return 'major';
  }

  // Check for minor severity
  if (minorKeywords.some(keyword => lowerDescription.includes(keyword))) {
    return 'minor';
  }

  // Default to moderate
  return 'moderate';
}
