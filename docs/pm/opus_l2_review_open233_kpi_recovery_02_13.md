# Opus独立レビュー#13(条件A)保存とFable評価: OPEN-233-KPI-RECOVERY-REDESIGN-02

保存日: 2026-10-04(委任_08)。親: OPEN-233-SELF-RECOVERY-TRIAL-01。Production未変更。

## (1) Opusへの依頼(要旨。委任_08の委任文に記載された形式のまま)

[Fableがopus-consultantへ送った依頼。論点1〜7: 1.AG1-strictの安全性・同義語表・負例検証 2.issue名指しの扱いとrep22型残余 3.構造要素delete禁止+書き換え 4.件数一致是正の安全性 5.より単純な方法(guard廃止等) 6.Production整合 7.cost・非決定性。packet: `docs/pm/opus_packet_open233_kpi_recovery_02_03.md`、設計書§14。]

## (2) Opus独立レビュー#13 全文(逐語)

# Opus独立レビュー#13(条件A)OPEN-233-KPI-RECOVERY-REDESIGN-02: Rewrite側Safety guardと処理フロー

## 結論
- **actor_guard是正**: 必要です。AG1-strictの方向は妥当です。ただし「42/42維持」は安全性の根拠として弱く、同義語表の粒度がSafety上の要になります。
- **構造要素のdelete禁止**: 必要です。妥当です。実LLMでの品質とtitle判定の位置ずれは未検証です。
- **件数一致の是正**: 必要です。方向は妥当ですが、実装に安全側へ倒しきれていない箇所が3点あり、要修正です。

## 12観点の評価

**1. 必要性**
- 3件ともKPI緩和ではなく実装欠陥です。是正は必要です。
- actor_guardの根本原因(英語の主体語を日本語Ledgerへ英語のまま部分一致)は、コードL581-586で確認しました。妥当です。

**2. より単純にできるか**
- AG1は決定論・¥0で十分単純です。AG2/AG3は不要です。
- 件数一致の是正は、下記の「全項目resolved ∧ 全index網羅」にすれば、さらに単純かつ安全になります。

**3. 既存処理・データの利用**
- `related_fact_id`(Stage 1で取得済み)とLedger全文の再利用は適切です。
- headline専用の再生成経路を作らず、既存ladderへ統合した判断に同意します。

**4. 情報の喪失・再探索**
- guardは現状、取得済みの関連fact・Checker issueを見ていません。前段の情報を捨てている状態で、AG1はこれを是正します。

**5. 不要なLLM処理**
- AG1と件数一致の是正は追加call 0です(件数一致の是正はむしろcallを減らします)。
- 構造要素の書き換えは、旧`0_delete`(0 call)が最大3 call(E1/③/④)になります。ただし該当は1文記事・title範囲のみで、件数は小さいです。

**6. 非決定性**: AG1・件数一致の是正では増えません。AG2/AG3は増えます(不採用が妥当)。

**7. Human Review**: rep28の3件中、2件(guard)と1件(title)は理論上解消します。rep22型の残余は後述します。

**8. 不要Rewrite**: 増えません。

**9. コスト**: 純減の見込みです(neg3の再確認call ¥0.2〜0.37/回が消えます)。

**10. retry/fallbackとの矛盾**: 構造要素の却下は既存の枯渇経路に乗っており、新経路はありません。矛盾なしです。

**11. Failure時に安全側へ倒れるか**: 件数一致の実装に穴が3点あります(論点4)。AG1は、関連fact欠落時に拒否へ倒す明記が必要です。

**12. 再発防止か個別パッチか**: 言語不一致の是正は再発防止です。同義語表は「データとして保守する負債」になる点に留意が必要です。

## 論点別回答

### 1. AG1-strictは「緩めずに」Human Review 0にできるか
- **「緩めない」とは言い切れません。正確には「本来のguard意図に戻す」です。**
  - 現行guardは言語不一致で、実質「英語の主体語は一律禁止」になっていました。
  - AG1はこれを「関連factにある主体なら許容」に戻すもので、設計時の意図(L562-567)と一致します。
