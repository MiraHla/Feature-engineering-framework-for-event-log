# Feature-engineering-framework-for-event-logs
Developing a feature engineering framework for event logs using intra- and inter-case information
Implemantation for the master thesis Feature engineering framework for event logs by Carlos Darwin Garrido Marquez, Miroslava Hladikova, Wai Ying Wong.

 # Overview
This repository provides feature engineering framework for event logs using only event log base features (Case ID, activity label, timestamp and resource). 

Description of developed features 
Feature name | Type | Intra-/inter-case |	Definition |
-------------|------|-------------------|------------|
Time since last event[^1] |	Numeric|	Intra-case	|Number of minutes elapsed between current and last event in a case|
Time since case start[^1]|	Numeric	|Intra-case|	Number of minutes elapsed since the first event of the case|
Time since midnight |	Numeric|	Intra-case|	Number of Minutes elapsed since midnight of the day the event was executed|
Event number[^1] |	Numeric	|Intra-case|	Ranking of the event according to the order it was executed in within its case|
Month[^1] |	Numeric|	Intra-case	|Month number extracted from timestamp|
Weekday[^1]	|Numeric|	Intra-case|	Day of week extracted from timestamp|
Hour[^1]|	Numeric|	Intra-case	|Hour number extracted from timestamp|
Part of day|	Categorical|	Intra-case|	Part of day (e.g. “Morning”, “Afternoon”) extracted from timestamp|
Rework|	Boolean|	Intra-case|	Boolean indicating whether event has previously already been executed within same case |
Daily execution order	|Numeric|	Intra-case|	Rank of event according to sequence of execution within the day|
Resource frequency	|Numeric|	Intra-case|	Number of times resource has been used within the same case|
Open cases[^1]|	Numeric|	Inter-case|	Number of ongoing cases that are not yet complete at the time the event was executed|
Start cases in 7-day window	|Numeric|	Inter-case|	Number of cases started in last 7 days|
End cases in 7-day window|	Numeric|	Inter-case|	Number of cases ended in last 7 days|
Open cases in 7-day window|	Numeric|	Inter-case| Number of ongoing cases in last 7 days|
7-day same resource cases|	Numeric|	Inter-case|	Number of cases that used the same resource in last 7 days|
7-day time since last event of resource|	Numeric|	Inter-case|	Average time since last event for the resource in question within the last 7 days|
7-day time since last event of event|	Numeric|	Inter-case|	Average time since last event for the event in question within the last 7 days|
7-day rolling average of time since last event| 	Numeric|	Inter-case|	Rolling 7-day average of time since last event for all events|



For testing purposes it is possible to use test event log [BPIC 2017](https://data.4tu.nl/articles/dataset/BPI_Challenge_2017/12696884/1)
[^1]: Teinemaa, I., Dumas, M., Rosa, M. la, & Maggi, F. M. (2019). Outcome-oriented predictive process monitoring: Review and benchmark. In ACM Transactions on Knowledge Discovery from Data (Vol. 13, Issue 2). Association for Computing Machinery. https://doi.org/10.1145/3301300
