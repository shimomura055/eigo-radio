# RESULT_01: Key Phrase選定・一般化 品質改善Trial(KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 委任_01)

原文=`docs/pm/delegation_log/2026-10-30_KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01_USER.md` / OPEN-618 / Trial専用・Production変更0 / 比較ページ=https://shimomura055.github.io/eigo-radio/user_test/kp_generalization_trial_01/ (公開確認は報告参照)

## 1. 結論・Trial Closeout Status(案)

**Closeout案: USER_DECISION_REQUIRED(Status上限VALIDATEDの手前。Fableが最終判定)。** 推奨=『方式Dの方向を採用して実装設計へ進む(Opus条件Aレビュー経由)』。ただし下記の判断事項と、追加Trial1回(約¥5)を前提とする。

- 目的(『7候補から修正なしで最大3件を選べる』)に対する実測(Sonnet実読、14ケース=必須8+汎化3+未使用3、フレーズ枠のみ):

| | 現行(Before) | 方式A(統合1call) | 方式D(工程分離・最終設計案) |
|---|---|---|---|
| そのまま選べる候補/提示候補 | 26/66(39%)※Beforeを再現できた12ケース | 56/70(80%) | **61/71(86%)** |
| Standard | 8/30(27%) | 20/28(71%) | **23/26(88%)** |
| Advanced | 18/36(50%) | 36/42(86%) | 38/45(84%) |
| 『3件以上そのまま選べる』ケース | 4/12 | 11/14 | **12/14** |
| 必須9例(下表) | 現行で達成: 学習価値3/4(blow a whistle・make room for・sales pitch)、一般化0/5 | 一般化2〜3/5(G4部分・G5・G1はb1bのみ)・学習価値3/4 | **一般化3/5(+G2は一般化単体で達成)・学習価値4/4** |
| 1レベルあたり費用(円) | 既存 | 0.31 | 0.98 |

- **目的は『概ね達成・完全ではない』**: Dの提示候補の14%(10/71)は修正が必要(自由な組合せ4・意味が変わる2・不自然な一般形2・易しい1・受動形残り1)。必須9例のうちG1(`take points away from`→`take something away from`)は未達、G2(`make life work`→`make something work`)は一般化単体では達成だが選定段で『自由な組合せ(F)』として脱落する。ユーザー指示の『候補が不足する場合は品質を下げて埋めない』に従い、提示は平均5.1件(7件に満たない)。
- 設計上の発見(最重要): 現行のcanonicalizationは**規則1〜5以外の変換を決定論検証で却下する**ため、目的語のsomething化・後続名詞句の除去は仕様上できない(不具合ではない)。改善には『本文一致を保つsource_span』と『学習表示用の一般化display_form』を分け、後者に別validatorを置く新しい許容ルールが必要=ユーザー判断事項(OPEN-349と同系統)。

必須9例の結果(○=ユーザー指定の方向を達成):

| # | 元の表現 | 望ましい方向 | Before | A(統合) | D(工程分離) |
|---|---|---|---|---|---|
| G1 | take points away from | take something away from | × 未一般化 | △ b1bで達成/a2は選定されず | × 選定段でF判定、単体でも`points`をCOREに残す |
| G2 | make life work | make something work | × | × 選定されず | △ 一般化単体○(`make something work`)、選定段でF判定 |
| G3 | at the time of writing | at the time of | × | × `writing`を残す | ○ `at the time of`(gloss『〜の時点で』) |
| G4 | narrow down the source | narrow down | × | ○ `narrow something down` | ○ `narrow down` |
| G5 | turn the usual steps around | turn something around(語義=順序を逆にする) | × | ○ | ○ 語義保持 |
| V1 | confirm a clear fall(drop) | 原則NG | × 提示されている | ○ 除外 | ○ 除外(F判定) |
| V2 | make room for | 提示 | ○ | ○ | ○ |
| V3 | blow a whistle | 提示 | ○ | × 脱落 | ○(比喩の語義をchunk_reasonに記録) |
| V4 | sales pitch | 提示 | ○ | ○ | ○ |

