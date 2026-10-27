# W2_UD1_BODY_REFLECTION_DESIGN_01(LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01 委任_02 / Phase A、設計のみ・API 0・JPY 0、2026-10-28)

原文=`docs/pm/delegation_log/2026-10-28_LR-FALLBACK-UNIFIED-PRODUCTION-WIRING-01_USER.md` §2・§3・§4・§8。共通=`…_委任_00_COMMON.md`。**Productionコード・test・SSOTは一切変更していない**(読取+メモリ内のpython試算のみ。試算スクリプトは作業用scratchpadにあり、repoには置いていない)。Opus条件Aレビュー対象(新しい構造・処理フロー)。
凡例: 【事実】=コード/保存データの読取で確認 / 【試算】=保存データをメモリ内で処理して確認(§10) / 【設計】=本書の提案(未実装) / 【未観測】。

---
## 0. 結論(重要度順)

1. **推奨方式=「派生の表示本文overlay」**。原本(`article.md`・`parts.json`・Writer出力・承認済みスクリプト・`tts_generation_results.json`の`canonical_text`)は**1バイトも書換えない**。LR採用が確定した最終entryから決定論的に「LR台帳(`lr_fallback_ledger.json`)+表示overlay」を**導出**し、ページ描画・ハイライト解決・三者一致検証がその1関数群(新module `er129_lr_display_reflection_01.py`【設計】)だけを通る。理由(実コード根拠):
   - `_generate_or_reuse`は`cached.canonical_text == expected_text`(元原稿一致)でLR音声を再利用する(`er019_family_x_audio_production_runner_01.py:1177-1180`)。`parts.json`をLR後の文へ書換えると**既存LR音声が再利用されず再生成**になり、再生成はLRなしの通常判定になる=LR成功の承認が「本文書換え+再生成」に化ける(W1 §5最終行が警告したGate緩和同等の副作用)。
   - HR Lock key・承認shaは元原稿(`er003_v1_n3_01_assemble.py:96-104`、`BlockProgress.key` `er127_tts_block_policy_01.py:241-247`、chunk親`parent_text=parts[...]` `er019:1436-1452`)。本文を書換えると承認が無効化される。
   - `article.md`のsha変更は`er128.stale_or_rebind`(`er128_kp_confirmed_content_01.py:765-822`)の再バインド+`rv.retire_final_outputs`(最終成果物の退役)を起動する。V3フォーム照合コード`t8`(本文sha先頭8桁、`user_test/selection_form_v3/form_logic.js:266,344`)も無効化。overlay方式は**全て不変**=ユーザー送信済み確定は無傷。
   - `scaffold_article_sha256.json`/Review Queue三者sha(`er019:3430-3560`、RF再実行=API費用)も不変。
2. **反映点は1か所=「ページ描画直前の表示読出関数」**(採用確定時や`parts.json`書換えではない)。X=`_row_info_family_x`へ渡す`parts/support`とハイライトDisplayUnitの手前、Y=`build_page_rows`(`er121_family_y_audio_01.py:1467-1527`)とY highlight units、Z=`build_page_rows`/`full_story_display_units`(`er063_family_z_audio_01.py:2425-2504`)。**最終entryからの導出**なので、初回/retry・fallback/regeneration/resumeの4経路が同じ結果になる(§3-3)。
3. **三者一致検証(表示・TTS入力・ASR正解)はassemble直前のGateに置く**(X/Y=assemble入口で`BLOCKED_LR_DISPLAY_CONSISTENCY`、Z=`run_audio_gate`で`FamilyZLRDisplayConsistencyStop`)。不一致・位置特定不能・確定内容干渉は**技術STOP(HR待ちキューへ入れない)**=ユーザー原文§5「本文と音声の不一致」「確定内容・原作保持違反」は従来どおり停止。正常LR(検証PASS)だけがUD-3の「停止/HR解除」対象になる。**W3(UD-3)との接続条件**: 「正常LR」=ledger verdict=PASS、と定義すればM3/Y gate側は`LOCAL_REWRITE_RECOVERY`の停止解除条件をこのverdictで判定できる(§5-3)。
4. **既公開4件の実態(重要な訂正)**: (i)AI島Std/Advは**未公開・未組立**(`a2|b1b/assembled/`空、M3 BLOCKはk2のみ、`user_test/family_x_ai_island_form_01/hr_01|02.html`はHR試聴ページ)。(ii)Melos Advの不一致ページ`family_z_melos_01`(2026-10-13、run_e2e_02)は**superseded**。ユーザー受入済みの最新`family_z_melos_02`(run_e2e_05/06、LR 0)にはLRがなく不一致なし。(iii)実在・現行の公開不一致は**Word Gacha Adv**と**猿の手Std**の2件。遡及是正は全件API 0、表示語句のみ(§8)。
5. **STOP該当(現時点の保存データ上)=0件**。確定KP/KW・文法・Factとの重なり判定(§4)を実データ5件で試算した結果、全件で重なりなし【試算】。ただし**Zの`Melos→He`は人物名の代名詞置換**であり、判定ルール(§4 T3)の運用に仕様解釈が絡む=判断候補B(§11)。
6. **注意(公開ページへの注記混入)**: 既存Z公開ページ(`family_z_monkeys_paw_01/standard.html`・`family_z_melos_01/advanced.html`)は旧形式で、`Local Rewrite採用(音声は原稿から変更…)`と`Voice/Style`を**公開ページ内**に出している(grep確認)。ユーザー原文§2(注記は最終Human報告資料のみ)と整合させるには、本文反映後は当該注記も公開ページから外し最終Human報告資料へ移す必要がある(§8、判断候補6)。

---
## 1. 現状(事実)とUD-1が要求する差分

