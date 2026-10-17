## 総合判定
**GO_WITH_FIXES**(推奨1に修正を加えた形+SRCはD1を強化した形で実装可)
理由: Styleの切替経路とDialogueの分離は、コード上で安全に成立している。一方、次の3点は配線前に設計へ組み込む必要がある。(1)run単位Style記録がNarratorにしか効いていない、(2)「Melos said.」の既存FAILがcharacterizationの陳腐化ではなく受理判定の変化を示している、(3)SRCをZへ適用するときのラベルと解釈。

---

## R-C1 Style配線: 判定=軽微(推奨1を修正して採用)
- 根拠:
  - Zは定数のコピーと独自のsha表を持つ(`er063_family_z_audio_01.py:109-165`)。
  - Xの定数は承認済み正本の逐語コピーで、import時に`_verify_constants`で検証される(`er019_family_x_style_profile_01.py:107-160, 304-321`)。
  - er019のprofileモジュールが依存するのは標準ライブラリだけ(:33-36)なので、er063からimportしても循環importは生じない。
- 推奨: Xの**定数**(PD06_TEXT / SUPPORT_JA_STYLE_S3_20261017 / P7_TEXT / P8_KP_JA_TEXT / E1_TEXT / K2_TEXT)は参照する。ただし`DEFAULT_NEW_RUN_PROFILE`やprofile解決関数には**従属させない**。
  - 理由: X側の既定変更(X限定の承認を含み得る)がZのProductionへ無言で波及すると、「Family別にAPPROVEDを追跡する」原則(§7案の項目2)に反する。
  - 波及防止とdrift防止は、別の手段で両立させる。Zのrole表に「どの共通定数へ結び付けるか」を明示し、drift testで差分を検知する(R-C7参照)。
- sha相互assertの置き場所:
  - Z側の`_STYLE_SHA256`に、PD06 / S3 / P7 / P8_KP の期待sha(literal)を固定する。
  - 既存のZ検証関数(`er063:232-240`)でimport時に照合する。Xの定数が誤って変わった場合はZがSTOPする。
- 代替案(Zにfz_20261017形式のprofile機構を導入)は不要。Xのprofile機構は、多数のprofile・CLI・resume互換のための仕組みで、Zには過剰。必要な安全性は、R-C4で述べる「全roleのStyle記録」で得られる。Family横断のprofileエンジン化はY導入時の課題としてOPEN記録を推奨する。

## R-C2 Dialogue別Voice: 判定=問題なし(test追加のみ)
- 根拠:
  - `build_level_plan`はspeakerがnarrator以外ならkind=dialogueにする(`er063:495-499`)。
  - `style_text_for`はdialogueでは`FAMILY_Z_ROLE_STYLE`を参照しない(Stdは`A2_ENGLISH_STYLE_PREFIX_SLOWER`、AdvはNone。:561-566)。
  - dialogueのgeneratorもrole表を参照しない(:646-657)。
  - したがってNarratorのtextを差し替えても、Dialogueには構造上波及しない。
- `FAMILY_Z_ROLE_STYLE_VERSION`をbumpしない方針は妥当。
  - reuse_keyには`style_prefix_sha256`(実際に送るStyle文のsha)が入る(:569-576)。PD06 / S3 / P8 / P7 roleはshaが変わるので、旧clipが誤って再利用されることはない。
  - E1 / K2 / E2_UPBEAT / Dialogueのキーは変わらない。
- 追加test案:
  - roleのtextを差し替えたときに該当roleのreuse_keyだけが変わる。
  - Dialogueのreuse_keyは不変。
  - speakerとVoiceの対応は不変。
- 注意: version文字列`z_v2_pd8_r2_..._m2`は内容と合わなくなる(誤解を招く名前)。bumpはせず、コメントと「実際のStyle labelは各entryに記録」の注記で対処する。

