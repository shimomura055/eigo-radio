# OPEN-233 「重大 / 軽微 / 問題なし」の線引き(2026-10-03、委任_51)

- 管理ID: `OPEN-233-SELF-RECOVERY-TRIAL-01`(委任_51)。read-only+新規doc(API費用¥0、コード・Prompt・テスト・設計書・CURRENT_SPEC・PM_GOVERNANCE未変更)。
- 位置づけ: ユーザー決定(2026-10-03、`DECISION_LOG.md`末尾エントリ)の例1=軽微・例2=問題なし、を基準例として、Fableが提示した線引き案(下記)を文書化し、既存の原則・実装との整合・不整合を表にしたもの。**ユーザー決定は例1・例2の2件の判定のみ。線引きの文言そのものは「Fable案」であり、Production仕様ではない(`APPROVED_FOR_PRODUCTION`ではない)。** 実装・設計書・rubricへは未反映。
- 再分類の結果: `docs/pm/open233_missed_candidates_reclassification_2026-10-03.md`。

## 1. Fable案(線引き。委任文のとおり、文言を変更していない)

- **重大(BLOCKING)= 読者に事実関係の重大な誤解を与える**。該当: (1)数値・数量・規模の変更や創作、(2)主体・当事者の取り違え、(3)否定の反転、(4)因果・比較・時期の変更や創作、(5)Ledgerの`notes_for_writer`が明示的に禁じる断定(例: 「実際の大規模な情報漏えいが発生した」と断定)、(6)Ledgerに無い新しい具体的事実(人物・出来事・発言・数値)の追加、(7)**被害・結果にあたる核心の主張**を、Ledgerが条件つき・可能性としか書いていないのに発生したと断定すること。
- **軽微(QUALITY)= 事実関係の核心は保たれているが、言い回しの精度が落ちている**。該当: (a)条件つき・可能性の内容を発生として書いているが、**被害・結果にあたる核心の主張には留保が残り、主体の帰属も保たれている**(例1: 「some calls needed user information」は断定だが、共有は「might」で留保、懸念の主体はMeta従業員のまま)、(b)対象の一般化で核心の主張が変わらないもの(Brent原油先物→oil prices、副社長→executive)、(c)語句の粗さ(肩書きの補い等、er003 533〜534行のMINOR規定に相当)。
- **問題なし(ACCEPTABLE)= Ledgerの事実から自然に導かれる描写・推論・物語的な導入で、新しい具体的事実を加えない**。該当: (i)開示がなかった等のLedger事実から導かれる利用者の状態・認識の推論(例2: 「They enjoyed AI’s convenience … They did not realize it.」。否定形・肯定形を問わない)、(ii)場面描写・導入(hook)で具体的な事実を加えないもの、(iii)同義の言い換え。
- **判定の順序**: まず重大の(1)〜(7)に当たるかを見る(1つでも当たれば重大)。当たらなければ軽微の(a)〜(c)。どれにも当たらなければ問題なし。迷う場合は、「読者がこの文を信じたとき、実害のある誤った行動・認識につながるか」で決め、つながるなら重大、つながらないなら軽微。
- **例1・例2から一般化した点**: 例1は(7)と(a)の境界を定める(核心の主張=「情報が共有された」。それが留保されていれば軽微)。例2は(i)を定める(既存の降格ルールは否定形に限定していたが、ユーザー決定により肯定形の推論[「驚いた」等]も、新しい具体的事実を加えなければ問題なし)。
- **既存の機械的な安全装置(数値・主体・否定・比較・時期のfloor、precheck)は変更しない。**

## 2. 既存の原則・実装との整合/不整合(各Grepで確認)

確認箇所: `docs/pm/design_open233_self_recovery_flow_01.md`(§0-1/§0-2 219〜245行、§4-21 1404〜1427行、§7-0-iter27 3566行〜、§7-0-iter29 3614行〜、disclosure_gap降格 1228〜1246行)、`er052_open233_self_recovery_stage2_production_01.py` 37〜46行、`er052_open233_self_recovery_stage2_calibration_01.py` 433〜(V4)・462〜(V5)・509〜(V6)、`er003_v1_en_direct_vfl_01_generate.py` 525〜541行、runner `SAFETY_CRITICAL_CLAIM_DEFS`(6145〜6175行)・`DISCLOSURE_GAP_NEGATION_RE`(2141行)・`FLOOR_FLAGS`(492行)・`BODY_RUBRIC_DEFAULT`(391行)。

