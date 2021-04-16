from __future__ import absolute_import, unicode_literals
from celery import shared_task
from bs4 import BeautifulSoup
import requests
import random
import datetime
from .models import Jobs, Company
from django.core.exceptions import ObjectDoesNotExist


headers_list = [
    {  # Firefox/Linux
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:86.0) Gecko/20100101 Firefox/86.0',  # Change
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'If-Modified-Since': 'Fri, 19 Mar 2021 05:07:23 GMT',
        'Cache-Control': 'max-age=0',
    },
    {  # Chrome/Linux
        'authority': 'remote.co',
        'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/89.0.4389.82 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                  'image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-US,en;q=0.9',
    },
]


@shared_task
def scrape_content_from_remote_co():
    """
    With this scraper function, we are scraping content from Remote.co webiste.
    We are using the scraper to extract the following data:
    - Company name;
    - Title/Job opening;
    - Date posted;
    - The final link for applying for a job;
    """

    # The link from which the data is scraped.
    URL = "https://remote.co/remote-jobs/developer/"
    # Used for creating the application link.
    base_url = "https://remote.co"

    # From created headers_list, we are randomly choosing one of the headers for the request.
    headers = random.choice(headers_list)

    # Assigning randomly selected header to requests.
    page = requests.get(URL, headers=headers)

    try:
        soup = BeautifulSoup(page.content, 'html.parser')

        # Searching for the <a> tag which contains all the job results we need.
        results = soup.find_all("a", class_="card m-0 border-left-0 border-right-0 border-top-0 border-bottom")

        for jobs in results:
            # Searching for a content for each job post.
            comp = jobs.find("p", class_="m-0 text-secondary")

            for span in comp("span"):
                # Removing labels we don't need which can be found as <span> tag in another <span> tag.
                # Doing this, we are creating a clean company name.
                if span:
                    # If we have <small> tag within <span> tag, we will extract and remove the data by using
                    # decompose().
                    # Unlike decompose(), extract() method returns the data (but in this case, we don't need it).
                    span.small.decompose()

            # Removing '\xa0' and '|' from html so we can get clean company name to save.
            company = comp.text.replace("\xa0", "").replace("|", "").strip()

            # Extracting the job title from HTML.
            title = jobs.find("span", class_="font-weight-bold larger").text.strip()
            # Extracting full link for job application.
            full_link = f"{base_url}{jobs['href'].strip()}"  # link for applying

            # This particular site has a time stamp in a form of 'hours/days/weeks ago'.
            # Therefore, we want to form a proper date based on a time stamp from the website so we can use
            # the DateField in the Jobs model.
            raw_date = jobs.find('date').text.strip()
            if 'hours' in raw_date:
                date = datetime.datetime.now()
            elif 'days' in raw_date:
                date = datetime.datetime.now() - datetime.timedelta(days=int(raw_date[:2]))
            elif 'week' in raw_date:
                date = datetime.datetime.now() - datetime.timedelta(days=(int(raw_date[0])*7))
            elif 'month' in raw_date:
                date = datetime.datetime.now() - datetime.timedelta(days=(int(raw_date[0])*3))

            # Accessing the company or creating a new company.
            # In both cases, we are using the company name to create a Job Post.
            obj, created = Company.objects.get_or_create(name=company)

            # Creating a Job Post based on extracted data from HTML.
            try:
                if Jobs.objects.get(link=full_link):
                    # If we have a link for the job in our database, we are skipping it because we avoid creating
                    # multiple models for the same job post.
                    pass
            except ObjectDoesNotExist:
                Jobs.objects.create(title=title, company=obj, date=date.date(), link=full_link)

    except Exception as e:
        print(f"The scraping from 'Remote Co' failed. See exception: {e}")


