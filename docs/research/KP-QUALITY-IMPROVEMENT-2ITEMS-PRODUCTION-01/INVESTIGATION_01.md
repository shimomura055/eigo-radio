# INVESTIGATION_01(KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_01、2026-10-22。調査のみ・API 0・費用0・Production既存ファイル編集0)

確認済み=実コード読取/実行の観測値、推測=近似を含む見積。再現script=`er108_kp_noguard_reeval_01.py`(結果`noguard_reeval_01.json`)、`er108_kp_cmu_census_01.py`(`cmu_census_01.json`)、`er108_kp_guard_exposure_01.py`(`guard_exposure_01.json`)。

## 1. 項目①: 数値・否定保護がKP英語の投票に効く全箇所(file:行)

### 1-1 判定の流れ(生成時)
`generate_narration_snippet_verified_strict(vote_pass_required=True)`(er003_v1_repro01_main_generate.py:271,374) -> `er006_secondary_asr_01.evaluate_attempt_with_cascade_detail`(attempt_ctx.vote_required。:1130-1155でwhisper_fn設定) -> `er078_asr_unified_judge_01.unified_judge`(ctx.vote_required) -> 票集計`finish_vote`(:551) -> `kp3v.whisper_needed`(:560)/`kp3v.tally`(:567)。

### 1-2 保護が票・結論に効く箇所(解除対象の全数。Grep `_protected(` / `protected_diff` / `NG_PROTECTED`)
| # | 箇所 | 現行の効き方 | ①での扱い |
|---|---|---|---|
| G1 | er078:428 `pvg,pneg=_protected(canon,gate_text)` + :452-453 最終ANDゲート | Primary PASSでも値DIFF/否定差なら`NG_PROTECTED`で確定(Secondary/Whisper不呼出)。**vote_requiredでも適用される** | **解除**(vote時はskip、観測値のみ監査) |
| G2 | er078:472-481 P1(Primary NG時の値DIFF/否定差/`protected_diff`) | `NG_PROTECTED`で即確定(Secondary不呼出) | **解除**(vote時はP3=Secondary呼出へ進む) |
| G3 | er078:589-592 `if svg.kind==DIFF or sneg` -> `finish_vote(False,..,s_pdiff=True)` | Secondary転写の保護差でS票を強制NG+`protected_diff=True` | **解除**(S票は許容集合判定[:600付近]だけで決める) |
| G4 | er104:264 `make_voter`: `passed = ok and not pdiff and not rescued`、`protected_diff=pdiff` | Whisper票もPASS票にならない | **解除**(passed=ok and not rescued) |
| G5 | er104:141 `whisper_needed`: Primary.protected_diffならFalse、:146 dissent側protected_diffならFalse(P-07解釈(b)) | 割れてもWhisperを呼ばない | **解除** |
| G6 | er104:161-162 `tally`: Primary.protected_diff -> `NG_PROTECTED`(S/W呼ばず) | 同上 | **撤去** |
| G7 | er104:170-171 `tally`: dissent側protected_diff -> `NG_PROTECTED_DISSENT` | 2/3でも不成立 | **撤去**(これがcoffee `pump one's fist`のHR原因) |
| G8 | er104:213 `decide`: Primary.protected_diffならS/W呼ばず終了 | 同上 | **解除** |
| G9 | **再利用点の事前guard** `er078_reuse_value_guard_01.guard_entry`(:32-)。呼出: er006_master_audio_store_01.py:126-130(Store)、er019_family_x_audio_production_runner_01.py:648-653/:699/:752(前回results)、er019_family_x_validation_inheritance_01.py:204-205(引継ぎ)、er063_family_z_audio_01.py:729-730(Z)。いずれも **KP voteのreuse gate(`kp_vote_reuse_ok`)より前**に実行され、保存Primary転写をJ11 rejudge(`rejudge_with_current_judge`)へ通し、値DIFF/否定差(`PROTECTED_REASON_PREFIXES`:23-26)なら`blocked=True`で再生成へ回す | 保存済みKP英語音声の再利用が、保護差を理由に**voteの手前で**止まる(=保護解除の漏れ箇所) | **KP英語のときだけskip**(label/style idで判定。`reuse_blocked`明示markは維持)。**Fableの前提整理に無かった箇所(追加提案)** |