| # | 既存の原則・実装 | 内容(要点) | Fable案との関係 |
|---|---|---|---|
| 1 | 設計書§0-1 重大誤解原則 | 「この違いは英語学習者に深刻な誤解を与えるか?」が最初の問い。それ以外はできるだけ元記事を守る | **整合**(Fable案の「迷えば実害で決める」と同じ問い) |
| 2 | 設計書§0-2 原則許容候補 | Brent→oil prices、2.6%→about 3%、確認済みFactから自然に導けるHook演出は許容(BLOCKしない) | **整合**((b)(ii))。ただし§0-2は「許容」の1区分で、軽微と問題なしを区別していない。Fable案の(b)=軽微は新しい区別(下記指摘5) |
| 3 | 設計書§0-2 BLOCK候補 | 上昇→下落(方向反転)、主体A→B、継続していた出来事→一度消えて戻った出来事、未確認の人物・行動・動機・数字の追加、因果の逆転 | **概ね整合**((1)〜(4)(6))。「動機の追加」「継続→消えて戻る」「方向反転」はFable案の列挙にない((4)の読み方次第、下記指摘3) |
| 4 | 設計書§4-21 V4原則 | 条件つき→断定を§0-2の「未確認の行動の追加」として**一律BLOCKING**(Meta-1をSafety-critical維持) | **不整合**。ユーザー決定の例1(軽微)により置き換わる対象。V4は「核心の主張に留保が残るか」を区別しない |
| 5 | 設計書§7-0-iter27 | Brent→oil pricesの一般化は許容候補、正解ラベルをBLOCKINGからACCEPTABLE/QUALITYへ(2026-10-01ユーザー指示) | **整合**((b)) |
| 6 | 設計書§7-0-iter29 | A5-1(副社長→executive)はQUALITY、Safety-criticalから除外 | **整合**((b)) |
| 7 | 設計書1228〜1246行 disclosure_gap降格 | 否定形(`DISCLOSURE_GAP_NEGATION_RE`)に限定、肯定形の「驚いた」「気づいた」には適用しない。条件: floor不発火+新しい数値・固有名詞なし | **不整合(既知)**。Fable案(i)は否定形・肯定形を問わない(ユーザー決定の例2の一般化)。「新しい具体的事実を加えない」条件は(i)と整合 |
| 8 | Stage 2 `MATERIALITY_RUBRIC`(production 37〜46行) BLOCKING | Ledgerの記載と矛盾/別の原因・別の主体/notes_for_writerが禁じた断定 | **概ね整合**((1)〜(5)) |
| 9 | 同 QUALITY | 矛盾しないが、Ledgerが保証していない関係付け(因果接続詞・**動機の帰属**・強調)が加わる | **不整合**。Fable案(4)は因果・動機の創作を重大とし、設計書§0-2もBLOCK候補、B4-a(AIフォールバック機構の新規主張)=BLOCKING。このrubricは動機の帰属をQUALITYとする(K20〜K22の分類に影響、下記指摘3) |
| 10 | 同 ACCEPTABLE | 新規の固有名詞・数値・時期・主体・因果を一切加えず、一般常識レベルの背景説明・条件付きの一般論 | **整合**((i)(ii)(iii)に近い) |
| 11 | 同 「迷う場合はBLOCKING(fail-closed)」 | 迷えばBLOCKING | **不整合**。Fable案は迷えば「実害のある誤認につながるか」で決める(つながらなければ軽微)。fail-closedは既存のSafety側の安全装置であり、変更するとSafety原則の変更に当たる可能性がある(下記指摘4) |
| 12 | `BODY_RUBRIC_DEFAULT`=V6(calibration 509〜) | V6は「別の特定の理由を断定」「Ledgerが特定していない主体(支払義務者等)を特定」を明確にBLOCKINGとする | **整合**((2)(4)(6))。K18の分類根拠 |
| 13 | V5(calibration 462〜) | 確認済みの中心的出来事から導ける、受け手側の驚き・反応の言及は新しい具体的Factの追加ではない(Stage 2 LLM側のrubric文言) | **整合**((i))。肯定形の推論をStage 2のLLM判定側では既に許容方向に誘導している(post-hocの降格ルールが否定形限定なのは別の話) |
| 14 | er003 533〜534行 MINOR規定 | 意味はおおむね保つが言い回しがやや粗い場合(出典に勝手な肩書きを補う、自己申告の調査結果を断定的な行動として書く)はMINOR | **整合**((c)) |
| 15 | er003のMAJOR条件(10フラグ) | 10種類のうち1つでも明確にtrueならMAJOR。changed_certaintyもMAJORフラグ | **差あり(整合は可能)**。条件→断定はChecker段階では引き続きMAJOR(`changed_certainty`)で出力される。軽微化はStage 2のmateriality判定側で行う設計になる(Checker側の10フラグは変更不要) |
| 16 | 機械floor(`FLOOR_FLAGS`: actor/number/negation/comparison/time) | LLM判定にかかわらずBLOCKINGへ引き上げる | **Fable案は変更しない前提**。ただし再分類の事実として、LLM判定がACCEPTABLE/QUALITYなのにfloorだけでBLOCKINGになった種類が8あった(K08, K09, K11〜K15, K17)。floorを変更しない限り、新しい線引きでも過剰品質は残る |

