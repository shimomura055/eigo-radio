# FORM_TEST_MONKEYS_PAW_B1B_01 「猿の手」Advancedフォームテスト送信の復元tool照合(委任_09、2026-10-27、API 0・音声生成なし)

**本件はフォーム送信のテストであり、「猿の手」の制作内容の正式確定ではない。日本語訳はすべて仮訳(`ja_gloss_status=provisional`)・未確定で、正式採用・Production反映はしない。確定(dry-run解除)も実施していない。**
原文=`docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_04.md` §3。

## 1. 入力の再構成(機械的)
受領内容は整形転記(フォームの逐語コピーではない可能性が高い)。`COPY_FORMAT_01.md` §1の形式へ再構成: `inbox/monkeys_paw_b1b_test_01.txt`。
推測した箇所: (a)各項目末尾の`（仮訳・未確定）`(§1の規則で、データが`provisional`のため。受領値に無いが実フォームのコピーには付くはず) (b)見出し`記事：猿の手｜Advanced`、`文法：選定なし`の文言(受領の「文法0件」を形式の固定文字列へ) (c)項目順=データ順(受領順と一致)。照合コード行は受領値そのまま。
比較用に注記なし版も作成: `inbox/monkeys_paw_b1b_test_01_nosuffix.txt`(受領文面に忠実)。

## 2. dry-run照合結果
コマンド: `py er119_kp_human_review_cli_01.py confirm --from-readable <txt> --run er118_output/fz_full_episode_trial_01/monkeys_paw --level b1b --by fable --user-ref docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_04.md --dry-run`(出力=`dryrun_*.out`、rc=0、確定・保存なし)。
データ版: 公開データ`user_test/selection_form_v3/data/monkeys_paw__b1b.json`(現行版のsha256先頭6桁=`00eb90`、履歴復元不要=notes空)。

| 照合コード欄 | 受領値 | 現データから算出 | 結果 |
|---|---|---|---|
| stem | monkeys_paw__b1b | ファイル名 | 一致 |
| d6 | 00eb90 | 00eb90 | 一致 |
| c8 | 00000000 | candidates_sha256=null→00000000 | 一致(null同士。下記4) |
| t8 | 8388280a | text_sha256=8388280adba4… | 一致 |
| s10 | e45da6b337 | ①②③×candidate_id順から独立再計算 e45da6b337 | 一致 |
| g10 | 0 | 文法0件 | 一致 |
| m8 | 8d5a3093 | sha256("テスト送信")先頭8桁 8d5a3093 | 一致 |
| k4 | a269 | 直前までの文字列sha256先頭4桁 a269 | 一致 |

復元payload(①②③): 
| 区分 | 英語表現 | 訳 | candidate_id |
|---|---|---|---|
| ① | accept no responsibility | 責任を負わない | p_79485f9a44 |
| ① | interfere with fate | 運命を変えようとする | p_3004ef933b |
| ① | pulled free | 振りほどく | p_82e055c35c |
| ② | caught in the machinery | 機械に巻き込まれる | p_e2b8f30da3 |
| ② | wail of loss | 失った悲しみを表す叫び声 | p_faf690f730 |
| ③ | shake one's husband awake | 自分の夫を揺すって起こす | p_15f296105c |
| ③ | compensation | 補償金 | p_acc646e6dc |
| ③ | snatch | さっとつかみ取る | p_789abf2833 |
| ③ | deserted | 人けのない | p_c0e95e0576 |
| ③ | burial | 埋葬 | p_cf22a4ad4b |

文法0件(`grammar:[]`)、コメント`テスト送信`保持、照合コード改変なし。本文sha一致。ユーザー向けテキストにJSON・candidate_id・内部コード混入なし(`candidate_id`は復元payload側のみ)。未選択候補=`pay off the house`(データに存在、選択されず)。候補集合sha: データ側null=受領c8と一致(下記4)。
注記なし版(受領文面に忠実)も復元成功。差は`（仮訳・未確定）`注記の欠落10件がnotesに記録されるのみ(dry-run、致命ではない。確定時にer128が確認する設計)。
評価事項(原文§3)の充足: ①3/②2/③5区分OK、文法0件・コメント保持OK、照合コード省略改変なしOK、混入なしOK、保存済み候補データとの照合OK。

## 3. 不一致の切り分け
不一致なし(全欄一致)。したがってユーザー転記の整形差・データ版差・改変のいずれも観測されず。注記欠落のみ整形差(許容)。

## 4. `c8=00000000`の意味
`COPY_FORMAT_01.md` §3: `c8`=`candidates_sha256`先頭8桁、「`null`なら`00000000`=er128が拒否」。これは「確定済みロック無し」ではなく、**候補集合shaが存在しないデータ**を表す。本データは`candidates_sha256_source=unavailable_dev_trial_doc`(Trial文書由来の候補で、Production KP review/候補docが無い試作)。実際に`discover_kp_dirs(猿の手run)`=`[]`(KP reviewディレクトリ無し)。よって:
- 試作データとしての照合(dry-run)は成立する。
- 本番確定(`--dry-run`解除)は、KP review/候補docが無く`cmd_from_form`の`candidates_sha256`・`text_sha256`照合ができないため**拒否される設計**。今回の送信は確定対象でなく、確定もしていない。

## 5. 「選定結果をコピー」の逐語貼付があれば確定可能か
照合・復元の観点では、受領文面でも逐語貼付でも同一payload(`payload_sha256=fbd5035e…`)になり差は生じない。ただし確定可否は貼付の形式ではなく**対象記事側の条件**で決まる: 猿の手はProduction候補doc(candidates_sha256)とKP reviewが未整備のため、逐語貼付があっても確定は不可(fail-closed)。確定には、猿の手Advancedの正式な候補doc生成(Production KP経路)と日本語訳の正式化が前提。いずれも今回の範囲外で、実施していない。
