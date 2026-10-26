## 管理ID

FAMILY-Z-STYLE-ACTUAL-GATE-01 委任_01(OPEN-551是正: Family Z正式経路に「実送信Style prefixと承認値の実測照合」Gateと実測記録を追加[Y方式: 期待集合との完全一致・fail-closed・`audit/style_actual_vs_approved.json`]、Adv・日本語roleの実測sha記録、Style落ちfallback採用は人間承認要。過去runは遡及BLOCKせず「未記録」警告。+猿の手Std `full_story_part1_c10`のfallback採用clipが公開版に含まれるかの確認。API 0中心、実経路確認はmock優先・必要時のみ≤¥5)。並行Agent: TTS-RETRY-FALLBACK-LR-UNIFICATION-XYZ-01 委任_05(X Std日本語1 segmentの実走、`er127`/driverのみ。`er063`は触らない)。あなたの所有=`er063_family_z_audio_01.py`(`run_audio_gate`・Style記録部)、Z generator側の実測sha記録(`er026_*`/`er062_*`の該当leaf呼出。leaf本体=`er003_v1_*`は**編集禁止**。実測prefixはleafの戻り値/attempts_logから取得し、Z側で記録)、新規test(`er063_family_z_style_actual_gate_test_01.py`)、`docs/research/FAMILY-Z-STYLE-ACTUAL-GATE-01/{DESIGN_01,IMPLEMENTATION_01,PUBLISHED_CLIP_CHECK_01}.md`、`docs/pm/delegation_log/2026-10-27_FAMILY-Z-STYLE-ACTUAL-GATE-01_DELEGATION_01.md`(+check.json)、`docs/pm/RESULT_PACKET_ZSG1.md`。`er019_family_x_style_profile_01.py`編集禁止(X影響回避、Y方式と同じ)。公開ページ・run dir不変。SSOT編集権なし。pathspec付きcommit。

## 性質/到達上限Status/禁止事項

- 性質: 承認済み再発防止方針(FAMILY-Y-STYLE-PROFILE-FIX-01 PREVENTION_01 (a)=全FamilyのProduction runnerで承認profileと実測prefixをaudit必須化、未記録/不一致はBLOCK)のZ展開(B)。Opus: Y設計で任意レビュー済み(P-2 Gate設計のM-1/M-4/R-3/R-8を適用)。内容が実質同一のため再レビュー不要(Fable判断)。Zのセリフ(Dialogue)role・例外role(`CROSS_FAMILY_COMMON_STYLE_MAP`)の扱いが新規論点なので、`DESIGN_01.md`に明記しFableが照合。到達上限=IMPLEMENTED(正式経路mock確認)。
- 禁止: Style文面・Prompt・Voice・回数の変更、X/Y Gateの変更、過去runの遡及BLOCK、禁止Git操作。
- 費用: 上限¥5(Guardrail、T-3定型どおり)。
- 時間見込み: 約3h。

## 固定ブロック

