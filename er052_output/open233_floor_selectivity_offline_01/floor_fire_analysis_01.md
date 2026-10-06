# floor_fire_analysis_01 (OPEN-233-FLOOR-SELECTIVITY-OPTIMIZATION-01 委任_01, read-only, 費用0円)

label_counts(RCA推測ラベル): {'不要': 24, '正当': 6, '判断不能': 5} / LLM判定分布(35件): {'ACCEPTABLE': 25, 'QUALITY': 6, 'BLOCKING': 4} / Stage1 sub_reasons全件model: True / unsupported_new_claim併発: 34/35

## カテゴリ別(延べ。複合flagは複数カテゴリへ計上)
| カテゴリ | 延べ発火 | 正当 | 不要 | 判断不能 | LLM判定(重大/軽微/問題なし) | 単独/複合 |
|---|---|---|---|---|---|---|
| 主体 | 6 | 2 | 2 | 2 | [1, 1, 4] | 6/0 |
| 数字 | 4 | 3 | 1 | 0 | [2, 1, 1] | 4/0 |
| 否定 | 5 | 0 | 5 | 0 | [0, 1, 4] | 3/2 |
| 比較 | 14 | 0 | 13 | 1 | [0, 1, 13] | 10/4 |
| 因果 | 1 | 0 | 1 | 0 | [0, 0, 1] | 1/0 |
| 時期 | 8 | 1 | 6 | 1 | [1, 3, 4] | 6/2 |
| その他(Tier0補助ベルト:issue文の主体語) | 1 | 0 | 0 | 1 | [0, 0, 1] | 1/0 |

## 不要24件の原因割付
{'(ii)種別妥当だが重大性判定欠如': 6, '(i)フラグ不整合': 17, '(iv)Tier0語彙': 1}

## 設計案replay(35件、in-sample)
| 案 | 強制重大 | うちfloorのみ起因 | 最終BLOCKING(強制∪LLM) | 追加確認へ | 非重大化 | 正当6の行き先 | 判断不能5の行き先 |
|---|---|---|---|---|---|---|---|
| 案0_現行 | 35 | 31 | 35 | 0 | 0 | {'強制重大': 6} | {'強制重大': 5} |
| 案1_条件精緻化 | 14 | 10 | 14 | 0 | 21 | {'強制重大': 6} | {'非重大化(Stage2判定へ戻る)': 2, '強制重大': 3} |
| 案2_確定のみ強制+他は追加確認 | 8 | 5 | 9 | 27 | 0 | {'追加確認へ': 2, '強制重大': 4} | {'追加確認へ': 4, '強制重大': 1} |
| 案3_トリガーのみ | 0 | 0 | 4 | 35 | 0 | {'追加確認へ': 6} | {'追加確認へ': 5} |
| 案4_floor撤廃+既存S1 | 4 | 0 | 4 | 31 | 0 | {'追加確認へ(既存S1)': 2, '強制重大(LLM自身がBLOCKING)': 4} | {'追加確認へ(既存S1)': 5} |
| 案5_段階化 | 14 | 10 | 14 | 3 | 18 | {'強制重大': 6} | {'非重大化(Stage2判定へ戻る)': 1, '追加確認へ': 1, '強制重大': 3} |

