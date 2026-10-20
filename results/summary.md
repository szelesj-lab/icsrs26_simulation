Mean ± standard error over seeds (seasons).

| Scenario | Approach | Hard violations, h | of which no safe level, h | controllable, h | Twin requests | Decisions without twin, last 30 days | CPU per season, s | of which twin, s | Output, % of ideal | Alone: predicted / observed violations | Surprises |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base | Fixed safety margins | 10.1 ± 3.3 | 9.7 ± 3.4 | 0.4 ± 0.2 | 0 ± 0 | 100 % | 0.2 ± 0.0 | 0.0 | 90.3 ± 0.1 | – | 0.0 |
| base | RL alone (no twin) | 44.9 ± 4.1 | 22.9 ± 4.4 | 22.0 ± 0.9 | 0 ± 0 | 100 % | 0.1 ± 0.0 | 0.0 | 97.9 ± 0.2 | – | 0.0 |
| base | RL + twin on every decision | 13.0 ± 3.4 | 10.6 ± 3.3 | 2.4 ± 0.5 | 1920 ± 0 | 0 % | 27.1 ± 0.2 | 25.7 | 97.7 ± 0.1 | – | 0.0 |
| base | This work: RL asks the twin when unsure | 12.1 ± 3.3 | 10.4 ± 3.3 | 1.7 ± 0.4 | 439 ± 22 | 95 % | 6.6 ± 0.3 | 6.1 | 95.7 ± 0.2 | 0.23 / 1.0 | 0.2 |
| base | This work, twin retired after day 60 | 11.6 ± 3.3 | 10.0 ± 3.3 | 1.6 ± 0.4 | 322 ± 13 | 100 % | 5.0 ± 0.2 | 4.6 | 95.0 ± 0.3 | 2.10 / 5.8 | 1.0 |
| base | Ideal reference (knows the plant) | 17.9 ± 3.0 | 11.1 ± 3.3 | 6.8 ± 0.6 | 0 ± 0 | 100 % | 1.5 ± 0.0 | 0.0 | 100.0 ± 0.0 | – | 0.0 |
| base | Ablation: Boole bound instead of union | 12.3 ± 3.3 | 10.4 ± 3.3 | 1.9 ± 0.4 | 585 ± 32 | 90 % | 8.4 ± 0.4 | 7.8 | 95.9 ± 0.2 | 0.17 / 0.7 | 0.1 |
| base | Ablation: no attribution checks | 11.6 ± 3.4 | 10.0 ± 3.3 | 1.6 ± 0.4 | 437 ± 17 | 94 % | 6.4 ± 0.3 | 5.9 | 95.8 ± 0.2 | 0.23 / 1.1 | 0.2 |
| episodes | Fixed safety margins | 10.5 ± 3.3 | 9.8 ± 3.3 | 0.7 ± 0.3 | 0 ± 0 | 100 % | 0.2 ± 0.0 | 0.0 | 90.7 ± 0.2 | – | 0.0 |
| episodes | RL alone (no twin) | 50.4 ± 4.3 | 22.3 ± 4.4 | 28.1 ± 0.8 | 0 ± 0 | 100 % | 0.1 ± 0.0 | 0.0 | 97.3 ± 0.2 | – | 0.0 |
| episodes | RL + twin on every decision | 14.7 ± 3.1 | 11.0 ± 3.3 | 3.7 ± 0.6 | 1920 ± 0 | 0 % | 27.1 ± 0.2 | 25.7 | 97.3 ± 0.1 | – | 0.0 |
| episodes | This work: RL asks the twin when unsure | 15.4 ± 3.7 | 10.6 ± 3.3 | 4.8 ± 1.1 | 416 ± 18 | 98 % | 6.3 ± 0.3 | 5.8 | 95.4 ± 0.2 | 0.19 / 3.8 | 1.1 |
| episodes | This work, twin retired after day 60 | 13.7 ± 3.6 | 10.4 ± 3.3 | 3.3 ± 1.1 | 322 ± 13 | 100 % | 4.9 ± 0.2 | 4.5 | 95.0 ± 0.3 | 2.11 / 7.9 | 1.9 |
| episodes | Ideal reference (knows the plant) | 17.6 ± 3.0 | 11.4 ± 3.2 | 6.2 ± 0.6 | 0 ± 0 | 100 % | 1.6 ± 0.0 | 0.0 | 100.0 ± 0.0 | – | 0.0 |
| episodes | Ablation: Boole bound instead of union | 14.4 ± 2.9 | 10.5 ± 3.3 | 3.9 ± 0.9 | 625 ± 40 | 88 % | 8.9 ± 0.6 | 8.3 | 95.8 ± 0.1 | 0.14 / 2.1 | 0.6 |
| episodes | Ablation: no attribution checks | 17.0 ± 3.6 | 10.2 ± 3.3 | 6.8 ± 0.9 | 409 ± 12 | 98 % | 6.0 ± 0.2 | 5.6 | 95.7 ± 0.2 | 0.21 / 5.5 | 2.0 |
| hinge | Fixed safety margins | 10.3 ± 3.3 | 9.7 ± 3.4 | 0.6 ± 0.3 | 0 ± 0 | 100 % | 0.2 ± 0.0 | 0.0 | 89.2 ± 0.1 | – | 0.0 |
| hinge | RL alone (no twin) | 40.5 ± 4.3 | 23.7 ± 4.6 | 16.8 ± 1.4 | 0 ± 0 | 100 % | 0.1 ± 0.0 | 0.0 | 97.4 ± 0.2 | – | 0.0 |
| hinge | RL + twin on every decision | 12.9 ± 3.2 | 10.8 ± 3.3 | 2.1 ± 0.5 | 1920 ± 0 | 0 % | 27.3 ± 0.2 | 25.9 | 97.0 ± 0.1 | – | 0.0 |
| hinge | This work: RL asks the twin when unsure | 11.6 ± 3.2 | 9.9 ± 3.4 | 1.7 ± 0.4 | 379 ± 9 | 96 % | 5.6 ± 0.1 | 5.2 | 94.3 ± 0.2 | 0.22 / 0.7 | 0.0 |
| hinge | This work, twin retired after day 60 | 11.0 ± 3.3 | 9.5 ± 3.4 | 1.5 ± 0.4 | 287 ± 7 | 100 % | 4.4 ± 0.1 | 4.0 | 93.8 ± 0.2 | 2.38 / 5.1 | 0.7 |
| hinge | Ideal reference (knows the plant) | 17.2 ± 3.0 | 11.3 ± 3.3 | 5.9 ± 0.8 | 0 ± 0 | 100 % | 1.2 ± 0.0 | 0.0 | 100.0 ± 0.0 | – | 0.0 |

