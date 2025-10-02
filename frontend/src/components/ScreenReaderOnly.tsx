import { ReactNode } from 'react';

interface ScreenReaderOnlyProps {
  children: ReactNode;
  as?: keyof JSX.IntrinsicElements;
}

/**
 * Component that renders content only visible to screen readers
 * Uses CSS to hide content visually while keeping it accessible
 */
export default function ScreenReaderOnly({ children, as: Component = 'span' }: ScreenReaderOnlyProps) {
  return (
    <Component className="sr-only">
      {children}
    </Component>
  );
}

/**
 * Live region component for announcing dynamic content to screen readers
 */
interface LiveRegionProps {
  children: ReactNode;
  politeness?: 'polite' | 'assertive' | 'off';
  atomic?: boolean;
  relevant?: 'additions' | 'removals' | 'text' | 'all' | 'additions text';
}

export function LiveRegion({
  children,
  politeness = 'polite',
  atomic = true,
  relevant = 'additions text'
}: LiveRegionProps) {
  return (
    <div
      role="status"
      aria-live={politeness}
      aria-atomic={atomic}
      aria-relevant={relevant}
      className="sr-only"
    >
      {children}
    </div>
  );
}

/**
 * Skip link component for keyboard navigation
 */
export function SkipLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      href={href}
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:bg-blue-600 focus:text-white focus:px-4 focus:py-2 focus:rounded-lg focus:shadow-lg"
    >
      {children}
    </a>
  );
}
