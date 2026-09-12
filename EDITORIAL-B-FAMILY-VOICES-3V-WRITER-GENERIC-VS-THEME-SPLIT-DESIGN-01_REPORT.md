# EDITORIAL-B-FAMILY-VOICES-3V-WRITER-GENERIC-VS-THEME-SPLIT-DESIGN-01

管理ID: `EDITORIAL-B-FAMILY-VOICES-3V-WRITER-GENERIC-VS-THEME-SPLIT-DESIGN-01`。
read-only設計(¥0、API呼び出しなし、コード変更なし)。書き込みは本REPORTの
みで、`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`・SSOT・コードは一切未編集。
Git操作(add/commit/push)は未実施。

## 要点(5行)

1. 2VにもWriter経路は無く(`EDITORIAL-B-FAMILY-VOICES-3V-PRODUCTION-WIRING-
   PHASE1B-03_REPORT.md`の結論を本タスクで再確認、runner未変更)、これは
   3V固有ではなく**B-Family共通の配線ギャップ**である。
2. Trial-02 Focus Module(330行)を全行分解した結果、大半(約7割)は
   registry/CURRENT_SPEC/design.md(Trial-03、Gate1 VALIDATED)・
   OPEN-131(`PRODUCTION_WIRED opt-in`)に根拠のある3V共通原則、約2割は
   Voice Card等の完全なテーマ固有内容、そして**新たな発見として1項目
   (`leak_tension_constraint_integration`)がコード内コメントで「3V
   新規」と自己申告**しており、これが最有力の「3V専用の新Writer原則」
   候補である。
3. Ledger作成は、PHASE1B-03報告が想定した「vfl01の`topic`引数を通すだけ」
   より深刻な未配線がある: Trial-02が実際に使ったLedger本文
   (`verified_fact_ledger.txt`)は、第3のスクリプト
   (`er012_ai_screening_ledger_trial_01.py`、Perplexity・テーマ完全
   ハードコード)のraw fact JSON出力を**人手でcurationした結果物**であり、
   自動生成関数は存在しない。
4. `[VOICE_n_EVIDENCE]`タグ形式自体はOPEN-131で`PRODUCTION_WIRED(opt-in)`
   済みの承認済みschemaのため、これを新テーマへ再利用すること自体は
   「Ledger意味変更」に当たらない。
5. 推奨は代替案Aの精緻化版(案A′): (a)のみを3V共通prompt定数として固定、
   (b)はVoice Card/Ledger生成という**人手主導の設計セッション**の出力を
   機械的に差し込む薄いテンプレート化、(c)は個別にユーザー判断を仰ぐ。
   判断点は最小2つ(7節)。

## 1. 2Vの現状確認

`er012_b_family_production_runner_01.py`を本タスクでも再確認した(前回
PHASE1B-03報告時点から無変更、下記grep結果)。

```
63:ARTICLE_PATH = "er012_output/editorial_b_voices_trial_07/b1b_run02_attempt2/article.md"
159:def prepare() -> dict:
659:def prepare_3v() -> dict:
1033:def main_b1_3v() -> None:
1495:def main() -> None:
```

`main()`(2V)・`main_b1_3v()`(3V)いずれも、固定パス(`ARTICLE_PATH`)から
既承認記事を読み取るだけで、新規テーマからの記事生成(Research→Ledger→
Writer)経路はrunner内に存在しない。過去の2V実記事はTrialスクリプト
`er012_editorial_b_voices_trial_07.py`で生成された。**結論: 「Writer/
Ledger未配線」はB-Family(2V・3V共通)の設計ギャップであり、3V固有の
問題ではない**(PHASE1B-03報告1節と同一結論、本タスクで独立再確認)。

## 2. Writer指示文の行単位分解

Trial-02 `B_FAMILY_VOICES_3V_FOCUS_MODULE_BLOCK`(該当ファイルL266-598、
332行)を全文読了し、論理ブロック単位(1行単位では330行の表になり可読性を
損なうため、意味の途切れる最小単位=段落・箇条書きブロックで分割。ブロック
内で分類が割れる場合はさらに分割した)でタグ付けした。

凡例: (a)=3V共通原則(既存SSOT・registry・design.md[Trial範囲VALIDATED]・
OPEN-131[PRODUCTION_WIRED]に根拠あり)/ (b)=AI採用選考テーマ固有内容 /
(c)=判定不能(根拠なし、新原則の疑い)

