# CONFIRMATION_CHECK_01 ユーザー確定20件の元データ照合(AI-ISLAND-FORM-PRODUCTION-01 委任_02、fail-closed)

機械生成: `docs/research/AI-ISLAND-FORM-PRODUCTION-01/tools/verify_user_confirm_aif2.py`(API 0)。ユーザー確定値=`docs/pm/delegation_log/2026-10-27_AI-ISLAND-FORM-PRODUCTION-01_USER_02.md` §2/§3の逐語転記。


## a2 (Standard)

### SHA照合

| 項目 | ユーザー値 | 照合先 | 照合先の値 | 結果 |
|---|---|---|---|---|
| 本文SHA256 | `76f80f62120b…` | 候補doc `text_sha256` | `76f80f62120b…` | OK |
| 本文SHA256 | `76f80f62120b…` | フォームデータ `source.text_sha256` | `76f80f62120b…` | OK |
| 本文SHA256 | `76f80f62120b…` | article.mdをLF正規化→空行区切り段落をstrip→`\n\n`連結(タイトル行・In one line節を含む全10段落)のSHA256 | `76f80f62120b…` | OK |
| 候補集合SHA256 | `25a7bce9357c…` | 候補doc `candidates_sha256` | `25a7bce9357c…` | OK |
| 候補集合SHA256 | `25a7bce9357c…` | フォームデータ `candidates_sha256` | `25a7bce9357c…` | OK |

参考(別基準・一致しなくてよい): article.md 生bytes SHA256=`90c66293dfb1…`(委任_01報告の値)。ユーザー値は生bytesではなく上記『正規化本文』基準のSHA(候補doc `text_sha256`と同一基準)。文法事前生成docの`text_sha256`は本文8段落(タイトル・In one line節を除く)基準で別値のため混同しない。

### 10件の逐語照合(区分・英語・日本語訳・candidate_id)

| 区分 | 英語(used_form) | ユーザー確定日本語訳 | candidate_id | 候補doc used_form | 候補doc japanese_gloss | form data term / ja_gloss / status | 本文の表層形 | 結果 |
|---|---|---|---|---|---|---|---|---|
| ①Key Phrase | carry over | 持ち越す | p_1a2370a6af | carry over | 持ち越す | carry over / 持ち越す / official | carried over(在) | OK |
| ①Key Phrase | take a detour | 寄り道をする | p_1473453d19 | take a detour | 寄り道をする | take a detour / 寄り道をする / official | taken a detour(在) | OK |
| ①Key Phrase | card to play | 使える手 | p_289a665236 | card to play | 使える手 | card to play / 使える手 / official | card to play(在) | OK |
| ②追加解説 | worth paying attention to | 注目する価値がある | p_1cf1329364 | worth paying attention to | 注目する価値がある | worth paying attention to / 注目する価値がある / official | worth paying attention to(在) | OK |
| ②追加解説 | obstacle | 障害物 | p_d17f8079e3 | obstacle | 障害物 | obstacle / 障害物 / official | obstacle(在) | OK |
| ③本文意味表示 | make a difference | 影響を与える | p_801113c17d | make a difference | 影響を与える | make a difference / 影響を与える / official | made a difference(在) | OK |
| ③本文意味表示 | separately | 個別に | p_dc8803926c | separately | 個別に | separately / 個別に / official | separately(在) | OK |
| ③本文意味表示 | feature | 性質 | p_4b7615dce5 | feature | 性質 | feature / 性質 / official | feature(在) | OK |
| ③本文意味表示 | Strategy | 作戦 | p_31e10e6357 | Strategy | 作戦 | Strategy / 作戦 / official | Strategy(在) | OK |
| ③本文意味表示 | setup | 設定 | p_80437a44a6 | setup | 設定 | setup / 設定 / official | setup(在) | OK |

