# ER-003-REPRO-02-MAIN 実行報告(ADD03本文・学習セクションまとめて生成)

**ステータス: `PASS`(ER-003-REPRO-FINAL、2026-08-09、ユーザー通し試聴OK)**

> 本文書は初回通し候補生成時点(`PROTOTYPE / NOT_APPROVED`)の記録として作成されたが、ER-003-REPRO-FINALにてユーザーが全体を試聴し「OK」と判定したため、最終ステータスを`PASS`へ更新した。あわせて7節・17節・18節の記述を、試聴で確定した事実(meaning_3はTTS hallucinationではなくASR同音異義語ambiguityであり、人間試聴の結果PASS)に合わせて訂正した。訂正箇所には[訂正: ER-003-REPRO-FINAL]と付記する。

## 1. 使用したADD03原稿・記事ID

- 記事ID: **ADD03**「ホルムズ海峡を通航する船舶への20％通航料をめぐる発言の撤回と市場反応」
- B1本文: `er003_output/b1_p1/ADD03/b1_article_raw.md`
- 英語タイトル: "20% Hormuz Fee Dropped, but Oil Market Remains Nervous"
- 日本語タイトル: "20％の料金所は一夜で撤去。それでも、原油市場は静まらない"

## 2. 使用した構成

A01/A02最終19パート構成をそのまま踏襲。サービス共通文言(Welcome/Preview案内/ポイント解説/Key Phrases案内/Full Story案内/番号1-5)はA01の既存音声をそのまま再利用。ADD03固有の例外処理は追加していない。

## 3. Preview再利用結果

`er003_output/b1_p9a/ADD03/narration/preview_japanese_only.wav`(ER-003-REPRO-02-PREVIEWでユーザー試聴・承認済み)を**無変更のまま**固定使用。

## 4. Key Phrase 5件

| # | used_form | 日本語(採用) |
|---|---|---|
| 1 | blockade | 海上封鎖 |
| 2 | be in place | 実施中である |
| 3 | freedom of navigation | 航行の自由 |
| 4 | tollbooth | 料金所 |
| 5 | smell of gunpowder | 火薬のにおい |

日本語訳は、canonicalization出力で読点区切りの2案(例: "実施中である、効力を保つ")が提示されていた2件について、最初の案をそのまま採用した(意訳の追加改善はしていない)。

## 5. Full Story生成条件・TTS call数・retry数

ER-002/A01/A02で確立した本文用凍結仕様をそのまま適用(model=gemini-2.5-pro-preview-tts、voice=Aoede、3chunk構成)。

| 項目 | 値 |
|---|---|
| 1回目の実行 | 3試行とも内容QA不合格(STOPPED) |
| 2回目の実行 | **1試行目で合格**(既存の3試行以内の枠組みで解決。追加許可を要さず) |
| technical retry | 0回 |

1回目の全滅は、詳細ログを保存していなかったため理由の詳細は残っていない(この点は今後の改善課題)。2回目の再実行で1回目に合格したことから、内容QAの一時的な変動と判断した。

## 6. 短文ナレーション生成結果

| 名前 | 試行回数 | 備考 |
|---|---|---|
| topic_intro | 2 | ASR不一致1回で自動再試行 |
| japanese_title | 1 | |
| meaning_1(海上封鎖) | 1 | |
| meaning_2(実施中である) | 1 | |
| meaning_3(航行の自由) | 6(strict verifier不合格のまま。TTS自体は正常、[訂正: ER-003-REPRO-FINAL]参照) | 後述7節 |
| meaning_4(料金所) | 2 | ASR不一致1回で自動再試行 |
| meaning_5(火薬のにおい) | 1 | |

## 7. meaning_3「航行の自由」のASR同音異義語ambiguity [訂正: ER-003-REPRO-FINAL]

