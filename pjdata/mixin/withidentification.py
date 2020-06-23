""" Identifyable Module. """
from abc import ABC, abstractmethod
from functools import cached_property

from pjdata.aux.uuid import UUID


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

    # def __eq__(self, other) -> bool:
    #     if not hasattr(other, 'uuid'):
    #         return False
    #     # TODO: check why compare uuid not work
    #     # return self.uuid == other.uuid
    #     return self.uuid.n == other.uuid.n
    #
    # def __hash__(self) -> int:
    #     return self._compute_uuid().n

    def isequal(self, other):
        if not hasattr(other, "uuid"):
            return False
        # TODO: check why compare uuid not work (I think is something related to self.m)
        # return self.uuid == other.uuid
        return self.uuid.n == other.uuid.n