| 行範囲 | 内容要約 | 分類 | 根拠 |
|---|---|---|---|
| L266-268 | ヘッダーコメント(Trial-01からの差分説明) | 管理用メタ | 分類対象外(指示文ではない) |
| L269-275 | 「Voices/Perspective型は一般役割定義と異なる、3人の立場を並立」という前提説明 | (a) | registry `B_FAMILY_B1_3V_REQUIRED_SEGMENTS`(voice_a/b/c 3スロット)、CURRENT_SPEC 3V行(`APPROVED_FOR_PRODUCTION`) |
| L276-287 | 6区切り構造(##3+###3)・見出しラベル禁止事項(固定ラベル・賛否対称ラベル禁止) | (a) | 上記registry構造 + design.md B-5(Trial-03、Gate1 VALIDATED)の6-heading集約案と一致 |
| L288-306 | Markdown出力の具体例(見出し文言例) | (a)骨格/(b)例文中の人物名 | 骨格は(a)同上。例文中の"Applicant"/"Recruiter, Hiring Manager"/"Business Owner"はテーマ固有 |
| L307-309 | Tensionは独立セクション(継続段落にしない) | (a) | 6-heading構造(上記)の帰結 |
| L311-321 | 見出しは合計6つ限定、追加見出し禁止、自己カウント確認 | (a) | 同上構造原則の具体化 |
| L323-332 | 中心原則「Research is backstage. People are on stage.」、Voice CardがLedgerより主役 | (a) | 「4V版から継続」と自己記載。design.md（Trial-03）4V/3V共通原則として整理済み |
| L332-335 | 「3人目のVoice(経営者)を効率性の代弁者にしない」 | (b) | Voice Card 3(このテーマ固有の人物設定)への言及 |
| L337-343 | 3つのPerspectiveは対称2陣営に分解できないという前提 | (a) | QAスキーマ`leak_binary_camp_split`(汎用フィールド、テーマ非依存の判定基準として実装済み) |
| L343-348 | Voice2/3それぞれの具体的な利害説明 | (b) | AI採用選考の登場人物の具体的説明そのもの |
| L350-442 | Voice Card 1/2/3全文(Person/Situation/Need/Concern/What they protect/Why/Constraint/Concrete lived scene/Supporting evidence、evidence tag `[VOICE_n_EVIDENCE n-xx]`含む) | (b) | 完全にテーマ固有(人物像・出典・数値)。tag**形式**自体は(a)(OPEN-131 `[VOICE_n_EVIDENCE]` `PRODUCTION_WIRED opt-in`)だが**中身**は(b) |
| L444-449 | Voiceの書き始め方(要約文で始めない、生きた場面から) | (a) | 「4V版から継続」明記 |
| L451-458 | 一人称"I"ルール(Voice本文のみ、Hook/Tension/Closingは三人称のまま) | (a) | 「4V版から継続、ユーザーが承認済みの原則」と明記 |
| L460-464 | Narratorが人物を外側から要約・分析しない | (a) | 「4V版から継続」明記 |
| L466-471 | Evidence脇役原則・Voice内の数字は最大1つ | (a) | 「4V版から継続」明記。QAフィールド`leak_evidence_subject`等で機械判定済み |
| L473-483 | 体験claimの根拠付け(Ledgerに直接根拠がない事柄は事実確定として書かない) | **(c)** | ブロック見出し自体が「Person-Voice版Trial-02**新規**」と自己申告。既存Fact Safety/Ledger原則の**拡張**であり、Voice数に依存しない一般化可能な内容に見えるが、SSOT上の独立承認は無い |
| L485-488 | トーン(業界レポート調でなくconversational) | (a) | テーマ言及なし、汎用文体指示 |
| L490-497 | Hookの書き方(70語未満、二人称呼びかけ禁止、企業名・統計を入れない) | (a) | テーマ言及なし(例示のみ)、汎用構造指示 |
| L499-502 | Tensionで第三者視点・解決策を混ぜない(Solution articleではない) | (a) | `CURRENT_SPEC.md`のEditorial Type分類(Discovery/Trend/Solution等)を参照した汎用線引き |
| L504-514 | Tensionの中心原則(共通前提→分岐点→非対称性の3段、Evidence列挙で終わらせない) | (a) | design.md B-7(Trial-03、Gate1 VALIDATED[Trial範囲]) |
| L514-527 | 3段構造の1(共通前提)・2(分岐点)・3a(非対称性)の**具体的な賭け金の記述** | (b) | Applicant/Recruiter/Business Ownerの具体的な賭け金の内容そのもの |
| L528-539 | 3b「外部制約の統合」(`[VOICE_4_EVIDENCE]`を使い、規制・監査が3人の選択肢をどう制約するかまで説明する) | **(c)** | コード内コメント`TENSION_LEAKAGE_FIELDS`の`leak_tension_constraint_integration`定義箇所に**「3V新規」と明記**(L746付近)。design.md自体もTrial-03執筆時点でこの3段構造を「記事本文レベルでの検証は未実施」と記載(未検証の設計目標として明示)。3V Audio Trial-01でこのTrial-02版がAPPROVED_FOR_PRODUCTIONの根拠になったのは事実だが、それは「この1記事が結果としてGate1を通った」ことの承認であり、「外部制約統合という構造要件」自体が独立に汎用原則として承認されたとは、SSOT上どこにも明記が無い |
| L540-547 | 3段構造のまとめ・2陣営分割禁止の再確認・Ledgerに無い新事実を作らない | (a) | 既存原則の繰り返し |
| L548-556 | Tensionの自己チェック手順(外部制約を除いても結論が成立するかのテスト) | (a)手続き/(c)対象 | 手続き自体は(a)相当だが、チェック対象が上記(c)の外部制約統合原則に依存 |
| L558-564 | Closingの役割(要約でなく再定義) | (a) | 「4V版から継続」明記 |
| L566-567 | 同じ意味を2回言わない | (a) | 汎用ルール |
| L569-579 | 語数目安(410-450語、区分別配分) | (a)計算式/前提は(c)寄り | 計算式自体はdesign.md B-6(2V実測語数/秒比からの逆算)で機械的。ただし目標秒数(325-355秒)自体はdesign.md自身が「未検証monitoring値」と明記しており、Trial-02本文も同様に自己申告 |
| L581-598 | 禁止事項まとめ(固定ラベル・Evidence主語文・三人称Voice・2陣営分割・Tension列挙化・Closing雑結び・Voice3を抽象的立場の代弁者にする、等) | (a) | 上記各原則の再掲、テーマ固有の言及なし(最終項目のみ「経営者」という役割名を含むが、パターン自体は一般化可能) |
| L892-922 (`build_leakage_corrective_note_3v()`) | Writer是正メモ生成(persona名"Applicant"/"Recruiter, Hiring Manager"/"Business Owner"をハードコード) | (b) | このタスクの依頼書自体が指摘済みのとおり完全テーマ固有 |

**分解結果の要約**: 332行中、明確に(a)共通原則に分類できたのは約230行
(約69%)、(b)テーマ固有は約85行(約26%、大半はVoice Card全文L350-442)、
(c)判定不能(新原則の疑いが濃い)は2ブロック・約23行(L473-483の体験claim
根拠付け、L528-539の外部制約統合)。(a)の大多数は文中に「4V版から継続」
「ユーザーが承認済みの原則」という自己注記があり、**3V専用に新規発明された
ものではなく、既にGate1=VALIDATED(Trial範囲)のdesign.mdおよびOPEN-131
`PRODUCTION_WIRED`schemaに遡れる**ことを本タスクで確認した。

## 3. Ledger作成のパラメータ化案(3経路の比較)

本タスクでコードを追跡した結果、Ledger生成に関わるスクリプトは想定より
1つ多く、**3系統**存在することが判明した(PHASE1B-03報告はこのうち
vfl01のみを検討していた)。

| 経路 | 実体 | topic引数化の状態 | Ledger schema | Production利用実績 |
|---|---|---|---|---|
| ①A-Family Researcher | `er002_ja_web_research_r3.py`(`build_writer_user_message_r3(topic,...)`/`build_fact_check_prompt(topic,...)`) | **既に汎用**(topic引数を関数シグネチャで必須化、グローバル定数無し) | Voice別タグ無し(単一Narrative記事用) | A-Family Production本体で稼働中 |
| ②B-Family vfl01 | `er003_v1_en_direct_vfl_01_generate.py`(`build_researcher_prompt(topic=TOPIC)`は引数を**持つが**、`run_researcher(client)`が呼び出し時に渡していない。`run_verification`も同様) | **部分的**(関数シグネチャに引数はあるが呼び出し元が固定`TOPIC`グローバル定数に依存、配線漏れのみで改修は小さい) | `FACT_LEDGER_JSON_SCHEMA`(Voice別タグ無し、単一narrative向け) | 3V productionが`run_deviation_check`/`get_client`のみimport、Ledger生成自体は3Vで**未使用** |
| ③AI審査Ledger専用Trial | `er012_ai_screening_ledger_trial_01.py`(Perplexity `sonar-pro`、`FACT_RESEARCH_PROMPT`にテーマ・4立場の説明を**プロンプト全文へ直接ハードコード**) | **無し**(topic引数の概念自体が無い、関数を新テーマに使うにはプロンプト文字列を書き直す必要) | `FACT_JSON_SCHEMA`(`stance_or_position`enumで立場を表現、`[VOICE_n_EVIDENCE]`タグは**この後の人手curationで**手動付与) | **これがTrial-02が実際に使ったLedgerの生成元**(raw facts JSON→人手curationで`verified_fact_ledger.txt`を作成、curationを行う自動関数は存在しない) |

**新たな重要事実**: `verified_fact_ledger.txt`冒頭コメント(「次に手作業で
Voice別Verified Fact Ledgerをcurationしてください」)により、raw fact
JSON→Voice別`[VOICE_n_EVIDENCE]`タグ付きLedger本文への変換は**完全に
人手作業**であることを本タスクで確認した。したがって「Ledger作成の
Production化」は、PHASE1B-03報告が想定した「vfl01の`topic`引数を通す
だけの軽微な改修」よりも実質的な作業量になる。パラメータ化の選択肢は
大きく2つ:

- **(i) 機械的curationスクリプトを新規に書く**: raw facts JSON
  (`stance_or_position`別に既に分類済み)から`[VOICE_n_EVIDENCE]`タグ
  付きテキストへの変換は、evidence_strength上位N件を選び定型テンプレート
  へ流し込むだけなら機械化しやすいが、Trial-01の実例では「Round 2実施
  (偏り補正のための追加research)」「PARTIALLY_CONFIRMED 2件を除外」
  という**人間の判断**が介在しており、これを機械化ルールとして定義する
  こと自体が新しい判断基準の考案に当たりうる。
- **(ii) curationは人手のまま、Research(①または③相当)だけを新テーマ用
  に再実行しraw facts JSONを都度用意する**運用を維持し、Ledger本文の
  組み立ては毎回Fable/ユーザー主導のミニ設計セッションとして扱う
  (Voice Card執筆と合わせて1回の人手セッションに統合)。

OPEN-146(News Ledgerへの`canonical_en_spelling`追加、Gate 2承認済み・
配線中)との整合については、OPEN-146はA-Family News Ledgerへの
**フィールド追加**(Research取得+Writer指示、`CURRENT_SPEC.md`改訂を
伴う正式仕様変更)であり、本タスクで検討しているB-Family Ledgerの
`[VOICE_n_EVIDENCE]`タグ**形式**自体は変更しない(taxonomyの再利用の
み)。したがって直接の衝突は無いが、「Ledger schemaへ新フィールドを
足す変更は`CURRENT_SPEC.md`改訂を要する正式仕様変更として扱う」という
OPEN-146の運用パターンは、上記(i)の機械的curationルールを新設する場合
にも同様に適用すべきと考えられる(=もし(i)を選ぶなら、それ自体を
`USER_DECISION_REQUIRED`として提示すべきという先例)。

## 4. 候補案の比較(QCD)

| 観点 | 案A(汎用prompt固定+Ledger駆動パラメータ化) | 案B(Trial-02を参照実装として薄いテンプレート化) | 案C(3段階設計セッション) |
|---|---|---|---|
| 新仕様に当たる部分 | 2節(c)の2ブロック(体験claim根拠付け・外部制約統合)を独立の恒久ルールとして確定させる必要がある | 「テーマ固有部分だけ差し替える」という置換ルール自体が、実質的に(c)を含む全体をそのまま踏襲するため新規判断は最小だが、次テーマでVoice構成が変わった場合(スマホ制限テーマではApplicant/Recruiter/Business Ownerという構図が存在しない)テンプレートの汎用性が低い | Ledger/Voice Card作成(人手)を明示的に別セッション化するだけで、Writer prompt自体の切り分け判断はしない(先送り) |
| ユーザー承認が必要な判断点 | (1)L473-483(体験claim根拠付け)を恒久3V共通ルールとして確定するか、(2)L528-539(外部制約統合)を恒久3V共通ルールとして確定するか、(3)Ledger curationの自動化方式(3節(i)/(ii)) | 「次テーマでVoice構成自体を変えてよいか」(OPEN_ITEMS 2026-09-12決定は既にVoice構成をLedger駆動で決めると明言、固定3人物を前提にしない) | 「毎回人手セッションを挟む」という運用そのものの承認(コスト増を許容するか) |
| 実装工数(Sonnet想定) | 中(prompt定数のリファクタ+Ledger curation方針確定後の薄いglue、1〜2セッション) | 小(既存Trial-02をほぼそのまま流用、テーマ固有部分のみ差し替えるプレースホルダ化、0.5〜1セッション) | 実装ゼロ(運用ルールの確認のみ) |
| 2Vとの対称性 | 2Vも同じくWriter経路が無いため、Ledger駆動パラメータ化の設計はB-Family共通moduleとして2V/3V両対応にできる可能性がある(1節の指摘どおり) | 2V用の別テンプレートが別途必要になり非対称のまま | 対称性への影響なし(先送りのため) |
| Phase 2までの見込み費用 | Ledger Research(Perplexity/OpenAI web検索、既存実績ベースで数百円規模)+Writer retry含む記事生成(既存3V実績の範囲、既存OPEN_ITEMS記載の3V実測コストと同水準を想定)。人手curationセッション1回分の追加(Fable/ユーザー時間、金銭コストではない) | 案Aとほぼ同額(Ledger生成部分は同じ課題を抱える) | 直接の追加API費用ゼロ(設計確認のみ)、ただし後続セッションで案A/Bいずれかの費用が別途発生 |

## 5. 推奨案

**案A′(案Aの精緻化版)を推奨する**。理由:

1. 2節の分解により、(a)共通原則が約7割を占め、しかもその大半が
   「4V版から継続」「ユーザー承認済み」という既存SSOT根拠を持つことが
   確認できたため、「共通prompt+テーマ固有Voice Card差し替え」という
   分割は、ゼロから新原則を考案する作業ではなく、**既に別々に承認されて
   いた2つのレイヤーを分離するだけの整理作業**に近いと判断できる。
2. ただし2節(c)の2項目(体験claim根拠付け・外部制約統合)は、コード
   コメント自身が「新規」と明記している以上、Sonnetが独断でどちらの
   バケツに入れるかを決めるべきではなく、この2項目**だけ**を切り出して
   ユーザーへ確認する(全330行の再設計をユーザーに求めるのではなく、
   争点を2件まで圧縮できたことが本タスクの主な成果)。
3. 3節の新発見(Ledger curationが人手作業)により、Ledger駆動の完全自動
   パラメータ化(3節(i))は追加の判断コストが高いため、Phase 2の初回
   スコープでは3節(ii)(curationは人手のまま、次テーマ用Ledgerを1回分
   人手で作る)を採用し、自動curation(i)は別途の判断に回すことを推奨
   する。

## 6. 禁止事項の遵守確認

`docs/pm/ACTIVE_TASK.md`/`RESULT_PACKET.md`は未編集。SSOT
(`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`)は未編集(全てGrep/
部分抽出のみで全文読込していない)。コード変更・Git操作(add/commit/push)・
API支出はいずれも無し(¥0)。全文読込を行ったのは分解対象の3V Writer
prompt(`er012_editorial_b_voices_3v_person_voice_trial_02.py`)本体のみ
(Ledger実体確認のため`er012_ai_screening_ledger_trial_01.py`・
`er003_v1_en_direct_vfl_01_generate.py`も一部関数定義・冒頭部分を読んだが、
いずれも既存コードの読み取りのみで編集なし)。`git stash`/`git clean`は
使用していない。

## 7. ユーザーが答えるべき判断点(最小2つ)

1. **2節(c)-1「体験claimの根拠付け」(L473-483)** を3V(および将来の
   B-Family Voices全般)共通の恒久Writerルールとして確定してよいか。
   (推奨: 確定してよい。既存Fact Safety/Ledger原則の一般化可能な拡張
   であり、Voice数・テーマに依存しない内容のため。)
2. **2節(c)-2「Tensionでの外部制約統合」(L528-539、
   `leak_tension_constraint_integration`)** を3V(または3人以上の
   Voice構成全般)共通の恒久Writerルールとして確定してよいか、それとも
   「3人が3陣営に単純分解できない場合の1パターン」として次テーマ
   (スマホ制限テーマ)ではLedger内容次第で任意適用とするか。
   (推奨: 恒久ルール化はせず、次テーマのVoice構成・Ledger内容確定後に
   Fableが個別判断する任意パターンとして扱う。理由: design.md自身が
   この3段構造を「記事本文レベルでの検証は未実施」と明記しており、
   1記事[AI採用選考]でのGate1通過だけでは一般化の十分な根拠にならない
   ため。)

上記2点さえ確定すれば、Ledger curation方式(3節(ii)を暫定採用)・Voice
Card執筆・Writer prompt汎用テンプレート化は、Sonnetが機械的に着手できる
状態になる。
