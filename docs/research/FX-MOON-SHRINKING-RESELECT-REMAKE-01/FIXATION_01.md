# FIXATION_01 正本特定(FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_01、2026-10-28、API 0で確認)

## 1. 対象
- 正式ID(slug)=`moon_shrinking`、Family=X(Std=a2 / Adv=b1b)。日本語題(HR承認済み)=「月のしわ、8,900本超！その奥に潜む『岩の上着』の秘密」、フォーム表示名=『月は少しずつ縮んでいる？』。
- 経緯(OPEN-505/507/509、DECISION_LOG 2026-10-25): run_ms_01(数値脱落・暫定)→run_ms_02(再脱落)→**run_ms_03**(中核数値保持方式v4=ユーザー正式採用APPROVED_FOR_PRODUCTION後の正式再生成)。run_ms_03のStd日本語題はユーザー個別承認(USER_06、attempt 2)。

## 2. 本文正本(run_ms_03。選定根拠: 正式Production配線で再生成された最新版・公開音声と一致・scaffold sha記録と一致)
| level | path | raw sha256 | LF正規化sha256(canonical先頭16) | bytes |
|---|---|---|---|---|
| a2 (Std) | `er019_output/moon_shrinking/run_ms_03/a2/article.md` | `6d388285febe5a766d4c02d19e573772fdfddbbec6185997274f92af5afff0bd` | `f456110d37dfb0dc` | 3097 |
| b1b (Adv) | `er019_output/moon_shrinking/run_ms_03/b1b/article.md` | `3fb35041e03e04c77ffd771034c32ad09193bccc833e81fdf03bf726d648624b` | `bb726361e196fdb2` | 3183 |
- 一致確認: `er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/audit/scaffold_article_sha256.json`(両level同sha)。新run `run_reselect_01`の本文コピーも同sha(sha256sum一致)。
- 他版(正本ではない): run_ms_01(a2 `9e0b0b16…`/b1b `1532dcac…`、数値脱落の暫定)、run_ms_02(`235e6c64…`/`b2bf2bc3…`、W-1再実行・再脱落)。
- 承認記録: 本文の専用承認レコードは無い(最終試聴PASS未取得=`COMPLETE_USER_LISTENING_PENDING`)。UDR #189回答(2026-10-25 Trial承認・Production再実行は採用判断後)+OPEN-507 PRODUCTION_WIRED(月run_ms_03がWIRING_RUNTIME_EVIDENCE)+USER_06(Std題)+本件ユーザー原文§1「既存のStd/Adv本文は変更しない」により、run_ms_03を正本と一意化(不一致・複数候補の競合なし)。

## 3. 既存完成物
- 公開(最終完成版): `user_test/family_x_moon_shrinking_02/index.html`(Std 334.5秒/Adv 305.8秒、47音声、commit `5306e5c59`)。旧公開 `user_test/family_x_moon_shrinking_01/`(run_ms_01、品質条件未達の暫定版)。
- 音声run: `er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/`(Adv=既存合格の非Chunk分割音声、Std=題のみユーザー個別承認)。
- 既存のKP: X2p'(旧方式 fulltext 3件選定・AIによる選定)。**V3フォーム(KP7+KW5・①3/②5/③12・ユーザー選定)・文法Top1/Top2は未適用**=本件の再選定対象。ユーザー最終試聴は未取得。

## 4. 新run(既存を上書きしない)
- source: `er019_output/moon_shrinking/run_reselect_01`(run_ms_03のコピー、raw_usage_logとaudit除く=本文・ja_writer・research_ledger・storyline_b3)
- out: `er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_reselect_01`(Preview/Commentの既存support文面2件+entity_table/rf_tts_guard/style_profileのみcopy=support再生成0・本文再生成0)
- 実行: (1)`--stage scaffold --scaffold-only kp`(KP候補+gloss整合+QA、rc=0でKP_REVIEW_PENDING)(2)`--stage study_text`(Part 2文法候補+Top1/Top2解説事前生成、KP未確定の待機)。`--kp-review auto`・`declare-absent`は未使用。TTS/ASR/assembleへは進んでいない(入口assertも迂回なし)。
