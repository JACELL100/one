-- one8 FitLab — Row Level Security + private storage buckets

-- Products & size charts are public read (catalog is not secret).
alter table products enable row level security;
alter table size_charts enable row level security;

drop policy if exists "products_public_read" on products;
create policy "products_public_read" on products
    for select using (true);

drop policy if exists "size_charts_public_read" on size_charts;
create policy "size_charts_public_read" on size_charts
    for select using (true);

-- User-owned tables: each row is scoped to auth.uid().
alter table scans enable row level security;
alter table profiles enable row level security;
alter table recommendations enable row level security;

drop policy if exists "scans_owner" on scans;
create policy "scans_owner" on scans
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "profiles_owner" on profiles;
create policy "profiles_owner" on profiles
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "recommendations_owner" on recommendations;
create policy "recommendations_owner" on recommendations
    for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

-- Private storage buckets for foot photos and run videos.
insert into storage.buckets (id, name, public)
values ('foot-scans', 'foot-scans', false)
on conflict (id) do nothing;

insert into storage.buckets (id, name, public)
values ('gait-videos', 'gait-videos', false)
on conflict (id) do nothing;

-- Only owners may read/write their own media (path prefixed with their uid).
drop policy if exists "foot_scans_owner" on storage.objects;
create policy "foot_scans_owner" on storage.objects
    for all using (
        bucket_id = 'foot-scans' and auth.uid()::text = (storage.foldername(name))[1]
    ) with check (
        bucket_id = 'foot-scans' and auth.uid()::text = (storage.foldername(name))[1]
    );

drop policy if exists "gait_videos_owner" on storage.objects;
create policy "gait_videos_owner" on storage.objects
    for all using (
        bucket_id = 'gait-videos' and auth.uid()::text = (storage.foldername(name))[1]
    ) with check (
        bucket_id = 'gait-videos' and auth.uid()::text = (storage.foldername(name))[1]
    );
