# 診断: OPEN-228(Hormuz Advanced「Main Story段落数<2」RuntimeError)切り分け

管理ID: FAMILY-X-CONCRETENESS-AN3-T0-PRODUCTION-WIRING-01(修正1回目=診断のみ、委任 _03)。
性質: 診断のみ(コード・Prompt・SSOT・REPORT・出力ディレクトリは一切変更していない、読み取りのみ)。
API支出: ¥0(LLM/TTS/ASR呼び出しなし。すべて既存ファイルの読み取り・ローカル集計のみ)。

## 1. チェックの実体

- `er003_v1_n3_01_scaffold_generate.py::split_article_text()`(107-162行)。
  - 138-142行: `paragraphs = [p.strip() for p in intro_text.split("\n\n") if p.strip()]`
    `if len(paragraphs) < 2: raise RuntimeError(f"Main Storyの段落数が2未満です(検出数: {len(paragraphs)})")`
  - 段落の定義=空行(`\n\n`)区切り。閾値=2以上必須(intro_text=タイトル直後〜最初の`###`見出し前)。
- 呼び出し元: `er012_e_family_entertainment_two_level_runner_01.py::run_writer_stage()` 350-351行。
  `save_text(f"{b1b_dir}/article.md", advanced_text)` の直後に
  `save_json(f"{b1b_dir}/parts.json", sc.split_article_text(advanced_text))` を**try/exceptなしで**呼んでいる。
  RuntimeErrorはそのまま呼び出し元(runner全体)まで伝播し未捕捉。article.mdは保存済みだがparts.jsonは未生成のまま停止する。standard(a2)側も419行で同型(未捕捉)。
- 既存`vfl01.run_writer_with_technical_retry()`(`generate_advanced_adaptation()`内部、`er003_v1_n3_01_advanced_adaptation_generate.py` 450-464行)は`er002_ja_free_markdown_restore_r2.py::validate_point_structure()`(58-87行)をGateとして使うが、**そのチェックは`###`見出しがちょうど2つか・各見出しのheading/bodyが非空かのみ**(62-84行、`h3_count != 2`判定と空チェック)であり、Main Storyのintro段落数は一切見ていない。すなわち段落数チェックは既存retry機構の対象外(runner側の後段でノーガードのまま実行される)ことを確認した。

## 2. Advanced Promptの指示状況

- `er003_v1_n3_01_advanced_adaptation_generate.py`をGrep(`paragraph|段落|Main Story|introduction|###`)。
  - 110-117行 `ADVANCED_ARM3_BLOCK`(Adaptation level: NATURAL ENGLISH、build_prompt内で無条件使用、343-349行)内に
    `"You may reorder, merge, or reshape paragraphs, and adjust the wording of metaphors where English needs it."`
    という文言が存在する。段落を「2つ以上に保て」という指示は**存在しない**。むしろ段落のmerge(統合)を明示的に許可している。
  - このARM3ブロックは`git log --follow`で確認した限り、AN3-T0配線タスクではなく前身コミット`0e028301`
    (NEWS-ADVANCED-A2-PRODUCTION-E2E-WIRING-01)由来であり、AN3配線(`1f47ff72`ほか)による変更は含まない
    (Advanced Prompt本体は無変更、REPORT §13の記述と一致)。
- 判定: このチェックはPromptに裏付けのない潜在的脆弱性であり、AN3配線の有無にかかわらず以前から存在した(Promptが明示的に段落merge=1段落化を許可しているため)。

## 3. 配線前の実績(段落数集計、機械計測・API不要)

`title直後〜最初の###まで`の段落数(空行区切り)をPythonで機械集計した。

| 記事×run | intro段落数 | 合計段落数 | 文字数 | 備考 |
|---|---|---|---|---|
| Meta `er012_output/e_family_two_level_wiring_01/meta/b1b/article.md`(配線前) | 4 | 12 | 1920 | PASS |
| Hormuz `er019_output/family_x_b3_diversity_trial_01/hormuz/run_02/b1b/article.md`(配線前) | 4 | 12 | 2020 | PASS |
| Hormuz `er038_output/tts_all_spoken_role_style_trial_01/hormuz/b1b/article.md`(配線前、上と同一内容=既存合格Master reuse、文字数一致) | 4 | 12 | 2020 | PASS(reuse) |
| Hormuz `an3_t0_wiring_regression_01/hormuz/b1b/article.md`(配線後、本番失敗run、2回目=must-fix後の最終text) | **1** | 11 | 1822 | **FAIL(本番)** |
| Meta `an3_t0_wiring_regression_01/meta/b1b/article.md`(配線後、本番PASS) | 2 | 14 | 2148 | PASS(ぎりぎり) |
| Trial-02 Hormuz AN2-T0(`er039_output/.../hormuz/cells/AN2-T0_en.md`) | **1** | 9 | 1814 | (Trial-02はこのチェックを実行するパイプラインではない、参考値) |
| Trial-02 Hormuz AN2-T1 | **1** | 14 | 2024 | 同上 |
| Trial-02 Hormuz AN3-T0 | 4 | 11 | 1764 | 同上 |
| Trial-02 Hormuz AN3-T1 | 3 | 10 | 1760 | 同上 |
| Trial-02 Meta AN2-T0 | 2 | 13 | 1880 | 同上 |
| Trial-02 Meta AN2-T1 | **1** | 12 | 1744 | 同上 |
| Trial-02 Meta AN3-T0 | 5 | 13 | 1826 | 同上 |
| Trial-02 Meta AN3-T1 | 5 | 13 | 1966 | 同上 |

