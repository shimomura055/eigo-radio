FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_12(Part 2 Trial-07: 文法解説は最大1件・該当なければ0件、前置/基礎接続の矛盾解消、引用文連結不具合の別対策、追加API上限12円)。あなたはsonnet-worker。Fable(PM)からの委任。ユーザー統合指示原文は§9に逐語(Part 1正式採用の節も含む。**全文を`docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_USER_05.md`へ逐語保存**。Part 1の配線は別agentが並行して担当するので本委任では触らない)。

## 0. 位置づけ
- 承認: Trial-07実施承認(ユーザー2026-10-25)。合格しても到達上限は**VALIDATED**。Production配線禁止。正式採用は別途ユーザー判断。
- 前回Trial-06(委任_11、EVAL_06/ADOPTION_NOTE_06/PREREGISTERED_CRITERIA_06/DESIGN_06/run_trial_06.py/analyze_06.py/posthoc_06.py/analysis_06.json/OUTPUT_06_*_STEPA_DEV.json)は事前登録基準で不合格(2/6)。原因=(1)Prompt内矛盾(FRONTの定義に副詞節を例示しつつ基礎項目に基本的な接続)で許容集合外14件中10件がbefore/after+節のFRONT (2)中クラス追加条件が埋め草を落とせず (3)同一クラス制約が逆効果 (4)強クラス拾い漏れ2標本(開いた窓r2=次段落の引用を連結して返しresolve失敗→P21脱落/賢者r2=features2件のみ) (5)分類コードの揺れ。1件目(強クラス)は難所5作品15標本中14標本で中核文。
- **費用: 追加API上限12円**(厳守、予約方式ガード使用、Trial-06で実装済み)。案件累計上限はFable権限で35→50円へ引き上げ(BUDGET_LOG_01に記録)。モデル=gpt-6-luna(従来と同一、最新世代推奨系)。有料は`.venv\Scripts\python.exe`、無料は`py`。
- 並行agent: Part 1配線設計(同じ`docs/research/FAMILY-Z-STUDY-TEXT-TRIAL-01/`配下に`PART1_WIRING_*`を書く。あなたは`*_07*`のみ書く)/ FX-CORE-NUMERIC / FZ-NARRATION-CHUNK / FZ-SOURCE-ESSENCE / Family Y音声化。SSOT編集は直前再Read・最小Edit・衝突時再適用。

## 1. 承認済み選定方針(ユーザー§3)
- 文法解説は**最大1件。解説する価値のある英文がなければ0件**。件数を満たすための無理な選定禁止。2件目の選定ロジック廃止。
- 「最も難しい文」を機械的に選ぶだけでなく、解説する学習価値を確認する(Trial-06の決定論的分類方式を基礎に、承認仕様に必要な範囲で見直す。承認済み品質基準は変更しない)。
- 前置/基礎接続の矛盾解消: `Before A, B`/`After A, B`のように文頭に従属節があるだけでは難文扱いしない(単純な文頭配置だけを根拠にしない)。一方、文頭要素が複雑な構造・解釈上の難しさを生んでいる場合まで一律除外しない。→ 分類定義とPromptを整合させ、FRONTの採否条件を事前登録で明文化する。
- 引用文連結不具合(開いた窓r2): 文法選定とは別に扱う。原因特定→本文中の対象英文を正しく抽出(既存の抽出・検証機構=`resolve_verbatim`系・段落境界・引用符処理を優先活用)→不正な連結・改変を防ぐ(例: 返却英文が単一段落内の連続span であることの検証、段落をまたぐ連結の検出と再解決)→**回帰テスト**(Trial-06のOUTPUT_06_open_window_r2のケースを固定データとして再現しPASS)で再発防止確認。単発の手動修正にしない。

