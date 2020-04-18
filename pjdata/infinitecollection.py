from itertools import repeat

from pjdata.collection import Collection


class InfiniteCollection(Collection):
    _almost_infinity = 10_000_000_000

    def __init__(self, data, history=None, failure=None, uuid=None):
        super().__init__(history, failure, data, uuid)

        # Yes, all Data objects here are exactly the same (immutability):
        self._datas = repeat(data, times=self._almost_infinity)
        self.size = self._almost_infinity
        self.has_nones = False

    def last_transformation_replaced(self, transformation):
        """Replace last transformation in history for convenience.

        Provided transformation should be equivalent to the replaced one for
        consistency.
        """
        return InfiniteCollection(
            self.original_data,
            history=self.history[:-1] + [transformation],
            failure=self.failure,
            uuid=self.uuid00 - self.history[-1].uuid00 + transformation.uuid00
        )

    def __str__(self):
        return 'Infinite collection!' + \
               str(self.history) + ' ' + \
               str(self.failure) + ' '
