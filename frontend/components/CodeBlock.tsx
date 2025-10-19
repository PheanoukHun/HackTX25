
import React from 'react';

interface CodeBlockProps {
  children: React.ReactNode;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ children }) => {
  return (
    <div className="bg-brand-blue-light text-white p-5 rounded-lg border-l-4 border-brand-teal-light shadow-inner">
      <div className="font-sans">{children}</div>
    </div>
  );
};
