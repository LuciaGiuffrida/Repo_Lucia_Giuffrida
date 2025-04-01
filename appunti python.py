

#struttura del ciclo for
#struttura del ciclo while 

#dictionary

#list 
lista = []
#tuple
#set 




#CLASSI E OGGETTI
class Persona:
    #sono attributi 
    def __init__(self, nome, cognome ):
        self.nome = nome
        self.cognome = cognome
    #metodo --> la persona fa delle azioni 
    def saluta (self):
        print("ciao sono "+self.nome)

    


persona1 = Persona("Lucia","Giuffrida") #sto passando delle stringhe quindi " "
print(persona1)
persona1.saluta()