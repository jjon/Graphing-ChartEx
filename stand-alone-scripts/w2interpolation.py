#!/usr/bin/env python
# -*-coding: utf-8-*-
from StringIO import StringIO

# 
# f = open("/Users/jjc/Sites/brat-v1.2_The_Larch/data/wards2 with interpolations/Ward2_55_188_21.ann", "r")
# 
# interp1 = "by estimation one acre and a half more or less in Fordham, "
# 
# llist = f.readlines()
# repstring1 = '(details specified)'
# 
# l = len(interp1)
# 
# 
# listsin = [x.split('\t') for x in llist]
# loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring1][0][0])
# #this is where it fails if file or replacement string are missing or wrong
# 
# replist = [x for x in listsin if x[-1].strip() == repstring1]
# idx = listsin.index(replist[0])
# 
# entity,off1,off2 = tuple(replist[0][1].split())
# listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
# listsin[idx][2] = interp1 + '\n'
# 
# 
# for x in listsin:
#     if 'T' in x[0]:
#         start,end = map(int, x[1].split()[1:])
#         if start > loc:
#             s = x[1].replace(str(start), str(start + l - len(repstring1)))
#             s = s.replace(str(end), str(end + l - len(repstring1)))
#             x[1] = s
# 
# print ''.join(['\t'.join(x) for x in listsin])
#### works for Ward2_55_188_2
f = open("/Users/jjc/Sites/brat-v1.2_The_Larch/data/wards2 with interpolations/Ward2_55_188_24.ann", "r")

interp1 = "by estimation one acre and a half of land with all its appurtenances"


llist = f.readlines()
repstring1 = '(details specified)'
lenrepstring1 = len(repstring1)
l = len(interp1) - lenrepstring1

listsin = [x.split('\t') for x in llist]
loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring1][0][0])
#this is where it fails if file or replacement string are missing or wrong

replist = [x for x in listsin if x[-1].strip() == repstring1]
#['T15', 'Apparatus 283 301', 'location specified\n']
idx = listsin.index(replist[0])

entity,off1,off2 = tuple(replist[0][1].split())
listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
listsin[idx][2] = interp1 + '\n'


for x in listsin:
    if 'T' in x[0]:
        start,end = map(int, x[1].split()[1:])
        if start > loc:
            s = x[1].replace(str(start), str(start + l))
            s = s.replace(str(end), str(end + l))
            x[1] = s

interimString = ''.join(['\t'.join(x) for x in listsin])

##############

interp2 = "that is to say between the common commonly called Plummers Green on the eastern side and the lands of the said Robert Jenner, now in the tenure of Walter Jenner, on the western side and between the messuage or tenement of the same Robert Jenner, now in the tenure of the said Walter Jenner, on the southern side and the lands called Stubbings of Robert Potter of Wethermontford now in the tenure of John Spark, on the northern side; in accordance with already established metes and bounds"


repstring2 = '(location specified)'
lenrepstring2 = len(repstring2)
l = len(interp2) - lenrepstring2

stringIn = StringIO(interimString)

listsin = [x.split('\t') for x in stringIn]
loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring2][0][0])
#this is where it fails if file or replacement string are missing or wrong

replist = [x for x in listsin if x[-1].strip() == repstring2]
#['T15', 'Apparatus 283 301', 'location specified\n']
idx = listsin.index(replist[0])

entity,off1,off2 = tuple(replist[0][1].split())
listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
listsin[idx][2] = interp2 + '\n'


for x in listsin:
    if 'T' in x[0]:
        start,end = map(int, x[1].split()[1:])
        if start > loc:
            s = x[1].replace(str(start), str(start + l))
            s = s.replace(str(end), str(end + l))
            x[1] = s


print ''.join(['\t'.join(x) for x in listsin])

