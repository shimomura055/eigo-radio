# FAMILY-A-DISCOVERY-FOCUS-PART-A-STANDALONE-DESIGN-TRIAL-01_REPORT

管理ID: FAMILY-A-DISCOVERY-FOCUS-PART-A-STANDALONE-DESIGN-TRIAL-01
性質: ¥0設計→最小Trial実施。到達: **VALIDATED**(判定語の最終確定はFableに委ねる)。
**Production配線・CURRENT_SPEC正式仕様化・APPROVED_FOR_PRODUCTIONへの変更は
行っていない**。Production経路のファイルは無編集(git status後述で確認)。

## ユーザー基本設計(原文、再確認不要)

> Focusを先に決める→Main StoryはそのFocusに従う→Pointはその後で、Main Story
> を見ながら独自価値を探す。重要なのは、Point-firstにしないことです。また、
> FocusからPointへ「mechanism / limitation / different angle」等の具体的な
> 角度を強く指定する接続も避けます。今回の案2で見られたA2/B1の角度収束を
> 再発させないことを優先してください。

## 1. 現行Production呼び出し順の事実確認(`er003_v1_n3_01_articles_generate.
   py::run_one_pattern`、818〜1248行)

1. L836: writer_model解決。
2. **L842-846: Point Role Planning(`point_planning.run_point_role_planning`)
   をWriter呼び出しより先に実行**。入力はtopic+verified_ledger_textのみ
   (`er011_point_role_value_planning_01.py` 124-145行、128行の
   `ROLE_PLANNING_PROMPT_TEMPLATE.format(topic=..., verified_ledger_text=...)`
   にMain Story/Focus本文は一切含まれない)。結果は`build_role_planning_block`
   でprompt末尾に追記される。
3. L848-854: `_generate_and_compress_article`でWriterを1回呼び出し、Main
   Story+Point One+Point Two+In One Lineを**まとめて1回で生成**(Evidence
   Compression込み)。
4. L863-949: Point Overlap/Value QA。NGの場合、`POINT_OVERLAP_ARTICLE_
   RETRY_MAX`(=2)回まで、**Point Role Planningを再計画したうえで記事全体を
   Diagnostic Full Retryで再生成**(3の単位ごと繰り返し)。
5. L986-1037: Fact Checker(FAILならNG_REVIEW_REQUIRED、REVIEW_REQUIREDは
   non-blocking advisory)。
6. L1040-1217: Ledger Deviation Check(Hook-aware)+Local Rewrite(MAJOR
   検出時、`local_rewrite.MAX_REWRITE_CYCLES`回まで局所書き換え+OPEN-141
   差分QA)。
7. L1219-1247: Directional Fact Precheck(non-blocking advisory)→戻り値。

分岐点(mode文字列): `editorial_type_module_block`(`resolve_editorial_type_
module_block(editorial_mode)`、452-469行)は現状**`"trend_synthesis"`のみ
Production登録**されている(`EDITORIAL_TYPE_MODULE_BLOCKS`辞書)。
`"discovery"`は未登録(既存Discovery Trialは`build_common_block`の
`editorial_type_module_block`引数へFocus Module Part Aの文字列を直接渡す
形で検証しており、辞書登録=Production採用はまだされていない)。News
(major_daily_news相当)は`editorial_type_module_block`を渡さない既定経路
(空文字列、既存挙動不変)。この分岐機構自体はNews/Trend/Discoveryいずれの
将来対応にも使える汎用placeholderであり、Part A案を配線する場合も同じ
placeholderへ`"discovery"`キーを追加するだけで済む(構造上の新規実装は
不要、ユーザー承認[APPROVED_FOR_PRODUCTION]が必要なだけ)。

**順序矛盾の確認**: ユーザー基本設計は「Point Role PlanningはMain Story
成立後」だが、現行Productionは新規・retry(Diagnostic Full Retry)のいずれの
経路でも「Point Role Planning→Writer(Main Story含む全文生成)」の順で、
Main Storyが存在する前にPoint Role Planningが実行される。これはNews/Trend/
Discoveryいずれの現行経路でも共通(run_one_pattern自体はmode非依存)。

## 2. Part A単独案の配置候補比較

- **案S1(現行順序維持、Focusのみ追加)**: 既存Trial
  `discovery_focus_module_revalidation_01`(A2/B1、既存結果、再実行なし)が
  これに相当する。Point Role PlanningはMain Storyを見ないままFocusなしの
  現行のまま。「Point Role PlanningがMain Story成立後」という要件を
  **満たさない**。角度収束は観察されなかった(4役割とも異なる)が、B1の
  Main Story抑制がやや弱い(既存Report参照)。
- **案S2(2段階生成、Focus→Main Story→Point Role Planning→Point)**:
  ユーザー基本設計を構造的に満たす唯一の案。既存結果では判断できない
  (Point Role PlanningがMain Story本文を読む経路は過去に一度も実行して
  いない)ため、最小Trialを実施(3節)。
- **案S3(現行順序+Main Story側への最小注記のみ、角度指定なし)**:
  順序矛盾は解消しない(Point Role Planningは依然Main Story成立前)。
  既存のROLE_PLANNING_PROMPT_TEMPLATE自体、具体的角度カテゴリの例示
  (「意外な詳細/方法論上のニュアンス/歴史的な対比/心理的な理由」)を既に
  含んでおり、案2の角度収束は**この既存例示ではなく、Trial-04が追加した
  Focus由来の強い角度hint(mechanism/different angle/limitationの3択)**に
  起因していた(`discovery_focus_role_planning_connection_trial_01/
  comparison.md` 211-227行)。S3はS1と実質的に同じであり、追加検証の
  価値は低いと判断し、Trialは実施しなかった。

**推奨: 案S2**。理由: ユーザーが明示した順序要件を構造的に満たす唯一の案
であり、3節のTrial結果でも角度収束の再発なし・新しいfailure modeなしを
確認できた。ただしMain Story抑制自体を改善する設計ではない(4節)。

News/Trend/Discovery既存設計との重複・競合: なし。`run_one_pattern`自体は
mode非依存の共通関数であり、S2はDiscovery専用の新しい呼び出し順(Trial
専用driverでのみ実装、Production `run_one_pattern`は無改変)として設計した。
Trend Synthesis(`editorial_mode="trend_synthesis"`)・News(既定)は本Trialの
影響を受けない。

## 3. 角度収束の再発防止策の整理

- 具体的な角度をhintしない: 案2のTrial-04が追加した「mechanism / different
  angle / limitation」の3択は今回のStage 2 promptに含めていない(2節参照)。
- 「A2とB1で同じ役割の組に固定しない」という制約自体はprompt上で保証でき
  ない(非決定性依存)ため、明示的な禁止文を書かなかった。その代わり、
  Stage 2ではMain Story本文の**実際の記述内容**を根拠にPoint設計させる
  ことで、抽象的な角度カテゴリではなく具体的なLedger/Main Story由来の
  内容に基づく判断を促した。
- 複数記事間の角度多様性はテーマ固有性に依存する(本Trialは単一テーマ・
  各条件1本のみであり、一般化可能性は未確定)。

## 4. Trial実施(最小、¥33.94/上限150円、Discovery残額¥253.53以内)

実行前見積: 既存focus腕生成コスト(A2=13.71円、B1=20.59円)を参考に、
Stage 2(小さいJSON呼び出し)+Stage 3(Point/In One Lineのみ、Main Storyより
出力が少ない)+既存QA一式(Fact Checker/Ledger Deviation/Point Overlap/
Value QA)で、1本あたり15〜25円程度、2本合計30〜50円程度と見積もった。

設計(詳細は`er011_discovery_focus_part_a_standalone_trial_01_run.py`
ヘッダーコメント参照):
- Stage 1(Main Story): 新規生成せず、既存Trial`discovery_focus_module_
  revalidation_01`のfocus腕article.mdからMain Story本文をread-onlyで
  抽出・固定(無駄な再生成コストを払わない)。
- Stage 2(新規LLM呼び出し): Main Story本文を実際に読ませたうえでPoint
  Role Planningを実行(`run_stage2_role_planning`、新規prompt。JSON
  schema/developer message/例外クラスは`point_planning`モジュールを
  無変更で再利用)。
- Stage 3(新規LLM呼び出し): Point One/Two/In One Lineのみを生成
  (`run_stage3_points_writer`、新規prompt。構造検証は`vfl01.run_writer_
  with_technical_retry`を無変更で再利用。この検証は「###見出し2件+本文の
  有無」のみを見るため、Main Story/Titleの有無を問わず安全に再利用できる
  ことを確認済み)。
- 結合: title行+Stage 1 Main Story(無変更)+Stage 3出力の単純連結。両
  記事とも`main_story_reproduced_exactly=true`(結合後にsplitした
  full_storyが元のMain Story本文とbyte単位で一致)を確認。
- 既存QA一式(Fact Checker/Ledger Deviation/Point Overlap QA/Point Value
  QA)はProduction関数を無変更で再利用し、単発実行(retry/Local Rewriteは
  未実装、5節「限界」参照)。

結果:
- A2: status=OK、fact_verdict=PASS、ledger_status=LEDGER_COMPLIANT
  (逸脱0件)、lexical/value overlap flagなし。実費¥16.51。
- B1: status=OK、fact_verdict=REVIEW_REQUIRED(non-blocking advisory、
  解釈ニュアンス3件、`b1b/fact_qa.json`参照)、ledger_status=
  LEDGER_COMPLIANT(逸脱0件)、lexical/value overlap flagなし。実費¥17.43。
- 合計実費¥33.94(上限150円、Discovery残額253.53円に対し十分な余裕)。
- **角度収束の再発なし**: A2 Point One/Two・B1 Point One/Twoの4役割は
  すべて異なる内容だった(比較表は`comparison.md`参照)。案2で観察された
  「A2・BいずれもPoint One=睡眠段階、Point Two=学習された期待」という
  収束は再発しなかった。
- Point Role Planningの入力に実際のMain Story本文が渡った証拠:
  `{a2,b1b}/audit/stage2_role_planning.json`のprompt fieldに実際のMain
  Story本文が埋め込まれていることを直接確認(`index.html`にも抜粋掲載)。

比較artifact: `er011_output/discovery_focus_part_a_standalone_trial_01/
comparison.md` + `index.html`(2記事本文全文・role plan・比較表を含む)。

## 5. 本Trialが再現しなかったもの(限界、正直に記録)

- Point Overlap/Value QA retry(Diagnostic Full Retry)は未実装(単発実行の
  み、fail-closed。本Trialでは両記事ともflagが出ず未発火)。
- Local Rewrite(Ledger MAJOR検出時の局所書き換え)は未実装(本Trialでは
  MAJOR逸脱0件のため未発火)。
- Directional Fact Precheckは未実施。
- Stage 3ではEvidence Compression未適用。

## 6. 確認事項(read-only)

| 論点 | 結果 |
|---|---|
| News/Discovery/Trend既存仕様との競合 | なし。`run_one_pattern`はmode非依存の共通関数。S2はTrial専用driverのみで実装、Production関数は無改変。 |
| Point Role Planningとの実処理順(現行) | Point Role Planning→Writer(Main Story含む全文)。News/Trend/Discovery共通。 |
| retry/fallback/regeneration整合 | S2のretry単位(Stage 1から作り直すか、Stage 2/3のみやり直すか)は未検証・**USER_DECISION_REQUIRED**(Production化する場合に必要、7節)。 |
| Dangling Reference | 新規ファイル`er011_discovery_focus_part_a_standalone_trial_01_run.py`はProduction側から一切importされていない(単方向importのみ、Production未汚染)。 |

## 7. USER_DECISION_REQUIRED(Production化する場合に必要な未解決事項)

Point Overlap/Value QA retryが発火した場合、S2のretry単位を「Stage 1
[Main Story]から全て作り直す」か「Stage 1は固定したままStage 2/3のみ
再実行する」かは、現行Production方式(全体を一体で再生成しRole Planningも
毎回再計画する、`run_one_pattern` L933-939)との整合性を含め、Production
配線前にユーザー判断が必要。本Trialは単発実行のみでこの論点を検証して
いない。

## 8. Git

対象: `er011_discovery_focus_part_a_standalone_trial_01_run.py`(新規)、
`er011_output/discovery_focus_part_a_standalone_trial_01/`(新規出力一式)、
本REPORT、`docs/pm/RESULT_PACKET_DPA.md`。`git add -A`は使用せず、上記を
明示的に指定してadd。Production 3ファイル(`er003_v1_n3_01_articles_
generate.py`、`er011_point_role_value_planning_01.py`、`er006_pool_pilot_
01_writer.py`)・SSOT本文・`docs/pm/ACTIVE_TASK.md`(他タスクが使用中のため
本タスクでは変更しない)は対象外。
