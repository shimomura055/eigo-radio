# OPUS_REVIEW_01: KP-GATE-DROP-BACKFILL-PRODUCTION-01 委任_01設計のOpus独立技術レビュー結果(条件A、逐語。Fable転記)

判定: GO with changes(M-1〜M-7必須、R-1〜R-10原則採用)。依頼文=`2026-10-26_KP-GATE-DROP-BACKFILL-PRODUCTION-01_OPUS_REQUEST_01.md`。以下はOpus返信の逐語。

## 1. 結論: GO with changes(修正すれば進めてよい)

理由:
1. 設計の核は承認原文§3-1〜3-2と合っており、委任_02へ進められる。核とは、候補組立後の`dropped`で数える方式(救済済み候補が構造的に除外へ数えられない)、補完は1回だけ、補完分は末尾へ追加、2-Vの本文を変えない、の4点。
2. ただし計数の取りこぼしがある。Prompt 2(call1、上位3件を選ぶ1回目の呼出)で最終attemptにitem単位で除外された句が、er119の`dropped`に届いていない(M-1)。
3. 外側retry(候補全件を作り直す再試行)の扱いの前提に事実誤りがある。CURRENT_SPECには記載がある(M-2)。さらに、`rescued_not_auto`の条件を残すと§3-1に反する(M-3)。この2点はユーザーへ区別して報告する事項。

## 2. 論点別判定

