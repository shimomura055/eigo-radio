# FIXATION_01 『告げ口心臓』既存成果の固定(FZ-TELL-TALE-HEART-RESELECT-REMAKE-01 委任_01、2026-10-27、API 0で確認)

## 1. 固定した本文(正本)
正本=**案A配線後の正式再生成 `run_sf_prod_02`**(OPEN_ITEMS OPEN-503/508、公開中の`user_test/family_z_tell_tale_heart_01`はそのChunk分割版`run_chunk_01`)。本文は`writer/r2.md`(=Advanced `b1b`)・`writer/std.md`(=Standard `a2`)。`_level_text_path`(er062_family_z_writer_01.py:1536)。

| 対象 | 所在(run: `er026_output/family_z_production_e2e_01/the_tell_tale_heart/`) | sha256 生バイト(LF正規化も同値、CRLFなし) | 語数 |
|---|---|---|---|
| Adv `r2.md` | `run_sf_prod_02/writer/r2.md` | `e11b84dd2be5a60a2adce62b550046acd47940222956e1b35dbcbab31b4e2f38` | 417(ファイル全体)/411(canonical本文) |
| Std `std.md` | `run_sf_prod_02/writer/std.md` | `b94c730552ef103eb7d18027db47fc9367f659ff8e5081a10e5949457b45d8ae` | 434/428 |
| Adv canonical本文sha(タイトル除く段落連結、KP/Gate/フォームの「本文sha」) | | `0c71c2f017d1e25a61c6a0ceaec6c9133b89f0e898990f3c21ccd7d9a199bafd` | 22段落 |
| Std canonical本文sha | | `66da3226a61eada97bbbfdd816c415e95e898a2233ff969642734045513a7dcb` | 22段落 |

writer provenance(`writer/provenance.json`)= r0/r1/r2/std_adjust 4段、生成2026-10-25 01:36〜01:38 UTC、seed_sha256 `355a317a9b18...`。

### 同一性(sha256比較)
- `run_sf_prod_02` = `run_chunk_01` = `run_p1_evidence_01/02/03` = `run_p2_evidence_r3/r4` = **新run `run_reselect_01`**(コピー後を再計算)で、r2.md/std.md/cp_checklist.md/r0.md/r1.mdのsha256が**完全一致**。本文の候補は1種のみで、正本は一意。
- 差分があるのは旧`run_sf_prod_01`のみ(Adv `9a3e949c8ccde50e...`/Std `3fe1cbdbe3607e61...`、Adv 434語・三人称。**ユーザーが三人称NG**と判断した版=退避扱い、OPEN-503)。**正本ではない**。
- 公開中ページとの照合(独立再実施、API 0): `user_test/family_z_tell_tale_heart_01/{advanced,standard}.html`のタグ除去文に、canonical本文22段落が語単位(大文字小文字・’正規化)で21/22一致、残1段落(`"Who's there?" he cried.`)はページ側が引用と地の文を別セルに分割している表記差のみ(前回記録`PUBLIC_REPLACEMENT_01.md`の「Adv 22/22・Std 22/22一致」と整合)。
- 新run `run_reselect_01` には本文生成stage(writer/std_adjust)を一切走らせず、runnerの承認済みassetコピー機構(`er063_family_z_audio_01.copy_reusable_run_assets`の許可リスト=`writer/`・segment_plan・dialogue_attribution・speaker_table・support)で**コピーのみ**(API 0)。コピー計画=`run_reselect_01_copy_plan.json`。旧KP(`key_phrases/`85ファイル)は**意図的に持ち込まず**新規に候補生成(Human Review対象)。

