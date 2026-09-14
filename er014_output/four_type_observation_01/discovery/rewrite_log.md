# Discovery No Jargon Fix / B1B / Key Phrase - rewrite_log
(STOP: budget exceeded before Key Phrase generation. This file was reconstructed
after a mid-run crash from on-disk artifacts only, with zero additional API calls.)

## A2 修正(使用経路: 既存rewrite経路 rewrite_ng_item + apply_diff_qa_to_resolved_rewrite、
委任文(1)(a)。理由: 優先指定された経路であり、両ブロックとも初回でLEDGER_COMPLIANT受理、
manual escalationは不要だった)

### Block 1 (section: "Quiet Does Not Always Mean Calmest")
terms_detected: EKG, acoustic noise, counterbalanced, fMRI, parasympathetic,
physiological arousal, sympathetic activity

旧:
In a counterbalanced EKG experiment, parasympathetic activity was higher during
fMRI acoustic noise than during silence, while sympathetic activity was higher
during white noise than during fMRI noise. Feeling calm and producing the lowest
physiological arousal are therefore different claims.

新:
In an experiment that balanced the order of the sounds, heart measurements showed
that the body's rest-and-recovery system was more active during noise from an MRI
scanner than during silence, while the body's alerting system was more active
during white noise than during the MRI noise. Feeling calm and having the lowest
level of bodily activation are therefore different claims.

Fact意味維持の確認: (a) 比較対象(rest-and-recovery system vs MRI scanner noise/silence、
alerting system vs white noise/MRI noise)は変更なし、(b) 方向(どちらがより高い/active)は
両方とも維持、(c) 結論(feeling calm と最低活性化は別物)は維持、(d) 新規Fact追加・因果強化
なし。diff QA(Fact Checker A' + Ledger Deviation Checker再実行)結果:
blocks_acceptance=False(受理)。jargon_after: hit_count=0。

### Block 2 (section: "The Person and the Relationship Matter")
terms_detected: correlates, need for cognition, positive affect

旧:
Enjoyment of thinking for pleasure was associated with need for cognition,
openness, meditation experience, initial positive affect, and lower phone
use—but these were correlates, not proven causes.

新:
Enjoyment of thinking for pleasure was linked with a preference for thinking
deeply, being open to new experiences, meditation experience, feeling more
positive at the start, and using a phone less—but these were related factors,
not proven causes.

Fact意味維持の確認: 5項目のリスト(preference for thinking deeply/openness/meditation
experience/positive affect/phone use)は増減なし、相関(correlates)の強さは
"related factors, not proven causes"としてcausal強化なく維持。diff QA結果:
blocks_acceptance=False(受理)。jargon_after: hit_count=0。

## B1B(既存Production正式関数run_one_pattern_staged_discovery_focus(level="b1b")で新規生成)

生成直後jargon scan: hit_count=1(語は生成完了ログでは個別に保存されていない。
クラッシュ発生[budget exceeded]によりB1B生成直後の原文[fix前]のバックアップが
本ドライバの実装漏れにより保存されていなかったため、修正前後のsentence-level diff
は再現できない。既知の事実: fix実行後、b1b/article.md line 15は"In a study that
measured heart activity, one noise condition showed more activity linked with the
body's calming system than silence, while white noise showed more activity linked
with its alerting system than that noise."であり、専門語(parasympathetic等)は
含まれず、A2側と同じ方向性[calming system higher during 該当noise than silence、
alerting system higher during white noise than 該当noise]を維持している(目視確認)。
fix適用: 既存rewrite経路(rewrite_ng_item+apply_diff_qa_to_resolved_rewrite)、
初回でLEDGER_COMPLIANT受理・manual escalation不要。

修正後jargon scan(article.md実ファイルへの再scan): hit_count=0。

## Key Phrase

**未実施(STOP: 費用上限超過)**。A2/B1BいずれもKey Phrase再生成に到達する前に
budget guardが発火し停止した。

## STOP理由

B1B post-fix final QA(Ledger Deviation Checker再実行)呼び出し中に、本タスク増分
実測費用が¥157.32となり上限¥130.00を超過したため、driver側budget guardが
RuntimeErrorを送出しmain()が異常終了した(uncaught exception、既存の3STOP分岐
[a2_needs_regeneration_fallback / budget-before-b1b / no-article-text]のいずれにも
該当しない箇所での発生であり、rewrite_log.md/cost_summary_fix.json等の正常な
書き出しコードへ到達しなかった)。本ファイルはクラッシュ後、追加API呼び出しゼロで
既存のディスク上artifact[raw_usage_log.jsonl・a2_before_fix/・reader_facing_article*.txt・
b1b/article.md・各audit JSON]のみから手動再構成した。
