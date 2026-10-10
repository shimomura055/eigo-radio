# PREREGISTRATION_01: POST-EN-HUMAN-PRE-SORTER-BLIND-TRIAL-01(Trial/DEV、2026-10-10)

結果を見る前に固定する。結果を見てPrompt・packet・件数・バッチ構成・モデルを変更しない。Production変更ゼロ。

## 固定物(sha256)
| 物 | sha256 |
|---|---|
| blind_packet_01.json(Union 29件) | f13dcbec891022f4d4c4a800e25bb103a99245a2d60408ac7be5415a31ff4610 |
| BLIND_PACKET_01.md(人間可読) | db30f8564b0884c6a4e862163c67185894753c8a20b6aacdc41641a37a450402 |
| prompt_presorter_01.txt(rubric+出力schema) | c04f5784590b5f8db95814d2d1496750599397cbfd40b9564172812fe470c070 |
| batch_text_1.txt | 4e41e5412b6cc4984abf45a73c22e1da0541f47e8255d025c32dcbb7a1e68c54 |
| batch_text_2.txt | c27dc8dfa1dfc1a09470a1c49aa12638d6cabd788565edaaaa00768dc57f85c5 |
| batch_text_3.txt | 98e256a0cd29b46a6d5e660b4d8e67d5864ac7240df44817ff0574471ec1e4bb |
| run_presorter.py(driver) | 2378dd71aff071ca78d2370090103f8cad66b10a5c74e1e2a878bd9abccf6007 |
| build_packet.py | 48889004c17fb274ffe0c3684373f4fa8d9727c76e1bb3ea133888ee72074a94 |
| model_check_01.json(疎通実測) | 2108b77da6f2523479f718b78eeed8b264abd4b5cc27ab832b4cfad64d23ec71 |
| cost_estimate_01.json | 48c22e6134762360a39e584e095df8325052bc21705b42e59cbc0ef3d7a8e56f |

## packet
- 出所: POST-EN-TRIAL-01の `flags/A3,A4`(Union 29件。新たな重複除去・件数変更・除外・Flag追加なし)。ID順に機械抽出、29件(機械assert)。HUMAN_REVIEW_POST_EN_01.md と同一の29件(A3∪A4)。
- 各件: ID / 中立Theme(重複テーマは "(draft 1/2)") / Flag対象英文(文ID付き) / 前後各2文(splitter結合・途中切れはそのまま、説明なし) / 対応Fact(台帳原文全文: 本文・scope・conditions・notes_for_writer等) / A3・A4のFlag理由(理由文のみ。type・confidenceは除外)。
- Fact未指定(4件)の規則: 全件同一規則として、そのFlagの記事の**台帳全Fact**を渡し、「flaggerは対応Factを指定していない」と中立に注記。
- 除外: confidence / type名 / severity / Known・Newラベル / 旧Checker / 既存Humanコメント / 稿のstatus・route(STOP稿・採用稿表記) / User・ChatGPTのA/B/C/D / 他モデル回答。Userの判定はリポジトリ参照せず、Claude(Sonnet・Fable)とも未見。
- Blind保全確認: `BLIND_PACKET_01.md` および `batch_text_*.txt` に対し grep(confidence|MAJOR|MINOR|STOP|Known|New issue|ADOPTED|Checker|severity|COMPLIANT|RESOLVED|主体対象入替)=0件(2026-10-10 実測)。
- 23番(splitter artifact疑い)は特別扱いしない(モデルへ教えない、追加説明なし)。

## 実行条件
- バッチ: ID順に3バッチ(10/10/9)、全モデル同一構成・同一Prompt(rubric全文を各バッチに含む)。モデル間は完全独立(他モデル回答を見せない)。各バッチ1回。再試行は同条件で最大1回、JSON不正/ID不一致/API errorの場合のみ(記録)。再現性Trialなし。
- 設定: OpenAI Responses API直接、reasoning effort=medium(ANTENNA/POST-EN Flaggerと同じ)、max_output_tokens=16,000、temperature等は送らない。

## モデル確認表(2026-10-10実測、model_check_01.json)
| モデル | provider | 要求model_id | API疎通 | routing | effort | 単価 $/1M in/out |
|---|---|---|---|---|---|---|
| Luna | OpenAI | gpt-6-luna | OK(応答model=gpt-6-luna) | 直接API | medium | 0.10/0.50(登録) |
| Sol | OpenAI | gpt-6.1-sol | OK(応答model=gpt-6.1-sol) | 直接API | medium | 2.00/10.00(登録) |
| Astra | OpenAI | gpt-6-astra | OK(応答model=gpt-6-astra) | 直接API | medium | 10.00/50.00(登録) |
| Fable | Anthropic | claude-fable-5-1 | **UNAVAILABLE** | - | - | 未確認(未登録) |
| Opus | Anthropic | claude-opus-5-5 | **UNAVAILABLE** | - | - | 未確認 |
| Sonnet | Anthropic | claude-sonnet-5-5 | **UNAVAILABLE** | - | - | 未確認 |
UNAVAILABLE証拠: ANTHROPIC_API_KEY が環境(process/User/Machine/.env)に存在しない(値は記載しない)。`.venv` に anthropic SDK なし。api.anthropic.com/v1/messages へ3モデルを鍵なしで疎通した結果は3件とも HTTP 401 authentication_error「x-api-key header is required」(request_id: req_011CfspcMS5zax5cwk5EzRXK / req_011CfspcNUqfKEC1Koa5G5ot / req_011CfspcPSdNY23iqDfViaNp)。**モデル存在・権限の有無は鍵がないため未検証**(「モデルが無い」ではなく「鍵が無く呼べない」)。Claude Code subagent経由の代替は同一条件(packet/raw response/token/cost)を満たせないため使わない。使えないモデルを別モデルへ置換しない(ユーザー指示7)。GPT系3モデルのみ先行実行し、結果保存・報告後STOP。

## 見積・ガード
COST_ESTIMATE_01.md。実行対象3モデル合計(見積): 中央約JPY249.5 / 高位約JPY452.8。判定は中央(ガード300以内)。ランタイムガード: 累計実費JPY300以上で以後のcall拒否。

## 宣言
結果を見てPrompt・packet・バッチ・設定・モデルを変更しない。悪かったモデルのみの再Trialをしない。User判定との照合・一致率計算はClaude側で行わない(ChatGPT側で実施)。Few-shot追加・threshold追加・Production wiringをしない。使用モデルは最新世代(PM_GOVERNANCE 25節): Luna(最新世代の効率系)/Sol 6.1(最新の推奨系)/Astra 6(最新の旗艦)。Fable/Opus/SonnetはUNAVAILABLE。
