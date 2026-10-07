# history

The history of `ordinal` project development will be documented in this file.

NOT `CHANGELOG.md`.

## v1.0.0

Rename `Ordinal._powerCoefs` as `Ordinal.power_coefs`, `Ordinal._powers` as `Ordinal.powers`.

Change the type of `Ordinal.power_coefs` to `frozendict` in `Python 3.15`.

Implement `Ordinal.__setattr__` and `Ordinal.__delattr__`
to protect attributes from being changed or deleted.

Replace all evil functions by using module `tb_hide`.

Finally upload to GitHub.

## v1.0.0-alpha.3

Move the `OrdMeta` to `ordinal.ordmeta`.

Implement an evil function to hide traceback in metaclass.

Implement `OrdMeta.__new__` evilly to make sure
the signature information of `Ordinal.__init__` won't be covered by `OrdMeta.__call__`.

Change the signatures of `Ordinal.__init__`, `Ordinal.formalize`
and so on a number of methods to positional-only.

## v1.0.0-alpha.2

Introduce new keyword-only argument `ignore` for `Ordinal.register`
to skip some checks and redirections.

## v1.0.0-alpha.1

Restructure `Ordinal`:

- Introduce `OrdMeta` to formalize argument before passed to `cls.__init__`
- Move zero-coefficient-remove logic from `Ordinal.__init__` into `Ordinal.formalize`
- Delete `Ordinal.__new__` and move its logic to `OrdMeta.__call__`
- Replace `ord_dict` with `ord_map`

## v0.7.2

Now `register` will issue `RuntimeWarning`
if some unnecessary methods are covered by attributes.

## v0.7.1

Fixed a hidden bug in `register`.

## v0.7.0

Implement `__class_getitem__` and `collect` for `Ordinal`
so that the virtual subclasses can store their important ordinals uniformly.

## v0.6.0

Implement right subtraction method `right_sub` for `Ordinal`.

## v0.5.1

Optimize the implementation of `FGH` and `MGH`.

## v0.5.0

Implement `FGH`, `MGH`, `HH`, `SGH` in `ordinal.growing`.

## v0.4.1

Fix a bug of `... in Ordinal(...)`.

## v0.4.0

Move `_sub_out_of_domain` from `ordinal.Ordinal` to `ordinal`.

## v0.3.0

Implement `divmod()`, division operator(`//`) and modulo operator(`%`) for `Ordinal`.

Implement `pow()` 3-argument form for `Ordinal`.

## v0.2.0

Implement (left) subtraction operator(`-`) for `Ordinal`.

## v0.1.0

Implement basic `Ordinal` class.