## 2. 過去の制作状況と停止箇所
| 項目 | 内容 | 根拠 |
|---|---|---|
| 到達工程 | Z正式E2E完了(writer→plan→support→kp→tts→gate→assemble→pages→page_verify)、公開差替え済み | OPEN_ITEMS OPEN-503, `PUBLIC_REPLACEMENT_01.md` |
| 版の履歴 | run_sf_prod_01(Adv三人称=ユーザーNG)→案A(FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01、OPEN-508)でrun_sf_prod_02再生成(実費34.64円、HR Lock 0・retry 0)→Chunk分割版run_chunk_01(2026-10-25、実費16.67円、Adv narrator 100語超2clipを[58,62]/[65,61]へ段落分割+0.2秒)→公開差替え(2026-10-25 15:04) | 同上 |
| 過去のKP選定 | **AI選定(V3フォーム未使用・ユーザー選定なし)**。Std: `make one's blood turn cold` / `louder and louder`(旧#2 `catch of one's lantern`をKP-FIX-01で差替え) / `go on talking`。Adv: `sharpen someone's senses` / `cloudy film` / `never stir`。文法・①②③表示仕様は未適用(旧仕様のKP3件) | `FAMILY-Z-TELL-TALE-HEART-KP-FIX-01/SELECTION_01.md`、`run_chunk_01/key_phrases/{a2,b1b}/keywords_canonicalized.json` |
| Chunk版・公開 | 公開dirは候補`user_test/family_z_tell_tale_heart_chunk_01`と全58本sha一致。Gate PASS、全segment OK(Adv22/Std19)、LR 0・HR 0 | PUBLIC_REPLACEMENT_01.md 8点確認 |
| ユーザー承認の状態 | **最終試聴PASSは未取得**(COMPLETE_USER_LISTENING_PENDING、UDR #188)。今回の委任原文が「既存のユーザー確認済みスクリプト」を本文として再利用する承認 | OPEN-503, 委任USER原文 §2 |
| 停止箇所 | なし(完了済み・試聴待ち)。今回は旧KP・旧音声を完成版に流用せず、新runで学習項目再選定→音声再制作する | 委任原文 §1,§4 |

## 3. 現行Production仕様との差(旧公開版にない現行仕様。CURRENT_SPEC.mdの該当節、Grep確認)
| 現行仕様 | CURRENT_SPEC.md | 旧公開版(run_chunk_01) |
|---|---|---|
| V3フォーム(人間可読コピー+照合コード、送信) | :3206 | 未使用(AIがKP選定) |
| KP確定内容保護(Human Review→確定→保護) | :3195節 | 旧run扱い(review無し・legacy再利用) |
| 文法Top1/Top2事前生成・原則1件・0件可 | :2104-2106 | 旧仕様(Part 2文法はV3以前の方式。詳細は未確認) |
| ①②③表示仕様(LEARNING_ITEMS_123_V1)・本文ハイライト・Std Part 1 | :2086, :3234 | 未適用(マークなし旧run) |
| Part 1(案α+T1訳) | :2088 | Advのみ・indexに1ブロック |
| Chunk TTS(Z=B_r1) | :2990-2992 | 適用済み(Adv narrator 2 clip) |
| セリフTTS 文脈・感情付き(fz_ctx_v1)+Fallback | :1644-1652 | 公開時点では未適用(2026-10-26採用)→新runで適用される見込み |
| 速度仕様v2(Std Narrator 6%減速・Adv Dialogue高速化) | :1633, :1707 | 適用済み(2026-10-23) |
| Style actual gate(M1)/統一TTS retry・LR・Primary/Secondary ASR・HR Lock | :1265ほか、runner `stage_tts`/`run_audio_gate` | 適用済み |

## 4. 再利用できる成果物
- 本文(writer/ r0〜r2・std)・segment_plan・dialogue_attribution・speaker_table・support(Preview/Comment)・provenance: コピーして再利用(API 0)。
- Voice割当(`voice_assignment.json`は決定的に再計算)、Style定義、固定Master/ショップ資産(`provision_shell`)は共通資産として再利用。
- 再利用しない: 旧KP(キー候補・選定結果)、旧音声(`a2/`/`b1b/`のnarration・audit・assembly)、旧公開ページ。
