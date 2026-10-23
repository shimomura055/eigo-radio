# COMPREHENSIVE_DESIGN_02: 原作の本質を守る包括対策 修正版B(Opusレビュー反映版)

管理ID: FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01 委任_02 / 2026-10-23 / 設計のみ・API 0
Status: **設計案(採用未承認)**。Trial・Production実装・Prompt変更・撤去Validatorの復活は行っていない。次=U1(Offline Trial承認)。
位置づけ: COMPREHENSIVE_DESIGN_01.md(案A〜D比較表・費用根拠)は履歴として有効。本書は条件付きGOのOpus指摘(OF-FZSF-M01〜M08・S01〜S10、OPUS_REVIEW_01.md)を全反映した現行版。**推奨は修正版B 1案**。案C/Dは採らない。

## 1. 前提・境界(再質問しない=S05)
- ユーザー原文§4「必須の品質方針」(`docs/pm/delegation_log/2026-10-23_FAMILY-Z-SOURCE-FIDELITY-AND-PROPER-NOUN-01_USER.md`)で境界は**既定義**: 維持=重要な結末・種明かし・伏線回収・主要人物の役割/関係/動機・重要因果。許容=脇筋・重複・背景の省略、自然な英語のための表現変更。逐語再現は要求しない。ユーザーに求める判断は「その方針を実装するPrompt/Seed変更のTrial承認」(U1)のみ。
- 2026-10-12決定③④(意味保持Validator不要・別名の意味チェック/独立QAを新設しない・Checker安易に増設しない・品質問題はWriter側Prompt)に整合。撤去済みer061は復活しない(案D、10-12③で既判断)。
- C案(事後確認)は採らない。再発時のみ§8の条件でユーザー提示。

## 2. 修正版Bの骨格
Seedに維持必須要素(essentials)を構造化し、全Writer段(R0・R1・R2・Std調整)へ**同一の決定論文字列**として渡す。**新規LLM呼出・Gate・Validator・retry・Human Reviewは追加しない**。確認は既存Fable CPの細分化(§6)。

## 3. 設計の中身
### 3-1 essentialsスキーマ(`seed.json`の任意キー`source_essentials`)
最大**5件**・各**1文**・**意味レベル**(④への逆戻り=逐語要求の防止、M03)。
| キー | 内容 | 規則 |
|---|---|---|
| `ending_reveal` | 結末・種明かしの意味(1文)。語り手の総括など出来事でない結末もここ | `source_quote`(原作最終段からの逐語引用)必須(S03)。`withhold_until_end`(結末前に匂わせない範囲)を**対で必須**(M02) |
| `withhold_until_end` | 結末前に示唆・説明してはいけない内容 | `ending_reveal`と同じブロックで提示(§3-3)。例『開いた窓』: 少女の話が作り話だと分かる説明 |
| `setups_and_payoffs` | 伏線→回収の対 | **欠けると結末が成立しないものだけ**(M03)。例: 窓・白いコート・歌・スパニエル→人影の場面 |
| `key_roles` | 物語上必須の人物の役割・動機。各`keep_name: true|false` | §4。`keep_name=true`人物は作品固有名を維持 |
| `key_causality` | 壊してはいけない因果 | 例: 少女の作り話→客の逃走→犬の作り話 |
| `free_to_cut` | 省略・圧縮してよいもの(明示) | 必須(④の自由の明示、M03) |
任意で`tone`1項目可(Opus)。題名の意味・枠物語は`setups_and_payoffs`/`ending_reveal`で表現する(古典で落ちやすい要素への対応、Opus論点2)。essentialsを持たないSeedは完全に従来動作(後方互換、§5)。

### 3-2 抽出漏れの検出(Seed記入規則・S03)
`ending_reveal.source_quote`は**原作最終段から逐語で引くことを必須**とする。Seed承認時にFableが原作最終段落(`seed/primary_text_excerpt.md`末尾)と照合する(手順化)。これはSeedデータの記入規則であり、本文Validatorではない(③に反しない)。

