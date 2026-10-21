# 委任文(Fable→sonnet-worker)

## 管理ID
FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_05(ユーザー指摘「Standard Key Phrase『take part』が『take tart』のように聞こえる」の原因調査。**調査・原因分析のみ、API 0、TTS/ASR/LLM呼出0、原稿・Prompt・音声・QA判定仕様・完成音声の変更禁止**)。並行agent: 記事A 委任_04(OPEN_ITEMS/CURRENT_SPEC/REGISTER/DECISION_LOG/REPORT_LEDGER/ACTIVE_TASKを編集中)。**本委任はSSOTを編集しない**(調査書と報告のみ。SSOT反映はFable判断後の別委任)。

## 性質/到達上限/禁止
- 性質: 不具合調査(14節 step1〜4: 検知→既存仕様reconcile→原因切り分け→failure mode一般化)。到達上限=原因特定+改善方針案(提案のみ)。
- 禁止: 有料API、音声差し替え、state/wav/Store操作、Production code/Prompt/閾値変更、新仕様の実装、SSOT編集、`git add -A`等。
- 費用JPY0。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_委任_05.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「BYUS-PRODUCTION-E2E-01 委任_05」を含む最新index。toolは`docs/pm/tools/`配下)。check結果1行。T-2: TTSなし。

## ユーザー指示(原文・2026-10-21、全文)
`docs/pm/delegation_log/2026-10-21_FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01_KP-TAKE-PART_USER.md`へ逐語保存(先頭に`# ユーザー指示原文(2026-10-21)`と`管理ID: FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_05(Std KP「take part」発音調査)`の2行、以降一字一句変えない。文字数・sha256[本文のみ]を報告)。
--- 原文ここから ---
# Claude Code／Fableへの指示
## Family X 漫画AI記事 — Standard Key Phrase発音不具合調査

### 1. 調査目的

対象記事：漫画キャラクターとAIで会話（byUs）

Production run：`run_byus_01`

試聴ページ：
https://shimomura055.github.io/eigo-radio/user_test/manga_ai_chat_byus_e2e_01/index.html

ユーザーから、StandardのKey Phraseにおいて、**「take part」が「take tart」のように聞こえる**との指摘があった。

以下をProductionの実行証拠に基づいて調査する。

### 2. 必須調査項目

**① ASR読み起こし結果**

- 該当Key Phraseを特定する。
- Primary ASR（gpt-4o-mini-transcribe）の転写結果を提示する。
- Secondary ASR（Azure）の転写結果が存在する場合は提示する。
- 台本「take part」との差分を明示する。
- 各ASRの判定結果（PASS／NG）と判定理由を示す。

**② Secondary ASR使用状況**

- Primary ASRはPASSしたのか、NGだったのか。
- NGだった場合、Secondary ASRが実際に発動したか。
- 発動した場合、どのような判定で最終的にPASS／NGとなったか。
- 発動しなかった場合、その理由は何か。

**③ TTS再生成状況**

- ASRのNGによってTTS再生成が発生したか。
- 発生した場合、何回実行されたか。
- 各TakeのASR結果・最終判定・採用Takeを提示する。
- 再生成されなかった場合、その理由を説明する。
- Fallback／Local Rewrite等の別経路が発動していれば併せて報告する。

**④ なぜ見抜けなかったのか**

特に以下を切り分ける。

- 実際のTTSが「tart」のように誤発音したのか。
- ASRが文脈補正によって「part」と誤認識したのか。
- ASRが不一致を出していたのに、同音等価判定・許容ルール等によって誤PASSしたのか。
- Primary／Secondary／TTS再生成の発動条件に抜けがあったのか。
- 検査対象音声と最終公開音声に差異がないか。
- Key Phrase固有のQA経路に、Full Story等との違いや検査漏れがないか。

**推測と確認済み事実を区別し、原因を特定すること。**

既存のASR表記揺れ対策・Connected Speech対策・Phrase List等との関係も確認する。

### 3. Fableによる独立評価

Claudeの分析に対してFableが以下を確認する。

1. Root Causeが実行ログ・コード・音声の証拠で裏付けられているか。
2. 現行の承認済みQA仕様が正しく発動したのか。
3. 一般的な再発リスクがあるか、今回固有の問題か。
4. 品質を守りながら、余計なTTS再生成やHuman Reviewを増やさずに解決できるか。

必要であれば改善方針を提案してよいが、**新仕様の採用・追加Trial・Production変更はユーザー承認前に実施しない。**

### 4. STOP条件

- 今回は調査・原因分析のみ。
- 有料のTTS／ASR再生成は行わない。
- 原稿・Prompt・音声・QA判定仕様を変更しない。
- 完成音声の差し替えは行わない。
- 既存のProduction音声・ログを最大限再利用する。

### 5. 報告形式

以下の表を必ず含め、簡潔に報告する。

