# PROPER_NOUN_TRIAL_01 (FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_01B, 2026-10-23)

Status: TRIAL_COMPLETE(共通ルールのみ=メロス達成/開いた窓は未達、作品個別指定=開いた窓で達成)。Production無変更。本文のみ・音声なし。

## 1. 決定(反映済み)
ユーザー決定(区分B、APPROVED_FOR_PRODUCTION[仕様決定]・未配線): docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_USER.md:128。CURRENT_SPEC Family Z節(「旧人物名ルール・外国人名ルールの扱い」の直後の追記)、DECISION_LOG、OPEN-464、UDR #160へ反映(commit c56b7bf00)。

## 2. Prompt差分と override 方式
- 現行Prompt(Production、無変更)の固有名詞指示箇所: `er062_family_z_writer_01.py` R0_BLOCK_COMMON「Only the main character…may be given a personal name…」(:94)、R0_BLOCK_PRESERVATION最終bullet(:109)、REVISE_USER_TMPL「only {main_character} may have a personal name」(:142)、`STORY_MAIN_CHARACTER`(:379)。Std段(STD_PROMPT_*)は名前指示なし(Advから名前が引き継がれる)。**Seed(凍結)の`conversion_plan`にも「Framton Nuttel as the only person with a personal name」(開いた窓)/「using only Melos as a personal name」(メロス)、`discarded_elements`に「Names of minor people…」が埋め込まれている**(Seedは凍結・Trialでも無変更)。
- 共通ルール(作品固有名なし、`pntrial_dev_runner_01.py` COMMON_NAMING_POLICY): 「固有名は主人公のみ。ただし物語の中心人物、または展開・結末の理解に重要な人物は、主人公/脇役の別なく原作の名前を維持。重要性で判断し登場回数では判断しない。それ以外は役割・関係性。名前を増やすこと自体を目的としない。First/Lastは一方のみ。他の命名指示(Seed内を含む)より優先」。R0_BLOCK_COMMON(キャラ節の命名文を置換+[Naming policy]ブロック追加)、R0_BLOCK_PRESERVATION最終bullet、REVISE_USER_TMPLを差替え。Std Promptは無変更。
- 方式: `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/pntrial_dev_runner_01.py`がProduction moduleをimport後、メモリ上でPrompt定数のみ差替えて`er062.main()`を呼ぶDEV専用script(Production file書換0)。Productionからの参照0(Grep: 参照するのはこのscript自身のみ)。`--variant common`=共通ルールのみ、`--variant per_story`=共通ルール+作品個別メモ`STORY_PROPER_NOUN_KEEP={"the_open_window":["Framton","Vera"],"melos":["Melos"]}`([Names for this story]ブロックとREVISEの名前列挙を追加)。
- 実際に送ったPrompt: 各run_dirの`writer/r0_prompt.txt`・`r1_prompt.txt`等。

## 3. 実行
モデル: gpt-6.1-sol(Production Writerと同一。最新世代最上位系、provenance.jsonのactual_model_id)。Seed/原作は既存Production Seed(`<story>/seed`)を無変更で再利用(メロス=受入済みrun_e2e_06と同じSeed)。writer(R0→R1→R2)+std_adjustのみ。音声段・plan/support/kpは未実行。
| run | 内容 | run dir |
|---|---|---|
| 開いた窓 共通 | variant=common | er026_output/family_z_production_e2e_01/the_open_window/run_pntrial_01 |
| メロス 共通 | variant=common | er026_output/family_z_production_e2e_01/melos/run_pntrial_01 |
| 開いた窓 個別 | variant=per_story | er026_output/family_z_production_e2e_01/the_open_window/run_pntrial_02 |

## 4. 結果(`pntrial_eval_01.py/.json`。名前=回数/初出段落)
| 作品 | run | レベル | 語数 | 固有名詞 | 目標 | 不要な名前増加 |
|---|---|---|---|---|---|---|
| 開いた窓 | 共通ルールのみ | Adv | 421 | Framton 5(段落1) | Framton+Vera → **未達(Vera無)** | なし |
| 開いた窓 | 共通ルールのみ | Std | 455 | Framton 6(段落1) | 同上 **未達** | なし |
| 開いた窓 | 作品個別指定 | Adv | 419 | Framton 5(1), Vera 6(段落2) | **達成** | なし(Sappleton/Ronnie/Nuttel無) |
| 開いた窓 | 作品個別指定 | Std | 436 | Framton 5(1), Vera 6(段落2) | **達成** | なし |
| メロス | 共通ルールのみ | Adv | 411 | Melos 7(段落3) | Melosのみ → **達成** | なし(Dionysius/Selinuntius無。友・王は"his friend"/"the ruler") |
| メロス | 共通ルールのみ | Std | 451 | Melos 9(段落3) | **達成** | なし |
(参考 受入済み現行: 開いた窓 Adv/Std 共にFramton 7+Nuttel 1[フルネーム1回]、メロスMelos 7。現行版にVera無。)
既存WARN/Gate: Adv warnings=全run空(NAME_RULE_NOTE含め0)、Std warnings=STD_AVG_SENT_LEN_NOT_SHORTER(soft、開いた窓共通8.20 vs adv 6.23、個別8.55 vs 7.35、メロス9.10 vs 7.80。baselineでも同種のsoft gate)、failures 0、語数は全て330-470内、Std/Adv段落数一致。

