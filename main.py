import urllib
import pandas as pd
import sqlalchemy as sal
from SQL_Queries import *
import os


def sql_connection(parameters):
    # this creates the connection to the SQL Server do not change
    params = parameters
    engine = sal.create_engine("mssql+pyodbc:///?odbc_connect={}".format(params))
    return engine


def main():
    file_location = r'C:\Users\salasrodriguez.j\OneDrive - Modesto City Schools\Desktop\DF Report'
    print('Deleting old files')
    for f in os.listdir(file_location):
        os.remove(os.path.join(file_location, f))
    parameters = urllib.parse.quote_plus("DRIVER={SQL Server};"
                                         "SERVER=reno-sqlis;"
                                         "DATABASE=AttunityHS;"
                                         "Trusted_Connection=yes")

    connx = sql_connection(parameters)

    print('Starting Query!')
    school = pd.read_sql(query_byschool(), connx)
    district = pd.read_sql(query_district(), connx)
    school_rate = pd.read_sql(query_StudentRateSchool(), connx)
    district_rate = pd.read_sql(query_StudentRateDisct(), connx)

    print('Query is complete!')

    school.to_csv(os.path.join(file_location, 'school.csv'), index=False)
    district.to_csv(os.path.join(file_location, 'district.csv'), index=False)
    district_rate.to_csv(os.path.join(file_location, 'district_rate.csv'), index=False)
    school_rate.to_csv(os.path.join(file_location, 'school_rate.csv'), index=False)
    print('Files Generated!')

main()
