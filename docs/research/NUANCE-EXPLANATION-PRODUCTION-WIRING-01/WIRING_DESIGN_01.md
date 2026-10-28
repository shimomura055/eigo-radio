# WIRING_DESIGN_01 ニュアンス解説 Production配線設計(NUANCE-EXPLANATION-PRODUCTION-WIRING-01 委任_01a)

Status: 設計(実装前・Productionコード変更0・API 0)。仕様の正本=ユーザー原文 `docs/pm/delegation_log/2026-10-29_NUANCE-EXPLANATION-PRODUCTION-WIRING-01_USER.md` §2(APPROVED_FOR_PRODUCTION)。現状は `CURRENT_STATE_01.md`、テスト計画は `TEST_PLAN_01.md`。
§3(候補JSON schema)は先行確定済み(commit 8f342a700)。以後は**追加のみ**(§3.3)で、既存フィールド名は変えない。並行01bの暫定schemaと差が出た場合は01b側 `PROMPT_TRIAL_01.md` に差分が明記される。

## §1 仕様A〜Eと設計の対応

| 仕様(ユーザー原文) | 設計での担保 | 節 |
|---|---|---|
| A-1 記事・レベルごと最大1件 | 候補JSONの`candidate`は0または1件(schema上で配列にしない)。HR・確定・表示とも単数 | §3,§6 |
| A-2/A-3 学習価値のある内容、KP・Word・文法と同じHR | 候補をKP/文法と同じ待機点(rc=4が1回)・同じフォーム・同じ確定コマンドに載せる | §6,§8 |
| A-5/A-6 採用時のみ独立コーナー、他は見出し・空枠含め非表示 | 表示は`nuance_result.status=="ADOPTED"`のときだけブロックを出力。それ以外は空文字 | §7 |
| A-7 代替の自動補充なし | 不採用・NG・候補なしのとき、同一levelで再生成・次点繰上げをしない(再生成は本文/KP候補poolが変わった場合の「同じ1件枠の作り直し」だけで、人間のNG/不採用後は行わない) | §8,§9 |
| B 主題(学習上の焦点)重複NG・HR確定後の最終確認・HR提示前に品質確認 | 2段重複判定(構造+LLM)をHR提示前に実行し、HR確定時とfinalize時に決定論で再確認 | §5,§8 |
| C 文法0件はコーナー全体非表示 | `compose_study_html`で文法ブロックを`status!="SELECTED"`のとき出力しない。検査側は「期待ブロック数」を0/1にする | §7 |
| D HR統合・再生成/再開で確定判断を保持 | `cmd_from_form`に採否を追加(既存項目は不変)。sidecar+`confirmation_id`で保持 | §6,§9 |
| E X/Y/Z全level、retry/fallback/regeneration/resume、既存公開記事は再生成しない | 共通module1つ+3runnerの薄い接続。`nuance_spec`マークで新規runのみ有効(遡及なし) | §4,§9,§11 |

## §2 全体フロー(1 level の時系列。Std/Advは別々に同じ流れ)

```
[本文確定] -> [KP/Word候補生成(既存)] -> [文法Top1/Top2候補+事前生成(既存)]
      -> (N0) nuance_spec.json マーク発行(新規run・KP未確定のときだけ)
      -> (N1) ニュアンス候補生成 + 重複判定2段(本設計。HR提示前)  -> nuance_candidate.json
      -> [統合HR依頼書 review_request.md / rc=4 待機]  (KP+Word+文法+ニュアンスが1回)
      -> フォーム(V3)で人間が選定+ニュアンス採用/不採用  -> 照合コード付きコピー(AIF2)
      -> confirm --from-readable -> cmd_from_form
           (N2) 確定時の最終重複確認(API 0)  -> confirmed_nuance.json(sidecar) + 確定レコード
      -> 制作コマンド再実行(resume)
      -> (N3) finalize(LLM 0): nuance_result.json (+ nuance.md) 
      -> [Part 1 -> 文法 -> ニュアンス] を compose_page_html で合成 -> ページ検証(期待ブロック数)
```

N0〜N3のLLM呼出はN1のみ(生成1+判定1)。N2・N3は決定論(API 0)。

## §3 ニュアンス解説 候補JSON schema (v1・先行確定)

1記事×1レベルにつき `nuance_candidate_<family>_<article>_<level>.json`(Production内の実体は`<study_dir>/nuance_candidate.json`、§4)を1ファイル。候補は0〜1件(`candidate` が null なら候補なし)。

```json
{
  "schema": "nuance_candidate_v1",
  "family": "X|Y|Z",
  "article_id": "string",
  "level": "standard|advanced",
  "generated_at": "ISO8601",
  "candidate": null,
  "no_candidate_reason": "string|null",
  "kp_word_basis": {"status": "confirmed|provisional", "items": ["expr1", "..."], "source_path": "string"},
  "model": "string",
  "prompt_sha": "sha256 hex of the full prompt template",
  "usage": {"input_tokens": 0, "output_tokens": 0, "cost_jpy": 0.0}
}
```

`candidate` が非nullのとき:

```json
{
  "expression": "英語表現(例: 'quite' vs 'rather')。解説の中心的な学習対象",
  "focus": "学習上の焦点を1行(日本語)。重複判定の主入力",
  "explanation_ja": "日本語解説(Part 1の1項目相当、目安120〜260字)",
  "quote_en": "本文からの英語引用(逐語。本文に実在すること)",
  "quote_ja": "quote_enの和訳",
  "overlap_check": {
    "verdict": "pass|fail",
    "stage1_structural": {"verdict": "pass|fail", "matched": ["..."]},
    "stage2_llm": {"verdict": "pass|fail|skipped", "reason": "string", "model": "string"},
    "reason": "最終判断の理由(日本語1〜2文)",
    "against": [{"item": "KP/Word表現", "kind": "kp|word", "same_focus": false, "note": "string"}]
  }
}
```

