## PART2-GRAMMAR-PRODUCTION-WIRING-01 Opus独立レビュー(条件A。読み取りのみ、API 0)

### 結論
**修正後であればrunner接続に着手してよい(条件付き可)。**
- module単体の移植は忠実です。Prompt byte一致、29標本の再parseでselect_tiered一致、fail-closed、routing未登録時の停止を確認しました。
- 一方、配線設計に穴が4系統あります。日本語訳の出所の変更(D-4)/Human確定と結果の結びつけ/HR待機点が2回に分かれる問題/NG(却下)の効き方。
- 下記M-1〜M-7をDESIGN_02に反映してから配線に入ってください。Production採用の可否は判断していません。

### 必須修正(M)
**M-1 D-4(T1訳をStep Bへ常時渡し、画面にはT1訳を表示)をTrial-07どおりに戻す(論点1)**
- 問題: 承認済みのTrial-07では、画面の【日本語訳】はStep B自身の訳です(`OUTPUT_07_melos_r1_USER.md`)。参考訳(ref_ja)を渡すのは、Part 1で訳済みの英文と一致したときだけでした(`run_trial_07.py:161-163`)。module側は常にT1訳を1 call生成し、`render_markdown`/`render_html_block`は`EXPLANATION_HEADINGS[1:]`でStep Bの訳を捨て、T1訳を表示する(`er120:941-962`)。これは安全のための修正ではなく、画面に出る訳の出所の変更です。ユーザーが承認したT1方式はPart 1に限った決定です。
- 具体案: Trialの規則をそのまま移植します。ref_jaは`ref_ja_pool`(Part 1のT1訳)に一致したときだけ渡す/画面にはStep Bの【日本語訳】を表示する/pool一致のない場合はT1 callを行わない。効果: Trial同一になり、約0.03〜0.08円/セットと1 callが減ります。

**M-2 `require_fresh_part2`をHuman確定・候補docに結びつける(論点2/4/5)**
- 現状の検査は、本文sha・抽出署名・単一span・解説が空でないこと・候補IDの自己整合だけです。`explain_signature`は再計算していません(`er120:897-901`)。事後レビューでTOP1をTOP2へ変えた後や、reselect・omit後も、古い`auto_top1`の結果が全入口を通過します。ZEROも本文sha一致だけで通ります。
- 具体案: 引数に`candidates_doc`と`grammar_review`(er119の確定)を追加し、(i)確定statusが{REVIEWED, UNREVIEWED_AUTO_ADOPTED}に含まれる (ii)`result.candidates_sha256`が現在の候補docと一致 (iii)`result.selection.candidate_id`が確定のchoiceに対応する候補と一致(omitならZERO/human_omit、0件ならZERO/no_candidate) (iv)候補docの材料欄で`explain_signature`を再計算して一致 (v)確定の`selection_signature`を再計算して一致。呼出点: Z=`load_level_inputs`(b1bのみ)・`stage_pages`・`stage_page_verify`、X=`tts`/`assemble`/`player`入口と公開ページbuilder。

**M-3 HRの待機点をKP HRと1回にまとめる(論点2/3、Delivery)**
- X案「scaffold b1b内・KP PASS後」では、KP確定後に文法候補を抽出しもう一度rc=4で待つことになり、人の待機が2回になります。
- 具体案: Part 2はKPに依存しないので2段に分けます。候補抽出(Step A'')は本文確定直後、KP候補生成と同じ待機点の**前**に実行/KPのpendingと文法のpendingを1つの`*_review_request.md`/rc=4にまとめる/選定確定・訳・Step Bは再開後に実行。Zでは2つのensure_stage: `part2_cand_b1b`(input=本文sha+label)と`part2_b1b`(M-4)。文法の`mode`はer119の`read_mode_declaration()`(KP M-6の失効規則含む)からだけ取得し、runner引数・hooks・環境変数から`auto`にできないことをtestで固定。

**M-4 Zのensure_stage来歴と`--regenerate-stage`の意味(論点2、KP M-3と同型)**
- `part2_b1b`のinput_shaは`sha(text_sha|label|grammar selection_signature)`。`--regenerate-stage part2_b1b`は「保存済み候補と現在の確定からの再finalize(再抽出なし)+子孫stale化」、再抽出はreselect CLIだけ。PENDINGはensure_stageが出力を書く前に専用例外で抜ける(PENDING状態の出力ファイルを作らない)。`DEPENDENTS["r2"]`へ`part2_cand_b1b`、`part2_cand_b1b`→`part2_b1b`。`ALL_STAGE_NAMES`/`--regenerate-stage`のchoices(`er026:2499`)へ両stage。copy-run: 候補は`extract_signature`一致で再利用、M-5のregistryでNGを引き継ぐ。

**M-5 NG(却下)の強度をKP HR共通核と同等にする(論点4)**
- (a) `rejected_ids`はrun内の候補docにしか残らない。registryは`family+slug+level`の共有storeへ。
- (b) 照合は candidate_id/正規化した文の一致(段落番号は見ない)/同一段落内の文字範囲の重なり・包含 の3つ。
- (c) 候補枯渇時に`select_from_candidates`が**ZERO(no_candidate)を自動確定**する(`er120:668,698-699`)のは、Humanが全候補を却下した事実を「適格なし」と誤記録し、Human判断なしに省略を確定する。枯渇時は`RESELECT_EXHAUSTED`として待機し、選択肢をomitか再抽出(上限内)にする。zero_reasonは`human_rejected_all`。
- (d) 再抽出の上限: `reselect_count≤2`(うち再抽出は最大1回)、超えたらSTOPして報告。
- (e) reselectで外れたTOP1/TOP2はNGとして記録(理由必須)。top2を選んだときのTOP1は`NOT_SELECTED`(NGではない)、区別をtestで固定。

