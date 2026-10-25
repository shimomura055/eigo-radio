# OPUS_REVIEW_01(条件A: Z narrator clip内部分割Trial設計、2026-10-25、opus-consultant、read-only・API 0)

---
## FZ-NARRATION-CHUNK-TTS-TRIAL-01 Opus独立技術レビュー(条件A、read-only、API 0)

### 判定: 条件付きで進んでよい(有料生成の前に、無料で直せる必須条件が4点あります)
Trialとして必要で、方式も妥当です。方式とは、長いnarrator clipだけを段落境界で分割し、chunkごとにRMS正規化して0.2秒の無音でつなぐものです。既存のDialogue分割・Voice・速度v2は再利用し、新しい音声加工もありません。設計の差し戻しは不要です。
ただし、直前のX Trialで私が必須にした隔離策(M1〜M3)が、Z設計に引き継がれていません。また、並行案件(OPEN-508)が動いている環境では、変更検知が誤ってSTOPする可能性が高いです。この2点は有料生成の前に直してください。

### 必須(有料生成の前に直す)
**N1. X Trialの隔離M1〜M3をそのまま引き継ぐ(DESIGN_01.md:59の記述が不足)**
- §3の隔離策は、sinkの差替え5種と、事後のsha比較だけです。これではPronunciation Ledgerを「検知」できても、書込み自体は「防止」できません。
- X runnerには対策が実装済みです(`er113_fx_paragraph_chunk_trial_01.py:655-704,714-763`)。
  - Ledgerの`LEDGER_PATH`をDEVのコピーへ向ける(negative_cacheも一緒にDEV側へ移る)
  - Ledgerのhint/low-confidenceを事前に計算し、空であることを確認する
  - `run_local_rewrite_recovery`をwrapperで包み、out_dirをDEV側へ差し替える
  - 監視対象に`negative_cache.json`、`er009…/human_review_queue.jsonl`、`er011_output/local_rewrite_recovery`のtreeを加える
  - 起動時にcwd==ROOTをassertする
  - gen_resultに`instruction_type`、`local_rewrite_recovery`、`canonical_text_before_local_rewrite`、`style_prefix`、`tts_model_id`を記録する(X OPUS_REVIEW_01.md:11-33)
- 新しく書かず、`redirect_production_sinks`を再利用してください。
- A(1b_s1)が生成された時点からLedgerが変わっています(working treeで`ledger.json`がM状態)。このため、事前計算で空にならなければ条件差になります。その場合はPhase 1へ進む前にFableへ報告してください。

**N2. 並行案件がある中でも誤らない書込み検知と、条件の固定**
- 誤検知の問題: repo全体のmtime走査と、PROTECTED_STORESのsha比較は、自分以外の書込みも拾います。OPEN-508や他のagentはTTS以外の処理(Writerのcost_summaryやattempt_historyへの書込み等)でもこれらを更新します。git statusを見ても多数のstoreが更新中です。このため誤ったSTOPが起きやすく、逆に誤検知を見慣れて本物の汚染を見逃すおそれもあります。
  - TTSだけを直列化する(DESIGN_01.md:60)のでは不十分です。
  - 推奨: `sys.addaudithook`で、自プロセスの書込みmodeの`open`と`subprocess.Popen`を記録し、許可dir以外への書込みは即STOPにする。これで原因を自プロセスに特定できる。
  - mtime走査とsha比較は補助として残す。差分が出たら即STOP・事実報告とし、その後で書込み元を特定する(自動で続行しない)。
- コード同一性の問題: OPEN-508の案A配線作業でProduction moduleが編集中の可能性があります。起動時に、importするProduction module(news_tail_fix、er063、er062、assemble、er025、er020等)のsha256とgit diffの状態を記録してください。TTSまたは組立の経路に未commitの変更があればSTOPしてください。そうしないと、Aと異なるコードで生成するおそれがあります。