規則:
- `overlap_check.verdict == "fail"` の候補はHR提示前に破棄し、`candidate=null`・`no_candidate_reason="overlap_ng"`にする(代替の自動補充なし)。破棄前の候補は `rejected_candidate_audit`(別キー、HRには出さない)に監査用に残す。
- `against[]` は比較したKP/Word全件(最大5件)を列挙する。
- 01bの暫定schemaが異なる場合は、フィールド名の差分を01bのPROMPT_TRIAL_01.mdに明記すること。

### §3.3 Production用の追加フィールド(v1互換・追加のみ。01bのTrialでは省略可)

| 追加キー | 位置 | 内容 |
|---|---|---|
| `text_sha256` | 最上位 | 生成に使った当該level本文の sha(`er119.sha256_text`と同一算式)。本文変更検出(STALE) |
| `kp_word_basis.candidates_sha256` | 最上位`kp_word_basis` | 比較に使ったKP/Word候補doc(`kp_candidates.json`)の`candidates_sha256`。reselect等で候補集合が変わった検出 |
| `kp_word_basis.provisional_ids` | 同上 | 暫定選定(`rv.auto_select`の結果=AI推奨のvocab最大5件)の`candidate_id`。重複判定の「必須NG対象」 |
| `kp_word_basis.pool_ids` | 同上 | 比較した提示pool全件(KP/Word候補<=12件 + 文法Top1/Top2)の`candidate_id`と`kind`(`kp`/`word`/`grammar`) |
| `candidate.focus_terms[]` | `candidate` | 解説の中心的な学習対象の英語表現(主表現+対比される表現。構造判定の入力。例 `["quite","rather"]`) |
| `candidate.pool_conflicts[]` | `candidate` | 暫定選定ではないが「同じ焦点」と判定された提示pool項目の`candidate_id`(**HRで人間がそれを選ぶと採用不可**になる。§5) |
| `candidate.candidate_sha256` | `candidate` | `expression/focus/explanation_ja/quote_en/quote_ja/focus_terms`の正規化jsha。HR提示・確定の照合キー(文法の`explanation_sha256`と同型) |
| `status` | 最上位 | `NO_CANDIDATE`/`CANDIDATE`/`FAILED_TECHNICAL`(§4。`candidate`の有無と`no_candidate_reason`と整合) |
| `level_key` | 最上位 | Production内部のlevelキー(`a2`=Standard / `b1b`=Advanced。`level`の表示名との対応)。`study_dir_for`/`level_name`と同一規約 |
| `rejected_candidate_audit` | 最上位 | 重複NGで破棄した候補全文+`overlap_check`(監査用。HR・ページには出さない) |

`kp_word_basis.status`は`provisional`(HR前の暫定+pool全体)が常態。HR確定後の値は`confirmed_nuance.json`側(§6)に`confirmed_against`として記録する(候補JSONは書換えない)。

## §4 (a) 生成段: X/Y/Z共通 module `er134_nuance_explanation_01.py`

- 名前: `er133_*`は使用済み(`er133_report_marks_01.py`)のため`er134_nuance_explanation_01.py`を提案(着手時に再確認)。Family A/B/Cからimportしない(`er119_isolation_test_01.py`のALLOWEDにこのmoduleを追加。§11)。
- 配置(artifactは文法と同じ`study_dir`、`er120_part2_wiring_01.study_dir_for`:70を再利用): `nuance_spec.json`(マーク) / `nuance_candidate.json` / `nuance_failed.json`(技術失敗) / `confirmed_nuance.json`(HR確定sidecar) / `nuance_result.json`+`nuance.md`(finalize結果)。
- 公開API(全て`level`必須・既定値なし、`er120`と同規約):
  - `ensure_spec(study_dir, *, level, kp_dir)`: **N0**。新規run(当該levelのKP確定レコードがliveでない、かつ`nuance_spec.json`が無い)のときだけ`{"spec":"nuance_v1"}`を発行。既存run(KP確定済み・マーク無し)は`LEGACY`=ニュアンス全工程を無効(生成0・待機0・表示0。`display_spec`の遡及なし規則と同型、`er128.display_spec_of`:483)。
  - `candidate_stage(study_dir, *, level, family, slug, article_id, paragraphs, kp_cands, grammar_doc, call_fn=None, judge_fn=None, client=None, budget_guard=None)`: **N1**。入力=当該level本文+KP/Word提示pool+暫定選定+文法Top1/Top2。候補0〜1件を生成→重複判定2段(§5)→`nuance_candidate.json`保存。resume(`text_sha256`・`candidates_sha256`・`prompt_sha`一致)はAPI 0で再利用。
  - `confirm_check(study_dir, *, kp_rec, grammar_selected_ids, decision)`: **N2**。決定論。確定時の最終重複確認(§5.3)。
  - `finalize_stage(study_dir, *, level, paragraphs)`: **N3**。決定論・**LLM 0**(引数にLLM関数を持たない)。`confirmed_nuance.json`から`nuance_result.json`/`nuance.md`を組立。
  - `require_final(study_dir, paragraphs, *, level, next_command, where)`: 使う側の入口(未確定=NuanceNotConfirmed[rc=4]、本文不整合/改変=NuanceStale[STOP rc=3]、LEGACY/NO_CANDIDATE/REJECTED=表示なしの結果)。
  - `render_markdown(result)` / `render_html_block(result, include_css)`: 採用時のみ非空。
  - `form_nuance_bundle(study_dir, *, level)`: フォームexporter用データ(§6)。
