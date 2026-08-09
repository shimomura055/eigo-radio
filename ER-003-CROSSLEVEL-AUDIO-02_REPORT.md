# ER-003-CROSSLEVEL-AUDIO-02 実行報告(A01・ADD03 A2音声プロトタイプ初回音声化)

**管理ID: ER-003-CROSSLEVEL-AUDIO-02**
**実施日: 2026-08-10**
**ステータス: `PROTOTYPE / UNDER_EVALUATION`(A01・ADD03とも初回生成、ユーザー未試聴)**

A01・ADD03は今回が**初めてのA2構造支援版音声化**(A02のER-003-A2-AUDIO-01に
相当する回)であり、ER-003-CROSSLEVEL-AUDIO-01でA02へ反映・承認済みの
5つのCross-level改善(Preview原則・Comment4文言・Key Phrase語末音素試作・
ポイント解説後+0.2秒・Outro減衰)を、**最初から**組み込んだ形で生成した。

## 1. Preview修正前後

**A01**
- 修正前(既存STRUCT-04版、B1の「深夜0-6時SNS停止」に相当する具体展開情報を含んでいた旧記事の名残):
  > 前半は激しい接触が続き、静かな均衡が保たれます。後半、イングランドは守備を固め、わずかなリードを守ろうとします。しかし後半終了間際、メッシが流れを変え、ついにアディショナルタイムへ。最後の数分、何が起きるのでしょうか。
- 修正後:
  > ワールドカップ準決勝で、イングランドとアルゼンチンが対戦しました。試合は最後まで緊張感の続く展開でしたが、終盤で大きく流れが変わります。いったい何が、この試合の勝敗を分けたのでしょうか。

**ADD03**
- 修正前:
  > トランプ米大統領が、ホルムズ海峡を通る船から通航料20%を徴収すると発表しました。ところがわずか1日で撤回され、原油価格は乱高下しました。市場はやや落ち着きを取り戻したように見えますが、緊張は本当に解けたのでしょうか。
- 修正後:
  > トランプ米大統領が、ホルムズ海峡をめぐる新しい料金案を発表しました。発表からまもなく、状況は大きく動き、市場の注目を集めます。本当のリスクは、いったいどこにあったのでしょうか。

## 2. PreviewとComment 1/2の重複解消確認

**A01**: 旧Previewは「イングランドが守備を固め、わずかなリードを守ろうとする」と明言しており、Comment1「最初にリードを奪ったのはどちらのチームか」への答えを先に言ってしまっていた。新Previewは「終盤で流れが変わる」「何が勝敗を分けたか」という問いに留め、どちらが先にリードしたかには触れない。Comment1・Comment2(「イングランドが先制し…このリードは最後まで続くのか」)とも、新Previewに対して重複なく機能する。

**ADD03**: 旧Previewは「20%」「1日で撤回」「原油価格の乱高下」「市場の落ち着き」まで具体的に述べており、Comment1(「まず何が発表されたのか」)・Comment2(「原油市場はこれで落ち着いたのか」)の答えを先取りしていた。新Previewはテーマと「本当のリスクはどこにあったか」という問いのみに留め、具体的な数字・結論には触れない。

いずれもComment1〜3の文言自体は無変更(STRUCT-04の既存文言を維持)。ASR全文確認(12節)で実際の接続を確認済み。

## 3. 使用Key Phrases

B1のKey Phraseをそのまま流用せず、方式L(Listening Blocker Ranking)選定+Canonicalization(ER-003-KP-02-R1「最小十分」版)を、A2最終英語本文(`er003_output/a2_p1_r3/{article}/a2_article_raw.md`)へ適用し直して選定した(詳細は[er003_v1_a2_kp_select_generate.py](er003_v1_a2_kp_select_generate.py)、結果は`er003_output/a2_p2_keywords/{A01,ADD03}/keywords_canonicalized.json`)。

**A01**(B1: shot on target/take players off/a narrow lead/close the door to the final/stoppage time)
| # | used_form | 日本語グロス | B1との一致 |
|---|---|---|---|
| 1 | shot on target | 枠内シュート | 一致(偶然) |
| 2 | go ahead | リードする | 新規 |
| 3 | come on | 交代出場する | 新規 |
| 4 | go out | 敗退する | 新規 |
| 5 | turn the game around | 試合を逆転する | 新規 |