| # | 事実 | 根拠 |
|---|---|---|
| F1 | LRは「TTSに送る文」だけを変える。`run_local_rewrite_recovery`は`retts_fn(rewritten_segment)`を呼ぶのみで`article.md`/`parts.json`を書かない。 | `er020_tts_retry_local_rewrite_01.py:757-834`、W1 §2-1 |
| F2 | LR後の英文の保存先=`tts_generation_results.json` segments.<seg>の`text`(LR後)・`canonical_text`(元=表示形)・`canonical_text_before_local_rewrite`(元のTTS入力=正規化済み)・`local_rewrite_recovery.selection.selected.{rewritten_segment,changed_span_*}`。Z形は`audio_text_deviation.{canonical_text_before_local_rewrite,audio_text_after,diff_summary}`。 | `er127_tts_block_policy_01.py:678-692`、`er063_family_z_audio_01.py:1211-1232`、W1 §3-1 |
| F3 | **resume経路のLR記録は`rewritten_segment`のみで`changed_span_*`・`rationale`・7 gateを持たない**(`recovery={…"selection":{"selected":{"rewritten_segment":rewritten}},…,"resumed_without_llm":True}`)。→差分の語句は記録の`changed_span`に頼らず**before/afterから再計算**する必要がある。 | `er127:660-672` |
| F4 | ASR正解原稿の単一参照点=`resolve_expected_text_after_local_rewrite`(LR採用=LR後の文、`HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG`真=原文、Z形は`audio_text_after`)。 | `er020:852-891` |
| F5 | 表示本文の出典: X=`parts[...]`/`support[...]`/`"Today's topic is {title}."`(`er019_..._runner_01.py:2956-3012`、ページ`er019_family_x_listening_page_01.py:80-96`)、Y=`parts["segments"][sid]`・`support`・`res["segments"]["topic_intro"]["canonical_text"]`(`er121:1467-1527`)、Z=`entry["canonical_text"]`(`er063:2459`)。LR後の文はどの描画も読まない。 | W1 §4 |
| F6 | ハイライト(SLOT-23)は(a)解決のdisplay unitと(b)描画が同じ文字列でなければならない: Zは`HL_DISPLAY_UNIT_MISMATCH`(`er063:2527,2576`)、Yは`FAMILY_Y_HIGHLIGHT_TEXT_MISMATCH`(`er121:1515-1517`)、Xはresolverが`x_display_units(parts)`(`er019:3033-3038`)を使い、`resolve_highlights`は**文単位の逐語整列**(`er_learning_highlight_01.py:153-175`、整列できない文はスキップ、cursorは進めない)。LR後の文は整列に失敗しうる。`lr_rebound=True`(`:223-300`、通知`HL_LR_REBOUND`)は既存・未使用。 | 左記file:line |
| F7 | 既存Z公開ページは旧形式で`<div class='note'>Local Rewrite採用…`と`Voice/Style`を公開ページ内に出す(`er063:2374-2390,2463-2468`、ページ実物をgrep確認)。現行の公開builder`_user_page_rows`(`er063:2520-`)は内部情報を載せない。 | grep `user_test/family_z_*` |
| F8 | 確定内容との重なりは**記録のみ・停止なし**(`er128.lr_overlap`/`note_lr_fired` `er128:1236-1284`、`er020:837-847`)。`confirmed_kp_lr_overlap.json`は実在0件。 | W4 §2.1 |

UD-1が要求する差分=「表示本文をLR後に合わせる」+「記録」+「三者一致検証」+「確定内容保護(干渉はSTOP)」。LR/TTS/ASRの動作には一切触れない(試行回数・待機・Fallback Style・LR範囲・ASR基準は不変、原文§7)。

---
## 2. 方式比較(原本非改変の原則を基本とし、代替案を比較)

| 案 | 内容 | 利点 | 欠点・衝突(根拠) | QDC |
|---|---|---|---|---|
| **A(推奨)派生overlay** | 最終entryからledger+表示overlayを導出。描画・ハイライト・検証だけが読む。原本・音声記録は不変 | 再利用キー/HR Lock/承認sha/確定レコードsha/`t8`/RF三者shaが全て不変。resumeでもLR再実行なし。4経路で同結果(導出)。空overlay=従来とバイト同一でA/B/C・非LR run不変 | 描画側の入口が3Family+highlightで計5〜6か所(§3-4)。位置特定アルゴリズム(§4)が必要 | Q高・D速(API 0)・C0円 |
| B `parts.json`/`article.md`の局所パッチ(W1案(i)) | LRの`changed_span`を本文へパッチ | 実装が直感的 | §0-1の全衝突(再利用不能→再生成でLR記録消失=Gate緩和同等、HR Lock key無効、`er128`再バインド+`retire_final_outputs`、`t8`無効、RF再実行=API費用)。plan段階再実行で`parts.json`が元に戻る(`er019:227-262`)=resume/regenで不整合 | Q中(副作用大)・D遅・C増 |
| C LR後の文を新原稿として①から再生成 | 本文を差替え、LRなしで再TTS | 本文=音声が自然に成立 | LRが解決した問題(ASR融合等)を再び踏み再生成費用が出る。「既存LR後音声を使用、再TTSなし」(UD-2)に反する | Q中・D遅・C増 |
| D HR選択肢提示(W1案(i)+(ii)) | 局所パッチをHR packetで人が選ぶ | 最も安全 | UD-1は**自動反映**をユーザーが決定済み(原文§3)。HR増=UD-3の趣旨(正常LRでHR要求しない)に反する | Q高・D最遅 |

→ **A**。原本非改変を維持すれば「記録に残る原本=承認済みスクリプト」と「ユーザーが見る表示本文=音声と一致」を分離でき、ユーザー原文§3「確定済み…原作保持要件を保護」とも整合する。

---
## 3. 処理フロー(単一反映点)

### 3-1. 新module(設計)
`er129_lr_display_reflection_01.py`(番号はPhase Bで空き番確認。現状`er129_*`なし)。純関数中心・API 0・TTS/ASRを呼ばない。公開面は4関数のみ:
- `build_lr_ledger(family, level, run_dir, results, units_ctx) -> ledger`(最終entry群→台帳導出。冪等・追記なし・全置換)
- `apply_overlay(ledger, unit_key, text) -> (text_after, chunk_texts_after, edits)`(表示本文への適用。台帳が空なら**入力をそのまま返す**=バイト同一)
- `verify_three_way(ledger, results, display_units, *, tts_norm_fn) -> verdict`(§5)
- `overlap_with_confirmed(ledger, confirmed_ctx) -> verdict`(§4。`er128`の純関数を再利用)

### 3-2. フロー図(テキスト)
```
[TTS stage 既存・不変]  LR発動? ─yes→ er127.lr_recover → entry{text=LR後, canonical_text=元, canonical_text_before_local_rewrite, local_rewrite_recovery}   (X/Y)
                                   └→ er063.build_entry → entry{canonical_text=元, audio_text_deviation}                                                 (Z)
                              │  (resume=BlockProgress.lr.text再利用 / reuse=cached entryごと再利用 / HR採用=人間承認flag)
                              ▼
[最終entry群 = tts_generation_results.json]  ──── 唯一の入力 ────┐
                                                                  ▼
 ┌────────────── build_lr_ledger(最終entryから導出。Family別アダプタ: X/Y共通・Z) ───────────────┐
 │ 1) 各entryを分類: ADOPTED(LR後文が最終音声) / SUPERSEDED_BY_HUMAN_APPROVAL(flag真=原文) / なし │
 │ 2) before=canonical_text_before_local_rewrite(Zはaudio_text_deviation.before) after=最終音声の文 │
 │    =resolve_expected_text_after_local_rewrite の戻り値(単一参照点を再利用)                       │
 │ 3) トークン差分(§4)→edits[] 4) 表示unit(part/段落/support)内の位置を一意特定 5) ledger保存      │
 └──────────────────────────────────────────────────────────────────────────────────────────────┘
        │                         │                                  │
        ▼                         ▼                                  ▼
 [表示読出] apply_overlay   [確定内容保護] overlap_with_confirmed   [三者一致] verify_three_way
  (ページ・ハイライト)        T1/T2/T3(§4) → STOP/PASS             表示=TTS入力=ASR正解 → STOP/PASS
        └────────────────────────┬─────────────────────────────────┘
                                  ▼  verdict=PASS のみ(§5-3: W3のM3/Y Gateが「正常LR」として停止解除)
 [assemble(音声組立・不変)] → [pages: overlay適用済み本文+(ハイライトはoverlay後本文で再解決)] → [page_verify: 表示==台帳after を再確認]
                                  └→ 最終Human報告資料(W4)は ledger を読む(赤色注記は資料側だけ。本文・TTS・ASR・KP・Style Promptへは書かない)
```
**位置づけ**: X/Y=`stage_assemble_family_x_b1/a2`(`er019:2551,2807`)と`assemble_level`(`er121:1174`)の**Style Gate判定前**にledger導出+検証(§5-3の順序)。Z=`run_audio_gate`(`er063:1908`)内のM2存在assert後・`z_style_actual_gate`前。

