import React, { useState } from 'react';
import { FormSection, Input, Select, RangeSlider } from '../components/FormControls';
import { CheckCircleIcon, DollarSignIcon, SparklesIcon, UserIcon } from '../components/Icons';
import type { FormData } from '../App';
import { useNavigate } from 'react-router-dom';

const initialFormData: FormData = {
  // About You
  name: "Sami Miri",
  age: 21,
  employment_status: "Student",
  location: "Austin, TX",

  // Lifestyle & Habits
  housing_situation: "Renting",
  dining_habits: "Mix of Both",
  monthly_subscriptions: 75,

  // Financial Snapshot (Simplified)
  monthly_income: 3200,
  monthly_expenses: 1800,
  total_debt: 400,
  credit_score: 700,
  bank_account_balance: 3700,

  // Your Goal
  financial_goal: "Buy first car",
  financial_confidence_score: 6,
};

interface FormPageProps {
    onSubmit: (data: FormData) => void;
}

export const FormPage: React.FC<FormPageProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<FormData>(initialFormData);
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    const isNumber = type === 'number';
    setFormData(prev => ({
      ...prev,
      [name]: isNumber ? (value === '' ? '' : Number(value)) : value,
    }));
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
    navigate('/planPage');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-8 bg-brand-blue-light">
      
      <FormSection title="About You" icon={<UserIcon />} description="Let's start with some basic information.">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Input label="Full Name" name="name" value={formData.name} onChange={handleChange} />
          <Input label="Age" name="age" type="number" value={formData.age} onChange={handleChange} />
          <Select label="Employment Status" name="employment_status" value={formData.employment_status} onChange={handleChange} options={['Student', 'Employed', 'Self-Employed', 'Unemployed']} />
          <Input label="Location (City, State)" name="location" value={formData.location} onChange={handleChange} />
        </div>
      </FormSection>

      <FormSection title="Lifestyle & Habits" icon={<SparklesIcon />} description="Tell us about your daily life to create a holistic financial picture.">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Select label="Housing Situation" name="housing_situation" value={formData.housing_situation} onChange={handleChange} options={['Renting', 'Owning', 'Living with Family', 'Other']} />
          <Select label="Dining Habits" name="dining_habits" value={formData.dining_habits} onChange={handleChange} options={['Mostly Cook at Home', 'Frequent Dining Out', 'Mix of Both']} />
          <Input label="Monthly Subscriptions & Memberships" name="monthly_subscriptions" type="number" value={formData.monthly_subscriptions} onChange={handleChange} prefix="$"/>
        </div>
      </FormSection>

      <FormSection title="Financial Snapshot" icon={<DollarSignIcon />} description="Provide a high-level picture of your current finances.">
         <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Input 
              label="Monthly Income" 
              name="monthly_income" 
              type="number" 
              value={formData.monthly_income} 
              onChange={handleChange} 
              prefix="$"
              tooltip="Your total take-home pay per month after taxes and other deductions."
            />
            <Input 
              label="Estimated Total Monthly Expenses" 
              name="monthly_expenses" 
              type="number" 
              value={formData.monthly_expenses} 
              onChange={handleChange} 
              prefix="$"
              tooltip="Include all regular monthly costs like rent/mortgage, utilities, groceries, transportation, and entertainment."
            />
            <Input 
              label="Total Debt" 
              name="total_debt" 
              type="number" 
              value={formData.total_debt} 
              onChange={handleChange} 
              prefix="$"
              tooltip="The combined total of all outstanding loans, such as student loans, credit card balances, and personal loans."
            />
            <Input 
              label="Credit Score" 
              name="credit_score" 
              type="number" 
              value={formData.credit_score} 
              onChange={handleChange}
              tooltip="A number between 300-850 that estimates your creditworthiness. You can find this on your credit card statement or a free credit report website."
            />
            <Input 
              label="Total Bank Account Balance" 
              name="bank_account_balance" 
              type="number" 
              value={formData.bank_account_balance} 
              onChange={handleChange} 
              prefix="$"
              tooltip="The sum of all funds in your checking and savings accounts."
            />
         </div>
      </FormSection>

      <FormSection title="Your Goal" icon={<CheckCircleIcon />} description="Describe your primary financial goal.">
        <Input label="Financial Goal" name="financial_goal" value={formData.financial_goal} onChange={handleChange} placeholder="e.g., Save for a down payment, pay off debt..." />
        <RangeSlider label="Financial Confidence Score" name="financial_confidence_score" value={formData.financial_confidence_score} onChange={handleChange} min={1} max={10} />
      </FormSection>

      <div className="flex justify-end pt-4">
        <button type="submit" className="bg-brand-teal text-white font-bold py-3 px-8 rounded-lg shadow-lg hover:bg-brand-teal-light hover:text-brand-blue transition-all duration-300 flex items-center gap-2">
          Generate My Plan
        </button>
      </div>
    </form>
  );
}
