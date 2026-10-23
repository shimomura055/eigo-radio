# U1_TRIAL_RESULT_01 (FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_03, 2026-10-23)

Status候補: **VALIDATED候補**(Sonnetの提示。確定はFable独立レビュー後。採用ではなく、`APPROVED_FOR_PRODUCTION`/`PRODUCTION_WIRED`ではない)。本文のみ・音声なし・Production無変更。
ユーザー原文: docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_USER_02.md(§2 Phase 1、承認済みTrial範囲のみ。独自合格基準なし)。

## 1. 条件
- モデル: gpt-6.1-sol(Production Writer既定と同一、最新世代最上位系。各run `writer/provenance.json`のactual_model_id)。effort=high。条件間でモデル・effort・語数目標は同一。
- DEV runner: `sftrial_dev_runner_01.py`(Production moduleをimportしメモリ上でprompt関数だけ差替え。Productionへの参照0)。Seedは`sftrial_seeds/{t1,t2}/`のコピー(Production seed.json無変更)。生成は`sftrial_make_seeds_01.py`。
- Seed修正版(T1/T2共通、同一sha): (i)`source_essentials`(5キー: ending_reveal[meaning+source_quote逐語「Romance at short notice was her speciality.」+withhold_until_end]/setups_and_payoffs 1件/key_roles[Framton・Vera=keep_name true、叔母=false]/key_causality/free_to_cut)、(ii)`conversion_plan`: 「only person with a personal name」→「main character」、結末定義に原作最終文を追加し「最後の行の後に説明を足すな」を「自分の説明は足すな。原作自身の最終文は説明ではなくクロージング行として維持」に改訂、`seed_elements[5]`に最終文を明記、(iii)`discarded_elements`から少女の名前省略を除去(叔母・兄弟の名前省略は残す)。
- T1「Seed修正のみ」= Promptは現行のまま(R0 PromptにSeedが入るだけ。`source_essentials`は読まれない)。T2「修正版B」= 上記Seed + Prompt側: essentialsブロックをR0(編集方針の直後)/R1/R2(出力指示の直前)/Std(`Keep the essence`の直前)へ同一の決定論文字列で挿入、keep_name人物がいる場合のみ命名文3箇所(R0_BLOCK_COMMON :94相当、R0_BLOCK_PRESERVATION最終bullet :109相当、REVISE_USER_TMPL :142相当)を上書き、Std版に「closing line(final reveal)は要約・新説明の禁止の対象外」を明示。結末前の示唆禁止(withhold)はR0/R1/R2の同一ブロックに併記(Stdは入力が完成稿のため除く)。自己チェック不採用。
- 実行(別run dir、`er026_output/family_z_production_e2e_01/the_open_window/`): T1 `run_sftrial_t1_01..03`(R0)、T2 `run_sftrial_t2_01..03`(R0)、T3 `run_sftrial_t3_01/02`(T2の`01`/`02`のR0をそのまま起点に再利用[`r0_reuse_source.json`]、R1→R2→Std)。承認外の追加run 0。
- Prompt実物: 各run `writer/*_prompt.txt`。T2のR0/R1/Stdの実物はdry-run出力と同一(`sftrial_dev_runner_01.py --arm t2 --run x`)。

## 2. 結果表(`sftrial_eval_01.py/.json`。名前=回数。語数は全段330〜470内)
### 2-1 T1(Seed修正のみ)/T2(修正版B) R0 各3本
| run | 語数 | 種明かし最終文(最終段落) | Vera | 固有名詞 |
|---|---|---|---|---|
| T1-01 | 429 | あり「Romance at short notice was her speciality.」 | 無(the niece) | Framton 6+Nuttel 1(フルネーム1回)、Bertie 2(歌詞) |
| T1-02 | 432 | あり(同文) | 無 | Framton 5+Nuttel 1(歌詞なし[Bertie無]) |
| T1-03 | 430 | あり(同文) | 無 | Framton 5+Nuttel 1、Bertie 2 |
| T2-01 | 426 | あり(同文) | **有 5(段落2初出)** | Framton 7、Bertie 2(Nuttel無) |
| T2-02 | 418 | あり(同文) | **有 6** | Framton 7、Bertie 2 |
| T2-03 | 421 | あり(同文) | **有 5** | Framton 5、Bertie 2 |
- 「Bertie」は歌詞の一部(登場人物名ではない)。他の人名(Sappleton/Ronnie/Mr.・Mrs.等)の増加は全run 0(大文字語の文中出現も0)。
- 種明かし保持: **T1 3/3、T2 3/3**。いずれも結末前の説明漏れ候補語なし(T1-02の"tease her"は歌詞の文脈=漏れではない)。語数・伏線(窓・白いコート・歌[T1-02除く]・スパニエル)は全runで保持。

