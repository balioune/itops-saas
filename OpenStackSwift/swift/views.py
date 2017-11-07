#-*- coding: utf-8 -*-

# Liste des imports :
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from swift.models import *
from .forms import * 
import requests
import binascii
import glob
import os



#Fonction qui renvoi la page index.html quand on l'appelle
#Fonction appelée dans urls.py
def index(request):
        return render(request, 'swift/index.html')

# Fonction qui traite la totalité des formulaires de la page swift.html
# En fontion du formulaire validé, on execute une action spécifique
def swift(request):   

    #On initialise les differents formulaires de la page
    formDelete = DeleteConteneurForm(request.POST or None)
    form = CreateConteneurForm(request.POST or None)
    formSelect = SelectConteneurForm(request.POST or None)
    formObjetDelete = DeleteObjet(request.POST or None)
    formObjetUpload = UploadObjet(request.POST, request.FILES)
    
    #On supprime le contenu du dossier static/tmp/.
    files = glob.glob('static/tmp/*')   
    for f in files:
        os.remove(f)
    
    #Si le formulaire de creation de conteneur est valide, on execute les actions suivantes :
    if form.is_valid():
        #On recupere le nom du conteneur à créer.
        contener = form.cleaned_data['conteneurName']
        #On le cree.
        createContainer(request,contener)
        #On selectionne le conteneur qui vient d'etre crée pour l'afficher
        conteneurName = contener
        # On recupère la liste des conteneurs
        conteneurs=getContainerList(request)

 
    #Si le formulaire de suppression de conteneur est validé, on execute les actions suivantes :  
    elif formDelete.is_valid():
        #On récupère le nom du conteneur à supprimer.
        contener = formDelete.cleaned_data['conteneurName2']
        #On le supprime
        removeContainer(request,contener)
         # On recupère la liste des conteneurs
        conteneurs=getContainerList(request)

    #Si le formulaire de selection d'un conteneur est validé, on execute les actions suivantes :  
    elif formSelect.is_valid():
        #On récupère le nom du conteneur à selectionner.
        conteneurName = formSelect.cleaned_data['conteneurName3']
        #On recupère la liste des objets de ce conteneur
        listeObjet = getObjectList(request,conteneurName,True)
         # On recupère la liste des conteneurs
        conteneurs=getContainerList(request)

    #Si le formulaire de suppression d'un objet est validé, on execute les actions suivantes :  
    elif formObjetDelete.is_valid():
        #On récupère le nom du conteneur où est situé l'objet à supprimer.
        objetName = formObjetDelete.cleaned_data['objetName']
        #On récupère le nom de l'objet à supprimer.
        conteneurName = formObjetDelete.cleaned_data['conteneurName4']
        #On supprimer l'objet
        removeObject(request,conteneurName,objetName)
        #On met à jour la liste des objets de ce conteneur
        listeObjet = getObjectList(request,conteneurName,True)
        #On recupère la liste des conteneurs
        conteneurs=getContainerList(request)

    #Si le formulaire d'import d'un objet est validé, on execute les actions suivantes : 
    elif formObjetUpload.is_valid():
        # On récupère le path de l'objet à importer sur le conteneur
        objetPath = formObjetUpload.cleaned_data['objetPath']
        # On recupère le nom de l'objet
        objetName = objetPath.name
        #On récupère le nom du conteneur où est situé l'objet à créer.
        conteneurName = formObjetUpload.cleaned_data['conteneurName5']
        
        #On upload temporairement l'objet sur le serveur dans un dossier temporaire
        path = default_storage.save('tmp/'+objetName, ContentFile(objetPath.read()))
        tmp_file = os.path.join(settings.MEDIA_ROOT, path)
        # On upload dans le conteneur l'objet précédemment uploder sur le serveur
        createObject(request,conteneurName,objetName,'tmp/'+objetName)
        # On supprime l'objet precemment crée sur le serveur
        os.remove('tmp/'+objetName)
        
        # On rend l'objet qui est sur le conteneur disponible au téléchargement
        readObject(request,conteneurName,objetName)
        
        #On met à jour la liste des objets de ce conteneur
        listeObjet = getObjectList(request,conteneurName,True)
        #On recupère la liste des conteneurs
        conteneurs=getContainerList(request)

    #Sinon on charge simplement la page avec les attributs necessaires au bon fonctionnement de la page
    else:
        #conteneurs est la variable utilisée pour stocker la liste de conteneurs
        conteneurs=getContainerList(request)
        #conteneurName est la variable utilisée pour stocker le conteneur à visualiser
        conteneurName = conteneurs[0].name
        #listeObjet est la variable qui contient la liste d'objet du conteneur selectionné
        listeObjet = getObjectList(request,conteneurName,True)

    
    #Enfin, on retourne la page avec les variables utilisées précédement dans la fonction.
    return render(request, 'swift/swift.html',locals())

