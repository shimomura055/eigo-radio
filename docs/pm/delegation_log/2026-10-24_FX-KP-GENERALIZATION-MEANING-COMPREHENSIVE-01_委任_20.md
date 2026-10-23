MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_20 (2026-10-24, Fable→sonnet-worker)

# 管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_20(課題② 見出し語の所有格一般化=APPROVED_FOR_PRODUCTION[UDR #173、2026-10-24]→Family X/Z Production Wiring+Family Y実装状況確認+runtime evidence+SSOT)

## 0. ユーザー決定(正本)
- ユーザー指示原文(課題①②の両方を含む)を**最初に** `docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_07.md` として末尾§Zを逐語保存すること。
- 本委任は§Zの「1. 課題②」のみを担当(課題①は別委任_21が並行、触らない)。UDR #173 課題②: 改善案+付帯条件(a)〜(f)を正式承認。付帯(a)〜(f)の正文は `docs/pm/USER_DECISION_REGISTER_01.md` #173 と `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/TRIAL_04/FABLE_JUDGMENT_04.md` を参照し、報告で各条件の充足を1対1で示す。
- 設計正本: `docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/WIRING_DESIGN_05.md`(②possessor_roles+A-1統合配線、Opus条件C反映済み `OPUS_REVIEW_06.md`、WC-01〜15)。DEV実装: `er112_kp_gm_poss_04.py`(+test)、Trial_04結果 `TRIAL_04/{POSS_RESCORE_01,POSS_REP2_01,FABLE_JUDGMENT_04}.md`。既存Trial成果を再利用し、再Trialはしない。

## 1. 仕様(ユーザー§1-1、逐語に近い要件)
- 所有者の指示対象(self / other / non_person)を判定し、one's / someone's / 原形維持を決定。物が動作主となる `its` は現状維持。判断に迷う場合は置換しない。不整合時は元表現へ戻し新たなエラーを発生させない(revertのみ)。役割条件付き受理で既存A/B/C旧ライン(§27-3凍結)への影響を防ぐ。承認済みPrompt変更・関連QA定義の整合・A-1との同梱を含める。既存完成記事は自動再生成しない。

