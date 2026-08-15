"""
main.py — Master Orchestration & Telegram Bot Entrypoint
=========================================================
Kingdom: Master System Controller
Purpose: Connect Phase 1 (Ingestion & Scraping), Phase 2 & 3 (AI Perception & Rendering),
         Phase 4 (Multi-Platform Publishing), and Telegram Admin Review Buttons.

Telegram 4-Button Approval Suite:
  - [✅ Clean (Yes)]      callback_data="wm_clean"        -> Confirm clip quality & watermark clean
  - [❌ Bad (No)]         callback_data="wm_bad"          -> Flag quality issue & trigger re-edit
  - [🚀 Approve & Post]   callback_data="approve_post"    -> Publish to YouTube, Meta, TikTok
  - [🗑️ Reject]           callback_data="reject_discard"  -> Discard ticket & delete local .mp4
"""

import os
import sys
import time
import json
import logging
import argparse
import signal
from typing import Dict, List, Any, Optional

# Instant Ctrl+C Termination Handler
def _instant_sigint_handler(signum, frame):
    print("\n🛑 [INSTANT EXIT] Ctrl+C detected. Terminating process immediately...", flush=True)
    os._exit(130)

try:
    signal.signal(signal.SIGINT, _instant_sigint_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _instant_sigint_handler)
except Exception:
    pass

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure the canonical workspace root is on sys.path.
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)


# ── Logging & Polling Filter Setup ───────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("main_orchestrator")

class PollingFilter(logging.Filter):
    def filter(self, record):
        return "getUpdates" not in record.getMessage()

for lib in ["httpx", "telegram", "telegram.ext", "httpcore"]:
    l = logging.getLogger(lib)
    l.setLevel(logging.WARNING)
    l.addFilter(PollingFilter())

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(_REPO_ROOT, "Credentials", ".env"), override=True)
except ImportError:
    pass

# ── Import Modular System Packages ───────────────────────────────────────────
from Import_Modules.phase1_imports import run_phase1_ingestion
from Import_Modules.phase2_imports import run_phase2_orchestration
from Downloader_Modules.scheduled_scraper_manager import run_scheduled_scraper_batch, get_rotated_max_two_accounts
from Main_Modules.master_ai_editor import MasterAIEditor
from Publishing_Modules.queue_publisher import PublishQueue
from Publishing_Modules.telegram_session_manager import session_manager
from Publishing_Modules.telegram_vault_indexer import TelegramVaultIndexer
from Core_Modules import MAX_RETRIES

vault_indexer = TelegramVaultIndexer()


# ── Platform Selection Keyboard & State ───────────────────────────────────────
user_selected_platform = {}  # {chat_id: "instagram" | "youtube" | "tiktok" | "direct"}
user_pending_text = {}       # {chat_id: "target_id_string"}
user_pending_reedit_session = {}  # {chat_id: "session_id"} for custom text feedback

def build_reedit_options_keyboard(session_id: str):
    """
    Builds 5-button re-edit feedback menu for aggressive Gemini prompt polishing:
      1. Change Music / Beat Alignment
      2. Aggressive Shot Reshaping (Dopamine Cuts)
      3. Polish Climax & Ending Hook
      4. Fix Intro & First 3s Hook
      5. Custom User Feedback Directive
    """
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("🎵 Change Music & Rhythm", callback_data=f"ro_music_{session_id}")],
            [InlineKeyboardButton("⚡ Aggressive Shot Reshaping (Dopamine Cuts)", callback_data=f"ro_shots_{session_id}")],
            [InlineKeyboardButton("🎬 Polish Climax & Ending", callback_data=f"ro_climax_{session_id}")],
            [InlineKeyboardButton("🎣 Fix Intro & Hook (First 3s)", callback_data=f"ro_hook_{session_id}")],
            [InlineKeyboardButton("✏️ Custom Suggestion...", callback_data=f"ro_custom_{session_id}")],
        ]
        return InlineKeyboardMarkup(keyboard)
    except ImportError:
        return None

