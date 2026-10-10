# RESULT_01: WRITER-RISK-FLAGGER-A4-DUALMODEL-OR-TRIAL-01 結果(Trial/DEV、2026-10-10)

**Status提案: USER_DECISION_REQUIRED**(ChatGPT側でUser A/B/C/D判定と照合後に判定)。Claude側はBlind(Human判定不使用)。A3を外せるかの最終判定は確定しない。APPROVED項目Status不変更、Production変更ゼロ、やらないこと9項目未実施。

## 0. 非エンジニア向け3点

- **A: A3を外せそうか** = Claude側では未確定(Human照合待ち)。機械的事実: A3-ORのみ検出(A4-ORでは拾えない)= **7件**(A3-OR全 15文のうち)。既存Sol A3 Flag 20文のうちA4-ORで拾えたのは 9文(Luna A4 9 / Gemini A4 0)。既存Union 29のうちA4-ORで拾えたのは 12文。
- **B: Human Review量の変化** = A4-OR は 15文(13 issue、1記事平均 1.36文)。参考: Sol A4(既存)25文、Sol A3∪A4(既存Union)29文(2.64文/記事)。新規(未評価)Flagは 7文。
- **C: 推奨次判断**: ChatGPT側で matching_packet_01.md と User判定(A/B/C/D)を照合し、A3-OR/A4-ORで失う有用Flag(A/B)の有無を確認したうえで、A3省略の可否を判断する(Production採用判断はしない)。

## 1. 実施概要

- 評価セット: POST-EN-TRIAL-01 英語稿11本(U01-U08, X09-X11)。A3 sha `9d995042…` / A4 sha `c87b95e5…`、既存raw requestと記事ごとに system/user 完全一致(dry-run assert 22/22、`dry_run/dry_run_report_01.json`)。
- 実行: Luna(`gpt-6-luna`, effort=medium) 22 call、Gemini(`gemini-3.5-flash-lite`, Provider既定thinking) 22 call。既存Sol A3/A4(22 call)は再実行せず補助指標。
- 出力無効: なし(44 cell全て valid JSON)。
- retry: Luna: attempts>1 のセル 0件、transient例外 0件; Gemini 3.5 Flash-Lite: attempts>1 のセル 0件、transient例外 0件。

## 2. 使用モデル(PM_GOVERNANCE 25節)

| 条件 | 指定model_id | API応答のmodel | 最新か | 最新でない場合の理由 |
|---|---|---|---|---|
| Luna | `gpt-6-luna` | gpt-6-luna | 現行世代のLuna(OpenAI効率系。ユーザー指定条件) | 該当なし(旧世代 gpt-5.6-luna は不使用) |
| Gemini | `gemini-3.5-flash-lite` | gemini-3.5-flash-lite | 最新世代のFlash-Lite(ユーザー指定名と同一) | **旧世代 gemini-3.1-flash-lite($0.25/$1.50)・gemini-2.5-flash-lite($0.10/$0.40)がより安価に実在するが、置換せず。** 呼出は成功 |
| Sol(既存・補助) | `gpt-6.1-sol` | POST-EN-TRIAL-01実測 | 最新世代最上位系 | - |

## 3. 4条件のFlag一覧(記事ID / 文ID / type / confidence / related Fact / reason原文)

confidenceは相対比較のみ(絶対評価に使わない)。

### Luna A3 (Flag 13件 / 文 13)

| 記事 | 文 | type | conf | Fact | Union29 | reason原文 |
|---|---|---|---|---|---|---|
| U03 | s5 | 不在断定 | 0.29 | F-001 | U03-s5 | 「性能の詳細は秘密のまま」という断定は、台帳にある発言内容と配備の説明だけでは確認できないのではありませんか。 |
| U03 | s13 | 不在断定 | 0.36 | F-001 | U03-s13 | 「具体的なシステム名や攻撃能力は示されていない」という断定は、台帳に明記された情報の範囲を超えているのではありませんか。 |
| U03 | s17 | 数量時系列 | 0.43 | F-003 | U03-s17 | 「satellites」という複数形は、台帳に記載されたロシアが破壊した衛星1基より広い範囲を示しているのではありませんか。 |
| U03 | s18 | 数量時系列 | 0.34 | F-003 | 未評価 | 「tests」という複数形は、台帳に記載された2021年の破壊試験1件より多い試験を示しているのではありませんか。 |
| U05 | s1 | 主体対象入替 | 0.55 | BYD-RECALL-07 | U05-s1 | 公告では限位垫が脱落する「極端な場合」に制動灯が点灯し続ける可能性とされていますが、この見出しはその条件を外して一般的な状態として述べているのではありませんか。 |
| U05 | s10 | 主体対象入替 | 0.78 | BYD-RECALL-07 | 未評価 | 公告では限位垫が脱落する「極端な場合」に制動灯が点灯し続ける可能性とされていますが、この文はその条件を外して一般的なリスクとして述べているのではありませんか。 |
| U05 | s11 | 主体対象入替 | 0.65 | BYD-RECALL-07 | 未評価 | 公告では限位垫が脱落する「極端な場合」に制動灯が点灯し続ける可能性とされていますが、この文はその条件を外して、ペダルを踏んでいないときに常に点灯するように読めるのではありませんか。 |
| U05 | s27 | 主体対象入替 | 0.78 | BYD-RECALL-06,BYD-RECALL-07 | 未評価 | 公告では限位垫の材料異常に続いてひび割れ・破損の可能性があり、脱落する「極端な場合」に制動灯が点灯し続けるとされていますが、この文はその条件を外して部品が直接点灯を引き起こすように述べているのではありませんか。 |
| U06 | s1 | その他 | 0.30 | F01,F05 | 未評価 | 「Disney+ Prices Are Going Up」は、確認対象の米国向け価格改定だけでなく全地域・全プランの値上げを示す表現ではありませんか。 |
| U06 | s17 | その他 | 0.35 | F06 | U06-s17 | 「different for each person」は、適用時期が請求サイクルによって異なるという記述よりも、全員の日付がそれぞれ異なると読める表現ではありませんか。 |
| U06 | s21 | その他 | 0.30 | F05,F06 | U06-s21 | 「when you signed up and your billing cycle」で変更時期が分かるという記述は、第三者請求では価格や適用条件が異なる場合がある点を含めた表現ではありませんか。 |
| X09 | s8 | その他 | 0.34 | HF-002,HF-003 | X09-s8 | “20% payment on all cargo”は貨物価値に20％を適用する意味にも読めますが、台帳では算定基礎は明記されていないのではありませんか。 |
| X11 | s7 | 主体対象入替 | 0.78 | F4 | X11-s7 | 「models’ output」が著作権管理情報を除去した主体と読めますが、Factでは除去したのはOpenAIと原告側が主張しているのではありませんか。 |

