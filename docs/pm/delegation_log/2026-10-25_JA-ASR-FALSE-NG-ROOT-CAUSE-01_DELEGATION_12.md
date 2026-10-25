# 委任_12｜JA-ASR-FALSE-NG-ROOT-CAUSE-01 しわ↔すわ是正: Opus条件Cレビュー反映(E3をP-1なしで是正本体に・M-1〜M-6/R-1〜R-6)・Secondary全件評価・E4(便乗PASS)の設計評価・Production適用(API 0)

## Fable判断(本委任の前提。変えない)
- Opusレビュー(全文は本委任文末尾に逐語で添付。`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/OPUS_REVIEW_01_OPEN333.md` に**そのまま保存**すること)は、区分「実装不具合」に同意、E3(数字を除いた全文の再diffで全差分の説明を要求)は承認範囲内の不具合是正として妥当。**助詞免除P-1は未承認のv2規則を既定ONで入れることになるため不具合是正の枠に入れない**。
- Fableは Opus の R-3 を採用する: **是正本体=E3(P-1なし)**。P-1(助詞免除)は①v2/②B-light βの採否と一緒にユーザー判断へ回す(本委任では実装しない。proto_02のP-1部分はProductionへ移植しない)。月題#1(転写「月の詩は八千九百本長」)がE3でNGになる(1/677=0.15%の再生成増)ことは、承認済み仕様どおりの結果として受け入れ、報告で「正常な月の記事タイトルの救済」はv2/βの担当であることを明示する。
- E4(便乗PASS: カタカナ固有名詞の母音違い等が他差分のE救済に便乗してPASS)は、Opus R-4どおり**同程度に優先度の高い不具合**として、本委任で負例作成→設計→API 0評価まで行う。Production適用はE3を先行し、E4はFableが評価結果を見て判断(同じE分岐なので、E4のproto↔Production一致検証はE3と同じ枠組みで準備)。
- Production適用は、Opus M-4〜M-6を満たした上で行う。07A(OPEN-517)と同形: proto↔Production一致(全行+sweep+Secondary全件)、rollback定数既定ON、fail-closed、監視用audit field、回帰、保存転写注入によるAPI 0のruntime発火確認(有料Trial不要)。

## 参照
`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/` の `OPEN333_DESIGN_01.md`・`OPEN333_EVAL_01.md`・`OPEN333_PREREGISTERED_01.md`・`proto_open333_fix_02.py`・`eval_open333_api0_0{1,2,3}.py`・`open333_trace_01.*`・`OPEN517_APPLY_PLAN_01.md`/`OPEN517_APPLY_RESULT_01.md`(07Aの適用手順の先例)・`OPUS_REVIEW_01_OPEN517.md`。Production: `er007_ja_asr_validator_01.py`(258-261, 366-386)、`er011_ja_asr_variant_layer_01.py`(347-372)、`er007_ja_secondary_asr_01.py`(644)、`er078_asr_value_guard_01.py`(`extract_atoms_ja`)、`er078_asr_unified_judge_01.py`。ユーザー指示 `docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_USER_02.md` §6/§8。

## 並行agent(衝突回避)
(A) KP HR 委任_05(er119/er120/er019/er026/er062系・その出力・OPEN-518/519/484行・CURRENT_SPECのKP/Part 2節)、(B) Family Y(er121系・Y docs・OPEN-520行)。本委任の所有: `er007_ja_asr_validator_01.py`・`er011_ja_asr_variant_layer_01.py`(+test)・必要なら `er078_*`(audit field追加の最小限)、`docs/research/JA-ASR-FALSE-NG-ROOT-CAUSE-01/`、OPEN-333/517行の最小追記、CURRENT_SPEC/DECISION_LOGの最小追記(一時index+commit-tree方式で自分のhunkのみ。直前再Read)。

