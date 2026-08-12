# OPEN_ITEMS — 未確定事項・技術的負債

**管理ID: ER-PM-001**
**最終更新: 2026-08-12(ER-003-A2-SPEC-FREEZE-01反映)**

検討中・候補・未確定仕様・技術的負債を記録する。確定済み仕様は書かない
(→[CURRENT_SPEC.md](CURRENT_SPEC.md))。

| ID | 内容 | 状態 | 種類 | Blocking | 次Action |
|---|---|---|---|---|---|
| OPEN-01 | ~~CEFR-A2の正式仕様が一切存在しない~~ | `DECIDED / CLOSED`(2026-08-12) | 仕様未決→解消 | 対応不要 | ER-003-A2-SPEC-FREEZE-01でA2の言語・構造・音声仕様一式を[CURRENT_SPEC.md](CURRENT_SPEC.md)へ正式反映済み。語彙は数値wordlistを設けない方針も含め`DECIDED` |
| OPEN-17 | [訂正・ER-003-A2-STRUCT-02] A2超一般語を記事全体で最大5語に制限する仕様 | `REJECTED / NO_FURTHER_ACTION` | 検証結果・却下 | Non-blocking(対応不要) | 対応不要。正式CEFR-A2 wordlist不在によりLLM判定基準が安定しない、厳密な上限達成には生成→QA→再生成の反復が必要で量産フローを不必要に複雑化する、複雑化に見合うリスニング難易度改善効果が確認できなかった、との理由でユーザーが不採用と判断(詳細は[DECISION_LOG.md](DECISION_LOG.md))。「A2として可能な範囲で平易な語を優先する」という原則(数値上限なし)は[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)に維持 |
| OPEN-19 | [ER-003-A2-STRUCT-02] 抽象語を「誰が何をしたか」という具体的行動表現へ優先的に変換する一般ルール | `REJECTED_AS_GENERAL_RULE` | 検証結果・却下 | Non-blocking(対応不要) | 対応不要。具体化で分かりやすくなるケースはあったが、無理な変換で意味関係が見えにくくなる・説明が長くなるケースもあり、「抽象=悪、具体=良」という一方向ルールにはしないとユーザーが判断。記事・文脈ごとに自然な方を選ぶ通常の編集判断へ委ねる |
| OPEN-20 | [ER-003-A2-STRUCT-02] 固有名詞のtoken数・密度を意図的に下げる一般ルール | `REJECTED / NO_FURTHER_ACTION` | 検証結果・却下 | Non-blocking(対応不要) | 対応不要。A01では固有名詞が減った一方、ADD03ではTrumpを明示的主語にした結果増加し、「誰が何をしたかを明確にする」「referentを明確にする」「spoken-firstにする」という別の分かりやすさ要求と競合することが判明。数量目標・密度目標は設けず、記事理解上の必要性で通常の編集判断により決める |
| OPEN-18 | [訂正・ER-003-A2-STRUCT-02] ER-003-A2-03の1文1数字ルールで、ADD03の日付"July 13, 2026"が2つの数字として検出されていた件 | `DECIDED`(原則整理のみ、checker実装は未着手) | 仕様の曖昧点・整理済み | Non-blocking | 対応不要(原則面)。「月+日+年」の日付表記は年齢範囲・スコア・時間帯と同様に1つの日付情報として扱う方針が確定した([DECISION_LOG.md](DECISION_LOG.md))。`er003_a2_article.py`の`_EXEMPT_NUMBER_PATTERNS`への正規表現追加は、今回のスコープでは実施しない(必要になった時点で対応) |
| OPEN-02 | ~~A2の生成元が矛盾~~ | `DECIDED / CLOSED`(2026-08-12) | 仕様矛盾→解消 | 対応不要 | Natural English Sourceからの独立生成を恒久方針として確定([CURRENT_SPEC.md](CURRENT_SPEC.md)) |
| OPEN-13 | ~~ER-003-A2-STRUCT-01 Candidate A(11パート構造)~~ | `DECIDED / CLOSED`(2026-08-12) | 構造支援候補→正式採用 | 対応不要 | 11パート構造・Comment役割・Full Story分割優先順位を[CURRENT_SPEC.md](CURRENT_SPEC.md)へ正式反映。A02はER-003-A2-AUDIO-AB-01でユーザー試聴・承認済み。A01/ADD03は音声プロトタイプ完成済みだが、最新Cross-level仕様の反映(→OPEN-34)が必要 |
| OPEN-21 | ~~ER-003-A2-AUDIO-01のASR数字表記ゆれ2箇所~~ | `DECIDED / CLOSED`(2026-08-12) | 要ユーザー試聴確認→解消 | 対応不要 | 同じ内容を含むA02完成候補をER-003-A2-AUDIO-AB-01でユーザーが試聴し「全体としてOK」と承認。TTS内容は正常と確定 |
| OPEN-22 | 共有診断関数`er003_b1_p4_audio.get_full_text_via_azure_stt_continuous`のデフォルト`timeout_seconds=90.0`が、長尺音声(5分超)では不十分で、timeout時にエラーを返さず部分結果を正常として返してしまう制限を確認。呼び出し側で`timeout_seconds`を大きく指定することで回避したが、関数自体の挙動は未修正 | `TBD` | 技術的負債 | Non-blocking(呼び出し側で回避済み) | 同種の長尺音声を診断する機会が今後増えた場合、関数側のtimeout処理(タイムアウトと正常終了を明確に区別する)を修正するか検討する。今回は共有モジュールを変更していない |
| OPEN-14 | ER-003-A2-STRUCT-01: Full Story前の簡易Listening Questions(2問程度) | `CANDIDATE / NOT_ADOPTED` | 構造支援候補 | Non-blocking | 同上 |
| OPEN-15 | [訂正・ER-003-A2-02] B1承認済みKey Phraseの語そのものがA2本文に残るかは要件にしない。A2 Key PhraseはA2本文確定後に本文から改めて選定する(方針確定) | `DECIDED` | 方針整理 | Non-blocking | 対応不要。当初「B1 Key Phrase語の消失」を問題視していたが、これは誤った懸念設定だったと整理した。実際の問題は主要fact自体がFull StoryからPointsへ流出していたことであり、これはER-003-A2-02で解消(下記OPEN-16参照) |
| OPEN-16 | ~~A2-01でFull Storyの情報比重が崩れていた件~~ | `DECIDED / CLOSED`(2026-08-12) | 検証結果→CURRENT_SPEC反映済み | 対応不要 | 「Full Storyだけでニュースの核心が分かる」原則として[CURRENT_SPEC.md](CURRENT_SPEC.md)へ正式反映済み |
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

