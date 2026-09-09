# EDITORIAL-B-FAMILY-VOICES-3V-4V-WRITER-DESIGN-OPUS-REVIEW-01 報告書

管理ID: PM-CLOSEOUT-CONSOLIDATION-30(Sonnet委任、SSOT反映+Git担当)。
本Reportの第1節「Opusレビュー原文」自体はOpus(L2 second opinion、読み取り専用
診断)の成果物であり、Sonnetは転記のみを行った(改変禁止)。第2節「Fable検証」
はSonnetが本タスクで追加実施した読み取り専用の実測検証(費用¥0)。

## 0. Fableメタ情報(転記前の付記)

- **管理ID**: EDITORIAL-B-FAMILY-VOICES-3V-4V-WRITER-DESIGN-OPUS-REVIEW-01
- **レビュー種別**: L2 second opinion(Opus、読み取り専用診断、Production/Prompt/
  Contract/registry編集なし、Trial着手なし)
- **実施日**: 2026-09-09
- **HIGHの理由**: 3V/4V本文Writer Trialへの着手可否判断であり、(a) Fact Safety
  (Ledger作成方式・出典帰属)、(b) 既存Production定数(Comment Contract・
  Disfluency QA必須segment表・A2 slowdown対象segment表)への後方互換性、
  (c) OPEN-131(複合Voice Fact Checker帰属)の既存PASS実績の前提、という複数の
  Production安全性論点が重なっており、Sonnet単独レビューでは委任案自体に含まれる
  事実誤り(下記0-A/0-B)を検出できていなかったため、着手前の第二意見(second
  opinion)としてOpusへ委任した。
- **対象**: (1) EDITORIAL-B-FAMILY-VOICES-PHASE1-5-3V-4V-INTEGRATED-DESIGN-
  TRIAL-03の統合設計案、(2) Fableが起草した3V/4V本文Writer Trial委任案(Sonnetへ
  委任予定だった実行計画)。
- **Opus使用量**: token 108,000、実行時間379秒。
- **差し戻し**: 0回(初回レビューで完了、Sonnetへの追加質問なし)。

---

## 1. Opusレビュー原文(Opus、読み取り専用診断、2026-09-09。以下、改変せず全文転記)

