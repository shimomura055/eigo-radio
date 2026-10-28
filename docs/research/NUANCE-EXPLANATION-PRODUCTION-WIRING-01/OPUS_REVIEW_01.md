# Opus条件Aレビュー(逐語、2026-10-29、転写から機械抽出)
## Opus独立技術レビュー(条件A) NUANCE-EXPLANATION-PRODUCTION-WIRING-01 設計

### 結論
設計の骨格は妥当です。「共通module1つ+合成点1か所+既存HRへの相乗り+N2/N3はAPI 0」という方針は良く、承認仕様A〜Eとも整合しています。ただし、実装前に直すべき欠陥が10件あります。内訳は、配線位置の誤り、遡及の穴、confirm-revise時の誤STALE、Yのpage_verifyの例外落ち、既存0件runの再構築STOP、Prompt入力形が未検証、の系統です。いずれも承認範囲内で直せるもので、ユーザー判断が要る事項はありません。

### F-1〜F-6への賛否
- F-1: 賛成。文法とのハードNGを外すのは、§2-Bの範囲を超える品質基準の引き上げを避けるという意味で正しい判断です。修正対象は次のとおりです(R-1): 判定(judge)は文法Top1/Top2も評価して警告用の`grammar_conflicts`を出す、`overlap_check.verdict`とN2の送信停止はKP/Word(①②)のみ、設計§5.1/§5.3-3、U-7、H-2、H-13。
- F-2: 条件付きで賛成。自動NGの規則は「正規化した主表現とKP/Wordの句が一致」に加えて、「複数語のKP/Wordがニュアンス主表現の中に連続して丸ごと含まれる」場合も自動NGにするよう提案します(例: KP `can't be helped` ⊂ 候補 `I guess it can't be helped`)。それ以外の構造一致は段2へのヒントとして渡し、HR画面に「語の共有あり」と表示します。段2のfailは常に優先、段2のpassは自動NGでない段1ヒットに優先、で妥当です。
- F-3: 条件付きで賛成。(b)は時点が誤っています。N1はHR前に動くので、入力は「HR確定済みの文法」ではなく「提示中の文法Top1/Top2」です。(a)の具体案はR-9。さらに入力形がTrialと変わるため、M-8の再検証が必要です。
- F-4: 賛成。ただしLEGACYと新規runを分ける判定条件(N0の発行条件)に遡及の穴があります(M-2)。AUTO採用の検出もN1時点だけでなくfinalize時点に要ります(R-15)。
- F-5: 賛成。ただし確定後のbindingを`candidates_sha256`で取らないこと(M-3)と、被覆検査(M-4)が必須です。
- F-6: 賛成。ただし「1か所の変更で6経路に効く」のは描画側だけで、検証側は直す箇所が多いです(M-5、M-6、M-7)。

### 必須修正(M-)
**M-1 N1の挿入位置が誤っています。**
- 設計§11は「X: `run_part2_candidates_x`:805の隣」としていますが、この時点ではKP候補docはまだありません。
  - Xでは文法候補がKP候補生成より前に動きます(`er019_family_x_audio_production_runner_01.py:936-941`)。KP候補はその後の`run_kp_with_review`(:997)で作られます。
  - Y/Zも文法→KPの順です(`er121_family_y_runner_01.py:620-628`、`er026_family_z_fiction_production_runner_01.py:2205-2218`)。
- 修正案:
  - N1は各levelで`_kp_review_step`/`run_kp_with_review`が返った後に置きます。PENDINGのとき候補を生成し、そのpendingを既存のpendingリスト(er121:631、er026:2221、er019:1005-1009→3913-3926)へ合流させます。
  - Xの`--stage study_text`経路(er019:3940-3966)でも、pending bannerにnuanceを合流させます。

**M-2 N0の発行条件「KP確定レコードがliveでない」は遡及の穴です。**
- 既存の公開記事で、保守目的にKPをrevokeしただけで`nuance_spec`が発行され、有料生成とHR項目追加が起きます(原文§2Eの趣旨に反します)。
- 前例のdisplay_specは、新規review作成時(`er119_kp_human_review_01.py:616-628` `new_review`/`issue_std_part1_mark`)にだけ発行され、prevから継承されます(`er128_kp_confirmed_content_01.py:272-277`)。
- 修正案: nuanceも同じ契機(新規KP review作成時、reselect/STALE時はprevから継承)で発行します。KPのselection signatureには含めません(`kp_<lv>`の来歴を動かさないため)。evidence用には、reconsumeと同型の明示コマンド(by/user_ref必須、copy-run限定)を別に用意します。

