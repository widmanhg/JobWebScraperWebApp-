from flask import Flask, render_template, request, flash, redirect, url_for, session
import asyncio
from scraper import JobScraper
import aiohttp
import urllib.parse

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
        query_place = location
        query_modes = ', '.join(modes)
        query_skills = ', '.join(technologies + techskills + robotics + embedded + softskills)

        # Checking in terminal if the values were correctly collected.
        print(query_skills)

        # Store user inputs in the session
        session['query_place'] = query_place
        session['query_modes'] = query_modes
        session['query_skills'] = query_skills
        session['scraping_done'] = False

        # Creating an Async function for the scraper to run apart from the web app.
        async def run_scraper():
            global jobs_data
            jobs_data = {}

            async with aiohttp.ClientSession() as aio_session:
                scraper = JobScraper(query_skills, query_place, query_modes)

                # Generar una única URL basada en las habilidades, lugar y modos seleccionados
                queries = query_skills
                if query_place:
                    queries += f" {query_place}"
                if query_modes:
                    queries += f" {query_modes}"

                encoded_queries = urllib.parse.quote(queries)
                url = f'https://www.google.com/search?&udm=8&q={encoded_queries}&jbr=sep:0'
                print(f"Generated URL: {url}")
                
                # Llamar al método get_info con la URL generada
                try:
                    await scraper.get_info(aio_session, url)
                except Exception as e:
                    print(f"Error during scraping: {e}")

            scraper.driver.quit()

            # Collect the jobs data
            jobs_data = scraper.jobs

            # Printing the found Jobs by the scraper.
            print("Jobs found:")
            for job_title, job_details in jobs_data.items():
                print(f"Title: {job_title}, Details: {job_details}")

            # Mark scraping as done in the session
            session['scraping_done'] = True

        # Running the Async function with asyncio.run to let it manage the loop of events.
        try:
            asyncio.run(run_scraper())
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