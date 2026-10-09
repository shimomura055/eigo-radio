=== ANNOTATED_BRIEF_BEGIN ===
# Selected Fact Brief

## Storyline
2026年【周辺数値】、ミニバッグはファッション媒体やFallランウェイで再び注目されているが、その注目は装飾的な小型アイテムを含む限定的なもので、大型バッグとも併存し、microバッグ全般の需要復活を示すものではない。

## Selected Facts
Storyline：2026年【周辺数値】、ミニバッグはファッション媒体やFallランウェイで再び注目されているが、その注目は装飾的な小型アイテムを含む限定的なもので、大型バッグとも併存し、microバッグ全般の需要復活を示すものではない。

- 【事実1】ELLEは2026年9月【中核数値】、ミニバッグをFall 2026【周辺数値】のトレンドとして紹介した。
- 【事実2】Who What WearのFall 2026【周辺数値】ランウェイまとめでは、小さなミノディエールは実用性より芸術性が強いものとして扱われる一方、大型・ゆったりした形も主要傾向に含まれている。
- 【事実3】別のWho What Wear記事では、microバッグのトレンドは短期間で終わったとの編集者の見解が示されている。これらは編集・ランウェイ上の注目を示すもので、消費者全体の需要や販売増を立証するものではない。「mini」と「micro」を混同しないこと。
=== ANNOTATED_BRIEF_END ===
=== SIDECAR_JSON_BEGIN ===
{
  "slug": "small_bag", "annotator": "A",
  "spec_sha256": "8d145c3d7cb3953ef2d344056e2e9979698fff7d1f60aec7a6b6d922e7cf1e57",
  "brief_sha256": "a4cfad728fafb255be93d912dfa3049101847f3a7b9d5cb2bbe2d861c1af7a3c",
  "facts": [
    {"n": 1, "ledger_ids": ["MB-01"]},
    {"n": 2, "ledger_ids": ["MB-05"]},
    {"n": 3, "ledger_ids": ["MB-06", "MB-01", "MB-05"]}
  ],
  "numbers": [
    {"surface": "2026年", "kind": "year", "concept": "C_year", "ledger_ids": ["MB-01", "MB-05"], "class": "peripheral", "role": "年のみ(Storyline及び重複行)"},
    {"surface": "2026年9月", "kind": "date_time", "concept": "C_elle_date", "ledger_ids": ["MB-01"], "class": "core", "role": "ELLE記事の掲載月"},
    {"surface": "Fall 2026", "kind": "name_embedded", "concept": "C_fall2026", "ledger_ids": ["MB-01", "MB-05"], "class": "peripheral", "role": "シーズン名の一部"}
  ],
  "unmapped_claims": [],
  "annotation_notes": [
    {"where": "概念 C_elle_date (2026年9月)", "question": "適格(MB-01 date_or_period先頭 2026年9月8日と年・月が一致)で、n=1のため上限3の内側", "options": ["中核", "周辺"], "chosen": "中核", "rule": "§3-5"},
    {"where": "2026年 (Storyline、Selected Facts内Storyline重複行)", "question": "年だけの表記は常に周辺。2026年9月の短い表記だが別kind(year)のため別概念とした", "options": ["C_elle_dateと同概念", "別概念C_year"], "chosen": "別概念C_year", "rule": "§3-2, §3-3"},
    {"where": "Fall 2026", "question": "名称内番号か量か", "options": ["name_embedded", "date_time"], "chosen": "name_embedded", "rule": "§5-3"},
    {"where": "事実3の末尾2文(これらは〜/「mini」と「micro」〜)", "question": "限定する文が別台帳ID(MB-01, MB-05)由来を含むため事実を分けるか", "options": ["別事実にする", "事実3に含めledger_idsへ追加"], "chosen": "事実3に含めMB-01, MB-05を追加", "rule": "§2"},
    {"where": "Storylineの印", "question": "Storyline文と重複行の2026年に同じ表記同じ印を付与", "options": ["付ける", "付けない"], "chosen": "付ける(同表記は同じ印)", "rule": "§3-1"}
  ]
}
=== SIDECAR_JSON_END ===
