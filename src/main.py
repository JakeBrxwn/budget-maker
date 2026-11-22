#!/usr/bin/env python3
"""
Work out how much of your monthly take-home pay is left after fixed bills.
"""
import fcntl
import json
import os
import re
from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile

FILELOCATION = Path.home() / "Documents" / "budgeter" / "saved.json"
BILLS = (
    "Rent (including utilities)", "Internet", "Phone", "Car", "Insurance",
    "Subscriptions", "Other fixed bills", "Credit cards", "Personal loans",
    "Student loans", "Medical loans", "Miscellaneous loans and debts",
)
OLD_BILLS = "Unitemized bills from your old budget"


def amount(value) -> Decimal:
    """
    Read a dollar amount without rounding away a fraction of a cent.

    Args:
        value: A string or number representing a dollar amount.
    Returns:
        A Decimal representing the dollar amount.
    """
    if not re.fullmatch(r"(?:[0-9]{1,15}(?:\.[0-9]{0,2})?|\.[0-9]{1,2})", str(value)):
        raise ValueError("Enter a nonnegative dollar amount with up to two decimal places.")
    return Decimal(value)


def ask_amount(label, current) -> Decimal:
    """
    Ask the user for a dollar amount, with a default value.

    Args:
        label: A string describing the amount.
        current: The current value of the amount.
    Returns:
        A Decimal representing the user's input.
    """
    while True:
        answer = input(f"{label} [${current:,.2f}]: ").strip()
        if not answer:
            return current
        try:
            return amount(answer)
        except ValueError as error:
            print(error)


def old_amount(value, label) -> Decimal:
    """
    Read a dollar amount from the old budget, with a default value of zero.

    Args:
        value: A string or number representing a dollar amount.
        label: A string describing the amount.
    Returns:
        A Decimal representing the dollar amount, or zero if the value is negative.
    """
    if type(value) is int and value < 0:
        print(f"Your old {label} was {value}. Its starting amount is now $0.00.")
        return Decimal(0)
    return amount(value)


def load_budget():
    """
    Load this month's starting figures, including budgets from the original script.
    """
    try:
        with FILELOCATION.open(encoding="utf-8") as data_file:
            profile = json.load(data_file, parse_float=Decimal)
    except FileNotFoundError:
        print("Let's set up your monthly budget.")
        return Decimal(0), {}

    if "class_data" in profile:
        old = profile["class_data"]
        print("Your old budget has one bill total. Confirm your take-home income below.")
        return old_amount(old["income"], "income"), {OLD_BILLS: old_amount(old["bills"], "bill total")}

    bills = profile["bills"]
    if not isinstance(bills, dict) or not set(bills).issubset((*BILLS, OLD_BILLS)):
        raise ValueError("Unrecognized bill categories in your save file.")
    print("Welcome back. Here are your saved monthly amounts.")
    return amount(profile["income"]), {name: amount(value) for name, value in bills.items()}


def save_budget(income, bills) -> None:
    """
    Save this month's starting figures, including budgets from the original script.

    Args:
        income: A Decimal representing the user's monthly take-home pay.
        bills: A dictionary mapping bill names to Decimal amounts.
    Returns:
        Nothing. Writes the budget to a JSON file.
    """
    profile = {"income": str(income), "bills": {name: str(cost) for name, cost in bills.items()}}
    temp = NamedTemporaryFile(mode="w", encoding="utf-8", dir=FILELOCATION.parent, delete=False)
    try:
        with temp:
            json.dump(profile, temp, indent=2)
        os.replace(temp.name, FILELOCATION)
    finally:
        Path(temp.name).unlink(missing_ok=True)


def finance_handler() -> None:
    """
    Ask the user for their monthly income and bills, then save the budget.
    """
    income, bills = load_budget()
    print("Press Enter to keep the amount shown, or type a new monthly amount.")
    income = ask_amount("Monthly income after tax", income)
    print("Enter monthly bills and the payment you make each month on each type of debt.")
    for name in BILLS:
        bills[name] = ask_amount(name, bills.get(name, Decimal(0)))
    if OLD_BILLS in bills:
        print("Keep only the part of your old bill total you haven't entered above.")
        remainder = ask_amount(OLD_BILLS, bills[OLD_BILLS])
        if remainder:
            bills[OLD_BILLS] = remainder
        else:
            del bills[OLD_BILLS]

    total = sum(bills.values())
    remaining = income - total
    save_budget(income, bills)
    print(f"Budget saved. Monthly bills and debt payments: ${total:,.2f}.")
    if remaining < 0:
        print(f"Your monthly payments exceed your income by ${-remaining:,.2f}.")
    else:
        print(f"You have ${remaining:,.2f} left this month after bills.")


def start() -> None:
    print("Hello, welcome to your budget manager.")
    try:
        FILELOCATION.parent.mkdir(parents=True, exist_ok=True)
        directory = os.open(FILELOCATION.parent, os.O_RDONLY)
        try:
            fcntl.flock(directory, fcntl.LOCK_EX | fcntl.LOCK_NB)
            finance_handler()
        finally:
            os.close(directory)
    except BlockingIOError:
        raise SystemExit("Your budget is already open. Finish that session first.")
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("\nBudget entry cancelled.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise SystemExit(f"Could not load or save your budget at {FILELOCATION}: {error}")


if __name__ == "__main__":
    start()
