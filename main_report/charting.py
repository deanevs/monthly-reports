import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
from matplotlib import pyplot as plt

import settings
import helper

# list to store return dictionary from pm calcs

def report_columns(data):
    """Report formatter"""
    df = data[data.status_std == 'OUT OF DATE'].sort_values(['next_pm', 'last_pm', 'install'], ascending=True)
    df = df.drop(columns=['collected', 'n_imma', 'contrac', 'month_end', 'origin', 'name', 'serial', 'price',
                          'warranty', 'replacement', 'eol', 'last_wo', 'last_corr', 'retired', 'retire_reason',
                          'received', 'po'])

    df = df.loc[:, ['asset_id', 'equip', 'gmdn_no', 'gmdn', 'manufacturer', 'model',
                       'site','md', 'division','install', 'tech_dept','contract', 'risk',
                       'last_pm', 'next_pm', 'status_std']]

    df = df.rename(columns={'asset_id':'Assetplus ID', 'equip':'Equipment No.', 'gmdn_no':'GMDN', 'gmdn':'Name',
                       'manufacturer':'Manufacturer', 'model':'Model', 'site':'Site','md':'Med Dept',
                       'division':'Division','install':'Install Date', 'tech_dept':'Tech Dept',
                       'contract':'Contract', 'risk':'Risk', 'last_pm':'Last PM', 'next_pm':'Next PM',
                       'status_std':'Status'})
    return df

def do_pm_compliance(merged, keys, dest_filename):
    """
    Called from main program and does all the charting
    :param merged:
    :param keys:
    :param dest_filename:
    :return:
    """

    pm_results = []

    with pd.ExcelWriter(dest_filename, mode="a", engine='openpyxl') as writer:  #

        # create pm charts
        data = merged[(merged.contract.isin(config.GE_CONTRACTS))]          # contract
        filename = helper.set_filename('PM_COMPLIANCE_GE_CONTRACTS')
        title =  'GE CONTRACTS'
        result = calc_single_chart(data, keys, title, filename)
        pm_results.append(result)
        lates = report_columns(data)
        lates.to_excel(writer, sheet_name=title, index=False)

        data = merged[(merged.contract.isin(config.TRUST_CONTRACTS))]       # contract
        filename = helper.set_filename('PM_COMPLIANCE_TRUST_CONTRACTS')
        title = 'TRUST CONTRACTS'
        result = calc_single_chart(data, keys, title, filename)
        pm_results.append(result)
        lates = report_columns(data)
        lates.to_excel(writer, sheet_name=title, index=False)

        data = merged
        filename = helper.set_filename('PM_COMPLIANCE_ALL_ASSETS')
        title = 'ALL ASSETS'
        result = calc_single_chart(data, keys, title, filename)
        pm_results.append(result)
        lates = report_columns(data)
        lates.to_excel(writer, sheet_name=title, index=False)

        data = merged[(merged.tech_dept.isin(config.IMAGING))]
        filename = helper.set_filename('PM_COMPLIANCE_GE_IMAGING')
        title = 'GE IMAGING'
        result = calc_single_chart(data, keys, title, filename)
        pm_results.append(result)
        lates = report_columns(data)
        lates.to_excel(writer, sheet_name=title, index=False)

        data = merged[(merged.tech_dept.isin(config.BIOMED))]
        filename = helper.set_filename('PM_COMPLIANCE_GE_BIOMED')
        title = 'GE BIOMED'
        result = calc_single_chart(data, keys, title, filename)
        pm_results.append(result)
        lates = report_columns(data)
        lates.to_excel(writer, sheet_name=title, index=False)

        data = merged[(merged.tech_dept.isin(config.GE_OTHER))]
        filename = helper.set_filename('PM_COMPLIANCE_GE_OTHER')
        title = 'GE OTHER'
        result = calc_single_chart(data, keys, title, filename)
        pm_results.append(result)
        lates = report_columns(data)
        lates.to_excel(writer, sheet_name=title, index=False)

        data = merged[(merged.tech_dept.isin(config.CLINICAL_ENG))]
        filename = helper.set_filename('PM_COMPLIANCE_CLINICAL_ENG')
        title = 'CLINICAL ENG'
        result = calc_single_chart(data, keys, title, filename)
        pm_results.append(result)
        lates = report_columns(data)
        lates.to_excel(writer, sheet_name=title, index=False)

        data = merged[(merged.tech_dept.isin(config.TRUST))]
        filename = helper.set_filename('PM_COMPLIANCE_TRUST')
        title = 'TRUST'
        result = calc_single_chart(data, keys, title, filename)
        pm_results.append(result)
        lates = report_columns(data)
        lates.to_excel(writer, sheet_name=title, index=False)

        data = merged[(merged.tech_dept.isin(config.TBC))]
        filename = helper.set_filename('PM_COMPLIANCE_TECH_DEPT_TBC')
        title = 'TECH DEPT TBC'
        result = calc_single_chart(data, keys, title, filename)
        pm_results.append(result)
        lates = report_columns(data)
        lates.to_excel(writer, sheet_name=title, index=False)

        data = merged[(merged.tech_dept.isin(config.ON_DEMAND_PAYG))]
        filename = helper.set_filename('PM_COMPLIANCE_ON_DEMAND_PAYG')
        title = 'ON DEMAND PAYG'
        result = calc_single_chart(data, keys, title, filename)
        pm_results.append(result)
        lates = report_columns(data)
        lates.to_excel(writer, sheet_name=title, index=False)

        # now do DIVISIONS
        filename = helper.set_filename('PM_COMPLIANCE_DIVISIONS')
        result = calc_division(merged, keys, 'DIVISIONS', filename)
        pm_results = pm_results + result

        df_results = pd.DataFrame(pm_results)

        df_results.to_excel(writer, sheet_name='PM Compliance Summary', index=False)
        print(df_results)

