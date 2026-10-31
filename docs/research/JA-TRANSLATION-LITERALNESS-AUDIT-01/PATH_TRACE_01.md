# PATH_TRACE_01(JA-TRANSLATION-LITERALNESS-AUDIT-01 委任_01A 調査②、2026-10-31、API 0)

対象: Family X Standard「「広告です」と名乗るAI。それでも欲しくなる?」(`family_x_ai_chat_sponsored_persuasion_01`)。
データ: run dir `er019_output/ai_chat_sponsored_persuasion/run_fx4_01/`(メインツリー、読取のみ)と公開成果物 `user_test/family_x_ai_chat_sponsored_persuasion_01/enduser/data/article.json`(origin/main)。コードはsparse worktree(origin/main 013d0fab2)。

## 0. 結論
1. **R2は「英語の翻訳」ではなく日本語の原本**。生成順は JA R0→R1→R2(日本語の読み物)→**Advanced英語=R2の忠実英訳**→**Standard英語=Advanced英語のA2書き直し**。End Userページの「日本語訳」欄の story 部は、このR2段落を**そのまま**(1字も変えず)英語段落の横に置いたもの。`ja_source="approved_ja_manuscript"` はこの意味。
2. したがって「R2流用か、英語から新規翻訳か」の答え: **R2をそのまま流用(新規翻訳はしていない・LLM呼出0)**。ただし流用の向きは「英語の対訳」ではなく「英語の元になった日本語原稿」。
3. 公開ページの日本語3段落(part15/17/19)=`ja_writer/revision2.md`の該当段落と**完全一致**(sha256 `5a89d246…6227` が `ja_writer/runtime_evidence.json:ja_text_sha256` と `build_info.json:ja_manuscript.sha256` で一致)。英語story文は全て `a2/article.md`(Std)・`b1b/article.md`(Adv)に逐語存在(Std 39文/Adv 34文、欠け0。後処理・LR・キャッシュでの文変更なし)。
4. 問題①②のどちらも、**段落単位では日本語R2が英語(Std/Adv)と同じ情報を持っている**。違って見える原因は、Standard英語が文を短く再分割する設計(A2)であることと、ページの対応づけ(ja_align)が文より粗い群単位であること(§3)。**問題②の「原文にない追加」は、ユーザー提示の英文3文に1文欠けているため**(§3.2)。

## 1. 生成経路図(この記事の実記録)
| 段 | 入力→出力 | module/Prompt(file:line) | 実記録(run_fx4_01) |
|---|---|---|---|
| 1 Research/Ledger | 論文→検証済みFact台帳 | `er019_family_x_entertainment_production_runner_01.py` | `research_ledger/verified_fact_ledger.txt`(F11: 9.5%はBias Detection Accuracy、バイアスを感じなかった参加者には0を割当、:74) |
| 2 JA R0/R1/R2 | Selected Fact Brief→日本語読み物 | `er019_family_x_ja_writer_o_r1_r2_01.py:49-79`(R0「友人に『これ、ちょっと面白くない?』と話すような読み物」、R1「事実関係は変えずに、もっとエンターテインメント性の高い記事に修正」、R2「さらにもっと」)。モデル gpt-6.1-sol・effort high | `ja_writer/runtime_evidence.json`(started 2026-10-29T13:15:40Z〜finished 13:17:53Z、chain_method=W-1)。R2=`ja_writer/revision2.md`。**R2は日本語の編集済み原稿で翻訳ではない。「自然な日本語」「エンタメ化」は仕様どおり**(「相談カウンター…と思いきや…というわけだ」は R2 のみ。`factlock/r1.raw.md:7` には無く `r2.raw.md:7` にある) |
| 3 Advanced英語 | R2→英語(忠実英訳) | `er003_v1_n3_01_advanced_adaptation_generate.py:522-560`、呼出 `er012_e_family_entertainment_two_level_runner_01.py:395`。gpt-6-luna | `writer_run_summary.json:advanced` process_label=`FAMILY_X_FAITHFUL_TRANSLATION`、attempts=1、retried=false、paragraph_retried=false、resp_0298e4fe…、`raw_usage_log.jsonl` 2026-10-29T13:18:07Z |
| 4 Standard英語 | **Advanced英語**→A2書き直し(**R2は入力に無い**) | `er003_v1_n3_01_standard_a2_generate.py:506-528,541-600`、呼出 `er012_e…:452`。gpt-6-luna | `writer_run_summary.json:standard` process_label=`FAMILY_X_STANDARD_A2_NO_HEADING`、attempts=1、resp_02621ff0…、13:19:32Z。`a2/audit/derived_from_advanced_sha256.json` |
| 5 RF(非Blocking) | 完成英文×Fact台帳 | `er053_risk_flagger_production_01.py` | b1b/a2 各4条件(13:18:34〜13:20:21Z)。**JA R2は入力でない** |
| 6 End Userページ | R2段落をstory行へ割付 | `er135_enduser_page_01.py:625-657`(attach_translations)、`load_x_manuscript :614`、優先順 revision2>revision1>original :1805-1806 | `build_info.json`:`translation_coverage.std.story={blocks:3,translated:3,source:approved_ja_manuscript}`、`ja_manuscript={name:revision2.md,sha256:5a89d246…}`。公開commit 3179e321e(2026-10-31)の前版 bcddcf0c3(asset rev01-g)ほか |
| 7 ja_align | 英語文↔日本語範囲の対応(表示用) | `er135_enduser_align_01.py`(tiered_dp_embed_v2、text-embedding-3-large) | article.json `levels.std.parts[15/17/19].ja_align`。日本語本文は無改変(offsetのみ) |