- **guardのSafety寄与は元々狭いです。**
  - 見ているのは25語の主名詞だけで、修飾語や範囲は見ていません。
  - 例: F-004には「乗客」があるため、`credit-card users`→`passengers`への一般化(まさにChecker指摘と同型)もAG1-strictで許容されます。
  - 範囲・限定の正しさは、元々Recheck頼みです。報告時に「guardがscopeも守る」と誤解されない書き方が必要です。
- **同義語表の決定論性**: 照合自体は決定論で問題ありません。危険なのは**同値クラスの粒度**です。
  - `契約スタッフ`→{contractor, worker}は可です。
  - しかし`staff`/`employee`まで同じクラスに入れると、Meta案件の核心である「Meta社員ではなく外部の契約者」という区別が消えます。
  - employee/contractor/staff、customer/user/passenger/client は**別クラスを原則**とし、1エントリずつ根拠付きでレビューしてください。
  - 表に無い主体は拒否(fail-closed)で安全です。
- **英語部分の一致は単語境界で**: 現行の`a in ledger_lower`は部分文字列一致で、英語側にも誤許容の余地があります。
- **42ケースでの検証は不十分です。** 差し替え先がexecutives/analystsなど「遠い主体」で、拒否されて当然です。現実のリスクは近接誤りです。以下の負例セットを追加することを推奨します(いずれも¥0の決定論テスト)。
  - (a) 近接クラスの取り違え: contractor→employee、users→customers/passengers、staff→executives
  - (b) 別factの主体の持ち込み(rep22型)
  - (c) `related_fact_id`の欠落・誤り
  - (d) 日本語の部分一致の誤ヒット(例: 「利用者」が別の語に含まれる)
  - (e) 複数の新主体語のうち一部だけ一致
  - 加えて、全ログの**許容された**Rewriteにも新guardを当てて、許容→拒否に変わる件が出ないこと(差分0)を確認すべきです。

### 2. issue名指しを単独根拠にしない判断と、rep22型の残余
- 単独根拠にしない判断は妥当です。
- rep22型への**代替案: 「Ledgerのどこかにある ∧ Checker issueが名指し」の2条件AND**で許容する。
  - 2つの独立な根拠が必要なので、AG1-ledger(Ledgerのどこかにあれば可)より狭く、issue単独の穴(誤主体の名指し)も塞げます。
  - issueは英語なので、名指しは単語境界の照合で決定論的に判定できます。
  - rep22(関連factに主体なし・他factに「ユーザー」)は、issueが`users`を名指ししていれば救えます。
- ただし採用前に、rep22が実際にladder枯渇を生むかを委任_08で確認すべきです。設計書の「段階判断」に同意します。

### 3. 構造要素のdelete禁止+書き換え
- Human Reviewへ逃げてはいません(全滅時のみ既存の枯渇経路)。
- 1文記事の場合の動き: `filter_levels_by_problem_kind`で④(段落=記事全体)へ送られ、たとえば「The NYC taxi researchers found that passengers shown higher suggested rates left more tips.」型に書き換わるはずです。
  - 「男女差」「2倍」の残存はRecheckが検出します。
  - 主体`passengers`は元文にあるためguardも通ります。
- **防げない劣化**:
  - (a) titleと本文の整合(Recheckが見るのはLedger準拠のみ)
  - (b) 他factの内容で「別の話題のtitle」にすり替わること
  - (c) 3語以上という基準が弱く、一般論のtitleになること
- 推奨: 構造要素を書き換えた場合は、before/afterの対をRecheckへ渡すこと(既存のN3′の対ブロックを流用、追加call 0)。
- **未検証の前提**: 「先頭の非空行=title」は1文fixture由来です。Production記事の実フォーマット(`#`付きtitle、メタ行、`In one line`の位置)で、位置判定がずれないか¥0テストが必要です。
- headline専用factが無い点: 既存ladder(Ledger全文を渡す)への統合で妥当です。専用経路は不要です。

