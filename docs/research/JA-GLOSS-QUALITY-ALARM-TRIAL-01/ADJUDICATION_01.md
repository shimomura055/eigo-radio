# ブラインド裁定の記録 (ADJUDICATION_01)

管理ID=JA-GLOSS-QUALITY-ALARM-TRIAL-01 / OPEN-636 / 委任_02A / 2026-10-31 / API 0。基準=`ADJUDICATION_RUBRIC_01.md`。凍結ラベル=`labels_frozen_01.json`(sha256は `TRIAL_PLAN_02.md` §0)。集計の再生成=`tools/build_labels_frozen_02a.py`(決定論)。

## 1. 手順と実施内容
1. 対象346件=T2 71件+T4 14件(dev分を含む全件)+運用プール261件(`user_test/selection_form_v3/data` 27ファイル)。同一内容の重複(別level・別ファイル)も別項目として裁定し、重複間で最終ラベルに食い違いがないことを機械確認した(`stats_02a.json inconsistent_duplicates=[]`)。
2. **ブラインド化**: 裁定者が見た情報は 表現・現訳・該当英文・前後文(各最大2文)・level のみ。tier(T2/T4/プール)、警告の有無、検査器(Luna)出力、HR承認済みか、過去の事前所見は見ていない(項目IDも `BL-001〜346` に差し替えseed=20261031でシャッフル)。
3. **第1判定**(`adjudication/pass1_exc.txt`): BL連番シートで全346件。**第2判定**(`pass2_exc.txt`): seed=20261101で再シャッフルした別シートを、各項目に3つの問い(①文脈上の語義と一致するか ②比喩・定訳・専門語を損なっていないか ③日本語として意味が取れるか)で判定。第1判定の結果・理由は参照せずに行った。**不一致は第3判定**(`pass3.txt`)で確定。
4. 記録形式: 例外行(problem)のみ `BL-id|p|severity|category|reason_ja|suggestion` で記録し、残りは normal(既定の理由文、境界の normal は個別の理由)。exclude は**0件**。`labels_frozen_01.json` に1項目ずつ全フィールド(label/severity/category/reason_ja/suggestion/pass1/pass2/decided_by)が入っている。
5. 抽出元の注記: プール項目の前後文は、各run dirの `gloss_alignment_prompt.txt`(生成時にLunaへ渡した記事本文)から該当英文を検索して取得(261件全件で取得成功)。T2/T4は `eval_set/items.json` の前後文。

## 2. 件数表(凍結ラベル)
| 母集団 | 件数 | normal | problem | exclude |
|---|---|---|---|---|
| T2(HR承認済み・旧「正常」) | 71 | 70 | **1** | 0 |
| T4(旧「判断保留」) | 14 | 13 | **1** | 0 |
| 運用プール | 261 | 249 | **12** | 0 |
| 計 | 346 | 332 | 14 | 0 |
- T2/T4をdev/held-outで分けると: T2 dev 38(normal 37・problem 1=`side by side`→『隣り合わせに』)/held-out 33(全normal)。T4 dev 7(全normal)/held-out 7(normal 6・problem 1=`insulation`→『熱を逃がしにくくするもの』)。
- **T2の再ラベル効果(Opus M-1)**: 警告に関係なくT2全71件を裁定した結果、1件(`side by side`)がproblemになった。片側裁定(警告が出た項目だけ再ラベル)では見えなかった種類のラベル変更である。T4は14件中13件がnormalで確定し、P-c等の正常側(T2+T4のnormal)に加わる。

### severity(rubric §4で凍結)
| | major | minor | inconsistent |
|---|---|---|---|
| 全体 | 5 | 9 | 0 |
| T2 | 0 | 1 | 0 |
| T4 | 0 | 1 | 0 |
| プール | 5 | 7 | 0 |
major 5件=verdict(Std・Adv)、charge、radius、equivalent width(Std)=**すべてユーザーが過去に指摘・修正した既知の型**。

