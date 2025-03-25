import tkinter as tk
from tkinter import messagebox, ttk
import requests
from bs4 import BeautifulSoup
import random
import os
import threading
import webbrowser

SEARCHED_CREATURES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "searched_creatures.txt")

def fetch_creature_details(creature_name):
    url = f"https://www.game.guide/{creature_name}-value-creatures-of-sonaria"
    try:
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        value_element = soup.find('p', class_='elementor-heading-title', string=lambda t: "Value:" in t)
        value = value_element.text.split(":")[-1].strip() if value_element else "N/A"

        demand_element = soup.find('p', class_='elementor-heading-title', string=lambda t: "Demand:" in t)
        demand = demand_element.text.split(":")[-1].strip() if demand_element else "N/A"

        stability_element = soup.find('p', class_='elementor-heading-title', string=lambda t: "Stability:" in t)
        stability = stability_element.text.split(":")[-1].strip() if stability_element else "N/A"

        last_update_element = soup.find('span', class_='posted-on')
        last_update_time = last_update_element.find('time').text.strip() if last_update_element else "N/A"

        return value, demand, stability, last_update_time
    except requests.exceptions.RequestException as e:
        return "Error fetching data", "N/A", "N/A", "N/A"

def save_searched_creature(creature_name):
    try:
        if not os.path.exists(SEARCHED_CREATURES_FILE):
            with open(SEARCHED_CREATURES_FILE, "w") as file:
                pass

        with open(SEARCHED_CREATURES_FILE, "r") as file:
            searched_creatures = {line.strip() for line in file}

        if creature_name not in searched_creatures:
            with open(SEARCHED_CREATURES_FILE, "a") as file:
                file.write(creature_name + "\n")

        update_autocomplete_suggestions()
    except PermissionError:
        messagebox.showerror(
            "Permission Error",
            f"Cannot write to file: {SEARCHED_CREATURES_FILE}. Check file permissions or run the program with appropriate privileges."
        )
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def update_autocomplete_suggestions():
    try:
        with open(SEARCHED_CREATURES_FILE, "r") as file:
            suggestions = [line.strip() for line in file]
        entry['values'] = suggestions
    except FileNotFoundError:
        entry['values'] = []

def display_results():
    creature_name = entry.get().replace(" ", "-").lower()
    if not creature_name.strip():
        messagebox.showwarning("Input Error", "Please enter a valid creature name.")
        return

    loading_label, progress_bar = show_loading_screen()

    def fetch_and_display():
        value, demand, stability, last_update_time = fetch_creature_details(creature_name)

        hide_loading_screen(loading_label, progress_bar)

        if value == "Error fetching data" or demand == "N/A" or stability == "N/A":
            messagebox.showwarning("Invalid Creature", "Could not fetch data for this creature. Please check the name and try again.")
            return

        save_searched_creature(creature_name)

        value_text.set(f"{value} Mush")
        demand_text.set(f"{demand} Players")
        stability_text.set(stability)

        tips = generate_trading_tips(demand, stability)

        tips_entry.config(state=tk.NORMAL)
        tips_entry.delete(1.0, tk.END)
        tips_entry.insert(tk.END, "\n".join(tips))
        tips_entry.config(state=tk.DISABLED)

        last_update_label.config(text=f"Last Update: {last_update_time}")

    threading.Thread(target=fetch_and_display, daemon=True).start()

def generate_trading_tips(demand, stability):
    tips = []
    if "N/A" not in demand:
        try:
            demand_value = int(demand.split("/")[0])
        except ValueError:
            demand_value = 0

        if demand_value >= 9:
            tips.append("The demand is very high! It’s the best time to sell at premium prices.")
        elif 7 <= demand_value < 9:
            tips.append("The demand is high! You can wait for better offers.")
        elif 5 <= demand_value < 7:
            tips.append("The demand is moderate. Be strategic in your trades.")
        elif 3 <= demand_value < 5:
            tips.append("The demand is low. Try to sell quickly before it drops further.")
        else:
            tips.append("The demand is very low. Selling may take a while, or you may want to hold on.")

    if stability == "STABLE":
        tips.append("Prices are steady. It’s a good time to make trades.")
    elif stability == "FLUCTUATING":
        tips.append("Prices are unpredictable. Trade with caution and stay informed.")
    elif stability == "DECLINING":
        tips.append("Prices are dropping. Consider selling quickly to avoid losing value.")
    elif stability == "RISING":
        tips.append("Prices are on the rise! You might want to hold off for a while to get higher returns.")
    elif stability == "VERY UNSTABLE":
        tips.append("The market is extremely unstable! Be prepared for rapid price changes, trade carefully.")

    return tips if tips else ["No trading tips available."]

