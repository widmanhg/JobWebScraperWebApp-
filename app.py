from flask import Flask, render_template, request, flash, redirect, url_for, session
import asyncio
import time
from scraper import scraper_main

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Global variable to save the Jobs founded.
jobs_data = {}

@app.route("/")
def main():
    return render_template("welcome.html")

@app.route("/welcome")
def welcome():
    return render_template("welcome.html")

# Main route of the web site/app.
@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == 'POST':
        # Getting all the values selected by the user.
        location = request.form.get('location')
        modes = request.form.getlist('mode')
        technologies = request.form.getlist('technologies')
        techskills = request.form.getlist('techskills')
        robotics = request.form.getlist('robotics')
        embedded = request.form.getlist('embedded')
        softskills = request.form.getlist('softskills')
        
        # Check if at least one of the checkbox categories has been selected.
        if not (modes or technologies or techskills or robotics or embedded or softskills):
            flash('Please select at least one checkbox from any category.')
            # Redirect back to the 'home' page
            return redirect(url_for('home'))
        
        # Placing together the values selected by the user to start scraping.
        query_place = str(location)
        query_modes = ', '.join(modes)
        raw_skills = ', '.join(technologies + techskills + robotics + embedded + softskills)
        query_skills = raw_skills.split(', ')

        # Checking in terminal if the values were correctly collected.
        print(query_place)
        print(type(query_place))
        print(query_modes)
        print(type(query_modes))
        print(query_skills)
        print(type(query_skills))

        # Store user inputs in the session
        session['query_place'] = query_place
        session['query_modes'] = query_modes
        session['query_skills'] = query_skills
        session['scraping_done'] = False

        # Running the Async function with asyncio.run to let it manage the loop of events.
        try:
            global jobs_data

            inicio = time.time()
            print('Loading...')

            jobs_data = asyncio.run(scraper_main(skills=query_skills, place=query_place, job_type=query_modes))

            fin = time.time()
            (f"Complete: {fin - inicio} seconds")

        except Exception as e:
            print(f"Error running the scraper: {e}")
            flash('An error occurred during the scraping process. Please try again.')

        # Rendering the main html template with the scraped jobs in the metadata for visualization.
        return render_template("main.html", jobs=jobs_data)
    
    elif request.method == 'GET':
        # Check if scraping has already been done
        if session.get('scraping_done'):
            # Retrieve data from session if available
            query_place = session.get('query_place')
            query_modes = session.get('query_modes')
            query_skills = session.get('query_skills')

            # Rendering the main html template with the scraped jobs in the metadata for visualization.
            return render_template("main.html", jobs=jobs_data)
    
    # Rendering the main html template by default.
    return render_template("main.html")

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/acknow")
def acknow():
    return render_template("acknow.html")

if __name__ == "__main__":
    app.run(debug=True)