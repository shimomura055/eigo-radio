# WIRING_DESIGN_01: 案A Production Wiring設計(設計のみ。API 0・Production file編集0)

作成: 2026-10-25 / 委任_03 / 状態: 案A=APPROVED_FOR_PRODUCTION(ユーザー正式承認2026-10-25、原文=`docs/pm/delegation_log/2026-10-25_FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01_USER_02.md`)。本書は**配線設計であり、実装はOpus条件Aレビュー後のFable Go(委任_04)**。この時点のStatusはPRODUCTION_WIREDではない。

## 0. 先行検証(API 0、Production file無編集)
設計どおりの差分を**scratchpad上のコピー**(`wiring_proto_patch_01.py`が`er062_family_z_writer_01.py`の複製へ4か所の置換を適用)に当て、Production Seed+記入予定`narration_voice`から作ったR0/R1/R2/Std Promptを、Trialが実際にLLMへ送ったPrompt dumpと比較した。

| 作品(Trial dump) | R0 | R1 | R2 | Std |
|---|---|---|---|---|
| 賢者の贈り物(`er026_output/family_z_dev_trials/fz_essence_01/the_gift_of_the_magi/p2_s1/writer/`) | byte一致 | byte一致 | byte一致 | byte一致 |
| 開いた窓(`.../the_open_window/p2_s1/writer/`) | byte一致 | byte一致 | byte一致 | byte一致 |
| 猿の手(`.../the_monkeys_paw/p2_s1/writer/`) | byte一致 | byte一致 | byte一致 | byte一致 |
| 告げ口心臓(`.../the_tell_tale_heart/1b_s1/writer/`、**Seed全体=dev_seed**で組立) | byte一致 | byte一致 | byte一致 | byte一致 |

- 実行: `py docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/wiring_proto_patch_01.py <scratch>/w_patched.py`(cwd=repo root)→ `wiring_proto_cmp_p2_01.py <scratch>` / `wiring_proto_cmp_tth_01.py <scratch>`(結果は上表。比較スクリプトは`<scratch>/w_patched.py`を読む)。
- **重要な発見**: 告げ口心臓のProduction Seedとdev_seedは`narration_voice`だけでなく**`free_to_cut`も違う**(Prod=「the narrator's repeated arguments that he is wise and cunning, …」、dev=「repetitions of the narrator's arguments that he is wise and cunning, …」。Opus修正3「語りの質の源をfree_to_cutに丸ごと入れない」に基づく変更)。`narration_voice`だけ足した場合はTrial dumpと不一致(再現: 4段とも`- May be cut or compressed:`行のみDIFF)。**告げ口心臓のSeed補完は`narration_voice`追記+`free_to_cut`のdev_seed文への差替えの2点**。賢者・開いた窓・猿の手は`narration_voice`のみ追記でdev_seedとSeed全体で一致(スクリプトで`seed==dev_seed`=True)。
- 限界: 上表は「Productionに入れる差分がTrialで検証した差分と同一」の証明であり、LLM出力の挙動そのものではない(挙動はTrial Phase 1/2の結果に依拠)。

