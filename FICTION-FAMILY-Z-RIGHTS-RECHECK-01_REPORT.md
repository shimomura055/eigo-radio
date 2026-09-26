# FICTION-FAMILY-Z-RIGHTS-RECHECK-01 REPORT

管理ID: `FICTION-FAMILY-Z-RIGHTS-RECHECK-01`
性質: 確認調査(read-only)。SSOT・コード・Story本文は一切変更していない。
API課金: ¥0(公開資料のHTTP GETなし、既存artifact/SSOTのRead/Grepのみ)。
走れメロスの差し替えは行っていない。判断・推奨はしない(事実の提示のみ)。

---

## §0 要約

- 走れメロスは、日本では1999-01-01からPD(著者没後50年、2018年70年化は
  非遡及)。米国ではURAA(1996-01-01発効)により著作権が回復し、
  発行日(1940年)から95年=2035年末まで保護される可能性が高い
  (2036年PD)、という分析が既に`docs/pm/recon_family_z_production_e2e_01.md`
  (commit `5284391b`、2026-09-26)にあり、本調査もこれを裏付ける追加事実を
  発見した(§1)。
- 過去Trial(`FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02`)は、Gate2
  「権利状態が利用目的上問題ない」を「ソース自身の明示的なPD/CC0表示」で
  判定する運用にしており、Aozora(青空文庫)は日本の著作権情報のみを表示する
  ため、走れメロスの判定は日本法のみで完結し、米国法(URAA)は最初から
  検討対象に入らなかった(§2)。
- 「日本法+米国法双方でPD」という条件は、Trial-02の**同じ評価回**の中で、
  Helen Keller候補(米国PDだが日本は著者没年1968のため未PD)をFableが
  ブラインド評価で発見したことを契機に、Fableが将来条件として提案し
  (§10③「今後の権利確認は『日本法(没後70年)と米国法の両方でPD』を条件に
  する」)、その直後の§11①でユーザー判断事項として明示され、同日
  (2026-09-26)ユーザーが`FICTION-FAMILY-Z-PRODUCTION-E2E-01`のSeed必須条件
  として確定した(`DECISION_LOG.md` 9597行、`CURRENT_SPEC.md` 1105-1109行)。
  **走れメロスはこの同じ評価回(§10④)でFableが著名作としての扱いのみ論じ、
  米国URAAの観点では再チェックされなかった**(§3)。
- 「なぜ米国も必要か」という理由そのものの記載は、Fableのブラインド評価
  コメント中の「eigo-radioは日本で提供するサービスであり」という一文
  (これは主に「なぜ日本法が必要か」の理由付けで、米国法についての理由
  説明ではない)以外に見当たらない。配信基盤(GitHub Pages)や対象国を
  明示的に理由として挙げた記述はSSOT中に見つからなかった(§3、§4)。

---

## §1 走れメロス rights表

| 法域 | 発行/没年等 | 適用ルール | 結論 |
|---|---|---|---|
| 日本 | 初出1940年(新潮)、太宰治没年1948-06-13 | 旧著作権法: 著者没後50年保護(1970年法改正で50年化)。2018年末TPP11整備法による70年化は**非遡及**(既に切れていた作品はそのままPD) | 没後50年=1998年末で保護満了、**1999-01-01からPD確定** |
| 米国 | 発行1940年(1931年以降・1978年以前) | URAA(Uruguay Round Agreements Act、1996-01-01発効)、17 U.S.C. §104A。「1996年1月1日時点で本国(source country)において著作権が消滅していない外国作品」の米国著作権を回復する | 1996-01-01時点で日本において保護期間中(没後50年=1998年末までの残り約3年)だったため回復し、**発行日から95年=2035年末まで保護の可能性が高い(2036-01-01にPD化の可能性が高い)** |

