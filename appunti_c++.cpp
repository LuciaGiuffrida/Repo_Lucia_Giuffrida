
#include <iostream>
#include <string>
#include <vector>
#include <cmath> 

using std::string; 
using std::vector; 

struct persona{
    string nome;
    string cognome; 
}; 


int main() {
    int eta=25; 
    string nome = "Lucia"; // In C++ usiamo std::string invece di char array
    bool online= true; 
    float temp = 0;
    float media[5] = {0}; // Array di float con 5 elementi inizializzati a 0
    float x = 11;  
    int giorno=0; 
    float array[5]={}; //non posso aggiungere o togliere elementi dagli array 
    //vettori sono array ma molto più permissivi 
    vector<int> numeri ={10,20,30}; //i vettori si dichiarano cosi 

    string tiponumero = (int(x) % 2 == 0) ? "pari" : "dispari";  //operatore ternario 
    std::cout << tiponumero << std::endl;


    std::cout << "Inserisci la tua eta"<< std::endl;
    std::cin >> eta; //comando per prendere qualcosa in input
    std::cout << std::sqrt(eta) << std::endl; 
    std::cout << std::fixed << x << std::endl; //stampo i numeri dopo la virgola 
    std::cout << std::fixed << int(x) << std::endl; //stampo i numeri dopo la virgola con cast a int

    for (int i=0; i < nome.size(); i++){

        std::cout << nome[i] << std::endl;

    }

    for (int i=0; i < sizeof(array)/sizeof(array[0]); i++){
        //per iterare sulla dimensione dell'array devo fare cosi, solo sizeof mi restituisce il numero di byte occupati dall'array 
        //versione con c++17 --> for (int i=0; i < std::size(array); i++){
        array[i]= 20; 
        std::cout << array[i] << std::endl;

    }
    

    std::cout << "Inserisci un numero da 1 a 7"<< std::endl;
    std::cin >> giorno;
    
    switch (giorno)
    {
    case 1:
        std::cout << "Lunedi"<< std::endl;
        break;
    case 2:
        std::cout << "Martedi"<< std::endl;
        break;
    default:
        std::cout << "Numero che non corrisponde a nessun giorno"<< std::endl;
        break;
    }

    //std::cout << "ciao sono Lucia";


    string lettere = "ABCDEFGHI"; 

    for (int i=0; i< lettere.size(); i++) {

        for(int j=0;j<lettere.size(); j++){

            std::cout << lettere[j] << " "; 
        }
        std::cout << " \n" << std::endl; 
    }


    //PUNTATORI, salvo indirizzo di memoria di una variabile in una memoria 
    int prova=5; 
    int *prt_prova = &prova; //int perchè punto all'indirizzo di memoria di un int

    std::cout << prt_prova << std::endl; //stampo indirizzo
    std::cout << *prt_prova << std::endl; //stampo valore contenuto nell'indirizzo 

    *prt_prova=200; 
    std::cout << *prt_prova << std::endl; //cambio il valore contenuto in quell'indirizzo 

    //REFERNZE --> sono alias per le variabili
    //si usa questo concetto all'interno delle funzioni --> mi permette di baypassare lo scope 
    int ref=5;
    int &referenza_ref=ref; //devo subito assegnarla, non posso dichiararla vuota

    numeri.pop_back(); //elimino ultimo elemento vettore 
    numeri.push_back(50); //inserisco un elemento in coda al vettore 
    numeri.insert(numeri.begin()+1, 0); //inserisco zero in seconda posizione del vettore 

    return 0;
   
}

/*
int counter=0; 
while(condizione){ //finchè la condizione è vera eseguo il while e poi esco

    faccio cose 
    counter ++; 
}
*/
/*
//il do-while lo uso quando voglio che almeno una volta, cioè la prima, il ciclo venga eseguito 
do
{
    counter ++; 
}while (condizione); 

*/

//il continue nel ciclo for o while serve a saltare quella iterazione, passo all'iterazione successiva
//il break rompe il ciclo se si verifica una determinata cosa, si esce dal ciclo 