**非KP(維持)**: unified_judgeの上記G1-G3は`vote is None`のときは従来どおり(KP以外の全音声)。`er078_asr_unified_judge_01.NG_PROTECTED`状態自体は非KPで使用継続=撤去しない。撤去するのはKP投票側の`kp3v.NG_PROTECTED`/`NG_PROTECTED_DISSENT`と`protected_dissent_blocks`引数のみ。

### 1-3 呼出点(X/Z)
KP英語の生成/再利用6点(KP3V設計): X (1)前回results `er019_family_x_audio_production_runner_01.py:752-770`、(2)引継ぎ `:735-744`(`validation_inheritance.try_inherit_from_cached`、API 0=allow_s1=False)、(3)(4)Store key A/B `er019_family_x_kp_en_k2_store_01.py:62,83,86,116`、(5)X default `+vote1` key `:1106-1107`(`ensure_key_phrase_english_component_x_vote`)、Z (6)`er063_family_z_audio_01.py:722-745`、生成 `:859,876`。いずれも判定は共通のunified_judge(vote_required)へ集約=**judge/er104の修正1箇所でX/Z両方へ効く**(Family別分岐なし)。Whisper preflight/circuitは`er104_kp_vote_reuse_01.guard_whisper`(X :730, Z :722)。

### 1-4 Store再利用時の再判定(既存仕様の確認)
`er104_kp_vote_reuse_01.kp_vote_reuse_ok`(:150-)は保存Primary/Secondary転写(+保存Whisper転写[同sha]があればそれ)を本番adapter(`evaluate_vote` :109-)へ渡して再判定し、割れればローカルWhisper(API 0)を保存音声へ実行する(`whisper_text=None`のとき`kp3v.whisper_vote`既定)。つまり**G1-G8を直せばStore再利用の再判定は追加実装なしで新規則になる**(G9のみ別途)。Store entry `+vote1`はPASSのみ保存=旧規則PASS集合は新規則PASS集合に包含される(単調: 保護解除は票を減らさない)ので、key bump不要・既存保存音声の一括再生成不要。

### 1-5 HR Lock・retry・resume
HR Lock(OPEN-371)はmodule不変。KPのNGは通常の再生成(slot消費)・上限(KEY_PHRASE_TOTAL_MAX_ATTEMPTS)到達でSTOPPED->HR Lock。①でNG減(保護差だけで止まっていた正常音声の偽NGが消える)ため、HR到達は減る方向(増える経路なし。両NGは従来どおりNG)。Whisper技術障害は`NG_WHISPER_UNAVAILABLE`=技術STOP(HRへ送らない)を維持。

## 2. 項目①の保存データ検証(API 0・本番adapter経路・保護解除を`uj._protected`差替で模擬)
`er108_kp_noguard_reeval_01.py`: baseline=現行 / A=値DIFF・否定差を解除(AMBIGUOUS維持=推奨) / B=値ガード・否定ガード全解除。対象=保存84件(KP3V trial corpus)+NG3 12本(coffee 8+small_bag 4)。Azure実呼出0を機械確認(`azure_real_calls_total=0`)。

| 対象 | 件数 | baseline PASS | A PASS | B PASS | 判定変化 |
|---|---|---|---|---|---|
| 保存84件(問題音声21件を含む。うちtake part問題13、他8) | 84 | 60 | 60 | 60 | **0件(偽PASS増加0。問題音声21件は全件NGのまま)** |
| NG3 coffee `pump one's fist` 8本(a2 N1/b1b N2 x4attempt) | 8 | 0 | 2 | 2 | N1#1(`Pump one's fist.`/Azure `Pump 1's fist.`)とN2#4(最終wav)が `NG_PROTECTED_DISSENT` -> `PASS_VOTE_2OF3`(行P+W、Whisper転写`Pump One's Fist`)。残り6本はPrimaryも`Pump one fist.`等でNG=P/S両NG=NG(真理値表どおり) |
| NG3 small_bag `novelty minaudière` 4本 | 4 | 0 | 0 | 0 | 全本P/S両NG(`Novelty Manoir`/`Novelty Menottiere.`等)で変化なし(項目②でも選定段で除外される) |

