FABLE-DELEGATION-MARKER: PNPS-PLAN-B1-委任_01-20261022

# 委任(PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_01 [B-1]: 固有名詞の正しい発音情報を「必要時のみ」取得・登録・再利用する仕組みの改善計画策定。計画のみ・API 0・JPY0・Trial/Production/Ledger無変更)

## 0. 運用ルール・並列注意
- 別agent(A-1: 多語同音救済のProduction実装設計)が同時に `docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/`・`er094_*`・`DECISION_LOG.md`・UDR #138・OPEN-439・`docs/pm/delegation_log/2026-10-22_PNMH-PRODUCTION-WIRING-AND-PRONUNCIATION-SUPPLY-PLAN-02_USER.md`(ユーザー原文全文の保存はA-1が行う。あなたは作成しない)へ書く。あなたの成果物は新dir `docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/` に置く。共有ファイル(`OPEN_ITEMS.md`/`docs/pm/REPORT_LEDGER.md`)編集前に `git status` → 該当行を再Grep → 自分の行だけ編集 → 即 `git add <file>` + commit。`index.lock`は30秒待って再試行。
- `git add -A/-u/-f`、amend、rebase、force push、stash、clean、reset --hard、checkout -f 禁止。secret_scan `--staged` hits=0。push=`git push origin HEAD:main`。一時ファイルはforce-add禁止。SSOT全文読込禁止。他人の未commit差分を混ぜない。有料API(Perplexity/LLM/TTS/ASR/Web検索)呼出禁止。

## 1. ユーザー原文(2026-10-22)のうちB関連部分(逐語)
---
### 3. B：固有名詞の発音取得方式の改善計画

#### 背景

当初の改善目的は以下2つをセットで解決することだった。

1. 1語⇔複数語の同音判定を可能にする。
2. 比較対象となる固有名詞の正しい発音情報を取得できるようにする。

1はTrial成功・正式採用済み。

2は前回の計画で切り離されたが、**改善対象から取り除くことはユーザーの意図ではない**。

今回、2の具体的な改善計画を策定する。

#### 設計方針

**必要な場合だけ発音を調査・登録・再利用する低コスト方式**を基本とする。

検討項目：

1. 既存Ledger・CMU辞書・発音取得機構の調査と再利用。
2. 発音情報が不足している固有名詞を検出する方法。
3. 調査が必要な条件と不要な条件の定義。
4. 公式情報・信頼できる辞書・公式音声等の調査優先順位。
5. 複数の発音候補がある場合の扱い。
6. 正しい発音をIPA・音素列等へ変換する方法。
7. Ledgerへの登録、情報源・信頼度の管理。
8. 登録済み情報のキャッシュ・再利用。
9. 発音情報が取得できない場合の自律的な解決方法。
10. 既存の同音判定Validator・ASR Cascadeとの統合方法。
11. Family X/Zおよび将来のFamily Yへの共通適用。
12. 誤PASS・過剰NG・量産費用への影響。

特に、`ByUs`のように、辞書に同じ綴りの別人名が存在しても、それだけでブランドの公式発音を確定できない問題を解決すること。

AIによる推測のみで発音を確定しない。

#### 検討すべき重要な観点

- すべての固有名詞を事前に検索する方式は避ける。
- 既存辞書で確実に解決できる場合は余計な調査をしない。
- 辞書未収録でも、必ずしも毎回Web検索する必要があるとは限らない。
- 過去に検証済みの発音情報を最大限再利用する。
- 不確実な発音を自動登録して、以降の量産で誤PASSを繰り返すリスクを防ぐ。
- Human Reviewは最後の手段とし、自律的に解決できる問題はAI側で処理する。
- 追加費用が必要な場合は発生頻度を踏まえ、1記事セット当たりの期待原価で評価する。
- 量産単価70円／記事セットの目標を踏まえる。

この設計方針より優れた方法があれば、Claudeから積極的に提案すること。

#### Fable独立レビュー

Claudeの設計案に対してFableが独立レビューを行う。

評価観点：

- 正しい発音情報を取得できるか
- 誤った発音を確定・登録するリスク
- 不要なWeb検索やLLM呼出の有無
- 既存機構との重複
- 同音判定拡張との整合
- 未知の固有名詞への対応力
- 再利用・キャッシュの有効性
- Failure時の適切な自律対応
- Family X/Z共通適用
- QCDと実装複雑性
- より単純・安全・低コストな代替案