# ************************************************************************************************************
# PM COMPLIANCE TRENDS
# ************************************************************************************************************

def do_pm_trends(merged):

        # GE TECH DEPTS
        GE_TECH_DEPTS = config.IMAGING + config.BIOMED

        filters = {  # 'ALL RISKS':merged_all.tech_dept.isin(GE_TECH_DEPTS),
            'HIGH': (merged.tech_dept.isin(GE_TECH_DEPTS)) & (merged.risk == 'HIGH'),
            'MEDIUM': (merged.tech_dept.isin(GE_TECH_DEPTS)) & (merged.risk == 'MEDIUM'),
            'LOW': (merged.tech_dept.isin(GE_TECH_DEPTS)) & (merged.risk == 'LOW')
        }
        title = "GE HEALTHCARE MMS - PM COMPLIANCE TRENDS"
        filename = helper.set_filename('PM_TREND_GE_IMAGING_BIOMED')

        calc_trend(merged, filters, title, filename)

        # TRUST TECH DEPTS
        filters = {  # 'ALL RISKS':merged_all.tech_dept.isin(GE_TECH_DEPTS),
            'HIGH': (merged.tech_dept.isin(config.TRUST)) & (merged.risk == 'HIGH'),
            'MEDIUM': (merged.tech_dept.isin(config.TRUST)) & (merged.risk == 'MEDIUM'),
            'LOW': (merged.tech_dept.isin(config.TRUST)) & (merged.risk == 'LOW')
        }
        title = "TRUST - PM COMPLIANCE TRENDS"
        filename = helper.set_filename('PM_TREND_TRUST')

        calc_trend(merged, filters, title, filename)

        # ALL IMPERIAL ASSETS
        filters = {  # 'ALL RISKS':'',
            'HIGH': merged.risk == 'HIGH',
            'MEDIUM': merged.risk == 'MEDIUM',
            'LOW': merged.risk == 'LOW'
        }
        title = "ALL IMPERIAL ASSETS - PM COMPLIANCE TRENDS"
        filename = helper.set_filename('PM_TREND_ALL_IMPERIAL')

        calc_trend(merged, filters, title, filename)

        # NO RETURN


def do_chart(df_prop, df):
    """
    This is used for each report going forward.  Added the ability to decide on rounding
    """
    for n, x in enumerate([*df.index.values]):
        for (proportion, count, y_loc) in zip(df_prop.loc[x], df.loc[x], df_prop.loc[x].cumsum()):
            try:
                if config.use_round:
                    proportion_calc = f'{count}\n({np.round(proportion * 100, 1)}%)'
                else:
                    proportion_calc = f'{count}\n{int(np.round(proportion * 100, 0))}%'

                plt.text(x= (y_loc - proportion) + (proportion / 2),
                         y= n - 0.11,
                         s= proportion_calc,
                         color= "black",
                         fontsize= 12,
                         fontweight= "bold")
            except:
                print("ERROR")
                pass
    # NO RETURN

