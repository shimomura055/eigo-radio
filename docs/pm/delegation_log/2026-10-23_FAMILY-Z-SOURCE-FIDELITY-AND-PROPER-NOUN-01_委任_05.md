FABLE-DELEGATION-MARKER: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01-委任_05-WIRING-20261023

# 委任_05: Phase 3 — 原作忠実性 包括対策「修正版B全体」(APPROVED_FOR_PRODUCTION、ユーザー正式採用2026-10-23)+固有名詞`keep_name`のFamily Z Production配線・テスト・runtime evidence・SSOT

## T-0
1. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_委任_05.md`(N≈339〜349、先頭行MARKER一致確認)。
2. ユーザー指示原文(§1)を `docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_USER_03.md` に逐語保存。
3. **先にユーザー決定をSSOTへ**: DECISION_LOG(修正版B全体=APPROVED_FOR_PRODUCTION、対象5項目、原文所在)、OPEN-465=`APPROVED_FOR_PRODUCTION_WIRING_IN_PROGRESS`、OPEN-464同様、UDR #164=判断済み(採用)。CURRENT_SPECのFamily Z該当節に仕様を追記(Status=APPROVED_FOR_PRODUCTION、未配線)。commit/push。
4. ACTIVE_TASK.md: 別agent(FAMILY-Y 委任_04、DEV/er110系、X基盤の読取利用)が並行。編集直前に再読込し、本管理ID行のみ更新。有料呼出の直前/直後に「有料run進行中/終了(時刻)」。

## 1. ユーザー指示原文(逐語)
```
# Claude Code / Fableへの指示
## Family Z『開いた窓』— 修正版B正式採用・Production Wiring・完成候補制作

### 1. ユーザー決定

原作忠実性の包括対策「修正版B全体」を**正式採用(APPROVED_FOR_PRODUCTION)**する。

対象は以下のとおり。

- Seedの「維持必須要素」スキーマ(最大5件)
- R0/R1/R2/Standardへの重要要素の引継ぎ
- `keep_name` による必要な固有名詞の保持
- Standardにおける原作最終行・結末の明示的な保持
- 既存CPの処置規則(重大な欠落は修正・原因分析、必要ならC案提示。軽微な不要文は削除・記録)

既存の承認済み仕様と整合させること。新たな意味保持Validator、LLM検査、retry、Human Review工程は追加しない。

### 2. 実行範囲

**Phase 3 → Phase 4 → 比較試聴ページ公開まで、一連の作業として進める。**

**Phase 3:Production Wiring**

- 正式初回Production経路に修正版Bを実装する。
- retry/fallback/regeneration/resumeとの整合を確認する。
- Trialで検証したPromptとの一致をテストする。
- 『開いた窓』の名前設定をFramton/Veraに統一し、不要なフルネームや日本語側の旧禁止設定を修正する。
- 他作品への副作用がないことを回帰テストで確認する。
- 正式runtime evidence、SSOT更新、Git反映を完了する。
- Fableが独立評価し、全受入条件を満たした場合のみ `PRODUCTION_WIRED` と判定する。

**Phase 4:『開いた窓』完成候補制作**

- Phase 3の正式Production経路を使用する。
- 承認済みのFamily Z会話速度仕様を統合する。
- Standard/Advancedの両方を制作する。
- 原作の重要要素、伏線、結末の種明かし、人物名の保持を確認する。
- 結末直前の不要な付加文など、オチの効果を弱める表現も確認する。
- Veraの発音は既存の固有名詞検査・音声品質管理で対応する。
- 既存の承認済み品質基準をすべて満たすことを確認する。

**比較試聴ページ**

- Standard/Advancedを切り替えて試聴可能にする。
- 全編再生・パート別再生・スクリプト確認に対応する。
- ユーザーが完成候補を評価できる状態で公開する。

### 3. 進行・QCD方針

