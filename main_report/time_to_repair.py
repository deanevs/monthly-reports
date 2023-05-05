import matplotlib.pyplot as plt
import pandas as pd

import settings
import helper


def do_time_to_repair(mth, keys, corr, dest_filename):
    print("Doing Time-to-Repair ..... ")
    filename = helper.set_filename('TIME_TO_REPAIR_PENALTY')
    title = 'TIME TO REPAIR PENALTIES'
    df_penalties = calc_time_to_repair(mth, keys, corr, title, filename)

    with pd.ExcelWriter(dest_filename, mode="a", engine='openpyxl') as writer:
        sheetname = 'Time-to-Repair'
        df_penalties.to_excel(writer, sheet_name=sheetname, index=False)
        print(f"Saved data to sheet {sheetname}")


def calc_time_to_repair(mth, keys, corr, title, out_filename):
    current_mth = mth.loc[mth.collected == keys[0]]
    year = keys[0].year
    month = keys[0].month
    alpha_month = keys[0].strftime("%B")

    corr_mth = corr[corr['month_end_corr'] == keys[0]].copy()
    corr_mth.Penalty = corr_mth.PENALTY.astype(int)

    # corr_mth.to_excel("corr_mth.xlsx")

    df_penalties = corr_mth[corr_mth['PENALTY'] > 0]
    # df_penalties.to_excel("df_penalties.xlsx")

    penalty_sum = df_penalties.PENALTY.sum()

    print(f"Total penalties = £{penalty_sum}")

    df_penalties.PENALTY.value_counts().plot(kind='bar', figsize=(12, 8), title=title, ylabel='£', fontsize=16)

    plt.savefig((settings.output / out_filename))

    if settings.show_chart:
        plt.show()

    plt.close()

    return df_penalties
