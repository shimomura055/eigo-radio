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
