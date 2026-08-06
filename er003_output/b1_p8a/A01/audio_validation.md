# ER-003-B1-P8A 実行報告(Preview＋本編 通し試聴版生成)

**ステータス: `PROTOTYPE / NOT_APPROVED`(ユーザー試聴前)**

## 訂正(2026-08-06)

P7Cの英語Component前ポーズにズレがあるバグが見つかり修正された
(詳細: `er003_output/b1_p7c/A01/audio_validation.md`冒頭の訂正記事)。
これに伴い、本ステージのPreviewファイルが差し替わったため、統合版を
修正後のPreviewで作り直した。**B1本編音声は無変更のまま再利用**して
おり、新規TTS callは発生していない。本文以下のsha256・durationは
修正後の値に更新済み。

## 1. 検証目的

P7Cでユーザー合格済みのPreview完成版と、同じB1エピソード(A01)の本編
音声を正しい順序で接続し、エピソード全体を通して試聴できる統合候補を
作成する。本番公開用の最終マスタリングではなく、Previewから本編への
移行の自然さ・音量差・全体構成を確認するための通し試聴版。

## 2. 使用したPreviewファイルと完全なsha256

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p7c/A01/A01_p7c_gemini31_english_replaced_dynamics3.wav` |
| sha256(P7C修正後の記録値) | `111788d635637be7d4edb38d2c45784a5d929144cbf7e68e5e1e3b31c0671168` |
| sha256(P8A読み込み時) | `111788d635637be7d4edb38d2c45784a5d929144cbf7e68e5e1e3b31c0671168`(**完全一致**) |
| duration | 44.845秒(P7C修正により旧44.055秒から変化) |
| モデル | gemini-3.1-flash-tts-preview |

## 3. Previewを再生成・再加工していない証拠

`er003_b1_p8a_audio.py`は、P7Cのファイルを`common.read_wav_float`で
読み込むだけで、日本語TTS呼び出し関数(`gclient.make_tts_call_fn`を
3.1で呼ぶ経路)を一度も呼び出していない。`verify_preview_unchanged()`
によるsha256一致確認(section2)に加え、Previewに対して
`apply_dynamics3_once`を呼んでいないこと(本モジュール内でPreview
samplesへDynamics3を適用する呼び出しが存在しない)をコードレベルで
確認した。

## 4. 対象B1本編の原稿・成果物

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p1/A01/b1_article_raw.md` |
| sha256 | `3a01120e0df0fb119b31dcc33b3a5d9342dc79dedec40880a1516add990da533` |
| 内容 | "Five Minutes from the Final—Then the Champions Struck"(England vs Argentina、A01 Previewと同一試合・同一Key Phrase(shot on target/take players off/a narrow lead/close the door to the final/stoppage time)を含み、対象エピソードとの一致を確認) |

### 承認状態についての確認事項

ER-003-B1-P1自身のcommitメッセージは、この原稿を「PROTOTYPE/
NOT_APPROVED」と自己申告していた。一方、後続のER-003-B1-P2・P3Rの
commitメッセージでは一貫して「承認済みA01 B1本文」と呼ばれており、
ファイルとしての明示的な承認記録は存在しなかった。この食い違いを
本ステージ開始前にユーザーへ直接確認し、**この原稿を本編音声生成の
入力として使用してよいとの回答を得た**(このチャット内の回答。ファイル
化はしていない)。

### 別記事(ER-002本編A01)との違い

`er002_output/A01/`には、同じ試合を扱うER-002本編(いわゆるB2レベル)
の完成音声(`final_audio_dynamics3.wav`)が存在するが、`user_evaluation.
json`で「台本は事実の羅列に近く、切り口が弱い...記事構造は維持し、
中身を作り直す必要がある」とユーザーから編集面で却下されており、
**承認済みではない**。また文章そのものがER-003-B1版とは異なる
(見出し・パラグラフ構成・語彙が別)。本ステージでは、ER-002本編A01を
一切使用していない(指示section3「別エピソードや検証用音声を、対象
B1本編として代用しない」に従う)。

