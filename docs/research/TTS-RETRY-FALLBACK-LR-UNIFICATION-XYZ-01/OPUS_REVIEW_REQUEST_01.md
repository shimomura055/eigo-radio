# OPUS_REVIEW_REQUEST_01 — 独立技術レビュー依頼(PM_GOVERNANCE 11-3 条件A: X/Y/Z共通核のretry/fallback/LRフロー変更=新しい処理フロー)

管理ID: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_01。依頼者=Fable。対象=`DESIGN_01.md`(以下D*)。**重要論点8件のみ**。要約済みの結論はDESIGN_01 §0。ユーザー原文=`docs/pm/delegation_log/2026-10-26_TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01_USER.md`(`APPROVED_FOR_PRODUCTION`、再承認不要・仕様の是非は問わない)。**仕様ではなく設計の正しさ・安全性・取りこぼしをレビューしてください**。

読む順: DESIGN_01 §0→D1→D4→D6→D10→D13→ROW_MAPPING_01 §1-2→EVIDENCE_PLAN_01 §2-3。コード事実の根拠は棚卸し`COMMON_CORE_01.md §1`。

## O-1. 「3回構成ブロック」抽象は正しいか(D1・D2・DESIGN §5)
- **主張**: 部位差は(a)③のStyle、(b)LR有無、(c)KP英語の③④の3点だけ。`BLOCK_PROFILES`表(9 policy)+`policy.before_attempt`(loop型L1/L2/L8)・`between_stages`(stage型L3/L5/L6/L7)の2アダプタで、leaf本体(TTS/ASR/QA)を書き換えずに全49行を表現できる。cooldownは「③を実際にTTSする直前・①②が通常NGのとき」だけ(Store hit/circuit open/Lock等で③が走らなければ払わない)。
- **疑うべき点**: loop型/stage型の2アダプタは「単一抽象」と呼べるか(実質2種)。`unified_flow_active()`(`er109.current_scope()`)でA/B/Cを温存する二重経路は、将来の保守負債か(撤去はユーザー判断=A/B/C廃止時)。leafが`segment_id`とscopeからpolicyを自己解決する方式(runner call site不変)は、暗黙依存を増やさないか(明示引数`tts_block`と比較)。
- **求める判定**: 抽象の境界(特にstage型でのcooldown位置)が全leafで同一意味か/scope gateの設計が11-7相当の迂回不能性(env・引数・設定dictで変えられない)を満たすか。

## O-2. LRラッパの再入禁止と最大回数(D4・D12)
- **主張**: LR block内は`BlockCtx(depth=1)`で`lr_allowed()==False`、`run_local_rewrite_recovery`にも二重防御のdepthガード。LR block=元と同じleaf・同じ引数(Style含む)・`script_version=v1`・`m1_anchor_text=元原稿`で①'②'→180秒→③'。最大6 attempt・LR 1回・待機2回(360秒)。resumeは`BlockProgress.lr_used`でLR二重実行を防ぐ。累積15(再生成3周目でBUDGET_GUARD)は維持。
- **疑うべき点**: `__wrapped__`呼出でguard(`_ACTIVE_GUARDED_OUT_PATHS`/OPEN-105)を迂回するため、LR block内の途中STOPPED/例外がLock・累積budget・`record_outcome`二重計上に与える影響。LR block①'で書換え後textが別の理由でNGになり続ける場合に、書換え連鎖(OPEN-376 D-B6)が構造的に起きないことの証明。LR成功時の`audio_text_deviation`(最初の書換えのみ記録)と表示本文の整合。
- **求める判定**: 再入禁止が全経路(L1/L2/L3/L4、chunk、resume、approve_regenerate後の再実行)で成立するか/追加の不変条件test案。

## O-3. Z dialogue ctxの統合範囲(D10)
- **主張**: cooldown定数・起点・5秒刻みSTOP確認・resume残り時間は`cooldown_core`へ共通化(Z ctxの設計を正本として採用)。`DialogueAttemptPolicy`のstate machine(`n_started`をTTS前に書く/`counted`・`carried_log`[M-1]/`explicit_regenerate`・`consuming_regenerate_approval`[M-4]/Adv外側ループ行会計[U-07])は**統合しない**(Opusレビュー済み・E-1〜E-6 evidence・26 test・再レビュー不要にするため)。非Z用`BlockProgress`は同一スキーマのsubset。legacy方式は③前180秒のみ追加。
- **疑うべき点**: 統合しないことで「Family別ロジックを増殖させない」(原文§5-4)に反しないか(state machineが2系統残る)。将来統合する場合の移行コスト。`COOLDOWN_SECONDS`をScope内で180、`er122.cooldown_seconds()`が`cooldown_core`へ委譲した際の既存26 testへの影響。
- **求める判定**: 今回は統合しない判断で妥当か/統合するならどの粒度か。

## O-4. U-03(ASR一致だがQA単独NG)の扱い(D5)
- **主張**: ①②→180秒→③は省略せず実行(原文§4)。③NG後に`lr_applicable`(0 API: `identify_ng_span`のfound・技術STOPでない・role等)を判定し、不可なら**LR LLM 0・LR block 0で即HR**。HRQ行は終端NGで必ず1行(LR前書込を廃止: `total_slots=6`でslot3/4/5を非最終化し、LR不可の終端は`register_terminal_hr`で明示登録)。これにより旧OPEN-536(旧=ユーザー判断要)は原文§4が既判断。
- **疑うべき点**: `identify_ng_span`を最終attemptの転写だけで判定する現行仕様のままでよいか(①②③のうちASR差分のあるattemptがあっても最後がQA単独NGならLR不可になる)。`total_slots=6`化が統一judgeの`is_last_slot`判定・`PASS_WITH_WARNING`・`HR queue`重複抑止(`is_duplicate_queue_entry`)と矛盾しないか。技術STOP(Secondary/Whisper不能)が③で出たときの扱い。
- **求める判定**: LR適用可否の位置と条件/HRQ一本化の副作用。

