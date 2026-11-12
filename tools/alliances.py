"""France's alliances, one bloc per kind of government, each with the countries it may ask to join.

Socialist France (commune, anarchists, Red Napoleon): the Second International, with the Spanish Republic.
Democratic France (the three parliaments, the guardian president): the Popular Front, with the Spanish Republic and
the United States (the Continental Army's republic). National France (Orleans, Bourbon, Petain): the Francophonie, with
Carlist Spain, the Kingdom of Spain, the Two Sicilies, the Papal States, the Ottoman Empire (won over by focus) and the
Balkan Pact if it won its war. The Emperor: the Deluge, with the Ottomans (by focus) and the victorious Balkan Pact.

Every invitation waits for its country's war to end: the Spanish civil war, the Balkan war, the American war of
independence. new_routes.define() calls define(); build_france.py writes TEXT.
"""
OFFER = "{tag} = {{ country_event = {{ id = lr_dipl.1 days = 3 }} }}"

BLOCS = {  # family: faction key, name, routes (prefix, route flag)
    "socialist": ("LR_second_international", "제2인터내셔널",
                  [("LR_COM_", "LR_route_communist"), ("LR_ANA_", "LR_route_anarchist"), ("LR_RED_", "LR_route_red")]),
    "democratic": ("LR_popular_front", "국민전선",
                   [("LR_JAC_", "LR_route_jacobin"), ("LR_GIR_", "LR_route_girondin"), ("LR_MAR_", "LR_route_marais"), ("LR_GUA_", "LR_route_guardian")]),
    "national": ("LR_francophonie", "프랑코포니",
                 [("LR_ORL_", "LR_route_orleans"), ("LR_BOU_", "LR_route_bourbon"), ("LR_PET_", "LR_route_petain")]),
    "empire": ("LR_deluge", "대홍수", [("LR_NAP_", "LR_route_empire")]),
}
# Routes whose old alliance focus becomes the founding focus of the bloc.
FOUNDERS = {"LR_BOU_": "LR_BOU_latin_league", "LR_ORL_": "LR_ORL_latin_front"}
# Routes whose bloc hangs from somewhere other than the head the integration focuses use.
HEADS = {"LR_JAC_": "LR_JAC_committee", "LR_GIR_": "LR_GIR_cabinet", "LR_MAR_": "LR_MAR_cabinet", "LR_GUA_": "LR_GUA_oath",
         "LR_COM_": "LR_COM_commune", "LR_ANA_": "LR_ANA_federation", "LR_PET_": "LR_PET_marshal", "LR_NAP_": "LR_NAP_coronation",
         "LR_RED_": "LR_RED_tribune"}


def free(tag):
    return f"{tag} = {{\n\texists = yes\n\tis_subject = no\n\tNOT = {{ is_in_faction_with = ROOT }}\n}}"


SPAIN_AT_PEACE = "custom_trigger_tooltip = {\n\ttooltip = LR_tt_spain_at_peace\n\tNOT = { has_global_flag = LR_spain_civil_war }\n}"
AMERICA_FREE = ("custom_trigger_tooltip = {\n\ttooltip = LR_tt_america_free\n\tCNA = {\n\t\texists = yes\n\t\thas_war = no\n\t}\n"
                "\tUSA = { exists = no }\n\tNOT = { has_global_flag = LR_cna_canada }\n}")
BALKANS_WON = "custom_trigger_tooltip = {\n\ttooltip = LR_tt_balkan_pact_won\n\thas_global_flag = LR_balkan_pact_won\n}"
BALKAN_PACT = ("YUG", "GRE", "ROM")

