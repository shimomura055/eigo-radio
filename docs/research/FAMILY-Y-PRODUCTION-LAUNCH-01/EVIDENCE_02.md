# EVIDENCE_02: Y runnerへのPart 1/Part 2/文法HR接続 と E-1(宅配)再走の結果

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_06 / 2026-10-25(JST)。**PRODUCTION_WIRED判定はFable。本書は事実の記録であり判定ではない。ユーザーの最終試聴PASSは別Status(未実施)。**

## 0. 結論
- **A(Part 1/Part 2/文法HRのY接続)= 完了**(API 0・test 242 PASS/1 skip)。実API(E-1)で動作確認済み(接続分の実費0.737円)。
- **B(E-1完走・限定公開)= 完走せずSTOP**(公開物なし)。理由は3点で、いずれも**共通Production module側の既存挙動**(Y固有の欠陥ではない):
  1. **a2 `preview`(日本語)**: OPEN-517型の誤NG。ASRが毎回「思い通り」と転写し、正本「思いどおり」と**かな/漢字の表記差**だけで不合格(6 attempt、`approve_regenerate`後の3 attemptも同じ転写)。音声自体は正しく「おもいどおり」と読まれている。
  2. **b1b/a2 `y_voice_1`(英語)**: ASRは全attemptで一致(EXACT/NORMALIZED_MATCH)だが、**Repetition QAの短ラグ検査(D')が閾値0.6秒を境界で超える**(0.60〜0.83秒)ため不合格。approve後に3〜4 attempt追加しても通らず、その後に**ER-020 Local Rewriteが自動で起動し、承認済みR0本文の語を書き換えた**(`redeliveries`→`repeat deliveries`)。この音声は本文と一致しないため、Y Gateが`LOCAL_REWRITE_RECOVERY`でBLOCKした(**Gateは回避していない**)。
  3. 上記により組立・ページ・公開は未実行。**NG音声の最終採用承認(`approved_by="user"`)は行っていない**(禁止事項)。再度の`approve_regenerate`も行っていない。
- 実費: 本委任 **20.062円**(接続0.737+b1b y_voice_1 5.579+a2 13.746)。Y累計は下記§7のとおり **約166.85円/Cap 170円(残約3.15円)**。**委任_05の較正費17.644円が本委任の「既支出129.14円」に含まれていなかった**ため、委任文の「残40.86円」は実際には約23円だった(Cap内には収まっている)。
- **EVIDENCE_01の訂正**(§8): 「Advanced(b1b)音声は完成」は誤り。b1b `y_voice_1`も当時すでにHR Lock(STOPPED、3 attempt)だった。Y style gateはb1bをPASSと表示したが、これは「Style/fallback検査のみ」の結果で、音声検証(AVG)は`assemble`で別に掛かる設計のため、`assemble`には進めなかった。

## 1. 実行条件・版
- コード: HEAD `d2bbce56c`(委任_06 Part A)+作業木の他agent未commit変更(委任_05のtext core等。run時点でtext stageは再利用[API 0]のため未使用。`origin/main`の`a035605a6`と作業木のtext coreは差分なし)。Lock/ASR/Repetition QA/Local Rewrite等の共通moduleは**無変更**。
- 起動(すべて`.venv\Scripts\python.exe`。`py`ではgoogle.genaiが無く起動直後に`rc=2`[API 0・原因明確]。`console_ypl6_launch1.log`は上書きしたため§付録参照):
  | # | 時刻 | stages | rc | 内容 |
  |---|---|---|---|---|
  | L1b | 21:58:53 | seed_check,text,translate,support,kp | **4**(文法待機) | Part 2候補抽出1 call(0.481円)。KP/テキストは再利用(API 0)。`review_request.md`に文法のpendingが出た |
  | (宣言) | 22:00:02 | — | — | 文法候補sha `d09c110a…`に紐づく**新しい不在宣言**`d_42edcb6d9e37`(旧KP宣言`d_bf821f18b541`は`_ypl6_pre_snapshot/`へ退避。KPは確定済みで再読込なし) |
  | L2 | 22:03:5x | 同上 | 0 | Part 1(解説0.107+訳0.059)+Part 2 Step B 0.090=0.256円 |
  | L3 | 22:05:36 | tts_b1b(`--regenerate-stage tts_b1b`) | 0(stage内で`y_voice_1`は再度STOP/Local Rewrite→OK扱い) | b1b y_voice_1のみ再試行。5.579円 |
  | L4 | 22:19:3x | tts_a2,gate,assemble,pages,page_verify(`--regenerate-stage tts_a2`) | **2**(`FAMILY_Y_GATE_BLOCK`) | a2 preview・y_voice_1のみ再試行。13.746円。gateでBLOCK |
  RESTART_STORM(5分3回)なし(L1失敗起動[21:58:47]と L1b[21:58:53]の後、L2は5分以上あけた)。`tools/stop_scope_check_01.py`は各起動前にrc=0(`stop_check_ypl6_l{1,2,3,4}.json`)。
- 日次(JST): 開始時1,200.32円(daily_dev_cost_01)+未捕捉94.28=約1,294.6円 → 終了時1,229.16+94.28=約1,323.4円(日次1,500円内)。

## 2. A. Part 1/Part 2/文法HRのY接続(`er121_family_y_runner_01.py`ほか)
変更点(すべてX/Zと同形。共通核er119/er120/er003_kp_*を呼ぶだけで再実装なし):
- **stage内の配置**: `kp` stageの先頭で`_part2_cand_step`(Step A'')をKP候補生成より前に実行 → KP(b1b/a2)と文法のpendingを1つの`review_request.md`/rc=4にまとめる(`YKpReviewPending`、pendingのkind="grammar"/"kp")。確定後に`kp_expl_b1b`→`kp_part1_b1b`(5件・Advのみ。入力=`vocab_confirmed.json`の`part1_items`)→`kp_part1_ja_b1b`(引用英文の訳)→`_assemble_study_rows`→`part2_b1b`(Step B。`input_sha`=本文sha|label|文法確定署名)。
- **使う側の入口(fail-closed)**: `_assert_study_ready`(KP確定+Part 1解説・訳の最新性+`require_final`)を`stage_tts(b1b)`/`stage_gate`/`stage_assemble`/`stage_pages`/`stage_page_verify`の入口で呼ぶ。未確定=rc=4待機、無い/古い/不整合=STOP(次コマンド付き)。gate/assembleは既存の`_require_fresh`(TTS stale検査)の**後**に呼ぶ(既存のSTOP順序を変えない)。
- **公開ページ**: `stage_pages`が`render_html_block`(Part 1)→`compose_page_html`(Part 2をPart 1の直後。0件は固定文面)→Advancedレベルの`study_html`にだけ載せる。`page_verify`は`verify_outputs`(確定↔part2_result↔md↔HTML)+ Part 2ブロックが`id='advanced'`より後に1個・Part 1の直後にあること+ KP検証5(`verify_selection_matches_outputs`)を実行。
- `UNIT_NAMES`に`kp_part1_b1b`/`kp_part1_ja_b1b`/`part2_cand_b1b`/`part2_b1b`を追加(`--regenerate-stage`の許可値)。`DEPENDENTS`: `translate_b1b→part2_cand_b1b→part2_b1b`。`seed_check`のrouting検査へ`STUDY_TEXT_GRAMMAR_EXTRACT/EXPLAIN`を追加(登録済みkeyの存在確認のみ)。`study_text_slots.json`の「未接続」記述を撤去(接続済み+各stageの状態)。
- **B-4(final_manifest)**: `stage_entries`のtext/kp/support等のmodel欄null(転記漏れ)を、費用ログ(`cost_log.jsonl`)のstageタグ集計(`models_used`)とtext_recordsの`routes`(voice_generate/lead/intros/closing: routing_key・model_id・effort・prompt_sha256)から転記。単一modelなら`actual_model_id`を埋める(複数modelのtextは`models_used`で示す)。E-3の保存済み記録で再現確認済み(API 0): support/kp系=`gpt-6-luna`、textは`{gpt-6.1-sol:10, gpt-6-luna:13}`+closing route。`chunk_tts`表記もOT-44(b)に従い`applied_X_method`へ更新(旧`not_applicable_Y`は撤去)。
- test(`.venv`・socket/client遮断harness): 新規 `StudyTextWiring`(8)、`StudyTextStructureMatchWithXZ`(2: Zの共通核呼出し ⊆ Yの呼出し[許可リスト付き]、5入口が`_assert_study_ready`を呼ぶ)、`ManifestModelTransfer`(2)。観点: 待機1回(KP+文法)・確定前のStep B/Part 1/TTSが0 call・HRあり再開でStep B 1回/Part 1 各1回・再開API 0・Advのみ表示・Part 1→Part 2の順・0件固定文面・fail-closed入口(結果欠落/Part 1欠落/未確定)・HRなし(不在宣言→`UNREVIEWED_AUTO_ADOPTED`)。回帰: runner+structure+audio chunk+text wiring+text core(読むだけ)+text core article = **242 passed, 1 skipped**。既存testの更新: API境界の許可kind追加、`study_text_slots`の期待値(未接続→接続済み)、`manifest.chunk_tts`の期待値、`NoticeDisplay`の許可リスト(`user_test/family_y_*`のYの限定公開dirはY自身の公開物。E-3の公開以降このtestが落ちていた既存不整合の是正)。
- 実API確認(E-1): 文法候補=2件(TOP1: P4 `CMP`「the same fee as…」)、不在宣言で`UNREVIEWED_AUTO_ADOPTED`・`ng=[]`・verdicts全null・`last_human_op_at=null`・宣言ID `d_42edcb6d9e37`(候補sha紐づけ)。Part 2結果`SELECTED`(model `gpt-6-luna`、Step A''+B)。Part 1は5件(sit right with someone / take the trouble / on top of / when it suits someone / end up receiving)、解説+訳とも`PROVIDED`(model `gpt-6-luna`、prompt sha `086bb354…`/`c11b9dc7…`)。接続分の実費**0.737円**(E-1)。

## 3. B. E-1 Lock原因の仕様照合(記録ベース。再現は実施済みのapprove後attemptを含む)
ER-011 Lock対象は**3 segment**(委任文の2 segmentに加え、b1b `y_voice_1`)。

| segment | 失敗の中身(attempt) | 既存仕様で本来PASSか | 判定 |
|---|---|---|---|
| a2 `preview`(ja) | 全6 attempt(approve前3+後3)が`ASR_VALIDATION_UNCERTAIN`。ASR転写「思い**通り**に」vs正本「思い**どお**りに」。Secondary(Azure)も同じ転写で`secondary_not_accepted`→`NG_BOTH` | **PASS相当**(読みは正しい)。同音・異表記の救済が動かない=**OPEN-517(JA ASR false-NG)と同型**。決定論の再現(API 0): `classify_ja_asr_match`が`ASR_VALIDATION_UNCERTAIN`(reason「読みが濁点/半濁点の有無を除き一致(Cascade対象、即PASSにはしない)」、`どお`↔`通`のdiff)を返し、Secondaryも同表記のため救済されない | 共通module既存欠陥(OPEN-517)。**修正は別委任(07A=F1+F2適用は「合格範囲を狭める」側のみで本件は救済されない。②B-light案βの適用待ち)** |
| b1b `y_voice_1`(en) | 全7 attempt中、ASRは一致(EXACT×4/NORMALIZED×3)。**Repetition QA D'(短ラグ0.5〜2.0秒、類似度0.7)の最長run=0.61/0.67/0.83/0.83/0.61/0.60秒 > 閾値0.6秒でflagged**。長ラグ検査(方式D)は`local_asr_confirmation.confirmed=false`で非flag、n-gram検査も非flag。最終attempt7(0.54)のみ非flagだが、これはLocal Rewrite後の別文(下記) | **QA仕様どおりの動作**(閾値0.6秒はTrial-02較正値。変更不可)。ただし**境界での偽陽性の疑い**: Y body全32 attemptのD'最長runは0.2〜0.54秒が大半で、この本文だけ0.60〜0.83秒。flag位置はt=2.1/10.0/31.0/42.5秒で本文の別々の箇所=特定の語でなく本文全体の反復的な`deliver…`語(redeliveries / deliver / delivery)が近接する本文に起因する傾向 | 共通module(er011 Repetition QA)の閾値は変更しない。別OPEN候補(下記§7) |
| a2 `y_voice_1`(en) | attempt1: NORMALIZED_MATCH、D'=0.68>0.6でflag。attempt2: ASR内容が正本と**異なる**(「was not home」→「is not home」、Azureは「I want→I wanted」も)=`TRUE_CONTENT_MISMATCH`。approve後: attempt4 D'=0.74、attempt5 D'=0.62でflag、attempt6(minimal fallback)は`TRUE_CONTENT_MISMATCH` | attempt1/4/5は**QA閾値の境界flag**、attempt2/6は**TTSの本物の読み違い**(was→is)。**ハイフン差(`re-deliveries`)自体は正規化で救済される**(`classify_asr_match`: 「表記正規化(…ハイフン…)後に一致」)。委任文の仮説(ハイフン差でUNCERTAIN)は半分誤り: attempt2のUNCERTAINは`was→is`の実差が主因 | 仕様どおり(NGは正当) |

**ER-020 Local Rewriteの起動(本委任で初めて表面化した所見)**: `y_voice_1`(b1b/a2)は、approve後の標準attemptが再びQAでflagされたあと、`LOCAL_REWRITE_RECOVERY`が走り、最後のattemptのASR転写が`re-deliveries`(ハイフン付き)だったことで`identify_ng_span`(`er020_tts_retry_local_rewrite_01.py:206-231`)が`asr_validation.tokenize`の素のトークン差分(`redeliveries` vs `re` `deliveries`)を**NG span**と判定し、luna候補生成→QA→`short_phrase_rewrite`として**`redeliveries`を`repeat deliveries`に書き換えた**(`local_rewrite_recovery.status=RESOLVED_BY_LOCAL_REWRITE`、b1b attempt7 EXACT_MATCH verified=True、D'=0.54)。分類器(`classify_asr_match`)は同じ転写を`NORMALIZED_MATCH`とみなしているのに、NG span特定は同じ正規化を使わない=**共通moduleの不整合**。結果として「QA(反復)だけが落ちた文」の語が承認済みR0本文から書き換えられた。初回のb1b(21:11)はASRがハイフン無しだったためNG span無し(`HUMAN_REVIEW_LOCKED_NO_NG_SPAN`)で書換えなしだった。
- この書換え音声は本文(R0 byte一致)と一致しないため、Y Gateが`LOCAL_REWRITE_RECOVERY`(b1b/a2)+`STD_FALLBACK_USED_OR_UNKNOWN`(a2)でBLOCK。**Gateを回避・無効化していない**。ER-020の承認フロー(人が書換え音声を承認)にも進めていない。
- **R0音声(書換え前)は保全されている**(下記§5の試聴対象)。

## 4. B. `approve_regenerate`の適用記録(Fable権限による追加再生成の許可。NG音声の最終採用承認ではない)
- 操作者表記: `approved_by="Fable権限による追加再生成の許可(Sonnet実行・委任_06。NG音声の最終採用承認ではない)"`(ER-011 storeの`approved_by`に記録)。**`approved_by="user"`は使っていない**。
- 対象と時刻: b1b `y_voice_1` 22:05:19(L3直前)、a2 `preview`・`y_voice_1` 22:19:31(L4直前)。**各segment 1回のみ**(再度のapproveなし)。テキストは正本の`'`正規化版(ER-011のsha一致を確認してから付与)。
- 結果: b1b `y_voice_1`=標準3 attempt flag→Local Rewrite→`status=OK`(ただし書換え音声)。a2 `preview`=3 attempt全て同じ`NG_BOTH`(再STOP)。a2 `y_voice_1`=標準2+fallback1 flag/不一致→Local Rewrite→`status=OK`(ただし書換え音声・fallback使用)。
- これに伴い**委任文の「2 segment」を超え、b1b `y_voice_1`にも1回適用した**(E-1完走に必要で、同一の権限範囲[追加再生成の許可のみ]。この拡張はFableが取消すことも可能)。

## 5. E-1の最終成果物(失敗終了時の最終状態)
- 場所: `er121_output/family_y_production_01/redelivery_fee/run_01/`(組立wav・ページ・final_manifestは**未生成**)。`gate_summary.json`: b1b BLOCK(`y_voice_1: LOCAL_REWRITE_RECOVERY`)、a2 BLOCK(`y_voice_1: STD_FALLBACK_USED_OR_UNKNOWN, LOCAL_REWRITE_RECOVERY`)。a2 `preview`は`STOPPED`(Lock再発)。
- ユーザー試聴判断のための**ローカルwav**(NG音声の最終採用承認はユーザーのみ。承認は`er011_human_review_lock_01`の`record_human_approval`/ER-020承認フロー):
  - **a2 preview**(正本「…思いどおりに…」。ASR「思い通りに」。耳で「おもいどおり」と聞こえれば表記差のみ): `…/a2/narration/attempts/preview_attempt{1,2,4,5}_customb8f0ff16.wav`(minimal fallbackは`preview_attempt{3,6}_minimalfallback.wav`)。
  - **b1b y_voice_1**(R0本文のまま。ASR一致・D'の最長runのみ0.6超): 候補=`…/b1b/narration/attempts/y_voice_1_attempt5_englishstyleprefixwidemargin.wav`(EXACT・D'=0.61)、`…attempt1…`(EXACT・0.61)、`…attempt6…`(NORMALIZED・0.60)。attempt3/4(0.83)・attempt2(0.67)は長い。attempt7(0.54)は**書換え音声なので不可**。
  - **a2 y_voice_1**(R0本文のまま): 候補=`…/a2/narration/attempts/y_voice_1_attempt5_custom53fd514d.wav`(NORMALIZED・D'=0.62)、`…attempt1…`(0.68)。attempt4(0.74)・attempt2/6(was→is等の実差)は不可。a2の確定は6%減速処理(`Y_MISSING_MANDATORY_A2_SLOWDOWN`)も通す必要がある点に注意。
  - `…/{b1b,a2}/narration/y_voice_1.wav`は現在**書換え版**(提出不可)。
- 選択肢(Fable判断): (a)ユーザーがR0 wavを試聴し承認(Lock/ER-020承認フロー経由)、(b)OPEN-517の救済(②B-light案β等)がProductionに入った後に再走、(c)新仕様候補: Y Voiceの文境界Chunk(OT-42: 現状1段落契約でChunk分割0)でD'の偽陽性を構造的に避ける(承認済み仕様の変更=ユーザー判断)、(d)Preview文言のみ再生成(`support_a2`、約3円)で「思いどおり」を避ける(ASRの誤NG回避のための本文変更に当たるため推奨度は低い。Fable判断)。

## 6. 受入条件13項目(USER_02 §6)の対応(E-1再走後。未達は未達)
| # | 条件 | E-3 | E-1(本委任後) | 判定 |
|---|---|---|---|---|
| 1 | 5パート・3 Voice構造 | 完走 | TTS 8 segment×2 levelは生成(b1b y_voice_1・a2 preview/y_voice_1は上記)。組立未 | E-3で達成。E-1未達 |
| 2 | 承認済みVoice生成方式 | Sol high×3(+UNMAPPED再生成) | R0再利用(byte一致、EVIDENCE_01) | 達成(E-3/E-1) |
| 3 | Prompt 02+Sol high | 達成 | 不使用(案B固定) | E-3で達成 |
| 4 | 宅配のみ案B | — | 案B判定PASS(EVIDENCE_01、textは本委任で再利用) | 達成(判定1回PASS。委任_05の「≤3回判定」経路はE-1 textが再利用のため未発火) |
| 5 | X方式Chunk+0.2秒ポーズ | 分割0(1段落契約) | b1b/a2とも`chunk_tts_decision.json`=`applied_X_method`、全segment`paragraphs=1<2`で分割0 | **機構は組込済・実分割の実走evidenceなし**(OT-42は未解消) |
| 6 | KP・文法HRあり/なし | KP:HRあり確認、文法:未接続だった | **文法HRなしを実走確認**(新宣言→`UNREVIEWED_AUTO_ADOPTED`)、KP HRなしは既存。**文法HRあり経路の実API確認は未実施**(mock testのみ) | **一部未達**(文法HRありは実走なし) |
| 7 | 承認済みXYZ共通仕様 | Part 1/2を除き達成 | **Part 1/Part 2接続済み**(実API確認) | Y側の接続は達成。公開物evidenceはE-1が未完走のため未取得 |
| 8 | retry/fallback/regeneration/resume | 確認済み | resume API 0・Lock維持・approve後の再試行・Local Rewrite起動・Gate BLOCKを確認(回避なし) | 達成(仕様維持の確認) |
| 9 | Gate・Regression・integration | E-3 PASS | E-1: **Gate BLOCK(正当)**。test 242 PASS | **E-1未達**(Gate PASSに至らず) |
| 10 | 実model_id・routing・Prompt等の記録 | 記録済み | `provenance.json`にPart 1/2のmodel・prompt sha。manifestのmodel転記は修正済み(E-3保存記録で再現確認)。**E-1のfinal_manifestは未生成** | 部分(E-3相当のmanifest実物は次回完走時) |
| 11 | SSOT更新 | — | OPEN-520/484最小追記、本書・COST_ANALYSIS_01・BUDGET_LOG_02・OPEN_TRACKING_05 | 達成(本委任分) |
| 12 | Git commit/push | — | 実施 | 達成 |
| 13 | Fable独立受入 | — | 未(Fable) | — |

## 7. 所見・OPEN候補(11-8分類)
| # | 所見 | 分類 | 備考 |
|---|---|---|---|
| F-1 | Repetition QA D'(短ラグ)が長尺Y Voice(40〜50秒、130語超の1段落)で閾値境界(0.60〜0.83秒)に張り付く。E-3は通過、E-1 y_voice_1は本文固有に連続flag(7 attempt中6) | **ユーザー判断要の可能性(共通module閾値/Y Voiceの文境界Chunk=新仕様)**。分類=D(真に新しい判断)。発生は本文依存で、E-1の宅配の本文のみ | 本委任では変更しない。別OPEN候補。ChunkはOT-42と同根 |
| F-2 | ER-020 `identify_ng_span`がハイフン付きASR転写(`re-deliveries`)を正規化せずNG span化し、**QA(反復)のみ失敗の文でR0本文の語を書き換える**(`redeliveries`→`repeat deliveries`) | **修正へ進む(共通module不整合。ER-020の別委任)**。分類=B(承認範囲内。既存の「表記正規化」仕様との不整合=11-8の不具合) | Y側ではGateが止めたため実害なし(公開物なし)。X/Zでも同条件で起こり得る |
| F-3 | a2 preview(JA)の「思いどおり/思い通り」誤NG=OPEN-517。07A(F1+F2)は救済側ではない | 修正へ進む(別委任・07B/08の案β適用待ち) | OPEN-517/522〜524で追跡中 |
| F-4 | `y_style_gate`は音声のstatus(STOPPED/HUMAN_REVIEW_LOCKED)を検査しない設計(Style/fallback専用)。`gate_summary`のPASS≠音声検証OK。最終防衛は`assemble`のAVG | 実害なし(assembleで止まる)。EVIDENCE_01の「b1b完成」は誤記→訂正 | 必要ならgateにstatus検査の追加を別委任で |
| F-5 | UNMAPPED再生成の個別理由がrecordに残らない(件数のみ) | 修正へ進む(text core所有の別委任、U-1) | COST_ANALYSIS_01 |
| F-6 | 運用: `pending_banner`の再開コマンドが`py …`(グローバルpythonにgoogle.genaiが無い環境では起動直後にrc=2)。`.venv`のpythonで実行する必要がある | 実害なし(運用注記。OPERATIONS_01へ追記候補) | 本委任では`.venv`で実行 |
| F-7 | 共有`attempt_history.jsonl`/Lock storeの`theme_id`がrun名(`run_01`)で、E-3とE-1の記録が同一theme_idで混在する(出典の区別は`level`+`segment_id`+text shaのみ) | 実害なし(Lockのkeyはrun dir単位のstoreなので衝突しない)が、監査ログの突合が難しい | 記録 |
| F-8 | **Y累計Capの管理**: 並行した委任_05の較正費17.644円が本委任の「既支出」に入っていなかった | 運用(Fable) | 実際の累計は約166.85円 |

## 8. EVIDENCE_01の訂正
- 「Advanced(b1b)音声は完成」→ **誤り**。b1b `y_voice_1`は21:11:34にHR Lock(STOPPED、標準3 attempt、`HUMAN_REVIEW_LOCKED_NO_NG_SPAN`)に入っていた。`gate_summary`のb1b=PASSは`y_style_gate`のStyle/fallback検査のみの結果で、音声status(AVG)は`assemble`で別に掛かる(F-4)。
- 「`y_voice_1`のRepetition QA/ハイフン差」: attempt1のQAは正しい(D'境界)、attempt2のUNCERTAINは`was→is`の実差が主因でハイフン差は主因ではない(§3)。
- 「`preview` JA false-NG疑い(未検証)」→ 検証済み(決定論再現、OPEN-517型)。
