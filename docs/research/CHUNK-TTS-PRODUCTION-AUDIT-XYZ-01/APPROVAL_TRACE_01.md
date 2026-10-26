# APPROVAL_TRACE_01 — Chunk分割+0.2秒ポーズ: ユーザー承認原文とStandard/Advanced適用範囲の照合(read-only、API 0)

管理ID: CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01 委任_01(2026-10-26)。表記: 引用は逐語。出典は`file:line`。判定語彙はPM_GOVERNANCE 11-8/27-3。

## 結論(先に)
1. **Standardを対象外にする明示のユーザー承認は存在しない。同時に、Standardを対象に含める明示のユーザー承認も存在しない**(Chunk方式の承認原文10件を全件Grep)。Standard除外は、ユーザーの「未承認の対象拡大を行わない」指示(下記E4)を受けた**Fable委任文+Sonnet Phase 0設計の解釈**(根拠=6%減速との相互作用が未Trial)で入った。Opus指摘由来ではない(`docs/pm/OPUS_FINDINGS_LEDGER.md` Grep `chunk`=0件、`OPUS_REVIEW_01.md`にStd除外の指摘なし)。
2. 但し「ユーザーが対象外にする指示をしていない」と「承認済み仕様どおり」は両立しない余地がある: ユーザー自身が承認時に **Trialは『Advancedのみ』**(E1,E2)、Production配線時に **『未承認の対象拡大を行わない』『Standard/Advancedの適用範囲は承認済みTrial条件と既存仕様を照合』**(E4)、Z最終版で **『Standardは承認済み仕様どおり維持する』**(E6)と書いている。よって**承認記録は曖昧(Std含意なし/除外含意あり/明示除外なし)**で、2026-10-26のユーザー原文(Std/Adv双方を意図)は**新しい意図表明**として扱う。
3. 結果として是正許可条件(a)(c)が成立せず、**自律是正は実施しない**(`FIX_01.md`)。判断候補として報告する。

