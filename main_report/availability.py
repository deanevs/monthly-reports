import matplotlib.pyplot as plt

import pandas as pd
import settings
import helper
import sys

sys.path.insert(0, 'C:\\Users\\212628255\\Documents\\PycharmProjects\\interfaces\\WorkDays')
import workdays as wds

HOURS_PER_WORKDAY = 10
MINS_PER_HOUR = 60


def do_availability(merged, keys, corr, dest_filename):
    """Orchestrates the different availability analysis"""
    print("Doing System Availability ..... ")

    MRI = ('MRI', ['37654'])
    XRAY = ('X-Ray', ['37672', '17904', '37646', '37645', '37647', '37679', '37661',
                      '42280', '37623', '37626', '40866', '38400', '37667'])
    CT = ('CT Scanners', ['37618', '45143', '45016'])

    gmdn_list = [CT, MRI, XRAY]
    filename = helper.set_filename('AVAILABILITY_MRI_CT_XRAY')
    stats = _calc_gmdn_availability(gmdn_list, merged, corr, keys, filename)
    print(stats)

    with pd.ExcelWriter(dest_filename, mode="a", engine='openpyxl') as writer:
        sheetname = 'Avail MRI-CT-XRay'
        stats.to_excel(writer, sheet_name=sheetname, index=True)
        print(f"Saved to sheet {sheetname}")

    # *****************************************
    filename = helper.set_filename('AVAILABILITY_GE_IMAGING_BIOMED')
    title = 'KPI SYSTEM AVAILABILITY GE IMAGING & BIOMED - FULLY COMPREHENSIVE ONLY'
    stats = _calc_availability_fully_comp(merged, keys, corr, filename, title)
    print(stats)

    with pd.ExcelWriter(dest_filename, mode="a", engine='openpyxl') as writer:
        sheetname = 'Avail GE Fully Comp'
        stats.to_excel(writer, sheet_name=sheetname, index=True)
        print(f"Saved to sheet {sheetname}")


def _availability_formulae(downtime, asset_cnt, month_days):
    return (1 - (downtime / (asset_cnt * month_days))) * 100


def _calc_gmdn_availability(gmdn_list, merged, corr, keys, out_filename, no_months=12):
    stats_list = []  # empty list to hold dicts results for each month
    wd = wds.Workdays()

    for n in range(len(keys) - 1):
        if n >= no_months:
            break

        year = keys[n].year
        month = keys[n].month
        alpha_month = keys[n].strftime("%b")
        legend = alpha_month + '-' + str(year)

        month_days = int(wd.get_year_month_mins(year, month) / HOURS_PER_WORKDAY / MINS_PER_HOUR)

        merged_mth = merged.loc[merged.collected == keys[n]]
        curr_corr = corr.loc[(corr.month_end_corr == keys[n])]

        dict1 = {}  # empty dictionary to create dataframe

        for gmdn in gmdn_list:
            print('\n')
            pattern = '|'.join(gmdn[1])
            print(f"Category : {gmdn[0]}, GMDN(s): {pattern}")

            df_gmdn = merged_mth[merged_mth.gmdn_no.str.contains(pattern)]

            gmdn_cnt = int(len(df_gmdn))

            df_sd = pd.merge(df_gmdn, curr_corr, how='inner', left_on='n_imma', right_on='Asset ID')
            df_sd.drop(columns=['n_imma', 'status_std', 'month_end', 'md', 'origin', 'name', 'serial', 'price',
                                'replacement', 'tech_dept', 'contract', 'eol', 'last_wo', 'division', 'retired',
                                'retire_reason', 'received', 'po', 'Asset ID', 'Contract'], inplace=True)

            if len(df_sd[df_sd['System Down (Days)'] > 0]) > 0:
                print(df_sd[df_sd['System Down (Days)'] > 0].sort_values('System Down (Days)', ascending=False))

            total_sd = round(df_sd['System Down (Days)'].sum(), 2)
            avail = round(_availability_formulae(total_sd, gmdn_cnt, month_days), 2)
            print(f"{gmdn[0]} Availability = {avail}%")

            dict1.update({'month': legend,
                          'Work days': int(month_days),
                          gmdn[0] + ' Asset Count': gmdn_cnt,
                          gmdn[0] + ' Down (Days)': total_sd,
                          gmdn[0] + ' Avail (%)': avail,
                          })

        stats_list.append(dict1)
        print("*****************************************************")

    # Create a new dataframe from the list of dictionaries
    df_stats = pd.DataFrame(stats_list)
    df_stats.set_index('month', inplace=True)
    df_stats = df_stats.reindex(index=df_stats.index[::-1])     # invert to get latest month on right

    df_stats[['MRI Avail (%)', 'X-Ray Avail (%)', 'CT Scanners Avail (%)']].plot(figsize=(18, 12), linewidth=4.0,
                                                                              fontsize=14, title='SYSTEM AVAILABILITY')
    # set limit lines at 96 and 98%
    plt.axhline(y=96, color='red', linestyle='dashed', linewidth=2.0)
    plt.axhline(y=98, color='orange', linestyle='dashed', linewidth=2.0)

    plt.savefig((settings.output / out_filename))
    print(f'Saved {out_filename}')

    if settings.show_chart:
        plt.show()

    plt.cla()
    plt.clf()
    plt.close()

    return df_stats


