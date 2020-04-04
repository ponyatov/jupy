## базовый класс узлов объектного графа
class Object:

    def __init__(self, V):
        #№ метка типа/класса
        self.type = self.__class__.__name__.lower()
        #№ скалярное значение узла (имя, строка, число)
        self.val = V
        #№ атрибуты = ассоциативный массив
        self.slot = {}
        ## упорядоченный набор ссылок = вектор = стек
        self.nest = []

    ## служебный метод вызывается из `print()`
    def __repr__(self):
        return self.dump()

    ## вывод дампа в виде текстового дерева
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
            tree += self.slot[i].dump(depth + 1, prefix='%s = ' % i) ; idx += 1
        # nest[]ы
        idx = 0
        for j in self.nest:
            tree += j.dump(depth + 1, prefix='%s = ' % idx)
        # дамп подграфа
        return tree

    ## короткий дамп: только <T:V> заголовок
    def head(self, prefix=''):
        return '%s<%s:%s> @%x' % (prefix, self.type, self._val(), id(self))

    ## отбивка пробелами в зависимости от уровня вложенности
    def pad(self, depth):
        return '\n' + '\t' * depth
    ## метод форматирует поле .val специально для дампа

    def _val(self):
        return '%s' % self.val
