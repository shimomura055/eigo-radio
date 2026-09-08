# PM-CONTEXT-MANAGEMENT-LIGHTWEIGHT-DESIGN-01 — 調査・設計レポート

管理ID: PM-CONTEXT-MANAGEMENT-LIGHTWEIGHT-DESIGN-01
担当: sonnet-worker(調査・設計のみ、実装なし)
対象: 長期PMセッション(Fable=sandwich-pm)における/compact前後のProject状態保持の最小構成設計

---

## 0. 調査方法・根拠

- ローカル確認: `claude --version`(2.1.263)、`claude --help`、`claude project --help`、
  `~/.claude/settings.json`、`C:\Users\tensh\eigo-radio\.claude\settings.local.json`、
  `.claude/agents/*.md`(sandwich-pm/sonnet-worker/opus-consultant)、
  `~/.claude/cache/changelog.md`(grep "compact")。
- ネット確認: `https://docs.claude.com/...` は301で `https://code.claude.com/docs/en/...` へ
  リダイレクト(200)。各ページの`.md`版(例: `https://code.claude.com/docs/en/hooks.md`)を
  取得できたため、こちらをSSOTとして使用(HTML版はNext.jsのクライアント側JSONに本文が
  埋まっており全文取得できなかった)。取得したページ: `hooks.md`, `hooks-guide.md`,
  `settings.md`, `slash-commands.md`, `commands.md`, `context-window.md`,
  `model-config.md`, `statusline.md`, `memory.md`, `costs.md`, `interactive-mode.md`。
  スクラッチパッドに保存済み: `C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\eba13a8b-6eec-4381-909a-3a2d71be7123\scratchpad\*.md`

以下、「確認済み(根拠URL)」「未確認」を明示する。

---

## 1. Claude Code正式機能の確認

| 項目 | 状態 | 根拠 |
|---|---|---|
| 自動compactの発火条件・閾値 | 確認済み | モデルのcontext windowが閾値に近づくと自動発火。Sonnet 5は既定で1M windowの約967Kトークンで自動compact(`CLAUDE_CODE_AUTO_COMPACT_WINDOW`で変更可)。`docs/en/model-config.md#sonnet-5-context-window`,`#default-auto-compact-thresholds` |
| 閾値のユーザー設定可否 | 確認済み(可能) | `/autocompact <auto\|tokens>`(100k〜1M、`autoCompactWindow`としてuser settingsへ保存)/ CLIフラグ`--autocompact`(その起動限定、settingsは変更しない)/ 環境変数`CLAUDE_CODE_AUTO_COMPACT_WINDOW`(最優先)。`docs/en/model-config.md#set-the-auto-compact-window`, `commands.md`行57 |
| `/context` | 確認済み | 現在のcontext使用量をカテゴリ別に可視化。人間が手動実行するUIコマンド(会話に自動で入らない)。`commands.md`行72 |
| `/statusline` | 確認済み | ステータスバーのカスタム設定コマンド。ステータスバー自体は「API tokenを消費しない」がUI表示専用で、モデルの会話contextには自動的に入らない。`docs/en/statusline.md`行37,166 |
| `/compact [instructions]` | 確認済み | 人間が手動実行。フォーカス指示可(`custom_instructions`としてPreCompactへ渡る)。`commands.md`行70 |
| モデル自身が`/compact`を自律実行できるか | 確認済み(不可) | `slash-commands.md`: 「A few built-in commands are also available through the Skill tool, including `/init` and `/security-review`. Other built-in commands such as `/compact` are not.」→ Fableは自分の判断で`/compact`を発火できない(人間かauto-compactのみ)。 |
| モデルがリアルタイムのcontext使用率を取得できるか | 確認済み(直接手段なし) | 通常ターンのhook入力(UserPromptSubmit等)には使用率フィールドがない。`context_tokens`等はSessionStart(`resume`/`fork`)とPreModelSwitchのhook入力にのみ存在(セッション境界のみ)。statuslineはUI専用でモデルにフィードされない。よってモデルは`/context`の出力が会話transcriptに現れた場合を除き、能動的に使用率を知る標準手段を持たない。 |
| PreCompact hook | 確認済み | `matcher: manual\|auto`。exit code 2 または `{"decision":"block"}`で compaction をブロック可。**`additionalContext`をサポートしない**(decision-onlyイベント)。`systemMessage`/`continue`フィールドは破棄される。`hooks.md`行2873-2889, `hooks-guide.md`行510 |
| PostCompact hook | 確認済み | compaction完了後に発火。`compact_summary`(生成された要約文字列)を受け取れる。**decision controlなし(副作用専用、contextへの注入不可)**。`hooks.md`行2890-2904 |
| SessionStart hook(matcher: startup/resume/clear/compact/fork) | 確認済み | `matcher: compact`は「Auto or manual compaction」後に発火。`hookSpecificOutput.additionalContext`で会話冒頭にテキストを注入可能。これが**唯一、compact後にcontextへ状態を再注入できる公式手段**。`hooks.md`行1848-1882 |
| compact後に自動保持・再注入されるもの | 確認済み(公式表あり) | `context-window.md#what-survives-compaction`: システムプロンプト/出力スタイルは会話履歴外のため無変更。**プロジェクトroot直下のCLAUDE.mdと無条件ルールはディスクから再注入される**。Auto memory(`MEMORY.md`)もディスクから再注入。plan modeのplanも再注入。直近読み書きしたファイル最大5件を再読込。skill本体は5,000トークン/skill・合計25,000トークン上限で再注入。**hookが以前注入したcontextは他の会話履歴と同様に要約されるだけ**。`matcher: compact`のSessionStart hookの出力は要約後のcontextに追加される。 |
| 公式推奨パターン | 確認済み | `hooks-guide.md`「Re-inject context after compaction」節がまさに`SessionStart`+`matcher: compact`の組み合わせを公式サンプルとして提示している(PreCompactは併用例なし、ブロック/監査用途のみ紹介)。 |

