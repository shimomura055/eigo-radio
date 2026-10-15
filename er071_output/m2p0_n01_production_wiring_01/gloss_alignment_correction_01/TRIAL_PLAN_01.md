# TRIAL_PLAN_01 (KP-GLOSS-ALIGNMENT-DESIGN-CORRECTION-TRIAL-01 委任_01A、2026-10-15)

Status: **計画のみ**(実行しない、費用JPY0)。DESIGN_DRAFT_01(Opus条件Aレビュー後)の実装完了後に実行する。全結果は**DEV/Trial**であり、`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`にはならない。
順序(ユーザー§5): まずオフライン(JPY0)→ 次に独立パターンをまとめた有料Trial。件数は「パターン種類×観測失敗率×情報価値」で決め、件数増自体を目的にしない。

## 1. オフライン検証(JPY0、実装後に再実行可能な決定論検証)
| ID | 内容 | 入力/分母 | 観測指標 | 合格基準(案) |
|---|---|---|---|---|
| O0 | 実施済み: 現行ルールの誤NG候補・意味欠落候補の規模(`OFFLINE_AUDIT_01.md`) | census 1,129 item、A'窓 765 item、replay 27 row | 誤NG母集団28/29、旧gloss不整合6件中現行ルール捕捉3件 | 参考(実施済み) |
| O1 | **既存glossの非劣化(差分0件)**: 新`align_glosses`をmock LLM(呼出されたら失敗)で全record再生し、対象外itemのmergedが完全一致 | census 226 record/1,129 item | 対象外itemの差分件数、対象外へのLLM呼出数 | 差分0、呼出0 |
| O2 | 追加語の機械算出 | 対象ユニーク8件(+全対象11 row) | 算出できた件数 / 追加語を拾えなかった件数 | 8/8(実施済み)を維持。追加語を過少/過大に拾うケースがあれば列挙 |
| O3 | 機械検査のunit test(誤NG/誤PASS):`based on interviews`+「～をもとにした」→FAIL / 「インタビューをもとにした」→PASS / span不実在→FAIL / span記号のみ→FAIL / 真+書換→INVALID / 偽+不変→INVALID / 追加語なしの正当な「～」(`point to`+『～を示す』)→対象外で不変 / スロットKP『～を～だと宣言する』→PASS | 合成ケース約15 | 期待どおりの判定 | 全件期待一致 |
| O4 | 既知不整合8ユニーク(目視ラベル付)に対する機械検査のみでの検出可否の机上確認(旧glossにはspanが無いため、期待される検出類型の分類) | 8ユニーク(不整合6) | 機械検出型(span欠落: prices/me/watch/interviews)/ 言語判断型(helper↔人) | 型の分類を記録(判定にはTrial T1が必要) |
| O5 | replay既存出力の判定矛盾(真⇔不変) | replay_high/medium 各27 row | 矛盾件数 | 0/27・0/27(実施済み。新規LLM出力でT1で再測) |
オフラインは全てAPI 0。O1は`select_alignment_targets`/`align_glosses`の既存関数を使用し、新規Validatorは作らない。

## 2. 有料Trial(gpt-6-luna、reasoning effort high。本番ラインと同一モデル)
モデル: 現行SUPPORT_MODEL`gpt-6-luna`(最新世代最上位/推奨系。`VALIDATION_01.md`冒頭の記載に依拠、今回再確認はしていない)。旧/下位モデル・medium effortは使わない(例外理由なし。medium切替は過去に提案しないと決定済み)。
共通条件: 実行前に`stop_scope_check_01.py`でSTOP確認、予算上限をrunnerに設定、Trial専用out_dir(`gloss_alignment_correction_01/trial_*`)、本番run dirと完全分離、flagは明示指定。独立なbatchは**まとめて並列実行**(直列化する理由が無い)。

### T1: 再整合の実効(独立パターンを1回にまとめて実行)
| パターン | 内容 | item数 | rep | eval | 根拠(なぜこの件数か) |
|---|---|---|---|---|---|
| P1 | 拡張KP・既知不整合(`based on interviews`×『～』『〜』2表記、`raw-bean prices`、`bring in a human helper`、`close around me`、`urge to watch`) | 6 | 2 | 12 | 実発生パターンそのもの。過去replayで揺れが出た(`close around me`のrep差)ため2rep |
| P2 | 既に正しいgloss(`locked into a narrow view`、`based on interviews`+『インタビューをもとにした』) | 2 | 2 | 4 | 不変保証の実測。過去に実際の整合例が2つしか無い |
| P3 | 「～」を含む正当な辞書表現(対象へ強制投入): `point to`/`answer for`/`keep up with`/`fall into`/`speak for`/`turn out not to be`/`put solo travel at`/`be associated with` | 8 | 2 | 16 | 欠陥①の誤NG検証の中心。census 29件のうち28が正当で、多様な型(目的語/補語/数値スロット)を代表8件で網羅 |
| P4 | 具体語欠落の注入(合成): 例 `lead to higher costs`+『～につながる』、`point to the cause`+『～を示す』 等 | 6 | 2 | 12 | 実記録は欠落4+弱1しか無く、spanが「存在するが意味が違う」型も必要(誤PASS検証) |
| P5 | 人称一般化・主語語 (`close around me`系、`take their/one's time`系を合成) | 3 | 2 | 6 | OPEN-357(me一般化)の再確認。頻度は低い(OFFLINE_AUDIT_01: 1.9%)ので最小 |
| 合計 | | 25 | | **50 eval = 10 batch(5 item/batch)** | |
P6(KP短縮・一般化): 対象外のためAPIに乗らない。O1で「LLMに渡らない」ことをオフライン検証(有料不要)。

