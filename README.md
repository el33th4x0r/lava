# lava
Lava
----

Lava is a production grammar system.

Given a grammar, it stochastically generates random inputs that satisfy that grammar.

This is generally useful for testing, though production grammars have also been used in computer graphics and gaming to create interesting backdrops, in computational biology to create molecular designs that fit certain physical constraints, and other settings.

How to Use
----------

You specify a grammar in traditional yacc format, amended with weights, and actions. For instance:

seed: root stalk
root: "=" | root "="
stalk: "+" | stalk "+" | stalk stem
stem: "Y"

Weights are interpreted 
