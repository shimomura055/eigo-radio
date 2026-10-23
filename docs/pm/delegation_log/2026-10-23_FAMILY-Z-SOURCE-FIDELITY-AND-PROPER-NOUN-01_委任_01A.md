FABLE-DELEGATION-MARKER: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01-委任_01A-20261023

# 委任_01A: 『開いた窓』原作結末欠落の根本原因調査(区分A)+原作の本質を守る包括対策の設計案(調査・設計のみ、API費用0、Production/Prompt変更禁止)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_委任_01A.md`(N≈325〜335、先頭行MARKER一致確認)。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_USER.md` に逐語保存(本委任Aが担当。並行の01Bは保存しない)。
3. ACTIVE_TASK.md: 別agent複数が並行中(FAMILY-Y 委任_02、ASR-HOMOPHONE 委任_05、速度Trial 委任_03、本件01B)。編集直前に再読込し、「並行タスク: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_01A(原因調査・設計)」の1行追加のみ。
4. 並行する委任_01B(固有名詞ルール改定のSSOT反映+Trial)とは成果物・SSOT行を分ける。本委任のSSOT編集はOPEN_ITEMSの新item 1行(原作忠実性、Status=`INVESTIGATED_DESIGN_PENDING_OPUS`)とREPORT_LEDGER 1行のみ。CURRENT_SPEC/DECISION_LOGは触らない(01Bが固有名詞ルールを反映する)。

