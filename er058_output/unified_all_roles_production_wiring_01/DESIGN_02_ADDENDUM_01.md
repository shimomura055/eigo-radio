# DESIGN_02_ADDENDUM_01: DESIGN_01へのOpus条件Aレビュー反映(追補)

管理ID: `ASR-TTS-UNIFIED-ALL-ROLES-PRODUCTION-WIRING-01` 委任_02a(2026-10-15)。性質: 設計文書のみ。Productionコード/Prompt/flag/test/SSOT本体は無変更、有料API 0、費用JPY0。到達上限=`DESIGN_02_READY`。
根拠: Opus条件Aレビュー原文=`OPUS_REVIEW_A_01_VERBATIM.md`(逐語保存、本書では所見IDと要旨のみ参照)。基準設計=`DESIGN_01.md`(commit 3953de4ff)。DESIGN_01と本書が食い違う場合は本書が優先する。
Production採用はユーザー承認済み(管理ID全体)。ただしU1/U2は未決のため、暫定は現行維持(§11)。

## 0. Fable判断表

| 所見 | 判断 | 理由(1行) | 反映節 |
|---|---|---|---|
| OF-AUW-01 | 採用 | 値ガードの内部矛盾(AMBIGUOUSの扱い)を5値意味論で解消。誤NG側の歯止め | §1 |
| OF-AUW-02 | 採用 | 共有module変更の波及を作業branch+単一mergeで1操作revert可能にする | §2 |
| OF-AUW-03 | 採用 | 引継ぎ・再利用経路が統一判定を素通りする穴を判定点J11で塞ぐ | §3 |
| OF-AUW-04 | 採用 | 呼出点の網羅漏れを手書きGrepでなくimport graph静的監査で担保 | §3 |
| OF-AUW-05 | 採用 | Melos regressionの転写欠損1件を実Azure1回で補い「12/12」を成立させる | §10 |
| OF-AUW-06 | U(U2) | LR後v1のSecondary必須化は未決事項の変更に当たる | §5, §11 |
| OF-AUW-07 | 採用 | 合意誤読の判定式を明文化しMelos転写で単体test化 | §5 |
| OF-AUW-08 | 採用(R+) | JA受理集合の縮小をDECISION_LOGに記録し、表記揺れ確認は2エンジンで維持 | §6 |
| OF-AUW-09 | 採用 | 費用見積を秒数ベースにし、COST_GUARD再校正または現状無効を明記 | §7 |
| OF-AUW-10 | 採用 | Secondary障害は技術STOP(再実行で再開可)+run単位circuit breaker | §4 |
| OF-AUW-11 | 採用 | testはProduction同一前処理後の原稿で行い、PASS→NG全件確認を受入基準に | §10 |
| OF-AUW-12 | 確認済み→R | 3回への揃えはユーザー決定の逐語なし(Trial値max_attempts=2の継承)。3回へ揃える | §9 |
| OF-AUW-13 | 採用 | revert予行・旧test再実行・新キー後方互換testをGate 4に入れる | §2 |
| OF-AUW-14 | 採用(記録) | EN PhraseListはV04 L69からの逸脱理由を記録して維持 | §6 |
| OF-AUW-15 | 採用 | 試聴リストはlegacyも単独HTML、途中STOP時も出力、引継ぎ時に警告継承 | §8 |
| OF-AUW-16 | 記録のみ | OPEN候補。本タスクでは実装しない | §12 |
| OF-AUW-17 | 採用 | 新ラベルの下流allowlist/count Grep手順を追加 | §6 |
| OF-AUW-18 | 記録のみ | OPEN候補。本タスクでは実装しない | §12 |
| U1(C-A5/A6) | ユーザー判断 | 既存の承認記載が矛盾。暫定=現行維持 | §11 |

## 1. 値ガードの意味論(OF-AUW-01採用)

### 1-1. 5値の定義
入力: 原稿側文と転写側文。各文から「値atom」(数字、漢数字、かな数詞、英数詞、単位・助数詞を含む)を位置順に抽出し、原稿側と転写側を位置対応させる。

