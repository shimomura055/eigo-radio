# DESIGN_02: Key Phrase Gate除外「救済」方式(Opus条件Aレビュー M1〜M4/R1〜R6 反映版)

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_02 / 2026-10-26 / 到達上限Status=`COMPLETED_PENDING_FABLE_ACCEPTANCE`→Fable受入後`USER_DECISION_REQUIRED`(区分2のみ提示)。
Production(`er105`/`er003_*`/`er119_*`/scaffold)は未変更・未配線(`git status --short`で6ファイルとも差分なし)。DEV=`er123_kp_rescue_dev_01.py`+test **154件PASS**(netblock harness下)。DESIGN_01の骨格(区分1=Gateを承認文の水準へ戻す是正 / 区分2=HR経路限定の救済フロー・慣用句例外 / 区分3)は維持し、Opusが指摘した誤受理の抜け(M1〜M3)と区分の誤り(M4)を是正した。Opus原文=`OPUS_REVIEW_02.md`(逐語)。

## 0. Opus M1〜M4 / R1〜R6 対応表(全件採用)

| ID | 指摘 | 実施内容 | 証跡 |
|---|---|---|---|
| **M1** | `is_manner_adverb`が-ly名詞(supply/rally…)を副詞扱いし`increased supply→increase supply`を受理 | (1)語幹復元(-ily→-y/-ally→-ic/-bly等→-ble/-lly→-l/-uly→-ue/それ以外-ly除去)がCMU実在であること (2)-ly名詞/動詞除外表`LY_NOUN_VERB`(supply/reply/rally/assembly/jelly/belly/bully/folly/monopoly/anomaly/tally/apply/comply/imply/multiply…)で語幹検査をすり抜ける語(reply→rep、supply→supple)も除外 (3)-ly形容詞表`LY_ADJ`を拡張(timely/scholarly/cowardly/leisurely/manly/hourly/nightly/sickly/burly/unruly…) (4)名詞用法のあるwell/stillを副詞表から除外 (5)敵対的test追加 | `adversarial_01.json`(conversions 22)・`old_vs_new_02.json`: **旧実装は9件を誤受理**(increased supply/failed rally/organized rally/revised assembly/filled belly/ended folly/joined assembly/ruled monopoly/dug well)→**新実装は0件**。`monotonicity_02.json`: 実データ315種(312ペア)で単調性違反0・新規受理は3変換(rang through/studied separately/thrown into it)のみで旧と同一 |
| **M2** | `have_role`の誤判定3類型 | (1)形が変わらない/不規則な過去分詞表`IRR_PARTICIPLES_EXTRA`(spread/quit/cast/cost/burst/shed/split/upset/bet/forecast/broadcast/bid/fit/rid/wed/dwelt/leapt/wrung/strode/stunk他)でnxt自身を分詞認識 (2)量化詞・副詞を読み飛ばして先が分詞/been/beingならaux(`_HAVE_SKIP`: all/both/each/more/than/just/already/never…) (3)限定詞(+形容詞)+名詞+過去分詞=aux(had the board known/had the house painted。「迷えばaux」) (4)`hundred`等-edで終わる非分詞語の誤aux化を防ぐ`_NOT_PARTICIPLE_ED` | `have_roles`40ケース。**旧実装は26件を誤判定(語彙have扱い) → 新実装は0件**(`old_vs_new_02.json`)。`have_probe_02.json`: 実本文のhave窓は72件(旧71件+`hundred`を分詞扱いしない補正で増えた1件`have two hundred`)。M2でaux側へ戻った窓は0。誤って語彙判定されるものを人手で全72件レビュー: 0。文脈つき再判定で助動詞構文の断片と出た窓が4件(`have a`/`have a package`[使役: have a package delivered]/`have its`/`have its own`[文中のcostを不規則分詞として保守側にaux判定])。窓単体では語彙haveとして自然 |
| **M3** | 慣用句例外が名詞主語のことわざ・完全文を通す | 例外を「(1)idioms由来 (2)先頭語が法助動詞/助動詞(縮約形含む) (3)5語以内 (4)レビュー済み」の**閉表27件**に限定。sha256固定・改ざん/欠落時は空表(fail-closed)。実行時に17,389見出しを照会しない | `IDIOM_CLOSED_TABLE_01.md`(採用27件・除外26件を全件列挙・出典sha・ライセンス確認事項)。idiom 15ケース: **旧は名詞主語5/5を通す → 新は0/5**。`could not bear`/`will be missed`/`you can’t be serious`も拒否のまま |
| **M4** | A2 `too soon to do`を区分3で閉じない | **区分2(非推奨・AI意見付き)**へ移動。LLM再評価を「学習者向け辞書の見出し形」の枠組みで実施し、前回「自然な英文」枠組みの結果と並べて開示(§4) | `judge_headword_01.json`(3回、gpt-6-luna、0.224円) |
| R1 | OPEN-152は「解消」でなく部分解消 | §8のOPEN文案を「fulltext経路だけ部分解消、A/B/Cは`USER_DECISION_REQUIRED`のまま」に修正。DESIGN_01の「区分1-1はOPEN-152の解」は撤回 | §8 |
| R2 | Productionは既定で決定論のみ | §3-2のとおり。LLM評価者はDEV検証限定。残す場合は却下専用・費用明示・QA扱いしない旨を区分2の提案に明記(§5 2-A) | §3-2/§5 |
| R3 | 過去形補完から同形異義語を除外 | `COMPLETION_EXCLUDE`に`lay/wound/ground/bore`を追加(`bound`は既存)。加えて「他動詞の原形と同形」を自動除外(`past in IRR`) | test `test_r3_past_table_completion_excludes_homographs`。補完後も`rang/sang/swam`は追加される |
| R4 | A1演算子表の拡張+HR旗 | `SCOPE_WORDS`に`little/few/unless/except/rather/instead/fail(s)(ed)(ing)`を追加。A1にHR旗「意味縮小の可能性」「低価値の可能性」「元句の中間部分」、M1窓内再導出の窓外tail破棄に旗「LLMが補った語を破棄(目的語の意味が失われる/多義の可能性)」を付与 | `rescue_eval_08.json`の`hr_flags`、test `test_r4_*` |
| R5 | 縮約形全般の測定 | `--contraction-probe`(API 0、X/Y/Z既存ログ381句): **縮約形を含む句29**。内訳=ASCII`'s`26(全件所有格。is/hasは0)・ASCII助動詞縮約1(`can't wait`=現行Gateを通過・採用)・曲線助動詞縮約2(`can’t be helped`/`it can’t be helped`=dropped)。トークン化は`can't`→1語(すり抜け)、`can’t`→`can`+`t`(拒否)、`they’re`→`they`+`re`・`I’ll`→`I`+`ll`(すり抜け)。§8に2-Bと同時提示の文案 | `contraction_probe_02.json` |
| R6 | LLM評価の限界とモデル記載 | §4・§7に明記(生成側と同系統・同一プロンプトの反復はばらつきのみで偏りは測れない・最新かどうか) | §4/§7 |

