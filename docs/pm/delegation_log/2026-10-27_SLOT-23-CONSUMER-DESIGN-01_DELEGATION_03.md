## 管理ID

SLOT-23-CONSUMER-DESIGN-01 委任_03(Opus条件Aレビュー結果(M1〜M14/R1〜R8/N1〜N3)の逐語保存と、設計正本への反映=`DESIGN_03.md`/`IMPL_PLAN_03.md`(DESIGN_02/IMPL_PLAN_02を置換)。Fable採否(下記)を反映。read-only(Productionコード編集禁止)、API 0)。並行Agent: A班(委任_04A: `er_learning_highlight_01.py`新設+オフライン解決器実行)、B班(委任_04B: `er003`level化+`er128`マーク/reconsume/G1)。あなたの所有=`docs/research/SLOT-23-CONSUMER-DESIGN-01/{DESIGN_03,IMPL_PLAN_03,CONTRACT_03}.md`、`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_OPUS_RESULT_02.md`(末尾「## Opus結果(逐語)」以下を一字一句保存)、`..._DELEGATION_03.md`(+check.json)、`docs/pm/RESULT_PACKET_S23D3.md`(gitignore)。SSOT編集権なし。pathspec付きcommit、`git push origin HEAD:main`。時間見込み約1h。

## Fable採否(反映すること)

- M1〜M14: 全採用。R1〜R8: 全採用(R6のworktree分離は不要=GPG05Cは完了済み。`audio_review_player`CSSはC班所有に割当)。
- M3の規則(表示範囲=Full Story本文、特定出現が範囲外なら`occurrence_sentence_ids`を番号順に並べ直し範囲内最初の出現を装飾+NOTICE `HL_OCCURRENCE_RELOCATED`、範囲内0件=③は訳リストのみ+NOTICE/①②はISSUE)=Fable採用(分類B、ユーザー報告に明記)。
- M7: Std Part 1=①+②(Adv同型、KP⊂vocab)=Fable採用、根拠(USER.md:18,20,95,97)を明文化。
- M9: reconsumeで確定Redundancy QA(LLM、少額)が走ることを明記し「選定不変(ユーザー選定は変えない)・QAのみ実行」に訂正。NG時=`reconfirm_required`→ユーザー選び直し(手順明記)。
- M10: 表示有効化はflag非経由、G3ハイライト検査はkill switch意味に従う。
- M14: マーク発行(`new_review`/`display_spec`導出)はA〜E配線+Validator完了後の最後の1commit(F班の直前)。
- 解説言語: ユーザー確認中。作業仮定=A(日本語解説、Adv同型、難易度調整のみ)。B(英語本文)になった場合の差分(N1)を付録に。
- CONTRACT_03.md: A/B/C/D/E/F班の境界契約を1ファイルに(型`DisplayUnit={key,texts[],joiner}`、highlight dict `{candidate_id,kind,surface,unit_key,start,end,gloss_short,used_form}`、原因コード一覧`HL_*`、Family別アダプタが渡す「候補生成に使った本文」+`text_sha256`必須、`data-hl`属性、G1不変条件、`display_spec`継承規則、遅延import、所有ファイル表)。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。

## 報告

`RESULT_PACKET_S23D3.md`: (0)T-0・Opus逐語保存、(1)DESIGN_03変更点(M/R別)、(2)CONTRACT_03要点、(3)IMPL_PLAN_03(班別所有・順序・M14)、(4)判断候補、(5)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。commit message: `SLOT-23-CONSUMER-DESIGN-01 委任_03: Opus条件A所見(M1-14/R1-8)を反映した設計正本DESIGN_03・班間契約CONTRACT_03・実装計画03+Opus結果逐語保存(read-only、API 0)`。

## Opus結果(逐語)

## SLOT-23-CONSUMER-DESIGN-01 Opus条件A独立レビュー結果(DESIGN_02/SPEC_CONFLICT_02/IMPL_PLAN_02/COST_02)

結論は**条件付きで実装着手可**です。設計の骨格は妥当です(Part 1生成工程のlevel引数化、二重下線のCSS、マークによる遡及なし、描画1関数への集約)。ただし実装前に直すべき所見が14件あります。うち3件(M1〜M3)は、このまま実装するとAI島Standardのページ生成が誤って止まる(誤STOP)ことを実データで確認しました。read-only・API 0・編集0。

### 論点別の判定
| # | 論点 | 判定 |
|---|---|---|
| 1 | 照合の正確性 | 修正要(M1〜M4、R5) |
| 2 | 多重出現・fail-closed境界 | 修正要(M3)。「特定した1出現のみ装飾」自体は妥当(KP音声・Part 1引用文と同じ出現になる) |
| 3 | 重なり | 修正要(R1) |
| 4 | Std level化でAdvが変わらないか | 方式はPASS、配線漏れで修正要(M6)。Head差分は「難易度調整のみ」の範囲内 |
| 5 | 「英語解説」の解釈 | PASS(日本語の解説文が最も忠実。N1)。ただし対象件数の扱いでM7 |
| 6 | 旧経路撤去の網羅性 | 修正要(M8、M11、M13、R4) |
| 7 | KCP整合 | 修正要(M8〜M10、R3) |
| 8 | X/Y/Z差異 | 修正要(M3、M4、M13) |
| 9 | 既存ページ回帰 | X playerのみ修正要(M13)、他はPASS |
| 10 | 表示 | 軽微な修正要(M12、R8) |
| 11 | 費用 | PASS(N2) |
| 12 | 並列分割 | 修正要(M14、R6) |

### M=実装前必須
**M1 照合に使う本文の取得元が違う**(DESIGN_02 §B-3)
- 問題: 照合本文を`<run>/<lv>/article.md`としていますが、Xのrun dirにarticle.mdはありません(実体は`{source_dir}/{lv}/article.md`、`er019_family_x_audio_production_runner_01.py:230`)。Zは`canonical_article_text(...)`で変換した本文で候補を作っています(`er026_family_z_fiction_production_runner_01.py:2092`)。
- 修正: Family別アダプタが「候補生成に使った本文」を渡し、`sha256_text(text) == cands["text_sha256"]`(`er119_kp_human_review_01.py:1353,1406`)を必須にする。不一致は新原因コード`HL_TEXT_SHA_MISMATCH`でISSUE。
- 影響: A班、C/D/E班の契約。

**M2 文の一致を「完全一致」で比べると誤STOPする**(§B-3 手順1)
- 問題: 候補docの`source_sentence`は引用符が直線引用符に正規化されています(`er128_kp_confirmed_content_01.py:661`)。AI島a2の実例は`kp_candidates.json:864`の`"Strategy Notes`(直線)に対し、`parts.json:3`の表示は曲線引用符です。`units[i].raw_text == source_sentence`の完全一致では偽の`HL_SENTENCE_MISMATCH`が出ます。
- 修正: 既存の`_norm_ws`(`er128…:660`)で比較する。

**M3 AI島Standardの③`Strategy`で、現設計はページ生成前にSTOPする**(§B-3 手順3〜4)
- 問題:
  - `Strategy`の特定出現S2は、本文ではなくタイトルの断片`But AI Has "Strategy Notes`です(`a2/key_phrases/kp_candidates.json:860-907`)。
  - タイトルはFull Story本文に含まれず、Topic intro行に出るだけです(`er019…:2938-2940`)。
  - したがって`HL_SENTENCE_NOT_IN_DISPLAY`でSTOPします。設計の「S2で1箇所に特定可」は、表示範囲に入っているかを確認していません。
  - さらに`occurrence_sentence_ids`は文字列順に並んでいます(`["S2","S34","S8"]`、`er105_kp_fulltext_selector_01.py:274`)。
- 修正:
  - 表示範囲=Full Story本文と明記する。
  - 特定出現が範囲外なら、`occurrence_sentence_ids`を**番号順**に並べ直し、範囲内で最初の出現を装飾する(NOTICE `HL_OCCURRENCE_RELOCATED`、停止しない)。
  - 範囲内に1つも無い場合: ③は訳リストのみ+NOTICE、①②はISSUE。
  - この規則は承認範囲内の表示詳細(分類B)なのでFable判断で決められます。
- 影響: 受入条件5、AI島ページ。

**M4 本文→表示への写像が脆い**(§B-3 手順4)
- 問題: 文ごとに独立に部分一致検索すると、短い文が先行する別の文に誤ってヒットし得ます。Zのクリップ台本は句読点・引用符が本文と異なる可能性もあります。
- 修正:
  1. 本文の全文を表示テキスト列へ**先頭から順に**対応付ける(カーソルを進める単調整列)。
  2. 対応した表示文の中で`_phrase_pattern(source_span)`を直接適用し、最初の一致を取る(オフセット表は不要になる)。
  3. highlight dictに`surface`を持たせ、描画時に`text[start:end]`と一致するかassertする。
  4. 配線前に、既存の確定済みX/Y/Z run全件で解決器をオフライン実行し(API 0)、ISSUE率を計測する。これが「過剰制約で制作を止めない」の実証になります。

**M6 入力隔離チェックがlevelに対応していない**(DESIGN_02 §A-2)
- 問題: `_variable_part`(`er003_kp_general_explanation_01.py:150-161`)と`check_prompt_isolation`(:182-200)が`PROMPT_HEAD`を直書きしています。auditの`prompt_template_sha256`(:310)とsignatureのpayload(:207)も同様です。このままだとStdは常に`KpIsolationViolation`で止まり、検査を弱める誘因になります。
- 修正:
  - levelを次の関数すべてに通す: `_variable_part`、`check_prompt_isolation`、`generate_general_explanations`、`generate_for_kp_items`、`resolve_*`、`require_fresh_*`、`assemble_part1`(:377)、`study_html_for_audio_dir`(:523)。
  - a2のpayloadは`PROMPT_TEMPLATE_SHA256_A2`+`level`を使う。
  - b1bのgolden(Prompt・sha・signature・HTML)とa2のshaを両方testで固定する。
- 補足: levelを渡し忘れてもSTALE STOPになる(fail-closed)ので安全側ではあります。

**M7 Std Part 1の対象件数が無言で決められている**(§A-1)
- 問題: 設計はStd Part 1=①3+②2=5件と決めています。一方USER.mdは:15で「②で選定された…」、:27で「①は勝手に表示対象を変えない」と書いています。①+②を支持する根拠は:18「Adv同等」、:20「Part 1相当」、:95「項目構成は踏襲」です。
- 推奨: ①+②(Advの既存構造KP⊂vocab=`er119:527-530`に一致し、②だけにすると新しい方式になり:97に反する)。
- 対応: 解釈と根拠を明文化し、ユーザー報告の3項目めに明記する。Fableが「英語で」を確認中なら同時に確認してもよい。

**M8 マーク(`std_part1`/`display_spec`)の一貫性が守られていない**
- 問題:
  - review側の`std_part1`は`selection_signature`の対象外です(`er119:583-591`)。消えても検知されず、黙って旧経路に戻ります。
  - 「`_new_record`で常に付与」は危険です。`_new_record`は`cmd_revise`(`er128:1715`)、`--adopt-existing`(:1651)、自動更新(:578,585)でも旧runに対して呼ばれるため、旧runに遡及してしまいます。継承しない実装なら、訳の修正(revise)でハイライトが消えます。
- 修正:
  - 前レコードがあれば`display_spec`を継承する。新規時はreviewの`std_part1`から導出する(付与は`new_review`の1箇所だけ)。
  - `std_part1`は存在するときだけ署名に含める(旧署名は不変)。
  - G1に不変条件を追加する:
    - a2では`display_spec`と`std_part1`が一致すること。
    - `display_spec`付きなら`STD_CATEGORY2_NO_SLOT`が0件であること。

**M9 `reconsume`(AI島の明示移行)の設計を修正する**(§F)
- 問題と修正(既存の`cmd_revise`型に合わせる):
  - `confirmation_id`を保持する。保持しないと文法sidecarの照合(`er128:441`)で整合性違反になります(AI島a2には`confirmed_grammar.json`があります)。
  - `origin`(form_submission)を保持する。`_form_source_problems`(:446-455)が効かなくなるのを防ぐためです。
  - Stdはreviewの`selection.vocab`と`std_part1`をreview_lock下で更新し、`validate_selection`(`er119:505-552`)を通す。NGなら移行せずISSUE。
  - `vocab_confirmed.json`の書込みは`finalize_kp`だけが行う(単一writer、`er119:1044-1048`)。reconsumeでは退避+`_try_refinalize`のみ。
- 訂正が必要な点: 「選定不変・API 0」は成立しません。Std vocab集合の確定Redundancy QA(LLM、`er119:937-963`)が次回起動時に必ず走ります。NGなら`reconfirm_required`になり、ユーザーの選び直しが必要です。
- 追加test: 署名変化に対し、Z(`er026:2055-2072,2106`)/Y(`er121:595-603`)/XでAPI 0の再バインドが働き、TTS・音声shaが不変であること。

**M10 「環境変数で迂回不能」は事実と違う**(§F/§G、IMPL §5(c))
- 問題: 既存のkill switch `EIGO_KP_CONFIRMED_PROTECTION=0`(`er128:87-89`)で、`verify_outputs`(:769)、`verify_items_against_record`(:1216)、`live_user_record`(:217)が無効になります。
- 修正: 表示の有効化判断はflagを経由せず読む(`load_record`/reviewを直接読み、`live_user_record`は使わない)。G3ハイライト検査は既存kill switchの意味に従う(スキップ+disabled marker)。設計文とtest期待値をそのように直す。

**M11 「Stdに②が無い」を積極的に検出していない**
- 問題: YのAdv規則は「Part 1が0個でも通る」(`er121_family_y_runner_01.py:1022-1024`)ため、「Adv規則を両levelへ」ではStdの欠落を検出できません。訳欄の判断記録が無いと`render_html_block`は空文字を返し(`er003:478-480`)、黙って欠落します。
- 修正: vocab対象levelではPart 1がちょうど1個であることを必須にする。X新builder・Z(`has_vocab_on_page`、`er026:2548`)にも同じ積極検出を入れる。判断記録が無い場合はSTOP。

**M12 G3「ちょうど1回出現」がそのままでは実装できない**(§D-1)
- 問題: Zではクリップ境界で装飾が複数要素に分割されます。表層形が同じ項目もあり得ます。index.htmlはStd/Advを1ページに載せています。
- 修正: 各片に文字を増やさない属性`data-hl="<candidate_id>"`を付ける。G3はcandidate_id単位で数え、連結したtextContentが`surface`と一致するかを見る。検査はlevel節単位(`level_section_html`、`er_user_listening_page_common_01.py:166`)。③の`title`属性は削除する(読み上げに混入し得るうえ、スマホでは無意味)。

**M13 X公開ページの標準builderに足りない点**
- `tools/build_aif3_listening_page_01.py`はAI島固有の内容を含みます(SLUG :29、intro「後続反映予定…」:118-121)。また`check_page`もKCP G3も呼んでいません。
  - 修正: 標準builderはYのpage_verifyと同等に、`check_page`(public)+G3(ハイライト含む)+Part 2の4者一致を実行する。
- 旧per-article scriptは`er019_*page*.py`が14本あり、docstringでの注意だけでは抜け穴が残ります。
  - 修正: `display_spec`検出STOPを共通module(例: `er019_pp_page_01`、nws2の:8でimport)に置く。
- X player(`er019:3067`)は`info["text"]`を未エスケープで出しています。`render_script_html`(`html.escape`、quote=True)へ一律に置き換えると、引用符を含む既存runのバイトが変わります。
  - 修正: ハイライトがある場合だけ切り替える。
- `CURRENT_SPEC.md:2095`は正式入口を`er019_nws2_final_page_01.py`としているため、更新対象に追加する。

**M14 commitの順序で危険な中間状態が生じる**(IMPL_PLAN_02)
- 問題: マーク発行(`new_review`/`_new_record`)が先にcommitされると、その間に作られた新規runは、マーク付きなのにXページにStd Part 1もハイライトも無い状態になります。Xにはそれを止めるValidatorがありません。
- 修正: マーク発行はA〜Eの配線とValidatorがすべて揃った後の**最後の1commit**にする(またはまとめてmerge)。

### R=推奨
- **R1 重なり規則の穴**: 高優先が低優先に包含される場合(①が③の内側)の規則がありません。③同士の部分交差はNOTICE(順位上位のみ装飾、訳リストには両方)にし、ISSUEは①②が関わる場合に限るのが妥当です。検出は確定時(手順6)、TTS前に行います。
- **R2 ③訳リストの英語表示**: 本文表層形ではなく確定値`used_form`(または「表層形(used_form)」)を表示し、KCPの保護値と揃える。
- **R3 ③の確定値の保護**: ③の訳は今回から表示されるのに、保護はrecord_shaのみで、`_cand_diffs`の照合対象外です。`confirm-revise`でも修正できません(`er128:1698-1700`)。G1照合と修正手段を追加してください。
- **R4 S一覧の漏れ**:
  - `er019`の:434-436(失敗markerがb1b限定)、:439-443(案内コマンドが`--level b1b`固定)、:461-524および:573-624(b1b固定パス・`{source_dir}/b1b/article.md`)、:603-614(study_text stageがb1b限定)。
  - `er063:2592`のコメント。
  - 完了基準案: Part 1系関数内の`"b1b"`リテラルが既定引数以外で0件。
- **R5 Local Rewrite対応**: 文がLRで変わっても項目の語句が変わっていない場合は、LR前後の記録で書換え後の文に対応付けてから装飾し、ISSUEで止めない。AI島はM3 Style GateのLRがあるので、M4のオフライン実行で確認してください。
- **R6 契約・ファイル所有**:
  - 契約に表示単位の型(`DisplayUnit={key, texts[], joiner}`)と`surface`を明記する。
  - `er128`と`er128_kp_highlight_01`が互いにimportし合う形になるため、遅延importにする。
  - `audio_review_player`(`PLAYER_STANDARD_CSS`)の担当班が未割当。
  - 文法側の並行作業(GPG委任_05C)が同じ作業ツリーで`er128`を編集しているため、直列化かworktree分離にする。
- **R7 evidence計画**:
  - 再利用予定のY/Z runはマーク無しなので、`--actor evidence`での新規確定か、複製runでのreconsumeが必要です。
  - 各Familyで③(フォーム経由でしか入らない)を含める。
  - GPG委任_05CのY run dirとは共用しない。
  - Redundancy QAの費用を見込みに加える。
- **R8 CSS・lint**:
  - `-webkit-text-decoration-line`も追加する。
  - 375/390px・DPR2/3で、二重下線が「太い1本」に潰れないことを撮影確認する。
  - 凡例と訳リストの文言は、Zのlint(`er063:2639`)の`英語:`/`日本語:`/`EN:`/`JA:`を避ける。
  - Std Headには`(A2)`表記を入れない(`PAGE_FORBIDDEN_RE`対策)。

### N=備考
- **N1 「英語で解説」の解釈**: DESIGN_01:10が自らPart 1を「英語解説」と呼んでおり、ユーザーの語はこれを引き継いだと見るのが自然です。日本語解説の解釈を強く支持します。紛らわしいのは、Advに既存の「英語での解説」(`explanation_en`、`CURRENT_SPEC.md:2081`)があることです。仮に解説本文を英語にする場合、Prompt以外の差分は次のとおりです(signature・dir・配線は共通):
  - Prompt BODYの「自然な日本語の文章」を変える(=新Promptで、難易度調整の範囲を超える)。
  - 構造検査の「日本語本文30字以上」(`er003:236`)を変える。
  - ページ禁止パターン`English:|EN:`との衝突リスクが増える。
  - 語数・CEFRなどの新しい品質基準が要る。
  - これらはユーザー承認事項です。またAdvが日本語・Stdが英語という難易度の逆転も生じます。
- **N2 費用**: COST_02 §2の(b)「T1訳のlevel間再利用」は、level別dirにキャッシュするため実際には起きません(記述を削除)。費用試算自体は妥当です。②のみにした場合は約¥0.08です。
- **N3 Std訳poolの有効化**: StdでもPart 1↔Part 2の訳の食い違い検査(`er120_part2_wiring_01.py:524-528`)が新たに働きます(既存Gateの適用拡大で、想定どおり)。

### 実装着手の可否
**条件付き可。** 条件は2つです。
1. **M1〜M14を設計正本(DESIGN_02/IMPL_PLAN_02)へ反映すること。** 特に次の5点を明文化:
   - 照合: 本文sha一致の必須化、正規化した文比較、単調整列、表示範囲外の出現の扱い(番号順ソート)。
   - level対応: Part 1生成の隔離チェック・auditへlevelを全面的に通す。
   - マーク: 継承・導出規則とG1の不変条件。
   - reconsume: `cmd_revise`型に揃え、確定Redundancy QAとNG時の手順を明記。
   - 積極検出: 3 FamilyでStd Part 1がちょうど1個であることのValidator化。
2. **配線(C/D/E)の前に、既存の確定済みX/Y/Z run全件(AI島を含む)で解決器をオフライン実行(API 0)し、誤STOP0を確認すること。**

その上で、マーク発行を最後の1commitにする順序を守れば、A‖B先行の並列計画で着手してよいです。M7(Std Part 1=①+②)は明文化してFable判断で拾えます。採否の最終判断はFableです。Production採用の可否は判断していません。