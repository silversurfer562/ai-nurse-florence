import { useEffect, RefObject } from 'react';

interface KeyboardNavigationOptions {
  onEnter?: () => void;
  onEscape?: () => void;
  onArrowUp?: () => void;
  onArrowDown?: () => void;
  onArrowLeft?: () => void;
  onArrowRight?: () => void;
  onTab?: () => void;
  onShiftTab?: () => void;
}

/**
 * Custom hook for keyboard navigation
 * Handles common keyboard interactions for accessibility
 */
export function useKeyboardNavigation(
  ref: RefObject<HTMLElement>,
  options: KeyboardNavigationOptions
) {
  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'Enter':
          if (options.onEnter) {
            e.preventDefault();
            options.onEnter();
          }
          break;

        case 'Escape':
          if (options.onEscape) {
            e.preventDefault();
            options.onEscape();
          }
          break;

        case 'ArrowUp':
          if (options.onArrowUp) {
            e.preventDefault();
            options.onArrowUp();
          }
          break;

        case 'ArrowDown':
          if (options.onArrowDown) {
            e.preventDefault();
            options.onArrowDown();
          }
          break;

        case 'ArrowLeft':
          if (options.onArrowLeft) {
            e.preventDefault();
            options.onArrowLeft();
          }
          break;

        case 'ArrowRight':
          if (options.onArrowRight) {
            e.preventDefault();
            options.onArrowRight();
          }
          break;

        case 'Tab':
          if (e.shiftKey && options.onShiftTab) {
            e.preventDefault();
            options.onShiftTab();
          } else if (!e.shiftKey && options.onTab) {
            e.preventDefault();
            options.onTab();
          }
          break;
      }
    };

    element.addEventListener('keydown', handleKeyDown);

    return () => {
      element.removeEventListener('keydown', handleKeyDown);
    };
  }, [ref, options]);
}

/**
 * Hook for managing focus trapping within a container
 * Useful for modals and dropdowns
 */
export function useFocusTrap(ref: RefObject<HTMLElement>, isActive: boolean) {
  useEffect(() => {
    if (!isActive) return;

    const element = ref.current;
    if (!element) return;

    const focusableElements = element.querySelectorAll<HTMLElement>(
      'a[href], button:not([disabled]), textarea:not([disabled]), input:not([disabled]), select:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault();
          lastElement?.focus();
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault();
          firstElement?.focus();
        }
      }
    };

    element.addEventListener('keydown', handleTab);

    // Focus first element when activated
    firstElement?.focus();

    return () => {
      element.removeEventListener('keydown', handleTab);
    };
  }, [ref, isActive]);
}

/**
 * Hook for announcing messages to screen readers
 */
export function useScreenReaderAnnounce() {
  const announce = (message: string, politeness: 'polite' | 'assertive' = 'polite') => {
    const announcement = document.createElement('div');
    announcement.setAttribute('role', 'status');
    announcement.setAttribute('aria-live', politeness);
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;

    document.body.appendChild(announcement);

    // Remove after announcement
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  };

  return announce;
}