**N3. DEV assemblerの不変条件をassertする(DESIGN_01.md:84-85)**
1. target_rmsの固定: 1b_s1には`gain_report.json`がありません。target_rmsは`b1b/assembly/timeline.json`の`gain_report.target_rms=0.07332`(:228)から読んでください。B・A_r2の両方でこの値に固定し、再計算はしないでください。再計算すると、er063:1761がfirst story clip(=chunk k1)のRMSを使ってしまいます。
2. Commentの位置: 1b_s1では`Comment 2`が`full_story_part1_c1`の直後にあります(timeline.json:370-371)。展開後の並びが`k1, 0.2s, k2, (既存gap), Comment 2`となることをassertしてください。既存のnarrator後0.5秒とComment前後の1.0/0.8秒は、最後のchunkの後に1回だけ入れます。
3. A_r2は新しいtakeであることの確認: A_r2の音声sha256が、Aのsha(例: part1_c1 `61957c46…`)と異なることを確認してください。Master Audio Storeやreuseを通っていないことの証明になります。

**N4. 判定基準(事前固定)の比較の基準点を直す(DESIGN_01.md:92)**
- 現在の基準は「境界音量差 <= Aのpart境界差の最大値」です。しかし1b_s1のpart境界には、5語のclipや2語のセリフclipが絡みます。1秒窓では値が不安定で、基準として緩すぎます。
- また、chunk境界の前後は内容そのものの音量差が大きい位置です。例: 「Surely a neighbour would hear!」→「I rushed in.」
- 基準点は「A(1 callで通して読んだもの)の同じ段落境界位置での、末尾1秒と先頭1秒の差」にしてください。これでBの差から内容による差を除けます。part境界の値は参考として併記します。
- 速度の対比較も、chunk(6対)ではなく段落単位(3 clipで計16段落)のspanにしてください(X M4と同じ考え方)。take間ノイズと比べられる数になります。

### 推奨(任意)
- **R1 クライマックス前の切断(論点a)**
  - part1_c1(「That eye had to go.」/「For seven nights」): 場面の転換点で、良い切断です。
  - part2_c3(「…would hear!」/「I rushed in.」)と part3_c1(「…quick beating.」/「I talked louder.」): 心音の高まりから行動・発狂へ移る、まさにその直前です。独立したcallでは抑揚の勢いが一度リセットされやすく、迫力の連続性にとって最悪のケースの位置です。
  - Trialとしては「最悪ケースの負荷テスト」として意味があるので、そのままで構いません。ただし試聴ページでそう明示してください。ここで不合格でも方式全体のREJECTとは即断せず、切断位置を変えた再試行の余地を残してください。
  - 代わりの切断位置の候補(段落の構成は推定): part2は「Wide open.」の後(約43/75語。心音の高まりと行動を同じchunkに残せる)、part3は「…how little I feared?」の後(約57/91語)。
  - 費用約3円の別arm(B_alt: この2 clipだけを切り直す)をFable判断で追加するのは合理的です。決定論的なルールにするのは難しいので、plannerは変えないでください。
- **R2 閾値の位置づけ**: 1b_s1の3 clip(141/118/148語)は、閾値を6〜117語のどこに置いても分割対象が同じです。つまり本Trialは閾値100語を検証していません。検証しているのは「約70語のchunk+0.2秒」です。また、WPM表の≥100語は3本だけで、短いclipほど端の無音比率が大きく低く出る交絡もあります。結果の報告で、これを閾値の正当化に使わないでください。閾値100の根拠としては、既存の`target_words`と同じ値であること、ユーザー指示「長く続く区間のみ」に沿うことで足ります。
- **R3 効果量は小さいかもしれない(論点f)**
  - Xではcallあたり約143語を約43語に分けました。Zは約135語を約68語なので、分け方が粗いです。Zの語数別WPMでも、60〜99語と≥100語の差は約2%しかありません(EXISTING_SPEC_CHECK_01.md:45-52)。
  - このため、事前基準の-3%に届かず「判定不能」になる可能性が実際にあります。
  - 対案: 段階運用の②で、B_r2の代わりに(または追加で)細かく分けるarmを、事前に固定して入れる。例: k=ceil(語数/50)、最小25語、約4.3円。こうすれば1回のTrialで「分割の細かさと効果」の関係まで取れます。ユーザー指示「長い地の文のみ追加分割」の範囲内です。
