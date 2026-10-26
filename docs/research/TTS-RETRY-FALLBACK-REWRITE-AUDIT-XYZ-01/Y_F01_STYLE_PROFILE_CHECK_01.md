# Y_F01_STYLE_PROFILE_CHECK_01 — Family Y runnerのStyle profile `default` 固定(Y-F01)の事実確認

管理ID: TTS-RETRY-FALLBACK-REWRITE-AUDIT-XYZ-01 委任_02 / 2026-10-26 / read-only(API 0・JPY0・コード/SSOT/run dir編集0)。到達上限Status=調査完了(AUDITED)。是正は行わない。
対象HEAD: 読取開始時 `31c41ea76`・終了時 `2dbc3841e`(作業ツリー読取。`er121_family_y_runner_01.py`・`er121_family_y_audio_01.py`・`er019_family_x_style_profile_01.py` は `git status --porcelain` で未変更を確認)。
表記: 表のセルは事実(ファイル:行)のみ。技術的見解は「8. 所見(事実ではない)」へ分離。根拠が見つからないものは「記録なし」と書く。

## 0. 結論(先に・3択の事実)

| 問い | 事実 | 根拠 |
|---|---|---|
| Yは承認上 `fx_20261017` 継承が仕様か | **設計・台帳・DEV Trialでは「継承」と明記**。ユーザー原文は個別のStyle名(PD06等)を名指しした承認ではなく、「他Familyで`APPROVED_FOR_PRODUCTION`の共通仕様はYも適用対象」「既存の正式な速度・Style・TTS設定を継承」という一般規定(§3) | `DESIGN_01.md:84`、`SPEC_LEDGER_03.md:60`(YL-A01=APPLY)、`er110_family_y_audio_trial_01.py:40`、ユーザー原文 `2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md:162-166`・`…USER_02.md:70-80`・`2026-10-25_FAMILY-Y-VOICES-DESIGN-01_USER_09.md:64` |
| `default` 固定が承認済みか | **承認記録なし** | §3の全Grep(設計・台帳・DECISION_LOG・OPEN_ITEMS・CURRENT_SPEC・UDR・コミットメッセージ・ユーザー原文)で `STYLE_PROFILE="default"` を承認/除外した記述は0件 |
| 意図的除外の記録はあるか | **記録なし** | 同上。`er121_family_y_runner_01.py:37` の定義行にも理由コメントなし。導入コミット `7d5b9f8fc`(委任_02B)の本文にも言及なし |

→ 事実としては「Yの設計・台帳・DEV Trialは`fx_20261017`継承。Production runnerだけが`default`で、その理由・承認・除外の記録はいずれも無い」。実際に送信されたStyleは基底(base)の旧6-role Styleで、`fx_20261017`のPD06/S3/E1/K2/P8-KP/P7はY runでは1つも使われていない(§4)。
分類(11-8)の提案: **B(承認済み仕様との不一致の疑い)・重要度=高**。ただしユーザーが個別のStyle名でYへ承認した原文は見つからないため、「B確定」か「Yを`default`のままにする意図的判断」かはFable/ユーザー確認事項(推奨: 修正へ進む前に確認。§7)。

## 1. (a) コード: `STYLE_PROFILE` の定義と、TTS生成への渡り方