出典(いずれも2026-09-26確認、HTTP 200、`docs/pm/recon_family_z_production_e2e_01.md`
1-1節に既記載):
- 初出年: 日本語版Wikipedia「走れメロス」(https://ja.wikipedia.org/wiki/走れメロス)
  のカテゴリタグ「1940年の小説」「新潮掲載の小説」。
- 没年: Aozora Bunko図書カード(https://www.aozora.gr.jp/cards/000035/card1567.html)、
  逐語「生年：1909-06-19 没年： 1948-06-13」。
- 日本の保護期間・非遡及: English Wikipedia "Copyright law of Japan"
  (https://en.wikipedia.org/wiki/Copyright_law_of_Japan)、逐語
  "Law changes promulgated in 1970 extended the duration to 50 years"、
  および "This new term was not applied retroactively; works that had
  entered the public domain between 1999 and 29 December 2018 (inclusive)
  due to expiration remained in the public domain."
- 米国URAA該当行: Cornell University Library "Copyright Term and the
  Public Domain in the United States"チャート
  (https://copyright.cornell.edu/publicdomain、ミラー
  https://guides.library.cornell.edu/copyright/publicdomain)、逐語(表内
  セル抜粋)「1931 through 1977 / Solely published abroad, without
  compliance with US formalities or republication in the US, and not in
  the public domain in its home country as of 1 January 1996 (but see
  special cases) / 95 years after publication date」。

**この判定は事実の提示であり、法的最終判断ではない**(著作権法解釈は
弁護士確認が望ましい論点であり、既に`docs/pm/recon_family_z_production_e2e_01.md`
§1-1末尾および`OPEN_ITEMS.md` OPEN-185がこの留保を明記している)。

---

## §2 過去Trialの見落とし原因

### 2-1. Gateの定義自体(逐語)

`FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02_REPORT.md` §2(25-31行、逐語):

> **必須Gate(1つでも欠ければ除外)**:
> 1. 元作品・一次内容を実際に確認可能 -- 本Trialでは**直接HTTP GETで一次
>    テキストを実際に取得し、URL・取得日時・冒頭数行(および可能な場合は
>    結末部)の引用で証跡化**することを必須とした。web_searchの要約のみで
>    「確認できた」とはみなさない。
> 2. 権利状態が利用目的上問題ない -- ソース自身の明示的なPD/CC0表示。
> 3. 限られた尺(A2、280〜420語)へ圧縮しても中心Storyを保持可能。

**Gate2の定義自体は「日本+米国双方」を明示的に要求していない。**
「ソース自身の明示的なPD/CC0表示」を判定基準とする運用だった。

### 2-2. 実際の判定文(逐語)

`candidates_evaluation.md` 44行目(走れメロスの行、逐語、権利列):

> Aozora公開・没年1948(著作権切れ)

同じ表内、Gutenberg由来候補(例: The Bet、52行目)の権利列(逐語):

> Public domain in the USA(Gutenberg #55283)

**見落とし箇所の特定**: Aozora(青空文庫)は日本の著作権法に基づく著者没年
のみを表示するソースであり、「ソース自身の明示的なPD/CC0表示」という
Gate2の運用定義をAozora由来候補にそのまま適用すると、判定は構造的に
日本法のみで完結する(Aozoraのページ自体が米国法の判定を一切表示しない
ため)。一方、Gutenberg由来候補はサイト自身が"Public domain in the USA"と
明示するため、Gate2の同じ運用定義を適用しても結果的に米国法の言及が
表に残る。**Gate2の文言自体が「日本+米国双方」を要求していたのに判定者が
見落としたのではなく、Gate2の運用定義(ソース自身の表示に依拠)が、
ソースの種類(Aozora=日本国内法基準の表示/Gutenberg=米国基準の表示)に
よって結果的に片方の法域しかカバーしない設計になっていた**、という
事実が本調査で確認できた。

### 2-3. 同じ評価回内での発見と、走れメロスへの不適用(逐語)

同REPORT §10(214-236行)は「Fable評価(ブラインド)」節であり、(3)で
Helen Keller候補について次のように記録している(228-234行、逐語):

> **権利の訂正(Fable)**: Helen Keller『The Story of My Life』は1903年刊で
> 米国ではPublic Domainだが、著者没年1968年のため**日本の著作権(没後70年→
> 2038年まで)では保護期間内**。eigo-radioは日本で提供するサービスであり、
> rights_check.mdの『well past copyright term』は米国基準のみで誤り。Story B
> 『The Word in My Hand』は必須Gate2(権利)FAILとして候補から除外し、本
> Trialでは『実話系でも面白い素材を選べる』ことの例証としてのみ扱う。今後の
> 権利確認は『日本法(没後70年)と米国法の両方でPD』を条件にする。

**この直後**、同REPORT §10(4)(235-236行、逐語)は走れメロスについて
次のように述べるのみで、米国URAAの観点からの再チェックは行っていない:

> 『走れメロス』は日本の学習者に極めて有名だが、方針(1)『忠実な再話も
> 許容』に従えば問題ない。ただし著名作の扱い(前回1-2)の判断次第。

**特定した見落とし**: Helen Kellerのケースで「片方の法域(日本)のみで
判定して見落とした」ことをまさに発見・訂正した**その同じ評価回・同じ
Fableコメント内**で、走れメロス(逆方向のケース: 日本はPD確定・米国が
未確定)については米国URAAの観点からの再判定が行われず、「著名作の扱い」
という別論点のみが論じられた。すなわち、Keller候補の教訓(片方の法域だけ
では不十分)が、直後の走れメロス評価には適用されなかった、という事実が
本調査で確認できる。

### 2-4. §11(ユーザー判断事項化)

同REPORT §11①(243-244行、逐語):

> ①権利確認条件を『日本法+米国法の両方でPD(著者没後70年以上、または明確な
> CC0等)』に固定するか(Fable推奨: 固定)。

この時点(Trial-02完了時)では、走れメロス自体の米国status再判定は
行われないまま、「今後の条件」としてのみユーザー判断事項化された。

---

## §3 「米国PD必須」の根拠所在

### 3-1. 初出箇所・日付・決定主体

- **初出提案**: `FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02_REPORT.md`
  §10(3)、Fableのブラインド評価コメント(commit `d2b6f744`/`1b9fa867`、
  いずれも2026-09-26)。逐語は§2-3に引用済み(「今後の権利確認は『日本法
  [没後70年]と米国法の両方でPD』を条件にする」)。**Fableが提案した**。
- **ユーザー判断事項化**: 同REPORT §11①(同日、Fable)。
- **ユーザー確定**: `DECISION_LOG.md` 9597行
  (`FICTION-FAMILY-Z-PRODUCTION-E2E-01: Family Z(Fiction)ユーザー確定
  ルールのSSOT記録`、commit `0e462796`、2026-09-26)、逐語(該当部抜粋):

  > (3) Seed必須条件(4項目): Original/primary textを直接確認できる/**日本法+
  > 米国法双方で利用可能**/短編化しても中心Storyを保持できる/Story品質基準
  > 4項目中原則3以上。

  同内容は`CURRENT_SPEC.md` 1105-1109行にも「ユーザーが逐語で確定した
  Production仕様」として反映されている(1080-1087行のStatus注記参照)。

**結論**: 「米国PDも必要」という条件は、**ユーザーが独自に最初に指示した
ものではなく、Fableが(Helen Kellerケースの発見を機に)将来条件として
提案し、それをユーザーが判断事項として提示されたうえで確定した**、という
経路が、上記の逐語記録から確認できる。ユーザー自身の元々の転記・指示文
(この確認より前の時点)がこれとは別に存在するかどうかは、本調査で参照した
範囲のSSOT・REPORT内には見当たらなかった。

### 3-2. 記載されている理由

Fableのコメント本文中で理由として書かれているのは、Helen Kellerの文脈での
以下の一文のみ(§2-3で引用済み、再掲):

> eigo-radioは日本で提供するサービスであり、rights_check.mdの『well past
> copyright term』は米国基準のみで誤り。

この一文は文脈上、「**なぜ日本法のチェックが必要か**」(eigo-radioが
日本向けサービスだから)の理由付けであり、その裏返しとして「**なぜ米国法
まで必要か**」という問い自体への理由説明にはなっていない(米国のみで
PDならば日本向けサービスとしては日本法チェックのみで足りるはずだが、
実際に確定した条件は「日本法+米国法の**両方**」であり、米国法を追加で
要求する理由は本調査で確認した範囲の逐語には明記されていない)。

`OPEN_ITEMS.md` OPEN-185・`CURRENT_SPEC.md` 1143-1154行(Phase 0結果の
転記)・`docs/pm/recon_family_z_production_e2e_01.md`のいずれにも、
「米国が必要な理由」自体(米国での配信・米国ユーザー・米国platform規約等)
を明示した記述は見当たらなかった。**根拠記載なし**(推測で理由を補って
いない)。

---

## §4 配信基盤に関するSSOT記述の有無

`CURRENT_SPEC.md`/`DECISION_LOG.md`/`OPEN_ITEMS.md`/`docs/pm/PM_GOVERNANCE.md`を
「hosting」「配信」「distribution」「YouTube」「Podcast」「プラットフォーム」で
Grepした結果、Fiction/Family Zの権利要件と関連付けた配信基盤の記述は
見当たらなかった。見つかった配信基盤の記述は以下の1件のみで、Family Z
とは無関係(ユーザーテスト用Web表示の話):

`CURRENT_SPEC.md` 1462-1503行「ユーザーテストWeb表示仕様・配信経路
(2026-09-18新設)」、逐語(1483-1487行):

> **配信経路**: ユーザーテストWeb Hosting=**GitHub Pages**
> (`https://shimomura055.github.io/eigo-radio/`、リポジトリ`main`ブランチ・
> root配信、`.nojekyll`あり)。**GitHub Pagesはユーザー自身の操作により
> 有効化された(ユーザー確認済み事実、2026-09-18、`PM-GOVERNANCE-
> DISTRIBUTION-PATH-PAGES-01`)**。

このGitHub Pages配信経路の記述は「ユーザーテスト」用途としてのみ記載
されており、対象国・米国ユーザー・YouTube/Podcast配信規約等への言及は
見当たらなかった。Family Z(Fiction)の権利要件(§3)とこの配信経路記述を
明示的に結び付けた記述もSSOT中には見当たらなかった。

---

## §5 参照ファイル一覧

- `docs/pm/recon_family_z_production_e2e_01.md`(commit `5284391b`、
  2026-09-26)
- `er018_output/fiction_external_seed_selection_criteria_trial_02/
  candidates_evaluation.md`(44行目、走れメロス権利判定)
- `FICTION-EXTERNAL-SEED-SELECTION-CRITERIA-TRIAL-02_REPORT.md`
  (§2 25-31行[Gate定義]、§10 214-236行[Fableブラインド評価]、§11
  239-251行[ユーザー判断事項化]、commit `d2b6f744`/`1b9fa867`)
- `FICTION-EXTERNAL-STORY-SEED-TRIAL-01_REPORT.md`(Trial-01系譜の参照、
  本調査では詳細クロスチェックはしていない)
- `DECISION_LOG.md` 9597-9601行(`FICTION-FAMILY-Z-PRODUCTION-E2E-01`
  ユーザー確定エントリ、commit `0e462796`)
- `CURRENT_SPEC.md` 1080-1154行(「Family Z(Fiction)」節、Seed必須条件・
  Phase 0結果転記)
- `OPEN_ITEMS.md` 334行(OPEN-185)
- `docs/pm/PM_GOVERNANCE.md`(hosting/配信/米国関連語でGrep、Family Z
  権利要件との関連記述なし)
- 外部公開資料(2026-09-26確認、HTTP 200、いずれも既存recon経由の再確認、
  本調査での新規HTTP GETなし): https://ja.wikipedia.org/wiki/走れメロス 、
  https://www.aozora.gr.jp/cards/000035/card1567.html 、
  https://en.wikipedia.org/wiki/Copyright_law_of_Japan 、
  https://copyright.cornell.edu/publicdomain
