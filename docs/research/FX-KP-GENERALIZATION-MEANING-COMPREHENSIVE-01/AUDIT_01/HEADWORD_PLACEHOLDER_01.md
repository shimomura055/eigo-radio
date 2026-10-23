# HEADWORD_PLACEHOLDER_01: 見出し語の人称placeholder(one's/someone's)の出所と規定(委任_12 §3、read-only・事実のみ・改善提案なし、2026-10-23)

## 1. 出所(2KP)
| 見出し語 | 出所 | 本文の元表現・指示対象 | 備考 |
|---|---|---|---|
| `reach for someone's wallet` | Trial_01 a1gE0 rep1(A-1プロンプト、LLM選定)の出力: `er112_output/kp_gm_trial_01/runs/a1gE0/rep1/X_family_x_audio_production_wiring_01_uk_train_speaker_playback_run_nws_02__b1b/result.json`(display_phrase=`reach for your wallet`、source_sentence=`That's enough to make you reach for your wallet before the volume button`、normalization_reason=None)。Trial_02/03のHARD20は `er112_kp_gm_trial_02.py:31` で手書き固定、`kp_probe_03.py:56-65 load_kps` が上記result.jsonから取得 | `your wallet`=二人称(読者=本文の「あなた」)自身の財布 | **同じ元表現・同じ記事(nws_02)のProduction a2は `reach for one's wallet`**(`er019_output/family_x_audio_production_wiring_01/uk_train_speaker_playback__run_nws_02/a2/key_phrases/keywords_canonicalized.json`、source_span=`reach for your wallet`、reason=`generalize_person_dependent_reference`)。同一display_phraseからrunにより one's / someone's の両方が出ている |
| `apply one's findings` | `er112_output/kp_gm_trial_01/a3_verify/units_a3verify.json` の `boredom_aggression__run_bape_01`(display_phrase=`apply its findings`、used_form=`apply one's findings`、source_sentence=`We can't apply its findings directly to everyday meanness or boredom that lasts a long time`)。`census_items_02_extended.json:116-122` も同じ(reason=generalize_person_dependent_reference) | `its`=本文が指す研究(人ではない) | `its`→`one's` はProduction表で許可された唯一の対応(下記2-b) |

## 2. Production側の規定(file:line)
- (a) 選定プロンプト規則3: `er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt:11`。my/your/his/her/their/our/its、you/they/he/she、yourself等が「記事固有の誰かを指しているに過ぎない場合」、「辞書の見出し語として使われる標準的な一般形(one's/someone's/somebody's、someone/somebody/one、oneself等、英語学習辞書がこの種の表現を掲載する際に使う慣例的な形)へ置換」。例は `catch their attention→catch someone's attention`・`a piece of your attention→a piece of someone's attention`。**one's と someone's のどちらを選ぶかの基準は記述なし**(「迷う場合はreasoningで説明し、より自然だと判断する側を選ぶ」のみ)。本文の指示対象が主語自身か他者かを考慮する旨の記述: **規定なし**。`pump its fist→pump one's fist` の例が規則4(:12)にある。
- (b) 決定論validator `er003_key_words_canonicalization.py:431-449` `_PERSON_DEPENDENT_TO_GENERIC`: my→{one's}、**your→{one's, someone's, somebody's}**、his/her/their→{one's, someone's, somebody's}、**its→{one's}**、our→{one's}、you/they/he/she→{someone, somebody, one}、yourself等→{oneself}。`:452-473 _is_valid_person_generalization` は語数同一・1対1置換がこの表の許可集合内にあればTrue。**表は許可集合を与えるだけで、one'sかsomeone'sかの選択規則・指示対象(主語自身/他者)を判定する処理はなし**。よって `your wallet→one's wallet` も `→someone's wallet` も機械的には両方合法。
- (c) 日本語意味側の整合: `er003_key_words_gloss_alignment.py:119`(_GENERIC_TOKENS)・`:169`(_REFLEXIVE_EN={one's, oneself})・`:205-228 person_reference_mismatch`: 見出し語が不定の人称を持ち、日本語意味が具体的な人称語(あなた/私/彼/君…)を含めば不整合。**one'sを含む見出し語は「自分/自身」を許容、someone系のみの見出し語で「自分」は不整合**(:206-209の docstring)。「相手/その人/人」は不定の自然な訳として検出しない。すなわちProductionは `one's` ⇒ 自分の可、`someone's` ⇒ 他者(不定の人)の読みを規定している。
- (d) 規則5(A-1、Trial専用 `er112_kp_gm_trial_01.py:94-108 A1_RULE5`、WIRING_DESIGN_01.md:5・12・18): this/that→a/an、**目的格 him/her/me/us→someone** のみ。所有格(your/its等)は規則3の扱いと明記(:102)で、規則5は対象外。したがって `reach for someone's wallet` のsomeone'sは規則5由来ではなく規則3の枠内でのLLM選択、`apply one's findings` のone'sは規則3+表(its→one'sのみ)由来。

## 3. 記事Bの実KP `reach for one's wallet` がone'sになった規則
- Production a2の `keywords_canonicalized.json` に `key_phrase=reach for one's wallet`・`normalization_reason=generalize_person_dependent_reference`。適用規則は上記(a)規則3。one's/someone'sのどちらを選ぶかの規定はなく、(b)の表では両方許可されるため、**この回のLLMがone'sを選んだ**ということ以上の規則上の理由は確認できない(規定なし)。DESIGN_01.md:62・DESIGN_01.md:77・WIRING_DESIGN_03.md:50 も同KPを `reach for one's wallet` と記載(文書上の確認のみ)。
- 確認できなかった点: Trial_01 a1gE0 rep1で同一display_phraseからsomeone'sが出た理由(LLM出力の揺れか、A-1プロンプト差分の影響か)は未確認(推測しない)。

## 4. 要約
- 出所: `reach for someone's wallet`=Trial_01 a1gE0 rep1のLLM選定出力(Productionの同一表現はone's)、`apply one's findings`=its→one'sの表規定どおり。
- 規定の有無: 一般化先は許可集合(表)と「辞書慣習の標準形」のみで、one's/someone'sの選択基準と、本文の指示対象(主語自身/他者/人でないもの)を考慮する規則は**規定なし**。日本語意味側だけがone's=自分可・someone's=不定の人、と区別している(gloss_alignment:205-228)。
