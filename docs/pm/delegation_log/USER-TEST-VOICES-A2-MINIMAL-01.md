## 管理ID

`USER-TEST-VOICES-A2-MINIMAL-01`
並行タスクなし(直近commit `27aa6c80`、background agent 0)。報告は`docs/pm/RESULT_PACKET_VOICES_A2.md`(新規)へ。`docs/pm/ACTIVE_TASK.md`は本タスクで上書き。

## 性質/到達上限Status/禁止事項

- 性質: ユーザー実検証用A2 artifactを**最小Token・最小APIコスト**で作る。Priority 1(必達)=B/Voices 3V「AI hiring」の既存B1「When AI Sits Between a Job and a Person」からA2記事を翻案し、音声・Audio Validation・playerまで完成。Priority 2(余力時のみ、Priority 1完了後)=B/Voices 2V「Personalized news」の既存正式User Test対象B1(`b1_2v_v2`)からA2記事+既存validatorまで(新規実装なしで進められる場合のみTTS→Assembly→Audio Validation→playerまで)。
- 到達上限Status: `VALIDATED候補 / USER_LISTENING_PENDING`。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`へ進めない。3V A2の正式仕様化・Production wiring・2V/3V共通汎用化はしない(3V A2は「既存2V A2翻案原則を3V構造へ最小適用するTrial artifact生成」)。
- **1 focused delegation**: Sonnet主体、Opus禁止、不要なagent分割禁止。
- 固定するもの(変更禁止): Theme/Fact/Verified Fact Ledger/3 Voice Cards/3人の立場・経験・価値観・懸念/Tensionの中心/既存voice assignment。新Fact・数字・経験・論点を追加しない。3Vを2Vへ減らさない、役割再設計・新Voice探索をしない。
- A2化で変更してよいもの: 語彙平易化、短文化、構文単純化、1文1アイデア、Spoken-first、難しい説明の日常語化(意味・論点・Stakeholder構造は不変)。
- 禁止(Token最小化): broad Repo audit、無関係な過去Trial調査、新規Theme探索、新規Web Research/Fact収集/Source探索、新規Voice探索、複数候補記事生成、A/B比較、Prompt改善研究、Validator新設、新QA設計、Production汎用化、Production wiring、Productionコード(`er012_b_family_*_production_*.py`/`er012_b_family_production_runner_01.py`/`er003_*`)の改修、all-Family展開、不要なRegression、不要な原因調査、Report増殖、「ついで」の修正、B1改稿、既存B1音声修正、episode全体の無条件再TTS、`git add -A`/`stash`/`amend`、wavのcommit。
- Retry上限: Article=原則1 generation、明確なValidator指摘がある場合のみ最小修正1回(2attemptで成立しなければSTOP)。Audio=失敗segmentの局所retryのみ(既存cascade 標準2+fallback1)、全episode再生成禁止。
- 費用上限: Priority 1 ¥180(記事翻案LLM+validator+Support/KP+TTS+ASR)、Priority 2 ¥150(記事+validator ¥60目安、音声化¥90目安)。Priority 2はPriority 1完了後、残余力がある場合のみ。超過見込みはSTOP。
- **イレギュラー時STOP(独自判断で範囲・仕様・実装を広げない)**: 既存B1とLedgerの不一致/既存3V A2原則(2V翻案原則の最小適用)で処理できない/新仕様決定・新Fact調査・新Voice選定が必要/既存Validatorが構造上使えない/想定外の大規模retry/音声化にProductionコード改修が必要/既存artifact破損/source不足/API費用が想定超過/2attemptで記事不成立/Audio Validationで局所対応を超える問題/他仕様との矛盾。該当時は「何が起きたか/Priority 1・2のどこで止まったか/既に完成している成果物/最小の選択肢/追加Token・APIコスト見込み」だけを簡潔に記録し`USER_DECISION_REQUIRED`で停止(完成済み分はcommit)。
- Output問題時の調査範囲: 今回のA2記事・音声完成に直接必要な局所原因のみ(1 segment TTS失敗/明確な構造エラー/明確なFact mismatch/player局所エラー)。横展開調査(再発性・全体設計・他Family・Validator新設)はしない。必要ならOpen Item候補を1行記録し実装しない。

## 固定ブロック(E-1/D-1/G-1/F-1/T-0/T-1)

E-1: 同一task内で同一ファイルを再読しない(結果を保持し再利用する)。
D-1: Grep→該当行範囲Readを基本とし、全文Readは構造変更時のみ許可する。
G-1: git出力は`--porcelain`/`--stat`/`--short`等で最小化する。
F-1: 自タスクのtranscript退避は不要(Fableが次回委任でコピーを指示する。委任文で明示的に退避コマンドが指定された場合はそれを実行する)。
T-1: 本委任文に列挙した「事前指定Read/Grep一覧」に従うこと。一覧外の追加Readが必要な場合は、その理由をRESULT_PACKETに1行で記録すること。
T-0(2026-09-13、`PM-TOKEN-EFFICIENCY-TOOL-USES-REDUCTION-PRODUCTION-WIRING-01`/`PM-CLOSEOUT-CONSOLIDATION-117`、ユーザー正式採用に伴う恒久運用、施策1 Trial対象タスクに限らず全委任で常時有効): 受領した委任文を`docs/pm/delegation_log/<管理ID>.md`へ保存し、`python docs/pm/tools/check_delegation_prompt.py --file <path> --json-out <path>_check.json`を実行する。結果(PASS/FAIL・reasons)をRESULT_PACKETへ1行記録する(FAILでも作業は継続する。ブロッキングではなく記録用)。

## ユーザー指示(原文)

ユーザー原文(2026-09-16、USER-TEST-VOICES-A2-MINIMAL-01)の要点は上記「性質」欄に転記済み。原文の重要文言を引用:

---
1. 目的: ユーザー実検証用として、既存B1記事からA2版を最小Token・最小APIコストで作成する。Priority 1 — 必達: B / Voices 3V — AI hiring。既存B1: When AI Sits Between a Job and a Person → A2記事を作成し、音声・Audio Validation・playerまで完成させる。Priority 2 — 余力があれば: B / Voices 2V — Personalized news。既存の正式User Test対象B1を基準にA2化する。→ まずA2記事を作成し、Priority 1完了後にToken/API余力があれば音声・playerまで進める。
2. Repo確認済みの前提: B-Family Voices A2の現行正式経路では、既存B1記事を固定入力としてA2へ翻案することが正式仕様である。したがって2V A2については、Theme再調査/新規Research/新規Fact収集/新規Voice設計をやり直す必要はない。既存B1本文・既存Ledger・既存Voice assignmentをreuseする。
3. AI hiring 3V A2の位置づけ: 既存B1 3V記事/既存Verified Fact Ledger/既存3 Voice Cards/既存Tension/既存Voice assignmentが存在する。これらを固定入力として使う。ただし、3V B1 → 3V A2の正式Production A2経路は現時点で正式化済みとは扱わない。今回は、既存2V A2翻案原則を3V構造に最小限適用するTrial artifact生成として扱う。新規Research・Fact収集はしない。
5. Priority 1 Audio: A2記事が成立したら、そのまま音声化する。既存のVoice/intro/outro/Comment/Preview/Key Phrase/Assembly/Audio Validation/player templateを最大限reuseする。Voice探索は禁止。episode全体の無条件再TTSは禁止。失敗したsegmentだけ局所再生成する。
12. Priority 1 受入条件: A2 article完成/3V構造維持/新規Factなし/Ledger逸脱なし/A2 level成立/required existing validator実行/audio完成/Assembly PASS/Audio Validation PASS/player生成/player再生可能/actual voice/model evidence/API cost記録。
13. Priority 2 到達目標: まずA2 article/existing validatorまで。Priority 1完了後もToken/API余力があり、新しい実装なしで進められる場合のみ、TTS/Assembly/Audio Validation/playerまで進める。
17. 最優先原則: 完成品を作るために必要なことだけを行う。Output完成に直接関係しない調査・分析・将来対策へTokenを使わない。イレギュラーを見つけた場合、勝手にスコープを広げず、ユーザーへ簡潔に報告してSTOPする。
---

## 事前指定Read一覧

- `er012_b_family_voices_a2_production_01.py`: Grepで`^def |^[A-Z_]+ = `→関数一覧(既知: `build_adapt_prompt`/`run_writer_adapt`[B1本文固定入力→A2翻案]/`run_evidence_compression`/`run_fact_checker`/`run_ledger_deviation`/`run_five_section_point_qa_monitoring`/`run_analytical_leakage_check`/`run_scaffold_a2`[A2 Support: Preview/Comment/Key Phrase]/`build_a2_voices_timeline`[2V])。各関数のシグネチャ行±5行のみRead(全文Read禁止)。
- `er012_b_family_production_runner_01.py`: 1300-1600行付近(`level="a2"`分岐: A2_SOURCE_DIR/A2_THEME_KEY/A2_OUT_DIR、A2工程の呼び出し順序[翻案→validator群→scaffold→TTS→Assembly→Gate→player]、使用model・reasoning_effort、TTS関数[Voice A/B slowdown]、player生成関数)、627-660行(3V B1のARTICLE_PATH_3V/KP_SOURCE_DIR_3V/OUT_DIR_3V/voice解決)、851行付近(`build_b1_voices_timeline_3v`呼び出し)。**編集禁止、呼び出し方の参照のみ。**
- `er012_b_family_voices_production_01.py`: Grepで`def build_b1_voices_timeline_3v|def build_b1_voices_timeline\b|def generate_voice_body_wide_margin|def resolve_voices|voice_c`→3V timeline構造(A2 3V timelineを新Trial driver内で最小実装する際の参照)。編集禁止。
- `er012_output/editorial_b_voices_3v_person_voice_trial_02/`: Glob`**/article.md`→AI hiring 3V B1本文(runner 627行`ARTICLE_PATH_3V`の実パスで確定)全文。同ディレクトリのGlob`**/verified_fact_ledger*.txt`・`**/voice_card*`・`**/tension*`→Ledger・3 Voice Cards・Tension(固定入力、全文)。
- `er012_output/editorial_b_voices_3v_audio_trial_01/`: `audit/voice_resolution.json`(既存3V voice assignment、全文)、`b1b/b1_support_texts.json`(B1 Support、参考のみ)、`b1b/key_phrases/keywords_canonicalized.json`(B1 KP、A2本文が変わるためA2用KPは`run_scaffold_a2`で再選定)、`b1b/audit/timeline.json`(3V B1 timeline構成: 順序・pause・Voice切替。A2 3V timelineの参照)、`b1b/audit/audio_gate_both_paths.json`(Gate形式)。
- `er012_output/editorial_b_family_voices_a2_production_wiring_01/`: Glob`**/*.json`→2V A2 Production Wiring版の生成物構成(a2/parts.json・timeline・audit・player.html、reuse可能なintro/outro/共通asset[Welcome/Preview intro/KP intro/番号読み/Outro等]の所在)。
- Priority 2用: `er014_output/four_type_observation_01/voices/`: Glob`**/b1_2v_v2/**`および`run2_clean/**/article.md`・`reader_facing_article.txt`→Personalized news正式User Test対象B1本文(`b1_2v_v2`のplayerが指す本文。`web_delivery.json`/`parts.json`から確定)、`research/verified_fact_ledger.txt`(Ledger)、voice assignment(`b1_2v_v2/audit/voice_resolution.json`等)。
- `CURRENT_SPEC.md`: Grepで`B-Family Voices A2|b_family_voices|A2翻案|Voices A2`→A2翻案の正式仕様行のみ(A2 Support言語=日本語・Aoede、日本語タイトル規約、Voice A/B slowdown等)。
- `docs/pm/PM_GOVERNANCE.md`: Grepで`15-8`→費用報告形式。`docs/pm/PM_BRIEF.md`: 135-159行。

## 事前指定Grep一覧+追記位置・更新位置の手順

1. **Priority 1 driver**: 新規Trial driver `er012_b_voices_3v_a2_user_test_01.py`を作成(Productionコードを編集せず、`er012_b_family_voices_a2_production_01`・`er012_b_family_voices_production_01`・registryの既存関数を**import して呼ぶだけ**)。工程: (a) B1本文固定入力→`run_writer_adapt`(既存model/reasoning_effort、1 generation)→(b) `run_evidence_compression`(既存経路で必須なら)→`run_fact_checker`(voice attribution block付き)→`run_ledger_deviation`→`run_five_section_point_qa_monitoring`/`run_analytical_leakage_check`(2V用のsection構造が3V[Point 3件/Tension reflection]と異なる場合は、既存関数に3V引数があればそれを使い、無ければ**該当validatorを3V用に改変せず**「3V構造のため既存2V validatorは非適用、代替として3V B1 audit `required_structure_3v.json`と同形式の構造チェック[3 Voice全員の登場・Point 3件・Tension reflection・In One Line]をdriver内で最小実装」して報告。Fact Checker/Ledger逸脱は必ず実行)→(c) 3V構造維持チェック(3人の立場・名前/呼称・Tensionが本文に存在、新規数字なし=B1本文に無い数字をregexで検出0件)→(d) `run_scaffold_a2`(A2 Support: Preview/Comment/Key Phrase、日本語、既存A2仕様)→(e) TTS: Voice A/B/Cは`voice_resolution.json`の既存assignment、既存A2 slowdown TTS関数(2Vと同じ関数を3人分に適用)、共通asset(Welcome/intro/Outro/番号読み等)は2V A2 Production Wiring版から`.ok`付きコピー→(f) A2 3V timeline: driver内に`build_a2_voices_timeline_3v(parts, voice_a, voice_b, voice_c)`を**最小実装**(`build_a2_voices_timeline`[2V]の構造に、B1 3V timeline[`build_b1_voices_timeline_3v`]のVoice C区間・Point 3・Tension reflectionを加える。pause値は既存値を流用、新規演出なし)→(g) Assembly→既存Audio Validation Gate→既存player template→`web_delivery.json`。出力先`er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/`。**上記(f)で既存2V A2 timeline関数の流用では成立せずProductionコード改修が必要と判明した場合はSTOP(イレギュラー)。**
2. **Priority 2 driver**(Priority 1完了・commit後、余力時のみ): 同driverに`--theme personalized_news_2v`分岐、または`er012_b_voices_2v_a2_user_test_personalized_news_01.py`。既存2V A2正式経路の関数群をそのまま適用(A2_SOURCE_DIRをPersonalized news B1へ差し替え、Ledger=`voices/research/verified_fact_ledger.txt`、voice assignment=既存)。記事+validatorまでで一旦報告用に記録し、余力があれば音声化。出力先`er012_output/user_test_voices_a2_minimal_01/personalized_news_2v_a2/`。
3. SSOT追記位置: `Grep pattern="^## FAMILY-C-SEGMENT-COMMENT-PRODUCTION-WIRING-AND-USER-TEST-INVENTORY-01" path=DECISION_LOG.md`→そのエントリ末尾直後に新エントリ(索引1行も)。`OPEN_ITEMS.md`はpythonでOPEN-151(Voices 2V)行末に「Personalized news A2 Trial artifact結果」を1行追記。AI hiring 3Vの既存Open Itemがあれば(python抽出`3V|AI hiring`)行末追記、無ければDECISION_LOGのみ(新規Open Item起票は不要。Open Item候補があれば1行のみ記録)。`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`末尾に翻案/Supportの行を追加。

## 実行コマンド全文

作業ディレクトリ`C:\Users\tensh\eigo-radio`、pythonは`.venv\Scripts\python.exe`。

T-0:
```
.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file docs\pm\delegation_log\USER-TEST-VOICES-A2-MINIMAL-01.md --json-out docs\pm\delegation_log\USER-TEST-VOICES-A2-MINIMAL-01_check.json
```
Priority 1(記事→validator→音声→player、上限¥180):
```
.venv\Scripts\python.exe er012_b_voices_3v_a2_user_test_01.py --stage all --budget-jpy 180
```
(driverのargparseは`--stage article|audio|all`・`--budget-jpy`・`--only-segments`[局所retry用]を持たせる。実引数全文を報告。)
Priority 2(記事+validator、上限¥60):
```
.venv\Scripts\python.exe er012_b_voices_3v_a2_user_test_01.py --theme personalized_news_2v --stage article --budget-jpy 60
```
Priority 2 音声化(余力時のみ、上限¥90):
```
.venv\Scripts\python.exe er012_b_voices_3v_a2_user_test_01.py --theme personalized_news_2v --stage audio --budget-jpy 90
```
新規数字検出(Fact追加なしの機械確認):
```
.venv\Scripts\python.exe -c "import re;b=open('<B1 article path>',encoding='utf-8').read();a=open('er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/a2/article.md',encoding='utf-8').read();nb=set(re.findall(r'\d[\d,.%]*',b));na=set(re.findall(r'\d[\d,.%]*',a));print('NEW_NUMBERS=',sorted(na-nb))"
```
(`<B1 article path>`は事前指定Readで確定した実パスに置換。`NEW_NUMBERS=[]`であること。)
回帰: 新規テストは作らない(不要なRegression禁止)。既存`er012*_test_*.py`の実行も不要(Productionコード無変更のため)。Productionコード無変更確認: `git status --porcelain er012_b_family_*.py er003_*.py`が空。
Web到達確認(push後、raw.githackはUser-Agent付きGET、CDN遅延時60秒待ち最大3回):
```
.venv\Scripts\python.exe -c "import urllib.request as u;[print(u.urlopen(u.Request(x,headers={'User-Agent':'Mozilla/5.0'})).status,x) for x in ['https://raw.githack.com/shimomura055/eigo-radio/main/er012_output/user_test_voices_a2_minimal_01/ai_hiring_3v_a2/player.html']]"
```
episode mp3 direct URL(`web_delivery.json`の実ファイル名)も同様にGET確認。Priority 2音声化時は同様に2件追加。

## SSOT追記文

`DECISION_LOG.md`(新エントリ):
```
## USER-TEST-VOICES-A2-MINIMAL-01

