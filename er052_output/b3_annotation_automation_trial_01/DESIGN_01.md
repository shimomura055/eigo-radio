# DESIGN_01: B3注記の自動化(B3-ANNOTATION-AUTOMATION-TRIAL-01 委任_01 Phase 1、2026-10-10)

Status: 設計・棚卸のみ。課金API 0件。Production変更なし。`APPROVED_FOR_PRODUCTION`ではない。
「確認済み」=本書作成時に実ファイル・実行で確認、「未確認」=確認していない。
パス基準: `C:\Users\tensh\eigo-radio`。Trial正本ディレクトリ = `er052_output/factlock_astra_e2e_trial_01/`(以下 `TR/`)。本Trialの出力先 = `er052_output/b3_annotation_automation_trial_01/`(以下 `OUT/`)。

## 1 注記仕様v2の正本と要件

### 1-1 正本の特定(確認済み)
| 文書 | 役割 | sha256 |
|---|---|---|
| `TR/B3_ANNOTATION_SPEC_v2_ANNOTATOR.md` | 注記者(worker A/B)に渡した規則。**仕様の実体** | `8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57` |
| `TR/ANNOTATION_DELEGATION_TEMPLATE_v2.md` | worker A/B指示文の固定テンプレート(置換欄7つのみ) | `e77e1ed6716291ad2d58275fd96013b5ccbc52732cabcdc99f5e01c41808bf09` |
| `TR/B3_ANNOTATION_SPEC_v2.md` | 完全版(Fable・評価者用。§A〜§J。注記者には渡していない) | `b8dd84b09cfefc3e065a2978a11943909b80af1ab598c45dc1a4867189049fc1` |
| `TR/stage_r/SPEC_V2_CLARIFICATIONS.md` | 運用明確化(a)〜(f)。(a)(b)は実プロンプト末尾に全テーマ共通で追記された | 未計算 |
| `TR/annotation/prompts/<slug>__<A|B>.md`(24ファイル) | **worker A/Bに実際に渡した指示文の実体**(sha: `TR/annotation/PROMPT_SHA256.json`) | 同左 |

状態: 仕様v2は `SPEC_V2_READY`(ユーザー確認待ち・未固定)と明記されている。`B3_SPEC_V2_SHA256.json` には同じ値が記録されている(確認済み)。固定されたか否かはSSOT側で未確認。

### 1-2 「自動化は範囲外」の引用(確認済み)
- `TR/B3_ANNOTATION_SPEC_v2.md` §B: 「範囲外: 注記の実施(本書は仕様のみ)、**注記の自動化(Production化にはB3自身が同等の注記を自動で付ける必要があり、その精度は未測定)**、Writer プロンプトの変更。」
- 同 §I-2: 「**人手(AI worker)注記の上限性能**: Production化にはB3自身が同等の注記を自動で付ける必要があり、その精度は未測定(未確認)。」
- `er052_output/factlock_astra_e2e_trial_01/PREREGISTRATION_01.md` 78行: 「B3注記は人手(Sonnet worker)で、独立二重注記+固定ルールだが、結果は『人手注記の上限性能』であり、Production化にはB3自動注記が必要(OPEN項目候補、起票はFable判断後)。」

### 1-3 重要な事実訂正(ユーザー指示文との対応)
- 指示文の「Sonnet系worker A + worker B + 決定論的統合」は実態と整合する。ただし**workerはAPI呼び出しではなく Claude Code subagent**(`transcript.jsonl` の `model` = **`claude-sonnet-5-5`**、確認済み)。subagentは `annotation/prompts/<slug>__<A|B>.md` をReadツールで1回読み、返答本文で答えた。したがって**API直渡しは未実施**(今回のAPI化で初めて、Claude Code harness由来のsystem prompt等の影響が外れる。差異として §3-5 に記録)。
- worker A/Bの区別はプロンプト中の `注記者は A/B です` の1語のみ(確認済み: A/Bのプロンプトは `annotator` の値と保存先パスの語以外同一)。つまり「A+B」は**同一プロンプト・同一モデルを2回**呼ぶ構成であり、役割分担ではない。
- worker指示文 = 固定テンプレート充填 + **全テーマ共通の末尾追記「運用上の明確化(a)(b)」**(md5一致を5テーマで確認)。テンプレートは「記事ごとの補足・ヒント禁止」を謳うが、(b)には「hormuz新B3『約25時間後』」というテーマ固有の例が含まれる。Productionでは(a)(b)を仕様本体へ取り込む必要があり、これは**仕様の変更(v2.1)**に当たる = USER_DECISION候補(§6 U-3)。