## 1. 結論(先に)

1. **Opus指摘は全件再現し、是正して再実証した**。旧実装は敵対的85ケースのうち、-ly名詞9件・語彙have誤判定26件・名詞主語のことわざ5件を誤って通していた。新実装は0件(`old_vs_new_02.json`)。実データ315種の単調性違反は0のまま。
2. **11件の区分は変わらない**: 区分1=4件(`studied separately`/`had our eye on`/`rang through`/`have a say`)、区分2・採否推奨=6件、区分2・非推奨=1件(`redelivery fee`)、Human NG 3件は区分3。**変更は、A2 `too soon to do`を区分3から区分2(非推奨)へ移した点のみ**。
3. 区分1は救済フロー・HRを経ない通常フローに直接効く(AUTO経路を含む)ため、Productionへ入れる前に、本DESIGNの敵対的test集(`adversarial_01.json`)を回帰testとして固定することが必須。
4. 追加費用はLLM評価0.224円のみ(M4の再評価)。Production適用時の追加APIは救済フローのgloss再整合(DESIGN_01 §7のとおり)のみで、区分1はAPI 0。

## 2. 全体フロー(DESIGN_01 §2から変更なし。差分のみ)
- 選定gate/正規化validatorの区分1是正は、M1(副詞の語幹検査+除外表)とM2(分詞表・量化詞介在・限定詞+名詞+分詞)を含む形に更新。
- H1の慣用句例外(D3)は、M3の閉表(先頭が助動詞)に限定。主語`it`を持つ完全文は、主語を除いた連続部分列(閉表の核)だけを通す(従来どおり)。