## R-C3 SRC: 判定=要修正(D1を強化して採用。ラベルと解釈はユーザー確認点)
- (a) 承認済みSRCをそのまま適用することは**不可**。
  - CURRENT_SPEC:1919の契約は、Stage1 shortlist→`source_candidate_id`(enum)→Pythonによる復元という流れを前提にしている。
  - 同じ行で、Strategy Lは`free_text_strategy_l`として別契約と明記されている。
  - 同じ行で、`er026` runnerは対象外・「Family Z DB Hybrid Core v2」の採用は未決とされている。
  - コードも`SUPPORTED_FAMILY_PROFILES=("family_x",)`で、gate関数はselectorの呼び出しまで内包している(`er030_..._source_reference_contract_01.py:62, 561-605`)。
- (b) D1は、承認済み`candidate_id_v1`の中核(LLMに元英文を自由記述させない出力契約)を実装しない。性質としては「Source Consistency Gateの強化+決定論IDによる紐付け」。
  - ただしユーザーの10-17の文言(「候補ID**等**によって決定論的に保証」+「KP方針をX方式へ変えない」)を両立できるのはD1だけ。
  - **`candidate_id_v1`というラベルは付けない**こと。例えば`z_sentence_id_posthoc_v1`のような別名にし、「LLM出力から自由記述を除去する部分は非適用(Strategy L維持のため)」と明記する。
- (c) D2は抵触し得る。
  - Strategy Lのpromptは共有(`er003_v1_n3_01_scaffold_generate.py:351-363`の`bk.build_user_message`)で、Xのfallbackや他Familyも使う。
  - これを変えると「既存Promptの変更」に当たり、ユーザー承認が必要。
  - KP再選定が必要になり、validatedなKPも失う。非推奨。
- (d) 第3案は部分的に実現可能。
  - 文の分割に`er030_key_phrase_db_hybrid_core_01.build_sentence_units`(:78、X Productionで使用中。Melos A2での実行evidenceがCURRENT_SPEC:1919にある)を使い、S1..Snを付ける。
  - itemごとに、Z adapterが一意な文IDを決定論的に解決する。順序は (i)source_sentenceと正規化後に完全一致する文、(ii)唯一の包含関係にある文、(iii)span offsetが一意。曖昧または該当なしならSTOP。
  - そのうえで`restore_source_fields`(:416、family_profileの検査を持たない)を流用して、Pythonが正本を復元する。
  - ただし`context_sentence_id`がNoneのときspanで代用するfallback(:463-464)は、Z adapter側で禁止する(STOP)。
  - `run_source_reference_contract_gate`は使えない(selectorを内包)。`SUPPORTED_FAMILY_PROFILES`への"family_z"追加は**しない**(DB Hybrid Zが未決のため)。
- 配線上の必須事項:
  - **gateは`stage_kp`の`ensure_stage`の後、`install_kp_assets`の前で、再利用経路にも必ず適用する**(OF-KGCPW-08と同じ型。`er026_family_z_fiction_production_runner_01.py:1252-1262`)。
  - 復元によってsource_sentenceが変わり得るのに、kp_expl_b1bのsigにsource_sentenceが入っていない(:1273-1279)。sigへ文IDまたはsource_sentenceを加える(新runなので互換問題はない)。
  - 実装前に、run_e2e_02の10 itemでオフライン(JPY0)の解決dry-runを行う。引用符付きのセリフ文が分割境界とずれる可能性がある(未確認)。
- (e) 切り分け:
  - D1の方式選択はFableの委任範囲内(JPY0、元に戻せる、fail-closed)。
  - 「D1をもってZのSRC正式適用とみなすか」は、承認済み仕様の解釈なのでユーザー確認点。Z SRCの`PRODUCTION_WIRED`は、その確認まで宣言しない。

## R-C4 再利用・provenance: 判定=要修正
- 根拠:
  - HR承認とLockはlevel dir単位で、テキストshaでしか照合しない(`er011_human_review_lock_01.py:155-190`)。新しいrun dirへaudit/をcopyしなければ混入しない。
  - ただし`narrator_style_record`はnarrator roleしか見ていない(`er063:509-553`)。旧run(run_e2e_02 / kgcpw)をresumeすると、S3 / P8 / P7のclipは新Styleで再生成される。そのうちStd comment_1(R2で生成)は旧HR承認とテキストshaが一致するので、新S3音声が人の試聴なしで自動採択され得る。
