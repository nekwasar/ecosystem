-- Create all 7 databases for the ecosystem
-- This script runs automatically on first PostgreSQL startup

-- Admin database (users, roles, settings, sessions)
CREATE DATABASE admin_db;

-- Agent database (AI agent data, tasks)
CREATE DATABASE agent_db;

-- Blog database (posts, comments, authors, tags)
CREATE DATABASE blog_db;

-- Gigs database (job listings, tracking)
CREATE DATABASE gigs_db;

-- Mail database (campaigns, subscribers, logs)
CREATE DATABASE mail_db;

-- Store database (products, orders, customers)
CREATE DATABASE store_db;

-- Grant privileges to main user
\c admin_db;
GRANT ALL PRIVILEGES ON DATABASE admin_db TO ${POSTGRES_USER};

\c agent_db;
GRANT ALL PRIVILEGES ON DATABASE agent_db TO ${POSTGRES_USER};

\c blog_db;
GRANT ALL PRIVILEGES ON DATABASE blog_db TO ${POSTGRES_USER};

\c gigs_db;
GRANT ALL PRIVILEGES ON DATABASE gigs_db TO ${POSTGRES_USER};

\c mail_db;
GRANT ALL PRIVILEGES ON DATABASE mail_db TO ${POSTGRES_USER};

\c store_db;
GRANT ALL PRIVILEGES ON DATABASE store_db TO ${POSTGRES_USER};
