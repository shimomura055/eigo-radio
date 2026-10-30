# EVIDENCE_04 (ENDUSER-EN-JA-LINKED-HIGHLIGHT-01 委任_04, 2026-10-30)

目的: Z story 2part(メロスAdv adv_14 25文 / 雪女Std std_11 18文)が生成訳不成立で英語のみだった状態の是正。

## 診断(API 0)
| 項目 | メロスadv_14 | 雪女std_11 |
|---|---|---|
| 該当英文 | adv_14-s062 "They held each other as the last sunlight touched the walls." | std_11-s013 "A woman in white bent over his master." |
| 旧訳 | 『城壁』を含む訳(旧生成訳は不成立のため非保存=失敗は非キャッシュの仕様。再現不能) | 『着物』を含む訳(同左) |
| NG理由(build_info記録) | verify_ng: walls は「壁」であり「城壁」は英文にない情報を加えている | verify_ng: 英文にない「着物」を追加している |
| 判定 | **真のNG(偽NGではない)** [確認済み] | **真のNG** [確認済み] |
| 根拠 | 同パートの英文に castle/city 等の語は無い(wall を含む文は当該1文のみ)。walls→城壁は種類の具体化 | 同パートに kimono/robe 等は無い。"in white"→着物は服装の具体化(今回の再生成では「白い服を着た女」で照合PASS) |

照合基準(VERIFY_HEAD「英文にない情報の追加」)は妥当で、緩和・精緻化は不要。原因は**照合NGの段落を再翻訳しない設計**(local_check NGだけがretry、照合NGは即null)。初回の翻訳が確率的に具体化を混ぜると、その段落(=part全体)が確定的に英語のみになる。[確認済み: er135_enduser_translate_01.py 旧:照合ブロックにretry無し]

## 修正
`er135_enduser_translate_01.py`: 照合NG(verify_ng)の段落だけを、不合格の指摘+前回の訳(RETRY_NOTE_VERIFY_HINT。既存のRETRY_NOTE方式)付きで**1回だけ**再翻訳→再照合(MAX_VERIFY_ROUNDS=2)。照合Prompt・判定基準・閾値は不変。local_check(件数/ID/構造/数値)も再度通す。verify_unavailable(照合応答不正)は再翻訳しない。再照合もNGなら従来どおりfail-closed(null・非キャッシュ)。上限: translate最大 2+1、verify最大 2+2(retry込み)/part。
test: `TestVerifyNgRetry` 3件追加(指摘付きretryで復旧しNG段落のみ対象・retryも失敗ならfail-closedで上限厳守・verify_unavailableは再翻訳なし)。translate+link test 55件全PASS。

## 検証(scratch copy。公開dir・repo内cacheは不変)
caches(`er026_output/.../enduser_sync_cache/ja_generated.json`)をscratchへcopyし、`translate_part`を実API(gpt-6-luna、`DefaultLLM`)で実行(`drive_verify_copy.py`)。
| | 未命中段落 | API call | 費用 | 結果 |
|---|---|---|---|---|
| メロス adv_14 | 1段落(3文 s061-s063) cache命中12段落 | translate 2 / verify 2 | ¥0.0832 | coverage 1.0。**初回verifyは別文(s061 "His friend answered." →「友は答えた。」で『彼の』欠落)をNG→指摘付きretryで「彼の友人は答えた。」→再照合PASS**=retry経路の実機動作を確認 |
| 雪女 std_11 | 1段落(12文 s006-s017) cache命中3段落 | translate 1 / verify 1 | ¥0.0879 | coverage 1.0。初回で全PASS(s013=「白い服を着た女が…」。着物は出ず=旧NGは確率的な揺れ) |
合計約¥0.17(Cap ¥8内)。ログ: `evidence_04/llm_log_{melos,yuki}.jsonl`、`verify_copy.json`。
- 既存訳の全文一致: copy前後でcache既存entry(メロス50/雪女29)が**全件同一**(`old_entries_identical: true`)、追加は各1entryのみ。
- `generate_missing_translations`(page module、API 0のstub llm=呼べば例外)をcopy cacheで実行: failures=[]、api_calls 0/0、story partで`ja`の無いpartは0(両記事)。→ 再produceはAPI 0で2partの訳が付く。
- diff Gate(`tools/ejh03b_diff_gate_01.py`)は公開dirとgit HEADの比較であり公開dirを変えない本委任では実行対象外。同等の「既存訳不変」は上の全entry一致で確認。公開反映後に実行する(手順は RESULT_PACKET_EJH04.md)。

## 新訳(delta)
`evidence_04/ja_generated_delta_melos.json`(adv:adv_14 s061-s063)、`ja_generated_delta_yuki.json`(std:std_11 s006-s017)。
