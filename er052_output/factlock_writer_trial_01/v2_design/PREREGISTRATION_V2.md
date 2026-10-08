# PREREGISTRATION_V2: Fact Lock v2 Trial 事前登録案(委任_04用。FACTLOCK-WRITER-REDESIGN-TRIAL-01、2026-10-08)

位置づけ: **案**。Opus条件Aレビューとユーザー/Fableの承認前は実行しない。Trial専用(Production経路ではない)。`APPROVED_FOR_PRODUCTION`なし。本書は測定の事前宣言であり、**しきい値は置かない(数値化のみ・有意性は主張しない)**。

## 1. 問い

v1 Fact Lockで落ちた面白さ(pairwise 実質9対35)を、事実固定(v1の照合指標)を悪化させずに現行版(6×現行)と同等以上に戻せるか。案A(Revise規則の調整)と案B(Writer prompt構成の見直し・制約最小化)で、それぞれ何がどれだけ動くかを数値化する。

## 2. 開始条件

1. 委任_02bの採点完了(`er052_output/factlock_writer_trial_01/RESULT.md`の存在。**存在確認のみ**: 本委任作成時点でファイルは存在するが内容は読んでいない。Fableが内容の完了性を確認する)。
2. DESIGN_02のOpus条件Aレビューが済み、Fableが照合のうえ次工程へ進めると判断(Opusレビュー自体はユーザー承認Gateではない)。
3. 共通修正Tを入れるか否かのFable判断(DESIGN_02 §0-2)。
4. 費用上限(¥100)の確認(T-3定型文: 予算ガードレール=上限¥100、累計がこれを超えそうなら停止して報告)。
5. 並行する委任(PRODUCTION-MODEL-ROUTING-GPT6-WIRING-01のProduction配線)がharness・モデル共通ファイルを変更していないことの確認(gpt-6-luna構成の同一性)。

## 3. セル(2アーム×6 brief×1反復=12本)

| アーム | 内容 | 本数 |
|---|---|---|
| 6×案A(`factlock_v2a`) | `blocks_v2.json` A.R0 / A.R1_R2 | 6 |
| 6×案B(`factlock_v2b`) | `blocks_v2.json` B.R0 / B.R1 / B.R2 | 6 |

brief(各アーム同一): meta b2・meta b3・hormuz b1・hormuz b4・space_weapons b1・space_weapons b3。反復=r1の1回。
**比較対象は既存の同brief・同r1**: 6×現行(`er052_output/all6_writer_redesign_necessity_01/runs/<slug>/control/b<i>__all6__r1/`)と6×Fact Lock v1(`er052_output/factlock_writer_trial_01/runs/<slug>/control/b<i>__factlock__r1/`)。確認済み【確認】: この12ディレクトリすべてに`ja_writer/revision2.md`が存在する(12/12)。
モデル・B3 brief・JA Fact Check(R0直後・R2直後、must-fix1回・STOP)・EN phase2・Checker構成は進行中Trialおよびv1と同一(v1の`DESIGN_01.md` §0)。briefにはv1と同じ注記版(`briefs/<slug>/<b>/selected_brief_factlock.md`と`core_numbers.json`)を使う。
STOP/失敗は欠測として母数に残し、STOP数も指標に含める(v1の`SUMMARY_FL`と同様)。

## 4. 指標(すべて数値化のみ。しきい値なし)

指標のprovenance(v1と同じ定義・同じ道具を再利用し、新しい定義を作らない):

