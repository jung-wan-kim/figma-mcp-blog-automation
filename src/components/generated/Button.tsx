import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
}

/**
 * Auto-generated Button component from Figma
 * Generated at: $(date)
 * TaskManager MCP Pipeline
 */
export const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  onClick 
}) => {
  const baseClasses = 'px-4 py-2 rounded font-medium transition-colors focus:outline-none focus:ring-2';
  const variantClasses = variant === 'primary' 
    ? 'bg-blue-500 hover:bg-blue-600 text-white focus:ring-blue-300'
    : 'bg-gray-200 hover:bg-gray-300 text-gray-800 focus:ring-gray-300';
  const sizeClasses = {
    small: 'text-sm px-3 py-1',
    medium: 'text-base px-4 py-2', 
    large: 'text-lg px-6 py-3'
  }[size];
  
  return (
    <button 
      className={`${baseClasses} ${variantClasses} ${sizeClasses}`}
      onClick={onClick}
    >
      {children}
    </button>
  );
};