- 修正案:
  1. narrator記録を全role記録に一般化する(role→label / shaの一覧、不一致ならSTOP)。
  2. Xの`_RUN_STATE_FILES`規則(`er019:291-293`)と同じく、記録がないのに`tts_generation_results.json` / `review_lock_state.json` / `human_approved_segments.json`が存在する場合は課金前にSTOPする。
  3. copyの許可リストを明文化してtest化する:
     - 許可: writer/、std、segment_plan_*、dialogue_attribution_*、speaker_table、support/、key_phrases/(snapshot類は除く)、provenance.json。
     - 除外: `*/audit/`全体、`*/narration/`、tts結果、`*_pending_result.json`、`.consumed.json`。
- 計画書の内部不整合: §3では「Dialogue等は再利用可」、§6では「wav・tts結果を除外」としている。新runでtts結果を持ち込まない場合、Dialogue / E1 / K2も**全部再生成**になる。持ち込む場合は、上記の記録STOPに当たるうえ、新しい取り込み機構が必要になる。
- **推奨**: 新runでTTSを全再生成する(取り込み機構は作らない)。計画の見積もりでは差額は約10〜20円規模(推定)。同一runのruntime evidenceで受入条件5・7を満たしやすく、Q優先の原則にも合う。
- KPの再利用元をrun_e2e_02にすることは妥当(unevaluated=[]。kgcpw版はAgentが注入したgloss解決を含む)。

## R-C5 retry/fallback/regeneration/resume: 判定=軽微
- Styleはモジュール定数から解決され、CLIでは渡されない。初回・`--regenerate-stage`・`--only-clips`・KPの外側retry・AUWの3回フロー・Stdの減速外側ループは、どれも同じ`style_text_for`を通る(`er063:634-726`)。経路の分岐はない。
- 旧run dirのresume時に混在が起き得る問題は、R-C4の全role記録で塞ぐ。
- Dangling Reference Check対象(旧名称が残る箇所):
  - `er063`: :35(version文字列)、:74-75 / :544のメッセージ「[STOP][N01]」、:551-552(management_idと`n01_sha256`のハードコード)、:138-176、:185-201、:206、:214-220、`verify_styles_against_origin`(:254-271、R2 / M2の原典照合)。
  - test: `er063_*_test`(N01固定)、`er063_family_z_audio_01_n01_test_01.py`。
  - `er019:124`の「Family Z `_K2`(er063:120)」という行参照。
  - `er063_family_z_page_verify_01.py`がStyle labelを検査しているか(未確認)。
  - CURRENT_SPEC:1608 / :1251。
  - TOPIC_INTRO / J3 / KP_EXPLのコピー定数(:129-136)。

## R-C6 既存FAIL 9件: 判定=要修正(一部は配線と無関係ではない)
- **Melos系7件は単なる期待値の陳腐化と断定できない。**
  - 失敗している入力は「Melos said.」/ Primary「Mello said.」/ Azure「Mellow said.」で、testは「反例: 誤PASSしてはならない」と明記している(`er026_post_slowdown_cascade_rescue_01_test_01.py:61-67, 217-221`)。
  - `er026_cs_audit_regression_01_test_01.py:149-152`はcharacterizationと明記されているが、これも同じ入力。
  - これを`M1_MULTI_CANDIDATE_ACCEPT`が受理している。M1は2026-10-13にユーザーが承認したもので、F1で説明できる置換のみを許す(`er006_m1_multi_candidate_01.py:1-16`)。そのため、承認範囲内の正当な受理(語末s+語頭sの音の融合)である可能性もある。
  - 一方、testはPronunciation Ledgerを固定していない(このtestは`pronun_ledger._load`をmockしていない。gitでは`ledger.json`がModified)。結果が作業ツリー上のLedgerの状態に依存し、再現性がない。
  - 対応: オフライン(JPY0)でM1のaudit(一致候補・出典クラス・ledger_key)を取得する。
    - 承認範囲内なら、Ledgerを固定したfixtureでM1 ON / OFFの2系統に分けて期待値を更新する。
    - 候補がASR由来の値など、範囲外から来ているならsafety問題として扱う。
  - Phase 3でのHR発火予想(Std part1_c5)にも直結するので、**Phase 3実走前に必ず確定する**。Phase 2のコード作業とは並行可。