### 1-4 仕様v2の要件(注記者用仕様 `..._ANNOTATOR.md` §1〜§7 の要約)
- **入力**: (1)元のニュース欄(brief、Storyline節 + Selected Facts節)、(2)台帳(VERIFIED事実の一覧。欄: statement / scope / conditions / numeric_value / date_or_period / notes_for_writer)、(3)仕様本文。他の道具・文書は使わない。
- **出力**: `=== ANNOTATED_BRIEF_BEGIN/END ===` で囲んだ注記版全文 + `=== SIDECAR_JSON_BEGIN/END ===` で囲んだサイドカーJSON。STOP時は `=== STOP ===` + 理由。
- **タグ種別(3種のみ)**: `【事実N】`(事実境界+台帳ID紐付け)、`【中核数値】`、`【周辺数値】`。他の【】は禁止。
- **非改変規則**: 元briefへの付け足しのみ。許す挿入は、Selected Facts節内の「`。`直後に`\n- `」「節先頭行/`。`+改行直後の行頭に`- `」だけ(直後は必ず`【事実N】`)。削除・言い換え・語順・句読点・空白の変更は禁止。
- **【事実N】の付け規則(§2)**: 単位=台帳の事実ID境界。既定は箇条書き1項目=1事実。(S1)項目内に文が2つ以上、かつ(S2)別々の文が別々の台帳IDを主な根拠にする場合だけ`。`で分割。限定文(「ただし〜」等)は直前の主張と同じ事実。1項目で最大3事実。連番1..K、欠番・重複・複合タグ(`【事実1,事実2】`)禁止。`Storyline`行・`素材:`行・`Storyline：`重複行には付けない。台帳IDは本文に書き足さずサイドカーに書く。
- **数字の印(§3)**: 対象=算用数字(全角含む)を含む表記。漢数字だけの数量は対象外(`annotation_notes`に記録)。台帳ID形(`ZZ-001`)は数字扱いしない。表記(surface)=数字+単位+ヘッジ語(約・およそ・最大・少なくとも・超・以上 等)で末尾に印。kind = magnitude / date_time / range / year / ordinal / name_embedded(後3者は常に周辺)。同じ台帳データを指す表記は同一concept。
- **中核/周辺の決定(§3-5、機械的)**: 主数字(表記末尾の数字列、範囲は両端)を10進で比較。適格 = 量は主数字が台帳`numeric_value`欄(`numeric_scope`括弧内除く)に含まれる / 日付は表記に月があり台帳`date_or_period`先頭の日付表現と年月日(時刻)が全て一致。台帳に当該欄が1件も無い場合のみ`statement`で代替。n = magnitude/date_time/range の概念総数、上限 = `max(3, min(6, floor(n/2)))`。優先順 = Storylineの量 → 他の量 → 日付、同順位は出現順。先頭から上限までが中核、他は周辺。上限超過の周辺化は`annotation_notes`に記録。
- **台帳に無い記述(§4)**: 印を付けず`unmapped_claims`(type: new_fact/new_number/new_causal/generalization/specification/qualifier)に記録。STOPは2条件のみ((i)Storyline骨格が台帳に無い (ii)台帳に無い数字が中核になりうる形でStorylineにある)。
- **迷ったとき(§5)**: 分けない / 周辺 / 名称内番号 / 台帳IDは全て併記 / 規則外は印を付けない、かつ`annotation_notes`に記録。
- **検証規則(完全版§E、`TR/b3_annotation_check_01.py`、LLM不使用)**: (a)原文一致(`align_md`: 3種の印と定義済み挿入だけを除いて原文とbyte一致) (b)台帳紐付け(全【事実N】がVERIFIED記録に1件以上、briefの明示ID一致。AMBIGUOUS紐付けは運用明確化(c)でWARN許容) (c)数値(分類漏れ0、架空宣言0、概念束ね不備0、宣言classが`compute_expected`と一致) (d)連番・複合タグ・未知【】・Storyline/素材行への事実タグ無し (e)サイドカーの`spec_sha256`/`brief_sha256`/`annotator`照合 (f)台帳スキーマ点検。
- **統合規則(完全版§D、`TR/b3_annotation_merge_01.py:merge` L229)**: 分割は粗い方=共通部分、数値表記は和集合、kind不一致は中核不可側、台帳IDは共通部分(空ならSTOP)、**class(中核/周辺)は統合入力から`compute_expected`で再計算**(A/Bの宣言は使わない)、統合後に検査再実行(FAILなら不採用)。判定線(分割一致率<0.8または中核Jaccard<0.67で「規則を機械適用できていない」)は事前登録の推定値。
- **既知の限界(完全版§I)**: A/B同モデルで誤りが相関し一致率が過大になりうる / 漢数字・「倍」等は対象外 / E1/E2'は台帳の欄名(`numeric_value`・`date_or_period`)に依存し、Production台帳が同じ欄を出すかは未確認。

