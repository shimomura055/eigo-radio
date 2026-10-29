# APPROVAL_RECONCILIATION_01(FX-MOON-SHRINKING-RESELECT-REMAKE-01 委任_03、2026-10-29、API 0)

対象=Family X『月は少しずつ縮んでいる？』Standard(a2)日本語題 `月のしわ、8,900本超！その奥に潜む「岩の上着」の秘密`(canonical_text sha256=`b02b1f603bf132f29d5d72db2d0dd8bcbe8d246b741497dccdce325bc9fbad16`。ms_03/reselect両runで同一=`tts_generation_results.json segments.japanese_title.canonical_text`をsha照合)。
ユーザー原文§2: `docs/pm/delegation_log/2026-10-29_FX-MOON-SHRINKING-RESELECT-REMAKE-01_USER_02.md`(1.前回OKとした3音声の対象を特定 2.今回HR 2音声との照合 3.承認済み音声は再判断を求めない)。

## 1. 「前回OKとした3音声」の特定(記録から)

| 記録 | 内容(逐語) | 対象 |
|---|---|---|
| `docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_06.md:6` | 「Family X『月は少しずつ縮んでいる？』のStandard日本語タイトルについて、ユーザーが3回分すべてを試聴し、**『どれも問題ありません』**と明示判断した。」 | **run_ms_03 のStd日本語題 attempt 1・2・3の3音声**(=「前回OKとした3音声」) |
| 同 `:8-13` | 「音声の再生成は不要。数字のASR照合が主・副とも一致したattempt 2を採用する。…今回の判断を一般的なASR検査免除として扱わない。」 | 採用=attempt 2 |
| `er019_output/family_x_audio_production_wiring_01/moon_shrinking__run_ms_03/a2/audit/fxnr10_user_approval_record.json` | `approved_by`=「user(2026-10-25 listening, 3 attempts all OK; attempt 2 adopted)」、`adopted_attempt`=2、`adopted_audio_sha256`=f0c4b415…、`scope`=「**this single segment / attempt 2 only; NOT a general ASR-check exemption; no TTS/ASR call**」 | 正式な承認(HUMAN_APPROVED)記録はattempt 2のみ |
| `…/ms_03/a2/audit/human_approved_segments.json`(`record_human_approval`の記録先=`er003_v1_n3_01_assemble.py:92-113`) | `japanese_title`: canonical_text_sha256=b02b1f60…、approved_at=2026-10-25T15:59:10 | 同上(segment単位・canonical_text sha) |
| `…/ms_03/a2/audit/review_lock_state.json`・`tts_generation_results.json` | `japanese_title`=RESOLVED/HUMAN_APPROVED化(`adopted_audio_sha256`=f0c4b415…)。ASR NG記録は保存(`pre_fxnr10_approval_backup.json`) | 同上 |

**追加の記録(3本ではなく6本)**: `docs/pm/delegation_log/2026-10-28_JA-ASR-FALSE-NG-ROOT-FIX-02_USER.md:22-40`(§2)に、ユーザーが「以下6音声を実際に試聴し、すべて問題なし」と判断した表がある(ms_03 attempt 1/2[OK・個別採用済み]/3、reselect_01 attempt 1/2/3=いずれもOK)。ただし同:40「今回のHuman OKは**検証用の正解ラベル**であり、ASR Gateの恒久的な免除や、6音声のProduction一括採用を意味しません」。したがって:
- **ユーザーOKの記録がある音声=6本**(ms_03 3本=2026-10-25、reselect 3本=2026-10-28の検証用ラベル)。
- **正式な承認(HUMAN_APPROVED)・採用の記録がある音声=ms_03 attempt 2の1本のみ**(sha f0c4b415…)。reselect 3本のOKは「検証用の正解ラベル」で、Production採用の承認ではない(原文§2が明記)。
- 「前回OKとした3音声」=ms_03 attempt 1・2・3(`USER_06:6`)。推測で別の3本を作っていない。

## 2. 音声別の照合表(今回判定=JA-ASR v2+β配線後の保存転写判定[RUNTIME_EVIDENCE_01.md:12-19])

