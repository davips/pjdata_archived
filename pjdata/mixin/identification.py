""" Identifyable Module. """
from abc import ABC, abstractmethod
from functools import cached_property

from pjdata.aux.uuid import UUID


class WithEquality(ABC):
    """Mixin for classes that need to be hashable to provide items for sets/dicts/lru) or be compared by UUID.
    This mixin needs WithIdentification, but cannot enforce it due to performance reasons.
    """

    def __eq__(self, other) -> bool:
        # TODO: some checks might be removed for speed (isinstance is said to be slow...)
        if not isinstance(other, WithEquality):  # Should never happen, so it is the first check.
            raise Exception('Cannot compare', self.name, 'with', other.name, ' which has no UUID!')
        if not isinstance(other, self.__class__):
            return False
        # raise Exception  # <- usei desse recurso para encontrar a origem do mal [davi]
        return self.uuid == other.uuid

    def __hash__(self) -> int:
        return self.uuid.n


class WithIdentification(ABC):
    """ Identifiable mixin. """

    @cached_property
    def name(self):
        return self._name_impl()

    @abstractmethod
    def _name_impl(self):
        pass

    # cannot use lru for uuid() because we are overriding data._hash_ with uuid --->>> loop
    _uuid = None

    @property  # see comment above
    def uuid(self) -> UUID:
        """Lazily calculated unique identifier for this dataset.

        Should be accessed direct as a class member: 'uuid'.

        Returns
        -------
            A unique identifier UUID object.
        """
        return self._compute_uuid()

    def _compute_uuid(self) -> UUID:
        if self._uuid is None:
            content = self._uuid_impl()
            self._uuid = (
                content if isinstance(content, UUID) else UUID(content.encode())
            )
        return self._uuid

    @cached_property
    def id(self):
        """
        Short uuID
        First 8 chars of uuid, usually for printing purposes.
        First collision expect after 12671943 combinations.
        :return:
        """
        return self.uuid.id

    @cached_property
    def sid(self):
        """
        Short uuID
        First 6 chars of uuid, usually for printing purposes.
        :return:
        """
        return self.id[:6]

    @abstractmethod
    def _uuid_impl(self):
        """Specific internal calculation made by each child class.

        Should return a string or a UUID object to be used directly."""

    # Eu tentei essa abordagem, mas infelizmente isso não parece ser interessante
    # 1) devido ao hash, o python reutiliza as classes e quebra os componentes que usam
    # 2) o tempo para criar os objetos triplicou
    #    ex:
    #     def ger_workflow(arq="iris.arff"):
    #         np.random.seed(0)
    #
    #         workflow = Pipeline(
    #             File(arq),
    #             Partition(),
    #             Map(PCA(), select(SVMC(), DT(criterion="gini")), Metric(enhance=False)),
    #             Summ(function="mean", enhance=False),
    #             Reduce(),
    #             Report("Mean S: $S", enhance=False),
    #         )
    #
    #         return workflow

    #     np.random.seed(0)
    #     start_time = time.time()
    #     pipes = rnd(ger_workflow(), n=1000)
    #     elapsed_time = time.time() - start_time
    #     print("enlapsed time: ", elapsed_time)
    #
    # Portanto, se não conseguirmos solução melhor, acho que o "isequal" será alternativa mais conveniente

    # UPDATE:
    # dict e set (incluindo @property e @lru_cache) provavelmente fazem o que toda hash table(?) faz:
    # usam primeiro __hash__ para encontrar o registro em O(1) e depois __eq__ para encontrar o item exato se há colisão
    # O problema parece ter surgido quando coloquei o Component na dança do Identification.
    # Isso azedou o mecanismo de property que acaba quebrando o stream por algum motivo obscuro.
    # Com relação a tempo de processamento, podemos verificar se há caches esquecidos, ou excesso de funções encadeadas.
    #                                                                                           [davi]
