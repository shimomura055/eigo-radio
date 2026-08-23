# ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01 完了報告

**管理ID: ER-006-POOL-MASTER-ADOPTION-N4N6-RESUME-01**
**内包する3区分: ER-006-POOL-ADOPTION-AUDIT-01 / ER-006-POOL-N4-N6-PRODUCTION-01 / ER-006-PRODUCTION-THROUGHPUT-GATE-01**
**日付: 2026-08-22〜2026-08-23**

---

## 0. タスクの位置づけ

前タスク`ER-006-POOL-ADOPTION-N4N6-PRODUCTION-01`は、「20 Topicリストの
一次資料がリポジトリ内に存在しない」ことが判明しSTOPした。今回、
ユーザーが20 Topic全体を新規承認したため、[POOL_TOPIC_MASTER.md](POOL_TOPIC_MASTER.md)
として正式記録した上でPart A(既存3記事の採用準備)・Part B(No.4〜6の
現行仕様生成)・Part C(Throughput Gate測定)を実施した。

---

## 1. 何が問題だったか
既存3記事(Public Benches/Subscriptions/Startups)は、実は複数の異なる
実装バージョン(Sol版/Luna版/ASR刷新版)が混在しており、どれが「今
ユーザーに聴いてもらうべき最終版」か、正式に整理されていませんでした。
また、20記事構成のうちNo.4〜6は未着手のままで、現在の音声生成の仕組み
(Gemini Batch API)が「1日20記事」という運用目標に耐えられるかどうかも、
実際のデータで検証されたことがありませんでした。

## 2. 何を変更したか
- **既存3記事の整理**: 各記事について最も現行仕様に近い組み合わせ
  (記事本文+音声)を1組ずつ特定し、台本と音声が実際に一致しているかを
  15区間全てで確認しました。その過程で、6箇所で「AIによる自動音声
  チェックには合格していないが、そのまま最終音声に使われている」区間
  を発見し、試聴用ページで名指しで警告しています
- **No.4〜6を実際に生成**: 3つの新しい記事(スーパーの棚替え・カフェの
  長時間客対応・配送追跡確認の心理)を、実在する学術論文や業界記事を
  Web検索で調べた上で、現在の正式な仕組み(Lunaモデル・Batch音声生成・
  OpenAI音声認識等)だけを使って、記事執筆から音声組み立てまで一通り
  作りました
- **実際の処理時間を計測**: 1記事だけを作った場合と、2記事を同時に
  作った場合の両方で、正確な所要時間を記録しました

## 3. 何が改善されるか
- ユーザーは、既存3記事・新規3記事とも、台本を読みながら音声を通しで
  確認できるページで最終判断ができるようになりました
- 「1日20記事作れるか」という問いに、机上の計算ではなく実測データで
  答えられるようになりました。結論は「4〜5個の処理を同時に走らせれば
  数字上は届くが、実際にそこまでの同時実行は試していないため、まだ
  リスクがある」という正直な評価です

## 4. リスク・注意点
- 新規3記事は、AIによる内容チェックで「用語がやや厳密さを欠く」等の
  軽微な指摘が残っています(捏造や事実誤りではありません)。最終的な
  採用可否はユーザーの試聴判断待ちです
- 音声生成(Gemini Batch)は依然として非常に時間がかかります(1記事の
  B1+A2ペアで3.4〜4.7時間)。これは今回の作業で新たに悪化したわけでは
  なく、実測して初めて正確な数字が分かった、という位置づけです
- 作業中に2件の技術的な不具合(見出し表記のずれ、Key Phrase生成の
  想定外の停止)を発見・修正しましたが、いずれも記事内容そのものへの
  影響はありませんでした

---

## 5. §15 完了報告25項目への回答

1. **Pool Topic Masterの正式保存先**: [POOL_TOPIC_MASTER.md](POOL_TOPIC_MASTER.md)(新規作成)
2. **No.1〜20が保存された証拠**: POOL_TOPIC_MASTER.mdの表に20件全て
   (No.+ English Title + 日本語タイトル + Theme Category + 3種の
   Status)を記載。git commit `850d292`で正式記録・push済み
3. **既存3記事の採用Candidate**: Public Benches=script(Luna版)+
   audio(ASR-Pilot-02版)。Subscriptions/Startups=唯一存在する原初版
   (Sol Writer時代)。詳細は
   [ER-006-POOL-ADOPTION-AUDIT-01_diff.md](ER-006-POOL-ADOPTION-AUDIT-01_diff.md)
4. **script/audio一致可否**: 一致(TTS送信テキストと正式scriptは、
   既知の安全な正規化を除き完全一致)。ただし6区間が機械ASR検証未合格
   のまま採用されており、試聴Artifactで明示的に警告済み
5. **不一致がある記事**: 厳密な意味での「script/audioの不一致」
   (旧scriptと新audioの食い違い)は0件。「audio未検証のまま採用」の
   6区間は上記4参照
