
import React from 'react';

interface SectionProps {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}

export const Section: React.FC<SectionProps> = ({ title, icon, children }) => {
  return (
    <section className="mb-10 sm:mb-12 bg-white p-6 rounded-xl shadow-md border border-slate-200">
      <div className="flex items-center gap-3 mb-4 border-b border-slate-200 pb-4">
        <div className="text-brand-teal">{icon}</div>
        <h2 className="text-2xl font-bold text-brand-blue font-display">{title}</h2>
      </div>
      <div>{children}</div>
    </section>
  );
};
