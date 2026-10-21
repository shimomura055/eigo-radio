# 委任文(Fable→sonnet-worker)

## 管理ID
ASR-THREE-WAY-COMPARISON-TRIAL-01 委任_02(Fable/Opus独立レビューの反映: 結果文書の是正7点+Opus指摘のLedger記録+費用0のオフライン追加集計(C5K発動率)+Fable判定のSSOT記録。**有料API 0・TTS/ASR実行なし・Production変更なし**)。
並行agent: `PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01`(docs/research/PROPER-NOUN-...配下とOPEN_ITEMS新規行を編集しうる)。SSOT共有プロトコル: 編集直前`git status --porcelain`+再Grep→自分の行だけ→即add/commit、index.lock 30秒待ち。`git add -f`/`-A`/`-u`禁止。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準(SSOT全文読込禁止)。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_ASR-THREE-WAY-COMPARISON-TRIAL-01_委任_02.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「ASR-THREE-WAY-COMPARISON-TRIAL-01 委任_02」を含む最新index)。T-2: TTSなし。費用Guardrail JPY0。

## Opus独立レビュー結果(OF-ASR3W-R-01〜16。全文は本委任文の末尾「Opusレビュー原文」。`docs/pm/OPUS_FINDINGS_LEDGER.md`へ既存書式で16件を登録し、各件の処置[反映済み/未検証事項として記載/却下+理由]を書く)
Fableの採否(Opus案をそのまま採用せず照合した結果):
- 採用(結果文書へ反映): R-01(構成音声は全方式検出→構成間を区別しない注記、「誤PASS率11%」「KP問題0/6」を実運用率のように示さない)、R-03(正常母集団の生存バイアス=現行Primary通過音声に偏る、HR難例は逆方向)、R-05(1試行あたり3/10と、再生成ループ込みKP単位の見逃し[最大4回で上限目安1−0.7^4≈76%、未実測]を区別。HR到達期待は上限側も併記)、R-06(本文Phase 3は`segment_id=None`でTier1 role gating/Tier3未発火+CS Equivalence全件有効+max_len近似→本文の構成比較と「本文Mullos 2/12」は参考値に格下げ)、R-08(C5KのWhisper費用はほぼ0: KPは`disfluency_qa=True`既定でverified時にWhisper smallが既に走る。C5Kの原価・時間を再計算。順序組替えが必要な点を明記)、R-09(C1dKはAzure可用性にKP全件が結合、障害時fail-closed=`NG_SECONDARY_UNAVAILABLE`→circuit breaker→技術STOP。頻度は過去telemetryから集計できれば記載、無理なら未確認)、R-10(KPにPhrase Listが付く場合の拒否権骨抜きリスク=未検証事項・Offline Trial必須項目)、R-12(C1dK実装時の変更範囲5点、C5Kは+順序変更+Whisper正規化規則)、R-13(追加検証の推奨順①′費用0→①″約30円→②聴取→③Offline Trial。新規TTS人工音声の追加は費用対効果低)、R-14(Mullos→Melosは既知OPEN-426の独立再現。安全網=PASS_WITH_WARNING+事後試聴リスト。KP限定案では本文のこのリスクは解消しない。事後試聴の運用実態は未確認と明記)、R-15(OpenAI prompt有無の差はprior補正と無関係=非ラテン文字抑止とみられる、未確認)、R-16(Whisper二重空白の原因=`" ".join`、C5Kで使うなら正規化明文化)、CURRENT_SPEC参照行2808→正しい行へ(再Grepで「Primary PASSならSecondary不要」の正本行を特定し修正)。
- 記載のみ(低): R-02(循環の程度・`make rewards smaller`の疑義・`sentence someone to death`過剰NGの真偽未確認→聴取対象に)、R-04(tags固有名詞判定は参考値)、R-07、R-11(PASS_WITH_WARNING増の件数未確認)。
- Fable補足(Opusと一致): C1dK/C5KはC1のPASS集合の部分集合(`er078_asr_unified_judge_01.py:438-441`)なので誤PASSは構造上増えない=この点だけは統計不要で確実。「最有望」は「方向は確実、量は未確定」と言い換える。

