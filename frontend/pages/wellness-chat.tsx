import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/router';
import { useUser, useAuth } from '@clerk/nextjs';
import Layout from '../components/Layout';
import { API_URL } from '../lib/config';
import { showToast } from '../components/Toast';
import Head from 'next/head';
import WellnessScore from '../components/WellnessScore';
import JourneyStageIndicator from '../components/JourneyStageIndicator';
import { completeStage, getNextStage, setCurrentStage } from '../lib/journey';

interface Message {
  type: 'agent' | 'user';
  content: string;
  timestamp: Date;
}

interface QuestionnaireResponses {
  age: string;
  employment_status: string;
  retirement_plan: string;
  financial_goals: string[];
  income_spending: string;
  emergency_savings: string;
  savings_cover: string;
  debts: string[];
  accounts: string[];
  financial_confidence: string;
  advisor: string;
}

const QUESTIONS = [
  {
    id: 'age',
    question: "1: How old are you?",
    type: 'text',
    key: 'age' as keyof QuestionnaireResponses,
  },
  {
    id: 'employment_status',
    question: "1.a What is your employment status?",
    type: 'select',
    key: 'employment_status' as keyof QuestionnaireResponses,
    options: ["Employed", "Self-Employed", "Not Currently Employed", "Student", "Retired"],
  },
  {
    id: 'retirement_plan',
    question: "1.b When do you plan to retire?",
    type: 'radio',
    key: 'retirement_plan' as keyof QuestionnaireResponses,
    options: ["in the next 5 years", "more than 5 years from now"],
  },
  {
    id: 'financial_goals',
    question: "2. Which of these are important to you right now?",
    type: 'multiselect',
    key: 'financial_goals' as keyof QuestionnaireResponses,
    options: [
      "Saving for retirement",
      "Saving for education",
      "Saving for health care",
      "Saving for a big purchase, like a house or car",
      "Preparing for emergencies",
      "Reducing credit card debt",
      "Paying off Student loans",
      "Catching up after a late payment",
      "Paying my bills"
    ],
  },
  {
    id: 'income_spending',
    question: "3. How would you describe a typical month?",
    type: 'radio',
    key: 'income_spending' as keyof QuestionnaireResponses,
    options: [
      "I usually spend more than I earn",
      "I usually spend as much as I earn",
      "I usually spend less than I earn"
    ],
  },
  {
    id: 'emergency_savings',
    question: "4. If an emergency happened today that cost $2,000, are you confident you can pay for it?",
    type: 'radio',
    key: 'emergency_savings' as keyof QuestionnaireResponses,
    options: ["Not at all", "Confident", "Entirely"],
  },
  {
    id: 'savings_cover',
    question: "5. How many months of expenses can your savings cover?",
    type: 'radio',
    key: 'savings_cover' as keyof QuestionnaireResponses,
    options: [
      "None",
      "Less than 1 month of expenses",
      "From 1 to 3 months of expenses",
      "From 4 to 6 months of expenses",
      "More than 6 months of expenses",
      "I'm not sure"
    ],
  },
  {
    id: 'debts',
    question: "6. What type of debts do you have?",
    type: 'multiselect',
    key: 'debts' as keyof QuestionnaireResponses,
    options: [
      "Payday Loan",
      "Credit Card",
      "Health Care",
      "General or Personal Plan",
      "Car Loan",
      "Student Loan",
      "Home Equity Line of Credit (HELOC)",
      "Mortgage",
      "Employer retirement plan loan",
      "None",
      "Other"
    ],
  },
  {
    id: 'accounts',
    question: "7. What types of accounts do you use for investing and saving?",
    type: 'multiselect',
    key: 'accounts' as keyof QuestionnaireResponses,
    options: [
      "Individual Retirement Account (IRA)",
      "Employer retirement plan",
      "Health",
      "Education",
      "Savings Account",
      "General Investing",
      "None of the above"
    ],
  },
  {
    id: 'financial_confidence',
    question: "8. How much do you agree or disagree with this statement: 'I have the knowledge, ability, and time to properly manage my finances.'",
    type: 'radio',
    key: 'financial_confidence' as keyof QuestionnaireResponses,
    options: ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
  },
  {
    id: 'advisor',
    question: "9. Do you have a financial advisor?",
    type: 'radio',
    key: 'advisor' as keyof QuestionnaireResponses,
    options: [
      "Yes",
      "No, but I'd consider working with one",
      "No, but I'd consider a digital advisor",
      "No, and I don't want one"
    ],
  },
];

