# ER-003-B1-SCAFFOLD-AUDIO-02 実行報告(A02 B1 Supported Natural English 完成版Audio)

**管理ID: ER-003-B1-SCAFFOLD-AUDIO-02**
**実施日: 2026-08-15**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

## A. A2 Audio Shell Audit

実装前に、A02のA2最終承認済みAudio Shellをread-onlyで確認した。

**参照したSource of Truth(優先順位順)**:
1. `CURRENT_SPEC.md`(「CEFR-A2構造・音声仕様」「Cross-level仕様」「Key
   Phrase」「Preview」「Full Story」「Audio Assembly」各節)
2. `DECISION_LOG.md`(ER-003-A2-AUDIO-AB-01のA/B採用記録、commit
   `e0e9a8d`)
3. `ARTIFACT_REGISTRY.md`(A02のPodcast組立ステータス確認)
4. **最終承認script**: `er003_v1_a2_audio_ab_01_generate.py`
   (variant B採用、`ER-003-A2-AUDIO-AB-01_REPORT.md`)

**継承した内容(A2から無変更)**:
- Intro(`C:/Users/tensh/sound/Intro.mp3`)・Outro(`.../outro.mp3`)・
  Notification(`.../notification.mp3`、同一ファイルを3箇所で再利用)
- Welcome・Topic Intro・Japanese Title・Preview Intro・**Point解説**
  ("ポイント解説"という4文字の固定ラベル)・Key Phrases Intro・Full
  Story Introの各service-level narration(A01/A02の既存承認済み音声)
- 全pause値: Point解説→Preview 0.7秒、Point One→Point Two 0.8秒、In
  One Line→Outro 0.8秒、Comment前後 1.0秒/0.8秒、Comment前後の効果音
  なし(ポーズのみ)
- Key Phraseブロック構造(`p9a.build_key_phrase_block`、内部pause0.4秒・
  ブロック末尾0.8秒)
- 音量調整方式(Preview/Full Story Part1の平均RMSをアンカーとするscalar
  gain、Outroは post-gain Introへ一致させた上で心理音響ベースの減衰を
  2段適用)

