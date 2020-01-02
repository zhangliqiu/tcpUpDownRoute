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
#define BUFFSIZE 1024 * 10
#define SERVER_PORT 9999
char KEY[] = "\xfa\x30\xc5\xe2\x6d\xce";
int KEY_LEN = 6;
int readList[20];
int readLen = 0;
int readTop = -1;
int BigFd = 0;
fd_set readFd;
int getSelectFd(int list[], int len)
{
    int i;
    int re = list[0];
    for (i = 0; i < len; i++)
    {
        if (list[i] > re)
            re = list[i];
    }
    return re+1;
}
void readListAdd(int fd)
{
    readLen++;
    readTop++;
    readList[readTop] = fd;

    BigFd = getSelectFd(readList,readLen);
}
void readListDelFd(int fd)
{
    // modefy the list
    int i = 0;
    for (i = 0; i < readLen; i++)
    {
        if (readList[i] == fd)
        {
            int j = i;
            for (; j < readLen - 1; j++)
            {
                readList[j] = readList[j + 1];
            }
            break;
        }
    }
    readLen--;
    readTop--;

    BigFd = getSelectFd(readList,readLen);

    // modefy the readFd
}

void putReadListToFd()
{
    FD_ZERO(&readFd);
    int i;
    for(i=0;i<readLen;i++)
    {
        FD_SET(readList[i],&readFd);
    }
}
void Encry(char *buff, int len)
{

    int i = 0;
    int j = 0;
    for (; i < len; i++)
    {
        if (j == KEY_LEN)
            j = 0;
        buff[i] = buff[i] ^ KEY[j];

        j++;
    }
}

int main(int argc, char *argv[])
{
    int serverFd, new_fd, struct_len, numbytes, i;
    struct sockaddr_in server_addr;
    struct sockaddr_in client_addr;

    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    server_addr.sin_addr.s_addr = INADDR_ANY;
    bzero(&(server_addr.sin_zero), 8);
    struct_len = sizeof(struct sockaddr_in);

    serverFd = socket(AF_INET, SOCK_STREAM, 0);

    int opt = 1;
    if (setsockopt(serverFd, SOL_SOCKET, SO_REUSEADDR, (const void *)&opt, sizeof(opt)))
    {
        perror("setsockopt");
        return -1;
    }
    while (bind(serverFd, (struct sockaddr *)&server_addr, struct_len) == -1)
        ;
    printf("Bind Success!\n");
    while (listen(serverFd, 10) == -1)
        ;
    printf("Listening on %d port...\n", SERVER_PORT);

    readListAdd(serverFd);
    putReadListToFd();
    struct sockaddr clientAddr;
    int sockaddrlen = sizeof(clientAddr);
    char buff[BUFFSIZE];
    int recvSize = 0;
    
    while (select(BigFd, &readFd, NULL, NULL, NULL) != -1)
    {
        printf("look !! there is some thing happed that you not notice !\n");
        int i,fd;
        for(i=0;i<readLen;i++)
        {
            fd = readList[i];
            if(FD_ISSET(fd,&readFd))
            {
                printf("cool we find the fd that triger event\n");
                if(fd == serverFd)
                {
                    printf("serverfd triger the event,that meaning there is a connecting,let's accept it ,go\n");
                    int clientFd=-1;
                    clientFd = accept(serverFd,&clientAddr,(socklen_t*)&sockaddrlen);
                    printf("now we have accept the connection. %d\n",clientFd);
                    readListAdd(clientFd);
                }
                else
                {
                    printf("clientfd triger the event,that mean the client send somedata to us,or it disconnected with us\n");
                    recvSize = recv(fd,buff,BUFFSIZE,0);
                    if(recvSize>0)
                    {
                        printf("clientfd send %d bytes to us\n",recvSize);
                        Encry(buff,recvSize);
                        send(fd,buff,recvSize,0);
                    }
                    else
                    {
                        printf("clientfd disconnected\n");
                        readListDelFd(fd);
                    }
                    
                }
                
            }
        }
        putReadListToFd();
        printf("\n\n");
    }

    close(serverFd);
    return 0;
}