## 5. 本編音声が既存か新規生成か

**新規生成。** 以下の証拠から、対象A01 B1本編の音声はこのリポジトリの
全履歴を通じて一度も生成されていなかったことを確認した。

- `er003_output/b1_p3r/A01/generation_stopped_status.json`:
  `"b1_article_tts_call_count": 0`
- `er003_output/b1_p4/A01/audio_metadata.json`: `b1_article_source_*`は
  記録するがTTS成果物は保存されていない
- 全履歴検索で、B1本編の生成済み`.wav`・manifestは1件も見つからず
- リポジトリ内の他の`episode_B1_*.wav`(旧番組フォーマット、CEFR
  レベル「B1」を指すが今回のER-003-B1 A01記事とは無関係)も、内容が
  別トピック(例: `episode_B1_036.json`は大谷選手の野球トピック)で
  あり、対象記事の代用にはできないことを確認した

## 6. 本編の使用モデル・voice・生成条件

| 項目 | 値 |
|---|---|
| model | `gemini-2.5-pro-preview-tts`(凍結仕様、無変更) |
| voice | Aoede |
| instruction | `er002_common.build_style_prefix()`(COMMON_BASE_INSTRUCTION+LEVEL2_INSTRUCTION+POINT_LABEL_FIDELITY_RULE、無変更) |
| chunk分割 | ER-001B-9/10以来の3chunk固定構造(body / Today's...Points+Point One+Point Two / In One Line)、`common.build_narration_plan`をそのまま使用 |
| セクション間無音 | `common.SECTION_JOIN_PAUSE_SECONDS`(0.8秒) |
| QA | embedded+grounded QA(`common.run_tts_content_attempts`、QAモデル`gemini-3-flash-preview`) |
| Dynamics 3 | 結合後の本編全体へ1回(`common.apply_dynamics3_once`) |
| 使用関数 | `er002_common.build_narration_plan`/`run_tts_content_attempts`/`apply_dynamics3_once`をいずれも無変更で使用。実装者による仕様変更は行っていない |

### 生成試行の経緯

1回目の試行(3回、指示section5の上限どおり)は**全て不合格**だった。
QAが検出したのは、原稿の欠落・重複・順序違反ではなく、いずれも
軽微な発話上の言い回しの違い(例:「Argentina captain」を「Argentine
captain」と発話、「substitute」の省略、「July 15」を「July 15th」と
発話、スコア表記の口語的な読み上げ)であり、`unauthorized_paraphrase`
理由での不合格だった。この結果をユーザーへ報告し、**ユーザーの明示的
な許可を得て**、指示書の上限(3回)を超える2回目の3回試行を実施した。
2回目の試行3回目で合格した(embedded QA・grounded QAとも`passed`)。

| 項目 | 値 |
|---|---|
| 1回目試行 | 3回とも不合格(`unauthorized_paraphrase`) |
| 2回目試行(ユーザー許可済み) | 3回中3回目で合格 |
| 合計の本編content試行回数 | 6回 |
| 詳細 | `er003_output/b1_p8a/A01/audit/body_generation_attempts_summary.json` |

**開示事項**: 2回目試行の各回のQA詳細(embedded/grounded分の発話
テキスト等)は、1回目とは異なりファイルへ保存していない(最終的な
`accepted_attempt`番号と合否のみ記録)。合格判定自体は
`common.run_tts_content_attempts`の`status == "OK"`(embedded・
grounded QAとも`passed`が確定した場合のみ到達する分岐)によって
保証されている。

## 7. Preview 3.1／本文2.5の設定分離

| 項目 | 値 |
|---|---|
| Preview | `gemini-3.1-flash-tts-preview`(P7Aで使用、本ステージでは再利用のみ) |
| 本編 | `gemini-2.5-pro-preview-tts`(`er002_common.MODEL_NAME`、無変更) |
| 隔離方式 | `er003_b1_p8a_audio.py`は新規モジュール。`er002_common.py`・`er002_gemini_client.py`は無編集 |

`er003_test_b1_p8a_audio.py::ModelIsolationTests`で、両モデルが異なり
本文モデルが凍結仕様のままであることを固定テストとして保存済み
(全合格)。

## 8. 本編のセクション構成と順序

QA(`embedded_classified.element_checks`)により、以下の構成・順序が
音声内に過不足なく存在することを確認した。

| セクション | 検出 |
|---|---|
| title | 1回(OK) |
| today_points_heading | 1回(OK) |
| point_one | 1回(OK) |
| subheading1 | 1回(OK) |
| point_two | 1回(OK) |
| subheading2 | 1回(OK) |
| in_one_line | 1回(OK) |

`observed_section_order`: title → today_points_heading → point_one →
subheading1 → point_two → subheading2 → in_one_line(仕様通り)。

## 9. Previewから本編への接続方法

`er003_b1_p8a_audio.concatenate_preview_and_body`で、以下の手順のみを
実施した(crossfade・time stretch・pitch変更・話速変更・ノイズ処理・
声質補正・自動音量均一化のいずれも行っていない)。

1. `p3u.find_speech_bounds`でPreview末尾・本編先頭の発話区間を検出
   (RMSは発話区間の検出のみに使用、内容削除の判断には使わない)
2. `p3z.adjust_trailing_silence`でPreview側の末尾無音を0.80秒へ調整
   (Previewの発話内容は一切変更しない、`speech_content_unchanged: True`)
3. `p3z.adjust_leading_silence`で本編側の先頭無音を0秒(タイト)へ調整
   (本編の発話内容は一切変更しない、`speech_content_unchanged: True`)
4. 単純に配列を連結(`np.concatenate`)

この設計により、Preview側に0.80秒分の無音を作り、本編側の既存の先頭
無音は除去してから連結することで、可聴音間の実効間隔がちょうど0.80秒
になるようにしている(指示section9「見かけ上の配置時刻だけで判定
しない」に対応)。

### 接続点のクリック/二重音リスクの診断

Preview末尾の発話終了点、本編先頭の発話開始点それぞれのサンプル振幅を
確認したところ、いずれも±0.03程度(フルスケール1.0に対して数%)と
小さく、無音への遷移点として自然な範囲だった(大きな振幅から急に
無音へ落ちる、いわゆるクリックノイズの典型的な原因となる急激な
不連続は見られない)。

## 10. 実効接続間隔

| 項目 | 値 |
|---|---|
| 目標 | 0.80秒 |
| 実測(achieved_trailing_seconds、Preview側) | 0.80秒(完全一致) |
| 実測(achieved_leading_seconds、本編側) | 0.00秒(タイトに調整、上記手順3) |
| 可聴音間の合計実効間隔 | **0.80秒** |

## 11. Preview・本編の音量診断

**P7C修正後の値。**

| 指標 | Preview | 本編 | 統合後全体 |
|---|---|---|---|
| duration | 44.845秒 | 150.033秒 | 194.638秒 |
| peak | 0.860 | 0.887 | 0.887 |
| RMS(全体) | 0.0910 | 0.0820 | 0.0842 |
| clipping | 検出なし | 検出なし | 検出なし |
| 発話区間 | 0.260〜44.145秒 | 0.340〜149.653秒 | 0.260〜194.258秒 |
| 末尾3秒RMS | 0.0848 | 0.0773 | 0.0773 |
| 先頭3秒RMS | 0.0947 | 0.0964 | 0.0947 |

PreviewのRMS(0.0910)と本編のRMS(0.0820)の差は約0.9dB相当であり、
大きな音量差ではないと考えられるが、**今回は自動補正を行っていない**
(指示section11の明記通り、補正はユーザー試聴後の別タスク)。

## 12. 全体試聴版の場所

**P7C修正後のPreviewを使って作り直した版。**

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p8a/A01/assembled/A01_p8a_preview_plus_main_full_listening.wav` |
| sha256 | `304be3b822cc92bb2942db00c5dfdc3cda4aba6af18fa265936fd54d29440b8b` |
| duration | 194.638秒(約3分15秒) |

## 13. 接続確認clipの場所

**P7C修正後のPreviewを使って作り直した版。**

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p8a/A01/clips/A01_p8a_preview_to_main_transition_clip.wav` |
| sha256 | `302c2ce98c10834217d1ee71a57d5f1eaaa8862a08193823faaea587f44ba0aa` |
| duration | 25.0秒(Preview末尾10秒+本編先頭15秒、指示section12の推奨値通り) |

**注意**: 全ての`.wav`ファイルは`.gitignore`によりリポジトリには
含まれていない(このプロジェクト全体で一貫した運用)。ローカルファイル
として存在するので、ユーザーが直接再生する必要がある。

## 14. 全体duration

**194.638秒(約3分15秒)** = Preview(44.845秒、P7C修正後)+ 接続無音
(0.80秒、Preview側の末尾無音として含まれる)+ 本編(150.033秒-本編
先頭の元々の無音0.34秒分)。

## 15. 機械QA結果

| 項目 | 結果 |
|---|---|
| PreviewがP7C合格ファイルとsha256一致 | 合格 |
| Previewを再生成していない | 合格(コード上、日本語TTS呼び出しなし) |
| Preview内の5英語フレーズが変更されていない | 合格(sha256完全一致のため自明) |
| Previewへ追加のDynamics3を適用していない | 合格 |
| 本編が対象B1エピソードである | 合格(記事内容の一致を確認) |
| 承認済み原稿を使用している | 合格(ユーザーに確認済み) |
| 本編モデルが2.5 Proである | 合格 |
| 本編の凍結仕様を維持している | 合格(build_narration_plan等を無変更で使用) |
| 必要なセクションが全て存在する | 合格(QA element_checks全てok) |
| セクション順序が正しい | 合格 |
| Previewが最初に1回だけ存在する | 合格 |
| 本編がPreview後に正しい順序で存在する | 合格 |
| Previewと本編の間に欠落・重複がない | 合格 |
| 実効接続間隔が0.80秒 | 合格 |
| 音声がdecode可能 | 合格 |
| clippingなし | 合格 |
| 接続点にクリックや二重音がない | 診断上は良好(section9末尾参照)、断定はしない |
| 統合後に追加のDynamics3を適用していない | 合格 |
| Preview 3.1／本文2.5のモデル設定が維持されている | 合格 |

**機械QAは全て合格した。ただしこれは音質・学習体験の承認を意味しない
(指示section13の明記通り)。**

## 16. 作成・変更したファイル

- `er003_b1_p8a_audio.py`(新規): Preview固定確認、B1本編narration
  plan構築、本編音声生成(凍結仕様のまま`run_tts_content_attempts`を
  呼ぶラッパー)、Preview+本編接続、音量診断、境界clip抽出、モデル
  隔離確認
- `er003_v1_b1_p8a_generate.py`: 本ステージでは対話的に各ステップを
  実行したため、単一のオーケストレーションscriptとしては未作成
  (再実行方法はsection18参照)
- `er003_test_b1_p8a_audio.py`(新規、8件、合成波形データのみ、実TTS/
  QA呼び出しなし)
- `er003_output/b1_p8a/A01/`配下の成果物一式(`audit/`、`body_raw/`、
  `assembled/`、`clips/`、`instruction/`、本報告書)
- `er002_common.py`・`er002_gemini_client.py`: **変更なし**(凍結仕様)

## 17. テスト結果

- `er003_test_b1_p8a_audio.py`(8件、合成データのみ): 全合格
- プロジェクト全体回帰テスト(`run_project_regression.py`、
  er0*_test_*.py全探索): P7C修正反映後の時点で**1598件全合格、回帰なし**

## 18. 再実行方法

対話的に以下の手順で実行した(単一scriptとしては未整備)。

```python
import er003_b1_p8a_audio as p8a
import er002_common as common

plan, text, script = p8a.load_and_build_narration_plan()
result = p8a.generate_article_body_audio(plan)  # 本編TTS(新規callが発生する)
# result["status"] == "OK" を確認した上で、
combined_result = p8a.concatenate_preview_and_body(
    preview_samples, result["post_dynamics3_samples"], sample_rate=24000)
```

本編音声(`body_raw/A01_b1_body_dynamics3.wav`)は既に生成・保存済み
のため、再実行時はこのファイルを読み込むだけで新規TTS callなしに
接続処理から再実行できる。

## 19. 既知のリスク

- 本編音声生成は、1回目の3回試行が全て不合格になり、ユーザーの明示的
  な許可を得て2回目の3回試行を追加実施した結果、合格した。**この
  差し替え可否・許容範囲については、今後同様の事象が起きた場合の
  運用方針をあらかじめ相談しておくとよい**(指示書の上限3回を毎回
  超えてよいかは今回の個別判断であり、恒久ルールではない)。
- PreviewのRMS(0.0910)と本編のRMS(0.0820)には約0.9dB相当の差が
  ある。今回は自動補正していないため、ユーザー試聴で気になる場合は
  別タスクとして音量差の調整を検討する必要がある。
- **(訂正)** 初版はP7Cの無音間隔バグの影響を受けたPreviewを使用して
  いたため、本ステージも修正後のPreviewで統合版を作り直した(本編
  音声は無変更のまま再利用、新規TTSなし)。詳細は本報告書冒頭の
  訂正記事を参照。
- 接続点のクリック/二重音の有無は、サンプル振幅の診断(section9末尾)
  では良好だったが、最終的には聴感でのみ判断できる。
- 本編は6回目の試行でようやく合格しており、Gemini TTSの発話上の
  自然な言い換え癖(冠詞・日付・スコア表記等)が、この厳格なQA基準と
  頻繁に衝突する可能性がある。将来的に同様の記事でも同じ問題が
  再発しうる。

## 20. 指示書の保存先とsha256

| 項目 | 値 |
|---|---|
| path | `er003_output/b1_p8a/A01/instruction/ER-003-B1-P8A_instruction.md` |
| sha256 | `04db3c401252581e340d1f0504ec9d9d98368953b6b4ed9f7eb6adf4d2888c72` |
| 管理ID | ER-003-B1-P8A |
| 指示書からの逸脱 | 本編生成の試行回数(指示section5の3回上限を、ユーザー許可を得て2回目の3回試行として追加実施、合計6回)。それ以外の逸脱なし |

## 21. Git status

このレポート作成時点では未コミット。P8A関連ファイルのみをステージして
コミットします。

## 22. push

実行していません。

---

## ユーザーへの確認事項(訂正版)

**P7Cの無音間隔バグ修正により、ファイルが差し替わっています。** 以下の
統合試聴版をご確認ください。

- [A01_p8a_preview_plus_main_full_listening.wav](assembled/A01_p8a_preview_plus_main_full_listening.wav)(全体、194.638秒)
- [A01_p8a_preview_to_main_transition_clip.wav](clips/A01_p8a_preview_to_main_transition_clip.wav)(接続部確認用、25秒)

指示section14の項目、特に以下を重点的にご確認ください。

- Preview終了後、本編へ自然に移行するか(0.8秒の間が適切か)
- 接続点に音切れ・クリック・二重音がないか
- Previewと本編の音量差・声質差が気にならないか
- Previewを聞いた後に本編の内容を理解しやすいか

**機械QAは全て合格していますが、「統合版合格」「エピソード完成」
「公開可能」とは判断していません。**