## やること(すべてAPI 0・実費0円)
### 0. R-1 確認
DECISION_LOGをGrepし、Candidate E承認(PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 Phase 2)の対象範囲に「数字不一致の経路」が含まれていたかを原文引用で記録(`OPEN333_DESIGN_02.md` §1)。含まれていなくても結論(E3=前提に戻す最小是正)は変わらない。R-6(E分岐の安全が07A F1に依存)を同§に記録し、可能ならE分岐内でも値ガードEQUALを要求する多層防御を設計に含める(判定を広げない方向のみ)。
### 1. E3 proto v3(P-1なし)+Opus M-1/R-2の反映
- `proto_open333_fix_03.py`: P-1を除去。数値の剥がし方は R-2 どおり、値ガード(`extract_atoms_ja`)が数値と認識したspanに限定し、削除ではなく両側を同じplaceholderに置換(ひとり/はたち/3.5/%等の剥がし残りで正常音声をNGにしない)。語中の漢数字(一緒・千葉・九州)を剥がさない。helper内例外は拒否(fail-closed)。
- M-3の負例・正例8クラスをsweepへ追加(`OPEN333_PREREGISTERED_02.md` に事前登録してから評価)。
- **M-2**: Secondary転写(保存済み1,098件)を含む全件(既存771+未知493+合成+sweep+Secondary)で、現行HEAD Production vs E3 の判定差分を出す(`eval_open333_api0_04.py` → `OPEN333_EVAL_02.md`+json)。期待: 縮む方向のみ(新規PASS 0)、正常音声のNG化は月題#1のみ(理由付き)、N3-07遮断。決定性2回実行。
### 2. E4(便乗PASS)の負例作成・設計・評価
- 負例: カタカナ固有名詞の母音違い(走れメロス→走レメラス 型)+別の場所の同音漢字差、ヴェ↔ベ、略語、濁点のみの差 など(M-3 6.と合わせる)。
- 設計案(例: Eが救済した後に残るnon-cascade以外の差分も、entity_like/濁点差は従来どおりCascade行きへ)。`proto_open333_fix_04.py`(E3+E4)で評価、E3単独との差分を明示。Production適用は**しない**(Fable判断待ち)。
### 3. E3のProduction適用(M-4〜M-6)
- protoをimportせず移植(er011のE分岐に `and not ...` を足す形。拒否時は既存の `return None`→TRUE_CONTENT_MISMATCH)。rollback定数(例 `CANDIDATE_E_FULL_DIFF_CHECK=True`、env/flag不可)。OFFでHEADと完全一致・ONで期待差分、の両方をtestで固定。
- M-6: 拒否した(c,a)を構造化audit field/warning codeで記録(判定不変)。07AのR-5記録と同じ場所に乗せられるなら乗せる。
- proto v3↔Production一致を全行+sweep+Secondary全件で確認(差分0)。
- 回帰: 遮断harness下で er007/er011/er078 unified系・er066・`er078_asr_unified_wiring_static_audit_01`(XYZ共通経路とYの配線漏れ確認)。er007:366-380・er011:347-362のコメントを前提に合わせて更新。
- runtime発火確認(API 0): 保存済み転写を正式adapter経路に注入し、E3拒否が発火すること、E経由PASSの件数と拒否件数を集計(OPEN-517と同方式)。有料Trialはしない。
- `DESIGN_02.md:53` の誤記訂正をSSOT(該当docs)に反映。
### 4. SSOT
- OPEN-333: E3適用(APPLIED)・P-1はユーザー判断へ・E4は評価済み適用待ち、を最小追記。OPEN-517: R-6依存関係を1文。CURRENT_SPEC: Candidate Eの節(Grep)に「数字不一致経路でも非数値差を全件検査(E3、rollback定数名)」を1〜2行。DECISION_LOG: 1件(区分・Opus反映・P-1保留・E4扱い)。
### 5. Git・ログ
- 禁止=`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。対象pathのみcommit→`git push origin HEAD:main`(non-fast-forwardなら fetch→`git merge --no-edit origin/main`→push、競合は両方残しSTOP)。secret grep 0件。
- 委任文逐語保存: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_DELEGATION_12.md`(直近既知index=604。605以降を試し、先頭行が「# 委任_12｜JA-ASR-FALSE-NG-ROOT-CAUSE-01」のものだけ採用。同じ探索で先頭が「# Opus必須レビュー(PM_GOVERNANCE 11-3 条件C)｜JA-ASR-FALSE-NG-ROOT-CAUSE-01「しわ↔すわ」」のものを `..._OPUS_REQUEST_DELEGATION_04.md` に保存)。

## 報告(`docs/pm/RESULT_PACKET_JAASR12.md`+最終報告)
1. R-1の確認結果 2. E3 v3の評価表(現行HEAD vs E3: 新規PASS/NG化/理由、Secondary含む全件、sweep 8クラス) 3. E4の負例・設計・評価(E3単独との差) 4. Production適用の内容・一致検証・回帰・runtime発火確認・rollback定数 5. SSOT・commit sha・raw URL 6. RESULT_PACKET 4行+判定整合行 7. ユーザー判断へ回す点(P-1=助詞免除、v2/βと一体)とE4のFable判断材料(QCD)。事実と推測を分ける。

---
## 添付: Opusレビュー全文(逐語。`OPUS_REVIEW_01_OPEN333.md` へそのまま保存)
## Opus独立レビュー(11-3 条件C): JA-ASR-FALSE-NG-ROOT-CAUSE-01 N3-07(しわ↔すわ)の是正案E3P

### 総括
- 「実装不具合」という区分には同意する。
- 是正の本体であるE3(数字を除いた全文を再diffし、全差分の説明を要求する方式)は、承認範囲内の不具合是正として技術的に妥当。
- ただし助詞免除P-1は、(a)未承認のB-light v2規則をProductionの既定動作に入れることになる、(b)実装が説明より広く、新たな抜け道が残る、という2点から、E3と同じ「不具合是正」の枠では入れられない。
- 加えて、評価母集団からSecondary転写が抜けている。
- 推奨は「E3(P-1なし、または後述の狭めたP-1をユーザー判断に回す)」+M-1〜M-6。
- Productionの採用可否は判断しない。

---

### 論点1 区分判定 — 同意(条件1点)
**根拠**
- er007:258-261 の `continue` が原因。数字差を含むopcodeごと飛ばすため、そこに糊付けされた非数値差は `content_diffs` に入らない。
- er011:363-366 のCandidate Eは、`content_diffs` に入った差分だけを見る。
- 反証も十分にある。
  - 同じ文字対でも、糊付けがなければNG(CF3 `p2_exclusion`)。
  - `すわ` はopcodeが分割されるとNG。
  - `しば`/`す`/`そ` は糊付けされていればPASS。
  - 超/長の差を除くとNG(CF1)。
- 「母音違いを許す規則」は存在しない。承認時の前提(er007:374-380「全文の読み一致/正規化後一致」「誤PASSのリスクを生まない」)に反する検査漏れである。

**条件(R-1)**
- Fableは、Candidate Eの承認(PRONUNCIATION-RESOLUTION-ALL-ACTIVE-FAMILIES-PRODUCTION-01 Phase 2)が「数字不一致の経路」を対象範囲に含んでいたかを、DECISION_LOGのGrepで1回確認してほしい。
- 含んでいなかった場合、Eがこの経路で動くこと自体が承認前提外となる。ただしそれでもE3は「前提に戻す最小是正」として説明でき、結論は変わらない。
- もう一つの事実として、数字不一致の経路ではEが**数値そのものを一切検査していない**。数値の安全は07A F1(最終Gateの値ガード)に全面的に依存している(R-6参照)。

### 論点2 E3Pの安全性 — 条件付き同意
**単調性(新しいPASSを生まないこと)は構造上成り立つ**
- 条件は、E分岐に `and not ...` を足すだけで、拒否時は既存の `return None` → TRUE_CONTENT_MISMATCH に落ちる実装にすること。
- 拒否後にunified_judgeがSecondaryで正規にPASSさせることはあり得る。これは承認済みの経路なので、新しいPASSには当たらない。

**残る漏れ・副作用(いずれも新しいPASSではなく、残存するもの)**
1. **P-1は説明より広い。**
   - `explained_p` は、文脈のない断片spanに対して `pron_hira` を呼ぶ。`pron_hira` の中身は「unidic kanaによる断片の読み一致+助詞は/へ」であり、「助詞だけ」の規則ではない。
   - さらに、断片 `は` を単独でtaggerにかけると助詞と判定されやすい。そのため、**助詞でない は↔わ**(例: 原稿 `はし8,900本…超` / 転写 `わし八千九百本…長` の h↔w の子音違い)が、糊付け+別の場所の同音差という条件で今後もPASSし続ける。
   - 「しわ↔すわ型の子音違いを再び通す経路」は、は↔わ・へ↔え に限って実在する。
2. **`strip_numerals` が漢数字の文字を語中からも剥がす**(一緒・千葉・九州・万一・一人前など)。
   - 漢数字の文字だけが入れ替わった差は見えなくなる。ただし07Aが助数詞付きのものは捕まえるので、残る範囲は狭い。
   - 逆方向として、`1人`↔`ひとり`、`2日`↔`ふつか`、`20歳`↔`はたち`、`3.5`↔`三点五`、`%`↔`パーセント` では剥がし残りが出て、**正常な音声をNGにする**方向に働く(Eを経由する条件のときだけ)。
3. 糊付けされた残余が濁点だけの差やカタカナ・略語同士の差だった場合、非糊付けならCascade(Azure再確認)へ回るところ、E3では即NGになる。安全側だが不整合である。

**M-1**
- P-1を残すなら、断片spanではなく**数字を除いた全文の文脈でtagし**、助詞と判定された位置の は→わ/へ→え だけを置換する。
- そのうえで既存の `explained`(pykakasi読み一致/E候補の共通読み)をかけ直す形に狭める。unidic kanaによる読み一致は使わない。

**R-2**
- 剥がす対象を全文字の正規表現ではなく、値ガード(`er078_asr_value_guard_01.extract_atoms_ja`)が数値として認識したspanに限る。
- さらに、削除ではなく両側を同じplaceholderに置き換える。アラインメントが安定し、ひとり/はたち型も値ガード側で扱える。

### 論点3 助詞免除の副作用 — 現設計には不同意(代替を提案)
- 承認済み仕様での正しい結果は、非糊付けの `詩は`↔`しわ` と同じくNGである。MOON#1は**不具合のおかげで**PASSしていたにすぎない。
- E3単独は、仕様どおりの状態に戻す是正である。
- P-1を入れると「糊付けならPASS・非糊付けならNG」という逆向きの不整合をコードに固定する(論点(c)は懸念どおり)。また、未承認のB-light v2規則を既定ONで入れることになり、CLAUDE.md禁止(2)とユーザー指示§6「承認済み不具合修正か新しい合格条件かを区別」に照らすと、新しい合格条件の側に入る。
- P-1を支える根拠はMOON#1の1件だけで、しかも「正常と推定」(再聴なし、同じwavの他の転写はNG)である。

**比較**

| 案 | 区分 | 再生成増 | 備考 |
|---|---|---|---|
| E3 | 純粋な是正 | 1/677(0.15%) | 月題タイトルの救済は、本来の担当である①v2/②B-lightで行う |
| E3P | ユーザー判断事項 | 0 | 未承認規則を含む |

**R-3**
- E3を不具合是正として先行させ、P-1はB-light v2の採否と一緒にユーザー判断へ回す。
- その際、MOON#1の音声ラベルを確定する(同じwavのSecondary転写や採用実績の確認で足りれば費用0)。
- ユーザー受入条件「正常な月の記事タイトルを適切に救済できる」との関係は、報告で明示すること。

### 論点4 汎化 — 条件付き
- 実データで糊付け残余を持つPASSは2件だけ。合成sweepも、し/す/しば系の1文型に偏っている。
- **M-2(必須)**: 評価母集団から**Secondary転写(保存済み1,098件)が除外されている**。しかし `classify_ja_asr_match` はSecondary判定(er007_ja_secondary_asr_01:644)でも呼ばれ、Candidate Eは `allow_reading_resolver=False` でも到達する。API 0で全件を通し、変化0(またはSecondaryでPHONETIC_MATCHが採用に効かないこと)を実測で示す必要がある。
- **M-3**: 次の負例・正例クラスをsweepに追加する。
  1. 数値の後ろ側の糊付け(`8,900本超`→`八千九百ぼん…`)、片側だけの挿入・削除(しわが脱落)
  2. 1文に複数の数値があるもの、`1万2,000`↔`一万二千`
  3. 小数・%・単位(km/℃)・分数
  4. かな数詞(ひとり・ふつか・はたち・ひとつ)。正常NG化の検査用
  5. 漢数字を含む普通の語(一緒/千葉/九州)。保持した場合と入れ替わった場合の両方
  6. P-1の負例(助詞でない は↔わ: はし→わし/はな→わな、へ↔え: へや→えや)
  7. 差分が文頭・文末にあって窓幅が切れる場合
  8. 全角数字・〇/零

### 論点5 便乗PASS(E4) — 見送りの理由づけには不同意。別委任はよい
- 構造はN3-07と同じ種類である。承認済みの「entity_like/濁点差はCascadeへ」という安全条件を、Eが迂回している。
- 実例の `走れメロス→走レメラス`(ロ→ラ)は、ユーザーが重視すると明示した**固有名詞の読み違い**の型にあたる。
- 「実害の証拠なし」は、その型の負例が凍結コーパスに無いことによる(neg_pass_blocked 0は、負例が無いから0になっている)。
- 費用はCascade 4/677件で、1件約0.27円。即座に再生成になるわけでもない。
- **R-4**: E3と同じくらい優先度の高い不具合として、並列の委任で負例(カタカナ固有名詞の母音違い+別の場所の同音漢字差)を作り、早期に是正する。E分岐の同じ場所への変更なので、parity検証とレビューをまとめる案も合理的。リスク評価は「中」(固有名詞の誤PASSが通り、発生頻度は約0.6%)。

### 論点6 Production適用設計 — 欠けている点
- **M-4**: proto(`docs/research/` 配下)をProductionからimportしない。移植したうえで、proto↔Productionの判定一致を、全行+sweep+Secondaryの全件で確かめる。
- **M-5**: rollback定数は既定ON(是正有効)とする。OFFにしたときHEADと完全一致すること、ONにしたとき期待どおりの差分になることを、両方テストで固定する。helper内の例外は「説明できない=拒否」(fail-closed)とする。
- **M-6**: E3による拒否は `return None` で情報が消え、理由が一般的な「数字の不一致」になる。監視用に、構造化されたaudit field/warning code(拒否した(c,a)を記録)を追加する。判定には影響させない。
- 既存のreason文字列一致を構造化フィールドにすることは、今回の必須事項ではない。
- runtime証拠: この分岐はまれにしか発火しない(約1/710)。保存済み転写を正式なadapterの経路に注入してAPI 0で発火を確認し、あわせて正式runでE経由PASSの件数と拒否件数を集計する(OPEN-517と同じ方式)。発火させるためだけの有料Trialは不要。
- 回帰テスト: er007/er011/er078 unified系のテスト、er066、`er078_asr_unified_wiring_static_audit_01`(XYZ共通経路とFamily Yの配線漏れ確認)。er007:366-380 と er011:347-362 のコメントも、前提に合わせて更新する。

### 論点7 その他
- **R-6**: 数字不一致経路でのEの安全は、07A F1が有効であることに依存している。F1を単独でrollbackすると、8,900↔89,000型が再び通る。その依存関係を記録し、可能であればE分岐の中でも値ガードEQUALを要求する(多層防御)。
- `DESIGN_02.md:53` の誤記訂正をSSOTに反映すること。

### 参照ファイル
- C:\Users\tensh\eigo-radio\er007_ja_asr_validator_01.py(258-261, 366-386)
- C:\Users\tensh\eigo-radio\er011_ja_asr_variant_layer_01.py(347-372)
- C:\Users\tensh\eigo-radio\er007_ja_secondary_asr_01.py(644: Secondary経路でもclassifyを呼ぶ)
- C:\Users\tensh\eigo-radio\docs\research\JA-ASR-FALSE-NG-ROOT-CAUSE-01\proto_open333_fix_02.py(22-28: 断片spanに対するpron_hira)
- C:\Users\tensh\eigo-radio\docs\research\JA-ASR-FALSE-NG-ROOT-CAUSE-01\proto_reading_compare_02.py(49-62)
- C:\Users\tensh\eigo-radio\docs\pm\delegation_log\2026-10-25_JA-ASR-FALSE-NG-ROOT-CAUSE-01_USER_02.md(§6, §8, §10)