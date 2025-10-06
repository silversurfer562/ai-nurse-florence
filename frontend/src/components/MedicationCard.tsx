/**
 * Medication Card Component
 *
 * Displays medication information with consistent UI whether collapsed or expanded.
 * Ensures all cards show prescription status, dosage form, and route even when collapsed.
 *
 * Key Features:
 * - Collapsed state shows: name, prescription badge, dosage form badge, route
 * - Expanded state shows: all above + detailed sections (primary use, warnings, etc.)
 * - Consistent visual hierarchy across all medication cards
 */

import { useState, ReactNode } from 'react';

interface MedicationCardProps {
  /** Medication name (e.g., "Aspirin (Pharbest Regular Strength Aspirin)") */
  name: string;

  /** Brand/generic display name */
  displayName?: string;

  /** Prescription status */
  prescriptionStatus: 'OTC' | 'Prescription Required';

  /** Dosage form (e.g., "TABLET", "TABLET, FILM COATED") */
  dosageForm: string;

  /** Route of administration (e.g., "ORAL", "INTRAVENOUS") */
  route: string;

  /** Primary use / indication */
  primaryUse?: string;

  /** "What is this medication for?" section content */
  whatIsThisFor?: string;

  /** Enhanced with FDA data? */
  fdaEnhanced?: boolean;

  /** Manufacturer name */
  manufacturer?: string;

  /** Additional content sections to show when expanded */
  children?: ReactNode;

  /** Initially expanded? */
  defaultExpanded?: boolean;

  /** Custom CSS classes */
  className?: string;
}

export default function MedicationCard({
  name,
  displayName,
  prescriptionStatus,
  dosageForm,
  route,
  primaryUse,
  whatIsThisFor,
  fdaEnhanced = false,
  manufacturer,
  children,
  defaultExpanded = false,
  className = ''
}: MedicationCardProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  // Determine prescription badge styling
  const prescriptionBadgeStyle =
    prescriptionStatus === 'OTC'
      ? 'bg-green-100 text-green-800 border-green-300'
      : 'bg-purple-100 text-purple-800 border-purple-300';

  const prescriptionIcon = prescriptionStatus === 'OTC' ? 'fa-shopping-cart' : 'fa-prescription';

  return (
    <div
      className={`border-2 border-blue-200 bg-blue-50 rounded-lg overflow-hidden ${className}`}
    >
      {/* Header - Always Visible (Collapsed & Expanded) */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-4 py-3 bg-blue-100 hover:bg-blue-200 transition-colors cursor-pointer text-left"
        aria-expanded={isExpanded}
        aria-controls={`medication-${name.replace(/\s+/g, '-').toLowerCase()}`}
      >
        <div className="flex items-start justify-between gap-3">
          {/* Left: Chevron + Icon + Name */}
          <div className="flex items-center gap-3 flex-1">
            {/* Expand/Collapse Chevron */}
            <i
              className={`fas fa-chevron-${
                isExpanded ? 'down' : 'right'
              } text-blue-600 text-sm transition-transform flex-shrink-0`}
              aria-hidden="true"
            ></i>

            {/* Medication Icon */}
            <i className="fas fa-pills text-blue-600 text-lg flex-shrink-0" aria-hidden="true"></i>

            {/* Medication Name */}
            <span className="font-semibold text-blue-900 text-base">
              {displayName || name}
            </span>
          </div>

          {/* Right: Visual hint */}
          <span className="sr-only">{isExpanded ? 'Click to collapse' : 'Click to expand'}</span>
        </div>
      </button>

      {/* Summary Info - Always Visible (Collapsed & Expanded) */}
      <div className="px-4 py-3 bg-white border-t border-blue-200">
        {/* Prescription Status + Dosage Form Badges */}
        <div className="flex items-center gap-2 mb-2 flex-wrap">
          {/* Prescription Status Badge */}
          <span
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded border font-medium text-xs ${prescriptionBadgeStyle}`}
          >
            <i className={`fas ${prescriptionIcon}`} aria-hidden="true"></i>
            {prescriptionStatus}
          </span>

          {/* Dosage Form Badge */}
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-blue-100 text-blue-800 border border-blue-300 font-medium text-xs">
            <i className="fas fa-pills" aria-hidden="true"></i>
            {dosageForm}
          </span>
        </div>

        {/* Route of Administration */}
        <div className="flex items-center gap-2 text-sm text-gray-700 mb-3">
          <i className="fas fa-arrow-right text-gray-500" aria-hidden="true"></i>
          <span className="font-medium">{route}</span>
        </div>

        {/* "What is this medication for?" - Always visible */}
        {whatIsThisFor && (
          <div className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded-r">
            <div className="flex items-start gap-2 mb-2">
              <i className="fas fa-question-circle text-blue-600 mt-0.5 flex-shrink-0" aria-hidden="true"></i>
              <h3 className="font-semibold text-blue-900 text-sm">
                What is this medication for?
              </h3>
            </div>
            <p className="text-sm text-gray-700 leading-relaxed">{whatIsThisFor}</p>
          </div>
        )}
      </div>

      {/* Expanded Content */}
      {isExpanded && (
        <div
          id={`medication-${name.replace(/\s+/g, '-').toLowerCase()}`}
          className="px-4 py-4 bg-white border-t border-blue-200 space-y-4"
        >
          {/* Primary Use Section */}
          {primaryUse && (
            <div className="bg-green-50 border-l-4 border-green-400 p-3 rounded-r">
              <h3 className="font-semibold text-green-900 text-sm mb-2">Primary Use</h3>
              <p className="text-sm text-gray-700 leading-relaxed">{primaryUse}</p>
            </div>
          )}

          {/* FDA Enhancement Badge */}
          {fdaEnhanced && (
            <div className="bg-blue-50 border border-blue-200 p-3 rounded-lg flex items-center gap-2">
              <i className="fas fa-shield-alt text-blue-600" aria-hidden="true"></i>
              <div className="flex-1">
                <span className="font-semibold text-blue-900 text-sm">Enhanced with FDA Data</span>
                {manufacturer && (
                  <span className="text-xs text-blue-700 ml-2">• {manufacturer}</span>
                )}
              </div>
            </div>
          )}

          {/* Additional Custom Content */}
          {children}
        </div>
      )}
    </div>
  );
}

// Example Usage:
//
// MedicationCard with all features:
// name="Aspirin (Pharbest Regular Strength Aspirin)"
// prescriptionStatus="OTC"
// dosageForm="TABLET"
// route="ORAL"
// primaryUse="Relief of minor aches and pains..."
// fdaEnhanced={true}
// manufacturer="P & L Development, LLC"
// defaultExpanded={true}
//
// MedicationCard minimal (collapsed):
// name="Warfarin (Warfarin Sodium)"
// prescriptionStatus="Prescription Required"
// dosageForm="TABLET"
// route="ORAL"
// defaultExpanded={false}
