# DESIGN_01 対策設計(ASR-TIME-NUMERAL-EQUIVALENCE-01 委任_01、設計のみ。Production変更0)

前提: ROOT_CAUSE_01。原因は『隣接数詞語の読みを層ごとに別の1通りで固定』。制約: 例外登録・特定語の個別救済は不可、年号・金額・通常数値・同音救済・Primary/Secondary ASR・最終Gateと整合、正常を誤NGにせず異常を誤PASSにしない、品質基準は変えない。

## 案A: 多義展開(1語列→候補集合 {time, year(number), num+num, 合算})
- 内容: `_tier1_atoms` が隣接数詞語から複数の読みを持つatomを返し、比較側で『いずれかの読みが相手の同kindと一致すればEQUAL』。
- 変更箇所/行数: atomに `alts` を持たせ、`_atoms_equal`/`_atom_key`(SequenceMatcherのhashキー)/er078 `_en_sequence`/`Atom.key()`/`_compare_pair`/`_clock_pair`/`_closed_punctuation_diff_ok`/`atoms_public` の全てを多義対応にする。見込み **+80〜120行・6関数**。
- (1)(2)の解消: (1)は解消(time読みが `10:30` と一致)。(2)は**構造的に解消できない**: 年読み(number 1030)を候補に残す限り `1030` と一致する。年読みを落とす条件(時0-12かつ分10-59)を足せば解消するが、それは案Cと同じ規則を多義機構の中に持つだけ。
- 衝突: SequenceMatcher が『等しいキー』で整列するため、多義atomのキー設計(どの読みをキーにするか)で整列が変わる。誤PASSの余地が最も広い(候補が増えるほど偶然一致が増える)。保守性: 低(全比較関数に波及、既存testの期待を広く再確認)。
- 評価: **不採用**。

## 案B: 時刻文脈語(at/around/by/until/am/pm/o'clock)で時刻kindを優先
- 内容: `at ten thirty` のように直前の前置詞等がある場合のみ time/2数値、無ければ年読み。
- (1)(2)の解消: 文脈語がある場合のみ。`He left ten thirty`・KP英語phrase・`Meet ten thirty`・`It happened at nineteen ninety`(atは年にも付く)で破綻。`at ten thirty`↔`at 1030` は文脈語があれば NG にできるが、文脈語が無いと(2)が残る。canonとASRで文脈語の有無が揺れる(ASRが `at` を落とす/足す)と一致しなくなり、誤NGの新経路を作る。
- 変更: 文脈語辞書の新設(=辞書追加、特定語依存)。保守性: 低(語彙の網羅に依存)。
- 評価: **不採用**(例外辞書型、制約『個別救済不可』に近い)。

## 案C(推奨): 『時(1〜12) + 分(10〜59)』の隣接2語を、atom化の1点で時刻形に統一する
内容(scratch実装 `proto_C/er021_en_asr_semantic_equivalence_production_01.py`、`diff` +約45行、新関数 `_try_clock_pair` 1つ + `_tier1_atoms` に3行のhook):
- `_tier1_atoms` で、位置 i が『時: 算用数字 1〜12(1〜2桁) または 数詞語 one〜twelve』で、直後が『分: 10〜19の語 / 十の位の語(twenty〜fifty) / 十の位の語+一の位(語 または TTS数字化後の1桁数字 `thirty 5`)』(値10〜59)のとき:
  - 直後が am/pm → **time atom(value=時*100+分, meridiem)**(既存`_try_spoken_time`と同じ形)
  - それ以外 → **number atom 2つ [時, 分]**(= TTS数字化後の `10 thirty` や ASR の `10 30` が既に持つatomと同一。時刻の最終判定は既存の `_clock_pair` が `10:30` との間で行う)
- 条件外はNone(従来の年ペア読み・単独数値へ): 時が13以上(`nineteen ninety`/`twenty twenty`/`twenty twenty six`)、分が10〜59以外(`ten sixty six`=1066)、前後が数詞語/数字/`point`(解釈不能な数詞3連続)、`hundred`/`thousand`を含む語列(`one hundred thirty`)。
- 効果(実測):
  | 組 | 修正前 | 案C |
  |---|---|---|
  | `ten thirty`↔`10:30` | vg UNKNOWN(Judge PASS) | EQUAL(PASS) |
  | `10 thirty`↔`ten thirty`/`ten-thirty`(c8実対) | DIFF→NG | EQUAL→PASS(Tier1) |
  | `10 thirty pm`↔`10:30 pm` | DIFF→NG | PASS |
  | `one/two/twelve forty five`↔`1:30`等 | UNKNOWN/DIFF | EQUAL |
  | `ten thirty`↔`1030` / `ten thirty five`↔`1035` / `eleven fifty`↔`1150` | **PASS(誤PASS)** | DIFF→NG |
  | `twenty twenty`↔`2020`, `nineteen ninety (nine)`↔`1990/1999`, `ten sixty six`↔`1066`, `twenty one`↔`21`, `one hundred thirty`↔`130` | PASS | PASS(不変) |
  | 異常: `10:13`/`10:03`/`11:30`/`40`/`forty`/`ten`/`30`/`10:30 pm` vs am/pm差 | NG | NG(不変)。`ten thirty`↔`10:13` は Primary NGの価値差=P1(Secondary不呼出)に変化(UNKNOWN→DIFF。既存の数字化canonと同じ扱い) |
  - 検証: TEST_MATRIX_01(84件): 期待値あり77件で 修正前 誤NG10/誤PASS6 → 案C 0/0。replay 5,330対(`protoC_vs_baseline_01.txt`): judge PASS→NG **0**、NG→PASS 1(c8実対の誤NG解消)、vg PASS→NG 0、分類層PASS→NG 0。既存test(er006/er021/er078/er109の12ファイル): 修正前と同じ失敗集合(環境依存)、新規失敗0(`unit_tests_01.txt`)。
