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


THIRTY_DAYS_SECONDS = 30 * 86400  # 30 Days in Seconds


def purge_expired_accounts() -> List[str]:
    """
    Checks all configured source accounts and purges any account older than 30 days.
    Returns list of removed handles.
    """
    if not os.path.exists(ACCOUNTS_JSON):
        return []

    try:
        with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        pap = data.setdefault("_paparazzi", {})
        accs = pap.get("source_accounts", [])
        timestamps = pap.setdefault("account_timestamps", {})
        now = time.time()

        expired = []
        for handle in list(accs):
            added_at = timestamps.get(handle)
            if added_at and (now - added_at) > THIRTY_DAYS_SECONDS:
                expired.append(handle)
                accs.remove(handle)
                timestamps.pop(handle, None)

        if expired:
            with open(ACCOUNTS_JSON, "w", encoding="utf-8") as wf:
                json.dump(data, wf, indent=2)
            sync_source_accounts_to_telegram_vault()
            logger.info("⏰ [EXPIRATION] Purged %d expired account(s) after 30 days: %s", len(expired), expired)

        return expired
    except Exception as e:
        logger.error("❌ Error during account expiration check: %s", e)
        return []


def get_active_accounts_metadata() -> List[Dict[str, Any]]:
    """Returns list of active target accounts with creation timestamps and days remaining until 30-day limit."""
    purge_expired_accounts()
    if not os.path.exists(ACCOUNTS_JSON):
        return []
    try:
        with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
        pap = data.get("_paparazzi", {})
        accs = pap.get("source_accounts", [])
        timestamps = pap.get("account_timestamps", {})
        now = time.time()

        res = []
        for h in accs:
            added_at = timestamps.get(h, now)
            elapsed_days = int((now - added_at) / 86400)
            days_left = max(0, 30 - elapsed_days)
            res.append({
                "handle": h,
                "added_at": added_at,
                "days_elapsed": elapsed_days,
                "days_left": days_left
            })
        return res
    except Exception as e:
        logger.error("Error loading account metadata: %s", e)
        return []


def get_rotated_max_two_accounts(max_accounts: int = 2) -> List[str]:
    """
    Reads source_accounts.json, selects max_accounts (2) using round-robin index,
    and updates the active target list. Automatically purges accounts >30 days old.
    """
    purge_expired_accounts()
    if not os.path.exists(ACCOUNTS_JSON):
        logger.warning(f"⚠️ {ACCOUNTS_JSON} not found. Please add target source accounts via Telegram Chat /addaccount.")
        return []

    try:
        with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)

        paparazzi = data.get("_paparazzi", {})
        all_accounts = paparazzi.get("source_accounts", [])
        if not all_accounts:
            logger.warning("⚠️ No target source accounts configured in source_accounts.json. Use /addaccount <handle> to add accounts.")
            return []

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
        return []


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

    clips_per_run = 5
    try:
        clips_per_run = int(os.getenv("CLIPS_PER_ACCOUNT_PER_RUN", "5"))
    except ValueError:
        clips_per_run = 5

    # Run ingestion for selected accounts
    ingest_res = run_phase1_ingestion(mode="auto", limit_per_account=clips_per_run)
    downloaded_files = ingest_res.get("downloaded_files", [])
    if not ingest_res.get("success") or not downloaded_files:
        logger.warning("⚠️ [SCHEDULED BATCH] Ingestion returned 0 new clips.")
        return []

    # Target ONLY the newly downloaded clip directories
    target_dirs = list(set(os.path.dirname(f) for f in downloaded_files if os.path.exists(f)))

    # Run AI Master Editor on ONLY the target downloaded clips
    phase2_res = run_phase2_orchestration(target_dirs=target_dirs, limit=len(target_dirs))
    rendered_reels = phase2_res.get("rendered_files", [])
    logger.info(f"🎬 [SCHEDULED BATCH COMPLETE] Rendered {len(rendered_reels)} reel(s).")
    return rendered_reels


