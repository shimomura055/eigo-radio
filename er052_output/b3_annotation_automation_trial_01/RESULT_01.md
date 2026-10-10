# RESULT_01: B3-ANNOTATION-AUTOMATION-TRIAL-01 Phase 2(2026-10-10、MEASURED、Production変更なし)

方式 = B3 -> LLM注記1回 -> 既存の機械検査 -> 保存(A/B二重化・統合・Union・自動Correction不使用)。10入力x2反復x2モデル=40 call実行(未実行・中断なし)。実費 **JPY350.08**(見積 低217/中530/高973の範囲内、ガードJPY1,200未到達)。
**重要**: 「機械検査PASS」は形式(本文非改変/番号形式/境界/タグ形式/必須タグ)の合格であり、意味的に正しい注記であることの保証ではない。GT(旧Trialの同一Sonnet系2回出力の決定論統合)は人間正解ではないので、GT一致の数字は参考値。

## 使用モデル(25節)
| 用途 | model_id(応答値) | 最新か | 備考 |
|---|---|---|---|
| Sonnet系 | claude-sonnet-5-5(応答値同一) | 最新(models list、2026-09-28作成) | Trial worker名と同一。代替なし。価格 in$2/out$10(公式ページ取得 2026-10-10) |
| Luna | gpt-6-luna(応答値同一) | Production routing上の正式model_id | 本番ラインの現行モデルで評価。Astra/Sol/Haiku等は追加せず |
Provider既定(temperature等は未指定、旧Trialはsubagent実行でAPIパラメータ記録なし)。Anthropicは max_tokens=16000 のみ指定(必須)、OpenAIは reasoning.effort=medium / max_output_tokens=16000(Phase 1のdry-run payloadと同一)。

## 1. 非エンジニア向け8点
1. **どちらが良かったか**: 品質は **Sonnet 5.5が明確に上**。機械検査PASS 16/18(失敗2件はいずれも出力打切り=後述)、危険な誤注記ゼロ、2回の結果がほぼ一致。Lunaは PASS 10/18、検査FAIL4・書式FAIL3・STOP1、2回の結果が揺れた。ただし費用は Luna が約40分の1。
2. **1回注記+機械検査で十分そうか**: Sonnet 5.5では「十分そう」(打切り対策が前提)。Sonnet 16/16(打切りを除く全出力)で検査PASS、PASS出力に意味上危険な誤りは見つからず(Claude側で全件を原文と照合)。Lunaは1回では足りない(FAIL/STOP 8/18)。ただし検査は誤りをよく止めており、LunaのFAIL出力4件はいずれも検査で捕捉された。
3. **危険な誤注記はあったか**: あった(Luna)。5件(事実でないものの【事実】化2、中核数値の落ち2、文の途中での事実分割1)。**うち4件は既存検査が捕捉。1件(指示文を単独の【事実】にして台帳に紐付けた、semiconductor Luna rep1)は検査の検出対象外**(その出力は別理由でFAILしたため採用されず)。Sonnetの採用可能出力(PASS 16)に危険な差分は0。Sonnetの非採用出力(central_bank 2回)に「0.25ポイントが周辺扱い」(中核の落ち)が2件。**加えて全モデル・GT共通の構造問題**: B3の事実欄に混在する指示文(「〜を付け加えないこと」等)は、どのモデルも分離できず【事実】の中に入ったまま(HUMAN_CHECK H-1)。注記方式では解決せず、B3出力の構造の問題。
4. **再現性**: Sonnet 5.5は高い(比較可能8組中、注記版が完全一致7組、残り1組(openai_copyright)もタグ位置のズレ6箇所のみで台帳対応・境界は同じ。1組は台帳ID付与のみ差)。Lunaは低い(比較可能6組中、完全一致2組、差分4〜5箇所が4組)。Lunaは同一入力でSTOP/書式崩れ/検査FAILと成功が混ざる。
5. **Sonnet/Luna 記事単価(実測)**: Sonnet 5.5 **約JPY15.7/記事**(正式9テーマ平均、PASS出力平均JPY14.0。既定のthinkingが出力トークンを多く消費(打切りを除く最大11,257 tokens)するため)。Luna **約JPY0.39/記事**(PASS平均JPY0.33)。約40倍の差。失敗分を含めた「PASS1件あたり総支出」は Sonnet JPY21.4 / Luna JPY0.81。
6. **A/B二重化が本当に必要か**: Sonnet 5.5には**不要と考える**(1回注記の誤りが採用可能出力にはなく、揺れも小さい=再検討条件に非該当)。Lunaは再検討条件(大きな揺れ・危険誤注記複数)に該当するが、検査がほぼ捕捉しており、Luna単独にA/B二重化を足すより、(a)Sonnet 5.5の1回注記を使う (b)別Trialで「Luna+既存retry上限内の再生成」を検証する、のどちらかが筋(未実施・提案のみ。今回は再実行・合成を一切していない)。
7. **Production候補としての推奨(採用判断はしない)**: B3注記の自動化は **Sonnet 5.5(1回注記+既存検査)を第一候補**。条件: ①出力上限(max_tokens)を打切りが起きない値へ見直す(現状16,000で正式9テーマ中1テーマ=central_bankが2回とも打切り、費用も大きい) ②**B3側で指示文を事実欄から分離する構造改善**(別仕様、未決) ③PASS後の意味確認の運用(形式PASSは意味保証ではない)。Lunaは現状の1回注記では推奨しない。QCD上は「Luna約JPY0.4で最大PASS率56%」対「Sonnet約JPY15で89〜100%」。
8. **USER_DECISION_REQUIRED事項**: (a)Sonnetの打切り4 call(central_bank/inbound各2)の扱い: 再実行(上限引上げ、予想約JPY120)するか、打切りを結果として確定するか(今回は結果を見た再実行になるため実施せず) (b)指示文の事実欄混在(H-1)をB3側の仕様改善として別Trial化するか (c)Lunaの書式FAIL3件は終端マーカーの空白欠落1文字(`=== SIDECAR_JSON_END===`)のみで、寛容に読めば space_weapons 2件はPASS(補足分析、採用外)。パーサの寛容化は仕様変更のため提案のみ (d)Production採用判断(採用は人間のみ)。

