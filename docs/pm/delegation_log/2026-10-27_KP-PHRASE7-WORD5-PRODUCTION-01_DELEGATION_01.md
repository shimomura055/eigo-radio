## 管理ID

KP-PHRASE7-WORD5-PRODUCTION-01 委任_01(ユーザー正式採用 APPROVED_FOR_PRODUCTION: Key Phrase最大7件+Key Word最大5件の分離抽出・Key Word優先順位5条件・補足/出力規則を、Family X/Y/Z×Std/Advの正式Production経路へ配線する。本委任=**棚卸し(A/B/C)+設計+実装差分計画+Opus条件A依頼文**。read-only。API 0・JPY0。実装・evidence・SSOTは委任_02以降)。並行Agent: (a)LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01 委任_02(`user_test/selection_form_v3/**`、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`、`build_data_01.py`を編集中)、(b)KP-CONFIRMED-CONTENT-PROTECTION-01 委任_01(read-only設計、`docs/research/KP-CONFIRMED-CONTENT-PROTECTION-01/`)。これらのファイルは編集しない(読むのは可)。あなたの所有=`docs/research/KP-PHRASE7-WORD5-PRODUCTION-01/{INVENTORY_ABC_01,CURRENT_PIPELINE_01,DESIGN_01,IMPL_PLAN_01,TEST_PLAN_01,EVIDENCE_PLAN_01,OPUS_REVIEW_REQUEST_01}.md`、`docs/pm/delegation_log/2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_{USER,DELEGATION_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_KP75.md`。コード/SSOT編集なし。pathspec付きcommit。

## 性質/禁止

- 性質: 承認済み仕様のProduction配線の設計=Production Prompt(call1 Prompt 2/call2 Prompt 2-V)・候補数・HR自動推奨・補完計数に跨る構造変更=**Opus条件A必須(実装前)**。到達上限=DESIGN_READY。
- 禁止: 本委任でのコード編集、承認外のフレーズ抽出規則の新設、易語の混入を品質不具合扱いすること、追加Trialの提案を目的化すること、禁止Git操作。
- 時間見込み: 約2h。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文保存+check、結果1行。ユーザー原文(下記)を`..._USER.md`へ逐語保存。T-2/T-3: なし。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_DELEGATION_01.md` をN=701から順に試し(699/700は並行委任)、先頭「## 管理ID」+「KP-PHRASE7-WORD5-PRODUCTION-01 委任_01」のものを採用。

## ユーザー指示(原文・逐語)

# Claude Code指示｜Key Phrase 7件＋Key Word 5件・抽出仕様 Production Wiring

## 1. 目的・正式採用Status

ユーザーが承認したKey Phrase／Key Word候補生成仕様を、Family X/Y/ZのStandard/Advancedすべての正式Production経路に実装し、PRODUCTION_WIREDまで完了させてください。

**Status：APPROVED_FOR_PRODUCTION**
**目標：PRODUCTION_WIRED（X/Y/Z、Std/Adv）**

対象仕様：
- Key Phrase最大7件＋Key Word最大5件の分離抽出
- Key Word抽出の優先順位5条件
- 補足規則・出力規則
- Gate除外補完・KP救済・Human Review・選定フォームとの整合

今回の承認は、以前のTrialで得られたすべての改善案を一括採用するものではありません。

## 2. 候補生成数

- **Key Phrase：最大7件**
- **Key Word：最大5件**
- **合計：最大12件**
- それぞれ学習価値の高い順に順位付けする。
- 件数は上限であり、無理に満たす必要はない。
- 広く候補を抽出し、最終的な採否はユーザーが判断する。
- 易しい単語が一部含まれることは許容し、それ自体を品質不具合や追加Trialの理由にしない。

## 3. Key Word抽出の優先順位【正式仕様】

以下の順序を維持し、AI・Prompt・後続処理で条件の意味や優先順位を変更しないこと。

1. **本文一致（絶対条件）**：本文中に実在する単語だけを、本文に現れる形のまま抜き出す。変更・言い換え・追加・創作は禁止。
2. **1語（絶対条件）**：スペースを含まない1語だけを出力する。2語以上は出力禁止。
3. **上級者向けの学習価値**：上級者でも学ぶ価値のある単語を優先する。
4. **易しい語の除外**：基本語や、上級者なら知っている易しい単語は除外する。ただし絶対条件ではなく、広く候補を拾うため、記事によって易しい単語が含まれることは許容する。
5. **単語単体の学習価値**：意味の明確さ・他の文脈での汎用性・難易度を考慮する。固有名詞・数字・この記事だけでしか使えない語は考慮の際に避ける。ただし必須条件にはしない。

**補足規則**
- 条件3・4を条件5より優先する。
- 条件5を理由に、条件3・4に適合する単語を不当に除外しない。
- **すでに選定されたKey Phraseに含まれる単語は、Key Word候補から除外する。** これは従前の7＋5 Trialからのユーザー承認済み変更。
- 絶対条件は1・2のみ。重複除外は別途承認された候補構成規則として適用する。

**出力規則**
- 最大5件を学習価値の高い順に出力。適切な候補が不足する場合は5件未満でよい。
- 各候補に日本語の選定理由を1文・40字以内で添える。
- 出力直前に本文との完全一致・1語条件を再確認する。
- 語数を記録する。
- 数合わせ目的の不自然な候補追加はしない。

Key Phrase側もTrialで用いた最大7件・順位付け・本文一致等の既存承認仕様を守る。今回未承認の新たなフレーズ抽出規則は導入しない。

## 4. 既存機能との整合

### Gate除外候補補完

すでに承認済みの補完仕様を維持する。

- **AIが実際に選定した候補がGateで除外された場合だけ**補完する。
- Gate除外件数を超えて補完しない。
- 初回選定が7件／5件未満であること自体を補完の発動条件にしない。
- Gate合格候補・救済済み候補は保持する。
- 補完候補にも適切な同一品質条件・Gateを適用する。
- フレーズ枠と単語枠の件数を区別し、最大7＋5を守る。
- 不要な再生成・API再課金を防止する。

### KP救済・Human Review・選定フォーム

- X/Y/Zで配線済みのKP救済方式を維持する。
- Gate、Human Review Lock、retry／fallback／regeneration／resumeとの整合を確認する。
- 学習項目選定フォームv3へ最大12件を正しく渡す。
- ①Key Phrase最大3件、①＋②最大5件、①＋②＋③最大12件、文法は独立最大2件という承認済み上限を維持する。
- 候補の英語表現、**エンドユーザー向け日本語訳**、AIによる選定理由を確認可能にする。
- ユーザーが確定した英語表現、日本語訳、選定区分、文法解説全文を後続工程で無断変更しない。

フォームのユーザー実操作確認待ちという別の受入条件は、本件のProduction配線作業を不合理に停止させる理由にしない。ただしフォーム自体の受入Statusは混同しない。

## 5. 関連Trial・未配線仕様の棚卸し

実装と並行して、以下を確認する。

- `KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01`
- `KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02`
- OPEN-534
- `er124_kp_phrase_word_trial_01.py`
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS
- 現行Production Prompt・候補生成・QA・Human Review・フォーム連携

関連仕様を次のように分類する。

**A：今回の承認内容を成立させるために必要な変更**
→ 承認範囲内で実装。

**B：過去に正式承認されているがProduction未配線の仕様**
→ 承認Scopeを確認し、進められる作業は並行実施。

**C：Trialのみ完了し正式採用されていない独立仕様**
→ 勝手に導入しない。重要なものだけ判断材料を整理して報告。

解決済み事項や今回承認済みの事項を、改めてユーザー判断に戻さないこと。

## 6. 必須検証・受入条件

Family X/Y/Z × Standard/Advancedの全6経路について確認する。

1. 正式初回Production経路で7＋5の分離抽出が実際に適用される。
2. Key Wordの5条件・補足規則・出力規則が承認内容どおりである。
3. 本文一致・1語・フレーズ包含重複除外が機能する。
4. 候補が上限未満でも不必要な補完を行わない。
5. Gate除外時のみ適切な件数を補完し、既存合格候補を保持する。
6. KP救済、QA、Human Review、フォーム連携が正常に機能する。
7. retry／fallback／regeneration／resumeで仕様が維持され、二重生成や確定内容の書換えが起きない。
8. Validator／回帰／統合テストがPASSする。
9. actual model_id、routing、Prompt hash、入力・出力、Gate結果、補完・救済記録などの正式runtime evidenceを取得する。
10. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSおよび必要なGit反映を完了する。
11. Fableによる独立受入評価を実施する。

特定Familyの証拠だけで全FamilyのPRODUCTION_WIREDを宣言しないこと。自然発火を必要とする受入条件についても既存Gateを遵守し、未観測の場合は未観測と報告する。

## 7. QCD・実行方針

優先順位：**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 承認済み品質水準を超える独自基準を追加しない。
- 易しい単語が含まれること自体を新たな品質問題にしない。
- 独立作業は並列化し、不要な待機・日付分割を避ける。
- 既存Trial出力・検証資産を再利用する。
- 量産単価70円／記事セットを目標とし、増分コストを計測する。
- 開発費は原則1,000円／日（JST）および個別承認予算内。
- 承認範囲内の問題は原因究明から修正・再検証まで自律解決する。

**STOP条件：** ユーザー未承認の仕様・品質基準変更、重大な品質・安全問題、予算超過、解決不能なblocker。STOP時も独立作業は継続可能な範囲で進める。

## 8. 完了報告

以下の順に簡潔に報告する。

1. **X/Y/Z・Std/Adv別のProduction Wiring Status**
2. 新7＋5方式の正式runtime生成結果（実候補例付き）
3. 5条件・補足規則・重複除外・Gate補完・KP救済の検証結果
4. Human Review／フォーム／後続工程との整合
5. 品質・制作時間・量産単価の実測または推定
6. 関連Trialの未配線仕様棚卸し（A/B/C）
7. SSOT/Git・Fable受入結果・未完了Open Item

**目標は、今回の承認仕様を必要十分な品質で全FamilyのPRODUCTION_WIREDまで完了することです。追加のTrialや品質基準変更を目的化しないでください。**

(原文ここまで)

## 既知の前提(Fable把握分。必ずコードで再確認)

- 共通経路`er119_kp_candidates_01._generate_candidates_impl`(X=`er019`:452付近、Y=`er121`:562付近、Z=`er026`:1974付近)。call1=Prompt 2(3件、`er105`のattempt内全件再選定 MAX_ATTEMPTS=2)→call2=Prompt 2-V(最大5)→selection gate/CMU/containment(`duplicate_of_top3`)→canonicalization→救済(er125、既定ON)→gloss→RQA→HR(`KP_CANDIDATE_MAX=8`、AI推奨=先頭3件KP、Advは先頭5件=単語解説vocab `er119_kp_human_review_01.py:550-551`付近)。
- Trial資産: `er124_kp_phrase_word_trial_01.py`(P7 sha先頭`2e930193…`、W5 sha先頭`3502f0ac…`、旧W3 `7a9c47a0…`は不採用)。W5の条件順序=①本文一致②1語③上級者向け④易語除外⑤単語単体価値(必須でない)。「KPに含まれる語の除外」がW5本文に含まれているか(P7句を入力して重複回避した事実)を確認し、不足ならPromptへ追加する設計(承認済み)。
- 補完`er119_kp_backfill_01.py`: kind別E_phrase/E_word計数は実装済み。上限定数(3/5?)が7/5へ変わる箇所を特定。
- Trial-01 `STATUS_01.md` §3に採用時の変更点素案(Prompt置換・sha固定test更新・`KP_CANDIDATE_MAX`不整合・単語が自動採用に届かない問題)あり。11-7限定例外(既定OFF flag)はPrompt直接編集に不適用=本件は正式採用済みのため既定ONの正規実装。

## 実施事項

1. **現行パイプライン(`CURRENT_PIPELINE_01.md`)**: call1/call2のPrompt定数・sha固定test・attempt loop・Gate・containment・救済・補完計数・HR自動推奨・Adv vocab5・フォームexport(`export_form_data_01.py`の読み取り項目)までを、ファイル:行で列挙。X/Y/Zの呼び出し差(Z特有SRC D1・人称整合、Y OPEN-484一般化配線の現状)。
2. **棚卸し(`INVENTORY_ABC_01.md`)**: Trial-01/02・OPEN-534・er124・SSOT(Grep `KP_CANDIDATE_MAX|Prompt 2-V|7＋5|7+5|OPEN-534|単語枠|P7|W5`)・現行Prompt/QA/HR/フォーム連携から関連仕様をA/B/Cに分類。Cは重要なもののみ判断材料(例: Trial-01の「有用閾値Y/B」「猿の手Adv偏り」は今回ユーザーが「易語許容・追加Trial不要」としたため判断不要と明記)。解決済み/今回承認済みを判断に戻さない。
3. **設計(`DESIGN_01.md`)**: (a)call1→P7(最大7、順位付け、本文一致、既存承認仕様のみ)、call2→W5(5条件+補足+出力規則: 理由1文40字以内・語数記録・出力直前再確認・数合わせ禁止・KP含有語除外)。Prompt本文は承認原文の条件をそのまま反映(順序変更禁止)。(b)件数: 候補最大12(`KP_CANDIDATE_MAX`→12、shortfall定義、HR依頼書/フォームへの12件受渡し)。(c)kind=phrase/wordを候補docに明示(DATA_CONTRACT `kind`既存)、ai_rankはフレーズ→単語の順、HR自動推奨(先頭3=フレーズ)・Adv vocab5の単語組入れ=現行の挙動をどう維持するか(承認済みUI上限①≤3/①+②≤5/①+②+③≤12との対応。新しい表示変更が必要なら「新仕様判断」として分離)。(d)Gate: 本文一致・1語(validate)、フレーズ包含重複除外(Prompt+containment Gateの二重)、CMU/canonicalization/gloss/RQA/救済は単語にも現行どおり。(e)補完: E_phrase上限7・E_word上限5、発動=E≥1かつ初回上限到達(上限未満は不発動)、補完Prompt=P7/W5再利用+exclusion note。(f)attempt loop(er105 MAX_ATTEMPTS=2)はP7で維持。(g)retry/fallback/regeneration/resumeで二重生成なし(候補doc存在時のskip規則)、確定内容保護(並行設計KCP1)との境界。(h)sha固定test更新一覧、`EIGO_KP_BACKFILL`と新実装の関係(新flag不要=承認済みのため既定ON。ただし旧3+5への復帰手段を残すか=設計判断としてFableへ提示、推奨付き)。(i)費用: +¥0.19〜0.4/level(Trial実測)の見込みと量産単価への影響。
4. **実装計画(`IMPL_PLAN_01.md`)**: 変更ファイル・関数・行・テスト・順序(並列可能単位)。並行Agent所有ファイル(export tool/フォーム)への変更は「委任_03でフォーム側へ引継ぎ」と分離。
5. **test/evidence計画**: 受入条件1〜9の各々に対するtest(unit/golden/DefaultOn)と、6経路のruntime evidence取得方法(既存run dirのコピーへのKP stage単独実行で本文TTS再課金を避ける等。見積¥/経路、合計≤¥60、1,000円/日内)。自然発火が要る項目(Gate除外→補完)は「未観測なら未観測と報告」。
6. **Opus論点(`OPUS_REVIEW_REQUEST_01.md`)**: Prompt置換の影響範囲/attempt loopとP7の整合/containment二重化/補完計数の7・5/HR自動推奨とAdv vocab5/resume二重生成/sha固定test/旧方式復帰手段の要否/費用。

## 事前指定Read一覧

- `er119_kp_candidates_01.py`(全体構造+Grep `PROMPT|sha|KP_CANDIDATE|containment|duplicate_of_top3|backfill|rescue` ±10)、`er105*`(Grep `MAX_ATTEMPTS|PROMPT_2|sha256` ±10)、`er119_kp_backfill_01.py`(Grep `E_phrase|E_word|MAX|cap|7|5` ±5)、`er119_kp_human_review_01.py`(Grep `KP_CANDIDATE_MAX|auto|vocab|ai_rank|shortfall|render_request_md` ±10)、`er124_kp_phrase_word_trial_01.py`(Prompt定数P7/W5全文、`make_p7_replay_factory`)、`er125_kp_rescue_production_01.py`(構造)
- `docs/research/KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/{STATUS_02,PROMPT_DIFF_01,PROMPT_SELFCHECK_01}.md`、`docs/research/KP-CANDIDATE-PHRASE7-WORD3-TRIAL-01/STATUS_01.md` §3、`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/{DESIGN_02,DATA_CONTRACT_01}.md`、`docs/research/LEARNING-ITEM-SELECTION-FORM-V3-PRODUCTION-01/DATA_MODEL_01.md`
- SSOT Grep: `CURRENT_SPEC.md` `Prompt 2-V|KP_CANDIDATE_MAX|候補生成|Gate除外補完` ±5、`OPEN_ITEMS.md` `OPEN-534|OPEN-545|OPEN-546|OPEN-549` ±3、`DECISION_LOG.md` `7＋5|7+5|KP候補` ±3

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_DELEGATION_01.md --json-out ...\_check.json`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし(委任_02以降で付与)。`RESULT_PACKET_KP75.md`にOPEN-534更新文案・DECISION_LOG文案(APPROVED_FOR_PRODUCTION 2026-10-27)。

## Git

- commit message: `KP-PHRASE7-WORD5-PRODUCTION-01 委任_01: 7+5分離抽出のProduction配線 設計・A/B/C棚卸し・実装計画・Opus依頼(read-only、API 0)`。trailer: `Delegation: KP-PHRASE7-WORD5-PRODUCTION-01/01`。push。

## 報告

`docs/pm/RESULT_PACKET_KP75.md`: (0)T-0、(1)現行パイプライン要点、(2)A/B/C棚卸し、(3)設計要点(a)〜(i)+Fable設計判断事項(旧方式復帰手段・HR推奨/Adv vocab扱い等。推奨付き)、(4)実装計画・test/evidence計画・費用見積、(5)Opus論点、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案、commit hash・raw URL。末尾10行要約。