FABLE-DELEGATION-MARKER: PNAP-KHAITE-B-TIER-APPROVAL-委任_03-20261022

管理ID: PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01 委任_03(OPEN-450)。目的: ユーザーが承認したKhaite→「Kate」のB階層(媒体由来)発音供給を、正式の承認CLIで人承認として登録し、後続の合同runtime evidenceで供給発火を観測できる状態にする。費用0(API呼出禁止)。Production .py/Prompt編集禁止(CLIの実行のみ)。並行agent(KP3V/KPFT/JRE)はLedgerファイルを触らないが、共有SSOTは `git status`→再Grep→自分の行だけ→即commit。

## ユーザー承認の原文(逐語、2026-10-22、chat)
「Khaite → Kate の登録を承認する」
(Fableが直前に提示した問い: 「Khaite→「Kate」の綴り供給を、B階層(媒体由来)として承認登録してよいか … 推奨: 承認」に対する回答)
→ `docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01_KHAITE-APPROVAL_USER.md` に、上記の問いと回答を逐語で保存(承認者=ユーザー、日時=2026-10-22 JST、媒体=chat)。

## 作業
1. 読む: `docs/research/PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01/IMPLEMENTATION_DESIGN_01.md`(B階層・承認CLI・Ledger additive keys `evidence_tier`/`human_approved`/`tts_respelling` の節)、`RUNTIME_EVIDENCE_02.md`(Khaiteの扱い)、`er103_pronunciation_approve_cli_01.py`(使い方・引数・検証)、`er103_pronunciation_tts_supply_01.py`(供給条件)。Khaiteの出典(媒体由来の根拠: 「Kate」と読む根拠となるメディア/ブランド公式情報)は Stage 2 Trial の記録(`docs/research/PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02/STAGE2_TRIAL_RESULT_0[123].md`・`STAGE2_TRIAL_CLOSEOUT_01.md`)からGrepで特定し、URL/引用を登録のsourceに使う(出典が記録に無ければ「ユーザー承認(chat)のみ、媒体出典は記録なし」と正直に登録し報告)。
2. 承認CLIで登録: 語=Khaite、供給綴り=Kate、tier=B(媒体由来)、human_approved=true、approver=ユーザー(shimomura)、approved_at=2026-10-22 JST、source=上記、備考=「UDR回答、chat承認」。CLIがdry-run/検証機能を持つなら先に実行。登録後、Ledgerの該当entryを読み戻してキーと値を報告(推測禁止)。CLIが想定どおり動かない場合は修正せずにFableへ報告(Production module編集禁止)。
3. 供給が発火する条件の確認(読み取りのみ): `er103_pronunciation_tts_supply_01.py` の判定で、登録後にX/Zのrun scope内でKhaiteを含むTTS入力がKateに置換される経路が通るかを、既存unit test(`er103_pnap_wiring_test_01.py`の承認CLI→置換→継承再判定)を実行して確認(API 0)。Khaiteを含む記事と既存run dir(例: `er019_output/family_x_audio_production_wiring_01/pnap_evidence_01__small_bag__run_02`、元記事 small_bag の a2/b1b 本文の所在)を特定し、合同evidenceで使えるrun dir・本文pathを報告。
4. SSOT: `docs/pm/USER_DECISION_REGISTER_01.md` のKhaite承認の問い(Grepで該当番号を探す。無ければ新番号で「問い+回答」を追加)を回答済みに、OPEN-450に「B階層 Khaite→Kate 人承認登録済み(2026-10-22、ユーザー承認)」を1行追記、`DECISION_LOG.md`末尾に短いエントリ、`docs/pm/REPORT_LEDGER.md`1行。
5. T-0保存: `docs/pm/delegation_log/2026-10-22_PROPER-NOUN-PRONUNCIATION-ALARM-POLICY-PRODUCTION-01_委任_03.md`(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、末尾から探索し本文先頭marker `FABLE-DELEGATION-MARKER: PNAP-KHAITE-B-TIER-APPROVAL-委任_03-20261022` 一致で確定)。
6. commit(自分のファイル+Ledgerデータファイルのみ `git add <file>`、`-A/-u/-f`禁止)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。index.lock競合時は30秒待って再試行、3回失敗ならFableへ報告。

## 報告
`docs/pm/RESULT_PACKET_PNAP3.md`に4行+判定整合行。本文: 登録したLedger entry(読み戻し値)、出典、test結果、合同evidence用のKhaite記事・run dir・本文path、commit hash、raw URL。