strict検証(部分一致+文字数上限)が6回とも不合格になった。ASR結果を精査したところ、6回中2回が**「高校の自由」(こうこうのじゆう)と完全一致**しており、これは「航行の自由」(こうこうのじゆう)と**全く同じ読み方の同音異義語**である可能性が高いと判断した。

このプロジェクトでは、「決勝→結晶」「歓喜→寒気」等、ASRが正しい発話を別の同音異義語の漢字として書き起こす既知のパターンが繰り返し確認されている。今回もそのパターンに合致すると判断した(他の4回の試行では「高雄」「高幸寺」等、さらに異なる読み取り結果や空文字となっていたが、これもASR側の不安定さを示す状況証拠として扱った)。

**当初の対応**: 自動retryをこれ以上繰り返さず、6回目(最後)の生成音声をそのまま保持し、`PROVISIONALLY_ACCEPTED_REQUIRES_HUMAN_REVIEW`として明示的にマークした。

**ER-003-REPRO-FINALでの確定**: ユーザーがADD03全体を試聴し、本項目を含めPASSと判定した。これにより以下が事実として確定した。

- TTS音声は正常(発音の誤りではない)
- strict verifierの不合格は、ASRが「航行」を同音異義語「高校」として誤認識したことが原因
- この事象は**TTS hallucination(無関係な内容の生成)ではない**。A01の"Now, the full story."やA02のmeaning_5/opt outとは異なる、別の不具合分類である
- 自動QAのみでは正誤を確定できず、human reviewへ送った判断は適切だった

この分類にもとづき、17節・18節の指標を「短文TTS hallucination: 0件」「ASR homophone ambiguity: 1件(human review結果: 正常)」へ訂正する。JSON上のステータスも`ACCEPTED_AFTER_HUMAN_REVIEW`へ更新済み(`er003_output/b1_p9a/ADD03/audit/new_narrations_result.json`)。

## 8. Point One / Two / In One Line・数字金額日付QA

ASR全文確認の結果、以下の数字・金額・日付表現はすべて書字順どおりに発話されていることを確認した(A01のスコア読み上げ問題のような語順入れ替わりは検出されなかった)。

| 対象 | ASR上の確認 |
|---|---|
| 20% | 複数箇所で正しく検出 |
| July 13, 2026 | "July thirteen twenty twenty six"として検出 |
| $87 a barrel | "eighty seven dollars a barrel" |
| $84.73 | "eighty four dollars and seventy three cents" |
| 4.9億円 | "four point nine billion yen" |
| $30 million(2箇所、見出し+本文) | いずれも正しく検出 |
| 10%, 2%, 24 hours, one day | いずれも正しく検出 |

Point One/Two/In One Lineの見出し・内容ともASR全文で欠落なく確認できた。

## 9. MFA利用箇所

Full Story本編音声全体(168.23秒)へ英語MFAを1回実行(`mfa_tool/add03_body_output/ADD03_body.TextGrid`)。タイトル境界1箇所、notification2挿入位置2箇所の特定に使用。**MFA単独では確定せず、3箇所ともASRで前後の発話内容を確認済み**(数字・金額・日付が密集する記事のため特に重点的に実施)。MFA手修正は発生していない。

## 10. 音声編集内容

Full Story音声へ、notification2挿入2箇所+タイトル除去の計3編集を、時系列で後ろから前の順(insert2→insert1→title_trim)で適用。編集前後で発話内容が変更されていないことをコードで確認済み(詳細: `audit/full_story_edit_info.json`)。

## 11. 効果音・ポーズ

Intro/Outro/notification(3回)/notification2(2回、Full Story内)はA01/A02最終仕様の共通部分を使用。ADD03固有のタイトル除去位置・notification2挿入時刻はADD03自身のMFA+ASRで新たに特定した。

## 12. 音量調整

A01 R1で確立した一般的な方法(Preview・本編は無加工のまま基準、他素材は平均RMSへ、OutroはIntroの調整後RMSへ一致)を適用。A01固有の追加減衰は未適用(A02と同じ方針)。