**M-3 確定後のbindingに`candidates_sha256`を使うと誤STALEになります。**
- confirm-revise(訳修正)は候補docを保存し直すのでshaが変わります(er128:1792-1793)が、confirmation_idは維持されます(:1804)。
- 現設計(§5.3-1、§9)では、確定済みニュアンスがSTALEになるか、N1が再生成されて人間が見たものと別の候補になります。
- 修正案:
  - HR提示時のフォーム鮮度確認は従来どおり`candidates_sha256`で行います。
  - 確定後および候補再利用の判定は、`pool_identity_sha`(candidate_id+used_form/display_phrase/key_phrase+kind。gloss/gatesは除く)、`text_sha256`、`confirmation_id`で行います。

**M-4 N2の被覆検査が不足しています。**
- `pool_conflicts`との交差を見るだけでは、judge出力から漏れたidを人間が選んだ場合に素通りします。
- 修正案:
  - 確定した①②の全idが、N1の`against[]`(判定済み集合)に含まれることを必須にします(欠ければISSUE rc=4)。
  - judgeの`per_item`はid単位で全件を返させ、欠落・重複はJSON不正と同じ扱い(retry→`overlap_unverified`)にします。
  - verdictはLLMの`verdict`欄ではなく、`per_item`から決定論で算出します。
  - `pool_ids`はexporterの提示集合(`export_form_data_01.py:26` DEFAULT_CAP=12)と同じ関数で算出します。

**M-5 Yのpage_verifyが文法0件で例外落ちします。**
- `er121_family_y_runner_01.py:1054`の`section.index(PART2_MARKER)`は、Advanced(Part 1は常時あり)で文法が0件のとき`ValueError`を投げます。YE2EStopではないため、通常のSTOP経路を通りません。設計§7・§11にこの箇所がありません。
- 修正案: Part 1→文法→ニュアンスの順序検査を「存在するブロック同士の相対順」に一般化します。
- 同型のassertがあるtest: `er121_y_highlight_wiring_test_01.py:106-107`、`er121_family_y_runner_01_test_01.py:758-761`、`er019_x_highlight_wiring_test_01.py:371`、`er120_part2_wiring_integration_test_01.py:509`、`er003_kp_general_explanation_01_runner_integration_test_01.py:252,288-289`(文法は常に渡る前提)。

**M-6 既存0件runのページ再構築がSTOPします。**
- ZERO_P2入りの旧md(Part 2のmd)が残るrunで、ページだけ再構築します(Y `pages,page_verify`は`part2_<lv>`を再実行しない)。
- すると`verify_outputs`(`er120_part2_wiring_01.py:439-442`→`er120_part2_grammar_production_01.py:1370`)で`md_text != render_markdown(result)`(="")になり、Part2Staleで止まります。R-15/D-12が成立しません。
- 修正案: 0件結果で旧固定文面と完全一致するmdは、決定論で退避(`.legacy_zero_p2.md`、削除しない)してから検証し、検証側は「0件=md不在」を要求します。

**M-7 ニュアンスの節単位一致検証がありません。**
- 設計は件数(`count_nuance_blocks`)だけです。
- 修正案: 文法のO-6と同型に揃えます。
  - `render_html_block(nuance_result)`が当該level節に含まれることを確認(Std/Advの取り違えを検出)。
  - 期待件数(ADOPTED=1、他=0)を確認。
  - ページ非表示語の検査`PAGE_FORBIDDEN_RE`(er120 prod:1352)をニュアンス本文にも適用。

**M-8 Production形の入力でPromptが未検証です。**
- 01b v2は「HR確定済み5件」を入力し、判定も5件だけでした(`PROMPT_TRIAL_01.md:106-107,193-194`)。
- 設計は「暫定選定+pool最大12件+文法Top2」を入力・判定対象にします。文言も「選定済み」から「候補」へ変わり、F-3(a)(b)も加わります。
- 原文§3の「過去Trial Promptを無検証採用しない」に照らし、Track Bの確定前に同じ8 levelでv3を1回だけ再検証します(約1.5円。各runの`kp_candidates.json`を使う)。
- `focus_terms`はPromptに追加せず、`expression`(A vs Bを分割)から決定論で導出し、Prompt変更を最小化します。

