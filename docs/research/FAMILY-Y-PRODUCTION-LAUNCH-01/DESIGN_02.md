# DESIGN_02: Family Y 正式Production設計(Opus条件Aレビュー反映版)

管理ID: FAMILY-Y-PRODUCTION-LAUNCH-01 委任_02A / 2026-10-25(JST)。DESIGN_01(`DESIGN_01.md`)を、Opus条件Aレビュー(`OPUS_REVIEW_01.md` M-1〜M-6・R-1〜R-7)で更新した版。DESIGN_01から変えない部分は「DESIGN_01 §x」と参照する。02A=テキストcore(Closing/Gate lane)、02B=runner/audio/routing/scope lane。**本書の実装済み範囲は§5に明記**(未実装を実装済みと書かない)。

## 1. Opus指摘の反映表

| 指摘 | 反映 | 状態 | 場所 |
|---|---|---|---|
| M-1 判定器入力の欠落(『上記と同じ意味』の参照先が判定promptに無い) | Production版Tension判定promptで3項目定義を`_VOICE_ITEMS`から逐語展開(DEV不変)。DEV差分=展開のみ(test固定) | **実装済み・較正済み**。結果は重大(案B 2/7 FAIL)=`GATE_CALIBRATION_01.md` | `er121_family_y_text_core_01.py` `_TENSION_ITEMS`/`build_leak_prompt` |
| M-2 書換え規則 | Prompt 02の【最終パートの書き方】節をマーカーで逐語切出し+選定済み切り口(new_view+evidence_quotes)+指摘箇所のみ直す。書換え後は`check_closing`+記号/タグ検査、2回失敗で`REWRITE_STOP`。**追加(02A発見)**: 範囲保全guard(引用箇所を含む文以外は一字違わず保存) | **実装済み・runtime evidence済み** `REWRITE_EVIDENCE_01.md` | 同module `closing_rules_section`/`build_closing_rewrite_prompt`/`apply_rewrites`/`rewrite_scope_check` |
| M-3 共通工程は直接import | §3の境界表・構造一致test仕様・STOP/RUN_LOCKのimport | 設計(runnerは02B) | §3 |
| M-4 KPはrun_kp_with_review置換 | §4 | 設計(02B) | §4 |
| M-5 台帳漏れ・スコープ基準 | `SPEC_LEDGER_02.md/json`(65行、基準(i)〜(iii)、Chunk=除外+OPEN記録) | 完了 | SPEC_LEDGER_02 |
| M-6 voices段のruntime evidence | E-3でSNS Theme Packageから`voices`段を実行 | 計画(`BUDGET_PLAN_02.md`)。Voice Gate/書換えのcoreは実装済み、Voice生成stageは次委任 | §8 |
| R-1 案B registry | slug+Theme Package sha+Voice R0 sha+承認ref。env/CLI無効。Gate既存PASS記録は来歴検査付きで再利用(判定prompt shaが一致する場合のみ) | **実装済み**(M-1でprompt shaが変わったため旧記録は再利用されず再判定になる) | module `FIXED_CLOSING_REGISTRY`/`fixed_closing_lookup`/`reusable_prior_gate` |
| R-2 E-3はSNSで`english`・`plan`まで | 採用 | 計画 | §8 |
| R-3 実model照合 | **er006に実model照合関数は存在しなかった**(`require_model`は呼出前の契約照合のみ)。呼出前`require_model`+呼出後`response.model` startswith照合(X/Trialと同方式)を`chat`に実装 | 実装済み | module `chat`。**Opusの前提と実コードが違う点を報告事項とする** |
| R-4 Voice書換えは題材非依存`_pl`系 | `build_voice_rewrite_prompt`(共通前提・Personaは入力から。DEV `build_voice_rewrite_prompt_pl`の移植) | 実装済み | module |
| R-5 配線漏れ防止の一本化 | 正本=CURRENT_SPEC配線Status表。台帳jsonは立上げ作業表で、Y PRODUCTION_WIRED時に廃止。コード強制=M-3(b) | 設計。CURRENT_SPEC編集は02Aの範囲外(02B/後続) | SPEC_LEDGER_02 §0 |
| R-6 原価(cached_tokens・flex/Batch) | **未確認**。cached_tokens実測は、本委任のevidence runで記録した`raw_usage_log.jsonl`にusageがあるが、cached_tokensの有無は未確認(次委任でE-3実測時に確認)。flex/Batch可否は未確認 | 未着手 | `BUDGET_PLAN_02.md` §4 |
| R-7 routing key先行→E-3先行 | key名はFable確定、02Bがer006へ登録済み(9キー、02Aが突合済み)。Closing core完成=**E-3(一般化Closing evidence)を今すぐ開始できる状態**(runner不要。`produce_closing`を直接呼べる) | 準備完了 | §5-3 |

## 2. routing(Fable確定。キー名・model・effort)

| routing key | model | reasoning effort | 用途 | er006登録(2026-10-25 02Bが実施、02Aが突合) | er121側の期待値 |
|---|---|---|---|---|---|
| `FAMILY_Y_CLOSING_GENERATE` | gpt-6.1-sol | **high** | Closing一般化(Prompt 02) | 登録済み(同値) | `ROUTE` |
| `FAMILY_Y_CLOSING_REWRITE` | gpt-6.1-sol | medium | Closing Gate FAIL時の局所書換え | 登録済み。**Fable指定リストに無い追加key**(DESIGN_01 §2にあった。02Bも同値で登録) | `ROUTE` |
| `FAMILY_Y_LEAK_JUDGE` | gpt-6-luna | high | Leakage Gate判定(Voice 7項目/Tension 6項目) | 登録済み | `ROUTE` |
| `FAMILY_Y_VOICE_GENERATE` | gpt-6.1-sol | high | Voice R0生成 | 登録済み | `ROUTE` |
| `FAMILY_Y_VOICE_REWRITE` | gpt-6.1-sol | medium | Voice局所書換え | 登録済み | `ROUTE` |
| `FAMILY_Y_LEAD_GENERATE` | gpt-6.1-sol | high | リード生成 | 登録済み | `ROUTE` |
| `FAMILY_Y_PERSONA_INTRO` | gpt-6.1-sol | high | 人物紹介(3本1 call) | 登録済み | `ROUTE` |
| `FAMILY_Y_TRANSLATE_ADV` / `_STD` | `WRITER_MODEL`(=gpt-6-luna)参照 | (X定数) | 英訳(Adv忠実/Std簡易化) | 登録済み(`WRITER_MODEL`参照) | 02Bのdrift test(X定数との一致) |

