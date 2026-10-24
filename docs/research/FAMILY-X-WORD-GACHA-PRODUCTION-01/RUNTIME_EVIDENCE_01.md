# RUNTIME_EVIDENCE_01 (FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_01, 2026-10-24) 【委任_04完了: Std/Adv正式組立・公開page_verify PASS。最終試聴PASS可否=UDR #184待ち】

## 起動履歴(すべて同一HEAD 00815e4d8、`TTS_EXECUTION_MODE=STANDARD`、`.venv\Scripts\python.exe`、各起動前 stop_scope_check rc=0=stop_check_*.json)
| # | 起動 | 結果 |
|---|---|---|
| 1 | `er019_family_x_entertainment_production_runner_01.py --theme <theme.txt> --slug word_gacha --out-dir er019_output/word_gacha/run_wg_01 --run-label run_wg_01 --budget-jpy 60 --stage all` (JST約17:54-18:03) | rc=0。Research→Ledger→B3→W-1 R0-R2→Advanced→Standard→RF。37.71円 |
| 2 | `er019_family_x_audio_production_runner_01.py --slug word_gacha --run run_wg_01 --level both --stage all --budget-jpy 60` (JST 18:03-18:29、cooldown600秒含む) | rc=0。plan/scaffold/tts完了。52.32円 |
| 3 | 同 `--stage assemble` | rc=0だがAdvは`BLOCKED_STYLE_PROFILE_GATE`(full_story_part3 STOPPED→FINAL_STYLE_RECORD_MISSING)、Stdは組立OK |
再起動0・approve_regenerate未実行・Gate迂回なし。

## text
Research gpt-6-luna、Ledger VERIFIED 13/AMBIGUOUS 0/REJECTED 0。B3(Min2)採用F03・F06、丸め overlay OK。W-1 R0→R1→R2、Advanced/Standard。RF issues=9(review queue保存)。費用37.706円(research 10.98/ledger 3.83/B3 7.65/writer 12.45/adv 0.39/std 0.44/RF約1.9)。事実検査=FACT_CHECK_01.md(混同禁止3点クリア、創作0)。

## audio(出力=er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/)
- Standard(a2): 11/11 segment OK、assemble OK 320.08秒、clipping無し、HR Lock 17件すべてRESOLVED、累計TTS>1: full_story_part3(2)・kp1_en(2)。PASS_WITH_WARNING 3件(事後試聴、非ブロッキング)。KP: pass it by / spark curiosity / by heart(KP英語3clip OK、KP3-ASR投票evidence 3/3)。
- Advanced(b1b): 9/10 segment OK、**full_story_part3=STOPPED/HUMAN_REVIEW_REQUIRED**(3回TTS試行すべてPrimary=ASR_VALIDATION_UNCERTAIN[「gacha」を「gotcha」と認識、他は全文一致]+Secondary(Azure)=TRUE_CONTENT_MISMATCH[句読点区切りで文が混線する脱落様出力]=NG_BOTH)。他のHR Lock 14件RESOLVED。累計TTS>1: in_one_line(2)。KP: star power / spark curiosity / tug at its sleeve(3clip OK)。
- 固有名詞アラーム: 0件(entity table 3件、うち証拠使用可1件。UR・Jackpotは weak)。「gacha」は実体表に載らず(一般語/借用語扱い)、PNAP受理境界の外。
- style_profile=fx_20261017、tts_backend=speech_metadata_flash_lite、KP gloss alignment flag=ON(source=default、EIGO_KP_GLOSS_ALIGNMENT未設定)、X2p'/G3は不使用。
- 費用: text 37.71 + audio 52.32 = 90.03円(上限100円内、目標70円は超過)。audio内訳 openai 2.59/gemini 17.60/openai_asr 4.64/azure 27.48。Adv part3の3回試行+cooldown600秒が主因(Azure Secondary費用)。

