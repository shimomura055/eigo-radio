# DESIGN_01: KP一般化N5方式の正式Production配線 設計(KP-GENERALIZATION-N5-PRODUCTION-WIRING-01 委任_01、2026-10-30、API 0・実装なし。**実装前にOpus独立レビュー[条件A:新しい処理フローの設計]を受ける**)

原文=`docs/pm/delegation_log/2026-10-30_KP-GENERALIZATION-N5-PRODUCTION-WIRING-01_USER.md`(:7-9 N5=APPROVED_FOR_PRODUCTION/最終目標PRODUCTION_WIRED、:21 D/E1L/E4/N2再判断不要、:59 新Gate・Prompt改善禁止)。現状=`CURRENT_STATE_01.md`(以下 CS)。Trial元=`docs/research/KP-GENERALIZATION-MEANING-PRESERVATION-TRIAL-03/`(以下 T3)。
状態: **設計案(未レビュー・未実装)**。Productionコード/Prompt/Validator/閾値の変更は本委任で0。

## 0. 設計の結論(推奨)
**N5を既定ON(flagなし)の正式経路として `er119_kp_candidates_01.py` の合流点2か所へ配線し、N5本体は新Production module `er138_kp_n5_generalization_01.py`(Trialコードはimportせず移植・Prompt shaを回帰testで固定)に置く。** 既存のcanonicalization(規則1〜5・QA12項目)・gloss再整合・救済・presentable filterは**無変更で維持**し、N5の一般化は「その後ろに足す表示形レイヤ」とする(新Gate・Prompt改善・閾値変更を作らない=原文:59)。
| 層 | 内容 | 配線位置 |
|---|---|---|
| L1 候補プール+塊判定(N5上流) | P7(live)∪B1過剰生成 → 既存の本文一致/語数/CMU Gate → SEL → pick(cap7) | `_generate_candidates_impl`のcall2直後・`_screen_human_ng`の後・`_gate_chain`の前(`er119_kp_candidates_01.py:403-430`の間)。補完は`_run_backfill`内(`:641`の前)でSEL+pickのみ |
| L2 既存canon(無変更) | `sc.run_key_phrase_canonicalization`(規則1〜5・QA12・possessor_roles・gloss再整合・救済H3) | `canon_fn`(`:209,366-368`)そのまま |
| L3 N5表示形レイヤ | GEN5 → VER5(FIX/revert) → CHK5(全件) → 確定。`used_form`=`key_phrase`=N5形、`japanese_gloss`=N5確定gloss、`source_span`=本文根拠(無変更)、旧canon形は`n5.canon_key_phrase_pre`に保存 | `canon_fn`を包むwrapper(canonが成功した直後・`merged`返却前)。`_gate_chain`の初回(`:430`)と補完(`:641`)が同じcanon_fnを呼ぶため**1か所の包みで両経路に効く** |
理由: (1)全分岐(初回/外側retry/補完/再選定round/本文変更STALE)は`_generate_candidates_impl`と`canon_fn`の内側(CS §2) (2)resumeは保存docの読戻しのみ=再生成せず旧方式へ「戻る」経路でもない (3)N5固有の判定(VER5/CHK5)を既存QA12の「代わり」にしないので承認済みGate(spec①)を変更しない。

