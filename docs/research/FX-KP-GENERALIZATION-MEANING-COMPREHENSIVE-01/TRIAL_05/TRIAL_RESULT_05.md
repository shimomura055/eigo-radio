# TRIAL_RESULT_05 (委任_22: 課題① 字義訳 Trial_05 Stage 1 + held-out の途中結果。**Fable盲検判定前。VALIDATEDの判定はしない**)

管理ID: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01 委任_22 / 設計=`../TRIAL_DESIGN_06.md` / 台帳=`BUDGET_LOG_01.md` / 実行=`er112_kp_gm_trial_05.py`(DEV専用、Production module編集0、Production hash開始=終了一致[`production_hash_start.txt`/`production_hash_end.txt`]) / 使用モデル: `gpt-6-luna`、effort=high固定(最新世代の最上位系ではない。理由=評価対象がluna生成の品質そのもの[Production系列と同一、25節の例外]。判定=Fable盲検、API 0)。

## 1. 状態(事実)
| arm | R(hard-core 4KP+co-KP 3、3rep) | held-out(10KP、1rep) |
|---|---|---|
| B0 | 3rep全件完了(12 call) | 完了(10 call) |
| M | 既存Trial_04のrep1-2を参照+**新規rep3完了**(4 call) | 対象外 |
| X1 | 3rep全件完了(12 call) | 対象外 |
| X2 | 3rep全件完了(12 call) | 完了(10 call) |
| Cp | **rep1全件完了(4 call)+rep2はdraw a lineのみ(1 call)で自動停止**(平均0.242円>0.20円)。rep2残り3・rep3 4 call未実行。Trial_04の既存Cp rep1は参照可 | **未実行**(約2.4円=残枠超過) |

費用合計 **6.252円/上限8.33円**(65 call)。held-out 10KP=抽出順(seed=22)の先頭10件(`heldout_selection_log_05.json`。Z[小説]は母集団に2件のみ[`rise above`,`tiny bomb`]で全数を含む)。残り4件(`feel borrowed`,`feel like friction`,`jump into action`,`story with two different speeds`)は未実行。

## 2. 決定論的集計(API 0。`metrics_05.md`)
| arm | n出力 | 1call円 | reasoning_tokens/call | validate互換 | gloss==naive_ja | 文字数比>1.5(対B0平均) | 説明文型語尾 | conveys yes/partly/no |
|---|---|---|---|---|---|---|---|---|
| B0 | 31 | 0.0585 | 304 | 31/31 | - | - | 1 | - |
| M | 7 | 0.0524 | 336 | -(M_SCHEMAは欄無し) | - | 3/7 | 0 | - |
| X1 | 21 | 0.0654 | 528 | 21/21 | - | 11/21 | 3 | - |
| X2 | 31 | 0.1254 | 1,074 | 31/31 | **0/31** | 15/31 | 3 | 8/1/22 |
| Cp | 9 | 0.2424 | 2,309 | 9/9 | - | 2/9 | 0 | - |
- Production `validate_item_corrected`(括弧禁止・算用数字・人称整合・qa・current_gloss_consistent型)への互換は、X1/X2/B0/Cpの全出力で不合格0(M6=動作は目標達成)。`gloss==naive_ja`(アンカリング)=0/31。
- 注意: 文字数比>1.5は短いgloss(多くが5〜10字)では1〜3文字の差でも超えるため、**長さの過剰の指標として弱い**(30字超は全armで0件)。説明文型語尾はX1/X2が各3件(B0 1件)=**種類の分類はFable盲検後**。
- M2(診断): X2のR core 4KP x 3rep=12出力の`naive_ja_conveys`は **no 9 / yes 3 / partly 0**(yes 3件はすべて`draw a line`で naive_ja=「線を引く」)。no/partly率=9/12(期待≧10/12の事前宣言をわずかに下回る)。全31出力では yes 8 / partly 1 / no 22。
- reasoning_tokens(OF-KP1-03): `REASONING_TOKENS_01.md`。B0 361→X1 527→X2 1,206→Cp 2,308 (R, 1callあたり)。

## 3. Fable盲検
- `fable_blind_05.md`(20行・78セル。R 7KP+held-out 10KP中の未ラベル文字列+**ラベル済み文字列10件の再判定[OF-KP1-08]**を混在、arm伏せ)と`fable_blind_05_key.json`。held-out 10KPの本文全体は`er112_output/kp_gm_trial_05/heldout_set_05.json`(`article`欄)。
- 判定済み文字列の継承: Trial_02〜04でFable確定済みの文字列は表に含めず継承(再判定10件のみ混在)。
- 判定後の集計: `py er112_kp_gm_trial_05_report.py report --labels <labels.json>`(labels形式=`{"<row#>:<col>": PASS|THIN|FAIL|FAIL_LIT}`。Trial_04と同じ。R基準の事前宣言[(FAIL_LIT+FAIL)≦1/12 かつ 2/3以上失敗KP 0 かつ THIN≦B0+1]、X1対M、X2対Cp、held-out悪化、control一致率、R Before/Afterを出力)。X2の`meaning_in_text_en`/conveysは**判定後に**`x2_fields_05.md`を開く。

