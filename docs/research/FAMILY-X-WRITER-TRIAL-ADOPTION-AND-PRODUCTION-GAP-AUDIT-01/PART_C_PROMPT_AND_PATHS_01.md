# PART_C_PROMPT_AND_PATHS_01(FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01 委任_01C、2026-10-16、read-only・JPY0)

最終Status: `PART_C_COMPLETE`(未確認は§7に分離)。編集したのは本文書・`docs/pm/RESULT_PACKET_FXWA1C.md`・委任文保存のみ。Production code/Prompt/SSOT/Git操作・API呼出は0。
確認方法: 実ファイルのGrep/Read、`ast.literal_eval`による定数同一性比較、現行コードの`verbatim_shas()`と実run(`er019_output/meta/run_sol61_01`、`er019_output/coffee_prices/run_l3_01`)の`ja_writer/runtime_evidence.json`のsha突合(オフライン、`.venv -I`)。承認commit以降のdiff: `git diff --stat adb15c30(Sol E案merge)..HEAD`。
用語注意(重要): 委任文§6の「K2/P8/P7」と、SSOTでの意味が一致しない(§7-1)。本書はSSOTの意味で照合し、ずれを§7に列挙した。

## §1 承認済みPrompt要素一覧(Family X Writer系。履歴=Luna/Astra期の記述は「履歴」と明記)

