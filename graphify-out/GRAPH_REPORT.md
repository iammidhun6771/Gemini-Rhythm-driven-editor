# Graph Report - D:\AMTCE  (2026-08-14)

## Corpus Check
- 110 files · ~257,878 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1432 nodes · 3027 edges · 90 communities detected
- Extraction: 58% EXTRACTED · 42% INFERRED · 0% AMBIGUOUS · INFERRED: 1263 edges (avg confidence: 0.65)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Community 0|Community 0]]
- [[_COMMUNITY_Community 1|Community 1]]
- [[_COMMUNITY_Community 2|Community 2]]
- [[_COMMUNITY_Community 3|Community 3]]
- [[_COMMUNITY_Community 4|Community 4]]
- [[_COMMUNITY_Community 5|Community 5]]
- [[_COMMUNITY_Community 6|Community 6]]
- [[_COMMUNITY_Community 7|Community 7]]
- [[_COMMUNITY_Community 8|Community 8]]
- [[_COMMUNITY_Community 9|Community 9]]
- [[_COMMUNITY_Community 10|Community 10]]
- [[_COMMUNITY_Community 11|Community 11]]
- [[_COMMUNITY_Community 12|Community 12]]
- [[_COMMUNITY_Community 13|Community 13]]
- [[_COMMUNITY_Community 14|Community 14]]
- [[_COMMUNITY_Community 15|Community 15]]
- [[_COMMUNITY_Community 16|Community 16]]
- [[_COMMUNITY_Community 17|Community 17]]
- [[_COMMUNITY_Community 18|Community 18]]
- [[_COMMUNITY_Community 19|Community 19]]
- [[_COMMUNITY_Community 20|Community 20]]
- [[_COMMUNITY_Community 21|Community 21]]
- [[_COMMUNITY_Community 22|Community 22]]
- [[_COMMUNITY_Community 23|Community 23]]
- [[_COMMUNITY_Community 24|Community 24]]
- [[_COMMUNITY_Community 25|Community 25]]
- [[_COMMUNITY_Community 26|Community 26]]
- [[_COMMUNITY_Community 27|Community 27]]
- [[_COMMUNITY_Community 28|Community 28]]
- [[_COMMUNITY_Community 29|Community 29]]
- [[_COMMUNITY_Community 30|Community 30]]
- [[_COMMUNITY_Community 31|Community 31]]
- [[_COMMUNITY_Community 32|Community 32]]
- [[_COMMUNITY_Community 33|Community 33]]
- [[_COMMUNITY_Community 34|Community 34]]
- [[_COMMUNITY_Community 35|Community 35]]
- [[_COMMUNITY_Community 36|Community 36]]
- [[_COMMUNITY_Community 37|Community 37]]
- [[_COMMUNITY_Community 38|Community 38]]
- [[_COMMUNITY_Community 39|Community 39]]
- [[_COMMUNITY_Community 40|Community 40]]
- [[_COMMUNITY_Community 41|Community 41]]
- [[_COMMUNITY_Community 42|Community 42]]
- [[_COMMUNITY_Community 43|Community 43]]
- [[_COMMUNITY_Community 44|Community 44]]
- [[_COMMUNITY_Community 45|Community 45]]
- [[_COMMUNITY_Community 46|Community 46]]
- [[_COMMUNITY_Community 47|Community 47]]
- [[_COMMUNITY_Community 48|Community 48]]
- [[_COMMUNITY_Community 49|Community 49]]
- [[_COMMUNITY_Community 50|Community 50]]
- [[_COMMUNITY_Community 51|Community 51]]
- [[_COMMUNITY_Community 52|Community 52]]
- [[_COMMUNITY_Community 53|Community 53]]
- [[_COMMUNITY_Community 54|Community 54]]
- [[_COMMUNITY_Community 55|Community 55]]
- [[_COMMUNITY_Community 56|Community 56]]
- [[_COMMUNITY_Community 57|Community 57]]
- [[_COMMUNITY_Community 58|Community 58]]
- [[_COMMUNITY_Community 59|Community 59]]
- [[_COMMUNITY_Community 60|Community 60]]
- [[_COMMUNITY_Community 61|Community 61]]
- [[_COMMUNITY_Community 62|Community 62]]
- [[_COMMUNITY_Community 63|Community 63]]
- [[_COMMUNITY_Community 64|Community 64]]
- [[_COMMUNITY_Community 65|Community 65]]
- [[_COMMUNITY_Community 66|Community 66]]
- [[_COMMUNITY_Community 67|Community 67]]
- [[_COMMUNITY_Community 68|Community 68]]
- [[_COMMUNITY_Community 69|Community 69]]
- [[_COMMUNITY_Community 70|Community 70]]
- [[_COMMUNITY_Community 71|Community 71]]
- [[_COMMUNITY_Community 72|Community 72]]
- [[_COMMUNITY_Community 73|Community 73]]
- [[_COMMUNITY_Community 74|Community 74]]
- [[_COMMUNITY_Community 75|Community 75]]
- [[_COMMUNITY_Community 76|Community 76]]
- [[_COMMUNITY_Community 77|Community 77]]
- [[_COMMUNITY_Community 78|Community 78]]
- [[_COMMUNITY_Community 79|Community 79]]
- [[_COMMUNITY_Community 80|Community 80]]
- [[_COMMUNITY_Community 81|Community 81]]
- [[_COMMUNITY_Community 82|Community 82]]
- [[_COMMUNITY_Community 83|Community 83]]
- [[_COMMUNITY_Community 84|Community 84]]
- [[_COMMUNITY_Community 85|Community 85]]
- [[_COMMUNITY_Community 86|Community 86]]
- [[_COMMUNITY_Community 87|Community 87]]
- [[_COMMUNITY_Community 88|Community 88]]
- [[_COMMUNITY_Community 89|Community 89]]

