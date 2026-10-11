# JA_EXCEPTION_CLASSIFICATION_DRAFT_01 (ASR-TTS-CROSS-LANGUAGE-RECONCILIATION-01 委任_01、暫定案、2026-10-11)

日本語側の「共通フローから外れる例外」の暫定分類。**提案のみ。新たな例外仕様・閾値は採用しない。Production・SSOT無変更。** 有料API未使用。
分類: **A=必要**(誤PASS/害の根拠があり、共通フローにも残すべき)、**B=統一可能**(共通フロー側へ寄せても品質低下の実績/根拠が見当たらない)、**C=要判断**(根拠が割れる/実測不足/ユーザー決定済みの仕様と衝突しうる)。
根拠の出所: `JA_SPEC_SURVEY_01.md`、`G8_GAS_KASU_INVESTIGATION_01.md`、`JA_OFFLINE_COMPARISON_01.md`(同ディレクトリ)。略記は同じ。
注: 以下の「誤PASS例」は、実測が無い場合は構造的な想定(推測)と明記する。

| ID | 例外 | 具体的な誤PASS例/害 | 過去の根拠 | 代替策(提案) | 分類 | 備考 |
|---|---|---|---|---|---|---|
| X1 | 数字差でSCG不実行(VAL L256-261、SEC L191) | 「理由は3つ」->音声が「4つ」(合成確認: NOT_APPLIED)。数量の取り違えは意味が逆転 | 2026-08-25 U承認の保護チェック。Phase 0のg42(Primary「三つ、四つ」=追加数字)は予算上限で未実行 | なし。漢数字/表記ゆれは既存D-1(OPEN-145)で救済済みのため除外を維持 | **A** | Phase 0で追加除外案の漢数字ルールはg27(一旦)を誤除外=粗すぎで不採用(RESULT_01(3))。現行の数字差判定(`\d+`のみ)はそのまま |
| X2 | 否定差でSCG不実行(`negation_mismatches`+推奨4マーカー、SEC L102-165) | 「縛られず自由に」->音声「縛られる自由に」(g12、C群)。Azureは逐語転写でNG(実測)だが、原稿寄りに丸められたら最終防壁が無い | 2026-08-25 U承認の保護チェック。推奨4は2026-10-11 U採用(DL L20550) | 活用ギャップの補強(合成確認: 「来なかった->来た」はマーカー対象外でSCG実行)=新規仕様候補、**未承認、提案のみ** | **A** | マーカー規則の追加効果は実測でAzure呼出節約(約0.2円/回)のみ。ギャップ補強はFable判断 |
| X3 | Primary-原稿の類似度<0.4でSCG不実行(SEC L195) | 目的は「TTS異常(echo/hallucination)にSecondaryを走らせない」。害の実測は**逆向き**: g7 湿度->Primary「死図塔」(Azure=湿度が正)が不救済 | 既存classifyのtts_failure_threshold=0.4(VAL L483)。Phase 0 RESULT_01(3)で「短いkey phraseでは正しい発音でも類似度0になる」と指摘。Phase 0で追加除外せず現行維持 | 短文(例: 原稿が数文字)は閾値を適用しない/絶対編集距離に置換/echo検出を別途(`detect_duration_anomaly`、length_ok)に任せる。**新閾値のため未採用** | **C** | 標本1件(g7)。誤PASS防止の実績は無し(除外しても誤PASS 0) |
| X4 | `length_ok=False`でSCG不実行(SEC L401-402) | SCG PASSでも`verified=verified_content and length_ok`で不合格になるためAzure無駄呼出 | OPUS推奨6(Fable採用、DL L20550) | なし | **A** | 品質ではなく費用最適化。害なし |
| X5 | entity_like差分(カナ/英字略語のreplace)があればSCG不実行(C1a、SEC L200-201) | 想定: 原稿「ガス」/音声「カス」をAzureが高頻度語「ガス」へ丸めて誤PASS。**実測0**(濁点誤りの実績0、C群0/5)。g8の実害は救済機会の喪失(再生成1回) | Opus必須1->Fable採用(F)。ユーザー個別承認なし(DL L20550、g8 13/14受入は確認待ち)。旧承認SPEC L1998は「entity-like検出時にAzure確認」で逆向き | (1)濁点差のみ(phonetic_uncertain)の混在はSCGを許す (2)旧Cascadeと同一に統一(Secondary PASSはEXACT/NORMALIZED) (3)現行維持。追加Trial案: 濁点最小対40クリップ約9〜10円(JA_OFFLINE_COMPARISON_01.md 6節) | **B**(濁点・一般カタカナ語)/ 真の固有名詞は**A** | ラベルと実挙動が不一致(一般カタカナ語も対象、挿入/脱落メタ->メタンは対象外)。最終はUSER_DECISION_REQUIRED(g8) |
| X6 | 辞書読み不一致(`reading_dictionary_mismatch`)でSCG不実行(C1b) | 辞書で確定した読み(例: Meta=メタ)とPrimaryの転写が異なる箇所で、Azureの表記一致だけを根拠にPASSさせると、読みの正否が検証されない(表記が同じでも読みが違う) | Opus必須1。SPEC L1693「ASR consensus ≠ pronunciation verification」(2026-08-28承認、英語だが原則は共通) | 辞書語は表記一致でなく読み一致(`expected_readings`照合)で判定済み。追加策なし | **A** | 実データでの発火は未測定(Phase 0 fixtureに該当音声なし) |
| X7 | 原稿側diffにラテン文字でSCG不実行(C1c) | 「AI」「FTC」等は表記が同じでも読み(エーアイ/アイ)が一意でなく、Azureの「AI」転写では読みが確定しない | Opus必須1。実測なし | 辞書(`expected_readings`)に登録して読み照合へ寄せる | **A**(暫定。実測根拠は無い) | 実発火データ未確認。Fableが実運用ログで頻度確認できると判断材料になる |
| X8 | 同形異音語候補(C2、SEC L168-180) | 原稿側漢字spanの辞書上の別読み(市場いちば/しじょう等)にPrimary転写側の読みが含まれる場合、Azureが原稿の漢字を転写しても読みの正否が不明 -> 誤PASS(文字は合うが読みが違う) | 2026-10-11 U採用(DL L20550)。実測: g5(名所/旅程)はC2で除外(C群、結果は同じNG) | 辞書補強(OPEN-263: 「行った」[おこなった]が候補に無いと除外されない)=**未承認仕様候補、提案のみ** | **A**(概念)/ 辞書補強は**C** | 合成確認: 「試合に行った->試合を行った」はdiffが助詞でC2非該当。Primaryの同形異音語盲点は既存(PHONETIC_MATCH、SCG以前) |
| X9 | SCG PASSはEXACT/NORMALIZEDのみ(PHONETIC_MATCH不可、SEC L78) | PHONETIC_MATCHを許すと、表記は異なるが読みが同じ別語(同音異義)も通る。ただしPrimary/旧CascadeはPHONETIC_MATCHをPASSにしている(非対称) | ユーザー決定済みの安全条件(DL L20550)。Phase 0: 許すと+3群(g2,g21,g36)、C群誤PASS 0(`ja_offline_replay_01.json`) | 追加Trial不要で再計算済み(CURRENT 13->16)。ただしユーザー決定の見直し=**要ユーザー判断** | **C** | 目標フローで「Secondary一致=PASS」に統一するなら論点。決定済み仕様のため暫定案は変更を推奨しない |
| X10 | UNCERTAIN経路は旧Cascade 4step->HR(再生成しない)(SEC L427-500) | HR行きで人手が必要になる。ASR repeats(Primary#2/Azure#2)は独立性が低い(HR queue 8件で実質同一転写) | ER-007-JA-ASR-TTS-RETRY-PATH-FIX-01(2026-08-25 U、DL L149、SPEC L1993/L1998)。「retryで解決しない可能性が高い」という判断 | 目標フロー: Secondary 1回 -> 両NG -> 再生成(同一Prompt)。Primary#2/Azure#2を廃止 | **C** | 旧承認は「TTS再生成の無駄」を避ける設計。目標フローでは再生成を許す方向で、承認済み仕様の変更になる |
| X11 | 3回目=minimal fallback(style喪失)(N3 L473-、V01 L434-) | 品質への害: J3(role style)がfallback attemptだけ外れ、同一segment内でも音調が変わる。履歴では最終採用7 segment。成功率36.8%(19中7、選択バイアスあり) | ER-003-N3-ROOT-FIX-01(instruction leakage対策、DL L132)、ER-011 25/26(2+1内訳、ユーザー正式決定)、FAMILY-X-02 D-1(JA minimalは既存テキスト流用)。Phase 0標本のminimal attempt 4件は全て不合格 | 3回目も標準Promptで再生成(目標フロー)。leakage再発リスクは未測定 | **C** | ユーザー正式決定の仕様のため、変更はユーザー判断。J2_BRIGHT導入後は喪失がより目立つ |
| X12 | 日本語Local Rewriteなし | 英語は3 attempt後にLocal Rewrite(局所書換)1回で回復 | OPEN-260(OPEN候補・未承認)。Gate7(ASCII語数)が日本語非対応 | 目標フローは「Local Rewrite除外」のため新規必要なし | **B**(統一=除外) | OPEN-260の結論はOPEN-258/本件次第と記載済み |
| X13 | SCG専用`_azure_stt_strict`(旧Cascadeは共通の非strict関数) | 旧Cascadeで途中Errorキャンセル時に部分転写をerror=Noneで受け、誤って一致/不一致判定する可能性(Opus必須2) | Opus必須2(F)。共通関数は無変更の判断 | 旧Cascade側も同じstrictラッパーへ(目標フローで旧Cascadeを廃するなら自然に解消) | **B** | 実害の報告は無い(推測: Azure失敗は稀) |
| X14 | JA HRキューの出力先が英語と別(`er007_output/ja_asr_cascade_01/` vs `er006_output/audio_retry_cascade_prod_01/`) | 運用上の見落とし(2系統) | 既存実装の履歴 | 統合は新仕様のためFable判断 | **B** | 品質より運用 |

## 暫定サマリ(提案、採用はしない)

- **A(維持)**: X1数字、X2否定、X4length_ok、X6辞書読み、X7ラテン、X8同形異音語(概念)。共通フローにも「重大差分はSecondaryで救わない」として残す候補。
- **B(統一可能)**: X5の一般カタカナ・濁点単独(g8)、X12 Local Rewriteなし(=除外のまま)、X13 strict化、X14キュー。
- **C(要判断)**: X3類似度<0.4、X9 PHONETIC_MATCH扱い、X10 UNCERTAIN経路、X11 minimal fallback、X8の辞書補強、X5の最終判断(g8 13/14)。
- 追加根拠が必要なら最小は「濁点最小対Trial(約9〜10円)」と「needs_listen 5音声の試聴(0円)」。
- 気付いた新規仕様候補(**未承認・実装せず**): (i)否定の活用ギャップ補強(来なかった型)、(ii)C1のentity判定を挿入/脱落にも広げる/一般カタカナ語に絞る、(iii)Primary側`entity_like`のカナ率ヒューリスティックの見直し。
