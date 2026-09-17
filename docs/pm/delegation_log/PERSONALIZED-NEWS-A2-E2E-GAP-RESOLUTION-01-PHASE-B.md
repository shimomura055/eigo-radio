## 管理ID

`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B`(前段: Phase A `docs/pm/RESULT_PACKET_PN_A2_GAP_PHASE_A.md`[設計案、既読扱い可・必要箇所のみ再Grep]、PREFLIGHT `docs/pm/RESULT_PACKET_PN_A2_PREFLIGHT.md`)。現在main=`0e956372`以降。報告は`docs/pm/RESULT_PACKET_PN_A2_PHASE_B.md`(新規)へ。

**並行タスクあり(重要・衝突回避ルール)**: 別sonnet-workerが`USER-TEST-NEWS-2EP-COMPLETION-01-RESUME-03`(er014_output/user_test_news_2ep_01配下でTheme 2のTTS/ASR/Assembly実行中→最後にDECISION_LOG/OPEN_ITEMS/PM_GOVERNANCE編集+commit/push)を実行中。
(1) **共有A-Family/共通module(`er003_*.py`、`er006_*.py`、`er008_*.py`、`er011_*.py`、`er005_*.py`)は変更しない**(相手のTTS/Assemblyが実行中に再importするため)。変更はB-Family module(`er012_b_family_*.py`)と新規ファイルに限定。共通contract(日本語タイトルconfig供給等)が共有moduleに触れる必要がある場合は、B-Family側で新規関数/新規moduleとして実装し、共有module側の変更が本当に必要なら**相手完了後**(下記marker確認後)に、既定値で既存挙動を完全に維持するadditive変更のみ行う。
(2) **音声stage(TTS/ASR/Assembly/Gate、共有store `er006_output/master_audio_store_01/manifest.json`・`pronunciation_ledger_01/ledger.json`・`human_review_queue.jsonl`へ書き込む処理)は、marker `docs/pm/RESULT_PACKET_NEWS_2EP_RESUME3.md` が存在するまで開始しない**(manifest.jsonの同時書き込み競合を避けるため)。markerが無ければ5分間隔で最大90分待つ。90分経っても無ければ音声stage前で停止し、記事stage完了までの状態を`WIRING_INCOMPLETE(音声runtime待ち)`として報告する(Fableが続きを再委任)。記事stage(Writer/Fact Checker/Ledger Deviation/Leakage/Key Phrase選定/Scaffold text/日本語タイトル text)はOpenAI呼び出しのみで共有storeに触れないため並行実行可。
(3) SSOT編集(DECISION_LOG/OPEN_ITEMS/CURRENT_SPEC/PM_GOVERNANCE)とgit操作は最後にまとめて行う。編集前に`git status --porcelain docs/pm/PM_GOVERNANCE.md DECISION_LOG.md OPEN_ITEMS.md CURRENT_SPEC.md`で自分以外の未commit変更が無いことを確認(あれば5分間隔で最大30分待つ)。commit前に`git fetch origin`→進んでいれば`git merge origin/main --no-edit`(rebase/force push禁止、競合時はSTOP)。全文Write禁止(Editで局所変更)。`docs/pm/ACTIVE_TASK.md`は最後に1回だけ固定ヘッダ形式で上書き(UDR-deferred欄: OPEN-159 DEFERRED/Family C 2仕様 APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE/RESUME-03の状態を引継ぎ)。

## 性質/到達Status/禁止事項

