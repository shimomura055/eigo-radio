# PM-TOKEN-EFFICIENCY-F1-ZERO-BYTE-TRANSCRIPT-ROOT-CAUSE-01

性質: 原因特定(¥0、API呼び出しなし)。Production/SSOT本文/PM_GOVERNANCEのルール変更なし(提案のみ)。

## 1. 結論(サマリ)

- **原因**: Claude Code CLI harness が subagent委任ごとに作成する
  `tasks/<taskId>.output`(完了通知`<task-notification>`の`output-file`が
  指す先)は、**タスク開始時に空ファイルとして作成された後、完了時に
  最終transcriptを書き込む処理自体が高確率(観測母集団で約35%)で
  実行されない**という、harness内部の書き込み不全である。
- 一方、Claude Code自身が標準で逐次追記している別の保存先
  `%LOCALAPPDATA%\...\.claude\projects\<project>\<sessionId>\subagents\agent-<taskId>.jsonl`
  には、**実行中からリアルタイムで完全な会話ログ(tool_use/tool_result/usage
  トークン数を含む)が書かれ続けており、0バイトになったケースでも
  ほぼ確実に内容が残っている**。
- 本タスク自身の委任(agentId `ac8f4ab86897a327c`)で**現在進行形の再現**を確認した:
  `tasks/ac8f4ab86897a327c.output`は最初から最後まで一貫して0バイトのままだったが、
  同時に`subagents/agent-ac8f4ab86897a327c.jsonl`は272,591→346,288→456,606バイトと
  実行中に成長し続けた。
- **観測基盤は回復した**: F-1手順(過去のOPUS/Sonnet往復)が既にコピーしていた
  0バイトプレースホルダー4件(`docs/pm/transcripts/`内)全てについて、代替保存元から
  完全なtranscriptを復元できた(4/4、100%)。直近10委任でも10/10(100%)復元・確認できた。
