# ER-006-GATE-CALIBRATION-ASR-CASCADE-MATH-VALIDATOR-01 完了報告

## 1. 何が問題だったか

前タスク(ER-006-COST-WASTE-RCA-RESEARCH-COVERAGE-GATE-01)で、3つの問題が見つかっていました。

**問題A: Research Coverage Gate(記事執筆前に取材情報が足りているか判定するチェック)がNo.6で誤判定**
Gateは「一般的な心理学研究を、身近な具体例へ類推適用する」という本番組の通常の書き方と、「Evidenceの範囲を超えて因果関係や頻度を断定してしまう」という本当に問題のある書き方を区別できず、問題のないNo.6を「Research不足」と誤判定していました(False Positive)。

**問題B: 固有名詞の音訳ゆれによるTTS(音声合成)の無駄な再生成**
No.6の"Sweeny"という人名が、ASR(音声認識による検証)で"Sweeney"と書き起こされる差だけで、本来は音声を作り直さずに人間レビューへ回すはずの仕組み(Cascade)が機能していませんでした。原因は2つ:
1. Cascade機能自体がProduction設定でOFFになっている
2. A2版では"result"(単数)/"results"(複数)という無関係な言い回しの違いが同時に起きており、これが「固有名詞だけの差」という条件を満たせなくしていた

**問題C: 数式表記(*b* = 0.90、2 × 10⁻¹⁶ など)をチェック機構が理解できていなかった**
記事中の統計値の表記(等号・掛け算記号・指数)を、ASR側の話し言葉("equals"、"times"、"to the minus 16th"等)と同一だと認識できず、実際には正しく読み上げられている音声を「内容が間違っている」として繰り返し作り直していました。

## 2. 何を変更したか

### (1) 数式表記の正規化を追加(`er006_preprod_hardening_01_validation.py`)
以下の記号・話し言葉の対応関係を、安全な形(意味が変わる差は区別したまま残す)で吸収するようにしました。
- `=`(等号)⇔ "equals" / "is equal to" / "was equal to"
- `<` `>`(不等号)⇔ "less than" / "greater than"
- `×`・数字に挟まれた`x`(掛け算記号。ASRが実際にこの形で書き起こす例を確認)⇔ "times"
- Unicode上付き文字(`10⁻¹⁶`)・ASCIIキャレット表記(`10^-16`。ASRが実際にこの形で書き起こす例を確認)⇔ "10 to the minus/negative 16th"

**発見した実装上のバグ**: Unicode上付き文字の変換を、既存の発音区別符号除去処理(`strip_diacritics`)より後に置いていたため、そちらの処理が先に上付き数字を通常の数字へ分解してしまい、指数だという情報自体が失われる不具合がありました。処理順序を入れ替えて修正しています。

指数の符号・桁が異なる場合(`10⁻¹⁶`と`10⁻⁶`、`10⁻¹⁶`と`10¹⁶`等)は、これまで通り区別して不一致のまま残るよう、専用のマーカーで管理しています。

### (2) 規則的な単数形/複数形の差を吸収(同ファイル)
"result"/"results"のような、規則的な語尾(-s、-es)だけが異なる語のペアを、意味誤りではなく表記ゆれとして扱うようにしました。無関係な語(例: "cats"と"dogs")を誤って同一視しないよう、語尾の形・長さで厳格に絞っています。

### (3) Research Coverage Gateのプロンプト較正(`er006_research_coverage_gate_01.py`)
「一般的な心理学的Evidenceを身近な例へ類推適用することは問題ない」「ただし因果関係・頻度・業界慣行・特定の行動についての具体的主張へのoverreachは問題」という判断基準を、GATE_DEVELOPER_MESSAGEへ明記しました。

### (4) 回帰テストの追加(`er006_preprod_hardening_01_validation_test.py`)
上記(1)(2)について、実際のNo.6音声で観測された表記パターンを含む23件のfixture(Positive/Negative両方)を追加しました。

## 3. 何が改善されるか

**全て既存ログの再生・実データでの検証のみ(新規TTS/ASRは検証用の少量のみ)で確認済みです。**

### 数式表記の修正による実測の節約効果
No.6の該当2 segmentで、実際に記録されていたTTS生成コストと、修正後のValidatorを本番と同じ判定ロジック(`evaluate_attempt`、3回連続で同じ判定なら打ち切り)へ通した場合に必要だった生成回数を比較しました。

| Segment | 実際の生成回数 | 修正後に必要だった回数 | 節約額 |
|---|---|---|---|
| B1 point_two | 3回($0.0233 / ¥3.74) | 1回 | $0.0159(¥2.54) |
| A2 point_one | 12回($0.1193 / ¥19.08、最終的にSTOPPED=完全失敗) | 2回 | $0.0987(¥15.80) |

