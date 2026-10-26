# RESCUE_ANALYSIS_01: 既存の全除外例に対する救済案と机上再検査(API 0・2026-10-26)

机上再検査の方法: `tools/kp_exclusion_inventory_01.py --recheck rescue_candidates_01.json`(結果=`recheck_01.json`)。既存の決定論validator(`er003 validate_canonicalization_item(allow_inflection_normalization=True)`、`er105 validate_and_resolve`、`er108 CMU`、有限助動詞照合)を**変更せずそのまま**呼ぶ。LLM段(canonicalization QA・gloss再整合・Redundancy QA・Z限定SRC D1/人称整合)は未実行(API 0)なので「全Gate通過」ではなく「決定論Gate通過」。学習価値の優劣判断はしない(最終選択はHR)。

## 1. 区分別集計(救済率)

| 区分 | HR導入後 Gate除外11件(Human NG 3件を除く) | HR導入前の一意句29 |
|---|---|---|
| S1 承認済み規則内・機械的(API 0)で救済可 | 4(36%)=X `studied separately`/Z `rose above`・`held out`・`rang through` | 12(41%) |
| S2 新規則(ユーザー承認)があれば救済見込み | 3(27%)=X `too soon to wave a flag`・`had our eye on`/Y `have a say` | 2(7%) |
| 困難(救済しない) | 4(36%)=Y `it can't be helped`・`can't be helped`・`redelivery fee`・`catch their interest` | 11(38%) |
| 現行validatorで既に通る | 0 | 4(14%) |

注: S1の救済は「正規化できなかった候補を、表層形(または現行表で許される再導出形)で**残す**」ことであり、期待する原形そのものを得る訳ではない(原形化はS2のW2/W3)。HR導入前の数は同一記事の再実行による重複を一意句に畳んだもの。「救済率」=S1/Gate除外=HR導入後36%・導入前41%。S1+S2=HR導入後64%。

## 2. HR導入後の全除外例(11件)

| # | Family/run | 除外句 | 修正案 | 区分(機械/AI) | 修正後句 | 机上再検査 | 本文対応 | 重複 | 自然さ所見 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | X AI島 a2 | `too soon to wave a flag`(6語) | 部分列短縮(§3.1) | AI/HR判断 | §3.1参照 | §3.1参照 | 保持(部分列) | 相互に包含(1つだけ提示可) | 意味反転/未完リスクあり |
| 2 | X AI島 a2 | `studied separately` | §3.2。表層形revert | 機械 | `studied separately` | validator ok・CMU ok・2語・PASS(AI2-b) | 保持(無変更) | 無し | 過去分詞形のまま。原形でない旨の旗が必要 |
| 3 | X EV R2 b1b | `had our eye on` | lexical have検査の精緻化(新規則)。現行規則内では不可 | S2(検査精緻化) | `have our eye on`(未検査) | 現行Gateでは`have`で不通過 | 保持 | - | 自然(定型表現) |
| 4 | Z melos R3 b1b | `rose above` | 決定論再導出 | 機械 | `rise above` | validator ok・CMU ok(Z-rose) | 保持(spanの1対1置換) | - | 自然 |
| 5 | Z melos R3 b1b | `held out` | 決定論再導出 | 機械 | `hold out` | validator ok(Z-held) | 保持 | - | 自然。LLM案`hold out one's hands`は範囲拡張で不可 |
| 6 | Z melos R4 b1b | `rang through` | 表層形revert(原形`ring through`は`rang`が過去形専用表に無く不通過=閉表拡張W3が必要) | 機械(原形化はS2) | `rang through` | 表層は通過、`ring through`は不通過(Z-rang) | 保持 | - | 表層形のまま |
| 7 | Y 再配達 a2 | `it can't be helped` | `be helped`へ縮約 | AI/HR判断 | `be helped` | validator ok(Y-be-helped)だが `can't`除去でイディオム「仕方がない」を失う | 保持 | - | 意味喪失=困難 |
| 8 | Y 再配達 b1b | `can't be helped` | 同上 | 同上 | `be helped` | 同上 | - | - | 困難 |
| 9 | Y 再配達 a2 | `redelivery fee` | CMU必須Gate(代替合格禁止) | - | - | 不可 | - | - | 困難 |
| 10 | Y SNS b1b | `have a say` | lexical have精緻化(新規則) | S2 | `have a say` | 現行Gateでは不通過(Y-have-a-say、理由=有限助動詞) | 保持 | - | 自然 |
| 11 | Y SNS b1b | `catch their interest` | 本文に無い | - | - | 本文不一致 | 喪失 | - | 困難 |

他にHuman NG 3件(`put in place`・`off the hook`・`sentenced him to death`)は**救済対象外**(NG復活禁止、USER.md:97)。

## 3. AI島 2件の具体案(Gate通過可否と理由のみ記す。推奨候補の選定=学習価値判断はHR=ユーザー)

文脈: a2本文 "Even so, it is too soon to wave a flag and say, 'Play and get smarter—proof complete!'" / "These two results need to be studied separately."。現在のa2候補5件=`carry over`・`worth paying attention to`・`a useful card to play`・`take a detour`・`one step ahead`。以下の全案は現在の5件と包含/同一関係にない(`ft.phrase_key`+`_is_subseq_tokens`で確認)。ただし案どうしは相互に包含するので、**同一系統からHRへ出せるのは1案まで**(call2の重複規則と同じ)。

### 3.1 `too soon to wave a flag`(6語)