def build_best_attempt_comparison_keyboard(session_id: str, total_attempts: int = 5):
    """
    Builds rating keyboard for selecting best attempt 1 to 5 after MAX_RETRIES limit.
    """
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [
                InlineKeyboardButton("Attempt 1", callback_data=f"pick_att_1_{session_id}"),
                InlineKeyboardButton("Attempt 2", callback_data=f"pick_att_2_{session_id}"),
            ],
            [
                InlineKeyboardButton("Attempt 3", callback_data=f"pick_att_3_{session_id}"),
                InlineKeyboardButton("Attempt 4", callback_data=f"pick_att_4_{session_id}"),
            ],
            [
                InlineKeyboardButton("Attempt 5", callback_data=f"pick_att_5_{session_id}"),
            ],
            [
                InlineKeyboardButton("❌ All 5 Attempts Are Bad", callback_data=f"pick_att_none_{session_id}"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    except ImportError:
        return None

def build_platform_selection_keyboard():
    """
    Builds Interactive Platform Selector Keyboard for Bulk Scraping:
      - [ 📸 Instagram Creator ]      callback_data="platform_instagram"
      - [ 🔴 YouTube Shorts / Channel ] callback_data="platform_youtube"
      - [ 🎵 TikTok Creator ]         callback_data="platform_tiktok"
      - [ 🌐 Direct URL / Raw File ]  callback_data="platform_direct"
    """
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [
                InlineKeyboardButton("📸 Instagram Creator", callback_data="platform_instagram"),
                InlineKeyboardButton("🔴 YouTube Shorts / Channel", callback_data="platform_youtube"),
            ],
            [
                InlineKeyboardButton("🎵 TikTok Creator", callback_data="platform_tiktok"),
                InlineKeyboardButton("🌐 Direct URL / Raw File", callback_data="platform_direct"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    except ImportError:
        return None


def build_back_button_keyboard():
    """Builds a single Back/Cancel button keyboard."""
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        return InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Back to Main Menu / Cancel", callback_data="platform_cancel")]])
    except ImportError:
        return None


# ── Telegram Inline Keyboard Builder ─────────────────────────────────────────

def build_telegram_session_keyboard(session_id: str):
    """
    Builds 4-Button Inline Keyboard for Telegram Master Reel Review:
      - [✅ Approve & Set Title]  callback_data="approve_title_<session_id>"
      - [🚀 Post Immediately]     callback_data="approve_post_<session_id>"
      - [❌ Bad / Re-Edit]        callback_data="reedit_<session_id>"
      - [🗑️ Reject & Discard]     callback_data="reject_<session_id>"
    """
    try:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [
                InlineKeyboardButton("✅ Approve & Set Title", callback_data=f"approve_title_{session_id}"),
                InlineKeyboardButton("🚀 Post Immediately", callback_data=f"approve_post_{session_id}"),
            ],
            [
                InlineKeyboardButton("❌ Bad / Re-Edit", callback_data=f"reedit_{session_id}"),
                InlineKeyboardButton("🗑️ Reject & Discard", callback_data=f"reject_{session_id}"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    except ImportError:
        logger.warning("python-telegram-bot package not installed; inline buttons unavailable.")
        return None


# ── Telegram Callback Handlers ───────────────────────────────────────────────

async def handle_telegram_callback(update, context):
    """
    Routes Telegram Inline Button Clicks:
      - Platform Selection: platform_instagram, platform_youtube, platform_tiktok, platform_direct, platform_cancel
      - Reel Review: approve_title_<id>, approve_post_<id>, reedit_<id>, reject_<id>
    """
    query = update.callback_query
    if not query:
        return

    try:
        await query.answer()
    except Exception:
        pass

    data = query.data
    user_id = query.from_user.id
    chat_id = query.message.chat_id if query.message else user_id
    logger.info(f"📲 [TELEGRAM BOT] Received Callback Click: '{data}' from User ID: {user_id}")

    # Handle Back / Cancel Button
    if data == "platform_cancel":
        user_selected_platform.pop(chat_id, None)
        user_pending_text.pop(chat_id, None)
        keyboard = build_platform_selection_keyboard()
        await query.edit_message_text(
            text="👋 **Platform selection cancelled!**\n\n🎯 **Select a platform below to begin:**",
            reply_markup=keyboard
        )
        return

    # Handle Platform Selection Buttons
    if data.startswith("platform_"):
        chosen_p = data.replace("platform_", "").strip()
        user_selected_platform[chat_id] = chosen_p

        # Check if user had already typed a pending target handle before clicking the platform button!
        pending_handle = user_pending_text.pop(chat_id, None)

        if pending_handle and chosen_p != "direct":
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"🎯 **[STEP 1/3] Target Handle Received!**\n\n"
                    f"👤 **Creator**: `@{pending_handle}`\n"
                    f"🌐 **Platform**: `{chosen_p.title()}`\n"
                    f"⚙️ **Status**: Scraping top reels for {chosen_p.title()} & starting AI editing pipeline... Please wait!"
                )
            )
            try:
                run_master_pipeline(
                    mode="auto",
                    target_accounts=[pending_handle],
                    platform=chosen_p,
                    requestor_chat_id=chat_id
                )
            except Exception as _p_err:
                logger.error(f"❌ Error executing pending handle pipeline: {_p_err}")
            return
        elif pending_handle and chosen_p == "direct":
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"📥 **[STEP 1/3] Direct Video Ingestion!**\n\n"
                    f"🔗 **Target**: `{pending_handle}`\n"
                    f"⚙️ **Status**: Ingesting video & starting AI Master Editor..."
                )
            )
            try:
                run_master_pipeline(
                    mode="manual",
                    url=pending_handle if pending_handle.startswith("http") else None,
                    input_path=pending_handle if os.path.exists(pending_handle) else None,
                    platform="direct",
                    requestor_chat_id=chat_id
                )
            except Exception as _p_err:
                logger.error(f"❌ Error executing direct pipeline: {_p_err}")
            return

        prompts = {
            "instagram": "📸 **Instagram Mode Selected!**\n\n👇 **Send the Instagram Creator handle** (e.g. `indiancelebspot` or `@b.town.ind`) to scrape top reels in bulk:",
            "youtube": "🔴 **YouTube Shorts / Channel Mode Selected!**\n\n👇 **Send the YouTube channel handle or URL** (e.g. `@ChannelName` or `https://www.youtube.com/@ChannelName/shorts`) to scrape top Shorts in bulk:",
            "tiktok": "🎵 **TikTok Mode Selected!**\n\n👇 **Send the TikTok Creator handle or URL** (e.g. `@tiktokuser` or `https://www.tiktok.com/@tiktokuser`) to scrape top videos in bulk:",
            "direct": "🌐 **Direct URL / Raw File Mode Selected!**\n\n👇 **Send any video URL** (Instagram Reel, YouTube Short, TikTok, etc.) or **upload a raw `.mp4` video file** directly to process:"
        }
        back_kbd = build_back_button_keyboard()
        await query.edit_message_text(text=prompts.get(chosen_p, "Send target handle or URL below:"), reply_markup=back_kbd)
        return

    if data.startswith("approve_title_"):
        session_id = data.replace("approve_title_", "").strip()
        session_manager.set_awaiting_title(session_id)
        sess = session_manager.get_session(session_id)
        clip_name = os.path.basename(sess["video_path"]) if sess else "reel"
        curr_text = query.message.caption or query.message.text or f"📁 `{clip_name}`"

        new_text = f"{curr_text}\n\n✅ **Approved!**\n✏️ **Please reply with your custom title for '{clip_name}':**"

        try:
            if query.message.video or query.message.document or query.message.photo:
                await query.edit_message_caption(caption=new_text)
            else:
                await query.edit_message_text(text=new_text)
        except Exception as _ce:
            logger.warning(f"⚠️ Callback caption edit warning: {_ce}")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"✅ **Approved!**\n✏️ **Please reply with your custom title for '{clip_name}':**"
            )

    elif data.startswith("approve_post_"):
        session_id = data.replace("approve_post_", "").strip()
        sess = session_manager.set_approved_title(session_id, custom_title="Viral Reel")
        curr_text = query.message.caption or query.message.text or "Master Reel"
        new_text = f"{curr_text}\n\n🚀 **APPROVED & DISPATCHED TO PUBLISHING QUEUE!**"

        try:
            if query.message.video or query.message.document or query.message.photo:
                await query.edit_message_caption(caption=new_text)
            else:
                await query.edit_message_text(text=new_text)
        except Exception:
            await context.bot.send_message(chat_id=query.message.chat_id, text=new_text)

        if sess:
            v_path = sess["video_path"]
            PublishQueue.add(v_path, channel_title="Viral Reel", channel_folder=sess.get("creator", "General"))
            try:
                from Publishing_Modules.media_publisher_main import run_phase4_publishing
                pub_res = run_phase4_publishing(
                    video_path=v_path,
                    title="Viral Reel",
                    tags="#viral #shorts #trending",
                    niche=sess.get("creator", "General")
                )
                status_lines = []
                for p_name, p_info in pub_res.get("platforms", {}).items():
                    st = p_info.get("status")
                    icon = "✅" if st == "success" else ("⏸️" if st == "skipped" else "❌")
                    detail = p_info.get("url") or p_info.get("link") or p_info.get("message") or st
                    status_lines.append(f"• {icon} **{p_name.upper()}**: `{detail}`")

                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"🎉 **Phase 4 Multi-Platform Broadcasting Complete!**\n\n" + "\n".join(status_lines)
                )
            except Exception as pub_err:
                logger.error(f"❌ Phase 4 publishing callback error: {pub_err}")

    elif data.startswith("reedit_"):
        session_id = data.replace("reedit_", "").strip()
        should_retry, count = session_manager.register_retry(user_id)

        if not should_retry:
            keyboard = build_best_attempt_comparison_keyboard(session_id, total_attempts=MAX_RETRIES)
            new_text = (
                f"🛑 **MAXIMUM RETRY LIMIT REACHED ({MAX_RETRIES}/{MAX_RETRIES} Attempts)**\n\n"
                f"Which attempt was the best (1 to {MAX_RETRIES})?\n"
                f"Select your star rating below to save the winning master edit and commit learning weights to RAG memory:"
            )
            try:
                if query.message.video or query.message.document or query.message.photo:
                    await query.edit_message_caption(caption=new_text, reply_markup=keyboard)
                else:
                    await query.edit_message_text(text=new_text, reply_markup=keyboard)
            except Exception as _m_err:
                logger.warning(f"Max retries menu warning: {_m_err}")
            return

        keyboard = build_reedit_options_keyboard(session_id)
        new_text = (
            f"🛠️ **RE-EDIT FEEDBACK DIRECTIVE (Attempt {count}/{MAX_RETRIES})**\n\n"
            f"What specific improvement should Gemini make for retry #{count}?\n"
            f"Select an option below to inject an aggressive correction prompt:"
        )
        try:
            if query.message.video or query.message.document or query.message.photo:
                await query.edit_message_caption(caption=new_text, reply_markup=keyboard)
            else:
                await query.edit_message_text(text=new_text, reply_markup=keyboard)
        except Exception as _re_e:
            logger.warning(f"Re-edit menu warning: {_re_e}")

    elif data.startswith("pick_att_"):
        # Format: pick_att_1_<session_id> or pick_att_none_<session_id>
        parts = data.split("_", 3)
        choice_str = parts[2]
        session_id = parts[3] if len(parts) > 3 else ""

        sess = session_manager.get_session(session_id)
        clip_id = sess.get("clip_id", "clip") if sess else "clip"
        history = sess.get("attempt_history", []) if sess else []

        if choice_str == "none":
            from Core_Modules import record_multi_attempt_feedback, purge_full_clip_and_assets
            record_multi_attempt_feedback(clip_id, winning_attempt_idx=None, total_attempts=MAX_RETRIES, attempt_paths=history)
            purge_res = purge_full_clip_and_assets(
                clip_id=clip_id,
                video_path=sess.get("video_path") if sess else None,
                attempt_history=history
            )
            new_text = (
                f"🗑️ **ALL {MAX_RETRIES} ATTEMPTS MARKED BAD & PURGED.**\n\n"
                f"Deleted video files, audio WAVs, source folder ({purge_res.get('purged_count')} assets), and purged index from pool_metadata.json."
            )
        else:
            try:
                winning_idx = int(choice_str) - 1
            except ValueError:
                winning_idx = 0

            from Core_Modules import record_multi_attempt_feedback
            record_multi_attempt_feedback(clip_id, winning_attempt_idx=winning_idx, total_attempts=MAX_RETRIES, attempt_paths=history)
            winning_path = history[winning_idx] if (winning_idx is not None and winning_idx < len(history)) else (sess.get("video_path") if sess else None)

            if sess and winning_path:
                PublishQueue.add(winning_path, channel_title=sess.get("title", "Viral Reel"), channel_folder=sess.get("creator", "General"))

            new_text = (
                f"🏆 **ATTEMPT {winning_idx + 1} SAVED AS BEST MASTER EDIT!**\n\n"
                f"⭐ Gold pattern weight (1.5x) committed to RAG pool_metadata.json for Attempt {winning_idx + 1}.\n"
                f"Dispatched winning reel to Phase 4 publishing queue!"
            )

        try:
            if query.message.video or query.message.document or query.message.photo:
                await query.edit_message_caption(caption=new_text)
            else:
                await query.edit_message_text(text=new_text)
        except Exception as _p_err:
            logger.warning(f"Attempt pick caption warning: {_p_err}")

    elif data.startswith("ro_"):
        # Format: ro_<type>_<session_id>
        parts = data.split("_", 2)
        opt_type = parts[1]
        session_id = parts[2] if len(parts) > 2 else ""

        preset_directives = {
            "music": "Change Music & Beat Alignment — switch to a faster BGM track and align cuts precisely to audio drops.",
            "shots": "Aggressive Shot Reshaping — force maximum cut frequency, dopamine-spike shot pacing, and rapid speed ramps for intense visual energy.",
            "climax": "Polish Climax & Ending Hook — sharpen the final 5-10 seconds of the video, ensure a high-satisfaction closing transition.",
            "hook": "Fix Intro & Hook (First 3s) — re-sample and emphasize the initial 3 seconds for maximum immediate visual grab."
        }

        if opt_type in preset_directives:
            directive = preset_directives[opt_type]
            await execute_reedit_with_directive(query, context, session_id, directive, chat_id)
        elif opt_type == "custom":
            user_pending_reedit_session[chat_id] = session_id
            await context.bot.send_message(
                chat_id=chat_id,
                text="✏️ **Custom Re-edit Directive Received!**\n\nPlease reply with your specific feedback instructions for Gemini (e.g. *'Make cuts faster during code section and use a cinematic zoom on the face'*):"
            )

    elif data.startswith("reject_"):
        session_id = data.replace("reject_", "").strip()
        sess = session_manager.set_rejected(session_id)
        curr_text = query.message.caption or query.message.text or "Master Reel"
        new_text = f"{curr_text}\n\n🗑️ **REJECTED & DISCARDED BY ADMIN.**\nAll audio, video assets, and metadata pool index purged!"

        try:
            if query.message.video or query.message.document or query.message.photo:
                await query.edit_message_caption(caption=new_text)
            else:
                await query.edit_message_text(text=new_text)
        except Exception:
            pass

        if sess:
            from Core_Modules import purge_full_clip_and_assets
            purge_res = purge_full_clip_and_assets(
                clip_id=sess.get("clip_id"),
                video_path=sess.get("video_path"),
                attempt_history=sess.get("attempt_history", [])
            )
            logger.info(f"🗑️ Purged all assets for rejected session {session_id}: {purge_res.get('purged_count')} items removed")
