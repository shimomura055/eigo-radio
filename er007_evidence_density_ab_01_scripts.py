# ============================================================
# er007_evidence_density_ab_01_scripts.py
# ER-007-SPOKEN-EVIDENCE-DENSITY-AB-01 Part A: B版(Evidence Compression)
# spoken script。A版(現行完成候補)は一切変更しない。
# ============================================================
# 圧縮ルール(タスク仕様Part A-4)に基づき、Full Story Part1/Part2・
# Point One/Two本文のみを対象に、evidence attributionの密度を下げる。
# heading・in_one_line・Comment/Preview(Support層)は対象外(元々薄い)。
# Evidence Ledger自体・Fact自体・論点構成・Key Phraseは変更しない。

B_SCRIPTS = {
    "n4_supermarket": {
        "b1b": {
            "part1": (
                "A supermarket is not just a place where products wait for shoppers. "
                "It is also a carefully planned map.\n\n"
                "That map often changes. A trade publication says stores update "
                "layouts to make the shop feel fresh, guide customer movement, "
                "highlight seasonal offers, and encourage impulse buying.\n\n"
                "But a new layout can also support healthier shopping.\n\n"
                "Researchers tested this in a group of UK supermarkets. Some stores "
                "changed their layout, while similar stores did not, so the two "
                "groups could be compared.\n\n"
                "The changes were practical. The fruit and vegetable area became larger "
                "and moved closer to the entrance. Frozen vegetables were moved to a "
                "more visible aisle. Sweets were removed from displays near the "
                "checkouts and replaced with non-food items and water."
            ),
            "part2": (
                "The effect was clear for fruit and vegetables. Sales rose sharply — by "
                "roughly 6,000 extra portions per store each week at first, growing to "
                "nearly 10,000 a few months later.\n\n"
                "Snack sales moved the other way at first, dropping by more than a "
                "thousand portions a week. But that drop did not hold up as a clear, "
                "lasting trend.\n\n"
                "Total sales for the whole store showed no clear change. The new layout "
                "did not seem to make people buy more overall — it changed what they "
                "bought.\n\n"
                "A related survey found a similar pattern at home: shoppers using the "
                "changed stores reported buying more fruit and vegetables, with little "
                "clear effect on snacks."
            ),
            "point_one_body": (
                "Another study looked at how shoppers feel while they shop. It found "
                "links between store layout, atmosphere, shoppers' feelings, and "
                "impulse buying. This does not prove that one shelf move causes a "
                "purchase. It shows that the shopping environment can be part of the "
                "decision-making process."
            ),
            "point_two_body": (
                "Some shelf changes are more than a visual refresh. Researchers have "
                "proposed using purchase data itself to decide which products should "
                "share an aisle, aiming to maximize impulse buying. In tests, this "
                "approach performed more consistently than simple manual changes — "
                "though it was not tested directly in real stores."
            ),
        },
        "a2": {
            "part1": (
                "A supermarket shelf may look fixed. But stores often change their "
                "layout.\n\n"
                "They move products, make some areas larger, and change what shoppers "
                "see first. This is not only about making the store look new. The "
                "layout can guide people through the shop and affect what they "
                "notice.\n\n"
                "Researchers tested this in several discount supermarkets in England. "
                "Some stores changed their layout. Similar stores stayed the same, so "
                "the results could be compared.\n\n"
                "In the changed stores, the fresh fruit and vegetable area became "
                "larger and moved near the entrance. Frozen vegetables moved to a more "
                "visible aisle. Sweets near the checkouts and opposite the checkouts "
                "were removed. They were replaced with non-food products and water."
            ),
            "part2": (
                "The result was clear for fruit and vegetables. Sales rose sharply — "
                "about 6,000 more portions per store each week at first, growing to "
                "nearly 10,000 a few months later.\n\n"
                "Sweets moved the other way at first, falling by about 1,300 portions "
                "a week. But that drop did not hold up as a clear, lasting trend.\n\n"
                "Total store sales showed no clear change overall.\n\n"
                "A related survey found a similar pattern at home: shoppers using the "
                "changed stores reported buying more fruit and vegetables, with little "
                "clear effect on sweets."
            ),
            "point_one_body": (
                "Another study looked at how shoppers feel while they shop. It "
                "reported links between store layout, atmosphere, shoppers' feelings, "
                "and impulse buying. The message is simple: shopping decisions are not "
                "made only in the shopper's mind. The space around them is also part "
                "of the experience."
            ),
            "point_two_body": (
                "Researchers have also proposed using buying data itself to keep "
                "changing product and aisle positions, aiming to maximize impulse "
                "buying. In tests, this approach performed better than simple visual "
                "or manual shelf changes. A trade publication also lists fresh "
                "experiences, easier routes, and seasonal displays as reasons for "
                "regular changes."
            ),
        },
    },
    "n5_cafes": {
        "b1b": {
            "part1": (
                "A café is no longer only a place for coffee and conversation. For "
                "some people, it is also a place to work for hours with a laptop. "
                "These “customer-workers” buy something, take a seat, and use "
                "a public space for work-related tasks.\n\n"
                "For café owners, this creates a difficult choice. Should they welcome "
                "this customer group, or protect the space for shorter visits and "
                "social use? Two recent examples show that both answers are now being "
                "tested.\n\n"
                "A qualitative study looked closely at this question, observing and "
                "interviewing people across dozens of these “third places” in "
                "London.\n\n"
                "The study places these businesses into four groups. Archetypal places "
                "discourage work. Status Quo places do not clearly choose between "
                "workers and social customers, and this is where conflict is described "
                "as strongest. Compromise places try to serve both groups but may "
                "struggle to enforce their rules. Productive Third Places, or PTPs, "
                "clearly target customer-workers and adapt the space for them."
            ),
            "part2": (
                "The other response is restriction. According to a trade report, The "
                "Barn, a Berlin café, introduced a one-hour laptop limit — or a full "
                "ban on certain busy days. The café reported that laptop users had "
                "been occupying more than 70 percent of its seats for long "
                "periods, alongside a "
                "25 percent drop in sales before the change.\n\n"
                "The Barn's founder said the business wants to offer an excellent "
                "coffee experience, while still recognizing the real demand from "
                "remote workers who want to work in cafés.\n\n"
                "So the debate is not simply about laptops. It is about whether a café "
                "treats work as a problem, a compromise, or a planned part of its "
                "identity."
            ),
            "point_one_body": None,  # 変更なし(元々dense evidenceマーカーなし)
            "point_two_body": None,  # 変更なし
        },
        "a2": {
            "part1": (
                "A café is no longer only a place for coffee and conversation.\n\n"
                "For some people, it is also a place to work. They buy a drink, open "
                "a laptop, and stay for many hours. Researchers call these people "
                "**customer-workers**: customers who also work in the café.\n\n"
                "A study looked closely at this change, observing and interviewing "
                "people across dozens of these “third places” in London.\n\n"
                "The study found four kinds of third place.\n\n"
                "**Archetypal places** try to stop people from working. They may not "
                "offer Wi-Fi. They may play loud music or use less comfortable "
                "chairs.\n\n"
                "**Status Quo places** do not clearly choose between workers and "
                "social customers. Because of this, clashes between the two groups "
                "can be strong.\n\n"
                "**Compromise places** try to welcome both groups. But they can have "
                "trouble making their rules work every day.\n\n"
                "The fourth kind is the **Productive Third Place**, or PTP. These "
                "cafés clearly welcome customer-workers. They offer reliable Wi-Fi, "
                "enough power outlets, useful furniture, and controlled noise. They "
                "may also offer daily deals.\n\n"
                "The study says these customers can bring value. They may use seats "
                "during quiet hours. They may also make the café look active and "
                "lively."
            ),
            "part2": (
                "A trade report described a different choice by The Barn, a Berlin "
                "café. Laptop users had been occupying more than 70 percent of "
                "its seats for long periods, alongside a 25 percent drop in "
                "sales before the "
                "café acted.\n\n"
                "The Barn then introduced a one-hour limit for laptop users. On some "
                "busy days, it could ban laptop use completely.\n\n"
                "So, cafés are moving in two directions. Some are changing the whole "
                "space to welcome people who work. Others are protecting seat "
                "turnover with time limits."
            ),
            "point_one_body": None,
            "point_two_body": None,
        },
    },
    "n6_delivery": {
        "b1b": {
            "part1": (
                "A package is on its way, but its next step is unclear.\n\n"
                "So we open the tracking page. Then, a few minutes later, we check it "
                "again. Nothing may have changed. Still, the update button pulls us "
                "back.\n\n"
                "What looks like simple impatience may be part of a wider response to "
                "uncertain waiting.\n\n"
                "Researchers followed people through several real waits: voters "
                "waiting for the 2020 U.S. presidential election result, people "
                "waiting for their California bar exam results, and academic job "
                "seekers waiting for hiring decisions.\n\n"
                "The pattern was clear: as people became more worried, they searched "
                "more often for news and updates."
            ),
            "part2": None,  # 変更なし(既に良い話し言葉・十分にhedge済み)
            "point_one_body": None,  # 変更なし
            "point_two_body": (
                "In a lab experiment, people watched moving-dot displays and had to "
                "judge which way the dots were mostly moving, replaying them before "
                "deciding. When the displays were harder to read, people asked to "
                "replay them more often. The link between uncertainty and checking "
                "was strong. People's own sense of not being sure predicted the "
                "checking — a feeling of uncertainty they weren't consciously aware "
                "of did not."
            ),
        },
        "a2": {
            "part1": (
                "Why do we open a delivery page again and again?\n\n"
                "The answer may begin with the waiting, not the package.\n\n"
                "When the result is unknown, checking for new information can feel "
                "like taking a small action in a situation we cannot control.\n\n"
                "Researchers followed people through several real waits: people "
                "waiting for the 2020 U.S. presidential election result, people "
                "waiting for their California bar exam results, and academic job "
                "seekers waiting for hiring decisions.\n\n"
                "They found a clear pattern. As people's worry grew, they checked the "
                "news and searched for updates more often."
            ),
            "part2": None,
            "point_one_body": (
                "A lab study looked at this question directly. People watched moving "
                "dots and judged their direction. Before answering, they could "
                "replay the dots as many times as they wanted.\n\n"
                "When the movement was harder to understand, they checked more "
                "often. The link between uncertainty and checking was strong. This "
                "supports a link between uncertainty and checking, but it does not "
                "prove the same direct effect on delivery tracking."
            ),
            "point_two_body": None,
        },
    },
}
