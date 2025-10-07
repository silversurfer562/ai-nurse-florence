/**
 * Medication Template Component
 *
 * Example template showing how to combine ExpandableSection and FDAWarnings
 * to create beautifully formatted, data-driven medication guides.
 *
 * This demonstrates the "pages as templates" approach with FDA data widgets.
 */

import ExpandableSection, { WarningSection, CriticalWarningSection, InfoSection } from './ExpandableSection';
import {
  Contraindications,
  Warnings,
  AdverseReactions,
  DrugInteractions,
  FDAAttribution,
  SafetyBadge,
  WarningBox
} from './FDAWarnings';
import { categorizeSideEffects, parseInteractionSeverity } from '../utils/sideEffectCategorization';

/**
 * FDA Drug Data Shape (from API)
 */
interface FDADrugData {
  brandName?: string[];
  genericName?: string[];
  manufacturer?: string[];
  route?: string[];

  // Clinical information (Nurse-focused)
  indicationsAndUsage?: string[];
  dosageAndAdministration?: string[];
  contraindications?: string[];
  warnings?: string[];
  adverseReactions?: string[];
  drugInteractions?: string[];

  // Patient information
  purpose?: string[];
  howSupplied?: string[];
  storageAndHandling?: string[];

  // Ingredients
  activeIngredient?: string[];
  inactiveIngredient?: string[];

  // Advanced/Research information (Researcher-focused)
  clinicalPharmacology?: string[];
  mechanismOfAction?: string[];
  pharmacokinetics?: string[];
  pharmacodynamics?: string[];
  description?: string[]; // Chemical description
}

interface MedicationTemplateProps {
  /** FDA drug data (can be fetched from API) */
  fdaData: FDADrugData;

  /** Patient-specific dosing (overrides FDA defaults) */
  patientDosing?: string;

  /** Additional notes from provider */
  providerNotes?: string;

  /** Show as preview or final document */
  mode?: 'preview' | 'document';
}

