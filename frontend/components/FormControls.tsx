import React from 'react';

// Form Section Wrapper
interface FormSectionProps {
  title: string;
  icon: React.ReactNode;
  description: string;
  children: React.ReactNode;
}
export const FormSection: React.FC<FormSectionProps> = ({ title, icon, description, children }) => (
  <section className="bg-brand-blue p-6 rounded-xl shadow-lg border border-slate-700">
    <div className="flex items-center gap-4 mb-2">
      <div className="text-brand-teal-light">{icon}</div>
      <div>
        <h2 className="text-xl font-bold text-white font-display">{title}</h2>
        <p className="text-sm text-slate-400 -mt-1">{description}</p>
      </div>
    </div>
    <div className="pt-4 border-t border-slate-700/50">{children}</div>
  </section>
);

// Generic Input
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
  prefix?: string;
}
export const Input: React.FC<InputProps> = ({ label, name, prefix, ...props }) => (
  <div>
    <label htmlFor={name} className="block text-sm font-medium text-brand-gray mb-1">{label}</label>
    <div className="relative">
       {prefix && <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-slate-400">{prefix}</span>}
      <input
        id={name}
        name={name}
        className={`w-full bg-brand-blue-light border border-slate-600 rounded-md py-2 text-white focus:ring-brand-teal-light focus:border-brand-teal-light transition ${prefix ? 'pl-7' : 'px-3'}`}
        {...props}
      />
    </div>
  </div>
);

// Generic Select
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string;
  options: (string | {label: string, value: string})[];
}
export const Select: React.FC<SelectProps> = ({ label, name, options, ...props }) => (
  <div>
    <label htmlFor={name} className="block text-sm font-medium text-brand-gray mb-1">{label}</label>
    <select
      id={name}
      name={name}
      className="w-full bg-brand-blue-light border border-slate-600 rounded-md py-2 px-3 text-white focus:ring-brand-teal-light focus:border-brand-teal-light transition"
      {...props}
    >
      {options.map(option => (
        typeof option === 'string' ?
        <option key={option} value={option}>{option}</option> :
        <option key={option.value} value={option.value}>{option.label}</option>
      ))}
    </select>
  </div>
);

// Radio Group
interface RadioGroupProps {
  label: string;
  name: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  options: string[];
}
export const RadioGroup: React.FC<RadioGroupProps> = ({ label, name, value, onChange, options }) => (
  <div>
    <label className="block text-sm font-medium text-brand-gray mb-2">{label}</label>
    <div className="flex gap-4 items-center">
      {options.map(option => (
        <label key={option} className="flex items-center gap-2 cursor-pointer">
          <input
            type="radio"
            name={name}
            value={option}
            checked={value === option}
            onChange={onChange}
            className="w-4 h-4 text-brand-teal bg-slate-700 border-slate-500 focus:ring-brand-teal-light"
          />
          <span className="text-white">{option}</span>
        </label>
      ))}
    </div>
  </div>
);

// Range Slider
interface RangeSliderProps extends React.InputHTMLAttributes<HTMLInputElement> {
    label: string;
}
export const RangeSlider: React.FC<RangeSliderProps> = ({ label, name, value, ...props }) => (
    <div>
        <label htmlFor={name} className="block text-sm font-medium text-brand-gray mb-1">{label}: <span className="font-bold text-brand-teal-light text-base">{value}</span></label>
        <input
            type="range"
            id={name}
            name={name}
            value={value}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-brand-teal"
            {...props}
        />
    </div>
);
