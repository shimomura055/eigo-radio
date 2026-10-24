# OPEN487_DESIGN_01(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_04、OPEN-487 `one hundred thirty people`↔`1:30 people` 誤PASS。原因究明・方式比較・ベースラインまで。実装・Production反映は委任_05、Opusレビュー後)

## 1. 結論(先に)
- **分類: 既存承認仕様の不具合(T1: コードの挙動が承認済み仕様文と矛盾)** = 修正へ進む。Production反映は本委任では未着手(Fable方針: 最終Gate/分類層の作用に触れるためOpusレビュー→委任_05)。
- **根本原因は当初想定(value_guardのUNKNOWNが止めない)ではなく、一次分類層の `despace` 一致規則が『数字と数字の境界』も消していること**。`1:30`=`1 30`(2つの数)が `130`(1つの数)と『複合語の分かち書き差のみ』として NORMALIZED_MATCH になる。value_guard の `UNKNOWN(kind_mismatch num/time)` は『止めない』設計のため、この誤一致をその後で救えない(二次要因)。
- **推奨: 案A(`despaced()`と冠詞除外despaceの連結で、『数字で終わるtoken+数字で始まるtoken』の境界だけ空白を残す)。** 1関数+1呼出(約12行)、共通module `er006_preprod_hardening_01_validation.py`、flagなし。replay 5,330対で最終judge PASS→NG 0、TEST_MATRIX 152件期待不一致0、OPEN-487の誤PASS 9件を全て解消。案B(value_guard UNKNOWN→DIFF)は24時間表記等の現行PASSを壊すため不採用候補。

## 2. 発生機序(実測、`root_cause`=`$TMP`相当の探索、`p487`出力を`TEST_MATRIX_487_01.md`に集約)
```
canon 'one hundred thirty people'  ->  normalize_numeric -> '130 people'            atoms [number 130, people]
asr   '1:30 people'                ->  normalize_numeric -> '1:30 people'(token化で '1 30 people')   atoms [time 130, people]
classify(_classify_asr_match_core): canon_tokens ['130','people'] != asr_tokens ['1','30','people']
   -> despaced('130 people')='130people' == despaced('1:30 people')='130people'  -> NORMALIZED_MATCH(er006:1150、should_pass=True)
value_guard: num130 vs time130 -> UNKNOWN 'kind_mismatch:num/time'(er078 _compare_pair:399)   最終Gateは DIFF のみ阻止(er078_asr_unified_judge_01.py:540,688) -> 止まらず PASS
```
- 仕様との矛盾(T1): `normalize_numeric`の契約は『数値表記の意味同一な差を吸収する一方、桁や単位が変わる差は区別可能なまま残す』(er006 `normalize_numeric` docstring)。despace規則の目的も『複合語の分かち書き差(blitzscaling/blitz scaling)』(er006:1146-1149、span版:709は『数値tokenを含むspanには適用しない』と明記)。全文版だけ数字token連結を許しており、span版の方針と非対称=不整合。
- 同根の誤PASS: `130 people`↔`1:30 people`(数字のみ)、`I saw 130 people`↔`I saw 1:30 people`、`one hundred twenty`↔`1:20`、`two hundred fifteen people`↔`2:15 people`、`one hundred thirty people`↔`1 30 people`、`10 30`↔`1030`(空白区切りと桁連結)、`3 10-minute`↔`310 minute`。
- 重要な逆向きの確認: `nineteen thirty`↔`19:30`・`fourteen fifteen`↔`14:15` 等の**24時間表記は despace ではなく token一致(`19 30`==`19 30`)でPASS**しており、案Aの影響を受けない(OPEN-488の調査と共通)。

