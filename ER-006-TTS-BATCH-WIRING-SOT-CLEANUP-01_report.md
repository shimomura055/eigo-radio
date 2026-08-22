# ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01 完了報告

**管理ID: ER-006-TTS-BATCH-WIRING-SOT-CLEANUP-01**
**日付: 2026-08-22**

## 0. タスクの位置づけ

ER-006-AUDIO-COST-SPEC-FIX-01で「Gemini TTS Batch APIの採用は正式
Decision済みだが、実際のProduction TTS生成6経路は全てStandard呼び出し
のまま」と正直に記録した実装ギャップ(OPEN-50)を解消するタスク。
(1) Batch APIをProduction 6経路へ実配線する、(2) CURRENT_SPEC内に
残っていた旧ASR記述(Azure STT全内容確認という古い表現)を、現行の
英語Primary=OpenAI mini/日本語=Azureという仕様へ整合させる、の2点を
実施した。新しい音声仕様・モデル変更・サービス仕様変更は行っていない。

---

## 1. 何が問題だったか
「BatchをProduction標準にする」という決定は前回のドキュメント整理
タスクで正式に記録されていましたが、実際の音声生成プログラム6箇所は
まだ古い方式(Standard、1件ずつすぐに結果が返る方式)のままでした。
つまり「決めたことになっているが、実際には切り替わっていない」状態
でした。加えて、正式仕様書の中に「音声認識(ASR)はAzureを使う」という
古い記述が一部残っており、実際の仕様(英語はOpenAI、日本語はAzure)と
食い違ったままでした。

## 2. 何を変更したか
- **新規モジュール**[er006_batch_tts_wiring_01.py](er006_batch_tts_wiring_01.py)
  を作成し、音声生成6ファイルすべての実際の呼び出し箇所を、Standard
  呼び出しからGemini Batch API(まとめて安く処理する方式)へ差し替え
  ました。声・話し方の指示・読み上げる文章・音質設定は一切変更して
  いません(内部の「送信方法」だけを変更)
- Batch job(1件の処理単位)が成功したように見えても、中身のitemが
  実際には失敗している場合を個別に検出し、失敗したものだけを
  再送する仕組みを実装しました(丸ごと再送はしない)
- 料金表([pricing_snapshot.json](er005_output/cost_baseline_01/pricing_snapshot.json))
  にBatch料金(通常の半額)を追加し、実際のコストを自動計算・記録
  できるようにしました
- CURRENT_SPEC.mdの「ASR診断」欄の古い記述を、現行仕様(英語=OpenAI
  Primary、日本語=Azure)へ修正しました
- Static Audit(自動チェックスクリプト)を更新し、「Standard呼び出しが
  残っていないか」を今後も自動検知できるようにしました
- **実際に少額の本番相当APIを使って動作確認**を行いました(既存の
  承認済みKey Phrase文言を再利用、代表2件のみ、既存の完成音声には
  一切触れていません)

## 3. 何が改善されるか
- 「決定はしたが未実装」というギャップが解消され、実際にコスト削減
  効果が発生する状態になりました
- 実測でコスト削減率**約50%**を確認しました(想定通り)
- 仕様書内の矛盾(ASR記述)が解消され、今後の作業者が誤読するリスクが
  減りました
- 自動チェックにより、将来のコード変更でうっかりStandard方式へ
  戻ってしまった場合に検知できるようになりました

## 4. リスク・注意点
- **新たに判明した重要な点**: Batch方式は1件あたりの処理に**90〜170秒
  程度**かかることが実測で分かりました(従来のStandard方式は数秒)。
  音声認識の検証に不合格で再試行が発生するsegmentでは、この待ち時間が
  積み重なります(実測例: 4回再試行で合計522秒)。**コストは下がります
  が、生成にかかる時間は増える可能性があります**。量産運用時は処理
  時間への影響を監視することをお勧めします
- TTS発音ヒント注入(固有名詞の発音を助ける仕組み)は、今回は意図的に
  手をつけていません(前回の検証で効果が不明確だったため)
- 実際に使った音声生成の費用は極めて小額です(下記参照)

---

## 5. §20 完了報告16項目への回答