## 2. 作業
 A. **Family X/Z Production実装**(WIRING_DESIGN_05どおり): A-1の `_EDITS`→`_POSS_EDITS` 統合、role条件付き受理、revertのみ、postprocess hookはfulltext schemaのみ、merge passthrough、recompute fixes。共通moduleならX/Zに1箇所で効くことを確認し、X/Z各経路(初回Production・retry/fallback/regeneration/resume)で同じ関数が呼ばれることをコード上で示す(関数・行番号)。A/B/C Legacyに影響0をtestで固定(DefaultOff/Legacy isolation test)。QA定義(KP関連QA・Validator)との整合を更新。
 B. **test**: WIRING_DESIGN_05 WC-07のtest計画を実装(正常/境界/revert/role不明時無変更/its維持/legacy非適用)。全回帰(`.venv\Scripts\python.exe run_project_regression.py`)で自分起因0(既知3件は記載)。
 C. **runtime evidence**(新規TTS 0、既存記事の自動再生成0): WIRING_DESIGN_05の証跡計画(X `uk_train_speaker_playback` の `reach for your wallet`→`someone's wallet`/Z Melos `gave my word`等)に従い、**正式経路の関数をDEV注入textで通すP-T2確認(≈11円、Fable裁量内)**と、可能なら正式Production経路のKP工程のみを既存記事のtextで実行(音声なし、出力は検証用ディレクトリに隔離、公開物を書き換えない)。actual model_id・routing・Prompt hash・flag状態・before/after見出し語・revert発生有無をログで示す。費用上限 **25円**(見込み11〜15円)。ACTIVE_TASK自分の行に有料run記録。10-24日次累計も記録(現在約240円+並行Y Phase 2 ≤27円)。
 D. **Family Y実装状況の確認**(ユーザー§1-2、1〜5に1対1で回答): Family Y制作ラインの現状工程(er110系はDEV/Trialのみか、正式Production経路は存在するか)、KP選定・一般化・意味生成工程の有無、X/Z共通実装の利用かY専用か、今回仕様を現時点でYに配線・検証できるか(**Trial専用経路への実装はPRODUCTION_WIREDと判定しない**)、できない場合の理由とY Production化までに必要な作業。コード・CURRENT_SPEC・runtime evidenceから事実で示す。合理的に適用可能(例: YがX/Z共通KP moduleを呼ぶ設計になっている)ならX/Zと同時に適用し検証。Yに正式Production経路がなければ**新規OPEN**に「未配線事項・依存関係・解消条件」を登録し、Y Production化時の必須受入条件と明記。
 E. **SSOT**: `CURRENT_SPEC.md`(KP見出し語canonicalization節に②の規則を既存書式で追記、A/B/C非適用・X/Z適用・Y状況)、`OPEN_ITEMS.md`(OPEN-474更新: ②APPROVED_FOR_PRODUCTION→実装→PRODUCTION_WIRED判定はFable受入後。OPEN-481(non_person_agent分割)は維持。Y用新規OPEN)、`DECISION_LOG.md`(UDR #173 ②承認・付帯a〜f、配線実施)、`docs/pm/USER_DECISION_REGISTER_01.md` #173を「②判断済み(承認・付帯a〜f)、①は再調査中(委任_21)」に更新。他agent(Family Y 委任_18/OPEN-482 委任_01)が並行編集中の可能性: commit前に `git diff -- OPEN_ITEMS.md DECISION_LOG.md CURRENT_SPEC.md` で自分以外のhunkを確認、含まれる場合は数分待って再確認、残る場合は報告に明記。
 F. 委任文逐語保存 `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-24_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_20.md`(先頭MARKER一致、0始まり)。commit(変更ファイル明示、`git diff --cached --name-status`、`git commit --only -- <paths>`、secret grep 0件、`git add -A/-u/-f`禁止、raw_usage_log不追跡)→`git push origin HEAD:main`。revertは単一commitで可能な構成にする(WIRING_DESIGN_05)。
 G. 報告 `docs/pm/RESULT_PACKET_KPGM20.md`: Familyごとの実装状況/Wiring Status候補(X/Z=WIRED候補[Fable受入後にPRODUCTION_WIRED]、Y=事実と新規OPEN)、受入条件(§1-3の9項目)のチェック表、付帯(a)〜(f)充足表、evidence要約(model_id/routing/Prompt/flag/before-after)、全回帰結果、費用、commit hash・raw URL、4行(既存仕様整合/未承認機能の既定値/失敗終了時の最終成果物/撤去[旧`_EDITS`経路の残置有無])、判定整合行、使用モデル(最新か)。Dangling Reference(未承認仕様・DEV専用定義への参照)が0であることをGrepで示す。

## §Z ユーザー指示原文(逐語)
# Key Phrase品質改善｜②一般化のXYZ Production Wiring・①字義訳の根本解決

## 0. 最上位方針

今回の作業は以下の2本立てとする。

- **課題② 見出し語の一般化：正式採用済み。Family X/Y/Z共通でProduction Wiringを完了する。**
- **課題① 日本語意味の字義訳：原因究明からやり直し、根本対策の立案・Trial検証を自律的に進める。**

品質（Q）＞完成速度（D）＞量産単価（C）を厳守する。

独立作業は可能な限り並列化し、不合理な待機・日付分割を行わない。

---

## 1. 課題② 見出し語の一般化｜正式採用

**Status：APPROVED_FOR_PRODUCTION**

UDR #173の課題②について、ユーザーは改善案および付帯条件(a)〜(f)を正式承認した。

### 1-1. Family X/Y/Z共通でProduction Wiring

承認済みの所有格一般化方式を正式Production経路へ反映する。

- 所有者の指示対象（self / other / non_person）を判定し、one's / someone's / 原形維持を決定する。
- 物が動作主となる `its` は現状維持。
- 判断に迷う場合は置換しない。
- 不整合時は元表現へ戻し、新たなエラーを発生させない。
- 役割条件付き受理により、既存のA/B/C旧ラインへの影響を防ぐ。
- 承認済みPrompt変更、関連QA定義の整合、A-1との同梱を含める。
- 既存完成記事は自動再生成しない。

既存Trial成果を再利用し、不要な再Trialは行わないこと。

### 1-2. Family Yの実装状況を最優先で確認

Family Yは現在Phase BのTrial中である。

以下を既存Repo・CURRENT_SPEC・実装・runtime evidenceから確認すること。

1. Family Yの制作ラインは、現在どの工程まで構築されているか。
2. Key Phraseの選定・一般化・意味生成工程は既に存在するか。
3. X/Zと共通の実装を利用しているか、Y専用実装か。
4. 今回承認した一般化仕様を、現時点でYに配線・検証できるか。
5. 配線できない場合、その理由と、YのProduction化までに必要な作業は何か。

**ユーザーの意図は、今後の共通品質改善をFamily Yにも漏れなく織り込むことにある。**

Yへの適用を後回しにすること自体を目的化しない。現在の実装段階で合理的に適用可能なら、X/Zと同時に進める。

ただし、Trial専用経路への実装をもってPRODUCTION_WIREDと判定しない。

Yに正式Production経路が存在しない場合は、未配線事項・依存関係・解消条件をOPEN_ITEMSへ登録し、Production化時の必須受入条件とする。

### 1-3. Production受入条件

対象Familyごとに以下を確認する。

- 正式初回Production経路に実装されている。
- retry / fallback / regeneration / resumeと整合している。
- 承認済みA-1、既存Key Phrase仕様、Promptとの整合が保たれている。
- runtime evidenceが取得されている。
- 必須Regression・Validator・integration testがPASS。
- actual model_id、routing、Prompt等の証拠が揃っている。
- CURRENT_SPEC / DECISION_LOG / OPEN_ITEMSを更新。
- Git反映完了。
- 未承認仕様やDEV専用定義へのDangling Referenceがない。

すべて確認できたFamilyのみPRODUCTION_WIREDとする。

---

## 2. 課題① 日本語意味の字義訳｜根本解決

**Status：対策未採用。Trialで検証後、正式採否をユーザー判断に戻す。**

### 2-1. 問題認識

今回のTrialでは、独立検査方式Cによって字義訳NGが6件から1件へ減少した一方、19件の検出中14件が修正不要だった。

これは、検査による品質改善には一定の効果があっても、誤検知・再生成・運用負荷の問題が大きいことを示している。

**検査方式Cを現段階でProduction採用しない。**

ただし、字義訳問題の解決そのものを諦めてはならない。

### 2-2. 原因究明を徹底する

単に「LLMが確率的に字義訳を選ぶ」という説明で終わらせないこと。

以下を具体的に解明する。

1. なぜ本文の文脈から適切な意味を取得できず、字義訳を選択するのか。
2. Key Phrase選定時点で、表現の意味・文脈が失われていないか。
3. 意味生成Promptへの入力情報は十分か。
4. 文脈の解釈と日本語への変換が一度に行われることが原因ではないか。
5. 過去のPrompt改善Trialが効かなかった本質的な理由は何か。
6. 字義訳NGの発生事例に共通する構造・条件は何か。
7. そもそも誤訳を生成させないために、どの工程を変更するのが有効か。

既存Trialデータ、失敗事例、Prompt、生成処理を調査し、原因仮説を証拠とともに整理する。

**Opusによる独立レビューを実施し、原因分析・対策案・見落とし・既存Trialとの重複を確認すること。**

### 2-3. 根本対策の立案

生成後の検査追加ありきではなく、**正しい意味を最初から生成する方法を優先**する。

候補例：

- 本文の文脈から意味を先に解釈し、その解釈を日本語化する。
- Key Phrase選定時に把握した意味・用法を意味生成工程へ確実に引き継ぐ。
- 比喩・慣用表現・通常の字義表現を文脈に応じて扱う。
- 意味生成工程の入力・出力構造や処理順序を見直す。

これらは例示であり、実装方法を限定しない。

Claude自身で有効な代替案を考案し、Opusレビューも活用して比較すること。

追加検査方式も排除しないが、誤検知の多さ、再生成負荷、量産単価への影響を踏まえ、必要性と有効性を説明できる場合に限り候補とする。

既存call内で改善できる方法を優先し、追加LLM callを極力抑える。

### 2-4. Trialと自己ループ

原因究明 → 対策立案 → Trial → 評価 → 改善を自律的に繰り返す。

- 既存の代表的な失敗例と、正常な意味表現を比較対象とする。
- 比喩・慣用表現の改善だけでなく、通常表現の意味が悪化しないことも確認する。
- 成功例だけでなく、残存NG・新規悪化・費用を記録する。
- 効果がない場合は同じPrompt変更を繰り返さず、原因仮説や方式を見直す。
- Opusレビューは初期原因分析に加え、必要な方針転換や最終評価にも活用する。
- 品質を守りながらTrialの検証効率を最大化する。

**「何度か試したがうまくいかなかった」という理由だけで、安易にUSER_DECISION_REQUIREDへ戻さないこと。**

解決の見込みがある限り、承認済み範囲内で自律的に取り組む。

一方、効果のない反復や、品質水準を超える過剰な改善は行わない。

### 2-5. Trial Closeoutと正式採用

今回の課題①について、Production採用は未承認である。

Trial結果を踏まえ、REJECTED / VALIDATED / USER_DECISION_REQUIREDのいずれかに分類する。

VALIDATEDとなってもProduction実装は自動開始しない。

採用可能な改善策が得られた場合、以下を報告し、ユーザーの正式採否判断を受けること。

- 根本原因
- 採用候補の仕組み
- Before / After
- 残存NG・新規悪化
- X/Y/Z共通仕様への影響
- 量産単価・速度への影響

## 3. 予算・STOP条件

既存の承認済みTrial予算・作業範囲・日次開発費上限を厳守する。

課題①は残存する個別承認枠を確認し、その範囲内で原因調査と有効なTrialを優先する。

少額費用ごとにユーザー判断を求めない。

ただし、以下ではSTOPし、判断を求める。

- 承認済み予算・Scopeの超過
- 未承認の新仕様・品質基準変更が必要
- 重大な品質・安全リスク
- 合理的な代替案を検討しても解決見込みがなく、根本的な方針変更を要する

## 4. 報告・Closeout

2課題は独立して進行・完了判定する。②のProduction Wiringを①のTrial完了待ちで止めない。

最終報告では以下を明示する。

**課題②**
- XYZ各Familyの実装状況
- Family Yの配線可否・実施結果
- 各FamilyのProduction Wiring Statusと証拠
- 未配線があれば理由とOPEN_ITEMS

**課題①**
- 原因究明とOpusレビュー結果
- 比較した対策と採否理由
- Trial結果・残存課題・QCD
- 次の採用判断に必要な情報

目的は、検査やTrialを増やすことではない。

**Key Phraseの品質を根本的に改善し、Family X/Y/Zに共通展開しながら、品質を守って最速・低単価で安定量産できる状態を実現すること。**