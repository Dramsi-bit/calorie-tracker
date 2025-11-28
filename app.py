from flask import Flask, request,redirect
import sqlite3 
from datetime import date,timedelta
# Database setup function
def init_db():
    conn = sqlite3.connect('calorie_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            calories INTEGER NOT NULL,
            date TEXT DEFAULT (date('now'))
        )
    ''')
    conn.commit()
    conn.close()

def get_all_ingredients(date_filter):
    conn = sqlite3.connect('calorie_tracker.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingredients WHERE date = ?", (date_filter,))
    results = cursor.fetchall()
    conn.close()
    return results

def add_ingredient(name, calories,date_value):
    conn = sqlite3.connect("calorie_tracker.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO ingredients (name, calories,date) VALUES (?, ?, ?)", (name, calories, date_value))
    conn.commit()
    conn.close()

def clear_all_ingredients():
    conn = sqlite3.connect("calorie_tracker.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ingredients")
    conn.commit()
    conn.close()

def delete_ingredient(ingredient_id):
    conn = sqlite3.connect("calorie_tracker.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ingredients WHERE id = ?", (ingredient_id,))
    conn.commit()
    conn.close()

# Initialize database
init_db()

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    error = ""
    success = ""
    today = date.today()


    dates = []
    for i in range(7):
        day = today - timedelta(days=i)
        dates.append(str(day))
    # Before the HTML, build the options
    selected = request.args.get('test', str(today))
    
    dropdown_options = ""
    for i, day in enumerate(dates):
        
        if i == 0:
            label = "Today"
        elif i == 1:
            label = "Yesterday"
        else:
            label = f"{i} days ago"
        
        dropdown_options += f'<option value="{day}" {'selected' if selected == day else ''}>{label}</option>'

    dropdown_options += f'<option value="summary" {'selected' if selected == "summary" else ''}>Last 7 Days Summary</option>'
    
    if request.method == "POST":
        if "action" in request.form:
            clear_all_ingredients()
            return redirect("/")
        elif "delete_id" in request.form:
        # Delete specific ingredient
            ingredient_id = request.form["delete_id"]
            delete_ingredient(ingredient_id)
            return redirect("/")
        else:
            ingredient = request.form["ingredient_name"]
            calories = request.form["calories"]

            if ingredient and calories:
                try:
                    calories_int = int(calories)
            
                    if calories_int <= 0:
                        error = "Calories must be a positive number!"
                    else:
                        add_ingredient(ingredient, calories_int,str(today))
                        success = "Ingredient added succesfully!"
                        return redirect("/")
                except ValueError:
                    error = "Calories must be a valid number!"
            else:
                error = "Please fill in both fields!"
    
    # Get data from database
    ingredients = get_all_ingredients(selected)

    if selected == "summary":
        all_ingredients = []
        for day in dates:
            day_ingredients = get_all_ingredients(day)
            all_ingredients.extend(day_ingredients)
        # Group ingredients by date
        daily_data = {}
        for ing in all_ingredients:
            ing_date = ing[3]  # Date is at index 3
            if ing_date not in daily_data:
                daily_data[ing_date] = []
            daily_data[ing_date].append(ing)
        print(f"Daily data: {daily_data}")  
        summary_html = ""
        week_total = 0

        for day_date, ingredients_list in daily_data.items():
            # Calculate total for this day
            day_total = 0
            for ing in ingredients_list:
                day_total += ing[2]  # What goes here?
                
            # Add to week total
            week_total += day_total
            
            # Build HTML for this day
            summary_html += f"<p>{day_date}: {day_total} calories</p>"
        summary_html += f"<p>Week Total: {week_total} calories</p>"
        summary_html += f"<p>Daily Average: {round(week_total)/7} calories</p>"    
        ingredients_html = summary_html
        total_calories = week_total  # We'll calculate this properly next
    else:
        ingredients_html = ""
        total_calories = 0
        for ing in ingredients:
            ingredients_html += f"""
                <div class="ingredient-item">
                    <span class="ingredient-name">{ing[1]}</span>
                    <div>
                        <span class="ingredient-calories">{ing[2]} cal</span>
                        <span class="ingredient-date">{ing[3]}</span>
                        <form method="POST" action="/" style="display: inline;">
                            <input type="hidden" name="delete_id" value="{ing[0]}">
                            <button type="submit" class="delete-btn">Delete</button>
                        </form>
                    </div>
                </div>
            """
            total_calories += ing[2]
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <title>Calorie Tracker</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background-color: #f5f5f5;
            }}

        h1 {{
            color: #2c3e50;
            text-align: center;
                }}

        h2 {{
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 5px;
        }}

        form {{
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}

        input[type="text"], input[type="number"] {{
            width: 100%;
            padding: 8px;
            margin: 5px 0 15px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }}

        button, input[type="submit"] {{
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }}

        button:hover, input[type="submit"]:hover {{
            background-color: #2980b9;

        
        }}
        .delete-btn {{
            background-color: #e74c3c;  /* Normal: bright red */
        }}

        .delete-btn:hover {{
            background-color: #c0392b;  /* Hover: darker red */
        }}

        .alert {{
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
            border: 1px solid transparent;
        }}

        .alert-error {{
            background-color: #f8d7da;
            color: #721c24;
            border-color: #f5c6cb;
        }}

        .alert-success {{
            background-color: #d4edda;
            color: #155724;
            border-color: #c3e6cb;
        }}
        .ingredient-item {{
            background-color: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .ingredient-name {{
            font-weight: bold;
            color: #2c3e50;
        }}

        .ingredient-calories {{
            color: #7f8c8d;
            margin-right: 15px;
        }}
        
        .ingredient-date{{
            color: #95a5a6;
            font-size: 0.9em;
            margin-right: 15px;
        }}
    </style>
</head>
<body>
    <h1>Calorie Tracker</h1>
    <p>Track your meals and stay healthy</p>
    <form method="GET" action="/">
    <select name="test" onchange="this.form.submit()">
        {dropdown_options}
    </select>
    </form>
    <form method="POST" action="/">
        <label>Ingredient Name:</label>
        <input type="text" name="ingredient_name">
        <br>
        
        <label>Calories:</label>
        <input type="number" name="calories">
        <br><br>
        
        <input type="submit" value="Add Ingredient">
    </form>
    <br>
    <form method="POST" action="/">
        <input type="submit" name="action" value="Clear All">
    </form>

    {  '<div class="alert alert-error">' + error + '</div>' if error else ''}
    {  '<div class="alert alert-success">' + success + '</div>' if success else ''}
    <br>
    
    <h2>Ingredients Added:</h2>
    {ingredients_html}

    <h2>Total:</h2>
    {total_calories} calories
</body>
</html>"""



if __name__ == "__main__":
    app.run(debug=True, port = 5001)