### 1-5 決定論的統合・検査の実装場所(確認済み)
- `TR/b3_annotation_merge_01.py`: `build_delegation`(L334、テンプレート充填)、`extract_output`(L319、返答から注記版md+サイドカー抽出、STOP/形式不正を区別)、`merge`(L229)、`agreement_metrics`(L164)。CLI: `fill` / `extract` / 統合。
- `TR/b3_annotation_check_01.py`: `run`(L700)、`align_md`(L329)、`compute_expected`(L470)、`check_c`(L542)。テスト `b3_annotation_check_01_test.py`。
- 実行手順: `TR/annotation/RUN_ANNOTATION.md`(subagent起動 → extract → 単独check → merge → 判定線)。**LLM呼び出し以外の全工程が既にスクリプト化されている**(これが自動化の最大の足場)。

## 2 既存Trial注記artifact棚卸(Ground Truth)

詳細JSON: `OUT/gt_inventory.json`(生成: `OUT/inventory_gt.py`)。注記版B3の基準: hormuz・streaming_priceは B3 v2(`stage_r/<slug>/storyline_b3_v2/`)、他は v1(`stage_r/<slug>/storyline_b3/`)。

### 2-1 テーマ数の訂正
指示文の「8テーマ想定」に対し、実在は**10テーマ中9テーマがGT完備**(inbound_tourismは単独検査FAILで統合せずGTなし)。なお過去の人手注記(旧4: META/ホルムズ/宇宙/ミニバッグ、`factlock_writer_trial_01/briefs/*/b2/selected_brief_factlock.md`)は存在するが、仕様v2は使用を禁じており(完全版§B、人手指定で規則文書がない)、**本Trialでは参考扱いにもしない**。

### 2-2 GT棚卸表(sha256は先頭12桁。全桁は `gt_inventory.json`)
| theme | B3 | 未注記B3 sha/字 | 台帳 sha/字 | GT注記版(`annotation/final/<s>/selected_brief_factlock.md`)sha | 事実/中核/周辺 | A/B単独の事実/中核/周辺 | merge分割一致/中核Jaccard/分類一致 |
|---|---|---|---|---|---|---|---|
| byd_recall | v1 | f374a4704364/353 | 06ae3dca98cd/3696 | 0d5fb346c366 | 1/3/0 | A 1/3/0, B 1/3/0 | 1.0/1.0/1.0 |
| central_bank_mortgage | v1 | cddeced887f1/731 | 7a5593c4a002/4312 | 277093f9c68b | 6/6/12 | A 6/6/12, B 6/6/12 | 0.8/1.0/0.88 |
| hormuz | v2 | 73afafe8c17a/567 | 9bd6834e68e7/4949 | cb5fa8ca8a0d | 4/7/5 | A 4/7/5, B 4/7/5 | 1.0/1.0/1.0 |
| inbound_tourism | v1 | 0bdfa5688ce2/446 | ddf3553ff2a0/6522 | **なし**(A/B単独check FAIL) | - | - | - |
| meta | v1 | 83c29bc213a7/401 | ea0ce587e605/6454 | 6371e1022d80 | 3/0/0 | A 3/0/0, B 3/0/0 | 1.0/n/a/n/a |
| openai_copyright | v1 | 3051aa83a58f/772 | 2463c2eabfc2/3545 | ab605888f796 | 1/5/1 | A 1/5/1, B 1/5/1 | 1.0/1.0/1.0 |
| semiconductor_earnings | v1 | 12638264343d/507 | 36b2c87dbc57/2215 | a6a5fe9dd8b6 | 1/6/6 | A 1/6/6, B 1/6/6 | 1.0/1.0/1.0 |
| small_bag | v1 | a4cfad728faf/537 | 0cc8ca3f2e73/2929 | 50a9dc7bc2fc | 3/1/4 | A 3/1/4, B 3/1/4 | 1.0/1.0/1.0 |
| space_weapons | v1 | 84c69f132926/760 | f172a253f24b/10472 | b25d3a8d201b | 5/1/3 | A 5/1/3, B 5/1/3 | 1.0/1.0/1.0 |
| streaming_price | v2 | 776ac8d80c32/545 | 11eb38bd8532/2775 | 8f5047b77e87 | 1/4/6 | A 1/4/6, B 1/4/6 | 1.0/1.0/1.0 |

