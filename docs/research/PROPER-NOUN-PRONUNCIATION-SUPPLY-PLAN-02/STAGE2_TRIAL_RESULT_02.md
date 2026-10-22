# STAGE2_TRIAL_RESULT_02: 固有名詞発音 Stage 2 Trial 第2巡(Opus Step B 案1)結果(ユーザー§7の順)

管理ID: PROPER-NOUN-PRONUNCIATION-SUPPLY-PLAN-02 委任_08 / 2026-10-22 / 到達Status: `TRIAL_R2_DONE_PENDING_FABLE`(`VALIDATED`/`REJECTED`/`USER_DECISION_REQUIRED`はFable判定)。Production・正式Ledger・HR queue・Master Audio Store・Validator・Prompt・モデル構成 無変更(生成前後でsha256・行数不変を自動assert済み)。
設計=`STAGE2_TRIAL_DESIGN_02.md`。証跡=`er100_output/pnps_stage2_trial_01/r2/`(`agg.json` `replay_stored.json` `plan.json` `gen_*.json` `paid_calls.jsonl`)。試聴ページ=https://shimomura055.github.io/eigo-radio/user_test/pnps_stage2_hr7_listen_02/index.html

## 1. 結論: Human Reviewを何件削減できたか
**効果基準(現行TTSでHRになる独立segmentの40%以上がPASS_WITH_WARNINGへ)は未達。現行TTS実測で 0%(0/25)。hard基準(誤PASS 0、Khaite「kite」NG維持、Production無変更)は満たした。**

| 区分 | 母数 | 現行基準でHR | 新arm(N5_UND)でPASS_WITH_WARNING | NG | 判定不能(HR維持) |
|---|---|---|---|---|---|
| 現行TTS実測 take1(独立30 segment) | 30 | **25**(プロキシ) | **0**(0%) | 15 | 10 |
| 現行TTS実測 take2(16 segment再生成) | 16 | 12 | 2(s12・s16、いずれもKhaite) | 5 | 5 |
| 現行TTS実測 全46音声 | 46 | 37 | **2**(5.4%) | 20 | 15 |
| 保存データ(旧TTS世代、HR事象58) | 58 | 58(定義上) | 1(Khaite・音声未保存で確証なし) | 16 | 41 |
| 保存データのうち単体テスト混入(§付録(b))を除く実質 | 33 | 33 | 1 | — | — |
| 保存attempt音声(旧TTS、Production不合格74語ペア) | 74 | 74 | 3(Khaite、Whisper不一致の要試聴) | 35 | 36 |

- 「現行基準でHR」は**プロキシ**: PrimaryまたはAzureが対象語を正しい綴りで返せばProductionは通る、とみなして再現(実判定ではない。限界に開示)。他に未解決span(Kallmeyer・Ganis)を持つsegmentは新armでもPASSにしない。
- PASS_WITH_WARNINGになった新規音声2本(s12/t2、s16/t2)は4エンジンとも「kate」。**同じ本文のtake1は4エンジンとも「kite」**で、現行TTSのKhaiteは再生成ごとに読みが変わる(確率的)。
- 判定側の天井: 現行TTSで HR(プロキシ)25 のうち、2エンジン以上が「どの妥当な読みからも逸脱」するTTS誤読の疑いが**18**、残り7のうち他の未解決spanを持たず判定側の改善余地があり得るのは**6**(24%)。すなわち**判定側をどれだけ改善しても、現行TTSの出力では最大でも約24%で、40%に届かない**(受理集合の有無・同定は考慮しない上限)。HRの多数はTTSの実誤読(Khaite「kite」、Meink「mink」、Toteme「totem」、Melos「mello/mallo」)に由来する。
- Production判定への影響(S2R-06の裏返し): 現行プロキシがPASSとする9音声のうち、新arm(N5)がNGとするものが3(Primaryだけが正しい綴りを返し、他エンジンは誤読を示す音声。s09/t1 Khaite、s11/t1 Toteme等)。新方式は誤PASSの検出側には働くが、HR削減には働かない。
- 結論: **第1巡の主因補正(OF-S2R-01)に沿って「候補集合が空」「ASR綴り経由」を同時に改善しても、HRは実測では減らない。ボトルネックは判定ではなくTTSの実誤読**。ユーザー§4に従いここで終了せず、§5に次の手を示す。