| 項目 | 結果 |
|---|---|
| 正しい台本 | take part |
| Primary ASR転写 | |
| Primary判定 | |
| Secondary ASR使用 | YES／NO |
| Secondary転写・判定 | |
| TTS再生成 | YES／NO・回数 |
| Fallback／Local Rewrite | |
| 最終採用Take | |
| 最終音声の発音評価 | |
| 見逃しの原因 | |
| 再発リスク・対策要否 | |

**最も重要なのは、「音声に問題があった」という結果だけでなく、なぜ既存の品質保証の仕組みで検出できなかったかを明らかにすることである。**

調査結果を踏まえ、ユーザーが修正・再発防止の必要性を判断できる状態で報告する。
--- 原文ここまで ---
(注: 原文保存は上の「--- 原文ここから ---」〜「--- 原文ここまで ---」の間を一字一句そのまま。末尾段落の「明らかにすること。」の文末表現は原文どおりに保存すること[Fableの転記ミスがあれば原文=ユーザー貼付が正])

## 調査の手がかり(鵜呑みにせず証拠で確認)
- Std KP音声の生成経路: 英語Key Phrase Component=`generate_key_phrase_component_verified`(CURRENT_SPEC.md:1828「例外: 合計上限4回=KEY_PHRASE_MINIMAL 2+ENGLISH_LOCK 2」)、Style=K2(profile fx_20261017、sha 9d905cfe…)、**Master Audio Store 2段key**(`er019_family_x_kp_en_k2_store_01.py`、key A=k2 primary / key B=english_lock_fallback)。**重要: KP音声はMaster Audio Storeから他記事の既存音声を再利用(reuse)している可能性がある**→`er006_output/master_audio_store_01/manifest.json`・`reuse_telemetry.jsonl`で「take part」のentry(生成元記事・生成日時・style key・ASR検証記録・wav sha)を特定し、今回run側のseed provenance(`a2/audit/`配下のkey phrase生成記録・`key_phrase_source_gate.json`・`tts_generation_results.json`のkp segment)と突合。
- ASR判定: 英語短句のASR照合関数(`er003_audio_tts_asr_safety`系、`classify_asr_match`、HOMOPHONE_EQUIVALENT/semantic_equivalence/Connected Speech対策/CMU発音辞書/`er021` EN semantic equivalence telemetry `er021_output/.../telemetry.jsonl`)。「part/tart」がどの規則でどう扱われるか(同音等価? 編集距離許容? 一次PASSなら二次呼出なし?)をコードと実ログ両方で。
- Azure Phrase List: Family X KP経路でPhrase Listが渡されるか(`AZURE_PHRASE_LIST_WEIGHT=2.0`はphrase list非空時のみ、Family Z側PL2.0との違い)。
- 公開音声との同一性: 試聴ページの該当mp3/wav(`user_test/manga_ai_chat_byus_e2e_01/`配下)と、run dirの採用wav、Store wavのsha256を比較(検査対象音声=公開音声か)。KP音声は英語句+phrase_repeat(2回読み)+日本語意味の構成→どの要素に「take part」が含まれ、何本の音声が存在するか。
- 音声の客観指標(API 0・ローカル): 採用wavの該当区間について、可能なら既存ツール(ピッチ/波形/無音)で「p」の破裂音の有無を示す簡易指標(スペクトログラム画像を`docs/research/.../kp_take_part_spectrogram_01.png`へ保存、判断はしない)。**発音の良否は未試聴=断定しない**。ただし「TTSが誤発音した」「ASRが文脈補正した」「同音等価で誤PASS」「検査対象と公開音声が別」の各仮説について、証拠で支持/不支持を明記。
- Full Story経路とのQA差: KP経路は一次PASSで終了か、二次強制か、減速後再検証の有無、reuse時の再検証有無。

## 手順
S1. 該当KPの特定(a2のkey phrases一覧[rank/canonical/ja gloss]、「take part」を含むitem)。S2. 生成/再利用経路の特定(今回生成か、Store reuseか。reuseなら生成元記事・日時・その時のASR記録)。S3. ASR記録全文(一次/二次、判定コード、理由、semantic_equivalence)と再試行回数・採用take。S4. 公開音声との同一性(sha)。S5. コード上の判定規則の該当箇所(file:行)と「part→tart」の扱い。S6. 仮説ごとの支持/不支持。S7. failure mode一般化(同種: 1音素差の短句、語頭破裂音、reuse音声の再検証なし等)と、既存対策(Connected Speech/表記揺れ/Phrase List/CMU)との関係。S8. 改善方針案(提案のみ・実装禁止・QCD影響付き、余計な再生成/HRを増やさない観点)。
S9. 調査書`docs/research/FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01/KP_TAKE_PART_INVESTIGATION_01.md`(ユーザー§5の表を先頭に)。secret scan→明示add(調査書・画像・delegation_log 2件)→commit(`FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_05: Std KP「take part」発音指摘の原因調査(API 0、SSOT未編集)`)→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_FXBY5.md 上書き)
ユーザー§5の表(11項目、未確定は「未確定(理由)」)→S2〜S8の要点→調査書path・commit・raw URL→判断候補(「判断候補」表記)→4行判定。