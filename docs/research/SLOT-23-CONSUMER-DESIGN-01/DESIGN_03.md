# DESIGN_03 学習項目①②③の表示仕様(DESIGN_02を置換する正本。Opus条件Aレビュー M1-M14/R1-R8/N1-N3 反映済み)
ユーザー正式決定(2026-10-27、`APPROVED_FOR_PRODUCTION`、到達目標`PRODUCTION_WIRED`、X/Y/Z x Std/Adv全6経路)。read-only設計(コード編集0・API 0)。到達上限=DESIGN_READY。
原文=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`(以下USER.md)。Opus逐語=`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_OPUS_RESULT_02.md`。班間契約=`CONTRACT_03.md`、実装計画=`IMPL_PLAN_03.md`、矛盾一覧=`SPEC_CONFLICT_02.md`(S番号はそのまま参照。R4の追補は本書§J)、費用=`COST_02.md`(N2訂正は本書§I)。
Fable採否: M1-M14全採用、R1-R8全採用(R6のworktree分離は不要=GPG05C完了済み。`audio_review_player`のCSSはC班所有)。

## 0. 解釈・前提
- **解説言語(ユーザー確認中)**: 作業仮定=**A**(解説本文は日本語、Adv同型、Std向け難易度調整のみ)。根拠: DESIGN_01:10がPart 1を自ら「英語解説」と呼ぶ語法を引き継いだと見るのが自然(N1)、USER.md:95,:97。**Bになった場合の差分は付録X1**。以降はAを前提とする。
- **M7 Std Part 1の対象=①+②**(AI島Std ①3+②2=5件。Adv同型、KP⊂vocab=`er119:527-530`)。根拠: USER.md:18(Adv同等)、:20(Part 1相当)、:95(項目構成は踏襲)、:97(新しい方式を足さない)。②のみにするとAdvの既存構造と異なる新方式になり:97に反する。USER.md:15「②で選定された…」・:27「①は勝手に表示対象を変えない」は、「確定済み①②をそのまま表示対象とし選定を変えない」意味で両立。ユーザー報告の3項目めに解釈と根拠を明記する(分類B、Fable採用)。②のみの場合の費用は約¥0.08(COST N2)。
- **表示範囲(M3)**: ハイライト対象の表示範囲=**Full Story本文**。タイトル・Topic intro・Part 1/2は範囲外。
- Part 1最大件数`MAX_PHRASES=5`(`er003:68`)で足りる。

## A. Std Part 1(区分②)= 既存Adv Part 1生成工程の`level`引数化
### A-1 入力
Advと同一の単一アクセサ`rv.part1_items(kp_dir)`+`load_verified_items(which="part1")`、a2は`kp_dir=<run>/a2/key_phrases`。Promptへ送るのは`used_form`のみ(`CURRENT_SPEC.md:2086`)。確定の英語・gloss・順序は不変(G1が守る)。

### A-2 level引数化(M6: levelを全関数へ通す。Adv出力はバイト同一)
- `PROMPT_HEADS={"b1b":現行, "a2":Std版}`。Std版=学習者像1文(B1-B2相当→A2-B1相当)+難易度指示1項目(やさしい語、専門/文法用語は短く言い換え、観点・項目・分量は不変)のみ。**Std Headに`(A2)`表記を入れない**(`PAGE_FORBIDDEN_RE`対策、R8)。BODY・出力形式・構造検査は共通。
- **levelを通す関数(漏れ禁止リスト、M6)**: `_variable_part`(`er003:150-161`)、`check_prompt_isolation`(:182-200)、`build_prompt`、`phrases_signature`(payload=:207)、`generate_general_explanations`、`generate_for_kp_items`、`resolve_*`、`require_fresh_*`、`assemble_part1`(:377)、`write_study_text`、`study_html_for_audio_dir`(:523)、audit内`prompt_template_sha256`(:310)。
- 入力隔離は`PROMPT_HEADS[level]`基準で検査する(検査は弱めない。level渡し忘れはSTALE STOP=fail-closed)。
- sha: b1bは`PROMPT_TEMPLATE_SHA256`不変。a2は`PROMPT_TEMPLATE_SHA256_A2`をaudit/signature payloadに使う。signature payloadの`level`はa2のときだけ追加(b1b署名不変)。
- **golden test**: b1bのPrompt・sha・signature・保存JSON・HTMLのバイト同一と、a2のPrompt・sha(`_A2`)・signatureを両方固定する。
- `write_study_text`のlevel値は`Advanced|Standard`。`study_html_for_audio_dir(audio_dir, items=None, level="b1b")`は`{audio_dir}/{level}`。
- T1訳: Prompt不変。level別dirに保存するためlevel間のreuseは発生しない(N2)。
- 品質検査: Adv検査を同一適用(課金前isolation、構造検査、gloss/引用文実在、model_id一致、ページ側現在値照合)。Std固有の追加検査・独自基準は足さない(USER.md:97)。retry/fallback/resumeは既存のまま。

### A-3 Family別配線
X: `generate_part1_all(level)`(`_for_b1b`を置換、互換別名なし)。Z: `kp_part1_{lv}`/`kp_part1_ja_{lv}`(`E2E_KP_EXTRA_REGEN_NAMES`へ`_a2`追加)。Y: `PART1_STAGES={lv:...}`。Part 1失敗はそのlevelのTTS前STOP(KP確定は保持)。Std/Advは別dir・別stageで相互独立。

### A-4 積極検出(M11)
- vocab対象level(Adv、およびマーク付きStd)では**Part 1がちょうど1個**であることをValidatorで必須とする(Yの「0個でも通る」=`er121_family_y_runner_01.py:1022-1024`を、vocab対象levelでは0個=STOPに変更)。Xの新builder、Z(`has_vocab_on_page`、`er026:2548`)にも同じ積極検出を入れる。
- 訳欄の判断記録が無いと`render_html_block`は空文字を返し黙って欠落する(`er003:478-480`)ため、判断記録なし=STOP。

## B. 本文ハイライト(二重下線方式。USER.md:96-115)
### B-1 表示仕様(決定どおり)
| 区分 | 要素 | 書式 |
|---|---|---|
| ① | `<strong class="lk1" data-hl="<candidate_id>">` | 太字+二重下線 |
| ② | `<strong class="lk2" data-hl="...">` | 太字+通常下線 |
| ③ | `<span class="lk3" data-hl="...">` | 通常下線のみ(太字なし) |
- `HIGHLIGHT_CSS`(単一定数、背景・色なし、`font-size:inherit;color:inherit;background:none`):
  lk1=太字+二重下線(text-decoration-style:double、-webkit-text-decoration-line / -webkit-text-decoration-style も併記=R8、offset 3px、thickness from-font)、lk2=太字+通常下線、lk3=下線のみ(太字なし)。具体的CSS値はA班が実装時にCONTRACT_03の定数として確定し、実ブラウザ撮影で調整する。
- 実ブラウザ確認(R8): PC幅+スマホ375/390px・DPR2/3で、二重下線が「太い1本」に潰れないことを撮影確認。潰れる場合のみthicknessを調整(承認見た目からの逸脱をしない範囲)。
- コピー/読み上げ: 記号・疑似要素・絵文字を追加しない。`textContent`は本文と同一。`aria-label`/`title`でテキストを足さない(**③の`title`属性は削除**。読み上げ混入の恐れ、スマホで無意味=M12)。開発用`⏸`は`audience="dev"`のみ。
- 凡例(任意1行): 台本表の外(`div.script`の外)に置く。文言は`英語:`/`日本語:`/`EN:`/`JA:`を避ける(Zのlint=`er063:2639`、R8)。
- **③の訳リスト**: 当該Partの台本セル直後に`<ul class="hl-meaning">`。各`<li>`の英語表示は本文表層形ではなく**確定値`used_form`**(または「表層形(used_form)」)とし、KCPの保護値と揃える(R2)。日本語訳=確定`japanese_gloss`(official)。文言も`英語:`/`日本語:`等を避ける。①②には出さない。`div.script`/`table`/`h2`の外(`check_page`に触れない)。
- 本文・改行・TTS・Chunk・ポーズは不変。包む前後で`unescape(strip_tags(x)) == text`をassert。

### B-2 描画入口(単一)
- `script_block(text, chunk_texts=None, audience="public", warnings=None, highlights=None)`。`highlights=None/[]`は現行とバイト同一。
- highlight dictは`{candidate_id,kind,surface,unit_key,start,end,gloss_short,used_form}`(型はCONTRACT_03)。描画時に`text[start:end]==surface`をassert(M4-3)。
- 併合描画: 文字位置の境界集合は、各highlightのstart/endと、dev時の各Chunk境界の和集合。各片を`esc`し、highlight内は開きタグで包む。Chunk境界の`⏸`はhighlightの外に出す(タグを閉じて`⏸`を置き再度開く)。publicは`⏸`0個。
- Chunk境界を跨ぐ装飾は許容(DESIGN_01の「跨がない」は撤回済み)。Zのようにクリップごとに別`div.script`となる場合は、片ごとに同種タグへ分割し、**各片に同一の`data-hl="<candidate_id>"`を付ける**(M12)。
- 入れ子は禁止、タグは平坦。

### B-3 確定情報の取得と照合(M1/M2/M3/M4/R5)
**取得**: `er128.load_verified_items(kp_dir, level=, which="highlight")`。`display_spec`付きレコードのみ(無し→`[]`=従来描画)。①②のitemsと`unconsumed[]`のcategory3を、候補doc(`candidates_sha256`がレコードの`origin.candidates_sha256`と一致)の`candidate_id`で結合する。③のreasonは`CATEGORY3_HIGHLIGHT`(旧`CATEGORY3_NO_CONSUMER`は読取互換のみ)。
**入力の取得元(M1)**: Family別アダプタが「候補生成に使った本文」を渡す。`<run>/<lv>/article.md`決め打ちは禁止(Xの実体は`{source_dir}/{lv}/article.md`=`er019:230`、Zは`canonical_article_text(...)`変換後=`er026:2092`)。`sha256_text(text) == cands["text_sha256"]`(`er119:1353,1406`)を必須とし、不一致は`HL_TEXT_SHA_MISMATCH`でISSUE。
**アルゴリズム**(純関数、`er_learning_highlight_01.py`):
1. 文の特定: `er028...build_sentence_units(text)`で`source_sentence_id`の文を得る。候補docの`source_sentence`との比較は`_norm_ws`(`er128:660`)で正規化して行う(M2)。候補docは引用符が直線に正規化済み(`er128:661`)で、AI島a2は`kp_candidates.json:864`が直線、`parts.json:3`の表示が曲線引用符。完全一致比較は偽の`HL_SENTENCE_MISMATCH`を生むため禁止。
2. 本文→表示の写像(M4): 本文の全文を表示テキスト列へ**先頭から順に対応付ける(カーソルを進める単調整列)**。文ごとの独立部分一致検索は禁止(短い文が先行文に誤ヒットするため)。Zのクリップ台本の句読点・引用符差は正規化比較で吸収する。
3. 語形の特定: 対応した表示文の中で`_phrase_pattern(source_span)`を**直接適用**し最初の一致を取る(オフセット表は不要)。`source_span`が正本のため原形からの活用推定はしない。
4. 複数出現(M3): 特定した**1出現のみ**装飾(KP音声・Part 1引用文と同じ出現)。
   - **表示範囲=Full Story本文**。特定出現の文が範囲外(例: AI島Std③`Strategy`のS2はタイトル断片`But AI Has "Strategy Notes`で、Topic intro行にのみ出る=`kp_candidates.json:860-907`、`er019:2938-2940`)なら、`occurrence_sentence_ids`を**番号順**に並べ直す(文字列順だと`["S2","S34","S8"]`になる=`er105:274`)。範囲内の最初の出現を装飾し、NOTICE `HL_OCCURRENCE_RELOCATED`を記録する
