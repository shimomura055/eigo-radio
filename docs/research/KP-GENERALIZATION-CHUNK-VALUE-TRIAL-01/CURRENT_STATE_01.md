# CURRENT_STATE_01: Key Phrase候補の現行経路・仕様確認(KP-GENERALIZATION-CHUNK-VALUE-TRIAL-01 委任_01)

調査日: 2026-10-30 / API 0(read-only確認) / Production file無変更。未確認事項は「未確認」と明記する。

## 1. 現行の「7候補提示→ユーザー最大3件選定」正式経路(file:line)

| 工程 | 実装・仕様 | 根拠 |
|---|---|---|
| 仕様の正本 | フレーズ最大7(P7)+単語最大5(W5')=候補上限12、Standard/Advanced × Family X/Y/Z、PRODUCTION_WIRED(Fable受入2026-10-27) | CURRENT_SPEC.md:2041-2048 |
| 候補抽出(call1) | P7 Prompt(`kp_prompt_p7`)。Prompt 2の件数文と条件6だけ置換した固定sha。モデル=gpt-6-luna(routing契約、SUPPORT_MODEL) | er119_kp_p7w5_prompts_01.py:24-43(P7_TEXT, sha 2e930193…固定)、er006_model_routing_contract_01.py:50 |
| 難易度優先 | P7条件4『上級者向けの学習価値』・条件5『易しい表現の除外(基本語だけで字面どおりに分かる表現を除外)』。ランキングは条件6『学習価値の高い順に最大7件・数合わせなし』 | 同:36-41(P7_TEXT条件4・5・6) |
| 単語候補(call2) | W5'(1語・最大5・KP含有語は除外) | er119_kp_p7w5_prompts_01.py:48-66 |
| 原型化・一般化・意味付与 | `sc.run_key_phrase_canonicalization`(fulltext版テンプレ) + gloss再整合 + 救済(er125)。**一般化は規則1〜5に限定**: 1文脈限定語(the/a/所有限定詞)の除去、2意味に必要な語の復元、3人称代名詞・所有格→one's/someone's/oneself(possessor_roles判定)、4語形の基本形化(lemma)、5指示語this/that→a/an・目的格him/her/me/us→someone。**目的語名詞のsomething化、目的語の削除、後続名詞句の除去は規則にない** | er003_v1_n3_01_scaffold_generate.py:475-、er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt:9-21 |
| 決定論検証 | 出力key_phraseは「display_phraseと同じ/文脈限定語を除いた形/source_span内の連続部分/規則3・4・5の1対1置換」のいずれかでなければならない(それ以外の辞書形の創作は却下) | 同テンプレート末尾の規則群、er003_key_words_canonicalization.py:529(`_is_valid_fulltext_normalization`)、er105_kp_fulltext_selector_01.py:1239 |
| Gate連鎖 | validate(本文一致・1〜5語)/CMU辞書/canonicalization(item単位除外・再実行最大2回 MAX_CANON_RERUN)/記号/人称整合(Z)/SRC D1(Z)/Human NG(exact)/提示前品質検査(presentable filter、仕様①)/Redundancy QA(アラームのみ、仕様②) | er119_kp_candidates_01.py:41,198-300、er119_kp_human_review_01.py:510-545 |
| 補完 | Gate除外件数Eが1以上のとき、種類別(フレーズ=P7/単語=W5')に1回だけ追加探索。初回合格候補は入替えない | er119_kp_candidates_01.py:558-、CURRENT_SPEC.md:2043 |
| 外側retry | 補完ON(既定)では候補0件と技術失敗のretryのみ | er119_kp_candidates_01.py:1-20(docstring) |
| 人間提示 | HR依頼書・選定フォームv3。候補は7+5=cap12、各候補のAI選定理由欄はユーザー向け画面では非表示(`reason_ja`は内部保持) | CURRENT_SPEC.md:2046-2047、docs/research/KP-GATE-DROP-BACKFILL-PRODUCTION-01/tools/export_form_data_01.py:32-38 |
| ユーザー選定 | KPは最大3件(+Advは単語解説最大5件、KP3件を含む)。`render_request_md`の文言 | er119_kp_human_review_01.py:1548 |
| 確定 | `finalize_kp`が`keywords_canonicalized.json`を書く唯一の場所。AUTO規則`auto_select`(KP=先頭3)はAI推奨表示・HR回避時の決定論 | er119_kp_human_review_01.py:1241、:705-709 |

## 2. 「最大3件を選定する旧・別経路」との混同確認

- 旧経路=**Prompt 2(AIが3件選ぶ)**と**Prompt 2-V(語彙最大5)**。本文は「新経路では使わない・旧runのresume・復帰用に残置(git revertで復帰)」(er119_kp_p7w5_prompts_01.py:1-12、CURRENT_SPEC.md:2043-2044)。KP_CANDIDATE_MAX=8は撤去済み(CURRENT_SPEC.md:2045)。
- 現行の「最大3件」は**ユーザーが候補から選ぶ上限**(HR依頼書の文言 er119_kp_human_review_01.py:1548)であり、AIの選定件数ではない。`auto_select`の先頭3(:705)もAI推奨/HR回避時の決定論であり、提示候補数(7+5)とは別。
- 結論: 「AIが7提示→ユーザーが最大3」が正式経路。仕様と実装の**矛盾は検出されず**。ただし次の整理が必要:
  1. ユーザー指示の「7候補」は**フレーズ枠(P7)のみ**。実際の提示は7(フレーズ)+5(単語)=12で、単語枠は別Prompt(W5')。本Trialはフレーズ枠を対象とし、単語枠は「単語単独で価値がある場合の振り分け先」として扱う(word_candidates)。
  2. 提示される候補は**実運用では7件に満たない**(Gate除外・shortfall)。実測(fx4_01の8 doc): フレーズ枠はStd 4〜6件、Adv 5〜6件(call1+補完、最大7に未達)(`kp_candidates.json`のcandidates)。
  3. HR画面ではAI選定理由欄が**非表示**(CURRENT_SPEC.md:2047)。塊としての価値説明(chunk_reason)は内部記録として保持でき、ユーザー画面の変更は不要(採用時に表示するかは別判断)。

## 3. 現行の問題の所在(実測: Before)

- 一般化: Production canonicalizationは規則1〜5以外の変換を禁止しているため、`take points away from`/`make life work`/`narrow down the source`/`turn the usual steps around`/`at the time of writing`は**設計上そのまま通る**(不具合ではなく仕様上の限界)。`hear it out`のitも規則3(it/themは列挙外)で未一般化。→ 改善は「規則の拡張」ではなく**学習表示用の一般化の新しい責務**(本文一致ルールとは別)として設計する必要がある(ユーザー指示3節『既存の本文一致ルールと学習表示用の正当な一般化を区別する』と整合)。
- 塊価値: P7条件3〜5は「難易度」中心で、『自由な組合せ(F)』と『塊(C)』を区別する条件がない。`confirm a clear fall`(4語、はっきりした減少を確認する)は条件1・2・4を満たしてランク1で通る。
- 実測(fx4_01 Before、フレーズ種別のみ): ユーザーが修正せず選べる候補の割合は Std/Adv 12ケース計 26/66(39%)(Sonnet実読。RESULT_01.md参照)。

## 4. retry/fallback/regeneration/resumeとの関係(採用時の影響範囲)

- 初回経路: `generate_candidates`→`_gate_chain`(canonicalization以降)。新しい一般化段を入れる場合は、`_gate_chain`の canonicalization(+gloss再整合)の**置換または前置**になる(er119_kp_candidates_01.py:198-260)。外側retry・補完・resume(保存済みdoc再利用、API 0)はdoc形式(`used_form`/`japanese_gloss`/`item`)を共有するため、新段が同形式のdocを出す限り変更不要。
- 補完(backfill)は同じ`_gate_chain`を通る(R-6純抽出)ため、一般化段を`_gate_chain`内に置けば初回と補完で共通化される。
- Validator: 本文一致(1〜5語)は`source_span`に適用し続け、`used_form`(=学習表示用)には「核語がsource_span由来の語形違い、プレースホルダ置換はsomething/someone/one's/oneselfのみ」という**別のvalidator**が必要(本Trialで`kpg01_validate.py`として試作)。
- Human NG再採用禁止: 照合は`used_form`に対して行われる(er119_kp_candidates_01.py:271-284)。一般化後の形でNG照合されるため、過去のNG履歴との整合(旧used_form vs 新used_form)は採用時に要確認(未確認)。
- Family/レベル差: X/Y/Z共通経路(CURRENT_SPEC.md:2041)。Z(物語)は人称整合(person_repair)・SRC D1が追加で入る(er119_kp_candidates_01.py:150-180)ので、新段との順序を要設計。
- 過去Trial(関連、再発明を避けるため確認): FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01(possessor_roles/A-1, OPEN-474)、KP-CANDIDATE-PHRASE7-WORD5-TRIAL-02、FAMILY-X-KP-SELECTION-PROMPT-MIN-AND-GENERALIZATION-TRIAL-02、OPEN-349(span外補語の一般化=新規許容ルール要否、USER_DECISION_REQUIRED起票)。本Trialの『目的語のsomething化・後続名詞句の除去』はOPEN-349と同系統の**新しい許容ルール**にあたるため、採用はユーザー判断(未承認のためProductionへは入れない)。
