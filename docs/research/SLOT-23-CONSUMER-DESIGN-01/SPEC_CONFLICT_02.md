# SPEC_CONFLICT_02 ユーザー正式決定(2026-10-27、原文=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`)と既存仕様・コード・Validator・testの矛盾一覧
read-only調査(API 0)。行番号は2026-10-27時点(HEAD c88ee48bc)。更新方針の記号: **U**=更新(新仕様へ) / **D**=削除(旧経路撤去) / **K**=維持(変更しない=決定の「他機能は変更しない」) / **T**=testの期待値更新。
決定の根拠行(USER.md): Std②全文表示=:15,:89,:167 / 旧経路を残さない=:80 / Adv側仕様踏襲・新方式を足さない=:95,:97 / 二重下線=§4(:100-115) / 照合=:119-138 / 遡及なし=:53-60。

## 1. 「Standardで②が生成・表示されない旧経路」全列挙(撤去対象。USER.md:80)
| # | 場所(file:line) | 現状 | 方針 |
|---|---|---|---|
| S1 | `er119_kp_human_review_01.py:524-525` | `level=="a2" and vocab`→エラー「vocab(単語解説5件)はAdvanced(b1b)のみ。Standardでは指定できません」 | **D/U**: `std_part1`マーク付きreview(新規)ではStdもvocab可(Adv同様、KP⊂vocab・最大5件)。マーク無し=遡及なし区分(§5) |
| S2 | `er119…:527-530` | b1bのみ「vocab必須・KP⊂vocab」 | **U**: 必須化の対象を「Adv、またはstd_partマーク付きStd」へ(level単独条件の撤去) |
| S3 | `er119…:564,579` | `auto_select`: `vocab = chosen[:5] if level=="b1b" else []` | **U**: Std新規reviewもvocab=先頭5(KP含む) |
| S4 | `er119…:667-668` | `op_select`: vocab指定必須はb1bのみ | **U**: 同上 |
| S5 | `er119…:941` | 最終Redundancy QA: `level=="b1b" and set(vocab)!=set(kp)` | **U**: Std新規も対象(②含む集合でQA) |
| S6 | `er119…:1024,1031-1035,1043-1050` | `finalize`: `vocab_items=…if level=="b1b" else []`、`vocab_confirmed.json`はb1bのみ書き、a2は`.removed`へrename | **D/U**: Std新規は`vocab_confirmed.json`を書く。a2の`.removed`分岐は「マーク無し旧review」限定へ縮小(新規からは到達不能) |
| S7 | `er119…:1092,1109` | `require_final_consistent`: `vocab`整合はlv=="b1b"のみ | **U**: Std新規も(iv)vocab_confirmed.json=selection.vocab |
| S8 | `er119…:1307` | 依頼書の選択コマンド例: `--vocab`はb1bのみ | **U**: Std新規も案内 |
| S9 | `er128_kp_confirmed_content_01.py:392,527,558,1641,1714` | `vocab_ids … if level=="b1b" else []`(artifact照合・`from-review`・`restore`・`revise`でStdは常にvocab空) | **U**: 共通ヘルパ`_vocab_ids_for(level,review)`に集約しStd新規対応 |
| S10 | `er128…:1378,1385-1386` | `cmd_from_form`: Stdは`vocab_ids=None`、②は`unconsumed[]`へ`reason=STD_CATEGORY2_NO_SLOT` | **D/U**: StdもStd②→`items`(category=2, slot=vocab)。`STD_CATEGORY2_NO_SLOT`は新規発行0(読取互換のみ残置) |
| S11 | `er128…:393-398`(`_artifact_diffs`) | vocab突合は`level=="b1b"`のみ | **U**: Std新規も`vocab_confirmed.json`と突合 |
| S12 | `er128…:818` | `verify_outputs`のPart 1表示G3は`elif level=="b1b" and vocab_page_paths` | **U**: Std新規もPart 1表示検査(`vocab_page_paths`) |
| S13 | `er120_part2_wiring_01.py:497-530` | `public_study_html`: `if level=="b1b"`のみPart 1、docstring「a2: Part 2のみ(Part 1はAdvのみ)」 | **U**: 新規(マーク付き)Stdも`part1_items`+`study_html_for_audio_dir(level="a2")` |
| S14 | `er003_kp_general_explanation_01.py:500-530` `study_html_for_audio_dir` | `b = f"{audio_dir}/b1b"`固定 | **U**: `level`引数化(既定b1b=Advバイト同一) |
| S15 | `er003…:411-415` `write_study_text` | `"level": "Advanced"`固定 | **U**: level引数(既定Advanced) |
| S16 | `er003…:39-44` `PROMPT_HEAD` | 「B1〜B2相当」固定 | **U**: levelキーでHead差替え(b1b=現行とバイト一致、`PROMPT_TEMPLATE_SHA256`不変) |
| S17 | `er019_family_x_audio_production_runner_01.py:415-418,430,558-570,904-921` | Part 1はb1bのみ生成(`generate_part1_all_for_b1b`、scaffoldでb1b KP PASS後のみ)、:921コメント「Standard(a2): Part 1は無い」 | **U/D**: level引数化し両levelで生成。コメント撤去 |
| S18 | `er019…:658-664` | Part 1訳pool「Part 1はAdvのみ=Standardは空」 | **U**: Std新規もpool(食い違い検査) |
| S19 | `er019…:3664` | tts/assemble/playerの入口のPart 1存在/最新性確認は`"b1b" in levels`のみ | **U**: Std新規も確認 |
| S20 | `er019…:3725-3749` | player: `_part1_html`は`"b1b" in levels`、`_study_html_a2=compose_page_html("", …)`「Part 1はAdvのみ」 | **U**: Std新規は`part1_study_html_for_player(level="a2")` |
| S21 | `er026_family_z_fiction_production_runner_01.py:1135,1537-1542,2196-2201,2206-2217` | `_part1_items_b1b`、stage名`kp_part1_b1b`/`kp_part1_ja_b1b`、path `key_phrases/b1b/…`、`part2_a2`「Part 1は無い」 | **U**: level別stage(`kp_part1_a2`等)・path・items |
| S22 | `er026…:1700-1705` `_part2_pool` | Std=空 | **U** |
| S23 | `er026…:2476-2491` `stage_pages` | `study_html_std = compose_page_html("", _p2res_std)`「Standardに載せるのはPart 2だけ」 | **U**: Std新規はPart 1ブロック+Part 2 |
| S24 | `er026…:2548` `has_vocab_on_page` | page_verifyのPart 1有無判定(Adv用) | **U**: Std新規にも要求 |
| S25 | `er121_family_y_runner_01.py:11,317,321,669-676,956,1098` | `STUDY_TEXT_SLOTS`「Advancedのみ」、`PART1_STAGE="kp_part1_b1b"`、`_part1_items_b1b`、`_assert_study_ready("tts_b1b")`、Std pool空 | **U** |
| S26 | `er121…:1202-1215` `stage_pages` | `study_html_std = compose_page_html("", p2res_std)` | **U** |
| S27 | **Validator** `er121…:1021-1026` | `elif n1: raise YE2EStop("FAMILY_Y_PART2_OUTPUT_MISMATCH(a2): StandardにPart 1が{n1}個あります(Part 1はAdvancedのみ)")` | **D/U**: Std新規は「Part 1がちょうど1個、かつPart 2の直前」(Adv規則を両levelへ)。マーク無し旧runのみ0個許容 |
| S28 | `er_user_listening_page_common_01.py:138-163` `render_standard_page` | level別study_htmlは任意(構造は両level対応済) | **K**(コード変更不要。コメントのみ) |
| S29 | `CURRENT_SPEC.md:1717`(表見出し「Advancedのみ」)/`:2083`(節見出し)/`:2086`(「Advanced=b1bのみ。Standard・A/B/C・Yへは拡張しない」)/`:2101`/`:2106`(Part 2の旧「Advancedのみ」履歴)/`:3111`(Y追記) | Part 1の対象 | **U**: 「②追加解説の表示に関して、2026-10-27ユーザー正式決定でStdへ拡張(X/Y/Z)。A/B/Cは対象外のまま」を追記(旧文は履歴化)。**SSOT編集はFable/別委任**(本委任は編集権なし) |
| S30 | `OPEN_ITEMS.md:1078`(OPEN-562)/`:1027`(OPEN-512) | 562=ユーザー確認待ち(Q1-3) / 512=Adv限定 | **U**: 562をAPPROVED_FOR_PRODUCTION・実装中へ、512は拡張注記(Fableが更新) |