## God Nodes (most connected - your core abstractions)
1. `get()` - 254 edges
2. `ClipIntelligenceStore` - 132 edges
3. `BeatEngine` - 128 edges
4. `AudioPoolManager` - 119 edges
5. `TelegramVaultIndexer` - 101 edges
6. `PublishQueue` - 48 edges
7. `MasterAIEditor` - 41 edges
8. `GeminiGovernor` - 40 edges
9. `ImportGate` - 34 edges
10. `GeminiFFmpegEngine` - 29 edges

## Surprising Connections (you probably didn't know these)
- `audio_extractor.py — Phase 1 Audio Extraction + Beat Analysis ==================` --uses--> `AudioPoolManager`  [INFERRED]
  D:\AMTCE\Audio_Modules\audio_extractor.py → D:\AMTCE\Audio_Modules\audio_pool_manager.py
- `Returns True if the file has at least one audio stream (fast ffprobe check).` --uses--> `AudioPoolManager`  [INFERRED]
  D:\AMTCE\Audio_Modules\audio_extractor.py → D:\AMTCE\Audio_Modules\audio_pool_manager.py
- `Extracts mono 16 kHz PCM WAV from video_path → output_path.     Returns True on` --uses--> `AudioPoolManager`  [INFERRED]
  D:\AMTCE\Audio_Modules\audio_extractor.py → D:\AMTCE\Audio_Modules\audio_pool_manager.py
- `Phase 1 post-download hook. Called immediately after video.mp4 is saved.      St` --uses--> `AudioPoolManager`  [INFERRED]
  D:\AMTCE\Audio_Modules\audio_extractor.py → D:\AMTCE\Audio_Modules\audio_pool_manager.py
- `Ingests clean musical audio extracted from a Phase 1 clip into the central     O` --uses--> `AudioPoolManager`  [INFERRED]
  D:\AMTCE\Audio_Modules\audio_extractor.py → D:\AMTCE\Audio_Modules\audio_pool_manager.py

## Communities

### Community 0 - "Community 0"
Cohesion: 0.02
Nodes (114): harvest_reels_from_apify(), 03_apify_harvester.py — Phase 1 Step 3: Apify Reel Scraper & Pre-screener ======, Step 3 Execution: Scrapes target reels via Apify actor., gemini_reel_prescreen(), Pre-screens a reel using its thumbnail JPEG from Apify's displayUrl field., get_user_id_from_chat(), handle_account_selection_callback(), integrate_with_approval_workflow() (+106 more)

### Community 1 - "Community 1"
Cohesion: 0.02
Nodes (109): Phase_2 / 02_forensic_perception.py ==================================== Step 2:, Executes Gemini Call 1.     Returns result dictionary containing visual_context,, run_forensic_perception(), Phase 1 post-download hook. Called immediately after video.mp4 is saved.      St, run_phase1_audio_analysis(), Analyze beats on the BGM (preferred) or extracted WAV (fallback).          What, analyze_beats_with_drops(), BeatEngine (+101 more)

### Community 2 - "Community 2"
Cohesion: 0.03
Nodes (107): ingest_to_publish_queue(), Phase 3 — Step 01: Queue Ingest Manager ========================================, Ingest a rendered video file into publish_queue.json.      Args:         video_p, check_deduplication(), 02_dedup_ledger.py — Phase 1 Step 2: Content Deduplication & Disk Checker ======, Step 2 Execution: Verifies if clip shortcode is clean/unique or already on disk., Phase_2 / 04_bgm_selector.py ============================ Step 4: Gemini Call 2, Attempts to load a previously selected BGM track from ClipIntelligenceStore. (+99 more)