## 2. 事前登録(有料前にcommit): `PREREGISTERED_CRITERIA_07.md`
- 作品: Trial-06の既存6作品(開いた窓・イグ・ノーベル・賢者の贈り物・猿の手・告げ口心臓・二十年後)+未使用の既存本文から新ホールドアウト1〜2作品(難所あり1、可能なら平易1。Family Z作品または Family X記事のAdvanced既存本文。新規生成禁止)。各作品の許容集合(0件が正解の作品は「許容=∅」)を本文を読んで生成前に登録(Trial-06の許容集合は継承、二十年後=∅の扱いを明記)。
- 合格条件: 全標本で「選定が許容集合内(中核または可)または正しく0件」、許容集合外の選定0、0件が正解の作品での選定0、中核がある作品での0件(見落とし)0、引用連結・改変0(抽出検証PASS)。安定性=同一作品の標本間で選定一致率を記録(判定補助)。
- 終了条件: 不合格でも追加Trialを自動実施しない(原因と改善見込みを報告)。
- 標本数と費用配分: 上限12円内で設計(例: Step A''≈0.5円/call→7〜8作品×N=2〜3、Step Bは合格時に各作品r1で選定1件の4点解説≈0.2円/call)。Trial-06との比較可能性を保つため、既存6作品はN=3を優先し、予算が足りなければホールドアウトをN=2にする等、配分理由を記す。予約合計が12円を超える起動はしない。
- Prompt例は全対象作品の本文以外から作りassert(前回どおり)。

## 3. 実装・実行
- `run_trial_07.py`(run_trial_06.pyから派生: 2件目ロジック削除、FRONT条件・基礎項目の整合、学習価値確認の欄[例: `teaching_value`=何を学べるか1句+`misread_target`]、抽出検証と連結検出、費用ガード予約方式)、`analyze_07.py`、`test_trial_07.py`(selftest+引用連結回帰テスト+0件経路テスト)。無料でtest PASS→commit→有料Step A''→合否→合格時のみStep B(Trial-04基準の4点解説、学習者向け表記、開発者語禁止)。
- 出力: `OUTPUT_07_<work>_r<n>_STEPA_DEV.json`、`OUTPUT_07_<work>_r1_USER.md`/`_DEV.md`(合格時)、`analysis_07.json`。

## 4. 記録・SSOT・Git
- `DESIGN_07.md`、`EVAL_07.md`(作品別0/1件の選定英文逐語と理由、誤選定・見落とし、引用連結対策結果、Trial-06からの改善、安定性)、`COMPARISON_07.md`(Before=03d/06、After=07、合格時はStep B全文無編集)、`ADOPTION_NOTE_07.md`(Status候補、量産単価=Step A''+Step B円/セット、開示事項)、`BUDGET_LOG_01.md`(上限引き上げ・実費・案件累計・日次把握分)。
- SSOT: OPEN-497更新、DECISION_LOG 1件。新規UDRは登録しない(Fableが付ける)。scratchpadバックアップ・`git diff --stat`確認。
- `docs/pm/RESULT_PACKET_FZST12.md`、`docs/pm/ACTIVE_TASK.md`自行(gitignore)。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 528 --out docs/pm/delegation_log/2026-10-25_FAMILY-Z-STUDY-TEXT-TRIAL-01_DELEGATION_12.md`(冒頭「FAMILY-Z-STUDY-TEXT-TRIAL-01 委任_12」で照合、不一致なら±5)。`check_delegation_prompt.py`はFAIL想定(非blocking)。
- Git: `git status`→対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`→`git commit --only -- <path…>`→`git push origin HEAD:main`。secret grep 0件。commitは最低2回(事前登録・結果)。Production file変更0。

## 5. STOP条件
上限12円超過見込み / 重大品質問題 / 仕様変更が必要 / Production変更が必要。

## 6. 報告(Fableへ)
(1)設計要点(1件/0件方式、FRONT条件、学習価値確認、連結対策)とTrial-06からの差分 (2)作品・許容集合 (3)作品別×標本の選定(0件は理由)・許容集合との関係・安定性 (4)誤選定・見落としの有無 (5)引用連結不具合の原因・対策・回帰テスト結果 (6)合否(事前登録基準)とStep B全文(合格時) (7)実費・call数・上限12円対比・案件累計・量産単価・モデル (8)Status候補(VALIDATED/REJECTED/USER_DECISION_REQUIRED候補)と、不合格時の原因・改善見込み (9)変更ファイル・commit・raw.githubusercontent.com URL (10)RESULT_PACKET 4行+「判定整合: 重大NG= / 主因= / 是正対象= / STOP理由= / 提示=」1行。

