#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#define BUFFSIZE 1024*10
#define SERVER_PORT 8000
char KEY[]="\xfa\x30\xc5\xe2\x6d\xce";
int KEY_LEN=6;
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

int main(int argc, char *argv[])
{
    int fd, new_fd, struct_len, numbytes,i;
    struct sockaddr_in server_addr;
    struct sockaddr_in client_addr;
    char buff[BUFFSIZE];

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;
    bzero(&(server_addr.sin_zero), 8);
    struct_len = sizeof(struct sockaddr_in);

    fd = socket(AF_INET, SOCK_STREAM, 0);

    int opt = 1;
    if(setsockopt(fd, SOL_SOCKET,SO_REUSEADDR, (const void *) &opt, sizeof(opt))){
        perror("setsockopt");
        return -1;
    }
    while(bind(fd, (struct sockaddr *)&server_addr, struct_len) == -1);
    printf("Bind Success!\n");
    while(listen(fd, 10) == -1);
    printf("Listening on %d port...\n",SERVER_PORT);
    char recvBuff[BUFFSIZE];
    while(1)
    {
        numbytes = 0;
        int nt = 0;
        new_fd = accept(fd, (struct sockaddr *)&client_addr, (socklen_t *)&struct_len);
        while (1)
        {
            nt = recv(new_fd,&recvBuff,BUFFSIZE,0);
            if(nt==0)
                break;
            printf("recv data size %d\n",nt);
            Encry(recvBuff,nt);
            nt = send(new_fd,(const char*)recvBuff,nt,0);
            printf("send data size %d\n",nt);
        }
        
        
        close(new_fd);
        //break;

    }
    close(fd);
    return 0;
}