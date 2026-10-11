# COFFEE_NG_ROOTCAUSE_01 — Coffee Standard `full_story_part2` が Human Review に至った根本原因

管理ID: FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01 委任_01 / 2026-10-11 / 有料API 0
証跡(read-only snapshot、sha256付き): `evidence_snapshot/`(`MANIFEST.sha256`、`SNAPSHOT_TIME.txt`=2026-10-11T19:32:39+09:00)。元は worktree `eigo-radio-tone` の `er019_output/family_x_audio_production_wiring_01/coffee_prices__run_e_tone_01/a2/…` と `er006_output/audio_retry_cascade_prod_01/human_review_queue.jsonl`、`er011_output/local_rewrite_recovery/…`。worktree内ファイルは一切変更していない。

## 0. 結論(先に)
1. 最終NGの直接原因は**単一の「音声が壊れていた」ではない**。5回のTTSのうち、(a) 1回目は Primary PASS だったが**6%減速後のPrimary-only再検証**でUNCERTAINとなり**捨てられた**(retry制御設計)、(b) 標準1回目は OpenAI が `showed→show` と聞いた(真の読み違いか Primary誤認かは**未確定**)、(c) 標準2回目は **Validatorの notation 偽NG(`US`↔`U.S.` + `cost`↔`costs`)+ Azure の誤認識(`raw bean→robbing`、文の入れ替わり)**、(d) fallback は **Primary PASS・Azure forced NG**(Azure転写は未保存)、(e) Local Rewrite は**無関係な箇所を書換え**、最終は **Primary PASS・Azure NG**。
2. 独立の第三者(無料のローカル faster-whisper small/medium)は、標準1・2回目・fallback の3音声を**全て原稿と一致(NORMALIZED_MATCH)**と転写した。**3本とも「人間が聞けば合格だった可能性」が高い**(確定ではない。要・人間の耳)。最終LR音声のみ、Azure と local small が `robbing` と聞き、OpenAI と local medium は `raw bean` と聞いた(本物の曖昧さの可能性)。
3. 主因の分類: 真の音声不良=**確認できたものは0件(未確定が2件: 標準1回目、LR音声)** / ASR誤認(Azure)=3件 / Validator不具合(notation偽NG)=1件 / retry制御設計不備(減速後Primary-only再検証で再生成、LR対象span誤り、証跡欠落)=3件。