### 3-3. 4経路で同じ結果になることの根拠
入力が**最終entryのみ**で、台帳・overlayは毎回全置換して導出する(状態を持たない・追記しない)。経路差は最終entryの差としてのみ現れ、同じ最終entryなら同じ出力。

| 経路 | 最終entryの形 | 台帳の結果 | 根拠 |
|---|---|---|---|
| (a) 初回Production | LR採用entry(`local_rewrite_recovery.status=RESOLVED_BY_LOCAL_REWRITE`、Z形は`audio_text_deviation`) | ADOPTED→overlay適用 | `er127:678-692`、`er063:1211-1232` |
| (b) retry/fallback | LRは3回使い切り後のみ発火(`er127.lr_recover`が`blk._open_ordinal`を閉じてから`:640-651`)。途中のattemptやFallback Styleは台帳のLR部に影響しない(Style変更はFallback側=委任_01/04)。retryで合格した場合はLR記録なし→overlayなし | 最終採用attemptだけを見る。**採用されなかった試行のLRを本文へ反映しない** | `er127:640-651` |
| (c) regeneration | 再生成entryが`segments`を置換。LRなしで通れば`local_rewrite_recovery`が無く、旧overlayは**再導出で消える**(古い台帳を信用しない=`source_results_sha256`不一致なら再導出必須) | LRなし→overlayなし / 再度LR→再度overlay | 冪等・全置換の設計 |
| (d) resume/再利用 | (d-1)`BlockProgress.lr.text`再利用=F3の形(`rewritten_segment`のみ。`changed_span`なしでもトークン差分で復元) (d-2)`_generate_or_reuse`が`cached_result`を丸ごと再利用(`er019:1177-1190`)=LR記録ごと不変 (d-3)Zの`reused_from_previous_run`はprovenance再追記なし(`er063:1587`)でも`entry.audio_text_deviation`は残る (d-4)**`HUMAN_APPROVAL_SUPERSEDES_LR_AUDIO_FLAG`真=原文に戻す**: `resolve_expected_text_after_local_rewrite`が原文を返す(`er020:868-870`、8fbfae04c)ので台帳はSUPERSEDEDでoverlayなし(表示=原文=音声) | 同一entryは同一導出 | 上記行 |

特に(d-4)は**LR記録が残っていても最終音声が原文**の既知3例(Y `y_voice_1`・X Coffee `comment_2`・Z Open Window `c12`、W4 §5.2)を、台帳が`resolve_expected_text_after_local_rewrite`を唯一の参照点とすることで**誤って本文へ反映しない**。

### 3-4. 各Familyの接続点(Phase Bで編集する箇所)
| Family | 表示出典(現行) | 接続(設計) |
|---|---|---|
| X | `_build_level_table`(`er019:3163-`)と公開ページ`er019_family_x_listening_page_01.py:80-96`が`parts`/`support`を`_row_info_family_x`へ渡す。ハイライトは`resolve_x_highlights`(`er019:3052-3075`)が`x_display_units(parts)`を使う | `parts/support`のロード直後に`apply_overlay`済みコピーを作り、**`_row_info_family_x`・`x_display_units`・`resolve_x_highlights`が全てそのコピーを使う**(同じ文字列で解決・描画=F6)。chunk化partは台帳のchunk editsを親partの文字位置へ写像(§4-2)。`plan stage`の`parts.json`書込み(`er019:227-262`)は不変 |
| Y | `build_page_rows`(`er121:1467-1527`)が`parts["segments"][sid]`・`support`・topic_introの`canonical_text`を出す。highlight units=`translate/<lv>.md`由来(`:1431-1440`、TTS前に解決可能) | ページ構築時に台帳を読み`script_block`へ渡す直前でoverlay。**`FAMILY_Y_HIGHLIGHT_TEXT_MISMATCH`は原文同士で比較(従来どおり)したうえで、描画とハイライト再解決の両方をoverlay後本文に揃える**(overlay非空のsegmentだけ`resolve_highlights(…, lr_rebound=True)`をページ時点で再実行)。dev用`⏸`はchunk textsもoverlay後に揃える |
| Z | `build_page_rows`(`er063:2459`)と`full_story_display_units`(`:2487-2504`)と`_user_page_rows`の`HL_DISPLAY_UNIT_MISMATCH`比較(`:2576`) | `row["script"]`と`full_story_display_units`の**2式を共通の`display_text_of(entry)`へ**(`entry.audio_text_deviation.audio_text_after`がADOPTEDのとき適用)。Zはclip=chunk単位なので位置特定は`canonical_text==before`の自明ケース(Melos・猿の手で確認【試算】)。旧形式builderの`notes`の`Local Rewrite採用(…)`は公開ページ出力から外し台帳(最終Human報告)へ移す(F7、判断候補6) |
| 共通 | — | 公開ページ出力関数が「台帳の赤・青・注記語を1語も出さない」ことをlintで検証(§9 U7) |

A/B/C(`er003_v1_*`・Legacy)はUD-1の対象外(原文§1: 方式を無断置換しない)。既存leaf(`voice01`/`news_tail_fix`/`crosslevel`/`n3_tts`)・`er020`・`er127`は**無編集**=`er127_test_golden_01.py`(A/B/C byte同一)が不変であることで確認(§9)。

---
## 4. 確定内容保護: 重なり判定アルゴリズム(語・句の位置照合)

### 4-1. 差分の取り方(位置は「記録のchanged_span」でなくトークン再計算)
```
norm(s):  ’‘→'、“”→"(英語のみ。LRは英語のみ)
tok(s):   re.finditer(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)*", norm(s)) → (小文字語, start, end)   # er128._toks(`er128:1232`)と同系。曲アポストロフィ正規化を追加
before = canonical_text_before_local_rewrite(TTS入力)   after = 最終音声の文(resolve_expected_text_after_local_rewriteの戻り値)
ops = SequenceMatcher(None, [t.lower for t in tok(before)], [t.lower for t in tok(after)], autojunk=False).get_opcodes()  (equal以外)
```
- 許容するop=**`replace`のみ**(語の置換=AI島`AIs→AI agents`、`you’ve→you have`、`Melos→He`、`guest→visitor`)。`insert`/`delete`、および語以外(句読点・記号)がbefore/afterの非変更域で異なる場合は`DISPLAY_PATCH_UNSUPPORTED_OP`としてSTOP(自動で本文へ当てない)。実データ5件は全て単純replaceで挿入・削除なし【試算】。
- 記録の`changed_span_before/after`は使わない。b1bは`"The AIs sent to the"→"The AI systems sent to the"`と文脈語を含むが、トークン差分は`AIs→AI systems`の1箇所に絞れる【試算】=**変更語句のみ**更新(原文§4「今回のLRが適用された該当英文箇所だけ」)。F3(resumeは`changed_span`なし)にも耐える。

