# ER-003-B1-P6A 実行報告(本編分割・接続方式のPreview適用検証)

## 1. 検証目的

本編(ER-002以来の記事ナレーション基盤)が実際に使っている日本語音声の分割生成・
接続方式をコードから具体的に特定し、その要因をPreviewへ適用することで、
「Gemini TTSの自然な日本語音声を維持」「全文一括生成での省略を避ける」
「分割生成での声色・抑揚・語尾の不連続を避ける」の両立可能性を検証する。

## 2. 本編の対象実装・成果物

以下のコードを実機で読み、推測ではなく実装から直接確認した。

| 項目 | ファイル/関数 |
|---|---|
| 台本→3chunk変換 | `er002_common.build_narration_plan` |
| chunkごとのTTS呼び出し | `er002_common.run_tts_content_attempts` |
| chunk結合(無音挿入) | `er002_common.assemble_audio` |
| PCMピーク正規化(chunk単位) | `er002_common.normalize_pcm` |
| Dynamics3適用 | `er002_common.apply_dynamics3_once` |
| 全体オーケストレーション | `er002_runner.run_article` |
| 共通演技指示 | `er002_common.COMMON_BASE_INSTRUCTION` / `LEVEL2_INSTRUCTION` / `POINT_LABEL_FIDELITY_RULE` |

**重要な留意点**: 本ステージ実行時点で、日本語B1本文の「本編」音声は実際には
まだ一度も生成されていない(ER-003-B1-P3RはListening Preview生成が失敗した
時点で停止し、B1本文のTTS callは0回)。したがって本レポートで言う「本編」とは、
ER-001B-9/10以来ER-002の英語記事ナレーションで繰り返し採用・実運用されてきた
共通基盤(`er002_common.py`)の設計そのものを指し、日本語B1本文での実運用実績を
指すものではない。この前提を明示したうえで、コードベースから読み取れる設計・
実装事実のみに基づいて監査した。

## 3. 本編の分割ルール

| 項目 | 結果(コードから直接確認) |
|---|---|
| 分割単位 | 記事の構造境界のみ(①タイトル+本文段落、②Points見出し+Point One+Point Two、③In One Line見出し+段落) |
| 1chunkの文字数・秒数 | 台本構造依存(固定値なし)。3chunk構成が`EXPECTED_CHUNK_COUNT=3`として確定仕様 |
| 文中分割 | **していない**。各chunkは複数paragraphを`"\n\n".join(...)`で連結した1つのテキストブロック |
| 優先する境界 | 句読点・呼吸位置ではなく、**記事の構造(見出し)** |
| 最短・最長chunkの条件 | 明示的な制約コードはなし(構造上、body/points/finalの3分割に自然に収まる) |
| 短すぎるchunkを避ける処理 | 専用処理はない。ただし構造分割自体が短すぎるchunkを生みにくい設計 |

## 4. 本編のTTS生成条件

| 項目 | 結果 |
|---|---|
| voice | 記事ごとに指定(config["voice"]、例: Aoede/Charon) |
| モデル | `gemini-2.5-pro-preview-tts`(`MODEL_NAME`) |
| 表現指示 | `COMMON_BASE_INSTRUCTION + LEVEL2_INSTRUCTION + POINT_LABEL_FIDELITY_RULE`(`build_style_prefix()`) |
| Level | 2固定(LEVEL2_INSTRUCTION) |
| speed指定 | **なし**(`assert_no_wpm_specification`で数値指定を明示的に禁止) |
| chunkの独立性 | **完全独立**。`run_tts_content_attempts`内で、chunkごとに`_call_tts_with_retry(tts_call_fn, style_prefix + text, ...)`を個別呼び出し |
| 前後文脈の共有 | **なし**。各chunkのプロンプトは「共通style_prefix + そのchunkのテキスト」のみ |
| session/seed/temperature制御 | コード上に該当設定なし(`GenerateContentConfig`は`response_modalities`/`speech_config`/`http_options`のみ) |
| chunkごとの生成条件変化 | **なし**。全chunk同一のstyle_prefix・voice・configを使用 |

