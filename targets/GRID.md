# The starting grid: three finance cycles at three levels of difficulty

Rows are finance cycles. Columns are difficulty:

- **Tier 1:** about 7 days. Clean actors and pure mechanics: timing lags, batching, fee netting, weekends and bank holidays.
- **Tier 2:** about 60 days. Operational exceptions and human slips across two month ends.
- **Tier 3:** 60-90 days. Several companies, foreign currency, fraud, control failures and audits.

Every target below is modeled on a real company's SEC filings. Its `SOURCES.md` says which facts are real (marked † in the prompt) and which are invented.

## Built targets

| Cycle | Tier 1 (7 days) | Tier 2 (60 days) | Tier 3 (60-90 days) |
|---|---|---|---|
| **Order-to-cash** | [`studio_payments/studio_payments_7day.md`](studio_payments/studio_payments_7day.md): Stripe Connect platform for 280 studios, first week of 2025 (Stripe and Nacha rules) | [`studio_payments/studio_payments_60day.md`](studio_payments/studio_payments_60day.md): same platform, January-February 2025 | [`short_drama_app/PROMPT.md`](short_drama_app/PROMPT.md): short-drama app paid through Apple, Google, Stripe, PayPal and a phone carrier, four regions, a Singapore company with a Cayman parent, Q1 2025 (**FlexTV / Mega Matrix 20-F**) |
| **Procure-to-pay** | [`defense_machining/defense_machining_7day.md`](defense_machining/defense_machining_7day.md): two defense machine shops, three-way match, net 30, `2% 10` discounts across Presidents' Day, February 2025 (**TechPrecision 10-K**) | [`cookie_wholesale/cookie_wholesale_60day.md`](cookie_wholesale/cookie_wholesale_60day.md): bakery brand with distributor deductions, airline portal rejections, an overrun and a duplicate bill, January-February 2025 (**Legally Addictive Foods Form C**; full year in `PROMPT.md`) | [`defense_machining/PROMPT.md`](defense_machining/PROMPT.md): same shops, fiscal Q4 2025: a business email compromise that succeeds, goods received but not invoiced at year end, split orders, holds released without receipts, a covenant default (**TechPrecision 10-K**) |
| **Record-to-report** | [`data_security_saas/data_security_saas_7day.md`](data_security_saas/data_security_saas_7day.md): bank-to-books matching, marketplace and plugin payout summary entries, trial balance check, July 1-7, 2023 (**Data443 10-K/A and XBRL**) | [`data_security_saas/PROMPT.md`](data_security_saas/PROMPT.md): same company, July-August 2023: multi-year unearned revenue rollforward, prepaids, payroll straddling month ends, note conversions, the real cash flow restatement (**Data443**) | [`data_security_saas/data_security_saas_audit_90day.md`](data_security_saas/data_security_saas_audit_90day.md): the 2022 audit: request lists, confirmations, weekend and round-dollar entries, one person posting and approving (**Data443**)<br>[`id_verification_saas/PROMPT.md`](id_verification_saas/PROMPT.md): a filed annual report restated for option awards and unremitted withholding taxes, spring 2022 (**Intellicheck 10-K/A**) |

Notes:

- `cookie_wholesale/PROMPT.md` covers a full year. The 60-day cut fills the tier 2 cell. The original stays as it was.
- Each row uses one company across tiers where it fits, so a tier change changes difficulty, not the business.
- Order-to-cash tier 3 and record-to-report tier 3 have no clean twin yet. The table below lists candidates.

## More real companies for each cell

These are **leads, not verified fits.** Each filing matched the search phrase shown in EDGAR full-text search. Read the filing before building a target from it. The leads marked ✓ were opened and checked in this session.

### Order-to-cash, tier 3: several processors, foreign currency, parent and subsidiaries

