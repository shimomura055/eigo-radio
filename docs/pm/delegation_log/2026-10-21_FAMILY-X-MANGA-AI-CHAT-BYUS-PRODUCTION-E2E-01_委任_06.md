# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_06(Adv Full Story第1部・第3部のASR不一致[byUs→Bias/BIOS/Buy Us/Byus/Baias/BAYAS/FAYAS、LINE→Lion]について、固有名詞抽出・Pronunciation Ledger・Azure Phrase List・重み2.0・同音等価判定が今回のProductionで仕様どおり機能したかの調査。**調査のみ、API 0、Production code/Prompt/設定/Ledger/音声の変更禁止、新Trial禁止**)。並行agent: 同管理ID 委任_05(Std KP「take part」調査、同run dirを読み取り中、調査書`KP_TAKE_PART_INVESTIGATION_01.md`)。**本委任はSSOTを編集しない**(調査書と報告のみ)。両agentとも同じrun dirを**読み取りのみ**。

## 性質/到達上限/禁止
- 性質: 不具合調査(14節 step1〜4)。到達上限=原因特定(1〜6のどこか)+是正案/判断候補の提示。
- 禁止: 有料API、Ledger/Phrase List/読みの追加・変更、例外ルール追加、Production変更、SSOT編集、`git add -A`等。費用JPY0。
- 「コード上の定数が2.0であるだけでは正常動作の証拠としない」「証拠が無い項目は未確認と明記」「GitHubコードで確認できること/ローカル実行ログでしか確認できないことを区別」を厳守。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_委任_06.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「BYUS-PRODUCTION-E2E-01 委任_06」を含む最新index)。check結果1行。T-2: TTSなし。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_PROPER-NOUN-PHRASELIST_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_06(固有名詞・Ledger・Phrase List調査)`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
# Claude Code／Fableへの指示
## Family X 漫画AI（byUs）— 固有名詞・Pronunciation Ledger・Azure Phrase List調査

### 1. 調査目的

対象：Family X「漫画のキャラクターとAIで会話（byUs）」

Production run：`run_byus_01`

Advanced Full Story第1部・第3部で、ASRが以下のように認識した。

- byUs → Bias／BIOS／Buy Us／Byus／Baias／BAYAS／FAYAS
- LINE → Lion

これらの認識不一致によってTTS再試行が発生した。

**既存の固有名詞対策・読み登録・Azure Phrase Listが、今回のProductionで正しく機能していたか調査する。**

### 2. 必須確認事項

**① 固有名詞としての認識**

- `byUs` と `LINE` は固有名詞として抽出・分類されていたか。
- どの工程で、どのような分類結果になったか。
- 抽出されていなかった場合、その理由は何か。

**② Pronunciation Ledger／Phrase Listへの登録**

各語について、以下を確認する。

- Pronunciation Ledgerに登録されていたか。
- canonical spellingと登録された読み方は何か。
- 読み方の根拠・登録経路は何か。
- Azure Phrase Listに実際に渡されていたか。
- 渡されたPhrase Listの具体的な内容は何か。

**Pronunciation Ledgerへの登録と、Azure Phrase Listへの投入を区別して報告すること。**

**③ 重み2.0の実際の適用**

Repoでは `er006_secondary_asr_01.py` に以下の設定が存在する。

- `AZURE_PHRASE_LIST_WEIGHT = 2.0`
- Phrase Listが空でない場合、`setWeight(2.0)` を実行

確認すべきこと：

- 今回のAdvanced第1部・第3部で実際にこの経路が使用されたか。
- 各Azure呼び出し時のPhrase List内容と重み設定。
- `setWeight(2.0)` が実行された証拠。
- 設定されていたが期待どおりに認識されなかったのか、そもそもPhrase Listに対象語が存在しなかったのか。
- retry／Secondary再実行でも同じ設定が維持されていたか。

コード上の定数が2.0であるだけでは、正常動作の証拠としない。

Azure内部の重み付け効果そのものが直接観測できない場合は、**APIに渡した設定の確認と、実際の認識精度の評価を分けること。**

**④ 不一致・再試行への影響**

第1部・第3部の各Takeについて、次を整理する。

- Primary／Secondary ASRの転写結果
- 固有名詞が原因となった不一致
- 固有名詞以外の不一致
- 同音等価判定等が発動したか
- 最終PASS／NGとTTS再試行の理由

特に、`byUs → Bias／Buy Us` のような同音の可能性がある表記差が、なぜ既存の同音許容機構で解決しなかったのかを確認する。

### 3. 原因分析・Fable独立評価

問題が見つかった場合は、以下のどこに原因があるか特定する。

1. 固有名詞の抽出・分類
2. Pronunciation Ledgerへの読み登録
3. Azure Phrase Listへの受け渡し
4. 重み2.0の適用
5. ASR結果の同音等価判定
6. TTS自体の発音

単に「ASRが特殊な固有名詞に弱い」で終了しない。

Fableは原因分析と証拠を独立検証し、品質・再試行削減・量産単価への影響を評価する。

### 4. 作業範囲・STOP条件

今回は**調査・原因分析のみ**。

- 有料のTTS／ASR再実行は行わない。
- Productionのコード・Prompt・設定を変更しない。
- 未承認の読み方や例外ルールを追加しない。
- 新たなTrialを開始しない。
- 既存ログ・成果物・コード・承認履歴を再利用する。

原因が既存承認仕様からの逸脱だった場合は、是正案を提示する。新仕様・品質基準の変更が必要な場合はユーザー判断へ上げる。

### 5. 報告形式

まず以下の比較表を提示する。

| 確認事項 | byUs | LINE |
|---|---|---|
| 固有名詞として抽出・分類 | | |
| Pronunciation Ledger登録 | | |
| 登録された読み | | |
| Azure Phrase List投入 | | |
| Azure重み2.0の適用 | | |
| 実際のASR認識 | | |
| 問題・原因 | | |

続いて、以下を簡潔に報告する。

1. **既存の固有名詞対策は仕様どおり機能していたか。**
2. **重み2.0は今回の実行で適用されていたか。**
3. **なぜbyUs／LINEの認識不一致を解決できず、TTS再試行に至ったか。**
4. **既存仕様内で是正可能か、新たなユーザー判断が必要か。**
5. **再発防止によって削減可能と見込まれる再試行・費用・時間。**

GitHubのコード上で確認できることと、ローカルProduction実行ログでしか確認できないことを明確に区別する。

**証拠が存在しない項目は推測でPASSにせず、「未確認」と明記する。**
--- 原文ここまで ---

## 手がかり(鵜呑みにせず証拠で確認)
- 既存調査: `docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/ADV_FULLSTORY_RETRY_ANALYSIS_01.md`(第1部/第3部の各attempt転写・判定。再利用し再抽出しない)。
- 固有名詞対策の仕様: CURRENT_SPEC.md:1829(固有名詞ASR不一致の自動PASS条件: CMU辞書一致のみ自動PASS、辞書外はPronunciation Ledger lookup/Perplexity研究→Human Reviewパッケージ充実のみ、自動PASS根拠にしない)。Pronunciation Ledger=`er006_output/pronunciation_ledger_01/ledger.json`、resolver=`er025_pronunciation_resolution_core_*`(telemetry `er025_output/pronunciation_resolution_core_telemetry_01/telemetry.jsonl`)、`er006_pronunciation_research_01.py`、固有名詞抽出(entity extraction)のコード箇所。
- Azure Phrase List: `er006_secondary_asr_01.py`(`AZURE_PHRASE_LIST_WEIGHT`、`setWeight`、phrase list構築元=どの語が入るか[entity list? Ledger? KP?])、Family Z側PL2.0配線(`FAMILY-Z-AZURE-PHRASELIST-WEIGHT-2-PRODUCTION-01`、wire evidence `dgi.bias=2.0`)とFamily X経路の違い。**実行証拠**: 今回runのAzure呼出記録(`b1b/audit/tts_generation_results.json`のsecondary記録、`er007_output`/`er021_output/.../telemetry.jsonl`、`raw_usage_log.jsonl`のazure行、attempt_history)にphrase list内容/weightが記録されているか。記録が無ければ「ローカルログでも未確認(記録機構なし)」と明記。
- 同音等価判定: `classify_asr_match`/semantic_equivalence(`er021_*`、HOMOPHONE_EQUIVALENT、CMU/metaphone等)。「byUs」(造語、読み"bias")が辞書外でどう扱われたか、「Bias」との同音判定がなぜ成立しなかったか(canonical "byUs"の発音推定が無い/辞書外は不一致扱い等)をコードと実ログで。第1部attempt3は一次ASR"Byus"でHOMOPHONE_EQUIVALENT=PASS→どの規則で通ったか(大文字小文字/連結の正規化?)。第3部attempt3はAzure"bias"で救済(secondary_confirmed)→Azureが"bias"と転写した根拠(Phrase Listに"byUs"が入っていれば"byUs"と出るはず→入っていなかった可能性)。
- 「LINE→Lion」(第1部attempt2 Azure)の扱い: 一般語のため固有名詞抽出対象外か。
- Writer原稿の "It is pronounced “bias.”" の文(本文に読みが明示されている)がASR判定の文脈で使われるか(使われない=仕様)。

## 手順
S1. 固有名詞抽出工程の実行証拠(run dir内のentity/pronunciation関連audit json)で byUs/LINE の分類結果。S2. Ledger登録状況(ledger.json内の該当entry有無、登録日時・経路・読み・source・confidence)。S3. Phrase List: 構築コード(どの集合から作るか)+今回runで実際に渡された内容(ログ有無)。S4. 重み2.0: setWeight経路が今回のAzure呼出で通ったことを示すログ(無ければ未確認)。retry/secondary再実行での維持。S5. 各attemptの不一致を「固有名詞起因/それ以外」に分け、同音等価判定の発動有無と理由。S6. 原因の所在(1〜6)を証拠付きで特定(複数可)。S7. 是正案(既存仕様内か新仕様か、QCD影響、削減見込み: 今回は第1部/第3部で各2回の余分なTTS+ASR+cooldown 20分=費用概算を実測raw_usage_logから算出)。
S8. 調査書`docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/PROPER_NOUN_PHRASELIST_INVESTIGATION_01.md`(ユーザー§5の比較表を先頭に、各セルに「確認済み(出典)/未確認(理由)」)。secret scan→明示add(調査書・delegation_log 2件)→commit(`FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_06: byUs/LINE 固有名詞・Ledger・Phrase List・重み2.0・同音判定の実行証拠調査(API 0、SSOT未編集)`)→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_FXBY6.md 上書き)
比較表→ユーザー§5の1〜5(各2〜5行)→原因の所在(1〜6)と証拠→GitHubコードで確認/ローカルログでのみ確認/未確認の区別一覧→調査書path・commit・raw URL→判断候補(「判断候補」表記)→4行判定。