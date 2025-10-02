import { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import { healthService } from '../services/api';
import LanguageSelector from './LanguageSelector';
import { SkipLink } from './ScreenReaderOnly';
import { useCareSettings } from '../hooks/useCareSettings';
import CareSettingModal, { CareSettingBadge } from './CareSettingModal';

export default function Layout() {
  const location = useLocation();
  const { t } = useTranslation();
  const { data: healthData } = useQuery({
    queryKey: ['health'],
    queryFn: healthService.checkHealth,
    refetchInterval: 30000, // Refetch every 30 seconds
  });

  // Care Setting Context
  const { careSetting, setCareSetting, isSettingSelected } = useCareSettings();
  const [showCareSettingModal, setShowCareSettingModal] = useState(false);

  const isOnDashboard = location.pathname === '/';

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Skip Navigation Links */}
      <SkipLink href="#main-content">Skip to main content</SkipLink>
      <SkipLink href="#primary-navigation">Skip to navigation</SkipLink>

      {/* Header */}
      <header role="banner" className="bg-white shadow-lg border-b-4 border-blue-600" aria-label="Main navigation">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link
              to="/"
              className="flex items-center space-x-4 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-lg p-2 -m-2"
              aria-label={`${t('common.appName')} - ${t('common.appTagline')}`}
            >
              <div className="bg-blue-600 p-3 rounded-xl" aria-hidden="true">
                <i className="fas fa-user-nurse text-white text-2xl"></i>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">{t('common.appName')}</h1>
                <p className="text-sm text-blue-600 font-medium">{t('common.appTagline')}</p>
              </div>
            </Link>

            {/* Right Side Icons */}
            <nav id="primary-navigation" className="flex items-center space-x-3" aria-label="Primary navigation" role="navigation">
              {/* Care Setting Badge */}
              <CareSettingBadge
                currentSetting={careSetting}
                onClick={() => setShowCareSettingModal(true)}
              />

              {/* Home Icon - Show when not on dashboard */}
              {!isOnDashboard && (
                <Link
                  to="/"
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                  aria-label={`Return to ${t('common.home')}`}
                >
                  <i className="fas fa-house-medical" aria-hidden="true"></i>
                  <span className="font-medium">{t('common.home')}</span>
                </Link>
              )}

              {/* Language Selector */}
              <LanguageSelector />

              {/* Settings Icon */}
              <Link
                to="/settings"
                className="flex items-center justify-center w-10 h-10 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                aria-label="Open settings"
              >
                <i className="fas fa-cog text-xl" aria-hidden="true"></i>
              </Link>

              {/* Help Icon */}
              <button
                onClick={() => {
                  const helpButton = document.querySelector('.help-system-button') as HTMLButtonElement;
                  if (helpButton) {
                    helpButton.click();
                  }
                }}
                className="flex items-center justify-center w-10 h-10 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
                aria-label={`Open ${t('common.help')} menu`}
              >
                <i className="fas fa-question-circle text-xl" aria-hidden="true"></i>
              </button>

              {/* Connection Status */}
              <div
                className="flex items-center space-x-2 bg-gray-50 px-3 py-2 rounded-lg"
                role="status"
                aria-live="polite"
                aria-label={`System status: ${healthData ? 'Connected' : 'Connecting'}`}
              >
                <div
                  className={`w-3 h-3 rounded-full ${healthData ? 'bg-green-500' : 'bg-gray-400'} animate-pulse`}
                  aria-hidden="true"
                ></div>
                <span className="text-sm text-gray-600 font-medium">
                  {healthData ? t('common.connected') : t('common.connecting')}
                </span>
                {healthData && (
                  <span className="text-xs text-gray-500">{t('common.version', { version: healthData.version })}</span>
                )}
              </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main
        id="main-content"
        role="main"
        aria-label="Main content"
        className="max-w-7xl mx-auto px-4 py-6"
        tabIndex={-1}
      >
        <Outlet />
      </main>

      {/* Footer - Only show disclaimer on dashboard */}
      <footer role="contentinfo" className="bg-white border-t mt-12" aria-label="Footer information">
        <div className="max-w-7xl mx-auto px-4 py-4 text-center text-sm text-gray-600">
          {isOnDashboard && (
            <>
              <p className="font-semibold text-blue-600 mb-1">{t('common.footer.disclaimer')}</p>
              <p>{t('common.footer.subtext')}</p>
            </>
          )}
          {!isOnDashboard && (
            <p className="text-gray-500">&copy; {new Date().getFullYear()} AI Nurse Florence</p>
          )}
        </div>
      </footer>

      {/* Care Setting Modal */}
      <CareSettingModal
        isOpen={showCareSettingModal}
        onSelect={(setting) => {
          setCareSetting(setting);
          setShowCareSettingModal(false);
        }}
        onClose={() => setShowCareSettingModal(false)}
        canDismiss={isSettingSelected}
      />
    </div>
  );
}