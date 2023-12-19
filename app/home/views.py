from django.shortcuts import render
from django.views.generic.edit import FormView
from . import forms
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from .models import User
from django.http import JsonResponse
from django.db import connection
from openrouteservice import convert
import folium
import json
import openrouteservice
import os
import statistics

# Create your views here.
def index(request):
    return render(request, "home/index.html")

def user_home(request):
    """ make home view """
    return render(request, 'home/home.html')

def user_logout(request):
    """logout logged in user"""
    logout(request)
    return HttpResponseRedirect(reverse_lazy('index'))

def localizador_residuo(request):
    return render(request, 'home/localizador_residuo.html')

def get_capitulos(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT capitulo, descricao FROM ibama_capitulo;")
        results = cursor.fetchall()
        
        capitulos = [{'capitulo': row[0], 'descricao': row[1]} for row in results]

        return render(request, 'home/localizador_residuo.html', {'capitulos': capitulos})

def get_subcapitulos(request):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT subcapitulo, descricao FROM ibama_subcapitulo WHERE capitulo = {request.GET.get('capitulo')};")
        results = cursor.fetchall()
        
        subcapitulos = [{'subcapitulo': row[0], 'descricao': row[1]} for row in results]

        return render(request, 'home/partials/form-subcapitulo.html', {'subcapitulos': subcapitulos})
    
def get_codigos(request):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT codigo, descricao FROM ibama_codigo WHERE subcapitulo = '{request.GET.get('subcapitulo')}';")
        results = cursor.fetchall()
        
        codigos = [{'codigo': row[0], 'descricao': row[1]} for row in results]

        return render(request, 'home/partials/form-codigo.html', {'codigos': codigos})
    
def get_municipios(request):
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT nome, id FROM ibge_municipios;")
        results = cursor.fetchall()
        
        municipios = [{'nome': row[0], 'id': row[1], } for row in results]

        return render(request, 'home/partials/form-municipio.html', {'municipios': municipios})
    
def get_mapa_residuos(request):
    
    return render(request, 'home/maps/waste_map.html')
    
def get_municipios_coord_by_id(id):
    
    with connection.cursor() as cursor:
        
        cursor.execute(f"SELECT longitude, latitude FROM ibge_municipios WHERE id = {id};")
        results = cursor.fetchall()
    
    return results[0]

def get_municipios_nome_ascii_by_id(id):
    
    with connection.cursor() as cursor:
        
        cursor.execute(f"SELECT nome_ascii FROM ibge_municipios WHERE id = {id};")
        results = cursor.fetchall()
    
    return results[0]

def get_municipios_nome_by_id(id):
    
    with connection.cursor() as cursor:
        
        cursor.execute(f"SELECT nome FROM ibge_municipios WHERE id = {id};")
        results = cursor.fetchall()
    
    return results[0]

def get_municipios_nome_by_nome_ascii(nome_ascii):
    
    with connection.cursor() as cursor:
        
        nome_ascii = nome_ascii.replace("'", '')
        cursor.execute(f"SELECT nome FROM ibge_municipios WHERE nome_ascii = '{nome_ascii}';")
        results = cursor.fetchall()
    
    return results[0]

def get_municipios_coord_by_nome_ascii(nome):
    
    with connection.cursor() as cursor:
        nome = nome.replace("'", '')
        cursor.execute(f"SELECT longitude, latitude FROM ibge_municipios WHERE nome_ascii = '{nome}';")
        results = cursor.fetchall()
    
    return results[0]

def get_directions(start_coord: tuple, end_coord: tuple, start_nome_ascii, end_nome_ascii, start_nome, end_nome):
    
    if start_coord != end_coord:
        
        # print(os.environ)
        client = openrouteservice.Client(key=os.environ.get('ORS_API_KEY', ''), retry_over_query_limit=False)

        coords = (start_coord, end_coord)
        try:
            res = client.directions(coords, radiuses=(8000, 8000))
            
            geometry = res['routes'][0]['geometry']
            decoded = convert.decode_polyline(geometry)

            distance = round(res['routes'][0]['summary']['distance']/1000,1)
            distance_txt = "<h4> <b>Distance :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['distance']/1000,1))+" km </strong>" +"</h4></b>"
            duration_txt = "<h4> <b>Duration :&nbsp" + "<strong>"+str(round(res['routes'][0]['summary']['duration']/60,1))+" min </strong>" +"</h4></b>"

            m = folium.Map(location=[start_coord[0], start_coord[1]], zoom_start=10, control_scale=True, tiles="cartodbpositron")
            folium.GeoJson(decoded).add_child(folium.Popup(distance_txt+duration_txt, max_width=300)).add_to(m)

            folium.Marker(
                location=list(coords[0][::-1]),
                popup=start_nome,
                icon=folium.Icon(color="green"),
            ).add_to(m)

            folium.Marker(
                location=list(coords[1][::-1]),
                popup=end_nome,
                icon=folium.Icon(color="red"),
            ).add_to(m)

            m.save(f'home/templates/home/maps/{start_nome_ascii}_{end_nome_ascii}.html')
            
            with connection.cursor() as cursor:
                cursor.execute(f"""INSERT INTO distancia_cidades ("start_nome", "end_nome", "distance") VALUES ('{start_nome_ascii}','{end_nome_ascii}',{distance});""")
                
            return distance

        except Exception as e:
            print(e)
            return None
            
    else: 
        distance = 0.0
        return distance
    
def get_score(distancia, quantidade_consumidor, quantidade_gerador):
    
    quantidade_gerador = float(quantidade_gerador)
    quantidade_consumidor = float(quantidade_consumidor)
    distancia = float(distancia)

    if quantidade_gerador / quantidade_consumidor <= 0.8:
        score = ( quantidade_gerador / quantidade_consumidor ) * ( ( 10**2 ) / ( 10**(-1) * (distancia**2) + 10) )
    else:
        score = ( ( 10**2 ) / ( 10**(-1)*distancia**2 + 10) )
        
    return '{0:.6f}'.format(score)

def get_custo(distancia):
    
    distancia = float(distancia)

    if distancia == 0.0:
        custo = 2.1
    else:
       custo = 2.1 * distancia
        
    return '{0:.2f}'.format(custo)

def get_pegada_carbono(distancia):
    
    distancia = float(distancia)

    if distancia == 0.0:
        pegada = 0.92
    else:
       pegada = 0.92 * distancia
        
    return '{0:.2f}'.format(pegada)

    
def match(request):
    
    with connection.cursor() as cursor:
        
        start_coord = get_municipios_coord_by_id(request.POST.get('municipio'))
        start_nome_ascii = get_municipios_nome_ascii_by_id(request.POST.get('municipio'))[0]
        start_nome = get_municipios_nome_by_id(request.POST.get('municipio'))[0]
        
        empresas_dados = []
        
                
        cursor.execute(f"""SELECT razao_social, SUM(quantidade) as quantidade, destinacao, municipio, situacao_cadastral, ddd_telefone, cnae_fiscal_descricao FROM mtr_residuo_gerador_destinacao WHERE cod_residuo = '{request.POST.get('codigos').replace(" ", "")}' AND municipio IS NOT NULL GROUP BY razao_social, destinacao, municipio, situacao_cadastral, ddd_telefone, cnae_fiscal_descricao;""")
        results = cursor.fetchall()
        results_dict = [{'razao_social': row[0], 'quantidade': row[1], 'destinacao': row[2], 'municipio': row[3], 'situacao_cadastral': row[4], 'ddd_telefone': row[5], 'cnae_descricao': row[6]} for row in results]
        
        files = []
        
        # print(os.getcwd())
        folder_name = "/app/home/templates/home/maps"
                
        # directory = os.fsencode(folder_name)
        # print(directory)
        for file in os.listdir(folder_name):
            files.append(file)
        
        print(files)
        for result in results_dict:
            try:
                end_coord = get_municipios_coord_by_nome_ascii(result.get('municipio'))
                end_nome_ascii = result.get('municipio')
                
                if f"{start_nome_ascii.replace(' ', '')}_{end_nome_ascii.replace(' ', '')}.html" not in files:
                    end_nome = get_municipios_nome_by_nome_ascii(end_nome_ascii)[0]
                    
                    distancia = get_directions(
                        start_coord=start_coord, 
                        end_coord=end_coord, 
                        start_nome_ascii=start_nome_ascii.replace(' ', ''), 
                        end_nome_ascii=end_nome_ascii.replace(' ', ''), 
                        start_nome=start_nome,
                        end_nome=end_nome)
                    
                    if distancia == None:
                        continue
                    
                    score = get_score(distancia=distancia, quantidade_consumidor=request.POST.get('quantidade'), quantidade_gerador=result.get('quantidade'))    
                    pegada = get_pegada_carbono(distancia=distancia)
                    custo = get_custo(distancia=distancia)
                    
                    empresas_dados.append(
                        {
                            "municipio": end_nome, 
                            "distancia": distancia, 
                            "razao_social": result.get('razao_social'),
                            'quantidade': result.get('quantidade'), 
                            'destinacao': result.get('destinacao'), 
                            'situacao_cadastral': result.get('situacao_cadastral'), 
                            'ddd_telefone': result.get('ddd_telefone'), 
                            'cnae_descricao': result.get('cnae_descricao'),
                            'score': float(score),
                            'pegada_carbono': pegada,
                            'custo_transporte': custo, 
                            'file_name': f"{start_nome_ascii.replace(' ', '')}_{end_nome_ascii.replace(' ', '')}"
                        })
                    
                                
                else:
                    cursor.execute(f"SELECT distance FROM distancia_cidades WHERE start_nome = '{start_nome_ascii.replace(' ', '')}' AND end_nome = '{end_nome_ascii.replace(' ', '')}';")
                    distancia = cursor.fetchone()[0]
                    end_nome = get_municipios_nome_by_nome_ascii(end_nome_ascii)[0]
                    
                    score = get_score(distancia=distancia, quantidade_consumidor=request.POST.get('quantidade'), quantidade_gerador=result.get('quantidade'))    
                    pegada = get_pegada_carbono(distancia=distancia)
                    custo = get_custo(distancia=distancia)
                    
                    empresas_dados.append(
                        {
                            "municipio": end_nome, 
                            "distancia": distancia, 
                            "razao_social": result.get('razao_social'),
                            'quantidade': result.get('quantidade'), 
                            'destinacao': result.get('destinacao'), 
                            'situacao_cadastral': result.get('situacao_cadastral'), 
                            'ddd_telefone': result.get('ddd_telefone'), 
                            'cnae_descricao': result.get('cnae_descricao'),
                            'score': float(score),
                            'pegada_carbono': pegada,
                            'custo_transporte': custo,
                            'file_name': f"{start_nome_ascii.replace(' ', '')}_{end_nome_ascii.replace(' ', '')}"
                        })
            except Exception as e:
                print(e)
                    
    empresas_dados = sorted(empresas_dados, key=lambda x: float(x['score']), reverse=True)
    return render(request, 'home/partials/form-resultado.html', {'empresas_dados': empresas_dados})
    
def get_popup_content(request):
    # Your logic to retrieve or generate the HTML content
    popup_content = f"home/maps/{request.GET.get('file_name', '')}.html"
    
    return render(request, 'home/partials/result-directions.html', {'popup_content': popup_content})    

class SignupView(FormView):
    """sign up user view"""
    form_class = forms.SignupForm
    template_name = 'home/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        """ process user signup"""
        credentials = form.cleaned_data
        user = User.objects.create_user(email=credentials['email'], password=credentials['password1'], name=credentials['name'])
        # user = form.save(commit=False)
        
        user.save()
        login(self.request, user)
        if user is not None:
            return HttpResponseRedirect(self.success_url)

        return super().form_valid(form)

class LoginView(FormView):
    """login view"""

    form_class = forms.LoginForm
    success_url = reverse_lazy('home')
    template_name = 'home/login.html'

    def form_valid(self, form):
        """ process user login"""
        credentials = form.cleaned_data

        user = authenticate(username=credentials['email'],
                            password=credentials['password'])

        if user is not None:
            login(self.request, user)
            return HttpResponseRedirect(self.success_url)

        else:
            messages.add_message(self.request, messages.INFO, 'Wrong credentials\
                                please try again')
            return HttpResponseRedirect(reverse_lazy('login'))