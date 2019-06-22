import numpy as np
import pandas as pd
from scipy.stats import skew, norm
from scipy.special import boxcox1p
from scipy.stats import boxcox_normmax
from sklearn.preprocessing import StandardScaler 

MODEL_COLUMNS = ['loan_amnt', 'term', 'int_rate',
       'installment', 'grade', 'sub_grade', 'emp_length',
       'home_ownership', 'annual_inc',
       'loan_status', 'pymnt_plan', 'dti', 'delinq_2yrs','open_acc',
     'revol_bal', 'revol_util', 'total_acc','out_prncp',
       'collections_12_mths_ex_med', 'application_type',
       'acc_now_delinq',  'total_rev_hi_lim',
       'acc_open_past_24mths', 'bc_util',
       'chargeoff_within_12_mths',
       'num_accts_ever_120_pd', 'num_actv_rev_tl',
     'num_il_tl', 'num_tl_120dpd_2m','num_tl_30dpd', 
       'pct_tl_nvr_dlq', 'percent_bc_gt_75', 'pub_rec_bankruptcies',
    'fico', 'credit_history']

numeric_features = ['loan_amnt', 'int_rate', 'installment',
       'emp_length', 'annual_inc',
       'dti', 'delinq_2yrs', 'open_acc', 'revol_bal',
       'revol_util', 'total_acc', 'out_prncp', 'collections_12_mths_ex_med',
      'acc_now_delinq', 'total_rev_hi_lim',
       'acc_open_past_24mths', 'bc_util', 'chargeoff_within_12_mths',
       'num_accts_ever_120_pd', 'num_actv_rev_tl', 'num_il_tl',
       'num_tl_120dpd_2m', 'num_tl_30dpd', 'pct_tl_nvr_dlq',
       'percent_bc_gt_75', 'pub_rec_bankruptcies', 'fico', 'credit_history']

COLUMNS_TO_FILL_NULL = ['dti',
       'delinq_2yrs', 'inq_last_6mths', 'open_acc',
       'pub_rec', 'revol_util', 'total_acc',
     'collections_12_mths_ex_med', 'acc_now_delinq',
       'tot_coll_amt', 'tot_cur_bal', 'total_rev_hi_lim',
       'acc_open_past_24mths', 'avg_cur_bal', 'bc_open_to_buy', 'bc_util',
       'chargeoff_within_12_mths', 'delinq_amnt', 'mo_sin_old_il_acct',
       'mo_sin_old_rev_tl_op', 'mo_sin_rcnt_rev_tl_op', 'mo_sin_rcnt_tl',
       'mort_acc', 'mths_since_recent_bc', 'mths_since_recent_inq',
       'num_accts_ever_120_pd', 'num_actv_bc_tl', 'num_actv_rev_tl',
       'num_bc_sats', 'num_bc_tl', 'num_il_tl', 'num_op_rev_tl',
       'num_rev_accts', 'num_rev_tl_bal_gt_0', 'num_sats', 'num_tl_120dpd_2m',
       'num_tl_30dpd', 'num_tl_90g_dpd_24m', 'num_tl_op_past_12m',
       'pct_tl_nvr_dlq', 'percent_bc_gt_75', 'pub_rec_bankruptcies',
       'tax_liens', 'tot_hi_cred_lim', 'total_bal_ex_mort', 'total_bc_limit',
       'total_il_high_credit_limit', 'annual_inc', 'credit_history', 'emp_length']

def preprocessing(df):

    # Feature engineering and column transformation
    df['fico'] = (df['fico_range_low'] + df['fico_range_high'])/2
    df['application_type'] = [0 if x == 'Individual' else 1 for x in df['application_type'].values]
    df['emp_length'] = [np.nan if pd.isnull(x) else 10 if x.split()[0]=='10+' else 0 if x.split()[0]=='<' 
                    else int(x.split()[0]) for x in df['emp_length'].values]
    df['home_ownership'] = [1 if x=='OWN' else 0 for x in df['home_ownership'].values]
    df['pymnt_plan'] = [1 if x=='y' else 0 for x in df['pymnt_plan'].values]

    df['issue_d'] = pd.to_datetime(df['issue_d'])
    df['earliest_cr_line']= pd.to_datetime(df['earliest_cr_line'])

    df['credit_history'] = [int((x-y).days) if pd.notnull(x) and pd.notnull(y) else np.nan 
                          for x, y in zip(df['issue_d'], df['earliest_cr_line'])]

    df['dti'] = [0 if x==-1 else np.nan if x == 999 else x for x in df['dti'].values]
    df['term'] = [x.split()[0] for x in df['term'].values]

    # Fill Null values
    for feature in COLUMNS_TO_FILL_NULL:
        df[feature] = df.groupby("addr_state")[feature].transform(lambda x: x.fillna(x.median()))

    # select columns to use
    test_df = df[MODEL_COLUMNS]
    #test_df['loan_status_int'] = [1 if x in ['Charged Off', 'Does not meet the credit policy. Status:Charged Off',
                                     #'Default'] else 0 for x in test_df['loan_status'].values]

    # Fill the Null values if they can not be filled by addr_state
    test_df.fillna(0, inplace=True)
    x_test_df = test_df.drop('loan_status', axis=1)
    # Find skewed numerical features
    skew_features = x_test_df[numeric_features].apply(lambda x: skew(x)).sort_values(ascending=False)

    high_skew = skew_features[skew_features > 0.5]
    skew_index = high_skew.index

    #Normalize skewed features
    for i in skew_index:
        x_test_df[i] = boxcox1p(x_test_df[i], boxcox_normmax(x_test_df[i] + 1))

    # One Hot Encoding
    x_test_df = pd.get_dummies(x_test_df, drop_first=True)

    for x in ['grade_B', 'grade_C', 'grade_D', 'grade_E', 'grade_F',
       'grade_G', 'sub_grade_A2', 'sub_grade_A3', 'sub_grade_A4',
       'sub_grade_A5', 'sub_grade_B1', 'sub_grade_B2', 'sub_grade_B3',
       'sub_grade_B4', 'sub_grade_B5', 'sub_grade_C1', 'sub_grade_C2',
       'sub_grade_C3', 'sub_grade_C4', 'sub_grade_C5', 'sub_grade_D1',
       'sub_grade_D2', 'sub_grade_D3', 'sub_grade_D4', 'sub_grade_D5',
       'sub_grade_E1', 'sub_grade_E2', 'sub_grade_E3', 'sub_grade_E4',
       'sub_grade_E5', 'sub_grade_F1', 'sub_grade_F2', 'sub_grade_F3',
       'sub_grade_F4', 'sub_grade_F5', 'sub_grade_G1', 'sub_grade_G2',
       'sub_grade_G3', 'sub_grade_G4', 'sub_grade_G5']:
        if x not in x_test_df.columns:
            x_test_df[x] = 0

    sc = StandardScaler()
    x_test_df[numeric_features] = sc.fit_transform(x_test_df[numeric_features])

    return x_test_df





