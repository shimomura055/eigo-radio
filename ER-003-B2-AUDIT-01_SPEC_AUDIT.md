# ER-003-B2-AUDIT-01 B2音声成果物・実施履歴の再監査

**管理ID: ER-003-B2-AUDIT-01**
**実施日: 2026-08-09**
**スコープ: 監査のみ。再生成・コード変更・pushは一切行っていない。**

## 0. 結論(先に要約)

**前回の報告「B2について完成した音声データはない」は、現行ER-003のCEFR
B2テキスト(`er003_output/p2/{article}/b2_version_raw.md`)に関する限り、
訂正の必要はない。** A01・A02・ADD03のいずれについても、現行B2テキストの
TTS音声・Preview音声・Key Phrase音声・Points/In One Line音声・通し試聴版・
Podcast完成版は1件も存在せず、生成が試みられた記録もない。

**ただし、ユーザーの記憶は別の事実に基づいて正しい。** 現行ER-003より前の
**ER-002プロジェクト**で、A01(サッカー記事)とA02(SNS/門限記事)については、
**実際に本文TTS音声を生成し、Dynamics3処理を行い、ユーザーが実際に試聴して
評価した記録が存在する**(2026-07-18生成、2026-07-19評価)。この評価結果は
**「編集的に不十分」という理由で否定的**であり(A01「台本は事実の羅列に近く、
切り口が弱い」、A02「記事選定と台本内容の両方が不十分」)、この否定的評価を
受けてA01は台本の書き直し(v1.1B)が行われたが、それも**「さらに悪化した」
としてユーザーに拒否**され(`playback_stopped_at: "in_one_line_start"`、
最後まで聴かれていない)、最終的にこの一連の実験全体が放棄され、ER-003の
新しいアーキテクチャ(Natural English Source→B2/B1/A2独立生成、Key Phrase
方式L、Canonicalization等)へ移行したと考えられる。

**この「ER-002で試聴・評価された音声」は、現行ER-003のB2テキストとは
別物である。** 台本の文面を実際に突き合わせた結果、両者は一致しない
(例: ER-002版A01タイトル"Argentina's Late Semifinal Win" vs 現行B2版
"Five Minutes from the Final—Then the Champions Made Time Their Ally"、
本文の書き出しも異なる)。またER-002の台本にはCEFRレベルの指定が一切ない
(`CEFR`/`level`のgrep結果0件)ことも確認した。

**したがって、「B2まで音声制作を完了してからB1へ移った」という理解は
誤りである。** 正しくは、「ER-002時代にCEFRレベル区分のない台本で音声制作・
試聴・否定的評価を行い、それを踏まえてプロジェクト全体を作り直し、その
新しいER-003アーキテクチャでB1(現行)を制作した。現行のCEFR B2テキストは
ER-003で新たに生成されたテキストのみで、音声化は一度も行われていない」
というのが証拠に基づく事実である。

---

## 1. 重要な用語の混同ポイント: 「B2」は2つの異なる意味を持つ

監査の過程で、「B2」という文字列がこのリポジトリの歴史の中で**2つの
無関係な意味**で使われていたことが判明した。これがユーザーの記憶と
今回の報告の食い違いの主因と考えられる。

| 意味 | 使用箇所 | 内容 |
|---|---|---|
| (a) 実行バッチ番号としての「B2」 | `er002_s3_config.py`(commit `db35020`) | `S3_BATCHES = {"B1": [A01, A02], "B2": [A03, A06], "B3": [A04, A05]}` ——**CEFRとは無関係な、6記事を3バッチに分けたときの2番目のバッチ**。A01・A02は「B1」バッチに属し、「B2」バッチは全く別の記事(A03=エンタメ、A06=政治)を指す |
| (b) CEFR難易度レベルとしての「B2」 | ER-003 (`er003_b2_adapter.py`等) | 現行の「English Your Way」パイプラインで、Natural English Sourceから独立生成される難易度レベルの1つ。ER-002には存在しない概念(ER-002全体でCEFR/levelの言及はgrep 0件) |

ユーザーが記憶している「B1へ進む前にB2の音声を試聴・調整した」という
経験は、時系列・内容ともに **(a) の「ER-002-S3のBatch1(A01・A02)」の
音声試聴・評価** と一致する。実行バッチの「B1」という名前と、CEFRの
「B1」という名前が偶然同じ文字列だったため、後から見ると紛らわしいが、
**この2つは無関係な採番である。**

