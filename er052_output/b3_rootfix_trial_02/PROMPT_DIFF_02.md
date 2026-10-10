# PROMPT_DIFF(D-plus-single-call腕): Trial専用B3 Prompt(Productionとの差分。unified diff逐語。自動生成、委任_02)
- Production module sha256=93d0e31e735057ae874bbf27be48449fdd5bd5188e535b0a280eada9d314b758
- Trialコピー sha256=5ff0f5d0d53ab074d5edc061dae95c20f60c111600f88234719a96212c41737e
- 置換箇所(各ちょうど1回出現をassert): THEME_TAG, role_declaration+count, step2_storyline_role, step6_number_ranks, output_desc, important, schema_props, schema_required, shape_ledger, validate_sig, validate_body, validate_call, stop_attach_attempts_log
- 不変: DEVELOPER_MESSAGE / FACT_TEST_DEFINITIONS_JA / 手順1,3,4,5の文言 / 採用Fact数注意 / fact_tests・selected_fact_ids・selected_fact_brief・recheck_note の schema項目 / retry機構(1回のみ)。削除した既存手順・schema項目は無い。
- 追加: (1)【Ledgerの読み方】役割宣言(U1: 制約を選択の参考にしてよい旨は削除済み) (2)手順2末尾に「事実の記述だけ・指示を含めない」 (3)手順6 数値ランク(定義=b3r2_sepcall_01.STEP6_RULESと逐語同一) (4)出力説明とschemaにnumber_ranks(最後尾) (5)入力整形 shape_ledger_for_b3 (6)number_ranksの技術検証をvalidate_selection_outputへ追加(hard=未知/未選択fact_id・surfaceがFactに無い(数字境界つき)・不正値・重複→既存の1回retry対象、flags=報告のみ) (7)2回失敗時のRuntimeErrorにattempts_logを添付(挙動は不変)
- THEME_TAGはcost logger用ラベルのみ変更。