#### Ward2_55_188_7
# interp1 = "between the lands of Thomas Motanne called Chances on the north and the lands of John Pach on the south, one end abutting 'le Chancefenne' towards the west and the road leading from Potonbredge towards Yoyesbredge also towards the west."
# 
# llist = f.readlines()
# repstring1 = '(location specified)'
# 
# l = len(interp1)
# 
# 
# listsin = [x.split('\t') for x in llist]
# loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring1][0][0])
# #this is where it fails if file or replacement string are missing or wrong
# 
# replist = [x for x in listsin if x[-1].strip() == repstring1]
# idx = listsin.index(replist[0])
# 
# entity,off1,off2 = tuple(replist[0][1].split())
# listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
# listsin[idx][2] = interp1 + '\n'
# 
# 
# for x in listsin:
#     if 'T' in x[0]:
#         start,end = map(int, x[1].split()[1:])
#         if start > loc:
#             s = x[1].replace(str(start), str(start + l - len(repstring1)))
#             s = s.replace(str(end), str(end + l - len(repstring1)))
#             x[1] = s
# 
# print ''.join(['\t'.join(x) for x in listsin])
#### Ward2_55_188_6
# interp1 = "between the field called Holmefeld on one side and the king's highway called Polmerty on the other side"
# 
# llist = f.readlines()
# repstring1 = '(location specified)'
# 
# l = len(interp1)
# 
# 
# listsin = [x.split('\t') for x in llist]
# loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring1][0][0])
# #this is where it fails if file or replacement string are missing or wrong
# 
# replist = [x for x in listsin if x[-1].strip() == repstring1]
# idx = listsin.index(replist[0])
# 
# entity,off1,off2 = tuple(replist[0][1].split())
# listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
# listsin[idx][2] = interp1 + '\n'
# 
# 
# for x in listsin:
#     if 'T' in x[0]:
#         start,end = map(int, x[1].split()[1:])
#         if start > loc:
#             s = x[1].replace(str(start), str(start + l - len(repstring1)))
#             s = s.replace(str(end), str(end + l - len(repstring1)))
#             x[1] = s
# 
# print ''.join(['\t'.join(x) for x in listsin])
#### Ward2_55_188_5
# interp1 = "by estimate in total one acre and a half more or less in Fordham, that is to say to the common commonly called Plommers Green towards the east and the messuage and land belonging to myself the said Robert Jenner, and lately in the tenure of Walter Jenner, towards the south and west and the lands called Stubbings towards the north. And a field called Hearde by estimate in total three acres and a half, with its appurtenances, in Fordham,  that is to say between the lands of the heirs of the late John Abell, knight, on the eastern side and the tenement called Howdes on the western side."
# 
# llist = f.readlines()
# repstring1 = '(details specified)'
# 
# l = len(interp1)
# 
# 
# listsin = [x.split('\t') for x in llist]
# loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring1][0][0])
# #this is where it fails if file or replacement string are missing or wrong
# 
# replist = [x for x in listsin if x[-1].strip() == repstring1]
# idx = listsin.index(replist[0])
# 
# entity,off1,off2 = tuple(replist[0][1].split())
# listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
# listsin[idx][2] = interp1 + '\n'
# 
# 
# for x in listsin:
#     if 'T' in x[0]:
#         start,end = map(int, x[1].split()[1:])
#         if start > loc:
#             s = x[1].replace(str(start), str(start + l - len(repstring1)))
#             s = s.replace(str(end), str(end + l - len(repstring1)))
#             x[1] = s
# 
# print ''.join(['\t'.join(x) for x in listsin])
#### Ward2_55_188_4
# f = open("/Users/jjc/Sites/brat-v1.2_The_Larch/data/wards2 with interpolations/Ward2_55_188_4.ann", "r")
# 
# interp1 = "by estimate one acre and a half more or less in Fordham, that is to say to the common there called Plummers Green towards the east and the messuage and lands presently and lately of Robert Jenner towards the south and the west and to the lands called Stubbings towards the north: Moreover a field called Hearde, by estimate three acres more or less in Fordham, that is to say between the lands of the heirs of John Abell, knight, on the eastern side and the tenement called Howde on the western side:"
# 
# llist = f.readlines()
# repstring1 = '(details specified)'
# 
# l = len(interp1)
# 
# 
# listsin = [x.split('\t') for x in llist]
# loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring1][0][0])
# #this is where it fails if file or replacement string are missing or wrong
# 
# replist = [x for x in listsin if x[-1].strip() == repstring1]
# idx = listsin.index(replist[0])
# 
# entity,off1,off2 = tuple(replist[0][1].split())
# listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
# listsin[idx][2] = interp1 + '\n'
# 
# 
# for x in listsin:
#     if 'T' in x[0]:
#         start,end = map(int, x[1].split()[1:])
#         if start > loc:
#             s = x[1].replace(str(start), str(start + l - len(repstring1)))
#             s = s.replace(str(end), str(end + l - len(repstring1)))
#             x[1] = s
# 
# print ''.join(['\t'.join(x) for x in listsin])
# 
#### works for Ward2_55_188_3
# f = open("/Users/jjc/Sites/brat-v1.2_The_Larch/data/wards2 with interpolations/Ward2_55_188_3.ann", "r")
# 
# interp1 = "by estimate one acre and a half more or less in Fordham, that is to say to the common there called Plummers Green towards the east and the messuage and lands presently and lately of Robert Jenner towards the south and the west and to the lands called Stubbings towards the north: Moreover a field called Hearde, by estimate three acres more or less in Fordham, that is to say between the lands of the heirs of John Abell, knight, on the eastern side and the tenement called Howde on the western side:"
# 
# llist = f.readlines()
# repstring1 = '(details specified)'
# 
# l = len(interp1)
# 
# 
# listsin = [x.split('\t') for x in llist]
# loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring1][0][0])
# #this is where it fails if file or replacement string are missing or wrong
# 
# replist = [x for x in listsin if x[-1].strip() == repstring1]
# idx = listsin.index(replist[0])
# 
# entity,off1,off2 = tuple(replist[0][1].split())
# listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
# listsin[idx][2] = interp1 + '\n'
# 
# 
# for x in listsin:
#     if 'T' in x[0]:
#         start,end = map(int, x[1].split()[1:])
#         if start > loc:
#             s = x[1].replace(str(start), str(start + l - len(repstring1)))
#             s = s.replace(str(end), str(end + l - len(repstring1)))
#             x[1] = s
# 
# print ''.join(['\t'.join(x) for x in listsin])
#### works for Ward2_55_188_2
# f = open("/Users/jjc/Sites/brat-v1.2_The_Larch/data/wards2 with interpolations/Ward2_55_188_2.ann", "r")
# 
# interp1 = "by estimate four acres more or less"
# 
# 
# llist = f.readlines()
# repstring1 = '(details specified)'
# lenrepstring1 = len(repstring1)
# l = len(interp1) - lenrepstring1
# 
# 
# listsin = [x.split('\t') for x in llist]
# loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring1][0][0])
# #this is where it fails if file or replacement string are missing or wrong
# 
# replist = [x for x in listsin if x[-1].strip() == repstring1]
# #['T15', 'Apparatus 283 301', 'location specified\n']
# idx = listsin.index(replist[0])
# 
# entity,off1,off2 = tuple(replist[0][1].split())
# listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
# listsin[idx][2] = interp1 + '\n'
# 
# 
# for x in listsin:
#     if 'T' in x[0]:
#         start,end = map(int, x[1].split()[1:])
#         if start > loc:
#             s = x[1].replace(str(start), str(start + l))
#             s = s.replace(str(end), str(end + l))
#             x[1] = s
# 
# interimString = ''.join(['\t'.join(x) for x in listsin])
# 
# ##############
# 
# interp2 = ", from where said piece of land called Plomers extend itself from the green called Plomers Green on the eastern side, to the land called Stubbynges on the western side. And the said piece of land called Lynches abuts the wood called Fordham Fryth on the eastern side and on the king's highway called Holdesgrene, leading from the church of Fordham to the village of Wethermonford, on the western side"
# 
# 
# repstring2 = '(location specified)'
# lenrepstring2 = len(repstring2)
# l = len(interp2) - lenrepstring2
# 
# stringIn = StringIO(interimString)
# 
# listsin = [x.split('\t') for x in stringIn]
# loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring2][0][0])
# #this is where it fails if file or replacement string are missing or wrong
# 
# replist = [x for x in listsin if x[-1].strip() == repstring2]
# #['T15', 'Apparatus 283 301', 'location specified\n']
# idx = listsin.index(replist[0])
# 
# entity,off1,off2 = tuple(replist[0][1].split())
# listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
# listsin[idx][2] = interp2 + '\n'
# 
# 
# for x in listsin:
#     if 'T' in x[0]:
#         start,end = map(int, x[1].split()[1:])
#         if start > loc:
#             s = x[1].replace(str(start), str(start + l))
#             s = s.replace(str(end), str(end + l))
#             x[1] = s
# 
# 
# print ''.join(['\t'.join(x) for x in listsin])
##### works (w/the right interp1) on Ward2_55_188_1
# f = open("/Users/jjc/Sites/brat-v1.2_The_Larch/data/wards2 with interpolations/Ward2_55_188_2.ann", "r")
# 
# interp1 = "by estimate four acres more or less in Fordham"
# 
# # 458
# 
# llist = f.readlines()
# repstring1 = '(details specified'
# lenrepstring1 = len(repstring1)
# l = len(interp1) - lenrepstring1
# 
# 
# listsin = [x.split('\t') for x in llist]
# loc = int([x[1].split()[1:] for x in listsin if x[-1].strip() == repstring1][0][0])
# #this is where it fails if file or replacement string are missing or wrong
# 
# replist = [x for x in listsin if x[-1].strip() == repstring1]
# #['T15', 'Apparatus 283 301', 'location specified\n']
# idx = listsin.index(replist[0])
# 
# entity,off1,off2 = tuple(replist[0][1].split())
# listsin[idx][1] = ' '.join([entity,off1,str(int(off1)+l)])
# listsin[idx][2] = interp1 + '\n'
# 
# 
# for x in listsin:
#     if 'T' in x[0]:
#         start,end = map(int, x[1].split()[1:])
#         if start > loc:
#             s = x[1].replace(str(start), str(start + l))
#             s = s.replace(str(end), str(end + l))
#             x[1] = s
# 
# print ''.join(['\t'.join(x) for x in listsin])