## 作業
S1. `TRIAL_RESULT_01.md`を是正(上記採用項目。§1結論を「方向は確実、量は未確定」に改め、§8「Fable独立評価」欄にFable判定文[下記]とOpus指摘IDの要約を記入、§9/§10を推奨順①′→①″→②→③に合わせて更新)。`RESULT_TABLES_01.md`のC5K行を再計算。変更箇所はfile:行で列挙。
S2. **費用0のオフライン追加集計(R-13 ①′)**: 過去のProduction KP(Family X/Zの完成記事run配下 `attempts_log`/audit の `disfluency_evidence` にWhisper転写、Primary転写はaudit/telemetry)から、「Primary PASSかつWhisper転写が内容語で不一致」=C5Kなら Azure必須になる件数/全KP件数を集計し、`KP_TAKE_PART_INVESTIGATION_01.md §5`の「EN 333件中29件」と突合。Whisper転写が保存されていなければ「保存なし(file:行)」と報告して打ち切る(探索は30分相当を上限、再実行はしない)。結果は`OFFLINE_C5K_TRIGGER_RATE_01.md`。
S3. Fable判定のSSOT記録:
 - OPEN-438: Status `TRIAL_DONE_PENDING_FABLE`→**`USER_DECISION_REQUIRED`**。Fable判定文(逐語): 「Trialは完走(費用JPY45.1、Production変更0)。得られた確実な結論=(1)現行C1の見逃し機構はPrimary(OpenAI)の言語prior補正+Primary PASS即PASSに起因(take part実音声1本・10回で3/10、再生成ループ込みでは上限目安76%・未実測)、(2)KP限定でAzure拒否権を足す構成(C1dK/C5K)はC1のPASS集合の部分集合で誤PASSを構造上増やさない、(3)Primary入替(Azure/Whisper)が現行を上回る証拠なし(Azure Primaryは原価約3倍+Phrase List誤PASSをPrimary段で通す、Whisperは容量由来誤り/CPU負荷)。量(過剰NG率・HR到達率)は正常母集団の生存バイアスとn=28のため未確定。Production構成の変更は新仕様(CURRENT_SPEC「Primary PASSならSecondary不要」の例外)でありユーザー判断。推奨=採用判断の前に費用0〜約30円の過去Production KP全件再評価(①′/①″)。VALIDATEDは付与しない(ランキング不成立)。」
 - `docs/pm/USER_DECISION_REGISTER_01.md`に **#136**: 件名「ASR構成(KP限定Azure拒否権 C1dK/C5K)のOffline Trial次段階化と、その前段検証(過去KP全件再評価 約JPY30)の実施可否」、選択肢(ア)前段検証①″(約JPY30)+聴取②を実施してからC1dK Offline Trial可否を再判断[Fable推奨: 理由=誤PASSを増やさない構造が確実な一方、過剰NG/HR/Azure障害結合の量が未確定で、約30円で実分布が測れる]/(イ)前段検証を省きC1dK Offline Trialへ/(ウ)現行維持(KP4是正で個別対処)。付記: Primary/Secondary入替は進めない推奨(証拠なし・原価3倍)。Mullos→Melos型(OPEN-426)の事後試聴リスト運用実態の確認を別件として提示。Status未決。
 - REPORT_LEDGER 1行、ACTIVE_TASK(ローカル)。
S4. secret scan→明示add→commit→`git push origin HEAD:main`。CURRENT_SPEC/DECISION_LOGは変更しない。

## 報告(docs/pm/RESULT_PACKET_ASR3W2.md 上書き、短く): 是正箇所一覧(file:行)、C5K再計算値、①′集計結果(件数/分母/根拠path、または保存なしの事実)、Ledger登録ID範囲、commit hash、push確認。

