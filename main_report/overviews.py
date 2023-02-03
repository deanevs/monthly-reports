import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import config
import helper


def do_overviews(assets, mth, keys):

    # create a dataframe for plotting trends
    df_stats = create_df(assets, mth, keys)

    filename = helper.set_filename("OVERVIEW_TREND_TOTAL_ACTIVE_ASSETS")
    title = 'TOTAL ACTIVE ASSETS PER MONTH'
    legend = 'Total Active Assets'
    create_trend(df_stats[['total_num']], title, legend, filename)

    filename = helper.set_filename("OVERVIEW_TREND_ADDED-RETIRED")
    title = 'ADDED/RETIRED ASSETS PER MONTH'
    legend = ['Added', 'Retired']
    create_hist(df_stats[['added_num', 'retired_num']], title, legend, filename)

    filename = helper.set_filename("OVERVIEW_TREND_TOTAL_COST_ALL_ASSETS")
    title = 'TOTAL COST OF ASSETS PER MONTH'
    legend = 'Total Cost of Assets'
    create_trend(df_stats[['total_cost']], title, legend, filename)

    filename = helper.set_filename("OVERVIEW_TREND_MEAN_RETIREMENT_AGE")
    title = 'MEAN RETIREMENT AGE PER MONTH'
    legend = 'Mean Retirement Age'
    create_trend(df_stats[['retired_age_mean']], title, legend, filename)

    return 'Done Overview'


def create_df(df_assets, mth, keys):
    # stores dict values from each month to create dataframe
    rows_list = []

    # iterate through each month
    for x in range(len(keys) - 1):
        # set up month and last_month dfs
        df_last = mth.loc[mth.collected == keys[x]]
        df_lastlast = mth.loc[mth.collected == keys[x + 1]]

        active = pd.merge(df_last, df_assets, how='left', left_on='n_imma', right_on='asset_id')

        # merge both months
        merged_outer = pd.merge(df_last, df_lastlast, how='outer', on='n_imma')
        # merged_inner = pd.merge(df_last, df_lastlast, how='inner', on='n_imma')

        # create separate dataframes for added and retired
        added = merged_outer[merged_outer['collected_y'].isna()]
        retired = merged_outer[merged_outer['collected_x'].isna()]

        # merge with all asset columns
        added = pd.merge(added, df_assets, how='left', left_on='n_imma', right_on='asset_id')
        retired = pd.merge(retired, df_assets, how='left', left_on='n_imma', right_on='asset_id')

        # calculate age of retired assets
        retired[['install', 'retired']] = retired[['install', 'retired']].apply(pd.to_datetime)
        retired['AGE'] = (retired.retired - retired.install).dt.days / 365
        retired.AGE = retired.AGE.round()

        # do monthly stats
        dict1 = {}
        dict1.update({'month-year': keys[x].date(), 'added_num': len(added), 'retired_num': len(retired),
                      'total_num': len(df_last), 'total_cost': round(active.price.sum()),
                      'retired_age_mean': round(retired.AGE.mean()), 'added_cost': round(added.price.sum()),
                      'retired_cost': round(retired.price.sum())})
        rows_list.append(dict1)

    stats = pd.DataFrame(rows_list)
    stats.set_index('month-year', inplace=True)

    return stats

def create_hist(data, title, legend, out_filename):
    data.plot.bar(figsize=(20,12))

    plt.legend = legend
    plt.title = title

    plt.savefig((config.output / out_filename))
    print(f"Saved {out_filename}")

    if config.show_chart:
        plt.show()

    plt.cla()
    plt.clf()
    plt.close()

def create_trend(data, title, legend, out_filename):
    fig, ax = plt.subplots(figsize=(20, 12))

    ax.plot(data,
            linewidth=4.0,
            label=legend)

    ax.set(xlabel='Year-Month',
           ylabel='No. Assets',
           title=title)

    # ax.grid()
    ax.grid(visible=True,
            color='grey',
            linestyle='-.',
            linewidth=0.5,
            alpha=0.8)

    ax.legend()

    fig.savefig((config.output / out_filename))
    print(f"Saved {out_filename}")

    if config.show_chart:
        plt.show()

    plt.cla()
    plt.clf()
    plt.close()