## 3. 実装設計(Production配線時の差分案。**今回は適用しない**)

### 3-1 区分1(規則是正。通常フロー。**HRを経ない経路にも効く**)
| # | 変更 | 場所(現行) | 内容(M1/M2/R3反映後) |
|---|---|---|---|
| 1 | 有限助動詞の役割判定 | `er105:213 _legacy_form_reasons`(fulltext専用)・`er003_key_words_canonicalization.py:627`(共有) | `have/has/had`のみ`have_role`。**共有側は`allow_inflection_normalization=True`のときだけ**新判定(A/B/C=27-7はバイト同一)。(a)形が変わらない過去分詞・不規則分詞の表を`IRR_PARTICIPLES`(+`IRR_PARTICIPLES_EXTRA`)で補完 (b)量化詞/副詞を介した分詞はaux(`_HAVE_SKIP`) (c)限定詞(+形容詞)+名詞+分詞はaux (d)迷えばaux。法助動詞・be系は不変 |
| 2 | guardへ量化詞限定詞 | `er105 _GUARD_DET` | `no/each/every/all/both/another/either/neither/several/few/many/much/enough`を追加 |
| 3 | guardへ副詞後続 | `er105 _guard_ok`/`_token_pair_ok` | `is_manner_adverb`(M1: 語幹CMU実在+-ly名詞/動詞/形容詞の除外表+`well/still`除外)かつ句末/直後が前置詞・不変化詞・限定詞・接続詞。この追加経路にだけ前方活用生成一致(強勢つきCVC重子音)を課す |
| 4 | 過去形/分詞の閉表補完 | `er105 _PAST_ONLY_IRREGULAR`・`_AMBIGUOUS_IRREGULAR` | 過去形専用・曖昧過去形・分詞を補完。**除外**: `bound`(OPEN-476=DEFERRED)・`lay/wound/ground/bore`(R3)・他動詞の原形と同形の語 |

回帰test(Production適用時の必須): (1)`adversarial_01.json`(conversions 22・have_roles 40・past 8・idiom 15)を固定。`reduced supply of→reduce supply of`は**Production現行でも受理される既存挙動**(承認文「句末が不変化詞」に該当、パッチ前後で不変)として別枠で固定(§8に記録)。(2)実選定句の単調性・新規受理リスト。(3)A/B/Cバイト同一。(4)HRを経ない経路(`scaffold:883-888`・`er062:1364-1373`)の出力が、flag未設定で不変。

**残るリスク(正直な開示)**: M1の除外表は閉表であり、未収載の-ly名詞でかつ語幹がCMUに実在する語は理論上すり抜ける(語幹検査は品詞を見ない)。緩和=副詞が動詞位置(先頭/to直後)の直後かつ句末/前置詞・限定詞の前にある場合に限る(後続名詞がある形はtail条件で止まる)、実データ315種に該当0、敵対的testで既知の-ly名詞を網羅。品詞タガーを使わない限りゼロにはできない。M2も同様に、表に無い不変化分詞はauxに倒れず語彙判定されうる(`has`+表外の不規則分詞)。この場合の害は「完了形を通す」方向で、Gateを緩める。配線前に、表の追加分(`IRR_PARTICIPLES_EXTRA`)を人手で再レビューする。

### 3-2 区分2(救済フロー。HR経路限定・既定OFF・単一flag読取関数)
DESIGN_01 §3-2のとおり。**追加・修正**:
- **Productionは既定で決定論のみ**(R2)。A1短縮は決定論の第1案+代替案を並べてHRへ出す。LLM評価者を残すかはユーザー判断(区分2 2-A、却下専用・約0.05円/呼出・QA扱いにしない)。
- HR表示案(元句・本文の文・旗)は§6。
- 慣用句例外は`idiom_closed_table_01.json`(27件、sha256固定)。出典表示・ライセンス確認が前提(`IDIOM_CLOSED_TABLE_01.md` §4)。

