#!/usr/bin/env python
"""
This is going to be a finance module. The main file. Should only be one file.
"""
import os
import getpass
import sys
import datetime
import json

PATHTOOS = f"/home/{getpass.getuser()}/Documents/budgeter"

class Money:
    """
    Handles money for users. Keeps track of items persistently.
    """

    const_purchases: int
    income: int
    cur_purchases: int
    last_balance: int

    def __init__(self, last = False):
        """
        Initialize the class.
        """
        self.last = last
        if self.last:
            print("Coming soon!")
        else:
            self.cur_balance = 0
            self.income = 0
            self.cur_purchases = 0
            self.last_balance = 0

    def get_balance(self) -> int:
        """
        Grab the user's current balance.
        """
        return self.cur_balance

    def set_balance(self, i: int):
        """
        Set the current balance for a user.
        """
        self.cur_balance = i

    def get_const_purch(self) -> int:
        """
        Get the constant purchase amounts.
        """
        return self.const_purchases

    def set_const_purch(self, i: int):
        """
        Setting constant purchase amounts.
        """
        self.const_purchases = i

    def get_last_bal(self):
        """
        This does not have merit yet.
        """
        return self.last_balance

    def set_income(self, i: int):
        """
        Set the user's consistent income.
        """
        self.income = i

    def get_income(self):
        """
        Return the user's consistent income.
        """
        return self.income


def finance_handler(user: Money) -> None:
    """
    Manage all finances through inputs given by the user.
    """
    post_bills = user.get_balance() - user.get_const_purch()
    print("You have ", post_bills, " for money after your bills are applied.")
    print(
        "Do you have any debt or credit cards you want to account for? \n",
        "if yes, please enter how much available credit you have and how much you will pay off",
    )
    credit_free = int(input("Please enter how much credit you have: "))
    credit_to_pay = int(input("Please select how much debt you plan on paying off: "))
    overall_credit = int(input("Account for how much overall credit you have: "))
    credit_debt = overall_credit - credit_free - credit_to_pay
    print(
        "You have ",
        credit_debt,
        " in debt. You have ",
        post_bills,
        " after this. Overall debt is: ",
        post_bills - credit_debt,
        "\n Depending on your income, you will recoup this for a month.",
    )
    post_money = 0
    user.set_income(int(input("This should be your income.")))
    if user.get_income() <= 0:
        print(
            "You need to look for income to make this sustainable.\n",
            "That said, you will have the same amount as before. \n",
        )
    print(
        "Assuming this is monthly, you will have this after you're paid: ",
        user.get_income() + post_bills - credit_debt,
    )
    post_money = user.get_income() + post_bills - credit_debt
    user.set_balance(post_money)
    print(
        "Now tell us how many things you will be buying and the cost.\n",
        "Note: Tell us to stop by entering any negative number. \n",
    )

    spend_amt = 0
    while True:
        indulges = int(input("Enter your money spent on indulgences: "))
        if indulges < 0: break
        else: spend_amt += indulges
    user.set_balance(user.get_balance() - spend_amt)
    print(
        "After indulging, you will have ",
        user.get_balance(),
        " left over.\n",
    )

    print(
        "Now that you have calculated everything, we will save this session.",
        "Beginning file save... \n",
    )
    json_data_str = {
        'date': datetime.datetime.now(),
        'class_data': {
            'cur_balance': user.get_balance(),
            'income': user.get_income(),
            'cur_purchases': user.get_const_purch(),
            'last_balance': user.get_last_bal(),
        },
    }
    new_file = f"{PATHTOOS}/saved.json"
    with open(new_file, "w") as json_file:
        json.dump(json_data_str, json_file)
    if os.path.isfile(new_file): print("Save file written.")
    else: print("Failed to write file. Continuing as normal.")

def start() -> None:
    """
    Assert the beginning of program.
    """
    print("Hello, welcome to your budget manager.")
    print("We're checking if you have something on file...\n")
    if os.path.isdir(PATHTOOS):
        print("Welcome back. We loaded your prior finances")
        print("This feature is coming soon.")
    else:
        print("You're new here. We will create a directory for your items.")
        os.mkdir(PATHTOOS)
        print("Path made. We will handle your finances now.\n")
        u_money = Money()
        print("How much money do you have right now? Only enter a number.")
        uc_money = input("Enter a number: ")
        if uc_money.isdigit():
            print("Good job. Now enter how much you constantly spend.")
            u_money.set_balance(int(uc_money))
        else:
            print("We cannot handle a value that contains letters. Goodbye")
            sys.exit(1)
        uc_money = input("Enter a number: ")
        if uc_money.isdigit():
            print("Great, we'll start handling your finances now.")
            u_money.set_const_purch(int(uc_money))
            finance_handler(u_money)
            print("Goodbye :D")
        else:
            print("We cannot handle a value that contains letters. Goodbye.")
            sys.exit(1)


if __name__ == "__main__":
    start()
