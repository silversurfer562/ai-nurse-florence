/**
 * Shift Handoff Wizard Page
 * Page wrapper for the Shift Handoff Wizard component
 */

import React from 'react';
import { ShiftHandoffWizard } from '@/widgets/ShiftHandoffWizard/ShiftHandoffWizard';

export const ShiftHandoffWizardPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <ShiftHandoffWizard />
    </div>
  );
};

export default ShiftHandoffWizardPage;