## 4. OF-KP1-07 Grep確認(API 0)
- A/B/C旧ライン(凍結中)は新規生成経路を通らない: `is_fulltext_gloss_missing`(`er003_key_words_gloss_alignment.py:270-273`)は`fulltext_source_ref`付きitemのみ真(docstring「A/B/Cのitemは該当しない」)。`fulltext_source_ref`の設定側=`er105_kp_fulltext_selector_01.py`・`er003_key_words_canonicalization.py`のみ。gloss再整合の呼出元(`align_glosses(`、Trial/test除く)は`er003_v1_n3_01_scaffold_generate.py:539`(X/標準)と`er026_family_z_fiction_production_runner_01.py:1552`(Zの人称修復、current glossあり=M-base/X2の新規生成分岐は適用されない)の2か所のみ。
- 今回のTrialは新規生成経路のみが対象。混在batch・Z repair経路は`TRIAL_DESIGN_06.md` §3-1に確定(採用設計時の課題)。

## 5. 未解決・次の判断(判断候補)
1. 事前宣言の判定基準(R)での判定は**Fable盲検後**(私はしない)。Cpが2rep目以降未完のため、X2対Cpの比較はCpが「rep1 4call+Trial_04のrep1参照」の1〜2rep相当。
2. 予算: Cp R残り7call(約1.7円)+held-out Cp 10call(約2.4円)=約4.1円=合計約10.4円で個別枠8.33円を約2.1円超過。Cpは単価が見積(0.18円)の1.35倍(0.242円)。**案**: (a)追加約4.1円(+上限の見積幅を含め約5円)で完遂(案件累計は約280円≦300円)=推奨、(b)held-out Cpを除きR Cp残りのみ(約1.7円、残枠内だがpilot閾値0.20円/callの平均超過で自動停止している=閾値の再設定が必要)、(c)Cpを追加せずStage 1の盲検結果(B0/M/X1/X2+Cp 1.2rep)で判断。いずれもFableの判断。

## 委任_23 追記(Fable盲検ラベル反映・Cp完遂)
- Fable盲検ラベル(Stage1+held-out、Key未開封で確定)を `fable_labels_05.json` に保存、注記を `FABLE_BLIND_RESULT_05.md` に逐語保存し集計(`report_05_fable_labels_05.md`)。
- 判定材料(**VALIDATED判定はFable**): R基準(FAIL系<=1/12 かつ 2rep以上失敗KP 0 かつ THIN<=B0+1)は、X2: FAIL系0/2rep失敗KP 0だがTHIN 4>B0+1=1、Cp: FAIL_LIT 2(ラベル確定前でも不達)、X1/M/B0不達。H5(X1対M)はFAIL系 6→5で有意差なし。held-out悪化: X2=0、Cp=追加盲検05c確定後。control一致率 7/10(不一致3件はすべて前回より緩い方向)。
- Cp追加(19call、2.545円)後の追加盲検表 `fable_blind_05c.md`(10文字列)。ラベル後に `--labels_c` 付きで再集計。
- Stage 2準備(未実行): `er112_kp_gm_trial_05.py gen --arm X2 --set S2 --reps 1`(non-R 54KP、29 call、見積約3.64円)→`er112_kp_gm_trial_05_report.py blind_s2`(B0/CpはTrial_04再利用)。Fableが「Stage 1通過」を連絡してから実行。

## 委任_25 追記(05cラベル確定・Stage 1確定表・X2')
- 05cラベル(Fable、Key未開封)を `fable_labels_05c.json` に保存、注記と「Fable判定の揺れ(緩化方向)」を `FABLE_BLIND_RESULT_05.md` に逐語保存。再集計: `py er112_kp_gm_trial_05_report.py report --labels fable_labels_05.json --labels_c fable_labels_05c.json`(`report_05_fable_labels_05_withc.md`、X2p追加後は同ファイル名で上書き)。
- **Stage 1確定表(R hard-core 4KP x 3rep=12出力/arm、ラベル確定後)**:

| arm | PASS | THIN | FAIL系(FAIL_LIT+FAIL) | 2rep以上失敗KP | 事前宣言基準 |
|---|---|---|---|---|---|
| B0 | 2 | 0 | 10 | unseen clock/trophy/greener grass | (基準線) |
| M | 6 | 0 | 6 | unseen clock/trophy | 不達 |
| X1 | 7 | 0 | 5 | trophy | 不達 |
| X2 | 8 | 4 | 0 | なし | THIN 4>B0+1のみ不達 |
| **Cp(確定)** | **9** | **1** | **2** | なし | FAIL系2>1で不達(unseen clock rep2「見えない時計」、greener grass rep3「より青々とした芝生」) |
- held-out 10KP: X2悪化0、**Cp悪化0**(05c確定後)。
- X2p(委任_25): 差分は `TRIAL_DESIGN_06.md` §9、費用 `BUDGET_LOG_01.md` 委任_25追記。決定論集計(`metrics_05.md`): 31出力、1call平均0.1412円、gloss==naive_ja 0/31、文字数比>1.5 14/31(X2 15/31)、説明文型語尾3(X2 3)、30字超0、conveys yes/partly/no=4/4/23(X2 8/1/22)、validate互換31/31。出力欄=`x2p_fields_05.md`(判定後に開く運用)。
- 盲検表 `fable_blind_05d.md`(X2pで新出の13文字列・10行、既出14文字列はラベル継承、arm伏せ)+`fable_blind_05d_key.json`(別ファイル)。**VALIDATED判定はしない(Fable)。** ラベル後: `report --labels fable_labels_05.json --labels_c fable_labels_05c.json --labels_d fable_labels_05d.json`。
