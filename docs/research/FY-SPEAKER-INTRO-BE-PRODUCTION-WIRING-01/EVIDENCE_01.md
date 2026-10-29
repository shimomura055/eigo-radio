# FY-SPEAKER-INTRO-BE-PRODUCTION-WIRING-01 委任_01 EVIDENCE(Family Y 人物紹介 B+E 正式配線。Status=PRODUCTION_WIRED_PENDING_FABLE)

原文=`docs/pm/delegation_log/2026-10-29_FY-SPEAKER-INTRO-BE-PRODUCTION-WIRING-01_USER.md`。正本Prompt=Trialの確定成果物(`docs/research/FY-SPEAKER-INTRO-GENERALIZATION-TRIAL-01/RESULT_01.md`/`RESULT_02.md`、`er121_output/family_y_intro_trial_01/*/prompt_E.txt`)。

## 1. 実装(編集範囲=紹介生成のPrompt/関数/test/SSOTのみ。runner/structure/er063/X/Z不変更)
| 項目 | 場所 | 内容 |
|---|---|---|
| Prompt | `er121_prompts/persona_intro_01.txt` `【書き方】`直後の2箇条 | 【人物紹介の一般化原則】(テーマに対する立場・経験を最優先/属性は立場理解に重要なときだけ/役割名の機械転記禁止/属性を削るだけで終わらせない/根拠のない設定は足さない)+【属性がそのまま立場のとき】(宅配ドライバー・高校生のように属性名が立場を表すなら省かず、話題との関わりを添える)。Trial確定文から`(Trial)`ラベルを除き、E節へ箇条書き記号を付けただけ(Trial prompt_Eと正規化後一致をtestで固定) |
| sha | `er121_family_y_text_core_01.py:1066` | `787794d6…`→`a5da099a2d7b44392f118f61a97f3538933cf2e3354d0024b3bbcf697a12fbe5`(`load_article_prompt`:1070がsha不一致をSTOP=PROMPT_SHA_MISMATCH) |
| 接点行 | `er121_family_y_text_core_01.py:1650 person_block` | 人物ブロックへ`話題との関わり: <contact_point_ja>`行を追加(役割行の直後)。`contact_point_ja`は既に`REQUIRED_SHEET_KEYS`(:1125)の必須key=入力スキーマ・validate_theme_package変更なし |
| role_patterns | 変更なし(判断) | B/E全候補(surname B1/B2、redelivery E1/E2、sns E1/E2)が既存`check_intro`(derived/explicit両モード)を通過。ROLE_NOT_CONVEYEDはTrial不採用案(A2・D)のみ。よって役割語集合の緩和・更新は不要(`role_patterns`はTheme Package別のexplicitデータで、乖離型の新規Packageはderived=`role_ja+who_ja`2字連続で足りる)。緩和はしていない |
| 時期語検査 | 追加なし | ユーザー決定。Trial A1(『結婚して』を含む)が`check_intro`を通ることをtestで固定 |
| 既存検査 | 不変 | `check_intro`(一人称・主張先取り語・10字一致・役割伝達・字数`INTRO_RANGE=(32,62)`)、補助Gate(`run_leadintro_gate`=gpt-6-luna)は不変 |

## 2. 経路(Std/Adv共通)
Y紹介は記事単位の日本語text stageで1回生成(3Voice=1call)→Std/Adv双方の英訳stageがそれを訳す。経路: runner `stage_text`(`er121_family_y_runner_01.py:336`)→`produce_article`→`_produce_article`(`er121_family_y_text_core_01.py:1985`)→`load_article_prompt("intro")`(:2009)→`generate_intros`(:1665)→`build_intro_prompt`(:1659)→`person_block`。`stage_translate`(runner:405)がb1b(Adv)・a2(Std)へ英訳。Std/Advの分岐は紹介生成に無い。
- retry(内部再生成): `generate_intros`:1665の2回ループは同じ`prompt`+問題リストを使う(testで2call両方にB+E節・接点行を確認)。
- `--regenerate-stage text`・初回・resume: すべて`produce_article`一本。cache keyに紹介Prompt sha(`intro=(parts_i or {}).get("sha256")`)とmodule sha(`**common`)が入る→旧Prompt生成物は再利用されない(下記)。reuse manifestで`intros`を指定した既存完成記事は従来どおり再利用され再生成されない(要件§8)。

## 3. 正式初回経路 runtime evidence(copy-run、使い捨て)
run=`er121_output/family_y_production_01/redelivery_fee/run_fybe_ev_01`(再配達料=一致型の既存Theme Package `THEME_DATA_02.json`+reuse manifestの`intros_file`だけ除去した複製`docs/research/FY-SPEAKER-INTRO-BE-PRODUCTION-WIRING-01/reuse_redelivery_no_intros_copy.json`。Voice R0・Leadは元manifestと同一を再利用、元manifest・既存完成記事は不変)。実行=`er121_family_y_runner_01.py --mode real --stages seed_check,text,translate --approved-budget-jpy 60`(正式runner、1起動)。STOP確認=`stop_check_start.json`・`stop_check_launch2.json`(rc=0)。
- Prompt: `text/text_records.json` intros.prompt_file=`persona_intro_01.txt`、prompt_sha256=`a5da099a…12fbe5`(B+E)、user_prompt_sha256=`f10dd9e8…`、`text/lead_intro/intro/intro_prompt.txt`に「話題との関わり」3行+一般化原則+E節が含まれる。
- routing/model: routing_key=`FAMILY_Y_PERSONA_INTRO`、expected=実=`gpt-6.1-sol`(effort high)、1call(再生成0)、input 2,062/output 1,614 tokens。補助Gate=`gpt-6-luna`(`gate/applicable_result.json` status=PASS、applicable_flagged=[])。英訳=`gpt-6-luna`×2(b1b/a2)。`check_intro`=3Voiceとも違反0(`problems_per_try=[[]]`、chars 43/43/40)。
- 生成された紹介文(JA):
  - V1: 最初に話すのは、毎日荷物を配る宅配ドライバー。留守だった家へ、もう一度届けに行く側だ。 → 一致型: 「宅配ドライバー」維持+再配達との関わり
  - V2: 次は、夫婦とも仕事があり、家を空けることも多い暮らしの中で、荷物を受け取っている人だ。
  - V3: 最後は、ロッカーなどで荷物を受け取り、再配達にならないよう手間をかけている人だ。