def _calc_availability_fully_comp(merged, keys, corr, out_filename, title, no_months=12):
    # stores dict values from each month to create dataframe
    rows_list = []
    wd = wds.Workdays()

    # iterate through each month
    for x in range(len(keys) - 1):
        if x >= no_months:
            break

        # set up month and last_month dfs
        current_mth = merged.loc[merged.collected == keys[x]]

        year = keys[x].year
        month = keys[x].month
        alpha_month = keys[x].strftime("%b")  # Sep, Jul etc
        legend = alpha_month + '-' + str(year)  # Sep-2022

        month_days = int(wd.get_year_month_mins(year, month) / HOURS_PER_WORKDAY / MINS_PER_HOUR)

        # filter on fully comp to get count of assets - using the contract status of the monthly-pm-status
        curr_mon_ge_contract = current_mth[current_mth.contrac.str.contains('MMS FULLY COMP', na=False, regex=False)]

        # holder for tech_dept and asset count
        tech_dept = {}
        for idx, td in enumerate(curr_mon_ge_contract.tech_dept.value_counts().index.tolist()):
            tech_dept[td] = curr_mon_ge_contract.tech_dept.value_counts()[idx]

        # init counters for groups
        imaging_cnt = 0
        biomed_cnt = 0
        for k, v in tech_dept.items():
            if k in settings.IMAGING:
                imaging_cnt += v
            else:
                biomed_cnt += v

        print(f"\nImaging count = {imaging_cnt}")
        print(f"Biomed count = {biomed_cnt}")
        print(f"Imaging + Biomed = {len(curr_mon_ge_contract)}")

        # merge filtered FULLY COMP with correctives
        df_sd = pd.merge(curr_mon_ge_contract, corr, how='inner', left_on='n_imma', right_on='Asset ID')
        print(f"Number in merged corrective = {len(df_sd)}")
        df_sd.drop(columns=['n_imma', 'status_std', 'month_end', 'md', 'origin', 'name', 'serial', 'price',
                            'replacement', 'tech_dept', 'contract', 'eol', 'last_wo', 'division', 'retired',
                            'retire_reason', 'received', 'po', 'Asset ID', 'Contract'], inplace=True)

        imaging = df_sd[(df_sd['Tech Dept (WO)'].isin(settings.IMAGING)) &
                                                 (df_sd.month_end_corr.dt.year == year) &
                                                 (df_sd.month_end_corr.dt.month == month)]

        print(imaging.head())

        img_sd_days = round(imaging['System Down (Days)'].sum(), 2)

        avail_imaging = round(_availability_formulae(img_sd_days, imaging_cnt, month_days), 2)

        # GE BIOMED FULLY COMP
        # bio_sd_days = round(corr[((corr['Tech Dept (Now)'].isin(settings.BIOMED)) &
        #                               (corr['Job End Month'] == legend) &
        #                               corr['Contract'].str.contains('MMS FULLY COMP', na=False, regex=False))][
        #                             'System Down (Days)'].sum(), 2)


        biomed = df_sd[(df_sd['Tech Dept (WO)'].isin(settings.BIOMED)) &
                                                 (df_sd.month_end_corr.dt.year == year) &
                                                 (df_sd.month_end_corr.dt.month == month)]

        print(biomed.head())

        bio_sd_days = round(biomed['System Down (Days)'].sum(), 2)

        avail_biomed = round(_availability_formulae(bio_sd_days, biomed_cnt, month_days), 2)

        # do monthly stats
        temp_dict = {}
        temp_dict.update({'month': legend,
                      'Imaging count': imaging_cnt,
                      'Imaging Sys Down (Days)': img_sd_days,
                      'Imaging Avail %': avail_imaging,
                      'Biomed count': biomed_cnt,
                      'Biomed Sys Down (Days)': bio_sd_days,
                      'Biomed Avail %': avail_biomed
                      })

        rows_list.append(temp_dict)

    stats = pd.DataFrame(rows_list)
    stats.set_index('month', inplace=True)
    stats = stats.reindex(index=stats.index[::-1])  # reverse index to get oldest to latest, left to right

    stats[['Imaging Avail %', 'Biomed Avail %']].plot(figsize=(18, 12), linewidth=4.0, fontsize=14, title=title)

    plt.axhline(y=96, color='red', linestyle='dashed', linewidth=2.0)
    plt.axhline(y=98, color='orange', linestyle='dashed', linewidth=2.0)

    plt.savefig((settings.output / out_filename))
    print(f'Saved {out_filename}')

    if settings.show_chart:
        plt.show()

    plt.cla()
    plt.clf()
    plt.close()

    return stats
