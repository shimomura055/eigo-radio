# IMPLEMENTATION_03 文法解説の事前生成: X/Y/Z runner・ページ・Validator配線(GRAMMAR-PREGEN-ALL-LEVELS-01 委任_03)

Status: **IMPLEMENTED(配線)**。到達上限=IMPLEMENTED(配線)。PRODUCTION_WIREDではない(実run evidence=委任_05が未実施)。API 0・JPY0。新flagなし(承認済みProduction仕様の本配線)。
設計=`DESIGN_02.md`、契約=`SCHEMA_CONTRACT_01.md`、核=`IMPLEMENTATION_02.md`。承認済みPrompt/閾値/辞書/正規表現は編集していない。

## 1. 緊急解消(先行commit `e2785c11a`、origin/main)
委任_02の核(level必須・finalizeのLLM引数撤去)でX/Y/Z runnerのPart 2が `TypeError`(API前fail-closed)になっていたのを、核の新APIへ適合。
- 候補抽出 -> **全候補の解説の事前生成**(`pregen_stage`=Step Bの唯一の呼出点)を、KP候補生成と同じ待機点の**前**(rc=4の前)に両level(Std=a2/Adv=b1b)で実行。resumeはAPI 0(生成済みの解説は再利用、未生成分のみ)。
- 確定後の `finalize_stage` は **LLM 0 call**(LLM引数なし)。`require_final`/`verify_outputs`/`cand_marker`/`public_study_html` はすべて `level=` 必須。
- 先行commitには(分離が困難だったため)ページ/Validator/D4の主要部も含まれる(commit messageに明記)。本commitでD1・整理・docs・test補強。

## 2. 変更ファイルと内容
| ファイル | 内容 |
|---|---|
| `er019_family_x_audio_production_runner_01.py` | `_part2_study_dir/_part2_inputs_x/part2_next_command(level)`、`run_part2_candidates_x`(候補+事前生成、失敗はstage名`part2_cand_<lv>`/`part2_expl_<lv>`)、`run_part2_final_x`(LLM 0・Part 1訳との食い違いISSUEは失敗ではなく待機rc=4)、`_scaffold_part2_final`、scaffold内の両level Part 2(Stdは KP確定後にfinalize、Part 1なし)、`--stage study_text`のAdv限定`parser.error`撤去(`--level a2`で候補->事前生成->待機->finalize)、`build_player_html(study_html_a2=)`・`player_level_section()`(節単位検査用)、player入口は両levelの`require_final`+節単位`verify_outputs`。tts/assemble入口はAdvancedのみ(従来どおり。Stdの文法はページ専用で音声の前提にしない) |
| `er121_family_y_runner_01.py` | `PART2_STAGES`(level別 cand/expl/final)・`UNIT_NAMES`/`DEPENDENTS`に`part2_cand_a2`/`part2_a2`(葉。`translate_a2`の子。TTS等への依存辺なし)、`_part2_cand_step(level)`(候補->事前生成)、`_part2_final_step(level)`(LLM 0)、`_assert_part2_final(level=)`、`_assert_std_part2_ready`(**pages/page_verifyだけ**から呼ぶ)、`stage_pages`でStd節にも同テンプレートの文法ブロック、`_verify_part2_outputs`を節単位(Adv=Part 1直後、Std=Part 1なし)へ、D1`_rebind_kp_on_confirmation`、D4(拒否されたregenerateは`part2_failed.json`を書かずrevoke案内)、cost tag `part2_cand_<lv>`/`part2_expl_<lv>` |
| `er026_family_z_fiction_production_runner_01.py` | Yと同形。`load_level_inputs(a2)`には文法入口検査を**付けない**(TTS/Gate/Assemblyの前提にしない)。`stage_pages`は`study_html_by_level`をbuild_pagesへ。`_verify_part2_outputs`は節(`adv`/`std`)単位+開発確認用`standard.html/advanced.html`に文法が出ていないこと |
| `er062_family_z_writer_01.py` | stage台帳: `std_adjust -> part2_cand_a2 -> part2_a2`(葉)。`rebind_confirmation_input`(D1の共有helper) |
| `er063_family_z_audio_01.py` | `build_pages(study_html_by_level={'b1b','a2'})`(旧`study_html`引数+`label=="Advanced"`限定を撤去) |
| `er_user_listening_page_common_01.py` | `level_section_html(page_html, level_id)`(節切出し。節単位4者一致検査用。無い/重複はValueError) |
| test | `er120_part2_wiring_integration_test_01`(X/Z: 両level・0件・2件採用・事前生成失敗・拒否regenerate・節取違え/欠落)、`er119_z_wiring_test_01`(D1)、`er121_family_y_runner_01_test_01`(Y: 両level・0件・2件・D1・Std入口の分離)、`er119_x_wiring_test_01`/`er119_kp_p7w5_e2e_test_01`/`er019_family_x_kp_stage_fail_closed_01_test_01`/`er003_kp_general_explanation_01_runner_integration_test_01`/`er062_..._source_essentials_test_01`(両level化に伴うfixture更新・期待値更新) |