## 4. M4: A2 `too soon to do`の再評価(開示)

| 枠組み | 評価対象 | 結果 | 出典 |
|---|---|---|---|
| 前回: 「自然な英文として適切か・本文対応・意味を保つか」 | `too soon to do` | **reject 3/3**(06〜08の最終プロンプト3回。全8回では7回reject)。理由=「原文にない`do`を加えた一般化」「不自然」 | `judge_06〜08.json` |
| 今回: 「学習者向け辞書の見出し形/パターン見出しとして適切か」(`do`は総称動詞のスロット) | `too soon to do` | **adopt 3/3**(`acceptable_as_headword=true`、`grammar_pattern_with_slot`、学習価値good、意味=generalized)。理由=「too … to do」の汎用パターン | `judge_headword_01.json` |
| 同上(対照) | `too soon`(A1) | adopt 3/3(ordinary_phrase、good、narrowed/generalized) | 同上 |
| 同上(対照) | `too soon to say`/`too late to do` | adopt 3/3 | 同上 |
| 同上(陰性対照) | `soon to do`(演算子を落とした断片) | **reject 3/3**(not_a_learning_unit/bad) | 同上 |

- **枠組みが結論を反転させた**。前回のreject理由の中心は「自然な英文でない」「本文に無い語」で、見出し形(総称スロット)としては成立する。陰性対照(`soon to do`)は3/3 rejectで、評価者が何でも通すわけではないことも確認した。よって、前回の「独立評価でreject」を根拠に区分3へ閉じるのは不適切だった(Opusのとおり)。
- 限界(R6): 評価者`gpt-6-luna`は生成側と同系統(repo承認済みの最新世代推奨系SUPPORT_MODEL。最新かつ下位でない)で、自分の系統の出力を好む偏りがありうる。同一プロンプトを3回回して測れるのは**ばらつきだけで偏りは測れない**。見出し形の枠組みはこちらが選んだもので、枠組みの選択自体が結論を動かすことが今回示された。したがって**LLM評価はユーザー判断の材料(参考)**であり、基準ではない。
- AI意見(非推奨を維持): 理由は評価ではなく**承認済み規則との関係**にある。(a)Rule 7/CURRENT_SPEC:2001「語形変化救済による代替合格は禁止」「本文に無い語を使わない」に対し、`do`は本文に無い語で、出典の具体的な表現(旗を振る=早まって成功を宣言する)が失われる。(b)パターン`too ... to do`は既習の文法項目で、元句が持っていた比喩(wave a flag)の学習価値が残らない。(c)同じ位置の代替として`too soon`(本文の連続部分列、意味は狭まる)が既に取れる。ただし品質水準の最終判断はユーザーが行う(ユーザー自身の例である)。採用する場合の条件案: パターン見出し専用の旗(「総称スロット do」)をHRに表示し、元句と本文の文を併記、gloss再整合を必須、AUTO不可。
- 区分: **区分2(非推奨・意見付き)**。

## 5. 区分1/2/3最終一覧

### 区分1(承認済み仕様への準拠修正。Fable判定のうえ別委任でProduction適用)
DESIGN_01 §5の1-1〜1-4を維持。**修正**: 1-1は「OPEN-152の解」ではなく「**fulltext経路に限った部分解消**。OPEN-152の対象は共有validatorとA/B/Cで、本設計はA/B/Cを変えないため`USER_DECISION_REQUIRED`のまま」(R1)。1-3(副詞guard)はM1の語幹検査+除外表を前提とする。1-1はM2の敵対的testを前提とする。