## 5. 共通ルールのみ/個別調整の区別と分析
- 共通ルールのみ: メロス=達成(Melosのみ、他は役割名)。開いた窓=**Veraは残らず**(Framtonのみ。R0/R1/R2/Stdいずれにも不在)。
- 原因分析(観測): (a)R0 Promptに送られるSeedのseed_elements/conversion_planに「Vera」の名前が**一度も出ない**(名前は`original_summary`にのみ存在し、R0 Promptには含まれない。r0_prompt.txt grepでVera 0)。モデルは「少女(the girl/niece)」としか知らず、共通ルール「原作の名前を維持」の"原作の名前"を参照できない。(b)Seed `conversion_plan`が「Framton Nuttel as the only person with a personal name…the girl(the niece)」と明示し、`discarded_elements`も「the girl's name」の省略を許容。共通ルールに「他の命名指示より優先」を入れたが、モデルは名前を持たない"the girl"を維持した。(c)共通ルール文は機能している(メロスでDionysius/Selinuntiusを増やしていない=過剰使用なし、First/Last一方のみもFramton単独で維持)が、「重要人物」の判定対象が原作名を知っている場合に限られる。
- 共通Promptの改善余地(**記録のみ・再Trialしない**): 重要人物の原作名をモデルへ渡す共通機構が必要。案1=R0 Promptに`original_summary`中の人名(または「key characters」欄)を共通フォーマットで渡す(作品固有名はSeedデータ側に置き共通Promptに埋め込まない)。案2=Seed生成段(上流)で`conversion_plan`/`discarded_elements`の命名文を新ルールに合わせる(既存Seed凍結のため再生成or編集=Seed変更はユーザー/Fable判断)。案3=作品個別メモ(本Trialで有効性確認済み)。費用増は案1/2とも約0(Prompt数十token増)。
- 作品個別指定(`STORY_PROPER_NOUN_KEEP`): 開いた窓=Framton+Vera達成。Veraは段落2で初登場し、台詞の話者・叔母との関係(her fifteen-year-old niece)が自然に説明され、役割名のみの現行より「少女Vera」を追える。他の人物は役割名のまま(her aunt/the aunt's husband)で人物関係・因果の理解は損なわれない。**注意**: 個別runのAdvは結末が犬の作り話(「He said he preferred cats」)で終わり、下記のオチ文なし。

## 6. 開いた窓のオチの有無(観察のみ・オチ補完Promptは追加していない)
- 受入済み現行(run_e2e_01): 犬の作り話で終了(`“He said they took turns.”`)、種明かし文なし。
- 共通ルールrun(run_pntrial_01): Adv最終文「Inventing stories at short notice was her speciality.」あり/Std「She was very good at making up stories quickly.」あり。
- 個別指定run(run_pntrial_02): Adv/Std共に最終は犬の作り話(「He said he preferred cats.」)、種明かし文なし。
- 解釈: 1試行ずつの観測で、命名ルール変更がオチの有無を決めたとは言えない(命名Promptはオチに触れていない)。run間のゆらぎ(確率的)の可能性が高い。01Aの参考データとして記録のみ。

## 7. 本文以外への影響(静的・API0。`pntrial_impact_check_01.py/.json`)
- speaker roster/Voice割当: `STORY_VOICE_ROSTER`のspeaker keyは固定keyで本文の名前の有無に依存しない(vera=Zephyr/framton=Algieba/mrs_sappleton=Kore/men=Schedar、melos=Algieba/dionysius=Charon/selinuntius=Erinome pin)。変更0。
- plan段の話者判定: 決定論keyword(`z_voice_keywords`)は名前+役割語(girl/niece/aunt/friend/ruler等)を両方持つため、Vera有無にかかわらず機能。決定論解決数(quotes中): 開いた窓baseline Adv 6/18・共通 9/18・個別 8/21、メロスbaseline 5/11・共通 4/12。未解決分は従来どおりLLM判定(llm_only)に回る。Veraの有無で解決率が悪化しない(個別でvera=6)。
- KP選定/Preview/Comment: 既存どおり本文から生成(本Trialでは未実行=静的確認のみ)。`STORY_LINT_CONFIG["the_open_window"]["forbidden_names"]`(Preview/Commentに出さない人名: Sappleton/Ronnie/ヴェラ等)に「ヴェラ」があり、Vera採用時はPreview/Commentで人名を出す方針との整合を配線時に要見直し(現時点は変更しない)。Writer `NAME_RULE_NOTE`はWARNのみ(短い'Vera'は含まれず、Trial中0件)。
- 発音: 「Vera」は新たな固有名詞TTS対象(Pronunciation Ledger未登録、Framtonは#157で発音アラーム)。配線後の音声生成時にASR/発音QA対象になる(本Trialは音声なし)。

## 8. 費用(出典: 各run_dirの`raw_usage_log.jsonl`とrunner出力`spent_jpy`)
開いた窓 共通 15.96円(writer 8.81+std 7.15)、メロス 共通 20.93円(8.84+12.09)、開いた窓 個別 18.73円(10.79+7.93)。**合計約55.62円**(見積: 共通2作品約36円+個別約18円=約54円、上限100円内)。本日累計(約80円+55.6円≒約136円)は日次1,000円内。再生成・音声・ASRの費用0。

## 9. Production無変更の証拠
`git diff HEAD --stat -- er062_family_z_writer_01.py er062_family_z_structure_01.py er026_family_z_fiction_production_runner_01.py er063_family_z_audio_01.py` 出力なし。DEV script以外にPrompt override参照0(Grep `pntrial_dev_runner_01|STORY_PROPER_NOUN_KEEP|COMMON_NAMING_POLICY`=当該DEV scriptのみ)。Seed/公開ページ/音声/Production run_dir無変更。

## 10. 次の一手(Fable向け)
Veraを共通ルールで残すには「重要人物の原作名をPromptへ渡す共通機構」(§5案1)が必要。配線時の選択肢(未決): 案1(共通機構・作品固有名はSeedデータ側)/案3(作品個別メモ)。ユーザーはPrompt調整とWriter Prompt配線を委ねており(原文§5)、仕様判断は不要で技術選択はFable。
