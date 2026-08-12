# ER-003-JP-STYLE-AUDIT-01 実行報告(阪神マスター方式・日本語記事生成フロー監査)

**管理ID: ER-003-JP-STYLE-AUDIT-01**
**実施日: 2026-08-12**
**ステータス: `AUDIT COMPLETE`(read-only監査のみ。コード・prompt・仕様・音声・文書はいずれも変更していない)**

## 1. 結論

ユーザーの記憶は**大筋で正しかった**。実際に、阪神タイガース記事(マスター)を
モデルへ**全文渡し**、比較的**短い指示文**(「このセンスで書いてください」程度)
だけで複数トピックの日本語記事を生成する方式が実在し、その成果物と実プロンプト
がリポジトリに残っている。

ただし記憶と異なる点が3つある。

- 「6トピック」は、ユーザーの依頼文(`original_request.txt`)に列挙された
  トピック数としては正しい(6件)。しかし**実際に生成された最終成果物は7記事**
  で、依頼文の6件のうち1件(熱中症警戒アラート)は生成されておらず、代わりに
  ワールドカップ記事(現ER-003 A01)と英国SNS記事(現ER-003 A02)という、
  依頼文には無かった2記事が加わっている。
- 「短い指示」は事実だが、**完全に固定ではなく段階的に育った**。最も短いのは
  R1版(15行)で、最終採用版(R4「条件L」)では文字数目標という**1種類の制約**
  が追加された。ただし「文体・語彙・構文の詳細ルール」は最後まで一切追加され
  なかった(4節・8節で詳述)。
- **ユーザーが挙げた「阪神記事に含まれるか」という問いへの回答は「含まれない」**
  ——阪神マスターは常に参照専用であり、7記事のいずれにもカウントされていない。

## 2. 6トピックの実体

| 記事ID | トピック | 状態 | ファイル |
|---|---|---|---|
| A01 | 2026年W杯準決勝 イングランド対アルゼンチン | 生成済み(現ER-003 A01の起点) | `er002_output/v1_2m_j1/A01/rendered_article.md`(J1版)、`er002_output/v1_2m_r4/condition_l/A01/reading_copy.md`(最終R4版) |
| A02 | 英国16-17歳向け夜間SNS設定 | 生成済み(現ER-003 A02の起点) | `er002_output/v1_2m_j1/A02/rendered_article.md`、`er002_output/v1_2m_r4/condition_l/A02/reading_copy.md` |
| ADD01 | 警視庁トクリュウ「案件屋」全国初摘発 | 生成済み(J1のみ、R4には引き継がれず) | `er002_output/v1_2m_j1/ADD01/rendered_article.md` |
| ADD02 | 参議院 皇室典範改正特別委審議 | 生成済み(同上) | `er002_output/v1_2m_j1/ADD02/rendered_article.md` |
| ADD03 | トランプ大統領ホルムズ海峡20%課税撤回 | 生成済み(現ER-003 ADD03の起点) | `er002_output/v1_2m_j1/ADD03/rendered_article.md`、`er002_output/v1_2m_r4/condition_l/ADD03/reading_copy.md` |
| ADD04 | 第175回芥川賞・直木賞決定 | 生成済み(J1のみ) | `er002_output/v1_2m_j1/ADD04/rendered_article.md` |
| ADD05 | 75歳以上老老介護37.1% | 生成済み(J1のみ) | `er002_output/v1_2m_j1/ADD05/rendered_article.md` |
| (未生成) | 関東等 熱中症警戒アラート(富山39℃) | **依頼文に記載はあるが、成果物としては発見できず** | 該当ファイルなし |