## O-5. Y Gate BLOCKとの整合(D13)
- **主張**: 新仕様の「HR」は生成flowの終端、Y Gate/X M3は採用Gate(別軸)。新仕様でも2026-10-21の『Fallback音声は個別承認、無条件自動採用ではない』は取り消されていない。**本件ではGate規則を変更しない**(`STD_FALLBACK_USED_OR_UNKNOWN`・`LOCAL_REWRITE_RECOVERY`・`ADV_MINIMAL_FALLBACK`等は③/LR採用時に従来どおりBLOCK。Advは③短文Styleが新規に入るため③採用がGate対象になる=Stdと同じ扱いに揃う)。LR block内のStyle純化でOPEN-312起因の余分なBLOCK理由は消える。`block_evidence`付与のみ追加。Gate緩和はデータ(③採用率)を測ってから別途ユーザー判断。
- **疑うべき点**: Adv ③採用が新たにGateでBLOCKされることで、Advの自動化率が落ちる(Delivery悪化)ことを許容してよいか。Gate不変の判断が11-8「承認済み仕様との論理的不整合の是正」に当たらないか(当たるなら本件で是正すべきか)。
- **求める判定**: Gate不変でよいか/是正すべき不整合の見落とし。

## O-6. 撤去による副作用(REMOVAL_01・D6・D11)
1. **D6(Std本文・6%減速)**: 案A=減速+再検証を各attemptの検証の一部にし外側ループ(OPEN-270 M3配管)を撤去/案B=L4をouter guardで包む/案C=U-09を単一例外として据置。**Aを推奨**。Aのリスク=strict/minimalのループ内にwav上書き・`*_original.wav`退避・attempt audio保存順序・chunk検査(`std_chunk_slowdown_violations`)を持ち込む。fzaq8/fzaq2 testの再表現。→ **A/B/Cの選択とAの落とし穴**。
2. **D11**: `resolve_narrative_role`に`topic_intro_en`→TOPIC_INTRO追加。LR+cooldownに加え、`er006._resolve_semantic_equivalence_role`経由でCS Equivalence層(判定)がZ topic introで有効になる。意図どおり(Xの`topic_intro`と同条件)か。
3. **A/B/C byte同一**: scope外のgolden方式(`er122_fz_ctx_fakes_01.build_golden`)で十分か。`FamilyAUnchangedTest`(working tree diff=0)との運用。
4. **表外(A-1)**: shell固定英語を現行維持(旧「Adv Style不変」がこの3行にだけ残る)で良いか。拡張する場合のMaster Audio Store汚染(③音声を通常keyへ保存しない設計)。
5. **`min(max_attempts,3)`クランプ・`PRODUCTION_MAX_TTS_ATTEMPTS=3`の意味を「1ブロック」に再定義**して残す判断。

## O-7. KP英語4回構成と180秒の位置(D8)
- **主張**: 待機はENGLISH_LOCK段の実TTS直前に1回(③④の間は無し)。Store key B hit・Azure/Whisper circuit open・Lock・STOPで後段TTSが走らない場合は待機しない。repro01:797・`er019_family_x_kp_en_k2_store._styled_two_stage`:55・`er063._kp_en_two_stage`:1069の3複製を`kp_two_stage`1実装へ統合(待機以外の挙動は同一であることをregression test)。
- **疑うべき点**: 「待機は通常2回NG後」という原文の文言と、Store hit時に待機しない解釈の整合。3複製統合で`slot_offset/total_slots`・`fallback_attempts_log`合算(record_outcomeの実TTS試行数=4)・vote circuit判定の差分が落ちないか。
- **求める判定**: 位置と統合の安全性。

## O-8. evidence計画の十分性(EVIDENCE_PLAN_01・BUDGET_PLAN_01)
- **主張**: 「代表+固定」(leaf種別ごと代表を実走、Family/レベルはrunner統合を最低1経路、残りはT-MAP 49行+leaf matrix+goldenで固定)。強制NGはFZCW driver方式(判定のNG化のみ)で、LR経路は**Primary転写への1語置換注入**で`identify_ng_span`を成立させ、LR LLM・LR block・実180秒待機・実Gateを実走。U-03はQA gate単独NGで別途再現。Lean 46 case/保守約200円/天井約298円(案件Cap 300円、6 process並列で約51分)。
- **疑うべき点**: 転写置換注入が「LR後も同じGate」の証拠として十分か/注入がjudge以外(Style・待機・回数)に影響しないことの担保。「代表: X」で省くY/Zの(d)(g)が本当に同一leaf・同一共通核で代替できるか。Std本文(L4)のE-S2a(LR PASS)をoffline固定にした判断(費用)。Adv KP解説の短文Style適合性を実測3 takeで判断する妥当性。
- **求める判定**: 不足するcase/過剰なcase、最低限追加すべき実走。

## 付記(Opusへの前提情報)
- 本件は`APPROVED_FOR_PRODUCTION`済みのため、Production直接実装(flag不要)。ただしX/Y/Z run scope限定でA/B/C(Legacy凍結)は不変。
- 並行Agentが`er125_*`/`er105`/`er119`/`er003_v1_n3_01_scaffold_generate.py`を編集中(本件の編集対象と現時点で重複なし。委任_02開始時に再確認)。
- 費用: 本レビューはAPI 0。依頼は1回(同一内容の重複レビューなし)。
