import { useState } from 'react';
import { useRouter } from 'next/router';
import { useUser, useAuth } from '@clerk/nextjs';
import Layout from '../components/Layout';
import { API_URL } from '../lib/config';
import { showToast } from '../components/Toast';
import Head from 'next/head';

interface QuestionnaireData {
  // Take Control of Finances
  monthlyIncome: number;
  monthlyExpenses: number;
  savingsRate: number;
  hasBudget: boolean;
  tracksSpending: boolean;

  // Prepare for the Unexpected
  emergencyFundMonths: number;
  hasHealthInsurance: boolean;
  hasLifeInsurance: boolean;
  hasDisabilityInsurance: boolean;

  // Make Progress Toward Goals
  hasFinancialGoals: boolean;
  goalTypes: string[];
  goalTimeline: string;
  progressOnGoals: number;

  // Long-Term Security
  retirementAccountBalance: number;
  retirementContributionRate: number;
  hasRetirementPlan: boolean;
  yearsUntilRetirement: number;
}

export default function WellnessQuestionnaire() {
  const { user, isLoaded: userLoaded } = useUser();
  const { getToken } = useAuth();
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [data, setData] = useState<QuestionnaireData>({
    monthlyIncome: 0,
    monthlyExpenses: 0,
    savingsRate: 0,
    hasBudget: false,
    tracksSpending: false,
    emergencyFundMonths: 0,
    hasHealthInsurance: false,
    hasLifeInsurance: false,
    hasDisabilityInsurance: false,
    hasFinancialGoals: false,
    goalTypes: [],
    goalTimeline: '',
    progressOnGoals: 0,
    retirementAccountBalance: 0,
    retirementContributionRate: 0,
    hasRetirementPlan: false,
    yearsUntilRetirement: 0,
  });

  const totalSteps = 4;

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

    setSubmitting(true);

    try {
      const token = await getToken();
      if (!token) {
        showToast('error', 'Not authenticated');
        return;
      }

      // Calculate savings rate if not provided
      const calculatedSavingsRate = data.savingsRate || 
        (data.monthlyIncome > 0 
          ? ((data.monthlyIncome - data.monthlyExpenses) / data.monthlyIncome) * 100 
          : 0);

      const response = await fetch(`${API_URL}/api/wellness/questionnaire`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...data,
          savingsRate: calculatedSavingsRate,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to submit questionnaire');
      }

      showToast('success', 'Questionnaire submitted successfully!');
      
      // Redirect to wellness score page
      router.push('/wellness-score');
    } catch (error) {
      console.error('Error submitting questionnaire:', error);
      showToast('error', 'Failed to submit questionnaire. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const updateData = (field: keyof QuestionnaireData, value: any) => {
    setData(prev => ({ ...prev, [field]: value }));
  };

  const toggleGoalType = (goalType: string) => {
    setData(prev => ({
      ...prev,
      goalTypes: prev.goalTypes.includes(goalType)
        ? prev.goalTypes.filter(g => g !== goalType)
        : [...prev.goalTypes, goalType],
    }));
  };

  if (!userLoaded) {
    return <Layout><div className="p-8">Loading...</div></Layout>;
  }

  if (!user) {
    router.push('/');
    return null;
  }

  return (
    <>
      <Head>
        <title>Financial Wellness Questionnaire - Samy AI Financial Advisor</title>
      </Head>
      <Layout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="mb-6">
              <h1 className="text-3xl font-bold text-dark mb-2">Financial Wellness Assessment</h1>
              <p className="text-gray-600">
                Help us understand your financial situation so we can provide personalized insights.
              </p>
              <div className="mt-4">
                <div className="flex justify-between text-sm text-gray-500 mb-2">
                  <span>Step {currentStep} of {totalSteps}</span>
                  <span>{Math.round((currentStep / totalSteps) * 100)}% Complete</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(currentStep / totalSteps) * 100}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Step 1: Take Control of Finances */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <h2 className="text-2xl font-semibold text-dark">Take Control of Finances</h2>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly Income ($)
                  </label>
                  <input
                    type="number"
                    value={data.monthlyIncome || ''}
                    onChange={(e) => updateData('monthlyIncome', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Monthly Expenses ($)
                  </label>
                  <input
                    type="number"
                    value={data.monthlyExpenses || ''}
                    onChange={(e) => updateData('monthlyExpenses', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Savings Rate (%)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={data.savingsRate || ''}
                    onChange={(e) => updateData('savingsRate', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    {data.monthlyIncome > 0 && data.monthlyExpenses > 0 && (
                      <>Calculated: {((data.monthlyIncome - data.monthlyExpenses) / data.monthlyIncome * 100).toFixed(1)}%</>
                    )}
                  </p>
                </div>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={data.hasBudget}
                      onChange={(e) => updateData('hasBudget', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">I have a monthly budget</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={data.tracksSpending}
                      onChange={(e) => updateData('tracksSpending', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">I track my spending regularly</span>
                  </label>
                </div>
              </div>
            )}

            {/* Step 2: Prepare for the Unexpected */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <h2 className="text-2xl font-semibold text-dark">Prepare for the Unexpected</h2>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Emergency Fund (months of expenses)
                  </label>
                  <input
                    type="number"
                    min="0"
                    value={data.emergencyFundMonths || ''}
                    onChange={(e) => updateData('emergencyFundMonths', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <p className="text-xs text-gray-500 mt-1">Recommended: 3-6 months</p>
                </div>
                <div className="space-y-3">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={data.hasHealthInsurance}
                      onChange={(e) => updateData('hasHealthInsurance', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">I have health insurance</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={data.hasLifeInsurance}
                      onChange={(e) => updateData('hasLifeInsurance', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">I have life insurance</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={data.hasDisabilityInsurance}
                      onChange={(e) => updateData('hasDisabilityInsurance', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">I have disability insurance</span>
                  </label>
                </div>
              </div>
            )}

            {/* Step 3: Make Progress Toward Goals */}
            {currentStep === 3 && (
              <div className="space-y-6">
                <h2 className="text-2xl font-semibold text-dark">Make Progress Toward Goals</h2>
                <div>
                  <label className="flex items-center mb-4">
                    <input
                      type="checkbox"
                      checked={data.hasFinancialGoals}
                      onChange={(e) => updateData('hasFinancialGoals', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm font-medium text-gray-700">I have specific financial goals</span>
                  </label>
                </div>
                {data.hasFinancialGoals && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        What are your financial goals? (Select all that apply)
                      </label>
                      <div className="space-y-2">
                        {['Home Purchase', 'Education', 'Travel', 'Debt Payoff', 'Business', 'Other'].map((goal) => (
                          <label key={goal} className="flex items-center">
                            <input
                              type="checkbox"
                              checked={data.goalTypes.includes(goal)}
                              onChange={() => toggleGoalType(goal)}
                              className="mr-2"
                            />
                            <span className="text-sm text-gray-700">{goal}</span>
                          </label>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Timeline for achieving goals
                      </label>
                      <select
                        value={data.goalTimeline}
                        onChange={(e) => updateData('goalTimeline', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      >
                        <option value="">Select timeline</option>
                        <option value="short">Less than 1 year</option>
                        <option value="medium">1-5 years</option>
                        <option value="long">5-10 years</option>
                        <option value="very_long">More than 10 years</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Progress on goals (%)
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={data.progressOnGoals || ''}
                        onChange={(e) => updateData('progressOnGoals', parseFloat(e.target.value) || 0)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                      />
                    </div>
                  </>
                )}
              </div>
            )}

            {/* Step 4: Long-Term Security */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <h2 className="text-2xl font-semibold text-dark">Long-Term Security</h2>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Retirement Account Balance ($)
                  </label>
                  <input
                    type="number"
                    value={data.retirementAccountBalance || ''}
                    onChange={(e) => updateData('retirementAccountBalance', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Retirement Contribution Rate (% of income)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="100"
                    value={data.retirementContributionRate || ''}
                    onChange={(e) => updateData('retirementContributionRate', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <p className="text-xs text-gray-500 mt-1">Recommended: 10-15%</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Years Until Retirement
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="50"
                    value={data.yearsUntilRetirement || ''}
                    onChange={(e) => updateData('yearsUntilRetirement', parseFloat(e.target.value) || 0)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={data.hasRetirementPlan}
                      onChange={(e) => updateData('hasRetirementPlan', e.target.checked)}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">I have a retirement plan</span>
                  </label>
                </div>
              </div>
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
                  className="px-6 py-2 bg-primary text-white rounded-lg font-medium hover:bg-blue-600"
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

