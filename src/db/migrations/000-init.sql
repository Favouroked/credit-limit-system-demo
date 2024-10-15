CREATE TABLE IF NOT EXISTS users
(
    id              text primary key,
    name            text        not null,
    email           text unique not null,
    credit_limit    integer,
    credit_limit_id text,
    device_token    text,
    created_at      timestamptz not null,
    updated_at      timestamptz
);

CREATE TABLE IF NOT EXISTS transactions
(
    id               text primary key,
    user_id          text references users (id) on delete cascade,
    amount           integer     not null,
    transaction_type text        not null,
    created_at       timestamptz not null,
    updated_at       timestamptz
);

CREATE TABLE IF NOT EXISTS emotions
(
    id           text primary key,
    user_id      text references users (id) on delete cascade,
    emotion_type text        not null,
    intensity    integer     not null,
    created_at   timestamptz not null,
    updated_at   timestamptz
);

CREATE TABLE IF NOT EXISTS thoughts
(
    id         text primary key,
    user_id    text references users (id) on delete cascade,
    content    text        not null,
    sentiment  text        not null,
    created_at timestamptz not null,
    updated_at timestamptz
);

CREATE TABLE IF NOT EXISTS credit_limits
(
    id           text primary key,
    user_id      text references users (id) on delete cascade,
    risk_score   integer     not null,
    credit_limit integer     not null,
    increase     integer     not null,
    created_at   timestamptz not null,
    updated_at   timestamptz
);

CREATE TABLE IF NOT EXISTS notifications
(
    id                text primary key,
    user_id           text references users (id) on delete cascade,
    title             text        not null,
    content           text        not null,
    notification_type text        not null,
    created_at        timestamptz not null,
    updated_at        timestamptz
);

CREATE INDEX emotions_search_idx ON emotions(user_id, created_at);
CREATE INDEX thoughts_search_idx ON thoughts(user_id, created_at);
CREATE INDEX transactions_search_idx ON transactions(user_id, created_at);