async def execute_reedit_with_directive(query, context, session_id: str, directive: str, chat_id: int):
    """Executes aggressive re-edit with human directive injected into Gemini Call 3."""
    sess = session_manager.get_session(session_id)
    curr_text = (query.message.caption or query.message.text or "Master Reel") if (query and query.message) else "Master Reel"
    new_text = f"{curr_text}\n\n⚡ **RE-EDITING WITH AGGRESSIVE DIRECTIVE:**\n*\"{directive}\"*\n\nGemini is polishing cuts & filtergraph..."

    try:
        if query and query.message and (query.message.video or query.message.document or query.message.photo):
            await query.edit_message_caption(caption=new_text)
        elif query and query.message:
            await query.edit_message_text(text=new_text)
    except Exception:
        pass

    if sess:
        raw_input = sess.get("raw_video_path")
        clip_id = sess.get("clip_id")
        if not raw_input and clip_id and clip_id != "Processed Shorts":
            possible_raw = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads", clip_id, "video.mp4")
            if os.path.exists(possible_raw):
                raw_input = possible_raw

        target_input = raw_input or sess.get("video_path")

        # 🛡️ Double-Mix Prevention Guard
        if target_input and "_master.mp4" in target_input and not raw_input:
            logger.warning(f"⚠️ [DOUBLE-MIX GUARD] Re-edit target is rendered master '{target_input}' — searching downloads for raw source...")
            bname = os.path.basename(target_input).replace("_master.mp4", "")
            d_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
            if os.path.isdir(d_dir):
                for d in os.listdir(d_dir):
                    if bname in d or d in bname:
                        candidate = os.path.join(d_dir, d, "video.mp4")
                        if os.path.exists(candidate):
                            target_input = candidate
                            logger.info(f"✅ [DOUBLE-MIX GUARD] Recovered raw source video: {target_input}")
                            break

        # ─────────────────────────────────────────────────────────────────────────
        # 📡 VAULT RECOVERY: If local disk is wiped (GitHub Actions runner restart),
        # download raw_video_file_id from Telegram Vault Storage Group to recover the
        # raw source video and run the full pipeline on it again.
        # ─────────────────────────────────────────────────────────────────────────
        if (not target_input or not os.path.exists(str(target_input))) and context and context.bot:
            logger.info(f"📡 [VAULT RECOVERY] Local source missing for session '{session_id}' — attempting Telegram Vault recovery...")
            try:
                # Look up raw_video_file_id from vault index
                vault_entry = (
                    vault_indexer.lookup_processed_reel(session_id=session_id) or
                    vault_indexer.lookup_downloaded_source(social_url=sess.get("social_url", ""))
                )
                raw_fid = (vault_entry or {}).get("raw_video_file_id")
                if raw_fid:
                    recovery_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads", clip_id or f"recovered_{session_id}")
                    os.makedirs(recovery_dir, exist_ok=True)
                    recovery_path = os.path.join(recovery_dir, "video.mp4")
                    logger.info(f"📥 [VAULT RECOVERY] Downloading raw source from Telegram Vault (file_id={raw_fid[:20]}...)...")
                    tg_file = await context.bot.get_file(raw_fid)
                    await tg_file.download_to_drive(custom_path=recovery_path)
                    if os.path.exists(recovery_path) and os.path.getsize(recovery_path) > 1024:
                        target_input = recovery_path
                        logger.info(f"✅ [VAULT RECOVERY SUCCESS] Raw source recovered from Telegram Vault → {recovery_path}")
                        await context.bot.send_message(
                            chat_id=chat_id,
                            text=f"📡 **[VAULT RECOVERY]** Raw source video recovered from Telegram Vault!\nRe-editing now with your directive: *\"{directive}\"*",
                            parse_mode="Markdown"
                        )
                    else:
                        logger.warning(f"⚠️ [VAULT RECOVERY] Downloaded file is too small or missing: {recovery_path}")
                else:
                    logger.warning(f"⚠️ [VAULT RECOVERY] No raw_video_file_id in vault index for session '{session_id}'")
            except Exception as _vr_err:
                logger.error(f"❌ [VAULT RECOVERY] Failed to recover raw source from Telegram Vault: {_vr_err}")

        if not target_input or not os.path.exists(str(target_input)):
            logger.error(f"❌ [RE-EDIT ABORT] Could not locate source video for session '{session_id}' even after Vault Recovery. Aborting.")
            try:
                await context.bot.send_message(chat_id=chat_id, text="❌ **Re-edit failed:** Source video not found on disk or in Telegram Vault. Please submit the URL again to start fresh.")
            except Exception:
                pass
            return

        try:
            run_master_pipeline(
                mode="manual",
                input_path=target_input,
                requestor_chat_id=sess.get("requestor_chat_id") or chat_id,
                user_edit_directive=directive
            )
        except Exception as _re_err:
            logger.error(f"❌ Re-edit execution failed: {_re_err}")