## Opusレビュー原文(Ledger登録用、逐語)
[結論] Sonnetの推奨(KP限定でAzureに拒否権)に条件付き賛成。C1dK/C5KはPrimary PASSをさらに絞るだけなので誤PASSがC1を上回らないことは構造上保証。効果の大きさの根拠は実音声1本、代償(過剰NG/HR)の根拠は正常KP n=28(現行パイプライン通過音声に偏る)。「最有望」は「方向は確実、量は未確定」。見落とし: (a)再生成ループ(KP最大4回)が「PASSが出るまで引き直すくじ」として働くためKP単位の見逃しは過小評価。(b)Primary PASSのKP全件に吃音QA用Whisper smallが既に走っており、C5Kの追加計算はほぼ0、過去記録で費用0の事前検証が可能な可能性が高い。品質優先ならC1dK(拒否が厳密・構造単純・費用差1円未満)、C5Kは後退案。
OF-ASR3W-R-01(高) 人工の問題音声は「ASRの言語priorによる補正」という失敗の型を代表していない。TTS構成のKP問題5本は全方式・全構成で検出(RESULT_TABLES G-1:159-169、G-2)。C1とC1dKの差を生んだ問題音声はtake part実音声1本のみ(§I:338-345)。推奨: 「KP問題 誤PASS 0/6」「全体誤PASS率11%」を実運用の見逃し率のように示さない。
OF-ASR3W-R-02(中) 循環: 構成ラベルの確認はASR転写との整合(TRIAL_RESULT §8:70)→「ASRに聞こえる誤り」だけが残る選択効果。`make rewards smaller`は複数形差で検出された可能性(DATASET B:32)。正常ラベルは記事単位(DATASET_01:4)。`sentence someone to death`→Azure「Sentenced」は過剰NGか正しい検出か未確認。推奨: 過剰NG音声と方式間不一致の正常音声だけ聴取で確定。
OF-ASR3W-R-03(高) 正常母集団の生存バイアス: 正常KP28・通常本文24は当時のPrimary系判定を通過した音声。C1の過剰NG 0/28・0/24は構造的に出やすい。HR難例は逆にOpenAI Primaryに不利。推奨: 偏りを併記、C1dKの1/28は過小/過大どちらの可能性もあると書く。
OF-ASR3W-R-04(低) 通常/HR難例の分離集計(G-4:298-310)は適切。tagsの固有名詞判定は文頭語を過剰に拾う(DATASET_01:5)ため参考値。
OF-ASR3W-R-05(高) 再生成ループによる見逃し増幅が未評価。KPはMinimal2+English Lock2=最大4回(`er003_v1_repro01_main_generate.py:810-830`)、本文も両NGなら再生成(CURRENT_SPEC.md:2818)。同型の誤発音を繰り返す場合、p=0.3のPrimaryでKP単位の見逃しは最大1−0.7^4≈76%(未確認)。Phase 3の1 attempt評価は現行リスクを下限側で見ている。C1dKの過剰NGは再生成で吸収されやすいが、Azureが決定論的に同じ誤認識をする語では4回とも落ちHR到達。表HのHR到達期待0〜0.36は後者では上限側が現実的。
OF-ASR3W-R-06(中) 本文Phase 3はProductionと条件不一致: `segment_id=None`固定でTier1 role gatingとTier3(Azure裏付け救済)が未発火(`er006_secondary_asr_01.py:855`)。CS Equivalence層を本文全件で有効(`phase3.py:74`、ProductionはA2/B1本文限定)、`max_len`近似(`phase3.py:70`)。KP結論には影響なし。本文の構成比較と「本文Mullos 2/12」は参考値に格下げ。
OF-ASR3W-R-07(低) Whisperの二重空白除去が全方式転写に適用(`phase3.py:95`)。OpenAI/Azureへの影響は実質なしとみられる(未確認)。
OF-ASR3W-R-08(高) C5KのWhisper費用はほぼ0: KPは`disfluency_qa=True`既定(`er003_v1_repro01_main_generate.py:782`)、吃音ゲートはverified=True時のみWhisper small実行・transcript記録(`er008_disfluency_qa_18.py:108-117,89`、呼出`er003_v1_repro01_main_generate.py:369`、記録`attempts_log.disfluency_evidence`)。C5Kの発動条件と一致、Trialも同関数(`er091_..._run.py:5,166`)。「CPU1.5秒/KP、+17CPU秒」は追加費用ではない。過去KPのWhisper転写が保存済みの可能性(未確認)。実装は判定後に吃音ゲートが走る順序の組替えが必要。
OF-ASR3W-R-09(中) C1dKではKP全件のPASSがAzure可用性に依存。障害時`NG_SECONDARY_UNAVAILABLE`→circuit breaker→技術STOP(`er078...:464-507`)。現行はOpenAI単独でPASS可。推奨: 障害時挙動と頻度を明示。
OF-ASR3W-R-10(中) KPにPhrase Listが付く場合、拒否権が骨抜きになる可能性。データ中KPはPL 0件(RESULT_TABLES A:13)。固有名詞KPに将来Ledger hintが付くとAzureは重み2.0で正解綴りに引き寄せられMullos型と同じ。拒否権呼出だけPLなしにする案はPLなし正常PASS21%(RESULT_TABLES D:115)で過剰NG増。推奨: 未検証事項・Offline Trial必須項目。
OF-ASR3W-R-11(低) force_secondary受理時にM1/CMU経由だと`PASS_WITH_WARNING`→事後試聴リスト増の可能性、件数未確認。
OF-ASR3W-R-12(中) 「Primary PASSならSecondary不要」の正本はCURRENT_SPEC.md:2818(依頼文の2808はM1の節で誤記)。C1dK実装時: (1)CURRENT_SPEC:2818にKP例外追加=新仕様、(2)KP経路への`force_secondary`受け渡し新設(`er003_v1_repro01_main_generate.py:356-366`は未受け渡し、既存用途はfallback音声のみ`er003_v1_crosslevel_audio_02_common.py:374-381`)、(3)Family X/Z runner共通KP経路への波及、(4)HR package step名`secondary_forced`の意味拡張(`er006_secondary_asr_01.py:988`)、(5)承認前配線なら既定OFF flag隔離ルール。C5Kは+吃音ゲート順序変更+Whisper転写正規化規則新設。
OF-ASR3W-R-13(高) 最も安く決定的な検証=過去Production KP全件の再評価。①′費用0: attempts_logのPrimary転写と吃音QAのWhisper転写でC5K発動率をオフライン集計、EN333件中29件と突合。①″約JPY30: 過去Production KP全件(数百本)にAzure1回ずつでC1dK拒否件数を実分布で測る。②聴取: ①′/①″の拒否・不一致音声+本Trialの過剰NG・不一致音声(sentence/weaken/far bank)に絞る。③C1dK Offline Trial(再生成ループ・HR到達・Azure障害・PL付きKPを含む)。新規TTS人工音声の追加はR-01の理由で費用対効果低。
OF-ASR3W-R-14(中) Mullos→Melosは既知リスクの独立再現、新事実ではない。OPEN-426記録済み、安全網=`PASS_WITH_WARNING`+事後試聴リスト(OPEN_ITEMS.md:938、CURRENT_SPEC:2818)。伝えるべきは「本Trialでも再現」「安全網は事後試聴が実施されて初めて効く(運用実態未確認)」。KP限定案では本文のこのリスクは解消しない。
OF-ASR3W-R-15(低) OpenAI prompt有無の差(23/28→28/28)はprior補正と無関係。KP用promptは英語で書かせる指示のみで正解テキストを含まない(`er003_v1_repro01_main_generate.py:771-775`)。差の5件は非ラテン文字出力の抑止とみられる(未確認)。
OF-ASR3W-R-16(低) Whisper二重空白は吃音QAの単語を`" ".join`で連結していることが原因(`er008:89`)。C5Kで内容比較に使うなら正規化の明文化が必要。
[ユーザー判断前に修正すべき点] 1.R-01注記 2.R-05の区別 3.R-03生存バイアス追記 4.C5K原価・速度再計算 5.R-06明記・本文比較参考値化 6.判断候補Aの前段にR-13①′/①″提示 7.CURRENT_SPEC参照行2808→2818。
[ユーザーに伝えるべき新事実] take part型見逃しは再生成のくじ引き効果で1試行30%より高くなり得る(上限目安76%、未実測)/KP限定拒否権は構造上誤PASSを増やさない、代償は過剰NG・HR増・Azure障害時KP停止、その量は過去KP全件で安く測定可/吃音QA用WhisperがPrimary PASSのKP全件で既に動いているためC5Kはほぼ追加費用なしで実装・検証できる可能性/Mullos→Melos型は既知(OPEN-426)で今回も再現、安全網は事後試聴なので運用実態確認が必要、KP限定案では解消しない/Production採用可否はユーザーのみ。