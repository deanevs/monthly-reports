import pandas as pd
from pathlib import Path

pd.options.display.max_columns = None
pd.options.display.max_rows = None  # displays all rows ... change None to 100 ow whatever number
pd.options.display.width = 1000

# controls

do_excel = True

wdire = Path(r'C:\Users\212628255\Documents\2 GE\AssetPlus\Monthly Reports\new downloads')
output = Path(r'C:\Users\212628255\Documents\2 GE\AssetPlus\Monthly Reports\Contract Changes')
assets = pd.read_csv((wdire / 'INFOASSETSRETIREDAFTER2015.csv'))  # , parse_dates=True)
mth = pd.read_csv((wdire / 'monthly_pm_status.csv'))  # ,parse_dates=True)

mth.collected = pd.to_datetime(mth.collected)
grp = mth.groupby('collected')
keys = list(grp.groups.keys())
keys.sort(reverse=True)

# how many months to display from most recent
NUM_MONTHS = 1

# stores dict values from each month to create dataframe
rows_list = []


def column_widths(df, sheet_name, writer):
    for column in df:
        column_width = max(df[column].astype(str).map(len).max(), len(column))
        col_idx = df.columns.get_loc(column)
        writer.sheets[sheet_name].set_column(col_idx, col_idx, column_width + 8)


assets = assets[['asset_id', 'equip', 'gmdn_no', 'name', 'manufacturer', 'model', 'install', 'tech_dept', 'contract']]

# iterate through each month
for x in range(len(keys) - 1):
    if x < NUM_MONTHS:
        # set up excel writer
        writer = pd.ExcelWriter((output / f'contract_changes_{keys[x].date()}.xlsx'), engine='xlsxwriter')

        # set up month and last_month dfs
        df_last = mth.loc[mth.collected == keys[x]]
        df_lastlast = mth.loc[mth.collected == keys[x + 1]]

        # outer join allows detection of new and retired assets
        outer = pd.merge(df_last, df_lastlast, how='outer', on='n_imma')
        # inner join allows detection of changes from month to month
        inner = pd.merge(df_last, df_lastlast, how='inner', on='n_imma')
        # get active fields for both months

        # do month to month changes for existing assets
        inner = inner.fillna('-------')  # needed because next statement since NaN != NaN

        delta_contract = inner[inner.apply(lambda x: x['contrac_x'] != x['contrac_y'], axis=1)]
        delta_contract = delta_contract.drop(
            columns=['tech_dept_y', 'status_std_y', 'status_cnl_y', 'tech_dept_x', 'status_std_x',
                     'status_cnl_x', 'collected_x', 'collected_y'])

        delta_contract = pd.merge(delta_contract, assets, how='left', left_on='n_imma', right_on='asset_id')

        delta_contract = delta_contract.drop(columns=['n_imma', 'contract'])

        delta_contract.reset_index(drop=True, inplace=True)

        # arrange order of columns
        delta_contract = delta_contract[['asset_id',
                                         'equip',
                                         'gmdn_no',
                                         'name',
                                         'manufacturer',
                                         'model',
                                         'install',
                                         'tech_dept',
                                         'contrac_y',
                                         'contrac_x']]

        # rename column headers
        delta_contract = delta_contract.rename(columns={'contrac_y': f'CONTRACT_{keys[x + 1].date()}',
                                                        'contrac_x': f'CONTRACT_{keys[x].date()}'
                                                        })
        sort_col = 'CONTRACT_' + str(keys[x].date())
        delta_contract.sort_values(sort_col, inplace=True)

        print("**************************************************************************************************")
        print(f"CHANGES OF CONTRACTS FOR EXISTING ASSETS {keys[x].date()}")
        print("**************************************************************************************************")
        print(delta_contract)
        if do_excel:
            delta_contract.to_excel(writer, sheet_name='delta', index=False)
            column_widths(delta_contract, 'delta', writer)

        # *********************************** ADDED **************************************
        # create separate dataframes for added and retired
        added = outer[outer.collected_y.isna()]

        added_contract = added[added.contrac_x.notna()]

        added_contract = pd.merge(added_contract, assets, how='left', left_on='n_imma', right_on='asset_id')
        added_contract = added_contract.drop(columns=['collected_y', 'collected_x', 'n_imma', 'tech_dept_y',
                                                      'contrac_y', 'status_std_y', 'status_cnl_y', 'tech_dept_x',
                                                      'contrac_x', 'status_std_x', 'status_cnl_x'])

        added_contract.sort_values('contract', inplace=True)

        print("**************************************************************************************************")
        print(f" NEWLY ADDED ASSETS ADDED TO CONTRACT {keys[x].date()}")
        print("**************************************************************************************************")
        print(added_contract)
        if do_excel:
            added_contract.to_excel(writer, sheet_name='added', index=False)
            column_widths(added_contract, 'added', writer)

        # *********************************** RETIRED **************************************
        retired = outer[outer.collected_x.isna()]
        # print(f"stage 1 {len(retired)}")
        retired_contract = retired[retired.contrac_y.notna()]
        # print(f"stage 2 {len(retired_contract)}")
        retired_contract = pd.merge(retired_contract, assets, how='left',
                                    left_on='n_imma', right_on='asset_id')
        retired_contract.drop(
            columns=['collected_x', 'collected_y', 'n_imma', 'tech_dept_y', 'contrac_y', 'status_std_y', 'status_cnl_y',
                     'tech_dept_x', 'contrac_x', 'status_std_x', 'status_cnl_x'], inplace=True)

        retired_contract.sort_values('contract', inplace=True)

        print("**************************************************************************************************")
        print(f"RETIRED ASSETS REMOVED FROM CONTRACT {keys[x].date()}")
        print("**************************************************************************************************")
        print(retired_contract)
        if do_excel:
            retired_contract.to_excel(writer, sheet_name='retired', index=False)
            column_widths(retired_contract, 'retired', writer)

        writer.save()

        print(
            "\n****************************************************************************************************************************************************************************************************\n")
