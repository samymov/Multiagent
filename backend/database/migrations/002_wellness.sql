-- Wellness Questionnaire and Scores Schema
-- Version: 002
-- Description: Add tables for financial wellness assessment

-- Wellness questionnaire responses
CREATE TABLE IF NOT EXISTS wellness_questionnaire (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) REFERENCES users(clerk_user_id) ON DELETE CASCADE,
    
    -- Take Control of Finances
    monthly_income DECIMAL(12,2),
    monthly_expenses DECIMAL(12,2),
    savings_rate DECIMAL(5,2),  -- Percentage
    has_budget BOOLEAN DEFAULT FALSE,
    tracks_spending BOOLEAN DEFAULT FALSE,
    
    -- Prepare for the Unexpected
    emergency_fund_months DECIMAL(5,2),
    has_health_insurance BOOLEAN DEFAULT FALSE,
    has_life_insurance BOOLEAN DEFAULT FALSE,
    has_disability_insurance BOOLEAN DEFAULT FALSE,
    
    -- Make Progress Toward Goals
    has_financial_goals BOOLEAN DEFAULT FALSE,
    goal_types JSONB DEFAULT '[]',  -- Array of goal types
    goal_timeline VARCHAR(50),  -- 'short', 'medium', 'long', 'very_long'
    progress_on_goals DECIMAL(5,2),  -- Percentage
    
    -- Long-Term Security
    retirement_account_balance DECIMAL(12,2),
    retirement_contribution_rate DECIMAL(5,2),  -- Percentage
    has_retirement_plan BOOLEAN DEFAULT FALSE,
    years_until_retirement INTEGER,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- One questionnaire per user
    UNIQUE(clerk_user_id)
);

-- Calculated wellness scores
CREATE TABLE IF NOT EXISTS wellness_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) REFERENCES users(clerk_user_id) ON DELETE CASCADE,
    questionnaire_id UUID REFERENCES wellness_questionnaire(id) ON DELETE CASCADE,
    
    -- Overall score
    overall_score DECIMAL(5,2),
    
    -- Individual pillar scores
    take_control_score DECIMAL(5,2),
    prepare_unexpected_score DECIMAL(5,2),
    goals_progress_score DECIMAL(5,2),
    long_term_security_score DECIMAL(5,2),
    
    -- Pillar details (stored as JSON for flexibility)
    pillar_details JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- One score per user (latest)
    UNIQUE(clerk_user_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_wellness_questionnaire_user ON wellness_questionnaire(clerk_user_id);
CREATE INDEX IF NOT EXISTS idx_wellness_scores_user ON wellness_scores(clerk_user_id);
CREATE INDEX IF NOT EXISTS idx_wellness_scores_questionnaire ON wellness_scores(questionnaire_id);

-- Update timestamp trigger
CREATE TRIGGER update_wellness_questionnaire_updated_at
    BEFORE UPDATE ON wellness_questionnaire
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wellness_scores_updated_at
    BEFORE UPDATE ON wellness_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