- 品質>速度>量産単価を遵守する。
- 承認済み範囲の不具合はFable/Claudeで原因分析・修正・再検証まで自律的に解決する。
- 不要な追加Trial、品質基準の独断変更、未承認仕様の導入は行わない。
- 作業を不合理に日付分割・直列化せず、独立作業は並列化して完成までの時間を短縮する。
- 量産単価70円/記事セットを意識し、不要なAPI呼出・再生成を避ける。
- 開発費は既存の承認済み予算・日次上限を守る。
- 重大な品質・安全問題、承認範囲外の仕様変更、予算超過、解決不能なblockerのみユーザー判断に上げる。

### 4. 最終報告・受入条件

①〜③を完了した時点で、以下をまとめて報告すること。

1. Phase 3の `PRODUCTION_WIRED` 判定とruntime evidence
2. 『開いた窓』Standard/Advanced完成候補の品質評価
3. 比較試聴ページURL
4. Fableによる独立受入結果
5. 実費・制作時間・量産単価への影響
6. 残存リスク・未解決Open Item・SSOT/Git反映状況

**原則、途中報告によるユーザー承認待ちは設けず、完成候補まで一気通貫で進めること。**

ただし、新仕様の採用判断が必要になった場合は、無断採用・無断Production反映をせず、該当部分をUSER_DECISION_REQUIREDとして報告する。

最終的な作品完成承認は、ユーザー試聴後に行う。

