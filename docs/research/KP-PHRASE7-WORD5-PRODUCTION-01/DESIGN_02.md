# DESIGN_02: Key Phrase最大7件 + Key Word最大5件 分離抽出のProduction配線(Opus条件A M-1〜M-9・R-2〜R-6反映版)
KP-PHRASE7-WORD5-PRODUCTION-01 委任_02 / 2026-10-27。`DESIGN_01.md`(委任_01)にOpus独立レビュー(`OPUS_REVIEW_01.md`、逐語=`docs/pm/delegation_log/2026-10-27_KP-PHRASE7-WORD5-PRODUCTION-01_OPUS_RESULT_01.md`)を反映した確定設計。DESIGN_01からの変更点だけを本書に書き、他はDESIGN_01のまま有効。
Status: ユーザー正式採用(APPROVED_FOR_PRODUCTION 2026-10-27)仕様のProduction実装設計。実装は`IMPLEMENTATION_01.md`。到達上限=IMPLEMENTED+EVIDENCE_COLLECTED(PRODUCTION_WIRED判定はFable)。

## 0. Opus指摘の対応表(M=必須修正 / R=任意)
| ID | 採否 | 反映内容(DESIGN_01からの変更) | 実装箇所 |
|---|---|---|---|
| M-1 | 採用 | `pick_backfill`の取り数を**種類別quota**(`plan.quota_phrase`/`quota_word`)にする(旧はE_kind)。`plan_quota(counts, n_phrase, n_word)`=`quota_phrase=min(E_phrase, 7-現存フレーズ)`、`quota_word=min(E_word, 5-現存単語)`、total=和 | `er119_kp_backfill_01.py:131,144` |
| M-2 | 採用 | 外側retry条件の`gate_dropped`除外tupleを`bf.GATE_DROP_EXEMPT_STAGES`(=`NOT_COUNTED_STAGES`+human_ng/duplicate_of_top3/excluded)に統一。`overflow_kind`は`NOT_COUNTED_STAGES`に含まれEに数えない。`rec["N"]`は`room/total/phrase_wanted/word_wanted/capped`を維持(`quota_phrase/quota_word`は追記) | `er119_kp_backfill_01.py:23-26`、`er119_kp_candidates_01.py:429` |
| M-3 | 採用 | フレーズ補完は`run_vocab_selection`を一般化した**1回call経路**(`spec=SPEC_P7`)。item単位で除外・内容不適合で再callしない(技術/parse失敗の再試行のみ既存2回)。`er105.run_selection_gate`は補完で使わず、`work/keywords_runtime_metadata.json`(call1)も書き換えない。`SELECTOR_2V_MAX_ITEMS`固定値は`max_items`(spec)へ置換 | `er119_kp_candidates_01.py:49-125,529-` |
| M-4 | 採用 | 既存Key Wordを含む補完フレーズは**補完フレーズの方を落とす**(`backfill_duplicate`、Nに数えない)。補完単語が既存/先着のKey Phraseに含まれる場合は補完単語を落とす。最終docの不変条件(フレーズ<=7・単語<=5・単語がフレーズに含まれない)をunit testとevidenceの検査項目に追加。DESIGN_01 §5の「既存単語を含む補完フレーズを保持する」は撤回 | `er119_kp_candidates_01.py:519-,605-640` |
| M-5 | 採用 | `make_p7_selector_fn`/`make_w5_selector_fn`を新設(`er119_kp_p7w5_prompts_01.py`)。harnessは`p7w5.make_*_selector_fn`をmockし、想定外のPrompt先頭は`AssertionError`(fail-closed)。旧`ft.make_selector_fn`・`p2v.make_vocab_selector_fn`は呼ばれたら失敗 | `er119_test_support_01.py` |
| M-6 | 採用 | er106のKPFT-3/4を`prompt_id`別の期待値(Prompt 2=3件・P2 sha / P7=7件・P7 sha)へ。無条件に両shaを許容しない。KPFT-1は`kp_backend=fulltext_p2`のまま(R-2)で変更不要 | `er106_joint_runtime_evidence_01.py`(`kpft_expected`) |
| M-7 | 採用(**直列**) | 補完のphrase/wordを**並列化しない**(理由: 共有state=contextvars[救済文脈]と`er005_cost_logger`のglobal `_CONTEXT`、発火は低頻度)。phrase→word順の直列。片方の種類だけ失敗した時は成功した種類を採用し`prompts[kind].status`にFAILEDを記録。STOP・routing違反(`FulltextSelectionError`)は握らず伝播(R-8継続) | `_run_backfill` |
| M-8 | 採用 | W5'のshaを**D4逐語1文**で再計算: `12d3370876d189f016cc49e26b2abcbe2618f028b380fe7fcff479554fa693b8`(DESIGN_01 §1-2の`187f1b87…`は旧2文案)。testで`P7 == er124.P7_TEXT`・`W5' == er124.W5_TEXT`と補足行1行だけ違う(test専用import)。Production moduleは`er124`を非import(testで固定) | `er119_kp_p7w5_prompts_01.py`、`er119_kp_p7w5_test_01.py` |
| M-9 | 採用 | `select_p7`内でP7のshaつきtelemetryを1行記録(`sc._log_kp_backend_telemetry`、`prompt_id/prompt_sha256`追記)。sc経由にしない(scは`PROMPT_2_SHA256`を固定記録するため)。er003は無編集 | `er119_kp_candidates_01.py:291-` |
| R-1 | **既知の限界として記録** | 基本形化後の`used_form`同士での含有確認(語形違い: price/prices・所有格・ハイフン語・push/pushed)は**導入しない**。一次防御=W5'本文の除外指示と、選定表層形でのGate`duplicate_of_top3`。取りこぼしはevidenceで`used_form`レベルの含有を実測して件数を記録する(下記§6) | - |
| R-2 | 採用 | `kp_backend`は`fulltext_p2`据置。Promptの識別は`prompt_id`/shaで行う | `select_p7` |
| R-3 | 確認済み・変更なし | Y/Zの`guard_fn`見積(`STAGE_EST_JPY["kp"]/2`=¥5、`er121:575`/`er026:1995`)は**候補生成roundごとの予算残guard**(事前確認)であり実費の上限ではない。7+5の1 level実費は約¥1.9〜2.2(Trial-02実測、現行比+約¥0.24)で¥5以内。最悪(外側retry 3周×attempt再選定+補完2call)でも約¥8で、以後のguard(次round・final redundancy)が`ctx.budget`で止める構造は不変。runnerは非編集 | `IMPLEMENTATION_01.md` §4 |
| R-4 | 採用 | evidence追記項目(最終docの不変条件、現行3+5比の費用・時間増分、`call1_attempts`/`outer_attempts`、P7が1語を返した件数・`overflow_kind`・`not_single_word`発生数、理由40字超件数[記録のみ]) | `EVIDENCE_01.md` |
| R-5 | 採用 | 受入8のmock E2Eは7+5のgeneratorを注入(`er119_kp_p7w5_e2e_test_01.py`: 共通配線をX/Y/Z×Std/Advで、X runner本体、Z runner kp stage)。runner内の古いコメント「最大8」(`er019:800`/`er026:2018`)は表記のみ=runner非編集のため記録のみ | e2e test |
| R-6 | 記録 | `count_exclusions`は`duplicate_of_top3`をEに数える(承認仕様どおり)。W5'の含有語漏れは単語補完callになるため、evidenceで発生頻度を監視 | evidence |

## 1. Fable確定D1〜D6の実装形
- **D1=R0**: 新flagなし・既定ON。`select_fn or select_p7`が唯一の既定。旧Prompt 2(`ft.PROMPT_2_TEXT`)・2-V(`p2v.PROMPT_2V_TEXT`)の本文・pin testは残置(旧runのresume・復帰用)。旧3+5へは`git revert`。
- **D2=(a)**: `auto_select`は無変更(kp=ai_rank先頭3、Adv vocab=先頭5)。単語組入れ(新仕様)は導入しない。
- **D3=X**: `not_single_word` Gate。位置=validate(救済後の句)→`not_single_word`→`duplicate_of_top3`。Eは`kind=word`固定(`count_exclusions`)。補完の単語callにも同じspecを適用。
- **D4**: W5'補足行=`- すでに選定されたKey Phraseに含まれる単語は、Key Word候補から除外する。`(ユーザー原文「…除外する。」の正しい表記)。DESIGN_01の2文案は不採用。
- **D5**: 補完Promptは種類別(フレーズ=P7、単語=W5')。2-Vは補完でも使わない。
- **D6**: 進行中の旧HR待ち候補は作り直さない(`ensure_kp_review`は保存済みdocをPromptのshaを見ずに読み戻す)。testで固定。

## 2. P7(Trial-02)とProductionの方式差(IMPLEMENTATION記録事項)
- Trial-02のP7(`er124:221-267`)は**ループなし**・不適合itemだけ落とす方式。Production化では`er105.run_fulltext_selection`のattempt loop(MAX_ATTEMPTS=2、1件でも不適合なら全件を機械診断noteで再選定、最終attemptはCMU未登録・除外句のみ落とす)を**維持**する(承認済みのcall1仕様)。K1(item単位化)は承認範囲外のため導入しない。
- 件数不足(7未満)は不適合ではないので再選定は起きない(再選定が起きるのはitem不適合時。費用+約¥0.12/回)。

## 3. 構成の確定(DESIGN_01からの差分のみ)
- er105(`keyword-only`・既定値=従来): `build_user_message(prompt_text=)`/`prompt_prefix_intact(prompt_text=)`/`validate_and_resolve(max_items=)`/`apply_exclusions(max_items=)`/`build_exclusion_note(limit=)`/`build_machine_note(limit=)`/`run_selection_gate(prompt_text,max_items,parse_fn)`/`run_fulltext_selection(…,prompt_id,prompt_sha256)`。`reason_ja`は入力にキーがある時だけ出力に付ける(Prompt 2経路はバイト同一)。
- `run_vocab_selection(spec=)`: specが`None`なら従来の2-V挙動。`SPEC_W5P`(max 5・単語1語のみ)、`SPEC_P7`(max 7)。
- `_enforce_kind_caps`: 組立直後に種類別上限(7/5)を強制(`overflow_kind`、Eに数えない)。
- doc: `prompt_ids={call1:kp_prompt_p7, call2:kp_prompt_w5p}`、`prompt_sha256`同様。`shortfall_detail`に`cap_by_kind/missing_by_kind`追記。`backfill`に`prompts={phrase,word}`(id/sha/quota/status/failure/model_id/response_id/n_kept/n_dropped)を追記し、旧スカラー`prompt_id/prompt_sha256`は`"per_kind"`(互換)。
- `rv.KP_CANDIDATE_MAX=12`(1行のみ。(a) KCP 02Aのcommit後)。`export_form_data_01.py`の`cap`既定8→12は本委任で触らず委任_03/フォーム側へ引継ぎ。

## 4. 撤去・残置(Charter 8)
撤去: `BACKFILL_MAX_CALL_ITEMS`(5件上限)・単一cap(`KP_CANDIDATE_MAX`)でのroom計算・補完が2-Vを使う記述・外側retry判定の独立tuple。残置: Prompt 2/2-V本文とpin test、`run_vocab_selection`の2-V既定、legacy経路。詳細=`REMOVAL_RESULT_01.md`。

## 5. 受入条件との対応
`TEST_PLAN_01.md`の1〜9に準拠。追加test=`er119_kp_p7w5_test_01.py`(pin/DefaultOn/er105既定値/select_p7/一般化vocab/D6/D2)・`er119_kp_p7w5_e2e_test_01.py`(mock E2E)・`er119_kp_backfill_test_01.py`改訂(種類別quota/M-1/M-3/M-4/overflow_kind)・golden_03(7+5)+旧golden call1分一致。

## 6. evidence追加観測(R-1/R-4/R-6)
最終docごとに(1)不変条件、(2)`used_form`レベルの単語⊂フレーズ件数(R-1限界の実測)、(3)`call1_attempts`/`outer_attempts`、(4)P7が1語を返した件数、(5)`overflow_kind`/`not_single_word`件数、(6)理由40字超件数(記録のみ・Gate除外にしない)、(7)現行3+5に対する実費・所要時間の増分(usage logから)。
