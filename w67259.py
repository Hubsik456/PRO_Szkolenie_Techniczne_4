"""
    Przedmiot:
        PRO Szkolenie Techniczne 4

    Temat:
        "6. Wyszukiwanie wartości w zbiorze danych."

    Repozytorium:
        https://github.com/Hubsik456/PRO_Szkolenie_Techniczne_4

    Autor:
        Hubert Michna, w67259, 6 IIZ
        Czerwiec 2025
"""

#! Importy
from tkinter import Tk as TK, Label as LABEL, Frame as FRAME, messagebox as MESSAGEBOX, Menu as MENU, ttk as TTK, scrolledtext as SCROLLED_TEXT, END, BooleanVar as BOOLEAN_VAR, filedialog as FILE_DIALOG, Button as BUTTON, Entry as ENTRY, Checkbutton as CHECK_BUTTON, IntVar as INT_VAR
from functools import partial as PARTIAL
from datetime import datetime as DATETIME
from re import match as MATCH
from time import time as TIME
from sqlite3 import connect as CONNECT
from pandas import read_csv as READ_CSV, DataFrame as DATA_FRAME
from multiprocessing import Process as PROCESS, Queue as QUEUE
from webbrowser import open as OPEN
from rich import print # Niestandardowa biblioteka; Opcjonalne

#! Klasy
class Metaklasa(type):
    """
        Specjalna metaklasa, przeznaczona do tworzenia filtrów.
    """

    def __new__(Klasa, Nazwa: str, Klasy_Bazowe: tuple, Dict: dict):
        """
            Nadpisanie domyślnej metody __new__. Wymuszenie aby właściwości posiadały odpowiedni format, nie dotyczy tych właściwości które będą dodawane podczas korzystania z konstruktora.
        """
        RegEx = r"^([A-Z][a-z0-9]*(_[A-Z][a-z0-9]*)*)?$" # https://regex101.com/r/Fv9ojY/1

        for Klucz, Wartość in Dict.items():
            #print(f"{Klucz=} --> {Wartość=}")

            if not Klucz.startswith("__"): # Żeby nie modyfikować systemowych właściwości
                if not bool(MATCH(RegEx, Klucz)):
                    raise Exception(f"Nazwa właściwości '{Klucz}' powinna być rozdzielana znakiem '_', a poszczególne słowa powinny być kapitalozowane!")

        return super().__new__(Klasa, Nazwa, Klasy_Bazowe, Dict)

class Filtr(metaclass=Metaklasa):
    """
        Klasa służąca do filtrowania danych.
    """

    #? Właściwości
    Licznik = 0 # "Globalne"; Na potrzby TreeView z listą filtrów

    #? Konstruktor
    def __init__(self, Kolumna: str, Treść: str, Rodzaj: str):
        """
            Tworzenie nowego filtru.

            :param Kolumna: W jakiej kolumnie dane mają być filtrowane.
            :param Treść: Dane które mają zostać znalezione.
            :param Rodzaj: Jakiego rodzaju jest to filtr, Tekst, RegEx, Liczba,.
        """

        if Rodzaj not in ["Tekst", "Liczba", "RegEx"]:
            raise ValueError(f"Podano niepoprawny rodzaj dla filtra, podano: '{Rodzaj}'. Dozwolne wartości to 'Tekst', 'Liczba' lub 'RegEx'.")

        Filtr.Licznik += 1

        self.ID = Filtr.Licznik
        self.Kolumna = Kolumna
        self.Treść = Treść
        self.Rodzaj = Rodzaj

    #? To String
    def __str__(self):
        """
            Ustawienie reprezentacji obiektu jako string.
        """

        return f"Filtr: ID: '{self.ID}', Kolumna: '{self.Kolumna}', Treść: '{self.Treść}', Rodzaj: '{self.Rodzaj}'."

#! Dekoratory
def Dekorator_Print_Czas(Funkcja):
    """
        Wyświetla w konsoli kiedy została wykonana dana funkcja.
    """

    def Dekorator(*args, **kwargs):
        print(f"--- Start {DATETIME.now().time()} ---")
        Funkcja(*args, **kwargs)
        print("--- Koniec ---")

    return Dekorator

