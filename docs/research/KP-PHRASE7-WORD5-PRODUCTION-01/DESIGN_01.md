# DESIGN_01: Key Phrase最大7件 + Key Word最大5件 分離抽出のProduction配線設計
KP-PHRASE7-WORD5-PRODUCTION-01 委任_01 / 2026-10-27 / 設計のみ(コード無編集・API 0・JPY0)。到達上限=DESIGN_READY。
Status: ユーザー正式採用(APPROVED_FOR_PRODUCTION、2026-10-27、原文`docs/pm/delegation_log/2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_USER.md`)。目標=PRODUCTION_WIRED(X/Y/Z x Std/Adv)。**Opus条件A(`OPUS_REVIEW_REQUEST_01.md`)を実装前に実施**。現行は`CURRENT_PIPELINE_01.md`、分類は`INVENTORY_ABC_01.md`。

## 0. 方針
承認済み仕様の配線であり、**新規flagは作らず既定ONの正規実装**(11-7限定例外は不要。DefaultOffIsolationではなくDefaultOn testで担保)。変更の核は(1)call1のPrompt差替(Prompt 2->P7)、(2)call2のPrompt差替(Prompt 2-V->W5')、(3)件数・補完の**種類別上限**(フレーズ7/単語5/合計12)の3点。Gate(validate/CMU/containment/canonicalization/gloss/RQA/救済)・HR・finalize・フォームの契約は**追記のみ**で変えない。Prompt 2とPrompt 2-Vの本文・shaは**1字も変えず残置**する(旧runのresume・復帰の部品)。

## 1. Prompt設計(a)
### 1-1 P7(call1、フレーズ最大7件)
- 本文=Trial-02で用いたP7をそのまま使う(`er124_kp_phrase_word_trial_01.py:62-93 _build_prompts`が`ft.PROMPT_2_TEXT`から**冒頭の件数文と条件6だけ置換**して生成。条件1〜5と最終確認文はProduction Prompt 2と逐語同一)。sha256=`2e93019300f960e5ff3070dd83b12a81566b8ceb87b44b335d554a7a711eb291`(本日import実測)。原文§3末尾「Key Phrase側もTrialで用いた最大7件・順位付け・本文一致等の既存承認仕様を守る。今回未承認の新たなフレーズ抽出規則は導入しない」に一致。新規規則は無し。
- P7条件6の「互いに同一、または一方がもう一方を含む類似の表現を重ねて選ばない」「各候補に日本語理由1文40字以内」はTrialで用いたP7の既存文言(原文が「Trialで用いた…を守る」と指定)。
- 本文は新moduleへ**コピーせず、同一の生成式**(`ft.PROMPT_2_TEXT`からreplace)で作り、import時にshaをassert(`er119_kp_prompt_2v_01.py:31-36`と同じ方式)。

### 1-2 W5'(call2、Key Word最大5件) — W5本文の1行だけを原文どおりに是正
- 基準本文=Trial-02 W5(`er124:100-123 W5_TEXT`、sha`3502f0ac813ca651c7f0cb6acb0ed86365e8f93d9e03e6b258322ed9471eb9d8`)。条件1〜5(原文§3の5条件と**同一順序・同一文言**)、補足1行目(条件3・4>条件5)、条件1・2必須、出力規則(最大5・順位付け・数合わせ禁止・理由1文40字以内・出力直前に本文照合と1語再確認・語数併記)は**無変更**。
- **変更するのは補足の2行目1箇所のみ**。原文§3補足「すでに選定されたKey Phraseに含まれる単語は、Key Word候補から除外する」を反映する。Trial W5は逆の文言で、Gate`duplicate_of_top3`と食い違っていた(STATUS_02 §5-3)。

| | 文言 |
|---|---|
| 現行Trial W5(`er124:115-116`) | 「- すでに選ばれたフレーズ・表現に含まれる単語であっても、それだけを理由に一律除外しない。学習価値の重複は評価してよいが、新たな絶対条件にはしない。」 |
| W5'(案) | 「- すでに選ばれたフレーズ・表現に含まれる単語は、選ばない(候補から除外する)。この除外は、条件1・2(絶対条件)とは別に適用する候補構成の規則である。」 |

- W5'のsha256(案)=`187f1b87d025b4f95d8ea9cf2f71c863009d1427b91304b67769ec14421bbaad`(本日`W5_TEXT.replace`で実測)。**文言の最終確定はFable(+Opus)**(D4)。第2文は原文「絶対条件は1・2のみ。重複除外は別途承認された候補構成規則として適用する」の言い換えで、条件の意味・順序は変えない。逐語優先なら第1文のみで足りる(sha再計算)。
- 条件4(易語除外)は絶対条件でないまま(原文§2/§3: 易語混入は許容)。**易語の混入をGate・test・evidenceの失敗条件にしない**。
- 条件順の確認: ①本文一致(絶対)②1語(絶対)③上級者向け学習価値④易語除外(絶対でない)⑤単語単体の学習価値(必須でない・固有名詞/数字/記事固有語は考慮で避ける)。補足=③④>⑤、⑤を理由に③④適合語を不当に除外しない、KP含有語は除外。

### 1-3 message組立・schema
- P7: `P7_TEXT + ft.BODY_DELIMITER + 本文`(+再選定時のみ`ft.NOTE_DELIMITER`+機械診断note。Prompt本文不変、`er105:109-119`と同じ本文後置方式)。W5': `W5'_TEXT + BODY_DELIMITER + 本文 + p2v.ALREADY_DELIMITER + "- フレーズ…"`(`er124:137-140`と同形)。
- JSON schemaはP7・W5'とも**2-Vのschema**(phrase/reason_ja/word_count、`er119_kp_prompt_2v_01.py:40-60`)を再利用(P7でreason_jaが必要。Trial-02で実績あり)。parseは`p2v.parse_selection`。call関数は`p2v.make_vocab_selector_fn`(model=`ft.resolve_model(process)`=gpt-6-luna、routing照合・response.model照合・HTTP400即停止は既存のまま)。
- 新module名(提案): `er119_kp_p7w5_prompts_01.py`(P7/W5'本文・sha pin・message builder・`KP_PHRASE_MAX=7, KP_WORD_MAX=5`)。A/B/Cから非importを`er119_isolation_test_01.py:71`の対象に追加。

## 2. 件数・種類・順序(b)(c)
- `rv.KP_CANDIDATE_MAX 8->12`(`er119_kp_human_review_01.py:52`)。参照は`candidates:429,443,467,580`のみ(shortfall/cap/補完room)。`shortfall=len(cands)<12`は従来どおり「上限未達の情報」であり**エラーではない**(件数は上限で満たす必要なし=原文§2)。`shortfall_detail`に`cap_by_kind={"phrase":7,"word":5}`・`missing_by_kind`を**追記**(既存キー`cap/missing/E_total/backfilled/unfilled_by_kind`は不変)。HR依頼書の表・フォームexportは既存契約のまま(フォームの7/5枠は`export_form_data_01.py:137`で既に仕様)。
- 種類(`kind`)は現行どおり候補組立時に`bf.kind_of_phrase(used_form)`(スペース無し1語=word)で付与(`candidates:253`、DATA_CONTRACT既存)。kindの源泉はcall1/call2の出自ではなく基本形化後のused_form(変更しない)。
- `ai_rank`: Gate通過後の通し連番、**call1(フレーズ、P7順位)->call2(単語、W5'順位)->補完(末尾追加)**。現行の「call1順->call2順->補完」と同一規則。補完フレーズは単語の後ろに付くが、フォームexportがkind別に分割するため表示は崩れない(HR依頼書は`ai_rank`昇順で、旗に「補完候補」と出る=`render_request_md:1236`)。
- **種類別cap強制**(新、組立直後・補完前): used_formのkindでフレーズ>7または単語>5になった場合、下位(ai_rank大)を`dropped(stage="overflow_kind")`へ。`overflow`同様**Eに数えない**(`NOT_COUNTED_STAGES`へ追加)。承認済み上限(7/5)の維持であり新規抽出規則ではない。想定頻度ほぼ0(Trial-02のP7返答34件に単語0件)。

## 3. Gate(d)
| Gate | 7+5での扱い | 根拠 |
|---|---|---|
| 本文一致 | `ft.validate_and_resolve`(本文連続一致`er105:225-278`)。無変更 | 原文§3-1 |
| 1語(単語) | W5'本文(LLM)+**機械確認(§3-A、設計判断D3)** | 原文§3-2 |
| フレーズ包含重複除外(KP含有語の単語除外) | 二重: (i)W5'本文 (ii)`run_vocab_selection`の`duplicate_of_top3`(`candidates:95-96`、比較先=call1の`display_phrase`、双方向containment)。Gate無変更 | 原文§3補足 |
| CMU/Human NG/除外句 | 現行どおり(call1=`er105`内、call2=`run_vocab_selection:100,104`) | - |
| canonicalization/gloss/CMU post-canon/記号/人称[Z]/SRC D1[Z]/RQA | 単語にも現行どおり(`_gate_chain`は種類を区別しない) | 原文§4 |
| 救済(er125) | 現行どおり(選定段H2は`validate_and_resolve`内で発火) | OPEN-529 |

### 3-A 「1語」の機械確認(設計判断D3)
原文§3はKey Wordの絶対条件2「1語」と「出力直前に1語条件を再確認」を求める。W5'本文はこれを含む(LLM側)が、現行Gateにはcall2の1語検査が無い(2-V=単語/フレーズ混在のため)。
- (X)推奨: W5'経路の`run_vocab_selection`でのみ、`validate`後に`count_words(phrase)!=1`のitemを`dropped(stage="not_single_word")`にする。原文条件2の**Gate化**であり新規抽出規則ではない。Eに数える(AIが選んだKWがGate除外された=KW枠で補完)。`count_exclusions`のkind判定は`stage=="not_single_word"`のときkind="word"固定(元phraseは複数語のため)。
- (Y): LLMのみ。複数語が来ても組立後にkind=phraseとなりフレーズ枠に入る/overflow_kindで落ちる。原文の絶対条件が保証されない。
推奨=X(品質Q: 絶対条件は機械で担保)。

## 4. HR自動推奨・Adv vocab5(c)
- 現行`auto_select`(`rv:536-555`)は**ai_rank順の先頭**から`kp=chosen[:3]`、`vocab=chosen[:5]`(Advのみ、KPを含む)。7+5でも**コード無変更**で動く: kp=P7上位3(フレーズ)、vocab(Adv)=P7上位5(フレーズ)。
- 旧3+5との差: 旧は`vocab`の4,5番目がcall2先頭2件(単語/フレーズ混在)。新は4,5番目がP7の4,5位フレーズ。**単語はAUTOでは選ばれない**(単語はai_rank 8前後以降)。
- AUTOは**明示の不在宣言があるときだけ**走る(`ensure_kp_review:1354`)。通常運用はHuman選択(フォームv3)。フォームの区分(①フレーズ<=3、②=①+②<=5、③=①+②+③<=12)は「ユーザーが12候補から選ぶ」UI上限で、Production slot(`kp`<=3/`vocab`<=5)とは別層(KCP `CURRENT_FLOW_01 §0`)。
- 単語をAUTOのvocab枠へ入れる規則は**新仕様**(原文に無い) -> 本委任では導入しない。**D2**: (a)現行維持(推奨) / (b)Advのvocab 4,5番目に先頭の適格単語を組み入れ(新仕様=ユーザー承認要)。実害=不在宣言AUTOでAdvの②解説に単語が入らない点だが、旧方式でも単語が入る保証はなかった(call2混在)。
- `render_request_md`の「単語」印(`mark`)は`top_vocab`(AUTO vocab集合、Advのみ)を指し、7+5ではフレーズ4,5位に付く。文言変更は表示変更=新仕様候補のため行わない。フォーム側は`kind`で単語を正しく表示。依頼書の表(`:1204-1250`)は12行になるが上限文言は無く追加変更不要。

## 5. 補完(e) — 承認済み仕様を維持し、種類別上限・種類別Promptへ
維持する承認仕様(原文§4、DESIGN_02 §4): (1)AIが実際に選定した候補がGate除外された場合だけ (2)Eを超えない (3)初回上限未満自体は発動条件にしない (4)Gate合格・救済済みは保持 (5)補完候補にも同一Gate (6)フレーズ/単語を区別し7+5を守る (7)不要な再生成・再課金をしない。
- **発動条件(確定)**: `backfill_enabled() and E_total>=1 and 現存候補>=1 and (フレーズ空き>=1 または 単語空き>=1)`。E=0は不発動(LLM 0)。**委任文の「E>=1かつ初回上限到達」は現行コードに無く、原文(初回が上限未満自体を条件にしない)にも反するため採らない**(現行`_run_backfill:464-469`は既に原文どおり)。
- **種類別の計数と上限**(`plan_quota`の置換): `quota_phrase=min(E_phrase, 7-現存フレーズ数)`、`quota_word=min(E_word, 5-現存単語数)`、`total=quota_phrase+quota_word`。旧`cap=KP_CANDIDATE_MAX`・`BACKFILL_MAX_CALL_ITEMS=5`によるmin(…,5)は廃止。種類をまたぐ数合わせはしない(`pick_backfill`は現行どおり種類別quota)。
- **補完Prompt=初回と同じPrompt**: フレーズ補完=P7(+除外note[`ft.build_exclusion_note`、件数文言を可変化=A-7]+現存候補の機械除外+`ALREADY_DELIMITER`節)、単語補完=W5'(+ALREADY節=現存候補[フレーズ・単語]の`shown_phrases`+除外note)。P7への「すでに選ばれた表現」はW5'と同じ`ALREADY_DELIMITER`節を本文後置(新規文言なし、P7本文不変)。Prompt 2-Vは補完でも使わない(混在・最大5でE_phrase最大7に不足)。根拠: 原文§4「補完候補にも適切な同一品質条件・Gate」。
- 呼出: quota>0の種類のみ(最大2 call)。2 callは入力が独立(同じcands snapshot)なので**並列実行可**(原則2)。比較先は常にcall1(M-5不変)。
- Gate連鎖は**両種類の結果を結合して1回**(canonicalization呼出を増やさない=費用)。結合後に(i)基本形化後の重複(R-3)、(ii)**補完単語 x 全フレーズのcontainment**(補完単語が補完フレーズに含まれる場合を落とす。`stage="backfill_duplicate"`、Nに数えない)、その後`pick_backfill`。
- 既存単語を含む新規補完フレーズは「初回合格候補は保持」を優先して**既存単語を落とさない**(原文§4「既存合格候補を保持」)。低頻度(Opus論点7)。
- 失敗時: 現行どおり`backfill.status=FAILED`で初回候補続行(M-6)、STOP/routing違反は伝播(R-8)。`stop_check("kp_backfill:…")`は補完call前に1回(M-4)。
- 記録: `backfill.prompts={phrase:{id,sha256,model_id,response_id}, word:{…}}`を**追記**。旧`prompt_id/prompt_sha256`(スカラー)は互換のため残し値は`"per_kind"`(`collect_evidence_02.py`等の読取を壊さないよう実装時に全Grep)。

## 6. attempt loop(f) / call1のitem不適合
call1は`er105:run_selection_gate`の**attempt loop(MAX_ATTEMPTS=2)を維持**(承認済み仕様。独自変更しない)。P7でも「1件でもitem不適合なら全件を機械診断noteで再選定、最終attemptはCMU未登録・除外句のみ落とす」(`er105:511-526`)。P7は最大7件のため全体INVALID(->外側retry、¥0.12/回+)の確率は3件時より高くなりうるが、**Trial-02のP7返答34件にGate不合格0件**。K1(item単位化、OPEN-547)は承認済み仕様の変更=区分Dのため導入しない。evidenceで`call1_attempts`/`outer_attempts`を記録して事後判断。
- 実装: `run_selection_gate`/`validate_and_resolve`/`apply_exclusions`/`build_user_message`/`prompt_prefix_intact`/`run_fulltext_selection`に**keyword-only既定値付き**引数`prompt_text=None, max_items=None, parse_fn=None`を追加(既定=従来のPrompt 2/3件/`parse_selection`=**既存呼出の挙動は不変**。既存er105 test+er003 wiring testで回帰担保)。新入口`select_p7`は`er105.run_fulltext_selection`をP7パラメータで呼び、metadata(`prompt_id="kp_prompt_p7"`, `prompt_sha256=P7_SHA`)を同形式で書く(`bf.read_call1_dropped`互換)。reason_jaは`resolved[i]["reason_ja"]`に載せ`build_original_items`でitemへ通す(A-6)。

## 7. retry / fallback / regeneration / resume(g)
| 事象 | 7+5での挙動 | 根拠 |
|---|---|---|
| resume(候補doc有り・本文sha一致) | **再生成しない**(API 0)。旧3+5のdocは旧のまま読戻し(provenanceはlogのみ) | `ensure_kp_review:1303,1330` |
| 外側retry(call1/call2失敗・live 0・canon全体失敗) | 現行どおり周回(max3)。周回ごとにcall1(P7)も再実行=従来と同じ課金構造(call1結果の再利用最適化はC-5、未実装) | `candidates:306-337` |
| 補完 | 1周1回。失敗は初回候補で続行 | `candidates:371-382` |
| 再選定(reselect、round>=2) | Human NG(`excluded`)を除外してP7+W5'を再実行(round1が旧3+5でもround2は7+5)。docの`prompt_sha256`で出自追跡可 | `ensure_kp_review:1330-1337` |
| 本文変更(STALE) | 旧候補/確定物をSUPERSEDEDへ退避して再生成(既存。確定内容保護の境界はKCP) | `ensure_kp_review:1316-1328` |
| 確定内容の書換え | 7+5は`finalize_kp`/`_final_items`/確定物に**触れない**。候補docはcandidates_sha256でreviewに結び付き、手編集はfail-closed(`KpReviewInconsistent`) | `finalize_kp:932`, `ensure_kp_review:1313-1315` |
| 進行中の旧候補(例: OPEN-526 X AI島 Std5/Adv7、HR待ち) | **再生成しない**(自動置換はHR待ち候補を失う)。7+5は新規生成・reselect・本文変更後の再生成から適用 | resume規則 |

## 8. test更新(h) — 詳細は`TEST_PLAN_01.md`
sha固定test: Prompt 2(`a12896f4…`)・2-V(`e1d5349c…`)の既存pin testは**据置**(本文不変・残置)。新規にP7(`2e930193…`)・W5'(`187f1b87…`案)のpin testを追加。`KP_CANDIDATE_MAX`既存test(`er119_kp_human_review_01_test_01.py:79`, `er119_kp_backfill_test_01.py:238`)は12へ。`er119_kp_backfill_test_01.py`の`plan_quota`/`pick_backfill`/`BACKFILL_MAX_CALL_ITEMS`系(22参照)を種類別上限へ改訂。`er106_joint_runtime_evidence_01.py:45`(旧run判定用`KPFT_PROMPT_2_SHA256`)は旧run専用と明記し新docのP7 shaを許容。

## 9. flagと旧方式への復帰手段(h) — Fable設計判断D1
- 新しいON/OFF flagは**作らない**(承認済み仕様の既定ON実装)。`EIGO_KP_BACKFILL`のkill switchが保護するのは「任意の追加層」でOFFの復帰先が承認済みの旧基準だったが、ここでの復帰先はsuperseded方式。`EIGO_KP_BACKFILL`自体は7+5でも有効(OFFで補完撤去・旧外側retry条件へ。この組合せも7+5の種類別上限でtestする)。
- 選択肢: **R0(推奨)**=runtime flagなし。単一commit(Prompt差替+上限+補完改訂)で配線し、`git revert`1手順で旧3+5へ戻す(OPEN-474と同じ運用)。旧Prompt 2/2-Vは残置するため差し戻しは機械的。**R1**=`EIGO_KP_P7W5=0`で3+5へ復帰(単一読取関数・既定ON)。メリット=再配備なしの即時切替。デメリット=2経路の恒久保守・test倍化、superseded挙動が環境変数で再現可能になり承認済み仕様の単一性が弱まる、補完のkind別Prompt・cap(8/12)も二重化。推奨理由: 品質Qに対し単一の承認済み経路を保つ方が安全で、local運用では切替速度の利益が小さい。
- 撤去・残置(Charter 8): Prompt 2/2-V本文・pin test・`run_vocab_selection`の2-V既定は**残置**(旧run resume/R1選択時/legacy `run_kp_with_outer_retry`[`er003:753`]のため)。配線後に`Grep "PROMPT_2V_TEXT|PROMPT_2_TEXT"`でProduction候補生成経路からの未参照を確認し、撤去はD1確定後の別commitで判断。

## 10. 費用・時間(i)
- 実測(Trial-02 `COMPARISON_02.md`「時間・費用」): 7+5の1 level平均**¥1.76(5.0 call)+P7 1 call ¥0.12=約¥1.88**。前回(P7+W3)¥1.83、7+3は現行3+5比**+¥0.19/level(約+¥0.4/記事セット)**(`STATUS_01 §3`)。7+5は約+¥0.05/level。見込み=**約+¥0.24/level、約+¥0.5/記事セット(目標¥70の約0.7%)**。内訳=P7出力増・canonicalization/gloss/RQA入力の候補増(8->最大12)。
- 追加が発生しうる箇所: 補完(従来同様E>=1時のみ、最大+2 call)、P7 attempt再選定(+¥0.12/回)。非発火時は0。
- 時間: call1->call2は直列(W5'がcall1の確定フレーズを入力に要する=前工程出力依存)。Trial実測で1 level平均+25秒程度(Trial-02 elapsed 178秒=前回r1と同等)。
- 原価低減余地(原則3): call1結果の外側retry間再利用(C-5)は未承認の外側retry変更に触れるため提案止まり。

## 11. Fable設計判断事項(推奨付き)
| ID | 論点 | 選択肢 | 推奨 |
|---|---|---|---|
| D1 | 旧3+5への復帰手段 | R0 flagなし(git revert) / R1 `EIGO_KP_P7W5=0` | **R0**(§9) |
| D2 | Adv AUTOのvocab5へ単語を入れるか(新仕様) | (a)現行維持 / (b)単語組入れ | **(a)**。(b)は新仕様=ユーザー承認が必要 |
| D3 | Key Wordの「1語」機械確認(Gate化) | X追加 / Yなし | **X**(原文の絶対条件をGateで担保) |
| D4 | W5'補足行の文言(第2文の有無) | 2文案 / 逐語1文案 | Fable/Opusで確定(sha再計算) |
| D5 | 補完のPrompt | 種類別P7/W5' / 2-V継続 | **種類別**(§5) |
| D6 | 進行中の旧HR候補を7+5へ作り直すか | 作り直さない / 作り直す | **作り直さない**(HR待ち候補の喪失回避) |
