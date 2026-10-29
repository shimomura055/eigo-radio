# PHASE0_SYNC_01(WP-C Phase-0: 音声同期方式・閾値の実測、委任_02A、2026-10-29、API 0)

対象: 完成済みの実音声(faster-whisperローカルのみ、API費用0、新規音声生成なし)。生データ=`phase0/res_<fam>_<lv>_<model>.json`、集計=`phase0/summary.json`、`phase0/e2e_{medium,small}.json`、`phase0/kp_blocks_numpy_vs_ffmpeg.json`。再現=`phase0_sync_01.py`(run/e2e)・`phase0_report_01.py`。

| 記号 | 入力 | Std / Adv の文数・行数(script行) |
|---|---|---|
| X | `user_test/family_x_moon_shrinking_reselect_01`(月 reselect。run=`er019_output/.../moon_shrinking__run_reselect_01`) | 63文/11行 ・ 49文/10行 |
| Y | `er121_output/family_y_production_01/redelivery_fee/run_01/pages`(最新完成run。3 Voice、短ポーズ) | 60文/14行 ・ 43文/12行 |
| Z | `user_test/family_z_melos_02`(= run_e2e_06の速度反映後page。話者断片`div.script`複数) | 66文/13行 ・ 74文/12行 |

KP行: X 2+3、Y 3+3、Z 5+5(計24行)。ASRは`faster-whisper medium/int8/CPU`(DEV同一)と`small`の両方を実行。

## 1. 主案の確定(二段整列 vs 直接整列)
| 比較 | 対象 | 境界差 |
|---|---|---|
| 直接整列 vs 二段整列(medium) | X/Y/Z × Std/Adv、計694境界(文の開始・終了。tts_textのある行) | **全6 levelで 中央値0.00s・最大0.00s**(差が出た境界0) |
| 二段整列のdisplay写像 | tts_textのある表示文 347文(全355文中) | exact 345、merged 2(Yの文結合)、split 0、unmatched 0 |
| 直接 vs **DEV最終sync(月Adv、49文・98境界)** | X Adv | 中央値0.00 / p95 0.00 / 最大1.133s。差>0.1sは**2境界のみ**=月Topic intro内の「Moon!」と「The Secret…」の境界(DEV=台本1単位の比例按分16.973s=二段目`split`、本実装=実測無音に吸着17.676/18.106s)。他96境界は差0.05s以下(中央値・p95とも0.00) |
| medium vs small(直接/二段) | 6 level | 最大0.04s(Y Std)、他0.00〜0.02s |

結論:
- **表示文へ直接整列は二段整列と同等(境界差0)**。DEVの`split 8/155`が起きた境界ではむしろ実測無音へ正しく吸着(DEV差の2境界)。直接は`tts_generation_results`/`chunk_plan`/組立記録に依存せず、Y/Zでも成立し、「画面に出す文」が実際に音声で読まれているか(token一致)を直接ゲートにできる。よって**Fable決定の条件(同等以上と実測)を満たす**。
- 実装は両方持つ(`rows[*].tts_text`があれば`align_mode=auto`で二段、無ければ直接。`align_mode='direct'`で強制直接)。**推奨=アダプタ(02B)は`tts_text`を渡さず直接整列を既定にする**(理由: 上記同等性、per-family台本取得の依存・LR/Fallback後のTTS台本とdevページの乖離リスクを避ける)。二段を主案にする場合は02Bが`tts_text`を渡すだけでよい(コード変更不要・testあり)。最終決定はFable。

## 2. token一致率の分布(medium、直接整列、script行のみ)
行長バケット(n_tok)=`<=8` / `9-20` / `21+`。表の値=行ごとの matched/total の最小(min)・中央値。
| 言語・Family | `<=8` | `9-20` | `21+` |
|---|---|---|---|
| en X | (行なし) | 3行 min 0.882 med 0.947 | 12行 min 0.957 med 0.994 |
| en Y | 2行 min 0.857 med 0.929 | 6行 min 0.944 med 1.000 | 13行 min 0.905 med 0.994 |
| en Z | 11行 min 1.000 | (行なし) | 9行 min 0.969 med 1.000 |
| ja X | - | - | 6行 min 0.913 med 0.968 |
| ja Y | - | 1行 1.000 | 4行 min 0.973 med 0.977 |
| ja Z | 1行 1.000 | - | 4行 min 0.939 med 0.970 |
- 全体最小は**X Std Topic intro 15/17=0.882**(「8,900」の読み差)と**Y Std Topic intro 6/7=0.857**(7トークン)。行全体0.90未満は短い行の2行のみ(いずれも内容は正しい)。
- 文単位: **全6 levelで「fully interpolated(1文で一致0、2トークン以上)」0件**。1文の最小一致率はZ Std Part1の0.50(他は0.75以上)。
- 低信頼度境界(短ポーズ/広窓スナップ、警告のみ): X Std 5・X Adv 4(DEV既知の月Advの短ポーズ0.08〜0.14s)、Y 0、Z Std 0、Z Adv 2(下記2-1)。文間ポーズ最小: X 0.08s、Y 0.37s(Yの短ポーズ懸念は実測で顕在化せず)、Z 0.12s。
- small: KP以外は同閾値で全て通る(最小比0.857〜0.870、X Std Japanese title 20/23)。**Z Adv KP2「Current」でsmallはKP照合失敗**(窓ASR=`['c']`)=Y/Zでmedium=small同一とはいえない(KPで差が出る)。

