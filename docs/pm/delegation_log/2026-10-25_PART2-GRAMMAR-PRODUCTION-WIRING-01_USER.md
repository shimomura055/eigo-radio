

<pasted_content id="a638">
# Claude Codeへの指示｜Family XYZ共通：Part 2文法解説・Key Phrase／文法Human Review 正式Production Wiring

## 1. ユーザー正式決定

以下の4項目を、**Family X／Y／Z共通仕様として正式採用**する。

| 項目 | 対象Family | Status | 目標 |
|---|---|---|---|
| ① Part 2「Grammar & Sentence Structure」 | X／Y／Z | APPROVED_FOR_PRODUCTION | PRODUCTION_WIRED |
| ② Trial-08構文選定方式 | X／Y／Z | APPROVED_FOR_PRODUCTION | PRODUCTION_WIRED |
| ③ Key Phrase Human Review | X／Y／Z | 承認済み | PRODUCTION_WIRED |
| ④ 文法Human Review | X／Y／Z | 承認済み | PRODUCTION_WIRED |

今回、ユーザーは①②についてもXYZ共通での正式採用を明示的に承認した。

**Family Z限定の実装ではない。X／Y／Zの3 Familyすべてが適用対象である。**

ただし、APPROVED_FOR_PRODUCTIONとPRODUCTION_WIREDを混同しないこと。

## 2. 採用する仕様

### ① Part 2文法・構文解説

Trial-07で検証した文法・構文解説機能を正式採用する。

- 本文中から学習価値のある構文を選定する。
- 本文と逐語一致する英文を引用する。
- 文法・構文の仕組み、通常の語順・表現との比較、意味・ニュアンス・表現効果を解説する。
- 適格な構文がなければ0件を許容する。
- 既存の承認済み品質条件を維持する。

### ② Trial-08構文選定方式

以下の優先順位を正式採用する。

- Tier1：倒置以外の適格な構文
- Tier2：倒置構文
- Tier3：該当なし

Trial-08では倒置の選定割合が4/8から1/8へ低下し、学習価値も維持された。

今回採用するのは、このVALIDATED（限定）の選定方式である。

Tier内順位の追加改善、HIGH判定の安定化ルール、OTHER分類の拡張は今回の承認対象に含めない。

### ③ Key Phrase Human Review

既存のユーザー承認済みFamily XYZ共通仕様に従い、正式Production経路に組み込む。

TOP候補の提示、レビュー操作、選定結果の反映、後続工程への引き渡しについて、承認済み仕様を確認して実装する。

### ④ 文法Human Review

既存のユーザー承認済み仕様に従う。

- AIがTOP1／TOP2を順位付きで提示する。
- HumanはTOP1／TOP2／再選定／省略を選択できる。
- Humanが介入しない場合のTOP1自動採用については、既存の承認済み条件を維持する。
- ただしHuman Review必須の運用と整合させ、未レビューのものを勝手に最終承認扱いしない。

既存仕様に不明点や矛盾がある場合、承認記録を照合して解決する。新たな運用仕様を独断で追加しない。

## 3. 品質改善方針

**今回は現行の承認済み仕様でProduction Wiringを完了させる。**

『走れメロス』で確認された解説の不正確さや、構文選定のばらつきは認識している。

しかし、ユーザーはこれらについて、今後必ず実施するHuman Reviewの結果を使いながら継続的に仕様を改善する方針を決定した。

したがって以下を遵守すること。

1. 既知の品質課題を理由にProduction Wiringを不必要に延期しない。
2. 追加Trialや未承認の品質基準変更を、今回のWiringの前提条件にしない。
3. 既存仕様から逸脱する明確な不具合は、委任範囲内で修正する。
4. Human Reviewの修正内容・理由を今後の改善に利用できる形で記録する。
5. 新しい選定規則や品質基準の正式採用は、別途ユーザー判断を必要とする。

Human Reviewによる品質確保を前提としつつ、将来は人間のレビュー負担が減る方向で改善する。

## 4. Family別の実装方針

### Family X

①〜④すべてを正式Production経路へ配線する。

Standard／Advancedなど、既存Productionで対象となるレベルについて、正式初回経路・後続経路を含めて検証する。

目標：①〜④すべてPRODUCTION_WIRED。

### Family Z

①〜④すべてを正式Production経路へ配線する。

Trial-07／08で利用したFamily Zの実績を活用するが、Trial専用コードが動いたことだけを正式Production配線の証拠にしない。

対象レベル・正式初回経路・後続経路を確認する。

目標：①〜④すべてPRODUCTION_WIRED。

### Family Y

①〜④すべてを正式採用対象とする。

ただし、Family YはProduction経路の整備が進行中であるため、まず現在の実装状況と正式経路の有無を確認する。

