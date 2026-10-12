# FAMILY-Z-MELOS-SOL-PRODUCTION-AUDIO-E2E-01 委任_08 (2026-10-12) STOP報告(kp_a2 再試行も失敗)

到達stage: seed_check -> writer -> validate_b1b -> std_adjust -> validate_a2 -> plan -> support -> kp(a2でSTOP)。TTS以降・試聴ページ・Playwright・客観チェックは未実施。PRODUCTION_WIRED未達。

## 実施
1. Comment3 content_facts限定を実装(`er062_family_z_writer_01.limit_comment3_part`: Part3先頭約40%・最低2段落、Std/Adv両Comment3に適用、共有module無改変)。再生成時のみPreview/Comment1/2を再利用する`prior`引数と、`--regenerate-stage support_<lv>`で旧supportを`*_prev_before_c3_limit.json`へ退避する処理を追加。test 2件追加(er062 58件OK、er026統合/er063含め全146件中、新規テストの不備1件を修正後OK)。
2. `--regenerate-stage kp_a2` を1回だけ実行(許可どおり)。結果: 再び `CANONICALIZATION_INVALID`(backend内attempt1/2とも。selectionは5件STRUCTURE_PASS、rank1 'take my place'、canonicalizationが 'take someone's place' に一般化しRule7違反: source_span 'take my place' の連続部分文字列でなく、閉じた語彙集合の人称代名詞置換にも該当しない)。同一理由。→ ルールどおりSTOP。人為修正・rank1手当て・追加retryは行っていない。
3. support_a2(Std Comment3再生成)は、kpがSTOPのため未実施(kp以降の再開時に`--regenerate-stage support_a2`を実施する)。Adv Comment3(現行)は結末に触れない問いかけ(「What will make him try to reach the city again?」)で維持。
4. SSOT: DECISION_LOG(委任_04A〜08エントリ)、OPEN_ITEMS(OPEN-306〜310新規)、CURRENT_SPEC Family Z節(E2E実行状態、STOP中)を更新。OPEN-309が決定論話者判定改善案。

## 費用
累計約JPY34.1(e2e_stage_log) + kp_a2再試行(selection+canonicalization計約2call、<JPY1) = 約JPY35/300、警告200未到達。cost_log.jsonlにはJPY換算列が無くトークン数のみ(集計はe2e_stage_logのspent_jpy_cumulativeで代替)。

## 証跡
er026_output/family_z_production_e2e_01/melos/evidence_08/kp_a2_failed_before_regen/(再試行前)、kp_a2_regen_failed_after/(再試行後、canonicalization_runtime_metadata.jsonに各attempt理由)。

## 判断依頼(Fable/ユーザー)
a2 KP rank1の扱い。選択肢案: (a)selectionのPhrase制約に「所有格を含むphrase不可」等を追加(KP backendは共有moduleのため範囲外・Fable判断)、(b)別rank1候補をFableが指示して人間確定として扱う(人為修正禁止との整合を要判断)、(c)Rule7の閉じた語彙集合に所有格人称代名詞(my->someone's)を追加(共有module変更・要承認)。kp_a2の追加再試行は禁止枠のため行わない。