(停止しない)。
   - 範囲内に出現が0件: ③は訳リストのみ表示+NOTICE、①②はISSUE(`HL_SENTENCE_NOT_IN_DISPLAY`)。
   - この規則は承認範囲内の表示詳細(分類B、Fable採用)。ユーザー報告に明記する。
5. LR対応(R5): 文がLocal Rewriteで変わっても項目の語句が変わっていない場合は、LR前後の記録で書換え後の文に対応付けてから装飾し、ISSUEで止めない。AI島はM3 Style GateのLRがあるため、オフライン実行(下記7)で確認する。
6. fail-closed: 特定不能はISSUE(ページ生成前STOP)。原因コード=CONTRACT_03の`HL_*`一覧。部分適用・黙って落とすことはしない。
7. **配線前のオフライン実証(必須条件、Opus条件2)**: C/D/E配線の前に、既存の確定済みX/Y/Z run全件(AI島を含む)で解決器をオフライン実行(API 0)し、ISSUE率を計測する。誤STOP 0を確認する(過剰制約で制作を止めないことの実証)。担当=A班(委任_04A)。
8. 事前検査: `confirm --from-form`時にも同じ解決を実行し、特定不能は確定前にISSUE(TTS費用前)。表示本文基準(LR後)の最終検査はG3。

