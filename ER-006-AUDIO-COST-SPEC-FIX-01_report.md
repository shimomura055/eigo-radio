# ER-006-AUDIO-COST-SPEC-FIX-01 完了報告

**管理ID: ER-006-AUDIO-COST-SPEC-FIX-01**
**日付: 2026-08-22**
**タスク種別: ドキュメント/SSOT統合(新規実装・新規API支出なし)**

## 0. タスクの位置づけ

過去4タスク(AUDIO-COST-PILOT-02 / PRONUNCIATION-LEDGER-SECONDARY-ASR-01 /
AUDIO-RETRY-CASCADE-PROD-01 / VALIDATOR-NUMERIC-COST-RECONCILE-01)で行った
Audio生成パイプラインの実装決定を、SSOT(CURRENT_SPEC.md /
DECISION_LOG.md / OPEN_ITEMS.md / Model Routing Contract)へ正式に
固定し、将来のcommitが気づかず古い実装へ後退(drift)しないよう
機械的な保護(Static Audit)を追加した。**新規のPool Topic生成・新規
API呼び出し・サービス仕様変更は一切行っていない。**

---

## 1. 何が問題だったか

過去4タスクの実装決定(ASR Provider切替・Validator一般化・Master Audio
Store・Pronunciation Ledger・Secondary ASR Cascade)は、それぞれの
完了報告とDECISION_LOGの個別entryには記録されていたが、**正式仕様
(CURRENT_SPEC.md)には未反映のまま**だった。特にCURRENT_SPEC.mdの
「Model Routing Contract」表は、TTS行が`gemini-2.5-pro-preview-tts`
(Batchへの言及なし)、ASR/Audio QA行が「Azure Speech-to-Text」
(OpenAI Primary化への言及なし)のまま古い状態で残っており、これを
見た将来の作業者が「AzureがEnglish ASR Primaryのまま」「TTSは
Standard呼び出しのまま」と誤解し、意図せず古い実装へ後退させる
リスクがあった。

また、調査の過程で**新たな実装ギャップ**を発見した:「Gemini TTS
Batch APIをProduction標準として採用する」というDecisionは確定して
いたが、実際にGrep/Readで確認したところ、Production TTS生成6箇所
(下記)はいずれも現時点で**Standard同期呼び出しのまま**であり、
Batch(`client.batches.create()`)はA/Bテスト用の使い捨てscriptでしか
使われていなかった。同様に、TTS Pronunciation Hint注入も
Production TTS生成には未配線のままだった。

## 2. 何を変更したか

### ドキュメント更新(3ファイル)

- **[CURRENT_SPEC.md](CURRENT_SPEC.md)**: 新設「Audio Production
  Pipeline(ER-006、Pool/N3 Production基盤)」節を追加し、Gemini TTS
  Batch方式・Batch Failure Handling・Master Audio Store・Primary ASR
  Routing・Validator一般化仕様・Pronunciation Ledger・TTS Pronunciation
  Hint・ASR-first Retry Policy・TTS Retry条件・Human Review Route・
  Production call site一覧を正式仕様として記載した。新設「Cost定義
  (Audio Production)」節で、Historical Actual / Clean Production Cost
  (¥65.14/pair) / Expected Conditional Waste(¥46.03/pair) / Expected
  Production Cost(¥111.17/pair)の4区分を定義した。既存「Model Routing
  Contract」表のTTS行・ASR/Audio QA行を、実際の決定内容(Batch方式・
  OpenAI Primary ASR)へ更新し、**Batch配線が未実装であることも
  隠さず明記**した。参照元に4タスクの完了報告リンクを追加した。
- **[DECISION_LOG.md](DECISION_LOG.md)**: 「ER-006-AUDIO-COST-SPEC-FIX-01
  (2026-08-22)」節を新設し、8件のDecision(Luna routing / Gemini Batch
  採用 / OpenAI mini Primary ASR / Master Audio採用 / Validator一般化 /
  Pronunciation Ledger採用 / ASR-first retry優先 / Cost 4区分定義)を、
  それぞれ日付・根拠・supersedes・根拠タスクを明記した形で記録した。
