-- 古建文旅规划助手 数据库初始化

-- 启用PostGIS扩展
CREATE EXTENSION IF NOT EXISTS postgis;

-- 古建遗产信息表
CREATE TABLE IF NOT EXISTS heritage (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    alias VARCHAR(200),
    dynasty VARCHAR(50),
    year_start INTEGER,
    year_end INTEGER,
    building_type VARCHAR(20) NOT NULL,
    style VARCHAR(100),
    protection_level VARCHAR(30) NOT NULL,
    listed_date TIMESTAMP,
    listing_batch VARCHAR(20),
    province VARCHAR(50) NOT NULL,
    city VARCHAR(50) NOT NULL,
    district VARCHAR(50),
    address VARCHAR(300),
    geom GEOMETRY(POINT, 4326),
    description TEXT,
    current_status VARCHAR(200),
    area_size FLOAT,
    is_open BOOLEAN,
    ticket_price FLOAT,
    annual_visitors INTEGER,
    nearby_poi_count INTEGER,
    nearby_hotel_count INTEGER,
    extra_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 规划方案表
CREATE TABLE IF NOT EXISTS plan (
    id SERIAL PRIMARY KEY,
    heritage_id INTEGER NOT NULL REFERENCES heritage(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    protection_measures JSONB,
    tourism_routes JSONB,
    business_layout JSONB,
    economic_estimation JSONB,
    constraints_check JSONB,
    llm_model VARCHAR(50),
    llm_tokens INTEGER,
    generation_time FLOAT,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    quality_score FLOAT,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 对话会话表
CREATE TABLE IF NOT EXISTS chat_session (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL REFERENCES plan(id) ON DELETE CASCADE,
    session_id VARCHAR(36) NOT NULL UNIQUE,
    messages JSONB,
    context JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 法规条例表
CREATE TABLE IF NOT EXISTS regulation (
    id SERIAL PRIMARY KEY,
    title VARCHAR(300) NOT NULL,
    source VARCHAR(100),
    level VARCHAR(20),
    publish_date TIMESTAMP,
    content TEXT NOT NULL,
    summary TEXT,
    keywords JSONB,
    protection_levels JSONB,
    is_constraint BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_heritage_province ON heritage(province);
CREATE INDEX IF NOT EXISTS idx_heritage_city ON heritage(city);
CREATE INDEX IF NOT EXISTS idx_heritage_protection ON heritage(protection_level);
CREATE INDEX IF NOT EXISTS idx_heritage_type ON heritage(building_type);
CREATE INDEX IF NOT EXISTS idx_heritage_geom ON heritage USING GIST(geom);
CREATE INDEX IF NOT EXISTS idx_plan_heritage ON plan(heritage_id);
CREATE INDEX IF NOT EXISTS idx_plan_active ON plan(is_active);
CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_session(session_id);
