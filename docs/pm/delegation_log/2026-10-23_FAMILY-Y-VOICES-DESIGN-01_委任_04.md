FABLE-DELEGATION-MARKER: FAMILY-Y-VOICES-DESIGN-01-委任_04-TRIAL-TEXT-20261023

# 委任_04: Family Y 統合Trial — Phase 0(整合確認・DEV実装)/Phase 1(Voice Card・R0→R1→R2比較)/Phase 2(英語化・レベル調整)。DEV/Trial経路のみ・X/Z Production変更禁止・費用上限250円(Phase 3音声分を含む全体。超過見込みなら実行前STOP)

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_委任_04.md`(N≈335〜345、先頭行MARKER一致確認)。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FAMILY-Y-VOICES-DESIGN-01_USER_02.md` に逐語保存。
3. ACTIVE_TASK.md: 別agent(FAMILY-Z-SOURCE-FIDELITY 委任_03 U1 Trial、本文生成のみ)が並行。編集直前に再読込し、FAMILY-Y行だけ更新。有料生成の直前/直後に「有料run進行中/終了(時刻)」。
4. **ユーザー決定の記録(先にcommit)**: DECISION_LOGに「Family Y基本設計確定(5パート固定、3 Voices固定、Comment4廃止、R0→R1→R2全段Trial、Leakage Check/Acceptance Gate継承、TTS Voice固定=Voice1 Algieba/Voice2 Zephyr/Voice3 Schedar[性別・登場順自動割当は不採用]、Trialテーマ=学校でスマホを禁止すべき?の1件、上限250円)」を原文所在付きで1件。UDR: D1/D3/D4/Trial承認・テーマを判断済み(D3は推奨と異なる固定割当で決定、D4は「R0のみ」ではなく全段比較で決定)。OPEN-463 Status=`DESIGN_APPROVED_TRIAL_IN_PROGRESS`。CURRENT_SPECは変更しない(Yは未採用)。