| # | 事実 | ファイル:行 |
|---|---|---|
| 1 | 定義: `STYLE_PROFILE = "default"`(コメントなし)。直前行は `TTS_CLIP_EST_JPY = 1.0` | `er121_family_y_runner_01.py:37` |
| 2 | TTS生成へ渡す(b1b): `ya.generate_y_b1_segments(ctx.out_dir, style_profile=STYLE_PROFILE, guard=guard)` | `er121_family_y_runner_01.py:988` |
| 3 | 同(a2): `ya.generate_y_a2_segments(…, style_profile=STYLE_PROFILE, guard=guard)` | `er121_family_y_runner_01.py:990` |
| 4 | gate/assemble にも同値を渡す: `ya.y_style_gate(ctx.out_dir, lv, STYLE_PROFILE)`、`ya.assemble_level(…, style_profile=STYLE_PROFILE, …)` | `er121_family_y_runner_01.py:1016` / `:1034` |
| 5 | `tts` stageの入力sha(stale判定)に `STYLE_PROFILE` を含む。値を変えると `_tts_input_sha` が変わる | `er121_family_y_runner_01.py:960-967`(`ya.TTS_BACKEND, STYLE_PROFILE`) |
| 6 | 関数側の既定値も `"default"`: `generate_y_b1_segments(…, style_profile: str = "default", …)` / `generate_y_a2_segments(…, style_profile: str = "default", …)` | `er121_family_y_audio_01.py:429` / `:516` |
| 7 | Styleの解決: `_style_resolvers` が `style_profile_mod.resolve_role_style(style_profile, role, level, _base)` を呼ぶ。`_base` は `er033_tts_flash_lite_family_x_styles_01.FAMILY_X_ROLE_STYLE_EN.get(role)`(旧6-role基底Style。flash-liteのみ) | `er121_family_y_audio_01.py:239-249` |
| 8 | `default` の定義は `{"overrides": {}}`(override無し)。`resolve_role_style` はoverrideが無いroleは `base_getter(role)` を素通し=基底Styleがそのまま送信される。モジュール冒頭にも「defaultは現行とバイト同一」「defaultでは新しいkey/fileを書かない」と明記 | `er019_family_x_style_profile_01.py:13-14`、`:229-230`、`:347-358` |
| 9 | Y Gateの効果: `y_style_gate` は `prof = get_profile(style_profile)["overrides"].get("FULL_STORY")` が `None` のとき、Adv側の `evaluate_segment_evidence`・`ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`・`ADV_MINIMAL_FALLBACK` を実行しない(`if prof is not None:`)。XのM3は `profile_id == PROFILE_DEFAULT` で即PASS(`checked=[]`)。※Std側の `STD_FALLBACK_USED_OR_UNKNOWN` と `LOCAL_REWRITE_RECOVERY` は `prof` と無関係に実行される | `er121_family_y_audio_01.py:683-709`、`er019_family_x_style_profile_01.py:685-697`(docstring「profile==default なら何もしない(PASS)」) |
| 10 | Yは固定記録を作らない: Grep `resolve_run_profile` in `er121_*.py` = 0件。run dirに `audit/style_profile.json` が存在しない(`redelivery_fee/run_01/b1b/audit/` 一覧に無し)。`assert_profile_backend(style_profile, tts_backend)` は呼ぶが `default` は検査対象外(`profile_id != PROFILE_DEFAULT` のときのみSTOP) | `er121_family_y_audio_01.py:430,517`、`er019_family_x_style_profile_01.py:387-395` |
| 11 | 対照: Y DEV Trial runnerは `STYLE_PROFILE = "fx_20261017"  # X新規run既定profile(Full Story=PD06 ほか)をそのまま継承`(コメント逐語)。固定記録も作成: `resolve_run_profile(theme, STYLE_PROFILE, write=True, …)` | `er110_family_y_audio_trial_01.py:40`、`:171`(導入コミット `a5646c542` FAMILY-Y-VOICES-DESIGN-01 委任_05) |
| 12 | 対照: Xの新規run既定は `DEFAULT_NEW_RUN_PROFILE = PROFILE_FX_20261017` | `er019_family_x_style_profile_01.py:187-189` |
| 13 | profile変更時の制約(M2): out_dirに `tts_generation_results.json`/`review_lock_state.json`/`human_approved_segments.json` のいずれかが既にあると、新規にprofile記録を作れない(Review Lock/人間承認はtext shaのみで照合しStyleを区別しないため)。resume時の[WARN]文も「承認済みの新Styleを使う場合は新しいout_dirで実行」と指示 | `er019_family_x_style_profile_01.py:290-295`(`_RUN_STATE_FILES`)、`:440-456`、`:373-386` |

## 2. (d) X側で `fx_20261017` が何を変えるか(1行説明)と、Yの対応部位

