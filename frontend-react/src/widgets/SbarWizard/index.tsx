/**
 * SBAR Wizard Widget Entry Point
 * Exports standalone widget for embedding in HTML pages
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import SbarWizard from './SbarWizard';
import '../../index.css';

// Export component for use in other React apps
export { SbarWizard };

// Mount function for standalone widget
export function mountSbarWizard(elementId: string = 'sbar-wizard-root') {
  const element = document.getElementById(elementId);

  if (!element) {
    console.error(`Element with id "${elementId}" not found`);
    return null;
  }

  const root = ReactDOM.createRoot(element);
  root.render(
    <React.StrictMode>
      <SbarWizard />
    </React.StrictMode>
  );

  return root;
}

// Auto-mount if element exists on page load
if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => {
    const element = document.getElementById('sbar-wizard-root');
    if (element) {
      mountSbarWizard();
    }
  });
}

// Expose to window for legacy integration
if (typeof window !== 'undefined') {
  (window as any).AINurseWidgets = {
    ...(window as any).AINurseWidgets,
    mountSbarWizard,
    SbarWizard,
  };
}
