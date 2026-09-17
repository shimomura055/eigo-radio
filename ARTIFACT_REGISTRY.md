# ARTIFACT_REGISTRY — 記事×CEFRレベルの成果物完成状態

**管理ID: ER-PM-001**
**最終更新: 2026-08-17(ER-003-B1-B2-SCOPE-FIX-01、B2 Launch Scope注記追加)**

記事×CEFRレベルごとの成果物完成状態を一覧化する。値はすべて監査証拠
(commit・manifest・report)に基づく。**推測で埋めた値はない。** 不明な
場合は`NOT_REVIEWED`/`未着手`等、事実に基づく状態を記載する。

`user_quality_status`(試聴品質)と`publication_status`(公開承認)は
必ず分離する(詳細は[PROJECT_INDEX.md](PROJECT_INDEX.md)参照)。

**`PASS`の意味についての注意(2026-08-12追記、ER-003-A2-SCRIPT-FINAL-01で
更新)**: 表内の`PASS`は「現行採用版が該当QAゲート・ユーザー試聴を
通過した」ことを意味する。**Script列**は、ER-003-A2-SCRIPT-FINAL-01
(2026-08-12)でOPEN-31のSHOULD_REVISE候補5件をすべて最終台本へ反映し、
6観点Naturalness QAに合格したことを示す(OPEN-31は`DECIDED / CLOSED`)。
ただし**Podcast組立列**が示すとおり、既存の完成音声はこのscript確定
より前に生成されたものであり、**台本と音声の内容が一致していない**
(音声側は旧文言のまま、[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-35で
再assemble待ちとして追跡中)。
**User Quality列の`PASS**`(A02)は、ER-003-A2-AUDIO-AB-01での通し
試聴による総合判断("A2の完成候補は全体としてOK")を指すが、この判断は
**script確定前の旧音声**に対するものであり、文単位のNaturalness QA
網羅を保証するものでもない。

**B2行の注意(2026-08-17、ER-003-B1-B2-SCOPE-FIX-01)**: 以下のCEFR-B2行は
`LAUNCH_SCOPE: OUT_OF_INITIAL_SCOPE`(初期Launch対象外)。これは
`Publication`列(`NOT_APPROVED`)とは別軸の情報であり、「未承認だから
Launch対象外」ではなく「初期Launchの対象レベルとして選ばれていない」
ことを意味する。研究・比較参照用として成果物自体は削除していない。

| Article | Level | Source | Script | Preview | Key Phrase | Full Story | Podcast組立 | User Quality | Publication |
|---|---|---|---|---|---|---|---|---|---|
| A01 | CEFR-B2(`LAUNCH_SCOPE: OUT`) | PASS | PASS(自動QA合格。ユーザーによる本文単独の明示承認記録なし) | N/A | N/A | 未生成 | 未生成 | NOT_REVIEWED | NOT_APPROVED |
| A01 | CEFR-B1 | PASS | PASS | PASS | PASS(5件) | PASS | PASS(r2が最終版) | NOT_REVIEWED(部分的な「修正箇所承認」は複数あるが、最終r2版の通し試聴OKは未記録) | NOT_APPROVED |
| A01 | CEFR-A2 | PASS(A2-03独立生成) | **PASS**(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で最終台本確定。旧OPEN-31の3件すべて反映済み、6観点Naturalness QA PASS。[DECISION_LOG.md](DECISION_LOG.md)参照) | PROTOTYPE_BUILT(Cross-level原則反映、ただしPause 0.8秒・Outro最新減衰・Key Phrase 3条件発音・In One Line見出し修正は未反映のER-003-CROSSLEVEL-AUDIO-02版のまま) | PROTOTYPE_BUILT(方式L+Canonicalizationで新規選定5件、機械QA合格。3条件発音方式は未適用) | PROTOTYPE_BUILT(機械QA合格、hallucinationなし) | PROTOTYPE_BUILT(294.2秒、clippingなし)。**再assemble要**(Cross-level最新仕様=Pause0.8秒/Outro最新減衰/Key Phrase3条件/In One Line見出し修正が未反映[OPEN-34]、**かつ2026-08-12のscript確定により台本と不一致[OPEN-35]**) | NOT_REVIEWED | NOT_APPROVED |
| A02 | CEFR-B2(`LAUNCH_SCOPE: OUT`) | PASS | PASS(自動QA合格。ユーザーによる本文単独の明示承認記録なし) | N/A | N/A | 未生成 | 未生成 | NOT_REVIEWED | NOT_APPROVED |
| A02 | CEFR-B1 | PASS | PASS | PASS | PASS(5件) | PASS | PASS | **PASS**(ER-003-REPRO-01、2026-08-08) | NOT_APPROVED |
| A02 | CEFR-A2 | PASS(A2-03独立生成) | **PASS**(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で最終台本確定。旧OPEN-31の1件を反映済み。Natural English Sourceとの意味一致を確認の上採用、Naturalness QA PASS。[DECISION_LOG.md](DECISION_LOG.md)参照) | PASS(Cross-level原則反映済み、ER-003-CROSSLEVEL-AUDIO-01) | PASS(3条件発音方式を5件へ適用済み、ER-003-A2-AUDIO-AB-01) | PASS(機械QA合格、hallucinationなし、In One Line見出し修正済み) | PASS(A/B版とも最新Cross-level仕様を全反映、310.5秒[A]/329.3秒[B]、clippingなし)。**ただし2026-08-12のscript確定により台本と不一致、再assemble要(OPEN-35)** | **PASS**\*\*(ER-003-A2-AUDIO-AB-01、2026-08-12。「A2の完成候補は全体としてOK」という通し試聴での総合判断だが、**この音声は script確定前の旧文言を含む**。文単位のNaturalness QA網羅を意味しない) | NOT_APPROVED |
| ADD03 | CEFR-B2(`LAUNCH_SCOPE: OUT`) | あり(日本語下書きのみ、英語台本なし) | 該当なし | N/A | N/A | 未生成 | 未生成 | NOT_REVIEWED | NOT_APPROVED |
| ADD03 | CEFR-B1 | PASS | PASS | PASS | PASS(5件) | PASS | PASS | **PASS**(ER-003-REPRO-FINAL、2026-08-09。meaning_3はASR homophone ambiguityとして人間確認済み、TTS音声は正常) | NOT_APPROVED |
| ADD03 | CEFR-A2 | PASS(A2-03独立生成) | **PASS**(2026-08-12、ER-003-A2-SCRIPT-FINAL-01で最終台本確定。旧OPEN-31の1件(Brent原油価格段落の時系列flashback構造)を7/13→7/14の実時系列順へ再構成、新規事実の追加なし、Naturalness QA PASS。[DECISION_LOG.md](DECISION_LOG.md)参照) | PROTOTYPE_BUILT(Cross-level原則反映、ただしPause 0.8秒・Outro最新減衰・Key Phrase 3条件発音・In One Line見出し修正は未反映のER-003-CROSSLEVEL-AUDIO-02版のまま) | PROTOTYPE_BUILT(方式L+Canonicalizationで新規選定5件、機械QA合格。3条件発音方式は未適用。**「Brent crude oil」キーフレーズの根拠文は台本確定後も文言としてそのまま残存**) | PROTOTYPE_BUILT(機械QA合格、hallucinationなし) | PROTOTYPE_BUILT(327.4秒、clippingなし)。**再assemble要**(A01と同じくCross-level最新仕様が未反映[OPEN-34]、**かつ2026-08-12のscript確定により台本と不一致[OPEN-35]**) | NOT_REVIEWED | NOT_APPROVED |

## N3-01: 3ジャンル横展開検証(Hanshin/Health/Household、B1-B/A2、2026-08-17更新)

以下は、Support-based Natural English設計(現行B1正式仕様)・B1-B Direct
Generation・A2 Core Explanatory Logic Preservationを使った、P-seriesとは
別系統の記事群。**PROTOTYPE / N-INCREASE VALIDATION**という位置づけで
制作され、CURRENT_SPEC.mdの現行B1/A2仕様の検証根拠になっている。

**「User Quality」列の注意**: 以下`NOT_REVIEWED`は、機械QA(ASR文字起こし・
波形解析等の技術的検証)は完了しているが、人間による通し試聴(プロジェクト
責任者を含む)がまだ記録されていないことを意味する。「開発者が試聴した」
という意味ではない(2026-08-17 SoT Consistency Cleanupで表現を訂正)。

| Article | Level | Ledger/Fact QA | Full Audio | Root Cause Fix適用状況 | User Quality | Publication |
|---|---|---|---|---|---|---|
| Hanshin | B1-B | PASS/LEDGER_COMPLIANT | 完成(clippingなし) | ROOT-FIX-01のコード変更(trim margin・instruction分離)後、**本番音声は未再生成**(コード変更は今後の新規生成から適用) | `NOT_REVIEWED`(機械QAのみ完了、人間試聴未記録) | NOT_APPROVED |
| Hanshin | A2 | PASS/LEDGER_COMPLIANT | 完成(clippingなし) | 同上。加えてA2 Core Logic Preservation原則は単発regression生成でのみ検証済み(`root_fix_01_regression/hanshin_a2_sidecheck/`)、本番article.mdへの反映は未実施(副作用なしの確認のみが目的だったため) | `NOT_REVIEWED` | NOT_APPROVED |
| Health | B1-B | PASS/LEDGER_COMPLIANT | 完成(clippingなし)。FIX-01でkp4_ja_charon「modeled differences」のinstruction leakageを修正・再assemble済み | 同上(コード変更後の本番再生成は未実施) | `NOT_REVIEWED` | NOT_APPROVED |
| Health | A2 | PASS/LEDGER_COMPLIANT | 完成(clippingなし)。FIX-01でkp4_en「follow-up time」の頭切れを修正・再assemble済み | 同上 | `NOT_REVIEWED` | NOT_APPROVED |
| Household | B1-B | PASS/LEDGER_COMPLIANT | 完成(clippingなし)。FIX-01時点から内容変更なし | 対象外(A2固有の不具合だったためB1-Bは無変更) | `NOT_REVIEWED` | NOT_APPROVED |
| Household | A2 | **REVIEW_REQUIRED**(2026-08-17 SoT Consistency Cleanupで訂正: `household/a2/fact_qa.json`の実際の最終記録値は`PASS`ではなく`REVIEW_REQUIRED`。指摘内容はPoint Two周辺の精度[バナナの追熟段階、ジャガイモ/サツマイモの最適湿度]で、今回の修正対象[fruit/vegetable二分法]の範囲外かつB1の同等表現と同水準と判断し、記録の上で許容[`er003_output/n3_01/household/a2/audit/fix01_fact_checker_acceptance_note.json`参照]。無限再生成はしていない)/LEDGER_COMPLIANT | 完成(clippingなし)。FIX-01でJapanese title のinstruction leakageとfruit/vegetable二分法を手動編集で修正・再assemble済み | **本番article.mdはFIX-01の手動編集版のまま。ER-003-N3-ROOT-FIX-01で正式採用したA2_KAI1_INSTRUCTION(Core Logic Preservation原則入り)による再生成は未実施**(→[OPEN_ITEMS.md](OPEN_ITEMS.md) OPEN-41) | `NOT_REVIEWED` | NOT_APPROVED |

**Household — 正式完成artifact(ユーザー最終試聴承認2026-09-10)、旧版
supersededへ整理**:
上記2行(`er003_output/n3_01/household/`)は**旧完成版**であり、本項の
一本化最終候補によりsupersededされた(参考のため削除はしていない)。
`HOUSEHOLD-UNIFIED-FINAL-CANDIDATE-01`(Discovery Focus Module+Part B
案1[未承認候補、Production不採用が確定]、Ledger v5、A2/B1B、
`er011_output/household_unified_final_candidate_01/`、試聴:
`player.html`)を、ユーザー試聴(2026-09-10、全体として良好)を経て
Householdの**一本化された最終候補**として確定した。B1B comment_3の
"prevent"発音に違和感の指摘があり、既存QA記録(disfluency QA用の
独立ローカルASR)に機械的誤認識証拠("prevent"→"perfect")を確認した
ため、既存segment再生成経路でcomment_3のみ差し替え済み(旧音声は
`comment_3_original.wav`として保存、A2は無変更)。再Assembly・Audio
Validation Gate opt-in ON再PASS済み(詳細はDECISION_LOG.md
`PM-CLOSEOUT-CONSOLIDATION-64`エントリ参照)。旧artifact
(`er011_output/open138_household_fact03_b1b_minimal_fix_03/`、
A-FACT03-5系)も本候補によりsupersededとして整理した(いずれのファイル
も削除はしていない、fallback候補としての再提示は行わない)。2026-09-10、
PM-CLOSEOUT-CONSOLIDATION-65にて本項を**Householdの正式完成artifact**
としてcloseoutした(ユーザー最終試聴承認済み、以後は旧版・fallbackの
再提示を行わない運用を維持する)。

**注意**: 本項目は「Household記事1本の最終版承認」を記録するもので
あり、本候補が用いた実験的Prompt要素(Discovery Focus Module Part B
案1、`cautionary_constrained`)のProduction採用(`APPROVED_FOR_
PRODUCTION`)や`editorial_mode="discovery_why"`の正式registry登録を
意味しない(Part B案1のProduction採用は2026-09-10にユーザー判断で
(c)見送りと確定、詳細はOPEN_ITEMS.md OPEN-135行参照)。番組としての
公開可否(publication)は別途判断であり、本項目は既存の
`publication_status: NOT_APPROVED`原則を変更しない。

**Artifact URL**(開発者向け試聴用、非公開): Hanshin/Health/Householdの
各テーマ比較ページ(詳細はER-003-A2-B1-N3-01完了報告・FIX-01完了報告を
参照)。

## 補足

- **A01のCEFR-B2「Source」がPASSとなっている理由**: A01のCEFR-B2は
  ER-003のNatural English Sourceから生成されたテキスト
  (`er003_output/p2/A01/b2_version_raw.md`)であり、ER-002時代の
  破棄された旧台本(`er002_output/A01/script_en.json`)とは別物。
  ER-002旧台本については[HISTORY_INDEX.md](HISTORY_INDEX.md)を参照。
- **「Podcast組立」列**: Intro/Outro/notification等を含む、番組として
  接続済みの完成候補の有無を指す。CEFR-B1のみ存在(3記事とも)。
- **A01 CEFR-B1の`User Quality`が`NOT_REVIEWED`である理由**: A01は
  P8A→P9A→P9A-R1→P9A-R2という段階的な修正プロセスを経ており、各段階で
  個別の「修正箇所承認」は得られているが、**最終版(r2)を通しで試聴し
  「これで良い」と判定した記録は見当たらない**。これはA02・ADD03の
  「初回通し候補をそのままOK」という一括判定とは性質が異なるため、
  同列に`PASS`とはしない。
- **`publication_status`が全記事`NOT_APPROVED`である理由**: 現時点では
  「番組として公開してよい」という明示的な承認判断がいずれの記事・
  レベルについても記録されていない。`user_quality_status: PASS`は
  「試聴した音質・内容に問題がない」ことのみを意味し、公開可否とは
  別の判断であることに注意([PROJECT_INDEX.md](PROJECT_INDEX.md)参照)。

## News-family(Space Weapons/AI Control/Personalized News A2、2026-09-17追加)

以下は`er014_output/user_test_news_2ep_01/`(Space Weapons/AI Control)・
`er012_output/b_family_a2_new_topic_production_01/`(Personalized News A2)
配下の通常News/B-Family新規topic正式Production経路の成果物である。
上記P-series/N3-01/Household表とは別系統(別のRunner/正式経路)のため、
別表として管理する。`User Quality`列はユーザー本人による通し試聴の
結果(`USER-FEEDBACK-CLOSEOUT-AND-VOICES-SPEC-REVIEW-01`、2026-09-17)。

| Article | Level | Full Audio | Gate結果 | User Quality | URL / player path |
|---|---|---|---|---|---|
| Space Weapons | A2 | 完成(365.408秒、clippingなし。タイトルTTS区切り修正[title_tts]適用済み、それ以外[article/scaffold/key_phrases/comment/full_story/他segment音声]は無変更を`c2af33f2..6d088d2e`diff+segment sha256比較で確認済み) | Audio Validation Gate PASS | **PASS**(2026-09-17、`USER_TEST_READY`。タイトル以外無変更確認後の条件付きPASS。**2026-09-17 `USER-TEST-REVIEW-PAGE-FORMAT-RULE-01`でunified.html表示フォーマット修正[Key Phraseラベル除去・Standard表示]反映、player.html/mp3は無変更、新SHAで再発行、E2E PASS**) | `https://rawcdn.githack.com/shimomura055/eigo-radio/55c8a324/user_test/unified.html?src=er014_output/user_test_news_2ep_01/space_weapons/a2/player.html&level=A2&en=The%20New%20Space%20Question%3A%20Is%20the%20Weapon%20in%20Orbit%3F&ja=%E5%AE%87%E5%AE%99%E3%81%AB%E5%85%B5%E5%99%A8%E3%81%AF%E3%81%82%E3%82%8B%E3%81%AE%E3%81%8B%E3%80%81%E3%82%A2%E3%83%A1%E3%83%AA%E3%82%AB%E3%81%8C%E5%88%9D%E3%82%81%E3%81%A6%E5%85%AC%E5%BC%8F%E3%81%AB%E8%AA%8D%E3%82%81%E3%81%9F%E5%87%BA%E6%9D%A5%E4%BA%8B`(旧URL全文は`docs/pm/RESULT_PACKET_CLOSEOUT_136.md`1節。E2E: `docs/pm/closeout_136_e2e/format_rule_01/e2e_result.json`) |
| Space Weapons | B1 | 完成(382.98秒、内容・音声無変更。視聴ページComment box表示レイアウトのみ修正) | Audio Validation Gate PASS | **PASS**(2026-09-17、`USER_TEST_READY`、再試聴不要。**表示フォーマット修正反映・新SHA再発行・E2E PASS[同上]**) | `https://rawcdn.githack.com/shimomura055/eigo-radio/55c8a324/user_test/unified.html?src=er014_output/user_test_news_2ep_01/space_weapons/b1b/player.html&level=B1&en=The%20New%20Space%20Question%3A%20Is%20the%20Weapon%20in%20Orbit%3F&ja=%E5%AE%87%E5%AE%99%E3%81%AB%E5%85%B5%E5%99%A8%E3%81%AF%E3%81%82%E3%82%8B%E3%81%AE%E3%81%8B%E3%80%81%E3%82%A2%E3%83%A1%E3%83%AA%E3%82%AB%E3%81%8C%E5%88%9D%E3%82%81%E3%81%A6%E5%85%AC%E5%BC%8F%E3%81%AB%E8%AA%8D%E3%82%81%E3%81%9F%E5%87%BA%E6%9D%A5%E4%BA%8B`(旧URL全文・詳細は`docs/pm/RESULT_PACKET_CLOSEOUT_136.md`1節) |
| AI Control | A2 | 完成 | Audio Validation Gate PASS | **PASS**(2026-09-17、`USER_TEST_READY`。ただし情報密度・概念負荷の重大指摘あり→OPEN-164。**表示フォーマット修正反映・新SHA再発行・E2E PASS[同上]**) | `https://rawcdn.githack.com/shimomura055/eigo-radio/55c8a324/user_test/unified.html?src=er014_output/user_test_news_2ep_01/ai_control/a2/player.html&level=A2&en=AI%20Is%20Getting%20Stronger.%20But%20What%20Does%20Control%20Really%20Mean%3F&ja=AI%E3%81%AF%E5%BC%B7%E3%81%8F%E3%81%AA%E3%81%A3%E3%81%A6%E3%81%84%E3%82%8B%E3%80%82%E3%80%8C%E5%88%B6%E5%BE%A1%E3%80%8D%E3%81%A8%E3%81%AF%E6%9C%AC%E5%BD%93%E3%81%AF%E4%BD%95%E3%82%92%E6%84%8F%E5%91%B3%E3%81%99%E3%82%8B%E3%81%AE%E3%81%8B`(旧URL全文は`docs/pm/RESULT_PACKET_CLOSEOUT_136.md`1節) |
| AI Control | B1 | 完成(RESUME-06でen=表題誤り[A2表題流用]をB1自身の表題へ是正済み) | Audio Validation Gate PASS | **PASS**(2026-09-17、`USER_TEST_READY`。OPEN-164同様の指摘あり。**表示フォーマット修正反映・新SHA再発行・E2E PASS[同上]**) | `https://rawcdn.githack.com/shimomura055/eigo-radio/55c8a324/user_test/unified.html?src=er014_output/user_test_news_2ep_01/ai_control/b1b/player.html&level=B1&en=AI%20Is%20Getting%20More%20Capable.%20What%20Do%20We%20Actually%20Know%20About%20Control%3F&ja=AI%E3%81%AF%E5%BC%B7%E3%81%8F%E3%81%AA%E3%81%A3%E3%81%A6%E3%81%84%E3%82%8B%E3%80%82%E3%80%8C%E5%88%B6%E5%BE%A1%E3%80%8D%E3%81%A8%E3%81%AF%E6%9C%AC%E5%BD%93%E3%81%AF%E4%BD%95%E3%82%92%E6%84%8F%E5%91%B3%E3%81%99%E3%82%8B%E3%81%AE%E3%81%8B`(旧URL全文は`docs/pm/RESULT_PACKET_CLOSEOUT_136.md`1節) |
| Personalized News A2(旧版、`REJECTED_AS_CURRENT_OUTPUT`) | A2(B-Family新規topic、2V) | 完成(Human Review Lock 2件[見出しASR脱落]をstandard+minimal fallback二段retryで解消し完走) | Audio Validation Gate PASS(Analytical Leakage Check残存flag[voice_a/voice_b、3attempt上限]は既存3V/2V仕様と同型、記事完成はブロックしない) | **NG**(`REJECTED_AS_CURRENT_OUTPUT`、2026-09-17。理由=Voices構造根本問題[VoiceがSurvey/統計/外部Evidenceを引用、立場がぼやける]。**本行は2026-09-17新版[次行]で置き換えられた旧記事の記録として保持**) | 旧player.html(上書き済み、`docs/pm/RESULT_PACKET_CLOSEOUT_136.md`1節) |
| Personalized News A2(新版、`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01`再生成) | A2(B-Family新規topic、2V) | 完成(Analytical Leakage Check attempt1で0件PASS[`leak_position_blur`含む全7項目]、TTS/ASR14segment全OK、Human Review Lock発生なし) | Audio Validation Gate PASS(duration=331.192秒、peak=0.95492、clipping=False) | **PASS**(`USER_TEST_READY`、2026-09-17ユーザー正式試聴・承認、closeout`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01-CLOSEOUT`。基盤`PRODUCTION_WIRED`確定。ユーザー指摘[肯定派Voiceに相手側懸念の取り込み1件残存]は記事全体として許容、再生成なし。新題"The Same Feed, Two Different Mornings"/「同じフィード、二つの違う朝」。当該指摘は`OPEN-167`で継続検討。**2026-09-17 `USER-TEST-REVIEW-PAGE-FORMAT-RULE-01`でunified.html表示フォーマット修正[Key Phraseラベル除去・Standard表示]反映、player.html/mp3は無変更[sha256記録済み]、新SHAで再発行、E2E PASS**) | `https://rawcdn.githack.com/shimomura055/eigo-radio/55c8a324/user_test/unified.html?src=er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/player.html&level=A2&en=The%20Same%20Feed%2C%20Two%20Different%20Mornings&ja=%E5%90%8C%E3%81%98%E3%83%95%E3%82%A3%E3%83%BC%E3%83%89%E3%80%81%E4%BA%8C%E3%81%A4%E3%81%AE%E9%81%95%E3%81%86%E6%9C%9D`(旧E2E evidence: `er012_output/b_family_a2_new_topic_production_01/personalized_news_2v_a2/web/e2e_playback_evidence.json`。新E2E: `docs/pm/closeout_136_e2e/format_rule_01/e2e_result.json`) |
| Personalized News B1(既知flag残存、`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01`再生成試行) | B1(B-Family、2V) | **未変更**(既存音声`voices/audio/b1_2v_v2/b1b/`のまま。再生成試行はattempt2でFact Checker A' FAILによりSTOPしたため音声化未実施) | Audio Validation Gate PASS(既存音声、無変更) | **ユーザーテスト対象外**(2026-09-17ユーザー決定、closeout`B-FAMILY-VOICES-POSITION-AND-EVIDENCE-SPEC-01-CLOSEOUT`。既存Leakage残存flagのまま[offline再評価でvoice_b 6項目+tension 2項目FAIL、`leak_position_blur`はPASS]。再生成試行はLedger鮮度問題[`OPEN-166`]でSTOP、再Research/再生成は別タスク管理) | 既存player URL: `https://raw.githack.com/shimomura055/eigo-radio/main/er014_output/four_type_observation_01/voices/audio/b1_2v_v2/player.html`(無変更) |
| Tiny Bags(`USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03`) | B1 | 完成(325.734秒、peak=0.73052、clippingなし。`point_one`は"only"5/6attempt脱落によりcanonical微修正[only→just]後1attempt目でNORMALIZED_MATCH。再生成なし・現行完成版のまま維持) | Audio Validation Gate PASS | **PASS**(2026-09-17、ユーザー本人が完成playerで通し試聴しOK/承認。`USER_TEST_READY`。**`USER-TEST-REVIEW-PAGE-FORMAT-RULE-01`で表示フォーマット修正反映[player.html/mp3無変更]、新SHA再発行、E2E PASS**) | `https://rawcdn.githack.com/shimomura055/eigo-radio/55c8a324/user_test/unified.html?src=er014_output/user_test_news_light_01/tiny_bags/b1b/player.html&level=B1&en=Are%20Tiny%20Bags%20Really%20Back%3F%20Fashion%27s%20Answer%20Comes%20With%20a%20Catch&ja=%E5%B0%8F%E3%81%95%E3%81%84%E3%83%90%E3%83%83%E3%82%B0%E3%81%AF%E6%9C%AC%E5%BD%93%E3%81%AB%E6%B5%81%E8%A1%8C%E3%81%97%E3%81%A6%E3%81%84%E3%82%8B%E3%81%AE%E3%81%8B%E3%80%81%E3%83%95%E3%82%A1%E3%83%83%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%AE%E7%AD%94%E3%81%88%E3%81%AF%E4%B8%80%E7%AD%8B%E7%B8%84%E3%81%A7%E3%81%AF%E3%81%84%E3%81%8B%E3%81%AA%E3%81%84`(旧evidence: `er014_output/user_test_news_light_01/tiny_bags/b1b/e2e/e2e_evidence.json`。新E2E: `docs/pm/closeout_136_e2e/format_rule_01/e2e_result.json`) |
| Tiny Bags(`USER-TEST-NEWS-LIGHT-TOPIC-01-CLOSEOUT-03`) | A2 | **完成**(`full_story_part2`のToteme/Kallmeyer、Human Review確認ページでの実読確認後ユーザー承認[TTS再生成なし]、`record_human_approval()`で正式記録。A2必須6% time-stretch post-processを承認済み音声へ追加適用[TTS新規生成なし、既存precedent[Trial-12/OPEN-112サブタスクG]と同型]。Assembly実行: 403.803秒、peak=0.95981、clippingなし) | Audio Validation Gate PASS(Human Approval記録によるHUMAN_APPROVED判定+slowdown post-process後にBLOCKED解消) | Human Review承認済み(ユーザーが確認ページでToteme/Kallmeyerの実読を確認し最終版として採用、2026-09-17。A2 playerは最終確認用。**`USER-TEST-REVIEW-PAGE-FORMAT-RULE-01`で表示フォーマット修正反映[player.html/mp3無変更]、新SHA再発行、E2E PASS**) | `https://rawcdn.githack.com/shimomura055/eigo-radio/55c8a324/user_test/unified.html?src=er014_output/user_test_news_light_01/tiny_bags/a2/player.html&level=A2&en=Are%20Tiny%20Bags%20Back%3F%20Fashion%27s%20Answer%20Is%20More%20Complicated&ja=%E5%B0%8F%E3%81%95%E3%81%84%E3%83%90%E3%83%83%E3%82%B0%E3%81%AF%E6%9C%AC%E5%BD%93%E3%81%AB%E6%B5%81%E8%A1%8C%E3%81%97%E3%81%A6%E3%81%84%E3%82%8B%E3%81%AE%E3%81%8B%E3%80%81%E3%83%95%E3%82%A1%E3%83%83%E3%82%B7%E3%83%A7%E3%83%B3%E3%81%AE%E7%AD%94%E3%81%88%E3%81%AF%E4%B8%80%E7%AD%8B%E7%B8%84%E3%81%A7%E3%81%AF%E3%81%84%E3%81%8B%E3%81%AA%E3%81%84`(旧E2E evidence: `docs/pm/closeout_136_e2e/tiny_bags_a2_closeout03.json`+`.png`。新E2E: `docs/pm/closeout_136_e2e/format_rule_01/e2e_result.json`) |
| Convenience AI(`USER-TEST-NEWS-CONVENIENCE-AI-01-FINALIZE-A2`) | A2 | **完成**(`point_two`"Oimo no Canele"/"AI while"ともUSER APPROVED[2026-09-17、FIX-02確認ページのattempt9+6%slowdown候補]。`record_human_approval()`で正式承認記録[TTS新規生成なし、slowdown二重適用回避]、内蔵Primary ASR再検証[単発]は`ASR_VALIDATION_UNCERTAIN`のままだが追加Secondary ASR cascade[Ledger Phrase List使用]は`NORMALIZED_MATCH`/verified_content=True。Assembly実行: 323.279秒、peak=0.95344、clippingなし) | Audio Validation Gate PASS(Human Approval記録によるHUMAN_APPROVED判定) | **PASS**(2026-09-17、`USER_TEST_READY`。post-slowdown内蔵再検証の設計ギャップは`OPEN-168`で継続管理、記事完成はブロックしない。**`USER-TEST-REVIEW-PAGE-FORMAT-RULE-01`で表示フォーマット修正反映[player.html/mp3無変更、sha256記録済み]、新SHA再発行、E2E PASS**) | `https://rawcdn.githack.com/shimomura055/eigo-radio/55c8a324/user_test/unified.html?src=er014_output/user_test_news_convenience_ai_01/convenience_ai/a2/player.html&level=A2&en=Pickles%20in%20a%20Lemon%20Tart%3F%20When%20AI%20Joins%20the%20Convenience-Store%20Kitchen&ja=%E6%97%A5%E6%9C%AC%E3%81%AE%E3%82%B3%E3%83%B3%E3%83%93%E3%83%8B%E3%80%81AI%E3%81%A7%E6%96%B0%E3%81%97%E3%81%84%E5%91%B3%E3%82%92%E9%96%8B%E7%99%BA`(旧E2E evidence: `docs/pm/closeout_136_e2e/convenience_ai_a2_finalize.json`+`.png`。新E2E: `docs/pm/closeout_136_e2e/format_rule_01/e2e_result.json`) |
| Convenience AI(`USER-TEST-NEWS-CONVENIENCE-AI-01-USER-REVIEW-FIX-02`) | B1 | **完成・ユーザー品質承認済み**(287.774秒、peak=0.95、clippingなし。`full_story_part1`のscript表示をユーザー実聴音声[実audio/ASR/独立local verbatim全て"Then Lawson planned..."]に合わせて語順修正[内容・事実は無変更、TTS再生成なし]、player再build) | Audio Validation Gate PASS | **PASS**(2026-09-17、`USER_TEST_READY`。記事全体ユーザーOK/承認済み。語順修正後は再試聴要求不要、`USER-TEST-NEWS-CONVENIENCE-AI-01-FINALIZE-A2`でscript/audio整合を再確認のみ[再build不要]。**`USER-TEST-REVIEW-PAGE-FORMAT-RULE-01`で表示フォーマット修正反映[player.html/mp3無変更]、新SHA再発行、E2E PASS**) | `https://rawcdn.githack.com/shimomura055/eigo-radio/55c8a324/user_test/unified.html?src=er014_output/user_test_news_convenience_ai_01/convenience_ai/b1b/player.html&level=B1&en=A%20Lemon%20Tart%2C%20Pickles%2C%20and%20an%20AI%20Suggestion&ja=%E6%97%A5%E6%9C%AC%E3%81%AE%E3%82%B3%E3%83%B3%E3%83%93%E3%83%8B%E3%80%81AI%E3%81%A7%E6%96%B0%E3%81%97%E3%81%84%E5%91%B3%E3%82%92%E9%96%8B%E7%99%BA`(旧evidence: `.../b1b/human_review/e2e_evidence_fix02.json`。新E2E: `docs/pm/closeout_136_e2e/format_rule_01/e2e_result.json`) |

上記5本(News-family既存分)は`publication_status`(公開承認)の判断対象
ではない(既存の「User Quality≠Publication」原則を維持、`NOT_APPROVED`
のまま)。Tiny Bags B1/A2・Convenience AI A2/B1も同様に`NOT_APPROVED`。

## 参照元

[ER-003-REPRO_BASELINE.md](ER-003-REPRO_BASELINE.md)、
[ER-003-B2-AUDIT-01_SPEC_AUDIT.md](ER-003-B2-AUDIT-01_SPEC_AUDIT.md)、
[ER-003-B1_P8A-P9A_AUDIT_REPORT.md](ER-003-B1_P8A-P9A_AUDIT_REPORT.md)、
各記事の`audio_validation_main.md`
