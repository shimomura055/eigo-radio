# ROOT_CAUSE_03: 2課題(①Std日本語意味の字義訳 / ②見出し語の人称placeholder)の根本原因確定(委任_13、2026-10-23、API 0)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_13 / 根拠ユーザー指示=`docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_06.md`(目標=2課題を実際に解消)
範囲: 既存データの決定論抽出+目視分類のみ。API 0・Production変更0・既存コード変更0。分析script=`er112_output/kp_gm_design_05/`(`t1_extract_possessive.py`、`t1_referent_table.py`、`t1_summary.py`、`t1_arm_breakdown.py`、`t1_arm_rate.py`、`t2_list.py`、`t2_pool_census.py`、`t3_possessive_sim.py`)。
前提の訂正(FABLE_VERIFICATION_02): `reach for someone's wallet→人の財布`・`apply one's findings→人の研究結果`は**見出し語に忠実な訳**でStd生成の誤りではない。Std確定NGは 第3回 G0=2(an unseen clock×2)・G2=1(draw a line「はっきりと線を引く」)・G3=0 に加え、第2回 G0の draw a line「線を引く」×2。

## 0. 結論(先頭)

| 課題 | 根本原因 | 確度 | 一言の証拠 |
|---|---|---|---|
| ② 見出し語の人称placeholder | **正規化段(canonicalization)に「所有格が誰を指すか(主語自身/別の人/人でないもの)」を判定する工程も規定もなく、one's/someone's/無変更の選択が確率的に決まる**。さらに決定論validatorの許可表は「語→許可集合」だけで指示対象を見ない(`its`→`one's`のみ、`your`→{one's,someone's,somebody's}全て合法)。日本語意味側は`one's`=自分/`someone's`=不定の人と区別する(`er003_key_words_gloss_alignment.py:205-228`)ため、見出し語の取り違えがそのままStd/Advへ「忠実に」伝わる | 高(規定の欠落はfile:lineで確認、現象は実データで再現) | 同一display_phrase `reach for your wallet` から、runにより one's / someone's / 無変更 の3種が出ている(§A-2)。全29件中4件(13.8%)が本文の指示対象と不一致(§A-1) |
| ① Stdの字義訳 | **「字義読みも文法的に成立する比喩・慣用表現」で、モデルが語彙既定(語ごとの対応訳)を確率的に選ぶ。これを検出・是正する工程が全段に存在しない(意味の正否・字義/慣用の検査ゼロ)**。Promptや構造を変えても(G1/G2/G3)全体の発生率(1〜3%)が有意に下がらないのは、原因が「Promptの言い回し」ではなく「出力後に誰も見ていない」ことと、「発生しやすいKP群が稀で評価の検出力が不足」の2点だから | 中〜高(検査の不在は`ROOT_CAUSE_02.md` §2・本書§B-4で再確認。「発生しやすいKP群で確率が高い」は事後層別で示唆に留まる=§B-3) | 字義NGの5出力(2KP)は全て初回採用(retry 0)、qa自己申告PASS。該当KPでの再現確率は draw a line 2/5(G0)、unseen clock 2/2(G0)と高く、集団では2〜3%/KPに希釈される |

## A. 課題②: 見出し語の人称placeholder

### A-1 影響範囲の定量(既存データ全件、決定論抽出+目視ラベル)
抽出: リポジトリ内の全`keywords_canonicalized.json`(729ファイル)から、`display_phrase`に所有格/人称代名詞(my/your/his/her/its/their/our/you/they/he/she/再帰)を含む項目を(source_sentence, display, key_phrase)で重複排除 → **45件**(`er112_output/kp_gm_design_05/t1_possessive_items.json`)。うち人称placeholder(one's/someone's/oneself/someone)へ一般化されたもの **29件**、一般化されず原形のまま16件。各件の本文の指示対象を目視で3分類(`t1_referent_table.py` の REF に根拠を1行ずつ保存): self=動詞の動作主自身の所有、other=動作主とは別の人、nonperson=人でない所有者(研究・組織等)。慣習上の正しい一般形は self→one's / other→someone's / nonperson→人称placeholderにしない。

| 指示対象 | 見出し語の実際 | 件数(重複排除) | 判定 |
|---|---|---|---|
| self | one's | 19 | 一致 |
| self | **someone's** | **3**(`reach for someone's wallet`、`go out of someone's way`、`lose someone's job`) | **不一致(自分の→別の人)** |
| other | someone's | 6 | 一致 |
| nonperson | **one's** | **1**(`apply one's findings`、its=研究) | **不一致(人でない所有者を人称化)** |
| **計** | | **29** | **不一致4件=13.8%** |

- 出所別: Production artifact(er019/er026等)は24件中不一致1(`apply its findings→apply one's findings`)=4.2%。DEV Trial_01(er112、A-1・variant arm)は5件中不一致3(小n)。artifactの複製(同一内容が複数runに残る)を数えると 194件中7件(3.6%)。
- Trial_01 arm別のrep単位(`t1_arm_rate.py`、self指示対象のKP出力): one's 45・**someone's 6**・原形のまま8。一般化されたself出力51件中 **someone'sが6件(11.8%)**。other指示対象は someone's 20/20(不一致0)。
- `its→one's`は全4件(distinct)中、self(擬人化された`your wallet`が主語)3件は妥当、nonperson(研究)1件が誤り。nonpersonの`its`/`their`が一般化されなかった例も5件(`use its results`、`turn on its head`、`find its way back`、`compete through its presence`、`enforce their rules`)=同じ記事で`use its results`は無変更、`apply its findings`は`one's`化、とProduction内でも一貫していない。
- 結論: 誤りの型は2つ。(型1)self→someone's(Trial_01のA-1・variant armで観測、Production a2では未観測)、(型2)nonperson→one's(its→one'sが許可表の唯一の写像のため、LLMが一般化すると必ずone'sになる)。n小(29件)につき率は目安。

### A-2 原因の確定(規定の欠落)
1. **選定規則3に基準なし**(`er003_v1_translator_briefs/b1_p2_keywords_canonicalization_fulltext_prompt_template.txt:11`): one's/someone'sの選択基準、本文の指示対象を見る規定は無い。「迷う場合はreasoningで説明し、より自然だと判断する側を選ぶ」のみ(HEADWORD_PLACEHOLDER_01 §2-a)。
2. **決定論validatorは指示対象を見ない**(`er003_key_words_canonicalization.py:431-473`): `_PERSON_DEPENDENT_TO_GENERIC`は語→許可集合。`your`→{one's,someone's,somebody's}、`its`→{one's}。`_is_valid_person_generalization`は語数同一・1対1置換が許可集合内ならTrue。→ `your wallet→one's wallet`も`→someone's wallet`も機械的に両方合法、`its(研究)→one's`も合法。
3. **canonicalization出力schemaに指示対象の欄が無い**(`:117-137` `_ITEM_SCHEMA_PROPERTIES`: rank/key_phrase/changed_from_display_phrase/normalization_reason/reasoning/QA11本)。`qa_person_reference_generalized`(`:96`)は「規則3に従って置換されているか」の自己申告で、指示対象の正否は問わない。
4. **下流は見出し語を正本として忠実に従う**: gloss段は`one's`=自分/`someone's`=不定の人を要求(`er003_key_words_gloss_alignment.py:205-228`、`PERSON_CONSTRAINT_TEXT`)、かつ「source_sentenceは人称の指示対象を決めるために使わない」(同`PERSON_CONSTRAINT_TEXT`)。Adv説明もglossと見出し語に従う(第2回59/60の唯一のNG=見出し語`someone's`への忠実な出力、FABLE_VERIFICATION_02)。→ 上流の誤りが検査されないまま全工程に固定される。
5. **同一入力で出力が揺れる実証**(`t1_arm_breakdown.py`): `reach for your wallet`(同一文)→ `reach for one's wallet`(多数)/`reach for someone's wallet`(a12 rep1・a1_c rep1・a1g rep1)/`reach for your wallet`無変更(a12 rep3・a1_c rep3・base_c rep3)。ルール欠落による確率的選択であり、特定のPrompt版(base_c/a12/a1_c/a1gの複数arm)の問題ではない。
6. A-1(規則5)との関係(`er112_kp_gm_trial_01.py:94-108`): 規則5は`this/that→a/an`と目的格`him/her/me/us→someone`のみ。所有格は「規則3の扱い」と明記(`:102`)で対象外。A-1は本課題の原因でも解でもない(併存・衝突なし)。

→ **原因は規定の欠落(指示対象の判定工程がどの段にも無く、許可表と選択が分離している)**。Promptの言い回しの問題ではなく、出力schemaと決定論validatorの構造の問題。

## B. 課題①: Std日本語意味の字義訳

### B-1 字義訳NGの全事例(確定データのみ)
対象: Fable最終判定(第3回、FABLE_BLIND_RESULT_03/VERIFICATION_01/02)とOpus確定gold(第2回、GOLD_LABELS_FINAL_01)。`reach`/`apply`は見出し語に忠実なため含めない。生データ行は`t2_list.py`で再確認(行番号=results.jsonlの物理行)。

| # | KP | 出力 | 場所 | 型 | 比喩の手がかり | retry | 同KP同armの他rep | 同KPのAdv(E0@G0) |
|---|---|---|---|---|---|---|---|---|
| 1 | draw a line | 線を引く | T2 G0 rep1(行7) | 動詞句(V+a+具体名詞)・辞書の慣用 | 主語が抽象物(`The words draw that line simply`)。字義も文法上は成立 | なし(初回採用) | rep2「一線を引く」(慣用義・許容) | 行127 "to show where one thing ends and another begins"=比喩 |
| 2 | draw a line | 線を引く | T2 G0 rep3(行80) | 同上 | 同上 | なし | 同上 | 行113 "to decide where a limit or boundary should be"=比喩 |
| 3 | draw a line | はっきりと線を引く | T3 G2 rep2(行212) | 同上 | 同上 | なし | 他4出力は慣用義 | 第3回に難例のAdvなし(**Adv無し**) |
| 4 | an unseen clock | 目に見えない時計 | T3 G0 rep1(行60) | 名詞句・**著者が作った比喩**(辞書に無い) | `A coffee price tag may have an unseen clock of its own`: 値札が主語、`of its own`が手がかり | なし | rep2も同一文字列 | 行412 "a hidden sense of time that affects when something happens or changes"=比喩寄り |
| 5 | an unseen clock | 目に見えない時計 | T3 G0 rep2(行177) | 同上 | 同上 | なし | 同上 | **Adv無し**(E0はrep1のみ生成) |

- 独立KPは2つ(draw a line、an unseen clock)。出力では5件。
- 参考(gold確定外、`ROOT_CAUSE_02.md` §3-3表L): carry the load「荷物を運ぶ」・take the wheel「ハンドルを握る→車を運転する」・pull someone under等は正解ラベルが曖昧で、事例数に含めない。
- **共通条件**: (1)具体名詞(line/clock)を含み、字義読みも文法的に成立する。(2)比喩の手がかりは文脈(抽象的な主語や`of its own`)に間接的にしかない。(3)モデルは語ごとの対応訳(語彙既定)を確率的に選ぶ。(4)全て初回採用で、qa自己申告はPASS、検査・retryは働いていない(`ROOT_CAUSE_02.md` §2: 16 unit/48 itemで初回合格16/16)。(5)承認済みgloss規則の「直訳調を避ける」(`b1_p2_keywords_l_prompt_template.txt:19`)は存在するが抑止力が不十分。

### B-2 Prompt変更で下がらない事実の整理
- 現行(G0)の字義NG(Std独立KP=難例20+第2回通常6+第3回新規通常40=66KP): 2KP/66 = **3.0%**(Wilson 95% CI 0.8〜10.4%。難例を意図的に多く含むため集団の率はこれより低い)。通常KPのみでは 1KP/46 = 2.2%(CI 0.4〜11%)。10KP/記事なら記事あたり約2割(推定。幅広い)に相当。
- G1(「全語反映」句の除去)は改善せず、G2(用法先決め)は`draw a line`を直すが`take the wheel`等を壊し差し引き0(`ROOT_CAUSE_02.md` §3-3)。G3は字義NGが0だが、薄い(△)出力が増える(第3回 G3=4/G0=1)。

### B-3 事後層別(示唆のみ、選択バイアスあり)
字義NGが出た2KPの出力(draw a line 5、an unseen clock 2=計7出力/方式)での方式別: G0=4/7、G2=1/7、G3=0/7(Fisher G0対G3 片側p≈0.035、両側約0.07)。
- 解釈: KP単位で「発生しやすいKP」が存在し、そのKPではG0の再現確率が40〜100%と高い一方、全体の分母(Std 66KP)に希釈されて2〜3%に見える。**「Prompt変更の効果が全体比で有意でない」のは、検出力不足(発生しやすい層の分母が小さい)の可能性が高い**。
- 限界: 層は結果(NGが出たKP)から事後に決めたため、方式差は過大に出る。次Trialでは**結果に依らない層**(比喩・慣用で字義読みが文法的に成立するKP群)を事前に定義して測る(DESIGN_05 §5)。

### B-4 「検査が無い」ことの確認
- `er003_key_words_gloss_alignment.py:612-665`(`validate_item_corrected`)の合否は qa自己申告・括弧禁止・数字・人称整合のみ。意味の正否・字義/慣用の検査なし。mappingはrecord-only(`ROOT_CAUSE_02.md` §2)。
- Adv段(`er019_family_x_kp_explanation_01.py:199-213`)の検査は語数・新規Factのみ。Std/Adv整合の検査なし。
- X/Z共通: 両runnerが同一の`generate_kp_explanations`と同一のgloss生成経路を使う(X `er019_family_x_audio_production_runner_01.py:1073-1095`、Z `er026_family_z_fiction_production_runner_01.py:1517-1543`)。

### B-5 仮置き仮説「Std字義×Adv比喩の不一致で機械的に検出できるか」の既存データ検証(結論: 検出器としては不適)
- 検出可能性(カバレッジ): 字義NG 5出力のうちAdvが存在するのは3出力(行7→127、行80→113、行60→412)で、**3/3がAdv比喩(=Stdと不一致)**。残り2出力(行212、行177)はE0未生成。ただしこれは「Stdを字義/比喩に分類できる分類器が別にある」場合の上限で、不一致を判定するにはStdの字義/比喩を読み取る意味判断(LLM)が結局必要。
- **構造的な欠陥(データに依らない)**: (i)Advは**b1b(Advanced)のKPにしか存在しない**(X `:1073`、Z `:1517`)。a2(Std)レベルのKPにはAdvが無く、検出が成立しない(X/Z共通の対策にならない)。(ii)Advに`usage_type`を出させるにはAdv schema/出力項目の追加が必要で、承認済みB仕様(PROMPT_SHA256 `c3d3734b…`、`er019_family_x_kp_explanation_01.py:142`、15語/新規Fact不可/逐語転記)の変更に当たる(ユーザー判断)。(iii)`ROOT_CAUSE_02.md` E3: 判断結果をStd/Adv間で共有すると、判断が外れたKPで悪化した(独立な第2の目が失われる)。
- 偽陽性の目視推定(E0@G0 難例60+通常40のうち行1のみ表示した100組=`t2_list`系出力の目視): Stdが「字義にも比喩にも読める日本語」でAdvが比喩となる組は`take the wheel`(ハンドルを握る)・`on the throne`(王座に君臨する)の2組程度(約2%)。不一致検出器が誤検出しうる型だが、検出器そのものを作らないため**参考値**(実行層Sonnetの主観、独立性なし)。
- 結論: **Std/Adv用法整合チェックは採用しない**(カバレッジ欠如・B仕様変更・共有で悪化した先行データ)。必要なのは、Std単独(a2/b1b共通のgloss段)での字義検査。

## C. 本書の限界(推測で埋めない)
- ②の指示対象ラベルは実行層の目視(29件の根拠はREFに1行ずつ)。LLMが同じ指示対象を判定できるか(ラベル精度)は未測定=次Trialの測定対象。
- ①のNGは2KP・5出力のみ。発生率・手法差の推定は広い信頼区間を持つ。事後層別は選択バイアスを含む。
- Production a2/b1bの実run全体でのself→someone's率は未観測(Production artifact 24件中0)。Trial_01のA-1/variant armで観測された型が、Production配線後のA-1で増える可能性はあるが、A-1配線後のデータは無い(推測しない)。