## 1. 変更箇所一覧(file:行は変更前の現行)
### 1-1. `er062_family_z_writer_01.py`(Z専用。X/Yからimportされない)
| # | 場所 | 現行 | 新(Trial DEV実装との対応) |
|---|---|---|---|
| W1 | 定数(`_REVISE_TAIL`:384の直後) | なし | `_REVISE_THIRD = "in third person, "` / `_REVISE_NARR = "in the narration described in the Must-keep section below, "` / `_NARR_LINE = "- Narration: {voice} Keep this narration throughout: the same person, point of view and narrator's stance (including how the narrator speaks to the listener); wording, length and sentence structure may change. The role descriptions of people below do not change who is telling the story."`(DEV `fz_essence_dev_runner_01.py:26-30`の`REV_III`/`NARR_LINE`と**文言同一**) |
| W2 | `_render_essentials_block`(403-433)、導入2行(405-407)の直後 | 導入2行→Ending行 | `L.append(_NARR_LINE.format(voice=ess["narration_voice"].strip()))`を導入2行の直後(=Key people行[425]より前)に1行追加。mode=full/std共通(Std調整は`block_std`経由で同一行が入る=`build_std_prompt`は無変更)。DEV `render_dev`のindex 2 insertと**同位置** |
| W3 | `build_revise_prompt`(533-541)の`if essentials is not None:`内 | keep_names置換と`_REVISE_TAIL`置換のみ | `assert _REVISE_THIRD in tmpl; tmpl = tmpl.replace(_REVISE_THIRD, _REVISE_NARR, 1)`を追加(既存`_REVISE_NAME_SENT_KEEP`置換と同型・assert付き)。**置換条件は既存の`essentials is not None`そのもの**(新flag・新分岐なし)。DEV `revise_dev`のarm iiiと同一置換 |
| W4 | `Essentials.__init__`(394)の先頭 | 検査なし | `narration_voice`が非空文字列でなければ`FamilyZSeedEssentialsStop("FAMILY_Z_SEED_ESSENTIALS_INVALID: narration_voice(必須)")`。**essentialsを構築できる唯一の入口で必須化**=「essentialsはあるがnarration_voiceが無い」第3状態をPrompt builderへ到達させない(Opus (d)) |
| W5 | `validate_source_essentials`(447-491)、`free_to_cut`検査(473-474)の直後 | なし | `narration_voice`が非空文字列でなければ`why.append("narration_voice(必須: 語り手の自称・立場を第1項目に記述)")`。戻り値dict(489)へ`"narration_voice": nv`を追加(seed_checkのe2e_stage_logにSeed記入文が残る)。`n_items`(5件上限)には**含めない**(DEVと同じ) |
| W6 | `build_cp_checklist`(817-855)、`key_causality`行(841)の直後 | なし | `items.append(("重大", "narration(人称・語り手の立場が各stageで保たれている)", ess["narration_voice"]))`。記入はCP担当(Fable確認)、自動判定なし。DEV `cmd_chain`(`fz_essence_dev_runner_01.py:171-172`)と同趣旨 |
| W7 | `run_writer_chain`(718-795)、`REVISE_USER_TMPL`(139-142) | 無変更 | **無変更**。`REVISE_USER_TMPL`のベース文言`in third person, `(141)はessentials無し=Melos用にそのまま残る(§1-4)。`validate_source_essentials`(730)→`build_essentials`(731)→各stage builderへ`essentials=ess`(758-766)は既存の全stage・全経路共通の配線 |

### 1-2. `er062_family_z_structure_01.py`
影響なし(R0〜Std Promptを作らない)。`STORY_SPEAKER_CONFIG["the_tell_tale_heart"]`の`attr_roster_text/attr_caution_text`(316-318)は既に一人称前提で、Advが一人称に戻ることで食い違いが解消する方向(ROOT_CAUSE_01.md:72)。コード変更0。

### 1-3. `er026_family_z_fiction_production_runner_01.py`
**コード変更0**。
- seed_check(`stage_seed_check`:1306-1332)は`validate_source_essentials`を呼ぶ(1321)ので、W5の必須検査が**自動的にseed_check段で効く**(narration_voice欠落=`FamilyZSeedEssentialsStop`でseed_check停止、writer到達前)。戻り値の`source_essentials`(1331)にW5の`narration_voice`が入りe2e_stage_logへ記録される。
- writer(`stage_writer`:1336-)/std_adjust(`stage_std_adjust`:1349-)は`run_writer_chain`を呼ぶだけで、Promptはその内部(W2-W3)で作る。runnerにPrompt文言は無い(`grep -n "third\|Narration" er026_...runner...py`=0件)。
- retry/fallback/regeneration/resume(すべて`run_writer_chain`の同一コード経路。Promptはstage実行の**前**に毎回Seedから作り直す純関数=状態を持たない):

| 経路 | 入口 | narration_voiceがPromptに入る根拠 |
|---|---|---|
| 初回 | `--stages seed_check,writer,std_adjust` | `run_writer_chain`:730-731→758-766 |
| `--regenerate-stage r0/r1/r2/std_adjust` | `_regen_for`(runner:1272)→`regenerate_stage` | 同一`run_writer_chain`。prompt生成(758-766)は`regen`判定(`ensure_stage`、781)より前=同一builder |
| resume(出力済みstage) | `ensure_stage`(674)の再利用判定 | `in_sha = sha(prev_sha + "##ESSENTIALS##" + ess.sha256)`(781)。`ess.sha256`は`narration_voice`を含むess全体のJSON sha=**Seedのnarration_voiceが変わると旧本文を黙って再利用せずSTOP**(既存機構。`er062_family_z_source_essentials_test_01.py:302`のtestが既に固定) |
| 部分run(`stages=("r1",)`/`("std_adjust",)`) | `stage_std_adjust`(runner:1356) | stagesに無いstageは出力を読むだけ(740-747)。実行stageは同builder |
| LLM技術retry(2回、`llm.call`内) | `runner`クロージャ(771-777付近) | `user`文字列は外側で1回構築され固定=retryでPromptは不変 |
| 外側retry/HR resume/`_bak_*`退避/`voice_assignment_STALE_*`(runner:2326-2333) | plan以降(KP/TTS/gate) | writer Promptに関与しない(本文確定後の段) |

