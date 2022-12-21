"""
title: Spending/Expenditure Tracker
author: Joanna Hao
date-created: 2022-12-16
"""
import sqlite3
import pathlib


# ----- SUBROUTINES ----- #
# --- Inputs
def getFileContent(filename):
    

def menu() -> int:
    print("""
Please choose an option:
1. View a table's data
2. Modify some existing data
3. Add new data set
4. Calculate greatest expense & revenue source
    """)
    choice = input("> ")
    if choice.isnumeric() and 1 <= int(choice) <= 4:
        return int(choice)
    else:
        print("Please enter a valid number from the list")
        return menu()

def getTableName():  # all options
    print("""
Please a select a table to interact with:
1. Income
2. Cost of Goods Sold
3. Business Expenses
4. Home Office & Home Operational Costs
5. Automobile Expenses
6. Bank Record
7. Miscellaneous Information
    """)
    table = input("> ")
    if table.isnumeric() and 1 <= int(table) <= 7:
        return int(table)
    else:
        print("Please select a valid option from the list.")
        return getTableName()


def getYear():  # option 3 (?), 4
    pass




# --- Processing
def setupContent():
    global CURSOR, CONNECTION
    CURSOR.execute("""
        CREATE TABLE
            income (
                date INTEGER PRIMARY KEY,
                sales FLOAT,
                commissions_fees FLOAT,
                professional_income FLOAT,
                sales_tax FLOAT
            )
    ;""")

    CURSOR.execute("""
        CREATE TABLE
            cost_goods_sold (
                date INTEGER PRIMARY KEY,
                opening_inventory FLOAT,
                year_purchases FLOAT,
                direct_wage_costs FLOAT,
                subcontracts FLOAT,
                other_costs FLOAT,
                closing_inventory FLOAT,
                sales_tax FLOAT
            )
    ;""")

    CURSOR.execute("""
        CREATE TABLE
            expenses (
                date INTEGER PRIMARY KEY,
                advertising FLOAT,
                meals_entertainment FLOAT,
                bad_debts FLOAT,
                insurance FLOAT,
                interest FLOAT,
                provincial_license_fee FLOAT,
                memberships_fees FLOAT,
                business_taxes FLOAT,
                govt_fees FLOAT,
                office_expenses FLOAT,
                supplies FLOAT,
                professional_legal_fees FLOAT,
                management_admin fees FLOAT,
                rent FLOAT,
                maintenance_repairs FLOAT,
                sub_contractors FLOAT,
                computer_expenses FLOAT,
                salary FLOAT,
                travel FLOAT,
                phone_utilities FLOAT,
                internet_cable FLOAT,
                delivery_freight FLOAT,
                capital_cost_allowance FLOAT,
                other FLOAT
            )
    ;""")

    CURSOR.execute("""
        CREATE TABLE
            home (
                date INTEGER PRIMARY KEY,
                office_sq_footage INTEGER,
            )
    ;""")


def getOneTableData():  # option 1, 2/3/4
    pass


def getAllTableData():  # option 1
    pass


def getTableColNames():  # option 2, 3, 4
    pass


# --- Outputs



# --- variables
DATABASE_FILE = "business_finance_tracker.db"
FIRST_RUN = True
if (pathlib.Path.cwd() / DATABASE_FILE).exists():
    FIRST_RUN = False

CONNECTION = sqlite3.connect(DATABASE_FILE)
CURSOR = CONNECTION.cursor()

INITIAL_DATA_FILES = ["file1.csv", "file2.csv", "file3.csv", ]


if __name__ == "__main__":
    # ----- MAIN PROGRAM CODE ----- #
    if FIRST_RUN:
        # setup everything
        CONTENT = getFileContent("INITIAL_DATA.csv")  # modify name later
        setupContent(CONTENT)
