# OPEN_ITEMS — 未確定事項・技術的負債

**管理ID: ER-PM-001**
**最終更新: 2026-08-21(ER-005-AUDIO-ROBUSTNESS-SPEC-FIX-01、OPEN-05・OPEN-06を更新)**

検討中・候補・未確定仕様・技術的負債を記録する。確定済み仕様は書かない
(→[CURRENT_SPEC.md](CURRENT_SPEC.md))。

| ID | 内容 | 状態 | 種類 | Blocking | 次Action |
|---|---|---|---|---|---|
| OPEN-01 | ~~CEFR-A2の正式仕様が一切存在しない~~ | `DECIDED / CLOSED`(2026-08-12) | 仕様未決→解消 | 対応不要 | ER-003-A2-SPEC-FREEZE-01でA2の言語・構造・音声仕様一式を[CURRENT_SPEC.md](CURRENT_SPEC.md)へ正式反映済み。語彙は数値wordlistを設けない方針も含め`DECIDED` |
| OPEN-17 | [訂正・ER-003-A2-STRUCT-02] A2超一般語を記事全体で最大5語に制限する仕様 | `REJECTED / NO_FURTHER_ACTION` | 検証結果・却下 | Non-blocking(対応不要) | 対応不要。正式CEFR-A2 wordlist不在によりLLM判定基準が安定しない、厳密な上限達成には生成→QA→再生成の反復が必要で量産フローを不必要に複雑化する、複雑化に見合うリスニング難易度改善効果が確認できなかった、との理由でユーザーが不採用と判断(詳細は[DECISION_LOG.md](DECISION_LOG.md))。「A2として可能な範囲で平易な語を優先する」という原則(数値上限なし)は[A2_PROTOTYPE_SPEC.md](A2_PROTOTYPE_SPEC.md)に維持 |
| OPEN-19 | [ER-003-A2-STRUCT-02] 抽象語を「誰が何をしたか」という具体的行動表現へ優先的に変換する一般ルール | `REJECTED_AS_GENERAL_RULE` | 検証結果・却下 | Non-blocking(対応不要) | 対応不要。具体化で分かりやすくなるケースはあったが、無理な変換で意味関係が見えにくくなる・説明が長くなるケースもあり、「抽象=悪、具体=良」という一方向ルールにはしないとユーザーが判断。記事・文脈ごとに自然な方を選ぶ通常の編集判断へ委ねる |
| OPEN-20 | [ER-003-A2-STRUCT-02] 固有名詞のtoken数・密度を意図的に下げる一般ルール | `REJECTED / NO_FURTHER_ACTION` | 検証結果・却下 | Non-blocking(対応不要) | 対応不要。A01では固有名詞が減った一方、ADD03ではTrumpを明示的主語にした結果増加し、「誰が何をしたかを明確にする」「referentを明確にする」「spoken-firstにする」という別の分かりやすさ要求と競合することが判明。数量目標・密度目標は設けず、記事理解上の必要性で通常の編集判断により決める |
| OPEN-18 | [訂正・ER-003-A2-STRUCT-02] ER-003-A2-03の1文1数字ルールで、ADD03の日付"July 13, 2026"が2つの数字として検出されていた件 | `DECIDED`(原則整理のみ、checker実装は未着手) | 仕様の曖昧点・整理済み | Non-blocking | 対応不要(原則面)。「月+日+年」の日付表記は年齢範囲・スコア・時間帯と同様に1つの日付情報として扱う方針が確定した([DECISION_LOG.md](DECISION_LOG.md))。`er003_a2_article.py`の`_EXEMPT_NUMBER_PATTERNS`への正規表現追加は、今回のスコープでは実施しない(必要になった時点で対応) |
| OPEN-02 | ~~A2の生成元が矛盾~~ | `DECIDED / CLOSED`(2026-08-12) | 仕様矛盾→解消 | 対応不要 | Natural English Sourceからの独立生成は、当時(P-series、2026-08-12時点)のDecisionであり恒久方針ではない。N3-01以降はVerified Fact Ledgerからのdirect generation方式へ移行済み([CURRENT_SPEC.md](CURRENT_SPEC.md)、[DECISION_LOG.md](DECISION_LOG.md)の`ER-003-A2-B1-N3-01`系Decision参照) |
| OPEN-13 | ~~ER-003-A2-STRUCT-01 Candidate A(11パート構造)~~ | `DECIDED / CLOSED`(2026-08-12) | 構造支援候補→正式採用 | 対応不要 | 11パート構造・Comment役割・Full Story分割優先順位を[CURRENT_SPEC.md](CURRENT_SPEC.md)へ正式反映。A02はER-003-A2-AUDIO-AB-01でユーザー試聴・承認済み。A01/ADD03は音声プロトタイプ完成済みだが、最新Cross-level仕様の反映(→OPEN-34)が必要 |
| OPEN-21 | ~~ER-003-A2-AUDIO-01のASR数字表記ゆれ2箇所~~ | `DECIDED / CLOSED`(2026-08-12) | 要ユーザー試聴確認→解消 | 対応不要 | 同じ内容を含むA02完成候補をER-003-A2-AUDIO-AB-01でユーザーが試聴し「全体としてOK」と承認。TTS内容は正常と確定 |
| OPEN-22 | 共有診断関数`er003_b1_p4_audio.get_full_text_via_azure_stt_continuous`のデフォルト`timeout_seconds=90.0`が、長尺音声(5分超)では不十分で、timeout時にエラーを返さず部分結果を正常として返してしまう制限を確認。呼び出し側で`timeout_seconds`を大きく指定することで回避したが、関数自体の挙動は未修正 | `TBD` | 技術的負債 | Non-blocking(呼び出し側で回避済み) | 同種の長尺音声を診断する機会が今後増えた場合、関数側のtimeout処理(タイムアウトと正常終了を明確に区別する)を修正するか検討する。今回は共有モジュールを変更していない |
| OPEN-14 | ER-003-A2-STRUCT-01: Full Story前の簡易Listening Questions(2問程度) | `CANDIDATE / NOT_ADOPTED` | 構造支援候補 | Non-blocking | 同上 |
| OPEN-15 | [訂正・ER-003-A2-02] B1承認済みKey Phraseの語そのものがA2本文に残るかは要件にしない。A2 Key PhraseはA2本文確定後に本文から改めて選定する(方針確定) | `DECIDED` | 方針整理 | Non-blocking | 対応不要。当初「B1 Key Phrase語の消失」を問題視していたが、これは誤った懸念設定だったと整理した。実際の問題は主要fact自体がFull StoryからPointsへ流出していたことであり、これはER-003-A2-02で解消(下記OPEN-16参照) |
| OPEN-16 | ~~A2-01でFull Storyの情報比重が崩れていた件~~ | `DECIDED / CLOSED`(2026-08-12) | 検証結果→CURRENT_SPEC反映済み | 対応不要 | 「Full Storyだけでニュースの核心が分かる」原則として[CURRENT_SPEC.md](CURRENT_SPEC.md)へ正式反映済み |
| OPEN-03 | CEFR-B2の音声化(Preview/Key Phrase/Full Story/Podcast組み立て)が一度も実施されていない | `TBD`(2026-08-17: B2は`LAUNCH_SCOPE: OUT_OF_INITIAL_SCOPE`のため、初期Launchの必須事項ではないことが確定。ER-003-B1-B2-SCOPE-FIX-01参照) | 未着手 | Non-blocking(初期Launch対象外のため、A2/B1のLaunchには影響しない) | External Pilot・Product Strategyを経て、B2をLaunch対象へ再追加するかを判断してから着手する(下記OPEN-42参照) |
| OPEN-04 | `used_form`/`key_phrase`の100%重複 | `DECIDED`(整理しない方針は確定済み) | 技術的負債 | Non-blocking | 実際に分ける必要が生じるまで対応しない(意図的放置) |
| OPEN-05 | 短文TTS hallucination・`INVALID_ARGUMENT`の根本原因(モデル側の挙動)が未解明。**2026-08-21更新**: ER-005-AUDIO-VALIDATION-ROBUSTNESS-02で、style instruction(読み上げ対象外の話し方指示)をTTSモデルが読み上げ対象の本文と混同する「instruction leakage」が強く疑われる状況証拠を得た(hallucination音声がstyle instruction文面をほぼ逐語的に含んでいた実例を確認)。緩和策としてStructured Separation(instructionとtextを明示的delimiterで分離、`ER-005-AUDIO-INSTRUCTION-SEPARATION-01`)をProduction Baselineとして採用し、Controlled Testで技術的失敗率9/18→0/18の改善を確認した。**ただし、これはproviderの内部挙動に対する緩和策であり、Geminiモデル側の確定的な誘発条件そのものは未解明のまま**。「完全解決」ではなく「現時点で最も安定したBaselineの採用」という位置づけで、本項目は`UNDER_REVIEW`のまま維持する(Structured Separation採用後もinstruction leakageが再発しないか、今後の量産で監視を続ける) | `UNDER_REVIEW`(provider behavior監視継続。Production blockerではない) | 技術的負債・provider挙動 | Non-blocking(Structured Separation採用+strict検証+fallbackで運用上は緩和済み) | Structured Separation採用後の量産で再発有無を監視する。Gemini側の公式仕様・ドキュメントに変化があれば再評価する(`system_instruction`フィールドの正式TTS対応等) |
| OPEN-06 | ASR homophone ambiguityを機械的に判別する手段が未実装(同音異義語リスト等)。**2026-08-21更新**: ER-005-AUDIO-VALIDATION-ROBUSTNESS-02/ER-005-AUDIO-ROBUSTNESS-SPEC-FIX-01で、短い日本語segment(Key Phrase・gloss等)向けに、個別語のリストに依存しない一般的な発音(読み)ベースのValidation(`PHONETIC_MATCH`、`ER-005-JA-SHORT-ASR-PHONETIC-01`)をProductionへ実装・反映した。既知の同音異義語ケース(内向化/内効果、鏡像/京三等)に加え、fixture外の未知データでも正しく機能することを確認済み。**対象は短いsegment(30文字以下)のみ**であり、長文Narration全体の同音異義語判別は依然として未対応 | `DECIDED`(短いsegment向けの一般的な発音ベース判定として実装済み。長文Narrationは対象外のまま`TBD`) | 技術的負債→大部分解消 | Non-blocking | 長文Narrationへの同種の判別が必要になった場合は、別途スコープを切って検討する(今回のPHONETIC_MATCHは長文への無条件適用を明示的に禁止している) |
| OPEN-07 | 正式なLUFS masteringが未導入(現状はscalar RMS基準の簡易調整のみ) | `TBD` | 技術的負債 | Non-blocking | 音質改善の必要が生じた際に検討 |
| OPEN-08 | ADD03初回Full Story生成(1回目3試行不合格分)の詳細ログが失われている(`stage_a_generate_body_audio`のバグ、2回目実行分からは修正済み) | `HISTORICAL`(バグ自体は修正済み) | 記録欠落 | Non-blocking | 再発防止は完了。過去分の復元は行わない |
| OPEN-09 | Dynamics3不使用の決定について、比較検討の詳細記録(なぜscalar RMSを選んだかの根拠レポート)が見当たらない | `TBD` | 記録欠落 | Non-blocking | 発見時に追記。現時点では推測で埋めない |
| OPEN-10 | A01(CEFR-B1)の「エピソード全体の最終承認」が未取得(`publication_status: NOT_APPROVED`のまま) | `UNDER_REVIEW` | 公開判断待ち | Non-blocking(A02・ADD03の作業には影響しない) | ユーザーがA01最終版(r2)を通しで試聴し、公開可否を判断 |
| OPEN-11 | A02・ADD03も`user_quality_status: PASS`だが`publication_status`は`NOT_APPROVED`のまま(品質OKと公開承認は別判断) | `UNDER_REVIEW` | 公開判断待ち | Non-blocking | ユーザーが公開判断を行うタイミングで確定 |
| OPEN-12 | `ER-003-B1_HANDOFF.md`が旧運用のまま(仕様・経緯を大量に含む29KB超のファイル)で、新ルール(直近作業再開専用)に未準拠 | `TBD` | 運用移行未完了 | Non-blocking | 次回以降の更新時に新フォーマットへ段階的に移行(今回は大規模書き換えを行わない) |
| OPEN-27 | ER-003-CROSSLEVEL-AUDIO-02で発見: `scripts/run_ci_tests.py`(公式CI回帰テストランナー、`ci_test_manifest.json`によるinclude/exclude明示登録方式)が、リポジトリ直下の6ファイル(`er003_test_b1_p7a_audio.py`/`er003_test_b1_p7c_audio.py`/`er003_test_b1_p8a_audio.py`/`er003_test_b1_p9a_audio.py`/`er003_test_b1_p9a_r1_audio.py`/`er003_test_key_words_canonicalization.py`)が`ci_test_manifest.json`のinclude/excludeに未登録であるためmanifest検証エラーで起動できない状態だった(いずれも本セッションで新規作成したファイルではなく、既存commit時点から未登録)。**2026-08-17 SoT Consistency Cleanupで再確認: 6ファイルは依然としてinclude/exclude双方に未登録のまま(`ci_test_manifest.json`直接確認)であり、本項目は未解消**。**用語の区別に注意**: ER-003-N3-ROOT-FIX-01以降のDECISION_LOG/完了報告で言及している「回帰テスト1711/1711 PASS」等の実績は、`scripts/run_ci_tests.py`(本項目が指す公式CIランナー)ではなく、**別ツールの`run_project_regression.py`(`er0*_test_*.py`グロブパターンによる自動探索方式、manifestを参照しない)による結果**。したがって「1711/1711 PASS」の実績は、本OPEN-27が指す公式CIランナーのBlocking状態を解消するものではない | `TBD` | 技術的負債・CI回帰不能 | Blocking(公式CIランナー`scripts/run_ci_tests.py`での全体回帰テストが実行不能。ただし`run_project_regression.py`という別ツールでの回帰テスト実行は可能で、実際に本セッションでも複数回使用し全件PASSしている) | 6ファイルを`ci_test_manifest.json`のinclude(またはexclude)へ登録する必要がある。本ステージでは原因調査のみ行い、manifestは変更していない(共有CI設定の無断変更を避けるため)。今回は代替として該当モジュールの個別`unittest`実行とpy_compileでの構文確認のみ実施(詳細は[ER-003-CROSSLEVEL-AUDIO-02_REPORT.md](ER-003-CROSSLEVEL-AUDIO-02_REPORT.md)参照)。以降のタスクで頻繁に使われている`run_project_regression.py`も、正式なCI運用として`scripts/run_ci_tests.py`の代替に位置づけてよいかは未確定 |
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
| OPEN-31 | ~~A2英文のnaturalness(SHOULD_REVISE5件)~~ | `DECIDED / CLOSED`(2026-08-12) | 品質候補→台本確定済み | 対応不要 | ER-003-A2-SCRIPT-FINAL-01で5件すべてを最終台本(`er003_output/a2_p1_r3/{article}/a2_article_raw.md`および各`ER-003-A2-STRUCT-0X_{article}_INTEGRATED_SCRIPT.md`)へ反映し、6観点Naturalness QA(3記事ともPASS)を実施済み。内訳: **A01**(3件)— (1)"Rogers sent the ball across the front of goal."→"Rogers crossed the ball into the box."(採用済み) (2)"Messi sent the ball across goal from the right."→"Messi crossed the ball from the right."(採用済み) (3)"The referee then added more time."→"The game went into added time."(採用済み)。**A02**(1件)— "apps under the plan would not open at first"→"apps under the plan would be switched off by default"(採用済み。Natural English Sourceの"covered apps would be unavailable by default"と意味一致を確認した上で採用)。**ADD03**(1件)— Brent原油価格段落を7/13→7/14の実時系列順へ再構成(採用済み、新規事実の追加なし)。詳細は[ER-003-A2-SCRIPT-FINAL-01_REPORT.md](ER-003-A2-SCRIPT-FINAL-01_REPORT.md)、決定理由は[DECISION_LOG.md](DECISION_LOG.md)。音声への反映は下記OPEN-35を参照 |
| OPEN-34 | A01・ADD03のA2完成音声が、CURRENT_SPECへ正式反映済みのCross-level最新仕様(Pause 0.8秒・Outro最新減衰・Key Phrase 3条件発音・In One Line見出し修正・約135 WPM速度目安)を反映していない(ER-003-CROSSLEVEL-AUDIO-02時点のバージョンのまま) | `TBD` | 再assemble待ち | Non-blocking | 次回A01/ADD03のA2音声assemble時に、CURRENT_SPECの最新仕様一式を反映する。あわせて下記OPEN-35(台本確定によるscript変更)・Key Phrase 3条件発音方式(A01: Come on/Go ahead等)も反映する |
| OPEN-35 | ER-003-A2-SCRIPT-FINAL-01(2026-08-12)でA01・A02・ADD03のA2台本本文(OPEN-31の5件)を確定・変更したが、**3記事とも音声は未再生成**。既存の完成音声(A01/ADD03=`crosslevel_audio_02`、A02=`a2_audio_ab_01`)は旧台本の内容のまま。**ユーザーDecision(2026-08-12): 音声最新化は実施する方針で確定済みだが、夜間にまとめて処理したいため、日中は意図的に保留中。** | `TBD` | 再assemble待ち(script変更、意図的保留中) | Non-blocking(次回各記事のA2音声assemble前に反映要) | 次回A01/A02/ADD03のA2音声assemble時に、`er003_output/a2_p1_r3/{article}/a2_article_raw.md`の最新版(確定済み台本)から音声を再生成する。A01・ADD03は上記OPEN-34(Cross-level仕様反映)とあわせて1回のassembleで両方を反映するのが効率的。A02は既にCross-level最新仕様を反映済み(ER-003-A2-AUDIO-AB-01)のため、台本変更分のみの差分再生成で足りる可能性が高い。夜間バッチ実行のタイミングはユーザー指示待ち |

