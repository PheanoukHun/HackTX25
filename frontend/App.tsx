import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HomePage } from './pages/HomePage';
import { FormPage } from './pages/FormPage';
import { PlanPage } from './pages/PlanPage';
import LoginPage from './pages/loginPage'; // Corrected casing

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
  const [submittedData, setSubmittedData] = useState<FormData | null>(null);

  const handleFormSubmit = (data: FormData) => {
    setSubmittedData(data);
    // In a real application, you would navigate to the plan page here
    // For now, we'll just set the data
  };

  const handleBackToForm = () => {
    setSubmittedData(null);
  };

  return (
    <Router>
      <div className="bg-brand-blue-light min-h-screen text-brand-gray">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/formPage" element={<FormPage onSubmit={handleFormSubmit} />} />
          <Route path="/planPage" element={<PlanPage formData={submittedData} onBack={handleBackToForm} />} />
          <Route path="/loginPage" element={<LoginPage />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
