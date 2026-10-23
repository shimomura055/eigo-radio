FABLE-DELEGATION-MARKER: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01-委任_03-U1-TRIAL-20261023

# 委任_03: Phase 1 — U1統合Offline Trial(原作忠実性「修正版B」+固有名詞`keep_name`共通機構)。DEV/Trial経路のみ・Production変更禁止・費用上限60円(ユーザー承認概算40円+積算上限50円の範囲、超過見込みなら開始前STOP)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_委任_03.md`(N≈333〜343、先頭行MARKER一致確認)。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_USER_02.md` に逐語保存。
3. ACTIVE_TASK.md: 別agent(FAMILY-Z-DIALOGUE-SPEED-PRODUCTION-WIRING-01、er063/er003を編集中・Z成果物を再処理中)が並行。編集直前に再読込し、本管理IDの行だけ更新。有料生成の直前/直後に「有料run進行中/終了(時刻)」。本Trialは本文生成のみ(音声なし)で、Store/音声成果物に触れないため速度配線と競合しないが、**`er062_family_z_writer_01.py`・`er062_family_z_structure_01.py`・Production Seedは書き換えない**(DEV overrideのみ)。

## 1. ユーザー指示原文(逐語)
```
# Claude Codeへの回答・指示:Family Z 原作忠実性・固有名詞統合Trial → Production Wiring → 『開いた窓』完成

## 1. ユーザー決定

報告されたU1・U2について、以下のとおり決定する。

**U1:統合Offline Trialを承認する。**

- 原作忠実性の包括対策「修正版B」と、承認済み固有名詞ルールを結合して検証する。
- 提案されたTrial設計、概算40円を承認する。
- Trial成功時のStatus上限は`VALIDATED`。
- 原作忠実性の包括対策をProduction採用するかは、Trial結果を受けてユーザーが別途判断する。

**U2:個別パッチによる先行修正は実施しない。**

『開いた窓』の完成は急がない。

U1で包括対策を検証し、正式採用・Production配線した後、その仕組みを使って『開いた窓』を制作する。

既存本文にVeraの名前や結末の一文を手動挿入するだけの個別修正を、今回の基本方針にはしない。

目的は、今回の作品を直すことだけでなく、**今後のFamily Zでも原作の本質を損なわずに制作できるProduction環境を完成させること**である。

## 2. Phase 1:U1統合Offline Trial

報告済みの修正版Bについて、提案された条件でTrialを実施する。

- 「Seed修正のみ」R0 × 3
- 「修正版B」R0 × 3
- 修正版Bの全段検証(R0→R1→R2→Standard)× 2
- 固有名詞`keep_name`の共通機構を同一Trial内で検証

既存成果物を再利用し、条件間で比較可能な設計を維持すること。

### 重点検証項目

1. 原作の重要な結末・種明かし・伏線回収が保持される。
2. 原作の重要な人物関係・因果関係が維持される。
3. 重要要素がR0からR1、R2、Standardへ引き継がれる。
4. 『開いた窓』でVeraの名前が適切に維持される。
5. 『走れメロス』ではMelos以外の不要な固有名詞が増加しない。
6. Standard/Advancedとも、自然で面白いStorytellingと難易度を維持する。
7. 作品固有の名前を共通Promptへ埋め込まず、Seed側で指定できる。

特に、同じSeedでもオチが残る場合と消える場合があった問題について、**再現性の改善**を確認すること。

単に1回成功しただけで、構造的な欠落リスクが解消されたと結論付けないこと。

ただし、独自の合格基準を追加したり、承認済みTrial範囲を無断で拡大したりしない。

### Trial終了条件

- 必要な結果・失敗例・残リスクを整理する。
- Fable独立レビューを実施する。
- `VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`のいずれかでCloseoutする。
- 原作忠実性の包括対策を、ユーザーの承認前にProduction実装しない。
- 承認範囲を超える追加Trialは実施しない。

## 3. Phase 2:Production採用判断

U1の結果を確認した段階で、ユーザーへ報告すること。

報告には以下を含める。

- Trial結果と再現性
- 原作の重要要素が保持されたか
- 固有名詞ルールの適用結果
- 既存仕様との整合
- Fable評価
- 制作速度・量産単価への影響
- 残る品質リスク
- 推奨する正式採用判断

**原作忠実性の包括対策は、ユーザーが正式採用を明示するまで`APPROVED_FOR_PRODUCTION`へ移行しない。**

ここは必須のPM Gateとする。

## 4. Phase 3:正式Production Wiring

原作忠実性の包括対策がユーザーに正式承認された場合、Family ZのProduction Wiringを実施する。

対象は以下。

### A. 原作忠実性の包括対策

修正版Bのうち、ユーザーが承認した仕様を正式Productionへ反映する。

- Seedの維持必須要素
- R0/R1/R2/Standardへの情報引継ぎ
- 既存Fable CPによる重要要素の保持確認
- 欠落が発見された場合、TTSへ進ませず、承認済みの方法で修正する運用
- 既存Prompt・QA・Gateとの整合

未承認のLLM Validatorや新しい自動検査Gateを追加しないこと。

### B. 固有名詞ルール

こちらは**既にユーザー正式承認済み**である。

> 固有名を使うのは基本的に主人公のみとする。ただし、それ以外に物語の中心人物、展開・結末の理解に重要な人物については、主人公・脇役の区別によらず原作の名前を維持する。

U1の検証結果を踏まえ、`keep_name`等の共通機構を正式Productionへ配線する。

作品固有の名前を共通Promptに埋め込まないこと。

『開いた窓』ではFramtonとVeraのみ、『走れメロス』ではMelosのみを使用する方針と整合させる。

### C. Production Wiringの受入条件

- 正式初回Production経路に実装されている。
- retry/fallback/regeneration/resumeでも新仕様が維持される。
- Trial専用経路だけの実装になっていない。
- 正式runtime evidenceが存在する。
- 必須Regression/Validator/Integration testがPASSする。
- 旧仕様・Prompt・QAとの矛盾やDangling Referenceがない。
- CURRENT_SPEC/DECISION_LOG/OPEN_ITEMSが更新されている。
- 必要なGit反映が完了している。
- Fable独立受入が完了している。

これらを満たして初めて`PRODUCTION_WIRED`と判断する。

## 5. 会話速度改善との並行作業

別途、ユーザーが正式採用したFamily Z会話速度改善は、そのままProduction Wiringを継続してよい。

採用仕様:

| 対象 | 速度仕様 |
|---|---|
| Standard Narrator | 従来どおり6%減速 |
| Standard Dialogue | 6%減速を撤去 |
| Advanced Narrator | 従来どおり速度変更なし |
| Advanced Dialogue | 約6%高速化 |

会話速度改善の配線は、U1 Trialおよび原作忠実性対策の採用判断と独立して進められる。

ただし、『開いた窓』の最終組立・公開更新は、原作忠実性・固有名詞・会話速度の各仕様が正式経路に揃ってから実施する。

不要な二重生成・二重組立を避けること。

## 6. Phase 4:『開いた窓』正式Production制作

原作忠実性の包括対策が正式承認され、必要なProduction配線が完了した後、**『開いた窓』Standard/Advancedの完成候補を制作する。**

適用する仕様は以下。

1. 原作の重要な結末・種明かし・伏線回収を保持する包括対策
2. 固有名詞ルール(FramtonとVeraのみ)
3. 承認済みの会話速度改善
4. 既存のFamily Z音声・品質仕様

原作の最後の種明かしが、単なる説明として省略されず、物語のオチとして自然に機能することを確認する。

また、Veraの名前が自然に導入され、人物関係が理解できることを確認する。

**今回は作品個別の決定論パッチを基本とせず、正式Production経路による制作を優先する。**

既存の成果物を再利用できる部分は再利用してよいが、新仕様の発火証拠が必要な工程については、実際のProduction動作を確認すること。

### 完成候補の受入条件

- 原作の結末・重要な因果関係が保持されている。
- VeraとFramtonが適切に登場する。
- 不要な人物名が増えていない。
- Standard/Advancedそれぞれの品質・難易度を満たす。
- 新しい会話速度仕様が適用されている。
- Voice割当・音声QA・ASR・組立がPASSする。
- Fable独立受入が完了している。
- Standard/Advancedの比較試聴ページが公開されている。

作品完成候補とユーザー最終試聴PASSは区別すること。

## 7. QCD・作業進行

優先順位は、**品質 > 完了速度 > 量産単価**。

今回は作品の完成を急がないが、不要な待機や逐次処理を認める趣旨ではない。

- U1の承認済みTrialを速やかに実施する。
- 会話速度Production Wiringなど、独立して進められる作業は並列化する。
- 原作忠実性の正式採用判断が必要な地点では必ずSTOPする。
- 承認済みの技術的問題・軽微な不具合は自律的に解決する。
- 不要なTrial追加、TTS再生成、個別パッチを避ける。
- 量産単価への影響も記録し、70円/記事セット目標との整合を確認する。

## 8. 直近の報告とSTOP位置

まずU1統合Trialを実施し、Fable独立レビューまで完了して報告すること。

**この時点で原作忠実性の包括対策について、ユーザーの正式採用判断を待つ。**

一方、すでに承認済みの会話速度改善については、その判断待ちを理由にProduction配線を止めない。

最終的には、承認済みの全仕様を統合した正式Production経路で『開いた窓』の完成候補を制作し、ユーザー試聴に提出する。

**今回の目的は『開いた窓』だけを個別に直すことではなく、原作の本質を守るFamily ZのProduction環境を確立し、その環境で作品を完成させることである。**
```