| 論点 | 判定 | 根拠(ファイル:行) | 修正 |
|---|---|---|---|
| P1 除外の定義・救済との順序 | 方式は妥当。ただし取りこぼしあり | call1の最終attemptで除外された句(`cmu_excluded` er108:274-279、`exclusion_dropped` er105:420-427)は、metadataのjsonにしか残らない(er105:562-574)。戻り値にも含まれない(er105:575-578)。er119は`dropped = list(v2["dropped"])`でcall2の分しか持たない(er119:214)。このためDESIGN §2の方式ではcall1の除外が数えられない。(i)の救済前の元句(R6)はstageをsource名にして除外され、1回だけ数えられる(er119:86-90)。二重計上はない。(ii)canonicalization INVALIDで除外したitemは`dropped`に1回だけ入る(er119:253)。全体失敗は技術失敗の扱い(:261-267)。(iii)`rescued_not_auto`は`cands`に残るので数えない。これは正しい | **M-1**: call1の最終attemptの除外をcall1の除外として数える。手段は2つ。er119がwork dirの`keywords_runtime_metadata.json`(`attempts_detail[-1]`)を読む方法なら、er105を変えずに済む。もう1つはer105の戻り値にkeyを足す方法。testを追加する。**R-4**: Eはphrase_keyで重複を除いてから数える |
| P2 human_ng・excludedを数えるか | 数える案に賛成。別カウンタも妥当 | 現行call2はLLMにNG句を見せていない。`run_vocab_selection`は`build_user_message(text, already)`だけで、noteを渡さない(er119:49)。`ex_keys`による機械除外だけである(er119:45,88)。このためRESELECTION(人間の再選定要求)のroundでは、AIがNG句を再び選ぶ可能性が高い。数えなければ候補が細る。前roundでユーザーがNGにした句そのものはこのroundの`dropped`に入らないので、数えられない。これは正しい。reselect上限・多層のNG復活防止とも矛盾しない | なし |
| P3 2-Vの再利用 | 条件付きで妥当 | DESIGN §4は「既存noteを添える」と書くが、`run_vocab_selection`にnoteを受ける引数がない(er119:37-49)。`p2v.build_user_message`はnoteを受けられる(er119_kp_prompt_2v_01:63-67)。ただし2-Vにnoteを後置した実績はProductionにない。Prompt本文(sha)は変わらないので「新Prompt」には当たらない。それでも新しい入力構成なので報告では明示する。noteの括弧書き「無理に3件に揃えず」(er105:394)は2-Vの「最大5件」と文言が食い違う。ただし趣旨は数合わせの禁止で同じなので、許容できる。余った候補を捨てるのは正しい(HR限定候補として残すと件数がEを超え、§3-1に反する)。7+5のslotで初回Promptを使い回す主張は、構造としては妥当。ただし将来のPromptが未採用なので検証できない | **M-7**: `run_vocab_selection`(er119内)に引数を足すことをDESIGNへ明記する。2-Vの本文が変わらないことをtestで担保する(prefix_intact・sha)。**R-2(任意)**: 選定Gateを通った候補(最大5件)すべてにGateの全段を通し、全段通過後に先頭N件を採る。canonicalizationが少し増える代わりに補完の充足率が上がる |
| P4 外側retry | **gate_dropped条件の撤去(R1)は採用でよい。ただし分類の前提に誤りがある** | CURRENT_FLOW §3は「CURRENT_SPECにM-7cの記載なし」とするが、CURRENT_SPEC.md:2021(救済方式、APPROVED_FOR_PRODUCTIONの節)に「外側retry=`n_auto<3 and (gate_dropped or 救済済みauto不可あり)`(Opus M3)」と明記されている。一方、救済のユーザー原文にretry条件の指定はない(該当はdelegation_log …RESCUE…_USER.md:57「retry…での救済結果の一貫性」だけ)。したがってこの変更は「承認文のない実装規則」ではない。「承認済みの節に記載された実装規則を、より新しい明示承認(§3-1)に合わせて変える」挙動変更である。STOPまでは不要と考えるが、ユーザーへの区別報告とCURRENT_SPEC:2021の更新が必要。(ii)n_auto<3のまま確定するのは`auto_select`の「不足は不足のまま」(er119_kp_human_review_01:539)と§3-2「上限未達を許容」に合う。ただしAUTOでn_auto=0になるとSTOPする(同:1338-1339)。R1でSTOPの頻度が上がりうるので報告する。(iii)`rescued_not_auto`条件を残すのは**不可**: 救済済み候補は§3-2のいう「救済で正式な候補として残ったもの」、つまり初回に合格した候補である。revert救済は「HR限定になる見込み」(CURRENT_SPEC:2021)なので、この条件は頻繁に成立しうる。成立すると初回候補と補完分をまとめて捨て、§3-1に反し、費用も無駄になる | **M-2**: CURRENT_FLOW §3・DESIGN §9の事実記載を直し、分類を改める。**M-3**: backfillがONの間は`rescued_not_auto`条件も撤去する(TBF18(c)の期待値も変える)。残す場合は区別報告が必須で、retryの判定を補完より先に行う(R-7)。候補0件(`not cands`、er119:363)と技術失敗のretryは残してよい。失われる合格候補がないため |
| P5 call1の全件再選定(K0/K1) | **K0を推奨。K1は承認済み仕様の変更に当たる** | attempt内の機械診断noteによる再選定は、承認済み記載に含まれる(CURRENT_SPEC:2010「再試行時の機械診断noteを本文の後ろへ追記」、ユーザー追加承認2026-10-22。:2016 CMU M1「未登録語itemはINVALID+機械診断noteで再選定」、APPROVED_FOR_PRODUCTION)。K1はこれを変えるのでユーザー判断が必要。影響範囲: 引数は`sc.run_key_phrase_selection`→`_run_key_phrase_selection_fulltext`(er003:296-365)→`run_fulltext_selection`→`run_selection_gate`と渡すことになり、DESIGN §8の「er003は無変更」と矛盾する。旧経路の`run_kp_with_outer_retry`(er003:754・er062:1350)も同じ関数を使う。A/B/Cは`strategy_l`経路なので実行時の影響はないが、ファイルとしてはer003を共有している。品質面では、Prompt 2による上位3件の選び直しの機会を失い、2-Vの末尾の句が繰り上がる。attemptがINVALIDの時点ではまだ「候補」が存在しない、と解釈できる(machine noteも「不適合でなかった語句はそのまま使ってかまいません」と書く、er105:382)。このためK0で§3-1との矛盾は限定的 | K0で実装し、残る差を区別報告・OPEN化する。M-1(最終attemptの除外を数える)はK0でも必須 |
| P6 重複・同じNGの防止 | おおむね十分。ただし実装上の罠がある | `run_vocab_selection`では、LLMに見せる`already`と包含判定の比較先が同じ変数でつながっている(er119:43-44,83)。already=現存候補すべてをそのまま渡すと、`duplicate_of_top3`が現存候補すべてとの比較に変わり、Gateが黙って厳しくなる。DESIGNの「比較先はcall1のまま」は既存Gateの意味として正しい(現行もcall2同士の包含は判定していない)。`phrase_key`はNFKC・空白・小文字化だけで、原形の違いは区別しない(er105:360-361)。表層形が違っても基本形化後に同じ`used_form`になる重複は残る。補完1回+除外理由の提示で十分。理由が同じNGの再発は不合格のまま許容 | **M-5**: 表示用の`already`と`containment_refs`を明示的に分け、その分離をtestで固定する。**R-3**: 基本形化後の`used_form`が既存候補と完全一致したら捨てる(Nに数えない) |
| P7 resume・再生成・失敗時の続行 | 妥当。ただし制御構造に注意 | 読み戻し(er119_kp_human_review_01:1283-1309)なので、補完の再課金は0。補完導入前の保存docに補完を後から足さないこと(現行の読み戻しなら自然にそうなる)。`_gate_chain`の抽出元には外側ループの`continue`/`return OUTER_RETRY_EXHAUSTED`が埋まっている(er119:232-237,261-267) | **M-6**: `_gate_chain`は外側ループの制御を持たず、statusを返す。補完側の全体失敗・live 0は`backfill.status=FAILED`とし、初回候補で続行する(test必須)。**R-8**: 技術失敗だけを捕捉する。routing違反などの`FulltextSelectionError`(er119:61)とSTOPは握り潰さず、従来どおり伝播させる |
| P8 kill switch・A/B/C不変・配線 | 妥当 | `EIGO_KP_RESCUE`と同じ形(er125:48-53)。承認済み機能なので11-7の限定例外は不要。`"0"`で外側retry条件(M-3を含む)ごと現行へ戻すのは、安全な戻し先である。配線点B1の行番号「:346-349の間」はRedundancy QAの後(er119:327-345が後ろにある)。DESIGNの「QAの前」と食い違う | **M-4**: 補完のAPI呼出の前に`stop_check_fn`を呼ぶ(新しい課金点でSTOP通知を迂回しない)。**R-10**: 配線位置はai_rank付番・Redundancy QAの前(:326付近)と明記する。**R-6**: `_gate_chain`抽出は単独のcommitにし、E=0とOFF時に候補docが完全一致することを示してから機能を足す。flagは生成1回につき1回だけ読み、docに記録する |
| P9 evidence | 方針は妥当だが観測が足りない | replay(凍結した初回出力+実LLMの補完)は「正式な関数の動作証拠」にはなる。しかし受入2「正式候補生成経路での動作証拠」の主証拠にはしない方がよい(§6「DEV経路の成功で全Family完了としない」) | **R-9**: freshで自然に補完が発動しなかったFamilyはfreshを追加する(1回約¥2)。追加で観測するもの: call1最終attemptの除外が計数されること(M-1)、補完候補がHR依頼書`render_request_md`とフォームのJSONに出ること、Zの補完候補にSRC D1と人称整合がかかること、AUTOでのn_auto<3(または0)の挙動、`rescued_not_auto`の扱い(M-3) |
| P10 コスト | 妥当 | 1発動あたり約¥0.7〜1.0。2つの外側retry条件を撤去すれば全件再生成(1周約¥1.0〜1.9)が減る。M-3まで含めると減る方向がさらに強い。R-2を採っても追加は1発動あたり約¥0.1〜0.3の見込み(未実測) | なし |
| F-1 単語枠 | **区別報告が必要** | 現行の候補プールは単語とフレーズの混在で(CURRENT_FLOW §2、er119_kp_human_review_01:552-554)、補完は種類を区別しない。単語が除外されても、フレーズで補完されうる。Prompt 2/2-Vの条件は「5語以内」で(er105:56-61)、§3-3の②「1語」を課す単語専用の抽出は現行経路にない。①③④はPrompt条件に含まれ、⑤は必須化されていない(順位逆転はない) | **R-1**: 候補ごと・除外ごとに`kind`(`word_count==1`なら単語)を記録し、E_word・E_phraseを分けて数える。2-Vの返答から種類別に先頭E_word件・E_phrase件を採るローカル規則なら、Promptを変えずに§3-1の種類別の例に沿える。不足は許容 |
| F-2 フォームとのデータ契約 | 不足あり | フォームは「フレーズ最大7・単語最大5」で、現行プールは最大8件の混在。単語・フレーズの分類はフォーム側の採用枠の判断を伴う(原文§4「採用枠…区別して報告」) | 候補ごとに`kind`・`origin`(call1/call2/backfill)・`ai_rank`・`auto_eligible`・`flags`(qa_fail/gloss_hr_pending/similar_to_ng/rescued/redundant_with)・`rescue`(元句・理由コード)・`human_selectable`を渡す。レベルごとには`backfill`(triggered/E(種類別)/N/status/dropped)と`shortfall`。これらを契約として固定する(R-1と同じ) |