### Gemini A3 (Flag 2件 / 文 2)

| 記事 | 文 | type | conf | Fact | Union29 | reason原文 |
|---|---|---|---|---|---|---|
| U01 | s18 | その他 | 0.80 | MUSE-HC-010 | U01-s18 | 台帳MUSE-HC-010では従業員がプライバシー上の懸念を示したとされていますが、文s18の「情報を共有されたとは仮定できない」という主張は台帳の事実と食い違っていませんか。 |
| X11 | s28 | 主体対象入替 | 0.30 | F2,F6 | 未評価 | s28で「Fourteen news companies」とありますが、台帳F2では14の法人・事業体、F3では19出版物とされていますが、これらはすべて純粋な「news companies（報道企業）」であると断定して問題ありませんか？ |

### Luna A4 (Flag 15件 / 文 15)

| 記事 | 文 | type | conf | Fact | Union29 | reason原文 |
|---|---|---|---|---|---|---|
| U03 | s5 | 不在断定 | 0.30 | F-001 | U03-s5 | F-001は具体的なシステム名や攻撃能力を推測で補わないよう述べていますが、「性能の詳細は秘密のまま」と確認済みの事実としている点は確認が必要ではありませんか。 |
| U03 | s13 | 不在断定 | 0.40 | F-001 | U03-s13 | F-001はシステム名や攻撃能力を推測で補わないよう述べていますが、「具体的な名称や能力は示されていない」と断定できる根拠があるか確認が必要ではありませんか。 |
| U03 | s17 | 数量時系列 | 0.30 | F-003 | U03-s17 | F-003が記録しているのはCOSMOS 1408衛星1基の破壊ですが、「satellites」と複数形で述べている点は確認が必要ではありませんか。 |
| U03 | s33 | 不在断定 | 0.40 | F-001 | U03-s33 | F-001は軌道上兵器の配備を認めた発言を記録していますが、「能力を公表していない」と断定できる根拠があるか確認が必要ではありませんか。 |
| U04 | s21 | その他 | 0.30 | MB-02 | 未評価 | 「only the attention given by fashion media and on runways」という限定は、ニューヨークとロサンゼルスの着用例やSNS投稿も紹介したMB-02の範囲と食い違う可能性があるのではありませんか。 |
| U05 | s1 | その他 | 0.84 | BYD-RECALL-07 | U05-s1 | 「Even When No One Is Pressing the Pedal」と一般的に述べていますが、公告の説明は限位垫が脱落する極端な場合に限った可能性ではありませんか。 |
| U05 | s4 | その他 | 0.28 | (なし) | U05-s4 | 「the driver has no idea why」は、運転者が理由を知らないという台帳に記載のない事実を述べているのではありませんか。 |
| U05 | s10 | その他 | 0.78 | BYD-RECALL-07 | 未評価 | 「there is a risk」と可能性を示す一方で、制動灯が点灯し続けるのは限位垫が脱落する極端な場合という条件が省かれているのではありませんか。 |
| U05 | s27 | その他 | 0.81 | BYD-RECALL-06,BYD-RECALL-07 | 未評価 | 「may keep the brake lights on」と述べていますが、公告が示すのは限位垫が脱落する極端な場合に限った可能性ではありませんか。 |
| U06 | s16 | その他 | 0.30 | F06 | U06-s16 | F06は新規契約者向け価格の開始日を示していますが、「sent to everyone（全員に送られた）」という通知の範囲までは確認できないのではありませんか。 |
| U06 | s17 | 数量時系列 | 0.40 | F06 | U06-s17 | F06は既存契約者への適用日が各人の請求サイクルによって異なるとしていますが、「different for each person（人ごとに異なる）」と全員の日付が異なるように断定しているのではありませんか。 |
| U07 | s1 | 主体対象入替 | 0.55 | F6 | U07-s1 | 「the models」の破棄という表現は、訴状が破棄を求めている「原告らのコンテンツを組み込んだモデル」より対象範囲が広く読めるのではありませんか。 |
| U07 | s5 | 主体対象入替 | 0.65 | F6 | U07-s5 | 「models such as GPT」の破棄という表現は、訴状が破棄を求めている「原告らのコンテンツを組み込んだモデル」より対象範囲が広く読めるのではありませんか。 |
| U08 | s25 | 不在断定 | 0.30 | F4,F6 | U08-s25 | F4の売上高見通しとF6の需要評価について、台帳だけでは両者の関連説明がないとは確認できないため、「発表だけではつながりを説明していない」という不在の断定は確認が必要ではありませんか。 |
| X11 | s7 | 主体対象入替 | 0.86 | F4 | X11-s7 | 「the models’ output ... removed copyright management information」は、台帳の「OpenAIが著作権管理情報を除去した」という主張と、除去した主体が異なる表現ではありませんか |

### Gemini A4 (Flag 0件 / 文 0)

Flagなし。

### A3-OR / A4-OR(sentence単位の和)

- A3-OR(Luna A3 ∪ Gemini A3): 15文 U01-s18, U03-s5, U03-s13, U03-s17, U03-s18, U05-s1, U05-s10, U05-s11, U05-s27, U06-s1, U06-s17, U06-s21, X09-s8, X11-s7, X11-s28
- A4-OR(Luna A4 ∪ Gemini A4): 15文 U03-s5, U03-s13, U03-s17, U03-s33, U04-s21, U05-s1, U05-s4, U05-s10, U05-s27, U06-s16, U06-s17, U07-s1, U07-s5, U08-s25, X11-s7
- A4 両モデル一致: 0文 なし

## 4. 表1(主評価): A3-ORの全項目とA4-ORカバー(Human列は空欄)

機械的事実: A3-OR 15文のうちA4-ORでカバーされない(A3のみ検出)= **7件**。