- 既存基盤に安全に配線できる部分は、X／Zと並行して進める。
- 今回の承認範囲内で正式Production Wiringまで到達できる部分は完了させる。
- 未完成のProduction経路を新規に完成させる必要がある場合、今回の承認範囲を超える開発は無断で行わない。
- 未配線部分は理由・依存関係・解消条件をOPEN_ITEMSに登録し、後のFamily Y Production化時に必ず適用する。

**Family Yを対象外として放置しない。一方、正式runtime evidenceなしにPRODUCTION_WIREDと判定しない。**

## 5. 並列化・Delivery最小化

今回の4項目は、可能な限り並列化して完成させる。

特に、

- Part 2／Trial-08のProduction実装
- Key Phrase Human Reviewの実装
- 文法Human Reviewの設計・実装
- Family X／Z／Yへの適用準備

を、依存関係・競合に応じて合理的に分割する。

文法Human ReviewはPart 2の選定方式が今回正式決定したため、もう仕様決定待ちを理由に止める必要はない。

既存のHuman Review Phase 0、必要なOpusレビュー、Fable独立評価も活用する。

共通部品は再利用し、Familyごとの重複実装を避ける。

独立作業は同時進行し、競合がある部分のみ順序を設定する。

不要な待機、日付分割、逐次実行、過剰なTrialを禁止する。

## 6. Production Wiring受入条件

各Family・各機能について以下を検証する。

1. 承認済み仕様が正式初回Production経路に存在する。
2. retry／fallback／regeneration／resumeと整合している。
3. Human Reviewの候補提示・操作・確定結果の反映が正しく動く。
4. Human Reviewの結果が後続の解説・音声・組立工程に正しく反映される。
5. 必須Regression／Validator／Integration TestがPASSする。
6. 正式runtimeでの発火証拠を取得する。
7. actual model_id、routing、Prompt等の実動作を確認する。
8. CURRENT_SPEC／DECISION_LOG／OPEN_ITEMSを更新する。
9. 必要なGit commit／pushを完了する。
10. Fableがユーザー承認内容・実装・実動作を独立照合する。

一つでも未確認の項目があれば、その範囲をPRODUCTION_WIREDと判定しない。

未承認のTrial仕様やDEV専用経路へのDangling Referenceも残さない。

## 7. QCD・予算

優先順位は以下のとおり。

**品質（Q）＞Delivery（D）＞量産単価（C）≫開発費用**

- 品質基準はユーザー承認済みのものを維持する。
- 品質を守る範囲で最速完成を目指す。
- 量産単価70円／記事セットを継続的な目標とする。
- Part 2のTrial時の推定増分は約0.41円／セット。Human Reviewを含む最終的な量産費用は別途実測・報告する。
- 開発費は既存個別承認枠と原則1,000円／日（JST）の範囲で管理する。
- 承認済み範囲内の少額費用・不具合修正について、都度ユーザー判断を求めない。

## 8. STOP条件

以下の場合のみ該当作業を停止・報告する。

- ユーザー承認済み仕様との重大な矛盾
- 重大な品質・安全問題
- 新仕様や品質基準変更が必要
- 重要なScope変更
- 承認済み予算上限への抵触
- 自律解決困難なblocker
- Family Yなどで正式Production経路が存在せず、今回の委任範囲では解決できない場合

該当作業を停止しても、独立して進められる他作業は止めない。

## 9. 最終報告・Closeout

4機能×3 Familyについて、以下の形式で結果を報告する。

| 機能 | Family X | Family Y | Family Z |
|---|---|---|---|
| Part 2文法解説 | Status／証拠 | Status／証拠 | Status／証拠 |
| Trial-08選定方式 | Status／証拠 | Status／証拠 | Status／証拠 |
| Key Phrase Human Review | Status／証拠 | Status／証拠 | Status／証拠 |
| 文法Human Review | Status／証拠 | Status／証拠 | Status／証拠 |

併せて、runtime evidence、テスト結果、Human Reviewの動作、QCD実績、SSOT／Git反映状況、残Open Itemを報告する。

特に以下を区別する。

- APPROVED_FOR_PRODUCTION：ユーザー正式採用済み
- PRODUCTION_WIRED：正式経路の実動作まで検証済み
- 未配線：正式採用済みだが、配線・検証が未完了

ユーザー判断待ちや承認済み未配線項目を残したまま、無条件に案件全体を完了扱いしないこと。

---

**最終指示**

①〜④すべてがFamily XYZ共通の正式採用仕様である。

X／Zは全対象機能のPRODUCTION_WIREDを目標とする。Yも可能な限り同時配線を進め、未完了部分は明確に追跡する。

今後の文法解説の品質改善はHuman Reviewの実績を活用するため、未承認の追加Trialを実装前に挟まない。

**承認済み品質を守りながら並列化を最大化し、今回の4項目を最速で完成させること。**
</pasted_content id="a638">