# ── Telegram Command Handlers ─────────────────────────────────────────────────

async def handle_telegram_start(update, context):
    """
    Handles /start command: Welcomes user & shows Platform Selection Keyboard.
    """
    msg = update.message
    if not msg:
        return

    chat_id = msg.chat.id
    user_selected_platform.pop(chat_id, None)
    user_pending_text.pop(chat_id, None)

    keyboard = build_platform_selection_keyboard()
    await msg.reply_text(
        "👋 **Welcome to Master AI Video Factory Bot!**\n\n"
        "🎯 **Choose a target platform below to scrape in bulk**, or send a direct Reel URL / upload a video file:\n"
        "• 📸 **Instagram**: Scrape top reels from creator handle\n"
        "• 🔴 **YouTube**: Scrape Shorts/Videos from channel handle\n"
        "• 🎵 **TikTok**: Scrape top TikTok videos\n"
        "• 🌐 **Direct URL**: Download from any supported site\n\n"
        "👇 **Select your target platform below:**",
        reply_markup=keyboard
    )


async def cmd_ytcode(update, context):
    """
    /ytcode          -> Triggers YouTube auth refresh (sends Google sign-in link to Telegram)
    /ytcode <code>   -> Submits auth code/URL back to complete YouTube OAuth flow
    """
    msg = update.effective_message
    user_id = update.effective_user.id

    if not context.args:
        # Trigger background auth script
        await msg.reply_text(
            "🔄 **Triggering YouTube OAuth Authentication...**\n\n"
            "The Google sign-in link will appear here in a moment.\n"
            "1️⃣ Tap the Google Sign-in link\n"
            "2️⃣ Sign in and copy the entire `http://localhost/?code=...` URL\n"
            "3️⃣ Paste that URL directly into this chat to authorize!",
            parse_mode="Markdown"
        )
        import threading
        import subprocess
        def _run_auth():
            try:
                auth_script = os.path.join(_REPO_ROOT, "scripts", "auth_youtube.py")
                subprocess.run(
                    [sys.executable, auth_script, "--admin-id", str(user_id)],
                    cwd=_REPO_ROOT,
                    timeout=300
                )
            except Exception as _ae:
                logger.error(f"auth_youtube background execution error: {_ae}")
        threading.Thread(target=_run_auth, daemon=True).start()
        return

    # User provided code/URL via args
    raw = " ".join(context.args).strip()
    await process_yt_auth_code_input(msg, raw)


async def process_yt_auth_code_input(msg, raw_text: str):
    """Processes pasted localhost OAuth redirect URL or raw code."""
    code = raw_text.strip()
    if code.startswith("http"):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(code)
        qs = parse_qs(parsed.query)
        extracted = qs.get("code", [None])[0]
        if extracted:
            code = extracted
            await msg.reply_text("✅ **Extracted OAuth code from URL!** Exchanging for YouTube token...")
        else:
            await msg.reply_text("❌ No 'code=' parameter found in that URL. Please paste the entire `http://localhost/?code=...` URL.")
            return
    else:
        await msg.reply_text("✅ **OAuth code received!** Exchanging for YouTube token...")

    try:
        cred_dir = os.path.join(_REPO_ROOT, "Credentials")
        os.makedirs(cred_dir, exist_ok=True)
        code_file = os.path.join(cred_dir, "yt_auth_code.txt")
        with open(code_file, "w", encoding="utf-8") as f:
            f.write(code)
        logger.info(f"🔑 Saved YouTube auth code to {code_file}")
    except Exception as _e:
        await msg.reply_text(f"❌ Failed to save code: {_e}")


# ── Telegram Message & Media Handler ─────────────────────────────────────────

