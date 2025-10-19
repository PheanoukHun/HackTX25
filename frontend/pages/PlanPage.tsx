import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI, Chat } from '@google/genai';
import { marked } from 'marked';
import type { FormData } from '../App';
import { ChatMessage } from '../components/ChatMessage';
import SendTranscriptOnUnmount from '../components/SendTranscriptOnUnmount'; // Import the component

interface PlanPageProps {
  formData: FormData;
  onBack: () => void;
}

interface Message {
  role: 'user' | 'model';
  text: string;
}

export const PlanPage: React.FC<PlanPageProps> = ({ formData, onBack }) => {
  const [chat, setChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [userInput, setUserInput] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    const initChat = async () => {
      try {
        const ai = new GoogleGenAI({ apiKey: 'AIzaSyCtC0f5wTHaoFihZBNROok1vjlp9cGCSuw' });
        const newChat = ai.chats.create({
          model: 'gemini-2.5-flash',
        });
        setChat(newChat);

        const initialPrompt = `
You are OptiLife, an expert financial advisor AI.

OVERALL STYLE GUIDE (Follow for ALL responses):

Persona: Act like a real human advisor, not a robot. Your tone should be encouraging, empathetic, and professional. If discussing cars, be a helpful expert from Toyota and Capital One. If discussing general finance, be a supportive advisor from Capital One.

Brevity: Keep all your responses concise and to the point.

Action Plan Structure: Present your advice as a simple, numbered list. IMPORTANT: Do NOT use the word 'Step' in your responses (e.g., do not write "Step 1"). Just use the numbers to guide the user through the plan naturally.

Readability: For easier reading, use double line breaks (an empty line) between paragraphs and distinct points to create more visual space.

---

A new user, ${formData.name}, has provided their information. Your first task is to analyze their primary goal: "${formData.financial_goal}".

PRIMARY INSTRUCTION: Check the user's goal.

IF the user's goal mentions buying a vehicle (e.g., car, truck, automobile):
Your role shifts to a specialized auto-financing advisor. Create a conversational, numbered action plan following the style guide above.

1. Welcome & Recommend a Toyota.
Welcome ${formData.name}. Based on their profile, recommend a specific, appropriate Toyota model.
Briefly justify why it's a good fit, referencing Toyota’s core advantages — reliability, resale value, and cost efficiency.
Mention that Toyota Financial Services and Capital One can both help them access flexible payment plans or pre-qualification options.

2. Share User Reviews.
To build trust, simulate finding user reviews. Present 1–2 summarized, realistic user reviews for the recommended model.
Start this section with "Here's what other owners are saying:".
Highlight benefits like fuel efficiency, comfort, tech features, and resale reliability.

3. Provide a Financing Simulation.
Provide a clear, estimated monthly payment simulation.
Base your calculation on their income ({formData.monthly_income}), credit score (${formData.credit_score}), and debt ({formData.total_debt}).
State your assumptions clearly (e.g., interest rate, loan term, and down payment).
Then, compare how Toyota Financial Services vs Capital One Auto Finance could structure their financing — mention things like pre-approval, flexible APRs, or loyalty discounts.

4. Engage and Ask.
End with an open-ended question to encourage conversation, like:
“How does this initial plan look, ${formData.name}? Would you like to explore a Toyota pre-qualification through Capital One, or view another model’s financing plan?”

ELSE (if the goal is NOT about a vehicle):
Follow your standard procedure. Create a numbered, step-by-step action plan to help them move towards their goal.

1. Welcome & Acknowledge.
Start with a warm welcome to ${formData.name} and state the first action.

2–4. Provide Actionable Steps.
Present the next most impactful, small, and actionable steps.
For each step, briefly explain why it's important based on their specific financial situation.
Use Capital One insights or savings products where relevant (e.g., budgeting, debt management, or credit improvement).

5. Engage and Ask.
End with a question to encourage conversation, like “Which of these first steps feels most achievable for you right now?”

General Rule:
If you need more information from the user to provide a better recommendation, feel free to ask them.

User Data for Analysis:

Name: ${formData.name}

Age: ${formData.age}

Employment: ${formData.employment_status}

Monthly Income: $${formData.monthly_income}

Monthly Expenses: $${formData.monthly_expenses}

Total Debt: $${formData.total_debt}

Bank Balance: $${formData.bank_account_balance}

Credit Score: ${formData.credit_score}

Primary Goal: "${formData.financial_goal}"
        `;

        setMessages([]);
        setIsLoading(true);

        const responseStream = await newChat.sendMessageStream({ message: initialPrompt });

        let currentText = '';
        setMessages([{ role: 'model', text: '...' }]);

        for await (const chunk of responseStream) {
          currentText += chunk.text;
          setMessages([{ role: 'model', text: currentText }]);
        }

      } catch (error) {
        console.error("Chat initialization failed:", error);
        setMessages([{ role: 'model', text: 'Sorry, I encountered an error while generating your plan. Please try again.' }]);
      } finally {
        setIsLoading(false);
      }
    };

    initChat();
  }, [formData]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || !chat || isLoading) return;

    const userMessage: Message = { role: 'user', text: userInput };
    setMessages(prev => [...prev, userMessage]);
    setUserInput('');
    setIsLoading(true);

    try {
      const responseStream = await chat.sendMessageStream({ message: userInput });

      let currentText = '';
      setMessages(prev => [...prev, { role: 'model', text: '...' }]);

      for await (const chunk of responseStream) {
        currentText += chunk.text;
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = { role: 'model', text: currentText };
          return newMessages;
        });
      }

    } catch (error) {
      console.error("Error sending message:", error);
      setMessages(prev => [...prev, { role: 'model', text: 'My apologies, I ran into a problem. Could you please rephrase that?' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-brand-blue p-4 sm:p-6 rounded-xl shadow-lg border border-slate-700 flex flex-col h-[calc(100vh-12rem)]">
      <div className="flex-grow overflow-y-auto pr-4 -mr-4 space-y-4">
        {messages.map((msg, index) => (
          <ChatMessage key={index} message={msg} />
        ))}
        {isLoading && messages.length > 0 && messages[messages.length - 1].role === 'user' && (
          <ChatMessage message={{ role: 'model', text: '...' }} />
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="mt-6 pt-4 border-t border-slate-700/50">
        <form onSubmit={handleSendMessage} className="flex items-center gap-3">
          <input
            type="text"
            value={userInput}
            onChange={(e) => setUserInput(e.target.value)}
            placeholder="Ask a follow-up question..."
            className="flex-grow bg-brand-blue-light border border-slate-600 rounded-md py-2 px-3 text-white focus:ring-brand-teal-light focus:border-brand-teal-light transition"
            disabled={isLoading}
          />
          <button type="submit" disabled={isLoading || !userInput.trim()} className="bg-brand-teal text-white font-bold py-2 px-5 rounded-lg shadow-md hover:bg-brand-teal-light hover:text-brand-blue transition-all duration-300 disabled:bg-slate-500 disabled:cursor-not-allowed">
            Send
          </button>
        </form>
      </div>
      <div className="text-center mt-4">
        <button onClick={onBack} className="text-sm text-slate-400 hover:text-white transition-colors">
          &larr; Back to form
        </button>
      </div>
      <SendTranscriptOnUnmount messages={messages} formData={formData} /> {/* Integrate the component here */}
    </div>
  );
};