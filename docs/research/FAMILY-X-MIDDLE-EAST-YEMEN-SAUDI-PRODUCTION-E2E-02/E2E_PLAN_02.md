# FAMILY-X-MIDDLE-EAST-YEMEN-SAUDI-PRODUCTION-E2E-02 E2E_PLAN_02(委任_01、2026-10-20)

性質: 正式Production経路の記事生成(text+audio)。新仕様探索ではない。ユーザー決定③(2026-10-20)。

## §0 受入条件の事前固定(実走前。以後変更しない)
- 攻撃主体Fact: Fact本文(英/日)が、サウジ領内(リヤド/アブハ空港・Aramco施設等)またはイエメン周辺への当該期間の攻撃について、実行主体または犯行声明主体として Houthi / Houthis / Houthi movement / Ansar Allah / Ansarallah / フーシ派 / アンサール・アッラー のいずれかを明示するもの。帰属付き(「〜が犯行声明」「連合軍/国連によれば〜」)可。場所言及のみ(「フーシ派支配地域」等)や攻撃と結びつかない言及は該当しない。
- 3段階を分けて記録: (i) Researcher Fact化=`research_ledger/audit/researcher_full_record.json`のfacts / (ii) Ledger登録=VERIFIEDか(AMBIGUOUS/REJECTEDなら理由) / (iii) B3採用=`storyline_b3/fact_selection_evidence.json` `selected_fact_ids`。(iii)Yesのみ下流へ。
- Writer反映: b1b/a2本文に攻撃主体がLedger帰属を保って登場(Grep `Houthi|Ansar ?Allah|Ansarallah|フーシ`)。B3採用済でWriter本文に無い場合のみ `--stage writer --regenerate-stage writer`(+advanced/standard各1回)を1回だけ許可。それでも無ければSTOP。
- 既存Gate(Fact Lock/記号Validator/IOL spec_ok/RF候補/AUW/Audio Validation Gate/style_profile_gate/key_phrase_source_gate)は従来どおり。HR/Lock/BLOCKは迂回せずSTOP。RF候補は件数・内容記録(合否はFable)。
- 日付・帰属CP: Ledger外具体描写0件、数字の帰属、時点明示の有無を記録(合否はFable)。
- Research最大3回(run_mey_02/03/04)。3回ともB3未採用=STOP(B3未採用)。手動Fact挿入・Ledger/B3手編集・`--regenerate-stage storyline_b3`による再抽選は禁止。
- 上限JPY180(本委任の新規支出合算)。次stage前に「既使用+次stage見積」が180超見込みならそのstageを開始せずSTOP。

## §1 開始条件チェック(S0、2026-10-20)
- 当日既使用: `daily_dev_cost_01.py --date 2026-10-20` adopted_jpy=513.24(予定値と一致)。残486.76。
- 出力dir: `er019_output/middle_east_yemen_saudi/` は `run_mey_01` のみ(run_mey_02〜04非存在)。
- runner引数実在: entertainment runner `--stage {research,ledger,storyline_b3,writer,advanced,standard,all}`/`--budget-jpy`/`--run-label`、audio runner `--stage {plan,scaffold,tts,assemble,player,all}`/`--level`/`--budget-jpy`/`--tts-backend`(既定speech_metadata_flash_lite)を`--help`で確認。
- 作業前`git status --porcelain`: 1142行(既存の他run差分。本委任は明示addのみ)。branch=work/post-merge-01。
- T-0: 委任文保存 `docs/pm/delegation_log/2026-10-20_..._委任_01.md`、sha256=3d7a45977694cc86366851ada8f14fcaa6c2e7ebc6459dd2ec3ae9228eeccf64、26036 chars(wc -m)。check_delegation_prompt=FAIL(理由: 「事前指定Grep一覧+追記位置・更新位置の手順」見出し不在。記録のみ・継続)。

