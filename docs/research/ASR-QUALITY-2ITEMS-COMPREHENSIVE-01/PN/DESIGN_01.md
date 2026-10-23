# DESIGN_01: 固有名詞の認識・分類の包括対策(Run Entity Table = RET)

管理ID: ASR-QUALITY-2ITEMS-COMPREHENSIVE-01-PN 委任_01 / 2026-10-23 / Status: DESIGN_READY_PENDING_OPUS_REVIEW(Trial実装は次委任。Production/Prompt/flag/閾値/Ledger変更0)
根本原因=ROOT_CAUSE_01.md。数値根拠=本フォルダの`quant_*`/`exposure_*`/`article_entity_scan_*`/`ner_probe_*`/`phonetic_gate_probe_*`。

## 1. 設計目標と制約

目標(ユーザー指示 §2・§4①): 台帳事前登録に依存せず、本文中の固有名詞(人名・地名・組織名・作品名・ブランド/商品)を高い網羅性で検出し、承認済み発音救済(アラーム記録のみで停止しない)を**登録済み・未登録の双方**で機能させる。ただし**固有名詞と認識しただけで異なる発音まで無条件にPASSさせない**。承認済みの受理条件・安全条件は変えない。

守る制約: ①受理境界(類似度≥0.40・一般語ブロック・P-03・G3二重ASR・数値/否定/脱落・KP/JA/HEADING除外・P-01入口)は不変 ②Ledger人承認フロー(B階層以上のTTS注入)不変 ③失敗時は**現行と同一挙動(HR行き)**へ倒す(fail-closed) ④Family A/B/Cへ影響しない(run scope X/Zのみ) ⑤追加費用 ≤0.1円/記事セット ⑥DEV/Trial専用経路で実装し、正式経路(retry/rewrite等)から暗黙参照させない。

## 2. 推奨案: Run Entity Table(RET)

「固有名詞とは何か」の**正本を1つ**、run(level)ごとに作る“本文実体表”とする。PNAPの証拠源に追加するだけで、判定ロジックの閾値・ガードは変えない。

```
 [最終脚本text(level単位)] ─┬─(R1) 決定論スキャン(API 0): 出現位置・大文字一貫性・CMU/zipf・ALLCAPS・所有格・大文字連なり
                              ├─(R2) 宣言済み実体(Z: Seed key_roles[].name / keep_name 等。無ければ空)
                              └─(R3) LLM NER 1回/level text(gpt-6-luna, strict JSON schema): surface+category
                                         ↓ 検証(原文に逐語出現・一般語/題名/長句の除去・大文字一貫性)
                              Run Entity Table(audit/entity_table.json: text sha256, model, usage, entries[surface,tokens,category,grade,sources], dropped[])
                                         ↓
   PNAP: evidence = 既存5証拠 ∪ entity_table(grade∈{declared,confirmed}) / Secondaryのspan許容 = 実体表token列に限る(RET-3)
```