- effortは`er006`に無い(modelのみ)。**effortの正本は`er121_family_y_text_core_01.ROUTE`**とし、`test_registered_in_er006_matches_when_present`でer006のmodelとのdriftを検出する(登録済みキー7個が一致することを02Aが実行確認)。
- 呼出前: `er006.require_model(key, model)`(未登録・不一致は`ModelContractViolation`=fail-closed、API前)。呼出後: `response.model`が期待modelで始まらなければ`ProvenanceViolation`(STOP)。`closing_record.json`に`model_id`(actual)/`expected_model`/`effort`/`routing_key`/`prompt_sha256`を記録。
- Charter 25節: 生成=gpt-6.1-sol(最新世代最上位系)、判定=gpt-6-luna(M7校正済みの判定専用。生成と別系統)。

## 3. 共通工程の「直接import」境界表(M-3a)

原則: **Y固有の新規範囲=テキスト生成・segment計画・timeline順・role文のみ**。それ以外は共通moduleの関数を**直接呼ぶ**。「相当版」を書かない。下表の関数名は02Aが実コード(`er026_family_z_fiction_production_runner_01.py`のstage関数とimport)で確認したもの。**「02B確認」列は02Bが実装時に実在・シグネチャを確認する項目(02Aは未確認と明記)**。

| Y stage | 直接importする共通関数/module | Y固有新規範囲(のみ) | 確認状況 |
|---|---|---|---|
| STOP/RUN_LOCK/費用guard | `er062_family_z_structure_01.check_stop_sentinel(where, run_dir)`、`acquire_run_lock(run_dir, argv)`、`release_run_lock`、`record_launch_and_check_storm`(いずれも実在を確認: er062:445/558/590/607)。予算は`er026.E2EBudget`/`wrap_generators_with_budget`(er026:2321。台帳YL-A30) | なし | STOP系=確認済み。予算wrapperのimport可否(er026の遅延import構造)=02B確認 |
| package_check | 共通なし(Theme Package検査) | 検査全体(出典逐語照合・Persona3名・立場3) | 新規 |
| voices | Voice Gate=`er121_family_y_text_core_01.run_gate(kind="voices")`(02A実装済み。DEV `p.run_gate`の展開移植)。API入口=`er121…chat`(routing照合) | Voice生成(Persona→R0)、Voice構造契約 | Gate=実装済み、生成=次委任 |
| lead_intro | `er121…run_leak`(Tension項目の補助適用)+`split_leadintro_flags`(適用外2項目) | Lead/紹介の生成・決定論検査 | 較正で`leak_evidence_memorable`の扱い要判断(GATE_CALIBRATION_01 §4) |
| closing | `er121…produce_closing`(02A実装済み) | (これ自体がY固有) | 実装済み・test PASS |
| english(Adv/Std英訳) | X承認済みの英訳関数(`FAMILY_Y_TRANSLATE_*`経由。`er053`系/`NATURAL_ENGLISH_ADAPTATION`/`STANDARD_A2_ADAPTATION`の既存呼出) | 5パート契約(段落数5)、Voice個性保持検査、In One Line非生成 | 02B確認 |
| plan | `w62.stage_plan`型の共通は無い(Z=story境界)。Yは5パートが固定 | segment計画(Y segment ID)、Voice別TTS Voice割当 | Y固有 |
| support(Preview/Comment/日本語タイトル) | Zは`w62.run_support_adv/std`(story固有)。Xは`er003_v1_n3_01_scaffold_generate`系 | Y版role文(Comment1〜3、Comment4廃止) | 02Bが「どの共通関数を使えるか」を確認(Z関数はstory固有の可能性あり=未確認) |
| kp | `er119_kp_wiring_01.run_kp_with_review(text=, kp_dir=, run_dir=, family=, slug=, level=, article_id=, ...)`(§4)。`ga.preflight()`が内部で呼ばれる | なし | シグネチャ確認済み(er119_kp_wiring_01.py:59)。family="Y"の受理=02B確認(未確認) |
| part1 | `er119_kp_human_review_01.part1_items(kp_dir)`(:1081)、`er003_kp_general_explanation_01`/`er003_kp_source_sentence_ja_01` | なし | 実在確認済み |
| part2 | `er120_part2_grammar_production_01`(別agent実装中)。Zは`_part2_cand_step`/`stage_kp`内で呼ぶ | Adv限定の接続のみ | 接続点(依存) |
| tts_b1b / tts_a2 | Z: `er063_family_z_audio_01.run_tts_stage`、X: er019側の共通TTS関数(retry/fallback/Local Rewrite/HR Lock/ASR/PNAP/RET/Chunk非適用) | Voice別TTS Voice割当(Algieba/Zephyr/Schedar)、ナレーターはlevel別Full Story設定から導出 | **02Bが「Zのer063関数がY segmentで使えるか」を確認**(Z=Dialogue/Seed前提の可能性。使えない場合のみ共通下位関数を直接呼ぶ。理由は台帳IDで許可リスト) |
| provision_shell | `a63.provision_shell_assets` | なし | 02B確認 |
| gate | `a63.run_audio_gate`(style/KP source/shared narration/Audio Validation/Std減速) + Y body拡張(`in_one_line`依存なし) | Y body拡張のみ | 02B確認 |
| assemble | `a63.run_assembly`型 | Y timeline順(DESIGN_01 §4-4) | 02B確認 |
| pages / page_verify | `er_user_listening_page_common_01`、`er063_family_z_page_verify_01`型 | 注意書き枠(既定None=出力不変) | 02B確認 |

