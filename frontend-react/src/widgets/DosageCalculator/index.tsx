/**
 * Dosage Calculator Widget Entry Point
 * Placeholder for future implementation
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import '../../index.css';

const DosageCalculator: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="card">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Dosage Calculator
        </h1>
        <p className="text-gray-600">
          Coming soon: AI-powered dosage calculation widget
        </p>
      </div>
    </div>
  );
};

export function mountDosageCalculator(elementId: string = 'dosage-calculator-root') {
  const element = document.getElementById(elementId);

  if (!element) {
    console.error(`Element with id "${elementId}" not found`);
    return null;
  }

  const root = ReactDOM.createRoot(element);
  root.render(
    <React.StrictMode>
      <DosageCalculator />
    </React.StrictMode>
  );

  return root;
}

// Auto-mount if element exists
if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => {
    const element = document.getElementById('dosage-calculator-root');
    if (element) {
      mountDosageCalculator();
    }
  });
}

// Expose to window
if (typeof window !== 'undefined') {
  (window as any).AINurseWidgets = {
    ...(window as any).AINurseWidgets,
    mountDosageCalculator,
    DosageCalculator,
  };
}

export default DosageCalculator;
