# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / 委任_01 (Phase A: 診断+設計) 2026-10-12

- 範囲: 読取+ローカル実行のみ。API/ネットワーク呼出0、費用JPY0、Production code/prompt/SSOT無変更。ACTIVE_TASK_KP_IDIOM_01.md / RESULT_PACKET_KP_IDIOM_01.md を使用(Melos用ACTIVE_TASK.md/RESULT_PACKET.mdは不使用)。
- STOP確認: `docs/pm/delegation_log/*STOP_NOTICE*` はMelos案件の1件が存在(本件は有料run無しのため影響なし、削除・変更なし)。
- 詳細: `er064_output/kp_idiom_trial_01/phase_a/DIAGNOSIS_AND_DESIGN_01.md`(診断・設計書)、同dirにtrace/sim/prototypeのpy+json。

## 要点
1. `pumps its fist` / `mark the date on your calendar` はn-gram生成は通過、DB照合でヒット0により消滅(後段未到達)。ローカル再実行でINV-01の件数と完全一致を確認(Std 439/204/156/155, Adv 499/226/181/180)。
2. 支配要因=DB未収録(Wiktionary idiom/phrasal/proverb titlesに `pump..fist` 0件、`mark the date` 0件)。第2の壁=placeholder見出し(`pump one's fist` 収録でも `pumps its fist` に非ヒット=注入実験)。
3. 現行DBは固定形+活用形のIdiomは可、`one's/someone's` 見出し(約1,600)×本文の所有格は不可(自作3文0/3)。placeholder照合(a)で3/3回復、400記事副作用走査は25件(0.06/記事)。ただしCoffee 2表現は回復しない。
4. 回復には非DB経路(LLM補助抽出b1、またはルールb2)が必須。推奨=V2 (a+b1+c+d)、代替=V3 (b2+c+d)、対照VL(Strategy L全文)。
5. 費用見積: B=0、C≈JPY10、D≈JPY21、予備8、計≈JPY39(上限50内)。単価は選定0.35-0.48円/回(実測)、抽出callは推定。
6. 要ユーザー判断: b1は「本文全文をLLMへ送らない」原則(CURRENT_SPEC.md:1847)と衝突(Trial限定可)。ほか未解決論点7件は設計書12節。
