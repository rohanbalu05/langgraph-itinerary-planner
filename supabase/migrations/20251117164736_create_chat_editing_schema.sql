/*
  Chat-Based Itinerary Editing Schema
  
  This migration creates tables for storing itineraries, tracking edits,
  and managing chat sessions for conversational editing.
  
  Tables:
  1. itineraries - Stores generated travel itineraries
  2. itinerary_edits - Tracks all edits with before/after snapshots
  3. chat_sessions - Manages chat conversation history
*/

-- Create itineraries table
CREATE TABLE IF NOT EXISTS itineraries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  destination text NOT NULL,
  budget numeric NOT NULL DEFAULT 0,
  interests jsonb DEFAULT '[]'::jsonb,
  dates text NOT NULL,
  content jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create itinerary_edits table
CREATE TABLE IF NOT EXISTS itinerary_edits (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  change_id text UNIQUE NOT NULL,
  itinerary_id uuid REFERENCES itineraries(id) ON DELETE CASCADE,
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  intent text NOT NULL,
  entities jsonb DEFAULT '{}'::jsonb,
  edit_command jsonb NOT NULL,
  before_snapshot jsonb NOT NULL,
  after_snapshot jsonb NOT NULL,
  confidence numeric NOT NULL DEFAULT 0,
  status text NOT NULL DEFAULT 'applied',
  error_message text,
  created_at timestamptz DEFAULT now(),
  reverted_at timestamptz
);

-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  itinerary_id uuid REFERENCES itineraries(id) ON DELETE CASCADE,
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
  messages jsonb DEFAULT '[]'::jsonb,
  created_at timestamptz DEFAULT now(),
  last_message_at timestamptz DEFAULT now()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_itineraries_user_id ON itineraries(user_id);
CREATE INDEX IF NOT EXISTS idx_itinerary_edits_itinerary_id ON itinerary_edits(itinerary_id);
CREATE INDEX IF NOT EXISTS idx_itinerary_edits_change_id ON itinerary_edits(change_id);
CREATE INDEX IF NOT EXISTS idx_itinerary_edits_user_id ON itinerary_edits(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_itinerary_id ON chat_sessions(itinerary_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);

-- Enable Row Level Security
ALTER TABLE itineraries ENABLE ROW LEVEL SECURITY;
ALTER TABLE itinerary_edits ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies for itineraries
CREATE POLICY "Users can view own itineraries"
  ON itineraries FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own itineraries"
  ON itineraries FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own itineraries"
  ON itineraries FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own itineraries"
  ON itineraries FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);

-- RLS Policies for itinerary_edits
CREATE POLICY "Users can view own edits"
  ON itinerary_edits FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own edits"
  ON itinerary_edits FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own edits"
  ON itinerary_edits FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- RLS Policies for chat_sessions
CREATE POLICY "Users can view own chat sessions"
  ON chat_sessions FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat sessions"
  ON chat_sessions FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own chat sessions"
  ON chat_sessions FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own chat sessions"
  ON chat_sessions FOR DELETE
  TO authenticated
  USING (auth.uid() = user_id);