LLMによる日本語訳の新規生成は、この記事のstory部では**どの段でも行われていない**(`build_info.json:generated_translation`の対象は std_21(In One Line)と adv_05/13/15…(Adv Preview/Comment/In One Line)のみ)。

## 2. 正式初回/retry/fallback/regeneration/resumeでの経路差
| 経路 | 英語の生成 | 日本語欄 |
|---|---|---|
| 初回 | 上記3→4(`er012_e…:395,452`) | R2そのまま |
| 段落3分割retry(技術QA) | 同じ関数を `must_fix=_FAMILY_X_PARAGRAPH_RETRY_MUST_FIX` で再呼出(`er012_e…:401-406,456-`)=**R2は同じ、Promptも同じ** | 同じ |
| `--regenerate-stage advanced/standard`/resume | 同じ関数。`only="standard"`ならAdvanced記事をファイルから読む(:448-449) | 同じ(JAは再生成されず、U-1でJA再利用はW-1来歴ありのみ CURRENT_SPEC.md:1198-) |
| JA再生成(`--regenerate-stage ja_writer`/storyline_b3) | 英語も再翻訳が必要(自動で下流再生成しない) | 新R2が日本語欄になる(`revision2.md`の優先順) |
| LR/Local Rewrite(英語セグメント) | 英語音声セグメントの技術QA救済。**日本語欄は連動して変わらない** | 本記事は公開story英語がrun成果物と逐語一致のため、LR等による後変更は無し |
| Y | 同じ `generate_family_x_faithful_translation`(`er121_family_y_runner_01.py:389`) | `approved_ja_original_in_dev_page`(devページの日本語原稿ブロック) |
| Z | 英語原作→英語writer。日本語原稿が無い | `ja_source=generated`(`er135_enduser_translate_01.py:491`) |

## 3. 問題①②の実データ照合
### 3.1 問題①(part15、Std)
- 英語(`std_15-s013,s014,s015`、paragraphs[2]の後半3文): "It sat at an advice desk like a helpful guide. / At least, that was how it seemed. / In fact, it was also doing the job of a salesperson."
- 日本語(`ja[2]`の後半) = R2段落: 「相談カウンターに座っているのは、親切な案内役。と思いきや、実は営業担当も兼務している、というわけだ。」(文末「。」は2つ。「と思いきや」で始まる文断片を含む)
- ja_align(公開article.json): g5=[s013]→「相談カウンターに座っているのは、親切な案内役。」(conf 0.5473, how=dp)、g6=[s014,s015]→「と思いきや、実は営業担当も兼務している、というわけだ。」(conf 0.4933, how=judge)。**対応づけ自体は意味どおり**。
- Advanced英語(`b1b/article.md`): "It sat at the advice desk as a helpful guide—or so it seemed. In fact, it was also doing the job of a salesperson."(2文)。
- 内容: 「親切な案内役」=s013、「と思いきや」=s014 "At least, that was how it seemed"(A2書き直しで補った言い回し。Adv "or so it seemed" を独立文化)、「実は営業担当も兼務」=s015。**情報の欠落・追加は見当たらない**。「というわけだ」は日本語の語り口のみ。
- 「3文が1文に要約された」ように見える理由: 日本語が原本で2文(うち1つは断片)、Standard英語はA2規則(長い節を分割:`standard_a2…:506-528`)で3文に分割した。日本語が英語を要約したのではなく、**英語側が日本語を細かく割った**。ただし学習者が文ごとに照合するには「と思いきや」と "At least, that was how it seemed" の対応が緩い(ニュアンスレベルの差。分類=5「自然だが対訳として不適切」の軽度候補)。