### 3-3 Promptの書き方(M02)
- `[Must-keep -- story essentials]`ブロックを編集方針ブロックの直後に挿入。**結末前の示唆禁止と最終の種明かし必須を同じブロックに併記**する: 「Do not hint at or explain the reveal before the ending. The final reveal itself is required: keep it as the final line, in your own words if you like, but the idea must be clearly conveyed.」(文言案、Trialで確定)。
- `conversion_plan`の「最後の行の後に説明を足すな」は**原作自身の最終文を除外する旨を明記**(今回の矛盾の直接修正)。Seed作成手順にも反映。
- `free_to_cut`は「Everything else may be shortened or reshaped.」相当。

### 3-4 Std調整Promptとの関係(M05)
`STD_PROMPT_TAIL`の「Do not add new explanations…」(`er062_family_z_writer_01.py:158`)と「Do not add … a closing summary」(L165)は、語り手の最終文を削る誘因。essentials行に**「the final reveal line is part of the story, not a summary or a new explanation」**を明示し、禁止の対象外であることを示す。A2化で語が平易語へ置換されることは許容(意味維持が要件)。

### 3-5 全段引継ぎ(実装設計)
- `build_r0_prompt`(L362)・`build_revise_prompt`(L382)・`build_std_prompt`(L391)に**essentials文字列引数**を追加(未指定=従来出力)。
- Seedから決定論的に1文字列を作り(`build_essentials_block(seed)`のような純関数)、全段へ**同じものを渡す**。R1/R2へSeed全文は渡さない(アンカリングによる自由度低下を避ける)。
- provenanceに当該文字列のshaを記録。
- 変更は**DEV/Trial経路のみ**(承認前)。Production既定動作にしない(§5)。

### 3-6 自己チェック不採用(M06)
同一呼出内で「essentialsを満たしたか」を出力させる自己チェックは**採らない**。実効性が低く、チェック文が本文=TTS原稿に混入するリスクがある。