- **[OPEN_ITEMS.md](OPEN_ITEMS.md)**: OPEN-46(Batch Human Review試聴を
  `Resolved`へ、Primary ASR/Master Audioの実装をCURRENT_SPEC確定へ
  昇格させ、残るOttoni対応・複数トピック検証・Prompt Cacheのみを
  継続扱いに整理)、OPEN-48(「28→twenty-eight」ギャップの解消を記録し、
  残るAzure時刻フォーマット誤認識・Cascade default化判断のみを継続
  扱いに整理)を更新。新規**OPEN-50**(Gemini TTS Batch配線・TTS
  Pronunciation Hint配線が未実装であるという実装ギャップ)を追加した。

### コード変更(2ファイル、いずれもロジック変更なし)

- **[er006_model_routing_contract_01.py](er006_model_routing_contract_01.py)**:
  `TTS_MODEL`定数へ、既存の`ASR_PROVIDER`コメントと同じ形式で、
  Batch方式採用・実装未配線の状況を説明するコメントを追加した(定数の
  値自体は無変更)。
- **[er006_audio_cost_spec_fix_01_static_audit.py](er006_audio_cost_spec_fix_01_static_audit.py)**
  (新規): Production Audio 6ファイルを対象に、(a)旧Azure英語Primary
  ASR直接呼び出しの不在、(c)旧Validator直接呼び出しの不在、(d)ASR
  不確実性からのTTS即時再生成という旧retry loopの不在(Cascade経由の
  強制)、(f)Master Audio bypassの不在、(e)Sol modelの不在(Audio/
  Pronunciation系モジュール含む)、(g)Pronunciation Ledgerが呼び出し
  経路から無視されていないこと、を機械的に検証する。Batch配線の
  状況は「既知GAP」として明示的にassertion対象外の状況報告のみ行い、
  実装済みと偽装しない設計にした。

## 3. 何が改善されるか

- CURRENT_SPEC.mdを見れば、Production Audioパイプラインの実装
  アーキテクチャ(TTS方式・ASR provider・Validator・Master Audio・
  Pronunciation・retry policy)が正しく分かるようになった(従来は
  DECISION_LOGの個別entryを4件遡らないと分からなかった)。
- 将来のcommitが、Static Audit(`er006_audio_cost_spec_fix_01_static_
  audit.py`)を実行することで、旧Azure ASR直接呼び出し・旧Validator
  直接呼び出し・旧retry loop・Master Audio bypass・Sol modelの復活を
  機械的に検出できるようになった。
- Batch API配線・TTS Pronunciation Hint配線という2つの実装ギャップを、
  ドキュメント上で偽装せず正直に記録した(OPEN-50)。これにより、次に
  このパイプラインへ触る作業者が「CURRENT_SPECにBatchと書いてあるから
  もう配線済みだろう」と誤解して量産判断を誤るリスクを防いだ。
- Cost定義4区分(Historical Actual/Clean/Waste/Expected)により、今後の
  報告で異なる定義のコスト数字が混同される(¥106.4 vs ¥113.0のような
  食い違い)リスクを構造的に減らした。

## 4. リスクや注意点

- **Gemini TTS Batch配線は依然未実装**(OPEN-50)。CURRENT_SPEC.mdは
  「Batch方式が採用された」ことと「実装は未配線」であることの両方を
  明記しているが、表面だけ見て誤解しないよう注意が必要。
- **TTS Pronunciation Hint注入も未配線のまま**(既存OPEN-47の内容を
  正式spec上でも明記)。ASR側(Secondary ASR Phrase List)のみ配線済み。
- Secondary ASR Cascadeのdefault ON化・発動率の実測検証・Pronunciation
  Research cache-hit率のサンプル拡大は、いずれも継続Open Item
  (OPEN-48/49)のまま。
- Expected Production Cost(¥111.17/pair)はestimateを含む進化中の
  baselineであり、恒久固定値ではない。

---

## 5. §15 完了報告15項目への回答

1. **正式にFIXしたProduction spec**: Gemini TTS Batch方式(採用方針)、
   Primary ASR Routing(英語=OpenAI mini/日本語=Azure)、Master Audio
   Store、Validator数値正規化一般化、Pronunciation Ledger(ASR側配線)、
   ASR-first Retry Policy、TTS Retry条件の絞り込み、Human Review
   Route、Cost定義4区分。CURRENT_SPEC.md「Audio Production Pipeline」
   節・「Cost定義」節・「Model Routing Contract」表として記載。