`fx_20261017` = `fx_20261016`(6 role)の SUPPORT_JA を R2→S3 に置換したprofile(`er019_family_x_style_profile_01.py:276-283`)。X新規runの既定(同:189)。ユーザー正式承認 2026-10-17(`CURRENT_SPEC.md:1268`、原文 `docs/pm/delegation_log/2026-10-17_FAMILY-X-STD-JA-S3-ADOPTION-AND-WIRING-01_PHASE-B_USER.md`)。

| 項目 | role(level) | 内容(1行・定数先頭) | Yの対応部位(Y ID) | Y run_01の実際のStyle(§4) |
|---|---|---|---|---|
| PD06 | FULL_STORY(Std/Adv) | 177字。`Speak directly to one listener with warmth and a smile in your voice; calm, steady and reassuring, like a favorite morning radio host, …`(Stdは減速指示を連結せず生成後6%減速のみ: `std_append_slower_instruction=False`) | Y-B-04/05/06・Y-S-05/06/07(lead/intro/voice/closing+chunk) | 基底 `calm, steady news narration with natural emphasis at key points and turns; not dramatic.`(Stdは更に `Speak at a slightly slower, relaxed pace…` を連結) |
| S3 | SUPPORT_JA(Stdのみ。対象segment=preview・comment_1〜4。japanese_title・KP日本語意味は対象外) | 199字。`温かみと親しみのあるニュースナレーターとして、落ち着いた、明瞭な声で伝えてください。…` | Y-S-04(Std日本語 preview/comment) | `落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。…`(基底。comment_1〜3。a2 `preview` entryには `style_prefix` キー無し) |
| E1 | PREVIEW(Advのみ。Commentは対象外) | 68字。`calm, composed news anchor; steady and unhurried, clear and natural.` | Y-B-03のpreview | `calm, conversational`(基底) |
| K2 | KP_EN(Std/Adv) | 332字。`Say the phrase as one single, smoothly connected chunk of meaning, …`(Master Audio Store 2段key `key_phrase_english_component_k2`) | Y-B-07・Y-S-08 | MINIMAL(`Speak the following short phrase aloud naturally and clearly, in a warm podcast announcer voice, exactly once. …`、`primary_instruction_type=MINIMAL`)。`has_role_override`=False→K2経路を使わず「旧key+vote1専用key」 |
| P8-KP | KP_JA_MEANING(Stdのみ) | 93字。`落ち着いたニュースキャスターのように、明瞭で安定した声で読み上げてください。…` | Y-S-09 | `落ち着いた、自然な話し言葉で。…`(基底J3素通し) |
| P7 | KP_EXPLANATION_EN(Advのみ) | 136字。`Speak clearly at a slightly relaxed, natural pace. Keep a steady rhythm, with brief transitions between phrases and no drawn-out pauses.` | Y-B-08 | `clear, precise, at a measured pace, without dragging`(基底) |

未override(`fx_20261017`でも基底のまま)のため差が出ない部位: topic_intro、Advのcomment_1〜3(`calm, conversational`)、Stdのjapanese_title、shell固定英語。

## 3. (b) 設計・承認側の記述(Grep結果)

1. **設計(Fable/Sonnet作成)**
   - `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/DESIGN_01.md:84`: 「Style: profile `fx_20261017`を継承(OPEN-415はZ方式[定数参照+drift test]を採用)。」
   - `SPEC_LEDGER_03.md:60`(YL-A01): 「Style profile(PD06/S3/E1/K2/P8-KP/P7、fx_20261017)・Role Style固定記録・M3 Style gate | APPROVED/PRODUCTION_WIRED | … | Y適用要否=**APPLY(適用)** | 残作業=Y新runのStyle記録+drift testへ`CROSS_FAMILY_COMMON_STYLE_MAP`相当を追加(OPEN-415はZ方式[定数参照]を推奨) | 完了証拠=Y runのaudit/style記録がprofile一致・旧style混在を課金前STOP」。SPEC_LEDGER_01/02にも同行(YL-A01=適用)。
   - `OPEN_TRACKING_01.md:22`(OT-16): 「Y runのstyle記録がprofile一致+drift test」を完了条件に挙げ追跡先=OPEN-415。`OT-04`(同:10)は「共通音声仕様(Style profile…YL-A01〜A23)Yは未着手」。
