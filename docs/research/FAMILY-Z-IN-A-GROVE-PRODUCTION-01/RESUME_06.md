# RESUME_06 (FAMILY-Z-IN-A-GROVE-PRODUCTION-01 委任_06)

## 1. RESTART_STORM解除(Fable承認)
- 22:39:26 `--clear-stop --reason "...委任_06: RESTART_STORM(...)をFable承認で解除。audit記録"` rc=0。removed=[run_sf_prod_01/STOP, RESTART_STORM_LOCK.json]、stop_all_still_present=false(STOP_ALL不触)。
- audit記録: `run_sf_prod_01/audit_stop_sentinel.jsonl` 2行目 event=CLEARED, pid=29324, previous.reason=RESTART_STORM(22:37:23生成)。解除後 STOP/LOCK は存在しない。
- stop_check_06.json: stop=false, rc=0(開始時)。

## 2. kp起動(計2起動、間隔>150秒、300秒窓に3起動なし)
- 22:43頃(ts1793195003) `--stages kp --regenerate-stage kp_a2`: rc=2 FamilyZProvenanceMismatchStop(part2_cand_a2 がstale、明示再生成が必要)。API 0。
- 22:51頃(ts1793195485) `--stages kp --regenerate-stage part2_cand_a2`: rc=4 KP_REVIEW_PENDING(正常)。part2_cand_a2再生成+Std KP候補生成。provenance `downstream_stale`=[](空)。
- Std kp候補sha(candidates_sha256)= f48b52514ec544083dbdb0b3e4006c41fa2ad707f7b97065d180fef577f79344、本文sha 8ec5e76f9381…。Std文法candidates_sha=4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945。
- 注意: kp_a2自体の明示再生成指定は不要だった(part2_cand_a2再生成で候補が新本文sha 8ec5e76f9381に追随)。
- 費用: 2起動で10呼出(入力27,339/出力17,465トークン)、推定約¥1.6(委任_05実績比の概算。累計約¥38.6/Cap¥70)。

## 3. Std候補一覧(review_request.md 逐語)
level=a2 round1 / candidates_sha256 f48b52514ec54408… / 本文sha 8ec5e76f9381
| 番号 | AI推奨 | 英語表現 | 本文中の意味 | 出典文 | AI理由 | 旗 |
| 1 | KP | through a medium | 霊媒を通して | I heard him speaking kindly to her," Takehiro's spirit said through a medium | 霊媒を介して意思を伝える表現です。 | |
| 2 | KP | on silent feet | 足音を立てずに | Someone came slowly towards me on silent feet | 足音を立てずに進む様子を表す文学的表現です。 | |
| 3 | KP | sink into the darkness | 死の闇へ沈んでいく | I sank into the darkness and never came back | 闇へ沈むように消えていく詩的な言い回しです。 | |
| 4 | 単語 | constable | 警官 | I caught the famous bandit Tajomaru near the bridge," the constable said | 警察官を指すやや改まった語で、報道などでも使われる。 | |
| 5 | 単語 | drown | 溺れる | I later tried drowning myself, but I failed | 「溺れること」を表し、事故や救助の文脈で使える。 | |
| 6 | | dagger | 短剣 | She fought with her dagger | 短剣を指す語で、歴史・物語の描写に使われる。 | |
| 7 | | bandit | 盗賊 | I caught the famous bandit Tajomaru near the bridge," the constable said | 物語や歴史の文脈で幅広く使われる語です。 | 補完候補(Gate除外の代替) |
Gate除外: woodcutter(CMU未登録語)。
文法(Part 2): 候補0件(grammar_candidates.json: 唯一の同格句 P4 "Takehiro, a kind samurai, married my daughter Masago" が resolve_fail/TV=LOW/mid_cond で不適格、他13段落は特徴なし)。解説items=[]、status=NO_CANDIDATE_UNREVIEWED。
(Adv b1b は不変: KP候補9件[cold contempt/The thicket fell silent/on soft feet/sink for ever/trampled/constable/veiled/seize/medium]、文法0件。)

## 4. フォーム
- data: user_test/selection_form_v3/data/in_a_grove__a2__prod.json(export_form_data_01.py --grammar-study-dir 経由。phrases=3, words=4, grammar=0, grammar_status=no_candidates_found)。articles.jsonへ slug=in_a_grove level=a2 を登録(Advの直前)。
- URL: https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/index.html?a=in_a_grove__a2 (Std) / ?a=in_a_grove__b1b (Adv)
- HTTP 200実測とcommit/pushは RESULT_PACKET_FZIG6.md 参照。

## 5. Fable注記
- 訳ずれ: 候補3「sink into the darkness=死の闇へ沈んでいく」(委任_02指摘の「命が尽きる」より本文に近い訳へ変化)。候補5 drown「溺れる」は出典文が「drowning myself(入水自殺未遂)」で一般義。
- 文法: Std旧Top1/Top2(同格句重複)は、本文是正後の再抽出で候補0件に変化。Top1/Top2重複問題は解消(0件)。Std/Adv双方とも文法0件=declare/選択なしで進む設計(ユーザーが0件確認する運用)。Part2 0件は仕様上許容(grammar_max_select=1、0件可)。
- Std性表現是正は適用済み(std.md:11)。