2. **観察のまま残した項目**: Batch API実装配線(OPEN-50)、TTS
   Pronunciation Hint配線(OPEN-47/OPEN-50)、Secondary ASR Cascade
   default ON化判断(OPEN-48)、Cascade発動率実測(OPEN-48/49)、
   Pronunciation Research cache-hit率サンプル拡大(OPEN-49)、
   Ottoni型固有名詞対応方針(OPEN-46/47)。
3. **CURRENT_SPEC.md更新箇所**: 「Audio Production Pipeline」節(新設、
   QA/Human Review節の直後)、「Cost定義(Audio Production)」節
   (新設、同節内サブセクション)、「Model Routing Contract」表のTTS行・
   ASR/Audio QA行、参照元リスト。
4. **DECISION_LOGへ追加したDecision**: 「ER-006-AUDIO-COST-SPEC-FIX-01
   (2026-08-22)」節に8件(上記2章参照)、各々に日付・根拠・supersedes・
   根拠タスクを明記。
5. **OPEN_ITEMS Resolved/継続リスト**: 2章参照(OPEN-46/48更新、
   OPEN-50新規追加)。
6. **Standard TTSへ戻る経路は残っているか**: **残っている、ただし
   それは「後退」ではなく「未着手」**。Batch配線自体が最初から実装
   されていないため、"戻る"というより"まだ到達していない"状態。
   Static Auditはこの状態を隠さず[GAP]として報告する。
7. **Azure-English-Primaryへ戻る経路は残っているか**: 残っていない。
   Static Audit checkで、旧Azure直接ASR関数(`get_full_text_via_
   azure_stt_continuous`)がProduction 6ファイルに一切現れないことを
   確認済み(PASS)。
8. **Solへ戻る経路は残っているか**: 残っていない。Static Auditで
   Audio/Pronunciation系13ファイル全てに`gpt-5.6-sol`literalが
   存在しないことを確認済み(PASS)。
9. **旧Validator bypassは残っているか**: 残っていない。Static Auditで
   `audio_validation.evaluate_attempt(`の直接呼び出しがProduction
   6ファイルに存在しないことを確認済み(PASS)。
10. **旧retry loop bypassは残っているか**: 残っていない。Static Audit
    で、英語ASR検証(`routing.transcribe`)の呼び出し箇所は必ず
    `secondary_asr.evaluate_attempt_with_cascade`を経由していることを
    確認済み(PASS、日本語呼び出しはCascade対象外として除外)。
11. **Master Audio bypassは残っているか**: 残っていない。Static Audit
    で、`ensure_all_shared_narration_b1/a2`が`er003_v1_n3_01_tts_
    generate.py`のsegment生成最上流で呼ばれていることを確認済み
    (PASS)。
12. **Static Audit結果**: 全チェックPASS(exit code 0)。詳細は
    `er006_audio_cost_spec_fix_01_static_audit.py`実行ログ参照。
    Batch配線・TTS Pronunciation Hint配線の2点のみ、assertion対象外の
    [GAP]として意図的に報告(実装済みと偽装しない設計)。
13. **Regression test結果**: `er006_preprod_hardening_01_validation_
    test.py`(32 fixture)全PASS。`er006_model_routing_contract_01_
    test.py`・`er006_model_routing_contract_01_static_audit.py`・
    `er006_audio_cost_spec_fix_01_static_audit.py`全PASS。プロジェクト
    全体回帰(`run_project_regression.py`)1753/1753 PASS。
14. **残るドリフトリスク**: Batch配線・TTS Pronunciation Hint配線の
    未実装状態そのもの(実装されるまでStatic Auditは継続してこの
    2点を[GAP]として報告し続ける設計)。Secondary ASR Cascadeの
    default ON化判断・発動率実測が未完了なため、その判断材料自体が
    まだ揃っていない。
15. **新規API支出**: **¥0**。本タスクはドキュメント更新・Static Audit
    scriptの新規作成・既存comment追加のみで、新規のLLM/TTS/ASR API
    呼び出しは一切行っていない。

---

**完了。残りPool Topic生成には進まない。**