- 性質: B-Family Voicesの**新規topic A2をResearch/Ledger→A2 Writer→QA→Scaffold→Key Phrase→日本語タイトル→TTS→Assembly→Audio Validation Gate→playerまで正式Production E2Eで完走可能にする配線**+**Personalized News A2の実生成(runtime evidence)**。今回のA2 E2E gapはOpen Itemへ逃がさずProduction wiringまで完了させる。目的は「Personalized News専用runner」ではなく**B-Family新規topic A2を今後も再利用できる正式Production能力**。過剰一般化はせず、他FamilyのProduction codeを一括改修しない。
- 到達Status: `PRODUCTION_WIRED`(下記全条件充足時のみ)/`WIRING_INCOMPLETE`(音声runtime待ち等、理由明記)/`USER_DECISION_REQUIRED`(本当に新しいProduct判断が必要な場合のみ)。
- 禁止: B1→A2翻案(`run_writer_adapt`)の採用・参照、Trial/DEV script(`er012_editorial_b_voices_a2_trial02_writer.py`、`er012_b_voices_3v_a2_user_test_01.py`等)のimport、固定topic path/free_address専用sha256制約の新規topic経路への流用、固定辞書へのtopic追加が必要な設計、新しいEditorial原則の追加、Gate緩和、承認済み仕様の無断変更(下記ユーザー承認3点を除く)、Research再実行、不要なTTS/Writer再生成、`git add -A`/`stash`/`amend`/`rebase`/`force push`、wavのcommit。

## ユーザー正式判断(2026-09-17、原文要旨)

1. **A2生成方式=Verified Fact Ledger→A2直接生成**。B1→A2翻案は不採用(他Familyの成熟方式と揃う/Family横断共通化原則/A2・B1を独立最適化/B1の癖を引きずらない)。
2. **Key Phrase=A2自身の確定本文から選定**。B1 Key Phrase流用禁止。既存共通Key Phrase selection/canonicalization primitiveを再利用。
3. **日本語タイトル=記事生成時にconfig/引数で供給**する方式へ一般化。タイトル生成規約は既存維持(英語タイトルの自然な直訳・新しい事実・数字を追加しない)。B-Family新規topic Production経路で正式採用。既存Familyの一括破壊的移行は不要、既存挙動を維持しつつ今後の新規topicで使える共通contractとして設計。

### PM運用方針の追加(SSOT記録対象、PM Governance)
上位方針・承認済み原則から明確に導ける/他Familyとの共通化・整合に沿う/ネガティブ影響ほぼ無し/既存Production挙動を壊さない/追加API費用100円以内目安/時間を大きく消費しない/新Product方針・UX判断を伴わない/品質・安全性を下げない/Gate緩和でない/承認済み仕様を変更しない——をすべて満たす内容(config一般化、固定path除去、共通primitive再利用、明らかなSSOT整合、typo/plumbing/parameterization、regression追加、docs整合、既存方針から一意に導ける実装判断)は、**Fable/Claude側で判断して同時に進めてよく、毎回USER_DECISION_REQUIREDにしない**。USER_DECISION_REQUIREDにすべきは: 新Product仕様の新設/既存承認仕様の変更/複数案に明確な品質・UXトレードオフ/Gate緩和/Family共通原則の新設・変更/大きなregression risk/大きなコスト/大きな時間消費/品質低下の可能性/ユーザー方針から一意に導けない場合のみ。「念のため確認」は理由にしない。→ `docs/pm/PM_GOVERNANCE.md`の適切な節(11節「ループ上限・自明な修正の自律実施」系または新19節)へ記録し、DECISION_LOGにも本IDエントリ内で記録。

## 実装方針(原文要旨)

