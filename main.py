import numpy as np
import pandas as pd
import sqlalchemy as sal
from SQL_query import *
import pyodbc


def sql_connection(parameters):
    # this creates the connection to the SQL Server do not change
    params = parameters
    engine = sal.create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
    return engine


def DIBELS_merge_data(df1, df2):
    df1 = df1
    df2 = df2
    file_location = r'C:\Users\salasrodriguez.j\OneDrive - Modesto City Schools\Desktop\Combo Class Report'
    file_name = 'Schools Key.csv'
    complete_filepath = file_location + "\\" + file_name
    df3 = pd.read_csv(complete_filepath, encoding='unicode_escape')
    merged_df = pd.merge(df1, df2, on='Student Id', how='inner')
    merged_df = pd.merge(merged_df, df3, on='School ID', how='inner')
    # columns that are unnamed were being added so the code below will remove those columns
    df = merged_df[merged_df.columns.drop(list(merged_df.filter(regex='Unnamed')))]
    df = df.drop_duplicates(subset=['Student Id'], keep='last')
    return df


def DIBELS_transform_data(df):
    merged_df = df
    # Loop through each row of the dataframe
    for index, row in merged_df.iterrows():
        # Check the value in the 'COURSE1' column for each row
        # and replace with the new value
        if row['COURSE1'] == 'Home Room Transitional Kindergarten':
            merged_df.at[index, 'COURSE1'] = 'TK'
        elif row['COURSE1'] == 'Gr 0 Home Room Regular' or row['COURSE1'] == 'Gr 0 Home Room Open Plan':
            merged_df.at[index, 'COURSE1'] = 'K'
        elif row['COURSE1'] == 'Gr 1 Home Room Regular' or row['COURSE1'] == 'Gr 1 Home Room Open Plan':
            merged_df.at[index, 'COURSE1'] = '1'
        elif row['COURSE1'] == 'Gr 2 Home Room Regular' or row['COURSE1'] == 'Gr 2 Home Room Open Plan':
            merged_df.at[index, 'COURSE1'] = '2'
        elif row['COURSE1'] == 'Gr 3 Home Room Regular' or row['COURSE1'] == 'Gr 3 Home Room Open Plan':
            merged_df.at[index, 'COURSE1'] = '3'
        elif row['COURSE1'] == 'Gr 4 Home Room Regular' or row['COURSE1'] == 'Gr 4 Home Room Open Plan':
            merged_df.at[index, 'COURSE1'] = '4'
        elif row['COURSE1'] == 'Gr 5 Home Room Regular' or row['COURSE1'] == 'Gr 5 Home Room Open Plan':
            merged_df.at[index, 'COURSE1'] = '5'
        elif row['COURSE1'] == 'Gr 6 Home Room Regular' or row['COURSE1'] == 'Gr 6 Home Room Open Plan':
            merged_df.at[index, 'COURSE1'] = '6'
        else:
            # If the value is anything else, leave it as it is
            pass
    for index, row in merged_df.iterrows():
        # Check the value in the 'COURSE1' column for each row
        # and replace with the new value
        if row['COURSE2'] == 'Home Room Transitional Kindergarten':
            merged_df.at[index, 'COURSE2'] = 'TK'
        elif row['COURSE2'] == 'Gr 0 Home Room Regular' or row['COURSE2'] == 'Gr 0 Home Room Open Plan':
            merged_df.at[index, 'COURSE2'] = 'K'
        elif row['COURSE2'] == 'Gr 1 Home Room Regular' or row['COURSE2'] == 'Gr 1 Home Room Open Plan':
            merged_df.at[index, 'COURSE2'] = '1'
        elif row['COURSE2'] == 'Gr 2 Home Room Regular' or row['COURSE2'] == 'Gr 2 Home Room Open Plan':
            merged_df.at[index, 'COURSE2'] = '2'
        elif row['COURSE2'] == 'Gr 3 Home Room Regular' or row['COURSE2'] == 'Gr 3 Home Room Open Plan':
            merged_df.at[index, 'COURSE2'] = '3'
        elif row['COURSE2'] == 'Gr 4 Home Room Regular' or row['COURSE2'] == 'Gr 4 Home Room Open Plan':
            merged_df.at[index, 'COURSE2'] = '4'
        elif row['COURSE2'] == 'Gr 5 Home Room Regular' or row['COURSE2'] == 'Gr 5 Home Room Open Plan':
            merged_df.at[index, 'COURSE2'] = '5'
        elif row['COURSE2'] == 'Gr 6 Home Room Regular' or row['COURSE2'] == 'Gr 6 Home Room Open Plan':
            merged_df.at[index, 'COURSE2'] = '6'
        else:
            # If the value is anything else, leave it as it is
            pass
    merged_df['Teacher Name'] = df[['LAST_NAME', 'FIRST_NAME']].apply(lambda x: ', '.join(x[x.notnull()]), axis=1)
    merged_df['Combo Type'] = ''
    for index, row in merged_df.iterrows():
        if row['COURSE1'] == 'K' and row['Course2'] == 'TK' or row['COURSE1'] == 'TK' and row['COURSE2'] == 'K':
            merged_df.at[index, 'Combo Type'] = 'Grades TK-K'
        elif row['COURSE1'] == 'K' and row['Course2'] == '1' or row['COURSE1'] == '1' and row['COURSE2'] == 'K':
            merged_df.at[index, 'Combo Type'] = 'Grades K-1'
        elif row['COURSE1'] == '1' and row['Course2'] == '2' or row['COURSE1'] == '2' and row['COURSE2'] == '1':
            merged_df.at[index, 'Combo Type'] = 'Grades 1-2'
        elif row['COURSE1'] == '2' and row['Course2'] == '3' or row['COURSE1'] == '3' and row['COURSE2'] == '2':
            merged_df.at[index, 'Combo Type'] = 'Grades 2-3'
        elif row['COURSE1'] == '3' and row['Course2'] == '4' or row['COURSE1'] == '4' and row['COURSE2'] == '3':
            merged_df.at[index, 'Combo Type'] = 'Grades 3-4'
        elif row['COURSE1'] == '4' and row['Course2'] == '5' or row['COURSE1'] == '5' and row['COURSE2'] == '4':
            merged_df.at[index, 'Combo Type'] = 'Grades 4-5'
        elif row['COURSE1'] == '5' and row['Course2'] == '6' or row['COURSE1'] == '6' and row['COURSE2'] == '5':
            merged_df.at[index, 'Combo Type'] = 'Grades 5-6'

    for index, row in merged_df.iterrows():
        if row['GRADE_LEVEL'] == 0:
            merged_df.at[index, 'GRADE_LEVEL'] = 'K'
        else:
            # If the value is anything else, leave it as it is
            pass
    for index, row in merged_df.iterrows():
        if row['GRADE_LEVEL'] == 'K' and row['TEAM'] == 'TK':
            merged_df.at[index, 'GRADE_LEVEL'] = 'TK'
        else:
            # If the value is anything else, leave it as it is
            pass
    return merged_df


