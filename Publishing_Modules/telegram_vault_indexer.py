"""
Publishing_Modules / telegram_vault_indexer.py
================================================
Telegram Storage Group Unified Master Vault Indexer.

Turns Telegram into an unlimited, zero-cost cloud data lake for ephemeral runners
(GitHub Actions / Docker). Stores permanent file_id references and full visual/lyric
intelligence in a single pinned master_vault_index.json document inside the storage group.

Columns:
  Column 1 (processed_reels):
    Indexed by session_id, social_media_id, and custom_title.
    Stores master_video_file_id, audio_data (pool_metadata + lyric_intel),
    and visual_data (.clip_intelligence.json).

  Column 2 (downloaded_sources):
    Indexed by social_media_id (Instagram/YouTube URL) and session_id.
    Stores raw_video_file_id, extracted_audio_file_id, and audio_math.
    Enables 1.5s cache hits on duplicate URL requests without re-downloading.

Author: AMTCE Serverless Vault Architecture v1.0
"""

import os
import sys
import json
import time
import logging
import urllib.request
import urllib.parse
from typing import Dict, Any, Optional, Tuple

try:
    from dotenv import load_dotenv
    for p in ["Credentials/.env", ".env"]:
        if os.path.exists(p):
            load_dotenv(p, override=False)
            break
except ImportError:
    pass

logger = logging.getLogger("telegram_vault_indexer")

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(_REPO_ROOT, "data")
MASTER_INDEX_FILE = os.path.join(DATA_DIR, "master_vault_index.json")


def _empty_vault_index() -> Dict[str, Any]:
    return {
        "version": 2.0,
        "updated_at": time.time(),
        "pinned_message_id": None,
        "column_1_processed_reels": {
            "by_session_id": {},
            "by_social_media_id": {},
            "by_user_id": {},  # User-scoped indexing
        },
        "column_2_downloaded_sources": {
            "by_social_media_id": {},
            "by_session_id": {},
            "by_user_id": {},  # User-scoped indexing
        },
    }