1. **Production Batch配線完了可否**: 完了。Production 6経路すべてが
   Gemini Batch API経由になった
2. **対象6ファイルの配線結果**: `er003_v1_repro01_main_generate.py`
   (2箇所)・`er003_v1_sing01_news_tail_fix.py`・`er003_v1_sing01_point_
   headings_aoede.py`・`er003_v1_sing01_voice01_generate.py`(4箇所)・
   `er003_v1_n3_01_tts_generate.py`(1箇所)を直接編集。
   `er003_v1_crosslevel_audio_02_common.py`は自身でTTS呼び出しを構築
   せず`repro01`の関数を再利用するだけのため、直接編集なしで自動的に
   Batch経由になった(Static Auditで確認済み)
3. **Standard TTS Production経路が残っていないか**: 残っていない。
   Static Auditで、Standard専用のcall_fn構築(`gclient.make_tts_call_fn`
   等4パターン)が実コード(コメント除く)に一切残っていないことを
   assertionで確認した
4. **暗黙Standard fallback有無**: なし。`er006_batch_tts_wiring_01.py`
   のソースコードに`generate_content`という文字列自体が(コメントも
   含め)存在しないことをunit testで確認済み(fail-closed設計)
5. **Master Audioとの統合結果**: 無変更のまま正常に機能している。
   Master Audio Storeのlookupは、Batch配線したTTS呼び出し関数より
   前段(呼び出されるかどうかの分岐そのもの)にあるため、設計上
   自動的に「hit時はBatch投入なし、miss時のみBatch」になっている
6. **item-level Failure Handling結果**: 実装済み・unit test 14件で
   確認済み(success/API error/empty result/invalid audio/missing
   response/job failed/timeoutの各ケース)
7. **最小実API確認結果**: 成功。代表2segment(英語Key Phrase"opt out"・
   日本語gloss「参加・適用を断る」)を実際のProduction関数
   (`repro01.generate_key_phrase_component_verified`/
   `generate_narration_snippet_verified_strict`)経由で生成し、
   両方ともstatus=OK(既存のtrim/hallucination検知/ASR検証を通過)。
   Batch job計5件全てSUCCEEDED
8. **Batch実コスト**: $0.003376(約¥0.54)
9. **Standard換算との差**: Standard換算$0.006755(約¥1.08)。
   **削減率50.02%**(想定通りの約50%を確認)
10. **Static Audit結果**: 全チェックPASS。Batch配線チェックは
    以前の[GAP]報告からassertion対象へ昇格させ、正式にPASSしている
11. **Project regression結果**: 1753/1753 PASS(既存の音声検証
    fixture・Model Routing Contract test・Batch wiring unit test
    14件を含む)
12. **CURRENT_SPEC修正内容**: 「Audio Production Pipeline」節の
    「Gemini TTS実装方式」「Batch Failure Handling」行(NOT_WIRED→
    WIRED、実測結果・運用上の注意点を追記)、「Model Routing Contract」
    節のTTS行、「QA / Human Review」節のASR診断行
13. **ASR旧記述解消可否**: 解消済み。「Azure STTを全内容確認・境界
    検証に使用」という記述を、現行の言語別Routing仕様へ書き換えた
14. **OPEN-50状態**: Batch配線部分は`RESOLVED`。TTS Pronunciation Hint
    配線部分は今回のスコープ外のまま`TBD`として継続(OPEN-47と関連
    づけて記録)
15. **残存Open Item**: TTS Pronunciation Hint配線判断(OPEN-47)、
    Secondary ASR Cascade default ON化判断(OPEN-48)、Cascade発動率の
    ランダムサンプル検証(OPEN-49)。加えて、今回新たに判明した
    「Batch方式は1件あたりの処理時間が長い」という運用上の特性を、
    CURRENT_SPECの当該行へ明記した(新規Open Itemとしては起票せず、
    Batch方式の仕様そのものの一部として記録)
16. **新規API Cost**: 実API確認で$0.003376(約¥0.54)。それ以外の
    作業(ドキュメント更新・コード実装・Static Audit)は新規API支出0円

---

**完了。既存3 Pool Topicの再生成・残り17 Topic量産には進まない。**