**M-9 引用規則が文書間で不整合です。**
- v2 Promptは「1〜2文」(PROMPT_TRIAL:151)、設計§4-5は「1文以内」、TEST U-9は「複数文=技術失敗」です。実例y_advは2文でした(:538)。
- 修正案: 「本文の連続した1〜2文の逐語部分文字列」に統一します。’と'などの引用符正規化は、文法の`norm_body`と同じ規則にします。

**M-10 runtime evidenceの「TTS 0円」前提に条件が要ります。**
- Y/Zには`kp_<lv>`→`tts`の来歴があります(er121:53)。copy-runでKPを別の選択で再確定するとTTSがstaleになります。
- KP候補を作り直す方式も使えません。reviewだけを消すと`KpReviewInconsistent`(er119:1391)になり、候補が変わればTTSの再生成になります。
- 修正案: revokeした後、元runと同一の①②③選択で再確定します(D1 rebind、er121:594-611でAPI 0)。これを手順に明記します。

### 推奨(R-)
- R-1: F-1を設計に反映する(上記)。F-1のもとでは文法の重複は警告だけになるので、`--grammar-pending`とニュアンス確定の結合(§6、H-13)は外して経路を1本減らせます。
- R-2: F-2の規則を具体化する(上記)。
- R-3: ニュアンスのfinalize(LLM 0、冪等)は`stage_kp`だけでなく、ページ構築の入口(X player/公開ページ、Y/Zのpages)でも実行する。CLIの`nuance-select`をstage_kpの後に行った場合や、Zの完成段だけの再起動を救えます。ニュアンス側の`require_final`はページ入口だけに置き、tts/assembleには入れない(音声がないためTTS前に止める必要はない、というFableの理解は正しいです)。
- R-4: N3の`SUPPRESSED`(自動で非表示)は廃止し、ISSUE rc=4に変える。確定後にKP集合が変わるのはrevoke経由だけで、その場合はconfirmation_idが変わって再判断になるため、ほぼ到達しません。到達した場合も人間の採用を自動で覆さない方が、仕様BもDも破らずに済みます。
- R-5: `FAILED_TECHNICAL`はHR画面・依頼書に「候補なし(技術失敗)」として、本物の0件と区別して表示する。HR送信前の再試行コマンドを案内する。自動の再試行はHR前のresumeで1回までにする。
- R-6: `compose_page_html`ではnuanceを既定値なしの必須keywordにする。渡し漏れによる黙った欠落を構造で防げます。旧testのため`compose_study_html`側の`None`既定は残してよいです。
- R-7: Y/ZのDEPENDENTSに`part2_cand_<lv>`→`nuance_cand_<lv>`を追加するか、文法候補docのshaをbasisに記録する(警告の鮮度のため)。
- R-8: 生成と判定が同じモデルである点は、別Promptを使い、生成側の`differs_from_kp_word_ja`/`criteria_check`を渡さない前提なら、gpt-6-lunaのままで可とします。判定Promptには入れ替えテストと「最も焦点が近い項目の明示」を追加します。runtime evidenceでは固定の検査用プローブ5〜6件(Part 1の類義語比較型、文法と同じ焦点、非重複)も実行します(約0.2円)。
- R-9: F-3(a)。Standard(A2)に「A2基礎文法の対比は不可」をレベル理由で課すと過剰抑制になります(at leastの見逃し)。除外理由を「文法コーナーの領域」に置き換え、「機能語・頻出表現の語用的な含みはStdでも可」「助動詞や構文を含む表現でも、焦点が仕組みでなく語用(誇張・婉曲・確信度)なら可」と明記します(You should have seenのStd/Adv割れへの対策)。自己評価`mid`の候補は決定論で0件にします。
- R-10: 費用。Production入力(判定対象約14件)では判定の出力が約2.5倍になる見込みで、全体は約0.40〜0.50円/記事セットです(70円の1%未満。原則7-7の範囲内でユーザー承認は不要ですが、報告はします)。判定出力は「id→bool、trueの項目だけ理由」の圧縮形にします。記事原価の集計にニュアンスのprocessを含め、YのSTAGE_EST(er121:35)に見積を追加します。
- R-11: revoke後に再確定するときは、旧採否をフォームの既定として表示する(明示送信は必須のまま)。
- R-12: 見出しの「Deeper Understanding」は旧Part 3の範囲を連想させます。軽微なのでFableの判断でよいです。
- R-13: R-G3のGrep対象は「Production module」に限定する。既存Production testがbyte固定のためrun_trial_04を参照しています(`er003_kp_general_explanation_01_test_01.py:71`、`er120_part2_grammar_production_01_test_01.py:108`)。後者のZERO_P2一致assertは削除します。
- R-14: 公開済みの0件ページ(`user_test/family_x_ai_island_form_01/index.html`など、ZERO_P2文面を含むHTMLが計15ファイル)は非遡及なので残ります。最終報告にその旨を現状として明記します(ユーザー判断事項ではありません)。
- R-15: TEST_PLANに次を追加する。
  - M-3、M-5、M-6、M-7、M-9、M-10の各回帰test。
  - N1の後に不在宣言(AUTO)が入った場合は`NONE`になる。
  - ③の選択はブロック対象外。
  - judgeの`per_item`欠落→`overlap_unverified`。
  - 0件の自己評価`mid`→0件。