- 日付: 2026-09-16
- 種別: ユーザー実検証用A2 artifact作成(最小Token・最小API)。Priority 1=Voices 3V AI hiring A2(既存B1固定入力→2V A2翻案原則の3V最小適用Trial、3V A2正式仕様化・Production wiringなし)。Priority 2=Voices 2V Personalized news A2(既存B1→A2翻案、正式2V A2経路の関数群使用)。Productionコード無変更。
- Priority 1: title「<A2 title>」、語数<n>、3V構造維持<3人の呼称>、新規Fact/数字なし(NEW_NUMBERS=[])、Fact Checker <結果>、Ledger逸脱<結果>、その他validator<結果/3V非適用の代替チェック>、Voice A/B/C=<実名>、model=<実名>、TTS <segment数>、局所retry<n>、Assembly <PASS/FAIL>、Audio Validation <PASS/FAIL>、duration <秒>、費用¥<実測>。Status=<VALIDATED候補/USER_LISTENING_PENDING または USER_DECISION_REQUIRED(内容)>。
- Priority 2: <未着手(理由)/記事完成(語数、validator結果、費用)/音声完成(duration、Gate、費用)>。Status=<…>。
- イレギュラー: <なし/あり(内容、勝手に対策せずUSER_DECISION_REQUIRED)>。Open Item候補: <なし/1行>。
- 参照: `docs/pm/RESULT_PACKET_VOICES_A2.md`、commit <hash>
```
索引1行。`OPEN_ITEMS.md` OPEN-151行末: ` 2026-09-16追記(USER-TEST-VOICES-A2-MINIMAL-01): Personalized news A2=<結果・Status>。AI hiring 3V A2=<結果・Status>(Trial artifact、3V A2正式仕様化なし)。`
`docs/pm/ACTIVE_TASK.md`: 固定ヘッダ形式で上書き(APPROVED未配線欄にFamily C 2仕様=`APPROVED_FOR_PRODUCTION / WIRING_INCOMPLETE`[regeneration live evidence未取得]を引継ぎ記載)。

## Git(明示add対象・コミットメッセージ・trailer)

- Priority 1完成時にcommit(Priority 2は別commit)。明示add対象(wav除外、mp3必須): 新規driver、`er012_output/user_test_voices_a2_minimal_01/**`(article.md、parts.json、audit/*.json、key_phrases/**、player.html、web/**/*.mp3、web_delivery.json、audio_validation.json、cost json等)、`DECISION_LOG.md`、`OPEN_ITEMS.md`、`docs/pm/MODEL_ROUTING_TRIAL_LOG.md`、`docs/pm/delegation_log/USER-TEST-VOICES-A2-MINIMAL-01.md`、同`_check.json`、`docs/pm/RESULT_PACKET_VOICES_A2.md`。
- Productionコード・既存B1成果物・`er006_output/`・`er011_output/`の既存M・`docs/pm/ACTIVE_TASK_*.md`/`RESULT_PACKET_*.md`の既存??は触らない。
- コミットメッセージ: `USER-TEST-VOICES-A2-MINIMAL-01 (P1): Voices 3V AI hiring A2 Trial artifact(既存B1翻案、音声・player完成)` / `USER-TEST-VOICES-A2-MINIMAL-01 (P2): Voices 2V Personalized news A2(<記事のみ/音声まで>)`
- trailer: `Task-ID: USER-TEST-VOICES-A2-MINIMAL-01`
- push: 各commit後`git push origin main`。STOP時は完成分のみcommit。