- **R4 声質の参考値**: chunkごとの中央値F0とspectral centroidを、Aの同じ区間と並べて「参考値・判定なし」として表示する(X R3と同じ)。閾値やGateにはしないでください。
- **R5 plannerの小修正**
  - `plan_run`は、段落の結合が一致しないとき、黙って文境界だけの分割に落ちます(er114:139-141)。`paragraph_info_lost`フラグを出力に残してください。
  - `sum(chunk words)==clip word_count`もassertに追加してください。
- **R6 試聴ページ**: OPEN-508(案A本文)の試聴とは別ページだと明記してください。そのうえで、次の2点を書いてください。
  - 「本文はTrial版で、正式再生成版とは異なる。本ページは読み上げ方式の比較のみ」
  - 「本文の良し悪しはここでは判断しない」

### 論点別の所見(要約)
- **(a)** 段落を優先し、次に文境界、引用の途中は除外し、最小25語とするルールは妥当です(1b_s1で引用途中・文途中の切断は0件)。part1の切断は良好です。part2・part3はR1のとおりです。
- **(b)** 既存仕様と整合しています。
  - narratorの内部だけを分けるので、話者切替の境界とVoiceは変わりません。Adv narratorは後処理なしのため、速度v2との干渉もありません。Stdを除外する判断も妥当です。
  - 0.2秒と0.5秒が混在しても不自然になりにくいです。chunk境界の実際の間は、trimの残り(両側)+0.2秒です。Xの実測では、段落間の間がA 0.53秒に対しB0.2 0.54秒でした(TRIAL_RESULT_02.md:27)。clip間(0.5秒+残り)より短く、Aの自然な段落の間と同じ程度で、間の長さの段階が保たれます。前提はN3-2のassertです。
- **(c)** 条件は同一です。
  - 1b_s1のAの3 clipは、いずれも`status: OK`で`gemini-3.8-flash-lite-tts`/Aoedeです(tts_generation_results.json:683-700,1129-1146,1282-1299)。
  - chunk単位のRMS正規化がA側に無いのは問題ありません。「独立したTTS出力ごと」という承認済みの適用単位を両方に同じく当てた結果で、比較対象そのものに含まれます(Xと同じ扱い)。
  - 「chunkに前後の文脈がない」ことは交絡ではなく、検証対象そのものです。
- **(d)** 書込先の隔離とTTSの直列化は良いです。ただしN1(X M1〜M3の引継ぎ)とN2(並行案件下の検知・コード同一性)が抜けています。予算上限の判定には、Perplexityの費用もraw_usage_logに入ることを確認してください。
- **(e)** P6Bとの条件差は大きいです(英語、flash-lite、同じVoice/Style、短い無音、意味の切れ目で分割)。ユーザーが2026-10-25に承認したTrialなので、再導入には当たりません。ただしZは一人称の激情的な独白なので、callごとに感情の強さがリセットされるリスクはXより高いです。X(境界音量差≤5.8dB)はそのまま外挿せず、N4の基準点で測ってください。声質の連続性はユーザー試聴で判断し、R4を補助にすれば足ります。
- **(f)** 費用は妥当です。見積12〜14円は上限30円の内側で、採用した場合も+0.12〜0.2円/Advと軽微です。B_r1+A_r2を先に行い、B_r2は条件付きにする段階運用に賛成です。ただし効果量の懸念(R3)から、②の2本目のarmは「同じ方式の別take」より「細かく分ける版」の方が得られる情報が多い可能性があります。Fableの判断です。
- **(g)** 1b_s1を先に使うのは妥当です(Charter原則2)。Aは生成済み・status OKで、本文の構造も同種です。正式再生成の後、本文が大きく変わった場合だけ、plannerを再実行して分割位置を比べてください(API 0)。

### ユーザー判断が必要な事項
なし。R1のB_alt、R3の細分割armの追加、上限30円以内での配分は、すべてFableの判断範囲です。
---
