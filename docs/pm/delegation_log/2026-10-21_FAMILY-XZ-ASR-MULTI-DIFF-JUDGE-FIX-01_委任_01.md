# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01 委任_01(承認済みの表記揺れ・同音等価判定が、同一音声内に複数差分があるときに個々の差分へ正しく適用されない不具合の是正。原因調査→最小修正→回帰test→Family X/Z正式経路への反映→runtime evidence→SSOT。到達上限=全Gate確認後`PRODUCTION_WIRED`判定[判定はFable])。
並行agent: `FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01 委任_01`(②の設計のみ。`docs/research/FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01/`と`er089_*`を使用、Production codeは触らない)。共有プロトコル(OPEN_ITEMS/REPORT_LEDGER/ACTIVE_TASK/DECISION_LOG: 編集直前`git status --porcelain`+末尾再Grep→自分の行だけ→即add/commit、index.lock 30秒待ち)。ユーザー原文の保存は本委任が担当(②agentは同pathが存在しsha一致ならskip)。

## 性質/到達上限Status/禁止事項
- 性質: **既存承認仕様の不具合是正(11-8範囲内、新仕様ではない)**。CURRENT_SPEC.md:411-446(OPEN-121 対称正規化)、同:1829(固有名詞自動PASS条件)、同音等価(HOMOPHONE_EQUIVALENT/CMU層)、保護数値判定、Azure Phrase List重み2.0、TTS Fallback仕様は**変更しない**。許容条件の拡張・期待結果を固定した例外処理の追加は禁止。
- 費用: 是正・回帰testはAPI 0。runtime evidence(下記S5)は既存wavに対するASR再実行のみ(TTS生成禁止)、見積JPY1〜5、T-3 Guardrail=JPY20。日次はS0で実測。
- Opus独立レビュー(11-3): 条件A非該当(構造変更なし)。ただし修正が判定関数の構造(トークン比較の方式)に及ぶ場合はFableへ報告し判断を仰ぐ(自分で広げない)。
- 禁止: 既存TTS音声・正式記事成果物・Master Store・Ledger・review_queueの変更、判定基準の緩和、`git add -A`等。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01_委任_01.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「ASR-MULTI-DIFF-JUDGE-FIX-01 委任_01」を含む最新index)。check結果1行。T-2: TTSなし。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-XZ-ASR-MULTI-DIFF-FIX-AND-PROPER-NOUN-EN-PRONUNCIATION_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01(①) / FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01(②)`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
# Claude Code／Fableへの指示
## Family X/Z共通 — ASR複数差分判定の是正・固有名詞英語読み供給Trial

### 1. 目的・対象

Family X「漫画のキャラクターとAIで会話（byUs）」で発覚した2つの問題を解決する。

**① 承認済みの表記揺れ・同音等価判定が、複数差分の存在下でも正しく機能するようにする。**

**② 未登録の英語固有名詞について、正しい発音を調査・登録し、Azure Phrase Listなどの後続工程へ供給する共通仕様を検証する。**

対象はFamily X・Zの両方。片方だけの改善で完了としない。

既存の品質基準・同音等価ルール・Azure Phrase List重み2.0・TTS Fallback仕様は変更しない。

### 2. ① 複数差分判定の不具合是正

**位置づけ：既存承認仕様の不具合修正。新仕様の追加ではない。**

`story-making` / `storymaking` の表記差そのものは既存仕様で吸収可能。

今回修正するのは、同じ音声内に複数の不一致が存在した際、個々の差分に既存の許容ルールが適切に適用されない問題。

実施内容：

- 既存の正規化・同音等価・差分比較処理を調査し、根本原因を特定する。
- 各差分を既存ルールに従って評価できるよう是正する。
- 許容できる差分が複数存在する場合、他に問題がなければPASSする。
- 一つでも実質的なNG差分が残る場合は、正しくNGにする。
- Family X/Z双方の正式判定経路に適用する。

**必須再現ケース**

今回の記事B Advanced Full Story第1部の既存ログ・台本・ASR結果を使い、`byUs → Bias` と `story-making → storymaking` が同時に存在するケースを再現する。

既存仕様の同音等価判定と表記揺れ吸収によって、両方が許容できる場合は最終PASSになることを確認する。

同時に、`two works → 20 works`、発音が異なる単語への置換、脱落などの実質的誤りは、別の許容差分が存在してもNGを維持する。

既存仕様の範囲を超えて許容条件を拡張しない。

### 3. ② 固有名詞の英語発音供給 — 新仕様候補

**位置づけ：仕様設計・Offline Trial。Production正式採用は未承認。**

対象はFamily X/Zの英語本文に登場する、英語発音情報が未登録の固有名詞・ブランド名・造語等。

既存のPronunciation Ledger、固有名詞検出、読み解決、Azure Phrase List、TTSヒントの仕組みを調査し、共通資産を最大限再利用する。

設計・Trialで以下を実現する。

1. `byUs` のような小文字始まりの名称も、文脈を踏まえて固有名詞候補として検出する。
2. 未登録の場合は、公式サイト・公式発表など信頼できる情報源を検索し、**正しい英語での発音**を確認する。
3. 日本語のカタカナ読みから英語発音を機械的に推定・確定しない。
4. 根拠を記録したうえで、Pronunciation Ledgerへ英語発音情報を登録する。
5. 登録情報をAzure Phrase Listおよび必要なTTS・ASR工程へ供給する。
6. Azure Phrase Listへの実投入内容と重み2.0の適用を、実行証拠で確認できるようにする。
7. 読みが確定できない場合は、誤った読みを登録・強制しない。既存の安全な判定経路を維持する。

Family X/Zの共通仕様として設計し、Familyごとの適用結果を確認する。

### 4. Trial必須条件：今回の実例を再現し、PASSさせる

**机上の設計や単体テストだけで終了しないこと。**

記事Bの実際の問題をTrialケースとして使用する。

| 再現ケース | 必須確認結果 |
|---|---|
| `byUs`（公式の英語読み） | 未登録検出→根拠確認→Ledger登録→Phrase List投入 |
| `byUs → Bias` | 同音等価として適切にPASS |
| `byUs → Bias` ＋ `story-making → storymaking` | 複数の許容差分が共存してもPASS |
| `LINE` | 正しい固有名詞として扱い、必要な読み情報を供給 |
| `LINE → Lion` | 実際の発音が異なる場合、誤PASSさせない |
| `two works → 20 works` | 数値の重大な不一致としてNG |

少なくとも、**記事Bで発生した本来PASSすべきケースが、修正・改善後に正しくPASSすること**を必須とする。

ただし、PASSさせるために判定基準を緩めたり、期待結果を固定した例外処理を追加してはならない。

実際の音声が誤発音している可能性と、ASRの誤記は区別する。実音声が誤っている場合は、ASR判定だけをPASSさせて品質改善完了としない。

### 5. Trialの検証範囲

既存の音声・ASRログ・Ledger情報を優先的に再利用し、次を検証する。

**A. 機能面**

- 固有名詞の検出精度
- 英語発音の検索・根拠の妥当性
- Ledger登録の正確性
- Azure Phrase Listへの実投入
- 重み2.0の実適用
- ASR認識・同音判定への効果
- 未登録語・検索不能語への安全な対応
- Family X/Z双方の経路での有効性

**B. 品質面**

- 正しい音声を誤NGにしない
- 誤発音・単語違い・数値違いを誤PASSさせない
- 既存のPronunciation LedgerやPhrase Listに悪影響を与えない

**C. QCD**

- 不要なTTS再生成の削減可能性
- ASR/API検索費用の増減
- 処理時間・待機時間への影響
- 量産単価70円／記事セットへの影響

追加の有料検証は、既存証拠で不足する部分に絞る。承認済み予算内で並列化・再利用を最適化し、不要な日付分割や待機を行わない。

### 6. 実施・承認境界

**①は承認済み仕様の不具合修正として、原因調査→修正→回帰テスト→Family X/Zの正式経路への反映まで実施する。**

正式配線、runtime evidence、retry／fallback／regeneration／resumeとの整合、SSOT・Git反映まで確認する。

**②はTrial専用経路で実施し、正式Productionには配線しない。**

Trialで良好な結果が出ても `VALIDATED` にとどめ、ユーザーの正式採用判断を待つ。

- 既存のTTS音声・正式記事成果物は変更しない。
- 判定基準・同音等価ルールを独断で拡張しない。
- 必要十分な品質に到達したら追加Trialを行わず終了する。
- 重大な品質・安全問題、承認範囲外の仕様変更、予算超過が必要な場合はSTOPする。
- Fableは設計・実行証拠・結果を独立評価する。

### 7. 完了報告・Closeout

以下をユーザー判断に重要な順で報告する。

1. **今回の記事Bの実例を再現し、本来PASSすべきケースがPASSしたか**
2. ①の修正結果とFamily X/ZそれぞれのProduction配線・回帰テスト・runtime evidence
3. ②の固有名詞検出・公式発音確認・Ledger登録・Phrase List投入・重み2.0適用の証拠
4. ②による実際のASR改善結果と誤PASSリスク
5. 追加費用・処理時間・量産単価への影響
6. Fable独立評価
7. 残るユーザー判断

CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS等を更新し、必要なGit反映を行う。

①は全Gate確認後に `PRODUCTION_WIRED` と判定する。未確認項目があれば完了扱いにしない。

②はTrial終了時に `VALIDATED`／`REJECTED`／`USER_DECISION_REQUIRED` のいずれかとし、Production採用を先取りしない。

**最重要：Family X/Z共通で機能すること。今回の記事Bで実際に起きた「本来PASSすべき差分」を再現してPASSさせ、同時に「本来NGの差分」は確実にNGとすること。**
--- 原文ここまで ---

## 手がかり(前調査、鵜呑みにせず再確認)
- `docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/PROPER_NOUN_PHRASELIST_INVESTIGATION_01.md`(委任_06調査: story-making/storymakingは単独ならNORMALIZED_MATCH、他diffが1つでもあるとtoken比較で漏れる。最小再現あり。`er006_preprod_hardening_01_validation.py:467-489,525,1000-1011`、`er006_secondary_asr_01.py:350-354,946`、CMU層`cmu_alternate`、`er078_asr_unified_judge_01`、`er021` EN semantic equivalence)。
- 第1部attempt1の実ログ: `er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/b1b/audit/tts_generation_results.json` `segments.full_story_part1.standard_attempts_log[0]`(canonical、一次転写[byUs→Bias、story-making→storymaking]、二次転写、判定)。
- Family Z経路: `er063_family_z_audio_01.py`→`er012_b_family_voices_production_01.generate_voice_body_wide_margin`→同じ判定関数か(呼出経路をGrepで確認し、X/Zが同一関数を通ることを証明。別関数なら両方に是正)。
- 既存test: `er006_*validation*test*`、`er021_*`、`er078_*`、`er011_open121*`(OPEN-121)。

## 手順
S0. daily cost、`git status`件数、T-0、原文保存。
S1. 原因特定(API 0): 判定経路を追い、「単独差分では正規化/同音等価が効くのに、複数差分だとtoken単位比較に落ちて個々の許容ルールが適用されない」箇所をfile:行で特定。最小再現test(第1部attempt1の実canonical/実転写を固定データとして使用)を先に書き、旧コードでFAILすることを確認。
S2. 是正(最小差分): 複数差分時も各差分に**既存の**許容ルール(対称正規化・ハイフン/連結・同音等価[CMU]・既存の数値保護・stopword扱い)を個別適用し、全差分が許容なら既存ラベル(NORMALIZED_MATCH/HOMOPHONE_EQUIVALENT等、既存の優先順位どおり)でPASS、1つでも実質NGならTRUE_CONTENT_MISMATCH/NG_PROTECTED等を維持。新しい許容規則・閾値・辞書を追加しない。変更はX/Z共通の判定関数(両Familyが通る関数)に限定し、コメントに管理ID。
S3. 回帰test(API 0): 必須ケース=(a)`byUs→Bias`単独PASS(既存)、(b)`byUs→Bias`+`story-making→storymaking`→PASS、(c)`two works→20 works`(+他の許容差分併存)→NG、(d)発音が異なる語への置換(例 LINE→Lion、part→tart)→NG、(e)語の脱落(the/story)→NG(既存の扱いどおり)、(f)`Buy Us`(2語化)→現行どおり(拡張しない、結果を記録)、(g)Family Z既存ログから1ケース(メロス run_e2e_06の任意segmentの実転写、既存結果と同一であること)。既存test全件PASS(er006/er021/er078/er011_open121/er063/er019関連)。**golden**: 既存run 3件(run_mey_02、coffee run_fxpw_01、run_pp_01)と Family Z run_e2e_06 の全attemptの保存済み転写を新旧判定関数でoffline再判定し、変化したケースを全列挙(変化は「複数差分かつ全差分が既存許容」のケースのみであること。NG→PASSに変わるものは各差分の許容根拠を明記、PASS→NGは0件であること)。
S4. X/Z正式経路への反映の証明: 呼出経路(X: er003/er006 cascade、Z: er012/er063)が修正関数を通ることをGrep+import graphで示し、test名を記録。
S5. runtime evidence(有料・最小): 第1部attempt1の**既存wav**(`b1b/narration/attempts/`配下に残っていれば)に対し、Production判定関数を実ASR呼出で1回実行(`force_secondary`なし、Production既定)し、新判定でPASSになるか記録(一次転写は変動するため、結果の転写と判定ラベルをそのまま記録。PASSにならなくても判定基準は変えない)。Family Z側は、メロスの任意既存clip 1本で同様に1回(既存結果と整合)。見積JPY1〜2。wavが無ければ「runtime evidenceはoffline再判定のみ」と明記しFable判断へ。
S6. retry/fallback/regeneration/resumeとの整合: 判定関数の戻り値契約(ラベル・理由コード・semantic_equivalence)が不変であることをtestで固定、呼出側(cascade/LR/Variant Layer)が影響を受けないことを確認。
S7. SSOT: CURRENT_SPEC.md:411-446(OPEN-121)の節末に是正注記(問題/変更/改善/リスク、file:行、golden差分件数)、DECISION_LOG 1件、OPEN_ITEMS新規行(Status `MULTI_DIFF_JUDGE_FIX_WIRED_PENDING_FABLE`、PRODUCTION_WIRED判定はFable)、REPORT_LEDGER 1行、ACTIVE_TASK。
S8. secret scan→明示add→commit(`FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01 委任_01: 複数差分時の個別許容判定の是正(X/Z共通判定関数)+回帰test+golden再判定+runtime evidence+SSOT`)→`git push origin HEAD:main`→到達確認。

## 報告(docs/pm/RESULT_PACKET_MDJF1.md 上書き)
1.原因(file:行、何が問題だったか) 2.変更(file:行、diff要約) 3.必須ケース(a)〜(g)の結果表 4.golden再判定の変化一覧(NG→PASSの各根拠、PASS→NG件数) 5.X/Z経路の証明(呼出graph・test名) 6.runtime evidence(転写・判定・費用) 7.整合確認(契約不変) 8.SSOT・commit・raw URL 9.PRODUCTION_WIRED判定材料(Gate 1〜7相当のチェック表、未確認項目があれば明記) 10.4行判定。