- モデル: **本番ライン既定**。`routing.SUPPORT_MODEL`(gpt-6-luna、`er120_part2_grammar_production_01.py:40`・`er003_kp_general_explanation_01.py:32`と同一)。新routing processを`er006_model_routing_contract_01.py:130`付近の`PROCESS_MODEL_MAP`へ登録(`NUANCE_EXPLANATION`、`NUANCE_OVERLAP_JUDGE`)。応答modelが違えばfallbackせずSTOP(`er003_kp_general_explanation_01.py`と同じ契約)。Charter 25節: 本番ラインのモデル選定は評価用途の最新原則とは別判断(01b Trialも同モデル)。
- **Prompt方針**(Trial Part 3を素材にしつつ、過去Promptを無検証採用しない。確定Promptは01bの結果を受けてFableがレビュー):
  1. **役割分担の明示**: Part 1=表現そのものの一般的な意味・用法・コロケーション・類義語との違い(文脈非依存、`er003_kp_general_explanation_01.py:41-53`)、Part 2=文の構造、ニュアンス解説=**この本文の文脈で、その語・言い回しが選ばれたことで生じる語感・印象・近い別表現との差**。KP/Word(Part 1対象)の表現の一般解説、文法解説(Part 2対象文の構造)は扱わない。
  2. **焦点の明示**: 出力に`focus`(1行)と`focus_terms[]`を必須化し、焦点を先に決めさせる。
  3. **KP/Wordとの差別化を生成時に指示**: 提示pool全件(`provisional`印付き)と文法Top1/Top2を入力に載せ、「これらを主題・対比の中心にしない。文中に登場するのは可」と明記。
  4. **価値なしなら0件**: 「基礎的な品詞/語法の比較(例 worthy of/worth)、物語の解釈・感想、一般論は不可」「適切な候補がなければ`candidate:null`と理由」。Trial-01〜04のFable評価(`FABLE_EVAL_01.md:8` Part 3=弱)の弱点を指示に反映: (i)品詞差など基礎的で学習価値が低い、(ii)「0個でもよい」より「1つ選ぶ」へ寄る、(iii)物語解釈寄りになる(`EVAL_02.md:40`)。内部で複数案を検討して**最良の1件だけ**出力させる(出力は1件のみ)。
  5. **引用は本文逐語**: `quote_en`は本文に実在する1文以内(決定論で検査し、不一致は技術失敗として1回retry)。
  6. 日本語解説(120〜260字目安、Part 1の1項目相当)。Part 4(Think & Express)・複数テーマ・質問は**入れない**(未承認、ユーザー原文§3)。
- 技術失敗の扱い: 構造不正(JSON/必須キー/引用不一致)は技術retry1回(Part 1と同じ上限、`er003_kp_general_explanation_01.py:307-349`)。それでも不正=`status=FAILED_TECHNICAL`・`nuance_failed.json`を書き**候補なし扱い(非ブロッキング)**で制作を止めない(ニュアンスは任意機能。ただし最終レポートに明記し、`--regenerate-stage nuance_cand_<lv>`で再実行可)。**model契約違反・予算超過・STOP通知はSTOP**(既存安全装置を迂回しない)。

## §5 (b) 主題重複判定(2段)と最終確認

### §5.1 比較対象
- **必須NG対象**=選定済みKP/Word(最大5件)=区分①+②(vocab)。HR前は**暫定選定**(`rv.auto_select`:577の結果、AI推奨のvocab最大5件)。
- **助言対象(pool)**=暫定選定以外のKP/Word提示候補(<=12件のうち)+③候補+文法Top1/Top2。同じ焦点と判定されたものは`pool_conflicts`に記録(§5.3でHR結果と突合)。
- 文法Top1/Top2を含める根拠: ユーザー原文§3「役割の重複を防ぐ」・§2D。Part 2の節「意味・ニュアンス・表現効果」(`er120_part2_grammar_production_01.py`の`EXPLANATION_REQUIRED`)と同じ内容を教える候補を防ぐ。判定規則はKP/Wordと同一。

### §5.2 N1の2段判定(HR提示前、決定論+LLM)
- **Stage 1 構造**(API 0): `candidate.focus_terms[]`を正規化(小文字化・所有格/`one's`等の置換・屈折の簡易正規化)し、比較対象各項目の`used_form`/`display_phrase`/`key_phrase`と
  (i)完全一致、(ii)語列としての部分一致(片方が他方の連続部分列。`er119_kp_human_review_01.phrase_key`:164・`used_form_key`:174・`_is_subseq_tokens`:180を再利用)を調べる。**必須NG対象と一致→fail**。pool項目と一致→`pool_conflicts`に追加(failにはしない)。文字列一致は必要条件に過ぎず、これで通っても焦点は別途Stage 2が判定する(ユーザー原文§2B「文字列一致ではなく学習上の焦点」)。
- **Stage 2 LLM**(1 call・生成とは別の独立call・別Prompt): 入力=候補(`expression`/`focus`/`explanation_ja`)と比較対象全件(表現・日本語訳・kind・暫定印)。**生成側の自己評価は渡さない**(独立性)。各項目に`{same_focus:bool, reason}`を返させる。判定定義(Promptに固定): 「解説の中心的な学習対象・論点が同一、または表現が違っても実質同じ内容を教える」=same_focus true。「解説文中に当該表現が登場するだけ・焦点が明確に別」=false。**必須NG対象で1件でもtrue→fail**。pool項目のtrue→`pool_conflicts`。判定不能(JSON不正が2回)→安全側でfail(候補は`FAILED_TECHNICAL`ではなく`overlap_unverified`として破棄、HRに出さない)。
- failなら`candidate=null`(`no_candidate_reason="overlap_ng"`)、破棄候補は`rejected_candidate_audit`へ(§3)。**同levelで次点を探す再生成・自動補充はしない**(仕様A-7)。生成Promptが提示pool全件を避けるよう指示するので、failは稀であることが期待される(01b Trialで実測)。

