# PREREGISTRATION: FACTLOCK-WRITER-REDESIGN-TRIAL-01(2026-10-08、委任_01で確定、v2=委任_02aでOpus条件A反映、生成は委任_02b)

性質: Trial(比較実験、Production経路ではない、決定Aの例外Trial=ユーザー指示)。Status上限=MEASURED。**合否しきい値なし**。Opus条件Aレビュー後に内容が変われば本書を改訂し再度固定する(改訂履歴を末尾に追記)。設計の詳細は `DESIGN_01.md`。

## 1. 問い
6-luna×Fact Lock が、6-luna×現行prompt(進行中Trial ALL-6-LUNA-...の all6 セル)に対し、事実NG(重大/軽微)をどれだけ改善/悪化させるか。数値化のみ。良化/悪化の判断・Production採用はFable/人間ユーザー。

## 2. セルと固定条件(§6確定版)
- セル: **6-luna×Fact Lock** 1セル。12 brief(B3 V0 b1〜b4 × meta/hormuz/space_weapons)×反復2=**24本**。
- 比較対象(reuse): 進行中Trialの all6(6-luna×現行)と baseline(5.6×現行)の各 brief×反復。値は進行中Trialのfresh測定値を再利用。本Trialのfresh: 生成NG率・照合値(Trial harness経由、production_formal_pathではない)。
- 固定: brief=注記版(`briefs/<slug>/b<i>/selected_brief_factlock.md`、原本B3 briefとの差は事実ID【事実N】と数値印のみ)、台帳=`open233_polysemy_trial_02/ledgers/<slug>/control`(進行中Trialと同一)、reasoning effort=high、Checker ON(進行中Trialと同一構成=同スイッチdump、新スイッチ既定OFF)、JA Fact Check(R0直後・R2直後、must-fix1回・STOP)現行どおり、R3なし、EN phase2は現行どおり(6-luna)。
- 変更点(Fact Lock): R0 prompt(AN3の数字文を数値規則(c)+タグ規則に置換、固有名詞文は逐語保持)、R1/R2指示に事実固定規則を追記、JA Fact Checkへ渡す本文のタグ除去、EN/Checker入力もタグ除去後。
- 実行条件: 並列度4(自動降格4→2→1)、`--budget-jpy 12`(phase1/phase2各)、`--checker-budget-jpy 10`、1枠の技術的失敗は再実行1回まで・全体4回まで。smoke 1本(meta/b1)を先に実施。
- 費用上限¥150(Guardrail)。到達=自動STOPではない。暴走疑い時のみSTOP(T-3定型文は DESIGN_01 §10)。見積≈¥95〜155。
- 開始条件: Opus条件A後のFable判断/進行中Trialの生成完了/ユーザーの費用了承。

## 3. 指標(§7確定版、しきい値なし)
主: 盲検rubric採点の 重大件数・軽微NG/記事・保留/記事(JA R2・EN別、テーマ別、評価者別)、R0→R2退行件数、NG型分布。
照合(本Trial固有、測定のみ): (i)文×タグ事実の和集合の主張分解判定: 文単位の不整合率・判定不能率と主張単位の集計、判定不能率、unknown_tags/記事 (ii)タグなし文(タイトル含む)の5分類(neutral/untagged_brief_fact/hedged_speculation/background_general/new_specific_claim)の件数/記事(段R0/R1/R2別、タイトルの分類) (iii)数値の不一致件数(hedge_changed+not_core)/記事、match_surface_diff、core_used_without_tag、marks_echoed、quantity_words(数量語の副指標、判定には使わない) (iv)R0→R1→R2のタグ付き文の維持/改変/削除/added/number_changed。
工程: JA Fact Check MAJOR率・must-fix率・STOP率、記号Gate must-fix率、Checker findings/Rewrite件数、費用/本(照合分別掲)、所要時間/本。
副: 面白さ盲検pairwise(6×現行 対 6×Fact Lock、同brief対、位置入替2回、LLM判定のみ)、タグによる文体の窮屈さ(目視所見)。
**しきい値なし**。Nが小さい(24本/セル)ため差と比のみ報告し有意性は主張しない。

## 4. 盲検手順
完了記事のJA R2・EN・R0・R1(タグ除去後の `ja_writer/*.md`、`b1b/article.md`)を匿名コード化し、MAPを`eval/_private/`へ隔離。**進行中Trialのall6記事と同一の評価パック・同一の評価者で一緒に採点する(v2・M8で必須化。「可能なら」を削除)**。評価者へはセル・モデル名を非開示。評価者=LLM2系統(gpt-5.6-luna / gpt-6-luna)を記事へ無作為配分、各評価者に各セル同数。MAP開封は集計時のみ。評価は人間確認なし(重大候補は `HUMAN_CHECK` に列挙)。

**STOP記事の扱い(M8)**: JA Fact CheckでSTOPした記事も母数に含める。STOP記事は、そのR0(と、到達した最終段=R1またはR2があればそれ)を同じrubricで評価する。STOP率は工程指標として別に報告し、記事単位のNG率の母数からは除かない。比較相手(all6/baseline)のSTOP記事も同じ扱いにする。

## 5. KPI provenance
生成NG率=fresh(Trial harness)/brief=reuse(B3 V0 b1〜b4注記版)/比較セル値=reuse(進行中Trialのfresh値)/E2E自己確認: No。