## 2. 入力(読む)
- 設計: `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/COMPREHENSIVE_DESIGN_02.md`(修正版B: essentialsスキーマ[最大5件・意味レベル・`ending_reveal`+`withhold_until_end`対・`source_quote`逐語・`free_to_cut`]、`build_r0_prompt`/`build_revise_prompt`/`build_std_prompt`へ決定論文字列、provenance sha、`key_roles.keep_name`で「only X may have a personal name」(R0 L94/REVISE L142/conversion_plan)を上書き、Std Promptのclosing summary禁止との関係明示、自己チェック不採用、Melos byte同一)、`ROOT_CAUSE_02.md`、`OPUS_REVIEW_01.md`、`PROPER_NOUN_TRIAL_01.md`(01Bの`pntrial_dev_runner_01.py` override方式・`COMMON_NAMING_POLICY`・結果)。
- Seed実体: `er026_output/family_z_production_e2e_01/the_open_window/seed/seed.json`(:9 seed_elements[5]、:15 discarded、:18 conversion_plan)。melos seed(受入済み`run_e2e_06`系)。
- Writer: `er062_family_z_writer_01.py`(L64-67 DEPENDENTS、L88、L94、L106-109、L142、L158、L165、L362-399)。

## 3. Trial設計(ユーザー承認済み範囲。拡大禁止)
- **対象作品**: 『開いた窓』(T1/T2/T3)。『走れメロス』は(a)essentials無し・keep_name未指定のSeedで新機構PromptがProduction現行Promptと**byte同一**になることのtest(API 0)、(b)01Bの共通ルールrun(`melos/run_pntrial_01`、Melosのみ達成)の結果を再利用し、新機構のPromptが01Bの共通ルールPromptと実質同一であることを差分で示す(API 0)。
- **DEV override**: 01Bの`pntrial_dev_runner_01.py`方式を拡張(`sftrial_dev_runner_01.py`等、DEV専用、Production参照0をGrep)。Production Prompt定数・関数をメモリ上で差し替え、Seedは**Trial dir内のコピー**を使う(Production seed.json無変更)。
- **Seed修正版(T1/T2共通)**: 『開いた窓』seedのコピーに(i)`essentials`(修正版Bスキーマ、最大5件: ending_reveal=「Veraは即興で作り話をするのが得意だった(原作最終文 source_quote逐語)」+withhold_until_end、setups_and_payoffs=結末成立に不可欠なものだけ、key_roles=Framton[主人公]・Vera[keep_name=true、結末理解に重要]、important_causality、free_to_cut)、(ii)`conversion_plan`の結末定義と「最後の行の後に説明を足すな」を「原作自身の最終文は除外」に改訂、(iii)`discarded_elements`から少女の名前省略を除去。**T1「Seed修正のみ」はPromptは現行のまま(R0 Promptに現行どおりSeedが入るだけ)**、**T2「修正版B」はSeed修正+Prompt側の修正版B(essentials行の全段引継ぎ+keep_name上書き+Std Promptの関係明示)**。
- **実行**: T1 R0×3、T2 R0×3、T3 修正版B全段(R0→R1→R2→Std)×2。条件間でモデル・temperature等の既定は同一(Production既定、gpt-6.1-sol)。各runは別run dir(`the_open_window/run_sftrial_t1_0{1,2,3}`、`run_sftrial_t2_0{1,2,3}`、`run_sftrial_t3_0{1,2}`)。T3の2本は、T2で生成したR0のうち2本を起点に再利用してよい(費用削減。比較可能性を保つため出典を記録)。
- **費用見積**: 01B実績(writer R0〜R2 約8.8〜10.8円、std 約7〜8円)からR0単体は約3〜4円と推定。T1 3本≈10円、T2 3本≈10円、T3 R1〜Std 2本≈2×(6+7)=26円 → 約46円。上限60円。開始前に`raw_usage_log`方式で見積を確定し、超過見込みならSTOP報告。実費は出典付き。
- **他agentとの関係**: `stop_scope_check` rc=0確認。有料run重複は本文生成のみのため可。ただし`er062_*`をいじらない。

