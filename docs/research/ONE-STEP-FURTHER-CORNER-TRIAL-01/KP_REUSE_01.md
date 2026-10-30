# KP_REUSE_01: 既存Key Phrase/Word候補選定方式の調査と再利用(委任_03、2026-10-30)

Production fileは変更せず、読取専用importまたは同等ロジックのTrial側実装で再利用した。

| 既存方式(file:line) | 内容 | OSF03での扱い |
|---|---|---|
| `er003_key_phrase_source_gate_01.py:45` normalize_text | 大小文字・apostrophe・ダッシュ・HTML entity・空白を吸収した本文実在照合 | **import再利用**(`tools/osf03_lib.py` `nt`)。Step1の引用文(quote)の本文実在検査とターゲット範囲の引用内実在検査 |
| `er003_key_phrase_source_gate_01.py:66` check_key_phrase_source_presence | KPのsource_span(無ければsource_sentence)が現行本文に実在するかGate | **同等ロジック**(check_extraction: quote_not_in_body / target_span_not_in_quote)。Gate A項目1・2の機械部分 |
| `er003_kp_general_explanation_01.py:191,406-444` _norm_match / assemble_part1 | 引用英文が本文に逐語実在しなければSTOP(KP_PART1_QUOTE_NOT_IN_ARTICLE)。gloss空・未整合はHR | **同等ロジック**。引用の逐語実在を必須化。意味(meaning_ja)は抽出時に確定し、最終確認でmn(意味一致)を再検査 |
| `er003_key_words_canonicalization.py:444,576` _is_contiguous_substring / validate_canonicalization_item | 表層形→原型(key_phrase)が選定句/source_spanの連続部分文字列または1対1語形変換であること、1〜5語、捏造禁止(Rule7) | **同等ロジック**(原型の各語がターゲット範囲由来か:語幹照合+不規則活用表、2〜8語)。**ただし「有限助動詞を含むと不可」は再利用しない**(原文§5 Step1は否定・法助動詞・主語を失わないことを要求。逆に否定・法助動詞が落ちたら棄却する検査 negation_lost / modal_lost を追加) |
| `er011_key_phrase_set_redundancy_qa_01.py:228` run_redundancy_qa_gate | KP集合内の意味重複除外 | **同等ロジック**: KP/Word/文法との核の内容語幹重複を機械検査(overlap_kp / overlap_grammar)+監査の欠陥コード`overlap_existing`。API追加なし |
| KP-GATE-DROP-BACKFILL-PRODUCTION-01(`docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/DESIGN_02.md`)の救済(Gate落ち→backfill) | 品質を満たさない候補を捨て、別候補で補充 | **同等の考え方**: Step5「別の基本表現を探す」=あるレベルで合格候補が0〜不足なら、検討済みを除外指定して再抽出(第2・第3ラウンド) |
| `er003_key_words_gloss_alignment`(gloss ALIGNED/HR) | 日本語glossと表現の整合、不整合はHR | **発想のみ再利用**: 抽出時にmeaning_jaを確定し、最終確認(本文参照)でmnを検査。不整合は不採用 |

再利用しなかったもの: KP選定Prompt本体(目的が異なる)、KPのHR(本Trialでは人手選別なし。採用時のHR統合は別判断)。
差分(新規): 発展表現の生成を記事から切り離す入力制限(Step2)、置換文(frame)による意味対応検査、長文化のみ/語順入替/単語1つ差の機械フラグ、別ベンダー監査、回帰セット。