「境界」タグ = 【事実N】の数。GT 9テーマ合計: 事実25 / 中核33 / 周辺37。全GT注記版は検査(`b3_annotation_check_01.py`)で再確認PASS(`baseline_check_exit=0`、9/9、確認済み)。

### 2-3 各テーマの所在
- 未注記B3: `TR/stage_r/<slug>/storyline_b3[_v2]/selected_brief.md`(+ `fact_selection_evidence.json`、`full_ledger.json`)
- 台帳: `TR/stage_r/<slug>/research_ledger/verified_fact_ledger.txt`
- worker A/B返答: `TR/annotation/out/{A,B}/<slug>/reply.md`、抽出後 `annotated.md` + `annotation.json`、検査 `TR/annotation/check/{A,B}/<slug>.json`、transcript `transcript.jsonl`(v1ラウンド分は`transcript_v1round.jsonl`)
- 統合: `TR/annotation/out/merged/<slug>/`(`merged_selected_brief_factlock.md`、`merged_annotation.json`、`merged_core_numbers.json`、`resolution_log.json`、`agreement.json`、`merged_check_result.json`)= 統合ログ
- final(GT注記版+JSON): `TR/annotation/final/<slug>/`(`selected_brief_factlock.md`、`annotation.json`、`fact_selection_evidence_factlock.json`)

### 2-4 GTの性質と限界(重要)
1. **GTは人間の正解ではない**。`claude-sonnet-5-5` の2回呼び出し(A/B)+決定論統合の出力であり、「Trial上の参照実装の出力」。人間確認は未実施(未確認)。
2. 9テーマ全てで **A単独とB単独のタグ件数が完全に一致**(事実/中核/周辺とも)。同一モデル・同一プロンプトの誤り相関(完全版§I-1)が実データで確認された形。したがって「A/Bが一致する」は規則の機械適用可能性の証拠として弱い。
3. briefは短い(353〜772字)。Production briefが同等とは限らない(未確認)。
4. 初回(v1ラウンド)の単独check結果: hormuz = FAIL(d: v1 briefのSelected Factsが「Storyline重複行+素材段落」で【事実N】を付ける箇条書きが0件)、semiconductor_earnings = FAIL(b: AMBIGUOUS台帳ID紐付け。運用明確化(c)の追加のみでPASS化=**同一返答を規則の方を変えてPASSにした**)、streaming_price = FAIL(b)/STOP、inbound_tourism = FAIL(b,c)。すなわち**初回FAILの主因は「LLMの注記能力」ではなく「入力briefの書式」と「検査規則の未定義事例」**。Productionで自動化するなら、B3出力書式(Selected Facts箇条書き)と台帳スキーマ(`numeric_value`/`date_or_period`欄)の前提をB3生成側で保証する必要がある。
5. inbound_tourismのA/B FAILの内訳(`ANNOTATION_SUMMARY_01.md`): `ID_RE`が連字符なしID(`F01`)を除外できず括弧内IDの数字(01,02…)を分類漏れと誤検出する検査script側の欠陥候補が未解決。本Trialでは**検査scriptを変更しない**(変更するとv3扱いになり全テーマ再注記が必要=完全版§J)。inbound_tourismは「GTなしのストレス入力」として check-only で扱う。

## 3 自動化方式の候補設計

共通前提: 仕様v2(sha固定)・テンプレートv2・Trial実プロンプトの本文を変更しない。出力検証は既存の `b3_annotation_check_01.py` / `b3_annotation_merge_01.py` をそのまま再利用(変更しない)。モデルは Provider既定のthinking/temperature(xm_driver.pyの規約)。

