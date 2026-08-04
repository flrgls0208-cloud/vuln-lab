#include <stdio.h>
void main(){
    int a =5;
    int b= 3;
    int result = a&b;

    for(int i=7; i<=0; i--){
        printf("%d",(result >> i)&1)
    }
}