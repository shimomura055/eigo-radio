## 管理ID

KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_02(Opusレビュー(条件A、変更部)のM1〜M4/R1〜R6をDEV設計・実装へ反映し再実証。Production非配線。到達=COMPLETED_PENDING_FABLE_ACCEPTANCE)。並行Agent: FZ Phase 2 evidence(Z run)、Y男性7Voice Trial、Chunk Opusレビュー(read-only)。本委任の所有=`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/**`、`er123_kp_rescue_dev_01.py`(+test)、`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_{DELEGATION_02,OPUS_REQUEST_02}*`、`docs/pm/RESULT_PACKET_KPRS4.md`。KP Production code(`er105_*`、`er003_key_words_*`、`er119_*`、`er003_v1_n3_01_scaffold_generate.py`)は編集禁止。SSOT・ACTIVE_TASKは編集しない。

## 性質/到達上限Status/禁止事項

- 性質: 設計改善+DEV再実証(ユーザー原文「不十分ならユーザーへ未完成案を転送せず、委任範囲内で設計を改善すること」)。
- 禁止: Production変更禁止/AI島HR候補の確定禁止(`status`のみ)/Git禁止操作(`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・`reset --hard`・`checkout -f`・`git checkout -- <file>`)。
- 費用: 原則API 0。例外=A2 `too soon to do`を「学習者向け辞書の見出し形」として再評価するLLM判定のみ(Opus M4の開示要件。最新世代推奨系モデル、使用モデル名・最新か・理由を記録、3回多数決、見積≤5円)。「上限¥15(Guardrail)。到達・接近時は、承認済みscope内/原因把握済み/異常retryでない/残作業明確/追加費用が合理的な範囲/QCD上の便益が明らか、であれば超過を記録して継続する。暴走疑い時(想定外の大量API/Web Search発火・同じ失敗の無意味なretry loop・費用増加の原因が説明できない・scope外処理の開始・残費用の見通しが立たない・明らかにQCD上不合理な追加処理)のみSTOPし、原因・既使用額・想定追加額・残作業を報告する。」呼出前に`py tools/stop_scope_check_01.py`。
- Opus独立技術レビューGate: 実施済み(本委任は反映)。Fable照合: Opus所見は設計の穴の是正であり既存ユーザー承認を変えない→**M1〜M4/R1〜R6を全件採用**。11件の区分はOpus意見どおり(A2を区分2・非推奨へ)。
- 修正範囲(11-8): 区分1=承認文の水準へGateを戻す是正(M1/M2で誤受理の抜けを塞いだうえで)、区分2=HR経路限定の救済フロー・慣用句閉表・A1短縮・再アンカー・A2(非推奨)。
- 時間見込み: 2〜2.5時間。費用/日次: 当日(JST 2026-10-26)既使用JPY約216+進行中(Y Trial Cap 250・Z Phase 2 Cap 200)/本委任JPY0〜5/承認区分: A。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2: TTSなし。
T-3(2026-09-26、`PM-BUDGET-CAP-GUARDRAIL-POLICY-01`): 費用上限[Cap]は「暴走防止のためのGuardrail」であり、Cap到達=自動STOPではない。上記定型文に従う。

委任文保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index 644 --out docs\pm\delegation_log\2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_DELEGATION_02.md`(先頭が「## 管理ID」+「KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_02」でなければ640〜655を順に試す)。Opus依頼文(prompt先頭「## 管理ID\nKP-GATE-EXCLUSION-RESCUE-DESIGN-02 Opus独立技術レビュー」、index 642付近)も`..._OPUS_REQUEST_02.md`へ保存。check実行は委任_02分。

## ユーザー指示(原文)

`docs/pm/delegation_log/2026-10-26_KP-GATE-EXCLUSION-RESCUE-DESIGN-02_USER.md`(保存済み)。要点: 「誤った原形を作るリスクには必要十分な検査を設ける」「区分3: 単にコードで対応が難しいという理由だけで区分3にしないこと」「学習価値の最終判断はユーザーが行う」。

## Opusレビュー原文(逐語。`docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/OPUS_REVIEW_02.md`へ一字も変えず保存。先頭に`# OPUS_REVIEW_02(条件A・変更部、2026-10-26、read-only、JPY0。以下Opus所見の逐語)`の1行を付ける)

## KP-GATE-EXCLUSION-RESCUE-DESIGN-02 Opus独立技術レビュー(条件A、read-only、JPY0)

前回レビュー(M1〜M6/R1〜R4)で決着した論点は扱っていない。読んだもの: OPUS_REVIEW_REQUEST_02、DESIGN_01、PATTERN_DESIGN_01、RESCUE_TABLE_01(いずれも全文)、er123:58-626、er105:200-229と560-700、er003_key_words_min_unit:240-289、er003_key_words_canonicalization:576-632、OPUS_REVIEW_COND_A_01:100-129、CURRENT_SPEC:1990-2003、OPEN_ITEMS:328。CASE_ANALYSIS/LOOP_LOGと実測json・testファイルは読んでいない(判断に必要な事実は設計書と実装で足りた)。

### 結論(先に)
- **Q1(b)**: 区分1でよい。ただし**M1を直すことが条件**。
- **Q2(b)**: 区分1でよい(fulltext経路に限る)。OPEN-152は「解消」ではなく「fulltext経路だけ部分的に解消、A/B/Cは`USER_DECISION_REQUIRED`のまま」と記録する。

---

### Q1 副詞前の原形化 — 要修正(M1)
- **(a) 元の目的を損なう抜けがある**: `is_manner_adverb`(er123:334-336)は「-lyで終わり5文字以上で、LY_ADJ表に無い語」を副詞とみなす。このため -ly で終わる名詞(`supply/reply/rally/assembly/jelly/belly/bully/folly/monopoly/anomaly/tally`等)も副詞扱いになる。
  - 句末、または直後が前置詞のとき、`_adverb_tail_ok`(:339-344)も通る。結果として `increased supply→increase supply`、`failed rally→fail rally`、`reduced supply of→reduce supply of` が受理される。
  - これはまさに`heated debate`型(形容詞化した分詞+名詞)で、er105:575の「V+名詞は原形化しない」という不変条件も破る。
  - 三重検査(LLM提案語・CMU実在・前方活用一致)は語形の正しさしか見ておらず、品詞の誤りは防げない。実データ315種に該当例が無かっただけである。
- **(b) 境界判定**: P-04原文(OPUS_REVIEW_COND_A_01:121)とCURRENT_SPEC:1997の承認済み条件は「先頭またはto直後」という位置だけ。直後語の条件(er105:570-572、:662)は実装時の追加である。
  - ただしP-04の目的(`heated debate`を通さない)は位置条件だけでは達成できない(`heated`は先頭語)。guardはその目的を満たすための実装と読める。
  - したがって「目的を脅かさない範囲だけguardを承認文の水準へ戻す」のは区分1と言える。その成立条件は「目的の失敗類型を再導入しないこと」で、現状はM1によりこれを満たしていない。
- **(c) 閉表**: -ly形容詞(`timely/scholarly/cowardly/leisurely/manly/hourly/nightly/sickly/burly/unruly`等)も漏れているが、後続名詞がある形はtail条件で止まるので実害は小さい。主なリスクは上記の -ly名詞。

### Q2 語彙have(lexical have)の役割判定 — 要修正(M2)。区分1は妥当
- **(c) dead pathの主張は正しい**: 選定段のer105:219と、正規化後のkey検査kc:627が、have/has/hadを含む句を必ず拒否する。そのためer105:592の`has/had/having→have`は受理結果を一度も生まない。
- **(b) 区分**: P-04(3)はユーザー承認済み(2026-10-22、OPEN-152より新しい)で、語彙haveが通ることを前提にしている。よってfulltext経路に限れば承認済み意図への準拠として区分1。
  - OPEN-152(OPEN_ITEMS:328)の対象は共有validatorとA/B/C。本設計はA/B/Cを変えないので、DESIGN_01:121の「区分1-1はOPEN-152の解」は言い過ぎ(R1)。
- **(a) 網羅の抜け**: 次の形が「語彙動詞」と誤判定される。区分1は救済旗もHRも経ない通常フロー(HRを経ない経路を含む)で効くため、配線前に直す必要がある。
  1. **形が変わらない不規則動詞などの過去分詞が表に無い**(er123:99-104): `has spread/quit/cast/cost/burst/shed/split/upset/bet/forecast/broadcast/bid/fit/rid/wed`、`dwelt/leapt/wrung/strode/stunk`。2語の句は nxt2=None になり、倒置ルール(:293)にも掛からない。
  2. **量化詞が助動詞と分詞の間に入る形**: `have all gone`、`have both agreed`、`has more than doubled`。nxt が_LEXICAL_STARTに含まれるため、:293の判定が効かない。
  3. **限定詞+名詞+過去分詞**: `had the board known`(倒置)と`had the house painted`(使役)は形が同じで区別できない。「迷えばaux」の原則に従い、auxへ倒す。

### Q3 語数超過の救済 — A1は採用可(R4)、A2の区分は要修正(M4)
- **(a) 歯止め**: 演算子語の表に`little/few`(a little / little で意味が反転)、`unless/except/rather/instead/fail`が無い(er123:447-448)。
  - `too soon to wave a flag→too soon` は「時期尚早」という核は保つが意味は狭まり、学習価値は低い。HRには「意味縮小・低価値の可能性」の旗と元句・本文の文を併記して出せば足りる。
  - 「機能語だけを禁止」という規則は質を担保しないので、低価値かどうかの最終判断はHRに置くのが正しい。
- **(b) A2 `too soon to do`**: ユーザー自身が出した例であり、却下の根拠はLLM評価(自然な英文として読ませた枠組み)にある。`too ~ to do`は学習者向け辞書の見出し形として一般的で、見出し語として評価させれば判定が変わる可能性がある。AIが区分3として閉じるのは、品質基準をAIが決めることになる。**区分2(非推奨の意見付き)としてユーザーに出すべき**(M4)。
- **(c) LLMを評価者に使う設計**: 決定論Gateが通したものを却下するだけ(単調)なら矛盾しない。ただしProductionで「任意」として残すと決定論で閉じない(PATTERN_DESIGN_01:16、:30)。R2参照。

### Q4 トリガー拡張・その他の新規救済
- **(a) 本文再アンカー**: 問題なし。既存の`find_inflection_window`を逆向きに使うだけで、受理基準は既存validatorのまま。窓の一意性は小文字化した表層形で判定し、複数の異なる表層形があれば救済しない(er123:600-617)。
  - 同じ表層形が複数文にある場合は、既存の選定gateがfirst_of_Nとして扱うので問題ない。
  - 軽微: 窓が句読点(カンマ等)をまたげる。
- **(b) 慣用句例外 — 要修正(M3)**: `contains_finite_aux_role_based_idiom`(er123:315-321)は、辞書に一致すれば助動詞検査を丸ごと外す。主語判定(_SUBJ_START)は代名詞しか見ていない。
  - そのため名詞主語のことわざ・完全文が通る: `beggars can't be choosers`、`boys will be boys`、`time is money`、`the die is cast`、`a leopard can't change its spots`。ER-003-P2G(完全文・節の排除)の原意図が崩れる。
  - 修正案: 例外は「句の先頭語が法助動詞/助動詞(主語の無い述部)」かつ「idioms由来(proverbsは除く)」に限る。根拠データは17,389件をその場で照会するのではなく、条件で絞った**レビュー済みの小さな閉表**にする。
- **(c) 外部辞書**: 閉表化すれば、実行時に外部データへ依存しない。版のsnapshotをsha256で固定し、出典表示ファイルを置く。repoが公開ならCC BY-SAの継承条件が掛かる点も確認条件に含める(M3に統合)。

### (a)〜(h)
- **(a)** ①副詞guard=区分1(M1が条件)。②語彙have=区分1(fulltext限定、OPEN-152は部分解消、M2が条件)。③`rang`補完=区分1でよい。ただし`bound`を外したのと同じ理由で、他の動詞の原形と同形の新規追加語(`lay→lie`、`wound→wind`、`ground→grind`、`bore→bear`)も除外する(R3)。
- **(b)** 必要十分ではない。品詞の誤り(-ly名詞)、形が変わらない分詞、同形異義の過去形が三重検査をすり抜ける。実データ315種に加えて、これらの敵対的なtestセットを必須にする(M1/M2/R3)。
- **(c)** DEVの検証用途としては可。ただし次の限界がある。
  - gpt-6-lunaは生成側と同系統で、自分の出力を好む偏りが入りうる。
  - 同じプロンプトで3回まわしても測れるのはばらつきだけで、偏りは測れない。
  - 最新モデル原則(PM_GOVERNANCE 25)に沿った記載(最新かどうか、違うなら理由)が必要(R6)。
  - Productionは既定で決定論のみとし、HRには決定論の第1案と代替案を並べる。評価者を残すなら、却下専用・費用を明示し、QA扱いにしないことを区分2の提案に明記する(R2)。
- **(d)** Q3(a)(b)参照。A1は区分2で可、A2は区分2(非推奨)へ移す。
- **(e)** Q4(b)(c)参照。
- **(f)** 問題なし(Q4(a))。
- **(g)** 「修正へ進む」(範囲内)の分類は妥当。ただし範囲は`n't`だけではない。
  - 縮約形`'re/'ll/'d/'ve/'m/'s`は曲線`’`でもASCII`'`でも今の判定をすり抜ける(er003_min_unit:264、:285-287)。`'s`は所有格と区別が要る。
  - Gateを締める修正なので、ASCIIの`can't be helped`(現在は通っている)が止まる。2-Bの判断と同時にユーザーへ出す(R5)。
- **(h)** 妥当。CURRENT_SPEC:2001が「語形変化救済による代替合格は禁止」と明記しているため、分解合格は仕様変更=区分2になり、非推奨の意見も筋が通る。

### 11件の区分への意見
1. `too soon to wave a flag`: 区分2で同意。低価値の旗を付けてHRへ。A2(`too soon to do`)は区分2(非推奨)へ移す。
2. `studied separately`: 区分1で同意。ただしM1が条件。
3. `had our eye on`: 区分1で同意(fulltext限定)。ただしM2が条件。
4. `rose above`: 区分2で同意。
5. `held out`: 区分2で同意。`hold out`単独では主な意味が「耐える」なので、多義の旗を付け、gloss再整合は本文での意味(差し出す)で行う(R4)。
6. `rang through`: 区分1で同意(R3を推奨)。
7. `it can’t be helped`: 区分2で同意。慣用句例外はM3の形に狭める。
8. `redelivery fee`: 区分2・非推奨で同意。
9. `can’t be helped`: 区分2で同意。(g)との関係を同時に提示する。
10. `have a say`: 区分1で同意。ただしM2が条件。
11. `catch their interest`: 区分2で同意(再アンカーという新しい工程のため)。

### M(必須修正)/ R(推奨)一覧
- **M1**: 副詞判定が -ly名詞を通し、`increased supply→increase supply`が受理される(er123:334-336、:392)。修正案は次の3点。
  - 語幹が形容詞かを確かめる(-ly/-ily/-ally/-ably を外した語幹がCMUに実在)。
  - -ly名詞の除外表を設ける。
  - 敵対的testを追加する。
- **M2**: `have_role`の誤判定3類型(形が変わらない分詞などの漏れ、間に入る量化詞、限定詞+名詞+分詞)をauxへ倒す(er123:99-104、:264-295)。
- **M3**: 慣用句例外を「先頭が法助動詞/助動詞で、idioms由来のレビュー済み閉表」に限り、ことわざ・名詞主語の完全文を通さない。snapshotのsha固定とライセンス表示を含む(er123:312-321)。
- **M4**: A2 `too soon to do`を区分3から区分2(非推奨の意見付き)へ移す。却下の根拠となったLLM評価の枠組み(自然な英文としての評価で、見出し語としての評価ではない)を開示する(DESIGN_01:106、PATTERN_DESIGN_01:35-39)。
- **R1**: OPEN-152は「fulltext経路で部分解消、A/B/Cは継続」と記録する(DESIGN_01:89、:121)。
- **R2**: Productionは既定で決定論のみとする。LLM評価者を残すなら、却下専用・費用明示・QA扱いにしないことを区分2の提案に明記する。
- **R3**: 過去形表の補完から、他の動詞の原形と同形の語(`lay/wound/ground/bore`)を除外し、testを追加する。
- **R4**: A1の演算子表に`little/few/unless/except/rather/instead/fail`を追加する。HR旗として「意味縮小・低価値の可能性」と「LLMが補った目的語を破棄・多義」(`hold out`)を付ける。
- **R5**: (g)の測定範囲を縮約形全般(`'re/'ll/'d/'ve/'m/'s`)に広げ、2-Bと同時に提示する。
- **R6**: LLM評価の限界(生成側と同系統、偏りは測れない)とモデル記載(PM_GOVERNANCE 25)を報告に明記する。ユーザー判断の材料は実例とHR表示にする。

### 要約
1. 骨格(区分1=Gateを承認文の水準へ戻す/区分2=HR経路限定の救済フロー)と、11件の区分の大半は妥当。
2. Q1・Q2を区分1とする判断は妥当だが、新しい判定に誤受理の抜けがある(-ly名詞、形が変わらない分詞、量化詞が間に入る形)。M1・M2の修正が前提で、区分1は通常フローに直接効くため配線前に必須。
3. 慣用句例外は名詞主語のことわざ・完全文を通してしまう。先頭が助動詞の句だけを対象にした閉表に狭める(M3)。
4. `too soon to do`はユーザー自身の例なので、AIが区分3で閉じず、区分2(非推奨の意見付き)として提示する(M4)。
5. 再アンカー、`redelivery fee`の判定、縮約形の不一致を「修正へ進む」とした分類は妥当。縮約形は`n't`以外にも広げて測定し、2-Bと同時に提示する。

(Opus原文ここまで)

## 実施事項

1. **M1**: `is_manner_adverb`を「語幹(−ly/−ily/−ally/−ably除去、綴り規則y→i等)がCMU実在の形容詞候補」+「−ly名詞除外表」に改め、敵対的test(`increased supply`/`failed rally`/`reduced supply of`/`heated debate`型が原形化されないこと、`studied separately`/`looked at separately`は通ること)を追加。実データ315種+敵対セットで再実行し単調性違反0を確認。
2. **M2**: `have_role`の3類型(不変化分詞表の補完[spread/quit/cast/cost/burst/shed/split/upset/bet/forecast/broadcast/bid/fit/rid/wed/dwelt/leapt/wrung/strode/stunk等]、量化詞介在[all/both/more than/each/just/already/also/never等]、限定詞+名詞+分詞=aux倒し)を「迷えばaux」で実装、敵対的test追加。`have_probe` 71窓を再実行し、誤って語彙判定されるものが0であることを確認。
3. **M3**: 慣用句例外を「先頭語が法助動詞/助動詞(主語なし述部)かつidioms由来(proverbs除外)のレビュー済み閉表」に限定。閉表は条件で機械抽出→件数・サンプルを`IDIOM_CLOSED_TABLE_01.md`に列挙(DEV用、snapshot sha256・出典・CC BY-SAの継承条件の確認事項を記載。ライセンス判断はユーザー判断材料)。ことわざ・名詞主語完全文(`beggars can't be choosers`等)が通らないtest。
4. **M4**: A2 `too soon to do`を区分2(非推奨の意見付き)へ。LLM再評価を「学習者向け辞書の見出し形として適切か」の枠組みで3回(最新推奨系モデル、≤5円)実施し、前回「自然な英文」枠組みの結果と並べて開示。AIの意見(非推奨)と根拠を分け、ユーザー判断材料にする。
5. **R1〜R6**: OPEN-152記述修正(部分解消)、Production既定=決定論のみ(LLM評価者はDEV検証限定・区分2提案に却下専用/費用明示/QA扱いしないと明記)、過去形表から`lay/wound/ground/bore`等を除外+test、A1演算子表に`little/few/unless/except/rather/instead/fail`追加+HR旗(意味縮小・低価値/目的語破棄・多義)、縮約形(`'re/'ll/'d/'ve/'m/'s`、曲線/ASCII)の影響測定(API 0、既存ログ)をOPEN-529追記文案に、R6の記載。
6. 再実証後に`RESCUE_TABLE_02.md`(11行+区分最終)、`DESIGN_02.md`(§0にOpus M/R対応表、区分1/2/3最終、Production配線時の差分案、HR表示案[元句・本文の文・旗]、追加コスト、期待救済率の再計算)、`LOOP_LOG_01.md`追記、`er123`+test更新(test全PASS)。
7. 保全確認(AI島status前後)、Production不変(`git status --short`)、secret grep。

## 事前指定Read一覧

1. `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/{DESIGN_01,PATTERN_DESIGN_01,RESCUE_TABLE_01,LOOP_LOG_01}.md`、`er123_kp_rescue_dev_01.py`(自作、全文可)、`er123_kp_rescue_dev_01_test_01.py`。
2. `er105_kp_fulltext_selector_01.py` :560-700、`er003_key_words_min_unit.py` :240-290(読取)。
3. `er023_output/key_phrase_db_trial_01/db/wiktionary/*.json`(閉表抽出元、構造把握のみ)、`wiktionary_ingest_log.md`。
4. `OPEN_ITEMS.md` Grep `OPEN-152|OPEN-529`。

## 実行コマンド全文

- DEV再実証: `py er123_kp_rescue_dev_01.py --inventory docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-01\inventory_01.json --out docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\rescue_eval_08.json --md docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\RESCUE_TABLE_02.md`(socket遮断付き)。
- 実データ315種+敵対セット: `py er123_kp_rescue_dev_01.py --monotonicity --adversarial docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\adversarial_01.json --out …\monotonicity_02.json`。
- test(遮断下): `$env:PYTHONPATH="netblock_harness_01"; py -m pytest er123_kp_rescue_dev_01_test_01.py -q`。
- LLM再評価(M4、1回のみ): `py tools\stop_scope_check_01.py`→`.venv\Scripts\python.exe er123_kp_rescue_dev_01.py --judge-headword docs\research\KP-GATE-EXCLUSION-RESCUE-DESIGN-02\a2_headword_cases.json --budget-jpy 15 --out …\judge_headword_01.json`。
- 保全: `py er119_kp_human_review_cli_01.py status --run er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_ai_01`。
- Production不変: `git status --short -- er105_kp_fulltext_selector_01.py er003_key_words_canonicalization.py er003_key_words_min_unit.py er119_kp_candidates_01.py er119_kp_human_review_01.py er003_v1_n3_01_scaffold_generate.py`。
- secret grep: `git diff --cached | findstr /R /C:"sk-[A-Za-z0-9]" /C:"AIza[A-Za-z0-9_-]" /C:"BEGIN PRIVATE KEY"`。

## SSOT追記文

文案のみ(RESULT_PACKETへ): OPEN-529更新(DESIGN-02完了・区分1/2/3最終・縮約形不具合候補・Opus M/R反映)、OPEN-152追記(fulltext経路で部分解消予定、A/B/C継続)、DECISION_LOG(Fable受入後)、OPUS台帳OF-KPRS2-M1〜M4/R1〜R6文案。

## Git(明示add対象・コミットメッセージ・trailer)

- SSOT編集権: なし。
- 明示add: `docs/research/KP-GATE-EXCLUSION-RESCUE-DESIGN-02/**`(新規・更新分)、`er123_kp_rescue_dev_01.py`、test、delegation_log 2ファイル+check.json。
- commit: `git commit --only <paths…> -m "KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_02: Opus M1〜M4/R1〜R6反映(−ly名詞・不変化分詞・量化詞介在の誤受理を遮断、慣用句例外を閉表化、A2を区分2非推奨へ)+DEV再実証(Production非配線、API <X>円)"`→`git push origin HEAD:main`(non-fast-forwardは`git fetch origin`→`git merge --no-edit origin/main`→再push。競合は両方残してSTOP)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_KPRS4.md`: (0)T-0 (1)結論(M/R反映状況表、11件の最終区分) (2)RESCUE_TABLE_02転記(11行) (3)敵対的test・単調性・have_probeの結果 (4)慣用句閉表の件数・サンプル・ライセンス確認事項 (5)A2見出し形再評価の結果と開示文 (6)区分2の判断材料(最終: 救済フロー本体/慣用句例外/A1短縮/A2一般化/CMU分解/辞書guard保留、各々修正例・メリット・リスク・代替・QCD・AI意見) (7)区分1のProduction適用差分案(M1/M2済み前提、HRを経ない経路にも効くことの明示、回帰test計画) (8)費用・モデル・最新性 (9)保全・不変 (10)commit/push・raw URL (11)一覧外Read (12)Fable向け懸念。最終行に要約10行以内。