import os

path_input = "/home/cbuse/Desktop/php/php-src/Zend/"
for filename in os.listdir(path_input):
        if filename.endswith('.c') or filename.endswith('.h'):
            f = open(path_input+filename)
            str1 = "?"
            str2 = ":"
            if  f.read().find(str1) != -1:
               # if f.read().find(str1) != -1:
                print filename