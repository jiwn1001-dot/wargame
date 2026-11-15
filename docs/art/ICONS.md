# 중점 아이콘과 국민정신 그림

`tools/custom_icons.py`가 만드는 문서입니다. 손으로 고치지 마세요.

## 넣는 법

그림을 아래 폴더에 이름만 맞춰 넣고 `python tools/build_all.py`(또는 `python tools/custom_icons.py`)를 돌립니다.
크기는 상관없습니다. 여백은 잘라 내고 아이콘 크기에 맞춰 DDS로 바꿉니다. 배경이 투명한 PNG가 가장 깔끔합니다.

| 넣을 곳 | 바뀌는 것 |
|---|---|
| `goals/중점ID.png` (예: `goals/LR_NAP_eagles.png`) | 그 중점 하나 |
| `goals/루트/바닐라아이콘.png` (예: `goals/NAP/goal_generic_major_war.png`) | 그 루트에서 그 아이콘을 쓰는 중점 전부 |
| `goals/all/바닐라아이콘.png` (예: `goals/all/goal_generic_major_war.png`) | 프랑스 중점 가운데 그 아이콘을 쓰는 것 전부 |
| `ideas/정신ID.png` (예: `ideas/LR_dyn_ruler_emperor.png`) | 그 국민정신 하나 |

위에 있는 것이 우선합니다. 그림을 지우고 다시 빌드하면 원래 아이콘으로 돌아갑니다.
루트 폴더 이름: `FRA` 공통, `ORL` 오를레앙, `BOU` 부르봉 왕정, `PET` 페탱, `NAP` 나폴레옹, `GUA` 공화국의 수호자, `RED` 붉은 나폴레옹, `JAC` 산악파, `GIR` 지롱드, `MAR` 푀양파, `COM` 코뮌, `ANA` 자유 코뮌 연합, `DEF` 패전.

지금 763개 가운데 743개가 바뀌어 있습니다. 하나하나의 목록은 `icon_worklist.csv`(엑셀로 열림)에 있습니다.

## 가장 효과가 큰 그림 (공통 주제)

한 장으로 많은 중점이 바뀝니다. 위에서부터 그리면 됩니다.

| 중점 수 | 주제 | 넣을 파일 |
|---|---|---|
| 94 | 전쟁·진격 | `goals/all/goal_generic_major_war.png` |
| 77 | 국민 통합 | `goals/all/goal_generic_national_unity.png` |
| 55 | 정치 압박·탄압 | `goals/all/goal_generic_political_pressure.png` |
| 50 | 선전·연설 | `goals/all/goal_generic_propaganda.png` |
| 49 | 외교·우호 | `goals/all/goal_generic_improve_relations.png` |
| 35 | 동맹 | `goals/all/goal_generic_major_alliance.png` |
| 24 | 영토 요구·편입 | `goals/all/goal_generic_demand_territory.png` |
| 22 | 민간 건설 | `goals/all/goal_generic_construct_civilian.png` |
| 22 | 육군 교리 | `goals/all/goal_generic_army_doctrines.png` |
| 18 | 보병·민병대 | `goals/all/goal_generic_allies_build_infantry.png` |
| 18 | 점령·출병 | `goals/all/goal_generic_occupy_start_war.png` |
| 18 | 군사 영향권 | `goals/all/goal_generic_military_sphere.png` |
| 16 | 해군 교리 | `goals/all/goal_generic_navy_doctrines_tactics.png` |
| 16 | 무역 협정 | `goals/all/goal_generic_positive_trade_relations.png` |
| 15 | 교역·금융 | `goals/all/goal_generic_trade.png` |
| 13 | 특수 부대·근위대 | `goals/all/goal_generic_special_forces.png` |
| 12 | 학문·연구 | `goals/all/goal_generic_scientific_exchange.png` |
| 11 | 민간 공장 | `goals/all/goal_generic_construct_civ_factory.png` |
| 10 | 요새·방어 | `goals/all/goal_generic_fortify_city.png` |
| 10 | 군수 공장 | `goals/all/goal_generic_construct_mil_factory.png` |
| 10 | 강압 조약 | `goals/all/goal_generic_forceful_treaty.png` |
| 8 | 협약 | `goals/all/goal_generic_alliance.png` |
| 7 | 생산 | `goals/all/goal_generic_production.png` |
| 6 | 군사 협정 | `goals/all/goal_generic_military_deal.png` |
| 6 | 위험한 거래 | `goals/all/goal_generic_dangerous_deal.png` |
| 6 | 정보·첩보 | `goals/all/goal_generic_intelligence_exchange.png` |
| 4 | 조선소 | `goals/all/goal_generic_construct_naval_dockyard.png` |
| 4 | 포병 | `goals/all/goal_generic_army_artillery.png` |
| 3 | 소총 | `goals/all/goal_generic_small_arms.png` |
| 3 | 차량화 | `goals/all/goal_generic_army_motorized.png` |
| 3 | 폭격기 | `goals/all/goal_generic_air_bomber.png` |