## 4. 評価(承認済み基準のみ。独自合格基準を追加しない)
各run(T1×3、T2×3、T3×2の各段R0/R1/R2/Std)について表にする:
1. 結末の種明かし(Veraが即興で作り話をする人物だという意味)の有無・該当文の引用・位置(最終段落か)。
2. 伏線回収(窓を開けている理由の作り話→男たちの帰還→Framtonの逃走→犬の作り話→種明かし)の保持、人物関係(叔母・姪・夫と弟)・重要因果の保持。
3. 固有名詞一覧(名前・回数・初出)。目標=FramtonとVeraのみ。他の名前の増加有無。
4. essentials各項目の充足(本文該当引用)=Fable CPチェックリストの試作(自動判定ではなく、Sonnetが読んで引用を貼る)。
5. 既存の決定論検査(語数330〜470、Std≠Adv、段落数一致、禁止名WARN[「ヴェラ」の挙動を記録]、権利Gate)の結果。
6. Storytelling・難易度の所見(事実と所見を分ける。Std A2らしさ・Adv B1らしさの既存基準に照らす)。
7. **再現性**: T1 3本 vs T2 3本で種明かし保持率を比較(現行Seed+現行Promptの既知観測=01Bのrun_pntrial_01で保持1/個別run_pntrial_02で欠落1、run_e2e_01で欠落、を参考値として併記)。n=3の限界を明記し、「1回成功=解消」と結論しない。
8. T3: 要素がR0→R1→R2→Stdで引き継がれたか(各段の該当引用)。Std調整で最終文が「要約」として削られないか。
9. `withhold_until_end`: 結末前に種明かしが漏れていないか。
10. メロス: byte同一test結果と、01B共通ルール結果の再利用。