### 2-2 T3(修正版B全段)×2: 各段の最終段落・Vera・名前
| run | 段 | 語数/段落 | 最終文(引用) | Framton/Nuttel/Vera |
|---|---|---|---|---|
| T3-01 | R0 | 426/30 | "Romance at short notice was her speciality." | 7/0/5 |
| | R1 | 440/30 | "Inventing convincing stories at a moment's notice was Vera's speciality." | 7/1/7 |
| | R2 | 433/31 | 同上(直前に追加文"She spoke so naturally that no one questioned her.") | 5/1/6 |
| | Std | 457/31 | "Making up stories in seconds was Vera's special skill."(直前"She sounded so sure that nobody thought she was lying.") | 5/1/6 |
| T3-02 | R0 | 418/27 | "Romance at short notice was her speciality." | 7/0/6 |
| | R1 | 418/25 | "Inventing convincing stories at a moment's notice was Vera's special talent." | 6/1/7 |
| | R2 | 420/23 | "Making up convincing stories on the spot was Vera's special talent." | 5/1/6 |
| | Std | 427/23 | "Vera was very good at inventing believable stories in seconds." | 5/1/6 |
- 全段で種明かしの意味が最終段落に残り、Stdの要約削りも発生せず(2/2)。R1以降は原作の逐語文が言い換えに変わる(意図どおり=意味維持。逐語は要求しない)。
- 既存決定論検査: Adv(R2)warnings=[](語数・NAME_RULE_NOTE含め0)。Std: failures 0、段落数Adv一致(31/31, 23/23)、同一文率0.02/0.00(FAIL閾値0.50未満)、`STD_AVG_SENT_LEN_NOT_SHORTER`のsoft WARN(9.33 vs adv 7.22、8.37 vs 7.64)=過去の全Z runも同種(01B 9.10/8.55、baseline 8.58)の既存WARN。「ヴェラ」: `forbidden_names`(Sappleton/Ronnie/サプルトン/サップルトン/ロニー/ヴェラ)は部分文字列照合で、英語本文の"Vera"は不一致→NAME_RULE_NOTE 0。**日本語のPreview/Comment(Std support)で「ヴェラ」が出るとlint対象のまま**(配線時にkeep_name人物をforbidden_namesから外す必要。本Trialでは変更せず記録のみ)。権利Gate: Seed rights_status無変更。

## 3. essentials充足(Fable CPチェックリスト試作=Sonnetが読んで引用。自動判定ではない)
| 項目 | T3-01 Std | T3-02 Std |
|---|---|---|
| ending_reveal(種明かし自体が最終に在る) | 充足「Making up stories in seconds was Vera's special skill.」 | 充足「Vera was very good at inventing believable stories in seconds.」 |
| withhold_until_end(結末前に説明していない) | **軽微な懸念**: 最終直前「She sounded so sure that nobody thought she was lying.」(犬の作り話が嘘だと語る。結末の1行前=ほぼ結末の予告。R2は"no one questioned her") | 充足(結末前に示唆なし) |
| setups_and_payoffs(窓・bog・白いコート・歌・スパニエル→人影→逃走→男たちの帰還) | 充足「A white coat lay across one man's shoulders.」「He heard a young voice sing, 'Bertie, why do you bound?'」「Those men were back from the bog!」 | 充足「One carried a white coat over his arm.」「A young man called out, 'Bertie, why do you bound?'」「...dead men walked towards him.」 |
| key_roles(Framton/Vera名、叔母・夫は役割) | 充足(Vera 6、"her aunt's husband") | 充足 |
| key_causality(作り話→叔母が裏付け→逃走→犬の作り話) | 充足(「She still expects them to come home」「Here they come」→grabbed his hat→"He ran because of the spaniel") | 充足 |
(R0/R1/R2も同様に充足。T3-02 Stdは地の文が平易化され「bog」語が"deep mud"になるが意味は維持。)

