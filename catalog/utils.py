from .models import Book

def generate_report_data(book_name=None, start_date=None, end_date=None, status=None):
  queryset = Book.objects.all()
  if book_name:
    queryset = queryset.filter(name__icontains=book_name)
  if start_date:
    queryset = queryset.filter(date_added__gte=start_date)
  if end_date:
    queryset = queryset.filter(date_added__lte=end_date)
  if status:
    queryset = queryset.filter(status=status)

  report_data = queryset.values_list('status').annotate(count=models.Count('id'))
  report_data = dict(report_data)
  return report_data