2. **SSOT**
   - `CURRENT_SPEC.md:1699`見出し「共通仕様のFamily別配線Status表」(2026-10-17)の Family Y列: PD06・S3・E1・K2・P8-KP・P7とも「未着手(Y化時に最初から配線対象)」(同:1701-1706)。この表のY列はその後更新されていない(Grep `Y化時|配線対象`)。
   - `OPEN_ITEMS.md:927` OPEN-415: 「Family Y導入時に、共通Styleを1か所で解決しFamily別に承認/配線を追跡するprofileエンジン化の要否を判断する…Y導入時の設計課題の記録。Production挙動変更なし」(OPEN、区分=POST_USER_VALIDATION、棚卸し未実施)。
   - `DECISION_LOG.md`: Grep `fx_20261017|YL-A01|Family Y.*Style` → `fx_20261017` は X 関連エントリ(L21844-21883)のみ。**Yについての`fx_20261017`継承の承認・`default`採用の決定エントリは0件**。
3. **ユーザー原文**(Y関連、Grep `Style|profile|PD06|S3|E1|K2|P8|P7` in `docs/pm/delegation_log/*FAMILY-Y*USER*.md`)
   - `2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md:162-166`(§4-1): 「Family Yへ適用する仕様は、原則として今回のProduction立ち上げ時に組み込む。他FamilyでAPPROVED_FOR_PRODUCTIONとなっている共通仕様については、Family Yも適用対象として管理する。Family Yへの配線が未完了なら、Family Yを無条件に完全Closeしない。」
   - `2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_02.md:70-80`(§3-A): 「Family Yへの適用が必要なものは、今回のProduction立ち上げで組み込む。」/同:150「承認済みXYZ共通仕様が適用される。」/同:153「正式runtime evidenceに実際のmodel_id、routing、Prompt／Style等が記録される。」
   - `2026-10-25_FAMILY-Y-VOICES-DESIGN-01_USER_09.md:52`: 「Preview、Comment、Key Phrase、In One LineなどはFamily Yの既決設計とX共通仕様を適用する。」/同:64: 「既存の正式な速度・Style・TTS設定を継承」/同:66: 「最新の承認記録を確認し、未承認のVoice選定方式やStyle変更を追加しない。」
   - **個別のStyle名(PD06/S3/E1/K2/P8-KP/P7/`fx_20261017`)をYへ適用すると名指しした原文は、Grepの範囲で見つからない**。上記は一般規定。
4. **コミット/委任文での理由**: `7d5b9f8fc`(委任_02B)本文にStyle言及なし。`2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_DELEGATION_02B.md:8`(M-3)は「style record…は**X/Zが使う共通moduleを直接importして呼ぶ**」と指示。`DESIGN_01.md:60`のgate行も「style_profile gate(+Y body拡張)」と書く。
5. **Grepしたが該当なし(=記録なし)**: `STYLE_PROFILE|style_profile|fx_20261017` in `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/{EVIDENCE_01,EVIDENCE_02,EVIDENCE_03,DESIGN_02,OPUS_REVIEW_01,E1_HUMAN_REVIEW_01}.md`(`default`採用の説明なし)、`FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/{PLAN_01,INVENTORY_01}.md`(`y_style_gate(…,'default')` を実行した事実のみ: `INVENTORY_01.md:42`)。

## 4. (c) runtime: 実際に使われたStyle prefix(Y Production run)

出典: `er121_output/family_y_production_01/redelivery_fee/run_01/{b1b,a2}/audit/tts_generation_results.json`(`style_version=v3_j3_kp_meaning_and_explanation_guard`、`tts_backend=speech_metadata_flash_lite`)と `y_style_profile_gate.json`。E-3(`sns_age_limit/run_01`)の `y_style_profile_gate.json` も同一(`x_gate.status=PASS, checked=[]`)。