## 3. Fable案への指摘(無理・矛盾。勝手に直していない)

1. **(7)と(a)の境界が文の位置に依存する**: 例1は「some calls needed」の文と留保の「might」の文が別の文(隣接)にある。留保が同じ段落内の別の文にあれば足りるのか、同じ文内に必要か、は案に書かれていない。K04は「隣接する次の文」で留保される型として軽微にした。
2. **(1)「数量の変更」の範囲**: K05〜K07(HC-011の「1件の報告」に対し「calls」「These calls」と複数形)は、(1)を字面どおり当てると重大になる。本分類では、同じ段落が「one employee’s report」「only one report」と件数を固定しているため(c)軽微とした。(1)の「数量」を「記事が明示した件数・数値」に限るのか、複数形のような単複の差も含むのか、を決める必要がある。決め方で真の重大見逃しが3種類(同一箇所の入れ子)増える(再分類doc 2-3節)。
3. **(4)に「動機・意図の創作」を含めるかが未記載**: K20〜K22(「when AI struggled, a person could help」=Metaの設計意図の追加)は、Fable案の列挙では(4)の因果の創作か(6)で読む必要がある。設計書§0-2(BLOCK候補「動機の追加」)、B4-a(AIフォールバック機構の新規主張=BLOCKING)は重大側だが、Stage 2 production rubricは「動機の帰属」をQUALITYとして食い違う(表9)。本分類は重大(境界)とした。見逃しはいずれも0のため、見逃し数には影響しない。
4. **「迷う場合」のルールが既存のfail-closedと逆向き**: 現行は「迷えばBLOCKING」(表11)。Fable案は「実害につながるか」で決める。これはSafety側の既定動作の変更になりうるため、採用して実装へ反映するなら、委任文のSTOP条件(Safety原則の変更はUSER_DECISION_REQUIRED)に該当する可能性がある。今回は文書化のみで実装していない。
5. **(b)=軽微と§0-2「原則許容」の対応が未定義**: 設計書は「許容」の1区分。Fable案は(b)を軽微(QUALITY)、(iii)を問題なしとして分ける。現行flowはQUALITYを非BLOCKINGとして通すので、実質の挙動は変わらないが、軽微を記事に残すのか、可能なら直すのか(Rewriteの要否)は案に書かれていない。ユーザー決定は「軽微な品質問題として許容」(残してよい)。
6. **K19(prices began to fall)とK18(支払う側の特定)は判断が分かれる**: K19は§0-2「上昇→下落(方向反転)」とnotes_for_writerを根拠に重大としたが、直後に「returned to a high level」と続くため、(7)の「核心の主張が保たれるか」で読めば軽微にもなりうる。K18は既存のV6 rubricが明示的にBLOCKINGとする型で、実害は小〜中。Fable案の文言だけでは両者の線が引ききれない。
7. **ユーザーの「20」「18」の対応づけ**: 23種類のうち、見逃しが1実行以上あったのが18、入れ子3種類(K20〜K22)を除くと20。「例1・例2を含め20、残り18」を同時に満たす一意の対応は無い(再分類doc 2-2節)。