注: `hormuz__run_06_flashlite_full_kp`(委任文が指定した配線前Production参照先)は当時
3幕構成scaffold(Act One/Two/Three形式、`parts.json`のkeyが`part1/heading1/body2/part2/
heading2/body3/part3`)であり、現行`split_article_text()`(2点構成+In one line)とは別schema。
生のarticle.md自体も保存されておらず(WAV/JSONのみ現存)、直接比較不可と判明したため上表からは除外した。

集計コマンド(全て読み取り専用、scratchpad配下):
`C:\Users\tensh\AppData\Local\Temp\claude\C--Users-tensh-eigo-radio\f1538907-8efe-486d-9790-ef5c6cd789fa\scratchpad\count_paras.py`
(タイトル直後〜最初の`###`前を`\n\n`区切りで段落数カウント、上表の全行を1回のPython実行で出力)

## 4. 過去の同一失敗の有無

- `git log --oneline -S "段落数" -- "*.md" | head -20` → 本件のAN3配線コミット(`1f47ff72`)以外に
  この特定チェックへの言及なし。他のヒットは無関係な文脈(語彙Trial等での"段落数"という別用法)。
- `DECISION_LOG.md:5877`に既存の別種の技術的発見あり: `split_article_text()`のintro_text抽出が
  `## In one line…`以外の`## `見出し行を除去しない仕様のため見出し文字列が本文へ混入する不具合
  (OPEN-165、`er011_output`配下)。ただしこれは段落数<2 RuntimeErrorとは別種の不具合(混入であり
  クラッシュではない)。
- `DECISION_LOG.md:8096`(OPEN-165)も同種(混入、クラッシュではない)。
- リポジトリ全体を`段落数が2未満`(RuntimeErrorの実際の文言)でGrepした結果、
  `er003_v1_n3_01_scaffold_generate.py`(定義元)以外に一致するファイルは0件。
  例外は未捕捉のため標準出力にしか出ず、ログファイルとして保存される仕組みがないことが
  原因と推測される(traceback保存のしくみ自体が無い)。
- 結論: 本チェック(段落数<2)がクラッシュを起こした記録は、SSOT・過去ログ上で今回(OPEN-228)が
  **初めて確認された事例**。ただし「保存されないタイプの失敗」である以上、配線前に同種の失敗が
  発生していたが記録に残らず単に再実行されていた可能性は排除できない(悪魔の証明)。

## 5. AN3 JA記事の構造比較

- Hormuz JA R2(AN3、REPORT §本文全文転記、177-193行)と配線前Hormuz JA(run_06相当、article.md自体
  現存せずJA本文比較は不可)は直接比較できなかった。
- Trial-02 Hormuz JA(`cells/AN3-T0_ja.md`「原油市場の主役は、消えた二割の請求書…」)と
  本番`an3_t0_wiring_regression_01/hormuz`のJA R2(「二割の料金案は撤回。それでも原油価格は
  すぐ戻った…」)は、同一の元ニュース(Hormuz海峡20%料金案)を扱うが**文面自体が異なる**
  (別生成、LLMのサンプリング差)。すなわち「同一AN3-T0条件」でも生成のたびにJA文面が変わり、
  それがAdvanced Englishの段落分割にも波及し得る。
- Trial-02のAN3-T0 Hormuz EN本文(`cells/AN3-T0_en.md`)はintro段落数4で明確にPASSしている
  (このTrial-02パイプラインが実際に`split_article_text()`のチェックを実行していたかは未確認だが、
  仮に実行していたとしても4段落はPASSする水準)。一方、本番`an3_t0_wiring_regression_01`の
  Hormuz Advanced(同じくAN3-T0ニュアンス)はintro段落数1で2回連続FAIL。
  **同じ「AN3-T0」ラベルでも段落数が1〜4の間でばらついており**、AN3条件そのものが段落数を
  一意に決定してはいない(生成ごとの確率的ばらつきが大きい)ことを示す実測値。

## 6. 切り分け判定

