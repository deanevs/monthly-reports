import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import config
import helper


def do_acceptance(assets, dest_filename):
    print('Doing Acceptance KPI ...')
    df_accept = get_accept(assets, )

    # create donut chart
    filename = helper.set_filename('ACCEPTANCE_KPI')
    title = 'KPI ACCEPTANCE'
    calc_acceptance(df_accept, title, filename)

    # create bin chart
    filename = helper.set_filename('ACCEPTANCE_DELAY')
    title = 'ACCEPTANCE DELAY BINS'
    calc_bins(df_accept, title, filename)

    out_spec = df_accept[(df_accept.workdays > 7) | (df_accept.workdays < 0)].copy()
    # out_spec.drop(columns=['install','received','wo','call','end_date','technician','month','days','analysis'], inplace=True)

    with pd.ExcelWriter(dest_filename, mode="a", engine='openpyxl') as writer:
        sheetname = 'Acceptance Delay'
        out_spec.to_excel(writer, sheet_name=sheetname, index=False)
        print(f"Saved data to sheet {sheetname}")


def convert_date_string(raw):
    return datetime.datetime.strftime(raw, '%Y-%m-%d')


def func(pct, all_vals):
    absolute = int(np.round(pct / 100. * np.sum(all_vals)))
    return "{:.0f}%\n{:d}".format(pct, absolute)


def calc_spec(x):
    if x <= 7 and x >= 0:
        return 'IN SPEC'
    elif x > 7:
        return 'OUT OF SPEC'
    else:
        return 'ERROR'


def get_accept(df_assets, mth_num=0):
    # create dataframe
    wo = pd.read_csv((config.wdir / 'acceptance.csv'))
    wo.drop(columns=['serial', 'model', 'manufacturer', 'gmdn_no', 'equip', 'dept', 'site'], inplace=True)
    wo.end_date = pd.to_datetime(wo.end_date)
    wo['month'] = wo.end_date.dt.month

    # get last month from today
    if mth_num == 0:
        mth_num = datetime.datetime.today().month
        if mth_num == 1:
            mth_num = 12
        else:
            mth_num = mth_num - 1

    # filter on last month and wo_subtype
    wo_analyse = wo[(wo.month == mth_num) & (wo.wo_subtype == 'COMMISSION')]

    assets = df_assets.drop(
        columns=['gmdn_no', 'gmdn', 'site', 'name', 'manufacturer', 'model', 'serial', 'price', 'warranty',
                 'replacement', 'tech_dept', 'contract', 'risk', 'eol', 'equip', 'last_wo', 'last_corr',
                 'last_pm', 'next_pm', 'division', 'retired', 'retire_reason'])

    # filter on required origins
    origins = assets[assets.origin.isin(['ADDITION', 'REPLACEMENT', 'EXCHANGE'])]

    # wo_analyse only has jobs ending in required month
    # origins has all assets with ADDED, etc
    # hence we are dependent on a commissioing work order being done, which is part of the process anyway
    merged = pd.merge(origins, wo_analyse, how='inner', on='asset_id')

    merged.end_date = pd.to_datetime(merged.end_date)
    merged.received = pd.to_datetime(merged.received)
    merged['days'] = merged.end_date - merged.received

    merged.replace(np.nan, '', inplace=True)

    merged['end_date_str'] = merged.end_date.apply(convert_date_string)
    merged['received_str'] = merged.received.apply(convert_date_string)

    merged['workdays'] = None
    for idx, row in merged.iterrows():
        merged.loc[idx, 'workdays'] = np.busday_count(row.received_str, row.end_date_str)

    merged['analysis'] = merged.workdays.apply(calc_spec)

    merged.drop(columns=['end_date_str', 'received_str', 'wo_subtype', 'wo_substatus'], axis=1, inplace=True)

    return merged


