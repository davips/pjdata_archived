from pjdata.collection import Collection
from pjdata.history import History


class FiniteCollection(Collection):
    from pjdata.specialdata import NoData

    def __init__(self, datas, history=None, failure=None, original_data=NoData):
        super().__init__(history, failure, original_data)

        self._datas = datas
        self.size = len(datas)
        self.has_nones = not all(datas)

        self._uuids = ""
        for data in self._datas:
            self._uuids += data.uuid if data else "00000000000000000000"

    def last_transformation_replaced(self, transformation):
        """Replace last transformation in history for convenience.

        Provided transformation should be equivalent to the replaced one for
        consistency.
        """
        return FiniteCollection(
            self._datas,
            history=History(self.history[:-1] + [transformation]),
            failure=self.failure,
            original_data=self.original_data
        )

    def __str__(self):
        return 'FiniteCollection [' + \
               '\n'.join(str(data) for data in self._datas) + ']'