**M-6 「未レビューを最終承認扱いしない」と「修正内容・理由の記録」の担保(論点4、ユーザー指示3.4)**
- ZERO(0件)を待たずに確定させる場合も、er119のstatusを`REVIEWED`にしない(`NO_CANDIDATE_UNREVIEWED`等の別値)。top2/reselect/omitでは`reason`必須、historyへ却下候補の文・分類・tier・tier_tableの理由と一緒に残す。`--accept-ai`はKPのR-6に合わせる(表示した`candidates_sha256`を記録)。closeout・evidenceの集計で`auto_top1`をレビュー済みに数えないことをtestで固定。

**M-7 Xの再開・失敗時に有料工程をやり直させない(論点3)**
- 通常の`scaffold`/`all`で再開するとsupport(`er019:657`)とKPが再生成される。Part 2の失敗やPENDINGで止まった後の案内は`--stage study_text`(Part 2を含むよう拡張)か専用stageの1つだけ。失敗の記録は`part2_failed.json`とrc=3。test: 再開時のsupport・KP・Step A''の呼出がすべて0。

### 推奨(R)
- R-1 描画: Part 1描画は判断記録がなければ空文字を返す(`er003:478-480`)。そのとき`include_css=False`だとCSSが欠ける。`include_css = not part1_html`。
- R-2 X公開ページ: Part 2描画は共通builder(`study_html_for_audio_dir`拡張か新設1関数)からだけ。Standardページから呼ばない静的test。
- R-3 一致検証: `verify_selection_matches_outputs`に`kind="grammar"`を実装。確定↔`part2_result.json`↔`study_text/*.md`↔公開HTML。Z `stage_page_verify`とX player末尾で実行。
- R-4 TOP2の重複除外: 同一段落内の範囲が重なる候補も除外。候補が1件のときは`review_request.choices`からtop2を外す。
- R-5 `load_level_inputs`でPart 2を確認するのはb1bだけ。
- R-6 費用ログ: Zでは`ctx.stage_context("part2_*")`でstageタグ。「KPと並列で追加時間≒0」は現行の直列runnerでは成立しないので+30〜60秒/セットに訂正。
- R-7 M-1を採る場合、pool一致の訳を`explain_signature`に含めて失効を検出できることをtestで確認。
- R-8 `ZERO_P2`文中の「このPart」は参照先がやや曖昧だが承認済み文面なので変更は任意。

### 問題なし確認(C)
- C-1 D-1(parse不能を0件にせずretry1回→STOP)は承認範囲内の安全側修正。
- C-2 D-2/D-3/D-5は承認範囲内。D-6(0件時は固定文面)は妥当。KP HR §kの「コーナーなし」側の記述を直す。
- C-3 Tier・適格条件・Prompt・逐語解決の移植は忠実。
- C-4 PENDINGで有料のStep B・訳を呼ばない、model不一致はretryせずSTOP、routing未登録はfail-closed、Trial資産をimportしない、は妥当。
- C-5 対象レベルをAdvancedのみとするのはTrial実績・Part 1前例と整合。
- C-6 Y: 未配線としOPEN-484で追跡は妥当。OPEN-484へ「Yの正式入口が`er120`、`er119 kind=grammar`、M-2の消費側検査、M-5の共有NG registryを通ること」を追記。

### ユーザー確認が必要と考える点
1. M-1で現行案(Part 2でもT1訳を表示)を残す場合のみ必要。Trial-07どおりに戻せば確認は不要(推奨)。
2. (報告で明示)Part 2をAdvancedのみとし、Standardは新仕様のため非適用とすることをcloseoutの表に明記。

### TEST_PLAN・evidenceへの追加
- 統合test(mock): M-2 事後レビューでtop2に変更した後に古い結果が全入口で拒否/M-3 KPと文法の待機がrc=4の1回/M-4 input_sha変更・再finalizeで再抽出0回/M-5 別runでのNG保持・範囲の違う引用でもNGが効く・枯渇時に自動ZEROにならない・再抽出上限/M-6 ZEROがREVIEWED扱いにならない・理由必須/M-7 再開時に有料API 0回/R-1 Part 1が空のときもCSS/Standardページに出ない。
- runtime evidence(X・Z各1 run以上): 実際のstage順でPart 2がTTS前に生成/pages・page_verifyと公開ページの一致検証(R-3)/HRなし(auto宣言)とHRあり(top2またはreselect)/rc=4からの再開でAPI 0/omitまたは0件の表示(mockで可)。copy-runの証跡だけでは弱いのでstage順序のlogを添える。
- 予算: 次委任の見積約4〜5円は妥当。

### 未確認
- Zの`a63.build_pages`がstudy_htmlをb1bページだけに入れるか/X `--stage study_text`の現行前提(KP成功必須)をKP非依存のPart 2とどう分けるか/er119の`mode_declaration`・registry・lockのI/F