## §2 試行ごとの記録
| 試行 | run dir | Research | (i) Researcher Fact化 | (ii) Ledger | (iii) B3採用 | text費用 |
|---|---|---|---|---|---|---|
| 1 | `er019_output/middle_east_yemen_saudi/run_mey_02` | facts 8(kept)、web_search 4回(Ledger含む合計7)、gpt-6-luna、reused:false | 攻撃主体Fact: YSA-20261020-01(連合軍報道官発表: フーシ派がリヤドへ発射した弾道ミサイル1発を迎撃)、YSA-20261019-01(シャブワ州知事: フーシ派ミサイル攻撃で新兵73人死亡)、YSA-20261015-02(フーシ派がアデン宮殿近くの攻撃を認めた)、YSA-20261015-01(連合軍は主体不明示・フーシ派は関与否定) | VERIFIED 7 / AMBIGUOUS 1(YSA-20261015-02、匿名政府関係者の死傷者数) / REJECTED 0。YSA-20261020-01=VERIFIED(連合軍発表の帰属付き) | **採用**: selected_fact_ids=[YSA-20261020-01, YSA-20261020-02](gpt-6.1-sol、attempts 1)。選定理由引用:「迎撃とフーシ派への帰属はいずれも連合軍報道官の発表として扱う」。YSA-20261019-01除外理由:「イエメン国内の訓練キャンプ攻撃…英国の任務との因果的な接続はLedgerにない」 | 32.514 |
→ 試行1で(iii)Yes。試行2/3(run_mey_03/04)は不要につき未実行。

## §3 採用試行の下流記録
- Writer(W-1 R0〜R2)/Advanced/Standard: 全rc=0、IOL spec_ok=true(Adv/Std各2文)、structure_status=STRUCTURE_PASS、retry 0、記号Validator停止なし、HR/Lock発火なし(text段階)。
- タイトル(Adv): "Who Says “We Won’t Attack”? A Warning About Mixing Up the Subject of British Support" / Std: "...Mixing Up British Support"。
- In One Line(Adv): "Britain said its Typhoon jets would defend Saudi cities and key facilities, not attack the Houthis, while its refueling support also backs operations to weaken Houthi military targets. So the no-attack statement applies to the Typhoon mission, not all British support."
- Writer反映Grep(`Houthi`): a2/article.md L5「A spokesperson for the Saudi-led coalition forces in Yemen said they had stopped and destroyed one ballistic missile. The Houthis had fired it toward Riyadh.」、b1b/article.md L5「A spokesperson for the Saudi-led coalition ... said they had intercepted and destroyed one ballistic missile fired toward Riyadh by the Houthis.」。帰属(連合軍報道官発表)は直前文/同一文で保持。Std L5は2文に分離(2文目単独は帰属語なし)=RF候補s11。再生成(`--regenerate-stage writer`)は不要で未使用。
- RF候補: b1b=0件(issues=0)、a2=1件: s11「The Houthis had fired it toward Riyadh.」(luna-A3 confidence 0.3、理由=情報源「連合軍報道官の発表」の限定を外していないか)。合否判定はFable。queue=`review_queue/post_en/middle_east_yemen_saudi__run_mey_02/a2__rf20261020T124010Z-0975/queue.md`。
- Ledger外描写/日付: 本文のLedger外固有事実の網羅突合は未実施(Fable判定用に原稿path=`a2/article.md`,`b1b/article.md`)。本文「Typhoon」「refueling」「Saudi cities」はYSA-20261020-02に対応。日付・数値は本文に具体数値なし(1 missile 以外)。

## §4 音声工程記録(試行1)
- plan: profile fx_20261017、6 role sha(SUPPORT_JA 060c08fd…/FULL_STORY 3a680861…/PREVIEW 8862317f…/KP_EXPLANATION_EN 05180006…/KP_EN 9d905cfe…/KP_JA_MEANING b12c8721…)全一致。backend=speech_metadata_flash_lite(CLI省略)。
- scaffold: KP canonicalization PASS(a2/b1b)、M2-FALLBACK発生なし、費用2.63。
- TTS Advanced(b1b): 完了、STOPPED/review_lock 0、費用 累計9.49(scaffold含む)。
- TTS Standard(a2): **comment_2が STOPPED(標準2回+fallback1回=合計3回とも不合格)→ review_lock_state `HUMAN_REVIEW_REQUIRED`**。原因(観測): canonical「ここまでで、タイフーン機の任務はサウジの防空で、フーシ派を攻撃しないと分かりました。…」に対し、一次ASR(OpenAI)が「台風機/台風期」、二次ASR(Azure)が「大奮期/台風期」と転写し、AUW統一judgeが3回とも TRUE_CONTENT_MISMATCH/NG_BOTH(secondary_not_accepted)。フーシ派・防空・空中給油部分は一致。カタカナ語「タイフーン」のASR漢字化(台風)が主因と推定(音声自体の誤読は未試聴・未確認)。pronunciation resolver `unresolved_human_review=[]`(辞書・Web検索0)。
- assemble: b1b=OK(294.12秒、peak 0.798、clipping なし、style_profile_gate PASS)。a2=**BLOCKED_STYLE_PROFILE_GATE**(comment_2 `JA_FALLBACK_USED_OR_UNKNOWN`、M3 Gate)→ Std wav未生成。Gateは迂回せずSTOP。
- 試聴ページ(S11)は未実行(Std音声未完成)。`er019_mey_page_02.py`/`er019_mey_play_verify_02.py`は準備済み(未実行)。
- PASS_WITH_WARNING: Adv 0件、Std 2件(`a2/audit/pass_with_warning_listening_list.json`)。