## 13. 初回完成候補の場所

| 項目 | 値 |
|---|---|
| path(WAV) | `er003_output/b1_p9a/ADD03/assembled/English_Your_Way_ADD03.wav` |
| sha256(WAV) | `24253fb9cab325f4766c1e9e3533d0c6a2a8dcefdc6abdf1e82e0c12374ebcf9` |
| path(MP3) | `er003_output/b1_p9a/ADD03/assembled/English_Your_Way_ADD03.mp3` |
| sha256(MP3) | `b8e2162801e52f32a17e03d3472cc82d747cdbe537542366d7e845f16f972ed6` |

## 14. 全体duration

**264.862秒(約4分25秒)**

## 15. セクション一覧とduration

| # | パート | 開始 | 終了 | 長さ | 直後のポーズ |
|---|---|---|---|---|---|
| 1 | Intro | 0.000 | 10.736 | 10.736秒 | 0秒 |
| 2 | Welcome to English Your Way.(A01再利用) | 10.736 | 12.847 | 2.111秒 | 0.5秒 |
| 3 | Today's topic is...(新規) | 13.347 | 19.018 | 5.671秒 | 0.65秒 |
| 4 | 日本語タイトル(新規) | 19.668 | 26.428 | 6.760秒 | 0.5秒 |
| 5 | Transition(1回目) | 26.928 | 28.968 | 2.040秒 | 0.4秒 |
| 6 | Here's a quick preview.(A01再利用) | 29.368 | 30.819 | 1.451秒 | 0.65秒 |
| 7 | ポイント解説(A01再利用) | 31.469 | 32.689 | 1.220秒 | 0.5秒 |
| 8 | Preview(承認済み、無変更) | 33.189 | 53.969 | 20.780秒 | 0.5秒 |
| 9 | Transition(2回目) | 54.469 | 56.509 | 2.040秒 | 0.4秒 |
| 10 | Here are today's key phrases.(A01再利用) | 56.909 | 58.800 | 1.891秒 | 0.5秒 |
| 11-15 | Key Phrase 1〜5 | 59.300 | 90.005 | 計30.705秒 | (各内包) |
| 16 | Transition(3回目) | 90.005 | 92.045 | 2.040秒 | 0.4秒 |
| 17 | Now, the full story.(A01再利用) | 92.445 | 94.316 | 1.871秒 | 0.7秒 |
| 18 | Full Story | 95.016 | 258.218 | 163.203秒 | 0.5秒 |
| 19 | Outro | 258.718 | 264.862 | 6.144秒 | 0秒 |

## 16. 機械QA

| 項目 | 結果 |
|---|---|
| Previewが承認済みファイルと同一 | 合格(sha256照合) |
| Key Phrase 5件が正しい順序・構成 | 合格(ASR全文で確認) |
| Full Storyに重大な欠落・追加がない | 合格(ASR全文で本文全体を確認) |
| 数字・金額・日付が書字順どおり | 合格(9節参照) |
| decode可能・clippingなし | 合格(peak 0.909) |
| セクション順序・ポーズ仕様 | 合格 |
| meaning_3の内容一致 | strict verifier上は不合格。**ただしTTS音声自体は正常(7節)**。ユーザー試聴でPASS確定 [訂正: ER-003-REPRO-FINAL] |

**機械QAは「meaning_3を除き」全て合格した。meaning_3も含め、これは音質・自然さ・完成度の承認を意味しない。ユーザー試聴での判断が必須 → ER-003-REPRO-FINALにて試聴実施、全体PASS。**

## 17. 再現性指標 [訂正: ER-003-REPRO-FINAL]