1. **新規topic A2正式入口**: `main_a2_2v()`または既存runner設計と整合する等価な正式入口(`er012_b_family_production_runner_01.py`、`main_b1_2v()` L1253と対称)。Trial/DEV非import、固定topic path不使用、free_address専用sha256制約を流用しない、genericなtopic/config/ledger/article outputを受ける、既存`main_a2()`(free_address固定記事経路)は壊さない。
2. **A2 Writer**: 既存B-Family generic writer構造(`er012_b_family_voices_writer_generic_01.py`)を利用し、**Ledgerを直接入力**にA2記事を独立生成。B1 article textは入力にしない。A2用Writer instructionはB-Familyの既存承認済みEditorial構造(5区切り: Hook/Voice A/Voice B/Tension/Closing)・Voice原則(一人称)・A2言語規約(CURRENT_SPEC「CEFR-A2構造」節の語彙・文長原則、B-Family A2節L652-718の既存A2規約)を維持しつつA2レベルへ適合させる。新しいEditorial原則を勝手に追加しない。
3. **共通QA配線**(A2確定まで、正式pathで): Fact attribution(`build_fact_attribution_block_if_enabled`/registry `fact_attribution_mode`、OPEN-132との整合を確認)、Fact Checker(`run_fact_check_a2`)、Ledger Deviation Checker、retry、Local Rewrite、Analytical Leakage Check、必要なB-Family Fact Safety、overlap monitoring等CURRENT_SPEC上A2で必要なQA。B1にあるから機械的に全部コピーせず、CURRENT_SPEC上A2に必要なものを正しく配線。
4. **Personalized News既存Ledger再利用**(Phase A項目7: `er014_output/four_type_observation_01/voices/`または`run2_clean/`のLedger、`VOICE_1/2_EVIDENCE`タグ付き)。Research再実行しない。A2は独立生成。B1の残存Leakage flagは継承扱いせず、A2で独立してLeakage QAを実行(既存corrective retry最大3回、残存時は既存B1/3V仕様と同型で記録)。
5. **Key Phrase**: A2確定本文から既存共通selection/canonicalization経路(Strategy L+Canonicalization、A-Family標準と同じ関数群)で選定。B1 KP dirコピー(`reuse_key_phrases_a2`)は新規topic pathで使わない。固定topic依存除去。
6. **日本語タイトル**: 新規topic A2 pathでconfig/argument供給。固定辞書追加が前提の設計にしない。既存規約維持。
7. **Scaffold/Comment/Preview**: 既存B-Family A2正式primitive(`run_scaffold_a2`、Comment Contract=registry COMMENT_ROLES、日本語Aoede)再利用。Writer確定前にScaffold生成しない(retry完了後の最終articleのみ)。
8. **TTS以降**: 既存B-Family A2 Production経路を正式利用(A2 slowdown/TTS/pronunciation safety/Primary・Secondary ASR/Human Review Lock/retry・fallback・regeneration/Assembly/Audio Validation Gate `B_FAMILY_A2`/player)。固定free_address専用asset依存は新規topic pathでは除去または汎用化。

## Regression(最低限)
B-Family既存B1 2V(`main_b1_2v`経路のtest)、既存A2 fixed-topic path(`main_a2`が無変更で動く=`--help`/`prepare` stage dry相当またはtest)、3V、relevant er012 tests(`er012_b_family_voices_writer_generic_01_test_01.py`、`er012_b_family_variable_voice_count_test_01.py`、`er012_*test*.py`をGlobで全列挙)、Family C test(`er013_family_c_production_test_01.py`、共有primitive変更がある場合)、project regression(既存の一括test runnerがあればGrep `regression|run_all_tests`で特定して実行)。新規topic A2追加により既存承認済みepisode生成が壊れていないことを確認。新規テスト(新入口のunit test: Trial非import・固定path非依存・日本語タイトルconfig必須・Key Phrase選定元がA2本文)を追加。

## Personalized News A2 runtime(wiring後、正式pathで1本実生成)
確認項目: actual model_id/Ledger reuse/Writer attempts/Fact Checker/Ledger Deviation/Leakage QA/Key Phrase/日本語タイトル/Comment・Preview/TTS/ASR/Human Review Lock/Assembly/Audio Validation Gate/player/duration/clipping/cost。出力dir例: `er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/`。日本語タイトルは英語タイトル("Is personalized news good for us?"相当、B1の確定英語タイトルを確認)の自然な直訳をconfigに記載(新事実・数字なし)。
- Human Review Lockが発火した場合: ASR EXACT/NORMALIZED_MATCHかつrepetition/disfluency QAのみの誤検知(OPEN-160/161相当のクラス、RESUME-03で登録予定)はNews 2EPタスク限定の事前承認であり**本タスクには適用されない**→STOPして報告(承認記録しない)。固有名詞誤読等も従来どおりSTOP。
- 語数報告義務: 本文語数、280未満/500超は明記。
- player: 既存B-Family A2 player primitive(`build_player_html_a2`)を使用し、あわせて`web/episode.mp3`(+segments)をexport。`user_test/unified.html`の`src`互換(既存player.html形式: `table.timeline`+`audio[id*=episode]`)を確認し、互換なら`https://rawcdn.githack.com/shimomura055/eigo-radio/<SHA>/user_test/unified.html?src=<PLAYER_PATH>&level=a2&en=<URL_ENCODED_EN>&ja=<URL_ENCODED_JA>`も出力。非互換ならunified.htmlは変更せずraw.githack player URLのみ出力し差分を報告。