**自然さを維持している直接の要因(実装から確認)**: `COMMON_BASE_INSTRUCTION`
自体に次の一文が含まれている。

> "Treat the narration as one continuous program, even when it is generated
> in separate sections."

これは「複数回に分けて生成しても、1つの連続した番組として扱え」という
明示指示であり、chunkが独立生成であるにもかかわらず声の一貫性を保つ直接の
要因と考えられる。この行は、日本語用instruction(`JAPANESE_STYLE_PREFIX`、
P3Y以降採用、言語指定の先頭1行だけを差し替え、それ以外は無変更)にも
**そのまま残っている**ことを確認済み。つまりP4B/P4Cも実は同じ継続性指示を
使っていたが、それだけでは6chunk・文中分割という条件下では不十分だった
ことになる(後述の差分表参照)。

## 5. 本編の接続・後処理

| 項目 | 結果 |
|---|---|
| chunk間無音 | 固定0.8秒(`SECTION_JOIN_PAUSE_SECONDS`)。2件目以降のchunkの前にのみ挿入(`assemble_audio`) |
| crossfade | **なし**(単純な無音サンプルの挿入のみ) |
| 音量合わせ | 各chunkのPCMを個別に**ピーク基準正規化**(`normalize_pcm`、target_peak=0.7)。loudness(LUFS)ベースの正規化はchunk単位では行わず、最終段のDynamics3内でのみLUFSマッチングを実施 |
| DC offset除去 | 該当処理は確認できず |
| 呼吸音・無音のtrim | **なし**。各chunk先頭・末尾の自然な無音はそのまま残し、trimしていない |
| Dynamics3の適用単位 | **結合後の全体波形へ1回だけ**(`apply_dynamics3_once`、`tts_result.accepted_audio`に対して) |
| その他後処理 | QA評価(embedded/grounded)は結合後の全体音声に対して実施 |

## 6. 本編とP4Cの差分表

| 項目 | 本編 | P4C(6chunk方式) |
|---|---|---|
| 分割数 | 3 | 6 |
| 分割位置 | 構造境界(見出し) | 文および読点(1marker=1chunkに強制) |
| 文中分割 | なし | **あり**(読点で追加分割) |
| 1chunkあたりmarker数 | 該当なし | 最大1(設計上の制約) |
| TTS入力 | 複数paragraphを結合した1ブロック | 1文(場合により節単位) |
| プロンプト | 共通style_prefix+chunkテキスト | 同左(同一関数を再利用) |
| 前後文脈 | なし(chunk独立) | なし(同左) |
| voice・Level | Aoede/Emotional+Connected/Level2 | 同一 |
| chunk間無音 | 固定0.8秒 | **追加無音なし**(自然な無音のみ、実測0.40〜0.64秒) |
| crossfade | なし | なし |
| 音量調整 | chunk単位ピーク正規化 | 同一関数(`normalize_pcm`)を経由(TTS応答の正規化自体は共通処理) |
| Dynamics3の順序 | 結合後1回 | 結合後1回(同一方針) |
| 最終後処理 | QA評価(embedded/grounded) | なし(Preview系にQA評価の仕組みは未実装) |
| ユーザー評価結果 | ER-002系で複数記事の承認実績あり(日本語B1本文への適用実績なし) | **不合格**(声色差・「わずかなリード」の抑揚不自然・close the door to the final周辺の分断) |

**P4Cが本編方式を使っていなかった理由**: P4Cは「英語Key Phrase 1件=1chunk」
という設計を明示的に採用しており(P4B/P4Cの指示書自身が「1chunkにKey Phraseを
1件だけ含める」ことを要件としていた)、本編の「構造境界のみで分割し、1chunkに
複数の意味的要素を含めてよい」という設計とは根本的に異なる分割思想だった。
また、本編の固定0.8秒無音は、英語Key Phraseとの接合には使われず(英語切替の
実効間隔仕様0.40秒/0.30秒は別途P3Z検証で確立)、通常chunk境界にのみ想定されて
いたため、P4Cでは「固定無音を足さない」方式を独自に採用していた。