## Cross-level(A2/B1/B2共通)仕様 — ER-003-A2-SPEC-FREEZE-01でDECIDEDへ昇格

以下はA2の検証過程で発見・試作し、ER-003-A2-AUDIO-AB-01でのユーザー
試聴・承認を経て**2026-08-12付でDECIDEDへ昇格し[CURRENT_SPEC.md](CURRENT_SPEC.md)の
「Cross-level仕様」節へ正式反映済み**。B1/B2の既存完成音声は一括
再生成していない(今後の新規生成・再assemble時から適用)。

| 旧ID | 内容 | 昇格後の状態 |
|---|---|---|
| OPEN-23 | Preview共通原則(具体的な答え・数字・結論を先出ししない) | `DECIDED / CLOSED` |
| OPEN-24 | Key Phrase語末音素品質 | `DECIDED / CLOSED`(下記OPEN-29と統合し「発音品質3条件」として採用) |
| OPEN-25 | ポーズ(ポイント解説後0.7秒、Point One→Two・In One Line→Outro 0.8秒) | `DECIDED / CLOSED` |
| OPEN-26 | Outro音量の心理音響ベース減衰 | `DECIDED / CLOSED` |
| OPEN-29 | Key Phraseのcontextual prosody品質 | `DECIDED / CLOSED`(Meaning/Phoneme integrity/Phrase groupingの3条件として採用) |
| OPEN-30 | 英語見出し(In One Line等)の発話安定性 | `DECIDED / CLOSED`(見出しテキストを実際にTTS inputへ含める方式を採用) |
| OPEN-32 | A2英語音声の読み上げ速度 | `DECIDED`(約135 WPMを目安として採用。B1/B2は現状維持) |
| OPEN-33 | Key Phrase統合発音方式のA02への適用 | `DECIDED / CLOSED`(方式そのものがCross-level仕様として確定) |

**残る作業**(下記OPEN-34参照): A01・ADD03の完成音声はまだ
ER-003-CROSSLEVEL-AUDIO-02時点のバージョンのままで、上記の最新仕様
(Pause 0.8秒・Outro最新減衰・Key Phrase 3条件発音・In One Line見出し
修正・約135 WPM)を反映した再assembleが済んでいない。

| ID | 内容 | 状態 | 種類 | Blocking | 次Action |
|---|---|---|---|---|---|
| OPEN-31 | A2英文のnaturalness: A2化(短文化・spoken-first等)の結果、文法的には正しいが英語として非慣用的/やや不自然な表現が一部残っている(例: A01 "sent the ball across the front of goal"、ADD03のBrent原油価格段落の時系列flashback構造)。3記事監査でSHOULD_REVISE5件・OPTIONAL6件を検出。A01の"The referee then added more time."→"The game went into added time."のみ[DECISION_LOG.md](DECISION_LOG.md)で修正方針が確定、台本への反映は未実施。他4件のSHOULD_REVISEは未判断のまま。Naturalness QAフロー自体は`DECIDED`(方針)だが、大規模自動実装はまだ | `UNDER_REVIEW` | 品質候補(A2固有) | Non-blocking(次回A01完成音声assemble前に確認要) | 詳細一覧は[ER-003-CROSSLEVEL-AUDIO-03_REPORT.md](ER-003-CROSSLEVEL-AUDIO-03_REPORT.md)11-12節。次回A01/ADD03のassemble前に、added time修正の台本反映漏れがないか確認する。他のSHOULD_REVISE項目はユーザー判断待ち |
| OPEN-34 | A01・ADD03のA2完成音声が、CURRENT_SPECへ正式反映済みのCross-level最新仕様(Pause 0.8秒・Outro最新減衰・Key Phrase 3条件発音・In One Line見出し修正・約135 WPM速度目安)を反映していない(ER-003-CROSSLEVEL-AUDIO-02時点のバージョンのまま) | `TBD` | 再assemble待ち | Non-blocking | 次回A01/ADD03のA2音声assemble時に、CURRENT_SPECの最新仕様一式を反映する。あわせてOPEN-31のadded time修正・Key Phrase 3条件発音方式(A01: Come on/Go ahead等)も反映する |

## 参照元

[CURRENT_SPEC.md](CURRENT_SPEC.md)、[DECISION_LOG.md](DECISION_LOG.md)、
[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)、
[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)