### 4-2. 表示unit内の位置特定(一意性必須)
1. 表示unit(X=`part1..3`/`in_one_line`/support各文、Y=segment、Z=clip)のトークン列に対し、`tok(before)`を**部分列として検索**する。**ヒット数==1**のときだけ採用(0または2以上=`DISPLAY_PATCH_UNLOCATABLE`でSTOP)。
2. 各replace opの表示側文字区間を`[unitトークン(h+i1).start, unitトークン(h+i2-1).end]`で求め、**表示側の元の綴り・引用符・句読点はそのまま**にして、置換語はafter側の語(`tok(after)`の`j1..j2`の文字区間)に差替える(曲アポストロフィの`you’ve`も表示側の字形を保ったまま置換できる【試算】)。複数opは後ろから適用。
3. chunk化part(X/Y)は`chunk_plan_<lv>.json`の`plans.<part>.chunks[].text`(`er019:1406-1453`、Zは`ClipSpec`)で各chunkを特定し、chunk→親partの位置へ写像。「置換後の親partをchunk textsへ再分割して全chunkのtoken列がchunk textsと一致する」ことを検証(dev用`⏸`マーカー整合)。
4. 検証: 台帳に`unit_text_sha256_before/after`を記録し、`after`から逆置換した本文のshaが`before`と一致すること(=LR箇所以外は1文字も変わっていない)を機械確認。

### 4-3. 確定内容との重なり(3段、いずれも**STOP/USER_DECISION_REQUIRED**、無断変更なし)
| 段 | 判定 | 既存資産 | 結果 |
|---|---|---|---|
| T1 語句重なり | 確定KP/KW(①②③)の`display_phrase/used_form/key_phrase`のトークン範囲と、`changed`トークン位置が交差(挿入は直前語含む) | `er128.lr_overlap`(`:1236-1259`)をそのまま再利用(純関数) | 交差あり=`CONFIRMED_CONTENT_ISSUE`相当のSTOP。現行は記録のみ→**停止に格上げ**(UD-1「確定内容に干渉する場合は無断で変更せず」) |
| T2 出典文重なり | 確定項目・確定文法の`source_sentence`(`er128._source_sentence_of`/`_grammar_sentences` `:738-762`)がLR変更文を含む(語句は交差しなくても、Part 1の「本文の英文」・日本語訳(`part1_vocabulary_expressions.md`が出典文を引用する)・凍結済み文法解説(G4)が旧文のままになるため) | `er128`の出典文取得を再利用(`_norm_ws`文比較) | 含む=STOP(確定済みの日本語訳・解説は無断で変えない)。AI島Std5・Adv5項目は**全て非該当**【試算】、確定文法0件 |
| T3 Fact/固有名詞/数値 | 変更`before`トークンに(i)数字を含む語 or (ii)Fact Lock台帳(X=`<run>/audit/entity_table.json`、Y=同系台帳、Z=話者表`speaker_table.md`・作品登録名)の語 | 既存の台帳(AI島`entity_table.json`はタイトル/固有名詞のみで`AIs`を含まない=確認済み) | (i)数字の変更=STOP。(ii)台帳語の置換・削除は「当該levelの全文に同語が残る」場合のみ**PASS+`entity_pronoun_substitution`フラグを台帳に記録**、全文から消える・別固有名へ置換=STOP。LR自身の`3_fact_non_contradiction`はLR内Gate(`er020`)で引き続き担保(重複検査ではなく**決定論的な補完**) |

`Melos→He`は(ii)で全文に`Melos`が多数残るためPASS+フラグ(§8で扱い、仕様解釈=判断候補4)。

---
## 5. 三者一致の検証点とGate接続

### 5-1. 検証項目(`verify_three_way`)
LRで台帳に載る各entryについて、以下を**全て**確認する(いずれもAPI 0)。
| # | 比較 | 方法 |
|---|---|---|
| V1 | 表示(overlay後の該当区間) == ASR正解原稿 | `tok(display_slice_after)`と`tok(resolve_expected_text_after_local_rewrite(entry, canonical)[0])`を比較。トークン列正規化連結のshaも記録 |
| V2 | 表示 == TTS入力 | `tok(display_slice_after)`と`tok(entry.text)`(LR後にTTSへ送った文。Xは`BlockProgress.lr.text_sha`=`er127:359-362`とも突合)。Family固有の送信前正規化(X=`n3_tts.tts_safe_news_en`、Z=`_norm_for_tts` `er063:987`)は**本番と同じ関数を注入**(`tts_norm_fn`)し新しい等価規則を作らない |
| V3 | TTS入力 == ASR正解原稿(LR採用時) | `entry.text` vs resolver戻り値(`post_slowdown_expected_text_source`=`local_rewrite_text`と整合) |
| V4 | LR箇所以外が不変 | §4-2-4の逆置換sha一致 + 非LR unitの表示がbyte同一 |
| V5 | SUPERSEDEDのentryは表示==原文==音声 | `HUMAN_APPROVAL…`真でoverlay空・resolver=原文であること |

sha列(`display_sha`/`tts_input_sha`/`asr_expected_sha`)を台帳に残す=最終Human報告(W4)が三者のshaを示せる。

### 5-2. 不一致の扱い(従来Gateのどの停止へ接続するか)
| 事象 | 新Gate結果 | 接続先 | HR待ちへ入れるか |
|---|---|---|---|
| V1〜V5の不一致、`UNLOCATABLE`、`UNSUPPORTED_OP` | `BLOCKED_LR_DISPLAY_CONSISTENCY`(X/Yのassemble summary status。`stage_assemble`は既に`BLOCKED_*`を`run_summary_assemble.json`へ保存して返す形=`er019:2551-2576`、`er121:1174-1199`)/Zは`FamilyZLRDisplayConsistencyStop(FamilyZAudioStop)`(`er063:93-116`の系列) | 「本文と音声の不一致」=技術STOP(原文§5) | **入れない**(音声・LRは正常。表示側の整合異常のため、HRキューへ流すとUD-3の趣旨と逆に人手が増える。原因と台帳パスを表示してFable/担当へ) |
| T1/T2/T3のSTOP | `BLOCKED_LR_CONFIRMED_CONTENT_INTERFERENCE`+`er128._write_issue(kind=CONFIRMED_CONTENT_ISSUE)`(既存機構、`er128:325-360`) | 原文§3「適切なSTOP/USER_DECISION_REQUIRED」 | ユーザー判断(Fableが付与) |
| 全PASS | `lr_fallback_ledger.json.lr_events[].verdict=PASS`、overlay有効 | assemble続行 | — |

### 5-3. W3(UD-3)との接続・実行順序
`ledger導出+検証` →(verdict)→ `Style/M3 Gate`(W3設計)→ gain/timeline/assemble。M3 `LOCAL_REWRITE_RECOVERY`(`er019_family_x_style_profile_01.py:742`)・Y gate(`er121:706-709`)の停止解除条件は「**当該LR eventのverdict=PASS**」(=正常LR)とすれば、「異常LR(意味・Fact・確定内容・本文音声不一致)は停止維持」を機械的に表現できる。W3設計が別の条件を採る場合もこのverdictを入力に差替え可能(接続点は`verdict`1項目のみ)。