## 3. D1(自動採用runへ後からユーザー確定 -> `kp_<lv>`来歴の親sha不一致STOP)
- 原因: `kp_<lv>`のinput_sha = sha(本文|KP review署名)。自動採用(UNREVIEWED_AUTO_ADOPTED)run後にフォーム/HRでユーザー確定が入るとreview署名が変わり、`ensure_stage`が親sha不一致でSTOP。`--regenerate-stage kp_<lv>`で解消すると子孫(tts)がstale化=TTS再生成コストに波及。
- 是正(`w62.rebind_confirmation_input` + Y/Z `_rebind_kp_on_confirmation`、API 0): 次の**すべて**のときだけ、entryの入力shaと署名を付け替える(出力は不変・子孫staleなし・`entry['rebinds']`に履歴)。(1)明示`--regenerate-stage kp_<lv>`ではない (2)確定レコードがユーザー確定(live, actor=user) (3)**旧署名で再計算した入力shaが記録済みentryと一致**(=本文は不変。署名変化だけが原因) (4)現在のKP assetsが新しい確定と一致(`_assert_kp_review_consistent`。内容が変わっていれば付け替えず従来どおりSTOP・再生成)。本文が変わった場合は従来どおり親sha不一致STOP。
- 対照実験: Zのtestで再バインドを無効化すると `FamilyZProvenanceMismatchStop: kp_b1b: 親sha不一致` を再現(`/tmp/neg.py`相当、本文参照)。
- 文法側: `part2_<lv>`(finalize)は確定でinput_shaが変わると従来どおり`--regenerate-stage part2_<lv>`を案内する。finalizeはLLM 0・葉のため費用0で、再バインドは設けていない(自動承認でなく明示1コマンド)。

## 4. D4(拒否された`--regenerate-stage part2_cand_<lv>`がpart2_failed.jsonを書き、次の一手が同一コマンドのループ)
- 確定済み文法への再抽出は`guard_grammar`が`CONFIRMED_CONTENT_LOCKED`(Part2Stale)で拒否する。runnerはこれを**失敗記録ではなく操作の拒否**として扱い、`part2_failed.json`を書かない。「次の一手」は`er128 revoke`案内(内容を変えないなら`--stage kp`再実行)で、同じregenerateの繰り返しにならない。確定済みの成果物は無傷。
- 通常の失敗(候補抽出/事前生成)の次の一手も `--regenerate-stage` ではなく「同じ`--stage kp`(X scaffold時は同じscaffold)再実行=未生成分のみ生成」に統一。

## 5. 費用・API
- 実API 0。mock/決定論のみ。事前生成による追加LLM(Std分)は、実runで 候補<=8 x 解説1 call(最大約8 call/level)。evidenceは委任_05(費用上限・go/no-go下記)。

## 6. 委任_05 evidenceへの引継ぎ
- stage列(実run): X: `--stage scaffold --level both`(候補->事前生成->待機rc=4) -> `grammar-select --run <out_dir> --level <a2|b1b> --choice pick --ids ...` + KP select -> 同じscaffold再実行(b1b: Part 1 -> finalize LLM 0、a2: finalize LLM 0) -> (Part 1訳との食い違いISSUEが出たら`grammar-accept-translation`) -> `tts`/`assemble`/`player`。Y: `--stage kp`(両levelの`part2_cand_<lv>`->待機)-> 選択 -> `--stage kp` -> `tts_*`/`gate`/`assemble`/`pages`/`page_verify`。Z: 同上(`kp` -> ... -> `pages` -> `page_verify`)。Z完成段の再実行は`--stages provision_shell,gate,assemble,pages,page_verify`を1起動(OPEN-480)。
- go/no-go: (1)mock E2Eで両level・0件・2件採用が通ること(本委任のtest) (2)実runは6セルで非0件経路を実証、2件採用を1経路で実証、所要時間を測り2分超なら並行化検討(O-2/O-8) (3)実費上限JPY150(EVIDENCE_PLAN_02) (4)`pages`/`page_verify`が節単位4者一致でPASS (5)公開済みX記事scriptは書換えない(履歴)。
- 注意: Std本文の候補0件率が高い恐れ(O-2)は`STD_CANDIDATE_RATE_01.md`参照。0件は固定文面で正常表示。
