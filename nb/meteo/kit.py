## @file
## модуль вычислений на объектных графах
#  метод EDS: Executable Data Structures
#  https://github.com/ponyatov/jupy/tree/public/nb/meteo

import os, sys
from graphviz import Digraph

## @defgroup core представление объектного графа

## базовый класс узлов объектного графа
## @ingroup core
class Object:

    ## @name Конструкторы

    ## @param[in] V создание объекта с указанным именем или значением (число, строка)
    ## @param[in] sid идентификатор существующего объекта в хранилище или None для создания нового id
    def __init__(self, V, sid=None):

        ## метка типа/класса
        self.type = self.__class__.__name__.lower()

        ## скалярное значение узла (имя, строка, число)
        self.val = V

        ## атрибуты = environment = ассоциативный массив
        self.slot = {}

        ## упорядоченный набор вложенных элементов (ссылок) = вектор = стек
        self.nest = []

        ## уникальный идентификатор объекта (глобальный или в пределах хранилища)
        if not sid:
            self.sid = id(self)
        else:
            self.sid = sid

    ## @name Текстовый дамп

    ## служебный метод вызывается из `print()`

    def __repr__(self):
        return self.dump()

    ## вывод дампа в виде текстового дерева
    ## @param[in] depth глубина рекурсии
    ## @param[in] prefix префикс перед `<T:V>` заголовком
    def dump(self, depth=0, prefix=''):

        # заголовок
        tree = self.pad(depth) + self.head(prefix)

        # останов бесконечной рекурсии на циклических ссылках
        if not depth:
            Object._dumped = []
        if self in Object._dumped:
            return tree + ' _/'
        else:
            Object._dumped.append(self)

        # slot{}ы
        for i in self.slot:
            tree += self.slot[i].dump(depth + 1, prefix='%s = ' % i)

        # nest[]ы
        idx = 0
        for j in self.nest:
            tree += j.dump(depth + 1, prefix='%s = ' % idx)

        # дамп подграфа
        return tree

    ## короткий дамп: только `<T:V>` заголовок
    def head(self, prefix=''):
        return '%s<%s:%s> @%x' % (prefix, self.type, self._val(), id(self))

    ## отбивка пробелами в зависимости от уровня вложенности
    def pad(self, depth):
        return '\n' + '\t' * depth

    ## метод форматирует поле .val специально для дампа
    def _val(self):
        return '%s' % self.val

    ## @name Графическое представление / graphviz /

    ## визуализация графа через библиотеку graphviz
    ## @param[in] plot Digraph объект или None для инициализации
    ## @param[in] parent родительский узел графа
    ## @param[in] label метка на ребре
    ## @param[in] color цвет ребра (отличать slot/nest/...)
    def plot(self, plot=None, parent=None, label='', color='black'):

        # инициализация или ветвь рекурсии
        if not plot:
            plot = Digraph(comment=self.head())
            plot.graph_attr.update(size="9,9")
            Object.plotted = []

        # остановка рекурсии на циклических графах
        if self in Object.plotted:
            return plot
        else:
            Object.plotted.append(self)

        # вывод узла графа
        plot.node('%s' % self.sid, '%s:%s' % (self.type, self._val()))

        # вывод ребра графа с меткой
        if parent:
            plot.edge('%s' % parent.sid, '%s' %
                      self.sid, label=label, color=color)

        # рекурсия по slot{}
        for i in self.slot:
            plot = self.slot[i].plot(
                plot, parent=self, label='%s' % i, color='blue')

        # рекурсия по nest[]
        idx = 0
        for j in self.nest:
            plot = j.plot(plot, parent=self, label='/%s' % idx, color='red')
            idx += 1

        # возврат подграфа из рекурсии
        return plot

    ## @name Операторы для построения структуры графа

    ## `A[key]` получить подграф из слота по имени
    def __getitem__(self, key):
        return self.slot[key]

    ## `A[key] = B` присвоить подграф слотупо имени
    def __setitem__(self, key, that):
        self.slot[key] = that
        return self

    ## `A << B -> A[B.type] = B` присвоить слот по имени типа B
    def __lshift__(self, that):
        return self.__setitem__(that.type, that)

    ## `A >> B -> A[B.val] = B` присвоить слот по значению B
    def __rshift__(self, that):
        return self.__setitem__(that.val, that)

    ## `A // B -> A.push(B)` втолкнуть B как в стек
    def __floordiv__(self, that):
        self.nest.append(that)
        return self

    ## @name Стековые операции

    ## ( 1 2 3 -- 1 2 4 ) -> 3
    def top(self):
        return self.nest[-1]

    ## ( 1 2 3 -- 1 2 3 ) -> 2
    def tip(self):
        return self.nest[-2]

    ## ( 1 2 3 -- 1 2 ) -> 3
    def pop(self):
        return self.nest.pop(-1)

    ## ( 1 2 3 -- 1 3 ) -> 2
    def pip(self):
        return self.nest.pop(-2)

    ## ( 1 2 3 -- )
    def dropall(self):
        self.nest = []
        return self

    ## ( 1 2 3 -- 1 2 3 3 )
    def dup(self):
        return self // self.top()

    ## ( 1 2 3 -- 1 2 )
    def drop(self):
        self.pop()
        return self

    ## ( 1 2 3 -- 1 3 2 )
    def swap(self):
        return self // self.pip()

    ## ( 1 2 3 -- 1 2 3 2 )
    def over(self):
        return self // self.nest[-2]

    ## ( 1 2 3 -- 1 3 )
    def press(self):
        self.pip()
        return self