- **runtime evidence**(正式runで残るもの。新規ログ追加なし): ①`<run>/writer/{r0,r1,r2,std_adjust}_prompt.txt`(各段Prompt全文dump、writer:768の`wt(...)`)に`- Narration: <voice> Keep this narration throughout…`行と、R1/R2の`in the narration described in the Must-keep section below,`が入る ②`writer/provenance.json`の各chain entryの`prompt_sha256`・`essentials_sha256`(766)・`actual_model_id`/`routing_key`/`requested_model`/`cost_jpy`(`_chain_fields`:707)とtop-levelの`source_essentials_sha256`(734) ③e2e_stage_logのseed_check `source_essentials.narration_voice`(W5) ④`writer/cp_checklist.md`のnarration行(W6)。Prompt dumpのGrep(`Narration:`が4段、`in the narration described`がR1/R2、`in third person`が0件)でFableが機械確認できる。

### 1-4. 旧固定文言(`in third person`)の撤去対象/残置の確認(現状Grep)
`grep -rn "in third person" --include=*.py`(test・docs/research除外)の結果: ①`er062_family_z_writer_01.py:141`(`REVISE_USER_TMPL`ベース文言)②`er012_editorial_b_voices_trial_08_audio.py`③`er059_melos_sol_b3z_trial_01.py`(②③はTrial旧script。Production runner/writerはimportしない)。testでは`er026_family_z_story_registry_open_window_test_01.py:181`(Melos用の旧byte固定test。**essentials=Noneの経路**を検査しておりW3後も有効=更新不要)。
- 実装後の状態: Production `REVISE_USER_TMPL`の`in third person, `は**essentialsのあるSeed(Melos以外の全Z作品)では必ず置換**され、残るのはessentials無し(`ESSENTIALS_EXEMPT_STORIES=("melos",)`:371)の経路のみ。
- **判断B(Fable確認、Opus論点b)**: 『走れメロス』は原作が三人称でessentials対象外(完成版不変。Promptはbyte一致を`er062_family_z_source_essentials_test_01.py:57`のGOLD shaで固定)。Melosに`narration_voice`を求めず`in third person`を残すことは、原作の語り口(三人称)と**矛盾しない**ため、承認文の「推敲工程に残る三人称固定指示の撤去」の趣旨(一人称原作で人称を壊す指示の撤去)に反しない、というのが設計の解釈。代替(Melosにもessentialsを課す/ベース文言を汎用句に置換)はMelosのPromptがbyteで変わり、完成版不変の前提と衝突するため**推奨しない**。「Grep上の残存1か所=Melos専用」を矛盾する旧指示の残存と見なさない運用でよいか、Opus/Fableが確認する。

### 1-5. 「人物を名前ではなく役割で呼ぶ」指示との整合
Key people行(`er062_family_z_writer_01.py:425`)の`refer to this person by role or relationship, without a name`は、一人称の語り手(`key_roles`の`the narrator`)を三人称で呼ばせる原因だった(ROOT_CAUSE_01.md:47、"the old man's housemate")。W1の`_NARR_LINE`末尾の汎用1句`The role descriptions of people below do not change who is telling the story.`(Opus修正1)が**Key people行より前**に置かれ、役割説明が語り手を外から呼ぶ指示でないことを示す。Key people行・R0の`_R0_NAME_SENT`等の既存文は**無変更**(新たな文学基準・作品別禁止ルールの追加なし)。