- 同音救済(er109)との整合: er109は X/Z scope内・既存層が全て不合格のときだけ最後に評価され、時刻は `\d{1,2}:\d{2}` と裸hour↔`o'clock`のみ(er109...:276,305-326)。案Cは er021 の atom化だけを変えるので er109 の入力・規則に触れない(`er109_probe_*`: 案C前後で er109 の反応は同一)。
- Primary/Secondary: 同じ`_en_sequence`/`_tier1_atoms`を通るので両転写に同じ読みが適用される。KP vote(guard_lifted)・approved basis skip の仕組みは不変。
- 最終Gate整合: Tier1が正しく等価/非等価になる(時刻形統一)ので、『Tier1はGateをskip』の経路が誤PASSを作らなくなる。value_guard側コードは案Cでは**無変更**(既存`_clock_pair`をそのまま利用)。
- 誤PASSリスク: (i) 時刻形に見える『数量+数量』(例: `ten thirty people`=10 30)は元々 num10,num30 の2atomなので同一のまま(変化なし)。(ii) 時1〜12+分10〜59の形をした**中世年号**(`twelve fifteen`=1215、`eleven fifty`=1150)は、語形↔桁連結(`1215`)の組が PASS→NG に変わる(意図した変化。(2)と同型で、時刻形の隣接語を年として桁連結と一致させない)。分が60以上の年(`ten sixty six`=1066)・時13以上(`nineteen ninety`/`twenty twenty`)は不変。replay 5,330対に該当0件、現代題材では稀。ただし品質基準(年号の語形↔数字一致)に触れるためOpus論点として明示する。 (iii) 時13以上の24時間表記(`thirteen thirty`)は従来どおり(年ペア読みのまま)=今回は救済しない(安全側)。
- 保守性: 規則が1関数に集約(時1〜12・分10〜59)。第1層(er006)は『ones→tens/teens境界で分割』、第2層`_clock_pair`は『分10〜59・時0〜24』で、時の上限だけ異なる(案Cは年号保護のため1〜12に絞る)。**委任_02で3層の定数を共通化するか要検討**(Opus論点)。
- 影響範囲: er021は共有module(X/Z/A/B/C共通)。A/B/C自体の開発・是正は対象外だが、変化は(a)時刻形の語列を含む文のみ、(b)方向は誤NG解消と桁連結誤PASS解消のみ(replay・matrixで確認)。

## 案D(参考・不採用): `_guard_en` だけを直す第3の局所パッチ
`ten thirty`(tier1が1030 numberに畳む)側は`_guard_en`では直せない(Tier1のskip経路がvalue_guardを通らない)。(2)が解消できない。不採用。

## 推奨と理由
**案C**。理由: (1) 同じ発音を同じatomにする『1点修正』で、(1)(2)と未発見の同根組(`one thirty`/`ten thirty five`/`10 thirty pm`/`eleven fifty`)を同時に解消する、(2) 例外登録・語彙辞書を持たない(数詞の閉じた表のみ。既存`_ONES`/`_TENS`再利用)、(3) 年号・通常数値・既存`_clock_pair`・er109・最終Gateを無変更のまま整合、(4) 変更行数が最小(+約45行1ファイル)。弱点は (ii) の中世年号の語形読みが NG 側へ倒れること(安全側)。

## 次の一手(委任_02の入口)
1. Opus必須レビュー(条件A/B。依頼文 OPUS_REVIEW_REQUEST_01.md)。
2. 承認後: er021 に案Cを実装、test追加(TEST_MATRIX_01から固定)、`replay_*`で修正後比較(PASS→NG 0確認)、全回帰、Production Wiring(共有moduleなので配線=コード反映のみ)、runtime evidence(PRODUCTION_PLAN_01.md)、SSOT更新、commit/push。