Hours with hard-limit events, mean per season (controllable hours in brackets):

| Scenario | Approach | shortage | lost | cooling_short | peak | thermal | hours without a safe level |
|---|---|---|---|---|---|---|---|
| base | Fixed safety margins | 0.0 (0.0) | 0.0 (0.0) | 1.9 (0.2) | 0.0 (0.0) | 9.4 (0.2) | 53.8 |
| base | RL alone (no twin) | 17.9 (15.4) | 4.2 (3.4) | 13.4 (4.1) | 6.3 (3.4) | 17.2 (0.4) | 66.5 |
| base | RL + twin on every decision | 1.7 (1.7) | 0.2 (0.2) | 1.8 (0.1) | 0.4 (0.4) | 10.3 (0.2) | 59.7 |
| base | This work: RL asks the twin when unsure | 1.3 (1.3) | 0.2 (0.2) | 1.8 (0.1) | 0.1 (0.1) | 10.1 (0.2) | 56.9 |
| base | This work, twin retired after day 60 | 0.9 (0.9) | 0.3 (0.3) | 1.9 (0.2) | 0.1 (0.1) | 9.9 (0.4) | 56.7 |
| base | Ideal reference (knows the plant) | 5.4 (5.4) | 0.3 (0.3) | 2.1 (0.4) | 0.7 (0.7) | 10.9 (0.3) | 63.4 |
| base | Ablation: Boole bound instead of union | 1.3 (1.3) | 0.2 (0.2) | 1.9 (0.2) | 0.2 (0.2) | 10.1 (0.2) | 57.3 |
| base | Ablation: no attribution checks | 1.1 (1.1) | 0.2 (0.2) | 1.8 (0.1) | 0.1 (0.1) | 9.8 (0.3) | 56.7 |
| episodes | Fixed safety margins | 0.2 (0.2) | 0.1 (0.1) | 1.9 (0.2) | 0.0 (0.0) | 9.6 (0.3) | 54.7 |
| episodes | RL alone (no twin) | 24.8 (22.0) | 7.5 (6.3) | 13.2 (4.1) | 5.5 (3.1) | 17.3 (0.4) | 66.8 |
| episodes | RL + twin on every decision | 3.1 (3.1) | 0.5 (0.5) | 1.8 (0.1) | 0.3 (0.3) | 10.7 (0.2) | 60.4 |
| episodes | This work: RL asks the twin when unsure | 4.4 (4.4) | 0.8 (0.8) | 1.8 (0.1) | 0.1 (0.1) | 10.3 (0.2) | 58.0 |
| episodes | This work, twin retired after day 60 | 2.7 (2.7) | 0.7 (0.7) | 1.9 (0.2) | 0.1 (0.1) | 10.2 (0.3) | 57.9 |
| episodes | Ideal reference (knows the plant) | 4.9 (4.9) | 0.3 (0.3) | 2.1 (0.4) | 0.6 (0.6) | 11.2 (0.3) | 64.1 |
| episodes | Ablation: Boole bound instead of union | 3.4 (3.4) | 0.8 (0.8) | 1.9 (0.2) | 0.1 (0.1) | 10.2 (0.2) | 58.7 |
| episodes | Ablation: no attribution checks | 6.3 (6.3) | 1.5 (1.5) | 1.8 (0.1) | 0.1 (0.1) | 10.0 (0.3) | 58.1 |
| hinge | Fixed safety margins | 0.0 (0.0) | 0.0 (0.0) | 1.9 (0.2) | 0.0 (0.0) | 9.6 (0.4) | 52.7 |
| hinge | RL alone (no twin) | 11.8 (7.9) | 3.9 (1.8) | 13.8 (4.5) | 7.9 (4.9) | 17.2 (0.5) | 65.9 |
| hinge | RL + twin on every decision | 1.3 (1.3) | 0.2 (0.2) | 1.8 (0.1) | 0.5 (0.5) | 10.5 (0.2) | 59.0 |
| hinge | This work: RL asks the twin when unsure | 0.8 (0.8) | 0.0 (0.0) | 1.9 (0.2) | 0.4 (0.4) | 9.7 (0.3) | 55.8 |
| hinge | This work, twin retired after day 60 | 0.4 (0.4) | 0.0 (0.0) | 2.0 (0.3) | 0.4 (0.4) | 9.4 (0.4) | 55.0 |
| hinge | Ideal reference (knows the plant) | 3.7 (3.7) | 0.3 (0.3) | 2.1 (0.4) | 1.5 (1.5) | 11.1 (0.3) | 62.5 |

