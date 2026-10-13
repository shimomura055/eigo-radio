# TRIAL_REPORT_01: FAMILY-Z-STANDARD-PREVIEW-PROMPT-TRIAL-01 委任_01 (2026-10-13)

Trial専用。Production Prompt/code/DB/経路は無変更。TTSなし。採用判断なし。1回のみのLLM呼出。

## 1. 正本の所在

| 対象 | 正本 | 備考 |
|---|---|---|
| Family X Standard(A2) Preview Prompt | `er003_v1_iran01_a2_generate.py` 174-210行 `PREVIEW_ROLE` (theme/problem/value、2文程度80〜110字、答え・数字・結論・turning point先出し禁止、Comment1/2重複回避)。仕様は`CURRENT_SPEC.md` 1590行「Preview原則」 | Family Zは流用していない |
| 現行Family Z Standard Preview Prompt | `er026_family_z_fiction_production_runner_01.py` 468-480行 `_FAMILY_Z_PREVIEW_ROLE_JA` / `build_family_z_preview_prompt()`。Production呼出は`er062_family_z_writer_01.py::run_support_std` (877-889行)が「重複回避」(Comment 1)を末尾に付与して`a2gen.run_support_text`へ渡す | 実際のrun_e2e_02経路はこちら。runnerの`generate_family_z_preview`(502行)はPhase 1互換の旧経路 |
| Production生成条件 | model=`gpt-6-luna`(`er006_model_routing_contract_01.py` 50行 `SUPPORT_MODEL`、`A2_SUPPORT`)、reasoning effort=`high`(`REASONING_EFFORT`)、developer message=`日本語のListening Support原稿を作成してください。`、`build_support_prompt`がSUPPORT_JA_PRINCIPLE・SUPPORT_PROHIBITIONSを付加 | 本Trialは完全同一(要求=応答=`gpt-6-luna`、effort high) |
| 入力本文 | `er026_output/family_z_production_e2e_01/melos/run_e2e_02/writer/std.md` (Production Previewが実際に参照した原稿と同一。`run_support_std(full_text=std.md全文)`)。Comment: 同`support/a2_support.json` | 選定理由: 最終組立(assemble)に使われたrun_e2e_02の正本 |
| 既存Preview | 同`support/a2_support.json`の`preview` (再生成なし) | |

## 2. Prompt差分(詳細: prompt_before_01.txt / prompt_after_01.txt / prompt_diff_01.md)

変更点(最小調整、Family X `PREVIEW_ROLE`の構造を流用):
1. 役割: 「Previewを書く担当」→「冒頭を担当するナビゲーター」(Family Xと同じ)。
2. 役割段落にtheme/problem/valueを導入(Family Xのquestionは省略。Family Xの「4要素を律儀に別文で書き並べなくてよい」注記を流用)。「状況設定(誰が・どんな状況か)」の指示を削除し、problem=「主人公がどんな状況で、何に迷い・何と向き合っているか」へ置換。
3. 「続きを聴きたいと思わせる」を目的として明記。
4. 分量は2文程度・80〜110字程度(Family X準拠、4文・150字超禁止)。
5. 禁止項目を箇条書き化: 出来事を順に説明しない(あらすじ化禁止)/結末先出し禁止/転換点・後半の具体展開先出し禁止/Comment 1との重複禁止/本文にない設定・事実の追加禁止。
6. 既存の禁止表現(`fam_c._BANNED_PHRASES_INSTRUCTION`)と末尾の「重複回避(Comment 1)」ブロックは無変更で維持。

before全文は`prompt_before_01.txt`、after全文は`prompt_after_01.txt`。LLMへ実際に送った組立済み全文は`prompt_*_full_assembled_01.txt`。

## 3. Preview全文

BEFORE(現行Production生成物、81字・3文):
> 結婚式を終えたメロスは、三日目の夜明け前に町へ戻り始めます。帰り道には、橋のない川と、道をふさぐ男たちがいます。川は雨で茶色くなり、流れもとても速くなっています。

AFTER(改善Prompt、1回生成、73字・2文):
> 友人の信頼に応えたい思いと、苦しさから逃れたい気持ちの間で揺れるメロスを描いた物語です。人を信じることの重さや、信頼に応える難しさも感じられます。

## 4. 品質評価(事実ベース、採用判断なし)

参照: Comment 1(開始前の状況: 王への抗議・死刑・猶予・友人が身代わり)/Comment 2(川・三人組・立てなくなる・待つか戻るかの選択)/Comment 3(友人の手の記憶・信頼・岩の水・立ち上がる)。Production PreviewはComment 1のみを重複回避の入力に持つ。