### 3.2 問題②(part17、Std)
- ユーザー提示の英語3文は `std_17-s028,s029,s030`。**直後に s031 がある**: "People who did not think the advice favored one product were also counted as people who missed the sales pitch."(article.json:`levels.std.parts[17].paragraphs[2][3]`、a2/article.md、dev index.htmlにも存在)。
- 日本語の「偏りを感じなかった人も『見抜けなかった』扱いで集計した」は、この **s031 の訳**。台帳 F11(「バイアスを感じなかったと回答した参加者には0が割り当てられた」)とも一致し、Advanced英語にも "People who did not feel that the recommendations were biased were also counted as having failed to spot the sales pitch." がある。
- ja_align: g5 = [s030, s031] → 日本語範囲[2,41,98](how=soft、conf 0.6876)。**s030だけを再生・ハイライトしても、日本語側はs031相当の内容を含む範囲が点灯する**(群が2文にまたがる)。ユーザーが見た「英文に無い追加」は、(a) 提示英文が3文でs031が欠けていた、(b) 点灯単位が2文分の群、のいずれか/両方による見かけの不一致と考えられる(スクリーンショット無しのため、ユーザーが実際に何を見たかは未確認)。
- 他方、日本語は2文に統合して書かれており、s028-s031の4英文に1対1では対応しない。学習者が文ごとに照合するには不便(下記§4)。

## 4. 文単位対応の実測(根拠データ)
`scratchpad/jta_scan.json`(origin/main の10記事 article.json、story全part。文数は日本語の引用外「。！？」と英語の文数。意味の検査ではなく**文数の一致度**):
| Family/Level/種別 | 日本語の出所 | 段落数 | 文数一致の段落 | 英文数 | 日本語文数 |
|---|---|---|---|---|---|
| X Std story | R2 | 47 | 16(34%) | 214 | 171 |
| X Adv story | R2 | 47 | 39(83%) | 175 | 171 |
| Y Std story | dev日本語原稿 | 16 | 3(19%) | 105 | 74 |
| Y Adv story | 同 | 16 | 11(69%) | 79 | 74 |
| Z Std story | 生成訳 | 36 | 30(83%) | 100 | 98 |
| Z Adv story | 生成訳 | 38 | 30(79%) | 110 | 103 |
| X Adv Comment/Preview/In One Line | 生成訳 | — | 20/20、3/5、4/5 | — | — |
→ **Standard story(X/Y)は英語が日本語原本より約25〜40%多い文数**で、文単位の対応が崩れるのが構造的。生成訳(Z・Adv Comment等)は1文=1訳Promptのため文数がほぼ揃う。ユーザー認識(「英日対応が大きくずれるのは例外的」`…LINKED-HIGHLIGHT-01_USER_02.md:40`)と実態は異なる。

## 5. Prompt上の許容文言(要約・意訳・自然な日本語)
- 日本語R0〜R2(原本作成): 「友人に…話すような読み物」「R2…さらにもっとエンターテインメント性の高い記事」(`er019_family_x_ja_writer_o_r1_r2_01.py:49,70-73`)。**日本語は編集された読み物であり、逐語性は要求も設計もされていない**。
- 忠実英訳(Adv): 「as close to the original as natural English allows」「Do not add…Do not remove any fact…」(`advanced_adaptation_generate.py:522-`)。段落単位。
- Standard: 「Rebuild the sentences…Split long clauses…Do not turn the article into a summary」(`standard_a2_generate.py:506-515`)。**文の再分割を指示**。
- 生成訳(別経路): 「意味を正確に訳す。意味を変えず、情報の追加・省略をしない。平易で読みやすい自然な日本語にする」「番号1つにつき訳は1つ」(`er135_enduser_translate_01.py:41-43`)。「意訳」「要約」を許容も禁止もしていない。

## 6. 未確認
- ユーザーが問題②を見た実際の画面・クリック位置(未確認)。
- R2が台帳F11以外の事実を含むか(本件ではF11/F10周辺のみ確認)。
- Std英語とAdv英語の他段落でのR2との情報差(01Bで全件照合予定)。
