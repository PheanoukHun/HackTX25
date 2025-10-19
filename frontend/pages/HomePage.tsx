import React from 'react';
import { useNavigate } from 'react-router-dom';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const logoSrc = "../logo.png"; // Assuming the logo is in the same relative path as in Header.tsx

  const handleRegisterClick = () => {
    navigate('/formPage');
  };

  const handleLoginClick = () => {
    navigate('/loginPage');
  };

  return (
    <div className="min-h-screen bg-brand-blue-light flex flex-col items-center justify-center">
      <div className="flex flex-col items-center mb-8">
        <img src={logoSrc} alt="OptiLife Logo" className="w-24 h-24 rounded-lg mb-4" />
        <div>
          <h1 className="text-5xl font-bold text-white font-display text-center">
            OptiLife
          </h1>
          <p className="text-xl text-brand-gray -mt-1 text-center">Spend light, sleep tight.</p>
        </div>
      </div>

      <div className="space-x-10 mt-8">
        <button
          onClick={handleRegisterClick}
          className="w-50 py-5 px-8 bg-green-800 text-white font-semibold rounded-lg shadow-md hover:bg-green-900 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-75 transition duration-300"
        >
          Register
        </button>
        <button
          onClick={handleLoginClick}
          className="w-50 py-5 px-8 bg-purple-800 text-white font-semibold rounded-lg shadow-md hover:bg-purple-900 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-opacity-75 transition duration-300"
        >
          Login
        </button>
      </div>
    </div>
  );
};