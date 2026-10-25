# WIRING_RUNTIME_EVIDENCE_01 (FX-CORE-NUMERIC-RETENTION-TRIAL-01 委任_07、2026-10-25)

正式Production経路(Family X news runner)に配線した中核数値保持方式v4+J2の**正式runtime検証**。対象=月(`moon_shrinking`、公開版は数値脱落=本方式の出発点)。run=`er019_output/moon_shrinking/run_ms_03`(Std/Adv完全再生成: B3→丸め→R0→R1→R2→EN Adv→RF→EN Std→RF→[audio]→組立→試聴ページ)。公開済みの既存ページ(`user_test/family_x_moon_shrinking_01/`)は差し替えない(完成候補は`user_test/family_x_moon_shrinking_02/`、ユーザー最終試聴待ち=USER_LISTENING_PENDING)。

## 1. 起動・条件
- 配線commit=`44b18d41a`(Production実装+test、push済み)。text段は同commitの作業ツリーから実行(import graph内の他agent未commit差分は`er006_model_routing_contract_01.py`の追加キー1行のみ=text段の挙動に無関係)。
- text: `er019_family_x_entertainment_production_runner_01.py --stage all --budget-jpy 100 --run-label run_ms_03`、1起動、再起動0。開始 JST 11:56:15、終了 約12:02:20(約6分)。`research_ledger`は`run_ms_01`から複製(Research/Ledgerは再実行しない=方式の検証対象外。B3以降は新規)。起動前`stop_scope_check` rc=0(`stop_check_text_ms03.json`)。
- 日次(JST)集計(`docs/pm/tools/daily_dev_cost_01.py`、text起動前790.09円→text後818.19円)。audio見積≤50円で1,000円内。

## 2. B3(v4、actual `gpt-6.1-sol`)
- 欄 `reader_must_hear_numbers` = `["約42〜46 m"]`(1回目=最終。M1合格、**B3再実行0**、`numeric_retention_b3.json: b3_rerun=false, mode=field_ok`)。Storyline: 「LROの月面画像で『しわ』を地図化し、後期の半径収縮を約42〜46 mと推定したが、熱史全体を扱う冷却モデルの予測より小さい理由は未解決で、砕けた岩の層の断熱効果が候補に挙がっている。」(= B3が選んだ切り口に対する数値)。
- v4指示文sha(base)=`a7b643ba41d6…`(Trialの`D.B3_ADDENDUM_V4`と同一)、`numeric_retention_b3`: `m1_retry=false`、attempts 1(技術retry 0)、`field_present_in_output=true`。
- E = {約42〜46}(`gate_E`)。`observe_E`=空。O-2': e_dimensions=[length]、demote=[](B3が750m等の別Factを採用しなかったため付替え対象なし。非Eの中核は『1』[km、単位なし小整数]・『約5,470本』・『8,900本超』=別単位系/単位不明のため残す)。