### 区分2(ユーザー判断。各々の修正例・メリット・リスク・代替・QCD・AI意見)
| # | 案 | 検証済み修正例 | メリット | 品質リスク | 代替 | QCD影響 | AI意見 |
|---|---|---|---|---|---|---|---|
| 2-A | **救済フロー本体**(H1短縮・再アンカー/H2窓内再導出。HR経路限定・既定OFF・AUTO不可・Production既定=決定論のみ) | `too soon to wave a flag→too soon`(旗付き)・`rose above→rise above`・`held out→hold out`(多義旗)・`catch their interest→本文のcatches their interest` | 11件中4件を残す | 狭まる/低価値の候補が出る。gloss・QA再判定が要る | 現行(除外のまま)・外側retry | gloss再整合0.53〜0.56円/件。約0.23円/level-run | **採用推奨**。LLM評価者の併用は任意(残す場合は却下専用・費用明示・QA扱いにしない・約0.05円/呼出)で、**既定は決定論のみ** |
| 2-B | 慣用句の法助動詞例外(レビュー済み閉表27件) | `can’t be helped`/`can of worms`/`might as well`/`had better` | 「仕方がない」等の高価値表現 | 閉表外は通らない。外部辞書は実行時に使わない | 現行どおり除外 | API 0 | **条件付き採用推奨**(ライセンス確認後)。**縮約形(R5)と同時に提示**: 縮約形を助動詞として判定する是正はGateを締める方向で、現在ASCIIで通る`can't wait`(1件採用実績)が止まる。曲線`can’t be helped`は2-Bの閉表で救える |
| 2-C | A1短縮の第1案選択・代替案併記 | `too soon`(旗: 意味縮小・低価値) | HRが判断できる | 低価値候補 | 現行 | API 0 | 2-Aに含める |
| 2-D | A2 `too soon to do`(スロット一般化) | `too soon to do` | 枠を残せる(見出し形評価はadopt 3/3) | 本文に無い語。比喩の消失 | A1 `too soon` | API 0 | **非推奨**(§4) |
| 2-E | CMU未登録語の分解合格 | `redelivery fee` | 1/12 level-run | TTS発音不良の再来。2026-10-22規則の趣旨に反する | 非採用 | TTS+ASRの追加費用 | **非推奨** |
| 2-F | 辞書裏付けguard(V+名詞の原形化) | `lost touch→lose touch` | 原形の見出し語 | 辞書依存 | revert | API 0 | **保留推奨** |

### 区分3(救済すべきでない)
Human NG 3件(`put in place`/`off the hook`/`sentenced him to death`)・`minaudière(s)`等の分解不能な外来語(発音を保証できない)・`could not bear`等(法助動詞/否定が意味の核で、外すと意味が変わる)。**11件内の区分3は0**。A2は区分2へ移動(§4)。

## 6. HR表示案(元句・本文の文・旗)

| 元句 | 本文の文(HR併記) | 提案(第1案)/代替 | 旗 |
|---|---|---|---|
| `too soon to wave a flag` | Even so, it is too soon to wave a flag and say, "Play and get smarter…" | `too soon` / 代替: `wave a flag`(意味changed) | 修正済み・QA未再判定・**意味縮小の可能性**・**低価値の可能性**(2語以下/程度の語が中心)・gloss再整合済み |
| `rose above`(LLMは`rise above the other voices`) | …his sister's laughter rose above the other voices. | `rise above` | 修正済み・QA未再判定・**LLMが補った語(`the other voices`)を破棄**(gloss再整合は本文での意味=声より大きく響く) |
| `held out`(LLMは`hold out one's hands`) | …his friend held out his hands for the chains. | `hold out` | 修正済み・QA未再判定・**目的語(`one's hands`)破棄・多義の可能性**(`hold out`単独の主な意味は「耐える」。gloss再整合は本文の意味=差し出す) |
| `catch their interest`(本文は`catches their interest`) | …let them use whatever catches their interest | 選定=`catches their interest`→key=`catch their interest` | 修正済み・QA未再判定・gloss再整合 |
| `it can’t be helped` | I guess it can't be helped. | `can’t be helped`(主語`it`を除く) | 修正済み・QA未再判定(慣用句閉表) |