## 9. ユーザー統合指示原文(逐語、USER_05.mdへ全文保存)
# Claude Codeへの統合指示
## Family X/Z 英語学習解説｜Part 1正式採用・Part 2 Trial-07

### 1. 決定事項・目的

以下の2件を、1委任で並列に進めてください。

**A. Part 1：Vocabulary & Expressions**

- Trial-04で検証した**案α（英語表現のみを別LLMに渡して解説を生成する方式）を正式採用**する。
- Status：**APPROVED_FOR_PRODUCTION**
- Family X/Zの対象Production経路へ配線し、必要な検証を完了させ、PRODUCTION_WIREDまで進める。
- ユーザー承認済みのTrial-04案αを採用し、未承認の追加改善や品質基準変更は行わない。

**B. Part 2：Grammar & Sentence Structure**

- 文法解説の対象を**最大1件、該当がなければ0件**とする方式でTrial-07を実施する。
- 件数を満たすための無理な選定は禁止。
- Status：Trial実施承認。合格しても到達上限はVALIDATED。
- Production配線は禁止。正式採用には別途ユーザー判断が必要。

Part 1とPart 2は独立して進行させ、不要な待機・直列化を避けること。

### 2. A：Part 1正式採用・Production Wiring

#### 採用仕様

Trial-04の案αを正式採用する。

- Key Phraseの英語表現のみを、解説担当の独立LLMへ渡す。
- 本文中の意味に過度に引きずられず、表現の一般的・中核的な意味から説明する。
- 必要に応じて、一般的な使用場面、自然な組み合わせ、類義表現との違いなどを説明する。
- 学習者にとって有益な、正確で実用的な解説とする。
- 本文に固有の用法だけを、その表現の一般的な意味として扱わない。
- 存在しない用法、根拠のない使用頻度の断定、不要な水増しを避ける。

Trial-04で残った `at a moment's notice` の軽微な即応性寄りの表現は把握済み。今回の採用判断により、これだけを理由とする追加Trialは不要。

ただし、既存の品質検査や意味整合性の確認は維持する。

#### Production配線

- Trial-04で検証した案αのPrompt・入力条件・モデル構成を基本として正式Productionへ反映する。
- TrialとProductionの仕様差分を確認する。
- Key Phrase確定後に解説を生成する。
- 英語表現の一般的な意味を説明する担当LLMへ、本文・本文中の日本語意味など、今回分離した情報を再投入しない。
- ユーザー向け出力には、確定済みKey Phrase、本文中の意味、本文引用英文、日本語訳、解説を適切に組み合わせる。
- 既存のKey Phrase選定・日本語意味確定などの工程を不要に変更しない。

**注意：Trial-04で未解決だった「本文引用英文の日本語訳」の生成元については、既存仕様・正式経路を再調査すること。**

既存の承認済み方式で解決可能なら、それを利用する。新しい品質仕様や追加の有料生成工程が必要な場合は、QCD影響とともにユーザー判断へ上げる。未承認の新仕様を暗黙に採用しない。

#### Production Wiringの受入条件

以下を確認する。

1. Family X/Zそれぞれの正式Production経路への配線
2. retry／fallback／regeneration／resumeとの整合
3. 本文・Key Phrase変更時の適切な再生成制御
4. 正式runtimeでの実際の発火証拠
5. 使用モデル、Prompt、入力、routingの証拠
6. 必須Validator／Regression／Integration TestのPASS
7. 既存Production仕様との整合およびDangling Referenceの不存在
8. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSの更新
9. Git反映およびFableによる独立受入評価

全条件を満たしたFamilyのみPRODUCTION_WIREDとする。コード実装やDEVテストだけで完了扱いしない。

### 3. B：Part 2 Trial-07

