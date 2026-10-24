# DESIGN_01 (ASR-OOV-HOMOPHONE-ROOT-CAUSE-01 委任_01) 対策候補の比較と推奨(実装なし。Trial専用コードのみ、Production無変更)

目的(ユーザー原文§3): 正しい発音を誤NGにせず、実際の誤発音は確実に検出。辞書未登録語・借用語に通用し、既存の仕組みを活用して複雑化しない。誤NG/Azure/TTS再生成の削減、誤PASS非増、X/Z/Y共通、70円/記事セット整合。数値の根拠=`TRIAL_01_RESULT_01.md`、原因=`ROOT_CAUSE_01.md`。

## 1. 候補比較(必須4系統+追加3)
| 候補 | 内容 | 効果(本件/保存データ) | 誤PASSリスク | 複雑さ | 費用 | X/Z/Y共通 | 既存仕様・過去判断との関係 | 判定 |
|---|---|---|---|---|---|---|---|---|
| A | Primary ASR `prompt` へ本文のOOV/固有名詞を渡す | gacha窓 2/8(25%)のみ解消 | **あり**: 実際の誤発音(gaycha)を gacha と書く実例。er065のmaskingと同じ | 小(1引数) | 0 | 共通 | 本文segmentへの拡張は新規(C分類)。KP用promptは承認済みだが目的が別(逐語化) | **非推奨** |
| B | CMU未登録語をG2Pで推定しer109/同音判定へ | 0件(gacha: G2P=/æ/で不一致。保存81件で0) | 緩和すれば増(1音素差12件) | 中(依存追加) | 0 | 共通 | **C3(規則G2P)はM1承認時に不採用、UDR #52に抵触** | **除外(再導入しない)** |
| C | Primary NG時のSecondaryを発話窓に絞る | Azure -87%/呼出(本件-約20円)。ただし再試行は減らず、PhraseListバイアスで gacha と書くため独立証拠にならない | PhraseList masking(gaycha→gacha) | 大(窓特定+新フロー) | -20円/本件 | 共通 | Secondary 1回+cache(L2814)の枠内だが新規入力形式。短clip精度低下(er065) | 単独非推奨(E2補完の保留案) |
| D | `_HOMOPHONE_OVERRIDE_GROUPS` へ個別登録 | gacha 1語のみ | 小 | 小 | 0 | 共通 | OPEN-498案A=ユーザー不採用(UDR #183) | 比較基準のみ |
| E1 | M1の入口を緩め、Ledger読み付きOOVを entity_like 扱い(A-1(a)再採用) | **0**(入口は通るがM1が`MULTI_CANDIDATE_NO_MATCH`) | — | 中 | 0 | 共通 | A-1(a)は2026-09-28 DEFERRED。単独では無効 | 単独では無効 |
| F | 語単位クロスエンジン確認(差分語を相手エンジンが正準どおり転写なら確認) | 保存144行でNG_BOTH 31→10行救済見込み | **高**(時制・語彙の食い違いを許す) | 中 | 小 | 共通 | 「独立証拠」の基準を弱める | **不採用** |
| **E2** | **Ledgerの出典付き読み(M1がsegment開始前に凍結した C2候補)に、ASR語のCMU代表発音が完全一致したら、置換後に既存classifyがPASSなら受理(PASS_WITH_WARNING+事後試聴リスト)** | gacha型を解消。本件Adv part3は attempt1で受理→TTS 8→1、Azure -約15円、全体 -約22円 | 負例14件で誤受理0、保存110ペアで正例3(gacha×2・meink)・誤受理0。Ledger読みの正否に依存(下記)。**音素が同一の別語は音では区別不能=定義上同等** | **小**: 既存凍結候補・IPA変換・classifyを再利用。新辞書・G2P・閾値なし | Phase 2検証のみ | 共通(M1と同じ場所) | **OF-184「直接音素置換は需要をtelemetryで測る」の需要が実証された形**。UDR #52(綴りだけを根拠にしない)には**抵触しない**(根拠は綴りでなく出典付き発音+音素完全一致) | **推奨** |
| E2+G | E2に加え、プラン段階でCMU未登録の小文字語をLedgerへ先行登録(供給側) | 初回出現segmentの救済(Secondary節約)にも効く | Ledger読みの品質に依存 | 中(既存Resolver流用) | 1語あたりの実費は未測定(Phase 2で測る) | 共通 | 新スコープ(Resolverは現状entityのみ) | Phase 2でE2の結果を見て判断(任意) |

## 2. 推奨案: E2(Ledger直接音素一致、M1の拡張として)
### 2-1. 仕様案(新しい処理フロー=Opus条件A対象)
位置: Primary NG(TRUE_CONTENT_MISMATCH/ASR_VALIDATION_UNCERTAIN)の直後、既存M1の次、Secondaryの前(`er006_secondary_asr_01.py`のM1呼出点の隣)。**Primary段で受理できればSecondaryを呼ばない**(Azure削減)。
受理条件(すべて。`trial_direct_ledger_phoneme_01.py`が実装): (1)protected(数値・否定)通過 (2)内容語差が「正準1語→ASR1語」のreplace 1件のみ (3)正準語がCMU未登録かつ凍結済みLedger C2候補(OF-179: segment開始前、OF-181: sources非空・disabled無・canonical_spelling==surface、IPA→ARPAbet決定論変換可)を持つ (4)ASR語がCMU収録で代表発音(ストレス除く)がC2候補のいずれかと完全一致 (5)ASR語を正準語へ置換した転写が既存`classify_asr_match`で should_pass(=他に差が残らない)。
受理時の扱い: 既存M1と同じ `PASS_WITH_WARNING`(理由コード例 `M1_LEDGER_DIRECT_PHONEME_ACCEPT`、audit に ledger_key/updated_at/ipa_raw/confidence/candidate_set_hash)、事後試聴リスト自動登録、値ガード・否定ガードの最終ANDゲートは既存どおり。KP英語phrase(3-ASR多数決)・見出し・日本語は対象外(Tier3のrole gating=5 roleと同じ範囲に限定)。
不変事項: retry/fallback/3回上限/LR/HR Lock/Style Gate、Secondary 1回+cache、Primary#2廃止、PhraseList重み、PASS→NG変化なし(受理を足すだけ)。
設計パラメータ(Phase 2で決定): Ledger confidence下限(medium以上を推奨。meinkはlowで除外される)、evidence_tier要件の有無、全体を1つの単一flag読取関数で既定OFFにする(11-7の5条件)かOffline TrialのままVALIDATEDで止めるか。

### 2-2. 残るリスクと緩和
- **Ledger読みが誤っている**(web検索由来のLLM生成、cascade_unresolved_entity)場合、系統的な誤受理: 緩和=confidence≥medium+PASS_WITH_WARNING+事後試聴リスト+ledger_key別の事後集計(M1既存の`aggregate_by_ledger_key`)。gachaのLedgerは confidence=medium・NAME_IN_CITED_PAGE(名称のみ出典、読みは二次情報)で、**読みの一次確認は未**。
- **音声が実際に別の読み(例 /æ/)でも、ASRが gotcha と書く場合**: 音素が同一なら受理される。Ledgerが両読み(US/UK)を候補に持つ語は両方受理するため、UK読み(/ɡætʃə/)が出た場合は ASR側が gatcha 系(CMU外)や catcher となり非受理になる。→ 学習者に「どちらの読みか」を保証する仕組みではない(既存M1・Tier3と同じ性質。事後試聴リストで人が確認)。
- 初回出現segmentはLedger読みが無く救済されない(従来どおりSecondary)。供給側Gで緩和可。

## 3. 費用・QCD
- Q: 誤PASS増の観測0(14負例+保存110ペア)。ただし**正例は保存データに3件のみ**=本質的に母数が小さい。追加の正例収集(借用語での新規TTS)がPhase 2の主課題。
- D: 本件でTTS再試行・LR・HR・Style Gate・人間承認の連鎖(数十分〜)を回避。
- C: 本件 -約22円(104.73→約82円)。発生頻度が低い(保存データ上 gacha型は1語)ため、期待値は「借用語を含む記事の割合×約22円」。Word Gacha系など借用語が主題の記事で効く。実装コストは小(新規コード数十行+test)。

## 4. 承認済み仕様との整合・撤去/残置
- 整合: CURRENT_SPEC L2794-2801(M1)、L2818(基本フロー)、UDR #52、OF-178〜187、2026-09-28 A-1(a) DEFERRED、E2は受理面の拡張=**新仕様=ユーザー判断事項**(Production採用は未承認、Trialの到達上限=VALIDATED)。
- 撤去: なし。残置: A-1(a)フラグ(OFFのまま)、`_HOMOPHONE_OVERRIDE_GROUPS`(空のまま)、G2P不採用。
- 既存不具合(11-8): F1 `tokenize` の ’ 未対応(ROOT_CAUSE §6)。E2はF1を使わない(val.classifyのみ)ため独立だが、既存M1・Eq Layerの前提不具合として別途修正が望ましい。

## 5. Phase 2 提案(次委任。Fableが判断)
1. E2のTrial module化(`er1xx_ledger_direct_phoneme_trial_01.py`、Production未import)+単体test(負例・境界・凍結契約・DefaultOffIsolation相当)。費用0。
2. Regression: 保存ASR全件(5,604行)の再判定(PASS→NG=0、NG→PASS全件目視)、X/Z golden、Y trial run。費用0。
3. 追加の正例収集(異なる原因の代表ケース): 借用語・造語5〜8語(例 bento/karaoke/sudoku/emoji/blitzscaling/unfollow)を各1〜2文でTTS→Primary→E2判定+Ledger先行登録(G)の1語あたり実費測定。見積 約15〜30円(TTS+ASR+Ledger lookup)。上限案40円。
4. 結果をVALIDATED/不採用で判定(Fable独立評価)→Production採用は人間ユーザー判断(QCD影響・M1との差分・UDR #52整合を明示)。
5. 並行: F1 `tokenize` ’ 修正の可否をFableへ(Production共有file、先行承認)。
