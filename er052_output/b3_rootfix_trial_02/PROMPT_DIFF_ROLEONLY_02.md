# PROMPT_DIFF(役割宣言のみ腕(number_ranksなし)): Trial専用B3 Prompt(Productionとの差分。unified diff逐語。自動生成、委任_02)
- Production module sha256=93d0e31e735057ae874bbf27be48449fdd5bd5188e535b0a280eada9d314b758
- Trialコピー sha256=72057976b28c656cbe010abf0dbd8d3d002106de10238392589453862e608de6
- 置換箇所(各ちょうど1回出現をassert): THEME_TAG, role_declaration+count, step2_storyline_role, shape_ledger, stop_attach_attempts_log
- 不変: DEVELOPER_MESSAGE / FACT_TEST_DEFINITIONS_JA / 手順1,3,4,5の文言 / 採用Fact数注意 / fact_tests・selected_fact_ids・selected_fact_brief・recheck_note の schema項目 / retry機構(1回のみ)。削除した既存手順・schema項目は無い。
- 追加: (1)【Ledgerの読み方】役割宣言(U1: 制約を選択の参考にしてよい旨は削除済み) (2)手順2末尾に「事実の記述だけ・指示を含めない」 (3)入力整形 shape_ledger_for_b3(欄ラベルのみ置換: notes_for_writer→制約(notes_for_writer)、ambiguity_note→制約(ambiguity_note)。値・ID行は不変) (4)2回失敗時のRuntimeErrorにattempts_logを添付(挙動は不変)
- THEME_TAGはcost logger用ラベルのみ変更。

## unified diff
```diff
--- Production(er019_family_x_storyline_b3_fact_selection_01.py)
+++ Trial(b3r2_b3_roleonly_01.py, 先頭コメント1行除く)
@@ -34,3 +34,3 @@
 
-THEME_TAG = "NEWS_FAMILY_X_B3_FACT_SELECTION_PRODUCTION_01"
+THEME_TAG = "B3R2_ROLEONLY_TRIAL_02"
 
@@ -58,2 +58,7 @@
 
+【Ledgerの読み方】
+各Factは「Fact本文」(ID行の文と、scope・conditions・numeric_value・date_or_periodなどの欄)と、「Writerへの制約」(notes_for_writer・ambiguity_noteの欄。`制約(…)`と表記されることがあります)に分かれています。
+- Fact本文は、Fact選択とStorylineの材料です。
+- Writerへの制約は、のちに記事を書く工程が守るガードレールです。Storylineやselected_fact_briefの内容・文言として転記・言い換えしないでください(「〜しない」「〜と断定しない」などの指示調の文を入れない)。Storylineには事実の記述だけを書き、制約に反する断定をしないでください。制約そのものは、システムが選択Factに対応づけて別途Writerへ渡します。
+
 あなたの仕事は次の5つです。
@@ -61,3 +66,3 @@
 1. このFull Ledgerの中から、記事として一本化しやすい中心Storyline(のちの記事が伝える「何が起きて、なぜそうなったか」という一続きの筋)を1つ決定してください。
-2. 決定したStorylineを1行の日本語で明示してください(これが後工程でWriterへ渡すテーマ文としてそのまま使われます)。
+2. 決定したStorylineを1行の日本語で明示してください(これが後工程でWriterへ渡すテーマ文としてそのまま使われます)。Storylineには、Fact本文に基づく事実の記述だけを書き、注意・禁止・書き方の指示は含めないでください。
 3. Full Ledgerの全fact_idそれぞれについて、以下4つのテストを適用してください。
@@ -147,5 +152,19 @@
 
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
@@ -241,3 +260,3 @@
             }
-    raise RuntimeError(
+    _err = RuntimeError(
         "[STOP] Storyline+B3 Fact Selection: 2回試行しても技術的に有効な出力を得られませんでした。"
@@ -245,2 +264,4 @@
     )
+    _err.attempts_log = attempts_log
+    raise _err
 
```
