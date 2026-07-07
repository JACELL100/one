-- one8 FitLab — initial schema
-- Postgres (Supabase). Run in the SQL editor or via `supabase db push`.

create extension if not exists "pgcrypto";

-- Products (curated one8 catalog) --------------------------------------------
create table if not exists products (
    id            text primary key,
    name          text not null,
    tagline       text,
    price_inr     integer not null,
    image_url     text,
    sport         text not null,
    surface       text not null,
    cushioning    text not null,
    support       text not null,          -- neutral | cushion | stability
    width_class   text not null,          -- narrow | standard | wide
    fit_offset_mm real not null default 10,
    created_at    timestamptz default now()
);

-- Per-model size charts ------------------------------------------------------
create table if not exists size_charts (
    id          uuid primary key default gen_random_uuid(),
    product_id  text not null references products(id) on delete cascade,
    size_label  text not null,
    length_mm   real not null,
    unique (product_id, size_label)
);

-- Foot scans (owned by a user, or anonymous null) ----------------------------
create table if not exists scans (
    id           uuid primary key default gen_random_uuid(),
    user_id      uuid references auth.users(id) on delete cascade,
    media_path   text,                    -- private storage object path
    video_path   text,
    length_mm    real,
    width_mm     real,
    confidence   real,
    method       text,
    created_at   timestamptz default now()
);

-- Performance profiles -------------------------------------------------------
create table if not exists profiles (
    id            uuid primary key default gen_random_uuid(),
    scan_id       uuid references scans(id) on delete cascade,
    user_id       uuid references auth.users(id) on delete cascade,
    sport         text,
    surface       text,
    cushioning    text,
    use_case      text,
    gait_profile  text,
    cadence_spm   integer,
    created_at    timestamptz default now()
);

-- Persisted recommendation payloads ------------------------------------------
create table if not exists recommendations (
    id          uuid primary key default gen_random_uuid(),
    scan_id     uuid references scans(id) on delete cascade,
    user_id     uuid references auth.users(id) on delete cascade,
    payload     jsonb not null,
    created_at  timestamptz default now()
);

create index if not exists idx_scans_user on scans(user_id);
create index if not exists idx_reco_user on recommendations(user_id);
