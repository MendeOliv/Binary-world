-- Setup Database Schema for Hermes Backend (Supabase Postgres)

-- 1. Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
-- Enable pgvector (optional but prepared for semantic search embeddings)
CREATE EXTENSION IF NOT EXISTS "vector";

-- 2. Create helper function for automatically updating updated_at columns
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = timezone('utc'::text, now());
    RETURN NEW;
END;
$$ language 'plpgsql';


-- 3. Projects Table
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    status TEXT,
    current_phase_id TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();


-- 4. State Table (Snapshot of current project state, one row per project)
CREATE TABLE IF NOT EXISTS state (
    project_id UUID PRIMARY KEY REFERENCES projects(id) ON DELETE CASCADE,
    current_phase JSONB DEFAULT '{}'::jsonb,
    completed JSONB DEFAULT '[]'::jsonb,
    in_progress JSONB DEFAULT '[]'::jsonb,
    next JSONB DEFAULT '[]'::jsonb,
    open_questions JSONB DEFAULT '[]'::jsonb,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TRIGGER update_state_updated_at BEFORE UPDATE ON state
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();


-- 5. Decisions Table
CREATE TABLE IF NOT EXISTS decisions (
    id TEXT PRIMARY KEY, -- e.g., "DEC-001"
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    reason TEXT,
    source TEXT NOT NULL, -- e.g. "user" or "model_inference"
    confidence NUMERIC DEFAULT 1.0,
    status TEXT DEFAULT 'active' NOT NULL, -- e.g. "active" or "revoked"
    replaced_by TEXT REFERENCES decisions(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TRIGGER update_decisions_updated_at BEFORE UPDATE ON decisions
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();


-- 6. Requirements Table
CREATE TABLE IF NOT EXISTS requirements (
    id TEXT PRIMARY KEY, -- e.g., "REQ-001"
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'pending' NOT NULL,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- 7. Tasks Table
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY, -- e.g., "TASK-001"
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending' NOT NULL, -- "pending", "in_progress", "done"
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();


-- 8. Memory Items Table (For general RAG/semantic storage)
CREATE TABLE IF NOT EXISTS memory_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    type TEXT NOT NULL, -- "decision", "requirement", "task", "state", "knowledge", "history"
    title TEXT,
    content TEXT NOT NULL,
    source TEXT,
    confidence NUMERIC DEFAULT 1.0,
    status TEXT,
    embedding VECTOR(1536), -- Prepared for OpenAI/other 1536-dim embeddings
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE TRIGGER update_memory_items_updated_at BEFORE UPDATE ON memory_items
    FOR EACH ROW EXECUTE PROCEDURE update_updated_at_column();


-- 9. Conflicts Table
CREATE TABLE IF NOT EXISTS conflicts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    item_a_id TEXT NOT NULL,
    item_b_id TEXT NOT NULL,
    description TEXT NOT NULL,
    resolved BOOLEAN DEFAULT FALSE NOT NULL,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- 10. Request Logs Table (Observability and recovery audit)
CREATE TABLE IF NOT EXISTS request_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    retrieved_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    reason TEXT,
    model_used TEXT,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);


-- --- INDEXES ---
-- Simple foreign key performance indexes
CREATE INDEX IF NOT EXISTS idx_state_project_id ON state(project_id);
CREATE INDEX IF NOT EXISTS idx_decisions_project_id ON decisions(project_id);
CREATE INDEX IF NOT EXISTS idx_requirements_project_id ON requirements(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_memory_items_project_id ON memory_items(project_id);
CREATE INDEX IF NOT EXISTS idx_conflicts_project_id ON conflicts(project_id);
CREATE INDEX IF NOT EXISTS idx_request_logs_project_id ON request_logs(project_id);

-- GIN Full-Text Search Functional Indexes (uses English configuration)
CREATE INDEX IF NOT EXISTS decisions_content_fts_idx ON decisions USING GIN (to_tsvector('english', coalesce(content, '')));
CREATE INDEX IF NOT EXISTS requirements_content_fts_idx ON requirements USING GIN (to_tsvector('english', coalesce(content, '')));
CREATE INDEX IF NOT EXISTS tasks_description_fts_idx ON tasks USING GIN (to_tsvector('english', coalesce(description, '')));
CREATE INDEX IF NOT EXISTS memory_items_content_fts_idx ON memory_items USING GIN (to_tsvector('english', coalesce(content, '')));


-- --- ROW LEVEL SECURITY (RLS) ---
-- Enable RLS on all tables to block public direct access
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE state ENABLE ROW LEVEL SECURITY;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE requirements ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE memory_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE conflicts ENABLE ROW LEVEL SECURITY;
ALTER TABLE request_logs ENABLE ROW LEVEL SECURITY;

-- Note: Because no policies are defined, standard direct anonymous and authenticated access is denied.
-- Only database owners and operations using the Supabase "service_role" key bypass RLS policies
-- and can perform all operations, which matches the backend access requirements.
