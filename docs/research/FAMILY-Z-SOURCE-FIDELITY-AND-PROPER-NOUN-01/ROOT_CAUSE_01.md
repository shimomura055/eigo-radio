# ROOT_CAUSE_01: 『開いた窓』原作結末(Romance at short notice was her speciality.)欠落の根本原因調査

管理ID: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_01A / 区分A(調査・設計) / 2026-10-23 / read-only・API 0・JPY 0
対象run: `er026_output/family_z_production_e2e_01/the_open_window/run_e2e_01/`(以下 `$R`)。Production/Prompt/音声/成果物は無変更。
語の対応: Standard=内部名`a2`/`std.md`、Advanced=内部名`b1b`/`r2.md`。

## 0. 結論(先頭)
- **最初に失われた工程 = Advanced R0**(`$R/writer/r0.md`、sha b6928997…、gpt-6.1-sol、attempt 1、2026-10-21T00:07:14Z)。原作取得・Seed・R0 Promptまでは「即興の作り話が得意」という意味が存在し、R0出力で初めて消えた。R1/R2/Std調整はR0を入力とする編集であり、欠落を引き継いだだけ。Std/Advが同じオチを欠いたのは、同一の上流(R0)を共有するため。独立に二度消えたのではない。
- **根本原因の判別: (b) Prompt・構成指示が省略を誘発 = 主因(確度 高、約80%)、(a) LLMの自主的選択 = 副因(約20%)、(c) 原作取得データの欠落 = 否定(確定)**。
  - 主因の中身: Seedの`conversion_plan`が**「結末」を「少女の犬の作り話」と定義し、かつ「最後の行の後に説明を足すな・驚きが要点」と指示**していた。原作の最終一文は「少女の台詞の後ろに付く語り手の種明かし」であり、この指示の文言上は「最後の行の後の説明」に見える。一方、現行の編集方針ブロック(2026-10-12置換)には「結末・種明かしを維持せよ」という条項が無く、R0 Promptは「Seedは素材であり再現すべき要約ではない」「固定の結末の形に縛られない」と述べる。この2つが重なり、LLMは語り手の最終文を落として台詞の小ネタ(`He said they took turns.`、原作に無い)で閉じた。
  - 「Validatorがないから」は主因ではない。生成工程で、指示体系が結末を犬の作り話の位置で終わらせるよう誘導していた(§2)。
- 確度の限界: LLMの内部判断は観測できない(reasoning_tokens=511は中身非公開)。反事実(旧Promptや修正Promptで同じR0を再生成すれば残るか)は未検証。実行はTrial(API費用)であり本委任の範囲外。検証案は`COMPREHENSIVE_DESIGN_01.md` §5。

## 1. 工程別追跡(原文§3の1〜7)
オチの意味 = 「Veraの語りは全部その場の作り話だった」と語り手が明かす1文(原作 `seed/primary_text_excerpt.md:59`)。

| # | 工程 | 成果物(path) | オチの意味が維持されていたか | 証拠 |
|---|---|---|---|---|
| 1 | 原作取得・保存 | `the_open_window/seed/primary_text_excerpt.md`(sha ead67681…=SEED_PROVENANCE) | **維持** | L59に `Romance at short notice was her speciality.`(末尾行)。Gutenberg #269 全文1,212語 |
| 2 | 原作→制作素材(Seed) | `seed/seed.json` | **維持(ただし間接話法)** | `seed_elements[5]`(L9)=「…backing it up with a vivid invented tale about his past; the closing line says that romance at short notice was her speciality.」。`original_summary`(L2)末尾にも同文。`discarded_elements`(L11〜)にオチは無い。歌詞・白いコートは引用で書かれるのに、オチだけ「the closing line says…」という説明文 |
| 2b | Seed `conversion_plan`(R0の[How to convert it]へ逐語投入) | `seed/seed.json` L18 | **矛盾を含む指示** | 「Preserve … the ending: … the visitor running away in panic; and **the girl's smooth lie about the dog, which reveals that she made up the whole tragedy**.」「**Do not explain the trick, hint that the girl is lying, or comment on the twist before the ending, and do not add a moral or an explanation after the last line; the surprise is the point.**」 → 結末=犬の嘘そのもの、種明かしは嘘自体が果たす、最後の行の後に説明を足すな、と読める |
| 3 | Story構成・分割 | `segment_plan_{a2,b1b}.json` | 消えた後の工程(欠落テキストを3分割しただけ) | boundaries [9,20]。Part3最終clip=`full_story_part3_c13`(Vera台詞 "He said they took turns.") |
| 4a | **Advanced R0** | `writer/r0.md`(`r0_prompt.txt`) | **初めて消失** | 末尾=`“It was the spaniel,” the girl said calmly. … She glanced at the sleepy spaniel. “He said they took turns.”`で終了。`grep -i "speciality\|romance" $R/writer/*.md` は0件(`r0_prompt.txt`は入力側として存在)。guardrails word_count=431(目標330〜470内。語数超過が理由ではない) |
| 4b | Advanced R1 | `writer/r1.md` | 欠落のまま継承 | R1 Promptの入力はR0本文のみ(Seedなし)。`r1_prompt.txt`末尾が`He said they took turns.` |
| 4c | Advanced R2 | `writer/r2.md`(Advanced最終、sha 9d1558ff…) | 欠落のまま継承 | R2 Promptの入力もR1本文のみ。「Without changing the events, the characters, or the cause-and-effect」(`er062_family_z_writer_01.py:139-142` REVISE_USER_TMPL)。R1/R2はSeedを見ないため、R0で落ちたものを復元する手段が構造上無い |
| 5 | Advanced→Standard調整 | `writer/std.md`、`std_adjust_prompt.txt` | 欠落のまま継承 | 入力=R2全文。段落30=30。Std末尾=`“He told me they took turns.”`。さらにStdは歌詞を `why do you bound`→`why are you jumping`(p12,p24で整合)に変更(結末とは別の副次ドリフト) |
| 6 | 最終本文・音声原稿 | `segment_plan_*.json`(clips)、`a2|b1b/assembly/*.wav` | 欠落のまま | `$R`配下のtxt/md/json/jsonlを`grep -i "romance at short\|speciality"` → ヒットは`writer/r0_prompt.txt`(Seed由来の入力)のみ |
| 7 | 既存Validator・QA・Gate | §4 | 検出手段なし | §4 |

