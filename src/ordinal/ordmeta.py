# ordinal/ordmeta.py

from abc import ABCMeta
from functools import wraps
from typing import Callable, Mapping
import inspect

from tb_hide import tb_hide, HideMode

ORD_SIGN = "OrdSign"   


def sig_free_self(func: Callable) -> inspect.Signature:
    sig = inspect.signature(func)
    new_params = list()
    for p in sig.parameters.values():
        if p.name == 'self':
            continue
        new_params.append(p)
    return sig.replace(parameters=new_params)


class OrdMeta(ABCMeta):
    __metas: dict[str, type[OrdMeta]] = dict()
    
    def __new__(mcls, name: str, bases: tuple[type], namespace: Mapping):
        for method in {'__init__', 'formalize'}:
            if not callable(namespace.get(method, None)):
                raise TypeError(f"{name!r} missing method: '{method}'")
        try:
            if mcls is OrdMeta:
                return mcls[name](name, bases, namespace)
            return super(OrdMeta, mcls).__new__(mcls, name, bases, namespace)
        except KeyError:
            pass
        init = namespace['__init__']
        namespace['_OrdMeta__interface'] = sig_free_self(init)
        
        meta = type(
            f"OrdMeta[{name}]",
            (OrdMeta,),
            {
                '__call__': tb_hide(wraps(init)(mcls._OrdMeta__actual_call),
                                    mode=HideMode.RECURSIVE),
                '__class_getitem__': None
            }
        )
        mcls.__metas[name] = meta
        return meta(name, bases, namespace)

    @tb_hide(exceptions=(KeyError,))
    def __class_getitem__(mcls, item: str | type) -> type[OrdMeta]:
        if isinstance(item, type):
            item = item.__name__
        try:
            return mcls.__metas[item]
        except KeyError:
            raise KeyError(f"no metaclass named 'OrdMeta[{item}]'") from None

    # noinspection PyPep8Naming
    def _OrdMeta__actual_call(cls, *args, **kwargs):
        try:
            cls._OrdMeta__interface.bind(*args, **kwargs)
        except TypeError as exc:
            exc.__context__ = None
            ex_args = list(exc.args)
            msg = ex_args[0]
            if msg.startswith('too'):
                msg = 'receiving ' + msg
            ex_args[0] = f"{cls.__init__.__qualname__}() " + msg
            exc.args = tuple(ex_args)
            raise
        try:
            f = cls._pre_check
        except AttributeError:
            pass
        else:
            check = f(*args, **kwargs)
            if check is not None:
                return check
        content = cls.formalize(*args, **kwargs)
        if isinstance(content, tuple) and content[0] == ORD_SIGN:
            args = content[1]
            kwargs = content[2]
        else:
            args = (content,)
            kwargs = dict()
        try:
            f = cls._post_check
        except AttributeError:
            pass
        else:
            check = f(*args, **kwargs)
            if check is not None:
                return check
        return super().__call__(*args, **kwargs)


__all__ = ["OrdMeta", "ORD_SIGN"]
