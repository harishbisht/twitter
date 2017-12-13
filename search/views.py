from django.http import JsonResponse, HttpResponse
import requests
from requests_oauthlib import OAuth1
import json
from datetime import datetime
from django.conf import settings
from django.views.decorators.http import require_http_methods
from operator import itemgetter
import csv
import sys
reload(sys)
sys.setdefaultencoding('utf8')


@require_http_methods(["GET"])
def search(request):
    try:
        auth = OAuth1(settings.CONSUMER_KEY, settings.CONSUMER_SECRET, settings.ACCESS_TOKEN, settings.ACCESS_TOKEN_SECRET)

        # getting count
        if 'count' in request.GET and int(request.GET['count']):
            count = request.GET['count']
        else:
            count = 4

        # datefilter
        if 'date' in request.GET and request.GET['date']:
            until = datetime.strptime(request.GET['date'], "%Y-%m-%d").date().isoformat()
        else:
            until = datetime.now().date().isoformat()

        # query filter
        if 'query' in request.GET and request.GET['query']:
            query = request.GET['query']
        else:
            raise Exception("query field missing")

        url = "https://api.twitter.com/1.1/search/tweets.json?q=%s&count=%s&result_type=mixed&until=%s" % (query, count, until)
        response = requests.get(url, auth=auth)
        response = json.loads(response.text)
        json_response = []
        if response['statuses']:
            for i in response['statuses']:
                json_response.append([i['text'], i['created_at']])
        else:
            return JsonResponse({"data": None})

        # option for sorting and downloading
        if 'type' in request.GET and request.GET['type']:
            if request.GET['type'].lower() == "sort":
                json_response.sort(key=itemgetter(0))
                return JsonResponse({"data": json_response}, json_dumps_params={'indent': 4})
            elif request.GET['type'].lower() == "download":
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="tweet.csv"'
                writer = csv.writer(response)
                writer.writerow(['Tweet', "Date"])
                writer.writerows(json_response)
                return response
            else:
                pass
        return JsonResponse({"data": json_response}, json_dumps_params={'indent': 4})
    except Exception, e:
        return JsonResponse({"error": str(e)})
