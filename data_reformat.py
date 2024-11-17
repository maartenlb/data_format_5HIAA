import numpy as np
import pandas as pd
from datetime import timedelta

old_data = "MKPython5HIAADUMMY.xlsx"
new_data = "DUMMY5HIAAlab.xlsx"

urine_candidates = set(["Urine 24-uursverzameling", "Urine anders 24-uursverzameling",
                        "Urine splint 24-uursverzameling", "Urine verblijfscatheter (CAD) 24uursverzameling"])
blood_candidates = set(["Veneus bloed", "Arterieel bloed"])

df_old = pd.read_excel(old_data)
df_new = pd.read_excel(new_data)

# Drop all rows while keeping the columns
df_old.drop(index=df_old.index, inplace=True)

#sort rows to be added by time so we can build starting at T0
df_new["DAT_TIJD_AFNAME"] = pd.to_datetime(df_new["DAT_TIJD_AFNAME"])

df_new = df_new.sort_values(by="DAT_TIJD_AFNAME", ascending=True)

urine_pair_dict = {}
plasma_pair_dict ={}
#make dict of pairs
for index, row in df_new.iterrows():
    #Load all relevant base values
    num = row["Nummer"]
    sex = row["SEX"]
    age = row["AGE"]
    time = row["DAT_TIJD_AFNAME"]
    value = row["UITSLAG"]
    test_name = row["MAT_SPEC"]
    test = None
    if test_name in urine_candidates:
        test = "urine"
    if test_name in blood_candidates:
        test = "blood"
    #if the test is not blood or urine related, we're done
    if test == None:
        continue


    for index2, row2 in df_new.iterrows():
        num2 = row2["Nummer"]
        time2 = row2["DAT_TIJD_AFNAME"]
        value2 = row2["UITSLAG"]
        test_name2 = row2["MAT_SPEC"]
        test2 = None
        if test_name2 in urine_candidates:
            test2 = "urine"
        if test_name2 in blood_candidates:
            test2 = "blood"
        
        if num != num2:
            continue
        if test == test2:
            continue
        if abs(time-time2) >= timedelta(days=182):
            continue
        best_value = None
        best_time = None
        best_diff = None

        time_diff = abs(time-time2)
        if best_diff is None or (time_diff <= best_diff and time_diff > timedelta(hours=48)):
            best_time = time2
            best_value = value2
            best_diff = time_diff
        
        if test == "blood":
            plasma_pair_dict[(num, value, time)] = (num2, best_value, best_time)
        if test == "urine":
            urine_pair_dict[(num, value, time)] = (num2, best_value, best_time)