def calc_single_chart(data, keys, title, out_filename):
    print(f"Number of assets = {len(data)}")

    cross_tab_prop = pd.crosstab(index=data['risk'],
                                 columns=data['status_std'],
                                 normalize="index").reindex(config.risk_order)

    cross_tab = pd.crosstab(index=data['risk'],
                            columns=data['status_std']).reindex(config.risk_order)

    cross_tab_prop.plot(kind='barh',
                        stacked=True,
                        color=['c', 'orange'],
                        figsize=(10, 6))

    do_chart(cross_tab_prop, cross_tab)

    plt.ylabel("Risks")
    plt.xlabel("Percentage Compliance")
    # plt.set_title(title)
    plt.title(title)
    plt.legend(loc="lower left", ncol=2)

    plt.savefig((config.output / out_filename))
    print(f"Saved {out_filename}")

    if config.show_chart:
        plt.show()

    plt.close()

    # do monthly stats
    dic_tech_dept_results = {}
    dic_tech_dept_results.update({'month': keys[0].date(),
                  'Group': title,
                  '#assets': len(data),
                  'HIGH': cross_tab_prop.loc['HIGH', 'IN DATE'],
                  'MEDIUM': cross_tab_prop.loc['MEDIUM', 'IN DATE'],
                  'LOW': cross_tab_prop.loc['LOW', 'IN DATE']})

    return dic_tech_dept_results


def calc_division(data, keys, title, out_filename):

    plt.figure(figsize=(25, 25))
    plt.subplots_adjust(hspace=0.2)
    plt.suptitle(title, fontsize=12, y=0.95)

    # set number of columns (use 3 to demonstrate the change)
    ncols = 3
    # calculate number of rows
    nrows = len(config.DIVISIONS) // ncols + (len(config.DIVISIONS) % ncols > 0)

    temp_results_list = []

    # loop through the length of tickers and keep track of index
    for n, div in enumerate(config.DIVISIONS):
        # add a new subplot iteratively using nrows and cols
        ax = plt.subplot(nrows, ncols, n + 1)

        # filter df and plot ticker on the new subplot axis
        df = data[data.division.str.contains(div, na=False, regex=False)]
        print(f"{div} has {len(df)} assets")

        cross_tab_prop = pd.crosstab(index=df['risk'],
                                     columns=df['status_std'],
                                     normalize="index").reindex(config.risk_order)

        cross_tab = pd.crosstab(index=df['risk'],
                                columns=df['status_std']).reindex(config.risk_order)

        cross_tab_prop.plot(kind='barh',
                            ax=ax,
                            stacked=True,
                            # colormap='tab10',
                            color=['c', 'orange'],
                            figsize=(25, 18))

        do_chart(cross_tab_prop, cross_tab)

        # chart formatting
        ax.set_title(div.upper())
        ax.get_legend().remove()
        ax.set_xlabel("")

        # do monthly stats
        dict_temp = {}
        dict_temp.update({'month': keys[0].date(),
                      'Group': div,
                      '#assets': len(df),
                      'HIGH': cross_tab_prop.loc['HIGH', 'IN DATE'],
                      'MEDIUM': cross_tab_prop.loc['MEDIUM', 'IN DATE'],
                      'LOW': cross_tab_prop.loc['LOW', 'IN DATE']})

        temp_results_list.append(dict_temp)

    plt.savefig((config.output / out_filename))
    print(f"Saved {out_filename}")
    if config.show_chart:
        plt.show()
    plt.clf()
    plt.close()
    return temp_results_list


def calc_trend(data, filters, title, out_filename):
    # create an empty dataframe
    df_concat = pd.DataFrame()

    for risk, filter in filters.items():
        df = data[filter]

        df_xtab = pd.crosstab(index=df.collected, columns=df.status_std, normalize="index")
        df_xtab.drop(columns=['OUT OF DATE'], inplace=True)
        df_xtab.rename(columns={'IN DATE': risk}, inplace=True)

        df_concat = pd.concat([df_concat, df_xtab], axis=1)

    print(title)
    print(df_concat)
    print('\n')

    df_concat.plot(kind='line',
                   stacked=False,
                   figsize=(18, 12),
                   linewidth=3.0,
                   color=['r', 'orange', 'b'])

    plt.xlabel("Month End")
    plt.ylabel("Proportion (%)")
    plt.title(title)
    plt.legend(loc="lower left", ncol=2)

    plt.savefig((config.output / out_filename))

    if config.show_chart:
        plt.show()

    plt.clf()
    plt.close()
"""
def my_plotter(ax, data1, data2, param_dict):

   # A helper function to make a graph.

    out = ax.plot(data1, data2, **param_dict)
    return out

data1, data2, data3, data4 = np.random.randn(4, 100)  # make 4 random data sets
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10,5))
my_plotter(ax1, data1, data2, {'marker': 'x'})
my_plotter(ax2, data3, data4, {'marker': 'o'});
"""