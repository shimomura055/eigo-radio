# ER-003-CROSSLEVEL-AUDIO-01 実行報告(A2試聴Feedback反映+B1/B2共通仕様整理)

**管理ID: ER-003-CROSSLEVEL-AUDIO-01**
**実施日: 2026-08-09**
**ステータス: `PROTOTYPE / UNDER_EVALUATION`(複数のCross-level候補を含む、いずれも未DECIDED)**

## 1. A02 Preview修正前後

**修正前**(B1既存承認版、そのまま流用していたもの):
> 英国政府が、16歳と17歳を対象に、深夜0時から午前6時までSNSを止める計画を発表しました。通知やおすすめ表示は自動で止まりますが、設定を変えれば元に戻せます。果たしてこの仕掛けは、深夜のスクロールを止められるのでしょうか。

**修正後**(A2専用の新規Preview、94文字):
> 英国政府が、10代の若者とSNSの使い方をめぐる新しい計画を発表しました。夜のSNS利用を見直すことで、若者の睡眠を守ろうという狙いです。この仕組みは、本当に行動を変えられるのでしょうか。

## 2. Preview変更理由

修正前のPreviewは、「16・17歳」「深夜0-6時」「通知停止」「おすすめ停止」
「opt-out可能」という、後続のComment1/2・Full Story Part1で聞き取らせたい
具体的な答えを既に日本語で説明していた。これによりComment1/2の
Listening Focus/Questionとしての機能が弱まっていた。修正後は、テーマ
(10代とSNSの新計画)・問題意識(睡眠を守る狙い)・聞く価値を生む問い
(本当に行動を変えられるか)のみに限定し、具体的な数字・条件・結論は
一切含めていない。

**重要な構造上の変更点**: これによりA02のA2版Previewは、B1の既存承認
Previewとは**別の音声・別のテキスト**になった(これまでA2はB1の
Previewをそのまま無変更で流用していた)。B1側のPreviewは変更していない。

## 3. Comment 1/2との重複解消確認

新Previewの後、Comment1「まずは、夜になるとSNSがどう変わるのかに注目
して聞いてみましょう」は、"夜になると何が起こるか"という具体的な変化を
まだ明かしていない新Previewに対して、意味のあるListening Focusとして
機能する(修正前は「深夜0-6時」「通知停止」等の答えを先に知っていたため
重複していた)。Comment2「では、利用者はこの設定を自分で変えられるので
しょうか」も、新Previewが「設定を変えられるか」に触れていないため、
Full Story Part1を聞く動機として機能する。ASR全文確認(13節)で実際の
接続を確認済み。

## 4. Comment 4修正前後

**A02**
- 修正前: 「最後に、今日のニュースを英語一文でまとめます。」
- 修正後: 「最後に、今日のニュースのポイントを英語で聞いてみましょう。」

最初の2文(「夜のルールだけで...」「でも、最初の設定を変えるだけで...」)
は変更していない。

**A01・ADD03(テキストのみ更新、音声化はしていない)**
- A01: 「最後に、この試合を英語一文で振り返ります。」→「最後に、この試合のポイントを英語で振り返ります。」
- ADD03: 「最後に、今日のニュースを英語一文でまとめます。」→「最後に、今日のニュースのポイントを英語でまとめます。」

いずれも既存の文体・語尾(A01「振り返ります」、ADD03「まとめます」)を
保ち、機械的なコピーはしていない。[ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md)、
[ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md)へ反映済み。

## 5. Key Phrase語末音素調査結果

`er003_b1_p3u_audio.trim_english_keyword_silence`(既存の英語Key Phrase
音声トリム関数)の実装を確認した。20msウィンドウ・RMS閾値0.02で発話
区間を判定し、前後に0.08秒の安全マージンを加える方式。既存の
"personalized feed"音声(旧版)の末尾波形を解析したところ、末尾は
なだらかにRMSが減衰するのみで、明確な破裂音(/d/の release)に相当する
二次的なエネルギーの盛り上がりは見られなかった。**トリムによる
削り過ぎというより、TTS生成そのものが語末子音を弱く発音した可能性が
高いと判断した**(トリム関数は検出した発話区間の最後まで実際には
保持しており、0.02秒の余白到達前に切れてはいなかった)。

## 6. A02で再生成したKey Phrase

