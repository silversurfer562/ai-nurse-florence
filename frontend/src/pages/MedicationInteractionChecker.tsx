/**
 * Medication Interaction Checker Page
 *
 * Allows users to add multiple medications and check for interactions.
 * Uses consistent MedicationCard component for all medications.
 */

import { useState } from 'react';
import MedicationCard from '../components/MedicationCard';

interface Medication {
  id: string;
  name: string;
  displayName: string;
  prescriptionStatus: 'OTC' | 'Prescription Required';
  dosageForm: string;
  route: string;
  primaryUse?: string;
  whatIsThisFor?: string;
  fdaEnhanced?: boolean;
  manufacturer?: string;
}

export default function MedicationInteractionChecker() {
  const [medications] = useState<Medication[]>([
    {
      id: '1',
      name: 'aspirin',
      displayName: 'Aspirin (Pharbest Regular Strength Aspirin)',
      prescriptionStatus: 'OTC',
      dosageForm: 'TABLET',
      route: 'ORAL',
      whatIsThisFor:
        'Uses for the temporary relief of minor aches and pains or as recommended by your doctor. Because of its delayed action, this product will not provide fast relief of headaches or other symptoms needing...',
      primaryUse:
        'Uses for the temporary relief of minor aches and pains or as recommended by your doctor. Because of its delayed action, this product will not provide fast relief of headaches or other symptoms needing immediate relief. ask your doctor about other uses for safety coated 81 mg aspirin',
      fdaEnhanced: true,
      manufacturer: 'P & L Development, LLC'
    },
    {
      id: '2',
      name: 'warfarin',
      displayName: 'Warfarin (Warfarin Sodium)',
      prescriptionStatus: 'Prescription Required',
      dosageForm: 'TABLET',
      route: 'ORAL',
      whatIsThisFor:
        'Warfarin is used to prevent blood clots from forming or growing larger in your blood and blood vessels. It is prescribed for people with certain types of irregular heartbeat, people with prosthetic (replacement or mechanical) heart valves, and people who have suffered a heart attack.',
      primaryUse:
        'Prevention of blood clots, stroke prevention in atrial fibrillation, treatment of deep vein thrombosis (DVT) and pulmonary embolism (PE)',
      fdaEnhanced: true,
      manufacturer: 'Various manufacturers'
    },
    {
      id: '3',
      name: 'atorvastatin',
      displayName: 'Atorvastatin calcium (ATORVASTATIN CALCIUM)',
      prescriptionStatus: 'Prescription Required',
      dosageForm: 'TABLET, FILM COATED',
      route: 'ORAL',
      whatIsThisFor:
        '1 INDICATIONS AND USAGE Atorvastatin calcium tablets are indicated: To reduce the risk of: Myocardial infarction (MI), stroke, revascularization procedures, and angina in adults with multiple risk fac...',
      primaryUse:
        '1 INDICATIONS AND USAGE Atorvastatin calcium tablets are indicated: To reduce the risk of: Myocardial infarction (MI), stroke, revascularization procedures, and angina in adults with multiple risk factors for coronary heart disease (CHD) or type 2 diabetes mellitus',
      fdaEnhanced: true,
      manufacturer: 'Multiple generic manufacturers'
    }
  ]);

  const [showInteractions, setShowInteractions] = useState(false);

  const handleCheckInteractions = () => {
    setShowInteractions(true);
    // In real implementation, this would call the API
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            <i className="fas fa-flask text-purple-600 mr-3"></i>
            Medication Interaction Checker
          </h1>
          <p className="text-lg text-gray-600">
            Add your medications below and check for potential interactions
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 mb-6">
          <button
            className="flex items-center gap-2 px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            onClick={() => {
              // In real implementation, this would open a medication search modal
              alert('Medication search modal would open here');
            }}
          >
            <i className="fas fa-plus" aria-hidden="true"></i>
            Add Another Medication
          </button>

          <button
            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold shadow-md"
            onClick={handleCheckInteractions}
          >
            <i className="fas fa-check-circle" aria-hidden="true"></i>
            Check for Interactions
          </button>
        </div>

        {/* Medication Information Section */}
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            <i className="fas fa-pills text-blue-600" aria-hidden="true"></i>
            Medication Information
          </h2>

          <div className="grid md:grid-cols-2 gap-4">
            {medications.map((med, index) => (
              <MedicationCard
                key={med.id}
                name={med.name}
                displayName={med.displayName}
                prescriptionStatus={med.prescriptionStatus}
                dosageForm={med.dosageForm}
                route={med.route}
                primaryUse={med.primaryUse}
                whatIsThisFor={med.whatIsThisFor}
                fdaEnhanced={med.fdaEnhanced}
                manufacturer={med.manufacturer}
                defaultExpanded={index === 0} // First card expanded by default
              />
            ))}
          </div>
        </div>

        {/* Interaction Results (shown after clicking "Check for Interactions") */}
        {showInteractions && (
          <div className="card mb-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <i className="fas fa-exclamation-triangle text-orange-600" aria-hidden="true"></i>
              Potential Drug Interactions
            </h2>

            <div className="border-l-4 border-red-500 bg-red-50 rounded-r-lg p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="font-semibold text-lg text-gray-900">
                  <i className="fas fa-exclamation-triangle mr-2 text-red-600"></i>
                  Aspirin + Warfarin
                </div>
                <span className="bg-red-600 text-white px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide">
                  MAJOR
                </span>
              </div>

              <div className="text-sm text-gray-800 mb-3 leading-relaxed">
                <span className="font-semibold">Interaction:</span> Increased risk of bleeding due
                to additive anticoagulant effects
              </div>

              <div className="text-sm text-gray-700 mb-3">
                <span className="font-semibold">Clinical Significance:</span> Significantly
                increased bleeding risk requiring close monitoring
              </div>

              <div className="mt-3 bg-white bg-opacity-50 rounded-lg p-3">
                <div className="text-sm font-semibold text-gray-900 mb-2">
                  <i className="fas fa-stethoscope mr-2" aria-hidden="true"></i>
                  Clinical Recommendations:
                </div>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  <li>Monitor INR closely if combination necessary</li>
                  <li>Consider alternative antiplatelet if appropriate</li>
                  <li>Educate patient on bleeding precautions</li>
                  <li>Consider PPI for GI protection</li>
                </ul>
              </div>

              <div className="flex gap-4 mt-3 text-xs text-gray-600">
                <div>
                  <span className="font-semibold">Evidence:</span> 1A
                </div>
                <div>
                  <span className="font-semibold">Onset:</span> delayed
                </div>
                <div>
                  <span className="font-semibold">Documentation:</span> excellent
                </div>
              </div>
            </div>
          </div>
        )}

        {/* FDA Attribution */}
        <div className="card text-center text-xs text-gray-600">
          <div className="flex items-center justify-center gap-2 mb-2">
            <i className="fas fa-shield-alt text-blue-600" aria-hidden="true"></i>
            <span className="font-semibold">Powered by FDA Data</span>
          </div>
          <p>
            Drug information sourced from the U.S. Food and Drug Administration's National Drug Code
            Directory and OpenFDA databases.
          </p>
        </div>

        {/* Educational Disclaimer */}
        <div className="mt-6 p-4 bg-yellow-50 border-2 border-yellow-300 rounded-lg text-sm text-gray-700">
          <p className="font-semibold mb-2 flex items-center gap-2">
            <i className="fas fa-info-circle text-yellow-600" aria-hidden="true"></i>
            Important Notice
          </p>
          <p>
            This tool is for educational purposes only and does not replace professional medical
            advice. Always consult your healthcare provider or pharmacist about your medications and
            potential interactions.
          </p>
        </div>
      </div>
    </div>
  );
}