### 3-1. 構造一致test(M-3b、02B担当。仕様のみここに書く)

- 目的: er026/er019の対応stageが呼ぶ**共通module呼出**を静的抽出し、er121 runnerと比較して配線漏れを機械検出する。
- 方式(推奨): `ast`でstage関数本体を走査し、`import X as m`に由来する`m.attr(...)`・`module.func(...)`の(module, func)集合を取得。Z/Xの対応stageとer121の対応stageの集合を比較し、**Zにあってer121に無い呼出**を失敗とする。
- 意図的差分(Y固有・除外)は**許可リスト**に`(module.func, 台帳ID, 理由)`で列挙(例: `chunk_tts.*`=YL-B08除外+OPEN、`fx_iol.*`=YL-C08 In One Line廃止、`xr.*In One Line`系)。許可リストに無い差分は失敗。台帳(`spec_ledger_02.json`)のIDが実在することも検査。
- 失敗時: 該当共通呼出の追加か、許可リストへの台帳ID付き理由追記のどちらかが必要。**新しい共通仕様をX/Zへ配線した時、Yに入れ忘れるとこのtestが落ちる**=再発防止。

### 3-2. STOP/RUN_LOCK(M-3c)
`er062_family_z_structure_01`の関数をimportして使う(「Z方式を移植」ではなく同一関数)。`--regenerate-stage`/`--stages`はZ方式(DESIGN_01 §3)。OPEN-480注意: 再実行は`provision_shell,gate,assemble,pages,page_verify`を1起動で指定(runnerのhelpとOPERATIONSに明記)。

## 4. KP段(M-4)
- KP呼出そのものを`er119_kp_wiring_01.run_kp_with_review(..., family="Y"...)`に置換(`sc.run_key_phrases`互換)。Xの入口確認(PENDING=rc4、NotConfirmed=rc4、Inconsistent=rc3)・`verify_selection_matches_outputs`・`part1_items`も同形で最初から入れる。文法HR/Part 2(er120)のみ接続点として残す(Adv限定、0件許容)。
- Y KPの引用文参照方式は**X=候補ID方式**(共通Core)を使う(台帳YL-A24/A25)。Z=D1(文ID事後付与)はDialogue向けでYに不適。
- 未確認(02B/KP HR担当が確認): `family`引数が`"Y"`を受理するか、`src_fn`の既定がY narrator記事で機能するか、gloss段のHR入口の有無(YL-A28)。

## 5. 02Aが実装済みのテキストcore(`er121_family_y_text_core_01.py`、56 test PASS)

### 5-1. 実装範囲(未実装を含まない)

| 機能 | 関数 | 備考 |
|---|---|---|
| Prompt 02 byte一致コピー+sha照合 | `er121_prompts/closing_general_02.txt`、`load_prompt_parts` | sha 4713ceff…、CRLF変換でもsha不変、不一致=`PROMPT_SHA_MISMATCH` STOP(runtime)。DEV原本と`cmp`一致(test) |
| 入力block・schema・決定論検査・再生成1回 | `normalize_input`/`render_blocks`/`build_prompt`/`SCHEMA`/`check_structure`/`check_closing`/`explain_problem`/`generate_closing_general` | DEVと出力一致をtest固定(別module import=DEV importはtestのみ) |
| `CLOSING_GENERAL_CONTRACT_STOP` | `generate_closing_general` | 再生成後も違反でSTOP |
| Leakage判定(Voice/Tension) | `build_leak_prompt`/`run_leak`/`leak_schema_for` | **Tension版のみM-1展開**。Voice版はDEVとバイト一致 |
| Gate運用 | `run_gate(kind=voices/tension)` | 判定≤3、局所書換え、`REWRITE_STOP`、`LEAKAGE_RESIDUAL_STOP`、`gate_history`全保存(`leak_check_N.json`+`gate_result.json`)、FAIL稿は`final_texts.json`を作らず後続へ流さない |
| 書換え(Closing) | `closing_rules_section`/`build_closing_rewrite_prompt`/`apply_rewrites`/`rewrite_scope_check` | M-2。範囲保全guard追加 |
| 書換え(Voice) | `build_voice_rewrite_prompt` | R-4。題材非依存 |
| 案B固定注入 | `FIXED_CLOSING_REGISTRY`/`fixed_closing_lookup`/`reusable_prior_gate`/`produce_closing` | R-1。判定1回、書換え禁止、FAIL=`FIXED_CLOSING_GATE_FAIL`でSTOP。**判断待ち(GATE_CALIBRATION_01 §3)** |
| Closing段の一括 | `produce_closing(client, slug=, inp=, theme_package_sha256=, voice_r0_sha256=, out_dir=)` | `closing_record.json`/`closing_final.txt`/`gate/`を出力 |
| routing/API入口 | `ROUTE`/`chat` | §2 |

### 5-2. 失敗終了時の最終成果物(目的要件との照合)
- Closing残存FAIL(`LEAKAGE_RESIDUAL_STOP`): `closing_record.json`(status=LEAKAGE_RESIDUAL_STOP)+`gen/`(分析・候補・根拠引用)+`gate/`(全判定履歴)。`closing_final.txt`は作らない(暫定版を公開しない)。JA稿(Voice+Lead+紹介)は呼出元が保持。音声は作らない。→目的要件(完成音声+限定試聴ページ)に対しては「未完成と明示」。
- 案B Gate FAIL: 同様に`closing_final.txt`なし。書換え・判定再試行をしない。
- `REWRITE_STOP`: `gate/gate_result.json`にstatus=REWRITE_STOP+履歴。

