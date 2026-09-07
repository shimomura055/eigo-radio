# PM-REVIEW-ARTIFACT-RULE-GAP-DIAGNOSTIC-01

読み取り専用診断。Git操作・編集は一切行っていない。`docs/pm/ACTIVE_TASK.md`・
`RESULT_PACKET.md`は対象外(触れていない)。

## 1. 過去の正式ルールの有無(原文引用・管理ID)

ユーザーの認識どおり、「完成候補音声の試聴依頼は音声+完全スクリプトを実
episode構造で提示する」という趣旨の正式ルールは**既に3段階で存在していた**
(新設は不要、重複ルールを足す必要はない)。

**(a) CURRENT_SPEC.md「試聴Artifact(ユーザー提示用ページ)仕様」節、
全script掲載の必須化 — `ER-008-N8-CLOSEOUT-GOVERNANCE-25`(2026-08-29)**
> 今後、ユーザーへ試聴用Artifactを提示する場合、実際に放送される全segmentの
> script(発話される文言そのもの)を同じページへ全文掲載することを標準仕様と
> する。

機械check補助として`er008_listening_artifact_script_standard_25.py`
(`A2_REQUIRED_SEGMENTS`/`B1_REQUIRED_SEGMENTS`、`check_full_script_coverage()`)
とfixture testも同時に作られた。ただし既存の**標準11-part A2/B1構造専用**
であり、新規Artifact生成scriptへの組み込みは「今後」の宿題として明記された
のみ(当時未配線)。

**(b) 適用範囲拡張(単発の試聴リンクも対象) —
`ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18`(2026-09-01)**
> 「全script掲載の必須化」は、正式なNo.8/No.9等の試聴Artifactに限らず、
> ユーザーから「この音声はどこで聞ける?」等、完成音声の確認・試聴・承認の
> ために単発で作成する試聴リンクにも同様に適用する。完成音声だけを提示し、
> full script…を欠いた提示は不可とする。

**(c) 最も直接的なルール — `docs/pm/PM_GOVERNANCE.md` §9-2、
`PM-GOVERNANCE-AUDIO-REVIEW-PAGE-STANDARD-09`(2026-09-06、DECISION_LOG.md
107行〜)**
> 完成音声・Trial音声の試聴を依頼する場合、リンク先ページには音声だけでなく、
> **その音声で実際に読み上げられる完全なスクリプト**(Preview/本文/Key
> Phrases・各Keywordの日本語gloss[表示用、TTS用が異なる場合は併記]/
> Comment/見出し・Intro・Outro等その音声内で読み上げられる全section)を
> **同一ページ**に表示する。A2/B1など複数レベルはレベルごとに音声と
> スクリプトを明確に分ける。segment順・開始時刻付きで「今聞いている箇所の
> 文言」を追える構成にする(クリックseek推奨)。`USER_FINAL_AUDIO_REVIEW_
> REQUIRED`/Trial音声レビューではこの形式を標準とし、**音声だけのreview
> linkは作らない**。

## 2. 適用scope

- (a)(b)は「完成音声の確認・試聴・承認」全般(正式Artifactに限らず単発
  リンクも含む)を対象。Lane・Editorial Type限定の文言は無い。
- (c)は文言上**「完成音声・Trial音声」を明示的に併記**しており、Trial音声を
  scope外とする根拠は原文に存在しない。A Family限定・Lane A限定の記述も無い。
- (c)の末尾に「本原則はFableのユーザー向け報告に適用する」という一文が
  あり、`file:///`形式URLの箇条書きは「sonnet-workerのReport/RESULT_PACKET
  にも同形式で記載させる」と明示するが、「音声+完全スクリプト同一ページ」
  箇条書き自体は主語がFableの説明かSonnetが作るartifactかを明示的に区別
  していない(軽微な曖昧さ、§5で後述)。ただし文言そのもの(「リンク先
  ページには…表示する」)はartifact自体の構造要件として書かれており、
  Fableの発言スタイルの話ではない。

## 3. Trial-08はscope内か

**scope内(該当する)。時系列でも(c)ルールの後に実行されている。**

- (c)のcommitは`8ff9654`(PM-GOVERNANCE-AUDIO-REVIEW-PAGE-STANDARD-09)。
- Lane B Trial-08の成果物commitは`3c8cfab`(2026-09-07 14:23:58 +0900、
  「Voices一人称版B1音声化(Standard同期)の成果物をcommit」)、その直前の
  `7f98f33`(2026-09-07 13:22:56、Trial-07 User Decision記録・Trial-08着手
  記録)より後。
- `git log --oneline`順: `8ff9654`(9-2ルール確定)→`7f98f33`(Trial-08着手)
  →`3c8cfab`(Trial-08成果物)。ルールはTrial-08着手より前から存在していた。
