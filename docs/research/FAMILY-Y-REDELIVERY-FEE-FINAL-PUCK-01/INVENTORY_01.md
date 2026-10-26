# INVENTORY_01 — 『宅配の再配達は有料にすべきか？』既存成果物の棚卸し

FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01(read-only・API 0、2026-10-26 17:2x JST時点)。機械可読版=`inventory_01.json`(全segmentのstatus/voice/duration/sha/mtime/lock/承認/公開ページ参照)。run dir・コード・SSOTは編集していない。wavは読込のみ(sha照合)。

## 1. run dir一覧(`er121_output/family_y_production_01/`)

| dir | 位置づけ | 本委任での扱い |
|---|---|---|
| `redelivery_fee/run_01` | **正式E-1成果物**(Std=a2 / Adv=b1b、290MB、wav 152本)。最終組立=Std 347.03秒/Adv 320.69秒、gate PASS、page_verify ok(`gate_summary.json`/`assemble_summary.json`/`page_verify_local.json`)。Comment 2削除はCOMMENT2 委任_03(commit 28bad7b33、2026-10-26 09:50-09:59 JST)で反映済み | 再利用元(=制作対象) |
| `redelivery_fee/run_voice_puck_ev_01` | 並行Agent(VOICE-TABLE)が17:19-17:22に`run_01`を複製して作成中のPuck evidence run。起動引数=`--stage tts_a2 --only-segments y_voice_1 --approved-budget-jpy 60`(`run_launch_log.jsonl`、`RUN_LOCK.json`)。読取時点でresults内`y_voice_1`はまだAlgieba(a2 sha c3f59b00…、b1b 821f2c18…)=生成完了前。`a2|b1b/audit/`に`human_approved_segments.json`/`review_lock_state.json`が**無い**(複製時に除去されたとみられる=推定) | **最終成果物には再利用しない**(dev evidence)。完了後に結果を参考にする |
| `redelivery_fee_stdchunk_ev/run_ev_01` | Chunk Std evidence(dev入力) | 再利用不可 |
| `sns_age_limit/run_01` | 別記事(E-3、Trial保管) | 対象外 |

## 2. Voice 1由来の音声(=Puckで再生成が必要)

Y構造ではナレーター(Aoede。Advのpreview/comment/共有はCharon)がリード文(`y_intro_n`)を読み、Voice nの声は**本文(`y_voice_n`)のみ**(`er121_family_y_structure_01.py:53` `FIXED_VOICE_SLOTS`、`:80-81` `voice_of_segment`、`er121_family_y_audio_01.py:82-84` `segment_voice_map`、いずれもHEAD)。よって**Voice 1由来=2 segmentのみ**。

| level | segment | 現状 | 長さ | 現sha256 | 公開ページ参照 | 備考 |
|---|---|---|---|---|---|---|
| a2(Std) | `y_voice_1` | status OK / **Algieba** / 6%減速済(`slowdown_applied=True`)/ 人間承認済(ypl7、attempt5) | 46.465秒(減速前38.79) | c3f59b0040d9… | `audio/std_18.mp3` | lock RESOLVED/HUMAN_APPROVED、累積TTS 6 |
| b1b(Adv) | `y_voice_1` | status OK / **Algieba** / 人間承認済(ypl7、attempt6) | 44.36秒(組立timeline) | 821f2c180ec0… | `audio/adv_16.mp3` | lock RESOLVED/HUMAN_APPROVED、累積TTS 7 |

この2本から派生する組立・公開物は全て再作成(TTSは2 segmentのみ): `a2/assembled/Family_Y_REDELIVERY_FEE_A2.wav`、`b1b/assembled/Family_Y_REDELIVERY_FEE_B1.wav`、`pages/audio/std_18.mp3`・`adv_16.mp3`・`std_full.mp3`・`adv_full.mp3`(+timeline変更に伴う後続位置)、`pages/index.html`、`final_manifest.json`。Voice 1の声を含む旧候補物(`*/hr_adopt_prep/voice1_candidates/take1-3`、`pages/audio/v1cand_*.mp3` 8本、`hr_listening/`、`user_test/family_y_production_redelivery_fee_01/listening/`の3 mp3)は**Algieba**であり、完成版ページには載せない(PLAN_01 §3)。

## 3. 再利用候補(Voice 2/3・導入・Comment・Closing・KP・定型音声)

全て status OK、wavのsha256が記録と一致(`inventory_01.json`の`wav_sha_matches_record`)。a2 `preview`のみresults entryに`path`が無く(STOPPED+人間承認)、`narration/preview.wav`のshaで承認記録(`6986099231…`)と照合する設計。

