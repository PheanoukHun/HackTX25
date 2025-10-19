import React, { useEffect } from 'react';
import type { FormData } from '../App';

interface Message {
  // Define the structure of your message object here.
  // Example:
  content: string;
  sender: 'user' | 'bot';
  timestamp: number;
  // Add other properties as needed
}

interface Props {
  messages: Message[];
  formData: FormData;
}

const SendTranscriptOnUnmount: React.FC<Props> = ({ messages, formData }) => {
  useEffect(() => {
    const sendTranscript = async () => {
      try {
        // Replace with your actual API endpoint
        const response = await fetch('http://127.0.0.1:5000/api/submit', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ messages, formData }),
        });

        if (!response.ok) {
          console.error('Failed to send transcript:', response.status);
        }
      } catch (error) {
        console.error('Error sending transcript:', error);
      }
    };

    return () => {
      sendTranscript(); // This function runs when the component unmounts
    };
  }, []); // Dependency array: Run only on mount and unmount

  return null; // This component doesn't render anything visible
};

export default SendTranscriptOnUnmount;