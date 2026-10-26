# IDIOM_LEXICON_01: 慣用句辞書(vendoring)の出典・件数・ライセンス・sha・取得手順

管理ID: KP-GATE-EXCLUSION-RESCUE-PRODUCTION-WIRING-01 委任_01 / 2026-10-26 / API費用0(Wikimedia公開API)

| 項目 | 値 |
|---|---|
| 出典 | English Wiktionary `Category:English idioms`(ns=0のタイトルのみ。本文・定義・例文は取得していない) |
| 取得日時 | 2026-10-26T09:01:12Z(UTC)。22 API call(`action=query&list=categorymembers`、User-Agent明記、逐次、429時は待って最大5回) |
| 件数 | 10,674見出し(`idioms.txt`、173,780 byte) / 正規化後10,671 / 除外表適用後10,661 |
| sha256 | `idioms.txt` = `5ec8f3aee57745064cbf53d6ab23fa20979a743e1dcb1f1300845bc1439327c1`(行をLF連結+末尾LF。CRLF checkoutはloaderが吸収) / `denylist.txt`(コメント除く10行) = `a8bb01599d69228fe22f5fdebf3a119c3b8cfdf20dfc881085853fa37dc7ca69` |
| 固定の仕方 | `er125_kp_rescue_production_01.py`の定数(`LEXICON_SHA256`/`DENYLIST_SHA256`)と`meta.json`の二重ピン。不一致/欠落/件数不一致/除外表欠落=空表(例外なし=fail-closed、例外は送出せずwarning log) |
| ライセンス | Wiktionary本文はCC BY-SA 4.0(+GFDL)。保存するのは見出し(語句)のみ。`data/kp_idiom_lexicon_01/ATTRIBUTION.md`に出典・ライセンス・取得方法・利用範囲(内部照合のみ・学習者向け出力に辞書内容は出さない)を同梱。外部公開する複合成果物に辞書そのものを含める場合はShareAlike(帰属ファイルを同梱) |
| 前回snapshotとの差 | Trial snapshot(2026-09-27、10,632件、sha `79956b90...`)から 削除13・追加55。旧27件閉表の27件はすべて新辞書でも一致 |
| 対象範囲 | idiomsのみ。proverbs(名詞主語の完全文)は入れない(Opus M3)。句動詞は既存の原形化経路で足りるため入れない |

## 使い方(runtime)と効く範囲
- 例外が判断を変えるのは、現行の有限助動詞guard(`contains_finite_aux_role_based`)が実際に拒否する句だけ。辞書10,661見出しのうち構造条件に合うのは116、そのうち**例外で判断が変わるのは25件**(curly引用符の縮約形を含む)。全件=`idiom_exception_listing_01.json`(`effective_where_exception_changes_decision`)。
- 25件: `can of corn / can of worms / can't get enough / can't help / can't stand / can't stand the sight of / can't wait / come what may / could not get elected dogcatcher / had better / have been around / have done with / have had it / have it all / have it both ways / have it coming / have it made / have it your way / have one's ears pinned back / have one's hands tied / have one's head read / have seen one's day / it can't be helped(核 can't be helped) / may as well / might as well`。
- 除外表(denylist.txt 10件。旧レビューの除外理由に対応): `would give a jew's eye`(侮蔑)、`has left the building`(出来事特定の決まり文句)、`have fingers made of lime-twigs`(方言/古風)、`have had one's chips`/`have it going on`/`have it large`/`have one's ears lowered`/`have one's name taken`/`have one's wig snatched`/`have seen this movie`(スラング)。
- 構造条件で自動的に除外される代表(辞書には載っている): `beggars can't be choosers`/`the die is cast`/`it is what it is`(名詞主語・be系の完全文)、`are you deaf`/`wouldn't you say`(倒置疑問文)、`can it`/`have got`/`will do`(中身語なしの断片)、`what can i say`(wh疑問節)、`you can't be serious`(主語付き節)。

## 取得・更新手順
1. `py data/kp_idiom_lexicon_01/fetch_wiktionary_idioms_01.py`(出力先既定=同dir。`--out-dir`で別dirへ試行可)。
2. 旧`idioms.txt`との差(追加/削除)を確認し、構造条件に合う追加見出し(`idiom_exception`で例外になるもの)を人が確認。スラング/侮蔑があれば`denylist.txt`へ追加しsha更新。
3. `LEXICON_SHA256`(と必要なら`DENYLIST_SHA256`)を`er125_kp_rescue_production_01.py`で更新し、`er125_kp_rescue_production_test_01.py`・`er105_kp_rule_compliance_test_01.py`を再実行。
自動では広がらない(実行時にネットワークへ出ない)。

## 本委任での再現確認
取得scriptはscratchpadへの試行(HTTP 429を1回受け、backoff追加後に成功)で再現済み。vendoringした`idioms.txt`はその成功出力そのもの。
