# Automated Testing TD3: UI-testing a Form application

Dans ce TD, nous allons faire une application de formulaires. Les utilisateurs peuvent:
- Créer des formulaires
- Specifier des champs nécessaires, de type numéro de téléphone, email
- Faire des formulaires privés

Si l'utilisateur se trompe en renseignant un champ ("email"), il y aura un message d'erreur explicatif sous le champ.

Nous allons créer un test frontend pour chacune de ses fonctionnalités.

Nous allons coder l'app en Django, avec du Javascript sur les pages.

## Installation

### Python

Créer un venv
```bash
uv sync
```
(Si vous n'avez pas `uv` installé, regarder les TDs précédents pour l'installer)

### Node (nécessaire pour les tests Javascript)

Ce guide vous explique comment installer Node.js et npm sur votre système, puis comment exécuter les tests du projet.

Via le site officiel:
- Téléchargez l'installateur depuis [nodejs.org](https://nodejs.org/).
- Suivez les instructions d'installation.

Pour Mac, vous pouvez utiliser Homebrew
```bash
brew install node
```

Sur Linux, vous pouvez utiliser le gestionnaire de paquets :
```bash
sudo apt update
sudo apt install nodejs npm
```

**Vérifier que cela fonctionne**.
Dans le dossier automated_testing_tp3/, faites:
```bash
npm install
npm run test
```

### Mise en place du projet Django

Dans le dossier automated_testing_tp3/, faites:
```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py collectstatic
```

Faites tourner les tests:
```bash
uv run pytest
```

## Tâches

### Créer un validateur pour "email"

#### Test du composant

En vous inspirant des tests dans core/tests/front/test_form_detail.py,<br/>
Créer un test `test_email_field__error` où le formulaire contient une question de type "email", et où l'utilisateur a répondu "bob". <br/> 
Un message "Invalid email address" doit être affiché dans la page.

Créer un test `test_email_field__ok` où le formulaire est bien rempli, et il n'y a pas de message d'erreur.

#### Test de la logique

La logique qui valide où non l'email doit être en javascript. <br/>
Inspirez-vous de core/static/core/js/validation.test.js pour créer les tests d'une function `isValidEmail(txt: str): bool`

