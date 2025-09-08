-- Enable fast substring search (optional but useful for find_regions)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Categories
CREATE TABLE IF NOT EXISTS categories (
  id          SERIAL PRIMARY KEY,
  name        VARCHAR(255) NOT NULL,
  region      VARCHAR(255) NOT NULL,
  type        VARCHAR(255) NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_categories_type  ON categories(type);
CREATE INDEX IF NOT EXISTS idx_categories_name  ON categories(name);

-- Files
CREATE TABLE IF NOT EXISTS files (
  id           SERIAL PRIMARY KEY,
  category_id  SERIAL NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
  name         VARCHAR(255) NOT NULL,
  binary_data  BYTEA NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_files_category_id ON files(category_id);

-- Cells (parsed cell values from uploaded Excel files)
CREATE TABLE IF NOT EXISTS cells (
  id         SERIAL PRIMARY KEY,
  file_id    SERIAL NOT NULL REFERENCES files(id) ON DELETE CASCADE,
  str_value  VARCHAR(32767),
  float_value DOUBLE PRECISION,
  CONSTRAINT cells_value_not_null CHECK (str_value IS NOT NULL OR float_value IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS idx_cells_file_id      ON cells(file_id);
CREATE INDEX IF NOT EXISTS idx_cells_float_value  ON cells(float_value);
-- For substring search on str_value
CREATE INDEX IF NOT EXISTS idx_cells_str_trgm   ON cells USING GIN (str_value gin_trgm_ops);