## 1. ユーザー指示原文(逐語)
```
# Claude Codeへの統合指示:Family Z 原作忠実性改善・固有名詞ルール改定

## 1. 目的・背景

Family Zの古典文学作品について、**原作の本質的な魅力を維持しながら、英語学習者が楽しめる自然なStorytellingを実現する。**

今回、『開いた窓(The Open Window)』のStandard/Advancedで、原作最後の重要な一文が欠落していることが判明した。

> Romance at short notice was her speciality.

これは、Veraが即興で作り話をする人物であることを明かし、作品全体の意味を完成させる重要なオチである。

現行版は犬に関するVeraの作り話で終了しており、原作の種明かしが失われている。

ユーザー判断:

**これは細部の省略や演出上のアレンジではなく、作品の根幹を損なう改変である。古典作品を採用する意義を失わせるため、許容しない。**

また、現在の固有名詞削減方針についても、『開いた窓』ではFramton以上に物語の仕掛けを担うVeraの名前を残すべきとの判断が示された。

この2つの問題を統合して調査・改善する。

対象はFamily Zのみ。

## 2. 作業全体の区分・Status

今回の作業は以下の3つに区分する。

### A. 原作結末欠落の原因究明・包括対策設計

- 状態:調査・設計
- 新しい包括対策のProduction採用:未承認
- 到達可能Status:調査完了/USER_DECISION_REQUIRED
- 新仕様の無断Trial・Production実装は禁止

### B. 固有名詞ルール改定

以下の共通方針をユーザーが正式承認した。

**Status:APPROVED_FOR_PRODUCTION(仕様決定)**

> 固有名を使うのは基本的に主人公のみとする。ただし、それ以外に物語の中心人物、展開・結末の理解に重要な人物については、主人公・脇役の区別によらず原作の名前を維持する。

これは現行仕様の原則を維持し、必要最小限の例外を追加する改定である。

固有名詞の使用を積極的に増やす趣旨ではない。

### C. 2作品での検証

対象:

- 『開いた窓』Standard/Advanced
- 『走れメロス』Standard/Advanced

新ルールをTrial環境で検証する。

Trialの成功は正式Production配線完了を意味しない。

**Bの正式採用と、CのTrial評価を区別して管理すること。**

## 3. 原作結末欠落の根本原因調査

まず、原作最後の種明かしが、どの工程で初めて失われたかを特定する。

確認対象:

1. 原作の取得・保存データ
2. 原作から制作素材を作る工程
3. Story構成・分割
4. Advanced R0→R1→R2
5. Advanced→Standard難易度調整
6. 最終本文・音声原稿
7. 既存Validator・QA・Gate

各工程で、「即興の作り話が得意」という結末の意味が維持されていたか、証拠に基づいて追跡する。

特に以下を確認すること。

- なぜStandard/Advanced双方で同じオチが欠落したか。
- LLMが自主的に省略したのか、Prompt・構成指示が省略を誘発したのか。
- 2026-10-12の編集方針変更がどう関係したか。
- 旧「中心Story・人物関係・結末を保持」という条件が、現行の「エッセンス重視・自然なStorytelling優先」へ置き換えられた影響。
- 原作保持Validatorの撤去と今回の欠落の関係。
- 既存QAが重大な改変を検出できなかった理由。

**単に「Validatorがないから」と結論付けず、生成工程で欠落した根本原因を明らかにすること。**

既存の承認履歴を確認し、当時の変更判断を正確に整理すること。

## 4. 原作の本質を守る包括対策の設計

今回の欠落を個別修正するだけでなく、今後の古典文学でも重大な改変を防ぐ現実的な仕組みを検討する。

### 必須の品質方針

- 原作の重要な結末・種明かし・伏線回収を維持する。
- 主要人物の役割・関係性・重要な動機を維持する。
- 重要な因果関係を損なわない。
- 原作の解釈を根本的に変える省略・改変をしない。
- 一方、脇筋・重複描写・細かな背景説明などの省略や、自然な英語Storytellingのための表現変更は許容する。
- 原文の逐語的な再現は要求しない。

### 設計の方向性

まずWriter・構成Promptの改善によって、重要要素を欠落させない方法を優先検討する。

必要に応じて、原作の重要要素を構造化し、最終本文に引き継ぐ方法を検討する。

検査の追加が必要と判断する場合も、以下を比較する。

- 既存工程の改善だけで十分か。
- 軽量な確認で必要な品質を守れるか。
- 独立Validatorが本当に必要か。
- 過剰な判定・retry・Human Reviewが発生しないか。

**2026-10-12に撤去された原作保持Validatorを無断復活させないこと。**

旧仕様の復活や新しい品質Gateの追加を提案する場合は、既存のユーザー承認との相違・必要性・QCD影響を明示し、ユーザー判断事項として提示する。

Fableに独立レビューさせ、推奨案を原則1つに絞る。

## 5. 固有名詞ルールの正式改定

以下をFamily Zの新しい共通編集方針とする。

> **固有名を使うのは基本的に主人公のみとする。ただし、それ以外に物語の中心人物、展開・結末の理解に重要な人物については、主人公・脇役の区別によらず原作の名前を維持する。**

### 運用上の留意点

- 主人公のみという原則は維持する。
- 名前を残す例外は、物語上の重要性が明確な人物に限定する。
- 重要性が低い人物は、役割名や関係性による表現を原則とする。
- First name/Last nameの一方のみという既存方針は維持する。
- 固有名詞を増やすこと自体を目的としない。
- 登場回数の多さだけで重要人物と判断しない。
- 物語の重要性をAIが適切に判断できるようWriter Promptを調整する。

既存の名前検査Gateを無条件に復活させない。

## 6. 2作品での固有名詞Trial

新しい共通方針が意図どおり機能するか検証する。

### 『開いた窓』

**目標:固有名はFramtonとVeraのみ。**

まず共通ルールのみで、AIがVeraを重要人物として認識して名前を残すか確認する。

- Veraが残る場合:共通ルールが機能した証拠として記録。
- Veraが残らない場合:理由を分析し、共通Promptの改善余地を評価。そのうえで作品個別の指定によりFramton・Veraのみを残す。
- その他の人物名は必要以上に増やさない。

Veraの名前を残すだけでなく、原作のオチとの関係が自然に理解できる構成を目指す。

### 『走れメロス』

**目標:固有名はMelosのみ。**

その他の登場人物は、原則として役割名・関係性で表現する。

ただし、人物関係や因果関係が理解できなくなるような省略・置換は避ける。

### 共通条件

- Standard/Advanced双方で検証する。
- 固有名詞の過剰使用が生じないことも確認する。
- 新ルールの適用結果と、作品個別の調整結果を明確に区別する。
- 作品固有の名前を共通Promptに埋め込まない。
- 本文以外の制作工程やVoice設定への影響も確認する。

Trialに必要な範囲で本文案を生成してよいが、**音声再生成・正式Production成果物の差し替えは行わない。**

既存の成果を最大限再利用し、最小限の費用で検証する。

## 7. 『開いた窓』の修正方針

根本原因調査を踏まえ、今回の作品の修正方法も設計する。

- オチの補完だけで十分か。
- 伏線や物語の展開にも修正が必要か。
- Veraの名前を残すことで物語理解がどう改善するか。
- Standard/Advancedの修正範囲。
- 既存音声をどこまで再利用できるか。
- 制作費・所要工程の見積。

結末の復元は必須の品質課題として扱うが、**現段階では完成音声の修正・再生成は行わない。**

『走れメロス』についても、既存完成版のProduction音声は変更しない。

## 8. QCD・実行方針

優先順位:**品質 > 完了速度 > 量産単価**

- 既存ログ・成果物を再利用し、原因調査は原則費用0円。
- 独立した調査・設計・Trial準備は並列化する。
- 不要な日付分割・待機をしない。
- 新しい検査Gateを安易に追加しない。
- 同じ方向の無益なTrialを繰り返さない。
- 有料Trialは承認済みの範囲・予算Gateを遵守する。
- 問題の原因と再発防止策を対応付け、過剰な対策を避ける。

既存仕様との衝突がある場合は、その内容と解消に必要なユーザー判断を明確にする。

## 9. SSOT・Production管理

固有名詞ルール改定はユーザー正式承認済みとして、CURRENT_SPEC・DECISION_LOG・OPEN_ITEMSに反映する。

ただし、正式Productionに未配線の段階では`APPROVED_FOR_PRODUCTION`とし、`PRODUCTION_WIRED`を宣言しない。

新ルールの正式経路への配線が必要な場合は、既存仕様との整合を確認し、実装・必要なテスト・runtime evidence・Fable受入まで追跡する。ただし、今回のTrial結果を待たずに、未検証のPrompt案をProductionに採用しないこと。

原作忠実性の包括対策については、今回の調査・設計結果を`USER_DECISION_REQUIRED`として管理し、正式採用を先行させない。

必要なGit反映を実施する。

## 10. 最終報告

次の順に報告してください。

1. **原作のオチが欠落した根本原因**と、初めて欠落した工程。
2. **既存仕様・QAの問題点**と、2026-10-12の編集方針変更との関係。
3. **原作の本質を守る包括対策の推奨案**とFableレビュー結果。
4. **固有名詞Trial結果**:共通ルールのみでVeraが復活したか、Melosのみの使用が実現したか、不要な名前が増えていないか。
5. **『開いた窓』の修正方針**と、必要な本文・音声修正範囲。
6. **QCD影響**:追加費用、量産単価、制作時間、品質リスク。
7. **Status・SSOT/Git・残Open Item・必要なユーザー判断**。

原作忠実性については、Trialの成功とProduction採用を混同しないこと。

固有名詞ルールについても、共通Promptの検証結果と作品個別調整の結果を混同しないこと。

**最優先は、古典作品の本質的な魅力を守りながら、自然で面白く、英語学習に適したStoryを継続的に量産できる状態を実現することです。**
```

