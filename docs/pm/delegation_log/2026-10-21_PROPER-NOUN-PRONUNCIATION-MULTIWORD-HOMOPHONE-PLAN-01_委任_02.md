# 委任文(Fable→sonnet-worker)

## 管理ID
PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01 委任_02(Fable/Opus独立レビューの反映→計画v2完成。**計画のみ。有料API 0・TTS/ASR実行なし・Production変更なし・CURRENT_SPEC/DECISION_LOG変更なし**。オフライン再計測(CMU/保存転写)は可)。
SSOT共有プロトコル: 編集直前`git status --porcelain`+再Grep→自分の行だけ→即add/commit、index.lock 30秒待ち。`git add -f`/`-A`/`-u`禁止。

## 固定ブロック
E-1/D-1/G-1/F-1: 標準(SSOT全文読込禁止)。T-0: 本委任文を`docs/pm/delegation_log/2026-10-21_PROPER-NOUN-PRONUNCIATION-MULTIWORD-HOMOPHONE-PLAN-01_委任_02.md`へ逐語保存(`.venv\Scripts\python.exe docs/pm/tools/extract_delegation_from_jsonl_01.py --jsonl C:\Users\tensh\.claude\projects\C--Users-tensh-eigo-radio\a66c19e8-1d31-4bc4-b0cb-f15b29248dc1.jsonl --role assistant --tool-use-name Agent --tool-input-field prompt --index N --out <path>`、N=「MULTIWORD-HOMOPHONE-PLAN-01 委任_02」を含む最新index)。T-2: TTSなし。費用Guardrail JPY0。

## Opusレビュー結果(OF-PNMH-R-01〜13)とFableの採否
ユーザー§4に従い、各指摘の合理性とQCDをSonnetが評価し、有効な案を計画へ反映する。Fable照合済みの採否は次のとおり(反対する場合は理由を書き、勝手に捨てない)。
- **R-01(高、採用)**: 案Aの連結比較は「ストレス無視」に依存(byus `B AY1 AH0 S` vs buy+us `B AY1`+`AH1 S`はストレス除去でのみ一致)。既存1:1 `homophone_arpabet_equivalent`(`er008_asr_variant_hardening_15_homophone_en.py:89-92`)はストレス付き文字列の集合積=完全一致。「既存と同じ」の記述(DESIGN G7、REVIEW_QUESTIONS:11)は誤りなので訂正し、「連結比較に限りストレス無視」をCURRENT_SPEC:1839からの緩和=**ユーザー判断事項(U2に含める)**として明示。一般語461組を「ストレス込みでも一致/ストレス除去で初めて一致」に分けて件数を出す(オフライン、0円)。
- **R-02(高、採用)**: CMU `bi`=`B AY1`のため canonical `bias`⇔ASR `Bi-us`が案Aで同音扱いになる。CURRENT_SPEC:454は`BAUS`/`Bi-us`を「実音声の誤発音、引き続きNG」と記録(runtime evidence `docs/research/FAMILY-XZ-ASR-MULTI-DIFF-JUDGE-FIX-01/runtime/runtime_evidence_x.json`)。ケース表に`bias`→`bi us`を追加し、CURRENT_SPEC:454との衝突を明記。期待ラベルは**ユーザー判断**(「音節を区切ったが音素は同じ読み」を合格にするか)。許容しない場合の対策案(複数語側各tokenをCMU代表発音に限定/G4を2文字以下に強化)を比較し、副作用を保存データで0円計測。
- **R-03(中、採用)**: 多語spanはCase A(代表発音のみ)が語数不一致で必ず失敗し(`hp:145-146`)、`_step_alternate_pass`の全variant一致へ流れる(`sec:592-595`)=固有名詞にD-2'で不採用とした基準を通る。設計に「canonical側がentity_likeのとき代表(先頭)variantのみ」を入れ、一般語も代表variant限定可能かを461組で計測。`Tse`→`sea`(`S IY1`一致)を既存の穴候補として実測し報告(是正はしない)。
- **R-04(中、採用)**: 「下流無改変」は「下流コード無改変・判定挙動の変化は次の4点」に書き直し、各点をケース表とunit test計画に追加: (a)数字ゲート例外(`val:834-838`、`HOMOPHONE_MATCH_NUMBER_EXCEPTION`即PASS)、(b)M1のSecondary矛盾拒否が働かなくなる(`er006_m1_multi_candidate_01.py:511`)、(c)connected-speech/F1経路の迂回(`val:1119-1162`、固有名詞差分混在でUNCERTAIN→cascade対象外。PASS→NGも理論上あり得る)、(d)F1残差判定は1:1限定のまま(`val:1008`)。
- **R-05(中、採用)**: O0再適用対象に`docs/research/**/runtime*`、`human_review_queue.jsonl`(er006/er007)、MDJF golden 193件を追加して再実行(0円)。`Bi-us`が含まれることを確認。
- **R-06(中、採用)+R-07(低、採用)**: P1を約12〜16本に縮小(F1・F2・F3・F4・F5・F7・F9・`bi-us`型、声1×carrier1、F3/F4のみ声2)。あわせて「run_byus_01の既存wavを確定ASR構成で再ASR(TTS 0円)」を計画に入れる。Cap案はJPY50。O1(3)「1音素摂動の負例バンク」は完全一致規則に対し必ず合格するため削除し、代わりに「代表以外のvariantでのみ一致/ストレス除去でのみ一致/stopwordのvariant(a=EY1、the=DH IY0等)経由で一致」する組を列挙して目視レビュー対象にする(0円)。
- **R-08(低、採用)**: B2の詳細(Tier表・negative cache TTL90日・T2b・P2)は今回の確定範囲から外し、「#133判断後の別計画」として骨子のみ残す。U6/U7のうちB2関連は削除。
- **R-09(低、採用)**: `er006_multi_diff_judge_fix_test_01.py:153`のkey集合完全一致testの改訂要否、監査用の生span+一致発音の記録、追加keyの付け方(常に/条件付き)を計画に明記。
- **R-10(低、Fable要照合→Sonnetが調査)**: CURRENT_SPEC:1839は「Secondary(または2回目のASR)側が(a)canonical文字一致または(b)ARPAbet完全一致を満たした場合のみPASS」と規定。一方コードはPrimary単独の`cmu_alternate`即時PASSが成立するとOpusが指摘(`sec:942-951`。委任_07でもpart1 att3はPrimary `Byus`のcmu_alternateで採用)。**どちらが有効な承認仕様か**をDECISION_LOG/CURRENT_SPECのGrep(`cmu_alternate|HOMOPHONE_EQUIVALENT|unified judge|AUW|Primary単独`)で特定し、(i)1839が後続決定で置換済み(出典行)/(ii)仕様とコードの不一致(11-8候補)/(iii)判定不能、のいずれかを事実で報告。コードは変更しない。新ルールでは「既存とのズレに上乗せしない」方針を計画に書く。
- **R-11(低、採用)**: 「CSパターン(ユーザー決定の3パターン、`val:1126-1131`)の拡張ではなく同音判定入口の一般化」であることを1行明記。
- **R-12(低、採用)**: G4は残す(強化はR-02の計測結果で判断)。O1(2)「DefaultOffIsolation型」testの表現を削除/言い換え(11-7 flagは使わない方針)。DESIGN 4-2の`by us`「救済」は既存の空白差規則で吸収される旨に訂正。層A/B/C分離報告とA5反復は維持。
- **R-13(低、採用)**: 既知の救済漏れ(2:2 span、F1残差1:1限定、固有名詞差分混在時のcascade対象外)を「対応不要の安全側の漏れ」として明記。
- 追加(採用): 「ASR構成変更時に再評価が必要な部分」6点(エンジン別多語化率/表記の癖[ハイフン・音節区切り]/Phrase List・promptの綴り誘導[K5型]/Secondary許容判定も同規則`sec:993-1002`/KPと本文で構成が違う場合の別集計/M1矛盾拒否の頻度)をTRIAL_PLAN §8に反映。
- Fable補足: 価値は予防(保存転写3,493中4件・1記事由来)。計画・Trialの分量を必要十分に縮め(Charter原則1)、ユーザー判断事項は「新仕様の採否に本当に必要なもの」だけに絞る。