**重要な訂正**: ユーザー原案の「PreCompact hook + SessionStart(compact) hook」のうち、**PreCompactはcontext再注入に無効**(decision-onlyでadditionalContext非対応)。公式ドキュメントもPreCompactを状態保存目的では紹介していない。有効なのは**SessionStart(matcher: compact)単体**である。

---

## 2. 標準compactだけでの保持評価

| 状態要素 | 標準compactで十分か | 理由 |
|---|---|---|
| Active task内容 | 別途保存が必要 | 会話履歴の一部としてLLM要約されるため、細部(受入条件の文言等)が非決定的に失われうる。ただし現行運用では既に`ACTIVE_TASK.md`が正式な永続ファイルであり、会話要約に依存していない。 |
| 管理ID一覧 | 概ね十分(ただしリスクあり) | IDはユニークな文字列で要約に残りやすいが、複数IDが並ぶ場合に一部が省略される可能性は否定できない(非決定的)。 |
| USER_DECISION_REQUIRED | **別途保存が必要** | これが会話要約でのみ保持される場合、「解決済みと誤認して見落とす」リスクが最も高い項目。`ACTIVE_TASK.md`のStatus欄は既に正式運用として存在するため、そこに明記されていれば実質「別途保存済み」。 |
| VALIDATED/APPROVED_FOR_PRODUCTION/PRODUCTION_WIRED | **別途保存が必要** | この3語の意味的距離が近く、LLM要約が「Production化済み」のように丸めてしまうリスクが高い(ユーザーが最も懸念している点)。正式SSOT(`CURRENT_SPEC.md`/`DECISION_LOG.md`)に記録されているため、会話要約が不正確でもSSOT自体は無事(正式記録は失われない)。ただしFableがSSOTを都度Grepし直さず要約のみを信じるとズレるリスクは残る。 |
| approved-but-unwired一覧 | **別途保存が必要** | 同上、Production配線状況はSSOT/OPEN_ITEMS.mdの管理ID単位でしか正確に追えない。 |
| STOP条件 | 概ね十分 | `PM_GOVERNANCE.md`(正式文書、compactの影響を受けない)に11節として明文化済み。会話要約に頼らず参照可能。 |
| 次アクション | 別途保存が必要(軽微) | 直近の作業手順のような細部は要約で粒度が変わりやすい。`ACTIVE_TASK.md`に明記済みなら問題なし。 |
| Open Item一覧 | 十分(SSOT前提) | `OPEN_ITEMS.md`が正式SSOTでcompactの影響を受けない。会話要約に依存しない設計が既に取れている。 |