def Dekorator_Print_Czas_Trwania(Funkcja):
    """
        Wyświetla w konsoli kiedy została wykonana dana funkcja i ile czasu zajeło jej wykonanie.
    """

    def Dekorator(*args, **kwargs):
        Czas_Rozpoczęcia = TIME()

        print(f"--- Start ---\n")
        Funkcja(*args, **kwargs)
        print(f"--- Koniec, Czas Wykonywania: {TIME() - Czas_Rozpoczęcia}s ---")

    return Dekorator

def Dekorator_Log_Czas(Funkcja):
    """
        Dopisuje do logu kiedy została wykonana dana funkcja.
    """

    def Dekorator(*args, **kwargs):
        Scrolled_Text_1.insert(END, f"{DATETIME.now().time()}| ")
        Funkcja(*args, **kwargs)
        Scrolled_Text_1.insert(END, "\n")

    return Dekorator

def Dekorator_Log_Czas_Trwania(Funkcja):
    """
        Dopisuje do logu kiedy została wykonana dana funkcja i ile czasu zajeło jej wykonanie.
    """

    def Dekorator(*args, **kwargs):
        Czas_Rozpoczęcia = TIME()

        Scrolled_Text_1.insert(END, f"--- Start ---\n")
        Funkcja(*args, **kwargs)
        Scrolled_Text_1.insert(END, f"--- Koniec, Czas wykonywania: {TIME() - Czas_Rozpoczęcia} ---\n")

    return Dekorator

#! Funkcje
#? Pomocniczne/WIP
@Dekorator_Print_Czas
def WIP_Komunikat_1(Tekst: str):
    """
        Funkcja pomocnicza, wyświetla w konsoli komunikat o treści podanej przez parametr.
    """

    print(f"WIP| {Tekst}")

@Dekorator_Print_Czas
def WIP_Komunikat_2():
    """
        Funkcja pomocnicza, wyświetla w konsoli komunikat o statycznej treści.
    """

    print("WIP| Testowy komunikat")

def Czy_Float(Tekst: str):
    """
        Sprawdza czy dany tekst może zostać zamieniony na typ float.
        TODO: Do usunięcia, nie sprawdza poprawnie np. notacji naukowej.
    """

    try:
        float(Tekst)
        print(Tekst)
        return True

    except ValueError:
        return False

#? Ustawienia
def Okno_Na_Wierzchu(Event = None):
    """
        Włącza lub wyłącza to czy aplikacja ma się znajdować na wierzchu, nad innymi normalnymi aplikacjami.
    """

    Okno_Główne.attributes("-topmost", bool(Ustawienia["Czy Okno Na Wierzchu"].get()))
    Okno_Główne.update()

#? Ogólne
def O_Programie():
    """
        Funkcja pomocnicza, wyświetla nowe okienko komunikatu z podstawowymi informacjami o tym programie.
    """

    MESSAGEBOX.showinfo("O Programie", "Ten program powstał w ramach projektu z przedmiotu LAB 'Szkolenie Techniczne 4'.\n\nAutor: Hubert Michna, w67259, 6 IIZ\nCzerwiec 2025")

def Pomoc():
    """
        Funkcja pomocnicza, wyświetla nowe okienko komunikatu z informacjami jak działa i jak używać tego programu.
    """

    MESSAGEBOX.showinfo("WIP", "Pomoc")

#? Log
@Dekorator_Log_Czas
def Log_Dopisanie_Tekstu(Tekst = "Lorem Ipsum"):
    """
        Dopisanie tekstu do logu.
    """

    Scrolled_Text_1.insert(END, f"{Tekst}")

@Dekorator_Print_Czas_Trwania
def Log_Kasowanie_Tekstu():
    """
        Skasowanie całej treści logu i dopisanie stosownego komunikatu.
    """

    Scrolled_Text_1.delete("1.0", END)
    Log_Dopisanie_Tekstu("Wyczyszczono Log.")