export default function WellnessChat() {
  const { user, isLoaded: userLoaded } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<QuestionnaireResponses>({
    age: '',
    employment_status: '',
    retirement_plan: '',
    financial_goals: [],
    income_spending: '',
    emergency_savings: '',
    savings_cover: '',
    debts: [],
    accounts: [],
    financial_confidence: '',
    advisor: '',
  });
  const [inputValue, setInputValue] = useState('');
  const [selectedOptions, setSelectedOptions] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [wellnessData, setWellnessData] = useState<{
    overallScore: number;
    pillars: Array<{
      name: string;
      score: number;
      rating: string;
      description: string;
      improvementTip: string;
      color: string;
      bgColor?: string;
    }>;
    lastUpdated: string;
    nbaRecommendations?: Array<{
      nba_code: string;
      agent_route: string;
      agent_name: string;
      icon: string;
      description: string;
    }>;
  } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (userLoaded && user && currentQuestionIndex === 0 && messages.length === 0) {
      // Start conversation
      const welcomeMessage: Message = {
        type: 'agent',
        content: "Hi! I'm your Financial Wellness Coach. I'll ask you a few questions to assess your financial wellness. This will take about 3 minutes. Let's get started!",
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
      
      // Add first question after a short delay
      setTimeout(() => {
        addAgentMessage(QUESTIONS[0].question);
      }, 1000);
    }
  }, [userLoaded, user, currentQuestionIndex, messages.length]);

  const addAgentMessage = (content: string) => {
    setMessages(prev => [...prev, {
      type: 'agent',
      content,
      timestamp: new Date(),
    }]);
  };

  const addUserMessage = (content: string) => {
    setMessages(prev => [...prev, {
      type: 'user',
      content,
      timestamp: new Date(),
    }]);
  };

  const handleResponse = (response: string | string[]) => {
    const currentQuestion = QUESTIONS[currentQuestionIndex];
    
    // Validate multiselect responses
    if (currentQuestion.type === 'multiselect') {
      const arrayResponse = Array.isArray(response) ? response : [response];
      if (arrayResponse.length === 0) {
        showToast('error', 'Please select at least one option');
        return;
      }
    }
    
    // Validate text responses
    if (currentQuestion.type === 'text' && (!response || (typeof response === 'string' && !response.trim()))) {
      showToast('error', 'Please provide an answer');
      return;
    }
    
    // Validate single select/radio responses
    if ((currentQuestion.type === 'select' || currentQuestion.type === 'radio') && !response) {
      showToast('error', 'Please select an option');
      return;
    }
    
    const responseText = Array.isArray(response) ? response.join(', ') : response;
    
    // Add user message
    addUserMessage(responseText);

    // Update responses
    setResponses(prev => ({
      ...prev,
      [currentQuestion.key]: response as QuestionnaireResponses[keyof QuestionnaireResponses],
    }));

    // Move to next question
    if (currentQuestionIndex < QUESTIONS.length - 1) {
      const nextIndex = currentQuestionIndex + 1;
      setTimeout(() => {
        setCurrentQuestionIndex(nextIndex);
        addAgentMessage(QUESTIONS[nextIndex].question);
      }, 500);
    } else {
      // All questions answered, submit
      setTimeout(() => {
        handleSubmit();
      }, 500);
    }
  };

  const handleSubmit = async () => {
    // Validate all required fields before submitting
    const requiredFields: (keyof QuestionnaireResponses)[] = [
      'age', 'employment_status', 'retirement_plan', 'financial_goals',
      'income_spending', 'emergency_savings', 'savings_cover', 'debts',
      'accounts', 'financial_confidence', 'advisor'
    ];
    
    const missingFields: string[] = [];
    for (const field of requiredFields) {
      const value = responses[field];
      if (field === 'financial_goals' || field === 'debts' || field === 'accounts') {
        if (!Array.isArray(value) || value.length === 0) {
          missingFields.push(field.replace('_', ' '));
        }
      } else {
        if (!value || (typeof value === 'string' && !value.trim())) {
          missingFields.push(field.replace('_', ' '));
        }
      }
    }
    
    if (missingFields.length > 0) {
      showToast('error', `Please answer all questions. Missing: ${missingFields.join(', ')}`);
      return;
    }
    
    setSubmitting(true);
    addAgentMessage("Thank you! I'm calculating your financial wellness score...");

    try {
      const token = await getToken();
      if (!token) {
        showToast('error', 'Not authenticated');
        setSubmitting(false);
        return;
      }

      const response = await fetch(`${API_URL}/api/wellness/questionnaire`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(responses),
      });

      if (!response.ok) {
        let errorMessage = 'Failed to submit questionnaire';
        let errorDetail = '';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
          errorDetail = errorData.detail || '';
        } catch (e) {
          errorMessage = response.statusText || errorMessage;
        }
        console.error('API Error Response:', {
          status: response.status,
          statusText: response.statusText,
          errorMessage,
          errorDetail,
          responses: responses
        });
        throw new Error(errorMessage);
      }

      const result = await response.json();
      
      // Show results
      setWellnessData({
        overallScore: result.overall_score,
        pillars: result.pillars,
        lastUpdated: new Date().toISOString(),
        nbaRecommendations: result.nba_recommendations || [],
      });
      setShowResults(true);
      
      // Mark assess stage as complete and move to explore
      completeStage("assess");
      const nextStage = getNextStage("assess");
      if (nextStage) {
        setCurrentStage(nextStage);
      }
      
      addAgentMessage(`Great! I've calculated your financial wellness score. Your overall score is ${result.overall_score.toFixed(1)}/100. Here's your detailed breakdown:`);
      
      showToast('success', 'Assessment completed successfully!');
    } catch (error) {
      console.error('Error submitting questionnaire:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit questionnaire. Please try again.';
      
      // Show more detailed error in console for debugging
      console.error('Full error details:', {
        error,
        errorType: error instanceof Error ? error.constructor.name : typeof error,
        errorMessage,
        responses: responses
      });
      
      // Check if it's a migration error
      if (errorMessage.includes('migration') || errorMessage.includes('Database migration') || errorMessage.includes('not available')) {
        showToast('error', 'Database setup required. Please contact support.');
        addAgentMessage("I'm sorry, the wellness feature needs to be set up first. Please contact support or check if database migrations have been run.");
      } else {
        showToast('error', errorMessage);
        addAgentMessage(`I'm sorry, there was an error: ${errorMessage}. Please try again or contact support.`);
      }
    } finally {
      setSubmitting(false);
    }
  };

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    
    handleResponse(inputValue);
    setInputValue('');
    setSelectedOptions([]);
  };

  const handleOptionSelect = (option: string) => {
    const currentQuestion = QUESTIONS[currentQuestionIndex];
    
    if (currentQuestion.type === 'multiselect') {
      const newSelection = selectedOptions.includes(option)
        ? selectedOptions.filter(o => o !== option)
        : [...selectedOptions, option];
      setSelectedOptions(newSelection);
    } else {
      handleResponse(option);
      setSelectedOptions([]);
    }
  };

  const handleMultiselectSubmit = () => {
    if (selectedOptions.length === 0) {
      showToast('error', 'Please select at least one option before continuing');
      return;
    }
    handleResponse(selectedOptions);
    setSelectedOptions([]);
  };

  if (!userLoaded) {
    return <Layout><div className="p-8">Loading...</div></Layout>;
  }

  if (!user) {
    router.push('/');
    return null;
  }

  const currentQuestion = QUESTIONS[currentQuestionIndex];

  return (
    <>
      <Head>
        <title>Financial Wellness Assessment - Samy AI Financial Advisor</title>
      </Head>
      <Layout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Journey Stage Indicator */}
          <JourneyStageIndicator currentStage="assess" />
          
          {!showResults ? (
            <>
              {/* Chat Header */}
              <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-2xl">💬</span>
                  </div>
                  <div>
                    <h1 className="text-2xl font-bold" style={{ color: '#062147' }}>
                      Financial Wellness Assessment
                    </h1>
                    <p className="text-sm text-gray-600">Chat with your Financial Wellness Coach</p>
                  </div>
                </div>
                <div className="text-sm text-gray-500">
                  Question {currentQuestionIndex + 1} of {QUESTIONS.length}
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${((currentQuestionIndex + 1) / QUESTIONS.length) * 100}%` }}
                  />
                </div>
              </div>

              {/* Chat Messages */}
              <div className="bg-white rounded-lg shadow-lg p-6 mb-6" style={{ minHeight: '400px', maxHeight: '600px', overflowY: 'auto' }}>
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex mb-4 ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {message.type === 'agent' && (
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center mr-2">
                        <span className="text-sm">💬</span>
                      </div>
                    )}
                    <div
                      className={`rounded-lg px-4 py-3 max-w-[70%] ${
                        message.type === 'user'
                          ? 'bg-green-50'
                          : 'bg-gray-50'
                      }`}
                    >
                      <p className="text-base" style={{ color: '#062147' }}>{message.content}</p>
                    </div>
                    {message.type === 'user' && (
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center ml-2">
                        <span className="text-sm">👤</span>
                      </div>
                    )}
                  </div>
                ))}

                {/* Current Question Input */}
                {currentQuestionIndex < QUESTIONS.length && !submitting && (
                  <div className="mt-4">
                    {currentQuestion.type === 'text' && (
                      <form onSubmit={handleTextSubmit} className="flex gap-2">
                        <input
                          type="text"
                          value={inputValue}
                          onChange={(e) => setInputValue(e.target.value)}
                          placeholder="Type your answer..."
                          className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                          autoFocus
                        />
                        <button
                          type="submit"
                          className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-600"
                        >
                          Send
                        </button>
                      </form>
                    )}

                    {(currentQuestion.type === 'radio' || currentQuestion.type === 'select') && (
                      <div className="space-y-2">
                        {currentQuestion.options?.map((option) => (
                          <button
                            key={option}
                            onClick={() => handleOptionSelect(option)}
                            className="w-full text-left p-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                            style={{ color: '#062147' }}
                          >
                            {option}
                          </button>
                        ))}
                      </div>
                    )}

                    {currentQuestion.type === 'multiselect' && (
                      <div>
                        <div className="space-y-2 mb-4">
                          {currentQuestion.options?.map((option) => (
                            <button
                              key={option}
                              onClick={() => handleOptionSelect(option)}
                              className={`w-full text-left p-3 border rounded-lg transition-colors ${
                                selectedOptions.includes(option)
                                  ? 'border-primary bg-primary/10'
                                  : 'border-gray-300 hover:bg-gray-50'
                              }`}
                              style={{ color: '#062147' }}
                            >
                              {selectedOptions.includes(option) && '✓ '}
                              {option}
                            </button>
                          ))}
                        </div>
                        <button
                          onClick={handleMultiselectSubmit}
                          disabled={selectedOptions.length === 0}
                          className={`w-full px-6 py-2 rounded-lg font-medium transition-colors ${
                            selectedOptions.length === 0
                              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                              : 'bg-primary text-white hover:bg-blue-600'
                          }`}
                          title={selectedOptions.length === 0 ? 'Please select at least one option to continue' : ''}
                        >
                          {selectedOptions.length === 0 
                            ? 'Select at least one option' 
                            : `Continue (${selectedOptions.length} selected)`}
                        </button>
                      </div>
                    )}
                  </div>
                )}

                {submitting && (
                  <div className="flex items-center gap-2 text-gray-500">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                    <span>Calculating your score...</span>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>
            </>
          ) : (
            /* Results View */
            <div>
              {wellnessData && (
                <WellnessScore
                  overallScore={wellnessData.overallScore}
                  pillars={wellnessData.pillars}
                  lastUpdated={wellnessData.lastUpdated}
                  nbaRecommendations={wellnessData.nbaRecommendations}
                />
              )}
              <div className="mt-6 text-center">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-blue-600"
                >
                  Back to Dashboard
                </button>
              </div>
            </div>
          )}
        </div>
      </Layout>
    </>
  );
}