## 7. Previewで採用した分割数と各chunk

**4chunk**(Pattern A原文の「。」区切りそのまま。読点での追加分割はしていない)。

| chunk_id | source_text | used_forms |
|---|---|---|
| 01 | 前半は激しい接触と緊張が続き、両チームとも枠内シュート、shot on targetを記録できないまま、静かな均衡が保たれます。 | shot on target |
| 02 | 後半に試合が動くと、イングランドは選手を交代で下げる、take players offという決断で守備を固め、わずかなリード、a narrow leadを守ろうとします。 | take players off, a narrow lead |
| 03 | アルゼンチンの決勝への道を閉ざすこと――close the door to the final――が現実になりそうなその時、メッシが流れを変え、ついにアディショナルタイム、stoppage timeへ。 | close the door to the final, stoppage time |
| 04 | 最後の数分、歓喜と痛みの境目で何が起きるのでしょうか。 | (なし) |

## 8. その分割を選んだ理由

Pattern A原文は本来4つの文で構成されており(「。」区切り)、P4B/P4Cはこれを
「1marker=1chunk」の制約のために6chunkへ人為的に追加分割していた(文2・文3を
読点でさらに分割)。本編の設計思想(構造境界のみで分割、1chunkに複数要素を
含めてよい)に従えば、Pattern A本来の4文構造をそのまま維持するのが最も
本編に近い。文2・文3にそれぞれ2件のused_formが含まれることになるが、これは
新たな技術的課題ではない(P4/P4Aで実証済みの`find_all_marker_spans`による
出現順ベースの対応づけをそのまま再利用できる)。

## 9. 実際の各TTS入力

| chunk_id | TTS入力(目印置換後) |
|---|---|
| 01 | 前半は激しい接触と緊張が続き、両チームとも枠内シュート、目印を記録できないまま、静かな均衡が保たれます。 |
| 02 | 後半に試合が動くと、イングランドは選手を交代で下げる、目印という決断で守備を固め、わずかなリード、目印を守ろうとします。 |
| 03 | アルゼンチンの決勝への道を閉ざすこと――目印――が現実になりそうなその時、メッシが流れを変え、ついにアディショナルタイム、目印へ。 |
| 04 | 最後の数分、歓喜と痛みの境目で何が起きるのでしょうか。(無変更) |

marker「目印」はP4Cで既に自然さを損なわないことを実証済みのため、そのまま
再利用した(変更なし)。

## 10. TTS call数

4回(chunk01〜04、各1回)。技術的retryは0回(全て初回成功)。

## 11. 接続処理

本編の実装(`common.assemble_audio`)をそのまま再利用する設計とし、chunk間に
`SECTION_JOIN_PAUSE_SECONDS`(0.8秒)の固定無音を挿入する予定だった。
**ただし、chunk03のmarker置換段階で停止したため、4chunk結合はまだ実行して
いない**(未到達)。

## 12. Dynamics 3の適用箇所

結合後の全体波形へ1回だけ適用する設計(本編と同一方針)。**未到達のため
未実施**。

## 13. 原稿忠実性QA

### chunk分割の静的検証(TTS呼び出し前)

| 項目 | 結果 |
|---|---|
| chunk結合 → Pattern A原文と完全一致 | 合格 |
| 5 used form残存 | すべて0 |
| 「目印」出現数合計 | 5(想定通り) |
| ASCII英字残存 | 0 |
| 「選手を交代で下げる」原文中に存在 | 合格 |
| 「という決断で」原文中に存在 | 合格 |
| 「守備を固め」原文中に存在 | 合格 |
| 「最後の数分」原文中に存在 | 合格 |
| 「何が起きるのでしょうか」原文中に存在 | 合格 |
| **総合判定** | **全項目合格、TTS実行可** |

### chunk別ASR診断結果(生成後、診断用途のみ)