| level | segment(voice/長さ) | 再利用 | 障害の有無 |
|---|---|---|---|
| a2 | topic_intro(Aoede 4.2)/japanese_title(3.41)/comment_1(6.07)/**comment_2(9.84。Stdは正規構成)**/comment_3(9.65)/y_lead(22.34)/y_intro_1〜3(4.69/6.99/7.62)/y_closing(41.45)/y_voice_2(Zephyr 51.58)/y_voice_3(Schedar 52.41)/KP kp1-3 en+ja meaning/定型10本 | 可 | §4で現コードのGateを実測しPASS |
| a2 | preview(STOPPED、ユーザー承認attempt5) | 可 | 承認はtext sha照合(`er003_v1_n3_01_assemble.py:132-137`)。Voice 1変更と無関係なので承認を残す |
| b1b | topic_intro/preview/comment_1/comment_3(Charon)、y_lead/y_intro_1〜3/y_closing(Aoede)、y_voice_2(Zephyr)/y_voice_3(Schedar)、KP kp1-3 en/explanation/phrase_repeat、定型9本 | 可 | 同上 |
| b1b | comment_2(Charon 00132a41…) | **使わない** | 旧成果物。組立・ページ・manifestから除外済み(COMMENT2_WIRING_CHECK_01) |

生成日時(wav mtime。entryに生成時刻フィールドが無いためmtimeで代用): 初回生成=2026-10-25 20:59〜21:30(b1b 20:59-21:14、a2 21:14-21:30)。HR採用で差し替えた y_voice_1/preview=2026-10-26 06:45。Style: results top-level `style_version=v3_j3_kp_meaning_and_explanation_guard`(現行`er019_family_x_audio_production_runner_01.py:910`と**一致**=`_generate_or_reuse`のstyle_version不一致による全再生成は起きない)、model=`gemini-3.8-flash-lite-tts`、tts_backend=`speech_metadata_flash_lite`、StyleProfile=`default`(`er121_family_y_runner_01.py:37`)。a2の`y_lead/y_intro_1-3/y_voice_1-3/y_closing`8本は全て6%減速済(`slowdown_applied=True`)。

## 4. 再利用の障害チェック(現コードを実測。scratch複製・API 0・run dir無編集)

`run_01/{a2,b1b}/{audit,parts.json,key_phrases/keywords_canonicalized.json}`をscratchへ複製し、現作業木のコードで実行:

- `er121_family_y_audio_01.y_style_gate(…,'a2'|'b1b','default')`(Chunk Std拡張`7ca0df0ad`/`d00f41c8b`を含む)→ **a2 PASS / b1b PASS**(`y_body_blocked=[]`、`x_gate_blocked_after_filter=[]`)。run_01の最終gateは10-26 09:50でChunk Std拡張commit(15:32/16:11)より前だったため、拡張後コードでの再確認が必要だった項目をここで解消。
- `er003_v1_n3_01_assemble.verify_episode_audio_validation_gate`(`_segment_missing_mandatory_a2_slowdown`=L239、`_segment_asset_hash_stale`=L212、呼出=L490/494/505)→ **A2 PASS / B1 PASS**(article_textは`translate/{lv}.md`の`canonical_body`)。Voice 1以外は現行Gate要件(Std減速必須・asset hash一致・disfluency QA・構造完全性)を満たす。
- Std減速必須(`check_std_slowdown` `er121_family_y_audio_01.py:651-664`)はa2全8本が`slowdown_applied=True`で充足。
- Chunk: `chunk_tts_decision.json`はa2/b1bとも不発火(現1段落本文構成を維持する指示と整合)。
- 障害1(要対処): y_voice_1の旧人間承認が再生成を無効化する(§5)。
- 障害2(要対処): 旧Voice 1候補表(Algieba)がページ生成に混入する(`voice1_candidates_aux_html` `er121_family_y_audio_01.py:1111-1135`。`hr_adopt_prep/voice1_candidates/take*/result.json`があれば「現行(採用済み)+候補」表を出す)。公開済みページにも`v1cand`が混在(grep 1行/8 mp3)。
- 障害3(要対処): KP declarationの`scope.run`がrun_01の絶対pathに束縛(`er119_kp_human_review_01.py:406,422`)。run dirを別名複製すると宣言が不一致になり得る(PLAN_01 §1)。

## 5. 重要所見: 旧人間承認がPuck再生成を止める/誤通過させる

