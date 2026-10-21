# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_07(調査のみ・費用上限JPY0・API呼出0・コード/仕様/成果物/Ledger変更なし: 記事B run_byus_01でASRが`byUs`を`Buy Us`/`by us`等と認識した際に、既存の発音同等性判定で救済できなかった直接原因・根本原因を、実行記録とProductionコードで特定し、既存仕様との整合を分類し、最小是正案を提示する)。
並行agent: `PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01 委任_01`(ledger.json・er006系codeを**変更中**)。本委任は読み取りのみ。Ledgerの「事象当時の状態」は、同agentが作るバックアップ(`er006_output/pronunciation_ledger_01/`配下のbackup、または`git show HEAD:er006_output/pronunciation_ledger_01/ledger.json`)を参照し、作業treeの変更中ファイルを根拠にしない。コードも`git show HEAD:<file>`基準で行番号を引く(作業tree差分がある場合は明記)。SSOTは編集しない。Git操作はT-0・原文・調査書のcommitのみ(共有プロトコル)。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_BYUS-EQUIVALENCE_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_07(byUs発音同等性判定の救済失敗原因調査)`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
## Claude Code指示：ByUsのASR発音同等性判定・救済失敗の原因調査

**目的：** Family Xの記事Bで、ASRが `ByUs` を `buy us` または `by us` と認識した際に、既存の発音同等性判定で救済できなかった原因を特定する。

**今回は調査のみ。コード修正・仕様変更・追加Trialは行わない。費用上限0円。**

### 1. 実際に起きた事象の確認

記事B `run_byus_01` の実行記録を確認する。

- 原稿中の `ByUs` に対し、Primary（OpenAI）が実際に何と認識したか
- Secondary（Azure）が何と認識したか
- `buy us` / `by us` / その他の表記が、それぞれどの音声・attemptで出現したか
- Validatorの判定結果と、最終的に救済されたかどうか

推測ではなく、実際の原稿・ASR出力・判定ログを対応させて示す。

### 2. 発音同等性判定が機能しなかった原因

以下をProductionコードとruntime evidenceで調査する。

1. **正解発音の取得**
   - `ByUs` の正しい発音をValidatorはどこから取得する設計か
   - Pronunciation Ledgerに発音ヒントがない場合、発音辞書・音素変換・その他の仕組みが機能するか
   - `ByUs` のような造語・ブランド名をどう扱う仕様か

2. **発音同等性判定**
   - `ByUs` と `buy us` / `by us` が、それぞれどの比較・正規化・音素判定を通るか
   - 複数単語への分割、CamelCase、同音異綴りへの対応状況
   - 既存のHomophone判定、Semantic Equivalence、M1複数発音候補、Connected Speech Equivalenceなどが発動したか
   - 発動しなかった場合は、どの条件で除外されたか
   - 発動したのに救済されなかった場合は、どの条件でNGになったか

3. **ASR Cascadeとの関係**
   - Primary／Secondaryの結果がどのように統合されたか
   - Azure Phrase Listが空だったことが、発音同等性判定に影響したか
   - 重み2.0の設定とは切り分けて説明する

### 3. 根本原因と既存仕様の整合

CURRENT_SPEC・DECISION_LOG・過去Trial・Production実装を照合し、原因を分類する。

- 承認済み仕様の実装漏れ
- 実装済み機構の発動条件・接続漏れ
- 発音情報の供給不足
- 既存仕様で未対応のケース
- 実際には発音が異なり、救済すべきでないケース

**重要：表記が異なるだけで発音が同じなら、原則として救済対象。ただし、正しい発音が未確定の場合に推測でPASSさせない。**

### 4. 報告・受入条件

以下を簡潔に報告する。

1. `ByUs → buy us / by us` の実測結果
2. 既存Validatorで救済されなかった直接原因
3. その原因が生じた根本原因
4. 既存のどの仕組みが機能し、どの仕組みが機能しなかったか
5. 既存仕様の範囲で解決できるか、新仕様の承認が必要か
6. 同種の固有名詞・造語にも影響する問題か
7. 最小限の是正案と、品質・速度・量産単価への影響

実行記録、該当コード、SSOTの根拠を示すこと。

Fableにも原因分析と是正案の妥当性を照合させる。

**到達Status：調査完了・是正案提示まで。Production変更は禁止。**
--- 原文ここまで ---

## 固定ブロック
E-1/D-1/G-1/F-1: 標準(SSOT全文読込禁止)。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_委任_07.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「BYUS-PRODUCTION-E2E-01 委任_07」を含む最新index)。check結果1行。T-2: TTSなし。

## 既存調査(再利用し再抽出しない。足りない部分だけ実ログを引く)
- `docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/ADV_FULLSTORY_RETRY_ANALYSIS_01.md`(第1部/第3部 各attemptの転写・判定)、同`PROPER_NOUN_PHRASELIST_INVESTIGATION_01.md`(委任_06: 救える形[1語対1語CMU同音 Bias/Byus/bias]と救えない形[①2語化 Buy Us/by us→stopword除去で"us"対"byus"、多語→1語の同音比較は未実装 ②BIOS別発音 ③Baias/BAYAS/FAYAS辞書外]、Ledger英語hint空、Phrase List空、entity_like=先頭大文字条件)、`docs/research/FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01/`(①是正: 複数差分時の個別許容、`Buy Us`は拡張せず従来どおりNG)、`docs/research/FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01/TRIAL_RESULT_01.md`(J3測定: 多語化3例中、転写側をBiasに置換した反実仮想で2/3がPASS。腕MでPhrase Listに"byUs"を入れるとAzureの"Buy Us"が"byUs"に単語化しNG→PASS 1例)。
- 実ログ: `er019_output/family_x_audio_production_wiring_01/manga_ai_chat_byus__run_byus_01/b1b/audit/tts_generation_results.json`(`segments.full_story_part1/part3`の各attempt: primary/secondary転写・判定・semantic_equivalence・cascade_steps)、`er021_output/en_asr_semantic_equivalence_production_wiring_01/telemetry.jsonl`(EN semantic equivalence発動記録)、`er025_output/.../telemetry.jsonl`(resolver)、`er011_output/attempt_history.jsonl`該当行。

## 調査観点(コードは`git show HEAD:`基準でfile:行)
1. 正解発音の取得設計: Validatorが"byUs"の発音をどこから得るか(CMU `pronouncing`辞書→"byus"が収録?[委任_06はCMU上byus=B AY1 AH0 Sで"bias"と同音と報告、要再確認]/Ledger hint[空]/M1[CMU未収録語限定なので対象外]/G2P等の音素変換の有無)。造語・ブランド名の仕様(CURRENT_SPEC.md:1829 固有名詞自動PASS条件A/B、IPA→ARPAbet近似禁止、OPEN-83)。
2. 同等性判定の経路: `classify_asr_match`→`protected_check`(diff span、stopword扱い、entity_like)→`_step_alternate_pass`/`cmu_alternate`(1語対1語のみ?)→M1→EN semantic equivalence(`er021`、content_word/homophone_only/protected_number等の分類)→Connected Speech対策(どの関数、対象条件)。"byUs"対"Buy Us"(Primary側Azure)と"by us"で、トークン化(stopword "by"除去→"us"対"byus")・CamelCase分割の有無・多語→1語同音比較の有無・同音異綴り(buy/by=B AY1)の扱いを、実際のdiff spanと関数の分岐で追う(可能ならHEADコードで当該canonical/転写をoffline実行し分岐を記録=API 0)。
3. Cascade統合: 一次NG→二次評価→統一judge(`er078`)でのNG_BOTH/secondary_not_acceptedの条件、Phrase List空の影響(Azure転写が"Buy Us"になった要因としてのみ関係、判定ロジック自体には無関係であることの切り分け)、重み2.0との切り分け。
4. 分類(ユーザー§3の5区分)と根拠。「表記が異なるだけで発音が同じなら救済対象/未確定なら推測PASS禁止」に照らし、"byUs"の正しい発音が**確定していない**(英語公式発音なし、公式は日本語「バイアス」)点をどう扱うべきかを事実として整理(判断はユーザー)。
5. 同種への影響(CamelCase/小文字始まり造語/多語に割れる固有名詞の一般性、過去runでの出現例をattempt_historyからGrep)。
6. 最小是正案(提案のみ、各案に: 既存仕様内か新仕様か/変更箇所/品質[誤PASS増のリスク]/速度/量産単価/再試行削減見込み)。候補例: (a)多語→1語の同音比較を**既存CMU同音層の範囲内で**拡張(連結した転写トークン列のARPAbet連結がcanonicalの発音と一致する場合のみ)=判定基準の拡張に当たるか要分類 (b)Ledger英語hint供給(PNEP Trialの結果、J7依存) (c)Writer側でCamelCase造語の扱い(原稿で読みを示す等=原稿仕様)。Fable/ユーザー判断用に長短を並べる。

## 成果物
調査書`docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/BYUS_EQUIVALENCE_INVESTIGATION_01.md`(ユーザー§4の1〜7の順、根拠file:行・ログ行付き)。secret scan→明示add(調査書・delegation_log 2件)→commit(`FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_07: byUs発音同等性判定の救済失敗原因調査(API 0、Production変更なし)`)→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_FXBY7.md 上書き)
ユーザー§4の1〜7(各3〜6行)→分類(§3の5区分のどれか、複数可)→判断候補(「判断候補」表記)→commit・raw URL→4行判定。