件数10(①3/②2/③5)・candidate_id重複なし: OK/OK。候補doc全体=10件(ユーザー確定10件が全候補)。


## b1b (Advanced)

### SHA照合

| 項目 | ユーザー値 | 照合先 | 照合先の値 | 結果 |
|---|---|---|---|---|
| 本文SHA256 | `00f14092c072…` | 候補doc `text_sha256` | `00f14092c072…` | OK |
| 本文SHA256 | `00f14092c072…` | フォームデータ `source.text_sha256` | `00f14092c072…` | OK |
| 本文SHA256 | `00f14092c072…` | article.mdをLF正規化→空行区切り段落をstrip→`\n\n`連結(タイトル行・In one line節を含む全10段落)のSHA256 | `00f14092c072…` | OK |
| 候補集合SHA256 | `5d8c1b12f01b…` | 候補doc `candidates_sha256` | `5d8c1b12f01b…` | OK |
| 候補集合SHA256 | `5d8c1b12f01b…` | フォームデータ `candidates_sha256` | `5d8c1b12f01b…` | OK |

参考(別基準・一致しなくてよい): article.md 生bytes SHA256=`a2951b9bdf7a…`(委任_01報告の値)。ユーザー値は生bytesではなく上記『正規化本文』基準のSHA(候補doc `text_sha256`と同一基準)。文法事前生成docの`text_sha256`は本文8段落(タイトル・In one line節を除く)基準で別値のため混同しない。

### 10件の逐語照合(区分・英語・日本語訳・candidate_id)

| 区分 | 英語(used_form) | ユーザー確定日本語訳 | candidate_id | 候補doc used_form | 候補doc japanese_gloss | form data term / ja_gloss / status | 本文の表層形 | 結果 |
|---|---|---|---|---|---|---|---|---|
| ①Key Phrase | carry over | 次に持ち越す | p_1a2370a6af | carry over | 次に持ち越す | carry over / 次に持ち越す / official | carried over(在) | OK |
| ①Key Phrase | call on | 頼む | p_ad091fb295 | call on | 頼む | call on / 頼む / official | called on(在) | OK |
| ①Key Phrase | take a detour | 遠回りをする | p_1473453d19 | take a detour | 遠回りをする | take a detour / 遠回りをする / official | taken a detour(在) | OK |
| ②追加解説 | card to play | 打てる手 | p_289a665236 | card to play | 打てる手 | card to play / 打てる手 / official | card to play(在) | OK |
| ②追加解説 | obstacle | 障害物 | p_d17f8079e3 | obstacle | 障害物 | obstacle / 障害物 / official | obstacle(在) | OK |
| ③本文意味表示 | look at separately | 別々に検討する | p_8f3df24cb8 | look at separately | 別々に検討する | look at separately / 別々に検討する / official | looked at separately(在) | OK |
| ③本文意味表示 | exploration | いろいろ探ること | p_0d5feb1964 | exploration | いろいろ探ること | exploration / いろいろ探ること / official | exploration(在) | OK |
| ③本文意味表示 | technique | やり方 | p_b41c6aff6d | technique | やり方 | technique / やり方 / official | technique(在) | OK |
| ③本文意味表示 | overlook | 見過ごす | p_1b8ee344f0 | overlook | 見過ごす | overlook / 見過ごす / official | overlook(在) | OK |
| ③本文意味表示 | erase | 消し去る | p_4513a423ab | erase | 消し去る | erase / 消し去る / official | erased(在) | OK |

件数10(①3/②2/③5)・candidate_id重複なし: OK/OK。候補doc全体=10件(ユーザー確定10件が全候補)。


## 判定

不一致 0件。ユーザー確定20件は、候補doc・フォームデータ・承認済み本文と逐語一致(英語・訳・区分・candidate_id・kind・official・SHA)。ユーザー確定の日本語訳と候補docの`japanese_gloss`は全件一致のため、ユーザー値を上書き・不採用にした項目は0件。

