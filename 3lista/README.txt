# Pliki:
-lzw.py - rozwiązanie zadania na ocenę 5
-coding.py - implementacja 4 zadanych kodowań

# Uruchomienie:
Plik lzw.py należy uruchomić poleceniem python3. Program przyjmuje minimum 3 parametry:
    python3 lzw.py --encode [nazwa pliu kodowanego] [nazwa pliku wyjściowego]
lub analogiczne polecenie dekodujące:
    python3 lzw.py --decode [nazwa pliu zakodowanego] [nazwa pliku wyjściowego]

Dodatkowo bezpośrednio za wymaganymi parametrami można podać dwa dodatkowe:
-typ kodowania:
    '--omega' - kodowanie Eliasa omega (domyślne)
    '--delta' - kodowanie Eliasa delta
    '--gamma' - kodowanie Eliasa gamma
    '--fib' - kodowanie Fibonacciego
-rozmiar słownika:
    '--size [rozmiar]' - ustawia rozmiar słownika, minimalny rozmiar to 512, domyślnie wartość ta wynosi 2^16

# Przykładowe wywołanie programu:
python3 lzw.py --encode in.txt out --delta --size 32768