| 観点 | BEFORE | AFTER |
|---|---|---|
| 興味喚起 | 弱い。具体的場面の列挙で「何が問題か」が無い | 葛藤(信頼 vs 逃げたい)を前面に出す点は改善。ただし誰が・どんな状況かが一切なく、リスナーは「友人の信頼」が何かを知らないまま聞くことになる。2文目は一般論(「感じられます」)で、どの信頼物語にも当てはまる汎用文。Previewとして具体的な引きは弱い |
| あらすじ化 | 該当(結婚式後の帰路・川・男たちの出来事列挙) | 解消(出来事の列挙なし) |
| ネタバレ | 結末なし。後半(Comment 2の川・三人組)の具体的障害を先出し | 結末なし。ただし「苦しさから逃れたい気持ちの間で揺れる」は物語中盤の岩場の転換点(本文: 倒れて「待つか戻るか」「楽に思えた」)の内面を要約的に先出し。「信頼に応える」は結末を強く示唆はしないが、結果の方向を匂わせる余地あり |
| Comment重複 | Comment 1とは重複なし。Comment 2(川・男たち)と具体的場面が重複 | Comment 1とは重複なし。Comment 2の「待つか戻るか」の選択とComment 3の「友人の信頼」が主題レベルで部分重複(Productionの重複回避入力はComment 1のみ) |
| 日本語の自然さ | 自然・平易 | 「〜を描いた物語です」「感じられます」は解説文調で、導入のナビゲーターとしては硬め。聴きやすさは許容範囲だがやや抽象的 |
| Family X設計思想(theme/problem/value) | 非整合(themeもvalueも無し) | theme(信頼 vs 苦しさ)・value(信頼の重さ)は有るが、problem(直面する具体的状況)が欠落 |
| 本文にない設定・事実 | なし | 事実の追加なし。「苦しさ」「信頼」は本文由来。「人を信じることの重さ」は解釈的評価で本文に直接の記述はない |
| 禁止表現 | 該当なし | Production lint該当なし。ただし「雰囲気だけの抽象的な誘導を避ける」というPrompt内の既存ルールの趣旨には、2文目が近い |
| 文字数・文数 | 81字・3文(80〜110字目安内) | 73字・2文(80字未満、文数は目安内)。目安から外れるがProductionのhard gateではない |

### 問題点
- あらすじ化は解消した一方、逆方向(抽象・評論調)に振れた。situationの提示が失われ、「続きを聴きたくなる」具体的な引き(約束・身代わりの友人など、Comment 1と重複しない範囲でのstakes)が無い。
- 「揺れる」で中盤の転換点の内面を要約している(軽度のネタバレ)。
- 1サンプルのみ(追加生成禁止)のため、出力のばらつき・Promptの再現性は未測定。

## 5. 実行モデル・費用・テスト

- モデル: 要求`gpt-6-luna`、応答model_id=`gpt-6-luna`(最新世代の系統。Production Preview生成と同一モデル=比較可能性のため例外として明記、reasoning effort=high)。response_id・トークンは`cost_01.json`。
- 費用: 事前見積¥0.30(入力3,822tok推定+出力3,000tok上限、`gpt-6-luna` input $0.10/output $0.50 per 1M、出典`er006_model_routing_pricing_coverage_test_01.py`50-52行、USD/JPY=160)。実測 入力1,556tok・出力888tok(reasoning 818)=約¥0.096。LLM呼出1回。上限¥20/ハードストップ¥25に対し大幅未満。
- Validator: `er062_family_z_structure_01.lint_support_text(text,'ja','melos')`(Production Preview lintと同一呼出)。BEFORE=違反なし、AFTER=違反なし。結果は`validator_result_01.json`。
- Regression: `er062_family_z_writer_01_test_01` 64件OK、`er026_family_z_fiction_production_runner_01_test` 21件OK (Production無変更のため想定どおり)。
- State guard: run_e2e_02配下全ファイルとProduction関連py 5本(計406ファイル)のsha256が前後で不変(`state_guard_01.json`、changed=[])。

## 6. Production整合性の事実確認(将来検討用、採用ではない)

- 差替箇所: `er026_family_z_fiction_production_runner_01.py` の`_FAMILY_Z_PREVIEW_ROLE_JA`定数1箇所(`build_family_z_preview_prompt()`経由)。`run_support_std`(er062)は`build_family_z_preview_prompt() + 重複回避(Comment 1)`と組立てるため、角括弧やformat置換を使わなければ呼出側無変更で差替可能。旧Phase 1経路`generate_family_z_preview`も同関数を参照する。
- Validator互換: Production lintは同一呼出で通過。retry(`generate_with_lint` retries=1→`FamilyZLintStop`)の挙動は不変。
- Dangling Reference: 新Promptは`{comment_1}`等のformat置換プレースホルダを使わず、既存の文字列結合(重複回避ブロック)を維持したため、未解決参照は生じない(Family Xの`PREVIEW_ROLE.format(...)`方式とは異なる点に注意)。
- Family Z Advanced Previewは`b1s.PREVIEW_ROLE`(英語、Family X B1)を使用しており、本Trialの変更は影響しない。AdvはComment 1/2両方を重複回避入力にするが、Std(Family Z)はComment 1のみ。
- 再生成機構: `prior`指定時はPreviewを再利用する仕様(`run_support_std`の`prior`)。Prompt差替後は既存run_e2e_02のPreviewとは別物になるため、差替を採用する場合は再生成対象の整理が必要(未判断)。

## 7. 終了Status案・未解決事項

- Status案: **USER_DECISION_REQUIRED**(Trial結果はあらすじ化の解消を確認したが、抽象化・中盤転換点の軽度ネタバレ・problem欠落があり、1サンプルのみのため採否・追加Trial要否は判断を要する)。VALIDATED/REJECTED の断定はしない。`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない。
- 未解決/Open Item候補: (1) Previewの「具体的な引き」(stakes)をネタバレなく入れる指示(例: Comment 1と重複しない状況のうち何を残すか)の設計、(2) Std Previewの重複回避入力をComment 1のみ→Comment 1〜2へ拡張するか(Family X Stdと同様)、(3) 複数サンプルでの再現性、(4) 他のFiction素材での挙動。OPEN-338として起票。
