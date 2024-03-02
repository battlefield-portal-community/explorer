create table if not exists experience_json (
    id BIGSERIAL primary key,

    playground_name varchar(255) not null,
    playground_description varchar(255) not null,
    created_at timestamptz not null,
    updated_at timestamptz not null,

    original_playground_json jsonb not null,
    validated_playground_json jsonb not null default '{}'::jsonb,
    tags jsonb not null default '[]'::jsonb,
    blockly jsonb not null default '{}'::jsonb,
    progression_mode jsonb not null default '{}'::jsonb
);