## 2. 本委任(01A)の範囲 = 原文§3(根本原因調査)+§4(包括対策の設計案)+§7(『開いた窓』修正方針の設計)
対象run: `er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01/`(本文はwriter/std_adjust段が先行runから再利用=provenance sha一致。先行runも追跡)。Family Z本文経路: `er026_family_z_fiction_production_runner_01.py`(stages: seed/原作取得→writer R0→R1→R2→std_adjust等)、`er062_family_z_structure_01.py`、Z Writer Prompt/brief(`er003_v1_translator_briefs/`等、Grepで特定)。

### 手順(read-only、API 0)
1. **工程別追跡**: 原文§3の1〜7の各工程について、run dir内の中間成果物(原作テキスト/seed/plan/R0/R1/R2/Adv本文/Std本文/音声原稿/audit)を順に読み、「Romance at short notice was her speciality」に相当する意味(Veraが即興で作り話をする人物だという種明かし)が**どの工程の出力で初めて消えたか**を、ファイルpath・該当箇所の引用で特定。Std/Advの双方で追跡し、同じ工程で消えたかを確認。
2. **原因の切り分け**: 当該工程のPrompt(実際に使われたPrompt本文またはsha→テンプレート)を読み、(a)LLMの自主的省略 (b)Prompt・構成指示(語数・尺・エッセンス重視・自然なStorytelling優先・結末の扱い・分割指示)が省略を誘発 (c)原作取得データ自体の欠落、を証拠で判別。推測は推測と明記。
3. **承認履歴の整理**: 2026-10-12の編集方針変更(旧「中心Story・人物関係・結末を保持」→現行「エッセンス重視・自然なStorytelling優先」)と原作保持Validatorの撤去について、ユーザー原文(`docs/pm/delegation_log/2026-10-12_*`)・DECISION_LOG・CURRENT_SPEC該当節・commitを引用し、当時の判断理由・範囲を正確に整理。今回の欠落との因果(方針変更前の版[あれば]との比較)を示す。
4. **既存QAが検出できなかった理由**: 現行のValidator/QA/Gate(Z本文系: 語数WARN、構造、Ledger/Fact系、音声系)の検査対象を列挙し、「結末の意味保持」を見る検査が存在しないこと、および撤去されたValidatorが検出できたか(その検査内容を確認)を示す。「Validatorがないから」で終わらせず、生成工程の原因(2.)を主因として整理。
5. **包括対策の設計案(採用は未承認)**: 原文§4の品質方針に沿い、**Writer・構成Promptの改善を最優先**に、候補を比較: (i)構成段階で「原作の重要要素(結末・種明かし・伏線回収・主要人物の役割/動機・重要因果)」を構造化データ(例: `source_essentials.json`)として抽出し、R0〜R2・std_adjustの各Promptに「維持必須要素」として引き継ぐ(各段で保持確認を同一LLM呼出内の自己チェックで行う) (ii)Writer Promptへの原則追記のみ (iii)軽量な事後確認(最終本文に必須要素が含まれるかの1回LLM判定、非Blocking/Blocking) (iv)独立Validator復活。各候補の必要性・費用(呼出回数・token)・retry/HR発生リスク・既存承認との相違を表にし、**推奨案を1つ**に絞る(Fable/Opusレビュー用)。撤去Validatorの無断復活は禁止。
6. **『開いた窓』修正方針の設計(実施しない)**: 現行本文の構成(伏線: 窓を開けている理由・Veraの最初の作り話・叔母の説明・男たちの帰還・Framtonの逃走・犬の作り話)を確認し、(a)オチ1文の補完で足りるか (b)伏線・展開の修正が要るか (c)Veraの名前を残す効果(01Bの固有名詞Trial結果と突き合わせる前提の設計) (d)Std/Advの修正範囲(段落・segment単位) (e)既存音声の再利用範囲(変更segmentのみ再TTS、Store再利用、assemble) (f)費用・工程見積(出典: run_e2e_01のcost_log=writer/std分17.76円、TTS約0.31円/clip等)。案を2つ以内(最小補完案/構成修正案)で提示し推奨1つ。

## 3. 成果物
- `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/ROOT_CAUSE_01.md`(§1〜4)、`COMPREHENSIVE_DESIGN_01.md`(§5、Opusレビュー用の論点付き)、`OPEN_WINDOW_FIX_PLAN_01.md`(§6)。
- SSOT: OPEN_ITEMS新item(原作忠実性、Status=`INVESTIGATED_DESIGN_PENDING_OPUS`)、REPORT_LEDGER 1行。commitは明示add、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 4. 禁止
- API呼出、Trial、Production/Prompt/音声/成果物の変更、撤去Validatorの復活、未承認案の正式仕様化、他作品への調査拡大(メロスは比較参照のみ)。

## 5. 報告(docs/pm/RESULT_PACKET_FZSF1A.md、同内容を最終報告で)
(1)初めて欠落した工程とその証拠 (2)根本原因の判別結果(a/b/c、確度) (3)2026-10-12方針変更・Validator撤去との関係(承認原文引用) (4)既存QAが検出できなかった理由 (5)包括対策の候補比較と推奨1案(QCD) (6)『開いた窓』修正方針(推奨1案、範囲・費用) (7)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。