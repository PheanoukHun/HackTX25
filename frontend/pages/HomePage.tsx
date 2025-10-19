import React from 'react';
import { useNavigate } from 'react-router-dom';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const logoSrc = "../React-icon.png"; // Assuming the logo is in the same relative path as in Header.tsx

  const handleRegisterClick = () => {
    navigate('/formPage');
  };

  const handleLoginClick = () => {
    navigate('/loginPage');
  };

  return (
    <div className="min-h-screen bg-brand-blue-light flex flex-col items-center justify-center">
      <header className="bg-brand-blue shadow-lg w-full py-5">
        <div className="max-w-3xl mx-auto px-4 sm:px-8">
          <div className="flex items-center gap-4 justify-center">
            <img src={logoSrc} alt="OptiLife Logo" className="w-16 h-16 rounded-lg" />
            <div>
              <h1 className="text-3xl font-bold text-white font-display">
                OptiLife
              </h1>
              <p className="text-md text-brand-gray -mt-1">Spend light, sleep tight.</p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex flex-col items-center justify-center flex-grow p-8">
        <div className="space-x-10">
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
      </main>
    </div>
  );
};