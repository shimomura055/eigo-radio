FABLE-DELEGATION-MARKER: FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01-委任_06-MEANING-ROOTCAUSE-REDESIGN-20261023

# 委任_06: Key Phraseの日本語意味(Std)・英語説明(Adv)の品質問題の**根本原因再調査と再設計**(Opusレビュー前まで)。Prompt文言の再調整ではなく、工程・入出力・検査の構造から原因を特定する。API≤15円(replay・probe)、Production/Prompt変更0。

## 背景(ユーザー決定 2026-10-23、原文を保存して全文読むこと)
- 品質問題は未解決: Std「draw a line」の意味は「一線を引く」の成功例がある一方「線を引く」「境界線を引く」が残る/Adv説明は「to set a clear limit on what is acceptable」(狭い)や「to set a limit or make a clear distinction」(併記)が残る。目標例「to establish a clear boundary or limit」(文字列固定ではなく品質例示)。
- A-1は正式採用維持(配線は改善案と合わせて)。A-3 v3は採用しない(記事固有条件は減るが本文の意味から離れる副作用)。**手段の不採用=目的達成ではない。改善を継続**。
- 方針: 既存工程の改善優先・不要なLLM工程/費用を増やさない・過去Trial(er112、A3_VERIFICATION)の入力/失敗例を再利用・個別対策不可・承認済み品質基準を緩めない・X/Z共通。

