管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02A(Opus条件Aレビュー反映→DESIGN_02、ユーザー原文の復元保存、Closing/Gate lane[text core]の実装・test・小額evidence)。並行して委任_02B(別agent)がrunner/audio/routing/scope laneを実装する。**ファイル所有を厳守**(§5)。

## 0. 読むもの
`docs/pm/PM_BRIEF.md`、`docs/pm/ACTIVE_TASK.md`(本案件節のみ更新)、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{SPEC_LEDGER_01,EXISTING_SPEC_CHECK_01,PROMPT_GATE_ALIGNMENT_01,DESIGN_01,OPUS_REVIEW_REQUEST_01,BUDGET_PLAN_01,OPEN_TRACKING_01}.md`、`er110_family_y_persona_text_trial_01.py`(376-414, 557-665)、`er110_family_y_persona_pipeline_01.py`(997-1083)、`er110_family_y_redelivery_revision_01.py`(112-122, 415-460)、`er012_b_family_voices_a2_production_01.py`(342-374)、`er110_family_y_closing_general_trial_01.py`、`prompt_closing_general_02.txt`(sha 4713ceff…)、案B正本 `docs/research/FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_REVISION_01/REVISION_SCRIPT_01.md`。

## 1. ユーザー原文の復元(Opus確認事項1。Fableのcontextから逐語復元)
`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md`(文字化け版)を`..._USER_RAW_JSONL.md`へ改名退避し、以下をUTF-8で同名ファイルへ逐語保存(内容を要約・改変しない):
<<<USER_TEXT_BEGIN
# Claude Codeへの指示
## Family Y Production正式立ち上げ・XYZ共通仕様統合・差分追跡

**Status：APPROVED_FOR_PRODUCTION**  
**目標：Family Y PRODUCTION_WIRED**  
**優先順位：品質（Q）＞納期・速度（D）＞量産単価（C）≫開発費用**

---

## 1. 目的と基本方針

Family Yを正式Productionとして立ち上げる。

Family Yは、旧Family BのVoices構想を出発点とし、Family XのProduction基盤を利用するFamilyとして設計されてきた。

しかし、その後Family Xおよび全Family共通仕様の改善が進む一方、Family YがTrial段階にとどまっているため、仕様差分が拡大している。

**今回の最優先目的は、この仕様乖離を解消し、現時点で承認済みの適用対象仕様を備えたFamily Y Productionを完成させることである。**

同時に、今後の共通仕様変更についても、Family Yへの配線漏れを防ぐ継続的な管理の仕組みを確立する。

単にFamily Yが1記事生成できる状態になっただけでは完了としない。

既存仕様、ユーザー承認履歴、正式Production経路、品質Gate、後続工程との整合を確認し、Family YとしてPRODUCTION_WIREDを目指す。

---

## 2. 今回正式採用するFamily Yの仕様

### 2-1. Family Yの基本構成

既存のユーザー承認済み設計を維持する。

記事構成は以下を基本とする。

1. 本文リード文
2. Voice 1
3. Voice 2
4. Voice 3
5. Tension＋Closing

Voiceは原則3人・3つの異なる立場とする。

各Voiceは明確な人物像を持ち、その人物の立場・経験・価値観に基づいて、一人称で主観的に語る。

単に記事の論点を3人へ割り振るのではなく、人物像から自然に主張が生まれる構成を守る。

既存の承認済み仕様と照合し、細部を確定すること。

### 2-2. Closing一般化方式

今回、ユーザーが以下を正式採用した。

- 使用Prompt：Closing一般化Trial Round 2のPrompt 02
- 生成モデル：GPT-6.1 Sol
- reasoning effort：high
- 対象：今後のFamily Y Production記事
- Status：APPROVED_FOR_PRODUCTION

Trialで使用したPrompt 02の正式な原文、hash、入力構造、候補選定処理、出力schemaを確認し、それをProductionへ正確に移植すること。

独断でPromptの意味を変更したり、新しいClosing生成方式へ変更したりしない。

Round 2で確認された課題（Gate FAIL、候補順序への偏り、見方の多様性、単価）は既知の課題として記録する。

ただし、今回のProduction立ち上げを理由なく停止させることなく、承認済み品質Gateを満たす正式経路を実現する。

### 2-3. 『宅配の再配達』の個別Closing

『宅配の再配達は有料にすべきか？』については、一般化方式ではなく、**既存の人手設計案Bを正式採用**する。

- 採用案：B「料金は何を動かせるか」
- 当該記事のみの個別採用
- 今後の記事にはPrompt 02の一般化方式を使用する

既存の案Bの正式本文・承認履歴を確認し、誤って案A・案CやRound 2生成案へ差し替えないこと。

当該記事は既に承認されたTrial制作範囲との関係を確認し、残工程を進める。

---

## 3. Family Yへの仕様継承・差分調査【最重要】

実装前に、Repoと過去の承認・Trial・Production記録を確認する。

主な確認対象：

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- PM_GOVERNANCE
- CLAUDE.md
- Family X／Y／ZのProduction実装
- Family Bの旧設計・承認履歴
- 現在進行中のTrial・実装・Production Wiring
- 関連するruntime evidenceとGit履歴

### 3-1. 仕様を分類する

既存仕様を次のように分類する。

**A：全Family共通仕様**

原則Family Yにも適用する。

**B：Family X基盤仕様**

Family Yの構造・目的と整合するものは継承する。

**C：Family Y固有仕様**

既存のユーザー承認を優先して維持する。

**D：Family X／Z固有仕様**

Family Yへ無条件には適用しない。適用の合理性を確認する。

**E：旧Family B仕様**

現行の承認内容と整合するもののみ継承し、旧仕様を無条件に復活させない。

**F：検討中・Trial中・実装進行中の仕様**

現時点のStatusとFamily Yへの将来適用要否を明確に管理する。

### 3-2. 必須の差分管理表

少なくとも以下の項目を含む仕様台帳を作成する。

| 項目 | 記録内容 |
|---|---|
| 仕様ID・名称 | 対象仕様を一意に識別 |
| 仕様分類 | 共通／X基盤／Y固有／Family固有等 |
| 承認Status | REJECTED／VALIDATED／APPROVED等 |
| 承認根拠 | ユーザー判断・Decision Log |
| X／Z配線状況 | Production反映・検証状況 |
| Y適用要否 | 必須／対象外／判断待ち |
| Y配線Status | 未着手／実装中／検証中／完了等 |
| 残作業 | 具体的な未完了事項 |
| 後続追跡先 | OPEN_ITEMS等 |
| 完了証拠 | runtime evidence・test・commit |

この台帳は、今回の立ち上げだけでなく、今後の共通仕様変更時にも参照できる形にする。

---

## 4. 承認済み仕様と進行中仕様の管理

**ここは今回、特に厳格に対応すること。**

ユーザーが懸念しているのは、以下の問題である。

1. 共通仕様の改善が進行中
2. Family Y立ち上げ時にはまだ実装できない
3. Family Y Productionが先に完成する
4. 後日、共通仕様が正式採用・配線される
5. しかしFamily Yだけ未反映のまま放置される

この事態を防ぐこと。

### 4-1. 承認済み仕様

Family Yへ適用する仕様は、原則として今回のProduction立ち上げ時に組み込む。

他FamilyでAPPROVED_FOR_PRODUCTIONとなっている共通仕様については、Family Yも適用対象として管理する。

Family Yへの配線が未完了なら、Family Yを無条件に完全Closeしない。

### 4-2. 進行中・未採用仕様

現在検討中の仕様、VALIDATED段階のTrial、APPROVEDだが未配線の仕様も一覧化する。

ただし、未承認の仕様をFamily Y Productionへ先行採用してはならない。

各仕様について、後日正式採用された場合にFamily Yへ適用する必要があるかを記録する。

必要なものはOPEN_ITEMSで追跡し、正式採用後のY配線・検証まで管理する。

### 4-3. 将来の配線漏れ防止

今後、新しい全Family共通仕様が正式採用された場合は、Family Yを適用対象に含める。

Family X／Zの実装時に、Family Yの適用要否・配線状況も確認する仕組みを整える。

Family Yだけ後回しになる場合は、理由、残作業、解消予定をOPEN_ITEMSへ記録する。

**単に仕様台帳を作るだけでなく、実際の将来の変更・Closeout時に参照される運用とすること。**

ただし、過剰な管理システムや新しい複雑な仕組みを作らず、既存SSOT・Gateを最大限利用する。

---

## 5. 今回特に組み込む共通仕様

現在進行中の改善も含め、Family Yへの適用対象を確認する。

特に重要なものは以下。

### 5-1. Key Phrase

- AIが候補TOP 8を順位付きで選定
- 原則Human Review
- Humanが3件をKey Phraseとして選定
- 当該3件＋追加2件＝5件を単語解説に掲載
- Human不在時はAI TOP 1〜3をKey Phrase、TOP 1〜5を単語解説へ採用
- HumanによるNGとHuman未レビューを区別

### 5-2. 文法解説

- AIがTOP 2を選定
- 原則Human Review
- 基本はTOP 1を採用
- HumanはTOP 2採用・再選定・文法コーナー省略を選択可能
- Human不在時はAI TOP 1を採用

### 5-3. 英語解説

現在進行中の英語解説改善について、承認済み仕様・適用対象・配線状況を確認し、Family Yへ反映する。

特にPart 2文法解説、Trial-08選定方式、Key Phrase英語解説等について、正式採用済み内容と開発中の内容を区別する。

### 5-4. その他の共通品質仕様

以下も漏れなく確認する。

- Key Phraseの語数・本文存在・難易度・汎用性
- ASR発音検査
- 同音・異表記救済
- TTS再生成・Human Review
- 英語／日本語音声の品質対策
- 音声Chunk分割・ポーズ仕様の適用要否
- 数字・固有名詞の取り扱い
- 公開ページの表示・音声構成
- Retry／fallback／resume
- Validator／Regression

この一覧は調査の出発点であり、網羅済みとみなさないこと。

既存の承認済み仕様をRepoから調査して補完する。

Family Yに適さない仕様は、その理由を記録して除外する。

判断が明確にできない場合は、無理に実装せずユーザー判断事項として提示する。

---

## 6. Closing PromptとGateの不整合

Round 2で判明したPromptとLeakage Gateの不整合を整理する。

既知の問題：

- Prompt側の「見えてくることとして示す」という趣旨の指示
- Gate側が「見えてくる」等の解釈表現をFAIL判定する場合がある
- 一方、抽象的な表現やResearch説明への逆戻りは本来防ぐ必要がある

### 対応方針

1. 現行Prompt 02とGateの実際の判定条件を照合する。
2. 過去のFAILを、本文の品質問題とGate側の過剰判定に分類する。
3. 承認済み品質基準を維持する。
4. Prompt変更だけで解消できる問題と、Gate仕様変更が必要な問題を分ける。
5. 必要十分な対策案を整理する。

**今回ユーザーが正式採用したPrompt 02および既存Gateの品質基準を、独断で変更してはならない。**

修正が必要な場合は、変更理由・具体的な差分・QCD影響を提示し、ユーザー判断を得る。

ただし、既存仕様内の実装不具合や判定器への入力ミス等は、委任範囲内で自律的に修正・検証する。

Closing一般化方式を無断でPrompt 03へ変更しない。

---

## 7. Family Y Productionの実装方針

Family Xの正式Production基盤を最大限再利用する。

ただし、Family Yの3 Voice構造や主観的な語りを損なわないこと。

実装方法を過度に固定せず、Claude/Fableが既存コード・QCD・全体構成を踏まえて最適化する。

必要な範囲：

- Family Y正式初回生成経路
- 記事構成・3 Voice生成
- Closing一般化方式
- 英訳・英語解説
- Key Phrase・文法
- TTS・ASR・音声組立
- Human Reviewあり／なし
- 品質Gate・Validator
- 公開ページ生成
- Retry／fallback／regeneration／resume
- SSOT・Git反映

Family Xの処理を流用する場合も、Family Yの記事構造・話者・音声・解説仕様に正しく対応していることを確認する。

DEV／Trial専用の動作を正式Production動作と誤認しない。

また、後続経路だけに参照が残るDangling Referenceを防止する。

---

## 8. 費用見積・予算管理

**有料Production実走前に、Family Y立ち上げに必要な追加API費用を概算して報告すること。**

見積には少なくとも以下を含める。

- 日本語原稿生成
- 英訳
- Closing生成・品質判定
- Key Phrase・文法・英語解説
- TTS
- ASR
- 必要なHuman Review関連の再生成
- 品質検査
- 正式Production E2Eの追加実走
- 合理的なretry・再試行余裕

以下を区別して示す。

1. **正常系で1記事を正式完成させる費用**
2. **必要な検証・再試行を含む立ち上げ総額**
3. **本日の承認済み予算残額**
4. **不足する場合の追加予算希望額**

既存成果物を再利用できる場合は、その前提も明示する。

概算は合理的な精度でよく、過度に精緻な積算によって作業を遅らせない。

ユーザーは、合理的な追加予算を事前に確保する意向である。

ただし、**見積依頼は予算増額の承認ではない。**

承認済み枠内の作業は自律的に進め、上限超過が必要な場合だけユーザーへ判断を求める。

また、今後の量産単価70円／記事セットを継続的な目標とし、品質を維持した原価低減余地を記録する。

---

## 9. 作業順序と並列化

品質・承認条件を守りながら、Production完成までの所要時間を最小化する。

次の作業は可能な限り並列化する。

- 既存仕様・承認履歴の調査
- Family Y差分台帳作成
- 進行中共通仕様の追跡整理
- Closing Prompt／Gate不整合調査
- Family Y Production実装設計
- 有料E2E費用の概算
- 既存コード・テストの再利用準備

ユーザー判断が必要な項目は速やかに提示する。

一方、判断待ち項目と独立して進められる作業は停止しない。

単に工程の順番や日付を理由として、作業を分割・待機させないこと。

---

## 10. Production Wiringの受入条件

Fableは、Claudeの完了報告をそのまま受け入れず、独立して照合する。

Family YのPRODUCTION_WIRED判定には以下を必須とする。

1. 正式初回Production経路に実装されている。
2. Family Y固有の承認済み構成が維持されている。
3. Closing Prompt 02＋GPT-6.1 Sol highが正式経路で実際に使用されている。
4. 正式runtimeのmodel_id・routing・Prompt hashが記録されている。
5. Human Reviewあり／なしの両経路が確認されている。
6. 承認済みの適用対象共通仕様が実装されている。
7. Retry／fallback／regeneration／resumeで仕様が維持される。
8. 必須Regression・Validator・integration testがPASSしている。
9. 正式Production E2Eで実動作が確認されている。
10. 必要なSSOT・Gitが更新されている。
11. 未完了事項・将来適用仕様がOPEN_ITEMSで追跡されている。
12. ユーザー承認内容と実際の出力が一致している。

コードが存在するだけ、単体テストが通っただけ、またはTrial経路で動いただけではPRODUCTION_WIREDとしない。

ユーザーによる記事の最終試聴PASSは、Production Wiringとは別のStatusで追跡する。

---

## 11. Open Item・将来仕様のCloseout

今回の完成報告前に、以下を必ず確認する。

- 承認済みなのにFamily Y未配線の仕様
- VALIDATEDだが採否未決定の共通仕様
- 現在進行中の共通仕様
- Family Yへの将来反映が必要な仕様
- 判断待ちのFamily固有差分
- Closing PromptとGateの未解決事項
- DEV／Trialにしか存在しない機能
- Dangling Reference
- 未反映のSSOT・Git

未完了事項を単に「後日対応」と記載するだけでは不十分。

各Open Itemに、適用対象・Status・残作業・解消条件を明示すること。

正式な共通仕様として採用された際、Family Yにも配線されるようにする。

---

## 12. STOP条件・ユーザー判断

既存仕様・承認Scope・予算内の不具合や実装上の問題は、Claude/Fableが自律的に原因究明・修正・検証する。

次の場合はSTOPし、判断事項を報告する。

- Family Yへの適用可否が曖昧な重要仕様
- Family固有設計との重大な衝突
- 承認済み品質基準の変更
- Closing Prompt 02・Gateの意味的変更
- 新仕様の正式採用が必要
- 承認予算の超過
- 重大な品質・安全上の問題
- Production正式経路の構築を妨げる重大blocker

ユーザーへは、技術的な軽微事項ではなく、仕様・品質・費用・Scopeに関わる重要判断のみを求めること。

---

## 13. 報告方法・到達目標

まず、以下の初期報告を提出する。

**初期報告**

1. Family Yの既存仕様と、Family X／XYZ共通仕様との差分一覧
2. Family Yへの適用／除外／判断待ちの分類
3. 現在進行中・今後適用予定の共通仕様一覧
4. Closing Prompt／Gate不整合の整理と対応方針
5. 正式Production立ち上げの実装計画
6. 正式E2E実走を含む追加API費用概算
7. ユーザー判断が必要な事項

この初期報告を待つ間も、承認範囲内の独立作業は並行して進めること。

**最終報告**

- Family Y正式ProductionのStatus
- 承認済み仕様の配線状況
- 正式runtime evidence
- 品質検査・Regression結果
- Human Reviewの動作結果
- Closing Prompt／Gateの整合状況
- 実費と量産単価見込み
- Family別の共通仕様追跡状況
- SSOT・Git反映結果
- 残Open Item
- Fable独立受入評価
- ユーザー最終試聴に必要な公開URL

**最終目標は、Family Yを現在の承認済み共通仕様に整合した正式Productionとして立ち上げ、将来の共通仕様変更でも取り残されない状態を実現することである。**

ただし、現在検討中で未承認の仕様は先行採用せず、正式採用された時点でFamily Yへ確実に適用する追跡管理を行うこと。

品質を守りながら、可能な限り最速で完了させてください。
USER_TEXT_END>>>
復元後、台帳YL-C03/C06〜C08の承認根拠を原文の節番号(§2-1, §7「記事構成・3 Voice生成」等)で逐語参照に更新。

## 2. Opusレビュー(逐語を`OPUS_REVIEW_01.md`に保存。要点)
- 結論: 新規er121(Z stage形式)は妥当。M-1〜M-6反映後に実装着手可。
- **M-1(実装不具合、Phase 0の「不具合0」は誤り)**: `er110_family_y_persona_text_trial_01.py:376-381,405-414` kind="tension"の判定promptは`_TENSION_ITEMS`のみで組み立てられ、その1行目「leak_evidence_subject/leak_discovery_syntax/leak_evidence_memorable: 上記と同じ意味」の「上記」=`_VOICE_ITEMS`が同promptに入っていない(developerにも定義なし)。判定器は3項目を定義なしで推測判定している。旧B英語版(`er012…:342-374`)は全セクション1promptで成立していた→Y版の移植ミス。過去FAIL#3(「見えてくる」discovery_syntax)・#4はこれが原因の可能性(G-2不要になる見込み)。具体案: Production側のtension判定promptで3項目の定義を`_VOICE_ITEMS`から逐語展開(判定基準文言は一字も変えず欠落定義を補うだけ)。DEVは変更しない。Production版とDEV版の差分が「定義の展開だけ」であることをtestで固定。着手前に過去Closing 11件+案B+Lead/紹介Gate(tension項目使用時)を修正後promptで再判定して較正(数円)。案BがFAILになった場合はユーザー判断。
- **M-2**: 既存`run_gate`/`run_gate_pl`のtension書換え規則`TENSION_RULES(_PL)`は旧B骨格(共通→違い→食い違い→締め、1文45字)でPrompt 02出力に当てるとPrompt 02の意味が変わる。`apply_rewrites`のtension経路は一人称検査のみで`check_closing`(175〜245字・1文55字・「？」終わり)を通さない。委任_28先例はCLOSING_RULESへ差替え+CLOSING_POST_GATE_STOPで再検査。具体案: 書換え規則はsha固定Prompt 02の【最終パートの書き方】節をマーカーで切り出して逐語使用+選定済み切り口(`new_view`+`evidence_quotes`)+run_gate共通「指摘箇所だけ直す」。書換え後は`check_closing`+記号・タグ検査必須、2回失敗で`REWRITE_STOP`。`closing_record`に書換え有無・生成時sha・最終sha。判定≤3・LEAKAGE_RESIDUAL_STOPは承認範囲内。書換え経路はTrialで未通過→過去FAIL稿(R1宅配gen_1、R2宅配H2)を入力に書換え経路のruntime evidenceを取る(新規生成不要、数円)。
- **M-3**: 共通工程(Zの`stage_kp` er026:1839-1954=約120行、`run_tts_stage` er063:1367〜)の「相当版」をYに書くと将来の配線漏れが再発。(a)DESIGN_02にstageごとの「直接importする共通関数」と「Y固有新規範囲(テキスト生成・segment計画・timeline順・role文のみ)」の境界表。(b)構造一致test: er026/er019の対応stageが呼ぶ共通module呼出しを静的抽出しer121と比較、意図的差分は台帳ID付き許可リスト。(c)STOP/RUN_LOCKは`er062_family_z_structure_01.py`の関数(`check_stop_sentinel`/`acquire_run_lock`/`record_launch_and_check_storm`等)をimport。
- **M-4**: KP HRは「stage 8の直後」ではなくKP呼出そのものを`er119_kp_wiring_01.run_kp_with_review`(`sc.run_key_phrases`互換、family引数)に置き換え、XのPENDING(rc=4)/NotConfirmed(rc=4)/Inconsistent(rc=3)入口確認・`verify_selection_matches_outputs`・`part1_items`も同形で最初から入れる。文法HR/Part 2(er120)のみ接続点として残す。
- **M-5**: 台帳漏れ: Source Reference Contract(X=候補ID方式、Z=D1)、YのKP引用文参照方式、gloss再整合(OF-229/`EIGO_KP_GLOSS_ALIGNMENT`)、gloss人称Gate(ITEM1)、gloss HR、Run Entity Table(OPEN-472)、TTS予算wrapper、mock時attempt_history隔離。スコープ判定基準の明文化: (i)Family非依存でYの明示除外なし→適用(PNAP/er109/基本形化例外、開示事項) (ii)Family別パラメータ方式→Y用方式承認まで「除外+OPEN記録」(Chunk。「判断待ち」より正確) (iii)明示除外→除外(中核数値v4/J2)。
- **M-6**: `voices`段(Voice生成+Voice Gate)のProduction runtime evidenceが計画にない→E-3でSNSのTheme Packageから`voices`段を実行(既存テーマ、約20〜26円、Cap 150円内)。
- R-1 案B固定registryはslugだけでなくTheme Package sha(f0d0af…)とVoice R0 `article_ja.md` sha(566ebd97…)にも紐付け、Voice変更時は注入せずSTOP。Gateは同shaの既存PASS記録(`closing_B/gate/gate_result.json`)を来歴検査付きで再利用(M-1で判定promptが変わった場合のみ再判定)。`check_closing`も適用。R-2 E-3はSNSで`english`・`plan`まで。R-3 model_id照合はer006既存の実model照合関数を流用。英訳は`FAMILY_Y_TRANSLATE_*`(値はX定数参照+drift test)。R-4 Voice Gate書換えpromptは題材非依存の`build_voice_rewrite_prompt_pl`系。R-5 配線漏れ防止: item33は28-2運用2と重複→正本はCURRENT_SPEC「共通仕様のFamily別配線Status表」に一本化しM-5の漏れ行を追加、`spec_ledger_01.json`は立上げ作業表としY PRODUCTION_WIRED時に廃止、コード強制はM-3(b)。R-6 原価: cached_tokens実測、flex/Batchの可否確認(未確認)。R-7 routing key名を先に確定しL1/L2を並行、Closing段+routing完成時点でE-3(M-2書換えevidence含む)を先行。C-1〜C-7 問題なし(X拡張/DEV昇格不採用、Prompt 02 byte一致+sha照合・schema・決定論検査・再生成1回・CONTRACT_STOP、I-2/I-3/I-4、Lead/紹介にTension専用2項目非適用、除外の妥当性、Y segment ID新設+網羅test[page・assembly・Master store keyまで]、G-1〜G-3/P-1のユーザー判断整理)。ユーザー確認: (1)原文復元(本委任§1で解決) (2)M-1再判定で案BがFAILの場合のみ (3)G-1提示時はY版`leak_tension_reverts_to_research`が旧B原文のFAIL条件(「survey/研究結果の紹介・数字比較が主たる内容ならFAIL」)と括弧内観点を欠く=「移植時の欠落の復元」に近い旨を添える。70円超過・Chunk非適用は実測後の報告事項。

## 3. Fable確定判断
M-1〜M-6・R-1〜R-7すべて採用。M-1はユーザー指示§6「判定器への入力ミス等は委任範囲内で自律的に修正・検証」に該当=Production版で定義展開(DEV不変)、較正で案BがFAILならSTOPしてユーザー判断。Chunkは「除外+OPEN記録」へ分類変更。配線漏れ防止の正本はCURRENT_SPEC配線Status表(PM_GOVERNANCE項目追加提案は取り下げ、28-2運用2の補強として記述)。

## 4. 本委任(02A)のScope
A. `OPUS_REVIEW_01.md`保存、`DESIGN_02.md`(M/R反映、M-3(a)境界表、routing key名を**確定**: `FAMILY_Y_CLOSING_GENERATE`[gpt-6.1-sol, effort high]、`FAMILY_Y_LEAK_JUDGE`[gpt-6-luna]、`FAMILY_Y_VOICE_GENERATE`、`FAMILY_Y_VOICE_REWRITE`、`FAMILY_Y_LEAD_GENERATE`、`FAMILY_Y_PERSONA_INTRO`、`FAMILY_Y_TRANSLATE_*`[X定数参照]。er006への登録は02Bが行うので名前・model・effortの表をDESIGN_02 §routingに書く)、`SPEC_LEDGER_02.md`+json(M-5漏れ行追加・基準(i)〜(iii)明文化・Chunk再分類・YL-C03根拠逐語)、`BUDGET_PLAN_02.md`(M-6 voices段+M-1較正+M-2 evidence加算、Cap 150円)、`OPEN_TRACKING_02.md`。
B. 実装(新規ファイル `er121_family_y_text_core_01.py`+test): Prompt 02のbyte一致コピー+sha照合(test・runtime)、入力block組立・schema・決定論検査・再生成1回・`CLOSING_GENERAL_CONTRACT_STOP`の逐語移植(er110からimportしない)、Production tension判定prompt(M-1定義展開、DEV差分=展開のみのtest)、Gate呼出(`run_gate`骨組み: 判定≤3・局所書換え[M-2: Prompt 02節逐語+切り口+指摘箇所のみ]・`check_closing`+記号検査・REWRITE_STOP・LEAKAGE_RESIDUAL_STOP・gate_history全保存・closing_record)、案B固定registry(R-1: slug+Theme Package sha+Voice R0 sha+承認ref、env/CLI無効、Gate既存PASS再利用+来歴検査、局所書換え禁止)、Voice Gate書換え(R-4 `_pl`系移植)、routing呼出はDESIGN_02のkey名で`er006`の関数を参照(02Bが登録するまでtestはmock。routing未登録時fail-closedをtestで固定)。
C. 小額evidence(有料、`.venv\Scripts\python.exe`、Cap 150円内・各call前に`py tools/stop_scope_check_01.py --managed-id FAMILY-Y-PRODUCTION-LAUNCH-01 ...`): (1)M-1較正: 過去Closing 11件(R1 4+R2 6+案A初回)+案B+Lead/紹介(tension項目使用時)を修正後promptで再判定、旧判定との差分表(`GATE_CALIBRATION_01.md`)。案BがFAILなら以降の案B関連を止めてSTOP報告。(2)M-2書換え経路evidence: R1宅配gen_1・R2宅配H2を入力に局所書換え→再判定→check_closing(`REWRITE_EVIDENCE_01.md`)。見積合計約5〜15円。日次累計を起動前に確認(1,500円上限、並行案件控除)。
D. SSOT: OPEN-520更新(Opus反映・M-1不具合発見・較正結果)、OPEN-484/463最小追記、Chunk除外のOPEN記録、DECISION_LOGにM-1修正方針1件。直前再Read・最小Edit・バックアップ。CURRENT_SPEC変更なし(02Bと重複しないよう本委任では触らない)。
E. Git: 対象pathのみadd→`git commit --only`→`git push origin HEAD:main`(non-fast-forwardならfetch→merge→push、競合は両方残しSTOP報告)。禁止: `git add -A/-u`・amend・rebase・force・stash・reset --hard。secret grep 0件。
F. 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_02A.md`(Nは583前後、先頭「管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02A」を578〜605で走査)。Opus依頼文(先頭「管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01。Opus必須レビュー」)も`..._OPUS_REQUEST_DELEGATION_01.md`へ。

