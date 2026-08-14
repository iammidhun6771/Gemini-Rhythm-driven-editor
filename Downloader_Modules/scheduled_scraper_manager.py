"""
scheduled_scraper_manager.py — Max 2-Account Rotating Scheduled Scraper Manager
=================================================================================
Manages scheduled account rotation for source_accounts.json:
  - Selects max 2 accounts per scheduled batch.
  - Updates source_accounts.json target list.
  - Executes Phase 1 Ingestion + Phase 2 AI Editing + Yields rendered reels one-by-one.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, List, Optional, Any, Generator

logger = logging.getLogger("scheduled_scraper_manager")

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACCOUNTS_JSON = os.path.join(_REPO_ROOT, "Content_Scraper_Modules", "source_accounts.json")


def get_rotated_max_two_accounts(max_accounts: int = 2) -> List[str]:
    """
    Reads source_accounts.json, selects max_accounts (2) using round-robin index,
    and updates the active target list.
    """
    if not os.path.exists(ACCOUNTS_JSON):
        logger.warning(f"⚠️ {ACCOUNTS_JSON} not found. Returning default fallback accounts.")
        return ["indiancelebspot", "b.town.ind"]

    try:
        with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        paparazzi = data.get("_paparazzi", {})
        all_accounts = paparazzi.get("source_accounts", [])
        if not all_accounts:
            return ["indiancelebspot"]

        # Track rotation pointer via state file
        rotation_state_file = os.path.join(_REPO_ROOT, "data", "scraper_rotation_pointer.json")
        os.makedirs(os.path.dirname(rotation_state_file), exist_ok=True)

        pointer = 0
        if os.path.exists(rotation_state_file):
            try:
                with open(rotation_state_file, "r") as rf:
                    pointer = json.load(rf).get("pointer", 0)
            except Exception:
                pointer = 0

        selected = []
        for i in range(min(max_accounts, len(all_accounts))):
            idx = (pointer + i) % len(all_accounts)
            selected.append(all_accounts[idx])

        # Save next pointer
        new_pointer = (pointer + len(selected)) % len(all_accounts)
        with open(rotation_state_file, "w") as wf:
            json.dump({"pointer": new_pointer, "last_selected": selected, "timestamp": time.time()}, wf, indent=2)

        logger.info(f"🔄 [SCHEDULER SCRAPER] Rotated account pool (max {max_accounts}): selected={selected}")
        return selected
    except Exception as e:
        logger.error(f"❌ Error rotating source accounts: {e}")
        return ["indiancelebspot", "b.town.ind"]


def run_scheduled_scraper_batch(max_accounts: int = 2) -> List[str]:
    """
    Runs a scheduled batch with max 2 target accounts:
    1. Selects 2 target accounts.
    2. Executes Phase 1 Ingestion.
    3. Executes Phase 2 & 3 Master AI Editing.
    4. Returns list of rendered master reels.
    """
    target_accounts = get_rotated_max_two_accounts(max_accounts=max_accounts)
    logger.info(f"🚀 [SCHEDULED BATCH] Triggering Apify scraper for accounts: {target_accounts}")

    from Downloader_Modules.downloader_main import run_phase1_ingestion
    from Main_Modules.phase2_main import run_phase2_orchestration

    # Run ingestion for selected accounts
    ingest_res = run_phase1_ingestion(mode="auto", limit_per_account=3)
    if not ingest_res.get("success") or not ingest_res.get("downloaded_files"):
        logger.warning("⚠️ [SCHEDULED BATCH] Ingestion returned 0 new clips.")
        return []

    # Run AI Master Editor
    phase2_res = run_phase2_orchestration()
    rendered_reels = phase2_res.get("rendered_files", [])
    logger.info(f"🎬 [SCHEDULED BATCH COMPLETE] Rendered {len(rendered_reels)} reel(s).")
    return rendered_reels