### B-4 重なり・部分一致(R1)
- 優先度は①>②>③。①②間の意味重複は選定時のRedundancy QAで排除済み。③はQA対象外。
- 高優先が低優先に包含される、またはその逆の完全包含(例: ①が③の内側)でも、**内側/高優先を装飾し、外側の低優先は装飾しない**。③の訳リストには残す。NOTICE(停止しない)。包含関係の向きに関わらず規則を適用する。
- ③同士の部分交差: NOTICE(順位上位のみ装飾、訳リストには両方)。停止しない。
- ISSUE(`HL_OVERLAP_PARTIAL`)は①②が関わる部分交差の場合に限る。
- 検出は確定時(B-3手順8)で行い、TTS前に確定する。
- 隣接(間に空白1つのみ)は別要素として個別に装飾。

### B-5 開発専用Chunkマーカーとの共存
`audience="public"`の出力に`⏸`/`chunk-mark`が0個(既存`check_page(audience="public")`+`count_chunk_markers`)。この検査は弱めない。devでは`⏸`はhighlightの外。

## C. X/Y/Z 配線点(file:line、全6経路。DESIGN_02 §Cを継承し以下を追補)
| Family | 本文を描く箇所(現行) | ハイライトの入口 | Part 1/Std Part 1 |
|---|---|---|---|
| **Z** | `er063_family_z_audio_01.py:2528`(Full Story各クリップ`uc.script_block(g["script"], chunk_texts, audience)`)・`:2554`(その他は`script_block(r["script"])`=非対象)。`build_pages`:`:2557-2610` | `_user_page_rows`→`build_page_rows`でPart単位に`g["script"]`群を`script_blocks_for_part`へ渡す。`build_pages(…, highlights_by_level=None)`新引数(None=従来バイト同一)。runnerの`stage_pages`(`er026:2476-2495`)が`load_verified_items(which="highlight")`→解決→渡す | `study_html_by_level["a2"]`にもPart 1(`stage_pages`:2484-2491) |
| **Y** | `er121_family_y_audio_01.py:1467`(`cp.script_block(parts["segments"][sid], chunk_texts, audience)`)、`:1418`(`_script`はFull Story以外=非対象) | `build_page_rows(…, highlights=…)`でsid単位に渡す。`stage_pages`(`er121_family_y_runner_01.py:1192-1215`)が解決 | `study_html`のstd側(:1208)をPart 1込みへ |
| **X(Production player)** | `er019_family_x_audio_production_runner_01.py:3017-`の`_build_level_table`(`info["text"]`を`player_common.render_timeline_row`へ。dev時のみ`script_html_with_chunk_markers`で上書き=:3056-3058)。`build_player_html`:3086-3150(CSS=`player_common.PLAYER_STANDARD_CSS`) | Full Story Part行の`info["text"]`を共通`render_script_html`に置換。`HIGHLIGHT_CSS`を`PLAYER_STANDARD_CSS`に連結。`--stage player`が解決 | `player`(:3725-3749)のa2側に`part1_study_html_for_player(level="a2")` |
| **X(公開ページ)** | 個別`er019_*_page_*.py`は`pp.seg_html`でテキストを組み、共通builderを使わない。AI島=`tools/build_aif3_listening_page_01.py`(Script行: `blocks=[f"<div class='script'>{esc(info['text'])}</div>"]`)(`blocks=[f"<div class='script'>{esc(info['text'])}</div>"]`)。最新generic=`er019_nws2_final_page_01.py`(Part 1は`study_html_for_audio_dir(pp.RUN)`のb1b固定、Part 2・Stdなし) | **新規 `er019_family_x_listening_page_01.py`**: `tools/build_aif3…`を`--slug --run-name --web`引数のProduction標準builderへ昇格(共通`render_standard_page`+`script_block(highlights=…)`+`public_study_html`)。AI島はこれで再ビルド。旧per-article script(`er019_nws2…`等)は**遡及なしのため未改修**(新規記事はこの標準builderを使うと`er019_nws2_final_page_01.py`の先頭docstringに明記し、旧scriptが確定レコード付きrunで呼ばれたら`display_spec`検出でSTOP=旧経路を新規記事で使えない) | `public_study_html`(`er120:512-531`)がa2でもPart 1 |
- 共通化の原則: 本文のハイライト描画は`render_script_html`1箇所、解決は`er_learning_highlight_01.resolve_highlights`1箇所、確定情報取得は`load_verified_items(which="highlight")`1箇所(R-1/R-2同型の「描画は1関数」)。
- `audience=dev`マーカーとの併用はB-2/B-5のとおり。

