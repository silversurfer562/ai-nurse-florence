import { ReactNode } from 'react';

/**
 * FDA Warning Display Components
 *
 * Nicely formatted warning components for displaying FDA drug safety information.
 * Uses clinical severity levels with appropriate visual hierarchy.
 */

export type WarningSeverity = 'critical' | 'major' | 'moderate' | 'minor' | 'info';

interface WarningBoxProps {
  severity: WarningSeverity;
  title?: string;
  children: ReactNode;
  icon?: string;
  className?: string;
}

/**
 * Generic Warning Box with severity-based styling
 */
export function WarningBox({
  severity,
  title,
  children,
  icon,
  className = ''
}: WarningBoxProps) {
  const severityConfig: Record<WarningSeverity, {
    bg: string;
    border: string;
    text: string;
    iconColor: string;
    defaultIcon: string;
  }> = {
    critical: {
      bg: 'bg-red-50',
      border: 'border-red-600',
      text: 'text-red-900',
      iconColor: 'text-red-600',
      defaultIcon: 'fa-exclamation-circle'
    },
    major: {
      bg: 'bg-orange-50',
      border: 'border-orange-500',
      text: 'text-orange-900',
      iconColor: 'text-orange-600',
      defaultIcon: 'fa-exclamation-triangle'
    },
    moderate: {
      bg: 'bg-yellow-50',
      border: 'border-yellow-400',
      text: 'text-yellow-900',
      iconColor: 'text-yellow-600',
      defaultIcon: 'fa-exclamation'
    },
    minor: {
      bg: 'bg-blue-50',
      border: 'border-blue-400',
      text: 'text-blue-900',
      iconColor: 'text-blue-600',
      defaultIcon: 'fa-info-circle'
    },
    info: {
      bg: 'bg-gray-50',
      border: 'border-gray-400',
      text: 'text-gray-900',
      iconColor: 'text-gray-600',
      defaultIcon: 'fa-info'
    }
  };

  const config = severityConfig[severity];
  const displayIcon = icon || config.defaultIcon;

  return (
    <div className={`${config.bg} border-l-4 ${config.border} p-4 rounded-r-lg ${className}`}>
      <div className="flex gap-3">
        <i className={`fas ${displayIcon} ${config.iconColor} text-xl flex-shrink-0 mt-0.5`} aria-hidden="true"></i>
        <div className="flex-1">
          {title && (
            <h4 className={`font-bold ${config.text} mb-2 text-lg`}>{title}</h4>
          )}
          <div className={`${config.text} text-sm leading-relaxed`}>
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * FDA Contraindication Display
 */
interface ContraindicationProps {
  items: string[];
  className?: string;
}

export function Contraindications({ items, className = '' }: ContraindicationProps) {
  if (!items || items.length === 0) return null;

  return (
    <WarningBox severity="critical" title="DO NOT USE This Medication If:" className={className}>
      <ul className="space-y-2 mt-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-start gap-2">
            <i className="fas fa-times-circle text-red-600 mt-1 flex-shrink-0" aria-hidden="true"></i>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </WarningBox>
  );
}

/**
 * FDA General Warnings Display
 */
interface WarningsProps {
  items: string[];
  className?: string;
}

export function Warnings({ items, className = '' }: WarningsProps) {
  if (!items || items.length === 0) return null;

  return (
    <WarningBox severity="major" title="Important Warnings" className={className}>
      <ul className="space-y-2 mt-2">
        {items.map((item, index) => (
          <li key={index} className="flex items-start gap-2">
            <i className="fas fa-exclamation-triangle text-orange-600 mt-1 flex-shrink-0" aria-hidden="true"></i>
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </WarningBox>
  );
}

/**
 * Adverse Reactions Display with severity grouping
 */
interface AdverseReactionsProps {
  common?: string[];
  serious?: string[];
  className?: string;
}

export function AdverseReactions({ common, serious, className = '' }: AdverseReactionsProps) {
  return (
    <div className={`space-y-4 ${className}`}>
      {/* Serious reactions - Critical severity */}
      {serious && serious.length > 0 && (
        <WarningBox severity="critical" title="Serious Side Effects - Seek Medical Help Immediately">
          <p className="mb-2 font-semibold">Contact your doctor or emergency services if you experience:</p>
          <ul className="space-y-2">
            {serious.map((reaction, index) => (
              <li key={index} className="flex items-start gap-2">
                <i className="fas fa-phone-volume text-red-600 mt-1 flex-shrink-0" aria-hidden="true"></i>
                <span>{reaction}</span>
              </li>
            ))}
          </ul>
        </WarningBox>
      )}

      {/* Common reactions - Moderate severity */}
      {common && common.length > 0 && (
        <WarningBox severity="moderate" title="Common Side Effects">
          <p className="mb-2">These side effects are usually mild and may go away with continued use:</p>
          <ul className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
            {common.map((reaction, index) => (
              <li key={index} className="flex items-start gap-2">
                <i className="fas fa-circle text-yellow-600 text-xs mt-1.5 flex-shrink-0" aria-hidden="true"></i>
                <span>{reaction}</span>
              </li>
            ))}
          </ul>
        </WarningBox>
      )}
    </div>
  );
}

/**
 * Drug Interactions Display
 */
interface DrugInteractionsProps {
  interactions: Array<{
    drug?: string;
    description: string;
    severity?: 'critical' | 'major' | 'moderate';
  }>;
  className?: string;
}

export function DrugInteractions({ interactions, className = '' }: DrugInteractionsProps) {
  if (!interactions || interactions.length === 0) return null;

  // Group by severity
  const critical = interactions.filter(i => i.severity === 'critical');
  const major = interactions.filter(i => i.severity === 'major');
  const moderate = interactions.filter(i => i.severity === 'moderate' || !i.severity);

  return (
    <div className={`space-y-4 ${className}`}>
      {critical.length > 0 && (
        <WarningBox severity="critical" title={`Critical Interactions (${critical.length})`}>
          <ul className="space-y-3 mt-2">
            {critical.map((interaction, index) => (
              <li key={index} className="border-l-2 border-red-400 pl-3">
                {interaction.drug && (
                  <p className="font-bold text-red-900 mb-1">{interaction.drug}</p>
                )}
                <p className="text-sm">{interaction.description}</p>
              </li>
            ))}
          </ul>
        </WarningBox>
      )}

      {major.length > 0 && (
        <WarningBox severity="major" title={`Major Interactions (${major.length})`}>
          <ul className="space-y-3 mt-2">
            {major.map((interaction, index) => (
              <li key={index} className="border-l-2 border-orange-400 pl-3">
                {interaction.drug && (
                  <p className="font-bold text-orange-900 mb-1">{interaction.drug}</p>
                )}
                <p className="text-sm">{interaction.description}</p>
              </li>
            ))}
          </ul>
        </WarningBox>
      )}

      {moderate.length > 0 && (
        <WarningBox severity="moderate" title={`Moderate Interactions (${moderate.length})`}>
          <ul className="space-y-2 mt-2">
            {moderate.map((interaction, index) => (
              <li key={index} className="flex items-start gap-2">
                <i className="fas fa-circle text-yellow-600 text-xs mt-1.5 flex-shrink-0" aria-hidden="true"></i>
                <div>
                  {interaction.drug && (
                    <span className="font-semibold">{interaction.drug}: </span>
                  )}
                  <span className="text-sm">{interaction.description}</span>
                </div>
              </li>
            ))}
          </ul>
        </WarningBox>
      )}
    </div>
  );
}

/**
 * FDA Data Attribution
 */
export function FDAAttribution({ className = '' }: { className?: string }) {
  return (
    <div className={`flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg ${className}`}>
      <i className="fas fa-shield-alt text-blue-600 mt-0.5" aria-hidden="true"></i>
      <div className="text-xs text-blue-900">
        <p className="font-semibold mb-1">Information Source: U.S. Food & Drug Administration (FDA)</p>
        <p className="text-blue-800">
          Drug information sourced from FDA via openFDA API. Always consult your healthcare provider
          about the risks and benefits of FDA-regulated products.
        </p>
      </div>
    </div>
  );
}

/**
 * Quick Reference Badge - Shows critical count
 */
interface SafetyBadgeProps {
  contraindications?: number;
  warnings?: number;
  interactions?: number;
  className?: string;
}

export function SafetyBadge({
  contraindications = 0,
  warnings = 0,
  interactions = 0,
  className = ''
}: SafetyBadgeProps) {
  const hasCritical = contraindications > 0;
  const hasWarnings = warnings > 0;
  const hasInteractions = interactions > 0;

  if (!hasCritical && !hasWarnings && !hasInteractions) return null;

  return (
    <div className={`inline-flex items-center gap-3 ${className}`}>
      {hasCritical && (
        <span className="flex items-center gap-1 px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-semibold">
          <i className="fas fa-times-circle" aria-hidden="true"></i>
          {contraindications} Contraindication{contraindications !== 1 ? 's' : ''}
        </span>
      )}
      {hasWarnings && (
        <span className="flex items-center gap-1 px-2 py-1 bg-orange-100 text-orange-800 rounded-full text-xs font-semibold">
          <i className="fas fa-exclamation-triangle" aria-hidden="true"></i>
          {warnings} Warning{warnings !== 1 ? 's' : ''}
        </span>
      )}
      {hasInteractions && (
        <span className="flex items-center gap-1 px-2 py-1 bg-yellow-100 text-yellow-800 rounded-full text-xs font-semibold">
          <i className="fas fa-pills" aria-hidden="true"></i>
          {interactions} Interaction{interactions !== 1 ? 's' : ''}
        </span>
      )}
    </div>
  );
}