| chunk_id | ASR認識結果 | marker検出数(期待) | 全文一致率 | 判定 |
|---|---|---|---|---|
| 01 | 前半は激しい接触と緊張が続き、両チームとも枠内シュートを目印を記録できないまま静かな均衡が保たれます。 | 1(1) | 0.9897 | 合格 |
| 02 | **後半に試合が動くと、イングランドは選手を交代で下げる目印という決断で守備を固め、わずかなリード目印を守ろうとします。** | 2(2) | **1.0(完全一致)** | 合格 |
| 03 | アルゼンチンの結晶への道を閉ざすこと。目印が現実になりそうなその時、メッシが流れを変え、ついにアディショナルタイムへ目印。 | 2(2) | 0.9153 | 合格 |
| 04 | 最後の数分。寒気と痛みの境目で何が起きるのでしょうか。 | 0(0) | 0.92 | 合格 |

**特筆すべき結果**: chunk02(「選手を交代で下げる」「という決断で」「守備を
固め」「わずかなリード」を全て含む)のASR認識結果は、**目印を除いて原文と
完全一致(一致率1.0)**。P4Bで問題となった「で下げる」「という決断」の欠落は、
今回は一切発生していない。P5C(GCP漢字かな交じり単独)でも同様の改善が
確認されており、今回さらに「文境界のみでの分割」でも同じ良好な結果が
再現された。

chunk03には軽微なASRノイズ(決勝→結晶、句点の挿入位置、「タイムへ目印」の
語順)が見られるが、これらはこのプロジェクト全体で繰り返し観測されている
ASR側の同音異義語・区切りの癖と一致するパターンであり、TTS発話そのものの
欠落ではない可能性が高い(断定はしない)。

## 14. ASR診断(まとめ)

指示section10の6対象句のうち、chunk02の範囲に含まれる4句(選手を交代で
下げる/という決断で/守備を固め/わずかなリード)は、ASR上完全な形で検出
された。「最後の数分」(chunk04)・「何が起きるのでしょうか」(chunk04)も
検出された。ASR結果は診断情報であり、これをもって品質合格とは判断していない。

## 15. 試聴音声の場所

**完成したPreview音声は存在しない(パイプラインがchunk03の英語置換段階で
停止したため)。** 以下の中間成果物のみ試聴可能。

| 項目 | path | 内容 |
|---|---|---|
| chunk01(日本語+目印) | `preview/ja_chunks/chunk01_ja.wav` | 目印入り、置換前 |
| chunk02(日本語+目印) | `preview/ja_chunks/chunk02_ja.wav` | 目印入り、置換前 |
| chunk03(日本語+目印) | `preview/ja_chunks/chunk03_ja.wav` | 目印入り、置換前 |
| chunk04(日本語) | `preview/ja_chunks/chunk04_ja.wav` | 無変更 |
| chunk01(英語置換済み) | `preview/replaced_chunks/chunk01_replaced.wav` | shot on target置換済み |
| chunk02(英語置換済み) | `preview/replaced_chunks/chunk02_replaced.wav` | take players off / a narrow lead置換済み |

chunk03の英語置換・4chunk結合・Dynamics3適用・最終Preview生成のいずれも
未実施。

## 16. 原因の詳細(chunk03停止)

chunk03には2件のmarker(close the door to the final、stoppage time)があり、
2件目(stoppage time)の直後には「へ。」という非常に短い残りテキストしかない。
MFAで特定した2件目markerの終了時刻(10.83秒)からchunk全体の終了(11.051秒)
までの区間は**わずか0.221秒**で、この区間の音量は既存のfind_speech_bounds
判定基準(RMS閾値0.02)を大幅に下回っていた(実測: 20msウィンドウの最大RMS=
0.00119、閾値の約1/17)。MFA(音響モデルによる強制アライメント)はこの区間に
「へ」という語があることを検出できているが、RMSエネルギーベースの
find_speech_bounds(英語Key Phrase用に設計された既存関数)では、この非常に
短く静かな日本語の文末を発話区間として検出できなかった。

これは、P4B/P4Cのように「1chunk=1marker、markerの後に十分な文が続く」設計
では発生しなかった問題である。本編方式(構造境界のみでの分割)を適用した
結果、2つ目のmarkerがchunkの終わり近くに位置するケースで、既存の無音調整
ロジックの前提(前後に十分な長さの発話区間がある)が崩れることが分かった。

