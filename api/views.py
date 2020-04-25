import datetime, json

from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from api.models import DataSpecification, DataValues

@require_POST
@csrf_exempt
def create_spec(request):
    '''
    Creates a new specification for a data provider.
    '''
    if "providerId" in request.POST and "fields" in request.POST:
        # Convert fields to required data types:
        providerId = int(request.POST.get("providerId"))
        try:
            fields = json.loads(request.POST.get("fields"))
        except:
            return HttpResponseBadRequest("Incorrect JSON format for 'fields' field.")
        
        DataSpecification.objects.create(providerId=providerId, fields=fields)
        return HttpResponse(status=201)
    else:
        return HttpResponseBadRequest('"providerId" and "fields" cannot be blank.')

@require_POST
@csrf_exempt
def set_data(request):
    '''
    Creates a new array of data values for a particular provider.
    '''
    if "providerId" in request.POST and "data" in request.POST:
        # Convert fields to required data types:
        providerId = request.POST.get("providerId")
        try:
            data = json.loads(request.POST.get("data"))
        except:
            return HttpResponseBadRequest("Incorrect JSON format for 'data' field.")

        # Ensure this provider exists in the DB:
        spec = DataSpecification.objects.filter(providerId=providerId)
        if len(spec) > 0:
            spec = spec[0]
            fields = spec.fields
            fields_len = len(fields)

            # Ensure each data value has all the fields defined in the specification
            for item in data:
                fields_valid = [field in fields for field in item]
                if sum(fields_valid) != fields_len or len(fields_valid) != fields_len:
                    return HttpResponseBadRequest("Invalid data supplied.")
            
            DataValues.objects.create(providerId=providerId, data=data)
            return HttpResponse(status=201)
        else:
            return HttpResponseBadRequest("Invalid providerId supplied.")
    else:
        return HttpResponseBadRequest('"providerId" and "data" cannot be blank.')

@require_GET
def filter_data(request, providerId):
    '''
    Filters and returns the data item that closest matches query parameters supplied in the
    GET request.
    '''
    # Get request parameters
    keys = request.GET.keys()
    values = [("string", value.split(":")[1].lower()) if "eqc" in value else ("number", value.split(":")[0], int(value.split(":")[1])) for value in request.GET.values()]
    
    # Ensure this provider exists in the DB:
    provider = DataValues.objects.filter(providerId=providerId)
    if len(provider) > 0:
        provider = provider[0]
        data = provider.data
        
        # Get the data item that closest matches the request parameters
        max_score = 0
        closest_item = None

        for item in data:
            # Add a score for each request parameter if it is found in this item
            score = 0
            for i, key in enumerate(keys):
                if values[i][0] == "string":
                    if item[key].lower() == values[i][1]:
                        score += 1
                else:
                    if values[i][1] == "eq" and int(item[key]) == values[i][2] or (
                        values[i][1] == "gt" and int(item[key]) > values[i][2]) or (
                        values[i][1] == "lt" and int(item[key]) < values[i][2]):
                        score += 1
            
            if score > max_score:
                max_score = score
                closest_item = item

        if closest_item is not None:
            return JsonResponse(closest_item)
        else:
            return HttpResponseBadRequest("No data found matching this query.")

    else:
        return HttpResponseBadRequest("Invalid providerId supplied.")