import React from 'react';
import { useTranslation } from 'react-i18next';
import { setDocumentDirection } from '../i18n';

const LanguageSwitcher = ({ className = '', variant = 'default' }) => {
  const { i18n, t } = useTranslation();
  const currentLang = i18n.language;
  
  const toggleLanguage = () => {
    // Toggle between English and Arabic
    const newLang = currentLang === 'ar' ? 'en' : 'ar';
    
    // Change language in i18next
    i18n.changeLanguage(newLang);
    
    // Update document direction
    setDocumentDirection(newLang);
  };
  
  // Different styles based on variant
  const getButtonStyles = () => {
    switch(variant) {
      case 'login':
        return `px-3 py-1.5 rounded-lg transition-colors ${
          currentLang === 'ar' 
            ? 'bg-white text-indigo-600 hover:bg-indigo-50' 
            : 'bg-white text-indigo-600 hover:bg-indigo-50'
        }`;
      default:
        return `px-3 py-1.5 rounded-lg transition-colors ${
          currentLang === 'ar' 
            ? 'bg-blue-600 hover:bg-blue-700 text-white' 
            : 'bg-indigo-600 hover:bg-indigo-700 text-white'
        }`;
    }
  };
  
  return (
    <button
      onClick={toggleLanguage}
      className={`${getButtonStyles()} ${className}`}
      aria-label={t('language')}
    >
      {currentLang === 'ar' ? 'English' : 'العربية'}
    </button>
  );
};

export default LanguageSwitcher; 