# GLOSS_ROOT_CAUSE_AND_FIX_04 (委任_04 1-2、KP gloss不整合の根本是正)

管理ID: FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_04。ユーザー指示(2026-10-14): 最終英語KPと日本語glossの意味的整合は基本品質要件。G1/G2/G3選択は撤回、Human Reviewへ戻さず自動で整合させる。

## 1. 工程順序(実コード・記録で確認)
```
[Stage1 候補生成 / M2供給]  surface_form候補(例 C1 "based on")  ※glossなし
        |
[選定LLM  DB Hybrid selector / Strategy L]   承認済みPrompt: 「選ぶ表現は本文中の実表現(source_span)に対応させ、
        |                                     短く自然な日本語グロスを付けてください」 ... 以降のglossの規則(自然/括弧禁止/「～」可/漢数字)
        |   → 5 item {rank, source_span="based on", display_phrase="based on", ja_gloss="～をもとにした"}   ★glossはここで確定
        |      (keywords_selector_prompt.txt / keywords_runtime_metadata.json)
[canonicalization LLM  別呼出]  入力 = {rank, display_phrase, source_span(案A'で原文窓に拡張), source_sentence} のみ(**glossを含まない**)
        |   → key_phrase="based on interviews"  (Rule7: A'窓内の連続部分文字列でPASS)
[merge_canonicalization_result]  japanese_gloss = original["ja_gloss"] をそのまま引継ぎ(★KPが変わってもglossは再生成されない)
        |   japanese_gloss_tts = 「～」→「なになに」の決定論変換のみ
[Redundancy QA]  KP同士の重複のみ判定(gloss整合は見ない)
        v
keywords_canonicalized.json → Std/Adv KP音声(Stdは英語KP + 日本語gloss TTS)
```
gloss生成は**選定段の1回のみ**(候補span/display_phrase基準)、最終KPは**後段canonicalization**が確定。両者の間に「KP確定後にglossを再整合する工程」も「gloss整合を検証する機構」も存在しない(fact_check/ja_gloss検証/gloss再生成・retry経路は未存在をgrepで確認: ja_glossを検査するコードは音声化禁止記号・placeholder記法のみ)。

## 2. 原因(仮説の検証)
- 仮説「glossが候補span 'based on' から先に生成され、A'でKPが 'based on interviews' に確定した後に再生成されない」= **実記録で確認**。`key_phrases_db_hybrid/keywords_runtime_metadata.json`(選定時 ja_gloss=「～をもとにした」)と `canonicalization_runtime_metadata.json`(KP='based on interviews'、入力にgloss無し)、`keywords_canonicalized.json`(japanese_gloss=選定時のまま)。
- 構造的欠落であり案A'固有ではない: Rule7はKPをsource_span内に制限していたが、`restore_semantic_complement`(span内の補語復元)や活用形/一般化でKPがdisplay_phraseと異なる経路は元々あった。案A'で窓が右拡張されKPが候補より伸びる機会が増えただけ。
- 反証の試み(census、API 0円): `gloss_census_extra_04.json`。er*_output配下の keywords_canonicalized.json 714ユニーク(display, KP, gloss)三つ組のうち、KPがdisplayに無い語を含むもの(活用形・人称一般化を除く)は**5件**(0.7%): 『based on interviews』『locked into a narrow view』『close around me』『urge to watch』(×2 gloss違い)。残り709件はKP語⊂display語(または人称一般化/活用形のみ)でgloss整合は構造上保たれる。
- 伸びたKP 5件のgloss整合(目視): 『based on interviews』=不整合(「～」スロットでinterviewsを反映せず)/『urge to watch』=不整合(『～したい衝動』でwatch未反映)/『close around me』=弱い不整合(『周りから迫ってくる』でmeを反映せず)/『locked into a narrow view』=整合/ ほか1件(同一KPのgloss違い)。→ 伸びたKPの約3/5が不整合=偶発でなく**構造的**。

