from datetime import date, datetime
tab = [[41, 141], [54, 23]]

for row in tab:
    print(row[0], row[1])


print(datetime.now())

mmm = {1: 'Badanie', 2: 'Montaż', 3: 'Palenie'}
for m in mmm:
    print(m, mmm[m])

print(mmm)

ludzie = {7: {'imie': 'Asia', 'nazwisko': 'Katarzyna', 'stanowisko': 1, 'uprawienia': 3}, 8: {'imie': 'agnieszka', 'nazwisko': 'Nowak',
                                                                                              'stanowisko': 1, 'uprawienia': 1}, 19: {'imie': 'Kamil', 'nazwisko': 'Wnuk', 'stanowisko': 2, 'uprawienia': 3}}
for i in ludzie:
    print(ludzie[i]['imie'] + ' ' + ludzie[i]['nazwisko'])
    print("\n")

print(ludzie[7]['imie'])
