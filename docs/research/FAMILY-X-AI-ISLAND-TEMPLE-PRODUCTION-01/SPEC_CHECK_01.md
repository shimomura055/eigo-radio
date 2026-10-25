# SPEC_CHECK_01 (FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01 委任_01、2026-10-26、API 0)

ユーザー原文§4の7項目のFamily X Production反映状況(CURRENT_SPEC.md、2026-10-26 HEAD基準)。未承認仕様・DEV専用経路・新flagは使わない。

| # | 項目 | Status(X) | 根拠 |
|---|---|---|---|
| 1 | B3と中核数値保持方式 | PRODUCTION_WIRED(B3経路=L1175、中核数値丸め=L2903、保持方式v4+J2=L2918、Fable受入2026-10-25。OPEN-514は非blocking) | CURRENT_SPEC.md:1175,2903,2918 |
| 2 | Std/Advの英訳・表現品質 | PRODUCTION_WIRED(Entertainment RF、固定フレーズChampion=L1908、Adv KP英語解説=L2035) | CURRENT_SPEC.md:1908,2035 |
| 3 | Key Phrase選定・Human Review | X=PRODUCTION_WIRED(R1 HRあり完走/R2 HRなし。既定=待機rc=4。HRなし宣言はユーザー宣言(declared_by+user_ref)のみ→本委任は宣言せず待機) | CURRENT_SPEC.md:2055-2057、OPERATIONS_01.md §5 |
| 4 | Part 1英語解説、Part 2文法・構文解説 | Part 1=L2039(X側Status要確認でも同一runnerが生成)、Part 2文法=X PRODUCTION_WIRED(Advのみ・Part 1直後) | CURRENT_SPEC.md:2039,2055-2057 |
| 5 | TTS速度・Chunk分割・ポーズ | PRODUCTION_WIRED(Adv地の文chunk TTS B0.2=L2936、TTS記号正規化=L2243、Std 6%減速等は既存) | CURRENT_SPEC.md:2243,2936 |
| 6 | Primary/Secondary ASR・発音同等性・音声品質検査 | PRODUCTION_WIRED(統一ASR判定=L2853、KP 3-ASR多数決=L2987、固有名詞アラーム+発音供給=L3026、M1 OOV=L2844、OPEN-517 F1+F2=L2862 X=PRODUCTION_WIRED) | CURRENT_SPEC.md:2844,2853,2862,2987,3026 |
| 7 | retry/fallback/resume | 既存仕様のまま(runnerの--regenerate-stage/--stage resume、RESTART_STORM回避、HR Lock) | runner help、CP_CHECK(MOON)§B |

- 未承認仕様の使用: なし。`EIGO_KP_GLOSS_ALIGNMENT`等のflagは設定しない(X2p'は2026-10-24にXYZ共通配線済み、新flagなし)。DEV専用経路・Trial経路は呼ばない。
- 入口: text=`er019_family_x_entertainment_production_runner_01.py`、audio=`er019_family_x_audio_production_runner_01.py`(直近『英単語ガチャ』『月』と同一)。
- 24時間条件: ユーザー原文§2末尾(`docs/pm/delegation_log/2026-10-26_FAMILY-X-AI-ISLAND-TEMPLE-PRODUCTION-01_USER.md`)により例外として扱う。
- 一次資料の渡し方: runnerにURL直指定の引数はなく、`--theme`(Research入力)に3 URLと確認済み要点・誤解防止を記載(`er019_output/ai_island_temple/theme.txt`)。`--source-note`はevidence記録のみ。取得原文は`sources/`(paper.txt等)に保存。