| 値 | 定義 |
|---|---|
| NO_VALUES | 両側とも値atomが無い。値ガードは判定に関与しない(通常のtext比較へ) |
| EQUAL | 対応する全atomが、値化できて値と単位が同じ(表層が違っても可。例 二十歳=20歳)、または両側表層が完全に同一 |
| DIFF | (a) 対応位置の両側atomがともに値化でき、値または単位が異なる、または (b) 片側の値atomに対応する相手側spanに数字・数詞・かな数詞のいずれも無い(脱落・挿入) |
| AMBIGUOUS | 位置単位で、両側の表層が異なり、かつ値か普通語か確定できない(例 十分=10分/充分)。同一表層ならEQUAL |
| UNKNOWN | 構文解析不能、または片側のみ値化できた(相手側が値か語か判別不能)。値ガードでは結論を出さず、既存protected_check・読み一致判定へ委譲 |

複数atomがある場合の集約優先順位: DIFF > UNKNOWN > AMBIGUOUS > EQUAL > NO_VALUES(一つでもDIFFがあれば全体DIFF)。

### 1-2. 判定表(要約)

| 例(原稿→転写) | 値 | 扱い |
|---|---|---|
| 150人→140人 | DIFF | NG_PROTECTED(Secondary不呼出、次slot) |
| 一人で→ひとりで / 一つ→ひとつ | EQUAL(同読み数詞変種辞書で値化) | PASS系 |
| 二十歳→はたち / 二〇二六年→2026年 / 1万2000人→一万二千人 | EQUAL | PASS系(不規則読みは警告対象) |
| 数十人→十数人 | DIFF(値範囲が異なる語) | NG_PROTECTED |
| 十分待ちました→10分待ちました | AMBIGUOUS | P3としてSecondaryを呼ぶ(1-3) |
| 十分な→充分な(別箇所に差分あり) | AMBIGUOUS+別差分 | 別差分側の判定が優先。AMBIGUOUSは単独で救済しない |
| 3分の1→3分の1(同表層) | EQUAL | PASS系 |
| 3分の1→1/3 など構文が合わない | UNKNOWN | 既存protected_check・読み一致へ委譲 |
| EN: "one"脱落/挿入 | DIFF(b) | NG_PROTECTED |
| EN: "for"→"4" | AMBIGUOUS(位置単位、表層差) | P3 |
| EN: Tier1が片側のみ構文失敗 | UNKNOWN | 既存protected_check・読み一致へ委譲 |

### 1-3. AMBIGUOUSの処理(DESIGN_01の矛盾の解消)
- AMBIGUOUSはP1(保護差)ではなくP3(Secondary確認要)として扱う。Primary NG扱いでSecondary 1回を呼ぶ。
- Secondary転写が原稿と同一表層のときだけPASS_WITH_WARNING(ラベル`NUMERIC_AMBIGUOUS_SURFACE`、人が試聴)。Secondaryも異表層ならNGとして次slotへ。
- 最終ANDゲート(値ガード)は、承認済みのequivalence(`HOMOPHONE_MATCH_NUMBER_EXCEPTION`、Tier1 diff-anchored、読み一致)で既にPASSと確定した結果を再否定しない。再否定が起きると承認済み救済が値ガードで無効化されるため。**(2026-10-25 OPEN-517で上書き・JA-ASR-FALSE-NG-ROOT-CAUSE-01 委任_07A)**: 本項のうち`読み一致`(READING_MATCH)は再否定しない対象から**外す**(OF-AUW-01のこの部分はFable採用でユーザー個別承認が無く、`CURRENT_SPEC.md:2855`・ユーザー原文L97『承認済み根拠にも値・否定の最終確認』と矛盾する不具合=11-8 T1のため撤回)。READING_MATCHのPrimary PASSにも最終ANDゲート(値DIFF/否定差=NG_PROTECTED、AMBIGUOUS=P3降格)を適用する。元の理由『承認済み救済が値ガードで無効化される(誤NG防止)』は、かな書き数詞の表記統一(F2。`kana_unify`、READING_MATCH PASSの最終ゲートのみ)で手当てした。他の承認根拠(`HOMOPHONE_MATCH_NUMBER_EXCEPTION`・Tier1)は本項のまま。詳細=`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPEN517_APPLY_RESULT_01.md`。