### §5.3 HR確定後の最終確認(N2: `confirm_check`、API 0)
`cmd_from_form`(または`nuance-select` CLI)の確定コミット前に全て検証し、1つでも不一致なら**ISSUE(rc=4)で何も保存しない**(`er128.raise_issue`:355型):
1. 提示された候補の`candidate_sha256`が現在の`nuance_candidate.json`と一致、かつ`kp_word_basis.candidates_sha256`が現在の`kp_candidates.json`のshaと一致(候補集合・本文が古いフォームでの採否送信を拒否)。
2. 候補の`overlap_check.verdict=="pass"`。
3. 人間が**実際に選んだ**KP/Word(①②)と文法の`candidate_id`集合に対し、`pool_conflicts`との交差が空(採用時のみ)。交差がある=「このニュアンス解説は選択した『X』と焦点が重複します。Xを外すか、ニュアンス解説を不採用にして再送信」。フォームUIも同じ規則で送信を止める(§6)。
4. 実際に選んだ①②の`used_form`/`display_phrase`/`key_phrase`に対する**Stage 1構造判定を再実行**(確定集合は暫定と異なり得るため)。fail=3と同じISSUE。
5. 不採用(reject)は上記1のshaのみ確認し常に受理(人間判断を覆す検査はしない)。

LLM再判定をしない理由: 提示pool全件に対する`same_focus`はN1で全て算出済み(`pool_conflicts`+`against[]`)で、HR確定集合は必ずpoolの部分集合だから、確定後にLLMを呼ばなくても「確定結果を踏まえた最終確認」を満たせる(ユーザー原文§2B)。poolの外(reselectで新候補)が選ばれる場合は候補doc shaが変わるので1で検出し、N1を再実行する(§9)。

### §5.4 N3 finalizeでの再確認(API 0)
`finalize_stage`が`confirmed_nuance.json`の`confirmed_against`(確定時点のKP/Word・文法)を現在の確定レコード/文法sidecar(`er128.live_user_record`:224・`grammar_state`:934)と突合する。確定後にKP/Wordが変更(revoke→reconfirm、`cmd_revise`)された場合は`confirmation_id`不一致=STALE。

## §6 (c) Human Review 統合(V3フォーム・export・confirm)

既存KP/文法項目は**不変**(「必要な項目のみ追加」=ユーザー原文§2D)。

- **データJSON(`eigo_radio_selection_article_v1`)に任意キー追加**: `nuance_spec`: `{version:"nuance_v1", max_select:1, allow_zero:true, presented: true|false}`、`nuance`: 候補があるとき`{id, candidate_sha256, expression, focus, explanation_ja, quote_en, quote_ja, pool_conflicts:[candidate_id…], overlap_summary_ja}`、無いとき`nuance_note_ja:"ニュアンス解説の候補はありません"`。`nuance_spec`が無い記事(既存公開記事・LEGACY)は従来どおりで、フォーム表示・照合コード(`AIF1`)・payloadはバイト不変。
- **exporter**: `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py`(:13のとおり`--grammar-study-dir`と同型)に`--nuance-study-dir`を追加。`nuance_candidate.json`のshaが現在の候補doc/本文と不一致ならデータを出さずエラー(rc=4)。
- **フォームUI**(`user_test/selection_form_v3/index.html`+`form_logic.js`): 文法節の下に「ニュアンス解説(1件・採用/不採用)」節。ラジオ`採用`/`不採用`、既定は未決定。決定状態`adopt`/`reject`/`undecided`/`n/a`(`grammarDecision`:42と同型)。
  - `undecided`かつ候補あり→送信/コピーを止める(`grammarBlocked`:52と同型)。
  - `adopt`かつ選択中のKP/Word/文法が`pool_conflicts`に含まれる→送信を止め重複メッセージを表示(§5.3-3と同じ規則をJSでも実装。Python側が最終権威)。
  - 候補なし(`n/a`)→節は「候補なし」の1行のみ(フォームはHR作業画面であり公開ページではない。公開ページの空枠禁止とは別)。
- **人間可読コピー形式**(`COPY_FORMAT_01.md`の拡張): 文法の下に
  ```
  ニュアンス解説：採用 | 不採用 | 候補なし
  【ニュアンス全文】                      ← 採用/不採用時のみ(候補本文を逐語)
  <expression / focus / explanation_ja / quote_en / quote_ja>
  【ニュアンスここまで】
  ```
  照合コードは`AIF2-<stem>-<d6>-<c8>-<t8>-<s10>-<g10|0>-<m8|0>-<n8|0>-<k4>`(`n8`=ニュアンスの`candidate_sha256`先頭8桁と決定の組。候補なし=`0`)。`er128_form_readable_restore_01.py:48`の`CODE_RE`は`AIF1`/`AIF2`の両方を受理(`nuance_spec`の無いデータは従来の`AIF1`のまま出力・復元=バイト不変)。復元は候補本文をデータJSONと逐語照合(文法解説全文の`norm_body`:106と同じ規則)。**欠落・改変・決定の読み取り不能はfail-closed**(推測復元しない)。