### 2-1. RET-1 実体表の構築(run単位1回、API 1 call)
- タイミング: TTS段の入口(X: `family_scope`、Z: `run_tts_stage`=er063_family_z_audio_01.py:1288-1300 が既に`article_text`を受ける)でscope内・最初のTTS前。text sha256が一致する既存表があれば再利用(resume/再実行/Local Rewrite無変更時はAPI 0)。textが変わった(Local Rewrite後など)場合のみ再構築。
- (R1) 決定論スキャン: 語ごとに n_total / n_cap / n_lower / n_mid(文頭・引用直後・見出し以外の大文字出現)/ 位置、CMU収録有無、zipf、単独ALLCAPS、所有格、大文字連なり(複数語名)を数える。**単独では証拠にしない**(実測: 文頭/引用直後のみの大文字語17のうち実在固有名詞3・偽候補5=精度3/8、`article_entity_scan_01.py`)。ただし文中大文字が一度でもあり小文字形が無い語、CMU未収録語、ALLCAPSは現行PNAPの既存証拠と同等なので“強”扱いで表に載せる(挙動は現行と整合)。
- (R2) 宣言済み実体: Z Seed `source_essentials.key_roles[].name`(`keep_name:true`は特に強い)等。**Bertie は宣言に無い**(歌詞のみ)ため、宣言だけでは足りない(=実測の要点)。Xには英語の宣言済み実体表が存在しない(Research Ledgerは日本語fact/subject)。
- (R3) LLM NER(gpt-6-luna、reasoning low): 実測 22本文 0.5767円(0.026円/本文、入力平均740 token、出力平均180 token)。**Bertie・Vera・Framton・Melos・ELLE・Vogue・Meta・Reuters を検出、決定論の偽候補(inventing/canceling/fats/roasting/unwanted)は0件誤検出**(`ner_probe_01_result.json`)。出力: surface(原文どおり)+category(person/place/organization/work_title/brand_product/other_named)。
- 検証(機械、API 0): (a) surfaceが原文に逐語(case-sensitive、curly quote正規化)で現れること=幻覚除去 (b) 見出し行そのもの・5語超は除外(題名/文) (c) category enum外は除外 (d) **大文字一貫性**: 非一般語tokenが本文中に小文字形で現れる語は証拠対象外(通常語の可能性) (e) 全tokenが一般語(CMU∧zipf≥4.0)の実体は表には載せるが証拠は付与しない(現行`R_GENERAL_WORD`を維持=§4)。
- 格付け(grade): **declared**=宣言済み実体 / **confirmed**=LLM ∧ 大文字一貫性 ∧ (決定論で大文字出現あり) / **weak**=その他(表に記録、証拠にしない)。PNAPに渡す証拠は declared と confirmed のみ(**2シグナル規則**: LLM単独の主張は証拠にならない)。
- 複数語名: 表のentryは`tokens`(fold)を持ち、`L. Mimoun`/`Kristie Tse`/`Stephen Reicher`を1実体として扱う(RET-3で使用)。イニシャル(`L.`)はentry内の内部tokenに限り許可。
- 失敗: API失敗・timeout・不正JSON・空応答・refusal → 表は`status=LLM_UNAVAILABLE`で決定論“強”のみ(=現行同等)。例外を投げない・制作を止めない・operator reportに「実体表未構築」と明記。

### 2-2. RET-2 PNAP証拠源の拡張(C階層=自動検出・発音注入なし・ASR受理証拠のみ)
- `evidence`に`entity_table`を追加。`proper_noun_evidence`の5証拠は**そのまま**残し、表のtoken(declared/confirmed)にも`True`を返す(ラベル`entity_table:<grade>:<category>`でアラームrecordに残る)。
- **Ledger人承認フロー維持**: Ledger=発音情報/TTS供給(A/B階層)の正本。RETは“その語が固有名詞であること”の証拠だけを供給し、TTS入力は一切変えない(発音注入なし)。
- 以降の関門は全て既存: G0 role/言語/KP除外、G1 NG_BOTH/secondary_not_accepted、G2 Primary分類+全diff entity_like、G3 Secondary二重一致、G4 diff≤3、G5 `_noun_checks`(一般語ブロック・ASR長≤2×・数値/否定・**despaced類似度≥0.40**・P-03両ASR一般語)、P-01入口、P-04 noise上限、slot。

### 2-3. RET-3 実体span対応(複数語名のSecondary跨ぎ)
- 現行 er103:355-366 は「Secondaryのdiff spanがPrimaryの固有名詞tokenに隣接する語まで巻き込んだら不受理」。実データではこれが**固有名詞のみ候補の16/67=24%**を止めている(L. Mimoun×10、Kristie Tse、Altuzarra Toteme×2、Melos drank×3)。
- 変更(表がある場合のみ): Secondary diffのcanonical span の**全tokenが実体表(declared/confirmed)のtokenである**(+所有格`s`)なら、隣接語の巻き込みではなく名前の一部とみなし、span全体を`_noun_checks`(類似度≥0.40・ASR長≤2×・数値/否定なし)で検査する。`melos drank`→`mellow strength`は`drank`が実体でないため**従来どおり不受理**を維持。
- 期待(推定、Trialで実測): C類16のうち13(Mimoun×10、Kristie Tse、Altuzarra Toteme×2)が救済対象、3(Melos drank)は不受理のまま。

### 2-4. RET-4 監査・可観測性
- alarm recordの`mismatch.proper_noun_evidence`に`entity_table:<grade>:<category>`、`pronunciation_basis`にtable sha・出典(declared/llm/det)を残す。operator reportにカテゴリ別の件数と「実体表に載ったが小文字一貫性等で証拠にならなかった語(weak/dropped)」を載せる。
- 継承再判定(er019_family_x_validation_inheritance_01.py:349-352)で同じ受理を再現できるよう、表のsha256と使用entryを`asr_judgement.pronunciation_alarm`ブロックに保存(OF-PNAP-P-05(iii)と同じ原則)。保存が無い/shaが不一致なら再評価は表なし=現行挙動に倒す。

