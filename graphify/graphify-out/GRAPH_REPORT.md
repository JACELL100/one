# Graph Report - graphify  (2026-07-10)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 327 nodes · 454 edges · 29 communities (18 shown, 11 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 8 edges (avg confidence: 0.76)
- Token cost: 72,683 input · 486 output

## Graph Freshness
- Built from commit: `98db12d7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Foot Scan & Recommend API
- Studio & History Pages
- Foot Measurement Pipeline
- App Config & Auth Deps
- TypeScript Compiler Config
- Product Catalog & Sizing
- Frontend Dependencies
- Dev & Build Dependencies
- Auth & Layout Components
- API Contract Tests
- Recommender Ranking Tests
- Scan History Auth Tests
- Initial DB Schema
- RLS & Storage Migration
- Gait Descriptor Derivation
- Seed SQL Generator
- Home Landing Page
- Segmented Control Component
- ESLint Config
- Backend Package Init
- Next.js Config
- Next Env Types
- PostCSS Config
- Tailwind Config

## God Nodes (most connected - your core abstractions)
1. `compilerOptions` - 16 edges
2. `get_settings()` - 11 edges
3. `compute_scale()` - 10 edges
4. `useAuth()` - 9 edges
5. `measure_foot()` - 8 edges
6. `analyze_foot_image()` - 7 edges
7. `scan_foot()` - 6 edges
8. `DbError` - 6 edges
9. `jsonOrThrow()` - 6 edges
10. `Product` - 5 edges

## Surprising Connections (you probably didn't know these)
- `test_scale_bad_ratio_low_confidence()` --calls--> `compute_scale()`  [INFERRED]
  backend/tests/test_geometry.py → backend/app/services/geometry.py
- `test_scale_perfect_a4_ratio_high_confidence()` --calls--> `compute_scale()`  [INFERRED]
  backend/tests/test_geometry.py → backend/app/services/geometry.py
- `test_scale_rejects_nonpositive()` --calls--> `compute_scale()`  [INFERRED]
  backend/tests/test_geometry.py → backend/app/services/geometry.py
- `scan_foot()` --calls--> `get_settings()`  [EXTRACTED]
  backend/app/routers/scan.py → backend/app/config.py
- `is_configured()` --calls--> `get_settings()`  [EXTRACTED]
  backend/app/services/db.py → backend/app/config.py

## Import Cycles
- None detected.

## Communities (29 total, 11 thin omitted)

### Community 0 - "Foot Scan & Recommend API"
Cohesion: 0.10
Nodes (37): BaseModel, Recommendation endpoint: hybrid ranker over fit + performance profile., recommend(), Scan endpoints: foot measurement (image or manual) and gait., Measure a foot from a photo taken on an A4 sheet., Manual fallback: build a measurement from entered centimetres., Derive a gait support profile from coarse biomechanical signals.      (Optional, scan_foot() (+29 more)

### Community 1 - "Studio & History Pages"
Cohesion: 0.10
Nodes (28): HistoryPage(), DEFAULT_GOALS, Phase, STEPS, StudioPage(), FitBadge(), MAP, FitCard() (+20 more)

### Community 2 - "Foot Measurement Pipeline"
Cohesion: 0.11
Nodes (26): analyze_foot_image(), _detect_sheet(), manual_measurement(), _order_quad(), Exception, OpenCV-backed foot-scan pipeline with graceful fallbacks.  Pipeline:   1. Decode, Run the full pipeline. Returns a dict matching ``Measurement``.      Raises ``Sc, Build a measurement from user-entered centimetres (always confident). (+18 more)

### Community 3 - "App Config & Auth Deps"
Cohesion: 0.11
Nodes (24): Any, BaseSettings, get_settings(), Application settings loaded from environment variables.  All values have safe de, Settings, _decode(), get_optional_user_id(), Auth dependency: verifies Supabase-issued JWTs without any extra SDK.  Supabas (+16 more)

### Community 4 - "TypeScript Compiler Config"
Cohesion: 0.07
Nodes (28): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+20 more)

### Community 5 - "Product Catalog & Sizing"
Cohesion: 0.11
Nodes (22): _chart(), get_product(), Product, Curated mock one8 catalog with per-model size charts and attributes.  This is th, Generate a UK size chart in ~8.5mm steps (half-size ~= 4.2mm)., SizeRow, list_catalog(), Catalog endpoint — serves the curated one8 demo models. (+14 more)

### Community 6 - "Frontend Dependencies"
Cohesion: 0.09
Nodes (21): dependencies, framer-motion, html-to-image, next, react, react-dom, @supabase/supabase-js, name (+13 more)

### Community 7 - "Dev & Build Dependencies"
Cohesion: 0.11
Nodes (19): autoprefixer, devDependencies, autoprefixer, eslint, eslint-config-next, postcss, tailwindcss, @types/node (+11 more)

### Community 8 - "Auth & Layout Components"
Cohesion: 0.22
Nodes (9): metadata, LoginPage(), SiteHeader(), AuthContext, AuthProvider(), AuthState, useAuth(), getSupabaseClient() (+1 more)

### Community 13 - "Initial DB Schema"
Cohesion: 0.53
Nodes (5): products, profiles, recommendations, scans, size_charts

### Community 14 - "RLS & Storage Migration"
Cohesion: 0.33
Nodes (5): products, profiles, recommendations, scans, size_charts

### Community 15 - "Gait Descriptor Derivation"
Cohesion: 0.50
Nodes (3): derive_gait(), Gait/cadence descriptor derivation.  In production this consumes pose keypoints, Map coarse biomechanical signals to a support profile.      - High pronation ->

### Community 16 - "Seed SQL Generator"
Cohesion: 0.67
Nodes (3): main(), q(), Generate supabase/seed.sql from the canonical catalog.  Run: python scripts/gene

## Knowledge Gaps
- **67 isolated node(s):** `next/core-web-vitals`, `nextConfig`, `name`, `version`, `private` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `App Config & Auth Deps` to `Foot Scan & Recommend API`?**
  _High betweenness centrality (0.015) - this node is a cross-community bridge._
- **Why does `devDependencies` connect `Dev & Build Dependencies` to `Frontend Dependencies`?**
  _High betweenness centrality (0.010) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `compute_scale()` (e.g. with `test_measure_foot_implausible_penalised()` and `test_measure_foot_realistic()`) actually correct?**
  _`compute_scale()` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `one8 FitLab — FastAPI backend package.`, `Application settings loaded from environment variables.  All values have safe de`, `Curated mock one8 catalog with per-model size charts and attributes.  This is th` to the rest of the system?**
  _113 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Foot Scan & Recommend API` be split into smaller, more focused modules?**
  _Cohesion score 0.09639953542392567 - nodes in this community are weakly interconnected._
- **Should `Studio & History Pages` be split into smaller, more focused modules?**
  _Cohesion score 0.10121457489878542 - nodes in this community are weakly interconnected._
- **Should `Foot Measurement Pipeline` be split into smaller, more focused modules?**
  _Cohesion score 0.1053763440860215 - nodes in this community are weakly interconnected._