---

## 2. 項目別監査結果(A01・A02・ADD03)

以下、9つの確認項目それぞれについて、現行ER-003のCEFR B2と、参考情報
としてのER-002時代の実績を分けて記録する。

### 2-1. B2本文原稿の有無

| 記事 | 現行ER-003 B2本文 | ER-002時代の(CEFR無指定)台本 |
|---|---|---|
| A01 | あり(`er003_output/p2/A01/b2_version_raw.md`) | あり、ただし**別内容**(`er002_output/A01/script_en.json`、タイトル"Argentina's Late Semifinal Win") |
| A02 | あり(`er003_output/p2/A02/b2_version_raw.md`) | あり、ただし**別内容**(`er002_output/A02/script_en.json`) |
| ADD03 | あり(`er003_output/p2/ADD03/b2_version_raw.md`) | **なし**(ER-002ではJapanese記事下書き`er002_output/v1_2m_r2/ADD03/raw_article_final.md`のみ存在。英語台本・音声化の記録は皆無) |

### 2-2. B2本文TTS音声の有無

| 記事 | 現行ER-003 B2音声 | ER-002時代の音声生成実績 |
|---|---|---|
| A01 | **なし**(TTS呼び出し記録0件) | **あり**。`gemini-2.5-pro-preview-tts`、voice=Aoede、2026-07-18生成。さらにv1.1B改訂版も生成(2026-07-18) |
| A02 | **なし** | **あり**。同モデル、voice=Charon、2026-07-18生成 |
| ADD03 | **なし** | **なし**(音声生成そのものが実施されていない) |

### 2-3. B2のPreview音声の有無

全記事・全時代を通じて**なし**。ER-002のS3実験は「本文(記事全体)を
1本のTTSで読む」構成であり、「Preview」という概念自体(短い抜粋を
先出しする構成)はER-003で初めて導入されたものであることを確認した
(ER-002のmanifest.json構造にPreview関連フィールドが存在しない)。

### 2-4. B2のKey Phrase音声の有無

全記事・全時代を通じて**なし**。「Key Phrase」抽出・選定・音声化という
工程自体がER-002には存在しない(方式L/P/Uの比較実験はER-003-P2D以降で
初めて導入、`er003_output/p2i/ER-003-P2I_decision_record.md`参照)。

### 2-5. B2のPoints / In One Line音声の有無

| 記事 | 現行ER-003 B2 | ER-002時代 |
|---|---|---|
| A01 | 独立した「Points/In One Line」音声はなし(本文と地続きの1本の音声のみが存在する場合、下記2-6参照) | ER-002の台本には"Today's Semifinal Turning Point Points" / "Point One" / "Point Two" / "In One Line"の構造見出しが含まれており、**本文と一体化した1本のTTS音声の中にPoints/In One Lineの読み上げが含まれている**(`er002_output/A01/manifest.json`の`element_checks`で構造要素の出現を確認済み)。独立した音声ファイルとしては分離されていない |
| A02 | 同上、なし | 同上(Points/In One Line含みの1本構成) |
| ADD03 | なし | なし(音声自体が存在しない) |

### 2-6. B2を通しで接続した試聴音声の有無

**全記事・全時代を通じてなし。** ER-002のA01/A02音声は「本文+Points+
In One Line」が最初から1本のTTS呼び出しで生成されたものであり、
「複数パーツを後から接続する」という工程(ER-003のPreview+本文+
Key Phrase+ナレーションを結合する`p9a.assemble`のような処理)自体が
存在しない。したがって「通しで接続した試聴音声」という定義に該当する
成果物は、ER-002・ER-003いずれにも存在しない。

### 2-7. Intro/Outro等を含むPodcast完成版の有無

**全記事・全時代を通じてなし。** Intro/Outro/notification等の番組
共通要素は、ER-003のB1パイプライン(`er003_b1_p9a_audio.py`)で初めて
導入されたものであり、ER-002のS3実験にはこの概念が存在しない
(ER-002の成果物は「記事1本分の読み上げ音声」のみで、番組としての
体裁は整えられていない)。

### 2-8. ユーザー試聴記録の有無

