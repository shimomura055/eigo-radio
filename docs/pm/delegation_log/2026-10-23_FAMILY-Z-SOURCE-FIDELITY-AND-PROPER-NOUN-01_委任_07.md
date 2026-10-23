FABLE-DELEGATION-MARKER: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01-委任_07-STD-TTS-ADVANCE-BERTIE-PREP-20261023

# 委任_07: 『開いた窓』Phase 4 — Std(tts_a2)先行実行(Bertie HR Lockはユーザー判断待ち)+ Ledger登録候補の準備 + LR表示仕様の確認。コード変更0・HR/STOP迂回0。

前提読込: `docs/pm/RESULT_PACKET_FZSF6.md`、`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/PHASE4_RESULT_01.md`。

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_委任_07.md`(直近保存のindexは340=委任_06。本文はその後の343〜346付近、先頭MARKER一致で特定)。
2. ACTIVE_TASK.md: 並行agent 2本(FAMILY-X-NEWS-2ARTICLES-E2E-02 委任_02=記事A TTSあり、FAMILY-Y 委任_05=Trial TTSあり)。編集直前に再読込・自分の行のみ。**TTS開始前に他行「有料run(TTS)進行中」を確認、あれば5分間隔・最大30分待機**。自分のTTS開始/終了を記す。

## Fable判定(記録用)
- Bertie HR Lock 2clip: 原因はPNAP P-02の想定内ケース(CMU収録人名が引用符直後・文頭で固有名詞証拠を持てない)。解決策(A)Ledger B階層登録は仕様上「人承認」(DECISION_LOG 2026-10-22 PNAP 委任_03、UDR #150のKhaite前例)のため**ユーザー判断待ち(UDR起票はFableが行う)**。HR Lockの手解除(C)・PNAP証拠源拡張(B)・er109 pair追加(D)はいずれも維持境界/受理面拡大のため本委任では行わない。
- 試聴ページ出力先: `e2e_pages_dir`のregistry変更はしない。ユーザー指示「既存完成音声はQA合格・公開確認後に安全に差し替え」に従い、QA(gate/assemble)PASS後に現行 `family_z_open_window_01` を正式pagesで差し替える(本委任ではpages未実行)。

## 1. Std(tts_a2)先行実行
- `run_sf_prod_01` で `tts_a2` を**1回だけ**起動(`--mode real`、STANDARD、`--approved-budget-jpy 100`は本Phase 4音声段合計、現時点37.20円)。STOPセンチネルrc=0確認。Bertie台詞を含むclipでHR Lockになり rc≠0 で止まる見込み(想定内)。再起動しない。
- 記録: OK clip数/STOPPED clip数とclip ID、HR Lock理由(Bertie以外のHR Lockが出たら原因を個別に分析)、Std会話速度v2の適用(`std_dialogue_none`/`std_narrator_slow6` の記録と、長さ比の実測:同一台詞のAdv tempo1.06版との秒数比較が可能なら)、LR発生箇所、PASS_WITH_WARNING、費用。
- 結末文 `Making up stories in seconds was Vera's special skill.` のASR結果を明記。

## 2. Bertie Ledger登録候補の準備(登録は実行しない)
- 承認CLI `er103_pronunciation_approve_cli_01.py` の仕様を読み、「Bertie」をB階層(またはこのケースに適切な階層)へ登録する場合の入力(surface=bertie、綴り供給なし=ASR受理証拠のみ、出典=原作本文 Saki "The Open Window" の歌詞 'Bertie, why do you bound?'、Seed source_essentials内の該当有無)を `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/BERTIE_LEDGER_CANDIDATE_01.md` にまとめる。CLIに `--dry-run` 相当があれば実行して結果を貼る(`--apply`は禁止)。
- 登録後の挙動予測: `_noun_checks` にledger_surfaces=['bertie']を与えた結果(受理・類似度0.667、委任_06で確認済み)を再掲し、登録→`--only-clips`(または正規の再開手順)で c14/part3_c2(+Std側該当clip)のみ再生成/再判定できる手順と費用見込みを書く。
- 同じ原作で今後も再発し得る他の名前(Nuttel, Sappleton, Ronnie等)がASRで別語化していないかをアラーム集計から列挙(アラーム「状態9件/報告8件」不一致の9件目も特定)。

## 3. LR表示仕様の確認(API 0)
- Adv `full_story_part3_c12`(`speciality`→`forte`、LR_REWRITTEN)について、既存のpages生成がスクリプト表示にLR後テキストと原稿のどちらを出すか(Family Z既存仕様、melos実例があれば)、`audio_text_deviation`の扱い(Production承認済み挙動)を `PHASE4_RESULT_01.md` に追記。変更はしない。
- `speciality`/`specialty` が er109 v1 の対象外である根拠(pair list/規則の該当箇所 file:line)を1行で記す。

## 4. SSOT・Git
- OPEN-465 Status=`PHASE4_STD_TTS_DONE_PENDING_USER_BERTIE`(内容に応じて)、REPORT_LEDGER。UDRは起票しない。
- 明示add(wav/mp3なし、証跡json/mdのみ)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。

## 5. 禁止
- コード/Prompt/registry変更、`--apply`登録、HR Lock手解除、pages実行、tts_b1bの再実行、有料run再起動、Pro系TTS。

## 6. 報告(docs/pm/RESULT_PACKET_FZSF7.md、同内容を最終報告)
(1)tts_a2結果(表) (2)HR Lock/LR/PASS_WITH_WARNING (3)速度v2 evidence (4)Bertie登録候補(入力・手順・費用見込み) (5)他の名前のアラーム状況 (6)LR表示仕様・er109対象外根拠 (7)費用累計(Phase 4音声段/100、本日Z分)・commit・raw URL (8)RESULT_PACKET 4行+「判定整合: 重大NG=あり/なし」。