## 2. 対象母数・現行HR件数・改善後HR件数(3区分を分離)
- 保存データ(旧TTS): HR事象58(独立segment 30、延べlookup 61)。うち25事象は**単体テストのmock出力**(§付録(b))。保存最終wav22・保存attempt 86音声(第1巡)。
- 現行TTS新規(本巡): 30 segment(take1)+16(take2)=46音声。設定=gemini-3.8-flash-lite-tts・Aoede・PD06 style(`er019`現行FULL_STORY profile、sha256 `3a680861e4d9d1bc…`)、Family Z(Melos)もnarrator=Aoede/PD06。Std生成後6%減速とProduction再試行ループは再現していない。
- 負例(拡充): 7語×{子音置換C・強勢母音置換V・音節/語頭脱落S・語末子音脱落F}=28本+縮約文脈2本=30本。2エンジン以上が妥当な読みから逸脱した**確認済み誤読29本**(未確認1本=『Melo said.』は縮約と区別不能のため除外)。
- 区別(実誤発音かASR誤認識か)は機械的な候補ラベルのみ(確定は耳)。

## 3. 誤PASS・誤NG
- **誤PASS: 確認済み負例29本×全8arm(R1_V4…N6_W2)で0件**(0/29。95%上限は約9.8%[1−0.05^(1/29)]、ルール・オブ・スリーで約10.3%。標本が小さく『安全』の保証ではない)。種別別: C 7/7・V 7/7・S 7/7・F 7/7(確認済み/生成)・縮約文脈C2 1/1・F2 0/1。第1巡P2の誤読6本(Kite/Kay-tee/Mink/May-ink/Al-tuh-ZAIR-ah/Alt-oo-zarr)も全arm PASS 0(N4以降でNG 5・判定不能1)。
- 短い断片(『kt』)へのG2P適用は誤PASS(Khaite『Kay-tee』→ASR『kt』→G2PがK EY Tを捏造してPASS)を生んだため、長さ4字未満/母音字なしはG2P対象外にした(test済)。
- **Khaite「kite」8事象: 全arm(R1…N6)でNG維持(8/8)**。現行TTSの追加観測でもKhaiteの『kite』(s13/t1,s14,s21等)はN5でNG。
- 縮約(N1)と真の語末子音脱落: 『Melos said.』と『Melo said.』(次語がS始まり)は音響上区別できず、縮約を許容すると『Melo』も受理集合側に寄る。Melosは受理集合が空で実害は出なかったが、受理集合のある語(次語が同一子音始まり)では誤PASSの経路になり得る(負例F2で逸脱が確認できず除外=この限界の実例)。
- 誤NG(正しい発音をNG)の測定は真の正否の根拠がなく不能。NGは現行でもHRなのでHR件数は増えない。N4以降はASR側OOVをG2P化するためNGが増える(保存58事象でNG 10→16)。S2R-07(N5)で母音1つ差でエンジン間不一致のものは判定不能に振り分けた。

## 4. Web取得と合理的発音推定
第1巡から変更なし(取得4語、推定収束はKhaite・Meink)。本巡の追加: E3b=gpt-6-luna N-best(最大3、7呼出・JPY0.24)。Canelé 3候補・Melos 2候補・Zabelina 2候補が得られたが、独立2出所の支持(E2/E3/取得、弱化母音同一視下)で新たに受理集合へ入ったのは**Zabelina**(E3のAH/IHとG2Pの弱化母音差、2候補)のみ(Altuzarraは取得根拠[媒体合意]があるため推定は捨てる規則で不変、Canelé・Khaiteも不変)。Toteme・Melosは依然空(G2PとLLMの母音が弱化母音の差を超えて割れる/Melosは同定未確認)。N-best自体は同一LLMの再呼出で独立出所ではないため、2出所の数には数えていない。official自己申告は記録のみで判定・区分に一切使っていない(コード走査+フラグ反転test)。

