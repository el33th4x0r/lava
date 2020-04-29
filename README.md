# lava
Lava
----

Lava is a production grammar system.

Given a grammar, it stochastically generates random inputs that satisfy that grammar.

This is generally useful for testing, though production grammars have also been used in computer graphics and gaming to create interesting backdrops, in computational biology to create molecular designs that fit certain physical constraints, and other settings.

How to Use
----------

You specify a grammar in traditional yacc format, amended with weights, and actions. For instance:

```yacc
root: ">=" | ">=" root
stalk: "-" | "-" stalk | stalk flower
flower: "*"
seed: root stalk "\n"
```

is a simple production grammar that will generate sideways flowers, with roots, a stem, and optionally a flower, like this:
```
>=---
>=----**
>=>=>=-**
>=>=>=-
```

These flowers are kind of squat. We can direct the code generation by associating weights with certain productions. For instance, changing the stalk rule to:

```yacc
stalk: "-" | {10} "-" stalk | stalk flower
```

will create flowers with much longer stalks, like this
```
>=>=>=>=--------------------------------------*
>=----------------------------------------*******
>=--
```

Weights are specified in any unit you like, and are interpreted with respect to each other. Default weight is "1".
So the second production above is 10 times more likely than the other two production rules, and will account for
10/12=5/6=83% of the flowers.

You can also associate actions with productions. So the grammar:

```yacc
subject: "I" 
verb: "CAME"
object: "HOME"
stmt: subject " " verb " " object " AT " hour "\n"

program: start stmt stmt stmt

action start {"
global clock
clock = 0
"}

action hour {"
global clock
clock += 1
print('%d' % clock, end='')
"}
```

will generate:
```
I CAME HOME AT 1
I CAME HOME AT 2
I CAME HOME AT 3
```

Enjoy!
- Emin Gun Sirer
- el33th4x0r@gmail.com