## 2. 現行7候補提示経路と既存仕様の確認結果
詳細=`CURRENT_STATE_01.md`(file:line付き)。要点: 正式経路=P7(フレーズ最大7)+W5'(単語最大5)=候補12→canonicalization(規則1〜5)→Gate→HR/フォーム(ユーザー最大3件)。旧『最大3件』=Prompt 2(AIが3件選ぶ)は新経路で未使用(残置)で、現行の『最大3件』はユーザー選定上限。**仕様と実装の矛盾は検出せず**。確認事項: ユーザー指示の『7候補』はフレーズ枠のみ(実提示は7+5)、実際のフレーズ提示は4〜6件、AI選定理由欄は画面で非表示、Human NG照合は`used_form`(一般化後の形)に対して行われるため採用時は旧NGとの整合要確認(未確認)。

## 3. 比較した方式・Promptと選定理由
詳細=`TRIAL_DESIGN_01.md`。A(統合: A_luna/A_sol/A2_sol)、B(工程分離: B_luna/B_mix)、C(C1現行P7再利用/C2塊判定+一般化1call/C3候補源拡張+C2)、D(最終案)。選定理由: ①一般化を文章生成にするとモデルが比喩語義に引きずられて名詞を核に残す・`/`で選択肢を併記する等が多発(B・C系)→**トークン分類(CORE/SLOT/DROP)+コード組立**で語の追加・併記・末尾プレースホルダを構造的に防止。②現行P7だけでは候補源が不足(C1: 1〜4件)→過剰生成との和集合(D最終71件中35件が過剰生成由来、合格率は同等: P7由来32/36・過剰生成由来29/35)。③sol(推奨系)は塊判定が厳しすぎ(A_sol 1件、A2_sol 2件)かつ3〜10倍の費用→lunaで判定・一般化、別系列(gemini)で検証。工程数を増やすこと自体は目的にしていない: C2(1call判定+一般化)は工程が少なく費用0.5円だが一般化の安定性が低い(`/`併記、冠詞変更で決定論検査に落ちる)。

## 4. 一般化・塊価値の改善結果
- 一般化(Dの最終候補のうち、Beforeが『未一般化』と判定された表現): `narrow down the source`→`narrow down`、`turned the usual steps around`→`turn something around`、`At the time of writing`→`at the time of`、`hear it out`→`hear someone out`(Beforeは22件が未一般化NG、Dは1件=hear something out)。
- 塊価値: 自由な組合せ(`confirm a clear fall`/`results suggest`/`favor one product`等)をDは除外(Before: 14件が自由な組合せNG、Dは4件)。比喩の語義区別: `blow a whistle`のchunk_reasonに『笛を吹く=危険を知らせる合図』を記録。
- 難易度優先: P7条件4・5を各Promptに逐語で維持。選べる候補のうち『難易度低め』(基本語寄りの固定表現)はD 4件/A 9件/Before 2件。`rely on`・`turn into`は易しいとして不可判定(D 1件・A 4件・Before 2件が易しい理由でNG)。
- 一般化段の単体評価(選定なし、必須一般化5例を強制通過): G2〜G5を達成(luna、改訂規則後)、G1のみ名詞`points`をCOREに残す(『減点になぞらえた比喩の語義に必要』とモデルが判断)。sol(low)でも同様で、モデル差ではなく『比喩語義と一般化のどちらを優先するか』の方針差。→ ユーザー判断事項(9節)。

## 5. Before/Afterの具体的な候補一覧と比較ページ
全候補(記事×レベル×Before/A/D、可否・理由付き)=比較ページ。必須9例の表・記事別3列比較・残NG一覧・内部評価(折りたたみ)を掲載。Fable実読用の機械可読版=`kpg01_work/results/*.json`(各方式の最終候補とログ)・`kpg01_work/judge/*.json`(別系列判定)・`kpg01_manual.py`(Sonnetの可否とNG理由)。