## 1. 11-8 線引き
| 区分 | 内容 |
|---|---|
| 範囲内(自己解決) | N5の忠実な移植(Prompt/モデル/工程順/判定条件/revert・fix規則/パラメータ)、routing・pricing登録(25節手順)、WordNetデータのvendoring、回帰fixture・test、cost telemetry、既存矛盾の是正(例: 追加fieldのpassthrough漏れ、N5形に対するNG照合・ga人称整合が`used_form`/`key_phrase`で一貫すること)、旧Trial参照の整理 |
| 範囲外(実装せずFable報告) | 新しい品質Gate/Prompt改善/閾値変更、QA12項目・presentable filterの変更/撤去、候補数を満たすための補充(N5のrevert/除外は補充しない)、単語(W5')へのN5拡張(Trial未検証)、kill switchによる旧方式への復帰手段の新設 |

## 2. 配線方式の詳細
### 2-1 新module `er138_kp_n5_generalization_01.py`(名称はer135(別worker編集中)/er137(origin既存)との衝突回避。着手時に`ls er13*`で再確認)
- 公開関数: `pool_and_select(text, units, originals, meta, ..., include_b1)`(L1)、`wrap_canon(base_canon_fn)`(L3、`canon_fn`と同シグネチャ・同戻り値形)、`audit_record()`(doc用: モデルrequested/actual、prompt sha、FLAGS_V1_HASH、方式id=`N5@T3-2026-10-30`)。
- 移植元(Trialコードはimportしない): `kpg01_validate`(display_check/same_word/lemmas/strip_trailing_slot/wn_multiword)、`kpg01_gen2`(GEN2_RULES/assemble/tokenize/LABELS)、`kpg01_methods`(prompt_B1/B1_SCHEMA/BODY)、`kpg01_methods2._contains`、`kpg02_methods`(FRAG、lemmas複数形補正、WordNet lock)、`kpg03_methods`(CHUNK_DEFS_V3/EXTRA_RULES_V3/SEL3_SCHEMA/prompt_S3/collect[B1部]/select/pick)、`kpg04_methods`(GEN5_EXTRA/GEN5_SCHEMA/prompt_G5/_norm_hw/reconcile/generalize5/VER5/revert_form/span_gloss/revert_to_span/fix_drops_content/verify5/FLAGS_V1/flag_item/CHK5/run_check/pack)。**Trial専用で移植しないもの**: `kpg04_llm`のCap/ledger/phase/SALT/mock(Productionの`_guard`+`er005_cost_logger`を使う)、probe・評価・page・stats。
- 移植時に**改変してよいのは**: 入出力の型変換(Production itemとの往復)、LLM呼出の差し替え(Production呼出基盤)、cost loggerのstageタグ、`stop_check_fn`呼出の挿入、Trialのcache key算出の撤去。**改変しないもの**: Prompt本文・schema・工程順・判定条件・閾値・max_out/think_budget/effort・revert/fix規則。
- JSON途切れ時のmax_out×1.6を1回だけ再試行する挙動(`kpg04_llm.call`)は**Trial確定版の挙動の一部**として移植する(Productionの技術失敗retry[`MAX_ATTEMPTS=2`+sleep]とは別層。同一失敗に二重適用しない順序: 先にmax_out拡大1回→なお失敗は技術失敗として既存retryへ)。

### 2-2 N5工程⇔Production工程の対応(CS §4の差分表に基づく)
| N5工程 | モデル | Production側の置き場 | 既存Gateとの関係 |
|---|---|---|---|
| B1過剰生成 | gpt-6-luna | L1 | B1出力は`ft.validate_and_resolve`(本文一致・1〜5語)+`cmu.reasons_for_phrase`を通す(Trialは`span_in_text`のみ)。**Gateで落ちたB1候補はTrial比で差分になり得る**→回帰testでは「N5モジュール単体」と「Gate適用後の統合」を分けて評価(§4) |
| SEL(E1L上流) | gpt-6-luna | L1 | keep=cls C かつ非passive。non-keepは`dropped`へstage=`n5_select`(`bf.NOT_COUNTED_STAGES`へ追加し、Eに数えず補完を誘発しない=「候補数を満たすために補充しない」を維持) |
| pick(cap7、難易度順は並びのみ) | - | L1 | 易しい表現は除外しない(難易度4段階表示と無関係。CS §3) |
| GEN5 | gpt-6-luna | L3 | 入力は`source_span`+`source_sentence`(Trialの`span`/`sentence`と同一。canonicalizationが変えない) |
| VER5 | gemini-3.8-flash(think_budget=0) | L3 | FIX/REJECT/revert。REJECT・revert不能は`dropped`へstage=`n5_verify`(Gate除外としてEに数える=既存の補完仕様[KP-GATE-DROP-BACKFILL]の範囲) |
| CHK5(全件) | gpt-6.1-sol(effort=low) | L3 | SHIFT系はfix採用/revert/除外。除外はstage=`n5_check`(Eに数える) |
| 決定論flag(FLAGS_V1) | - | L3 | 記録のみ(N5はscope=all) |
対象は**フレーズ(kind=phrase)のみ**。単語(W5'/kind=word)はTrial未検証かつ一般化対象外で現状維持(`bf.kind_of_phrase`)。

### 2-3 既存コードの修正点(最小)
`er119_kp_candidates_01.py`: (a)L1呼出挿入、(b)既定`canon_fn`を`n5.wrap_canon(...)`で包む(`:366-368`。test注入`canon_fn`は包まない=現行どおり注入優先)、(c)`doc`に`generalization`記録(方式id/モデル/prompt sha/FLAGS hash/N5統計)を追加、(d)`bf.NOT_COUNTED_STAGES`/`GATE_DROP_EXEMPT_STAGES`に`n5_select`を追加(`er119_kp_backfill_01.py:23-25`)。`er006_model_routing_contract_01.py`: PROCESS_MODEL_MAPにN5用process追加(§3-1)。`er005_output/cost_baseline_01/pricing_snapshot.json`: gemini-3.8-flash追加。各runnerの`STAGE_EST_JPY["kp"]`(Y `er121:35`、Z `er026:1237`、X相当)をN5分上方修正(予算guard用の見積値のみ)。

### 2-4 既定ON・flagなし・旧方式へ戻る状態の排除
- 承認済み(原文:7-9)のため**既定ON**。DEV/Trial専用flagにしない。env kill switch(`EIGO_KP_RESCUE`型)は**新設しない**を推奨: N5は方式の置換であり、flag OFF=旧方式復帰は原文§3「retry時だけ旧方式へ戻る状態を防ぐ」と同型のリスクを恒久化する。撤退手段=N5導入commitの単一`git revert`(`er003_key_words_gloss_alignment.py:124`と同型)。→判断候補ではなく設計判断(分類B)。Opusに妥当性確認。
- 旧方式に戻る経路の網羅・遮断: CS §2の表。X非Production互換分岐(`er019...:1000-1002`、`kp_backend!=fulltext_p2`)と旧`sc.run_key_phrases(fulltext_p2)`は正式runnerから到達不能であることを**到達性test**で固定(§4-3)し、コードは削除しない(A/B/C・旧run復帰のため。範囲外)。

## 3. 設計詳細
### 3-1 routing / モデル / 価格
- `PROCESS_MODEL_MAP`(`er006_model_routing_contract_01.py:82-`)へ**追加のみ・既存キー不変・リテラル固定**: `KP_N5_VERIFY: "gemini-3.8-flash"`、`KP_N5_CHECK: "gpt-6.1-sol"`。B1/SEL/GEN5は既存`A2_SUPPORT`/`B1_SUPPORT`(=SUPPORT_MODEL gpt-6-luna、`:91-92`)を`require_model(process, SUPPORT_MODEL)`で解決(KP選定・原型化と同一契約)。CHK5の別系列モデルは**Trial確定版と同一(gpt-6.1-sol、VER5=gemini-3.8-flashとも別系列)**。
- 応答モデル照合: OpenAI系は`response.model`==要求(既存`ft.ModelMismatchError`と同型)。Gemini系はSDK応答の`model_version`が取得できる場合は照合し、取れない場合は「要求名=actual」と記録しその旨を証跡に明記(Trialは`mid=model`固定[`kpg02_llm.py`]で照合なし=**改善余地。ただし挙動変更ではなく記録の厳格化**)。
- `ModelContractViolation`/STOPは握らず伝播(`bf.is_propagating_exception`、`er119_kp_backfill_01.py:41`)。runnerは`[STOP]` rc=2(自動retry・再生成・迂回なし)。技術失敗(通信等)は既存の`MAX_ATTEMPTS=2`+`sleep(2)`型retryのみ。**N5段が失敗した場合に旧方式(N5なし)で続行しない**(fail-closed)。
- 価格: `pricing_snapshot.json`に`gemini-3.8-flash`が無い(gpt-6.1-sol/gpt-6-lunaは登録あり)ため、公式単価取得→登録→`PricingNotFoundError`(fail-closed)が出ないことをtestで確認(25節 25-2)。最新モデル原則(25節)との整合: luna=最新世代効率系(Production SUPPORT_MODELと同一)、gemini-3.8-flash=最新世代Flash、gpt-6.1-sol=推奨系(T3 DESIGN_01 §3の公式inventory 2026-10-09)。本番ライン選定の例外理由はN5のTrial確定版に従う旨を記録。

### 3-2 Prompt移植と同一性の固定
CS §4のsha表(B1 97dd3c28…、SEL 2db6e53e…、GEN5 1838b515…、VER5 e138983c…、CHK5 26109d1d…、各schema、FLAGS_V1 3bba7ad2cc6a)を**回帰testの期待値として固定**(Production moduleが組み立てた同一ダミー入力のprompt全文sha・schema shaが一致)。加えて(§4-1)実Trialの全cache keyをProduction moduleが再計算して一致することで、実入力でもPrompt/schema/モデル/effort/max_outが同一であることを証明する。Prompt変更にはユーザー承認が必要である旨を`assert`+コメントに固定(`er119_kp_p7w5_prompts_01.py:44`と同型)。

### 3-3 既存QA12・presentable filterとの接続(最大の設計論点)
| 案 | 内容 | 評価 |
|---|---|---|
| α N5がcanonicalizationを置換 | QA12を走らせず、N5の判定でqa_overall_statusを代替 | **不可**: presentable filter(spec① `rv.presentation_blockers`、fail-closed)の入力契約(qa_overall_status=PASS)を満たすにはQA12の撤去・読替えが必要=承認済みGate変更(原文:59違反の恐れ) |
| **β′ canon後に足すレイヤ(推奨)** | canon(QA12・gloss整合・救済)は無変更で先に走る。L3がその後ろで`used_form`/`key_phrase`/`japanese_gloss`をN5形へ更新。QA12は**canon形(N5前)**を判定した結果として保持 | 承認済みGate無変更。欠点: QA12の対象とユーザーに提示される形が一致しない(提示形はVER5/CHK5が判定)。Trialでは非検証の組合せ(QA12がN5前形を落として良質候補が消える)が起こり得る→実測で件数を報告 |
| γ N5形をcanonicalizationへ入れ直す | N5形を`display_phrase`としてcanonを再実行 | canonの決定論validator(`_is_valid_fulltext_normalization`、something/someone化を許容しない)の変更が必要=Validator/Promptの変更 |
**推奨=β′。** 実測でQA12がN5の良質候補を材料的に落とす(例: Trial N5で残った境界例・MODIFIER_DROPPED_OK型を落とす)場合は、設計判断ではなく「承認済みGate(QA12)とN5の整合」という**ユーザー判断事項(分類D)としてFableへ報告**(件数・例を添える)。独断でQA12を緩めない。

### 3-4 データ受渡し(3 field)
- `used_form`=`key_phrase`=**N5表示形**(音声`tts_safe_kp_en`、フォーム`term`、難易度、NG照合`used_form_key`、KP一般解説が参照=CS §1の15行目)。`kc.merge_canonicalization_result`の同値不変条件(used_form==key_phrase)を維持し、ga人称整合(`key_phrase`参照 `er003_key_words_gloss_alignment.py:296-337`)と`er128_kp_confirmed_content_01.py:1203`が**N5形に対して一貫して**働く。
- `source_span`/`source_sentence`/`source_sentence_id`/`selection_phrase`/`display_phrase`=**本文根拠(無変更)**(ハイライト`er_learning_highlight_01.py:263`、出典検査`er003_v1_n3_01_assemble.py:394-410`、candidate_id生成)。
- `japanese_gloss`=N5確定gloss(CHK5/VER5修正・revert時の本文語義gloss)、`japanese_gloss_tts`は`kc.convert_display_gloss_to_tts_text`で再計算。
- 監査field(新規・追加のみ): `n5`={display_form, source_span, gloss_ja, source_sense_ja, headword_frame, frame_change, reconcile, flags, verify, check, reverted, canon_key_phrase_pre, canon_gloss_pre, models, prompt_sha}。後段が無視することを確認するtestと、`rv.save_candidates`/exporter/finalize/`er128`系のpassthrough要否の確認test(CS §1の未確認事項)を実装時に行う。選定フォームv3は無改修の見込み(`selection_phrase`併記は既存 `export_form_data_01.py:175-176`。UI側の表示箇所は実装時に確認)。

### 3-5 gloss整合・人称整合
- canon内のga再整合は無変更で先に走る。L3は**ga再整合を再実行しない**(N5がCHK5/VER5で確定したglossを旧語義へ書き戻させない=原文§2②)。代わりに既存の決定論検査`ga.person_reference_mismatch`(API 0)をN5形に適用し、不整合は既存の`gloss_alignment_status`(HR_REQUIRED等)経路へ接続(新Gateではなく既存検査の適用)。Zの`person_repair_fn`(`_gate_chain`内、canonの後)もN5形で動く。
- `select_alignment_targets`(語を足した場合のみ対象)はN5前のcanon形に対して動くため影響なし。N5の語の減少・置換が対象外であることをtestで確認。

### 3-6 retry/fallback/regeneration/resume 全分岐が同一関数を経由する証明方法
1. 構造: 一般化は`canon_fn`1点(包み)+L1の2呼出点のみ。X/Y/Zは`run_kp_with_review`→`make_generate_fn`→`generate_candidates`以外でKP候補を作らない(CS §2)。
2. 静的test: ソースを走査し(a)正式runner3本が`sc.run_key_phrase_canonicalization`/`run_key_phrase_selection`を`er119`経由以外で直接呼ばない、(b)`generate_candidates`内で`canon_fn`が包み済みの既定(test注入除く)である、(c)`n5.wrap_canon`未適用の`_gate_chain`呼出が0、を固定。
3. 動的test(mock、API 0): 初回/外側retry(call1失敗→再試行)/補完(Gate除外E≥1)/再選定round(Human NG)/本文変更STALE再生成の各シナリオで、N5の各stageのcall記録(stage名・回数)が出ること。resumeシナリオ(保存doc読戻し)では**API 0かつdocのgeneralizationがN5**であること。旧doc(generalization marker無)をresumeした場合は`logging.warning`(停止しない=`er119_kp_human_review_01.py:1641-1647`のprovenance driftと同型)。
4. runtime evidence(§5): 実runで上記のうち少なくとも初回+補完(自然発生)+再選定round1回を観測。

### 3-7 失敗系の扱い(fail-closed)
| 事象 | 扱い |
|---|---|
| N5 stageの通信等の技術失敗 | 既存retry(MAX_ATTEMPTS=2、sleep(2))→なお失敗は`CANON_FAILED`相当で外側retry(既存)→`OUTER_RETRY_EXHAUSTED`→`rv.ensure_kp_review`のFAILED。**N5なしの候補を出さない** |
| ModelContractViolation/モデル不一致 | STOP(伝播、runner rc=2)。自動downgrade・旧方式続行なし |
| GEN5の項目欠落/組立失敗/validator不通過 | Trial確定版どおりlog(`gen_missing`/`assemble_failed`/`gen_validator_dropped`)して当該itemを除外(stage=`n5_generalize`、Eに数える) |
| VER5/CHK5が一部itemの判定を返さない | **Trial確定版の挙動を忠実に移植**(VER5欠落=`{}`扱いでOK相当、CHK5欠落=未検査のまま通過)。ただし件数を`n5.stats.check_missing`等で記録し証跡に出す。この「未検査通過」はTrial挙動であり新Gateではない→Opus論点4 |
| 全件除外で候補0 | 既存の0件処理(外側retry/shortfall)に委ねる。補充しない |

### 3-8 WordNet依存(Productionに無い新依存)
Trialの`T1/nltk_data`(11MB・**git未追跡**)に依存し、SEL Promptの「WordNet複合語見出し」ヒントと`display_check`/`revert_form`が使う。→Production moduleは**tracked資産としてWordNetデータをvendoring**(`data/nltk_data/corpora/wordnet.zip`相当、sha256固定)し、欠落/sha不一致は**起動時にfail-closed STOP**(旧方式で続行しない)。NLTKのthread非安全対策(RLock)はTrial(`kpg02_methods`の`_WN_LOCK`)と同一に移植。依存追加のため`requirements`/環境の確認要。ライセンス(WordNet)記録。代替(自前辞書等)はPrompt同一性が崩れるため不採用。

### 3-9 費用
- Trial実測(結果JSON stage meta): ¥3.42〜3.88/レベル(平均報告¥3.14)。内訳(untidi_a2): B1 0.16/SEL 0.27/GEN5 0.36/VER5 0.80/CHK5 2.30。1記事セット(Std+Adv)=約¥6.3〜7.8。70円目標比約9〜11%(増分)。
- 相殺: L1でSELがP7候補を絞るため後段canonの対象数が減る可能性があるが、**現行canon・gloss整合の実費は台帳に無く未確認**。実測は`er005_cost_logger`のstageタグ(`kp_n5_b1/sel/gen/ver/chk`)で集計し、Trial値との差を報告。
- 最適化余地(品質機能を省略しない範囲): (a)B1/SELのcache再利用はProductionでは不可(別run)(b)CHK5の入力は全件のまま(N5の品質機能・省略しない)(c)重複API呼出の排除(L3でgaを再実行しない=追加費用0)(d)VER5/CHK5を可能な範囲で並列(独立なので逐次依存=VER5→CHK5は直列、レベル間は並列)。

## 4. 回帰テスト設計(API 0。原文§4A=「新基準でTrialをやり直さず、承認済みN5の挙動を正式経路で再現」)
### 4-1 Trial cache replay fixture
- 抽出: `T1/kpg01_work/llm_cache`(688件・untracked・3.1MB)から、N5(ALL14+HELDOUT計20ケース)のB1/SEL/GEN5/VER5/CHK5の応答を`fixtures/n5_replay_<case>.json`へ(key=Trial算出hash、model_req、user prompt sha、raw out)。サイズ見込み<1MB。取込元の完全性は「Trial `ARMS['N5']`をCAP=0で再実行して全stage cache hit」で事前確認済み(untidi_a2/jwst_m_b1b/melos_a2、CS §4)。
- **key一致test**: Production moduleが各stageで組み立てる`[model, user, system, schema, effort, think_budget]`のhashがTrial keyと一致=Prompt/schema/モデル/effort/max_out/think_budgetの同一性を実入力で証明。
- **挙動再現test**: 記録応答をinjectした呼出関数でProduction moduleを走らせ、最終items(display_form/gloss/reverted/dropped/flags)がTrial記録(`T3/kpg04_work/results/*__N5.json`)と**完全一致**(exact)。
### 4-2 必須回帰項目(原文§4A、CS §4末表のfixture値で期待値固定)
①`hear it out`→`hear someone out`(untidi_a2/b1b、PERSON_OVERRIDE) ②`take points away from`→`take something away from`+訳修正(untidi_a2 GLOSS_MISMATCH→fix_gloss)と`taking points away`の本文形revert(untidi_b1b) ③`keep one's eye on`(melos_a2、FRAME_MISMATCH/PRONOUN_SLOT境界例の記録どおり) ④`set a lower limit`→`set a limit`(jwst_m_b1b、MODIFIER_DROPPED_OK) ⑤`took an unexpected turn`→`take a turn`(jwst_m_a2/b1b) ⑥日本語訳が旧語義のまま残らない(GLOSS_MISMATCHでfix_gloss/本文語義revert。revert時にform・glossが対で本文語義に戻ること) ⑦良質候補の保持(20ケース全件の出力一致=Trialで保持された候補が正式経路でも保持)。+M1〜M3/M9の単体test(revert_form/span_gloss/fix_drops_content/reconcile)。
### 4-3 構造・統合test
到達性(§3-6 静的/動的)、DefaultOn確認(flag/envなしでN5発火、`gen_hook`注入時のみ迂回=test専用を固定)、presentable filterとの接続(N5出力itemが`presentation_blockers`契約を満たす/満たさない場合の除外stage)、`bf`のE計数(n5_select非計数・n5_verify/check計数)、doc/exporter/finalizeの互換(既存`er119_*_test`・`er128_*_test`・`er134`系の回帰)、モデル/価格登録test(PricingNotFound無し、routing違反でSTOP)、WordNet欠落でfail-closed。既存Regression: `er119_*`/`er125_*`/`er003_*gloss*`/`er019_*kp*`/`er121_*`/`er026_*`のKP関連testを全件実行(並列shardで実施)。

## 5. runtime evidence計画(原文§4B。費用節約のために証跡を省略しない)
- 対象: 6経路(X/Y/Z × Std[a2]/Adv[b1b])。**既存run dirの複製**上で、各runnerの**公式CLIのKP段**を実行(本文・TTS再生成なし)。Y/Zは`--stages kp`系、Xは`--stage scaffold`(support段の再生成を避ける条件は着手時にmock/dry-runで確認=**未確認**)。`stop_scope_check_01.py`を各起動前に実行、launch規則(300秒窓内≤2回・間隔≥150秒)を遵守、監督ループ・自動再試行ラッパなし、再起動は委任文が許可した回数のみ。
- 記録(各経路): actual model_id(B1/SEL/GEN5=gpt-6-luna、VER5=gemini-3.8-flash、CHK5=gpt-6.1-sol。応答値)、doc.generalization(prompt sha/FLAGS hash/方式id)、routing解決結果、N5各stageの実行・判定記録(`n5.verify/check/reverted/flags`、dropped stage別件数)、英語候補(`used_form`)・日本語訳(`japanese_gloss`)・本文根拠(`source_span`)の一致(`used_form`が`source_span`の語形違い+placeholderのみであること=display_check再適用、glossがrevert時は本文語義であること)、費用(stage別)、Trial値との差。
- retry/fallback/regeneration/resume: (a)補完は自然発生を観測(Gate除外E≥1の経路があれば)(b)再選定roundは1経路でHuman NG 1件を与えて再生成(+¥約5)(c)resumeは同dirの2回目起動でAPI 0確認(d)外側retry/技術失敗/ModelContractはmock注入testで(実APIで故意に失敗させない)。
- 費用見込み: N5 ¥3.4〜3.9×6レベル≈¥21〜23 + 既存canon/ga/difficulty相当(置換前後で重複計上しない実測)≈¥6 + 再選定round1回≈¥5 + 予備 → **≈¥35**。**提案Cap: ¥60**(案件見積300円以下かつ承認済みScope内=AI自律、PM_GOVERNANCE 7-7。日次1,000円内)。累計80%(¥48)で事前警告。Cap超過見込みは実装せずFableへ。
- 後続工程の整合: 候補確定(`finalize_kp`)→学習項目/KP音声(`used_form`)をmock/API 0で通し、`keywords_canonicalized.json`のfield一致を確認。TTS実音声の再生成は行わない(Cap外・原文「不要な再生成を避ける」)。音声の語形(`something`/`someone`のTTS安全化 `tts_safe_kp_en`)は既存one's/someone's実績の範囲かをAPI 0で確認し、実音声が必要と判断した場合はFableへ(別Cap)。

## 6. 旧D/E1L参照・Trial実装の整理案
- コード: Production内に旧Trial参照0(CS §5)。**整理対象のコード無し**。Trial専用コード(`T1|T2|T3/kpg0*.py`)はProductionから参照されない・importされないことを静的testで固定(DefaultOff/Dangling防止)。
- `user_test/kp_generalization_trial_02|03/index.html`: 公開済みTrial比較ページ。N5採用後も「採用前のTrial記録」として残し、ページ冒頭に「採用方式=N5(Production採用済み)、他方式は不採用」の注記を追加するか撤去するかは**Fable判断(軽微・UI/証跡、分類B)**。
- 旧記述: OPEN-621/623、UDR #227。#228は解消済み。#227はTRIAL-01の採用判断(display_form許容・G1型等)でN5採用に統合されるが、原文はD/E1L/E4/N2のみ明示(:21)→#227は「N5採用で統合」の解釈をFableが確認(分類B)。

## 7. SSOT更新案(配線完了時。本委任では採用記録のみ済み)
- 済み: OPEN-623に採用追記、OPEN-625(本管理ID)新規、DECISION_LOG採用決定1件、UDR #228解消。
- 配線完了時: CURRENT_SPEC(KP節 `CURRENT_SPEC.md:2041-2048`近傍へN5追記: 工程・モデル・Prompt sha・データfield・Status表)、DECISION_LOG(配線・Fable受入)、OPEN-625のStatus更新、PM_GOVERNANCEへの追記は不要の見込み(新規運用規則なし)。
- Family別Production Wiring Status(現時点・全6経路同一):
| Family | Std(a2) | Adv(b1b) |
|---|---|---|
| X | APPROVED_FOR_PRODUCTION・未配線 | APPROVED_FOR_PRODUCTION・未配線 |
| Y | 同上 | 同上 |
| Z | 同上 | 同上 |
(配線後はruntime evidenceが揃った経路ごとに「配線済み・Fable受入待ち」→受入後にPRODUCTION_WIRED。全6経路が揃うまでPRODUCTION_WIREDと呼ばない)

## 8. 判断候補・Opusレビュー論点・リスク
### 8-1 判断候補(いずれも現時点では**ユーザー判断ではなくFable確認/自己解決**の見込み。停止根拠を付す)
| ID | 内容 | 根拠(file:line) | 分類 |
|---|---|---|---|
| J1 | N5=Trial確定版の全工程(B1過剰生成+E1L SEL+pick を含む)を正式採用範囲と解釈する | 原文:7-9(Trial 03方式B[N5])、:21(E1L再判断不要)、`T3/kpg04_methods.py` ARMS["N5"]=run_N(collect→select→pick→generalize5→verify5→check)。SELを外すとTrial未検証構成(SELなしN5)になる | B(承認範囲内で自己解決。ただし解釈の記録をFableが受入時に確認) |
| J2 | QA12(spec①)維持によりN5後の良質候補が追加で落ちた場合の扱い | `rv.presentation_blockers :521-546`、`kc.QA_FIELDS :71-100`、原文:59 | 現時点B(既存Gate維持)。**実測でN5の許容形(MODIFIER_DROPPED_OK等)を材料的に落とすなら D**(承認済みGate変更=ユーザー判断) |
| J3 | kill switchを置かない(撤退=単一commit revert) | 原文§3「retry時だけ旧方式へ戻る状態を防ぐ」、`er003_key_words_gloss_alignment.py:124` | B(設計判断) |
| J4 | WordNetデータのvendoring(11MB)・環境依存追加 | `T1/kpg01_validate.py:5-7`、SEL prompt `prompt_S3`のwn_multiword | B(技術) |
| J5 | gemini-3.8-flash単価のpricing_snapshot登録・routing追加 | `pricing_snapshot.json`未登録、`er006...:82-`、25節 | B(手順) |
### 8-2 Opusレビュー論点(5件)
1. 統合方式β′(L1=select段、L2=既存canon無変更、L3=canon後の表示形レイヤ、used_form=key_phrase=N5形、QA12は旧canon形を判定)の妥当性。代替α(置換)/γ(再投入)との比較、QA12とユーザー提示形のずれの許容可否。
2. 補完(backfill)のSEL適用範囲(SELのみ・B1は初回のみ)と、`n5_select`をEに数えない/`n5_verify`・`n5_check`を数える線引きが「候補数補充をしない」と既存補完仕様の双方に整合するか。
3. 失敗系: fail-closed設計(N5なし続行禁止・kill switchなし)と、Trial挙動(VER5/CHK5が判定を返さないitemの未検査通過)を忠実移植する是非(新Gateを作らず記録のみ)。
4. WordNet vendoringとPrompt同一性の担保方法(SEL promptにWordNetヒントが入る)、Gemini応答モデル照合の厳格化が「挙動変更」に当たらないか。
5. 回帰test設計: 実Trial cache keyの再計算一致+記録応答replayのexact一致(モジュール単体)と、Gate適用後の統合差分を「報告対象(assertしない)」に分ける線引き。ga再整合をL3で再実行しない設計(N5 glossの保護)と既存gloss整合仕様の整合。
### 8-3 リスク
- Trial非検証の組合せ(QA12/ga/CMU/救済がN5形に作用)で、Trialの品質数値(確定誤り0/80)がそのまま再現されない可能性 → 実測で差分を報告し、材料的ならJ2。
- B1候補が既存Gateで落ちる/通る差(Trialは`span_in_text`のみ)。
- 費用: Trial値¥3.14/レベルに対し本番はGate連鎖・再選定で上振れ得る。
- ER番号衝突(er138)・OPEN-625番号の並行採番(着手時再確認)。
- 実装規模が大きい(移植約1,000行+test)ため、Opus承認後に独立部分(移植module・fixture抽出・routing/価格・test骨格)を並列で進める。

## 9. 実装順・クリティカルパス(Opus承認後)
1. [並列] (a)module移植+WordNet vendoring (b)fixture抽出+key一致test (c)routing/pricing/見積値更新 (d)到達性・構造testの骨格。
2. `er119_kp_candidates_01.py`への配線(L1/L3/doc/bf定数)→mock統合test→既存Regression全件(shard並列)。
3. Opus実装レビュー(必要に応じ)→runtime evidence(6経路を独立に並列起動、launch規則内)→Trial比較・費用実測→SSOT更新→Fable独立受入。