## 4. 区分B(固有名詞)との1セット化(M04・S10)
承認済み区分B(UDR #160、APPROVED_FOR_PRODUCTION未配線)の配線方式をここに統合する。
### 4-1 keep_name上書き
`key_roles.keep_name=true`の人物がある場合のみ、次の**三重の硬い制約**を上書きする文言に差し替える。
| 箇所 | 現行 | 上書き |
|---|---|---|
| R0 `R0_BLOCK_COMMON` | L94 「Only the main character … may be given a personal name」 | 「…ただし`keep_name`の人物はoriginal nameを維持」 |
| `REVISE_USER_TMPL` | L142 「only {main_character} may have a personal name」 | 同上(R1/R2でもkeep_name人物を消さない) |
| Seed `conversion_plan` | `seed.json:18`「Framton Nuttel as the only person with a personal name」 | Seed記入規則で「only X」を書かない/`keep_name`人物を併記 |
作品固有名は**共通Promptに入れない**(Seedの`key_roles`に置く=作品個別指定の置き場)。現状だとR0でVeraが残ってもR1/R2が消す(三重制約)。**Trial(§9)では名前ルール配線とessentialsを1セットで変更・検証する**。
### 4-2 forbidden_names(S10)
`STORY_LINT_CONFIG["the_open_window"].forbidden_names`(`er062_family_z_structure_01.py:808`)にはカタカナ`ヴェラ`のみがあり(英語`Vera`は無い)、Std(日本語Preview/Comment)だけblocking・Adv(英語)素通りの非対称がある(`romance at short notice`は同:812)。区分B配線の一部として、**`keep_name=true`人物を`forbidden_names`から外す**(作品別config値の変更。共通Promptへの作品名埋め込みなし)。承認済みルールの帰結であり、新たなユーザー判断は不要(Fableが記録して実施、Trial/配線時)。01Bの評価では「共通ルールのみ」アームと「keep_name指定」アームを分けて報告する。01B Trial結果: 共通のみ未達の原因=SeedにVera不在(OPEN-464)。

## 5. 隔離・Production安全性(11-7)
- essentialsが無いSeedではPromptが**byte同一**であることをtestで保証。**Melos(Production)不変**。test計画(API 0円): (a)essentials無しSeedで`build_r0_prompt`/`build_revise_prompt`/`build_std_prompt`の出力が現行とbyte一致(Melos Seedで比較)、(b)essentials有りSeedでのみブロックが挿入、(c)`keep_name`無しなら名前文言も従来どおり、(d)Production経路でessentialsを自動読込しない(DEV/Trial関数からのみ)。
- 承認前はDEV/Trial経路のみ。単一flag読取関数が必要な場合は11-7の5条件を満たす(現時点では新コード経路はTrial用runnerに閉じ、Production関数は無変更とする方針)。
- 未承認Promptを既定ONにしない。VALIDATEDでもProduction採用は別途ユーザー判断。

## 6. Fable CP(人手確認)の強化
### 6-1 項目別の引用必須(旧観点4型の曖昧さの排除)
essentials各項目に**「本文の該当引用」を必須欄**とし、チェックリストをessentialsから機械的に作る。観点4は「結末前に示唆が無い」に加え「**種明かし自体が最終に在る**」を要求する書き方に改める。
### 6-2 Seed承認時
FableがessentialsをSeed原作(最終段含む、§3-2)と照合(1回)。
### 6-3 処置規則(M01)
**essentialsに未充足が1件でもあれば、CP不合格とし、TTS前に修正する**(Writer再実行または決定論的パッチ)。所見を記録して先へ進むことを禁じる。10-21のCP所見(a)を処置せずTTSへ進んだ欠陥(ROOT_CAUSE_02 §2)の再発防止。
### 6-4 透明性(M07・③への適合をユーザー自身が確認できる形)
ユーザー資料に明記する: 「Fable(AI)による意味確認であり、**既存CPの細分化**。自動判定・retry・API呼出・新工程は無い」。

## 7. 費用
追加API呼出/記事=0。Must-keepブロック約250tok×4段≒入力約1,000tok=約0.3円。Opus評価:0.3〜1.0円は妥当(実際は下限側)。Text工程17.76円に対し+2〜6%以下。自己チェック不採用のため出力増なし。

## 8. 再発時のエスカレーション(S04)
修正版B適用後、**CP到達時点でessentials未充足が1件出たら**、原因分析のうえC案(軽量事後確認)の要否をユーザーに提示する(旧案「2作品連続」は緩すぎるため変更)。C案はいずれにせよユーザー承認事項。Dは10-12③で既判断(提案しない)。

## 9. Trial計画(U1・Offline、DEV Prompt override)
| アーム | 内容 | 回数 | 概算 |
|---|---|---|---|
| T1「Seed修正のみ」 | `conversion_plan`矛盾修正(最終文除外明記)とSeed `seed_elements[5]`を本文由来で記述。Prompt原則は不変 | R0×3 | 約6.5円 |
| T2「修正版B」 | essentials+keep_name上書き+Std文言(§3〜4) | R0×3 | 約6.7円 |
| T3 修正版B全段 | R0→R1→R2→Std調整 | ×2 | 約35円 |
| 共用 | 固有名詞keep_nameアーム(01B)と共用 | — | — |
合計: Opus概算約40円(積算上限約50円)、7-7の300円以下・日次1,000円内。モデルは本番Writerと同じ(gpt-6.1-sol等、最新世代)。対象=『開いた窓』Seed(`er026_output/family_z_production_e2e_01/the_open_window/seed/seed.json`)。Melosはessentials無しでbyte同一をtestで確認(API 0円)。
評価(本文のみ): ①`Romance at short notice`相当の最終種明かしが最終に在るか(意味。逐語不要)②結末前の先回り示唆が無いか③Vera維持・他の名前が増えないか④Std/Adv対応・段落数・語数⑤R1/R2で消えていないか。
成功=**VALIDATED**(採用ではない)。T1で十分ならPrompt原則変更は不要(その場合はSeed記入規則の改訂のみ)。**Production採用は別途ユーザー判断**。Trial前に新規LLM呼出が最終的に増えない設計であることを確認済み。

## 10. ユーザー判断(判断候補。ラベルはFableが付与)
| ID | 内容 | 区分 |
|---|---|---|
| **U1** | 修正版BのOffline Trial承認(T1/T2/T3、約40円、keep_nameアーム共用、成功=VALIDATED、採用は別途) | D 真に新しい判断(未承認Trial範囲) |
| **U2** | 『開いた窓』完成音声修正の保留解除と実施時期(推奨=OPEN-462配線確定直後)。OPEN_WINDOW_FIX_PLAN_02 | D(ユーザー原文§7の保留の解除) |
再質問しない事項: 境界定義(A既判断、USER.md §4)・反証Trial要否(U1に吸収)・Vera補完の有無・forbidden_names修正・Std最終文文言(Fable決定)・C/D。