## 5. 成果物・SSOT
- `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/U1_TRIAL_RESULT_01.md`(条件表、Seed差分、Prompt差分、結果表、再現性、失敗例、残リスク、費用出典、Production無変更の証拠、Fable/Opusレビュー論点、Status候補=VALIDATED/REJECTED/USER_DECISION_REQUIRED)、`sftrial_eval_01.json`、DEV runner。
- OPEN-465 Status=`U1_TRIAL_COMPLETE_PENDING_FABLE_REVIEW`、OPEN-464に参照追記、DECISION_LOG(Trial実施、採用なし)、REPORT_LEDGER。CURRENT_SPECは**変更しない**。commitは明示add(本文md/json/DEV script。Production .py差分0をgit diffで確認)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 6. 禁止
- Production Prompt/コード/Seed/音声/成果物/公開ページの変更、音声生成、承認外の追加run、独自合格基準、個別パッチ、`APPROVED_FOR_PRODUCTION`/`VALIDATED`の自己宣言(候補として提示)。

## 7. 報告(docs/pm/RESULT_PACKET_FZSF3.md、同内容を最終報告で)
(1)Trial結果表の要約(T1/T2/T3別、種明かし保持率、Vera/他名、essentials充足、既存検査) (2)再現性の評価(限界明記) (3)失敗例と残リスク (4)メロス不変の証拠 (5)費用(出典) (6)Production無変更の証拠 (7)Status候補と推奨理由 (8)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。