### 2-1 Phase-0で見つかった不具合(実装へ反映済み、testで再現確認)
1. **境界スナップの逆転(DEVにも潜在)**: Z Adv Full Story Part 1の`"Go."`/`I know you'll come back."`(話者断片、間に0.12sの短い谷だけ)で、2番目の境界が**1つ前の境界で使った無音を再選択**し`end<start`(`[39.19, 38.21]`)。DEVはZの話者断片行を未試験だった。→ `align_sentences`で「前の境界の無音終了+0.05s以降の無音のみ候補」に変更(単調性を構造的に保証)。`TestSnapMonotone`は旧実装でFAIL・新実装でPASSを確認。
2. **KP英語区間のASR**: 全体clipを言語自動判定でASRすると、日本語clipでは英語がカタカナ化(Z Std KP5「far bank」→`ファーベンク`、窓ASR空)し照合不能。→ 英語区間(2番目ブロック±余白)だけを`language=en`で切出してASR(1clipあたり約1〜3秒、キャッシュ可)に変更。さらにASRの単語分割差(X Std KP1 `shoving match`→`shove in match`)はトークン照合+連結文字被覆率の大きい方で判定。
3. **Y devページの⏸ポーズ表示**: Yは`div.script`内にclass無し・inline styleの`<span title="実測の停止…">&#9208;0.76s@0:04.6</span>`が入る(X/Zは`class='chunk-mark'`)。本文に混ぜるとトークン列が汚れる(`0.76s@0:04.6`が文頭に入る)ので**アダプタ(02B)で`&#9208;`を含むspanを丸ごと除去**が必要(Phase-0ハーネスは除去済み。WIRING_DESIGN §4の除去対象に「Yのclass無しinline span」を追加すべき)。
4. **KP「ブロック数」**: ffmpeg `silencedetect -40dB d=0.2`の発話ブロック数は(DEV方式の集計で)全KP clipで5(Y Adv KP2は6)、numpy(連続して-40dB未満が0.2s以上=無音)版は全clipで4。ffmpeg版は末尾の無音(silence_end無し)を対にできず最後の発話扱いにする可能性があるが、原因は未確定。**2番目ブロックの時刻はffmpegとnumpyで全29clip最大0.038s差**で、英語区間の選択結果には影響しない。Z Adv KP2「Current」も4ブロック/2番目=英語で正常(5ブロックに見えるのは数え方の差)。`kp_min_blocks=4`で(以上=4,5,…)許容する規則は維持。

## 3. 閾値案(確定値、`DEFAULT_THRESHOLDS`)
- 行ゲート: `matched/total >= 0.90` **または** 短い行(en: `n_tok<=20`、ja: `n_tok<=30`)で「不一致 <= 2(ja 3)かつ比率 >= 0.75、一致>=1」。
  - 根拠: 実測の0.90未満はen 17トークン2不一致(0.882)とen 7トークン1不一致(0.857)のみ。0.90固定だと内容が正しい行でSTOPし、数字・固有名詞の読みで短い行が必ず誤STOPする。一方、長い行は0.90を維持(長い行の欠落はハイライト破綻に直結)。
  - 追加ゲート: **2トークン以上の文で一致0(全補間)が1件でもあればSTOP**(`ENDUSER_SYNC_TOKEN_MATCH`)。実測は全6 level 0件。
- KP: 英語区間ASRの`max(トークン一致, 連結文字被覆率) >= 0.80`、ブロック数>=4(組立記録時刻があればそれを第一根拠で省略可)。実測24行全て1.00。
- 構造不変条件(ハード): 各文`0<=start<end<=音声長+0.05s`、文間単調・重なりなし、sid全件に時刻。実測全て満足(Z Adv Part1は2-1の修正後)。

最終ゲート結果(`phase0/e2e_medium.json`、実API `sync_level`、既定閾値): **X/Y/Z × Std/Adv × (直接/二段) の全12実行(6 level×2方式)がPASS**(最小行比 X Std 0.882、Y Std 0.857、他0.90〜0.97)。

## 4. 所要時間(medium vs small、ASR生出力のみ、他Workerとの並行CPU負荷下の実測)
| model | script行ASR合計(3 set×Std+Adv、音声1,492秒) | RTF | 1セット(Std+Adv)平均 | KP英語区間ASR | 備考 |
|---|---|---|---|---|---|
| medium | 991秒 | 0.66 | 約330秒 + KP約60秒 = **約6.5分** | 14〜60秒/level | DEV同一。Z Adv KP2を含む全KP通過 |
| small | 392秒 | 0.26 | 約131秒 + KP約17秒 = **約2.5分** | 5〜10秒/level | Z Adv KP2でKP照合失敗 |
- 境界時刻は medium vs small で最大0.04s差(実用上同一)だが、**KPの短い単語(Current)でsmallは失敗**。品質を守る(Charter 1)ため**mediumを維持**。ASR所要はキャッシュ(segment mp3 sha256)で再実行時0秒(`sync_level`再実行は6 level全て約1秒)。
- DEV報告の「mediumで約4分/セット」よりも長いのは並行CPU負荷のため。`pages`stageの所要は初回のみ約6.5分、再実行はキャッシュで約1秒。

## 5. 未確認・02Bへの引継ぎ
- 聴感(ブラウザでの再生中ハイライト体感)は未確認(SYNC_METHOD_01と同じ)。
- `episode_offset_check`(全編mp3内`data-t`位置の相互相関)と全編音声長/timeline合計差(WIRING_DESIGN §6-2のゲート(4)(5))は本モジュールに含めていない(アダプタ/validator側=02Bまたは次委任)。
- 02Bへ: 行の`kind=='kp'`の`kp.expressions`(英語表現)を渡す、Yの⏸span除去、Zのspeaker断片は`sentences`をdiv順に連結して渡す。`tts_text`は任意(渡さなければ直接整列)。`sync_level`が返す時刻は**行のsegment mp3先頭からの秒**(episode時刻=`data-t`+秒)。