**(a) AN3起因の可能性: 低〜中**
根拠: Trial-02の実測(表3参照)では、AN3セル(4件: Hormuz T0=4, T1=3, Meta T0=5, T1=5)は
一度も1段落に落ち込んでいない(最小3)。むしろAN2セル(4件: Hormuz T0=1, T1=1, Meta T0=2, T1=1)の
方が1段落への収縮が3/4件と高頻度に発生している。もしAN3が「JA導入部を短くし、Advanced化で
導入部を1段落へ圧縮する」系統的効果を持つなら、Trial-02のAN3セルでも同様の収縮が見られるはずだが
観測されていない。この限られたサンプル(Hormuz/Meta×2試行ずつ)からは、AN3が段落収縮の直接原因
とする仮説は支持されない。ただし本番の実際の失敗事例(Hormuz、AN3-T0)は含まれていないサンプル
(Trial-02とは別生成)であり、"低"と断定するには材料不足のため"低〜中"とした。

**(b) 配線前からの偶発ばらつきの可能性: 中〜高**
根拠: ①Advanced Prompt(ARM3ブロック)はAN3配線以前(`0e028301`)から「段落のreorder/merge」を
明示的に許可しており、この許可自体が段落数の予測不能性を生む構造的要因である(2の判定)。
②同一の「AN3-T0」ラベル内でもintro段落数が1〜4とばらつく(5参照)ことは、LLM生成の
サンプリング分散が支配的であることを示唆する。③配線前の比較サンプルはN=2(Meta 1件、Hormuz 1件、
かつHormuz 2件は同一内容のreuseで実質N=1)に過ぎず、「配線前は常に4段落で安定していた」と
主張するには根拠が薄い(たまたま安定していた2サンプルを見ているだけの可能性)。

**(c) 追加サンプルが必要な場合の再実行回数と概算費用**
- Advanced段階のみを対象に、Hormuz固定JAソースからAN2/AN3それぞれ5回ずつ(計10回)再生成し
  intro段落数の分布を比較するのが最小構成。
- 実測コスト参考値: 本番run(`an3_t0_wiring_regression_01/hormuz/cost.json`)ではJA段階
  (original/original_check/r1/r2/r2_check/r2_must_fix/r2_check_retry の7 API呼び出し)合計で
  ¥3.785。Advanced段階のtoken数(raw_usage_log.jsonlより、1回目attemptでinput 1703+output
  6604=8307 tokens、reasoning_tokens 6214)はJA段階の1呼び出しと同程度〜やや多いオーダーであり、
  Advanced単体のcost_jpyはこのログに直接記録されていない(未確認、価格表参照が必要)。委任文の
  目安¥4/回を使うなら10回で概算¥40程度(未検証の見積り、実測ではない点に注意)。

**(d) 対処選択肢(実装しない、提案のみ)**

| 案 | 内容 | 影響範囲 | リスク | 費用感 |
|---|---|---|---|---|
| ① 既存`run_writer_with_technical_retry`の対象拡張 | `validate_point_structure`と同じGate機構に段落数<2判定を追加し、構造Gate内でretry(既存max_attempts=2の枠内) | `er002_ja_free_markdown_restore_r2.py`(共通関数の可能性)or Advanced固有関数、既存Gate機構への追記のみ | 既存の安全装置(Gate)の対象を広げるだけで無効化ではない。ただし共通関数の変更は他のWriter(Standard等)にも影響し得るため影響範囲の精査が必要 | コード変更のみ、追加API費用なし(既存retry枠内で吸収) |
| ② 段落数チェックを警告化 | RuntimeErrorをwarning+ログ記録に格下げし、生成は継続 | `split_article_text()`本体 | Gate弱体化(非推奨)。1段落のまま本番へ流れるリスクを容認することになり、ユーザーが求める「安定性優先」方針に反する可能性 | 0 |
| ③ Advanced Promptへ導入部2段落の明示を追加 | ARM3ブロックへ「keep at least two paragraphs before the first ### heading」等を追記 | Advanced Prompt本体(英語化Prompt) | **現行Prompt変更はユーザー禁止事項に抵触**(本委任文で明示的に禁止)。ユーザー承認なしに実装不可 | 0(実装しない前提) |
| ④ 何もしない | 現状維持 | なし | Production稼働時に同型クラッシュが再発するリスク(頻度不明、Trial-02実測では条件によらず4/8件で1段落化が発生しており無視できない頻度) | 0 |

## 結論(要約)

- 1: チェックは既存retry機構(`validate_point_structure`)の対象外であり、runner側で未捕捉の
  RuntimeErrorとして伝播する構造的欠陥を確認。
- 2: Advanced Promptは段落数維持を指示しておらず、むしろmerge許可により1段落化を助長し得る
  (AN3配線とは無関係にPrompt側に以前から存在)。
- 3-5: 実測データ(Trial-02 8セル+本番2記事+配線前2記事)では、AN3セルは一度も1段落化していない
  一方AN2セルは4件中3件が1段落化しており、AN3が原因とする仮説は支持されにくい。ただし本番の
  実際の失敗はAN3-T0ラベルの生成であり、サンプル間で条件をまたいだ直接比較はできていない。
- 6: 総合判定は(b)偶発的ばらつき(Prompt起因の予測不能性)が(a)AN3起因より優勢。ただし双方とも
  サンプル数が少なく確定的ではない。