**結論**: 8要素のうち「STOP条件」「Open Item一覧」は既存の正式SSOT運用により標準compactでも実質安全。残り6要素はSSOT自体は無事だが、**Fableが会話要約だけを信じて再照合を怠るリスク**が本質的な弱点であり、「compact後に必ずSSOT/ACTIVE_TASKへ戻る」ことを保証する仕組みが必要。

---

## 3. 最小構成案の設計

既存資産のトークン規模(概算、次節参照)から、`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`は**そもそも1M contextに全文を載せられない**規模(特に`DECISION_LOG.md`は概算120万トークン超で1M windowを超過)。したがって「毎回全文読込禁止」は既存howto通りの必須設計であり、compact対応もこの制約の上に乗せる。

比較した案:

- **A. 標準auto-compactのみ**: 追加実装ゼロ。ただし2節の通り「Fableが要約を過信して再照合しない」リスクを構造的に防げない。
- **B. 標準compact + compact後にFableが短いPM状態ファイルを再読込(hookなし)**: `CLAUDE.md`(プロジェクトroot、無条件ルール)は**compact後に自動的にディスクから再注入される**ことが公式に確認済み。ここに「compact直後は必ず`ACTIVE_TASK.md`を読み、Statusが`USER_DECISION_REQUIRED`でないか確認せよ」という数行の手順を置けば、hookなしで自動的に(毎ターン)この指示がFableに再提示される。
- **C. PreCompact + SessionStart(compact) hook**: 上記1節の訂正の通り、PreCompactはcontext注入に寄与しない。有効なのは**SessionStart(matcher: compact)単体**。`.claude/settings.json`に数行追加し、`ACTIVE_TASK.md`の固定ヘッダ部分(例: `head -n 15`)をechoしてadditionalContextとして自動注入する。公式ガイド(`hooks-guide.md`)そのままのパターン。
- **D. その他軽量案**: (D1)`ACTIVE_TASK.md`に固定ヘッダ(管理ID/Status/UDR一覧/approved-but-unwired一覧/STOP条件/次アクション)を持たせる、(D2)`PM_BRIEF.md`に「compact後の復帰手順」を数行追記、(D3)`CLAUDE.md`へ復帰指示を置く(=Bと同義、CLAUDE.mdの自動再注入特性を利用)、(D4)`/compact <instructions>`をユーザーが手動実行する運用(例:`/compact focus on ACTIVE_TASK.md and open USER_DECISION_REQUIRED items`)、(D5)statuslineでcontext使用率を可視化(人間向けの早期警戒のみ、モデルへの状態保持効果はゼロ)。

D1(固定ヘッダ)はB・Cいずれとも独立に有効で、「何を読めば全状態が分かるか」を決定的にする土台。B/C/D4/D5は排他ではなく組み合わせ可能。

---

## 4. Tokenコストの数値化

実測(文字数、`wc -c`)と概算トークン数(タスク指定の目安「日本語1文字≒1〜1.5token」を採用し、中間値1.2token/文字で概算。英語IDやパスも多いため実際はこれよりやや少ない可能性がある近似値):

| ファイル | 文字数 | 概算トークン数 |
|---|---|---|
| `docs/pm/PM_BRIEF.md` | 3,175 | 約3,800 |
| `docs/pm/ACTIVE_TASK.md`(現状) | 244 | 約290 |
| `docs/pm/RESULT_PACKET.md`(現状) | 938 | 約1,130 |
| `docs/pm/PM_GOVERNANCE.md` | 53,479 | 約64,000 |
| `CLAUDE.md` | 3,514 | 約4,200 |
| `CURRENT_SPEC.md` | 304,816 | 約366,000 |
| `DECISION_LOG.md` | 1,007,957 | 約1,209,000(**1M windowを超過**) |
| `OPEN_ITEMS.md` | 449,457 | 約539,000 |
| `.claude/agents/sandwich-pm.md` | 3,876 | 約4,650 |

**各案の追加トークン(1 compactあたり)**:

