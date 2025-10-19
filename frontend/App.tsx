import React, { useState } from 'react';
import { Header } from './components/Header';
import { FormPage } from './pages/FormPage';
import { PlanPage } from './pages/PlanPage';
//import { LoginPage } from './pages/LoginPage';

export interface FormData {
  // About You
  name: string;
  age: number;
  employment_status: string;
  location: string;
  // Lifestyle & Habits
  housing_situation: string;
  dining_habits: string;
  monthly_subscriptions: number;
  // Financial Snapshot (Simplified)
  monthly_income: number;
  monthly_expenses: number;
  total_debt: number;
  credit_score: number;
  bank_account_balance: number;
  // Your Goal
  financial_goal: string;
  financial_confidence_score: number;
}

const App: React.FC = () => {
  const [page, setPage] = useState<'form' | 'plan'>('form');
  const [submittedData, setSubmittedData] = useState<FormData | null>(null);

  const handleFormSubmit = (data: FormData) => {
    setSubmittedData(data);
    setPage('plan');
  };

  const handleBackToForm = () => {
    setSubmittedData(null);
    setPage('form');
  };

  return (
    <div className="bg-brand-blue-light min-h-screen text-brand-gray">
      <Header />
      <main className="max-w-3xl mx-auto p-4 sm:p-8">
        {page === 'form' && <FormPage onSubmit={handleFormSubmit} />}
        {page === 'plan' && submittedData && (
          <PlanPage formData={submittedData} onBack={handleBackToForm} />
        )}
      </main>
    </div>
  );
}

export default App;