# STATE_01 — Y段落分割(Chunk)の現状(2026-10-26、FAMILY-Y-CHUNK-OPEN527-CLOSEOUT-01 委任_01、API 0)
事実のみ。記事本文・run dir・公開ページは未変更。

1. 承認: Y Std/Adv=APPROVED_FOR_PRODUCTION(X方式=段落境界+0.2秒、`docs/pm/delegation_log/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_02.md` §1-① / `2026-10-26_CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01_USER.md` §2)。`er121_family_y_structure_01.py:117,121`(CHUNK_TTS_SCOPE Y=True、LEVELS=("b1b","a2"))。
2. 本文契約: 段落5固定・Voice本文1行(`er121_family_y_structure_01.py:159-183` split_y_article、`*_MULTI_LINE`違反)。= 正式CLIでは各segment 1段落。承認済み・変更しない。
3. 配線: `er121_family_y_audio_01.py:267` plan_y_chunks(共通`er117.plan_x_part`、段落2未満=chunked False)、`:288` _record_chunk_decision(課金前)、`:731` _load_y_body_chunks(Gate/組立がchunk単位で検査)。Std=chunk別6%減速→0.2秒無音→連結、Adv=減速なし0.2秒。
4. 実記事: 各segment 1段落のため分割0(`chunk_tts_decision.json` chunked=False)。runnerは毎回`write_level_inputs`でparts.jsonを記事本文から再生成するため、parts.jsonへの空行挿入は正式CLIでは消える(`y_chunk_evidence_driver_01.py` docstring)。
5. 実測evidence: `docs/research/CHUNK-TTS-STD-PRODUCTION-WIRING-XYZ-01/EVIDENCE_01.md` §3(Y Std/Adv、複数段落dev入力で正式生成関数・Gate・組立が発火。Std 0.2秒ポーズ実測0.647秒/2chunk等)。有料(約11円規模)で取得済み・追加取得不要。
6. 状態表記: Y=`APPROVED_FOR_PRODUCTION`・配線済み(`WIRED_NOT_FIRING`)・PRODUCTION_WIREDとは判定しない(CURRENT_SPEC L2981、ユーザー決定2026-10-26)。**本委任でも格上げしない。**
7. 既存オフライン回帰(Std 14: `er121_family_y_std_chunk_test_01.py` / Adv: `er121_family_y_audio_chunk_test_01.py` / Opus追加: `er121_family_y_std_chunk_opus_test_01.py`)は、すでに複数段落合成入力(y_voice_2=2段落、y_closing=3段落)で発火〜Gate〜組立〜resume〜改竄を検証していた。不足=(a)全8 segment同時の複数段落 (b)発火境界(1/2/3/5段落・空白ゆれ・単一改行) (c)planner版/方式のpin (d)回帰発見パターンからの脱落検知。→ 新規`er121_family_y_multiparagraph_regression_test_01.py`(7件)で補完。

## 重複記述一覧(Grep `OPEN-527`、*.md)
- OPEN_ITEMS.md: L1035(OPEN-520内参照)、**L1042 OPEN-527本体**(Comment 2削除+Voice 1ポーズ+Y分割方式[UDR-YFB-1]の複合項目)、L1047 OPEN-532(Y WIRED_NOT_FIRING記述)。
- CURRENT_SPEC.md: L2972(Y適用の実測、OPEN-527参照・『分割の実効化は新仕様=ユーザー判断待ち』)、L2981(Y Std/Adv WIRED_NOT_FIRING)、L3096(Chunk TTS 2026-10-26)。
- USER_DECISION_REGISTER_01.md: L411(Comment 2削除=判断済み)、L424(UDR-YFB-1/2待ち)、L451(OPEN-532 Chunk)、**L456(OPEN-527 Y分割方式=継続・ユーザー判断待ち)**。
- 重複の実体: 『Y chunkの状態』がOPEN-527(L1042/UDR L456)とOPEN-532(L1047/CURRENT_SPEC L3096)の二重管理。OPEN-527はComment 2削除・Voice 1原因(後者=OPEN-531でCLOSED)も含むため、Closeoutはそれらが他OPEN/UDRで完結していることをFableが確認のうえ行う(下記CLOSEOUT_01注意点)。