#? Wybór Pliku
@Dekorator_Log_Czas_Trwania
def Dane_Wybierz_Plik():
    """
        Otwarcie okienka pozwalajacego na wybór pliku z danymi i wyświetlenie ich w TreeView.
    """

    #! Zmienne globalne
    global Dane

    #! Formaty Plików
    Dozwolone_Formaty_Plików = (
        ("Plik CSV", "*.csv"),
        ("Baza Danych SQLite", "*.db"),
    )

    #! Wybranie Pliku
    Wybrany_Plik = FILE_DIALOG.askopenfilename(title="Wybierz Plik", initialdir="/", filetypes=Dozwolone_Formaty_Plików)

    #! Wyjście z funkcji jeśli nie wybrano żadnego pliku
    if Wybrany_Plik == "":
        MESSAGEBOX.showwarning(title="Wybierz Plik", message="Nie wybrano żadnego pliku.")
        return

    Label_5.config(text=f"Wybrano plik: '{Wybrany_Plik}'")
    Log_Dopisanie_Tekstu(f"Wybrano plik: '{Wybrany_Plik}'.")

    #! Jeśli wybrany plik to .db
    if Wybrany_Plik.endswith(".db"):
        Label_6.pack()

        with CONNECT(Wybrany_Plik) as Połączenie:
            Kursor = Połączenie.cursor()

            DB_Wyniki = Kursor.execute("SELECT * FROM Tabela_1")
            DB_Kolumny = [DB_Kolumna[0] for DB_Kolumna in DB_Wyniki.description]

            WIP_Dane = DATA_FRAME.from_records(data=DB_Wyniki.fetchall(), columns=DB_Kolumny) # Ponieważ samo zapytanie nie zwraca nazw kolumn potrzebnych do DataFrame i Treeview

    #! Jeśli wybrany plik to .csv
    elif Wybrany_Plik.endswith(".csv"):
        Label_6.pack_forget()

        WIP_Dane = READ_CSV(Wybrany_Plik)

    #! Usunięcie obecnej zawartości TreeView
    for Wiersz in Tree_View_1.get_children():
        Tree_View_1.delete(Wiersz)

    #! Tworzenie kolumn w TreeView
        #? Wyciągnienięcie nazw kolumn z DataFrame
    Kolumny = list(WIP_Dane.columns)

        #? Select z nazwami kolumn do filtrów
    Select_1.config(values=Kolumny)
    Select_1.set("")

    Tree_View_1["columns"] = Kolumny

    #! Dodanie kolumn do TreeView
    for Kolumna in Kolumny:
        #print(Kolumna)

        Tree_View_1.heading(Kolumna, text=Kolumna)
        Tree_View_1.column(Kolumna)

    #! Wstawianie danych do TreeView
    for Index, Wiersz in WIP_Dane.iterrows():
        Tree_View_1.insert("", END, values=list(Wiersz))

    print(WIP_Dane)
    Dane = WIP_Dane # Zapisanie DataFrame do zmiennej globalnej

    Log_Dopisanie_Tekstu("Dane zostały wyświetone w tabelce.")

@Dekorator_Log_Czas_Trwania
def Dane_WIP_Wyświetl():
    """
        Funkcja pomocniczna, wyświetla w konsoli dane wejściowe, z pliku wybranego przez użytkownika.
        Ponieważ dane to pandas.DataFrame, całość może nie zostać wyświetlona.
    """

    print(Dane)

#? Filtry
@Dekorator_Log_Czas_Trwania
def Filtr_Wyświetl():
    """
        Funkcja pomocnicza, wyświetla w konsoli wszystkie obecne filtry, które zostały utworzone przez użytkownika
    """

    print("--- Filtry: ---")

    for Filtr in Filtry:
        print(Filtr)

    print("--- Filtry - Koniec ---")

