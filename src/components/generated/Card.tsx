import React from 'react';

interface CardProps {
  children: React.ReactNode;
  variant?: 'default' | 'elevated' | 'outlined';
  padding?: 'none' | 'small' | 'medium' | 'large';
  className?: string;
}

/**
 * Card component - Phase 3 Complete Automation
 * Auto-generated with advanced features
 */
export const Card: React.FC<CardProps> = ({ 
  children, 
  variant = 'default',
  padding = 'medium',
  className = ''
}) => {
  const baseClasses = 'rounded-lg transition-all duration-200';
  
  const variantClasses = {
    default: 'bg-white border border-gray-200',
    elevated: 'bg-white shadow-lg hover:shadow-xl',
    outlined: 'bg-transparent border-2 border-gray-300 hover:border-gray-400'
  }[variant];
  
  const paddingClasses = {
    none: '',
    small: 'p-3',
    medium: 'p-4',
    large: 'p-6'
  }[padding];
  
  return (
    <div className={`${baseClasses} ${variantClasses} ${paddingClasses} ${className}`}>
      {children}
    </div>
  );
};