def add_source_account(account_handle: str, platform: str = "instagram") -> bool:
    """Adds a new target account handle with creation timestamp to source_accounts.json and syncs to Telegram Vault."""
    clean_handle = account_handle.strip().lstrip("@")
    if not clean_handle:
        return False
    try:
        data = {}
        if os.path.exists(ACCOUNTS_JSON):
            with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
        
        pap = data.setdefault("_paparazzi", {})
        accs = pap.setdefault("source_accounts", [])
        timestamps = pap.setdefault("account_timestamps", {})

        if clean_handle not in accs:
            accs.append(clean_handle)
            timestamps[clean_handle] = time.time()
            with open(ACCOUNTS_JSON, "w", encoding="utf-8") as wf:
                json.dump(data, wf, indent=2)
            sync_source_accounts_to_telegram_vault()
            logger.info("➕ [SOURCE ACCOUNTS] Added @%s (%s) with 30-day limit to source_accounts.json & synced to Telegram Vault", clean_handle, platform)
            return True
        else:
            # Refresh timestamp on re-adding
            timestamps[clean_handle] = time.time()
            with open(ACCOUNTS_JSON, "w", encoding="utf-8") as wf:
                json.dump(data, wf, indent=2)
            return True
    except Exception as e:
        logger.error("❌ Failed to add source account @%s: %s", clean_handle, e)
    return False


def remove_source_account(account_handle: str) -> bool:
    """Removes a target account handle from source_accounts.json and syncs to Telegram Vault."""
    clean_handle = account_handle.strip().lstrip("@")
    if not clean_handle:
        return False
    try:
        if os.path.exists(ACCOUNTS_JSON):
            with open(ACCOUNTS_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
            pap = data.get("_paparazzi", {})
            accs = pap.get("source_accounts", [])
            timestamps = pap.get("account_timestamps", {})

            if clean_handle in accs:
                accs.remove(clean_handle)
                timestamps.pop(clean_handle, None)
                with open(ACCOUNTS_JSON, "w", encoding="utf-8") as wf:
                    json.dump(data, wf, indent=2)
                sync_source_accounts_to_telegram_vault()
                logger.info("🗑️ [SOURCE ACCOUNTS] Removed @%s from source_accounts.json & synced to Telegram Vault", clean_handle)
                return True
    except Exception as e:
        logger.error("❌ Failed to remove source account @%s: %s", clean_handle, e)
    return False


def sync_source_accounts_to_telegram_vault():
    """Uploads source_accounts.json to Telegram Storage Group cloud vault."""
    try:
        from Publishing_Modules.telegram_vault_indexer import TelegramVaultIndexer
        indexer = TelegramVaultIndexer()
        storage_group_id = os.getenv("TELEGRAM_STORAGE_GROUP_ID") or os.getenv("TELEGRAM_CHAT_ID")
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        if storage_group_id and bot_token and os.path.exists(ACCOUNTS_JSON):
            from Downloader_Modules.telegram_listener import _send_file_multipart
            res = _send_file_multipart(
                "sendDocument",
                storage_group_id,
                "document",
                ACCOUNTS_JSON,
                caption=f"📋 **[VAULT BACKUP]** `source_accounts.json` (Updated {time.strftime('%H:%M:%S')})"
            )
            if res and isinstance(res, dict):
                doc_id = res.get("document", {}).get("file_id")
                if doc_id:
                    indexer.vault_index["source_accounts_file_id"] = doc_id
                    indexer._save_local_index()
                    indexer.upload_and_pin_vault_index_sync(_send_file_multipart)
                    logger.info("✅ [SOURCE ACCOUNTS VAULT BACKUP] Uploaded & PINNED updated source_accounts.json (file_id: %s)", doc_id[:15])
    except Exception as _e:
        logger.debug("Notice syncing source_accounts.json to vault: %s", _e)