### 3-1 方式表
| 方式 | 概要 | 呼び出し/記事 | Prompt | 新Promptが必要か |
|---|---|---|---|---|
| **M-A 単一呼び出し** | Trial worker 1名分(A)をAPIで再現。返答 → extract → 単独check。FAILなら不採用(再試行は後述の規則) | 1 | Trial実プロンプト本文(`prompts/<slug>__A.md`の`【依頼文(ここから)〜(ここまで)】`)を**逐語** | **不要** |
| **M-B 二重注記+決定論統合** | Trialと同じ構成: 同一プロンプト・同一モデルでA/Bの2回呼び出し → 各単独check(双方PASS必須)→ `merge`(決定論)→ 統合後check | 2 | 同上(`annotator`の1語のみ違い) | **不要** |
| **M-C 構造のみLLM+決定論タグ挿入** | LLMには「事実境界(文位置)・数値表記・kind・concept・台帳ID」だけをJSONで出させ、【事実N】【中核数値】【周辺数値】の**挿入と中核/周辺の決定は全てスクリプト**(`compute_expected`)。本文非改変がby constructionで保証される | 1 | 出力形式が変わるため**新Prompt必須**(仕様本文は逐語、§1/§6/§7と出力例のみ差し替え) | **必要 = USER_DECISION候補** |
| M-D 決定論前処理+LLM | 台帳・briefから数値・日付候補と適格判定を機械抽出して候補表をLLMに渡し、LLMは境界・concept・ID紐付けを判断 | 1 | 候補表の追加・仕様の再構成が必要なため**新Prompt必須** | **必要 = USER_DECISION候補** |

### 3-2 M-A / M-B の詳細
- 入力: `TR/stage_r/<slug>/{storyline_b3[_v2]/selected_brief.md, research_ledger/verified_fact_ledger.txt}`、`..._ANNOTATOR.md`、テンプレート。依頼文は `build_delegation` で生成され、Trial実プロンプトは「これ + 全テーマ共通の運用明確化(a)(b)」。`annot_driver.py` の `verify_provenance` が「テンプレート充填結果が実プロンプト本文の先頭と一致」「実プロンプトのsha256が `PROMPT_SHA256.json` と一致」を全24+(10テーマ×2)で確認済み(60 payload、provenance_failures=0、確認済み)。
- 出力: 返答本文 → `extract_output` → `annotated.md` + サイドカー。
- 決定論的検証: `chk.run`(a:タグ除去後に原文とbyte一致 / b:Fact ID存在とVERIFIED / c:数値分類・宣言class一致 / d:連番 / e:sha照合)。M-Bはさらに `merge` の `status`。
- 非改変の担保: LLMが本文を再出力するため、**by constructionではなく検査で担保**(検査(a)がFAILなら不採用)。これがM-Cとの本質的な差。
- 失敗モード: (1)区切り欠落・JSON不正(`extract_output`が`Stop`) (2)本文の言い換え/空白変更(a FAIL) (3)中核/周辺の誤宣言(c FAIL) (4)概念束ね不備・分類漏れ(c) (5)台帳ID誤り・VERIFIED以外(b) (6)連番崩れ・複合タグ(d) (7)根拠のないSTOP返答 (8)出力トークン上限切れ(`max_output_tokens`不足)(9)thinking/reasoning で長時間・高費用 (10)A/B誤りの相関(M-Bで検出不能)。
- 再試行: Trial運用では「形式FAIL時は同slug・同注記者に再委任1回まで、3回目なし」(`RUN_ANNOTATION.md`節6)。本Trialは**この上限を踏襲**(同一入力・同一プロンプトで1回のみ再実行、元応答も保存)。上限の独自変更・Gate回避はしない。
- M-AはM-Bの呼び出しのうち「A」の出力を再利用して評価できる(同じ呼び出しを2方式の評価に使う)。**呼び出しは共有し、評価だけを分ける**ことでM-A/M-Bを追加費用なしで比較する。

