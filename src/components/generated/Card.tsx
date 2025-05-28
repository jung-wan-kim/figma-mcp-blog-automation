import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps {
  variant?: 'default' | 'elevated' | 'outlined';
  children: React.ReactNode;
  className?: string;
}

const Card: React.FC<CardProps> = ({
  variant = 'default',
  children,
  className
}) => {
  const baseClasses = 'rounded-lg bg-white p-6';
  
  const variantClasses = {
    default: 'border border-gray-200',
    elevated: 'shadow-lg',
    outlined: 'border-2 border-gray-300'
  };

  return (
    <div className={cn(baseClasses, variantClasses[variant], className)}>
      {children}
    </div>
  );
};

export default Card;