def SWUN_transform_data():
    file_location = r'C:\Users\salasrodriguez.j\OneDrive - Modesto City Schools\Desktop\Combo Class Report'
    file_name = 'BBSwun.csv'
    save_name = 'SWUN QA file.csv'
    complete_filepath = file_location + "\\" + file_name
    save_filepath = file_location + "\\" + save_name
    df = pd.read_csv(complete_filepath)
    df['SWUN Score'] = ''
    df['Score Meaning'] = ''
    # iterate through each row
    for index, row in df.iterrows():
        # iterate through columns 3-10
        for col in df.columns[2:11]:
            # check if there is a value in the column
            if pd.notnull(row[col]):
                # set the value to a different column in the same row
                df.at[index, 'SWUN Score'] = row[col]
                # break out of the inner loop if a value has been set
                break
    df['SWUN Score'] = df['SWUN Score'].replace('', np.nan).fillna(0).astype('Int64')
    for index, row in df.iterrows():
        if 0 <= row['SWUN Score'] <= 48:
            df.at[index, 'Score Meaning'] = 'Not Met'
        elif 49 <= row['SWUN Score'] <= 61:
            df.at[index, 'Score Meaning'] = 'Nearly Meets'
        elif 62 <= row['SWUN Score'] <= 80:
            df.at[index, 'Score Meaning'] = 'Meets'
        elif row['SWUN Score'] >= 81:
            df.at[index, 'Score Meaning'] = 'Exceeds'
    df.to_csv(save_filepath, index=False)
    df = df.drop(df.iloc[:, 2:10], axis=1)
    return df


def SWUN_DIBELS_Merge(df1, df2):
    df1 = df1
    df2 = df2
    merged_df = pd.merge(df1, df2, on='Student Id', how='inner')
    merged_df = merged_df.drop(
        columns=['LAST_NAME', 'FIRST_NAME', 'TEAM', 'COURSE1', 'COURSE2', 'YEAR'],
        axis=1)
    return merged_df


def main():
    # Change these parameters if you want to look at a different server
    parameters = ("DRIVER={SQL Server};"
                  "SERVER=reno-sqlis;"
                  "DATABASE=AttunityHS;"
                  "Trusted_Connection=yes")
    connx = pyodbc.connect(parameters)
    cursor = connx.cursor()
    #
    file_location = r'C:\Users\salasrodriguez.j\OneDrive - Modesto City Schools\Desktop\Combo Class Report'
    file_name = 'BBDibels.csv'
    save_file = 'Combo Class Data.csv'
    complete_filepath = file_location + "\\" + file_name
    save_filepath = file_location + "\\" + save_file
    bbReport = pd.read_csv(complete_filepath, encoding='unicode_escape')
    query = pd.read_sql_query(SQL_query(), connx)
    merged_df = DIBELS_merge_data(bbReport, query)
    transformed_df = DIBELS_transform_data(merged_df)
    SWUN_data = SWUN_transform_data()
    Combo_Report = SWUN_DIBELS_Merge(transformed_df, SWUN_data)
    Combo_Report.to_csv(save_filepath, index=False)


main()