- **次の施策1/2の効果測定へ進める状態か**: **条件付きでYes**。今回復元した
  データと、汎用の復元スクリプト(`docs/pm/tools/collect_subagent_transcripts.py`)
  により、必要なtranscriptは(tasks/*.outputが0バイトでも)取得可能になった。
  ただし恒久的な保存元切替はF-1手順の運用変更であり、本タスクの権限外
  (`USER_DECISION_REQUIRED`として下記5節で提案のみ行う)。

## 2. 調査データ

対象: セッション`294958fe-da6e-491c-8a02-4f864d8195c8`の
`tasks/*.output`全298件(調査開始時点)。

| 区分 | 件数 |
|---|---|
| 全task出力ファイル | 298 |
| うち0バイト | 106 (35.6%) |
| うち非0バイト | 192 |
| 0バイトのうちsubagent委任(`a`接頭辞、17桁) | 102 |
| 上記102件のうち代替保存元(`subagents/agent-<id>.jsonl`)で復元可能 | **102/102 (100%)** |
| 0バイトのうちBackground Bashコマンド出力(`b`接頭辞、9桁、F-1のスコープ外) | 4 |
| 上記4件の代替保存元 | 該当なし(そもそも会話ログではなく単なるコマンド標準出力キャッシュのため対象外、原理的に問題なし) |
| 直近10委任(a接頭辞、作成時刻降順) | 10/10 復元・確認済み(2件は元々非0、8件は代替保存元から復元) |

### 2-1. 決定的な物理証拠

- 0バイトファイルは例外なく`birth時刻 == modify時刻`(作成後、一度も書き込まれていない)。
  非0バイトファイルは全て`modify > birth`(平均約807秒後、最大約7.4時間後に書き込み)。
  → 「遅延して書かれる」型ではなく、**書き込みが発生するかしないかの二値**。
- 非0バイトの`tasks/*.output`と対応する`subagents/agent-<id>.jsonl`が両方存在するケースでは、
  バイト数が完全一致(例: `a889112392727048a`=861,279バイト、`a8dd9313c22d94da5`=2,071,973バイト、
  いずれも両ファイルで同一)。→ 両者は同一内容の別経路コピーであり、`subagents/`側が
  信頼できる原本。
- 0バイト発生は特定の日時・特定のエージェント種別・特定の所要時間に偏らず、
  Sep 11 06:25〜Sep 13 13:48の全期間に分散して発生(単発のクラッシュ/再起動起因ではなく、
  継続的な確率的不具合)。
- `agentType`(`sonnet-worker`/`opus-consultant`)、`requestShape`(全件`background`)による
  差異なし。

### 2-2. リアルタイム再現(本タスク自身)

本タスクの委任ID`ac8f4ab86897a327c`について、実行中に3回計測:

| 時刻(実行経過) | `tasks/ac8f4ab86897a327c.output` | `subagents/agent-ac8f4ab86897a327c.jsonl` |
|---|---|---|
| 開始直後 | 0バイト | 272,591バイト |
| 中盤(調査完了後) | 0バイト | 346,288バイト |
| 終盤(本レポート作成前) | 0バイト | 456,606バイト |

→ `subagents/`側は逐次追記のClaude Code標準セッションログであることが確定。
`tasks/*.output`側は完了後の一括書き込み(またはそれすら発生しない)という
別メカニズムであることが確定。

## 3. 修正要否

- **repo側/Production側の修正は不要かつ不可能**: 0バイト化はClaude Code CLI harness
  内部(非公開実装)の問題であり、eigo-radioリポジトリのコード・SSOT・運用ルールの
  不具合ではない。今回のタスク範囲(Production/SSOT変更禁止)でも修正対象外。
- **実務上の回避策は既に存在する**: 代替保存元(`subagents/agent-<id>.jsonl`)から
  読み取れば、0バイト問題を実質的に無効化できる。

## 4. 観測基盤の回復状況

- `docs/pm/transcripts/`内で0バイトのまま残っていた既知4件を、代替保存元から
  復元して追加コピーした(既存の0バイトプレースホルダーは削除・上書きせず、
  `<taskId>_recovered.jsonl`として追加のみ):
  - `a61ba9010d3a04cbd_recovered.jsonl`(0.69MB、PM-TOKEN-EFFICIENCY-STATUS-MEASUREMENT-02のToken計測委任)
  - `a64dc8c9e1d913cfb_recovered.jsonl`(1.49MB、CONSOLIDATION-104 OPEN-141 Phase B)
  - `a8548d8b676ce6a06_recovered.jsonl`(2.56MB、CONSOLIDATION-105 OPEN-141 Wiring)
  - `ab873c6e75280759d_recovered.jsonl`(2.14MB、CONSOLIDATION-104 OPEN-121 D'/C-v2)
  - 4件合計6.88MB、JSONL整合性を全行検証済み(不正行0件)。
- 全106件中102件(a接頭辞)は同じ方法で復元可能であることを確認済みだが、
  合計サイズが20MBを大きく超える(概算90MB超)ため、今回は上記の
  「既にrepoで0バイトのまま追跡されていた4件」のみ復元してgit追加した。
  残り98件は代替保存元(`subagents/agent-<id>.jsonl`)に存在することのみ記録し、
  repoへは追加していない(必要時に同スクリプトで個別取得可能)。

## 5. 改善案(提案のみ、運用ルール未変更)

今回作成した`docs/pm/tools/collect_subagent_transcripts.py`(¥0、read-only+追加コピーのみ):
- `tasks/*.output`が0バイトのものを検出し、対応する`subagents/agent-<id>.jsonl`が
  非0であれば`docs/pm/transcripts/`へ`<taskId>_recovered.jsonl`として追加コピーする。
- 既定はdry-run。`--apply`指定時のみ書き込み。既存ファイルの上書き・削除は行わない。
- `--only-existing-placeholders`で、既にF-1退避済みだが0バイトのものだけに
  対象を絞れる(repoサイズ影響を最小化)。
- `--max-total-mb`(既定20MB)で1回の実行あたりの追加サイズに上限を設けられる。

**提案(`USER_DECISION_REQUIRED`、Fable/ユーザー判断待ち)**:
今後のF-1退避手順そのものを「`tasks/*.output`が0バイトの場合、
`subagents/agent-<id>.jsonl`から自動的に代替取得する」よう恒久変更するかどうか。
本タスクでは運用ルール変更は実施せず、スクリプトの提供と実証のみ行った。

## 6. 限界

- `subagents/agent-<id>.jsonl`はClaude Code CLIの非公開・非文書化の内部実装であり、
  将来のCLIバージョンでパスや形式が変わる可能性がある(保証されたAPIではない)。
- `tasks/*.output`writerが具体的に「なぜ」書き込みに失敗するか(harness内部のどの
  処理か)は、ファイルシステム上の状態証拠からの推定であり、CLIのソースコードを
  確認したものではない。
- 今回0バイトのうち4件(`b`接頭辞)は、そもそもsubagent transcriptではなく
  Background Bashコマンドの標準出力キャッシュであり、F-1のスコープ外(問題なし)。
