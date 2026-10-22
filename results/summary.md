Mean ± standard error over seeds (seasons).

| Scenario | Approach | Hard violations, h | of which no safe level, h | controllable, h | Twin requests | Decisions without twin, last 30 days | CPU per season, s | of which twin, s | Output, % of ideal | Alone: predicted / observed violations | Surprises |
|---|---|---|---|---|---|---|---|---|---|---|---|
| base | Fixed safety margins | 10.1 ± 3.3 | 9.7 ± 3.4 | 0.4 ± 0.2 | 0 ± 0 | 100 % | 0.2 ± 0.0 | 0.0 | 90.3 ± 0.1 | – | 0.0 |
| base | RL alone (no twin) | 44.9 ± 4.1 | 22.9 ± 4.4 | 22.0 ± 0.9 | 0 ± 0 | 100 % | 0.2 ± 0.0 | 0.0 | 97.9 ± 0.2 | – | 0.0 |
| base | RL + twin on every decision | 12.5 ± 3.4 | 10.5 ± 3.4 | 2.0 ± 0.5 | 1920 ± 0 | 0 % | 28.5 ± 0.3 | 26.5 | 97.4 ± 0.0 | – | 0.0 |
| base | This work: RL asks the twin when unsure | 11.8 ± 3.3 | 10.2 ± 3.3 | 1.6 ± 0.3 | 460 ± 20 | 95 % | 7.3 ± 0.3 | 6.6 | 95.5 ± 0.2 | 0.23 / 0.7 | 0.0 |
| base | This work, twin retired after day 60 | 11.0 ± 3.3 | 9.9 ± 3.3 | 1.1 ± 0.3 | 336 ± 12 | 100 % | 5.4 ± 0.2 | 4.9 | 95.0 ± 0.3 | 1.97 / 5.2 | 0.8 |
| base | Ideal reference (knows the plant) | 17.9 ± 3.0 | 11.1 ± 3.3 | 6.8 ± 0.6 | 0 ± 0 | 100 % | 1.8 ± 0.0 | 0.0 | 100.0 ± 0.0 | – | 0.0 |
| base | Ablation: Boole bound instead of union | 12.4 ± 3.4 | 10.5 ± 3.4 | 1.9 ± 0.3 | 570 ± 21 | 91 % | 8.7 ± 0.3 | 7.9 | 95.9 ± 0.2 | 0.17 / 1.0 | 0.3 |
| base | Ablation: no attribution checks | 11.8 ± 3.3 | 10.0 ± 3.3 | 1.8 ± 0.5 | 406 ± 20 | 96 % | 6.4 ± 0.3 | 5.9 | 95.6 ± 0.2 | 0.23 / 1.8 | 0.6 |
| base | Ablation: no interaction learning (twin uncorrected) | 35.7 ± 3.5 | 12.0 ± 3.3 | 23.7 ± 1.3 | 174 ± 5 | 99 % | 2.8 ± 0.1 | 2.4 | 98.2 ± 0.2 | 0.13 / 13.9 | 7.4 |
| episodes | Fixed safety margins | 10.5 ± 3.3 | 9.8 ± 3.3 | 0.7 ± 0.3 | 0 ± 0 | 100 % | 0.2 ± 0.0 | 0.0 | 90.7 ± 0.2 | – | 0.0 |
| episodes | RL alone (no twin) | 50.4 ± 4.3 | 22.3 ± 4.4 | 28.1 ± 0.8 | 0 ± 0 | 100 % | 0.2 ± 0.0 | 0.0 | 97.3 ± 0.2 | – | 0.0 |
| episodes | RL + twin on every decision | 14.5 ± 3.3 | 10.6 ± 3.3 | 3.9 ± 0.9 | 1920 ± 0 | 0 % | 28.0 ± 0.3 | 26.0 | 94.9 ± 0.5 | – | 0.0 |
| episodes | This work: RL asks the twin when unsure | 15.7 ± 3.5 | 10.5 ± 3.3 | 5.2 ± 0.9 | 437 ± 14 | 98 % | 7.0 ± 0.3 | 6.4 | 95.5 ± 0.2 | 0.21 / 3.9 | 1.0 |
| episodes | This work, twin retired after day 60 | 13.0 ± 3.3 | 10.4 ± 3.3 | 2.6 ± 0.9 | 336 ± 12 | 100 % | 5.5 ± 0.2 | 4.9 | 95.3 ± 0.3 | 1.98 / 7.2 | 1.3 |
| episodes | Ideal reference (knows the plant) | 17.6 ± 3.0 | 11.4 ± 3.2 | 6.2 ± 0.6 | 0 ± 0 | 100 % | 2.0 ± 0.1 | 0.0 | 100.0 ± 0.0 | – | 0.0 |
| episodes | Ablation: Boole bound instead of union | 15.3 ± 3.5 | 10.8 ± 3.3 | 4.5 ± 0.7 | 535 ± 16 | 96 % | 8.2 ± 0.2 | 7.5 | 95.8 ± 0.2 | 0.16 / 2.7 | 0.9 |
| episodes | Ablation: no attribution checks | 16.6 ± 3.6 | 10.2 ± 3.3 | 6.4 ± 1.0 | 387 ± 14 | 98 % | 6.1 ± 0.3 | 5.6 | 95.5 ± 0.3 | 0.21 / 5.5 | 2.1 |
| episodes | Ablation: no interaction learning (twin uncorrected) | 44.3 ± 3.4 | 12.5 ± 3.2 | 31.8 ± 1.0 | 176 ± 5 | 99 % | 2.8 ± 0.1 | 2.4 | 97.8 ± 0.1 | 0.12 / 20.3 | 8.9 |
| hinge | Fixed safety margins | 10.3 ± 3.3 | 9.7 ± 3.4 | 0.6 ± 0.3 | 0 ± 0 | 100 % | 0.2 ± 0.0 | 0.0 | 89.2 ± 0.1 | – | 0.0 |
| hinge | RL alone (no twin) | 40.5 ± 4.3 | 23.7 ± 4.6 | 16.8 ± 1.4 | 0 ± 0 | 100 % | 0.2 ± 0.0 | 0.0 | 97.4 ± 0.2 | – | 0.0 |
| hinge | RL + twin on every decision | 12.7 ± 3.2 | 10.5 ± 3.4 | 2.2 ± 0.6 | 1920 ± 0 | 0 % | 27.6 ± 0.4 | 25.7 | 96.6 ± 0.1 | – | 0.0 |
| hinge | This work: RL asks the twin when unsure | 11.3 ± 3.3 | 9.8 ± 3.4 | 1.5 ± 0.4 | 360 ± 12 | 97 % | 5.8 ± 0.2 | 5.2 | 94.0 ± 0.2 | 0.22 / 0.4 | 0.1 |
| hinge | This work, twin retired after day 60 | 10.7 ± 3.4 | 9.5 ± 3.4 | 1.2 ± 0.4 | 274 ± 7 | 100 % | 4.5 ± 0.1 | 4.0 | 93.7 ± 0.2 | 2.50 / 5.0 | 0.5 |
| hinge | Ideal reference (knows the plant) | 17.2 ± 3.0 | 11.3 ± 3.3 | 5.9 ± 0.8 | 0 ± 0 | 100 % | 1.4 ± 0.0 | 0.0 | 100.0 ± 0.0 | – | 0.0 |

