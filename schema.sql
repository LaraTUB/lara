DROP TABLE user;

CREATE TABLE user (
  id integer PRIMARY KEY AUTOINCREMENT,
  github_name text NULL,
  github_login text NULL,
  slack_user_id text NULL,
  token text NULL,
  state text NULL
);

INSERT INTO user ('slack_user_id', 'token') VALUES ('SLACK123456', 'F6BI03dHsHs7gBGj1u48kj9kTgYhMbbFd7');