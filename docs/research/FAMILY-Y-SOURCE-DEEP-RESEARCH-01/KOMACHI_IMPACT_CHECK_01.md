# KOMACHI_IMPACT_CHECK_01 (FAMILY-Y-SOURCE-DEEP-RESEARCH-01 委任_02B: 発言小町由来素材の既存Family Y制作物への影響確認。read-only・API 0)

作成: 2026-10-28。**既存成果物の削除・変更は一切していない**(ユーザー決定①)。LLM不使用。小町・Redditの新規取得なし。下記は既存ファイルの読取りと文字列照合のみ。
根拠となるユーザー決定: 小町は当面除外、過去Trialで使った小町由来素材は再利用しない、既存成果物への影響はAPI費用をかけず確認(`docs/pm/delegation_log/2026-10-28_FAMILY-Y-SOURCE-DEEP-RESEARCH-01_USER_02.md` §1①)。

## 0. 結論(Fable判断用)

| 項目 | 結論 |
|---|---|
| 影響の有無 | **影響あり**(素材=意見の趣旨レベル)。Family Yの小町由来素材は「宅配の再配達は有料にすべきか」1テーマのみ。SNS年齢制限テーマ(`sns_age_limit`)は小町なし(TBS記事・みらい議会が出典、`RIGHTS_CHECK_01.md`/`OPINION_BASED_01`にkomachi記述0) |
| 逐語転載 | **なし**(後述§3。20字以上の連続一致0件、10字以上でも小町の発言の逐語一致は成果物本文に0件)。例外的に、意見の趣旨を言い換えた一文の言い回しの近似がある(§3の「近似」) |
| 小町由来の量 | 声16件(RV-39〜RV-54、3トピック)。うち**成果物のPersona・原稿に実際に反映されたのは A Third Voice(V3)の経験欄4スロット**(RV-40・41・42・46・54)。残り11件は収集・分析・Persona設計の参考止まり |
| 公開状況 | 限定共有のTrial/検証ページ4件(`user_test/`、noindex、一覧にリンクなし、GitHub Pagesでurlを知れば誰でも閲覧可)に、V3の小町由来の言い回しが載っている。ユーザー向け正式公開(Landing/一覧)への掲載は確認されず |
| 今後の再利用リスク | `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json` がV3を含むVoice R0(`er110_output/family_y_opinion_based_03/redelivery_fee/run_01/article_ja.md`)を固定参照している。**同テーマをProductionで再実行するとV3の小町由来部分が再び使われる** |
| 付随して見つかった事実(本委任のスコープ外・参考) | 同じ素材集合(OPINION_BASED_02)は知恵袋38件に依存。02A暫定版は知恵袋を「利用不可」とした(`TERMS_REVIEW_01.md` §1、§3-4)。小町の除外だけでは「再配達」テーマの根拠は解消しない。是正要否はFable判断 |

## 1. 小町由来素材の所在(a: どの成果物のどの箇所か)

小町16件の対応(`OPINION_BASED_02/VOICES_02.json`の`src`と`date`):
- S19 `https://komachi.yomiuri.co.jp/topics/id/800042/`(2017-04-08〜10): RV-39〜RV-48(10件)
- S20 `https://komachi.yomiuri.co.jp/topics/id/912455/`(2019-09-04〜06): RV-49〜RV-51(3件)
- S21 `https://komachi.yomiuri.co.jp/topics/id/1227312/`(2025-12-10〜11): RV-52〜RV-54(3件)

