# SOURCE_CHECK_01 (FAMILY-Z-YUKI-ONNA-PRODUCTION-01 委任_01、2026-10-30、API 0)

## 1. 原作
- 作品: 『雪女』= Lafcadio Hearn(小泉八雲) "Yuki-Onna"、『怪談(Kwaidan: Stories and Studies of Strange Things)』(1904)冒頭の一編。**英語原作**(日本の伝承を英語で再話した作品)。日本語訳は使わない(翻訳権の問題を持ち込まない)。
- 原文取得元: Project Gutenberg eBook #1210 `https://www.gutenberg.org/cache/epub/1210/pg1210.txt`(HTTP 200、取得2026-10-30)。全体sha256=`7a65d208d24f0cae80afb1b8ae2787df7f40b331d6d28f4c3eb5166a70928fb2`。
- 抽出範囲: `pg1210.txt`の1729-1878行(見出し`YUKI-ONNA`〜末尾`Never again was she seen.`、次の`THE STORY OF AOYAGI`の前)。保存先: `er026_seeds/yuki_onna/source_gutenberg_raw_extract.txt`(sha256 `49ebdeb2…e785`)、整形版 `story.md`(sha256 `95dba57b…1db`、18段落・約1,467語)、`SOURCE_PROVENANCE.json`。
- story.md の変換: 段落内改行の連結・題名行`### Yuki-Onna`の追加・脚注記号(`(1)`,`[1]`等)/挿絵行/斜体`_`の除去のみ。語の改変なし(testで再導出一致を固定)。

## 2. 権利(法的最終判断ではない。既存4作品と同形式)
- 著者没: 1904-09-26(en.wikipedia.org/wiki/Lafcadio_Hearn)。日本の旧法(死後50年)満了=1954-12-31。連合国民(英国籍出身)と仮定した最も保守的な場合でも戦時加算3,794日で1965-05-21に満了(計算値をtestで固定)。2018年の70年化は遡及しない。→ **日本でパブリックドメイン**。
- 米国: 1904年刊=1931年より前でPD(記録事項)。
- 翻訳を使わないため訳者の没年確認は不要(Hearnの英語原文を直接使用)。第三者の翻案・Wikipedia要約・Web要約は使っていない(`SOURCE_PROVENANCE.json` not_used)。
- rights block: `er026_family_z_fiction_production_runner_01.py` の `YUKI_ONNA_RIGHTS_BLOCK`(既存の`check_rights_gate`をPASS、`legal_use_basis`は開いた窓と同じユーザー決定2026-09-26の逐語転記)。
- ユーザー判断が必要な権利懸念: **なし**(原文§8の「原作上の権利・扱い」STOP条件には非該当)。

## 3. 管理情報(重複防止・カテゴリ分析用)
- 作品名=雪女 / 原作名・英題=Yuki-Onna(Lafcadio Hearn『怪談』1904) / Family=Z / カテゴリー=①ミステリー・サスペンス・ホラー / 軸=**日本題材・英語原作(外国人作者Hearnによる日本の伝承の再話)** / 制作状態=制作中(委任_01=原作確認・Seed・登録・構成案まで)。
- 記録先: 機械可読 `docs/research/FAMILY-Z-YUKI-ONNA-PRODUCTION-01/WORK_RECORD_01.json`、SSOT OPEN-616、DECISION_LOG、ACTIVE_TASK(ZY)。コード上の登録は `STORY_REGISTRY["yuki_onna"]`(`e2e_management_id`=FAMILY-Z-YUKI-ONNA-PRODUCTION-01)。
- 既存の作品横断台帳(カテゴリー/日本・海外軸)は **repo内に存在しない**(`日本題材`/`日本/海外`/`カテゴリー`のGrep結果: 作品台帳としての記録は0件。ヒットはFamily Y Voice設計の無関係な記述のみ)。藪の中・メロス・告げ口心臓等の過去Z作品にもこの2軸のタグは記録されていない。→ 本作は上記4か所に記録。作品横断台帳の新設・過去作の後追い記録は別委任案(OPEN-616に記載、実害なし)。