Hours with hard-limit events, mean per season (controllable hours in brackets):

| Scenario | Approach | shortage | lost | cooling_short | peak | thermal | hours without a safe level |
|---|---|---|---|---|---|---|---|
| base | Fixed safety margins | 0.0 (0.0) | 0.0 (0.0) | 1.9 (0.2) | 0.0 (0.0) | 9.4 (0.2) | 53.8 |
| base | RL alone (no twin) | 17.9 (15.4) | 4.2 (3.4) | 13.4 (4.1) | 6.3 (3.4) | 17.2 (0.4) | 66.5 |
| base | RL + twin on every decision | 1.3 (1.3) | 0.2 (0.2) | 1.9 (0.2) | 0.3 (0.3) | 10.2 (0.2) | 59.4 |
| base | This work: RL asks the twin when unsure | 1.1 (1.1) | 0.2 (0.2) | 1.8 (0.1) | 0.1 (0.1) | 10.0 (0.3) | 56.3 |
| base | This work, twin retired after day 60 | 0.5 (0.5) | 0.2 (0.2) | 1.9 (0.2) | 0.1 (0.1) | 9.7 (0.3) | 55.5 |
| base | Ideal reference (knows the plant) | 5.4 (5.4) | 0.3 (0.3) | 2.1 (0.4) | 0.7 (0.7) | 10.9 (0.3) | 63.4 |
| base | Ablation: Boole bound instead of union | 1.2 (1.2) | 0.1 (0.1) | 2.1 (0.3) | 0.2 (0.2) | 10.1 (0.2) | 57.1 |
| base | Ablation: no attribution checks | 1.4 (1.4) | 0.2 (0.2) | 1.9 (0.2) | 0.0 (0.0) | 9.7 (0.2) | 57.0 |
| base | Ablation: no interaction learning (twin uncorrected) | 15.6 (15.6) | 3.0 (3.0) | 6.3 (4.3) | 3.8 (3.8) | 11.8 (0.6) | 64.4 |
| episodes | Fixed safety margins | 0.2 (0.2) | 0.1 (0.1) | 1.9 (0.2) | 0.0 (0.0) | 9.6 (0.3) | 54.7 |
| episodes | RL alone (no twin) | 24.8 (22.0) | 7.5 (6.3) | 13.2 (4.1) | 5.5 (3.1) | 17.3 (0.4) | 66.8 |
| episodes | RL + twin on every decision | 3.2 (3.2) | 0.7 (0.7) | 1.9 (0.2) | 0.3 (0.3) | 10.3 (0.2) | 59.4 |
| episodes | This work: RL asks the twin when unsure | 4.8 (4.8) | 1.0 (1.0) | 1.8 (0.1) | 0.1 (0.1) | 10.2 (0.2) | 57.6 |
| episodes | This work, twin retired after day 60 | 2.1 (2.1) | 0.3 (0.3) | 1.9 (0.2) | 0.1 (0.1) | 10.1 (0.2) | 57.4 |
| episodes | Ideal reference (knows the plant) | 4.9 (4.9) | 0.3 (0.3) | 2.1 (0.4) | 0.6 (0.6) | 11.2 (0.3) | 64.1 |
| episodes | Ablation: Boole bound instead of union | 3.8 (3.8) | 0.9 (0.9) | 2.1 (0.3) | 0.2 (0.2) | 10.4 (0.2) | 58.2 |
| episodes | Ablation: no attribution checks | 6.0 (6.0) | 1.5 (1.5) | 1.9 (0.2) | 0.0 (0.0) | 9.9 (0.2) | 58.2 |
| episodes | Ablation: no interaction learning (twin uncorrected) | 24.3 (24.3) | 6.9 (6.9) | 6.2 (4.1) | 3.4 (3.4) | 12.2 (0.6) | 64.7 |
| hinge | Fixed safety margins | 0.0 (0.0) | 0.0 (0.0) | 1.9 (0.2) | 0.0 (0.0) | 9.6 (0.4) | 52.7 |
| hinge | RL alone (no twin) | 11.8 (7.9) | 3.9 (1.8) | 13.8 (4.5) | 7.9 (4.9) | 17.2 (0.5) | 65.9 |
| hinge | RL + twin on every decision | 1.4 (1.4) | 0.2 (0.2) | 1.9 (0.2) | 0.4 (0.4) | 10.2 (0.2) | 58.7 |
| hinge | This work: RL asks the twin when unsure | 0.6 (0.6) | 0.2 (0.2) | 1.9 (0.2) | 0.3 (0.3) | 9.7 (0.4) | 56.0 |
| hinge | This work, twin retired after day 60 | 0.3 (0.3) | 0.1 (0.1) | 2.0 (0.3) | 0.2 (0.2) | 9.4 (0.4) | 55.5 |
| hinge | Ideal reference (knows the plant) | 3.7 (3.7) | 0.3 (0.3) | 2.1 (0.4) | 1.5 (1.5) | 11.1 (0.3) | 62.5 |