| # | 成果物(path) | 箇所 | 小町由来のID | 使われ方 | (b)状態 |
|---|---|---|---|---|---|
| 1 | `docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/VOICES_02.json` | `voices[]` の RV-39〜54(16件) | RV-39〜54 | 声の収集記録(要約・短い逐語抜粋`quotes`・日付) | 調査記録(git追跡) |
| 2 | 同 `SOURCE_LOG_02.md` | §2(件数16)、§出典表 S19〜S21(158〜160行) | RV-39〜54 | 出典ログ | 調査記録 |
| 3 | 同 `scripts/voices_data_02.py`、`scripts/build_source_log_02.py`、`scripts/build_theme_data_02.py`、`scripts/build_personas_05.py`、`scripts/build_provenance_04.py`、`scripts/axes_check_02.py` | 小町ID・URLを含むデータ・生成script | RV-39〜54 | 上記文書の生成元 | 調査記録 |
| 4 | 同 `AXIS_ANALYSIS_03.md`、`axes_check_02.json`、`PROMPT_DIFF_06.md`、`OPUS_REVIEW_06.md` | 立場軸の集計・レビューにRV-IDが出現 | RV-39〜54のいずれか | 分析・レビューの参照 | 調査記録 |
| 5 | 同 `PERSONAS_05.md` | 14行(V3の根拠の声)、79・82・83・86行(経験欄THREE_a/d/e/i)、95・100行(補足) | **RV-40・41・42・46・54** | V3(A Third Voice)の人物像・経験欄の根拠 | Persona設計(git追跡) |
| 6 | 同 `THEME_DATA_02.json` | 経験欄 `THREE_a`(source_ids RV-26,RV-54)、`THREE_d`(RV-40,RV-41)、`THREE_e`(RV-42)、`THREE_i`(RV-46) | RV-40・41・42・46・54 | **Productionのテーマ入力データ(Theme Package)の根拠欄** | Production入力(git追跡) |
| 7 | 同 `PROVENANCE_04.md` | 32〜35行(V3第1〜4文のURLに`komachi.yomiuri.co.jp/topics/id/800042/`等)、100行(V3の根拠) | RV-40・41・54(第4文はRV-40,41のみ) | R0本文の文ごとの出典対応 | 出典記録 |
| 8 | `docs/research/FAMILY-Y-VOICES-DESIGN-01/OPINION_BASED_02/sources/pages/komachi.yomiuri.co.jp_*.txt`(6ファイル) | 取得した小町ページの本文 | 全16件の原文 | 原文保存。**`.gitignore:63`でgit管理外**(権利上commitしない) | ローカルのみ(未公開) |
| 9 | `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/theme_packages/redelivery_fee_reuse_01.json` | `voice_r0_article`=下記#10を固定参照、`source_dir`=OPINION_BASED_02/sources | V3経由で間接 | **再実行時にV3を再投入する再利用manifest** | Production入力(git追跡) |
| 10 | `er110_output/family_y_opinion_based_03/redelivery_fee/run_01/`(`article_ja.md`=R0本文、`voice_3_prompt.txt`、`state.json`、`voices_final.json`、`gate_voices/final_texts.json`、`repetition_report_03.json`) | V3の第1〜4文・第6文 | RV-40・41・42・54経由 | R0のVoice 3原稿・生成プロンプト・出典メモ | Trial生成物(git追跡) |
| 11 | `er110_output/family_y_redelivery_audio_01/**`、`er110_output/family_y_closing_general_01/**`、`er110_output/family_y_closing_general_02/**`(いずれもredelivery_fee) | V3原稿を含むarticle_final・revision・closing/intro/tension用prompt | 同上(V3経由) | 音声Trial・Closing設計Trialの入力 | Trial生成物 |
| 12 | `er121_output/family_y_production_01/redelivery_fee/` 配下 10 run(`run_01`、`run_gpg5_y_01`、`run_gpg5_y_01_s23f`、`run_kp75_ev_01`、`run_kpbf_ev_01`、`run_kprescue_ev_01`、`run_hrguard_ev_02_mock`、`run_style_fix_01`、`run_voice_puck_ev_01`、`redelivery_fee_stdchunk_ev/run_ev_01`)とその`pages/index.html`・`a2/`・`audit/` | V3の語り(「営業所やロッカーで受け取る」「ロッカーを選べない」「営業所が近くて…言い分かもしれない」)が本文・要約・Comment 3に出現(10 runで文字列一致、`grep -rlE`) | V3経由 | Production手順のE2E評価run。他のrun(`run_tru_ev_*`系ほか)はV3文字列の検出なし | Trial/評価(音声・ページ含む) |
| 13 | `user_test/family_y_production_redelivery_fee_01/index.html`、`_02/index.html`、`_03/index.html` | 「日本語の元原稿」のV3(僕は再配達で迷惑をかけないよう、営業所やロッカーで受け取る…)と、Comment 3の訳・解説 | V3経由 | **限定共有のTrial試聴ページ**(最新=`_03`) | **公開(限定共有・noindex。origin/mainに存在: `_01` 28bad7b33 2026-10-26、`_02` 38da6e414 2026-10-26、`_03` 29d1a79d7 2026-10-27)** |
| 14 | `user_test/family_y_redelivery_audio_01/index.html` | R0 V3の語り | V3経由 | 限定共有のTrial試聴ページ | **公開(限定共有・noindex、803882ded 2026-10-25)** |

