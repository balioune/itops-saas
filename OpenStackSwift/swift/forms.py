from django import forms

# Fichier contenant la totalite des formulaires utilisees dans l'application

# Forulaire de connexion 
# Variables utilisees : tenant est le tenant ou l'utilisateur souhaite se connecter.
#                       identifiant est l'identifiant de connexion de l'utilisateur.
#                       motDePasse est le mot de passe de l'utilisateur.
class ConnexionForm(forms.Form):
    tenant = forms.CharField(max_length=100)
    identifiant = forms.CharField(max_length=100)
    motDePasse = forms.CharField(max_length=100)

# Formulaire de creation d'un conteneur
# Variable utilisee : conteneurName nom du conteneur a creer.
class CreateConteneurForm(forms.Form):
    conteneurName = forms.CharField(max_length=100)

# Formulaire de suppression d'un conteneur
# Variable utilisee : conteneurName2 nom du conteneur a supprimer.
class DeleteConteneurForm(forms.Form):
    conteneurName2 = forms.CharField(max_length=100)

# Formulaire de selection du conteneur actuelle
# Variable utilisee : conteneurName3 nom du conteneur a selectionner.
class SelectConteneurForm(forms.Form):
    conteneurName3 = forms.CharField(max_length=100)

# Formulaire de suppression d'un objet dans un conteneur specifique
# Variable utilisee : conteneurName4 nom du conteneur ou l'objet se situe.
#                     objetName est le nom de l'objet a supprimer
class DeleteObjet(forms.Form):
    objetName = forms.CharField(max_length=100)    
    conteneurName4 = forms.CharField(max_length=100)

# Formulaire d'importation de fichier
# Variable utilisee : conteneurName5 nom du conteneur ou l'on veut importer le fichier.
#                     objetPath est le chemin du fichier a importer.
class UploadObjet(forms.Form):
    objetPath = forms.FileField()   
    conteneurName5 = forms.CharField(max_length=100) 