Attribution (this work, mean over seeds): learned slope ± sd at season end (true value), first day identified, residuals rejected by A5 (of which on fault days 70–74), A6 drift detections and first day, A6 model-form detections, drift offset at season end, A1 at season end:

| Scenario | Approach | Coupling | Slope (true) | Identified on day | A5 rejections (fault days) | A6 drift detections | first drift day | A6 misfit detections | drift offset | A1 at end |
|---|---|---|---|---|---|---|---|---|---|---|
| base | This work: RL asks the twin when unsure | air | -0.97 ± 0.01 (-1.00) | 0.1 (10/10) | 13.7 (13.2) | 0.5 | 110 | 0.0 | -0.7 | 9/10 |
| base | This work: RL asks the twin when unsure | power | 0.31 ± 0.04 (0.32) | 18.4 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| base | This work: RL asks the twin when unsure | chiller | -1.51 ± 0.04 (-1.50) | 23.9 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| base | Ablation: no attribution checks | air | -1.00 ± 0.02 (-1.00) | nan (0/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 8/10 |
| base | Ablation: no attribution checks | power | 0.30 ± 0.05 (0.32) | nan (0/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| base | Ablation: no attribution checks | chiller | -1.50 ± 0.05 (-1.50) | nan (0/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| base | Ablation: no interaction learning (twin uncorrected) | air | -0.97 ± 0.02 (-1.00) | 0.2 (10/10) | 5.8 (5.8) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| base | Ablation: no interaction learning (twin uncorrected) | power | 0.31 ± 0.06 (0.32) | 39.8 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| base | Ablation: no interaction learning (twin uncorrected) | chiller | -1.52 ± 0.07 (-1.50) | 30.2 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| base | RL + twin on every decision | air | -0.97 ± 0.01 (-1.00) | 0.1 (10/10) | 76.8 (75.2) | 3.7 | 83 | 0.1 | -4.0 | 9/10 |
| base | RL + twin on every decision | power | 0.33 ± 0.03 (0.32) | 6.9 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| base | RL + twin on every decision | chiller | -1.51 ± 0.04 (-1.50) | 22.0 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| episodes | This work: RL asks the twin when unsure | air | -1.01 ± 0.01 (-1.00) | 0.1 (10/10) | 11.7 (11.3) | 1.2 | 73 | 0.0 | -2.0 | 9/10 |
| episodes | This work: RL asks the twin when unsure | power | 0.31 ± 0.05 (0.32) | 18.4 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| episodes | This work: RL asks the twin when unsure | chiller | -1.51 ± 0.05 (-1.50) | 23.9 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| episodes | Ablation: no attribution checks | air | -1.07 ± 0.02 (-1.00) | nan (0/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| episodes | Ablation: no attribution checks | power | 0.30 ± 0.06 (0.32) | nan (0/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| episodes | Ablation: no attribution checks | chiller | -1.50 ± 0.05 (-1.50) | nan (0/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| episodes | Ablation: no interaction learning (twin uncorrected) | air | -0.97 ± 0.02 (-1.00) | 0.2 (10/10) | 6.2 (6.2) | 0.8 | 75 | 0.1 | -1.1 | 7/10 |
| episodes | Ablation: no interaction learning (twin uncorrected) | power | 0.30 ± 0.06 (0.32) | 39.8 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| episodes | Ablation: no interaction learning (twin uncorrected) | chiller | -1.52 ± 0.07 (-1.50) | 30.2 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| episodes | RL + twin on every decision | air | -1.14 ± 0.05 (-1.00) | 0.1 (10/10) | 76.8 (75.2) | 8.1 | 68 | 1.3 | -4.2 | 6/10 |
| episodes | RL + twin on every decision | power | 0.33 ± 0.03 (0.32) | 6.9 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| episodes | RL + twin on every decision | chiller | -1.51 ± 0.04 (-1.50) | 22.0 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| hinge | This work: RL asks the twin when unsure | air | -0.37 ± 0.08 (hinge) | 18.7 (10/10) | 8.4 (8.1) | 1.1 | 54 | 2.0 | -1.4 | 7/10 |
| hinge | This work: RL asks the twin when unsure | power | 0.32 ± 0.05 (0.32) | 19.7 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| hinge | This work: RL asks the twin when unsure | chiller | -1.50 ± 0.05 (-1.50) | 24.2 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| hinge | RL + twin on every decision | air | -0.14 ± 0.03 (hinge) | 11.0 (10/10) | 76.8 (75.2) | 5.5 | 44 | 4.3 | -2.1 | 2/10 |
| hinge | RL + twin on every decision | power | 0.33 ± 0.03 (0.32) | 6.9 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
| hinge | RL + twin on every decision | chiller | -1.51 ± 0.04 (-1.50) | 22.0 (10/10) | 0.0 (0.0) | 0.0 | nan | 0.0 | 0.0 | 10/10 |