@Dekorator_Log_Czas_Trwania
def Filtr_Dodanie():
    """
        Funkcja dodająca nowy filtr, sprawdza dane podane przez użytkownika
    """

    #! RegEx'y
    RegEx_Walidacja_Zakres = r"^\d+(\.\d+)?-\d+(\.\d+)?$" # Regex: https://regex101.com/r/1Ci5AP/1
    RegEx_Walidacja_Liczba = r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$" # https://docs.vultr.com/python/examples/check-if-a-string-is-a-number-float#using-regular-expressions-for-pattern-checking

    #! Wcztanie danych
    Kolumna = Select_1.get()
    Treść = Entry_1.get()
    Rodzaj = Select_2.get()

    #! Sprawdzenie danych i komunikaty o błędach
    Komunikat = ""

    if Kolumna == "":
        Komunikat += "Nie wybrano kolumny w której dane maja być wyszukiwane. Jeśli nie możesz wybrać żadnej wartości, musisz najpierw podać plik, który ma być sprawdzany.\n\n"

    if Rodzaj == "":
        Komunikat += "Nie wybrano rodzaju danych jaki ma być filtrowany.\n\n"

    if Rodzaj == "Liczba" and (not bool(MATCH(RegEx_Walidacja_Liczba, Treść))):
        Komunikat += "Wybrano że treść ma być liczbą, ale nie jest.\n\n"

    if Rodzaj == "Zakres" and (not bool(MATCH(RegEx_Walidacja_Zakres, Treść))):
        Komunikat += "Podany regex nie jest poprawny. Należy podać dwie liczby, int lub float'y rozdzielone znakiem pauzy."

        #? Wyświetlenie komunikatu
    if Komunikat != "":
        MESSAGEBOX.showerror("Błąd", f"Podano niepoprawne dane!\n\n{Komunikat}")
        return

    #! Dodanie filtra
    Filtry.append(Filtr(Kolumna, Treść, Rodzaj))
    Tree_View_2.insert("", END, values=(Filtry[-1].ID, Filtry[-1].Treść, Filtry[-1].Rodzaj, Filtry[-1].Kolumna))

    Log_Dopisanie_Tekstu(f"Dodano nowy filtr:\n\tKolumna: '{Kolumna}'\n\tTreść: '{Treść}'\n\tRodzaj: {Rodzaj}")

@Dekorator_Log_Czas_Trwania
def Filtr_Usunięcie():
    """
        Usuwa filtr który został zaznaczony w TreeView.
    """

    #! Wybranie obecnie zaznaczonego wiersza w TreeView
    Zaznaczony_Wiersz = Tree_View_2.focus()

    if Zaznaczony_Wiersz == "":
        MESSAGEBOX.showwarning("Uwaga", "Żaden wiersz nie jest zaznaczony.")
        Log_Dopisanie_Tekstu("Żaden filtr nie został zaznaczony.")
        return

    ID_Filtra = Tree_View_2.item(Zaznaczony_Wiersz, "values")[0]
    Tree_View_2.delete(Zaznaczony_Wiersz)

    #! Przejście przez wszystkie filtry i usunięcie zaznaczonego
    for x in range(len(Filtry)):

        if Filtry[x].ID == (int(ID_Filtra)):
            #print(x, Filtry[x].ID, (int(ID_Filtra), Filtry[x]), "<-- Do usunięcia")
            Filtry.pop(x)
            break

        else: # Ten else nie jest usunięty po to żeby nie trzeba było printa usuwać
            #print(x, Filtry[x].ID, (int(ID_Filtra)), Filtry[x])
            pass

    Log_Dopisanie_Tekstu("Usunięto zaznaczony filtr.")

@Dekorator_Log_Czas_Trwania
def Filtr_Usunięcie_Wszystkie():
    """
        Usuwa wszystkie filtry i usuwa wzsystkie pozycje z TreeView.
    """

    #! Usunięcie elementów listy
    Filtry.clear()

    #! Usunięcie wszystkich wierszy
    for Wiersz in Tree_View_2.get_children():
        Tree_View_2.delete(Wiersz)

    Log_Dopisanie_Tekstu("Usunięto wszystkie filtry.")