## 4. 作業4: 新しい線引きと現在の実装・ラベルの食い違い(読むだけ。変更しない)

ユーザー指示は「真のMajor見逃しだけが対策対象」であり、以下はいずれも変更していない。

| # | 箇所 | 新しい線引きとの差 | 変更した場合に必要になる再較正(過去の較正の費用等) |
|---|---|---|---|
| 1 | 設計書の正解ラベル表(§7-0-iter27の委任_29追記 3602〜3612行、§7-0-iter29 3614行〜): Meta-1/Meta-2(MUSE-HC-010「needed user information to continue」)はSafety-critical(BLOCKING維持)。runner `SAFETY_CRITICAL_CLAIM_DEFS`(6163〜6166行)に`meta_run03_standard`のMeta-1(HC-010)・Meta-2(HC-012)として登録、`detect_safety_critical_misdowngrades`/`silent_pass_candidate`の対象 | 新判定は軽微(K04)。ラベルがBLOCKINGのまま残る限り、Stage 2がQUALITYへ降格させると「Safety-critical誤降格」警告になる(偽の警告)。設計書の「Meta-1=§0-2の未確認の行動の追加に該当」という記述(§4-21)も新しい線引きと食い違う | ラベル更新(設計書の正解ラベル表・`SAFETY_CRITICAL_CLAIM_DEFS`から2件除外、Safety-critical 8claim→6claim)は¥0(定義の変更+unittest)。ただし、その後のStage 2の合否検証(Safety-critical定義の変更後の誤降格0件の再確認)が必要。過去の同種の検証費用: V4の較正¥4.9438(Safety-critical 8claim+Safety12[er009 9フラグ]+Hormuz許容5/NG5、n=1予備+n=2公式、設計書§4-21)、V6昇格¥6.4033(同§9-1付近) |
| 2 | `MISCONCEPTION_PRINCIPLE_TEXT_V4`(calibration 433〜、V5・V6が積み上げ、現行`BODY_RUBRIC_DEFAULT`=V6に含まれる): 条件つき→既成事実の断定を「§0-2の未確認の出来事の追加」として**一律BLOCKING** | 新しい線引きでは、核心の主張に留保が残り主体の帰属が保たれるなら軽微(例1)。V4の文言は留保の有無を区別しない | V4の1段落の修正(新しい例示は追加しない)+再較正が必要。過去の費用: V4¥4.9438、V5のSafety再確認¥1.6243+rep17¥3.1313、V6昇格合計¥6.4033。priming(原則文が存在するだけで別のSafety-criticalが誤降格する現象、設計書1116行・委任_16の実測)のリスクがあり、Safety-critical 8claimの再測定が必須。Safety原則の変更に当たる場合はUSER_DECISION_REQUIRED |
| 3 | disclosure_gap降格(`apply_disclosure_gap_downgrade`、runner 2141行付近、設計書1228〜1246行): 否定形(`DISCLOSURE_GAP_NEGATION_RE`)に限定。条件=floor不発火+`unsupported_new_claim`または`changed_certainty`+否定形+新規数値・固有名詞なし | 新しい線引き(i)は肯定形の推論も問題なし。現行は肯定形(例: K23「That was what people thought」)にはこの降格が効かず、Stage 2のLLM判定(V5文言)だけが頼り | 正規表現の拡張(肯定形の語)は決定論で¥0だが、false downgrade(本来重大なものの降格)を防ぐ再測定が必要(Safety-critical 8claim+Safety12のStage 2のみ、n=1で¥数円規模が過去の同種の水準)。Trial限定の判定候補であり、Production採用(`APPROVED_FOR_PRODUCTION`)には別途ユーザー承認が必要 |
| 4 | Stage 2 production `MATERIALITY_RUBRIC`(production 37〜46行): QUALITYに「動機の帰属」、末尾に「迷えばBLOCKING」 | 表9・表11のとおり、動機の帰属と迷いの扱いがFable案・設計書§0-2と食い違う。なお、現行flowの`BODY_RUBRIC_DEFAULT`はV6(calibration系)で、このproduction rubricとは別系統(runnerは`s2p`も`import`、使い分けは未精査) | 変更する場合は、K04(条件→断定)・K20〜K22(動機)を含む較正セットでの再測定が必要。Safety側の既定(fail-closed)の変更に当たるためユーザー判断 |
| 5 | 機械floor(`FLOOR_FLAGS`、runner 492行) | Fable案は変更しない前提。ただし再分類で、LLM判定がACCEPTABLE/QUALITYなのにfloorだけでBLOCKINGになった種類が8(K08, K09, K11〜K15, K17)。新しい線引きでも過剰品質の主因として残る | 変更しない方針。仮に変更する場合は、er009 9フラグ(Safety12)・changed_actor等のfixtureを使った再較正が必要(過去: 委任_30〜35のD是正、rep20で¥6.0782、設計書§6-16) |
| 6 | 設計書の正解ラベル表(B4-aほか): B4-a(AIフォールバック機構の新規主張)=BLOCKING | Fable案(4)(6)と整合。K20〜K22が同型のため、重大のまま。変更不要 | なし(整合) |
| 7 | 設計書§7-0表の旧版B4-d(「実際に驚きを生じさせた」確実性強化、Trial扱いBLOCKING): 委任_12でQUALITYへ再ラベル済み(runnerコメント) | 例2の肯定形推論の許容と方向は整合(再ラベル済みのため差なし)。ただし設計書3510行・3743行付近の旧表記に「BLOCKING(Trial扱い)」の記述が残っている | 文書の整合のみ(¥0)。設計書は本委任では編集しない |