| Issue(記事+文+related Fact) | 既存Union29一致ID | Luna A3 | Gemini A3 | Luna A4 | Gemini A4 | A4-OR | A4-ORでカバー | Human評価 | A3なしで失うか |
|---|---|---|---|---|---|---|---|---|---|
| U01 s18 / Fact: MUSE-HC-010 / We cannot assume from this story that any information was sh… | U01-s18 | - | その他 0.80 | - | - | - | **A3のみ** | | |
| U03 s5 / Fact: F-001 / The details of the system’s performance remain secret, while… | U03-s5 | 不在断定 0.29 | - | 不在断定 0.30 | - | ○ | カバー | | |
| U03 s13 / Fact: F-001 / But no specific system names or attack capabilities have bee… | U03-s13 | 不在断定 0.36 | - | 不在断定 0.40 | - | ○ | カバー | | |
| U03 s17 / Fact: F-003 / Russia has destroyed satellites with ground-launched anti-sa… | U03-s17 | 数量時系列 0.43 | - | 数量時系列 0.30 | - | ○ | カバー | | |
| U03 s18 / Fact: F-003 / But these were tests fired from the ground. | 未評価 | 数量時系列 0.34 | - | - | - | - | **A3のみ** | | |
| U05 s1 / Fact: BYD-RECALL-07 / # A Car’s Red Lights Say “Braking!” Even When No One Is Pres… | U05-s1 | 主体対象入替 0.55 | - | その他 0.84 | - | ○ | カバー | | |
| U05 s10 / Fact: BYD-RECALL-07 / As a result, there is a risk that the brake lights will stay… | 未評価 | 主体対象入替 0.78 | - | その他 0.78 | - | ○ | カバー | | |
| U05 s11 / Fact: BYD-RECALL-07 / In other words, no foot is pressing the brake, but the light… | 未評価 | 主体対象入替 0.65 | - | - | - | - | **A3のみ** | | |
| U05 s27 / Fact: BYD-RECALL-06,BYD-RECALL-07 / BYD is recalling 183,211 cars in China because faulty pedal … | 未評価 | 主体対象入替 0.78 | - | その他 0.81 | - | ○ | カバー | | |
| U06 s1 / Fact: F01,F05 / # Disney+ Prices Are Going Up: Don’t Miss the “Coming Up Nex… | 未評価 | その他 0.30 | - | - | - | - | **A3のみ** | | |
| U06 s17 / Fact: F06 / But the day the main story begins on your bill is different … | U06-s17 | その他 0.35 | - | 数量時系列 0.40 | - | ○ | カバー | | |
| U06 s21 / Fact: F05,F06 / The price list tells you “how much.” When you look at it tog… | U06-s21 | その他 0.30 | - | - | - | - | **A3のみ** | | |
| X09 s8 / Fact: HF-002,HF-003 / Trump’s “20% plan.” It called for a 20% payment on all cargo… | X09-s8 | その他 0.34 | - | - | - | - | **A3のみ** | | |
| X11 s7 / Fact: F4 / They also say the models’ output copied or put articles toge… | X11-s7 | 主体対象入替 0.78 | - | 主体対象入替 0.86 | - | ○ | カバー | | |
| X11 s28 / Fact: F2,F6 / Fourteen news companies and related entities are asking a co… | 未評価 | - | 主体対象入替 0.30 | - | - | - | **A3のみ** | | |

## 5. 補助表1b: 既存Sol A3 Flag(Union 29のA3側 20文)をA4で拾えたか(Human列は空欄)

カバー率: A4-OR 9/20、Luna A4 9/20、Gemini A4 0/20。Sol A3のみ(Sol A4で未Flag)の項目 4文のうちA4-ORカバー 1。参考: Sol A4 25文のうちA4-ORカバー 11。Union 29全体のA4-ORカバー 12/29(Luna A4 12、Gemini A4 0)。

| Union29 ID | Sol A3 type conf | Sol A4でも検出 | Luna A4 | Gemini A4 | A4-OR | (参考)Luna A3 | (参考)Gemini A3 | Human評価 | A3なしで失うか |
|---|---|---|---|---|---|---|---|---|---|
| U02-s18 | その他 0.72 | ○ | - | - | - | - | - | | |
| U03-s1 | その他 0.72 | ○ | - | - | - | - | - | | |
| U03-s5 | その他 0.83 | ○ | ○ | - | ○ | ○ | - | | |
| U03-s13 | 不在断定 0.70 | ○ | ○ | - | ○ | ○ | - | | |
| U03-s17 | 数量時系列 0.76 | ○ | ○ | - | ○ | ○ | - | | |
| U03-s33 | 不在断定 0.68 | ○ | ○ | - | ○ | - | - | | |
| U04-s7 | 主体対象入替 0.45 | ○ | - | - | - | - | - | | |
| U04-s15 | 主体対象入替 0.30 | - | - | - | - | - | - | | |
| U05-s1 | その他 0.35 | - | ○ | - | ○ | ○ | - | | |
| U05-s6 | 主体対象入替 0.88 | ○ | - | - | - | - | - | | |
| U06-s8 | 数量時系列 0.35 | ○ | - | - | - | - | - | | |
| U06-s9 | 数量時系列 0.35 | ○ | - | - | - | - | - | | |
| U06-s17 | 主体対象入替 0.64 | ○ | ○ | - | ○ | ○ | - | | |
| U07-s5 | 主体対象入替 0.62 | ○ | ○ | - | ○ | - | - | | |
| U08-s25 | 不在断定 0.68 | ○ | ○ | - | ○ | - | - | | |
| X09-s8 | 主体対象入替 0.65 | ○ | - | - | - | ○ | - | | |
| X11-s4 | 主体対象入替 0.42 | ○ | - | - | - | - | - | | |
| X11-s7 | 主体対象入替 0.96 | ○ | ○ | - | ○ | ○ | - | | |
| X11-s17 | 主体対象入替 0.35 | - | - | - | - | - | - | | |
| X11-s25 | 不在断定 0.35 | - | - | - | - | - | - | | |

## 6. 表2(副評価): Human Review量(A/B/C/D列は空欄)

1記事平均=件数/11記事。出力無効の回は件数に含まない(出力無効セル数を併記)。

