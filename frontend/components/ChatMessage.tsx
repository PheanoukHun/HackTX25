import React from 'react';
import { marked } from 'marked';

interface Message {
  role: 'user' | 'model';
  text: string;
}

interface ChatMessageProps {
  message: Message;
}

// Configure marked to interpret single newlines as <br> tags for better formatting.
marked.setOptions({
  breaks: true,
});

const logoSrc = "../logo.png";

const TypingIndicator: React.FC = () => (
    <div className="flex items-center gap-1.5">
        <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
        <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
        <span className="w-2 h-2 bg-slate-500 rounded-full animate-bounce"></span>
    </div>
);


export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isModel = message.role === 'model';
  
  const createMarkup = (text: string) => {
    // Basic sanitization for security
    const sanitizedHtml = marked.parse(text);
    return { __html: sanitizedHtml };
  };

  if (isModel) {
    return (
      <div className="flex items-start gap-3">
        <img src={logoSrc} alt="OptiLife Logo" className="w-8 h-8 rounded-full flex-shrink-0 mt-1" />
        <div className="bg-brand-blue-light rounded-lg rounded-tl-none p-4 text-brand-gray flex-1">
          {message.text === '...' ? <TypingIndicator /> : (
            <div className="prose prose-invert prose-sm max-w-none" dangerouslySetInnerHTML={createMarkup(message.text)} />
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-end">
      <div className="bg-brand-teal text-white rounded-lg rounded-br-none p-4 max-w-xl">
        <p className="whitespace-pre-wrap">{message.text}</p>
      </div>
    </div>
  );
};