# FAMILY-X-KP-IDIOM-EXTRACTION-SELECTION-TRIAL-01 / Phase A: 診断と改善設計(2026-10-12)

範囲: 読取+ローカル実行のみ。API呼出0、ネットワーク呼出0(Wiktionary APIも未使用)、費用JPY0、Production code/prompt無変更。
本書の「事実」は保存ファイル・コード・ローカル再実行で確認したもの。「推測」は明示する。
既存調査 `docs/pm/delegation_log/2026-10-12_FAMILY-X-COFFEE-KP-SELECTION-INVESTIGATION-01.md`(以下 INV-01)の確認済み事実は再調査せず引用する。

## 0. 結論(最重要)

| # | 結論 | 根拠 |
|---|---|---|
| 1 | `pumps its fist` と `mark the date on your calendar` は、**n-gram生成は通過したが、DB照合(段2)で「ヒット0」となり候補化されなかった**。後段(重複除去・機械gate・文脈除外・shortlist上限・LLM選定)には到達していない | `trace_targets_local_01.json`(2節)。v4 Std/Advとも当該文の n>=2 の部分n-gram全件がDB不一致 |
| 2 | **支配要因 = DB未収録**(CEFR-J/NGSL/Wiktionary 3カテゴリのどの見出しにも `pump ... fist` も `mark the date` も無い)。続いて **placeholder見出し未対応**(仮に `pump one's fist` が収録されていても現行照合では `pumps its fist` にヒットしない=注入実験で実証) | 3節、`sim_inject_db_entries_01.json` |
| 3 | LLM選定は「候補一覧に無い表現は選べない」契約。候補に出ない以上、Promptだけでは2表現は救えない。**DB側だけの改善(a,c,d)では2ターゲットは回復しない。回復には非DB経路(b: 非透明表現の補助抽出)が必須** | 4節、7節 |
| 4 | 現行DBで抽出できるIdiomは「固定形+語形変化(代名詞slotなし)」まで。`one's/someone's`等のplaceholder見出し(Wiktionary idiom 10,632件中1,505件=14.2%、phrasal verb 5,169件中101件)は、本文が `her/his/its/my` になると原則ヒットしない(自作10文の実測: 該当3文は3/3失敗) | 5節 |
| 5 | v4 Stdの重要語4件(`push prices up`/`take time`/`right away`/`on a regular basis`)は、phrase候補が8件しかなく高頻度・透明に近い表現が中心だったため。**Wiktionaryの「idiom」ラベルは非透明性を意味しない**(`take time`/`of a`/`At that`もidiom) | INV-01付録A、本書4,5節 |

## 1. 入力と再現性

- 対象原稿: ユーザーが試聴するv4原稿(tone run `run_e_tone_01` の article.md)。`parts.json` sha256 は main の `er057_output/coffee_final_listening_tone_trial_01/part_45/evidence_snapshot/{a2,b1b}/parts.json` と一致(a2 `f4421bd8...`、b1b `5634890b...`)。ローカル複製: `inputs/v4_std_article.md` `inputs/v4_adv_article.md`(tone worktree の article.md を読取複製)。
- 当該文: Std `When you hear that, your wallet pumps its fist` / Adv `At that news, your wallet pumps its fist`。両Levelとも `It is too soon to mark the date on your calendar`(article.md L3, L17)。
- 再現性確認: 現行 `er030_key_phrase_db_hybrid_core_01.run_stage1_for_article` をAPI・ネットワークなしでローカル実行し、INV-01記録値と**完全一致**(Std tokens439/before_dedup439/after_dedup204/stage_a156/stage_b155、Adv 489/499/226/181/180)。ローカル再実行は本番と同一ロジックの再現として有効。
- DB実体(`er023_output/key_phrase_db_trial_01/db/`、`er023_key_phrase_db_ingest.py:27-37`):
  - CEFR-J 7,035語(うちmultiword 145)、NGSL family 14,146語、Wiktionary title集合 16,317キー(idiom 10,632 / phrasal_verb 5,169 / proverb 1,588 titles。idiom+phrasal重複983、idiom+proverb 71)。
  - Wiktionaryは3カテゴリの**title一覧のみ**(語義・例文・活用情報なし)。`multiword_term` は実行時のonline lookup(後述)。

## 2. どの段階で消えたか(実測)