---
## 6. 既存確定内容保護(er128 G0-G4)・V3照合・Fact Lock・原作保持との整合

| 対象 | 現行 | overlay方式での扱い | 根拠 |
|---|---|---|---|
| `text_sha256`(`confirmed_selection.json` `article.text_sha256`・`kp_candidates.json`) | 本文(`article.md`)のLF正規化sha | **不変**(overlayは`article.md`を書かない)→**再バインド(`stale_or_rebind`)不要・`retire_final_outputs`起動なし** | `er128:765-822` |
| G0(finalize前後) | 確定後の成果物書換え検知 | 影響なし(finalizeは本機構の前) | `er128:621-672` |
| G1(消費者入口) | 確定レコードと成果物の一致 | 影響なし。新Gateは**G1通過後**(`load_verified_items`)に確定itemを読み、T1/T2判定に使う | `er128:530-586,1331` |
| G2(TTS record) | `_tts_text`が`used_form`と一致 | KP英語はLR対象外(`lr=False` `er127:112`、`lr_recover`の`if not blk.policy.profile.lr: return None` `:641`)なので不変 | W4 §1 |
| G3(公開ページHTML) | Std=`japanese_gloss`表示、Adv=Part 1行の描画 | overlayは本文scriptのみ変更。Part 1行・gloss表示は不変(T2で出典文干渉はSTOP済み)。**page_verifyでG3を再実行**(`verify_outputs` `er128:837-908`)し描画一致を再確認 | 同 |
| G4(文法凍結) | 凍結解説全文・選定文の保護 | T2で文法出典文干渉はSTOP。非干渉なら凍結値に触れない | `er128:912-1190` |
| V3フォーム照合コード`t8`(本文sha先頭8桁) | `form_logic.js:266`、不一致で`kp_confirmed: text_sha256不一致`(`:344`) | **不変**=ユーザー送信済み確定コードは引続き有効(overlay方式の大きな利点) | W1 §5 |
| Fact Lock(X) | Writer段階(`W-1`)の数字規則・Ledger、`scaffold_article_sha256`(`er019:3430-3560`) | 原本不変のためshaも不変。LR後の語はT3で決定論的に補完検査 | `CURRENT_SPEC.md:1165-1181` |
| 原作保持(Z) | `er061`検証は2026-10-12ユーザー決定で撤去。`CURRENT_SPEC.md:1486`「人物名変更…しない」は編集スタイル規定として残り、`check_character_name_rule`はSUPERSEDED(`er026_family_z_fiction_production_runner_01.py:560-575`) | 台帳に`entity_pronoun_substitution`を記録し、T3(ii)の全文残存条件で人物名消失を決定論的に防ぐ。**Melos→Heの許容は判断候補4** | 左記 |
| 日本語訳・JA Support | LRは英語のみ。X/Y/Zの日本語roleはLRなし(`er127:123`) | 不変。Yの`<details>日本語の元原稿`も不変(意味変更はLR 7 Gateで保証済み、T3で数値固定) | W4 §1 |

---
## 7. 記録schema(最終Human報告が読む単一の記録)

### 7-1. 案の比較
| 案 | 内容 | 評価 |
|---|---|---|
| **推奨 案1: run×level単位の導出ファイル `<run>/<lv>/audit/lr_fallback_ledger.json`** | 最終entryから導出する単一ファイル。LR eventsを本設計が定義、Fallback eventsの枠(`fallback_events`)は委任_01/04が定義した形をそのまま受ける(同一ファイル・同一reader`load_ledger`) | 記録形が不統一(X/Yの`local_rewrite_recovery`、Zの`audio_text_deviation`、resume形=F3、人間承認flag)を**1か所で正規化**。**最終採用状態**を表す(採用されなかった試行を含めない=原文§6-C)。LR/Fallback両方を同じ導出元から作るので「実行履歴」と「最終採用状態」の区別を1ファイルで持てる |
| 案2: 既存`er011_output/local_rewrite_recovery/<theme>/<lv>/local_rewrite_recovery_<seg>.json`を拡張 | 既存LR監査コピーへ追記 | 試行履歴(採用・不採用・失敗を含む)でキーが`<theme>/<lv>/<seg>`、`run_id`なし。**最終採用状態の記録ではない**ので不適。既存recordは**変更せず**、台帳の`audit_sources[]`から参照する |
| 案3: `tts_generation_results.json`へ追記 | 結果ファイルへ`display_text`を足す | 再利用キー・shaに影響する危険(`_with_recorded_sha256`・chunk親再構築が書き換える `er019:1107-1122`)。却下 |

### 7-2. schema(`lr_fallback_ledger_v1`、LR部。`built_at`はsha計算から除外=決定論)
```
{ "schema": "lr_fallback_ledger_v1", "family": "X|Y|Z", "level": "a2|b1b", "run_id": "...", "article_slug": "...",
  "source_results_sha256": "<tts_generation_results.json内の関連entryのcanonical化sha>", "built_at": "...",
  "lr_events": [ {
     "event_id": "full_story_part1_k2#lr",
     "segment_id": "full_story_part1_k2", "unit_key": "full_story_part1", "clip_or_chunk_id": "...", "role": "FULL_STORY|TOPIC_INTRO|PREVIEW|COMMENT_n|IN_ONE_LINE",
     "status": "ADOPTED|SUPERSEDED_BY_HUMAN_APPROVAL",           // 失敗LR(HUMAN_REVIEW_LOCKED_*)はeventに載せない(overlayなし・従来のHR/STOP経路)
     "final_audio_text_source": "local_rewrite_text|canonical_text",
     "before_tts_text": "...", "after_tts_text": "...", "before_sha256": "...", "after_sha256": "...",
     "edits": [ { "op": "replace", "before": "AIs", "after": "AI agents", "unit_char_span_before": [a,b], "unit_char_span_after": [a2,b2],
                  "before_tokens": ["ais"], "after_tokens": ["ai","agents"] } ],
     "rationale": { "candidate_id": "1", "text": "<LRの理由>", "rewrite_type": "short_phrase_rewrite", "seven_gates": {...}, "source": "local_rewrite_recovery|resumed(rationale unavailable)|audio_text_deviation" },
     "unit_text_sha256_before": "...", "unit_text_sha256_after": "...",
     "audio": { "path": "...", "sha256": "...", "duration_seconds": 0.0, "lr_block_final_attempt_ordinal": 4, "resumed_without_llm": false },
     "protection": { "t1_phrase_overlap": [], "t2_source_sentence_overlap": [], "t3": { "numbers": [], "entities": [], "flags": ["entity_pronoun_substitution"] }, "verdict": "PASS|STOP_T1|STOP_T2|STOP_T3" },
     "three_way": { "display_sha": "...", "tts_input_sha": "...", "asr_expected_sha": "...", "asr_expected_source": "local_rewrite_text", "verdict": "PASS|MISMATCH_V1|…" },
     "human_approval": { "supersedes_lr_audio": false, "ref": null }, "verdict": "PASS|STOP_*" } ],
  "fallback_events": [ /* 委任_01・04が定義(最終採用attemptのStyle名・切替元・区間)。本書は枠のみ予約 */ ],
  "audit_sources": [ "er011_output/local_rewrite_recovery/<theme>/<lv>/local_rewrite_recovery_<seg>.json", "<lv>/audit/tts_block_progress/<seg>.json", "<lv>/audit/confirmed_kp_lr_overlap.json" ] }
```
- **既存recordとの重複・移行**: 既存の`local_rewrite_recovery`/`audio_text_deviation`/`tts_block_progress`/`confirmed_kp_lr_overlap.json`は**変更しない**(一次記録として維持)。台帳は派生であり再生成可能。`confirmed_kp_lr_overlap.json`の「記録のみ」書込み(`er128.note_lr_fired`)は挙動不変で残し、判定は台帳が行う。旧run(台帳導出前)も台帳を**遡及生成**できる(最終entryから導出、API 0)=既公開4件の遡及是正の材料にもなる。
- 同じ入力(`source_results_sha256`)なら出力は同一(テストU6)。