| # | 要素 | 原則文・要素 | 出典 | 承認/状態 |
|---|---|---|---|---|
| W1 | B3 Storyline+Fact選定 | 4 Test(逐語)・LLM 1 call・採用3〜5件目安。モデル=gpt-6.1-sol | CURRENT_SPEC:1157(E案)、1165〜1167。実装`er019_family_x_storyline_b3_fact_selection_01.py:35-60` | 2026-09-26 / Sol 2026-10-11 PRODUCTION_WIRED |
| W2 | 決定論B3 producer(注記済みB3) | D-det v2+assembler・llm_calls=0・契約V1〜V10 | :1167 | 2026-10-10/11 PRODUCTION_WIRED |
| W3 | R0 Prompt(P7方式) | `R0_PROMPT`逐語(友人に話す・面白い「見方」一つ・易しい日本語・800〜1000字) | :829(「Trial P7方式」)、:1169。`er019_family_x_ja_writer_o_r1_r2_01.py:49-64` | 2026-09-24採用 |
| W4 | Fact Lock(R0ブロック) | 出典タグ【事実N】・ニュース欄外の事実禁止・範囲/確かさ/方向を強めない・【中核数値】のみ使用・MUSTFIX_PRIORITY | :1169。`er053_family_x_factlock_ja_writer_01.py:73-95` | 2026-10-10/11 PRODUCTION_WIRED |
| W5 | AN3(Concreteness Control) | 数字/時刻の抑制+固有名詞は必要時のみ | :886-905、:1169 | 2026-09-28/29 PRODUCTION_WIRED(§2 W5参照) |
| W6 | 記号予防ブロック(Layer1)+記号QA(Layer2) | 〜…/()等禁止、R0は1回再生成、R2は同一R1 rawで1回再実行 | :1169 | PRODUCTION_WIRED |
| W7 | R1/R2(Astra方式) | `USER_TMPL`逐語、R2入力=R1 raw、effort high、previous_response_idなし。モデル=gpt-6.1-sol | :1169(履歴記述=Astra)、:1157 | Sol E案 2026-10-11 |
| W8 | Advanced英訳 | 忠実英訳(Faithful Translation)・段落数同一・見出し禁止・語彙ルールv2 | :1325-1332(W1 2026-09-29)、:830(履歴=Natural English Adaptation) | PRODUCTION_WIRED |
| W9 | Advanced In One Line | :583「中心1文+補足2文程度」(DECIDED 2026-08-09)。:1170 M1(a)=JA R2本文+Ledger入力 | :583、:1170 | 仕様=:583、M1(a)=2026-10-10採用 |
| W10 | Standard Level調整(Family X見出し廃止A2) | v5「6,000語ライン」語彙+構造保持。入力=Advanced英文 | :831、:1170 | PRODUCTION_WIRED |
| W11 | Comment4 Prompt(Standard) | 「In One Lineは番組最後の英語による要点整理」「『続いて』より『最後に』」2文追加 | :2625付近(V5決定A)。`er019_family_x_audio_plan_01.py:221-238` | APPROVED_FOR_PRODUCTION 2026-10-12(Std共通定数) |
| W12 | KP候補供給M2P0 | 注釈のみ・P0選択prompt無変更・失敗時Strategy L fallback(報告義務) | :1856 | APPROVED 2026-10-13 |
| W13 | KP英語解説 | 15語以内・1文・技術retry 1回(`er019_family_x_kp_explanation_01.py:45-49`) | W4 2026-09-29 | PRODUCTION_WIRED |
| W14 | In One Line「基本2文・必要時のみ3文」 | 委任文§6では既決扱い。SSOT側は**未記録**(OPEN-299 L802=未仕様化、UDR #69未回答) | OPEN_ITEMS:802、USER_DECISION_REGISTER_01:88 | SSOT上は未承認(§5) |
| W15 | Coffee限定Style: K2(KP英語)/M2(KP日本語意味)/A5・B5/E1/R2/P3/N01 | Style選択のみ。Coffee限定(OPEN-298) | :2623-2634 | Coffee限定APPROVED |

(Writer原則 Storytelling First/No Jargon[:1941-1942]は`er003_v1_n3_01_articles_generate.py::COMMON_BLOCK_TEMPLATE`=英語直書きWriter[Family A/B/C]の原則。Family Xの日本語起点Writerへの適用有無は仕様上明記なし=§7-4。)

## §2 現行Production Prompt本文との対照(要素ごと)

実Promptの所在(Family X初回経路): R0=`er053_family_x_factlock_ja_writer_01.py:260-276(build_r0_prompt)`+`er019_family_x_ja_writer_o_r1_r2_01.py:49-134`、R1/R2=`er053...:67 USER_TMPL`、B3=`er019_family_x_storyline_b3_fact_selection_01.py:51`、Adv英訳=`er003_v1_n3_01_advanced_adaptation_generate.py:522-632`、Adv IOL=同`:551-615`、Std=`er003_v1_n3_01_standard_a2_generate.py:506-538`、Comment=`er019_family_x_audio_plan_01.py:193-238`、KP解説=`er019_family_x_kp_explanation_01.py:62-93`。

| 要素 | 判定 | 根拠(file:line・実測) |
|---|---|---|
| W1 B3 | 存在 | 4Test定数逐語。Sol E案merge(adb15c30)以降の当該ファイルdiff=0 |
| W3 R0本文 | 存在・不変 | 現行コードの`verbatim_shas()`が実run 2本(`meta/run_sol61_01`、`coffee_prices/run_l3_01`)の`runtime_evidence.json:verbatim_shas`14項目と全一致(R0_PROMPT/DEVELOPER/SYMBOL/AN3/FACTLOCK_*/USER_TMPL/各regex) |
| W4 Fact Lock | 存在・Trialとbyte-identical | `FACTLOCK_R0_BLOCK_HEAD`/`MUSTFIX_PRIORITY`/`USER_TMPL`をTrial(`er052_factlock_writer_trial_01_run.py:53`、`er052_factlock_astra_e2e_runner_01.py`)とast比較=一致(TAIL/regexは定数式のためast比較不可、sha一致で代替) |
| W5 AN3 | **変質(承認文との差)** | `build_r0_block`(w1:99-111)は`CONCRETENESS_CONTROL_AN3_BLOCK`の第1文(数字・時刻の抑制)を送らず、Fact Lock規則5で置換、第2文(固有名詞)のみ逐語保持。SPEC:1169は「AN3-T0はR0 Promptに含まれたまま(sha 067030ff…)」と記述。runtime_evidenceが記録するshaは定数のshaで、実送信文のshaではない(`R0_BLOCK`は別項目で記録)。**Fact Lockはユーザー承認済み構造であり挙動の誤りではない。SSOT記述の精度の問題** |
| W6 記号 | 存在 | `build_r0_prompt`が`jaw.SYMBOL_PREVENTION_BLOCK_JA`を付加(w1:271) |
| W7 R1/R2 | 存在。Fact Lock/AN3/記号予防は**R1/R2に付かない**(R0のみ) | `USER_TMPL`のみ。Trial byte-identical(設計通り、SPEC:886でR1/R2 reminder削除は2026-09-28ユーザー決定)。R0以降の事実保護はRF(非Blocking)+Human Reviewに依存(承認済み設計) |
| W8 Adv英訳 | 存在 | `build_family_x_faithful_translation_prompt`(adv:621)にVOCAB_RULE_V2が含まれる(:626-627) |
| W9 Adv IOL | **欠落/矛盾** | Production本文`"- Exactly one sentence."`(adv:558)+`"Do not pack in multiple separate points"`。SPEC:583「中心1文+補足2文程度」未実装。実run証拠: `er019_output/coffee_prices/run_l3_01/b1b/article.md:22`=1文、`a2/article.md:22`=1文。さらにPromptに`"Trial-only guidance, not a strict rule... 12-18 words"`というTrial由来文言がそのまま送信される(adv:561-563) |
| W10 Std | 存在 | `STANDARD_A2_NEW_VOCAB_BLOCK`を結合(std:513)。IOL節は「保持せよ」のみ=IOLの文数は入力のAdvanced IOLに従属 |
| W11 Comment4 | 存在(Std)/**B1側は未反映** | A2側plan:221-238に「最後に」2文あり。B1側plan:193-208には無し(V5決定AはStd共通定数のみ=意図通り。B1展開はOPEN-316(c)未決) |
| W12 M2P0 | 存在 | SPEC:1856。失敗時Strategy L fallbackは承認済み・報告義務あり |
| W13 KP解説 | 存在 | 同一`PROMPT_SHA256`で初回/retryとも同じ |
| W15 K2/M2/A5/B5/IOL Style | **Family Xに欠落** | `er019_family_x_style_profile_01.py:149-175` profileはFULL_STORY/SUPPORT_JA(R2)/KP_EXPLANATION_EN(P3)/PREVIEW(E1)のみ。K2/M2/A5/B5/IN_ONE_LINEのroleなし(:16-17「後続Phase」)。**一方Family Z定数表`er063_family_z_audio_01.py:154-155,175-206`はK2/M2/R2/E1/A5/B5を保持**=Coffee由来の承認Styleが派生側(Z)にあり本家(X)に無い逆転 |

### 経路別: 同一Promptか(初回/retry/fallback/regeneration/LR/self recovery/precheck retry/resume)

| 経路 | 使うPrompt | 判定 |
|---|---|---|
| R0初回 | `build_r0_prompt` | 基準 |
| R0 記号再生成 | `build_r0_prompt`+違反note(w1:279-281) | 同一(新規文言なし) |
| R1/R2 技術retry | `call_astra`(同一`USER_TMPL`・同一model、w1:163-176) | 同一 |
| R2 記号再実行 | 同一R1 rawで`astra_stage`再呼出 | 同一 |
| resume/再利用(JA) | Prompt使用なし。`load_reused_ja_text`(runner:233-260)でW-1来歴+注記sha一致のみ許可 | 旧Writer記事は遮断(U-1) |
| `--regenerate-stage writer/storyline_b3` | 初回と同じ関数(runner:218,147) | 同一 |
| Adv英訳 構造parse retry | 同一`build_family_x_faithful_translation_prompt`(max_attempts=2) | 同一 |
| Adv/Std 段落3分割retry | 同Prompt+must-fix block(`_FAMILY_X_PARAGRAPH_RETRY_MUST_FIX`、er012:315-326)。AdvはIOLも同じ`_advanced_in_one_line`で再生成(M1(a)維持) | 同一(+技術must-fixのみ) |
| Std単独再生成 | `b1b/article.md`を入力に同関数 | 同一 |
| KP解説 技術retry | 同`PROMPT_SHA256` | 同一 |
| KP候補供給 M2失敗 | Strategy L(旧供給)へfallback | **別経路(承認済み・報告義務)** |
| Local Rewrite(TTS ASR NG回復) | `er020_tts_retry_local_rewrite_01.py:367 CANDIDATE_GEN_SYSTEM_PROMPT`/`:524 LOCAL_QA_SYSTEM_PROMPT`=別Prompt。承認済みWriter原則(IOL文数・Fact Lock等)は参照しない。局所書換(unchanged_ratio・numeric_preservation検査あり)に限定 | 別Prompt(2026-09-26承認済み)。IOL文数保持の検査は未確認(§7-5) |
| Self Recovery / precheck retry | Family X Productionに未配線(OPEN-233=SUPERSEDED、OPEN_ITEMS:416)。Family X runner/er053*に`precheck`のGrepヒット0 | 該当なし |
| Risk Flagger | A3/A4 system promptは台帳との照合のみ(`er053_risk_flagger_production_01.py:57-110`)、Writer原則への参照なし | Dangling無し |

## §3 Trial専用コードにのみ存在する改善

(Trial棚卸し全体はPart B。ここではWriter Promptに入る/入らない要素のみ。)
- Fact Lock/Astra方式: Trial(`er052_factlock_*`)→Production(`er053_family_x_factlock_ja_writer_01.py`)へbyte-identical移植済み。**残存なし**。
- In One Line 2文方針: Trial原稿のみ(`er057_output/coffee_final_audio_assembly_01/IN_ONE_LINE_REWRITE_01.md`、OPEN-299)。**Production Promptに存在しない**(§2 W9)。**該当**。
- K2/M2/A5/B5: Trial(`er057_output/coffee_final_listening_tone_trial_01/part_AEF,part_BCD/prompts`)にのみ原本。Family X Production定数に無し(Family Zのみ)。**該当**。
- OPEN-243 M1(b)/M2/M3の`open243_m1_enabled()`/`OPEN243_M1_ENV`(adv:583,601)は定義が残るが呼出0(M1(a)は無条件ON)。**死コード(影響なし)**。
- `jaw.run_ja_writer_o_r1_r2`(`er019_family_x_ja_writer_o_r1_r2_01.py:183`)と`REVISION_INSTRUCTIONS`(:70): 非testの呼出0=Trial互換の孤立コード。誤って呼ぶとLuna連鎖の旧仕様で動く(隔離はtestのAST固定に依存)。
- OPEN-233系(self recovery/precheck/polysemy/ledger clarity等、`er052_open233_*`): SUPERSEDEDでProduction未配線。Writer側の`notes_for_writer`は決定論producerが制約ブロックへ転記(`er053_b3_deterministic_producer_01.py:141`)=失われていない。
- OPEN-238 precheck偽陽性修正(案1 APPROVED・配線874dd6e2)は旧Checker連鎖内。Checker撤去(2026-10-10)でFamily X Productionの到達経路から消滅。Family A/B/C側の扱いは本監査対象外。

## §4 Dangling Reference

| # | 箇所 | 内容 | 影響 |
|---|---|---|---|
| D1 | `er053_family_x_factlock_ja_writer_01.py:66,95`(R0 Prompt規則7) | 「事実確認の修正指示がある場合はそれを最優先し、直すか削る。」を送信。Fact Checker/must-fixは撤去済みで`build_r0_prompt`に修正指示の入力経路が無い(docstring :262「must-fix引数は持たない」)。**参照先の無い指示がR0に毎回送られる**。Trialからのbyte-identical移植のため意図的な残置の可能性 | 実害は未確認(モデルが無視するだけの可能性大)。削除はPrompt変更=ユーザー判断事項。撤去要否はFableへ |
| D2 | Comment4 `er019_family_x_audio_plan_01.py:206-208,234-237` vs Adv IOL `advanced_adaptation_generate.py:558` | Comment4は「In One Lineの実際のsentence数は記事により異なります(1文とは限りません)」と指示、IOL生成は「Exactly one sentence」。前段Promptが後段の実態と矛盾 | 実run IOL=1文(run_l3_01) |
| D3 | SPEC:1169 vs 実装 | 「AN3-T0はR0に含まれたまま」だがAN3第1文は規則5へ置換(§2 W5) | 記述精度のみ |
| D4 | SPEC:1169(R0=Luna、R1/R2=Astra)vs :1157(Sol E案) | :1157自身が「旧配置の記述」と注記済み。現行コード=routing値(Sol)でshaに影響なし | 履歴注記済み・混乱の余地 |
| D5 | SPEC:830-831 | Advanced=Natural English Adaptation(h3構造)・Std=2節構造の記述が現行Family X(忠実英訳・見出し無し)と異なる。:1325-1332で置換されているが:830行自体にFamily X向け置換注記があるか未確認 | §7-6 |
| D6 | `er053_dangling_reference_check_01.py`のSCOPE_FILES | 走査対象に`er003_v1_n3_01_advanced_adaptation_generate.py`/`standard_a2_generate.py`/`scaffold_generate.py`が無い。今回実行(既存9ファイル)のhit=37(MAJOR 25=audio側ASR語彙、must_fix 11=記号/段落の技術QA語彙、Local Rewrite 1)で撤去対象の残存は0。ただしWriterのEN生成moduleは走査外 | 検査の死角 |

## §5 承認済み仕様と完成品の不一致

Coffee監査(`er071_output/m2p0_n01_production_wiring_01/coffee_spec_completeness_audit_01/AUDIT_REPORT_01.md`、2026-10-15)の3件の2026-10-16時点の現状(コードのgit log・実ファイルで確認):

| 項目 | 現状 | 根拠 |
|---|---|---|
| In One Line 1文 | **未是正** | `advanced_adaptation_generate.py`最終変更=2026-10-08(`git log`)。Prompt=Exactly one sentence。UDR #69(a)未回答 |
| K2(KP英語) | **未是正** | Family X profile定数にK2無し(style_profile:149-175)。OPEN-313 Phase2未着手 |
| M2(KP日本語意味) | **未是正** | 同上 |
| 是正の決定記録 | なし | DECISION_LOGに2026-10-15/16のIOL/K2/M2是正決定のGrepヒット0 |

Writer側で同型(技術test PASSでも仕様要素が抜ける)の候補:
1. **Coffee限定profileは明示CLI指定専用**: `DEFAULT_NEW_RUN_PROFILE=n01`(style_profile:110)。`--style-profile coffee_n01_r2_p3_e1`を付け忘れた新規Coffee runは、R2/P3/E1が黙って落ちる(profile=defaultのときGateは働かない設計)。委任文§6「Coffeeを代表記事としてFamily X共通Production仕様を完成」とは逆に、既定では共通化されていない。→要確認(§7)。
2. **Std IOLの文数はAdvanced IOLに従属**: Std PromptはIOL節を「保持」するだけ(std:522)。Adv IOLを2文化しても、Std側で文数が保たれるかのtestは未確認。
3. **Comment4の「最後に」2文は適用済み(Std)だがB1(Advanced)側に未展開**(OPEN-316(c))。
4. **IOL文数を検査するValidatorが無い**: `split_family_x_article_text_v2`はNG_MISSING_IN_ONE_LINE等の存在検査のみ(er012:296-304のコメント)。仕様が1文→2文に変わっても検出されない。→仕様化後に要検討(新規仕様候補、実装しない)。

## §6 委任文§6既存決定事項の配線確認

| 決定 | 初回 | retry/fallback/regeneration | 備考 |
|---|---|---|---|
| B3/R0/R1/R2 Sol統一 | `routing.PROCESS_MODEL_MAP`(er006:134-137)・runner:147-155・w1:38-41。実run `meta/run_sol61_01` r1.model=gpt-6.1-sol | 同routing keyを`call_astra`/`call_luna_r0`が全retryで使用、`require_model`で都度確認 | 詳細はPart A |
| Fact Lock構造 | w1:73-95 | 記号再生成・R2再実行・regenerate-stage・resume全て同一(§2) | sha一致を実run 2本で確認 |
| Coffee全面再制作(Research〜) | Writer側のコード要件なし | - | SSOT記録は未確認(「全面再制作」のGrepヒット0) |
| Coffee代表でFamily X共通完成 | §5-1参照: 既定では共通化されていない | - | 配線ではなく運用決定 |
| KP候補供給M2P0 | w12。runner:355-440でM2→Strategy L fallback報告 | fallbackは承認済み | 「選定優先順位A」はSSOT内でラベル未確認(§7-1) |
| Full Story PD06 | `PD06`はSSOT/コードのGrepヒット0。Full Storyは**N01**(2026-10-13、style_profile:79-103)がP8を置換 | - | ラベル不一致。Part Aへ |
| KP英語K2 | **未配線**(§2 W15) | - | Family Zのみ |
| Std日本語意味(委任文P8) | **M2として未配線**。P8はFull Story style | - | ラベル不一致 |
| Adv英語解説(委任文P7) | P3として配線(Coffee限定profile)。P7は2026-10-16のTrial候補(KP-EN-EXPLANATION-PACING、未採用) | - | ラベル不一致 |
| IOLは基本2文・必要時3文 | **未配線**(W9)・SSOT未記録 | - | |

## §7 未確認事項

1. 委任文§6のラベル(K2/P8/P7/PD06/選定優先順位A)のSSOT上の定義と照合不能な部分: SSOTでは P8=Coffee Full Story style(→N01に置換)、P7=旧「Entertainment Original Prompt方式」(:829)かつ2026-10-16 Trialの1候補、P3=Adv KP英英解説、M2=KP日本語意味(Std)。委任文の「Standard日本語意味P8、Advanced英語解説P7」はSSOTと不一致の可能性。ユーザー意図の確認を推奨。
2. 実際に送信されたPrompt全文は**保存されていない**: `raw_usage_log.jsonl`はusageのみ、`runtime_evidence.json`はshaのみ(R0/R1/R2 user_message_sha256)。英訳・IOL・Std・Commentはshaが`writer_run_summary.json`に無く、実送信Promptとコード定数の一致は**コードからの推定**(R0/R1/R2のみsha突合済み)。
3. 最新Coffee audio run(`coffee_prices__run_m2p0_n01_01`)にはWriter段のPrompt保存なし。Writer artifactは`coffee_prices/run_l3_01`(Luna/Astra期)のみ確認、Sol期のCoffee Writer runは確認できず。
4. Storytelling First/No Jargon(:1941-1942)のFamily Xへの適用範囲は仕様上不明。
5. Local RewriteがIOL文数・Std/Adv構造を保つ検査の有無は未精読。
6. SPEC:830-831のFamily X向け置換注記の有無(行全文未精読)。
7. 「Coffee全面再制作」「Coffee代表記事でFamily X共通仕様」のDECISION_LOG記録はGrepで未発見。
8. `adb15c30`以降のdiffは主要11ファイルのみ確認。Family X以外(A/B/C/Z)のWriter Promptは範囲外。

## §8 Sonnet所見(参考。仕様候補は実装しない)

- 最重要は**In One Line**: SSOT(:583)・ユーザー決定(2文)・Production Prompt(Exactly one sentence)・Comment4(文数断定禁止)の4者が不整合で、実runが1文を出し続ける。Coffee監査から是正が進んでいない(UDR #69待ち)。
- K2/M2/IOLを含むCoffee承認Styleの本家(Family X)未配線と、Zへの先行配線は優先順位の逆転に見える。
- D1(R0規則7の宙ぶらりん)は軽微だが、Prompt変更は`USER_DECISION_REQUIRED`扱いのため削除は不可。
- 新規仕様候補(未実装・提案のみ): IOL文数Validator、Std IOL文数継承test、dangling検査のSCOPE拡大(EN生成module)、Prompt送信全文の保存(runtime入力の事後検証用)。

## §9 T-0結果・受入記録5項目

- T-0: 委任文を`docs/pm/delegation_log/2026-10-16_FAMILY-X-WRITER-TRIAL-ADOPTION-AND-PRODUCTION-GAP-AUDIT-01_01C.md`に保存(**要約版**。全文は委任文原本[Fable側]。`check_delegation_prompt.py`結果=**FAIL**[必須セクション見出し不足、要約保存のため]。記録用・作業継続)。
- 所要: 約60分(見込み90〜120分)。費用JPY0。
- 受入記録: (1)当初目的(ユーザー原文§1・§5、逐語): 「Production初回経路にはあるが、retry／fallback／regenerationで旧仕様に戻る」「Promptの改善成果がTrial用コードにだけ存在する」「C. 部分配線 — 初回のみ反映され、retry・fallback・再生成時に旧仕様へ戻るもの。D. 仕様の上書き・消失。E. Dangling Reference — 後段Prompt・Validatorが、初回Writerに存在しない原則や未承認仕様を参照しているもの。F. 承認済み仕様と完成品の不一致」「承認済みPrompt要素と現在の実際のPrompt本文・runtime入力を比較すること」 (2)最終成果物: 本書+`docs/pm/RESULT_PACKET_FXWA1C.md` (3)証拠: §2のsha突合(実run 2本×14項目一致)、ast比較、git diff --stat、実run `b1b/article.md:22`(IOL 1文) (4)一致/不一致: 一致=R0/R1/R2/Fact Lock/B3/Adv英訳/Std/KP解説/retry全経路。不一致=IOL(W9)、K2/M2(W15)、R0規則7(D1)、AN3記述(D3)、Coffee profile既定(§5-1) (5)判定: `PART_C_COMPLETE`(未確認は§7)。
