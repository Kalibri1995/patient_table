import datetime

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from .models import Modalities, Studies
import names
import random
from datetime import timedelta
import uuid


def random_date(start, end):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timedelta(seconds=random_second)


def filter_studies(studies, query, birthdate_order, birthdate_before, birthdate_after,
                   study_order, study_before, study_after, modality_order,
                   patient_order, uuid_order):
    if query:
        studies = studies.filter(
            Q(patient_fio__icontains=query) |
            Q(study_uid__icontains=query) |
            Q(study_date__icontains=query) |
            Q(study_modality__name__icontains=query)
        )

    if birthdate_order == "asc":
        studies = studies.order_by('patient_birthdate')
    elif birthdate_order == "desc":
        studies = studies.order_by('-patient_birthdate')

    if study_order == "asc":
        studies = studies.order_by('study_date')
    elif study_order == "desc":
        studies = studies.order_by('-study_date')

    if birthdate_before:
        studies = studies.filter(patient_birthdate__lte=birthdate_before)

    if birthdate_after:
        studies = studies.filter(patient_birthdate__gte=birthdate_after)

    if study_before:
        studies = studies.filter(study_date__lte=study_before)

    if study_after:
        studies = studies.filter(study_date__gte=study_after)

    if modality_order:
        studies = studies.filter(study_modality__name=modality_order)

    if patient_order == 'alphabet':
        studies = studies.order_by('patient_fio')
    elif patient_order == 'reverse_alphabet':
        studies = studies.order_by('-patient_fio')

    if uuid_order == 'alphabet':
        studies = studies.order_by('study_uid')
    elif uuid_order == 'reverse_alphabet':
        studies = studies.order_by('-study_uid')

    return studies


def home(request):
    try:
        unique_modalities = Modalities.objects.values_list('name', flat=True).distinct()
        studies = Studies.objects.all()

        items_per_page = int(request.GET.get('items_per_page', 10))
        page_number = request.GET.get('page', '')
        query = request.GET.get('query', '')
        birthdate_order = request.GET.get('birthdate_order', '')
        birthdate_before = request.GET.get('birthdate_before', '')
        birthdate_after = request.GET.get('birthdate_after', '')
        study_order = request.GET.get('study_order', '')
        study_before = request.GET.get('study_before', '')
        study_after = request.GET.get('study_after', '')
        modality_order = request.GET.get('modality_order', '')
        patient_order = request.GET.get('patient_order', '')
        uuid_order = request.GET.get('uuid_order', '')

        studies = filter_studies(studies, query, birthdate_order, birthdate_before, birthdate_after,
                                 study_order, study_before, study_after, modality_order,
                                 patient_order, uuid_order)

        paginator = Paginator(studies, items_per_page)
        page = paginator.get_page(page_number)

        return render(request, 'test_datatable/home.html', {
            'page': page,
            'items_per_page': items_per_page,
            'query': query,
            'birthdate_order': birthdate_order,
            'birthdate_before': birthdate_before,
            'birthdate_after': birthdate_after,
            'study_order': study_order,
            'study_before': study_before,
            'study_after': study_after,
            'unique_modalities': unique_modalities,
            'modality_order': modality_order,
            'patient_order': patient_order,
            'uuid_order': uuid_order
        })

    except Exception as e:
        return render(request, 'error.html', {'error_message': str(e)})



# def search_studies(request):
#     query = request.GET.get('query', '')
#     page_number = request.GET.get('page')
#     items_per_page = request.GET.get('items_per_page', 10)
#
#     results = Studies.objects.filter(
#         Q(patient_fio__icontains=query) |
#         Q(patient_birthdate__icontains=query) |
#         Q(study_uid__icontains=query) |
#         Q(study_date__icontains=query) |
#         Q(study_modality__name__icontains=query)
#     )
#
#     paginator = Paginator(results, items_per_page)
#     page = paginator.get_page(page_number)
#
#     data = [
#         {
#             'id': item.id,
#             'patient_fio': item.patient_fio,
#             'patient_birthdate': item.patient_birthdate.strftime('%Y-%m-%d'),
#             'study_uid': str(item.study_uid),
#             'study_date': item.study_date.strftime('%Y-%m-%d %H:%M:%S'),
#             'study_modality': item.study_modality.name,
#         }
#         for item in page
#     ]
#
#     return JsonResponse({'data': data, 'page_number': page_number, 'items_per_page': items_per_page})


def init_db(request):
    """
    База предоставляется уже предзаполненной, но в случае желания перехода
    на другую СУБД, можно раскомментировать код ниже и сгенерировать тестовые данные.
    """

    # Modalities.objects.all().delete()
    # modalities = [['CT', 'Computed Tomography'],
    #               ['MR', 'Magnetic Resonance'],
    #               ['PT', 'Positron emission tomography'],
    #               ['US', 'Ultrasound'],
    #               ['XA', 'X-Ray Angiography'],
    #               ['MG', 'Mammography'],
    #               ['CR', 'Computed Radiography'],
    #               ['AS', 'Angioscopy'],
    #               ['DX', 'Digital Radiography'],
    #               ['EC', 'Echocardiography']]
    # for modality in modalities:
    #     modality_obj = Modalities()
    #     modality_obj.short_code = modality[0]
    #     modality_obj.name = modality[1]
    #     modality_obj.save()
    # for i in range(100000):
    #     study_obj = Studies()
    #     study_obj.patient_fio = names.get_full_name()
    #     study_obj.patient_birthdate = random_date(datetime.datetime(2000, 1, 1, 0, 0, 0),
    #                                               datetime.datetime(2023, 1, 1, 0, 0, 0))
    #     study_obj.study_date = random_date(datetime.datetime(2023, 1, 1, 0, 0, 0),
    #                                        datetime.datetime(2023, 9, 1, 0, 0, 0))
    #     study_obj.study_uid = uuid.uuid4()
    #     random_modality_id = random.randint(1, 10)
    #     study_obj.study_modality = Modalities.objects.get(id=int(random_modality_id))
    #     study_obj.save()
    return render(request, 'test_datatable/init_db.html')