### 補足(R0が自分で足したもの)
R0は原作に無い `He said they took turns.`(原作は"snarling and grinning and foaming just above him")と`sleepy spaniel`の描写を追加した(`E2E_PLAN_01.md` §10-A所見(c)でも既出)。LLMは「最後は台詞のドライユーモアで閉じる」という別の結末形を選んだ。これは(a)自主的選択の証拠だが、Promptが「結末の形に縛られない」「ドライユーモアを保て」と許し、語り手の最終文を「最後の行の後の説明」として禁じた結果の合理的な着地であり、無根拠な省略ではない。

## 2. 原因の切り分け((a)(b)(c))
### (c) 原作取得データの欠落 = 否定
`seed/primary_text_excerpt.md:59`にオチあり。Seedの`seed_elements[5]`・`original_summary`にも言及あり。取得・保存・Seed化の段階では欠落していない。

### (b) Prompt・構成指示が誘発 = 主因
R0 Prompt(`r0_prompt.txt`、sha 141b7c4d…)の該当箇所とそのソース:
1. **Seed `conversion_plan`(`seed.json:18`)**: 上表2b。結末を「犬の嘘」と定義し、「最後の行の後に説明を足すな」「驚きが要点」。原作のオチはまさに「最後の行の後の語り手の1文」で、指示の文言と原作構造が衝突している。起源はユーザー2026-10-21指示(`docs/pm/delegation_log/2026-10-21_FAMILY-Z-THE-OPEN-WINDOW-PRODUCTION-E2E-01_USER.md:33`「結末の意外性を損なう先回りの説明や、過剰な解説を入れないこと」)で、Seed作成担当が`conversion_plan`へ翻訳する際に、語り手の最終文を「過剰な解説」側に置いた解釈(翻訳方針は`E2E_PLAN_01.md:41`に記載)。ユーザー指示自体は「結末を維持」(同:35)も求めていた。
2. **編集方針ブロック**(`er062_family_z_writer_01.py:106-109` `R0_BLOCK_PRESERVATION`): 「Keep the essence…」「The story may develop differently from the original」。2026-10-12以前の旧ブロックにあった「Seed要素を全て維持」「結末の帰結を維持」が無い(§3)。
3. **R0 Promptのフレーミング**: 「[Story Seed -- … freely reimagined; this is NOT a summary to reproduce, just raw material]」(`R0_TEMPLATE` L117〜)、`WRITER_DEVELOPER_MESSAGE`(L75〜)の「or a fixed ending shape」、「Do not just retell the original … a faithful, simplified retelling … is welcome」(L91)。いずれも結末形の自由を許す。
4. **語数**: 目標400語・330〜470(`R0_BLOCK_LENGTH_ADV` L100)。原作1,212語→431語(約36%)。R0は範囲内で、オチ1文は約7語。語数制約が直接の原因とは言えない(圧縮圧は背景要因)。
5. **Seed `discarded_elements`**: 人名を「省略可」と明示(`seed.json:15`)。区分B(固有名詞)の論点。オチの主語(`her`=Vera)が名前を持たないため、「少女の台詞で閉じる」ほうが自然と判断された可能性(推測)。

