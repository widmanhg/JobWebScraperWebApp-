import unittest
import asyncio
import json
import aiohttp
from scraper import JobScraper

class TestJobScraper(unittest.TestCase):
    async def run_scraper(self, skills, place, job_type):
        scraper = JobScraper(skills, place, job_type)
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector()) as session:
            queries = f'{skills},{place}'
            url = f'https://www.google.com/search?q={queries.replace(",", "+").replace(" ", "+")}&oq=trab&ibp=htl;jobs&sa=X#htivrt=jobs&fpstate=tldetail&htichips=employment_type:{job_type}&htischips=employment_type;{job_type}'
            
            # Print the url request
            print(f"Request URL: {url}")

            try:
                await scraper.get_info(session, url)
            except Exception as e:
                print(f"Error during scraping: {e}")

        scraper.driver.quit()
        return scraper.jobs # Run the scraper

    def test_get_info(self):
        skills = 'python, java, C++'
        place = "CDMX"
        job_type = "FULLTIME"

        jobs = asyncio.run(self.run_scraper(skills, place, job_type))

        # Saves the data into a json
        with open('jobs_data.json', 'w', encoding='utf-8') as file:
            json.dump(jobs, file, indent=4, ensure_ascii=False)

        # Check if the data is saved and if there is data provided
        self.assertIsInstance(jobs, dict)
        self.assertTrue(len(jobs) > 0, "No jobs found")

if __name__ == '__main__':
    unittest.main()