## 3. ユーザーへ区別報告すべき事項

1. **外側retry条件の変更(M-2/M-3)**: CURRENT_SPEC:2021(救済方式・APPROVED節)に記載された`n_auto<3 and (gate_dropped or 救済済みauto不可)`の全件再生成を、§3-1に従って撤去する。挙動変更である。影響はAUTOでのKP件数減と、0件時のSTOP(er119_kp_human_review_01:1339)の頻度増の可能性。
2. **call1のattempt内再選定は残す(K0)**: 承認済みの機械診断noteによる再選定(CURRENT_SPEC:2010,2016)は変えない。§3-1と字面上の差が残ることを開示し、K1(item単位の除外+補完)はユーザー判断事項とする。
3. **2-Vへ既存の除外noteを後置する**: Prompt本文は変わらないが、新しい入力構成である(M-7)。新Promptではない。evidenceで指示が守られないと分かり件数の文言が必要になった場合は、その時点で「新Prompt」として報告する(DESIGN §4どおり)。
4. **単語枠の不在(F-1/F-2)**: 現行経路では単語・フレーズの補完が種類を区別せず、§3-3の単語抽出は将来の7+5 Prompt採用待ちである。フォームの7+5表示に対し、現行プールは最大8件の混在。種類別の計数(R-1)を採る場合も、その旨を報告する。

