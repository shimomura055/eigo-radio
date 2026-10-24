# CP_CHECK_35: X2p'(委任_35)実装前の整合確認(ユーザー原文§2)

2026-10-24、API 0。照合先は作業ツリー現行(`er003_key_words_gloss_alignment.py`はHEAD=未変更状態で照合し、実装後に再確認)。

## 1. 4つの別仕様の責務表(X2p'は前3者の経路・出力を変えない)
| 仕様 | 責務・段 | 実装(file:行) | 対象item | X2p'との関係 |
|---|---|---|---|---|
| A-1(見出し語の一般化) | canonicalization段(`kc`のfulltext template/validator + `er105`のhook)。英語KPの参照語(that/the等)を`a/an`等へ | `er003_key_words_canonicalization.py`(`generalize_reference_word`)、`er105_kp_fulltext_selector_01.py`(`reference_pair_ok`・`find_inflection_window`)、配線commit `4128fffeb`(OPEN-474) | 全文選定item | **無変更**。X2p'はcanonicalization**後**のgloss生成段のみ(英語KP文字列は読むだけ) |
| 課題②(所有格一般化) | 同じcanonicalization段。`possessor_roles`→revertのみの決定論後処理(`postprocess_possessor_roles`) | 同上、`er003_v1_n3_01_scaffold_generate.py:504-507`(hook渡し) | 全文選定item | **無変更**。X2p'の対象はこの出力(`key_phrase`)を前提にglossを書くだけ |
| gloss再整合(欠落・人称) | gloss alignment段の**旧経路**: 追加語の欠落、人称一般化(`PERSON_CONSTRAINT_TEXT`)、決定論の人称突合 | `er003_key_words_gloss_alignment.py` `build_user_message_corrected`(:572→実装後は同関数・同文面)、`validate_item_corrected`、Z repair=`er026_family_z_fiction_production_runner_01.py:1612` | glossあり(再整合対象・人称一般化・人称不整合) | **旧builder/旧schema/旧developerのまま**(byte-identical、`DEVELOPER_MESSAGE`/`GLOSS_ALIGNMENT_JSON_SCHEMA`/`NEW_GENERATION_TEXT`/`PERSON_CONSTRAINT_TEXT`のsha256をtest WC-01で固定)。混在batchのlegacy側はこの旧経路 |
| **X2p'(本件)** | gloss alignment段の**新規生成経路**: gloss未生成の全文選定itemについて、本文での語義を確定(`meaning_in_text_en`→`naive_ja`→`naive_ja_conveys`)してから`japanese_gloss`を書く | 新builder`build_user_message_newgen_meaning`・`NewGenMessage`・`NEWGEN_*`(同module。文面=Trial_06`build_x_message06`とbyte一致) | `is_fulltext_gloss_missing(item)`(`fulltext_source_ref`あり∧gloss空)だけ | 新規。**人称規則(`PERSON_CONSTRAINT_TEXT`)は新builderでも文脈限定句置換版を引き継ぎ**、決定論の人称突合・括弧/算用数字/…/記号/qa/mappingの既存検査は新経路でも同一に働く(WC-07) |

## 2. 照合した既定値・SSOT
- CURRENT_SPEC.md:2788-2794(KP gloss再整合段: 「corrected=唯一の方式・既定ON」「flag=`EIGO_KP_GLOSS_ALIGNMENT`」「機械検査=記録のみ」「HR=人間通知」)。X2p'はこれを変更しない(flag新設なし、retry上限`MAX_GLOSS_ALIGNMENT_ATTEMPTS=2`不変、unresolved→HR不変)。
- CURRENT_SPEC.md:1994(全文選定の後段canonicalization・A-1・②)。X2p'は後段(gloss生成)のみ。
- DECISION_LOG: UDR #169(A-1採用)、#173(②+付帯)、#179(X2p' XYZ共通採用、本委任の根拠)。OPEN-467(記事B最終版再提出)・OPEN-474(KP一般化包括)・OPEN-484(Y未配線)。
- 既定値のGrep: 新規flagなし(`grep -n "EIGO_KP" er003_key_words_gloss_alignment.py`は`EIGO_KP_GLOSS_ALIGNMENT`のみ)。新経路は未承認機能ではなく`APPROVED_FOR_PRODUCTION`(UDR #179)。
- 本件のimport graph(`er003_key_words_gloss_alignment.py`・`er003_v1_n3_01_scaffold_generate.py`・`er026_family_z_fiction_production_runner_01.py`・`er019_family_x_audio_production_runner_01.py`・`er003_key_words_canonicalization.py`)に**未commit変更なし**(`git status --short`で`.py`のM表示0、`??`は無関係の新規.pyのみ)。Production runの前に確認。

## 3. 作業ツリー確認(ユーザー原文§4相当)
- `CURRENT_SPEC.md`は着手前から未commit修正(M)。`git diff`の内容=2026-10-23追記「ASR品質改善2件 X/Z状態」の1行を2行に分割しただけ(`+ 【Fable最終受入2026-10-23】`の改行化。他agent=ASR系の作業)。**本委任の変更ではないため触らない**。本委任のCURRENT_SPEC追記時は同ファイルの該当箇所以外を触らず、commitでこの差分が混ざる場合は報告する。

## 4. Family Y
- 正式Production入口(量産runner)は**存在しない**(`er110_family_y_*`はDEV/Trial専用。音声Trialは`production_reachable=False`、`er110_family_y_audio_trial_01.py:176`・`er110_family_y_persona_audio_trial_01.py`)。OPEN-484(2026-10-24起票)の記載どおり。
- KP段は共通module(`sc.run_key_phrases(..., kp_backend="fulltext_p2")`: `er110_family_y_text_trial_01_run.py:264`、`er110_family_y_persona_text_trial_01_run.py:281`)を通るため、共通実装により**コード上は追加配線なしでX2p'が効く**。ただしY Production入口が無いので `Y=COMMON_IMPLEMENTED_NOT_PRODUCTION_WIRED`。必要対応=Y正式Production入口の新設(OPEN-463/484)。本委任はY全体の新規Production構築を開始しない。
