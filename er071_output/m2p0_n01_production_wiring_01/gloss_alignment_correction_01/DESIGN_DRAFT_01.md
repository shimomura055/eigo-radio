# DESIGN_DRAFT_01 (KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_01A、2026-10-15)

Status: **DESIGN_DRAFT**(設計草案。Opus条件Aレビュー待ち)。コード・Prompt・Gate・config既定値・SSOT・Production は一切変更していない。以下の全項目は「提案」であり、`APPROVED_FOR_PRODUCTION`ではない。新しい品質条件(追加語→日本語span対応の機械検査等)も、ユーザー承認までProductionへ追加しない(DEV/Trial範囲=flag配下、実装は委任_02以降)。
根拠資料: `INVESTIGATION_01.md`(経路・FAILED扱い・既存機構)、`OFFLINE_AUDIT_01.md`(数値)、`gloss_alignment_01/`(現行実装の証跡)。

## 1. 目的と工程順
目的: 最終英語KPの全ての語(目的語・補語・修飾語)の意味を日本語glossが過不足なく反映していること(基本品質要件、ユーザー2026-10-14)。
工程順(ユーザー指示B):
1. KP候補選定・初期gloss生成(既存、無変更)
2. 英語KP最終確定(canonicalization、既存、無変更)
3. **最終KPとglossの再整合**(本設計で修正する段): 対象=KPが候補から伸びたitemのみ(既存の`select_alignment_targets`、無変更)
4. 必要な品質判定(Redundancy QA/記号QA〔既存〕。+3の結果が`FAILED`ならここへ進まず例外処理)
5. TTS(FAILED itemは対象KP segmentの生成をしない)
「不整合が残ったitemを正常なTTS入力・正常完成として扱わない」を、**状態をartifactに永続化し、消費側(TTS/Gate/runner)がそれを必ず参照する**構造で担保する(現行は消費側が誰も参照していない: INVESTIGATION_01 5節)。