## 2. Validator / test(期待値が旧仕様=Stdに無いをassertしているもの。不整合な出力を期待値としてassertするtestは書かない)
| # | file:line | 内容 | 方針 |
|---|---|---|---|
| T1 | `er120_part2_wiring_integration_test_01.py:182,444,510` | `assertNotIn("Vocabulary", sec_std/html_std)`「StandardにPart 1は無い」 | **T**: 新規(マーク付き)Stdは`assertIn`+Part 1→Part 2順。マーク無し旧fixtureのみ`NotIn`を残す(遡及なし回帰として) |
| T2 | `er128_kp_confirmed_content_test_01.py`(`STD_CATEGORY2_NO_SLOT`参照) | Std②がunconsumedになることを固定 | **T**: 新規はStd②→items。旧record読取互換のtestは別名で残す |
| T3 | `er119`系test(Stdのvocab指定エラーを固定する箇所。実装時に`Standardでは指定できません`をGrep) | | **T** |
| T4 | `er121_family_y_runner_01_test_01.py`(PART1/Std 0個) | 上記S27のtest | **T** |
| T5 | `er003_kp_general_explanation_01_runner_integration_test_01.py`/`er120_part2_grammar_production_01_test_01.py:929`ほか | Std非対象/level固定 | **T**(Adv系はバイト同一の回帰として維持) |

