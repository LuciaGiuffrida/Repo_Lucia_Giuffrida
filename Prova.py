class Persona:
    #sono attributi
    def __init__(self, nome, cognome ):
        self.nome = nome
        self.cognome = cognome
    #metodo --> la persona fa delle azioni
    def saluta (self):
        print("ciao sono "+ self.nome)

persona1 = Persona("Lucia","Giuffrida") #sto passando delle stringhe quindi " "
print(persona1)
persona1.saluta()

#ereditarietà --> proprietà (metodi) che una classe eredita da un altro classe (abbiamo classe figlia e una classe madre)

class Insegnante(persona):
    def __init__(self, nome, cognome, materia): #costruttore
        super().__init__(nome,cognome)
        self.materia = materia
    def saluta(self):
        print ("Buongiorno sono" + self.nome + " " + self.cognome)


insegnante1 = Insegnante("Lucia", "Giuffrida")
print(insegnante1)
insegnante1.saluta()