Attribution (this work, mean over seeds): learned slope ± sd at season end (true value), first day identified, residuals rejected by A5 (of which on fault days 70–74), drift detections (A6) and first detection day:

| Scenario | Approach | Coupling | Slope (true) | Identified on day | A5 rejections (fault days) | A6 drift detections | first drift day |
|---|---|---|---|---|---|---|---|
| base | This work: RL asks the twin when unsure | air | -0.98 ± 0.01 (-1.00) | 0.2 (10/10) | 11.5 (10.9) | 0.4 | 106 |
| base | This work: RL asks the twin when unsure | power | 0.31 ± 0.04 (0.32) | 16.4 (10/10) | 0.0 (0.0) | 0.0 | nan |
| base | This work: RL asks the twin when unsure | chiller | -1.51 ± 0.05 (-1.50) | 24.1 (10/10) | 0.0 (0.0) | 0.0 | nan |
| base | Ablation: no attribution checks | air | -0.99 ± 0.02 (-1.00) | nan (0/10) | 0.0 (0.0) | 0.0 | nan |
| base | Ablation: no attribution checks | power | 0.32 ± 0.05 (0.32) | nan (0/10) | 0.0 (0.0) | 0.0 | nan |
| base | Ablation: no attribution checks | chiller | -1.51 ± 0.05 (-1.50) | nan (0/10) | 0.0 (0.0) | 0.0 | nan |
| base | RL + twin on every decision | air | -0.99 ± 0.01 (-1.00) | 0.1 (10/10) | 76.8 (75.2) | 2.5 | 83 |
| base | RL + twin on every decision | power | 0.33 ± 0.03 (0.32) | 6.8 (10/10) | 0.0 (0.0) | 0.0 | nan |
| base | RL + twin on every decision | chiller | -1.51 ± 0.04 (-1.50) | 22.0 (10/10) | 0.0 (0.0) | 0.0 | nan |
| episodes | This work: RL asks the twin when unsure | air | -1.00 ± 0.02 (-1.00) | 0.2 (10/10) | 9.6 (9.1) | 1.1 | 72 |
| episodes | This work: RL asks the twin when unsure | power | 0.31 ± 0.05 (0.32) | 16.4 (10/10) | 0.0 (0.0) | 0.0 | nan |
| episodes | This work: RL asks the twin when unsure | chiller | -1.51 ± 0.05 (-1.50) | 24.1 (10/10) | 0.0 (0.0) | 0.0 | nan |
| episodes | Ablation: no attribution checks | air | -1.07 ± 0.02 (-1.00) | nan (0/10) | 0.0 (0.0) | 0.0 | nan |
| episodes | Ablation: no attribution checks | power | 0.32 ± 0.05 (0.32) | nan (0/10) | 0.0 (0.0) | 0.0 | nan |
| episodes | Ablation: no attribution checks | chiller | -1.52 ± 0.05 (-1.50) | nan (0/10) | 0.0 (0.0) | 0.0 | nan |
| episodes | RL + twin on every decision | air | -0.99 ± 0.01 (-1.00) | 0.1 (10/10) | 76.8 (75.2) | 6.7 | 67 |
| episodes | RL + twin on every decision | power | 0.33 ± 0.03 (0.32) | 6.8 (10/10) | 0.0 (0.0) | 0.0 | nan |
| episodes | RL + twin on every decision | chiller | -1.51 ± 0.04 (-1.50) | 22.0 (10/10) | 0.0 (0.0) | 0.0 | nan |
| hinge | This work: RL asks the twin when unsure | air | -0.77 ± 0.02 (hinge) | 14.2 (10/10) | 8.7 (8.2) | 3.7 | 28 |
| hinge | This work: RL asks the twin when unsure | power | 0.31 ± 0.04 (0.32) | 21.5 (10/10) | 0.0 (0.0) | 0.1 | 60 |
| hinge | This work: RL asks the twin when unsure | chiller | -1.50 ± 0.05 (-1.50) | 23.7 (10/10) | 0.0 (0.0) | 0.0 | nan |
| hinge | RL + twin on every decision | air | -0.64 ± 0.01 (hinge) | 10.9 (10/10) | 76.8 (75.2) | 13.6 | 26 |
| hinge | RL + twin on every decision | power | 0.33 ± 0.03 (0.32) | 6.8 (10/10) | 0.0 (0.0) | 0.0 | nan |
| hinge | RL + twin on every decision | chiller | -1.51 ± 0.04 (-1.50) | 22.0 (10/10) | 0.0 (0.0) | 0.0 | nan |