## 2. Seed補完(正本の確認)
- Writerが実際に読むのは**Production seed置き場** `er026_output/family_z_production_e2e_01/<story>/seed/seed.json`(`E2EContext.seed_dir`=runner:1251-1253、`run_writer_chain`:722、`SEED_PROVENANCE.json`のshaで凍結検査:724-726)。`er026_seeds/<story>/seed.json`はその**複製元**(`SEED_PROVENANCE.json`の`source_dir`)で、5作品とも現状**byte同一**(`cmp`で確認)。各story registry testが両者のsha一致を固定している(例`er026_family_z_story_registry_after_twenty_years_test_01.py:109`)。→ **両方に同一内容を書き、`SEED_PROVENANCE.json`のshaを更新する**(片方だけだとtestが落ちる)。
- 旧Seed退避: 『開いた窓』の先例(2026-10-23の`seed_STALE_20261023.json`)に倣い、各作品の旧`seed.json`を`seed_STALE_20261025.json`として両置き場に退避してから更新(削除しない)。
- `narration_voice`記入規則(ADOPTION_NOTE_01 §4): (a)第1項目に語り手の自称(`speaks as 'I'`/`told in the third person by an outside narrator`) (b)記述のみ。作品別の禁止文・内容ノルマを書かない (c)`free_to_cut`に語りの質の源を丸ごと入れない (d)一人称作品のSeedに`_CONVERSION_SUBSTITUTIONS`の三人称雛形(`er062_family_z_writer_01.py:130-134`)を流用しない。

| 作品 | 記入文(`source_essentials.narration_voice`) | 出典・状態 |
|---|---|---|
| 告げ口心臓 | The narrator speaks as 'I' (an unnamed first-person speaker) and keeps addressing the listener as 'you'; his calm, proud, over-confident voice, insisting that he is sane while he relishes his own cunning, is where the horror comes from. **加えて`free_to_cut`をdev_seed文へ差替え**: ["repetitions of the narrator's arguments that he is wise and cunning, the old man's imagined thoughts and the personification of Death, the graphic details of how the body was dealt with, and the officers' formal introduction"] | dev_seed(Phase 1/1b/1c検証済み)と**Seed全体で一致** |
| 賢者の贈り物 | The story is told in the third person by an outside narrator, close on Della and Jim, in a warm, gently ironic voice. | dev_seed(Phase 2検証済み)と一致。観察: `free_to_cut`に"the narrator's jokes and asides"が既にある(Trialと同状態で人称不変を確認済みなので**変更しない**) |
| 開いた窓 | The story is told in the third person by an outside narrator, close on Framton, in a cool, dry, matter-of-fact voice that plays the events straight. | dev_seed(Phase 2検証済み)と一致 |
| 猿の手 | The story is told in the third person by an outside narrator in a quiet, restrained voice; the fear comes from sounds, silence and what the characters say and do. | dev_seed(Phase 2検証済み)と一致 |
| 二十年後 | The story is told in the third person by an outside narrator, close on Bob, in a plain, matter-of-fact voice. | **Trial未検証(dev_seed無し)**。三人称3作品の記入パターンに倣った**Sonnet起案**。Fable確認事項(判断B)。Trial dumpとのbyte照合はできない |
| 走れメロス | **記入しない**(essentials対象外=従来どおり。Promptはbyte同一をGOLD testで固定) | §1-4 |

- Seed変更後、`SEED_PROVENANCE.json`の`files.seed.json.sha256`と`note`/`date`を更新。`primary_text_excerpt.md`は不変。
- **副作用S-1(要判断)**: `Provenance.__init__`(`er062_family_z_writer_01.py:612-619`)は、provenance内の`seed_sha256`と現行seed.json shaが違うと`FamilyZProvenanceMismatchStop`。`stage_plan`/`stage_support`/`stage_kp`(runner:1421/1440/1697の`_prov(ctx)`)も同じ`_prov`を使う。したがって5作品のSeedを書き換えると、**既存の完成済みrun dir(例 `the_tell_tale_heart/run_sf_prod_01`、`the_open_window/run_sf_prod_01`ほか)に対し`--stages plan/support/kp`等を再実行するとSeed凍結違反でSTOPする**(writer/std_adjustの再実行も元からessentials sha不一致でSTOP)。公開済みページ/音声と`writer/`の本文は不変で、公開物への影響はない。「Seedは凍結、変更ならrun新規作成」という既存設計の帰結。
  - (M3・推奨)現状仕様のまま受容する。既存5作品の再実行が必要になった場合は新run id(writer再生成)で行う。告げ口心臓は今回新run `run_sf_prod_02`で再生成するので影響なし。他4作品は完成済みで再生成予定がない。
  - (M4)必要になった時点で、`apply_cp_deletion_patch`の親付替え(`cp_parent_relink`、writer:870-896)と同型の「provenanceへ`seed_sha256`付替え(旧sha・新sha・理由を記録)」手順を別委任で設ける。コード追加を伴うので今回の設計には入れない。
  - 分類: **実害なし**(公開物・音声・本文は不変、将来の運用制約)。Fable確認(Opus論点b)。`OPEN_ITEMS.md`のOPEN-508備考に記録(§SSOT)。