重要所見(Fableへ): (a)coffee **b1bの最終HR wav(N2#4)はPASSに変わる=HR原因が解消**。(b)**a2の最終wav(N1#4)はPrimaryが`Pump one fist.`(`'s`落ち)でNG、Azureも`1's`でNG=両NGのためユーザー真理値表どおりNGのまま**(local Whisperは同wavを`one's`と聞く可能性があるが、両NGではWhisperを呼ばない仕様。FableがEVIDENCE_01で記録した「local Whisper 8本中7本PASS」は『Whisperだけで見た場合』であり、ユーザー表の判定とは別)。(c)N2#1はS転写が`Pump 1's.`(fist欠落)で、Whisperも`Pump Ones Fest`でNG=正しくNG。

### 偽PASS露出の見積(`er108_kp_guard_exposure_01.py`、API 0)
保存distinct KP 656句から、数詞置換(8)・数字置換(1)・否定語脱落(21)・否定語付加(635)=計665の合成誤転写を作り、保護解除後に票を決める分類器(`classify_asr_match`+同音救済)に通した: **分類器が単独でPASSさせたものは0/665**(旧来のguardが止めていたのは665/665だが、分類器単独でも全て不合格)。数値を含むKPは11句、否定語を含むKPは21句=露出面自体が小さい。結論(確認済み): 保護解除で偽PASSが増えるのは「分類器が数値/否定の違いを許容する経路」(同音救済・正規化一致)だけで、保存データ・合成で観測0。

## 3. 項目②: KPテキストが確定する箇所と検査挿入点
選定(er105)-> canonicalization -> gloss再整合 -> Redundancy QA -> TTS plan。
| 段 | 確定内容 | 場所 | CMU検査 |
|---|---|---|---|
| 選定 | LLM(Luna)が本文中の語句を選ぶ。`source_span`=原文スライス | `er105_kp_fulltext_selector_01.validate_and_resolve`(:236-)。機械検証(本文一致・語数・件数・重複・旧形式precheck`_legacy_form_reasons`:223) | **挿入点M1**: item別`r.extend(...)`に`er108.reasons_for_phrase(phrase)`。note文は既存`build_machine_note`(:343)が`「phrase」: reasons`形式で載せる(Prompt 2本文不変) |
| canonicalization | 基本形化・人称一般化後の`used_form`(=TTS対象) | `er003_key_words_canonicalization.merge_canonicalization_result`(:773-。`used_form`=canon["key_phrase"] :807) | **挿入点M2**: X/Z共通の`er003_v1_n3_01_scaffold_generate.run_kp_with_outer_retry`(:666-)のcanonicalization PASS直後(:714付近、`merged_items`確定後・Redundancy QA前)に`canonicalized_check(canon["merged"]["items"])`。不適合=canonicalization INVALIDと同じ扱い(failures加算・artifacts退避・次周へ) |
| gloss再整合 | 日本語glossのみ(英語KPは不変) | `er003_v1_n3_01_scaffold_generate.run_key_phrase_canonicalization`(:476-) | 不要(英語不変) |
| TTS入力 | `n3_tts.tts_safe_kp_en(used_form)`=`tts_safe_en`+ハイフン->空白+複合語分割(`er003_v1_n3_01_tts_generate.py:1012-1016`) | X `er019...runner:1103`, Z `er063:535` | M2で`used_form`を検査すれば、TTS入力は`used_form`の機械的変形(ハイフン分割は語単位照合と整合)。追加検査は不要 |

**挿入が1段(M1)だけだと不十分な理由**: 基本形化は語を変える(`pushed prices up`->`push prices up`)。ただし実測では、保存全2,130 item中、canonicalizationが「source/display側は登録語なのに`used_form`が未登録」にした例は **0件**(`t2`集計)。M2は防御(保証の最終関門)として1箇所追加する価値はあるが、発火頻度は極小の見込み(推測)。**shortfallの扱い**: M1は最終attemptで除外->shortfall。M2は後段のため除外でなくINVALID(外側retry)。

A/B/C(Strategy L/`_run_key_phrases_impl`)は`run_kp_with_outer_retry`を通らず、`validate_and_resolve`も使わない=**M1/M2はX/Z(fulltext_p2)のみに効き、A/B/C無影響**(27-7整合)。

## 4. CMU辞書の実体
- 本番が使う辞書: `pronouncing`(0.3.0)の`phones_for_word`/`pronunciations`。Production使用箇所: `er006_m1_multi_candidate_01.py:69-70`、`er008_asr_variant_hardening_15_homophone_en.py:33,61`、`er011_connected_speech_equivalence_layer_production_01.py:37,74`。
- 実体: `pronouncing`は`cmudict`(1.1.3)のデータを読む。path=`C:\Users\tensh\eigo-radio\.venv\Lib\site-packages\cmudict\data\`、登録エントリ **135,166**(`pronouncing.init_cmu()`後の`len(pronunciations)`)。`er108.lexicon_info()`で取得可能。
- 実測照合: `one's`=登録(W AH1 N Z)、`someone's`・`don't`・`o'clock`・`well-being`・`state-of-the-art`・`u.s.`・`mr.`・`players'`・`'bout`=登録、`minaudière`=未登録、`covid`/`ll`/`n't`=未登録。

## 5. 保存KPのCMU未登録率(`er108_kp_cmu_census_01.py`、`cmu_census_01.json`)
| 母集団 | 句数 | 未登録語を含む句 | 率 | distinct未登録語 |
|---|---|---|---|---|
| A: 保存KP英語segment(lock state列挙、canonical解決分) | 554 | 16 | **2.9%** | 15 |
| B: 全`keywords_canonicalized.json`のdistinct used_form | 656 | 23 | 3.5% | 23 |
| 参考: fulltext_p2由来item(`fulltext_source_ref`付き) | 69 | 2 | 2.9% | -- |

未登録語の型(A、語数ベース): plain OOV(新語・複合語・専門語)9(`pushback` `biofilm` `grogginess` `timekeeper` `cytokine` `concierges` `misconfigured` `counterspace` `conscientiousness`)、固有名詞1(`Houthi`)、アクセント2(`résumé` `minaudière`)、数字2(`2` `30`=既存precheckの数値placeholder規則でもselection段で拒否済み)、テスト合成語(`Xzqwtrlk`)。**誤除外になりうる型**(人手判断): (a)語形変化で未登録だが原形は登録(`concierges`)、(b)複合語が1語で未登録(`pushback` `timekeeper` `counterspace`)、(c)アクセント付き外来語(`résumé`)、(d)固有名詞(`Houthi`)。これらはCMUに無い語=ユーザー要件どおり「選定不可」(綴り正規化・語形救済・外部辞書は禁止)。大文字小文字・句読点・アポストロフィ・ハイフン・ピリオド略語(`u.s.`)・`someone's`で誤除外された語は **0**(正規化経路集計: whole 1425 / whole_stripped 3 / hyphen_parts 2 / FAIL 16)。
推測(低確度): 3件選定で少なくとも1件が未登録になる確率は約8%(1-(1-0.029)^3)=最終attemptまで同じ語を選び続けない限り、retry 1回で解消するのが通常。追加Luna呼出の期待値は約0.08回/レベル(約0.2円)。

## 6. retry/fallback/resumeとの関係(確認結果)
- er105内retry: `MAX_ATTEMPTS=2`(旧Strategy Lと同じ。独自増減しない)。X/Z外側retry: `run_kp_with_outer_retry`の`failures>=max_outer(3)`とRedundancy再選定の`KEY_PHRASE_REDUNDANCY_RETRY_MAX`は別カウント、各周でSTOPセンチネル確認。CMU失敗はこの既存機構に載せ、**回数上限・STOP確認は変更しない**。
- resume: X TTS段はディスク上の`keywords_canonicalized.json`をloadして使う(er019 runner :933,:1340。無ければKP生成のみスキップ)。scaffold段(`run_theme_scaffold` -> `run_key_phrases`、er003_v1_n3_01_scaffold_generate.py:1004)の再実行時に選定が再走するかはstage単位の再開条件に依存し、本調査では未確認(委任_02で確認する)。過去runの未登録語KP(coffee等)は「今回の変更だけを理由とする一括再生成は不要」(ユーザー原文§4)に従い遡及しない=新規選定/再選定からだけ適用。
