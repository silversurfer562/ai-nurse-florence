import { useState, useEffect } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { drugInteractionService } from '../services/api';
import DrugAutocomplete from '../components/DrugAutocomplete';

export default function DrugInteractions() {
  const { t } = useTranslation();
  const [medications, setMedications] = useState<string[]>(['', '']);
  const [submittedMeds, setSubmittedMeds] = useState<string[]>([]);
  const queryClient = useQueryClient();

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
    <div>
      <h1 className="text-3xl font-bold text-gray-800 mb-6">{t('drugInteractions.title')}</h1>

      <div className="card mb-6">
        <form onSubmit={handleCheck}>
          <div className="mb-4">
            <label className="block text-gray-700 font-medium mb-2">
              {t('drugInteractions.subtitle')}
            </label>

            {medications.map((med, index) => (
              <div key={index} className="flex space-x-2 mb-2">
                <div className="flex-1">
                  <DrugAutocomplete
                    value={med}
                    onChange={(value) => updateMedication(index, value)}
                    placeholder={t('drugInteractions.searchPlaceholder')}
                    className="w-full"
                  />
                </div>
                {medications.length > 2 && (
                  <button
                    type="button"
                    onClick={() => removeMedication(index)}
                    className="btn-secondary"
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
              Add Medication
            </button>
          </div>

          <button type="submit" className="btn-primary">
            <i className="fas fa-check-circle mr-2"></i>
            {t('drugInteractions.checkButton')}
          </button>
        </form>
      </div>

      {isLoading && (
        <div className="bg-blue-100 border border-blue-400 text-blue-800 px-4 py-3 rounded-lg">
          <i className="fas fa-spinner fa-spin mr-2"></i>
          Checking drug interactions...
        </div>
      )}

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-800 px-4 py-3 rounded-lg">
          <i className="fas fa-exclamation-circle mr-2"></i>
          Error checking drug interactions. Please try again.
        </div>
      )}

      {data && (
        <>
          {/* Drug Information Section */}
          {data.data?.drug_information && data.data.drug_information.length > 0 && (
            <div className="card">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">
                <i className="fas fa-pills mr-2"></i>
                Medication Information
              </h2>
              <div className="space-y-6">
                {data.data.drug_information.map((drug: any, index: number) => (
                  <div key={index} className="border-l-4 border-blue-500 pl-4 py-2">
                    <div className="font-semibold text-gray-800 text-lg">
                      {drug.name}
                      {drug.brand_names && drug.brand_names.length > 0 && (
                        <span className="text-sm font-normal text-gray-600 ml-2">
                          ({drug.brand_names.join(', ')})
                        </span>
                      )}
                    </div>

                    {drug.drug_class && (
                      <div className="text-sm text-gray-600 mt-1">
                        <span className="font-medium">Class:</span> {drug.drug_class}
                      </div>
                    )}

                    {drug.indication && (
                      <div className="text-sm text-gray-700 mt-2">
                        <span className="font-medium">Used for:</span> {drug.indication}
                      </div>
                    )}

                    {drug.nursing_considerations && drug.nursing_considerations.length > 0 && (
                      <div className="mt-2">
                        <div className="text-sm font-semibold text-gray-700">Nursing Considerations:</div>
                        <ul className="list-disc list-inside text-sm text-gray-600">
                          {drug.nursing_considerations.map((consideration: string, idx: number) => (
                            <li key={idx}>{consideration}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {drug.common_side_effects && drug.common_side_effects.length > 0 && (
                      <div className="mt-2">
                        <div className="text-sm font-semibold text-gray-700">Common Side Effects:</div>
                        <ul className="list-disc list-inside text-sm text-gray-600">
                          {drug.common_side_effects.map((effect: string, idx: number) => (
                            <li key={idx}>{effect}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {drug.warnings && drug.warnings.length > 0 && (
                      <div className="mt-2">
                        <div className="text-sm font-semibold text-red-700">
                          <i className="fas fa-exclamation-triangle mr-1"></i>
                          Warnings:
                        </div>
                        <ul className="list-disc list-inside text-sm text-red-600">
                          {drug.warnings.map((warning: string, idx: number) => (
                            <li key={idx}>{warning}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Drug Interactions Section */}
          <div className="card">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              <i className="fas fa-flask mr-2"></i>
              Drug Interactions
            </h2>

            {data.data?.interactions && data.data.interactions.length > 0 ? (
              <div className="space-y-4">
                {data.data.interactions.map((interaction: any, index: number) => {
                  // Determine severity colors and styles
                  const severity = (interaction.severity || 'unknown').toLowerCase();
                  let borderColor = 'border-gray-400';
                  let bgColor = 'bg-gray-50';
                  let textColor = 'text-gray-800';
                  let badgeBg = 'bg-gray-100';
                  let badgeText = 'text-gray-800';
                  let icon = 'fa-info-circle';

                  if (severity === 'contraindicated') {
                    borderColor = 'border-red-600';
                    bgColor = 'bg-red-50';
                    textColor = 'text-red-900';
                    badgeBg = 'bg-red-600';
                    badgeText = 'text-white';
                    icon = 'fa-ban';
                  } else if (severity === 'major') {
                    borderColor = 'border-red-500';
                    bgColor = 'bg-red-50';
                    textColor = 'text-red-800';
                    badgeBg = 'bg-red-500';
                    badgeText = 'text-white';
                    icon = 'fa-exclamation-triangle';
                  } else if (severity === 'moderate') {
                    borderColor = 'border-orange-500';
                    bgColor = 'bg-orange-50';
                    textColor = 'text-orange-800';
                    badgeBg = 'bg-orange-500';
                    badgeText = 'text-white';
                    icon = 'fa-exclamation-circle';
                  } else if (severity === 'minor') {
                    borderColor = 'border-yellow-500';
                    bgColor = 'bg-yellow-50';
                    textColor = 'text-yellow-800';
                    badgeBg = 'bg-yellow-500';
                    badgeText = 'text-white';
                    icon = 'fa-info-circle';
                  }

                  return (
                    <div key={index} className={`border-l-4 ${borderColor} ${bgColor} rounded-r-lg p-4`}>
                      {/* Header with drug names and severity badge */}
                      <div className="flex items-start justify-between mb-3">
                        <div className="font-semibold text-lg text-gray-900">
                          <i className={`fas ${icon} mr-2 ${textColor}`}></i>
                          {interaction.drug1} + {interaction.drug2}
                        </div>
                        <span className={`${badgeBg} ${badgeText} px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wide`}>
                          {interaction.severity || 'Unknown'}
                        </span>
                      </div>

                      {/* Interaction description */}
                      {interaction.description && (
                        <div className="text-sm text-gray-800 mb-3 leading-relaxed">
                          <span className="font-semibold">Interaction:</span> {interaction.description}
                        </div>
                      )}

                      {/* Clinical significance */}
                      {interaction.clinical_significance && (
                        <div className="text-sm text-gray-700 mb-3">
                          <span className="font-semibold">Clinical Significance:</span> {interaction.clinical_significance}
                        </div>
                      )}

                      {/* Mechanism */}
                      {interaction.mechanism && (
                        <div className="text-sm text-gray-700 mb-3">
                          <span className="font-semibold">Mechanism:</span> {interaction.mechanism}
                        </div>
                      )}

                      {/* Recommendations */}
                      {interaction.recommendations && interaction.recommendations.length > 0 && (
                        <div className="mt-3 bg-white bg-opacity-50 rounded-lg p-3">
                          <div className="text-sm font-semibold text-gray-900 mb-2">
                            <i className="fas fa-stethoscope mr-2"></i>
                            Clinical Recommendations:
                          </div>
                          <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                            {interaction.recommendations.map((rec: string, idx: number) => (
                              <li key={idx}>{rec}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Evidence level and onset if available */}
                      <div className="flex gap-4 mt-3 text-xs text-gray-600">
                        {interaction.evidence_level && (
                          <div>
                            <span className="font-semibold">Evidence:</span> {interaction.evidence_level}
                          </div>
                        )}
                        {interaction.onset && (
                          <div>
                            <span className="font-semibold">Onset:</span> {interaction.onset}
                          </div>
                        )}
                        {interaction.documentation && (
                          <div>
                            <span className="font-semibold">Documentation:</span> {interaction.documentation}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="space-y-3">
                <div className="text-gray-600 mb-3">
                  <i className="fas fa-check-circle text-green-500 mr-2"></i>
                  No significant interactions detected between the entered medications.
                </div>
                {data.data?.drugs_checked && data.data.drugs_checked.length > 0 && (
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="text-sm font-semibold text-gray-700 mb-2">Medications Checked:</div>
                    <div className="space-y-1">
                      {data.data.drugs_checked.map((drug: string, idx: number) => (
                        <div key={idx} className="text-sm text-gray-700">
                          <i className="fas fa-pill text-green-600 mr-2"></i>
                          <span className="font-medium">{drug}</span> - No interactions detected with other medications in this list
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {data.data?.service_note && (
              <div className="mt-4 text-xs text-gray-500 italic">
                {data.data.service_note}
              </div>
            )}
          </div>
        </>
      )}

      {!data && !isLoading && (
        <div className="bg-blue-100 border border-blue-400 text-blue-800 px-4 py-3 rounded-lg">
          <i className="fas fa-info-circle mr-2"></i>
          This feature checks for drug-drug interactions using live medical databases.
        </div>
      )}
    </div>
  );
}