観測指標: (1)最終gloss不整合(目視+機械)数 — P1/P4 (2)整合済み対照の不変率・書換率 — P2/P3(目標: 誤FAIL=整合glossのretry/failure化 0) (3)機械検査FAIL内訳 (4)判定矛盾(真⇔不変)件数 (5)`added_word_mappings`のspan実在率 (6)few-shot例の影響(例そのままの出力が不自然に混入しないか) (7)usage/cost実測(新スキーマの出力トークン増分)。
統計の限界(明記): P2+P3 = 20 itemで書換0件でも95%上限は約14%(rule of three: 3/20×2rep→独立性弱く実効はさらに甘い)。P1+P4 = 18 item。**少数での限界を超える主張はしない**。

### T2: 誤PASSの追加検証(条件付き。T1の結果次第でFableが実行可否判断)
- 目的: 「機械検査を通り抜けるが意味が誤っている(span実在・意味違い)」gloss、および自然さ違反を、LLM判定が拾うかを測る。対象=T1出力50 + 意味違い注入12(合成) = 62 → 約13 batch。
- 実行条件: T1でP4の誤PASS ≥1、またはspan意味違いの検出が不確実と判断された場合。代替案E(独立verifier)の有効性評価を含む。

### T3: 失敗系・停止系(mock、JPY0、API無し)
パターン(決定論の統合test): (a)API例外2回 (b)JSON不正2回 (c)不正gloss(括弧/算用数字/…)2回 (d)mapping欠落2回 (e)1回目失敗→2回目成功(採用、HR無し) (f)2回連続失敗→HR報告書の5必須項目+queue+Lock+run summary+最終stdout (g)batch内一部成立・一部失敗(item単位、成立分は採用) (h)HR通知の書込失敗(queue/Lock/report各々で例外)→fail-closed(stageを止める) (i)TTS不正通過のmock: FAILED itemのkp segmentに対しTTS関数が0 API callで拒否し、Gateが`EPISODE_BLOCKED_BY_AUDIO_VALIDATION`を返す (j)Family Z `stage_kp`が`FamilyZE2EStop` (k)flag OFF(従来どおり素通り=DISABLED) (l)HR解消後(gloss更新=新version)の再開でTTSが進む (m)別プロセスの`--stage tts`単独実行でも保留される(artifact永続化の確認)。
Regression: DESIGN_DRAFT_01 7節の一覧。

## 3. 費用見積り(単価の出典=`gloss_alignment_01/cost_01.json`の実測のみ)
| 項目 | 計算 | JPY |
|---|---|---|
| T1(10 batch、high) | 実測5 item/batch平均0.1137(範囲0.0694〜0.1422)×10 | 約1.14(0.69〜1.42) |
| 新スキーマの出力トークン増分(`added_word_mappings`) | **未確認**(T1で実測)。保守的余裕として+50%を見込む | 上限約2.1 |
| T2(条件付き、約13 batch) | 単価は**判定用promptで未測定**。align callと同単価と仮定(想定) | 約1.5(想定、未確認) |
| T3 / オフライン | API無し | 0 |
| 合計(T2含む上限) | | 約3.6〜4.1 → **予算上限JPY5を提案**(T2非実行ならJPY3) |
日次上限1,000円との関係: 最大でも約0.5%。承認済み予算(別途委任文で設定)内。量産コスト70円/記事セットへの影響=Trial自体はDEV実行で量産コストに加算されない。採用後の恒久単価増は`cost_01.json`の現行見積り(通常0.014〜0.08、最悪0.57、絶対最悪1.7円)+新スキーマ増分(T1で確定)で評価し、1〜2円級の恒久増になる場合はユーザー判断材料にする。
実行時間見込み: 実装5〜8h(委任_02)+O/T3テスト整備2〜3h+T1実行(独立10 batchを並列、API待ち中心、1回あたりの所要時間は**未計測**のため見込みは数分〜十数分程度と想定)。並列化: T1の10 batchは相互に独立のため同時実行。T2はT1出力依存のため直列(理由: 前工程出力依存)。

## 4. Trial Status分類基準(案。Opus/Fableレビューで確定)
- **REJECTED**(設計不採用・再設計): (a)機械検査で検出できるはずの欠落(span欠落)がPASSした(P4/P1) (b)FAILED itemのTTSが生成された、またはGateが通った(T3 i) (c)HR通知5条件のいずれかを欠いたまま下流が進んだ(T3 f/h) (d)対象外itemのgloss差分>0(O1) (e)実測費用が`cost_01.json`の絶対最悪見積り(1.7円/記事セット)を上回る見込み
- **VALIDATED**(Trial範囲で有効。Production採用ではない): O1差分0、O3/T3全件PASS、T1でP1/P4の最終不整合0(目視+機械)、P2/P3の書換・誤FAIL 0件(0/20。n小のため95%上限約14%を併記)、機械検査FAIL内訳に不整合なし
- **USER_DECISION_REQUIRED**: (a)Production採用そのもの(常に。Q1を再提示) (b)P2/P3で書換が1〜2/20件(誤NG寄りの許容度判断) (c)few-shotの偏りが疑われる (d)案B/Eの採否 (e)新スキーマで恒久増が1円級を超える (f)Family Xのitem保留/Zのstage停止の使い分け
- いずれの結果も`APPROVED_FOR_PRODUCTION`を意味しない。人間ユーザーの承認を経るまで、既存config既定値・量産経路を変更しない。