- 英訳(translate/b1b.md=Adv、a2.md=Std):
  - V1 Adv: `First is a delivery driver who delivers packages every day, going back to homes where no one was home.` / Std: `First is a delivery driver who delivers packages every day. They return to homes where no one was home.`
  - V2 Adv: `Next is someone who receives packages while both they and their spouse work and are often away from home.` / Std: `Next is someone who works. Their spouse works too, and both are often away from home.`
  - V3 Adv: `Last is someone who takes the trouble to pick up packages at a delivery office or locker to avoid redelivery.` / Std: `Last is someone who picks up packages at a delivery office or locker. They do this to avoid causing trouble with another delivery.`
- 英訳の性別表現(確認のみ。追加記事・TTSなし): Theme Packageの性別=V1男性・V2女性・V3男性(`sheets.*.gender`)。JA紹介文自体に性別手がかりが無く、EN紹介はV1/V2/V3とも中立(`they`/`someone`/`their spouse`/`delivery driver`)。本文Persona(V2「My husband and I」=女性・夫あり)と矛盾する`he`/`she`は無く、Trial課題(誤った`He`/`father`の独立文)は再発しない。旧ENの`she and her husband`/`a woman`のような性別明示は無くなった(情報は減るが誤りは無い。RESULT_02 §3観察3どおり)。性別が自然に表れない紹介行は許容範囲と判断(新たな品質基準は追加せず)。
- resume: 同一入力での再実行は、同一run 300秒内3回目の起動で`FAMILY_Z_RESTART_STORM`の自動STOP(`run_fybe_ev_01/STOP`作成。rc=3、API 0。原因=本Worker自身の起動3回[最初の1回はTheme Package引数誤りで課金前STOP]。解除はしていない=使い捨てcopy-runにつき残置)。代替として、保存済み`stage_lead_intro.json`のinput_keyを現行コードで再計算して一致(MATCH True)、旧Prompt shaで計算すると不一致(旧Prompt生成物は再利用されない)を確認(再現: §5)。
- 費用: run合計¥4.29(`console_launch2.log` spent_jpy)。内訳概算: 紹介生成(gpt-6.1-sol 2,062/1,614 tok、$2/$10 per M)≒¥3.1、補助Gate+Closing Leak(luna)、英訳(luna)×2。委任Cap¥40の範囲内。

## 4. Regression(Trial 3類型)
`er121_family_y_intro_be_test_01.py`(新規、13 test): Prompt sha・B+E節の位置・ラベル除去、person_blockの接点行(surname/redelivery/sns全9人物)、生成Prompt=Trial確定Prompt(redelivery/sns=prompt_E、surname=prompt_B+E節)と正規化後一致、3類型golden(姓=「父親」を主名詞にしない・「姓」中心/再配達=「宅配ドライバー」維持・A案は欠落=後退検出/SNS=親+見守り・使い方、高校生+制限、中学生の親)と全件`check_intro`通過、時期語検査なし、内部retryが同じB+E Promptを使用、cache keyのPrompt sha、runner単一経路、X/Zがintro関数・Promptを参照しない。
既存: `er121_family_y_text_core_article_test_01.py`(Prompt shaを更新、DEV(旧委任_28)等価testは追加2箇条と接点行を除いて比較=旧部分は不変)・`er121_family_y_text_core_01_test_01.py`・`er121_family_y_runner_text_wiring_test_01.py` 合計169 test OK。
合理的補完を一律NGにしない: `check_intro`に事実・時期の決定論検査なし(Trial A1「結婚して」を通すtest)。明確な矛盾・不自然な創作・立場不整合は既存の補助Gate(luna)・Lead/紹介適用範囲とVoice整合のPrompt指示(「人物の情報は【人物】にあることだけ。…新しい事実は足さない」を従来どおり維持)・HRで扱う(新Gateは追加していない)。

## 5. Dangling Reference
Grep(`787794d6`): 実行コード0(`er121_family_y_text_core_01.py:1066`のコメントと新test/更新testの旧sha記録のみ)。履歴文書`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/DESIGN_02.md:153`は当時の記録として残置(Prompt shaを現行仕様としては参照していない)。旧role_patterns: 変更なし。DEV `er110_family_y_redelivery_revision_01.py`のINTRO_TMPLは旧委任_28の凍結DEVであり不変(等価testは旧部分のみ比較)。
resume key再計算: `docs/research/FY-SPEAKER-INTRO-BE-PRODUCTION-WIRING-01/resume_key_check.py`(`stage_lead_intro.json` input_key=`23354823…5417`と現行コード再計算が一致)。

## 6. 未確認・限界
- 乖離型(姓)・中間型(SNS)の正式経路runtimeは未実施(copy-runは一致型=再配達のみ。費用・時間とユーザー指示「追加Trial不要」のため、Trial出力を使ったgolden+Prompt同一性testで代替)。
- Fable独立受入評価(§7 Gate 10)は未実施。
- 姓記事(run_02)は別承認の固定V1文で是正済み(B+Eで再生成しない)。