| 指標 | 内容 | 定義・道具(再利用元) |
|---|---|---|
| M1 面白さpairwise(主指標) | v2A対6×現行、v2B対6×現行(各6対×順序入替2=12判定/アーム)。補助: v2A/v2B対v1(各12判定)、v2A対v2B(12判定) | `tools/eval_fl.py` の`pairwise()`方式(judge=gpt-6-luna、`PW_INSTR`同一、JA R2比較)。**事前宣言: 片方の本文が存在しない対は集計から除外し、除外数を併記する**(v1で4判定が不戦勝だった教訓)。位置バイアス(A/B選択率)を併記 |
| M2 照合(i)文×タグ | 不整合率、判定不能率、unknown_tags、主張別unsupported件数 | v1の`factlock_check_r{0,1,2}.json`と同じ手順(照合側は6-luna自己判定) |
| M3 照合(ii)タグなし文の5分類 | neutral/untagged_brief_fact/hedged_speculation/background_general/new_specific_claim | 同上 |
| M4 数値(iii) | トークン数、match、hedge_changed、not_core、core_used_without_tag | 同上(決定論) |
| M5 タグ除去後残存 | residual_brackets_after_strip、broad_only_tags_removed | 同上(0維持が期待) |
| M6 運用指標 | JA Fact Check must-fix発動、最終非COMPLIANT、STOP/失敗、EN deviation再生成発動、費用/本、所要時間/本 | v1の`SUMMARY_FL §1`と同じ集計 |
| M7 盲検rubric(重大/軽微) | 同一rubric・同一評価者(gpt-5.6-luna、gpt-6-luna)で12本を再採点 | v1の`eval_fl.py make_blind/judge`が再利用可能であることを前提(ブラインド化パックに12本を追加)。**再採点できない場合はM7を欠測とする** |
| M8 文体の機械指標(診断の追跡用) | です・ます文割合、アラビア数字/本、異なり比喩語/本、4種以上の記事数、推量・仮定語/本、問い/本、字数/本 | `DIAGNOSIS_01.md` (b)(c)(g)と同一の定義(タグ除去後のR0/R1/R2)。LLM判定を介さない決定論指標 |

基準値(v1、比較のために事前に記録)【確認: FACTLOCK_CHECK_SUMMARY.md】: 不整合率 R0 6.7%/R1 7.3%/R2 6.9%、数値トークン不一致 R2で5(うちnot_core 4)、残存タグ0、タグなし文のnew_specific_claim R0 7/R1 4/R2 4。diag基準【確認: DIAGNOSIS_01】: です・ます文割合 R2 FL 0.26対現行 0.50、異なり比喩語4種以上 FL 17/24対現行 11/22。

## 5. 比較の読み方(事前宣言)

- 判定ルールは置かない。各アームについて、M1(対6×現行の勝敗とA/B位置バイアス)、M2〜M5(v1基準との差)、M6(STOP/再生成)、M8(診断指標の変化)を**並べて報告**し、「事実固定指標が悪化したか」「面白さの勝敗が動いたか」を数字で示す。
- 1アーム6本・1反復のため、差の原因帰属(どの規則が効いたか)は主張しない。案Aと案Bは複数要素が同時に違う。
- 外れ値(1本が指標を大きく動かす場合)は、run別の値も表で併記する(v1のb3 r2のように)。
- Production採用は人間ユーザーだけが承認する。Trial結果(VALIDATED等)をPRODUCTION仕様と読み替えない。

## 6. 費用見積(T-3)と時間

| 項目 | 見積 | 根拠 |
|---|---|---|
| 生成12本 | ≈¥60 | v1実測 4.94円/本(Writer系+Checker+照合を含む、`SUMMARY_FL §1`)× 12 |
| pairwise 約60判定 | ≈¥1〜2 | v1実測 48判定=入力64.5k+出力14.0kトークン(`raw_usage_log_pairwise.jsonl`)。60判定でも同規模。円換算は未計算 |
| 盲検rubric 12本(M7) | ≈¥5〜10 | v1実測 72本=入力599k+出力245kトークン(`raw_usage_log_judge.jsonl`)。12本は1/6規模。円換算は未計算(推定) |
| 余裕 | | |
| **合計** | **≈¥80** | **上限¥100(予算ガードレール)。累計がこれを超えそうなら停止して報告** |

時間見込み(委任_04): harness段別ブロック対応と単体テスト≈30分/生成12本(v1は24本を並列実行、所要≈410秒/本)≈60分/照合・pairwise・M8集計≈30分/報告≈15分。合計≈2.5時間。生成はアーム別・brief別に並列可能(条件同一性を保てる範囲で)。

## 7. 実行時の禁止/注意

- v1のrunsを上書きしない(別ディレクトリ`factlock_v2`相当に出力)。
- Production経路(`er019_family_x_ja_writer_o_r1_r2_01.py`本体)を編集しない。v1と同様にモジュール属性の一時置換(終了時に復元)の方式を使う。
- must-fix再生成・STOP・EN deviationの既存安全装置を無効化しない。
- 有料APIの支出は上限¥100内。超える場合はFableに報告。