## 17. 作成・変更したファイル

- `er003_b1_p6a_audio.py`(新規): 本編監査結果のdocstring記録、4chunk分割(1chunkに0〜2marker許容)、静的検証、漢字かな表記のままの対象句チェック
- `er003_v1_b1_p6a_generate.py`(新規): オーケストレーションscript(chunk生成、per-chunk ASR QA、MFA、複数marker対応splice、本編と同じ0.8秒結合・Dynamics3の実装、ただし未到達)
- `er003_test_b1_p6a_audio.py`(新規、20件、実TTS呼び出しなし)
- `er003_output/b1_p6a/A01/`配下の成果物一式(chunk_plan.json、static_check.json、4件のchunk音声、3件のTextGrid、2件の置換済みchunk音声)
- `er003_output/b1_p6a/A01/instruction/ER-003-B1-P6A_instruction.md`: 本指示書の保存

## 18. テスト結果

- `er003_test_b1_p6a_audio.py`(20件、実TTS呼び出しなし): 全合格
- プロジェクト全体の既存テストスイート: 1117件全合格(discover実行、回帰なし)

## 19. 再実行方法

```
.venv/Scripts/python.exe er003_v1_b1_p6a_generate.py
```

現状のコードのままでは、chunk03のmarker置換で同じ理由により再度停止する
見込み(MFAで特定される境界時刻は決定的なため)。再開には、chunk03の
「2件目marker後の区間が極端に短い」問題への対処方針についてご指示が必要
(下記19参照)。

## 20. 既知のリスク

- chunk03固有の構造(2件目markerの直後にごく短い文末しか残らない)が、
  既存のfind_speech_bounds(RMS閾値ベース)の前提を破っている。この問題は
  「本編方式(構造境界優先の少数chunk化)」を採用した結果として新たに
  顕在化したものであり、Previewの分割方針自体が抱えるトレードオフである
  可能性がある。
- chunk01・chunk02(成功分)の実測gapは0.40秒/0.30秒の目標を達成しているか
  未確認(本レポート作成時点で未計算、次回作業で確認要)。
- chunk02の「完全一致」という結果は極めて良好だが、単一chunkでの成功であり、
  声色・抑揚の連続性そのものはまだ試聴確認できていない(最終Preview未生成)。

## 21. 指示書の保存先とハッシュ

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p6a/A01/instruction/ER-003-B1-P6A_instruction.md` |
| sha256 | `39b6cd787795213926e24d1ad1c35ff5b09dd1ffabca7dec32805680fe67e1fa` |
| 管理ID | ER-003-B1-P6A |
| 実行時commit | `e2b75b757cd5e1b821c4c1113fa6687bfe6e44a7`(P5C完了コミット、このステージ実行直前のHEAD) |
| 指示書からの逸脱 | なし(想定外の技術的停止であり、指示の不履行ではない) |

## 22. Git status / push

このレポート作成時点では未コミット。P6A関連ファイルのみをステージして
コミットします。**pushは実行していません。**

---

## ユーザーへの確認事項

本編方式(構造境界のみでの4文分割)の効果自体は、chunk02の「ASR完全一致」
という結果からも非常に有望であることが確認できました。一方、chunk03固有の
構造(2件目markerの直後がごく短い文末)により、既存の無音検出ロジックが
機能しない技術的な壁に当たりました。以下のいずれかをご指示ください。

1. chunk03のみ、文の区切り方(例: 「stoppage timeへ。」を独立させず前の
   文へ含める、または「へ。」を含めた形でmarker後の区間長を確保する)を
   見直す
2. find_speech_bounds側の閾値・アルゴリズムを、極端に短く静かな末尾にも
   対応できるよう改善する(この場合、既存の英語Key Phrase処理への影響有無も
   確認が必要)
3. 現状のまま保留し、chunk01・chunk02の良好な結果を踏まえた別のアプローチを
   検討する