## 作業
S1. 上記を反映して4文書をv2へ改訂(変更箇所をfile:行で列挙)。オフライン再計測(R-01の461組分割、R-02の対策案副作用、R-03の代表variant限定効果とTse→sea、R-05の拡張再適用、R-07の列挙)を実行し結果jsonを保存。
S2. `PLAN_SUMMARY_01.md`(ユーザー§7の1〜11の順、各項目5行以内、ユーザー判断事項は次に絞る: U2 案Aの採否[ストレス無視・1:n/n:1・n≤3を含むCURRENT_SPEC:1839の拡張]、`Bi-us`型の合否ライン、U1 適用範囲[推奨初期値=全語+entity_likeは代表variant限定]、U7 有料Trial実施とCap[新仕様Trialのため金額によらず承認]、既存の穴[AI→eye/us→u s/am→a m/Tse→sea候補]を扱うか、未回答のJ7・#133・#134・GitHub Issue #133本文は「未回答のまま進める確認」のみ)。
S3. Opus指摘をOPUS_FINDINGS_LEDGERへOF-PNMH-R-01〜13として登録(処置付き)。OPEN-439: Status `PLAN_V2_PENDING_USER_FIX`、依存=ASR-THREE-WAY(OPEN-438 UDR #136)とPrimary/Secondary確定。USER_DECISION_REGISTERに **#137**(本計画のFixと上記判断事項、Fable推奨: 案A採用方向で計画Fix、適用範囲=全語+entity_like代表variant限定、Bi-us型は「不合格維持(CURRENT_SPEC:454整合)」を推奨初期値、有料TrialはASR確定後にCap JPY50で承認を求める)。REPORT_LEDGER 1行、ACTIVE_TASK(ローカル)。
S4. secret scan→明示add→commit→`git push origin HEAD:main`。

## 報告(docs/pm/RESULT_PACKET_PNMH2.md 上書き): 反映一覧(指摘ID→変更箇所)、R-10の調査結果(i/ii/iii+出典行)、再計測の数値(461組分割、Bi-us対策案の副作用件数、代表variant限定の影響件数、Tse→sea実測、拡張再適用の結果)、P1縮小後の本数と見積、commit hash、push確認。