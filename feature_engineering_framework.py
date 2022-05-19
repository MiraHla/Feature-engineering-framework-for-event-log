import pandas as pd
import numpy as np
import os
from datetime import timedelta

#path to get the event log in .csv format
#example dataset
directory= "BPIC17.csv"
dataset_name=["BPIC17"]

#define columns for case ID, activity, resource and timestamp
case_id_col = 'case:concept:name'
activity_col = 'concept:name'
resource_col = 'org:resource'
timestamp_col = 'time:timestamp'

#in case the event log does not have a complete timestamp define lifecycle status:
#leave empty quatation marks '' if not present
lifecycle_col = 'lifecycle:transition'

#feature engineering - information about features can be found in README file

def time_since_last_event(group):
    group = group.sort_values(timestamp_col, ascending=False, kind='mergesort')
    
    tmp = group[timestamp_col] - group[timestamp_col].shift(-1)
    group["timesincelastevent"] = tmp.apply(lambda x: float(x / np.timedelta64(1, 'm'))) # m is for minutes
    group["timesincelastevent"]=group["timesincelastevent"].fillna(0)
    return group

def time_since_case_start(group):
    group = group.sort_values(timestamp_col, ascending=False, kind='mergesort')
    tmp = group[timestamp_col] - group[timestamp_col].iloc[-1]
    group["timesincecasestart"] = tmp.apply(lambda x: float(x / np.timedelta64(1, 'm'))) # m is for minutes
    group["timesincecasestart"]=group["timesincecasestart"].fillna(0)
    return group

def event_nr(group):
    group = group.sort_values(timestamp_col, ascending=True, kind='mergesort')
    group["event_nr"] = range(1, len(group) + 1)
    
    return group

def rework(group):
    if lifecycle_col=='':
        group["rework"] = group.duplicated(subset=[activity_col]) 
    else:
        group["rework"] = group.duplicated(subset=[activity_col, lifecycle_col])  
    return group

def resource_freq(group):
    group = group.sort_values([timestamp_col], ascending=True, kind='mergesort')
    group["res_freq"] = group.groupby(resource_col).cumcount() + 1
    return group

def get_open_cases(date):
    return sum((dt_first_last_timestamps["start_time"] <= date) & (dt_first_last_timestamps["end_time"] > date))

def get_starts_cases_days (date, dias=7):
    return sum((dt_first_last_timestamps["start_time"] <= date) & (dt_first_last_timestamps["start_time"] >= (date-timedelta(days=dias))))

def get_end_cases_days(date):
    return sum((dt_first_last_timestamps["end_time"] <= date) & (dt_first_last_timestamps["end_time"] >= (date-timedelta(days=7))))
                
def get_open_cases_days(date):
    return sum(~(((dt_first_last_timestamps["start_time"] > date) & 
               (dt_first_last_timestamps["end_time"] >= date)) 
               | ((dt_first_last_timestamps["start_time"] < (date-timedelta(days=7))) & 
                          (dt_first_last_timestamps["end_time"] <= (date-timedelta(days=7)))
               )))

def get_resource_count (date,resource):
    dt_resource_filter=dt_resource_timestamps[(dt_resource_timestamps[resource_col]==resource)
                                              & (dt_resource_timestamps[timestamp_col]<=date)
                                              & (dt_resource_timestamps[timestamp_col]>=(date-timedelta(days=7)))][case_id_col]
    return dt_resource_filter.nunique()

def get_7d_timesincelastevent_R (date,resource):
    return data_ts["timesincelastevent"][(data_ts[resource_col]==resource)
                                               &(data_ts[timestamp_col]<=date)
                                               &(data_ts[timestamp_col]>=(date-timedelta(days=7)))].mean()

def get_7d_timesincelastevent_E (date,act):
    return data_EV["timesincelastevent"][(data_EV[activity_col]==act)
                                               &(data_EV[timestamp_col]<=date)
                                               &(data_EV[timestamp_col]>=(date-timedelta(days=7)))].mean()

print("--------------------------------------------------")


data = pd.read_csv(directory,sep=',', nrows=100) 
data[timestamp_col] = pd.to_datetime(data[timestamp_col],utc=True)

print("Extracting intra-case features...")

print("Time since last event")
data = data.groupby(case_id_col).apply(time_since_last_event)
data = data.reset_index(drop=True)

print("Time since case start")
data = data.groupby(case_id_col).apply(time_since_case_start)
data = data.reset_index(drop=True)

print("Time since midnight")
data["timesincemidnight"] = data[timestamp_col].dt.hour * 60 + data[timestamp_col].dt.minute

print("Event number")
data = data.groupby(case_id_col).apply(event_nr)
data = data.reset_index(drop=True)

print("Month")
data["month"] = data[timestamp_col].dt.month

print("Weekday")
data["weekday"] = data[timestamp_col].dt.weekday

print("Hour")
data["hour"] = data[timestamp_col].dt.hour

print("Part of day")
data["part_of_day"] = (data[timestamp_col].dt.hour % 24 + 4) // 4
data["part_of_day"].replace({1: 'Late Night',
                      2: 'Early Morning',
                      3: 'Morning',
                      4: 'Noon',
                      5: 'Evening',
                      6: 'Night'}, inplace=True)

print("Rework")
data = data.groupby(case_id_col).apply(rework)


print("Daily execution order")  
data[timestamp_col] = pd.to_datetime(data[timestamp_col])  
data["date"] = data[timestamp_col].dt.date
data = data.sort_values([timestamp_col], ascending=True, kind='mergesort')
data["daily_ex_order"] = data.groupby("date").cumcount()+1
data = data.drop(["date"], axis=1)


print("Resource frequency")
data = data.groupby(case_id_col).apply(resource_freq)

print('--------------------------------------------------')
print("Extracting inter-case features...")

print("Open cases")
data = data.sort_values([timestamp_col], ascending=True, kind='mergesort')
dt_first_last_timestamps = data.groupby(case_id_col)[timestamp_col].agg([min, max])
dt_first_last_timestamps.columns = ["start_time", "end_time"]
data["open_cases"] = data[timestamp_col].apply(get_open_cases)

print("Start cases in 7-day window")
data["7d_start_cases"]=data[timestamp_col].apply(get_starts_cases_days)

print("End cases in 7-day window")
data["7d_end_cases"]=data[timestamp_col].apply(get_end_cases_days)

print("Open cases in 7-day window")
data["7d_open_cases"]=data[timestamp_col].apply(get_open_cases_days)

print("7-day same resource cases")
dt_resource_timestamps=data[[case_id_col,resource_col,timestamp_col]]
data["7d_#cases_resouce"]=data[[timestamp_col,resource_col]].apply(lambda x: get_resource_count(*x), axis=1)  
    
print("7-day time since last event of resource")
data_ts = data[[timestamp_col, "timesincelastevent", resource_col]]
data["7d_timesincelastevent_R"] = data[[timestamp_col,resource_col]].apply(lambda x: get_7d_timesincelastevent_R(*x), axis=1)

print("7-day time since last event of event")
data_EV = data[[timestamp_col, "timesincelastevent", activity_col]]
data["7d_timesincelastevent_E"] = data[[timestamp_col,activity_col]].apply(lambda x: get_7d_timesincelastevent_E(*x), axis=1)

print("7-day rolling average of time since last event")
data.index = pd.DatetimeIndex(data[timestamp_col])
data = data.sort_index()
data["7d_ravg_tsle"] = data["timesincelastevent"].rolling('7d').mean()
data = data.reset_index(drop=True)

#Output file
data.to_csv( "%s_feature_engineering.csv" % (dataset_name),sep=";", index=False)