## 1. 時系列(raw_usage_log UTC→JST、attempt json、review_lock、queue より再構成)
| JST | 事象 | 根拠 |
|---|---|---|
| 15:10:47 | segment開始(TTS#1 リクエスト) | raw_usage_log |
| 15:13:02 | TTS#1 完了(135.6s)= file `attempt1_customf1837a73.wav`。Style=F1.5+減速指示(標準) | attempt1 json |
| 15:13:05 | Primary ASR → **NORMALIZED_MATCH**。Repetition QA(方式A/D/D')も flagged=false | attempt1 json `repetition_qa_evidence` |
| 15:13:34 | attempt json 保存。直後に `apply_a2_slowdown_postprocess`(6%減速 5.977%)→ **Primary ASR 1回のみ**(15:13:36) | n3_tts:117-194、raw_usage_log ASR#2 |
| 15:13:36 | 再検証 = **ASR_VALIDATION_UNCERTAIN**(`slowdown_attempts_log`)→ status=STOPPED → 外側ループ(max 3)が **新しい3回予算で再TTS** | tts_generation_results.json `slowdown_attempts_log`、n3_tts:248-266 |
| 15:16:25 | TTS#2(168.9s)= file attempt2 = 標準1回目。Primary → **TRUE_CONTENT_MISMATCH**(`show coffee costs`)。`cascade_invoked=false`、Secondaryなし、即再TTS | attempt2 json |
| 15:18:22 | TTS#3(113.9s)= file attempt3 = 標準2回目。Primary#1 UNCERTAIN → Primary#2 UNCERTAIN → Azure#1 TCM(15:18:48)→ Azure#2 TCM(15:19:10)→ Human Reviewログ(15:19:10)、`stop_retrying=True` | attempt3 json、queue row 1 |
| 15:19:10–15:29:10 | **10分cool-down**(600.003s)→ fallback | tts_generation_results `cooldown_events` |
| 15:31:42 | TTS#4(152.1s)= file attempt4 = fallback(**[branch]では承認Style維持**)。Primary(15:31:45) **PASS**。Azure forced(15:32:07)→ **TRUE_CONTENT_MISMATCH** | attempt4 json、raw_usage_log |
| 15:32:24–15:32:52 | Local Rewrite: Luna 候補生成(17.2s)+QA(13.9s)。NG span=`us`↔`u s` | local_rewrite_recovery json |
| 15:35:18 | TTS#5(159.4s)= LR再TTS(最終 `full_story_part2.wav`)。Primary(15:35:20) **PASS**、Azure forced(15:35:44)→ **TRUE_CONTENT_MISMATCH**(`raw bean`→`Robbing/Robbins`)→ queue row 2 → `HUMAN_REVIEW_REQUIRED` | queue row 2、review_lock_state |
実測総数(この1 segment): **TTS 5回**(Lockの記録は累計4=LR再TTSは数えない)、OpenAI ASR 7、**Azure 4(197.8s)**、LLM 2、所要 **24分57秒**。

## 2. 質問別の根本原因
### (1) 減速前の初回TTS: Primary ASR PASS なのに次 attempt へ進んだ理由
- **直接原因**: A2本文は `generate_a2_segment_with_slowdown`(n3_tts:197-268)が「通常ペース生成 → 6% time-stretch → **Primary ASR 1回のみ**で再検証」を行い、NGなら `max_slowdown_attempts=3` の**外側ループ**で `generate_english_segment_with_fallback` を丸ごと再実行する(L251-266)。1回目の再検証が `ASR_VALIDATION_UNCERTAIN` だった(`slowdown_attempts_log=[{attempt:1,status:STOPPED,post_slowdown_classification:ASR_VALIDATION_UNCERTAIN}]`)。
- Review Lock は `RESOLVED` を再実行ブロックしない(er011_human_review_lock_01.py:242-252。6%減速retryのためと明記)ので、新たな「標準2+fallback1」予算が与えられた。attempt_history.jsonl 15:13:34 は `RESOLVED`・`tts_attempts_this_call=1`・`asr_calls_this_call=1`(post-slowdown ASRは未計上)。
- **何と聞こえて UNCERTAIN だったか = 証跡欠落**: `post_slowdown_asr_text` は結果dictに入るが、次ループで結果が上書きされ**永続化されない**(F-2)。raw_usage_log にもトークン数のみ。**推定(未確認)**: 標準2回目と同じ notation 偽NG(`US`→`U.S.` + 軽微差)。根拠: (i) 6%減速を**ffmpegで再現**し local whisper で転写すると small=NUMERIC_EQUIVALENCE_MATCH、medium=UNCERTAIN(`People`脱落+`U.S.`)で、減速自体は内容を壊していない、(ii) 標準2回目で同型のUNCERTAINが実際に起きている(§(2)-b)。→ **真の音声不良ではなく、「合格済み音声を再検証で捨てた retry 制御設計(F-1)」が主因**。
- 分類: **retry制御の設計不備(仕様どおりに動作している)**。「TTS最大3回」は外側ループで実際には守られない(本segmentはTTS 5回)。

### (2) Attempt 1・2: Primary/Secondary判定と再生成遷移は仕様どおりか
**仕様どおり**。ただし仕様自体に下記の欠点がある。
- **標準1回目(file attempt2)**: Primary分類を `val.classify_asr_match` で再実行して**再現**(`replay1.py`出力、FREE_VERIFICATION §4-1): `TRUE_CONTENT_MISMATCH`、非entity内容語差 `showed→show`(+ `cost→costs` は benign plural で無視、`us→u s` は entity-like)。`_classify_asr_match_core` の `non_entity_diffs` 分岐(val:1068-1094)で TCM。5role+CS層ONだが `cheap_check` が `NOT_A_PHONEME_PREFIX_DROP`(NEVER_ELIGIBLE、本調査で `classify_connected_speech_equivalence` を再実行して確認)のため追加確認なし(er006_secondary_asr_01.py:542-551、:326-328)。`cascade_eligible`(entity/homophone UNCERTAINのみ)に該当せず**Secondaryは呼ばれず**再TTS(L723-728)。
  - 原因分類: **未確定**(真の読み違い=現在形/過去形の取り違え か OpenAI の誤転写)。独立ローカルASR(small/medium)は原稿どおり `showed coffee cost` と転写(NORMALIZED_MATCH)。**目標フローなら Secondary が呼ばれ、ここで救済/確定できた**。
- **標準2回目(file attempt3)**: Primary#1・#2とも `ASR_VALIDATION_UNCERTAIN`。再現: diff は `us`↔`u s` ×3 のみ(`cost↔costs` は無視)で、entity-like(`entity_like_source=['capitalized']`)。**同一音声の `US data` を OpenAI は `U.S. data` と書いた**だけ。単独なら despace 判定で NORMALIZED_MATCH(参考の初回 file attempt1 は `U.S.`/`cost` でそれにより合格)だが、`costs` との同時発生で despace 等価が崩れ(val:986-1007)、entity-like 経路へ(F-5)。→ cascade(`cascade_eligible`=True)で Primary#2(同文)→ **Azure×2: `TRUE_CONTENT_MISMATCH`**。Azure転写: `They estimate robbing prices take at least about nine months to.In US shop prices, the road to a price tag is quite a long journey, the article says. U.S. companies…`(`raw bean→robbing`、文の入れ替え/境界崩れ)。OpenAI と**ローカルwhisper small/mediumは同じ音声を原稿どおり**に転写。
  - 原因分類: **Validator notation 偽NG(F-5)+ Azure ASR誤認(F-6)**。「真の音声不良」の証拠なし。
  - 帰結: Human Review ログ → `stop_retrying=True` → **10分cool-down** → fallback。ここで約13分(cool-down+TTS)を消費。

### (3) Attempt 3(fallback): 原稿とASR転写に差分がないのに NG になった理由
- Primary転写は**原稿と実質同一**(replay: `NUMERIC_EQUIVALENCE_MATCH`、段落改行 `\n\n` が入るだけ)で、Primary は **PASS**。attempt json の `audio_classification=TRUE_CONTENT_MISMATCH` は **Azure forced の分類**(`detail["classification"]` を返すのは `secondary_forced` の cls_s_forced、er006_secondary_asr_01.py:716-721)であり、Primaryの判定ではない。
- 経路: fallback は `_run_a2_minimal_fallback_attempt`(crosslevel:292-355)が `force_secondary=True` で評価 → Primary PASS でも Azure を必ず呼び、**Azure が TCM なら不合格**(L699-721、CS:1911)。ASR転写が一致して見えるのに不合格に見えた理由はこれ。
- **Azure転写は保存されていない**: fallback attempt json は `cascade_steps` を持たず(crosslevel:213-223)、queue は同一wav+同一原稿で重複排除され(er011_human_review_lock_01.py:429-452)、row 1(15:19:10)がある ため追記されなかった(F-3)。raw_usage_log には Azure 呼出(15:32:07、47.72s)のみ。
- 原因分類: **仕様どおり(force_secondary の副作用)+ 証跡欠落**。Azure 誤認識の可能性が高い(local small/medium とも原稿一致)が、Azure転写がないため**断定不可**。欠けている証跡: attempt 4 の Azure転写全文。
- 補足: この fallback Prompt は **[branch] では標準と同一Style**(承認F1.5+減速)。`main` なら `natural, clear, conversational` で声質・速度とも変わる。

### (4) Attempt 4(Local Rewrite再TTS): Primary PASS なのに Azure `raw beans→Robbins` で最終NG
- queue row 2(15:35:44): Primary=NORMALIZED_MATCH、`secondary_forced`(Azure)= `TRUE_CONTENT_MISMATCH`。Azure転写: `…experts spoke with Reuters, they estimate.Robbing prices take at least about nine months… keep Robbins in stock.`。再現: `raw bean→robbing`, `raw beans→robbins`。
- **本物の曖昧さの可能性**: ローカル faster-whisper **small** もこの音声を `robbing prices … keep robbings in stock` と転写(Azureと一致)、**medium** と OpenAI は `raw bean(s)`。2/4 系統が `robbing`。→ 「ASR誤認」と断定できず、**この take で `raw bean` が `robbing` 寄りに発音された可能性**を排除できない(人間の耳で確認要)。ほかの3音声(標準1・2・fallback)は local small/medium とも `raw bean` と転写 = 影響なし。
- **LRの書換え箇所が無関係**: LR は `last_asr_text`(Primary転写)と原稿の最初の差分(`us`↔`u s`)を NG span に選び、`US data → data from the United States` に書換え(local_rewrite_recovery json `ng_span`、`selection.selected.id=2`)。実際の不一致箇所(Azureが誤聴した `raw bean`)は**書き換わっていない**。→ LRはこの失敗パターン(Primary PASS・Secondary NG)に対して**原理的に無効**(F-4)。しかも本文が変更された。
- 原因分類: **ASR誤認 or 真の音声曖昧(未確定)+ LR対象span誤り(retry制御不備)**。

### (5) 各 NG の分類(「真の音声不良 / ASR誤認 / Validator不具合 / retry制御不具合」)
| # | NG | 真の音声不良 | ASR誤認 | Validator不具合 | retry制御/設計 | 確度 |
|---|---|---|---|---|---|---|
| 0 | 減速前の初回(15:13) PASS後に再生成 | 証拠なし(減速で内容は壊れない) | 疑い(Primary再検証) | 疑い(F-5型) | **主因(F-1)** | 設計=確定 / 後二者=推定 |
| 1 | 標準1回目 TCM(`showed→show`) | **未確定** | 疑い(local ×2 は原稿一致) | — | Secondary未実施(仕様) | 低 |
| 2 | 標準2回目 UNCERTAIN→Azure TCM | 証拠なし | **Azure**(確度高: OpenAI/local×2が原稿一致) | **F-5 偽NG** | 10分cool-down消費 | 高 |
| 3 | fallback Primary PASS・Azure forced NG | 証拠なし | Azure疑い(local×2一致、**Azure転写欠落**) | — | force_secondary(仕様)+証跡欠落(F-3) | 中 |
| 4 | LR再TTS Primary PASS・Azure NG | **未確定**(local small も robbing) | 未確定 | — | **LRが無関係span書換え(F-4)** | 低〜中 |

## 3. 欠けている証跡(追記が必要なら後続の有料不要/有料別)
1. 減速後ASR転写(file attempt1→stretched)の OpenAI 転写本文(未保存)。再現には OpenAI ASR 1回(約¥0.07)が必要=本委任では未実施。
2. fallback attempt の Azure 転写全文(重複排除で欠落)。再現には Azure 1回(約¥1.9)が必要=未実施。
3. **人間の聴取**: 標準1回目の `showed`/`show`、LR音声の `raw bean`。音声は公開試聴ページ `user_test/coffee_new_tone_01/part2_review/`(attempt 1〜4+参考)で聴ける。

## 4. この調査から導かれる要点(設計への入力)
- 偽NGの最大要因は **(i) Primary-only の減速後再検証(F-1)**、**(ii) notation 差(F-5)**、**(iii) Azure を最終権威にする forced 確認(F-6)**、**(iv) TCM で Secondary を呼ばない(英語未実装)**。
- 4つの音声のうち3つが、無料のローカルASR(第三の系統)では原稿どおりに転写された。**目標フロー(Primary NG→Secondary)**は(iv)を解消するが、Secondary に Azure を使うと(iii)の誤認識が残り得る(TARGET_FLOW_DESIGN_01 §4 の Secondary 候補比較参照)。
