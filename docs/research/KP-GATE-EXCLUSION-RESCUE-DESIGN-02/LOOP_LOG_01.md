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

---

# 委任_02 追記(2026-10-26、Opus条件A M1〜M4/R1〜R6の反映)

終了条件=「Opus指摘の誤受理が敵対的testで再現→是正後0件、実データ315種の単調性違反0、11件の区分が説明可能」。LLM: 1回(M4の見出し形再評価、3呼出、gpt-6-luna、0.224円、呼出前に`tools/stop_scope_check_01.py` rc=0=`stop_check_judge_headword.json`)。

| ループ | 入力→結果 | 不合格の原因(観測) | 設計/実装の変更 |
|---|---|---|---|
| **5** Opus指摘の再現(`old_vs_new_02.json`) | 旧実装(委任_01のHEAD)に敵対的セットを当てる: -ly名詞9件(increased supply/failed rally/organized rally/revised assembly/filled belly/ended folly/joined assembly/ruled monopoly/dug well)を誤受理、語彙have誤判定26件(has spread等の不変化分詞19・量化詞介在4・限定詞+名詞+分詞3)、名詞主語のことわざ5/5を慣用句例外が通す | M1: `is_manner_adverb`が語幹も品詞も見ず「-lyで終わる5文字超」だけ。M2: `IRR_PARTICIPLES`が表依存で、nxt2を見る倒置ルールは2語句と量化詞介在に効かない。M3: `lex_hit`が17,389見出しを全照会し、主語判定が代名詞のみ | M1: 語幹復元(CMU実在)+-ly名詞/動詞除外表+-ly形容詞表拡張+well/still除外。M2: 不変化分詞表補完・量化詞/副詞のskip・限定詞+名詞+分詞をaux。M3: レビュー済み閉表27件+sha256固定+fail-closed |
| **6** 再実証 | 敵対的85ケース=不一致0。実データ315種(312ペア)の単調性違反0、新規受理3変換(旧と同一)。have窓72件(旧71件+`have two hundred`)は全件レビューで語彙have。rescue_eval_08の11件decisionは07と同一。test 154 PASS | 途中で発見: (a)`reduced supply of→reduce supply of`はProduction現行で既に受理(「句末が不変化詞」の承認文言。パッチ由来ではない)→preexisting枠で固定 (b)ASCII`beggars can't be choosers`は現行Gateが通す(縮約形のすり抜け=R5。パッチ由来ではない)→preexisting枠 (c)`hundred`が`-ed`で分詞扱い(保守側の誤aux)→`_NOT_PARTICIPLE_ED` (d)敵対的セット側の誤り(`lit`は曖昧不規則として正当)→期待値を修正 | R3(同形異義語の除外)・R4(演算子表+HR旗)・R5(縮約形測定)を実装 |
| **7** M4 見出し形再評価 | A2 `too soon to do`: 前回枠組みreject 3/3 → 見出し形枠組みadopt 3/3。陰性対照`soon to do`はreject 3/3 | 前回のreject根拠(LLM評価)は枠組みに依存する | A2を区分3推奨→区分2(非推奨・AI意見付き)へ。評価の限界(生成側と同系統・ばらつきのみ測定)を開示。非推奨の根拠を評価から承認済み規則との関係へ置き換え |

## 手法転換(委任_02)
- 委任_01は「実データ315種で誤受理0」を安全の根拠にしていたが、実データに無い形(-ly名詞・不変化分詞)は検証されていなかった。**実データ+敵対的セット**(承認済み不変条件を破る形を設計側から生成する)へ検証方式を転換し、旧実装を同じ敵対セットに当てて「指摘が再現すること」「是正で消えること」の両方を機械で固定した。
- 「LLM評価でreject」を区分判断の根拠にする方式をやめ、評価の枠組み依存を開示した上で、根拠を承認済み規則との関係に置き換えた。

## 終了判定
- M1〜M4/R1〜R6は全件実装・敵対的test固定。Production非配線。
- 残る不確実性(改善見込み低と判断して打ち切り): 除外表が閉表である限界(品詞タガーなしでは未収載の-ly名詞を理論上防げない)、`has`+表外の不規則分詞、A2を採るかの品質判断(ユーザー)、Wiktionary見出し27件のライセンス(ユーザー/法務判断)。