| Company | Filing | Why it matched |
|---|---|---|
| ✓ Mega Matrix (FlexTV), Singapore / Cayman | [20-F 2025](https://www.sec.gov/Archives/edgar/data/1953021/000121390026044335/ea0281860-20f_mega.htm) | built: `short_drama_app` |
| ✓ Zedge, New York (Lithuania, Israel, Emojipedia in Australia) | [10-K FY2026](https://www.sec.gov/Archives/edgar/data/1667313/000121390026113312/ea0309434-10k_zedge.htm) | App Store, Google Play and Meta process payments; virtual currency (Zedge Credits, GuruShots coins); 1.3 million active subscriptions; 82 staff mostly in Israel and Lithuania; FX forwards; largest customer 34.2% of revenue |
| Motorsport Games, Miramar FL (UK, Netherlands) | [10-K 2025](https://www.sec.gov/Archives/edgar/data/1821175/000149315226009532/form10-k.htm) | Steam, PlayStation, App Store, foreign currency |
| Snail, Culver City CA (parent in China) | [10-K 2022](https://www.sec.gov/Archives/edgar/data/1886894/000110465923038408/snal-20221231x10k.htm) | Steam, PlayStation, App Store, foreign currency |
| PLAYSTUDIOS, Las Vegas (Israel, Hong Kong) | [10-K 2024](https://www.sec.gov/Archives/edgar/data/1823878/000182387825000017/myps-20241231.htm) | in-app purchases through both stores, foreign currency translation |
| Spark Networks SE, Berlin (US dating apps) | [10-K 2022](https://www.sec.gov/Archives/edgar/data/1705338/000162828023010147/lov-20221231.htm) | subscriptions; manual journal entries named in a material weakness |
| DatChat / Myseum, New Brunswick NJ | [10-K 2024](https://www.sec.gov/Archives/edgar/data/1648960/000101376225004290/ea0234787-10k_datchat.htm) | in-app purchases, foreign subsidiary |
| DoubleDown Interactive, Seoul (US subsidiary) | [20-F 2023](https://www.sec.gov/Archives/edgar/data/1799567/000119312524080583/d750578d20f.htm) | social casino coins through both stores, foreign currency |
| GDEV, BVI (games) | [20-F 2025](https://www.sec.gov/Archives/edgar/data/1848739/000110465926037847/gdev-20251231x20f.htm) | in-app purchases, foreign currency |
| Gamehaus, Shanghai | [20-F](https://www.sec.gov/Archives/edgar/data/2000530/000149315226044775/form20-f.htm) | mobile games, both stores |
| CooTek, Shanghai | [20-F 2025](https://www.sec.gov/Archives/edgar/data/1734262/000110465926048866/ctkyy-20251231x20f.htm) | apps including short dramas, both stores |
| DarkIris, Hong Kong | [20-F](https://www.sec.gov/Archives/edgar/data/2058584/000149315226004488/form20-f.htm) | mobile games, both stores |
| Skillz, Las Vegas | [10-K 2025](https://www.sec.gov/Archives/edgar/data/1801661/000180166126000020/sklz-20251231.htm) | paid entry fees, both stores |
| RoyaLand, Bermuda | [20-F](https://www.sec.gov/Archives/edgar/data/1924064/000121390025104706/ea0262853-20f_royaland.htm) | game with in-app purchases |
| Apphive (Form C) | [Form C 2023](https://www.sec.gov/Archives/edgar/data/1962006/000196200623000002/apphive_formc.pdf) | small-company scale; both stores, foreign currency translation |

### Procure-to-pay, tiers 1 and 3: purchasing-heavy companies with control weaknesses

| Company | Filing | Why it matched |
|---|---|---|
| ✓ TechPrecision, Westminster MA / Los Angeles | [10-K FY2025](https://www.sec.gov/Archives/edgar/data/1328792/000141057825001537/tpcs-20250331x10k.htm) | built: `defense_machining` |
| Solitron Devices, West Palm Beach FL | [10-K FY2026](https://www.sec.gov/Archives/edgar/data/91668/000143774926018779/sodi20260225_10k.htm) | small military semiconductor maker; purchase orders, segregation of duties and approval in a material weakness |
| Coffee Holding Co., Staten Island NY | [10-K FY2025](https://www.sec.gov/Archives/edgar/data/1007019/000149315226004052/form10-k.htm) | coffee roaster and importer; segregation of duties and purchase approvals in a material weakness (FY2022 10-K/A) |
| Pioneer Power Solutions, Fort Lee NJ | [10-K 2024](https://www.sec.gov/Archives/edgar/data/1449792/000164117225004681/form10-k.htm) | receiving reports and purchase orders in a material weakness |
| Envirotech Vehicles, Corona CA | [10-K 2023](https://www.sec.gov/Archives/edgar/data/1563568/000143774924009818/adom20231231_10k.htm) | receiving reports and purchase orders in a material weakness |
| Sonim Technologies, Austin TX | [10-K/A 2021](https://www.sec.gov/Archives/edgar/data/1178697/000156459022024599/sonm-10ka_20211231.htm) | goods received not invoiced in a material weakness |
| Ducommun, Costa Mesa CA | [10-K/A 2025](https://www.sec.gov/Archives/edgar/data/30305/000162828026032536/dco-20251231.htm) | unrecorded liabilities in a material weakness (larger company) |
| Karat Packaging, Chino CA | [10-K 2024](https://www.sec.gov/Archives/edgar/data/1758021/000162828025012816/krt-20241231.htm) | vendor master file in a material weakness |
| Ramaco Resources, Lexington KY | [10-K/A 2021](https://www.sec.gov/Archives/edgar/data/1687187/000110465923002700/metc-20211231x10ka.htm) | vendor master file in a material weakness |
| Tattooed Chef, Paramount CA | [10-K 2020](https://www.sec.gov/Archives/edgar/data/1741231/000121390021016721/f10k2020_tattooedchef.htm) | early-payment discounts, purchase orders, later restated |
| Concrete Pumping, Thornton CO | [10-K FY2022](https://www.sec.gov/Archives/edgar/data/1703956/000143774923002137/bbpp20221031_10k.htm) | unrecorded liabilities and manual journal entries |
| Omnitek Engineering, Vista CA | [10-K/A 2024](https://www.sec.gov/Archives/edgar/data/1404804/000109690625000528/omtk-20241231.htm) | tiny manufacturer; segregation of duties and approvals |
| Trident Brands, Brookfield WI | [10-K 2019](https://www.sec.gov/Archives/edgar/data/1421907/000147793220001361/tdnt_10k.htm) | early-payment discounts, purchase orders, segregation of duties |

### Procure-to-pay, tier 2: food brands living on distributor deductions (cookie_wholesale's siblings)

All Form C filers whose filings mention UNFI, KeHE and deductions, except the last two:

| Company | Filing |
|---|---|
| Goodwolf Feeding Co, Portland OR | [Form C 2021](https://www.sec.gov/Archives/edgar/data/1805743/000180574321000003/goodwolfii_formc.pdf) |
| WellWell, New York | [C-AR 2021](https://www.sec.gov/Archives/edgar/data/1666081/000166608121000003/wellwellcar.pdf) |
| Rojo's Famous, Normandy Park WA | [Form C/A 2021](https://www.sec.gov/Archives/edgar/data/1856715/000185671521000003/formc.pdf) |
| Midgie's Good Cream, Napa CA | [Form C 2021](https://www.sec.gov/Archives/edgar/data/1845329/000184532921000001/formc.pdf) |
| Kokus, Venice CA | [Form C 2021](https://www.sec.gov/Archives/edgar/data/1835638/000183563821000001/formcsunscoop2.pdf) |
| Good Beverage, Hinsdale IL | [Form C 2022](https://www.sec.gov/Archives/edgar/data/1796998/000179699822000001/hey.pdf) |
| Hagel Bites, Schwenksville PA | [Form C/A 2025](https://www.sec.gov/Archives/edgar/data/2041954/000204195425000003/sprinklebitesformc.pdf) |
| Poppilu, Chicago | [Form C 2021](https://www.sec.gov/Archives/edgar/data/1852227/000185222721000001/poppiluformc.pdf) |
| Vital Leaf, Portland OR | [Form C/A 2021](https://www.sec.gov/Archives/edgar/data/1687278/000168727821000001/formc.pdf) |
| Genius Juice, Torrance CA | [Form C/A 2021](https://www.sec.gov/Archives/edgar/data/1796106/000179610621000001/geniusjuiceformca0002.pdf) |
| American Provenance, Mount Horeb WI | [Form C 2021](https://www.sec.gov/Archives/edgar/data/1797422/000179742221000003/apformc001.pdf) |
| LES Foods, Boston | [Form C 2021](https://www.sec.gov/Archives/edgar/data/1851291/000185129121000001/bohanaformc.pdf) |
| Make Real Foods, Chicago | [Form C 2021](https://www.sec.gov/Archives/edgar/data/1849940/000184994021000001/makerealfoodsformc1.pdf) |
| True Made Foods, Alexandria VA | [Form C 2021](https://www.sec.gov/Archives/edgar/data/1691692/000169169221000002/tmfformc.pdf) |
| Zaahh, San Anselmo CA | [Form C 2022](https://www.sec.gov/Archives/edgar/data/1770329/000177032922000005/awesomefc.pdf) |
| Healthy Crop, San Diego | [Form C 2021](https://www.sec.gov/Archives/edgar/data/1860044/000186004421000001/ChasinDreamsFarmFormC.pdf) |
| Vital Farms, Austin TX (10-K, larger) | [10-K 2022](https://www.sec.gov/Archives/edgar/data/1579733/000095017023006950/vitl-20221225.htm) |
| Alkaline Water Co., Scottsdale AZ (10-K) | [10-K FY2023](https://www.sec.gov/Archives/edgar/data/1532390/000106299323016652/form10k.htm) |

### Record-to-report, all tiers: small software companies with restatements or weak close controls

| Company | Filing | Why it matched |
|---|---|---|
| ✓ Data443, Research Triangle Park NC | [10-K/A 2022](https://www.sec.gov/Archives/edgar/data/1068689/000149315223030030/form10-ka.htm) | built: `data_security_saas` |
| ✓ Intellicheck, Melville NY | [10-K/A 2021](https://www.sec.gov/Archives/edgar/data/1040896/000149315222016322/form10ka.htm) | built: `id_verification_saas` |
| iCoreConnect, Ocoee FL | [10-K/A 2022](https://www.sec.gov/Archives/edgar/data/1408057/000147793223004637/icct_10k.htm) | dental software; restatement, deferred revenue |
| CXApp, Palo Alto CA | [10-K/A 2022](https://www.sec.gov/Archives/edgar/data/1820875/000141057823000742/cxai-20221231x10ka.htm) | workplace software; restatement, deferred revenue |
| Minim, Manchester NH | [10-K/A 2021](https://www.sec.gov/Archives/edgar/data/1467761/000149315222023610/form10ka.htm) | restatement, deferred revenue |
| Healthcare Triangle, Pleasanton CA | [10-K/A 2023](https://www.sec.gov/Archives/edgar/data/1839285/000121390025014503/ea0230296-10ka1_healthcare.htm) | restatement, deferred revenue |
| VSee Health, Boca Raton FL | [10-K/A 2024](https://www.sec.gov/Archives/edgar/data/1864531/000155837025011815/vsee-20241231x10ka.htm) | restatement, deferred revenue |
| Cyngn, Mountain View CA | [10-K/A](https://www.sec.gov/Archives/edgar/data/1874097/000121390025110998/ea0264946-10ka1_cyngn.htm) | restatement, deferred revenue |
| Logiq, New York | [10-K/A 2022](https://www.sec.gov/Archives/edgar/data/1335112/000157587224000486/lgiq-20221231.htm) | restatement, deferred revenue |
| Rubicon Technologies, Lexington KY | [10-K/A 2023](https://www.sec.gov/Archives/edgar/data/1862068/000182912624003558/rubicontechnologies_10ka2.htm) | restatement, deferred revenue |
| DZS, Plano TX | [10-K/A 2022](https://www.sec.gov/Archives/edgar/data/1101680/000095017024096338/dzsi-20221231.htm) | restatement (Korea), deferred revenue |
| Cleartronic, Clearwater FL | [10-K FY2024](https://www.sec.gov/Archives/edgar/data/1362516/000109181825000013/clri0930202410k.htm) | tiny software company; segregation of duties, journal entries |
| Powerfleet, Woodcliff Lake NJ | [10-K FY2025](https://www.sec.gov/Archives/edgar/data/1774170/000162828025033105/aiot-20250331.htm) | manual journal entries in a material weakness |
| TruBridge, Mobile AL | [10-K 2024](https://www.sec.gov/Archives/edgar/data/1169445/000116944525000042/tbrg-20241231.htm) | manual journal entries in a material weakness |
| Evolv Technologies, Houston TX | [10-K 2023](https://www.sec.gov/Archives/edgar/data/1805385/000162828024008053/nhic-20231231.htm) | subscriptions; restated for sales practices |
| Kiora Pharmaceuticals, Salt Lake City | [10-K/A 2021](https://www.sec.gov/Archives/edgar/data/1372514/000141057822001931/kprx-20211231x10ka.htm) | post-closing adjustments in a material weakness |
| 1847 Holdings, New York | [10-K/A](https://www.sec.gov/Archives/edgar/data/1599407/000121390025073709/ea0251187-10ka1_1847hold.htm) | post-closing adjustments, several subsidiaries |
| Selectis Health, Greenwood Village CO | [10-K/A](https://www.sec.gov/Archives/edgar/data/727346/000149315224039543/form10-ka.htm) | post-closing adjustments |

### Order-to-cash, tiers 1 and 2: small sellers whose money runs through processors

| Company | Filing | Why it matched |
|---|---|---|
| Hylete, San Diego (apparel) | [C-AR/A 2021](https://www.sec.gov/Archives/edgar/data/1599738/000168316822003143/hyletereport.pdf) | Stripe, chargebacks, payouts |
| Xtrades, St. Louis (subscriptions) | [C-AR 2025](https://www.sec.gov/Archives/edgar/data/2017510/000201751026000002/form_car.pdf) | Stripe, chargebacks, payouts |
| NeuroGym, Solana Beach CA (online courses) | [Form C/A 2026](https://www.sec.gov/Archives/edgar/data/2089067/000187285626000209/neurogymformca060426.pdf) | Stripe, chargebacks, payouts |
| RYVYL, San Diego (payments) | [10-K 2024](https://www.sec.gov/Archives/edgar/data/1419275/000118518525000244/rvyl10k123124.htm) | PayPal, Stripe, Adyen, foreign currency |
| Existing targets | `brewery_taproom`, `dtc_brand`, `pt_clinic`, `vacation_rentals` | full-year order-to-cash worlds that can be cut into 7- and 60-day windows like `studio_payments` |

## Real fraud events to borrow from

Business email compromise losses that public companies have disclosed. ✓ means the amount and description were read in this session:

- ✓ **NETSTREIT, Q2 2024.** Two fraudulent transfers totaling $3.3 million to someone impersonating a development partner, a $2.8 million loss after insurance ([release](https://www.sec.gov/Archives/edgar/data/1798100/000179810024000064/netstreitearningsrelease-q.htm)).
- ✓ **Journey Medical, Q3 2021.** About $9.5 million "erroneously wired to fraudulent accounts", shown as its own operating expense line ([release](https://www.sec.gov/Archives/edgar/data/1867066/000110465921148566/tm2135030d1_ex99-1.htm)).
- ✓ **Mega Matrix, December 2021.** A business email compromise of the Delaware company, after which large transfers needed extra confirmation ([20-F](https://www.sec.gov/Archives/edgar/data/1953021/000121390026044335/ea0281860-20f_mega.htm)).
- **Unchecked leads.** These matched "business email compromise" with "loss of". Check them for an actual incident, not risk-factor wording:
  - Sky Quarry ([10-K/A 2024](https://www.sec.gov/Archives/edgar/data/1812447/000109690625001422/skyq-20241231_10kz.htm));
  - Century Casinos ([10-K/A 2024](https://www.sec.gov/Archives/edgar/data/911147/000091114725000056/cnty-20241231x10ka.htm));
  - MineralRite ([10-K/A](https://www.sec.gov/Archives/edgar/data/1096296/000153949726001592/n4863_x24-10ka.htm));
  - ADTRAN ([10-K/A 2024](https://www.sec.gov/Archives/edgar/data/926282/000095017025075366/adtn-20241231.htm));
  - Ault Alliance, a "spoofed" vendor wire ([10-K/A 2022](https://www.sec.gov/Archives/edgar/data/896493/000121465923007664/aa5192301ka1.htm)).

## How these were found

- **[EDGAR full-text search](https://efts.sec.gov/LATEST/search-index?q=%22business%20email%20compromise%22&forms=10-K).** Phrases were combined with form filters: `10-K,10-K/A` for control weaknesses and restatements, `8-K` for incidents, `C,C-AR` for small companies, `20-F` for foreign parents. The queries are in each table's "why it matched" column.
- **Reading a filing.** Fetching a filing page through the fetch tool works in pages (offset 0, 100000, 200000 ...). Scripts that fetch from www.sec.gov are blocked without a contact email.
- **[SEC XBRL company concept API](https://data.sec.gov/api/xbrl/companyconcept/CIK0001068689/us-gaap/DeferredRevenueCurrent.json).** It gives every tagged balance by quarter, such as deferred revenue, revenue and accrued liabilities. It is how Data443's quarterly balances were found when the filing text was too long to read.
