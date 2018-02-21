CREATE TABLE IF NOT EXISTS user (
  id integer PRIMARY KEY AUTOINCREMENT,
  github_name text NULL,
  github_login text NULL,
  github_token text NULL,
  slack_user_id text NULL,
  token text NULL,
  state text NULL
);