## 7. 費用・モデル・最新性
- 本委任: LLM 0.224円(headword再評価 3呼出)。モデル=`gpt-6-luna`(repo承認済みの最新世代推奨系SUPPORT_MODEL。PM_GOVERNANCE 25の「最新世代の推奨系」に該当、旧/下位モデルではない)。生成側と同系統のため偏りは測れない(R6)。
- Production適用時: 区分1は追加API 0。救済フローはDESIGN_01 §7のとおり(gloss再整合0.53〜0.56円/件、約0.23円/level-run、70円目標の<1%)。LLM評価者を残す場合は約0.05円/呼出を追加。
- **期待救済率(再計算)**: HR導入後11件=区分1が4件(36%)、区分2・推奨まで含め10件(91%)、非推奨1件(9%)、区分3は11件内0。導入前一意句25種(現行で通る4を除く)=区分1が5(20%)、区分1+2が17(68%)、区分3が8(32%)。M1〜M3の是正による数値の変化はなし(是正は誤受理を塞ぐもので、実データの救済対象は減らさなかった)。

## 8. OPEN更新文案・新規不具合候補(SSOT未編集。Fable受入後に転記)
- **OPEN-529更新**: 「KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_02(2026-10-26): Opus条件Aレビュー(M1〜M4/R1〜R6)を全件反映しDEV再実証。-ly名詞(supply/rally等)の誤受理・不変化分詞/量化詞介在の語彙have誤判定・名詞主語のことわざを通す慣用句例外を是正(旧実装の誤受理 計40件→0件、実データ315種の単調性違反0)。慣用句例外をレビュー済み閉表27件に限定。A2 `too soon to do`は区分2(非推奨)へ。区分1=4件/区分2=救済フロー・慣用句例外・A1旗・A2(非推奨)・CMU分解(非推奨)/区分3=Human NG。縮約形の不具合候補(R5)あり。Production非配線。Status=`COMPLETED_PENDING_FABLE_ACCEPTANCE`」。
- **OPEN-152追記(R1)**: 「語彙動詞haveの誤判定は、KP fulltext経路(allow_inflection_normalization=True)のみ区分1の是正案(`have_role`+敵対的test)で部分解消予定。共有validator(A/B/C)は未変更で、A/B/Cの扱いは`USER_DECISION_REQUIRED`のまま」。
- **縮約形(R5)**: 新OPENは発番せずOPEN-529へ追記。実測(381句): 縮約形を含む句29のうち、所有格`'s`26件(全件所有格)、ASCII助動詞縮約1件(`can't wait`採用)、曲線助動詞縮約2件(`can’t be helped`ほかdropped)。Gateの現状=ASCII`can't`はすり抜け・曲線`can’t`は拒否。`they’re`/`I’ll`も曲線では`re`/`ll`のみでは助動詞と認識されずすり抜ける。**分類=修正へ進む(範囲内。承認済みの助動詞排除との乖離)**。ただしGateを締める修正で`can't wait`が止まるため、**2-Bの判断と同時にユーザーへ提示**(`'s`は所有格との区別が要り、実測では全件所有格のため`'s`は対象から外す案が合理的)。次委任案: 縮約を「助動詞+not」と判定する是正案の影響測定(API 0)。
- **新規観測A: Production既存の挙動**: `reduced supply of→reduce supply of`が現行ProductionのGuard(承認文「句末が不変化詞」)で既に受理される(パッチ前後で不変。`adversarial_01.json`のpreexisting_accept枠)。V+名詞の誤原形化の余地だが、承認済み文言どおりの挙動で、実データ315種に該当0。**分類=実害なし(観測継続)**。
- **新規観測B(新仕様候補、実装せず)**: 名詞の`can`(`open a can of worms`)は先頭が動詞の句ではGateが拒否する(`can`/`may`/`will`/`must`の名詞用法)。役割判定で是正できる可能性があるが受理面の変更。**分類=修正へ進む候補(次委任で件数を測る、API 0)**。
- OPEN-476(`bound to`)は維持(`bound`は補完から除外)。OPEN-530はDESIGN_01 §8のとおり。
- OPUS台帳文案: OF-KPRS2-M1〜M4/R1〜R6 = すべて「採用・実装・敵対的test固定」(§0)。
- DECISION_LOG文案はFable受入後。

## 9. DESIGN_01との差分
- M1〜M4/R1〜R6の反映のみ。区分(11件)・全体フロー・救済率は不変。A2を区分3推奨→区分2(非推奨)へ。DESIGN_01 §5の「1-1はOPEN-152の解」「A2は区分3推奨」を本書が上書きする。