### 4. 件数一致の是正(index別集約)の安全性
- 方向は妥当です。index欠落=未解消も妥当です。ただし**実装(L1723-1733)に偽のTrueの経路が3つ**あります。
  1. `bool(it.get("resolved"))`は文字列`"false"`をTrueと判定します。`is True`にすべきです(strictなSchemaなら起きないはずですが、防御として)。
  2. n>0のとき、**範囲外のindex**(例: n=1で`{index:1, resolved:false}`)と非dictの項目(`groups[None]`)は無視されます。
     - Checkerが1始まりで番号を振ると、`{0:true}`(別物)+`{1:false}`(本当のprior 0)がTrueになりえます。旧式ならFalseでした。
  3. indexの型(int/str)が混在すると、全てNone→False(これは安全側なので問題なし)。
- **推奨する式(より単純かつ安全)**: `all_prior = 全項目のresolved is True ∧ {0..n-1} ⊆ 返却indexの集合`。範囲外の項目やfalseが1つでもあればFalse。
- 再確認での取りこぼしについて:
  - 再確認(cite-or-release)は項目別なので、偽の自己矛盾は最終的にPASSに落ちていた、という説明は論理的に整合します。
  - ただし旧式で「再確認によって非PASSになった」実例があったかは、37件中31件が未記録で未確認です。
  - 推奨: 全ログの`LEDGER_COMPLIANT ∧ all_prior=False`37件について、再確認の最終結果がPASS以外だった件数を¥0で集計してください。0件ならN1′との合流も含め、取りこぼし経路なしと判断できます。

### (packet論点4)remains_in_final_en
- 判定(目印の部分一致残存・因果`so`は除去済み)に同意します。
- ただしこれは指標側の欠陥です。目印を「因果接続語+目印」型のパターンに改めないと、毎回同じ偽陽性を手作業で分類し続けることになります。

### 5. より単純な方法(guard廃止など)
- **廃止は推奨しません。** 正当拒否の実績0は「guardが言語不一致で機能していなかった」ことの裏返しで、価値が0という証明ではありません。後ろ盾のfloor `changed_actor`はCheckerの検出に依存しており、決定論の層を失うのはSafety最優先と逆行します。
- **代替案(残余用、Fable/ユーザー判断事項)**: guard違反を「拒否」ではなく「Recheckへの注記」に変える方式。
  - before/afterの対と「主体が変わっていないか」の確認を既存Recheckに載せる(追加call 0)。
  - 枯渇は防げますが、Safetyの担保がCheckerの検出(非決定)へ移るため、**最終水準のみ・同義語表の範囲外の主体のみ**に限定すべきです。現時点では保留を推奨します。
- Rewrite promptで主体を指定する案: Checker issueの要求(限定化)と衝突するため、劣後します。

### 6. Production整合
- **件数一致**: er003 vfl01(L827)にも同じバグがあり、Production側でも偽の自己矛盾が起きている可能性が高いです。配線時は**共有関数を1つにまとめ**、er052とer003の式が二重管理にならないようにしてください。
- **actor_guard**: er052にしかありません。将来配線するなら**guard本体・同義語表・負例テストを一体で**移すことが必須です。現行guardだけを移すと、Production側でHuman Reviewが急増します。
- **構造要素の判定**: Production記事フォーマットに基づくテストを前提条件にしてください。

### 7. コスト・非決定性・retry
- 3施策とも追加callは0か微小で、非決定性も増えません。AG2/AG3を入れない限りretry loopは増えません。
- 唯一の増分は、構造要素の書き換えで最大3 call(該当はまれ)です。

## リスクまとめ
1. 同義語表の同値クラスが粗いと、近接主体の誤許容が起きます(最大のリスク)。
2. 件数一致の範囲外index・bool変換による偽のTrue。
3. title判定がProductionフォーマットに合わない可能性。
4. 構造要素の書き換えで、titleと本文の整合が崩れる可能性。
5. 37件中31件の再確認結果が未確認。