| 案 | PreCompact時追加 | compact後再読込・注入 | 合計追加(Low/Typical/Worst) |
|---|---|---|---|
| A | 0 | 0 | 0 / 0 / 0(ただし安全性の代償あり) |
| B(CLAUDE.md手順+ACTIVE_TASK手動Read) | 0(CLAUDE.mdは既に毎回ロード済みで純増分は導入時の一度きり約+100〜300token) | ACTIVE_TASK.md全文Read(現状290token)+必要なら該当行のみGrep数百token | 約300 / 約800 / 約3,000(Fableが不安になり関連SSOT数箇所を追加Grepした場合) |
| C(SessionStart compact hookでヘッダをecho) | 0 | echoされる固定ヘッダ分のみ(設計次第、目安200〜800token) | 約200 / 約600 / 約2,000(ヘッダを大きくしすぎた場合の上限、10,000文字超で自動的にファイル参照化される安全弁あり) |
| D1(固定ヘッダのみ、B/Cと併用) | 0 | ヘッダ部分のみで済むためB/Cの再読込コストをむしろ削減 | B/Cの数値に対し軽減方向 |

**削減量に対する割合**: 200K window運用なら典型的な削減量は約150,000〜170,000トークン(閾値近くまで使ってから要約20-30K程度に圧縮と仮定)、1M window(Sonnet 5既定)なら約870,000〜900,000トークン。B/Cいずれも典型追加コストは600〜800トークン程度であり、**削減量に対して約0.1〜0.5%(200K想定)、0.07〜0.09%(1M想定)**。Worst caseでも3,000トークン程度なら200K想定で約2%、1M想定で0.3%程度に収まり、「仕組みがToken節約効果を上回ってはならない」という原則を明確に満たす。

---

## 5. Fable復帰の時間コスト

| 案 | compact前保存 | compact後再読込 | 状態再構成 | 通常作業へ戻るまで |
|---|---|---|---|---|
| A | なし | なし(要約のみ) | Fableが要約を信じるか、不安な場合はPM_BRIEF→ACTIVE_TASK→SSOT Grepを自主的にやり直す | 信じた場合は数秒だが安全性未保証。やり直す場合は30秒〜1分超 |
| B | なし(常時ACTIVE_TASK.mdを更新している前提) | ACTIVE_TASK.md Read数秒 | CLAUDE.mdの手順に従いStatus確認、必要ならSSOT該当箇所Grep数秒 | 10〜30秒(手順通り動けば) |
| C | なし | SessionStart(compact)hookが自動でecho、Fableの明示的な読込アクション不要 | ヘッダが会話冒頭に既にある状態で次の応答を組み立てるだけ | 数秒〜10秒程度(Bよりやや速いが、Fableが確実にそのadditionalContextを見て行動する保証は「hookが常に発火する」という仕組み依存であり、Bの「CLAUDE.mdの指示を読んで自分でReadする」よりも人的判断の介在が減る分、実行漏れリスクも減る) |
| D1単独(手順記述なし) | なし | ヘッダ形式のACTIVE_TASK.mdをRead | 固定フィールドなので解釈が速い | B相当、ただし手順記述(PM_BRIEFやCLAUDE.md)と組み合わせないと「読むきっかけ」が保証されない |

---

## 6. 比較表(A〜D)

| 案 | 状態保持の安全性 | Token追加量 | Fable復帰時間 | 実装複雑度 | メンテナンス負担 | 誤作動時のリスク |
|---|---|---|---|---|---|---|
| A. 標準auto-compactのみ | 低(要約の非決定性に全面依存) | なし | 不定(数秒〜1分超) | なし | なし | なし(そもそも何もしないので壊れようがないが、安全性の担保もない) |
| B. compact+CLAUDE.md手順(hookなし) | 中〜高(CLAUDE.mdの自動再注入は確認済み事実。ただし「手順に従うかどうか」はFableの遵守に依存) | 極小 | 10〜30秒 | 最小(CLAUDE.mdに数行追記のみ) | 最小 | 低(単なる文書追記、誤作動という概念がほぼない) |
| C. SessionStart(compact) hook | 高(システムが強制的に発火、人的判断に依存しない。ただしPreCompactは無効なので併用不要) | 極小 | 数秒〜10秒 | 小(settings.jsonへhook追加、動作確認要) | 小(hookスクリプトの保守、ACTIVE_TASK.mdの書式変更に追従が必要) | 低〜中(SessionStartは decision controlなし=ブロック不可なので、失敗時は単に注入されないだけでOption A相当に自然劣化するfail-safe設計。ただしhook自体のバグでstderrノイズが出る可能性はある) |
| D. その他軽量案(固定ヘッダ/PM_BRIEF追記/`/compact`手動テンプレ/statusline) | D1(固定ヘッダ)は中〜高、他は人間の運用に依存 | 極小(D5のstatuslineはAPI token消費ゼロ) | 案により様々(D1はB/C双方の効果を底上げ) | 最小 | 最小 | 低 |

