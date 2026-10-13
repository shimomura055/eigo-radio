# before_after_meta_adv_02: Meta Adv Before(M2P0対照, Round1既存) / After(M2P0X, 本Trial) 全件
管理ID: FAMILY-X-KP-NO-WAY-MINIMAL-FIX-TRIAL-01 委任_02 / 2026-10-13 / Trial専用・採用判断なし / モデル gpt-6-luna(Production同一=比較可能性の例外、応答model_id=gpt-6-luna。最新世代最上位系ではない)

## Before (M2P0, n=2。最終5件=canonicalized key_phrase)
| run | 1 | 2 | 3 | 4 | 5 | no way | gate |
|---|---|---|---|---|---|---|---|
| ctl_run1 | behind the scenes | contract workers | **no way** | unintentionally | concierge | 裸 | PASS |
| ctl_run2 | contract worker | unintentionally | concierge | behind the scenes | **no way** | 裸 | PASS |

## After (M2P0X, n=5)
| run | rank1 | 2 | 3 | 4 | 5 | no wayの扱い | gate(sel/canon/red/merged) |
|---|---|---|---|---|---|---|---|
| x_run1 | contract workers | behind the scenes | unintentionally | **no way to know** | instead of AI | 拡張(候補`no way`→`no way to know`) | PASS/PASS/PASS/PASS |
| x_run2 | **no way to know** | behind the scenes | contract workers | unintentionally | other end of the call | 拡張 | 全PASS |
| x_run3 | unintentionally | behind the scenes | contract workers | **no way to know** | talking to AI | 拡張 | 全PASS |
| x_run4 | contract workers | behind the scenes | unintentionally | **no way to know** | other end of the call | 拡張 | 全PASS |
| x_run5 | contract workers | behind the scenes | unintentionally | **no way to know** | take care of | 拡張 | 全PASS |
- 裸の`no way`: Before 2/2 → After **0/5**(解消)。拡張5/5、拡張形のINVALID 0/5、有限助動詞INVALID 0/5。5/5が`no way to know`(`have`は含まない形=既存Validator適合)。
- 拡張形の本文逐語性: `no way to know`は本文S14に連続して存在(literal/tolerant逐語 25/25)。canonicalizationは無変更(key_phrase==display_phrase)、Redundancy PASS。自然さ(定性): 「~する方法がない/知る由もない」の意味が単独で成立し、Key Phraseとして自然。LLMは5/5とも`source_candidate_id`を元の`no way`のまま、display_phraseのみ拡張(設計どおり)。

## 副作用(重要): concierge の消失
- Before: `concierge` 2/2。After: **0/5**。run1・run4では`backup_item`(rank6)にconciergeが回り最終5件から外れた。他3 runは最終にもbackupにも出ず。
- 5枠目(After)は `instead of AI` / `other end of the call`×2 / `talking to AI` / `take care of`。うち`instead of AI`・`talking to AI`は候補`instead of`・`talking to`(語彙断片)へ後続名詞(AI)を足した拡張、`other end of the call`は候補`end of`の拡張。いずれも記事固有の組合せで、`concierge`(希少な名詞)より学習価値が高いとは言い難い(定性判断、Fable/ユーザー確認事項)。P0Xの「構文の一部は隣接語で拡張」が`no way`以外の断片(`instead of`/`talking to`/`end of`)にも波及した(over_extended_items 7件/25、対照0/10)。
- 維持できた良い選定: `behind the scenes` 5/5、`unintentionally` 5/5、`contract workers` 5/5(対照 2/2・2/2・2/2)。