## 3. test計画(実装は委任_04。本委任ではtestを書かない)
### 3-1. 更新が必要な既存test
| test | 理由 | 方針 |
|---|---|---|
| `er062_family_z_source_essentials_test_01.py`の`test_r0_byte_identical_to_t2_and_t3_dumps`(160)/`test_r1_r2_match_t3_dumps_except_intended_name_diff`(171)/`test_std_byte_identical_to_t3_dumps`(181) | 開いた窓のProduction Promptが`narration_voice`分だけT2/T3 dump(案A導入前)と一致しなくなる | 期待値を**Trial Phase 2 dump**(`fz_essence_01/the_open_window/p2_s1/writer/*_prompt.txt`、案A込みで実送信されたPrompt)のbyte一致へ差替え。旧T2/T3は「Narration行1行+REVISE置換1か所の意図した差分のみ」を検査する形に(既存`_revise_expect`型) |
| `test_production_seed_equals_t2_trial_seed`(86)ほか、OW Seedを`T2_SEED`とbyte比較している箇所 | Seedが`narration_voice`分だけ変わる | 期待値を「T2 Seed+narration_voice 1キー」へ(dict比較で差分キーが`narration_voice`のみであることを検査) |
| `er062_family_z_source_essentials_test_01.py`の`_seed()`/essentials fixture、`er062_family_z_writer_01_test_01.py`の同fixture(`build_essentials`を呼ぶtest) | W4で`narration_voice`欠如は`FamilyZSeedEssentialsStop` | fixtureへ`narration_voice`を追加。欠如を意図するtestは新規testへ |
| 5件の`er026_family_z_story_registry_*_test_01.py`(`test_source_essentials_pass_seed_approval_check`ほか) | Seedに`narration_voice`が入る(W5で必須)。PROD/trial Seed sha一致 | 両置き場に同一内容を書くため追加なしで通る見込み。通らなければ原因分類 |
| `test_checklist_generated_from_essentials`(342) | W6でnarration行が増える | needleに`narration`を追加 |
| `fz_essence_dev_runner_01_test_01.py`(DefaultOffIsolation 8件) | 本体へ昇格後はDEV差替えが不要 | 本体testへ性質(欄なし=例外、arm iii相当)を移植。DEV runnerは「Trial専用・歴史的」注記のみで削除しない |
| `er026_family_z_story_registry_open_window_test_01.py:181`(Melos旧byte固定) | essentials=None経路=Melos | **更新不要**(W3は`essentials is not None`のみ) |
| `er062_family_z_writer_01_test_01.py:1015`(`test_old_targets_not_in_prompt_constants`) | `REVISE_USER_TMPL`等を数字走査 | 通る見込み |
| `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/sftrial_prompt_tests_01.py`等のTrial test | `build_essentials`をnarration_voice無しで呼ぶ可能性 | 全回帰で落ちたら自分起因か分類し、歴史的dump比較ならfixtureにvoice追加、不要なら対象外記録 |

