# OPUS_REVIEW_01: Opus独立技術レビュー(条件A、2026-10-28、INTEGRATION_01対象)+Fable照合

Opus(opus-consultant、読み取り専用)の最終応答をFableが転記。Fable照合=§Fable。

## (a) 必要/不要
必要。(1)M3/Y/Z Gateが正常LR/Fallbackと異常を同じ違反コードで止める(`er019_family_x_style_profile_01.py:713-743`、`er063:2139-2140`) (2)LR後英文がページ描画に未反映(`er063:2459,2502`) (3)採用takeを一意に示す記録がない。overlay方式は最も単純で安全(`_generate_or_reuse`は`canonical_text`一致時のみ再利用 `er019 runner:1180`)。ただし判断が複数箇所に分かれ偽STOP/見逃し経路が残るため、(b)の差分を条件に推奨。

## (b) 推奨構造(Fable案との差分)
1. 採用take判定関数を1つに: `er129.resolve_adopted_take()`。優先順位=①人間承認の採用記録(`er121_e1_hr_adopt_r0_01.py:132-147`) ②再利用(Store key) ③`final_adoption`(BlockProgress `verified`(depth,ordinal)と突合) ④旧記録からの導出 ⑤UNKNOWN(Gate停止/報告「記録なし」)。ledger・classify・報告生成器・Z `style_actual`(B6)が全てこれを呼ぶ。
2. `final_adoption`は最小限 `{depth, ordinal, slot, style_mode(Step.style_mode er127:467), sent_style_sha, attempt_audio_sha, source}`。`human_approval_superseded`・`lr_applied`・LR本文は持たせない(重複・陳腐化)。
3. ledgerは消費者ごとにメモリ上で毎回導出(純関数)。ファイルは監査用出力に限定し、保存済みファイルをGate入力にしない。
4. 確定内容重なりT1は`er128.lr_overlap`を純関数として再計算。`confirmed_kp_lr_overlap.json`はGate入力にしない(M-3)。
5. 三者一致検査はassemble入口Gate 1か所のみ。M3内側に置かない(M3は`PROFILE_DEFAULT`で無条件PASS・上書き対象roleのみ `er019:695-696,662`)。
6. 位置特定は変更箇所前後k語のanchor方式。insert/delete対応(M-1,M-2)。
7. resumeでもLR選定根拠を保存(M-4)。
8. 配線は1つの統合commit(R-6)。

## (c) リスク
- M-1(高) TTS正規化差で偽STOP: LR before文はTTS正規化後(`er127:692`、数字語化・人名発音置換・PNAP `er003_v1_n3_01_tts_generate.py:1090-1091`、`er063:987-995`)、Z表示文は正規化前`spec.text`(`er063:1246`)。chunk全体トークン列探索は数字/人名1つでUNLOCATABLE。対策=anchor方式、ZのV2照合は`audio_text_after`。
- M-2(高) insert/deleteをSTOPにすると正常LRが止まる(LR 7 Gateは語の削除・挿入を許す)。対策=隣接一致語を取り込みreplaceへ正規化。句読点差は単語単位一致で判定(W2の「句読点差STOP」と統一)。
- M-3(高) `confirmed_kp_lr_overlap.json`は追記専用(`er128:1276-1279`)・`_ACTIVE_KP_DIRS`依存(`:1267`)・resume経路未呼出(`er020:829`のみ、`er127:666-673`は呼ばない)。Gate入力にすると偽STOPと見逃し両方。
- M-4(高) resume時LR記録は`rewritten_segment`のみ(`er127:671`)、7 Gate結果の監査コピーは再TTS後にしか書かれない(`er020:825-832`)→`LR_RECORD_INCOMPLETE`でBLOCK・変更理由欠落。対策=`save_lr_text`時点でBlockProgressへ候補・7 Gate結果・理由・範囲を保存、またはer020で再TTS前に成果物書込み(er020/er127追記のみ。INTEGRATION §3「無編集」の例外はFable判断)。
- M-5(中) finish 1点書込みの陳腐化/欠落: (i)HR採用でwav/entry置換(`er121_e1_hr_adopt_r0_01.py:124-147`) (ii)KP_EN key B hitはTTS未実行でStore採用(`er019_family_x_kp_en_k2_store_01.py:87-99`)→「Store再利用(ENGLISH_LOCK)」表現が必要 (iii)`_generate_or_reuse`はentry丸コピー(`runner:1185`)、旧cacheに`final_adoption`なし (iv)Z `build_entry`はキー列挙(`er063:1243-1282`)、コピー追加が必要 (v)wav shaはfinish後の加工(減速・連結)で変わるためGate条件に使うと偽BLOCK。対策=(b)-1の優先順位、`final_adoption`とBlockProgress `verified`の食い違い時のみ「記録不一致」停止。
- M-6(中) T2「変更文」=変更箇所を含む1文と定義(segment全体だと常時STOP)。T3は正規化後では数字が語化され見逃す→表示側で判定。
- M-7(中) 混入経路の漏れ: X公開ページ(audience=public)の事後試聴リストが`LR_REWRITTEN`ラベル・期待文・ASR文を表示(`er019_family_x_listening_page_01.py:159-166`)。Z `page_verify`は`Voice:`/`TTS方式`表示を必須検査(`er063_family_z_page_verify_01.py:68,70`)→F-9の撤去はLR/Fallback由来注記(`er063:2464-2468`)のみに限定。混入検知語に`LR_REWRITTEN`・`LR_APPLIED`・`FALLBACK_APPLIED`・Fallback Style名を追加。
- M-8(中) 部分配線: B6単独先行→告げ口心臓Adv KP2(ENGLISH_LOCK)が`Z_STYLE_ACTUAL_MISMATCH`+`FALLBACK_ADOPTED`でBLOCK(`er063:2134-2140`)。Z注記撤去単独先行→不一致表示が消える。
- M-9(中) 厳格化でBLOCK増→HR増の可能性(採用take基準化・parity全LR role/既定profile・旧記録UNKNOWN)。旧Gate/新Gateの差分監査(保存run全件、API 0)を配線前受入条件に。
- M-10(低) 告げ口心臓の`style_actual_vs_approved all_match=True`は誤同定の上に成立。B4/B6後にENGLISH_LOCKと判定され承認済みFallback警告で通るのが期待挙動。