**SoT間の食い違い(発見、報告のみで独断判断はしていない)**:
- `CURRENT_SPEC.md:148`の「notification2挿入 | Full Story内2箇所
  (Today's Points直前、In One Line直前)」は、A2最終scriptの実装と
  一致しない。実際のA2 Shellはnotificationを3箇所とも**サービス
  ラップ区間**(Japanese Title後・Preview後・Key Phrases後)に配置して
  おり、Full Story本文の内部(Comment/Points周辺)には一切配置していない。
  これはB1(19パート)時代の仕様記述が、A2(11パート content構造)導入後
  も更新されないまま残っている可能性が高いと考えられるが、CURRENT_SPEC
  自体は書き換えていない。今回はコードで確認された実装(A2最終script)を
  正とし、これをそのままB1へ継承した
- `topic_intro`/`japanese_title`の音声は、記事固有だがCEFRレベル非依存
  としてA2から継承・再利用したが、その文言(`"Today's topic is UK
  Plans Midnight Social Media Break for Teenagers."`)は、今回の固定
  B2 V2記事のタイトル("Britain Plans to Turn Down the Social Media
  Noise at Night")とは異なる、旧B1本文時代のタイトルに基づいている。
  事実として矛盾するものではないが、字面の一致は取れていない。今回は
  既存承認済み音声をそのまま再利用する方針(Shell継承)に従い、新規
  録り直しは行わなかった

## B. Previous Prototypeとの差分

| 項目 | ER-003-B1-SCAFFOLD-AUDIO-01 | ER-003-B1-SCAFFOLD-AUDIO-02(今回) |
|---|---|---|
| Intro | なし | あり(A2既存音声) |
| Outro | なし | あり(A2既存音声、二段減衰) |
| Welcome/Topic Intro/Japanese Title | なし | あり(A2既存音声) |
| Notification/SFX | なし | あり(3箇所、A2既存音声) |
| Preview Intro/Point解説/Key Phrases Intro/Full Story Intro | なし | あり(A2既存音声) |
| 11コンテンツパート(Preview/Comment/News/Key Phrases) | あり(単純連結) | 同一音声をそのまま再利用、A2 Shellへ正しく組み込み |
| 総尺 | 261.3秒(4分21秒) | 316.3秒(5分16秒) |

## C. Final B1 Audio Structure

Intro〜Outroの全41パート(pause含む)は、比較Artifact(K節)の
Full Timelineセクション参照。主要な流れ:

Intro→Welcome→Topic Intro→Japanese Title→Notification1→Preview
Intro→**Point解説**→**Preview(易しい英語)**→Notification2→Key
Phrases Intro→**Key Phrase×5**→Notification3→Full Story Intro→
**Comment1**→**Full Story Part1(B2共通)**→**Comment2**→**Full
Story Part2(B2共通)**→**Comment3**→**Point One(B2共通)**→**Point
Two(B2共通)**→**Comment4**→**In One Line(B2共通)**→Outro

(太字がB1固有のコンテンツ、それ以外はA2 Shellからの無変更継承)

## D. Key Phrase Audio

**使用方式**: A2と同一のE→J→E方式(`p9a.build_key_phrase_block`、
無変更)。ただし選定内容はA2とは別(B1固有の5件、B2共通ニュース本文
から選定済み: ER-003-B1-SCAFFOLD-01)。

**QA**: 5件ともER-003-B1-SCAFFOLD-AUDIO-01でTTS生成→ASR検証→合格
確認済み。A2のKey Phrase Component/meaning音声(opt out/covered apps
等)は一切使用していない(記事内容が異なるため無関係)。

## E. SFX / Notification

Notification(単一音源`notification.mp3`)を3箇所、A2 Shellと同一の
配置(Japanese Title後・Preview後・Key Phrases後)で使用した。Comment
1〜4の前後には、A2仕様(`CURRENT_SPEC.md:93`「Comment前後の効果音:
専用効果音は入れない」)通り、専用SFXを追加していない(ポーズのみ)。

## F. Pause / Transition

全pause値はA2最終script(`er003_v1_a2_audio_ab_01_generate.py`)から
無変更で継承した(A節の表参照)。

**Comment周辺pauseの扱いについて(今回の判断)**: A2のComment用pause
(1.0秒/0.8秒)は本来「英語→日本語」「日本語→英語」という言語切替を
前提に定義されていた。B1ではCommentも英語のため、この言語切替根拠は
文字通りには当てはまらない。今回は、

- 新しいpause秒数を独自に設計しない
- Point One→Point Two(0.8秒、同一言語間の遷移として確立済み)等、
  他の「既決transition rule」に機械的に差し替えることもしない
  (Comment用の1.0秒/0.8秒は、単なる言語切替のためだけでなく、
  「ニュース本文と短い解説パートの切り替わり」という役割の区別にも
  機能している可能性があり、根拠なく緩めることは避けた)

という判断のもと、**A2のComment用pause値(1.0秒/0.8秒)をそのまま
数値として維持**した。これは「言語切替pauseだから不要」と機械的に
判断せず、かつ「新しい秒数を勝手に決める」こともしない、両立させる
ための今回の選択である。妥当性の最終判断はユーザーに委ねる(ユーザー
試聴観点Dで特に確認を依頼する)。

## G. TTS / ASR Hardening

ER-003-B1-SCAFFOLD-AUDIO-01で発見した4件の技術的問題への対策は、
すべて`er003_v1_b1_scaffold_audio_01_generate.py`内の関数として維持
されており、今回のShell組み込みでも(11コンテンツパートを再利用した
ため)引き続き有効である。

| 問題 | 対策 | 状態 |
|---|---|---|
| Markdown強調記号(`**`) | `strip_markdown_emphasis`でTTS入力直前のみ除去 | 維持 |
| カーブ引用符 | 同上 | 維持 |
| 自己言及的な一文でのTTS拒否 | ENGLISH_STYLE_PREFIX失敗時にMINIMAL_INSTRUCTION_PREFIXへ自動フォールバック | 維持 |
| ASR検証の文字列比較バグ | `expected_words_present`(単語列連続部分列一致)へ置換 | 維持 |
| 英国綴り/米国綴り差 | TTS/ASR入力のみAmerican綴りを使用、表示は元の綴りを維持 | 維持 |

これらの**恒久化・共通化・仕様継承チェックリスト化**は、今回のスコープ
外とし、後続のER-003-AUDIO-HARDENING-01で扱う(ユーザー指示により、
今回のRunを中断・変更せず完了させることを優先した)。

## H. Regression Test

`er003_test_b1_scaffold_audio_01.py`(新規)を作成し、ASR検証ロジック
(`expected_words_present`)とTTS入力正規化(`strip_markdown_emphasis`)
の純粋なテキスト処理部分について、12件のテストケースを実行した。

| ケース | 結果 |
|---|---|
| `**` Markdown除去 | PASS |
| カーブ引用符除去 | PASS |
| 正規化後も単語自体は不変 | PASS |
| ストレート引用符は無変更 | PASS |
| 正常一致する音声 | PASS(検証合格) |
| コンマ差で偽陰性にならない | PASS(検証合格) |
| ハイフン複合語(night-curfew)正規化 | PASS(検証合格) |
| 改行を含む原文でも偽陰性にならない | PASS(検証合格) |
| 英国綴り/米国綴り差(このロジック単体では吸収しない、意図通り) | PASS(想定通りFalse) |
| 内容が明らかに異なる音声 | PASS(正しくFalse=不合格) |
| 空ASRテキスト | PASS(正しくFalse=不合格) |
| 複数語Key Phraseの一致 | PASS |

全12件成功(`.venv/Scripts/python.exe -m unittest
er003_test_b1_scaffold_audio_01 -v`で再現可能)。実際のTTS層での修正
効果(400エラー解消・self-reference対策)は、ER-003-B1-SCAFFOLD-
AUDIO-01/02の実行時に本物のTTS+ASRで確認済み(`audit/segment_
generation_results.json`参照、全11パートasr_verified: true)。

## I. Fact Safety

Support(Preview+Comment1-4)は、ER-003-B1-SCAFFOLD-AUDIO-01で確定した
テキストをそのまま音声化した(再修正なし)。

| Check | 結果 |
|---|---|
| Support Fact Checker | `PASS` |
| Support Ledger Deviation Check | `LEDGER_COMPLIANT` |

ニュース本文(B2共通)はER-003-CEFR-DIRECT-02で検証済み。今回はSHA256
一致確認のみを実施し、`match: true`を確認した。

## J. Full Timeline

Intro/Outro/SFX込みの全41パート(pause含む)は比較Artifact(K節)の
Full Timelineセクション、および`er003_output/b1_scaffold_audio_02/
A02/audit/timeline.json`参照。

| # | Section | Type | Duration | New / Reused |
|---|---|---|---:|---|
| 1 | Intro | Shell | 10.7s | Reused(A2既存) |
| 2 | Welcome | Shell | 2.1s | Reused(A01既存) |
| 3 | Topic Intro | Shell | 5.4s | Reused(A02既存) |
| 4 | Japanese Title | Shell | 9.1s | Reused(A02既存) |
| 5 | Notification 1 | Shell | 2.0s | Reused(共通音源) |
| 6 | Preview Intro | Shell | 1.5s | Reused(A01既存) |
| 7 | Point Explanation | Shell | 1.2s | Reused(A01既存) |
| 8 | **Preview** | **Support** | **19.6s** | **Reused(AUDIO-01で新規生成済み)** |
| 9 | Notification 2 | Shell | 2.0s | Reused(共通音源) |
| 10 | Key Phrases Intro | Shell | 1.9s | Reused(A01既存) |
| 11-15 | **Key Phrase 1〜5** | **Key Phrases** | **33.2s(計)** | **Reused(AUDIO-01で新規生成済み)** |
| 16 | Notification 3 | Shell | 2.0s | Reused(共通音源) |
| 17 | Full Story Intro | Shell | 1.9s | Reused(A01既存) |
| 18 | **Comment 1** | **Support** | **6.2s** | **Reused(AUDIO-01で新規生成済み)** |
| 19 | **Full Story Part 1** | **News(B2共通)** | **40.0s** | **Reused(AUDIO-01で新規生成済み)** |
| 20 | **Comment 2** | **Support** | **9.0s** | **Reused** |
| 21 | **Full Story Part 2** | **News(B2共通)** | **55.2s** | **Reused** |
| 22 | **Comment 3** | **Support** | **16.2s** | **Reused** |
| 23 | **Point One** | **News(B2共通)** | **28.8s** | **Reused** |
| 24 | **Point Two** | **News(B2共通)** | **22.1s** | **Reused** |
| 25 | **Comment 4** | **Support** | **13.8s** | **Reused** |
| 26 | **In One Line** | **News(B2共通)** | **12.3s** | **Reused** |
| 27 | Outro | Shell | 6.1s | Reused(A2既存、二段減衰適用) |

(pause区間はここでは省略。詳細はtimeline.json参照)

**合計: 316.3秒(5分16秒)**。今回のRunで新規にTTS/ASR呼び出しを行った
音声は0件(すべてShell継承 + AUDIO-01既存生成の再利用)。

## K. Final Artifact

**URL**: https://claude.ai/code/artifact/dd90ea68-8c7a-4598-84d6-fe1522b4a82e

Intro〜Outroまで通し試聴可能な完成版候補。Full Timeline(Shell/
Support/News/Key Phrasesを色分け)・Key Phrase一覧・技術QA表を掲載。

リポジトリ内の原本: `er003_output/b1_scaffold_audio_02/A02/assembled/English_Your_Way_B1_A02.wav`(WAV)/`.mp3`

## L. Git

commit/push結果は、本報告の送付メッセージ末尾を参照。

## M. Production非変更確認

- **CURRENT_SPEC.md・DECISION_LOG.md・A2最終承認script
  (`er003_v1_a2_audio_ab_01_generate.py`等)・その他Production audio
  モジュール本体**: 無変更。新規の独立ファイル
  (`er003_v1_b1_scaffold_audio_02_generate.py`)から、これらの関数・
  定数を読み取り専用でimportした
- **B1/B2共通化の正式決定**: 行っていない(プロトタイプ検証のまま)
- **A2仕様・A01/ADD03**: 変更・音声化していない
- **OPEN-35(A02台本と2026-08-12確定scriptの不一致)**: 変更・解決
  していない(A節で言及したのみ)
- **TTS voice選定・Audio Dynamics・CEFR仕様・Key Phrase選定ロジック・
  WPM仕様・SFX仕様**: 変更していない

## 対象ファイル・新規Artifact一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_b1_scaffold_audio_02_generate.py`(新規) | A2 Shell継承+B1コンテンツ組み込みの完成版assembleスクリプト。A2最終承認scriptの関数・定数を読み取り専用でimport |
| `er003_test_b1_scaffold_audio_01.py`(新規) | ASR検証ロジック・TTS入力正規化の回帰テスト(12件) |
| `er003_output/b1_scaffold_audio_02/A02/assembled/`(新規) | 完成版wav/mp3(316.3秒) |
| `er003_output/b1_scaffold_audio_02/A02/audit/`(新規) | timeline.json・gain_report.json・b2_text_sha_check.json |
| `er003_output/b1_scaffold_audio_02/A02/player_final.html`(新規) | 完成版Artifact原本 |

## 受入条件チェック

| 条件 | 結果 |
|---|---|
| A2 current Audio ShellをSoTから確認 | 済(A節) |
| Intro反映 | 済 |
| Outro反映 | 済(二段減衰込み) |
| Notification/SFX反映 | 済(3箇所、共通音源) |
| Key Phrase A2音声仕様反映 | 済(presentation方式のみ、内容はB1固有5件) |
| 全11コンテンツパート反映 | 済 |
| pause仕様反映 | 済(F節で扱いを説明) |
| Comment SFXなし等、A2 current仕様と一致 | 済 |
| B2ニュース本文完全一致 | 済(SHA256一致確認) |
| Support Fact Checker PASS | 済 |
| Support Ledger compliant | 済 |
| ASR全新規音声PASS | 該当なし(今回新規TTS/ASR呼び出し0件、AUDIO-01の既存合格結果を再利用) |
| Markdown/quote normalization動作確認 | 済(回帰テスト) |
| British/US spelling validation対応 | 済(回帰テスト) |
| self-reference TTS failure対策確認 | 済(AUDIO-01実績+関数維持) |
| regression test実施 | 済(12件全PASS) |
| 最終完成版assemble成功 | 済(clipping/SHA不一致なし) |
| Artifactで通し試聴可能 | 済 |
| Production非変更 | 済 |
| commit/push結果報告 | 本報告書末尾参照 |
