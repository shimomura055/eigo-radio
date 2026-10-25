FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_07(Production Wiring: 中核数値保持方式v4+J2(範囲値正規化)をFamily X正式経路へ配線→runtime evidence→回帰→SSOT→Fable受入でPRODUCTION_WIRED)。あなたはsonnet-worker。Fable(PM)からの委任。ユーザー指示原文2通は§9に逐語(`docs/pm/delegation_log/2026-10-25_FX-CORE-NUMERIC-RETENTION-TRIAL-01_USER_04.md`[採用・配線指示]と`..._USER_05.md`[J2承認]へ全文保存)。

## 0. ユーザー承認(2026-10-25)
- 中核数値保持方式(Trial v4)=**APPROVED_FOR_PRODUCTION**、目標**PRODUCTION_WIRED**、対象Family X Std/Adv、Y/Z対象外。承認済みTrial方式を基本とし品質基準・仕様を独断で変更しない。
- J2(範囲値の波ダッシュ正規化)=**APPROVED_FOR_PRODUCTION**。Trial検証済みのJ2方式を採用、数値・桁・既存の数字丸め仕様は変更しない、記号QA・TTSとの整合を確認、v4と合わせてPRODUCTION_WIREDまで。
- 「Opusレビューの残件も承認済み範囲内で自律的に処理」「追加のユーザー判断は不要。未承認の仕様変更や重大な問題のみ報告」。
- QCD: 品質>速度>量産単価≫開発費。不要な待機・追加Trial・逐次処理を避け、独立作業は並列化。量産単価増分の基準=Trial推定約4円/記事(実測で評価)。