## 4. 見落としリスク

- Zの人称整合は、出力先`out_dir`が初回と同じ`{work_dir}/gloss_person_repair`に固定されている(er119:147)。補完で監査用の成果物が上書きされうる(R-5: 補完用のdirを分ける)。
- 補完の`candidate_id`が既存と衝突すると、reviewの`verdicts`(candidate_id単位)が壊れる。完全一致で捨てる処理は必須。
- 技術失敗によるretry(call2失敗など)はcall1の合格分も作り直す。まだ候補が成立していないので許容範囲だが、記録に残す。
- AUTOでの実際の運用頻度(宣言付きrunの比率)は未確認。M-3による件数減の影響度は未測定。
- DESIGN_03 §1・§5は直接読んでいない。救済の順序はコード(er119:83-90,308,324、er125:639-642)とCURRENT_FLOWで確認した。

## 5. 5行要約

1. GO with changes。補完の核(dropped基準・1回・末尾追加・2-V本文不変)は原文に合う。
2. 必須: call1の最終attemptの除外を数える(M-1)、STOP確認(M-4)、already/包含比較先の分離(M-5)、`_gate_chain`のstatus化(M-6)、noteの引数追加(M-7)。
3. 外側retryはCURRENT_SPEC:2021に記載がある。gate_dropped条件に加えて`rescued_not_auto`条件も撤去し(M-2/M-3)、挙動変更としてユーザーへ報告する。
4. call1の再選定はK0(承認済み仕様。K1はer003にも波及しユーザー判断)。単語枠の不在とフォーム7+5との差も区別報告する。
5. evidenceはreplayを補助とし、fresh自然発動・HR依頼書/フォーム表示・Z SRC D1・AUTOの件数減を追加で観測する。
