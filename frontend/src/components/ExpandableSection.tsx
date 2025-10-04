import { useState, ReactNode } from 'react';

/**
 * Expandable Section Component
 *
 * Reusable component for progressive disclosure in templates.
 * Ideal for medication guides, patient education, and clinical documents.
 */

export type SectionVariant = 'default' | 'warning' | 'critical' | 'info' | 'success';

interface ExpandableSectionProps {
  /** Section title */
  title: string;
  /** Icon class (FontAwesome) */
  icon?: string;
  /** Section content */
  children: ReactNode;
  /** Visual variant */
  variant?: SectionVariant;
  /** Initially expanded? */
  defaultExpanded?: boolean;
  /** Badge count (e.g., "5 items") */
  badge?: string | number;
  /** Disabled state */
  disabled?: boolean;
  /** Additional CSS classes */
  className?: string;
}

export default function ExpandableSection({
  title,
  icon,
  children,
  variant = 'default',
  defaultExpanded = false,
  badge,
  disabled = false,
  className = ''
}: ExpandableSectionProps) {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  const variantStyles: Record<SectionVariant, {
    container: string;
    header: string;
    icon: string;
    badge: string;
  }> = {
    default: {
      container: 'border-gray-200 bg-white',
      header: 'bg-gray-50 hover:bg-gray-100 text-gray-800',
      icon: 'text-gray-600',
      badge: 'bg-gray-200 text-gray-700'
    },
    warning: {
      container: 'border-yellow-300 bg-yellow-50',
      header: 'bg-yellow-100 hover:bg-yellow-200 text-yellow-900',
      icon: 'text-yellow-600',
      badge: 'bg-yellow-200 text-yellow-800'
    },
    critical: {
      container: 'border-red-400 bg-red-50',
      header: 'bg-red-100 hover:bg-red-200 text-red-900',
      icon: 'text-red-600',
      badge: 'bg-red-200 text-red-800'
    },
    info: {
      container: 'border-blue-300 bg-blue-50',
      header: 'bg-blue-100 hover:bg-blue-200 text-blue-900',
      icon: 'text-blue-600',
      badge: 'bg-blue-200 text-blue-800'
    },
    success: {
      container: 'border-green-300 bg-green-50',
      header: 'bg-green-100 hover:bg-green-200 text-green-900',
      icon: 'text-green-600',
      badge: 'bg-green-200 text-green-800'
    }
  };

  const styles = variantStyles[variant];

  return (
    <div className={`border-2 rounded-lg overflow-hidden ${styles.container} ${className}`}>
      {/* Header - Clickable to expand/collapse */}
      <button
        onClick={() => !disabled && setIsExpanded(!isExpanded)}
        disabled={disabled}
        className={`w-full px-4 py-3 flex items-center justify-between transition-colors ${styles.header} ${
          disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        }`}
        aria-expanded={isExpanded}
        aria-controls={`section-${title.replace(/\s+/g, '-').toLowerCase()}`}
      >
        <div className="flex items-center gap-3">
          {/* Expand/Collapse Icon */}
          <i
            className={`fas fa-chevron-${isExpanded ? 'down' : 'right'} ${styles.icon} text-sm transition-transform`}
            aria-hidden="true"
          ></i>

          {/* Custom Icon */}
          {icon && (
            <i className={`fas ${icon} ${styles.icon} text-lg`} aria-hidden="true"></i>
          )}

          {/* Title */}
          <span className="font-semibold text-left">{title}</span>

          {/* Badge */}
          {badge && (
            <span className={`ml-2 px-2 py-0.5 rounded-full text-xs font-medium ${styles.badge}`}>
              {badge}
            </span>
          )}
        </div>

        {/* Accessibility hint */}
        <span className="sr-only">{isExpanded ? 'Click to collapse' : 'Click to expand'}</span>
      </button>

      {/* Content - Shown when expanded */}
      {isExpanded && (
        <div
          id={`section-${title.replace(/\s+/g, '-').toLowerCase()}`}
          className="px-4 py-4 bg-white"
        >
          {children}
        </div>
      )}
    </div>
  );
}

/**
 * Pre-configured Warning Section
 */
interface WarningSectionProps {
  title?: string;
  children: ReactNode;
  badge?: string | number;
  defaultExpanded?: boolean;
  className?: string;
}

export function WarningSection({
  title = 'Important Warnings',
  children,
  badge,
  defaultExpanded = false,
  className = ''
}: WarningSectionProps) {
  return (
    <ExpandableSection
      title={title}
      icon="fa-exclamation-triangle"
      variant="warning"
      badge={badge}
      defaultExpanded={defaultExpanded}
      className={className}
    >
      {children}
    </ExpandableSection>
  );
}

/**
 * Pre-configured Critical Warning Section
 */
export function CriticalWarningSection({
  title = 'Critical Safety Information',
  children,
  badge,
  defaultExpanded = true,
  className = ''
}: WarningSectionProps) {
  return (
    <ExpandableSection
      title={title}
      icon="fa-exclamation-circle"
      variant="critical"
      badge={badge}
      defaultExpanded={defaultExpanded}
      className={className}
    >
      {children}
    </ExpandableSection>
  );
}

/**
 * Pre-configured Info Section
 */
export function InfoSection({
  title = 'Information',
  children,
  badge,
  defaultExpanded = false,
  className = ''
}: WarningSectionProps) {
  return (
    <ExpandableSection
      title={title}
      icon="fa-info-circle"
      variant="info"
      badge={badge}
      defaultExpanded={defaultExpanded}
      className={className}
    >
      {children}
    </ExpandableSection>
  );
}