## B1/A2 SPEC-FREEZE以降の既知の限界・継続監視事項(ER-003-B1-A2-SPEC-FREEZE-01、2026-08-17)

仕様Freezeは「未決事項が消えた」ことを意味しない。以下は正式仕様化した
上でなお残る既知の限界・継続監視事項として明示的に残す。

| ID | 内容 | 状態 | 種類 | Blocking | 次Action |
|---|---|---|---|---|---|
| OPEN-36 | External User Validation: B1(Support-based Natural English)・A2(Core Logic Preservation含む)とも、生成→Fact QA→機械QA(ASR/波形解析等)までは完了している。**用語の区別に注意**: [PROJECT_INDEX.md](PROJECT_INDEX.md)の定義上「ユーザー」はプロジェクト責任者(本プロジェクトのオーナー)を指し、「実際の学習者ユーザー」(番組の想定視聴者)とは別人格。N3-01の3ジャンルについては、[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)の`user_quality_status`が3記事とも`NOT_REVIEWED`のままであり、**プロジェクト責任者自身による通し試聴もまだ記録されていない**(開発側の機械QA・波形解析等の技術的検証のみ完了)。そのため「実際の学習者でB1/A2体験が成立するか」というExternal User Validationは、プロジェクト責任者自身の試聴より前段階の、さらに先の未検証事項である | `TBD` | 外部検証待ち | Non-blocking(機械QAは完了、プロジェクト責任者試聴・External Pilotは別途) | まずプロジェクト責任者によるN3-01音声の試聴・`user_quality_status`更新を行い、その後にExternal Pilotのタイミング・設計を判断する |
| OPEN-37 | ~~B1のNews本文がB2と完全同一テキストを共有するかは`NEEDS_CONFIRMATION`~~ | `DECIDED / CLOSED`(2026-08-17、ER-003-B1-B2-SCOPE-FIX-01) | 仕様未決→解消 | 対応不要 | B1はB2と同一テキストを共有せず、Verified Fact LedgerからB1専用Writerで独立生成する、とユーザーDecisionで確定([DECISION_LOG.md](DECISION_LOG.md) Decision A、[CURRENT_SPEC.md](CURRENT_SPEC.md)「B1(独立生成Natural Spoken News English)」節)。実際の学習者がB1本文+Supportを理解できるかというExternal Pilot確認自体は、引き続き未実施(→OPEN-36) |
| OPEN-38 | 短いJapanese phraseへのminimal instruction fallback(ER-003-N3-ROOT-FIX-01)は、標準経路が不合格を繰り返す短いKey Phrase等で追加のTTS/ASR呼び出しを発生させる。実測では1トライアルあたり1〜5回のfallback呼び出しが必要だった。頻繁にfallbackが発生する場合、標準経路(短いフレーズへ長いstyle instructionをそのまま使う設計)自体の見直し余地がある | `UNDER_REVIEW` | 技術的負債・監視事項 | Non-blocking(fallbackで運用上は吸収済み) | 今後の記事生成でfallback発生率を継続観察し、頻発するようなら標準経路の指示設計そのものを見直す |
| OPEN-39 | A2 Core Explanatory Logic Preservation(ER-003-N3-ROOT-FIX-01)は、Householdで実際に見つかった「conceptual oversimplification」(正しい判断軸を誤った近似ルールへ置換する)という失敗パターンへの発生源対策。3ジャンルでの単発検証では有効性を確認したが、今後さらに記事数・ジャンルが増えた際に同種の問題が別の形で再発しないかは継続監視が必要。Fact Checker/Ledger Deviation Checkは文単位の正確性を見るのみで、記事全体の判断軸一致までは検証していないことに変わりはない(クロスレベル一貫性チェックは今回意図的に未導入) | `UNDER_REVIEW` | 品質パターン・監視事項 | Non-blocking | 今後の新規記事(N4以降)でHousehold型の失敗パターンが再発しないか、生成のたびに確認する。頻発する場合はクロスレベル一貫性チェック(ER-003-N3-ROOT-FIX-01検討時に却下したOption B)の追加を再検討する |
| OPEN-40 | `er003_audio_tts_asr_safety.py`(TTS/ASR共通安全部品)は、ER-003-A2-B1-N3-01/FIX-01で新規発見・実装したnormalization処理(curly quote正規化、Markdown太字除去、数字表記ゆれ吸収、Key Phrase複合語対応、日本語数字表記ゆれ等)の一部を含んでいない。これらは現状N3専用スクリプト(`er003_v1_n3_01_tts_generate.py`)内にとどまっており、**Production共通モジュールへは未統合** | `TBD` | 実装統合未完了 | Non-blocking(N3記事では個別スクリプト内で機能している) | 今後同種のnormalizationが必要な記事が増えた段階で、共通モジュールへの統合を検討する。先回りでの統合作業は今回のスコープに含めない |
| OPEN-41 | Household A2の本番article.md(`er003_output/n3_01/household/a2/article.md`)は、ER-003-A2-B1-N3-01-FIX-01時点の手動編集版のままであり、ER-003-N3-ROOT-FIX-01で正式採用したA2_KAI1_INSTRUCTION(Core Logic Preservation原則入り)で再生成したものではない。内容の方向性(ethylene/moisture軸を維持)は一致しているが、生成経路が異なる。**訂正(2026-08-17)**: 本番article.mdのFact Checker状態は`PASS`ではなく`REVIEW_REQUIRED`(Point Two周辺の精度指摘、記録の上で許容判断済み。→[ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md)) | `TBD` | 本番成果物と仕様の不一致 | Non-blocking(Ledger Deviation CheckはLEDGER_COMPLIANT。Fact CheckerはREVIEW_REQUIREDだが今回の修正対象外の精度指摘のみ) | 将来Household記事の音声・記事を更新する機会があれば、正式採用済みのA2_KAI1_INSTRUCTIONで再生成することを検討する。今回のFreezeでは強制しない |
| OPEN-42 | B2は2026-08-17付で`LAUNCH_SCOPE: OUT_OF_INITIAL_SCOPE`となった(ER-003-B1-B2-SCOPE-FIX-01 Decision B)。廃止ではなく将来拡張候補として保持している | `TBD` | Product Strategy待ち | Non-blocking | B2を将来のLaunch対象へ再追加するかは、External Pilot(A2/B1)の結果とProduct Strategyの判断を経てから検討する。現時点で着手・優先度付けは行わない |
| OPEN-43 | ER-005-COST-BASELINE-01のAKB48 A2テーマで、Key Phrase音声10本(英語5+日本語5)全てが、標準経路(6回)・fallback経路(6回)とも全attemptでAzure ASRの文字起こしが空文字列を返し、STOPPEDとなった(ER-005-TTS-CLEAN-COST-AUDIT-01で発見)。同記事の他segmentで見られたhomophone系の誤認識(非空だが不一致な文字起こし)とは異なる失敗signatureであり、TTS自体は音声を生成できている(output tokenが計測されている)。Azure側のクォータ/レート制限的な問題か、Key Phraseのような短い音声(1〜2秒)に対するリアルタイムASRの認識信頼性の限界かは、既存ログ(Azureの詳細エラーコードを含まない)からは確定できない | `UNDER_REVIEW`(原因未確定) | 未解決の障害・原因調査待ち | Non-blocking(該当記事はCost計測目的であり本番公開対象ではない。ただし本番でKey Phraseのような短い音声に同種の問題が起きる場合はUser体験に影響しうる) | Azure側の詳細エラーログ取得方法の確認、または短い音声clipに対するASR検証方式の再現実験により原因を切り分ける。原因確定まではCLOSEDにしない |

## 参照元

[CURRENT_SPEC.md](CURRENT_SPEC.md)、[DECISION_LOG.md](DECISION_LOG.md)、
[ER-003-A2-00_SPEC_AUDIT.md](ER-003-A2-00_SPEC_AUDIT.md)、
[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)