#Fonction qui gère l'authentification de l'utilisateur sur l'application
def login(request):
    #Dès qu'un utilisateur accède à la page login, on supprime les variables de session.
    removeSession(request)
    form = ConnexionForm(request.POST or None)
    #Si l'utilisateur rentre toutes les informations de connexion, on peut traiter la demande
    if form.is_valid(): 

        tenant = form.cleaned_data['tenant']
        username = form.cleaned_data['identifiant']
        motDePasse = form.cleaned_data['motDePasse']

        #Si la fonction connexion renvoie un Objet User vide, la connexion a échoué
        user = connexion(username,motDePasse,tenant,request)
        if user.token=="":
            #On redirige donc l'utilisateur vers la page de connexion
            return render(request, 'swift/login.html')
        else:      
            #Sinon, la connexion à fonctionnée et on renvoi l'utilisateur sur la page d'accueil
            return render(request, 'swift/index.html')

    #Si le formulaire est incomplet on renvoi l'utilisateur sur la page de connexion
    else:
        return render(request, 'swift/login.html')
        
#Fonction permettant de supprimer les variables stockées en session
def removeSession(request):
       request.session['userToken'] = ''
       request.session['username'] = ''
       request.session['currentTenant'] = ''
       request.session['tenantId'] = ''

# Fonction permettant l'authentification d'un utilisateur sur l'application 
def connexion(identifiant,motDePasse,tenant,request):
    
    # Initialisation de la requette
    tokenUrl = 'http://192.168.150.15:5000/v2.0/tokens'
    headersToken = {'content-type': 'application/json'}
    dataJson = '{"auth": {"tenantName": "'+tenant+'" , "passwordCredentials": {"username": "'+identifiant+'", "password": "'+motDePasse+'"}}}'
    
    # Envoi de la requette
    requestToken = requests.post(tokenUrl, data=dataJson, headers=headersToken)
    
    # Si la réponse contient le mot 'erreur', alors l'authentification échoue
    test = requestToken.text.find('error')
    
    # Authentification echouée :
    if test>0 :
        return User(tenant="",name="",token="",tenantId="")
    # Réussite de l'authentification :
    else:

       # On récupère les différentes variables nécéssaire au bon fonctionnement de l'application : 
       responseToken = requestToken.json()
       userToken = responseToken['access']['token']['id']
       username = responseToken['access']['user']['username']
       currentTenant = responseToken['access']['token']['tenant']['name']
       tenantId = responseToken['access']['token']['tenant']['id']
      
       # Puis on les stocks en session :
       request.session['userToken'] = userToken
       request.session['username'] = username
       request.session['currentTenant'] = currentTenant
       request.session['tenantId'] = tenantId

       return User(tenant=currentTenant,name=username,token=userToken,tenantId=tenantId)

# Fonction qui retourne la liste des conteneurs du tenant selectionné.
def getContainerList(request):

    # Création de la requette 
    containerListUrl = 'http://192.168.150.15:8080/v1/AUTH_'+request.session['tenantId']+'/'
    # Création du header contentant les données permettant de s'identifier
    headersToken = {'X-Auth-Token': request.session['userToken']}
    # On effectue la requete 
    requestContainerList = requests.get(containerListUrl+'?format=json', headers=headersToken)
    # Puis on la transforme dans le format json, pour pouvoir lire les données recues. 
    responseContainerList = requestContainerList.json()
    containerList = []

    # On parcourt les données reçues (un élement de la liste = un conteneur)
    for c in responseContainerList:
        # On crée l'objet Container 
        container = Container(c['name'],c['bytes'],c['count'])
        # On compte le nombre d'objets qu'il contient
        container.count = len(getObjectList(request,container.name,False))
        # On rajoute le conteneur crée dans la liste de conteneurs
        containerList.append(container)       
    # On retourne la liste de tous les conteneurs
    return containerList