- **payload**(`eigo_radio_selection_result_v2`、`schema_minor` 1→2): `selection.nuance`: `{decision:"adopt"|"reject", candidate_sha256, id}`、`nuance_status`。`schema_minor 1`のpayloadは従来どおり受理(ニュアンス無し=候補が無いrunのみ。候補があるrunで`selection.nuance`が無い=ISSUE rc=4「ニュアンス解説の採否が未回答」。**黙って不採用にしない**)。
- **確定**: `er128_kp_confirmed_content_01.cmd_from_form`(:1390)に`_validate_form_nuance`(何も書かない検証。文法の`_validate_form_grammar`:1503と同型。§5.3の1〜5)と、KP確定レコード保存(commit点)と同じロック内での`confirmed_nuance.json`書込みを追加。書込み順は既存の呼出順(検証→KPロック→文法review→sidecar→KPレコード保存)に**ニュアンスsidecarを文法sidecarの直後**へ挿入(commit点は変えない)。`--grammar-pending`(KP先行確定)時のニュアンスは、文法Top2との`pool_conflicts`があるため**文法確定後に確定する**(`cmd_grammar_from_form`:1645で併せて検証・書込み)。
- **`confirmed_nuance.json`**(`eigo_radio_confirmed_nuance_v1`): `{schema, level, decision:"adopted"|"rejected", candidate_sha256, candidate(逐語コピー=改変検出用), confirmed_against:{kp_word:[candidate_id…], grammar:[id…]}, final_overlap_check, confirmation_id(=KP確定レコードと同一), kp_dir_rel, by, user_ref, decided_at, text_sha256, sidecar_sha256}`。`er128.grammar_state`:934と同じ自己整合検査(sha・`confirmation_id`・level)をnuance版で実装(`nuance_state()`)。
- **フォームを経由しないHR面**(文法の`grammar-select` CLIと同じ位置づけ): `py er119_kp_human_review_cli_01.py nuance-show|nuance-select --run … --level … --choice adopt|reject --candidates-sha … --by … --user-ref …`。KP確定レコードがliveでないと拒否(`confirmation_id`で結び付けるため)。確定済みの変更は`revoke`経由のみ(`guard_grammar`:1170と同型の`guard_nuance`)。
- **統合依頼書**: `er119_kp_wiring_01.write_unified_request`:121 / `pending_banner`:130に`kind="nuance"`を追加(「KP+文法」→「KP+文法+ニュアンス」。rc=4は引き続き1回)。

## §7 (d) 表示: 独立コーナー + 文法0件の完全非表示

合流点は1か所(CURRENT_STATE §1-1): `er120_part2_wiring_01.compose_page_html`:507 -> `er120_part2_grammar_production_01.compose_study_html`:1449。署名を`compose_study_html(part1_html, result, nuance=None)`に拡張(`nuance`未指定=従来呼出を壊さない)し、3ブロックを順に連結する。

| 状態 | 出力 |
|---|---|
| Part 1 | 既存どおり(空のこともある)。変更なし |
| 文法 | `result["status"]=="SELECTED"`のときのみ`render_html_block`。**それ以外は空文字**(見出し・空`<section>`・`ZERO_P2`・プレースホルダーを出さない)。候補なし/全件不採用/該当構文なし/ユーザー省略のすべて |
| ニュアンス | `nuance["status"]=="ADOPTED"`のときのみ`<section class='study'><h3>Nuance &amp; Deeper Understanding</h3>…</section>`。不採用・候補なし・LEGACY・技術失敗・SUPPRESSED=空文字 |
| CSS | 最初に非空になったブロックが`STUDY_CSS`を持つ(従来の`include_css = not part1_html`を3ブロックに一般化)。3つとも空なら全体が空文字(CSSも出さない) |

- 見出し名の注記: 既存見出しは英語(`Vocabulary & Expressions` / `Grammar & Sentence Structure`)。ユーザー原文は「ニュアンス解説」(独立コーナー名)で英語見出しの指定はない。Trial由来の`Nuance & Deeper Understanding`を採る(「Part 3」の番号は出さない: `render_markdown`の注記どおりPart 3/4未採用の番号参照=Dangling防止)。見出し文言は軽微事項で、実装前にFableが別名にしても配線に影響しない(§13-3)。
- 本体の描画: 採用時のみ。`expression`見出し/`focus`(1行)/`explanation_ja`/`quote_en`(`>`引用)+`quote_ja`。LLM出力はHTMLエスケープ後に`**`→`<b>`(`er120.render_html_block`:1430の規則・`er003._paragraphs_html`を再利用)。
- **検査側の変更**(文法0件の非表示と同時に必要。これを落とすとSTOPになる):
  - `verify_selection_matches_outputs`:1368の「文法ブロックがちょうど1個」→「`expected_grammar_blocks(result)`個(SELECTED=1、他=0)」。`count_grammar_blocks`:1962は維持し、新`count_nuance_blocks`(`<h3>Nuance &amp; Deeper Understanding</h3>`)を追加。節内に空`<section class='study'>`が無いことの検査(`count_empty_study_sections`)も追加。
  - Y `_verify_part2_outputs`(er121:1031、`n2 != 1`:1049-1051)・Z(er026:1843、:1861-1863)・X player検査(er019:4114)・`public_study_html`(er120_part2_wiring:518)を同じ関数へ集約(期待値の分散をやめる)。
  - `render_markdown`:1415は0件で空文字を返し、`write_artifacts`/`write_md`は0件のmdを書かない(内部artifactでもプレースホルダーを残さない)。`verify_outputs`(wiring:432)はmd不在を0件で許容。
- 公開済み記事の静的ページ(AI島等)は触らない。再構築したときだけ新規則が適用される(§9)。

## §8 (e) 順序と各時点の状態