### 3-3 M-C の詳細(新Prompt案、Phase 2前に承認が要る)
- LLM出力JSONの案: `{"items":[{"line":N,"split_after_chars":[…],"ledger_ids":[[…],…]}], "numbers":[{"surface","kind","concept","ledger_ids"}], "unmapped_claims":[], "annotation_notes":[]}`。スクリプトが(1)分割位置で`\n- 【事実N】`を挿入、(2)surfaceの出現位置(最長一致)に印を挿入、(3)classを`compute_expected`で計算。
- 利点: 本文非改変率が構造上100%、classの誤りが原理的に消える、出力トークンが少ない(本文再出力なし)。
- 欠点/リスク: 新Promptで仕様の一部(§1の出力形式・§6・§7・§8の例)を書き換えるため、**Trial仕様v2との同一性が崩れる**(`sha固定`違反=v3扱い)。surfaceの位置同定(同一表記が複数回出る場合)をスクリプトが決める仕様が新規に必要。Production採用提案時は「未検証の簡略方式への勝手な置換」に該当しないよう、**M-A/M-Bを先に検証し、M-Cは別Phaseで承認を得てから**とする。
- 今回のPhase 1では**M-Cのプロンプトは作成しない**(指示文の逐語移植で自動化が成立するため、STOP条件「新Promptが必要」には該当しない。M-C/M-Dは任意の追加案としてUSER_DECISION候補に載せる)。

### 3-4 モデル候補(PM_GOVERNANCE 25節 最新モデル原則)
| モデル | 位置づけ | 価格(USD/1M: in/cached/out) | 出典・日付 | Trialとの対応 |
|---|---|---|---|---|
| `claude-sonnet-5`(API) | Trialのworkerと同系列。ただしTrial実体は `claude-sonnet-5-5`(Claude Code subagent)。**`claude-sonnet-5`(API)と`claude-sonnet-5-5`の同一性は未確認**(Phase 2前にmodels listで確認) | 2.0 / 0.2 / 10.0(登録値) | `xm_prices_01.json`(取得2026-10-10 04:50Z、`platform.claude.com/docs/en/about-claude/pricing`)。`claude-sonnet-5-5`の個別単価は**未確認** | 同系列(対応: 近い) |
| `gpt-6.1-sol` | OpenAI最新世代の主力。cross-modelとして、A/B誤り相関の影響を受けない参照 | 2.0 / 0.1 / 10.0 | `er005_output/cost_baseline_01/pricing_snapshot.json`(OFFICIAL_PRICING_PAGE_FETCHED、`PRICING_SOURCES_01.md`) | 別系列 |
| `gpt-6-astra` | 最上位。精度の上限確認用(任意) | 10.0 / 1.0 / 50.0 | 同上 | 別系列 |
- 使わない: `gpt-6-luna`(最廉価・PROJECT_INTERNAL_RECORD。本タスクは仕様遵守精度が要で最廉価を使う理由が現時点でない)、`gpt-5.6-*`・`claude-haiku-4-5`(旧/下位世代)、Gemini/DeepSeek(最上位系ではない)。
- Claude Opus系: 価格が登録されておらず**未確認**。候補に入れるなら価格確認が先(無料のpricing page取得)。

### 3-5 Trialとの差異(自動化で変わる条件。Phase 2の報告に必ず記載)
1. 実行基盤: Claude Code subagent(harnessのsystem prompt・ツール一覧が付く) → API直呼び出し(system promptなし、ツール無し)。「道具を使ってはいけない」の依頼文は残るが、API直呼び出しでは道具が存在しないため§C(ii)事後監査は不要(代わりに request/response 全文を保存)。
2. 同一モデルでも thinking/effort 設定が異なる可能性(Trialは未確認、APIはProvider既定)。
3. Trialの「(d) Bash経由の返答書込み9/20本」はAPIでは起こり得ない(利点)。

## 4 評価設計

### 4-1 比較対象とスクリプト(実装済み、確認済み)
- `OUT/annot_eval.py`: 位置合わせは既存`align_md`(原文オフセット上のタグ位置)を再利用。LLM不使用。`selftest`: GT 9テーマで「GT=候補 → F1=1.0・class一致1.0」「中核タグ1個削除を検出」「本文1字改変を検出」を確認(**ALL_PASS、確認済み**。`annot_eval_selftest.json`)。
- `OUT/annot_driver.py replay`: 既存Trial返答(reply.md)を `extract → 単独check → merge → 評価` に通し、**9テーマ全てで統合結果がTrialのfinalとbyte一致**(`merged_equals_trial_final=True` 9/9、F1=1.0)、inbound_tourismはA/Bとも単独FAIL(Trialと同じ)を再現(確認済み、`replay_result.json`)。→ Phase 2のAPI応答を同じ関数(`pipeline_one`)に通せば、Trialと同一のgateで判定できる。

