# ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_02 (2026-10-11、Sonnet実行層、日英統合)

Status: USER_DECISION_REQUIRED候補(提案のみ。Opus独立レビュー並行中)。read-only・有料API 0円。Production/Prompt/Validator/Routing/SSOT/Coffee worktree/user_test無変更。
使用モデル: 実行層 Sonnet 5.5(有料モデル呼出なし)。ローカル集計のみ。

## 成果物
- er056_output/asr_tts_cross_language_reconciliation_01/RECONCILIATION_REPORT_01.md(13章。日英比較表・差の理由・g8・Coffee・統一案・例外・QCD・Trial・判断事項U-0〜U-16・統一例外分類UX01〜23・Dangling Reference Check・未配線一覧)
- er056_output/asr_tts_cross_language_reconciliation_01/COFFEE_AZURE_COST_ADDENDUM_01.md

## 主要な発見(確定)
- 日英の差の大半は導入時期差による継ぎ足し。言語が要求する違いは判定器の中身と英語A2の6%減速だけ。
- Coffee part2: 「真の音声不良」確認0件。標準1回目・LR音声のみ人間聴取待ち。合格相当の可能性が高い音声は5本中3本以上(推測)。
- g8: Primary NGの直接原因は「熟->じく」。SCG除外はC1のカタカナ率ヒューリスティック。誤PASS防止の実績は0、C群誤PASS 0/5。
- Coffee費用: Azure 8回・231.83秒・約10.30円が累計20.73円に未計上。補正後約31.03円/50円。同型の集計コードが11ファイルにある。
- 英語側「wav 16MB commit」は事実と異なる: commit 7ef4eed2は37ファイル約1.55MB(wavなし)。wav 6本約14.3MBは.gitignore(*.wav)でgit管理外、ローカルのみ。16MBはローカルsnapshot全体(15.4MB)に近い。履歴書換えは不要・禁止。
- Dangling: fallback廃止でLocal Rewrite再TTS(crosslevel L383)が壊れる。welcome共有殻がFALLBACK style定数を通常styleとして使用。TTS回数定数(2+1)は日英共有。静的監査・g8回帰testが固定。
## 要判断
U-0〜U-16(RECONCILIATION_REPORT_01.md 9章)。優先: U-1(g8/C1)、U-2(UNCERTAIN経路)、U-4(minimal fallback)、U-5(Local Rewrite)、U-7(6%減速)、U-8(Secondary選択)、U-14(Trial予算)、U-15(Azure費用計上)。
## 追加Trial候補(未実行)
X-T1 約80円(上限120円)、J-T1 約9〜10円、J-T2 約3〜8円、E-T2 約10〜15円(実装後)、H-T4 人間聴取(0円)。
