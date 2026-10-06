# 委任_03a1 (OPEN-233-DIRECTIONAL-MISREAD-SAFETY-DESIGN-01)

Opus Part 2レビュー指摘の設計doc反映のみ。対象: docs/pm/design_open233_directional_misread_safety_01.md + RESULT_PACKET_03A1.md。他ファイル・git操作なし。

反映項目(各該当§末尾へ「Opus Part 2反映(2026-10-06)」追記、既存文削除せず訂正注記):
1. §4/§7: 123件=Stage 1候補のみ(SUPPORTED含まず)。正母集団=Stage 1全単位(support_fact_ids付き、checker L636-645)、要集計。
2. §8: 抽出失敗=BLOCKING撤回→1回retry→QUALITY。案E'(Ledger側事前抽出enum/記事側blind抽出/Python比較/迂回BLOCKING/再抽出解消/上限到達はSTOPかQUALITY/T3T4観察のみ)。案D撤回候補。起動T-D'。
3. §3: 代替E→代替V改名(E/T-C主導→V/T-C主導)。
4. §1表: S1本体L4160-4203。
5. §9: 限定Trial追加対象(1)-(6)、費用約15円以内。
6. §13: 追加3点。
7. §12: ユーザー判断7点。
8. §14新設: Opus Part 2レビュー要約とFable照合。

T-0: 本文を逐語保存しcheck_delegation_prompt.py実行。T-2/T-3対象外。
