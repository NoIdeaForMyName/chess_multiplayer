Chess multiplayer jest projektem wykonanym w ramach kursu języki skryptowe - laboratoria. Głównym założeniem projektu było utworzenie wieloosobowej gry online w szachy. W skład projektu wchodzą cztery główne skrypty: skrypt klienta gry i klienta lobby oraz serwera gry i serwera lobby. Po uruchomieniu skryptu serwera lobby (może być uruchomiony na dowolnym serwerze, lub komputerze jednego z graczy), gracze mogą połączyć się do odpowiedniego serwera, celem znalezienia lub utworzenia nowej gry. Po udanym połączeniu, gracz ma możliwość rozpoczęcia nowej gry lub dołączenia do już utworzonej (nierozpoczętej) dostępnej na liście. Po rozpoczęciu rozgrywki, oprócz typowej dla szachów planszy, dla graczy dostępne są zegary z czasem. Po zakończeniu rozgrywki, tworzony jest plik z wykonanymi podczas gry ruchami. Aplikacja udostępnia tryb analizy takiego pliku, celem prześledzenia rozgrywki. Menu do gry zostało wykonane z użyciem frameworka QT, natomiast sama gra - w pygame.

Najważniejsze biblioteki użyte do wykonania projektu:
PyQt5
pygame
socket
threading
pickle
json

Twórca: Michał Maksanty
