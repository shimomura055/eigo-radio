# DESIGN_02: Opus条件A必須修正1〜5反映後の設計(FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_02)

作成: 2026-10-25 / Status: **Opus条件A反映済み・DEV/Trial専用・Production未採用**(`APPROVED_FOR_PRODUCTION`/`VALIDATED`/`PRODUCTION_WIRED`ではない)
基礎: `DESIGN_01.md`(案A)+`OPUS_REVIEW_01.md`(必須修正5件+推奨)。DESIGN_01から変わる点のみを書く。変わらない点(案A=Seed→essentials→全段Must-keepで語り口を運ぶ、Validator不追加、Production file無変更)は踏襲。

## 1. 必須修正の反映
| # | Opus指摘 | 反映(DEV実装・記入規則) | 検証 |
|---|---|---|---|
| 1 | key_roles描画("refer to this person by role... without a name")が一人称の語り手を外から呼ぶ指示として働く | (a) Seed記入規則: `narration_voice`の第1項目に「語り手が自分をどう指すか」(例 `speaks as 'I'` / `no narrator in the story`)を必ず書く。(b) Narration行を**Key people行より前**に描画(導入2行の直後)。(c) 同行に汎用1句「The role descriptions of people below do not change who is telling the story.」を添える(作品別の分岐なし)。 | `fz_essence_dev_runner_01_test_01.py::test_arm_iii_with_voice_places_narration_before_key_people_in_full_and_std` |
| 2 | 「keep exactly as in the original」はR1/R2/Stdに原作が渡らず参照不能で、"exactly"は過剰忠実を招く | Narration行を「Keep this narration throughout: the same person, point of view and narrator's stance (including how the narrator speaks to the listener); wording, length and sentence structure may change.」へ。Opus案の「how he speaks」は性別を前提にするため「how the narrator speaks」に1語置換(意味不変)。Seed例文末尾の「do not retell it in the third person」を**削除**(禁止はテンプレート側の汎用文のみ)。REVISE固定句"in third person, "はarm iiiで"in the narration described in the Must-keep section below, "へ。 | 同test(`exactly`/`as in the original`/`third person`がNarration行に無い)、`do not retell`がDEV Seedに無い |
| 3 | free_to_cut「narrator's repeated arguments that he is wise and cunning」とnarration_voice「relishing his own cunning」の矛盾 | 汎用記入規則: **free_to_cutに`narration_voice`の担い手(語りの質の源)を丸ごと入れない。削れるのが繰り返しだけなら「repetitions of …」と書く**。DEV Seedコピーのfree_to_cut[0]を「repetitions of the narrator's arguments that he is wise and cunning」へ。`narration_voice`は3点(自称・聞き手との関係・その作品の面白さの源となる語りの質1点)の**記述だけ**とし、「1〜2例は残す」のような内容ノルマは入れない(DESIGN_01 §3-3の「1〜2例は残す」案は**撤回**)。 | `test_dev_seed_free_to_cut_does_not_swallow_voice_carrier` |
| 4 | 1aは現行/案Aの2アームでは「欄が要るか」が切り分けられない | 1aを**3アーム×各2サンプル=6 call**に拡張: (i)現行Production文言 (ii)汎用置換のみ・Seed欄なし(B'。er055 `NEUTRAL_CONVERSION_PLAN`の先例と同型)(iii)案A。 | `PREREGISTERED_CRITERIA_01.md` §1。arm iのPromptはProduction `r1_prompt.txt`とbyte一致(`test_arm_i_equals_production_r1_prompt_file`) |
| 5 | 評価基準の穴 | 基準を`PREREGISTERED_CRITERIA_01.md`に作り直し、**生成前にcommit**: 三人称作品は「完成版+ノイズ帯以内、かつ地の文の一人称は原作にもある語り手の論評に限る(引用確認)」。一人称作品のStd youは「≥1かつAdvと人称一致」。過剰忠実の上限(youがr0の2倍超=9以上)をFable読みの観点に追加。 | 同文書 |

## 2. 推奨の反映
- Phase 2は『賢者の贈り物』→『開いた窓』→『猿の手』の順(語り手介入の副作用が最も出やすい作品を先に)。
- ノイズ帯の限界: 既存の複数run(pntrial/sftrial/sf_prod)はPromptが異なるため純粋なサンプリング揺れより幅が広い/単一run参照は狭い、という限界を報告に明記。『告げ口心臓』は1b 2本+既存sf_prodの3点で幅を見る。
- `_CONVERSION_SUBSTITUTIONS`(`er062_family_z_writer_01.py:130-134`、"third-person English"を含む正規表現)は、一人称作品のSeedの`conversion_plan`雛形に流用しない。→ **Seed作成手順への1行**(採用時にSeed作成手順書へ追記する。`ADOPTION_NOTE_01.md`に記載)。

## 3. 採用時の整合(Opus (d))
Trial中は「欄がある作品でのみ置換」(DefaultOffIsolation確認のため)。**採用時はnarration_voiceを全essentials作品で必須**にする(`validate_source_essentials`に1項目)と、置換条件は既存の「essentialsの有無」(名前置換と同じ切替。Melosだけが従来どおり)と一致し3状態目が生まれない。作品別例外ではなく、既存4作品のSeedに1行追記すれば足りる(公開版は変わらない)。※これはTrial結果が(iii)に決まった場合の話。(ii)に決まった場合は欄が不要で、REVISE固定句を全作品で汎用文へ置換するだけ(`ADOPTION_NOTE_01.md`)。

## 4. 実装(DEV/Trial専用。Production file差分0)
- `fz_essence_dev_runner_01.py`: `sftrial_dev_runner_01.py`同型。メモリ上でのみ `_render_essentials_block`/`build_revise_prompt`/`REVISE_USER_TMPL` を差し替え、`uninstall()`で復元。出力は`er026_output/family_z_dev_trials/fz_essence_01/`のみ。flag新設なし。
- DEV Seedコピー: `dev_seed/the_tell_tale_heart/`(Production `seed/`のコピー+`narration_voice`+free_to_cut[0]修正+再計算した`SEED_PROVENANCE.json`)。
- `fz_essence_metrics_01.py`: 決定論指標(LLM判定0)。
- DefaultOffIsolation test: `fz_essence_dev_runner_01_test_01.py`(8件)。narration_voiceが無いProduction Seed(全4作品のessentials)では描画関数・REVISE Promptが元関数とbyte同一、arm iiiでも同一(欄が無いSeedではREVISE置換が起動しない)、uninstallで復元、出力先がDEV dirのみ、をassert。

## 5. 『告げ口心臓』DEV Seed narration_voice(記入規則どおり)
`The narrator speaks as 'I' (an unnamed first-person speaker) and keeps addressing the listener as 'you'; his calm, proud, over-confident voice, insisting that he is sane while he relishes his own cunning, is where the horror comes from.`
(第1項目=自称 'I' / 第2=聞き手'you' / 第3=面白さの源である声の質。作品別の禁止文・内容ノルマなし。)