Family Yの進行中Trialについても、既存の承認範囲を維持し、不必要に停止させないこと。
```

## 2. 配線仕様(正本: `COMPREHENSIVE_DESIGN_02.md`+`OPUS_REVIEW_02_U1.md`の配線パッケージ+`U1_TRIAL_RESULT_01.md`「Fable判定」節。優先順)
1. **Seedスキーマ** `source_essentials`(最大5件・意味レベル・各1文、`ending_reveal`+`withhold_until_end`対、`setups_and_payoffs`[結末成立に不可欠なものだけ]、`key_roles`[`keep_name`付き]、`key_causality`、`free_to_cut`、`source_quote`は原作最終段から逐語必須)。**新規のFamily Z文学作品はessentialsが無いとSeed承認(seed_check相当)を通さない**(fail-closed)。既存作品の互換: Melosは対象外(essentials無しで従来どおり、PromptはProduction現行とbyte一致をtest固定)。Seed承認手順(Fable CPでsource_quoteを原作最終段と照合)をrunbook/CURRENT_SPECに明文化。
2. **全段引継ぎ**: `build_r0_prompt`/`build_revise_prompt`(R1/R2)/`build_std_prompt`へessentials文字列を**引数で渡す**(グローバル差替え禁止)。Seedから決定論的に1文字列を生成し全段同一。essentials shaを各段の入力指紋(キャッシュ/resume判定、`DEPENDENTS`連鎖)に組込み、provenanceにsha記録。retry/fallback/regen/resumeの全経路がSeedからessentialsを渡すことをtest固定。Std Promptにはessentials行で「最終の種明かしは本文の一部であり要約ではない(closing summary禁止の対象外)」を明示。自己チェック出力は入れない。
3. **keep_name上書き**: `key_roles.keep_name=true`の人物名を、R0の「Only the main character … may be given a personal name」(er062_family_z_writer_01.py:94)・`REVISE_USER_TMPL`(:142)・Seed `conversion_plan`の「only X may have a personal name」より優先する文言(作品名は共通Promptに入れない。「一方の名前のみ」節をREVISE側にも)。`STORY_MAIN_CHARACTER["the_open_window"]`(:379)を"Framton"へ。`STORY_LINT_CONFIG["the_open_window"].forbidden_names`(er062_family_z_structure_01.py:808)からkeep_name人物(ヴェラ)を外し、keep_name人物とそのカナ表記が禁止名に含まれないtest。
4. **『開いた窓』Production Seedの更新**: `the_open_window/seed/seed.json`に`source_essentials`を追加(T2 Seed `sftrial_seeds/t2/seed.json`を正として反映)、`conversion_plan`の結末矛盾を是正(原作最終文は「説明禁止」の対象外)、`discarded_elements`から少女の名前省略を除去、`key_roles`にFramton/Vera(keep_name)。旧Seedは`seed_STALE_<date>.json`退避。
5. **CP処置規則**: Fable CPチェックリストをessentialsから機械生成(本文該当引用の必須欄)。重大(ending_reveal・key_roles・key_causality・setups_and_payoffsの欠落)=CP不合格→修正→原因分析→C案要否提示/軽微(結末直前の付加文等withhold希釈)=決定論の削除パッチ+記録。**自動判定・LLM検査・retry・HRは追加しない**。`E2E_PLAN`/CPテンプレートに処置規則を追記。
6. **Trial Promptとの一致test**: 配線後の『開いた窓』R0/R1/R2/Std PromptがT2/T3 dump(`run_sftrial_t2_*/writer/*_prompt.txt`、`run_sftrial_t3_*/writer/*_prompt.txt`)とbyte一致(意図した名前修正="Framton"化・REVISE一方名節のみ差分許容、差分を列挙)。Melos Promptは現行とbyte一致。
7. **回帰**: 新規test+既存Zテスト+`run_project_regression.py`単独 failed 0/errors 0、pytest別枠。X/A/B/C無変更(Z専用ファイルのみ編集。共有moduleを触らない)。

## 3. runtime evidence(費用: Writer全段 約15〜17円。上限40円、超過見込みならSTOP)
- 正式Production経路(er026 runner、`--stage writer`/`std_adjust`相当の正式stage。DEV runner不可)で『開いた窓』の本文を新Seedから生成(新run dir `the_open_window/run_sf_prod_01`。これが**Phase 4で使う本文**になるため、音声段は本委任では実行しない=Phase 4で同runを継続)。証拠: provenanceのessentials sha、各段PromptのTrial dumpとの一致、R0/R1/R2/Std全段で種明かし保持・Vera維持・他人名増加なし・5段落/語数/段落数一致・既存決定論検査、CPチェックリストの機械生成結果と**Fable CP相当の記入**(Sonnetが本文引用を貼る。重大欠落があれば修正[承認済み方式]、軽微な付加文があれば削除パッチ+記録)。resume整合: 同runで`--stage writer`を再実行→キャッシュ再利用(sha一致)で再生成0を確認(費用0)。
- Melos: essentials無しで正式経路のPrompt生成がbyte一致(test)、本文再生成はしない(費用0)。

## 4. SSOT/Git
- CURRENT_SPEC(Family Z: 原作忠実性包括対策v1=Seed essentials/全段引継ぎ/keep_name/Std最終行明示/CP処置規則、Status=`WIRED_PENDING_FABLE`、Fable受入後PRODUCTION_WIRED)、固有名詞ルール(OPEN-464)も同Status、旧「主人公のみ」記述の履歴化、10-12③④との関係の注記(新Validator/LLM検査なし)。OPEN-465/464、DECISION_LOG、OF-FZSF-U1-M01〜M06 → IMPLEMENTED_VERIFIED、REPORT_LEDGER。commitは論理単位(配線+test / Seed更新+runtime evidence / SSOT)、明示add、secret_scan `--staged` hits=0、`git push origin HEAD:main`。共有SSOTは編集直前`git status`→自分の行のみ→即commit。

## 5. 禁止
- 新しい意味保持Validator・LLM検査・retry・HR工程の追加、共有module(X/A/B/C到達)の変更、Melos本文・音声・公開ページの変更、音声生成(Phase 4)、個別パッチでの本文手修正(軽微付加文の決定論削除パッチはCP処置規則として可・記録必須)、`PRODUCTION_WIRED`の自己宣言。

## 6. 報告(docs/pm/RESULT_PACKET_FZSF5.md、同内容を最終報告で)
(1)Status候補 (2)実装(ファイル:行、Seedスキーマ、引継ぎ、keep_name、名前修正、forbidden_names、CP処置規則) (3)Trial Promptとの一致test結果(差分列挙) (4)runtime evidence(run_sf_prod_01: 全段の保持結果、CP記入、resume) (5)テスト・回帰数値、Melos不変 (6)費用(出典) (7)commit・raw URL・SSOT (8)Phase 4へ引き継ぐ事項(run dir、本文確定、Vera発音の扱い、会話速度仕様の統合点) + RESULT_PACKET 4行 + 「判定整合: 重大NG=あり/なし」。