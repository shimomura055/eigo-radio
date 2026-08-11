# OPEN_ITEMS — 未確定事項・技術的負債

**管理ID: ER-PM-001**
**最終更新: 2026-08-10(ER-003-CROSSLEVEL-AUDIO-04反映)**

検討中・候補・未確定仕様・技術的負債を記録する。確定済み仕様は書かない
(→[CURRENT_SPEC.md](CURRENT_SPEC.md))。

| ID | 内容 | 状態 | 種類 | Blocking | 次Action |
|---|---|---|---|---|---|
| OPEN-01 | CEFR-A2の正式仕様(語彙・文長・語数等、全20項目)が一切存在しない | `PROTOTYPE / UNDER_REVIEW`(ER-003-A2-01→A2-02→A2-03と3段階で暫定仕様を検証中) | 仕様未決 | Blocking(CURRENT_SPECへ正式反映するまでは音声化・量産着手不可) | ユーザーがA2-03の3記事テキストを確認し、DECIDEDとするかどうか判断する。[ER-003-A2-03_LISTENING_SIMPLIFICATION.md](ER-003-A2-03_LISTENING_SIMPLIFICATION.md)参照 |
| OPEN-17 | [訂正・ER-003-A2-STRUCT-02] A2超一般語を記事全体で最大5語に制限する仕様 | `REJECTED / NO_FURTHER_ACTION` | 検証結果・却下 | Non-blocking(対応不要) | 対応不要。正式CEFR-A2 wordlist不在によりLLM判定基準が安定しない、厳密な上限達成には生成→QA→再生成の反復が必要で量産フローを不必要に複雑化する、複雑化に見合うリスニング難易度改善効果が確認できなかった、との理由でユーザーが不採用と判断(詳細は[DECISION_LOG.md](DECISION_LOG.md))。「A2として可能な範囲で平易な語を優先する」という原則(数値上限なし)は[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)に維持 |
| OPEN-19 | [ER-003-A2-STRUCT-02] 抽象語を「誰が何をしたか」という具体的行動表現へ優先的に変換する一般ルール | `REJECTED_AS_GENERAL_RULE` | 検証結果・却下 | Non-blocking(対応不要) | 対応不要。具体化で分かりやすくなるケースはあったが、無理な変換で意味関係が見えにくくなる・説明が長くなるケースもあり、「抽象=悪、具体=良」という一方向ルールにはしないとユーザーが判断。記事・文脈ごとに自然な方を選ぶ通常の編集判断へ委ねる |
| OPEN-20 | [ER-003-A2-STRUCT-02] 固有名詞のtoken数・密度を意図的に下げる一般ルール | `REJECTED / NO_FURTHER_ACTION` | 検証結果・却下 | Non-blocking(対応不要) | 対応不要。A01では固有名詞が減った一方、ADD03ではTrumpを明示的主語にした結果増加し、「誰が何をしたかを明確にする」「referentを明確にする」「spoken-firstにする」という別の分かりやすさ要求と競合することが判明。数量目標・密度目標は設けず、記事理解上の必要性で通常の編集判断により決める |
| OPEN-18 | [訂正・ER-003-A2-STRUCT-02] ER-003-A2-03の1文1数字ルールで、ADD03の日付"July 13, 2026"が2つの数字として検出されていた件 | `DECIDED`(原則整理のみ、checker実装は未着手) | 仕様の曖昧点・整理済み | Non-blocking | 対応不要(原則面)。「月+日+年」の日付表記は年齢範囲・スコア・時間帯と同様に1つの日付情報として扱う方針が確定した([DECISION_LOG.md](DECISION_LOG.md))。`er003_a2_article.py`の`_EXEMPT_NUMBER_PATTERNS`への正規表現追加は、今回のスコープでは実施しない(必要になった時点で対応) |
| OPEN-02 | A2の生成元(Natural English Sourceから独立生成 vs B1/B2からの派生簡略化)が、ユーザー依頼文言と公式decision recordで矛盾 | `DECIDED`(ER-003-A2-01実行分については独立生成を採用、恒久方針としての確定はユーザー判断待ち) | 仕様矛盾 | Non-blocking(今回は独立生成で実施し、矛盾は解消せず併記) | ER-003-A2-01では独立生成方式を採用したことをユーザーへ明示。恒久的な方針決定はユーザーに委ねる |
| OPEN-13 | ER-003-A2-STRUCT-01 Candidate A: Full Story分割+日本語コメント(Comment1〜4)による構造支援。11パート構成。**3記事(A01/A02/ADD03)とも音声プロトタイプまで完成**(A02: ER-003-A2-AUDIO-01→CROSSLEVEL-AUDIO-01再試作。A01/ADD03: ER-003-CROSSLEVEL-AUDIO-02で初回音声化、294.2秒/327.4秒、機械QA合格) | `PROTOTYPE_BUILT / UNDER_EVALUATION`(3記事とも音声レベルで検証済み) | 構造支援候補 | Non-blocking | ユーザーが3記事分の音声プロトタイプ([ER-003-A2-AUDIO-01_REPORT.md](ER-003-A2-AUDIO-01_REPORT.md)、[ER-003-CROSSLEVEL-AUDIO-01_REPORT.md](ER-003-CROSSLEVEL-AUDIO-01_REPORT.md)、[ER-003-CROSSLEVEL-AUDIO-02_REPORT.md](ER-003-CROSSLEVEL-AUDIO-02_REPORT.md))を確認し、ADOPTED/REJECTEDを判断する。ADOPTEDの場合、A2速度最適化(別Task)→自動一般化コードの順で進める |
| OPEN-21 | ER-003-A2-AUDIO-01の機械QAで2箇所、ASRの数字表記ゆれ(Comment3「2つ」→「二つ」、Point Two"seven in ten"→"7 in 10")を検出。TTS内容自体は正常と判断したが、最終確認はユーザー試聴に委ねている | `UNDER_REVIEW` | 要ユーザー試聴確認 | Non-blocking | ユーザーが該当箇所(約192秒・242秒付近)を試聴し、TTS音声が正常かどうか最終確認する |
| OPEN-22 | 共有診断関数`er003_b1_p4_audio.get_full_text_via_azure_stt_continuous`のデフォルト`timeout_seconds=90.0`が、長尺音声(5分超)では不十分で、timeout時にエラーを返さず部分結果を正常として返してしまう制限を確認。呼び出し側で`timeout_seconds`を大きく指定することで回避したが、関数自体の挙動は未修正 | `TBD` | 技術的負債 | Non-blocking(呼び出し側で回避済み) | 同種の長尺音声を診断する機会が今後増えた場合、関数側のtimeout処理(タイムアウトと正常終了を明確に区別する)を修正するか検討する。今回は共有モジュールを変更していない |
| OPEN-14 | ER-003-A2-STRUCT-01: Full Story前の簡易Listening Questions(2問程度) | `CANDIDATE / NOT_ADOPTED` | 構造支援候補 | Non-blocking | 同上 |
| OPEN-15 | [訂正・ER-003-A2-02] B1承認済みKey Phraseの語そのものがA2本文に残るかは要件にしない。A2 Key PhraseはA2本文確定後に本文から改めて選定する(方針確定) | `DECIDED` | 方針整理 | Non-blocking | 対応不要。当初「B1 Key Phrase語の消失」を問題視していたが、これは誤った懸念設定だったと整理した。実際の問題は主要fact自体がFull StoryからPointsへ流出していたことであり、これはER-003-A2-02で解消(下記OPEN-16参照) |
| OPEN-16 | A2-01でFull Storyの情報比重が崩れていた(3記事ともFull Story語数シェアが12.5〜29%まで低下、B1は49〜62%)。ER-003-A2-02のprompt改訂(情報削減を目的化しない、Full Storyに主要factを必須化)で3記事ともFull Story比重をB1同等(52〜65%)まで回復したことを確認済み | `DECIDED`(A2-02として確定、ただしCURRENT_SPECへの正式反映はユーザー承認待ち) | 検証結果 | Non-blocking | ユーザーがA2-02本文を確認し、DECIDEDとしてCURRENT_SPECへ反映するか判断する |
| OPEN-03 | CEFR-B2の音声化(Preview/Key Phrase/Full Story/Podcast組み立て)が一度も実施されていない | `TBD` | 未着手 | Non-blocking(B1公開には影響しない) | 着手するかどうか・いつ着手するかをユーザーが判断 |
| OPEN-04 | `used_form`/`key_phrase`の100%重複 | `DECIDED`(整理しない方針は確定済み) | 技術的負債 | Non-blocking | 実際に分ける必要が生じるまで対応しない(意図的放置) |
| OPEN-05 | 短文TTS hallucinationの根本原因(モデル側の挙動)が未解明 | `UNDER_REVIEW` | 技術的負債 | Non-blocking(strict検証+fallbackで運用上は吸収済み) | 発生時にstrict検証+fallbackで対応を継続。原因調査は優先度低 |
| OPEN-06 | ASR homophone ambiguityを機械的に判別する手段が未実装(同音異義語リスト等) | `TBD` | 技術的負債 | Non-blocking(human reviewフローで運用上は吸収済み) | 次に同種の事象が実際に発生してから検討(先回り実装はしない) |
| OPEN-07 | 正式なLUFS masteringが未導入(現状はscalar RMS基準の簡易調整のみ) | `TBD` | 技術的負債 | Non-blocking | 音質改善の必要が生じた際に検討 |
| OPEN-08 | ADD03初回Full Story生成(1回目3試行不合格分)の詳細ログが失われている(`stage_a_generate_body_audio`のバグ、2回目実行分からは修正済み) | `HISTORICAL`(バグ自体は修正済み) | 記録欠落 | Non-blocking | 再発防止は完了。過去分の復元は行わない |
| OPEN-09 | Dynamics3不使用の決定について、比較検討の詳細記録(なぜscalar RMSを選んだかの根拠レポート)が見当たらない | `TBD` | 記録欠落 | Non-blocking | 発見時に追記。現時点では推測で埋めない |
| OPEN-10 | A01(CEFR-B1)の「エピソード全体の最終承認」が未取得(`publication_status: NOT_APPROVED`のまま) | `UNDER_REVIEW` | 公開判断待ち | Non-blocking(A02・ADD03の作業には影響しない) | ユーザーがA01最終版(r2)を通しで試聴し、公開可否を判断 |
| OPEN-11 | A02・ADD03も`user_quality_status: PASS`だが`publication_status`は`NOT_APPROVED`のまま(品質OKと公開承認は別判断) | `UNDER_REVIEW` | 公開判断待ち | Non-blocking | ユーザーが公開判断を行うタイミングで確定 |
| OPEN-12 | `ER-003-B1_HANDOFF.md`が旧運用のまま(仕様・経緯を大量に含む29KB超のファイル)で、新ルール(直近作業再開専用)に未準拠 | `TBD` | 運用移行未完了 | Non-blocking | 次回以降の更新時に新フォーマットへ段階的に移行(今回は大規模書き換えを行わない) |
| OPEN-27 | ER-003-CROSSLEVEL-AUDIO-02で発見: `scripts/run_ci_tests.py`(公式CI回帰テストランナー)が、リポジトリ直下の6ファイル(`er003_test_b1_p7a_audio.py`/`er003_test_b1_p7c_audio.py`/`er003_test_b1_p8a_audio.py`/`er003_test_b1_p9a_audio.py`/`er003_test_b1_p9a_r1_audio.py`/`er003_test_key_words_canonicalization.py`)が`ci_test_manifest.json`のinclude/excludeに未登録であるためmanifest検証エラーで起動できない状態だった(いずれも本セッションで新規作成したファイルではなく、既存commit時点から未登録) | `TBD` | 技術的負債・CI回帰不能 | Blocking(公式CIランナーでの全体回帰テストが実行不能) | 6ファイルを`ci_test_manifest.json`のinclude(またはexclude)へ登録する必要がある。本ステージでは原因調査のみ行い、manifestは変更していない(共有CI設定の無断変更を避けるため)。今回は代替として該当モジュールの個別`unittest`実行とpy_compileでの構文確認のみ実施(詳細は[ER-003-CROSSLEVEL-AUDIO-02_REPORT.md](ER-003-CROSSLEVEL-AUDIO-02_REPORT.md)参照) |
| OPEN-28 | ER-003-CROSSLEVEL-AUDIO-02で発見: 方式L選定+Canonicalizationが機械的に生成したjapanese_gloss(例: ADD03 blockade→「封鎖、通行遮断」)が、読点区切りの複数言い換えを含む場合、単独ナレーションとしてTTS→ASR往復検証で安定して認識されない(6回とも別の同音異義語へ誤認識)。ナレーション用テキストのみ、実績のある単一語(「海上封鎖」等)へ手動で差し替えて回避した。Canonicalizationの正式出力(`keywords_canonicalized.json`)自体は変更していない | `TBD` | 品質パターン・未一般化 | Non-blocking(個別記事で回避済み) | 「ナレーション表示用グロス」と「Canonicalization正式グロス」を分離するフィールドを設けるか、Canonicalizationのプロンプト側で「単独音声ナレーションとして自然な1つの言い換え」を優先する指示を追加するか、量産時に同種の事象が増えた段階で検討する(今回は個別記事での手動回避に留め、方式自体は変更しない) |