## 4. 再現性の評価(限界を明記)
| 条件 | n | 種明かし保持 | Vera |
|---|---|---|---|
| 現行Seed+現行Prompt(参考値、既知観測) | 01B共通run 1/1(保持)、01B個別run 0/1(欠落)、run_e2e_01 0/1(欠落)=計1/3 | | 無 |
| T1 Seed修正のみ(R0) | 3 | 3/3 | 0/3 |
| T2 修正版B(R0) | 3 | 3/3 | 3/3 |
| T3 修正版B全段 | 2 | 2/2(全4段) | 2/2 |
- **所見**: Seedの結末矛盾(`conversion_plan`の「最後の行の後の説明禁止」が原作最終文を含んでしまう)の修正だけで、R0の保持はT1・T2とも3/3。T1とT2は種明かし保持では**区別できない**。ROOT_CAUSE_02の主因仮説(Seed conversion_plan+結末維持条項の消失)と整合。Veraについては、Prompt側のkeep_name上書き+Seed(key_roles)の1セット(T2)でのみ達成(T1 0/3)=名前ルールの三重制約(R0/R1/R2)上書きが必要という設計(4-1)と整合。
- **限界**: n=3(T3はn=2)。0/3や3/3の差は小さなnでは偶然と区別できず、「1回成功=解消」とは結論しない。T2のessentials(ブロック)が、Seed修正だけに対しR1/R2/Std段での欠落防止に**追加で効く**かは、T1の全段実行(承認範囲外)が無いため本Trialでは示せない。参考値は条件が異なり(旧Seed、凍結版)比較は参考止まり。Seed修正後にseed_elements[5]へ原作最終文を逐語で入れたため、モデルが最終文を逐語コピーした可能性(T1・T2のR0は全て逐語、R1以降は言い換え)。ノイズは語数・段落数(23〜31)にも出る。
- 再現性の改善の観測根拠は「新Seed条件下のT1・T2のR0計6本とT3全段2本のうち欠落0件」まで。構造的リスクが解消したとは断定しない(残リスク§6)。

## 5. 固有名詞(keep_name)
- 目標=FramtonとVeraのみ。T2/T3は達成(Vera全段で保持、Sappleton/Ronnie等の増加0)。**残る点**: T3のR1以降で「Framton Nuttel」が冒頭に1回出る(T2のR0はFramtonのみ)。原因=`REVISE_USER_TMPL`の`{main_character}`が`STORY_MAIN_CHARACTER["the_open_window"]="Framton Nuttel"`(Production現行、baselineでも同様のFramton 7+Nuttel 1)。新規の人名ではなく同一人物のフルネーム併記で、受入済み現行と同水準だが、「FirstかLastの一方のみ」(01B共通ルール)とは厳密には異なる。Fable判断事項(`STORY_MAIN_CHARACTER`をkeep_nameで上書きするか、許容か)。
- 共通Promptへの作品固有名の埋込: なし(Vera/Framtonは`seed.json`の`source_essentials.key_roles`のみ。`sftrial_prompt_tests_01.py`でR0 PromptがProduction文面と差がないことを確認)。
- 『走れメロス』: (a)essentials無しSeed(Production melos seed)で、新機構(`build_r0_prompt_t2`/`make_revise`/`make_std`)のR0/R1/Std Promptが現行Productionと**byte一致**(pytest 5件PASS、API 0)。さらに`build_r0_prompt_t2(melos seed)`のdevelopers+userのsha=受入済み`melos/run_e2e_06/writer/r0_prompt.txt`と一致(True)。(b)01B共通ルールrun(`melos/run_pntrial_01`、Melosのみ達成)との差分: 01B共通版は`[Naming policy]`ブロックと命名文2箇所が追加された別Promptで、新機構(keep_name未指定)はProduction現行と同一であり、**01B共通ルールPromptとは実質同一ではない**(差分7行=命名ポリシー段落と`Keep the cast small...`のbullet)。メロスの結果としては、現行Production文面(=新機構)のrun_e2e_06がMelos 7のみ、01B共通版もMelos 7のみで、いずれも名前増加なし(`pntrial_eval_01.json`)。メロスを新機構で変更する必要はなく、新機構を有効にするのはSeedに`source_essentials`を置いた作品のみ。