## 承認原文(逐語) — Family×レベルの適用範囲に関わる全件
| ID | 日付・出典 | 逐語引用 | Std/Advへの含意 |
|---|---|---|---|
| E1 | 2026-10-25 `docs/pm/delegation_log/2026-10-25_FX-PARAGRAPH-CHUNK-TTS-TRIAL-01_USER.md:31` | 「レベル：**Advancedのみ**」(Family X『英国の電車マナー』段落単位Chunk Trial。:33「Trial方式：本文1・2・3の内部を段落単位でChunk分割」、:34「Production変更：禁止」[:34]) | X Trialの対象はAdvancedのみ(ユーザー指定) |
| E2 | 2026-10-25 `…/2026-10-25_FX-FZ-CHUNK-TTS-TRIAL-02_USER.md:23` | 「対象：『英国の電車マナー』Advanced本文。」(X 0.2秒版B0.2。Z B_r1 Trialは:44-59、level明記なし=実Trial成果物はAdv `tth_*_adv`) | X B0.2のTrial/試聴はAdvanced |
| E3 | 2026-10-25 `…/2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_USER.md:5-10` | 「X／ZのTTS Chunk分割について、試聴結果を踏まえ、以下の2方式を**正式採用（APPROVED_FOR_PRODUCTION）**します。」 X=「段落分割＋0.2秒追加ポーズ（Trial B0.2）」 Z=「B_r1：約70語を目安とした段落境界分割＋0.2秒追加ポーズ」 | 方式の正式採用。レベルの記述なし |
| E4 | 同 `:24`(X)・`:32`(Z) | 「Standard／Advancedへの適用範囲は承認済みTrial条件と既存仕様を照合し、**未承認の対象拡大を行わない**。」「Standard／Advancedへの適用範囲も、承認済み仕様と照合する。」 | **レベル適用範囲は『Trial条件との照合』に委ねられ、拡大禁止**。Std含意/除外のどちらも明記せず |
| E5 | 同 `:62`(§5 STOP) | 「採用済みの分割方式・ポーズ時間・適用対象の変更が必要になった場合」はユーザー判断へ | 適用対象の変更は判断事項 |
| E6 | 2026-10-25 `…/2026-10-25_FZ-TELL-TALE-HEART-CHUNK-FINAL-01_USER.md:13-14,48-49` | 「Family Z B_r1（約70語目安のChunk分割＋0.2秒ポーズ）」「既存のStandard／Advancedの音声・品質仕様」/「2. Advancedの対象箇所にB_r1が適用されている。」「3. **Standardは承認済み仕様どおり維持する。**」 | Std除外の報告(DECISION_LOG:22394)後の指示。Std維持と読める(但しChunk非適用を明示承認した文言ではない) |
| E7 | 2026-10-25 `…/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER_02.md:13-25` | 「**Family X方式（段落分割＋0.2秒ポーズ）をFamily Yに正式採用する。**…既存のX方式を最大限再利用する。…セリフや話者の切替を不自然に結合・分割しない。事前の追加Trial・ユーザー試聴承認は不要。…今回の承認はX方式のY適用であり、ZのB_r1方式は採用しない。」 | **Std/Advの記述なし**。『X方式』の中にレベル範囲を含めるかは未定義 |
| E8 | 同 `:148` | 「5. X方式Chunk分割＋0.2秒ポーズがYで機能する。」 | 受入条件(レベル指定なし) |
| E9 | 2026-10-25 `…/2026-10-25_FAMILY-Y-PRODUCTION-LAUNCH-01_USER.md:231` | 「音声Chunk分割・ポーズ仕様の適用要否」(Phase 0で判断を求めるべき確認項目の列挙) | 適用要否のみ。レベル言及なし |
| E10 | 2026-10-26 `…/2026-10-26_CHUNK-TTS-PRODUCTION-AUDIT-XYZ-01_USER.md:25-31` | 表「X 段落境界分割（Trial B0.2）0.2秒 Standard／Advanced / Z …B_r1 0.2秒 Standard／Advanced / Y X方式を導入 0.2秒 Standard／Advanced」「**ユーザーはStandard／Advancedの一方を対象外にする指示をした認識がありません。**」 | 今回の**新しい意図表明**(Std/Adv双方)。過去承認の再解釈であって、Std含意を示す過去原文は上記に無い |

## Standard除外の出所(Family別、時系列)
| Family | 出所 | 内容(出典) | 分類 |
|---|---|---|---|
| X | Fable Phase 0委任文 | 「適用範囲: X=Trial条件(Advanced=b1b…)と既存仕様を照合し**未承認の対象拡大なし**(Standard(A2、6%減速あり)への適用はTrial未検証=対象外として明記)」(`docs/pm/delegation_log/2026-10-25_FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01_DELEGATION_01.md:8`) | **Fable設計判断**(E4の解釈) |
| X | Sonnet Phase 0設計 | 「X Standard(a2)本文 | 対象外(生成後6%減速post-process…との相互作用が未Trial)」(`docs/research/FX-FZ-CHUNK-TTS-PRODUCTION-WIRING-01/EXISTING_SPEC_CHECK_01.md:116`)、「Std(a2)本文は非適用…理由=生成後6%減速とchunk別生成の相互作用が未Trial(Fable委任文、ユーザー決定の「未承認の対象拡大を行わない」)」(`WIRING_DESIGN_01.md:117`) | 設計判断(+実装都合=6%減速との合成が未設計) |
| Z | 同上 | 「Z Standard(a2) narrator | 対象外(6%減速…・verify_std_english_slowdownとの相互作用が未Trial)」(`EXISTING_SPEC_CHECK_01.md:120`)。実装は`er117_chunk_tts_production_01.py:143-144` `level != "b1b"`→`reason="level!=b1b(Std対象外…)"` | 同上 |
| X/Z | SSOT | `DECISION_LOG.md:22394`(「対象外=Standard(6%減速との相互作用が未Trial)・Dialogue・短narrator・KP・Y」、委任_01記録)、`CURRENT_SPEC.md:2936,2939`(節題「Family X・Z Advanced…」、「対象外: Standard(a2)…」) | SSOT記載。ユーザー承認原文の引用ではない |
| Y | Sonnet設計(YPL) | 「level: Adv(b1b)本文のみ(X同様。Std[a2]は非chunk)」(`docs/research/FAMILY-Y-PRODUCTION-LAUNCH-01/DESIGN_02.md:211`)、実装`er121_family_y_structure_01.py:111` `CHUNK_TTS_Y_LEVELS = ("b1b",)  # X同様Advanced(b1b)本文のみ`、`er121_family_y_audio_01.py:309` `not_applied_reason = "Std(a2)本文はX同様chunk化しない"` | **Xからの継承**(E7に『X方式』とだけあり、Xの運用上のレベル範囲をそのまま移植)。YでStdを除外する独自根拠はない。Phase 0時点でもDESIGN_01.md:83「Chunk分割は非適用(YL-B08判断待ち)」 |

