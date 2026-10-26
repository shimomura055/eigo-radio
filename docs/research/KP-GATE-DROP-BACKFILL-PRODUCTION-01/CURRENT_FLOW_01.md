# CURRENT_FLOW_01: KP候補生成の現行フローと外側retryの事実(KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_01、2026-10-26、read-only・API 0)

照合ファイル:行は全て本日のworking tree。コードは編集していない。

## 1. 共通核(X/Y/Z・Std/Adv共通)の入口
- 単一入口: `er119_kp_candidates_01.py:157 generate_candidates` -> `:166 _generate_candidates_impl`(`er125.rescue_context()`の文脈内)。
- 呼出点: X=`er019_family_x_audio_production_runner_01.py:452`(`er119_kp_wiring_01`経由、`er119_kp_wiring_01.py:69 make_generate_fn`)、Y=`er121_family_y_runner_01.py:543,562`(最初からwiring経由)、Z=`er026_family_z_fiction_production_runner_01.py:1948,1974`(`kcand.make_z_src_fn`/`make_person_repair_fn`を注入)。**3 Familyとも同じ`_generate_candidates_impl`を通る**=補完の配線点は1箇所。
- 永続化/resume: `er119_kp_human_review_01.py:1272 ensure_kp_review`。保存済み`kp_candidates.json`があれば再生成せず読み戻し(`:1284`、API 0)。生成するのは`cands is None or review is None or status==RESELECTION_REQUESTED`のときだけ(`:1309-1316`)。本文sha変更=STALE(旧候補をSUPERSEDEDへ退避しNG保持して再生成、`:1294-1306`)。
- A/B/C: `er119_isolation_test_01.py`(`ALLOWED`にX/Zランナーのみ)で`er119_`のimportを制限。A/B/Cは`er119`を通らない。

## 2. 1回の候補生成(1 outer attempt)の段(`er119_kp_candidates_01.py`)
| 段 | 場所 | 除外の単位 | 除外時の扱い |
|---|---|---|---|
| call1: Prompt 2(3件、sha固定) | :189 `select_fn`=`sc.run_key_phrase_selection`->`er105.run_selection_gate`(`er105:456`) | **attempt単位**。validate/CMU不合格itemがあると`INVALID`でその3件全体を再選定(MAX_ATTEMPTS=2[`er105:38`]、2回目以降は機械診断noteを後置[`:483,530`])。最終attemptのCMU未登録のみ例外的にitem除外(`:517-519`) | 初回に通ったitemも再選定で入れ替わる(**attempt内の全件再選定**) |
| call2: Prompt 2-V(最大5件、`er119_kp_prompt_2v_01.py:19`) | :206 `run_vocab_selection`(:37) | **item単位**: validate(本文連続一致/1-5語/有限助動詞等、救済H2込み)->`duplicate_of_top3`(call1の3件との同一/包含、`_containment` :32,:83)->明示除外(Human NG/外側retry累積、`source`をstageに)->CMU(:94)。6件目以降は`overflow`(:97-100) | droppedへ(stage付き)。技術/parse失敗のみ最大2回再試行(:46) |
| canonicalization(+救済H3) | :249-273 | **item単位**: INVALIDなら`item_reasons`のitemを除外し残りで再実行(`MAX_CANON_RERUN=2`)。全体PASS/REVIEW_REQUIREDのみ受理(M-7a) | dropped(stage=canonicalization) |
| CMU post-canon / 記号 / 人称整合[Z] / SRC D1[Z] | :285-306 | item単位 | dropped(stage=cmu_post_canon/symbol/src_d1)。人称整合の不能は除外でなく`gloss_hr_pending`旗(:311) |
| Human NG再照合 | :318-336 | item単位 | dropped(stage=human_ng)。similarは旗(`similar_to_ng`)で候補に残る |
| 候補組立+救済annot | :322-346 | - | `auto_eligible = not(qa_fail or gloss_hr_pending or similar_to_ng)`。**救済済み候補は除外でなく正式候補**(`er125.annotate_candidate`、rescue_blocks_autoでauto不可になる場合も候補に残る) |
| Redundancy QA | :349-366 | **除外せず旗のみ**(`redundant_with`) | 確定集合には`finalize`で再適用(M-8) |
- 上限: `KP_CANDIDATE_MAX=8`(`er119_kp_human_review_01.py:49`)は**提示件数の上限**。実装上、AI選定は最大3+5=8件なので候補生成側では超過しない(`shortfall = 件数<8`:374は記録のみ)。`KP_FINAL_MAX=3`(KP確定)・`VOCAB_COUNT_MAX=5`(Advの単語解説、候補プールからauto_selectが先頭5を取る、`:536-554`)。
- **Adv単語解説は別選定ではない**: `auto_select(level=b1b)`が同じ候補プールから`vocab=chosen[:5]`を取る(`:552-553`)。`run_vocab_selection`(名称は"vocab"だがPrompt 2-Vの汎用追加選定)は単語専用でなく、単語・フレーズ混在の追加最大5件。現行Productionに「フレーズ枠/単語枠」の分離は無い(分離は`er124`の7+5 Trial=未採用のみ)。