### 5-3. 02B/後続への引継ぎI/F
- runnerはstageで`produce_closing(...)`を呼ぶ。`client`は`.responses.create(**kw)`を持つOpenAI client(test用の偽clientも同形)。`cl.install(<run>/raw_usage_log.jsonl)`はrunner側で行う(本moduleのstageタグは`THEME_TAG="FAMILY_Y_PRODUCTION_01"`+`yp_closing_*`)。費用guardはrunner側(各callの前に`_guard`)。本moduleは`E2EBudget`を持たない。
- `inp`はTheme Package→`normalize_input(question, premise, distinctions, personas, voices)`で作る(adapterはrunner側)。`theme_package_sha256`/`voice_r0_sha256`はファイルbytesのsha256(registry照合用)。
- 返り値: `{"text": <最終Closing>, "record": <closing_record>}`。STOP時は`er121…YStop`(`.code`: `CLOSING_GENERAL_CONTRACT_STOP`/`REWRITE_STOP`/`LEAKAGE_RESIDUAL_STOP`/`CLOSING_POST_GATE_STOP`/`FIXED_CLOSING_*`/`PROMPT_SHA_MISMATCH`)。runnerは`code`を`run_status.json`へ書く。
- **`guard`引数**: `produce_closing`/`generate_closing_general`/`run_gate`/`run_leak`/`chat`は`guard=callable(stage_label)`を受け取り、**各API呼出の直前(routing照合の後)に1回呼ぶ**(例外ならAPIを呼ばない)。runnerの`_guard(ctx, label, est)`を包んで渡す(test: `TestGuard`)。ラベル例: `yp_closing_gen`/`yp_closing_leak1`/`yp_closing_rewrite1`。
- **(委任_02Cで実装済み→§12。以下は02A時点の記述)`produce_article`は02Aでは未実装**(02B runnerは`produce_article(client, slug=, theme_package=, out_dir=, guard=)`→`{title, lead, intros, voices, closing, closing_record}`を期待し、無ければ`FAMILY_Y_TEXT_CORE_NOT_CONNECTED`でSTOPする=安全側)。Voice生成・Lead・人物紹介・見出しの生成関数が未実装のため、記事全体の組立は**次の02委任(Voice/Lead/紹介生成の移植)**で実装して接続する。`produce_closing`はそのClosing部として使われる。`closing_record`は`produce_closing`が返すものをそのまま渡す。
- 追加routing key `FAMILY_Y_CLOSING_REWRITE`は02B登録済み。`ROUTE`のeffortをer006が持たないことに注意。
- **Lead/紹介のGate(補助適用)の扱いは判断待ち**(GATE_CALIBRATION_01 §4)。Lead/紹介の生成関数は未実装(次委任)。

## 6. DEV/Trial専用機能の非移植(OT-23の実装確認)
`er121_family_y_text_core_01.py`に次が無いことをtestで固定: DEV(`er110*`)のimport、`SKIPPED_BUDGET`(Gate予算skip)、`os.environ`/`argparse`/`sys.argv`/`__main__`、`openai`の直接import、`patched_*`モジュール差替え、alias segment ID。DEV側は`er121`を参照しない(test: `test_dev_modules_do_not_import_production_core`)。

## 7. 案B固定注入とM-1の関係(重要)
- 案Bは判定promptが変わるため既存PASS記録を再利用できず、**実行時に毎回1判定**を通す。M-1後promptで2/7 FAIL → 約3割でSTOPする見込み。これは**Fable指示『案BがFAILならSTOPしてユーザー判断』**に該当するため、案B関連の追加作業を止めて報告する(GATE_CALIBRATION_01 §3)。registry実装自体は完成している(判断後にE-1で使える)。

## 8. E-3(一般化Closing + voices段のruntime evidence、M-6/R-2/R-7)
- 対象: SNSの年齢制限(Voice R0既存・Theme Package既存)。段=`voices`(Production Voice生成+Gate)→`lead_intro`→`closing`(`produce_closing`、slug=`sns_age_limit`=registry外→一般化)→`english`→`plan`(音声なし)。想定費用は`BUDGET_PLAN_02.md`。
- **前倒し可能**: `closing`だけは今すぐ`produce_closing`を直接呼んで実行できる(runner不要)。M-2書換えevidence(過去FAIL稿)は取得済み(`REWRITE_EVIDENCE_01.md`)なので、E-3のclosing部は「新規生成の一般化経路」のevidenceとなる。voices/lead_intro/englishはrunner接続後。

## 9. Dangling Reference防止(DESIGN_01 §11の更新)
- 新規参照: `er121_family_y_text_core_01.py`(被参照=02Bのrunner[未]・test)、`er121_prompts/closing_general_02.txt`、`er121_family_y_calibration_01.py`(証跡用runner、Production経路から非参照)、台帳`spec_ledger_02.json`。被参照0の項目は「次委任で接続」を`OPEN_TRACKING_02.md`に記録。
- 台帳02が正。`spec_ledger_01.json`はSPEC_LEDGER_02に置換済み(履歴として残置)。台帳のtracking(OPEN番号・path)の実在はCloseoutでGrep。

## 10. 判断候補と未確認(まとめ)

1. **判断候補(D、真に新しい判断)**: 案BのM-1後Gate FAIL(2/7)の扱い(案I/II/III、推奨=案I)。`GATE_CALIBRATION_01.md` §3。
2. **判断候補(Fable判断)**: Lead/紹介の補助適用で`leak_evidence_memorable`が3/4 FAIL → 適用対象外にするか(承認Gate定義は不変、補助適用の範囲設定)。
3. 既知(ユーザー判断候補G-1/G-2): R2宅配H2の`leak_discovery_syntax`は定義補完で消えない(3/3)。G-2は不要になるどころか必要性が裏づけられた。
4. 未確認: `run_kp_with_review`のfamily="Y"受理、gloss HR、予算wrapperのimport可否、cached_tokens/flex/Batch(R-6)、Z audio関数のY segment適合。

## 11. Fable判断(委任_02C、2026-10-25。委任文の転記)