## 委任_02(2026-10-24 18:3x-18:55 JST): Fable approve_regenerate 1回目→HR解除→Adv assemble blocked
- 起動前: stop_scope_check rc=0(`stop_check_regen1.json`/`stop_check_regen1b.json`/`stop_check_assemble2.json`)、X経路 .py の未commit変更0(`git status`)。
- approve_regenerate: `er011_human_review_lock_01.approve_regenerate(.../b1b/narration/full_story_part3.wav, text, approved_by="FABLE_APPROVE_REGENERATE 2026-10-24 FAMILY-X-WORD-GACHA-PRODUCTION-01 委任_02: ASR homophone gacha->gotcha x3, no audio defect evidence, Std passed on retry; max 2 regenerations")`(正規関数のみ。text=`tts_safe_news_en(parts['part3'])`でlock記録hash bb9df6f0…と一致を事前確認)。state=REGENERATE_APPROVED。
- 再生成: `er019_family_x_audio_production_runner_01.py --slug word_gacha --run run_wg_01 --level b1b --stage tts --only-segments full_story_part3 --budget-jpy 110`(1起動、rc=0、console=`er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/regen1_console.txt`)。cooldownはrunnerが待機。
- 結果(lock `review_lock_state.json`): state=RESOLVED、累計TTS7/ASR7(委任_02分=4)。テイク1〜3: 全て `NG_BOTH(secondary_not_accepted)`、ASRは `gacha→gotcha`(テイク2は`oh`脱落、テイク3は`you've→you`も)。**3回NG後、既存のTTS Local Rewrite recovery(TTS-LOCAL-REWRITE-CONNECTED-SPEECH-PRODUCTION-WIRING-01)が作動**し `you've felt`→`you have felt` の短句書換候補1(ng_span=`ve`削除)で生成→テイク4=`PASS_WITH_WARNING(secondary_confirmed, NORMALIZED_MATCH)`。最終ASRでも `gotcha` は残る(Secondary確認で通過)。
- Adv assemble(`--level b1b --stage assemble`、rc=0): **status=BLOCKED_STYLE_PROFILE_GATE**。segment=full_story_part3、violations=`FINAL_STYLE_RECORD_MISSING`/`ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED`(style_prefix=`<default:ENGLISH_STYLE_PREFIX>`)/`LOCAL_REWRITE_RECOVERY`。Gateは人間承認(`record_human_approval`)がなければ組立を拒否する仕様(`er019_family_x_style_profile_01.py`:582,685,716。runnerはGateを解除しない)。Gate迂回なし・人間承認記録なし。
- 2回目の再生成は未実施: 案件累計 text37.71+audio67.02=**104.73円**(Fable設定上限110円)。もう1回(約+14.7円)は約119円となり上限超過のため実行せずFableへ(§費用)。2回目で通常テイク(Local Rewrite不要)になる保証はなく、Adv7テイク中gacha→gotcha 7/7(Std part3は2テイク目でOK)。
- 最終成果物の現状: Std=assemble OK(320.08秒、`a2/assembled/`)。Adv=part3のみ未組立(他9 segment OK)。試聴ページ・page_verify=未作成(Advが組立てられないため。Std単独ページは仕様のStd/Adv切替を満たさないので作らない)。
- ユーザー耳確認用: 新テイク mp3 =`er019_output/family_x_audio_production_wiring_01/word_gacha__run_wg_01/ear_check/adv_full_story_part3_regen1_final.mp3`(47.2秒、wavから変換、untracked)。元テイクのwav=`.../b1b/narration/attempts/full_story_part3_attempt{N}_englishstyleprefixwidemargin.wav`(N=1〜8、最終=8)。聴取ポイント=「gacha」が/ˈɡɑːtʃə/として自然か、`you have felt`の書換が不自然でないか、style(profile prefixでなくdefault prefix)が他segmentと乖離しないか。

## 費用(内訳分析。目標70円/記事セット vs 実績。出典=`raw_usage_log.jsonl` 144行、lock、runner cost行)
| 段 | 費用(円) | 主因 |
|---|---|---|
| text(Research/Ledger/B3/Writer/RF) | 37.71 | research(gpt-6-luna web検索)10.98=GIGAZINE/wordgacha関連の調査、ledger 3.83、B3 7.65、writer 12.45、adv 0.39/std 0.44、RF約1.9 |
| audio 委任_01 | 52.32 | Azure Secondary 27.48(最大)、gemini 17.60、openai_asr 4.64、openai 2.59 |
| audio 委任_02(再生成) | 14.70 | Azure 8.59(4呼出193.1秒)、残り約6.1(gemini TTS/OpenAI ASR/LR候補生成) |
| **合計** | **104.73** | 目標70円比 +34.73円 |
- Azure Secondary(単価約0.0444円/送信秒、`audio_duration_submitted_seconds`集計): 委任_01分 24呼出・618.4秒=27.48円。内訳: full_story_part3 7呼出335.8秒(約14.9円=54%。Adv3テイク+Std2テイク等の本文3再試行)、full_story_part1 3呼出173.2秒(約7.7円)、in_one_line 4呼出68.2秒、KP英語・topic_intro・preview等で残り。委任_02分 full_story_part3 4呼出193.1秒=8.59円。Azure合計36.07円(audio合計の約54%、案件合計の約34%)。
- 3回試行: Adv part3は3テイク全てPrimary=UNCERTAIN→Secondary呼出(長文約47秒×呼出)。cooldown600秒は待機のみで費用なし。
- 事実のみ(仕様変更提案ではない): SecondaryはPrimaryがNG/UNCERTAINのときのみ発火し、長文segment(約45〜60秒)ほど1呼出が高い(約2〜2.7円/呼出)。part3のgacha↔gotcha関連のAzureは14.9+8.6=約23.5円(Azure合計の65%)。同音NGが無ければ総額は約75円前後になる推計(未検証)。Secondary呼出を減らす余地=『同音が原因のNG』でSecondaryが走る回数(GACHA_HOMOPHONE_01.md案A)。ただしSecondary不要になるかは要検証(未確認)。

