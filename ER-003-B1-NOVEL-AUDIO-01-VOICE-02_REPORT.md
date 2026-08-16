# ER-003-B1-NOVEL-AUDIO-01-VOICE-02 実行報告(Point One/Two=Aoede化 + Point explanation削除)

**管理ID: ER-003-B1-NOVEL-AUDIO-01-VOICE-02(ユーザー指示によるVOICE-01の追加修正)**
**実施日: 2026-08-16**
**ステータス: `PROTOTYPE / EXPERIMENT`(N増し検証。Production仕様化はしていない)**

## 背景・ユーザー指示(2件)

1. 「First point./Second point.およびそれに続く英文は記事本体だから
   Aoede(女性)に変更してほしい」— VOICE-01ではPoint One/Two(見出し+
   本文)をNavigator役としてCharonへ変更していたが、これを記事本体
   (Listeningコンテンツ)として扱い直し、Aoedeへ戻す。
2. 「"Point解説"はPreviewに対する日本語訳として機能していたため、
   英語化すると"Here's a quick preview."と内容が重複する。B1では
   不要なので削除してほしい」— VOICE-01で英語化して残していた
   "Point explanation"("Here's the point.")セグメントを、B1構成
   からは完全に削除する。

## A. 変更内容

| セクション | VOICE-01 | 今回(VOICE-02) |
|---|---|---|
| Point explanation("Here's the point.") | Charon(維持) | **削除**(Preview intro直後は既存pause 0.65秒のみ) |
| "First point."/"Second point."見出し | Charon | **Aoede** |
| Point One/Two本文 | Charon | **Aoede**(元のNOVEL-AUDIO-01時点のAoede音声をそのまま再利用) |

それ以外(Welcome/Topic intro/Preview intro/Key phrases intro/Full
story intro/番号ラベル/Key Phrase日本語meaning = Charon、Preview/Key
Phrase英語Component/Full Story Part1・2 = Aoede、Comment1-4/In One
Line = Charon)はVOICE-01から無変更。

## B. 発見した技術的問題と対策

Point見出しをAoedeで再生成する1回目の試行で、ASR検証ロジックの
チェック漏れ(単語列の先頭一致は確認していたが、末尾の長さ上限
チェックを付け忘れていた)により、"First point."の生成結果に無関係
かつ不適切な内容("First point sex is always on his mind."という
hallucination)が含まれていたにもかかわらず、誤って合格判定してしまう
自己回帰的なミスがあった。生成直後に自分でASR全文を確認して発見し、
即座に該当ファイルを破棄・長さチェックを追加したうえで再生成し直した
(最終的に採用した音声はEXACT_MATCH+長さ確認済み、hallucination内容は
含まれていないことを確認)。

## C. Pause構成の変更

Preview introの直後にあった「pause_0.65 → Point explanation →
pause_0.7」を、「pause_0.65」のみに簡略化した(Point explanation削除に
伴う)。新しいpause値は作らず、既存の0.65秒をそのまま残した。Point
見出し→本文間のpause(0.7秒、Point explanation由来の値を転用)は
VOICE-01から変更していない。

## D. Full Audio

- 総尺: **392.421秒(6分32秒)**(VOICE-01の394.332秒から、Point
  explanation削除分だけ短縮)
- clipping: なし(peak 0.95)
- 日本語残存Audit: Key Phrase訳(5件)以外0件
- head/tail cut: 新規生成した2 segment(Point見出し×2)を確認、問題なし

## E. Regression Test

既存回帰テスト37件、全PASS。

## F. Artifact

既存Blind Listening Artifactを更新(同一URL)。Voice Allocation表の
Point One/Two行をAoedeへ修正、Point explanation削除の説明を追記。

URL: https://claude.ai/code/artifact/701978f4-0a54-489e-a766-6cdeba8d91d7

## G. Production非変更確認

記事本文・Fact Ledger・B1 Scaffold構造・Production本体は無変更。
今回の変更はAudio Shell構成(Point explanationの削除)とvoice割当てに
限定される。

## H. Git

commit/push結果は、本報告の送付メッセージ末尾を参照。

## 対象ファイル一覧

| ファイル | 内容 |
|---|---|
| `er003_v1_sing01_point_headings_aoede.py`(新規) | Point見出しAoede版生成(hallucination検出・再生成含む) |
| `er003_v1_sing01_assemble_v3_generate.py`(新規) | Point explanation削除+Point One/Two Aoede化後のFull Audio組み立て |
| `ER-003-B1-NOVEL-AUDIO-01-VOICE-02_REPORT.md`(新規) | 本報告書 |
