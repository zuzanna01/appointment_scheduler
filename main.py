import sqlite3
import datetime
import Clinic_functions


# POŁĄCZENIE Z BAZĄ DANYCH
conn = sqlite3.connect('Clinic.sqlite ')
cur = conn.cursor()
Clinic_functions.update_availability_table()

# WŁAŚCIWY PROGRAM
end = 0
while end == 0:

    today = datetime.datetime.now()
    print("Dzisiaj: " + today.strftime("%x"))
    print("Witaj w naszej klinice, co chcesz zrobć?")

    try:
        # wybór co chcemy zrobić
        print(
            "(1)Chcę umówić wizytę \n(2)Chcę odwołać wizytę\n(3)Chcę zmienić termin mojej wizyty\n(4)Zamknij "
            "program\n-> wybierz numer: ")
        choice = int(input())

        # umawianie nowej wizyty
        if choice == 1:
            # wypisanie specjalizacji
            print('Nasi specjaliści:')
            cur.execute(' SELECT DISTINCT specialization FROM Doctors ')
            spec_dict = {}
            i = 1
            for row in cur:
                spec_dict[i] = row[0]
                i = i + 1
            print("{:<5} {:<10}".format('NUMER', 'SPECJALNOŚĆ'))
            for key, value in spec_dict.items():
                print("{:<5} {:<10}".format(str(key), str(value)))
            # wybór specjalisty z klawiatury
            print("Do którego specjalisty chcesz się umówić:\n-> wpisz numer specjalności:  ")
            spec_num = int(input())
            if spec_num > len(spec_dict) or spec_num < 1:
                raise ValueError

            spec = str(spec_dict.get(spec_num)).replace('(', '').replace(')', '').replace(',', '').replace("'", '')

            # wypisanie lekarzy danej specjalizacji
            cur.execute("SELECT * FROM Doctors WHERE specialization = ?", (spec,))

            chosen_spec = []
            print("{:<5} {:<10} {:<15} {:<10}".format('NUMER', 'IMIĘ', ' NAZWISKO', 'SPECJALNOŚĆ'))
            for row in cur:
                print("{:<5} {:<10} {:<15} {:<10}".format(row[0], row[1], row[2], row[3]))
                chosen_spec.append(int(row[0]))

            # wybór lekarza
            print("Do którego lekarza chcesz się umówić: -> podaj numer lekarza")

            nr_doctor = int(input())

            if nr_doctor not in chosen_spec:
                raise ValueError

            chosen = False

            app_id = Clinic_functions.make_appointment(nr_doctor)

            patient_idx = Clinic_functions.create_patient()

            # zapis wizyty do bazy danych
            cur.execute('UPDATE Appointments SET patient = ? WHERE ID_DATE = ?', (int(patient_idx), int(app_id)))
            conn.commit()

            Clinic_functions.write_appointment(app_id)

        elif choice == 2:

            print('Chcesz usunąć wizytę')
            patient_idx = Clinic_functions.get_patient()
            Clinic_functions.delete_appointment(0, patient_idx)

        elif choice == 3:

            print('Chcesz zmienić termin wizyty: ')
            patient_idx = Clinic_functions.get_patient()
            nr_doctor = Clinic_functions.delete_appointment(1, patient_idx)
            if nr_doctor != 0:
                app_id = Clinic_functions.make_appointment(nr_doctor)
                # zapis wizyty do bazy danych
                cur.execute('UPDATE Appointments SET patient = ? WHERE ID_DATE = ?', (int(patient_idx), int(app_id)))
                conn.commit()
                Clinic_functions.write_appointment(app_id)

        elif choice == 4:
            pass
        else:
            raise ValueError

        # pytamy czy zakończyć program
        print('Czy chcesz zrobić coś jeszcze?')
        print('t - tak, n - nie')
        end_str = input()
        end_str = end_str.lower()
        if end_str == 't':
            end = 0
        elif end_str == 'n':
            end = 1
        else:
            raise ValueError

    except ValueError:
        print("Podano nieprawidłową wartość!")
    finally:
        pass

cur.close()
