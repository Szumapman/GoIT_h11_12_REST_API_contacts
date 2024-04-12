### GoIT moduł 2 web
# Zadanie domowe #14
W tym zadaniu domowym kontynuujemy udoskonalanie naszej aplikacji REST API z zadania domowego 13.
### Zadanie
- Uzyj **Sphinx** aby stworzyć dokumentację dla swojego zadania domowego. W tym celu dodaj `docstrings` do niezbędnych funkcji i metod klas w głównych modułach.
- Pokryj moduły repozytorium zadania domowego testami jednostkowymi przy użyciu frameworka `Unittest`. Weź jako podstawę przykład z konspektu modułu `tests/test_unit_repository_notes.py`
- Pokryj dowolną wybraną ścieżkę z zadania domowego testami funkcjonalnymi przy użyciu frameworka `pytest`.

### Zadanie dodatkowe
- Pokryj testami ponad 95% swojego zadania domowego. Do kontroli użyj pakietu [pytest-cov](https://pypi.org/project/pytest-cov/).

  
# Zadanie domowe #13 (Część pierwsza - REST API)
W tym zadaniu domowym kontynuujemy ulepszanie aplikacji opartej na REST API z poprzedniego zadania domowego.
### Zadania
- Zaimplementuj mechanizm weryfikacji adresu e-mail zarejestrowanego użytkownika;
- Ogranicz liczbę żądań do tras kontaktów. Pamiętaj, aby ograniczyć maksymalną liczbę kontaktów tworzonych przez jednego użytkownika w określonym czasie;
- Włącz CORS dla interfejsu API REST;
- Zaimplementuj funkcjonalność umożliwiającą aktualizację awatara użytkownika. Skorzystaj w tym celu z usługi Cloudinary;

### Wymagania ogólne
- Wszystkie zmienne środowiskowe powinny być przechowywane w pliku `.env`. Kod nie powinien zawierać żadnych danych poufnych;
> [!TIP]
> Przed uruchomieniem programu należy utworzyć plik `.env`, zgodnie z dołączonym do projektu wzorcowym plikiem: `env`
- Do uruchamiania usług i baz danych używany jest Docker Compose.

### Dodatkowe zadania
- Zaimplementuj mechanizm buforowania przy użyciu bazy danych Redis. Wykonaj buforowanie bieżącego użytkownika podczas autoryzacji;
- Zaimplementuj mechanizm resetowania hasła dla aplikacji opartej na REST API.


# Zadanie domowe #12 

W tym zadaniu domowym kontynuujemy pracę nad REST-owym API aplikacji z poprzedniego zadania domowego. [Opis wcześniejszego zadania domowego #11](#zadanie-domowe-11)

### Zadania
* implementacja mechanizmu uwierzytelniania;
* implementacja mechanizmu autoryzacji za pomocą tokenów JWT, tak aby wszystkie operacje na kontaktach były wykonywane tylko przez zarejestrowanych użytkowników;
* użytkownik ma dostęp tylko do swoich operacji na kontaktach.

### Wymagania ogólne
* Jeśli podczas rejestracji użytkownik z podanym adresem `email` już istnieje, serwer zwróci błąd `HTTP 409 Conflict`;
* Serwer haszuje hasło i nie przechowuje go w bazie danych w postaci zwykłego tekstu;
* W przypadku udanej rejestracji użytkownika serwer powinien zwrócić status odpowiedzi `HTTP 201 Created` oraz dane nowego użytkownika;
* W przypadku udanych żądań metodą `POST` służących do tworzenia nowych zasobów serwer zwraca status `201 Created`;
* W przypadku żądań metodą `POST` służących do uwierzytelnienia użytkownika serwer akceptuje żądania z danymi użytkownika (`email`, `hasło`) w treści żądania;
* Jeśli użytkownik nie istnieje lub hasło jest niepoprawne, system zwraca błąd `HTTP 401 Unauthorised`;
* Mechanizm autoryzacji jest zaimplementowany przy użyciu pary tokenów JWT: tokena dostępu `access_token` i tokena odświeżania `refresh_token`.


  
# Zadanie domowe #11

Celem tego zadania domowego jest stworzenie interfejsu REST API do przechowywania i zarządzania kontaktami. API powinno być zbudowane przy użyciu infrastruktury FastAPI i używać SQLAlchemy do zarządzania bazą danych.

Kontakty powinny być przechowywane w bazie danych i zawierać następujące informacje:
* Imię
* Nazwisko
* Adres e-mail
* Numer telefonu
* Datę urodzenia
* Dodatkowe dane (opcjonalnie)

Interfejs API powinien być w stanie wykonywać następujące czynności:
* Utworzyć nowy kontakt
* Pobrać listę wszystkich kontaktów
* Pobrać jeden kontakt według ID
* Zaktualizować istniejący kontakt
* Usunąć kontakt

Oprócz podstawowej funkcjonalności, CRUD API powinien mieć również następujące cechy:
* Kontakty powinny być przeszukiwalne według imienia, nazwiska lub adresu e-mail (Query).
* API powinno być w stanie pobrać listę kontaktów z datami urodzin na najbliższe 7 dni.

### Wymagania ogólne
1. Użycie frameworka FastAPI do tworzenia API.
2. Użycie SQLAlchemy ORM do pracy z bazą danych.
3. Jako bazy danych należy użyć PostgreSQL.
4. Obsługa operacji CRUD dla kontaktów.
5. Obsługa przechowywania daty urodzenia kontaktu.
6. Dostarczenie dokumentów dla API.
7. Użycie modułu walidacji danych Pydantic.