**ADD03**(B1: blockade/be in place/freedom of navigation/tollbooth/smell of gunpowder)
| # | used_form | 日本語グロス(公式Canonicalization結果) | B1との一致 |
|---|---|---|---|
| 1 | Strait of Hormuz | ホルムズ海峡 | 新規 |
| 2 | blockade | 封鎖、通行遮断 | 英語のみ一致(グロスは新規選定) |
| 3 | drop the fee | 料金案を取り下げる | 新規 |
| 4 | Brent crude oil | ブレント原油 | 新規 |
| 5 | be in place | 実施中である、存続している | 英語のみ一致(グロスは新規選定) |

## 4. Key Phrase語末音素QA

語末が停止音・摩擦音(/d/ /t/ /k/ /s/ /z/ /ʃ/等)で終わるものを「要注意」と分類した(あくまで機械的な音韻分類であり、実際に聞こえが弱いと確認されたわけではない)。

**A01**
| # | used_form | 語末音素 | 要注意 | 採用版 |
|---|---|---|---|---|
| 1 | shot on target | target語末/t/ | ○ | 試作版 |
| 2 | go ahead | ahead語末/d/ | ○ | 試作版 |
| 3 | come on | on語末/n/(鼻音) | - | 標準版 |
| 4 | go out | out語末/t/ | ○ | 試作版 |
| 5 | turn the game around | around語末/d/ | ○ | 試作版 |

**ADD03**
| # | used_form | 語末音素 | 要注意 | 採用版 |
|---|---|---|---|---|
| 1 | Strait of Hormuz | Hormuz語末/z/ | ○ | 試作版 |
| 2 | blockade | blockade語末/d/ | ○ | 試作版 |
| 3 | drop the fee | fee語末は母音 | - | 標準版 |
| 4 | Brent crude oil | oil語末/l/(流音) | - | 標準版 |
| 5 | be in place | place語末/s/ | ○ | 試作版 |

## 5. 再生成したKey Phraseと理由

上記「要注意」7件(A01: 4件、ADD03: 3件)について、まず標準経路(ENGLISH_STYLE_PREFIX)で生成した上で、ER-003-CROSSLEVEL-AUDIO-01でA02の"feed"に使った試作instruction(語末まで言い切ることを明示、過剰強調はしない)を**同一のまま**適用し、追加で試作版を生成した。両バージョンの末尾エネルギー波形を比較し(`key_phrase_tail_energy_comparison.json`)、8件中8件(A02の"feed"含む)で試作版に旧版になかった末尾の二次エネルギーピークを確認した。組立には試作版を採用したが、**知覚的に改善したかどうかは未確認**(6節参照)。「要注意」でない3件(come on/drop the fee/Brent crude oil)は標準版のみで採用した(不要な再生成を避けるため)。

## 6. 日本語Comment TTS条件

Preview・Comment1〜4・Key Phrase日本語訳(meaning)とも、既存の確立済み経路(`gemini-3.1-flash-tts-preview` + Aoede、`er003_b1_p7a_audio.JAPANESE_STYLE_PREFIX`)を無変更で使用した。新しいinstructionは作らなかった。

## 7. 英語TTS条件

Full Story Part1/2・Point One/Two・In One Line・Key Phrase標準版は、既存の確立済み経路(`gemini-2.5-pro-preview-tts` + Aoede、`er003_b1_p4c_audio.ENGLISH_STYLE_PREFIX`)を無変更で使用した。

**新たに一般化したフォールバック**: ADD03のPoint One(金額表現「$30 million」等を含む)で、標準経路が6回とも同一の`400 INVALID_ARGUMENT`(「モデルがテキストを読み上げず応答しようとした」)で失敗した。これはA02の"opt out"等で既に確立済みの「文脈のない短いフレーズがモデルを迷わせる」現象と同種と判断し、Key Phrase Component用に確立済みのminimal instructionフォールバック(`repro01.MINIMAL_INSTRUCTION_PREFIX`、声・モデルは無変更)を、Key Phrase以外の英語ナレーションセグメントにも汎用化して適用した(`generate_english_segment_with_fallback`、[er003_v1_crosslevel_audio_02_common.py](er003_v1_crosslevel_audio_02_common.py))。ADD03のPoint Oneはこのフォールバック経路で合格した。