| # | 時点 | ニュアンスの状態 | LLM |
|---|---|---|---|
| 1 | KP/Word候補+文法Top2事前生成の完了 | (前提) | 既存 |
| 2 | N0マーク発行(新規runのみ) | `SPEC_ISSUED` | 0 |
| 3 | N1生成+重複判定 | `CANDIDATE`(0〜1件)/`NO_CANDIDATE`/`FAILED_TECHNICAL` | 生成1+判定1(候補ありのときのみ判定) |
| 4 | HR待機(rc=4) | 候補ありなら`PENDING_DECISION`(統合依頼書とフォームに載る) | 0 |
| 5 | 人間が選定+採否 → `cmd_from_form`でN2検証→sidecar+確定レコード | `ADOPTED_CONFIRMED`/`REJECTED_CONFIRMED`。N2不一致=ISSUE rc=4(何も保存しない) | 0 |
| 6 | 再実行(resume)→N3 finalize | `nuance_result.json`(`ADOPTED`/`REJECTED`/`NONE`/`SUPPRESSED`) | 0 |
| 7 | ページ合成+検証 | ADOPTEDのみ表示 | 0 |

不在宣言(`declare-absent`)でKPが`UNREVIEWED_AUTO_ADOPTED`になるrun: 人間の採否が無いので**ニュアンスは生成しない・採用しない・表示しない**(`nuance_candidate.status=NO_CANDIDATE`, `reason="auto_adopted_no_human_review"`)。費用0。理由: 仕様A-4「Human Reviewで人間が採用/不採用を決定」、A-5「採用された場合のみ表示」。

N3で最終重複確認が失敗(N2通過後に確定集合が変わった等)した場合: ニュアンスは`SUPPRESSED`(**非表示**、`final_overlap_check`に理由を記録、最終レポートに明記)。仕様B(最重要条件: 重複は表示しない)をD(確定判断の保持)より優先する保守側の解釈(§13-4)。本文変更で`quote_en`が消えた場合は、重複と無関係に確定済み判断を黙って捨てないため**ISSUE rc=4**(`stale_or_rebind`型、§9)。

## §9 (f) retry / fallback / regeneration / resume

| 事象 | 扱い | 根拠・既存機構との整合 |
|---|---|---|
| resume(同じコマンド再実行) | 候補(`text_sha256`・`candidates_sha256`・`prompt_sha`一致)と確定sidecarは再利用、API 0 | `ensure_kp_review`:1370・`pregen_stage`の再利用規則と同型 |
| ページのみ再構築(`--stages provision_shell,gate,assemble,pages,page_verify`等、`pages`再実行) | `nuance_result.json`+sidecarのみから決定論再合成。LLM 0、同一入力で同一HTML | Z完成段1起動規則(OPEN-480)。新LLM呼出が無いので`provision_shell`欠落のような再起動連鎖を作らない |
| KP外側retry/reselect(HR前〜HR中) | KP候補docのshaが変わると`kp_word_basis.candidates_sha256`不一致=STALE→次回待機点でN1再実行(旧候補は`nuance_candidate.<tag>.json`へ退避、削除しない)。**確定済みsidecarがあれば再生成しない** | `rv.RESELECT_MAX`=2(最大2回再生成=費用上限が明確)。reselectは人間操作 |
| 人間が不採用/NG後 | 同level同候補セットで**再生成・次点繰上げしない**(A-7)。候補doc/本文が変わる別事象のときだけ新しい1件枠を作り直す | ユーザー原文§2A-7 |
| 本文変更(Local Rewrite・text/translate再生成) | (i)確定sidecarあり: `quote_en`が新本文に逐語で残る→API 0で`text_sha256`を再結合、残らない→ISSUE rc=4(`revoke`→再選択を案内)。(ii)未確定: 候補STALE→N1再実行 | `er128.stale_or_rebind`:765に`_nuance_sentences`(quote)を追加して同じ機構に乗せる |
| `--regenerate-stage nuance_cand_<lv>` | 確定前=許可(N1再実行)。確定後=`CONFIRMED_CONTENT_LOCKED`で拒否(revoke必須) | 文法のD4(er019:824 / er121:905 / er026:1745)と同型 |
| `--regenerate-stage kp_<lv>`/`part2_<lv>` | ニュアンス確定は保持(sidecar/`confirmation_id`は確定レコードに紐づく)。KP確定レコードがrevokeされた場合のみ`confirmation_id`不一致=STALE→reconfirmで再判断 | `confirmed_grammar.json`の`confirmation_id`照合(er128:934-)と同型 |
| fallback(モデル/経路) | N1は`routing.require_model`契約。fallbackしない、応答model不一致はSTOP | `er003_kp_general_explanation_01.py:307-349` |
| 確定のrevoke→再確認 | 旧`confirmed_nuance.json`は`RECONFIRM_SUPERSEDED`タグで退避(削除しない)。新`confirmation_id`で再判断 | `_archive_prior_grammar_files`:1601と同型 |
| copy-run | sidecarは`kp_dir_rel`(相対path)で確定レコードを辿るため移動に強い | `_write_grammar_sidecar`:1609 |
| Y/Z provenance | 新unit `nuance_cand_<lv>`(親=`translate_<lv>`相当の本文stage)と`nuance_<lv>`(finalize、子)を`UNIT_NAMES`/`DEPENDENTS`(Y: er121:43-56)・`PART2_STAGES`相当(Z: er026:1675)へ追加。X(ledgerなし)はfile存在+shaで判定 | 来歴の入力shaはmarkerのみで凍結(`cand_marker`:106と同型。確定後にモデル/Prompt変更しても再抽出しない) |
| 既存公開記事 | `nuance_spec.json`が無い=LEGACY: 生成0・待機0・表示0。ページを再構築した場合のみ「文法0件の非表示」(仕様C)が適用される。**公開済みページの再生成・差替えはしない** | ユーザー原文§2E |
| provenance(来歴記録) | `nuance_result.json`に`candidate_sha256`・`confirmation_id`・`model`・`prompt_sha`・`generated_at`・`decided_by/at`・`user_ref`・`final_overlap_check`を保持 | 監査用。受入時の発火証拠に使う |