- R-16: 「正式Production経路」と言える条件を§7に定義する。
  - runnerのmainから`--mode real`で実行し、hooksは注入しない。`routing.require_model`経由。N0はrunner内で発行(手置き禁止。evidence用の明示コマンドは除く)。
  - フォームはexporter→V3の`form_logic.js`(node)でreadableを生成→`confirm --from-readable`。ページはrunnerのpage stageで作る。
  - 判定はHTML実物とAPIのusage・modelで行う。
  - 自動のN0分岐は、少なくとも1 Familyの初回経路でstudy_textまで実機確認し、表示はrevoke経路のcopy-runで確認する、という分担を提案します。

### 妥当(OK-)
- OK-1: 単一の合成点(er120_part2_wiring:507→er120 prod:1449)の拡張、CSSの「最初の非空ブロックが持つ」への一般化、3ブロックとも空なら空文字。
- OK-2: 既存`cmd_from_form`への相乗り。書込み順はニュアンスsidecarを文法sidecarの直後に入れ、commit点(er128:1488)は不変。AIF2、`nuance_spec`なしはAIF1でバイト不変、fail-closedの復元、未回答=ISSUE(黙って不採用にしない)。
- OK-3: ユーザーがpool外を選ぶ経路はありません。候補doc外のidは拒否され(er128:1436-1439)、自由入力もありません。補完候補(Gate除外の代替)も同じ候補doc内にあります(`export_form_data_01.py:72-73`)。M-4を満たせば、N2のAPI 0による最終確認で仕様§2-Bを満たします。確定後に重複が見つかった場合の「非表示・自動補充なし」はA-7と整合しますが、R-4のISSUE化の方が安全です。
- OK-4: fail-closedの設計。技術失敗は非ブロッキング、model契約違反・予算・STOPはSTOP。制作全体を止めない設計で、TTS前の停止は不要です。
- OK-5: F-4。AUTO採用runではニュアンスを不採用(0件)とする。
- OK-6: §9の大部分(候補なしなら判定callを省く、確定後は`CONFIRMED_CONTENT_LOCKED`、退避して削除しない、`kp_dir_rel`)。
- OK-7: 01bの学習価値。at least(Adv)、You should have seen、was linked to は十分な水準です。I guess it can't be helped(y_adv)はKP級の句ですが同level内では非重複で、HRに委ねてよいです。

### 確認できていない範囲
`form_logic.js`の`makeCode`/`k4`の算式、`er119_kp_wiring_01.write_unified_request`、`stale_or_rebind`の内部、Zのtest群は読んでいません。M-5の同型assertは上記のGrep範囲以外にもある可能性があり、Track Aの着手時に再Grepが必要です。

主な参照ファイル:
- C:\Users\tensh\eigo-radio\docs\research\NUANCE-EXPLANATION-PRODUCTION-WIRING-01\WIRING_DESIGN_01.md
- C:\Users\tensh\eigo-radio\docs\research\NUANCE-EXPLANATION-PRODUCTION-WIRING-01\TEST_PLAN_01.md
- C:\Users\tensh\eigo-radio\er121_family_y_runner_01.py(:1054)
- C:\Users\tensh\eigo-radio\er019_family_x_audio_production_runner_01.py(:936-1009, :3940-3966)
- C:\Users\tensh\eigo-radio\er128_kp_confirmed_content_01.py(:272-277, :1792-1804)
- C:\Users\tensh\eigo-radio\er120_part2_wiring_01.py(:432-458)
