from __future__ import unicode_literals
from django.db import models

# Classe objet d'un utilisateur
class User(models.Model):
    # Tenant ou est situe le conteneur
    tenant=models.CharField(max_length=50)
    # Token de l'utilisateur pour l'authentification
    token =models.CharField(max_length=50)
    # Nom de l'utilisateur
    name =models.CharField(max_length=50)
    # ID du tenant ou est situe l'utilisateur
    tenantId=models.CharField(max_length=50)   

    def __str__(self):
        return self.token

# Classe objet d'un conteneur
class Container:

	def __init__(self,name,size,count):
                # Nom du conteneur
		self.name = name
		# Taille en octets du conteneur
		self.size = size
		# Nombre d'objet dans le conteneur
		self.count = count

class Object:

	def __init__(self,name,size):
                # Nom du fichier
		self.name = name
        # Taille en octets du fichier
		self.size = size
		self.hash = ''
		# Extension du fichier
		extension = name.split(".")[-1]
		#
		if extension=='wma' or extension=='aac' or extension=='wav' or extension=='mp3' or extension=='ogg':
			self.type = 'audio'
		elif extension=='mp4' or extension=='wmv' or extension=='avi' or extension=='mpg' or extension=='mpeg' :
			self.type = 'video'
		elif extension=='pdf':
			self.type = 'pdf'
		elif extension=='png' or extension=='jpg' or extension=='jpeg' or extension=='bmp' or extension=='gif':
			self.type = 'image'
		else:
			self.type='autre'