| 案 | 修正後句 | 語数 | 決定論Gate(選定gate+canon validator+CMU+助動詞) | 本文対応 | 現行規則内/新規則 | 所見(学習価値の評価はしない) |
|---|---|---|---|---|---|---|
| a | `soon to wave a flag` | 5 | PASS(AI1-a) | 保持(連続部分列) | 新規則(段階2c: 短縮提案) | **`too`を落とすと意味が反転**(「時期尚早」→「もうすぐ振る」)。機械的な左削りはこの理由で禁物 |
| b | `too soon to wave` | 4 | PASS(AI1-b) | 保持 | 同上 | 目的語が無く句が未完 |
| c | `wave a flag` | 3 | PASS(AI1-c) | 保持 | 同上 | 動詞句の核。「時期尚早」の含意は失うが意味は自立。本文では「勝利宣言する」意の比喩 |
| d | `to wave a flag` | 4 | PASS(AI1-d) | 保持 | 同上 | to不定詞句。cより情報は増えない |
| e | `too soon to` | 3 | PASS(AI1-e) | 保持 | 同上 | 内容語が無い枠のみ |
| f | `too soon to wave a` | 5 | PASS(AI1-f) | 保持 | 同上 | 末尾が冠詞で構造的に不適(機械フィルタで落とせる) |
| u | `too soon to do`(ユーザー例) | 4 | **FAIL**: 選定gate「本文に連続一致しない」、canon validator「Rule7: key('too soon to do')がdisplay/spanと不一致」(AI1-u) | **喪失**(本文に`do`は無く、`wave a flag`を`do`に置換=1対1置換ではなく語数も変わる) | **新規則が必要**(Rule7の閉集合「人称/参照語/所有格」に無い「動詞句スロットの一般化」。承認済み一般化の範囲を超える) | 文型としては成立するが目的語が空で、学習単位としての内容が薄い。本文に無い語の生成は承認済みRule7原則(`kc:620`「source_spanに存在しない別の辞書形を勝手に生成しない」)と衝突する |

決定論Gateはa〜fを区別できない。構造フィルタ(両端が機能語でない等)で落とせるのはe/fのみで、a〜dの選択は意味判断=AI(LLM)判断またはHR選択が必要。機械で「最も長い部分列」を取るとaになり意味が反転する、という実例である。

### 3.2 `studied separately`

| 案 | 修正後句 | 語数 | 決定論Gate | 本文対応 | 現行規則内/新規則 | 所見 |
|---|---|---|---|---|---|---|
| a | `study separately`(LLM案・ユーザー例) | 2 | **FAIL**(AI2-a)。理由=Rule7拒否。基本形化例外は適用されている(fulltext itemでvalidator到達)が、`er105:662 _guard_ok`が「直後が限定詞/代名詞/不変化詞/前置詞」を要求し、直後が副詞`separately`のため不通過 | 保持(1対1置換) | **新規則が必要**(W2: guardに副詞追加。`er105:575`は「V+名詞等は基本形化しない」設計) | 自然。what-if(`_Whatif(adverb_ly)`でguard拡張を仮定)では`study separately`が通る |
| b | `studied separately`(revert) | 2 | PASS(AI2-b) | 保持(無変更) | **現行規則内**(Rule7の「無変更」。新受理面なし) | 過去分詞形のまま。本文は受動`be studied separately`。HR表に「原形化できず表層形」の旗を要する |
| c | `be studied separately` | 3 | PASS(AI2-c) | 保持(連続部分列) | 新規則(段階2c 部分列) | 受動の見出し形(旧template「be+過去分詞」見出し形と整合)。語が増える |
| d | `separately` | 1 | PASS(AI2-d) | 保持 | 同上 | 副詞のみ。学習単位として最小 |
| e | `look at separately` | 3 | 選定gate FAIL(a2本文に無い=AI2-e)。canon validator単体は通る(AI2-f=b1b本文では`looked at separately→look at separately`がPASS) | a2では喪失 | - | b1b側の表現であり、a2へ持ち込むと本文対応を失う(別レベル本文の流用は不可) |

b1b側で`looked at separately→look at separately`がPASSしている事実(`kp_candidates.json` b1b candidates[2])と、a2の`studied separately`が不通過な事実は、**Gateが活用形の品詞環境(直後が前置詞か副詞か)で判定を分けている**ことの実例。

## 4. 補足: 救済可能性を左右する構造的所見

1. **LLM canonicalization出力の質に依存する除外が多い**: Z R3の`rose above`/`held out`はLLMがspan外へ拡張したため落ちたが、決定論の1対1再導出(`rise above`/`hold out`)なら承認済み規則内で通る。LLMを再呼出するより、既にある応答(`canonicalization_runtime_metadata.json`の`parsed`)を後処理で直す方が安く確実。
2. **既存の先例**: `postprocess_possessor_roles`(`er105:927`)は同じ位置(parse直後・validate前、`run_canonicalization_gate(postprocess=)`)で「revertのみ・validator通過を確認・通らなければ無変更」を既に行っており(UDR #173②承認済み)、救済の中核はこの型の拡張で足りる。
3. **S2にあたる4種**: (W1)guard限定詞の網羅(`no`/`each`等。X/Zで2句)、(W2)guardに副詞(`studied separately`)、(W3)過去形専用表の網羅(`rang`)、(2e)有限助動詞のlexical have区別(X1・Y1・X(HR導入前)1)、(2c)短縮提案(over-5)。いずれも「受理面の拡大」で、11-8上はユーザー判断(W1/W3は記述意図への是正とも読めるためFable判定、SPEC_CHECK_01 §2)。
4. **救済しないもの**: CMU(承認済み規則が代替合格を禁止)・本文不一致・modal/進行形auxを句の核とするもの・Human NG・重複/overflow。
