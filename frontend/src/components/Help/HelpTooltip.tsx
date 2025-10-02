import React, { useState } from 'react';

interface HelpTooltipProps {
  content: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
}

/**
 * Contextual Help Tooltip Component
 *
 * Displays helpful information when users hover over or click on an element.
 * Use this to provide inline guidance without cluttering the interface.
 *
 * Usage:
 * <HelpTooltip content="Explanation of this field">
 *   <input type="text" />
 * </HelpTooltip>
 */
export function HelpTooltip({ content, children, position = 'top' }: HelpTooltipProps) {
  const [isVisible, setIsVisible] = useState(false);

  const positionClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2',
  };

  return (
    <div
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}

      {isVisible && (
        <div
          className={`absolute z-50 ${positionClasses[position]} w-64`}
          role="tooltip"
        >
          <div className="bg-gray-900 text-white text-sm px-3 py-2 rounded shadow-lg">
            <div className="flex items-start space-x-2">
              <i className="fas fa-info-circle text-blue-400 mt-0.5 flex-shrink-0"></i>
              <p>{content}</p>
            </div>
          </div>

          {/* Arrow */}
          <div className={`absolute w-2 h-2 bg-gray-900 transform rotate-45 ${
            position === 'top' ? 'bottom-0 left-1/2 -translate-x-1/2 translate-y-1' :
            position === 'bottom' ? 'top-0 left-1/2 -translate-x-1/2 -translate-y-1' :
            position === 'left' ? 'right-0 top-1/2 -translate-y-1/2 translate-x-1' :
            'left-0 top-1/2 -translate-y-1/2 -translate-x-1'
          }`}></div>
        </div>
      )}
    </div>
  );
}

/**
 * Helper component: Info Icon with Tooltip
 *
 * A small info icon that shows a tooltip on hover.
 * Use next to form labels or section headers.
 *
 * Usage:
 * <label>
 *   Patient Language <InfoTooltip content="Choose the language..." />
 * </label>
 */
export function InfoTooltip({ content }: { content: string }) {
  return (
    <HelpTooltip content={content}>
      <i className="fas fa-info-circle text-gray-400 hover:text-blue-600 cursor-help ml-1 text-sm"></i>
    </HelpTooltip>
  );
}

export default HelpTooltip;
