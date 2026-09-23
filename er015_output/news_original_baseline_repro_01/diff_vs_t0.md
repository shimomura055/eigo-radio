# Step 2: 前回T0との差分表

比較対象: `er015_output/news_core_idea_editorial_trial_01/T0/prompt.txt`
(T0でWriterに実際に渡した全文)・`T0/api_meta.json` と、
オリジナルChatGPT Baseline条件(§7、本ディレクトリ`original_conditions.md`)。

| 項目 | オリジナルChatGPT Baseline(§7) | 前回T0 | 本Trial R0(今回) |
|---|---|---|---|
| Prompt本文(指示部分) | §7逐語(146〜161行) | §7と同一の指示文 + `[ニュース]\n{news}`を追加 | §7と**完全に同一**(逐語)。`[ニュース]`セクションは付与しない |
| [ニュース]素材の有無 | 資料に記録なし(特定できず) | あり。`source_note.md`(=Source Note S、下記)を`{news}`へ埋め込み | **なし**(資料に存在しないため付与しない) |
| Source Note S(編集者要約) | 資料に記録なし | あり。Ledger(15件)を基にer015 `cmd_source_note`が生成した要約文(453字、南伊豆町・66件・32市町村54区域等を含む) | **なし** |
| Ledger(事実台帳) | 資料に記録なし | 生成に間接使用(Source Note S生成の元)。Writerへは直接渡していない | 生成に不使用。Writerへは渡していない(Fact照合のみに使用) |
| 事前Research結果 | 資料に記録なし | あり(er002/er003経由のweb_search研究でLedger作成) | **なし**(本Trialでは新規Researchを実行していない。既存Ledgerを照合用にのみ参照) |
| Writerに実際に渡したテキスト | 不明(素材の有無・内容とも特定できず) | §7指示文 + Source Note S(453字の要約) | §7指示文のみ(逐語、素材なし) |
| developer/system message | 不明(ChatGPT UI側の設定は資料に記載なし) | 「あなたは日本語のニュースを分かりやすく面白く伝える書き手です。」 | T0と同一(「あなたは日本語のニュースを分かりやすく面白く伝える書き手です。」)。この選択はFable設計上「T0と同一の最小system promptがあれば使用可」との指示に基づく |
| モデル | 不明(ChatGPT UI) | gpt-5.6-luna(`response_model_actual`実値で確認) | gpt-5.6-luna(5 run全てで`response_model_actual`実値確認) |
| reasoning effort | 不明(ChatGPT UIに相当する設定なし) | "high"(`vfl01.REASONING_EFFORT`) | "high"(T0と同一) |
| web_search/tools | 不明(資料に検索の言及なし) | 未使用(`web_search=False`、`web_search_call_count=0`) | 未使用(5 run全てで`web_search_call_count=0`確認) |
| 温度・その他パラメータ | 記載なし | 未指定(Production Writer既定のみ、`schema=None`) | T0と同一(未指定、`schema=None`) |
| 出力字数(本文のみ) | 657字(タイトル除く) | 目安未算出(T0記事全文は`T0/article.md`参照、タイトル含め約630字) | run1=701字/run2=744字/run3=690字/run4=702字/run5=715字(いずれも`article.md`全文の文字数、タイトル込み) |

## 主要な差分の要約

1. **素材の有無が最大の差**: T0はSource Note S(Ledgerから編集者が要約した453字の
   ニュース要約)を`{news}`として与えていたが、オリジナルChatGPT Baselineの
   Prompt(§7)にはそのような素材挿入箇所が資料上存在しない。本Trial(R0)は
   ユーザー指示に従い、T0のSource Note Sを使わず、§7のPrompt指示文のみを
   逐語で使用した。
2. Prompt指示文そのもの(語り口・見方選択・長さ800〜1000字等)はT0・R0・
   オリジナルの3者で(資料の記録範囲では)一致している。
3. developer message・モデル・reasoning effort・web_search未使用は
   T0とR0で同一(R0はT0の値を踏襲する設計判断)。ただしオリジナル
   ChatGPT Baseline側の対応する設定は資料に記録がなく「不明」。
