# C1_POSITIVE_CONTROL_CLOSEOUT_01(FAMILY-X-RESEARCH-BACKGROUND-GAP-ROOT-CAUSE-01 委任_03、2026-10-20)

- Status: `C1_POSITIVE_CONTROL_TRIAL_CLOSEOUT_PENDING_FABLE`。eval機械判定=`REJECTED_CANDIDATE_MACHINE`(Fable最終ラベル待ち)。Production採用はユーザーのみ・未承認。DEV/Trial専用経路、Production Prompt/schema/producer/Writer/B3/Research Prompt変更0。
- 設計・判定基準は`C1_POSITIVE_CONTROL_DESIGN_01.md`§5を実走前から変更していない。使用モデル=Production B3 routing値(`gpt-6.1-sol`、前Trial実測と同一、最新世代)。C1文言sha 592a13b3…無改変。
- 生データ: `er083_output/c1_positive_control_01/`(`c1_posctrl_eval.json`、セル別`trial_meta.json`)。commit 1ea464843。

## 1 R1 セル別結果(B3 12 call、実費JPY112.78、全セル status=OK・技術retry0・`rules_sha256` 525f2309…不変)
| Ledger | 期待core | baseline s1 / s2 採用 | C1 s1 / s2 採用 | 【背景補完】追加 | 期待core採用 | extras | eval判定 |
|---|---|---|---|---|---|---|---|
| PC1_hormuz(陽性) | HF-006 | HF-002,007,009 / 同 | HF-002,007,009 / 同 | 0 / 0 | baseline 0/2, C1 0/2 | 0 | **POS_NOT_ADDED** |
| PC2_mey_positive(陽性) | F12 | F11,F12 / 同 | F11,F12 / 同 | 0 / 0 | baseline 2/2, C1 2/2 | 0 | **NONDISCRIMINATING**(flag CORE_ADDED_WITHOUT_MARKER=C1とbaselineが同一選定でマーカー無しcore採用) |
| NC1_coffee(陰性) | なし | 001,010,014,015 / 同 | 009,010,014,015 / 001,010,014,**018** | 0 / 0 | - | 1(COFFEE-018、マーカー無しの入替) | **NEG_FAIL**(機械規則) |
- overall=`REJECTED_CANDIDATE_MACHINE`(NC1 NEG_FAIL または 判別可能な陽性が全てPOS_NOT_ADDED のいずれかで成立)。
- 解釈: C1は12 callすべてで`【背景補完】`付きFactを**1件も追加していない**(supplement=0)。NC1のNEG_FAILは補完追加ではなく、C1 s2で採用がCOFFEE-015→018、s1で001→009へ入れ替わったことによる(baselineは2/2同一だったが、B3選定自体がn=2では揺れる。recheck_noteはいずれも『追加不要』)。事前固定規則(baseline観測∪過去実績外のマーカー無し新規=extras)では機械的にNEG_FAILだが、『C1が背景Factを追加した』事象ではない。基準は変更しない。
- C1のrecheck_note(PC1): 「HF-002とHF-007で提案主体・提案理由・置換の経緯、HF-009で発表後の値動きと継続する軍事・海運上の懸念を確認できるため、初見の理解に不可欠な前提の欠落はない」(s1)。HF-006(7/13のBrent+9.59%の背景=対イラン海上封鎖・ホルムズ懸念)は『補足/部分的に示される前提』として扱われ、C1仕様自身の既定(部分的に示される前提は欠落とみなさない・迷えば追加しない)が働いた。

## 2 Writer到達・本文使用の追跡(R2、W-1 2本、実費JPY26.40)
- 条件: PC1はC1が期待coreを採用せず(0/2)W-1対象外。PC2のみ『C1が期待core F12を採用』を満たすため C1 s1とbaseline s1の各1本(Production `run_w1_writer`、契約V1-V10は課金前)。**ただしPC2ではC1の追加ではなく、baselineも同一のF11,F12を採用**している(NONDISCRIMINATING)ため、これは『C1が追加したFactのWriter到達』ではなく『B3が採用した主体Fact(F12)のWriter到達』の検証。
- trace(`trace_writer_path`、両条件): in_selected=true / annotation.json facts[].ledger_ids=F12あり / writer_constraints.txt有 / 契約V1-V10 PASS / `rules_sha256` 525f2309…一致=既存producer→W-1入力経路でF12は届く。schema・producer変更は不要(F12は通常のcore Factとして乗る)。**C1が追加した補完Factの到達は、追加が0件のため未検証**(補完マーカー付きFactの伝達はW-1入力で通常Factと区別されない設計=前Trial §3の『補足扱い』リスクは観測機会なし)。
- 本文使用: baseline・C1ともに『特使は…サウジの民間施設への攻撃をアンサール・アッラーによるものと述べた/攻撃停止を求めた』を明記(キーワード『アンサール』両方True、参考値)。

