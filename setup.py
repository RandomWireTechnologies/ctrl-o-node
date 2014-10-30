from distutils.core import setup, Extension

module1 = Extension('pn532',
                    libraries = ['nfc','freefare'],
                    sources = ['pn532.c'])

setup (name = 'PN532',
       version = '1.0',
       description = 'This allow access to the PN532 through libnfc',
       ext_modules = [module1])