| level | segment | 記録された `style_prefix`(先頭) | `fx_20261017`で使われるStyle |
|---|---|---|---|
| b1b | y_lead / y_intro_1〜3 / y_voice_2 / y_voice_3 / y_closing | `calm, steady news narration with natural emphasis at key points and turns; not dramatic.` | PD06 |
| b1b | y_voice_1 | `<default:ENGLISH_STYLE_PREFIX>`(LR再TTS経由。`news_tail_fix` はLR再TTSで `style_prefix_override` を転送しない: `er003_v1_sing01_news_tail_fix.py:370-377`、共通核CC-F2) | PD06(ただしLR再TTSでは脱落する既知挙動) |
| b1b | preview | `calm, conversational` | E1 |
| b1b | comment_1 / comment_3 | `calm, conversational` | 未override(同一) |
| b1b | topic_intro | `brief, clear, engaging news topic introduction with natural emphasis on the topic; not dramatic.` | 未override(同一) |
| b1b | KP1 英語 / 解説 | `Speak the following short phrase aloud naturally…`(MINIMAL) / `clear, precise, at a measured pace, without dragging` | K2 / P7 |
| a2 | y_lead / y_intro / y_voice_2 / y_voice_3 / y_closing | `calm, steady news narration …` + `Speak at a slightly slower, relaxed pace than natural adult narration, …`(基底+減速指示連結) | PD06逐語(減速指示を連結せず6%減速のみ) |
| a2 | y_voice_1 | `natural, clear, conversational`(30字。minimal fallback系の記録) | PD06 |
| a2 | japanese_title / comment_1〜3 | `落ち着いた、自然な話し言葉で。意味の流れ・強調点・転換に応じて表情豊かに抑揚をつけてください。…` | comment=S3 / japanese_title=未override |
| a2 | KP1 英語 / 日本語意味 | MINIMAL / `落ち着いた、自然な話し言葉で。…` | K2 / P8-KP |

- `y_style_profile_gate.json`: `x_gate = {status: PASS, checked: [], human_approved: [], warnings: null}`(`checked`が空=XのM3は何も検査していない)。`y_body_checks` は `LOCAL_REWRITE_RECOVERY`(y_voice_1)以外の違反なし。
- 結論: Y run_01で実際に送信されたStyleは、基底6-role Style(`FAMILY_X_ROLE_STYLE_EN`)。`fx_20261017`のPD06・S3・E1・K2・P8-KP・P7のsha一致は検査されず、一致もしていない(文字列が別物)。

## 5. 再配達記事の完成版を「いま」制作した場合の影響(事実ベース。是正はしない)

前提: `FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01`(ユーザー指示 `2026-10-26_FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01_USER.md` §2-§3)は「Voice 2／3、その他の正常な音声は原則再利用」「現行の正式TTSモデル・Style・速度・Retry／Fallbackを使用」と指示している。