## §10 (g) 費用(1記事セット=Std+Adv、モデルは本番既定gpt-6-luna)

- 01bの実測(`results_v1.json` ai_island_std 生成call): input 1,990 / output 632(reasoning 314)tok、約0.082円。Trial Part 3の設計推定は0.10〜0.14円/call(`FAMILY-Z-STUDY-TEXT-TRIAL-01/DESIGN_04.md`:55-62)。
- 本設計の増分見積(level当たり): 生成0.08〜0.14円 + 独立判定call(入力~1.2k+短い出力)0.03〜0.07円 = **0.11〜0.21円/level → 0.22〜0.42円/記事セット(Std+Adv)**。70円目標比 約0.3〜0.6%。
- ユーザー原文§6の「+約0.10〜0.14円/記事セット」は**1level・1call・従来概算**。本設計はSt+Adv各1候補+HR提示前の独立判定を含むため、約2〜3倍(絶対額は小)。実測は実装後のruntime evidenceで確認(§6「実際の追加API費用を確認」)。
- 再生成ドライバ: reselect/本文変更でN1を再実行した場合はlevelごとに+0.11〜0.21円/回(`RESELECT_MAX`=2が上限)。確定後は再生成0。
- 削減案(Q非劣化のもの): (i)候補`null`のときは判定callを省く(実装済み設計)、(ii)AUTO採用runは生成しない、(iii)本文を先頭に置きprompt cacheを効かせる(cached input単価は1/10)、(iv)Std/Advの独立呼出を並列化(費用不変、時間のみ短縮)。**判定を生成callに統合する案は不採用**(自己評価は独立性がなく仕様B「HR提示前の品質確認」を満たしにくい=Q優先)。
- 開発費: 実装+Trialは別委任。runtime evidence(各Family×level 6経路、既存run再利用)の見積は`TEST_PLAN_01.md` §7。

## §11 (h) 変更ファイル一覧・影響範囲・A/B/C波及

### 新規
- `er134_nuance_explanation_01.py`(core) / `er134_nuance_explanation_01_test_01.py`(単体) / `er134_nuance_wiring_integration_test_01.py`(X/Y/Z×Std/Adv integration、mock LLM) / `er134_nuance_display_test_01.py`(DOM/HTML)

### 変更(Production)
| ファイル | 変更内容 | 備考(競合) |
|---|---|---|
| `er120_part2_grammar_production_01.py` | `render_markdown`:1415 / `render_html_block`:1430 / `compose_study_html`:1449 / `verify_selection_matches_outputs`:1357 / 新`expected_grammar_blocks`・`count_nuance_blocks`。`ZERO_P2`:161の撤去(§12) | Part 2のPrompt・閾値・選定規則・Step Bは**無変更** |
| `er120_part2_wiring_01.py` | `compose_page_html`:507 / `public_study_html`:518 / `verify_outputs`:432にnuance引数を追加(未指定=従来) | |
| `er128_kp_confirmed_content_01.py` | `cmd_from_form`:1390 / `cmd_grammar_from_form`:1645 に`_validate_form_nuance`・sidecar書込み、`cmd_revoke`の退避、`stale_or_rebind`:765にquote追加、`cmd_status`:1955に表示 | 保護項目`PROTECTED_ITEM_FIELDS`:88は不変 |
| `er128_form_readable_restore_01.py` | `CODE_RE`:48(AIF2)、`build_readable`:151、`restore`:285、`_build_payload`:447、`cmd_from_readable`:504 | `nuance_spec`無しデータはAIF1のまま |
| `er119_kp_human_review_cli_01.py` | `nuance-show`/`nuance-select`、`status`表示 | |
| `er119_kp_wiring_01.py` | `write_unified_request`:121 / `pending_banner`:130 に`kind="nuance"` | |
| `er019_family_x_audio_production_runner_01.py` | N0/N1呼出(`run_part2_candidates_x`:805の隣)、N3(`run_part2_final_x`:838の隣)、pending banner合流(:3925-3984)、player合成(:4082-4094)・検証(:4114) | **(I)JA-ASR配線がer019 listening page等を編集中**。本件は`er019_family_x_listening_page_01.py:161`を触らない(`public_study_html`内で完結) |
| `er121_family_y_runner_01.py` | `stage_kp`:614に`_nuance_cand_step`/`_nuance_final_step`、`UNIT_NAMES`:43/`DEPENDENTS`:46、`stage_pages`:1271(合成:1291)、`_verify_part2_outputs`:1031 | **(I)が1282付近を編集中**: 実装着手時にrebase。合成行(:1291)のみの最小差分にする |
| `er026_family_z_fiction_production_runner_01.py` | `stage_kp`:2195に同様、`PART2_STAGES`:1675隣、`stage_pages`:2613(合成:2638-2639)、`_verify_part2_outputs`:1843 | |
| `er006_model_routing_contract_01.py` | `PROCESS_MODEL_MAP`(:130付近)に`NUANCE_EXPLANATION`/`NUANCE_OVERLAP_JUDGE` | 単一定義点 |
| `user_test/selection_form_v3/index.html`・`form_logic.js` | ニュアンス節・状態・`validateArticle`・`buildReadable`・`makeCode` | `nuance_spec`無しデータは出力不変 |
| `docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py` | `--nuance-study-dir` | |
| テスト | §CURRENT_STATE 5の既存テスト期待値の是正+`er119_isolation_test_01.py`のALLOWED追加 | |