従来どおり。T-0: 委任文保存+check、結果1行。T-2: 実TTS時は`TTS_EXECUTION_MODE=STANDARD`明示。T-3: 上記。
T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-27_FAMILY-Z-STYLE-ACTUAL-GATE-01_DELEGATION_01.md` をN=695から順に試し、先頭「## 管理ID」+「FAMILY-Z-STYLE-ACTUAL-GATE-01 委任_01」のものを採用。

## 事前指定Read一覧

- `docs/research/PM-OPEN-548-551-INVESTIGATION-01/OPEN551_Z_STYLE_CHECK_01.md` 全文(出発点: 不足箇所・実測null role・猿の手clip)
- `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/{PREVENTION_01,DESIGN_02,IMPLEMENTATION_01}.md`(Y方式: `Y_ROLE_COVERAGE`完全一致、`style_actual_vs_approved.json`、日本語roleの実測instruction取得、M-4「取れなければ意図sha(実測なし)ラベル」)、`er121_family_y_audio_01.py`: Grep `style_actual_vs_approved|Y_ROLE_COVERAGE|y_style_gate` ±20(実装の参照)
- `er063_family_z_audio_01.py:266-312,677-723,1148-1170,1253,1899-1930`、Grep `CROSS_FAMILY_COMMON_STYLE_MAP|style_record|z_adoption|fallback` ±10
- `er019_family_x_style_profile_01.py:534-594`(`_final_style_record`、読み取り)
- 統一flow後のStyle記録: `er127_tts_block_policy_01.py` Grep `style_prefix|block_evidence` ±10(採用attemptのtop-level `style_prefix`正規化=M-5)
- 公開確認: `user_test/family_z_monkeys_paw_01/`(Std公開ページ・mp3)と`er026_output/.../the_monkeys_paw/run_sf_prod_01/a2/`の`full_story_part1_c10`採用記録・assembled manifest

## 実施事項

1. **DESIGN_01.md**: Z期待集合`Z_ROLE_COVERAGE`(role×level×segment/clip。セリフ=既定Style[意図値]を期待、例外role=`CROSS_FAMILY_COMMON_STYLE_MAP`の理由付き期待値)、実測取得元(統一flow後はtop-level `style_prefix`、旧記録は`attempts_log`末尾、日本語はinstruction実測・取れなければ「意図sha(実測なし)」ラベルで一致扱いしない)、判定規則(不一致/未記録/checked空/role未カバー=BLOCK。**過去run(本Gate導入前のaudit)は「未記録」警告でBLOCKしない**=導入日時/run作成日で判定)、Style落ちfallback(`z_adoption=adopted`かつfallback Style)=人間承認必須(承認recordなし→BLOCK)、出力`audit/style_actual_vs_approved.json`。
2. **実装**: `run_audio_gate`への検査追加、Z側の実測sha記録(Adv narrator/preview/comment、日本語role、Dialogue、b1b TOPIC_INTRO)、test(match/不一致注入/checked空/未記録/fallback承認なし→BLOCK・承認あり→PASS/過去run警告/既存fixture出力不変)。回帰: `er063*`・`er026*`・`er062*`・`er127*`(接続0)。正式経路確認=mock runner(`--mode mock`相当があれば)で新Gateの発火/PASSを観測。
3. **PUBLISHED_CLIP_CHECK_01.md**: 猿の手Std公開版に`full_story_part1_c10`のfallback採用clipが含まれるか(assembled manifest/sha/公開mp3のtimeline照合)。含まれる場合=事実と選択肢(差替え=再生成約¥1〜2+再組立・公開更新[公開物差替えはユーザー判断]/現状維持)を記載(実施しない)。

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-27_FAMILY-Z-STYLE-ACTUAL-GATE-01_DELEGATION_01.md --json-out ...\_check.json`
- 回帰: `.venv\Scripts\python.exe run_project_regression.py --pattern "er063*_test_*.py"`、`--pattern "er026*_test_*.py"`、`--pattern "er062*_test_*.py"`、`--pattern "er127*_test_*.py"`
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。`RESULT_PACKET_ZSG1.md`にOPEN-551更新文案(IMPLEMENTED・evidence要否)、CURRENT_SPEC Z節追記案、猿の手clipの判断候補(該当時のみ)。

## Git

- commit message: `FAMILY-Z-STYLE-ACTUAL-GATE-01 委任_01: Z正式経路にStyle実測照合Gate(Z_ROLE_COVERAGE完全一致・fail-closed・過去run警告)+実測sha記録+test、猿の手Std fallback clipの公開確認(API 0)`。trailer: `Delegation: FAMILY-Z-STYLE-ACTUAL-GATE-01/01`。push。

## 報告

`docs/pm/RESULT_PACKET_ZSG1.md`: (0)T-0、(1)設計要点(Z固有論点)、(2)実装・test・回帰、(3)正式経路mock確認、(4)猿の手clip確認結果、(5)判断候補、(6)必須4行+「判定整合: 重大NG=<なし|あり>」、(7)SSOT文案、commit hash・raw URL。末尾5行要約。