### C-追補(M13/R6)
- X公開ページの標準builder(`er019_family_x_listening_page_01.py`)は、AI島固有の内容を持ち込まない。`tools/build_aif3_listening_page_01.py`のSLUG(:29)・intro「後続反映予定…」(:118-121)は引数化/撤去する。
- 旧builderは`check_page`もKCP G3も呼んでいなかったため、標準builderで必須化する。
- 旧per-article script(`er019_*page*.py`が14本)はdocstringの注意だけでは抜け穴が残る。**`display_spec`検出STOPを共通module(例: `er019_pp_page_01`。nws2の:8がimport)に置く**。
- X player(`er019:3067`)は`info["text"]`を未エスケープで出している。`render_script_html`(`html.escape` quote=True)へ一律置換すると引用符を含む既存runのバイトが変わるため、**ハイライトがある場合だけ切り替える**(ない場合は従来バイト同一)。
- `CURRENT_SPEC.md:2095`は正式入口を`er019_nws2_final_page_01.py`としているため、更新対象に追加する(Fable/別委任)。
- ファイル所有(R6): `er128`と`er128_kp_highlight_01`は互いにimportし合うため**遅延import**(関数内import)にする。`audio_review_player`(`PLAYER_STANDARD_CSS`)の担当はC班。GPG委任_05Cは完了済みのためworktree分離は不要(着手直前に`git status`/`git diff --stat`で他Agent未commit差分を確認)。

