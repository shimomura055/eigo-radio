## 管理ID

SLOT-23-CONSUMER-DESIGN-01 委任_02(ユーザー正式決定(2026-10-27「学習項目①②③の表示仕様正式採用・X/Y/Z Production Wiring」、APPROVED_FOR_PRODUCTION、到達目標PRODUCTION_WIRED、全6経路)を受けた設計更新=DESIGN_02+Opus条件Aレビュー依頼文+実装分割計画。read-only(Productionコード編集禁止)、API 0)。前提=委任_01(c44853cec)の`CURRENT_CONSUMERS_01/DESIGN_01/COST_01/OPUS_REVIEW_REQUEST_01/USER_DECISION_DRAFT_01.md`。並行Agent: GPG委任_05C(Y evidence run)、X TTS診断(read-only)。あなたの所有=`docs/research/SLOT-23-CONSUMER-DESIGN-01/{DESIGN_02,OPUS_REVIEW_REQUEST_02,IMPL_PLAN_02,COST_02,SPEC_CONFLICT_02}.md`、`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`(ユーザー原文の逐語保存=下記「ユーザー原文」を一字一句そのまま。要約禁止)、`..._DELEGATION_02.md`(+check.json)、`docs/pm/RESULT_PACKET_S23D2.md`(gitignore)。SSOT編集権なし。pathspec付きcommit、`git push origin HEAD:main`。

## ユーザー正式決定の要点(原文は末尾。原文が正)

- 決定① Std②「追加解説」=**C案**: StandardにもAdv Part 1と同様の英語解説全文を表示(Std難易度の英語)。②を③と同じ扱いにしない。旧「Part 1はAdvancedのみ」は②表示に関して変更。矛盾する記述・Validator・表示処理を更新。①KP/文法/他の機能は変更しない。「Standardで②の英語解説が生成・表示されない旧経路を残さない」。
- 決定② 本文ハイライト=B案(二重下線方式): ①太字+二重下線/②太字+通常下線/③通常下線のみ。文字サイズ・色は本文同一、背景マーカー・色分けなし、①②③すべて対象、③は短い日本語訳を確認できる、スマホで区分判別可、本文テキスト・TTS・Chunk・ポーズ不変。照合は候補データの本文表層形・出現位置を優先(`carry over`→`carried over`等)、複数出現=不合格としない(確定情報で特定できればそれを使う)、特定不能はfail-closed+原因調査、重なり等はKCP Gateと整合、過剰制約で制作を止めない。コピー/読み上げに余計な記号を混入しない、開発用Chunkマーカー非混入。
- 決定③ 遡及なし(AI島Std/Advと今後の新規記事のみ。既存公開記事の一括再生成・差替えなし。個別承認は妨げない)。
- 受入条件14(§6)・報告9項目(§8)。

## 実施事項