#Iterate new data to insert by row
for index, row in df_new.iterrows():
    #Load all relevant base values
    num = row["Nummer"]
    sex = row["SEX"]
    age = row["AGE"]
    time = row["DAT_TIJD_AFNAME"]
    value = row["UITSLAG"]
    test_name = row["MAT_SPEC"]
    test = None
    if test_name in urine_candidates:
        test = "urine"
    if test_name in blood_candidates:
        test = "blood"
    #if the test is not blood or urine related, we're done
    if test == None:
        continue
    
    #Create new entry if num does not exist already
    if num not in df_old["Nummer"].values:
        max_id = df_old["ID"].max()
        if pd.isna(max_id):
            max_id = 0
        new_row = {
        "ID": max_id+1,
        "Nummer": num,
        "Sex": sex,
        "Age": age,
        }
        df_old = df_old._append(new_row, ignore_index=True)
    existing_row_index = df_old.index[df_old["Nummer"] == num][0]
    existing_row = df_old.iloc[existing_row_index]
    
    #insert new values into old table

    #always take minimum age
    df_old.loc[existing_row_index, "Age"] = min(age, df_old.loc[existing_row_index, "Age"])


    found = False
    t=0
    while found == False:
    #Check if column even exists
        if f"p5HIAA_T{t}" not in df_old.columns:
        # Create a new Series with NaN values and set it as a new column in the DataFrame
            df_old[f"p5HIAA_T{t}"] = pd.Series(dtype=float)
            df_old[f"u5HIAA_T{t}"] = pd.Series(dtype=float)
            df_old[f"u5HIAA_T{t}_2"] = pd.Series(dtype=float)
            df_old[f"u5HIAA_T{t}_mean"] = pd.Series(dtype=float)
            df_old[f"Date_of_collection_T{t}_plasma"] = pd.Series(dtype=float)
            df_old[f"Date_of_collection_T{t}_urine"] = pd.Series(dtype=float)
            df_old = df_old.copy()
            existing_row = df_old.iloc[existing_row_index]
        
        if test == "urine":
            # Check if urine within 48 hrs
            if not pd.isna(existing_row[f"Date_of_collection_T{t}_urine"]):
                if abs(time - existing_row[f"Date_of_collection_T{t}_urine"]) <= timedelta(hours=48):
                    found = True
                    df_old.loc[existing_row_index, f"u5HIAA_T{t}_2"] = value
                    df_old.loc[existing_row_index, f"u5HIAA_T{t}_mean"] = (existing_row[f"u5HIAA_T{t}"] + value) / 2

            # Check paired plasma
            if not pd.isna(existing_row[f"Date_of_collection_T{t}_plasma"]):
                if (num, value, time) in urine_pair_dict.keys():
                    num2, value2, time2 = urine_pair_dict[(num, value, time)]
                    if (num2, value2, time2) in plasma_pair_dict.keys():
                        num3, value3, time3 = plasma_pair_dict[(num2, value2, time2)]
                        if num == num3 and abs(time-time3) <= timedelta(hours=48) and value2 == existing_row[f"p5HIAA_T{t}"]:
                            if pd.isna(existing_row[f"u5HIAA_T{t}"]):
                                found = True
                                df_old.loc[existing_row_index, f"u5HIAA_T{t}"] = value
                                df_old.loc[existing_row_index, f"Date_of_collection_T{t}_urine"] = pd.to_datetime(time)
                            elif pd.isna(existing_row[f"u5HIAA_T{t}_2"]):
                                found = True
                                df_old.loc[existing_row_index, f"u5HIAA_T{t}_2"] = value
                                df_old.loc[existing_row_index, f"u5HIAA_T{t}_mean"] = (existing_row[f"u5HIAA_T{t}"] + value) / 2

        if test == "blood":
            # Check paired urine
            if not pd.isna(existing_row[f"Date_of_collection_T{t}_urine"]):
                if (num, value, time) in plasma_pair_dict.keys():
                    num2, value2, time2 = plasma_pair_dict[(num, value, time)]
                    if (value2 == existing_row[f"u5HIAA_T{t}"] or value2 == existing_row[f"u5HIAA_T{t}_2"]) and (urine_pair_dict[num2,value2,time2] == (num,value,time)):   
                        found = True
                        df_old.loc[existing_row_index, f"p5HIAA_T{t}"] = value
                        df_old.loc[existing_row_index, f"Date_of_collection_T{t}_plasma"] = pd.to_datetime(time)

        #if no edge-cases and both plasma and urine are empty, insert new timestep
        if pd.isna(existing_row[f"p5HIAA_T{t}"]) and pd.isna(existing_row[f"u5HIAA_T{t}"]):
            found = True
            if test == "blood":
                df_old.loc[existing_row_index, f"p5HIAA_T{t}"] = value
                df_old.loc[existing_row_index, f"Date_of_collection_T{t}_plasma"] = pd.to_datetime(time)
            if test == "urine":
                df_old.loc[existing_row_index, f"u5HIAA_T{t}"] = value
                df_old.loc[existing_row_index, f"Date_of_collection_T{t}_urine"] = pd.to_datetime(time)

        #update t value
        t += 1

# Save the updated dataframe
df_old.to_excel("processed_data.xlsx", index=False)
df_old.to_csv("processed_data.csv", index=False)
print("Finished processing")