- 未精査: Hook専用rubric(`er052_open233_self_recovery_stage2_hook_01.py`、`HOOK_RUBRIC_WITH_MISCONCEPTION_PRINCIPLE_V4`)は本委任の事前指定Readに無く、内容を読んでいない。(ii)hookの扱いとの整合は未確認。
- 一覧外のRead/確認: `er052_open233_self_recovery_flow_runner_01.py`の`build_target_instances()`をimportして呼び出し(fixtureの`ledger_text`取得、API呼び出しなし、¥0)、`er051_output/.../step1/A2A3/V4A/run_1.json`(K19の固定Stage 1出力の確認)、各instance JSON(K18・K19の再確認)、`docs/pm/design_open233_self_recovery_flow_01.md`の追加行範囲(3503〜3514、3737〜3745)、`calibration` 385〜470・509〜530行。

## 5. 正式採用(2026-10-03、`APPROVED_FOR_PRODUCTION`、`PRODUCTION_WIRED`未達、委任_55で追記)

ユーザーは2026-10-03(2回目の決定、`DECISION_LOG.md`末尾エントリ)に、上記のFable案を土台とした一般ルールを正式採用した。Statusは`APPROVED_FOR_PRODUCTION`。再較正・テスト・runtime evidence・SSOT更新が終わるまで、またSelf-Recovery Flow自体がProduction未接続のため、`PRODUCTION_WIRED`ではない。

### 5-1. 正式な基準(ユーザー原文、逐語)

- **重大**
  - 英語学習者に事実関係の重大な誤解を与えるもの
- **軽微**
  - 事実関係の核心は保たれているが、表現の精度が少し落ちるもの
- **問題なし**
  - 確認済みFactから自然に導ける描写・推論で、新しい具体的事実を追加しないもの

例として、すでにユーザー判断済みの以下を必ず基準にしてください。

- `Also, some calls needed user information to continue.`
  → 軽微
- `They enjoyed AI's convenience, but a human was on the other end. They did not realize it.`
  → 問題なし
- `Just after the charge plan disappeared, prices began to fall.`
  → 軽微

特に、

- 条件付き→断定を一律Majorにしない
- 自然な推論は否定形だけでなく肯定形も許容
- 「迷ったら重大」に機械的に寄せず、重大な誤解になるかで判断

という方向へ合わせてください。

ただし、数値・主体・否定・比較・時期などの機械的な安全装置については、今回の採用内容だけを理由に勝手に緩めないでください。

### 5-2. Fable案との対応