### Community 3 - "Community 3"
Cohesion: 0.03
Nodes (86): Attempts to load a previously selected BGM track from ClipIntelligenceStore., build_rhythm_timeline(), Phase_2 / 05_rhythm_timeline.py =============================== Step 5: Rhythm &, Builds micro-shots and routing parameters for editing., Phase 2 helper: loads pre-computed audio_analysis.json from clip_dir.     Return, AudioFamilyPipeline, _empty_packet(), AudioFamilyPipeline v2.0 — "Saints With Ego" =================================== (+78 more)

### Community 4 - "Community 4"
Cohesion: 0.03
Nodes (76): Phase_2 / 01_folder_scanner.py ============================== Step 1: Scans `dow, Scans for clip targets. Returns list of target clip dicts:     [{"dir": clip_fol, scan_clip_targets(), 01_source_config.py — Phase 1 Step 1: Target Source Account & Channel Resolver =, Step 1 Execution: Resolves target accounts to scrape., resolve_target_accounts(), Phase 3 — Step 02: Monetization & Safety QA Gate ===============================, Verify safety and monetization compliance from clip intelligence.      Args: (+68 more)

### Community 5 - "Community 5"
Cohesion: 0.05
Nodes (81): detect_faces(), FaceProtector, HybridWatermarkDetector, is_safe_region(), load_detected_niche(), _niche_sidecar_path(), Hybrid Watermark Manager (Gemini Authority) -----------------------------------, Logs user feedback (Reinforcement Learning Stub).         In "Strict Mode", thi (+73 more)

### Community 6 - "Community 6"
Cohesion: 0.07
Nodes (35): _async_static_scheduler_task(), build_back_button_keyboard(), build_best_attempt_comparison_keyboard(), build_platform_selection_keyboard(), build_reedit_options_keyboard(), build_telegram_session_keyboard(), cmd_ytcode(), execute_reedit_with_directive() (+27 more)

### Community 7 - "Community 7"
Cohesion: 0.1
Nodes (16): ensure_montserrat_font(), Downloads Montserrat-Bold.ttf if it does not exist or is corrupted.     Returns, _validate_font(), cmd_list_to_string(), FFmpegCommandGenerator, Gemini FFmpeg Command Synthesis Engine — AMTCE Video Engine ===================, Evaluates rendered output against intended video context score.     If quality, Computes dynamic 0.0 - 1.0 quality score for synthesized plan.         Returns (+8 more)

### Community 8 - "Community 8"
Cohesion: 0.06
Nodes (38): Compatibility shim for the sample update tree.  This file provides the local pub, _batch_label(), _detect_gender(), _download_reel(), _extract_person_name(), _fetch_reels_apify(), get_source_accounts(), _inject_niche() (+30 more)

### Community 9 - "Community 9"
Cohesion: 0.08
Nodes (31): clear_user_session(), get_user_session(), handle_cancel(), handle_targeted_harvest_input(), handle_targeted_harvest_start(), handle_time_range_selection(), Main_Modules/targeted_harvest_bot.py ===================================== Teleg, Handle time range button selection. (+23 more)

### Community 10 - "Community 10"
Cohesion: 0.11
Nodes (32): publish_to_instagram(), publish_to_meta(), publish_to_telegram(), publish_to_tiktok(), publish_to_youtube(), media_publisher_main.py — Phase 4 Standalone Multi-Platform Publishing Orchestra, Uploads video reel to Instagram via Meta Graph API., Uploads video reel to TikTok Creator account via TikTok Direct Post API. (+24 more)

### Community 11 - "Community 11"
Cohesion: 0.1
Nodes (30): apify_get_video_url(), apify_get_video_url_any(), apify_scrape_creator_accounts(), _check_quota(), _consume_quota(), _find_video_urls(), _get_client(), _get_instagram_cookies() (+22 more)

### Community 12 - "Community 12"
Cohesion: 0.11
Nodes (29): add_user_api_key(), check_vault_cache(), format_pool_status(), get_active_keys(), get_next_api_key(), get_pool_status(), _load_pool(), _load_usage() (+21 more)

### Community 13 - "Community 13"
Cohesion: 0.15
Nodes (10): Core_Modules / session_manager.py ================================== Thread-safe, Increments retry_count. Returns (should_retry, new_count).         Caller decide, Records a rendered attempt video path into attempt_history., Record 1-5 star user feedback rating., Record optional e-commerce affiliate link and product MRP/price., Recover active sessions from disk on startup., Thread-safe session store with per-user locking and atomic disk persistence., Context manager to acquire user-level lock and retrieve session. (+2 more)

### Community 14 - "Community 14"
Cohesion: 0.1
Nodes (16): ContentLedger, extract_shortcode(), file_md5(), get_ledger(), content_ledger.py — Military-Grade Deduplication Ledger =======================, Returns True if this Instagram post was already downloaded., Computes the file MD5 and checks if we've seen it before.         Attaches the, Adds a successfully downloaded reel to the ledger and persists to disk. (+8 more)

### Community 15 - "Community 15"
Cohesion: 0.11
Nodes (25): get_all_active_accounts(), get_primary_accounts(), get_secondary_accounts(), _get_social_folders(), get_target_folder(), is_account_mode_enabled(), _load_config(), actress_config.py — AMTCE Actress Account Router ============================== (+17 more)

### Community 16 - "Community 16"
Cohesion: 0.11
Nodes (25): clear_account_session(), get_account_session(), get_user_id_from_chat(), handle_account_name_input(), handle_account_selection_callback(), handle_add_account_start(), handle_credential_input(), handle_list_accounts() (+17 more)

### Community 17 - "Community 17"
Cohesion: 0.12
Nodes (24): extract_targeted_frames(), Phase_2 / 03_vector_frame_extractor.py ======================================, Extracts targeted frames using Gemini visual_vectors.     Returns list of absol, _compute_optical_flow_scores(), _detect_scene_cuts(), extract_frames_from_vectors(), extract_high_gradient_crops(), extract_strategic_frame_files() (+16 more)

### Community 18 - "Community 18"
Cohesion: 0.11
Nodes (13): BaseModel, AutoHarvestRequest, ConnectionManager, EventBroadcastRequest, ManualHarvestRequest, on_startup(), pipeline_event_callback(), tracker_server.py — FastAPI Real-time Visual Pipeline Tracker Server =========== (+5 more)

### Community 19 - "Community 19"
Cohesion: 0.11
Nodes (20): publish_to_tiktok(), Phase 3 — Step 05: TikTok Publisher ===================================== Handle, Publish video to TikTok platform.      Args:         video_path: Path to rendere, _get_valid_access_token(), _init_post(), _load_tokens(), _poll_status(), tiktok_uploader.py — AMTCE TikTok Content Posting API (Direct Post) =========== (+12 more)

### Community 20 - "Community 20"
Cohesion: 0.14
Nodes (20): check_platform_lock(), _get_service_sync(), get_valid_credentials(), main(), Niche-Aware Credential Resolver.      Resolution order:       1. Niche folder, Retrieves and refreshes valid credentials.     Accepts an optional niche to rou, Checks if the video file has fresh metadata (Unique ID, Creation Time).     Ret, Injects a fresh Unique ID into the video metadata without re-encoding. (+12 more)

### Community 21 - "Community 21"
Cohesion: 0.13
Nodes (11): Phase 3 Package — Master Distribution, Publishing & Creator RAG Feedback =======, phase1_orchestrator.py — Phase 1 Master Pipeline Orchestrator ==================, main(), phase3_main.py — Standalone Entry Point for Phase 3 ============================, notify_tracker(), Phase3Orchestrator, Phase 3 Master Orchestrator — Distribution, Publishing & Creator RAG Feedback =, Convenience wrapper for executing Phase 3 orchestration. (+3 more)

### Community 22 - "Community 22"
Cohesion: 0.17
Nodes (14): analyze_scene_pre_pipeline(), cluster_faces(), load_cached_face(), OpenCVFaceDetector, Core_Modules/scene_intel.py — Scene & Face Intelligence Layer ==================, OpenCV DNN Res10 300x300 Caffe SSD Face Detector with Haar Cascade Fallback., Detect faces in frame.         Returns list of bboxes: [(x, y, w, h), ...], Groups bounding box locations across keyframes into Subject A, B, C... (+6 more)

### Community 23 - "Community 23"
Cohesion: 0.18
Nodes (9): FFmpegAudioRecorder, format_llm_prompt(), Formats the extracted transcript and Gemini analysis into a ready-to-paste LLM p, Executes the full recording -> whisper -> gemini -> JSON export workflow., Handles global FFmpeg system & microphone audio recording on Windows., run_meeting_pipeline(), extract_speech_boundaries(), Speech Boundary Detector (faster-whisper)  Extracts word-level timestamps and se (+1 more)

### Community 24 - "Community 24"
Cohesion: 0.19
Nodes (13): clean_json_response(), detect_watermark(), detect_watermark_from_video(), evaluate(), extract_best_frame_ffmpeg(), frame_to_pil(), Gemini Watermark Detection Module --------------------------------- Isolated m, Detects watermarks AND classifies fashion vs NSFW + picks best thumbnail frame i (+5 more)

### Community 25 - "Community 25"
Cohesion: 0.18
Nodes (12): encode_proxy_video(), 05_proxy_encoder.py — Phase 1 Step 5: 480p Proxy Video Encoder ================, Step 5 Execution: Encodes 480p proxy video., encode_proxy(), ensure_proxy(), _ffmpeg_bin(), get_proxy_path(), proxy_encoder.py — 480p Proxy Compression Engine ============================== (+4 more)

### Community 26 - "Community 26"
Cohesion: 0.24
Nodes (5): HumanPresenceGuard, Visual Safety & Quality Orchestrator ------------------------------------ Gove, Primary Quality Signal:         Detects if humans are present to GATE risky enh, Loads OpenCV DNN Face Detector (ResNet-10) with Haar Cascade fallback, Returns list of faces: {'box': [x,y,w,h], 'confidence': float}         STRICT:

### Community 27 - "Community 27"
Cohesion: 0.5
Nodes (3): notify_tracker(), Import_Modules / tracker_notifier.py ==================================== Lightw, Sends stage event to local tracker server. Safe & non-blocking if server is offl

### Community 28 - "Community 28"
Cohesion: 0.5
Nodes (3): publish_to_meta(), Phase 3 — Step 04: Meta (Instagram & Facebook Reels) Publisher =================, Publish video to Instagram Reels / Facebook Reels.      Args:         video_path

### Community 29 - "Community 29"
Cohesion: 1.0
Nodes (1): Import_Modules / phase1_imports.py =================================== Centraliz

### Community 30 - "Community 30"
Cohesion: 1.0
Nodes (1): Import_Modules / phase2_imports.py ================================== Central

### Community 31 - "Community 31"
Cohesion: 1.0
Nodes (1): Import Hub for Phase 3 Package ================================ Exposes all Phas

### Community 32 - "Community 32"
Cohesion: 1.0
Nodes (0): 

### Community 33 - "Community 33"
Cohesion: 1.0
Nodes (0): 

### Community 34 - "Community 34"
Cohesion: 1.0
Nodes (0): 

### Community 35 - "Community 35"
Cohesion: 1.0
Nodes (0): 

### Community 36 - "Community 36"
Cohesion: 1.0
Nodes (0): 

### Community 37 - "Community 37"
Cohesion: 1.0
Nodes (1): Resolves Meta credentials using a 3-tier priority chain:           1. Credentia

### Community 38 - "Community 38"
Cohesion: 1.0
Nodes (1): Orchestrates uploads to enabled Meta platforms.          The ``niche`` paramet

### Community 39 - "Community 39"
Cohesion: 1.0
Nodes (1): Uploads the local image to a temporary public host so the Instagram         Gra

### Community 40 - "Community 40"
Cohesion: 1.0
Nodes (1): Smart person-aware Instagram ratio formatter (4:5 = 1080x1350).          Strat

### Community 41 - "Community 41"
Cohesion: 1.0
Nodes (1): Uploads a standard Image Post to Instagram feed using the Graph API.         Re

### Community 42 - "Community 42"
Cohesion: 1.0
Nodes (1): Cleans captions of UTF-16 surrogates that cause UnicodeEncodeError in httpx/UTF-

### Community 43 - "Community 43"
Cohesion: 1.0
Nodes (1): Generic retry wrapper for HTTP requests using httpx.         Default timeout in

### Community 44 - "Community 44"
Cohesion: 1.0
Nodes (1): Polls Instagram container status until FINISHED or ERROR.         Timeout defau

### Community 45 - "Community 45"
Cohesion: 1.0
Nodes (1): Fix C: remove `item` from `container` by object identity, not value         equa

### Community 46 - "Community 46"
Cohesion: 1.0
Nodes (1): Get a module by name, loading it lazily if not already cached.

### Community 47 - "Community 47"
Cohesion: 1.0
Nodes (1): Clear the import cache.

### Community 48 - "Community 48"
Cohesion: 1.0
Nodes (1): Singleton pattern so we only load the 500MB model into memory once.

### Community 49 - "Community 49"
Cohesion: 1.0
Nodes (0): 

### Community 50 - "Community 50"
Cohesion: 1.0
Nodes (1): Hydrates local disk stores (pool_metadata.json, .clip_intelligence.json)

### Community 51 - "Community 51"
Cohesion: 1.0
Nodes (1): Mark a BGM track as used without moving to cooldown (rotation disabled per direc

### Community 52 - "Community 52"
Cohesion: 1.0
Nodes (1): Rotates clips from cooldown back to active based on hybrid logic.         Clean

### Community 53 - "Community 53"
Cohesion: 1.0
Nodes (1): Return the pool_metadata["files"] dict — the unified audio track index.

### Community 54 - "Community 54"
Cohesion: 1.0
Nodes (1): Merge rich lyric intelligence fields from a _lyric.json result INTO         poo

### Community 55 - "Community 55"
Cohesion: 1.0
Nodes (1): Hydrates local disk stores (pool_metadata.json, .clip_intelligence.json)

### Community 56 - "Community 56"
Cohesion: 1.0
Nodes (1): Lazy load beat data from cache or disk.

### Community 57 - "Community 57"
Cohesion: 1.0
Nodes (1): Moves newly extracted audio into pool and caches deep beat metadata.

### Community 58 - "Community 58"
Cohesion: 1.0
Nodes (1): Rotate files from cooldown back to active. If force=True, recycle all files imme

### Community 59 - "Community 59"
Cohesion: 1.0
Nodes (1): Mark a BGM track as used without moving to cooldown (rotation disabled per direc

### Community 60 - "Community 60"
Cohesion: 1.0
Nodes (1): Rotates clips from cooldown back to active based on hybrid logic.         Clean

### Community 61 - "Community 61"
Cohesion: 1.0
Nodes (1): Return the pool_metadata["files"] dict — the unified audio track index.

### Community 62 - "Community 62"
Cohesion: 1.0
Nodes (1): Merge rich lyric intelligence fields from a _lyric.json result INTO         poo

### Community 63 - "Community 63"
Cohesion: 1.0
Nodes (1): Hydrates local disk stores (pool_metadata.json, .clip_intelligence.json)

### Community 64 - "Community 64"
Cohesion: 1.0
Nodes (1): Atomic write to prevent corruption.

### Community 65 - "Community 65"
Cohesion: 1.0
Nodes (1): Standardized cache key for requests (Vanguard Pattern).

### Community 66 - "Community 66"
Cohesion: 1.0
Nodes (1): World-Class Weighted Scoring Engine (V4.2 'Elite' Edition).          Factors:

### Community 67 - "Community 67"
Cohesion: 1.0
Nodes (1): Public wrapper for prompt simplification used by the VANGUARD retry loop.

### Community 68 - "Community 68"
Cohesion: 1.0
Nodes (1): [VANGUARD] Local Fallback to Ollama (Phi-3).

### Community 69 - "Community 69"
Cohesion: 1.0
Nodes (1): VANGUARD BULLETPROOF GENERATOR: Loop-based Retry + Global Deadline + Jitter.

### Community 70 - "Community 70"
Cohesion: 1.0
Nodes (1): Returns active models list and task ratings matrix.     Loads from cache if ava

### Community 71 - "Community 71"
Cohesion: 1.0
Nodes (1): Filters out embeddings, audio-only, imagen, and legacy non-gemini models.

### Community 72 - "Community 72"
Cohesion: 1.0
Nodes (1): Sorts discovered models into Pro -> Flash -> Lite tiers.

### Community 73 - "Community 73"
Cohesion: 1.0
Nodes (1): Computes heuristic category rating matrices for all 10 task categories     base

### Community 74 - "Community 74"
Cohesion: 1.0
Nodes (1): Refreshes storage/gemini_models_cache.json.     Enforces a 5-minute cooldown ti

### Community 75 - "Community 75"
Cohesion: 1.0
Nodes (1): Loads model cache from storage/gemini_models_cache.json if valid.

### Community 76 - "Community 76"
Cohesion: 1.0
Nodes (1): Returns active models list and task ratings matrix.     Loads from cache if ava

### Community 77 - "Community 77"
Cohesion: 1.0
Nodes (1): Check if the global circuit breaker is active.

### Community 78 - "Community 78"
Cohesion: 1.0
Nodes (1): Record a 5xx failure. Trip breaker if conditions met.

### Community 79 - "Community 79"
Cohesion: 1.0
Nodes (1): Reset the circuit breaker on a successful call.

### Community 80 - "Community 80"
Cohesion: 1.0
Nodes (1): V3.5 World-Class Intelligent Router.      Handles multi-tier scoring, adaptive

### Community 81 - "Community 81"
Cohesion: 1.0
Nodes (1): Compute a non-reversible hash of the API key for change detection.

### Community 82 - "Community 82"
Cohesion: 1.0
Nodes (1): Pre-initialize supported models with default states.

### Community 83 - "Community 83"
Cohesion: 1.0
Nodes (1): Call at the start of every video to reset the per-video call budget.

### Community 84 - "Community 84"
Cohesion: 1.0
Nodes (1): Atomic write to prevent corruption.

### Community 85 - "Community 85"
Cohesion: 1.0
Nodes (1): Standardized cache key for requests (Vanguard Pattern).

### Community 86 - "Community 86"
Cohesion: 1.0
Nodes (1): World-Class Weighted Scoring Engine (V4.2 'Elite' Edition).          Factors:

### Community 87 - "Community 87"
Cohesion: 1.0
Nodes (1): Public wrapper for prompt simplification used by the VANGUARD retry loop.

### Community 88 - "Community 88"
Cohesion: 1.0
Nodes (1): [VANGUARD] Local Fallback to Ollama (Phi-3).

### Community 89 - "Community 89"
Cohesion: 1.0
Nodes (1): VANGUARD BULLETPROOF GENERATOR: Loop-based Retry + Global Deadline + Jitter.

## Knowledge Gaps
- **381 isolated node(s):** `Mixes Voiceover + Background Music + Original Audio using Context-Aware Audio Ro`, `Beat Engine ----------- Zero-dependency Beat Detection for Viral Edits. Uses`, `Returns True if the file contains at least one audio stream.         Used as a`, `Analyzes an audio file and returns a list of significant beat timestamps.`, `Detect beat DROPS: moments where energy surges suddenly after relative quiet.` (+376 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **Thin community `Community 29`** (2 nodes): `phase1_imports.py`, `Import_Modules / phase1_imports.py =================================== Centraliz`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 30`** (2 nodes): `phase2_imports.py`, `Import_Modules / phase2_imports.py ================================== Central`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 31`** (2 nodes): `phase3_imports.py`, `Import Hub for Phase 3 Package ================================ Exposes all Phas`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 32`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 33`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 34`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 35`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 36`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 37`** (1 nodes): `Resolves Meta credentials using a 3-tier priority chain:           1. Credentia`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 38`** (1 nodes): `Orchestrates uploads to enabled Meta platforms.          The ``niche`` paramet`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 39`** (1 nodes): `Uploads the local image to a temporary public host so the Instagram         Gra`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 40`** (1 nodes): `Smart person-aware Instagram ratio formatter (4:5 = 1080x1350).          Strat`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 41`** (1 nodes): `Uploads a standard Image Post to Instagram feed using the Graph API.         Re`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 42`** (1 nodes): `Cleans captions of UTF-16 surrogates that cause UnicodeEncodeError in httpx/UTF-`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 43`** (1 nodes): `Generic retry wrapper for HTTP requests using httpx.         Default timeout in`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 44`** (1 nodes): `Polls Instagram container status until FINISHED or ERROR.         Timeout defau`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 45`** (1 nodes): `Fix C: remove `item` from `container` by object identity, not value         equa`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 46`** (1 nodes): `Get a module by name, loading it lazily if not already cached.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 47`** (1 nodes): `Clear the import cache.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 48`** (1 nodes): `Singleton pattern so we only load the 500MB model into memory once.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 49`** (1 nodes): `__init__.py`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 50`** (1 nodes): `Hydrates local disk stores (pool_metadata.json, .clip_intelligence.json)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 51`** (1 nodes): `Mark a BGM track as used without moving to cooldown (rotation disabled per direc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 52`** (1 nodes): `Rotates clips from cooldown back to active based on hybrid logic.         Clean`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 53`** (1 nodes): `Return the pool_metadata["files"] dict — the unified audio track index.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 54`** (1 nodes): `Merge rich lyric intelligence fields from a _lyric.json result INTO         poo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 55`** (1 nodes): `Hydrates local disk stores (pool_metadata.json, .clip_intelligence.json)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 56`** (1 nodes): `Lazy load beat data from cache or disk.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 57`** (1 nodes): `Moves newly extracted audio into pool and caches deep beat metadata.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 58`** (1 nodes): `Rotate files from cooldown back to active. If force=True, recycle all files imme`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 59`** (1 nodes): `Mark a BGM track as used without moving to cooldown (rotation disabled per direc`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 60`** (1 nodes): `Rotates clips from cooldown back to active based on hybrid logic.         Clean`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 61`** (1 nodes): `Return the pool_metadata["files"] dict — the unified audio track index.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 62`** (1 nodes): `Merge rich lyric intelligence fields from a _lyric.json result INTO         poo`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 63`** (1 nodes): `Hydrates local disk stores (pool_metadata.json, .clip_intelligence.json)`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 64`** (1 nodes): `Atomic write to prevent corruption.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 65`** (1 nodes): `Standardized cache key for requests (Vanguard Pattern).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 66`** (1 nodes): `World-Class Weighted Scoring Engine (V4.2 'Elite' Edition).          Factors:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 67`** (1 nodes): `Public wrapper for prompt simplification used by the VANGUARD retry loop.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 68`** (1 nodes): `[VANGUARD] Local Fallback to Ollama (Phi-3).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 69`** (1 nodes): `VANGUARD BULLETPROOF GENERATOR: Loop-based Retry + Global Deadline + Jitter.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 70`** (1 nodes): `Returns active models list and task ratings matrix.     Loads from cache if ava`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 71`** (1 nodes): `Filters out embeddings, audio-only, imagen, and legacy non-gemini models.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 72`** (1 nodes): `Sorts discovered models into Pro -> Flash -> Lite tiers.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 73`** (1 nodes): `Computes heuristic category rating matrices for all 10 task categories     base`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 74`** (1 nodes): `Refreshes storage/gemini_models_cache.json.     Enforces a 5-minute cooldown ti`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 75`** (1 nodes): `Loads model cache from storage/gemini_models_cache.json if valid.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 76`** (1 nodes): `Returns active models list and task ratings matrix.     Loads from cache if ava`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 77`** (1 nodes): `Check if the global circuit breaker is active.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 78`** (1 nodes): `Record a 5xx failure. Trip breaker if conditions met.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 79`** (1 nodes): `Reset the circuit breaker on a successful call.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 80`** (1 nodes): `V3.5 World-Class Intelligent Router.      Handles multi-tier scoring, adaptive`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 81`** (1 nodes): `Compute a non-reversible hash of the API key for change detection.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 82`** (1 nodes): `Pre-initialize supported models with default states.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 83`** (1 nodes): `Call at the start of every video to reset the per-video call budget.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 84`** (1 nodes): `Atomic write to prevent corruption.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 85`** (1 nodes): `Standardized cache key for requests (Vanguard Pattern).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 86`** (1 nodes): `World-Class Weighted Scoring Engine (V4.2 'Elite' Edition).          Factors:`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 87`** (1 nodes): `Public wrapper for prompt simplification used by the VANGUARD retry loop.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 88`** (1 nodes): `[VANGUARD] Local Fallback to Ollama (Phi-3).`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.
- **Thin community `Community 89`** (1 nodes): `VANGUARD BULLETPROOF GENERATOR: Loop-based Retry + Global Deadline + Jitter.`
  Too small to be a meaningful cluster - may be noise or needs more connections extracted.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get()` connect `Community 0` to `Community 1`, `Community 2`, `Community 3`, `Community 4`, `Community 5`, `Community 6`, `Community 7`, `Community 8`, `Community 9`, `Community 10`, `Community 11`, `Community 12`, `Community 14`, `Community 15`, `Community 16`, `Community 17`, `Community 18`, `Community 19`, `Community 20`, `Community 21`, `Community 22`, `Community 23`, `Community 24`?**
  _High betweenness centrality (0.600) - this node is a cross-community bridge._
- **Why does `ClipIntelligenceStore` connect `Community 2` to `Community 0`, `Community 1`, `Community 3`, `Community 4`, `Community 7`, `Community 11`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `BeatEngine` connect `Community 1` to `Community 2`, `Community 3`, `Community 4`, `Community 7`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 253 inferred relationships involving `get()` (e.g. with `handle_telegram_callback()` and `execute_reedit_with_directive()`) actually correct?**
  _`get()` has 253 INFERRED edges - model-reasoned connections that need verification._
- **Are the 113 inferred relationships involving `ClipIntelligenceStore` (e.g. with `PollingFilter` and `main.py — Master Orchestration & Telegram Bot Entrypoint ======================`) actually correct?**
  _`ClipIntelligenceStore` has 113 INFERRED edges - model-reasoned connections that need verification._
- **Are the 118 inferred relationships involving `BeatEngine` (e.g. with `AudioFamilyPipeline` and `AudioFamilyPipeline v2.0 — "Saints With Ego" ===================================`) actually correct?**
  _`BeatEngine` has 118 INFERRED edges - model-reasoned connections that need verification._
- **Are the 98 inferred relationships involving `AudioPoolManager` (e.g. with `audio_extractor.py — Phase 1 Audio Extraction + Beat Analysis ==================` and `Returns True if the file has at least one audio stream (fast ffprobe check).`) actually correct?**
  _`AudioPoolManager` has 98 INFERRED edges - model-reasoned connections that need verification._