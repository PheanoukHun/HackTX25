import React from 'react';

export const Header: React.FC = () => {
  const logoSrc = "../React-icon.png";

  return (
    <header className="bg-brand-blue shadow-lg">
      <div className="max-w-3xl mx-auto px-4 sm:px-8 py-5">
        <div className="flex items-center gap-4">
          <img src={logoSrc} alt="OptiLife Logo" className="w-12 h-12 rounded-lg" />
          <div>
            <h1 className="text-2xl font-bold text-white font-display">
              OptiLife
            </h1>
            <p className="text-sm text-brand-gray -mt-1">Spend light, sleep tight.</p>
          </div>
        </div>
      </div>
    </header>
  );
};