- **阪神タイガース記事自体はこの7記事に含まれない**(マスターとして別枠)。
- **バージョンの関係**: J1(2026-07-15?、7記事初回一括生成)→R2(A01/ADD01-05の
  再検証、ADD01/02/04/05はR2止まり)→R3(A01/A02/ADD03の3記事のみに絞り込み、
  Web検索をwriter呼び出しに統合)→R4(同じ3記事で「条件L」(1記事1回実行+
  文字数指示)と「条件LB」(3記事同時生成)を比較、**条件Lを正式採用**
  (`2ed7f59`, 2026-07-19)。この時点でADD01/02/04/05は正式フローから外れた。
- 当時の管理ID: `ER-002-v1.2M-JA`(J1)→`ER-002-v1.2M-R1`〜`R4`
  →`ER-002-v1.2M-R4-FINALIZE`(正式採用)。reportは各`ER-002-v1.2M-R*_user_review.md`。
- 「ER-001 口調比較」という名称のreport・commitはリポジトリ内に**発見できなかった**
  (`git log --all --grep`で該当なし)。既存の`ER-001B-*`は音声のダイナミクス・
  ナレーター比較実験であり、日本語記事の文体比較とは別物。ユーザーの記憶する
  「口調比較・6トピック」は、本節で述べた`ER-002-v1.2M-JA`〜`R4`のことを
  指している可能性が高いと判断する(**推定**であり、断定はしない)。

## 3. 阪神マスター

- **ファイル名**: `hanshin_ja_master.txt`
- **保存場所**: `er002_v1_2m_masters/hanshin_ja_master.txt`(sha256固定、
  `masters_sha256.json`で照合)
- **段階**: 完成済みの読み上げ本文(reading copy相当。見出し・本文・
  「今日の虎ポイント」×2・「一言で表すなら」の完成形。draft注記やtopic
  packageの痕跡はない)
- **該当本文**: 中日6-5阪神の敗戦を扱った記事(2節参照、全文は同ファイル)
- **「マスター」として明示的に使われていた証拠**: `original_request.txt`
  冒頭「オリジナルが一番良いです...このセンスで複数トピックを上げてみて
  再現性や記事の揺れを見てみたいです」、および`er002_ja_master_imitation.py`
  ・`er002_ja_article_generation.py`双方でこのファイルをプロンプトへ
  `master_full_text`として直接埋め込む実装
- **全文か要約か**: **全文をそのままプロンプトへ渡していた**(要約・特徴抽出
  ではない)。J1版(`er002_ja_master_imitation.py`)・R1〜R4版
  (`writer_prompt_template*.txt`)のいずれも`{master_full_text}`の
  プレースホルダーに全文を埋め込む設計
- **転写されていた特徴(依頼文・プロンプト内で明示された理由)**:
  「全体の概要を面白く展開」「今日の虎ポイントで、別切口でも解説」
  「一言で表すなら、でサマリー」「聞き手があきない設計」の4点。7記事の
  実際の見出し(例: A01「一言で表すなら」、ADD01「一言で表すなら」等)を
  確認したところ、いずれも阪神マスターと同じ「概要→2ポイント→一言まとめ」
  の3部構成を踏襲していた
- 阪神固有の比喩(「虎」「竜」等)そのものは転写されておらず、プロンプト側で
  明示的に「阪神や野球固有の表現をコピーするのではなく」と禁止していた

## 4. 実プロンプト

**A. 実際に残っている原文(最終採用版=条件L、`er002_ja_article_generation.py`
+ `er002_v1_2m_restore_briefs/`)**

R3ベースの本体プロンプト(`writer_prompt_template_r3.txt`、web検索は
writer自身が同一呼び出し内で実施):

```
以下は、私が良いと評価している日本語記事です。

【マスター記事】

{hanshin_master_full_text}

【今回のテーマ】

{topic}

この阪神記事が良いのは、全体の概要を面白く展開し、ポイントでは本文とは別の
切り口から解説し、最後に一言でまとめることで、聞き手が飽きない設計になって
いる点です。

今回のテーマについて必要な情報をWebで調べてください。検索内容や検索回数、
何を記事の中心にするか、どの事実を本文と二つのポイントに使うかは、あなた
自身で判断してください。

調査から記事作成までを一つの作業として行い、このセンスで今回のテーマの
記事全文をMarkdownで書いてください。

阪神や野球固有の表現をコピーするのではなく、今回の題材に合う表現を使って
ください。

ポイント部分には、Markdownの「###」見出しをちょうど2つ置いてください。
```

R4で追加された長さ指示3文(`length_instruction_suffix_r4.txt`、末尾へ結合):

```
記事本文は、引用表記を除き、阪神マスターの読み上げ対象本文と同程度の
分量にしてください。
目安は{master_count}字、許容範囲は{lower_bound}字から{upper_bound}字です。
調べた情報をすべて盛り込まず、記事の面白さに必要な情報だけを選んでください。
```

**B. コード内prompt**: `er002_ja_article_generation.py`
`build_writer_user_message()`(238-247行)がR3テンプレート+長さ指示を結合。
実際のweb検索・writer本体呼び出しは`er002_ja_web_research_r3.py`
(`make_writer_research_fn`/`build_writer_user_message_r3`、このモジュールは
R3から不変のまま再利用)。より初期の別実装(`er002_ja_master_imitation.py`
129-144行、`MINIMAL_JA_GENERATION_PROMPT_TEMPLATE`)も存在するが、こちらは
Web検索を使わずJSON構造化出力で生成する設計で、実際にはR2以降で使われず
(J1版のみで使用された可能性が高いが、J1のraw実行スクリプトを直接特定する
証拠は見つからなかった。**推定**)。

**C. report/history内の記録**: `original_request.txt`(ユーザー原文そのもの、
2節参照)、`ER-002-v1.2M-R4-FINALIZE`commit(`2ed7f59`)・
`d769d31`が条件L採用・条件LB不採用の理由を記録。

**D. 推定**: J1版(7記事初回一括生成)で実際にどちらのプロンプト実装
(`er002_ja_master_imitation.py`のJSON構造化出力版か、`er002_ja_web_research_r3.py`
のWeb検索版か)が使われたかは、J1の生成スクリプト実行ログから確定できなかった
(**推定**: J1の出力にWeb検索由来と見られる具体的事実が多く含まれること、
かつADD01(トクリュウ)等は阪神マスターと無関係の固有名詞・数字を多数含む
ことから、何らかの形でWeb検索相当の情報収集を伴っていたと推測されるが、
J1固有の実行スクリプトファイルは特定できなかった)。

## 5. 当時の生成フロー(R3〜R4、現ER-003 A01/A02/ADD03の実際の経路)

```
[阪神マスター全文 + 依頼トピック文字列(人間が手書き)]
        ↓
[writerモデル1回呼び出し(OpenAI Responses API、web_search toolあり)]
   ・調査(何を検索するか・何回検索するかはモデル自身が判断)
   ・記事執筆
   を同一呼び出し内で実施(topic packageのような中間JSON成果物は生成されない)
        ↓
[raw_article.md / reading_copy.md]
        ↓
[独立fact checker(別モデル呼び出し、PASS/REVIEW_REQUIRED/FAILを判定)]
        ↓
[reading_copy.md確定](条件L採用版、A01/A02/ADD03)
        ↓ (ER-003-P1B、2026-07-20、commit 45c48ee)
[ER-003-P1B: 固定構造付き英訳]
        ↓
[Natural English Source確定]
        ↓
[B1/B2/A2各レベル生成へ](現行ER-003が実際に使用中)
```

## 6. 現在の上流フロー(2026-08-12時点、main上)

```
キーワード
   ↓  ※自動接続なし(下記(a)(b)は独立した別系統)
   ├─ (a) gather_topic.py --genre="..."
   │      ・実装済み・現在は不使用(A01/A02/ADD03の生成には使われていない)
   │      ・出力: topic_package_*.pyファイル(TOPIC_PACKAGE辞書)
   │      ・接続先はgenerate_test.py(v9.0、LEO/MAYA系の別番組向け汎用パイプ
   │        ライン。generate_test.py自体はER-003本編とは異なる企画・構成表
   │        ・台詞化・論理検品という多段工程を持つ)
   │
   └─ (b) 人間がトピック文字列を手書き(実際にA01/A02/ADD03で使われた経路)
          ↓
   [er002_v1_2m_generate_article.py <topic_id> "<topic文字列>"]
          ・実装済み・現在使用可能(CLIとして汎用: 任意のtopic_idと
            トピック文字列を受け付ける)
          ・半自動: 記事探索(Web検索)はwriterモデルが同一呼び出し内で
            自律的に実施。人間が用意するのはトピック文字列だけ
          ↓
   [reading_copy.md](記事ごとに`er002_output/v1_2m_article_generation/`等)
          ↓
   [ER-003-P1B: er003_v1_p1b_generate.py <topic_id>]
          ・実装済みだが**topic_idがp1b.APPROVED_ARTICLE_SOURCE_PATHSに
            事前登録されている場合のみ動作**(A01/A02/ADD03の3件のみ登録済み)
          ↓
   [Natural English Source] → 現行ER-003 B1/A2パイプラインへ接続済み
```

各工程の状態:

| 工程 | 状態 |
|---|---|
| キーワード→ニュース候補探索 | (a)系統は実装済みだが現在使用中ではない。(b)系統は自動化されておらず、人間がトピック文字列を書く運用のまま |
| ソース収集 | (b)系統では半自動(writerモデルが自律的にWeb検索、人間は検索クエリ・情報源を指定しない) |
| topic package生成 | (a)系統のみ存在。(b)系統(実際にA01/A02/ADD03で使われた経路)にはtopic package相当の中間成果物が存在しない |
| 日本語draft生成 | 実装済み・現在使用可能(条件L、`er002_v1_2m_generate_article.py`) |
| reading_copy生成 | 実装済み・現在使用可能(条件Lのwriter呼び出しが直接reading_copy.mdを出力) |
| reading_copy→Natural English Source | 実装済みだが**新規topic_idには未対応**(登録制、半自動) |

## 7. ER-003との接続判定: **PARTIAL**

- 日本語記事生成(阪神マスター方式・条件L)→`reading_copy.md`→
  ER-003-P1B→Natural English Source→B1/A2、という経路は、**A01/A02/ADD03の
  3記事については既に実際に接続・実行済み**(2節・5節参照)。
- 新しいトピック(4件目以降)を同じ経路に流す場合、次の1点だけが障害になる。
  - `er003_ja_to_en_translation.APPROVED_ARTICLE_SOURCE_PATHS`
    (および`er003_ja_to_en_translation_p1b.py`が参照する同名の辞書)に
    新しいtopic_idのファイルパスを追加登録する必要がある。これはコードの
    小さな追加(辞書へのエントリ追加)であり、方式の再設計は不要
- 上記以外(阪神マスター・条件L本体・fact checker・P1B構造)は**そのまま
  再利用可能**であり、大規模な再実装は不要
- よって**READY(完全に無変更で使える)ではないが、NOT READY(再設計が必要)
  でもない**。**PARTIAL**と判定する

## 8. 仮説A〜D

| 仮説 | 判定 | 根拠 |
|---|---|---|
| **A**: 阪神記事をfew-shot/referenceとして渡し、短いinstructionで複数ジャンルへ転写していた | **SUPPORTED** | 4節の実プロンプト原文で確認。マスター全文+短い指示(15〜20行程度)のみで、詳細な文体・語彙ルールの列挙は一切ない。R4で追加されたのは文字数目標という量的制約1点のみ |
| **B**: 実際には裏で詳細なstyle ruleがあり、「短い指示だけ」という記憶は表面的だった | **NOT SUPPORTED** | R1→R4の全プロンプト版(4種)を確認したが、いずれも15〜37行に収まり、「短い指示」から「詳細ルール集」への質的な変化は確認できなかった。増えたのはWeb検索の自律化・文字数制約・構造(見出し数)制約という、文体そのものとは別種の制約のみ |
| **C**: 記事探索はgather_topic.py等で既に自動化されていたが、日本語記事生成との接続は手動だった | **NOT SUPPORTED** | A01/A02/ADD03の実際の生成経路(R3〜R4条件L)では、gather_topic.pyは一切使われていない。writerモデル自身がOpenAI Responses APIのweb_search toolで同一呼び出し内に検索を組み込んでおり、gather_topic.pyが生成するtopic package形式の中間成果物は存在しない。gather_topic.pyは別系統(generate_test.py向け)として実装済みだが、日本語記事生成(条件L)とはコードレベルで一切接続されていない(「手動接続」ですらなく「非接続」) |
| **D**: 過去方式は現在のreading_copy.md入口へ比較的容易に再接続できる | **PARTIALLY SUPPORTED** | A01/A02/ADD03の3記事については「再接続」ではなく**既に接続済み**(実行済み)。新規トピックについては、P1B側の登録辞書へのエントリ追加のみで足りる見込みだが、実際に新規topic_idで試したことはまだない(未検証)ため、「容易」との断定は避け、PARTIALLY SUPPORTEDとする |

## 9. A2音声保留

`ARTIFACT_REGISTRY.md`・`OPEN_ITEMS.md`・`DECISION_LOG.md`・
`CURRENT_SPEC.md`・`PROJECT_INDEX.md`を検索したが、「音声最新化を意図的に
夜間へ保留する」旨の記述は**見つからなかった**。

現在Source of Truthに存在するのは、[OPEN_ITEMS.md](OPEN_ITEMS.md)の
**OPEN-35**(2026-08-12新設、ER-003-A2-SCRIPT-FINAL-01)で「script確定済み
だが3記事とも音声は未再生成」という**事実**のみが記録されており、
「夜間にまとめて処理したいため保留している」という**理由・意図**は記録
されていない。

本監査はread-only制約のため、この記録不足を**修正せず、報告のみ**とする。
今回の監査中、音声関連ファイルの生成・更新は一切行っていない。

## 10. 次に必要な最小作業(実装はしない、提案のみ)

監査結果を踏まえると、「日本語記事の魅力は詳細ルールではなく良いマスター
記事で作られていた」ことが裏付けられた(8節、仮説A SUPPORTED / B NOT
SUPPORTED)。したがって、新しいルールを大量に追加する方向には進まず、
以下の**最小限の接続作業**だけでE2Eへ進める見込みが高い。

1. **P1B側の登録辞書を汎用化する**: `er003_ja_to_en_translation.APPROVED_ARTICLE_SOURCE_PATHS`
   を、新規topic_id追加のたびにコードへハードコードする現状から、
   `er002_v1_2m_generate_article.py`の出力ディレクトリを走査して自動登録する
   (または設定ファイル化する)方式へ小さく変更する。7節のPARTIAL判定を
   READYへ引き上げる唯一の障害
2. **新規トピック1件で実地検証する**: 上記変更後、A01/A02/ADD03以外の
   実際の新規キーワードを1件選び、条件L→P1B→Natural English Sourceまで
   通しで走らせ、既存3記事以外でも同じ経路が機能するかを確認する
   (仮説DのPARTIALLY SUPPORTEDをSUPPORTEDへ引き上げる検証)
3. **A2音声保留の意図をSource of Truthへ明記する**(9節): 「事実」だけで
   なく「なぜ・いつ実施するか」を[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-35
   へ一文追記することを推奨する(本監査では実施していない、ユーザー判断待ち)
4. **キーワード→トピック文字列の変換は依然として人間依存のまま残す**か
   どうかを判断する: gather_topic.py(a系統)を条件L(b系統)へ接続する
   統合作業は、今回の調査結果からは「必須」ではない(b系統はwriterモデルが
   自律的に調べるため、topic package自体が無くても機能している)。無理に
   統合せず、当面は人間がトピック文字列を書く運用を維持するという選択肢も
   妥当である

## 受入条件14項目

| # | 条件 | 結果 |
|---|---|---|
| 1 | 過去の6トピック相当の成果物を可能な範囲で特定している | PASS(2節) |
| 2 | 阪神マスター記事を特定している | PASS(3節) |
| 3 | 当時の実プロンプトまたは最も近い記録を提示している | PASS(4節) |
| 4 | 実プロンプトと推定を明確に区別している | PASS(4節、A/B/C/Dで分離) |
| 5 | 「短い指示だったか」を証拠ベースで判定している | PASS(8節、仮説A/B) |
| 6 | 現在のキーワード→topic package→日本語記事フローを整理している | PASS(6節) |
| 7 | 各工程の自動/手動/半自動状態を区別している | PASS(6節表) |
| 8 | 阪神マスター方式がどこに接続されていたか示している | PASS(5節) |
| 9 | 現在のER-003 reading_copy.md以降へ接続可能か判定している | PASS(7節、PARTIAL) |
| 10 | 仮説A〜DをSUPPORTED等で評価している | PASS(8節) |
| 11 | コード・仕様・音声・文書を変更していない | PASS(本監査中、Write/Editしたのは本報告書のみ) |
| 12 | A2音声更新の夜間保留状態を把握し、今回実行していない | PASS(9節) |
| 13 | 不明点を推測で埋めていない | PASS(不明箇所は「不明」「推定」と明記、4節D・2節末尾) |
| 14 | 調査した主要ファイル・履歴・report一覧を提示している | PASS(下記一覧) |

## 調査した主要ファイル・履歴・report一覧

- `er002_v1_2m_masters/original_request.txt`、`hanshin_ja_master.txt`、`masters_sha256.json`
- `er002_ja_master_imitation.py`、`er002_test_ja_master_imitation.py`
- `er002_ja_article_generation.py`(正式採用モジュール)
- `er002_ja_web_research_r3.py`(参照のみ、内容はコード内コメント経由で確認)
- `er002_v1_2m_generate_article.py`、`er002_v1_2m_r4_generate.py`
- `er002_v1_2m_restore_briefs/`配下全ファイル(`writer_prompt_template*.txt`、`length_instruction_suffix_r4.txt`、各`*_concise_brief.txt`)
- `er002_output/v1_2m_j1/`、`v1_2m_r1/`〜`v1_2m_r4/`配下の各記事成果物・`ER-002-v1.2M-R*_user_review.md`
- `gather_topic.py`、`er002_topic_adapter.py`、`generate_test.py`、`topic_package_阪神タイガース_2026-07-15.py`
- `er003_v1_p1b_generate.py`、`er003_ja_to_en_translation_p1b.py`、`er003_ja_to_en_translation.py`(`APPROVED_ARTICLE_SOURCE_PATHS`)
- commit: `f90b399`(v1.2M-JA P0)、`21e946f`(R1)、`cd51557`(R3)、`34d1db5`/`2ed7f59`/`d769d31`(R4・FINALIZE)、`45c48ee`(ER-003 Natural English Source確定)
- `git log --all --grep`による「阪神」「口調」「6トピック」検索(ER-001系のヒットなし)
- [OPEN_ITEMS.md](OPEN_ITEMS.md)、[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)、[DECISION_LOG.md](DECISION_LOG.md)、[CURRENT_SPEC.md](CURRENT_SPEC.md)、[PROJECT_INDEX.md](PROJECT_INDEX.md)(A2音声保留記録の有無確認)

## 今回行っていないこと

コード変更、prompt変更、新しい日本語記事生成仕様の策定、新規記事生成、
Web検索の実行、B1/A2生成、TTS生成、音声assemble、OPEN項目のクローズ、
現在仕様の変更、A2音声の更新。
