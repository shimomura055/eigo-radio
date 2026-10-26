# LOOP_LOG_01: 原因究明→設計→検証の自律ループ記録

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_01 / 2026-10-26。終了条件=「各パターンで救済可能な候補が既存Gateを通過し、区分3の理由が品質・安全根拠で書けた」。
保存物: `rescue_eval_02〜07.json`(各ループの出力。`_01`は初版実行でループ1内に上書きされたため保存なし)、`judge_01〜08.json`(LLM評価。06〜08が最終プロンプト)、`selection_probe_01.json`・`have_probe_01.json`・`irregular_gap_01.json`(実データでの副作用確認)、`final_table_01.json`。判定は同じ入力で再現する(決定論部分)。
LLM評価: 8回、gpt-6-luna(最新世代の推奨系=repo承認済みSUPPORT_MODEL)、合計約2.14円(上限30円のGuardrail内)、各回前に`tools/stop_scope_check_01.py`(rc=0)。

| ループ | 入力→結果 | 不合格の原因(観測) | 設計/実装の変更 |
|---|---|---|---|
| **1** 初版を11件+導入前29種へ適用 | 11件のうち規則是正で通る4、窓内再導出/revertで通る形が4、他は未救済 | (a)`can’t be helped`が慣用句例外で通らない: 見出しは`it can't be helped`のみで、主語を除いた核が一致しない。(b)A1の第1案が`wave a flag`/`his hands for the chains`(接尾部分列優先の順位)。(c)canonicalization段の助動詞除外(`have a big moment`=key側)は、キーではなく**表層displayを本文から逆引きしないと**選定段検査に掛けられない。(d)`were mocking me`の原形変種`be mocking me`が「通過」に見えたが、**displayの`were`が選定段で落ちる**ので誤り | (a)見出し「it/that+核」の核も一致扱い(`lexicon_cores`)。(b)動詞アンカー導入。(c)canon段理由は再アンカーでdisplayを復元してから検査。(d)displayの選定段precheck(`_legacy_form_reasons`)をpass判定に必須化 |
| **2** `rescue_eval_02/03`+LLM評価`judge_01/02`(11件+代替案) | A1:`wave a flag`=意味changed、`too soon to wave`=changed、`too soon to do`=reject(2回)、`too soon`=adopt | 決定論は通る案でも、**比喩の核が目的語側にある動詞句を目的語抜きで残す/演算子を落とす**と意味が変わる。決定論の検査だけでは足りない | (i)順位を「演算子語を保持」優先に、(ii)「動詞が句末で目的語・補語を欠く」案を決定論で禁止、(iii)候補が複数のときはLLMを評価者に使う任意段(約0.1円)、(iv)**A2(`too soon to do`)を区分3推奨に**(検査はPASSでも意味保持/自然さの独立評価で基準未達)。judgeの入力不備も発見(Y事例に本文の文が無く「原文がない」とreject)→本文の文を必ず付与 |
| **3** `rescue_eval_04/05`+`judge_03` | `it can’t be helped`は完全文=原承認趣旨(完全文排除)に反する例外になってしまう。結果の最終形にGate再検証証跡が無い | 例外が「完全文」まで広がる設計 | (i)慣用句例外を**主語で始まらない核**に限定し、主語`it`を除く本文の連続部分列(`can’t be helped`)だけを通す、(ii)全最終形に既存validator(同一引数)+CMU+選定gate+重複の再検査証跡(`final_check`)を付与、(iii)助動詞を外した連続部分列の探索を追加 |
| **4** `rescue_eval_06/07`+`judge_04〜08`+probe | (1)judgeが**承認済み一般化**(`my→one's`)を「本文と異なる」とrejectした=評価プロンプトの不備、(2)同一入力でjudgeが揺れる(`not bear`:reject/adopt交互)、(3)**testで`hoped→hop`が受理される不具合**を発見(CVC語を重子音あり/なし両方許していた)、(4)`bound to the protein→bind to…`の誤受理を実データprobeで発見(OPEN-476=DEFERRED)、(5)`have`の役割判定が倒置/副詞挟み(`Had users been`/`have only put`/`had also faded`)を語彙と誤認 | 上記 | (1)プロンプトに承認済み変換を明記、(2)**3回の多数決**(2/3以上)で判定、(3)CMU音素の強勢で重子音化を決める(`hop→hopped`のみ、`visit→visited`)、(4)`bound`を表補完から除外、(5)役割判定に倒置・副詞・追加分詞表を追加(test 52 PASS) |

## 手法転換(同一方向の反復を避けた点)
- ループ2: 「決定論の検査を増やし続ける」方向をやめ、**独立LLM評価を品質ゲートに入れる**へ転換(決定論=生成+安全の歯止め、LLM=意味保持/自然さの評価)。
- ループ4: 単発のLLM評価をやめ**多数決**へ。評価の揺れ自体を観測値として残した(`too soon`=adopt系7回/7、`too soon to do`=reject 7回/8)。

## 終了判定
- 区分1(4件): 規則是正で通常フローを通る。実データ315種で単調性違反0・新規受理3変換(全て妥当)。
- 区分2(7件): 6件は救済形が既存Gate(同一引数)を通過し、LLM評価の多数決でadopt。1件(`redelivery fee`)は救済形が存在するが承認済みCMU規則の趣旨に反するため**非推奨**。
- 区分3(Human NG 3件+A2 `too soon to do`推奨)。11件内の救済不能は0。
- 残る不確実性(改善見込み低と判断して打ち切り): `too soon`(2語)の学習価値、`pulling free`/`eased open`の原形(POS情報が要る=不採用)、救済フロー全体のProduction上の挙動(実run未観測=DEV実証止まり)。
