import requests
import tkinter as tk
from tkinter import ttk, font

# Setup
API_KEY = "2c11b2de4dmshc9f9db90d75a981p1b09e1jsnc0a6d14694d2"
URL = "https://currency-exchange.p.rapidapi.com/exchange"
CURRENCIES = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "HKD", "NZD", "SGD"]
CACHE = {}

# Pulls a currency rate from a free API, then caches the currency rate and returns it.
def find_conversion_rate(from_currency, to_currency):
    key = f"{from_currency}_{to_currency}"

    if key in CACHE:
        return CACHE[key]
    else:
        headers = {
            "X-RapidAPI-Key": API_KEY,
            "X-RapidAPI-Host": "currency-exchange.p.rapidapi.com"
        }
        querystring = {"from": from_currency, "to": to_currency, "q": "1.0"}
        try:
            with requests.request("GET", URL, headers=headers, params=querystring) as response:
                response.raise_for_status()
                result = float(response.text)
        except (requests.exceptions.RequestException, ValueError):
            raise ValueError("API request failed")

        CACHE[key] = result
        return result


# Calculates money for the customer and profit for the service provider
def calculate_profit(from_currency, to_currency, intermediary_currency, amount):
    try:
        rate1 = find_conversion_rate(from_currency, intermediary_currency)
        rate2 = find_conversion_rate(intermediary_currency, to_currency)
    except ValueError:
        raise ValueError("Unable to find conversion rates.")

    start_to_intermediary = amount * rate1
    intermediary_to_end = start_to_intermediary * rate2
    service_profit = f"0.00{str(intermediary_to_end).split('.')[1][2:4]}"

    return start_to_intermediary, intermediary_to_end, service_profit

class CurrencyConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Currency Converter")

        self.from_currency_label = tk.Label(master, text="From Currency:")
        self.from_currency_label.grid(row=0, column=0, padx=75, pady=10)
        self.from_currency_entry = tk.Entry(master)
        self.from_currency_entry.grid(row=0, column=1, padx=75, pady=10)

        self.to_currency_label = tk.Label(master, text="To Currency:")
        self.to_currency_label.grid(row=1, column=0, padx=75, pady=10)
        self.to_currency_entry = tk.Entry(master)
        self.to_currency_entry.grid(row=1, column=1, padx=75, pady=10)

        self.amount_label = tk.Label(master, text="Amount:")
        self.amount_label.grid(row=2, column=0, padx=75, pady=10)
        self.amount_entry = tk.Entry(master)
        self.amount_entry.grid(row=2, column=1, padx=75, pady=10)

        self.convert_button = tk.Button(master, text="Convert", command=self.convert)
        self.convert_button.grid(row=3, column=1, padx=75, pady=10)

        self.table = tk.ttk.Treeview(master)
        self.table["columns"] = ("1", "2", "3", "4")
        self.table.column("#0", width=0, stretch=tk.NO)
        self.table.column("1", width=250, anchor=tk.CENTER)
        self.table.column("2", width=250, anchor=tk.CENTER)
        self.table.column("3", width=250, anchor=tk.CENTER)
        self.table.column("4", width=100, anchor=tk.CENTER)
        self.table.heading("#0", text="", anchor=tk.CENTER)
        self.table.heading("1", text="Intermediary currency", anchor=tk.CENTER)
        self.table.heading("2", text="{} to intermediary currency".format(self.from_currency_entry.get().upper()), anchor=tk.CENTER)
        self.table.heading("3", text="Intermediary currency to {}".format(self.to_currency_entry.get().upper()), anchor=tk.CENTER)
        self.table.heading("4", text="PROFIT!", anchor=tk.CENTER)
        self.table.grid(row=4, column=0, columnspan=2)
        
        self.result_label = tk.Label(master, text="")
        self.result_label.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def convert(self):
        from_currency = self.from_currency_entry.get().upper()
        to_currency = self.to_currency_entry.get().upper()
        amount = float(self.amount_entry.get())

        for row in self.table.get_children():
            self.table.delete(row)

        self.table.heading("2", text="{} to intermediary currency".format(from_currency), anchor=tk.CENTER)
        self.table.heading("3", text="Intermediary currency to {}".format(to_currency), anchor=tk.CENTER)

        #Inserting the values to the table
        best_customer_money = float("-inf")
        best_service_profit = float("-inf")
        best_intermediary_currency_customer = None
        best_intermediary_currency_service = None
        
        for intermediary_currency in CURRENCIES:
            if intermediary_currency == from_currency or intermediary_currency == to_currency:
                continue
            
            start_to_intermediary, intermediary_to_end, service_profit = calculate_profit(from_currency, to_currency, intermediary_currency, amount)
            self.table.insert("", tk.END, text="Row 1", values=(intermediary_currency, start_to_intermediary, intermediary_to_end, service_profit))
            if intermediary_to_end > best_customer_money:
                best_customer_money = intermediary_to_end
                best_intermediary_currency_customer = intermediary_currency
            if float(service_profit) > best_service_profit:
                best_service_profit = float(service_profit)
                best_intermediary_currency_service = intermediary_currency
                
        self.result_label.configure(text=f"Best for customer: {best_intermediary_currency_customer}\nBest for service provider: {best_intermediary_currency_service}")

root = tk.Tk()
gui = CurrencyConverterGUI(root)
root.mainloop()    