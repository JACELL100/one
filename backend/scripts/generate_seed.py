"""Generate supabase/seed.sql from the canonical catalog.

Run: python scripts/generate_seed.py
Keeps the DB seed in sync with backend/app/data/catalog.py (single source).
"""

from pathlib import Path

from app.data.catalog import CATALOG


def q(text: str) -> str:
    return text.replace("'", "''")


def main() -> None:
    lines = [
        "-- one8 FitLab — seed catalog (generated from backend/app/data/catalog.py)",
        "-- Regenerate with: python backend/scripts/generate_seed.py",
        "",
    ]
    for p in CATALOG:
        lines.append(
            "insert into products "
            "(id,name,tagline,price_inr,image_url,sport,surface,cushioning,support,width_class,fit_offset_mm) "
            f"values ('{p['id']}','{q(p['name'])}','{q(p['tagline'])}',{p['price_inr']},"
            f"'{p['image_url']}','{p['sport']}','{p['surface']}','{p['cushioning']}',"
            f"'{p['support']}','{p['width_class']}',{p['fit_offset_mm']}) "
            "on conflict (id) do update set name=excluded.name, price_inr=excluded.price_inr;"
        )
    lines.append("")
    for p in CATALOG:
        for r in p["size_chart"]:
            lines.append(
                "insert into size_charts (product_id,size_label,length_mm) "
                f"values ('{p['id']}','{r['size_label']}',{r['length_mm']}) "
                "on conflict (product_id,size_label) do update set length_mm=excluded.length_mm;"
            )

    out = Path(__file__).resolve().parents[2] / "supabase" / "seed.sql"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({sum(len(p['size_chart']) for p in CATALOG)} size rows)")


if __name__ == "__main__":
    main()