## 3. 各段の保持(照合=較正済み`match_core`、EN=`en_present`)
| 段 | 約42〜46 | 備考 |
|---|---|---|
| R0 | あり(『約42から46 m縮んだ』) | R4入力正規化により波ダッシュなしで出力。J2(R0出力)適用0件。Gate: 不足なし、再生成なし |
| R1 | あり(『約42から46メートル』) | J2適用**1件**(R1がR0の「から」を「〜」へ書き戻した=OPEN-509の再現。`raw_sha256_before_norm`記録) |
| R2 | あり(『約42から46メートル』) | J2適用**1件**。記号QA findings=0、再実行0 |
| EN Adv | あり(about 42 to 46 meters) | 観察のみ(WARN 0)。波ダッシュなし |
| EN Std | あり(about 42 to 46 meters) | 同上 |
- Gate発火=0(R0/R1/R2とも初回で保持)、R1再実行0、R2再実行0、M2新規数値(R1/R2)=0、周辺数値混入=0。【中核数値】【周辺数値】の印の書き写し=0。
- 不要数値: 事前の固定表(750m・4億年前・11cm・9.14等)の復活=0(B3がそれらのFactを採用しなかった)。非E中核の掲載=『8,900本超』(題と冒頭の導入。別単位系[本]のためO-2'の対象外=仕様どおり)。→Fable確認事項(§6)。
- 数字丸め(承認済み仕様): overlay `status=OK`、判断=『8,900本超』のみ`APPROXIMATE_OK`(約9,000本超)、`約42〜46`/`約5,470本`/`1`=`EXACT_REQUIRED`。EはEXACT_REQUIREDの『約42〜46』として**表記のまま**全段保持(丸め・換算・中点『約45』なし)。J2は数字・桁を変えない(本文の数字列比較で不変を確認)。不要な桁数の復活なし。
- 禁止表現(『今も』『急速』『近いうち』『目に見え』『崩壊』『毎年』『ずっと』『縮み続け』『一定の速』/EN rapid・still shrinking・visibly等)の本文grep=0。誤解表現WARN(heuristic)は『誕生以来』1件=『月は誕生以来、それだけしか縮んでいないのか」と思ったら、ちょっと待った。…誕生から現在までの総決算ではない』という**正しい打ち消し**(否定語の位置が検出窓外=偽陽性)。

## 4. actual model・prompt・routing(`ja_writer/runtime_evidence.json`、`storyline_b3/runtime_evidence.json`)
- B3: `gpt-6.1-sol`(routing `FAMILY_X_STORYLINE_B3`、effort high、response_id `resp_0ec61c84…`)。丸め判断: `gpt-6-luna` low。W-1 R0/R1/R2: `gpt-6.1-sol`(routing `FAMILY_X_FACTLOCK_R0`/`_REVISE`、`model_mismatch`なし)。EN Adv/Std・RF: 既存どおり(`gpt-6-luna`ほか)。
- R0 Prompt sha=`ed6e153e3a4b…`(R4入力正規化後)、`verbatim_shas`(規則5=`FACTLOCK_R0_BLOCK_HEAD` `e72822deeabf…`・`R0_PROMPT` `6108a7cddaa9…`)はTrial/既存と不変。
- 費用: text 25.426円(B3 11.483/丸め 0.119/R0 5.322/R1 3.776/R2 2.042/Adv 0.515/Std 0.366/RF 1.805)。**参考**: `run_ms_01` textは49.76円だがresearch 5.82+ledger 9.10(今回は複製して非再実行)とR0の記号QA再生成6.23(今回は発生せず)を含む。方式由来の追加費用の実測=**0円**(B3再実行0・Gate再生成0・追加LLM call 0。B3 11.48円は参照12.07円と同水準)。

## 5. audio・page
(audio run: JST 12:31:34起動、`er019_family_x_audio_production_runner_01.py --level both --stage all`、他agentのPart 1 T1(翻訳工程)が同runnerへ入ったHEADで実行)
- **Adv(b1b)**: TTS 48 segment全OK、HR 0。ASR転写に『about 42 to 46 meters』。Part 1はT1翻訳(`--stage study_text`、0.12円)を追加実行して解決(scaffold後にT1が必須化されたため。scaffold再実行なし)。assemble/player完了(`b1b/assembled/Family_X_Audio_B1_MOON_SHRINKING.wav`)。
- **Std(a2) 1回目**: 51 segment OK・2 STOPPED。(i) `comment_2`: A2 support生成LLMが範囲値『約42〜46メートル』を波ダッシュで出力(Writer段J2の適用点の外)→TTS用Normalizerが『42なになに46』→ASR NG(NG_BOTH)→STOPPED。(ii) `japanese_title`『月のしわ、8,900本超！…』: ASRが数値を『8000900本』等と転写し`p1_value_diff`でNG→STOPPED。
- **是正(同じJ2の目的・数字桁不変)**: `_a2_run_support_text_j2`(A2 support本文生成直後にJ2)を追加(test追加)。run_ms_03の`a2_support_texts.json` comment_2へ同じ決定論変換を適用(原本は`audit/a2_support_generation.json`、`audit/a2_support_j2_applied.json`にsha記録)→`--level a2 --stage tts --only-segments japanese_title,comment_2`(1回、+0.24円): **comment_2 OK(ASR『約42から46メートル』PASS、なになになし)**。
- **未解決(HR Lock、回避せず)**: `japanese_title`は`HUMAN_REVIEW_LOCKED`(同一テキストの再生成はロックが拒否=正しい動作)。このためStd組立は`EPISODE_BLOCKED_BY_AUDIO_VALIDATION: japanese_title=UNVALIDATED`で停止、Std wav/試聴ページ(user_test/family_x_moon_shrinking_02)は未作成。原因は非E中核『8,900本超』が題に載ったこと(§6-2)。解決案: (a)人間のロック承認(音声が正しく読めていれば承認)、(b)題から数値を外す/変更する(題生成仕様=新仕様候補)。
- 音声費用15.19円(text 25.43円と合計約40.6円。日次JST 862円、上限1,000円内)。

## 6. Fable確認事項(受入観察事項)
1. **欄の1回目値**: 月=`約42〜46 m`(望ましい値)。最初の数記事で欄の1回目(`numeric_retention_b3.json: first_pass.field_items`)・半導体型の初回選定傾向を確認。
2. **非E中核『8,900本超』**: 題と導入に使われた(崖の本数=『しわ』の導入)。Writerの規則5上は許可された中核数値で、B3の切り口(縮みの推定量)とは別の補足数値。Trialの月標本(r6m1/r6m2)では非E中核の掲載0だった。「数値の羅列」ではない(本文の数値は2種)が、切り口基準で不要と判断する場合は、仕様候補(別単位系の補足数値も周辺扱い)は新仕様=未実装・ユーザー判断事項。
3. C-2(委任_06)の観察: v4は数値が中心でない記事でも欄に1個入れる傾向(2/2)があり、そのうち1つは境界(manga『2作品、4人』)。欄の数値は`gate_required`ならGate対象のため、本文に入らなければ再生成枠→STOPに乗り得る(品質上は数値が確実に本文へ入る側)。
4. 英訳の数値観察はWARNのみ(Gate化なし)。