## T-0
1. **ユーザー原文を逐語保存**: jsonl `C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl` の最新userメッセージ(「# 指示｜Key Phrase意味・説明品質の根本改善継続とPM判断是正」)を `docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_USER_03.md` へ無改変保存(最初にcommit)。
2. 委任文逐語保存: `.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl <同jsonl> --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out docs/pm/delegation_log/2026-10-23_FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01_委任_06.md`(index 376以降、先頭MARKER一致)。
3. ACTIVE_TASK自分の行のみ(並行: ASR PN/UKUS実装、PM_GOVERNANCE是正agent。pythonは自分のPIDのみ終了可。commitはpath限定+`git diff --cached --name-status`確認)。OPEN-474 Status=`A1_APPROVED_WIRING_PREP / MEANING_QUALITY_IMPROVEMENT_IN_PROGRESS(A3_v3_REJECTED_AS_MEANS)`、UDR #169に「A-3 v3不採用(2026-10-23)、品質改善は継続」追記。

## 1. 根本原因の再調査(証拠 file:line、実データ)
対象工程: 選定(er105 fulltext_p2: 全文を見てKPを選ぶ。選定時に「本文での意味」を把握しているか、出力に意味情報があるか)→canonicalization(kc、全文入力、surface→used_form。意味情報の出力有無)→Std日本語意味 gloss(`er003_key_words_gloss_alignment.py:586-604`: 入力=全文+KP、「全語の意味を反映」要求、mapping検査、person検査)→Adv英語説明(`er019_family_x_kp_explanation_01.py:54-85,164-178`: 入力=phrase+1文(S29)+日本語参考意味、5件一括)→検査(gloss alignment gate/HR、redundancy、KP3V)→retry/fallback。
確認事項:
(a) **意味の正本がどこにも無い**仮説: 各工程が独立にLLMに「意味」を推定させており、「本文中の中心義」を1回決めて下流で共有する構造が無い→Std/Advの揺れ・不整合・逐語化の共通原因か。工程間で受け渡される情報(全文/1文/参考意味)の差と、その差が結果に与える影響を、er112 replayデータ(a1gE0/E2/E3、A3_verify 92行)で層別分析(例: 1文だけ渡した場合に狭くなる率、日本語参考意味が逐語のとき説明も逐語化する率)。
(b) Stdが逐語に戻る原因: gloss Promptの「key_phrase全語の意味を反映」要求+mapping検査(語対応)が「一線を引く」のような非逐語の慣用義を減点/retryさせていないか(mapping_gate既定False=record-onlyでも、LLM自己申告 `qa_reflects_all_key_phrase_words` がPrompt上の圧力になっていないか)。「draw a line」で「線を引く」が出るのは、本文文脈(許容範囲の境界)が意味選択に効いていない=全文は渡しているが「本文での用法」を特定する指示が無い、または慣用句と字義の判別指示が無い。probe(≤5円)で、同一入力に「本文中の該当文を引用し用法を特定してから意味を書く」等の構造的指示を与えた場合の安定性を測る(Prompt案の最終化ではなく原因切り分けのため)。
(c) Advが狭い/広い原因: 入力が1文+日本語参考意味で、(i)文脈が1文だと記事固有の条件が入り、(ii)A-3 v3で「中心義1つ」と言うと一般義へ逃げる→「本文での用法に合う中心義」を特定する手がかり(用法の種類: 比喩/字義、対象、場面)が入力に無い。日本語参考意味が逐語(「線を引く」)だと説明も影響するか(相関)。
(d) Validator/retry/fallbackの寄与: gloss alignment gate(HR経路)、`_person_mismatch_reason`、redundancy QA、OUTER_RETRYが品質方向にどう働くか。fallback時(gloss失敗→?)の出力。
(e) 既存承認仕様・過去Trial: Trial-02(一般化LLM工程REJECTED)、KPQ①②、db_hybrid時代の辞書見出し形+辞書義の供給(旧経路で意味品質はどうだったか)、JRE、OPEN-454。承認済み品質基準(Std=日本語意味1つ簡潔/Adv=英語説明、B仕様PROMPT_SHA256)の内容を確認。

## 2. 再設計(DESIGN_03、推奨1案+代替、比較表)
目標: 「本文での用法に合う中心義」を正しく捉え、Std日本語意味(慣用義・簡潔・1つ)とAdv英語説明(本文の意味を踏まえ、記事固有条件に限定されず、広すぎない中心義)を**安定して**出す。X/Z共通、新規LLM call原則0。
検討必須の候補(採否は設計者、各々の費用・副作用・既存仕様との差分を明記):
- 案S「中心義の正本化」: canonicalization call(全文を見ている既存call)の構造化出力に `sense`(本文中の該当文の引用+用法種別[idiom/literal/phrasal]+中心義の英語1文[記事固有名詞・数値を含めない]+日本語中心義案)を追加し、gloss/説明の両callに「この中心義に従う」入力として渡す(新規call 0、出力トークン微増)。Std/Advの整合は構造的に確保。schema/validator/goldenへの影響、A/B/C凍結との関係(fulltext専用)、既存Trial-02(別工程新設REJECTED)との違い(既存callの出力拡張であり工程追加ではない)。
- 案G「gloss Promptの構造化」: 「本文の該当文を特定→用法(比喩/字義)判定→慣用義なら日本語の定訳/フレーズ全体の意味→1つに絞る」の手順化+「全語反映」要求の撤回(mapping検査との整合)。
- 案E「説明Promptの入力拡張」: 1文→前後1文+用法種別+中心義(案Sがあれば不要)。
- 案D「決定論の補助」: 慣用句辞書(既存資産にあるか)、逐語検知(日本語意味がsurface語の直訳連結に一致)の警告(新検査=原則避ける、根拠があれば)。
- 組合せと最小構成(Charter 1)。失敗例(A-3 v3の「一般義への逃げ」、bring in/letter of introduction/hold on)が構造的に防がれる理由を各案で説明。
- 検証計画: er112 replay基盤を再利用、難例20+正常30+A3_verify 25の計≥75 KP(X/Z)、arm=現行/A-1/A-1+案S等、各2〜3回、Judge 2系統+Fable目視、ユーザー§4検証項目1〜6(retry/fallback含む量産条件=実runでの確認計画)、成功基準(数値: 本文意味一致≥現行、記事固有混入≤5%、過度限定/過度一般化≤5%、Std/Adv整合100%、正常KP非劣化≥95%、`draw a line`=Std慣用義3/3・Adv中心義3/3)、費用見積(Trial≤60円)。
- Opus論点(条件A: 工程出力の構造変更)。

## 3. 成果物
`docs/research/FX-KP-GENERALIZATION-MEANING-COMPREHENSIVE-01/{ROOT_CAUSE_02,DESIGN_03,OPUS_REVIEW_REQUEST_03}.md`、probe結果json。commit(path限定)、secret_scan hits=0、`git push origin HEAD:main`。

## 禁止
Production/Prompt/template変更、A-1配線実施、OPEN-476修正、記事B成果物変更、15円超過、`er111_*`/`er109_*`/`er103_*`編集、Trial実装(Opus後)。

## 報告(docs/pm/RESULT_PACKET_KPGM6.md)
(1)根本原因(a)〜(e)の結論と証拠 (2)層別分析の数値 (3)推奨案の仕組み・代替・比較表・最小構成 (4)検証計画・成功基準・費用 (5)Opus論点 (6)commit・raw URL・SSOT + RESULT_PACKET 4行 + 「判定整合: 重大NG=なし」。