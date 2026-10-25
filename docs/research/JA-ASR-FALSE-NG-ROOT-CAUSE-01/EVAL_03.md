# EVAL_03(v2 API 0再評価、委任_04、2026-10-25)
評価対象=プロトタイプ **v2** `proto_reading_compare_02.py`(sha256 `bcb042c651f05c7801b382e51b802a870e1240892d3ae65efc6cdbbca27c6144`)。v1(`8799aa60fed66e2d…`)は不変。事前登録=`PREREGISTERED_CRITERIA_03.md`(基準は02同一)。評価=`eval_api0_v2_01.py`(API 0・LLM不使用・socket guard。再現: リポジトリrootで`PYTHONUTF8=1 .venv/Scripts/python.exe docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/eval_api0_v2_01.py`、2回実行で標準出力が完全一致=決定的)。出力=`eval_api0_v2_01.out.txt`/`.out.json`/`eval_api0_v2_01_phase3.out.json`/`eval_api0_v2_01_diff.out.json`(v1との差分)。
使用モデル: 新規ASR/TTS呼出なし(保存済み転写のみ。転写の元=EVAL_02記載のOpenAI `gpt-4o-mini-transcribe`/Azure ja-JP/`gpt-4o-transcribe`[O1のみ])。LLM判定なし(決定的ルール)。費用0円。

## 1. 事前登録基準の結果
| 基準 | v1(EVAL_01/02) | **v2(本評価)** | 合否 |
|---|---|---|---|
| 1 増分誤PASS(N-1 150、Primary+A4(a)(b)込み) | 0 | **0** | 合格 |
| 1 増分誤PASS(N-3 30、案A Primary) | 0 | **0** | 合格 |
| 1 増分誤PASS(N-3 30、A4(a)込み) | **1(N3-21)** | **0** | 合格(v1の不合格が解消) |
| 1 増分誤PASS(N-3、A4(b)込み=新仕様候補) | 1 | 0 | 参考 |
| 2 非回帰(P-4 421ユニーク/現行PASS334) | 回帰0 | **回帰0** | 合格 |
| 2 非回帰(正例対照47: 現行PASS37→v) | v1 39 PASS/回帰0 | 39 PASS/**回帰0** | 合格 |
| 2 非回帰(Phase 3新規転写: 月題・N-3・O1でbase PASS→NG) | 0 | **0** | 合格 |
| 3 P-3 flip(NG pool 150転写) | 8(primary 2+secondary 6) | **8**(失う救済0/増加0) | 合格(flip集合同一、EVAL_01の個別審査を継承) |
| 4 警告継承 | 付与 | 付与(Primary側コードパス不変、test済) | 合格 |
| 6 費用 | 実費約5.6円 | **追加0円** | 合格 |
→ 厳密適用で**基準1〜6を全て満たす**。既存誤PASS(報告のみ): N-1 23件・N-3 16件(v1と同数・OPEN-517)。

## 2. v1→v2 差分表(変化した判定の全件)
`eval_api0_v2_01_diff.out.json`から。全コーパス(N-1 151対・P-3 150転写・P-4 421・Phase 3 N-3 30・月題12転写+O1 6・Melos)でv1とv2で判定が変わったのは**2件のみ**:
| ID | 原稿 / 転写 | v1 | v2 | 備考 |
|---|---|---|---|---|
| **N3-21**(N-3) | `三日待った` / OpenAI `三日間待った。`(NG)・Azure `3日待った。` | A4(a)でPASS_WITH_WARNING(増分誤PASS) | **NG** (`a4a_irregular_reading_value:三日`) | **NGに戻った**(目的) |
| N1-new-035(N-1、Secondary見立て) | `3人でついたちに会った` / `三人で一日に会った` | A4(a)受理(Secondary見立て) | 不受理 | Primary側は現行で既にPASS(`NUMERIC_VALUE_EQUIVALENT_MATCH`・既存誤PASS)で最終判定は不変=非増分 |
- 失う救済: **0件**。月題12転写(v1の救済1件=attempt3#0)・Melos preview・P-3 flips 8・P-4 flips 2・正例対照のいずれも変化なし。
- N-1のSecondary A4(a)受理: v1 4件→v2 3件(残る3件=`三分の一`↔`3分の1`×3は、Primary側が現行で既に通す型=非増分)。
## 3. 月題・Melos
- 月題12転写: v2もv1と同一(案A救済=attempt3の1件のみ。数詞崩れの揺らぎは救えない)。**効果の限定性はv1から不変**。
- Melos preview(`三日目`): Primary側=`PRON`(`JA_PRON_VALUE_EQUIVALENT_MATCH`+警告`JA_NUMERIC_IRREGULAR_READING`/`JA_PRON_EQUIVALENT`)でv1と**完全同一(副作用なし)**。Secondary(Azure)はv1の時点で既にC2(`町→街`)で不受理でありA4(a)は寄与していなかった=v2で失う救済なし。(Primary層の`VALUE_ONLY`の不規則読みは、Productionが既に受理するためv2でも除外していない。)
## 4. 事前登録写像によるStatus候補
基準1〜6を満たす → **v2=VALIDATED(限定)候補**。ただし限界を併記: (a)月題の誤NG安定解消は未達(12転写中1件、数詞崩れ・同音異字は別途Azure併用等=UDR #136)、(b)A4(a)は`is_irregular_sig`の閉集合のみ除外=連濁/音便系(三本・六百・三百・三階)は残る(`DESIGN_02.md`§2、Primary既存の盲点と同型)、(c)同一データでの再評価(未知データでの汎化未確認)。最終Statusは Fable。Phase 4は提案段階にない。
## 5. OPEN-517(既存誤PASS16件)
`DESIGN_02.md`§3に型別・箇所・是正案の方向・API 0影響調査(155件中10件がNG化、うち正常実attempt1件[`いちばん`↔`一番`]の新規誤NG=除外処理が必須)。実装なし。