### 3-2. 新規test(`er062_family_z_source_essentials_test_01.py`へ追加。課金0)
1. 描画順: block_full/block_stdとも導入2行の直後・`Ending`行と`Key people`行より前に`- Narration:`が1行だけ。
2. Std調整への伝達: `build_std_prompt(adv, essentials=ess)`に同一Narration行。
3. REVISE: essentialsありのPromptに`in third person`が0件、`in the narration described in the Must-keep section below,`が1件。essentials=None(Melos)のPromptは既存GOLD shaのまま。
4. fail-closed: `narration_voice`なし/空/空白のみ/非文字列→`validate_source_essentials`と`Essentials()`直接構築がともに`FamilyZSeedEssentialsStop`(メッセージにnarration_voice)。Melos(exempt)は従来どおり`{"present": False, "exempt": True}`。essentialsありでvoice無しのPromptがどこからも作れない(3状態目なし)。
5. 全段・全経路への伝達(既存265の拡張): mock LLMで通常/`regenerate_stage`/resume/部分run、いずれのstage Prompt dumpにも`Narration:`行。`narration_voice`を変えたSeedでresume→STOP(既存302と同型)。
6. 旧固定文言のGrep test: Production module(`er062_family_z_writer_01.py`)ソースの`"in third person"`が`REVISE_USER_TMPL`の1か所のみ、かつ`_REVISE_THIRD`置換assertと対になっていること(動的な3と合わせて固定)。
7. 5作品の実Seed(Production seed置き場)から組んだR0/R1/R2/StdがTrial dump(賢者/開いた窓/猿の手=`p2_s1`、告げ口心臓=`1b_s1`)とbyte一致(§0の検査のtest化=「Trial結果の再利用」の根拠を回帰で固定)。二十年後はTrial dumpが無いため構造検査(Narration行1件・REVISE置換・Key people行の位置)のみ。
8. Seed記入規則の軽い構造検査(記入規則であり本文Validatorではない): 5作品の`narration_voice`が非空・第1文に自称(`told in the third person by an outside narrator`または`speaks as 'I'`)を含む。`free_to_cut`に`narration_voice`が丸ごと含まれない。
9. CPチェックリストのnarration行(W6)。
10. 新stage/Validator/routing key不変(既存`test_no_new_stage_or_validator_added`:333がそのまま通る)。
### 3-3. 全回帰
全回帰(自分起因のfailed/errors=0)。実装前にHEAD基準の回帰結果を保存し、実装後の差分を分類(基準は`docs/research/TEST-HYGIENE-02/REGRESSION_BASELINE_01.md`)。

## 4. 既存作品の副作用確認計画(再生成しない)
- 根拠1(Prompt): §0の4作品byte一致(実装後はtest化=§3-2の7)。ProductionのPromptが**Trialで実際にLLMへ送られたPromptと同一**であることを根拠に、Trial Phase 2(賢者/開いた窓/猿の手)の「人称不変・語数/文長範囲内・欠落0」を再利用する。ただし猿の手の段落数+8は事前基準±4を**未達**で、ノイズか副作用か未確定(PHASE2_RESULT_01.md)=再利用する結論の限界。
- 根拠2(未カバー): 『二十年後』はTrial Phase 2の対象外。三人称3作品で挙動不変だったことの類推のみで直接の検証は無い(**Opus論点dで妥当性を確認**)。再生成は行わず、次回この作品を扱う時の初回CPで確認する運用を提案(費用0)。
- 実装後のAPI 0確認: 5作品について、Production経路のbuilderで全stage Promptを組み、(a)`Narration:`行の位置 (b)`in third person`が0件 (c)Key people行・name-sentence置換が不変、を検査。Melosは既存GOLD shaと一致。
- Family X/Yへの波及なし(`er062_family_z_writer_01.py`はZ専用。`er111_pn_entity_table_trial_01.py`は`key_roles`のみ読み`narration_voice`を参照しない)。