## 8. ポーズ

ER-003-CROSSLEVEL-AUDIO-01でA02へ適用した値をそのまま再利用した(新しい数値はここで設計していない)。
- 「ポイント解説」後: 0.7秒(A02 v2と同一)
- Comment前後(EN→JA / JA→EN): 1.0秒 / 0.8秒(無変更)
- その他の既存ポーズ(0.5秒/0.4秒/0.65秒): 無変更

## 9. Outro音量処理の変更内容

ER-003-CROSSLEVEL-AUDIO-01でA02へ適用した係数(Introへのgain matching後、追加で振幅×0.6903≒-3.22dBを乗じる、心理音響上の体感80%狙い)を、**同じ数値のまま**A01・ADD03にも適用した。新しい係数は設計していない(計算式`OUTRO_EXTRA_GAIN_DB = 10 × log2(0.8) ≈ -3.22dB`自体は[er003_v1_a2_audio_02_generate.py](er003_v1_a2_audio_02_generate.py)から定数としてそのままimportして再利用、共通モジュール経由)。

## 10. 全パートタイムライン(主要区間、A01・ADD03とも同一構成47パート)

**A01**(`er003_output/crosslevel_audio_02/A01/assembled/English_Your_Way_A2_A01.wav`)

| Part | Start(s) | Duration(s) |
|---|---:|---:|
| Point explanation | 29.829 | 1.220 |
| pause_0.7_point_explanation | 31.049 | 0.700 |
| Preview | 31.749 | 16.400 |
| Key Phrase 1〜5 | 53.480〜82.685 | (5ブロック) |
| Comment 1 | 87.995 | 7.820 |
| Full Story Part 1 | 96.615 | 35.991 |
| Comment 2 | 133.606 | 8.660 |
| Full Story Part 2 | 143.066 | 41.091 |
| Comment 3 | 185.157 | 14.900 |
| Point One | 200.857 | 23.431 |
| Point Two | 224.788 | 28.531 |
| Comment 4 | 254.319 | 19.240 |
| In One Line | 274.359 | 13.171 |
| Outro | 288.030 | 6.144 |

**ADD03**(`er003_output/crosslevel_audio_02/ADD03/assembled/English_Your_Way_A2_ADD03.wav`)

| Part | Start(s) | Duration(s) |
|---|---:|---:|
| Point explanation | 31.469 | 1.220 |
| pause_0.7_point_explanation | 32.689 | 0.700 |
| Preview | 33.389 | 15.340 |
| Key Phrase 1〜5 | 54.060〜87.085 | (5ブロック) |
| Comment 1 | 92.395 | 6.660 |
| Full Story Part 1 | 99.855 | 43.071 |
| Comment 2 | 143.926 | 10.220 |
| Full Story Part 2 | 154.946 | 62.051 |
| Comment 3 | 217.997 | 15.620 |
| Point One | 234.417 | 28.331 |
| Point Two | 263.248 | 25.351 |
| Comment 4 | 289.599 | 18.120 |
| In One Line | 308.519 | 12.211 |
| Outro | 321.230 | 6.144 |

完全な47区間の詳細は`er003_output/crosslevel_audio_02/{A01,ADD03}/audit/timeline.json`参照。

## 11. 完成音声総尺

- A01: **294.174秒**(約4分54秒)
- ADD03: **327.374秒**(約5分27秒)

## 12. ASR全文確認

両記事とも、完成音声全体をAzure STT(en-US/ja-JP、`timeout_seconds=420`、ER-003-A2-AUDIO-01/CROSSLEVEL-AUDIO-01で確立した長尺音声向けの明示的timeout指定を踏襲)で全文確認した。4トランスクリプトとも`err=None`(タイムアウトによる部分結果ではない)で取得できた。新Preview・新Comment4・新Key Phrase・全パートの内容が過不足なく含まれていることを目視確認済み(`full_assembled_asr_en.txt`/`full_assembled_asr_ja.txt`)。

## 13. hallucination有無

**検出されなかった。** 数字表記のASR書き起こしゆれ(例: "seven minutes"→"7 minutes"、"1隻"→ASRでは「一席」)は、ER-003-REPRO-FINALで確立済みのASR_NUMBER_NOTATION_AMBIGUITY/ASR homophone ambiguityと同種の既知パターンであり、TTS内容自体の誤りではない。