### 影響範囲
- 全て`level`単位。X/Y/Zの6経路は同じ共通moduleと同じ合成関数を通る。Familyごとの差は「stage ledgerの有無」「study_dirのパス」(`study_dir_for`で吸収)と接続行のみ。
- **A/B/C**: Part 1/Part 2/HR共通核・er128・form・新moduleをimportしない(`er119_isolation_test_01.py`:TestImportersAreOnlyXZRunners)。`sc.run_key_phrases`・`run_key_phrase_redundancy_qa`のsha固定testは無変更。新moduleはALLOWEDに追加するが、A/B/Cが参照する関数・定数・出力は変えない(互換確認のみ: 隔離test+A/B/Cのimport経路Grep)。
- 既存のKP/Word・Part 1・Part 2仕様: 選定規則・Prompt・閾値・解説生成・TTS・音声は変更なし。変更は「文法0件の描画/検査」「確定コマンドへの追加項目」「合成関数への引数追加」のみ。

## §12 (i) 撤去・残置要否

| 対象 | 判断 | 理由・確認方法 |
|---|---|---|
| `ZERO_P2`(er120 prod:161)+ HTML描画:1433-1436 + md:1420 | **撤去** | 文法0件を非表示にするため不要。撤去後に`ZERO_P2`をGrepして残存0を確認(テスト参照も是正) |
| `count_grammar_blocks == 1`の固定要求(er120 prod:1368、Y:1049-1051、Z:1861-1863) | **置換**(`expected_grammar_blocks`) | 0件=0個を期待。旧規則を残すと非表示のページが全てSTOPする |
| `render_markdown`の0件固定文面 | **撤去**(空文字) | 内部artifactでもプレースホルダーを残さない |
| テストが固定文面を期待する箇所(CURRENT_STATE §5) | **期待値是正**(旧期待値assertは書かない) | 不整合な出力を期待値にしない規則 |
| `AIF1`コード | **残置**(`nuance_spec`無しデータ用・読取互換) | 既存公開データの復元を壊さない |
| `compose_study_html(part1_html, result)`旧署名 | **残置**(`nuance=None`既定) | 既存呼出元を壊さない。X player/Y/Z/公開ページ全てに新引数を渡すことをtestで確認 |
| AI島等の既存公開ページの文法0件文面 | **残置**(静的ページ。再生成しない) | ユーザー原文§2E |
| 旧Trial Part 3/4 Prompt・スクリプト | **残置**(Trial履歴)。Productionから参照しない | Dangling Reference検査: Production moduleから`FAMILY-Z-STUDY-TEXT-TRIAL-01`・`run_trial_*`のimport/参照0をGrep |

## §13 (j) 判断候補の整理(停止根拠)

ユーザー判断が必要(分類D)な事項は**見つからなかった**。以下は分類付きの確認事項。

| # | 事項 | 分類 | 根拠(承認原文 file:line / 理由) |
|---|---|---|---|
| 1 | 「Key Phrase・Word(最大5件)」=区分①+②のvocab、③は非ブロッキング参考 | B(承認範囲内で自己解決) | ユーザー原文§2B「選定済みKey Phrase・Word(最大5件)」/`er119.SLOT_RULES`:63・`VOCAB_COUNT_MAX`=5/③は短い訳のみ(解説の焦点を持たない) |
| 2 | 文法Top1/Top2を重複判定対象に含める | B | 原文§3「独立コーナーとして追加し、役割の重複を防ぐ」。Part 2は「意味・ニュアンス・表現効果」節を持つ(INVESTIGATION_01 §3-C) |
| 3 | コーナー見出し文言(`Nuance & Deeper Understanding`) | B(軽微・変更しても配線不変) | 原文は日本語名「ニュアンス解説」のみ指定。既存見出しは英語 |
| 4 | N3最終重複確認の失敗は非表示(SUPPRESSED)、本文変更で引用消失はISSUE | B(保守側。Fableが別の優先順位にしても配線は同じ) | 原文§2B「最重要条件」>§2D「判断を失わない」と読む |
| 5 | 不在宣言(AUTO)runはニュアンス生成・採用・表示なし | A/B | 原文§2A-4,5(人間が採用を決定。採用時のみ表示) |
| 6 | 費用が原文の概算より増える(0.22〜0.42円/セット) | B(7-7: 承認Scope内・300円以下。70円目標の1%未満) | 原文§6「実際の追加API費用を確認」 |
| 7 | 既存公開記事の再構築時にだけ文法0件が非表示になる(遡及再生成なし) | A | 原文§2C,§2E |
| 8 | 新構造(新module+HR/フォーム拡張+表示契約変更)の設計 | PM規則(ユーザー判断ではない) | CLAUDE.md「Opus独立技術レビューGate 条件A」(PM_GOVERNANCE 11-3)。実装前にFableがOpusレビューを起票 |

## §14 実装フェーズ案(参考。実装は別委任・Opus条件Aレビュー後)

並列化(CLAUDE.md 8-X): ファイルが重ならない3トラックを並列、その後に接続。
- **Track A(表示・検査)**: er120/er120wiring の合成・検証変更、文法0件非表示、既存テスト是正。他と独立。
- **Track B(core)**: `er134`のPrompt/生成/判定/state/finalize/render(01bのPrompt結果待ち、Opusレビュー後)。
- **Track C(HR)**: form/export/restore/er128/CLI(Track Bの`candidate`スキーマ確定後でも、スキーマは§3で確定済みなので先行可)。
- **Track D(runner接続)**: A・B・C後。(I)JA-ASR・(M)Y統合のファイル競合を避け最後に最小差分で。
- **Track E(runtime evidence)**: 各Family×levelの正式経路。`TEST_PLAN_01.md` §7。
