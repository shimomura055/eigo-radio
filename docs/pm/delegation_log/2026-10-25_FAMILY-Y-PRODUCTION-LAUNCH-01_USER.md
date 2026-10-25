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