#### ユーザー承認済みの選定方針

**文法解説は最大1件。解説する価値のある英文がなければ0件。**

- 難しい構文があり、英語学習者に説明する価値の高い英文だけを選ぶ。
- 適切な対象がなければ0件とし、無理に選ばない。
- 2件目の選定ロジックを廃止する。
- 「最も難しい文」を機械的に選ぶだけではなく、解説する学習価値を確認する。
- 既存の承認済み品質基準を独断で変更しない。

#### 文法分類の矛盾解消

Trial-06で判明した「前置」と「基本的な接続」の判定矛盾を解消する。

例えば、以下は文頭に従属節があるという理由だけでは難文扱いしない。

- `Before A, B`
- `After A, B`

単純な文頭配置だけを根拠として選定しない。

一方、文頭に置かれた要素が複雑な構造や解釈上の難しさを生んでいる場合まで、一律除外する必要はない。

Trial-06の決定論的分類方式と既存の評価記録を踏まえ、今回の承認仕様に必要な範囲で見直すこと。

#### 引用文連結不具合への別対策

Trial-06で、1件目の選定英文に次段落の引用を連結する不具合が1件発生した。

これは文法選定の問題とは別に扱う。

- 原因を特定する。
- 本文中の対象英文を正しく抽出する。
- 不正な連結・改変を防ぐ。
- 既存の抽出・検証機構を優先活用する。
- 回帰テストで再発防止を確認する。

単発の手動修正ではなく、同種の不具合を防げる必要十分な対策とする。

### 4. Trial-07の実施・評価

- Trial-06の既存6作品と未使用の既存本文を活用する。
- 生成前に合格条件・終了条件を固定する。
- 過去Trialとの比較可能性を維持する。
- 作品ごとに0件／1件の選定結果と理由を確認する。
- 学習価値の低い文の誤選定を確認する。
- 学習価値の高い文の見落としを確認する。
- 引用文連結不具合の解消を確認する。
- 選定の安定性と量産単価を評価する。
- Fableが独立評価する。

**Trial-07の追加API予算上限は12円。**

承認済みのTrial範囲内で、呼出回数・再利用・並列化を最適化する。

予算超過、重大な品質問題、仕様変更が必要な場合はSTOPする。

不合格の場合は原因と改善見込みを分析して報告する。追加Trialを自動実施しない。

### 5. 全体のQCD・実行方針

優先順位は **品質（Q）＞速度（D）＞量産単価（C）≫開発費用**。

- Part 1のProduction WiringとPart 2 Trialは、依存しない範囲で並列に進める。
- 今回の2件を理由に、他の進行中のFamily X/Z開発を不合理に停止させない。
- 共通基盤の変更や生成物の書き込みなど、衝突する処理のみ適切に制御する。
- 量産単価70円／記事セットの目標を維持し、両工程の追加原価を計測する。
- 承認済みの品質基準を満たしたら、それ以上の磨き込みや追加Trialは行わない。
- 開発上の軽微な不具合は承認範囲内で自律的に修正・検証する。

なお、Part 1の正式採用は、そのために必要な新しい未承認仕様の採用まで包括承認するものではない。

### 6. Closeout・報告

Fableによる独立評価を経て、以下を報告する。

**A. Part 1**

- Production Wiringの完了状況（Family X/Z別）
- Trial-04案αと正式runtimeの仕様一致
- runtime evidence、テスト結果
- retry／fallback／regeneration／resumeとの整合
- 未解決事項と量産単価
- Status：PRODUCTION_WIRED、または未達の理由

**B. Part 2**

- Trial-07の合否
- 作品別の選定英文（0件の場合は理由）
- 不適切な選定・見落としの有無
- 引用文連結不具合の対策結果
- Trial-06からの改善
- 実費、量産単価
- Status：VALIDATED／REJECTED／USER_DECISION_REQUIRED

**重要：Part 1は正式採用済み、Part 2はTrial段階であることを明確に区別すること。**

Part 1が完了したら、Part 2の終了を待つ必要はない。独立してCloseout・報告してよい。