## 1. ユーザー指示原文(逐語)
```
# Claude Codeへの指示:Family Y 基本設計確定・統合Trial実施

## 1. ユーザー決定

Family Y(Voices型)の基本設計について、以下を正式な設計方針として確定する。

- Family Xの正式Production基盤を最大限再利用する。
- 本文は5パート固定:リード → Voice 1 → Voice 2 → Voice 3 → Tension+Closing。
- Voiceは3人固定。それぞれ主観的な立場から、一人称で自由に発言する。
- Comment4は廃止する。
- WriterはR0→R1→R2をすべてTrialし、各段階の品質変化を比較する。
- 旧Voicesで承認済みのAnalytical Leakage Check・Acceptance Gateを適切に継承する。
- TTS Voiceは以下の固定割当とする。

| パート | TTS Voice |
|---|---|
| Voice 1 | Algieba |
| Voice 2 | Zephyr |
| Voice 3 | Schedar |

**性別・登場順による自動割当は採用しない。上記3つをFamily Yの固定仕様とする。**

人物設計では、固定Voiceの声質・性別との整合も考慮すること。

## 2. Trialテーマ

**「学校でスマホを禁止すべき?」の1テーマのみ。**

「観光客が増えすぎた小さな町」は今回のTrial対象から除外する。

テーマについて、賛成・反対・中立を機械的に1人ずつ配置する必要はない。

3人がそれぞれ固有の生活背景・事情・価値観を持ち、本人として自然に語る構成を優先する。

## 3. Family Yの品質方針

重要なのは、3人のVoiceが単に異なる論点を説明するのではなく、**それぞれ独立した人物として、自分の意見・感情・判断を自由に語ること**である。

- 一人称(I)による発言を基本とする。
- 解説者・評論家のような客観的説明に偏らない。
- 人物ごとの立場・経験・価値観を明確にする。
- 3人の主張が実質的に重複しないようにする。
- 他のVoiceの主張を過度に取り込まない。
- ただし、迷いや複雑な感情まで禁止しない。
- 不自然なテンプレート化や、機械的な賛否の割当を避ける。
- 未確認の事実や統計を個人の体験として創作しない。

旧Voicesの品質問題と承認済み対策を参照する一方、**対策が強すぎて人物の自由な発言を阻害しないか**も評価すること。

## 4. Trial実施内容

### Phase 0:既存仕様との整合確認

Family Xの正式Production基盤、旧Voicesの承認済み品質対策、Family Y設計書を確認する。

既存の承認済み仕様を無断変更せず、Family Y固有の差分に限定してDEV/Trial実装する。

### Phase 1:日本語原稿・Writer比較

Voice Cardを生成し、以下を実施する。

**R0 → R1 → R2**

各段階の原稿を保存し、比較可能にする。

確認事項:

1. 人物の個性・一人称の自然さ
2. 3人の意見の独立性・多様性
3. エンターテインメント性・聞きたくなる面白さ
4. Analytical Leakageの発生・改善・悪化
5. R1/R2による品質改善と副作用

旧Voicesで承認されたLeakage Check/Acceptance Gateを活用し、不適切な箇所があれば承認済み方式で局所修正する。

単にR2まで生成するのではなく、**R0・R1・R2のどの工程が、どの品質に寄与したか**を確認すること。

### Phase 2:英語化・レベル調整

比較可能な日本語原稿を基に、既存の忠実英訳・Standard向け簡易化を適用する。

Standard/Advancedで、人物の個性・立場・主観性が維持されているか確認する。

特に、英語化によって3人の発言が平板化・解説者化しないか評価する。

### Phase 3:音声Trial

3人のVoiceに、決定済みのAlgieba/Zephyr/Schedarを適用する。

- 既存の軽量TTSを優先使用する。
- 登場人物ごとのVoiceを全編で固定する。
- ナレーター・補助音声は既存の適切なFamily Y設計に従う。
- Standard/Advancedの承認済み音声品質仕様を維持する。
- ASR・音声QAを実施する。
- ユーザーが3人の意見を自然に聞き分けられるか確認できる試聴ページを作成する。

Pro系TTSへの変更など、追加費用・仕様変更を伴う判断は無断で行わない。

## 5. Trial成果物

以下を提出すること。

1. **R0/R1/R2の日本語原稿比較**と品質評価
2. 3人のVoice Cardと、それぞれの立場・人物像
3. Standard/Advancedの英語本文
4. Analytical Leakage Check・Acceptance Gate結果
5. Standard/Advancedの音声試聴ページ
6. 既存Family X基盤の継承状況とFamily Y固有の追加部分
7. 開発費・Trial費用・推定量産単価
8. Fable独立評価とProduction採用に向けた残課題

R0・R1・R2それぞれの音声化は必須としない。品質比較は原稿段階で実施し、音声化は品質評価に必要十分な候補を対象とする。

## 6. 予算・QCD

当初のTrial上限250円を基準とする。

ただし、今回の変更により、

- テーマ数は2件から1件へ減少
- Writer工程はR0のみからR0→R1→R2へ拡大

しているため、既存見積をそのまま流用せず、**変更後の概算費用を確認すること。**

250円以内で承認済み範囲を実施できる場合は、不要な少額承認を求めず進めてよい。

250円超過が見込まれる場合は、実行前に報告すること。

品質を最優先しながら、既存成果物の再利用・独立工程の並列化・不要なLLM呼出削減を徹底する。

量産単価70円/記事セットを目標とし、R1/R2の追加費用に見合う品質改善があるか評価する。

## 7. Productionとの境界・PM Gate

今回の到達目標は**Trial完了・ユーザー試聴・採用判断材料の提示**である。

- Family Yの正式Production採用は未決定。
- Family X/Zの正式Production経路を変更しない。
- Trial用の機構・Promptを無断で正式Productionへ配線しない。
- 新しい品質基準やValidatorを独断で追加しない。
- Trial成功時は`VALIDATED`まで。
- Fableの独立レビューを受け、ユーザーの正式採用判断を待つ。

Trial中に発見した既存仕様内の不具合は、承認範囲内で自律的に解決する。

## 8. 報告形式

報告は次の順とする。

1. **結論:Family Yの基本設計は品質面で成立するか**
2. R0→R1→R2の品質比較
3. 3 Voicesの自然さ・個性・意見の多様性
4. Standard/Advancedの品質・音声結果
5. 旧Voices品質問題への対策効果
6. QCD(費用・速度・推定量産単価)
7. 試聴URL
8. Fable受入結果・Status・必要なユーザー判断

必要なSSOT・OPEN_ITEMS・Git記録を更新すること。

**今回のTrialの核心は、3人の人物が生き生きと主観を語るFamily Yを、既存Production基盤と低い量産単価で実現できるか確認することである。**

Trial結果が良好でも、正式Production採用はユーザー判断まで保留すること。
```