# Fonction permettant de créer un conteneur sur un tenant spécifique
def createContainer(request,conteneurName):
    headersToken = {'X-Auth-Token': request.session['userToken']}
    createContainerUrl = 'http://192.168.150.15:8080/v1/AUTH_'+request.session['tenantId']+'/'+conteneurName+'/'
    requestCreateContainer = requests.put(createContainerUrl, headers=headersToken)

# Fonction permettant de supprimer un conteneur sur un tenant spécifique
def removeContainer(request,containerName):
    headersToken = {'X-Auth-Token': request.session['userToken']}
    removeContainerUrl = 'http://192.168.150.15:8080/v1/AUTH_'+request.session['tenantId']+'/'+containerName+'/'
    requestRemoveContainer = requests.delete(removeContainerUrl, headers=headersToken)

# Fonction permettant de récuperer la liste des objets dans un conteneur spécifique
# L'attribut 'activate' permet, quand il est à 'true', de télécharger les objets du conteneur sur le serveur (voir fct readObject)
def getObjectList(request,containerName,activate):
    # On initialise le requete permettant de récuperer la liste des objets puis on l'éxecute.
    headersToken = {'X-Auth-Token': request.session['userToken']}
    objectListUrl = 'http://192.168.150.15:8080/v1/AUTH_'+request.session['tenantId']+'/'+containerName+'/'
    requestObjectList = requests.get(objectListUrl+'?format=json', headers=headersToken)
    responseObjectList = requestObjectList.json()
    objectList = []
    # On parcourt les données recues (un élement de la liste = un objet)
    for o in responseObjectList:
        #On crée l'objet Objet en fonction des données recues
        objet = Object(o['name'],o['bytes'])
        # Si l'attribut activate est à 'true' on télécharge l'objet en question sur le serveur
        if activate:
            objet.hash=readObject(request,containerName,objet.name)
            objectList.append(objet)
	# On retourne la liste de tous les objets
    return objectList

# Fonction permettant de supprimer un objet d'un conteneur spécifique
def removeObject(request,containerName,objectName):
    headersToken = {'X-Auth-Token': request.session['userToken']}
    removeObjectUrl = 'http://192.168.150.15:8080/v1/AUTH_'+request.session['tenantId']+'/'+containerName+'/'+objectName
    requestRemoveObject = requests.delete(removeObjectUrl, headers=headersToken)

# Fonction permettant d'uploader un objet dans un tenant spécifique
def createObject(request,containerName,objectName,pathFile):
    createObjectUrl = 'http://192.168.150.15:8080/v1/AUTH_'+request.session['tenantId']+'/'+containerName+'/'+objectName
    requestCreateObject = requests.put(createObjectUrl, headers={'X-Auth-Token': request.session['userToken'], 'X-Detect-Content-Type' : 'true' }, data=open(pathFile,'rb'))

# Fonction permettant de lire un objet situé dans un conteneur en le téléchargeant dans un dossier temporaire 
def readObject(request,containerName,objectName):
    
    # On crée et on execute la requete permettant de récupèrer l'objet en question
    createObjectUrl = 'http://192.168.150.15:8080/v1/AUTH_'+request.session['tenantId']+'/'+containerName+'/'+objectName
    r = requests.get(createObjectUrl, headers={'X-Auth-Token': request.session['userToken'], 'X-Detect-Content-Type' : 'true' })

    #On génère un hash de 16 caractères de manière aléatoire
    hashRandom = binascii.hexlify(os.urandom(16))
    #On crée le nom du fichier avec ce hash et avec son extension
    local_filename = 'static/tmp/'+hashRandom+'.'+objectName.split(".")[-1]           
    
    # On upload cet objet dans le dossier temporaire
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk:
                f.write(chunk)

    # On retourne le nom et le chemin du fichier pour qu'il puisse être téléchargé
    return local_filename