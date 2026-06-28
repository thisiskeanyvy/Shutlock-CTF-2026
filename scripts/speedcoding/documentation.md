# Démarrage rapide avec Fortran90 "Lite"

> [!info]
>
> - Il s'agit d'une version simplifiée de Fortran90 adaptée aux besoins du challenge. Si vous souhaitez comprendre pleinement le langage Fortran, consultez ce [lien](https://www.math.u-bordeaux.fr/~lmieusse/PAGE_WEB/ENSEIGNEMENT/cours_f90.pdf)
> - Dans tout ce document, l'utilisation de `<...>` signifie que vous devez remplacer par la valeur appropriée.

## INTERDIT

- Pas de modules comme `os` / `sys` / `subprocess` / ...
- Pas d'instructions `print` dans le code

## Général

- Vous n'avez pas à gérer les erreurs.
- Pas d'entrée / sortie. Pour le cas particulier du print, voir [Retour](#retour)
- Pas de pointeurs, tableaux ni allocation dynamique
- Les commentaires ne sont pas dans le périmètre de ce challenge.

### Variables

#### Types

Dans ce challenge, nous ne considérerons que le type entier.

#### Déclaration

Nous considérons que toutes les variables sont déclarées explicitement. L'utilisation du mot-clé `implicit none` n'est pas obligatoire.

```fortran
integer :: mon_entier, mon_autre_entier
```

### Structures de contrôle

Les structures suivantes doivent être implémentées dans votre interpréteur.

- `if/else` (et imbriqués)
- `do`

### Sous-programme

Vous devez implémenter uniquement le type fonction.

### Retour

En Fortran, il n'y a pas de notion claire de retour pour les programmes et fonctions.

Dans ce challenge, nous considérerons que `print` joue le rôle d'instruction de retour.
Tous nos programmes se terminant par un `print` doivent retourner la chaîne de caractères dans notre code Python.

Le séparateur `,` (virgule) doit être traité comme un opérateur de concaténation de chaînes. Aucun espace ne doit être ajouté entre les chaînes concaténées.

À la fin d'une ligne, vous devez ajouter un caractère de saut de ligne `\n` à la chaîne retournée.

```fortran
program main
    print *, "Hello", " world!"
end program main
```

Et le résultat est :

```console
$ python3 speedcoding.py | cat -e
Hello world!$
```

## Suite de tests

Quelques tests pour vérifier que votre programme fonctionne correctement. Assurez-vous que tous les tests passent — le flag est une combinaison des résultats des tests. Lors de la validation, ces tests seront exécutés mais avec des valeurs différentes.

### Test 1 : Simple

```fortran
program test1
    integer :: x
    x = 42
    print *, x
end program test1
```

Sortie attendue : `42`

### Test 2 : Variables

```fortran
program test2
    implicit none
    integer :: a, b, result
    a = 10
    b = 20
    result = a + b
    print *, result
end program test2
```

Sortie attendue : `30`

### Test 3 : Boucle Do

```fortran
program sum_numbers
    integer :: i, sum
    sum = 0
    do i = 1, 5
        sum = sum + i
    end do
    print *, sum
end program sum_numbers
```

Sortie attendue : `15`

### Test 4 : If/Else

```fortran
program conditions
    integer :: x, result
    x = 7
    if (x > 10) then
        result = 100
    else
        if (x > 5) then
            result = 50
        else
            result = 10
        end if
    end if
    print *, result
end program conditions
```

Sortie attendue : `50`

### Test 5 : Fonction simple

```fortran
program function_simple
    integer :: a, b, res
    a = 3
    b = 4
    res = multiply(a, b)
    print *, res

contains
    function multiply(x, y) result(prod)
        integer :: x, y, prod
        prod = x * y
    end function multiply
end program function_simple
```

Sortie attendue : `12`

### Test 6 : Conditions imbriquées

```fortran
program nested_conditions
    integer :: score, bonus
    score = 85
    bonus = 0
    if (score >= 90) then
        if (score >= 95) then
            bonus = 20
        else
            bonus = 10
        end if
    else
        if (score >= 70) then
            bonus = 5
        else
            bonus = 0
        end if
    end if
    print *, bonus
end program nested_conditions
```

Sortie attendue : `5`

### Test 7 : Boucle avec condition

```fortran
program loop_condition
    integer :: i, count
    count = 0
    do i = 1, 7
        count = count + 1
    end do
    print *, count
end program loop_condition
```

Sortie attendue : `7`

### Test 8 : Fonction avancée

```fortran
program function_advanced
    integer :: result
    result = sum(calculate(10, 3, 2), 5)
    print *, result

contains
    function calculate(a, b, c) result(val)
        integer :: a, b, c, val
        val = a * b + c
    end function calculate
    function sum(x, y) result(s)
        integer :: x, y, s
        s = x + y
    end function sum
end program function_advanced
```

Sortie attendue : `37`xpected output: `37`
