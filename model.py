import pandas as pd
import numpy as np
import time
from sklearn.linear_model import LassoCV, Lasso
from statsmodels.tools.tools import pinv_extended
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import KFold, cross_validate
from sklearn.model_selection import train_test_split
import statsmodels.api as sm
import pygsheets

## Data preparation
gc = pygsheets.authorize(service_account_file='hackthon-396711-57515e0c836f.json')
survey_key = '1lwyWwhDdzcbvOCVUzKuJac8oRRysWfScTdOHfzXsTME'
sh = gc.open_by_key(survey_key)
ws = sh.worksheet_by_title('工作表1')
ws.export(filename = 'data')
number_of_factor = 12
df = pd.read_csv('data.csv', index_col=False)

df.dropna(subset=['比率'], inplace=True)
df = df.fillna(0)
df['比率'] = df['比率'].astype(str)
df.iloc[:, 2:(number_of_factor+2)] = df.iloc[:, 2:(number_of_factor+2)].astype(np.float32)
arr = df.iloc[:, 1:(number_of_factor+2)].to_numpy()

ratio = np.empty(0)
for fraction in arr[:, 0]:
    if fraction == '0':
        ratio = np.append(ratio, [0])
    else:
        numerator, denominator = fraction.split('/')
        ratio = np.append(ratio, float(int(numerator)/int(denominator)))

factor = arr[:, 1:(number_of_factor+1)]
factor_train, factor_test, ratio_train, ratio_test = train_test_split(factor, ratio,test_size=0.2,random_state=0)
df["ratio"] = ratio
# print(df)
def dist_type(data):

  # select only the variables that are metric type
  metric_vars = data.select_dtypes(include='number')
  cate_vars = data.select_dtypes(exclude='number')

  metric_vars = metric_vars.columns
  cate_vars = cate_vars.columns

  return list(metric_vars), list(cate_vars)

metric_variables, categorical_variables = dist_type(df)

def adjust(metric_variables, categorical_variables, metric_to_cate, cate_to_metric, drop):
  for i in drop:
    if i in metric_variables:
      metric_variables.remove(i)
    elif i in categorical_variables:
      categorical_variables.remove(i)
  for i in metric_to_cate:
    metric_variables.remove(i)
  for i in cate_to_metric:
    categorical_variables.remove(i)
  for i in metric_to_cate:
     categorical_variables.append(i)
  for i in cate_to_metric:
     metric_variables.append(i)

  return metric_variables, categorical_variables

metric_variables, categorical_variables = adjust(metric_variables, categorical_variables,
                                                 metric_to_cate = [], cate_to_metric = [], drop =[])
y= "ratio"

def dummyChange(data, y, drop, clf, pos_name = ""):
  data_processed = data.drop(drop, axis = 1)
  data_processed = data_processed.drop(y, axis = 1)
  if y in categorical_variables:
    categorical_variables.remove(y)
  for i in drop:
    if i in categorical_variables:
      categorical_variables.remove(i)
  if clf == True:
    res = []
    for i in data[y]:
      if i == pos_name:
        res.append(1)
      else:
        res.append(0)
    res_dict = {y : res}
    dummy_x = pd.concat([pd.get_dummies(data_processed, columns = categorical_variables, drop_first = True), pd.DataFrame(res_dict)], axis = 1)
  else:
    dummy_x = pd.concat([pd.get_dummies(data_processed, columns = categorical_variables, drop_first = True), data[y]], axis = 1)
  return dummy_x

data_changed = dummyChange(df, y, drop = ['判決書標頭', '比率', '結果'], clf = False, pos_name = "")

# Lasso Regression 
def LassoReg(data, y, input_data):
  start_time = time.time()
  model = make_pipeline(StandardScaler(), LassoCV(cv=10)).fit(data.drop(y, axis = 1), data[y])
  fit_time = time.time() - start_time
  lasso = model[-1]
  X_lin = sm.add_constant(data.drop(y, axis = 1))
  model = sm.OLS(data[y], X_lin)
  lasso_sm = model.fit_regularized(alpha = lasso.alpha_, L1_wt = 1)
  pinv_wexog,_ = pinv_extended(X_lin)
  normalized_cov_params = np.dot(pinv_wexog, np.transpose(pinv_wexog))
  final = sm.regression.linear_model.OLSResults(model, lasso_sm.params, normalized_cov_params)
  print("Lasso summary:\n", final.summary(), "\n")

  model = Lasso(lasso.alpha_)
  model.fit(data.drop(y, axis = 1), data[y])
  kfold = KFold(n_splits=10, shuffle=True, random_state=19972003)
  result = model.predict([input_data])
  scores = cross_validate(model, data.drop(y, axis=1), data[y], cv = kfold, scoring=("neg_root_mean_squared_error", "r2"),
                       return_train_score=True)
  print("Lasso RMSE:", -1 * np.mean(scores["test_neg_root_mean_squared_error"]))
  print("Lasso R Squared:", np.mean(scores["test_r2"]))
  return result
  

input_data = [10,	1,	0,	0,	9,	0,	0,	0,	0,	0,	0,	0]
result = LassoReg(data_changed, y, input_data)
print('The ratio is '+str(result[0]))
