# WIRING_DESIGN_01 (FAMILY-XZ-M2P0-N01-PRODUCTION-WIRING-01 委任_01、2026-10-13)

Status: **WIRING_DESIGN_DRAFT(Opus条件A/C待ち)**。設計のみ。Production code・Prompt・Validator・Gate・SSOT変更なし。費用JPY0(有料API・生成なし)。`PRODUCTION_WIRED`ではない。
使用モデル(開発・評価用途最新モデル原則): 本委任はAPI呼出なし(読取・設計のみ)のため該当なし。

## 0. 先に結論(Fable/Opus向け、5行)

1. **M2P0(Family X)**: 配線は可能。ただしM2は「M1(照会予算拡大+precision guard+U2+U3)」と「(a)(b2)(c)」の**Trial専用module群(`er064_kp_opt_01_upstream_core.py`/`er064_kp_idiom_trial_01_matcher.py`/`..._pipeline.py`、約490+160+130行)に依存**しており、Production moduleへの**移設(copy+byte parity test)**が必須。挿入点は`er030_key_phrase_db_hybrid_selector_01.run_db_hybrid_selection`のStage1直後(L450-461)と候補行組立(L508、`evidence_fn`引数は既存)。選定Prompt P0は**無変更**(sha固定、§A-iii)。
2. **M2P0(Family Z)**: **構造上載らない**。Family Zの`kp` stageは`run_key_phrases`の既定`kp_backend="strategy_l"`(本文全文方式、shortlistなし)で、`db_hybrid`も`family_profile="family_z"`(`NotImplementedError`)も未配線。M2を載せるには「Family ZへDB Hybridを採用する」という**別の仕様変更**が必要 → **USER_DECISION_REQUIRED候補 Z-1(STOP条件に該当、設計は継続)**。
3. **N01(Family X)**: 「現行P8」はFamily Xでは**Coffee限定の`--style-profile`機構(`er019_family_x_style_profile_01.py`)にのみ存在**し、defaultのFull Story styleはP8ではない(`FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]`、Stdは+減速instruction連結)。「N01を全Family X記事のdefaultにするか/Coffee profile内のP8置換にとどめるか」は**解釈が分かれる → USER_DECISION_REQUIRED候補 N-1**。委任_02(Coffee音声化)は新profile `n01`(明示CLI)で、どちらの解釈でも成立する。
4. **N01(Family Z)**: 差替点は`er063_family_z_audio_01.py` `FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_ADV/STD"]`(Zの現行は短い版PD8、Stdはさらに減速instruction連結)。Std/Advとも逐語N01(Std連結なし)・6%減速/減速後再検証は無変更。Family Z(Fiction)に対する「sharing a true story」の意味ズレ → **USER_DECISION_REQUIRED候補 N-2(文言は変更しない)**。
5. **Family Z**: 記事再生成・音声化STOPのため、Checklist 5/6(runtime発火・actual model_id)は**未確認として残す**設計(mock/dry-runのみ)。よってFamily Zは委任_02以降も`PRODUCTION_WIRED`にならない(設計上の帰結)。

## 0-1. STOP確認(開始時、旧記録は非適用)

- `docs/pm/delegation_log/*STOP_NOTICE*`: `2026-10-12_FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01_STOP_NOTICE.md`の1件のみ(2026-10-12、Melos run_e2e_01の旧記録、ローカルのみ)。
- `er026_output/family_z_production_e2e_01/`配下の`STOP`/`STOP_ALL`/`STOP_NOTICE`: **存在しない**(`melos/`ディレクトリのみ)。`.git/index.lock`なし。
- Family Zの記事再生成・音声化STOPは本委任でも厳守(コード・成果物の読取のみ。Melos run_e2e_02配下・Master Store・HR queue・attempt_history・telemetryへの書込なし)。

## A. M2P0 配線設計

### A-i. 現状のProduction KP経路(Family X)と挿入点

Family X正式runner = `er019_family_x_audio_production_runner_01.py`(stage: plan/scaffold/tts/assemble)。KP経路(ファイル:行、2026-10-13時点の実測):

| # | 位置 | 内容 |
|---|---|---|
| 1 | `er019_family_x_audio_production_runner_01.py:323-378` `run_theme_scaffold(..., kp_backend="db_hybrid")` | Family Xは`sc.run_key_phrases(..., kp_backend=kp_backend)`を呼ぶ(L368、既定"db_hybrid"。Family X以外[A/B/C/News/Z]はこの引数を渡さず既定"strategy_l") |
| 2 | `er003_v1_n3_01_scaffold_generate.py:677-` `run_key_phrases` | 外側ループ(Redundancy/Symbol QA NG時の選定やり直し、上限`KEY_PHRASE_REDUNDANCY_RETRY_MAX`)、`shortlist_cache`共有、記事単位`KP_ARTICLE_COST_CAP_JPY=15`(`er030_..._selector_01.py:79`) |
| 3 | 同`:293` `run_key_phrase_selection` → `:494` `_run_key_phrase_selection_db_hybrid_with_fallback` | `DbHybridFailure`時、`fallback_allowed`なら`_run_key_phrase_selection_strategy_l`(`:350`)へfallback、不可ならSTOP(fail-closed) |
| 4 | `er030_key_phrase_db_hybrid_selector_01.py:387` `run_db_hybrid_selection` | **M2の主挿入点**。L450-461: `core.run_stage1_and_shortlist(article_text, dbs, title)`→`s1r`(`shortlist_cache`に保存)。L494: `assign_candidate_ids`、L502: `correct_shortlist_source_span_consistency`、L508: `src_ref_contract.build_lightweight_user_message(title, shortlist_with_ids, sentence_reference, static_instructions, ...)`、L524付近: 既存`prod.run_production_selection_gate`(Source Reference Contract) |
| 5 | `er030_key_phrase_db_hybrid_core_01.py:431-` `run_stage1_and_shortlist(article_text, dbs, title, rare_word_lookup_budget=15, wiktionary_multiword_lookup_budget=60)` | 現行M0。2〜3-gram Wiktionary照会予算60(`DEFAULT_WIKTIONARY_MULTIWORD_LOOKUP_BUDGET`、L64)、cap15は`s1v2.build_shortlist`内 |
| 6 | `er030_key_phrase_db_hybrid_source_reference_contract_01.py:215` `build_lightweight_user_message(..., family_profile="family_x", display_type_fn=None, evidence_fn=None)` | **`evidence_fn`引数が既存**=候補行末尾の注釈(contains:/contained_in:/fragment_risk)はこの契約関数を**無変更**で付けられる(Trialもこの関数経由) |