## §5 費用(JPY、出典=cost.json/`audit/cost_by_stage_e2e_02.json`/runner console)
text 32.514(Research 7.415 + Ledger 5.538 + B3 5.044 + Writer R0-R2 12.693 + Adv/Std/RF 1.82)、audio 23.36(openai 2.78/gemini 11.95/openai_asr 3.25/azure 5.38、うちStd comment_2の3試行+ASRを含む)。本委任新規支出合計 55.87(上限180内)。当日累計 569.11(`daily_dev_cost_01.py --date 2026-10-20`)。中東記事案件累計(E2E-01 text 79.881+今回55.87)=135.75。異常retry由来: Std comment_2再試行(TTS 3回+ASR 3回+Azure 3回)。Trial特有=なし。Batch使用なし(TTS_EXECUTION_MODE=STANDARD)。

## §6 所要時間(JST、2026-10-20)
Research+Ledger 21:32:54〜21:34:31 / B3 21:35:52〜 / Writer 21:36〜(約3分) / Adv・Std text〜21:40 / plan 21:41:29 / scaffold 21:41:44〜21:46台 / TTS Adv 21:47:04〜21:50:18 / TTS Std 21:50:28〜21:52:2x / assemble 21:55:03前後(各stage時刻は`run_mey_02/t_*_start.txt`,`t_*_end.txt`)。

## §7 runtime evidence
Research/Ledger/B3: `run_mey_02/research_ledger/runtime_evidence.json`(gpt-6-luna, reused:false)、`storyline_b3/runtime_evidence.json`(gpt-6.1-sol, attempts 1)。profile=`audio/.../audit/style_profile.json`。AUW/gate: `a2/audit/style_profile_gate.json`(BLOCK)、`a2/audit/review_lock_state.json`、`a2/audit/tts_generation_results.json`、`b1b/audit/style_profile_gate.json`(PASS)。stop_scope_check: `run_mey_02/audit/stop_scope_*.json` 全rc=0。

## §8 STOP(2026-10-20 委任_01)
Std comment_2 の M3 Gate BLOCK(HUMAN_REVIEW_REQUIRED)でS10にてSTOP。Gate迂回・resume・再起動なし。判断候補は RESULT_PACKET_MEY2.md 参照。