## 未完了(Fableへ)
1. Adv part3: 新テイクを(a)ユーザー耳確認→`record_human_approval`(Gate指定の人間承認)、(b)approve_regenerate 2回目(約+14.7円、案件上限110円を超える見込みのため上限引上げ要。Local Rewriteに再度なる可能性あり)、(c)GACHA_HOMOPHONE_01.md案A(同音データ追加)を先に実装してから再判定、のいずれか。
2. Adv assemble→試聴ページ(`er019_nws2_final_page_01.py`)→page_verify→UDR(最終試聴PASS可否)は未実施。

## 委任_04(2026-10-24 JST 20:1x〜): 人間承認の正式記録→Adv組立→試聴ページ公開→page_verify(API 0、追加TTS 0、費用0円)
- 前提: UDR #183=(a) ユーザー承認(原文=docs/pm/delegation_log/2026-10-24_FAMILY-X-WORD-GACHA-PRODUCTION-01_USER_02.md §1)。起動前 stop_scope_check rc=0(stop_check_d04.json)、tracked .pyの未commit変更0。
- 人間承認: `er003_v1_n3_01_assemble.record_human_approval(.../b1b, "full_story_part3", <Gateが照合するentry.canonical_text>, approved_by="user (USER_APPROVED 2026-10-24 UDR #183 (a), recorded via Fable delegation 04): ...")` 1回。記録=`er019_output/.../word_gacha__run_wg_01/b1b/audit/human_approved_segments.json`(sha256=12063e23…, approved_at=2026-10-24T20:14:31)。Gate直接編集・迂回なし。
- Adv `--stage assemble`(1起動、rc=0、console=assemble_adv_final_console.txt): style_profile_gate status BLOCK→**PASS**(human_approved=full_story_part3[FINAL_STYLE_RECORD_MISSING/ADV_STYLE_PREFIX_NOT_PROFILE_PREFIXED/LOCAL_REWRITE_RECOVERY]、blocked 0)。assemble OK 312.98秒、clipping無し、peak 0.95、KP vote audit 3/3、固有名詞アラーム0。
- 最終秒数: **Standard 320.08秒 / Advanced 312.98秒**。KP: Std= pass it by / spark curiosity / by heart、Adv= star power / spark curiosity / tug at its sleeve(各KP英語3clip OK)。
- 試聴ページ: https://shimomura055.github.io/eigo-radio/user_test/family_x_word_gacha_01/index.html(Std/Adv切替・通し・パート別・全スクリプト・KP、開発者向け情報なし。`er019_nws2_final_page_01.py`、commit dffd5b4f4)。
- 公開page_verify(`er019_nws2_play_verify_01.py`、Playwright実再生、証跡=page_verify_01.json): HTTP 200、audio 47/47再生OK、seek OK、full duration Std 320.08/Adv 312.98(期待値一致)、KP table 6、file:///C: 、Style sha露出なし、http>=400 0、console error 0 = **PASS**。
- PASS_WITH_WARNING一覧(事後耳確認候補、非ブロッキング、全てsecondary_confirmed): Std 3件=full_story_part1/full_story_part3/in_one_line。Adv 7件=topic_intro/preview/comment_1/full_story_part1/full_story_part3(Local Rewrite)/in_one_line/key_phrases/3/english(vote_2of3)。多くは中心語gacha→gotcha転写(Primary)をAzure Secondaryが確認したもの。
- Local Rewrite 1件の音声/表示差の開示: Adv full_story_part3は音声が`If you have felt that way`(you've→you have、TTS Local Rewrite recovery)。表示スクリプト(正本原稿)は`If you've felt that way`のまま(音声と1語展開の差)。ユーザーはこの差を承知の上で承認(UDR #183 (a)、聴取ポイント(2)に明記)。
- 実費: 案件累計104.73円(text37.71+audio67.02)、本委任0円(上限110円内、目標70円/セットは超過[+34.73円]、主因Azure Secondary 36.07円)。残: 目標70円超過の恒久対策はASR-OOV-HOMOPHONE-ROOT-CAUSE-01(別管理ID・別agent)。