## D. KCP G3拡張(`verify_highlight_outputs`、`er128_kp_highlight_01.py`。fail-closed)
`display_spec`付きレコードのみ検査。**検査はlevel節単位**(`level_section_html`、`er_user_listening_page_common_01.py:166`。index.htmlはStd/Advを1ページに載せるため)。
1. 網羅: 各item(①②③)を**candidate_id単位**(`data-hl`)で数え、ちょうど1出現(Zのクリップ分割は同一candidate_idの片を連結)。連結した`textContent`が`surface`と一致。包含で省略した項目はNOTICE記録と照合。欠落・余剰・区分違いはBLOCK。
2. 本文不変: 装飾タグを剥がしたScript文字列が元台本と完全一致。
3. ③訳: `ul.hl-meaning`の訳が確定`japanese_gloss`と一致、全③を網羅。英語表示は`used_form`(R2)。
4. public混入: `⏸`/`chunk-mark`が0。装飾以外の追加テキスト・記号なし。③の`title`属性なし。
5. Std Part 1: マーク付きStdで、vocab対象levelのPart 1がちょうど1個、各itemの`japanese_gloss`が表示、`meaning_in_text_ja`==確定gloss(M11)。
6. LR整合: ハイライト解決失敗時、ISSUEに`lr_overlap`記録を添付。
7. G1(record↔artifact): `_artifact_diffs`のvocab突合をマーク付きStdへ拡張(S11)。**③の確定値の保護(R3)**: ③の`used_form`/`japanese_gloss`を`_cand_diffs`の照合対象に加え、`confirm-revise`で③の訳を修正できる手段を追加する(現状`er128:1698-1700`では修正不可)。
8. G1不変条件(M8): (a)a2では`display_spec`と`std_part1`が一致する。(b)`display_spec`付きなら`STD_CATEGORY2_NO_SLOT`が0件。
9. G3ハイライト検査と既存kill switchの関係はF-4(M10)。

