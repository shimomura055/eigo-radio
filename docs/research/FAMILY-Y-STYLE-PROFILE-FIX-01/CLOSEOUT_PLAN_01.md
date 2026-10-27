# CLOSEOUT_PLAN_01 — Voice説明文の正式文言への整合(棚卸し+計画、委任_07)
承認文言(USER_04 §1-B): 「Voice 1〜3は実在人物の発言をそのまま再現したものではなく、実際に投稿された意見をもとに、AIが編集・再構成したものです。」

## 1. 旧文言の所在(origin/main Grep `実在する人々|実在人物|AIが編集・構成|AIが編集した意見|y-ai-notice|PAGE_NOTICE`)
| 場所 | 内容 | 区分 | 担当 |
|---|---|---|---|
| `er121_family_y_structure_01.py:100` `PAGE_NOTICE_JA`(旧文言「本コンテンツのVoiceは、実在する人々の意見を参考に、AIが編集・構成したものであり…」)、`:101 PAGE_NOTICE_CLASS="y-ai-notice"`、`:111`(notice div生成)、`:333/340/343`(検査) | **Production template(単一ソース)** | Production | 委任_08 |
| `er110_family_y_redelivery_revision_01.py:39` `PAGE_NOTICE_JA`(DEV Trial旧文言) | DEV/Trial。Productionは`er121_..._structure_01`を使用 | DEV | 委任_08で同期するか凍結注記(要判断: 凍結でよい) |
| test: `er121_family_y_text_core_article_test_01.py:988-1000`(旧文言と`rev.PAGE_NOTICE_JA`/`ys.PAGE_NOTICE_JA`の一致をassert)、`er121_family_y_runner_01_test_01.py:262-263`(class数)、`er121_family_y_structure_match_test_01.py:267` | 旧文言をassertする旧test | Production test | 委任_08で承認文言へ更新(旧文言のassertを残すと不整合な期待値になる) |
| `docs/research/FAMILY-Y-STYLE-PROFILE-FIX-01/tools/build_page_04.py:43`(「Voice 1〜3は実在人物の発言ではなく、AIが編集した意見です。」、制作情報節) | research tool(`_03`生成済み・再実行不可) | research | 本委任: 凍結。`_03`は`build_page_05.py`で修正済 |
| `docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/EXISTING_SPEC_CHECK_01.md:13`、`FAMILY-Y-VOICES-DESIGN-01/REDELIVERY_REVISION_01/REVISION_SCRIPT_01.md:19` | 設計docの旧文言(履歴) | 履歴 | 変更しない(履歴)。CURRENT_SPECに正式文言を追記(RESULT_PACKET §8) |
| `user_test/family_y_production_redelivery_fee_03/index.html`・`preview_segments_01.html` | 公開ページ | 公開 | **本委任で修正済**(VERIFY_05.md) |
| `user_test/family_y_*`の他ページ(`_01`/`_02`等の旧公開) | 旧版 | 旧版 | 履歴として変更せず(旧版承認扱い)。要否はFable判断 |
| `CURRENT_SPEC.md`(Y設計) / `DECISION_LOG.md` | 旧文言の正式記述は`YL-C07`相当(structure_01:13) | SSOT | RESULT_PACKET §8の文案をFableが反映 |

`user_test/`配下を他に確認: `git grep -l 実在する人々 origin/main -- user_test` で`_03`系以外の旧版が残る可能性(未確認)。

## 2. 「根拠のない出典主張を生成しない」条件(判定条件の確認)
- Y Productionは`--theme-package`必須(`er121_family_y_runner_01.py:328`「実在意見ベースの入力」)。Theme Packageの各Voice`experiences[].source_ids`(例: RV-55/RV-56、`OPINION_BASED_02/THEME_DATA_02.json`)で実投稿への対応が機械可読。`validate_theme_package`(`er121_family_y_text_core_01.py:1132`)が検査経路。
- よって『実投稿に基づく記事のみに注意書きを出す』判定は **全Voiceの全experienceに非空`source_ids`がある場合のみ承認文言を出し、無い場合は注意書きを出さずSTOP(または旧来の汎用文言を出さない)** とする実装が可能。現行は無条件に出力(Theme Package必須なので実質同条件)。委任_08で`structure_01`のnotice生成に上記条件のassertを追加することを推奨(新仕様ではなく承認文言(「根拠のない出典主張を生成しない」)の実装)。

## 3. 将来アプリ向け
アプリ表示でも同一文言(USER_04 §1-B)。文言の単一ソース=`er121_family_y_structure_01.py:PAGE_NOTICE_JA`とし、アプリ側は定数を参照する設計を仕様として記録(アプリ開発は範囲外)。

## 4. 委任_08への引継ぎ(Voice説明文)
(a) `structure_01.py:100`を承認文言へ、(b)上記test 3件更新、(c)`er110_*:39`の扱い、(d)旧文言残存Grep=0(履歴docを除く)、(e)source_ids条件assert。