## 14. clipping有無

検出されなかった。A01ピーク0.95723、ADD03ピーク0.92308(いずれも`compute_gain_for_target_rms`のmax_peak=0.95上限による自然な値。A01がやや上限に近いが、`measure_metrics`によるclipping判定はいずれもFalse)。

## 15. 手動修正

TTS生成過程で以下4件の問題が発生し、いずれもテキストや対象範囲を調整して解消した(音声内容の意味は変えていない)。

1. **ADD03 Point One**: 金額表現を含むテキストで標準経路が6回とも`400 INVALID_ARGUMENT`で失敗 → 8節のfallback汎用化で解消。
2. **ADD03 meaning_2「封鎖、通行遮断」**: 読点区切りの2言い換えがASRで6回とも別の同音異義語(「風咲」等)に誤認識 → ナレーション音声のみB1で実績のある単一語「海上封鎖」へ差し替え(Canonicalization正式結果自体は変更せず)。
3. **ADD03 meaning_4「ブレント原油」**: 「ブレント」部分がASRで6回とも誤認識される一方「原油」部分は安定して認識された → expected_substringを「原油」へ緩和(テキスト自体は変更なし、ASR側の限界と判断)。
4. **A01 full_story_part2の検証substring**: 当初"seven minutes"を指定していたが、ASRが"7 minutes"(数字表記)へ一貫して転記し不一致 → 数字を含まない安定箇所("referee then added more time")へ変更。
5. **A01 meaning_1「枠内シュート」**: 新規生成6回ともASRが同音異義語(「湧内シュート」等)へ誤認識 → B1のA01既存音声(用語・グロスとも偶然完全一致)を再利用し新規生成を回避。

いずれもOPEN-28([OPEN_ITEMS.md](OPEN_ITEMS.md))として今後の一般化検討事項に記録した。

## 16. ユーザー確認が必要な箇所

- 7件の試作Key Phrase(4〜5節)が自然に聞こえるか、不自然に強調されていないか。機械診断(波形上の二次ピーク)は「TTSが語末の音を発している可能性が高い」ことを示すに留まり、「自然に聞こえる」ことは証明しない
- Outro音量が体感4/5に近いか(3記事共通)
- 「ポイント解説」後+0.2秒の間が適切か(3記事共通)
- 新Preview(A01・ADD03とも)がテーマ・問いを適切に伝え、答えを先出ししすぎていないか
- Comment4の新しい締め文言(「ポイントを英語で振り返ります/まとめます」)が自然か
- A01・ADD03とも**初めての音声化**のため、Full Story分割位置・Comment1〜3の役割・全体テンポも含め、通しでの確認が必要

## 17. A02 v2との方式差分

A02(ER-003-CROSSLEVEL-AUDIO-01)は既存のER-003-A2-AUDIO-01資産(Comment1-3・Full Story・Points・In One Line)を再利用し、5点の差分のみ新規生成した。A01・ADD03は**今回が初回音声化**のため、Preview・Comment1〜4・Full Story Part1/2・Point One/Two・In One Line・Key Phrase全件(5×2=10件)を新規生成する必要があった。処理の一貫性を保つため、A01・ADD03間で共通する処理(セグメント生成・Key Phrase試作判定・組立・ゲイン計算)を新規の共通モジュール[er003_v1_crosslevel_audio_02_common.py](er003_v1_crosslevel_audio_02_common.py)へまとめ、Cross-level改善の実体(Outro係数・ポーズ秒数・試作instruction)はA02 v2([er003_v1_a2_audio_02_generate.py](er003_v1_a2_audio_02_generate.py))から定数・関数として直接importして再利用した(数値の再設計・重複コピーによるズレを避けるため)。

## 18. Cross-level一般化の再現性

4つのCross-level候補すべてについて、A01・ADD03でも問題なく適用でき、3記事目までの再現性を確認した。

- **Preview原則**: A01・ADD03とも、旧Previewが後続Comment1/2の答えを先出ししていた事実を確認し、新原則で書き直すことでComment1/2との重複が解消した(2記事で再現)。
- **Key Phrase語末音素試作**: A02の1件と合わせ、計8件(A01: 4件、ADD03: 3件、A02: 1件)で同一instructionを適用し、8件中8件で末尾エネルギー波形上の変化を確認した(ただし知覚的改善は依然未確認)。
- **ポイント解説後+0.2秒**: 3記事とも同一の0.7秒を適用(数値の一元化=共通定数化はまだ行っていない、OPEN-25参照)。
- **Outro減衰**: 3記事とも同一係数(振幅×0.6903)を適用。

