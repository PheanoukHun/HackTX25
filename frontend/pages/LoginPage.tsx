import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

interface LoginPageProps {
  // You can add props here if needed, e.g., a redirect URL
}

const LoginPage: React.FC<LoginPageProps> = () => {
  const [username, setUsername] = useState<string>('');
  const [password, setPassword] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null); // Clear previous errors

    if (!username || !password) {
      setError('Please enter both username and password.');
      return;
    }

    try {
      const response = await fetch('http://localhost:5000/api/login', { // Assuming Flask runs on 5000
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        console.log('Login successful!', data);
        // Store user data (e.g., in localStorage or context)
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/planPage'); // Redirect to PlanPage
      } else {
        setError(data.error || 'Login failed. Please try again.');
      }
    } catch (err) {
      console.error('Login API call failed:', err);
      setError('Network error or server is unreachable.');
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-brand-blue-light">
      <div className="bg-white shadow-lg p-8 rounded-lg w-96">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Login</h2>

        {error && <p className="text-red-500 text-center mb-4">{error}</p>}

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="username" className="block text-sm font-medium text-gray-700">
              Username
            </label>
            <input
              type="text"
              id="username"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-teal focus:border-brand-teal sm:text-sm"
              value={username}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
            />
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-medium text-gray-700">
              Password
            </label>
            <input
              type="password"
              id="password"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:ring-brand-teal focus:border-brand-teal sm:text-sm"
              value={password}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
            />
          </div>

          <div className="flex items-center justify-end">
            <button
              type="submit"
              className="bg-brand-teal text-white font-bold py-2 px-4 rounded-lg shadow-lg hover:bg-brand-teal-light hover:text-brand-blue transition-all duration-300 flex items-center gap-2"
            >
              Login
            </button>
          </div>
        </form>

        <p className="mt-4 text-sm text-gray-500 text-center">
          Don't have an account? <a href="/formPage" className="text-brand-blue hover:underline">Register</a>
        </p>
      </div>
    </div>
  );
};

export default LoginPage;