export default function MedicationTemplate({
  fdaData,
  patientDosing,
  providerNotes
}: MedicationTemplateProps) {

  // Extract and process FDA data
  const brandName = fdaData.brandName?.[0] || 'Unknown';
  const genericName = fdaData.genericName?.[0] || '';
  const manufacturer = fdaData.manufacturer?.[0];

  const contraindications = fdaData.contraindications || [];
  const warnings = fdaData.warnings || [];
  const interactions = fdaData.drugInteractions || [];

  return (
    <div className="max-w-4xl mx-auto bg-white">

      {/* Header Section - Always Visible */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-xl">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">{brandName}</h1>
            {genericName && (
              <p className="text-blue-100 text-lg">Generic: {genericName}</p>
            )}
            {manufacturer && (
              <p className="text-blue-200 text-sm mt-1">Manufactured by {manufacturer}</p>
            )}
          </div>

          {/* Safety at-a-glance */}
          <SafetyBadge
            contraindications={contraindications.length}
            warnings={warnings.length}
            interactions={interactions.length}
            className="bg-white/10 backdrop-blur-sm px-3 py-2 rounded-lg"
          />
        </div>
      </div>

      <div className="p-6 space-y-4">

        {/* Critical Safety - Always Expanded */}
        {contraindications.length > 0 && (
          <CriticalWarningSection
            title="DO NOT USE This Medication If"
            badge={contraindications.length}
            defaultExpanded={true}
          >
            <Contraindications items={contraindications} />
          </CriticalWarningSection>
        )}

        {/* What It's For - Expanded by Default */}
        {fdaData.indicationsAndUsage && fdaData.indicationsAndUsage.length > 0 && (
          <InfoSection
            title="What This Medication Is For"
            defaultExpanded={true}
          >
            <div className="prose prose-sm max-w-none">
              {fdaData.indicationsAndUsage.map((indication, index) => (
                <div key={index} className="mb-2">
                  <p className="text-gray-700 leading-relaxed">{indication}</p>
                </div>
              ))}
            </div>
          </InfoSection>
        )}

        {/* How to Take It - Expandable */}
        <ExpandableSection
          title="How to Take This Medication"
          icon="fa-pills"
          variant="default"
          defaultExpanded={!!patientDosing}
        >
          {/* Patient-specific dosing overrides FDA default */}
          {patientDosing ? (
            <WarningBox severity="info" title="Your Prescribed Dosage">
              <p className="font-semibold text-lg">{patientDosing}</p>
            </WarningBox>
          ) : (
            fdaData.dosageAndAdministration?.map((dosing, index) => (
              <div key={index} className="mb-3">
                <p className="text-gray-700 leading-relaxed">{dosing}</p>
              </div>
            ))
          )}

          {fdaData.route && fdaData.route.length > 0 && (
            <div className="mt-3 p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                <span className="font-semibold">Route:</span> {fdaData.route.join(', ')}
              </p>
            </div>
          )}
        </ExpandableSection>

        {/* Warnings - Collapsed */}
        {warnings.length > 0 && (
          <WarningSection
            title="Important Warnings & Precautions"
            badge={warnings.length}
            defaultExpanded={false}
          >
            <Warnings items={warnings} />
          </WarningSection>
        )}

        {/* Side Effects - Collapsed */}
        {fdaData.adverseReactions && fdaData.adverseReactions.length > 0 && (() => {
          const categorized = categorizeSideEffects(fdaData.adverseReactions);
          return (
            <ExpandableSection
              title="Possible Side Effects"
              icon="fa-heartbeat"
              variant="warning"
              badge={fdaData.adverseReactions.length}
              defaultExpanded={false}
            >
              <AdverseReactions
                common={categorized.common}
                serious={categorized.serious}
              />
            </ExpandableSection>
          );
        })()}

        {/* Drug Interactions - Collapsed */}
        {interactions.length > 0 && (
          <ExpandableSection
            title="Drug Interactions"
            icon="fa-exchange-alt"
            variant="warning"
            badge={interactions.length}
            defaultExpanded={false}
          >
            <DrugInteractions
              interactions={interactions.map(i => ({
                description: i,
                severity: parseInteractionSeverity(i)
              }))}
            />
          </ExpandableSection>
        )}

        {/* Storage - Collapsed */}
        {fdaData.storageAndHandling && fdaData.storageAndHandling.length > 0 && (
          <ExpandableSection
            title="How to Store This Medication"
            icon="fa-box"
            variant="default"
            defaultExpanded={false}
          >
            {fdaData.storageAndHandling.map((storage, index) => (
              <div key={index} className="flex items-start gap-3 mb-3">
                <i className="fas fa-warehouse text-blue-600 mt-1" aria-hidden="true"></i>
                <p className="text-gray-700">{storage}</p>
              </div>
            ))}
          </ExpandableSection>
        )}

        {/* Ingredients - Collapsed */}
        {(fdaData.activeIngredient || fdaData.inactiveIngredient) && (
          <ExpandableSection
            title="Ingredients"
            icon="fa-flask"
            variant="default"
            defaultExpanded={false}
          >
            {fdaData.activeIngredient && fdaData.activeIngredient.length > 0 && (
              <div className="mb-4">
                <h4 className="font-semibold text-gray-900 mb-2">Active Ingredients:</h4>
                <ul className="list-disc list-inside space-y-1">
                  {fdaData.activeIngredient.map((ingredient, index) => (
                    <li key={index} className="text-gray-700">{ingredient}</li>
                  ))}
                </ul>
              </div>
            )}

            {fdaData.inactiveIngredient && fdaData.inactiveIngredient.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Inactive Ingredients:</h4>
                <p className="text-sm text-gray-600 italic mb-1">
                  (Check for allergies - these do not contribute to medication's effect)
                </p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  {fdaData.inactiveIngredient.map((ingredient, index) => (
                    <li key={index} className="text-gray-600">{ingredient}</li>
                  ))}
                </ul>
              </div>
            )}
          </ExpandableSection>
        )}

        {/* Advanced/Research Information - Collapsed by default */}
        <div className="mt-6 pt-6 border-t-2 border-gray-200">
          <h3 className="text-lg font-semibold text-gray-700 mb-4 flex items-center gap-2">
            <i className="fas fa-microscope text-gray-500" aria-hidden="true"></i>
            Advanced Information for Researchers & Pharmacology
          </h3>

          {/* Clinical Pharmacology - Research level */}
          {fdaData.clinicalPharmacology && fdaData.clinicalPharmacology.length > 0 && (
            <ExpandableSection
              title="Clinical Pharmacology"
              icon="fa-flask-vial"
              variant="default"
              defaultExpanded={false}
              className="mb-3"
            >
              <div className="prose prose-sm max-w-none text-gray-700">
                {fdaData.clinicalPharmacology.map((pharma, index) => (
                  <div key={index} className="mb-3">{pharma}</div>
                ))}
              </div>
            </ExpandableSection>
          )}

          {/* Mechanism of Action - Research level */}
          {fdaData.mechanismOfAction && fdaData.mechanismOfAction.length > 0 && (
            <ExpandableSection
              title="Mechanism of Action"
              icon="fa-dna"
              variant="default"
              defaultExpanded={false}
              className="mb-3"
            >
              <div className="prose prose-sm max-w-none text-gray-700">
                {fdaData.mechanismOfAction.map((mechanism, index) => (
                  <div key={index} className="mb-3">{mechanism}</div>
                ))}
              </div>
            </ExpandableSection>
          )}

          {/* Pharmacokinetics - Research level */}
          {fdaData.pharmacokinetics && fdaData.pharmacokinetics.length > 0 && (
            <ExpandableSection
              title="Pharmacokinetics (ADME)"
              icon="fa-chart-line"
              variant="default"
              defaultExpanded={false}
              className="mb-3"
            >
              <div className="bg-blue-50 border-l-4 border-blue-400 p-3 mb-3 rounded-r">
                <p className="text-xs text-blue-800 font-semibold mb-1">Absorption • Distribution • Metabolism • Excretion</p>
              </div>
              <div className="prose prose-sm max-w-none text-gray-700">
                {fdaData.pharmacokinetics.map((pk, index) => (
                  <div key={index} className="mb-3">{pk}</div>
                ))}
              </div>
            </ExpandableSection>
          )}

          {/* Pharmacodynamics - Research level */}
          {fdaData.pharmacodynamics && fdaData.pharmacodynamics.length > 0 && (
            <ExpandableSection
              title="Pharmacodynamics"
              icon="fa-wave-square"
              variant="default"
              defaultExpanded={false}
              className="mb-3"
            >
              <div className="prose prose-sm max-w-none text-gray-700">
                {fdaData.pharmacodynamics.map((pd, index) => (
                  <div key={index} className="mb-3">{pd}</div>
                ))}
              </div>
            </ExpandableSection>
          )}

          {/* Chemical Description - Research level */}
          {fdaData.description && fdaData.description.length > 0 && (
            <ExpandableSection
              title="Chemical Description & Structure"
              icon="fa-atom"
              variant="default"
              defaultExpanded={false}
              className="mb-3"
            >
              <div className="prose prose-sm max-w-none text-gray-700">
                {fdaData.description.map((desc, index) => (
                  <div key={index} className="mb-3 font-mono text-sm">{desc}</div>
                ))}
              </div>
            </ExpandableSection>
          )}
        </div>

        {/* Provider Notes - if provided */}
        {providerNotes && (
          <WarningBox severity="info" title="Special Instructions from Your Healthcare Provider" className="mt-6">
            <p className="text-gray-800 leading-relaxed whitespace-pre-line">{providerNotes}</p>
          </WarningBox>
        )}

        {/* FDA Attribution - Always at bottom */}
        <FDAAttribution className="mt-6" />

        {/* Educational Disclaimer */}
        <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded-lg text-xs text-gray-600 text-center">
          <p className="font-semibold mb-1">This is not medical advice</p>
          <p>
            Always follow your healthcare provider's instructions. Contact your doctor or pharmacist
            if you have questions about your medications. In case of emergency, call 911.
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Example Usage:
 *
 * const sampleFDAData = {
 *   brandName: ['Tylenol'],
 *   genericName: ['Acetaminophen'],
 *   manufacturer: ['Johnson & Johnson'],
 *   route: ['ORAL'],
 *   indicationsAndUsage: ['For temporary relief of minor aches and pains', 'Reduction of fever'],
 *   contraindications: ['Known hypersensitivity to acetaminophen', 'Severe liver disease'],
 *   warnings: ['Do not exceed recommended dose', 'May cause severe liver damage if taken with alcohol'],
 *   adverseReactions: ['Nausea', 'Rash', 'Liver damage (rare but serious)'],
 *   drugInteractions: ['Warfarin - may increase bleeding risk', 'Alcohol - increases liver toxicity'],
 *   storageAndHandling: ['Store at room temperature 20-25°C (68-77°F)', 'Keep out of reach of children']
 * };
 *
 * <MedicationTemplate
 *   fdaData={sampleFDAData}
 *   patientDosing="Take 500mg every 6 hours as needed for pain. Do not exceed 3000mg in 24 hours."
 *   providerNotes="Patient has mild liver impairment - reduced maximum daily dose to 3000mg instead of 4000mg."
 * />
 */