## 3. 維持すべき記述(今回の決定で変えない。USER.md:23-25「勝手に表示対象や品質基準を変更しない」)
- ①KP音声(Std/Adv)・KP行表示・Adv「英語での解説」(`explanation_en`)・Part 2文法(Top1/Top2、0件可、`er120`系)・Chunk/ポーズ・Style: すべて**K**。
- Adv Part 1の生成物(Prompt本文・`PROMPT_TEMPLATE_SHA256`・signature・保存形式・表示HTML)はバイト同一を保つ(DESIGN_02 §A、回帰test必須)。
- `STUDY_CSS`(`.study`)/`compose_study_html`(Part 2)の共通テンプレ: **K**。
- A/B/C Family: 対象外のまま(開発対象はX・Z・将来Y、27-7)。

## 4. 影響を受ける承認済みGate/Validatorとの整合(矛盾ではなく拡張が必要)
- KCP G0〜G4(`er128`): Std②がitemsに入る→G1(`_artifact_diffs`)/G2(TTSは対象slot=kpのみで不変)/G3(Std Part 1表示)/G4(retry/resume時のvocab保持)をAdvと同型でStdへ拡張(DESIGN_02 §D)。`PROTECTED_ITEM_FIELDS`は変更しない(`content_sha256`の定義不変)。
- `check_page`(`er_user_listening_page_common_01.py`、`div.script`の`all_text()`を`_norm`して`_INTERNAL_RE`検査): ハイライトの`<strong>/<span>`は`all_text()`が子ノード文字を連結するため文字列は不変(test+実ブラウザで確認、DESIGN_02 §B)。`⏸`検査(public)は無関係。
- GPG(文法事前生成・Top1/Top2・0件可): 文法は**Part 2**で独立。Std節の構成順はAdvと同じ「Part 1→Part 2」(`compose_page_html(part1_html, result)`、`er120_part2_wiring_01.py`)。Std文法0件(AI島)でも固定文面はPart 2に出る→Part 1は影響なし。文法の選定・解説・凍結ロジックには触れない。
- 進行中作業との競合: GPG委任_05C(Y evidence)は`er121`/`er128`のgrammar系・evidence出力を触る可能性。本設計の`er121`/`er128`編集はlevel化・vocab系の別関数。着手前に`git status`で競合確認し、同一ファイルの同時編集は関数単位で分離(IMPL_PLAN_02 §所有)。X TTS診断(read-only)は競合なし。AI島のassemble停止(d05729316、M3 Style Gate)は別Agent担当=AI島ページ再ビルドの前提(IMPL_PLAN_02 §依存)。

## 5. 「遡及なし」の実装的意味と、残る旧挙動の明示(USER.md:53-60 vs :80)
- 旧挙動(Stdに②なし・ハイライトなし)が**残る**のは次のみ: (a)`std_part1`マークを持たないreview(=決定前に作られた既存run)、(b)`display_spec`マークを持たない確定レコード。いずれも**新規作成経路からは到達不能**(`new_review`/`_new_record`が常に付与)。
- 制作中のAI島(Std)は既存reviewがマーク無し→**明示migrationコマンド**(`er128 … reconsume`、DESIGN_02 §F)で新仕様へ上げる(USER.md:140-155)。他の制作中runは、実記事かevidenceかを実装前のA0(API 0、`kp_human_review.json`走査)で列挙し、実記事のみ個別にmigrationする。
- 公開済みページは再ビルドしない。旧runで`pages`段を再実行しても、マーク無し→従来描画(ハイライトなし・Std Part 1なし)=バイト同一。