### 2-5. 実装場所(Trial)と将来の配線点(Production配線は未承認=今回は実装しない)
- Trial: 新規DEVモジュール `er111_pn_entity_table_trial_01.py`(builder+検証+evidence/span判定のwrapper)と`er111_pn_entity_table_trial_01_test_01.py`、評価harness `docs/research/ASR-QUALITY-2ITEMS-COMPREHENSIVE-01/PN/trial_*.py`。**`er103`/`er006_secondary_asr_01`/`val`は編集しない**。`evaluate_alarm_eligibility`の純関数に`ledger_surfaces=ledger∪表token`を渡し、span規則だけtrial moduleにG3部分を差分実装(表が空ならオリジナルとバイト同値であることをtestで固定)。命名は②UKUS側(`ukus`等)と衝突しないよう`_pn_`を含める。
- 将来の配線点(参考): `er103_pnap_runner_hooks_01.run_with_alarm_hook`(scope内・fn前に表を構築/読込→`pnap`が参照する run-scoped holder へ設定→finallyで解除)。Zは`er063_family_z_audio_01.py:1300`、Xは`@pnap_hooks.family_scope`(er019_family_x_audio_production_runner_01.py:886,1232)の共通部品を使う。flagは新コード経路+単一flag読取関数、既定OFF(PM_GOVERNANCE 11-7の5条件)。**配線自体は採用承認後**。

## 3. 代替案と比較

| 案 | 概要 | 網羅(recall) | 誤PASSリスク | 追加費用/記事 | 時間 | 評価 |
|---|---|---|---|---|---|---|
| **A 最小**: P-02緩和(引用直後/文頭の大文字を、低zipf語に限り証拠化) | 決定論のみ | Bertieは救済。偽候補 inventing/canceling 等も証拠化(実測精度3/8) | 高(通常語を固有名詞扱い。OF-PNAP-P-02の防止対象そのもの) | 0 | 0 | 不採用(Opus P-02と逆行) |
| **B 決定論RET**(R1+R2のみ、LLMなし) | 本文スキャン+Seed宣言 | 宣言/文中大文字/OOVの語のみ。Bertie(宣言外・歌詞のみ)は**救済不可** | 低 | 0 | 0 | フォールバックとしてのみ採用 |
| **C 推奨RET**(R1+R2+R3+2シグナル規則+RET-3) | 上記 | 実測でBertie・Vera・Vogue等を検出、偽候補0。span問題も13/16救済見込み | 表の精度に依存(2シグナル+既存ガード維持で抑制) | **0.03〜0.1円** | +5〜15秒(1 call, TTS前) | **推奨** |
| D Writer宣言型(Writerに固有名詞表を出力させる) | Prompt変更 | Writer網羅に依存 | 中 | +Writer出力増 | 0 | Prompt原則変更=ユーザー承認事項。将来案として残す |
| E 事前調査型(本文実体を全てStage 1調査→Ledger先行登録) | Perplexity | 調査成功に依存(今401) | 低だが供給は別問題 | 約0.4円×実体数 | 数十秒〜 | 不採用(Stage 2で判定側改善はREJECTED、調査は環境依存) |
| F フラップ等価のhomophone救済(Bertie≒Birdie=米語/t/→[ɾ])でPASS | 承認済みhomophone層拡張 | Bertieのみ(同音語系)、span問題・Vera等は不変 | 中〜高(全語に効く新PASS基準) | 0 | 0 | 不採用(認識でなく別仕様、ASR-HOMOPHONE承認範囲外) |

**採用判断**: Cを推奨し、LLM失敗時はBへ自動縮退(=現行同等)。Trialで未達ならB+(R2強化)や2回目の自己点検callを検討(§7)。

## 4. 安全条件・誤PASS対策(変えないもの/加えるもの)

変えない(全て既存・不変): 類似度≥0.40(`MIN_SPAN_SIMILARITY` er103:102)/ 一般語ブロック(`R_GENERAL_WORD`: CMU∧zipf≥4.0の語のみで成る句は受理しない)/ P-03(両ASRが一般語に揃えば不受理)/ ASR語数≤canonical×2 / 数値・否定語 / KP(vote_required)・JA・HEADING・TTS_FAILURE・除外表・Secondary障害 / G3(Primary・Secondary両方が同じ名詞で不一致)/ P-01入口(p3_primary_ng)/ P-04 / 差分数≤3 / slot / HR Lock経路(受理されなければ従来どおりHR Lock)。