- Trial-08自身のReport(`EDITORIAL-B-FAMILY-VOICES-TRIAL-08-AUDIO-FIRST-
  PERSON-CHECK-01_REPORT.md`3行目)は自ら「試聴ページ:
  `er012_output/editorial_b_voices_trial_08_audio/player.html`(file:///
  形式、音声+完全スクリプト同一ページ)」と(c)の標準文言をなぞって自己
  ラベル付けしている。Sonnet自身も本ルールの適用対象と認識していたことが
  読み取れる。

## 4. なぜ適用されなかったか(証跡付き分類)

実際の`er012_output/editorial_b_voices_trial_08_audio/player.html`を直接
確認した。

**含まれていたもの**: Episode 1(P1、一人称)の単一結合audioタグ+
Hook/Voice A/Voice B/Tension(Trial限定beat)/Closing(In One Line)の5
テキストブロック。Episode 2(P3)のBLOCKED説明。Voice A/B の1人称版vs3人称版
component単体wav比較(4個の個別`<audio>`+本文)。

**欠けていたもの(rule (c)の要求と直接対比)**:
1. **Preview / Comment 1-4のテキストが1件も掲載されていない。**
   Report自身の§4は「Production Support経路…を無変更で使用。全文は
   `p1/b1b/b1_support_texts.json`」「Preview/Comment1-4は…」と、Preview・
   Comment 1-4が実際に生成・TTS化(P1の「全13標準segment」に含まれる)
   された事実を明記しているにもかかわらず、player.htmlにはこれらの本文が
   一切表示されていない。
2. **Key Phrase 5件のテキスト・日本語glossが1件も掲載されていない。**
   Report §0「Key Phrase 5件が`status=OK`」と明記されているが、player.html
   にKey Phraseセクション自体が存在しない。
3. **Intro/Outro/Welcome/Notification等の固定section(rule (c)が明示的に
   列挙する「見出し・Intro・Outro等」)がplayer.htmlに一切無い。**
4. **segment順・開始時刻(クリックseek)が無い。** Episode 1は298.665秒の
   結合済みassembled wav 1本を単一`<audio>`タグで提示しているだけで、
   印刷されている5テキストブロックのどれが音声の何秒に対応するかを示す
   タイムスタンプ・seekリンクが無い(rule (c)「segment順・開始時刻付きで
   『今聞いている箇所の文言』を追える構成にする(クリックseek推奨)」に
   非該当)。
5. Episode 2下段の「Voice A/Voice B: 1P vs 3P並べて聞き比べ」節は、rule
   (c)が求める**完成episode構造としての一体提示ではなく、component
   単体サンプルの並列提示**(narration単体wav×4)であり、これ自体は補足と
   しては有用だが、Episode全体の完全スクリプト要件を代替しない。

**分類(委任文4パターンとの対応)**:
- **Sonnet側の実装漏れ(主因)**: Report自身がPreview/Comment/Key Phrase 5件
  の生成・TTS化を明記しながら、同じ成果物のplayer.htmlにそれらのテキストを
  転記していない。これは既存ルール(c)の文言を認識していた(自己ラベル付け
  で確認済み)にもかかわらず、実装(player.html生成script
  `er012_editorial_b_voices_trial_08_audio.py`)が5-part skeletonの「本体
  テキスト」だけを転記し、Production標準11-part構造の他sectionを転記対象
  に含めなかった実装上の欠落。
- **既存ルールscopeの曖昧さ(副次)**: §2で述べたとおり(c)末尾「本原則は
  Fableのユーザー向け報告に適用する」という一文が、artifact自体の構築主体
  (Sonnet)にも直接同一の拘束力を持つかを明示していない、という軽微な
  曖昧さは存在する。ただし(a)(b)(CURRENT_SPEC側、Fable/Sonnetを区別しない
  一般ルール)は曖昧さ無く「全segmentのscript全文掲載」をartifact自体の
  要件として定めており、(a)(b)だけでも今回の欠落(Preview/Comment/KP/
  Intro/Outro省略)を防ぐには十分だった。したがって「ルール不在」や
  「scope外」が根本原因とは言えない。
- **Fableの受入時レビュー漏れ(検証不能・UNVERIFIED)**: Fableの委任文原文・
  受入時の会話ログは本リポジトリから確認できない(`docs/pm/ACTIVE_TASK.md`
  はgit管理外、`git log -- docs/pm/ACTIVE_TASK.md`は空)。ただし、commit
  `3c8cfab`(Trial-08成果物)後、ユーザーが本Diagnosticを依頼するまでの間に
  player.htmlの補完・差し替えcommitは存在しない(`git log --oneline -- \
  er012_output/editorial_b_voices_trial_08_audio`は`3c8cfab`1件のみ)。
  Gate 7(Fableの受入判定)が(c)の具体的チェックリスト(Preview/Comment/KP/
  Intro/Outro/timestamp)と照合して差し戻した形跡は確認できない。