## @defgroup prim примитивы
## @ingroup core

## @ingroup prim
class Primitive(Object):
    pass

## @ingroup prim
## символ (уникальное имя)
class Symbol(Primitive):
    pass

## @ingroup prim
## строка
class String(Primitive):
    pass

## @ingroup prim
## число
class Number(Primitive):
    def __init__(self, V): Primitive.__init__(self, float(V))

## @ingroup prim
## целое число
class Integer(Number):
    def __init__(self, V): Primitive.__init__(self, int(V, 0x0A))

## @ingroup prim
## шестнадцатеричное машинное число
class Hex(Integer):
    def __init__(self, V): Primitive.__init__(self, int(V[2:], 0x10))
    def _val(self): return hex(self.val) # '0x{0:x}'.format(self.val)

## @ingroup prim
## битовая строка
class Bin(Integer):
    def __init__(self, V): Primitive.__init__(self, int(V[2:], 0x02))
    def _val(self): return bin(self.val) # '0b{0:b}'.format(self.val)


## @defgroup cont контейнеры
## @ingroup core

## @ingroup cont
## контейнер (структура) данных
class Container(Object):
    pass

## @ingroup cont
## вектор
class Vector(Container):
    pass

## @ingroup cont
## словарь (ключ/значение), `map<>` в С++
class Dict(Container):
    pass

## @ingroup cont
## FIFO стек
class Stack(Container):
    pass

## @ingroup cont
## LIFO очередь
class Queue(Container):
    pass


## @defgroup active исполняемые данные
## @ingroup core

## @ingroup active
class Active(Object):
    pass

## виртуальная (форт-)машина
## @ingroup active
class VM(Active):
    pass


## команда ВМ (обёртка для функций написанных на Python)
## @ingroup active
class Command(Active):

    ## @param[in] F Python-функция `func(context) -> Object`
    def __init__(self, F):
        Active.__init__(self, F.__name__)
        ## функция хранится как дополнительное поле объекта
        self.fn = F

    def eval(self, env):
        return self.fn(env)

## @defgroup meta метапрограммирование
## @ingroup core

## @ingroup meta
class Meta(Object):
    pass

## синтаксис языка программирования/данных
## @ingroup meta
class Syntax(Meta):
    pass


## @defgroup metal язык metaL
## @brief `meta`programming `L`anguage


## глобальная ВМ = глобальный контекст & таблица символов
## @ingroup metal
vm = VM('metaL')

## @ingroup metal
def BYE(ctx): exit(0)


vm >> Command(BYE)

## @defgroup lexer лексер
## @ingroup metal

import ply.lex as lex

## @ingroup lexer
class Lexer(Syntax):

    def __init__(self, V):
        Syntax.__init__(self, V)
        self.lexer = lex.lex(module=self)

    ## обработчик ошибок лексера (нераспознанный символ в токене)
    def t_ANY_error(self, t):
        raise SyntaxError(t)

    ## загрузка кода в лексер
    ## @param[in] source строка с исходным кодом
    def input(self, source): self.lexer.input(source)

    ## получить следующий токен (в цикле) или None
    def token(self): return self.lexer.token()

    ## @name правила выделения токенов

    ## типы токенов языка `metaL`
    tokens = ['symbol', 'integer', 'nl']

    ## игнорировать любые пробельные символы
    t_ignore = ' \t\r+'

    ## удаляем строчные комментарии
    t_ignore_comment = r'\#.*'

    ## концы строк обрабатываем особо: увеличиваем счетчик, и считаем концом выражения
    def t_nl(self, t):
        r'\n'
        t.lexer.lineno += 1
        t.value = ''
        return t

    ## целое число
    def t_integer(self, t):
        r'[+\-]?[0-9]+'
        t.value = Integer(t.value)
        return t

    ## символ (имя переменной)
    def t_symbol(self, t):
        r'[^ \t\r\n\#]+'
        t.value = Symbol(t.value)
        return t


lexer = Lexer('metaL')
print(lexer)

## @defgroup parser парсер
## @ingroup metal

import ply.yacc as yacc

## @ingroup parser
class Parser(Syntax):

    def __init__(self, V):
        Syntax.__init__(self, V)
        self.parser = yacc.yacc(module=self, #tabmodule=self,
                                debug=False, write_tables=False)

    def parse(self,source,lexer):
        self.parser.parse(source,lexer=lexer)

parser = Parser('metaL') ; print(parser)

## @defgroup init инициализация системы
## @ingroup metal


if __name__ == '__main__':
    for srcfile in sys.argv[1:]:
        with open(srcfile) as src:
            parser.parse(src.read(),lexer=lexer)