1. `SPEC_CONFLICT_02.md`: CURRENT_SPEC/DECISION_LOG/OPEN_ITEMS(Grep: `Advancedのみ|Part 1|Vocabulary & Expressions|OPEN-512|OPEN-562|vocab_confirmed|script_block|unconsumed`)・`er119_kp_human_review_01.py:524-530`(Std vocab指定エラー)・`er003_kp_general_explanation_01.py`・各FamilyのPart 1描画/Validator・`er_user_listening_page_common_01.py`(`script_block`、`audience`)・KCP(`er128` G3、`load_verified_items`)・V3フォームpayload/確定レコード(`selection.{key_phrase,extra_explanation,meaning_display}`、`unconsumed[]`)・GPG(Std節=文法のみ→文法+Part 1の配置)を照合し、矛盾箇所(file:line)と更新方針を一覧化。「Std②が生成・表示されない旧経路」を全て列挙。
2. `DESIGN_02.md`(DESIGN_01を置換する正本): (a)Std Part 1=既存Adv Part 1生成工程(`er003`系)をlevel引数化(Prompt難易度調整のみ、項目構成同一=英語表現/本文中の意味/引用文/訳/解説)、入力=確定レコード①+②(Std ①3+②2=5件、Adv同様)、`vocab_confirmed.json`相当のStd生成、品質検査=既存Adv検査を同一適用、retry/fallback/resumeで確定保持(KCP G4相当)。(b)ハイライト: `script_block(highlights=[{kind, source_span, start, end, gloss_short}])`、HTML=①`<strong class="lk1">`(text-decoration: underline double)/②`<strong class="lk2">`(underline)/③`<span class="lk3">`(underline)、font-size/colour継承、background none、記号なし(コピー・読み上げに影響しない)、③の短い日本語訳=本文直下の「英語=訳」リスト(JS不要、スマホ可)+任意で`title`。照合アルゴリズム=候補docの`source_span`/offset優先→確定レコードの表層形→正規化一致(大小/引用符)、複数出現時は候補データの出現位置で特定、特定不能=fail-closed(ISSUE、原因記録)、重なりは①>②>③優先で入れ子禁止=ISSUE、Chunk境界跨ぎは許容(表示のみ、音声不変。DESIGN_01の「跨がない」条件は過剰制約として撤回し理由明記)。(c)X/Y/Z配線点(file:line)と`audience=dev`マーカーとの共存(devマーカーは`<mark>`等と衝突しない挿入順序)。(d)KCP G3拡張の検査項目。(e)Std節の構成順(文法ブロックとの位置)。(f)遡及なし=再ビルド対象はAI島のみ、既存ページはビルド時に確定レコード無→従来描画。(g)既定動作: 確定レコードがある記事で自動有効(承認済み仕様のためflag不要)、確定レコード無=従来どおり。
3. `COST_02.md`: Std Part 1生成費用/記事(実測ベース、Adv ¥0.17相当)、6経路評価費用見込み、量産単価影響。
4. `IMPL_PLAN_02.md`: 並列分割(A: 共通描画+照合+G3拡張+test / B: Std Part 1生成level化+Std検査 / C: X配線+AI島再ビルド / D: Y配線 / E: Z配線 / F: evidence 6経路)、所有ファイル分離、依存、所要時間、受入条件14との対応表、報告9項目の雛形。
5. `OPUS_REVIEW_REQUEST_02.md`: 条件Aレビュー論点(照合の正確性・多重出現・fail-closed境界、Std Part 1のlevel化で既存Adv品質を変えないこと、旧経路撤去漏れ、KCP整合、X/Y/Z差異、既存ページ回帰、費用)。
6. commit: `SLOT-23-CONSUMER-DESIGN-01 委任_02: ユーザー正式決定(Std②=C案/二重下線方式/遡及なし)を反映した設計DESIGN_02・矛盾一覧・実装分割計画・Opus依頼文(read-only、API 0)`、trailer `Delegation: SLOT-23-CONSUMER-DESIGN-01/02`。Secret grep 0件。

## 固定ブロック

従来どおり(E-1/D-1/G-1/F-1)。T-0: 委任文=`...\subagents\agent-*.jsonl`最新・先頭が本管理IDのものをindex 0で逐語抽出(方法は`docs/pm/RESULT_PACKET_SSOT22.md`(0))+check。T-2/T-3: なし。時間見込み: 約1.5h。

## 報告

`RESULT_PACKET_S23D2.md`: (0)T-0・USER原文保存、(1)矛盾一覧要約、(2)設計要点、(3)費用、(4)実装分割、(5)判断候補(ユーザー判断は原則なし。設計上どうしても必要な選択のみ)、(6)必須4行+「判定整合」、commit hash・raw URL。末尾5行要約。

## ユーザー原文(逐語。`docs/pm/delegation_log/2026-10-27_SLOT-23-CONSUMER-DESIGN-01_USER.md`へこの見出し以下を一字一句保存)

# Claude Code指示｜学習項目①②③の表示仕様正式採用・X/Y/Z Production Wiring

## 1. ユーザー正式決定

`SLOT-23-CONSUMER-DESIGN-01`について、以下3点を正式採用します。

**Status：APPROVED_FOR_PRODUCTION**  
**到達目標：PRODUCTION_WIRED**  
**対象：Family X/Y/Z × Standard/Advancedの全6経路**

### 決定① Standardの②「追加解説」

**C案を正式採用。**

StandardにもAdvancedと同様に、②で選定された英語表現について英語解説全文を表示する。

