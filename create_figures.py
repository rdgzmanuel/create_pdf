import pandas as pd
import numpy as np
import pizza_analysis_cleaning
import plotly.express as px
import os
import copy


import plotly.io as pio  # To solve some problems with plotly
pio.kaleido.scope.mathjax = None


def create_profits(df_weekly_pizzas, df_prices):
    weeks = [i for i in range(1, 51)]
    profits = []

    for i in range(1, 51):
        profit = 0
        for j in range(df_weekly_pizzas.shape[0]):
            pizza = df_weekly_pizzas.iloc[j, 0]
            price = df_prices.loc[pizza, "price"]
            sold = df_weekly_pizzas.iloc[j, i]
            if sold >= df_weekly_pizzas.loc[j, "optimal"]:
                profit += (df_weekly_pizzas.loc[j, "optimal"] * price * 0.15)  # We add the profit for each pizza sold.
            else:
                remaining = df_weekly_pizzas.loc[j, "optimal"] - sold
                profit -= (remaining * price * 0.85)
        profits.append(profit)

    profits_dict = {"week": weeks,
                    "profit": profits}
    df_profits = pd.DataFrame(profits_dict)
    return df_profits


def show_profits_year(df_profits):
    y = [0, 2000]
    if not os.path.exists("images"):
        os.mkdir("images")

    fig = px.line(df_profits, x='week', y="profit", range_y=y, height=400, title="Total Profit through the Year",
                  markers=True)
    fig.show()

    fig.write_image("images/profit_year.png")


def create_weekly_pizzas_total(df_weekly_pizzas):
    weekly_pizzas_total = {"weeks": [], "orders": []}
    week = 1
    for column in df_weekly_pizzas.columns:
        if column not in ["pizza", "mean", "optimal"]:
            if week % 2 == 1:
                weekly_pizzas_total["weeks"].append(week)
                weekly_pizzas_total["orders"].append(df_weekly_pizzas[column].sum())
            week += 1

    df_weekly_pizzas_total = pd.DataFrame(weekly_pizzas_total)
    return df_weekly_pizzas_total


def show_weekly_orders(df_weekly_pizzas_total):
    y = [0, 1200]
    fig = px.line(df_weekly_pizzas_total, x='weeks', y='orders', title="Orders by Weeks of the year", range_y=y,
                  height=400, markers=True)
    fig.show()

    fig.write_image("images/profit_year.png")


def update_order_details(df_order_details, df_pizza_types):
    new_df = copy.deepcopy(df_order_details)
    new_df["category"] = ""
    new_df["subcategory"] = ""
    for i in range(new_df.shape[0]):
        pizza = new_df.iloc[i, 2]
        if pizza[-2] != "_":
            # We check this beacuse the greek pizza can be xl or xxl.
            pizza = pizza[:9]
        else:
            pizza = pizza[:-2]
        new_df.loc[i, "subcategory"] = pizza
        j = 0
        found = False
        while not found and j < df_pizza_types.shape[0]:
            if df_pizza_types.iloc[j, 0] == pizza:
                new_df.loc[i, "category"] = df_pizza_types.iloc[j, 2]
                found = True
            j += 1
    return new_df


def create_cat_subcat(df_order_details):
    total = df_order_details.shape[0] - 1
    categories = sorted(list(df_order_details["category"].unique()))
    categories.remove("")
    counts = [i for i in df_order_details["category"].value_counts().sort_index()]
    counts.remove(1)

    subcategories = sorted(list(df_order_details["subcategory"].unique()))
    subcategories.remove("")
    counts_sub = [i for i in df_order_details["subcategory"].value_counts().sort_index()]
    counts_sub.remove(1)

    new_counts_sub = [round(count / total * 100, 2) for count in counts_sub]

    dict_categories = {"categories": categories,
                    "counts": counts}
    df_categories = pd.DataFrame(dict_categories)

    dict_subcategories = {"subcategories": subcategories,
                    "percentage": new_counts_sub}
    df_subcategories = pd.DataFrame(dict_subcategories)
    df_subcategories = df_subcategories.sort_values("percentage", ascending=True)

    return df_categories, df_subcategories


def show_cat_subcat(df_categories, df_subcategories):
    fig1 = px.pie(df_categories, names="categories", values="counts", title="Total Orders by Category %")
    fig1.show()
    fig1.write_image("images/orders_category.png")

    fig2 = px.bar(df_subcategories, x="subcategories", y="percentage", title="Total Orders by Subcategory %", 
                  orientation="v", height=600, facet_row_spacing=0.1, width=900)
    fig2.show()
    fig2.write_image("images/orders_subategory.png")



if __name__ == "__main__":
    df_order_details = pd.read_csv("order_details.csv", sep = ";", encoding="latin1")
    df_orders = pd.read_csv("orders.csv", sep=";")
    df_pizzas = pd.read_csv("pizzas.csv")
    df_pizza_types = pd.read_csv("pizza_types.csv", encoding="latin1")

    # Cleaning the mewwy Datasets
    df_orders = df_orders.sort_values("order_id")
    df_orders = df_orders.reset_index(drop=True)
    df_orders.index = np.arange(1, len(df_orders) + 1)
    df_order_details = df_order_details.sort_values("order_details_id")
    df_order_details = df_order_details.reset_index(drop=True)
    df_order_details.index = np.arange(1, len(df_order_details) + 1)

    pizza_ingredients = pizza_analysis_cleaning.create_pizza_ingredients(df_pizza_types)
    ingredients = pizza_analysis_cleaning.create_ingredients(pizza_ingredients)

    df_prices = pizza_analysis_cleaning.obtain_prices(df_pizzas)
    df_orders = pizza_analysis_cleaning.clean_orders(df_orders)
    df_order_details = pizza_analysis_cleaning.clean_order_details(pizza_ingredients, df_order_details)
    df_order_details.dropna()

    df_weekly_pizzas = pizza_analysis_cleaning.create_weekly_pizzas(df_orders, df_order_details, df_prices, pizza_ingredients)

    df_profits = create_profits(df_weekly_pizzas, df_prices)
    show_profits_year(df_profits)

    df_weekly_pizzas_total = create_weekly_pizzas_total(df_weekly_pizzas)
    show_weekly_orders(df_weekly_pizzas_total)

    df_order_details = update_order_details(df_order_details, df_pizza_types)
    df_categories, df_subcategories = create_cat_subcat(df_order_details)
    show_cat_subcat(df_categories, df_subcategories)