## 6. 失敗例・残リスク
1. T3-01 R2/Stdで、結末の1行前に語り手が追加した文(R2 "She spoke so naturally that no one questioned her." / Std "She sounded so sure that nobody thought she was lying.")。`withhold_until_end`の趣旨(結末前の示唆禁止)に軽く触れる。R0にはなく、R2/Std段での自発的付加。essentialsブロックはこれを防げなかった(1/2)。Fable CPの観点4(結末前の示唆)で検出可能。決定論LEAK語検出(lying等)でも検出できた(eval json `possible_pre_ending_leak_words`)が、新Gateにはしない。
2. 種明かし最終文の逐語コピーがR0に偏る(Seedに逐語を入れたため)。他作品でSeedに最終文を入れる運用が必須(`ending_reveal.source_quote`のFable照合)。
3. nが小さい。T1の全段(Seed修正のみでR1/R2/Stdまで通した場合)を実施していないため、essentialsのR1〜Std段での追加効果は未実証。
4. フルネーム併記(§5)。Std段のA2らしさ: soft WARN(平均文長)は既存同水準。Std T3-02は地の文が平易で、T3-01よりやや平板という所見(印象)。
5. 日本語support(Preview/Comment)の`forbidden_names`に「ヴェラ」が残る(配線時に要修正、API 0の設定値変更)。発音Ledger未登録のVeraが音声段で新規固有名詞TTS対象。
6. ProductionのCPで未充足が出た場合はTTS前に修正する(設計6-3)。人間運用のためFable CPの実効性に依存。

## 7. 所見(事実と所見の分離)
- 事実: 全ての本文が330〜470語、Std/Adv段落数一致、failures 0、固有名詞はFramton(+Nuttel 1)/Vera/歌詞のBertieのみ。Veraは段落2で「said Vera, her fifteen-year-old niece」として導入され、叔母との関係が最初に説明される。
- 所見(Sonnet、Fable確認要): 名前付きのVeraは台詞の話者が追いやすく、語り手の最終文が「Vera's speciality」と人物に紐づくため、オチが説明の追記ではなくストーリーの結びとして機能している。Storytellingの面白さ(間・緊張)はAdv全runで同水準。A2らしさの定量はsoft WARNのみ(既存基準)。

## 8. 費用(出典: 各run_dir `raw_usage_log.jsonl`、`sftrial_run_meta.json`の`spent_jpy`)
T1 R0: 2.19/1.88/1.76、T2 R0: 2.08/1.58/1.69(計11.18円)、T3 R1〜Std: 14.91/12.95(計27.86円、R0はT2費用に計上)。**Trial合計 39.03円**(上限60円・ユーザー承認概算40円内)。Std単体は推論トークンのばらつきで5.6〜11.0円。
量産単価への影響: essentialsブロックによる入力トークン増はR0 1,442→1,959、R1/R2 約700→1,140、Std約1,306→1,800(+約450〜500/段、合計約+1,900tok、数銭未満)。追加API呼出0。Writer chain実費(R0〜Std)は修正版B 14.5〜17.0円 vs 参考(01B共通15.96円、baseline R2+Std約13.8円)で、出力トークンのばらつきの範囲内。70円/記事セット目標への影響は無視できる。

## 9. Production無変更の証拠
`git diff HEAD --stat -- er062_family_z_writer_01.py er062_family_z_structure_01.py er026_family_z_fiction_production_runner_01.py er063_family_z_audio_01.py` 出力なし。`seed/`(Production)に変更0(`git status --short .../the_open_window/seed`=空)。`sftrial_dev_runner_01|source_essentials|sftrial_seeds`を参照する.pyはDEV script3本のみ(Grep)。音声・公開ページ・Production Seed/Prompt変更0。新規LLM呼出・Gate・Validator・retryの追加0。

## 10. Fable独立レビュー論点
- T1とT2が種明かし保持で区別できない点をどう扱うか(Seed記入規則の改訂だけで足りる可能性)。essentialsの追加価値は主にkeep_name(Vera)と全段引継ぎの設計上の担保。
- 結末直前の付加文(§6-1)をCP観点4でどう扱うか。
- `STORY_MAIN_CHARACTER`のフルネームと「FirstかLastのみ」(§5)。
- Stdのclosing line明示は有効だったか(2/2で最終文が残ったが、対照なし)。
- Status: VALIDATED(提示。承認範囲内の観測のみで、独自合格基準なし)。ユーザーの正式採用判断はPhase 2のPM Gate。