def show_loading_screen():
    loading_label = tk.Label(root, text="Fetching data, please wait...", font=("Arial", 14), fg="white", bg="black")
    loading_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

    progress_bar = ttk.Progressbar(root, length=200, mode='indeterminate')
    progress_bar.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
    progress_bar.start()

    return loading_label, progress_bar

def hide_loading_screen(loading_label, progress_bar):
    loading_label.destroy()
    progress_bar.destroy()

def open_donation_link():
    webbrowser.open("https://www.roblox.com/games/98354037145737/Donations-Place-Creature-of-Sonaria-Fetcher")

root = tk.Tk()
root.title("Creature Value Fetcher")
root.geometry("800x600")

canvas = tk.Canvas(root, width=800, height=600, bg="black")
canvas.pack(fill="both", expand=True)
stars = []

for _ in range(50):
    x, y = random.randint(0, 800), random.randint(0, 600)
    star = canvas.create_oval(x, y, x + 2, y + 2, fill="white", outline="")
    stars.append(star)

def animate_stars():
    for star in stars:
        x1, y1, x2, y2 = canvas.coords(star)
        canvas.move(star, 0, 1)
        if y1 > 600:
            canvas.move(star, 0, -600)
    canvas.after(50, animate_stars)

animate_stars()

entry_frame = tk.Frame(root, bg="black")
entry_frame.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

entry_label = tk.Label(entry_frame, text="Enter Creature Name:", font=("Arial", 14), fg="white", bg="black")
entry_label.pack(side=tk.LEFT, padx=5)

entry = ttk.Combobox(entry_frame, width=30, font=("Arial", 14))
entry.pack(side=tk.LEFT, padx=5)

search_button = tk.Button(entry_frame, text="Search", command=display_results, font=("Arial", 14), bg="#4CAF50", fg="white")
search_button.pack(side=tk.LEFT, padx=5)

results_frame = tk.Frame(root, bg="black")
results_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

value_label = tk.Label(results_frame, text="Creature Values:", font=("Arial", 14), fg="white", bg="black")
value_label.grid(row=0, column=0, pady=5, sticky="e")
value_text = tk.StringVar(value="Results will be displayed here.")
value_entry = tk.Entry(results_frame, textvariable=value_text, font=("Arial", 14), state="readonly", readonlybackground="black", fg="white", width=30, borderwidth=0)
value_entry.grid(row=0, column=1, pady=5, sticky="w")

demand_label = tk.Label(results_frame, text="Player Demand:", font=("Arial", 14), fg="white", bg="black")
demand_label.grid(row=1, column=0, pady=5, sticky="e")
demand_text = tk.StringVar(value="N/A")
demand_entry = tk.Entry(results_frame, textvariable=demand_text, font=("Arial", 14), state="readonly", readonlybackground="black", fg="white", width=30, borderwidth=0)
demand_entry.grid(row=1, column=1, pady=5, sticky="w")

stability_label = tk.Label(results_frame, text="Price Stability:", font=("Arial", 14), fg="white", bg="black")
stability_label.grid(row=2, column=0, pady=5, sticky="e")
stability_text = tk.StringVar(value="N/A")
stability_entry = tk.Entry(results_frame, textvariable=stability_text, font=("Arial", 14), state="readonly", readonlybackground="black", fg="white", width=30, borderwidth=0)
stability_entry.grid(row=2, column=1, pady=5, sticky="w")

tips_label = tk.Label(results_frame, text="Trading Tips:", font=("Arial", 14), fg="white", bg="black")
tips_label.grid(row=3, column=0, pady=5, sticky="e")
tips_entry = tk.Text(results_frame, height=5, width=50, font=("Arial", 14), wrap=tk.WORD, bg="black", fg="white", bd=0)
tips_entry.grid(row=3, column=1, pady=5, sticky="w")
tips_entry.config(state=tk.DISABLED)

last_update_label = tk.Label(results_frame, text="Last Update: N/A", font=("Arial", 14), fg="white", bg="black")
last_update_label.grid(row=4, column=1, pady=5, sticky="w")

donation_button = tk.Button(root, text="Support the Project! ❤️", font=("Arial", 14), bg="#FFD700", fg="black", command=open_donation_link)
donation_button.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

update_autocomplete_suggestions()

root.mainloop()