Lancer `npm run test`, vous devez avoir une erreur (la fonction n'existe pas).

#### Implémentation logique 

Implémenter `isValidEmail` dans cor/static/core/js/validation.js

Lorsque `npm run test` est vert, faîtes `uv run python manage.py collectstatic` pour que le javascript codé soit disponible dans l'app.

#### Implémentation composant

Vous pouvez maintenant changer core/templates/core/form_detail.html et core/static/core/js/validation.js pour que votre test pass.

#### Refacto

##### Logique isError et getErrorMessage

Si le message d'erreur est écrit ~en dur dans form_detail.html, ce sera dur à maintenir.
Vous pouvez coder des fonctions
- `isFieldValid`, qui fait appel à `isValidEmail` si le champ est email, `isFilled` is le champ est mandatory
- `getErrorMessage` qui retourne le message d'erreur à afficher

Créer les tests dans validation.test.js, cela fixe le "contrat" d'utilisation de ces fonctions.

Implémentez ces fonctions, et utilisez-les dans form_detail.html

puis
```bash
uv run python manange.py collectstatic
uv run pytest
```

##### Page "FormDetail"

Dans les tests `test_mandatory_field_...` et `test_email_field_...`, nous faisons des opérations similaires:
- get_input(...)
- write_in_input(...)
- assert_has_error(...) ou assert_no_error(...)

Créer un objet FormPage:
```python
class FormPage:
    def __init__(self, selenium, live_server, form):
        self.selenium = selenium
    	self.selenium.get(f"{live_server.url}/forms/{form.slug}/")

    ...
```

Puis changer vos tests pour qu'ils utilisent FormPage. <br/>
Les tests doivent être très faciles à lire maintenant

### Créer un validateur pour téléphone

Un numéro de téléphone ne peut comporter que des nombres, espaces " " et tiret "-". <br/>
Uniquement en 1ère position, il peut comporter "+" suivi de 2 chiffres

#### Test de composant

Créer les tests `test_field_phone_number_...` en erreur et OK, en utilisant FormPage

#### Test de logique

Créer la logique `isValidPhoneNumber`. <br/>

#### Implémenter

#### Refacto

Si vous avez bien travaillé jusqu'ici, cette feature s'intègre bien au code.

### Formulaires privées

On veut que certains formulaires soient réservées aux personnes avec le bon email.<br/>
Pour les formulaires protégés, on demande à l'utilisateur son email. S'il fait partie des admis, il a accès aux questions.

#### Test Composant

Changer le modèle core/models.py.Form pour qu'il puisse être privé, et admette une liste d'emails white lister

Créer les tests `test_private_form_...` avec le cas OK, où l'utilisateur a mis un email admis, et voit les questions.<br/>
Puis le cas non-OK, où l'utilisateur a mis un email refusé, et voit écrit "access denied".

#### Implémentation

Implémenter la fonctionnalité

#### Refacto

Faut-il mettre à jour le "PageForm" ?

### Créer des formulaires privées

En vous inspirant de core/tests/front/test_create_form.py, créer un test où l'utilisatrice "Alice" veut créer un formulaire privé ou "bob@example.com" est admis.

Changer le code de core/templates/core/create_form.html et core/views.py pour que la feature soit disponible.

### Voir les statistiques d'un formulaire

En vous inspirant de core/tests/front/test_create_form.py, <br/>
Créer le fichier de test core/tests/front/test_form_stat.py <br/>

Créer, en fixture, un formulaire avec 2 réponses. <br/>
Lorsque l'utilisatrice "Alice" va sur la page des statistiques de son formulaire, elle voit le nombre de formulaires remplis (2) et, par questions, toutes les réponses données.

Changer le code "core/urls.py", "core/views.py". Créer un "core/templates/core/form_stat.html pour passer le test.

### Test end-to-end

On veut créer des tests end-to-end pour nos fonctionnalités principales:
- Qu'un.e utilisateur.trice puisse remplir un formulaire, que ses réponses soient enregistrées
- Qu'un.e créateur.trice puisse voir les statistiques
- Qu'un.e utilisateur.trice, avec le bon email, puisse voir un formulaire privé
- Qu'un.e utilisateur.trice, avec le mauvaise email, ait "access denied" sur un formulaire privé

Pour le test end-to-end, on veut:
- Qu'un serveur run (sur "http://localhost:8000/")
- Qu'un browser selenium l'utilise et fasse vraiment les actions.

On ne veut pas que ces tests interfèrent les uns les autres. Qu'un test écrive des données sur la database, qui change le résultat d'un autre test.

Pour chaque test, on aura des "seed_data", avec un utilisateur, un formulaire, peut-êtr des stats pré-remplies.

#### Setup

J'ai créé une fonction, gérant le Django-framework, pour créer des données, dans core/management/commands/init_test_db.py

Si vous faites
```bash
uv run python manage.py init_test_db
```

Vous devriez voir que la fonction tourne, et a initialisé la base de données test.

Pour faire tourner des tests end-to-end, vous pouvez
```bash
uv run python manage.py init_test_db
uv run python manage.py runserver 0.0.0.0:8000
```
pour lancer le serveur, et

```bash
uv run pytest core/tests/test_end_to_end.py
```
pour faire tourner les tests end-to-edn.

#### Seed data

Changer le code de init_test_db.py pour qu'il créé les données pour vos cas de tests. <br/>
REFACTOREZ!<br/>
On ne veut pas que `init_test_db` soit un script de 1000 lignes. Vous aurez une fonction

```python
def add_seed_data():
    add_case_1()
    add_case_2()
    ...
```

#### Test end-to-end
Après avoir fait:
```bash
uv run python manage.py init_test_db
uv run python manage.py runserver 0.0.0.0:8000
```

Avec un serveur qui tourne<br/>
Faites les tests

```python
URL = "http://0.0.0.0:8000"


def test_...(selenium):
    # Given
    selenium.get(f"URL/forms/...the_form_id...")

    # When
    ...operations to do in test
    
    # Then
    ...expected outcom
```