6. **既存3記事のcurrent Productionとの差異一覧**:
   [ER-006-POOL-ADOPTION-AUDIT-01_diff.md](ER-006-POOL-ADOPTION-AUDIT-01_diff.md)
   のStage別表参照。Public Benchesは主にQA_ONLY/COST_ONLY差、
   Subscriptions/StartupsはWriter/Support系がSolのままでCONTENT_
   AFFECTINGに分類
7. **ユーザー最終確認Artifact URL**(No.1〜6全件):
   - No.1 Public Benches: https://claude.ai/code/artifact/31c9ac90-75a6-4742-89c2-3d2590d30662
   - No.2 Subscriptions: https://claude.ai/code/artifact/3a5ad42b-d06e-4016-b830-a90df63e732d
   - No.3 Startups: https://claude.ai/code/artifact/aeaf4fee-c82d-45e4-b02f-f3f7dbc7ccd0
   - No.4 Supermarket Shuffle: https://claude.ai/code/artifact/441e2f85-9c27-4cb6-99b0-a3014df788f4
   - No.5 Cafes: https://claude.ai/code/artifact/519d6d3a-00d6-457a-bfbb-9674b7e0a8d5
   - No.6 Delivery Tracking: https://claude.ai/code/artifact/b9403185-9af7-4aac-9b3e-1c286cabfc4e
8. **No.4のTopic title**: The Supermarket Shuffle: Why Shelves Keep Moving
9. **No.5のTopic title**: Cafes Are Rethinking the All-Day Customer
10. **No.6のTopic title**: The Strange Pull of Delivery Tracking
11. **No.4〜6はすべてcurrent Production仕様で生成できたか**: できた。
    Research routing(Luna)・Writer/FactCheck/Support(Luna)・TTS
    (Gemini Batch)・English Primary ASR(OpenAI gpt-4o-mini-transcribe)・
    Japanese ASR(Azure)・現行Validator・Master Audio Store・ASR-first
    Retry Policyを全て使用
12. **Sol call数**: **0件**(3 Topic合計、raw_usage_log.jsonlで確認)
13. **Standard TTS call数**: **0件**(全てGemini Batch API経由)
14. **No.4 actual wall-clock**: 4.15時間(14,938秒。Research/Writer
    反復込み。TTS単体は3.44時間)
15. **No.5 actual wall-clock**: 3.67時間(13,210.5秒、並列実行)
16. **No.6 actual wall-clock**: 4.67時間(16,831秒、並列実行+自己復旧
    作業込み。純TTS作業時間ベースでは約4.55時間)
17. **No.5+6 parallel wall-clock**: 両方完了まで約4.67時間(開始
    2026-08-23 11:45:42 JST〜No.6完了16:26:13 JST)
18. **各TopicのBatch job数**: No.4=67件(65成功)、No.5=67件(66成功)、
    No.6=88件(88成功)
19. **各TopicのTTS retry数**: Batch job数と技術的失敗数の差分が実質
    retry数(No.4=2、No.5=1、No.6=0[全件初回成功、ただしSTOPPED区間は
    6回のASR検証retryを内部で消費])
20. **各TopicのHuman Review件数**: No.4=1区間(A2 comment_2)、No.5=2
    区間(B1 full_story_part1/2)、No.6=3区間(B1 full_story_part1
    [UNCERTAIN]、A2 full_story_part1・point_one[STOPPED])
21. **1-lane Topic/day換算**: 約6.5 Topic/day(No.5の3.67時間を代表値
    として24時間で割った値)
22. **observed parallel Topic/day換算**: 約12 Topic/day(2 lane、約4
    時間で2 Topic処理した実測に基づく換算)
23. **20 Topic/dayに必要な推定parallelism**: 最低4 lane相当
    (30 Topic/day参考値は5 lane相当)
24. **20 Topic/day判定**: **`AT_RISK`**(2 lane並列では劣化が見られ
    なかったが、4〜5 laneでの実測は未実施のため。詳細は
    [ER-006-PRODUCTION-THROUGHPUT-GATE-01_report.md](ER-006-PRODUCTION-THROUGHPUT-GATE-01_report.md))
25. **ボトルネック工程**: Gemini Batch TTS(Audio生成stage)。全Topicで
    総所要時間の83〜96%を占める

**各Topic実費**: No.4=¥143.5、No.5=¥95.6、No.6=¥117.4(詳細は
Throughput Gate報告書参照)

**回帰テスト結果**: `run_project_regression.py` 1753/1753 PASS

**残存Open Item**: OPEN-51(4〜5 lane並列実行の実測未実施)、OPEN-52
(Key Phrase Selectorのretry loop欠如)、OPEN-53(No.4〜6の最終採用は
ユーザー試聴待ち)

**新規API Cost総額**: No.4〜6のPool Production生成で**¥356.5**
(Research+Writer+Support ¥113.4、TTS Batch ¥202.3、ASR English ¥18.0、
ASR Japanese ¥22.9)。既存3記事の棚卸し・Artifact作成には新規API
支出なし(既存生成物の再利用・ffmpeg圧縮・静的ページ生成のみ)。

---

**完了。No.7以降には進まない。**
