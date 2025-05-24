import React from 'react';

interface CardProps {
  children: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'small' | 'medium' | 'large';
  className?: string;
}

/**
 * Card component - Phase 3 Complete Automation
 * Auto-generated from Figma with full pipeline integration
 * Features: Multiple variants, flexible padding, accessibility
 */
export const Card: React.FC<CardProps> = ({ 
  children, 
  variant = 'default',
  padding = 'medium',
  className = ''
}) => {
  const baseClasses = 'rounded-lg transition-all duration-200 focus-within:ring-2 focus-within:ring-blue-500 focus-within:ring-offset-2';
  
  const variantClasses = {
    default: 'bg-white border border-gray-200 hover:border-gray-300',
    elevated: 'bg-white shadow-md hover:shadow-lg',
    outlined: 'bg-transparent border-2 border-gray-300 hover:border-gray-400'
  }[variant];
  
  const paddingClasses = {
    none: '',
    small: 'p-3',
    medium: 'p-4',
    large: 'p-6'
  }[padding];
  
  return (
    <div 
      className={`${baseClasses} ${variantClasses} ${paddingClasses} ${className}`}
      role="article"
      tabIndex={0}
    >
      {children}
    </div>
  );
};
