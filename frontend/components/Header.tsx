import React from 'react';
import { LogoIcon } from './Icons';

export const Header: React.FC = () => {
  return (
    <header className="bg-brand-blue shadow-lg">
      <div className="max-w-3xl mx-auto px-4 sm:px-8 py-5">
        <div className="flex items-center gap-4">
          <LogoIcon />
          <div>
            <h1 className="text-2xl font-bold text-white font-display">
              FinAI
            </h1>
            <p className="text-sm text-brand-gray -mt-1">Personalized Car Financing</p>
          </div>
        </div>
      </div>
    </header>
  );
};
