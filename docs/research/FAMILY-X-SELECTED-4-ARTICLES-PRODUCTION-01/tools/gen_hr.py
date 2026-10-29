import json,os
R='docs/research/FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01'
BASE='https://shimomura055.github.io/eigo-radio/user_test/selection_form_v3/'
arts=[("②","untidiness_family_resource","部屋は少し散らかっている方が、家族はうまくいく？"),
("④","ai_chat_sponsored_persuasion","AIに勧められた商品、気づかないうちに選ばされている？"),
("⑨","meta_waddle_world","AIペットは、たまごっちの次のブームになる？"),
("⑭","jwst_mystery_emission_line","地球の外にある天体、光だけでどこまで探せる？")]
L=[]
L.append("# HR_REQUEST_01(FAMILY-X-SELECTED-4-ARTICLES-PRODUCTION-01 委任_01、2026-10-29)\n")
L.append("""## 区分(PM_GOVERNANCE 30-3)
**既存の承認済みProductionルートを正常に通過した結果のHR**(不具合・未実行工程によるHRではない)。4記事とも、正式Production入口の本文生成(Research→Ledger→B3→W-1 Writer→Advanced→Standard)とscaffold stage(Part 2文法候補・KP候補・ニュアンス候補)を通過し、`--stage scaffold`が仕様どおりKP Human Review待機(rc=4、失敗ではない)で停止した。TTS以降は未実施。

## 30-2 必須7項目(共通)
1. 対象: 4記事(下表)のStandard(a2)/Advanced(b1b)。判断対象=学習項目の選定(KP・単語・文法・ニュアンス解説)。音声はまだ無い(TTS前)ので聴取判断はない。
2. 適用ルート: `er019_family_x_entertainment_production_runner_01.py`(本文)→`er019_family_x_audio_production_runner_01.py --stage scaffold`(`kp_backend=fulltext_p2`のKP review、Part 2文法`run_part2_candidates_x`、ニュアンス`run_nuance_candidates_x`)。CURRENT_SPEC「学習項目選定フォームv3」節・「ニュアンス解説」節。
3. 通過工程と判定: 各記事のRUNTIME_EVIDENCE_01.md参照(時刻・model・費用)。
4. 救済処理: 本文段のRisk Flaggerは非Blocking(4条件逐次、全件実行)。B3 M1(中核数値)再実行=④のみ1回発動(既存機構、storyline_b3_attempt1へ退避)。KP段のGate除外→補完(backfill)・gloss再整合・canonicalization再判定は②(Std/Adv)等で既存機構が自動発動(依頼書「Gateで除外された候補」欄)。LR/ASR/TTS retryは本段に存在しない(TTS前)。
5. HRに至った直接原因: 仕様上、KP・文法・ニュアンスの選定はHuman判断が必須(自動確定は明示の不在宣言のみ)。
6. 残る自動救済: なし(選定はHumanの仕事)。
7. 判断依頼: 下記の各フォームで、Standard/Advancedそれぞれ ①KP(最大3)・単語(最大5、KP含む)・文法(最大1)・ニュアンス解説(採用/不採用)を選び『選定結果をコピー』またはChatGPT送信で返信。AI推奨のまま良ければ『AI推奨でOK』と書くだけでも可(推奨は各表の`AI推奨`列)。
""")
L.append("## フォームURL(同一フォーム、記事直リンク)\n")
L.append("| # | 記事 | Standard | Advanced |\n|---|---|---|---|")
for n,s,t in arts:
    L.append(f"| {n} | {t} | {BASE}?a={s}__a2 | {BASE}?a={s}__b1b |")
L.append("")
for n,s,t in arts:
    ja=open(f'er019_output/{s}/run_fx4_01/ja_writer/revision2.md',encoding='utf-8').read().split('\n')[0]
    en=open(f'er019_output/{s}/run_fx4_01/b1b/article.md',encoding='utf-8').read().split('\n')[0].lstrip('# ')
    L.append(f"\n---\n## {n} {t}\n- 本文タイトル(JA): {ja} / (EN): {en}\n- 原記事/一次情報: `SOURCE_IDENTIFICATION_01.md`")
    for lv,lab in (('a2','Standard'),('b1b','Advanced')):
        d=json.load(open(f'user_test/selection_form_v3/data/{s}__{lv}__prod.json',encoding='utf-8'))
        L.append(f"\n### {n} {lab}\n- フォーム: {BASE}?a={s}__{lv}")
        L.append("- KP(フレーズ)候補: "+" / ".join(f"{p['term']}({p['meaning_ja']}){'★' if p.get('ai_rank',99)<=3 else ''}" for p in d['phrases']))
        L.append("- 単語候補: "+" / ".join(f"{p['term']}({p['meaning_ja']})" for p in d['words']))
        if d['grammar']:
            for g in d['grammar']:
                L.append(f"- 文法候補[{g.get('rank','')}]: {g['title']} — 例: {g['example']}")
        else:
            L.append("- 文法候補: 0件(Part 2抽出が該当構文なしと判定=`no_feature_paras`全段落。既存仕様の『候補0件』経路。フォーム上は文法欄が出ません)")
        nu=d.get('nuance')
        if nu:
            L.append(f"- ニュアンス解説(全文): **{nu['expression']}** — {nu['focus']}\n  - 本文の英文: {nu['quote_en']}\n  - 日本語訳: {nu['quote_ja']}\n  - 解説: {nu['explanation_ja']}\n  - 重複判定: {nu['overlap_summary_ja']}")
        else:
            L.append("- ニュアンス解説: 候補なし(モデルが『該当なし』を返却=NO_CANDIDATE。既存仕様どおり提示0件・待機なし)")
L.append("\n(★=AI推奨KP。文法の解説全文・AI選定理由はフォームに表示)\n")
open(f'{R}/HR_REQUEST_01.md','w',encoding='utf-8').write('\n'.join(L))
print(len('\n'.join(L)))