加える: ①**2シグナル規則**(LLMのみでは証拠にならない=大文字一貫性かつ決定論の大文字出現が必須。幻覚・通常語誤タグを抑制) ②逐語出現検証 ③題名/長句除外 ④**RET-3はentityトークン列のみ**に限定(`melos drank`型は不受理維持) ⑤表が無い/不一致/空なら現行同等。

**音素近接ゲート案は不採用(データで棄却)**: 「別語への聞き違い」と「名前の聞き間違い変種」を音素距離で分けられるか実測(`phonetic_gate_probe_01.py`)。承認方針の受理済み30差分は距離0.00〜0.50、別語への聞き違い21合成例は0.10〜0.57で**分布が重なり閾値で分離できない**(例 vera→very 0.10、reuters→writers 0.10、framton→farm 0.54)。これらの“別の一般語”は既存の一般語ブロック/P-03が止める(very・writersはzipf≥4)。Bertie→Birdie=0.062。よって新たな関門を足さず**既存ガードが実効境界**であることを維持する。

**残存する誤PASS経路(by design)と評価**: ASRが別の非一般語(zipf<4)へ聞き違い、類似度≥0.40のもの(例 bertie→berry[zipf 3.97])は、Ledger証拠がある語に対する現行の受理と同一境界で受理される(承認方針の範囲)。RETはその“証拠を持つ語の集合”を広げるだけで、語ごとの受理境界は同じ。→ **parity test**(§6 SC-5)で「表由来証拠とLedger由来証拠で同一語・同一ASR変種の判定が一致」を証明する。実誤読をアラームで運営者へ報告する点も不変(記録のみで止めない=承認済み方針)。

**Std/Adv等レベル差・Local Rewrite**: 表はlevel textのsha単位。Local Rewriteでtextが変わった場合のみ再構築(幻覚防止のため逐語検証は新textで再実行)。

## 5. 費用・処理時間・単価
- 追加API: NER 1 call/level text(Std/Advで2 call)。実測 0.026円/call(最大0.043円)→**0.05〜0.09円/記事セット**(再構築1回含む上限≤0.1円)。70円/記事セットの0.1%以下。LLMのみ新規(gpt-6-luna、既存Model Routing登録モデル)。決定論・検証・PNAP評価は追加API 0。
- 時間: 1 call ≒ 数秒〜十数秒(Trial SC-7で測定)。TTS前の独立処理で、TTS(分単位)に隠れる/Xではscaffold段階と並列化可。
- Trial費用: NER約70 call ≈ 2〜3円(保存22本文の再実行、合成10本文、安定性3回×10、別モデル比較含む)。他API 0(保存転写のreplay)。

## 6. 検証計画と成功基準(Trial)

### 6-1. データ(再利用優先)
- D1 HR queue 88実イベント(`human_review_queue.jsonl`、汚染34除外)。D2 保存4,032ペア(`PNMH-PLAN-01/pairs_02.jsonl`、EN 3,041)+既存ON/OFF harness(`onoff_differential_02.py`のadapter replay方式を再利用)。D3 本文22(X記事+Z脚本)・Z『開いた窓』『走れメロス』。D4 **合成コーパス**: 位置(文頭/引用直後/vocative/所有格/複合名/イニシャル/ハイフン/非ASCII)×カテゴリ(person/place/organization/work_title/brand_product)×語彙性(CMU収録の人名[Bertie型]/OOV/一般語同形[Bill/Mark/Rose/Will])。D5 合成負例(ASR変種: 別内容語/数値/否定/脱落/語追加/両ASR一般語/題名一般語)。D6 失敗注入(LLM timeout/不正JSON/空/refusal/幻覚surface)。
- 正解集合(gold): 人手adjudication(D3+D4)。D1/D2は“entity_like diff”トークンをgoldの一部に使用。保存HR queueは地名・作品名・組織名が乏しいためD4で補う。