## 2. QCD対比表(正式9テーマ x 2反復=18 call/モデル、inbound_tourismストレス入力は別掲)
| 指標 | Sonnet 5.5 | Luna | 備考 |
|---|---|---|---|
| Cost/記事(実測平均) | JPY15.69(PASS出力 14.0) | JPY0.386(PASS出力 0.33) | 約40倍。PASS1件あたり総支出 21.4 / 0.81 |
| Latency平均 | 51s | 37s | |
| 機械検査PASS | 16/18(88.9%) | 10/18(55.6%) | Sonnetの2失敗=max_tokens打切り。打切りを除くと16/16 |
| 失敗内訳 | 書式FAIL2(打切り) | 検査FAIL4、書式FAIL3(終端マーカー)、STOP1 | |
| 本文非改変(出力のあった分) | 16/16 | 14/14(正式9。inbound r2は改変でFAIL) | |
| GT比較 事実境界F1 | 1.00 | 0.82(PASS出力のみ0.84) | Lunaは事実を細かく分割する(byd 4 vs 1等)。細かい分割=誤りとは限らない。FPの多くは過分割 |
| GT比較 中核F1 / 周辺F1 | 0.94 / 0.96 | 0.84 / 0.84(PASS出力のみ0.91 / 0.94) | |
| 位置一致した印の中核/周辺分類一致 | 1.00 | 0.97 | |
| Fact ID(台帳紐付け)一致 | 0.81 | 0.63(PASS出力のみ0.70) | GT自体が同系列の出力のため差は参考 |
| 反復一致(注記版完全一致) | 7/8組 | 2/6組 | 比較は両反復に出力のある組のみ |
| 反復差分箇所数(合計) | 7(うち6は1テーマのタグ位置ズレ) | 18 | |
| Fact/指示分離の誤り(Storyline行・指示文の事実化) | 0 | 2(openai r1=検査で捕捉、semiconductor r1=検査対象外) | 事実欄内の指示文混在はGT含め全員共通(H-1) |
| 意味上危険な差分(件) | 採用可能出力 0 / 非採用(打切り)2 | 5(検査捕捉4、非捕捉1) | 件数の定義は下記3節 |
inbound_tourism(ストレス、指標外): Luna r1=FAIL(c)、r2=FAIL(a:本文に「2025年」を挿入=本文改変、検査が捕捉)。Sonnet 2回とも打切り(thinking 15,936 tokens)。
**価値判断材料**: Sonnet 5.5はLunaより約JPY15/記事高く、その対価として PASS率+33pt、危険誤注記の0化、揺れの大幅減が得られる。注記は1記事1回の作業でありFact Lock Writer・Fact Check下流の誤りコスト/人手確認コストを考えると、JPY15/記事の差は小さいと評価できる(判断はPM/ユーザー)。