## 5. 初回で効果が限定的だった原因・Opus指摘・改善内容・再Trial結果
- 第1巡の原因(Step A): 受理集合が空44/58+ASR綴り経由の判定不能。
- Opus Step B(OF-PNPS-S2R-01〜10): 主因の補正・測定単位・縮約・弱化母音/2出所・ASR側G2P・母音1つ差・official無視・負例拡充・代替案評価(`OPUS_REVIEW_STAGE2_STEPB_01.md`、要旨)。
- 第2巡で実施した改善(Trial arm): N1縮約/N2弱化母音/N3 2出所支持+N-best/N4 ASR側G2P+アクセント正規化/N5母音1つ差=判定不能/N6 Whisper追加要件。
- **再Trial結果**:
  - arm別(現行TTS全46音声、HRプロキシ37のうち): R1_V4/R1_EXT/N1〜N3 = PASS 2・NG 11・HR維持24 / N4 = PASS 2・NG 20・HR維持15 / N5・N6 = PASS 2・NG 20・HR維持15(N6はPASSの2本が全エンジンkateでWhisper要件も満たす)。**N1〜N3(縮約・弱化母音・2出所支持)は現行TTS音声でPASS件数を1件も増やさなかった**(効く語=受理集合が空のToteme・Melosがそのまま空のため、また縮約・弱化母音が必要になる観測が現行TTS出力に無かったため)。N4/N5はHR維持を減らす(判定不能→NG)が、NGも現行HRなので**HR件数は減らない**。
  - 保存データ(旧TTS、58事象): R1_EXT=PASS 1・NG 10・HR47 → N4/N5=PASS 1・NG 16・HR41。attempt音声(Production不合格74語ペア): PASS 3は不変、NG 25→35。
  - 結論: **判定側の4つの改善はTrial内でも効果を示さなかった**(HR削減0〜2件)。ボトルネックは(a)TTSの実誤読(18/25)と(b)受理集合が空の語(Toteme・Melos)。
- 次の一手の候補(改善見込みの自己評価、事実ベース。採否はFable):
  1. **TTS側の読みの制御(OF-S2R-10(1))**: 取得できている語(Khaite=Kate、Altuzarra=ahl-too-ZAH-rah、Meink=MEENK)の読みをTTS入力側で指定し、既存の判定でその音声を確認する。根拠: 負例では綴り替え(Bate/Kite/Monk/Ink等)にTTSが29/29追従し、制御が効く。既存`tts_safe_name_pronunciation_en`は`er003_v1_n3_01_tts_generate.py:994`にあるが辞書は`{"Reicher": "Riker"}`のみで7語は未登録(`tts_safe_news_en`[:998-999]経由で配線済み)。見込み: **中〜高**(HRの主因=TTS誤読に直接効く)。ただしESTIMATED供給禁止の原則(v4-5)との整合、現行Aoede/PD06での効果は未測定(本巡のTrialでは測っていない)。
  2. **再生成の活用(既存retryの範囲)**: Khaiteはtake間で読みが変わる(kite→kate)。既存の再生成上限内でASR合意(Primary以外を含む)でPASSできるか。見込み: 低〜中(語依存、Production規則の変更を伴う)。
  3. wav2vec2音素CTC(案2): 判定の天井(24%)が低いため、TTS誤読が主因の現状では優先度低。保留のまま。
  - 判断候補: 判定側arm(N1〜N6)のProduction採用は**推奨しない**(HR削減がなく、誤NGリスクとコードの複雑度が増えるだけ)。TTS側制御のTrialは承認範囲内か新規Trial範囲かの確認が要る(区分D候補)。

## 6. 使用総額・量産単価への影響
- 本巡 **JPY63.55**(`r2/paid_calls.jsonl`): E3b 0.2435、TTS 34.94(Gemini 3.8 flash-lite TTS、76呼出)、OpenAI ASR 7.51(76呼出。上限見積。`gpt-4o-mini-transcribe` USD0.006/分×160円、秒換算単価は未確認)、Azure STT 20.86(76呼出、$1/audio-hour、pricing_snapshot)。為替=USD_JPY=160(プロジェクト既定)。
- Trial累計Cap300: 第1巡15.54+本巡63.55=**79.09**(残220.91)。本巡Guardrail80内(残16.45)。当日(JST 2026-10-22): 委任文の既使用約686+63.55=**約749.6/1,000**(残約250.4)。
- 見積差の理由: 委任文の見積約60円は『約90本×0.65円/本』で、0.65円は第1巡の短文(約7秒)の実測。実本文は平均約35秒のため全長ASRでは約190円になる見込みで、(1)Primary/Azureを対象文の窓へ切り出し(12秒超のみ)、(2)take2を16 segmentに絞った。実測63.55円はGuardrail内。
- 量産単価への影響: Production無変更のため0。判定側armを採用しても削減が出ないので単価改善はなし(E3b追加は新出現語1つあたり約0.03円)。