処理段(INV-01 §4): ①n-gram生成(`er023:85 generate_ngrams` 1-5語、core:350) → ②DB照合(`er027:201 match_candidate_with_irregular_rescue` → `er023:176 match_candidate_against_group1`、core:351-353 で `db_match_count==0` は `continue`) → ③重複除去(`er023:322`、core:365) → ④機械gate(core:367-376) → ⑤文脈不一致除外(core:378-380、`er028:88`) → ⑥phrase上位cap(`er027:639 build_shortlist` phrase_cap=15) → ⑦LLM選定。

### 2-1. `pumps its fist`(Std/Adv同一結果)
- ①通過: 部分n-gram 6個(1語3+2語2+3語1)が生成された。
- ②**消滅**: n>=2 の `pumps its` / `its fist` / `pumps its fist` はすべて db_match_count=0。ヒットしたのは単語 `pumps`(cefr_j+ngsl_family)と `its` のみ(`trace_targets_local_01.json` の multiword_subngram_hits=[])。
- 単語 `pumps` は word_survivors に残った: Std は希少度順4位でshortlist(word上限5)に入った(C25 `pumps`、INV-01付録A)がLLMは選ばず / Adv は6位でword上限5のため shortlist脱落。ただし単語 `pumps` はMUSTの `pumps its fist`(擬人化比喩の複数語表現)の代替にならない。
- Wiktionary multiword online lookup(core `run_stage1_and_shortlist`、budget 60)でも拾われない: 未一致の2-3gramプールは Std 623 / Adv 694 件で、先頭60件(2語・content語2個を優先し以降アルファベット順、`er027:601`)しか問い合わせない。`pumps its` `its fist` `mark the` `mark the date` は全て範囲外(`trace_wiktionary_lookup_budget_01.json` の probe_in_budget60 が全てfalse)。しかも問い合わせは `Category:English multiword terms` のliteral title一致のみ(活用・所有格正規化なし、`er023_key_phrase_db_ingest.py:141-186`)。

### 2-2. `mark the date on your calendar`
- ①: 6語表現そのものは `max_n=5`(`er023:85`)のため**生成されない**。部分n-gram(`mark the date` 等20個)は生成される。display_phraseも1-5語上限(Prompt L5)なので最小単位は `mark the date`(3語)が自然。
- ②**消滅**: n>=2 の部分n-gram全てがDB不一致。ヒットは単語 `mark`/`date`/`calendar` 等のみ(word_survivors の希少度順位: `mark` 69位(Std)/77位(Adv)、`date` 76/88、`calendar` 14/20。いずれもshortlist word上限5に遠い)。
- 注: `mark the date` 見出しが仮にDBにあれば**現行ロジックでヒットする**(注入実験で phrase_survivors に出現)。この表現の主因は純粋な「DB未収録」。

### 2-3. 実証ファイル
`trace_targets_local_01.py/.json`、`trace_wiktionary_lookup_budget_01.py/.json`、`sim_inject_db_entries_01.py/.json`(同dir。`.venv` のPythonでローカル実行。DBはメモリ上コピーに仮想見出しを入れるだけでDBファイルは書換えなし)。

## 3. 支配要因の分解

