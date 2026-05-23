# run pip install pulp
# run pip install pandas

import pandas as pd

from pulp import *

model = LpProblem("DietProblem", LpMinimize)

df_foods = pd.read_csv("diet_food.csv")
df_nutrients = pd.read_csv("diet_nutrients.csv")
df_food_nutrients = pd.read_csv("diet_food_nutrients.csv")

num_foods = df_foods.shape[0]

food_names = list(df_foods["name"])
print('The foods are:')
print('\t' , food_names)

# create a list of food decision variables
food_decision_variables = [LpVariable('x_'+str(j+1), 0.0, None) for j in range(num_foods)]
# Note: the argument 0.0 in creating LpVariable already sets lower bound
# of the variable created to 0.0. No need to add x >= 0 constraint.
# The None argument indicates that no upper bound is needed.


# make a dictionary that maps the variable for each food name. This will be useful
food_name_to_dec_var = {name:var for (name, var) in zip(food_names, food_decision_variables)}
print('The variables are:')
print('\t', food_name_to_dec_var)

obj_fun = sum([df_foods.iloc[j]['unit_cost'] * food_decision_variables[j] for j in range(num_foods)])
print('Objective function:' , obj_fun)
model += obj_fun

all_nutrients = [(row['name'], row['qmin'], row['qmax']) for _, row in df_nutrients.iterrows()]
print('All nutrients: \n\t', all_nutrients)

for (nk,l,u) in all_nutrients:
    # Just restrict ourselves to nutrient `nk`
    nut_terms = ( [ (row['Food'], row[nk]) for (_, row) in df_food_nutrients.iterrows() ])
    nut_lhs_expr = sum( [c*food_name_to_dec_var[name] for (name, c) in nut_terms])
    print(f'Constraints for nutrient: {nk}')
    print(f'\t {nut_lhs_expr} <= {u}')
    model += nut_lhs_expr <= u
    print(f'\t {nut_lhs_expr} >= {l}')
    model += nut_lhs_expr >= l 


model.solve()
# Each of the variables is printed with it's resolved optimum value
for f in food_names:
    v = food_name_to_dec_var[f]
    print(f' {f} --> {v.varValue} servings')
print(f'Cost: ${value(model.objective)}')
