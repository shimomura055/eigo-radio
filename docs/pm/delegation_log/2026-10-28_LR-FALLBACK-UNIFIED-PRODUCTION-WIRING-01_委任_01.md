# 委任_01(Phase A / W1): 49経路×現行配線の照合表と、LR・Fallback発動記録の所在・runtime evidence手段の棚卸し(API 0)

共通事項=`…_委任_00_COMMON.md`(必読)。成果物=`docs/research/LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01/W1_ROUTE_WIRING_AND_RECORDS_01.md`。

## 目的
Phase Bの実装・受入に必要な「どの経路(Family×Level×Role)の、どの記録を読めば、最終採用音声のLR/Fallback状態が分かるか」と「ユーザー原文§7の試行回数・待機・Fallback Style・LR範囲が現行Production配線と一致しているか(Dangling Reference含む)」を確定する。

## 作業
1. **49経路対応表の照合**: `ROW_MAPPING_01.md` §2の49行それぞれについて、現行HEADのProduction配線(呼出箇所file:line、`er127` policy名、呼出元の`unified_flow_active()`判定)を表にし、§7の代表仕様(EN LR対象=3+3、JA=3/JA minimal/LRなし、KP英語=2+ENGLISH_LOCK 2、Adv KP解説=3/英語短文、Z Dialogue=3/3回目従来Style、固定Shell=既存、固定MP3=生成なし)との一致/不一致を判定。不一致・旧仕様参照(例: 旧retry回数・旧待機・`style_prefix_override`欠落・旧Fallback名)が残る箇所をDangling Referenceとして列挙(修正はしない)。A/B/C Familyは「対象外(方式置換禁止)」と明記しつつ、最終Human報告仕様の適用可否判定に必要な記録構造だけ確認。
2. **発動記録の所在表(経路×記録)**: 各経路で、最終採用attemptの(a)LR発動有無・前後英文・差分・対象区間、(b)Fallback発動有無・採用Style名・切替元Style・対象区間/Chunk、(c)採用されなかった試行のFallback(誤表示防止のため区別が必要)、がどのファイル・どのキーに残るか(`tts_generation_results.json`/attempt JSON/`BlockProgress`/`chunk_tts_evidence`/`pass_with_warning_listening_list.json`/`style_record.json`/Y・Zの相当物)。欠落(記録されない経路・キー)はW2 F4「Adv ③NG attemptのStyle未記録」等を含めて列挙。**最終Human報告へ伝搬させるために追加記録が必要な項目**を明示(設計提案、実装はしない)。
3. **runtime evidence手段**: LR・Fallbackは自然発生に依存する。既存の承認済みevidence手段(例: `er011_output/.../forced_fallback`系・`kpx1_evidence_forced_fallback_rerun.log`の仕組み・mock/DEV専用の強制NG・保存済みrunの再判定`rejudge_with_current_judge`・resume)を棚卸しし、Family×Level×Role別に「有料0で発火を再現できる手段」「有料最小で再現できる手段(見積)」「再現不可(自然発生待ち)」を表にする。Production既定動作を変える手段は提案しない。
4. **既存evidenceの再利用候補**: 直近runで実際にLR/Fallbackが発生した保存run(AI島 hr_02、Word Gacha Adv、メロス、猿の手、Y E-1 y_voice_1、他)を一覧化し、最終Human報告の表示検証(赤/濃青)の入力データとして使えるか(記録の完全性)を判定。

## 出力形式
表中心。各行にfile:line。判断候補はA/B/C/D区分。推測は「未確認」と明記。
