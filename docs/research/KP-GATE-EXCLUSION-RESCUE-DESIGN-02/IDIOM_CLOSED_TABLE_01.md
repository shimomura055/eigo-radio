# IDIOM_CLOSED_TABLE_01: 慣用句の法助動詞/助動詞例外(M3)のレビュー済み閉表

管理ID: KP-GATE-EXCLUSION-RESCUE-DESIGN-02 委任_02 / 2026-10-26。実体=`idiom_closed_table_01.json`(`entries`のsha256=`0fb89833d0e0548102b758bad1af15a6fc3fffe866cdd27c86dec4c21cefa3aa`を`er123_kp_rescue_dev_01.py`の定数`IDIOM_TABLE_SHA256`に固定。不一致なら空表=例外なし=fail-closed)。DEV用(Production非配線)。

## 1. 目的と条件(Opus M3)
- 旧設計(委任_01)は『Wiktionaryの慣用句見出し(17,389件)に一致すれば助動詞検査を丸ごと外す』で、主語判定は代名詞しか見ず、**名詞主語のことわざ・完全文**(`beggars can't be choosers`/`boys will be boys`/`time is money`/`the die is cast`/`a leopard can't change its spots`)を通した(`old_vs_new_02.json`で再現: 旧実装は5/5を通す、新実装は0/5)。
- 新設計: 例外は **(1)idioms由来(proverbs/phrasal verbsは不使用) (2)先頭語が法助動詞/助動詞(縮約形can't等を含む=主語の無い述部) (3)5語以内 (4)人手レビューで採用した句** に限る閉表(27件)だけ。実行時に外部辞書(17,389件)を照会しない。句の全体一致(所有格my/our/his等→one's、has/had→haveを正規化)で、先頭が助動詞でない句は閉表に載せても照会しない。
- 機械抽出(`build_idiom_candidates`)で53候補 → レビューで27件採用・26件除外。採用/除外の全件を下に列挙(件数・サンプルではなく全件)。

## 2. 採用(27件)
| # | 句 | 備考 |
|---|---|---|
| 1 | `can of corn` | 名詞can(助動詞ではない語形) |
| 2 | `can of worms` | 名詞can。高価値の慣用句 |
| 3 | `can't be helped` | 『it can't be helped』の主語を除いた核 |
| 4 | `can't get enough` |  |
| 5 | `can't help` |  |
| 6 | `can't stand` |  |
| 7 | `can't stand the sight of` |  |
| 8 | `can't wait` |  |
| 9 | `could not get elected dogcatcher` |  |
| 10 | `couldn't be more different` |  |
| 11 | `couldn't care less` |  |
| 12 | `had better` | 助動詞連語(学習文法項目) |
| 13 | `have been around` |  |
| 14 | `have done with` |  |
| 15 | `have had it` |  |
| 16 | `have it all` |  |
| 17 | `have it both ways` |  |
| 18 | `have it coming` |  |
| 19 | `have it made` |  |
| 20 | `have it your way` |  |
| 21 | `have one's ears pinned back` |  |
| 22 | `have one's hands tied` |  |
| 23 | `have one's head read` |  |
| 24 | `have seen one's day` |  |
| 25 | `may as well` | 高価値 |
| 26 | `might as well` | 高価値 |
| 27 | `wouldn't be seen dead` |  |