**総合**: BとD1は事実上ワンセット(CLAUDE.mdの手順+ACTIVE_TASK.mdの固定ヘッダ)。Cはこれに「人的判断への依存を減らす」自動化層を足すもので、排他ではなく積み増し。

---

## 7. 設計原則チェック(各案)

| 原則 | A | B | C | D1 |
|---|---|---|---|---|
| `/compact`を任意タイミングで実行しても復帰できる | △(要約次第) | ○(CLAUDE.md常時再注入) | ○(matcher:compactは手動/自動どちらも対象) | ○(ファイル自体は`/compact`と無関係に存在) |
| `/clear`を自動実行しない | ○(そもそも何もしない) | ○(何も自動実行しない) | ○(SessionStartはmatcher:clearも存在するが今回のhookはmatcher:compactのみ登録するため`/clear`時は発火しない設計にできる) | ○ |
| SSOTを会話contextに依存させない | ○(元々SSOTはファイル) | ○ | ○ | ○ |
| USER_DECISION_REQUIREDを落とさない | △(要約依存) | ○(手順で強制的に確認) | ◎(自動的にcontextへ再掲載されるため見落としにくい) | ○(固定フィールドとして存在) |
| APPROVED_FOR_PRODUCTION未配線を落とさない | △ | ○ | ◎ | ○ |
| 古いTrial結果をProduction仕様と誤認しない | △(要約が丸める可能性) | ○(SSOT再照合を促す手順があれば) | ○ | ○ |
| 毎回大量ファイルを再読込しない | ○ | ○(ACTIVE_TASK.mdのみ、SSOTはGrepのみ) | ○(ヘッダのみecho) | ○ |
| Token節約効果を上回らない | ○ | ○(4節参照、0.1〜0.5%程度) | ○(同上) | ○ |

---

## 推奨構成(要約)

1. `docs/pm/ACTIVE_TASK.md`に**固定ヘッダ**(管理ID/Status/未処理UDR一覧/approved-but-unwired一覧/STOP条件/次アクション)を持たせる(D1)。
2. `CLAUDE.md`(または`PM_BRIEF.md`)へ「compact直後は必ず`ACTIVE_TASK.md`の固定ヘッダを読み、Statusと未処理UDRを確認してから作業を再開すること」という数行を追記する(B)。CLAUDE.mdはcompact後に自動的にディスクから再注入されることが公式に確認済みのため、hookなしでもこの指示は必ず再提示される。
3. 上記だけで安全性・Token・時間のバランスは十分だが、**人的判断(手順を読んで実行する)への依存をさらに減らしたい場合のみ**、公式パターン通り`SessionStart`+`matcher: compact`のhookを追加し、`ACTIVE_TASK.md`の固定ヘッダをテキストとして自動echoする(C)。PreCompact hookは効果がないため追加不要(ユーザー原案からは除外を推奨)。
4. いずれの案も実装(hook追加、CLAUDE.md編集、ACTIVE_TASK.md書式変更)は**このタスクの範囲外**であり、本レポートは調査・設計のみ。実装するかどうか、および具体的な追記文言はユーザー判断が必要。

---

## USER_DECISION_REQUIRED候補

1. Bのみ(hookなし、CLAUDE.md追記数行)で運用開始するか、Cまで実装して自動化するか。
2. Cを採用する場合、`.claude/settings.json`(project共有)と`.claude/settings.local.json`(個人環境限定)のどちらへhook定義を置くか。
3. `ACTIVE_TASK.md`の固定ヘッダの具体的なフィールド名・書式(既存の細い運用を壊さない範囲で誰が最終文言を確定するか)。
