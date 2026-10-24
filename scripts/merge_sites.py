#!/usr/bin/env python3
"""Merge latest EMD hits into accumulating sites.json (dedupe by domain)."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

BJ = timezone(timedelta(hours=8))
SHARE = Path.home() / ".local/share/webcafe-emd"
SITE_DIR = SHARE / "site"
REPO_DATA = Path(__file__).resolve().parents[1] / "data"


def today_bj() -> str:
    return datetime.now(BJ).date().isoformat()


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def primary_keyword(domain: str, keywords: list[str]) -> str:
    if not keywords:
        return ""
    stem = domain.split(".")[0].replace("-", "")
    for k in keywords:
        kk = k.replace(" ", "").replace("-", "").lower()
        if kk and kk in stem:
            return k
    return keywords[0]


def merge(existing: dict[str, dict], hits: list[dict], today: str) -> tuple[dict[str, dict], int]:
    new_count = 0
    for h in hits:
        dom = (h.get("domain") or "").lower().strip()
        if not dom:
            continue
        kw = h.get("keyword") or ""
        mt = "完全" if h.get("type") == "exact" else "模糊"
        if dom not in existing:
            existing[dom] = {
                "domain": dom,
                "url": h.get("url") or f"https://{dom}/",
                "keywords": [kw] if kw else [],
                "keyword": kw,
                "match_type": mt,
                "created_bj": h.get("created_bj"),
                "site_category": h.get("site_category") or "其他",
                "site_class": h.get("site_class") or "",
                "site_blurb": h.get("site_blurb") or "",
                "title": h.get("title") or "",
                "heat_ratio": h.get("heat_ratio"),
                "growth_pct": h.get("growth_pct"),
                "verdict": h.get("verdict"),
                "trend_now": h.get("trend_now"),
                "first_seen": today,
                "last_seen": today,
            }
            new_count += 1
            continue
        rec = existing[dom]
        if kw and kw not in rec.get("keywords", []):
            rec.setdefault("keywords", []).append(kw)
        rec["keyword"] = primary_keyword(dom, rec.get("keywords") or [])
        if mt == "完全" or not rec.get("match_type"):
            rec["match_type"] = mt
        if h.get("created_bj") and (
            not rec.get("created_bj") or h["created_bj"] < rec["created_bj"]
        ):
            rec["created_bj"] = h["created_bj"]
        if h.get("site_category"):
            rec["site_category"] = h["site_category"]
        if h.get("site_blurb"):
            rec["site_blurb"] = h["site_blurb"]
        if h.get("url"):
            rec["url"] = h["url"]
        if h.get("title"):
            rec["title"] = h["title"]
        if h.get("heat_ratio") is not None:
            rec["heat_ratio"] = h["heat_ratio"]
            rec["growth_pct"] = h.get("growth_pct")
            rec["verdict"] = h.get("verdict")
            rec["trend_now"] = h.get("trend_now")
        rec["last_seen"] = today
    return existing, new_count


def main() -> None:
    today = today_bj()
    SITE_DIR.mkdir(parents=True, exist_ok=True)
    sites_path = SITE_DIR / "sites.json"
    hits_path = SHARE / "hits_latest.json"

    existing_list = load_json(sites_path, [])
    existing = {r["domain"].lower(): r for r in existing_list if r.get("domain")}
    hits = load_json(hits_path, [])
    existing, new_count = merge(existing, hits, today)

    out = list(existing.values())
    out.sort(
        key=lambda r: (r.get("created_bj") or "0000-00-00", float(r.get("heat_ratio") or 0)),
        reverse=True,
    )
    meta = {
        "generated_at": datetime.now(BJ).isoformat(timespec="seconds"),
        "timezone": "Asia/Shanghai",
        "site_count": len(out),
        "today": today,
        "new_today": sum(1 for r in out if r.get("first_seen") == today),
        "new_merged": new_count,
        "source": "web.cafe EMD radar",
    }
    text = json.dumps(out, ensure_ascii=False)
    meta_text = json.dumps(meta, ensure_ascii=False, indent=2)
    sites_path.write_text(text, encoding="utf-8")
    (SITE_DIR / "meta.json").write_text(meta_text, encoding="utf-8")

    # sync into repo working copy when present
    if REPO_DATA.exists() or True:
        REPO_DATA.mkdir(parents=True, exist_ok=True)
        (REPO_DATA / "sites.json").write_text(text, encoding="utf-8")
        (REPO_DATA / "meta.json").write_text(meta_text, encoding="utf-8")

    print(json.dumps({"ok": True, **meta}, ensure_ascii=False))


if __name__ == "__main__":
    main()
