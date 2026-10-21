# ユーザー指示原文(2026-10-21)
管理ID: FAMILY-X-MANGA-AI-CHAT-BYUS-PRODUCTION-E2E-01 委任_05(Std KP「take part」発音調査)

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
