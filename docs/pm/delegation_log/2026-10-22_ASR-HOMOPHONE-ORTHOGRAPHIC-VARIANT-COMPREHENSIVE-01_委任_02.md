FABLE-DELEGATION-MARKER: ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-委任_02-20261022

管理ID: ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01 委任_02(OPEN-459)。Opus必須レビュー(条件付きGO、must-fix P-01〜P-06)の是正と、B不具合3件の最小修正(自律)、VALIDATED判定のための再検証。費用0(API禁止。保存音声・ローカルWhisperのみ)。並行agent: KP-OUTER-RETRY-SAME-PHRASE-FIX(er105/er003を編集中)。共有ファイル手順厳守(`git status`→再Grep→自分の行→即commit)。

## 0. 読む・保存
- 委任_01成果 `docs/research/ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01/{INVESTIGATION_01,PATTERN_CATALOG_01,DESIGN_PROPOSAL_01}.md`、`er109_asr_orthographic_equivalence_01.py`(+test)、`er109_machine_pairs_eval_01.py`、集計json。ユーザー原文 `docs/pm/delegation_log/2026-10-22_ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01_USER.md`。
- Opusレビュー全文(§5)を `.../OPUS_REVIEW_MANDATORY_01.md` へ逐語保存、`docs/pm/OPUS_FINDINGS_LEDGER.md` に OF-AHO-P-01〜12 登録。T-0保存 `docs/pm/delegation_log/2026-10-22_ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-COMPREHENSIVE-01_委任_02.md`(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、末尾から探索、本文先頭marker `FABLE-DELEGATION-MARKER: ASR-HOMOPHONE-ORTHOGRAPHIC-VARIANT-委任_02-20261022` 一致で確定)。

## 1. Fable決定
- Opus条件付きGOを採用。**P-01〜P-06はVALIDATED前に必須**、P-07〜P-12も実施。「新規誤同値0」の主張はP-05再測定まで保留。
- **B不具合3件(B-1 複合序数の最終ゲート値DIFF/B-2 1語・短文でratioゲートが承認済み同音救済より先行/B-3 `60 %`)は、Opus F1のとおり「B単独の最小修正」として既存承認仕様の不具合修正(自律可)で実施**。条件: 既存の単一関数を再利用(`val._convert_compound_ordinal_words`、`homophone_arpabet_equivalent`(stress付き))、B-2の迂回は「token数同一・差のある全位置が既存同音判定でTrue・entityでない・同形異音語でない(P-03)」をすべて満たす場合のみ。NG→PASS方向のみ、A/B/Cも同じ改善を受ける(27-7上、挙動変化は「不合格→合格」のみでProduction品質Gateの緩和ではない旨をSSOTに明記)。
- er109(新規救済範囲C/C-KP)は**本委任ではProductionへ配線しない**(既定OFFの11-7例外配線も次委任でFable判断)。オフラインで保存データ全件のON/OFF比較を行う。
- A/B/C波及は(a)呼出点共通を候補として提示(ユーザー採用判断材料)。

