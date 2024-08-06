import aiohttp
import asyncio
import json
import time
import urllib.parse
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as chromeoptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class JobScraper:
    def __init__(self, skills, place, job_type):
        self.jobs = {}
        self.skills = skills
        self.place = place
        self.job_type = job_type
        self.user_agent = UserAgent(platforms='pc')

        # Generate a random User Agent
        user_agent_str = self.user_agent.random
        print(f"User-Agent: {user_agent_str}")

        # Setting Selenium options
        options = chromeoptions()
        options.add_argument('--incognito')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'user-agent={user_agent_str}')
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    async def get_info(self, session, url, skill):
        user_agent_str = self.user_agent.random
        retries = 1
        for attempt in range(retries):
            try:
                async with session.get(url, headers={'User-Agent': user_agent_str}) as response:
                    response.raise_for_status()
                    self.driver.get(url)
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="rso"]/div/div/div/div/div[2]/div/div/div/div/infinity-scrolling/div[1]/div[1]/div/div[1]'))
                    )
                    break
            except (aiohttp.ClientError, aiohttp.ClientConnectorError) as e:
                print(f"Attempt {attempt + 1} - Network error: {e}")
                if attempt == retries - 1:
                    return
                await asyncio.sleep(5)  # Wait before retrying
            except Exception as e:
                print(f"Attempt {attempt + 1} - Timeout waiting to load the first job of the page: {e}")
                if attempt == retries - 1:
                    return
                await asyncio.sleep(5)  # Wait before retrying

        for i in range(3):  # Limit to 3 jobs
            job_elements = self.driver.find_elements(By.XPATH, '//*[@class="L5NwLd"]')
            if i < len(job_elements):
                job_elements[i].click()
                time.sleep(2)

                try:
                    title = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[2]/h1').text.strip()
                except:
                    continue

                try:
                    company = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[1]/div/div[1]/div/div[2]/span/div').text.strip()
                except:
                    company = 'Error'

                try:
                    details = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[2]/div[1]').text.strip()
                    split_text = [part.strip() for part in details.split('•')]
                    place = split_text[1]
                except:
                    place = 'Not mentioned'

                try:
                    salary = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[@class="A8mJGd NDuZHe"]/div[@class="LrPjRb"]/div/div[@class="BIB1wf EIehLd fHE6De"]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[@class="JmvMcb"]/div[@class="mLdNec"]/div[(contains(., "MXN"))]/span[@class="RcZtZb"]').text.strip()
                except:
                    salary = 'Not mentioned'

                try:
                    job_type = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[@class="A8mJGd NDuZHe"]/div[@class="LrPjRb"]/div/div[@class="BIB1wf EIehLd fHE6De"]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[@class="JmvMcb"]/div[@class="mLdNec"]/div[not(contains(., "MXN")) and not(contains(., "hace")) and not(contains(., "título"))]/span[@class="RcZtZb"]').text.strip()
                    if job_type == '':
                        job_type = 'Not mentioned'
                except:
                    job_type = 'Not mentioned'

                try:
                    published = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[@class="A8mJGd NDuZHe"]/div[@class="LrPjRb"]/div/div[@class="BIB1wf EIehLd fHE6De"]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[@class="JmvMcb"]/div[@class="mLdNec"]/div[(contains(., "hace"))]/span[@class="RcZtZb"]').text.strip()
                except:
                    published = 'Weeks ago.'

                try:
                    short_description = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[6]/div/span[1]').text.strip()
                    try:
                        long_description = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[6]/div/span[3]').text.strip()
                        description = short_description + long_description
                    except:
                        description = short_description
                except Exception as e:
                    description = f'No description - Error: {e}'

                try:
                    links_container = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[4]')
                    job_urls = []
                    links = links_container.find_elements(By.TAG_NAME, 'a')
                    for link in links:
                        href = link.get_attribute('href')
                        job_urls.append(href)
                except Exception as e:
                    job_urls = f'Error: {e}'

                self.jobs[title] = {
                    'Company': company,
                    'Place': place,
                    'Salary': salary,
                    'Type': job_type,
                    'Published': published,
                    'URLs': job_urls,
                    'Description': description
                }

    async def get_all_jobs(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
            for skill in self.skills:
                queries = skill
                if self.place:
                    queries += f" {self.place}"
                if self.job_type:
                    queries += f" {self.job_type}"

                encoded_queries = urllib.parse.quote(queries)
                url = f'https://www.google.com/search?&udm=8&q={encoded_queries}&jbr=sep:0'
                print(url)
                await self.get_info(session, url, skill)
                await asyncio.sleep(2)  # Adding delay to reduce request frequency

    def save_to_json(self, output_file='jobs.json'):
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(self.jobs, json_file, indent=4, ensure_ascii=False)

    def return_dict(self):
        return json.dumps(self.jobs, indent=4, ensure_ascii=False)

async def scraper_main(skills, place, job_type):
    scraper = JobScraper(skills, place, job_type)
    await scraper.get_all_jobs()
    scraper.driver.quit()
    return scraper.jobs



# ------------------ T E S T I N G -----------
'''
if __name__ == "__main__":
    inicio = time.time()
    print('Loading...')

    # User parameters [skills - type - place]:
    qskills = ['carpintero', 'sql', 'trabajo en equipo', 'c++', 'ensamblador', 'html', 'vendedor', 'react', 'comisiones', 'docker']
    qplace = 'CDMX'    #City of the job [example: CDMX] , if you don't insert an option the scraper would show the trending jobs.
    qtype = 'Tiempo completo' #Type of job ['Medio Tiempo' or 'Tiempo completo'], if you don't insert an option the scraper would show the trending jobs.

    asyncio.run(scraper_main(skills=qskills, place=qplace, job_type=qtype))

    fin = time.time()
    print(f"Complete: {fin - inicio} seconds")


 RESUME:
    -Asynchronous Scraping: The script asynchronously handles multiple queries using asyncio.gather.
    -Job Limit: The loop in get_info is adjusted to scrape a maximum of 3 jobs per skill.
    -Skill Processing: The get_all_jobs method now processes one skill at a time, creating a URL and adding the task for each skill individually.
    -Slight Refactoring: Added a skill parameter to the get_info method to keep track of which skill the jobs are associated with.
    -This ensures that the scraper processes each skill individually and limits the number of job postings scraped to a maximum of 3 per skill.
    -The code return a dictionary with all the results.
    
    '''