## コスト
Research ¥0(Ledger再利用)。追加コストが¥100を大きく超える見込み(目安: 累計¥250超)になった場合はその理由を確認し、必要ならSTOP。TTS/Writerを意味なく再生成しない。

## Dangling Reference Check(必須)
新A2 Writer instructionがCURRENT_SPECと整合/retry・fallbackも同じinstruction・仕様を見る/Key Phrase contractが初回pathと後段(TTS・player)で一致/日本語タイトルcontractが正式仕様として存在(CURRENT_SPECへ記載)/Trial定義をProductionが参照していない/B1→A2翻案の旧Trial codeが新Productionから参照されていない。

## PRODUCTION_WIRED判定条件(全て)
新規topic A2正式入口/initial Production path/retry・fallback・regeneration整合/QA正式接続/Key Phrase汎用化/日本語タイトル汎用化/Audio後半接続/Personalized News A2 runtime evidence/regression PASS/actual model・routing evidence/CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS整合/Git commit・push/approved仕様と挙動一致。一部コード追加だけでは`PRODUCTION_WIRED`としない。

## SSOT
- CURRENT_SPEC.md: B-Family A2節(L652-718)へ「新規topic A2 Production経路(Ledger直接A2 Writer/Key Phrase=A2本文から選定/日本語タイトル=config供給)」行を追加し、L667(日本語タイトル)・L668(Key Phrase)行を「既存固定記事経路(free_address)では従来どおり、新規topic経路では本節新行を適用」と併記(既存行を削除しない)。Status列は実測結果に応じ`PRODUCTION_WIRED`または`WIRING_INCOMPLETE`。
- DECISION_LOG.md: 本IDエントリ(ユーザー判断3点+PM自律判断方針+実装・runtime結果+regression)。
- OPEN_ITEMS.md: A2 E2E gapは登録しない。OPEN-132(Fact attribution既定接続)に本経路での扱いを追記(接続したなら解消相当、未接続なら理由)。OPEN-151行に「A2新規topic経路配線(本ID)」を追記。別の独立問題を発見し、低risk/低cost/方針から一意なら同時解消してよい(報告)。本当にdeferが必要なもののみOpen Item候補として報告。
- PM_GOVERNANCE.md: PM自律判断方針を記録(上記)。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)
E-1: 同一ファイル再読禁止。D-1: Grep→該当行範囲Read(実装対象moduleの全文Readは可)。G-1: git出力最小化。F-1: transcript退避不要。T-1: 事前指定外Readは理由をRESULT_PACKETに1行記録(実装タスクのため広く許容)。T-0: 委任文を`docs/pm/delegation_log/PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行、結果をRESULT_PACKETへ1行記録(FAILでも継続)。

## 事前指定Read/Grep一覧
- `docs/pm/RESULT_PACKET_PN_A2_GAP_PHASE_A.md` 5-9節(設計案・Dangling結果)
- `er012_b_family_production_runner_01.py`: `main_b1_2v()`(L1253〜)全体、`main_a2()`(L1625〜)全体、`prepare_a2`/`reuse_approved_a2_assets`/`run_tts_a2`/`run_assembly_a2`/`build_player_html_a2`本体、L225-247(Phase 2コメント)、`if __name__`分岐
- `er012_b_family_voices_writer_generic_01.py`: 全体(B1 instruction構造、`write_new_theme`の入出力contract)
- `er012_b_family_voices_a2_production_01.py`: 全体
- `er012_b_family_editorial_type_registry_01.py`: `COMMENT_ROLES`/`japanese_titles`/`VOICE_ASSIGNMENT`/`fact_attribution_mode`
- A-Family Key Phrase共通経路: Grep `def .*key_phrase|canonicaliz|strategy_l` in `er003_v1_n3_01_scaffold_generate.py`/`er003_v1_n3_01_tts_generate.py`(呼び出すだけ、変更しない)
- `CURRENT_SPEC.md`: L586-720(B1/B-Family A2節)、Grep `^## CEFR-A2構造`→該当節、Grep `OPEN-132|fact_attribution_mode`
- `OPEN_ITEMS.md`: Grep `OPEN-132|OPEN-151`、`DECISION_LOG.md`: Grep `^## PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01`(直近エントリ書式)、`docs/pm/PM_GOVERNANCE.md`: Grep `^## 11|^## 18|^## 19|自明な修正`
- Personalized News B1成果物: `er014_output/four_type_observation_01/voices/`配下 Glob `**/verified_fact_ledger*`・`**/article*.md`・`run_result*.json`(英語タイトル・Ledger path確定)
- `user_test/unified.html`: Grep `src|table.timeline|audio|episode`(互換確認のみ、変更禁止)
- `docs/pm/PM_BRIEF.md` L135-159(固定ヘッダ)