# key: (icon, name, desc, availability, bypass, effects)
INVITES = {
    "ESR": ("improve_relations", "스페인 공화국 초대", "피레네 너머의 공화국에 손을 내밉니다. 내전에서 살아남은 그들이라면 무엇과 싸우는지 압니다.",
            SPAIN_AT_PEACE + "\n" + free("ESR"), "NOT = { has_global_flag = LR_spain_civil_war }\nESR = { exists = no }", [OFFER.format(tag="ESR")]),
    "SPR": ("improve_relations", "스페인 왕국 초대", "마드리드의 왕에게 동맹을 청합니다. 피레네의 양쪽이 같은 깃발 아래 섭니다.",
            SPAIN_AT_PEACE + "\n" + free("SPR"), "NOT = { has_global_flag = LR_spain_civil_war }\nSPR = { exists = no }", [OFFER.format(tag="SPR")]),
    "CRL": ("improve_relations", "카를로스파 스페인 초대", "신과 조국과 왕을 외치며 내전을 이긴 카를로스파에게 동맹을 청합니다.",
            SPAIN_AT_PEACE + "\n" + free("CRL"), "NOT = { has_global_flag = LR_spain_civil_war }\nCRL = { exists = no }", [OFFER.format(tag="CRL")]),
    "CNA": ("improve_relations", "미합중국 초대", "영국의 왕관을 벗어던진 대서양 건너의 공화국에 동맹을 제안합니다. 1778년에 맺지 못한 조약입니다.",
            AMERICA_FREE + "\nCNA = { NOT = { is_in_faction_with = ROOT } }", None, [OFFER.format(tag="CNA")]),
    "TTS": ("improve_relations", "양시칠리아 초대", "나폴리의 왕에게 동맹을 청합니다. 지중해의 남쪽 문이 열립니다.",
            free("TTS") + "\nTTS = { has_war = no }", "TTS = { exists = no }", [OFFER.format(tag="TTS")]),
    "PAP": ("improve_relations", "교황령 초대", "로마에 사절을 보냅니다. 성하의 축복이 있는 동맹은 유럽의 모든 성당에서 들립니다.",
            free("PAP") + "\nPAP = { has_war = no }", "PAP = { exists = no }", [OFFER.format(tag="PAP")]),
}
BALKAN_INVITE = ("major_alliance", "발칸 동맹 초대", "불가리아를 꺾은 발칸 동맹의 세 나라에 동맹을 청합니다. 대전쟁 때 프랑스와 함께 싸운 옛 전우들입니다.",
                 BALKANS_WON + "\nOR = {\n" + "\n".join("\t" + free(t).replace("\n", "\n\t") for t in BALKAN_PACT) + "\n}",
                 "has_global_flag = LR_bulgaria_hegemon",
                 ["if = {\n\tlimit = { " + free(t).replace("\n", " ") + " }\n\t" + OFFER.format(tag=t) + "\n}" for t in BALKAN_PACT])
OTTOMAN_CONTACT = ("positive_trade_relations", "이스탄불의 대사관", "오스만 정부에 무역 협정과 차관을 제안합니다. 승전국의 질서 안에서 오스만은 늘 런던과 빈의 셋째 자리였습니다.",
                   "TUR = {\n\texists = yes\n\tNOT = { has_war_with = ROOT }\n}", "TUR = { exists = no }",
                   ["TUR = { add_opinion_modifier = { target = ROOT modifier = large_increase } }", "add_political_power = -25"])
OTTOMAN_WIN = ("major_alliance", "오스만 포섭", "술탄에게 승전국의 동맹을 버리고 프랑스 곁에 서라고 청합니다. 오스만은 영국 진영을 떠나고, 프랑스는 그 대가로 오스만의 국경을 보장합니다.",
               "TUR = {\n\texists = yes\n\tis_subject = no\n\tNOT = { has_war_with = ROOT }\n\tNOT = { is_in_faction_with = ROOT }\n}", "TUR = { exists = no }",
               ["TUR = {\n\tif = {\n\t\tlimit = { is_in_faction = yes }\n\t\tleave_faction = yes\n\t}\n}", OFFER.format(tag="TUR")])

MEMBERS = {
    "socialist": ["ESR"],
    "democratic": ["ESR", "CNA"],
    "national": ["CRL", "SPR", "TTS", "PAP", "ottoman", "balkans"],
    "empire": ["ottoman", "balkans"],
}

TEXT = {
    "LR_second_international": "제2인터내셔널",
    "LR_popular_front": "국민전선",
    "LR_francophonie": "프랑코포니",
    "LR_deluge": "대홍수",
    "LR_tt_america_free": "§Y미국 독립전쟁§!에서 대륙군이 이겨 미합중국이 서고, 전쟁이 끝나야 합니다.",
    "LR_tt_balkan_pact_won": "§Y발칸 전쟁§!에서 발칸 동맹이 이겨야 합니다.",
}


MADE = []  # every focus define() adds; build_france.py files them under diplomacy


def define(g):
    focus, focuses = g["focus"], g["FOCUSES"]
    made = MADE
    for family, (faction, name, routes) in BLOCS.items():
        for prefix, route in routes:
            found = FOUNDERS.get(prefix)
            if found is None:
                found = prefix + "found_bloc"
                focus(found, "major_alliance", 0, 0, f"{name} 창설", f"프랑스가 이끄는 동맹 {name}을 세웁니다. 뜻을 같이하는 나라들이 차례로 초대받을 것입니다.",
                      f"if = {{\n\tlimit = {{ is_in_faction = no }}\n\tcreate_faction = {faction}\n}}", pre=[HEADS[prefix]], route=route)
                made.append(found)
            for member in MEMBERS[family]:
                if member == "ottoman":
                    rows = [("ottoman_contact", OTTOMAN_CONTACT, found), ("ottoman_win", OTTOMAN_WIN, prefix + "ottoman_contact")]
                elif member == "balkans":
                    rows = [("invite_balkans", BALKAN_INVITE, found)]
                else:
                    rows = [(f"invite_{member.lower()}", INVITES[member], found)]
                for key, (icon, fname, desc, available, bypass, effects), parent in rows:
                    fid = prefix + key
                    focus(fid, icon, 0, 0, fname, desc, *effects, pre=[parent], route=route, available=available)
                    if bypass:
                        focuses[-1]["bypass"] = bypass
                    made.append(fid)
    return made
