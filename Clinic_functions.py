import sqlite3
import re
import datetime


def delete_appointment(i, patient_idx):
    """ This function deletes previously made appointment.
    In Appointments table in Clinic.sqlite database sets
    value of patient column  back to NULL.

    Parameters
    ----------
    i : int
        if equals 1 function checks and saves in nr_doctor variable with what doctor was the deleted appointment made
    patient_idx : int
        Contains value of patient column from Appointments (ID_PATIENT) whose appointment we want to remove

    Raises
    ------
    ValueError
        If the user enters invalid appointment number (ID_DATE) - not his/her

    Returns
    -------
    nr_doctor
        Contains value of doctor column from Appointments (ID_DOCTOR) for the deleted appointment, if i==1

    """
    conn = sqlite3.connect('Clinic.sqlite')
    cur = conn.cursor()

    ok = False

    cur.execute('SELECT ID_DATE, date, hour FROM Appointments WHERE patient=?', (patient_idx,))
    exist = cur.fetchall()
    if not exist:
        print("Nie masz zaplanowanych wizyt")
        return 0
    chosen_visit = []
    for row in exist:
        print(row)
        chosen_visit.append(row[0])

    while not ok:
        try:
            print('Wpisz numer wizyty, którą chcesz odwolać:')
            app_id = input()
            if int(app_id) not in chosen_visit:
                raise ValueError

            cur.execute('UPDATE Appointments SET patient = NULL WHERE ID_DATE = ?', (int(app_id),))

            print('Twoja wizyta została odwołana')
            ok = True
        except ValueError:
            print("Niewłaściwy numer wizyty")
        finally:
            pass

    if i == 1:
        cur.execute('SELECT doctor FROM Appointments WHERE ID_DATE=?', (app_id,))
        for row in cur:
            nr_doctor = row[0]

        conn.commit()
        cur.close()
        conn.close()
        return nr_doctor

    conn.commit()
    cur.close()
    conn.close()


def create_patient():
    """ This function adds new patient into Patients table
    in Clinic.sqlite database.

    Raises
    ------
    IndexError
        If entered pesel variable from console doesn't match pattern

    sqlite3.IntegrityError
        If entered pesel already exists under different name in database

    Returns
    -------
    patient_id
        Contains key value of added patient
    """
    conn = sqlite3.connect('Clinic.sqlite')
    cur = conn.cursor()

    print("W celu umówienia wizyty podaj dane:")
    # dane: imie nazwisko pesel wiek
    patient_name = input('Imie:').upper()
    patient_last_name = input('Nazwisko:').upper()
    ok = False

    while not ok:
        try:
            pesel = input('PESEL:')
            pattern_pesel = "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]"

            if not bool(re.match(pattern_pesel, pesel)):
                raise IndexError

            cur.execute('SELECT * FROM Patients WHERE first_name = ? AND last_name = ? AND pesel = ?',
                        (patient_name, patient_last_name, pesel))

            exist = cur.fetchall()

            if not exist:
                cur.execute('INSERT INTO Patients (first_name , last_name , pesel ) VALUES (? , ?, ?)',
                            (patient_name, patient_last_name, pesel))

            cur.execute('SELECT ID_PATIENT FROM Patients WHERE first_name = ? AND last_name = ? AND pesel = ?',
                        (patient_name, patient_last_name, pesel))
            for row in cur:
                patient_id = row[0]

            ok = True
        except IndexError:
            print("Nieprawidłowy numer pesel!")
        except sqlite3.IntegrityError:
            print("Pesel znajduje się w naszej bazie pod innym pacjentem!")
        finally:
            pass

    conn.commit()
    cur.close()
    conn.close()

    return patient_id


def get_patient():
    """ This function returns existing patient's ID_PATIENT.
    Firstly, it asks user for his/her 'pesel' and
    looks for match in Patients table in Clinic.sqlite database.

    Raises
    ------
    IndexError
        If entered pesel doesn't match pesel pattern
        If entered pesel doesn't exist in data base

    Returns
    -------
    patient_id
        Contains key value of the found patient
    """
    conn = sqlite3.connect('Clinic.sqlite')
    cur = conn.cursor()
    pattern_pesel = "[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]"

    ok = False
    while not ok:
        try:
            pesel = input("Podaj PESEL: ")
            if not bool(re.match(pattern_pesel, pesel)):
                raise IndexError
            cur.execute('SELECT ID_PATIENT FROM Patients WHERE pesel=?', (pesel,))
            exist = cur.fetchall()
            if not exist:
                raise IndexError
            for row in exist:
                patient_id = int(row[0])
            ok = True
        except IndexError:
            print("Nieprawidłowy numer pesel!")
        finally:
            pass

    cur.close()
    conn.close()
    return patient_id