## 루트별 주제

루트마다 분위기를 다르게 하고 싶을 때 씁니다. 3개 이상 쓰는 것만 적었습니다.

### 공통 (`FRA`)

- 육군 교리 4개: `goals/FRA/goal_generic_army_doctrines.png`
- 보병·민병대 3개: `goals/FRA/goal_generic_allies_build_infantry.png`
- 학문·연구 3개: `goals/FRA/goal_generic_scientific_exchange.png`
- 폭격기 3개: `goals/FRA/goal_generic_air_bomber.png`

### 오를레앙 (`ORL`)

- 전쟁·진격 10개: `goals/ORL/goal_generic_major_war.png`
- 외교·우호 6개: `goals/ORL/goal_generic_improve_relations.png`
- 국민 통합 4개: `goals/ORL/goal_generic_national_unity.png`
- 선전·연설 4개: `goals/ORL/goal_generic_propaganda.png`
- 육군 교리 4개: `goals/ORL/goal_generic_army_doctrines.png`
- 군수 공장 3개: `goals/ORL/goal_generic_construct_mil_factory.png`
- 정치 압박·탄압 3개: `goals/ORL/goal_generic_political_pressure.png`
- 군사 영향권 3개: `goals/ORL/goal_generic_military_sphere.png`

### 부르봉 왕정 (`BOU`)

- 국민 통합 9개: `goals/BOU/goal_generic_national_unity.png`
- 동맹 9개: `goals/BOU/goal_generic_major_alliance.png`
- 전쟁·진격 8개: `goals/BOU/goal_generic_major_war.png`
- 외교·우호 8개: `goals/BOU/goal_generic_improve_relations.png`
- 정치 압박·탄압 6개: `goals/BOU/goal_generic_political_pressure.png`
- 영토 요구·편입 3개: `goals/BOU/goal_generic_demand_territory.png`
- 군사 영향권 3개: `goals/BOU/goal_generic_military_sphere.png`

### 페탱 (`PET`)

- 전쟁·진격 8개: `goals/PET/goal_generic_major_war.png`
- 외교·우호 7개: `goals/PET/goal_generic_improve_relations.png`
- 국민 통합 5개: `goals/PET/goal_generic_national_unity.png`
- 정치 압박·탄압 4개: `goals/PET/goal_generic_political_pressure.png`
- 선전·연설 3개: `goals/PET/goal_generic_propaganda.png`
- 동맹 3개: `goals/PET/goal_generic_major_alliance.png`

### 나폴레옹 (`NAP`)

- 전쟁·진격 9개: `goals/NAP/goal_generic_major_war.png`
- 국민 통합 7개: `goals/NAP/goal_generic_national_unity.png`
- 동맹 7개: `goals/NAP/goal_generic_major_alliance.png`
- 정치 압박·탄압 6개: `goals/NAP/goal_generic_political_pressure.png`
- 군사 영향권 6개: `goals/NAP/goal_generic_military_sphere.png`
- 선전·연설 4개: `goals/NAP/goal_generic_propaganda.png`
- 강압 조약 3개: `goals/NAP/goal_generic_forceful_treaty.png`
- 영토 요구·편입 3개: `goals/NAP/goal_generic_demand_territory.png`

### 공화국의 수호자 (`GUA`)

- 국민 통합 9개: `goals/GUA/goal_generic_national_unity.png`
- 전쟁·진격 8개: `goals/GUA/goal_generic_major_war.png`
- 외교·우호 5개: `goals/GUA/goal_generic_improve_relations.png`
- 정치 압박·탄압 4개: `goals/GUA/goal_generic_political_pressure.png`
- 선전·연설 3개: `goals/GUA/goal_generic_propaganda.png`