| 条件 | raw Flag数 | sentence重複除去後 | semantic issue数 | 既存Union29一致数 | 未評価(新規)数 | 1記事平均(sentence) | 1記事平均(issue) | 出力無効セル | A | B | C | D |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Luna A4 | 15 | 15 | 13 | 12 | 3 | 1.36 | 1.18 | 0 | | | | |
| Gemini A4 | 0 | 0 | 0 | 0 | 0 | 0.00 | 0.00 | 0 | | | | |
| A4-OR(Luna A4 ∪ Gemini A4) | 15 | 15 | 13 | 12 | 3 | 1.36 | 1.18 | 0 | | | | |
| 参考: Sol A4(既存) | 25 | 25 | 21 | 25 | 0 | 2.27 | 1.91 | 0 | | | | |
| Luna A3 | 13 | 13 | 12 | 8 | 5 | 1.18 | 1.09 | 0 | | | | |
| Gemini A3 | 2 | 2 | 2 | 1 | 1 | 0.18 | 0.18 | 0 | | | | |
| A3-OR(Luna A3 ∪ Gemini A3) | 15 | 15 | 14 | 9 | 6 | 1.36 | 1.27 | 0 | | | | |
| 参考: Sol A3(既存) | 20 | 20 | 14 | 20 | 0 | 1.82 | 1.27 | 0 | | | | |
| 参考: Sol A3∪A4(既存Union) | 45 | 29 | 23 | 29 | 0 | 2.64 | 2.09 | 0 | | | | |
| 参考: 4条件全部(A3-OR ∪ A4-OR) | 30 | 22 | 20 | 15 | 7 | 2.00 | 1.82 | 0 | | | | |

## 7. 表3(相互補完): A4で片方のモデルのみがFlagした項目

Luna A4のみ 15件 / Gemini A4のみ 0件 / 両方 0件。

### Luna A4のみ(15件)

| 記事 | 文 | related Fact | reason要約 | 既存Union29 ID / 未評価 | Human評価 | 有用/ノイズ |
|---|---|---|---|---|---|---|
| U03 | s5 | F-001 | F-001は具体的なシステム名や攻撃能力を推測で補わないよう述べていますが、「性能の詳細は秘密のまま」と確認済みの事実としている点は確認が必要ではありませんか。 | U03-s5 | | |
| U03 | s13 | F-001 | F-001はシステム名や攻撃能力を推測で補わないよう述べていますが、「具体的な名称や能力は示されていない」と断定できる根拠があるか確認が必要ではありませんか。 | U03-s13 | | |
| U03 | s17 | F-003 | F-003が記録しているのはCOSMOS 1408衛星1基の破壊ですが、「satellites」と複数形で述べている点は確認が必要ではありませんか。 | U03-s17 | | |
| U03 | s33 | F-001 | F-001は軌道上兵器の配備を認めた発言を記録していますが、「能力を公表していない」と断定できる根拠があるか確認が必要ではありませんか。 | U03-s33 | | |
| U04 | s21 | MB-02 | 「only the attention given by fashion media and on runways」という限定は、ニューヨークとロサンゼルスの着用例やSNS投稿も紹介したMB-02の範囲と食い違う可能性があるのではありませんか。 | 未評価 | | |
| U05 | s1 | BYD-RECALL-07 | 「Even When No One Is Pressing the Pedal」と一般的に述べていますが、公告の説明は限位垫が脱落する極端な場合に限った可能性ではありませんか。 | U05-s1 | | |
| U05 | s4 | (なし) | 「the driver has no idea why」は、運転者が理由を知らないという台帳に記載のない事実を述べているのではありませんか。 | U05-s4 | | |
| U05 | s10 | BYD-RECALL-07 | 「there is a risk」と可能性を示す一方で、制動灯が点灯し続けるのは限位垫が脱落する極端な場合という条件が省かれているのではありませんか。 | 未評価 | | |
| U05 | s27 | BYD-RECALL-06,BYD-RECALL-07 | 「may keep the brake lights on」と述べていますが、公告が示すのは限位垫が脱落する極端な場合に限った可能性ではありませんか。 | 未評価 | | |
| U06 | s16 | F06 | F06は新規契約者向け価格の開始日を示していますが、「sent to everyone（全員に送られた）」という通知の範囲までは確認できないのではありませんか。 | U06-s16 | | |
| U06 | s17 | F06 | F06は既存契約者への適用日が各人の請求サイクルによって異なるとしていますが、「different for each person（人ごとに異なる）」と全員の日付が異なるように断定しているのではありませんか。 | U06-s17 | | |
| U07 | s1 | F6 | 「the models」の破棄という表現は、訴状が破棄を求めている「原告らのコンテンツを組み込んだモデル」より対象範囲が広く読めるのではありませんか。 | U07-s1 | | |
| U07 | s5 | F6 | 「models such as GPT」の破棄という表現は、訴状が破棄を求めている「原告らのコンテンツを組み込んだモデル」より対象範囲が広く読めるのではありませんか。 | U07-s5 | | |
| U08 | s25 | F4,F6 | F4の売上高見通しとF6の需要評価について、台帳だけでは両者の関連説明がないとは確認できないため、「発表だけではつながりを説明していない」という不在の断定は確認が必要ではありませんか。 | U08-s25 | | |
| X11 | s7 | F4 | 「the models’ output ... removed copyright management information」は、台帳の「OpenAIが著作権管理情報を除去した」という主張と、除去した主体が異なる表現ではありませんか | X11-s7 | | |

### Gemini A4のみ(0件)

なし(0件)。

## 8. 未評価Flag一覧(既存Union 29に記事ID+文IDで一致しないFlag、7文)

ChatGPT側追加判定用。版A(confidence・モデル名あり)と版B(なし、Blind packet形式)。版Bは `unreviewed_packet_01.md` にも単体出力。

### 版A(confidence・モデル名あり)

#### N01: U03 s18

- 記事: U03(space_weapons)
- 対象文: But these were tests fired from the ground.
- ±2文:
  - s16: “Haven’t there already been weapons that destroy satellites?” That’s right.
  - s17: Russia has destroyed satellites with ground-launched anti-satellite missiles.
  - s18(対象): But these were tests fired from the ground.
  - s19: “Firing from the ground into space” and “placing a weapon in orbit” both involve space, but they have different starting points and locations.
  - s20: The terminology needs care, too.