### 1-4. 擬似コード
```
def value_guard(src, hyp, lang):
    A, B = extract_atoms(src, lang), extract_atoms(hyp, lang)
    if not A and not B: return NO_VALUES
    pairs, parse_ok = align(A, B)          # 位置対応
    if not parse_ok: return UNKNOWN
    res = []
    for a, b in pairs:
        if a is None or b is None:         # 脱落・挿入
            res.append(DIFF if no_numeral_span(partner_span) else UNKNOWN)
        elif a.surface == b.surface: res.append(EQUAL)
        elif both_valuable(a, b):
            res.append(EQUAL if (a.value, a.unit) == (b.value, b.unit) else DIFF)
        elif one_valuable(a, b): res.append(UNKNOWN)
        else: res.append(AMBIGUOUS)
    return aggregate(res)   # DIFF > UNKNOWN > AMBIGUOUS > EQUAL
```
UNKNOWNは値ガードで勝手に決めない。既存の判定(protected_check・読み一致)の結果をそのまま使う(新規に厳格化も緩和もしない)。

### 1-5. DESIGN_01の改定箇所
- :282 P1の列挙から「値AMBIGUOUS(未解決)」を外し、P1=値DIFF/否定差/JA否定マーカー差。AMBIGUOUSはP3(Secondary呼出)へ。
- :361 「AMBIGUOUS→未解決=保護差扱い(Secondaryには回さない)」を「AMBIGUOUS→P3。Secondary転写が原稿と同一表層ならWARNING、それ以外はNG」へ改定。
- :381 は1-3に整合する記述として維持。「10分/十分」はP3でSecondaryを呼ぶ旨を明記。
- :395 5a行の「Secondary不呼出」を「P3としてSecondaryを呼ぶ。ASR転写`10分`のままではPASSせず、原稿同一表層のEXACTのみWARNING」へ改定。

### 1-6. test追加パターン
一人で/ひとりで、一つ/ひとつ、二十歳/はたち、二〇二六年/2026年、1万2000人/一万二千人、数十人、十数人、十分な/充分な(別箇所差分あり)、3分の1、EN "one"脱落/挿入、"for"→"4"、Tier1片側構文失敗。各パターンで5値のどれになるか、およびP1/P3/PASSの結果を期待値として固定する。

## 2. ロールアウト(OF-AUW-02, 13採用)
- 作業branch `feat/auw-unified-asr-01` 上で委任_02b〜05を進める。Integration・Regression全PASS後にmainへ1回だけmergeする。revert単位=そのmerge 1個。
- registry・ページ節はEN配線と同段(委任_03)で入れる。`_is_number`およびJA数字分岐(`_DIGIT_RE`)の変更は、配線と同じcommitに含める(単独先行で入れない)。
- Gate 4で次を実施: (1) `git revert --no-commit` の予行(結果は破棄)、(2) 旧testの再実行、(3) 新キー(新ラベル・新フィールド)に対する後方互換test(旧reader/旧集計が新キーで壊れないこと)。

## 3. 判定点J11「引継ぎ・再利用」とimport graph静的監査(OF-AUW-03, 04採用)
### 3-1. J11
- 対象: `er019_family_x_validation_inheritance_01.py:180-227` のように既存音声・保存転写を再利用する経路。
- 処理: 保存転写に対して最終ANDゲート(値ガード+protected_check)をAPI 0で再適用し、WARNINGを再導出する。ASR結果を丸ごと信用する旧経路を、統一判定の入口経由に置換する。
### 3-2. 静的監査
- entrypoint `er019 / er063 / er026 / er012_b / er013 / er012_e / n3_tts` から到達できるmodule内で、`transcribe|classify_asr_match|classify_ja_asr_match|val.evaluate_attempt|evaluate_attempt_*` の全呼出を列挙し、allowlist(統一判定の内部、およびtest)に無い呼出が1件でもあればFAIL。allowlist方式により、手書きの呼出点一覧(DESIGN_01 §3.1)の網羅漏れを機械的に検出する。

## 4. Secondary障害処理(OF-AUW-10採用)
- HR_TECH(技術理由の人間確認)をLock状態に追加しない。Secondary障害は「技術STOP(再実行で再開可・承認不要)」として扱い、PASS扱いにしない。
- run単位でcircuit breakerを設ける(連続障害でそのrunのSecondary呼出を止め、技術STOPへ)。
- Secondaryの失敗結果はキャッシュしない(重複API防止のキャッシュ対象は成功結果のみ)。

## 5. LR(OF-AUW-07採用、OF-AUW-06=U2)
- 合意誤読: 両エンジン(PrimaryとSecondary)のASR側の語が一致する、またはARPAbet距離が閾値以下の場合を「合意誤読」と定義。Melos転写を使った単体testで固定する。
- OF-AUW-06はU2(§11)。暫定: 暫定A2のみ現行`force_secondary`を維持。B1は統一判定+`LR_REWRITTEN`をWARNINGとして扱う。