Key Phrase 4「personalized feed」のみ、試作として再生成した。標準の
`ENGLISH_STYLE_PREFIX`・`MINIMAL_INSTRUCTION_PREFIX`(いずれも既存、
無変更)とは別に、今回の試作専用instruction("...make sure the very
last sound of the phrase is actually spoken, not trailed off into
silence... do not over-emphasize or exaggerate any single sound.")を
新規定義し、trim安全マージンも0.08秒→0.15秒へ広げて生成した。

末尾エネルギー解析の比較:

| | 旧版(末尾300ms) | 新試作版(末尾300ms) |
|---|---|---|
| 波形の特徴 | なだらかな減衰のみ、破裂音相当の二次ピークなし | 約1.39〜1.43秒付近に0.03〜0.04のRMSを持つ明確な二次ピークあり(その後急減衰) |
| 総尺 | 1.451秒 | 1.591秒(140ms長い) |

新試作版には、旧版になかった語末の音響的な盛り上がりが確認できた。
これは/d/の破裂・気息が実際に音として記録された可能性を示唆する。
**ただし、これは波形上の状況証拠であり、実際に自然に聞こえるかは
別問題である。最終判断はユーザーの試聴に委ねる**(10節参照)。

## 7. 語末音素の機械QA可否

ご指摘の5つの調査観点への回答:

1. **どの程度起きるか**: 今回は"feed"1件のみを深掘り調査した。A01/A02/ADD03の全Key Phrase Componentを体系的に走査してはいないため、発生頻度は不明(推測で埋めない)。
2. **ASR/forced alignmentで量産時に検出できるか**: 現行のstrict ASR検証(部分一致+文字数上限)は**検出に向いていないと判断した**。ASRは言語モデルによる補完(トップダウン予測)で、語末の音響的証拠が弱くても文脈から正しい単語を書き起こす傾向があり、実際に今回の旧"feed"音声もASR検証(部分一致)には合格していた。forced alignment(MFA)であれば、語末音素の継続時間や信頼度スコアを個別に測定し、極端に短い/不確実なケースを候補として検出できる可能性があるが、**今回は検証していない**(未実装、将来候補)。
3. **TTS instructionで自然に改善可能か**: 6節の波形比較からは改善の兆候が見られたが、1語1回の試行のみであり、他の語(opt/switch等)への一般化は未検証。
4. **instructionが語末強調しすぎて不自然にならないか**: 機械では判定できない。ユーザー試聴による確認が必須。
5. **再生成条件を一般化可能か**: 今回のinstruction文言・trim余白の拡大という組み合わせ自体は、他のKey Phrase Componentにもそのまま適用可能な形で実装した(`generate_key_phrase_trial_clarity`関数、text/out_pathを引数に取る汎用関数)。ただし効果が実証されたのは今回の1件のみ。

## 8. 語末音素について残る人間確認事項

- 新試作版"personalized feed"(Key Phrase 4、完成音声の約2分00秒付近)を実際に聴き、語末の/d/が自然に知覚できるか
- 子音が不自然に強調されすぎていないか
- この方式を他のKey Phrase(A01/A02/ADD03の他の項目)へも広げるべきか、それとも個別に確認が必要なケースのみに適用すべきか

## 9. ポイント解説後ポーズ変更前後

修正前: 0.5秒 → 修正後: **0.7秒**(+0.2秒)。この値は既存の
`er003_v1_repro01_main_generate.py`(A02 B1組立)等、記事ごとの組立
スクリプトに個別にハードコードされており、共通定数として一元化はされて
いない(OPEN_ITEMS OPEN-25に記録)。今回はA02試作の該当箇所のみ0.7秒へ
変更し、他のポーズ値(Comment前後の1.0秒/0.8秒、その他の0.5秒/0.4秒/
0.65秒)は一切変更していない。

## 10. Outro音楽レベル処理の変更内容

既存のOutro音量処理(Introの調整後RMSへ一致させるgain matching)は維持
した上で、その後に追加の減衰を乗じた。amplitudeの単純な0.8倍ではなく、
心理音響上の知覚音量を狙った計算式を用いた。

## 11. 「4/5体感」をどのように候補化したか

一般的な音響工学上の経験則「10dBの増減で知覚音量がおよそ2倍/半分に
なる」(Stevens損失指数則に基づく近似)を用いた。知覚音量を80%(4/5)に
するための減衰量を、`dB = 10 × log2(0.8) ≈ -3.22dB`として算出し、
線形振幅倍率へ変換すると`10^(-3.22/20) ≈ 0.693`となる。この0.693倍を、
既存のIntro基準RMS一致ゲインの**後に追加で乗じた**(既存のOutro音量
決定ロジック自体は変更していない)。単純な0.8倍(自然な感覚では
「気持ち小さくなった程度」にしかならない)ではなく、より踏み込んだ
減衰にしている点に注意されたい。

## 12. A02完成音声タイムライン

主要区間の開始・長さ(全区間は`er003_output/a2_audio_02/A02/audit/timeline.json`参照):

| Part | Start(s) | Duration(s) |
|---|---:|---:|
| Intro | 0.000 | 10.736 |
| ... (Welcome〜Notification1、A2-AUDIO-01と同一区間) | | |
| Point explanation | 33.529 | 1.220 |
| **pause_0.7_point_explanation(新)** | 34.749 | **0.700** |
| Preview(**新版**) | 35.449 | 18.020 |
| ... (Notification2〜Key Phrase 3、同一区間) | | |
| **Key Phrase 4(試作版)** | (Key Phrase 1〜3に続く位置) | (試作版の尺に応じて可変) |
| ... (Key Phrase 5〜Comment3、A2-AUDIO-01と同一区間) | | |
| Point One | 同一 | 33.511 |
| Point Two | 同一 | 33.071 |
| Comment 4(**新版**) | 可変 | 14.800 |
| pause_0.8_ja_to_en | | 0.800 |
| In One Line | | 13.611 |
| pause_0.5 | | 0.500 |
| Outro(**減衰版**) | | 6.144 |

## 13. 完成音声総尺

**309.934秒**(約5分10秒)。A2-AUDIO-01(310.414秒)とほぼ同じ
(Preview短縮とポーズ+0.2秒・Comment4文言変更等が相殺し、総尺の差は
0.48秒のみ)。

## 14. ASR / content QA

個別新規segment(Preview V2、Comment4 V2、Key Phrase 4試作)は3件とも
strict ASR検証に初回で合格した。完成音声全体をAzure STT(en-US/ja-JP、
timeout 300秒)で全文確認し、新Preview・新Comment4を含む全パートが
欠落なく含まれていることを確認した(15節参照)。

## 15. hallucination有無

**検出されなかった。** ASR全文確認で、新規生成した3segment(Preview
V2/Comment4 V2/Key Phrase4試作)を含む全パートの内容が過不足なく
含まれていることを確認した。前回(ER-003-A2-AUDIO-01)で確認された
ASR数字表記ゆれ(Comment3「二つ」、Point Two"7 in 10")は今回も同様に
現れたが(音声自体は変更していないため)、これは既に「TTS内容としては
正常」と判断済みの事象であり、hallucinationではない。

## 16. Cross-level共通仕様候補として記録した内容

[OPEN_ITEMS.md](OPEN_ITEMS.md)へ新規4件を記録した(状態は指示どおり
`DECIDED`にはしていない):

- OPEN-23: Preview原則(具体回答を先に言いすぎない) — `CANDIDATE / USER_DIRECTION_CONFIRMED`
- OPEN-24: Key Phrase語末音素品質 — `UNDER_INVESTIGATION`
- OPEN-25: 「ポイント解説」後ポーズ+0.2秒 — `CANDIDATE / TO_BE_LISTENED`
- OPEN-26: Outro音量4/5体感 — `CANDIDATE / TO_BE_LISTENED`

いずれもA02試作にのみ反映し、既存のB1/B2完成音声・既存Preview全記事の
一括再生成や差し替えは行っていない。

## 17. A2固有として記録した内容

Comment4の文言修正(「英語一文でまとめます」→「ポイントを英語で聞いて
みましょう/まとめます/振り返ります」)は、In One Lineが中心1文+補足2文の
計3文構成であるA2固有の事情によるものであり、Cross-level候補には
含めていない([A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)へ反映)。

## 18. Source of Truth更新

- [OPEN_ITEMS.md](OPEN_ITEMS.md): 新規4件(OPEN-23〜26)を「Cross-level
  (A2/B1/B2共通)候補」節として追加
- [ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md)、
  [ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md):
  Comment4の末尾文言をテキストのみ更新(音声は生成していない)
- A2構造全体のステータスは引き続き`PROTOTYPE / UNDER_EVALUATION`。
  CURRENT_SPECへは反映していない

## 19. 作成・変更ファイル

- 新規: [er003_v1_a2_audio_02_generate.py](er003_v1_a2_audio_02_generate.py)
- 新規: `er003_output/a2_audio_02/A02/narration/*.wav`(Preview V2・Comment4 V2・Key Phrase4試作)
- 新規: `er003_output/a2_audio_02/A02/assembled/*.wav`, `*.mp3`
- 新規: `er003_output/a2_audio_02/A02/audit/*.json`, `*.txt`(検証記録・タイムライン・ASR全文・語末エネルギー比較)
- 新規: 本レポート
- 更新: [OPEN_ITEMS.md](OPEN_ITEMS.md)
- 更新: [ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_A01_INTEGRATED_SCRIPT.md)、[ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md](ER-003-A2-STRUCT-04_ADD03_INTEGRATED_SCRIPT.md)(Comment4文言のみ)
- ER-003-A2-AUDIO-01の成果物・B1既存資産・共有凍結モジュールは一切変更していない

## 20. テスト結果

プロジェクト全体回帰テスト: **1660件全合格**。既存の凍結モジュールへの変更は行っていない。

## 21. Git status

音声ファイル(`.wav`/`.mp3`)は`.gitignore`により追跡対象外。コード・監査JSON・レポート・テキスト更新のみをcommit対象とする。

## 22. commit

コミット済み(詳細はcommitログ参照)。

## 23. push未実行確認

**pushは実行していません。**

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、
[ER-003-A2-AUDIO-01_REPORT.md](ER-003-A2-AUDIO-01_REPORT.md)
