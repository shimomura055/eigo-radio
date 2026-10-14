# 委任_01 KP-GLOSS-ALIGNMENT-PRODUCTION-01(2026-10-14、要点保存。§0逐語)

新管理ID。FAMILY-XZ-M2P0-N01-PRODUCTION-COMPLETION-01 委任_04で配線したKP gloss再整合段(`er003_key_words_gloss_alignment.py`、OPEN-356)に対するOpus独立レビュー所見OF-225〜235の是正と有効性検証。ユーザー採否提示前の開発側作業。Production採用判断はユーザーのみ。

## 0. 前提(ユーザー指示2026-10-14の要旨・逐語保存対象)
「最終英語KPと日本語glossの意味的整合は、当然満たすべき基本品質要件である。」「既存の翻訳・正規化・検証機構を優先して利用する。自動的な整合を実現する方向で是正する。効果・副作用・Regression・量産コストを確認する。新仕様のProduction採用が本当に必要な場合だけ、検証結果を揃えてユーザー判断を求める。」「Q>D>C≫開発コスト。量産コスト上限70円/記事セット。恒久的な1〜2円の単価増も軽視しない。」「Human Reviewを常態化しない。」
Fable判断: Opus総評「根本原因は正しい、別段方式はSonnet案を支持、採用前に4点修正」を採用。修正は開発側で完了させ、その後Q1(再整合段の採否、課題指示文全文込み)/Q2(fallback方式)/Q3(承認前配線の扱い)をユーザーへ提示する。**承認済みPrompt(選定/canonicalization)・Rule7・Gate・A′は変更しない。**

## 1. 是正項目(Opus所見→Fable採否)
OF-227/228 fallbackを(ii)主体へ[採用] / OF-229 規則抽出の堅牢化[採用] / OF-230 決定論チェック[採用] / OF-233 費用記録[採用] / OF-232 費用再見積り(effort比較は結果報告のみ、切替なし)[採用] / OF-231 有効性検証[採用] / OF-234 追加確認(a)Family Z音声test(b)KP短縮頻度(c)meはOPEN記録のみ[採用] / OF-235 明示flag既定ON・PRODUCTION_WIRED未宣言・ユーザー判断までは新規量産runでこの段を通さない[採用] / OF-225/226 記録のみ(Q1〜Q3としてユーザーへ)。詳細対応=`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_01/FIX_01.md`。

## 2. 成果物・固定ブロック(要点)
コード=`er003_key_words_gloss_alignment.py`/test拡張/`er003_v1_n3_01_scaffold_generate.py`最小変更。証跡=`er071_output/m2p0_n01_production_wiring_01/gloss_alignment_01/`(FIX_01/VALIDATION_01/cost_01)。予算JPY10。E-1/D-1/G-1(明示add、telemetry/evidence_*/ログ/wav/words禁止、trailer `Managed-ID: KP-GLOSS-ALIGNMENT-PRODUCTION-01`)。STOP確認は`tools/stop_scope_check_01.py`。

## 3. 結果(Sonnet、2026-10-14)
実装・test・実API検証(JPY1.18)完了。詳細は`docs/pm/RESULT_PACKET_KGA.md`。