## 5a. 言えること/言えないこと(M9、v2追加)
言えないこと:
- 5要素(出典タグ/台帳外禁止/数値規則(c)/R1・R2事実固定規則/印付きbrief)のどれが効いたか(同時変更で分離不可)。
- 3テーマ(meta/hormuz/space_weapons)を超えた一般化(反復はbrief内で相関しており、実質のNは小さい)。
- 重大件数の差(0〜2件程度で判断不能)。
- B3が中核数値を選んだ場合の性能(中核数値の注記は実装者(Claude)の手付けで、8本が上限3件ちょうど。未測定)。
- 照合(i)(ii)の判定がWriterと同系列モデル(6-luna)による自己判定であること(同じ盲点を共有しうる)。照合は測定のみで、主指標は盲検rubric採点に限る。
- 名称内番号を省く(案A)ことによる読みやすさの良否(目視所見のみ)。
言えること:
- 軽微NG/記事・R0のNG・照合値の方向(Fact Lockが現行より増えた/減った)と、3テーマ間で方向がそろっているか。
- 数字を省いた書き方(案A)で記事が成立するかの観察。

## 6. 固定条件のsha一覧(v2再固定、2026-10-08)
全briefと原本briefのshaは `FIXED_SHAS.json`(briefs 12本の brief・core_numbers、original_briefs_unchanged 12本)。

| 項目 | sha256 |
|---|---|
| er052_factlock_writer_trial_01_run.py | `0b20b3dd9af492e6f4232b6adc403a85fce63f8ae66b7c5c19137f4630abfdb1` |
| er052_factlock_writer_trial_01_test_01.py | `e48c2aefcb9bdfeae2569852f223b9e30c6d5d67bfeed9d3052af26510127e52` |
| er052_all6_writer_trial_01_run.py(reused,read-only) | `9412a19e43753f28d55e6915e5337a5053aa037b347fb8664e261c68f508d7d0` |
| tools/annotate_briefs.py | `d09fad2db172915a4cc4528934154fe6ec2f92965903bbe2816b24bb49bf6975` |
| prompt: R0_PROMPT(不変) | `6108a7cddaa9eaf31262354ba32d33e4683ccaf810d861f27e3dcc8972028366` |
| prompt: AN3_original(不変) | `067030ff53ecb76a4d1477a3deace07b3e1fac438a33cb873edbe045cf6927fe` |
| prompt: FACTLOCK_R0_BLOCK | `74b948719e14fd7184ff3719d36639ede7905e45cef95b97c1cca1a5638b2bf1` |
| prompt: FACTLOCK_REVISION_BLOCK | `e621ee631cb6681415e41acf7de3c0ed0f6e4d9a15d337e5b82bbcb30b3c44f1` |
| prompt: PAIR_PROMPT | `e30501573f24964e48423a95322d4269a4296b9c84ff792336d834ed2506709b` |
| prompt: UNTAGGED_PROMPT | `95931cbc02cf57f4246dcb1a603015f9ca82b212d482aa72dc9e4025050bcb02` |
| production(無編集): er019_family_x_ja_writer_o_r1_r2_01.py | `b3b5b9ff0eb6e97241d50cd70b0443b43007fd32680f764911f69d70420b28e6` |
| production(無編集): er003_v1_en_direct_vfl_01_generate.py | `0aac53ecf45189150a8411b2f3a0f5817ea5de25c4c013903077051f961cbe17` |
| production(無編集): er006_model_routing_contract_01.py | `eb9bd951f9270b7b27ce4a7d585387bd8f9aa3ae583c8e9e3800c86c8e2a38bb` |

注記brief12本・core_numbers12本のv2 shaは`FIXED_SHAS.json`の`briefs`。v1の旧値(harness/prompt/brief)は`FIXED_SHAS.json`の`superseded_v1`と改訂履歴に保存。

## 改訂履歴
- 2026-10-08 初版(委任_01)。
- 2026-10-08 v2(委任_02a): Opus条件Aレビュー(M1〜M9、O1/O2採用、O3/O4不採用)反映。変更: タグ形式`【事実N】`、照合(i)=文×タグ事実の和集合の主張分解、照合(ii)=5分類・タイトル対象化、数量語副指標、タグ除去強化と残存記録、同一評価パック必須(§4)、STOP記事の扱い(§4)、言えること/言えないこと(§5a)、sha再固定(§6)。旧shaの先頭12桁: harness run `dac150add6f7` / test `7bc85de1bbf9` / annotate_briefs `43e75fc1dcfb` / FACTLOCK_R0_BLOCK `4e0bcfecc23e` / FACTLOCK_REVISION_BLOCK `3cb035e7f1d6` / PAIR_PROMPT `f18c875f1caa` / UNTAGGED_PROMPT `bd8c242a2baf`(全桁は`FIXED_SHAS.json`の`superseded_v1`)。名称内番号は案A(Opus推奨)で実施、所見は結果報告時にユーザーへ。Opus全文: `docs/pm/opus_l2_review_factlock_writer_trial_01.md`。

- 2026-10-08 委任_02b smoke後: harness `scan_residual_brackets`の許可リストに`runtime_evidence`/`fact_selection_evidence`を追加(入力brief由来・生出力の監査ログで下流入力ではない)。生成・照合・プロンプトは不変。harness sha `0b20b3dd9af4`->`6a04e22d73e4`(全桁はFIXED_SHAS.json、§6表の旧値は本改訂で置換)。
