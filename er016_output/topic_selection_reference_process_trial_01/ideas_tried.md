# ideas_tried.md — Claude独自Idea記録(TOPIC-SELECTION-REFERENCE-PROCESS-TRIAL-01)

逐次探索の枠内で試したこと・何を疑い・なぜ・結果・費用を記録する
(禁止事項: 別方式の大型Trial並行起票はしない。今回の1本の逐次探索
Trialの中でのみ扱う)。

## Idea 1: 検索結果URLに「個別記事permalinkのみ」を明示指示する

- 何を疑ったか: Round1の12候補のうち3件(チワワ納豆/オリックス珍
  グッズ/NZ鳥チャタムヒタキ)が、livedoor/CNN.co.jpの一覧・カテゴリ・
  キーワードページURLを返しており、個別記事が特定できなかった。
- なぜ試したか: このままではSource品質検証(verify step)が機能せず、
  Topic自体は良くてもSourceが弱いまま残ってしまう構造的な問題だと
  判断したため、SEARCH_DEVELOPER(検索担当のdeveloper prompt)に
  「一覧/カテゴリ/タグ/キーワードページは候補として使わない」旨を
  明記する変更をRound2以降に反映した(Round1結果は事後変更しない)。
- 結果: Round2以降のcandidate内、一覧ページURLの再発件数で効果を
  確認する(§3のRound2ログ参照)。
- 費用: 追加費用なし(プロンプト文言変更のみ、API呼び出し構造は不変)。

## Idea 2: Source Gateを機械signalのみにし、LLM分類callを省略する

- 何を疑ったか: Trial-03はSource Gateに毎回1 Luna分類callを使っており、
  費用を圧迫する一因だった。今回は費用上限が¥150とTrial-03(¥200)より
  厳しいため、Search callに予算を優先配分したいと考えた。
- なぜ試したか: 委任文の設計で「Source Gateは機械signal+Sonnet判断」と
  明記されており、Sonnet(このエージェント自身)が既に各候補のtitle/
  summary/urlを読んで判断できる立場にあるため、追加のLLM callを挟まず、
  正規表現による機械signal(PR/UGC domain)だけをスクリプト側で計算し、
  最終のkept/dropped判断はpool_updates_round{n}.jsonへ直接記録する設計
  にした。
- 結果: 5ラウンドで機械signal専用のgate callは0円。Search call20本に
  予算の大部分(¥112.52)を使い切れた。Round3のgate結果(R3_008の
  'prd'誤検出等)から、機械signalだけでは誤検出・見逃しの両方が起き
  うることを確認し(§9参照)、Sonnet目視判断の必要性を実地で確認できた。
- 費用: 削減額はTrial-03のgate1/gate2実績(各1 call、詳細な金額は
  Trial-03のcost.json参照)相当。本Trialでは発生していない。

## Idea 3: 判断の事後修正(Round3でdropした候補をRound5で読み直しkeepへ変更)

- 何を疑ったか: Round3時点で「Tech/AIクラスタ過多になるかもしれない」
  という懸念だけでR3_002(AI営業研修、初受注1年→5カ月短縮)をdropした
  が、これは実際のクラスタ比率を確認する前の予防的判断だった。
- なぜ試したか: Round5終了時点でPool全体を見直したところ、Tech/AI型は
  実質0件になっており、当初の懸念(過多)は結果的に発生していなかった。
  「固定Laneに固執せず、探索結果を見て判断を更新する」という本Trialの
  基本思想に沿って、Sonnet自身の過去の判断を再検証し、入替を行った。
- 結果: R3_002をkeepへ変更したが、その後のverify step(公開日時検証)で
  window外(実行開始時刻より後に公開)と判定され、最終的には不採用と
  なった(§5参照)。判断の当否とは別に、時間窓検証で失格したという
  結果は、逐次探索の判断修正だけでは補えない制約(検証ステップの
  独立性)を示す実例になった。
- 費用: 追加費用なし(新規API呼び出しなし、pool.json更新のみ)。