---
## 8. 既公開4件の遡及是正計画(実施はしない)

保存データ・公開ページ・承認記録を照合した結果【事実】。いずれも**API 0・音声再生成なし・対象語句のみ**。

| # | 記事・Level | 現状(本文/音声/ASR基準) | LR変更 | 学習項目(確定KP/KW/文法)との重なり | ユーザー承認記録 | ページ注記の現状 | STOP該当 |
|---|---|---|---|---|---|---|---|
| 1 | X「AI島」Std(a2) | **未公開・未組立**(`er019_output/family_x_audio_production_wiring_01/ai_island_temple__run_form_prod_01/a2/assembled`空)。M3 BLOCKはk2のみ。`parts.json` part1(chunk k2)=`The AIs sent…`、LR後音声=`The AI agents sent…`(`tts_generation_results.json` `full_story_part1_k2`、候補id=1、全7 gate PASS)、ASR正解=LR後文(`local_rewrite_text`)、減速後再検証もLR後 | `AIs`→`AI agents`(1語) | 確定KP/KW 5件(carried over/taken a detour/card to play/worth paying attention to/obstacle)の語・出典文とも**非該当**【試算】。確定文法0件(`confirmed_grammar.json` items=[]) | UD-2(原文§4)で`AI agents`を正式採用。学習項目はUSER_CONFIRMED(`confirmed_selection.json` state=live、sha `76f80f62…`) | 公開ページ未作成。HR試聴ページ`user_test/family_x_ai_island_form_01/hr_01|02.html`にLR前後併記 | **なし**(`in_one_line`の`AIs with island experience…`は別segmentでLR対象外=UD-2「該当英文箇所だけ」により不変。表示上`AIs`と`AI agents`が同記事に残るがユーザー決定どおり=判断候補7) |
| 2 | X「AI島」Adv(b1b) | 同上(未公開)。`The AIs sent…`→音声`The AI systems sent…`(候補id=2) | `AIs`→`AI systems`(1語。記録のchanged_spanは`The AIs sent to the`だが差分は1語【試算】) | 確定KP/KW 5件(carried over/called on/taken a detour/card to play/obstacle)**非該当**【試算】(sha `00f14092…`) | UD-2 | 同上 | **なし** |
| 3 | X「英単語ガチャ」Adv | **公開中**(`user_test/family_x_word_gacha_01/index.html`。最終commit dffd5b4f4、2026-10-24)。表示=`If you’ve felt that way`(曲アポストロフィ)、音声=`you have felt`(LR `RESOLVED_BY_LOCAL_REWRITE`、part3全体=chunkなし)、ASR正解=LR後。pre-V3 run(確定レコード・Part 2文法なし) | `you’ve`→`you have`(1語) | 確定レコードなし。旧KP 3件(star power/spark curiosity/tug at its sleeve)は該当文に**非該当**【試算】 | **UDR #183(a)(2026-10-24)**=現行音声承認・LR `you've→you have`を承知(`human_approved_segments.json`、`docs/pm/USER_DECISION_REGISTER_01.md:377`)。**本文反映は未承認**(UD-1で今回決定) | ページ注記なし | なし |
| 4 | Z「猿の手」Std | **公開中・現行**(`user_test/family_z_monkeys_paw_01/standard.html`、commit 8cf1f7726、2026-10-24)。表示=`After their guest left, Herbert joked,`、音声=`visitor`(clip `full_story_part1_c10`、`audio_text_deviation`)。`canonical_text==before`(自明な位置特定) | `guest`→`visitor`(1語) | 確定レコードなし(旧KP: sergeant-major/take hold of/rise into the night)**非該当**【試算】 | LR採用は監査記録のみ(Z Gateなし)。ユーザーの明示的な個別承認記録は未確認(公開commitのみ) | **旧形式ページが`Local Rewrite採用(音声は原稿から変更: replace 'guest'->'visitor')`+`Voice/Style`を公開ページ内に表示**(F7) | なし(注記の扱いは判断候補6) |
| 5 | Z「走れメロス」Adv | 対象ページは`user_test/family_z_melos_01`(run_e2e_02、2026-10-13暫定完成候補、`full_story_part3_c1`、表示`Melos drank`→音声`He drank`)。ただし**superseded**: ユーザー受入済みの最新`family_z_melos_02`(run_e2e_05/06、`a52e99f76` 2026-10-23更新)はLR **0件**で表示=音声(不一致なし)。`family_z_melos_01`への入リンクはHTML内0件(直URLのみ) | `Melos`→`He`(人物名→代名詞。全文に`Melos`は多数残存) | 旧KP 5件(sentence someone to death/current/hold out/seize/abandon)**非該当**【試算】、確定レコードなし | OPEN-422 `USER_ACCEPTED_FINAL`(2026-10-21、完成版=run_e2e_06)=最新版はLRなし | 旧形式注記あり | 条件付き(§8-2) |

