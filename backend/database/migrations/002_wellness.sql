-- Wellness Questionnaire and Scores Schema
-- Version: 002
-- Description: Add tables for financial wellness assessment

-- Wellness questionnaire responses (New format matching Streamlit questions)
CREATE TABLE IF NOT EXISTS wellness_questionnaire (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) REFERENCES users(clerk_user_id) ON DELETE CASCADE,
    
    -- Store all questionnaire responses as JSON for flexibility
    questionnaire_responses JSONB,
    age INTEGER,  -- Age stored separately for easy access
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- One questionnaire per user
    UNIQUE(clerk_user_id)
);

-- Calculated wellness scores (New format matching Streamlit scoring)
CREATE TABLE IF NOT EXISTS wellness_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    clerk_user_id VARCHAR(255) REFERENCES users(clerk_user_id) ON DELETE CASCADE,
    questionnaire_id UUID REFERENCES wellness_questionnaire(id) ON DELETE CASCADE,
    
    -- Overall and pillar scores (0-100 scale)
    overall_score DECIMAL(5,2),  -- Average of all pillar scores
    take_control_score DECIMAL(5,2),  -- Take Control of Finances pillar
    prepare_unexpected_score DECIMAL(5,2),  -- Prepare for the Unexpected pillar
    goals_progress_score DECIMAL(5,2),  -- Make Progress Toward Goals pillar
    long_term_security_score DECIMAL(5,2),  -- Long-Term Security pillar
    
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