## E. Std節の構成順
Std節: 全編通し再生 → 台本表(ハイライト+③訳リスト) → Part 1「Vocabulary & Expressions」(新) → Part 2「Grammar & Sentence Structure」。`compose_page_html(part1_html, result)`(`er120_part2_wiring_01.py:507`)でPart 1が先。GPGの文法選定・事前生成・凍結には触れない。StdでもPart 1↔Part 2の訳食い違い検査(`er120:524-528`)が新たに働く(N3、既存Gateの適用拡大で想定どおり)。

## F. マーク・遡及なし・既存ページ・AI島(M8/M9/M10/M14)
### F-1 マーク(feature flagではない承認済み仕様。環境変数・設定dictで切替不可)
- review側`std_part1:true`、確定レコード側`display_spec:"LEARNING_ITEMS_123_V1"`。
- 付与は`new_review`の1箇所のみ。`_new_record`(`cmd_revise`=`er128:1715`、`--adopt-existing`=:1651、自動更新=:578,585からも呼ばれる)では新規付与しない。
- 継承規則: 前レコードがあれば`display_spec`を継承する(継承しないと訳の修正=reviseでハイライトが消える)。前レコードが無い新規時のみ、reviewの`std_part1`から導出する。
- 署名: `std_part1`は**存在するときだけ**`selection_signature`に含める(`er119:583-591`。旧署名は不変。消えても検知されず旧経路に戻る問題を防ぐ)。
- `display_spec`は`content_sha256`/`PROTECTED_ITEM_FIELDS`の対象外。`record_sha256`は全体ハッシュなので再計算される。
- マーク無し=従来描画(ハイライトなし・Std Part 1なし)。

### F-2 既存公開ページ
再ビルド・差替えなし。マーク無しの既存runで`pages`段を再実行しても従来バイト同一(test)。個別承認された再ビルドは`reconsume`で可能。

### F-3 AI島のmigration: `reconsume`(M9。既存`cmd_revise`型)
`py er128_kp_confirmed_content_01.py reconsume --run <run> --level a2|b1b --by <名> --user-ref <path>`
- `confirmation_id`を保持する(保持しないと文法sidecar照合=`er128:441`で整合性違反。AI島a2には文法のsidecarがある)。
- `origin`(form経由の由来)を保持する(`_form_source_problems`=`er128:446-455`が効かなくなるのを防ぐ)。
- Stdはreviewの`selection.vocab`と`std_part1`を**review_lock下で更新**し、`validate_selection`(`er119:505-552`)を通す。NGなら移行せずISSUE。
- `vocab_confirmed.json`の書込みは`finalize_kp`だけ(単一writer、`er119:1044-1048`)。reconsumeは退避と`_try_refinalize`のみ。
- 処理: Stdの`unconsumed[]`のSTD_CATEGORY2_NO_SLOT 2件を`items`(category2, slot=vocab)へ移す。Std/Adv共通で③のreasonを`CATEGORY3_HIGHLIGHT`へ、`display_spec`付与。履歴`event="reconsumed"`、`content_sha256`再計算。冪等、実行前にhash chain検証。
- **訂正(旧DESIGN_02の「選定不変・API 0」)**: ユーザーの選定(①②③の候補ID・区分・件数)は変えない。ただしreconsume後の次回起動時に、Std vocab集合の**確定Redundancy QA(LLM、少額、`er119:937-963`)が必ず走る**。よって「選定不変・QAのみ実行」。
- QAがNGの場合は`reconfirm_required`となり、**ユーザーの選び直しが必要**。手順: (1)ISSUE/待機内容をFableへ報告、(2)Fableがユーザーへ選び直しを依頼、(3)ユーザーが再選定、(4)通常のconfirm経路で再確定。reconsumeは自動で選定を変えない。
- 追加test: 署名変化に対し、Z(`er026:2055-2072,2106`)/Y(`er121:595-603`)/XでAPI 0の再バインドが働き、TTS・音声shaが不変。
- 音声は不変。HTML再ビルド(API 0)+Std Part 1生成(約¥0.16)+Redundancy QA(少額)。