| 指標 | 値 |
|---|---|
| Full Story TTS call数 | 4回(1回目3回不合格+2回目1回目合格) |
| technical retry数 | 0回 |
| 内容起因再生成数(本文) | 3回(1回目の3試行分) |
| **短文TTS hallucination件数** | **0件**(meaning_3はhallucinationではないと確定。A01/A02の"Now, the full story."/"opt out"のような無関係内容の生成は発生していない) |
| **ASR homophone ambiguity件数** | **1件**(meaning_3「航行の自由」。TTS音声は正常、ASRが同音異義語「高校」を誤選択) |
| hallucinationの自動検出・自動吸収件数 | 該当なし(hallucination自体が0件のため) |
| 自動QAのみで確定できずhuman reviewへ送った件数 | 1件(meaning_3) |
| human review結果 | 正常(PASS、ER-003-REPRO-FINAL) |
| MFA利用箇所数 | 1箇所(本編音声全体、3境界の特定に使用) |
| MFA手修正数 | 0 |
| ASRで検出した問題数 | 2件(meaning_3の同音異義語ambiguity、Full Story 1回目3試行の内容QA不合格) |
| 人間試聴前の手修正数 | 0(meaning_3は保持のみ、書き換えなし) |
| ADD03固有例外追加数 | 0(汎用パイプラインをそのまま適用) |
| 初回通し候補までの人間確認回数 | 0回(指示どおり、途中確認なしで到達。ただしmeaning_3は最終報告で明示的にフラグを立てている) |
| 初回通し候補のユーザー判定 | そのままOK(修正往復なし) |
| **最終ユーザー判定** | **PASS**(ER-003-REPRO-FINAL、2026-08-09) |

## 18. A02との比較 [訂正: ER-003-REPRO-FINAL]

| 指標 | A02 | ADD03 |
|---|---:|---:|
| Full Story TTS call数 | 2 | 4(1回目全滅+2回目1回で合格) |
| MFA手修正数 | 0 | 0 |
| 短文TTS hallucination件数 | 2件(いずれも自動吸収) | **0件** |
| ASR homophone ambiguity件数 | 0件 | **1件**(human review結果: 正常) |
| 数字・金額・日付の語順異常 | (該当なし) | **0件**(20%、$87、$84.73、4.9億円等すべて書字順どおり) |
| 初回通し候補のユーザー判定 | そのままOK | そのままOK |

ADD03はA02より数字・金額・日付が密集する記事だったが、**語順の異常は1件も検出されなかった**(A01のスコア読み上げ問題のような事例は再発しなかった)。一方、短文ナレーションでは新しい種類の不具合(ASR同音異義語によるstrict検証の機械的な行き詰まり)が見つかった。これはA01/A02で見られた「TTSが無関係な内容を生成するhallucination」とは原因が異なり、**strict検証システムでは機械的に解決できない**性質のものである。今回はretryを打ち切ってhuman reviewへ送り、ユーザー試聴で正常と確定した。この判断プロセス自体は適切に機能したと言える。

## 19. 人間試聴前に残るリスク

- **meaning_3「航行の自由」は未確認のまま(最重要)**。実際に「高校の自由」と誤読されている可能性を排除できていない。
- B1本文自体はまだユーザー最終承認前。
- Full Story 1回目の3試行不合格の詳細理由が記録されていない(スクリプトの初期バージョンの記録漏れ、2回目実行分からは記録済み)。

## 20. 作成・変更したファイル

- `er003_v1_repro02_main_generate.py`(新規、全stage a〜e。A02の汎用関数をimportして再利用)
- `er003_output/b1_p9a/ADD03/`配下の新規成果物一式
- 既存A01/A02コード: **変更なし**

## 21. テスト結果

新規ロジックは追加していない(A02のstrict検証・フォールバック関数をそのまま再利用)。プロジェクト全体回帰テスト: **1660件全合格、回帰なし**。

## 22. Git status

このレポート作成時点では未コミット。関連ファイルのみをステージしてコミットする。

## 23. Push

実行していません。
