/**
 * Complete Page Template with Placeholder Content
 *
 * This is a rough template showing the full page layout structure
 * with placeholder graphics and lorem ipsum text until real data is available.
 */

import ExpandableSection, { WarningSection, CriticalWarningSection, InfoSection } from './ExpandableSection';
import { WarningBox, FDAAttribution, SafetyBadge } from './FDAWarnings';

export default function PageTemplate() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-8">
      <div className="max-w-5xl mx-auto bg-white shadow-2xl rounded-xl overflow-hidden">

        {/* HEADER - Drug/Topic Title Section */}
        <header className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-8">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {/* Drug/Topic Icon */}
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                  <i className="fas fa-prescription-bottle-alt text-4xl" aria-hidden="true"></i>
                </div>
                <div>
                  <h1 className="text-4xl font-bold mb-2">Medication Name</h1>
                  <p className="text-blue-100 text-lg">Generic: Chemical Name Here</p>
                </div>
              </div>

              {/* Manufacturer */}
              <p className="text-blue-200 text-sm">Manufactured by: Company Name, Inc.</p>
            </div>

            {/* Safety Quick Stats */}
            <div className="bg-white/10 backdrop-blur-md rounded-lg p-4 ml-4">
              <SafetyBadge
                contraindications={3}
                warnings={8}
                interactions={12}
              />
            </div>
          </div>
        </header>

        {/* MAIN CONTENT */}
        <main className="p-8">

          {/* TIER 1: CRITICAL SAFETY - Always Expanded */}
          <section className="mb-6">
            <CriticalWarningSection
              title="Critical Safety Information - DO NOT USE IF"
              badge={3}
              defaultExpanded={true}
            >
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 bg-red-50 border-l-4 border-red-500 rounded-r">
                  <i className="fas fa-times-circle text-red-600 text-xl mt-1 flex-shrink-0" aria-hidden="true"></i>
                  <div>
                    <h4 className="font-bold text-red-900 mb-1">Lorem ipsum dolor sit amet</h4>
                    <p className="text-red-800 text-sm">Consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-red-50 border-l-4 border-red-500 rounded-r">
                  <i className="fas fa-times-circle text-red-600 text-xl mt-1 flex-shrink-0" aria-hidden="true"></i>
                  <div>
                    <h4 className="font-bold text-red-900 mb-1">Ut enim ad minim veniam</h4>
                    <p className="text-red-800 text-sm">Quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-red-50 border-l-4 border-red-500 rounded-r">
                  <i className="fas fa-times-circle text-red-600 text-xl mt-1 flex-shrink-0" aria-hidden="true"></i>
                  <div>
                    <h4 className="font-bold text-red-900 mb-1">Duis aute irure dolor</h4>
                    <p className="text-red-800 text-sm">In reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
                  </div>
                </div>
              </div>
            </CriticalWarningSection>
          </section>

          {/* TIER 1: WHAT IT'S FOR - Expanded by Default */}
          <section className="mb-6">
            <InfoSection
              title="What This Medication Is For"
              defaultExpanded={true}
            >
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <i className="fas fa-check-circle text-green-600 text-xl mt-1 flex-shrink-0" aria-hidden="true"></i>
                  <p className="text-gray-700 leading-relaxed">
                    <strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.
                  </p>
                </div>

                <div className="flex items-start gap-3">
                  <i className="fas fa-check-circle text-green-600 text-xl mt-1 flex-shrink-0" aria-hidden="true"></i>
                  <p className="text-gray-700 leading-relaxed">
                    <strong>Duis aute irure dolor</strong> in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur excepteur sint occaecat cupidatat non proident.
                  </p>
                </div>

                {/* Placeholder Image/Graphic Area */}
                <div className="mt-4 p-8 bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-dashed border-blue-300 rounded-lg">
                  <div className="text-center">
                    <i className="fas fa-image text-blue-400 text-6xl mb-3" aria-hidden="true"></i>
                    <p className="text-blue-600 font-medium">Placeholder for Infographic</p>
                    <p className="text-blue-500 text-sm mt-1">Visual diagram showing indication/use case</p>
                  </div>
                </div>
              </div>
            </InfoSection>
          </section>

          {/* TIER 1: HOW TO TAKE IT - Expanded by Default */}
          <section className="mb-6">
            <ExpandableSection
              title="How to Take This Medication"
              icon="fa-pills"
              variant="info"
              defaultExpanded={true}
            >
              <WarningBox severity="info" title="Your Prescribed Dosage">
                <p className="text-xl font-semibold text-gray-900 mb-2">Take 500mg every 6 hours</p>
                <p className="text-gray-700">Do not exceed 3000mg in 24 hours</p>
              </WarningBox>

              <div className="mt-4 grid md:grid-cols-2 gap-4">
                <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <i className="fas fa-clock text-blue-600" aria-hidden="true"></i>
                    When to Take
                  </h4>
                  <p className="text-sm text-gray-700">Lorem ipsum dolor sit amet, consectetur adipiscing elit.</p>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <i className="fas fa-utensils text-blue-600" aria-hidden="true"></i>
                    With or Without Food
                  </h4>
                  <p className="text-sm text-gray-700">Sed do eiusmod tempor incididunt ut labore et dolore.</p>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <i className="fas fa-glass-whiskey text-blue-600" aria-hidden="true"></i>
                    How to Take
                  </h4>
                  <p className="text-sm text-gray-700">Ut enim ad minim veniam, quis nostrud exercitation.</p>
                </div>

                <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <h4 className="font-semibold text-gray-900 mb-2 flex items-center gap-2">
                    <i className="fas fa-exclamation-triangle text-yellow-600" aria-hidden="true"></i>
                    Missed Dose
                  </h4>
                  <p className="text-sm text-gray-700">Ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
                </div>
              </div>
            </ExpandableSection>
          </section>

          {/* TIER 2: WARNINGS - Collapsed */}
          <section className="mb-6">
            <WarningSection
              title="Important Warnings & Precautions"
              badge={8}
              defaultExpanded={false}
            >
              <div className="space-y-4">
                <div className="border-l-4 border-orange-400 pl-4 py-2">
                  <h4 className="font-bold text-orange-900 mb-1">Lorem ipsum dolor sit amet</h4>
                  <p className="text-orange-800 text-sm">Consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.</p>
                </div>

                <div className="border-l-4 border-orange-400 pl-4 py-2">
                  <h4 className="font-bold text-orange-900 mb-1">Quis nostrud exercitation</h4>
                  <p className="text-orange-800 text-sm">Ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit.</p>
                </div>

                <div className="border-l-4 border-orange-400 pl-4 py-2">
                  <h4 className="font-bold text-orange-900 mb-1">Excepteur sint occaecat</h4>
                  <p className="text-orange-800 text-sm">Cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
                </div>

                {/* Placeholder for chart/graphic */}
                <div className="mt-4 p-6 bg-gradient-to-br from-orange-50 to-yellow-50 border-2 border-dashed border-orange-300 rounded-lg">
                  <div className="text-center">
                    <i className="fas fa-chart-bar text-orange-400 text-5xl mb-3" aria-hidden="true"></i>
                    <p className="text-orange-600 font-medium">Placeholder for Warning Timeline Chart</p>
                    <p className="text-orange-500 text-sm mt-1">Visual showing when to watch for specific warnings</p>
                  </div>
                </div>
              </div>
            </WarningSection>
          </section>

          {/* TIER 2: SIDE EFFECTS - Collapsed */}
          <section className="mb-6">
            <ExpandableSection
              title="Possible Side Effects"
              icon="fa-heartbeat"
              variant="warning"
              badge={15}
              defaultExpanded={false}
            >
              {/* Serious Side Effects */}
              <WarningBox severity="critical" title="Serious Side Effects - Seek Medical Help Immediately" className="mb-4">
                <p className="mb-3 font-semibold">Contact your doctor or emergency services if you experience:</p>
                <div className="grid md:grid-cols-2 gap-3">
                  <div className="flex items-start gap-2">
                    <i className="fas fa-phone-volume text-red-600 mt-1 flex-shrink-0" aria-hidden="true"></i>
                    <span className="text-sm">Lorem ipsum dolor sit amet</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <i className="fas fa-phone-volume text-red-600 mt-1 flex-shrink-0" aria-hidden="true"></i>
                    <span className="text-sm">Consectetur adipiscing elit</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <i className="fas fa-phone-volume text-red-600 mt-1 flex-shrink-0" aria-hidden="true"></i>
                    <span className="text-sm">Sed do eiusmod tempor</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <i className="fas fa-phone-volume text-red-600 mt-1 flex-shrink-0" aria-hidden="true"></i>
                    <span className="text-sm">Incididunt ut labore</span>
                  </div>
                </div>
              </WarningBox>

              {/* Common Side Effects */}
              <WarningBox severity="moderate" title="Common Side Effects">
                <p className="mb-3">These side effects are usually mild and may go away with continued use:</p>
                <div className="grid md:grid-cols-3 gap-2">
                  <div className="flex items-center gap-2">
                    <i className="fas fa-circle text-yellow-600 text-xs" aria-hidden="true"></i>
                    <span className="text-sm">Dolor sit amet</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <i className="fas fa-circle text-yellow-600 text-xs" aria-hidden="true"></i>
                    <span className="text-sm">Consectetur</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <i className="fas fa-circle text-yellow-600 text-xs" aria-hidden="true"></i>
                    <span className="text-sm">Adipiscing elit</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <i className="fas fa-circle text-yellow-600 text-xs" aria-hidden="true"></i>
                    <span className="text-sm">Sed do eiusmod</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <i className="fas fa-circle text-yellow-600 text-xs" aria-hidden="true"></i>
                    <span className="text-sm">Tempor incididunt</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <i className="fas fa-circle text-yellow-600 text-xs" aria-hidden="true"></i>
                    <span className="text-sm">Ut labore</span>
                  </div>
                </div>
              </WarningBox>
            </ExpandableSection>
          </section>

          {/* TIER 2: DRUG INTERACTIONS - Collapsed */}
          <section className="mb-6">
            <ExpandableSection
              title="Drug Interactions"
              icon="fa-exchange-alt"
              variant="warning"
              badge={12}
              defaultExpanded={false}
            >
              <div className="space-y-3">
                {/* Critical Interaction */}
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r">
                  <div className="flex items-start gap-2 mb-2">
                    <span className="px-2 py-1 bg-red-200 text-red-900 text-xs font-bold rounded">CRITICAL</span>
                    <h4 className="font-bold text-red-900">Lorem Ipsum Drug Name</h4>
                  </div>
                  <p className="text-red-800 text-sm">Consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                </div>

                {/* Major Interactions */}
                <div className="bg-orange-50 border-l-4 border-orange-400 p-4 rounded-r">
                  <div className="flex items-start gap-2 mb-2">
                    <span className="px-2 py-1 bg-orange-200 text-orange-900 text-xs font-bold rounded">MAJOR</span>
                    <h4 className="font-bold text-orange-900">Dolor Sit Medication</h4>
                  </div>
                  <p className="text-orange-800 text-sm">Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip.</p>
                </div>

                <div className="bg-orange-50 border-l-4 border-orange-400 p-4 rounded-r">
                  <div className="flex items-start gap-2 mb-2">
                    <span className="px-2 py-1 bg-orange-200 text-orange-900 text-xs font-bold rounded">MAJOR</span>
                    <h4 className="font-bold text-orange-900">Amet Consectetur Drug</h4>
                  </div>
                  <p className="text-orange-800 text-sm">Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore.</p>
                </div>

                {/* Moderate Interactions */}
                <div className="bg-yellow-50 border-l-4 border-yellow-400 p-3 rounded-r">
                  <div className="flex items-start gap-2">
                    <span className="px-2 py-1 bg-yellow-200 text-yellow-900 text-xs font-bold rounded">MODERATE</span>
                    <div className="flex-1">
                      <span className="font-semibold text-yellow-900 text-sm">Adipiscing Elit Medicine: </span>
                      <span className="text-yellow-800 text-sm">Excepteur sint occaecat cupidatat non proident.</span>
                    </div>
                  </div>
                </div>
              </div>
            </ExpandableSection>
          </section>

          {/* TIER 2: STORAGE - Collapsed */}
          <section className="mb-6">
            <ExpandableSection
              title="Storage Instructions"
              icon="fa-box"
              variant="default"
              defaultExpanded={false}
            >
              <div className="grid md:grid-cols-2 gap-4">
                <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <i className="fas fa-thermometer-half text-blue-600 text-2xl mt-1" aria-hidden="true"></i>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Temperature</h4>
                    <p className="text-sm text-gray-700">Store at 20-25°C (68-77°F). Lorem ipsum dolor sit amet.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <i className="fas fa-sun text-yellow-600 text-2xl mt-1" aria-hidden="true"></i>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Light</h4>
                    <p className="text-sm text-gray-700">Consectetur adipiscing elit, sed do eiusmod tempor.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <i className="fas fa-tint text-blue-600 text-2xl mt-1" aria-hidden="true"></i>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Moisture</h4>
                    <p className="text-sm text-gray-700">Incididunt ut labore et dolore magna aliqua.</p>
                  </div>
                </div>

                <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <i className="fas fa-child text-red-600 text-2xl mt-1" aria-hidden="true"></i>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-1">Safety</h4>
                    <p className="text-sm text-gray-700">Keep out of reach of children and pets.</p>
                  </div>
                </div>
              </div>
            </ExpandableSection>
          </section>

          {/* TIER 3: RESEARCH SECTION */}
          <section className="mt-8 pt-8 border-t-4 border-gray-200">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-700 mb-2 flex items-center gap-3">
                <i className="fas fa-microscope text-gray-500" aria-hidden="true"></i>
                Advanced Information for Researchers & Pharmacology
              </h2>
              <p className="text-sm text-gray-600">
                Detailed scientific and pharmacological data for research and deep learning
              </p>
            </div>

            {/* Mechanism of Action */}
            <div className="mb-4">
              <ExpandableSection
                title="Mechanism of Action"
                icon="fa-dna"
                variant="default"
                defaultExpanded={false}
              >
                <div className="prose prose-sm max-w-none">
                  <p className="text-gray-700 mb-3">
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                  </p>

                  {/* Placeholder for molecular diagram */}
                  <div className="my-4 p-8 bg-gradient-to-br from-purple-50 to-indigo-50 border-2 border-dashed border-purple-300 rounded-lg">
                    <div className="text-center">
                      <i className="fas fa-project-diagram text-purple-400 text-6xl mb-3" aria-hidden="true"></i>
                      <p className="text-purple-600 font-medium">Placeholder for Molecular Mechanism Diagram</p>
                      <p className="text-purple-500 text-sm mt-1">Receptor binding and cascade pathways</p>
                    </div>
                  </div>

                  <p className="text-gray-700">
                    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
                    Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
                  </p>
                </div>
              </ExpandableSection>
            </div>

            {/* Pharmacokinetics */}
            <div className="mb-4">
              <ExpandableSection
                title="Pharmacokinetics (ADME)"
                icon="fa-chart-line"
                variant="default"
                defaultExpanded={false}
              >
                <div className="bg-blue-50 border-l-4 border-blue-400 p-3 mb-4 rounded-r">
                  <p className="text-xs text-blue-800 font-semibold">Absorption • Distribution • Metabolism • Excretion</p>
                </div>

                <div className="space-y-4">
                  <div>
                    <h4 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                      <i className="fas fa-arrow-down text-blue-600" aria-hidden="true"></i>
                      Absorption
                    </h4>
                    <p className="text-sm text-gray-700 pl-6">
                      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                      <strong className="block mt-1">Tmax: 2-3 hours | Bioavailability: 85%</strong>
                    </p>
                  </div>

                  <div>
                    <h4 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                      <i className="fas fa-share-alt text-green-600" aria-hidden="true"></i>
                      Distribution
                    </h4>
                    <p className="text-sm text-gray-700 pl-6">
                      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                      <strong className="block mt-1">Vd: 50-70 L | Protein binding: 95%</strong>
                    </p>
                  </div>

                  <div>
                    <h4 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                      <i className="fas fa-random text-purple-600" aria-hidden="true"></i>
                      Metabolism
                    </h4>
                    <p className="text-sm text-gray-700 pl-6">
                      Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
                      <strong className="block mt-1">Primary: CYP3A4, CYP2D6 | Half-life: 4-6 hours</strong>
                    </p>
                  </div>

                  <div>
                    <h4 className="font-bold text-gray-900 mb-2 flex items-center gap-2">
                      <i className="fas fa-sign-out-alt text-red-600" aria-hidden="true"></i>
                      Excretion
                    </h4>
                    <p className="text-sm text-gray-700 pl-6">
                      Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
                      <strong className="block mt-1">Renal: 60% | Fecal: 40%</strong>
                    </p>
                  </div>
                </div>

                {/* Placeholder for PK curve */}
                <div className="mt-4 p-8 bg-gradient-to-br from-green-50 to-teal-50 border-2 border-dashed border-green-300 rounded-lg">
                  <div className="text-center">
                    <i className="fas fa-chart-area text-green-400 text-6xl mb-3" aria-hidden="true"></i>
                    <p className="text-green-600 font-medium">Placeholder for Pharmacokinetic Curve</p>
                    <p className="text-green-500 text-sm mt-1">Plasma concentration vs time graph</p>
                  </div>
                </div>
              </ExpandableSection>
            </div>

            {/* Clinical Pharmacology */}
            <div className="mb-4">
              <ExpandableSection
                title="Clinical Pharmacology"
                icon="fa-flask-vial"
                variant="default"
                defaultExpanded={false}
              >
                <div className="prose prose-sm max-w-none text-gray-700">
                  <p className="mb-3">
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                    Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
                  </p>
                  <ul className="list-disc list-inside space-y-1 mb-3">
                    <li>Duis aute irure dolor in reprehenderit</li>
                    <li>Voluptate velit esse cillum dolore</li>
                    <li>Excepteur sint occaecat cupidatat</li>
                    <li>Non proident sunt in culpa</li>
                  </ul>
                  <p>
                    Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam.
                  </p>
                </div>
              </ExpandableSection>
            </div>

            {/* Chemical Structure */}
            <div className="mb-4">
              <ExpandableSection
                title="Chemical Description & Structure"
                icon="fa-atom"
                variant="default"
                defaultExpanded={false}
              >
                <div className="space-y-4">
                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <h4 className="font-semibold text-gray-900 mb-2">Molecular Formula</h4>
                    <p className="font-mono text-lg text-gray-800">C₁₇H₂₁NO₄</p>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <h4 className="font-semibold text-gray-900 mb-2">Chemical Name (IUPAC)</h4>
                    <p className="font-mono text-sm text-gray-700">
                      Lorem ipsum dolor sit amet consectetur adipiscing elit sed do eiusmod tempor incididunt
                    </p>
                  </div>

                  {/* Placeholder for chemical structure */}
                  <div className="p-8 bg-gradient-to-br from-gray-50 to-slate-50 border-2 border-dashed border-gray-300 rounded-lg">
                    <div className="text-center">
                      <i className="fas fa-draw-polygon text-gray-400 text-6xl mb-3" aria-hidden="true"></i>
                      <p className="text-gray-600 font-medium">Placeholder for Chemical Structure Diagram</p>
                      <p className="text-gray-500 text-sm mt-1">2D molecular structure with bonds and atoms labeled</p>
                    </div>
                  </div>

                  <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                    <h4 className="font-semibold text-gray-900 mb-2">Physical Properties</h4>
                    <dl className="grid grid-cols-2 gap-2 text-sm">
                      <dt className="text-gray-600">Molecular Weight:</dt>
                      <dd className="font-mono text-gray-900">303.35 g/mol</dd>

                      <dt className="text-gray-600">Melting Point:</dt>
                      <dd className="font-mono text-gray-900">150-152°C</dd>

                      <dt className="text-gray-600">Solubility:</dt>
                      <dd className="text-gray-900">Slightly soluble in water</dd>

                      <dt className="text-gray-600">pKa:</dt>
                      <dd className="font-mono text-gray-900">8.5</dd>
                    </dl>
                  </div>
                </div>
              </ExpandableSection>
            </div>
          </section>

          {/* FOOTER - Attribution & Disclaimers */}
          <footer className="mt-8 pt-6 border-t-2 border-gray-200 space-y-4">
            <FDAAttribution />

            <div className="p-4 bg-gray-50 border border-gray-200 rounded-lg text-xs text-gray-600 text-center">
              <p className="font-semibold text-gray-800 mb-2">Educational Use Only - This is Not Medical Advice</p>
              <p className="mb-1">
                Always follow your healthcare provider's instructions. Contact your doctor or pharmacist if you have questions about your medications.
              </p>
              <p className="font-semibold text-red-700">
                In case of emergency, call 911 or your local emergency services.
              </p>
            </div>

            <div className="text-center text-xs text-gray-500">
              <p>Document generated: {new Date().toLocaleDateString()} at {new Date().toLocaleTimeString()}</p>
              <p className="mt-1">AI Nurse Florence - Clinical Decision Support Platform</p>
            </div>
          </footer>

        </main>
      </div>
    </div>
  );
}
