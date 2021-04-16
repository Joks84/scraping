from django.views import generic
from .models import Jobs, Company
from django.db.models import Q


class Homepage(generic.ListView):
    # A ListView for all the jobs from the database.
    template_name = "django_jobs/homepage.html"

    def get_queryset(self):
        return Jobs.objects.all()


class CompanyDetailView(generic.DetailView):
    # A DetailView for each company we have in our database and jobs related to the company.
    template_name = "django_jobs/company_detail.html"
    queryset = Company.objects.prefetch_related("jobs_set")


class SearchViewSet(generic.ListView):
    # Adding a search view for search function.
    model = Jobs
    template_name = "django_jobs/search_results.html"

    def get_queryset(self):
        # Filtering the queryset based on a user's input.
        queryset = self.request.GET.get('query')
        # Searching for both, job titles and company names.
        object_list = Jobs.objects.filter(Q(title__contains=queryset) | Q(company__name__contains=queryset))
        if object_list:
            return object_list