### 붉은 나폴레옹 (`RED`)

- 전쟁·진격 9개: `goals/RED/goal_generic_major_war.png`
- 선전·연설 5개: `goals/RED/goal_generic_propaganda.png`
- 국민 통합 5개: `goals/RED/goal_generic_national_unity.png`
- 정치 압박·탄압 3개: `goals/RED/goal_generic_political_pressure.png`

### 산악파 (`JAC`)

- 정치 압박·탄압 8개: `goals/JAC/goal_generic_political_pressure.png`
- 전쟁·진격 8개: `goals/JAC/goal_generic_major_war.png`
- 국민 통합 7개: `goals/JAC/goal_generic_national_unity.png`
- 선전·연설 7개: `goals/JAC/goal_generic_propaganda.png`
- 외교·우호 5개: `goals/JAC/goal_generic_improve_relations.png`

### 지롱드 (`GIR`)

- 전쟁·진격 8개: `goals/GIR/goal_generic_major_war.png`
- 교역·금융 7개: `goals/GIR/goal_generic_trade.png`
- 무역 협정 7개: `goals/GIR/goal_generic_positive_trade_relations.png`
- 국민 통합 6개: `goals/GIR/goal_generic_national_unity.png`
- 정치 압박·탄압 5개: `goals/GIR/goal_generic_political_pressure.png`
- 선전·연설 3개: `goals/GIR/goal_generic_propaganda.png`
- 민간 공장 3개: `goals/GIR/goal_generic_construct_civ_factory.png`

### 푀양파 (`MAR`)

- 국민 통합 11개: `goals/MAR/goal_generic_national_unity.png`
- 전쟁·진격 9개: `goals/MAR/goal_generic_major_war.png`
- 정치 압박·탄압 7개: `goals/MAR/goal_generic_political_pressure.png`
- 외교·우호 6개: `goals/MAR/goal_generic_improve_relations.png`
- 동맹 3개: `goals/MAR/goal_generic_major_alliance.png`

### 코뮌 (`COM`)

- 선전·연설 11개: `goals/COM/goal_generic_propaganda.png`
- 전쟁·진격 8개: `goals/COM/goal_generic_major_war.png`
- 국민 통합 6개: `goals/COM/goal_generic_national_unity.png`
- 보병·민병대 5개: `goals/COM/goal_generic_allies_build_infantry.png`
- 정치 압박·탄압 4개: `goals/COM/goal_generic_political_pressure.png`
- 민간 건설 3개: `goals/COM/goal_generic_construct_civilian.png`
- 군수 공장 3개: `goals/COM/goal_generic_construct_mil_factory.png`

### 자유 코뮌 연합 (`ANA`)

- 전쟁·진격 7개: `goals/ANA/goal_generic_major_war.png`
- 선전·연설 6개: `goals/ANA/goal_generic_propaganda.png`
- 국민 통합 5개: `goals/ANA/goal_generic_national_unity.png`
- 육군 교리 4개: `goals/ANA/goal_generic_army_doctrines.png`
- 민간 건설 3개: `goals/ANA/goal_generic_construct_civilian.png`
- 정치 압박·탄압 3개: `goals/ANA/goal_generic_political_pressure.png`
- 외교·우호 3개: `goals/ANA/goal_generic_improve_relations.png`

### 패전 (`DEF`)

- 국민 통합 3개: `goals/DEF/goal_generic_national_unity.png`

## 국민정신