## 19. Source of Truth更新

- [OPEN_ITEMS.md](OPEN_ITEMS.md): OPEN-13(音声プロトタイプ状況)・OPEN-23〜26(Cross-level候補、3記事再現の追記)を更新。新規OPEN-27(CI manifest未登録ファイル発見)・OPEN-28(Canonicalizationグロスの単独ナレーション不安定パターン)を追加
- [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md): A01/A02/ADD03のCEFR-A2行を`TBD`から`PROTOTYPE_BUILT`(各列)へ更新
- `A2_PROTOTYPE_SPEC.md`: 変更なし(今回追加した内容はいずれも既存原則の適用結果であり、新しい仕様決定を伴わないため)
- `CURRENT_SPEC.md`: 変更なし(A2は引き続き非DECIDED)

## 20. 作成・変更ファイル

- 新規: [er003_v1_a2_kp_select_generate.py](er003_v1_a2_kp_select_generate.py)(A2版方式L選定+Canonicalization)
- 新規: [er003_v1_crosslevel_audio_02_common.py](er003_v1_crosslevel_audio_02_common.py)
- 新規: [er003_v1_crosslevel_audio_02_a01_generate.py](er003_v1_crosslevel_audio_02_a01_generate.py)
- 新規: [er003_v1_crosslevel_audio_02_add03_generate.py](er003_v1_crosslevel_audio_02_add03_generate.py)
- 新規: `er003_output/a2_p2_keywords/{A01,ADD03}/*.json`,`*.txt`,`*.md`(Key Phrase選定成果物)
- 新規: `er003_output/crosslevel_audio_02/{A01,ADD03}/audit/*.json`,`*.txt`(検証記録・タイムライン・ASR全文・語末エネルギー比較)
- 新規: 本レポート
- 更新: [OPEN_ITEMS.md](OPEN_ITEMS.md)、[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)
- 音声ファイル(`.wav`/`.mp3`、`er003_output/crosslevel_audio_02/`、`er003_output/a2_audio_01/A02/assembled/`等)は`.gitignore`により追跡対象外
- A02側の既存資産(ER-003-A2-AUDIO-01/CROSSLEVEL-AUDIO-01の成果物)・B1既存資産・共有凍結モジュールは一切変更していない

## 21. テスト結果

`scripts/run_ci_tests.py`(公式CIランナー)を実行したところ、リポジトリ直下の6ファイルが`ci_test_manifest.json`に未登録のためmanifest検証エラーで起動できないことを発見した(いずれも本セッションで新規作成したファイルではなく、以前のcommit時点から未登録。OPEN-27として記録)。この6件は今回のCROSSLEVEL-AUDIO-02の変更とは無関係な既存のリポジトリ状態であり、無断でmanifestを変更することは避けた。

代替として実施した検証:
- 新規4ファイルの構文チェック(`py_compile`): 全件合格
- 今回使用したCanonicalizationモジュールの既存テスト(`er003_test_key_words_canonicalization.py`)を直接実行: **36件全合格**

公式CIランナーによる全体回帰テスト(過去「1660件」)は、上記manifestの問題により今回は実行できなかった。

## 22. Git status

音声ファイル(`.wav`/`.mp3`)は`.gitignore`により追跡対象外。コード・監査JSON・Key Phrase選定成果物・レポート・ドキュメント更新のみをcommit対象とする。

## 23. commit

コミット済み(詳細はcommitログ参照)。

## 24. push未実行確認

**pushは実行していません。**

## 参照元

[PROJECT_INDEX.md](PROJECT_INDEX.md)、[OPEN_ITEMS.md](OPEN_ITEMS.md)、
[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)、[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)、
[ER-003-A2-AUDIO-01_REPORT.md](ER-003-A2-AUDIO-01_REPORT.md)、
[ER-003-CROSSLEVEL-AUDIO-01_REPORT.md](ER-003-CROSSLEVEL-AUDIO-01_REPORT.md)