Trial側M2の構成(移植元、すべてTrial専用でProductionから参照されていない):

| 機能 | 移植元(Trial) | 内容 |
|---|---|---|
| M1 照会予算拡大 | `er064_kp_opt_01_phase2_run_03.py:115 build_method1`、`er064_kp_opt_01_upstream_core.py:49 THREEGRAM_CAP=100,:214 make_order_fn("default")`、`:175 patched` | 予算=`n2+100`(n2=Stage1前プールの2-gram数)でWiktionary照会。Trialは`patched`でmonkeypatch+snapshot再生 |
| M1 precision guard | 同`:370 assemble_shortlist(demoted_allow=…)` | 現行の窓(予算60)外で新規に拾った「名詞句判定で外れたonline hit」はphraseへ入れない |
| M1 U2 | 同`:293 compute_containment(r2=True)`、`assemble_shortlist(u2="tierH+S")` | 包含ペア検出、Tier-H(完全包含された単語)を削除しbackfill |
| M1 U3 | 同`:329-352 FRAG_START/fragment_risk`、`u3_exclude/u3_annotate/r3` | 閉クラス語のみの句を除外、先頭が前置詞等の句に`fragment_risk`注釈 |
| (a) placeholder | `er064_kp_idiom_trial_01_matcher.py:27 build_pattern_index,:71 match_sentence_tokens,:96 placeholder_candidates` | one's/someone's等の見出しとの照合(本文token照合) |
| (b2) ルール所有格3-gram | 同`:145 rule_possessive_pattern_candidates` | 所有格代名詞+名詞等のルール候補 |
| (c) 予約枠 | `er064_kp_idiom_trial_01_pipeline.py:24 RESERVED_SLOT_CAP`(M2は`er064_kp_int_01_machine.py:26 RESERVED_CAP=3`)、`:62 reserved_sort_key`、`machine.py:109-157 build_pattern(M2)` | (a)+(b2)プールを(由来優先度,最小Zipf,canonical)で整列し先頭3件を候補末尾へ追加(cap15の**外側**)、追加LLM呼出なし。句読点をまたぐ3-gramは除外(本文に空白のみで連続実在=`contiguous`) |
| 候補行形式 | `upstream_core.py:458 candidate_row_text`、`machine.py:72 rows_for` | M2は`match:`を付けない(M3ではない)。注釈は`contains:`/`contained_in:`/`fragment_risk`のみ |

**移植方針(Checklist 3対応)**:

- 新Production module(提案名)`er030_key_phrase_db_hybrid_m2_supply_01.py`へ、上表の関数を**コピー移設**する(Trial moduleからのimportは不可。Trial fileは無変更のまま残し、Trial記録の再現性を保つ)。先例: `er030_key_phrase_db_hybrid_selector_01.py:122-136`の「Er028UtilByteParityTests」方式(Trial定義とProduction複製がbyte-for-byteで同一であることをsha256で固定)。
- 共有依存として許される既存資産: `er023_*`/`er027_*`/`er028_*`の`_stage1`接尾辞module(純粋関数の候補生成)、`er030_core_01`(同、selectorが既にimport済み)。`er064_kp_idiom_trial_01_matcher`は`er027_..._stage1`/`er028_..._stage1`のみimportする(Trial専用の実行設定を含まない純関数)が、ファイル名が`er064_kp_*_trial_*`でありTrial scriptと見なされるため**copy移設**する。
- 移設しないもの(Trial専用): `U.Snapshot`/`patched`(monkeypatch)/`make_order_fn`のu1系mode/`P.build_variant_shortlist`のV1-V3/(b1)LLM補助抽出/`match:`注釈(M3)。
- **monkeypatch不要**: `core.run_stage1_and_shortlist`は`wiktionary_multiword_lookup_budget`引数を既に持つ。ProductionではM1の予算拡大を「`wiktionary_multiword_lookup_budget = n2 + 100`を引数で渡す」だけで実現できる(core無変更)。n2は`core.run_stage1_for_article`(DB照合のみ、ネットワークなし)+純関数`s1v2.select_unmatched_ngram_candidates_for_lookup(sentences_tokens, existing, budget=10**7)`の2-gram数で算出できる(Trial `_pool_by_default`/`pool_for_article`と同型)。
- **`demoted_allow`(precision guard)の算出(設計上の最重要論点、Opus論点①)**: Trial M1は「現行窓(予算60)で照会した場合のonline multiword survivors」集合`_mw_survivors(cur["stage1"])`を使う。Productionは(A)現行60窓と拡大窓で**2回照会**(Wiktionary負荷・時間が約倍、不採用寄り)、(B)拡大1回の結果から**純関数`select_unmatched_ngram_candidates_for_lookup(..., budget=60)`で「先頭60候補」集合を求め、拡大結果のonline hitのうち先頭60候補に属するものを`demoted_allow`とする**(ネットワーク1回、core無変更)。(B)が(A)と同値であることは`gate_and_merge_multiword_hits`(hit間の併合・重複除去)の挙動に依存するため、**Trial snapshot(`er064_output/kp_extraction_selection_opt_01/phase1_a/wiktionary_snapshot_01.json`)を使った¥0オフライン回帰で9記事×Std/Advの`shortlists_r1.sha256.txt`と完全一致することを実装前提のGateにする**(不一致なら(A)へ切替=coreへ照会関数注入が必要になり「共有module変更」の扱いをOpusに確認)。
- 既存のTrial test(`er064_kp_int_01_test_01.py`ほか)は無変更で通し続ける(Trial fileは触らない)。