#? Przefiltrowanie Dane
@Dekorator_Log_Czas_Trwania
def Dane_Filtrowanie():
    """
        Funkcja odpowiadająca za przefiltrowanie danych z pliku według filtrów podanych przez użytkownika i wyświetlenie tych danych w TreeView.

        Ta funkcja wykorzystuje multiprocessing.Process a nie multiprocessing.Pool ponieważ to drugie przyjmuje funkcję i iterable które będą służyły jako paramtetry do tej funkcji, obecna struktura danych nie pozwala na bezproblemowe użycie Puli.
    """

    #! Zmienne
    global Dane_Przefiltrowane
    Procesy = []
    Kolejka = QUEUE()

    #! Tworzenie procesów dla każdego z filtrów
    for x in range(len(Filtry)):
        #print(f"{x} --> {Filtry[x]}")

        Proces = PROCESS(target=Dane_Filtrowanie_Proces, args=(Filtry[x], Dane, Kolejka))

        Procesy.append(Proces)
        Proces.start()

    #! Czekanie na wyniki działania procesów
    for Proces in Procesy:
        Proces.join()

    #! Wynik działania filtrów
    while not Kolejka.empty():
        Element_Kolejki = Kolejka.get()

        Dane_Przefiltrowane = Dane_Przefiltrowane._append(Element_Kolejki) # Dodanie pandas.Series do pandas.DataFrame z wynikami filtrowania

    #! Wyświetlenie wyników
    print("--- Dane Przefiltrowane ---")
    print(Dane_Przefiltrowane)
    print("---")

    #! Wyświetlenie wyników w TreeView
    for Wiersz in Tree_View_3.get_children():
        Tree_View_3.delete(Wiersz)

    #! Tworzenie kolumn w TreeView
    Kolumny = list(Dane_Przefiltrowane.columns)
    Tree_View_3["columns"] = Kolumny

    for Kolumna in Kolumny:
        #print(Kolumna)

        Tree_View_3.heading(Kolumna, text=Kolumna)
        Tree_View_3.column(Kolumna)

    #! Wstawienie danych do TreeView
    Dane_Przefiltrowane.drop_duplicates()

    for Index, Wiersz in Dane_Przefiltrowane.iterrows():
        Tree_View_3.insert("", END, values=list(Wiersz))

    Dane_Przefiltrowane = DATA_FRAME() # Wyczyszczenie DataFrame z wynikami na potrzeby kolejnych wywołań tej funkcji

    Log_Dopisanie_Tekstu("Dane zostały przefiltrowane.")

def Dane_Filtrowanie_Proces(_Filtr: Filtr, _Dane: DATA_FRAME, _Kolejka: QUEUE):
    """
        Funkcja odpowiadająca za faktyczne filtrowanie danych. Ta funkcja jest wykonywana przez procesy.

        :param _Filtr: Obiekt typu "Filtr" który będzie realizowany.
        :param _Dane: Obiekt typu pandas.DataFrame z wszystkimi danymi które będą przetwarzane.
        :param _Kolejka: Obiekt typu multiprocessing.Queue który robi za "zmienną globalną"
    """

    #! Przejście po wszystkich wierszach z danych
    for Index, Wiersz in _Dane.iterrows():

        #? Tekst
        if _Filtr.Rodzaj == "Tekst":
            if str(Wiersz[_Filtr.Kolumna]) == _Filtr.Treść:
                _Kolejka.put(Wiersz)

        #? RegEx
        if _Filtr.Rodzaj == "RegEx":
            if bool(MATCH(_Filtr.Treść, Wiersz[_Filtr.Kolumna])):
                _Kolejka.put(Wiersz)

        #? Liczba
        if _Filtr.Rodzaj == "Liczba":
            Regex_Float = r'^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$' # https://docs.vultr.com/python/examples/check-if-a-string-is-a-number-float#using-regular-expressions-for-pattern-checking

            if bool(MATCH(Regex_Float, str(Wiersz[_Filtr.Kolumna]))):
                if float(Wiersz[_Filtr.Kolumna]) == float(_Filtr.Treść):
                    _Kolejka.put(Wiersz)

