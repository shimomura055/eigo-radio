## 管理ID

AI-ISLAND-FORM-PRODUCTION-01 委任_06(AI島Std/AdvへのSLOT-23新表示仕様の適用準備。HR(hr_02 Q1)承認待ちの間に、承認後に残る作業を最小化する。前提=SLOT-23 A〜E+M班完了(マーク発行接続 commit 1684e19f5)、AI島run=`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01`(確定レコードあり=旧マーク無し、Std ②2件は`unconsumed`、M3 Gate BLOCK中=assemble未実施)。ユーザー正式決定=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md` §5(AI島に適用、①②③・文法の再選定不要、本文再生成不要、既存音声再利用)+`..._AI-ISLAND-FORM-PRODUCTION-01_USER_04.md` §2。有料上限¥10(Std Part 1 ①3+②2の解説+T1訳≈¥0.2、確定Redundancy QA少額)。並行Agent: SLOT-23 F班(他runでevidence中。X runner起動が重ならないよう`tasklist`で確認、全体150秒間隔)、SYNC-26。あなたの所有=AI島run dir(明示コマンドのみ)、`docs/research/AI-ISLAND-FORM-PRODUCTION-01/{RECONSUME_01,PREP_06}.md`、`..._DELEGATION_06.md`(+check.json)、`docs/pm/RESULT_PACKET_AIF6.md`(gitignore)。Productionコード編集禁止。SSOT権なし。pathspec付きcommit、`git push origin HEAD:main`。時間見込み約1h。

## 禁止

- `record_human_approval`・assemble・player・公開(**HR承認後の別委任**)、音声再生成、本文・①②③・文法の変更、Gate緩和、禁止Git操作。起動間隔150秒以上・同一run 5分3回禁止、有料前に`stop_scope_check`+必要性1行。

## 実施事項

1. `reconsume`(`IMPL_B_01.md` §3手順): 両levelで`--user-ref <USER(SLOT-23)>`付きで実行。確認: `confirmation_id`/`origin`保持、hash chain継続、Std ②2件が`items`へ(③5件=`CATEGORY3_HIGHLIGHT`)、`display_spec`付与、ユーザー確定の英語・訳・区分は逐語不変(実行前後のdiff)、文法0件維持。確定Redundancy QAの実行有無・結果(NGなら停止し報告)。
2. Std Part 1生成: `--stage study_text --level a2`(①3+②2、日本語解説、Std Head)、T1訳。品質検査PASS、Adv Part 1(既存)不変(sha)。費用記録。
3. ハイライト解決の事前確認(API 0): 両levelで`resolve_x_highlights`相当をdry-run(ツールがあれば`offline_resolve_01.py`)→ISSUE 0、NOTICE(Std `Strategy`再配置)を記録。
4. 承認後手順書`PREP_06.md`: `record_human_approval`(両level or 片方)→`--stage assemble --level both`→`--stage player --level both`→標準builder `er019_family_x_listening_page_01.py`(check_page+G3+Part 1個数+Part 2一致)→公開`user_test/family_x_ai_island_form_01/index.html`→page_verify、の各コマンドと所要時間、API 0の確認。
5. commit: `AI-ISLAND-FORM-PRODUCTION-01 委任_06: 新表示仕様の適用準備(reconsume・Std Part 1生成・ハイライト解決確認、HR承認後の手順書、¥<費用>)`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: 有料=対象。

## 事前指定Read一覧

`IMPL_B_01.md`(§2/§3)、`IMPL_C_01.md`、`docs/pm/RESULT_PACKET_S23{B,C,M}.md`、`docs/research/AI-ISLAND-FORM-PRODUCTION-01/{RESOLUTION_01,BUILD_01}.md`、`er128_kp_confirmed_content_01.py`(Grep `def cmd_reconsume|reconsume` ±10)。

## 報告

`RESULT_PACKET_AIF6.md`: (0)T-0、(1)reconsume結果(不変性diff)、(2)Std Part 1生成結果・費用、(3)解決確認、(4)承認後手順、(5)判断候補、(6)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。