## 3. 内容分析の要約(Claude側が全40出力のうち出力の存在する全件をB3原文・台帳・GTと照合)
- (a)Fact/指示分離: Storyline行は Sonnet全て正しく無印。Lunaは openai r1 で事実化(検査で捕捉)。事実欄内の指示文は全モデル・GT共通で事実に内包(H-1)。Luna semiconductor r1 は指示文を独立【事実6】にし台帳F1に紐付け(H-2)。
- (b)Fact境界: Sonnetは常にGTと同境界(粗い=段落全体で1事実が多い。bydは1事実、openaiは1事実)。Lunaは文単位に細分化(byd 4〜5、streaming 5、openai 3〜4)。細分化は多くは妥当だが、byd r1は文の途中で分割(H-4)。事実が粗いほど数値とその文脈が同じFactに残る(Fact Lock上は安全側)。細かいほど台帳との対応が細かくなる反面、断片化リスク。どちらが望ましいかは仕様判断(未決)。
- (c)中核/周辺: Sonnet 2反復で同じ判断(再現的)。Sonnetの判断が割れるのは「0.25ポイント」(周辺)と「2026年2月【周辺】下旬」でのタグ位置。Lunaは上限3の扱いが不安定(central r2、semiconductor r1)。
- (d)本文書換え: 採用出力で0。LunaのFAIL出力 inbound r2 に本文挿入(検査で捕捉)。
- (e)癖: Luna=事実を細かく割る・終端マーカーの空白欠落・STOP判断が揺れる(semiconductor)。Sonnet=thinkingが長く(最大15,936 tokens)入力により打切り。中核/周辺は安定。
- (f)揺れの内容: Luna=過分割の有無(byd/openai/streaming)、タグ位置(午前を含むか)、中核/周辺3箇所、ledger ID 1箇所。Sonnet=openaiのタグ位置ズレのみ。
- (g)Sonnet vs Luna: 上記。同一反復どうしの比較は eval_results_01.json の `cross`。
- (h)危険の定義と件数: 「事実でないものの【事実】化」「Fact境界の誤りで数値が別Factに紐づく/断片化」「中核数値の落ち」「本文改変」。Luna 5件(openai r1 Storyline事実化[検査捕捉]、semiconductor r1 指示文事実化[非捕捉]+348億ドル中核落ち[捕捉]、central r2 7.40％中核落ち[捕捉]、byd r1 文途中分割[捕捉])。Sonnet採用可能出力 0、非採用(打切り)2(central 0.25ポイント周辺扱い、GT比較で他は一致)。

## 4. Prompt起因の問題(Trial結果と分離)
- 実プロンプト末尾の運用明確化(b)に **hormuz固有例(「約25時間後」)** を含む(Phase 1で確認)。今回は逐語使用のため改変せず、結果への影響は分離できない(Hormuzの結果は両モデルとも良好、他テーマに悪影響を示す所見は無し)。Productionでは仕様本体へ取り込むv2.1が必要=仕様変更。
- プロンプトは終端マーカーを `=== SIDECAR_JSON_END ===` と明示しており、Lunaの1文字欠落はモデルの遵守ミス(プロンプトの曖昧さではない)。
- 事実欄内の指示文混在はB3入力側の構造であり、注記プロンプトで解決できない(プロンプトも本文非改変を要求)。
- 結果を見たプロンプト修正は実施していない。

## 5. 限界
GTは同系列モデルの出力であり、Sonnet側の一致は過大に出うる。正式9テーマx2反復の小サンプル。briefは短い(353〜772字)。Sonnet打切り2テーマ(正式1+ストレス1)はこの入力長で既定thinkingが長くなる性質が出た可能性。複数回の独立反復は再現性測定用で合成していない。

## 6. Status提案: USER_DECISION_REQUIRED(VALIDATEDでもAPPROVED_FOR_PRODUCTIONではない)
根拠: 事前登録の VALIDATED候補条件(採用候補モデルで高PASS率・危険少数・安定)にSonnet 5.5は概ね合致するが、(1)正式9テーマの1テーマが2回打切りで未評価(結果を見た再実行になるため確定させていない) (2)事実欄の指示文混在というB3構造問題が未解決 (3)GTが同系列で外部妥当性が弱い、の3点が残る。Luna単独はREJECTEDに近いが、検査が誤りを止める性質から「Luna+再生成」は未検証の選択肢として残る(未実行)。

## 7. 保存先
runs/{luna,sonnet55}/<theme>/rep<n>/(request.json, response_raw.json, reply.txt, annotated.md, annotation.json, check.json)。cost_ledger_annot_01.jsonl、eval_results_01.json、eval_summary_01.json、HUMAN_CHECK_ANNOT_01.md、PREREGISTRATION_02.md、analysis/luna_format_fail_lenient_supplement.json、eval_all.py、view.py。