## 3. 方式比較
| 案 | 内容 | 利点 | 欠点・リスク | 実測 |
|---|---|---|---|---|
| **A(推奨)** | `despaced()`と冠詞除外despaceで、数字-数字境界の空白を残す(er006 +12行) | 根本原因に1点で対処。全Family共通moduleの誤PASSを全部閉じる。年号(`nineteen ninety`↔`1990`)はTier1経路でPASS維持。複合語の分かち書き(story making/covid 19/e mail)は無影響 | `At 1030`↔`At 10:30`・`At 130`↔`At 1:30`・`At 3:45`↔`At 345`(桁連結と時刻)は、Primary 1本の分類ではPASS→NGに変わる(旧=偶然のdespace一致)。X/Zは承認済みer109(`1030`↔`10:30`同音規則、CURRENT_SPEC 2026-10-23追記)が救済(`xz.decision` True/True/True を確認)、A/B/C Legacyは非救済→Secondary次第 | 最終judge PASS→NG **0**/5,330対、分類層PASS→NG 21(全て最終judge不変)、matrix_02 152件不一致0(REF 2件のみ変化) |
| B | value_guard `_compare_pair`の num↔time kind_mismatch を UNKNOWN→DIFF | 最終Gateで一律に止まる(Fable初期案) | 24時間表記`nineteen thirty`↔`19:30`・`fourteen fifteen`↔`14:15`が現行PASS→NGの退行、承認済みer109の`1030`↔`10:30`も最終Gateで阻止、最終Gate作用の拡大 | 退行3件(m487_B) |
| C | Tier1 atomに由来(scale語由来のnumber)を持たせ、scale由来number↔time だけDIFF | 最小の誤PASS閉鎖 | 数字のみの`130 people`↔`1:30 people`は閉じられない。atom構造変更(`_mk_number`)で影響範囲が広い | 未実装(設計のみ) |
| D | 個別文字列の例外登録 | — | ユーザー指示③で不可 | 不採用 |

## 4. 影響分析(案A、委任_05の実装前に固定する観点)
- 作用面: 一次分類 `classify_asr_match`(英語、`er006:1150,1165`)。X/Z/A/B/C共通module。flag/閾値/辞書/Prompt変更なし。新しい受理条件の追加ではなく**過剰受理の是正**(受理面は縮小する方向)。最終Gate・Secondary・retry/fallback・HR Lock・Tier1・value_guardは無変更。
- 副作用(開示): (1)桁連結と時刻/空白区切りの『偶然PASS』が消える(上表欠点)。(2)日本語は`despaced`を通らない英語専用経路(`classify_asr_match`は英語validator)のため影響なし(要・委任_05で再確認)。(3)`3,000`↔`3000`は`normalize_numeric`が先にカンマを除去するため影響なし(matrix確認済み)。
- 回帰: TEST_MATRIX_487_01(56件)+TEST_MATRIX_03(152件)+replay 5,330対+全回帰(env依存分は同条件のbase比較)。委任_05で `er006_preprod_hardening_01_validation` の既存test(despace関連: `er021_en_asr_semantic_equivalence_production_wiring_01_test_01`のdespaced言及、`er006_*test*`)を単独実行して確認する。
- 副所見 X-5(別件): `1,000,000 dollars`↔`1000000 dollars`が修正前から最終Gate DIFF(7桁以上の生数字列を値化せずliteral扱いする規則とカンマ付きの非対称。ASRはカンマ付きで返す傾向のため実害低。OPEN-492候補・実害未観測)。

## 5. 実装計画(委任_05、Opus承認後)
1. `er006_preprod_hardening_01_validation.py`: `_join_keep_digit_boundary`追加+`despaced`/冠詞除外despaceの2箇所差替え(`proto_487A/er006_preprod_hardening_01_validation.py`が原案)。
2. test: `er006_*`/`er021_time_numeral_test_01.py`へ TEST_MATRIX_487_01 のNE/EQ/REF固定、X/Z end-to-end(adapter経由のer109救済を `xz.decision` ではなく正式Primary chainで確認)。
3. gate: replay PASS→NG 0・合成負例NG維持・全回帰(base比較)・runtime evidence(既存entry再判定、新規TTS 0)。
4. SSOT/commit。
