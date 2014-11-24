/*
* @file quick_start_example1.c
* @brief Quick start example that presents how to use libnfc
*/

// To compile this simple example:
// $ gcc -o quick_start_example1 quick_start_example1.c -lnfc
#include <Python.h>

#include <stdlib.h>
#include <nfc/nfc.h>
#include <freefare.h>
#include mifare_key.h

nfc_context *g_context = NULL;
nfc_device *g_device = NULL;


MifareClassicKey default_keys[] = {
    { 0xff,0xff,0xff,0xff,0xff,0xff },
    { 0xd3,0xf7,0xd3,0xf7,0xd3,0xf7 },
    { 0xa0,0xa1,0xa2,0xa3,0xa4,0xa5 },
    { 0xb0,0xb1,0xb2,0xb3,0xb4,0xb5 },
    { 0x4d,0x3a,0x99,0xc3,0x51,0xdd },
    { 0x1a,0x98,0x2c,0x7e,0x45,0x9a },
    { 0xaa,0xbb,0xcc,0xdd,0xee,0xff },
    { 0x00,0x00,0x00,0x00,0x00,0x00 }
};

struct mifare_classic_key_and_type {
    MifareClassicKey key;
    MifareClassicKeyType type;
};

struct {
    bool interactive;
} write_options = {
    .interactive = true
};

const MifareClassicKey default_keyb = MIFARE_KEY;


const MifareClassicKey data_key = MIFARE_KEY;

#define MSG_SIZE_OFFSET 2
#define MSG_DATA_OFFSET 5
const uint8_t ndef_default_msg[37] = {
    0xd1, 0x02, 0x20, 0x73, 0x68, 
    0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 
    0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 
    0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x30, 
    0x31, 0x32
};

static int
search_sector_key (MifareTag tag, MifareClassicSectorNumber sector, MifareClassicKey *key, MifareClassicKeyType *key_type)
{
    MifareClassicBlockNumber block = mifare_classic_sector_last_block (sector);

    /*
    * FIXME: We should not assume that if we have full access to trailer block
    *        we also have a full access to data blocks.
    */
    mifare_classic_disconnect (tag);
    if ((0 == mifare_classic_connect (tag)) && (0 == mifare_classic_authenticate (tag, block, data_key, MFC_KEY_B))) {
        memcpy (key,data_key,sizeof (MifareClassicKey));
        *key_type = MFC_KEY_B;
        return 1;
    }
    mifare_classic_disconnect (tag);
    
    size_t i;
    for (i = 0; i < (sizeof (default_keys) / sizeof (MifareClassicKey)); i++) {
        if ((0 == mifare_classic_connect (tag)) && (0 == mifare_classic_authenticate (tag, block, default_keys[i], MFC_KEY_A))) {
            //printf("Authenticated with default key A #%d\n",i);
            if ((1 == mifare_classic_get_trailer_block_permission (tag, block, MCAB_WRITE_KEYA, MFC_KEY_A)) &&
                (1 == mifare_classic_get_trailer_block_permission (tag, block, MCAB_WRITE_ACCESS_BITS, MFC_KEY_A)) &&
                (1 == mifare_classic_get_trailer_block_permission (tag, block, MCAB_WRITE_KEYB, MFC_KEY_A))) {
                    memcpy (key, &default_keys[i], sizeof (MifareClassicKey));
                    *key_type = MFC_KEY_A;
                    return 1;
            } else {
                uint8_t a,b,access;
                a = mifare_classic_get_trailer_block_permission (tag, block, MCAB_WRITE_KEYA, MFC_KEY_A);
                b = mifare_classic_get_trailer_block_permission (tag, block, MCAB_WRITE_KEYB, MFC_KEY_A);
                access = mifare_classic_get_trailer_block_permission (tag, block, MCAB_WRITE_ACCESS_BITS, MFC_KEY_A);
                //printf ("Block permissions = %d,%d,%d\n",a,b,access);
            }
        }
        mifare_classic_disconnect (tag);

        if ((0 == mifare_classic_connect (tag)) && (0 == mifare_classic_authenticate (tag, block, default_keys[i], MFC_KEY_B))) {
            //printf("Authenticated with default key B #%d\n",i);
            if ((1 == mifare_classic_get_trailer_block_permission (tag, block, MCAB_WRITE_KEYA, MFC_KEY_B)) &&
                (1 == mifare_classic_get_trailer_block_permission (tag, block, MCAB_WRITE_ACCESS_BITS, MFC_KEY_B)) &&
                (1 == mifare_classic_get_trailer_block_permission (tag, block, MCAB_WRITE_KEYB, MFC_KEY_B))) {
                    memcpy (key, &default_keys[i], sizeof (MifareClassicKey));
                    *key_type = MFC_KEY_B;
                    return 1;
            }
        }
        mifare_classic_disconnect (tag);
    }
    return 0;
}

