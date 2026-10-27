## 管理ID

SLOT-23-CONSUMER-DESIGN-01 委任_04B(B班: Standard Part 1(①+②の英語表現に対するAdv同型の解説=日本語解説・Std難易度調整のみ、T1訳含む)の生成工程level化と、確定内容保護側の`display_spec`継承規則・G1不変条件・`reconsume`(AI島の明示移行)・③訳の保護。ユーザー正式決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`(APPROVED_FOR_PRODUCTION、Std②=C案)。設計=`DESIGN_02.md` §A/§F(+Opus所見M6/M7/M8/M9/M10/M11(er119部分)/R3/R4/N1/N2=下記に転記、これを優先)。Fable決定: Std Part 1=①+②(Adv同型KP⊂vocab)、解説言語=日本語(作業仮定A。ユーザー確認中。Prompt BODYのみで切替可能な構造にし、英語化は実装しない)。並行Agent: 委任_03(設計正本docs)、A班(委任_04A: `er_learning_highlight_01.py`/`er128_kp_highlight_01.py`/`er_user_listening_page_common_01.py`=**あなたは編集禁止**)、KCP委任_04(Z Std evidence run実行中。`er128`のCLI/関数の既存挙動を壊さないこと。run dirは触らない)。あなたの所有=`er003_kp_general_explanation_01.py`、`er003_kp_source_sentence_ja_01.py`(level対応が必要な場合のみ)、`er128_kp_confirmed_content_01.py`、`er119_kp_human_review_01.py`、対応test(`er003_kp_general_explanation_test_*.py`、`er128_kp_confirmed_content_*_test_*.py`、`er119_*test*`の該当)、新規`docs/research/SLOT-23-CONSUMER-DESIGN-01/IMPL_B_01.md`、`..._DELEGATION_04B.md`(+check.json)、`docs/pm/RESULT_PACKET_S23B.md`(gitignore)。**runner/builder配線(er019/er026/er121/er063/er120)は触らない**(C/D/E班)。**マーク発行(`new_review`での`std_part1`付与・`display_spec`導出の有効化)は実装するが既定では発火しない状態=関数は用意しcommitするが呼出点(`new_review`)への接続は最後の1commit(M14)でF直前に行う**。既存Adv Part 1はPrompt・sha・signature・HTMLバイト不変(golden test)。pathspec付きcommit、`git push origin HEAD:main`。時間見込み約3h。

## 仕様(Opus所見反映。これに従う)

1. **er003 level化(M6)**: `level`引数を`_variable_part`/`check_prompt_isolation`/`generate_general_explanations`/`generate_for_kp_items`/`resolve_*`/`require_fresh_*`/`assemble_part1`/`study_html_for_audio_dir`に通す。a2=`PROMPT_HEAD_A2`(学習者像1文+難易度指示1項目のみ差替え、BODY同一)、`PROMPT_TEMPLATE_SHA256_A2`、signature payloadに`level`(a2のみ付与、b1bのpayload/sha/signature不変)。保存先=level別dir(`study_text/<lv>/`相当、既存Adv dirは不変)。品質検査=Advと同一(日本語本文30字以上・見出し一致・禁止パターン)。Std Headに`(A2)`表記禁止。入力隔離(`KpIsolationViolation`)はlevel対応で維持(弱めない)。T1訳工程(`er003_kp_source_sentence_ja_01.py`)はlevel別dirで独立実行(level間再利用なし=N2)。golden test: b1bのPrompt/sha/signature/HTML固定+a2のsha固定。
2. **er119(M9/M11一部/R4)**: Stdでのvocab指定エラー(`:524-525`)をlevel非依存化(KP⊂vocab規則は両level)、auto選定/op_select/最終QA/finalizeのStd vocab空化・`.removed` rename(`:1044-1048`)を撤去し、両levelで`vocab_confirmed.json`を`finalize_kp`のみが書く(単一writer維持)。`std_part1`は存在時のみ`selection_signature`に含める(旧署名不変)。失敗marker/案内コマンドのb1b固定(`er019`側はC班)。
3. **er128(M8/M9/M10/R3)**: (a)`display_spec`=前レコードがあれば継承、新規時はreviewの`std_part1`から導出(付与点は`new_review`の1箇所のみ、**接続は最後の1commit**)。`_new_record`では付与しない。(b)G1不変条件: a2で`display_spec`⇔`std_part1`一致、`display_spec`付きなら`STD_CATEGORY2_NO_SLOT`=0件、Std②は`unconsumed`へ落とさず`items`へ(`:1378-1386`の分岐を`display_spec`有無で切替。マーク無し旧runは従来どおり)。(c)`reconsume`コマンド(`cmd_revise`型): `confirmation_id`/`origin`保持、Stdのreview `selection.vocab`+`std_part1`をreview_lock下で更新、`validate_selection`通過必須(NG=ISSUE・移行しない)、`vocab_confirmed.json`は退避+`_try_refinalize`のみ(直接書かない)、確定Redundancy QA(LLM)が次回起動で走ることを出力案内に明記、`--user-ref`必須、hash chain継続。(d)③`japanese_gloss`の保護: `_cand_diffs`照合対象へ追加、`confirm-revise`で③も修正可能に(`:1698-1700`)。(e)kill switch `EIGO_KP_CONFIRMED_PROTECTION`の意味は変えない。表示有効化判断用に`load_record`直読みの純関数`display_spec_of(run, level)`(flag非経由)を提供。
4. test: 上記すべて+A/B/C非接触検査の許可リスト更新+`er128_*` 201件・`er119_*`・`er003_*`回帰PASS。既存失敗(OPEN-543)は無関係なら記録のみ。
5. `IMPL_B_01.md`: 変更点・公開API(C/D/E班向け: `generate_for_kp_items(level=)`、`study_html_for_audio_dir(audio_dir, level=)`、`display_spec_of`、`reconsume`手順)・AI島移行手順(Std ②2件を`items`へ、Std Part 1=①3+②2生成≈¥0.16+QA)。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし(本委任はAPI 0。実生成はC班/F班)。

## 事前指定Read一覧

`DESIGN_02.md` §A/§F/§G、`SPEC_CONFLICT_02.md`(S1〜S27のer003/er119/er128該当行)、`er003_kp_general_explanation_01.py:140-240,300-400,470-540`、`er119_kp_human_review_01.py:500-600,930-1060`、`er128_kp_confirmed_content_01.py:80-100,210-260,440-460,570-600,1370-1420,1640-1720`、`CURRENT_SPEC.md:2083-2095`。

## 報告

`RESULT_PACKET_S23B.md`: (0)T-0、(1)差分・公開API、(2)golden test結果(Adv不変の証明)、(3)test、(4)M14対応(未接続箇所の明示)、(5)判断候補、(6)必須4行+「判定整合」、commit hash・raw URL。commit message: `SLOT-23-CONSUMER-DESIGN-01 委任_04B: Part 1生成のlevel化(Std=①+②・日本語解説・難易度調整のみ、Adv不変)+確定保護のdisplay_spec継承/G1不変条件/reconsume/③訳保護(マーク発行は未接続、API 0)`。末尾5行要約。