| 要因 | 判定 | 根拠(実測) |
|---|---|---|
| DB未収録 | **支配的(両ターゲット)** | Wiktionary idiom titles中 `pump` を含むもの6件(`prime the pump`/`pump out`/`pump someone's tires` 等)、`fist` 5件(`hand over fist` 等)、`pump ... fist` は0件。`mark the date` を含む見出しは idiom/phrasal_verb/proverb 全てで0件。CEFR-Jにも無し。(注: ローカルdumpに無いことの確認であり、Wiktionary本体に `pump one's fist` のページが存在するかは**未確認**。本委任ではネットワーク不使用) |
| 活用形(pumps) | 副次的。単独では阻害要因でない | `lemma_candidates_for_phrase`(`er023:123-173`)が先頭語のみlemma化した `pump its fist` を生成する |
| 所有格(its vs one's) | **`pump one's fist` が収録されていても阻害(第2の壁)** | 注入実験: `pump one's fist` を仮想追加してもStd/Advともヒットせず。`pump its fist` を注入した場合のみヒット。`mark the date` 注入はヒット |
| 不規則活用 | 関係なし | irregular rescueは先頭語のみ(`er027:201-243`) |
| shortlist上限 | 本件ターゲットには無関係(候補化前に消滅)。ただし**潜在リスク**: phrase_survivorsは `db_match_count` 降順だがWiktionary由来は全て1で同点のため、canonical_formのアルファベット順(core:385)になり、cap=15超過時はアルファベット後方のIdiomが切り捨て(Advは phrase 16件中 `waiting for` が落ちた)。Idiom候補を増やすと後方アルファベットのIdiomが体系的に不利 | `trace_targets_local_01.json` phrase_survivors_all(Adv16件) |
| LLM選定 | 候補外は選べない(契約) | `SELECTION_GUIDANCE` 「候補に無い新しい表現を作らないでください」(selector_01) |

## 4. LLM選定側の現状(Idiom/非透明比喩の優先度)

- Prompt(`er003_v1_translator_briefs/b1_p2_keywords_l_prompt_template.txt` L11, L13): 優先順位「初回音声での処理困難→未知の可能性→瞬時の推測困難→…」、L13「比喩・感情表現を同格の候補として扱う。透明表現は優先度を下げる」は**既に存在**。DB Hybrid追加ガイダンス(`er030_key_phrase_db_hybrid_source_reference_contract_01.py:177-196`)は「phrase/idiom/phrasal verb区分を優先」と区分名による優先のみで、「非透明性」「既知可能性」「Level差」の指示は無い。
- 実績の症状: v4 Std は phrase候補8件のうち `right away`/`take time`/`on a regular basis`/`prices up` を全採用(高頻度・透明に近い)。idiom区分=非透明ではない(`of a`/`At that`/`Hold on`/`By the way`/`Got it` もidiomとして候補に入る、INV-01 U5)。
- 推測(未検証): 比喩が候補に載れば現行L13だけでも一定確率でLLMが選ぶ可能性はあるが、4枠の競合(高頻度句+Topic)に勝てる保証はなく、Phase Cで反復測定が必要。

## 5. 現行DBでIdiomを抽出できるか(Q1)

自作10文(API不使用。`proto_placeholder_match_01.json` probe_sentences)での現行パイプライン(n>=2のDB一致)の結果:

| 文 | 現行 | 理由 |
|---|---|---|
| spill the beans | ○ | 固定形 |
| call it a day | ○ | 固定形 |
| an arm and a leg | ○ | 固定形 |
| keeps an eye on | ○(`keep an eye on` へlemma化) | 先頭語lemma |
| went the extra mile | ○(`go the extra mile`、irregular rescue) | 先頭語のみ |
| bit her tongue | **×** | 見出し `bite one's tongue`(placeholder) |
| pulling my leg | **×** | 見出し `pull someone's leg` |
| lost her temper | **×** | 見出し `lose one's temper` |
| pumped his fist | **×** | DB未収録 |
| Mark the date on your calendar | **×** | DB未収録 |

できる範囲: DB収録の固定形Idiom + 先頭語/末尾語/全語の活用形。できない範囲: (i)代名詞/所有格slot見出し(約1,600見出し)に対する本文の `his/her/its/my...`、(ii)DB未収録の比喩・新奇表現、(iii)語中間の活用、(iv)6語以上(`max_n=5`)、(v)中断された句(discontinuous phrasal verb、`er023:123` docstringで未実装と明記)。

## 6. 案(a)の試作と副作用の実測(Q5)

試作 `proto_placeholder_match_02_strict.py`(診断用、Production外): Wiktionary titleの `one's/someone's/somebody's` を所有代名詞(my/your/his/her/its/their/our)、`someone/somebody/oneself` を目的語/再帰代名詞、他語はlemma(規則+irregular)で照合。strict版(`one`と`something`と `'s`所有を除外)で:
- 自作10文: `bit her tongue`/`pulling my leg`/`lost her temper` の**3/3を回復**。現行で既に取れていた文は影響なし。
- v4 Std/Adv: 新規ヒット0(2ターゲットは回復しない=DB未収録のため)。
- 副作用走査: `er0*_output/**/article.md` から重複除去・150語以上の400本。新規候補 25件/400本(0.06件/記事、最大2件/記事、376本は変化なし)。例: `on its head`/`on their feet`/`open your eyes`/`made its mark`/`changes my mind`。ゆるい版(35件、`it up<=one up` 等のノイズあり)から `one`/`something`/`'s` を除外して改善。strict版にも `know it <= know someone` のようなノイズが残る(目的語slotの追加制限が必要)。
- 結論: (a)は低リスクで有効(約1,600見出しの活用)だが、**今回のCoffee 2表現には効かない**。

## 7. 改善設計案の比較(Phase B/C向け)

共通方針: 既存Productionファイル(er030_*/er023_*/er027_*/er003_*/Strategy L prompt)は**編集しない**。Trial専用の新規ファイル `er064_*` と `er064_output/kp_idiom_trial_01/` 配下のPromptコピーで実験し、flagはTrial runnerのみに置く(Productionの `kp_backend` 分岐に触れない)。Coffee固有の文字列hardcodeなし(2表現は評価fixtureとしてのみ使用)。

| 案 | 内容 | 変更対象(新規trialファイル) | Coffee 2表現の回復見込み | 他記事への副作用 | 追加LLM費用 | 工数 |
|---|---|---|---|---|---|---|
| **(a)** placeholder/lemma複数語辞書照合 | Wiktionary見出しの `one's/someone's/oneself` を `its/his/her/my...` に展開、動詞lemma化。stage1の後段で追加ヒットとしてmerge(既存ヒットを置換しない) | `er064_kp_idiom_matcher_trial_01.py`(`proto_placeholder_match_02_strict.py` を整備) | **0/2**(DB未収録。`pump one's fist` が収録されていれば `pumps its fist` は回復可) | 小(0.06件/記事、400本走査)。ノイズ: 目的語slot、`'s` | 0 | S |
| **(b1)** LLMによる非透明複数語表現の補助抽出 | 本文(level本文)を1回LLMへ渡し、「構成語から意味を推測しにくい複数語表現(比喩・擬人化・Idiom)」を最大N件、exact substring(5語以下)+見出し形案つきで出力。Pythonが本文実在をverify(Source Consistency相当)し、候補ID付与してshortlistへ併置(evidence=`llm_noncompositional`、DB由来と別枠) | `er064_kp_idiom_llm_extractor_trial_01.py`+schema+Promptコピー | **高いと推測(未検証)**。DB外でも拾える。Phase Cで測定 | 中: 偽陽性・過剰抽出。verify+件数上限+Level別基準で抑制。**DB Hybridの設計原則「本文全文をLLMへ送らない」(`CURRENT_SPEC.md:1847`)に抵触**(Trial限定。Production採用時は別途ユーザー判断が必要) | 1 call/記事-levelあたり約JPY0.2-0.4(推定。選定callの実測0.35-0.48円/回[INV-01 §5-A]を基準にした見積りで未測定) | M |
| **(b2)** ルールベース(`X + 所有代名詞 + Y` 等の構文パターンで3語候補を注入) | v4でのパターン出現数: Std 3件(`pumps its fist`/`imagine your usual`/`have its own`)、Adv 2件。`mark the date on your calendar` は取れない | `er064_kp_idiom_pattern_trial_01.py` | 1/2(pumps its fistのみ。偶然性高い) | 中-大: 品詞なしでは `have its own` 等のノイズ。POS tagger導入は新規依存 | 0 | M |
| **(c)** shortlist優先枠/上限 | phrase_cap tie-breakをアルファベット順から「非透明性シグナル順」(llm_noncompositional > placeholder展開idiom > Wiktionary idiom > phrasal_verb > phrase)へ。LLM抽出/placeholderヒットの**予約枠**(最大5件程度)をphrase_capの外に設ける。capは15のまま、または+5。1候補行は約40token、+10件でも選定call費用 +約JPY0.04(推定) | `er064_kp_idiom_shortlist_trial_01.py`(`build_shortlist` のTrialコピー) | (a)(b)が候補を作った後の「残存」を担保(単体では0/2) | 小。phrase数が少ない記事では挙動不変 | +約0.03-0.05/call | S |
| **(d)** 選定Prompt改訂 | Trialコピーのguidanceへ: ①非字義的/擬人化/イディオム的に使われた複数語を、同等の透明な高頻度句(`right away`/`take time`)より優先、②「Idiomなら無条件採用」にしない(条件=本文中で非字義的・構成語から意味推測困難・初回リスニング理解阻害)、③Std(A2)は高頻度句を既知とみなして優先度を下げ、Adv(B1)はコロケーション/phrasal verbも評価、④重要語4+Topic1・本文出現・意味重複回避・candidate ID契約・Rule7正規化は維持 | `er064_output/kp_idiom_trial_01/prompts/` にtemplateとguidanceのコピー(元ファイル不変) | 単体では0/2(候補外は選べない)。(a)(b)(c)と組合せて効く | 中: Prompt変更は全記事の選定挙動に影響。Phase Dの「Idiomなし記事」「透明複数語」で劣化確認が必須 | +0〜+0.02/call | S |

比較する組合せ(Phase C): V0=現行(記録済み、再実行不要) / V1=a+c+d(LLM追加なし) / V2=a+b1+c+d / V3=b2+c+d(代替) / VL=Strategy L全文方式(既存fallback。本文全文を送る既存経路)で `pumps its fist` を選ぶか=比較対照(約JPY1以内)。

### Production影響・注意点
- 現行Productionの `SELECTION_GUIDANCE` と `_FAMILY_X_SOURCE_REFERENCE_SELECTION_GUIDANCE` はTrialから参照のみ。Trial runnerが自前のguidance文字列を組み、`er030_key_phrase_db_hybrid_selector_01.build_lightweight_user_message` 相当をTrialコピー側で呼ぶ想定(Phase Bで関数差し替えの可否を精査。monkeypatchは避けコピー関数で実装)。
- 正規化経路は既存: LLMが `pump its fist` 等を出せば、`er003_key_words_canonicalization.py:304-322` の `_PERSON_DEPENDENT_TO_GENERIC`(its→one's、your/his/her/their→one's/someone's)で `pump one's fist` へ置換できる設計。動詞の基本形化(pumps→pump)はPrompt L7とnormalizationが担う(推測。Phase Cでcanonicalization完了まで実測して確認する)。
- 候補IDの契約: 補助抽出候補はsource_span=本文の実在substringである限り、`_verify_source_spans_against_raw_article`(selector_01:364)とSource整合Gateを通過できる(設計上の見込み。実測はPhase B/C)。

## 8. 確実性の見込み(Q4)と他記事への悪影響を避ける方法(Q5)

- (a)+(c)+(d)のDB側のみ: Coffee 2表現の回復は**0/2**(確定的: 候補が作られない)。ただし約1,600見出しのIdiom回復には有効。
- (b1)併用: 回復可否は**未測定**。推測として「LLMが擬人化比喩を拾う可能性は高い」程度。確実性はPhase Cで n=3反復×2Level で測る(受入基準案: 両Levelで `pumps its fist` が候補に残る率 3/3、MUST。`mark the date...` はWANTで2/3以上)。最終選定での採用(MUST)は別問題であり、(c)予約枠+(d)で押し上げた上で測定する。
- 副作用抑制:
  1. 既存ヒットを置換しない「追加のみ」merge(V0の候補集合 ⊆ V1/V2の候補集合を単体testで固定)。
  2. LLM抽出はverify失敗(本文不在)を機械除外、件数上限(例5)、DB既存候補との重複除去。
  3. Phase DでIdiomなし記事・透明複数語記事に対し、V0とV2の最終5件を比較し「Idiomなし記事で非Idiom選定が不当に押し出されない」ことを確認(受入: 悪化0)。
  4. flagはTrial runnerのみ。Productionに入れない。
- 他の既知課題(INV-01 U5: 複数語機能語句 `Hold on`/`of a`/`At that` の混入)は本Trialの範囲外。(c)の優先順位で相対的に押し下げられる副次効果は期待できる。別建て判断を提案(要ユーザー判断)。

## 9. Phase D 汎化検証設計(サンプル記事はAPI不使用で自作)

自作テキスト6本(各300-350語、A2/B1想定。3本はStd/Adv両Level):

| # | 種別 | 検証対象 | 例(下書き。実装時に確定) |
|---|---|---|---|
| D1 | 典型Idiom | DB収録固定形の維持 | spill the beans / break the ice / call it a day |
| D2 | 活用・所有格・代名詞変化Idiom | (a)の回復 | bit her tongue / lost their temper / pulling my leg / keep an eye on his sister |
| D3 | 辞書に載りにくい比喩 | (b)の回復 | 擬人化・自作の比喩(Coffee表現のコピーは使わない。別の主語・動詞で自作) |
| D4 | phrasal verb中心 | 既存挙動の維持 | figure out / run into / turn down |
| D5 | 透明な複数語表現のみ(ネガティブ対照) | 偽陽性監視 | traffic jam / after school / make a decision |
| D6 | Idiomなし(技術/統計中心) | 悪化なし | 既存Production出力と比較 |

各記事でV0(現行)/最良案の最終5件、候補数、shortlist件数、非Idiom枠の押し出し有無、費用を記録。判定は「Idiom候補の回復率」「Idiomなし記事の悪化0」「費用」。

## 10. Phase B/C/D 費用見積(JPY、上限50)

実測単価: DB Hybrid選定1回 = JPY 0.3462 / 0.4371 / 0.3922 / 0.4805(Coffee 4系統。tokens in 3.6k-4.6k、out 3.6k-4.8k、モデル gpt-6-luna。INV-01 §5-A)。補助抽出callは**未測定の推定** JPY0.2-0.4/call。canonicalization/Redundancy QAの単価は保存ファイルに記録が無く未測定(推定: 各JPY0.3-0.5程度)。

| Phase | 内容 | 費用見込み |
|---|---|---|
| B | Trial実装+単体test(fixtureはAPIなし) | JPY0 |
| C | Coffee v4 Std/Adv。V1/V2を各n=3反復=選定12回(約0.45)≈5.4、抽出6回(約0.3)≈1.8、VL対照2回≈1、canonicalization/QA到達確認数回≈2 | 約JPY10(上限12) |
| D | 6本×1Level(+3本は2Level)=9記事。V0とV_best各2反復: 選定36回≈16、抽出18回≈5 | 約JPY21(上限25) |
| 予備 | 失敗再試行・追加検証 | 約JPY8 |
| **計** | | **約JPY39(上限50内、予備込みで約JPY11の余裕)** |

注: 各Phase前にFableが費用ガードを設定する。モデル: 現行選定モデルは gpt-6-luna(INV-01実測)。開発・評価用途は最新世代モデルを使う原則(PM_GOVERNANCE 25節)に従い、Phase C開始前に「gpt-6-lunaが最新か」を確認し、最新でなければ理由を記載する。

## 11. 推奨案(Fableへ提示)

- **主案(推奨)**: V2 = (a)placeholder照合 + (b1)LLM補助抽出(Pythonでverify) + (c)予約枠/優先順位 + (d)Prompt改訂。ablationのためV1(a+c+d)と対照VL(既存Strategy L全文方式)も同時比較。理由: Coffee 2表現が「DB外」であることは実証済みで、(b)なしでは回復不能。(a)(c)(d)は低リスクで一般性が高い。
- **代替案**: V3 = (b2)ルールベース+(c)+(d)(LLM追加なし)。費用0だが精度が低く(pumps its fistのみ回復、mark the dateは不可)ノイズ大。「本文全文をLLMへ送らない」原則を優先する場合の代替。
- **オプション**: 補助抽出を「Idiom候補が不足する時(例: Wiktionary由来phrase候補<N)のみ発動」する条件付き運用でコストと影響範囲を抑える(Phase Dで検討)。

## 12. 未解決論点(ユーザー判断要)

1. (b1)はDB Hybridの設計原則「本文全文をLLMへ送らない」(`CURRENT_SPEC.md:1847`)と衝突する。Trial限定は可だが、Production採用時の扱い(要ユーザー判断)。
2. Wiktionary本体に `pump one's fist` / `mark the date` のページが存在するか(ローカルdumpには無い)。Phase Bでネットワーク確認するか(費用0だが外部アクセス)。
3. 受入基準の数値(反復回数、MUST=3/3等)の確定。
4. 複数語機能語句(`Hold on`/`of a`/`At that`)のノイズ対応(INV-01 U5)を本件に含めるか。
5. `max_n=5`(`er023:85`)とdisplay_phrase 5語上限により、6語以上のIdiom/proverbは現行対象外。本件で扱いを変えるか。
6. v4のKP資産(run_e_tone_01)はmain未merge(INV-01 U2)。Phase Cの正本入力は main管理の `parts.json` snapshot(sha一致)を使う。
7. 補助抽出の費用・canonicalization/QA単価は推定のみ。Phase Cの最初の1回で実測し、上限判断を更新する。

## 13. 付録: ローカル実行ファイル(すべて `er064_output/kp_idiom_trial_01/phase_a/`)

| ファイル | 内容 |
|---|---|
| `trace_targets_local_01.{py,json}` | ターゲット部分n-gramのDB照合結果、phrase/word survivors、希少度順位 |
| `trace_wiktionary_lookup_budget_01.{py,json}` | Wiktionary multiword lookup(60件)の対象範囲(ネットワーク不使用で再現) |
| `sim_inject_db_entries_01.{py,json}` | 仮想DB見出し注入(メモリ上のみ)での現行照合のヒット可否 |
| `proto_placeholder_match_01.{py,json}` / `_loose.json` / `proto_placeholder_match_02_strict.{py,json}` | placeholder照合試作と副作用走査(400本) |
| `inputs/` | v4原稿複製 |