### (a) LLMの自主的省略 = 副因
上記指示の枠内で、語り手の最終文を落とし台詞の小ネタを足したのはLLMの選択。ただし指示がその選択を誘導していたため「LLM単独の気まぐれ」ではない。別のR0再生成で残る可能性はあるが、検証は未実施。

## 3. 承認履歴の整理(2026-10-12の方針変更・Validator撤去)
### 3-1 ユーザー原文(逐語)
出典: 前セッション`C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\f2c17cf7-6207-4666-abec-016808eac6d3.jsonl` の2026-10-12T05:39:31Zユーザー発話。SSOT要旨=`CURRENT_SPEC.md:1620-1621`(③④)、`DECISION_LOG.md`「委任_10結果・旧仕様支出事故・ユーザー仕様修正①〜④」。
> **③ 原作保持Validator**
> - Family Zの原作保持LLM Validatorは不要。新設・calibrationを中止する。
> - 固有名詞必須の既存チェックも撤廃する。
> - 人物関係、出来事、因果関係、結末などの原作との厳密な一致を、新しいChecker／Validatorで強制しない。
> - 既に着手したer061等の実装があれば、不要な処理をProduction経路へ組み込まない。
> - 関連API呼び出し・retry・検査費用を発生させない。
>
> **④ Family Zの編集方針**
> - 原作のエッセンスを活かし、面白さ・自然なStorytellingを優先する。
> - 原作と異なる展開・表現も、作品として成立し面白ければ許容する。
> - 品質上の問題をユーザーが指摘した場合、原則としてWriter側の仕様・Promptを改善する。
> - Checker／Validatorを安易に増設しない。
> - これは『走れメロス』限定ではなく、Family Z全体の方針とする。
>
> (同発話§3)中止・撤廃対象=原作との意味的一致を評価するLLM Validator／人物名必須チェック／原作との差異を理由とする自動NG・再生成／上記のcalibration。「原作保持Validatorの代わりに、別名の意味チェックや独立QA工程を新設しないこと。」(同§4)「WriterのPromptに残る過度な原作忠実性要求も今回の方針に合わせて調整する。」

### 3-2 当時の変更の範囲(事実)
| 項目 | 変更前(2026-10-12 委任_04B、commit f955847db) | 変更後(委任_11〜現行) | 根拠 |
|---|---|---|---|
| R0 Prompt保持条項 | `R0_BLOCK_PRESERVATION`=「Keep **every Story Seed element above, in the same order of events**. Keep the central story, the relationships between the characters (…), and the **ending's outcome** (what finally happens to each main character) as stated in the Seed. Do not invent a different ending. Do not add new named people, new places, or new events that change the cause-and-effect」 | 「[Editorial policy -- keep the essence, tell it as a story] Keep the essence…／Give priority to making it interesting and natural as storytelling. The story may develop differently from the original…／Keep the cast small and do not add named people other than the main character.」 | `git show f955847db:er062_family_z_writer_01.py` L97-100 vs 現行 L106-109 |
| 原作保持Validator(er061) | R0〜Std後にLLM判定(preserved/altered/missing、`ending`カテゴリ含む)、FAILで再生成/STOP | Production経路から撤去(NOT_WIRED)。コード・fixtures・calibrationは履歴保持 | `er061_family_z_semantic_validator_01.py:1-24, 49` |
| 名前検査 | 必須化→Hard FAIL | `NAME_RULE_NOTE`のWARNのみ | `er062_family_z_writer_01.py:417` |

### 3-3 今回の欠落との因果
- 旧ブロックの「Keep every Story Seed element above」は文言上`seed_elements[5]`(オチ)も含む。旧ブロック有効なら欠落確率は下がった可能性が高い(推測、未検証)。ただし旧ブロックの「ending's outcome (what finally happens to each main character)」は主要人物の帰結を指し、『開いた窓』の語り手の種明かしは帰結ではないため、旧ブロックでも守られたと断定はできない。また§2の`conversion_plan`矛盾は旧ブロック下でも残る。
- 10-12の方針変更自体は、ユーザーが「品質問題が出たらWriter Promptを改善して対応する」と定めた枠内の変更で、不具合・誤実装ではない。**ただし「結末・種明かしの維持」条項がPromptから全削除された結果、結末保持は(1)Seedデータ側(`conversion_plan`・`seed_elements`の書き方)と(2)Fable CPの人手確認だけに依存する構造になった**。これが本件の構造的背景。
- 今回ユーザー2026-10-23指示(重要な結末の改変は許容しない)と10-12④「原作と異なる展開も許容」は文言上の強さが異なる(`E2E_PLAN_01.md:49`も同旨を10-21時点で指摘)。解消には「許容する差異/許容しない差異」の境界定義(Promptへの追記)が必要で、Writer Prompt原則の変更に当たるためユーザー判断事項(`COMPREHENSIVE_DESIGN_01.md` §7)。
- 10-21の本文生成後、「原作最終文が両版に無い(Fable CP対象)」と記録された(`E2E_PLAN_01.md` §10-A所見(a)、`docs/pm/RESULT_PACKET_OW2.md:5`、OPEN-428)。Fable CPの判定内容の記録は確認できていない(**未確認**)。チェックリスト項目4(`E2E_PLAN_01.md:47`「結末の前に嘘だと分かる説明や示唆がない」)は、語り手の最終文の欠落が合格側に読める書き方だった。