## 6. 残ったNG・改善できなかった理由(失敗箇所の切り分け)
| NG(D) | 失敗箇所 | 原因 | 次の一手(改善見込み自己評価) |
|---|---|---|---|
| `take a turn`(took an unexpected turn) | 一般化(組立) | 意味を担う修飾語unexpectedをDROP→語義が変わる(検証が冠詞欠落を指摘してa補完はされたが語義は戻らない) | 決定論ガード: 意味を担う修飾語(形容詞)のDROPを禁止または検証でmeaning_preserved=falseなら元のspan形へ戻す(見込み高、小改修) |
| `set a limit`(lowerを落とし下限の語義が消える) | 一般化 | 意味を担う修飾語のDROP | 同上+検証でmeaning_preserved=falseなら元のspanへ戻す(見込み中) |
| `deep image`/`point-like object`/`need an instruction manual`/`protein crystal`(自由な組合せ4件) | 選定(塊判定) | lunaがFをCに甘く判定。専門語・比喩の名詞句 | 塊判定にsol(low)を使うD_sol(未実施。Beforeの『厳しすぎ』を避けるためDでは候補源が広い)。見込み中、費用+1.5円/レベル |
| `have yet to be spoken`/`hurdle to clear`/`hear something out` | 一般化・選定 | 受動形が核に残る/単数化で不自然/somethingがsomeoneであるべき | 検証(gemini)はOK判定で通過=検証の見落とし。人称(someone/something)判定を一般化段の指示に追加、受動形は塊判定で除外(見込み中) |
| G1/G2が選ばれない | 選定(塊判定)と一般化 | 動詞+一般名詞目的語は『自由な組合せ(F)』と判定され、名詞を核に残す | **方針判断が必要**: 『一般化すれば塊(`take something away from`)として価値あり』と見るか。見込みは方針次第(ユーザー判断) |
| Before成功例の脱落(6/26)| 選定 | `Sales pitch`(ai_cha_b1b)・`take a detour`・`on hold`・`give something up`・`overlap with`・`take an unexpected turn`がDで脱落 | 候補源をBefore(現行P7)全件を必ず塊判定にかける仕様は既にあるが判定段で落ちる。判定のばらつき(同一入力で変動)。2回判定の和集合(+¥0.2)で改善見込み中 |

失敗箇所の分布(D、NG 10件): 一般化4(take a turn・set a limit・hurdle to clear・hear something out)、選定(F混入)4、受動形残り1、易しい1。**抽出段の失敗は少ない**(過剰生成で供給は確保)。主因は『塊判定(F/C境界)の判定ばらつき』と『一般化での修飾語DROP』。

## 7. QCD比較
| 軸 | 現行 | A | D |
|---|---|---|---|
| 品質(そのまま選べる率) | 39% | 79% | 86% |
| 時間(平均, 1レベル) | (現行の同段は未測定) | 約33秒(1 call) | 約55秒(4段逐次。Std/Adv並列で短縮可) |
| 量産単価(1レベル) | 既存(P7+canonicalization+gloss整合+QA。未計測) | +0.31円 | +0.98円(過剰生成0.16・選定0.18・一般化0.18・検証0.46) |
| 記事セット(Std+Adv) | - | +約0.6円 | +約2.0円(目標70円の約2.8%) |
- 既存段(canonicalization+gloss整合)を置き換えられる場合の相殺額は**未確認**(Production段の実費を本Trialで計測していない)。検証段(gemini)がDの費用の47%。thinking予算を0へ下げる案は未試行(見込み: -0.3円/レベル、品質影響は未確認)。
- **Trial費用: ¥79.1**(Cap ¥60を理由記録で¥80まで継続、¥80未満で終了): gpt-6.1-sol ¥25.4(単体一般化test¥8.2含む)、gpt-6-luna ¥21.3、gemini-3.8-flash ¥23.3、deepseek-v4-pro ¥7.5(下記)、deepseek-flash ¥1.6。Cap超過理由=最初のA/B/C(単一Prompt)で一般化が安定せず、一般化単体のPrompt改訂と構造化方式への転換が必要になったため(同一方向の反復でなく方式転換: 文章生成→トークン分類)。**費用の無駄**: deepseek-v4-pro判定1回が既定thinkingで10,995 tok出力(¥7.4)。以降はflash・非thinkingへ切替(¥0.1〜0.3/回)したため、**独立判定の対象が8/14ケースに縮小**(残りはSonnet実読のみ)。
- 使用モデル(開発評価の最新原則): gpt-6-luna(Production routingのモデル=比較基準かつ『ライン組込候補の性能確認』という例外2)、gpt-6.1-sol(最新世代の推奨系=最新)、gemini-3.8-flash(最新世代Flash、検証者=別系列)、deepseek-v4-pro(最新世代最上位、判定1回のみ)、deepseek-flash(下位系: 例外=費用Cap上の実務制約、判定者)。gpt-6-astraは未使用(費用がsolの約5倍で、Cap内で比較不能)。