## 6. JA受理集合・EN PhraseList・新ラベル(OF-AUW-08 R+, 14, 17)
- OF-AUW-08(R+): JA UNCERTAIN経路の縮小をDECISION_LOGに記録する予定(本タスクでは記録文案のみ。SSOT本体は委任_07)。`ORTHOGRAPHIC_VARIANT_CONFIRMED`はPrimary#1+Secondary#1の2エンジン確認で維持し、testで固定する。
- OF-AUW-14(記録): ENのPhraseListはV04 L69の記載から逸脱するが維持する。逸脱理由(学習対象語彙の保護)を記録。
- OF-AUW-17: 新ラベル(`NUMERIC_VALUE_EQUIVALENT_MATCH`、`NUMERIC_AMBIGUOUS_SURFACE`等)について、下流のallowlist/count集計(PASS系ラベルの許可リスト、ラベル別件数)をGrepで洗い出し、全箇所を更新する手順を委任_03/04のチェックリストに入れる。

## 7. 費用(OF-AUW-09採用)
- `est_jpy`は秒数ベース(音声秒×単価)で算出する。COST_GUARDを再校正するか、「現状無効」と明記する。
- 委任_06前に `attempt_history` のNG分布から1記事あたりの増分費用を試算し、15-9(目標70円/記事セット)と照合する。DESIGN_01の約JPY8見積は、この試算で更新する。

## 8. 試聴リスト(OF-AUW-15採用)
legacy(Family A/B/C)でも単独HTMLを出力する。runが途中STOPした場合も、それまでのWARNING分を出力する。既存音声の引継ぎ時は、元のWARNINGを継承して表示する。

## 9. OF-AUW-12の確認結果
前回確認済み: C-B(Key Phrase 3回化)について、ユーザー決定の逐語は見当たらず、Trial値`max_attempts=2`の継承にとどまる。結論=R(3回へ揃える)。`DESIGN_01.md`:414のC-B行と`APPLICABILITY_MATRIX_01.csv`のX-B1-06行を「R(3回へ揃える)」へ修正済み(本コミット)。判定統一(Primary NG→Secondary→WARNING)は変わらない。

## 10. test・evidence計画の改定(OF-AUW-05, 11採用)
- Melos regression: Azure転写が未保存の1件は、保存wavに対し実Azure 1回で補完する。期待値は「統一フローでの12/12」。API割込み・障害時はSTOP条件としてFableが判断する。
- OF-AUW-11: testはProduction同一の前処理後の原稿で行う。受入基準に「PASS→NG(旧PASSが新NGになる)全件を確認し、意図しないものが0件」を追加する。

## 11. ユーザー判断(質問文案)
### U1(C-A5/A6): JA C1固有名詞差・類似度<0.4の除外を解放するか
事実: `REDETERMINATION_CHECK_01.md`:12は「除外条件も承認」とあり、:35は「C1はFable採用・ユーザー個別承認の逐語なし」とある。両記載が食い違う。
質問: JAのSecondary確認で、固有名詞差(C1)と類似度0.4未満の除外条件を外し、通常どおりSecondary確認の対象にしてよいか。
暫定: 現行維持(除外を残す)。Fable推奨: 解放する(誤NGの原因を減らすため。値保護は解放後も値ガード・否定差で維持)。
### U2(OF-AUW-06): LR後v1にSecondary確認を必須とするか
選択肢(V04 2-7): (A)統一判定にそろえ必須とする / (B)現行の一部のみ必須 / (C)必須としない。
暫定: 暫定A2のみ現行`force_secondary`を維持。Fable推奨: (A)。

## 12. 記録のみ(OPEN候補)
- OF-AUW-16: 本タスクでは実装せず、OPEN候補として記録する(OPEN_ITEMS起票は委任_07)。
- OF-AUW-18: 同上。

## 13. 委任分割の改定(branch `feat/auw-unified-asr-01` 上)
- 02b: 共通judge+値ガード+Unit+静的監査(§1, §3)
- 03: EN配線+registry+ページ(§2, §6)
- 04: JA配線+J11(§3)
- 05: A2減速・Dialogue汎化・KP(§9)
- 06: evidence(§7, §10)
- 07: SSOT・Gate・main merge(§2)