| ID | 判断 | 内容 |
|---|---|---|
| OT-27 | **案Iを採用=進める** | 案B(固定Closing)はE-1実走時に**1回だけ判定**し、FAILなら**STOPして**「ユーザー承認済み本文とGateの衝突」としてユーザー判断へ上げる。推奨案として、既存のHuman個別承認記録機構(`record_human_approval`型)でGate FAILをユーザー承認で上書きする案を提示する予定。書換え禁止・判定再試行禁止(I-4)は維持。 |
| OT-28 | Lead/人物紹介の補助適用範囲を確定(Fable権限) | Lead/紹介はナレーター文であり、Voice用の`leak_evidence_memorable`(人物の経験・感情の具体性)は性質上適合しないため**非適用**。適用するのは出所・創作・一人称・Tension専用2項目を除く「ナレーター文に意味を持つ項目」のみ。これは承認済みGate定義の変更ではなく、Y固有の新パート(Lead/紹介)への適用範囲の確定。委任_28で用いた決定論検査(主張先取り語禁止・本人語りとの10字連続一致なし・字数)は必須のまま。 |
| 個別Cap | 150→**170円** | 7-7の自律範囲(300円以下)。`BUDGET_PLAN_03.md`。 |
| E-3 voices段 | SNS Theme Packageから**実生成** | Opus M-6どおり。R0再利用ではProduction runtime evidenceにならない。 |
| `rewrite_scope_check` | 維持 | 緩和は運用実績後。 |
| G-2 | 変更しない | `leak_discovery_syntax`が「見えてくる」を3/3 FAIL(台帳YL-E02)。Gate文言の補足はユーザー判断事項として提示。 |

## 12. 委任_02C: 記事全体の実装(`produce_article`。Status=実装・offline test済み。**Production runtime evidence未取得**)

### 12-1. 実装範囲(`er121_family_y_text_core_01.py`に追加。DEV `er110_*`は無変更・非import)

| 機能 | 関数 | DEV移植元 | 備考 |
|---|---|---|---|
| Theme Package検査・sha | `validate_theme_package`/`load_theme_package` | `opinion_based_03.validate_theme/load_theme` | shaは案B registryと同じ算出(ファイルbytes)。dictのみ渡すとcanonical JSON shaになり案Bは注入されない(fail-closed) |
| Voice生成 | `build_voice_prompt`/`render_persona`/`generate_voice` | `opinion_based_01.build_voice_prompt_ob`+`02.VOICE_PROMPT_OB2/render_persona_ob2`+`03`の`relevant_terms`絞り込み | Prompt=`er121_prompts/voice_generate_02.txt`(sha48645f1d…)。構造契約違反は1回だけ再生成、残れば`VOICE_CONTRACT_STOP` |
| Voice出典付番・UNMAPPED再生成 | `build_map_prompt`/`check_mapping`/`map_voice`/`unmapped_extra` | `opinion_based_01`(OF-Y6-07) | luna/medium。再生成後の残りは記録のみ(DEVと同じ。検証済みR0でも最終付番に1件残る実績があるため、STOPにしない) |
| 構造タグ | `tag_structure`/`structure_fire` | `persona_pipeline`(OF-Y5-06) | luna/medium。発火なら該当1本だけ1回再生成。記録のみ |
| Voice Gate | `run_gate(kind="voices")`(02A) | — | 判定≤3・局所書換え(`FAMILY_Y_VOICE_REWRITE`)・`gate_history`全保存。残存FAILは`VOICE_RESIDUAL_STOP`(`final_texts.json`を作らず後続へ流さない)。**予算によるGate skipは移植していない** |
| Lead | `build_lead_prompt`/`check_lead`/`generate_lead` | `redelivery_revision_01`(委任_28) | Prompt=`lead_generate_01.txt`(sha76282235…)。AI編集説明なし(検査`HAS_AI_EDIT_ANNOUNCEMENT`)。字数115〜160 |
| 人物紹介(3本1 call) | `build_intro_prompt`/`check_intro`/`generate_intros` | 同(委任_28) | Prompt=`persona_intro_01.txt`(sha787794d6…。題材固有の2箇所だけplaceholder化し、DEVの宅配用語を代入するとDEV版とバイト一致)。主張先取り語禁止・本人語りとの10字連続一致なし・字数32〜62。紹介は「1人につき1〜2文・改行なし」(DEVどおり。委任文の「1文」はDEVの1行=単一行契約と解釈。厳密な1文化は仕様変更になるため行わず報告) |
| 補助Gate | `run_leadintro_gate`/`split_leadintro_flags(na_fields=)`/`LEADINTRO_NA_FIELDS_PROD` | `rev.LEADINTRO_NA_FIELDS`+OT-28 | Tension判定を1回。適用外=`leak_tension_reverts_to_research`/`leak_binary_camp_split`/`leak_evidence_memorable`。適用対象FAILは`LEADINTRO_LEAKAGE_FLAGGED`でSTOP(本文を手で直さない) |
| 再利用(E-1) | `load_reuse`/`reuse_voices`/`reusable_prior_voice_gate` | `redelivery_audio.load_r0` | R0 article↔Gate最終本文のbyte一致を検証。Gateは来歴検査付き既存PASS記録を再利用(判定prompt shaが一致する場合のみ)、使えなければ判定1回(書換えなし。FAILは`REUSED_VOICE_GATE_FAIL`)。再利用Lead/紹介は本Productionの決定論検査を再度通す |
| 出典連続一致 | `verbatim_report`/`shingle_hits_ja` | `redelivery_audio.shingle_hits_ja` | Theme Packageの`source_dir`(または再利用manifestの`source_dir`)がある場合のみ検査。1件でも→`SOURCE_VERBATIM_STOP`。無い場合は「未確認」と記録 |
| 組立・契約検査 | `render_article_text`/`check_article_parts` | `rev.render_revised/check_revised` | 5パート(Lead/[紹介+Voice]×3/Closing)、In One Line不在、AI編集説明不在、Voice本文がGate最終とbyte一致 |
| 一括 | `produce_article(client, *, slug, theme_package, out_dir, guard=None, reuse=None, theme_package_path=None)` | — | 返り値`{title, lead, intros, voices, closing, closing_record, records}`(02B runnerの`stage_text`が期待する形。runner+実coreの結線をoffline smokeで確認済み) |
| routing | `ROUTE_AUX`/`preflight_routes` | — | 付番・構造タグ用に**新key 2本**(下記)。`produce_article`は最初のAPI呼出の前に使用予定の全keyを`require_model`で照合(未登録なら費用0で停止) |

