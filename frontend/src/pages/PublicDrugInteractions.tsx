import { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { drugInteractionService } from '../services/api';
import DrugAutocomplete from '../components/DrugAutocomplete';
import ExpandableSection from '../components/ExpandableSection';
import MedicationCard from '../components/MedicationCard';
import { WarningBox, FDAAttribution } from '../components/FDAWarnings';

/**
 * Public Drug Interaction Checker
 *
 * Free community service providing drug interaction checking to the public.
 * This tool helps fill the gap left by the discontinued NIH Drug Interaction API.
 *
 * No authentication required - accessible to everyone.
 */

export default function PublicDrugInteractions() {
  const [medications, setMedications] = useState<string[]>(['', '']);
  const [submittedMeds, setSubmittedMeds] = useState<string[]>([]);
  const queryClient = useQueryClient();

  // Helper function to capitalize drug names properly
  const capitalizeDrugName = (name: string): string => {
    if (!name) return '';
    return name.charAt(0).toUpperCase() + name.slice(1).toLowerCase();
  };

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['drug-interactions', submittedMeds],
    queryFn: () => drugInteractionService.check(submittedMeds),
    enabled: false,
  });

  // Reset form and clear results when component mounts
  useEffect(() => {
    setMedications(['', '']);
    setSubmittedMeds([]);
    queryClient.removeQueries({ queryKey: ['drug-interactions'] });
  }, [queryClient]);

  const addMedication = () => {
    setMedications([...medications, '']);
  };

  const removeMedication = (index: number) => {
    const newMeds = medications.filter((_, i) => i !== index);
    setMedications(newMeds);
  };

  const updateMedication = (index: number, value: string) => {
    const newMeds = [...medications];
    newMeds[index] = value;
    setMedications(newMeds);
  };

  const handleCheck = (e: React.FormEvent) => {
    e.preventDefault();
    const validMeds = medications.filter(med => med.trim() !== '');
    if (validMeds.length < 2) {
      alert('Please enter at least 2 medications');
      return;
    }
    setSubmittedMeds(validMeds);
    refetch();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">

        {/* Hero Section */}
        <div className="text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            <i className="fas fa-pills text-blue-600 mr-3"></i>
            Free Drug Interaction Checker
          </h1>
          <p className="text-xl text-gray-600 mb-2">
            A Public Service by AI Nurse Florence
          </p>
          <p className="text-gray-500 mb-4">
            Check medication interactions instantly - No login required
          </p>

          {/* FDA Data Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 border-2 border-blue-200 rounded-lg">
            <i className="fas fa-shield-alt text-blue-600" aria-hidden="true"></i>
            <span className="text-sm font-semibold text-blue-900">Powered by FDA Data</span>
            <span className="text-xs text-blue-700">|</span>
            <span className="text-xs text-blue-700">U.S. Food & Drug Administration</span>
          </div>
        </div>


        {/* Main Tool Card */}
        <div className="card mb-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">
            Check Your Medications
          </h2>

          <form onSubmit={handleCheck}>
            <div className="mb-4">
              <label className="block text-gray-700 font-medium mb-3">
                Enter at least 2 medications to check for interactions:
              </label>

              {medications.map((med, index) => (
                <div key={index} className="flex space-x-2 mb-3">
                  <div className="flex-1">
                    <DrugAutocomplete
                      value={med}
                      onChange={(value) => updateMedication(index, value)}
                      placeholder={`Medication ${index + 1} (e.g., Aspirin, Metformin, Lisinopril)`}
                      className="w-full"
                    />
                  </div>
                  {medications.length > 2 && (
                    <button
                      type="button"
                      onClick={() => removeMedication(index)}
                      className="btn-secondary"
                      aria-label={`Remove medication ${index + 1}`}
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  )}
                </div>
              ))}

              <button
                type="button"
                onClick={addMedication}
                className="btn-secondary mt-2"
              >
                <i className="fas fa-plus mr-2"></i>
                Add Another Medication
              </button>
            </div>

            <button type="submit" className="btn-primary" disabled={isLoading}>
              {isLoading ? (
                <>
                  <i className="fas fa-spinner fa-spin mr-2"></i>
                  Checking Interactions...
                </>
              ) : (
                <>
                  <i className="fas fa-check-circle mr-2"></i>
                  Check for Interactions
                </>
              )}
            </button>
          </form>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="bg-blue-100 border border-blue-400 text-blue-800 px-4 py-3 rounded-lg mb-6">
            <i className="fas fa-spinner fa-spin mr-2"></i>
            Checking drug interactions...
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-800 px-4 py-3 rounded-lg mb-6">
            <i className="fas fa-exclamation-circle mr-2"></i>
            Error checking drug interactions. Please try again or contact support if the problem persists.
          </div>
        )}

        {/* Results */}
        {data && (
          <>
            {/* Drug Information Section */}
            {data.data?.drug_information && data.data.drug_information.length > 0 && (
              <div className="card mb-6">
                <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                  <i className="fas fa-pills text-blue-600 mr-2"></i>
                  Medication Information
                </h2>
                <div className="grid lg:grid-cols-2 gap-4 lg:items-start">
                  {data.data.drug_information.map((drug: any, index: number) => (
                    <MedicationCard
                      key={index}
                      name={drug.name}
                      displayName={`${capitalizeDrugName(drug.name)}${drug.brand_names && drug.brand_names.length > 0 ? ` (${drug.brand_names.join(', ')})` : ''}`}
                      prescriptionStatus={
                        drug.product_type?.includes('OTC')
                          ? 'OTC'
                          : 'Prescription Required'
                      }
                      dosageForm={drug.dosage_form || 'Unknown Form'}
                      route={drug.route || 'Unknown Route'}
                      primaryUse={drug.indication}
                      whatIsThisFor={
                        drug.indication
                          ? drug.indication.length > 200
                            ? drug.indication.substring(0, 200) + '...'
                            : drug.indication
                          : undefined
                      }
                      fdaEnhanced={drug.fda_data_available}
                      manufacturer={drug.manufacturer}
                      defaultExpanded={true}
                      className="h-full"
                    >
                      {/* Drug Class Info */}
                      {drug.drug_class && (
                        <div className="p-3 bg-blue-50 rounded-lg mb-4">
                          <div className="text-xs font-semibold text-blue-700 mb-1">Drug Class</div>
                          <div className="text-sm text-gray-800">{drug.drug_class}</div>
                        </div>
                      )}

                      {/* Side Effects */}
                      {drug.common_side_effects && drug.common_side_effects.length > 0 && (
                        <WarningBox severity="moderate" title="Common Side Effects">
                          <ul className="grid md:grid-cols-2 gap-2">
                            {drug.common_side_effects.map((effect: string, idx: number) => (
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
                            {drug.warnings.map((warning: string, idx: number) => (
                              <li key={idx} className="flex items-start gap-2 text-sm">
                                <i className="fas fa-exclamation-triangle text-orange-600 mt-1 flex-shrink-0"></i>
                                <span>{warning}</span>
                              </li>
                            ))}
                          </ul>
                        </WarningBox>
                      )}

                      {/* FDA Black Box Warning (MOST CRITICAL) */}
                      {drug.boxed_warning && (
                        <WarningBox severity="critical" title="⚠️ FDA BLACK BOX WARNING">
                          <div className="text-sm whitespace-pre-wrap">{drug.boxed_warning}</div>
                        </WarningBox>
                      )}

                      {/* FDA Contraindications */}
                      {drug.contraindications_fda && (
                        <ExpandableSection
                          title="FDA Contraindications"
                          icon="fa-ban"
                          variant="critical"
                          defaultExpanded={false}
                        >
                          <div className="text-sm whitespace-pre-wrap text-gray-700">{drug.contraindications_fda}</div>
                        </ExpandableSection>
                      )}

                      {/* FDA Warnings and Cautions */}
                      {drug.warnings_fda && (
                        <ExpandableSection
                          title="FDA Warnings and Cautions"
                          icon="fa-exclamation-triangle"
                          variant="warning"
                          defaultExpanded={false}
                        >
                          <div className="text-sm whitespace-pre-wrap text-gray-700">{drug.warnings_fda}</div>
                        </ExpandableSection>
                      )}

                      {/* FDA Adverse Reactions */}
                      {drug.adverse_reactions_fda && (
                        <ExpandableSection
                          title="FDA Adverse Reactions"
                          icon="fa-heartbeat"
                          variant="warning"
                          defaultExpanded={false}
                        >
                          <div className="text-sm whitespace-pre-wrap text-gray-700">{drug.adverse_reactions_fda}</div>
                        </ExpandableSection>
                      )}

                      {/* FDA Drug Interactions */}
                      {drug.drug_interactions_fda && (
                        <ExpandableSection
                          title="FDA Drug Interactions"
                          icon="fa-flask"
                          variant="info"
                          defaultExpanded={false}
                        >
                          <div className="text-sm whitespace-pre-wrap text-gray-700">{drug.drug_interactions_fda}</div>
                        </ExpandableSection>
                      )}

                      {/* FDA Special Populations */}
                      {drug.special_populations && (
                        <ExpandableSection
                          title="Use in Special Populations"
                          icon="fa-users"
                          variant="info"
                          defaultExpanded={false}
                        >
                          <div className="text-sm whitespace-pre-wrap text-gray-700">{drug.special_populations}</div>
                        </ExpandableSection>
                      )}
                    </MedicationCard>
                  ))}
                </div>
              </div>
            )}

            {/* Drug Interactions Section */}
            <div className="card mb-6">
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">
                <i className="fas fa-flask mr-2 text-purple-600"></i>
                Drug Interactions
              </h2>

              {data.data?.interactions && data.data.interactions.length > 0 ? (
                <div className="space-y-4">
                  {data.data.interactions.map((interaction: any, index: number) => {
                    const severityColors = {
                      high: 'bg-red-100 border-red-500 text-red-800',
                      moderate: 'bg-yellow-100 border-yellow-500 text-yellow-800',
                      low: 'bg-blue-100 border-blue-500 text-blue-800',
                    };

                    const severityColor = severityColors[interaction.severity?.toLowerCase() as keyof typeof severityColors]
                      || 'bg-gray-100 border-gray-500 text-gray-800';

                    return (
                      <div key={index} className={`border-l-4 p-4 rounded-r-lg ${severityColor}`}>
                        <div className="flex items-start justify-between mb-2">
                          <div className="font-semibold text-lg">
                            {capitalizeDrugName(interaction.drug1)} + {capitalizeDrugName(interaction.drug2)}
                          </div>
                          {interaction.severity && (
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                              interaction.severity.toLowerCase() === 'high' ? 'bg-red-200 text-red-800' :
                              interaction.severity.toLowerCase() === 'moderate' ? 'bg-yellow-200 text-yellow-800' :
                              'bg-blue-200 text-blue-800'
                            }`}>
                              {interaction.severity.charAt(0).toUpperCase() + interaction.severity.slice(1).toLowerCase()} Severity
                            </span>
                          )}
                        </div>

                        <div className="text-sm mt-2">
                          <strong>Interaction:</strong> {interaction.description}
                        </div>

                        {interaction.clinical_effects && (
                          <div className="text-sm mt-2">
                            <strong>Clinical Effects:</strong> {interaction.clinical_effects}
                          </div>
                        )}

                        {interaction.management && (
                          <div className="text-sm mt-2">
                            <strong>Management:</strong> {interaction.management}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-r-lg">
                  <div className="flex items-center">
                    <i className="fas fa-check-circle text-green-600 text-2xl mr-3"></i>
                    <div>
                      <div className="font-semibold text-green-800">No Known Interactions Found</div>
                      <div className="text-sm text-green-700 mt-1">
                        Based on available data, no significant interactions were identified between these medications.
                        However, always consult your healthcare provider about your specific situation.
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* FDA Attribution */}
            <div className="mt-6">
              <FDAAttribution />
            </div>

            {/* Important Medical Disclaimer - shown after results */}
            <div className="bg-yellow-50 border-l-4 border-yellow-600 p-6 rounded-r-lg mt-6">
              <h3 className="text-lg font-semibold text-yellow-900 mb-3">
                <i className="fas fa-exclamation-triangle mr-2"></i>
                Important Medical Disclaimer
              </h3>
              <div className="text-sm text-yellow-800 space-y-2">
                <p>
                  <strong>This tool is for informational and educational purposes only.</strong> It is not a substitute for
                  professional medical advice, diagnosis, or treatment.
                </p>
                <p>
                  <strong>Always consult your healthcare provider</strong> about your medications, potential interactions,
                  and any health concerns. Do not start, stop, or change medications without medical supervision.
                </p>
                <p>
                  <strong>In case of emergency,</strong> call 911 or your local emergency services immediately.
                </p>
                <p className="text-xs mt-3 font-medium">
                  By using this tool, you acknowledge that you understand these limitations and will consult appropriate
                  healthcare professionals for medical decisions.
                </p>
              </div>
            </div>

            {/* Mission Statement - shown after results */}
            <div className="bg-blue-50 border-l-4 border-blue-600 p-6 rounded-r-lg mt-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-3">
                <i className="fas fa-heart mr-2"></i>
                Our Mission: Serving the Healthcare Community
              </h3>
              <div className="text-sm text-blue-800 space-y-2">
                <p>
                  When the NIH Drug Interaction API was discontinued, the healthcare community lost a valuable public resource.
                  We're providing this free tool to help fill that gap and serve patients, caregivers, and healthcare consumers.
                </p>
                <p>
                  AI Nurse Florence is a clinical decision support platform designed to help nurses work more efficiently
                  and deliver better patient care. This free public tool is part of our commitment to serving the healthcare
                  community and advancing accessible health technology.
                </p>
                {/* Uncomment link once SSL is fixed
                <p className="mt-3">
                  <a href="https://ainurseflorence.com" className="text-blue-600 hover:text-blue-800 underline font-medium">
                    Learn more about AI Nurse Florence →
                  </a>
                </p>
                */}
              </div>
            </div>
          </>
        )}

        {/* Data Attribution & About Section */}
        <div className="bg-gray-50 rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            <i className="fas fa-info-circle mr-2 text-blue-600"></i>
            About This Tool
          </h2>

          <div className="space-y-4 text-gray-700">
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">
                <i className="fas fa-shield-alt text-blue-600 mr-2"></i>
                Data Sources & Attribution
              </h3>
              <p className="text-sm">
                <strong>Powered by FDA Data:</strong> This tool uses authoritative drug information from the U.S. Food & Drug Administration (FDA)
                databases, combined with clinical pharmacology references and medical literature. All FDA data is sourced directly
                from official government databases, ensuring you receive the most reliable drug interaction information available.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-800 mb-2">How It Works</h3>
              <p className="text-sm">
                Our interaction checker analyzes the medications you enter against comprehensive FDA drug databases.
                It identifies potential interactions, assesses their severity, and provides clinical context to help you
                make informed decisions in consultation with your healthcare provider.
              </p>
            </div>

            <div>
              <h3 className="font-semibold text-gray-800 mb-2">Privacy & Security</h3>
              <p className="text-sm">
                <strong>Your privacy matters:</strong> No personal health information is stored. All searches are processed
                in real-time and session data is automatically cleared. This tool is HIPAA-aware and designed with privacy
                as a core principle.
              </p>
            </div>

          </div>
        </div>

        {/* Help & Support */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            <i className="fas fa-question-circle mr-2 text-green-600"></i>
            Need Help?
          </h2>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">How to Use This Tool</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Enter at least 2 medications (generic or brand names)</li>
                <li>• Use autocomplete suggestions for accuracy</li>
                <li>• Add more medications as needed</li>
                <li>• Review interaction results and severity levels</li>
                <li>• Discuss findings with your healthcare provider</li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold text-gray-800 mb-2">When to Seek Medical Help</h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• You experience unexpected side effects</li>
                <li>• High severity interactions are identified</li>
                <li>• You're starting a new medication</li>
                <li>• You have questions about your medications</li>
                <li>• Medical emergency: Call 911 immediately</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <div className="mb-4">
            <a
              href="/app"
              className="inline-block px-4 py-2 text-sm text-blue-600 hover:text-blue-800 border border-blue-300 hover:border-blue-500 rounded-lg transition-colors"
            >
              <i className="fas fa-laptop-medical mr-2"></i>
              Access Full Clinical Platform (Beta) →
            </a>
          </div>
          <div className="text-sm text-gray-500">
            <p>
              Free Public Service by AI Nurse Florence |
              <a href="/" className="text-blue-600 hover:text-blue-800 ml-1">ainurseflorence.com</a>
            </p>
            <p className="mt-2">
              Helping fill the gap left by discontinued public health tools | Inspiring accessible healthcare technology
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