## 2. 設計の正本と前提
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/DESIGN_PROPOSAL_02.md`(M1〜M7・S1〜S13反映済み)、`OPUS_REVIEW_01.md`、`INVENTORY_X_Z_SPEC_01.md`(接続点T1〜T17)、`INVENTORY_OLD_B_VOICES_01.md`。ユーザー決定で設計書から変わる点: TTS Voiceは固定(Voice1 Algieba/Voice2 Zephyr/Voice3 Schedar、自動割当不採用)/WriterはR0→R1→R2を全段Trialして比較(R0のみ採用は未決)/Comment4廃止は確定/テーマ1件。人物設計(Voice Card)は固定Voiceの声質・性別(Algieba=男性的、Zephyr=女性的、Schedar=男性的)と整合させる。
- 費用の再見積(開始前に確定して記録): 設計書§⑦の内訳を1テーマ・R0+R1+R2に置き換え: 段階(0)日本語Leakage校正5〜20円/段階(1)テキスト1テーマ(Research+Ledger+Y版B3+Card+R0+R1+R2+各段Leakage Check+局所書き換え+忠実英訳+A2簡易化+RF+学習支援構造)約45〜100円/段階(2)音声Std/Adv約19〜28円 → 合計約70〜150円の見込み。**250円超の見込みなら実行前STOP**。実費は`raw_usage_log`/`spent_jpy`で出典付き。
- Production境界: X/Zの.py・Prompt・閾値・辞書は変更しない。Y固有の差分はDEV/Trial専用ファイル(例 `er110_family_y_*.py`、Trial Prompt/brief)に置き、Production fileからの参照0をGrepで固定。共有moduleを使う場合は呼出側(Y側)でのみ挙動を変える(共有関数への引数追加が必要なら、既定値で既存挙動不変をtestで固定し、理由を記録)。X/Zへの影響0(X/Z出力のbyte一致回帰)。
- 既存基盤の再利用(T1〜T17): Research web_search→Fact Ledger→(Y版)B3→Writer→忠実英訳→A2簡易化→Risk Flagger→学習支援構造(Preview/Comment1〜3/KPFT+KP3V+CMU/In One Line/日本語タイトル)→TTS(gemini-3.8-flash-lite-tts、style profile)→ASR 3層→Audio Validation→Assembly→試聴ページ標準。X runnerは無変更で、Y用の薄い入口(DEV)から共有部品を呼ぶ。segment_id `full_story_part1〜5`に対する検査の網羅(M3: `A2_SLOWDOWN_TARGET_SEGMENTS`等の直書き一覧)はDEV側で対応し、Phase 3前にparity確認。
- 開発モデル原則(25節): 最新世代最上位系(Production Writerと同じgpt-6.1-sol等)。使用モデルと「最新か」を報告に記載。

## 3. Phase 0: 整合確認・DEV実装
1. 設計書§③-5の直書き一覧を再Grepして最終化(`full_story_part`、`_BODY_SEGMENT_NAMES`、`A2_SLOWDOWN_TARGET_SEGMENTS`、`resolve_narrative_role`、style_profile、audio_plan等)。Y part1〜5がX本文と同じ検査を受ける対応表を作る(Phase 3で使用)。
2. DEV実装: (a)Y版B3(3視点のStakeholder候補をスキーマ検証付きで出力。賛否中立の機械配置はしない。固定Voiceの声質・性別と整合する人物像の制約を入れる: Voice1=男性的声、Voice2=女性的声、Voice3=男性的声)、(b)Voice Card生成(6〜7項目、`not_my_point`は他2人の`concern`から決定論生成、世界スコープは背景fact id参照のみ、数値欄なし)、(c)Y版R0 Prompt(5段落ちょうど、個人/世界スコープ分離[M1]、Voice段落は数字なし、一人称"I"、話し言葉・常体[S13]、リードは「取材した」表現回避[S10]、最終パートは再定義要素なし・締め2〜3型[S7]、Fact Lock規則はリード/最終パートの世界スコープにのみ適用)、(d)R1/R2: XのR1/R2 Prompt(エンタメ性up等)をVoice文脈向けに最小限調整したY版(何を変えたか差分を記録。X Promptは無変更)、(e)Leakage Check(旧B承認済み7項目[Voice]/6項目[Tension]を日本語原稿向けに移植、Closing項目は最終パート規則へ吸収)、(f)局所書き換え(M5: flag段落のみ差替え、他段落byte固定、判定3回=初回+2回、書き換え後もR0同等の決定論検査[Fact Lockタグ・`clean_ja_for_next`・記号QA・`postprocess_ja`・5段落確認]、失敗時は全文書き直しへ戻さずSTOP)、(g)Acceptance Gate(残存flagのある原稿を後続へ流さない)、(h)決定論モニタ(記録専用、Gateにしない: Voice段落の数字、段落ごとのタグ数、一人称有無、最終パートとVoiceの語彙overlap)、(i)5段落契約と話者取り違え防止の決定論確認(M2)、(j)R0最終稿への`postprocess_ja`+記号QA(M6)。
3. 段階(0) M7校正: 旧B記事(正解ラベル付き: NG例=PN A2旧版/PN B1/3V汎用化Regressionでflagされた個体、OK例=PN A2新版/free_address)を日本語化し、日本語版Leakage Checkの誤検知・見逃しを測定。結果が悪ければGateとして使う前に定義を調整(調整内容を記録)。**Phase 1と並列可**(Phase 1のGate適用前に校正結果を反映する順序は守る)。

## 4. Phase 1: 日本語原稿・Writer比較(テーマ: 学校でスマホを禁止すべき?)
1. Research(web_search)→Ledger→Y版B3→Voice Card×3(人物像・立場・生活背景・価値観。固定Voiceとの整合を記載)。
2. R0→R1→R2を各段保存。各段で: Leakage Check(日本語)結果、決定論モニタ、5段落契約、Fact Lockタグ検査。不適切箇所は承認済み方式(局所書き換え上限2回)で修正し、修正前後を保存。
3. 各段の比較表(R0/R1/R2): 人物の個性・一人称の自然さ/3人の独立性・多様性(意味レベルの重複の有無、`not_my_point`違反)/面白さ(所見)/Leakage発生・改善・悪化(項目別件数)/R1・R2の寄与と副作用(語数・Leakage悪化・平板化)。**事実(機械結果)と所見(Sonnetの読み)を分ける**。対策が強すぎて自由な発言を阻害していないかの所見も記載。
4. Acceptance Gate通過原稿を確定(R0/R1/R2のうち、Phase 2へ渡す候補を「全部」=3本、費用が許せば。許さなければ理由付きで絞る[最低R0とR2])。

## 5. Phase 2: 英語化・レベル調整
1. 候補原稿ごとに既存の忠実英訳(Adv)→A2簡易化(Std)を適用。S2(A2簡易化に「各段落の話者・一人称・迷いの表現を保つ」1文を足したY版)はR2候補でのみ比較(+0.5円)。
2. Std/Advで、人物の個性・立場・主観性が維持されているか: 監視専用Leakage Check(英語、S3、Gateにしない)、一人称保持率、数字混入、段落=話者の対応(M2決定論確認)。平板化・解説者化の所見。
3. Risk Flagger(X既定)を適用しflag件数を記録(S5)。
4. 学習支援構造(日本語タイトル/In One Line/Preview/Comment1〜3/KP 3件[KPFT+CMU]/日本語意味・解説)を既存scaffold経路で生成。Comment4は生成しない。
5. Phase 3用の確定: 音声化する候補(品質評価に必要十分な本数: 原則Std/Adv各1本=最良候補1本。R0/R2の差が大きければ2本まで。理由付き)。

## 6. 成果物・SSOT
- `docs/research/FAMILY-Y-VOICES-DESIGN-01/TRIAL_01/`: `COST_ESTIMATE_01.md`(事前見積・実費)、`LEAKAGE_CALIBRATION_01.md`(M7)、`VOICE_CARDS_01.md`、`WRITER_COMPARISON_01.md`(R0/R1/R2原稿全文+比較表)、`EN_COMPARISON_01.md`(Std/Adv本文+評価)、`INHERITANCE_STATUS_01.md`(X基盤の継承状況とY固有追加部分、T1〜T17対応、Production参照0の証拠)、`PHASE3_PLAN_01.md`(音声化候補・Voice固定・Narrator/補助音声の設計[X準拠: Std=Aoede、Adv=Aoede+Charon; 3 Voices=Algieba/Zephyr/Schedar]・費用見積)。
- run dir: `er110_output/family_y_trial_01/<slug>/`(X/Z出力dirに書かない)。
- OPEN-463 Status更新、DECISION_LOG(Trial実施)、REPORT_LEDGER。commitは論理単位(DEV実装+test / Phase1 / Phase2 / SSOT)、明示add、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。X/Z出力のbyte一致回帰と全回帰(`run_project_regression.py`単独)で自分起因の新規失敗0。

## 7. 禁止
- X/Z Production .py/Prompt/閾値の変更、Pro系TTS等の仕様変更、新しい合格基準・Validatorの追加(モニタは記録専用)、Comment4の生成、テーマの変更・追加、250円超過、`VALIDATED`/`APPROVED_FOR_PRODUCTION`の自己宣言、音声生成(Phase 3は次委任。ただしPhase 3計画と費用見積は本委任で作る)。

## 8. 報告(docs/pm/RESULT_PACKET_FYT1.md、同内容を最終報告で)
(1)費用見積と実費(Phase 0〜2、出典) (2)M7校正結果 (3)Voice Card 3人の要約 (4)R0/R1/R2比較表の要約(事実/所見) (5)Std/Adv評価の要約 (6)Leakage/Acceptance Gate/決定論モニタ結果 (7)継承状況とY固有追加部分、Production無変更の証拠 (8)Phase 3計画(候補・費用) (9)commit・raw URL・SSOT (10)残課題 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。