## 手順
1. T-0。2. 設計確定(Phase A案に基づく、ユーザー判断3点反映)。3. 実装(runner新入口+A2 writer instruction+Key Phrase A2本文選定+日本語タイトルconfig contract+QA配線+player/web export、Trial非依存)。4. 新規unit test追加+regression実行(全PASSまで。失敗時は自分の変更起因かを切り分け、既存挙動を壊した場合は修正、既存の無関係な失敗は記録)。5. Personalized News A2記事stage実行(Writer→QA→Key Phrase選定→Scaffold text→日本語タイトル)。6. marker確認→音声stage(TTS→ASR→Assembly→Gate→player→web export)。7. SSOT(衝突回避ルール)。8. Git: 成果物commit(明示add、wav除外)→push→URL到達確認→SSOT/RESULT_PACKET commit→push。メッセージ`PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B: B-Family新規topic A2 E2E Production配線(Ledger直接A2 Writer/KP A2本文選定/日本語タイトルconfig)+Personalized News A2生成+regression+SSOT`、trailer `Task-ID: PERSONALIZED-NEWS-A2-E2E-GAP-RESOLUTION-01-PHASE-B`。

## 報告(`docs/pm/RESULT_PACKET_PN_A2_PHASE_B.md`、累積Full形式: Preflight/Phase Aの結論も1〜2行で含める)
0. T-0 1. 現在Status 2. Family横断原則との整合 3. 実装したA2 E2E構成(ファイル:関数、呼び出し順) 4. Production entrypoint(CLI実行例全文) 5. A2 Writer方式(instructionの要点、CURRENT_SPEC整合) 6. Key Phrase方式 7. 日本語タイトル方式(contract定義箇所) 8. QA/retry/fallback(配線一覧+runtime結果) 9. Personalized News A2 runtime(タイトルEN/JA、語数、Writer attempts、Fact Checker/Ledger Deviation/Leakage結果、TTS segment数、ASR、Human Review Lock有無、Assembly duration/peak/clipping) 10. Audio Gate 11. player URL(raw.githack player.html+web mp3+可能ならunified.html rawcdn) 12. cost(実測、model別) 13. model_id/routing 14. regression(test名・件数・PASS/FAIL) 15. CURRENT_SPEC更新行 16. DECISION_LOG行 17. OPEN_ITEMS更新 18. Git commit/push SHA 19. Dangling Reference Check(6項目○×) 20. 未決事項/同時解消した独立問題/Open Item候補 21. 無変更証跡(`git status --porcelain er003_*.py er006_*.py er008_*.py er011_*.py er005_*.py er013_*.py`が空[相手完了後にadditive変更した場合はその差分を明記])/事前指定外Read(理由付き)。ユーザー向け表記は「B1」に統一。
