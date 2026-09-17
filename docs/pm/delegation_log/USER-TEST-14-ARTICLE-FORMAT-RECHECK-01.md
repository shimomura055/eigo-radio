## 管理ID

`USER-TEST-14-ARTICLE-FORMAT-RECHECK-01`。報告は`docs/pm/RESULT_PACKET_14_ARTICLE_FORMAT_RECHECK_01.md`(新規、★★★★報告ここから/ここまで)。一時ファイル`docs/pm/ACTIVE_TASK_14_ARTICLE_RECHECK_01.md`。現在main=origin/main=`74298923`(要fetch確認)。**並行Agentなし。API 0、音声再生成0、記事本文変更0。** 到達Status=`VERIFIED`または`FIXED_AND_VERIFIED`(新仕様Trialではない)。

## 目的

ユーザー管理のGoogle Sheet「ユーザーテスト記事一覧_2026-09-16」に掲載中の**14記事のみ**を対象に、視聴ページの表示フォーマット(PM_GOVERNANCE Gate 7(n)、2026-09-17ユーザー正式決定)を実ブラウザで再確認し、軽微な表示不整合は修正する。**Sheet自体はrepoに存在せずAPIアクセス手段も無い**ため、Sheetのリンク整合(PC用「記事一覧」タブ/スマホ用タブ)はFable/ユーザー側で扱う。本タスクは(a)各記事の最新登録URL(ARTIFACT_REGISTRY等)を特定→(b)5項目E2E→(c)Sheetへ貼れる最新URL表を作る、まで。

## 対象14記事(タイトルはSheet表記。repo内の該当記事dir/URLはARTIFACT_REGISTRY.md・DECISION_LOG・`er0*_output/**/player.html`/`web/index.html`をGrep/Globで特定し、対応表を報告)

1. AI Beyond the Smartphone 2. Why Young Travelers Are Slowing Down 3. How Often Should You Wash Towels? 4. Why We Wake Before the Alarm 5. Why the Crisper Drawer Is at the Bottom 6. Free-Address or Assigned Desks? 7. Personalized News: Useful or Narrowing? 8. When AI Helps Choose Who Gets Hired 9. Home Robots: What They May Change 10. How Technology May Change Memory 11. Digital Twins: A Copy of the Real World 12. AI in the Convenience-Store Kitchen 13. Are Tiny Bags Really Back? 14. Weapons in Orbit: What Has Actually Changed?

各記事についてStandard(A2)/Advanced(B1)の**存在有無**を確定(`USER_TEST_READY`のもののみ。Statusが対象外のlevelは「—」)。**Personalized News**: Standard(A2新版)=USER_TEST_READY、Advanced(B1)=対象外(OPEN-166、旧B1を再掲載しない・再生成しない)→Advanced「—」を正とする。

## 確認項目(各ページ、Browser E2E。`docs/pm/tools/user_test_page_e2e_check.py`を使用。unified.html以外の形式[Family A/Cのweb export等]はチェッカーを拡張して同じ5項目をDOM assertionで判定。拡張はチェッカー内で形式自動判別、既存9本の判定は不変)

1. level表示: A2/B1/B1B表記を出さない、Standard/Advancedを使用
2. Key Phrases: `English:`/`英語:`/`EN:`/`日本語:`/`日本語gloss:`/`JA:`等ラベル不在、英語|日本語2列
3. 再生: Play開始・currentTime進行・audio errorなし
4. 本文: script/Key Phrases/Comment表示、表示崩れなし(screenshot保存)
5. (Sheet整合はスコープ外。代わりに)各記事の**最新URL**(最新SHAのunified.html経由、または該当形式の最新ページ)を確定。旧SHAのURLしか登録されていない記事は最新mainのSHAでURLを再構成して検証。

## 修正方針