- Fable案(1節)は、上記3定義の具体化として維持する(重大の(1)〜(7)、軽微の(a)〜(c)、問題なしの(i)〜(iii)。判定の順序も維持)。
- ただし1節「判定の順序」末尾の「迷う場合は、読者がこの文を信じたとき、実害のある誤った行動・認識につながるかで決める」は、ユーザーの「『迷ったら重大』に機械的に寄せず、重大な誤解になるかで判断」で**置き換える**(ユーザー文言が正)。
- 機械的な安全装置(`FLOOR_FLAGS`によるfloor、precheck、主体置換ガード)は不変。数値・主体・否定・比較・時期の差は、この原則(迷ったら重大な誤解になるかで決める)の対象外で、従来どおり機械的にBLOCKINGとする。
- K19(`prices began to fall`)は、ユーザー決定により軽微(旧: 重大(境界))。Fable案の(7)・(a)の境界を、K19の側(軽微)へ引く事例になった。

### 5-3. 3節の指摘7点の「正式採用後の扱い」

1. (7)と(a)の境界が文の位置に依存する: 正式採用後も、境界は「核心の主張に留保が残り、主体の帰属が保たれるか」で判断する(rubric V7の3-1の文)。留保が隣接する文にある型(K04)は軽微のまま。同一文内か隣接文かの線引きは未規定のため、再較正の対象外(未決のまま残る)。
2. (1)「数量の変更」の範囲: K05〜K07(単数→複数形)は、ユーザー決定の例には含まれない。再分類docのとおり軽微(境界)のまま。ユーザー決定の追加は無く、未決のまま残る(再分類doc 2-3節の感度どおり)。
3. (4)に「動機・意図の創作」を含めるか: rubricの「動機の帰属=QUALITY」(production `MATERIALITY_RUBRIC`)は変更しない(委任_55 3-4)。新しい基準の「新しい具体的事実の追加」に当たる動機の創作(K20〜K22、B4-a)は、V7の3-1の文(Ledgerに無い新しい具体的事実の追加はBLOCKING)で拾う。食い違いの残り(production `MATERIALITY_RUBRIC`と設計書§0-2)は未解消として記録する。
4. 「迷う場合」のルールが既存のfail-closedと逆向き: ユーザーが「迷ったら重大に機械的に寄せず、重大な誤解になるかで判断」と明示したため、Safety原則の変更としてユーザー承認済み。rubric V7で置き換える(旧版は定数として残す)。機械的な安全装置は不変。
5. (b)=軽微と§0-2「原則許容」の対応: 現行flowはQUALITYを非BLOCKINGとして通す(軽微は記事に残してよい)。ユーザー決定の例1・K19も「軽微な品質問題として許容」であり、Rewriteしない。軽微を記事に残す扱いはそのまま正式化された。
6. K19・K18の判断が分かれる: K19はユーザー決定で軽微に確定。K18(日本語文の支払い主体)は、日本語本文は原則修正しない方針(ユーザー判断2026-10-03)のもとで、英語側の同内容文がBLOCKING検出済みのため、重大だが内容として見逃しなしの扱いのまま。
7. 「20」「18」の対応づけ: ユーザーが再度の確認をしていないため、対応案A・Bの2案併記のまま(再分類doc 2-2節、K19更新後の値で更新済み: 案A 18/20過剰・0/20重大見逃し、案B 17/18過剰・0/18重大見逃し)。

### 5-4. 実装への反映(委任_55)

- Stage 2のbody rubric: `MISCONCEPTION_PRINCIPLE_TEXT_V7`(V6に追記、旧版は残す)へ昇格。差分は設計書§4-23と再較正の`rubric_diff.md`。
- 正解ラベル: Meta-1/Meta-2=QUALITY、MUSE-HC-012「They enjoyed…」=ACCEPTABLE、HF-009「prices began to fall」=QUALITY(いずれもユーザー決定)。`SAFETY_CRITICAL_CLAIM_DEFS`のMeta-1/Meta-2は「過剰品質の監視用」(期待QUALITY)へ移し、Safety-critical検出の対象外とした。
- 決定論的な降格(`DISCLOSURE_GAP_NEGATION_RE`、否定形限定)は変更しない。肯定形の推論の許容は、rubric本文(V7)の追加文だけで行う。
- Production配線時は、`PM_GOVERNANCE.md` 11-3節の条件C(重要変更のProduction採用提案前のOpus独立技術レビュー)で、本線引き・rubric V7・句読点差対策を併せて確認する。
