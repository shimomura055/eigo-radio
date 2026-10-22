# IMPLEMENTATION_DESIGN_01(KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01 委任_01、2026-10-22。設計のみ・API 0・Production既存ファイル編集0)

Status: `APPROVED_FOR_PRODUCTION_DESIGN_PENDING_OPUS`(OPEN-457)。ユーザー原文=`docs/pm/delegation_log/2026-10-22_KP-QUALITY-IMPROVEMENT-2ITEMS-PRODUCTION-01_USER.md`。根拠データ=`INVESTIGATION_01.md`。配線は委任_02(Fableの正式run完了後)。未配線module=`er108_kp_cmu_lexicon_gate_01.py`(②)、`er108_kp_vote_noguard_01.py`(①)、test=`er108_*_test_01.py`(計51 test PASS)。

## 0. 結論(Fableの前提整理との差分を先に)
1. **前提整理は妥当。ただし1点追加(異論ではなく漏れの補完)**: 項目①の保護は、Fableが挙げた`make_voter/tally/whisper_needed`+統一judge内KP分岐に加え、**再利用点の事前guard `er078_reuse_value_guard_01.guard_entry`**(INVESTIGATION §1-2 G9)にも効いている。これは6再利用点すべてでKP vote gateの**手前**に走り、保存Primary転写の値DIFF/否定差で再生成へ回す。解除しないと『保存済みのcoffee等の再利用が保護差で止まる』ので、KP英語に限ってskipする。
2. 判定の変化(保存データ・API 0・本番adapter経路): **84件は判定変化0(偽PASS増加0)**、coffeeは**b1b最終wav(N2#4)がNG->PASS(P+W)に変わりHR原因が消える一方、a2最終wav(N1#4)はPrimary(`Pump one fist.`)もAzure(`1's`)もNGでユーザー真理値表どおり両NG=NGのまま**(Whisper不呼出)。a2側の救済は本変更の範囲外(真理値表の修正が必要=ユーザー判断事項。判断候補、区分D)。
3. ②は選定段(er105)に語単位のCMU照合を1箇所足し、未登録語itemは機械診断noteつきで再選定、最終attemptでCMU未登録だけが原因なら除外して残りで確定(shortfall)。canonicalization後の最終`used_form`は外側retry入口(X/Z共通`run_kp_with_outer_retry`)で再確認(INVALID扱い)。A/B/C無影響。

## 1. 変更箇所一覧(file:行は現行。X/Z/共通)
### ① KP英語音声の数値・否定保護解除(X/Z共通=判定は共通judge1箇所)
| # | file:行 | 変更 | 区分 |
|---|---|---|---|
| ①-1 | er078_asr_unified_judge_01.py:428-453 | vote_required時、最終ANDゲートの`NG_PROTECTED`短絡をskip(`final_gate={"applied":False,"skipped":"vote_guard_lifted","observed":{...}}`。値DIFF/否定差は監査に記録のみ)。**AMBIGUOUS降格(:454-456)は維持** | 共通(KPのみ。`vote is None`は不変) |
| ①-2 | er078:472-481 | vote_required時、Primary NGのP1(値DIFF/否定差/`protected_diff`)短絡をskipしてP3(Secondary呼出)へ進む | 共通 |
| ①-3 | er078:551-567 `finish_vote` | `kp3v.Voter`組立から`protected_diff`を除去(観測のみ`observed_protected_diff`)、`whisper_needed`->`whisper_needed_noguard`、`tally`->`tally_noguard`、audit組立を`build_vote_audit_noguard`(`guard_lifted:true`+観測値) | 共通 |
| ①-4 | er078:589-592 | vote_required時、`svg.DIFF or sneg`の`finish_vote(False,..,s_pdiff=True)`分岐を削除(S票は許容集合判定[:600-]で決める) | 共通 |
| ①-5 | er104_kp_three_asr_vote_01.py:138-146,151-190,203-225,248-264 | `whisper_needed`/`tally`/`decide`/`make_voter`を`er108_kp_vote_noguard_01`の実装へ**折り込む**(同名関数。`protected_dissent_blocks`引数、`NG_PROTECTED`/`NG_PROTECTED_DISSENT`、`HARD_STATES`/`STATES`の該当要素を撤去。`Voter.protected_diff`は`observed_protected_diff`(判定に使わない)へ)。**折り込み後、`er108_kp_vote_noguard_01.py`は削除**(二重実装を残さない) | 共通 |
| ①-6 | er104_kp_three_asr_vote_01.py:394-415 `vote_check_from_audit` | secondary.`protected_diff`キーを`observed_protected_diff`へ。保存evidenceの`version`は`kp_vote_check_v1`のまま(reader `er104_kp_vote_reuse_01._stored_check`:90 / `_entry_has_vote_pass`が無改修で読める)、新規fieldは`guard_lifted:true`(加算) | 共通 |
| ①-7 | er078_reuse_value_guard_01.py:32- `guard_entry` | KP英語のentry(label=`master:key_phrase_english_component*`[X default/K2]・`kp<N>_english`[X前回results/引継ぎ]・`kp<N>_en`[Z]。`kp_english`判定は1関数に集約)では保存転写の再判定guardをskip(`reason="KP_EN_VOTE_GATE_DECIDES"`, blocked=False)。**`reuse_blocked`明示markは従来どおりblocked**(一括再判定が付けた再利用禁止の印は尊重)。Store/X/Z/引継ぎの4呼出元は無改修(label判定) | 共通 |
| ①-8 | er104_kp_vote_reuse_01.py:1-30(docstring)、:109(`evaluate_vote`) | 判定ロジック変更なし(adapter経由のため自動追随)。docstringの『保護差』記述を更新 | 共通 |
| ①-9 | er006_secondary_asr_01.py:892(docstring) | 『vote_requiredでは保護差でNG_PROTECTEDにならない』を1行追記のみ | 共通 |

### ② CMU登録必須(X/Z共通=`fulltext_p2`経路。A/B/C無影響)
| # | file:行 | 変更 | 区分 |
|---|---|---|---|
| ②-1 | er108_kp_cmu_lexicon_gate_01.py(新設済み・未配線) | 語単位CMU照合・正規化・`apply_cmu_to_validation`・`canonicalized_check`。配線時もこのmoduleをそのままProduction moduleとする(名称変更なし)。docstringのStatusを更新 | 共通 |
| ②-2 | er105_kp_fulltext_selector_01.py `run_selection_gate`(:379-)のvalidate直後 | `v = validate_and_resolve(selected, units)` の直後に `v = cmu.apply_cmu_to_validation(v, final_attempt=(attempt==max_attempts))`(1行)。`validate_and_resolve`本体と`_legacy_form_reasons`は不変 | 共通 |
| ②-3 | er105 `run_selection_gate`戻り値/`run_fulltext_selection`(:466-) | `rec`に`cmu_excluded`、`gate`に`cmu_excluded`、`keywords_runtime_metadata.json`に`cmu_gate:{version,excluded,attempts_with_cmu_reason}`を追加(加算) | 共通 |
| ②-4 | er003_v1_n3_01_scaffold_generate.py `run_kp_with_outer_retry`(:666-)、canonicalization PASS判定(:712-714)の直後 | `chk = cmu.canonicalized_check(canon["merged"]["items"])`。`not chk["ok"]`ならcanonicalization INVALIDと同じ扱い(`failures += 1`・`entry["cmu_post_canon"]=chk`・artifacts退避・上限で`OUTER_RETRY_EXHAUSTED`)。次周のnoteには`build_canonicalized_note(chk)`を`generic_note`/`red_note`と同様に連結 | 共通(X/Zとも本関数経由: Xは`run_key_phrases`:755、Zは`er062.run_kp_with_outer_retry_fulltext`が委譲) |
| ②-5 | er103_*/PNAP等 | 影響なし(固有名詞発音台帳は参照しない。CMU未登録語を台帳で救済しない) | -- |
| ②-6 | 許可リスト: er104_kp_vote_wiring_test_01.py:754 と同型の『Production importer allowlist』test | er108 cmuのimporter(er105, er003_v1_n3)を許可に追加するtestを新設 | test |

## 2. 新旧の判定表(①)
票の定義(新旧共通): P/S/Wの各票PASS=`classify_asr_match`+同音救済`_step_alternate_pass`(長さ・救済層は従来どおり)。差は『値DIFF・否定差が票・短絡に効くか』のみ。
| 状況 | 旧(KP3V現行) | 新(保護解除) |
|---|---|---|
| P PASS / S PASS | 最終ANDゲートで値DIFF/否定差ならNG_PROTECTED、無ければPASS_DUAL | **PASS_DUAL**(Whisper不呼出) |
| P PASS / S NG(S転写に値DIFF/否定差) | NG_PROTECTED_DISSENT(Whisper不呼出) | **Whisper実行->2/3でPASS_VOTE_2OF3(P+W)**、W NGなら`NG_VOTE_WHISPER_NG` |
| P PASS / S NG(保護差なし) | Whisper実行->多数決 | 同左(不変) |
| P NG(自身に保護差) / S PASS | NG_PROTECTED(S/W不呼出) | **Secondary呼出->Whisper->S+Wで`PASS_WITH_WARNING`+`SECONDARY_CONFIRMED`**(P-03維持) |
| P NG / S NG | NG_BOTH(保護差があればNG_PROTECTED系) | **NG_BOTH**(Whisper不呼出) |
| Whisper例外/timeout/circuit open | NG_WHISPER_UNAVAILABLE(技術STOP) | **同左(PASSにしない)** |
| Whisper空転写 | NG票 | 同左 |
| Azure取得不能 | NG_SECONDARY_UNAVAILABLE(技術STOP、2/3へ縮退しない) | 同左 |
| rescued Primary(Azure転写依存の救済) | PASS票に数えない(P-07d) | 同左 |
| 非KP音声(本文・Dialogue・KP解説・Preview・A/B/C) | 統一judge(最終ANDゲート/P1/Secondary保護差を維持) | **不変**(`vote is None`) |
| 観測した保護差 | 判定に使用 | **audit(`observed_protected_diff`)にのみ記録**。NGの理由には使わない |

### 2-1 AMBIGUOUS(Opus Q1)
`value_guard.kind==AMBIGUOUS`(根拠のない曖昧表層。例: 十分/10分)は『数値の不一致』ではなく『読みが一意に決まらない』区分で、現行はPrimary PASSを降格しS票でsame_surface要求。ユーザー文言は『数値・否定の不一致』のみ。**推奨=維持(変種A)**。保存データでA/B(AMBIGUOUSも解除)は判定が同一(変化2件とも同じ)=Aで必要十分(§1ルール:過不足なし)。

## 3. Store再利用時の再判定(①)
- **新規実装なし**: `er104_kp_vote_reuse_01.kp_vote_reuse_ok`(:150-)は保存Primary/Secondary(+Whisper)転写を`evaluate_vote`(本番adapter)へ渡して再判定する。①-1〜①-4で判定核が変わるため、保存evidenceがP PASS/S NG(`Pump 1's fist.`)の場合、`whisper_text=None`なら**ローカルWhisperを保存音声へ実行**(`kp3v.whisper_vote`既定、API 0)し多数決になる。保存evidenceに両PASSがあればそのまま。
- 保存Whisper転写(`kp_dual_check.whisper.text`)があれば同shaで再利用(再転写しない。既存仕様)。
- **旧NGの救済の方向**: Storeは`+vote1`でPASSのみ保存=旧PASS集合⊆新PASS集合(単調)。旧NG evidenceを持つentryはStoreに存在しない。前回results/引継ぎでentryが`NG_PROTECTED_DISSENT`の保存証跡を持つ場合のみ新規則で再判定->PASSに変わりうる(再生成不要になる方向)。
- ①-7(G9)が前提: これを解除しないと、保存Primary転写の保護差でvote gateの手前でblockされる。

## 4. ②の正規化規則と除外->再選定->shortfallのフロー
### 4-1 正規化規則(`er108_kp_cmu_lexicon_gate_01`、test30件)
R0 NFC・曲線引用符->`'`・ダッシュ類->`-`・小文字化(アクセントは畳まない) / R1 前後の句読点除去(前後`'`・末尾`.`は保持形と除去形の両方を候補) / R2 語全体を`pronouncing.phones_for_word`で照合 / R3 ハイフン語は全体->各部分(全部分登録で合格。`well-being`は全体登録) / R4 `base'clitic`(clitic=s,d,m,re,ve,ll,tの閉集合)はbase登録で合格(`someone's`等は全体で登録済み)。不適合: 英字なし(数字のみ/記号のみ)、数字を含み全体未登録、他。**LLM推測・外部辞書・発音台帳・アクセント畳み込み・語形変化救済は一切なし**(testで固定: 注入lookupのみで合否が決まる/importがstdlib+pronouncingのみ)。
### 4-2 フロー(1選定gate= er105 `run_selection_gate`、MAX_ATTEMPTS=2)
1. attempt k: Luna出力 -> 既存の機械検証(本文一致・語数・件数・重複・旧形式precheck) -> **CMU語単位照合を重ねる**(`apply_cmu_to_validation`)。
2. 不適合(CMU含む)あり かつ k<最終: INVALID -> `build_machine_note`が『「novelty minaudière」: CMU発音辞書に登録されていない語を含む(未登録語: minaudière。…)』を本文後置noteに載せ再選定(Prompt 2本文・sha不変、`prompt_prefix_intact`で検査済み)。
3. k=最終: 不適合がCMU未登録のitemだけで残りが1件以上 -> **未登録itemのみ除外して確定(shortfall=True)**。他の不適合が残る/残り0件 -> INVALID(既存どおり外側retryへ。条件緩和・数合わせ・空確定なし)。
4. shortfall(<3件)の下流は既存の1〜3件可変処理(rank駆動、Redundancy QAは2件未満skip)。**ユーザー原文の『5件』は現行最大3件の読み替え**(KPFT仕様)。
5. canonicalization後: `run_kp_with_outer_retry`でused_formを再確認。不適合=INVALID扱い(外側retry通算3回内。次周noteにCMU診断を連結)。基本形化が語を変えて未登録にする例は保存2,130 item中0件(推測: 発火は稀、最終関門として保持)。
### 4-3 retry/fallback/resume整合
- 回数上限は不変(er105内2回、外側`failures>=3`・Redundancy別カウント、各周STOPセンチネル確認)。CMU失敗はretry上限を増やさない。
- fallback: 旧5件経路・Strategy Lへ倒さない(fail-closed維持)。
- resume: 既存`keywords_canonicalized.json`は遡及しない(ユーザー原文§4)。scaffold再実行時の挙動は委任_02で確認。
- OPEN-456 F1(同一句の繰り返し選定)との関係: CMU診断はnoteに未登録語を明示するため、F1の対策(明示除外note)と同型の機構になる。独立に実装可能。

## 5. 撤去する分岐・識別子とDangling確認
| 識別子 | 現行の出現(Grep対象) | 配線後 |
|---|---|---|
| `NG_PROTECTED_DISSENT` | er104:41,49,171、test: er104_kp_three_asr_vote_01_test_01.py:125、er104_kp_vote_wiring_test_01.py:189、記録系: er106_joint_runtime_evidence_01.py:921、er107_fx_kp_audio_ng3_listen_page_01.py:123 | 撤去。test2件は新期待値へ更新。er106/er107の2件は過去runの集計・説明文(歴史的記録)=意味は変えず残置可、ただし文字列定数がkp3v名を参照していないことを確認 |
| `kp3v.NG_PROTECTED`(KP vote側) | er104:40,48,49,162 | 撤去。**`er078.NG_PROTECTED`(非KP統一judge)は残置**。Grep `kp3v\.NG_PROTECTED` = 0 |
| `protected_dissent_blocks` | er104:138,151,204,208,221、test_01:131、test_02:58-61 | 撤去(関数引数・test引数とも) |
| `Voter.protected_diff` | er104:71,82,141,161,213,264,411 | `observed_protected_diff`へ改名(判定に不使用)。Grep `\.protected_diff` = 0(audit読取のみ`observed_`) |
| `make_voter`内`pdiff` | er104:256-264 | 撤去 |
| P-07解釈(b) | CURRENT_SPEC:2937 | 置換(§10) |
| `er108_kp_vote_noguard_01.py` / `_test_01.py` | 本staging | 折り込み後に削除し、testはer104 testへ移設(同名関数) |
Dangling確認: 配線後 `Grep -rn "NG_PROTECTED_DISSENT\|protected_dissent_blocks\|kp3v\.NG_PROTECTED\b" --include=*.py` が(歴史記録2ファイルを除き)0、`.protected_diff`の判定用途参照0、`import er108_kp_vote_noguard_01`が0であること。`test_dangling_reference_*`(er104_kp_vote_wiring_test_01.py:767)方式で静的testを1本追加。

## 6. 既存test更新一覧と追加test一覧
更新(新期待値へ。不整合な出力を期待値にしない): er104_kp_three_asr_vote_01_test_01.py:117-131(Primary protected短絡/dissent/`protected_dissent_blocks=False`)、_test_02.py:50-61,82(行列からpdbを除去)、er104_kp_vote_wiring_test_01.py:179-189(P-05短絡・P-07b dissent)、同:754 allowlist(+er108 cmu importer、**既存失敗の是正**: 現在`er107_fx_kp_audio_ng3_listen_page_01.py`が`import er104_`でallowlist外として失敗しており(NG3 委任_01 commit 8d02ff119由来)、er107は研究用pageとして除外対象に追加)、er105_kp_fulltext_selector_01_test_01.py・er003_test_kp_fulltext_wiring_01.py・er003_test_b1_p2.py・er030_..._m2_supply_01_test_01.py・er062_family_z_writer_01_test_01.py(fixtureのphraseがCMU登録語であること=`phrase1..5`等の数字入り合成語は実在語へ。期待値は変えない)。
追加(現存分は未配線module用): **現状PASS 51件**(`er108_kp_vote_noguard_01_test_01.py` 21件=真理値表4行・保護差全組合せ不変・Whisper失敗・空転写・Azure障害・PASS_WITH_WARNING行・`Pump 1's fist.`->P+W固定fixture・両NG・Production参照0 / `er108_kp_cmu_lexicon_gate_01_test_01.py` 30件=登録語/未登録語/one's/don't/ハイフン/数字/アクセント/大文字/句読点/`novelty minaudière`除外/`pump one's fist`通過/er105実関数でのretry->note->PASS・shortfall・全未登録でINVALID・他不適合は除外しない)。配線時に追加: (a)judge統合test(vote_requiredで`NG_PROTECTED`が出ない/非KPは出る)、(b)G9 `guard_entry`のKP skip/`reuse_blocked`維持/非KP不変、(c)X/Z双方でStore再利用->再判定のtest、(d)`run_kp_with_outer_retry`でcanonicalization後未登録->failures加算・STALE退避、(e)非KP 12,096行バイト一致の再実行(`er104_nonkp_before_after_01.py`)、(f)A/B/Cが`apply_cmu_to_validation`を通らないことのtest。

## 7. runtime evidence計画と見積(委任_02。API費用は7-7の案件300円以下・合計≤40円見込み)
| 項目 | 内容 | 費用 |
|---|---|---|
| ①-R1 | 保存音声(coffee 8本+KP3V 84件)を**配線後の本番adapter(monkeypatchなし)**で再判定し、偽NG回避・偽PASS0を記録(`er108_kp_noguard_reeval_01.py`の無patch版) | 0 |
| ①-R2 | 正式入口のStore再利用gate(`KpVoteReuseGate`/`kp_vote_reuse_ok`)をcoffee b1b最終wavの保存evidenceへ実行(X経路)。Z側は`generate_or_reuse_z`の再利用点6を同型で実行 | 0(ローカルWhisperのみ) |
| ①-R3 | Fableの正式run(新規2記事)中のKP英語で自然発火した行(P+W/S+W/保護差を伴う票)を`kp_dual_check`の`guard_lifted`/`observed_protected_diff`から集計 | 0(既存run成果) |
| ②-R1 | X small_bag a2(`novelty minaudière`を含む本文)のKP段を正式入口で実行: `keywords_runtime_metadata.json`の`attempts_detail[].item_reasons`にCMU診断、retry後の最終KPが登録語のみであることを記録 | 3〜8円(Luna選定+canon+gloss+Redundancy) |
| ②-R2 | Z melosのKP段(a2またはb1b 1レベル)を`run_kp_with_outer_retry_fulltext`経由で実行し、CMU gateが通過(または発火)したことを記録 | 3〜8円 |
| ②-R3 | 自然に未登録語が選ばれない場合の発火証拠: 実Lunaを使わず、保存済みの実Luna出力(`keywords_selector_raw_attempts.json`の`novelty minaudière`)を正式`run_selection_gate`へ再生(mock selector=API 0)。これは**runtime fireではなくtest証拠**と明記し、PRODUCTION_WIRED判定はR1/R2の正式経路で行う | 0 |
合計見込み: ①0円、②6〜16円(上限20円まで見て余裕)=**≤40円**(Fable見積に収まる)。日次1,000円・案件300円に対し十分小さい。

並列化: ①(er078/er104/reuse guard/test)と②(er105/er003 scaffold/test)はファイル非競合で**2系統並列**。SSOT(CURRENT_SPEC/OPEN/DECISION)は最後に1回。runtime evidenceはFableの正式run完了後(共有Store/出力の競合回避)に①-R1/R2(API 0)と②-R1/R2を同時起動。所要見込み: 実装+test各1.5h並列、回帰(§6)+evidence 1h。

## 8. 失敗終了時の最終成果物(目的要件との適合)
- ①: Whisper失敗=技術STOP(再実行で再開可・HRへ送らない)。両NG=通常の再生成->上限でSTOPPED->HR Lock(従来どおり)。最終成果物=NG時も保存音声・転写・`observed_protected_diff`付きevidence(後日人手確認可能)。
- ②: 選定が全未登録(0件)=INVALID->外側retry3回->`OUTER_RETRY_EXHAUSTED`でstale artifact退避(旧KPを後段が読めない=KPMP B1の恒久対策)。**空のKPで進行しない/条件を緩めて通さない**ため、目的『CMU未登録語を含むKPは存在させない』に適合(最悪でもKPなしでSTOP)。

## 9. 失敗モードと対策
| リスク | 対策 |
|---|---|
| 保護解除で偽PASS(誤った数/否定をPASS) | 分類器単独での偽受理0/665(合成)・保存84件で偽PASS増加0。S+W行は`PASS_WITH_WARNING`+事後試聴リスト(P-03維持)。監査に`observed_protected_diff`を残し事後検証可能 |
| `one's`等のCMU誤除外 | 正規化経路集計で誤除外0。未登録は『辞書に無い語』のみ(語形変化`concierges`・アクセント`résumé`は仕様どおり除外) |
| 除外が頻発しretryコスト増 | 実測未登録率2.9%/句。期待追加Luna呼出≈0.08回/レベル(約0.2円) |
| 非KPへ波及 | `vote is None`分岐不変+非KP 12,096行バイト一致test再実行。A/B/Cは`apply_cmu_to_validation`/M2を通らない |

## 10. SSOT更新文案(委任_02で反映)
**CURRENT_SPEC「Key Phrase英語phraseのPrimary・Secondary・Whisper 3-ASR多数決」節**
- P-07解釈(b)を次で**置換**: 「(b)【2026-10-22ユーザー決定により解除】少数側の転写に値・否定差があっても、Key Phrase英語音声の票は本文一致判定(`classify_asr_match`+同音救済)だけで決める。P/S割れは必ずWhisperを呼び2/3でPASS。値・否定差は監査(`observed_protected_diff`)に記録するのみで判定に使わない。`NG_PROTECTED_DISSENT`・Primary保護差短絡(`NG_PROTECTED`のKP投票側)は撤去。非KP音声の最終ANDゲート(値DIFF/否定差)は維持。再利用点の事前guard(`er078_reuse_value_guard_01.guard_entry`)もKP英語ではskip」
- PASS条件表の備考に『保護差の有無は票に影響しない』を追記。『限界/残リスク』に『a2最終wav相当(P・S両NG)は両NGのため救済されない』を追記。
**KPFTブロック(CURRENT_SPEC:1986)**: 末尾に「【2026-10-22追記】Key Phrase選定条件に『構成する全英単語がCMU発音辞書(`pronouncing`/cmudict 1.1.3)に登録済み』を追加(ユーザー承認APPROVED_FOR_PRODUCTION、OPEN-457)。語単位照合(大文字小文字・句読点・アポストロフィ・ハイフン・縮約は正規化、アクセント・語形変化の救済なし)、未登録語itemは選定時点で除外し機械診断noteで再選定、最終attemptでCMU未登録のみが原因なら除外してshortfall確定(数合わせしない)、canonicalization後の`used_form`をX/Z共通外側retry入口で再確認(INVALID扱い)。LLM推測・外部辞書・発音台帳による代替合格は禁止。A/B/C無変更」
**OPEN_ITEMS**: OPEN-457(本件)。Statusは配線後に更新。**DECISION_LOG**: 配線完了時にまとめて1エントリ。

## 11. Opus確認事項(Q形式。条件A=新しい処理フローの設計に該当)
- **Q1(AMBIGUOUS)** 値ガードAMBIGUOUS降格を維持する変種Aを推奨(§2-1)。『数値・否定の不一致の解除』にAMBIGUOUSを含めるべきか。保存データでA=Bのため過不足の観点で問題ないか。
- **Q2(Primary自身の保護差)** ユーザー文言『例外なく適用』に従い、Primary票の保護差による短絡(G2/G6)も解除した。Primary PASSでAzure/WhisperがNGの割れ(P+W要求)ではなく、『Primary自身がDIFF』時にSecondary/Whisperを呼ぶ副作用(Azure呼出増・費用)に問題はないか(追加API=Primary NGかつ自身に保護差の稀なケースでAzure最大1回/件=推測。保存84件の再判定ではAzure実呼出0)。
- **Q3(折り込み方針)** er108 stagingをer104へ折り込み、er108_vote_noguardを削除する案(単一実装)で、`kp_vote_check_v1`のversion文字列を据え置く(additiveな`guard_lifted`フィールド)判断は妥当か。
- **Q4(G9)** `guard_entry`のKP英語skipを呼出元でなくlabel判定(1関数)に置いた案、および`reuse_blocked`明示markは維持する案で、非KP(A/B/C共有Store)への波及がないか。
- **Q5(CMU正規化)** 縮約cliticの閉集合分解(R4)・ハイフン分解(R3)は『CMU未登録語を推測で救済しない』要件に抵触しないか。語形変化(`concierges`)・アクセント(`résumé`)を救済しない判断で良いか。
- **Q6(shortfall)** 最終attemptでCMU未登録のみが原因のとき除外確定(shortfall)する設計は、既存の『内容品質を理由とした再選定はしない(hard requirementのみ)』・『数合わせしない』と整合するか。canonicalization後の不適合は除外でなくINVALID(外側retry)とする非対称は妥当か。
- **Q7(Whisper単独の偽PASS)** S+W行(Primary NG・Azure PASS・Whisper PASS)が保護解除でさらに増える場合の事後試聴リスト運用で足りるか(既存P-03)。

## 12. 引継ぎ(委任_02)
推奨手順: (1)Opus確認(Q1-Q7、並行して実装着手可=ファイル非競合) (2)①実装(er078→er104折り込み→guard_entry→test更新) と②実装(er105→scaffold M2→test)を並列 (3)回帰(§6 a〜f)+Dangling Grep (4)Fableの正式run完了後にruntime evidence(§7) (5)SSOT(§10)・commit・push。判断候補: a2最終wav相当(両NG)の扱いは本変更で解消されない=真理値表の変更になるため**区分D(新しい判断)**。それ以外にユーザー判断は不要(A:原文§2/§3で既判断、B:本設計で自己解決)。