- Fact本文:
  - F-003: ロシアは2021年11月15日、地上発射型の直接上昇式ASATミサイルでロシアの衛星COSMOS 1408を破壊し、1,500個超の追跡可能な軌道デブリを発生させた。([spacecom.mil](https://www.spacecom.mil/Newsroom/News/Article-Display/Article/2842957/russian-direct-ascent-anti-satellite-missile-test-creates-significant-long-last/?utm_source=openai))
  scope: 低軌道、COSMOS 1408および発生デブリ
  conditions: 米宇宙軍による公式発表
  numeric_value: >1,500個 (numeric_scope: 追跡可能な軌道デブリ)
  date_or_period: 2021年11月15日
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 地上から発射したASATミサイルによる破壊試験であり、兵器を軌道上に恒久配備した事例とは区別する。
- reason:
  - [Luna A3 / 数量時系列 conf 0.34] 「tests」という複数形は、台帳に記載された2021年の破壊試験1件より多い試験を示しているのではありませんか。

#### N02: U04 s21

- 記事: U04(small_bag)
- 対象文: What we see here is only the attention given by fashion media and on runways.
- ±2文:
  - s19: We cannot use the attention on mini bags as proof that micro bags in general are popular again.
  - s20: Even a glamorous story needs a note of caution.
  - s21(対象): What we see here is only the attention given by fashion media and on runways.
  - s22: It does not prove demand among all shoppers or that sales have actually risen.
  - s23: “Often seen in magazines” and “often sold at the checkout” are two different things.
- Fact本文:
  - MB-02: Who What Wearは2026年5月、Bottega VenetaのMini Andiamoについて、ニューヨークとロサンゼルスのファッション関係者に好まれていると報じ、SNS上の着用例を紹介した。同記事は同モデルが「前月」に発売されたとしている。([whowhatwear.com](https://www.whowhatwear.com/fashion/luxury/bottega-veneta-mini-andiamo-bag-trend-2026))
  scope: 同記事が取り上げた特定のバッグと、ニューヨーク／ロサンゼルスの着用例。
  conditions: ファッション媒体による編集者の観察とSNS投稿の紹介。地域全体や消費者全体の代表調査ではない。
  date_or_period: 2026年5月（記事掲載月。発売は記事によればその前月）
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 特定モデルの局所的な注目例。ミニバッグ全般の市場復調や、XLバッグからの広範な乗り換えを示す証拠として一般化しない。
- reason:
  - [Luna A4 / その他 conf 0.30] 「only the attention given by fashion media and on runways」という限定は、ニューヨークとロサンゼルスの着用例やSNS投稿も紹介したMB-02の範囲と食い違う可能性があるのではありませんか。

#### N03: U05 s10

- 記事: U05(byd_recall)
- 対象文: As a result, there is a risk that the brake lights will stay on even when the brake pedal is not being pressed.
- ±2文:
  - s8: Often hidden behind showier features, this part started the trouble this time.
  - s9: According to the notice, the part may crack or break over time, and in an extreme case, it may come off.
  - s10(対象): As a result, there is a risk that the brake lights will stay on even when the brake pedal is not being pressed.
  - s11: In other words, no foot is pressing the brake, but the lights alone keep announcing, “The brake is being pressed!” The people on the ground and the press office are not communicating.
  - s12: The driver might want to say, “Could you run that announcement by me first?”
- Fact本文:
  - BYD-RECALL-07: 公告によると、極端な場合には限位垫が脱落し、制動ペダルを踏んでいないときにも制動灯が点灯し続ける可能性がある。
  scope: 召回対象車両のうち、限位垫が極端なケースで脱落した場合
  conditions: 公告上の説明は「極端な場合」に限った条件付きの可能性。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「ブレーキが効かなくなる」とは言い換えない。規制当局が明示する帰結は、ペダル非踏下時の制動灯常時点灯。
- reason:
  - [Luna A3 / 主体対象入替 conf 0.78] 公告では限位垫が脱落する「極端な場合」に制動灯が点灯し続ける可能性とされていますが、この文はその条件を外して一般的なリスクとして述べているのではありませんか。
  - [Luna A4 / その他 conf 0.78] 「there is a risk」と可能性を示す一方で、制動灯が点灯し続けるのは限位垫が脱落する極端な場合という条件が省かれているのではありませんか。

#### N04: U05 s11

- 記事: U05(byd_recall)
- 対象文: In other words, no foot is pressing the brake, but the lights alone keep announcing, “The brake is being pressed!” The people on the ground and the press office are not communicating.
- ±2文:
  - s9: According to the notice, the part may crack or break over time, and in an extreme case, it may come off.
  - s10: As a result, there is a risk that the brake lights will stay on even when the brake pedal is not being pressed.
  - s11(対象): In other words, no foot is pressing the brake, but the lights alone keep announcing, “The brake is being pressed!” The people on the ground and the press office are not communicating.
  - s12: The driver might want to say, “Could you run that announcement by me first?”
  - s13: But on the road, this is not something you can laugh off and correct.
- Fact本文:
  - BYD-RECALL-07: 公告によると、極端な場合には限位垫が脱落し、制動ペダルを踏んでいないときにも制動灯が点灯し続ける可能性がある。
  scope: 召回対象車両のうち、限位垫が極端なケースで脱落した場合
  conditions: 公告上の説明は「極端な場合」に限った条件付きの可能性。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「ブレーキが効かなくなる」とは言い換えない。規制当局が明示する帰結は、ペダル非踏下時の制動灯常時点灯。
- reason:
  - [Luna A3 / 主体対象入替 conf 0.65] 公告では限位垫が脱落する「極端な場合」に制動灯が点灯し続ける可能性とされていますが、この文はその条件を外して、ペダルを踏んでいないときに常に点灯するように読めるのではありませんか。

#### N05: U05 s27

- 記事: U05(byd_recall)
- 対象文: BYD is recalling 183,211 cars in China because faulty pedal pads may keep the brake lights on when drivers aren’t braking.
- ±2文:
  - s25: On the road, we want cars to be good at getting the message across, not just good at talking.
  - s26: ## In one line
  - s27(対象): BYD is recalling 183,211 cars in China because faulty pedal pads may keep the brake lights on when drivers aren’t braking.
- Fact本文:
  - BYD-RECALL-06: 規制当局公告は、製造上の問題により制動ペダルの限位垫（brake pedal stopper pad／ペダルストッパーパッド）の材料にロット単位の異常が生じたと説明している。長期間使用すると、当該部品がひび割れ・破損する可能性がある。
  scope: 召回対象の唐系・秦系車両に取り付けられた制動ペダル限位垫
  conditions: 公告は材料異常を製造上の問題に帰属させ、長期間使用後の破損可能性を記載。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 対象部品は制動ペダルの限位垫。公告が説明する不具合はこの部品の材料異常・ひび割れ・破損であり、ブレーキそのものの制動不能とは記載していない。
  - BYD-RECALL-07: 公告によると、極端な場合には限位垫が脱落し、制動ペダルを踏んでいないときにも制動灯が点灯し続ける可能性がある。
  scope: 召回対象車両のうち、限位垫が極端なケースで脱落した場合
  conditions: 公告上の説明は「極端な場合」に限った条件付きの可能性。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「ブレーキが効かなくなる」とは言い換えない。規制当局が明示する帰結は、ペダル非踏下時の制動灯常時点灯。
- reason:
  - [Luna A3 / 主体対象入替 conf 0.78] 公告では限位垫の材料異常に続いてひび割れ・破損の可能性があり、脱落する「極端な場合」に制動灯が点灯し続けるとされていますが、この文はその条件を外して部品が直接点灯を引き起こすように述べているのではありませんか。
  - [Luna A4 / その他 conf 0.81] 「may keep the brake lights on」と述べていますが、公告が示すのは限位垫が脱落する極端な場合に限った可能性ではありませんか。

#### N06: U06 s1

- 記事: U06(streaming_price)
- 対象文: # Disney+ Prices Are Going Up: Don’t Miss the “Coming Up Next” on Your Bill!
- ±2文:
  - s1(対象): # Disney+ Prices Are Going Up: Don’t Miss the “Coming Up Next” on Your Bill!
  - s2: The news that “Disney+ is raising its prices” may have made tense background music start playing in your mental household budget.
  - s3: Before you clutch your wallet and think, “Not my subscription fees again...,” pause here.
- Fact本文:
  - F01: 2026年10月8日までに今回のWeb調査で確認できた主要な米国向け動画ストリーミング価格改定のうち、最も新しい発表としてDisney+の2026年9月23日の改定を選定した。
  scope: 米国向け動画ストリーミングサービスの価格改定発表として調査で確認した範囲
  conditions: 「最も新しい」は調査時点までにWeb検索で確認できた発表に基づく選定。
  date_or_period: 発表日：2026-09-23。調査基準日：2026-10-08
  ambiguity_note: 全世界・全地域の小規模サービスを網羅した比較ではなく、検索で確認できた主要サービスの発表からの選定。
  notes_for_writer: 対象はDisney+の当該発表に限定する。他サービスとの比較はしない。
  - F05: Disney+の改定後価格は米国向けであり、公式価格ページは第三者請求パートナー経由では価格が異なる場合があると記載している。
  scope: Disney+ Help Centerの米国向け価格ページに掲載された価格
  conditions: 第三者請求パートナー経由の価格は、プラットフォーム上の制限や地域別価格により異なる場合がある。
  date_or_period: 2026-09-23掲載の価格情報
  notes_for_writer: 確認した価格を全世界共通価格として記述しない。
- reason:
  - [Luna A3 / その他 conf 0.30] 「Disney+ Prices Are Going Up」は、確認対象の米国向け価格改定だけでなく全地域・全プランの値上げを示す表現ではありませんか。

#### N07: X11 s28

- 記事: X11(openai_copyright)
- 対象文: Fourteen news companies and related entities are asking a court to destroy OpenAI’s models and training sets they say contain their content.
- ±2文:
  - s26: For now, all we know is that demands have been made that cannot be summed up as “pay and it’s over.” How much of that bill will be accepted remains to be seen.
  - s27: ## In one line
  - s28(対象): Fourteen news companies and related entities are asking a court to destroy OpenAI’s models and training sets they say contain their content.
- Fact本文:
  - F2: 訴状に記載された原告は14の法人・事業体で、USA TODAY Co., Inc.、Gannett Satellite Information Network, LLC、Gannett GP Media, Inc.、The Courier-Journal, Inc.、Des Moines Register and Tribune Company、Detroit Free Press, Inc.、Detroit Newspaper Partnership, L.P.、CA Florida Holdings, LLC、Scripps NP Operating, LLC、CA North Carolina Holdings, Inc.、GateHouse Media Oklahoma Holdings, Inc.、Journal Sentinel Inc.、GateHouse Media Ohio Holdings II, Inc.、Phoenix Newspapers, Inc.である。訴状は、これらをUSA TODAY Co., Inc.傘下の原告らとしている。
  scope: 本件訴状に名を連ねる法人・事業体
  conditions: 訴状に記載された当事者名。各出版物そのものがすべて別個の法人原告だという意味ではない。
  numeric_value: 14 (numeric_scope: 訴状の共同原告として記載された法人・事業体数)
  date_or_period: 2026-10-08時点の訴状
  notes_for_writer: 原告数14と、訴状が対象として挙げる出版物数19を混同しない。
  - F6: 原告らは、損害賠償額が2億5,000万ドルを超えるとする請求を記載し、法定・補償的損害賠償、利益の返還・吐き出し、宣言的救済、恒久的差止め、訴訟費用・弁護士費用等を求めている。さらに、原告らのコンテンツを組み込んだGPTその他の大規模言語モデルおよび訓練セットの破棄も請求している。
  scope: 本件訴状のPrayer for Reliefおよび損害額に関する記載
  conditions: 請求された救済であり、裁判所が認めた損害額・救済ではない。
  numeric_value: 2億5,000万ドル超 (numeric_scope: 原告らが訴状で求める損害賠償額。認容額ではない。)
  date_or_period: 2026-10-08に提出された訴状
  notes_for_writer: 金額とモデル・訓練セットの破棄はいずれも原告側の請求。認容・命令済みと書かない。
- reason:
  - [Gemini A3 / 主体対象入替 conf 0.30] s28で「Fourteen news companies」とありますが、台帳F2では14の法人・事業体、F3では19出版物とされていますが、これらはすべて純粋な「news companies（報道企業）」であると断定して問題ありませんか？

### 版B(confidence・モデル名なし)

#### N01: U03 s18

- 記事: U03(space_weapons)
- 対象文: But these were tests fired from the ground.
- ±2文:
  - s16: “Haven’t there already been weapons that destroy satellites?” That’s right.
  - s17: Russia has destroyed satellites with ground-launched anti-satellite missiles.
  - s18(対象): But these were tests fired from the ground.
  - s19: “Firing from the ground into space” and “placing a weapon in orbit” both involve space, but they have different starting points and locations.
  - s20: The terminology needs care, too.
- Fact本文:
  - F-003: ロシアは2021年11月15日、地上発射型の直接上昇式ASATミサイルでロシアの衛星COSMOS 1408を破壊し、1,500個超の追跡可能な軌道デブリを発生させた。([spacecom.mil](https://www.spacecom.mil/Newsroom/News/Article-Display/Article/2842957/russian-direct-ascent-anti-satellite-missile-test-creates-significant-long-last/?utm_source=openai))
  scope: 低軌道、COSMOS 1408および発生デブリ
  conditions: 米宇宙軍による公式発表
  numeric_value: >1,500個 (numeric_scope: 追跡可能な軌道デブリ)
  date_or_period: 2021年11月15日
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 地上から発射したASATミサイルによる破壊試験であり、兵器を軌道上に恒久配備した事例とは区別する。
- reason:
  - 「tests」という複数形は、台帳に記載された2021年の破壊試験1件より多い試験を示しているのではありませんか。

#### N02: U04 s21

- 記事: U04(small_bag)
- 対象文: What we see here is only the attention given by fashion media and on runways.
- ±2文:
  - s19: We cannot use the attention on mini bags as proof that micro bags in general are popular again.
  - s20: Even a glamorous story needs a note of caution.
  - s21(対象): What we see here is only the attention given by fashion media and on runways.
  - s22: It does not prove demand among all shoppers or that sales have actually risen.
  - s23: “Often seen in magazines” and “often sold at the checkout” are two different things.
- Fact本文:
  - MB-02: Who What Wearは2026年5月、Bottega VenetaのMini Andiamoについて、ニューヨークとロサンゼルスのファッション関係者に好まれていると報じ、SNS上の着用例を紹介した。同記事は同モデルが「前月」に発売されたとしている。([whowhatwear.com](https://www.whowhatwear.com/fashion/luxury/bottega-veneta-mini-andiamo-bag-trend-2026))
  scope: 同記事が取り上げた特定のバッグと、ニューヨーク／ロサンゼルスの着用例。
  conditions: ファッション媒体による編集者の観察とSNS投稿の紹介。地域全体や消費者全体の代表調査ではない。
  date_or_period: 2026年5月（記事掲載月。発売は記事によればその前月）
  causal_strength: OBSERVED_REPORTED
  notes_for_writer: 特定モデルの局所的な注目例。ミニバッグ全般の市場復調や、XLバッグからの広範な乗り換えを示す証拠として一般化しない。
- reason:
  - 「only the attention given by fashion media and on runways」という限定は、ニューヨークとロサンゼルスの着用例やSNS投稿も紹介したMB-02の範囲と食い違う可能性があるのではありませんか。

#### N03: U05 s10

- 記事: U05(byd_recall)
- 対象文: As a result, there is a risk that the brake lights will stay on even when the brake pedal is not being pressed.
- ±2文:
  - s8: Often hidden behind showier features, this part started the trouble this time.
  - s9: According to the notice, the part may crack or break over time, and in an extreme case, it may come off.
  - s10(対象): As a result, there is a risk that the brake lights will stay on even when the brake pedal is not being pressed.
  - s11: In other words, no foot is pressing the brake, but the lights alone keep announcing, “The brake is being pressed!” The people on the ground and the press office are not communicating.
  - s12: The driver might want to say, “Could you run that announcement by me first?”
- Fact本文:
  - BYD-RECALL-07: 公告によると、極端な場合には限位垫が脱落し、制動ペダルを踏んでいないときにも制動灯が点灯し続ける可能性がある。
  scope: 召回対象車両のうち、限位垫が極端なケースで脱落した場合
  conditions: 公告上の説明は「極端な場合」に限った条件付きの可能性。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「ブレーキが効かなくなる」とは言い換えない。規制当局が明示する帰結は、ペダル非踏下時の制動灯常時点灯。
- reason:
  - 公告では限位垫が脱落する「極端な場合」に制動灯が点灯し続ける可能性とされていますが、この文はその条件を外して一般的なリスクとして述べているのではありませんか。
  - 「there is a risk」と可能性を示す一方で、制動灯が点灯し続けるのは限位垫が脱落する極端な場合という条件が省かれているのではありませんか。

#### N04: U05 s11

- 記事: U05(byd_recall)
- 対象文: In other words, no foot is pressing the brake, but the lights alone keep announcing, “The brake is being pressed!” The people on the ground and the press office are not communicating.
- ±2文:
  - s9: According to the notice, the part may crack or break over time, and in an extreme case, it may come off.
  - s10: As a result, there is a risk that the brake lights will stay on even when the brake pedal is not being pressed.
  - s11(対象): In other words, no foot is pressing the brake, but the lights alone keep announcing, “The brake is being pressed!” The people on the ground and the press office are not communicating.
  - s12: The driver might want to say, “Could you run that announcement by me first?”
  - s13: But on the road, this is not something you can laugh off and correct.
- Fact本文:
  - BYD-RECALL-07: 公告によると、極端な場合には限位垫が脱落し、制動ペダルを踏んでいないときにも制動灯が点灯し続ける可能性がある。
  scope: 召回対象車両のうち、限位垫が極端なケースで脱落した場合
  conditions: 公告上の説明は「極端な場合」に限った条件付きの可能性。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「ブレーキが効かなくなる」とは言い換えない。規制当局が明示する帰結は、ペダル非踏下時の制動灯常時点灯。
- reason:
  - 公告では限位垫が脱落する「極端な場合」に制動灯が点灯し続ける可能性とされていますが、この文はその条件を外して、ペダルを踏んでいないときに常に点灯するように読めるのではありませんか。

#### N05: U05 s27

- 記事: U05(byd_recall)
- 対象文: BYD is recalling 183,211 cars in China because faulty pedal pads may keep the brake lights on when drivers aren’t braking.
- ±2文:
  - s25: On the road, we want cars to be good at getting the message across, not just good at talking.
  - s26: ## In one line
  - s27(対象): BYD is recalling 183,211 cars in China because faulty pedal pads may keep the brake lights on when drivers aren’t braking.
- Fact本文:
  - BYD-RECALL-06: 規制当局公告は、製造上の問題により制動ペダルの限位垫（brake pedal stopper pad／ペダルストッパーパッド）の材料にロット単位の異常が生じたと説明している。長期間使用すると、当該部品がひび割れ・破損する可能性がある。
  scope: 召回対象の唐系・秦系車両に取り付けられた制動ペダル限位垫
  conditions: 公告は材料異常を製造上の問題に帰属させ、長期間使用後の破損可能性を記載。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 対象部品は制動ペダルの限位垫。公告が説明する不具合はこの部品の材料異常・ひび割れ・破損であり、ブレーキそのものの制動不能とは記載していない。
  - BYD-RECALL-07: 公告によると、極端な場合には限位垫が脱落し、制動ペダルを踏んでいないときにも制動灯が点灯し続ける可能性がある。
  scope: 召回対象車両のうち、限位垫が極端なケースで脱落した場合
  conditions: 公告上の説明は「極端な場合」に限った条件付きの可能性。
  causal_strength: CAUSAL_STATED_BY_SOURCE
  notes_for_writer: 「ブレーキが効かなくなる」とは言い換えない。規制当局が明示する帰結は、ペダル非踏下時の制動灯常時点灯。
- reason:
  - 公告では限位垫の材料異常に続いてひび割れ・破損の可能性があり、脱落する「極端な場合」に制動灯が点灯し続けるとされていますが、この文はその条件を外して部品が直接点灯を引き起こすように述べているのではありませんか。
  - 「may keep the brake lights on」と述べていますが、公告が示すのは限位垫が脱落する極端な場合に限った可能性ではありませんか。

#### N06: U06 s1

- 記事: U06(streaming_price)
- 対象文: # Disney+ Prices Are Going Up: Don’t Miss the “Coming Up Next” on Your Bill!
- ±2文:
  - s1(対象): # Disney+ Prices Are Going Up: Don’t Miss the “Coming Up Next” on Your Bill!
  - s2: The news that “Disney+ is raising its prices” may have made tense background music start playing in your mental household budget.
  - s3: Before you clutch your wallet and think, “Not my subscription fees again...,” pause here.
- Fact本文:
  - F01: 2026年10月8日までに今回のWeb調査で確認できた主要な米国向け動画ストリーミング価格改定のうち、最も新しい発表としてDisney+の2026年9月23日の改定を選定した。
  scope: 米国向け動画ストリーミングサービスの価格改定発表として調査で確認した範囲
  conditions: 「最も新しい」は調査時点までにWeb検索で確認できた発表に基づく選定。
  date_or_period: 発表日：2026-09-23。調査基準日：2026-10-08
  ambiguity_note: 全世界・全地域の小規模サービスを網羅した比較ではなく、検索で確認できた主要サービスの発表からの選定。
  notes_for_writer: 対象はDisney+の当該発表に限定する。他サービスとの比較はしない。
  - F05: Disney+の改定後価格は米国向けであり、公式価格ページは第三者請求パートナー経由では価格が異なる場合があると記載している。
  scope: Disney+ Help Centerの米国向け価格ページに掲載された価格
  conditions: 第三者請求パートナー経由の価格は、プラットフォーム上の制限や地域別価格により異なる場合がある。
  date_or_period: 2026-09-23掲載の価格情報
  notes_for_writer: 確認した価格を全世界共通価格として記述しない。
- reason:
  - 「Disney+ Prices Are Going Up」は、確認対象の米国向け価格改定だけでなく全地域・全プランの値上げを示す表現ではありませんか。

#### N07: X11 s28

- 記事: X11(openai_copyright)
- 対象文: Fourteen news companies and related entities are asking a court to destroy OpenAI’s models and training sets they say contain their content.
- ±2文:
  - s26: For now, all we know is that demands have been made that cannot be summed up as “pay and it’s over.” How much of that bill will be accepted remains to be seen.
  - s27: ## In one line
  - s28(対象): Fourteen news companies and related entities are asking a court to destroy OpenAI’s models and training sets they say contain their content.
- Fact本文:
  - F2: 訴状に記載された原告は14の法人・事業体で、USA TODAY Co., Inc.、Gannett Satellite Information Network, LLC、Gannett GP Media, Inc.、The Courier-Journal, Inc.、Des Moines Register and Tribune Company、Detroit Free Press, Inc.、Detroit Newspaper Partnership, L.P.、CA Florida Holdings, LLC、Scripps NP Operating, LLC、CA North Carolina Holdings, Inc.、GateHouse Media Oklahoma Holdings, Inc.、Journal Sentinel Inc.、GateHouse Media Ohio Holdings II, Inc.、Phoenix Newspapers, Inc.である。訴状は、これらをUSA TODAY Co., Inc.傘下の原告らとしている。
  scope: 本件訴状に名を連ねる法人・事業体
  conditions: 訴状に記載された当事者名。各出版物そのものがすべて別個の法人原告だという意味ではない。
  numeric_value: 14 (numeric_scope: 訴状の共同原告として記載された法人・事業体数)
  date_or_period: 2026-10-08時点の訴状
  notes_for_writer: 原告数14と、訴状が対象として挙げる出版物数19を混同しない。
  - F6: 原告らは、損害賠償額が2億5,000万ドルを超えるとする請求を記載し、法定・補償的損害賠償、利益の返還・吐き出し、宣言的救済、恒久的差止め、訴訟費用・弁護士費用等を求めている。さらに、原告らのコンテンツを組み込んだGPTその他の大規模言語モデルおよび訓練セットの破棄も請求している。
  scope: 本件訴状のPrayer for Reliefおよび損害額に関する記載
  conditions: 請求された救済であり、裁判所が認めた損害額・救済ではない。
  numeric_value: 2億5,000万ドル超 (numeric_scope: 原告らが訴状で求める損害賠償額。認容額ではない。)
  date_or_period: 2026-10-08に提出された訴状
  notes_for_writer: 金額とモデル・訓練セットの破棄はいずれも原告側の請求。認容・命令済みと書かない。
- reason:
  - s28で「Fourteen news companies」とありますが、台帳F2では14の法人・事業体、F3では19出版物とされていますが、これらはすべて純粋な「news companies（報道企業）」であると断定して問題ありませんか？

## 9. 費用実測

| モデル | call数(HTTP) | 入力tok | 出力tok(thinking込み) | 実費JPY | 見積(中央/高位) |
|---|---|---|---|---|---|
| Luna | 22(22) | 110278 | 21057 | 3.449 | 4.4 / 9.4 |
| Gemini 3.5 Flash-Lite | 22(22) | 104060 | 303 | 4.764 | 5.9 / 24.2 |
| **合計** | 44 | | | **8.213** | 10.3 / 33.6 |

累計JPY100ガード: 未到達。台帳 `cost_ledger_dm_01.jsonl`。見積差(実費-中央): -2.09。

## 10. 参考: META rollback(母集団外)

CROSSMODEL-01(`meta_rollback_crossmodel_01/RESULT_01.md`)の結果を参考付記のみ(本Trialの集計に含めない)。機械読取: {"luna": {"closeout": "DETECTED", "A3": "Yes", "A4": "Yes"}, "gemini35fl": {"closeout": "DETECTED", "A3": "Yes", "A4": "Yes"}}。

## 11. Status提案・不変更

- Status提案: **USER_DECISION_REQUIRED**(ChatGPT側照合後に判定)。A3_REMOVAL_SUPPORTED等はClaude側で確定しない。
- APPROVED項目(OPEN-244運用コンセプト、R0後/翻訳後Hard STOP除去)は不変更、未PRODUCTION_WIRED。A3+A4英訳後配置=VALIDATED不変。
- やらないこと9項目(PREREGISTRATION_01.md 9節)未実施。Production・CURRENT_SPEC・Prompt変更なし。