class TelegramVaultIndexer:
    """
    Manages reading, writing, uploading, and pinning the master_vault_index.json
    inside TELEGRAM_STORAGE_GROUP_ID.
    """

    def __init__(self, index_file: str = MASTER_INDEX_FILE):
        self.index_file = index_file
        os.makedirs(os.path.dirname(self.index_file), exist_ok=True)
        self.vault_index = self._load_local_index()

    def _load_local_index(self) -> Dict[str, Any]:
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "column_1_processed_reels" in data:
                        return data
            except Exception as e:
                logger.warning(f"⚠️ Could not load local vault index: {e}")
        return _empty_vault_index()

    def _save_local_index(self):
        try:
            self.vault_index["updated_at"] = time.time()
            temp_path = self.index_file + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.vault_index, f, indent=2, ensure_ascii=False)
            os.replace(temp_path, self.index_file)
        except Exception as e:
            logger.error(f"❌ Failed to save local vault index: {e}")

    # ── LOOKUP APIs ───────────────────────────────────────────────────────────

    def lookup_downloaded_source(self, social_url: str) -> Optional[Dict[str, Any]]:
        """
        Column 2 Lookup: Returns cached raw video file_id and audio_math if this URL
        was downloaded previously. Enables 1.5s re-use without re-downloading.
        """
        if not social_url:
            return None
        clean_url = str(social_url).strip().rstrip("`").rstrip("%60")
        c2 = self.vault_index.get("column_2_downloaded_sources", {}).get("by_social_media_id", {})
        
        # 1. Exact match
        hit = c2.get(clean_url) or c2.get(social_url.strip())
        if hit:
            logger.info(f"⚡ [VAULT CACHE HIT] Column 2 found source for URL: {clean_url[:60]}...")
            return hit

        # 2. Extract shortcode or video ID and match
        import re
        sc_match = re.search(r"/(?:reel|reels|p|shorts|v)/([A-Za-z0-9_-]{5,})", clean_url)
        shortcode = sc_match.group(1) if sc_match else None
        if shortcode:
            for stored_url, entry in c2.items():
                if shortcode in stored_url or shortcode in str(entry.get("session_id", "")):
                    logger.info(f"⚡ [VAULT CACHE HIT] Column 2 matched shortcode '{shortcode}' -> {stored_url[:60]}")
                    return entry

        # 3. Substring matching fallback
        for stored_url, entry in c2.items():
            s_clean = stored_url.split("?")[0].rstrip("/").rstrip("`").rstrip("%60")
            u_clean = clean_url.split("?")[0].rstrip("/")
            if s_clean and u_clean and (s_clean == u_clean or s_clean.endswith(u_clean) or u_clean.endswith(s_clean)):
                logger.info(f"⚡ [VAULT CACHE HIT] Column 2 matched base URL -> {stored_url[:60]}")
                return entry

        return None

    def lookup_processed_reel(self, session_id: Optional[str] = None, social_url: Optional[str] = None, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Column 1 Lookup: Returns master reel data and full intelligence dicts by
        session_id, social_media_id, or user_id.
        """
        c1 = self.vault_index.get("column_1_processed_reels", {})
        
        # User-scoped lookup
        if user_id:
            user_data = c1.get("by_user_id", {}).get(user_id, {})
            if session_id and session_id in user_data:
                return user_data[session_id]
            if social_url:
                for sess_id, entry in user_data.items():
                    if entry.get("social_media_id") == social_url.strip():
                        return entry
        
        # Global lookup
        if session_id:
            hit = c1.get("by_session_id", {}).get(session_id)
            if hit:
                return hit
        if social_url:
            sess_link = c1.get("by_social_media_id", {}).get(social_url.strip())
            if sess_link:
                return c1.get("by_session_id", {}).get(sess_link)
        return None

    async def download_audio_track_from_vault(self, bot, track_name: str, dest_dir: Optional[str] = None) -> Optional[str]:
        """
        On-Demand Audio Vault Fetcher:
        If an audio track selected from pool_metadata.json is missing on local disk,
        this method queries Column 2 of master_vault_index.json for extracted_audio_file_id,
        downloads it from Telegram Storage Group in ~1s, and saves it to Original_audio/active/<track_name>.
        """
        if not track_name or not bot:
            return None

        filename = os.path.basename(track_name)
        if not dest_dir:
            dest_dir = os.path.join(_REPO_ROOT, "Original_audio", "active")
        os.makedirs(dest_dir, exist_ok=True)
        local_path = os.path.join(dest_dir, filename)

        if os.path.exists(local_path) and os.path.getsize(local_path) > 1024:
            return local_path

        # Find extracted_audio_file_id in Column 2 or Column 1
        c2 = self.vault_index.get("column_2_downloaded_sources", {}).get("by_social_media_id", {})
        file_id = None
        for _url, entry in c2.items():
            if entry.get("extracted_audio_file_id") and (filename in _url or filename in str(entry.get("session_id", ""))):
                file_id = entry["extracted_audio_file_id"]
                break

        if not file_id:
            c2_sess = self.vault_index.get("column_2_downloaded_sources", {}).get("by_session_id", {})
            for sess_id, entry in c2_sess.items():
                if entry.get("extracted_audio_file_id") and (filename in sess_id or filename in str(entry.get("social_media_id", ""))):
                    file_id = entry["extracted_audio_file_id"]
                    break

        if file_id:
            try:
                logger.info(f"📥 [VAULT FETCH] Downloading on-demand audio track '{filename}' from Telegram Storage Group...")
                t_file = await bot.get_file(file_id)
                await t_file.download_to_drive(custom_path=local_path)
                if os.path.exists(local_path) and os.path.getsize(local_path) > 1024:
                    logger.info(f"✅ [VAULT FETCH SUCCESS] Audio track ready: {local_path}")
                    return local_path
            except Exception as e:
                logger.warning(f"⚠️ Vault on-demand audio fetch failed for '{filename}': {e}")
        return None

    def download_telegram_file_sync(self, file_id: str, dest_path: str) -> bool:
        """
        Synchronous direct HTTP downloader from Telegram Bot API using file_id.
        Streams in 64KB chunks directly into dest_path.
        """
        if not file_id:
            return False
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            return False

        try:
            os.makedirs(os.path.dirname(os.path.abspath(dest_path)), exist_ok=True)
            get_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
            req = urllib.request.Request(get_url, headers={"User-Agent": "AMTCE-VaultDownloader"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if not data.get("ok") or not data.get("result", {}).get("file_path"):
                    logger.warning(f"[VAULT DOWNLOAD] getFile failed for {file_id}: {data}")
                    return False
                remote_path = data["result"]["file_path"]

            down_url = f"https://api.telegram.org/file/bot{bot_token}/{remote_path}"
            down_req = urllib.request.Request(down_url, headers={"User-Agent": "AMTCE-VaultDownloader"})
            temp_dest = dest_path + ".tmp"
            with urllib.request.urlopen(down_req, timeout=60) as src, open(temp_dest, "wb") as dst:
                while True:
                    chunk = src.read(65536)
                    if not chunk:
                        break
                    dst.write(chunk)

            if os.path.exists(temp_dest) and os.path.getsize(temp_dest) > 100:
                os.replace(temp_dest, dest_path)
                logger.info(f"✅ [VAULT DOWNLOAD SUCCESS] Hydrated {os.path.basename(dest_path)} ({os.path.getsize(dest_path)} bytes) from Telegram Storage.")
                return True
            else:
                if os.path.exists(temp_dest): os.remove(temp_dest)
                return False
        except Exception as e:
            logger.warning(f"⚠️ [VAULT DOWNLOAD ERROR] Could not download file_id {file_id}: {e}")
            return False

    def hydrate_raw_video_from_vault(self, social_url: str, destination_dir: str) -> Optional[str]:
        """
        Phase 1 Ingestion Accelerator:
        Checks Column 2 of master_vault_index.json for cached raw video.
        If found, downloads it directly from Telegram Storage in ~1s into destination_dir/video.mp4.
        """
        hit = self.lookup_downloaded_source(social_url)
        if not hit:
            # Fallback search by shortcode substring
            c2 = self.vault_index.get("column_2_downloaded_sources", {}).get("by_social_media_id", {})
            for u, entry in c2.items():
                if any(part in u for part in social_url.split("/") if len(part) > 6):
                    hit = entry
                    break

        if hit and hit.get("raw_video_file_id"):
            file_id = hit["raw_video_file_id"]
            out_path = os.path.join(destination_dir, "video.mp4")
            if os.path.exists(out_path) and os.path.getsize(out_path) > 1024:
                return out_path
            logger.info(f"📥 [VAULT HYDRATE] Fetching raw video from Telegram Storage Group for {social_url[:60]}...")
            if self.download_telegram_file_sync(file_id, out_path):
                return out_path
        return None

    def hydrate_audio_and_math_from_vault(self, social_url: str, destination_dir: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Phase 1 Audio & Math Accelerator:
        Checks Column 2 of master_vault_index.json for extracted_audio_file_id and audio_math.
        Downloads extracted audio WAV and returns cached beat DSP math.
        """
        hit = self.lookup_downloaded_source(social_url)
        if not hit:
            c2 = self.vault_index.get("column_2_downloaded_sources", {}).get("by_social_media_id", {})
            for u, entry in c2.items():
                if any(part in u for part in social_url.split("/") if len(part) > 6):
                    hit = entry
                    break

        audio_path = None
        audio_math = None
        if hit:
            audio_math = hit.get("audio_math")
            file_id = hit.get("extracted_audio_file_id")
            if file_id:
                wav_path = os.path.join(destination_dir, "video_extracted.wav")
                if os.path.exists(wav_path) and os.path.getsize(wav_path) > 1024:
                    audio_path = wav_path
                else:
                    logger.info(f"📥 [VAULT HYDRATE] Fetching extracted audio from Telegram Storage Group for {social_url[:60]}...")
                    if self.download_telegram_file_sync(file_id, wav_path):
                        audio_path = wav_path
        return audio_path, audio_math

    def get_vault_audio_pool(self) -> Dict[str, Dict[str, Any]]:
        """
        BGM Selection Primary Index:
        Gathers all candidate audio tracks, beat math, and semantic intelligence
        indexed across master_vault_index.json (from both column_1_processed_reels and column_2_downloaded_sources).
        Returns a mapping of track_filename -> metadata dict (bpm, dominant_emotion, vibe_tags, lyrics, tension_arc, file_id, etc.).
        """
        pool = {}
        # 1. From Column 1 processed reels (contains rich lyric_intel + pool_metadata)
        c1 = self.vault_index.get("column_1_processed_reels", {}).get("by_session_id", {})
        for sess_id, rdata in c1.items():
            adata = rdata.get("audio_data") or {}
            lyric_intel = adata.get("lyric_intel") or {}
            pool_meta = adata.get("pool_metadata") or {}
            track_name = pool_meta.get("selected_audio_track") or pool_meta.get("selected_bgm_track")
            if track_name:
                fname = os.path.basename(track_name)
                pool[fname] = {
                    "filename": fname,
                    "bpm": float(pool_meta.get("tempo_bpm") or pool_meta.get("bpm") or lyric_intel.get("tempo_bpm", 120.0)),
                    "energy": float(pool_meta.get("energy", 0.5)),
                    "dominant_emotion": str(lyric_intel.get("dominant_emotion") or pool_meta.get("dominant_emotion", "hype")),
                    "vibe_tags": list(lyric_intel.get("vibe_tags") or pool_meta.get("vibe_tags", [])),
                    "energy_profile": str(lyric_intel.get("energy_profile") or pool_meta.get("energy_profile", "medium")),
                    "has_vocals": bool(lyric_intel.get("has_vocals", pool_meta.get("has_vocals", False))),
                    "language": str(lyric_intel.get("language") or pool_meta.get("language", "unknown")),
                    "lyrics": lyric_intel.get("lyrics", []),
                    "shot_directives": lyric_intel.get("shot_directives", []),
                    "tension_arc": lyric_intel.get("tension_arc", []),
                    "emotional_peak_moments": lyric_intel.get("emotional_peak_moments", []),
                    "source": "vault_column_1",
                    "file_id": adata.get("audio_file_id") or pool_meta.get("file_id")
                }

        # 2. From Column 2 downloaded sources (harvested audio with math and semantic context)
        c2 = self.vault_index.get("column_2_downloaded_sources", {}).get("by_social_media_id", {})
        for url, sdata in c2.items():
            math_data = sdata.get("audio_math") or {}
            sem_data = math_data.get("semantic_context") or {}
            audio_file_id = sdata.get("extracted_audio_file_id")
            sess_id = sdata.get("session_id", "source")
            fname = f"{sess_id}_extracted.wav"

            # Strict candidate gate: Must be genuine musical audio with >= 12 beats, NOT speech-only, NOT unusable
            beat_cnt = int(math_data.get("beat_count", 0))
            is_speech_only = bool(math_data.get("is_speech_only", False) or sem_data.get("is_speech_only", False))
            is_unusable = bool(math_data.get("is_unusable", False) or sem_data.get("is_unusable", False))

            if beat_cnt >= 12 and not is_speech_only and not is_unusable and audio_file_id:
                pool[fname] = {
                    "filename": fname,
                    "bpm": float(math_data.get("tempo_bpm", 120.0)),
                    "energy": float(math_data.get("avg_energy", 0.5)),
                    "dominant_emotion": str(sem_data.get("dominant_emotion") or math_data.get("vibe", "groove")),
                    "vibe_tags": list(sem_data.get("vibe_tags") or [math_data.get("vibe", "groove")]),
                    "energy_profile": str(sem_data.get("energy_profile", "medium")),
                    "has_vocals": bool(sem_data.get("has_vocals", False)),
                    "language": str(sem_data.get("language", "unknown")),
                    "is_unusable": False,
                    "is_speech_only": False,
                    "source": "vault_column_2",
                    "file_id": audio_file_id
                }

        return pool

    def hydrate_bgm_track_from_vault(self, track_filename: str, destination_dir: str) -> Optional[str]:
        """
        Hydrates a selected BGM track directly from Telegram Storage Group Vault
        if it's not already on local disk.
        """
        target_path = os.path.join(destination_dir, track_filename)
        if os.path.exists(target_path) and os.path.getsize(target_path) > 1024:
            return target_path

        pool = self.get_vault_audio_pool()
        track_info = pool.get(track_filename) or pool.get(os.path.basename(track_filename))
        if track_info and track_info.get("file_id"):
            file_id = track_info["file_id"]
            logger.info(f"📥 [VAULT BGM HYDRATE] Downloading '{track_filename}' from Telegram Storage Vault (file_id: {file_id[:16]}...)...")
            if self.download_telegram_file_sync(file_id, target_path):
                return target_path
        return None

    async def sync_vault_index_from_telegram(self, bot) -> bool:
        """
        Startup Sync: Checks TELEGRAM_STORAGE_GROUP_ID for pinned master_vault_index.json.
        Downloads and merges it into local disk storage so ephemeral runners hydrate in 0.5s.
        """
        storage_group_id = os.getenv("TELEGRAM_STORAGE_GROUP_ID") or os.getenv("TELEGRAM_CHAT_ID")
        if not storage_group_id or not bot:
            return False

        try:
            logger.info(f"🔍 [VAULT SYNC] Checking Storage Group ({storage_group_id}) for pinned master index...")
            chat = await bot.get_chat(chat_id=int(storage_group_id))
            pinned = chat.pinned_message if hasattr(chat, "pinned_message") else None

            if pinned and pinned.document and pinned.document.file_name == "master_vault_index.json":
                doc_file = await bot.get_file(pinned.document.file_id)
                temp_down = os.path.join(DATA_DIR, "pinned_vault_down.json")
                await doc_file.download_to_drive(custom_path=temp_down)

                if os.path.exists(temp_down) and os.path.getsize(temp_down) > 50:
                    with open(temp_down, "r", encoding="utf-8") as f:
                        remote_index = json.load(f)

                    if isinstance(remote_index, dict) and "column_1_processed_reels" in remote_index:
                        self.vault_index = remote_index
                        self.vault_index["pinned_message_id"] = pinned.message_id
                        self._save_local_index()
                        self._hydrate_local_caches()
                        logger.info(f"✅ [VAULT SYNC SUCCESS] Hydrated master index from Telegram (Pinned msg: {pinned.message_id})")
                        return True
        except Exception as e:
            logger.warning(f"⚠️ [VAULT SYNC] Could not fetch pinned vault index: {e}")
        return False

    def _hydrate_local_caches(self):
        """
        Hydrates local disk stores (pool_metadata.json, .clip_intelligence.json)
        from the downloaded master_vault_index.json.
        """
        try:
            # 1. Hydrate pool_metadata.json
            c1_reels = self.vault_index.get("column_1_processed_reels", {}).get("by_session_id", {})
            if c1_reels:
                from Audio_Modules.audio_pool_manager import AudioPoolManager
                pm = AudioPoolManager()
                for sess_id, rdata in c1_reels.items():
                    adata = rdata.get("audio_data") or {}
                    pool_meta = adata.get("pool_metadata") or {}
                    track_name = pool_meta.get("selected_audio_track") or pool_meta.get("selected_bgm_track")
                    if track_name and pool_meta:
                        pm._set_file_metadata(os.path.basename(track_name), pool_meta)
                pm._save_metadata()

            logger.info("⚡ [VAULT HYDRATE] Local pool_metadata and clip caches updated from Vault Index.")
        except Exception as e:
            logger.debug(f"[VAULT HYDRATE] Cache hydration notice: {e}")

    # ── RECORDING APIS ───────────────────────────────────────────────────────

    async def record_downloaded_source(
        self,
        bot,
        social_url: str,
        session_id: str,
        raw_video_path: Optional[str] = None,
        audio_path: Optional[str] = None,
        beat_math: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        pin_now: bool = True,
    ) -> Dict[str, Any]:
        """
        Column 2 Record: Uploads raw source video and extracted audio to TELEGRAM_STORAGE_GROUP_ID,
        saves file_ids under column_2_downloaded_sources, and re-pins master_vault_index.json.
        
        Args:
            user_id: Optional user ID for user-scoped storage
            pin_now: If False, skips re-uploading and pinning the index (useful when chained with record_processed_reel)
        """
        storage_group_id = os.getenv("TELEGRAM_STORAGE_GROUP_ID") or os.getenv("TELEGRAM_CHAT_ID")
        raw_file_id = None
        audio_file_id = None

        if storage_group_id and bot:
            try:
                if raw_video_path and os.path.exists(raw_video_path):
                    with open(raw_video_path, "rb") as rf:
                        rmsg = await bot.send_video(
                            chat_id=int(storage_group_id),
                            video=rf,
                            caption=f"📥 **[VAULT RAW SOURCE]** `{os.path.basename(raw_video_path)}`\n🔗 `{social_url}`\n🆔 `{session_id}`" + (f"\n👤 User: `{user_id}`" if user_id else ""),
                            read_timeout=600.0,
                            write_timeout=600.0
                        )
                        if rmsg and rmsg.video:
                            raw_file_id = rmsg.video.file_id

                if audio_path and os.path.exists(audio_path):
                    logger.info(f"🎙️ [VAULT AUDIO UPLOAD] Sending extracted audio ({os.path.basename(audio_path)}, {os.path.getsize(audio_path)} bytes) to Storage Group...")
                    try:
                        with open(audio_path, "rb") as af:
                            amsg = await bot.send_document(
                                chat_id=int(storage_group_id),
                                document=af,
                                filename=os.path.basename(audio_path),
                                caption=f"🎵 **[VAULT AUDIO EXTRACT]** `{os.path.basename(audio_path)}`\n🆔 `{session_id}`" + (f"\n👤 User: `{user_id}`" if user_id else ""),
                                read_timeout=600.0,
                                write_timeout=600.0
                            )
                            if amsg:
                                audio_file_id = amsg.document.file_id if amsg.document else (amsg.audio.file_id if amsg.audio else None)
                                logger.info(f"✅ [VAULT AUDIO SUCCESS] Extracted audio file_id captured: {audio_file_id}")
                    except Exception as _aud_err:
                        logger.warning(f"❌ [VAULT AUDIO ERROR] Audio upload failed: {_aud_err}")
            except Exception as e:
                logger.warning(f"⚠️ Vault raw source upload warning: {e}")

        entry = {
            "social_media_id": social_url,
            "session_id": session_id,
            "raw_video_file_id": raw_file_id,
            "extracted_audio_file_id": audio_file_id,
            "audio_math": beat_math or {},
            "downloaded_at": time.time(),
            "user_id": user_id,
        }

        c2 = self.vault_index.setdefault("column_2_downloaded_sources", {})
        c2.setdefault("by_social_media_id", {})[social_url] = entry
        c2.setdefault("by_session_id", {})[session_id] = entry
        
        # User-scoped indexing
        if user_id:
            c2.setdefault("by_user_id", {}).setdefault(user_id, {})[session_id] = entry

        self._save_local_index()
        if pin_now:
            await self._upload_and_pin_index(bot, storage_group_id)
        logger.info(f"📦 [VAULT RECORD] Recorded Column 2 source for URL: {social_url[:60]}" + (f" (User: {user_id})" if user_id else ""))
        return entry

    async def record_processed_reel(
        self,
        bot,
        session_id: str,
        social_url: Optional[str],
        custom_title: Optional[str],
        master_video_path: str,
        clip_intel: Optional[Dict[str, Any]] = None,
        lyric_intel: Optional[Dict[str, Any]] = None,
        master_file_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Column 1 Record: Saves rendered master reel intelligence and file_id into
        column_1_processed_reels, updates local index, and re-pins master_vault_index.json.
        
        Args:
            user_id: Optional user ID for user-scoped storage
        """
        storage_group_id = os.getenv("TELEGRAM_STORAGE_GROUP_ID") or os.getenv("TELEGRAM_CHAT_ID")

        entry = {
            "session_id": session_id,
            "social_media_id": social_url or "direct_upload",
            "custom_title": custom_title,
            "master_video_file_id": master_file_id,
            "video_path": os.path.abspath(master_video_path),
            "created_at": time.time(),
            "audio_data": {
                "lyric_intel": lyric_intel or {},
            },
            "visual_data": clip_intel or {},
            "editing_plan_history": [],  # Sorted list of attempts & user approval status for RAG Creator Behavior
            "pipeline_execution_trajectory": {
                "stage_0_intent_classification": {},
                "stage_1_visual_forensics": clip_intel or {},
                "stage_2_audio_intelligence": lyric_intel or {},
                "stage_3_attempts_and_re_edits": [],
                "stage_4_final_verdict": {"status": "AWAITING_REVIEW", "timestamp": time.time()},
            },
            "user_id": user_id,
        }

        c1 = self.vault_index.setdefault("column_1_processed_reels", {})
        existing = c1.get("by_session_id", {}).get(session_id)
        if existing:
            if "editing_plan_history" in existing:
                entry["editing_plan_history"] = existing["editing_plan_history"]
            if "pipeline_execution_trajectory" in existing:
                entry["pipeline_execution_trajectory"] = existing["pipeline_execution_trajectory"]

        c1.setdefault("by_session_id", {})[session_id] = entry
        if social_url:
            c1.setdefault("by_social_media_id", {})[social_url] = session_id
        
        # User-scoped indexing
        if user_id:
            c1.setdefault("by_user_id", {}).setdefault(user_id, {})[session_id] = entry

        self._save_local_index()
        await self._upload_and_pin_index(bot, storage_group_id)
        logger.info(f"🎬 [VAULT RECORD] Recorded Column 1 master reel for Session: {session_id}" + (f" (User: {user_id})" if user_id else ""))
        return entry

    async def update_pipeline_trajectory(
        self,
        bot,
        session_id: str,
        stage_name: str,
        stage_data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        AI Trajectory Store: Records structured, un-mixed pipeline stage logs into
        column_1_processed_reels -> pipeline_execution_trajectory.
        Stages:
          - 'stage_0_intent'  : IntentVector classification & confidence
          - 'stage_1_visual'  : Keyframe sampling, faces, watermark detection
          - 'stage_2_audio'   : Beat math, Whisper transcript, Gemini lyric directives
          - 'stage_3_attempts': Rendering attempts, FFmpeg filtergraph, user verdict
          - 'stage_4_verdict' : Final outcome (APPROVED/REJECTED), total time, winning attempt
        """
        c1 = self.vault_index.setdefault("column_1_processed_reels", {})
        session_entry = c1.setdefault("by_session_id", {}).setdefault(session_id, {
            "session_id": session_id,
            "created_at": time.time(),
        })

        trajectory = session_entry.setdefault("pipeline_execution_trajectory", {
            "stage_0_intent_classification": {},
            "stage_1_visual_forensics": {},
            "stage_2_audio_intelligence": {},
            "stage_3_attempts_and_re-edits": [],
            "stage_4_final_verdict": {},
        })

        stage_key = {
            "stage_0_intent": "stage_0_intent_classification",
            "stage_1_visual": "stage_1_visual_forensics",
            "stage_2_audio": "stage_2_audio_intelligence",
            "stage_3_attempts": "stage_3_attempts_and_re-edits",
            "stage_4_verdict": "stage_4_final_verdict",
        }.get(stage_name, stage_name)

        if stage_key == "stage_3_attempts_and_re-edits":
            if not isinstance(trajectory.get("stage_3_attempts_and_re-edits"), list):
                trajectory["stage_3_attempts_and_re-edits"] = []
            trajectory["stage_3_attempts_and_re-edits"].append(stage_data)
        else:
            trajectory[stage_key] = stage_data

        session_entry["updated_at"] = time.time()
        self._save_local_index()
        storage_group_id = os.getenv("TELEGRAM_STORAGE_GROUP_ID") or os.getenv("TELEGRAM_CHAT_ID")
        await self._upload_and_pin_index(bot, storage_group_id)
        logger.info(f"🧠 [TRAJECTORY RECORD] Updated {stage_key} for Session: {session_id}")
        return trajectory


    async def record_plan_attempt(
        self,
        bot,
        session_id: str,
        attempt_number: int,
        editing_plan: Dict[str, Any],
        user_approved: bool = False,
        user_feedback: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        RAG Creator Behavior Store: Appends an editing plan attempt (and user approval/feedback)
        to column_1_processed_reels -> editing_plan_history.
        Stores both approved (positive RAG) and rejected (negative RAG) attempts for AI learning.
        """
        c1 = self.vault_index.get("column_1_processed_reels", {}).get("by_session_id", {})
        session_entry = c1.get(session_id)
        if not session_entry:
            logger.warning(f"⚠️ Cannot record plan attempt: session '{session_id}' not found in Column 1 index.")
            return None

        history = session_entry.setdefault("editing_plan_history", [])
        attempt_record = {
            "attempt_number": attempt_number,
            "timestamp": time.time(),
            "user_approved": user_approved,
            "user_feedback": user_feedback or ("Approved by user" if user_approved else "Rejected/Re-edit requested"),
            "editing_plan": editing_plan or {},
        }
        history.append(attempt_record)
        # Keep sorted by attempt_number
        session_entry["editing_plan_history"] = sorted(history, key=lambda x: int(x.get("attempt_number", 0)))

        self._save_local_index()
        storage_group_id = os.getenv("TELEGRAM_STORAGE_GROUP_ID") or os.getenv("TELEGRAM_CHAT_ID")
        await self._upload_and_pin_index(bot, storage_group_id)
        logger.info(f"🧠 [RAG PLAN RECORD] Recorded Attempt {attempt_number} (approved={user_approved}) for Session: {session_id}")
        return attempt_record


    async def _upload_and_pin_index(self, bot, storage_group_id: Optional[str]):
        """Uploads updated master_vault_index.json to TELEGRAM_STORAGE_GROUP_ID and pins it."""
        if not storage_group_id or not bot or not os.path.exists(self.index_file):
            return

        for attempt in range(1, 4):
            try:
                with open(self.index_file, "rb") as idf:
                    doc_msg = await bot.send_document(
                        chat_id=int(storage_group_id),
                        document=idf,
                        filename="master_vault_index.json",
                        caption=f"📌 **[VAULT MASTER INDEX]** Auto-Synced\n🕒 `{time.strftime('%Y-%m-%d %H:%M:%S')}`\n📊 Reels: `{len(self.vault_index.get('column_1_processed_reels', {}).get('by_session_id', {}))}` | Sources: `{len(self.vault_index.get('column_2_downloaded_sources', {}).get('by_social_media_id', {}))}`",
                        read_timeout=600.0,
                        write_timeout=600.0
                    )
                    if doc_msg and doc_msg.message_id:
                        await bot.pin_chat_message(
                            chat_id=int(storage_group_id),
                            message_id=doc_msg.message_id,
                            disable_notification=True,
                            read_timeout=60.0,
                            write_timeout=60.0
                        )
                        self.vault_index["pinned_message_id"] = doc_msg.message_id
                        logger.info(f"📌 [VAULT PIN] Pinned updated master_vault_index.json (Message ID: {doc_msg.message_id})")
                        return
            except Exception as e:
                logger.warning(f"⚠️ Vault index upload/pin notice (attempt {attempt}/3): {e}")
                if attempt < 3:
                    import asyncio
                    await asyncio.sleep(2)