## 35件一覧
| no | run | cy | fact | floor | LLM | label | issue_type | 原因 | 案1 | 案2 | 案5 | claim |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | hormuz_run03_a | 1 | HF-009 | changed_actor | 問題なし | 不要 | contra_or_expansion | (ii)種別妥当だが重大性判定欠如 | 強制重大 | 強制重大 | 強制重大 | At the same time, attacks by the United States and Iran, a s |
| 2 | meta_run03_adv | 1 | MUSE-HC-012 | changed_negation | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | The issue was not that humans made the calls themselves. |
| 3 | meta_run03_adv | 1 | MUSE-HC-012 | changed_comparison | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | The real challenge for AI phone calls is not just how they t |
| 4 | meta_run03_adv | 1 | MUSE-HC-012 | changed_comparison | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | The more useful a service is, the less it should hide the pe |
| 5 | meta_run03_adv | 3 | MUSE-HC-011 | changed_actor | 軽微 | 正当 | contra_or_expansion |  | 強制重大 | 追加確認 | 強制重大 | News reports also cited an employee’s report that human staf |
| 6 | meta_run03_sta | 1 | MUSE-HC-012 | changed_negation,changed_comparison | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | The problem was not that humans made the calls. |
| 7 | meta_run03_sta | 1 | MUSE-HC-012 | changed_comparison | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | The real challenge for AI calls is not only how they talk. |
| 8 | meta_run03_sta | 1 | MUSE-HC-012 | changed_comparison | 問題なし | 不要 | unclear | (ii)種別妥当だが重大性判定欠如 | 非重大化 | 追加確認 | 追加確認 | The more useful a service is, the less it should hide worker |
| 9 | meta_run03_sta | 1 | MUSE-HC-011 | changed_number | 重大 | 正当 | contra_or_expansion |  | 強制重大 | 強制重大 | 強制重大 | It said human staff made inappropriate comments about race d |
| 10 | meta_run03_sta | 1 | MUSE-HC-011 | changed_number | 重大 | 正当 | contra_or_expansion |  | 強制重大 | 強制重大 | 強制重大 | These calls were about trying to lower internet or cable fee |
| 11 | neg1_meta_b3pr | 1 | MUSE-HC-006 | changed_time | 軽微 | 判断不能 | absence_only |  | 非重大化 | 追加確認 | 非重大化 | But as the conversation went on, the voice was not AI at all |
| 12 | neg1_meta_b3pr | 1 | MUSE-HC-008 | changed_comparison | 問題なし | 判断不能 | contra_or_expansion |  | 非重大化 | 追加確認 | 追加確認 | A human can handle situations that AI alone finds difficult. |
| 13 | neg1_meta_b3pr | 1 | MUSE-HC-010 | changed_time | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | But this was where the problem began. |
| 14 | neg1_meta_b3pr | 1 | MUSE-HC-010 | changed_comparison | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | It is another when you know a person is listening. |
| 15 | neg1_meta_b3pr | 1 | MUSE-HC-004 | changed_time | 問題なし | 不要 | contra_or_expansion | (ii)種別妥当だが重大性判定欠如 | 強制重大 | 追加確認 | 強制重大 | As AI becomes able to make calls or reservations for us, thi |
| 16 | neg1_meta_b3pr | 1 |  | changed_comparison,changed_time | 軽微 | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | The more useful the feature, the more people will want to kn |
| 17 | neg1_meta_b3pr | 1 |  | changed_time | 軽微 | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | They will want to know if it is AI or human. |
| 18 | neg1_meta_b3pr | 2 | MUSE-HC-010 | changed_time | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | And this was where the concern began. |
| 19 | neg1_meta_b3pr | 2 |  | changed_comparison,changed_time | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | People will want to know who is on the other side. |
| 20 | neg2_meta_refr | 1 | MUSE-HC-011 | changed_number | 問題なし | 不要 | contra_or_expansion | (ii)種別妥当だが重大性判定欠如 | 強制重大 | 強制重大 | 強制重大 | News reports also quoted a report from an employee. |
| 21 | neg2_meta_refr | 1 | MUSE-HC-011 | changed_number | 軽微 | 正当 | contra_or_expansion |  | 強制重大 | 強制重大 | 強制重大 | It said that human staff made inappropriate comments about r |
| 22 | neg3_hormuz_pr | 1 | HF-003 | changed_actor | 重大 | 正当 | contra_or_expansion |  | 強制重大 | 強制重大 | 強制重大 | On July 13, Trump posted that all cargo passing through the  |
| 23 | neg3_hormuz_pr | 1 | HF-009 | changed_time | 重大 | 正当 | contra_or_expansion |  | 強制重大 | 追加確認 | 強制重大 | The fee plan left the stage, but the events driving oil pric |
| 24 | neg7_meta_prod | 1 | MUSE-HC-004 | changed_actor | 問題なし | 判断不能 | contra_or_expansion |  | 強制重大 | 追加確認 | 強制重大 | Imagine asking AI to book a haircut. |
| 25 | neg7_meta_prod | 1 | MUSE-HC-006 | changed_actor | 問題なし | 不要 | contra_or_expansion | (ii)種別妥当だが重大性判定欠如 | 強制重大 | 追加確認 | 強制重大 | So it sounds like a simple story: you make a request, and AI |
| 26 | neg7_meta_prod | 1 | MUSE-HC-006 | changed_comparison | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | It was like an AI-led play with a hidden supporting actor. |
| 27 | neg7_meta_prod | 1 | MUSE-HC-010 | changed_negation,changed_comparison | 問題なし | 不要 | contra_or_expansion | (ii)種別妥当だが重大性判定欠如 | 非重大化 | 追加確認 | 追加確認 | The issue was not that humans handled calls. |
| 28 | neg7_meta_prod | 1 | MUSE-HC-010 | changed_comparison | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | A service that seemed simple now looked like a mystery story |
| 29 | neg7_meta_prod | 1 | MUSE-HC-010 | changed_negation | 軽微 | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | No large information leak was confirmed. |
| 30 | neg7_meta_prod | 1 | MUSE-HC-010 | changed_actor | 問題なし | 判断不能 | contra_or_expansion |  | 強制重大 | 追加確認 | 強制重大 | But users could not know who was really doing the work they  |
| 31 | neg7_meta_prod | 1 | MUSE-HC-010 | changed_comparison | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | That uncertainty turned convenience into a mystery. |
| 32 | neg7_meta_prod | 1 | MUSE-HC-012 | changed_negation | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | The company did not stop Muse itself. |
| 33 | neg7_meta_prod | 2 | MUSE-HC-004 | changed_causality_floor | 問題なし | 不要 | absence_only | (iv)Tier0語彙 | 強制重大 | 強制重大 | 強制重大 | So it sounds like a simple story: you make a request, and so |
| 34 | neg7_meta_prod | 2 | MUSE-HC-010 | changed_comparison | 問題なし | 不要 | absence_only | (i)フラグ不整合 | 非重大化 | 追加確認 | 非重大化 | The issue was not just that humans handled calls. |
| 35 | neg7_meta_prod | 2 | MUSE-HC-010 | tier0:aux:issue_actor | 問題なし | 判断不能 | contra_or_expansion |  | 強制重大 | 強制重大 | 強制重大 | Users might not know who was doing the work they had asked A |

## SC gold hold-out参考(rep30、旧Stage1由来)
{"list_floor_only_gold": [["safety_A4", "“Through Muse, trained human contract workers made some call", ["changed_actor"], "unclear", true, true], ["neg3_hormuz_prodrunner_b1b", "The fee plan left the stage, but the events driving oil pric", ["changed_time"], "unclear", false, false]], "n_unique_gold_floor_claims(非列挙複製、gold一致、全保存run重複排除)": 12, "うちLLM非BLOCKING(floorだけが重大化)": 2, "案1(floor-only gold)": {"強制": 1, "非強制": 1}, "案2(floor-only gold)": {"強制": 1, "追加確認": 1}, "案5(floor-only gold)": {"強制": 1, "追加確認": 1}, "案4(floor-only gold)": {"追加確認(S1)": 2}}

## コスト材料
{"8run_total_by_stage_jpy": {"stage1_initial": 11.113, "stage2_second_judge": 11.011, "stage3_rewrite": 6.085, "stage1_recheck": 6.89, "stage1_exit_check": 3.454, "floor_verify": 0.809}, "8run_total_jpy": 39.363, "S1_second_opinion_jpy_per_claim_mean": 0.0281, "n_s1_claim_records": 161}