from django.test import TestCase
from django.test.client import Client
from django_jobs.models import Jobs, Company
import datetime


class TestViewsets(TestCase):
    """
    Test Case for testing viewsets we have.
    We are checking the responses, templates, results based on created models.
    """
    def setUp(self):
        # Setting the Client so we can access the response.
        self.client = Client()

    def test_homepage(self):
        # Testing the Homepage viewset.
        # Setting up the Jobs and Company models so we can see if we have the data we need in the response.
        company = Company.objects.create(name="Company One")
        job = Jobs.objects.create(
            title="Job One",
            company=company,
            date=datetime.date(2021, 4, 27),
            link="https://some-link-to-job.com",
        )
        response = self.client.get('')

        # Checking the status code, template used and content of the response.
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"{company.name}".encode(), response.content)
        self.assertIn(f"{job.title}".encode(), response.content)
        self.assertIn(f"{job.link}".encode(), response.content)
        self.assertIn(f"{job.date:%B %d, %Y}".encode(), response.content)
        self.assertTemplateUsed(response, "django_jobs/homepage.html")

    def test_company_detail(self):
        # Testing Company Detail Viewset.
        # Setting up the the few companies so we can see what response is returning and what is not returning.

        # Company No 1.
        company_1 = Company.objects.create(name="Company One")
        job_1 = Jobs.objects.create(
            title="Job One",
            company=company_1,
            date=datetime.date(2021, 4, 15),
            link="https://some-link-one",
        )

        # Testing Company No 1.
        response = self.client.get(f"/{company_1.id}/")

        # Checking the status code, template used, and content of the response.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "django_jobs/company_detail.html")
        self.assertIn(f"{company_1.name}".encode(), response.content)
        self.assertIn(f"{job_1.title}".encode(), response.content)
        self.assertIn(f"{job_1.date:%B %d, %Y}".encode(), response.content)
        self.assertIn(f"{job_1.link}".encode(), response.content)

        # Company No 2.
        company_2 = Company.objects.create(name="Company Two")
        job_2 = Jobs.objects.create(
            title="Job Two",
            company=company_2,
            date=datetime.date(2021, 3, 17),
            link="https://some-link-two",
        )
        job_3 = Jobs.objects.create(
            title="Job Three",
            company=company_2,
            date=datetime.date(2021, 3, 19),
            link="https://some-link-three",
        )

        # Testing Company No 2.
        response = self.client.get(f"/{company_2.id}/")

        # Checking the status code, template used, and content of the response.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "django_jobs/company_detail.html")
        # Check if both job_2 and job_3 are in response content.
        self.assertIn(f"{company_2.name}".encode(), response.content)
        self.assertIn(f"{job_2.title}".encode(), response.content)
        self.assertIn(f"{job_2.date:%B %d, %Y}".encode(), response.content)
        self.assertIn(f"{job_2.link}".encode(), response.content)

        self.assertIn(f"{company_2.name}".encode(), response.content)
        self.assertIn(f"{job_3.title}".encode(), response.content)
        self.assertIn(f"{job_3.date:%B %d, %Y}".encode(), response.content)
        self.assertIn(f"{job_3.link}".encode(), response.content)

        # Check in there is no information about Company No 1. on the page.
        self.assertNotIn(f"{company_1.name}".encode(), response.content)
        self.assertNotIn(f"{job_1.title}".encode(), response.content)
        self.assertNotIn(f"{job_1.link}".encode(), response.content)
        self.assertNotIn(f"{job_1.date:%B %d, %Y}".encode(), response.content)

        # Company No 4.
        company_4 = Company.objects.create(name="Company Three")
        job_4 = Jobs.objects.create(
            title="Job Four",
            company=company_4,
            date=datetime.date(2021, 3, 20),
            link="https://another-link",
        )
        # Testing Company No 4.
        response = self.client.get(f"/{company_4.id}/")

        # Checking the status code, template used, and content of the response.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "django_jobs/company_detail.html")
        # Check if  job_4 in response content.
        self.assertIn(f"{company_4.name}".encode(), response.content)
        self.assertIn(f"{job_4.title}".encode(), response.content)
        self.assertIn(f"{job_4.date:%B %d, %Y}".encode(), response.content)
        self.assertIn(f"{job_4.link}".encode(), response.content)

        # Checking that none of information related to Company 1 and Company 2 are in the result page.
        # Company 1.
        self.assertNotIn(f"{company_1.name}".encode(), response.content)
        self.assertNotIn(f"{job_1.title}".encode(), response.content)
        self.assertNotIn(f"{job_1.link}".encode(), response.content)
        self.assertNotIn(f"{job_1.date:%B %d, %Y}".encode(), response.content)
        # Company 2, job 2.
        self.assertNotIn(f"{company_2.name}".encode(), response.content)
        self.assertNotIn(f"{job_2.title}".encode(), response.content)
        self.assertNotIn(f"{job_2.link}".encode(), response.content)
        self.assertNotIn(f"{job_2.date:%B %d, %Y}".encode(), response.content)
        # Company 2, job 3.
        self.assertNotIn(f"{company_2.name}".encode(), response.content)
        self.assertNotIn(f"{job_3.title}".encode(), response.content)
        self.assertNotIn(f"{job_3.link}".encode(), response.content)
        self.assertNotIn(f"{job_3.date:%B %d, %Y}".encode(), response.content)

    def test_search_viewset(self):
        # Testing the search view which will show us the results of our query.
        # Setting companies and jobs with different names to see if queryset is filtered properly.
        # Company No 1.
        company_1 = Company.objects.create(name="Company One")
        job_1 = Jobs.objects.create(
            title="Job One",
            company=company_1,
            date=datetime.date(2021, 4, 15),
            link="https://some-link-one",
        )
        # Company No 2.
        company_2 = Company.objects.create(name="Company Two")
        job_2 = Jobs.objects.create(
            title="One job",
            company=company_2,
            date=datetime.date(2021, 3, 17),
            link="https://anotherlink",
        )
        # Company No 3.
        company_3 = Company.objects.create(name="Company Three")
        job_3 = Jobs.objects.create(
            title="Job Three",
            company=company_3,
            date=datetime.date(2021, 3, 21),
            link="https://third-link",
        )

        # Testing responses with different queries.
        # If the query is 'one', we should get the data from first and second company, but not the third.
        response = self.client.get('/search_jobs/', {'query': 'one'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "django_jobs/search_results.html")
        self.assertIn(f"{company_1.name}".encode(), response.content)
        self.assertIn(f"{job_1.title}".encode(), response.content)
        self.assertIn(f"{job_1.link}".encode(), response.content)
        self.assertIn(f"{job_1.date:%B %d, %Y}".encode(), response.content)

        self.assertIn(f"{company_2.name}".encode(), response.content)
        self.assertIn(f"{job_2.title}".encode(), response.content)
        self.assertIn(f"{job_2.link}".encode(), response.content)
        self.assertIn(f"{job_2.date:%B %d, %Y}".encode(), response.content)

        self.assertNotIn(f"{company_3.name}".encode(), response.content)
        self.assertNotIn(f"{job_3.title}".encode(), response.content)
        self.assertNotIn(f"{job_3.link}".encode(), response.content)
        self.assertNotIn(f"{job_3.date:%B %d, %Y}".encode(), response.content)

        # If the query is 'company three', we should get the data from the third company,
        # but not for the first and second.
        response = self.client.get('/search_jobs/', {'query': 'company three'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "django_jobs/search_results.html")
        self.assertIn(f"{company_3.name}".encode(), response.content)
        self.assertIn(f"{job_3.title}".encode(), response.content)
        self.assertIn(f"{job_3.link}".encode(), response.content)
        self.assertIn(f"{job_3.date:%B %d, %Y}".encode(), response.content)

        self.assertNotIn(f"{company_2.name}".encode(), response.content)
        self.assertNotIn(f"{job_2.title}".encode(), response.content)
        self.assertNotIn(f"{job_2.link}".encode(), response.content)
        self.assertNotIn(f"{job_2.date:%B %d, %Y}".encode(), response.content)

        self.assertNotIn(f"{company_1.name}".encode(), response.content)
        self.assertNotIn(f"{job_1.title}".encode(), response.content)
        self.assertNotIn(f"{job_1.link}".encode(), response.content)
        self.assertNotIn(f"{job_1.date:%B %d, %Y}".encode(), response.content)

        # If the query is 'company', we should get the data from all three companies/jobs.
        response = self.client.get('/search_jobs/', {'query': 'company'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "django_jobs/search_results.html")
        self.assertIn(f"{company_3.name}".encode(), response.content)
        self.assertIn(f"{job_3.title}".encode(), response.content)
        self.assertIn(f"{job_3.link}".encode(), response.content)
        self.assertIn(f"{job_3.date:%B %d, %Y}".encode(), response.content)

        self.assertIn(f"{company_2.name}".encode(), response.content)
        self.assertIn(f"{job_2.title}".encode(), response.content)
        self.assertIn(f"{job_2.link}".encode(), response.content)
        self.assertIn(f"{job_2.date:%B %d, %Y}".encode(), response.content)

        self.assertIn(f"{company_1.name}".encode(), response.content)
        self.assertIn(f"{job_1.title}".encode(), response.content)
        self.assertIn(f"{job_1.link}".encode(), response.content)
        self.assertIn(f"{job_1.date:%B %d, %Y}".encode(), response.content)