A2 point_oneは実際には12回全て失敗し「STOPPED」(人間の介入が必要な完全失敗)扱いになっていましたが、修正後のロジックでは2回目で正常合格しています。

### Sweeny(固有名詞)ケースの節約効果
Cascade機能のON/OFFで2パターン報告します(OFFが現在のProduction既定値、ONは今回のタスクでは変更していません)。

| Segment | 実際 | Validator修正のみ(Cascade OFF、現状維持) | +Cascade ON(要判断) |
|---|---|---|---|
| B1 full_story_part1 | 6回(¥13.02) | 3回(¥6.12、節約¥6.89) | 1回(¥2.00、節約¥11.01) |
| A2 full_story_part1 | 12回(¥20.92、STOPPED) | 6回(¥10.66、節約¥10.26、最終判定もASR_VALIDATION_UNCERTAINへ改善) | 1回(¥1.84、節約¥19.07) |

### 合計(この4 segmentのみ、No.6全体のごく一部)
- 実際の合計: $0.3547(¥56.75)
- Validator修正のみ(Cascade現状維持): $0.1329(¥21.26)、**62.5%削減**
- Validator修正+Cascade ON: $0.0521(¥8.33)、**85.3%削減**(Cascadeによる追加ASRコストは1回あたり$0.00002程度で無視できる水準)

### Research Coverage Gateの較正結果
| Topic | 較正前 | 較正後 | 要求値 |
|---|---|---|---|
| No.4(スーパー) | MORE_RESEARCH_REQUIRED | MORE_RESEARCH_REQUIRED | ✅一致 |
| No.5(カフェ) | COVERAGE_PASS | COVERAGE_PASS | ✅一致 |
| No.6(配送) | MORE_RESEARCH_REQUIRED(誤判定) | **COVERAGE_PASS**(修正) | ✅一致・Flip成功 |
| No.1(ベンチ) | (未検証) | MORE_RESEARCH_REQUIRED | 要求なし |
| No.2(サブスク) | (未検証) | MORE_RESEARCH_REQUIRED | 要求なし |
| No.3(スタートアップ) | (未検証) | COVERAGE_PASS | 要求なし |

必須のNo.4/5/6は全て要求通りに動作しました。ただし、既に配信済みのNo.1・No.2でも「タイトルの前提(例:『より多くの都市が』という頻度の主張)を裏付ける直接的Evidenceが不足」「企業側の動機を示す直接的Evidenceがなく因果を断定しかねない」という、具体的で較正基準に沿った理由でMORE_RESEARCH_REQUIREDと判定されました。これは較正の誤作動ではなく、同種のEvidence Coverage上の懸念が過去の配信済みTopicにも存在する可能性を示す新しい発見です。

### 回帰テスト
- プロジェクト全体の回帰テスト: 1753件中1753件成功(既存挙動への影響なし)
- 本タスクで追加したValidator fixture: 55件中55件成功(既存32件+新規23件、Positive/Negativeとも意図通り)

## 4. リスクや注意点

1. **Gate較正の判定(Part A)**: `READY_FOR_PRODUCTION`ではなく **`PROMISING_BUT_MORE_DATA_NEEDED`** と判断しました。理由: 必須の3 Topic(No.4/5/6)は正しく動作しましたが、No.1・No.2で予期しなかった判定が出ており、これが「較正のしすぎ(過検知)」なのか「過去のTopicにも実在する編集上の懸念」なのかは人による確認が必要なためです。**タスク仕様の通り、Production配線は行っていません**。
2. **`FEATURE_FLAG_SECONDARY_ASR_ENABLED`は`False`のまま変更していません**。上表の「+Cascade ON」列は今回有効化した場合の参考値であり、実際に有効化するかはCLAUDE.mdの方針に基づき、影響範囲の大きい判断としてユーザーの確認を得てから対応します。
3. A2 point_oneでは、TTSが"*b* was 0.90"を"B equals 0.90"のように言い換えてしまう(記号ではなく単語自体の違い)ケースが一部残っており、これは意図的にValidatorでは吸収していません(過度な同義語吸収は別種の誤りを見逃すリスクがあるため、タスク仕様の対象外としています)。
4. 固有名詞専用のホワイトリスト("Sweeny"=="Sweeney"等)や、記事固有の特別扱いは一切追加していません。全ての修正は数式記号・規則的複数形という一般的なパターンに対するものです。

## 5. 変更ファイル

- `er006_preprod_hardening_01_validation.py`(数式正規化・複数形吸収)
- `er006_preprod_hardening_01_validation_test.py`(fixture追加、55件)
- `er006_research_coverage_gate_01.py`(Gateプロンプト較正)
- `run_coverage_gate_backtest.py`(No.1-6のbacktestへ拡張)
