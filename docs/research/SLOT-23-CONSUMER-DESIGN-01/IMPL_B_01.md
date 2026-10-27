# IMPL_B_01 委任_04B(B班): Part 1生成のlevel化 + 確定保護側(display_spec継承・G1不変条件・reconsume・③訳保護)
API 0 / JPY0。ユーザー正式決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`(APPROVED_FOR_PRODUCTION、Std②=C案)。設計=`DESIGN_02.md` §A/§F(+Opus所見M6〜M11/R3/R4)。
**マーク発行(`issue_std_part1_mark`の`new_review`への接続)は未接続**(M14=全6経路の準備後・F直前の最後の1commit)。接続前は新規reviewにマークは付かず、全経路が従来どおり動く。

## 1. 変更点(ファイル別)
| ファイル | 変更 |
|---|---|
| `er003_kp_general_explanation_01.py` | `level`引数(既定`"b1b"`)を`build_prompt`/`_variable_part`/`check_prompt_isolation`/`phrases_signature`/`generate_general_explanations`/`generate_for_kp_items`/`resolve_general_explanations`/`require_fresh_general_explanations`/`assemble_part1`/`write_study_text`/`study_html_for_audio_dir`へ。`PROMPT_HEAD_A2`/`PROMPT_TEMPLATE_SHA256_A2`新設。`phrases_signature`のpayloadは**a2のときだけ**`"level"`を追加(b1bのpayload/sha/signature不変)。a2のdocは`"level":"a2"`を記録、`require_fresh`/`resolve`はlevel不一致をStale/再生成。`write_study_text`のjson `level`は`Advanced`/`Standard`。入力隔離(`KpIsolationViolation`)・品質検査(日本語本文30字以上・見出し一致・禁止パターン`PAGE_FORBIDDEN_RE`)はAdvと同一のまま全levelで有効。 |
| `er003_kp_source_sentence_ja_01.py`(T1訳) | **変更なし**(翻訳Promptはレベル非依存=Adv/Std同一。署名・fileにlevelを入れない。level間の再利用はcaller側のlevel別dir分離で防ぐ=N2: Stdは`<audio_dir>/a2/key_phrases/`で独立に生成・検証)。 |
| `er119_kp_human_review_01.py` | `vocab_enabled(level, review)`(=`level=="b1b" or review.std_part1`)を新設し、`validate_selection(std_part1=)`/`auto_select(std_part1=)`/`op_select`/`_run_final_qa`/`finalize_kp`/`require_final_consistent`/`verify_selection_matches_outputs`/`render_request_md`/`ensure_kp_reviewのAUTO`をこの1関数に統一。Stdのvocab空化と`vocab_confirmed.json.removed`退避renameを**撤去**。KP ⊂ vocab規則は両level共通。`vocab_confirmed.json`を書くのは`finalize_kp`のみ(単一writer)。`selection_signature`は`std_part1`が真のときだけpayloadに含める(旧署名不変)。`issue_std_part1_mark(review)`新設(**呼出点0**)。`new_review`はprevがマーク付きなら継続のみ(新規付与はしない)。 |
| `er128_kp_confirmed_content_01.py` | `DISPLAY_SPEC_V1="LEARNING_ITEMS_123_V1"`、`_display_spec_for_new`(前レコードがliveなら継承、無し/取消済み/reconfirm_requiredならreviewの`std_part1`から導出)、`_new_record`がレコードへ`display_spec`を付与(マーク無しはキー自体を作らない)。`_artifact_diffs`は`display_spec`付きa2も`vocab_confirmed.json`と突合。G1不変条件`_display_spec_diffs`、③`japanese_gloss`保護(`_cand_diffs`、display_spec付きのみ)、`confirm-revise`で③も修正可、`cmd_reconsume`(CLI `reconsume`)、純関数`display_spec_of(run, level)`。`cmd_from_form`は`display_spec`有無で②の扱い(items/unconsumed)と③のreasonを切替。 |
| `er128_kp_confirmed_content_test_01.py` | A/B/C非接触検査の許可リストに`er128_kp_highlight_01.py`(A班の表示builder入口)を追加。 |
| 新test | `er003_kp_general_explanation_level_test_01.py`(golden含む)、`er128_kp_confirmed_content_slot23_test_01.py`。`er003_kp_general_explanation_01_test_01.py`のsignature assertを`level`追加に追随。 |

## 2. 公開API(C/D/E班向け)
```python
# Part 1生成(両level同一関数。b1b既定=従来とバイト同一)
import er003_kp_general_explanation_01 as p1
p1.generate_for_kp_items(items, call_fn=None, client=None, level="b1b"|"a2") -> dict        # a2は doc["level"]=="a2"
p1.resolve_general_explanations(items, cached, call_fn=None, client=None, level=...)           # signature+level一致ならAPI 0再利用
p1.require_fresh_general_explanations(items, doc, next_command=..., where=..., level=...)
p1.assemble_part1(kp_items, explanations, translations, article_text, level=...)
p1.write_study_text(dir_path, rows, level=...)
p1.study_html_for_audio_dir(audio_dir, items=None, level="b1b"|"a2") -> str                   # b = f"{audio_dir}/{level}"
p1.phrases_signature(items, model=None, level=...)  /  p1.build_prompt(phrases, level=...)
p1.LEVELS, p1.PROMPT_HEAD_A2, p1.PROMPT_TEMPLATE_SHA256_A2
# T1訳(変更なし): er003_kp_source_sentence_ja_01.generate_for_kp_items / resolve_translations / require_fresh_translations
#   Stdは a2 の key_phrases dir(例 <run>/a2/key_phrases/、Z=<run>/key_phrases/a2/)に独立して保存・検証する(level間再利用なし)

