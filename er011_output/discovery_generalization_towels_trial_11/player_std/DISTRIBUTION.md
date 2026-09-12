# DISTRIBUTION.md — 標準player配布経路(URL設計のみ、本タスクではpush・有効化なし)

管理ID: FAMILY-A-DISCOVERY-GENERALIZATION-TOWELS-TRIAL-11-STANDARD-PLAYER-01

対象artifact:
`er011_output/discovery_generalization_towels_trial_11/player_std/index.html`
(A2/B1B標準player、Gate 7 (a)〜(m)準拠、詳細は同ディレクトリのREPORTを参照)

このplayer自体はHTML(音声再生・click-seekにJavaScriptを使用)であり、
`raw.githubusercontent.com`はContent-Type: `text/plain`で配信するため
ブラウザ上でHTMLとして描画されない(ソースコードとして表示される)。
そのため、**player自体(index.html)の配布**と、**player内が参照する
音声ファイル(mp3)の配布**は別に扱う。

## 音声ファイル(mp3)のURL

個別segment音声・完成episode音声は、すべてGitHub raw絶対URLで参照している
(push後に有効になる想定):
`https://raw.githubusercontent.com/shimomura055/eigo-radio/main/<path>`

これはaudioタグの`src`としてブラウザが直接読み込むバイナリであり、
raw.githubusercontent.comがそのまま音声ファイルとして配信するため問題ない
(HTMLのようにレンダリング解釈は不要)。

## player本体(index.html)のURL — 2候補

### 第1候補: GitHub Pages

`https://shimomura055.github.io/eigo-radio/er011_output/discovery_generalization_towels_trial_11/player_std/index.html`

- 確認結果(本タスクで実施、有効化はしていない):
  - `gh auth status` / `gh api repos/shimomura055/eigo-radio/pages`
    による認証済みAPI確認を試みたが、本Sonnet実行環境に`gh`コマンドが
    インストールされておらず(`gh: command not found`)、直接確認できな
    かった。
  - 補助的read-only確認として、`https://shimomura055.github.io/eigo-radio/`
    へHTTP GETを実行した結果、**HTTP 404**が返った。これはGitHub Pagesが
    現時点で有効化されていない可能性と整合するが、`gh api`によるSSOT確認
    の代替にはならない(branch指定・Pages設定の有無を断定はできない)。
  - 結論: GitHub Pagesが有効かどうかは**未確定**。有効化する場合は
    ユーザー承認の上、別タスクで`gh api repos/shimomura055/eigo-radio/pages`
    (有効化状態確認)→必要なら有効化、の順で行う(本タスクでは有効化して
    いない、委任文の禁止事項どおり)。
  - push後、上記URLへのHTTP GETが200になることと、ページ内の音声が実際に
    読み込める(再生できる)ことの両方を確認する必要がある。

### 第2候補: raw.githack.com

`https://raw.githack.com/shimomura055/eigo-radio/main/er011_output/discovery_generalization_towels_trial_11/player_std/index.html`

- raw.githack.comは、公開GitHubリポジトリ内の任意のファイルを、正しい
  Content-Type(HTMLファイルは`text/html`)で配信する無料の公開proxyサービス
  であり、GitHub Pages配線が不要(リポジトリ側の設定変更なしにその場で使える)。
- 制約: 第三者サービスへの依存(raw.githack.com自体の可用性に依存する)。
  Production配布経路としては採用しない(Trial試聴用途に限る)。
- push後、上記URLへのHTTP GETが200になることと、ページ内の音声(GitHub raw
  URL)が実際に読み込める(再生できる)ことの両方を確認する必要がある。

## 推奨

- 即時利用: 第2候補(raw.githack.com)。push直後から追加設定なしで使える。
- 恒久的な配布経路が必要な場合: 第1候補(GitHub Pages)をユーザー承認の上
  で有効化する(有効化はProduction的な公開設定変更に相当するため、
  本タスクの範囲外・別タスクでのユーザー判断事項とする)。

## 未実施事項(次のconsolidationで実施予定)

1. `git add`対象: `player_std/index.html`, `player_std/DISTRIBUTION.md`,
   `player_std/audio_mp3/**`(新規追加分のみ)、および
   `er011_towels_trial11_std_player_01.py`(生成script)。
   `{a2,b1b}/assembled/`配下は本タスクで一切変更していないため追加不要。
2. push後、上記2候補URLの両方でHTTP 200確認、および実際にブラウザで
   音声が再生できることの確認(evidence取得)。
3. 確認結果を次のconsolidationでSSOTへ反映。
