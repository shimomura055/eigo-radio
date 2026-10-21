# -*- coding: utf-8 -*-
"""FAMILY-X-B3-CORE-NUMBER-ROUNDING-TRIAL-01 委任_03 事前登録ラベル(判断LLM実行前にcommit。LLMへは非開示)。
ラベル基準(人間基準、承認済みSpoken-first/Listener-Friendly条件の読み替えのみ。新基準ではない):
  A=APPROXIMATE_OK: 聞き取りで精度自体に意味が薄い大きな数量(標本数・台数等)で、通常の四捨五入が意味・比較方向・閾値を変えず、
                    同一Factの別数値と同一視されず、既に概数/限定語(超・以上)でもない
  E=EXACT_REQUIRED: 日付・時刻、小さな整数(数え上げ)、閾値/限定語付き(超・以上・最大)、価格・金利・率など精度が比較/意味を持つ値、
                    同一Factで近接/合算関係にある値、既に「約」/概数が付く値、条件値
  B=BOUNDARY: 人間でも割れる境界。正解率(合否)の分母から除外し、分布のみ報告(安全検証V1〜V7は通常通り適用)
キー=(article_id, 代表surface[sidecar先頭surface])。
"""
LABELS = {
    # art_a31992b5 paycheck_personality(Sol Trial 評価セットA)
    ("art_a31992b5", "11件"): "E", ("art_a31992b5", "最大134,515人"): "A", ("art_a31992b5", "3回以上"): "E", ("art_a31992b5", "0.0630"): "E",
    # art_1e4c771e coffee_prices fxpw(評価セットX1,X2)
    ("art_1e4c771e", "2025年2月"): "E", ("art_1e4c771e", "4.30"): "E", ("art_1e4c771e", "9.14"): "B",
    ("art_1e4c771e", "3%"): "E", ("art_1e4c771e", "41%"): "B",
    # art_701612d8 boredom_aggression(評価セットX3,X5)
    ("art_701612d8", "634"): "A", ("art_701612d8", "5分"): "E", ("art_701612d8", "10"): "E", ("art_701612d8", "最大50"): "E", ("art_701612d8", "1,332"): "A",
    # art_36b2c87d semiconductor_earnings(評価セットX4=境界)
    ("art_36b2c87d", "295億9,100万ドル"): "B", ("art_36b2c87d", "167億ドル"): "E", ("art_36b2c87d", "221％"): "B",
    ("art_36b2c87d", "54％"): "E", ("art_36b2c87d", "約348億ドル"): "E",
    # art_e94a50c1 coffee_prices v5_ms(既に約/範囲/小数%)
    ("art_e94a50c1", "262.18"): "B", ("art_e94a50c1", "8.7%"): "E", ("art_e94a50c1", "約9か月"): "E",
    ("art_e94a50c1", "約2～3か月分"): "E", ("art_e94a50c1", "6.1%"): "E", ("art_e94a50c1", "約15%"): "E",
    # art_9bd6834e hormuz(僅差・同Fact複数数値・閾値超・既に約)
    ("art_9bd6834e", "20％"): "E", ("art_9bd6834e", "7.29ドル"): "E", ("art_9bd6834e", "9.59％"): "E",
    ("art_9bd6834e", "83.30ドル"): "B", ("art_9bd6834e", "約2.6％"): "E", ("art_9bd6834e", "85ドル"): "E",
    # art_7a5593c4 central_bank_mortgage(金利・範囲・採決・目標値)
    ("art_7a5593c4", "0.25パーセントポイント"): "E", ("art_7a5593c4", "3.75～4.00％"): "E", ("art_7a5593c4", "12対0"): "E",
    ("art_7a5593c4", "2％"): "E", ("art_7a5593c4", "30年"): "E", ("art_7a5593c4", "5.98％"): "E",
    # art_11eb38bd streaming_price(僅差の価格比較: 0.50ドル増等。丸めると差が消える)
    ("art_11eb38bd", "11.99ドル"): "E", ("art_11eb38bd", "12.49ドル"): "E", ("art_11eb38bd", "18.99ドル"): "E",
    ("art_11eb38bd", "21.49ドル"): "E", ("art_11eb38bd", "189.99ドル"): "E", ("art_11eb38bd", "214.99ドル"): "E",
    # art_6322c220 sewer(既に約が付く/曖昧語)
    ("art_6322c220", "約50万"): "E", ("art_6322c220", "数50年"): "E", ("art_6322c220", "約4万"): "E",
    ("art_6322c220", "約7%"): "E", ("art_6322c220", "10年"): "E", ("art_6322c220", "約11万"): "E",
    # art_06ae3dca byd_recall(合算関係: 143k+40k=183k。部品は丸めると合算が崩れる)
    ("art_06ae3dca", "142,895台"): "B", ("art_06ae3dca", "40,316台"): "B", ("art_06ae3dca", "183,211台"): "A",
    # art_2463c2ea openai_copyright(件数・閾値超・日付)
    ("art_2463c2ea", "14"): "E", ("art_2463c2ea", "2億5,000万ドル"): "E", ("art_2463c2ea", "2026-10-08"): "E",
    # art_f172a253 space_weapons(日付・超)
    ("art_f172a253", "2026年9月14日"): "E", ("art_f172a253", "2021年11月15日"): "E", ("art_f172a253", "1,500個超"): "E",
    # art_0cc8ca3f small_bag(日付)
    ("art_0cc8ca3f", "2026年9月8日"): "E", ("art_0cc8ca3f", "2026年10月"): "E",
    # art_256c6721 ai_control(roughly/more than 付き=既に概数・限定語)
    ("art_256c6721", "1,200"): "E", ("art_256c6721", "70,000"): "E", ("art_256c6721", "700"): "E",
    # art_9d9f7170 ai_control(別Ledger: 評価run数=大きな数量、15=小さな数え上げ。同一テーマで適否が分かれる)
    ("art_9d9f7170", "141,006"): "A", ("art_9d9f7170", "15"): "E",
    # art_bd7114bc manga(小さな整数)
    ("art_bd7114bc", "2"): "E", ("art_bd7114bc", "4"): "E",
    # art_4f7d28b0 middle_east mey_01(死傷者。309人は同Factの「300人超」と別ソース。丸めると別主張になる)
    ("art_4f7d28b0", "12人"): "E", ("art_4f7d28b0", "309人"): "E", ("art_4f7d28b0", "300人超"): "E",
    # art_ae7611d0 middle_east mey_02
    ("art_ae7611d0", "1"): "E",
}

# Sol/Luna比較に使う旧評価セット(TRIAL_DESIGN_01 (f) の9件=記事A4件+coffee2+boredom3+semi1 のうち、
# 現行機械選定のsidecarに存在するもの。A=paycheck(run_pp_01)、coffee/boredom/semi=各記事。キーは旧(source,surface))
PRIOR9 = [("A", "134,515人"), ("A", "11件"), ("A", "3回以上"), ("A", "0.0630"),
          ("coffee", "4.30"), ("coffee", "2025年2月"), ("boredom", "1,332"), ("boredom", "5分"), ("boredom", "最大50"), ("semi", "295億9,100万ドル")]