注: 1〜11・13・14のページは`noindex`と「限定共有」を満たすが、GitHub Pagesはurlを知っていれば誰でも閲覧できる(`RIGHTS_CHECK_01.md` 残るリスク)。`user_test/`のUI一覧(`articles_2026_0918.html`ほか)に`redelivery_fee`は載っていない(grep 0件)。

## 2. V3の小町由来の対応(PROVENANCE_04.md 32〜37行)

| V3 | 文 | 出典ID | 小町由来か |
|---|---|---|---|
| 第1文 | 営業所やロッカーで受け取るようにしている | THREE_a(RV-26,**RV-54**) | 部分(RV-54=S21は小町。RV-26は知恵袋/他) |
| 第2文 | 取りに行けるのは便利/ロッカーを選べない | THREE_a・THREE_b(RV-26) | 部分 |
| 第3文 | 手間をかけているのに不在の人と同じ料金は正直おかしい | THREE_a・THREE_c(RV-11) | 部分 |
| 第4文 | 配達する人の時間を使うんだから再配達は有料でいい | THREE_d(**RV-40,RV-41**=S19) | **小町のみ** |
| 第5文 | 最初の再配達は無料にし、繰り返し不在の人から | THREE_h(RV-09,RV-15,RV-19) | なし |
| 第6文 | 営業所が近くて受け取り方を選べる僕の言い分かもしれない | IDなし(PROVENANCE_04は偽陽性と判断)。THREE_e(RV-42=S19)の趣旨 | **趣旨が小町(RV-42)** |

V3が公平感(RV-11・RV-40・RV-41)、「営業所が近い人の言い分」への引け目(RV-42)、有料化で受け取り方が変わる実感(RV-46)を小町から取っていることは`PERSONAS_05.md` 100行に明記されている。

## 3. 逐語転載の照合(c)

方法(今回の独自照合。LLM不使用): 正規化(空白・句読点・括弧除去)後の**連続10字**の一致を、(i)小町16件の逐語抜粋(`VOICES_02.json` `quotes`)、(ii)ローカル保存の小町原文6ページ、に対し、Y関連成果物のテキスト 2,411 ファイル(`er121_output/family_y_production_01/**`のjson・md、`er110_output/family_y_opinion_based_03/**`、`user_test/family_y*/**`のhtml・json、`final_human_report/Y/**`)で検索。
| 照合 | 結果 |
|---|---|
| (i) 抜粋 vs 成果物本文 | 一致は `RV-42`「営業所が近い人の言い分」(12字相当)が `er110_output/.../run_01/state.json`(出典メモ、Gateの内部note)に1件のみ。**article_ja.md・公開ページ・音声原稿には一致なし**(公開ページのV3は「営業所が近くて、受け取り方を選べる僕の言い分かもしれない」で、連続10字は一致しない近似) |
| (ii) 原文6ページ vs 成果物 | 一致は一般的な定型句(例:「ことがあります」「不在票が入っていた」級)のみで、小町の投稿の特定文の転載は0 |
| 既存の機械チェック(参照) | `RIGHTS_CHECK_01.md` 2.の表: R0 vs 出典153ファイル(小町6ページ含む)で**日本語20字以上の連続一致0件**(`rights_check_phase0.json`)。12字で4件ヒットしたが短い一般表現 |
| 判定 | **逐語転載なし**。ただし小町の意見(宅配ボックスがあるので再配達はほとんど出ない/営業所が近い人の言い分/払って当然)の趣旨を言い換えた一文がV3に残っている=**素材としての利用は発生**。小町規約(第7条:生成AI等の学習・開発、営利目的の利用の禁止、`DOMESTIC_SOURCES_01.md` §0)の「利用」にあたるかは法的解釈を含み、本書は判断しない |

限界: 10字の連続一致は言い換え(要約・翻案)を検出しない。意見の趣旨が残っているか否かは、PROVENANCE_04.md(agent目視)と`PERSONAS_05.md`の記載に依拠した。

## 4. 影響判定(Fable判断用)