| ID | 이름 |
|---|---|
| `LR_dyn_economy` | 프랑스 경제 |
| `LR_dyn_army` | 프랑스 육군 |
| `LR_dyn_navy` | 프랑스 해군 |
| `LR_dyn_air` | 프랑스 공군 |
| `LR_dyn_society` | 사회 정책 |
| `LR_dyn_army_fire` | 보병과 포병 |
| `LR_dyn_army_armour` | 기갑과 기동 |
| `LR_dyn_army_staff` | 참모본부 |
| `LR_dyn_army_supply` | 보급과 방어 |
| `LR_dyn_army_elite` | 정예 부대 |
| `LR_dyn_navy_line` | 주력 함대 |
| `LR_dyn_navy_light` | 경함대와 잠수함 |
| `LR_dyn_navy_air` | 해군 항공대 |
| `LR_dyn_regime_provisional` | 임시 정부 |
| `LR_dyn_regime_orleans` | 오를레앙 왕정 |
| `LR_dyn_regime_bourbon` | 부르봉 왕정 |
| `LR_dyn_regime_communist` | 프랑스 코뮌 |
| `LR_dyn_regime_jacobin` | 산악파 정부 |
| `LR_dyn_regime_girondin` | 지롱드 정부 |
| `LR_dyn_regime_marais` | 푀양파 정부 |
| `LR_dyn_regime_napoleon` | 통령 정부 |
| `LR_dyn_regime_empire` | 프랑스 제국 |
| `LR_dyn_regime_guardian` | 공화국의 수호자 |
| `LR_dyn_regime_petain` | 프랑스국 |
| `LR_dyn_regime_anarchist` | 자유 코뮌 연합 |
| `LR_dyn_regime_red` | 붉은 통령정 |
| `LR_dyn_regime_vanquished` | 점령된 프랑스 |
| `LR_dyn_ruler_louis` | 국왕 루이 20세 |
| `LR_dyn_ruler_orleans` | 국왕 장 드 오를레앙 |
| `LR_dyn_ruler_constitutional` | 입헌 국왕 |
| `LR_dyn_ruler_emperor` | 황제 나폴레옹 |
| `LR_dyn_ruler_president` | 대통령 나폴레옹 |
| `LR_dyn_ruler_petain` | 국가원수 페탱 |
| `LR_dyn_ruler_red` | 인민의 통령 나폴레옹 |
| `LR_dyn_sig_orleans` | 복수의 맹세 |
| `LR_dyn_sig_bourbon` | 백합과 제단 |
| `LR_dyn_sig_marais` | 1791년 헌법 |
| `LR_dyn_sig_jacobin` | 공안의 공화국 |
| `LR_dyn_sig_girondin` | 상인의 공화국 |
| `LR_dyn_sig_communist` | 노동자 평의회 |
| `LR_dyn_sig_anarchist` | 검은 깃발의 규율 |
| `LR_dyn_sig_napoleon` | 통령의 법전 |
| `LR_dyn_sig_empire` | 제국의 독수리 |
| `LR_dyn_sig_guardian` | 대통령의 서약 |
| `LR_dyn_sig_red` | 인민의 대육군 |
| `LR_dyn_sig_petain` | 노동, 가족, 조국 |
| `LR_dyn_defeat` | 대전쟁의 굴욕 |
| `LR_dyn_disarmed` | 버려진 군대 |
| `LR_dyn_power_orleans` | 권력 균형: 장교단과 궁정 |
| `LR_dyn_power_bourbon` | 권력 균형: 귀족과 교회와 개혁 관료 |
| `LR_dyn_power_communist` | 권력 균형: 구역 평의회와 중앙위원회 |
| `LR_dyn_power_anarchist` | 권력 균형: 강령파와 종합파 |
| `LR_dyn_power_napoleon` | 권력 균형: 원수들과 국무원 |
| `LR_dyn_power_red` | 권력 균형: 정치위원과 원수들 |
| `LR_dyn_power_petain` | 권력 균형: 군부와 라발파 정치가 |
| `LR_dyn_power_empire` | 권력 균형: 원수들과 국무원 |
| `LR_FRA_defeat` | 대전쟁의 굴욕 |
| `LR_JAP_han_autonomy` | 번의 자치 |
| `LR_FRA_algerian_crisis` | 알제리 위기 |
| `LR_FRA_resistance_high` | 격화된 저항 |
| `LR_FRA_minority` | 소수 내각 |
| `LR_FRA_gov_provisional` | 임시 정부 |
| `LR_FRA_gov_orleans` | 오를레앙 왕정 |
| `LR_FRA_gov_bourbon` | 부르봉 왕정 |
| `LR_FRA_gov_communist` | 프랑스 코뮌 |
| `LR_FRA_gov_jacobin` | 산악파 정부 |
| `LR_FRA_gov_girondin` | 지롱드 정부 |
| `LR_FRA_gov_marais` | 푀양파 정부 |
| `LR_FRA_gov_guardian` | 공화국의 수호자 |
| `LR_FRA_gov_napoleon` | 통령 정부 |
| `LR_GRE_reparations` | 막대한 배상금 |
| `LR_CNA_continental_army` | 제2차 대륙군 |
| `LR_great_power_army` | 승전국의 군대 |
| `LR_USA_arsenal` | 민주주의의 무기고 |
