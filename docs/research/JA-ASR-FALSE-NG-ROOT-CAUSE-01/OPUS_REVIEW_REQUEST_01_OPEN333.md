# Opus独立技術レビュー依頼(条件C: 重要変更のProduction採用提案前)— OPEN-333系 しわ↔すわ(N3-07)是正案 E3P
依頼元: Fable(JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_11成果)。レビュー対象はProduction適用**提案**であり、Production変更は未実施。ユーザー承認(APPROVED_FOR_PRODUCTION)はレビュー後もユーザーのみ。
読むもの(この順): `OPEN333_DESIGN_01.md` → `OPEN333_EVAL_01.md` → `open333_trace_01.out.txt` → `OPEN333_PREREGISTERED_01.md`(§5・§6の改訂経緯) → `proto_open333_fix_02.py`(E3P本体)/`proto_open333_fix_03.py`(E4)。Production読取: `er007_ja_asr_validator_01.py:242-326,366-383`、`er011_ja_asr_variant_layer_01.py:289-372`。

## 論点(絞る。各点で『同意/修正/反対』と根拠を)
1. **区分は『実装不具合』で妥当か**。根拠=Candidate E設計(er011:347-362「残っている差分span同士」)と、er007:366-380の承認時前提(「誤PASSのリスクを生まない」)に対し、`protected_check_ja`が数字opcodeに糊付けされた非数値差を`content_diffs`へ入れない(er007:258-261)ためEが未検査で通る、という因果(trace §1〜§4)。『母音違いを許す規則』ではないとする反証(同一対を糊付けなしにするとNG、すわ/そ/しば等も糊付け次第でPASS/NG)は十分か。仕様変更扱い(ユーザー承認要)にすべき観点はあるか。
2. **E3Pの設計は最小か**。数値entryのみに効く条件(`protected.number_mismatches`)、数字・漢数字run・桁区切りcommaを除去した全文の再diff、Productionと同じ2段+窓幅の説明検査、の3点。取りこぼし(漢数字の語内の使用を剥がすことで誤って許す/誤って止める型、アラインメント非依存の副作用)の懸念はあるか。E1Pでなくアラインメント非依存のE3Pを選ぶ判断は妥当か。
3. **助詞発音等価の免除(P-1)**。v1評価で月題の正常音声(`月の詩は八千九百本長`、助詞はをwaと読めば`しわ`と同音)が、現行Productionでは糊付け未検査のためたまたまPASSしていた。免除なしだとこれをNG化する(正常音声の誤NG)。免除は『助詞は→わ・へ→えのみ発音形』の読み一致(新規受理0、現行PASS維持)。(a)免除を入れる判断は品質ライン(承認済み水準)を変えないか=ユーザー承認不要と言えるか、(b)B-light v2(未採用)の規則を検査側で使うことの是非、(c)免除が非糊付けの`詩は`↔`しわ`NGとの不整合を固定化しないか。
4. **事前登録の健全性**: v1(E1/E2/E3)の結果を見て v2(P-1)を設計した履歴(準備書§5に開示)。母集団で糊付け残余を持つPASSが2件のみ(N3-07とMOON#1)の状況で、合成sweepによる補強で十分か。追加で見るべき反例クラス(桁区切り・小数・助数詞同居・全角など)。
5. **便乗PASS(E4、第2の漏れ)の扱い**。`remaining_diffs`がnon-cascadeのみで、cascade_eligible差分(entity_like/phonetic_uncertain)が他差分のE救済に便乗してPASSする(実データ4/23行。凍結負例の遮断は0)。実害証拠なし・正常音声へのCascade費用増(4/677)を理由に今回見送る判断は妥当か。別OPEN/別委任に切り出す方針でよいか。
6. **Production適用の方式**: 既定ONの承認済み不具合是正として`er011`のCandidate E分岐へ直接入れる(11-7の限定例外=未承認機能のflag隔離には当たらない)で良いか。構造化フィールド化(OPEN-333記載の「Candidate E経由判定はreason文字列一致でなく構造化フィールド」)を同時に行うべきか。適用後の監視(OPEN-517同様の正式run集計)の観点。

## 事実の固定(レビューで再確認可能)
- 母集団1,327件、Candidate E経由PASS 23件/PASS 710件。E3P: 変化=N3-07のみ(PASS→NG_EXCLUDED)、非PASS→PASS 0、正常NG化0、他行state/reason/label完全一致。sweep: 糊付け残余PASS 14件全て遮断、正例(`しわ`+超/長、`…円長です`)維持。
- 決定性: eval_01/02/03を各2回実行し出力が完全一致。API 0・費用0円・Production無変更(`git diff --stat`空)。