**挿入点の差分(擬似diff、Productionコードは本委任では変更しない)**:

```
er030_key_phrase_db_hybrid_selector_01.py  run_db_hybrid_selection(..., candidate_supply="m2")   # 既定をFamily Xの正式仕様=M2へ
  L450-461:  s1r = core.run_stage1_and_shortlist(...)                     # M0(現行)
         →   s1r = m2_supply.build_m2_stage1_and_shortlist(article_text, dbs, title)   # M2: 予算拡大+guard+U2+U3+(a)(b2)(c)
             # 戻り値は{"stage1","shortlist_info"(+"containment_pairs","m2_meta")}。shortlist_cacheへ同じ形で保存(retry時の再照会なし)
  L494-:     assign_candidate_ids/ correct_shortlist_source_span_consistency / build_lightweight_user_message は無変更
  L508:      evidence_fn = m2_supply.make_annotating_evidence_fn(pairs, ids)   # 既存引数に渡すだけ(契約関数は無変更)
```

- `candidate_supply="m0"`は回帰・切戻し用に残すが**自動fallbackには使わない**(新たなfallbackを独自に作らない)。M2構築で例外(Wiktionary 429枯渇等)が出た場合は、既存の`DbHybridFailure("SELECTOR_EXCEPTION", fallback_allowed=True)`→既存Strategy Lへfallback(`:494`)にそのまま乗る(L455-460の`except Exception`が既にstage1/shortlist構築失敗をこの経路へ変換)。→「M2失敗時にM0へ黙って落ちる」ことはしない(Opus論点②)。
- telemetry: 既存`_log_kp_backend_telemetry`のkeyに`kp_supply="m2"`、`reserved`(予約枠候補のcanonical/件数)、`overflow_beyond_cap`、`m2_lookup_seconds`、`wiktionary_api_calls`を追記(既存keyは変更しない)。`db_hybrid_stage1_debug.json`にもM2メタを保存(runtime evidence用)。

### A-ii. M1前提とWiktionary照会時間の影響

- M2はM1を**含む**(委任文どおり): 照会予算拡大(n2+100)・precision guard・U2包含整理・U3断片注釈。M2単独(予算60のまま)は成立しない(Trial定義: `M2=M1+(a)+(b2)+(c)`、`ROUND1_REPORT_01.md` §2)。
- 照会時間(Trial実測): M0 約10秒/記事(2call) → M1/M2 **約43秒/記事(8call、HTTP429待ち込み)**(`ROUND1_REPORT_01.md` §2表)。Coffeeは**Std・Advの2記事で約86秒**(各記事で独立に照会。retryループは`shortlist_cache`で再照会しない)。
- 既存の照会実装(`er023_key_phrase_db_ingest.py:141 wiktionary_multiword_targeted_lookup`): batch_size=50、バッチ間sleep=1.5秒、`urlopen(timeout=20)`、429時`Retry-After`/指数backoff(`max(wait, 2**retry_i)`)で**最大5回試行**、枯渇時は`HTTPError`をraise。→ coreを通じて`run_db_hybrid_selection`のL455`except Exception`で`DbHybridFailure(SELECTOR_EXCEPTION, fallback可)`へ変換され、既存Strategy L fallbackへ進む(**M2が発火せず黙ってStrategy L全文方式になる**リスク)。対策(設計): telemetryで`kp_backend_used`/`kp_supply`を必ず記録し、runtime evidenceの合格条件に「`kp_backend_used=="db_hybrid"`かつ`kp_supply=="m2"`」を含める(Strategy Lにfallbackした場合はM2発火不成立として扱い、`PRODUCTION_WIRED`根拠にしない)。timeout/retry値は**既存のまま変更しない**(新retry上限を作らない)。
- OPEN-337(Wiktionaryオフライン索引、未承認・未実装)は本配線に**含めない**。未実装のまま配線した場合の運用上の注意: (1)1記事1レベルあたり+約33秒(M0比)・429待ちの変動、(2)大量バッチ運転(同時多記事)でWiktionary公開APIのrate limitに触れやすい(既存`sleep_sec=1.5`・並列度は変更しない)、(3)SSOT上はOPEN-337を「M2P0配線後の運用課題」として残す(Trial既存追記を維持)。

### A-iii. 選定Prompt = P0 無変更の確認方法(実測sha)

P0 = Production現行(`extract_static_instructions(bk.load_prompt_template())` + `src_ref._FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`)。本委任で`PYTHONUTF8=1 .venv\Scripts\python.exe`により実測:

| 対象 | sha256 | 備考 |
|---|---|---|
| `er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt`(ファイルbyte) | `69d0e6ff548987896b561c0684e7aca10eae5b35a4974490fe92d42933d2e8f6` | `er003_b1_p2_keywords.py:39 PROMPT_TEMPLATE_PATH` |
| `selector.extract_static_instructions(template)`(1381文字) | `b8af4d50669fbd3e47de73f3b4f48e54226f293fa61697138397b190896d6025` | P0の静的instructions |
| `src_ref._FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE`(676文字) | `026aa7306afcde5cb8c4ee1f2b40928543909fe0fe4a371c4fe98affa5bcd08c` | P0のguidance |
| `er030_key_phrase_db_hybrid_source_reference_contract_01.py`(ファイルbyte、本委任時点) | `6602d784ee7e8e16a733e8f3b01848f9b83a3fdc365de6330ca8972bdfedfb41` | guidance定数を含むファイル |