## 5. ファイル所有(厳守)
- 02A(本委任)が編集: `er121_family_y_text_core_01.py`(+test)、`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{OPUS_REVIEW_01,DESIGN_02,SPEC_LEDGER_02,spec_ledger_02.json,BUDGET_PLAN_02,OPEN_TRACKING_02,GATE_CALIBRATION_01,REWRITE_EVIDENCE_01}.md`、delegation_log、OPEN-520/484/463、DECISION_LOG(1件)。
- 02B(別agent)が編集: `er121_family_y_runner_01.py`、`er121_family_y_audio_01.py`、`er006`(routing登録)、scope/segment ID/PNAP/er109の共有file、`OPERATIONS_01.md`、構造一致test。**02Aはこれらを編集しない**(読むだけ)。
- 他agentが編集中(読むだけ): `er019/er026/er062/er119/er120`、KP HR・Part 2・JA ASRのdocs。
- 禁止: DEV(`er110_*`)の変更、Prompt 02・Gate基準文言・案B本文の変更、公開ページ・`er0XX_output/`既存成果物の変更、Family Yの有料生成(較正・書換えevidence以外)。

## 6. 報告(RESULT_PACKET_YPL2A.md+口頭要約)
DESIGN_02の要点(境界表・routing表)、M-1較正結果(件数・旧/新判定差分・案Bの結果)、M-2書換えevidence結果、実装ファイル/関数・test件数(API 0証明は遮断harness)、実費、02Bへの引継ぎ事項(I/F)、commit hash・raw URL、RESULT_PACKET 4行+判定整合、判断候補(27-3)。