async def handle_telegram_incoming_msg(update, context):
    """
    Handles user messages sent to Telegram bot:
      1. Active Session Title Capture: If user is replying to an approved reel, captures title & dispatches to PublishQueue.
      2. Creator ID / URL / File Upload: Ingests & edits video manually.
    """
    msg = update.message
    if not msg:
        return

    chat_id = msg.chat.id

    # Check if user pasted a localhost OAuth redirect URL or auth code
    if msg.text and ("localhost" in msg.text or "code=" in msg.text) and ("http://" in msg.text or "https://" in msg.text):
        await process_yt_auth_code_input(msg, msg.text.strip())
        return

    # Check if we are waiting for custom re-edit feedback from user
    if chat_id in user_pending_reedit_session and msg.text and not msg.text.startswith("/"):
        session_id = user_pending_reedit_session.pop(chat_id)
        custom_directive = msg.text.strip()
        await msg.reply_text(f"🚀 **Received Custom Directive**: *\"{custom_directive}\"*\n\nStarting aggressive AI re-edit with your feedback...")
        await execute_reedit_with_directive(None, context, session_id, custom_directive, chat_id)
        return

    # Check if we are waiting for a custom title from user
    pending_sess = session_manager.get_pending_title_session()
    if pending_sess and msg.text and not msg.text.startswith("/"):
        custom_title = msg.text.strip()
        sess_id = pending_sess["session_id"]
        updated_sess = session_manager.set_approved_title(sess_id, custom_title)

        if updated_sess:
            v_path = updated_sess["video_path"]
            PublishQueue.add(v_path, channel_title=custom_title, channel_folder=updated_sess.get("creator", "General"))
            logger.info(f"🚀 Title captured for session {sess_id}: '{custom_title}'. Triggering Phase 4 Broadcasting...")

            await msg.reply_text(
                f"🚀 **Title Saved!** Starting 4-Platform Broadcasting...\n\n"
                f"📌 **Title**: `{custom_title}`\n"
                f"📁 **Reel**: `{os.path.basename(v_path)}`"
            )

            try:
                from Publishing_Modules.media_publisher_main import run_phase4_publishing
                pub_res = run_phase4_publishing(
                    video_path=v_path,
                    title=custom_title,
                    tags="#viral #shorts #trending",
                    niche=updated_sess.get("creator", "General")
                )

                status_lines = []
                for p_name, p_info in pub_res.get("platforms", {}).items():
                    st = p_info.get("status")
                    icon = "✅" if st == "success" else ("⏸️" if st == "skipped" else "❌")
                    detail = p_info.get("url") or p_info.get("link") or p_info.get("message") or st
                    status_lines.append(f"• {icon} **{p_name.upper()}**: `{detail}`")

                await msg.reply_text(
                    f"🎉 **Phase 4 Multi-Platform Broadcasting Complete!**\n\n"
                    f"📌 **Title**: `{custom_title}`\n\n"
                    + "\n".join(status_lines)
                )
            except Exception as pub_err:
                logger.error(f"❌ Phase 4 publishing error: {pub_err}")
                await msg.reply_text(f"⚠️ Multi-platform broadcast warning: `{pub_err}`")
            return

    target_url = None
    local_video_path = None
    target_accs = None

    # Determine active platform choice (check if user explicitly clicked a platform button)
    has_platform_choice = chat_id in user_selected_platform
    chosen_platform = user_selected_platform.pop(chat_id, "instagram")

    GREETINGS = {"hello", "hi", "hey", "test", "help", "bot", "start", "menu", "status", "yo", "hola"}

    if msg.text:
        text = msg.text.strip()

        if text.startswith("/start") or text.startswith("/help") or text.startswith("/mode"):
            await handle_telegram_start(update, context)
            return

        elif text.startswith("http://") or text.startswith("https://") or "instagram.com" in text or "youtube.com" in text or "youtu.be" in text or "tiktok.com" in text:
            target_url = text
            await msg.reply_text(
                f"📥 **[STEP 1/3] Direct Video URL Received!**\n\n"
                f"🔗 **Target URL**: `{target_url}`\n"
                f"🌐 **Platform**: `{chosen_platform.title()}`\n"
                f"⚙️ **Status**: Ingesting video & starting AI Master Editor..."
            )
            # Execute pipeline immediately for URL input
            try:
                results = run_master_pipeline(
                    mode="manual",
                    url=target_url,
                    platform=chosen_platform,
                    requestor_chat_id=chat_id
                )
            except Exception as _url_err:
                logger.error(f"❌ URL pipeline execution failed: {_url_err}")
            return

        elif text.startswith("@") or text.lower().startswith("scrape:") or text.lower().startswith("account:"):
            clean_handle = text.replace("scrape:", "").replace("account:", "").strip().lstrip("@")
            target_accs = [clean_handle]
            await msg.reply_text(
                f"🎯 **[STEP 1/3] Target Creator Handle Received!**\n\n"
                f"👤 **Creator**: `@{clean_handle}`\n"
                f"🌐 **Platform**: `{chosen_platform.title()}`\n"
                f"⚙️ **Status**: Scraping top reels & launching AI editing pipeline... Please wait!"
            )
            # Execute pipeline immediately for account scraping
            try:
                results = run_master_pipeline(
                    mode="auto",
                    target_accounts=target_accs,
                    platform=chosen_platform,
                    requestor_chat_id=chat_id
                )
            except Exception as _acc_err:
                logger.error(f"❌ Account pipeline execution failed: {_acc_err}")
            return

        elif has_platform_choice:
            clean_handle = text.strip().lstrip("@")
            target_accs = [clean_handle]
            await msg.reply_text(
                f"🎯 **[STEP 1/3] Target Creator Handle Received!**\n\n"
                f"👤 **Creator**: `@{clean_handle}`\n"
                f"🌐 **Platform**: `{chosen_platform.title()}`\n"
                f"⚙️ **Status**: Scraping top reels for {chosen_platform.title()} & launching AI pipeline..."
            )
            # Execute pipeline immediately for platform-specific handle
            try:
                results = run_master_pipeline(
                    mode="auto",
                    target_accounts=target_accs,
                    platform=chosen_platform,
                    requestor_chat_id=chat_id
                )
            except Exception as _plat_err:
                logger.error(f"❌ Platform pipeline execution failed: {_plat_err}")
            return

        else:
            clean_id = text.strip().lstrip("@")
            user_pending_text[chat_id] = clean_id
            keyboard = build_platform_selection_keyboard()
            await msg.reply_text(
                f"🎯 **Target ID Received**: `@{clean_id}`\n\n"
                f"👇 **Please select which platform `@{clean_id}` belongs to:**",
                reply_markup=keyboard
            )
            return

    elif msg.video or msg.document:
        await msg.reply_text(
            f"📥 **[STEP 1/3] Video File Upload Received!**\n\n"
            f"📁 **File**: Saved successfully\n"
            f"⚙️ **Status**: Launching AI Master Editing Pipeline..."
        )
        file_obj = await (msg.video or msg.document).get_file()
        temp_dir = os.path.join(_REPO_ROOT, "downloads", f"telegram_{chat_id}_{int(time.time())}")
        os.makedirs(temp_dir, exist_ok=True)
        local_video_path = os.path.join(temp_dir, "video.mp4")
        await file_obj.download_to_drive(custom_path=local_video_path)
        # Execute pipeline immediately for video file upload
        try:
            results = run_master_pipeline(
                mode="manual",
                input_path=local_video_path,
                platform=chosen_platform,
                requestor_chat_id=chat_id
            )
        except Exception as _upload_err:
            logger.error(f"❌ Video upload pipeline execution failed: {_upload_err}")
        return

    # Fallback: No valid input detected
    await msg.reply_text(
        "⚠️ **Invalid Input**\n\n"
        "Please send:\n"
        "• A video URL (Instagram, YouTube, TikTok)\n"
        "• A creator handle (e.g., @username)\n"
        "• Upload a video file directly"
    )


# ── Full End-to-End Execution Pipeline ───────────────────────────────────────

