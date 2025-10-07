/**
 * SOAP Note Wizard Page
 * Page wrapper for the SOAP Note Wizard component
 */

import React from 'react';
import { SoapNoteWizard } from '@/widgets/SoapNoteWizard/SoapNoteWizard';

export const SoapNoteWizardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <SoapNoteWizard />
    </div>
  );
};

export default SoapNoteWizardPage;
