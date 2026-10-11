# TARGET_FLOW_DESIGN_01 — 目標フローとの仕様差分設計(設計案のみ。実装・Production変更なし)

管理ID: FAMILY-X-EN-ASR-CONFIRM-RETRY-REDESIGN-01 委任_01 / 2026-10-11
Status: **設計案(DESIGN_PROPOSAL)。`APPROVED_FOR_PRODUCTION` ではない。** 本設計は「新しい構造・処理フロー」に該当するため、実装前に **Opus独立技術レビュー(Gate 条件A、必須)** が必要(`docs/pm/PM_GOVERNANCE.md` 11-3節)。本委任ではOpusを起動していない(実行層は他Agent起動禁止)。Fableが手配する。

## 1. 目標フロー(ユーザー指示の再掲)
```
[初回TTS] → Primary ASR ─PASS→ 完了(Secondary不要)
              │NG
              ▼
          Secondary ASR ─PASS(既存安全条件内)→ 完了(救済)
              │両NG
              ▼
          [再生成①(同一Prompt)] → Primary ─PASS→ 完了
              │NG → Secondary ─PASS→ 完了
              │両NG
              ▼
          [再生成②(同一Prompt)] → Primary ─PASS→ 完了
              │NG → Secondary ─PASS→ 完了
              │両NG
              ▼
          Human Review
```
確定要件: TTSは最大3回/初回=再生成①=②は同一Prompt(voice・model・backend・Style・速度・原稿その他)/minimal fallback不使用/Local Rewriteは通常retryから除外/数値・否定・重要語欠落・時制等の真の内容誤りは見逃さない/「Promptだけ同じで別経路でStyle/modelが変わる」状態を残さない。