- Standardの学習レベルに合わせた英語で解説する。
- Advancedと同等の学習機能を提供する。
- ②を③「本文意味表示」と同じ扱いにしない。
- Part 1相当の学習コンテンツをStandardにも提供する。
- 既存のAdvanced側の承認済み解説仕様・品質基準を維持する。

旧「Part 1はAdvancedのみ」という制約は、**②追加解説の表示に関して今回の正式決定で変更**されます。

既存仕様と矛盾する記述・Validator・表示処理を確認し、適切に更新すること。

なお、以前から承認済みの①Key Phrase、文法解説、その他の学習機能については、今回の変更を理由に勝手に表示対象や品質基準を変更しないこと。

### 決定② 本文ハイライト

**ユーザーがAI島Standard／Advancedの実際の英文を用いて確認・承認したB案（二重下線方式）を正式採用。**

| 区分 | 正式表示仕様 |
|---|---|
| ① Key Phrase | 太字＋二重下線 |
| ② 追加解説 | 太字＋通常の下線 |
| ③ 本文意味表示 | 通常の下線のみ |

共通条件：

- 文字サイズは本文と同じ。
- 文字色は本文と同じ。
- 背景マーカー・色分けはしない。
- 本文中の①②③すべてを対象とする。
- 日本語訳の表示は選定区分の仕様に従う。
- ③は短い日本語訳を確認できるようにする。
- スマートフォンでも区分の違いが分かるようにする。
- 本文のテキスト自体は変更しない。
- TTS音声、Chunk、ポーズ長は変更しない。

①②③は見た目だけでなく、学習内容の役割も異なるため、既存の選定区分を維持すること。

### 決定③ 過去記事への遡及

**過去に公開済みの記事への一括遡及は行わない。**

- 今回制作中のAI島Standard／Advancedには適用する。
- 今後の新規制作記事へ適用する。
- 既存公開済みの記事を一括再生成・差し替えしない。
- 明示的に別途承認された個別記事の変更は妨げない。

## 2. 既存仕様・先行実装との整合確認

作業開始時に以下を確認する。

- CURRENT_SPEC
- DECISION_LOG
- OPEN_ITEMS
- PM_GOVERNANCE
- `SLOT-23-CONSUMER-DESIGN-01` の設計書
- V3フォームと①②③確定データの保存方式
- 既存Part 1英語解説生成工程
- Standard／Advancedの公開ページ生成処理
- 確定内容保護機能
- 進行中の文法事前生成・文法Top1/Top2選定方式
- 他Familyの共通表示仕様

今回の表示仕様変更によって、既に承認された仕様が暗黙に上書きされないようにする。

特に、**Standardで②の英語解説が生成・表示されない旧経路を残さないこと。**

承認済み共通仕様とFamily固有仕様を区別し、X/Y/Zすべての対象レベルで整合を取る。

## 3. Standardの②英語解説

Standardの②について、次を実現する。

1. ユーザーが確定した②の英語表現・日本語訳をそのまま使用する。
2. Standard向けの適切な難易度で英語解説全文を生成する。
3. 既存のAdvanced Part 1と整合する学習コンテンツとして表示する。
4. ユーザー確定内容を後続工程で変更しない。
5. 生成結果の品質検査を行う。
6. retry／fallback／resume時も選定内容を保持する。

解説の見せ方・項目構成は既存のAdvanced側仕様を原則として踏襲し、Standardに必要な難易度調整のみ行う。

不要な新しい説明方式や独自の品質基準を追加しない。

## 4. 本文ハイライトの実装

選定結果①②③を正式な記事本文表示へ接続する。

**①：太字＋二重下線**  
**②：太字＋通常下線**  
**③：通常下線のみ**

HTML/CSSの実装方法は任せるが、次の受入条件を満たすこと。

- 実ブラウザで二重下線が明確に表示される。
- ①②③の太さ・下線の違いが視覚的に確認できる。
- 文字サイズの不自然な拡大がない。
- スマートフォン・PCで適切に表示される。
- 本文の改行・段落・句読点が変化しない。
- テキストのコピーや通常の読み上げに余計な記号が混入しない。
- 開発専用のChunk境界マーカーを一般ユーザー向け本文に混入させない。

