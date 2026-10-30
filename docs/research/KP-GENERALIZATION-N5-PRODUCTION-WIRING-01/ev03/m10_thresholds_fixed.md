# M10 統合replay 判定基準(実行前に固定。2026-10-30、実行前に作成)
対象: untidi_a2 / untidi_b1b / melos_a2 / jwst_m_a2 / jwst_m_b1b の5level(Trial 03 N5の記録あり。費用Cap ¥20、実測で逐次確認し超過見込みなら中断してFableへ)。
実行: Production `generate_candidates`(`kcand.make_generate_fn`)を公式経路のまま実API(N5既定ON)で1 roundだけ実行。入力=Trial corpus本文(fixture)。
Trial生存候補 = fixture trial_items(Trial N5最終item)の source_span 集合。
判定:
- 分母 = 全対象levelのTrial生存候補の総数。
- 「既存Gateで失われた」 = そのsource_span(または同一語彙のspan)がProduction側のpool/call1/backfill記録に現れ、最終的に**n5_*以外のstage**(symbol/cmu/ft/human_ng/qa12/ga/...)のdropで落ちたもの。
- 「未再現」 = Production側にそのspanが現れない(LLM非決定性。J2判定の分子に入れず別掲)。
- 「N5が落とした」 = n5_*のdrop/revert(別掲、J2の分子に入れない)。
J2トリガ(いずれか): (a) §4A ①〜⑤の項目が最終出力から失われた(下記期待形と不一致かつ原因がGate drop。未再現は別掲しFableが評価)、(b) 「既存Gateで失われた」/分母 > 15%。
J2該当時は是正せず、Gate別drop件数・例・Trial比差分を添えて判断候補J2として報告する。
§4A期待: ① hear it out -> hear someone out(untidi_a2/b1b) ② take points away from -> take something away from + 訳修正(untidi_a2)、taking points awayの本文形revert(untidi_b1b) ③ keep one's eye on(melos_a2) ④ set a lower limit -> set a limit(jwst_m_b1b) ⑤ took an unexpected turn -> take a turn(jwst_m_a2/b1b)