## 2. 現行との差分(項目別)
| # | 項目 | 現行(`main`) | 目標 | 差分の性質 | 再利用できる既存機構 |
|---|---|---|---|---|---|
| 1 | 生成回数 | A2: 標準2+fallback1(+LR1)×減速外側ループ最大3周(理論12)。B1B: 3(+技術fallbackで最大6) | 最大3 | **構造変更**(外側ループ・fallback・LRの除去/統合) | `PRODUCTION_MAX_TTS_ATTEMPTS=3`(er011_human_review_lock_01.py:80) |
| 2 | Prompt | 3回目が別Prompt(A2 fallback)/技術失敗時別Prompt(B1B) | 3回とも同一 | 経路の削除+同一性検証 | B1B `news_tail_fix` は既に3回同一Prompt(L128,152) |
| 3 | Primary NG→Secondary | 英語は entity/homophone の UNCERTAIN のみ(最大Primary#2+Azure×2)。TCMは即再生成 | 全Primary NG(除外条件を除く)で Secondary 1回 | **新ゲート**(JA SCG と同型) | JA SCG(`er007_ja_secondary_asr_01.py:77-330`)の設計・除外条件、`get_full_text_via_azure_stt_with_phrase_list`(`er006_secondary_asr_01.py:69`) |
| 4 | Primary PASS時のSecondary | fallback/LR再TTSでは必須(force_secondary) | 不要 | force_secondary経路の消滅(fallback廃止に伴う) | — |
| 5 | Secondary PASSの扱い | 救済条件が分散(CMU Case A、Tier3、CS層、cascade) | 1回のSecondary転写で既存安全条件内の救済 | **既存救済の統合** | Tier3 `corroboration_supports`、CS層 `classify_connected_speech_equivalence`、CMU `entity_span_arpabet_match` |
| 6 | 減速後検証 | Primary 1回のみ、NGで全体再生成 | 「TTS最大3回」を破らない | **設計変更**(§3-3) | `apply_a2_slowdown_postprocess` |
| 7 | Local Rewrite | 3回NG後に自動発火 | 通常retryから除外 | 呼出元の接続を外す(機構は残す) | `run_local_rewrite_recovery`(OPEN-256 CLOSED) |
| 8 | cool-down | attempt3前に固定600秒(5role+CS層) | 未指定 | **要判断** | `maybe_cooldown_before_attempt` |
| 9 | 証跡 | fallback/減速後の転写・cascade_stepsが未保存、queueが重複排除 | 全attempt・全Secondaryを保存 | 追記設計 | `save_tts_attempt_audio`(er011:489-) |
| 10 | Human Review | STOPPED/UNCERTAIN→Review Lock(累計TTS15/ASR60) | 3回両NG→HR | 条件の明確化のみ | Review Lock一式(無変更) |

## 3. 設計詳細

### 3-1. 同一Prompt固定と「別経路でStyle/modelが変わる」状態の排除
- **Prompt fingerprint** を導入: `sha256(model_id + backend + voice + final_style_string(発音hint追記後) + tts_text + trim_margin)`。attempt 1/2/3 で同一であることを実行時にassertし、`tts_generation_results.json`・attempt json・`review_lock_state` に記録する。
- 除去する別Prompt経路: (i) A2 `generate_english_segment_with_fallback` の fallback ループ(crosslevel:158-259)と Local Rewrite 再TTS(L381-398、fallback関数を再利用しているため)、(ii) B1B 2関数の「技術的fallback」(`news_tail_fix.py:172-182`、`voice01.py:172-213`)→ **同一Promptでの再試行(attemptを消費)**に変更、(iii) `FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]` の参照は新モードでは到達不能にする(定数は残す。Key Phrase・JAは別経路)。
- 発音ヒント(`resolve_and_augment_en_style_prefix`)は関数冒頭で1回だけ算出されるため attempt 間で変わらない(repro01:291-296)。fingerprint には hint追記後の最終文字列を使う。
- Standard の「減速指示連結」も `style_prefix_override` に含まれるため3回同一(`er019 _role_style_slower`)。6%の事後stretchは決定論的で Prompt ではないが、**減速の有無は全attempt共通**であることを fingerprint 付随情報に記録する。

### 3-2. Primary NG → Secondary 確認ゲート(英語版SCG、案)
- 名称案: `EN_ASR_CONFIRM`(Feature Flag `EN_ASR_CONFIRM_ENABLED`、既定OFF。承認後にON。環境変数で即時停止可。`cascade_enabled=False` 時は不実行 — SCGと同型)。
- **発火**: Primary の `should_pass=False` かつ下記「除外条件」に非該当。attempt を**消費しない**(確認のみ)。
- **除外条件(Secondaryを呼ばず再生成)**— 「真の内容誤りを見逃さない」ための防波堤:
  1. `protected_check` 不合格(数字・否定の不一致)。Tier1の値等価で救われない数値差は再生成。
  2. 類似度<0.4(`TTS_FAILURE`)または `length_ok=False`(幻覚追加・反復の疑い)。
  3. Disfluency / Repetition QA の NG(ASR転写で救済すべき性質ではない)。
  4. Primary転写が None(ASR障害)→ §3-9 の「ASR技術再試行」へ。TTS技術失敗(無音・異常長)は再生成。
  5. 非ラテン文字主体(言語ドリフト、OPEN-222型)→ Secondaryでも救えないので再生成。
- **Secondary 実行**: 同一音声を 1回(Primary#2・Secondary#2 は廃止: Coffee で Primary#2=同文・Azure#2=同文だった)。**Phrase Listなし**を推奨(SCG同様。Phrase List は Azure を原稿綴りへ寄せ、誤PASSの余地を作る — CS:1994 の不採用理由)。ただし固有名詞では Azure が Phrase List なしだと綴りが揃いにくい → D-2 でユーザー判断。
- **PASS条件**(Secondary転写を **同一のValidator** `classify_asr_match(canonical, secondary_text, segment_id)` で判定): 分類が `EXACT_MATCH / NORMALIZED_MATCH / TRANSCRIPT_STYLE_NORMALIZED_MATCH / NUMERIC_EQUIVALENCE_MATCH`(厳格集合)。`HIGH_SIMILARITY_SAFE`(benign複数形等)を含めるかは D-3。`CONNECTED_SPEECH_*` / `SECONDARY_ASR_CORROBORATED_MATCH` / `HOMOPHONE_*` は**この確認ゲートでは自動PASSにしない**(既存の個別機構で扱う、§3-2b)。
  - 無料検証(FREE_VERIFICATION §4-7): 真の内容誤り16種(数値3・否定2・時制2・重要語4・文脱落/追加/反復4・entity1)を Secondary転写に見立てて流すと**誤PASS 0/16**、benign 5/7 を救済。ただしこれは Validator側の安全性であり、**Secondary ASR自身が原稿へ「自動補正」する性質**(LM寄り)は含まない(§5 リスクR-1)。
- **Secondary エラー/空/タイムアウト/途中キャンセル** = UNAVAILABLE = NG扱い(従来どおり再生成)。
- **証跡**: `confirm_info` = {primary_text, primary_class, secondary_provider, secondary_text(全文), secondary_class, decision, reason, phrase_list, audio_seconds, est_cost_jpy, wall_seconds, timestamp}。attempt jsonに `cascade_steps`・`confirm_info` を必ず保存。queue の重複排除キーに **attempt番号/音声sha256** を追加(F-3対策)。

#### 3-2b. 既存の部分救済機構との整理(競合・重複)
| 既存機構 | 現行の役割 | 新モードでの扱い(案) |
|---|---|---|
| CMU Case A / homophone 即PASS(0 call) | Primary 単独で entity/homophone を ARPAbet 比較 | **維持**(追加費用0。確認ゲートより前に評価) |
| Primary#2 + Secondary#1,#2(entity/homophone cascade, :723-833) | 同一音声の再転写 | **確認ゲートに置換**(Primary#2/Secondary#2は廃止) |
| Tier3 corroboration(plural_only/entity_only, :593-674) | Azure 1回の corroboration | **確認ゲートの Secondary 転写を共有**して同判定を行う(Azure二重呼出を避ける)。救済は warning付き |
| CS Equivalence Layer(音韻カテゴリA〜G, :542-591) | Azure + local whisper の corroboration | 同上(Secondary転写共有。local whisper は無料のため維持可) |
| 非ラテン cascade(Key Phrase, :676-697) | Key Phrase 専用 | **無変更**(対象外) |
| force_secondary(:699-721) | fallback経路 | 新モードでは到達不能(経路ごと廃止) |

### 3-3. 6%減速後の検証と「TTS最大3回」(最重要の構造論点)
現行 F-1: 減速後Primary-only再検証NG → 外側ループが標準2+fallback1(+LR)を再実行。目標の「最大3回」と両立しない。
- **案B(推奨)**: 各TTS attemptを「生成 → 原音声を Primary→(NG→Secondary) → PASSなら6%stretch → stretch音声を同じ Primary→(NG→Secondary)で検証」までを**1 attemptの内部**に畳み込む。stretchNGなら**そのattemptを不合格**とし次attemptへ(3回共有)。外側ループ(`max_slowdown_attempts`)は廃止。stretchは決定論的なので、原音声がPASSでstretch音声のみNGの場合、再生成しても同じ現象が再現するとは限らない(OPEN-76「再生成で解消」)が、**予算は3回で打ち切る**。
- **案C(代替・仕様変更を伴う)**: stretch後の再検証を sanity(長さ・clipping・Primary のみ。NGでも**再生成しない**)に格下げし、原音声の検証結果を正とする。Coffee 初回(原音声PASS)は救われる。ただし CS:1916(OPEN-76)の承認仕様(「post-process後にASRで再検証、不一致なら取り直し」)を変更するため **ユーザー承認必須**。
- 実装影響: `generate_a2_segment_with_slowdown`(n3_tts:197-268)+`apply_a2_slowdown_postprocess`(L117-194)+`generate_english_segment_with_fallback` の attempt ループへ post-verify hook を追加。Advanced(B1B)は減速post-processなし → 影響なし。
- 注: 無料検証で、Coffee初回音声を6%stretchしても local whisper small は NUMERIC_EQUIVALENCE_MATCH、medium は UNCERTAIN(`People`脱落)で、**stretchが内容を壊した証拠はない**(FREE_VERIFICATION §4-2)。

### 3-4. minimal fallback の廃止
- A2: `generate_english_segment_with_fallback` に `fixed_prompt_mode`(新引数、既定False=現行互換)を追加し、True時は `standard_attempts=3`・fallbackループ非実行・LR非実行。`PRODUCTION_STANDARD_TTS_ATTEMPTS=2`/`MINIMAL=1` 定数は**変更しない**(他経路が参照)。新定数 `EN_FIXED_PROMPT_TTS_ATTEMPTS=3`(`PRODUCTION_MAX_TTS_ATTEMPTS` と等値assert)。
- B1B 2関数: 技術的fallbackを同一Prompt再試行に変更(同attempt内の2回目TTSを廃止)。
- 影響先: A2のみがfallbackをユーザー可視のStyle不連続の原因として持つ。JA(`generate_a2_japanese_with_fallback`/`generate_charon_japanese`)・Key Phrase(Minimal/English lock)・共有殻は**対象外**(§3-9)。
- minimal fallback が当初解決しようとした問題("Model tried to generate text…" 400 INVALID_ARGUMENT、crosslevel:50-59)は、**Flash-Lite speech_metadata backend では role Style が短く(長いENGLISH_STYLE_PREFIXではない)**、発生条件が異なる。過去データ(FREE_VERIFICATION §4-3)でFlash-Lite時代の fallback 利用は narrative5 の 7/160 calls(4.4%)、うち合格2・不合格5(5件のうち3件は A/B Trial arm 由来)。**固定Prompt3回で同現象が再発した場合は同じPromptで3回失敗しHRになる**=リスクR-4。

### 3-5. Local Rewrite の通常retryからの除外
- 呼出点: `crosslevel:252-258,282-288`、`news_tail_fix:290-324`、`voice01:291-319`。新モードでは `LOCAL_REWRITE_IN_AUTO_RETRY_ENABLED`(新flag、新モード既定False)でガード。`er020.run_local_rewrite_recovery` 本体・OPEN-256の全文性検証は**無変更で残す**。
- 位置づけ案: **Human Review 到達後に、人間が明示的に起動する回復オプション**(本文書き換えを伴うため自動では行わない)。
- 除外の根拠(本調査): (i) Primary PASS・Secondary NG 型の失敗では NG span 特定が誤る(F-4)、(ii) 本文を変更する(Fact/文脈リスク、QA 7 Gate・LLM費用・約3分)、(iii) 新フローでは Secondary が先に救済する。
- リスク: 現行LRで救えていた事例が救えなくなる(FREE_VERIFICATION §4-4 で過去の成功件数を集計)。

### 3-6. cool-down(10分)
- ユーザー目標に記載なし。現行はattempt3の直前のみ(5role+CS層ON、`er020:63-90`)。新フローでは再生成②の前に置くかを **D-5** で判断。観察: 過去の「cool-down後の3回目」が通った事例 4件(family_x_b3 の full_story_part1 ×3 とmeta part3)があるが、同一Promptの2回目と比較した対照はなく、効果は未確定。cool-down は所要時間を +10分/segment(HR近傍のみ)。

### 3-7. Human Review 条件
- 3回目で Primary・Secondary とも不合格 → `STOPPED` を返し Review Lock が `HUMAN_REVIEW_REQUIRED`(現行どおり)。累計上限(TTS15/ASR60、er011:68-69)は無変更だが、**TTS計数は実TTS呼出基準へ修正**(現行はLR再TTSや外側ループ分を過少計上: attempt_history 15:35:44 は累計4、実際は5)。
- queue への登録は **attempt ごとの Primary/Secondary 全転写**を含める。

### 3-8. 初回/retry/fallback/regeneration/resume の整合・Dangling Reference
- `_generate_or_reuse`(er019:405-432)の再利用条件は `style_version` と `canonical_text` のみ。**Promptが変わっても(Style値だけ変えて version を上げ忘れると)古い音声を再利用する**。対策案: 再利用条件に `prompt_fingerprint` 一致を追加(未記録の旧cacheは再利用不可=再生成)。
- Master Store(共有殻)再利用は別機構。新モードは narrative5 の本文/コメント等のみ対象で共有殻には触れない。ただし worktree で発生した `stored_audio_file_missing` による殻の再生成(Coffee `num_three`)は別問題。
- Dangling Reference Check(`er053_dangling_reference_check_01.py`)を実装後に実行し、新flag(`EN_ASR_CONFIRM_ENABLED`、`LOCAL_REWRITE_IN_AUTO_RETRY_ENABLED`、`fixed_prompt_mode`)の「定義だけで配線されない」を防ぐ(本委任は設計のみのため未実行)。
- resume: `REGENERATE_APPROVED` 後の再実行は attempt 計数が segment 単位でグローバルに継続(attempts/ のファイル採番, er011:489-)。新モードでも Lock 上は3回予算が新たに始まる(人間承認によるため仕様どおり)。

### 3-9. 条件別の例外と適用範囲
| 条件 | 現行 | 新フロー(案) | 例外の要否・理由 |
|---|---|---|---|
| 数値・否定・時制・重要語の差(TCM) | 再生成 | 数値/否定=Secondary呼ばず再生成。時制/重要語(非entity内容語差)=Secondary確認(PASSなら救済、Validatorが全文照合) | 例外不要。ただし時制・重要語は **Secondary転写が原稿へ寄る**リスク(R-1) |
| 固有名詞・同音異義語 | CMU Case A即PASS、cascade | CMU Case A維持、残りは確認ゲート | 例外不要 |
| Connected Speech | 3パターン/CS層 | 維持(Secondary共有) | 不要 |
| 両ASR誤認識(OPEN-257、3系統同一誤聴) | cascade→HR | 3回再生成→HR | 例外不要(HRで人間確認)。Trial候補(OI:759 B1〜B4)は別管理 |
| ASR障害・転写不能 | Primary None=TTS_FAILURE扱いで再生成 | **ASR技術再試行(同一音声、最大2回、attempt非消費)**を新設。Secondary不可は NG扱い | **例外あり**: 音声不良と区別するため。リスク: ASR費用微増 |
| TTS技術的失敗(無音/異常長) | B1B: 同attempt内に別Prompt fallback / A2: attempt消費 | 同一Prompt再試行(attempt消費) | 不要。技術fallback廃止 |
| Key Phrase(英語) | Minimal2 + English lock2 = 4回 | **対象外(現行維持)** | **例外あり**: ユーザー正式決定済みの専用構成(repro01:633-635)。短語で別Prompt前提。統一は D-7 |
| 共有殻 num_* / welcome | Master Store再利用、生成時は標準経路 | 対象外 | OPEN-222(極短語言語ドリフト)はSecondaryで救えない |
| 日本語 | JA SCG(Primary TCM→Azure1) | 対象外(既に目標型) | — |
| topic_intro / comment / preview / in_one_line | 標準2+fb1 / 3同一 | 5role全て対象 | 短文は Azure 秒課金が小さい |
| Advanced Full Story | 3同一Prompt | 確認ゲートのみ追加 | 変更小 |

## 4. Secondary ASR 候補の比較(D-1 の材料)
| 候補 | 独立性 | 費用/call | 所要 | 観察された癖 | 備考 |
|---|---|---|---|---|---|
| Azure STT(現行) | 別ベンダー | **$1/音声時間 → 50秒で約¥2.2、29秒で約¥1.3** | 12〜24秒 | `raw bean→robbing`、`M→am`、`two` 挿入、語脱落、文入れ替え(queue 67行・Coffee) | 偽NGが多い。Primaryより悪い傾向 |
| local faster-whisper medium(無料、CPU) | 別モデル系 | **¥0** | 要実測(CPU) | Coffee 5音声中4音声で原稿一致、`People`脱落1(減速音声・原音声) | LM寄りの自動補正リスクR-1、モデル同梱依存 |
| local faster-whisper small | 同上 | ¥0 | 速い | LR音声で Azure と同じ `robbing` | 精度やや低 |
| 2系統投票(例: Azure + local) | 高 | Azure費用+0 | Azure待ち | SCG は Whisper 2-of-3 を**未採用**(CS:1994) | 誤PASSには強いが救済率は下がる |
Coffee の NG take 4本(標準1・標準2・fallback・LR)での結果: Azureが実際に確認したのは3 take(標準2・fallback[forced]・LR[forced])で、**救済 0/3**(全てTCM)。local medium は4本全てが原稿一致(NORMALIZED_MATCH)。**費用はAzureが支配的**(この1 segmentでAzure ¥8.8 > TTS ¥3.0 + OpenAI ASR ¥1.8 + LLM ¥0.4 の合計 ¥5.2)。

## 5. リスクと防止策
| ID | リスク | 防止策(案) |
|---|---|---|
| R-1 | Secondary ASR が原稿へ自動補正して真の誤読をPASSさせる(Phrase List、LM寄り) | Phrase Listなし、厳格PASS集合、数値/否定は呼ばない、Primary・Secondary転写の差分を証跡に全文保存し**事後監査**、ユーザー最終試聴(CS「最終人間試聴」原則)を維持 |
| R-2 | Azure偽NGで救済率が低いまま費用が増える | D-1(local medium併用)、救済率の事前Trial |
| R-3 | 固定Prompt3回で全NG→HR率が上がる(fallbackの救済機会喪失) | FREE_VERIFICATION §4-3 の下限/上限(完了率 91.9%〜95.6% vs 現行93.1%)を提示。実測は有料Trialで確認 |
| R-4 | "Model tried to generate text" 型の再発 | Flash-Lite backendでの発生率を実測(過去データ上は旧backend事象)。HRで検出可能 |
| R-5 | 外側ループ廃止で 6%減速NG の取り直し機会が減る | 案B/C(D-4) |
| R-6 | LR撤去で救済できていた事例がHR化 | LRを「HR後オプション」で残す |
| R-7 | 既存承認済み仕様(CS:1692/1911/1916/1971)との競合 | 仕様変更として扱い、CURRENT_SPEC更新はユーザー承認後 |

## 6. 変更範囲(実装時、本委任では未実装)
| 区分 | ファイル | 関数/箇所 | 変更 | flag |
|---|---|---|---|---|
| 確認ゲート | `er006_secondary_asr_01.py` | `evaluate_attempt_with_cascade_detail`(459-864)に `confirm_mode` 分岐、`get_full_text_via_azure_stt…`(69)に Phrase Listなし呼出口 | 新分岐追加(既存分岐は無変更) | `EN_ASR_CONFIRM_ENABLED` |
| 固定Prompt | `er003_v1_crosslevel_audio_02_common.py` | `generate_english_segment_with_fallback`(78-289) | `fixed_prompt_mode` 引数、fallback/LR非実行、fingerprint記録 | `fixed_prompt_mode`(呼出元から) |
| 固定Prompt | `er003_v1_sing01_news_tail_fix.py`/`er003_v1_sing01_voice01_generate.py` | 172-182 / 172-213 | 技術fallback→同Prompt再試行(新モード時) | 同上 |
| 減速 | `er003_v1_n3_01_tts_generate.py` | `generate_a2_segment_with_slowdown`(197-268)、`apply_a2_slowdown_postprocess`(117-194) | 外側ループ廃止、post-verify hook化(案B) | 新モード時のみ |
| LR | 上記3関数の LR呼出 | 252-258,282-288 / 290-324 / 291-319 | ガード追加 | `LOCAL_REWRITE_IN_AUTO_RETRY_ENABLED` |
| 計数/証跡 | `er011_human_review_lock_01.py`、`er006_secondary_asr_01.py:_log_human_review` | `record_outcome`、重複排除キー | 実TTS計数、attempt別queue | — |
| resume | `er019_family_x_audio_production_runner_01.py` | `_generate_or_reuse`(405)、Standard/Advanced呼出(559-671,825-990) | fingerprint一致条件、`fixed_prompt_mode` 渡し | `FAMILY_X_VARIABLE_ROLE_STYLE_VERSION` bump |
| テスト | `er003_test_*`/新規 | 新モードのunit/回帰 | 追加(既存挙動は既定OFFで不変) | — |
| 既存SSOT | `CURRENT_SPEC.md`(1692,1911,1916,1971)、`DECISION_LOG.md`、`OPEN_ITEMS.md` | 仕様更新 | **ユーザー承認後**(本委任では編集しない) | — |

## 7. ユーザー判断が必要な点(USER_DECISION_REQUIRED 候補)
D-1 Secondary ASR の選択(Azure / local medium / 併用)。D-2 Phrase List の有無。D-3 PASS集合に `HIGH_SIMILARITY_SAFE` を含めるか。D-4 6%減速検証の扱い(案B/案C=OPEN-76仕様変更)。D-5 cool-down(10分)の継続。D-6 Local Rewrite の位置づけ(HR後オプション/完全撤去)。D-7 Key Phrase を新フロー対象外とするか。D-8 TTS技術的API再試行・ASR技術再試行をattempt外とする定義。D-9 適用範囲(5role一斉 / Full Storyのみ先行)。D-10 Azure費用の許容(現状 segmentあたり ¥0.3〜0.4 追加見込み、QCD §8)。D-11 既存Tier3・CS層・entity cascadeとの統合方針。いずれも**未承認の仕様候補**であり、本委任では実装していない。
