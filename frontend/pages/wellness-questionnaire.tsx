import { useState } from 'react';
import { useRouter } from 'next/router';
import { useUser, useAuth } from '@clerk/nextjs';
import Layout from '../components/Layout';
import { API_URL } from '../lib/config';
import { showToast } from '../components/Toast';
import Head from 'next/head';

// New questionnaire responses matching Streamlit format
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

export default function WellnessQuestionnaire() {
  const { user, isLoaded: userLoaded } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [data, setData] = useState<QuestionnaireResponses>({
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

  const totalSteps = 11;

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSubmit = async () => {
    if (!userLoaded || !user) {
      showToast('error', 'Please sign in to continue');
      return;
    }

    // Validate all questions answered
    if (!data.age || !data.employment_status || !data.retirement_plan || 
        data.financial_goals.length === 0 || !data.income_spending || 
        !data.emergency_savings || !data.savings_cover || data.debts.length === 0 ||
        data.accounts.length === 0 || !data.financial_confidence || !data.advisor) {
      showToast('error', 'Please answer all questions before submitting');
      return;
    }

    setSubmitting(true);

    try {
      const token = await getToken();
      if (!token) {
        showToast('error', 'Not authenticated');
        return;
      }

      const response = await fetch(`${API_URL}/api/wellness/questionnaire`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        // Try to get error message from response
        let errorMessage = 'Failed to submit questionnaire';
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch (e) {
          // If response is not JSON, use status text
          errorMessage = response.statusText || errorMessage;
        }
        console.error('API Error:', response.status, errorMessage);
        throw new Error(errorMessage);
      }

      const result = await response.json();
      showToast('success', 'Questionnaire submitted successfully!');
      
      // Redirect to wellness score page
      router.push('/wellness-score');
    } catch (error) {
      console.error('Error submitting questionnaire:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to submit questionnaire. Please try again.';
      showToast('error', errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  if (!userLoaded) {
    return <Layout><div className="p-8">Loading...</div></Layout>;
  }

  if (!user) {
    router.push('/');
    return null;
  }

  const renderQuestion = (questionText: string, children: React.ReactNode) => {
    return (
      <div className="mb-8">
        <div className="flex items-start gap-3 mb-4">
          <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center" style={{ backgroundColor: '#F8F8F8' }}>
            <span className="text-sm font-semibold">💬</span>
          </div>
          <div className="flex-1">
            <div className="rounded-lg px-4 py-3 inline-block" style={{ backgroundColor: '#F8F8F8' }}>
              <p className="text-lg font-semibold" style={{ color: '#062147' }}>{questionText}</p>
            </div>
          </div>
        </div>
        <div className="ml-11">
          {children}
        </div>
      </div>
    );
  };

  const renderUserResponse = (response: string) => {
    return (
      <div className="flex justify-end mb-6">
        <div className="rounded-lg px-4 py-3 max-w-[70%]" style={{ backgroundColor: '#E8F5E9' }}>
          <p className="text-base font-medium" style={{ color: '#062147' }}>{response}</p>
        </div>
      </div>
    );
  };

  return (
    <>
      <Head>
        <title>Financial Wellness Assessment - Samy AI Financial Advisor</title>
      </Head>
      <Layout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Banner - MoneyMind style */}
          <div className="border-l-4 border-yellow-400 bg-gray-50 p-4 mb-8 rounded-r-lg" style={{ borderLeftColor: '#FFD700', backgroundColor: '#F9F9F9' }}>
            <h4 className="text-lg font-semibold mb-2" style={{ color: '#062147' }}>We&apos;ll build a plan just for you</h4>
            <p className="mb-4" style={{ color: '#4B5563' }}>
              Get personalized investment planning and account management from our team of professionals. 
              We&apos;ll select your funds, invest your money, and take the guesswork out of your financial planning.
            </p>
            <button className="text-white px-5 py-2 rounded-lg font-medium hover:opacity-90 transition-opacity" style={{ backgroundColor: '#000000' }}>
              I want a plan for my money
            </button>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="mb-6">
              <h1 className="text-3xl font-bold mb-2" style={{ color: '#062147' }}>Feeling confident about your finances?</h1>
              <p className="mb-4" style={{ color: '#4B5563' }}>
                Check if your saving and spending strategies are right for you by taking our Financial Wellness Assessment. 
                Your answers will help us determine which personalized tools and resources are the best fit for you.
              </p>
              <p className="text-sm" style={{ color: '#6B7280' }}>⏱ Time to complete: 3 minutes</p>
            </div>

            {/* Progress bar */}
            <div className="mb-8">
              <div className="flex justify-between text-sm text-gray-500 mb-2">
                <span>Question {currentStep} of {totalSteps}</span>
                <span>{Math.round((currentStep / totalSteps) * 100)}% Complete</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(currentStep / totalSteps) * 100}%` }}
                />
              </div>
            </div>

            {/* Question 1: Age */}
            {currentStep === 1 && renderQuestion(
              "1: How old are you?",
              <>
                <input
                  type="text"
                  value={data.age}
                  onChange={(e) => setData({ ...data, age: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="Enter your age"
                />
                {data.age && renderUserResponse(data.age)}
              </>
            )}

            {/* Question 2: Employment Status */}
            {currentStep === 2 && renderQuestion(
              "1.a What is your employment status?",
              <>
                <select
                  value={data.employment_status}
                  onChange={(e) => setData({ ...data, employment_status: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  <option value="">Select your employment status...</option>
                  <option value="Employed">Employed</option>
                  <option value="Self-Employed">Self-Employed</option>
                  <option value="Not Currently Employed">Not Currently Employed</option>
                  <option value="Student">Student</option>
                  <option value="Retired">Retired</option>
                </select>
                {data.employment_status && data.employment_status !== '' && renderUserResponse(data.employment_status)}
              </>
            )}

            {/* Question 3: Retirement Plan */}
            {currentStep === 3 && renderQuestion(
              "1.b When do you plan to retire?",
              <>
                <div className="space-y-2">
                  {["in the next 5 years", "more than 5 years from now"].map((option) => (
                    <label key={option} className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="radio"
                        name="retirement_plan"
                        value={option}
                        checked={data.retirement_plan === option}
                        onChange={(e) => setData({ ...data, retirement_plan: e.target.value })}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>
                {data.retirement_plan && renderUserResponse(data.retirement_plan)}
              </>
            )}

            {/* Question 4: Financial Goals */}
            {currentStep === 4 && renderQuestion(
              "2. Which of these are important to you right now?",
              <>
                <div className="space-y-2">
                  {[
                    "Saving for retirement",
                    "Saving for education",
                    "Saving for health care",
                    "Saving for a big purchase, like a house or car",
                    "Preparing for emergencies",
                    "Reducing credit card debt",
                    "Paying off Student loans",
                    "Catching up after a late payment",
                    "Paying my bills"
                  ].map((goal) => (
                    <label key={goal} className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="checkbox"
                        checked={data.financial_goals.includes(goal)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setData({ ...data, financial_goals: [...data.financial_goals, goal] });
                          } else {
                            setData({ ...data, financial_goals: data.financial_goals.filter(g => g !== goal) });
                          }
                        }}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{goal}</span>
                    </label>
                  ))}
                </div>
                {data.financial_goals.length > 0 && renderUserResponse(data.financial_goals.join(', '))}
              </>
            )}

            {/* Question 5: Income Spending */}
            {currentStep === 5 && renderQuestion(
              "3. How would you describe a typical month?",
              <>
                <div className="space-y-2">
                  {[
                    "I usually spend more than I earn",
                    "I usually spend as much as I earn",
                    "I usually spend less than I earn"
                  ].map((option) => (
                    <label key={option} className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="radio"
                        name="income_spending"
                        value={option}
                        checked={data.income_spending === option}
                        onChange={(e) => setData({ ...data, income_spending: e.target.value })}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>
                {data.income_spending && renderUserResponse(data.income_spending)}
              </>
            )}

            {/* Question 6: Emergency Savings */}
            {currentStep === 6 && renderQuestion(
              "4. If an emergency happened today that cost $2,000, are you confident you can pay for it?",
              <>
                <div className="space-y-2">
                  {["Not at all", "Confident", "Entirely"].map((option) => (
                    <label key={option} className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="radio"
                        name="emergency_savings"
                        value={option}
                        checked={data.emergency_savings === option}
                        onChange={(e) => setData({ ...data, emergency_savings: e.target.value })}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>
                {data.emergency_savings && renderUserResponse(data.emergency_savings)}
              </>
            )}

            {/* Question 7: Savings Cover */}
            {currentStep === 7 && renderQuestion(
              "5. How many months of expenses can your savings cover?",
              <>
                <div className="space-y-2">
                  {[
                    "None",
                    "Less than 1 month of expenses",
                    "From 1 to 3 months of expenses",
                    "From 4 to 6 months of expenses",
                    "More than 6 months of expenses",
                    "I'm not sure"
                  ].map((option) => (
                    <label key={option} className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="radio"
                        name="savings_cover"
                        value={option}
                        checked={data.savings_cover === option}
                        onChange={(e) => setData({ ...data, savings_cover: e.target.value })}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>
                {data.savings_cover && renderUserResponse(data.savings_cover)}
              </>
            )}

            {/* Question 8: Debts */}
            {currentStep === 8 && renderQuestion(
              "6. What type of debts do you have?",
              <>
                <div className="space-y-2">
                  {[
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
                  ].map((debt) => (
                    <label key={debt} className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="checkbox"
                        checked={data.debts.includes(debt)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setData({ ...data, debts: [...data.debts, debt] });
                          } else {
                            setData({ ...data, debts: data.debts.filter(d => d !== debt) });
                          }
                        }}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{debt}</span>
                    </label>
                  ))}
                </div>
                {data.debts.length > 0 && renderUserResponse(data.debts.join(', '))}
              </>
            )}

            {/* Question 9: Accounts */}
            {currentStep === 9 && renderQuestion(
              "7. What types of accounts do you use for investing and saving?",
              <>
                <div className="space-y-2">
                  {[
                    "Individual Retirement Account (IRA)",
                    "Employer retirement plan",
                    "Health",
                    "Education",
                    "Savings Account",
                    "General Investing",
                    "None of the above"
                  ].map((account) => (
                    <label key={account} className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="checkbox"
                        checked={data.accounts.includes(account)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setData({ ...data, accounts: [...data.accounts, account] });
                          } else {
                            setData({ ...data, accounts: data.accounts.filter(a => a !== account) });
                          }
                        }}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{account}</span>
                    </label>
                  ))}
                </div>
                {data.accounts.length > 0 && renderUserResponse(data.accounts.join(', '))}
              </>
            )}

            {/* Question 10: Financial Confidence */}
            {currentStep === 10 && renderQuestion(
              "8. How much do you agree or disagree with this statement: 'I have the knowledge, ability, and time to properly manage my finances.'",
              <>
                <div className="space-y-2">
                  {["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"].map((option) => (
                    <label key={option} className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="radio"
                        name="financial_confidence"
                        value={option}
                        checked={data.financial_confidence === option}
                        onChange={(e) => setData({ ...data, financial_confidence: e.target.value })}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>
                {data.financial_confidence && renderUserResponse(data.financial_confidence)}
              </>
            )}

            {/* Question 11: Advisor */}
            {currentStep === 11 && renderQuestion(
              "9. Do you have a financial advisor?",
              <>
                <div className="space-y-2">
                  {[
                    "Yes",
                    "No, but I'd consider working with one",
                    "No, but I'd consider a digital advisor",
                    "No, and I don't want one"
                  ].map((option) => (
                    <label key={option} className="flex items-center p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50">
                      <input
                        type="radio"
                        name="advisor"
                        value={option}
                        checked={data.advisor === option}
                        onChange={(e) => setData({ ...data, advisor: e.target.value })}
                        className="mr-3"
                      />
                      <span className="text-gray-700">{option}</span>
                    </label>
                  ))}
                </div>
                {data.advisor && renderUserResponse(data.advisor)}
              </>
            )}

            {/* Navigation Buttons */}
            <div className="flex justify-between mt-8">
              <button
                onClick={handleBack}
                disabled={currentStep === 1}
                className={`px-6 py-2 rounded-lg font-medium ${
                  currentStep === 1
                    ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                Back
              </button>
              {currentStep < totalSteps ? (
                <button
                  onClick={handleNext}
                  disabled={
                    (currentStep === 1 && !data.age) ||
                    (currentStep === 2 && (!data.employment_status || data.employment_status === '')) ||
                    (currentStep === 3 && !data.retirement_plan) ||
                    (currentStep === 4 && data.financial_goals.length === 0) ||
                    (currentStep === 5 && !data.income_spending) ||
                    (currentStep === 6 && !data.emergency_savings) ||
                    (currentStep === 7 && !data.savings_cover) ||
                    (currentStep === 8 && data.debts.length === 0) ||
                    (currentStep === 9 && data.accounts.length === 0) ||
                    (currentStep === 10 && !data.financial_confidence) ||
                    (currentStep === 11 && !data.advisor)
                  }
                  className={`px-6 py-2 rounded-lg font-medium ${
                    (currentStep === 1 && !data.age) ||
                    (currentStep === 2 && (!data.employment_status || data.employment_status === '')) ||
                    (currentStep === 3 && !data.retirement_plan) ||
                    (currentStep === 4 && data.financial_goals.length === 0) ||
                    (currentStep === 5 && !data.income_spending) ||
                    (currentStep === 6 && !data.emergency_savings) ||
                    (currentStep === 7 && !data.savings_cover) ||
                    (currentStep === 8 && data.debts.length === 0) ||
                    (currentStep === 9 && data.accounts.length === 0) ||
                    (currentStep === 10 && !data.financial_confidence) ||
                    (currentStep === 11 && !data.advisor)
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-primary text-white hover:bg-blue-600'
                  }`}
                >
                  Next
                </button>
              ) : (
                <button
                  onClick={handleSubmit}
                  disabled={submitting}
                  className={`px-6 py-2 rounded-lg font-medium ${
                    submitting
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-primary text-white hover:bg-blue-600'
                  }`}
                >
                  {submitting ? 'Submitting...' : 'Submit & View Score'}
                </button>
              )}
            </div>
          </div>
        </div>
      </Layout>
    </>
  );
}