## 1. 前提(読むもの、必要箇所のみ)
- Trial正本: `docs/research/FX-CORE-NUMERIC-RETENTION-TRIAL-01/{DESIGN_03,DESIGN_04,ADOPTION_NOTE_01,TRIAL_RESULT_01,OPUS_REVIEW_01,OPUS_REVIEW_02,OPUS_REVIEW_03(条件C。委任_06が保存中。無ければ§2のFable要約を使う),PREREGISTERED_CRITERIA_03,PREREGISTERED_CRITERIA_04,COMPARISON_05}.md`、`er115_fx_numeric_retention_trial_01.py`(DEV wrapper: `with_field_schema`:1034-1041、v4指示文:95-104、M1:383-443、derive_E_r5、Gate、O-2'、M2、J2出力正規化、R4入力正規化:365-372、B3再実行:1142-1194)と`er115_*_test_01.py`(Gate経路mock test:194-245,486-502)。
- 並行の委任_06(Opus条件C反映: C-1オフライン再適用`C1_REAPPLY_01.md`、C-2対照標本、C-3 ADOPTION_NOTE改訂、`docs/pm/RESULT_PACKET_FXNR6.md`)。**着手時と配線完了前に存在を確認し、C-2(数値が主役でない記事での欄の挙動)の結果を受入条件の観察事項に反映**。委任_06はer115 DEVとdocsのみ編集、あなたはProduction側を編集(同一docs[ADOPTION_NOTE_01/OPEN-507/DECISION_LOG]は直前再Read・最小Edit)。
- Production: `er019_family_x_storyline_b3_fact_selection_01.py:118-157`(B3 schema定数、strict/additionalProperties:False、Y Trialからimportあり)、`er053_b3_deterministic_producer_01.py:450-551`(derive_ranks/cap_of)、`er053_family_x_factlock_ja_writer_01.py:87-94`(規則5)、`er019_family_x_ja_writer_o_r1_r2_01.py:51`(R0 Prompt)、Family Xニュースrunner(B3→W-1 R0→R1→R2→EN Std/Adv→記号QA→TTS…の正式経路、retry/regeneration/resume、記事あたり費用上限)、`er003_audio_tts_asr_safety.py:879-907`(波ダッシュNormalizer`normalize_tilde_placeholder_ja`、TTS用コピーのみ変更・「なになに」欠陥)、記号QA(R2停止条件)。
- SSOT: CURRENT_SPECのFamily X B3/Writer/数字丸め/記号QA節をGrep、OPEN-507/OPEN-509、UDR #194/#195、DECISION_LOGの本件決定。
- 他agent: FAMILY-Z-STUDY Part 1配線(`er019_family_x_audio_production_runner_01.py`のKP/scaffold部分と`er019_family_x_kp_explanation_01.py`を編集中。**あなたはKP/scaffold部分を触らない**。同一ファイルを編集する場合は一時index方式でcommit)、Family Y(er110)、Z Chunk(DEV)。Production file編集前に`git status`で他者差分を確認。

## 2. 配線仕様(Fable決定=承認済み範囲内。Opus条件Cの「配線実装時に必須1〜8」を全て反映)
1. **欄の追加**: schema定数を直接書き換えず、Family X Production B3呼出時にdeepcopyへ`reader_must_hear_numbers`(最大2・空可)を足す関数で配線(Y Trialのimport契約を変えない)。v4指示文(V2=Storyline数値規則O-1'+欄指示の組合せ)をProduction B3 Promptへ=検証済みのバイト同等。J1(B3 Prompt/schema変更)はユーザー承認済み(本指示)。
2. **E=欄**: 欄の数値を決定論でEへ。M1=構造違反のみ(写像不可/_STORYのみ/2個超/数値表記なし/年・序数/周辺数値)→B3再実行1回。再実行後も違反なら**E=∅で続行し、WARN+runtime evidence**(現行Production同等の品質、新しい既定動作を作らない)。欄が空の記事はGateなし・O-2'なし=現行動作。
3. **保持Gate**: R0直後(およびR1/R2後)のE保持検査→不足時は既存再生成枠1回(記号QAの既存枠と共有、DESIGN_03 §3)→なお不足なら**既存Human Reviewキューへ停止**(検証済み設計J3。STOP先が既存HRキューに繋がることを0円testで確認)。
4. **O-2'**: Eと同単位系の非E中核をWriter入力でメモリ上の付替え(年系は残す)。規則5文言・R0 Promptは不変(CURRENT_SPECに運用を追記)。
5. **M2**: R1/R2での新規数値検出→既存再生成枠。
6. **J2**: Family X Writer出力(R0/R1/R2)の後処理1か所で範囲値の波ダッシュ「A〜B」→「AからB」(数字・桁不変)。R4(入力側`range_norm`)がTrialの検証済み構成に含まれていれば同じ判断で配線。既存TTS Normalizerは役割が違うため二重化せず残置し、「J2が先に『から』へ変換すれば範囲値ではNormalizer欠陥が表に出ない」関係をOPEN-509に記録。記号QA(R2停止条件)との整合と、TTS読み(「42から46メートル」)の確認。**J2はR5のflag内に置かず独立の後処理**。
7. **retry/resume/再生成**: B3再実行1回・R0/R1/R2各1枠を既存枠と共有。途中段からの再開は保存済み`reader_must_hear_numbers.json`からEを決定論で再構成(B3を呼び直さない)。欄のない旧記事の再生成はE=∅。記事あたり費用上限に最悪ケース(B3再実行+各段再生成≈28円+)が収まることを確認し、収まらなければ上限内で動く設計(B3再実行を優先、再生成枠は既存どおり)と報告。
8. **runtime evidence**: run単位で`b3_rerun`・違反理由・欄の1回目/最終値・E・Gate発火段・再生成・O-2'付替え・M2・J2適用箇所・actual model_id・prompt sha・routingを記録。COMPARISON_05の「rerun=None」表示不具合は委任_06が修正中(重複しない)。
9. **Gate経路の担保**: er115のmock test(194-245,486-502)をProduction側testへ移植(Gate発火→再生成→HR停止の経路、E=∅経路、M1最終違反→E=∅+WARN経路、J2正規化、resume再構成、旧記事E=∅)。
10. **撤去・残置**: Productionへ移すのはv4・M1構造検査・E=欄・Gate・O-2'・M2・J2(+R4)のみ。v1〜v3指示文・Storyline由来E・RULE9・`resume_w1_dev_from_r2`はer115に残置しProductionからimportしない(Grep確認)。固定表は参考。不要になった旧処理・重複検査があれば整理(撤去一覧を報告)。
11. **C-1(欄をderive_ranks優先に加える最適化)は今回配線しない**(検証済みv4からの挙動変更のため)。委任_06のC-1再適用結果を「後続の改善候補(B3再実行率と約4円/記事の低減)」としてADOPTION_NOTE/OPENに記録。
12. **半導体型の初回選定傾向(見通し値)**: 指示文追加はしない(Opus推奨、ユーザー評価済み基準の独断引締め回避)。runtime evidenceで欄の1回目値を記録し、最初の数記事をFableが確認する受入観察事項に含める。

## 3. 手順
- Step 1(API 0): 配線設計メモ`WIRING_DESIGN_01.md`(上記1〜12の実装箇所・関数・test計画、記事あたり費用上限の確認結果)→実装+test(移植含む)→無料test全PASS→**commit(Production実装+testは1 commit=revert単位)**。
- Step 2(有料): **正式runtime検証**。対象=月の記事(`moon_shrinking`、公開版は数値脱落=本方式の出発点)を**正式Family X経路でStd/Adv完全再生成**(B3→R0→R1→R2→EN Std/Adv→記号QA→TTS→組立→page)。**有料起動前に当日(JST)累計を集計**し、見積(≈70〜80円)を足して1,000円を超える見込みなら、本文段(B3〜EN Std/Adv+記号QA、≈25円)までで止めて証拠を取り、TTS以降は日次上限解除後に実施する計画を報告(予算上限は待機の正当理由)。1,000円内なら完走。生成物は`user_test/`配下の完成候補として置き、**既存公開ページは差し替えない**(ユーザー最終試聴後=USER_LISTENING_PENDING)。記事上限・STOP・HR Lockは既存どおり、迂回禁止。起動回数・再起動間隔150秒・RESTART_STORM順守。
- Step 3: evidence確認(欄=約42〜46m、R0〜Adv保持、不要数値0、J2「42から46」、英語"42 to 46"、記号QA PASS、TTS読み確認[ASR一致]、数字丸め仕様の正常動作、Gate/再生成/HRの発火有無)。Trialの4記事型の知見は回帰test(保存済みB3出力・Writer出力での決定論再適用=0円)で活用。
- Step 4: 回帰(`run_project_regression.py`+pytest群。他agent起因はclean worktreeで再現確認して分類)、SSOT(CURRENT_SPEC新節: 中核数値保持方式v4+J2の正式仕様、規則5運用、E=∅/M1最終違反/Gate不足の既定動作、runtime evidence項目、量産単価; OPEN-507=`WIRED_PENDING_FABLE`、OPEN-509=J2配線で解消(Normalizer残置の関係を記録)、DECISION_LOG、UDR #194/#195へ実施記録)、`docs/pm/RESULT_PACKET_FXNR7.md`、ACTIVE_TASK自行。
- 委任文逐語保存: `--index 536`で`..._DELEGATION_07.md`(冒頭「FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_07」で照合、不一致なら±5)。
- Git: 対象pathのみadd(`-A/-u/-f/-N`禁止)→`git diff --cached --name-status`→`git commit --only`→`git push origin HEAD:main`。secret grep 0件。wav/raw_usage_log/STOP/lock/telemetry不追跡(公開mp3は`user_test/`配下のみ)。

## 4. STOP条件(整理して報告、自動続行なし)
未承認の仕様変更が必要 / 既存Gate・STOP・HR Lockの迂回が必要 / 記事あたり上限・日次1,000円超過見込み(上記の本文段まで計画で対応できない場合) / 重大品質問題 / 他agentと同一Production fileで解決できない衝突。

## 5. 報告(Fableへ、ユーザー§7の簡潔形式が作れる形)
(1)Production Wiringの完了Status候補(受入条件: 配線/Std・Adv正式runtime/retry・fallback整合/必須test/承認内容と実動作の一致/SSOT/Git/判断待ち・Dangling Reference無し) (2)中核数値保持・J2・数字丸めのruntime evidence要約(月の記事: 欄・各段の数値・J2適用・記号QA・TTS読み・費用) (3)回帰test結果 (4)制作時間・量産単価への影響(実測、Trial推定4円との比較) (5)残存リスク・Open Item(C-1候補、半導体型初回選定の観察、C-2結果) (6)Git/SSOT反映・commit hash・raw URL (7)月の記事 完成候補の試聴URL(公開差替えはしていない旨) (8)RESULT_PACKET 4行+「判定整合」1行。

## 9. ユーザー指示原文(逐語)
### USER_04.md
# Claude Codeへの指示｜Family X 中核数値保持方式 Production正式採用・配線

## 1. ユーザー正式承認

Family X「中核数値保持方式」（Trial v4）について、ユーザーが**Production正式採用を承認**した。

- 対象：Family X（Standard／Advanced）
- Status：**APPROVED_FOR_PRODUCTION**
- 目標：**PRODUCTION_WIRED**
- Family Y／Zへの展開は今回の対象外
- 承認済みTrial方式を基本とし、品質基準や仕様を独断で変更しない

## 2. 採用する方式

B3が決定した記事の切り口に基づいて「読者が聞くべき重要数値」を選定し、その数値を後続工程で保持する。

重要な原則：

1. 数値は記事の切り口に対する必要性で判断する。記事ごとに固定しない。
2. 選定した中核数値は、R0→R1→R2→英語Standard／Advancedまで保持する。
3. 不要な数値の混入を防ぎ、数値の羅列による文章品質・エンターテインメント性の低下を避ける。
4. **既存の承認済み「数字の丸め」仕様を維持する。** 中核数値保持と矛盾させず、不要な桁数を復活させない。
5. 新たな事実・数値を創作しない。

TrialでVALIDATEDとなったv4を採用基準とする。検証済みの判定ロジックや境界条件を省略しない。

## 3. 実装前確認

CURRENT_SPEC、DECISION_LOG、OPEN_ITEMS、Trial結果、既存Production経路を照合する。

特に以下を確認する。

- Opus条件Cレビューの結果と未解決指摘
- 半導体記事で見られた、不適切な見通し数値の初回選定傾向
- 既存の数値丸め・数値保持・Fact整合性検査との関係
- B3再実行条件、Writer再生成、retry／fallback／resumeとの整合
- DEV／Trial専用処理と正式Production処理の相違

既存機構を最大限利用し、検査の重複や不要なLLM呼出を増やさない。

Opusレビューに重大な未解決事項がある場合は、承認済み仕様内で解決する。仕様変更が必要ならUSER_DECISION_REQUIREDとして報告する。

## 4. Production Wiring

正式Production初回経路に、承認された中核数値保持方式を配線する。

以下を満たすこと。

- Family XのStandard／Advanced双方に適用
- B3から最終英語原稿までの保持
- retry／fallback／regeneration／resumeでも仕様を維持
- 既存の数字丸め仕様との整合
- 既存のFact・文章品質・数値検査との整合
- DEV限定の実装や設定変更で終わらせない
- 不要になった旧処理・重複検査を整理する

## 5. 検証・受入条件

Trialの成功だけでProduction配線完了としない。

正式Production経路でruntime検証を行い、以下を確認する。

1. B3が記事の切り口に沿って中核数値を選定している。
2. R0／R1／R2／Standard／Advancedまで中核数値が保持される。
3. 不要数値の混入・数値創作がない。
4. 承認済みの数字丸め仕様が正常に機能する。
5. retry／fallback等の後続経路でも同じ品質を維持する。
6. 文章の自然さ・エンターテインメント性が損なわれない。
7. 必須Regression／Validator／Integration TestがPASSする。

Trialで確認した4記事型の知見を回帰検証に活用する。不要な有料Trialを繰り返さず、既存証跡と無料テストを最大限再利用する。

正式runtime evidence、実際のモデル・Prompt・routing、テスト結果を記録する。

## 6. QCD

優先順位は **品質＞完成速度＞量産単価≫開発費**。

- Trialで確認された品質水準を守る。
- 不要な追加改善・日付分割・待機を行わない。
- 独立作業は並列化し、最速で完成させる。
- 量産単価の増分はTrial推定で約4円／記事。これを基準に実測・評価する。
- 70円／記事セットの目標を意識し、品質を維持した原価低減を図る。
- 既存承認予算内で自律的に不具合を修正・検証する。

## 7. 完了条件・報告

以下をすべて確認した時点で **PRODUCTION_WIRED** とする。

- 正式Production経路への配線
- Standard／Advancedの正式runtime検証
- retry／fallback等との整合
- 必須テストPASS
- 承認内容と実動作の一致
- CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS更新
- 必要なGit commit／push
- 未処理の判断待ち・Dangling Referenceがないこと

最後に、Fableの独立受入評価を実施する。

**最終報告は以下を簡潔に示すこと。**

- Production Wiringの完了Status
- 中核数値保持・数字丸めのruntime evidence
- 回帰テスト結果
- 制作時間・量産単価への影響
- 残存リスク・Open Item
- Git／SSOT反映状況

承認済み範囲の不具合は自律的に解決し、技術上の軽微な判断をユーザーに求めない。

未承認の仕様変更、重大な品質リスク、予算超過が必要な場合のみSTOPして報告する。

**必要十分な品質を満たしたら、それ以上の磨き込みをせず速やかに完了すること。**

### USER_05.md
Claudeへ

**J2方式（範囲値の波ダッシュ正規化）のProduction正式採用を承認します。**

- 対象：Family X（Standard／Advanced）
- Status：APPROVED_FOR_PRODUCTION
- Trialで検証済みのJ2方式を採用する。
- 数値・桁・既存の数字丸め仕様は変更しない。
- 記号QA・TTSとの整合を確認する。
- 中核数値保持方式v4と合わせて、**PRODUCTION_WIREDまで進めること。**
- 正式runtime evidence、回帰テスト、SSOT／Git反映まで確認する。

Opusレビューの残件も承認済み範囲内で自律的に処理してください。

品質を守りながら最速で完成させ、不要な待機・追加Trial・逐次処理は避けてください。

**本件について追加のユーザー判断は不要です。** 未承認の仕様変更や重大な問題が発生した場合のみ報告してください。