## 3. 除外(26件。機械抽出されたがレビューで不採用)
| 句 | 由来 | 除外理由 |
|---|---|---|
| `are bears catholic` | title | 完全文/疑問文(主語を持つ節) |
| `are you deaf` | title | 完全文/疑問文(主語を持つ節) |
| `are your ears burning` | title | 完全文/疑問文(主語を持つ節) |
| `can it` | title | 語彙動詞can等の曖昧/断片(単独では学習単位でない) |
| `couldn't happen to a nicer` | title | 主語(there等)を要する構文の核/語数・未完 |
| `has left the building` | title | スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外) |
| `have` | title | 語彙動詞can等の曖昧/断片(単独では学習単位でない) |
| `have fingers made of lime-twigs` | title | スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外) |
| `have got` | title | 語彙動詞can等の曖昧/断片(単独では学習単位でない) |
| `have had one's chips` | title | スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外) |
| `have it going on` | title | スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外) |
| `have it in one` | title | 語彙動詞can等の曖昧/断片(単独では学習単位でない) |
| `have it large` | title | スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外) |
| `have one's ears lowered` | title | スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外) |
| `have one's name taken` | title | スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外) |
| `have one's wig snatched` | title | スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外) |
| `have seen this movie` | title | スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外) |
| `is a bear catholic` | title | 完全文/疑問文(主語を持つ節) |
| `is no telling` | core_of:there is no telling | 主語(there等)を要する構文の核/語数・未完 |
| `is no there there` | core_of:there is no there there | 主語(there等)を要する構文の核/語数・未完 |
| `is what it is` | core_of:it is what it is | 完全文/疑問文(主語を持つ節) |
| `will do` | core_of:that will do | 語彙動詞can等の曖昧/断片(単独では学習単位でない) |
| `would` | title | 語彙動詞can等の曖昧/断片(単独では学習単位でない) |
| `would give a jew's eye` | title | スラング/方言/侮蔑的/古風で学習価値が低い(レビューで除外) |
| `wouldn't you know` | title | 完全文/疑問文(主語を持つ節) |
| `wouldn't you say` | title | 完全文/疑問文(主語を持つ節) |

## 4. 出典・スナップショット・ライセンス(ユーザー判断材料)
- `er023_output/key_phrase_db_trial_01/db/wiktionary/idioms.json`: sha256=`79956b90bf29df26710d1cbf1afcf1ddb6a871603e751b8446767a6db7793cff` / Category:English idioms / 10632見出し / 表の抽出に使用=True
- `er023_output/key_phrase_db_trial_01/db/wiktionary/phrasal_verbs.json`: sha256=`b727414f07da9f83fb78c1e11abc99ad92270f3898043a21816a9548f4b9a98e` / Category:English phrasal verbs / 5169見出し / 表の抽出に使用=False
- `er023_output/key_phrase_db_trial_01/db/wiktionary/proverbs.json`: sha256=`e956df28520ad9675ba7c70ca18b4d4ced1142eb3d075ae9575ba2e65d029b31` / Category:English proverbs / 1588見出し / 表の抽出に使用=False
- 表に取り込むのは**見出し(語句)のみ**で、Wiktionaryの本文・定義・例文は含まない。Wiktionaryの本文は CC BY-SA 4.0 (+GFDL) で、repo内の`db_licenses.md`にも同記載。
- **確認条件(ユーザー/法務判断)**: (a)語句の列挙(短い見出し27件)がShareAlikeの継承対象とみなされるか(一般に短い語句の事実的な列挙は著作物性が低いが、法的判断は未確認)。(b)repoが公開かどうかで、継承条件が掛かる範囲が変わる。(c)安全側の運用案: 出典表示ファイル(`THIRD_PARTY_NOTICES`等にWiktionary/CC BY-SA 4.0/取得日/見出しのみ利用を明記)を置く。(d)ライセンスを避けるなら、27件を自前の語彙表として再編(出典は参照のみ)する案もある(件数が小さいため低コスト)。
- 版: 取得時のsnapshotはsha256で固定。更新する場合は表の再生成→再レビュー→`IDIOM_TABLE_SHA256`更新が必要(自動で広がらない)。

## 5. 範囲外の観測(新規仕様候補。実装しない)
- 名詞の`can`(`can of worms`)は閉表で救えるが、`open a can of worms`のように先頭が動詞の句では`can`が名詞でも現行Gateが拒否する(`can`/`may`/`will`/`must`の名詞用法)。役割判定(語彙動詞haveと同型)で是正できる可能性があるが、受理面の変更になるため別委任で測定する案(DESIGN_02 §8)。
