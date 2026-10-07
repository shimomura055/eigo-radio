# PREP_NOTE: OPEN-233-NG-ROOT-CAUSE-ANALYSIS-01 委任_A1(盲検再採点パック、2026-10-07、API費用0円)

注意: この文書は出所(条件)を含む。評価者には渡さない。

## 1. 対象記事(27本、MAP: `er052_output/open233_ng_root_cause_01/_private/MAP_rca.json`)
| 出所 | 件数 | テーマ構成 | 元の場所 |
|---|---|---|---|
| E2E_02 従来版(TRIAL-04 Control rep1) | 5 | meta/hormuz/space_weapons/sewer/ai_control 各1 | er052_output/open233_polysemy_trial_04/runs/<slug>/control/rep1 |
| E2E_02 P2版 | 10 | 同5テーマ x rep1/rep2 | er052_output/open233_allfact_note_e2e_02/runs/<slug>/nb/p2/rep<N> |
| B3 V0(較正アンカー) | 12 | meta 4 / hormuz 4 / space_weapons 4 | er052_output/open233_b3_trial_01/eval/blind_stage2(MAP_stage2のV0を再匿名化) |
- テーマ合計: {'ai_control': 3, 'hormuz': 7, 'meta': 7, 'sewer': 3, 'space_weapons': 7}。依頼の概算32本に対し27本(従来版は各テーマ1本=5本、E2E_02のP2は10本、V0 12本)。N=10ずつ想定ではなくE2E_02の従来版は5本のみ(SUMMARYどおり)。
- 匿名code: sha256(seed 20261007rca|キー)由来の4文字。B3の既存code(blind/blind_stage2)と重複なし、27件内も重複なし。B3 V0の記事は「別の新規code」で複製したので、旧codeとの対応はMAP_rcaのsrc欄にだけある。

## 2. 採用した版
- JA: 全記事 `ja_writer/original.md`(R0)・`revision1.md`(R1)・`revision2.md`(R2)をそのままコピー。
- EN(`b1b/article.md`としてコピー): 
  - E2E_02従来版・P2版は **Checker最終出力(ユーザーに届くEN)**。Checkerが書き換えた記事は、最後に`en_text_after_rewrite`が空でないcycleの本文を採用(過去評価STAGEWISEの③と同じ定義)。Rewriteなし(sewer全3、space_weapons P2 rep1など)はb1b/article.mdと同一。
  - B3 V0はCheckerなしのためb1b/article.mdそのまま。
  - Checker後ENがb1bと異なる記事(MAPの`en_differs_from_b1b`=true): 9本(従来版 2/5、P2 7/10)。Rewrite前のENは `er052_output/open233_ng_root_cause_01/_private/pre_checker_en/<slug>/<code>.md` に保存(評価者非公開、後の切り分け用)。
- 注意(分析上の交絡): 今回のrubric s2_enは「Checkerなし最終EN」を想定。E2E_02はChecker後ENなので、ENの採点件数はV0(Checkerなし)と厳密に同条件ではない。必要ならpre_checker_enで再パックして比較できる(要追加委任)。

## 3. 台帳
- 整形なし。評価者はB3と同じ `er052_output/open233_polysemy_trial_02/ledgers/<slug>/control/research_ledger/verified_fact_ledger.txt` を参照(sewer/ai_controlも同パスに存在)。ハッシュ照合: このcontrol台帳 = TRIAL-04 control台帳 = E2E_02 FREEZE.jsonのbase(5テーマとも一致)。P2版はnotes欄のみ追加で事実本文は同一(FREEZE: non_notes_diff_lines空)。評価者はP2の追加notesを見ない(=従来評価のE_*.mdと同じ前提)。
- ★fact一覧: `docs/pm/allfact_e2e_02/theme_fact_watchlist.md` は5テーマとも記載あり(B3 READMEと同じ参照)。