| 記事 | 現行ER-003 B2 | ER-002時代 |
|---|---|---|
| A01 | **記録なし**(音声が存在しないため試聴不可能) | **あり、完了**。`er002_output/A01/user_evaluation.json`: `"status": "completed", "listened_to_end": true, "completed_at": "2026-07-19"`。改訂版(v1.1B)も試聴されたが`"listened_to_end": false`(In One Line開始時点で停止) |
| A02 | 記録なし | **あり、完了**。`er002_output/A02/user_evaluation.json`: `"status": "completed", "listened_to_end": true, "completed_at": "2026-07-19"` |
| ADD03 | 記録なし | 記録なし(音声が存在しないため) |

### 2-9. ユーザー承認記録の有無

| 記事 | 現行ER-003 B2 | ER-002時代 |
|---|---|---|
| A01 | **なし** | 試聴は完了しているが**承認ではなく否定的判定**。`editorial_diagnosis.primary: "COMMON_SCRIPT_EDITORIAL_FAILURE"`、`content_interest: "neutral"`、改訂版は`"user_acceptance": "rejected"` |
| A02 | なし | 同様に**否定的判定**。`editorial_diagnosis.primary: "TOPIC_SELECTION_AND_SCRIPT_EDITORIAL_FAILURE"`、`content_interest: "no"` |
| ADD03 | なし | 該当なし |

---

## 3. 各成果物のpath / sha256 / manifest / commit(確認できたもの)

| 記事 | 成果物 | path | sha256 | manifest | commit |
|---|---|---|---|---|---|
| A01(ER-002) | 本文音声(初版) | `er002_output/A01/final_audio_dynamics3.wav` | `6992be41...15931` | `er002_output/A01/manifest.json` | `ed0f786`(JSON側。wavは`.gitignore`の`*.wav`ルールにより現在も**未追跡**) |
| A01(ER-002) | 本文音声(v1.1B改訂版) | `er002_output/A01/v1_1b_c1/final_audio_dynamics3.wav` | `0411a6f7...8cf1a` | `er002_output/A01/v1_1b_c1/manifest.json`, `provenance.json` | `f90b399` |
| A02(ER-002) | 本文音声 | `er002_output/A02/final_audio_dynamics3.wav` | `acc52fce...a0a8c` | `er002_output/A02/manifest.json` | `ed0f786` |
| ADD03 | (音声なし) | — | — | `er002_output/v1_2m_r2/ADD03/raw_article_final.md`(日本語記事下書きのみ) | — |
| A04(参考、無関係記事) | 本文音声2種(Aoede/Charon) | `er002_output/A04/aoede/final_audio_dynamics3.wav`, `er002_output/A04/charon/final_audio_dynamics3.wav` | 未計測(本監査スコープ外の参考情報) | `er002_output/A04/{aoede,charon}/manifest.json` | `7742945` |

**A04についての補足**: ユーザー指示により確認したが、A04は「Meta Museの
Instagram AI機能撤去」という**現行A01/A02/ADD03のいずれとも無関係な
技術記事**である(`er002_output/A04/topic_selection.json`で確認)。
かつユーザー評価は両声とも`"status": "pending_user_listening"`のまま
未完了であり、承認・否定いずれの判定も下されていない。

**gitignore・git履歴についての確認**: `.gitignore`の`*.wav`ルールにより、
上記すべての`.wav`は最初から意図的にGit管理対象外である(commit記録が
ないのは「生成されなかったから」ではなく「音声実体はGit管理しない
プロジェクト方針」のため)。全branch・reflogを含めて`git log --all
--diff-filter=D -- "*.wav"`を実行し、**過去にcommitされ後で削除された
wavファイルは0件**であることも確認した(=working tree外に「失われた
音声」が存在する可能性も否定できた)。manifest/JSON類(音声の生成条件・
QA結果・ユーザー評価)は通常通りGit管理されており、これらから当時の
音声生成実績を過不足なく復元できた。

---

## 4. 最終整理表(ユーザー指定フォーマット)

