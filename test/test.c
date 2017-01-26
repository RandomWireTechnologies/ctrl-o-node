// Test file to simulate NFC software

#include <stdio.h>
#include <stdlib.h>

#ifdef _WIN32
    #include <windows.h>
#else
    #include <unistd.h>
#endif

void wait( int seconds )
{   // Pretty crossplatform, both ALL POSIX compliant systems AND Windows
    #ifdef _WIN32
        Sleep( 1000 * seconds );
    #else
        sleep( seconds );
    #endif
}


int main( int argc, char **argv) {
    while (1) {
        wait(3);
        printf("deadbeef\n");
    }
    return 0;
}