レビューで見つかった問題は計画に反映する。必要十分な計画となった時点で完成とし、過剰な再レビューは行わない。

#### 今回の到達点

- 改善方式の比較と推奨案
- 既存機構との具体的な統合設計
- Trial方法・合格基準
- 品質リスクと対策
- 開発費・量産単価への影響
- Fableレビュー結果
- 残るユーザー判断事項

**Bは計画提出まで。Trial・Production実装を無断開始しないこと。**

### 5. 最終報告(B部分)
- 推奨する方式と理由
- 具体的に、いつ・どうやって発音情報を調査するか
- 発音の正しさをどう保証するか
- Ledgerへの登録・再利用方法
- 既存の同音救済との連携
- Fable独立レビュー結果
- Trial計画と概算費用
- ユーザー判断が必要な事項

**報告では管理番号だけを使わず、必ず課題の具体的な名称を示すこと。**
---
(原文全文の保存先=`docs/pm/delegation_log/2026-10-22_PNMH-PRODUCTION-WIRING-AND-PRONUNCIATION-SUPPLY-PLAN-02_USER.md`[A-1が作成]。出典として参照してよい。)

## 2. 既存資産(必ず調査・再利用。鵜呑みにせず再照合)
- 前計画のL2検討: `docs/research/PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01/{INVESTIGATION_01.md, DESIGN_OPTIONS_01.md(案B1/B2/B3、L2縮小案), PLAN_SUMMARY_01.md}`、`demand_oov_result_01.json`(辞書外需要)、`rule_domain_result_01.json`。
- PNEP Trial(固有名詞英語発音供給、K1 byUs未達・安全終了、JPY113.10、UDR #133 Fable推奨(イ)見送り): `docs/research/FAMILY-XZ-PROPER-NOUN-EN-PRONUNCIATION-SUPPLY-TRIAL-01/{TRIAL_DESIGN_01.md, TRIAL_RESULT_01.md}`、OPEN-434。
- 既存機構: Pronunciation Ledger(`er006_pronunciation_research_01.py` Perplexity調査Prompt・confidence基準[本人音声source=high、テキストのみ=medium以下]、登録時validator[PRONUNCIATION-LEDGER-INVALID-ENTRY-REMEDIATION-01、OPEN-436]、`human_approved`/`hint`構造)、CMU辞書アクセス(`er008_asr_variant_hardening_15_homophone_en.py`、`pronouncing`)、Case A `PROPER_NOUN_ENTITY_ARPABET_CONFIRMED`、Case B(Ledger lookup→Human Reviewパッケージ充実のみ、自動PASS根拠にしない=CURRENT_SPEC:1837)、A7登録読み保護(CURRENT_SPEC:2817/2820)、Azure Phrase List供給(`er006_secondary_asr_01.py` L75-111)、M1複数発音候補(`er006_m1_multi_candidate_01.py`)、Human Review表示ルール(a)〜(f)(CURRENT_SPEC:1837)、固有名詞判定基準「英語圏で許容できる発音集合」(ER-008-N8-…-16)、IPA→ARPAbet近似自動PASSの禁止(CURRENT_SPEC:1837)、OPEN-83(外部発音根拠とTTS実音声の自動照合は未実装)。
- 多語同音救済L1(採用済み・配線中、A-1): 純関数`multiword_span_equivalent_v3`。L2はこれに「原稿側の正しい音素列」を供給する層。
- 承認済み原則: ASR consensus≠発音検証(1837)/AI推測のみで確定しない/Human Reviewは最後の手段(PM_GOVERNANCE 14節)/量産単価70円目標/#133・#134(Perplexity枠)は未回答(Statusを変えない)。

## 3. 作業
1. 既存調査: 上記資産を読み、「発音情報が不足している」が実際に起きた事例(byUs、Kristie Tse、Stephen Reicher、Mullos/Melos、iCapital、FamilyMart等)と、Ledger/CMU/Case Aで解決済みの割合を、保存データ(`demand_oov_result_01.json`、telemetry、Ledger)から**費用0で**定量化(独立記事数・固有名詞数・辞書外数・Ledger命中数・Human Review到達数)。
2. 方式比較(最低5案+ユーザー方針より優れる案があれば追加): 例=(P1)反応的調査: Primary/Secondary不一致かつ辞書外/entity_likeのときのみ、Ledger→(なければ)1回限りの調査→登録・再利用/(P2)Writer段での「読み併記」要求(記事Bの型)/(P3)Phrase List供給のみ/(P4)ASR側の多候補転写から音素列を逆算し候補集合として保持(確定せず)/(P5)公式音声(公式動画・PR音声)のASR転写から発音を抽出/(P6)人手登録の軽量UI(Human Review最後の手段)/(P7)複合=Ledger階層(human_approved>公式音声>公式テキスト>辞書>未確定)+未確定はPASS根拠にしない。各案に: 取得できる正しさの保証/誤登録リスク/不要な検索・LLM呼出/既存機構との重複/L1との連携(音素列の供給形式)/未知語対応力/キャッシュ・再利用/Failure時の自律対応/X・Z・将来Y共通/QCD・複雑性/1記事セットあたり期待原価(発生頻度×単価、出典付き。未確認は未確認)。
3. 推奨案の統合設計: いつ(トリガー条件・不要条件)/どうやって(調査優先順位: 本人・公式音声>公式プロフィール/公式表記の読み>信頼できる辞書>一般的英語圏発音。日本語公式読み[例: バイアス]の扱いはJ7未回答のため「ユーザー判断事項」として分岐を残す)/正しさの保証(confidence階層、AI推測のみ不可、`PASS根拠にできる階層`と`Human Reviewパッケージ用途のみの階層`を分ける)/IPA・音素列への変換(IPA→ARPAbet近似自動PASS禁止との整合: 禁止されるのは「近似での自動PASS」。完全一致・人間承認済みのみ根拠にする等)/Ledger登録・情報源・信頼度・有効期限/キャッシュ再利用(記事横断)/取得不能時の自律対応(Writer読み併記→再TTS/構成変更/最後にHR)/Validator・Cascade・M1・Phrase Listとの統合点(ファイル:行)/Family共通化(呼出点は統一judge側)/誤PASS・過剰NG・費用影響。**ByUs問題の解き方を具体例として通して書く**(CMU姓収録だけで確定しない→公式情報源は日本語読みのみ→どう扱うか)。
4. Trial計画: 既存成果物の再利用(PNEP Trialの調査結果、Trial音声)、対象語、合格基準(正しい発音の取得率、誤登録0、不要呼出数、HR到達数、1記事あたり期待原価)、費用概算(出典付き)、STOP条件、Production採用はユーザー。
5. レビュー論点(Fableレビュー用): ユーザーの11観点に沿って、自己評価と残論点を1表に。
6. 成果物: `docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/{INVESTIGATION_01.md, DESIGN_OPTIONS_01.md, PLAN_01.md(統合設計+Trial計画+費用), REVIEW_POINTS_01.md, PLAN_SUMMARY_01.md(1画面)}`。SSOT: `OPEN_ITEMS.md`へ新OPEN(次番号、`POST_USER_VALIDATION`、Status=`PLAN_DRAFT_PENDING_FABLE_REVIEW`、#133との関係を明記[#133のStatusは変えない])、`docs/pm/REPORT_LEDGER.md`行追加。DECISION_LOG・CURRENT_SPECは書かない。
7. T-0保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02_委任_01.md`(Nは jsonl 内で `FABLE-DELEGATION-MARKER: PNPS-PLAN-B1-委任_01-20261022` を含むAgent tool_useの0始まり通番、A-1[241前後]の次=242前後)。`check_delegation_prompt.py`実行(見出し不一致FAILは既知の偽陽性)。
8. commit(対象のみ)→push→到達確認。`docs/pm/ACTIVE_TASK.md`先頭に固定ヘッダ。`docs/pm/RESULT_PACKET_PNPS1.md`へ報告(ユーザー§5 B部分の順で要約+定量化結果+レビュー論点+RESULT_PACKET 4行+JPY0+raw URL)。

## 4. 禁止
Trial実行・Production/Ledger/Validator/Prompt変更・有料API禁止。#133/#134/J7のStatus変更禁止(未回答のまま、分岐として扱う)。AI推測で発音を確定する設計の提案禁止。管理番号だけの表記禁止(課題名を併記)。