- **サブステージ再開(二重課金防止)**: `voices/`・`lead_intro/`・`closing/`の各`stage_*.json`に入力key(Theme Package sha・slug・Prompt sha・再利用manifest・module sha)を保存し、一致すればAPI 0で再利用する。Closing STOP後の再実行でVoice/Lead/紹介を再課金しない(test固定)。
- **逐次実行**: Voice生成を3本並列にしない。`er005_cost_logger.logging_context`がprocess globalでstageタグが競合するため(DEVは並列で混在し得た)。時間はVoice段が約3倍、費用への影響なし。

### 12-2. 新routing key(02Bへの要求。er006登録+pricing)

| key | model | effort | 用途 |
|---|---|---|---|
| `FAMILY_Y_VOICE_PROVENANCE_MAP` | gpt-6-luna | medium | Voice出典付番(DEV `ob_map_*`と同一設定) |
| `FAMILY_Y_VOICE_STRUCTURE_TAG` | gpt-6-luna | medium | 構造タグ(DEV `ob_structure*`と同一設定) |

02Bの`test_text_core_route_table_matches_contract_no_drift`(`tc.ROUTE`全件のdrift検査)を壊さないため、`ROUTE`本体ではなく`ROUTE_AUX`に置いた(登録後に`ROUTE`へ統合してよい)。`chat`は両表を引く。**未登録のままE-3を実行すると`produce_article`冒頭のpreflightで`ModelContractViolation`となりAPI呼出0で停止する**(Voice生成の費用が発生する前)。

### 12-3. 02Bのrunnerへの要求(02Cは編集しない)

1. `stage_text`の`fn(...)`呼出に`theme_package_path=ctx.theme_package_path`を追加(dictのみだと案B registryのsha照合が成立せず、E-1が`FIXED_CLOSING_PROVENANCE_MISMATCH`/`REQUIRES_R0_REUSE`で停止する)。
2. `--reuse-manifest <json>`(任意)を追加し`reuse=`として渡す。manifest例=`theme_packages/redelivery_fee_reuse_01.json`(schema=`y_reuse_v1`)。
3. 出力dir衝突なし(02C: `text/{voices,lead_intro,closing}/`・`article_record.json`・`article_status.json`・`article_assembled.md`。runner: `text/article_ja.md`・`text/text_records.json`)。`res["records"]`は`text_records.json`に保存される。
4. Closing再生成が`--regenerate-stage`の明示のみ(DESIGN_01 §3)にするには、`text`段を`voices`/`lead_intro`/`closing`の3段に分けて公開関数(`produce_voices`/`reuse_voices`/`generate_lead`/`generate_intros`/`run_leadintro_gate`/`produce_closing`)を直接呼ぶ方式も可(現状の`produce_article`は一括。サブステージ再開で費用の二重払いは防いでいる)。

### 12-4. Theme Package / 再利用manifest

- Theme Package=`THEME_DATA`形式(`theme_id`/`world_frame`/`sheets`×3/`who_ja`/`restricted_voice_ids`)。任意の追加欄: `lead_premise_ja`/`lead_scope_lines`(無ければ`question_ja`と`distinctions`から機械的に作る=新しい事実を足さない)、`intro_checks`(役割語・具体物・主張先取り語。無ければ汎用導出し`check_mode=derived`と記録)、`source_dir`。
- SNS年齢制限: `theme_packages/sns_age_limit_package_01.json`(sha aa37a1e1…)。DEV `WORLD_FRAME_02`/`SHEETS_02`/`WHO_JA_02`の機械転記(testで内容一致を固定)。E-3のvoices段入力。
- 宅配: 既存`OPINION_BASED_02/THEME_DATA_02.json`(sha f0d0af36…、registry登録済み・無変更)+`theme_packages/redelivery_fee_reuse_01.json`(R0 Voice・改訂Lead・人物紹介・`intro_checks`・`source_dir`)。

### 12-5. 失敗終了時の最終成果物(目的要件との照合)

| STOP | 残る成果物 | 目的要件(完成音声+限定試聴ページ)に対して |
|---|---|---|
| `THEME_PACKAGE_INVALID`/`FIXED_CLOSING_REQUIRES_R0_REUSE`/`REUSE_MISMATCH`/routing未登録 | `article_status.json`のみ(API 0・費用0) | 未着手と明示 |
| `VOICE_CONTRACT_STOP`/`VOICE_RESIDUAL_STOP`/`REWRITE_STOP` | `voices/voices_partial.json`(確定稿ではない)・`gate_voices/`全履歴・`article_status.json`。`voices_final.json`/`final_texts.json`は作らない | 未完成と明示。Lead/紹介/Closing/音声へ進まない |
| `LEAD_CONTRACT_STOP`/`INTRO_CONTRACT_STOP`/`LEADINTRO_LEAKAGE_FLAGGED` | Voice確定稿(`voices_final.json`)+Lead/紹介の試行記録。再開時Voiceは再課金なし | 未完成。Closingへ進まない |
| `FIXED_CLOSING_GATE_FAIL`(OT-27) | Voice・Lead・紹介の確定稿+`closing/gate/`判定記録。`closing_final.txt`なし | ユーザー承認本文とGateの衝突=ユーザー判断へ。暫定版を作らない |
| `CLOSING_*`/`LEAKAGE_RESIDUAL_STOP` | 02Aの規定どおり(`closing_record.json`にstatus・`gen/`・`gate/`)。Voice/Lead/紹介は確定稿を保存 | 未完成 |
| `ARTICLE_ASSEMBLY_STOP`/`SOURCE_VERBATIM_STOP` | `article_assembled.md`(確定稿ではない)・`verbatim_hits.json`。`article_record.json`は作らない | 公開しない(権利確認の対象) |

