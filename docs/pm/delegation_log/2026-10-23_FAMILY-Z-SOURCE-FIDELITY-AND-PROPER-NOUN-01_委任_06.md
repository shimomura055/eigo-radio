FABLE-DELEGATION-MARKER: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01-委任_06-PHASE4-20261023

# 委任_06: Phase 3のFable受入反映 + Phase 4『開いた窓』Standard/Advanced完成候補の正式Production制作 + 比較試聴ページ公開

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_委任_06.md`(N≈341〜351、先頭行MARKER一致確認)。
2. ACTIVE_TASK.md: 別agent2本(FAMILY-X-NEWS-2ARTICLES-E2E-02=X音声TTSあり、FAMILY-Y 委任_04=DEV Trial)が並行。編集直前に再読込し、本管理ID行のみ更新。**TTS段の直前/直後に「有料run(TTS)進行中/終了(時刻)」を記し、他agentの行に「有料run(TTS)進行中」があればTTS段のみ待機(5分間隔・最大30分)**(Master Audio Store manifest非atomic)。

## 1. Fable受入判定(Phase 3、先にSSOTへ反映してcommit)
- **原作忠実性 包括対策v1(修正版B全体)+固有名詞ルール(keep_name共通機構)= PRODUCTION_WIRED(Family Z、Fable受入2026-10-23)**。根拠: 正式経路への実装(Seed essentials検査=LLM呼出前STOP、R0/R1/R2/Std引数渡し+入力指紋+provenance、keep_name上書き、Framton化、forbidden_names「ヴェラ」除去、CPチェックリスト機械生成+処置規則、新Validator/LLM検査/retry/HRなし[test固定])/Trial Promptとの一致(R0 byte一致、R1/R2は意図した2差分のみ、Std byte一致、Melos byte一致)/正式経路runtime evidence(`run_sf_prod_01`: 全段で種明かし保持、Framton・Veraのみ、既存決定論検査PASS、CP重大0・軽微0、resume再生成0・費用0)/新規test 24・Z pytest 249 PASS/費用12.63円/X・A・B・C無変更。
- 全回帰のfailed 3は本変更起因ではない: 2件はFamily Y Trialの新規DEVファイル(`er110_family_y_text_trial_01*.py`)が`er053`/`er095`をimportしたことで既存の静的隔離testの許可リスト外になったもの、1件は並行runによる共有ログ変動(単独再実行PASS)。→ **本委任の最後に扱う**(§5)。
- OPEN-465=`PRODUCTION_WIRED(配線)+OPEN_WINDOW_PHASE4_IN_PROGRESS`、OPEN-464=`PRODUCTION_WIRED`、CURRENT_SPEC両Status行、DECISION_LOG受入エントリ、UDR #164配線完了追記、REPORT_LEDGER。

## 2. Phase 4: 『開いた窓』完成候補(正式Production経路、`run_sf_prod_01`を継続)
- 本文確定: `writer/r2.md`(Adv)/`writer/std.md`(Std)(再生成しない)。
- 実行: `plan`(話者判定: Framton/Vera/Mrs. Sappleton/men。Voice割当=正式表の割当関数[Vera=Zephyr/Framton=Algieba/Mrs. Sappleton=Kore/men=Schedar、Narrator=Aoede、Adv補助=Charon]、`voice_assignment.json`記録)→`support`(Std JA lint含む。Veraが禁止名に当たらないこと)→`kp`(KPFT 3件・CMU gate・KP3V)→`tts_b1b`/`tts_a2`(**会話速度仕様v2**=Std会話減速なし/Adv会話tempo1.06、Narrator従来。`speed_profile`記録を確認)→`gate`→`assemble`→`pages`→`page_verify`。`--mode real`、`TTS_EXECUTION_MODE=STANDARD`、`--approved-budget-jpy 300`、STOPセンチネル確認rc=0。**有料runの再起動は1回も許可しない**(rc≠0なら原因・証拠・選択肢を報告して終了。ただしHR Lock到達で止まった場合、原因が既知のValidator不具合など承認済み範囲で自律解決できるものは原因分析→修正→再検証まで行い、再開が必要ならその旨をRESULT_PACKETに書いて終了=Fableが再開を判断)。
- Store再利用: 本文が変わったsegmentは新規生成、不変segment(Preview/Comment/KP等で一致するもの)は再利用可。旧run(`run_e2e_01`)の音声は参照のみ。
- 費用見込み: 音声段約35〜60円(run_e2e_01実績52円から本文分を除く)。上限100円(超過見込みなら開始前STOP)。本日累計は約200円+並行(X 2記事≤300、Y≤250)で日次1,000円内であることを確認。
- 品質確認(Fable受入資料): (a)原作の重要要素・伏線・種明かし・人物名の保持(本文は確定済みだが、Preview/Comment/In One Line等がネタバレ[spoiler lint]や矛盾を起こしていないか)、(b)結末直前の不要な付加文なし(CP記入済み)、(c)Veraの発音(PNAP: アラーム発火・供給の有無、ASR転写、HR状況。Ledger未登録のため新規固有名詞として扱う)、(d)会話速度v2の適用証拠(speed_profile、長さ比)、(e)Voice割当・音声QA・ASR・gate・assembleのPASS、(f)既存承認基準(Audio Validation、KP3V、HR Lock 0、PASS_WITH_WARNING箇所の列挙)。
- 比較試聴ページ: **新ディレクトリ `user_test/family_z_open_window_02/`**(現行公開版`family_z_open_window_01`は速度v2適用済みの旧本文版としてそのまま残す)。Std/Adv切替、全編通し再生、パート別再生、全スクリプト(Preview/Comment/本文/In One Line相当)、KPと意味・解説、開発者向け情報非表示。既存のZページ生成(`pages` stage)を使う。commit/push後にHTTP 200+Playwright全audio実再生+ページ標準検査。
- 証跡: `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/PHASE4_RESULT_01.md`(品質確認(a)〜(f)、費用出典、所要時間、Trial B/速度v2/固有名詞/包括対策の統合状況、Production影響範囲[melos無変更])。

## 3. SSOT/Git(Phase 4後)
- OPEN-465=`PHASE4_COMPLETE_CANDIDATE_PENDING_USER_LISTEN`、OPEN-428(『開いた窓』)=`USER_LISTENING_PENDING(完成候補02)`、UDR #157を「完成候補02の試聴PASS/NG」へ更新(URL付き)、DECISION_LOG、REPORT_LEDGER。commitは論理単位(受入SSOT / Phase 4 run証跡+pages / SSOT)、明示add(mp3のみ、wavなし)、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 4. 禁止
- 本文・台詞の手修正、Prompt/コード/仕様の変更(Phase 3で配線済みのものを使う)、melos成果物・公開ページの変更、`family_z_open_window_01`の上書き、有料run再起動、HR/STOP迂回、Pro系TTS等の仕様変更、追加Trial。

## 5. 全回帰(最後に)
- `run_project_regression.py`単独実行。failed 3の内訳を再確認: (i)`er003_test_kp_gloss_alignment_stop_paths T3(r)`は単独再実行でPASSなら「並行run起因」と記録。(ii)`er053...after_c2`/`er095...production_py_in_c1`は**Family Y側のDEVファイルのimportが原因**。該当testの意図(Production moduleを誰がimportしてよいか/許可リストの趣旨)を読み、(α)Trial/DEV用ファイルのimportが許容される設計なら許可リストに`er110_family_y_*`を追加(test修正のみ、理由をコメント)、(β)Productionモジュールの隔離保護が趣旨でDEVからのimportも禁止すべきなら修正せず「Family Y側で回避が必要」と報告(Fableが判断)。FAMILY-Y agentが作業中なら、そのファイルは触らない。
- 結果(failed/errors)を報告。自分起因0を確認。

## 6. 報告(docs/pm/RESULT_PACKET_FZSF6.md、同内容を最終報告で)
(1)Phase 3受入のSSOT反映 (2)Phase 4実行結果(stage別、Voice割当、speed_profile、KP、PNAP/Vera、HR、gate、assemble) (3)品質確認(a)〜(f) (4)試聴URL+再生検証 (5)費用(出典)・所要時間・量産単価への影響 (6)全回帰結果と隔離testの扱い (7)commit・raw URL・SSOT (8)残存リスク・残件 + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。