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

    async def get_info(self, session, url):
        user_agent_str = self.user_agent.random
        #print(f"User-Agent for aiohttp request: {user_agent_str}")
        async with session.get(url, headers={'User-Agent': user_agent_str}) as response:
            try:
                response.raise_for_status()

                try:
                    # Open the website with Selenium
                    self.driver.get(url)

                    # Waiting for the first element job to load [Max. 10 seconds]
                    WebDriverWait(self.driver, 10).until(
                        # EC.presence_of_element_located((By.XPATH, '//*[@id="rso"]'))
                        EC.presence_of_element_located((By.XPATH, '//*[@id="rso"]/div/div/div/div/div[2]/div/div/div/div/infinity-scrolling/div[1]/div[1]/div/div[1]'))
                    )
                except Exception as e:
                    print(f"*** (47) Timeout waiting to load the first job of the page: {e}")
                    return

                #print('...(79) Collecting jobs')

                # Clicking 10 jobs to open their description
                for i in range(10):
                    job_elements = self.driver.find_elements(By.XPATH, '//*[@class="L5NwLd"]')
                    if i < len(job_elements):
                        job_elements[i].click()
                        time.sleep(2)
                        #print(f'...(55) Job #{i+1}/10 clicked')

                        try:  # Extracting job details using Selenium
                            title = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[2]/div[2]/div/div[2]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[2]/h1').text.strip()
                            #print(f'Title: {title}')
                        except Exception as e:
                            title = 'Error'
                            #print(f'Error on title: {e}')

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
                        except Exception as e:
                            salary = 'Not mentioned'

                        try:
                            job_type = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[@class="A8mJGd NDuZHe"]/div[@class="LrPjRb"]/div/div[@class="BIB1wf EIehLd fHE6De"]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[@class="JmvMcb"]/div[@class="mLdNec"]/div[not(contains(., "MXN")) and not(contains(., "hace")) and not(contains(., "título"))]/span[@class="RcZtZb"]').text.strip()
                            if job_type == '': 
                                job_type = 'Not mentioned'
                        except Exception as e:
                            job_type = 'Not mentioned'

                        try:
                            published = self.driver.find_element(By.XPATH, '//*[@id="Sva75c"]/div[@class="A8mJGd NDuZHe"]/div[@class="LrPjRb"]/div/div[@class="BIB1wf EIehLd fHE6De"]/c-wiz/div/c-wiz[1]/c-wiz/c-wiz/div[@class="JmvMcb"]/div[@class="mLdNec"]/div[(contains(., "hace"))]/span[@class="RcZtZb"]').text.strip()
                        except Exception as e:
                            published = f'Weeks ago: {e}'

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

                        # Saving the job information
                        self.jobs[title] = {
                            'Company': company,
                            'Place': place,
                            'Salary': salary,
                            'Type': job_type,
                            'Published': published,
                            'URLs': job_urls,
                            'Description': description
                        }

            except aiohttp.ClientResponseError as e:
                print(f"*** (137) Failed to access the page. ClientResponseError: {e}")

    async def get_all_jobs(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
            tasks = []
            skills_pairs = [self.skills[i:i + 2] for i in range(0, len(self.skills), 2)]
            for pair in skills_pairs:
                queries = ' '.join(pair)
                if self.place:
                    queries += f" {self.place}"
                if self.job_type:
                    queries += f" {self.job_type}"

                encoded_queries = urllib.parse.quote(queries)
                url = f'https://www.google.com/search?&udm=8&q={encoded_queries}&jbr=sep:0'
                #print(url)
                tasks.append(self.get_info(session, url))
            await asyncio.gather(*tasks)

    def save_to_json(self, output_file='jobs.json'):
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(self.jobs, json_file, indent=4, ensure_ascii=False)

async def scraper_main(skills, place, job_type):
    scraper = JobScraper(skills, place, job_type)
    await scraper.get_all_jobs()
    scraper.driver.quit()
    return scraper.jobs

# ------------------ T E S T I N G -----------
if __name__ == "__main__":
    inicio = time.time()
    print('Loading...')

    # User parameters [skills - type - place]:
    qskills = ['python', 'sql', 'java', 'c++', 'javascript', 'html', 'css', 'react', 'nodejs', 'docker']
    qplace = 'CDMX'    #City of the job [example: CDMX] , if you don't insert an option the scraper would show the trending jobs.
    qtype = 'Tiempo completo' #Type of job ['Medio Tiempo' or 'Tiempo completo'], if you don't insert an option the scraper would show the trending jobs.

    asyncio.run(main(skills=qskills, place=qplace, job_type=qtype))

    fin = time.time()
    print(f"Complete: {fin - inicio} seconds")


    '''
    
NEW VERSION OF THE SCRAPER:
    -Divided Skills into Pairs: The skills list is split into pairs, and each pair is used to build a search query.
    -Asynchronous Scraping: The script asynchronously handles multiple queries using asyncio.gather.
    -Error Handling: The script attempts to scrape up to 10 job listings per pair and handles cases where fewer than 10 jobs are available.
    
    '''
