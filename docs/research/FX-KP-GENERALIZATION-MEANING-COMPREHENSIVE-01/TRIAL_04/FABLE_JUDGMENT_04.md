# FABLE_JUDGMENT_04 (Fable判定 2026-10-23、委任_19 §1の逐語保存)

- 課題②(見出し語の人称placeholder、`possessor_roles`先行判定+決定論写像[revertのみ]): **VALIDATED(Fable)**。根拠: 意味関係の誤り 現行+A-1 7(rep1)/5(rep2)→本案 0/1(2rep計 14→1、公式score)、role判定76/80 gold一致、INVALID/REVIEW_REQUIRED増0、非所有格key同一率97.5%、rep間一致率96.0%(現行95.6%)、追加LLM call 0、費用+0.03円/記事、Adv/PROMPT_SHA256不変。開示: 一般化の後退4件(いずれも無変更its形、誤りではない)、rep2の誤り1件(`out of our hands`→someone's)、goldはFable基準で再採点(独立盲検ではない)、標本は所有格約40件×2rep。Opus条件C: 必須修正後に配線可(反映済み=WIRING_DESIGN_05)。Production採用はユーザー判断(UDR)。
- 課題①(Std字義訳): **部分改善・未解消**(Closeしない)。C(独立検査+flag項目のみ再生成): F層字義NG 6→1/122、FAIL計8→4(残3は継承の既知分)、flag項目内 改善5/不変14/PASS→FAIL悪化0、未flag項目はバイト同一。検出器recall 5/6・precision 5/19。残存: `question shaped like a trophy`型(rep1未修復、rep2は語義誤認へ)。Cp(同一call自己監査、1 rep・61出力)はFAIL 0だが検出器としてはrecall 0で、文字列が変わる=事実上の生成Prompt変更(非劣化の構造保証なし)。M(再整合指示除去)は改善なし。追加費用: C≈0.2〜0.25円/記事。
- 原因の確定: ②=正規化段に所有者の指示対象を判定する規則・工程が無い(規定欠落)+規則3例示の偏り。①=字義/慣用を検査する工程が全段に無い+確率的字義選択(生成Prompt側の誘因仮説Mは本Trialで不支持)。