## Cross-level(A2/B1/B2共通)候補 — ER-003-CROSSLEVEL-AUDIO-01/02

以下はA2-AUDIO-01のユーザー試聴Feedbackから抽出した、**A2固有ではなく
番組全体(A2/B1/B2)に共通する編集・音声品質の候補**。ER-003-CROSSLEVEL-
AUDIO-02でA01・ADD03のA2音声プロトタイプにも同一原則を適用し、3記事目
までの再現性を確認した(記事ごとの文言・数値は個別、原則・数値定数は
共通)。B1/B2の既存完成音声は一括再生成していない。いずれも
`DECIDED`ではなく、ユーザーが[ER-003-CROSSLEVEL-AUDIO-01_REPORT.md](ER-003-CROSSLEVEL-AUDIO-01_REPORT.md)・
[ER-003-CROSSLEVEL-AUDIO-02_REPORT.md](ER-003-CROSSLEVEL-AUDIO-02_REPORT.md)
の試聴版(A01/A02/ADD03の3記事分)を確認した後に採否を判断する。

| ID | 内容 | 状態 | 種類 | Blocking | 次Action |
|---|---|---|---|---|---|
| OPEN-23 | Preview共通原則: 後続本文で聞かせたい具体的な答え・詳細な数字・結論・重要な転換点を、Previewで先に日本語で全部言わない。ニュースの全体テーマ・問題意識・聞く価値を示すことに限定する | `CANDIDATE / USER_DIRECTION_CONFIRMED` | 編集原則候補(A2/B1/B2共通) | Non-blocking | A01・ADD03でも同原則で新Previewを再設計し、旧Previewとの重複解消を確認済み(3記事で再現)。ユーザーが3記事分を試聴し、原則としてDECIDEDへ昇格するか判断する。昇格した場合も既存B1/B2完成記事のPreviewは自動的に差し替えず、今後の新規生成時から適用する |
| OPEN-24 | Key Phrase語末音素品質: 自然さを保ったまま、語末の子音・音素が脱落せず単語として知覚できる品質を求める(例: "feed"の語末/d/)。TTS instructionでの改善余地、trim安全マージンの影響、ASR/forced alignmentによる量産時の機械検出可能性を調査中 | `UNDER_INVESTIGATION` | 音声品質候補(A2/B1/B2共通) | Non-blocking | A01・ADD03の語末が停止音/摩擦音で終わるKey Phrase計7件(A01の4件+ADD03の3件)にも同一instructionを適用し、7件中7件で末尾エネルギー波形上の二次ピークを確認(A02の1件と合わせ計8件で再現性を確認)。それでも改善の知覚は未確認、ASRベースの機械検出も引き続き検知不能(調査結果は両REPORT参照)。forced alignment(MFA)による音素長・音素レベルQAは将来候補として記録するが、今回は実装しない |
| OPEN-25 | 「ポイント解説」後のポーズを現行0.5秒から+0.2秒(0.7秒)へ。現状、この値はB1組立スクリプト(`er003_v1_repro01_main_generate.py`等)ごとにハードコードされており、共通定数として一元化されていない。ER-003-CROSSLEVEL-AUDIO-03で追加提案: Point One→Point Two、In One Line→Outroのポーズも0.5秒→0.8秒(+0.3秒)へ | `CANDIDATE / TO_BE_LISTENED` | 番組テンポ候補(A2/B1/B2共通) | Non-blocking | A01・ADD03でも0.7秒を適用(3記事で再現)。Point One→Two・In One Line→Outroの0.8秒案は次回assemble候補として記録のみ(今回未反映)。ユーザーが試聴し採否判断。採用時も既存B1/B2完成音声は一括再生成せず、値の一元化(共通定数化)は別途検討する |
| OPEN-26 | Outro音楽レベルを、人間聴覚上「現状の約4/5(80%)」程度に下げる。単純な振幅0.8倍ではなく、心理音響の経験則(10dBの増減で知覚音量が倍/半分)に基づき約-3.2dB(振幅×0.693)を追加減衰する候補で試作済み。ER-003-CROSSLEVEL-AUDIO-03で追加提案: v2版からさらに同じ考え方で約0.8倍(Introから見た複合比率0.64、約-6.44dB、振幅×0.4765)を試作 | `CANDIDATE / TO_BE_LISTENED` | 音量候補(A2/B1/B2共通) | Non-blocking | A01・ADD03でも同一係数を適用(3記事で再現)。v3(さらに減衰)候補をArtifactで比較試聴可能([ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md)参照)。既存B1/B2完成音声のOutroは差し替えていない |
| OPEN-29 | Key Phraseのcontextual prosody品質: 音素は正しく読めていても、フレーズ単体では意味に合わない強勢・イントネーションになることがある(例: A01 "Come on"/"Go ahead"が命令・許可の口語義に聞こえる)。ER-003-CROSSLEVEL-AUDIO-04で判明: 現行採用中のGo ahead試作は語末音素対策(trial-clarity)のみで、意味prosody対策(context-aware)は一度も併用されていなかった。両方+フレーズ一体感を統合した新instructionを試作(Come on/Go ahead/Brent crude oil) | `UNDER_INVESTIGATION` | 音声品質候補(A2/B1/B2共通、Key Phraseを持つ全レベル) | Non-blocking | 既存の語末音素QA(segmental accuracy)とは独立した軸(contextual prosody)として管理する。ユーザーが[比較Artifact](https://claude.ai/code/artifact/53c4897d-c77c-49a4-973e-c59087619d05)を試聴し改善を確認できるか判断 |
| OPEN-30 | 英語見出し(In One Line等)の発話安定性。**2026-08-10訂正**: 前回(AUDIO-03)は「見出しを発話しないよう抑制する」ことを解決策として記録していたが誤り。In One Lineは読み上げるべき見出しであり、問題は「発話したこと」ではなく「見出しテキスト自体を本文に含めずに生成していたため発話が不安定だったこと」(A01/A02では省略、ADD03では日本語風の幻覚発話)。Point One/Twoと同じく見出しテキストを実際に本文へ含める方式へ修正し、3/3で安定した正しい発話("In one line.")を確認した(B1の実音声と同じ発話) | `CANDIDATE / TO_BE_LISTENED` | 音声品質候補(A2/B1/B2共通、segment単位生成の全箇所) | Non-blocking | `ER-003-LANGUAGE-ROUTING`として管理。language routing誤りでもinstruction抑制でもなく、見出しテキストをsegment本文へ含めるかどうかの問題と判明。ユーザーが[修正版](https://claude.ai/code/artifact/53c4897d-c77c-49a4-973e-c59087619d05)を試聴し採否判断。共有凍結モジュール(`er002_common.py`)は変更せず、呼び出し側のテキスト構成のみで対応する方針。他の英語見出し(Now, the full story.等)への一般適用は今後検討 |
| OPEN-31 | A2英文のnaturalness: A2化(短文化・spoken-first等)の結果、文法的には正しいが英語として非慣用的/やや不自然な表現が一部残っている(例: A01 "sent the ball across the front of goal"、ADD03のBrent原油価格段落の時系列flashback構造)。3記事監査でSHOULD_REVISE5件・OPTIONAL6件を検出。ER-003-CROSSLEVEL-AUDIO-04で、生成とQAを分離したPASS/REVISE/HUMAN_REVIEWフローの設計案を記録(実装はまだ) | `UNDER_REVIEW` | 品質候補(A2固有) | Non-blocking | `ER-003-A2-SCRIPT-QA`として管理。詳細一覧は[ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md)11-12節、量産フロー設計案は[ER-003-CROSSLEVEL-AUDIO-04_REPORT.md](ER-003-CROSSLEVEL-AUDIO-04_REPORT.md)6節参照。本文へは未反映、ユーザー判断待ち |
| OPEN-32 | A2英語音声の読み上げ速度: 明示的なspeed parameter・post-processing time-stretchはB1/B2/A2いずれも未実装(既存監査ER-003-A2-00で確認済み)。**2026-08-10更新**: 前回の「A2平均150 vs B1平均137」は記事構成差を含む粗い比較だったため、B1本編音声をnotification2挿入位置マーカーでFull Story/Points/In One Lineへ分割し同一条件で再測定した。結果は記事依存(A02はA2が明確に速い、ADD03はほぼ同じ)。In One Lineのみ2記事ともA2が明確に速い。A2 target案として約125〜130 WPM(B1平均約141の89〜92%)を提案、ただし音声試作は次回 | `UNDER_INVESTIGATION` | 速度候補(A2固有、B1/B2は現状維持で確定) | Non-blocking | `ER-003-A2-SPEED`として管理。次の一手はtarget WPM(125〜130)に向けたより弱い減速instructionの再試作、またはpitchを保持する高品質time-stretchとの比較。`levels.py`(別の無関係なレガシー番組の設定、wpm105-115)を誤って参照しないよう引き続き注意 |

## 参照元

[CURRENT_SPEC.md](CURRENT_SPEC.md)、[DECISION_LOG.md](DECISION_LOG.md)、
[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)、
[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)
