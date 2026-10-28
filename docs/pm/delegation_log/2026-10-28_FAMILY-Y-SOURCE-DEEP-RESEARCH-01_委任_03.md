# FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_03 委任文(Fable→Sonnet、本文逐語。2026-10-28)

管理ID FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_03「追加情報源(規約が明確な公的意見源)の確認→5テーマ確定→情報源レジストリ正式版→SSOT反映」。前提(全て先に読む): `docs/pm/delegation_log/2026-10-28_FAMILY-Y-SOURCE-DEEP-RESEARCH-01_USER_02.md`(ユーザー原文)、`docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/`の `TERMS_REVIEW_01.md`(02A規約判定)、`THEME_SHORTLIST_01.md`・`KOMACHI_IMPACT_CHECK_01.md`・`SOURCE_REGISTRY_DRAFT_01.md`(02B)、01A/01Bの各文書。並行worker: Z『藪の中』委任_02(SSOT・ACTIVE_TASKを編集する可能性あり=直前再Read・最小Edit)。
Fable判断(委任_02A/02Bの判断候補): 規約面で使える主材料がガルちゃん・ママスタ(条件付き)に偏るため、**規約が明文で商用・二次利用を許可する公的意見源**を追加確認してから5件を確定する。運営への書面照会(ガルちゃん・ママスタ・YC/HN・SE)とGuardian商用鍵はユーザー判断(D)として提示のみ。小町影響の対応=A(記録)+B(再実行凍結を文書・OPENで明示。既存成果物・theme_packageファイルは変更しない)、C(限定共有ページ非公開化)はユーザー判断、D/Eは提案のみ。知恵袋38件依存の宅配テーマも同じ扱い(記録+凍結提案)。
**ファイル範囲**: `docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/`配下(新規: `PUBLIC_SOURCES_CHECK_01.md`、`THEME_FINAL_01.md`、`SOURCE_REGISTRY_01.md`、`terms_evidence/`追加、`sources_public/`、`BUDGET_LOG_03.md`、`stop_check_03.json`)、SSOT(下記)、`docs/pm/ACTIVE_TASK.md`、`docs/pm/RESULT_PACKET_FYDR3.md`、`docs/pm/delegation_log/2026-10-28_FAMILY-Y-SOURCE-DEEP-RESEARCH-01_委任_03.md`(本文逐語)。Production code・Prompt・既存成果物(小町/知恵袋由来を含む)は変更禁止。LLM不使用、API 0。小町・Reddit・知恵袋(robots禁止)・増田(robots禁止)・5ch・Mumsnet・Guardianの新規取得禁止。Family A/B/C不可。
開始時 `.venv\Scripts\python.exe tools/stop_scope_check_01.py --managed-id FAMILY-Y-SOURCE-DEEP-RESEARCH-01 --run-dir docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01 --out docs/research/FAMILY-Y-SOURCE-DEEP-RESEARCH-01/stop_check_03.json`(rc=3で停止)。

