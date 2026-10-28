# METHOD_DIFF_01: Family X Std日本語Comment方式 と Family Z Std方式の差分(実コード照合)

照合元: X=`er019_family_x_audio_production_runner_01.py:331-355`(`run_family_x_a2_scaffold`)、`er019_family_x_audio_plan_01.py:209-241`(Comment3/4 role)、`er003_v1_iran01_a2_generate.py:91-257`(共通Prompt枠・Comment1/2/Preview role・`run_support_text`)。Z=`er062_family_z_writer_01.py:1242-1296`(`run_support_std`)、同`:1146-1177`(lint/retry・`limit_comment3_part`)、同`:245`(`NOT_NEWS_NOTE`)。

## 1. 同一(固定した)項目
| 項目 | X(Before) | Z | 根拠 |
|---|---|---|---|
| 生成関数・Prompt枠 | `a2gen.run_support_text` / `build_support_prompt`(SUPPORT_JA_PRINCIPLE+SUPPORT_PROHIBITIONS+context+出力形式) | 同じ関数をimport(`er062:1250`) | iran01_a2:91-123, 207 |
| Comment1 role | `a2gen.COMMENT_1_ROLE`(Listening Focus、原則1文) | 同一定数 | runner:336 / er062:1261 |
| Comment2 role | `a2gen.COMMENT_2_ROLE`(前半核心を1点回収+後半への問い、1〜2文) | 同一定数 | runner:340 / er062:1261 |
| Preview | `a2gen.PREVIEW_ROLE`(Comment1/2を渡して重複回避)、本文全文入力、**最後に生成** | 同一定数・同一順序 | runner:349-355 / er062:1276 |
| モデル/効き | `routing.require_model("A2_SUPPORT")`=gpt-6-luna、reasoning effort・temperature/seed指定なし | 同一 | runner:129-130 / er062:1253 |
| Comment 1/2の参照範囲 | C1=Part1のみ、C2=Part1(聞いた)+Part2(これから) | 同一範囲 | runner:335,339 / er062:1257-1258 |
| 生成順序 | C1→C2→C3→C4→Preview | C1→C2→C3→Preview(Comment間の連鎖入力なし=互いのtextは渡さない) | runner:331-355 / er062:1262-1280 |

=> C1/C2はX・Zで実質同一方式。ラベル文言とStory向け注記の有無しか違わず、Before/After差は主に生成揺らぎ(同一モデル・非決定)になる。

## 2. 方式差(Afterで取り入れた項目)
| # | 項目 | X(Before) | Z方式(After) |
|---|---|---|---|
| D1 | **Comment 3のrole** | `FAMILY_X_A2_COMMENT_3_ROLE`(Mid-story Recovery + Bridge to Part 3、2〜3文、『第3部の結論を先に言ってはいけません』)er019_plan:209-219 | `a2gen.COMMENT_2_ROLE`を流用(Comment2とComment3は同じrole、1〜2文、前半核心を1点回収+後半への問い)er062:1261 |
| D2 | **Comment 3の本文参照範囲** | Part1+Part2のみ(Part3は一切見せない)runner:343 | Part1+Part2(聞いた)+**Part3の先頭約25%(最低2段落)**かつ到着/結末段落以降を除外(`limit_comment3_part`)er062:1158-1177,1259 |
| D3 | context見出し | 【これから聞く本文(本文1、英語)】/【すでに聞いた本文(本文1)】/【本文1】等 | 【本文(これから聞く部分)】/【すでに聞いた本文(前半)】/【これから聞く本文(後半)】er062:1257-1259 |
| D4 | 決定論lint+retry | なし(J2範囲値正規化のみ。runner:317-328) | `lint_support_text`(ネタバレ語/禁止名/ニュース語/構造ラベル)違反→retry1回→STOP。LISTEN_INSTRUCTIONのみWARN er062:1146-1155,1255 |
| D5 | 物語向け注記 | なし | `NOT_NEWS_NOTE`(『ニュースではなく短い物語』)を全contextへ付加 er062:245 |
| D6 | 後処理 | J2(『数字〜数字』→『数字から数字』) | なし(Z側にJ2は無い) |
| D7 | Comment 4 | あり(`FAMILY_X_A2_COMMENT_4_ROLE`、Part1-3全文入力、In One Lineへの橋渡し、『最後に』) | **なし**(Zは3 Comment構成) |

## 3. After生成での適用(比較軸の分離)
- D1・D2(**中心の方式差**)・D3を適用。D5(Story向け)は**適用しない**(ニュースに誤)。D4のlintはStory向け語禁止(『記事』『ニュース』等)を含み、Xの正規文言(『この記事では』)と矛盾するためGate/retryに使わず、参考表示のみ(ログ記載)。D6は後処理のみで適用なし(AfterにJ2は未適用。今回の本文に範囲値『〜』はなく影響なし)。
- ネタバレ制御のニュース適用(Story固有→ニュース): ZのPart3先頭25%・最低2段落規則の定数(`COMMENT3_FACT_RATIO/MIN_PARAGRAPHS`)は流用し、Story固有の『到着/城門/剣』目印の代わりに、結論・留保段落の目印(`even so|still,|in short|overall|in conclusion|too soon|do not show|proof`)以降を除外。本記事のPart3は3段落で、先頭2段落→『Even so…』を含む第2段落以降を除外→**Part3第1段落のみ**がComment3に渡る。第1段落は『特定の記憶(方法)を消すと塔の平均数が下がった』という中心結果を含むため、渡す範囲自体が結果を含む点に注意(後述の所見)。
- Comment 4: Z方式にComment4は存在しない。X固有role(`FAMILY_X_A2_COMMENT_4_ROLE`)・参照範囲(全文)・生成順(Comment3の後)は不変で、Z流ラベル『すでに聞いた本文(全体)』に変えただけ。X側の入力は既にZ流の『聞き終えた全文』と同等のため、**方式差は実質なし=実質再サンプル**。条件変更はラベルのみ。
- Preview/KP/本文/文法/音声は不変(Beforeのものを維持、Afterで生成せず)。

## 4. 入力固定
本文=`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/a2/parts.json`(sha256 444f9836…012d4b、Before生成時と同一)。注: 完成版音声はLocal Rewriteで『AIs sent』→『AI agents sent』の1語が変わっているが、Beforeの生成入力(parts.json)は『AIs』であり、Afterも同じparts.jsonを使用(条件同一)。