## (d) 代替案
- `final_adoption`新設の代わりにBlockProgress+`Step.style_mode`から決定的導出(finish無編集)。ただし旧runは`blocks["1"]`欠落、Z ctx・Store再利用は対象外→推奨は「最小限`final_adoption`+BlockProgress突合」。
- 既公開2件: Word Gacha局所パッチはbuilder再生成不能な手作業drift。builder再描画の差分が2か所以上なら原因特定を先に。手修正でも`check_page`+ハイライト検査+ledger保存。

## (e) R-1〜R-7
R-1 初回/retry・fallbackは保証。resume(M-4)、Z(M-1 V2照合元)、HR原文復帰(優先順位明文化 M-5)、KP再利用(M-5 ii/iii)に抜け。Z chunk境界またぎLRは構造上起きない(clip単位)。X chunkは親partへの写像検証(W2 §4-2-3)要。
R-2 finish 1点では一意にならない(M-5)。Z ctxは`er122`側書込み+`build_entry`コピー。減速後再検証はattempt内。ENGLISH_LOCK段は1 with_block内(`k2_store:56`)で一意、key B hit表現要。
R-3 allowlistをleaf定数importで導出+drift test妥当。弱める懸念はユーザー決定済み2点のみ。厳格化で止まる件数増はM-9で確認。UNKNOWN/記録不完全BLOCK・例外時BLOCK適切。旧記録はF-6方針可、「完全」の定義は解決関数に一本化。
R-4 偽STOP=M-1,M-2,M-6 T2。見逃し=M-6 T3,M-3。
R-5 M-7の2点が漏れ。他層(AST import・出力先分離・run dir不変)は堅い。
R-6 「同一commit群」では不足(変更毎push運用)。B2 ledger・B4判定核は未配線純module+testとして並列commit可。配線(assemble parity Gate・M3/Y/Z呼出切替・ページoverlay・Z注記撤去・B6)は1統合commit。告げ口心臓runの位置確認のうえ投入。
R-7 範囲は必要十分。AI島は特別扱いコードなしで通常経路、ledgerがLR記録から`AI agents`/`AI systems`を自動導出することを確認。メロス`_02` LR 0で対象外は妥当、最終報告に原文§8との差を明記。

## (f) Phase B分割
B1(final_adoption)とB2(ledger)は並列可。B0「ledger schemaと採用take解決関数の契約」を先に置けばB2/B4/B5/B6を並列化。追加作業=(1)旧/新Gate差分監査(保存X/Y/Z run全件、API 0、配線前受入条件) (2)resume時LR根拠保存(M-4)。B6は判定核と同じ配線commit(M-8)。B7 AI島は配線後。Word Gacha/猿の手はB3後に候補ページ並列。B8配線後、B9最後。

## (g) 12観点
1必要 2採用take判定3通り・parity2か所を各1つに 3BlockProgress/`resolve_expected_text_after_local_rewrite`/`er128.lr_overlap`再利用妥当、記録ファイル不使用 4resumeでLR根拠喪失(M-4)・正規化対応喪失(M-1) 5LLM追加なし 6決定的 7差分監査まで要注意 8原稿書換え・再TTSなし 9API 0・evidence¥10〜40 10 HR採用/Store再利用/resume優先規則明文化で適合 11例外時BLOCK適切・部分配線でM-8→統合commit必須 12判定一本化で再発防止。
注: Y gate(`er121:874-1000`)・`er122`本体は未直読(W3/W1依拠)。Phase Bで直接照合。

## Fable照合(2026-10-28)
- (b)1〜8すべて採用。M-1〜M-10を`docs/pm/OPUS_FINDINGS_LEDGER.md`へOF-LRW-M01〜M10として登録(委任_07で転記)。
- M-4の対策=er020/er127への**記録追記のみ**(policy・回数・待機・判定不変)としてINTEGRATION §3の例外を承認(Fable判断、11-8範囲内)。
- M-7: F-9撤去対象をLR/Fallback由来注記に限定。X公開ページの事後試聴リストのLR行(ラベル・期待文・ASR文)は**public audienceでは非表示**にし最終Human報告へ移す(原文§2)。HR audienceは従来どおり。
- M-9: 旧/新Gate差分監査を配線前受入条件に追加(B4に含める)。
- R-6: 配線は1統合commit(B-wire)。B1/B2/B4/B5は未配線module+testとして先行commit可(既定動作不変)。
- 11-3 STOP条件該当なし→Phase Bへ進む(Opusレビューはユーザー承認Gateではない)。