---
## 0. 委任案の前提に事実誤りが2件(着手前に要修正)
**A. 「Trial-09系Writer経路」は存在しない(HIGH)** 根拠: `er012_editorial_b_voices_trial_09_audio.py` の関数は音声専用。B1本文Writerは `er012_editorial_b_voices_trial_07.py::run_voices_pattern_run03`(L694)。推奨: 「Trial-07 Writer経路を新規Trialファイルへ複製して3V/4V化」。Trial-07自体の編集は禁止(`er012_editorial_b_family_production_phase1_test_01.py` L315-322がProduction `a2prod` 定数とTrial-07定数のbyte一致をテスト)。
**B. 「Ledgerは既存Research primitiveで作成」できない(HIGH)** 根拠: Trial-07 L190-191「research/perspective_map.md・research/verified_fact_ledger.txtを本Trial側で手作業でcuration」。`VOICE_n_EVIDENCE`タグ付きLedgerを自動生成するprimitiveは存在しない。固定テーマ"AI screening"の検証済みLedgerは未作成(既存Ledgerはhot-desking 1本のみ)。推奨(UDR): (a) er002 research pipelineで新テーマLedgerを作る(費用・時間が¥100を大きく超える)、(b) 既存hot-desking Ledgerを流用し3V/4Vのstakeholderをそのテーマへ再設計(同一テーマで2V比較が厳密、ただし4V軸設計はAI screening前提のため再設計要)、(c) Ledger作成を別Trialへ分離。どれを選ぶかを決めずに着手すると、事実未検証Ledgerの捏造(Fact Safety違反)かSTOPのどちらかになる。
## 1. Fact A'既定接続とWriter配線の整合
- (HIGH) `registry.build_voice_attribution_block()`(L327-334)は `[VOICE_n_EVIDENCE]` で始まる物理1行のみを抽出。実Ledger(trial_07 verified_fact_ledger.txt L54-64)は1 evidenceが約10行で、2行目以降が全部落ちる。OPEN-131のPASS(unsupported 5→0)は切り詰められたevidenceに対して免除ルールが効いた結果である可能性があり、false acceptの上限が実証されていない。単体テストは単行サンプルのみ。3V/4Vはevidence量・Voice数が増えるため悪化。推奨: Phase 2既定接続の前提条件として複数行evidenceの塊単位抽出へ修正(Production修正、要ユーザー承認)。本Trialでは修正せず、ON実行時の実blockテキストを保存して欠落を実測記録するだけに留める。
- (MED) 3V/4Vを別`editorial_type`にすると `is_fact_attribution_mode_enabled()`(L375-380)は新キーに`family`/`fact_attribution_mode`が無いとFalse/KeyError。Trial側定義でも同キーを必ず持たせる。
- (MED) 手戻りを出さない前提条件3つ: (i) TrialがProduction関数(`runner.run_fact_check_b1` → `b1prod.run_fact_checker` → `r3.build_fact_check_prompt`)を必ず経由、(ii) タグ命名規約 `[VOICE_n_EVIDENCE]` をLedger作成側で固定しn=Voice位置番号、(iii) stage順序(Writer→Fact A'→Ledger Deviation→Local Rewrite)をTrialで実際に踏み、Phase 2(OPEN-132項目1)がそのまま採用できる形で記録。
- (LOW) Fact A' blockは`article_text`非依存なのでretry/regeneration整合は3V/4Vでも保たれる見込み。未確認: 3V/4V実データでの再検証。
## 2. 3V/4VのQA設計(役割分担)
- (HIGH) 既存Point Overlap(`er008_point_overlap_qa_18.lexical_overlap_ratio`、L44-47)は`|A∩B|/|A|`の非対称指標で、閾値0.40はPoint⊂Full Storyの包含関係用に較正。Voice間の「立場・制約・責任・守るもの・推論の違い」は語彙では測れない(語彙が全く違っても推論構造が同一=ユーザーが問題視する事象を検出できない)。推奨: Voice間overlapはmonitoring専用のまま(2V Trial-07 L639-648と同じ)、合否判定に使わない。「役割・理由・主張の同一性」判定はルーブリック型(Analytical Leakage Checkと同じjson_schema方式)で新設が妥当(未承認仕様候補: pairwise Voice Distinctness Check、判定軸=stakeholder position / constraint / responsibility / what they protect / reasoning)。
- (HIGH) Analytical Leakage Checkは2V固定。`ANALYTICAL_LEAKAGE_JSON_SCHEMA`(`er012_b_family_voices_a2_production_01.py` L323-337)が `required:["voice_a","voice_b","tension","closing"]` + `additionalProperties:False` + `strict:True`、promptも「One Voice/Another Voice」で固定。3V/4VはTrial側で新スキーマを作る以外に方法がない。委任案はこの作業を明示していない。
- (MED) 「Perspective Diversity」は自動QAとして実装されていない。実体はperspective_map.mdの人手判定+Writer prompt埋め込み文言、TRIAL-06 Report L419「正式採用するかは未決定」。3V/4Vのperspective_map(3者/4者版)作成を明示タスク化すべき。
- (MED) pairwise前提ロジックの拡張: 2V monitoringは4比較(voice_a↔voice_b両方向+各voice vs hook、Trial-07 L628-631)。N Voiceへは「順序付きN(N-1)+N×hook」に一般化。
## 3. 閾値0.40の適用可否検証設計
- (MED) 「3/6ペア総当たり」は無向ペア数。指標が非対称なので有向ペア(3V=6、4V=12)+vs Hook(3/4)にすべき。
- (MED) 閾値を変えずに検証する方法: 実測ratioを記録のみ。¥0のcontrol群: Positive=承認済みVoice A本文の語彙のみ改変複製。決定的control(追加推奨)=「職名だけ違い推論構造が同一」のVoiceペア(語彙は大きく変える)。ここでratioが低いままなら語彙指標では要件を満たせないことの直接証拠。Negative=2V実測ペア(0.14〜0.2)の再現、テーマ語彙共有ダミー。
- (MED) 件数: 記事1本ずつでは閾値の採否判断に不十分。「N=1では閾値を決めない、記録のみ」を明記、閾値決定は各構成3本以上の蓄積後(未承認仕様候補)。
## 4. required_structureの可変voice数設計
- (MED) `build_required_structure(level, voice_a, voice_b)`(registry L401)は2声固定の位置引数、`_ROLE_TO_VOICE_RESOLVERS`(L390-398)もvoice_a/voice_bのみ。関数シグネチャ変更必須(PRODUCTION_WIRED関数の変更=要承認)。本TrialでProduction registryを触らずTrial側定義にする方針は正しいが正本の二重化が発生するので、OPEN-132へ「3V/4V required_structureの正本統合」を追記する前提で進めるべき。
- (MED) 組合せ爆発の抑え方(未承認仕様候補): family×level×voice数を列挙せず、`(fixed_prefix, per_voice_template × N, fixed_suffix)`から生成する1関数+`voice_map`方式。
- (MED) level文字列の名前空間が不整合: Gate側`"B1"/"A2"/"B_FAMILY_A2"`(assemble.py L166-179、L362-372)、registry側`"b1"/"a2"`(L406-411)。3V/4Vで4倍化する前に統一方針を決めるべき。
- (HIGH、mandatory化時) `_check_structural_completeness`(assemble.py L318)は未知segmentをUNEXPECTED_EXTRAでblock。mandatory化後に3V/4V構造が未登録のままAssemblyすると全episodeがBLOCK。mandatory化は「3V/4V構造の登録完了」を前提条件にすべき。
## 5. Family横断の矛盾・二重定義
- (HIGH、音声化フェーズ) `DISFLUENCY_QA_MANDATORY_SEGMENTS_BY_LEVEL`(assemble.py L166-179)は`point_one_heading`/`point_two_heading`をベタ書き。3V/4Vで`voice_3_heading`等の新名称を導入するとdisfluency QA必須対象から静かに外れる(fail-open)。`B_FAMILY_A2_SLOWDOWN_TARGET_SEGMENTS`(registry L197-203)も`point_one/point_two`固定で、Voice 3/4本文が6% slowdownを受けない。「Phase 1配線での安全機構未適用」型の再発点。推奨: 本Trial(音声なし)でもsegment命名の設計決定だけは先に行い、上記2テーブルへの登録要否をReportに明記。命名は後戻りコスト最大の決定。
- (MED) A-Family A2は`point_one/point_two`がAoede単一声、B-Familyは同名で別voice。同名再利用を続けるならlevel分離を必ず継承。
- (MED) section分割ユーティリティの非互換: Trial-07 L670-676「Production `split_common_sections_for_point_qa()`と`sf1r1.section_word_counts()`はこの5見出し構造を正しく解釈しない」。語数・尺見積りは6/7見出し用のTrial側parserが必要。
- (MED) Comment言語の二重仕様: B1=英語Charon、B-Family A2=日本語Aoede。design.md B-1の3V/4V Comment 2/3ドラフトは英語のみ。A2の3V/4Vを将来作るなら日本語版が別途必要。
## 6. 将来の4V量産時の後戻りリスク
- (HIGH) segment命名(前項)。既存2V episode・master audio store・review lock keyまで波及。
- (HIGH) Comment Contractのvoice数ハードコード: `VOICES_COMMENT_2_ROLE`(registry L99-115)「One Voiceの後、続けてAnother Voice」、`COMMENT_3`「2つの声を聞き終えた」。3V/4V版を別定数として増殖させると4系統になる。voice数をパラメータ化したrole生成(未承認仕様候補)を今決めておくと安い。
- (MED) Ledgerタグ規約と1行抽出バグ。Voice数が増えるほど免除の質が劣化。
- (MED) 尺・語数目標は未検証の設計目標。Productionのgateとして固定するのは早い。monitoring値として記録。
- (LOW) voice割当の性別ラベル(Fable決定)はSSOTに性別的印象の記載なしからの新情報。判断根拠をReportに1行記録。
## 7. Sonnet委任案への修正提案
追加すべき(必須): 1. Step 0(テーマ/Ledger決定)を置き(a)(b)(c)をユーザーへ提示してから着手(未決ならSTOP)。2. Writer基盤をTrial-07と明記し新規ファイルへ複製(Trial-07/Production編集禁止をSTOP条件に)。3. Analytical Leakage Checkの3V/4V版スキーマ・promptをTrial側で新規作成。4. 6/7見出し用のTrial側section parser+語数集計。5. Ledger Deviation Checker+Local Rewriteを省略しない、または省略するなら明記。6. Fact A'はProduction関数経由で呼び、ON実行時の実block文字列をファイル保存。7. perspective_map(3者/4者版)作成を明示タスク化。8. 一人称"I"の実現状況の観察記録(OPEN-132項目2の材料)。
変更すべき: overlapは有向ペア(3V=6、4V=12)+vs Hook、閾値は記録のみ・N=1で閾値決定しない旨を明記。削る/後回し: OPEN-129 dry-runは「Trial側required_structure定義+構造定義の妥当性レビューのみ」に縮小。費用: ¥100は不足の可能性が高い(TRIAL-07 Report L242/548でwriter stageのみ1記事あたり¥25〜¥165)。上限見直し(例¥400)か、4V 1本のみ先行を推奨。STOP条件(追加): 検証済みLedger未確定/費用上限到達/見出し数が6・7にならない状態がretry上限まで継続/Production・Trial-07・registryへの書込みが必要になった時点/4V記事が賛否2対2に分割された時点。
## 8. Reconciliation Check観点
- (MED) 3V/4V版Comment 2/3文言はdesign.md B-1の手動ドラフトで未承認。Trial内で使うのは可だがReportで「未承認・Trial-only・registry未反映」を明記し、registry/Contractへは一切書かない。
- (MED) 3V/4V required_structureはOPEN-129承認範囲外(opt-in・2V相当のみ)。Trial側定義であることと正本統合をOPEN-132で追跡することをReportに記載。
- (MED) Fact A'の既定stage接続はOPEN-132項目1でPhase 2に予約済み。TrialでON実行自体は承認範囲内だが「既定接続の先取り」と読める記述は避ける。
- (LOW) 3V構成・4V構成・voice割当・目標尺・Tension構造はdesign.mdでUSER_DECISION_REQUIREDのまま列挙。Fableが「承認済み」として渡したものはより新しいユーザー決定に基づくと理解したが、DECISION_LOGでの該当エントリは未確認。委任前にSSOT側の記録有無を確認。
- (LOW) design.md B-1〜B-7を前提として再設計しないことを明記。
---

## 2. Fable検証(Sonnet、2026-09-09、読み取り専用・費用¥0)

Opus 0-A/1-HIGHの指摘(`build_voice_attribution_block()`が`[VOICE_n_EVIDENCE]`
で始まる物理1行のみを抽出し、evidence本体が欠落する)について、コード修正は
一切行わず、既存の実Ledger・実コードを対象に読み取り専用で実測した。

### 2-1. 対象

- コード: `er012_b_family_editorial_type_registry_01.py::build_voice_attribution_
  block()`(L321-338、実測ではOpus指摘のL327-334付近が抽出正規表現・フィルタ処理
  に一致することを確認)。
- Ledger: `er012_output/editorial_b_voices_trial_07/research/verified_fact_
  ledger.txt`(現存する唯一の実Ledger。`a2_free_address_04`/`phase1_02`はいずれも
  このLedgerを再利用しており別ファイルは存在しない)。
- OPEN-131 evidence: `er012_output/open131_fact_attribution_production_wiring_
  evidence_01/`(`b1_on_result.json`・`a2_on_result.json`・`on_off_comparison.
  json`等)。

### 2-2. 手法

`build_voice_attribution_block()`を実際にimportし、上記Ledgerファイル全文を
渡して実行、出力blockの行数・文字数を計測した。あわせて、Ledger中の各
`[VOICE_n_EVIDENCE]`エントリの「実際の複数行本体」(次の空行までの段落)を
パースし、その行数・文字数の合計と比較した。API呼び出し・LLM呼び出しは
一切行っていない(費用¥0)。

### 2-3. 実測結果

| 項目 | 値 |
|---|---|
| Ledger中のevidenceエントリ数(`[VOICE_1/2_EVIDENCE]`) | 11件(VOICE_1: 7件、VOICE_2: 4件) |
| evidence本体(複数行)の合計行数 | 123行 |
| evidence本体(複数行)の合計文字数 | 5,016文字 |
| `build_voice_attribution_block()`が実際に抽出した行数(11エントリの先頭1行のみ) | 11行 |
| 同上、文字数 | 637文字 |
| **行ベース欠落率** | **91.1%**(123→11行) |
| **文字ベース欠落率** | **87.3%**(5,016→637文字) |

各evidence本体には、数値の詳細・出典名・URL・`counter_or_limitation`(限界の
注記)・`verification`(CONFIRMED/PARTIALLY_CONFIRMED等の検証判定)が含まれるが、
抽出されるのは「[VOICE_n_EVIDENCE] n-NN(fact_xxx): 」で始まる要約文の冒頭1行の
みで、`source`・`verification`を含む全ての付随情報が欠落する。

**追加発見(Opus指摘に無い、本検証で新規発見)**: `build_voice_attribution_
block()`内部の抽出フィルタ(`line.strip()`してから`^\[VOICE_\d+_EVIDENCE\]`で
再マッチ)は、Ledger冒頭の「タグ体系」定義行(例:「  [VOICE_1_EVIDENCE] = Voice
1(固定席を好む社員)を支える事実」、行頭に2スペースのインデントあり)も誤って
拾ってしまう(existence-check用の正規表現`_VOICE_EVIDENCE_LINE_RE`は`^`アンカーが
行頭インデントを許容しないため11件のみヒットするが、実際の抽出フィルタは
`.strip()`後にマッチさせるため13行[本来の11件+タグ定義2行]を拾う)。実害は
ノイズ2行の混入のみで主要な欠落率には影響しないが、抽出ロジックの粗さを示す
副次的な証拠。

### 2-4. OPEN-131 evidenceでの確認

`er012_open131_fact_attribution_production_wiring_evidence_01.py`を確認した
ところ、`B1_LEDGER_PATH`/`A2_LEDGER_PATH`は共に上記と同一の
`er012_output/editorial_b_voices_trial_07/research/verified_fact_ledger.txt`
であり(`A2_LEDGER_PATH = B1_LEDGER_PATH`)、OPEN-131のPASS実測(B1/A2とも
verdict REVIEW_REQUIRED→PASS、unsupported_specific_claims 5件/6件→0件)は、
本検証で計測した「87.3%欠落」の同一blockに対して得られたものであることを
確認した。`on_off_comparison.json`のOFF側`unsupported_specific_claims`一覧は
いずれも「発言者・企業名・調査対象が明示されていない」という帰属曖昧起因の
指摘であり、事実誤り・矛盾の指摘は含まれていなかった(免除ルールが本来
想定した対象と一致)。ただし、免除ルールがfalse acceptを許容する上限
(捏造・数値改変を見逃さない保証)は、この欠落した1行のみの入力に対して
確認されたものであり、evidence本体全文を渡した場合との比較実験は行われて
いない。

また、単体テスト`er012_open131_fact_attribution_production_wiring_01_test_
01.py`(L19-21)を確認したところ、テスト用Ledgerサンプルは
`[VOICE_1_EVIDENCE] 1-01(fact_001): Gensler調査、固定席保有者は所属感87%。
source: Bisnow`のように、実Ledger形式とは異なり1エントリを意図的に単一物理行へ
圧縮した合成データのみを使用しており、実運用で発生する複数行evidenceの欠落を
検知する設計にはなっていない(Opus指摘「単体テストは単行サンプルのみ」と一致)。

### 2-5. 結論

Opusの指摘0-A/1-HIGHは、コード読み取り・実Ledgerでの実行・OPEN-131 evidence
JSON確認のいずれによっても裏付けられた。修正(複数行evidenceの塊単位抽出への
変更)は本タスクの範囲外のため実施していない(`OPEN_ITEMS.md`OPEN-131行へ
Production修正候補として記録、要ユーザー承認)。