### 8-1. 「必要十分な修正」の手順(表示語句のみ更新+記録+最終Human報告資料。Phase B後に実施、事前に必ずdry-run差分=API 0)
| 件 | 手順 | 影響ファイル | 公開差替えの承認 |
|---|---|---|---|
| AI島Std/Adv | UD-3のM3解除と本設計のGate実装後、`assemble`→`pages`を通常経路で実行(overlayが`AIs`→`AI agents/systems`を表示へ反映、再TTSなし=既存LR後音声を使用=UD-2)。最終Human報告資料にLR前後を赤色で表示(W4) | `<run>/<lv>/audit/lr_fallback_ledger.json`(新規)、公開ページ(新規作成=差替えではない) | 公開は通常の記事公開運用。UD-2で語は確定済み |
| Word Gacha Adv | (1)台帳を遡及導出(API 0)(2)現行公開ページをoverlay入りbuilderで再描画し、**元ページとのdiffが`you’ve`→`you have`の1箇所だけ**であることを確認できればその出力を採用。差分が他にも出る(builder版差)場合は**既存HTMLの`If you’ve felt that way`1箇所だけを置換する局所パッチ**(grep=1件【確認済み】)(3)音声・他Levelは不変(`you have felt`の音声はUDR #183(a)で承認済みのまま) | `user_test/family_x_word_gacha_01/index.html`、`…/word_gacha__run_wg_01/b1b/audit/lr_fallback_ledger.json`(新規) | **記事単位の承認**(原文§8)。変更は1語・音声不変で、UDR #183(a)承認内容と整合 |
| 猿の手Std | 同様。`After their guest left`(1件【確認済み】)→`visitor`の局所置換+旧形式の`Local Rewrite採用…`注記を**公開ページから外す**(本文=音声となり注記は不正確になる。原文§2は注記を最終Human報告のみとする)→ 注記内容は台帳・最終Human報告資料へ | `user_test/family_z_monkeys_paw_01/standard.html`、`er026_output/family_z_production_e2e_01/the_monkeys_paw/run_sf_prod_01/a2/audit/lr_fallback_ledger.json`(新規) | 記事単位の承認 |
| メロスAdv | まず**公開対象の確認**: `family_z_melos_01`(旧)をそのまま残すか。残す場合は猿の手と同じ手順(`Melos drank`1件【確認済み】→`He drank`、注記除去)。**推奨=superseded旧ページは修正せず、最新`family_z_melos_02`が正でLRなしであることを確認して「実害なし」とする** | (推奨案では)なし | 旧ページの扱い=判断候補5 |

### 8-2. STOP該当の有無まとめ
- 現行保存データで**確定内容(KP/KW/文法/Fact)に干渉する件は0件**(上表、実データ試算)。→UD-1上の必須STOPなし。
- **条件付き**: Melos `Melos→He`は§4 T3(ii)で`entity_pronoun_substitution`フラグ付きPASS(全文に`Melos`残存)。Z「人物名変更しない」(`CURRENT_SPEC.md:1486`)との整合解釈は判断候補4。旧ページを修正対象外にすれば発動しない。
- STOPの形式=§5-2。公開差替えは1記事ずつ(原文§8・既存運用)。無関係な過去記事へは遡及しない。

---
## 9. test計画

### 9-1. 単体(`er129_lr_display_reflection_01_test_01.py`【設計】)
| ID | 対象 | 内容 |
|---|---|---|
| U1 | 位置特定 | 一意ヒット/0件/複数ヒット(→STOP)、曲引用符(`you’ve`)・縮約・複数編集・chunk写像。実データfixture=§10の5件 |
| U2 | overlay | 台帳空→入力と**byte同一**。2回適用=1回適用(冪等)。逆置換でbefore sha一致 |
| U3 | 4経路 | 同一最終entryから同一ledger: (a)初回形 (b)retry後LR (c)再生成でLRなし→overlay消失 (d-1)resume形(`rewritten_segment`のみ。F3) (d-2)reused entry (d-4)`HUMAN_APPROVAL…`真→SUPERSEDEDでoverlayなし |
| U4 | 三者一致 | V1〜V5の合格表+不一致注入(表示を旧文に戻す/TTS入力を差替え/resolverの出典を`canonical_text`に)で各MISMATCH |
| U5 | 重なり | T1/T2/T3を、AI島実データ(非該当)と合成(KP語がchangedに重なる・出典文に含まれる・数字・台帳語の全文消失)で |
| U6 | schema/決定論 | `lr_fallback_ledger_v1`検証、`built_at`除外sha、`source_results_sha256`不一致時の再導出要求 |
| U7 | 混入防止 | 公開ページ出力・TTS入力・ASR正解・KP表示・Style Promptに、赤/濃青の色定義、注記クラス、`Local Rewrite採用`文字列が**0件**(原文§2・§10-9) |
| U8 | 異常維持 | 3-way不一致・T1〜T3はSTOP statusになり、`register_terminal_hr`(HR queue)へ流れない。正常LR(PASS)はSTOPしない |

### 9-2. integration(mock E2E、API 0)
- **X**: AI島a2/b1bの保存結果を凍結コピーしたfixtureで`stage_assemble`(assemble入口まで)→`pages`。期待=表示に`AI agents`/`AI systems`・音声ファイルshaと`tts_generation_results.json`・`parts.json`・`article.md`・`confirmed_selection.json`のshaが**全て不変**、G1/G3 PASS、highlight再解決OK(`HL_LR_REBOUND`通知の有無も記録)。
- **Y**: LR採用のY entry(合成。公開Yに実LR採用なし=【未観測】)で`assemble_level`/`build_page_rows`、`FAMILY_Y_HIGHLIGHT_TEXT_MISMATCH`が原文同士で通りoverlay後と描画が一致。
- **Z**: 猿の手/メロスのZ形entryで`build_page_rows`/`full_story_display_units`/`_user_page_rows`が同じ`display_text_of`を使い`HL_DISPLAY_UNIT_MISMATCH`が出ない。
- **resume/regeneration**: 既存`er127_test_fakes_01.py`のBlockProgress resume fixtureでU3(d-1)をintegration化。

### 9-3. regression対象(必須PASS)と既存golden不変の確認
| 区分 | test | 目的 |
|---|---|---|
| A/B/C byte同一(golden) | `er127_test_golden_01.py`+`er127_test_golden_01.json`(scope外のleaf結果dict・sleep列・prompt列・HRQ行をbyte比較)、`er109_wiring_golden_test_01.py` | **leaf・er020・er127を編集しない**ことの機械確認。加えて`git diff --stat`でこれらのパスが0であること |
| LR/policy | `er020_tts_retry_local_rewrite_01_test_01.py`・`er020_tts_retry_local_rewrite_fullseg_test_01.py`・`er020_lr_post_rewrite_expected_text_fzaq2_test_01.py`・`er020_lr_post_rewrite_m1_anchor_fzaq3_test_01.py`・`er020_tts_local_rewrite_natural_english_qa_trial_02_test_01.py`、`er127_tts_block_policy_01_test_01.py` | resolver・resumeの不変 |
| 確定内容保護 | `er128_kp_confirmed_content*_test_01.py`(7本)、`er128_kp_highlight_test_01.py`、`er128_form_readable_restore_test_01.py` | G0〜G4・照合コード不変 |
| ハイライト | `er_learning_highlight_test_01.py`(`test_lr_rebound_notice` `:194`)、`er019_x_highlight_wiring_test_01.py`、`er121_y_highlight_wiring_test_01.py`、`er026_z_highlight_wiring_test_01.py` | overlay空でバイト同一・非空で整列 |
| 描画/ページ/chunk | `er019_family_x_audio_production_runner_01_test_01.py`、`er121_family_y_runner_01_test_01.py`・`er121_family_y_page_pause_test_01.py`、`er063_family_z_audio_01_test_01.py`、`er117_x_chunk_wiring_test_01.py`・`er117_z_chunk_wiring_test_01.py`・`er117_std_chunk_wiring_test_01.py`・`er121_family_y_std_chunk_test_01.py`・`er063_z_std_chunk_test_01.py` | chunk親・ページ行・dev用`⏸`不変 |
| HR/承認 | `er011_human_review_lock_01_test_01.py`、`er121_e1_hr_adopt_r0_01_test_01.py`、`er121_family_y_hr_approval_guard_test_01.py` | HR Lock key=元原稿、人間承認flag |
| Z gate/E2E | `er063_family_z_style_actual_gate_test_01.py`、`er026_family_z_e2e_integration_test_01.py`、`er026_family_z_fiction_production_runner_01_test.py` | Z gate順序・stage |
| 空台帳=バイト同一 | 上記ページtestに「LR eventなしrun=従来出力と同一」ケースを追加 | 非LR run不変 |
- **runtime evidence(Phase B、API 0)**: (1)AI島(実データ)で`assemble`→`pages`→ledger+三者sha、(2)猿の手・Word Gachaの現行公開ページとの差分(1語)、(3)Zメロス(run_e2e_02)でledger導出。**Yの実LR採用run=【未観測】**(公開Yに実在なし)→既存evidence run再処理+mockで代替し、残りは自然発生のmonitor(OPEN-283型)。有料API実行は不要(表示・検証は保存データのみ)。

---
## 10. 実データ試算(読取・メモリ内、5件)【試算】
`tts_generation_results.json`/`parts.json`/`chunk_plan_<lv>.json`を読み、§4-1/4-2のアルゴリズムをメモリ内で実行した結果(repoへの書込みなし)。
| 件 | unit_text | before→after(差分) | 位置ヒット | 結果 |
|---|---|---|---|---|
| AI島Std `full_story_part1_k2` | `parts.part1`(chunk k2を含む) | `AIs`→`AI agents` | 一意 | replace 1語のみ(unit長 795→801) |
| AI島Adv `full_story_part1_k2` | `parts.part1` | `AIs`→`AI systems`(記録changed_spanは`The AIs sent to the`) | 一意 | replace 1語のみ(893→900) |
| Word Gacha Adv `full_story_part3` | `parts.part3` | `you’ve`→`you have`(表示側は曲アポストロフィ) | 一意 | replace 1語、表示側字形を保持(849→851) |
| メロスAdv(run_e2e_02) `full_story_part3_c1` | clip `canonical_text` | `Melos`→`He` | `canonical_text==before` | replace 1語 |
| 猿の手Std `full_story_part1_c10` | clip `canonical_text` | `guest`→`visitor` | 同上 | replace 1語 |

確定内容重なり(`er128.lr_overlap`+出典文照合): AI島は`confirmed_selection.json`のitems(Std5/Adv5)で**T1/T2非該当**、Word Gacha/猿の手/メロスは確定レコードなしで旧KP語との重なりなし。実データは全て単純replaceで`insert/delete/句読点差`は0件。

---
## 11. 判断候補(区分付き。ユーザー決定済みのUD-1/2/3・色表示・試行回数不変は再質問しない)

| # | 内容 | 区分 | 根拠・推奨 |
|---|---|---|---|
| 1 | 方式=派生overlay(原本非改変)+導出台帳。反映点は描画直前の1関数群、検証は`assemble`直前Gate | **B(Fable判断+Opus条件A)** | ユーザーは「本文反映」を決定済み(原文§3)。方式は仕様候補ではなく実装設計。原本を書換える案Bは再利用キー・承認sha・確定レコード・`t8`・Gate緩和同等の副作用(§0-1)で不適 |
| 2 | 三者不一致・位置特定不能は**HRキューへ入れず技術STOP**(正常LRは通す) | **A(既存仕様内で自己解決)** | 原文§5「本文と音声の不一致は従来どおり停止」「正常LRでHR解除」。HRキュー投入はUD-3の趣旨と逆 |
| 3 | T1(確定語句重なり)・T2(出典文重なり)を**記録のみ→STOPへ格上げ** | **A** | 原文§3「確定内容に干渉する場合は無断変更せずSTOP/USER_DECISION_REQUIRED」の実装に必要。現行は記録のみ(F8)=承認済み設計原則との矛盾の是正(11-8) |
| 4 | T3(ii): Z人物名の代名詞置換(`Melos→He`)を「全文に残存すれば許容+フラグ」とするか | **B**(`CURRENT_SPEC.md:1486`「人物名変更しない」と2026-10-12のer061撤去の境界の解釈。Fable/Opus判断。「許容しない」と決める場合のみユーザー判断=D) | 旧ページ`family_z_melos_01`を修正対象外にすれば発動しない |
| 5 | `family_z_melos_01`(superseded旧版)を是正対象とするか(推奨=対象外、最新`family_z_melos_02`はLR 0で不一致なし) | **B**(原文§8の列挙と実データの差。監査時点の旧ページ同定の可能性) | Fable判断で足りるが、最終報告で明示 |
| 6 | Z既存公開ページ(猿の手Std・旧メロス)内の`Local Rewrite採用…`/`Voice/Style`注記を、本文反映時に公開ページから外し最終Human報告へ移す | **A寄りB**(原文§2「学習者向け公開ページ・注記は最終Human報告のみ」の既決事項の遡及適用) | 注記が公開ページに残る現状は§2と矛盾(F7)。本文反映後は注記内容(音声は原稿から変更)自体が不正確になる |
| 7 | AI島の`in_one_line`に`AIs`が残る(LR対象外segment)ことの扱い | **C(軽微・実害なし)** | UD-2「今回のLRが適用された該当英文箇所だけ」により仕様どおり |
| 8 | 既公開2件(Word Gacha Adv・猿の手Std)の公開差替え | **B**(通常運用=記事単位承認。原文§8で既定) | 1語・音声不変、UDR #183(a)承認と整合。差替えは記事ごとに最終Human報告→承認で実施(一括遡及しない) |
| 9 | ledgerの`fallback_events`枠の定義 | **C**(委任_01/04の成果物と統合) | 本書は枠のみ予約。統合はFable |

**D(真に新しいユーザー判断)=現時点なし**。ただし判断候補4で「Z人物名→代名詞LRを許容しない」とする場合のみDへ昇格。

---
## 12. 未観測・限界・次の一手
- 【未観測】Yの実LR採用run(公開Yに実在せず)。mock+既存evidence run再処理で代替(Phase B)。TTS前正規化関数(`tts_safe_news_en`/`_norm_for_tts`)とトークン一致の実等価性は、Phase Bで**W4 §3の43 LR entry全件にAPI 0で適用して偽STOP 0件**を確認してから配線する(最初の実装ステップ)。
- 【未実行】ledger導出の実装・page_verify統合・Z旧形式注記の移行。
- 影響範囲(Phase B見積): 新module1+test1、編集=`er019_family_x_audio_production_runner_01.py`(`_build_level_table`/`x_display_units`/`resolve_x_highlights`/`stage_assemble_*`)・`er019_family_x_listening_page_01.py`・`er121_family_y_audio_01.py`(`build_page_rows`/`assemble_level`/highlight)・`er063_family_z_audio_01.py`(`build_page_rows`/`full_story_display_units`/`run_audio_gate`/旧形式ページnotes)・`er026_family_z_fiction_production_runner_01.py`(`_resolve_level_highlights`/`stage_pages`/`stage_page_verify`)・`er128`(T1/T2判定の公開関数追加。既存関数は無変更)。**leaf(`voice01`/`news_tail_fix`/`crosslevel`/`n3_tts`)・`er020`・`er127`は無編集**。
- 新規OPEN登録の分類(登録はFable): 「公開Z旧形式ページへのLR注記混入(F7)」=**修正へ進む**(承認済み仕様§2との矛盾の是正、同一委任内で着手可)。「`family_z_melos_01`の扱い」=**実害なし(superseded)**だが判断候補5。