## 2. 現行設計との差分
### 欠陥①(「～」記号を合否条件にしている)
| | 現行 | 修正案 | 理由 |
|---|---|---|---|
| 合否の根拠 | KPにスロット語(someone/something/one's等)が無くglossに「～」があればFAIL(`gloss_alignment.py:223-226,252-253`)。LLM自己申告`qa_reflects_all_key_phrase_words`併用 | 「～」の有無は合否に使わない。**KPに追加された内容語ごとに、gloss内の対応する日本語spanが存在すること**(機械検査)+意味が合っているか(LLM判定) | 承認済み規則は「辞書的に自然なら『～』可」。意味欠落の検出手段を記号から対応関係へ置換。旧gloss記録では「～」ルールは意味不整合6件中3件(50%)しか捕捉せず、無関係な正当な「～」28/29件をFAIL対象にする性質(OFFLINE_AUDIT_01) |
| 課題指示文 | 「スロット語がある場合に限り『～』を許可」(承認規則と矛盾) | 当該文を削除。承認済み規則の引用はそのまま。「～」の可否は規則に従い、判定は意味のみ | OF-226の緊張関係を解消。承認済み規則本文は変更しない(実行時に`b1_p2…template.txt`から抽出、sha256 `447e07cb…`固定を維持) |
| `current_gloss_consistent`が真なのに別glossを返す | 検査なし | 真ならgloss==current(厳密)、偽ならgloss!=current。矛盾はINVALID(retry) | 既存の自然なglossを不必要に変更しない保証の機械的部分。replayでは矛盾 0/27(high)・0/27(medium) |
### 欠陥②(2回失敗でFAILED通知のみで正常工程へ進む)
| | 現行 | 修正案 | 理由 |
|---|---|---|---|
| 2回失敗時 | 最終KP+古いglossを残し、`gloss_alignment_status=FAILED`、NOTICE.md(`key_phrases/`配下)、stdout。TTS・Gate・assembleは素通り | **Human Review例外報告**(英語KP・現在gloss・失敗理由・試行結果・再生成候補)+対象itemのTTS保留+Gate/runnerで完成扱い禁止 | INVESTIGATION_01 5節: 消費側にFAILEDを参照するコードが無い |
| KPを短い候補へ戻すfallback(i) | config選択時のみ条件付き(既定は(ii)) | **廃止**(コードパス削除)。候補(display_phrase)+旧glossは「参考情報」としてHR報告に載せるのみ。自動適用しない | ユーザー: 安易にKPを短くしない。canonicalizationの判断(補語復元)を捨てて意味を落とす |
| 一部itemだけ失敗 | batch単位で全itemがFAILED扱い(`validate_alignment_response`は全件OKでのみ`ok`) | **item単位で検証**し、検証済みitemは採用、未解決itemのみFAILED | 独立itemを不必要に止めない。再整合成立済みitemのgloss改善を捨てない |
| 通知 | ファイル生成・印字のみ | 「届いた」の定義5条件(4節) | 通知ファイル生成だけではHuman Reviewが届いたとみなさない |
| Human Reviewの位置付け | 「送らない」(OF-228) | 例外の最終対応としてのみ送る。通常運用ではない | ユーザー2026-10-15: 常態化しない=例外対応は必要 |

## 3. 意味整合判定の設計
### 3.1 機械的に確認できる事項 / 言語的判断が必要な事項の分離
| 事項 | 種別 | 実装 |
|---|---|---|
| 対象item選定(KPが候補から伸びたか) | 機械 | 既存`select_alignment_targets`(無変更) |
| **追加内容語の算出**(KPのうち候補に無い内容語) | 機械 | 既存`kp_adds_words_beyond_display`の判定ロジックを語リストで返す関数へ(例: `locked into a narrow view`→narrow,view)。活用形・冠詞・人称一般化(my→one's)は追加語に数えない(既存同様)。OFFLINE_AUDIT_01で8/8算出確認 |
| 追加語ごとに**対応する日本語span**が応答にあるか(`added_word_mappings`) | 機械 | LLM出力の`[{english_word, japanese_span}]`が、算出した追加語と1:1か |
| `japanese_span`が最終glossの**部分文字列**か(実在確認) | 機械 | 文字列包含。LLMが存在しない部分を指す(幻覚)を検出 |
| spanが記号のみ(「～」等)でない | 機械 | 追加語は具体的な日本語で表すこと(スロットで済ませない)。これは「glossに『～』が有る」ではなく「追加語の対応部が記号のみ」を禁じる。gloss全体の「～」は不問 |
| 判定とgloss変更の整合(真⇔不変) | 機械 | 厳密比較 |
| 括弧・「…」・算用数字・音声化禁止記号 | 機械 | 現行の承認規則由来のチェックを維持(`_PAREN_RE`/`…`/`_ARABIC_DIGIT_RE`/`detect_prohibited_symbols`)。新条件ではない |
| span対応が**意味的に正しい**か(`interviews`→`インタビュー`は正、`prices`→`コーヒー`は誤) | **言語的** | LLM判定(`current_gloss_consistent`/`reasoning`)。機械は検出できない |
| KP全体(動詞・前置詞のニュアンス含む)の意味に合うか、自然さ・平易さ(承認規則) | **言語的** | LLM判定+承認規則(課題指示文に引用) |
| `helper`↔`人`のように対応らしき語はあるが意味が曖昧 | **言語的** | LLM判定。必要なら任意の独立verifier(代替案E) |

### 3.2 LLM入出力
入力(1 batch=対象item最大5): `rank, key_phrase, display_phrase_before_canonicalization, current_japanese_gloss, source_sentence, added_content_words`(新規フィールド=機械算出)+記事本文(参考、現行どおり)。
出力スキーマ(strict JSON): `rank, current_gloss_consistent(bool), japanese_gloss, added_word_mappings[{english_word, japanese_span}], qa_reflects_all_key_phrase_words(PASS|FAIL), reasoning`。追加は`added_word_mappings`のみ。`qa_reflects…`は補助(合否の唯一の根拠にしない、現行と同じ位置付け)。
retry上限は現行どおり2(`MAX_GLOSS_ALIGNMENT_ATTEMPTS`)。上限・既存の外側retry機構は変更しない。

### 3.3 課題指示文の修正案(全文。承認済み規則本文は変更しない)
developer(無変更):
```
英語学習教材のKey Phraseに付ける日本語グロスを、最終的な英語Key Phrase全体の意味に過不足なく一致させてください。
```
user(固定部。【】は実行時差込。承認規則は`b1_p2_keywords_l_prompt_template.txt`から実行時抽出し複製しない):
```
以下の各英語key_phraseは、教材として最終確定した英語表現です。current_japanese_glossは、確定前の候補表現(display_phrase_before_canonicalization)を基準に付けた日本語グロスで、確定したkey_phrase全体とは一致していない可能性があります。added_content_wordsは、確定時に候補表現へ新しく加わった内容語です。

各項目について、次を行ってください。
1. current_japanese_glossが、最終的なkey_phrase全体(目的語・補語・修飾語を含むすべての語)の意味と過不足なく一致しているかを判定し(current_gloss_consistent)てください。「～」「〜」を含むかどうかは判定の基準ではありません。key_phrase全体の意味が日本語に表れているかどうかだけで判定してください。
2. 一致している場合は、japanese_glossにcurrent_japanese_glossをそのまま返してください。一致していない場合は、最終key_phrase全体に一致する日本語グロスを返してください。
3. added_content_wordsの各語について、japanese_glossの中でその語の意味を表している部分を、japanese_glossからそのまま切り出してadded_word_mappingsに書いてください(japanese_glossに含まれない文字列や、「～」などの記号だけを書かないでください)。
判定の参考例:
- key_phrase「based on」にcurrent「～をもとにした」: 辞書的に自然なので一致です。
- key_phrase「based on interviews」にcurrent「～をもとにした」: interviewsの意味が欠けているので不一致です。「インタビューをもとにした」なら一致です。

key_phrase単体で他の文脈でも再利用できる自然な訳にし、本文固有の固有名詞・文脈の追加はしないでください。key_phrase全体の意味を反映できている場合のみqa_reflects_all_key_phrase_wordsをPASSにしてください。

【日本語グロスの規則(承認済み選定Promptと同一)】
(承認済み選定Promptから実行時抽出。sha256 447e07cb8b9a30850a8dc75b6c3cce48c53d99b5f1fafa88d19b778d9155949b)

【対象項目】 (rank / key_phrase / display_phrase_before_canonicalization / current_japanese_gloss / source_sentence / added_content_words のJSON)
【記事本文(参考)】 (記事本文)
```
現行との差分は3点のみ: (a)「スロット語がある場合に限り『～』を許可」を削除し「『～』の有無は基準ではない」へ、(b)`added_content_words`入力と`added_word_mappings`出力指示、(c)判定例2行(ユーザー提示の例)。例が出力を引っ張る懸念(few-shot偏り)はTrialで確認する(TRIAL_PLAN_01 T1)。

### 3.4 既存の自然なglossを変更しない保証
1. 再整合の入口は変更しない: 対象外item(KP==display、追加語なし)は**LLMに渡らない**(`NO_TARGETS`/対象外はmergedを無変更)。census 1,129 itemのうち対象は7(0.6%)。
2. 対象でも、`current_gloss_consistent=true`なら**gloss==currentを機械強制**(矛盾はINVALID)。LLMが書換えを返してもcurrent維持が採用される形ではなく、矛盾として再試行扱いにして無言の書換えを防ぐ。
3. 判定が偽で書換えた場合は`original_japanese_gloss`・`reasoning`・差分を既存どおり`gloss_alignment`/runtime metadataに残す(監査可能)。
4. 限界(正直に記載): 対照(整合済みをforcedで対象にした)10件中1件(`drop the fee`『料金案を取り下げる』→『料金をなくす』)でLLMが「不整合」と判定し書換えた(`VALIDATION_01.md`)。LLMの判定自体が誤る場合(誤NG)は機械では防げない。→ Trialで対照を増やして書換率を測定(T1)。差分0件の検証=**対象外itemの差分0件**(全1,129 item再生で`merged`が同一であること)+**整合済み対照の不変率**。
### 3.5 誤NG・誤PASSの検証方法
| 種別 | 検証 | 時期/費用 |
|---|---|---|
| 機械検査の誤NG/誤PASS | mock LLM出力でのunit test(決定論): 例 `based on interviews`+`～をもとにした`→mapping欠落でFAIL / `インタビューをもとにした`+span`インタビュー`→PASS / span実在せず→FAIL / spanが「～」のみ→FAIL / 真+書換→INVALID / `point to`+`～を示す`(追加語なし対照)→PASS / スロットKP`declare something to be`+`～を～だと宣言する`→PASS | オフライン、JPY0 |
| 既存記録での機械検査 | 旧glossでは対応span出力が無いため後ろ向き適用不可(OFFLINE_AUDIT_01 限界4)。代替=追加語算出の8/8確認済み | JPY0 |
| LLM意味判定の誤NG(整合を不整合と判定) | 整合済みの自然なgloss(辞書的な「～」を含むものを含む)を対象へ強制投入した対照セット20件前後で、書換率・誤FAIL率 | 有料Trial T1/T2 |
| LLM意味判定の誤PASS(不整合を整合と判定) | 欠陥注入セット: 既知不整合(`based on interviews`×「～をもとにした」等)+span対応が存在するが意味が誤っているもの(例 `prices`→`コーヒー豆`のspan)を意図的に含める | 有料Trial T2 |
| 停止の確実性 | mock統合テスト(失敗系パターン、TRIAL_PLAN_01 T3) | オフライン、JPY0 |

## 4. 失敗時設計(FAILED→Human Review→対象工程停止)
### 4.1 起点と範囲
- 起点: 再整合が上限2回で**item単位**に成立しなかった(機械検査FAIL/JSON不正/技術失敗/LLM判定不整合のまま)。
- 停止範囲(線引き):
  - **停止**: 当該levelの当該rankのKP segment(`kp{rank}_japanese_meaning`、およびglossを入力にする`explanation`)のTTS生成(0 API call)。Audio Validation Gateでepisode assemblyを禁止。「正常完成」として扱わない。
  - **継続**: 本文・support・他rankのKP・他levelの独立TTS(Family X)。Family Zは既存のstage順(kp→tts)で`stage_kp`が`FamilyZE2EStop`を送出する既存前例(`er026…:1175`、canonicalization非PASSも同様に停止)に合わせ**stage単位で停止**(KPがTTSより前のstageのためAPI費用は発生せず、HR解消後に既存resumeで再開)。Family Xのitem単位保留とZのstage停止の使い分けは決定事項としてレビューに出す(4.4)。
### 4.2 既存機構のどれに載せるか(新機構を作らない理由)
| 要素 | 載せる既存機構 | 新設分 |
|---|---|---|
| TTS停止 | Human Review Lock(`er011_human_review_lock_01.py`): `record_outcome(out_path=…/narration/kp{rank}_japanese_meaning.wav, text=現在gloss(canonical text), result={"status":"STOPPED_GLOSS_ALIGNMENT_FAILED","reason":…})`→`HUMAN_REVIEW_REQUIRED`。以降`guarded_generate`が0 API callで拒否。glossが変われば新version扱いで解除、明示解除は既存`approve_regenerate`(:472) | なし |
| 完成禁止 | Audio Validation Gate(`assemble.py:~480-515`): 当該KP componentに非許可status(`STOPPED_GLOSS_ALIGNMENT_FAILED`)を`tts_generation_results.json`へ記録→`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`。`--only-segments`の`SKIPPED_NOT_SELECTED`と同じ前例 | status文字列1つ(Gate無変更) |
| Human Review提示 | `human_review_queue.jsonl`(`er006_secondary_asr_01.py:321`)へ`kind="KP_GLOSS_ALIGNMENT_FAILED"`のentryを追記(同一wav_path+canonical_textの重複抑止`is_duplicate_queue_entry`を流用) | kind付きentry。**queue消費側(`er006_*_build_review.py`)が`steps`無しentryを許容するかは未確認→実装前確認。許容しなければ専用queueを作らず、まず消費側を非破壊で拡張する提案をOpusへ** |
| 内容の提示 | HR報告書 `key_phrases/GLOSS_ALIGNMENT_HUMAN_REVIEW_01.json`(+人間可読.md) | 報告書スキーマ1つ(既存NOTICE.mdを置換。M2 fallbackのNOTICEと同パターン) |
| run summary | `scaffold_run_summary.json`の`m2_fallback_events`と同位置に`gloss_alignment_human_review_events` | キー1つ |
| 停止条件の参照 | 永続化された`keywords_canonicalized.json`のitem `gloss_alignment_status="FAILED"`を、TTS段と`stage_kp`が読む(別プロセス実行でも参照可能) | 参照関数`collect_unresolved(kp_json)`1つ |
新Validator・新Hook・新管理機構(独自の状態機械・独自STOPセンチネル等)は作らない。STOP/STOP_ALLセンチネルとは混用しない(センチネルは外部停止用。本停止はLock+Gate+stage停止)。
### 4.3 HR報告書の必須項目と再生成候補
必須: article/level/rank、**英語KP**(最終)、**現在gloss**(再整合前=currentのまま)、**失敗理由**(機械検査コード+LLM`reasoning`)、**試行結果**(全attemptのstatus・提案gloss・違反理由・usage/cost)。
再生成候補(提示のみ、自動適用しない): (1)試行で得た提案gloss(各違反理由付き) (2)追加語ごとの対応が欠けている語の一覧 (3)参考: 候補表現(display_phrase)+旧gloss — **「KPを短くすると意味が失われる、人間判断でのみ採用」と明記。最終KPは戻さない** (4)KP再生成(既存経路、1レベル1回)。
### 4.4 「通知が届いた」の定義(ファイル生成だけで完了としない)
以下5条件を**全て**満たして初めて「届いた」とし、いずれかが書込失敗なら**fail-closed**(例外で当該stageを止める。「通知失敗だが継続」は許さない):
1. HR報告書が存在し、必須5項目が非空(スキーマ検証をその場で再読して確認)
2. queueにentryが追記済み(または重複抑止で既存entryを確認)
3. Lockのstateが`HUMAN_REVIEW_REQUIRED`(再読して確認)
4. run summaryに`gloss_alignment_human_review_events`が載り、runnerの最終stdoutに専用1行(`print_m2_fallback_final_line`と同形式)
5. 下流が実際に止まる: TTS段が当該segmentで0 API callとなり、Gateが非許可statusでassemblyを拒否(mock統合テストで確認)
### 4.5 既存機構との整合
STOP_ALL/STOPセンチネル: 変更・参照しない(有料呼出前のセンチネル確認は従来どおり)。Audio Validation Gate: 無変更。M2 fallback: 別物(代替経路の結果がGateを通る設計)なので触れない。既存retry上限(再整合2回、外側redundancy retry)は変更しない。flag(`EIGO_KP_GLOSS_ALIGNMENT`)はそのまま。**フラグ既定値は別提案(INVESTIGATION_01 8節: 既定OFF化を推奨、要承認)**。

## 5. 代替案とQDC比較
| 案 | 内容 | Q | D | C(/記事セット) |
|---|---|---|---|---|
| **A(提案)** | 再整合LLM 1 call(最大2回)+追加語→span機械検査+失敗→HR例外+Lock/Gate停止 | 欠落をspan対応で機械的に捕捉。意味誤りはLLMのみ | 変更: gloss module/scaffold/X・Z runner/テスト。Lock/Gate/Assembleは無変更 | 現行見積り通常0.014〜0.08、最悪0.57、絶対最悪1.7(`cost_01.json`)。スキーマ追加による出力トークン増分は**未確認**(T1で実測) |
| B | A+失敗時に既存外側retry(選定からやり直し、`KEY_PHRASE_REDUNDANCY_RETRY_MAX`共有)を先に使い、尽きてからHR | HRへの到達率をさらに下げる(別KPになる可能性) | `_run_key_phrases_impl`のループ条件にgloss FAILEDを追加(既存retry再利用)。ユーザー指示は「2回失敗→HR」なので**ユーザー承認が別途必要** | 再選定+canonicalization費用が追加(単価は`cost_01.json`に無く**未確認**)。記事単位cap`KP_ARTICLE_COST_CAP_JPY`(既定15円、`er030_key_phrase_db_hybrid_selector_01`定数。DB Hybrid経路の累積費用に適用)以内に収まる |
| C | LLM無し・機械検査のみ | 英日対応を機械で作れず意味判定不能。**不採用** | - | 0 |
| D | canonicalization Promptにgloss再生成を統合(1 call化) | 承認済みPrompt/Rule7に触れ、再検証が必要。**不採用(要ユーザー承認の別案件)** | 大 | -約1 call分 |
| E | A+独立verifier(日本語→英語の逆翻訳比較等、別call)で誤PASS低減 | 誤PASSをさらに低減しうる | +1 call/対象。Trialで効果を実測してから | 追加は対象batchごとにalign callと同オーダー(0.07〜0.14/batch、**想定**。未測定) |
推奨: A。BとEは、T1/T2でAの誤PASS・HR到達率が許容を超えた場合のみ提案(独断採用しない)。

## 6. Opus台帳(`docs/pm/OPUS_FINDINGS_LEDGER.md`)への影響案(本委任では編集しない)
| OF | 現行 | 案 |
|---|---|---|
| OF-230 | KP側スロット語なしで「～」FAIL | **置換**: 「機械的に検出可能な品質」という所見の意図は維持し、手段を「追加内容語→日本語span対応の機械検査+LLM意味判定」へ。「～」記号条件は撤回 |
| OF-228 | FAILED通知のみ、Human Review送りなし | **一部撤回**: 通知は維持しつつ「Human Review送りなし・下流を止めない」を撤回し、例外時HR+対象TTS保留+Gate停止へ。通知の定義を5条件へ |
| OF-227 | fallback既定(ii)、(i)は条件付き | **一部改訂**: (i)廃止、(ii)は「FAILEDで継続」ではなく「HR+停止」 |
| OF-226 | 課題指示文と承認規則の「～」緊張が未承認 | 課題指示文から「スロット語に限り許可」を削除することで解消(承認は再度Q1で要) |
| OF-225 | 新仕様採用の位置付け未確定 | 継続(新品質条件を含めて再度ユーザー判断) |
| OF-235 | flag既定ON、口頭運用の隔離 | 強化案: 既定OFF化(要承認)、preflight警告 |

## 7. 変更対象ファイルと影響範囲(実装は委任_02以降)
| ファイル | 変更 |
|---|---|
| `er003_key_words_gloss_alignment.py` | 追加語リスト関数、スキーマ(`added_word_mappings`)、`validate_alignment_response`のitem単位化+機械検査+「～」条件削除(`SLOT_TOKENS`/`gloss_has_unjustified_slot`/`kp_has_slot_word`は不使用化→削除)、`build_user_message`文面、fallback(i)(`revert_to_candidate_allowed`、モード定数)削除、HR報告書生成/queue登録/Lock記録/`collect_unresolved` |
| `er003_v1_n3_01_scaffold_generate.py` | `run_key_phrase_canonicalization`でFAILED itemのHR登録とfail-closed、`run_key_phrases`で`gloss_alignment_human_review_events`をrun root向けに伝播(NOTICE配置の是正) |
| `er019_family_x_audio_production_runner_01.py` | scaffold summaryへのevents追加、最終stdout行、TTS段のKP保留(Lock/Gate連携) |
| `er026_family_z_fiction_production_runner_01.py` | `stage_kp`の停止条件にgloss FAILEDを追加(既存`FamilyZE2EStop`) |
| `er003_test_key_words_gloss_alignment.py` ほか | 「～」関連・fallback関連の既存testを置換/追加 |
| 無変更 | Prompt(選定/canonicalization)、Rule7、Gate(`assemble.py`)、`er011_human_review_lock_01.py`、承認済みgloss規則本文、config既定値 |
影響範囲: `run_key_phrases`を呼ぶ全スクリプト(約40)に共通のため、機能は引き続きflag配下。FAILED時のhard stopは「flag ON かつ 対象itemがFAILED」に限る(通常は対象率0.6〜1.4%、記事あたり7%程度、FAILED実測0/16)。
Regression対象test: `er003_test_key_words_gloss_alignment`(現366のうち当該ファイル分を改訂)/ `er003_test_key_words*`全体366 / `er003_v1_n3_01` 55 / `er019` 421 / `er030` 108 / Family Z音声test(er063)59 / Human Review Lock関連(`er011_*lock*_test`)/ `er008_audio_validation_gate_05_test.py`(新status追加がGateで確実にblockされること)。

## 8. 未決事項(レビューで判断を仰ぐ点)
1. 停止粒度: Family Xはitem単位保留、Zはstage単位停止(4.1)で良いか。
2. HR queue消費側が`steps`なしentryを許容するか(4.2、実装前調査が必要)。
3. 解決手段: 人間が確定したglossを入れる最小手段(`gloss_alignment_status="HUMAN_RESOLVED"`を書く小関数)を新設するか、既存のKP再生成のみにするか。
4. few-shot例が出力を偏らせないか(T1で確認)。
5. 案B(既存外側retryを先に使う)を採るか(ユーザー指示と差があるため、採るならユーザー判断)。
6. 並行検出: Family XでNG_REVIEW_REQUIRED素通りの疑い(INVESTIGATION_01 7節a)は別OPEN候補。本設計では対象外。