### F-4 kill switchとの関係(M10)
「環境変数で迂回不能」は事実ではない。既存の`EIGO_KP_CONFIRMED_PROTECTION=0`(`er128:87-89`)は`verify_outputs`(:769)・`verify_items_against_record`(:1216)・`live_user_record`(:217)を無効にする。
- **表示の有効化判断はflagを経由しない**: `load_record`/reviewを直接読み、`live_user_record`は使わない。
- G3ハイライト検査は既存kill switchの意味に従う(スキップ+disabled marker)。設計文とtest期待値はそのとおりとする。

### F-5 commit順序(M14)
マーク発行(`new_review`の`std_part1`、`display_spec`導出)は、A〜Eの配線とValidatorが全て揃った後の**最後の1commit**(F班の直前)。先にmarkを出すと、その間に作られた新規runが「マーク付きなのにXページにStd Part 1もハイライトも無い」状態になり得る(XにはそれをStopするValidatorが無い)。

## G. 既定動作・安全性
- APPROVED_FOR_PRODUCTION(ユーザー正式決定2026-10-27)のため隔離flagは置かない。「`display_spec`付き確定レコードがある記事で自動有効、無し=従来どおり」。Grep確認: `display_spec`/`std_part1`の付与箇所が`new_review`の1箇所だけであること。
- 既存retry/fallback/regeneration/resume・KCP G0-G4・STOP/Gateは迂回しない。fail-closedは既存`raise_issue`系に追加する。
- DEV/Trial経路のみの実装にしない(受入条件7)。全てX/Y/Z正式runner・page builderの入口に配線(§C)。

## H. 受入条件との対応
IMPL_PLAN_03 §6参照。

## I. 費用(N2訂正)
COST_02 §2の(b)「T1訳のlevel間再利用」は、level別dirキャッシュのため**実際には起きない**(記述削除)。試算自体は妥当(Std Part 1約¥0.155-0.16/記事)。②のみにした場合は約¥0.08。reconsumeの確定Redundancy QA(LLM、少額)と、evidence各Familyの③を含むrun費用を見込みに加える(IMPL_PLAN_03 §7)。

## J. 旧経路撤去の網羅(R4。SPEC_CONFLICT_02への追補)
追加S項目: `er019`の:434-436(失敗markerがb1b限定)、:439-443(案内コマンドが`--level b1b`固定)、:461-524および:573-624(b1b固定パス・`{source_dir}/b1b/article.md`)、:603-614(study_text stageがb1b限定)。`er063:2592`のコメント。
**完了基準**: Part 1系関数内の`"b1b"`リテラルが既定引数以外で0件(Grepで確認)。

## K. evidence計画の注意(R7)
- 再利用予定のY/Z runはマーク無しのため、`--actor evidence`での新規確定、または複製runでのreconsumeが必要。
- 各Familyで③(フォーム経由でしか入らない)を含める。GPG委任_05CのY run dirとは共用しない。Redundancy QAの費用を見込みに加える。
- 実ブラウザ撮影: 375/390px・DPR2/3(R8)。

## 付録X1 解説本文を英語にする場合(B)の差分(N1)
signature・dir・配線は共通。差分は次のとおりで、いずれもユーザー承認事項(難易度調整の範囲を超える)。
- Prompt BODYの「自然な日本語の文章」を変える(新Prompt)。
- 構造検査「日本語本文30字以上」(`er003:236`)を変える。
- ページ禁止パターン`English:|EN:`との衝突リスクが増える。
- 語数・CEFR等の新しい品質基準が要る。
- Advが日本語・Stdが英語という難易度の逆転も生じる。
