/**
 * Drug Interaction Demo Page
 *
 * Demonstrates the polished drug interaction display with sample data
 * showing all the useful clinical information we provide.
 */

import MedicationCard from '../components/MedicationCard';
import { WarningBox, FDAAttribution } from '../components/FDAWarnings';

export default function DrugInteractionDemo() {
  // Sample data matching actual API response structure
  const sampleData = {
    drugs_checked: ['aspirin', 'warfarin'],
    drug_information: [
      {
        name: 'aspirin',
        brand_names: ['Bayer', 'Ecotrin'],
        drug_class: 'antiplatelet',
        indication: 'Pain relief, fever reduction, cardiovascular protection',
        route: 'oral',
        common_side_effects: ['Stomach upset', 'Heartburn', 'Nausea', 'Easy bruising'],
        warnings: ['Risk of bleeding', 'Stomach ulcers', 'Not for children with viral infections (Reye syndrome)']
      },
      {
        name: 'warfarin',
        brand_names: ['Coumadin', 'Jantoven'],
        drug_class: 'anticoagulant',
        indication: 'Prevention of blood clots, stroke prevention in atrial fibrillation',
        route: 'oral',
        common_side_effects: ['Bleeding', 'Bruising', 'Hair loss', 'Skin rash'],
        warnings: ['Regular INR monitoring required', 'Bleeding risk', 'Many drug and food interactions'],
        nursing_considerations: [
          'Monitor INR levels regularly',
          'Educate patient on dietary vitamin K consistency',
          'Assess for signs of bleeding',
          'Review all medications for interactions'
        ]
      }
    ],
    interactions: [
      {
        drug1: 'aspirin',
        drug2: 'warfarin',
        severity: 'major',
        mechanism: 'pharmacodynamic',
        description: 'Increased risk of bleeding due to additive anticoagulant effects',
        clinical_significance: 'Significantly increased bleeding risk requiring close monitoring',
        recommendations: [
          'Monitor INR closely if combination necessary',
          'Consider alternative antiplatelet if appropriate',
          'Educate patient on bleeding precautions',
          'Consider PPI for GI protection'
        ],
        evidence_level: '1A',
        onset: 'delayed',
        documentation: 'excellent'
      }
    ]
  };

  // Helper to get severity colors
  const getSeverityColors = (severity: string) => {
    const sev = severity.toLowerCase();
    if (sev === 'contraindicated') {
      return {
        border: 'border-red-600',
        bg: 'bg-red-50',
        text: 'text-red-900',
        badge: 'bg-red-600 text-white',
        icon: 'fa-ban'
      };
    } else if (sev === 'major' || sev === 'high' || sev === 'severe') {
      return {
        border: 'border-red-500',
        bg: 'bg-red-50',
        text: 'text-red-800',
        badge: 'bg-red-500 text-white',
        icon: 'fa-exclamation-triangle'
      };
    } else if (sev === 'moderate' || sev === 'medium') {
      return {
        border: 'border-orange-500',
        bg: 'bg-orange-50',
        text: 'text-orange-800',
        badge: 'bg-orange-500 text-white',
        icon: 'fa-exclamation-circle'
      };
    } else if (sev === 'minor' || sev === 'low') {
      return {
        border: 'border-yellow-500',
        bg: 'bg-yellow-50',
        text: 'text-yellow-800',
        badge: 'bg-yellow-500 text-white',
        icon: 'fa-info-circle'
      };
    }
    return {
      border: 'border-gray-400',
      bg: 'bg-gray-50',
      text: 'text-gray-800',
      badge: 'bg-gray-100 text-gray-800',
      icon: 'fa-info-circle'
    };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8">
      <div className="container mx-auto px-4 max-w-6xl">

        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            <i className="fas fa-flask text-purple-600 mr-3"></i>
            Drug Interaction Demo
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            Example: Aspirin + Warfarin Interaction
          </p>
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 border-2 border-blue-200 rounded-lg">
            <i className="fas fa-shield-alt text-blue-600"></i>
            <span className="text-sm font-semibold text-blue-900">Powered by FDA Data</span>
          </div>
        </div>

        {/* Medication Information Section */}
        <div className="card mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            <i className="fas fa-pills text-blue-600 mr-2"></i>
            Medication Information
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {sampleData.drug_information.map((drug, index) => (
              <MedicationCard
                key={index}
                name={drug.name}
                displayName={`${drug.name.charAt(0).toUpperCase() + drug.name.slice(1)}${drug.brand_names.length > 0 ? ` (${drug.brand_names.join(', ')})` : ''}`}
                prescriptionStatus={drug.name === 'aspirin' ? 'OTC' : 'Prescription Required'}
                dosageForm="TABLET"
                route={drug.route}
                primaryUse={drug.indication}
                whatIsThisFor={drug.indication}
                fdaEnhanced={true}
                manufacturer="Sample Manufacturer"
                defaultExpanded={true}
              >
                {/* Drug Class */}
                <div className="p-3 bg-blue-50 rounded-lg mb-4">
                  <div className="text-xs font-semibold text-blue-700 mb-1">Drug Class</div>
                  <div className="text-sm text-gray-800">{drug.drug_class}</div>
                </div>

                {/* Nursing Considerations */}
                {drug.nursing_considerations && drug.nursing_considerations.length > 0 && (
                  <WarningBox severity="info" title="Nursing Considerations">
                    <ul className="list-disc list-inside space-y-1">
                      {drug.nursing_considerations.map((consideration, idx) => (
                        <li key={idx} className="text-sm">{consideration}</li>
                      ))}
                    </ul>
                  </WarningBox>
                )}

                {/* Side Effects */}
                {drug.common_side_effects && drug.common_side_effects.length > 0 && (
                  <WarningBox severity="moderate" title="Common Side Effects">
                    <ul className="grid md:grid-cols-2 gap-2">
                      {drug.common_side_effects.map((effect, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <i className="fas fa-circle text-yellow-600 text-xs mt-1.5 flex-shrink-0"></i>
                          <span>{effect}</span>
                        </li>
                      ))}
                    </ul>
                  </WarningBox>
                )}

                {/* Warnings */}
                {drug.warnings && drug.warnings.length > 0 && (
                  <WarningBox severity="major" title="Important Warnings">
                    <ul className="space-y-2">
                      {drug.warnings.map((warning, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm">
                          <i className="fas fa-exclamation-triangle text-orange-600 mt-1 flex-shrink-0"></i>
                          <span>{warning}</span>
                        </li>
                      ))}
                    </ul>
                  </WarningBox>
                )}
              </MedicationCard>
            ))}
          </div>
        </div>

        {/* Drug Interactions Section */}
        <div className="card mb-6">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">
            <i className="fas fa-flask text-purple-600 mr-2"></i>
            Drug Interactions
          </h2>

          <div className="space-y-4">
            {sampleData.interactions.map((interaction, index) => {
              const colors = getSeverityColors(interaction.severity);

              return (
                <div key={index} className={`border-l-4 ${colors.border} ${colors.bg} rounded-r-lg p-4`}>
                  {/* Header with drug names and severity badge */}
                  <div className="flex items-start justify-between mb-3">
                    <div className="font-semibold text-lg text-gray-900">
                      <i className={`fas ${colors.icon} mr-2 ${colors.text}`}></i>
                      {interaction.drug1.charAt(0).toUpperCase() + interaction.drug1.slice(1)} + {interaction.drug2.charAt(0).toUpperCase() + interaction.drug2.slice(1)}
                    </div>
                    <span className={`${colors.badge} px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide`}>
                      {interaction.severity}
                    </span>
                  </div>

                  {/* Interaction description */}
                  <div className="text-sm text-gray-800 mb-3 leading-relaxed">
                    <span className="font-semibold">Interaction:</span> {interaction.description}
                  </div>

                  {/* Clinical significance */}
                  <div className="text-sm text-gray-700 mb-3">
                    <span className="font-semibold">Clinical Significance:</span> {interaction.clinical_significance}
                  </div>

                  {/* Mechanism */}
                  <div className="text-sm text-gray-700 mb-3">
                    <span className="font-semibold">Mechanism:</span> {interaction.mechanism}
                  </div>

                  {/* Recommendations */}
                  <div className="mt-3 bg-white bg-opacity-50 rounded-lg p-3">
                    <div className="text-sm font-semibold text-gray-900 mb-2">
                      <i className="fas fa-stethoscope mr-2"></i>
                      Clinical Recommendations:
                    </div>
                    <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                      {interaction.recommendations.map((rec, idx) => (
                        <li key={idx}>{rec}</li>
                      ))}
                    </ul>
                  </div>

                  {/* Evidence level and onset */}
                  <div className="flex gap-4 mt-3 text-xs text-gray-600">
                    <div>
                      <span className="font-semibold">Evidence:</span> {interaction.evidence_level}
                    </div>
                    <div>
                      <span className="font-semibold">Onset:</span> {interaction.onset}
                    </div>
                    <div>
                      <span className="font-semibold">Documentation:</span> {interaction.documentation}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* FDA Attribution */}
        <FDAAttribution />

        {/* Color Coding Legend */}
        <div className="card mt-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Severity Color Coding</h3>
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 bg-red-600 rounded"></div>
              <span className="text-sm"><strong>Contraindicated/Major:</strong> Do not use together or requires close monitoring</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 bg-orange-500 rounded"></div>
              <span className="text-sm"><strong>Moderate:</strong> Use with caution, monitoring recommended</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-4 h-4 bg-yellow-500 rounded"></div>
              <span className="text-sm"><strong>Minor:</strong> Usually safe, minimal clinical impact</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
