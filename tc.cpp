#include <stdio.h>
char KEY[]="1234";
int KEY_LEN=4;
void Encry(char* buff,int len)
{

    int i = 0;
    int j = 0;
    for(;i<len;i++)
    {
        if(j==KEY_LEN)
            j=0;
        buff[i] = buff[i]^KEY[j];

        j++;
    }
}
int main()
{
    char aa[]="\xff";
    printf("%hhd\n",aa[0]);
    return 0;
}