| 成果物群 | 判定 | 根拠 |
|---|---|---|
| 調査記録(§1 #1〜4,7,8) | **影響あり(記録のみ)**・削除不要 | 小町を読んだ事実の記録。ユーザー決定①は「今後の制作に利用しない」「再利用しない」で、記録の削除までは求めていない。原文ページ(#8)はgit管理外 |
| Persona・Theme Package(#5,6,9) | **影響あり** | V3の経験欄4スロット(THREE_a/d/e/i)の根拠に小町。`redelivery_fee_reuse_01.json`が固定参照して再実行すると再投入される |
| Trial/評価run(#10〜12) | **影響あり(再利用しない対象)** | V3原稿にRV-40・41・42・54の趣旨 |
| 限定共有ページ(#13,14) | **影響あり(公開されている)** | 小町由来の言い回し。逐語転載ではない |
| 他のFamily Yテーマ(`sns_age_limit`) | **影響なし** | 小町の記述0件。出典はTBS記事・みらい議会等(`OPINION_BASED_01`) |
| 公開(Landing・一覧)への掲載 | **不明→確認できず** | 一覧へのリンクは見つからず、公開ページのみ限定共有。Landing表示の最終状態はこの範囲で未検証 |

## 5. 対応案(Fable判断用。実行は本委任の範囲外)

| 案 | 内容 | 費用 | 備考 |
|---|---|---|---|
| A. 記録のみ | 本書を根拠に、台帳(DECISION_LOG・OPEN_ITEMS)へ「V3(RV-40・41・42・46・54)の小町由来、逐語転載なし、再利用しない」と記載。既存成果物は据え置き | API 0・0円 | ユーザー決定①の「再利用しない」を、`redelivery_fee_reuse_01.json`の将来の再実行禁止として記録する運用が必要(manifestは変更しない) |
| B. 再実行の凍結 | `redelivery_fee`の再実行をFableが指示するまで止める運用注記(コードは変更しない) | 0円 | Aに付随。Production code変更なし |
| C. 限定共有ページの非公開化 | `user_test/family_y_production_redelivery_fee_01〜03`・`family_y_redelivery_audio_01`の非公開化(git rm等) | API 0。作業のみ(docs/git) | **ユーザー決定①「既存成果物を無断で変更・削除しない」に該当するため、実施前にユーザー明示判断が必要**。GitHub Pagesの履歴・キャッシュは残る |
| D. V3のみ小町なしで再制作 | V3の経験欄4スロットを、小町以外(02Aで条件付きのガルちゃん等)の実投稿で組み直し、V3のR0を再生成→Gate→翻訳・音声を全工程で再実行 | 目安: Voice R0生成のみ約13円(`BUDGET_LOG_OB_05.md` 11行)、Y完成版の1記事分のProduction run実績は 32.1円(`er121_output/family_y_production_01/redelivery_fee/run_01/cost_by_stage.json`)・82.7円(`sns_age_limit/run_01`)。合計で数十円〜100円弱+Opus等レビュー別 | 同じ素材集合は知恵袋38件にも依存(02A暫定=利用不可)。V3だけ直してもV1・V2の根拠(知恵袋・個人ブログ・新聞読者投稿)は別問題。新Scope=Fable判断 |
| E. 同テーマを廃止し新テーマへ | 再配達テーマ全体を終了し、新5テーマ(`THEME_SHORTLIST_01.md`)に注力 | 新テーマ1件あたり約30〜90円(上記実績の幅) | ユーザー原文§1は新テーマの選定へ進む前提。既存ページの扱いはCと同じ |

推奨(調査者の私見。決定はFable/ユーザー): まずA+Bを即時、Cの要否はユーザー判断、Dは行わずEへ進む(Dは知恵袋依存が残り費用対効果が低い)。

## 6. 未確認・限界

1. 公開ページ`_01〜_03`の差分で、小町由来の言い回しの変化は未比較(全て同じV3を含む)。
2. `er121_output`のrunのうち、`run_tru_ev_*`系(約25 run)でV3文字列が検出されなかった理由(別版の本文を使ったか)は未調査。
3. 原文6ページのうち、S19〜S21以外の3ページ(`komachi.yomiuri.co.jp_*.txt`)がどのトピックか、本書では未確認。Persona・原稿への反映はRV-IDでのみ追跡した。
4. 10字連続一致の照合は言い換えを検出できない。趣旨の残存はPROVENANCE_04.md・PERSONAS_05.mdの記載に依拠した。