## 7. Fable独立評価、Trial終了Status
(Fable記入欄)到達Status=`TRIAL_R2_DONE_PENDING_FABLE`。

## 8. Production採用に必要なユーザー判断
(Fable記入欄)現時点で本巡の結果から新規にユーザー判断が必要な事項は無い(N1〜N6はProduction採用の段階ではない。推奨しない)。参考: TTS側読み制御のTrial化はFable判断(新仕様候補)。

---
## 付録 S2R-02/06/10 の事実確認(判断・修正はしていない)
- **(a) 承認の再利用**: `er006_*.py`に`human_approved|approval_reuse|reuse_human`は0件。実体は`er011_human_review_lock_01.py:179-191`の`_human_approved(level_out_dir, segment_id, text)`(使用箇所:320)で、`{level_out_dir}/audit/human_approved_segments.json`の`segment_id`+`canonical_text_sha256`一致のみ。**同一run(level dir)内に限られ、別run/別Tempディレクトリへは再利用されない**(run間の承認再利用機構は見つからなかった)。同一本文・同一音声(別run)で同じHRが何度も起票され得る構造。
- **(b) 開発用run・単体テストのHR混入**: HR queue 113行にrun種別の項目は無く、`wav_path`で分類した。`er026_pscr_outer_*`(`er026_post_slowdown_cascade_rescue_01_test_01.py:250`の`tempfile.mkdtemp(prefix="er026_pscr_outer_")`)の**25行(113行の22%、対象7語の58事象の43%、Melos lookup 36のうち25)**は、Primary「Mello said.」/Azure「Mellow said.」がそのテストのmock入力(同test:108,175,231,241,280,287)と完全一致し、音声実体もない=**単体テストの出力がHR queueに混入している強い状況証拠**(行87〜113[1始まり]のうち25行、2026-10-17〜10-22の各所)。残りは、pool_pilot 30、`er019_output/family_x_audio_production_wiring_01` 25、`er026_output/family_z_production_e2e_01` 10(開発用E2E)ほか。本Trialはテストを実行していない。Melosの『真のHR』は11事象(E2E run 10+er063 1)。
- **S2R-06 実測**: 確認済み誤読負例29本のうちPrimaryが正しい綴り(altuzarra)を返したのは**2本(6.9%)**(n_altuzarra_V/F)。現行TTSの自然音声46本のうち、Primaryが正しい綴りで他の2エンジン以上が妥当な読みから逸脱するものが3本(s09/t1 Khaite、s11/t1 Toteme、s17/t1 Altuzarra)。現行プロキシがPASSとする9音声のうち2本(s09/t1、s11/t1)。→ Primary単独PASS経路のリスクは実在(Productionの変更はしていない)。Fableが結果を見てOPEN項目化を判断。
- **S2R-10(1)**: `tts_safe_name_pronunciation_en`=`er003_v1_n3_01_tts_generate.py:994`、辞書`_EN_NAME_PRONUNCIATION_OVERRIDES = {"Reicher": "Riker"}`(:990)、`tts_safe_news_en`(:998-999)経由。対象7語は未登録。他の使用箇所: `er008_n8_reicher_pronunciation_22_test_01.py:31`(test)のみ。
- 限界の開示: (1)ASRはPrimary/Azureを対象文の窓、Whisperを全体音声で転写。(2)現行基準HRは『Primary/Azureの綴り一致』のプロキシで実判定ではない。(3)Std生成後6%減速・Production再試行ループ・Store再利用は再現していない(狙いは単発の読みの測定)。(4)Family Zの対話(dialogue)voiceは未使用(Melos 8 segmentは全てnarrator)。(5)標本が小さい(各語・各種別1本、take2は16本)。確率的なTTSで1回の生成は統計的評価ではない。(6)誤読確認の『妥当な読み』は推定E2/E3/取得の和集合(正解の確定ではない)。(7)Melosの同定は未確認のまま。(8)OpenAI ASR単価は上限見積。
