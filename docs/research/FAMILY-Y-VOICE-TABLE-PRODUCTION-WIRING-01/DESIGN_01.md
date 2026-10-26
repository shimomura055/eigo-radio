# DESIGN_01 — 方針(b): 固定3 Voice + 承認済み候補プールをデータとして追加
- `Y_DIALOGUE_VOICE_POOL`(男性Puck/Schedar/Fenrir/Orus/Iapetus、女性Zephyr/Kore/Leda/Sulafat/Erinome)を structure_01 に**読み取り専用データ**として追加。選定アルゴリズムは新設しない(Voice 1〜3は固定割当のまま)。
- `FIXED_VOICE_SLOTS`: voice_1 Algieba→**Puck**。voice_2=Zephyr / voice_3=Schedar は不変(表内)。
- `verify_voice_assignment()`: 既存関数`assign_dialogue_voices(roster, pool=)`のpool引数にY表を渡す(Z表依存を解消)。新機構ではなく既存引数の利用。条件A非該当。
- Z表(`er062 FAMILY_Z_DIALOGUE_VOICE_POOL`)・メロスpin(Algieba)は不変。Y/Z差分はユーザー許容の承認済みFamily固有仕様(コメント・testメッセージに明記)。
- 既存完成音声は差し替えない: voice_guard(`ya.voice_guard_cached`)により旧Algieba cacheは再利用されず、既存run_01は触らない。今後の制作(新run)にのみ適用。
