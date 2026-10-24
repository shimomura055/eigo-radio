# OPUS_REVIEW_REQUEST_01 (条件A: 新しい構造・処理フローの設計レビュー依頼)

管理ID: FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01 委任_01 Phase 0。依頼者=Fable(本ファイルはSonnetが用意した依頼素案。Opusへ渡すのはFable)。
発火条件: `PM_GOVERNANCE.md` 11-3 条件A(Seed構造[`source_essentials`]とWriter契約の拡張という新しい構造設計)。**Phase 1(有料・実装)はこのレビュー後のFable Goまで開始しない。**
Opusは採用可否を宣言しない(Production採用は人間ユーザーのみ)。ユーザー原文§4「Opusによる独立設計レビューを行い、根本対策として成立しているか確認」に対応。

## (a) 論点(以下8点)
1. **根本原因の特定がevidenceに基づくか**: `ROOT_CAUSE_01.md`の結論(R1の固定文言"in third person"[`er062_family_z_writer_01.py:141`、`r1_prompt.txt:55`]が一人称R0を反転。Stdは偶然一人称に戻る)は、実Prompt・実出力(`r0.md`/`r1.md`/`r2.md`/`std.md`、人称語集計、`provenance.json`のsha照合)で成立しているか。因果の確定は未実施(1aの対照実験が必要)だが、現時点の証拠で十分な仮説か。見落とし要因(例: Must-keepのkey_roles呼称指示と"housemate"の関係)はないか。
2. **対策が上流に置かれValidatorに依存しないか**: 案A(`source_essentials.narration_voice`1欄+全段Must-keep描画+REVISE固定文言の条件置換+CPチェックリスト1行+Seed承認時の非空検査)は、「検出機構」ではなく「そもそも反転しない契約」と言えるか。`validate_source_essentials`の非空検査とCPチェックリスト1行は、ユーザー原文§4の「新たなCheck/Validator不採用」に抵触しないか(本文検査ではなくSeed記入規則・確認入口の補修という整理は妥当か)。
3. **作品固有の例外ルール化・過剰適合の有無**: 欄は全Z作品共通の1文必須記入で、作品別コード分岐は0。『告げ口心臓』用の記入例(自己陶酔・呼びかけ)がPrompt文面に作品固有の語を持ち込んでいないか。一人称原作が本作1件のため、汎用性の検証が三人称作品の「挙動不変」と「語りの質指定が働くか」に限られる点は許容範囲か。
4. **Voice構造・会話生成器との整合**: `ROOT_CAUSE_01.md`§4(`er062_family_z_structure_01.py:316-318`の話者設定が元から一人称前提、Std一人称が既にplan〜assembleを通過)の結論、すなわち一人称Advでも構造変更不要、という判断は妥当か。独白中心の作品で「人物の会話」を要請する構造が人称変更を誘発していないという判断は妥当か。
5. **既存忠実性対策(修正版B)との重複なし・整合**: `narration_voice`は`ending_reveal`/`setups_and_payoffs`/`key_roles`/`key_causality`/`free_to_cut`と役割が重ならないか(語りの質の指定が`free_to_cut`と矛盾しないか、特に『告げ口心臓』のfree_to_cut「narrator's repeated arguments that he is wise and cunning」)。最大5件の上限の外に置く判断は妥当か。`tone`(Opus所見で任意と言及、未実装)との関係はこれで回収されるか。`COMPREHENSIVE_DESIGN_02.md` §3-5(R1/R2へSeed全文を渡さない)の方針と矛盾しないか。
6. **過剰忠実による長さ・冗長・テンポ悪化の副作用**: 追加は1行・約40 token/段だが、「keep exactly」型の強い文言が`free_to_cut`の圧縮を妨げ、語数が上限(470)に張り付く、R1の"more engaging"の効果が弱まる等の副作用が出ないか。Phase 2の副作用指標(語数・平均文長・段落数、既存複数runのノイズ帯との比較)で十分に検出できるか。
7. **量産単価増分**: 追加LLM呼出0・入力Prompt約+40 token/段×4段(<0.05円/記事)の見積は妥当か。D案(conversion_plan全文を全段へ)・E案(R1/R2スキップ)を不採用とした判断は妥当か。
8. **過去Trial/不採用方式の再導入なし**: `ROOT_CAUSE_01.md`§5のGrep結果(Z本文の語り口維持を扱った過去Trialは0件。Family B Voicesの人称関連は別目的)で見落としはないか。撤去済み意味保持Validator(er061)や、2026-10-12決定③④(意味保持Validator不要・Checker増設回避)との整合に問題はないか。

## (b) 背景・事実(Opusが追加ファイルを読まなくて済む最小限)
- 問題: Family Z『告げ口心臓』Adv=ユーザー最終試聴NG(2026-10-25)。原作は一人称独白("I")だが、Advが三人称("He")。Stdは一人称。出来事・因果・結末は維持されていたが、語り手の直接の語りが失われ、エンタメ性を損なう重大品質問題と判断。改善Trialはユーザー承認済み、Production仕様変更・採用は未承認。
- 実測(`ROOT_CAUSE_01.md`§1): 一人称語数/三人称語数 = r0 43/23、r1 0/53、r2(Adv最終)0/51、std(Std最終)41/26、原作173/69。聞き手への呼びかけ"you": r0=4、r1=0、r2=0、std=1。他のZ作品は全て原作も三人称で人称語0〜1。
- 直接原因: `REVISE_USER_TMPL`(`er062_family_z_writer_01.py:139-142`)の固定"in third person"。R1/R2はSeed全文を受け取らず、essentials(語り口の欄なし)のみで制約される。
- 設計: `DESIGN_01.md`。案A=essentialsに`narration_voice`(1文)を追加し、既存のessentials描画経路でR0/R1/R2/Stdへ同一文字列を伝達、REVISE固定文言は欄がある作品でのみ置換、欄がない作品はbyte同一。比較案B〜Eと不採用理由は§2。
- Trial計画: Phase 1=(1a)R1のみ対照A/B(既存r0固定、5.6円)→(1b)全段チェーン×2サンプル(約32円)→(1c)合格時のみAdv音声。Phase 2=賢者の贈り物・開いた窓・猿の手のテキスト(DEV Seedコピー、約44.5円)。見積合計約110円(案件上限150円)。DEV runnerはメモリ上差し替え(`sftrial_dev_runner_01.py`同型)、出力は`docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/out/`のみ。Production無変更。
- 既存資産: 修正版B(`docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/COMPREHENSIVE_DESIGN_02.md`、`OPUS_REVIEW_01.md`/`OPUS_REVIEW_02_U1.md`)、`er062_family_z_writer_01.py`、`er062_family_z_source_essentials_test_01.py`。

### 読むファイル(この順で十分)
`docs/research/FZ-SOURCE-ESSENCE-RETENTION-TRIAL-01/ROOT_CAUSE_01.md` → `DESIGN_01.md` → `er026_output/family_z_production_e2e_01/the_tell_tale_heart/run_sf_prod_01/writer/{r0.md,r1_prompt.txt,r1.md,r2.md,std.md}` → `er062_family_z_writer_01.py` 130-142行・403-433行・447-491行・533-541行 → `docs/research/FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01/COMPREHENSIVE_DESIGN_02.md` §3。

## (c) 参照すべき既存仕様のGrep確認欄(Sonnet記入済み)
- `CURRENT_SPEC.md` 1624付近(修正版B=`PRODUCTION_WIRED`、Family Zのみ)。「人称」Grep結果はFamily B Voices(672-707行)・KP人称一般化(1633-1635,1972行)のみで、Z本文の語り口維持仕様は未定義。
- `DECISION_LOG.md`/`DECISION_LOG_HISTORY.md`/`OPEN_ITEMS.md`/`OPEN_ITEMS_HISTORY.md`: 同Grep。Z本文の語り口(人称)維持に関する決定・不採用方式は0件(B Voices Trial-07は一人称→三人称の機械変換検証で目的が逆)。
- PM_GOVERNANCE 21節分類: 固定文言とSeedの矛盾=A(不具合、11-8)、`narration_voice`欄=C(新規。ただし改善Trialはユーザー承認済み)、B該当なし。

## (d) Opusへの依頼形式
各論点に対し「GO / 条件付きGO(must-fix列挙) / 要再設計」と根拠(ファイル:行)を返す。特に論点1(原因の確度)と論点2(Validator不採用との整合)を重視。must-fixはPhase 1実施前に反映する。Production採用判断は含まない。