## 4. 既存QAが検出できなかった理由
Family Z本文系で、本文と原作の対応を見る検査は存在しない。

| 検査 | 場所 | 対象 | オチ欠落の検出 |
|---|---|---|---|
| 語数範囲・タイトル・禁止名(WARN) | `er062_family_z_writer_01.py:405-418` | Advanced本文 | 不可 |
| Std≠Adv(同一文率≥0.5でFAIL)・段落数一致・平均文長 | 同:421-444 | StdとAdvの関係 | 不可(両者が同じ欠落を共有) |
| support lint(spoiler語・禁止名) | `er062_family_z_structure_01.py:809-812, 874-876` | Preview/Commentのみ(本文は対象外)。`romance at short notice`はspoiler語として登録され、**補助文へオチが漏れること**を防ぐ側 | 不可(逆方向) |
| 権利Gate(Z-1)・必須ファイル/構造 | er026 | 権利・構造 | 不可 |
| 音声系(ASR・audio_text_deviation・6%減速・shared_gate) | er063 | **本文↔音声**の一致 | 不可(本文自体が欠落済み、原作は参照しない) |
| Fable CP(人手確認) | `E2E_PLAN_01.md` §2-2, §10 | 5観点 | 観点4の文言上、欠落が合格側に読める。所見(a)として記録されたが検査として機能せず |
| 撤去済みer061 | `er061_family_z_semantic_validator_01.py` | 意味保持(`ending`カテゴリ L49) | **本件には元から未適用**: anchors・SEED_DIRはMelos固定(L36)、`SEED_PROVENANCE.json`も「er061 validator_anchorsは撤廃済みのため無し」。稼働していても『開いた窓』用anchors新規作成が必要。judgeは`seed_element_index 5`欠落を`missing`と判定した可能性が高い(推測) |

要約: 検査が無かったことは「検出できなかった理由」であって「欠落の原因」ではない。原因は§2(生成工程の指示体系)。検査を足すだけでは欠落の後追い検出にとどまり、再生成費・retry・Human Review増を伴うため、再発防止の第一手段にしない(`COMPREHENSIVE_DESIGN_01.md`)。

## 5. 参考(メロスとの比較、他作品への調査拡大はしない)
メロスの`seed.json`最終要素は「Melos arrives just in time; his friend is freed, and the ruler is changed…」という**出来事としての結末**で、R2末尾(王の"Lower the sword…How does a man earn such trust?")に保持されている。『開いた窓』のオチは**語り手のメタ的な1文**(出来事ではなく意味づけ)であり、Seed化・Prompt化の際に落ちやすい構造的差異がある。今後の古典でも「出来事でない結末(語り手の総括・反転の一文)」は同じ落ち方をするリスクがある。

## 6. 次の一手の候補(FableのQDC記録用)
- 原因仮説: 主因(b)Seed `conversion_plan`が結末を「犬の嘘」と定義し「最後の行の後に説明を足すな」と指示+編集方針から結末維持条項が消えている。副因(a)LLMの結末形の選択。
- 根拠観測値: `seed.json:9,15,18`、`r0_prompt.txt`、`r0.md`末尾、`er062_family_z_writer_01.py:106-109`、旧ブロック`f955847db`。
- 前回との差分: 2026-10-21 text stageで所見(a)として既に記録されていたが検査に昇格しなかった点が新規の整理。
- 次の一手(改善見込み 高): `COMPREHENSIVE_DESIGN_01.md`の推奨案B(Seed側に維持必須要素を構造化し、全Writer段Promptへ引き継ぐ。ランタイムAPI追加ほぼ0、Validator追加なし)をOpusレビュー→ユーザー判断→(承認後)Offline Trial(R0のみ約2円で因果の反証が可能)。