## 3. 是正(Prompt/Rule7/Validator/Gate/A'無変更・既存機構を再利用)
新規 `er003_key_words_gloss_alignment.py`(工程追加は最小の1段、(c)に相当。(a)(b)は不可能と判断: 既存のgloss生成経路は選定LLM呼出に内包されKP確定後に単独で再実行できず、既存の整合検証機構は存在しないため)。
- 配線: `er003_v1_n3_01_scaffold_generate.run_key_phrase_canonicalization`(初回/Redundancy retry/Strategy L fallback/regeneration**全経路が通る**唯一の関数)内、`merge_canonicalization_result`直後・保存前。
- 対象: 最終KPが表示候補display_phraseに無い語を含むitemのみ(活用形/人称一般化/冠詞増減は除外)+`kp_extends_beyond_candidate=true`。**対象0件ならAPI呼出なし**(変更なし)。
- 入力: 最終KP・候補・現gloss・source_sentence・記事本文。出力: 現glossが整合しているか判定(整合なら同一文字列を返す)+最終KP全体に一致するgloss+自己検証。
- gloss生成規則は**承認済み選定Promptテンプレート(`b1_p2_keywords_l_prompt_template.txt`)の『日本語グロス…』段落を実行時に抽出して流用**(複製・改変なし)。routing=同じSUPPORT_MODEL(`gpt-6-luna`、routing.require_model経由、モデル不一致検出あり)。
- 検証(既存規則を流用): 括弧禁止・算用数字禁止・「…」禁止・音声化禁止記号(`safety.detect_prohibited_symbols`、TTS変換後に判定)・rank整合・自己検証PASS。retry上限2(canonicalization retry上限と同じ思想)。
- それでも整合できない場合: **Human Reviewへ送らず自動でKPを表示候補display_phraseへ戻す**(候補とglossは元々整合)。record に `gloss_alignment.status=FALLBACK_KP_REVERTED_TO_DISPLAY_PHRASE` を残す。
- 監査: `gloss_alignment_prompt.txt`/`gloss_alignment_runtime_metadata.json`、itemに`gloss_alignment{status,original_japanese_gloss,reasoning}`。
- **新Production仕様候補としての注意(Fable判断事項)**: 新しい処理フロー1段+新Promptの組み立て(規則文は承認済みPromptから流用、課題指示文は新規)を含む。承認済みPrompt本文・Rule7・Validator・Gate・A'・Style・N01は一切変更していない。Opus条件A(新しい処理フロー)相当のため、Production採用(`APPROVED_FOR_PRODUCTION`)の位置づけと独立レビューの要否はFable/ユーザー判断。

## 4. 効果(Before/After、実API)
| 対象 | Before | After |
|---|---|---|
| Coffee Std KP #4 | KP『based on interviews』/gloss『～をもとにした』/TTS『なになにをもとにした』 | KP『based on interviews』/gloss『インタビューをもとにした』/TTS『インタビューをもとにした』(`gloss_alignment` GLOSS_REALIGNED、Std KP5件すべて整合) |
| census 伸びたKP 5件(`gloss_census_replay_04.json`) | 整合1〜2 / 5(不整合3: based on interviews / urge to watch / close around me) | 整合5 / 5(『urge to watch』→『見たいという衝動』、『close around me』→『私を取り囲む』、既に整合の『locked into a narrow view』は**無変更**=過剰書換え0) |
| gloss整合率(714ユニーク三つ組) | 709 + 伸びた5件中2件 = 約99.6% | 714/714(伸びた5件すべて整合) |
- 注: census replayの『based on interviews』行は、Coffee記録が既に再整合済みのためBefore欄が整合後の値になっている(Beforeは`keywords_canonicalized_before_gloss_align_04.json`で『～をもとにした』)。

## 5. 副作用・Regression
- 既存test: er003_test_key_words* **354**(既存332+新規22)/ er003_v1_n3_01 **55** / er019 **421** / er030 **108** 全PASS、失敗0(`regression/*_final.log`)。新規test 22件(`er003_test_key_words_gloss_alignment.py`: 対象判定/再整合/整合済み無変更/retry/2回失敗でKP自動復帰/規則抽出/モデル不一致/Production関数経由の統合3件)。
- A'維持: 原文窓拡張ロジック・5語上限・左端ガード・Rule7判定は無変更(KPを増やす/伸ばす処理は追加していない)。唯一KPを変えうるのはfallback(KPを候補へ戻す=短くする方向、原文外拡張は構造上発生しない)。
- 初回/retry/fallback/regeneration: 全経路が`run_key_phrase_canonicalization`経由=同一工程(統合testで確認)。Family Zを含む`sc.run_key_phrases`呼出元は自動的に同じ工程を通る(対象0件なら無影響)。
- 対象外: `kc.merge_canonicalization_result`を直接呼ぶ旧Trial/他runner(er073等)は未配線(Production量産経路ではない)。

## 6. 量産コスト
- gloss再整合は対象itemがある記事のみ・1記事(1レベル)あたり1呼出(バッチ)。入力約5KB(約2〜3k token)、SUPPORT_MODEL、reasoning high。既存canonicalization呼出(実測約JPY0.4)と同等以下=**約JPY0.3〜0.5/呼出(推定、canonicalizationと同様Productionの費用ログ未計測)**。
- 頻度: 伸びたKPは過去714三つ組で0.7%、案A'再生では15 item中1(約7%)+Coffee5 item中1。1記事(5KP)で対象ありとなる確率は約5〜15%(A'下)。
- 70円/記事セット(2レベル)への影響: 約JPY0.3〜0.5 x 2レベル x 5〜15% = **約JPY0.03〜0.15/記事セット(約0.05〜0.2%)**。API失敗時は2回retry(最大+JPY0.5)後に自動でKPを候補へ戻す。