## unified diff
```diff
--- Production(er019_family_x_storyline_b3_fact_selection_01.py)
+++ Trial(b3r2_b3_dplus_01.py, 先頭コメント1行除く)
@@ -34,3 +34,3 @@
 
-THEME_TAG = "NEWS_FAMILY_X_B3_FACT_SELECTION_PRODUCTION_01"
+THEME_TAG = "B3R2_DPLUS_TRIAL_02"
 
@@ -58,6 +58,11 @@
 
-あなたの仕事は次の5つです。
+【Ledgerの読み方】
+各Factは「Fact本文」(ID行の文と、scope・conditions・numeric_value・date_or_periodなどの欄)と、「Writerへの制約」(notes_for_writer・ambiguity_noteの欄。`制約(…)`と表記されることがあります)に分かれています。
+- Fact本文は、Fact選択とStorylineの材料です。
+- Writerへの制約は、のちに記事を書く工程が守るガードレールです。Storylineやselected_fact_briefの内容・文言として転記・言い換えしないでください(「〜しない」「〜と断定しない」などの指示調の文を入れない)。Storylineには事実の記述だけを書き、制約に反する断定をしないでください。制約そのものは、システムが選択Factに対応づけて別途Writerへ渡します。
+
+あなたの仕事は次の6つです。
 
 1. このFull Ledgerの中から、記事として一本化しやすい中心Storyline(のちの記事が伝える「何が起きて、なぜそうなったか」という一続きの筋)を1つ決定してください。
-2. 決定したStorylineを1行の日本語で明示してください(これが後工程でWriterへ渡すテーマ文としてそのまま使われます)。
+2. 決定したStorylineを1行の日本語で明示してください(これが後工程でWriterへ渡すテーマ文としてそのまま使われます)。Storylineには、Fact本文に基づく事実の記述だけを書き、注意・禁止・書き方の指示は含めないでください。
 3. Full Ledgerの全fact_idそれぞれについて、以下4つのテストを適用してください。
@@ -68,2 +73,6 @@
 5. 採用したFactだけを使って、Writerへそのまま渡す「Selected Fact Brief」(必要最小限のFactを簡潔にまとめた文章。冒頭にStorylineの1行を含める)を作成してください。Selected Fact Briefは記事本文そのものではなく、Writerへの素材です。
+6. 採用したFactそれぞれについて、そのFact本文(ID行の文)に書かれている数字・日付の表記を1つずつ洗い出し、number_ranksへ中核(core)か周辺(peripheral)の別とともに記載してください。
+- surface: 数字・単位・「約」「超」などのヘッジ語まで含めた形で、Fact本文に書かれている通りに写してください(例: 約3.4％、2,300件超、7月13日)。Fact本文に無い数字、Ledgerの他の欄にしかない数字、別のFactの数字は書かないでください。数字を含まない表記は不要です。
+- kind: magnitude(量・割合・金額・件数など)/date_time(月を含む日付・時刻・四半期)/range(範囲)/year(年だけ)/ordinal(第12回など識別子の序数)/name_embedded(名称の一部の番号)のどれか。
+- role: 次の順で決めてください。(a)year・ordinal・name_embeddedは常にperipheral。(b)量とrangeは、そのFactのnumeric_value欄の数字(numeric_scopeの括弧内を除く)に含まれるものだけがcore候補(Ledger全体にnumeric_value欄が1件も無い場合に限り、Fact本文の数字で比べる)。日付は、表記に月があり、そのFactのdate_or_period欄の先頭の日付と、表記にある年・月・日が全て一致するものだけがcore候補(Ledger全体にdate_or_period欄が1件も無い場合に限り、Fact本文の最初の日付で比べる。年だけ・日だけ・時刻だけ・四半期の表記は候補になりません)。(c)core候補を、Storylineに出る量、それ以外の量、日付の順に並べ(同じ順位ではFactの採用順・本文の出現順)、先頭から最大 max(3, min(6, floor(n/2))) 個をcore、残りと候補でないものをperipheralとする(nは量・range・日付の概念の総数。概念=同じFactの中で主数字と単位が同じ表記のまとまり。同じ概念の表記は全て同じroleにする)。迷ったらperipheral。
 
@@ -79,4 +88,5 @@
 - recheck_note: 採用Fact数が6件以上の場合のみ記入。5件以下の場合はnull。
-
-【重要】fact_idは、上記Full Ledgerに実在するfact_idのみを使用してください。Ledgerに存在しないfact_idを作り出さないでください。"""
+- number_ranks: 手順6の結果(採用Factの数字・日付の表記ごとに fact_id・surface・kind・role)。数字が1つも無い場合は空配列。
+
+【重要】fact_idは、上記Full Ledgerに実在するfact_idのみを使用してください。Ledgerに存在しないfact_idを作り出さないでください。number_ranksのfact_idは採用したFactのみ、surfaceは当該Factのfact本文に実在する表記のみとしてください。"""
 
@@ -118,2 +128,16 @@
             "recheck_note": {"type": ["string", "null"]},
+            "number_ranks": {
+                "type": "array",
+                "items": {
+                    "type": "object",
+                    "properties": {
+                        "fact_id": {"type": "string"},
+                        "surface": {"type": "string"},
+                        "kind": {"type": "string", "enum": ["magnitude", "date_time", "range", "year", "ordinal", "name_embedded"]},
+                        "role": {"type": "string", "enum": ["core", "peripheral"]},
+                    },
+                    "required": ["fact_id", "surface", "kind", "role"],
+                    "additionalProperties": False,
+                },
+            },
         },
@@ -121,3 +145,3 @@
             "selected_storyline", "fact_tests", "selected_fact_ids",
-            "selected_fact_brief", "recheck_note",
+            "selected_fact_brief", "recheck_note", "number_ranks",
         ],
@@ -147,5 +171,19 @@
 
+SHAPE_MODE = "sep"   # "sep"=制約欄を制約(…)ラベルへ置換 / "none"=台帳そのまま(D-plus-min腕用)
+SHAPE_LABELS = (("  notes_for_writer:", "  制約(notes_for_writer):"), ("  ambiguity_note:", "  制約(ambiguity_note):"))
+
+
+def shape_ledger_for_b3(ledger_text: str) -> str:
+    """Fact本文と制約を欄ラベルで役割分離して見せる。ID行(`[VERIFIED] ID:`)の形式・欄の値は不変(ラベルのみ置換)。"""
+    if SHAPE_MODE != "sep":
+        return ledger_text
+    out = ledger_text
+    for a, b in SHAPE_LABELS:
+        out = out.replace("\n" + a, "\n" + b)
+    return out
+
+
 def build_user_prompt(topic: str, ledger_text: str) -> str:
     return USER_PROMPT_TEMPLATE.format(
-        topic=topic, ledger_text=ledger_text,
+        topic=topic, ledger_text=shape_ledger_for_b3(ledger_text),
         fact_test_definitions=FACT_TEST_DEFINITIONS_JA,
@@ -154,3 +192,8 @@
 
-def validate_selection_output(parsed: dict, ledger_fact_ids: list) -> list:
+import os as _os, sys as _sys
+_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
+import b3r2_rank_01 as _rank
+
+
+def validate_selection_output(parsed: dict, ledger_fact_ids: list, ledger_text: str = None) -> list:
     """技術的整合性エラーのリストを返す(空リスト=技術的に有効)。
@@ -183,2 +226,6 @@
         errors.append("RECHECK_NOTE_MISSING_FOR_6_OR_MORE_SELECTED")
+    if ledger_text is not None and not unknown_selected:
+        nv = _rank.validate_number_ranks(parsed.get("number_ranks"), ledger_text, selected_ids, parsed.get("selected_storyline"))
+        errors.extend("NUMBER_RANKS_" + e for e in nv["errors"])
+        parsed["_number_rank_flags"] = nv["flags"]
     return errors
@@ -225,3 +272,3 @@
             continue
-        errors = validate_selection_output(result["parsed"], ledger_fact_ids)
+        errors = validate_selection_output(result["parsed"], ledger_fact_ids, ledger_text)
         # RECHECK_NOTE_MISSING_FOR_6_OR_MORE_SELECTEDはsoft warning(内容面の
@@ -241,3 +288,3 @@
             }
-    raise RuntimeError(
+    _err = RuntimeError(
         "[STOP] Storyline+B3 Fact Selection: 2回試行しても技術的に有効な出力を得られませんでした。"
@@ -245,2 +292,4 @@
     )
+    _err.attempts_log = attempts_log
+    raise _err
 
```