#! "Main"
if __name__ == "__main__":

    #! Start
    Okno_Główne = TK()
    Okno_Główne.title("w67259| Wyszukiwanie wartości w zbiorze danych")
    Okno_Główne.geometry("800x600+100+100")
    Okno_Główne.minsize(200, 200)

    Filtry = []
    Dane = DATA_FRAME()
    Dane_Przefiltrowane = DATA_FRAME()

    #! Ustawienia
    Ustawienia = {
        "Czy Okno Na Wierzchu": BOOLEAN_VAR() # TODO
    }

    #! Menu
    Menu_Główne = MENU(Okno_Główne)
    Okno_Główne.config(menu=Menu_Główne)

        #? Plik
    Menu_Plik = MENU(Menu_Główne, tearoff=False)
    Menu_Plik.add_command(label="Pomoc", command=Pomoc)
    Menu_Plik.add_command(label="O Programie", command=O_Programie)
    Menu_Plik.add_separator()
    Menu_Plik.add_command(label="WIP| Log", foreground="gray", command=PARTIAL(Log_Dopisanie_Tekstu, "Lorem Ipsum #1"))
    Menu_Plik.add_command(label="WIP| Print #1", foreground="gray", command=PARTIAL(WIP_Komunikat_1, "Lorem Ipsum"))
    Menu_Plik.add_command(label="WIP| Print #2", foreground="gray", command=WIP_Komunikat_2)
    Menu_Plik.add_command(label="WIP| Wyświetl Filtry", foreground="gray", command=Filtr_Wyświetl)
    Menu_Plik.add_command(label="WIP| Wyświetl Dane", foreground="gray", command=Dane_WIP_Wyświetl)
    Menu_Plik.add_separator()
    Menu_Plik.add_command(label="Zamknij Program", foreground="red", command=Okno_Główne.destroy)
    Menu_Główne.add_cascade(label="Plik", menu=Menu_Plik, underline=0)

        #? Log
    Menu_Log = MENU(Menu_Główne, tearoff=False)
    Menu_Log.add_command(label="Dopisz", foreground="gray", command=PARTIAL(Log_Dopisanie_Tekstu, "Lorem Ipsum #2"))
    Menu_Log.add_command(label="Wyczyść Log", command=Log_Kasowanie_Tekstu)
    Menu_Główne.add_cascade(label="Log", menu=Menu_Log)

        #? Ustawienia
    Menu_Ustawienia = MENU(Menu_Główne, tearoff=False)
    Menu_Ustawienia.add_checkbutton(label="Czy Okno Na Wierzchu?", command=Okno_Na_Wierzchu, onvalue=1, offvalue=0, variable=Ustawienia["Czy Okno Na Wierzchu"])
    Menu_Główne.add_cascade(label="Ustawienia", menu=Menu_Ustawienia)

        #? Linki
    Menu_Linki = MENU(Menu_Główne, tearoff=False)
    Menu_Linki.add_cascade(label="GitHub", command=PARTIAL(OPEN, "https://github.com/Hubsik456/PRO_Szkolenie_Techniczne_4"))
    Menu_Linki.add_cascade(label="RegEx 101", command=PARTIAL(OPEN, "https://regex101.com/"))
    Menu_Główne.add_cascade(label="Linki", menu=Menu_Linki)

    #! UI
        #? Frame
    Frame_Góra = FRAME(Okno_Główne)
    Frame_Dół = FRAME(Okno_Główne)

        #? Notebook / Zakładki
    Zakładki_1 = TTK.Notebook(Frame_Góra, height=1) # Ustawienie nawet 1px wysokości sprawi że nie będzie przycinać reszty UI i że całość będzie responsywna
    Zakładki_1.configure(takefocus=True)
    Zakładka_1 = FRAME(Zakładki_1) # Dane
    Zakładka_2 = FRAME(Zakładki_1) # Filtry
    Zakładka_3 = FRAME(Zakładki_1) # Wyniki
    Zakładka_4 = FRAME(Zakładki_1) # Log
    Zakładki_1.add(Zakładka_1, text="Dane")
    Zakładki_1.add(Zakładka_2, text="Filtry")
    Zakładki_1.add(Zakładka_3, text="Wyniki")
    Zakładki_1.add(Zakładka_4, text="Log")

        #? Label
    Label_1 = LABEL(Zakładka_1, text="Wybierz Dane:", font=("Calibri 12 bold"))
    Label_2 = LABEL(Frame_Dół, text="Hubert Michna, w67259, 6 IIZ", fg="gray")
    Label_3 = LABEL(Zakładka_2, text="Dodaj Nowy Filtr:", font=("Calibri 12 bold"))
    Label_4 = LABEL(Zakładka_3, text="Wyszukane Dane:", font=("Calibri 12 bold"))
    Label_5 = LABEL(Zakładka_1, text="Wybrany Plik: ...")
    Label_6 = LABEL(Zakładka_1, text="W przypadku baz danych SQLite, sprawdzana będzie tylko tabela/widok o nazwie 'DANE'.")
    Label_7 = LABEL(Zakładka_2, text="Treść:")
    Label_8 = LABEL(Zakładka_2, text="Kolumna:")
    Label_9 = LABEL(Zakładka_2, text="Rodzaj Danych:")
    Label_10 = LABEL(Zakładka_2, text="Obecne Filtry:", font=("Calibri 12 bold"))
    Label_11 = LABEL(Zakładka_3, text="Poniżej znajdują się wszystkie wiersz, bez duplikatów, które spełniają przynajmniej jeden warunek z filtrów.")

        #? Entry / Input
    Entry_1 = ENTRY(Zakładka_2) # Treść filtru

        #? Button / Przycisk
    Przycisk_1 = BUTTON(Zakładka_1, text="Wybierz Plik", command=Dane_Wybierz_Plik)
    Przycisk_2 = BUTTON(Zakładka_2, text="Dodaj Filtr", command=Filtr_Dodanie)
    Przycisk_3 = BUTTON(Zakładka_2, text="Usuń Zaznaczony Filtr", command=Filtr_Usunięcie)
    Przycisk_4 = BUTTON(Zakładka_2, text="Usuń Wszystkie Filtr", command=Filtr_Usunięcie_Wszystkie)
    Przycisk_5 = BUTTON(Zakładka_3, text="Przeszukaj Dane", command=Dane_Filtrowanie)

        #? ComboBox / Select
    Select_1 = TTK.Combobox(Zakładka_2)
    Select_2 = TTK.Combobox(Zakładka_2, values=("Tekst", "RegEx", "Liczba"))

        #? ScrolledText
    Scrolled_Text_1 = SCROLLED_TEXT.ScrolledText(Zakładka_4, undo=True)

        #? Tree View
            #* Dane
    Tree_View_1_Kolumny = ("Wybierz Plik", )
    Tree_View_1 = TTK.Treeview(Zakładka_1, selectmode="browse", show="headings", columns=Tree_View_1_Kolumny) # Dane wejściowe
    Tree_View_1.heading("Wybierz Plik", text="...")

            #* Filtry
    Tree_View_2_Kolumny = ("ID", "Treść", "Rodzaj", "Kolumna", "Czy Negacja")
    Tree_View_2 = TTK.Treeview(Zakładka_2, selectmode="browse", show="headings", columns=Tree_View_2_Kolumny) # Filtry
    Tree_View_2.heading("ID", text="ID:")
    Tree_View_2.heading("Treść", text="Treść:")
    Tree_View_2.heading("Rodzaj", text="Rodzaj:")
    Tree_View_2.heading("Kolumna", text="Kolumna:")

            #* Przefiltrowane Dane
    Tree_View_3_Kolumny = ("Wybierz Plik i Filtry", )
    Tree_View_3 = TTK.Treeview(Zakładka_3, selectmode="browse", show="headings", columns=Tree_View_3_Kolumny) # Dane wejściowe
    Tree_View_3.heading("Wybierz Plik i Filtry", text="...")

    #! Umieszczanie Elementów - Pack
        #? Frame'y
    Frame_Góra.pack(fill="both", expand=True)
    Frame_Dół.pack(fill="both")

        #? Zakładki
    Zakładki_1.pack(fill="both", expand=True)

            #* Zakładka #1 - Dane
    Label_1.pack()
    Przycisk_1.pack()
    Label_5.pack()
    Tree_View_1.pack()

            #* Zakładka #2 - Filtry
    Label_3.pack()
    Label_8.pack()
    Select_1.pack()
    Label_7.pack()
    Entry_1.pack()
    Label_9.pack()
    Select_2.pack()

    Przycisk_2.pack()

    Label_10.pack()
    Tree_View_2.pack()
    Przycisk_4.pack()
    Przycisk_3.pack()

            #* Zakładka #3 - Wyniki
    Label_4.pack()
    Przycisk_5.pack()
    Label_11.pack()
    Tree_View_3.pack()

            #* Zakładka #4 - Log
    Scrolled_Text_1.pack(fill="both", expand=True)

        #? Stopka
    Label_2.pack(side="right")

    #! Koniec
    Log_Dopisanie_Tekstu("Uruchomienie programu.")
    Okno_Główne.mainloop()