## 4. 評価パック(`er052_output/open233_ng_root_cause_01/eval_pack/`)
- README_EVALUATOR.md: B3段階2版を流用。rubric本文は`docs/pm/b3_trial_01/eval_rubric.md`と逐語一致(検算済み)。変更したのは冒頭の適用メモ(パス・件数・テーマ複数・禁止Read一覧)のみ。rubric 7節が参照する過去NG評価シート(NG_meta.md、STAGEWISE_SUMMARY)は評価者に読ませないと適用メモに明記。
- unprovided_checklist: meta/hormuz/space_weapons=B3版コピー。sewer/ai_control=「該当なし」(新規作成せず)。
- article_schema.json: B3版と同一。ただしslug enumにsewer/ai_controlを追加(唯一の変更。scores_templateのslugも同様)。
- 評価者出力先(未作成、評価者が作る): `er052_output/open233_ng_root_cause_01/eval/articles/<slug>_<code>.json`、`er052_output/open233_ng_root_cause_01/eval/notes/rca_<A|B|C>.md`。

## 5. 評価者割当(3人、各9記事、seed固定。評価順もseed固定シャッフル)
出所別の割当(非公開): A=従来2/P2 3/V0 4、B=従来2/P2 3/V0 4、C=従来1/P2 4/V0 4。テーマは評価者内で混在(テーマ別評価者ではない: B3のテーマ別評価者との違い)。
- assignment_rca_A.md: hormuz/j7gv, hormuz/qc67, space_weapons/mc4j, hormuz/kbds, ai_control/cupe, space_weapons/bcgj, space_weapons/89wf, space_weapons/dkus, hormuz/byz5(テーマ {'hormuz': 4, 'space_weapons': 4, 'ai_control': 1})
- assignment_rca_B.md: space_weapons/493w, meta/7aqr, space_weapons/ya3m, meta/ehz9, hormuz/7hd4, sewer/g8qg, hormuz/h3rq, space_weapons/xf65, sewer/4hgy(テーマ {'space_weapons': 3, 'meta': 2, 'hormuz': 2, 'sewer': 2})
- assignment_rca_C.md: meta/ky69, meta/52ap, hormuz/xzhv, meta/78bg, ai_control/cfqm, meta/475j, sewer/87tc, ai_control/b3ux, meta/a5te(テーマ {'meta': 5, 'hormuz': 1, 'ai_control': 2, 'sewer': 1})
- 配分の記録: `er052_output/open233_ng_root_cause_01/_private/assignment_balance_rca.json`
- 限界: Cのみ従来版1本。評価者とテーマが交絡(Cはmeta5/ai_control2/sewer1/hormuz1中心)。V0は元のB3評価者(テーマ別A/B)と別人なので評価者間一致が測れる。

## 6. Fableが評価者へ渡す最小委任文(B3版と同形式、条件・出所に触れない。A/B/Cを差し替えて3インスタンスへ)
```
あなたは記事評価者(1インスタンス、単独評価)です。まず `er052_output/open233_ng_root_cause_01/eval_pack/README_EVALUATOR.md` を読み、その指示(rubric・読んでよいもの/読んではいけないもの・出力形式)に従ってください。
担当: `er052_output/open233_ng_root_cause_01/eval_pack/assignment_rca_<A|B|C>.md` に列挙された記事(9本、記載順)。
出力: 記事ごとに `er052_output/open233_ng_root_cause_01/eval/articles/<slug>_<code>.json`(scores_template.json・article_schema.json準拠)。任意の根拠メモは `er052_output/open233_ng_root_cause_01/eval/notes/rca_<A|B|C>.md`。
API・記事生成・SSOT編集・git操作・記事本文の編集は禁止。報告は8行以内(README記載の形式)。
```

## 7. 検算結果
- 件数: blindディレクトリ27 = MAP27 = 割当27(重複・漏れなし)。出所別 5/10/12。
- code重複なし(B3既存code含め)。MAPから全記事の出所復元可。
- 全記事4ファイル(R0/R1/R2/EN)が存在、各200バイト以上、NUL含まず。blind配下に出所を示す文字列(rep/p2/checker/V0)なし(「control」は記事本文中の一般語のみ)。
- 生成スクリプト(再現可): `er052_output/open233_ng_root_cause_01/tools/make_rca_pack.py`(決定論)。
