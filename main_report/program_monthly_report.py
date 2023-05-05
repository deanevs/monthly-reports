import pandas as pd
import datetime
from pandas.tseries.offsets import MonthEnd
import sys
import settings
import charting
import availability
import time_to_repair
import acceptance
import overviews

pd.options.display.max_columns = None
pd.options.display.max_rows = None  # displays all rows ... change None to 100 ow whatever number
pd.options.display.width = 1000


def main():
    # load dataframes
    print('Loading correctives ...')
    corr = pd.read_csv((settings.wdir / 'correctives.csv'))
    corr = corr.fillna('')
    # add column for last of month for date end month
    corr['month_end_corr'] = pd.to_datetime(corr.DA_FIN, dayfirst=True) + MonthEnd(1)

    print(f"Correctives shape = {corr.shape}")
    print(corr.head(20))
    print('\n')

    # main assets
    print('Loading assets i.e. how they are now! ....')
    assets = pd.read_csv((settings.wdir / 'infoassetsretiredafter2015.csv'))
    # format next pm date from 20230315.0
    assets.next_pm = pd.to_datetime(assets.next_pm, errors='ignore', format="%Y%m%d")

    assets = assets.fillna('')
    assets.risk = assets.risk.apply(convert_risk)

    print(f"Shape = {assets.shape}")
    print(assets.head())
    print('\n')

    # monthly data grab
    print("Loading monthly-pm-status ...")
    mth = pd.read_csv((settings.wdir / 'monthly_pm_status.csv'))
    mth = mth[mth.tech_dept != 'ASSET ONLY'].copy()  # this stopped from Nov22
    mth['month_end'] = pd.to_datetime(mth.collected) + MonthEnd(0)
    mth.drop(columns=['tech_dept'], inplace=True)

    print(f"Shape = {mth.shape}")
    print(mth.head())
    print('\n')

    # make keys
    print('Making keys for filtering months ...')
    mth.collected = pd.to_datetime(mth.collected)
    grp = mth.groupby('collected')
    keys = list(grp.groups.keys())
    keys.sort(reverse=True)

    print([k for k in keys])
    print('\n')

    # merge last month i.e. active assets with assets for all descriptions columns
    print('Merge mth, assets to create merged ...')
    merged = pd.merge(mth, assets, how='left', left_on='n_imma', right_on='asset_id')

    print(f"Shape = {merged.shape}")
    print(merged.head())
    print('\n')

    # these are used to make a dataframe for comparison with this and last month
    print('last_mth ...')
    last_mth = merged.loc[merged.collected == keys[0]]
    last_mth.drop(columns=[])

    print(f"Last month shape = {last_mth.shape}")
    print(last_mth.head())
    print('\n')

    # create the main output excel file
    dest_filename = settings.output / (
            datetime.datetime.today().date().strftime("%Y-%m-%d") + ' - Monthly Report Data.xlsx')
    last_mth.to_excel(dest_filename, index=False, header=True, engine='xlsxwriter', sheet_name='All Data')

    print(f"Saved last_mth to {dest_filename}")

    if settings.do_overviews:
        result = overviews.do_overviews(assets, mth, keys)
        print(result)

    if settings.do_pm_charts:
        charting.do_pm_compliance(last_mth, keys, dest_filename)

    if settings.do_pm_trends:
        charting.do_pm_trends(merged)

    if settings.do_availability:
        availability.do_availability(merged, keys, corr, dest_filename)

    if settings.do_time_to_repair:
        time_to_repair.do_time_to_repair(mth, keys, corr, dest_filename)

    if settings.do_acceptance:
        acceptance.do_acceptance(assets, dest_filename)


# ***************************************************************************************************************


def convert_risk(r):
    if r == 1:
        return 'HIGH'
    elif r == 2:
        return 'MEDIUM'
    elif r == 3:
        return 'LOW'
    else:
        return r


def max_col_widths(df, writer, sheetname):
    for column in df:
        column_length = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets[sheetname].set_column(col_idx, col_idx, column_length)
    return writer


def col_widths(df, worksheet):
    for idx, col in enumerate(df):  # loop through all columns
        series = df[col]
        max_len = max((
            series.astype(str).map(len).max(),  # len of largest item
            len(str(series.name))  # len of column name/header
        )) + 1  # adding a little extra space
        worksheet.set_column(idx, idx, max_len)  # set column width


if __name__ == '__main__':
    main()
