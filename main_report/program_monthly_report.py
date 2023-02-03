import pandas as pd
import datetime
from pandas.tseries.offsets import MonthEnd
from interface import ss_interface

import config_secret
import config
import charting
import availability
import time_to_repair
import acceptance
import overviews

pd.options.display.max_columns = None
pd.options.display.max_rows = None  # displays all rows ... change None to 100 ow whatever number
pd.options.display.width = 1000

connect_ss = False


def main():
    # load dataframes
    if config.do_availability or config.do_time_to_repair or 1:
        print('Loading correctives ...')
        if connect_ss:
            corr22 = ss_interface.Sheet(config_secret.smartsheet_token, config.CORRECTIVE2022).get_df()
            corr22['WO Number'] = corr22['WO Number'].astype(int)
            corr23 = ss_interface.Sheet(config_secret.smartsheet_token, config.CORRECTIVE2023).get_df()
            corr23['WO Number'] = corr23['WO Number'].astype(int)
            corr = pd.concat([corr22, corr23])
            corr.to_excel((config.wdir / 'correctives.xlsx'), index=False)
            del corr22, corr23
        else:
            corr = pd.read_excel((config.wdir / 'correctives.xlsx'))

        print(corr.head())

        def clean_asset_id(a):
            """Ensures all are strings """
            if isinstance(a, float):
                result = str(int(a))
                # print(f"float: {a, result}")
                return result
            elif isinstance(a, int):
                return str(a)
            elif isinstance(a, str):
                if a[-2] == '.':
                    result = a[:-2]
                    # print(f"String: {a, result}")
                    return result
                else:
                    return a
            else:
                print(f"MISSED ALL is {type(a)}")

        # clean up df
        corr['month_end_corr'] = pd.to_datetime(corr['Job End Date']) + MonthEnd(
            1)  # converts to last day of month eg 2022-10-31
        corr['WO Number'] = corr['WO Number'].fillna(0)
        corr['WO Number'] = corr['WO Number'].astype(int)
        corr['Asset ID'] = corr['Asset ID'].apply(clean_asset_id)
        corr['Analyzed Date'] = pd.to_datetime(corr['Analyzed Date'])

        corr.drop(columns=['row_id', 'parent_id', 'Description', 'Site', 'Tech Dept (Now)', 'Risk',
                           'Technical Comments', 'Reporting Error', 'Verify'],
                  inplace=True)

        print(f"Shape = {corr.shape}")
        print(corr.head(20))
        print('\n')

    # main assets
    print('Loading assets i.e. how they are now! ....')
    assets = pd.read_csv((config.wdir / 'INFOASSETSRETIREDAFTER2015.csv'))
    assets = assets.fillna('')
    assets.risk = assets.risk.apply(convert_risk)
    assets.asset_id = assets.asset_id.astype(str)

    # next pm tidy up from mix of NaN and 20210511.0
    def pm_date_convert(s):
        if isinstance(s, float):
            s = str(s)
            return s[:4] + '-' + s[4:6] + '-' + s[6:8]

    assets.next_pm = assets.next_pm.apply(pm_date_convert)

    print(f"Shape = {assets.shape}")
    print(assets.head())
    print('\n')

    # monthly data grab
    print("Loading monthly-pm-status ...")
    mth = pd.read_csv((config.wdir / 'monthly_pm_status.csv'))
    mth = mth[mth.tech_dept != 'ASSET ONLY'].copy()  # this stopped from Nov22
    mth['month_end'] = pd.to_datetime(mth.collected) + MonthEnd(0)
    mth.drop(columns=['status_cnl', 'tech_dept'], inplace=True)

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

    print(f"Shape = {last_mth.shape}")
    print(last_mth.head())
    print('\n')

    # create the main output excel file
    dest_filename = config.output / (
                datetime.datetime.today().date().strftime("%Y-%m-%d") + ' - Monthly Report Data.xlsx')
    last_mth.to_excel(dest_filename, index=False, header=True, engine='xlsxwriter', sheet_name='All Data')

    print(f"Saved last_mth to {dest_filename}")

    if config.do_overviews:
        result = overviews.do_overviews(assets, mth, keys)
        print(result)

    if config.do_pm_charts:
        charting.do_pm_compliance(last_mth, keys, dest_filename)

    if config.do_pm_trends:
        charting.do_pm_trends(merged)

    if config.do_availability:
        availability.do_availability(merged, keys, corr, dest_filename)

    if config.do_time_to_repair:
        time_to_repair.do_time_to_repair(mth, keys, corr, dest_filename)

    if config.do_acceptance:
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