### 4-2 指標(各候補出力 × GT)
| 指標 | 定義 | 備考 |
|---|---|---|
| 本文非改変率 | `align_md`が通る(許可挿入以外の差分なし)出力の割合 | 目標100%。ハードゲート |
| 単独check PASS率 | `chk.run` verdict=PASS の割合(初回 / 1回再試行後) | 再試行は元応答も保存 |
| 【事実N】境界 precision/recall/F1 | 原文オフセットが一致したタグ集合で比較 | 分割位置を比較 |
| 【中核数値】/【周辺数値】 P/R/F1 | (オフセット, 種別) 完全一致 | 種別別 |
| 数値位置のみ一致 F1 | 種別を問わず印の有無だけ | 付け漏れ/過剰付与の分離 |
| 中核/周辺 分類一致率 | 位置が一致した印のうち種別が一致した割合 | c checkのPASS下ではクラスは構造的に整合するため、不一致は「どの表記を印対象にしたか/conceptの束ね方」由来 |
| Fact ID対応一致率 | 位置が一致した【事実N】どうしで`ledger_ids`集合が同一の割合(サイドカー) | |
| 安定性 | 同一入力・同一モデル2反復の(i)統合注記版の完全一致率、(ii)タグF1 | M-Aは反復間A同士、M-Bは統合後同士 |
| 費用・latency | 実測usage × 登録単価、応答時間 | `thinking`/reasoningトークンを別掲 |
| failure mode分類 | §3-2の失敗モード(1)〜(10)に分類し件数集計 | |
- 評価単位は記事。9テーマは全て1記事。メタ(中核0件)は中核/周辺のF1を算出不能として除外し件数を併記。
- 評価は決定論スクリプト + 人間確認用の**差分一覧**(GTと候補の注記版を行単位で並べ、差分タグを一覧化)。差分は全件を出力し、人間(ユーザー/Fable)が3テーマ以上を目視する(GTが人間正解でない以上、候補がGTより良い場合もある)。差分一覧スクリプトはPhase 2で`annot_eval.py`に追加する(Phase 1では未実装)。

### 4-3 成功基準案
`PREREGISTRATION_01.md` 6節に事前登録案として記載(確定はFable/ユーザー)。

## 5 費用見積

根拠: 実測サイズ(`OUT/estimate_01.json`、スクリプト `OUT/estimate_01.py`)。1呼び出しの入力 = 依頼文(Trialプロンプトから前置き約700字を除く)で**平均 約15.1k字**(最小約12.5k〜最大約21k)、出力 = 返答 平均 **約3.5k字**(最小1.1k〜最大6.6k)。**tokens/char比とreasoning tokensは未確認の仮定**(low=0.5 tok/字・reasoning 0、mid=0.75・3,000、high=1.0・8,000)。キャッシュ割引は見込まない(安全側)。為替 USD/JPY=160(`flagger_lib.USD_JPY`と同値)。

呼び出し数: 10テーマ(GT 9 + inbound_tourismのストレス入力) × 反復2 × {A,B} = **40 call/モデル**(M-AとM-Bで共有)。M-Cは新Prompt前提で A のみ 20 call(入力+15%仮定)。