static int
fix_trailer_block (MifareTag tag, MifareClassicSectorNumber sector, MifareClassicKey key, MifareClassicKeyType key_type)
{
    MifareClassicBlock block;
    mifare_classic_trailer_block (&block, mad_public_key_a, 0x6, 0x6, 0x6, 0x6, 0x00, data_key);
    if (mifare_classic_authenticate (tag, mifare_classic_sector_last_block (sector), key, key_type) < 0) {
        //printf("Failed to authenticate\n");
	    return -1;
    }
    if (mifare_classic_write (tag, mifare_classic_sector_last_block (sector), block) < 0) {
        //printf("Failed to write\n");
	    return -1;
    }
    return 0;
}

static PyObject* pn532_init(PyObject *self) {
    // Initialize libnfc and set the nfc_context
    nfc_init(&g_context);
    if (g_context == NULL) {
        // Error?
        return Py_BuildValue("i", 0);
    }
    g_device = nfc_open(g_context, NULL);

    if (g_device == NULL) {
        // Error?
        return Py_BuildValue("i", 0);
    }
    // Set opened NFC device to initiator mode
    if (nfc_initiator_init(g_device) < 0) {
        // Error?
        return Py_BuildValue("i", 0);
    }
    
    return Py_BuildValue("i", 1);
}

static PyObject* pn532_close(PyObject *self) {
    // Close NFC device
    nfc_close(g_device);
    // Release the context
    nfc_exit(g_context);
    return Py_BuildValue("i", 1);
}

const nfc_modulation nmMifare = {
        .nmt = NMT_ISO14443A,
        .nbr = NBR_106,
    };


static PyObject* pn532_format(PyObject *self, PyObject *args) {
    MifareTag *tags = NULL;
    MifareClassicKey key;
    MifareClassicKeyType key_type;

    tags = freefare_get_tags (g_device);
    if ((tags == NULL) || (tags[0] == 0 )) {
        // Error?
        return Py_BuildValue("s","No card found");
    }
    //tag_uid = freefare_get_tag_uid(tags[0]);
    if (0 != mifare_classic_connect (tags[0])) {
        // Error
        return Py_BuildValue("s","Failed to Connect");
    }
    if (!search_sector_key(tags[0], 3, &key, &key_type)) {
        return Py_BuildValue("s","Failed to find Auth key");
    }
    if (0 != mifare_classic_format_sector (tags[0], 3)) {
        // Error
        return Py_BuildValue("s","Failed to Format Sector");
    }
    if (!search_sector_key(tags[0], 3, &key, &key_type)) {
        return Py_BuildValue("s","Failed to find Auth key");
    }
    if (0 != fix_trailer_block (tags[0], 3, key, key_type)) {
        // Error
        return Py_BuildValue("s","Failed to write trailer block");
    }
    mifare_classic_disconnect (tags[0]);

    freefare_free_tags(tags);
    return Py_BuildValue("i",1);;
}

static PyObject* pn532_format_blank(PyObject *self, PyObject *args) {
    MifareTag *tags = NULL;
    MifareClassicKey key;
    MifareClassicKeyType key_type;

    tags = freefare_get_tags (g_device);
    if ((tags == NULL) || (tags[0] == 0 )) {
        // Error?
        return Py_BuildValue("s","No card found");
    }
    //tag_uid = freefare_get_tag_uid(tags[0]);
    if (0 != mifare_classic_connect (tags[0])) {
        // Error
        return Py_BuildValue("s","Failed to Connect");
    }
    if (!search_sector_key(tags[0], 3, &key, &key_type)) {
        return Py_BuildValue("s","Failed to find Auth key");
    }
    if (0 != mifare_classic_format_sector (tags[0], 3)) {
        // Error
        return Py_BuildValue("s","Failed to Format Sector");
    }
    mifare_classic_disconnect (tags[0]);

    freefare_free_tags(tags);
    return Py_BuildValue("i",1);;
}