| 場合 | 事実 |
|---|---|
| (A) `STYLE_PROFILE="default"` のまま制作 | Styleは現行公開版(run_01)と**同条件**(基底6-role Style)。Voice 2/3等の再利用は`_tts_input_sha`(`STYLE_PROFILE`含む)が変わらないため成立する(`er121_family_y_runner_01.py:960-967`)。一方、§3の設計・台帳・DEV Trialが「`fx_20261017`継承」を仕様としているため、**仕様違反の可能性を残したまま完成版にする**ことになる(A/Bの確定は未)。X/Zの完成記事と比べ、本文Style(PD06)・KP(K2/P7/P8-KP)・Std日本語解説(S3)・Adv Preview(E1)が異なる。 |
| (B) `fx_20261017` へ切替えて制作 | 事実として: (1) `STYLE_PROFILE` は`_tts_input_sha`に入るため、`tts_b1b`/`tts_a2` が stale 判定になり再生成が要る(`er121_family_y_runner_01.py:960-967`)。(2) M2: 既存run_01 out_dirは`tts_generation_results.json`等が存在するため固定記録を新規作成できない=**新しいout_dir(新run)でのStyle記録開始が必要**(`er019_family_x_style_profile_01.py:290-295,440-456`)。(3) 影響範囲は`fx_20261017`のoverride対象=本文8 segment(Std/Adv)、Std日本語Preview/Comment、Adv Preview、KP英語(K2はMaster Store 2段keyで別key)、Adv KP解説、Std KP日本語意味。Voice 2/3の再利用は成立しない(Styleが変わるため)。(4) 切替後はX M3 Gateが有効になり、Advのminimal_fallback・Std fallback・LR採用がStyle違反としてBLOCK/要承認になる(`er019_family_x_style_profile_01.py:685-`)。(5) 費用の事実: run_01の`tts_b1b`+`tts_a2` 実績合計 ≒ JPY 28.2(Gemini TTS 9.16+8.85、OpenAI ASR 2.78+1.81、Azure 5.41+0.19、他。`cost_by_stage.json`)。再生成+再試行の見積は本調査では未実施。 |
| 補足 | Voice 1=Puck化(`FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01`、並行)はVoice名のみ差替えでStyle解決には影響しない(`er121_family_y_audio_01.py:239-249`は`voice`と独立)。 |

## 6. 3文書(X/Y/Z担当)との整合

Y棚卸し `FAMILY_Y_01.md` §8 Y-F01 の記述(`STYLE_PROFILE="default"`固定・`DESIGN_01.md:84`・YL-A01・runtime style prefix・M3/Y Gate no-op)は、本確認で全点を再現した。補正が1点ある。Y-F01の「M3/Y Gateの検査がno-op」はAdv側(`evaluate_segment_evidence`・`ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`・`ADV_MINIMAL_FALLBACK`)とXのM3(`checked=[]`)に限る事実で、Y GateのStd側`STD_FALLBACK_USED_OR_UNKNOWN`と`LOCAL_REWRITE_RECOVERY`は`prof`と無関係に実行される(§1-9)。

## 7. 未確認・限界

- ユーザーが「Yは`default`でよい」と口頭/別経路で述べた可能性は、`docs/pm/delegation_log/`・`DECISION_LOG.md`・`USER_DECISION_REGISTER_01.md`のGrep範囲では見つからない(会話ログ全文は未走査)。
- `USER_09.md:64`の「既存の正式な…Style…を継承」が、`fx_20261017`(X既定)を指すのか、Y Trial時点の基底Styleを指すのかは、原文からは確定できない(ただしDEV Trial `er110:40` は`fx_20261017`継承で実装されていた事実はある)。
- 費用: `fx_20261017`切替の再生成コストは見積っていない(read-only・API 0)。
- 次の一手(手順): 是正に進む前に Fable が「Yは`fx_20261017`継承か」を確認(read-only 30分程度)。B確定なら配線方針(Z方式=定数参照+drift test / X方式=`resolve_run_profile`)と、新run要否・再生成費用の見積を次委任で行う。

## 8. 所見(事実ではない)

1. 導入コミット(委任_02B)の指示文M-3は「style recordは共通moduleを直接import」としており、`default`固定は設計意図ではなく実装時の暫定値が残った可能性がある。ただし記録が無いため断定できない。
2. `default`は「X経路のM3を迂回する」性質を持つ(§1-9)。Yが`default`のまま通るため、`fx_20261017`のGate(Adv minimal_fallback等)がY Adv本文に働かず、Y Gateが一部だけを補っている構造に見える。`fx_20261017`へ切替えると、E-1で観測された「Std本文3回目=minimal fallbackは必ず要人間承認」(Y-F05)の扱いが変わる可能性がある。
3. 再配達記事の完成版を急ぐ場合、(A)で制作して「Style継承の確認結果が出るまで`default`版は暫定」と明示する選択も技術的には成立するが、これは品質基準の扱い(Charter 1)に関わるためFable/ユーザー判断事項。
