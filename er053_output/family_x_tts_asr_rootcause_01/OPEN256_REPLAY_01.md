# OPEN-256 是正後 (a') ¥0 replay(委任_25)

スクリプト: `er053_family_x_open256_replay_01.py`(API 0)。記録済み候補90件・QA evaluationsを本番コード経路
`build_full_candidate_records` -> `select_final_candidate` -> `_write_recovery_artifacts`(一時dir)へ通した。
詳細: `OPEN256_REPLAY_01.json`(全90件の旧/新判定)、`open256_fixture_90records_01.json`(固定fixture)。

## 是正案の選定(先に両案をreplay)
- 案S(推奨): span整合 `normalize(原文に申告spanを適用) == normalize(候補)`(トークン単位、原文内の任意の一致箇所)。
- 案B: 編集予算(候補側の非equal token数 <= len(changed_span_after)+2)。
- 90件replay結果: 案Bは誤拒否0だが、実記録の「申告外変更」(下記 Gemini part1 候補5 の "it"->"them")を検出できない(候補側の非equal token 2 <= 2+2 で通る)。
  案Sは旧採択76件に誤拒否0、救済対象14件のうち拒否1件のみ(後述、実際に申告外変更あり=正しい拒否)。**案Sを採用**。
- 注: 最初の素朴実装(文字列の最初の一致へreplace、asr_validation.tokenizeで正規化)は誤拒否が出た
  (短い申告span "a"/"from" が語中に一致、tokenizeが数字を文脈依存変換 "2xdecimalpointx3000000" 等)。
  最終実装はトークン単位の任意一致箇所+単純正規化(`[\w']+` 小文字化)で、この誤拒否は解消済み。

## 合格基準3点
| 基準 | 結果 |
|---|---|
| 旧採択76件の判定維持 | 76/76 全文性PASS維持(判定変化0)。all_seven True->False の反転も0件 |
| 救済対象14件が全文性PASS | 13/14 PASS。1件 REJECT: tts_gemini_3_8..._ab_trial_01/b/full_story_part1 候補5(`a job application`->`Job applications`、実際は文末 "sees it"->"sees them" も変更=申告外)。この候補は記録上も Gate6 不合格(変更が窓外)で、旧・新どちらでも採択されない=選択結果への影響なし |
| META comment_2 の3件が all_seven_gates_pass=True | 候補1・2・4 = True(候補3・5は意味保存Gate不合格のまま=従来どおり)。選択: 旧 NO_CANDIDATE -> 新 SELECTED id=2 |

追加の反転: 旧 all_seven False -> 新 True になった候補は9件(META 3 + Gemini trial 6)、selection が旧 None -> 新 SELECTED になったファイルは3件。
旧 True -> 新 False は0件。