static PyObject* pn532_read(PyObject *self, PyObject *args) {
    MifareTag *tags = NULL;
    char *tag_uid = 0;
    uint8_t buffer[64];
    MifareClassicBlock data;

    // Select tag presence to block until a tag is available
    //if (nfc_initiator_select_passive_target(g_device, nmMifare, NULL, 0, &nt) > 0) {
        // Read Tag
    tags = freefare_get_tags (g_device);
    
    if ((tags == NULL) || (tags[0] == 0 )) {
        // Error?
        return Py_BuildValue("");
    }
    tag_uid = freefare_get_tag_uid(tags[0]);
    if (0 != mifare_classic_connect (tags[0])) {
        // Error
        PyObject *resp = Py_BuildValue("ss",tag_uid,"Failed to Connect");
        free(tag_uid);
        freefare_free_tags(tags);
        return resp;
    }
    if (0 != mifare_classic_authenticate (tags[0], 12, data_key, MFC_KEY_B)) {
        // Error
        PyObject *resp = Py_BuildValue("ss",tag_uid,"Failed to Authenticate");
        free(tag_uid);
        freefare_free_tags(tags);
        return resp;
    }
    if (0 != mifare_classic_read(tags[0],12,data)) {
        // Error
        PyObject *resp = Py_BuildValue("ss",tag_uid,"Failed to read data");
        free(tag_uid);
        freefare_free_tags(tags);
        return resp;
    }
    memcpy(buffer,data,16);
    if (0 != mifare_classic_authenticate (tags[0], 13, data_key, MFC_KEY_B)) {
        // Error
        PyObject *resp = Py_BuildValue("ss",tag_uid,"Failed to Authenticate");
        free(tag_uid);
        freefare_free_tags(tags);
        return resp;
    }
    if (0 != mifare_classic_read(tags[0],13,data)) {
        // Error
        PyObject *resp = Py_BuildValue("ss",tag_uid,"Failed to read data");
        free(tag_uid);
        freefare_free_tags(tags);
        return resp;
    }
    memcpy(buffer+16,data,16);
    //}
    PyObject *resp =Py_BuildValue("ss#",tag_uid,buffer,32);
    free(tag_uid);
    freefare_free_tags(tags);
    return resp;
}

static PyObject* pn532_write(PyObject *self, PyObject *args) {
    MifareTag *tags = NULL;
    MifareClassicBlock data;
    
    const char* input_data;
    int input_len;
    
    if (!PyArg_ParseTuple(args,"s#",&input_data,&input_len)) {
        return Py_BuildValue("i", -7);
    }

    if (input_len <= 0) {
        return Py_BuildValue("s", "Invalid Data Length");
    }
    memset(&data,0,16);
    if (input_len<16) {
        memcpy(&data,input_data,input_len);
    } else {
        memcpy(&data,input_data,16);
    }
    tags = freefare_get_tags (g_device);
	if (!tags) {
	    //nfc_close (device);
	    //printf("No tag found\n");
		return Py_BuildValue("s", "No tag found");
	}
	if (tags[0] == 0) {
	    return Py_BuildValue("s","Failed to get tag");
	}
    if (0 != mifare_classic_connect (tags[0])) {
        // Error
        return Py_BuildValue("s","Failed to Connect");
    }
    if (0 != mifare_classic_authenticate (tags[0], 12, data_key, MFC_KEY_B)) {
        // Error
        return Py_BuildValue("s","Failed to Authenticate");
    }
    if (0 != mifare_classic_write(tags[0],12,&data)) {
        // Error
        return Py_BuildValue("s","Failed to write data");
    }
    if (input_len > 16) {
        if (input_len<32) {
            memcpy(&data,input_data+16,input_len-16);
        } else {
            memcpy(&data,input_data+16,16);
        }
        if (0 != mifare_classic_authenticate (tags[0], 13, data_key, MFC_KEY_B)) {
            // Error
            return Py_BuildValue("s","Failed to Authenticate");
        }
        if (0 != mifare_classic_write(tags[0],13,&data)) {
            // Error
            return Py_BuildValue("s","Failed to write data");
        }
    }
    
	return Py_BuildValue("i", 0);
}

static PyObject* pn532_none(PyObject *self, PyObject *args) {
    return Py_BuildValue("");
}

static PyMethodDef PN532Methods[] = {
    {"init",    pn532_init, METH_VARARGS,"Initialize Reader."},
    {"format",  pn532_format, METH_VARARGS,"Format and key data sector."},
    {"format_blank",  pn532_format_blank, METH_VARARGS,"Format data sector, blank."},
    {"read",    pn532_read, METH_VARARGS,"Wait for a card and read it's serial and hash."},
    {"write",   pn532_write, METH_VARARGS,"Write a new hash to a specific card."},
    {"none",   pn532_none, METH_VARARGS,"None"},
    {"close",   pn532_close, METH_VARARGS,"Close Reader"},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initpn532(void) {
    (void) Py_InitModule("pn532", PN532Methods);
}

int main(int argc, char *argv[]) {
    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(argv[0]);
    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();
    /* Add a static module */
    initpn532();

}
