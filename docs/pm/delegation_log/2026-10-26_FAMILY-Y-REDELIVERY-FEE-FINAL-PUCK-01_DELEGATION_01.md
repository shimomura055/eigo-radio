## 管理ID

FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01(準備・棚卸し。read-only・API 0。Family Y『宅配の再配達は有料にすべきか？』Std/Adv完成版[Voice 1=Puck、Advanced Comment 2なし]制作の先行作業: 再利用可能音声の棚卸し・Comment 2削除配線の照合・制作計画。実際の生成・組立・公開は委任_02[Y Voice配線のPRODUCTION_WIRED確認後]で行う)。並行タスク衝突確認: 並行Agent 6件(FAMILY-Y-VOICE-TABLE-PRODUCTION-WIRING-01 委任_01[`er121_*.py`編集中+`er121_output/family_y_production_01/<slug>/run_voice_puck_ev_01/`に有料run中]、PM-SSOT-SYNC-06[SSOT編集中]、TTS-RETRY…01X/Y/Z[read-only]、KP Trial)。あなたは**コード・run dir・SSOTを一切編集しない**。所有ファイル=`docs/research/FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/{INVENTORY_01,COMMENT2_WIRING_CHECK_01,PLAN_01}.md`、`inventory_01.json`、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01_{USER,DELEGATION_01}.md`(+check.json)、`docs/pm/RESULT_PACKET_YRF1.md`。git index.lock競合時は10秒待って再実行(最大3回)。

## 性質/到達上限Status/禁止事項

- 性質: 準備調査(read-only)。到達上限Status=計画確定(PLAN_READY)。
- 禁止: 有料API・TTS・音声生成、コード/SSOT/run dir/公開ページの編集、`git add -A/-u/-f/-N`・amend・rebase・force push・stash・clean・reset --hard・checkout -f・`git checkout -- <file>`。推測禁止(根拠ファイル:行を付ける。不明は「不明」)。
- 費用/日次: JPY0。
- Opus独立技術レビューGate(11-3): 非該当(調査)。
- 時間見込み: 約1h(棚卸し25分/Comment 2照合20分/計画15分)。並列化: 本委任自体が並列先行作業。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1/T-2/T-3)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: 読込効率=Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。修正範囲の線引き(PM_GOVERNANCE 11-8)=範囲外は受理面・閾値・方式の新設/拡大、範囲内は承認済み仕様・設計原則との矛盾(仕様文と実装の乖離・論理的に不整合な比較)の是正とそのRegression・検証。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。
T-2(2026-09-25、`PM-GOVERNANCE-DEV-TTS-STANDARD-SYNC-REMINDER-01`、既存ガバナンスPM_GOVERNANCE.md 7-1/7-2の再確認・運用是正であり新ルールではない、全委任で常時有効): TTSを伴う委任は、正式リリース前である限り`TTS_EXECUTION_MODE=STANDARD`を実行コマンドに明示する。Batchは7-2の例外条件に該当する理由を委任文に明示した場合のみ使ってよい(`--batch-reason`等で理由を明記)。既存の`T-1`(施策1 Read Efficiency Trial用ラベル)とは別ラベルであり、ラベルの意味を混同しない。(本委任はTTSなし。委任_02の計画に反映)
T-2追記(2026-09-25、`NEWS-E2E-PRE-KEYPHRASE-CLOSEOUT-02`、PM_GOVERNANCE.md 7-5、予算逸脱再発防止): TTSを伴う委任は実行前に(1)差分[変更箇所のみ]再生成が対象コード上で実際に可能か確認、(2)既存の音声再利用キャッシュの有無を確認、(3)`--budget`/`--budget-jpy`等が存在すればタスク固有の承認上限に合わせて明示、(4)想定外の全再生成と判明した場合はAPI実行前にSTOPし報告、の4点を必須とする。(本委任で(1)(2)を事前確認し、PLAN_01に結果を書く)

T-0補足: `py docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs\pm\delegation_log\2026-10-26_FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01_DELEGATION_01.md` をN=657から順に試し、先頭が「## 管理ID」+「FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01」で始まるものを採用(`--index -1`不可)。ユーザー指示原文(下記全文)を`..._USER.md`へ逐語保存。

## ユーザー指示(原文)

# 【改訂指示】Family Y『宅配の再配達は有料にすべきか？』完成版制作・公開

**対象：Family Y『宅配の再配達は有料にすべきか？』Standard／Advanced**

**目標：承認済みの最新Production仕様を反映した完成版を制作し、ユーザー最終試聴へ提出する。**

## 1. 今回反映する2つの正式仕様

### ① Voice 1＝Puck

ユーザー正式承認済み。

- Voice 1はAlgiebaからPuckへ変更。
- Family Yの男性候補No.1はPuck、No.5はIapetus。
- Family ZのVoice候補は変更しない。

Family YのVoice変更がPRODUCTION_WIREDに到達したことを確認し、**本記事のVoice 1音声を正式Production経路でPuckを使って再生成すること。**

### ② AdvancedのComment 2削除

ユーザーによれば、AdvancedのComment 2削除は既にPRODUCTION_WIRED済み。

CURRENT_SPEC・承認記録・正式Productionコード・runtime evidenceを照合し、実際に反映されていることを確認する。

**Advanced完成版ではComment 2を含めない。**

- 音声だけでなく、スクリプト・組立・公開ページからも除外する。
- Comment 2削除によって前後の接続、内容の流れ、再生順序に不整合が生じないことを確認する。
- Standardには、承認されていない構成変更を加えない。

既に配線済みである場合、同じ機能を重複実装しない。

## 2. 制作方針

既存の確定済み記事本文・構成・3人の人物像・Human Review結果を最大限再利用する。

変更対象は原則として以下に限定する。

1. Standard／AdvancedのVoice 1音声をPuckで再生成。
2. AdvancedのComment 2削除が完成版全体に反映されていることを確認。
3. 上記変更に必要な組立・メタデータ・公開ページの更新。

Voice 2／3、その他の正常な音声は原則再利用し、不要な再生成を行わない。

ただし、再利用によって最新の承認済みProduction仕様や品質検査と不整合が生じる場合は、必要な部分のみ再生成・修正すること。

## 3. Production実行・品質検査

Standard／Advancedそれぞれについて、正式Production経路で完成版を組み立てること。

- Voice 1のactual voiceがPuckであることをruntimeで確認。
- 現行の正式TTSモデル・Style・速度・Retry／Fallbackを使用。
- ASR、発音、内容一致、繰り返し、不自然な長ポーズ、速度、音量など、既存の必須品質検査をPASS。
- AdvancedのComment 2が音声・本文・公開ページのいずれにも残存していないこと。
- Comment 2削除に伴う音声順序・つながりを確認。
- Key Phrase・解説・既存Human Reviewの確定内容と最終成果物が一致すること。
- retry／fallback／regeneration／resumeでも旧Voiceや削除済みComment 2が復活しないこと。

Family YのChunk分割については、現在の1段落本文構成を維持する。Chunk発火のために本文を無断変更しない。

## 4. 完成版の公開

Standard／Advancedの両方を試聴できる完成版ページを公開する。

ページには、通し再生、パート別再生、確定スクリプト、Key Phrase・解説等の既存仕様に沿った学習情報を掲載する。

再生リンク・音声参照・スクリプトの整合を確認する。

公開後、ユーザーへ完成版URLを報告すること。

## 5. 作業順序・QCD

Family Y Voice 1＝PuckのProduction Wiringは先行条件とする。

Comment 2削除の既存配線確認、使用可能な音声の棚卸し、組立・公開準備などの独立作業は並列で進めてよい。

品質 ＞ Delivery ＞ 量産単価。

既存の正常な成果物を再利用し、不要なTrial・音声再生成・待機を行わない。

承認済み予算・日次1,000円（JST）を守る。

## 6. 完了条件・報告

Fable独立受入のうえ、以下を簡潔に報告すること。

1. Family Y Voice 1＝PuckのPRODUCTION_WIRED確認
2. Advanced Comment 2削除のPRODUCTION_WIRED確認
3. Standard／Advancedの正式Production生成・組立結果
4. Voice 1のruntime evidence（Puck使用）
5. Advanced Comment 2の完全除外証拠
6. 品質検査・再利用状況・追加費用
7. 完成版の公開試聴URL
8. SSOT／Git反映と残Open Item

**最終Statusは「完成版・ユーザー最終試聴待ち」。**

ユーザーによる試聴承認を先取りして完成確定・Closeoutしないこと。

---

**今回の最終成果物は、Voice 1＝Puck、Advanced＝Comment 2なし、という2つの正式仕様を反映した『宅配の再配達は有料にすべきか？』のStandard／Advanced完成版である。**

(原文ここまで)

## 本委任(準備)の調査項目

1. **既存成果物の棚卸し(INVENTORY_01)**: `er121_output/family_y_production_01/redelivery_fee/`配下の全run dir(run_01、`run_ev_01`[Chunk evidence、dev入力=再利用不可]、`run_voice_puck_ev_01`[並行Agentが生成中。存在すれば中身を読み取りのみで記録し、Voice 1 Puck音声の再利用可否を判断材料として書く]等)について、レベル別(a2/b1b)に全segment(導入/Comment 1/Lead/Comment 2[a2のみ正規]/Voice 1〜3リード文/Voice 1〜3本文/Comment 3/Tension+Closing/Key Phrase・解説/定型音声)の: 最終status(OK/NG/HR)、使用voice(actual voice記録フィールド)、生成日時、Style/減速/モデル、QA結果、asset hash、公開ページ(`user_test/family_y_production*/redelivery_fee*`)が参照しているファイル。**Voice 1由来の全音声(本文・リード文等Voice 1の声で読まれるもの全て)**を特定し「Puckで再生成が必要」の一覧を作る。Voice 2/3・導入・Comment・Closing・KP解説は「再利用候補」とし、再利用の障害(承認済み最新仕様との不整合: Std減速方式・Style profile固定記録・asset hash stale・Comment 2削除後の順序・Chunk Std拡張後のGate要件`_segment_missing_mandatory_a2_slowdown`等)を既存Gate関数の要件とconcretely照合して記録。
2. **Human Review確定内容**: redelivery_feeのKP/単語/文法HR選択結果(`er119_kp_human_review*`成果物・run_01内の選択記録・HR Lock)の所在と内容を記録(再利用対象。変更不可)。
3. **Comment 2削除の配線照合(COMMENT2_WIRING_CHECK_01)**: `CURRENT_SPEC.md:3080-3090`の「PRODUCTION_WIRED(限定: 組立・ページ・resume経路はruntime確認済み。初回生成stage[導入文3 call]は次のY新規記事で確認)」を、`er121_family_y_structure_01.py` `Y_SUPPORT_NAMES`、`er121_family_y_audio_01.py`/`er121_family_y_runner_01.py`/ページ生成/manifestの各経路、`docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/{DESIGN_01,EVIDENCE*}.md`のruntime evidenceと照合。本記事(既存run_01はComment 2ありで生成済み)を**resume/再組立**した場合にb1bのcomment_2が音声・スクリプト・ページ・manifest・再生順序から除外されるか(「旧runのcomment_2成果物は無視」の実装箇所:行)、Advanced Previewの`advanced_preview_role`がrun_01の既存Preview音声(Comment 2へ言及している可能性)に影響するか=**Preview再生成が必要か**を判定し、必要ならPuck再生成に加える。限定事項「初回生成stage未確認」が本記事(既存記事の再組立)に該当するかを明記。
4. **制作計画(PLAN_01)**: 委任_02で実行する正式CLIコマンド列(run dir方針: run_01を上書きせず`run_02`を新設してrun_01のcacheを正式resume機構で再利用できるか/`--only-segments`でVoice 1関連のみ再生成できるか[T-2追記(1)(2)]、`--budget-jpy`の有無、stage順[tts_a2/tts_b1b→gate→assemble→pages→page_verify]、Comment 2除外の確認コマンド、Puck actual voice確認手順、公開先URL規則)、費用見積(Voice 1関連segment数×Trial実績2.34円/take×retry見込み+KP解説等の再生成が必要な場合の追加)、所要時間、並列化可否、リスク(Voice 1 Puckでのリード文・本文の長さ/Repetition QA、Comment 2削除後のpause、retry/resumeで旧Algieba cacheが復活しないことの確認方法=cache keyにvoiceが含まれるか:行)。**計画は並行Agent(FAMILY-Y-VOICE-TABLE)の変更後コードを前提にせず、現HEADで確認できる事実と「配線完了後に再確認する項目」を分けて書く。**

## KPI provenance欄

該当なし(調査のみ)。

## Opus台帳更新

該当なし。

## 事前指定Read一覧

- `CURRENT_SPEC.md:3078-3095`(Comment 2削除節)、Grep `Family Y` + `公開|user_test|pages|page_verify` → ±5(公開URL規則)
- `er121_family_y_structure_01.py`: Grep `Y_SUPPORT_NAMES|advanced_preview_role|comment_2|segment` → ±20
- `er121_family_y_runner_01.py`: Grep `def stage_|only_segments|--run|resume|cache|reuse|pages|page_verify|budget` → ±20
- `er121_family_y_audio_01.py`: Grep `reuse|cache_key|reused_from_previous_run|voice|comment_2|manifest|load_results` → ±20
- `er003_v1_n3_01_assemble.py`: Grep `_segment_missing_mandatory_a2_slowdown|_segment_asset_hash_stale` → ±30(再利用時のGate要件)
- `docs/research/FAMILY-Y-FEEDBACK-COMMENT2-PAUSE-01/DESIGN_01.md` 全文、同dir `EVIDENCE*`/`RESULT*`: Grep `runtime|resume|comment_2|Preview` → ±10
- `er121_output/family_y_production_01/redelivery_fee/run_01/{a2,b1b}/results*.json`・`manifest*.json`・`audit/`配下の一覧(Glob→必要ファイルのみRead。wav不読)
- `user_test/`配下のredelivery_fee公開ページ(Glob `user_test/**/redelivery*`、`user_test/family_y*/**/index.html`) → audio参照一覧のみ抽出
- `OPEN_ITEMS.md`: Grep `redelivery|OPEN-527|OPEN-533|Comment 2` → 該当行のみ

## 事前指定Grep一覧+追記位置・更新位置の手順

- Glob `er121_output/family_y_production_01/redelivery_fee/*/` → run dir一覧
- Grep `Algieba|Puck` in `er121_output/family_y_production_01/redelivery_fee/run_01/**/*.json` → Voice 1音声の特定
- Grep `comment_2` in `er121_output/family_y_production_01/redelivery_fee/run_01/b1b/**/*.json` と公開ページhtml → 残存箇所一覧
- Glob `er119_output/**/redelivery*`・`er121_output/**/redelivery_fee/**/human_review*`・`**/kp*select*` → HR確定内容
- 成果物は`docs/research/FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/`に新規作成

## 実行コマンド全文

- `py docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\2026-10-26_FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01_DELEGATION_01.md --json-out docs\pm\delegation_log\2026-10-26_FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01_DELEGATION_01.md_check.json`
- `.venv\Scripts\python.exe er121_family_y_runner_01.py --help`(引数名の実値確認のみ。実行はしない)
- Secret grep: `git diff --cached | Select-String -Pattern "sk-[A-Za-z0-9]{20,}|AIza[0-9A-Za-z_-]{30,}"` → 0件

## SSOT追記文

SSOT編集権なし。RESULT_PACKET_YRF1.md(9)に「OPEN起票候補(あれば)」のみ文案。

## Git(明示add対象・コミットメッセージ・trailer)

- add対象: `docs/research/FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/{INVENTORY_01,COMMENT2_WIRING_CHECK_01,PLAN_01}.md`、`inventory_01.json`、`docs/pm/delegation_log/2026-10-26_FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01_{USER,DELEGATION_01}.md`、`..._DELEGATION_01.md_check.json`。RESULT_PACKETはaddしない。
- commit message: `FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01 委任_01: 完成版制作の準備棚卸し(再利用可能音声・Comment 2削除配線照合・制作計画、read-only、API 0)`
- trailer: `Delegation: FAMILY-Y-REDELIVERY-FEE-FINAL-PUCK-01/01`
- push: `git push origin HEAD:main`(non-ffなら`git fetch origin`→`git merge --no-edit origin/main`→push。競合はSTOPし報告)。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_YRF1.md`: (0)T-0結果・index、(1)run dir一覧と各segmentの状態表(a2/b1b)、(2)Puck再生成が必要なsegment一覧(id・長さ・理由)と再利用候補一覧(再利用障害の有無・根拠:行)、(3)HR確定内容の所在、(4)Comment 2削除の配線照合結果(経路別○×、Preview再生成要否、限定事項の該当)、(5)制作計画(コマンド列・費用見積・時間・リスク・配線完了後の再確認項目)、(6)判断候補(あれば。例: 再利用不可の音声が多く費用が見積を大きく超える場合)、(7)RESULT_PACKET必須4行+「判定整合: 重大NG=<なし|あり>」1行、(8)一覧外Read、commit hash、raw URL。末尾に10行以内の要約。