### 英語表現の照合

ハイライト対象は、ユーザーが確定した英語表現と本文中の実際の語形を正確に対応させる。

例：

- `carry over` → `carried over`
- `take a detour` → `taken a detour`
- `look at separately` → `looked at separately`
- `erase` → `erased`

元の候補データにある本文表層形・出現位置などの情報を優先して利用する。

同じ語が本文中に複数回登場した場合も、**単純に「複数出現＝不合格」としないこと。**

既存の確定情報で対象箇所を正確に特定できる場合は、それを使用する。

対象箇所を特定できない場合は、誤った箇所に表示せずfail-closedとし、原因を調査する。

重複・部分一致・表現同士の重なりがある場合は、既存の確定内容保護Gateと整合させる。

過剰な制約によって正常な記事制作が停止しないようにする。

## 5. AI島への適用

対象：

Family X「AIの仮想の島」

- Standard：確定済み①3件・②2件・③5件
- Advanced：確定済み①3件・②2件・③5件
- 文法：両レベルともユーザー判断により0件確定

先に送付された両レベルの選定結果を正本として使用する。

**①②③の再選定、文法の再選定、本文再生成は不要。**

Standardの②について新たに必要となる英語解説は、承認済みの品質基準に従って生成する。

既存の有効な音声・本文・学習コンテンツを再利用する。

新しい表示仕様を反映した完成記事のStandard／Advanced試聴ページを提出する。

音声を変更しない表示修正のみで対応できる箇所は、HTML再ビルドを優先する。

## 6. Production Wiring・受入条件

全6経路について、以下を確認する。

1. 正式初回Production経路に①②③の表示機能が接続されている。
2. Standard／Advancedの②で英語解説全文が生成・表示される。
3. ①②③の表示強度がユーザー承認仕様と一致する。
4. ③の日本語意味表示が正常に機能する。
5. ユーザー確定内容と記事表示が一致する。
6. retry／fallback／regeneration／resumeとの整合がある。
7. DEV／Trial専用経路ではない。
8. 正式runtimeでの発火証拠がある。
9. 必須Regression／Validator／Integration TestがPASSする。
10. actual model_id、routing、Prompt・Style等を確認する。
11. Fable独立受入を完了する。
12. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを更新する。
13. 必要なGit反映を完了する。
14. 未承認の仕様参照・Dangling Referenceがない。

Family別・レベル別にStatusを判定する。

未検証経路をPRODUCTION_WIREDとしない。

## 7. QCD・進行方針

優先順位：**品質 ＞ Delivery ＞ 量産単価 ≫ 開発費用**

- 既存成果を最大限再利用する。
- 独立した実装・検証は並列化する。
- 進行中のV3フォームProduction Wiring、文法仕様変更、確定内容保護の作業と競合しないよう調整する。
- 本文・TTSの不要な再生成を行わない。
- 量産単価70円／記事セットを継続目標とする。
- Standard②の追加費用を必要十分な範囲に抑える。
- 日次開発費1,000円（JST）と個別承認枠を遵守する。
- 承認済み範囲内の不具合は原因究明から修正・検証まで自律的に実施する。
- 重大な品質問題、予算超過、未承認の仕様変更、解消不能なblockerはSTOPして報告する。

新規実装に関するOpus条件Aレビューが必要な場合は、承認済み手順に従う。

必要十分な品質に到達した後、不要な追加Trialを行わない。

## 8. 報告・Closeout

以下の順に報告すること。

1. **AI島Standard／Advancedの完成版URL**
2. ①②③のユーザー確定内容との一致結果
3. Standard②英語解説の内容・品質検査結果
4. 二重下線／通常下線の実ブラウザ表示検証
5. X/Y/Z全6経路のProduction Wiring Status
6. Fable独立受入結果
7. QCD実績
8. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMS／Git反映
9. 残るOpen Item・ユーザー判断事項

**今回の正式採用内容は、Standardの②英語解説、①②③の3段階表示、過去記事への遡及なし、の3点です。**

これらをAI島の完成記事に反映し、Family X/Y/Zの正式Production経路でPRODUCTION_WIREDまで完了させてください。