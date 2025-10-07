/**
 * Admission Assessment Wizard Page
 * Page wrapper for the Admission Assessment Wizard component
 */

import React from 'react';
import { AdmissionAssessmentWizard } from '@/widgets/AdmissionAssessmentWizard/AdmissionAssessmentWizard';

export const AdmissionAssessmentWizardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <AdmissionAssessmentWizard />
    </div>
  );
};

export default AdmissionAssessmentWizardPage;