## 5. 『告げ口心臓』正式再生成計画(委任_04以降。本委任では実行しない)
- 事前: Opus条件Aレビュー→Fable Go→Production実装(W1-W6+Seed5件+test)→全回帰PASS→commit/push(ここまでが「配線」)。
- 正式runner: 有料runは`.venv\Scripts\python.exe er026_family_z_fiction_production_runner_01.py --story the_tell_tale_heart --run run_sf_prod_02 --mode real --approved-budget-jpy 70 --tts-execution-mode STANDARD --stages <段>`(共通引数は`docs/research/FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01/CP_CHECK_01.md`:17の実績と同一)。新run id=`run_sf_prod_02`(既存`run_sf_prod_01`は上書きしない。Seed sha変更でresume不可になるため新runが必須=§2 S-1)。各起動直前に`tools/stop_scope_check_01.py --managed-id FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 --run-dir er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_02 --out <json>`(rc=3なら新規API呼出をせず停止)。
- stage順(1起動1コマンド): ①`seed_check,writer,std_adjust`(narration_voice必須検査が先に効く) → Fable/CP: `writer/cp_checklist.md`のnarration行・原作本質行を確認。Prompt dumpのGrepで`Narration:`/`narration described in`/`in third person`=0を機械確認 → ②`plan,support,kp` → ③`tts_b1b`と`tts_a2`は独立のため**並列2process**(PIDを記録) → ④`provision_shell,gate,assemble,pages,page_verify`を**1起動**(OPEN-480、provision_shell欠落禁止)。
- 見積: 約40円(出典=`RUNTIME_EVIDENCE_01.md`§8: `run_sf_prod_01` writer 9.26+std_adjust 6.84+plan 0.10+support 0.40+kp 5.51+tts_b1b 6.75+tts_a2 7.78=36.64円、委任_04のKP再選定+TTS差替え約3.3円を加え39.97円)。`--approved-budget-jpy`は従来実績と同じ70円(guardが`E2E_STAGE_EST_JPY`[runner:1131]の段別見積を含むため)。案件見積300円以下かつ承認済みScope(UDR #193)内=7-7によりAI自律。当日費用(JST 2026-10-25)は414.66円(`ACTIVE_TASK.md`記載)+本再生成約40円≒455円/1,000円。起動直前に`docs/pm/tools/daily_dev_cost_01.py`で再集計し、1,000円超過見込みなら停止報告。
- Human Review(HR Lock)が出た場合: 既存の自律解決手順(`approve_regenerate`のFable権限は変えない)。
- 公開: `user_test/family_z_tell_tale_heart_01/`(runner `e2e_pages_dir`:506)を`build_pages`が上書き。**旧三人称Advが残らないように**: (i)pages前に旧ディレクトリを`er026_output/family_z_production_e2e_01/_pages_backup_tell_tale_heart_pre_fzse_20261025`へ退避(既存`_pages_backup_open_window_pre_b5_20261023`の先例)(ii)pages後に`advanced.html`と`audio_advanced`の各mp3 shaが`run_sf_prod_01`版と異なること、`audio_advanced`の全ファイルがrun_sf_prod_02のtimeline由来であること、`advanced.html`に旧三人称特有表現("housemate"等、ROOT_CAUSE_01.md:47)が無いことをGrep/sha比較で確認 (iii)`page_verify_local.json`でindex/standard/advanced HTTP200・console_errors 0・plays_failedなし。
- 語り口の維持評価(受入時): CP checklistのnarration行(一人称'I'・聞き手'you'への呼びかけ・自己正当化/自己陶酔の語りが各stage本文に引用できるか)をFableが確認。承認文§4の品質重点は**新たな内容ノルマではなく確認観点**として使い、自動判定・追加Validatorは設けない。
- ユーザー最終試聴PASSは**先取りしない**(OPEN-503は試聴待ちのまま)。
- runtime evidence項目: `writer/*_prompt.txt`(Narration行・REVISE置換)、`provenance.json`(`prompt_sha256`/`essentials_sha256`/`actual_model_id`/`routing_key`/`requested_model`/`cost_jpy`)、e2e_stage_logの`source_essentials.narration_voice`、cp_checklist.md、gate_result・page_verify。`docs/research/FAMILY-Z-TELL-TALE-HEART-PRODUCTION-01/RUNTIME_EVIDENCE_02.md`へ集約(既存構造に追加、新置き場なし)。

## 6. 撤退
採用commit(Production writer 3か所+Seed 5件の両置き場+SEED_PROVENANCE+test)を**単一commit**に収め、撤退=そのcommitのrevert(Seed追記含む)。`seed_STALE_20261025.json`が旧Seedを保持。公開済み『告げ口心臓』差替えは別commitとし、撤退は旧公開物へのrevert。Trial専用`fz_essence_dev_runner_01.py`はProduction非依存で残置。

## 7. 量産単価
追加LLM呼出0、新Validator 0、新retry 0。Prompt+約90 input token/段(Trial実測 r1 1208→1300 token)=4段で約360 token/記事≒0.05円未満(ADOPTION_NOTE_01の見積と同じ)。70円/記事セット目標への影響は無視できる水準。

## 8. 注意・未解決(報告用)
1. S-1(Seed変更で既存run dirのplan/support/kp再実行不可、実害なし・運用制約、Fable判断B)。
2. 告げ口心臓Seedは`narration_voice`と`free_to_cut`の2点変更が必要(dev_seed全体との一致が検証済み条件)。
3. 二十年後の記入文はTrial未検証のSonnet起案(判断B)。
4. Melosはessentials対象外のため`in third person`がベース文言として残る(判断B、原作が三人称)。
5. 猿の手の段落数+8は事前基準未達のまま(ノイズ可能性)。再利用する「副作用なし」の結論の限界。