def run_master_pipeline(
    mode: str = "auto",
    url: Optional[str] = None,
    input_path: Optional[str] = None,
    target_accounts: Optional[List[str]] = None,
    platform: str = "instagram",
    requestor_chat_id: Optional[int] = None,
    user_edit_directive: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes End-to-End Master Pipeline across all 4 Phases.
    Supports URL inputs, local file paths, or target account list.
    """
    logger.info("==================================================================")
    logger.info("🚀 [MASTER PIPELINE] Starting End-to-End Master Execution Cycle")
    logger.info("==================================================================")

    rendered_master_reels = []

    target_clip_dirs = None
    # Phase 1: Ingestion (when mode == 'auto', or when URL/target_accounts provided)
    if mode == "auto" or url or target_accounts:
        logger.info(f"📥 [PHASE 1] Running Content Ingestion for target: {target_accounts or url or 'auto-pool'} (platform='{platform}')...")
        ingest_res = run_phase1_ingestion(mode=mode, url=url, limit_per_account=3, target_accounts=target_accounts, platform=platform)
        if not ingest_res.get("success") and not input_path:
            logger.warning("⚠️ [MASTER PIPELINE] Ingestion completed with no new clips to process.")
            return {"success": False, "rendered_files": []}
        
        dl_files = ingest_res.get("downloaded_files", [])
        if dl_files:
            target_clip_dirs = list(set(os.path.dirname(f) for f in dl_files if os.path.exists(f)))
            logger.info(f"   🎯 Targeted ingestion isolated {len(target_clip_dirs)} folder(s): {[os.path.basename(d) for d in target_clip_dirs]}")

    # Phase 2 & 3: Master AI Perception & Render Orchestrator
    try:
        from Main_Modules.phase2_main import run_phase2_orchestration

        # ── Scalable Dynamic Multi-User Isolation ─────────────────────────────
        # Every Telegram user (User A, User B, User N) gets their rendered reel
        # delivered dynamically to their own chat window.
        # CLI/scheduled runs without a requestor_chat_id remain local (no spam).
        target_chat = requestor_chat_id
        bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

        def _on_clip_rendered(reel_path: str):
            """Immediately delivers each rendered clip to the requesting Telegram user."""
            PublishQueue.add(reel_path, channel_title="General", channel_folder="General")
            logger.info(f"🚀 [PHASE 4] Dispatched reel '{os.path.basename(reel_path)}' to publish queue.")
            if target_chat:
                session_manager.record_rendered_attempt(target_chat, reel_path)

            if bot_token and target_chat:
                try:
                    import asyncio
                    from telegram import Bot
                    from telegram.request import HTTPXRequest

                    async def _send_single():
                        storage_group = os.getenv("TELEGRAM_STORAGE_GROUP_ID") or os.getenv("TELEGRAM_CHAT_ID")
                        req = HTTPXRequest(
                            connection_pool_size=16,
                            read_timeout=600.0,
                            write_timeout=600.0,
                            connect_timeout=120.0,
                            pool_timeout=120.0
                        )
                        bot = Bot(token=bot_token, request=req)
                        active_reel_path = reel_path
                        real_cid = os.path.basename(active_reel_path).replace("_master.mp4", "")
                        possible_raw = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads", real_cid, "video.mp4")

                        # ── PHASE 2.1 WATERMARK GATE (bypass if inpainting occurred upfront) ──
                        watermark_output = os.path.splitext(active_reel_path)[0] + "_wm_cleaned.mp4"
                        _inpainted_upfront = False

                        try:
                            from Gemini_Modules.clip_intelligence_store import ClipIntelligenceStore
                            _store = ClipIntelligenceStore()
                            _intel_d = _store.load(real_cid)
                            if _intel_d:
                                _inpainted_upfront = bool(
                                    _intel_d.get("forensic", {}).get("inpainted_upfront") or
                                    _intel_d.get("output", {}).get("mode") == "SINGLE_PASS" or
                                    _intel_d.get("output", {}).get("status") == "SUCCESS" or
                                    _intel_d.get("editing_plan")
                                )
                        except Exception as _ce:
                            logger.debug(f"[PHASE 2.1] Store lookup note: {_ce}")

                        if not _inpainted_upfront:
                            # Fallback to direct path inspection
                            _possible_intel_paths = [
                                os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads", real_cid, ".clip_intelligence.json"),
                                os.path.join(os.path.dirname(active_reel_path), ".clip_intelligence.json"),
                                os.path.join(os.path.dirname(active_reel_path).replace("Processed Shorts", "downloads"), real_cid, ".clip_intelligence.json")
                            ]
                            for intel_file in _possible_intel_paths:
                                if os.path.exists(intel_file):
                                    try:
                                        with open(intel_file, "r", encoding="utf-8") as _f:
                                            _id_data = json.load(_f)
                                        _inpainted_upfront = bool(
                                            _id_data.get("forensic", {}).get("inpainted_upfront") or
                                            _id_data.get("output", {}).get("mode") == "SINGLE_PASS" or
                                            _id_data.get("editing_plan")
                                        )
                                        break
                                    except Exception:
                                        continue

                        # Master reels (_master.mp4) rendered via Phase 2 single pass are already clean
                        if "_master.mp4" in os.path.basename(active_reel_path):
                            _inpainted_upfront = True

                        if _inpainted_upfront:
                            logger.info(f"✅ [PHASE 2.1] Watermark handled UPFRONT in Phase 2 — skipping post-render inpainting gate for {os.path.basename(active_reel_path)}.")
                        else:
                            try:
                                from Watermark_and_Inpainting.watermark_main import run_watermark_removal
                                logger.info(f"🧼 [PHASE 2.1] Running watermark cleanup on rendered master before Telegram delivery: {os.path.basename(active_reel_path)}")
                                cleaned_video_path, watermark_log = run_watermark_removal(
                                    input_path=active_reel_path,
                                    output_path=watermark_output,
                                    keywords="",
                                    retry_level=0,
                                    video_path=active_reel_path
                                )
                                if cleaned_video_path and os.path.exists(cleaned_video_path):
                                    active_reel_path = cleaned_video_path
                                    logger.info(f"✅ [PHASE 2.1] Watermark gate completed. Telegram payload now uses: {os.path.basename(active_reel_path)}")
                            except Exception as _wm_err:
                                logger.warning(f"⚠️ [PHASE 2.1] Watermark gate failed, continuing with original render: {_wm_err}")


                        sess_id = session_manager.create_session(
                            video_path=active_reel_path,
                            clip_id=real_cid,
                            raw_video_path=possible_raw if os.path.exists(possible_raw) else None,
                            requestor_chat_id=requestor_chat_id
                        )
                        keyboard = build_telegram_session_keyboard(session_id=sess_id)
                        with open(active_reel_path, "rb") as vf:
                            sent_msg = await bot.send_video(
                                chat_id=int(target_chat),
                                video=vf,
                                caption=f"🎉 **AI Master Edit Complete!**\n📁 `{os.path.basename(active_reel_path)}`\n🆔 `Session: {sess_id}`",
                                reply_markup=keyboard
                            )
                            if sent_msg:
                                session_manager.update_message_id(sess_id, sent_msg.message_id)

                        # Storage Group Backup & Master Vault Index Sync
                        if storage_group:
                            try:
                                master_file_id = sent_msg.video.file_id if sent_msg and sent_msg.video else None
                                if str(target_chat) != str(storage_group):
                                    with open(active_reel_path, "rb") as svf:
                                        sg_msg = await bot.send_video(
                                            chat_id=int(storage_group),
                                            video=svf,
                                            caption=f"📦 **[VAULT BACKUP]** Master Reel Backup\n📁 `{os.path.basename(active_reel_path)}`\n🆔 `Session: {sess_id}`"
                                        )
                                        if sg_msg and sg_msg.video:
                                            master_file_id = sg_msg.video.file_id

                                # Load clip intelligence and lyric intelligence from disk
                                clip_intel = {}
                                lyric_intel = {}
                                beat_math = {}
                                base_dir = os.path.dirname(os.path.abspath(__file__))
                                
                                intel_file = os.path.join(base_dir, "downloads", real_cid, ".clip_intelligence.json")
                                if os.path.exists(intel_file):
                                    try:
                                        with open(intel_file, "r", encoding="utf-8") as f:
                                            clip_intel = json.load(f)
                                    except Exception: pass

                                beats_file = os.path.join(base_dir, "Original_audio", "beats", f"{real_cid}_lyric.json")
                                if os.path.exists(beats_file):
                                    try:
                                        with open(beats_file, "r", encoding="utf-8") as f:
                                            lyric_intel = json.load(f)
                                    except Exception: pass

                                audio_analysis_file = os.path.join(base_dir, "downloads", real_cid, "audio_analysis.json")
                                if os.path.exists(audio_analysis_file):
                                    try:
                                        with open(audio_analysis_file, "r", encoding="utf-8") as f:
                                            beat_math = json.load(f)
                                    except Exception: pass

                                possible_audio = os.path.join(base_dir, "downloads", real_cid, "video_extracted.wav")
                                if not os.path.exists(possible_audio):
                                    clip_dir_path = os.path.join(base_dir, "downloads", real_cid)
                                    if os.path.exists(clip_dir_path):
                                        for f_item in os.listdir(clip_dir_path):
                                            if f_item.endswith(".wav") or f_item.endswith(".mp3") or f_item.endswith(".m4a"):
                                                possible_audio = os.path.join(clip_dir_path, f_item)
                                                break

                                social_link = url or f"https://instagram.com/reel/{real_cid}"

                                # 1. Record Column 2 Source Download entry & Upload Raw Source + Audio to Vault
                                await vault_indexer.record_downloaded_source(
                                    bot=bot,
                                    social_url=social_link,
                                    session_id=sess_id,
                                    raw_video_path=possible_raw if os.path.exists(possible_raw) else None,
                                    audio_path=possible_audio if os.path.exists(possible_audio) else None,
                                    beat_math=beat_math,
                                    pin_now=False
                                )

                                # 2. Record Column 1 Master Reel entry with full intel and pin index
                                await vault_indexer.record_processed_reel(
                                    bot=bot,
                                    session_id=sess_id,
                                    social_url=social_link,
                                    custom_title=None,
                                    master_video_path=active_reel_path,
                                    clip_intel=clip_intel,
                                    lyric_intel=lyric_intel,
                                    master_file_id=master_file_id,
                                )
                            except Exception as _sg_e:
                                if "Chat not found" in str(_sg_e) or "chat not found" in str(_sg_e).lower():
                                    logger.warning(f"⚠️ Vault storage group backup skipped: Storage group chat not found. Check TELEGRAM_STORAGE_GROUP_ID in .env")
                                else:
                                    logger.warning(f"⚠️ Vault storage group backup warning: {_sg_e}")

                    import threading

                    def _run_in_thread():
                        asyncio.run(_send_single())

                    t = threading.Thread(target=_run_in_thread, daemon=True)
                    t.start()
                    t.join(timeout=1200.0)

                    logger.info(f"📲 [REALTIME TELEGRAM DELIVERY] Delivered '{os.path.basename(reel_path)}' directly to Telegram!")
                except Exception as _deliv_err:
                    logger.error(f"❌ Realtime Telegram delivery failed for {os.path.basename(reel_path)}: {_deliv_err}")

        phase2_res = run_phase2_orchestration(
            input_path=input_path,
            target_dirs=target_clip_dirs,
            on_rendered_callback=_on_clip_rendered,
            user_edit_directive=user_edit_directive
        )
        rendered_master_reels = phase2_res.get("rendered_files", [])
        logger.info(f"🎬 [PHASE 2 & 3 COMPLETE] {len(rendered_master_reels)} master reel(s) ready.")

    except Exception as p2_err:
        logger.error(f"❌ [MASTER PIPELINE FAILED] Phase 2 error: {p2_err}")

    return {"success": len(rendered_master_reels) > 0, "rendered_files": rendered_master_reels}


# ── Dual Pipeline Schedulers (Scraping vs Publishing) ────────────────────────

def parse_scraping_auto_input_times() -> List[str]:
    """
    Parses SCRAPING_AUTO_INPUT_TIMES from .env (e.g., '07:00,12:00,19:00').
    Defaults to ['07:00', '12:00', '19:00'].
    """
    raw = os.getenv("SCRAPING_AUTO_INPUT_TIMES", "07:00,12:00,19:00")
    slots = [s.strip() for s in raw.split(",") if ":" in s.strip()]
    return slots or ["07:00", "12:00", "19:00"]


def parse_static_publish_times() -> List[str]:
    """
    Parses PUBLISH_STATIC_TIMES from .env (e.g., '07:30,12:30,19:30').
    Defaults to ['07:30', '12:30', '19:30'].
    """
    raw = os.getenv("PUBLISH_STATIC_TIMES", "07:30,12:30,19:30")
    slots = [s.strip() for s in raw.split(",") if ":" in s.strip()]
    return slots or ["07:30", "12:30", "19:30"]


def get_seconds_until_next_slot(slots: List[str]) -> tuple[str, float]:
    """
    Calculates the next target time slot and seconds remaining until it fires.
    """
    import datetime
    now = datetime.datetime.now()
    today_date = now.date()

    candidates = []
    for slot_str in slots:
        try:
            h, m = map(int, slot_str.split(":"))
            slot_dt = datetime.datetime.combine(today_date, datetime.time(hour=h, minute=m))
            if slot_dt <= now:
                slot_dt += datetime.timedelta(days=1)
            candidates.append((slot_str, slot_dt))
        except Exception:
            pass

    if not candidates:
        return ("12:00", 3600.0)

    candidates.sort(key=lambda x: x[1])
    next_slot, next_dt = candidates[0]
    delay_s = max(1.0, (next_dt - now).total_seconds())
    return (next_slot, delay_s)


def run_scheduled_pipeline_loop():
    """
    Blocking CLI Loop for Static Time Scheduler.
    Rotates max 2 source accounts and runs master pipeline automatically at each configured slot.
    """
    slots = parse_scraping_auto_input_times()
    logger.info("==================================================================")
    logger.info(f"⏰ [SCRAPING SCHEDULER] Active auto-input slots: {slots}")
    logger.info("==================================================================")

    while True:
        next_slot, delay_s = get_seconds_until_next_slot(slots)
        hours_left = delay_s / 3600.0
        logger.info(f"⏳ [SCHEDULER] Next scheduled run at {next_slot} (in {hours_left:.2f} hours / {delay_s:.0f}s)...")
        time.sleep(delay_s)

        logger.info(f"⏰ [SCHEDULER] Trigger time reached ({next_slot})! Executing max 2-account scraper batch...")
        try:
            rendered = run_scheduled_scraper_batch(max_accounts=2)
            logger.info(f"✅ [SCHEDULER] Completed batch run: {len(rendered)} reel(s) rendered.")
        except Exception as e:
            logger.error(f"❌ [SCHEDULER] Pipeline execution error: {e}")


async def _async_static_scheduler_task(bot_app=None):
    """
    Async background task running alongside Telegram Bot polling.
    Rotates max 2 accounts per scheduled slot, renders reels, creates sessions, and sends to Telegram.
    """
    import asyncio
    slots = parse_scraping_auto_input_times()
    logger.info(f"⏰ [ASYNC SCRAPER SCHEDULER] Scraping auto-input times active: {slots}")

    while True:
        next_slot, delay_s = get_seconds_until_next_slot(slots)
        hours_left = delay_s / 3600.0
        logger.info(f"⏳ [ASYNC SCHEDULER] Next run scheduled at {next_slot} (in {hours_left:.2f} hours)...")
        await asyncio.sleep(delay_s)

        logger.info(f"⏰ [ASYNC SCHEDULER] Trigger time reached ({next_slot})! Starting 2-account ingestion & AI edit cycle...")
        try:
            rendered = run_scheduled_scraper_batch(max_accounts=2)
            if bot_app and rendered:
                admin_id = os.getenv("TELEGRAM_CHAT_ID")
                if admin_id:
                    for r_file in rendered:
                        try:
                            sess_id = session_manager.create_session(video_path=r_file)
                            keyboard = build_telegram_session_keyboard(session_id=sess_id)
                            with open(r_file, "rb") as vf:
                                sent_msg = await bot_app.bot.send_video(
                                    chat_id=int(admin_id),
                                    video=vf,
                                    caption=(
                                        f"⏰ **[SCHEDULED SLOT {next_slot}]** Master Edit Complete!\n"
                                        f"📁 `{os.path.basename(r_file)}`\n"
                                        f"🆔 `Session: {sess_id}`"
                                    ),
                                    reply_markup=keyboard
                                )
                                if sent_msg:
                                    session_manager.update_message_id(sess_id, sent_msg.message_id)
                        except Exception as _e:
                            logger.warning(f"Failed to send scheduled video to Telegram admin: {_e}")
        except Exception as e:
            logger.error(f"❌ [ASYNC SCHEDULER] Error during scheduled run: {e}")


def start_telegram_bot_service():
    """
    Launches continuous Telegram Bot Polling Listener.
    Waits for user input on Telegram (URL, video upload, or target account ID).
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token.startswith("your_"):
        logger.error("❌ TELEGRAM_BOT_TOKEN environment variable is missing or unconfigured in .env!")
        return

    try:
        from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters
        from telegram.request import HTTPXRequest

        logger.info("🤖 [TELEGRAM BOT] Starting Silent Long-Polling Telegram Listener...")

        request = HTTPXRequest(
            connection_pool_size=8,
            read_timeout=300.0,
            write_timeout=300.0,
            connect_timeout=30.0
        )

        async def _on_startup(application):
            try:
                # Hydrate all vault JSON databases (master index, users, audio pool) from Telegram Storage Group
                logger.info("📦 [VAULT CLOUD HYDRATION] Hydrating vault index, user sessions, and pool metadata from Telegram...")
                vault_indexer.hydrate_all_vault_jsons_on_startup()
                await vault_indexer.sync_vault_index_from_telegram(application.bot)

                bot_user = await application.bot.get_me()
                bot_id = str(bot_user.id)
                admin_id = os.getenv("TELEGRAM_CHAT_ID") or os.getenv("TELEGRAM_ADMIN_ID")
                if admin_id and str(admin_id).strip() != bot_id:
                    try:
                        keyboard = build_platform_selection_keyboard()
                        await application.bot.send_message(
                            chat_id=int(admin_id),
                            text=(
                                "🚀 **Master AI Video Factory Bot Active!**\n\n"
                                "🎯 **Select a platform below to begin bulk scraping & editing**, or send a creator handle / video link:\n"
                                "• 📸 **Instagram**: `@indiancelebspot`\n"
                                "• 🔴 **YouTube**: `@ChannelName`\n"
                                "• 🎵 **TikTok**: `@tiktokuser`\n"
                                "• 🌐 **Direct URL / File**: Paste link or upload video\n\n"
                                "👇 **Select your target platform below:**"
                            ),
                            reply_markup=keyboard
                        )
                        logger.info(f"📲 Automatically pushed Platform Selection Menu to Telegram Chat ID: {admin_id}")
                    except Exception as _st_err:
                        error_str = str(_st_err)
                        if "can't send messages to the bot" in error_str.lower() or "bot can't initiate" in error_str.lower():
                            logger.info("ℹ️ Startup push skipped: TELEGRAM_CHAT_ID is set to bot ID or user has not sent /start yet.")
                        elif "Chat not found" in error_str or "chat not found" in error_str.lower():
                            logger.warning(f"⚠️ Startup welcome push warning: Admin chat ID {admin_id} not found. Bot may not have access to this chat, or the ID is incorrect.")
                        else:
                            logger.warning(f"⚠️ Startup welcome push warning: {_st_err}")
            except Exception as _init_err:
                logger.debug(f"Startup check exception: {_init_err}")

        app = ApplicationBuilder().token(token).request(request).post_init(_on_startup).build()
        app.add_handler(CommandHandler("start", handle_telegram_start))
        app.add_handler(CommandHandler("ytcode", cmd_ytcode))
        app.add_handler(CallbackQueryHandler(handle_telegram_callback))
        app.add_handler(MessageHandler(filters.TEXT | filters.VIDEO | filters.Document.ALL, handle_telegram_incoming_msg))

        logger.info("✅ Telegram Bot Active & Listening! Platform Selection Menu dispatched to admin chat.")
        app.run_polling(poll_interval=2.0, drop_pending_updates=False)
    except KeyboardInterrupt:
        logger.info("\n🛑 [SHUTDOWN] Ctrl+C / KeyboardInterrupt received. Telegram Bot stopped gracefully.")
        sys.exit(0)
    except Exception as bot_err:
        logger.error(f"❌ Failed to start Telegram bot polling: {bot_err}")


# ── CLI Entrypoint ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description="Master AI Video Factory Orchestrator & Telegram Bot")
        parser.add_argument("input", type=str, nargs="?", default=None, help="Target video URL, local .mp4 file, or clip folder")
        parser.add_argument("--mode", type=str, choices=["auto", "manual"], default=None, help="Ingestion mode ('auto' or 'manual')")
        parser.add_argument("--url", "-u", type=str, default=None, help="Target video URL for manual ingestion")
        parser.add_argument("--target-accounts", "-t", type=str, default=None, help="Target Instagram handle(s) to scrape (comma-separated, max 2)")
        parser.add_argument("--bot", action="store_true", help="Launch Telegram Bot polling listener mode + timed auto-input scheduler")

        args = parser.parse_args()

        # Launch bot if --bot is explicitly passed OR if no input/url/target/mode is specified
        if args.bot or (not args.input and not args.url and not args.target_accounts and not args.mode):
            start_telegram_bot_service()
        else:
            target_input = args.input or args.url
            target_url = None
            target_file = None
            target_accs = None

            if args.target_accounts:
                target_accs = [a.strip() for a in args.target_accounts.split(",") if a.strip()][:2]
            elif target_input:
                clean_in = target_input.strip().strip("'").strip('"')
                if clean_in.startswith("http://") or clean_in.startswith("https://") or "instagram.com" in clean_in:
                    target_url = clean_in
                elif os.path.exists(clean_in):
                    target_file = clean_in
                else:
                    # Treat positional input argument as target Instagram handle (e.g., python main.py indiancelebspot)
                    target_accs = [clean_in.lstrip("@")]

            mode_to_use = args.mode or ("manual" if (target_url or target_file) else "auto")
            run_master_pipeline(mode=mode_to_use, url=target_url, input_path=target_file, target_accounts=target_accs)

    except KeyboardInterrupt:
        logger.info("\n🛑 [SHUTDOWN] Ctrl+C / KeyboardInterrupt received. System stopped gracefully.")
        sys.exit(0)