## 1. 追加情報源の確認 `PUBLIC_SOURCES_CHECK_01.md`(02Aと同じ項目・4区分で判定、条文逐語+URL+確認日)
候補: (a)e-Govパブリック・コメント「結果公示」の提出意見(意見の概要・理由が公開される。利用規約=政府標準利用規約(第2.0版)/CC BY 4.0互換の明記を確認。個人提出者の意見は匿名化されているか、個人情報の扱いも確認)。テーマ例: 第3号被保険者・年収の壁・配偶者控除、高齢者雇用・定年、介護保険、こども誰でも通園、選択的夫婦別姓、ライドシェア、働き方(残業規制)等=02Bの候補(3号年金・定年後・親の仕送り[介護]・転勤[働き方])と重なる領域を優先。(b)各府省の審議会・意見募集結果、こども家庭庁・厚労省の「国民の声」、自治体の市民意見(政府標準利用規約準拠を確認できるもの)。(c)国民生活センター相談事例(規約確認)。各候補で**実際の意見本文を取得**し(1〜3件/テーマ、URL・公示日)、個人の生活経験・感情・利害が読めるか、3視点が揃うかを評価(公的意見は制度論に寄りやすい点を正直に評価)。
## 2. 5テーマ確定 `THEME_FINAL_01.md`
02Bの上位候補(T1′仕送り/T2′転勤/T11定年後/T12ペットか旅行か/T3田舎/T7 3号年金/T6)を基に、各テーマで「条件付き利用可能」以上の情報源**のみ**を根拠に、可能な限り2サイト以上(ガルちゃん+ママスタ、+公的意見源)で3視点を裏取り(ママスタはカテゴリ一覧からサイト内で探索・本文取得、Crawl-Delay遵守)。ユーザー§5Bの表(テーマ/国内・海外/情報源[サイト+実投稿URL]/実在する意見[確認済み]/3 Voice候補[【確認】事実と【構成案】を区別]/面白さ/利用規約[規約URL・確認日・判定根拠、採用全情報源と対応付け]/評価/推奨順位と理由)で、国内候補・海外候補を分けて提示。海外は現時点で採用可能な情報源がない旨を明記(保留理由付き)。**規約未確認・利用不可の情報源を根拠に混ぜない。5件に届かなければ届いた件数と不足理由を正直に書く**(ガルちゃん単一依存の件数も明記)。最推奨テーマ1件と理由、残るリスク(規約の不確実性=AI入力の明文なし等)。
## 3. 情報源レジストリ正式版 `SOURCE_REGISTRY_01.md`(02B草案+02A判定+§1を統合。§2の10項目、国内/海外分離、区分=ユーザー決定除外/規約上の禁止/未確認/条件付き/アクセス不能/低優先度を混同しない。「登録≠Production継続利用承認」を冒頭に明記。今後の制作工程からの参照方法(FLOW_DESIGN_02 ①収集、OPERATIONS_01等の該当箇所に1行の参照を追記=編集可、内容変更はしない)。
## 4. SSOT反映(追記のみ、直前再Read)
- `CURRENT_SPEC.md` Family Y節(Grep「Family Y」の情報収集/Research該当箇所): 「2026-10-28ユーザー決定: ①発言小町=素材源から除外(ライセンス確認まで)、②Reddit=自動収集対象外・API申請見送り、③情報源候補は`SOURCE_REGISTRY_01.md`に登録(登録≠継続利用承認。利用は条件付き判定の条件遵守と、新収集方式のユーザー承認が前提)」2〜4行。
- `DECISION_LOG.md`末尾1件(①②③、規約判定の要点[無条件利用可0、条件付き=ガルちゃん・ママスタ(+公的意見源の判定)]、5テーマ確定状況、小町影響=記録+再実行凍結、Fable判断)。
- `OPEN_ITEMS.md`: 新規OPEN 3件=(a)Family Y情報源レジストリ運用(条件付きサイトの運用規則は新収集方式=ユーザー承認待ち、書面照会はUDR)、(b)小町・知恵袋由来素材の影響(宅配テーマpackageの再実行凍結提案、限定共有ページ4件の扱い=ユーザー判断、D/E案)、(c)海外情報源の保留(HN書面確認・Guardian商用鍵)。
- `docs/pm/USER_DECISION_REGISTER_01.md`: 判断済み=①②③(2026-10-28)。新規UDR=(i)運営への書面照会(ガルちゃん・ママスタ・YC/HN・SE)の実施可否 (ii)限定共有ページ4件(小町由来V3入り)の非公開化可否 (iii)次回制作テーマの選定(5件提示後)。前回の①②は判断済みへ更新。
- `docs/pm/ACTIVE_TASK.md`: 本管理IDの行を追加/更新(Status=USER_DECISION_REQUIRED[テーマ選定・書面照会・ページ非公開化])。
- `docs/pm/RESULT_PACKET_FYDR3.md`(≤20行: 追加情報源判定、確定テーマ件数と各テーマの根拠サイト・規約判定、未達理由、SSOT箇所、判断候補、判定整合行、4行)。
## 5. Git
`git diff --cached --name-only`空確認→自分のファイルのみ明示`git add … && git commit -m "FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_03: 公的意見源の規約確認+5テーマ確定+情報源レジストリ正式版+SSOT反映(API 0)"`を1コマンド(段階commit可)、`git add -A`禁止、他workerファイル不可。`git push origin HEAD:main`(FFのみ、拒否時fetch後再試行、force禁止)。hand-back: 追加情報源の判定、確定テーマ(件数・各テーマ1行: 問い+根拠サイト+規約判定)、最推奨、未達理由、SSOT箇所、commit sha、判断候補。