- 事実(実行確認): `er011_human_review_lock_01.check_before_generation`(L299-341)は`human_approved_segments.json`に当該segment+同一canonical textがあれば`proceed=False, status=HUMAN_APPROVED`(「再生成には該当しません」)を返し、TTS/ASRを**0 callでスキップ**する。scratchでrun_01の承認JSONを使い、a2/b1b両方で`proceed=False HUMAN_APPROVED`、`y_voice_1`承認を除くと両方`proceed=True`を確認(同一関数の直接呼出、API 0)。
- 帰結(コード読みによる推論・未実行): 承認を残したまま`y_voice_1`を要求Voice=Puckで再実行すると、(1)生成されず`HUMAN_REVIEW_LOCKED`の空結果が返り、(2)`er121_family_y_audio_01.py:492`(b1b)/`:606`(a2)(HEAD行)が`y_tts_voice_requested="Puck"`を**無条件に刻印**し、(3)Gateは`_segment_gate_status`(`er003_v1_n3_01_assemble.py:132-137`)がtext shaのみで`HUMAN_APPROVED`と判定して通過し得て、(4)ディスク上の旧Algieba wavで組立される恐れがある。Voice刻印が実Voiceを保証していない。
- 承認原文の範囲: `a2|b1b/audit/ypl7_user_approval_record_y_voice_1.json`の`scope`=「this single segment / this attempt only; NOT a general ASR/QA exemption」。Puckは別attemptなので旧承認の適用外=承認を残す理由は無い。
- 分類: **修正へ進む**(承認済みscopeおよびユーザー指示3章「retry/regeneration/resumeでも旧Voiceが復活しない」と、実装[text sha照合のみ]の乖離=PM_GOVERNANCE 11-8範囲内の不具合是正)。次委任案: 委任_02の前段で(a)run dir運用での承認除去(PLAN_01 S3)と(b)最小コードguard案(生成結果の`voice`≠要求Voiceなら`y_tts_voice_requested`を刻印せずSTOP)をoffline testで固定。コード編集は並行Agent(VOICE-TABLE)の`er121_family_y_audio_01.py`編集完了後に行う(競合回避)。

## 6. Human Review確定内容の所在(再利用対象・変更不可)

- **音声HR(ユーザー承認3 segment)**: a2 `preview`(attempt5、2026-10-26T06:45:07)、a2 `y_voice_1`(attempt5+6%減速、06:45:15)、b1b `y_voice_1`(attempt6、06:45:11)。記録=`run_01/{a2,b1b}/audit/{human_approved_segments.json,ypl7_user_approval_record_*.json,review_lock_state.json}`、原文=`docs/pm/delegation_log/2026-10-26_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_E1_APPROVAL.md`。**y_voice_1の2件はAlgieba音声への承認でありPuck音声には引き継がれない**(§5)。再利用対象はa2 `preview`の承認のみ。
- **KP/Vocab(er119系)**: `run_01/key_phrases/{a2,b1b}/kp_selection_final.json`・`kp_human_review.json`。`review_status=UNREVIEWED_AUTO_ADOPTED`(`declare_absent_cli`による「Fable代行(Sonnet実行)」のHRなし宣言、declaration_id d_bf821f18b541、理由=E-1のHRなし経路evidence取得)。a2 KP=[p_9f42c71603, p_cae22ed992, p_49a03b6ebd](make an effort / end up getting it / take up)、b1b KP=[p_4e11d37d8a, p_58e94a0d31, p_9bae6da75f](sit right with someone / take the trouble / on top of)+vocab 5(+p_36eda7a782, p_27797b97e2)。final_redundancy_qa=REDUNDANCY_PASS。
- **文法Part 2(Adv)**: `run_01/study_text/{grammar_human_review.json,part2_result.json}`、status=`UNREVIEWED_AUTO_ADOPTED`(d_42edcb6d9e37、auto_top1 `g1de62b0de2`「asを用いた比較」)。
- **事実**: ユーザー指示2章の「Human Review結果」のうち、KP/Vocab/文法は人間が選んだ結果ではなく**自動採用**。人間が確定したのは音声HR 3 segmentのみ(うちVoice 1の2件は無効化対象)。

## 7. 判断候補

- KP/Vocab/文法が`UNREVIEWED_AUTO_ADOPTED`のまま完成版に載ることの扱い: 分類=**B寄り(承認範囲内で自己解決可)**。根拠: ユーザー原文は「既存の確定済み記事本文・構成・3人の人物像・Human Review結果を最大限再利用」(`_USER.md` §2)で、ユーザーはE-1ページ(KP含む)を試聴評価済み(CURRENT_SPEC「ユーザー評価良好」)。変更しないのが最小。ただし最終報告では「人間確定」ではなく「自動採用のまま試聴評価済み」と正確に記載する。
