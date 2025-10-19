
import React from 'react';
import type { Persona } from '../types';
import { CheckIcon, XMarkIcon } from './Icons';

interface PersonaCardProps {
  persona: Persona;
}

export const PersonaCard: React.FC<PersonaCardProps> = ({ persona }) => {
  return (
    <div className="bg-slate-50 rounded-lg shadow-sm border border-slate-200 p-5 flex flex-col sm:flex-row gap-5 items-start">
      <img src={persona.imageUrl} alt={persona.name} className="w-24 h-24 rounded-full border-4 border-white shadow-md mx-auto sm:mx-0" />
      <div className="flex-1 text-center sm:text-left">
        <h3 className="text-xl font-bold text-brand-blue">{persona.name}</h3>
        <p className="text-md text-brand-teal font-semibold mb-3">{persona.role}</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <h4 className="font-semibold text-slate-800 mb-2">Goals</h4>
            <ul className="space-y-1.5">
              {persona.goals.map(goal => (
                <li key={goal} className="flex items-start gap-2">
                  <CheckIcon className="text-green-500 mt-1 flex-shrink-0" />
                  <span>{goal}</span>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-slate-800 mb-2">Pain Points</h4>
            <ul className="space-y-1.5">
              {persona.painPoints.map(point => (
                <li key={point} className="flex items-start gap-2">
                  <XMarkIcon className="text-red-500 mt-1 flex-shrink-0" />
                  <span>{point}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};
