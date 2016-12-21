// To compile this simple example:
// $ gcc -o nfc nfc.c -lnfc

#include <stdlib.h>
#include <nfc/nfc.h>
#include <signal.h>

nfc_context *g_context = NULL;
nfc_device *g_device = NULL;


struct {
    bool interactive;
} write_options = {
    .interactive = true
};

const nfc_modulation nmModulations[5] = {
    { .nmt = NMT_ISO14443A, .nbr = NBR_106 },
//  { .nmt = NMT_ISO14443B, .nbr = NBR_106 },
//  { .nmt = NMT_FELICA, .nbr = NBR_212 },
//  { .nmt = NMT_FELICA, .nbr = NBR_424 },
//  { .nmt = NMT_JEWEL, .nbr = NBR_106 },
};
const size_t szModulations = 1;

static void stop_polling(int sig)
{
  (void) sig;
  if (g_device != NULL)
    nfc_abort_command(g_device);
  else {
    nfc_exit(g_context);
    exit(EXIT_FAILURE);
  }
}

void print_hex_buffer(char *data,uint8_t length)
{
	if (length == 0)
	{
		while (*data != 0)
		{
			printf("%02X",*data++);
		}
	}
	else
	{
		while (length > 0)
		{
			printf("%02X",*data++);
			length--;
		}
	}
}

//typedef struct {
//  uint8_t  abtAtqa[2];
//  uint8_t  btSak;
//  size_t  szUidLen;
//  uint8_t  abtUid[10];
//  size_t  szAtsLen;
//  uint8_t  abtAts[254]; // Maximal theoretical ATS is FSD-2, FSD=256 for FSDI=8 in RATS
//} nfc_iso14443a_info;



void print_nfc_target(nfc_target* nt)
{
    size_t len = nt->nti.nai.szUidLen;
    char *uid = nt->nti.nai.abtUid;
    if (nt == 0) {
        return;
    }
    if (nt->nti.nai.btSak == 8) {
        printf("UID:");
        print_hex_buffer(uid,len);
        printf("\r\n");
    }
    
//    printf("ATQ:");
//    print_hex_buffer(nt->nti.nai.abtAtqa,2);
//    printf("\r\n");
//    printf("btSak:%d\r\n",nt->nti.nai.btSak);
//    printf("ATS:");
//    print_hex_buffer(nt->nti.nai.abtAts,nt->nti.nai.szAtsLen);
//    printf("\r\n");
}

bool readTag(void)
{
    nfc_target nt;
    int res = 0;
    
    const uint8_t uiPollNr = 255;
    const uint8_t uiPeriod = 1;
    
    if ((res = nfc_initiator_poll_target(g_device, nmModulations, szModulations, uiPollNr, uiPeriod, &nt))  < 0) {
        return false;
    }

    if (res > 0) {
        //print_nfc_target(&nt, verbose);
        print_nfc_target(&nt);
        res = nfc_initiator_target_is_present(g_device, &nt);
        while (0 == res) {
            // Check to make sure we don't get stuck in here?    
            res = nfc_initiator_target_is_present(g_device, &nt);
        }
        //printf("target present response:%d\r\n",res);
        if ((res == -1) || (res == -7)) {
            return false;
        } else {
            return true;
        }
    } else {
        printf("ERR: Failed to find tag with error code %d\r\n",res);
        return false;
    }
}

int main(int argc, char *argv[]) {
    
    signal(SIGINT, stop_polling);
    
	// Init NFC
	nfc_init(&g_context);
	if (g_context == NULL) {
		// Error?
		printf("ERR: Couldn't Init NFC\r\n");
		return -1;
	}
	g_device = nfc_open(g_context, "pn532_uart:/dev/ttyAMA0");
	
	if (g_device == NULL) {
		// Error?
		printf("ERR: Couldn't Open NFC port\r\n");
		return -1;
	}
	// Set opened NFC device to initiator mode
	if (nfc_initiator_init(g_device) < 0) {
		// Error?
		printf("ERR: Couldn't setup NFC module\r\n");
    	return -1;
	}

    bool keepRunning = true;
	while(keepRunning)
	{
		keepRunning = readTag();
	}
	return 0;
}
