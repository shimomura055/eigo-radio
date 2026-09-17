管理ID: USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01(Closeout部分、項目2〜6)

0. T-0: 委任文を`docs/pm/delegation_log/USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01_closeout.md`へ保存、`check_delegation_prompt.py`実行=`FAIL`(理由: 「性質」「事前指定Grep一覧+追記位置の手順」「実行コマンド全文」の見出しキーワード欠落。テンプレ非準拠だが記録のみ、続行)。結果json: 同ディレクトリ`..._check.json`。

1. Space Weapons A2差分確認: `c2af33f2..6d088d2e`は19ファイル変更、全てaudit/web成果物・attempt記録・regenスクリプト。`parts.json`は`title_tts`1行追加のみ、`title`/`part1`/`part2`等は無変更。`article.md`/`a2_support_texts.json`/`key_phrases/`は差分なし。`tts_generation_results.json`全segment sha256比較で`topic_intro`のみ変更、他13narration+10support segmentは全一致。episode.mp3/topic_intro.mp3の変更はtopic_intro差し替えに伴う再assemblyの結果。→タイトル以外無変更を確認、`USER_TEST_READY`。

2. Status整理: AI Control A2/B1=`USER_TEST_READY`(試聴PASS、情報密度の重大指摘→OPEN-164)。Space Weapons A2=`USER_TEST_READY`(1節の確認後)。Space Weapons B1=`USER_TEST_READY`(レイアウト修正のみ、再試聴不要)。Personalized News A2=`REJECTED_AS_CURRENT_OUTPUT`(Voices構造根本問題、実装基盤`main_a2_2v()`は`WIRING_INCOMPLETE`のまま変更なし)。**訂正(PM-CLOSEOUT-CONSOLIDATION-137、Fable受入照合)**: 「実装基盤`WIRING_INCOMPLETE`」は誤記。FIX-01で`PRODUCTION_WIRED`到達済み(CURRENT_SPEC L669、OPEN_ITEMS.md OPEN-151行参照)。

3. OPEN-164全文: `OPEN_ITEMS.md`新規行(OPEN-163直後)。要旨=CEFR言語難易度調整とは別にListening Newsとしての情報密度・前提知識依存・概念密度・難語密度制御が必要。観点(information density/prerequisite knowledge/conceptual load/number density/difficult but non-technical vocabulary/abstract concept density/論点数/audio-only理解可能性/script不要理解/Fact全部入れない編集判断/Storytelling Firstとのバランス)を明記。優先度=中〜高、期限=量産開始前。今回のAI Control A2/B1は再生成しない。

4. OPEN-151追記: 「Personalized News A2現行版ユーザーNG、`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-REVIEW-01`で仕様見直し継続中(USER_DECISION_REQUIRED想定)、実装基盤`WIRING_INCOMPLETE`は不変」を該当行末尾へ追記(`OPEN_ITEMS.md` L295相当行)。**訂正(PM-CLOSEOUT-CONSOLIDATION-137、Fable受入照合)**: 「実装基盤`WIRING_INCOMPLETE`は不変」は誤記だった。実際はFIX-01で基盤Status=`PRODUCTION_WIRED`へ到達済みであり、OPEN-151行を訂正済み。

5. DECISION_LOG行: 新規エントリ`## USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01`(索引行+本体エントリ、ファイル末尾`## 参照元`直前に追加)。5本のStatus・OPEN-164新規登録・AI Control難易度問題の整理結論を記録。

6. CURRENT_SPEC注記: L670(新規topic A2 Production経路行)へ2026-09-17追記を付加。「初回生成記事[Personalized News A2]はユーザー品質NG[Voices仕様レビュー中]、本行の基盤Status`PRODUCTION_WIRED`は変更しない」と明記。新規のVoice役割仕様は書いていない。

7. ARTIFACT_REGISTRY追記: 新規セクション「News-family(Space Weapons/AI Control/Personalized News A2、2026-09-17追加)」を`## 参照元`直前に追加。5行(Space Weapons A2/B1、AI Control A2/B1、Personalized News A2)、User Quality列にPASS×4/NG×1・URL・Gate結果を記載。

8. 難易度調整の既存仕様確認: `CURRENT_SPEC.md` L538(vocabulary、CEFR外語彙・wordlist数値ルール化は`REJECTED`、これがユーザー言及の「過去Trial却下」の裏付け。DECISION_LOG独立エントリはgrepで見つからず、CURRENT_SPEC.md本文内へインラインで記録されている形)、L539-542(平均文長11語以下/最長18語以下/1文1メッセージ、生成方針でありgateではない)、L606(B1-B Direction Control原則、診断的原則・hard rule追加禁止)。結論=AI Controlの難しさはレベル調整未実施ではなく情報設計・概念負荷の問題(OPEN-164として分離)。

9. Git SHA: 作業前HEAD=`ce33f48a`(origin/mainと一致、fetch確認済み、マージ不要)。commit=`609794fb`(SSOT4ファイル+ARTIFACT_REGISTRY.md+delegation_log2件+本RESULT_PACKET、計7ファイル)、`git push origin main`成功(`ce33f48a..609794fb`)。`docs/pm/ACTIVE_TASK.md`は`.gitignore`対象のためcommit対象外(想定どおり)。

10. API 0証跡: 本タスクはgrep/diff/git操作・ファイル編集のみ、外部API呼び出し・TTS実行なし(コマンド履歴上、`.venv`実行はcheck_delegation_prompt.py[ローカルツール]のみ)。

11. 未決事項/事前指定外Read: OPEN_ITEMS.md本体先頭の「最終更新」要約行はPM-CLOSEOUT-CONSOLIDATION専用の慣行のため本タスクでは更新していない(次回consolidationで反映想定)。DECISION_LOGの語彙数上限却下に関する独立エントリは存在せず、CURRENT_SPEC.md本文の記述のみが根拠(8節参照)。事前指定外のRead/Grepは行っていない。ユーザー向け表記は全箇所「B1」で統一済み。