@shared_task
def scrape_weworkremotely():
    """
    We are using this function to scrape the data from WeWorkRemotely website.
    The data we are searching for are:
    - Company;
    - Title/Job opening;
    - Date posted;
    - Final link for applying for a job.
    """

    # The link from which developers jobs_app are being scraped.
    URL = "https://weworkremotely.com/categories/remote-programming-jobs"

    # Base url we are using for creating the link for job application.
    base_url = "https://weworkremotely.com"

    # We randomize headers from headers_list so the website won't detect we are using requests library.
    # And we are avoiding being blocked by the website.
    headers = random.choice(headers_list)

    # Assigning randomly selected header to requests.
    page = requests.get(URL, headers=headers)

    try:
        soup = BeautifulSoup(page.content, 'html.parser')

        # List of results.
        results = soup.find_all("li", class_="feature")

        for result in results:
            # In this for loop, we are searching for: company name, title, application link and the time posted.

            # Depending on a company and a job post itself, there are different number of links which are included in
            # the result variable. Sometimes, there are only one link, and sometimes there are multiple links ("href").
            # Therefore, we are searching for all <a> tags.
            a_tags = result.find_all("a")
            url = a_tags[1]['href']
            full_link = f"{base_url}{url}"

            # Getting the job title name.
            title = result.find("span", class_="title").text.strip()

            # Getting the Company name.
            # result.find_all("span", class_="company") returns a list because there are multiple results with the
            # same class name within <span> tag.
            company_result = result.find_all("span", class_="company")
            # Based on html research, I've discovered that the first result from a list is a name of the Company.
            company = company_result[0].text.strip()

            # Getting the date.
            if result.find("span", class_="date"):
                # Not each job has date posted on this website.
                # If there is, we are cleaning the date data.
                raw_date = result.find("time")["datetime"]
                date = datetime.datetime.strptime(raw_date, "%Y-%m-%dT%H:%M:%SZ").date()
            else:
                # If not, we are adding the job post with today's date.
                date = datetime.date.today()

            # Getting or creating the company we will use while creating the job post.
            obj, created = Company.objects.get_or_create(name=company)

            try:
                # Use link as something that is unique in our database.
                # We are checking if there is a link for application in the database.
                # If there is, we are skipping that result because we already have that job in our database.
                if Jobs.objects.get(link=full_link):
                    pass
            except ObjectDoesNotExist:
                # If there is no such link, we are creating a Job object.
                Jobs.objects.create(title = title, company=obj, date=date, link=full_link)

    except Exception as e:
        print(f"Scraping from 'We Work Remotely' failed. See the Exception: {e}")



@shared_task
def scrape_remotive():
    """
    We are using this function to scrape the data from WeWorkRemotely website.
    The data we are searching for are:
    - Company;
    - Title/Job opening;
    - Date posted;
    - Final link for applying for a job;
    """

    # The url we are using for scraping.
    URL = "https://remotive.io/remote-jobs/software-dev"
    # We use 'base_url' for creating the final link for application.
    base_url = "https://remotive.io/"

    # We are mixing the headers from headers_list so we can cover up tools we are using for web scraping and
    # prevent potential block from the website.
    headers = random.choice(headers_list)

    # Assigning randomly selected headers while we are sending the request to the website.
    page = requests.get(URL, headers=headers)

    try:
        soup = BeautifulSoup(page.content, 'html.parser')

        # Getting the tag we need and which contains the data we want for our models.
        results = soup.find_all("li", class_="tw-cursor-pointer")
        for result in results:
            # From 'raw' variable we can extract 2 things we need: title and the link.
            raw = result.find("a", class_="job-tile-title")
            # Getting the title from a job post.
            title = raw.text.strip()
            # Getting the application link.
            link = f"{base_url}{raw['href']}"

            # Getting the company name.
            company = result.find("span", itemprop="hiringOrganization").text.strip()
            # Getting the post date.
            raw_date = result.find("span", itemprop="datePosted").text.strip()
            date = datetime.datetime.strptime(raw_date, "%Y-%m-%d %H:%M:%S").date()

            # Getting or creating the company we will use while creating the job post.
            obj, created = Company.objects.get_or_create(name=company)

            try:
                # Use link as something that is unique in our database.
                # We are checking if there is a link for application in the database.
                # If there is, we are skipping that result because we already have that job in our database.
                if Jobs.objects.get(link=link):
                    pass
            except ObjectDoesNotExist:
                # If there is no such link, we are creating a Job object.
                Jobs.objects.create(title=title, company=obj, date=date, link=link)

    except Exception as e:
        print(f"Scraping from 'Remotive' failed. See the Exception: {e}")