- 確認方法(委任_02で新規test化): (1)上記3つの文字列sha(template file/static/guidance)をtest定数に固定、(2)M2配線後も`build_lightweight_user_message`が生成するメッセージの「static部」「guidance部」が(1)と一致、(3)M2で変わるのは候補行(【重要な単語…】〜【SENTENCE REFERENCE】)のみ(候補追加+注釈)で、Prompt文面(固定部)は不変。(4)`er064_kp_int_01_test_01.py`既存test(P0=Production逐語)が引き続きPASS。
- **Opus論点③(注意事項)**: M2P0のTrial(`er064_kp_int_01_machine.rows_for`)は、候補行末尾に`contains:`/`contained_in:`/`fragment_risk`注釈を付けるが、**P0はそれらラベルを説明しない**(説明するのはP1-P4のANNOT。`er064_kp_int_01_prompts.py`)。Trial結果(M2P0 71.3点/pump 6/6)はこの状態で得られたので、Productionも**同一(未説明注釈付き)で移植**する(説明文を足すとP0の改変=禁止)。この未説明ラベルがLLMに与える影響は、Trialの実測(M2P0最良)以外に追加検証しない。

### A-iv. canonicalization / Redundancy QA / retry上限との整合

| 項目 | 現状 | M2配線後 |
|---|---|---|
| 選定gate retry | `prod.MAX_PRODUCTION_RETRY_ATTEMPTS=2`(`er003_key_words_production.py:164`、初回+1回) | **無変更**。M2はgateの前(候補生成)のみ |
| canonicalization | `run_key_phrase_canonicalization`(`scaffold:589`)、Rule7等 | **無変更**。M2は`pump its fist`型(所有格)候補を増やすため、Rule7(OPEN-310: person表はits/my/our->one'sのみ許可、`my->someone's`はINVALID)に当たる確率が上がる。Trialでは`pumps its fist→pump one's fist`はOK(OPEN-310追記の¥0監査)。INVALIDは既存のretry/STOP経路で処理(上限回数も既存のまま) |
| Redundancy/Symbol QA retry | `KEY_PHRASE_REDUNDANCY_RETRY_MAX`(`scaffold:656`)、上限超過で`NG_REVIEW_REQUIRED`(自動採用しない) | **無変更**。retryでは`shortlist_cache`によりM2候補生成(Wiktionary照会)を再実行しない(同一article_text→同一shortlist。診断noteだけ変わる) |
| 記事単位コスト上限 | `KP_ARTICLE_COST_CAP_JPY=15`→超過でSTOP(fallbackしない) | **無変更**(M2はLLM呼出を増やさない。入力tokenが候補行+約91 tokens増、`ROUND1_REPORT_01.md` §2) |
| fallback | `DbHybridFailure`→Strategy L(`fallback_allowed`の場合)、`MODEL_CONTRACT_VIOLATION`/`KP_ARTICLE_COST_CAP_EXCEEDED`はSTOP | **無変更**。M2構築失敗は既存`SELECTOR_EXCEPTION`経路に乗る(§A-ii) |
| routing/model | `process="A2_SUPPORT"/"B1_SUPPORT"`→`routing.require_model(process, routing.SUPPORT_MODEL)`、`SUPPORT_MODEL="gpt-6-luna"`(`er006_model_routing_contract_01.py:50`) | **無変更**。runtime evidenceでactual model_idを確認(§D) |

### A-v. Family Z(M2P0)

- Zの`kp` stage: `er062_family_z_writer_01.py:931 run_kp_stage` → `scaffold.run_key_phrases(text, kp_dir, f"family_z_{slug}_{level}", src_level, process=process)`(**`kp_backend`未指定=既定`"strategy_l"`**)。`er026_family_z_fiction_production_runner_01.py`は`kp_backend`を一切参照しない(Grep確認)。
- つまりZは**本文全文をLLMへ送るStrategy L**(`_run_key_phrase_selection_strategy_l`、`prod.run_production_selection_gate`)で、**shortlist・候補行・予約枠が存在しない**。M2(候補供給の改善)を載せる土台がない。
- さらに`db_hybrid.run_db_hybrid_selection(family_profile="family_z")`は`src_ref_contract._check_family_profile_supported`(`er030_..._contract_01.py:60-72`、`SUPPORTED_FAMILY_PROFILES=("family_x",)`)で**`NotImplementedError`**。コメント上も「Family Z DB Hybrid Core v2全体の採用可否・Production配線は別途ユーザー/Fableが判断する」と明記。
- Z限定の暫定策(`er062:943-`の`run_kp_with_outer_retry`、OPEN-310の暫定回避)は共有module無改変で外側retryを持つ。M2との関係は未定。
- → **M2P0をFamily Zに適用するには「Family ZのKP選定方式をStrategy LからDB Hybridへ変更する」仕様変更が必要**であり、委任文STOP条件(M2がFamily Z KP経路に構造上載らない)に該当。**USER_DECISION_REQUIRED候補 Z-1**(選択肢: (Z-a)ZのKPは現行Strategy Lのまま「M2P0未適用」とユーザー承認の解釈を確認/(Z-b)Family Z DB Hybrid採用を別管理IDで設計[Z用guidance=新Promptが要るため本承認範囲外]/(Z-c)`family_profile="family_x"`でZへ流用[X向けguidance文言の適合性未確認、非推奨])。設計は継続するが、委任_02のZ側M2実装は**Fable/ユーザー判断まで着手しない**。
- Checklist 5/6(Family Z): KP再生成を伴う検証は記事再生成STOPに抵触するため**実施しない=未確認として残す**(推測・Trial結果で代替しない)。Z側は`PRODUCTION_WIRED`と判定しない。

### A-vi. Coffee記事のKP再生成計画(Family X、委任_02)

- 原稿: Coffeeは**2種類の原稿**が存在(OPEN-326)。v5試聴版=Tone Trial由来(Std `a3cc7bb9…`/Adv `d9b77190…`、`er019_output/coffee_prices/run_v5_ms_01`)、Production正本source_dir=`run_l3_01`(Std `6f5e8e53…`/Adv `5e8979dc…`)。**どちらの原稿でM2P0再生成・音声化するかは未決(OPEN-326)**。設計上の推奨: 試聴の連続性・M2P0 TrialがCoffee v5原稿(`pumps its fist`等のアンカー)で評価された点から**v5原稿(`run_v5_ms_01`)を維持**。判断が必要なら委任_02開始前にFableが確認(**USER_DECISION_REQUIRED候補 X-1**、ブロックではなく確認事項)。
- KPのみ再生成: `run_theme_scaffold`はPreview/Comment1-4(日本語)も再生成するため、そのまま使うと**承認済みStd R2音声の元テキストが変わる**。→ **KP単独stage**が必要。設計案: runnerへ**最小の`--scaffold-only kp`(または同等の内部引数)**を追加し、`run_theme_scaffold`のKPブロック(L350-370)だけを実行(`support`生成・Comment/Preview生成をskip)。既存の`--only-segments`(tts専用)と同様の最小CLI拡張で、新stageは作らない。Opus論点④: この追加が「新しい処理フロー」に当たるか。代替(K2)として、V5委任で行った「text bundle事前配置」型の手作業は**Production正式経路のevidenceにならない**ため非推奨。
- KP再生成後に必要な下流: (1)KP音声(Std/Adv各5件: 英語phrase・日本語gloss、Advは英語解説text再生成[`er019_family_x_kp_explanation_01.generate_kp_explanations`]+解説音声[P3 style])を**再生成**(KP項目が変わるため既存KP音声は流用不可)、(2)Full Story(Std/Adv各part1-3)をN01で再生成、(3)IN_ONE_LINE/Preview/Comment1-4/shell等は**再利用**(M2P0・N01の影響を受けない。Review Lockはtext shaで照合されるため同一text・同一styleの再利用は成立)、(4)組立(`stage_assemble_family_x_a2/b1b`)・Audio Validation Gate・QA・WPM・文末ポーズ実測・試聴ページ。
- 注意: Full StoryをN01で新out_dirに再生成する場合、`style_profile.json`の固定記録(M2: 既存run記録があるout_dirで新profileを記録できない)により**新out_dir(例: `run_v6_n01_01`)**が必要。再利用segmentは新out_dirへ明示コピー+sha一致確認(V5委任の手順を踏襲、`_generate_or_reuse`はsha一致で再利用)。

## B. N01 配線設計

### B-i. N01の正式文言(逐語、sha256で固定、改変禁止)

出典: `er057_output/coffee_tts_style_h_speed_04/round5/prompts_r5.json` `candidates.N01.style`(本委任で`d1956c91…`と一致を実測)。

```
A cheerful, kind storyteller sharing a true story at a pace a little slower than usual. Bring each sentence to its natural close, then go directly on to the next, including where the story takes a turn.
```

- sha256 = `d1956c91c925d197e27cf1204d7ed17248a96bef096b082fb1bd0846106a0477`(202文字・37語・2文)。数値WPM・速度倍率・unhurried/slowly・位置語を含まない(Trial側`contains_unhurried_slowly=false`,`has_numeric_wpm=false`)。
- Std/Adv共通に同一文言。Trial gen04はStdでN01**単体**をspeech_metadata.styleに渡し、生成後に6%減速(`er057_coffee_tts_style_h_speed_05_gen04.py`: `call(job["tts_input"], style, B.VOICE)`→Stdのみ`slowdown.apply_a2_slowdown`)。**減速instruction(`A2_SLOWER_PACE_INSTRUCTION`)の連結なし**。

### B-ii. 現行styleの所在と差替点(事実)

「現行P8」の実体はFamilyで異なる:

| 対象 | 現行style | 定数・行 | 備考 |
|---|---|---|---|
| Family X Full Story、**default** | `"calm, steady news narration with natural emphasis at key points and turns; not dramatic."` | `er033_tts_flash_lite_family_x_styles_01.py:46 FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]`。Stdは`runner _base_role_style_slower`(`er019_family_x_audio_production_runner_01.py:975-990`)で`+"\n"+A2_SLOWER_PACE_INSTRUCTION`を連結 | tts_backend=`speech_metadata_flash_lite`時のみ(それ以外はNone=既存挙動) |
| Family X Full Story、**Coffee限定profile** | **P8**(402文字、sha `3eadf4f6…`) | `er019_family_x_style_profile_01.py:49-54 P8_TEXT/P8_SHA256`、`:111-116 _FULL_STORY_OVERRIDE`(`std_append_slower_instruction=False`=Std逐語例外`COFFEE-P8-STD-VERBATIM-EXCEPTION-01`)、`:118-128 STYLE_PROFILES`(`coffee_p8`,`coffee_final_v5`)。runner `--style-profile`(L1986-1995)、解決`resolve_role_style`(`style_profile.py:152-`) | 新out_dir限定(M2)、`speech_metadata_flash_lite`必須(M5) |
| Family Z narrator Adv | **短い版PD8**(`"Warm, bright, cozy storytelling … never flat or sleepy."`、sha `329ff46a…`) | `er063_family_z_audio_01.py:103 _PD8`、`:153 FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_ADV"]`、`:133-147 _STYLE_SHA256/_STYLE_TEXT`、`:208 assert_style_table_integrity`(sha不一致=`FamilyZStyleIntegrityStop`) | 生成: `news_tail_fix.generate_news_narration_wide_margin(... style_prefix_override=style, tts_backend=TTS_BACKEND)`(`er063:551-558`) |
| Family Z narrator Std | PD8+`"\n"`+`A2_SLOWER_PACE_INSTRUCTION`(sha `74b456ca…`) | `er063:156 NARRATOR_FULL_STORY_STD`、`:147 PD8_A2SLOW` | 生成: `n3_tts.generate_a2_segment_with_slowdown(...)`(`er063:559-`、6%減速) |
| Family Z dialogue Adv/Std | style無し(既存`ENGLISH_STYLE_PREFIX`/`A2_ENGLISH_STYLE_PREFIX_SLOWER`) | `er063:160-166 DIALOGUE_ADV/STD`(`text=None`、`bvoices.generate_voice_body_wide_margin`) | **N01の対象外**(§B-iii) |
| 他role(Comment/Preview/KP EN/JA/KP解説/TOPIC_INTRO/JA title/IN_ONE_LINE/SHELL) | 各々の承認済みstyle(R2/K2/M2/E1/E2/P3等) | `er019_family_x_style_profile_01.py`、`er063:167-190` | **N01の対象外** |

**差替の設計**:

- **Family X(提案、UDR N-1の推奨案C)**: `er019_family_x_style_profile_01.py`に`N01_TEXT`/`N01_SHA256`/`N01_LENGTH`(`_verify_constants()`のループに追加=import時にsha/長さ/`assert_no_wpm_specification`検証)と新profile `PROFILE_N01="n01"`(FULL_STORYのみoverride、`std_append_slower_instruction=False`)および、Coffeeの承認済みR2/P3を維持する`PROFILE_COFFEE_FINAL_V5_N01`(`FULL_STORY=N01`+`SUPPORT_JA=R2`+`KP_EXPLANATION_EN=P3`、命名は実装時確定)を追加。`resolve_role_style`/runner/assembly gate(M3)は既存の単一解決関数を通るため**runner本体のstyle分岐は無変更**。既存`coffee_p8`/`coffee_final_v5`は後方互換(再現・Trial比較用)に**残す**(削除しない)。
- **Family X(案B: default切替)**: 全Family X記事のdefaultをN01にするには、`er033 FAMILY_X_ROLE_STYLE_EN["FULL_STORY"]`差替(B1B)+`_base_role_style_slower("FULL_STORY")`のStd逐語化(A2のスタイル連結をFULL_STORYのみ外す)が必要。影響: (1)`er033_tts_flash_lite_family_x_styles_01_test_01.py`(Trial02 E2とのbyte一致test)の期待値変更、(2)defaultが「バイト同一」前提の全回帰test、(3)resume時にstyle_profile.json無しの既存out_dirでstyleが途中で変わる混在リスク(M2が守っている問題)。**案Bは影響が大きくOpus条件A該当**。案Cで先に実装・実証し、default化は別判断を推奨。
- **Family Z**: `er063`の`_STYLE_SHA256`/`_STYLE_TEXT`に`"N01"`を追加(sha `d1956c91…`)、`FAMILY_Z_ROLE_STYLE["NARRATOR_FULL_STORY_ADV"]`を`style_label="N01"`/`text=_N01`、`["NARRATOR_FULL_STORY_STD"]`を`style_label="N01"`/`text=_N01`(連結なし、Trial gen04と同じ構成)へ。`assert_style_table_integrity`・原典照合(`:230-`)・`real_generators().narrator`(L551-558、`style_text_for(spec)`経由)は無変更で追従。`PD8`/`PD8_A2SLOW`定数は他roleから参照がなければ削除せず残す(要grep、Dangling防止)。**本委任ではコード変更なし、Z音声化もしない**(STOP厳守)。

### B-iii. 対象範囲の解釈(明記)

- 「メイン音声Prompt: N01」= **Full Story narration(Std/Advの本文part1-3)のみ**と解釈する(Trialもstd_part1/part2/part3・adv_part1-3のFull Story本文のみ)。対象外: Family Zのdialogue voices(別voice・別style)、Comment/Preview/KP読み上げ、IN_ONE_LINE、TOPIC_INTRO、japanese_title、shell。
- Family Zは「narrator」役のFull Story clip全てがN01対象(`role_for`が`NARRATOR_FULL_STORY_*`を返すkind)。短い帰属句narrator clip(`Melos said`型)も同じroleのため含まれる。→ 別管理IDの未承認`er069_*`(帰属clip分割改善)・`er065/er068`系とは**混ぜない**(本設計はstyle定数の差替のみ)。
- **別解釈が必要な場合はUSER_DECISION_REQUIRED**: (a)dialogue voicesにもN01を適用するか、(b)Comment/Previewにも適用するか。承認文言(「メイン音声Prompt」)とTrial範囲から対象外と読むのが自然だが、未確認ならユーザー確認(候補 N-3)。

### B-iv. 品質Gate・減速・retry/fallbackは無変更(経路ごとの確認)

詳細マトリクスは`PATH_MAP_01.md`。要点:

| 経路 | 現状(実測) | N01差替後 | 変更 |
|---|---|---|---|
| Std 初回生成 | `generate_a2_segment_with_slowdown`(`er003_v1_n3_01_tts_generate.py:283-`)→`generate_english_segment_with_fallback`(`er003_v1_crosslevel_audio_02_common.py:79-`)標準経路2回+fallback1回(`PRODUCTION_MAX_TTS_ATTEMPTS=3`)、`style_prefix_override`=Std style | styleだけN01 | **styleのみ** |
| Std 6%減速+再検証 | `apply_a2_slowdown_postprocess`(`:169-`): `a2_slowdown.apply_a2_slowdown`(6%、`er008_a2_postprocess_slowdown_01.py:32`)→`routing.transcribe`→`en_validator.classify_asr_match(segment_id=name)`、NG→STOPPED、`_post_slowdown_cascade_rescue`(`:117`、UNCERTAINのみ共有Cascade) | 無変更 | なし |
| Std 減速後NG時の取り直し | `generate_a2_segment_with_slowdown`外側ループ(`max_slowdown_attempts=3`)、通算TTS上限`PRODUCTION_MAX_TTS_ATTEMPTS=3`共有(OPEN-270、残予算0なら取り直さずSTOPPED) | 無変更 | なし |
| Adv 初回 | `news_tail_fix.generate_news_narration_wide_margin`(`er003_v1_sing01_news_tail_fix.py:61-`): `standard_style_prefix = style_prefix_override or p9a.ENGLISH_STYLE_PREFIX`(L128)、`max_attempts=PRODUCTION_MAX_TTS_ATTEMPTS`、ASR Gate | styleだけN01 | **styleのみ** |
| fallback take(Std/Adv共通) | **N01(や他のrole style)を使わない**: Std=`_run_a2_minimal_fallback_attempt`は`style_prefix_override`を渡さない(`crosslevel_audio_02_common.py:110-114`の仕様記述)。Adv=`repro01.generate_english_component_minimal_instruction(text,out_path,enable_pronunciation_resolver,tts_backend)`(`news_tail_fix.py:175-177`)、`speech_metadata_flash_lite`では`FAMILY_X_ROLE_STYLE_EN_FALLBACK[0]="natural, clear, conversational"`(`er019/er033`既存、`repro01.py:558-`) | 無変更(**fallback takeはN01ではない=既存仕様どおり**) | なし |
| ASR Gate/連結発音層/Repetition QA | `enable_connected_speech_equivalence_layer`/`enable_repetition_qa`(Full Story part1-3のみ) | 無変更(未承認のer065/er068系を混ぜない) | なし |
| regeneration(Local Rewrite等) | 既存`_local_rewrite_recovery_for_english_segment_with_fallback` | 無変更 | なし |

### B-v. Trial(gen04)とProductionの一致確認

| 項目 | Trial gen04 | Production(Family X、`speech_metadata_flash_lite`) | 一致 |
|---|---|---|---|
| モデル | `gemini-3.8-flash-lite-tts`(`er057_tone_trial_final_build_03.py:30 MODEL`、`rc.require_model(FAMILY_X_FLASH_LITE_TTS_PROCESS, MODEL)`) | 同(`er006_model_routing_contract_01.py:119 "FAMILY_X_FLASH_LITE_TTS": "gemini-3.8-flash-lite-tts"`) | 一致(runtime evidenceで`model_version`確認) |
| voice | `Aoede`(`:31`) | Family X/Z narratorはAoede(`er063:153`、Family X runner既定) | 一致 |
| 呼出方式 | `types.SpeechMetadata(style=style)`をPartに付与(`:92-` call関数)、`response_modalities=["AUDIO"]` | `speech_metadata_flash_lite` backend(`er033/er019`の既存) | 同方式(Productionの実装関数経由で確認) |
| Std減速 | 生成後`apply_a2_slowdown`(6%) | `generate_a2_segment_with_slowdown`内で同関数 | 一致 |
| ASR | `gpt-4o-mini-transcribe`+`classify_asr_match`系(Trial版`asr_and_judge`) | Production ASR routing(`routing.transcribe`)+EN ASR Semantic Equivalence Validator | **Trialは簡易再現(Production Gateと完全同一ではない)**。Productionでは本物のGateが判定(緩和なし) |
| 実行モード | `STANDARD(sync, DEV Trial)` | **`TTS_EXECUTION_MODE=STANDARD`を明示**(T-2) | 一致させる |

### B-vi. Trial知見の注記(仕様変更なし)

委任文記載: N01 Std減速後WPM中央値≈148、生成破綻2/92はASR Gateで捕捉(本委任では再検証していない=委任文の転記)。これは品質Gateの**緩和根拠ではない**(`PATH_MAP`のとおりGate・閾値・retry上限は無変更)。

### B-vii. Family Zへの「sharing a true story」(USER_DECISION_REQUIRED候補 N-2)

N01は"sharing a true story"を含む。Family Z(Fiction)は創作物語のため意味上のズレがありうる。**文言は変更しない**(N01以外への変更禁止、委任文)。ユーザー確認事項: (a)Zでもそのまま逐語N01を使う(ズレを許容)、(b)Z用の文言差分(=新Prompt、別Trial・別承認が必要)。Fable/ユーザー判断までZ側N01の実装は着手しない(コード変更も音声化もSTOP)。

## C. 回帰・テスト計画(要約。詳細は`TEST_PLAN_01.md`)

- 既存回帰(実行コマンド・件数は`TEST_PLAN_01.md`)+新規test: (1)M2 module byte parity/決定論test(Trial moduleとの関数出力一致、Trial snapshotで`shortlists_r1.sha256.txt`一致)、(2)P0無変更sha test(§A-iii)、(3)N01 sha test(X/Z定数、profile定義、`_verify_constants`)、(4)Family X経路: `candidate_supply="m2"`が既定でdb_hybridに乗る/Strategy L fallback時は`kp_supply`未設定でM2発火不成立と記録されるmock test、(5)Family Z mock test: narrator roleのstyleがN01・dialogue/他roleが不変、`kp_backend`が`strategy_l`のまま(Z-1未決の間はZ KPを変更しない)ことのguard test。
- Trial専用fileの無変更確認(`git diff --stat`でer064_*/er057_*無変更)と、Production→Trial importゼロのDangling Reference test。

## D. runtime evidence計画(要約。詳細は`EVIDENCE_PLAN_01.md`)

- Family X(Coffee、`production_formal_path`/`fresh`): KP M2P0再生成(`kp_backend_used`/`kp_supply`/候補数/予約枠/`model_id`=`gpt-6-luna`/Wiktionary秒・call数/Redundancy・Canonicalization結果)→KP音声→Full Story Std/Adv N01音声(style sha・`model_version`・Std減速後再検証・ASR Gate・WPM・文末ポーズ)→試聴ページ(GitHub Pages `user_test/`+Playwright実再生)。
- Family Z: mock/dry-run(課金なし・生成なし)のみ。Checklist 5/6は**未確認として残す**。

## E. 費用見積(要約。出典・内訳は`COST_ESTIMATE_01.md`)

Coffee 1記事(Std+Adv)のKP再生成+KP音声+Full Story N01音声+ASRで**期待約JPY21〜27、最悪(retry上限)で約JPY57**(上限提案JPY80、`--budget-jpy 80`)。未確認単価(KP短clip単価、Azure Secondary)は「未確認」と明記。

## F. Dangling Reference / SSOT計画

- Dangling Reference(委任_02完了時に確認): (1)新module `er030_key_phrase_db_hybrid_m2_supply_01.py`がTrial `er064_*`をimportしない、(2)`er019_family_x_style_profile_01.py`/`er063`がTrial `er057_*`をruntime importしない(既存方針: Trialファイルへruntime依存なし)、(3)`coffee_p8`/`coffee_final_v5`/`PD8`定数を残す場合はその旨をCURRENT_SPECに明記(参照元がある限り削除しない)。
- CURRENT_SPEC更新箇所(委任_02、配線完了後のみ): KP仕様節 `CURRENT_SPEC.md:1847-1851`(DB Hybrid/Source Reference Contract/4+1構成/修正1回目の記述群。M2P0を「Family X候補供給=M2P0」として追記)、TTS style節 `:2619-2622`(P8/V5記述。N01 profile・default方針[N-1]を追記)、Family Z styleは`er063`関連節(該当行は委任_02で再Grep)。「本文全文をLLMへ送らない」原則(L1847付近)はM2(b1なし)では**影響なし**(M2は(b1) LLM補助抽出を含まない)。
- DECISION_LOG: ユーザー正式決定(2026-10-13、M2P0・N01の`APPROVED_FOR_PRODUCTION`、Family別実行範囲)の原文要旨。
- OPEN更新: OPEN-325(M2P0採用部分=(a)+(b2)+(c)をAPPROVEDとして更新、(b1)は未採用のまま)、OPEN-336(Pkg U1-U4=M1がM2に含まれて採用された点を更新、Pkg P/E/R/Xは未採用)、OPEN-337(M2P0配線後の運用課題として維持、未承認・未実装)、OPEN-310(Rule7: M2で所有格候補が増えるためINVALID頻度の監視、根本対応は未実施)、OPEN-332(N01で文末ポーズ関連の位置づけ更新。N01採用はPrompt側緩和案Cに近いが、案A/Bは未実装のまま)。
- USER_DECISION_REGISTER(`docs/pm/USER_DECISION_REGISTER_01.md`)更新: M2P0・N01のユーザー決定行、Z-1/N-1/N-2/X-1のUDR行。
- Status遷移の記録: Trial `VALIDATED` → `APPROVED_FOR_PRODUCTION`(2026-10-13ユーザー) → `PRODUCTION_WIRED`(Family X: Checklist全充足後のみ。Family Z: 未確認項目が残るため付与しない)。

## G. Opusに問う論点(5件)

1. **`demoted_allow`の算出方式**(§A-i): 拡大1回+純関数で先頭60候補を特定する方式(B)で、Trial M1と決定論的に同値と言えるか。(B)がsnapshot回帰で不一致の場合、coreへ照会関数を注入する(=共有module変更)か、2回照会(A)か。
2. **M2構築失敗時の挙動**: 既存`SELECTOR_EXCEPTION`→Strategy L fallbackにそのまま乗せる設計でよいか(M2が黙って不発火になる点は、telemetry+evidence合格条件で検知)。M0へのfallbackを追加する案は「新たなfallback=新仕様」として却下してよいか。
3. **P0の未説明注釈**(§A-iii): M2P0を「注釈(contains:/contained_in:/fragment_risk)はP0に説明なし」のまま移植する判断の妥当性(Trialでの最良結果に準拠、P0改変禁止)。
4. **KP単独再生成の経路**(§A-vi): runnerへ`--scaffold-only kp`相当の最小引数を追加してよいか(新stageではなく既存scaffoldのsub-select)。それとも別構造が望ましいか。
5. **N01のFamily X適用範囲**(§B-ii): 案C(profile追加+明示CLI、defaultは別判断)と案B(default切替)の技術的リスク比較、および「Std逐語例外」(減速instruction非連結)を新profileでも踏襲することの妥当性。

## H. USER_DECISION_REQUIRED候補(Fable経由でユーザーへ)

| ID | 内容 | 設計上の暫定扱い | 実装をブロックするか |
|---|---|---|---|
| **Z-1** | M2P0のFamily Zへの適用: ZのKPはStrategy L(shortlistなし)で、`family_profile="family_z"`は`NotImplementedError`。適用=Family ZへのDB Hybrid採用という別仕様変更(§A-v) | Z側M2は未着手。Z KPは無変更 | Z側M2のみブロック(Family X・N01は進められる) |
| **N-1** | N01の適用範囲: (C)新profile+明示CLI(Coffee等で使用)/(B)Family X全記事のdefault化(§B-ii)。「現行P8」はCoffee限定profileにしか存在しない | 委任_02はC(新profile、新out_dir)で実装・Coffee実証 | default化(B)のみ別判断待ち |
| **N-2** | Family Zへのsharing a true story文言(Fiction)。文言は変更しない(§B-vii) | Z側N01は未着手 | Z側N01のみブロック |
| **N-3** | N01の対象をFull Story narrationのみと解釈(Z dialogue voices/Comment/Preview/KPは対象外)(§B-iii) | 左記の解釈で設計 | 解釈確認(ブロックではない) |
| **X-1** | Coffeeの原稿正本(OPEN-326): v5原稿とProduction正本`run_l3_01`のどちらでM2P0・N01を再生成するか | v5原稿(`run_v5_ms_01`)維持を推奨 | 委任_02着手前に確認推奨(ブロックではない) |
| **X-2** | Coffee再生成が「Family Xの音声化まで」に含まれるか(原稿・Preview/Comment再利用の可否) | KP+Full Storyのみ再生成、他は再利用 | 確認事項 |