| 記事 | B2本文 | 本文TTS生成実績 | 現在音声ファイル | 通し試聴版 | Podcast完成版 | ユーザー試聴 | 根拠 |
|---|---|---|---|---|---|---|---|
| **A01**(現行ER-003 B2) | あり | **なし** | なし | なし | なし | なし | `er003_output/p2/A01/b2_version_raw.md`、TTS呼び出しコード・ログが存在しない(grep確認) |
| A01(参考: ER-002当時、CEFR無指定) | あり(別内容) | **あり**(初版+v1.1B改訂版、計2回) | あり(working tree、Git未追跡) | なし | なし | **あり、完了**(否定的評価、改訂版は拒否) | `er002_output/A01/manifest.json`, `user_evaluation.json`, `v1_1b_c1/*` |
| **A02**(現行ER-003 B2) | あり | **なし** | なし | なし | なし | なし | `er003_output/p2/A02/b2_version_raw.md`、TTS呼び出し記録なし |
| A02(参考: ER-002当時、CEFR無指定) | あり(別内容) | **あり**(1回) | あり(working tree、Git未追跡) | なし | なし | **あり、完了**(否定的評価) | `er002_output/A02/manifest.json`, `user_evaluation.json` |
| **ADD03**(現行ER-003 B2) | あり | **なし** | なし | なし | なし | なし | `er003_output/p2/ADD03/b2_version_raw.md`、TTS呼び出し記録なし |
| ADD03(参考: ER-002当時) | 日本語下書きのみ、英語台本なし | **なし** | なし | なし | なし | なし | `er002_output/v1_2m_r2/ADD03/raw_article_final.md` |

---

## 5. 「B2まで音声制作を完了してからB1へ移った」という理解について

**証拠に基づき、誤りと判定する。**

- 現行ER-003のCEFR B2テキスト(3記事とも)について、本文TTS・Preview・
  Key Phrase・Points/In One Line・通し試聴版・Podcast完成版のいずれも、
  生成された記録・試みられた記録が一切ない。
- 「音声制作・試聴・調整を実施していた」という記憶自体は、**ER-002の
  実行バッチ「B2」ではなく「B1」(A01・A02)** について事実であるが、
  これはCEFRレベルとは無関係な採番であり、かつ台本の中身も現行の
  ER-003 B1・B2いずれとも異なる、**その後ユーザー自身に否定的評価を
  受けて破棄された旧世代の成果物**である。
- ADD03(ホルムズ海峡記事)に至っては、ER-002時代に英語台本すら
  作られておらず、音声制作を「完了」した実績は時系列的に存在しない
  (ADD03が記事として最初に登場するのはER-002のv1_2m_r2、日本語下書き
  段階のみ)。

したがって、「B2音声制作 → B1音声制作」という順序で完了させてきた、
という理解は事実と一致しない。正しい時系列は次の通りである。

1. ER-002-S3(2026-07-18〜19): CEFR無指定の台本でA01・A02の音声を生成・
   試聴・評価 → **否定的評価により台本を作り直すも再度拒否、実験放棄**
2. ER-002-v1.2M(日付不明、j1〜r4): 日本語記事下書きの作り直し
   (A01・A02・ADD01〜05・ADD03等、テキストのみ、音声化なし)
3. ER-003: 新アーキテクチャで(Natural English Source→)B1を先に音声まで
   完成(A01・A02・ADD03の3記事)。B2は**テキストのみ生成、音声化は
   一度も実施していない**。A2は仕様監査のみ実施済み(`ER-003-A2-00`)、
   本文・音声とも未着手。

---

## 6. 本監査のスコープ外(実施していないこと)

- B2音声の新規生成・再生成
- 既存コードの変更
- push

---

## 参照元

- `er002_output/A01/manifest.json`, `user_evaluation.json`, `final_audio_dynamics3.wav`
- `er002_output/A01/v1_1b_c1/manifest.json`, `user_evaluation.json`, `provenance.json`
- `er002_output/A02/manifest.json`, `user_evaluation.json`, `final_audio_dynamics3.wav`
- `er002_output/A04/{aoede,charon}/manifest.json`, `user_evaluation.json`(参考、無関係記事)
- `er002_output/v1_2m_r2/ADD03/raw_article_final.md`
- `er002_s3_config.py`(バッチ「B1/B2/B3」の定義)
- [er003_output/p2/A01/b2_version_raw.md](er003_output/p2/A01/b2_version_raw.md)
- [er003_output/p2/A02/b2_version_raw.md](er003_output/p2/A02/b2_version_raw.md)
- [er003_output/p2/ADD03/b2_version_raw.md](er003_output/p2/ADD03/b2_version_raw.md)
- git全branch・reflog確認(`git log --all --diff-filter=D -- "*.wav"`、結果0件)
