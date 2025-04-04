
#include <stdio.h>

int main (){

    char nome[10];
    snprintf(nome, sizeof(nome), "%s" ,"lucia");
    printf("Nome: %s\n", nome);

}