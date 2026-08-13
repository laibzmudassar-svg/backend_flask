-- Day 16: Advanced Database Indexing & Query Optimization
-- Migration: add indexes for posts table performance

CREATE INDEX IF NOT EXISTS idx_posts_active ON posts(user_id) WHERE user_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_posts_user_title ON posts(user_id, title);
CREATE INDEX IF NOT EXISTS idx_posts_title ON posts(title);