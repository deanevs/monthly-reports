from decouple import config
from pathlib import Path

smartsheet_token = config('smartsheet_token')

use_round = False
show_chart = True

do_overviews = False
do_pm_charts = True
do_pm_trends = True
do_availability = True
do_time_to_repair = True
do_acceptance = True

# load paths and files and create dataframes
wdir = Path(r'C:\Users\212628255\Documents\2 GE\AssetPlus\Monthly Reports\new downloads')
output = Path(r'C:\Users\212628255\Documents\2 GE\AssetPlus\Monthly Reports\output')

CORRECTIVE2021 = config('CORRECTIVE2021')
CORRECTIVE2022 = config('CORRECTIVE2022')
CORRECTIVE2023 = config('CORRECTIVE2023')

# declare all constants and lookups
RISKS = ['HIGH', 'MEDIUM', 'LOW']
# for high to low horizontal charts
risk_order = ['LOW', 'MEDIUM', 'HIGH']

# CONTRACT GROUPS 2
GE_CONTRACTS = ['MMS PM ONLY 20-25', 'MMS FULLY COMP 20-25', 'MMS OUT 20-25']
TRUST_CONTRACTS = ['OLYMPUS-2021', 'HOISTS', 'PENTAX', 'SPACELABS', 'MIS HEALTHCARE 2021', '3M HEALTH',
                   'TRUST - PCA PUMPS', 'MEDTRONIC/13']

# TECH DEPTS GROUPS 3
IMAGING = ['GE MVS DI', 'GE MVS ULS', 'GE ULS', 'GE DI']
BIOMED = ['GE BIOMED', 'GE LCS']
GE_OTHER = ['GE TEST EQUIPMENT', 'MEDTRONICS / GE']

# CHERYL'S CATEGORIES
GE_HEALTHCARE = ['GE MVS DI', 'GE MVS ULS', 'GE ULS', 'GE DI', 'GE BIOMED', 'GE LCS', 'GE COVID SUPPORT',
                 'GE TEST EQUIPMENT', 'MEDTRONICS / GE', 'GE LOAN EQUIPMENT']
CLINICAL_ENG = ['CLINICAL ENG', 'CLINICAL ENG CONTRACTS', 'POCT']
TRUST = ['COVID SUPPORT', 'ERU/DECON', 'LOAN EQUIPMENT', 'RADIOTHERAPY', 'RENAL']
ON_DEMAND_PAYG = ['ON DEMAND PAYG']
TBC = ['TECH DEPT TBC']

# DIVISIONS
DIVISIONS = ['WOMEN\'S, CHILDREN\'S & CLINICAL SUPPORT', 'MEDICINE & INTEGRATED CARE', 'PRIVATE HEALTHCARE',
             'SURGERY, CANCER & CARDIOVASCULAR', 'NURSING, ESTATES & FACILITIES', 'RESEARCH & DEVELOPMENT', 'CORPORATE']

# CORPORATE = ['NURSING, ESTATES & FACILITIES', 'RESEARCH & DEVELOPMENT', 'CORPORATE']