## §9 委任_02 調査結果(Std comment_2 HR、2026-10-20、費用JPY0・新規TTS/ASR/LLM呼出0・Lock操作0)
### 9-1 既存仕様reconcile(14節step2)+11-8判定材料
- 正式仕様: JA ASR Secondary(SCG)=`CURRENT_SPEC.md:2138`(Azure ja-JP、**Phrase Listなし**、受理=EXACT/NORMALIZED_MATCHのみ。PHONETIC_MATCHは受理しない)。統一judge JA受理集合=`:2819`(OF-AUW-08 R+: EXACT/NORMALIZED、ORTHOGRAPHIC_VARIANT_CONFIRMEDは2エンジン確認)。除外表=`:2810`(**『読みでの受理禁止』2026-10-11ユーザー安全条件**、A7)。表記ゆれ一般化Variant Layer(OPEN-145)=`:2154`、実装`er011_ja_asr_variant_layer_01.py`(形態素解析の全文読み一致)。短文PHONETIC_MATCH=`:1827`(30字以下のみ・読み完全一致のみ)。
- 判定: 漢字/カタカナの読み同値を受理するTierは**存在する**(Variant Layer Candidate B)が、読みが一致した場合のみ発火する。オフライン再現(`classify_ja_asr_match`、API不要): 台本「タイフーン機」=タイフーンキ(`morph_kana_reading`)に対し、ASR「台風機/台風期」=タイフウキ、「大奮期」=ダイフンキ。**撥音『ン』の有無・濁音が異なる=読みが不一致**のため同値Tierは正しく不発火。よって (a)(仕様と実装の乖離=11-8範囲内の是正)は**非該当**、受理するには「ン脱落を許容する読み許容の新設」=受理面の新設=範囲外(`:2810`の『読みでの受理禁止』とも衝突)。T1/T2(11-8)とも該当なし=不具合0件。
- Family Z既決との関係: REGISTER #52(M1 OOV除外)・#120(Pattern A受理範囲)は**英語**の音韻等価の判断で、JA固有名詞の表記ゆれは別問題。JAに直接効く既決は`:2810`/`:2819`(読みでの受理禁止・受理集合縮小)。OPEN-371はSecondary障害時のHR Lock早期return(本件と別。委任文のP1辞書UDRとは不一致)。結論: JAで『読みが違うASR転写を受理する』方向は既に否の判断済みで、本件の出口は既存のHR人間試聴(REGISTER #116の運用例)のみ。再質問材料なし。
- Azure Phrase List(A-3): JA経路は`phrase_list=False`(`er007_ja_secondary_asr_01.py:314`、audit実値は3 attemptとも`phrase_list:false`、`azure_phrase_list`/`azure_phrase_list_weight`キー自体はJA SCG scg_infoに無い)。`AZURE_PHRASE_LIST_WEIGHT=2.0`は`er006_secondary_asr_01.py:75,111`でPhrase List**非空時のみ**適用されるため、JA SCG(PLなし)には効かない。台本語[タイフーン]をJAのPLへ入れる配線は存在しない(新設なら仕様変更=範囲外・判断候補)。
### 9-2 原因切り分け(14節step3)
| attempt | route | 音声sha(先頭16)/bytes | 一次ASR(OpenAI) | 二次ASR(Azure) | 差分 |
|---|---|---|---|---|---|
| 1 | custom_06ec49ff(S3) | 57c6b7a8…/638,924 | …台風機の… | …**大奮期**の任務は？… | タイフーン機のみ(二次に句読点差) |
| 2 | custom_06ec49ff(S3) | c9f48c1b…/637,484 | …台風機…**風師波**を攻撃… | …大奮期… | タイフーン機+**フーシ派→風師波(一次のみ)** |
| 3 | minimal_fallback | 8a05886b…/658,604 | …**台風期**… | …台風期… | タイフーン機のみ |
- 訂正: 委任_01の『フーシ派以降は全一致』はattempt2の一次ASRについて不正確(風師波)。差分は主に「タイフーン機」、attempt2のみ追加で「フーシ派」。
- 3音声は**同一ではない**(sha・サイズ全て異なる、3回別生成)。3回とも『ン』を含まない読み(taifū-ki系)にASRが収束=(i)TTSが『タイフーキ』と読んだ、(ii)ASRの語彙事前分布が既知語『台風機/台風期』へ寄せた、の双方が成立し得て転写からは区別不能。傍証: 同runのComment 3『タイフーン戦闘機』は一次=台風戦闘機・二次=**タイフーン戦闘機(完全一致)**でSECONDARY_CONFIRMED合格(pass_with_warning list)=同じ語を含む別文ではTTSが読めている。断定しない。確定は人間の試聴。
- 所見(1行・変更しない): 台本「タイフーン機」は『戦闘機』を欠く不自然な略称で、ASRが『台風期(typhoon season)』という自然語へ引かれる設計上の弱点。S3 scaffoldは同runのComment 3では『タイフーン戦闘機』を生成しており、『タイフーン戦闘機』のほうが自然で聴取者にも明瞭。
### 9-3 failure mode一般化(14節step4)
- failure mode=『台本のカタカナ外来語/固有名詞を、JA ASRが同音近似の既知漢字語へ正書化する』。既往(全Grep、`pass_with_warning_listening_list.json` 51ファイルJA 18エントリ): 一次が漢字化→二次(Azure)が原稿一致で救済(SECONDARY_CONFIRMED)された例3件(タイフーン1[本run Comment 3]、メロス2[Family Z])。二次も漢字化して失敗(NG_BOTH→HR)は`er007_output/ja_asr_cascade_01/human_review_queue.jsonl` JA 11件中の本件1件のみ。er009 JA queue(343件)はASR steps無しのテキストGate記録で対象外。
- 発生構造は『一次だけ誤る→二次で救済』が通常で、『両エンジンが同じ漢字語へ収束』は希少。語の性質は『カタカナ語+短い漢語接尾(機)』で既知漢語(台風期)に衝突するもの。一般対策の候補(実装せず): (1)scaffold側で衝突しやすい略称を避ける(『戦闘機』等で既知語衝突を減らす)(2)JA SCGへPhrase List(台本のカタカナ語)を渡す(仕様変更=判断)。いずれも未承認・今回実施せず。
## 9-4 残CP(E2E-01 §14観点、b1b/a2 article.mdをLedger YSA-20261020-01/-02と突合)
- Ledger外の具体事実・数字・日付・創作場面=0件。本文に数字・月日・曜日・時点語(today等)は0件(grep 0)。比喩(meeting minutes/news detective/name tag/運転と給油)は4つのみで、うち運転/給油の例えは本文で『これで責任は決められない』と非事実を明示。省略(A400M/軍事顧問)は誤りでなく省略。
- 帰属: Adv=『A spokesperson for the Saudi-led coalition ... said they had intercepted and destroyed one ballistic missile fired toward Riyadh by the Houthis.』=同一文でFact(F-01、連合軍報道官発表)の帰属内に収まる。Std=『...said they had stopped and destroyed one ballistic missile. The Houthis had fired it toward Riyadh.』(s11)。
- s11所見: Stdは2文に分離され、第2文『The Houthis had fired it』は文法上は報道官のsaid節の外に置かれる。過去完了(had fired)で直前の『said』の内容として読める余地は残るが、独立文としては地の文の断定(フーシ派が発射した)に見える。Ledgerでは『フーシ派が発射したミサイルを連合軍報道官が迎撃と発表』=帰属付き(OBSERVED_REPORTED)なので、Advは帰属維持、Stdは帰属が弱まる(luna A3 conf 0.3のRF候補と整合)。変更は行わない。帰属を強めるなら『the coalition said the Houthis had fired it』形が候補(Writer/Prompt変更に当たるため報告のみ)。
## 9-5 解除後の手順書(実行しない・ユーザー試聴承認が前提)と代替案
0. 前提確認: `TTS_EXECUTION_MODE=STANDARD`を明示(新規TTS時のみ)。承認対象wavは**`a2/narration/comment_2.wav`(=attempt3 minimal_fallback、sha 8a05886b…)**。attempt1/2を採用したい場合の既存の公式差替え経路は未確認(要Fable確認。承認は台本shaにのみ紐づきwavは紐づかない=`er003_v1_n3_01_assemble.py:96-117`)。
1. `record_human_approval(out_dir="er019_output/family_x_audio_production_wiring_01/middle_east_yemen_saudi__run_mey_02/a2", segment_key="comment_2", canonical_text=<a2_support_texts.json comment_2>, approved_by="user")`(`er003_v1_n3_01_assemble.py:96`の正規経路)。費用0。承認でM3 Gate(`er019_family_x_style_profile_01.py:692-693,m3_assembly_gate`)がhuman_approvedへ移る。
2. `TTS_EXECUTION_MODE=STANDARD .venv\Scripts\python.exe er019_family_x_audio_production_runner_01.py --slug middle_east_yemen_saudi --run run_mey_02 --level a2 --stage tts --budget-jpy 70`(resume)。コード読みでは、comment_2はlock HUMAN_REVIEW_REQUIRED(`er011_human_review_lock_01.py:339`)で0 API、他segmentはstatus==OK+wav存在でreuse(同`:661,708`、14-6)=差分のみ。見積JPY0〜(上限=--budget-jpy 70、実測は走らせて確認)。承認だけでassembleに進める可能性もあるため、tts resumeが必要かはFable確認。
3. `--stage assemble --level both`(API呼出なし想定、見積0。b1bは既存OKの再組立)→ `--stage player` → `python er019_mey_page_02.py --run-dir ... --audio-dir ... --out user_test/middle_east_yemen_saudi_e2e_02` → `er019_mey_play_verify_02.py`(Playwright)。いずれもJPY0。合計見積JPY0〜数円。
4. 代替案(判断候補): (ア)承認して続行(上記、最安・最速)。(イ)comment_2のみ文言再生成=**専用経路なし**: `--stage scaffold`はStd support 5文を全て再生成(`runner:309-333`)、LLM非決定のため他4文のshaも変わりTTS再実行(概算JPY10〜15)。かつHR Lock/承認キーは台本shaなので新版扱いで自動解放される(`er011_human_review_lock_01.py:329-332`)が、これは台本の再生成=ユーザー承認範囲(Production挙動の変更でなく既存scaffold再実行)か要Fable判断。(ウ)11-8範囲内是正=9-1のとおり(a)非該当のため案なし。