## 追加で読んだファイルと概算文字数
- `docs\pm\design_open233_kpi_recovery_02.md` L460-555(§14、約9千字)
- `er052_open233_self_recovery_flow_runner_01.py` L560-600(guard)、L1710-1770(集約関数・run_recheck冒頭)、L5565-5635(構造要素の判定)(計約8千字)
- packet `docs\pm\opus_packet_open233_kpi_recovery_02_03.md`(約1.1万字)

## 十分に答えられなかった点
- **ladder内の切り替え(L5700付近)とguard適用3箇所の実コードは未読**: 構造要素の書き換え時に`0_delete`が確実に外れるか、guardの`before_text`がどの範囲かは、設計書の記述に依拠しています。
- **`related_fact_id`の欠落率・誤り率**: 未確認です。AG1-strictのfail-closed化の頻度に直結します。
- **論点4の31件の再確認結果**: 未確認です(上記の¥0集計を推奨)。
- **構造要素の書き換えの実LLM品質**: 未検証です(次の有料runの対象)。
- 採用可否・Production採用は判断していません(人間ユーザーのみが決定)。

## (3) Fableの評価(逐語。委任_08の委任文より。変更しない)

1. **AG1-strictを採用(修正付き)**: 「緩める」ではなく「本来のguard意図(関連factにある主体なら許容)に戻す」是正。同義語表は**細粒度の同値クラス**(employee/contractor/staff、customer/user/passenger/clientは別クラスを原則。「契約スタッフ」↔{contractor, contract worker}、「クレジットカード利用者」↔{credit-card user(s)}のように1エントリずつ根拠[Ledger逐語・辞書的対応]をコメントに書く)。英語側の照合は単語境界、日本語側は語の境界に相当する前後文字の検査(部分文字列誤ヒット[「利用者」が別語に含まれる等]を排除)。`related_fact_id`欠落・誤りはfail-closed(拒否)。guardがscope(限定・一般化)を守るものではないことを設計書と報告に明記(scopeはRecheck担保)。
2. **2条件AND補助を採用**: 関連factに無い新主体でも、「Ledgerのどこか(他fact)に同義語表で一致」∧「Checker `issue`/`explanation`がその主体を単語境界で名指し」の両方を満たすときのみ許容(rep22型の残余)。issue単独・Ledger単独では許容しない。
3. **負例テスト(a)〜(e)と差分0確認を必須化**: (a)近接クラスの取り違え(contractor→employee、users→customers/passengers、staff→executives)、(b)別factの主体の持ち込み(issue名指しなし)、(c)`related_fact_id`欠落・誤り、(d)日本語部分一致の誤ヒット、(e)複数新主体語の一部のみ一致→拒否。加えて全ログの**許容された**Rewrite全件に新guardを当て、許容→拒否に変わる件が0であること(差分0)。
4. **件数一致是正の修正**: Opus指摘の3点を反映。式=「全項目の`resolved is True` ∧ {0..n-1} ⊆ 返却indexの集合」。範囲外index・非dict項目・`resolved`が`True`以外(文字列"false"等)が1つでもあればFalse。
5. **構造要素書き換えの補強**: 構造要素を書き換えた場合、before/afterの対をRecheckへ渡す(N3′の対ブロックを**構造要素の場合に限定して**流用、追加call 0、`RECHECK_BEFORE_AFTER_PAIRS`とは独立のスイッチ`STRUCTURAL_PAIRS_TO_RECHECK`、KPI構成ON)。title判定の位置ずれをProduction記事フォーマット(`#`付きtitle・メタ行・`## In one line`の位置。`er019_output`/`er012_output`配下の実記事`article.md`/`parts.json`を3本以上サンプル)で¥0テスト。
6. **残存指標の是正**(計測): `SAFETY_CRITICAL_CLAIM_DEFS`の`text_substring`に、因果型は「因果接続語+目印」のパターン(例: `so the flashy 20% plan`/`because`…)を使えるよう`text_pattern`(regex)を追加し、B3/neg5は`\b(so|because|therefore|as a result|led to)\b[^.]{0,40}flashy 20% plan`相当へ。旧`text_substring`も残し旧新並記。
7. **¥0集計**: 全ログの`LEDGER_COMPLIANT∧all_prior=False` 37件の再確認最終結果(PASS以外の件数)。0件なら「取りこぼし経路なし」と記録、>0なら各件の中身を列挙。
8. **不採用/保留**: guard廃止(不採用)、guard違反の「Recheck注記化」(保留)、AG2/AG3(不採用)、Rewrite promptでの主体指定(劣後)。
9. **Production整合**: 件数一致式はer003 vfl01 L827と共有関数化が必要(配線時)、actor_guardはguard本体・同義語表・負例テストを一体で移す、構造要素判定はProductionフォーマットのテストを前提 — `OPEN-233-A1-PROD`へ記録。