## 報告(RESULT_PACKET項目)

`docs/pm/RESULT_PACKET_VOICES_A2.md`に、ユーザー指示16の形式で:
1. T-0結果
2. Priority 1 — AI hiring A2: article title/word count/3V structure(3人の呼称と登場確認)/Fact・Ledger整合(Fact Checker・Ledger逸脱結果、NEW_NUMBERS)/Validator結果(実行したもの・3V非適用としたものと代替チェック)/audio duration/Audio Validation/player URL/direct audio URL/actual voices(A/B/C実名)/actual model/API cost(LLM/TTS/ASR)/retry回数(article・segment)/Status
3. Priority 2 — Personalized news A2: article完成/未完成/word count/Validator結果/音声化した場合はduration・Audio Validation・player URL・direct audio URL/API cost/Status(未着手なら理由=Priority 1後の余力判断)
4. Cost: delegation回数(=1)/API call数/TTS費用/retry回数/合計
5. イレギュラー: なし/あり(あり=何が起きたか・どこで止まったか・完成済み成果物・最小の選択肢・追加コスト見込み、`USER_DECISION_REQUIRED`)
6. PM Closeout: Priority 1 USER_LISTENING_PENDINGか/Priority 2 USER_LISTENING_PENDINGか/未処理USER_DECISION_REQUIRED/Production変更をしていないこと(git status証跡)/新規Open Item候補/不要な追加調査を実施していないこと
7. commit hash・push結果・Web到達確認・事前指定外Read(理由付き)

ユーザー向け表記は「B1」に統一(「B1B」不使用)。
