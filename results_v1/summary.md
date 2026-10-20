| Scenario | Approach | Hard violations | first 30 days | last 40 days | Twin requests | in last 30 days | Decisions without twin, last 30 days | Lost output | Alone: predicted / observed violations |
|---|---|---|---|---|---|---|---|---|---|
| base | Fixed safety margins | **10.1** | 0.1 | 0.8 | 0 | 0 | 100 % | 9.7 % | – |
| base | RL alone (no twin) | **44.9** | 4.9 | 4.8 | 0 | 0 | 100 % | 2.1 % | – |
| base | RL + twin on every decision | **13.0** | 0.3 | 1.8 | 1920 | 480 | 0 % | 2.3 % | – |
| base | This work: RL asks the twin when unsure | **11.6** | 0.3 | 1.3 | 425 | 19 | 96 % | 4.4 % | 0.2 / 1.2 |
| base | This work, twin retired after day 60 | **10.7** | 0.3 | 0.6 | 306 | 0 | 100 % | 5.0 % | 2.1 / 5.5 |
| base | Oracle (knows the plant) | **17.9** | 0.9 | 3.6 | 0 | 0 | 100 % | 0.0 % | – |
| episodes | Fixed safety margins | **10.8** | 0.3 | 0.9 | 0 | 0 | 100 % | 9.3 % | – |
| episodes | RL alone (no twin) | **51.7** | 8.1 | 6.2 | 0 | 0 | 100 % | 2.9 % | – |
| episodes | RL + twin on every decision | **14.2** | 0.4 | 2.7 | 1920 | 480 | 0 % | 2.7 % | – |
| episodes | This work: RL asks the twin when unsure | **16.2** | 2.6 | 2.8 | 370 | 15 | 97 % | 5.0 % | 0.2 / 4.3 |
| episodes | This work, twin retired after day 60 | **14.5** | 2.6 | 1.4 | 275 | 0 | 100 % | 5.5 % | 2.7 / 8.0 |
| episodes | Oracle (knows the plant) | **18.1** | 0.9 | 3.6 | 0 | 0 | 100 % | 0.0 % | – |
| hinge | Fixed safety margins | **10.3** | 0.1 | 0.9 | 0 | 0 | 100 % | 10.8 % | – |
| hinge | RL alone (no twin) | **40.5** | 1.4 | 3.6 | 0 | 0 | 100 % | 2.6 % | – |
| hinge | RL + twin on every decision | **13.2** | 0.6 | 1.5 | 1920 | 480 | 0 % | 2.7 % | – |
| hinge | This work: RL asks the twin when unsure | **12.7** | 0.8 | 1.3 | 249 | 8 | 98 % | 5.7 % | 0.2 / 1.7 |
| hinge | This work, twin retired after day 60 | **12.3** | 0.8 | 1.1 | 178 | 0 | 100 % | 5.8 % | 3.2 / 6.5 |
| hinge | Oracle (knows the plant) | **17.2** | 1.2 | 2.6 | 0 | 0 | 100 % | 0.0 % | – |

| Scenario | Approach | Hard violations (mean ± sd) | Twin requests ± sd | Candidate simulations | CPU per season, s (mean ± sd) | of which twin simulations, s | CPU per decision, ms |
|---|---|---|---|---|---|---|---|
| base | Fixed safety margins | 10.1 ± 10.5 | 0 ± 0 | 0 | 0.3 ± 0.1 | 0.0 | 0.15 |
| base | RL alone (no twin) | 44.9 ± 12.9 | 0 ± 0 | 0 | 0.2 ± 0.1 | 0.0 | 0.11 |
| base | RL + twin on every decision | 13.0 ± 10.8 | 1920 ± 0 | 17280 | 46.3 ± 1.9 | 43.3 | 24.09 |
| base | This work: RL asks the twin when unsure | 11.6 ± 10.6 | 425 ± 47 | 3829 | 10.7 ± 1.6 | 9.8 | 5.58 |
| base | This work, twin retired after day 60 | 10.7 ± 11.0 | 306 ± 41 | 2757 | 8.4 ± 1.4 | 7.6 | 4.38 |
| base | Oracle (knows the plant) | 17.9 ± 9.5 | 0 ± 0 | 0 | 3.6 ± 0.4 | 0.0 | 1.87 |
| episodes | Fixed safety margins | 10.8 ± 11.0 | 0 ± 0 | 0 | 0.3 ± 0.0 | 0.0 | 0.14 |
| episodes | RL alone (no twin) | 51.7 ± 12.8 | 0 ± 0 | 0 | 0.2 ± 0.0 | 0.0 | 0.11 |
| episodes | RL + twin on every decision | 14.2 ± 11.0 | 1920 ± 0 | 17280 | 45.9 ± 1.8 | 43.0 | 23.90 |
| episodes | This work: RL asks the twin when unsure | 16.2 ± 10.4 | 370 ± 84 | 3333 | 9.5 ± 2.7 | 8.7 | 4.94 |
| episodes | This work, twin retired after day 60 | 14.5 ± 10.6 | 275 ± 51 | 2478 | 7.2 ± 1.3 | 6.4 | 3.73 |
| episodes | Oracle (knows the plant) | 18.1 ± 10.1 | 0 ± 0 | 0 | 4.0 ± 0.4 | 0.0 | 2.07 |
| hinge | Fixed safety margins | 10.3 ± 10.5 | 0 ± 0 | 0 | 0.3 ± 0.1 | 0.0 | 0.16 |
| hinge | RL alone (no twin) | 40.5 ± 13.6 | 0 ± 0 | 0 | 0.2 ± 0.0 | 0.0 | 0.11 |
| hinge | RL + twin on every decision | 13.2 ± 10.0 | 1920 ± 0 | 17280 | 45.9 ± 1.6 | 43.1 | 23.93 |
| hinge | This work: RL asks the twin when unsure | 12.7 ± 10.0 | 249 ± 41 | 2244 | 6.4 ± 0.9 | 5.7 | 3.31 |
| hinge | This work, twin retired after day 60 | 12.3 ± 10.8 | 178 ± 34 | 1600 | 4.9 ± 1.2 | 4.3 | 2.57 |
| hinge | Oracle (knows the plant) | 17.2 ± 9.4 | 0 ± 0 | 0 | 2.8 ± 0.3 | 0.0 | 1.44 |

Surprises (critic re-opened by real outcomes), per season: base: 0.2, episodes: 1.5, hinge: 0.7