| 音声 | run/attempt | wav sha256(先頭12/全64) | 今回判定 | 承認記録の有無・scope | 結論 |
|---|---|---|---|---|---|
| ms_03 a1 | run_ms_03 a2/narration/attempts/japanese_title_attempt1_customb8f0ff16.wav | 5ccb3c481547 (5ccb3c481547abba2bda656be32bf82f441d3723b192d0bd1f7081f81d460ee3) | **HR `p1_value_diff`** | ユーザー試聴OK(2026-10-25 USER_06:6)。正式承認記録なし(採用はattempt 2のみ) | ユーザーOK済み(聴取)。ただし**この音声を使う必要はない**(下記attempt 2を使う) |
| ms_03 a2 | 同 attempt2 | f0c4b41580d3 (f0c4b41580d30e2da496a818a55ec0bbd012af8bbd7bfc39c47913da6eed6865) | PASS_W(`primary_pass`/v2/`JA_NEWLAYER_PRON_EQUIVALENT`) | **あり**: ユーザー試聴OK+個別採用、scope「this single segment / attempt 2 only; NOT a general ASR-check exemption」(fxnr10_user_approval_record.json、human_approved_segments.json) | **承認済み** |
| ms_03 a3 | 同 attempt3(minimal fallback) | d0dd41e4d8bf (d0dd41e4d8bf4995a2ee7dc6f415165eda8fd2a586d6c71b185ada74d3567b5c) | PASS_W(`ja_beta_composite`/β/`JA_COMPOSITE_LISTEN_ADVISED`) | ユーザー試聴OK(USER_06:6)。正式承認記録なし | ユーザーOK済み(聴取)。正式採用記録はなし |
| reselect a1 | run_reselect_01 a2/narration/attempts/japanese_title_attempt1_customb8f0ff16.wav | 6801464baf94 (6801464baf94805e20093dc26a2071b003ac6e30bbdfa8b924c92bb9dc298a25) | PASS_W(v2) | ユーザーOK=検証用ラベルのみ(JA-ASR-FALSE-NG-ROOT-FIX-02_USER.md:40)。HUMAN_APPROVED記録なし | Production採用の承認なし。ただし機械判定はPASS_W |
| reselect a2 | 同 attempt2 | dd3dbc1e6304 (dd3dbc1e630450305b6613e6449395e4ae8ad3885e9c49d9dba8d0c3b3548e19) | PASS_W(v2) | 同上 | 同上 |
| reselect a3 | 同 attempt3(fallback) | 45309c9f88e1 (45309c9f88e1af709fc96d90d6d7bd72e54ae4a34de0ce99565be775ebb27a82) | **HR `secondary_not_accepted`** | ユーザーOK=検証用ラベルのみ。HUMAN_APPROVED記録なし。現runのnarration/japanese_title.wav(=この音声、sha一致)は`review_lock_state` HUMAN_REVIEW_REQUIRED/STOPPED | 検証用OKのみ。**現run(STOPPED)のHR Lockはこの音声に残っている** |

今回HRに残った2音声と承認記録の関係:
- **ms_03 a1(HR, p1_value_diff)**: ユーザー聴取OK(3本全て問題なし)あり。承認(採用)記録はattempt 2のみで、a1は使用しない。→再判断不要(使わない)。
- **reselect a3(HR, secondary_not_accepted)**: 承認(採用)記録なし(検証用OKラベルのみ)。ただし**この音声を使う必要がない**: 同一canonical_text・同一Voice(Aoede)・同一style(customb8f0ff16)の**承認済み音声(ms_03 attempt 2, sha f0c4b415…)が存在する**ため、未承認のまま残るのはreselect a3のみで、それは採用しない。
- 結論: **ユーザーに再判断を求める音声は無い**。Std日本語題に使う音声=ms_03 attempt 2(承認済み)。reselect a3を採用する場合のみ未承認だが、採用しない。

## 3. 注入経路と承認scopeの確認(新機構なし)

- 経路: `er003_v1_n3_01_assemble.record_human_approval()`(`:96-113`)+ review_lock_state `HUMAN_REVIEW_REQUIRED→RESOLVED/HUMAN_APPROVED` + 採用wavを`narration/japanese_title.wav`へ配置。先例=`er019_fx_moon_title_individual_approval_01.py:44-85`(ms_03自身で実施。`FXNR10_HUMAN_APPROVAL_NOTE`)、`er011_discovery_generalization_towels_trial_11_audio_03_b1b_individual_approval_and_assemble_01.py`。組立側gate=`er003_v1_n3_01_assemble._segment_gate_status`(`:116-136`: status=STOPPED/HUMAN_REVIEW_LOCKEDは`human_approved_segments.json`のcanonical_text_sha256一致で承認扱い。**canonical_text shaはms_03とreselectで一致**)。新Gate・flag・迂回なし。
- scope: 承認scope「this single segment / attempt 2 only」の対象=月記事のStd日本語題segment・attempt 2の**音声そのもの**(sha f0c4b415…)。reselect runのattemptへ自動拡大はしない(UDR #203記述)が、**同一shaの承認済み音声を同一canonical_textのsegmentに置く**ことは「attempt 2 only」の範囲内。ユーザー原文§2-3「承認済みの音声について、同じ内容の再判断をユーザーに求めない」とFable委任文§2(承認済み音声再利用注入)に整合。注入時にsha照合(f0c4b415…と一致)とcanonical_text sha照合(b02b1f60…と一致)をscriptで実施・記録する。「一般的なASR検査免除」ではない(注入記録のscopeに明記)。
- 前提の確認項目: 同一Voice=Aoede(両runのattempt json `voice`)、同一style(`customb8f0ff16`)、同一canonical_text(上記sha)。