## 4つの問いへの答え(ユーザー原文§3-④に対応)
1. **なぜYのStandardが除外されているか**: X方式をYへ『再利用』する際、Xの適用範囲(Adv本文のみ)をそのまま移した(`DESIGN_02.md:211`、`er121_family_y_structure_01.py:111`)。USER_02(E7)にレベル指定は無く、Yで固有にStdを除外した根拠はない。
2. **X自身もStandard対象外か**: **はい**。`er117_chunk_tts_production_01.py`はX Std(a2)に呼ばれない(`er019_family_x_audio_production_runner_01.py:1443-1547`はb1b生成関数内のみ。`generate_family_x_a2_segments`[:1743]にchunk経路なし。test `er117_x_chunk_wiring_test_01.py:194-202` `test_std_a2_path_untouched_no_chunk_ids`が固定)。Zも同様(`er117_chunk_tts_production_01.py:143-144`、`er117_z_chunk_wiring_test_01.py:130-132,202`)。
3. **Yへの移植時だけ除外されたか**: いいえ。X/Zで最初に(2026-10-25 Phase 0)入り、Yが継承。
4. **承認履歴に根拠があるか**: 明示根拠なし(上記E1〜E10)。間接的根拠は E1/E2(Trial=Advancedのみ)+E4(未承認の対象拡大を行わない)+E6(Std維持)。これを『除外の承認』と読むのか『Std含意なし』と読むのかが曖昧。
5. **不一致の場合の影響範囲と是正方法**: `RUNTIME_EVIDENCE_01.md`・`FIX_01.md`参照。要点: (i) X Std本文は3 part(123〜170語、3段落)が各1 callのまま、(ii) Z Stdはnarrator 122〜139語clip(tell_tale part2/3、melos part2、gift_of_the_magi part1)が1 callのまま(Advでは同規模がchunk化される)、(iii) Y Stdは**拡張しても1段落契約のため分割は発火しない**(Adv同様)。是正はStd用の『減速との合成』設計(下記)が必要で新規設計。

## 当初仕様と実装仕様の食い違いの原因(整理)
- 原因1(承認文面): Trialが『Advancedのみ』で実施され(E1,E2)、正式採用文(E3)がレベルを明示せず「適用範囲は承認済みTrial条件と照合」(E4)とした。
- 原因2(解釈): 『Trial条件=Advanced』『Stdは6%減速post-processあり=相互作用未Trial』と解釈され、Std除外が設計に入った。ユーザーへ個別のStd除外承認は取っていない(DECISION_LOG:22394は報告記載であり、承認項目としては提示していない)。
- 原因3(SSOT表記): `CURRENT_SPEC.md:2936`の節題が「Family X・Z **Advanced**…」であり、ユーザーが見たとき『Advancedのみ』が目立つ形になっていた。
- 原因4(Y移植): 『X方式を最大限再利用』(E7)に従いXの範囲ごと移植。さらにYは1段落契約(`er121_family_y_text_core_01.py:175,1266,1494`)のため、レベルに関係なく不発火(DECISION_LOG:22449、OT-42)。