def make_appointment(doctor_number):
    """ This function makes an appointment.
    In a table Appointments in Clinic.sqlite database sets
    patient column value to patient key.

    Parameters
    ----------
    doctor_number : int
        Contains key value of doctor with who we want to make an appointment
    Raises
    ------
    IndexError
        If user enters incorrectly formatted date or time
        If user enters unavailable date or time

    Returns
    -------
    app_id
        Contains key value of the created appointment
    """
    chosen = False
    while not chosen:
        try:
            conn = sqlite3.connect('Clinic.sqlite')
            cur = conn.cursor()

            print("Dokonujemy rejestracji tylko na najbliższe 30 dni. Wpisz interesujący Cię termin:")
            # podanie konkretnej daty
            dat = input("Data w formacie yyyy-mm-dd: ")
            date_pattern = "202[2-3]-[0-1][0-9]-[0-3][0-9]"
            if not bool(re.match(date_pattern, dat)):
                raise IndexError

            # wypisanie dostępnych godzin
            cur.execute('SELECT * FROM Appointments WHERE date = ? AND doctor = ? AND patient IS NULL',
                        (str(dat), doctor_number))

            exist = cur.fetchall()

            if exist:
                print("\nTerminy dostępne tego dnia:")
                chosen_date = []
                for row in exist:
                    print(row[1] + ", " + row[2])
                    chosen_date.append(row[2])

                time = input("Przepisz interesującą Cię godzinę z wyświetlonych: ")
                if time not in chosen_date:
                    raise IndexError

                cur.execute(
                    'SELECT * FROM Appointments WHERE date = ? AND doctor = ? AND patient IS NULL AND hour = ?',
                    (str(dat), doctor_number, str(time)))

                for row in cur:
                    print(row[1] + ", " + row[2])
                    app_id = row[0]

                print("Czy na pewno chcesz się zarejestrować na ten termin?\n")
                choice = input("t - tak, inny przycisk - nie, powrót do wyboru terminu \n")
                if choice == 't':
                    chosen = True

            else:
                print("\nNa tę chwilę nie ma dostępnych wolnych terminów na ten dzień. Wybierz inny. \n")
        except IndexError:
            print("Niewłaściwy format daty/godziny!")
        finally:
            pass

    cur.close()
    conn.close()

    return app_id


def write_appointment(app_id):
    """ This function writes information about existing appointment to console

    Parameters
    ----------
    app_id : int
        Key value of the appointment we want to get information about

    """
    conn = sqlite3.connect('Clinic.sqlite')
    cur = conn.cursor()

    print("Twoja wizyta:")

    cur.execute(' SELECT doctor, patient FROM Appointments WHERE ID_DATE=?', (app_id,))
    for row in cur:
        nr_doctor = row[0]
        nr_patient = row[1]
        break
    cur.execute('SELECT * FROM Doctors WHERE ID_DOCTOR= ?', (nr_doctor,))
    for row in cur:
        print(row)
    cur.execute('SELECT * FROM Patients WHERE ID_PATIENT= ?', (nr_patient,))
    for row in cur:
        print(row)
    cur.execute('SELECT date, hour FROM Appointments WHERE ID_DATE=?', (app_id,))
    for row in cur:
        print(row)

    cur.close()
    conn.close()


def create_hour_list(start_hour, end_hour):
    """ This function creates list of available appointment hours in the clinic

    Parameters
    ----------
    start_hour : int
        Hour of begining of first appointment in a day
    end_hour : int
        Hour of ending of last appointment in a day

    Returns
    -------
    hours
        List of starting hours of appointments
    """
    hours = []
    # creating a list of times
    for i in range(start_hour, end_hour):
        hours.append(f"{i}:00")
    return hours


def update_availability_table():
    """ This function updates Appointments table in Clinic.sqlite
    so that it always contains all possible appointments for the next
    30 days (starting from tomorrow). It ignores weekends.

    """
    conn = sqlite3.connect('Clinic.sqlite')
    cur = conn.cursor()

    cur.execute('SELECT DISTINCT date FROM Appointments')
    date_list = []

    for i in cur:
        date_list.append(datetime.datetime.strptime(
            str(i).replace('(', '').replace(')', '').replace(',', '').replace("'", ''), '%Y-%m-%d').date())

    today = datetime.date.today()
    if date_list[0] != today + datetime.timedelta(days=1):
        start_date = today + datetime.timedelta(days=1)
        end_date = today + datetime.timedelta(days=30)
        start_hour = 9
        end_hour = 15
        hours = create_hour_list(start_hour, end_hour)
        cur2 = conn.cursor()

        i = 0
        while date_list[i] < start_date:
            cur.execute('DELETE FROM Appointments WHERE date = ? ', (str(date_list[i]),))
            i = i + 1

        last_date = date_list[-1]

        while last_date != end_date:
            cur.execute(' SELECT ID_DOCTOR FROM Doctors ')
            last_date = last_date + datetime.timedelta(days=1)
            if last_date.weekday() != 5 and last_date.weekday() != 6:
                for i in cur:
                    for k in hours:
                        cur2.execute('INSERT INTO Appointments (date, hour, doctor) VALUES (?, ?, ?)',
                                     (str(last_date), k, sum(i)))

        conn.commit()
        cur.close()
        cur2.close()
        conn.close()