## 3. 外側retry(`er119_kp_candidates_01.py:182-368`)の事実
- 状態: `outer`ループ(`max_outer=sc.KP_OUTER_RETRY_MAX=3`、`er003:656`)。各周で**call1(Prompt 2)とcall2(Prompt 2-V)を最初から再実行**。
- 発動条件(:355): `n_auto < KP_FINAL_MAX(3) and (gate_dropped or rescued_not_auto) and not last`。`gate_dropped`=droppedのうちstageが`human_ng/overflow/duplicate_of_top3/excluded`以外(:347)。`rescued_not_auto`=救済済みだがauto不可(M3、:353)。
- 発動時の動作(:356-362): gate_droppedの句を理由付きで`excluded`へ累積(F1)、`dropped_all=[]`、**ループ先頭へ=候補listを丸ごと再生成して置き換える**(docstring:6「候補list全体を置き換える。roundに内mergeしない」)。最終採用は最後の周の`cands`のみ(:371 `cands_final`)。
- 技術失敗(call1/call2失敗、live 0、canonicalization全体失敗)も同じループ(`continue`、:191-258)。最終周で失敗なら`OUTER_RETRY_EXHAUSTED`(FAILED)。
- 起源: 初案DESIGN_01(HR KP)からのFable/Opus設計(M-7c、`docs/research/KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/OPUS_REVIEW_01.md:54`)。`CURRENT_SPEC.md`にはM-7c本文の記載なし(Grep `M-7c`=0件、F1累積除外[`CURRENT_SPEC.md:2013`]とREVIEW_REQUIRED[:1983、旧`run_kp_with_outer_retry`経路]の記述のみ)。ユーザー原文に外側retryの記述なし。
- **事実(矛盾の特定)**: 現行の外側retryは、Gate除外が出て`n_auto<3`のとき「初回に合格した候補も含めて全て再選定し置き換える」。ユーザー原文§3-1「初回に合格した候補は保持し、再生成・入れ替えをしない」と**運用上矛盾**する。ただし`n_auto<3`のときだけ発動するため、実例(AI島Std: n_auto=5、`KP_CANDIDATE_COUNT_CHECK_01.md:§1`)では**発動していない**(outer_attempts=1)。発動すると、除外が無い周の候補も入れ替わる。
- 同様に、call1の**attempt内全件再選定**(上表1行目)も「初回合格の入れ替え」に当たる(外側retryとは別機構。hard requirement不合格時のみ)。

## 4. 救済(KP-GATE-EXCLUSION-RESCUE、PRODUCTION_WIRED待ち/配線済み。`DESIGN_03.md`)との順序
- 救済は`validate_and_resolve`内(H2、call1/call2共通)とcanonicalization内(H3: postprocess[roles->rescue]、gloss強制再整合+QA再判定)で**除外判定の前に**行われ、救済成立したitemはdroppedに入らず`flags.rescued=true`の正式候補になる(`DESIGN_03.md §1,§5`)。auto不可でも候補に残る(`rescued_not_auto`)。
- 従って「除外件数」を**候補組立後のdropped(Gate stage)**で数えれば、救済済み候補は構造的に数えられない(後述DESIGN_01 §2)。

## 5. Human NG / HR / resume / 再生成の現行
- Human NG: `ng_entries`->`excluded`(source=human_ng)でcall1の機械診断noteとcall2の`ex_keys`へ(:179-181,:78-91)、選定後の`match_ng`再照合(:318-336、used_form・救済前の元句も)。exactは除外、similarは旗。
- RESELECTION_REQUESTED: 新roundで`generate_candidates(round_no+1, ng_entries)`を最初から(ensure_kp_review :1309-1316)。
- resume: 保存済み候補を読み戻し、生成関数を呼ばない(API 0)。`candidates_sha256`は候補doc全体(rescueメタ込み)。
- `--regenerate-stage`: Yは`ctx.regenerate_stage`(`er121:168,207`)、Zは`_regen_for`(`er026:1283`)。KP stageの確定済みHRは再抽選しない設計(`KP-GRAMMAR-HUMAN-REVIEW-PRODUCTION-01/TEST_PLAN_01.md:13`)。

## 6. 既知の除外事例(evidence候補)
AI島Std(run_ai_01 a2): call2の`too soon to wave a flag`(6語)=validate除外、canonicalization INVALIDで`studied separately`除外(計2)、Adv=0。再配達(Y)Std除外2/Adv1、SNS年齢(Y)Adv2、猿の手(Z)Adv=`interferes`(`duplicate_of_top3`)、UK(X)Std=数字。出典: `KP_CANDIDATE_COUNT_CHECK_01.md §4`、`KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02/COMPARISON_02.md:7,109-111,122`。