## 2. 作業
A. er109の是正: P-01 stressは2値(有/無)で比較、P-02 弱形のみの一致は非同値(are/or、we're/were、our/are)、P-03 同形異音語の保護(canonical語が強勢母音または子音の異なる複数読みを持ち、ASR語が別綴りで一部読みとしか一致しない→非同値)、P-04 曖昧略語(St/Dr/Mt/#)fail-closed・大文字略語のCMU展開variant(tv→television)除外、P-07 数・記号spanに混ざる語は数読み語彙に限定、P-08 警告方針(決定的規則=警告なし/否定語同音・代表発音以外variantのみ一致=PASS_WITH_WARNING+事後試聴)と監査項目(span毎の一致variant・代表か・stressモード・同形異音フラグ・flag状態・層version)、P-09 漏れ(`March 5`序数読み、`$5 million`、`$5.50`、`24/7`、ローマ数字、-ise/-yse)をC/Eへ分類記録、P-06 最終ANDゲートの扱いは「値ガード・否定差は実行し、各DIFFがer109の同値spanで説明できる場合だけ解除、Secondary分岐(:599)も同基準」を設計に明記(配線は次委任)、P-10 HR Lock済みsegmentの明示再判定手順(API 0、自動解除なし)を設計に記載、P-11 11-7例外条件(flag OFFで到達不能・DefaultOffIsolation test)を配線設計に記載。
B. **敵対的負例の再構築(P-05)**: CMU辞書全体から「代表発音以外のvariant・弱形・stress除去でしか交わらない綴りの異なる語の組」全数、同形異音語の組、曖昧略語の誤展開、数を介したoronym(`for tea`/`40`)を機械生成し、是正後er109で誤同値0を測定。誤同値が出たら1件ずつ真の同音か分類(真の同音なら正例へ、そうでなければ是正)。正例(既存機械生成ペア+カタログ正例)も再測定して同値率の低下を報告。
C. B-1/B-2/B-3の最小修正: 該当Production関数(val、`er078_asr_value_guard_01.py`等)を修正+test(Z `seize`/`sees`の保存事例が新判定でPASSになること、`seize`/`cease`はNGのまま、`twenty first`/`21st`、`60 %`、1語KPのlead/led型は非同値)。非KP 12,096行の前後比較(NG→PASSのみ、PASS→NG 0)。全回帰(自分起因新規失敗0。他agentの編集中ファイル由来は切り分けて記録)。commit分離(B修正は独立commit)。
D. 保存データ全件(4,877行、A/B/C/X/Z)のON/OFF比較(オフライン、er109を直接呼ぶharness。Productionへは未配線): PASS→NG 0件の確認、NG→PASS全件列挙(Family別、A/B/C分を分離)、新たにPASSになる保存wavをローカルWhisperで再転写して裏付け(API 0)、ユーザー指摘NG音声全件(問題音声21件+take part B+Melos母音誤読+byUs blurt等)で新規PASS 0。新たにPASSになるsegmentの試聴リスト(`user_test/aho_new_pass_listen_01/index.html`、既存ページ体裁流用、再生検証)。
E. SSOT: OPEN-459を`B_FIXED_C_VALIDATION_PENDING_FABLE`等の正確なStatusへ(B修正=FIXED_RECORDED、C=オフライン検証結果とVALIDATED候補か否かを明記。**VALIDATEDの宣言はFable**)。B修正はCURRENT_SPECの該当行(同音救済・値ガード)へ「不具合修正」として追記、DECISION_LOG短いエントリ。REPORT_LEDGER 1行。`docs/pm/RESULT_PACKET_AHO2.md`(4行+判定整合行)。commit(自分のファイルのみ)、secret_scan hits=0、push。

## 3. 報告
ユーザー向け10項目(原文§7)に対応づけて: パターンと対策状況(A/B/C/D/E件数の更新)、B修正内容と証拠、保存データの偽NG改善件数(Family別)、偽PASS非増加の証拠(敵対的負例の結果)、Opus是正状況(P-01〜12)、適用範囲、Wiring状況(未配線・既定OFF)、費用、SSOT/Git、ユーザー判断が必要な新仕様(Opus§5の7項目を採用判断材料として整理)。

## 5. Opusレビュー全文(逐語保存用)
---
## 1. 総合判定: 条件付きGO(must-fixあり)

全体の構造は妥当です。
- 純関数の共通層を1つ作る
- `classify_asr_match`の末尾で、既存判定が不合格のときだけ呼ぶ(NG→PASS方向のみ)
- 欠落・付加・CMU未登録はfail-closed(同値にしない)
- 既存のCMU取得・contraction表・er094を再利用する
- 追加API 0

ただし実装の判定基準に、**発音が異なるものを同値にしてしまう経路が少なくとも4系統**あります(CMU辞書`.venv\Lib\site-packages\cmudict\data\cmudict.dict`で確認済み)。さらに、**負例評価が判定基準と循環しているため、「新規誤同値0」は安全性の証拠として弱い**です。must-fix(P-01〜P-06)を解消し、敵対的な負例で再測定するまで、VALIDATEDとは言えません。

## 2. ユーザー観点(1)〜(7)

1. **漏れ: 条件付き。** 主要な系統は網羅されています。未カバー(残存偽NG)は次のとおりです。
   - 月名の後の日付の序数読み(`March 5`→fifth)
   - `$5 million`(語順が入れ替わる)
   - `$5.50`↔`five fifty`
   - `24/7`、`9/11`
   - KPでのローマ数字(`World War II`↔`2`)
   - CMU未登録の英綴り(-ise/-yse)
2. **不一致になる箇所: GO。** INVESTIGATION §2の地図は正確です。以下は実コードで確認しました。
   - ratioゲートが同音判定より先に走る: val:1133とval:1193
   - 既存同音判定はstress付き(`er008...homophone_en.py:91-92`)
   - P1/最終ゲート: er078:445-460/:480-483
   - Secondaryの保護差チェックが許容判定より先: :599
   - 追加の発見: Store再利用・X引継ぎ(`er019...:305`)は`segment_id`を渡さないため、Tier1も効いていません。er109はrole非依存なので、これも結果的に解消します。
3. **既存同音救済との整合: 条件付き。** 「既存1:1同音と同じ単位」と書かれていますが、実装は**stressを除去し**(`er109:165`)、**stopwordにもany-variantを適用**しています。既存より緩いので、P-01/P-02で整合させてください。
4. **偽NG削減: GO。** 保存データで24行/21segment、HR/STOPは3segment。機械生成の正例も大幅に改善しています。残りは上記の漏れとE(CMU限界)です。
5. **誤PASS: NO(現状)。** 次の実例があります。
   - weak formの一致: are(2)=ER0、or(2)=ER0 → `are`↔`or`が同値になる
   - stress除去: billow `B IH1 L OW0`、below `B IH0 L OW1` → 同値になる
   - stress除去+語境界越え: `for tea`↔`40`
   - 同形異音語の別読み: lead/led、desert(2)/dessert、wind/wined、bass(2)/base、read/red
   - 曖昧な略語: `St. Louis`↔`Street Louis`、`Dr.`↔`drive`
   - CMUの変種: tv(2)=television
   - 負例生成器(`er109_machine_pairs_eval_01.py:277-317`)は「stress除去後の全variantで交わらない語」だけを置換先に選びます。これはer109自身の判定基準と同じなので、上記の系統は構造上検出できません。
6. **経路の漏れ: 概ねGO。** 3票・KP再利用(`er104_kp_vote_reuse_01.py:123`の本番adapter経由)・X引継ぎ・retry/fallback/resumeは、すべて`classify_asr_match`を通ります。Zの`er063:1047`は差分表示だけで、判定には使っていません。要対応は2点です。
   - Secondary分岐(:599)は、許容判定より前に値ガードを見ます。新しいbasisを考慮する形に直す必要があります。
   - 既にHUMAN_REVIEW_LOCKEDのsegment(Z `seize`)は自動では再判定されません。
7. **API・量産コスト: GO。** 追加API 0、計算が走るのは不合格時の約1.2msだけです。ただし削減効果には限りがあります。
   - Azure呼出が減るのは非KPだけです。KPは`vote_required`で常にSecondaryを呼ぶため(er078:471-476)、減るのは割れたときのWhisperと再生成です。
   - 単価への影響は小さいプラスです。

## 3. Q1〜Q8・F1〜F6

**Q1(any-variantか代表発音か): 条件付き。** どちらも不採用とし、次の組合せを推奨します。
- stressは「強勢あり/なし」の2値で比較する(ok `OW1 K EY1`とokay `OW2 K EY1`は同値を維持、billow/belowは非同値)
- 一致した読みに強勢母音を含まない場合(弱形のみの一致)は同値にしない
- 同形異音語の保護(P-03)
- 大文字略語は「文字読み+代表発音」だけを使う(tv→televisionを排除)

**Q2(数詞↔同音語、否定語の同音):**
- `to/2`、`for/4`、`won/1`: GO。承認済みのTrack Bと既存basis `HOMOPHONE_MATCH_NUMBER_EXCEPTION`と同じ方向です。
- `no/know`: 原則どおり同値でGO。no・knowはどちらも`N OW1`の1発音だけで曖昧さがありません。ただし警告ラベル+事後試聴リスト、P-06の照合、ユーザー採用材料への明記を条件とします。

**Q3(配線位置と順序): GO。** 末尾の配置で、Tier1・contraction・CS/M1/Tier3の責務は壊れません。Tier1より前に置く必要はありません。KP票では、er109によるPrimaryの合格はOpenAI自身の票として数えてよく、Secondaryによる救済扱いにはなりません。

**Q4(語境界の扱い):**
- 語だけのspan: GO。oronymの除外は保守的で妥当です。
- 数・記号を含むspan: 条件付き。語境界を越えて連結できてしまいます(P-07)。

**Q5(略語・記号表と漏れ): 条件付き。**
- `St/Dr/Mt/#`のように複数の展開を持つ曖昧略語はfail-closedにします。許すのは、候補が同じ語の活用違いだけの場合(degree/degrees、minute/minutesなど)です。
- 漏れは観点(1)の一覧のとおりです。

**Q6(警告と監査): 条件付き。**
- 決定的な規則(数・記号・綴り連結)は警告なし。既存のNUMERIC/Track Bと同じ扱いです。
- 否定語の同音、および代表発音以外のvariantでしか一致しないspanは、PASS_WITH_WARNING+事後試聴にします。
- 監査に追加するもの: spanごとの一致したvariant(代表かどうか)、stressモード、同形異音フラグ、flag状態、層のversion。

**Q7(経路の網羅): GO(観点(6)の注記つき)。** A/B/CはF2を参照。

**Q8(費用): GO(観点(7)のとおり)。**

**F1(Bの修正手段): 「B単独の最小修正」を推奨し、既存承認仕様の不具合修正として自律実施可とします。** 理由: er109から切り離せるので、Trial効果の帰属が明確になり、①②とも独立します。
- B-1: 値ガードの値atomで、`val._convert_compound_ordinal_words`を再利用して複合序数を扱う。再実装はしない。
- B-3: `%`前の空白を共通の正規化で吸収する。
- B-2: ratioゲートを迂回してよいのは、次をすべて満たす場合だけにします。
  - token数が同じ(1:nはer094の承認条件)
  - 差のある全位置が既存の`homophone_arpabet_equivalent`(stress付き)でTrue
  - entityでない
  - 同形異音語でない(P-03)
  
  それ以外はratioゲートを変えません。B-2が不具合だとする根拠: despaced判定には「短いKey Phraseではratioが不安定なので先に判定する」という既存コメントがあり(val:1064-1066)、短文を救済から外す意図は読み取れません。
- 副作用: 非KP最終ゲートの偽NGが減る方向だけです。A/B/Cも同じ改善を受けます(NG→PASSのみ)。

**F2(A/B/C共有部): (a)呼出点共通を推奨。** 理由は次のとおりです。
- 安全性はX/Zと同じで、PASS→NGはありません。
- (b)のopt-inにすると、run単位のscope状態が要ります。PNAPの前例のとおり、共有Storeの再利用で判定が食い違い、別途ブロックが必要になります。
- ただし27-7の「対象を勝手に拡張しない」に従い、A/B/Cの影響件数(保存データで18行)を示して、ユーザー採用判断の一項目にしてください。(b)を選ぶ場合も、呼出点ごとのパッチではなく、既存のrun-scope方式(`er103...is_active_for_run`)で実装してください。

**F3(否定語・数詞の同音化): 論理は妥当です。** 値・否定の保護の目的は、音声の内容誤りを捕まえることです。転写がcanonicalと音素列で完全に同一なら、聴者に差は生じません。この論理が崩れるのは、CMUの一致が実際の同一発音を意味しない場合だけです(weak form・stress・同形異音)。したがってP-01〜P-03が前提条件です。

**F4(any-variantの誤PASS余地): あります(観点(5)の実例)。** 「内容語は代表発音、機能語はany」という折衷は不可です。are/orの衝突はまさに機能語側で起きており、内容語を代表発音に絞ると、既存の同音救済と整合しない正例の取りこぼしが出ます。Q1の組合せを推奨します。

**F5(B-2の安全性とseize/sees): CMUで確認しました。**
- seize・sees・seasはいずれも`S IY1 Z`で同一。ceaseは`S IY1 S`で異なるため、NGのまま残ります。
- 全位置が同音のときだけ迂回するので、幻聴(hallucination)が通ることは構造上ありません。
- 新たなリスクは、1語KPでの同形異音です(lead→ledなど)。P-03で塞いでください。

**F6(VALIDATEDの十分条件): 以下を満たせば、追加のTTS/ASR APIは不要です。**
1. P-01〜P-07を適用したうえで、正例を再測定する。
2. CMU全体から作った敵対的負例で、新規誤同値0。誤同値が出た場合は、1件ずつ真の同音か分類する。中身は次のとおり。
   - 「代表発音以外のvariant・弱形・stress除去でしか交わらない、綴りの異なる語の組」の全数
   - 同形異音語の組
   - 曖昧略語の誤展開
   - 数を介したoronym
3. 保存4,877行を全件、flag ON/OFFで比較する。PASS→NGが0件であること、NG→PASSを全件列挙すること(A/B/C分を含む)。
4. 新たにPASSになる保存wavをローカルWhisperで再転写し、裏付けを取る(API 0)。
5. 既知の問題音声は21件に限らず、ユーザーが指摘したNG音声の全件で新規PASS 0。
6. 全Regression+DefaultOffIsolation testがPASS。
7. 新たにPASSになる保存segment(約21件)の試聴リストを作り、採用判断の材料にする。

## 4. 指摘事項(OF-AHO-P-NN)

**Major(VALIDATED前に必須)**
- **P-01** stressを除去せず、2値で比較する(billow/below、for tea/40)。
- **P-02** 弱形同士だけの一致は不可(are/or)。we're(3)`W ER1`/were、our(3)/areも敵対検証の対象に含める。
- **P-03** 同形異音語の保護。canonical語が強勢母音または子音の異なる複数の読みを持ち、ASR語が別綴りで、そのうち一部の読みとしか一致しない場合は非同値にします(または警告)。適用範囲はer109とB-2で新たに到達可能になる経路だけで、既存の本文同音救済は変えません。
- **P-04** 曖昧略語(St/Dr/Mt/#)はfail-closed。大文字略語に付くCMUの展開variant(tv→television)は除外する。
- **P-05** 負例が循環しているので作り直す(F6の2)。「新規誤PASS 0」の主張は再測定までは保留です。
- **P-06** 最終ANDゲートを丸ごとskipしない。値ガードと否定差は実行し、各DIFFがer109の同値spanで説明できる場合だけ解除します(Tier1 diff_anchoredでの否定の二重防御と同じ前例)。Secondary分岐(:599)も同じ基準にする。

**Minor(推奨)**
- **P-07** 数・記号を含むspanに混ざる普通の語は、数の読み語彙(and/point/percent/dollars/o'clock等)に限る。それ以外はfail-closed。
- **P-08** 警告方針(Q6のとおり)と監査項目の追加。
- **P-09** パターンの漏れ(観点(1))を、CかEに分類して記録する。
- **P-10** HR Lock済みsegmentを救済するには、明示的な再判定手順(API 0)が要る。自動解除はしない。
- **P-11** 11-7例外: 新basisとSecondary分岐の変更は、flag OFFでは到達不能にし、testで固定する。新ラベルを使う側の確認も行う。
- **P-12** B修正は既存の単一関数を再利用する(F1の条件)。

## 5. ユーザー判断が必要な新仕様(採用判断の材料)

1. er109の採用。KP/Whisper票への数の表記差の適用を含みます(Tier1をKPに適用しないという承認済み仕様の、範囲拡大にあたる)。
2. 否定語の同音(no/know)を、警告つきで同値扱いにすること。
3. er109の同値を最終ANDゲートの承認済みbasisにすること(span単位で解除)。
4. A/B/Cへの波及を(a)許容するか、(b)opt-inにするか。
5. 記号・曖昧でない略語・年代・時刻・セント・年読みの閉じた読み表。
6. 警告・事後試聴の方針。
7. (任意)oronym(ice cream/I scream)を除外したままにすること。

自律対応でよいもの(判断不要): B-1/B-2/B-3の修正、P-01〜P-04の安全側の絞り込み。いずれも承認済み原則の範囲内で狭める変更です。

## 6. 量産コスト・品質影響の見積

- コストの見積(追加API 0、Azure呼出・再生成は減る方向のみ)は妥当です。ただしAzureの削減は非KPに限られ、規模も小さい(偽NGは全attemptの約0.5%)。
- 品質面では、HR/STOP 3segment相当の解消は妥当です。誤PASSの見積は、P-05で再測定するまで「未確認」として扱ってください。
---