表示上の軽微な不整合で既存承認済みルールに明確に反するもの(例: ヘッダーのA2/B1生表示、Key Phraseラベル)は修正してよい: 対象は**14記事のページ/テンプレートのみ**。`user_test/unified.html`は最新版で適合済み(変更不要想定)。Family A/C等が独自テンプレート(`web/index.html`生成スクリプト)を使う場合は、そのテンプレートのlevel表示ラベル・Key Phrase描画のみ修正し、対象14記事のページを再生成(音声・script・Key Phrase内容は不変。episode.mp3/segments sha256不変を証跡化)。**禁止**: 音声再生成、記事本文変更、新Product仕様追加、14記事以外のLegacy修正(A02/ADD03/hanshin/health等は対象外、不適合を見ても修正せず「対象外参考情報」として一言報告のみ)、OPEN ItemのProduction化、PN B1再生成。unified.html経由の記事は、ページ再生成なしでも最新SHA URLで適合するはず(確認)。

## STOP条件(該当時のみSTOP報告、他は修正→検証まで進める)
表示修正だけでは直らない問題/音声再生成が必要/記事本文変更が必要/現行Statusと一覧内容の重大矛盾(例: USER_TEST_READYでない記事がSheetに載っている疑い)/新Product仕様判断が必要/git conflict。

## SSOT/Git
`DECISION_LOG.md`: `## USER-TEST-14-ARTICLE-FORMAT-RECHECK-01`(索引+本体): 14記事対応表、確認結果、修正一覧、Status(VERIFIED/FIXED_AND_VERIFIED)。`ARTIFACT_REGISTRY.md`: 対象記事の最新URLを更新(旧SHAの行は最新へ)。`OPEN_ITEMS.md`: 変更なし想定(新規問題があれば登録、`USER_DECISION_REQUIRED`にはしない)。`CURRENT_SPEC.md`/`PM_GOVERNANCE.md`: 変更なし想定(チェッカー拡張は`docs/pm/tools/`内のみ、Gate 7(n)の文言にツール適用範囲を1行追記する場合のみPM_GOVERNANCE変更可)。Git: 明示add、`git add -A`禁止、wav禁止、mp3差分なし確認、fetch→merge、trailer `Task-ID: USER-TEST-14-ARTICLE-FORMAT-RECHECK-01`。commit分割可(テンプレ修正+ページ再生成 → SSOT+evidence)。

T-0: 委任文を`docs/pm/delegation_log/USER-TEST-14-ARTICLE-FORMAT-RECHECK-01.md`へ保存し`.venv\Scripts\python.exe docs\pm\tools\check_delegation_prompt.py --file <path> --json-out <path>_check.json`、結果1行記録(FAILでも継続)。事前指定Read: `ARTIFACT_REGISTRY.md`全体(記事→URL対応)、`docs/pm/tools/user_test_page_e2e_check.py`、`docs/pm/closeout_136_e2e/format_rule_01/urls.txt`、`user_test/unified.html`(形式確認)、各対象記事のplayer/web/index.html(ヘッダー・Key Phrase部分)、該当web生成スクリプト(Family A/C等)、PM_GOVERNANCE Gate 7(n)。事前指定外Readは理由付き報告。

## 報告項目(★ブロック内)
1.14記事すべての確認結果(記事×Standard/Advanced×5項目の表) 2.各記事のStandard/Advanced存在有無(repo内dir・Status根拠) 3.実際に確認した視聴ページ総数 4.Key Phrase表示PASS/FAIL 5.Standard/Advanced表示PASS/FAIL 6.Play/currentTime PASS/FAIL 7.script/KP/Comment表示PASS/FAIL 8.Sheet整合=スコープ外の明記+**Sheet貼付用の最新URL表**(記事名/Standard URL/Advanced URL、旧SHAから変わったものに印) 9.修正したページ/テンプレート一覧(before/after要旨) 10.音声変更の有無(sha256証跡) 11.14記事以外は未変更であること(`git diff --stat`の範囲証跡)+対象外参考情報(あれば一言) 12.未処理USER_DECISION_REQUIRED有無 13.到達Status 14.Git SHA 15.ユーザー判断 A/B(想定: なし) 16.事前指定外Read。