## 8. Fableによる独立受入評価
未実施(Fableが実施)。Fableの実読対象: 比較ページ全候補、`kpg01_manual.py`(Sonnetの可否・NG理由と難易度『低め』印)、必須9例表。確認してほしい論点: (1) 私の『可』判定の厳しさ(基本語寄りの固定表現を『可・難易度低め』としている点)、(2) 別系列判定(寛容)との乖離、(3) G1/G2の扱い。

## 9. Production採否に必要なユーザー判断(判断候補)と採用時の影響範囲
判断候補(分類は27-3: A既判断/B承認範囲内/C独立/D真に新しい判断):
1. **D**: 学習表示用の一般化(目的語のsomething化・固定表現の後続名詞句の除去・`display_form`と`source_span`の分離)を新しい許容ルールとして採用するか(OPEN-349と同系統。承認済み『本文一致』仕様の緩和ではなく並設)。
2. **D**: 提示候補が7件に満たなくてもよいか(現行も満たしていないが、Dは平均5件)。
3. **D**: G1型(比喩語義のある動詞+名詞)の扱い=一般化を優先して`take something away from`にするか、語義保持を優先して現行のままにするか。
4. **B/Fable判断**: 追加Trial約¥5(意味破壊ガード・FIX失敗時破棄・塊判定の2回和集合・verify予算の削減)の費用(Cap ¥80消化済みのため追加Capが必要)。
5. **D**: 費用+約¥2/記事セット(最大)の容認(既存段置換での相殺は未確認)。

採用時の影響範囲(実装するならOpus条件A→実装):
- 共通(X/Y/Z・Std/Adv): 新段は`er119_kp_candidates_01._gate_chain`のcanonicalization(+gloss再整合)の**置換または前置**。docの形式(`used_form`/`japanese_gloss`/`item`)を保てば、外側retry・補完(backfill)・resume(保存docのAPI 0再利用)は変更不要。補完は同じ`_gate_chain`を通るため自動で新段が適用される。
- Validator: `source_span`の本文一致(1〜5語)は維持。`display_form`用に`kpg01_validate`相当の別validatorを追加(核語の語形違い・プレースホルダ規則・末尾スロット除去)。CMU辞書Gateは`used_form`に対する既存post-canon Gateを流用。
- Family固有: Zは人称整合(person_repair)・SRC D1が`_gate_chain`内に入るため新段との順序を要設計。Zの会話体・人称(my/your)はSLOT_POSS系で扱えるが、Z実走のevidenceは未取得(本TrialのZはメロスa2の1ケースのみ)。
- HR/フォーム: 候補表示は`used_form`+gloss(AI選定理由は非表示)で現行と同じ。Human NG照合は新`used_form`基準になるため、過去NG履歴との照合(旧used_form vs 新)の整合確認が必要(未確認)。
- SSOT/runtime evidence/Git: CURRENT_SPEC KP節・DECISION_LOG・OPEN(OPEN-349/474関連の整理)・X/Y/Z×Std/Adv の正式経路runtime evidence(共通経路の実走)が必要。flag名を決める場合は11-7の限定例外5条件(既定OFF・DefaultOffIsolation test)を満たすか、Offline Trial→VALIDATED→正式採用の順。
- 副作用: Before成功例26件中6件(23%)がDで脱落(判定ばらつき)。採用前に『Before候補を必ず塊判定にかける+2回判定の和集合』等で是正する追加Trialを推奨。

## 付: 限界・未確認
- 独立判定は8/14ケースのみ(コスト事故のため)。Sonnet実読は全14ケース。Fable再読が最終。
- 未使用記事のBeforeは1ケース(ignobel_a2)のみ再現できた(他はProduction Gate連鎖の簡易再現でcanonicalization不合格)。moon(X)は未実行。
- D_sol(塊判定にsol)は未実行。Zの会話体は1ケース。生成の乱数ばらつき(同一入力の再実行差)は測っていない。
- 本文一致Gate・CMU・Redundancy QA・Human NGは本TrialのDに組み込んでいない(Production統合時に既存Gateを維持する前提)。