### PM_GOVERNANCE 11-3「Fableの役割」8項目の照合

| 照合対象 | 結果 |
|---|---|
| Claude案 | 委任_07のAG1(Ledger照合型)・構造要素delete禁止+書き換え・件数一致index別集約。OpusはAG1-strictの方向・件数一致の方向を妥当とし、同義語表の粒度・件数一致の3穴・構造要素の対渡し・指標のパターン化を修正点として指摘。FableはAG1-strict(修正付き)+2条件AND・3穴修正・対渡しを採用(Claude案とOpusの対立なし、Opusの修正採用) |
| Opusレビュー | 評価1〜9のとおり(AG1-strict+2条件AND・負例(a)〜(e)・差分0・件数一致式・構造要素の対渡し・text_pattern・37件集計・guard廃止不採用・Production整合) |
| CURRENT_SPEC.md | 変更なし。Trial側(`er052_open233_*`)のみ。Checker本体Prompt/Schema/判定規則は不変 |
| DECISION_LOG.md | 2026-10-04のユーザー指示(KPI変更禁止・Opusの指摘はFable/Claudeで採否判断)の範囲内 |
| OPEN_ITEMS.md | `OPEN-233-KPI-RECOVERY-REDESIGN-02`行のStep 7再ループに対応。新しいUSER_DECISION_REQUIREDなし |
| ユーザー承認済み内容 | KPI(Human Review 0件/Safety重大見逃し0件/+¥2/+¥3 Cap)を変更しない。Human Reviewへ倒す新経路を作らない。新しいretry loopなし(`MAX_CYCLES=2`/`HARD_MAX_CYCLES=3`不変) |
| QCD | 1重大見逃し0(guardは廃止せず細粒度化・負例テスト必須)・2 Human Review 0(過剰拒否の是正)・3不要Rewriteは増えない・4 追加call 0(構造要素書き換えのみ最大3 call、該当まれ) |
| PM強制Gate | Production採用なし(APPROVED/WIRED不変)。有料実行は費用概算を先出し、母数・採否基準を事前設定して事後変更しない |

### STOP条件(11-3「必ずSTOP」7項目)非該当の根拠

(1) 重要な結論の対立: なし。(2) 新しい仕様・Product原則: なし(guardの意図への回帰とKPI範囲内の是正)。(3) Safety/QCD上の明確なトレードオフ: なし(同義語表は細粒度・fail-closed・負例テスト・差分0確認を必須化)。(4) Production正式採用判断: なし。(5) 既存のユーザー承認内容の変更: なし。(6) 予算・Scope・運用方針の変更: なし(委任_08上限¥32のGuardrail内、Phase残¥232.81)。(7) 新しいUSER_DECISION_REQUIRED: なし。

結論: 進行条件7項目をすべて満たすため、Fable判断で次工程(実装・差分0確認・限定確認rep29a・Step 6再確認rep29)へ進む。