## 3 盲検rubric(項目3・5・6)— **限定的・厳密な盲検ではない(開示)**
- 設計は『別process採点』。本委任ではPC1に記事が無く(W-1対象外)、PC2のみ2本。パック`C1_POSCTRL_BLIND_PACK_01.md`(A/B化、key=`blind_key.json`)は生成したが、**採点は実行agent自身が行い、W-1生成直後に記事ラベル(baseline/C1)を既に知っていたため盲検にならない**。別Agent起動は禁止のため。したがって下表は参考値で、VALIDATED/REJECTEDの根拠には用いない(判定は機械判定に基づく)。判定の再現にはパックを別採点者に渡せる。
| 項目 | PC2(baseline記事 vs C1記事) | 所見 |
|---|---|---|
| 3 中心Storyline・エンタメ | 同等(両記事とも『空港攻撃→イエメン和平』の視点転換。C1記事は『地図を一段引く』構成で読み味は同等〜やや良) | 維持 |
| 5 理解しやすさ(読者質問『サウジ施設への攻撃は誰によるものか』) | **両記事とも正答が記載**(アンサール・アッラー、特使の説明・声明) | **改善なし**(baselineが既に正答。C1の便益は未確認) |
| 6 誤帰属・因果創作・過剰網羅 | 両記事とも違反0(主体は特使の帰属として保持、和平影響は『特使の評価』と明記、動機の創作なし) | 違反0 |

## 4 判定基準の評価と候補Status
- 事前固定VALIDATED条件: 『判別可能な陽性が全てPOS_ADDED_2of2』を満たせず(PC1=POS_NOT_ADDED、PC2=判別不能)。REJECTED条件の『判別可能な陽性が全て追加0』は成立(判別可能な陽性=PC1のみ)＋NC1はNEG_FAIL(機械規則)。→ eval機械判定`REJECTED_CANDIDATE_MACHINE`。『追加しなかった』は成功扱いしない。
- 候補Status: **REJECTED提案**(最終ラベルはFable)。ユーザー§3の『単に追加しなかった結果を背景補完能力の成功としない』に整合。
- 判定の限界(正直な開示): ①判別可能な陽性はPC1の1件のみ、n=2。②PC1の期待core(HF-006)は『Storyline理解に不可欠か』が主観的(設計書リスク1)で、C1が『HF-009等で部分的に示される』と判断した点は文言どおりの挙動であり、陽性対照として最適とは断定できない。③PC2は本来の通常B3が主体Factを拾うためC1の効果と分離できず。

## 5 W4 失敗時の原因分析と修正再検証の要否
- 原因(観測): (a)C1の既定・安全弁(補完なしが既定、部分的に示される前提は欠落でない、迷えば追加しない、推測で言えるFactは直接述べていない扱い)が設計どおりに作用し、PC1のHF-006を『補足』として追加しなかった。2サンプルとも同一(recheck_noteの推論も同型)で非決定性ではない。(b)PC2は通常B3がF12を『誰が』の核として採用。
- 承認範囲内の修正案の検討: 『部分的に示される前提は欠落でない』『迷えば追加しない』を緩める修正はHF-006を拾う可能性がある一方、NC1(背景風Factが多数)での過剰補完とユーザー項目2・6(不必要なFact・過剰網羅)の悪化に直結する。陽性1件に合わせた文言調整は過学習で、構造的な弁別力の改善ではない。→ **改善見込みが低いと判断し、再検証(R3)は実施しなかった**(Cap残も未使用: 使用139.2/180)。この判断はFableが覆せる(R3を行う場合の費用見込みはC1'×{PC1,PC2,NC1}×2=約50円)。
- 重要な副次所見: **Ledgerに主体Factが存在すれば、通常のB3(baseline)がそれを拾う**(PC2 baseline 2/2でF12採用)。委任_01の根本原因(Researchが出典の帰属を落とす)と合わせると、中東記事で『誰が』が欠けたのはB3/C1の選定ではなく**上流のResearch/検証でLedgerに主体Factが無かった**ためで、C1を足してもそれは直らない。是正の本線はResearch/検証Promptの条件付き観点追加(新仕様=ユーザー判断事項、委任_01 §5-3)。

## 6 Production採用時に必要なschema/producer変更(仮にC1を採用する場合)
- 『【背景補完】』は`fact_tests[].reason`先頭の転用で、Production採用にはschema(補完区分フィールド)変更が必要(前Trial/設計書リスク5)。ただし本Trialでは補完Fact追加が0件のためWriter到達は実証されず、変更範囲の確定には追加が実際に起きる陽性が先に必要。現時点でschema/producer変更は提案しない(実装0)。

## 7 費用
| 工程 | 実費 | 備考 |
|---|---|---|
| R1 B3 12 call | JPY112.78 | 平均9.40円/call(前Trial8.67円。coffee C1が13.1〜13.4円) |
| R2 W-1 2本 | JPY26.40 | baseline 12.87 + C1 13.53 |
| 合計(本委任) | **JPY139.18** | Cap180(R1 125/R2 55)内。案件合算139.18≤300 |
- 当日(JST)累計(`daily_dev_cost_01.py`、全作業): JPY390.26(本委任139.18を含む)。1,000円/日内。
- 追加工程の時間: R1壁時間≈2分(3 process並列)、W-1≈1分。量産単価への影響: C1はProduction未採用のため影響なし(採用すればB3 call+1回の追記プロンプト分のトークン増。追加callなし)。
- 再開: なし(R1・R2とも途中停止なし)。W-1初回起動で`--out-root`指定誤り(preflight guard、API前)により2process失敗→課金0で引数修正し再実行(費用重複0)。
