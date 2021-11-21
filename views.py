from django.shortcuts import render
import requests,json,datetime,pycountry
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.http import HttpResponse,JsonResponse
from django.utils import timezone
from .forms import CityForm
from .models import Country,City
from django.urls import reverse, reverse_lazy

@csrf_exempt
def astro(request):
    #REST API call by City name
    #res = requests.get("http://api.openweathermap.org/data/2.5/weather?q=‘Ayn Ḩalāqīm&APPID=b1494fa152443dbecb13f3f5173e88cf")
    '''You can receive the complete response as a string by using the python expression
       res = requests.get("http://api.openweathermap.org/data/2.5/weather?id=50064&APPID=b1494fa152443dbecb13f3f5173e88cf").text 
       Then the variable res is actually serialized JSON content.To get a dictionary, you could take the str you retrieved from .text and
       deserialize it using json.loads() by the python expression res = json.loads(res).
       However, a simpler way to accomplish this task is to use .json() on the response'''
    coordinates = timezone.now()
    '''First the view looks at the request method. 
    When the user visits the URL connected to this view, the browser performs a GET request but 
    the request method 'POST' indicates that the form was submitted'''
    if request.method == "POST":
        city_weather={}
        # Create a form instance with the submitted data
        form = CityForm(request.POST)
        # Validate the form
        if form.is_valid():
            if form.data['city'] and form.data['City']:
                msg= 'enter only one city'
                return render(request,'catalog/astronauts.html',{'form':form,'clock':coordinates,'message':msg})
            if not form.data['City']:
               cityname = form.cleaned_data['city']
            else:
               cityname = form.cleaned_data['City']
            url = 'http://api.openweathermap.org/data/2.5/weather?q=%s&APPID=b1494fa152443dbecb13f3f5173e88cf'% cityname
            res = requests.get(url)
            try:
              res = res.json()
            except (ConnectionError,ConnectionAbortedError):
              msg = 'POOR OR NO INTERNET CONNECTIVITY. PLEASE CHECK'
              return render(request,'catalog/astronauts.html',{'form':form,'clock':coordinates,'message':msg})
            
            try:
              country = res["sys"]["country"]
            except KeyError:
              msg = 'ERROR:THERE IS A SPELLING MISTAKE IN CITY NAME.CORRECT IT AND RETRY'
              return render(request,'catalog/astronauts.html',{'form':form,'clock':coordinates,'message':msg})
            '''the exception handling above can be replaced by 'if res["cod"]=='404': ' which was framed after analysing the traceback that one gets
            when you enter an incorrectly spelled city name in the textbox'''

            cityname = res["name"]
            tz = res["timezone"]
            visible = round((res["visibility"]/1000))
            latitude = round(res["coord"]["lat"],2)
            max_temp_k = res["main"]["temp_max"]
            min_temp_k = res["main"]["temp_min"]
            pressure = res["main"]["pressure"]
            humidity = res["main"]["humidity"]
            wind_speed = res["wind"]["speed"]
            wind_degree = res["wind"]["deg"]
            feels_like_temp_c = round((res["main"]["feels_like"] - 273.15),2)
            feels_temp = f'Feels like {feels_like_temp_c}°C'
            max_temp_c = round((max_temp_k - 273.15),2)
            min_temp_c = round((min_temp_k - 273.15),2)
            picture = res["weather"][0]["icon"]
            try:
                Country= pycountry.countries.lookup(country).official_name
                code=pycountry.countries.lookup(country).numeric
            except AttributeError:
                #for countries that are known by two abbreviations for e.g. Russia can be either RU or RUS, former is alpha_2 and latter is alpha_3. Look  at pycountry documentation
                Country = pycountry.countries.get(alpha_2=country).name
                code=pycountry.countries.lookup(country).numeric
            try:
                currency=pycountry.currencies.lookup(code).name
            except LookupError:
                currency=f"Not found for {cityname}"
            #openweathermap gives windspeed in m/s but on our page, we want to display in km/hr, so multiply by 3.6 to do the conversion
            wind_speed = round((wind_speed)* 3.6)
            #how to get the time in the city using timezone
            hours = (tz/3600) - 5.5
            hours_adjusted = datetime.timedelta(hours=hours)
            citytime = coordinates + hours_adjusted
            city_weather = {
                 'city':cityname,
                 'country':Country,
                 'max_temperature':max_temp_c,
                 'min_temperature':min_temp_c,
                 'feels_like_temp':feels_like_temp_c,
                 'longitude':round(res["coord"]["lon"],2),
                 'latitude':latitude,
                 'description':res["weather"][0]["description"],
                 'pressure':pressure,
                 'humidity':humidity,
                 'wind_speed':wind_speed,
                 'wind_degree':wind_degree,
                 'currency':currency,
                 'citytime':citytime,
                 'visibility':visible,
                 'feels_temp':feels_temp,
                 'icon':picture}
            '''Other items needed are wind(speed and degree), temp - min & max in degree celsius, Humidity, country also'''
            ''' We will use Python F strings to format the HttpResponse with above parameters'''
            '''message=(
                   f"City: {cityname} Longitude: {longitude} degrees; Latitude: {latitude} degrees \r"
                   f"Weather : {weather} Max_temp:{max_temp_c} Celsius Min_temp:{min_temp_c} Celsius.")
                   wurl stands for weather url and cfurl stands for country flag url. Pl. note that Python F strings are used to pass these variables
                   as img sources in templates'''
            wurl=f'http://openweathermap.org/img/w/{picture}.png'
            cfurl=f'https://www.countryflags.io/{country}/shiny/32.png'
            for x,y in res.items():
                print(x,y)
            #context = {'form':form,'clock':coordinates,'output':city_weather,'weatherpic':wurl,'countryflag':cfurl}
            '''After the user enters the city name manually, and presses
            "Get Data" button, after the city data is fetched, the
            existing city name should disappear '''
            if (not form.data['City']) and (not form.data['city']):
              msg = 'Enter a city'
              return render(request,'catalog/astronauts.html',{'form':form,'clock':coordinates,'message':msg})
            if form.data['City']:
                form=CityForm()
            else:
                pass
            return render(request,'catalog/astronauts.html',{'form':form,'clock':coordinates,'output':city_weather,'weatherpic':wurl,'countryflag':cfurl})
        else:
         pass
    else:
        '''If the view receives a GET request (or, to be precise, any kind of request that is not a
        POST request), it creates an instance of CityForm and uses django.shortcuts.render() to 
        render the astronauts.html template'''
        form = CityForm()
        return render(request,'catalog/astronauts.html',{'form':form,'clock':coordinates})
    #return render(request,'catalog/astronauts.html',context)
    #response = requests.get("http://api.open-notify.org/astros.json")
    #return HttpResponse(('The latitude and longitude of ',cityname, ' are ',latitude,' & ',longitude,'.','The weather is ', weather))

def logout(request):
    return render(request, 'catalog/logout.html')
def filter_cities(request):
    country_id = request.GET.get('country')
    cities = City.objects.filter(country=country_id).order_by('name')
    print(cities)
    return render(request, 'catalog/city_dropdown_list_options.html', {'cities': cities})