### 12-6. E-1〜E-3の実行に必要な残作業

- **E-3(SNS一般化+voices実生成)**: ①02Bのer006登録(`FAMILY_Y_*` 9キー+上記新2キー+pricing) ②runnerの`stage_text`が`produce_article`を呼ぶ(現状でも呼べる。`theme_package_path`は任意) ③`--approved-budget-jpy`と日次予算確認 ④英訳以降(02B)。voices段〜closingまでは**今すぐ実行可能な状態**(runner経由でなくても`produce_article(client, slug="sns_age_limit", theme_package=<SNS pkg path>, out_dir=…)`で単独実行できる)。見積39〜48円(`BUDGET_PLAN_03.md`)。
- **E-1(宅配+案B)**: ①上記01〜02の要求(`theme_package_path`・`--reuse-manifest`) ②案BのGate判定(1回)でFAILすればSTOP→ユーザー判断(OT-27 案I)。③英訳以降(02B)。
- 未確認(02B領域): `run_kp_with_review`のfamily="Y"受理、gloss HR、予算wrapperのimport、Z audio関数のY segment適合、cached_tokens/flex/Batch。

## 13. 追加決定反映(委任_04、2026-10-25。ユーザー追加決定USER_02 ①②③)

原文=`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_02.md`。台帳=`SPEC_LEDGER_03.md`、追跡=`OPEN_TRACKING_03.md`、費用=`BUDGET_PLAN_04.md`。以降、§1〜12の記述のうち下記と矛盾する箇所(§3の`chunk_tts.*`許可リスト、§12の案B「判定1回」、OT-21/OT-27等)は**本節が優先**する。

### 13-1. ① Chunk TTS(X方式をY正式採用。YL-B08)

- 方式: 共通`er117_chunk_tts_production_01`の**X方式(段落単位chunk+0.2秒ポーズ)を直接import**して使う(Yで再実装しない)。ZのB_r1は採用しない。
- 適用単位: Y本文8 segment(`y_lead`/`y_intro_1..3`/`y_voice_1..3`/`y_closing`)それぞれに`chunk_tts.plan_x_part`を適用(`plan_y_chunks`)。段落が2つ以上のsegmentだけ分割、1段落は従来の1 call(X規則)。chunk ID=`<segment_id>_k<j>`(`ys.Y_CHUNK_ID_RE`)。**分割はsegmentの内側だけ**=話者切替(intro→voice、voice→次のintro)は別segmentなので結合も分割もされない(testで固定)。
- level: Adv(b1b)本文のみ(X同様。Std[a2]は非chunk)。
- 経路: 生成=`_generate_y_body_segment_chunked`(chunkごとに従来本文と同一呼出し`generate_news_narration_wide_margin`、同一Voice/Style/model/ASR/retry/fallback、chunk失敗後も後続chunkを続行、Style記録はchunkごと)→親集約entry(`chunk_tts.refresh_parent_status`。statusは`OK`か`CHUNKS_NOT_ALL_VALIDATED`。共有Audio Validation Gateで必ずブロック)+親wav(生連結)→gate(`y_style_gate`は親でなく**全chunk**を検査、planにあるのにentryが無いchunkはBLOCK)→組立(`_load_y_body_chunks`が`verify_parent_integrity`+`verify_raw_parent`を音声読込前に実行→共通`apply_family_x_b1_gain`がchunk別gain+0.2秒無音で連結)。resume: 版違い・Voice不一致のchunk entryは再利用しない、保存済みplanと不一致ならSTOP(`reconcile_saved_plan`)。
- fail-closed: (a)適用可否表がYを非適用に戻されたら課金前STOP(`FAMILY_Y_CHUNK_TTS_SCOPE_REVERTED`) (b)chunk idが共通role判定でFULL_STORYに解決されなければ課金前STOP(`FAMILY_Y_CHUNK_ID_ROLE_UNRESOLVED`。共通er020の正規表現追加が必要=OT-44)。
- `--only-segments y_voice_2`は親が選択されていればchunk idも選択扱いにする(`_only_includes_chunks`。共通runnerのXのchunk id形式しか解釈しない`_only_segments_skip`を共通module変更なしで補う)。
- 記録: `audit/chunk_tts_decision.json`(decision=`applied_X_method`、approval=APPROVED_FOR_PRODUCTION、z_b_r1_adopted=false、segmentごとの段落数・chunk id)、`audit/chunk_plan_b1b.json`、`audit/chunk_tts_evidence_b1b.json`(分割がある場合)、`audit/chunk_tts_assembly_b1b.json`(0.2秒の実測offset・chunk別gain/RMS/peak)。
- 重要な事実(OT-42): 現行のY本文契約はsegmentごとに**1段落**(check_voice_pl/closing/lead/intro)のため、通常の記事では分割が発火せず従来の1 callになる。分割機構は複数段落segmentで機能することをofflineで検証済み。

### 13-2. ② Closing Prompt/Gate(Prompt 02・既存Gate不変。案Bの再判定仕様の更新)

- Prompt 02+gpt-6.1-sol/high、Gate基準、Tension判定prompt(M-1定義展開版)は**変更しない**。Prompt 03・Gate緩和・Gate文言補足(G-2)は行わない(OT-20)。
- 一般Closing: 従来どおり`run_gate`(判定<=3+局所書換え、残存FAILは`LEAKAGE_RESIDUAL_STOP`=公開しない)。
- 案B(`redelivery_fee`のみ・他記事へ拡張しない): `run_gate(allow_rewrite=False, rejudge_without_rewrite=True, max_judgements=3)`。承認本文は書換えない。同一本文を最大3回判定し、PASSした時点で終了、3回ともFAILなら`FIXED_CLOSING_RESIDUAL_FAIL`でSTOP(`closing_record.json`にstatus・n_judgements・judgements[]を残し、`closing_final.txt`は作らない)。PASS時も各判定の結果(attempt・本文sha・flag有無・FAIL項目・model・prompt sha)を`closing_record.judgements`へ記録(OT-45)。過去の来歴検査付きPASS記録の再利用(`reusable_prior_gate`)は従来どおり。
- 置換: `FIXED_CLOSING_GATE_FAIL`(判定1回で即STOP)は廃止し`FIXED_CLOSING_RESIDUAL_FAIL`へ(残存Grepは`er121_*.py`で0件)。