def calc_bins(merged, title, out_filename):
    bins = [-500, -1, 3, 7, 11, 15, 500]
    labels = ['Error', '0-3', '4-7', '8-11', '12-15', '>15']
    merged['binned'] = pd.cut(merged.workdays, bins=bins, labels=labels)

    series = merged.binned.value_counts()
    series = series.reindex(index=['0-3', '4-7', '8-11', '12-15', '>15', 'Error'])
    x = series.index
    y = series.values

    col = []
    for val in x:
        if val == '0-3':
            col.append('olivedrab')
        elif val == '4-7':
            col.append('yellowgreen')
        elif val == 'Error':
            col.append('saddlebrown')
        elif val == '8-11':
            col.append('lightcoral')
        elif val == '12-15':
            col.append('firebrick')
        elif val == '>15':
            col.append('darkred')

    # Figure Size
    fig, ax = plt.subplots(figsize=(20, 12))

    # Horizontal Bar Plot
    ax.bar(x, y, color=col)

    # Remove axes splines
    for s in ['top', 'bottom', 'left', 'right']:
        ax.spines[s].set_visible(False)

    # Remove x, y Ticks
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')

    # Add padding between axes and labels
    ax.xaxis.set_tick_params(pad=5)
    ax.yaxis.set_tick_params(pad=10)

    # Add x, y gridlines
    ax.grid(visible=True,
            color='grey',
            linestyle='-.',
            linewidth=0.5,
            alpha=0.8)

    # Show top values
    # ax.invert_yaxis()

    # Add annotation to bars
    for i in ax.patches:
        plt.text(i.get_width() + 0.2, i.get_y() + 0.5,
                 str(round((i.get_width()), 2)),
                 fontsize=12,
                 fontweight='bold',
                 color='dimgrey')

    # Add Plot Title
    ax.set_title('Acceptance Delay', loc='center', fontsize=25)
    ax.set_xlabel('Delay Bin Ranges (Days)', fontsize=15)
    ax.set_ylabel('No. Commissioned Assets', fontsize=15)
    ax.tick_params(axis='both', labelsize=15)

    fig.savefig((config.output / out_filename))
    print(f"Saved {out_filename}")

    # Show Plot
    if config.show_chart:
        plt.show()


def doughnut_notused(merged, title, out_filename):
    # https://matplotlib.org/stable/gallery/pie_and_polar_charts/pie_and_donut_labels.html
    print(merged.head())
    analysis_grp = merged.groupby('analysis').size()

    data = analysis_grp.tolist()
    data_labels = analysis_grp.index.tolist()

    fig, ax = plt.subplots(figsize=(18, 9), subplot_kw=dict(aspect="equal"))

    wedges, texts = ax.pie(data, wedgeprops=dict(width=0.5), startangle=90)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(data_labels[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                    horizontalalignment=horizontalalignment, **kw)

    ax.set_title("Matplotlib bakery: A donut")
    plt.show()

def calc_acceptance(merged, title, out_filename):
    print(merged.head())
    analysis_grp = merged.groupby('analysis').size()

    data = analysis_grp.tolist()
    data_labels = analysis_grp.index.tolist()

    # allow for no errors
    if len(data_labels) == 3:
        explode = (0.0, 0.1, 0.15)
        colors = ['darkkhaki', 'yellowgreen', 'lightcoral']  # error, good, bad
    elif len(data_labels) == 2:
        explode = (0.02, 0.05)
        colors = ['yellowgreen', 'lightcoral']  # without errors

    fig, ax = plt.subplots(figsize=(18, 9))  # , aspect='equal') 36,18

    wedges, texts, autotexts = ax.pie(data,
                                      autopct=lambda pct: func(pct, data),
                                      startangle=90,
                                      shadow=False,
                                      labels=data_labels,
                                      labeldistance=1.2,  # 1.05
                                      textprops={'fontsize': 12},   # 20
                                      colors=colors,
                                      explode=explode,
                                      wedgeprops={'linewidth': 3, 'edgecolor': 'white'},
                                      pctdistance=0.85)

    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)

    # ax.legend(wedges,
    #           data_labels,
    #           # title="Ingredients",
    #           loc="center left",
    #           bbox_to_anchor=(1, 0, 0.5, 1))

    plt.setp(autotexts, size=15, color='black', weight="bold")  # 20

    fig.savefig((config.output / out_filename))

    if config.show_chart:
        plt.show()

    plt.close()