## 5. 既存対策が機能しなかった理由

- **CURRENT_SPEC (a)の機械check(`check_full_script_coverage()`)は今回
  使われていない。** このモジュールは標準A2/B1の11-part構造専用に定義
  (`A2_REQUIRED_SEGMENTS`/`B1_REQUIRED_SEGMENTS`)されており、Lane B
  Voices(5-part skeleton+Trial限定beat)という新しいEditorial Type構造には
  未拡張のまま(ER-008導入時点で「次回以降の新規Artifact生成scriptへ組み
  込むこと」と明記されていたが、Trial-08時点でも組み込まれていない)。
  結果、Trial-08のplayer.html生成は完全に手動判断に依存し、機械的な
  欠落検知が一切働かなかった。
- **PM_GOVERNANCE (c)は文書ルールのみで、対応する機械checkが存在しない。**
  9-2は「Fableの説明原則」節に置かれており、Sonnetの委任文テンプレートや
  Gate 7の具体的チェック項目としては明文化されていない(Gate 7自体は
  「Production正式path/runtime evidence/test/approved specとの一致/
  retry・fallbackとの整合/QCD副作用」という一般基準のみを定め、audio
  review artifactの必須要素チェックリストは持たない)。
- **Gate 7受入判定の実行有無は本リポジトリからは検証不能**(§4参照)。
  少なくとも、受入判定を行った痕跡(差し戻しcommit・rework記録)は無い。

## 6. 必要な最小再発防止(実装しない、提案のみ)

既存ルール(a)(b)(c)の内容そのものは十分であり、**新規ルールの追加は
不要**と判断する。不足しているのは「実行可能性(enforceability)」であり、
最小限は以下(いずれも文書・チェック項目の追加のみを想定、実装は今回一切
行っていない):

1. **(c)の主語明確化**: 「本原則はFableのユーザー向け報告に適用する」の
   直前または直後に、「artifact自体(player.html等)を構築するSonnetにも
   同様に適用する」旨を一文追記し、§2で述べた軽微な曖昧さを解消する。
2. **Gate 7チェックリスト化**: audio review artifactを受入判定する際の
   最小チェック項目(「実際にTTS化・Assemblyされた全section(Preview/
   Comment/Key Phrase/Intro/Outro等)がテキストとして掲載されているか」
   「segment順・開始時刻/click-seekがあるか」「音声だけのreview linkに
   なっていないか」)をPM_GOVERNANCE.md Gate 7またはCloseout Mandatory
   Checkへ明文の確認項目として追加する。
3. **新規Editorial Type/Lane向けartifact生成時、CURRENT_SPEC (a)の
   `check_full_script_coverage()`相当パターン(REQUIRED_SEGMENTS定義+機械
   check)を、その構造に合わせて都度定義・実行することを標準手順として
   明記する**(既存A2/B1専用モジュールを流用できない新構造の場合の手順を
   明確化)。
4. 委任文テンプレート(Fableがsonnet-workerへaudio review artifact生成を
   委任する際)に、(c)の必須要素リストをその都度inlineで再掲することを
   推奨する(ルール参照だけに頼らず、委任文自体に要件を明記)。

いずれもユーザー承認(`APPROVED_FOR_PRODUCTION`相当の運用ルール確定)が
必要な事項であり、本タスクでは提案のみで実装していない。

## 7. 参照ファイル

- `C:\Users\tensh\eigo-radio\CURRENT_SPEC.md`(453-459行、試聴Artifact仕様節)
- `C:\Users\tensh\eigo-radio\docs\pm\PM_GOVERNANCE.md`(312-364行 §9-2、
  580-609行 変更履歴)
- `C:\Users\tensh\eigo-radio\DECISION_LOG.md`(107-148行
  PM-GOVERNANCE-AUDIO-REVIEW-PAGE-STANDARD-09、3120-3151行
  ER-010-NO9-B1-APPROVAL-AND-OPEN103-TTS-DIAGNOSTIC-18)
- `C:\Users\tensh\eigo-radio\OPEN_ITEMS.md`(OPEN-120/OPEN-123行、Trial-08
  言及)
- `C:\Users\tensh\eigo-radio\EDITORIAL-B-FAMILY-VOICES-TRIAL-08-AUDIO-FIRST-
  PERSON-CHECK-01_REPORT.md`(全文)
- `C:\Users\tensh\eigo-radio\er012_output\editorial_b_voices_trial_08_audio\
  player.html`(全文確認)
- `C:\Users\tensh\eigo-radio\er008_listening_artifact_script_standard_25.py`
  (既存機械checkモジュール、参照のみ・未実行)
- git commit: `8ff9654`(9-2ルール確定)、`7f98f33`(Trial-08着手記録)、
  `3c8cfab`(Trial-08成果物)