### 13-3. ③ Voice生成方式(YL-C03=APPROVED_FOR_PRODUCTION)

- 実装(`produce_voices`/Voice Gate)に変更なし。承認Statusのみ更新。公開前条件(出典・利用許諾、V1根拠R2+のみ/人手収集約25分/目視1名/V2単一出典例外)は省略せず継続管理(OT-46)。意見収集の自動化はScope外。

### 13-4. 配線漏れ防止(U2 §3)

- 台帳を66行へ更新(SPEC_LEDGER_03)、PM Closeout Mandatory Checkに項目33(共通仕様のX/Y/Z配線Status確認)を追加(`PM_GOVERNANCE.md` 3節)。未承認仕様(NO_PREADOPT 4件)は先行採用しない。

## 14. 追加承認2件の反映(委任_05、2026-10-25。ユーザー正式承認 USER_03 §1・§2)

原文=`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_03.md`(取得元jsonlで末尾が文字化け。無改変保存)。台帳=`SPEC_LEDGER_04.md`、追跡=`OPEN_TRACKING_04.md`、案B承認の詳細=`HUMAN_APPROVAL_CASE_B_01.md`、補足の較正=`GATE_CALIBRATION_02.md`。以降、§13-2の「Gate文言補足(G-2)は行わない」「案Bは3回FAILなら常に`FIXED_CLOSING_RESIDUAL_FAIL`でSTOP」は**本節が優先**する(§13-2のうち、他項目FAIL時のSTOP・書換えなし・判定<=3・過去記録保持は維持)。

### 14-1. ① 案Bの個別Human承認(`er121_family_y_text_core_01.py`)

- 適用条件(全て「かつ」。判定は`evaluate_case_b_human_approval`1関数): registryに`human_approval`がある案B slug(`redelivery_fee`のみ)/本文byte一致/Gate=`LEAKAGE_RESIDUAL_STOP`・書換えなし・3判定すべてFAIL/全判定の本文sha=承認本文sha/FAIL項目の和集合=={`leak_evidence_memorable`}/FAIL sectionが`tension`のみ。
- 発動時: Gate判定ファイル(`leak_check_N.json`・`gate_result.json`)は改変せず、別ファイル`human_approved_closing.json`(既存`record_human_approval`と同形のキー+approval_ref=USER_03 §1・各判定のFAIL理由/引用/snapshot sha)を書く。`closing_record.status=PASS_BY_HUMAN_APPROVAL`・`human_approval_ref`・`original_gate_result`・`judgements[]`。Gate PASSの印`final_texts.json`は作らない。再実行時は`gate_prior_runs/`へ過去判定を退避、旧承認記録は`previous_entries`へ。cache/resume再利用時も`verify_human_approval_record`で来歴(本文sha・項目・snapshot sha)を再検査し、不一致は`HUMAN_APPROVAL_PROVENANCE_MISMATCH`でSTOP。
- 適用しない場合: 従来どおり`FIXED_CLOSING_RESIDUAL_FAIL`でSTOP(`closing_record.human_approval_checked.reasons`に理由コード)。一般化Closing経路・他slug・本文変更/再生成/局所書換え後は対象外。新しいflag・env・CLI・設定dictなし(registry定数のみ)。

### 14-2. ② `leak_discovery_syntax`の判定定義の補足

- 文言=ユーザー承認原文の一文: 「Prompt指示に基づく『〜から見えてくる』という提示表現は解釈語と見なさない。」。Tension判定prompt(Closing判定)の当該項目定義の末尾にのみ付加(`DISCOVERY_SYNTAX_SUPPLEMENT`・`build_leak_prompt(..., discovery_supplement=True)`)。Lead/人物紹介の補助判定は`discovery_supplement=False`(補足なし=M-1定義のまま)、Voice判定(`_VOICE_ITEMS`)・DEV・他Family・`leak_tension_reverts_to_research`・Prompt 02(sha 4713ceff…)は不変(test固定)。
- 委任文の後半「ただし、3人の語りに根拠がない解釈、不要な一般化、研究・調査の説明への逆戻りは引き続きFAIL。」は**較正により不採用**(GATE_CALIBRATION_02 §0-2: 案Bが`leak_discovery_syntax`で3/3 FAILし①の救済条件を壊す、無関係な本文のFAILが増える)。『引き続きNG』の担保は既存の他項目(不変)。

### 14-3. ④ 共通`er020`のY chunk ID解決(OT-44(a))

- `_FAMILY_Y_SEGMENT_PATTERN`へ`(?:_k[1-9][0-9]*)?`を追加(import時自己検査に`y_voice_2_k1`・`y_closing_k12`)。`er121_family_y_structure_01.Y_CHUNK_ID_RE`と同形(test固定)。`er117`の既存ID不変testは`y_`始まりを除外(Yの解決は`er121_family_y_text_core_01_test_01.py::TestEr020YChunkPattern`で固定)。`er121_family_y_structure_match_test_01.py`の旧負例`y_lead_k1`は意図した変更に合わせて更新。

### 14-4. runnerへの要求(委任_03所有。本委任では編集しない)

- `"chunk_tts": "not_applicable_Y"` → `"applied_X_method"`(`er121_family_y_runner_01.py` 984行・1181行、`er121_family_y_runner_01_test_01.py` 118行)。`chunk_tts_decision.json`(`ys.chunk_decision_record`)の`decision=applied_X_method`と整合させる。
- `closing_record.status=PASS_BY_HUMAN_APPROVAL`の取り扱い: runnerは`closing_record.source`/`final_sha256`だけを読むため無改変で動くが、最終manifest/EVIDENCEへ`status`・`human_approval_ref`・`original_gate_result`を転記するのが望ましい(受入12項目の「Gate結果の記録」)。