# Std Part 1の入力=Advと同一の単一アクセサ
import er119_kp_human_review_01 as rv
rv.part1_items(kp_dir)            # a2のvocab_confirmed.json(①+②)。reviewがあるのにvocabが無ければfail-closed
rv.vocab_enabled(level, review)   # vocab可否の単一関数(b1b常にTrue、a2はreview.std_part1)

# 表示有効化判断(flag非経由・書込みなし・load_record直読み)
import er128_kp_confirmed_content_01 as cc
cc.display_spec_of(run, level) -> "LEARNING_ITEMS_123_V1" | None     # 取消済み/レコード無し=None、未知の値=ValueError
```
Std Part 1の表示可否は`display_spec_of(run, "a2")`がNone以外であること(マーク無しの旧Std記事はNone=従来描画・Part 1なし)。保存先のlevel別dirはFamilyごとの既存規約(X=`<audio_dir>/<lv>/{key_phrases,study_text}`、Z=`<out>/key_phrases/<lv>/`)で、runner/builder配線(C/D/E班)が`level`を渡す。

## 3. マーク発行の接続手順(M14。F直前の最後の1commit)
1. `er119_kp_human_review_01.py` `new_review` の末尾コメント `NOTE(M14)` の位置で `issue_std_part1_mark(r)` を呼ぶ(1行)。
2. `er128_kp_confirmed_content_slot23_test_01.py::TestMarkAndVocabEnabled::test_M14_new_review_does_not_issue_mark_yet` を接続後の期待値(新規a2/b1b reviewに`std_part1`が付く)へ置換し、`marks_connected()`のpatchを不要にする。
3. `er119_*`/`er128_*`/`er003_*`回帰を再実行。接続は新規reviewのみ(既存review・既存記事は`reconsume`を明示実行しない限り不変=遡及なし)。
注意: 接続後に新規作成されるreviewは`std_part1`付き(b1bも)で、`selection_signature`が旧式と異なる(新規のみ。旧runの署名は不変)。

## 4. AI島(Std)移行手順(`reconsume`。ユーザー選定は不変)
前提: ユーザー確定レコード(live)があり、hash chainが正常。
```
py er128_kp_confirmed_content_01.py reconsume --run <run> --level a2  --by <名> --user-ref <delegation_logのpath>
py er128_kp_confirmed_content_01.py reconsume --run <run> --level b1b --by <名> --user-ref <delegation_logのpath>   # Adv: record側のみ(items/review/成果物は不変)
```
- a2: `unconsumed`のSTD_CATEGORY2_NO_SLOT(②)を`items`(category2, slot=vocab)へ移し、reviewへ`std_part1:true`と`selection.vocab=①+②`を書く(`review_lock`下、`validate_selection`通過必須。NG=`CONFIRMED_CONTENT_ISSUE`・rc=4で何も書かない)。③のreasonは`CATEGORY3_HIGHLIGHT`へ。`confirmation_id`/`origin`保持、`event="reconsumed"`・`user_ref`記録、hash chain継続、`content_sha256`再計算(itemsが変わるa2のみ)。確定物(kp/vocab/final)は`RECONSUME_SUPERSEDED`へ退避し、`_try_refinalize`のみ(`vocab_confirmed.json`を直接書かない)。`redundancy_fn=None`のため再finalizeは保留され、**確定Redundancy QA(LLM 1 call、①+②集合)は次回のrunner起動(制作コマンドの同コマンド再実行)で走る**。PASSで`vocab_confirmed.json`が`finalize_kp`により書かれる。QA NGならreviewはPENDINGへ戻りレコードは`reconfirm_required`(自動差替えしない)。
- 冪等: 同一入力の再実行は`{"reconsumed": false, "unchanged": true}`でレコードをバイト不変のまま返す。`--user-ref`必須(存在するファイル)。
- 費用: 移行そのものはAPI 0。Std Part 1生成(①3+②2=5件、1 call、`gpt-6-luna`)≈¥0.16 + 確定Redundancy QA(≈¥0.1/call級)。

## 5. 判断区分(判断候補)
- (B・承認範囲内で自己解決)`issue_std_part1_mark`はb1bのKP reviewにも`std_part1`を付ける設計とした(DESIGN_02 A-4「b1bは不問」。Adv新規記事にも`display_spec`=新表示仕様[二重下線等]を出すため、record導出元のマークが両levelに必要)。b1bでは`vocab_enabled`は元々True=挙動不変、署名にだけ反映。
- (B)Std Part 1の解説本文言語は日本語(作業仮定A)。英語化が必要になった場合は`PROMPT_HEAD_A2`のPrompt本文のみ差替え(構造は切替可能。英語化は未実装)。
- 未対応(スコープ外): `verify_outputs`(G3)のa2 Part 1行検査(`level=="b1b"`ガード)は§D(KCP G3拡張、別班)。本班は`_artifact_diffs`(G0/G1)までが対象。