- `er006 test_flagger_design_models_registered`: test自体が「gpt-6.1-solはX用の3キーのみ」という混入防止の目的を持つ(`er006_model_routing_pricing_coverage_test_01.py:113-115`)。ZのSol R0 / R1 / R2 / STD_ADJUSTの割当がユーザー判断済みであることをSSOTで確認したうえで、許可集合へ根拠付きで明示追加する(期待値の更新で可)。受入条件6に含まれるので、今回のタスク内で是正する。
- `er020 test_recorded_candidates`: 特定runのartifactに依存。今回の配線とは無関係で、別管理でよい。
- `er026_family_z_stop_sentinel_test_01`は未実行。本物のSTOP_ALLを操作するため、隔離した実行方法をFableが決める。

## R-C7 Cross-Family同時配線: 判定=軽微(drift test追加を推奨)
- 定義場所を1か所にすれば、Yへの配線漏れの防止にも効く。ただし「定義が1か所」であることと「適用が自動波及する」ことは分けて扱う。
- drift test案: Cross-Family表を1つのdictとして持つ(role → {X: 定数名, Z: 定数名 or "EXCEPTION:<理由/ID>"})。testで次を確認する。
  1. 共通roleでは、Zの解決sha == Xの`DEFAULT_NEW_RUN_PROFILE`の解決sha。X既定の変更時にFAILさせ、Z配線か例外登録を強制する。
  2. Z側に、er019定数と同一文字列のコピー定数が残っていない。
  3. 例外role(Adv Comment E2_UPBEAT、TOPIC_INTRO / J3、Dialogue)を明示的に列挙する。

## R-C8 Phase 2前に直すべき点(優先度順)
1. (P1)narrator記録を全role記録へ一般化し、run状態ファイルがある場合のSTOPを追加する(R-C4)。
2. (P1)Melos M1受理の正当性を確定し、testのLedgerを固定する(R-C6)。Phase 3の前提条件。
3. (P2)音声の再利用方針を「新runで全TTS再生成」に統一する(計画§3と§6の矛盾を解消)。あわせて、SRC gateを再利用経路にも適用し、kp_explのsigを修正する(R-C3)。

---

## Fableへの注意(ユーザー判断が必要になり得る点)
- **SRCの解釈**: D1(事後の決定論ID付与)を「Z SRC正式適用」とみなすか。承認済み`candidate_id_v1`の、LLMに自由記述させない契約部分は非適用になる。D2は共有Promptの変更になるため、それ自体がユーザー承認事項。
- **M1による「Melos said.」受理**: 承認範囲外と判明した場合はsafety問題として即時報告の対象になる。
- **費用**: 全TTS再生成でも、承認済み上限の残枠の扱い(66.5円か約21円か)は未決。10-17の当日開発費も、計画では使用済み約370円+BAPE進行中なので、事前確認が必要。
- Adv Comment(E2_UPBEAT)はユーザーの表に記載がない。Xとの差異として例外登録するか確認が必要。
- 未確認事項: page_verifyのStyle label検査、Melosのセリフ文で文分割境界とsource_sentenceが一致するか、M1が「Mellow」を受理する具体的な経路。

関連ファイル:
- C:\Users\tensh\eigo-radio\er063_family_z_audio_01.py
- C:\Users\tensh\eigo-radio\er019_family_x_style_profile_01.py
- C:\Users\tensh\eigo-radio\er026_family_z_fiction_production_runner_01.py
- C:\Users\tensh\eigo-radio\er030_key_phrase_db_hybrid_source_reference_contract_01.py
- C:\Users\tensh\eigo-radio\er030_key_phrase_db_hybrid_core_01.py
- C:\Users\tensh\eigo-radio\er011_human_review_lock_01.py
- C:\Users\tensh\eigo-radio\er006_m1_multi_candidate_01.py
- C:\Users\tensh\eigo-radio\er026_post_slowdown_cascade_rescue_01_test_01.py
- C:\Users\tensh\eigo-radio\er026_cs_audit_regression_01_test_01.py
- C:\Users\tensh\eigo-radio\er006_model_routing_pricing_coverage_test_01.py
- C:\Users\tensh\eigo-radio\docs\research\FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01\FZ_COMPLETION_PLAN_01.md