### 6-2. 成功基準(数値、全て達成でVALIDATED)
| ID | 基準 |
|---|---|
| SC-1 同値性(DefaultOffIsolation) | 表なし/空のとき、D1 88・D2 EN 3,041・既存`er103_proper_noun_alarm_policy_test_01.py`全件で判定が現行とバイト一致。flag未設定でAPI 0・副作用ファイル0 |
| SC-2 検出(網羅) | gold(≥150出現)で declared∪confirmed の recall ≥0.90(全体)、カテゴリ別 ≥0.85。**Bertie型(CMU収録の人名×文頭/引用直後)合成n≥10で 100%**。※recallが低い場合は大文字一貫性/2シグナル規則のablationで原因分解 |
| SC-3 精度 | 証拠付与entryの非固有名詞率 ≤2%。偽候補(inventing/canceling/fats/roasting/unwanted/farther/muddy/withdrawn、見出し語、Title Case一般語)の証拠化=0 |
| SC-4 受理(初見語) | Ledgerを全除外し、表は当該記事textから構築して再評価: B類9件 ≥8件受理(**Bertie 3/3必須**)、C類のentity-only 13件 ≥12件受理、Melos drank×3は不受理維持、A類41は受理維持、D/E類は不受理維持。Ledger1件ずつのleave-one-out(39 entry)で、その語に依存する受理の ≥90%が表で維持 |
| SC-5 誤PASS(parity) | 各表entryについて、合成ASR変種(≥200)で「表由来証拠の判定 = 同一tokenをLedger登録した場合の判定」が100%一致(=証拠源拡張だけで受理境界が緩まないことの証明)。D2の新規flip(260超)は100%人手確認で全てentity-only、非entity flip=0。D5の合成負例で受理0(by-designの“非一般語・類似度≥0.40”変種は別集計して明示) |
| SC-6 フェイルセーフ | D6の全注入で例外0・表由来受理0・現行と同一挙動・operator reportに未構築を明記 |
| SC-7 費用・時間 | NER ≤0.1円/記事セット(実測)、p95遅延を報告(TTS待ち時間に隠れること) |
| SC-8 横断 | Z 2作品+X ≥6記事の保存textで構築・カテゴリ分布・weak/dropped一覧を提示 |
| SC-9 安定性 | 同一textを3回構築し、confirmed entry集合のJaccard ≥0.90(未達なら多数決/2回目自己点検を設計追加) |

### 6-3. 反復方針(Trial回数で止めない)
未達原因を分解して再設計: ①recall不足→宣言源拡充(Seed/KP)・2回目call・別モデル比較・E2規則の緩和をablation ②精度不足→カテゴリ限定(work_title/other_namedは証拠にしない)・自己点検call ③parity崩れ→実装差分調査(spanパス) ④安定性不足→多数決。同一方向の微修正を繰り返さず、前提(LLM依存か、Seed宣言を主にするか)から見直す。ユーザーへ戻すのは、代替も尽きて行き詰まったとき/予算・安全・承認境界のみ。

## 7. 撤去・縮小・残置する旧規則(明示)
| 対象 | 扱い | 理由 |
|---|---|---|
| P-02(引用符/文頭/Title Caseの大文字を証拠にしない、er103:200-206) | **残置(撤去0・縮小0)** | 表が無い/失敗時の受け皿(fail-closed)。表が正常なrunでは“補助”に降格するがコードは触らない。撤去すれば偽候補(inventing等)を証拠化する(実測) |
| `proper_noun_evidence`の5証拠、`R_GENERAL_WORD` | 残置 | 受理境界の本体 |
| G3 `adjacent_word_changed`(er103:355-366) | 残置+例外1(entity token列のみのspan) | 非entity隣接語の巻き込み(Melos drank)は引き続き不受理 |
| `val.capitalized_flags`(緩い entity_like、val:485-509) | 変更しない(Trial範囲外) | 将来「定義の正本をRETへ一本化」する候補(Opus論点) |
| Ledger反応登録(Stage 1)・B階層承認・TTS供給 | 残置 | 発音供給の基盤。固有名詞“認識”の必須条件ではなくなる |
| 撤去/新設の予定 | 撤去0、新設=RET(builder/evidence/span/audit) | 残存Grepは実装委任で確認 |

## 8. 『開いた窓』停止音声の扱い(本設計との関係)
停止中の4 clip(a2/b1b × part1_c14/part3_c2、run_sf_prod_01)は保全。再開の選択肢は採用後に判断: (R1)RET有効で該当clipを再生成(費用約2〜5円、BERTIE_LEDGER_CANDIDATE_01.md §4、cascade内で受理見込み)、(R2)保存転写の再評価でAPI 0救済(現行はALARM起点のみ=er019:349-352。NG_BOTH起点へ拡張する場合はHR Lock解除に人承認が要るため別判断)。Trialでは**状態変更なしのreplay**(HR queue行118/120/121のPNAP再評価)でBertie受理の見込みだけを証拠化する。