### 類型(1〜6)
| 類型 | 全体 | T2 | T4 | プール |
|---|---|---|---|---|
| 1 意味不一致 | 0 | 0 | 0 | 0 |
| 2 辞書第一義への一般化 | 0 | 0 | 0 | 0 |
| 3 比喩・物語像の喪失 | 4 | 0 | 0 | 4(verdict×2、charge、culprit) |
| 4 定訳・専門用語の言い換え | 5 | 0 | 1(insulation) | 4(radius、equivalent width×2、insulation) |
| 5 不自然・分かりにくさ | 5 | 1(side by side) | 0 | 4(side by side、one's型×3) |
| 6 記事内不整合 | 0 | 0 | 0 | 0(単項目裁定では付けない。rubric §3) |

問題14件の内訳: **ユーザー既知の型7件**(プール: verdict×2、charge、culprit、radius、equivalent width×2)+**ブラインド裁定で新たに見つけた7件**(すべてminor: insulation×2〈プール1・T4 1〉、side by side×2〈プール1・T2 1〉、`one's`型3〈scrape one's chair across、hold one's son back、blame one's scream on〉)。**運用プールのmajor(意味が変わる)は、ユーザー既知の型を除き0件**。

## 3. 一致率(第1判定対第2判定)と不一致
| | normal | problem | exclude |
|---|---|---|---|
| 第1判定 | 332 | 14 | 0 |
| 第2判定 | 331 | 15 | 0 |
- 観測一致 345/346 = 0.9971、**Cohen's κ = 0.964**(3値 normal/problem/exclude)。severity・類型は一致した14件すべてで一致。
- 不一致=**1件**: `BL-332` forced to log in→『無理やり聞かされる』(第1=normal、第2=problem[類型3 minor])。
- **第3判定**(`pass3.txt`): normal で確定。理由=承認済みの生成仕様(`gloss_alignment_prompt`: 『比喩・慣用は、その比喩が指す一般的な意味を書く』)に沿い意味が正しく、比喩の像の喪失は単独では修正指示水準でない(rubric §7-4)。凍結ファイルでは `borderline_normal=true`。
- **κの解釈上の限界(重要)**: 第1・第2・第3判定とも同一の裁定者(同一モデル)が行った。shuffle・理由非表示・別手順(3つの問い)で独立性を高めたが、同一モデル・同一セッションのため第2判定は第1判定の記憶の影響を受けうる。κ=0.964は**人間2名の評価者間一致ではなく、同一裁定者の再現性**を示す上限的な値である。Fableの抜き取り確認(§6)を、独立性を補う主な手段として位置づける。

## 4. 有病率(運用プール261件、problem率。Wilson 95%区間)
根拠=TRIAL_PLAN_02 §2 の「有病率の根拠(M-4)」。
| 集計 | n | problem | 率 | Wilson 95% |
|---|---|---|---|---|
| **全体** | 261 | 12 | 4.6% | 2.6〜7.9% |
| **dev評価セット項目を除く(P-a'の母集団)** | 216 | 8 | **3.7%** | 1.9〜7.1% |
| dev項目のみ(45件) | 45 | 4 | 8.9% | 3.5〜20.7% |
| dev記事を除く(別掲・参考) | 148 | 8 | 5.4% | 2.8〜10.3% |
| Family別(全体) X / Y / Z | 144 / 41 / 76 | 9 / 1 / 2 | 6.3% / 2.4% / 2.6% | 3.3〜11.5 / 0.4〜12.6 / 0.7〜9.1 |
| Family別(dev項目除く) X / Y / Z | 115 / 37 / 64 | 5 / 1 / 2 | 4.3% / 2.7% / 3.1% | 1.9〜9.8 / 0.5〜13.8 / 0.9〜10.7 |
| level別(全体) Std / Adv | 116 / 145 | 6 / 6 | 5.2% / 4.1% | 2.4〜10.8 / 1.9〜8.7 |
| level別(dev項目除く) Std / Adv | 97 / 119 | 3 / 5 | 3.1% / 4.2% | 1.1〜8.7 / 1.8〜9.5 |
- 事前の仮置き(3〜10%、TRIAL_PLAN_01 §2-1)の範囲内。ただし**problem率4.6%(区間2.6〜7.9%)の大部分は、ユーザー指摘済みの型が占める**(全体12件中7件)。devを除く8件のうち5件(culprit、radius、equivalent width×2、insulation)は**held-outのT1/T4項目と同一内容**で、P-a'とP-c(held-out)は完全には独立でない(TRIAL_PLAN_02 §1で明記)。
- P-a'の母集団(216件)にはdev項目を除いた後も、**Y/Zのproblemが3件しかなく**(Y 1・Z 2)、Family別Precisionは区間が極めて広い。Family別は参考表示にとどめる。

## 5. 裁定者の較正と偏りの注意(Fable向け)
1. 基準の較正に、ユーザー指摘の実例(verdict/charge/culprit/radius/equivalent width)を用いた(rubric §7-4)。これらの型の判断は既知の指摘の影響を受ける。逆に、**ユーザーが指摘していない型を新たにmajorとした件数は0**であり、裁定者が厳しすぎる偏りは見られない一方、寛容すぎる(取りこぼす)可能性は排除できない。抜き取り確認で境界(normalのborderline 19件)を見てほしい。
2. **borderline normal 19件**(`borderline_normal=true`、凍結ファイルに理由付き): BL-016, 049, 074, 093, 106, 115, 130, 141, 179, 184, 192, 198, 213, 237, 257, 261, 292, 293, 332。内訳=compensation(説明的)、sink for ever(婉曲)、frustrate(感情寄り)×4、persuade(説得/納得の差)、blow a whistle(笛→警報)×2、lose one's trust(硬い)、hold someone back(悪意含み)、over its entire history(『終わりまで』)×2、drown(受身的)×2、exception(定義的)、sponsored、forced to log in。これらは検査器が警告した場合に「誤警告(好み水準)」と数える。
3. **T1との対応(rubric適用後のseverity)**: T1の重大度は元の `eval_set/items.json` ではagent案だったが、凍結したrubricをT1相当のプール項目に当てはめると下表になる。`items.json` 本体のT1 severityは変更していない(ラベルの事後変更をしないため)。ガードの分母には**rubric適用後**を使う案を TRIAL_PLAN_02 §3 に記載した(**判断候補**: 採否はFable)。

| T1 id | 表現→現訳 | split | agent案 | rubric適用後(対応するBL) |
|---|---|---|---|---|
| T1-039 | verdict→結論(Std) | dev | major | major(BL-092) |
| T1-045 | verdict→結論(Adv) | dev | major | major(BL-120) |
| T1-106 | charge→非難 | dev | major | major(BL-190) |
| T1-114 | things left out→省かれたもの | dev | major | (プール外・comment_translationのため対応なし。majorのまま) |
| T1-035 | culprit→原因 | held_out | minor | minor(BL-002) |
| T1-107 | radius→中心から外側までの長さ | held_out | minor | **major**(BL-223、類型4) |
| T1-108 | equivalent width→光の線の特徴を表す幅 | held_out | minor | **major**(BL-229、類型4) |
| T1-109 | equivalent width→スペクトル線の強さを示す等価幅 | held_out | minor | minor(BL-006、類型4・訳語『等価幅』は残るため) |
   → held-out の T1 major は 0件(agent案)から 2件(rubric適用後)になる。

## 6. Fable抜き取り確認用(無作為20件、seed=20261101)
- ブラインドシート(ラベル・理由なし)=`adjudication/spot_check_20_blind.md`。対象ID(`labels_frozen_01.json` の `blind_id` で突合):
  BL-001, BL-014, BL-023, BL-026, BL-031, BL-047, BL-060, BL-065, BL-070, BL-073, BL-113, BL-141, BL-169, BL-182, BL-202, BL-229, BL-251, BL-287, BL-320, BL-334
- 無作為20件には problem が **BL-065, BL-229 の2件**しか入らない(problem率が低いため)。追加の推奨確認(任意): problem全14件(BL-002, 006, 015, 065, 068, 092, 120, 190, 194, 197, 223, 229, 273, 341)と borderline normal 19件(§5-2)。**判断割れがあっても本ファイルは書き換えない**(凍結)。割れた場合は件数と内容をFableが `TRIAL_PLAN_02.md` 末尾に追記し、変更前後の結果を併記する(TRIAL_PLAN_01の冒頭規則と同じ)。

## 7. 備考
- `tools/adj_build_pool_02a.py`(プール項目と前後文の抽出)・`tools/adj_mk_sheets_02a.py`(ブラインド連番化とシャッフル)・`tools/build_labels_frozen_02a.py`(集約)は、メインツリー(`C:/Users/tensh/eigo-radio/er*_output`)を読み取り専用で参照する。ブラインドシート本体はscratchに生成しており、再生成は `blind_map.json`/`order2.json` から可能。
- T3'(16件)は裁定対象外(合成による確定)。`labels_frozen_01.json` の `t3prime` セクションに分けて収録。作成規則=`T3PRIME_RULES_02.md`。

## 8. Fable抜き取り確認の結果(2026-10-31、委任_02Bでの追記。凍結ラベルは変更しない)
- Fableが §6 の無作為20件(seed=20261101)を独立に確認した結果、**20/20一致**。problem 2件(BL-065 hold one's son back「足を引っ張る」[引き止める/束縛のニュアンス]、BL-229 equivalent width「光の線の特徴を表す幅」[定訳=等価幅])と、normal 18件。Fable判定として記録。
- κ=0.964 の限界(第1〜3判定が同一裁定者)は維持する。Fable一致率(20/20)は補助証拠であり、独立した複数裁定者の代替ではない(problemが2件しか入っていないため、problem側の検証力は弱い)。