| モデル | 方式 | call | low | mid | high |
|---|---|---|---|---|---|
| claude-sonnet-5 | M-A/M-B共有 | 40 | JPY 207 | JPY 503 | JPY 927 |
| gpt-6.1-sol | M-A/M-B共有 | 40 | JPY 207 | JPY 503 | JPY 927 |
| gpt-6-astra | M-A/M-B共有 | 40 | JPY 1,036 | JPY 2,514 | JPY 4,632 |
| 上3モデル合計 | | 120 | JPY 1,451 | JPY 3,520 | JPY 6,485 |
| sonnet-5 + sol のみ | | 80 | JPY 414 | JPY 1,006 | JPY 1,853 |
(sonnet-5とsolは同単価のため同額。厳密な値は `estimate_01.json`。出典: sonnet-5=xm_prices_01.json 取得2026-10-10 04:50Z、sol/astra=`pricing_snapshot.json` OFFICIAL_PRICING_PAGE_FETCHED、いずれも確認済み。`claude-sonnet-5-5`単価・Opus単価・Responses API/Anthropic APIの再取得は未確認。)
- 1記事あたり(2反復・A+B=4 call・1モデル)の目安: mid 約JPY 50(sonnet-5/sol)。Production相当(1記事1回・M-B 2 call)は mid 約JPY 25(仮定込み。実測で置換)。
- 再試行は上限1回。FAIL率によっては+最大40 call/モデルを見込む(最大 +JPY 927/モデル[high])。
- 推奨Phase 2 Cap案: **JPY 3,000**(sonnet-5 + sol の high JPY 1,853 + 再試行余裕。実測で超過しそうなら停止)。astra追加は別途Fable判断(全量は high JPY 4,632 でCap超過。9テーマ×1反復×Aのみに縮小すると約JPY 1,040[high]/約JPY 565[mid])。
- 無料の事前作業(Phase 2前): models list による model_id 実在確認(`claude-sonnet-5` と `claude-sonnet-5-5` の関係を含む)。

## 6 推奨方式とFable判断が必要な点

### 6-1 推奨(Phase 2案)
1. **M-A と M-B を同じAPI呼び出し(A,B各2反復)で評価**(新Prompt不要・Trial逐語・追加費用最小)。M-Bが本命(Trialと同一構成)、M-AはM-Bの簡略版の可否を測る(「未検証の簡略方式へ勝手に置換」しないため、M-AがGTに届いても**Production候補にするのはM-Bの結果と併記した上でのユーザー判断**)。
2. モデルは **`claude-sonnet-5`(Trial同系列)+ `gpt-6.1-sol`(別系列。A/B誤り相関に対するcross-model参照)**。astraは任意の上限確認(縮小実施)。
3. M-C/M-Dは新Prompt必須のため、M-A/M-Bの結果(特に本文改変・クラス誤りの失敗率)を見てから別Phaseで検討(USER_DECISION)。

### 6-2 Fable/ユーザー判断が必要な点
- **U-1 方式選定**: M-A/M-B(逐語)のみでPhase 2を行うか。M-C(構造のみLLM+決定論挿入)の新Promptを先に設計させるか。
- **U-2 モデル**: sonnet-5 + sol で良いか。astraの扱い。`claude-sonnet-5` と `claude-sonnet-5-5` の同一性確認(無料)を先に行うか。Opus系の追加(価格未確認)。
- **U-3 末尾追記(a)(b)の扱い**: Trial実プロンプトは仕様 + 全テーマ共通の末尾追記を含む。(a)は規則の記録単位化、(b)はhormuz固有例を含む。Phase 2は**Trial実プロンプト(末尾追記込み)を逐語**で使う案を推奨。Productionでは(a)(b)を仕様本体へ取り込むv2.1が必要になり、これは仕様変更(sha変更・再検証)。
- **U-4 成功基準と費用Cap**: PREREGISTRATION 6節の閾値案とCap JPY 3,000案の確定。
- **U-5 GTの人間確認**: GTは人間の正解ではない。差分一覧の目視を何テーマ・誰が行うか。
- **U-6 inbound_tourism**: GTなし。ストレス入力(check-onlyで使う)で良いか、除外か。検査scriptの`ID_RE`欠陥は修正せず(§J)。
- **U-7 Production前提**: Production側で(i)B3の書式(Selected Facts箇条書き)が保証されるか、(ii)台帳の`numeric_value`/`date_or_period`欄が出力されるかは**未確認**(本Trialの範囲外。確認なしにProduction採用を判断しない)。

### 6-3 STOP条件の判定
- 注記仕様v2の正本: 特定できた(1-1)。
- Ground Truth: 9/10テーマで完備(inbound_tourismのみ欠落、理由と対処案を明記)。「GTが揃わない」の全面STOPには該当しない(ただしテーマ数が指示文の8とは異なる点を報告)。
- 逐語移植で自動化が成立するか: M-A/M-Bは**逐語で成立**(dry-runで60 payloadの出所検証PASS、既存返答のreplayでTrial finalを9/9再現)。新Promptは不要。M-C/M-Dのみ新Prompt必須 = 追加案としてUSER_DECISION候補に記載。STOPではない。
